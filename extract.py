import pandas as pd
import os
from db import get_engine

DATA_SOURCE = "data/source"


def extract_store(store_name, engine):
    """Extract CSVs from a store folder into PostgreSQL staging tables."""
    store_path = os.path.join(DATA_SOURCE, store_name)

    for file in os.listdir(store_path):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(store_path, file))
            df.columns = [c.strip().strip("'").lower().replace(" ", "_") for c in df.columns]
            table_name = f"staging_{store_name}_{file.replace('.csv', '').lower()}"
            df.to_sql(table_name, engine, if_exists="replace", index=False)
            print(f"[EXTRACT] Loaded → {table_name} ({len(df)} rows)")


def run_extract():
    """Extract both Japan & Myanmar stores into PostgreSQL staging layer."""
    engine = get_engine()
    extract_store("japan_store", engine)
    extract_store("myanmar_store", engine)
    print("[EXTRACT] Done.")
