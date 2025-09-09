"""Tests for the Registry API class."""

from unittest.mock import Mock, patch

from mimitfuelpy.api.registry import Registry
from mimitfuelpy.utils.http_client import HttpClient


class TestRegistry:
    """Test cases for the Registry class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_http_client = Mock(spec=HttpClient)
        self.registry = Registry(self.mock_http_client)

    def test_registry_initialization(self):
        """Test Registry initialization."""
        http_client = Mock(spec=HttpClient)
        registry = Registry(http_client)
        assert registry._http == http_client

    def test_service_area_success(self):
        """Test successful service area retrieval."""
        service_area_id = "12345"
        mock_data = {
            'id': service_area_id,
            'name': 'Test Station',
            'nomeImpianto': 'Test Plant',
            'address': 'Test Address',
            'brand': 'Test Brand',
            'fuels': [],
            'phoneNumber': '123456789',
            'email': 'test@example.com',
            'website': 'https://example.com',
            'company': 'Test Company',
            'services': [],
            'orariapertura': []
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.registry.service_area(service_area_id)
        
        self.mock_http_client.request.assert_called_once_with(
            "GET", f'registry/servicearea/{service_area_id}'
        )
        assert result.id == service_area_id
        assert result.name == 'Test Station'

    def test_brands_success(self):
        """Test successful brands retrieval."""
        mock_data = {
            'results': [
                {'id': '1', 'name': 'Brand 1'},
                {'id': '2', 'name': 'Brand 2'}
            ]
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.registry.brands()
        
        self.mock_http_client.request.assert_called_once_with("GET", "registry/brands")
        assert len(result) == 2
        assert result[0].name == 'Brand 1'
        assert result[1].name == 'Brand 2'

    def test_brands_empty_results(self):
        """Test brands retrieval with empty results."""
        mock_data = {'results': []}
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.registry.brands()
        
        assert len(result) == 0

    def test_brands_logos_success(self):
        """Test successful brand logos retrieval."""
        mock_data = {
            'loghi': [
                {'id': '1', 'url': 'http://example.com/logo1.png'},
                {'id': '2', 'url': 'http://example.com/logo2.png'}
            ]
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.registry.brands_logos()
        
        self.mock_http_client.request.assert_called_once_with("GET", "registry/alllogos")
        assert len(result) == 2

    def test_highways_success(self):
        """Test successful highways retrieval."""
        mock_data = {
            'results': [
                {'id': '1', 'name': 'Highway 1'},
                {'id': '2', 'name': 'Highway 2'}
            ]
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.registry.highways()
        
        self.mock_http_client.request.assert_called_once_with("GET", "registry/highway")
        assert len(result) == 2

    def test_regions_success(self):
        """Test successful regions retrieval."""
        mock_data = {
            'results': [
                {'id': '1', 'name': 'Region 1'},
                {'id': '2', 'name': 'Region 2'}
            ]
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.registry.regions()
        
        self.mock_http_client.request.assert_called_once_with("GET", "registry/region")
        assert len(result) == 2

    def test_provinces_success(self):
        """Test successful provinces retrieval."""
        region_id = "123"
        mock_data = {
            'results': [
                {'id': '1', 'name': 'Province 1'},
                {'id': '2', 'name': 'Province 2'}
            ]
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.registry.provinces(region_id)
        
        self.mock_http_client.request.assert_called_once_with(
            "GET", 'registry/province', {"regionId", region_id}
        )
        assert len(result) == 2

    def test_towns_success(self):
        """Test successful towns retrieval."""
        province_id = "456"
        mock_data = {
            'results': [
                {'id': '1', 'name': 'Town 1'},
                {'id': '2', 'name': 'Town 2'}
            ]
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.registry.towns(province_id)
        
        self.mock_http_client.request.assert_called_once_with(
            "GET", 'registry/town', {"province", province_id}
        )
        assert len(result) == 2