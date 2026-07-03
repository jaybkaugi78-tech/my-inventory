import itertools
import os
import sys
from unittest.mock import MagicMock, patch
import pytest
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app as app_module  # noqa: E402
@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    app_module.inventory.clear()
    app_module._id_counter = itertools.count(1)
    with app_module.app.test_client() as test_client:
        yield test_client

def test_get_inventory_empty(client):
    resp = client.get("/inventory")
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_add_item(client):
    resp = client.post(
        "/inventory", json={"name": "Almond Milk", "price": 3.5, "stock": 10}
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Almond Milk"
    assert data["id"] == 1

def test_add_item_missing_name(client):
    resp = client.post("/inventory", json={"price": 3.5})
    assert resp.status_code == 400
    assert "error" in resp.get_json()

def test_get_item(client):
    client.post("/inventory", json={"name": "Oat Milk"})
    resp = client.get("/inventory/1")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Oat Milk"

def test_get_item_not_found(client):
    resp = client.get("/inventory/999")
    assert resp.status_code == 404

def test_update_item(client):
    client.post("/inventory", json={"name": "Soy Milk", "stock": 5})
    resp = client.patch("/inventory/1", json={"stock": 20})
    assert resp.status_code == 200
    assert resp.get_json()["stock"] == 20

def test_update_item_not_found(client):
    resp = client.patch("/inventory/999", json={"stock": 20})
    assert resp.status_code == 404

def test_update_item_no_body(client):
    client.post("/inventory", json={"name": "Rice Milk"})
    resp = client.patch("/inventory/1", json=None)
    assert resp.status_code == 400

def test_delete_item(client):
    client.post("/inventory", json={"name": "Rice Milk"})
    resp = client.delete("/inventory/1")
    assert resp.status_code == 200

    resp2 = client.get("/inventory/1")
    assert resp2.status_code == 404

def test_delete_item_not_found(client):
    resp = client.delete("/inventory/999")
    assert resp.status_code == 404

@patch("app.fetch_product_by_barcode")
def test_fetch_and_add_by_barcode(mock_fetch, client):
    mock_fetch.return_value = (
        {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Almonds, water",
        },
        None,
    )
    resp = client.post("/inventory/fetch/barcode/1234567890123")
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["name"] == "Organic Almond Milk"
    assert data["barcode"] == "1234567890123"

@patch("app.fetch_product_by_barcode")
def test_fetch_by_barcode_not_found(mock_fetch, client):
    mock_fetch.return_value = (None, None)
    resp = client.post("/inventory/fetch/barcode/0000000000000")
    assert resp.status_code == 404

@patch("app.fetch_product_by_barcode")
def test_fetch_by_barcode_api_error(mock_fetch, client):
    mock_fetch.return_value = (None, "Connection timed out")
    resp = client.post("/inventory/fetch/barcode/0000000000000")
    assert resp.status_code == 502

@patch("app.search_products_by_name")
def test_fetch_search_by_name(mock_search, client):
    mock_search.return_value = (
        [{"product_name": "Oat Milk", "brands": "Oatly"}],
        None,
    )
    resp = client.get("/inventory/fetch/search?name=oat milk")
    assert resp.status_code == 200
    assert len(resp.get_json()) == 1

def test_fetch_search_missing_param(client):
    resp = client.get("/inventory/fetch/search")
    assert resp.status_code == 400

@patch("app.requests.get")
def test_fetch_product_by_barcode_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "status": 1,
        "product": {"product_name": "Test Product"},
    }
    mock_get.return_value = mock_resp

    product, error = app_module.fetch_product_by_barcode("123")
    assert error is None
    assert product["product_name"] == "Test Product"

@patch("app.requests.get")
def test_fetch_product_by_barcode_not_found_helper(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"status": 0}
    mock_get.return_value = mock_resp
    product, error = app_module.fetch_product_by_barcode("000")
    assert product is None
    assert error is None

@patch("app.requests.get")
def test_fetch_product_by_barcode_request_error(mock_get):
    mock_get.side_effect = requests.RequestException("timeout")
    product, error = app_module.fetch_product_by_barcode("123")
    assert product is None
    assert error == "timeout"

@patch("app.requests.get")
def test_search_products_by_name_helper(mock_get):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {
        "products": [
            {
                "product_name": "Almond Milk",
                "brands": "Silk",
                "code": "111",
                "ingredients_text": "almonds, water",
            }
        ]
    }
    mock_get.return_value = mock_resp

    results, error = app_module.search_products_by_name("almond milk")
    assert error is None
    assert len(results) == 1
    assert results[0]["product_name"] == "Almond Milk"

@patch("app.requests.get")
def test_search_products_by_name_request_error(mock_get):
    mock_get.side_effect = requests.RequestException("boom")
    results, error = app_module.search_products_by_name("almond milk")
    assert results == []
    assert error == "boom"