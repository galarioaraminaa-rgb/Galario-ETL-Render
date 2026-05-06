# transform.py
import pandas as pd
import sqlite3
import os

STAGING_DB = "data/Staging/staging.db"
TRANSFORM_DB = "data/Transformation/transformation.db"


def transform_and_clean():
    """
    Cleans and standardizes data from staging layer
    and stores results in the transformation layer.
    """

    os.makedirs("data/Transformation", exist_ok=True)

    staging_conn = sqlite3.connect(STAGING_DB)
    transform_conn = sqlite3.connect(TRANSFORM_DB)

    # Load sales data only (simple, not complex)
    japan_sales = pd.read_sql(
        "SELECT * FROM japan_store_sales_data",
        staging_conn
    )

    myanmar_sales = pd.read_sql(
        "SELECT * FROM myanmar_store_sales_data",
        staging_conn
    )

    # Basic cleaning
    japan_sales = japan_sales.dropna().drop_duplicates()
    myanmar_sales = myanmar_sales.dropna().drop_duplicates()

    # Add store label
    japan_sales["store"] = "Japan"
    myanmar_sales["store"] = "Myanmar"

    # Currency standardization (example)
    if "price" in myanmar_sales.columns:
        myanmar_sales["price"] = myanmar_sales["price"] * 150  # USD → JPY

    # Save transformed data
    japan_sales.to_sql(
        "japan_sales_clean",
        transform_conn,
        if_exists="replace",
        index=False
    )

    myanmar_sales.to_sql(
        "myanmar_sales_clean",
        transform_conn,
        if_exists="replace",
        index=False
    )

    print("[TRANSFORM] Data cleaned and standardized")

    staging_conn.close()
    transform_conn.close()
