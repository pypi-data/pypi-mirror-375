from enum import Enum

class ServiceType(Enum):
    """Enumeration for refueling modes."""
    SELF = '1'
    SERVED = '0'
    ALL = 'x'