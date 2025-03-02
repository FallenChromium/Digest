import pytest

from app.retrieval.parsers.tchan import TchanParser


class TestTchanParser:
    @pytest.mark.asyncio
    async def test_fetch(self):
        parser = TchanParser("test-source", {"channel_name": "tchantest", "limit": 10})
        content_pieces = await parser.fetch()
        assert len(content_pieces) == 8  # Parser skips posts without any text.

    @pytest.mark.asyncio
    async def test_test_connection_success(self):
        parser = TchanParser("test-source", {"channel_name": "tchantest", "limit": 5})
        result = await parser.test_connection()
        assert result is True

    @pytest.mark.asyncio
    async def test_test_connection_failure(self):
        parser = TchanParser(
            "test-source", {"channel_name": "ihopethereisnochannelwithsuchname", "limit": 10}
        )
        result = await parser.test_connection()
        assert result is False
