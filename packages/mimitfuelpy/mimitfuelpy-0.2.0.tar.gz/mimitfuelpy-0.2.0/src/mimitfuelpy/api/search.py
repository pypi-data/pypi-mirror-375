from dataclasses import asdict

from ..utils.http_client import HttpClient
from ..models.core.service_area import ServiceArea
from ..models.core.fuel import Fuel
from ..models.search.response import ServiceAreaSearchResponse

class Search:
    def __init__(self, http_client: HttpClient):
        self._http = http_client
    
    """Retrieves the service area by zone."""
    def byZone(self, criteria) -> ServiceAreaSearchResponse:
        body = asdict(criteria)
        body['fuelType'] = f"{body.pop('fuelType')}-{body.pop('serviceType')}"

        data = self._http.request("POST", "search/zone", body=body)
        
        return ServiceAreaSearchResponse(
            success=data['success'],
            center=data['center'],
            results=[ServiceArea(
                id=service['id'],
                name=service['name'],
                fuels=[Fuel(**fuel) for fuel in service.get('fuels', [])],
                location=service['location'],
                insertDate=service['insertDate'],
                address=service['address'],
                brand=service['brand'],
                distance=service['distance']
            ) for service in data.get('results', [])])
        
    """Retrieves the service area by geographic area."""
    def byArea(self, criteria) -> ServiceAreaSearchResponse:
        data = self._http.request("POST", "search/area", body=asdict(criteria))
        
        return ServiceAreaSearchResponse(
            success=data['success'],
            center=data['center'],
            results=[ServiceArea(
                id=service['id'],
                name=service['name'],
                fuels=[Fuel(**fuel) for fuel in service.get('fuels', [])],
                location=service['location'],
                insertDate=service['insertDate'],
                address=service['address'],
                brand=service['brand'],
                distance=service['distance']
            ) for service in data.get('results', [])])
        
    """Retrieves the service area by highway."""
    def byHighway(self, highway_id) -> ServiceAreaSearchResponse:
        data = self._http.request("POST", f'search/highway/{highway_id}')
        
        return ServiceAreaSearchResponse(
            success=data['success'],
            center=data['center'],
            results=[ServiceArea(
                id=service['id'],
                name=service['name'],
                fuels=[Fuel(**fuel) for fuel in service.get('fuels', [])],
                location=service['location'],
                insertDate=service['insertDate'],
                address=service['address'],
                brand=service['brand'],
                distance=service['distance']
            ) for service in data.get('results', [])])
        
    """Retrieves the service area by brand."""
    def byBrand(self, criteria) -> ServiceAreaSearchResponse:
        data = self._http.request("POST", "search/servicearea", body=asdict(criteria))
        
        return ServiceAreaSearchResponse(
            success=data['success'],
            center=data['center'],
            results=[ServiceArea(
                id=service['id'],
                name=service['name'],
                fuels=[Fuel(**fuel) for fuel in service.get('fuels', [])],
                location=service['location'],
                insertDate=service['insertDate'],
                address=service['address'],
                brand=service['brand'],
                distance=service['distance']
            ) for service in data.get('results', [])])