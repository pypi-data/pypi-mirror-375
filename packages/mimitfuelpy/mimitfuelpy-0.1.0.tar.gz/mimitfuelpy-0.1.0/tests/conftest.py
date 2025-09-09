"""Pytest configuration and shared fixtures."""

import pytest
from unittest.mock import Mock

from mimitfuelpy.utils.http_client import HttpClient


@pytest.fixture
def mock_http_client():
    """Mock HttpClient for testing."""
    return Mock(spec=HttpClient)


@pytest.fixture
def sample_service_area_data():
    """Sample service area data for testing."""
    return {
        'id': '12345',
        'name': 'Test Station',
        'nomeImpianto': 'Test Plant Name',
        'address': 'Via Test 123, Test City',
        'brand': 'Test Brand',
        'fuels': [
            {'type': 'benzina', 'price': 1.50, 'available': True},
            {'type': 'diesel', 'price': 1.45, 'available': True}
        ],
        'phoneNumber': '+39 123 456 7890',
        'email': 'test@example.com',
        'website': 'https://example.com',
        'company': 'Test Company S.r.l.',
        'services': [
            {'name': 'Car Wash', 'available': True},
            {'name': 'ATM', 'available': False}
        ],
        'orariapertura': [
            {'day': 'Monday', 'open': '06:00', 'close': '22:00'},
            {'day': 'Tuesday', 'open': '06:00', 'close': '22:00'}
        ]
    }


@pytest.fixture
def sample_search_response_data():
    """Sample search response data for testing."""
    return {
        'success': True,
        'center': {'lat': 45.4642, 'lng': 9.1900},
        'results': [
            {
                'id': '12345',
                'name': 'Test Station 1',
                'fuels': [
                    {'type': 'benzina', 'price': 1.50},
                    {'type': 'diesel', 'price': 1.45}
                ],
                'location': {'lat': 45.4650, 'lng': 9.1850},
                'insertDate': '2023-12-01T10:00:00Z',
                'address': 'Via Milano 1, Milano',
                'brand': 'Test Brand 1',
                'distance': 0.8
            },
            {
                'id': '67890',
                'name': 'Test Station 2',
                'fuels': [
                    {'type': 'gpl', 'price': 0.75}
                ],
                'location': {'lat': 45.4630, 'lng': 9.1920},
                'insertDate': '2023-12-01T11:00:00Z',
                'address': 'Via Roma 2, Milano',
                'brand': 'Test Brand 2',
                'distance': 1.2
            }
        ]
    }