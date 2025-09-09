from dataclasses import dataclass
from typing import List, Optional

from ..core.service_area import ServiceArea
from ..location.point_map import PointMap

@dataclass
class ServiceAreaSearchResponse:
    success: bool
    center: PointMap
    results: Optional[List[ServiceArea]]
    
    def __init__(self, 
                 success: bool, 
                 center: PointMap, 
                 results: Optional[List[ServiceArea]]):
        
        self.success = success
        self.center = center
        self.results = results if results is not None else []