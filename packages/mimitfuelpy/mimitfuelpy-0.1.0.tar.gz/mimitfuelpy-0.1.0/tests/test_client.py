"""Tests for the main Client class."""

from unittest.mock import patch

from mimitfuelpy import Client


class TestClient:
    """Test cases for the Client class."""

    def test_client_initialization_default_timeout(self):
        """Test client initialization with default timeout."""
        client = Client()
        assert client.registry is not None
        assert client.search is not None

    def test_client_initialization_custom_timeout(self):
        """Test client initialization with custom timeout."""
        timeout = 60
        with patch('mimitfuelpy.client.HttpClient') as mock_http_client:
            client = Client(timeout=timeout)
            mock_http_client.assert_called_once_with(timeout=timeout)
            assert client.registry is not None
            assert client.search is not None

    def test_client_has_registry_attribute(self):
        """Test that client has registry attribute."""
        client = Client()
        assert hasattr(client, 'registry')

    def test_client_has_search_attribute(self):
        """Test that client has search attribute."""
        client = Client()
        assert hasattr(client, 'search')