import pytest
from datetime import datetime
from sqlmodel import Session, SQLModel, create_engine, delete
from sqlalchemy import text
from uuid import UUID
import os

from digest.config.settings import settings
from digest.database.models.source import Source
from digest.database.repositories.sources import SourceRepository
from digest.database.enums import SourceType, UpdateFrequency


def get_test_db_url():
    """Get the test database URL, creating a new test database if needed."""
    base_db_url = settings.DATABASE_URL
    # Create a unique test database name
    test_db_name = "test_digest"
    # Get the base URL without the database name
    base_url = base_db_url.rsplit('/', 1)[0]
    return f"{base_url}/{test_db_name}"


@pytest.fixture(scope="session")
def db_url():
    """Create and drop test database."""
    base_db_url = settings.DATABASE_URL
    test_db_url = get_test_db_url()
    
    # Connect to default database to create/drop test database
    engine = create_engine(base_db_url)
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))  # Close any open transactions
        conn.execute(text(f'DROP DATABASE IF EXISTS test_digest'))
        conn.execute(text("COMMIT"))
        conn.execute(text(f'CREATE DATABASE test_digest'))
    
    engine.dispose()
    
    # Create all tables in the test database
    test_engine = create_engine(test_db_url)
    SQLModel.metadata.create_all(test_engine)
    test_engine.dispose()
    
    yield test_db_url
    
    # Cleanup: drop test database
    engine = create_engine(base_db_url)
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        # Terminate all connections to the test database
        conn.execute(text(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'test_digest'
            AND pid <> pg_backend_pid()
        """))
        conn.execute(text("COMMIT"))
        conn.execute(text(f'DROP DATABASE IF EXISTS test_digest'))


@pytest.fixture
def engine(db_url):
    """Create a test database engine."""
    engine = create_engine(db_url)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine):
    """Create a test database session."""
    with Session(engine) as session:
        yield session
        session.rollback()


@pytest.fixture
def repo(session):
    """Create a test source repository."""
    return SourceRepository(session)


@pytest.fixture(autouse=True)
def cleanup_db(session):
    """Clean up the database after each test."""
    yield
    session.exec(delete(Source))
    session.commit()


class TestSourceRepository:
    """Tests for the SourceRepository class."""
    
    def test_create_source(self, repo):
        """Test creating a new source."""
        source = Source(
            name="Test Source",
            source_type=SourceType.RSS,
            parser_id="mock_parser",
            config={"url": "https://example.com/feed.xml"},
            enabled=True
        )
        
        created = repo.create(source)
        
        assert isinstance(created.id, str)
        assert created.name == "Test Source"
        assert created.source_type == SourceType.RSS
        assert created.config["url"] == "https://example.com/feed.xml"
        assert created.enabled is True
        assert isinstance(created.created_at, datetime)
        assert isinstance(created.updated_at, datetime)
    
    def test_get_by_id_returns_source(self, repo):
        """Test retrieving a source by ID."""
        source = Source(
            name="Test Source",
            source_type=SourceType.RSS,
            parser_id="mock_parser",
            config={"url": "https://example.com/feed.xml"}
        )
        created = repo.create(source)
        
        retrieved = repo.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "Test Source"
    
    def test_update_source(self, repo):
        """Test updating a source."""
        source = Source(
            name="Test Source",
            source_type=SourceType.RSS,
            parser_id="mock_parser",
            config={"url": "https://example.com/feed.xml"}
        )
        created = repo.create(source)
        
        # Update source
        created.name = "Updated Name"
        created.config = {"url": "https://example.com/new.xml"}
        updated = repo.update(created)
        
        assert updated.id == created.id
        assert updated.name == "Updated Name"
        assert updated.config["url"] == "https://example.com/new.xml"
    
    def test_get_by_type_filters_correctly(self, repo):
        """Test that get_by_type returns only sources of specified type."""
        # Add sources of different types
        rss_source = Source(
            name="RSS Source",
            source_type=SourceType.RSS,
            parser_id="mock_parser",
            config={"url": "https://example.com/feed.xml"}
        )
        webpage_source = Source(
            name="Webpage Source",
            source_type=SourceType.WEBPAGE,
            parser_id="mock_parser",
            config={"url": "https://example.com"}
        )
        
        repo.create(rss_source)
        repo.create(webpage_source)
        
        rss_sources = repo.get_by_type(SourceType.RSS)
        webpage_sources = repo.get_by_type(SourceType.WEBPAGE)
        
        assert len(rss_sources) == 1
        assert len(webpage_sources) == 1
        assert rss_sources[0].source_type == SourceType.RSS
        assert webpage_sources[0].source_type == SourceType.WEBPAGE
        
    def test_get_enabled_sources(self, repo):
        """Test retrieving only enabled sources."""
        enabled_source = Source(
            name="Enabled Source",
            source_type=SourceType.RSS,
            parser_id="mock_parser",
            enabled=True
        )
        disabled_source = Source(
            name="Disabled Source",
            source_type=SourceType.RSS,
            parser_id="mock_parser",
            enabled=False
        )
        
        repo.create(enabled_source)
        repo.create(disabled_source)
        
        enabled_sources = repo.get_enabled()
        
        assert len(enabled_sources) == 1
        assert enabled_sources[0].name == "Enabled Source"
        assert enabled_sources[0].enabled is True