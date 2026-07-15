# Inventory Management System

A Flask REST API + CLI for managing retail inventory, with product
enrichment via the [OpenFoodFacts API](https://world.openfoodfacts.org/data).

Built for the *Summative Lab: Python REST API with Flask – Inventory
Management System* assignment.

## Features

- Flask REST API with full CRUD (`GET`, `POST`, `PATCH`, `DELETE`) for inventory items
- Integration with OpenFoodFacts to fetch product details by barcode or search by name
- CLI tool to add, view, update, delete, and look up inventory items
- Unit tests (pytest + `unittest.mock`) covering the API, the CLI, and the external API client
- In-memory "database" (a Python list) that simulates persistent storage, as specified by the assignment

## Project Structure

```
inventory_api/
├── app.py                 # Flask REST API, routes, and OpenFoodFacts integration
├── cli.py                 # Command-line interface
├── requirements.txt
├── README.md
├── frontend/               # Optional Vite + React admin UI (bonus, alongside the CLI)
│   ├── src/
│   └── ...
└── tests/
    ├── test_api.py
    └── test_cli.py
```

## Installation and Setup

1. Clone the repository and move into it:
   ```bash
   git clone <your-repo-url>
   cd inventory_api
   ```

2. (Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Start the Flask API (keep this terminal running):
   ```bash
   python app.py
   ```
   The API will be available at `http://127.0.0.1:5000`.

5. In a **second terminal**, use the CLI to interact with the running API (see below).

## API Endpoint Details

| Method | Endpoint                          | Description                                              |
|--------|------------------------------------|------------------------------------------------------------|
| GET    | `/inventory`                      | List all inventory items                                   |
| GET    | `/inventory/<id>`                 | Get a single item by id                                     |
| POST   | `/inventory`                      | Create a new item (`name` required in JSON body)             |
| PATCH  | `/inventory/<id>`                 | Update one or more fields of an item                        |
| DELETE | `/inventory/<id>`                 | Delete an item                                               |
| POST   | `/inventory/fetch/barcode/<code>` | Fetch a product from OpenFoodFacts by barcode and add it     |
| GET    | `/inventory/fetch/search?name=`   | Search OpenFoodFacts by product name (does not modify inventory) |

### Item shape

```json
{
  "id": 1,
  "name": "Organic Almond Milk",
  "brand": "Silk",
  "barcode": "3274080005003",
  "price": 3.5,
  "stock": 12,
  "ingredients_text": "Filtered water, almonds, cane sugar, ..."
}
```

### Example requests

```bash
# Create an item
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"name": "Almond Milk", "brand": "Silk", "price": 3.5, "stock": 12}'

# List items
curl http://127.0.0.1:5000/inventory

# Update an item
curl -X PATCH http://127.0.0.1:5000/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{"stock": 20}'

# Delete an item
curl -X DELETE http://127.0.0.1:5000/inventory/1

# Fetch a product from OpenFoodFacts by barcode and add it to inventory
curl -X POST http://127.0.0.1:5000/inventory/fetch/barcode/3274080005003

# Search OpenFoodFacts by name
curl "http://127.0.0.1:5000/inventory/fetch/search?name=almond%20milk"
```

## CLI Usage

The CLI talks to the Flask API, so the server must be running first.

```bash
# List all items
python cli.py list

# View a single item
python cli.py view 1

# Add a new item
python cli.py add --name "Almond Milk" --brand Silk --price 3.5 --stock 12

# Update price and/or stock
python cli.py update 1 --price 4.0 --stock 20

# Delete an item
python cli.py delete 1

# Fetch a product from OpenFoodFacts by barcode and add it to inventory
python cli.py find --barcode 3274080005003

# Search OpenFoodFacts by name (does not modify inventory)
python cli.py find --name "almond milk"
```

If the Flask server isn't running, the CLI will print a clear error
instead of crashing.

## Running Tests

```bash
pytest -v
```

All external HTTP calls (both to OpenFoodFacts and, in the CLI tests,
to the local API) are mocked with `unittest.mock`, so the test suite
runs offline and does not depend on the real OpenFoodFacts service
being reachable.

## Optional: React Frontend

Alongside the required CLI, this project also includes an optional
Vite + React admin UI in `frontend/`. It talks to the same Flask API
and supports full CRUD plus the OpenFoodFacts barcode/name lookup.

### Setup

```bash
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). Make
sure the Flask API is running separately first (`python app.py` from
the project root) — the Vite dev server proxies `/inventory/*`
requests straight through to `http://127.0.0.1:5000`, so no CORS
setup is needed.

### Build for production

```bash
cd frontend
npm run build
```

Output goes to `frontend/dist/`.

## Notes

- Data is stored in memory only (a Python list); it resets whenever the
  Flask server restarts. This matches the assignment's "simulated
  storage" requirement.
- The OpenFoodFacts client sends a descriptive `User-Agent` header, as
  requested by their API usage guidelines.