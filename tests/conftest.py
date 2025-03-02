import os
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from pydantic import HttpUrl

from digest.retrieval.models import ContentPiece, SourceConfig, SourceType, ContentType, UpdateFrequency
from digest.retrieval.sources.base import Source
from digest.retrieval.parsers.base import BaseParser, ParserRegistry
from digest.retrieval.processors.base import BaseProcessor, ProcessorRegistry


@pytest.fixture
def sample_content_piece():
    """Return a sample content piece for testing."""
    return ContentPiece(
        id="nytimes-20240101-1",
        title="The Year in Technology: AI's Rapid Rise",
        content="""<article>
            <h1>The Year in Technology: AI's Rapid Rise</h1>
            <p>Artificial intelligence saw unprecedented advances in 2023, with large language models 
            like GPT-4 demonstrating remarkable capabilities in natural language processing, coding, 
            and creative tasks.</p>
            <p>Tech giants and startups alike raced to develop and deploy AI solutions, while 
            policymakers grappled with regulation and ethical concerns.</p>
            </article>""",
        content_type=ContentType.ARTICLE,
        source_id="nytimes-tech",
        url=HttpUrl("https://www.nytimes.com/2024/01/01/technology/ai-advances-2023.html"), # non-existent URL, but that's fine
        author="Cade Metz",
        published_at=datetime(2024, 1, 1, 9, 0),
        metadata={
            "categories": ["technology", "artificial intelligence", "year in review"],
            "read_time_minutes": 5,
            "section": "Technology"
        }
    )


@pytest.fixture
def sample_source_config():
    """Return a sample source configuration for testing."""
    return SourceConfig(
        id="nytimes-tech",
        name="New York Times - Technology",
        source_type=SourceType.RSS,
        parser_id="mock_parser",
        update_frequency=UpdateFrequency.HOURLY,
        config={
            "url": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
            "user_agent": "Digest RSS Reader/1.0"
        },
        tags=["technology", "trusted source"],
        last_retrieved=datetime(2024, 1, 1, 8, 0)
    )


@pytest.fixture
def temp_storage_path():
    """Create a temporary file for source storage."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        path = Path(tmp.name)
        yield path
        # Clean up after test
        if path.exists():
            path.unlink()


class MockParser(BaseParser):
    """Mock parser for testing."""
    
    parser_id = "mock_parser"
    name = "Mock Parser"
    description = "A mock parser for testing"
    supported_source_types = [SourceType.RSS]
    
    @classmethod
    def config_schema(cls):
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri"},
                "user_agent": {"type": "string"}
            },
            "required": ["url"]
        }
    
    async def fetch(self):
        """Return mock content."""
        return [
            ContentPiece(
                id=f"{self.source_id}:20240101-1",
                title="The Year in Technology: AI's Rapid Rise",
                content="<article><p>Artificial intelligence saw unprecedented advances in 2023...</p></article>",
                source_id=self.source_id,
                url=HttpUrl("https://www.nytimes.com/2024/01/01/technology/ai-advances-2023.html"),
                author="Cade Metz",
                published_at=datetime(2024, 1, 1, 9, 0)
            ),
            ContentPiece(
                id=f"{self.source_id}:20240101-2", 
                title="Tech Companies Prepare for AI Regulation",
                content="<article><p>Major tech companies are preparing for new AI regulations...</p></article>",
                source_id=self.source_id,
                url=HttpUrl("https://www.nytimes.com/2024/01/01/technology/ai-regulation-prep.html"),
                author="Karen Weise",
                published_at=datetime(2024, 1, 1, 10, 30)
            )
        ]
    
    async def test_connection(self):
        """Always return success for testing."""
        return True


class MockProcessor(BaseProcessor):
    """Mock processor for testing."""
    
    processor_id = "mock_processor"
    name = "Mock Processor"
    description = "A mock processor for testing"
    
    @classmethod
    def config_schema(cls):
        return {
            "type": "object",
            "properties": {
                "prefix": {"type": "string", "default": "[Processed] "},
                "add_timestamp": {"type": "boolean", "default": True}
            }
        }
    
    async def process(self, content):
        """Add a prefix and optional timestamp to the content."""
        processed = ContentPiece(**content.model_dump())
        prefix = self.config.get("prefix", "[Processed] ")
        if self.config.get("add_timestamp", True):
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
            prefix = f"[{timestamp}] {prefix}"
        processed.content = f"{prefix}{processed.content}"
        return processed


@pytest.fixture(autouse=True)
def register_mock_components():
    """Register mock components for testing."""
    # Register mock parser
    if "mock_parser" not in ParserRegistry._parsers:
        ParserRegistry.register(MockParser)
    
    # Register mock processor
    if "mock_processor" not in ProcessorRegistry._processors:
        ProcessorRegistry.register(MockProcessor)
    
    yield
    
    # Clean up registries after tests
    if "mock_parser" in ParserRegistry._parsers:
        del ParserRegistry._parsers["mock_parser"]
    
    if "mock_processor" in ProcessorRegistry._processors:
        del ProcessorRegistry._processors["mock_processor"]