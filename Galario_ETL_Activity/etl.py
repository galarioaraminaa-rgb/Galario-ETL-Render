import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import create_engine, text
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")

DATA_SOURCE = os.path.join(os.path.dirname(__file__), "data", "source")


def get_engine():
    url = DATABASE_URL
    # Render gives postgres:// but SQLAlchemy needs postgresql://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return create_engine(url)


def init_db():
    """Create schema tables if they don't exist."""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS etl_logs (
                id SERIAL PRIMARY KEY,
                stage VARCHAR(50),
                message TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.commit()
    logger.info("DB initialized")


def log_to_db(engine, stage, message):
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO etl_logs (stage, message) VALUES (:stage, :msg)"),
            {"stage": stage, "msg": message}
        )
        conn.commit()


# ─── EXTRACT ────────────────────────────────────────────────────────────────

def extract_store(engine, store_name, logs):
    store_path = os.path.join(DATA_SOURCE, store_name)
    files = [f for f in os.listdir(store_path) if f.endswith(".csv")]

    for file in files:
        df = pd.read_csv(os.path.join(store_path, file))
        table_name = f"staging_{store_name}_{file.replace('.csv', '').lower()}"
        df.to_sql(table_name, engine, if_exists="replace", index=False)
        msg = f"Extracted {len(df)} rows → {table_name}"
        logger.info(msg)
        logs.append(("EXTRACT", msg))
        log_to_db(engine, "EXTRACT", msg)


def run_extract(engine, logs):
    extract_store(engine, "japan_store", logs)
    extract_store(engine, "myanmar_store", logs)


# ─── TRANSFORM ──────────────────────────────────────────────────────────────

def run_transform(engine, logs):
    japan_sales = pd.read_sql("SELECT * FROM staging_japan_store_sales_data", engine)
    myanmar_sales = pd.read_sql("SELECT * FROM staging_myanmar_store_sales_data", engine)

    japan_sales = japan_sales.dropna().drop_duplicates()
    myanmar_sales = myanmar_sales.dropna().drop_duplicates()

    japan_sales["store"] = "Japan"
    myanmar_sales["store"] = "Myanmar"

    # Currency standardisation: Myanmar price (USD) → JPY
    if "price" in myanmar_sales.columns:
        myanmar_sales["price"] = myanmar_sales["price"] * 150

    japan_sales.to_sql("transform_japan_sales_clean", engine, if_exists="replace", index=False)
    myanmar_sales.to_sql("transform_myanmar_sales_clean", engine, if_exists="replace", index=False)

    msg = f"Transformed Japan({len(japan_sales)} rows) Myanmar({len(myanmar_sales)} rows)"
    logger.info(msg)
    logs.append(("TRANSFORM", msg))
    log_to_db(engine, "TRANSFORM", msg)


# ─── LOAD ────────────────────────────────────────────────────────────────────

def run_load(engine, logs):
    japan = pd.read_sql("SELECT * FROM transform_japan_sales_clean", engine)
    myanmar = pd.read_sql("SELECT * FROM transform_myanmar_sales_clean", engine)

    big_table = pd.concat([japan, myanmar], ignore_index=True)
    big_table.to_sql("presentation_big_table", engine, if_exists="replace", index=False)

    msg = f"Loaded BIG TABLE with {len(big_table)} total rows"
    logger.info(msg)
    logs.append(("LOAD", msg))
    log_to_db(engine, "LOAD", msg)


# ─── FULL PIPELINE ───────────────────────────────────────────────────────────

def run_etl():
    logs = []
    try:
        engine = get_engine()
        init_db()

        logs.append(("START", "ETL pipeline started"))
        run_extract(engine, logs)
        run_transform(engine, logs)
        run_load(engine, logs)
        logs.append(("DONE", "ETL pipeline completed successfully"))
        return {"success": True, "logs": logs}
    except Exception as e:
        error_msg = str(e)
        logger.error(error_msg)
        logs.append(("ERROR", error_msg))
        return {"success": False, "logs": logs}


def get_big_table_preview(limit=50):
    try:
        engine = get_engine()
        df = pd.read_sql(f"SELECT * FROM presentation_big_table LIMIT {limit}", engine)
        return df.to_dict(orient="records"), list(df.columns)
    except Exception:
        return [], []


def get_etl_logs(limit=30):
    try:
        engine = get_engine()
        df = pd.read_sql(
            "SELECT stage, message, created_at FROM etl_logs ORDER BY created_at DESC LIMIT %s",
            engine, params=(limit,)
        )
        return df.to_dict(orient="records")
    except Exception:
        return []
