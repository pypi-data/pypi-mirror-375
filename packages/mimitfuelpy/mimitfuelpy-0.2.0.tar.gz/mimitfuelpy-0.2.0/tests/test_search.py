"""Tests for the Search API class."""

from unittest.mock import Mock
from dataclasses import dataclass

from mimitfuelpy.api.search import Search
from mimitfuelpy.utils.http_client import HttpClient


@dataclass
class MockSearchCriteria:
    """Mock search criteria for testing."""
    fuelType: str
    serviceType: str
    lat: float = 45.0
    lng: float = 9.0
    radius: int = 10


class TestSearch:
    """Test cases for the Search class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_http_client = Mock(spec=HttpClient)
        self.search = Search(self.mock_http_client)

    def test_search_initialization(self):
        """Test Search initialization."""
        http_client = Mock(spec=HttpClient)
        search = Search(http_client)
        assert search._http == http_client

    def test_by_zone_success(self):
        """Test successful search by zone."""
        criteria = MockSearchCriteria(fuelType="benzina", serviceType="self")
        
        mock_data = {
            'success': True,
            'center': {'lat': 45.0, 'lng': 9.0},
            'results': [
                {
                    'id': '123',
                    'name': 'Test Station',
                    'fuels': [{'type': 'benzina', 'price': 1.50}],
                    'location': {'lat': 45.1, 'lng': 9.1},
                    'insertDate': '2023-01-01',
                    'address': 'Test Address',
                    'brand': 'Test Brand',
                    'distance': 1.2
                }
            ]
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.search.byZone(criteria)
        
        expected_body = {
            'fuelType': 'benzina-self',
            'lat': 45.0,
            'lng': 9.0,
            'radius': 10
        }
        
        self.mock_http_client.request.assert_called_once_with(
            "POST", "search/zone", body=expected_body
        )
        assert result.success is True
        assert len(result.results) == 1
        assert result.results[0].name == 'Test Station'

    def test_by_area_success(self):
        """Test successful search by area."""
        criteria = MockSearchCriteria(fuelType="diesel", serviceType="servito")
        
        mock_data = {
            'success': True,
            'center': {'lat': 45.0, 'lng': 9.0},
            'results': []
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.search.byArea(criteria)
        
        self.mock_http_client.request.assert_called_once_with(
            "POST", "search/area", body={
                'fuelType': 'diesel',
                'serviceType': 'servito',
                'lat': 45.0,
                'lng': 9.0,
                'radius': 10
            }
        )
        assert result.success is True
        assert len(result.results) == 0

    def test_by_highway_success(self):
        """Test successful search by highway."""
        highway_id = "A1"
        
        mock_data = {
            'success': True,
            'center': {'lat': 45.0, 'lng': 9.0},
            'results': [
                {
                    'id': '456',
                    'name': 'Highway Station',
                    'fuels': [],
                    'location': {'lat': 45.2, 'lng': 9.2},
                    'insertDate': '2023-01-02',
                    'address': 'Highway Address',
                    'brand': 'Highway Brand',
                    'distance': 2.5
                }
            ]
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.search.byHighway(highway_id)
        
        self.mock_http_client.request.assert_called_once_with(
            "POST", f'search/highway/{highway_id}'
        )
        assert result.success is True
        assert len(result.results) == 1
        assert result.results[0].name == 'Highway Station'

    def test_by_brand_success(self):
        """Test successful search by brand."""
        criteria = MockSearchCriteria(fuelType="gpl", serviceType="self")
        
        mock_data = {
            'success': False,
            'center': None,
            'results': []
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.search.byBrand(criteria)
        
        self.mock_http_client.request.assert_called_once_with(
            "POST", "search/servicearea", body={
                'fuelType': 'gpl',
                'serviceType': 'self',
                'lat': 45.0,
                'lng': 9.0,
                'radius': 10
            }
        )
        assert result.success is False
        assert result.center is None
        assert len(result.results) == 0

    def test_search_results_with_no_fuels(self):
        """Test search results handling when fuels are missing."""
        criteria = MockSearchCriteria(fuelType="benzina", serviceType="self")
        
        mock_data = {
            'success': True,
            'center': {'lat': 45.0, 'lng': 9.0},
            'results': [
                {
                    'id': '789',
                    'name': 'Station No Fuels',
                    'location': {'lat': 45.3, 'lng': 9.3},
                    'insertDate': '2023-01-03',
                    'address': 'No Fuels Address',
                    'brand': 'No Fuels Brand',
                    'distance': 3.0
                    # Note: 'fuels' key is missing
                }
            ]
        }
        
        self.mock_http_client.request.return_value = mock_data
        
        result = self.search.byZone(criteria)
        
        assert len(result.results) == 1
        assert len(result.results[0].fuels) == 0  # Should default to empty list