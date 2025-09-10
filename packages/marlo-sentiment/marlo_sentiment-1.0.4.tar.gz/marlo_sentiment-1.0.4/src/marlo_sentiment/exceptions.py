"""Exception classes for Marlo sentiment analysis client."""


class MarloError(Exception):
    """Base exception for Marlo client errors."""
    
    def __init__(self, message: str, status_code: int = 0) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        
    def __str__(self) -> str:
        if self.status_code:
            return f"MarloError {self.status_code}: {self.message}"
        return f"MarloError: {self.message}"


class MarloAPIError(MarloError):
    """Exception for API-related errors."""
    pass


class MarloValidationError(MarloError):
    """Exception for input validation errors."""
    pass


class MarloAuthenticationError(MarloError):
    """Exception for authentication errors."""
    pass


class MarloRateLimitError(MarloError):
    """Exception for rate limit errors."""
    pass