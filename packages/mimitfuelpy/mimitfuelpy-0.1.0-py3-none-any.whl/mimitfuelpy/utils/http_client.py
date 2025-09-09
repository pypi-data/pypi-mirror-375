import urllib.request
import urllib.parse
import json
from typing import Any, Dict, Optional

from .exceptions import MimitApiError

# The official base URL for the API
BASE_URL = "https://carburanti.mise.gov.it/ospzApi/"

class HttpClient:
    """Handles HTTP requests, session management, and error handling."""

    def __init__(self, timeout: int = 30):
        """
        Initializes the HTTP client.
        Args:
            timeout (int): Request timeout in seconds.
        """
        self.headers ={
            "User-Agent": "MimitFuelPricesPythonClient/2.0",
            "Accept": "application/json"
        }
        self.timeout = timeout

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None
    ) -> Any:
        url = f"{BASE_URL}/{endpoint}"
        
        headers = self.headers.copy()

        if params:
            query_string = urllib.parse.urlencode(params)
            url = f"{url}?{query_string}"

        data = None
        if body is not None:
            data = json.dumps(body).encode('utf-8')
            headers["Content-Type"] = "application/json"
        
        req = urllib.request.Request(url, headers=headers, method=method, data=data)
            
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                status_code = response.getcode()

                # Emula response.raise_for_status()
                if not (200 <= status_code < 300):
                    # Tenta di leggere l'errore se disponibile nel body, altrimenti usa il codice
                    error_body = response.read().decode('utf-8', errors='ignore')
                    try:
                        error_data = json.loads(error_body)
                        message = error_data.get('message', f"HTTP Error: {status_code}")
                    except json.JSONDecodeError:
                        message = f"HTTP Error: {status_code} - {error_body.strip()[:100]}..."
                    raise MimitApiError(message, status_code)

                # Prova a parsare la risposta JSON
                response_body = response.read().decode('utf-8')
                if not response_body: # Gestisce risposte vuote
                    return None

                try:
                    data = json.loads(response_body)
                except json.JSONDecodeError:
                    raise MimitApiError("Invalid JSON response from API.", status_code)

                return data

        except urllib.error.HTTPError as e:
            # Cattura errori HTTP specifici (4xx, 5xx)
            # e.code è lo status code
            # e.read() contiene il corpo della risposta di errore
            error_body = e.read().decode('utf-8', errors='ignore')
            try:
                error_data = json.loads(error_body)
                message = error_data.get('message', f"HTTP Error: {e.code}")
            except json.JSONDecodeError:
                message = f"HTTP Error: {e.code} - {error_body.strip()[:100]}..."
            raise MimitApiError(message, e.code) from e
        except urllib.error.URLError as e:
            # Cattura errori di rete (es. URL non valido, DNS fallito)
            raise MimitApiError(f"Connection error: {e.reason}") from e
        except TimeoutError:
            # Cattura specificamente il timeout
            raise MimitApiError(f"Request timed out after {self.timeout} seconds.")
        except Exception as e:
            # Cattura qualsiasi altro errore inatteso
            raise MimitApiError(f"An unexpected error occurred: {e}") from e