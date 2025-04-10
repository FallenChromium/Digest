from digest.config.settings import settings
from typing import Generator
from sqlmodel import Session, SQLModel, create_engine, text
from pathlib import Path

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
)

def create_db_and_tables() -> None:
    """Create database and tables."""
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))


def get_session() -> Generator[Session, None, None]:
    """Get database session."""
    with Session(engine) as session:
        yield session

def get_long_session() -> Session:
    return Session(engine)
