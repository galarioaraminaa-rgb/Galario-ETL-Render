import pandas as pd
from db import get_connection


def build_big_table():
    """Combine transformed Japan & Myanmar data into a single BIG TABLE in PostgreSQL."""
    conn = get_connection()

    japan = pd.read_sql("SELECT * FROM transform_japan_sales_clean", conn)
    myanmar = pd.read_sql("SELECT * FROM transform_myanmar_sales_clean", conn)

    big_table = pd.concat([japan, myanmar], ignore_index=True)
    big_table.to_sql("presentation_big_table", conn, if_exists="replace", index=False)

    print(f"[LOAD] BIG TABLE created — {len(big_table)} total rows.")
    conn.close()
    print("[LOAD] Done.")
