import duckdb
import pandas as pd
import pytest
import requests

from include import ingest_orders
from include.ingest_orders import to_dataframe, load_raw, extract_from_api


def test_to_dataframe_ok():
    df = to_dataframe("order_id,quantity\n1,2\n3,4\n")
    assert len(df) == 2
    assert list(df.columns) == ["order_id", "quantity"]


def test_to_dataframe_keeps_strings():
    # la couche raw garde tout en texte : le typage se fait dans dbt
    df = to_dataframe("order_id,unit_price\n1,10.50\n")
    assert df["unit_price"].iloc[0] == "10.50"


def test_to_dataframe_empty():
    with pytest.raises(ValueError):
        to_dataframe("   ")


def test_to_dataframe_header_only():
    with pytest.raises(ValueError):
        to_dataframe("order_id,quantity\n")


def test_load_raw(tmp_path):
    db = str(tmp_path / "t.duckdb")
    df = pd.DataFrame({"order_id": ["1", "2"], "quantity": ["3", "4"]})
    assert load_raw(df, db) == 2
    con = duckdb.connect(db)
    assert con.execute("select count(*) from raw.orders").fetchone()[0] == 2
    con.close()


def test_load_raw_replaces_snapshot(tmp_path):
    db = str(tmp_path / "t.duckdb")
    load_raw(pd.DataFrame({"order_id": ["1", "2", "3"]}), db)
    assert load_raw(pd.DataFrame({"order_id": ["9"]}), db) == 1


def test_extract_requires_api_key(monkeypatch):
    monkeypatch.delenv("MOCKAROO_API_KEY", raising=False)
    with pytest.raises(ValueError, match="MOCKAROO_API_KEY"):
        extract_from_api()


def test_extract_calls_api(monkeypatch):
    monkeypatch.setenv("MOCKAROO_API_KEY", "fake")

    class FakeResp:
        text = "order_id\n1\n"
        def raise_for_status(self):
            pass

    captured = {}
    def fake_get(url, params, timeout):
        captured["params"] = params
        return FakeResp()

    monkeypatch.setattr(requests, "get", fake_get)
    assert extract_from_api(count=5) == "order_id\n1\n"
    assert captured["params"]["count"] == 5