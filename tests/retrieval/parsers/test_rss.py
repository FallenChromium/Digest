from pydantic import HttpUrl
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from digest.retrieval.parsers.rss import RssParser
from digest.database.models.content import ContentPiece


class TestRssParser:
    """Tests for the RssParser class."""
    
    def test_config_schema(self):
        """Test the config schema."""
        schema = RssParser.config_schema()
        assert schema["type"] == "object"
        assert "url" in schema["required"]
        assert "url" in schema["properties"]
        assert "headers" in schema["properties"]
        assert "timeout" in schema["properties"]
    
    def test_validate_config_valid(self):
        """Test validating a valid configuration."""
        parser = RssParser("test-source", {"url": "https://example.com/feed.xml"})
        # Should not raise an exception
        parser.validate_config()
    
    def test_validate_config_missing_url(self):
        """Test validating a configuration with a missing URL."""
        with pytest.raises(ValueError):
            RssParser("test-source", {})
    
    def test_validate_config_invalid_url(self):
        """Test validating a configuration with an invalid URL."""
        with pytest.raises(ValueError):
            RssParser("test-source", {"url": "not-a-url"})
    
    @pytest.mark.asyncio
    async def test_fetch(self):
        """Test fetching content from an RSS feed."""
        # Mock the requests.get response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <rss version="2.0">
            <channel>
                <title>Test Feed</title>
                <link>https://example.com</link>
                <description>A test feed</description>
                <item>
                    <title>Test Item 1</title>
                    <link>https://example.com/item1</link>
                    <description>This is test item 1</description>
                    <pubDate>Mon, 01 Jan 2023 12:00:00 GMT</pubDate>
                </item>
                <item>
                    <title>Test Item 2</title>
                    <link>https://example.com/item2</link>
                    <description>This is test item 2</description>
                    <pubDate>Tue, 02 Jan 2023 12:00:00 GMT</pubDate>
                </item>
            </channel>
        </rss>
        """
        # Mock the feedparser.parse result
        mock_feed = MagicMock()
        mock_feed.feed.title = "Test Feed"
        mock_feed.entries = [
            {
                "title": "Test Item 1",
                "link": "https://example.com/item1",
                "description": "This is test item 1",
                "published_parsed": (2023, 1, 1, 12, 0, 0, 0, 1, 0),
                "id": "https://example.com/item1"
            },
            {
                "title": "Test Item 2",
                "link": "https://example.com/item2",
                "description": "This is test item 2",
                "published_parsed": (2023, 1, 2, 12, 0, 0, 0, 2, 0),
                "id": "https://example.com/item2"
            }
        ]
        
        with patch("requests.get", return_value=mock_response), \
             patch("feedparser.parse", return_value=mock_feed):
            
            parser = RssParser("test-source", {"url": "https://example.com/feed.xml"})
            content_pieces = await parser.fetch()
            
            # Check the results
            assert len(content_pieces) == 2
            assert all(isinstance(piece, ContentPiece) for piece in content_pieces)
            assert content_pieces[0].title == "Test Item 1"
            assert content_pieces[1].title == "Test Item 2"
            assert content_pieces[0].url == "https://example.com/item1"
            assert content_pieces[1].url == "https://example.com/item2"
            assert content_pieces[0].source_id == "test-source"
            assert content_pieces[1].source_id == "test-source"
    
    @pytest.mark.asyncio
    async def test_fetch_http_error(self):
        """Test fetching content with an HTTP error."""
        # Mock the requests.get response
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        with patch("requests.get", return_value=mock_response):
            parser = RssParser("test-source", {"url": "https://example.com/feed.xml"})
            with pytest.raises(RuntimeError):
                await parser.fetch()
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        """Test testing a connection successfully."""
        # Mock the requests.head response
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        with patch("requests.head", return_value=mock_response):
            parser = RssParser("test-source", {"url": "https://example.com/feed.xml"})
            result = await parser.test_connection()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self):
        """Test testing a connection with a failure."""
        # Mock the requests.head response
        mock_response = MagicMock()
        mock_response.status_code = 404
        
        with patch("requests.head", return_value=mock_response):
            parser = RssParser("test-source", {"url": "https://example.com/feed.xml"})
            result = await parser.test_connection()
            assert result is False
    
    @pytest.mark.asyncio
    async def test_test_connection_exception(self):
        """Test testing a connection with an exception."""
        # Mock the requests.head to raise an exception
        with patch("requests.head", side_effect=Exception("Connection error")):
            parser = RssParser("test-source", {"url": "https://example.com/feed.xml"})
            result = await parser.test_connection()
            assert result is False 