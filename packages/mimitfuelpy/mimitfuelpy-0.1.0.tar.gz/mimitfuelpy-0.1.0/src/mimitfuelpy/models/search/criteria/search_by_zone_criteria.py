from dataclasses import dataclass
from typing import List, Optional

from .search_base_criteria import SearchBaseCriteria
from ....models.location.point_map import PointMap

@dataclass
class SearchByZoneCriteria(SearchBaseCriteria):
    points: List[PointMap]
    radius: Optional[int] = 5