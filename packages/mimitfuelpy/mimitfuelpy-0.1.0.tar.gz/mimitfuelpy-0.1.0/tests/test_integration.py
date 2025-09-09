"""Integration tests for the mimitfuelpy library."""

import pytest
from unittest.mock import patch, Mock

from mimitfuelpy import Client
from mimitfuelpy.utils.exceptions import MimitApiError


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the main library components."""

    def test_client_full_workflow(self):
        """Test a complete workflow using the client."""
        # This would be a real integration test if we had a test server
        # For now, we'll mock the HTTP responses
        
        with patch('mimitfuelpy.utils.http_client.urllib.request.urlopen') as mock_urlopen:
            # Mock successful response
            mock_response = Mock()
            mock_response.getcode.return_value = 200
            mock_response.read.return_value = b'{"results": [{"id": "1", "name": "Test Brand"}]}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response
            
            client = Client(timeout=10)
            brands = client.registry.brands()
            
            assert len(brands) == 1
            assert brands[0].name == "Test Brand"

    def test_client_error_handling(self):
        """Test that client properly handles API errors."""
        with patch('mimitfuelpy.utils.http_client.urllib.request.urlopen') as mock_urlopen:
            # Mock error response
            mock_response = Mock()
            mock_response.getcode.return_value = 404
            mock_response.read.return_value = b'{"message": "Not found"}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response
            
            client = Client()
            
            with pytest.raises(MimitApiError) as exc_info:
                client.registry.brands()
            
            assert "Not found" in str(exc_info.value)

    @pytest.mark.slow
    def test_client_with_different_timeouts(self):
        """Test client behavior with different timeout values."""
        # Test with very short timeout
        client_short = Client(timeout=1)
        assert client_short.registry is not None
        assert client_short.search is not None
        
        # Test with long timeout
        client_long = Client(timeout=300)
        assert client_long.registry is not None
        assert client_long.search is not None

    def test_client_registry_search_independence(self):
        """Test that registry and search modules work independently."""
        with patch('mimitfuelpy.utils.http_client.urllib.request.urlopen') as mock_urlopen:
            mock_response = Mock()
            mock_response.getcode.return_value = 200
            mock_response.read.return_value = b'{"results": []}'
            mock_response.__enter__.return_value = mock_response
            mock_urlopen.return_value = mock_response
            
            client = Client()
            
            # Test registry call
            regions = client.registry.regions()
            assert isinstance(regions, list)
            
            # Reset mock for search call
            mock_urlopen.reset_mock()
            mock_response.read.return_value = b'{"success": true, "center": null, "results": []}'
            
            # This would normally require proper criteria object, but for integration test
            # we'll use a mock
            with patch('mimitfuelpy.api.search.asdict') as mock_asdict:
                mock_asdict.return_value = {
                    'fuelType': 'benzina',
                    'serviceType': 'self',
                    'lat': 45.0,
                    'lng': 9.0
                }
                
                # Create a simple mock criteria
                mock_criteria = Mock()
                response = client.search.byZone(mock_criteria)
                
                assert response.success is True
                assert isinstance(response.results, list)