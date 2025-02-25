import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import uuid
import time

from app.retrieval.models import SourceConfig, SourceType
from app.retrieval.sources.base import Source


class SourceRepository:
    """
    Repository for managing news sources.
    
    This implementation uses a simple JSON file storage, but could be
    replaced with a database implementation in the future.
    """
    
    def __init__(self, storage_path: Path | None = None):
        """
        Initialize the repository.
        
        Args:
            storage_path: Path to the JSON file for storing sources
        """
        if storage_path is None:
            # Default to a file in the user's home directory
            home_dir = Path.home()
            app_dir = home_dir / ".digest"
            app_dir.mkdir(exist_ok=True)
            storage_path = app_dir / "sources.json"
        
        self.storage_path = storage_path
        self.sources: Dict[str, Source] = {}
        self._load_sources()
    
    def _load_sources(self) -> None:
        """Load sources from the storage file."""
        if not self.storage_path.exists():
            # Create an empty sources file if it doesn't exist
            self._save_sources()
            return
        
        try:
            with open(self.storage_path, "r") as f:
                sources_data = json.load(f)
            
            for source_data in sources_data:
                source = Source.from_dict(source_data)
                self.sources[source.config.id] = source
        except (json.JSONDecodeError, FileNotFoundError):
            # If the file is corrupted or doesn't exist, start with an empty dict
            self.sources = {}
    
    def _save_sources(self) -> None:
        """Save sources to the storage file."""
        sources_data = [source.to_dict() for source in self.sources.values()]
        
        # Create the directory if it doesn't exist
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to a temporary file first, then rename to avoid corruption
        temp_path = self.storage_path.with_suffix(".tmp")
        with open(temp_path, "w") as f:
            json.dump(sources_data, f, indent=2, default=str)
        
        # Atomic rename on most platforms
        temp_path.replace(self.storage_path)
    
    def get_all(self) -> List[Source]:
        """
        Get all sources.
        
        Returns:
            A list of all sources
        """
        return list(self.sources.values())
    
    def get(self, source_id: str) -> Optional[Source]:
        """
        Get a source by ID.
        
        Args:
            source_id: The ID of the source
            
        Returns:
            The source if found, None otherwise
        """
        return self.sources.get(source_id)
    
    def add(self, config: Dict[str, Any]) -> Source:
        """
        Add a new source.
        
        Args:
            config: The source configuration
            
        Returns:
            The newly created source
            
        Raises:
            ValueError: If a source with the same ID already exists
        """
        # Generate a source ID if not provided
        if "id" not in config:
            config["id"] = f"{config.get('name', 'source').lower().replace(' ', '-')}-{str(uuid.uuid4())[:8]}"
        
        # If the source already exists, raise an error
        if config["id"] in self.sources:
            raise ValueError(f"Source with ID '{config['id']}' already exists")
        
        source_config = SourceConfig(**config)
        source = Source(source_config)
        
        self.sources[source.config.id] = source
        self._save_sources()
        
        return source
    
    def update(self, source_id: str, config: Dict[str, Any]) -> Source:
        """
        Update an existing source.
        
        Args:
            source_id: The ID of the source to update
            config: The new configuration
            
        Returns:
            The updated source
            
        Raises:
            ValueError: If no source with the given ID exists
        """
        if source_id not in self.sources:
            raise ValueError(f"Source with ID '{source_id}' not found")
        
        # Preserve the original ID
        config["id"] = source_id
        
        # Create a new SourceConfig and Source
        source_config = SourceConfig(**config)
        source = Source(source_config)
        
        self.sources[source_id] = source
        self._save_sources()
        
        return source
    
    def delete(self, source_id: str) -> bool:
        """
        Delete a source.
        
        Args:
            source_id: The ID of the source to delete
            
        Returns:
            True if the source was deleted, False if it didn't exist
        """
        if source_id not in self.sources:
            return False
        
        del self.sources[source_id]
        self._save_sources()
        
        return True
    
    def get_by_type(self, source_type: SourceType) -> List[Source]:
        """
        Get sources of a specific type.
        
        Args:
            source_type: The type of sources to get
            
        Returns:
            A list of sources of the specified type
        """
        return [
            source for source in self.sources.values()
            if source.config.source_type == source_type
        ] 