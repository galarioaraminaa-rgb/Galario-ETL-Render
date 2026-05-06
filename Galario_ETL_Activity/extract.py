import pandas as pd
import sqlite3
import os

DATA_SOURCE = "data/source"
STAGING_DB = "data/Staging/staging.db"


def extract_store(store_name):
    """
    Extract CSV files from a specific store
    and load them into the staging SQLite database.
    """
    conn = sqlite3.connect(STAGING_DB)
    store_path = os.path.join(DATA_SOURCE, store_name)

    for file in os.listdir(store_path):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(store_path, file))
            table_name = f"{store_name}_{file.replace('.csv','')}"
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            print(f"[EXTRACT] {table_name}")

    conn.close()


def run_extract():
    """Extract both Japan & Myanmar stores into staging."""
    os.makedirs("data/Staging", exist_ok=True)
    extract_store("japan_store")
    extract_store("myanmar_store")