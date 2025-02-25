import re
from typing import Any, Dict, List, Optional

from readability import Document

from app.retrieval.models import ContentPiece
from app.retrieval.processors.base import BaseProcessor, ProcessorRegistry


@ProcessorRegistry.register
class ReaderModeProcessor(BaseProcessor):
    """Processor that converts HTML content to reader mode format."""
    
    processor_id = "reader_mode"
    name = "Reader Mode"
    description = "Converts HTML content to reader mode format using Mozilla's Readability library."
    
    @classmethod
    def config_schema(cls) -> Dict[str, Any]:
        """Configuration schema for reader mode processor."""
        return {
            "type": "object",
            "properties": {
                "include_title": {
                    "type": "boolean", 
                    "description": "Whether to include article title in output",
                    "default": False
                },
                "include_excerpt": {
                    "type": "boolean",
                    "description": "Whether to include article excerpt in output",
                    "default": False
                }
            }
        }
    
    async def process(self, content: ContentPiece) -> ContentPiece:
        """Convert HTML content to reader mode format."""
        # Clone the content to avoid modifying the original
        processed_content = ContentPiece(**content.model_dump())
        
        # Skip if content is empty
        if not processed_content.content:
            return processed_content
            
        # Parse with readability
        doc = Document(processed_content.content)
        
        # Get the main content
        article = doc.summary()
        
        # Get optional elements based on config
        if self.config.get("include_title", False):
            title = doc.title()
            if title:
                article = f"<h1>{title}</h1>\n{article}"
                
        if self.config.get("include_excerpt", False):
            excerpt = doc.get_excerpt()
            if excerpt:
                article = f"<p><em>{excerpt}</em></p>\n{article}"
        
        # Update the content
        processed_content.content = article
        
        return processed_content