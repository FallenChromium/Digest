from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, ClassVar

from digest.database.models.content import ContentPiece


class ProcessorRegistry:
    """Registry for all available content processors."""
    _processors: Dict[str, Type["BaseProcessor"]] = {}
    
    @classmethod
    def register(cls, processor_cls: Type["BaseProcessor"]) -> Type["BaseProcessor"]:
        """Register a processor class with the registry."""
        processor_id = processor_cls.processor_id
        if processor_id in cls._processors:
            raise ValueError(f"Processor with ID '{processor_id}' is already registered")
        cls._processors[processor_id] = processor_cls
        return processor_cls
    
    @classmethod
    def get_processor(cls, processor_id: str) -> Type["BaseProcessor"]:
        """Get a processor class by ID."""
        if processor_id not in cls._processors:
            raise ValueError(f"Processor with ID '{processor_id}' not found")
        return cls._processors[processor_id]
    
    @classmethod
    def list_processors(cls) -> List[Dict[str, Any]]:
        """List all registered processors with their metadata."""
        return [
            {
                "id": processor_id,
                "name": processor_cls.name,
                "description": processor_cls.description,
                "config_schema": processor_cls.config_schema(),
            }
            for processor_id, processor_cls in cls._processors.items()
        ]


class BaseProcessor(ABC):
    """Base interface for all content processors."""
    
    # Class-level attributes that should be defined by all subclasses
    processor_id: ClassVar[str]
    name: ClassVar[str]
    description: ClassVar[str]
    
    def __init__(self, config: Dict[str, Any] | None = None):
        """
        Initialize the processor with optional configuration.
        
        Args:
            config: Processor-specific configuration
        """
        self.config = config or {}
        self.validate_config()
    
    @classmethod
    @abstractmethod
    def config_schema(cls) -> Dict[str, Any]:
        """
        Define the configuration schema for this processor.
        
        Returns:
            A JSON Schema dictionary defining the required configuration
        """
        pass
    
    def validate_config(self) -> None:
        """
        Validate the provided configuration against the schema.
        
        Raises:
            ValueError: If the configuration is invalid
        """
        # In a real implementation, this would validate against the schema
        # For simplicity, we assume the config is valid
        pass
    
    @abstractmethod
    async def process(self, content: ContentPiece) -> ContentPiece:
        """
        Process a content piece.
        
        Args:
            content: The content piece to process
            
        Returns:
            The processed content piece
        """
        pass 