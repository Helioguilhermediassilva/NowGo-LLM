import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import os

# Adjust the import path based on your project structure and how pytest discovers tests
# Assuming tests are run from the 'backend' directory or that 'app' is in PYTHONPATH
from app.core.openai_client import get_chat_completion, test_openai_connection

@pytest_asyncio.fixture
def mock_openai_chat_completions_create():
    """Mocks the OpenAI client's chat.completions.create method."""
    mock_create_method = AsyncMock()
    
    # This mock_client_instance is what get_openai_client will be patched to return.
    mock_client_instance = AsyncMock()
    mock_client_instance.chat = MagicMock()
    mock_client_instance.chat.completions = MagicMock()
    mock_client_instance.chat.completions.create = mock_create_method
    mock_client_instance.api_key = "test_api_key_123" # Ensure the mock client has an api_key

    # Patch os.getenv to ensure get_openai_client believes an API key is set,
    # so it attempts to create and return a client (which will be our mock_client_instance).
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_api_key_123"}):
        with patch('app.core.openai_client.get_openai_client', return_value=mock_client_instance) as mock_get_client_func:
            yield mock_create_method # Yield the 'create' method for tests to set return_values/side_effects

@pytest.mark.asyncio
async def test_get_chat_completion_success(mock_openai_chat_completions_create):
    mock_create_method = mock_openai_chat_completions_create
    
    mock_response = AsyncMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = "Test completion successful"
    mock_create_method.return_value = mock_response

    prompt = "Hello, test!"
    completion = await get_chat_completion(prompt)

    assert completion == "Test completion successful"
    mock_create_method.assert_called_once_with(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )

@pytest.mark.asyncio
async def test_get_chat_completion_api_error(mock_openai_chat_completions_create, capsys):
    mock_create_method = mock_openai_chat_completions_create
    mock_create_method.side_effect = Exception("API communication error")

    prompt = "Test error case"
    completion = await get_chat_completion(prompt)

    assert completion is None
    captured = capsys.readouterr()
    # The error message now comes from the more generic except block in get_chat_completion
    assert "An unexpected error occurred while calling OpenAI API: API communication error" in captured.out

@pytest.mark.asyncio
async def test_get_chat_completion_no_api_key(capsys):
    # For this test, we want get_openai_client to return None.
    # We achieve this by ensuring os.getenv("OPENAI_API_KEY") returns None.
    with patch.dict(os.environ, {}, clear=True): # Clear all env vars, or specifically remove OPENAI_API_KEY
        with patch('app.core.openai_client.os.getenv', return_value=None) as mock_getenv:
            # We also need to ensure that get_openai_client is called afresh, not using a cached version
            # The refactored get_openai_client is called inside get_chat_completion, so this should work.
            prompt = "Test no API key"
            completion = await get_chat_completion(prompt)
            assert completion is None
            captured = capsys.readouterr()
            # The first print comes from get_openai_client, the second from get_chat_completion
            assert "Warning: OPENAI_API_KEY not found in environment variables." in captured.out
            assert "Error: OpenAI client could not be initialized. API key missing or invalid." in captured.out
            mock_getenv.assert_called_with("OPENAI_API_KEY")

@pytest.mark.asyncio
async def test_test_openai_connection_success(mock_openai_chat_completions_create, capsys):
    mock_create_method = mock_openai_chat_completions_create
    
    mock_response = AsyncMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message = MagicMock()
    mock_response.choices[0].message.content = "OpenAI connection is working!"
    mock_create_method.return_value = mock_response

    result = await test_openai_connection()

    assert result is True
    captured = capsys.readouterr()
    assert "OpenAI Test Response: OpenAI connection is working!..." in captured.out # Adjusted for snippet

@pytest.mark.asyncio
async def test_test_openai_connection_failure(mock_openai_chat_completions_create, capsys):
    mock_create_method = mock_openai_chat_completions_create
    mock_create_method.side_effect = Exception("Connection failed")

    result = await test_openai_connection()

    assert result is False
    captured = capsys.readouterr()
    assert "Failed to get response from OpenAI during connection test." in captured.out

