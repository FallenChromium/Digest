from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, ClassVar

from digest.retrieval.models import ContentPiece, SourceType


class ParserRegistry:
    """Registry for all available parsers."""
    _parsers: Dict[str, Type["BaseParser"]] = {}
    
    @classmethod
    def register(cls, parser_cls: Type["BaseParser"]) -> Type["BaseParser"]:
        """Register a parser class with the registry."""
        parser_id = parser_cls.parser_id
        if parser_id in cls._parsers:
            raise ValueError(f"Parser with ID '{parser_id}' is already registered")
        cls._parsers[parser_id] = parser_cls
        return parser_cls
    
    @classmethod
    def get_parser(cls, parser_id: str) -> Type["BaseParser"]:
        """Get a parser class by ID."""
        if parser_id not in cls._parsers:
            raise ValueError(f"Parser with ID '{parser_id}' is not registered")
        return cls._parsers[parser_id]
    
    @classmethod
    def list_parsers(cls) -> List[Dict[str, Any]]:
        """List all registered parsers with their metadata."""
        return [
            {
                "id": parser_id,
                "name": parser_cls.name,
                "description": parser_cls.description,
                "supported_source_types": [t.value for t in parser_cls.supported_source_types],
                "config_schema": parser_cls.config_schema(),
            }
            for parser_id, parser_cls in cls._parsers.items()
        ]


class BaseParser(ABC):
    """Base interface for all content parsers."""
    
    # Class-level attributes that should be defined by all subclasses
    parser_id: ClassVar[str]
    name: ClassVar[str]
    description: ClassVar[str]
    supported_source_types: ClassVar[List[SourceType]]
    
    def __init__(self, source_id: str, config: Dict[str, Any]):
        """
        Initialize the parser with source-specific configuration.
        
        Args:
            source_id: Identifier of the source
            config: Parser-specific configuration
        """
        self.source_id = source_id
        self.config = config
        self.validate_config()
    
    @classmethod
    @abstractmethod
    def config_schema(cls) -> Dict[str, Any]:
        """
        Define the configuration schema for this parser.
        
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
    async def fetch(self) -> List[ContentPiece]:
        """
        Fetch content from the source.
        
        Returns:
            A list of ContentPiece objects
        """
        pass
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test if the parser can connect to the source.
        
        Returns:
            True if the connection is successful, False otherwise
        """
        pass 