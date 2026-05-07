import os
from sqlalchemy import create_engine

def get_connection():
    """Return a SQLAlchemy engine connection to PostgreSQL."""
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    # SQLAlchemy requires postgresql:// not postgres://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    engine = create_engine(database_url)
    return engine.connect()
