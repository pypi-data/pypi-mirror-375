"""
Exception classes for Recreate NFT SDK
"""


class RecreateError(Exception):
    """Base exception for all Recreate SDK errors"""
    pass


class APIError(RecreateError):
    """Error communicating with the API"""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)


class ValidationError(RecreateError):
    """Error validating input parameters"""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded error"""
    def __init__(self, message: str = "Rate limit exceeded. Please try again later."):
        super().__init__(message, status_code=429)


class AuthenticationError(APIError):
    """Authentication/authorization error"""
    def __init__(self, message: str = "Invalid API key or authentication failed"):
        super().__init__(message, status_code=401)


class NetworkError(RecreateError):
    """Network connectivity error"""
    pass


class DeploymentError(RecreateError):
    """Error during NFT collection deployment"""
    pass