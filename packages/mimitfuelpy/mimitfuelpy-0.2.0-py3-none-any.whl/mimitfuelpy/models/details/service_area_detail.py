from dataclasses import dataclass
from typing import List, Optional

from ..core.fuel import Fuel
from .service_area_service import ServiceAreaService
from .opening_hour import OpeningHour

@dataclass
class ServiceAreaDetail:
    id: int
    name: str
    nomeImpianto: str
    address: str
    brand: str
    fuels: Optional[List[Fuel]]
    phoneNumber: str
    email: str
    website: str
    company: str
    services: Optional[List[ServiceAreaService]]
    orariapertura: Optional[List[OpeningHour]]
    
    def __init__(self, 
                 id: int, 
                 name: str, 
                 nomeImpianto: str, 
                 address: str, 
                 brand: str,
                 fuels: Optional[List[Fuel]],
                 phoneNumber: str, 
                 email: str, 
                 website: str, 
                 company: str,
                 services: Optional[List[ServiceAreaService]],
                 orariapertura: Optional[List[OpeningHour]]):
        
        self.id = id
        self.name = name
        self.nomeImpianto = nomeImpianto
        self.address = address
        self.brand = brand
        self.fuels = fuels if fuels is not None else []
        self.phoneNumber = phoneNumber
        self.email = email
        self.website = website
        self.company = company
        self.services = services if services is not None else []
        self.orariapertura = orariapertura if orariapertura is not None else []