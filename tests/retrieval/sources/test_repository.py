import pytest
import json
from pathlib import Path

from app.retrieval.sources.repository import SourceRepository
from app.retrieval.sources.base import Source
from app.retrieval.models import SourceConfig, SourceType, UpdateFrequency


class TestSourceRepository:
    """Tests for the SourceRepository class."""
    
    def test_init_loads_existing_sources(self, temp_storage_path):
        """Test that repository loads existing sources on init."""
        source_data = {
            "id": "test-source",
            "name": "Test Source", 
            "source_type": "rss",
            "parser_id": "mock_parser",
            "update_frequency": "hourly",
            "config": {"url": "https://example.com/feed.xml"},
            "tags": ["test"],
            "enabled": True
        }
        
        with open(temp_storage_path, "w") as f:
            json.dump([source_data], f)
            
        repo = SourceRepository(temp_storage_path)
        
        assert len(repo.sources) == 1
        assert repo.sources["test-source"].config.name == "Test Source"
    
    def test_add_source_generates_id(self, temp_storage_path):
        """Test that adding a source without ID generates one based on name."""
        repo = SourceRepository(temp_storage_path)
        
        source = repo.add({
            "name": "Test Source",
            "source_type": "rss",
            "parser_id": "mock_parser",
            "config": {"url": "https://example.com/feed.xml"}
        })
        
        assert source.config.id is not None
        assert source.config.id.startswith("test-source-")
        
        # Verify saved to file
        with open(temp_storage_path, "r") as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]["id"] == source.config.id
    
    def test_update_source_preserves_id(self, temp_storage_path):
        """Test that updating a source preserves its ID."""
        repo = SourceRepository(temp_storage_path)
        
        # Add initial source
        source = repo.add({
            "id": "test-source",
            "name": "Test Source",
            "source_type": "rss",
            "parser_id": "mock_parser",
            "config": {"url": "https://example.com/feed.xml"}
        })
        
        # Update with new data
        updated = repo.update("test-source", {
            "name": "Updated Name",
            "source_type": SourceType.RSS,
            "parser_id": "mock_parser",
            "config": {"url": "https://example.com/new.xml"}
        })
        
        assert updated.config.id == "test-source"
        assert updated.config.name == "Updated Name"
        assert updated.config.config["url"] == "https://example.com/new.xml"
    
    def test_get_by_type_filters_correctly(self, temp_storage_path):
        """Test that get_by_type returns only sources of specified type."""
        repo = SourceRepository(temp_storage_path)
        
        # Add sources of different types
        repo.add({
            "id": "rss1",
            "name": "RSS Source",
            "source_type": "rss",
            "parser_id": "mock_parser",
            "config": {"url": "https://example.com/feed.xml"}
        })
        
        repo.add({
            "id": "webpage1", 
            "name": "Webpage Source",
            "source_type": "webpage",
            "parser_id": "mock_parser",
            "config": {"url": "https://example.com"}
        })
        
        rss_sources = repo.get_by_type(SourceType.RSS)
        webpage_sources = repo.get_by_type(SourceType.WEBPAGE)
        
        assert len(rss_sources) == 1
        assert len(webpage_sources) == 1
        assert rss_sources[0].config.id == "rss1"
        assert webpage_sources[0].config.id == "webpage1"