import pandas as pd
from db import get_connection


def transform_and_clean():
    """Clean and standardize staging data → transformation tables in PostgreSQL."""
    conn = get_connection()

    japan_sales = pd.read_sql("SELECT * FROM staging_japan_store_sales_data", conn)
    myanmar_sales = pd.read_sql("SELECT * FROM staging_myanmar_store_sales_data", conn)

    # Basic cleaning
    japan_sales = japan_sales.dropna().drop_duplicates()
    myanmar_sales = myanmar_sales.dropna().drop_duplicates()

    # Add store label
    japan_sales["store"] = "Japan"
    myanmar_sales["store"] = "Myanmar"

    # Currency standardization: Myanmar price (USD) → JPY
    if "price" in myanmar_sales.columns:
        myanmar_sales["price"] = myanmar_sales["price"] * 150

    # Write to transformation tables
    japan_sales.to_sql("transform_japan_sales_clean", conn, if_exists="replace", index=False)
    myanmar_sales.to_sql("transform_myanmar_sales_clean", conn, if_exists="replace", index=False)

    print(f"[TRANSFORM] Japan rows: {len(japan_sales)} | Myanmar rows: {len(myanmar_sales)}")
    conn.close()
    print("[TRANSFORM] Done.")
