"""Test suite for exceptions.py."""
import pytest
from nijivoice.exceptions import NijiVoiceError, NijiVoiceAPIError


class TestNijiVoiceExceptions:
    """Test cases for NijiVoice exceptions."""

    def test_nijivoice_error(self):
        """Test NijiVoiceError base exception."""
        # Create an instance
        error = NijiVoiceError("Test error message")
        
        # Check if it's an instance of Exception
        assert isinstance(error, Exception)
        
        # Check the error message
        assert str(error) == "Test error message"

    def test_nijivoice_api_error_with_status_code(self):
        """Test NijiVoiceAPIError with status code."""
        # Create an instance with status code
        error = NijiVoiceAPIError("API error message", status_code=404)
        
        # Check inheritance
        assert isinstance(error, NijiVoiceError)
        
        # Check properties
        assert str(error) == "API error message"
        assert error.status_code == 404

    def test_nijivoice_api_error_without_status_code(self):
        """Test NijiVoiceAPIError without status code."""
        # Create an instance without status code
        error = NijiVoiceAPIError("API error message")
        
        # Check properties
        assert str(error) == "API error message"
        assert error.status_code is None