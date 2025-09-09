from dataclasses import dataclass
from typing import List, Optional

from ..core.fuel import Fuel
from .logo_img import LogoImg

@dataclass
class Logo:
    bandieraId: int
    bandiera: str
    isEliminabile: Optional[bool] = None
    carburantiList: Optional[List[Fuel]] = None
    logoMarkerList: Optional[List[LogoImg]] = None
    
    def __init__(self, 
                 bandieraId: int, 
                 bandiera: str,
                 isEliminabile: Optional[bool],
                 carburantiList: Optional[List[Fuel]],
                 logoMarkerList: Optional[List[LogoImg]]):
        
        self.bandieraId = bandieraId
        self.bandiera = bandiera
        self.isEliminabile = isEliminabile if isEliminabile is not None else None
        self.carburantiList = carburantiList if carburantiList is not None else []
        self.logoMarkerList = logoMarkerList if logoMarkerList is not None else []