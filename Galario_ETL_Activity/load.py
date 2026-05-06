# load.py
import sqlite3
import pandas as pd
import os

TRANSFORM_DB = "data/Transformation/transformation.db"
PRESENTATION_DB = "data/Presentation/BIG_TABLE.db"


def build_big_table():
    """
    Combines transformed Japan and Myanmar data
    into a single BIG TABLE in the presentation layer.
    """

    # Ensure presentation folder exists
    os.makedirs("data/Presentation", exist_ok=True)

    transform_conn = sqlite3.connect(TRANSFORM_DB)
    presentation_conn = sqlite3.connect(PRESENTATION_DB)

    japan = pd.read_sql(
        "SELECT * FROM japan_sales_clean",
        transform_conn
    )

    myanmar = pd.read_sql(
        "SELECT * FROM myanmar_sales_clean",
        transform_conn
    )

    big_table = pd.concat([japan, myanmar], ignore_index=True)

    big_table.to_sql(
        "big_table",
        presentation_conn,
        if_exists="replace",
        index=False
    )

    print("[LOAD] BIG TABLE created in presentation layer")

    transform_conn.close()
    presentation_conn.close()
