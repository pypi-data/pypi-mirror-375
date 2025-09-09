from typing import List

from ..models.details.service_area_detail import ServiceAreaDetail

from ..utils.http_client import HttpClient
from ..models.details.service_area_service import ServiceAreaService
from ..models.core.fuel import Fuel
from ..models.details.opening_hour import OpeningHour
from ..models.core.brand import Brand
from ..models.details.logo import Logo
from ..models.location.highway import Highway
from ..models.location.region import Region
from ..models.location.province import Province
from ..models.location.town import Town

class Registry:
    def __init__(self, http_client: HttpClient):
        self._http = http_client

    """Retrieves the details of service area by id."""
    def service_area(self, service_area_id) -> ServiceAreaDetail:
        data = self._http.request("GET", f'registry/servicearea/{service_area_id}')

        return ServiceAreaDetail(
            id=data['id'],
            name=data['name'],
            nomeImpianto=data['nomeImpianto'],
            address=data['address'],
            brand=data['brand'],
            fuels=[Fuel(**fuel) for fuel in data.get('fuels', [])],
            phoneNumber=data['phoneNumber'],
            email=data['email'],
            website=data['website'],
            company=data['company'],
            services=[ServiceAreaService(**service) for service in data.get('services', [])],
            orariapertura=[OpeningHour(**hour) for hour in data.get('orariapertura', [])]
        )
        
    """Retrieves the list of all brands."""
    def brands(self) -> List[Brand]:
        data = self._http.request("GET", "registry/brands")

        return [Brand(**brand) for brand in data.get('results', [])]
    
    """Retrieves the list of all logos."""
    def brands_logos(self) -> List[Logo]:
        data = self._http.request("GET", "registry/alllogos")

        return [Logo(**logo) for logo in data.get('loghi', [])]
    
    """Retrieves the list of all highways."""
    def highways(self) -> List[Highway]:
        data = self._http.request("GET", "registry/highway")
        
        return [Highway(**highway) for highway in data.get('results', [])]
    
    """Retrieves the list of all regions."""
    def regions(self) -> List[Region]:
        data = self._http.request("GET", "registry/region")

        return [Region(**region) for region in data.get('results', [])]
    
    """Retrieves the list of all provinces by region id."""
    def provinces(self, regionId) -> List[Province]:
        data = self._http.request("GET", f'registry/province', {"regionId", regionId})

        return [Province(**province) for province in data.get('results', [])]
    
    """Retrieves the list of all highways."""
    def towns(self, provinceId) -> List[Town]:
        data = self._http.request("GET", f'registry/town', {"province", provinceId})

        return [Town(**town) for town in data.get('results', [])]