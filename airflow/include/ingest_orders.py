import os
import logging
from io import StringIO

import requests
import duckdb
import pandas as pd

logger = logging.getLogger(__name__)

API_URL = os.getenv("MOCKAROO_URL", "https://api.mockaroo.com/api/ceaad240")
DB_PATH = os.getenv("DUCKDB_PATH", "/opt/airflow/data/ecommerce.duckdb")


def extract_from_api(count: int = 1000) -> str:
    api_key = os.getenv("MOCKAROO_API_KEY")
    if not api_key:
        raise ValueError("MOCKAROO_API_KEY is not configured")

    response = requests.get(
        API_URL, params={"count": count, "key": api_key}, timeout=60
    )
    response.raise_for_status()
    return response.text


def to_dataframe(csv_data: str) -> pd.DataFrame:
    """Fonction pure : testable sans API ni base."""
    if not csv_data.strip():
        raise ValueError("Mockaroo returned an empty response")
    df = pd.read_csv(StringIO(csv_data), dtype=str)
    if df.empty:
        raise ValueError("No records found in the API response")
    return df


def load_raw(df: pd.DataFrame, db_path: str = DB_PATH) -> int:
    conn = duckdb.connect(db_path)
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.register("staging_orders", df)
        conn.execute(
            "CREATE OR REPLACE TABLE raw.orders AS SELECT * FROM staging_orders"
        )
        conn.unregister("staging_orders")
        return conn.execute("SELECT COUNT(*) FROM raw.orders").fetchone()[0]
    finally:
        conn.close()


def run() -> int:
    df = to_dataframe(extract_from_api())
    n = load_raw(df)
    logger.info("Loaded %s rows into raw.orders", n)
    return n