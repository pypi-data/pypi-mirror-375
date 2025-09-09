from dataclasses import dataclass
from typing import Optional

@dataclass
class Fuel:
    fuelType: str
    serviceType: str
    price: float
    isSelf: bool
    isAvailable: bool
    id: Optional[int] = None
    name: Optional[str] = None
    fuel_id: Optional[int] = None
    service_area_id: Optional[int] = None
    insert_date: Optional[str] = None
    validity_date: Optional[str] = None