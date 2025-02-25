import logging
from typing import Dict, List, Optional, Any

from app.retrieval.models import ContentPiece
from app.retrieval.processors.base import BaseProcessor


logger = logging.getLogger(__name__)


class ProcessingPipeline:
    """
    A pipeline for processing content pieces through a series of processors.
    """
    
    def __init__(self, name: str, processors: List[BaseProcessor] = None):
        """
        Initialize a processing pipeline.
        
        Args:
            name: Name of the pipeline
            processors: List of processors to apply, in order
        """
        self.name = name
        self.processors = processors or []
    
    async def process(self, content: ContentPiece) -> ContentPiece:
        """
        Process a content piece through all processors in the pipeline.
        
        Args:
            content: The content piece to process
            
        Returns:
            The processed content piece
        """
        processed_content = content
        
        for processor in self.processors:
            try:
                processed_content = await processor.process(processed_content)
            except Exception as e:
                logger.exception(f"Error processing content with processor {processor.processor_id}: {e}")
                # Continue with the next processor
        
        # Mark the content as processed
        processed_content.processed = True
        
        return processed_content
    
    async def process_batch(self, content_pieces: List[ContentPiece]) -> List[ContentPiece]:
        """
        Process a batch of content pieces through the pipeline.
        
        Args:
            content_pieces: The content pieces to process
            
        Returns:
            The processed content pieces
        """
        processed_pieces = []
        
        for content in content_pieces:
            processed_content = await self.process(content)
            processed_pieces.append(processed_content)
        
        return processed_pieces
    
    def add_processor(self, processor: BaseProcessor) -> None:
        """
        Add a processor to the end of the pipeline.
        
        Args:
            processor: The processor to add
        """
        self.processors.append(processor)
    
    def remove_processor(self, processor_id: str) -> bool:
        """
        Remove a processor from the pipeline.
        
        Args:
            processor_id: The ID of the processor to remove
            
        Returns:
            True if the processor was removed, False if it wasn't found
        """
        for i, processor in enumerate(self.processors):
            if processor.processor_id == processor_id:
                del self.processors[i]
                return True
        
        return False
    
    def clear(self) -> None:
        """Remove all processors from the pipeline."""
        self.processors = []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the pipeline to a dictionary.
        
        Returns:
            A dictionary representation of the pipeline
        """
        return {
            "name": self.name,
            "processors": [
                {
                    "id": processor.processor_id,
                    "config": processor.config
                }
                for processor in self.processors
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], processors_by_id: Dict[str, BaseProcessor]) -> "ProcessingPipeline":
        """
        Create a pipeline from a dictionary.
        
        Args:
            data: A dictionary representation of the pipeline
            processors_by_id: A mapping of processor IDs to processor instances
            
        Returns:
            A ProcessingPipeline instance
        """
        name = data["name"]
        processor_configs = data.get("processors", [])
        
        processors = []
        for config in processor_configs:
            processor_id = config["id"]
            processor_config = config.get("config", {})
            
            if processor_id in processors_by_id:
                processor = processors_by_id[processor_id]
                processor.config = processor_config
                processors.append(processor)
            else:
                logger.warning(f"Processor with ID '{processor_id}' not found")
        
        return cls(name, processors) 