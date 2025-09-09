"""
mimitfuelpy - Python library for accessing Mimit Fuel Prices API
"""

from .client import Client
from .__version__ import __version__, __author__, __email__

__all__ = ['Client']