from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# For dev: simple SQLite file in the current directory.
DATABASE_URL = "sqlite:///./refcue.db"


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Needed for SQLite + FastAPI
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
