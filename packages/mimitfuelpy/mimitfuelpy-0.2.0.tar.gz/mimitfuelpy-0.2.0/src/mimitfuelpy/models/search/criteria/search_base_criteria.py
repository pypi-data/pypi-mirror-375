from dataclasses import dataclass
from typing import Optional, Literal

from ....models.enums.fuel_type import FuelType
from ....models.enums.service_type import ServiceType

@dataclass
class SearchBaseCriteria:
    fuelType: Optional[FuelType]
    serviceType: Optional[ServiceType]
    priceOrder: Optional[Literal['asc', 'desc']]