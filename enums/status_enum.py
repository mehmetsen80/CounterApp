from enum import Enum

class StatusEnum(Enum):
    """Enum for API response status values"""
    SUCCESS = "success"
    INCREMENTED = "incremented"
    RESET = "reset"
    ERROR = "error"
    NOT_FOUND = "not_found"
    BAD_REQUEST = "bad_request" 