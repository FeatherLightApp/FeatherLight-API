"""
Generic error class for unexpected GraphQL response
"""
from typing import Optional


class Error:
    """Generic Error type for unexpected response"""

    def __init__(self, error_type: str, message: Optional[str] = None) -> None:
        self.error_type = error_type
        self.message = message

    def __str__(self):
        return f"{self.error_type}: {self.message or 'An unknown error has occured'}"
