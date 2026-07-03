import os
import sys
from argparse import Namespace
from unittest.mock import MagicMock, patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cli 

@patch("cli.requests.get")
def test_cmd_list(mock_get, capsys):
    mock_resp = MagicMock()
    mock_resp.json.return_value = [{"id": 1, "name": "Milk"}]
    mock_get.return_value = mock_resp

    cli.cmd_list(Namespace())
    captured = capsys.readouterr()
    assert "Milk" in captured.out

@patch("cli.requests.get")
def test_cmd_view_found(mock_get, capsys):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": 1, "name": "Milk"}
    mock_get.return_value = mock_resp

    cli.cmd_view(Namespace(id=1))
    captured = capsys.readouterr()
    assert "Milk" in captured.out

@patch("cli.requests.get")
def test_cmd_view_not_found(mock_get, capsys):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp

    cli.cmd_view(Namespace(id=99))
    captured = capsys.readouterr()
    assert "not found" in captured.out

@patch("cli.requests.post")
def test_cmd_add(mock_post, capsys):
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"id": 1, "name": "Bread"}
    mock_post.return_value = mock_resp

    args = Namespace(name="Bread", brand="", barcode="", price=2.5, stock=10)
    cli.cmd_add(args)
    captured = capsys.readouterr()
    assert "Bread" in captured.out

@patch("cli.requests.patch")
def test_cmd_update(mock_patch, capsys):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": 1, "stock": 20}
    mock_patch.return_value = mock_resp

    args = Namespace(id=1, name=None, price=None, stock=20)
    cli.cmd_update(args)
    captured = capsys.readouterr()
    assert "20" in captured.out

def test_cmd_update_nothing_to_update(capsys):
    args = Namespace(id=1, name=None, price=None, stock=None)
    cli.cmd_update(args)
    captured = capsys.readouterr()
    assert "Nothing to update" in captured.out

@patch("cli.requests.delete")
def test_cmd_delete(mock_delete, capsys):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"message": "Item 1 deleted"}
    mock_delete.return_value = mock_resp

    cli.cmd_delete(Namespace(id=1))
    captured = capsys.readouterr()
    assert "deleted" in captured.out

@patch("cli.requests.post")
def test_cmd_find_by_barcode(mock_post, capsys):
    mock_resp = MagicMock()
    mock_resp.status_code = 201
    mock_resp.json.return_value = {"id": 1, "name": "Almond Milk"}
    mock_post.return_value = mock_resp

    args = Namespace(barcode="123", name=None)
    cli.cmd_find(args)
    captured = capsys.readouterr()
    assert "Almond Milk" in captured.out

@patch("cli.requests.get")
def test_cmd_find_by_name(mock_get, capsys):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [{"product_name": "Oat Milk"}]
    mock_get.return_value = mock_resp

    args = Namespace(barcode=None, name="oat milk")
    cli.cmd_find(args)
    captured = capsys.readouterr()
    assert "Oat Milk" in captured.out

def test_cmd_find_no_args(capsys):
    args = Namespace(barcode=None, name=None)
    cli.cmd_find(args)
    captured = capsys.readouterr()
    assert "Provide --barcode or --name" in captured.out