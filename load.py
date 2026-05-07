import pandas as pd
from db import get_engine


def build_big_table():
    """Combine transformed Japan & Myanmar data into a single BIG TABLE in PostgreSQL."""
    engine = get_engine()

    japan = pd.read_sql("SELECT * FROM transform_japan_sales_clean", engine)
    myanmar = pd.read_sql("SELECT * FROM transform_myanmar_sales_clean", engine)

    big_table = pd.concat([japan, myanmar], ignore_index=True)
    big_table.to_sql("presentation_big_table", engine, if_exists="replace", index=False)

    print(f"[LOAD] BIG TABLE created — {len(big_table)} total rows.")
    print("[LOAD] Done.")
