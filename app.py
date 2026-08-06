from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
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
# DATABASE CONNECTION
# =========================================================

def get_db():

    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor
    )


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database():

    connection = get_db()
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
    connection.close()

# =========================================================
# GET COMPLETE WAREHOUSE
# =========================================================

def get_warehouse():

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT lane, slot, product_code
        FROM storage
        ORDER BY lane, slot
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    warehouse = {
        lane: {
            "A": None,
            "B": None
        }
        for lane in range(1, N_LANES + 1)
    }

    for row in rows:
        warehouse[row["lane"]][row["slot"]] = row["product_code"]

    return warehouse


def validate_product(product_code):

    product_code = product_code.strip().upper()

    if re.fullmatch(r"NY\d+", product_code):
        return True

    if re.fullmatch(r"PE\d+", product_code):
        return True

    return False

# =========================================================
# FIND STORAGE LOCATION
# =========================================================

def find_storage(product_code):

    warehouse = get_warehouse()

    # -----------------------------------------------------
    # PRIORITY 1
    # Same product already occupies one slot
    # -----------------------------------------------------

    for lane in range(1, N_LANES + 1):

        slot_a = warehouse[lane]["A"]
        slot_b = warehouse[lane]["B"]

        if slot_a == product_code and slot_b is None:

            return lane, "B"

        if slot_b == product_code and slot_a is None:

            return lane, "A"

    # -----------------------------------------------------
    # PRIORITY 2
    # Completely empty lane
    # -----------------------------------------------------

    for lane in range(1, N_LANES + 1):

        if (
            warehouse[lane]["A"] is None
            and warehouse[lane]["B"] is None
        ):

            return lane, "A"

    return None


# =========================================================
# FIND PRODUCT FOR OUT
# =========================================================

def find_product(product_code):

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT lane, slot
        FROM storage
        WHERE product_code = %s
        ORDER BY lane ASC,
                 CASE slot
                    WHEN 'A' THEN 1
                    ELSE 2
                 END
        LIMIT 1
        """,
        (product_code,)
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if row is None:
        return None

    return row["lane"], row["slot"]


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

    warehouse = get_warehouse()

    occupied = 0

    lanes = []

    for lane in range(1, N_LANES + 1):

        slot_a = warehouse[lane]["A"]
        slot_b = warehouse[lane]["B"]

        if slot_a is not None:
            occupied += 1

        if slot_b is not None:
            occupied += 1

        lanes.append(
            {
                "lane": lane,
                "A": slot_a,
                "B": slot_b
            }
        )

    total = N_LANES * 2

    return jsonify(
        {
            "success": True,
            "lanes": lanes,
            "occupied": occupied,
            "available": total - occupied,
            "total": total
        }
    )


# =========================================================
# API - STORE PRODUCT
# =========================================================

@app.route("/api/store", methods=["POST"])
def store_product():

    data = request.get_json(silent=True) or {}

    product_code = (
        str(data.get("product_code", ""))
        .strip()
        .upper()
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not validate_product(product_code):

        return jsonify(
            {
                "success": False,
                "message": "INVALID BARCODE"
            }
        ), 400

    # -----------------------------------------------------
    # FIND LOCATION
    # -----------------------------------------------------

    location = find_storage(product_code)

    if location is None:

        return jsonify(
            {
                "success": False,
                "message": "WAREHOUSE FULL"
            }
        ), 409

    lane, slot = location

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE storage
        SET product_code = %s
        WHERE lane = %s
        AND slot = %s
        """,
        (
            product_code,
            lane,
            slot
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify(
        {
            "success": True,
            "message": "ITEM SUCCESSFULLY STORED",
            "product_code": product_code,
            "lane": lane,
            "slot": slot
        }
    )

# =========================================================
# API - TAKE PRODUCT
# =========================================================

@app.route("/api/take", methods=["POST"])
def take_product():

    data = request.get_json(silent=True) or {}

    product_code = (
        str(data.get("product_code", ""))
        .strip()
        .upper()
    )

    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not validate_product(product_code):

        return jsonify(
            {
                "success": False,
                "message": "INVALID BARCODE"
            }
        ), 400

    # -----------------------------------------------------
    # FIND PRODUCT
    # -----------------------------------------------------

    location = find_product(product_code)

    if location is None:

        return jsonify(
            {
                "success": False,
                "message": "PRODUCT NOT FOUND"
            }
        ), 404

    lane, slot = location

    # -----------------------------------------------------
    # REMOVE PRODUCT
    # -----------------------------------------------------

    connection = get_db()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE storage
        SET product_code = NULL
        WHERE lane = %s
        AND slot = %s
        """,
        (
            lane,
            slot
        )
    )

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify(
        {
            "success": True,
            "message": "ITEM TAKEN",
            "product_code": product_code,
            "lane": lane,
            "slot": slot
        }
    )

if __name__ == "__main__":

    try:
        conn = get_db()
        print("✅ Connected to Supabase")
        conn.close()

    except Exception as e:
        print("❌ Connection Failed")
        print(e)

    # initialize_database()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )