from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from dotenv import load_dotenv

import re
import os

# =========================================================
# CONFIGURATION
# =========================================================

app = Flask(__name__)
load_dotenv()

N_LANES = 17
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================================================
# DATABASE CONNECTION POOL
# =========================================================

# Create a connection pool instead of opening a new connection every request
# minconn=1, maxconn=10
db_pool = SimpleConnectionPool(1, 10, DATABASE_URL)

def get_db():
    return db_pool.getconn()

def release_db(connection):
    if connection:
        db_pool.putconn(connection)

# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database():
    connection = get_db()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS storage (
                lane INTEGER NOT NULL,
                slot CHAR(1) NOT NULL,
                product_code TEXT,
                PRIMARY KEY (lane, slot)
            );
        """)

        for lane in range(1, N_LANES + 1):
            for slot in ["A", "B"]:
                cursor.execute(
                    """
                    INSERT INTO storage (lane, slot, product_code)
                    VALUES (%s, %s, NULL)
                    ON CONFLICT (lane, slot)
                    DO NOTHING;
                    """,
                    (lane, slot)
                )

        connection.commit()
        cursor.close()
    finally:
        release_db(connection)

# =========================================================
# GET COMPLETE WAREHOUSE (Used only for UI Status now)
# =========================================================

def get_warehouse(connection):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT lane, slot, product_code
        FROM storage
        ORDER BY lane, slot
    """)
    rows = cursor.fetchall()
    cursor.close()

    warehouse = {
        lane: {"A": None, "B": None}
        for lane in range(1, N_LANES + 1)
    }

    # Standard cursor returns tuples: row[0]=lane, row[1]=slot, row[2]=product_code
    for row in rows:
        warehouse[row[0]][row[1]] = row[2]

    return warehouse

def validate_product(product_code):
    product_code = product_code.strip().upper()
    if re.fullmatch(r"NY\d+", product_code) or re.fullmatch(r"PE\d+", product_code):
        return True
    return False

# =========================================================
# FIND STORAGE LOCATION (Optimized with SQL)
# =========================================================

def find_storage(connection, product_code):
    cursor = connection.cursor()

    # -----------------------------------------------------
    # PRIORITY 1: Same product already occupies one slot, other is empty
    # -----------------------------------------------------
    cursor.execute("""
        SELECT s1.lane, 
               CASE WHEN s1.slot = 'A' THEN 'B' ELSE 'A' END as target_slot
        FROM storage s1
        JOIN storage s2 ON s1.lane = s2.lane AND s1.slot != s2.slot
        WHERE s1.product_code = %s AND s2.product_code IS NULL
        LIMIT 1
    """, (product_code,))
    
    row = cursor.fetchone()
    if row:
        cursor.close()
        return row[0], row[1]

    # -----------------------------------------------------
    # PRIORITY 2: Completely empty lane
    # -----------------------------------------------------
    # COUNT(product_code) only counts non-NULL values. If 0, lane is empty.
    cursor.execute("""
        SELECT lane
        FROM storage
        GROUP BY lane
        HAVING COUNT(product_code) = 0
        ORDER BY lane ASC
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    cursor.close()
    
    if row:
        return row[0], "A"

    return None

# =========================================================
# FIND PRODUCT FOR OUT
# =========================================================

def find_product(connection, product_code):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT lane, slot
        FROM storage
        WHERE product_code = %s
        ORDER BY lane ASC,
                 CASE slot WHEN 'A' THEN 1 ELSE 2 END
        LIMIT 1
        """,
        (product_code,)
    )
    
    row = cursor.fetchone()
    cursor.close()

    if row is None:
        return None

    return row[0], row[1]

# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")

# =========================================================
# API - GET WAREHOUSE STATUS
# =========================================================

@app.route("/api/warehouse", methods=["GET"])
def warehouse_status():
    connection = get_db()
    try:
        warehouse = get_warehouse(connection)
        
        occupied = 0
        lanes = []

        for lane in range(1, N_LANES + 1):
            slot_a = warehouse[lane]["A"]
            slot_b = warehouse[lane]["B"]

            if slot_a is not None:
                occupied += 1
            if slot_b is not None:
                occupied += 1

            lanes.append({
                "lane": lane,
                "A": slot_a,
                "B": slot_b
            })

        total = N_LANES * 2

        return jsonify({
            "success": True,
            "lanes": lanes,
            "occupied": occupied,
            "available": total - occupied,
            "total": total
        })
    finally:
        release_db(connection)

# =========================================================
# API - STORE PRODUCT
# =========================================================

@app.route("/api/store", methods=["POST"])
def store_product():
    data = request.get_json(silent=True) or {}
    product_code = str(data.get("product_code", "")).strip().upper()

    if not validate_product(product_code):
        return jsonify({"success": False, "message": "INVALID BARCODE"}), 400

    connection = get_db()
    try:
        # Pass connection directly. We no longer download the whole warehouse dict!
        location = find_storage(connection, product_code)

        if location is None:
            return jsonify({"success": False, "message": "WAREHOUSE FULL"}), 409

        lane, slot = location
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE storage
            SET product_code = %s
            WHERE lane = %s AND slot = %s
            """,
            (product_code, lane, slot)
        )
        connection.commit()
        cursor.close()

        return jsonify({
            "success": True,
            "message": "ITEM SUCCESSFULLY STORED",
            "product_code": product_code,
            "lane": lane,
            "slot": slot
        })
    finally:
        release_db(connection)

# =========================================================
# API - TAKE PRODUCT
# =========================================================

@app.route("/api/take", methods=["POST"])
def take_product():
    data = request.get_json(silent=True) or {}
    product_code = str(data.get("product_code", "")).strip().upper()

    if not validate_product(product_code):
        return jsonify({"success": False, "message": "INVALID BARCODE"}), 400

    connection = get_db()
    try:
        location = find_product(connection, product_code)

        if location is None:
            return jsonify({"success": False, "message": "PRODUCT NOT FOUND"}), 404

        lane, slot = location
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE storage
            SET product_code = NULL
            WHERE lane = %s AND slot = %s
            """,
            (lane, slot)
        )
        connection.commit()
        cursor.close()

        return jsonify({
            "success": True,
            "message": "ITEM TAKEN",
            "product_code": product_code,
            "lane": lane,
            "slot": slot
        })
    finally:
        release_db(connection)


if __name__ == "__main__":
    try:
        conn = get_db()
        print("✅ Connected to Supabase")
        release_db(conn)
    except Exception as e:
        print("❌ Connection Failed")
        print(e)

    # initialize_database()
    app.run(host="127.0.0.1", port=5000, debug=True)