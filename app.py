import itertools
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
inventory = []
_id_counter = itertools.count(1)

OFF_BASE_URL = "https://world.openfoodfacts.org"
OFF_USER_AGENT = "InventoryManagementCLI/1.0 (student-project; contact@example.com)"

OFF_REQUEST_TIMEOUT = 10 

def find_item(item_id):
    return next((item for item in inventory if item["id"] == item_id), None)

def fetch_product_by_barcode(barcode):
    url = f"{OFF_BASE_URL}/api/v2/product/{barcode}.json"
    headers = {"User-Agent": OFF_USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=OFF_REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        return None, str(exc)

    data = response.json()

    if data.get("status") != 1:
        return None, None

    return data.get("product", {}), None

def search_products_by_name(name, page_size=5):
    url = f"{OFF_BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": page_size,
    }
    headers = {"User-Agent": OFF_USER_AGENT}

    try:
        response = requests.get(
            url, headers=headers, params=params, timeout=OFF_REQUEST_TIMEOUT
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return [], str(exc)

    data = response.json()
    products = data.get("products", [])

    simplified = [
        {
            "product_name": p.get("product_name") or "Unknown",
            "brands": p.get("brands", ""),
            "barcode": p.get("code", ""),
            "ingredients_text": p.get("ingredients_text", ""),
        }
        for p in products
    ]

    return simplified, None

@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200

@app.route("/inventory/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    return jsonify(item), 200

@app.route("/inventory", methods=["POST"])
def add_item():
    data = request.get_json(silent=True)
    if not data or "name" not in data:
        return jsonify({"error": "Missing required field: name"}), 400

    item = {
        "id": next(_id_counter),
        "name": data["name"],
        "brand": data.get("brand", ""),
        "barcode": data.get("barcode", ""),
        "price": data.get("price", 0.0),
        "stock": data.get("stock", 0),
        "ingredients_text": data.get("ingredients_text", ""),
    }
    inventory.append(item)
    return jsonify(item), 201

@app.route("/inventory/<int:item_id>", methods=["PATCH"])
def update_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    updatable_fields = [
        "name", "brand", "barcode", "price", "stock", "ingredients_text"
    ]
    for field in updatable_fields:
        if field in data:
            item[field] = data[field]

    return jsonify(item), 200

@app.route("/inventory/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = find_item(item_id)
    if item is None:
        return jsonify({"error": "Item not found"}), 404

    inventory.remove(item)
    return jsonify({"message": f"Item {item_id} deleted"}), 200

@app.route("/inventory/fetch/barcode/<barcode>", methods=["POST"])
def fetch_and_add_by_barcode(barcode):
    product, error = fetch_product_by_barcode(barcode)
    if error:
        return jsonify({"error": f"OpenFoodFacts request failed: {error}"}), 502
    if not product:
        return jsonify({"error": "Product not found in OpenFoodFacts"}), 404
    item = {
        "id": next(_id_counter),
        "name": product.get("product_name", "Unknown"),
        "brand": product.get("brands", ""),
        "barcode": barcode,
        "price": 0.0,
        "stock": 0,
        "ingredients_text": product.get("ingredients_text", ""),
    }
    inventory.append(item)
    return jsonify(item), 201

@app.route("/inventory/fetch/search", methods=["GET"])
def fetch_search_by_name():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Missing query parameter: name"}), 400

    results, error = search_products_by_name(name)
    if error:
        return jsonify({"error": f"OpenFoodFacts request failed: {error}"}), 502

    return jsonify(results), 200

if __name__ == "__main__":
    app.run(debug=True)