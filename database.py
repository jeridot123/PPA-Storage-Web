import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor

from config import DATABASE_URL

# ==========================================
# DATABASE CONNECTION POOL
# ==========================================

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")

db_pool = SimpleConnectionPool(
    1,
    10,
    DATABASE_URL
)


def get_connection():
    return db_pool.getconn()


def release_connection(connection):
    if connection:
        db_pool.putconn(connection)

# ==========================================
# GET ALL WAREHOUSE LINES
# ==========================================

def get_lines():

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""

            SELECT *
            FROM warehouse_lines
            ORDER BY
            CASE line_id

                WHEN '1A' THEN 1
                WHEN '2A' THEN 2

                ELSE 100 + CAST(line_id AS INTEGER)

            END

        """)

        return cursor.fetchall()

    finally:

        release_connection(connection)

# ==========================================
# GET ALL STORED ROLLS
# ==========================================

def get_storage():

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute("""

            SELECT *
            FROM storage
            ORDER BY
            line_id,
            position

        """)

        return cursor.fetchall()

    finally:

        release_connection(connection)

# ==========================================
# INSERT ROLL
# ==========================================

def insert_roll(product_code, line_id, position, batch=None):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO storage
            (
                product_code,
                batch,
                line_id,
                position
            )

            VALUES (%s, %s, %s, %s)
            """,
            (
                product_code,
                batch,
                line_id,
                position
            )
        )

        connection.commit()

        cursor.close()

    finally:

        release_connection(connection)

# ==========================================
# NEXT POSITION
# ==========================================

def get_next_position(line_id):

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(
            """
            SELECT MAX(position) AS last_position

            FROM storage

            WHERE line_id = %s
            """,
            (line_id,)
        )

        row = cursor.fetchone()

        cursor.close()

        if row["last_position"] is None:
            return 1

        return row["last_position"] + 1

    finally:

        release_connection(connection)

# ==========================================
# GET OLDEST ROLL
# ==========================================

def get_oldest_roll(product_code):

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(
            """
            SELECT *

            FROM storage

            WHERE product_code = %s

            ORDER BY
            created_at ASC,
            position ASC

            LIMIT 1
            """,
            (product_code,)
        )

        row = cursor.fetchone()

        cursor.close()

        return row

    finally:

        release_connection(connection)

# ==========================================
# DELETE ROLL
# ==========================================

def delete_roll(roll_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            DELETE FROM storage
            WHERE id = %s
            """,
            (roll_id,)
        )

        connection.commit()

        cursor.close()

    finally:

        release_connection(connection)

# ==========================================
# SHIFT POSITIONS
# ==========================================

def shift_positions(line_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            WITH ordered AS (

                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        ORDER BY position
                    ) AS new_position

                FROM storage

                WHERE line_id = %s

            )

            UPDATE storage

            SET position = ordered.new_position

            FROM ordered

            WHERE storage.id = ordered.id
            """,
            (line_id,)
        )

        connection.commit()

        cursor.close()

    finally:

        release_connection(connection)

# ==========================================
# COUNT ITEMS IN A LINE
# ==========================================

def count_items(line_id):

    connection = get_connection()

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM storage
            WHERE line_id = %s
            """,
            (line_id,)
        )

        row = cursor.fetchone()

        cursor.close()

        return row["total"]

    finally:

        release_connection(connection)