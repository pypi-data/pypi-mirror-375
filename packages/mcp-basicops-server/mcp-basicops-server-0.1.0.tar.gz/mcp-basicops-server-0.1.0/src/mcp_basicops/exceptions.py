"""Custom exceptions for the BasicOps MCP server."""

from typing import Optional, Dict, Any


class BasicOpsError(Exception):
    """Base exception for BasicOps-related errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, 
                 endpoint: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.endpoint = endpoint
        self.details = details or {}


class BasicOpsAPIError(BasicOpsError):
    """Exception for API-related errors."""
    pass


class BasicOpsAuthenticationError(BasicOpsError):
    """Exception for authentication-related errors."""
    pass


class BasicOpsNotFoundError(BasicOpsError):
    """Exception for resource not found errors."""
    pass


class BasicOpsValidationError(BasicOpsError):
    """Exception for validation errors."""
    pass


class BasicOpsRateLimitError(BasicOpsError):
    """Exception for rate limit errors."""
    pass


class BasicOpsNetworkError(BasicOpsError):
    """Exception for network-related errors."""
    pass


class BasicOpsConfigurationError(BasicOpsError):
    """Exception for configuration-related errors."""
    pass


def create_error_from_response(status_code: int, endpoint: str, 
                              response_data: Optional[Dict[str, Any]] = None) -> BasicOpsError:
    """Create appropriate exception from HTTP response."""
    message = "Unknown error occurred"
    details = response_data or {}
    
    if response_data and "message" in response_data:
        message = response_data["message"]
    elif response_data and "error" in response_data:
        message = response_data["error"]
    
    if status_code == 401:
        return BasicOpsAuthenticationError(
            message="Authentication failed. Check your API token.",
            status_code=status_code,
            endpoint=endpoint,
            details=details
        )
    elif status_code == 403:
        return BasicOpsAuthenticationError(
            message="Access forbidden. Insufficient permissions.",
            status_code=status_code,
            endpoint=endpoint,
            details=details
        )
    elif status_code == 404:
        return BasicOpsNotFoundError(
            message="Resource not found.",
            status_code=status_code,
            endpoint=endpoint,
            details=details
        )
    elif status_code == 422:
        return BasicOpsValidationError(
            message=message or "Validation error occurred.",
            status_code=status_code,
            endpoint=endpoint,
            details=details
        )
    elif status_code == 429:
        return BasicOpsRateLimitError(
            message="Rate limit exceeded. Please try again later.",
            status_code=status_code,
            endpoint=endpoint,
            details=details
        )
    elif 400 <= status_code < 500:
        return BasicOpsAPIError(
            message=message,
            status_code=status_code,
            endpoint=endpoint,
            details=details
        )
    elif 500 <= status_code < 600:
        return BasicOpsAPIError(
            message="Internal server error occurred.",
            status_code=status_code,
            endpoint=endpoint,
            details=details
        )
    else:
        return BasicOpsError(
            message=message,
            status_code=status_code,
            endpoint=endpoint,
            details=details
        )
