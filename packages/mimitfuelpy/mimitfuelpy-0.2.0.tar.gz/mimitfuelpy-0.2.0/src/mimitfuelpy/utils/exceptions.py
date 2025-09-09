from typing import Optional

class MimitApiError(Exception):
    """Custom exception for Mimit API specific errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(f"Mimit API Error: {message}" + (f" (Status Code: {status_code})" if status_code else ""))