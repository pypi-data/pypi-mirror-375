"""Test suite for server.py."""
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from fastmcp import FastMCP

from nijivoice.models import VoiceActor, VoiceGenerationRequest, Balance
from nijivoice.exceptions import NijiVoiceAPIError
from tests.mock_client import MockNijiVoiceClient

# Patch environment to avoid loading actual API keys
@pytest.fixture(autouse=True)
def mock_env():
    """Mock environment variables."""
    with patch.dict(os.environ, {"NIJIVOICE_API_KEY": "test-api-key"}):
        yield

@pytest.fixture
def mock_client():
    """Create a mock NijiVoiceClient."""
    client = MockNijiVoiceClient(api_key="test-api-key")
    return client

@pytest.fixture
def server_module():
    """Import the server module with patched client."""
    with patch("nijivoice.api.NijiVoiceClient", MockNijiVoiceClient):
        import server
        yield server

@pytest.mark.asyncio
async def test_get_voice_actors(server_module, mock_client):
    """Test get_voice_actors function returns list of voice actors."""
    # Patch the client in server module
    server_module.client = mock_client
    
    # Get the tool function
    get_voice_actors = server_module.get_voice_actors
    
    # Call the function
    result = await get_voice_actors()
    
    # Check if result is a list of VoiceActor objects
    assert isinstance(result, list)
    assert all(isinstance(actor, VoiceActor) for actor in result)
    assert len(result) == 2
    assert result[0].id == "voice-actor-1"
    assert result[1].id == "voice-actor-2"

@pytest.mark.asyncio
async def test_get_voice_actors_error(server_module, mock_client):
    """Test error handling in get_voice_actors function."""
    # Set client to fail
    mock_client.set_should_fail(True)
    
    # Patch the client in server module
    server_module.client = mock_client
    
    # Get the tool function
    get_voice_actors = server_module.get_voice_actors
    
    # Call the function and expect an exception
    with pytest.raises(NijiVoiceAPIError) as excinfo:
        await get_voice_actors()
    
    # Check the exception details
    assert excinfo.value.status_code == 500
    assert "Failed to get voice actors" in str(excinfo.value)

@pytest.mark.asyncio
async def test_mcp_tools_registration(server_module):
    """Test that the tool is properly registered with FastMCP."""
    mcp = server_module.mcp
    
    # Check if FastMCP instance is created
    assert isinstance(mcp, FastMCP)
    assert mcp.name == "nijivoice MCP"
    
    # Check if the get_voice_actors function exists and is decorated
    assert hasattr(server_module, "get_voice_actors")
    get_voice_actors = server_module.get_voice_actors
    
    # Check if function has the expected docstring
    assert "Get the list of voice actors." in get_voice_actors.__doc__

@pytest.mark.asyncio
async def test_client_initialization(server_module):
    """Test that the NijiVoiceClient is initialized properly."""
    # Check that the client is initialized
    client = server_module.client
    assert isinstance(client, MockNijiVoiceClient)
    assert client.api_key == "test-api-key"

@pytest.mark.asyncio
async def test_dotenv_loading():
    """Test that dotenv is loaded properly."""
    # Create a mock for load_dotenv
    with patch("dotenv.load_dotenv") as mock_load_dotenv:
        # Import the server module to trigger load_dotenv
        with patch("nijivoice.api.NijiVoiceClient"):
            import importlib
            import sys
            
            # Remove the module from sys.modules if it exists
            if "server" in sys.modules:
                del sys.modules["server"]
                
            # Re-import the module
            import server
            
            # Check that load_dotenv was called
            mock_load_dotenv.assert_called_once()

@pytest.mark.asyncio
async def test_generate_voice(server_module, mock_client):
    """Test generate_voice function."""
    # Setup
    server_module.client = mock_client
    
    # Create a detailed mock for client.generate_voice
    mock_response = {"encoded_voice": "mock_data", "credits": 100}
    mock_client.generate_voice = AsyncMock(return_value=mock_response)
    
    # Replace get_voice_actors with a mock
    mock_actors = [
        VoiceActor(id="test-actor-1", name="Test Actor 1"),
        VoiceActor(id="test-actor-2", name="Test Actor 2")
    ]
    server_module.get_voice_actors = AsyncMock(return_value=mock_actors)
    
    # Call the function
    result = await server_module.generate_voice(script="こんにちは")
    
    # Verify
    server_module.get_voice_actors.assert_called_once()
    
    # Check that the client's generate_voice was called with the correct request
    called_request = mock_client.generate_voice.call_args[1]["request"]
    assert isinstance(called_request, VoiceGenerationRequest)
    assert called_request.script == "こんにちは"
    
    # Assert the result matches the mock response
    assert result == mock_response

@pytest.mark.asyncio
async def test_generate_voice_no_actors(server_module, mock_client):
    """Test generate_voice function when no actors are available."""
    # Setup
    server_module.client = mock_client
    
    # Replace get_voice_actors with a mock that returns empty list
    server_module.get_voice_actors = AsyncMock(return_value=[])
    
    # Call the function
    result = await server_module.generate_voice(script="こんにちは")
    
    # Verify
    server_module.get_voice_actors.assert_called_once()
    
    # The result should indicate an error
    assert result["status"] == "error"
    assert "利用可能なVoice Actorが見つかりません" in result["message"]

@pytest.mark.asyncio
async def test_get_credit_balance(server_module, mock_client):
    """Test get_credit_balance function."""
    # Setup
    server_module.client = mock_client
    mock_balance = Balance(balance=200)
    mock_client.get_balance = AsyncMock(return_value=mock_balance)
    
    # Call the function
    result = await server_module.get_credit_balance()
    
    # Verify
    mock_client.get_balance.assert_called_once()
    assert result == 200

@pytest.mark.asyncio
async def test_voice_actors_resource(server_module, mock_client):
    """Test voice_actors_resource function."""
    # Setup
    server_module.client = mock_client
    
    # Replace get_voice_actors with a mock
    mock_actors = [
        VoiceActor(id="test-actor-1", name="Test Actor 1"),
        VoiceActor(id="test-actor-2", name="Test Actor 2")
    ]
    server_module.get_voice_actors = AsyncMock(return_value=mock_actors)
    
    # Call the function
    result = await server_module.voice_actors_resource()
    
    # Verify
    server_module.get_voice_actors.assert_called_once()
    assert result == mock_actors

@pytest.mark.asyncio
async def test_voice_actor_resource(server_module, mock_client):
    """Test voice_actor_resource function."""
    # Setup
    server_module.client = mock_client
    
    # Replace get_voice_actors with a mock
    mock_actors = [
        VoiceActor(id="test-actor-1", name="Test Actor 1"),
        VoiceActor(id="test-actor-2", name="Test Actor 2")
    ]
    server_module.get_voice_actors = AsyncMock(return_value=mock_actors)
    
    # Call the function with existing actor ID
    result = await server_module.voice_actor_resource(actor_id="test-actor-1")
    
    # Verify
    server_module.get_voice_actors.assert_called_once()
    assert result == mock_actors[0]
    
    # Reset the mock
    server_module.get_voice_actors.reset_mock()
    
    # Call the function with non-existing actor ID
    result = await server_module.voice_actor_resource(actor_id="non-existing")
    
    # Verify
    server_module.get_voice_actors.assert_called_once()
    assert result is None

@pytest.mark.asyncio
async def test_credit_balance_resource(server_module, mock_client):
    """Test credit_balance_resource function."""
    # Setup
    server_module.client = mock_client
    mock_balance = Balance(balance=200)
    mock_client.get_balance = AsyncMock(return_value=mock_balance)
    
    # Call the function
    result = await server_module.credit_balance_resource()
    
    # Verify
    mock_client.get_balance.assert_called_once()
    assert result == mock_balance

@pytest.mark.asyncio
async def test_voice_generation_prompt(server_module):
    """Test voice_generation_prompt function."""
    # Call the function
    result = server_module.voice_generation_prompt()
    
    # Verify
    assert isinstance(result, str)
    assert "にじボイス音声生成" in result
    assert "利用可能なVoice Actor" in result