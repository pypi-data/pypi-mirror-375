from .api.registry import Registry
from .api.search import Search
from .utils.http_client import HttpClient

class Client:
    """
    Main client to interact with the Mimit Fuel Prices API.
    It exposes 'registry' and 'search' handlers for different operations.
    """
    def __init__(self, timeout: int = 30):
        """
        Initializes the API client.
        Args:
            timeout (int): HTTP request timeout in seconds.
        """
        http_client = HttpClient(timeout=timeout)
        self.registry = Registry(http_client)
        self.search = Search(http_client)