"""Test suite for NijiVoiceClient in api.py."""
import os
import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock

import httpx
import pytest_asyncio

from nijivoice.api import NijiVoiceClient
from nijivoice.models import VoiceActor, VoiceGenerationRequest, Balance
from nijivoice.exceptions import NijiVoiceAPIError


@pytest.fixture
def mock_env():
    """Mock environment variables."""
    with patch.dict(os.environ, {"NIJIVOICE_API_KEY": "test-api-key"}):
        yield


@pytest.fixture
def mock_response():
    """Create a mock response."""
    mock = MagicMock()
    mock.status_code = 200
    mock.text = "Success"
    return mock


@pytest.fixture
def client():
    """Create a NijiVoiceClient instance."""
    return NijiVoiceClient(api_key="test-api-key")


class TestNijiVoiceClient:
    """Test cases for NijiVoiceClient."""

    def test_init_with_api_key(self):
        """Test initialization with api_key parameter."""
        client = NijiVoiceClient(api_key="test-api-key")
        assert client.api_key == "test-api-key"
        assert client.timeout == 30.0
        assert client.headers == {
            "x-api-key": "test-api-key",
            "Accept": "application/json",
        }

    def test_init_without_api_key(self, mock_env):
        """Test initialization without api_key parameter."""
        client = NijiVoiceClient()
        assert client.api_key == "test-api-key"
        assert client.timeout == 30.0

    def test_init_with_custom_timeout(self):
        """Test initialization with custom timeout."""
        client = NijiVoiceClient(api_key="test-api-key", timeout=60.0)
        assert client.timeout == 60.0

    def test_init_without_api_key_and_env(self):
        """Test initialization without api_key parameter and environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as excinfo:
                NijiVoiceClient()
            assert "APIキーが指定されていません" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_voice_actors_success(self, client, mock_response):
        """Test get_voice_actors successful response."""
        # Create mock data
        voice_actors_data = [
            {
                "id": "actor-id-1",
                "name": "Actor 1",
                "gender": "Female",
                "age": 25
            },
            {
                "id": "actor-id-2",
                "name": "Actor 2",
                "gender": "Male",
                "age": 30
            }
        ]
        mock_response.json.return_value = voice_actors_data

        # Mock the AsyncClient.get method
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Call the method
            result = await client.get_voice_actors()
            
            # Verify the result
            assert len(result) == 2
            assert isinstance(result[0], VoiceActor)
            assert result[0].id == "actor-id-1"
            assert result[0].name == "Actor 1"
            assert result[1].id == "actor-id-2"
            assert result[1].name == "Actor 2"
            
            # Verify the request was made correctly
            mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
                f"{client.BASE_URL}/voice-actors", 
                headers=client.headers
            )

    @pytest.mark.asyncio
    async def test_get_voice_actors_voiceActors_key(self, client, mock_response):
        """Test get_voice_actors with voiceActors key in response."""
        # Create mock data with voiceActors key
        voice_actors_data = {
            "voiceActors": [
                {
                    "id": "actor-id-1",
                    "name": "Actor 1",
                    "gender": "Female",
                    "age": 25
                },
                {
                    "id": "actor-id-2",
                    "name": "Actor 2",
                    "gender": "Male",
                    "age": 30
                }
            ]
        }
        mock_response.json.return_value = voice_actors_data

        # Mock the AsyncClient.get method
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Call the method
            result = await client.get_voice_actors()
            
            # Verify the result
            assert len(result) == 2
            assert isinstance(result[0], VoiceActor)
            assert result[0].id == "actor-id-1"
            assert result[0].name == "Actor 1"

    @pytest.mark.asyncio
    async def test_get_voice_actors_unexpected_format(self, client, mock_response):
        """Test get_voice_actors with unexpected data format."""
        # Create unexpected data format
        mock_response.json.return_value = {"unexpectedKey": "unexpected value"}

        # Mock the AsyncClient.get method
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Call the method
            result = await client.get_voice_actors()
            
            # Verify the result is an empty list
            assert isinstance(result, list)
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_voice_actors_error_response(self, client):
        """Test get_voice_actors with error response."""
        # Create error response
        error_response = MagicMock()
        error_response.status_code = 404
        error_response.text = "Not Found"

        # Mock the AsyncClient.get method
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = error_response
            
            # Call the method and expect exception
            with pytest.raises(NijiVoiceAPIError) as excinfo:
                await client.get_voice_actors()
            
            # Verify the exception
            assert excinfo.value.status_code == 404
            assert "Voice Actor一覧の取得に失敗しました" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_voice_actors_timeout(self, client):
        """Test get_voice_actors with timeout."""
        # Mock the AsyncClient.get method to raise TimeoutError
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = TimeoutError("Timeout")
            
            # Call the method and expect exception
            with pytest.raises(NijiVoiceAPIError) as excinfo:
                await client.get_voice_actors()
            
            # Verify the exception
            assert excinfo.value.status_code == 408
            assert "APIリクエストがタイムアウトしました" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_voice_actors_general_exception(self, client):
        """Test get_voice_actors with general exception."""
        # Mock the AsyncClient.get method to raise Exception
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Some error")
            
            # Call the method and expect exception
            with pytest.raises(NijiVoiceAPIError) as excinfo:
                await client.get_voice_actors()
            
            # Verify the exception
            assert excinfo.value.status_code == 500
            assert "API呼び出し中にエラーが発生しました" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_voice_success(self, client, mock_response):
        """Test generate_voice successful response."""
        # Create mock response data
        response_data = {
            "encoded_voice": "base64_encoded_data",
            "remaining_credits": 100
        }
        mock_response.json.return_value = response_data

        # Create request
        request = VoiceGenerationRequest(
            id="actor-id-1",
            script="これはテストです",
            speed=1.0
        )

        # Mock the AsyncClient.post method
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Call the method
            result = await client.generate_voice(request=request)
            
            # Verify the result
            assert result == response_data
            
            # Verify the request was made correctly
            mock_client.return_value.__aenter__.return_value.post.assert_called_once_with(
                f"{client.BASE_URL}/voice-actors/{request.id}/generate-voice",
                headers=client.headers,
                json=request.model_dump(by_alias=True)
            )

    @pytest.mark.asyncio
    async def test_generate_voice_error_response(self, client):
        """Test generate_voice with error response."""
        # Create error response
        error_response = MagicMock()
        error_response.status_code = 500
        error_response.text = "Server Error"

        # Create request
        request = VoiceGenerationRequest(
            id="actor-id-1",
            script="これはテストです",
            speed=1.0
        )

        # Mock the AsyncClient.post method
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = error_response
            
            # Call the method and expect exception
            with pytest.raises(NijiVoiceAPIError) as excinfo:
                await client.generate_voice(request=request)
            
            # Verify the exception
            assert excinfo.value.status_code == 500
            assert "音声生成に失敗しました" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_balance_success(self, client, mock_response):
        """Test get_balance successful response."""
        # Create mock response data
        response_data = {"balance": 500}
        mock_response.json.return_value = response_data

        # Mock the AsyncClient.get method
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Call the method
            result = await client.get_balance()
            
            # Verify the result
            assert isinstance(result, Balance)
            assert result.balance == 500
            assert result.get_credit() == 500
            
            # Verify the request was made correctly
            mock_client.return_value.__aenter__.return_value.get.assert_called_once_with(
                f"{client.BASE_URL}/balances",
                headers=client.headers
            )

    @pytest.mark.asyncio
    async def test_get_balance_complex_response(self, client, mock_response):
        """Test get_balance with complex response structure."""
        # Create mock response data with complex structure
        response_data = {
            "balances": {
                "remainingBalance": 500,
                "credits": [
                    {"balance": 300, "type": "regular"},
                    {"balance": 200, "type": "bonus"}
                ]
            }
        }
        mock_response.json.return_value = response_data

        # Mock the AsyncClient.get method
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            # Call the method
            result = await client.get_balance()
            
            # Verify the result
            assert isinstance(result, Balance)
            assert result.balances == response_data["balances"]
            assert result.get_credit() == 500

    @pytest.mark.asyncio
    async def test_get_balance_error_response(self, client):
        """Test get_balance with error response."""
        # Create error response
        error_response = MagicMock()
        error_response.status_code = 403
        error_response.text = "Forbidden"

        # Mock the AsyncClient.get method
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = error_response
            
            # Call the method and expect exception
            with pytest.raises(NijiVoiceAPIError) as excinfo:
                await client.get_balance()
            
            # Verify the exception
            assert excinfo.value.status_code == 403
            assert "クレジット残高の取得に失敗しました" in str(excinfo.value)