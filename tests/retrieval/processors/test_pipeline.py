import pytest
import asyncio
from unittest.mock import MagicMock, patch

from app.retrieval.processors.pipeline import ProcessingPipeline
from app.retrieval.processors.base import BaseProcessor, ProcessorRegistry
from app.retrieval.models import ContentPiece


class TestProcessingPipeline:
    """Tests for the ProcessingPipeline class."""
    
    @pytest.fixture
    def mock_processor(self):
        """Create a mock processor."""
        processor = MagicMock(spec=BaseProcessor)
        processor.processor_id = "mock_processor"
        processor.config = {}
        
        async def mock_process(content):
            # Create a new content piece with modified content
            processed = ContentPiece(**content.model_dump())
            processed.content = f"Processed by mock: {processed.content}"
            return processed
        
        # Use side_effect to simulate the async function
        processor.process.side_effect = mock_process
        return processor
    
    @pytest.fixture
    def mock_processor2(self):
        """Create another mock processor."""
        processor = MagicMock(spec=BaseProcessor)
        processor.processor_id = "mock_processor2"
        processor.config = {}
        
        async def mock_process(content):
            # Create a new content piece with modified content
            processed = ContentPiece(**content.model_dump())
            processed.content = f"Processed by mock2: {processed.content}"
            return processed
        
        # Use side_effect to simulate the async function
        processor.process.side_effect = mock_process
        return processor
    
    @pytest.fixture
    def error_processor(self):
        """Create a processor that raises an error."""
        processor = MagicMock(spec=BaseProcessor)
        processor.processor_id = "error_processor"
        processor.config = {}
        
        async def mock_process(content):
            raise ValueError("Test error")
        
        # Use side_effect to simulate the async function
        processor.process.side_effect = mock_process
        return processor
    
    @pytest.mark.asyncio
    async def test_process_single(self, mock_processor, sample_content_piece):
        """Test processing a single content piece."""
        # Create a pipeline with a single processor
        pipeline = ProcessingPipeline("test-pipeline", [mock_processor])
        
        # Process the content
        result = await pipeline.process(sample_content_piece)
        
        # Check if the content was processed
        assert result.content.startswith("Processed by mock:")
        assert result.processed is True
        
        # Check if the processor was called
        mock_processor.process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_multiple(self, mock_processor, mock_processor2, sample_content_piece):
        """Test processing a content piece through multiple processors."""
        # Create a pipeline with multiple processors
        pipeline = ProcessingPipeline("test-pipeline", [mock_processor, mock_processor2])
        
        # Process the content
        result = await pipeline.process(sample_content_piece)
        
        # Check if the content was processed by both processors
        assert result.content.startswith("Processed by mock2: Processed by mock:")
        assert result.processed is True
        
        # Check if both processors were called
        mock_processor.process.assert_called_once()
        mock_processor2.process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_error(self, mock_processor, error_processor, sample_content_piece):
        """Test processing with an error in one processor."""
        # Create a pipeline with a processor that raises an error
        pipeline = ProcessingPipeline("test-pipeline", [error_processor, mock_processor])
        
        # Process the content
        result = await pipeline.process(sample_content_piece)
        
        # Check if the content was processed by the second processor
        assert result.content.startswith("Processed by mock:")
        assert result.processed is True
        
        # Check if both processors were called
        error_processor.process.assert_called_once()
        mock_processor.process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_batch(self, mock_processor, sample_content_piece):
        """Test processing a batch of content pieces."""
        # Create a pipeline with a single processor
        pipeline = ProcessingPipeline("test-pipeline", [mock_processor])
        
        # Create a batch of content pieces
        content_pieces = [
            sample_content_piece,
            ContentPiece(
                id="test-content-2",
                title="Test Content 2",
                content="This is another test content.",
                source_id="test-source",
                url=None,
                author=None,
                published_at=None
            )
        ]
        
        # Process the batch
        results = await pipeline.process_batch(content_pieces)
        
        # Check if all content pieces were processed
        assert len(results) == 2
        assert all(result.processed for result in results)
        assert all(result.content.startswith("Processed by mock:") for result in results)
        
        # Check if the processor was called for each content piece
        assert mock_processor.process.call_count == 2
    
    def test_add_processor(self, mock_processor):
        """Test adding a processor to the pipeline."""
        # Create an empty pipeline
        pipeline = ProcessingPipeline("test-pipeline")
        
        # Add a processor
        pipeline.add_processor(mock_processor)
        
        # Check if the processor was added
        assert len(pipeline.processors) == 1
        assert pipeline.processors[0] == mock_processor
    
    def test_remove_processor(self, mock_processor, mock_processor2):
        """Test removing a processor from the pipeline."""
        # Create a pipeline with multiple processors
        pipeline = ProcessingPipeline("test-pipeline", [mock_processor, mock_processor2])
        
        # Remove a processor
        result = pipeline.remove_processor("mock_processor")
        
        # Check if the processor was removed
        assert result is True
        assert len(pipeline.processors) == 1
        assert pipeline.processors[0] == mock_processor2
    
    def test_remove_nonexistent_processor(self, mock_processor):
        """Test removing a processor that doesn't exist."""
        # Create a pipeline with a single processor
        pipeline = ProcessingPipeline("test-pipeline", [mock_processor])
        
        # Try to remove a nonexistent processor
        result = pipeline.remove_processor("nonexistent_processor")
        
        # Check if False was returned
        assert result is False
        assert len(pipeline.processors) == 1
    
    def test_clear(self, mock_processor, mock_processor2):
        """Test clearing all processors from the pipeline."""
        # Create a pipeline with multiple processors
        pipeline = ProcessingPipeline("test-pipeline", [mock_processor, mock_processor2])
        
        # Clear the pipeline
        pipeline.clear()
        
        # Check if all processors were removed
        assert len(pipeline.processors) == 0
    
    def test_to_dict(self, mock_processor, mock_processor2):
        """Test converting the pipeline to a dictionary."""
        # Create a pipeline with multiple processors
        pipeline = ProcessingPipeline("test-pipeline", [mock_processor, mock_processor2])
        
        # Convert to a dictionary
        result = pipeline.to_dict()
        
        # Check the result
        assert result["name"] == "test-pipeline"
        assert len(result["processors"]) == 2
        assert result["processors"][0]["id"] == "mock_processor"
        assert result["processors"][1]["id"] == "mock_processor2"
    
    def test_from_dict(self, mock_processor, mock_processor2):
        """Test creating a pipeline from a dictionary."""
        # Create a dictionary representation
        pipeline_dict = {
            "name": "test-pipeline",
            "processors": [
                {"id": "mock_processor", "config": {"option": "value1"}},
                {"id": "mock_processor2", "config": {"option": "value2"}}
            ]
        }
        
        # Create a mapping of processor IDs to processors
        processors_by_id = {
            "mock_processor": mock_processor,
            "mock_processor2": mock_processor2
        }
        
        # Create a pipeline from the dictionary
        pipeline = ProcessingPipeline.from_dict(pipeline_dict, processors_by_id)
        
        # Check the result
        assert pipeline.name == "test-pipeline"
        assert len(pipeline.processors) == 2
        assert pipeline.processors[0] == mock_processor
        assert pipeline.processors[1] == mock_processor2
        assert mock_processor.config == {"option": "value1"}
        assert mock_processor2.config == {"option": "value2"} 