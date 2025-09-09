from enum import Enum

class FuelType(Enum):
    """
    Enumeration for available fuel types.
    The values correspond to the IDs used by the Mimit API.
    """
    ALL = '0'
    PETROL = '1'
    DIESEL = '2'
    METHANE = '3'
    GPL = '4'
    GCN = '323'
    GNL = '324'