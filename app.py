from flask import Flask, render_template, redirect, request, jsonify
from dotenv import load_dotenv

import re

app = Flask(__name__)

load_dotenv()

from warehouse import (
    store_roll,
    take_roll,
    get_warehouse_status
)
@app.route("/")
def home():
    return redirect("/entry")


@app.route("/entry")
def entry():
    return render_template("entry.html")


@app.route("/takeout")
def takeout():
    return render_template("takeout.html")


@app.route("/display")
def display():
    return render_template("display.html")



# =========================================================
# VALIDATION
# =========================================================

def validate_product(product_code):

    product_code = product_code.strip().upper()

    if re.fullmatch(r"NY\d+", product_code):
        return True

    if re.fullmatch(r"PE\d+", product_code):
        return True

    if re.fullmatch(r"IMP\d+", product_code):
        return True

    return False



# =========================================================
# WAREHOUSE STATUS
# =========================================================

@app.route("/api/warehouse", methods=["GET"])
def warehouse():

    return jsonify(
        get_warehouse_status()
    )

# =========================================================
# STORE PRODUCT
# =========================================================

@app.route("/api/store", methods=["POST"])
def store():

    data = request.get_json(silent=True) or {}

    product_code = str(
        data.get("product_code", "")
    ).strip().upper()

    if not validate_product(product_code):

        return jsonify({
            "success": False,
            "message": "INVALID BARCODE"
        }), 400

    result = store_roll(product_code)

    if result is None:

        return jsonify({
            "success": False,
            "message": "WAREHOUSE FULL"
        }), 409

    return jsonify({
        "success": True,
        "message": "ITEM STORED",
        "product_code": product_code,
        "line": result["line"],
        "position": result["position"]
    })

# =========================================================
# TAKE PRODUCT
# =========================================================

@app.route("/api/take", methods=["POST"])
def take():

    data = request.get_json(silent=True) or {}

    product_code = str(
        data.get("product_code", "")
    ).strip().upper()

    if not validate_product(product_code):

        return jsonify({
            "success": False,
            "message": "INVALID BARCODE"
        }), 400

    result = take_roll(product_code)

    if result is None:

        return jsonify({
            "success": False,
            "message": "PRODUCT NOT FOUND"
        }), 404

    return jsonify({
        "success": True,
        "message": "ITEM TAKEN",
        "product_code": result["product_code"],
        "line": result["line"],
        "position": result["position"]
    })

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )