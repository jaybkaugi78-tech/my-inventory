import argparse
import json
import sys
import requests
API_BASE = "http://127.0.0.1:5000"

def cmd_list(args):
    resp = requests.get(f"{API_BASE}/inventory")
    print(json.dumps(resp.json(), indent=2))

def cmd_view(args):
    resp = requests.get(f"{API_BASE}/inventory/{args.id}")
    if resp.status_code == 404:
        print(f"Item {args.id} not found.")
        return
    print(json.dumps(resp.json(), indent=2))

def cmd_add(args):
    payload = {
        "name": args.name,
        "brand": args.brand,
        "barcode": args.barcode,
        "price": args.price,
        "stock": args.stock,
    }
    resp = requests.post(f"{API_BASE}/inventory", json=payload)
    if resp.status_code != 201:
        print(f"Error: {resp.json().get('error')}")
        return
    print("Added item:")
    print(json.dumps(resp.json(), indent=2))

def cmd_update(args):
    payload = {}
    if args.name is not None:
        payload["name"] = args.name
    if args.price is not None:
        payload["price"] = args.price
    if args.stock is not None:
        payload["stock"] = args.stock

    if not payload:
        print("Nothing to update. Provide --name, --price, and/or --stock.")
        return

    resp = requests.patch(f"{API_BASE}/inventory/{args.id}", json=payload)
    if resp.status_code == 404:
        print(f"Item {args.id} not found.")
        return
    print("Updated item:")
    print(json.dumps(resp.json(), indent=2))

def cmd_delete(args):
    resp = requests.delete(f"{API_BASE}/inventory/{args.id}")
    if resp.status_code == 404:
        print(f"Item {args.id} not found.")
        return
    print(resp.json().get("message"))

def cmd_find(args):
    if args.barcode:
        resp = requests.post(f"{API_BASE}/inventory/fetch/barcode/{args.barcode}")
        if resp.status_code != 201:
            print(f"Error: {resp.json().get('error')}")
            return
        print("Fetched product and added to inventory:")
        print(json.dumps(resp.json(), indent=2))
    elif args.name:
        resp = requests.get(
            f"{API_BASE}/inventory/fetch/search", params={"name": args.name}
        )
        if resp.status_code != 200:
            print(f"Error: {resp.json().get('error')}")
            return
        results = resp.json()
        if not results:
            print("No products found.")
            return
        print(json.dumps(results, indent=2))
    else:
        print("Provide --barcode or --name to search OpenFoodFacts.")
def build_parser():
    parser = argparse.ArgumentParser(
        description="Inventory Management CLI (talks to the Flask API)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list", help="List all inventory items")
    p_list.set_defaults(func=cmd_list)

    p_view = subparsers.add_parser("view", help="View a single item by ID")
    p_view.add_argument("id", type=int)
    p_view.set_defaults(func=cmd_view)

    p_add = subparsers.add_parser("add", help="Add a new inventory item")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--brand", default="")
    p_add.add_argument("--barcode", default="")
    p_add.add_argument("--price", type=float, default=0.0)
    p_add.add_argument("--stock", type=int, default=0)
    p_add.set_defaults(func=cmd_add)

    p_update = subparsers.add_parser(
        "update", help="Update the name, price, and/or stock of an item"
    )
    p_update.add_argument("id", type=int)
    p_update.add_argument("--name")
    p_update.add_argument("--price", type=float)
    p_update.add_argument("--stock", type=int)
    p_update.set_defaults(func=cmd_update)

    p_delete = subparsers.add_parser("delete", help="Delete an item by ID")
    p_delete.add_argument("id", type=int)
    p_delete.set_defaults(func=cmd_delete)

    p_find = subparsers.add_parser(
        "find", help="Look up a product on OpenFoodFacts by barcode or name"
    )
    p_find.add_argument("--barcode", help="Fetch by barcode and add to inventory")
    p_find.add_argument("--name", help="Search by name (does not add to inventory)")
    p_find.set_defaults(func=cmd_find)

    return parser
def main():
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except requests.exceptions.ConnectionError:
        print(
            f"{API_BASE}. Is the Flask server running? (python app.py)"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()