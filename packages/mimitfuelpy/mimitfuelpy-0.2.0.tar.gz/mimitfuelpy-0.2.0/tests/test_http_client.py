"""Tests for the HttpClient class."""

import pytest
from unittest.mock import patch, Mock, MagicMock
import urllib.error
import json

from mimitfuelpy.utils.http_client import HttpClient, BASE_URL
from mimitfuelpy.utils.exceptions import MimitApiError


class TestHttpClient:
    """Test cases for the HttpClient class."""

    def test_http_client_initialization_default_timeout(self):
        """Test HTTP client initialization with default timeout."""
        client = HttpClient()
        assert client.timeout == 30
        assert "User-Agent" in client.headers
        assert "Accept" in client.headers

    def test_http_client_initialization_custom_timeout(self):
        """Test HTTP client initialization with custom timeout."""
        timeout = 60
        client = HttpClient(timeout=timeout)
        assert client.timeout == timeout

    @patch('urllib.request.urlopen')
    def test_request_success_with_params(self, mock_urlopen):
        """Test successful request with parameters."""
        # Mock response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"result": "success"}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        client = HttpClient()
        params = {"param1": "value1", "param2": "value2"}
        result = client.request("GET", "test/endpoint", params=params)

        assert result == {"result": "success"}
        mock_urlopen.assert_called_once()

    @patch('urllib.request.urlopen')
    def test_request_success_with_body(self, mock_urlopen):
        """Test successful request with JSON body."""
        # Mock response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'{"result": "created"}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        client = HttpClient()
        body = {"data": "test"}
        result = client.request("POST", "test/endpoint", body=body)

        assert result == {"result": "created"}
        mock_urlopen.assert_called_once()

    @patch('urllib.request.urlopen')
    def test_request_empty_response(self, mock_urlopen):
        """Test request with empty response body."""
        # Mock response
        mock_response = MagicMock()
        mock_response.getcode.return_value = 204
        mock_response.read.return_value = b''
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        client = HttpClient()
        result = client.request("DELETE", "test/endpoint")

        assert result is None

    @patch('urllib.request.urlopen')
    def test_request_http_error_status(self, mock_urlopen):
        """Test request with HTTP error status code."""
        # Mock response with error status
        mock_response = MagicMock()
        mock_response.getcode.return_value = 404
        mock_response.read.return_value = b'{"message": "Not found"}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        client = HttpClient()
        
        with pytest.raises(MimitApiError) as exc_info:
            client.request("GET", "nonexistent/endpoint")
        
        assert "Not found" in str(exc_info.value)

    @patch('urllib.request.urlopen')
    def test_request_invalid_json_response(self, mock_urlopen):
        """Test request with invalid JSON response."""
        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.getcode.return_value = 200
        mock_response.read.return_value = b'invalid json'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        client = HttpClient()
        
        with pytest.raises(MimitApiError) as exc_info:
            client.request("GET", "test/endpoint")
        
        assert "Invalid JSON response" in str(exc_info.value)

    @patch('urllib.request.urlopen')
    def test_request_http_error_exception(self, mock_urlopen):
        """Test request with HTTPError exception."""
        error = urllib.error.HTTPError(
            url="http://test.com", 
            code=500, 
            msg="Server Error", 
            hdrs={}, 
            fp=Mock()
        )
        error.read = Mock(return_value=b'{"message": "Internal Server Error"}')
        mock_urlopen.side_effect = error

        client = HttpClient()
        
        with pytest.raises(MimitApiError) as exc_info:
            client.request("GET", "test/endpoint")
        
        assert "Internal Server Error" in str(exc_info.value)

    @patch('urllib.request.urlopen')
    def test_request_url_error(self, mock_urlopen):
        """Test request with URLError (connection error)."""
        mock_urlopen.side_effect = urllib.error.URLError("Connection failed")

        client = HttpClient()
        
        with pytest.raises(MimitApiError) as exc_info:
            client.request("GET", "test/endpoint")
        
        assert "Connection error" in str(exc_info.value)

    @patch('urllib.request.urlopen')
    def test_request_timeout_error(self, mock_urlopen):
        """Test request with timeout."""
        mock_urlopen.side_effect = TimeoutError()

        client = HttpClient()
        
        with pytest.raises(MimitApiError) as exc_info:
            client.request("GET", "test/endpoint")
        
        assert "timed out" in str(exc_info.value)

    def test_base_url_constant(self):
        """Test that BASE_URL constant is defined correctly."""
        assert BASE_URL == "https://carburanti.mise.gov.it/ospzApi/"