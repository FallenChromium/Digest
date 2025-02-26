# Digest App Tests

This directory contains tests for the Digest news aggregator app.

## Test Structure

The tests are organized by module:

- `tests/retrieval/parsers/`: Tests for the news source parsers
- `tests/retrieval/sources/`: Tests for the source management components
- `tests/retrieval/processors/`: Tests for the content processing pipeline
- `tests/retrieval/`: Integration tests for the retrieval module

## Running Tests

To run the tests, you'll need to install the test dependencies:

```bash
pip install pytest pytest-asyncio
```

Then, you can run the tests with:

```bash
# Run all tests
pytest

# Run tests for a specific module
pytest tests/retrieval/parsers/

# Run a specific test file
pytest tests/retrieval/parsers/test_rss.py

# Run a specific test
pytest tests/retrieval/parsers/test_rss.py::TestRssParser::test_fetch
```

## Test Fixtures

Common test fixtures are defined in `tests/conftest.py`. These include:

- `sample_content_piece`: A sample ContentPiece for testing
- `sample_source_config`: A sample SourceConfig for testing
- `temp_storage_path`: A temporary file path for testing source storage
- `register_mock_components`: Automatically registers mock parsers and processors for testing

## Writing New Tests

When writing new tests:

1. Use the existing fixtures where possible
2. For parser tests, mock external requests
3. For processor tests, use the sample content piece
4. For source tests, use the temporary storage path
5. For integration tests, combine the above

## Mocking External Services

The tests use `unittest.mock` to mock external services like HTTP requests. For example:

```python
with patch("requests.get", return_value=mock_response):
    # Test code that makes HTTP requests
```

## Async Testing

Many components in the app use async/await. Use the `@pytest.mark.asyncio` decorator for async tests:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected_value
``` 