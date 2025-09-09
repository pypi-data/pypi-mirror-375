from dataclasses import dataclass, field
from typing import List, Optional

from ..location.point_map import PointMap
from .fuel import Fuel

@dataclass
class ServiceArea:
    id: int
    name: str
    location: PointMap
    insert_date: str
    address: str
    brand: str
    distance: str
    fuels: Optional[List[Fuel]] = field(default_factory=list)