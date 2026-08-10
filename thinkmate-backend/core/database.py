"""
PostgreSQL connection layer. Everything else imports `get_db` as a
FastAPI dependency — never opens its own session.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from config.settings import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a session, always closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Call once on app startup (or use Alembic in prod)."""
    from models import db_models  # noqa: F401  (import so metadata registers)
    Base.metadata.create_all(bind=engine)
