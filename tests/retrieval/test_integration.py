import pytest
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from digest.retrieval.models import ContentPiece, SourceConfig, SourceType, UpdateFrequency
from digest.retrieval.sources.repository import SourceRepository
from digest.retrieval.sources.base import Source
from digest.retrieval.processors.pipeline import ProcessingPipeline
from digest.retrieval.processors.base import BaseProcessor, ProcessorRegistry


class TestRetrievalIntegration:
    """Integration tests for the retrieval pipeline."""
    
    @pytest.fixture
    def temp_storage_path(self):
        """Create a temporary file for source storage."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
            path = Path(tmp.name)
            yield path
            # Clean up after test
            if path.exists():
                path.unlink()
    
    @pytest.fixture
    def mock_processor(self):
        """Create a mock processor."""
        class TestProcessor(BaseProcessor):
            processor_id = "test_processor"
            name = "Test Processor"
            description = "A test processor"
            
            @classmethod
            def config_schema(cls):
                return {}
            
            async def process(self, content):
                processed = ContentPiece(**content.model_dump())
                processed.content = f"Processed: {processed.content}"
                processed.metadata["processed_by"] = "test_processor"
                return processed
        
        # Register the processor
        if "test_processor" not in ProcessorRegistry._processors:
            ProcessorRegistry.register(TestProcessor)
        
        processor = TestProcessor()
        yield processor
        
        # Clean up
        if "test_processor" in ProcessorRegistry._processors:
            del ProcessorRegistry._processors["test_processor"]
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self, temp_storage_path, mock_processor):
        """Test the full retrieval pipeline."""
        # Create a source repository
        repo = SourceRepository(temp_storage_path)
        
        # Add a source with the mock parser
        source_config = {
            "id": "test-source",
            "name": "Test Source",
            "source_type": "rss",
            "parser_id": "mock_parser",
            "update_frequency": "hourly",
            "config": {"url": "https://example.com/feed.xml"}
        }
        source = repo.add(source_config)
        
        # Create a processing pipeline
        pipeline = ProcessingPipeline("test-pipeline", [mock_processor])
        
        # Create a content callback that processes content through the pipeline
        processed_content = []
        
        async def content_callback(content_pieces):
            # Process the content through the pipeline
            processed = await pipeline.process_batch(content_pieces)
            processed_content.extend(processed)
        
        # Manually trigger the source
        source_obj = repo.get("test-source")
        content = await source_obj.fetch()
        await content_callback(content)
        
        # Check the results
        assert len(processed_content) == 2
        assert all(piece.processed for piece in processed_content)
        assert all(piece.content.startswith("Processed:") for piece in processed_content)
        assert all("processed_by" in piece.metadata for piece in processed_content)
        assert all(piece.metadata["processed_by"] == "test_processor" for piece in processed_content)
    
    @pytest.mark.asyncio
    async def test_source_to_processor_pipeline(self, temp_storage_path, mock_processor):
        """Test the pipeline from source to processor."""
        # Create a source repository
        repo = SourceRepository(temp_storage_path)
        
        # Add a source with the mock parser
        source_config = {
            "id": "pipeline-source",
            "name": "Pipeline Source",
            "source_type": "rss",
            "parser_id": "mock_parser",
            "update_frequency": "hourly",
            "config": {"url": "https://example.com/feed.xml"}
        }
        repo.add(source_config)
        
        # Create a processing pipeline
        pipeline = ProcessingPipeline("pipeline-test", [mock_processor])
        
        # Create a list to store processed content
        processed_content = []
        
        # Create a content callback
        async def content_callback(content_pieces):
            # Process the content through the pipeline
            processed = await pipeline.process_batch(content_pieces)
            processed_content.extend(processed)
        
        # Create a mock for the source fetch method to track calls
        source = repo.get("pipeline-source")
        original_fetch = source.fetch
        
        # Patch the fetch method to use the original but track calls
        with patch.object(source, 'fetch', side_effect=original_fetch) as mock_fetch:
            # Manually trigger the source and process the content
            content = await source.fetch()
            await content_callback(content)
            
            # Check if the source was fetched
            mock_fetch.assert_called_once()
            
            # Check the processed content
            assert len(processed_content) == 2
            assert all(piece.processed for piece in processed_content)
            assert all(piece.content.startswith("Processed:") for piece in processed_content)
            assert all(piece.source_id == "pipeline-source" for piece in processed_content)
            assert all("processed_by" in piece.metadata for piece in processed_content)
            assert all(piece.metadata["processed_by"] == "test_processor" for piece in processed_content) 