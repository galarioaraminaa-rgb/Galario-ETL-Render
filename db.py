import os
from sqlalchemy import create_engine

_engine = None

def get_engine():
    """Return a shared SQLAlchemy engine for PostgreSQL."""
    global _engine
    if _engine is None:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise RuntimeError("DATABASE_URL environment variable is not set.")
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        _engine = create_engine(database_url)
    return _engine
