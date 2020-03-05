"""
Generic error class for unexpected GraphQL response
"""
from typing import Optional

class Error:
    """Generic Error type for unexpected response"""
    possible_errors = [
        'AuthenticationError'
    ]

    def __init__(self, error_type: str, message: Optional[str] = None) -> None:
        assert error_type in self.possible_errors
        self.error_type = error_type
        self.message = message

    def __str__(self):
        return f"{self.error_type}: {self.message or 'An unknown error has occured'}"

    @classmethod
    def get_type_dict(cls):
        return {x: x for x in cls.possible_errors}

        
