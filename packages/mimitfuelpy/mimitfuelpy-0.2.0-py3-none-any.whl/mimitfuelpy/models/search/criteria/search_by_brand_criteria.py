from dataclasses import dataclass
from typing import Optional

from .search_base_criteria import SearchBaseCriteria

@dataclass
class SearchByBrandCriteria(SearchBaseCriteria):
    province: Optional[str] = None
    region: Optional[int] = None
    brand: Optional[str] = None
    queryText: Optional[str] = None