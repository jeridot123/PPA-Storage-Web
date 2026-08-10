from config import (
    LINES,
    IMPORT_PREFIX,
    NEAREST_LINES
)

from database import (
    get_storage,
    get_next_position,
    insert_roll,
    count_items,
    get_oldest_roll,
    delete_roll,
    shift_positions,
    get_lines
)

def is_import(product_code):

    product_code = product_code.upper()

    return product_code.startswith(IMPORT_PREFIX)


def get_line_capacity(line_id):

    for line in LINES:

        if line["id"] == line_id:

            return line["capacity"]

    return None


def allow_import(line_id):

    for line in LINES:

        if line["id"] == line_id:

            return line["allow_import"]

    return False



def line_has_space(storage, line_id):

    occupied = 0

    for item in storage:

        if item["line_id"] == line_id:
            occupied += 1

    return occupied < get_line_capacity(line_id)

def find_same_product_line(storage, product_code):

    for item in storage:

        if item["product_code"] == product_code:

            if line_has_space(storage, item["line_id"]):
                return item["line_id"]

    return None

def find_nearest_available_line(storage, product_code):

    imported = is_import(product_code)

    # Step 1
    # Search completely empty lines first

    for line in LINES:

        line_id = line["id"]

        if imported and not allow_import(line_id):
            continue

        occupied = 0

        for item in storage:

            if item["line_id"] == line_id:
                occupied += 1

        capacity = get_line_capacity(line_id)

        if imported:
            capacity = min(capacity, 8)

        if occupied == 0:
            return line_id

    return None

def find_best_line(product_code):

    storage = get_storage()

    line = find_same_product_line(storage, product_code)

    if line:
        return line

    return find_nearest_available_line(storage, product_code)

def store_roll(product_code):

    line = find_best_line(product_code)

    if line is None:

        return None

    position = get_next_position(line)

    # IMPORT products only use positions 1-8
    if is_import(product_code):

        if position > 8:

            return None

    insert_roll(
        product_code,
        line,
        position,
        None
    )

    return {
        "line": line,
        "position": position
    }


# =========================================================
# TAKE ROLL (FIFO)
# =========================================================

def take_roll(product_code):

    roll = get_oldest_roll(product_code)

    if roll is None:
        return None

    line = roll["line_id"]
    position = roll["position"]

    delete_roll(roll["id"])

    shift_positions(line)

    return {
        "line": line,
        "position": position,
        "product_code": product_code
    }


# =========================================================
# WAREHOUSE STATUS
# =========================================================

def get_warehouse_status():

    lines = get_lines()
    storage = get_storage()

    result = []
    occupied = 0

    for line in lines:

        line_id = line["line_id"]

        items = []

        for roll in storage:

            if roll["line_id"] == line_id:

                items.append({

                    "position": roll["position"],

                    "product_code": roll["product_code"],

                    "batch": roll.get("batch"),

                    "created_at": roll.get("created_at")

                })

        items.sort(key=lambda x: x["position"])

        occupied += len(items)

        capacity = line["capacity"]

        result.append({

            "line_id": line_id,

            "capacity": capacity,

            "occupied": len(items),

            "available": capacity - len(items),

            "items": items

        })

    total = sum(line["capacity"] for line in lines)

    return {

        "success": True,

        "lines": result,

        "occupied": occupied,

        "available": total - occupied,

        "total": total

    }