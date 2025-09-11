"""
Custom exceptions for EODData API client
"""


class EODDataError(Exception):
    """Base exception for EODData API errors"""
    pass


class EODDataAPIError(EODDataError):
    """Raised when API returns an error response"""
    pass


class EODDataAuthError(EODDataAPIError):
    """Raised when authentication fails"""
    pass

