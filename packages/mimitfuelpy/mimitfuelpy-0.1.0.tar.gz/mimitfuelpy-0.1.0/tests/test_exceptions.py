"""Tests for custom exceptions."""

import pytest

from mimitfuelpy.utils.exceptions import MimitApiError


class TestMimitApiError:
    """Test cases for the MimitApiError exception."""

    def test_mimit_api_error_message_only(self):
        """Test MimitApiError with message only."""
        message = "Test error message"
        error = MimitApiError(message)
        
        assert str(error) == f"Mimit API Error: {message}"
        assert error.status_code is None

    def test_mimit_api_error_with_status_code(self):
        """Test MimitApiError with message and status code."""
        message = "Test error message"
        status_code = 404
        error = MimitApiError(message, status_code)
        
        expected_msg = f"Mimit API Error: {message} (Status Code: {status_code})"
        assert str(error) == expected_msg
        assert error.status_code == status_code

    def test_mimit_api_error_inheritance(self):
        """Test that MimitApiError inherits from Exception."""
        error = MimitApiError("Test message")
        assert isinstance(error, Exception)

    def test_mimit_api_error_can_be_raised(self):
        """Test that MimitApiError can be raised and caught."""
        with pytest.raises(MimitApiError) as exc_info:
            raise MimitApiError("Test error", 500)
        
        assert "Test error" in str(exc_info.value)
        assert exc_info.value.status_code == 500