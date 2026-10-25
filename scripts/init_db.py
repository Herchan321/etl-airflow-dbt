import logging

import duckdb

# =========================
# 1. Configure logging
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# =========================
# 2. Connect to DuckDB
# =========================
def connect_db(db_path="ecommerce.duckdb"):
    try:
        conn = duckdb.connect(db_path)
        logger.info("Connected to DuckDB: %s", db_path)
        return conn

    except Exception:
        logger.exception("Failed to connect to DuckDB")
        raise


# =========================
# 3. Create database schemas
# =========================
def create_schemas(conn):
    try:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute("CREATE SCHEMA IF NOT EXISTS refined")
        conn.execute("CREATE SCHEMA IF NOT EXISTS reported")

        logger.info("Database schemas created successfully")

    except Exception:
        logger.exception("Failed to create database schemas")
        raise


# =========================
# 4. Create raw table
# =========================
def create_raw_table(conn):
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS raw.orders (
                order_id VARCHAR,
                order_date VARCHAR,
                customer_id VARCHAR,
                customer_name VARCHAR,
                customer_email VARCHAR,
                country VARCHAR,
                city VARCHAR,
                product_id VARCHAR,
                product_name VARCHAR,
                category VARCHAR,
                quantity VARCHAR,
                unit_price VARCHAR,
                discount VARCHAR,
                shipping_cost VARCHAR,
                payment_method VARCHAR
            )
        """)

        logger.info("Table raw.orders created successfully")

    except Exception:
        logger.exception("Failed to create raw.orders")
        raise


# =========================
# 5. Create refined table
# =========================
def create_refined_table(conn):
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS refined.orders (
                order_id INTEGER,
                order_date DATE,
                customer_id INTEGER,
                customer_name VARCHAR,
                customer_email VARCHAR,
                country VARCHAR,
                city VARCHAR,
                product_id INTEGER,
                product_name VARCHAR,
                category VARCHAR,
                quantity INTEGER,
                unit_price DECIMAL(10, 2),
                discount DECIMAL(10, 2),
                shipping_cost DECIMAL(10, 2),
                payment_method VARCHAR,
                total_amount DECIMAL(12, 2)
            )
        """)

        logger.info("Table refined.orders created successfully")

    except Exception:
        logger.exception("Failed to create refined.orders")
        raise


# =========================
# 6. Create reported table
# =========================
def create_reported_table(conn):
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reported.sales (
                order_id INTEGER,
                order_date DATE,
                customer_id INTEGER,
                country VARCHAR,
                city VARCHAR,
                product_id INTEGER,
                product_name VARCHAR,
                category VARCHAR,
                quantity INTEGER,
                unit_price DECIMAL(10, 2),
                discount DECIMAL(10, 2),
                shipping_cost DECIMAL(10, 2),
                total_amount DECIMAL(12, 2),
                payment_method VARCHAR
            )
        """)

        logger.info("Table reported.sales created successfully")

    except Exception:
        logger.exception("Failed to create reported.sales")
        raise


# =========================
# 7. Main function
# =========================
def main():
    conn = None

    try:
        conn = connect_db()

        create_schemas(conn)
        create_raw_table(conn)
        create_refined_table(conn)
        create_reported_table(conn)

        logger.info("Database initialization completed successfully")

    except Exception:
        logger.exception("Database initialization failed")
        raise

    finally:
        if conn is not None:
            conn.close()
            logger.info("DuckDB connection closed")


if __name__ == "__main__":
    main()