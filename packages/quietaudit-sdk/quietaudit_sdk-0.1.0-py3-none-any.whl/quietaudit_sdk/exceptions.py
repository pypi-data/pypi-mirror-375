"""Custom exceptions for QuietAudit SDK"""

class QuietAuditError(Exception):
    """Base exception for QuietAudit SDK"""
    pass

class AuthenticationError(QuietAuditError):
    """Raised when API key authentication fails"""
    pass

class ConfigurationError(QuietAuditError):
    """Raised when SDK is misconfigured"""
    pass

class APIError(QuietAuditError):
    """Raised when QuietStack API returns an error"""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    pass

class ModelNotSupportedError(QuietAuditError):
    """Raised when trying to wrap an unsupported model"""
    pass

class ContextExtractionError(QuietAuditError):
    """Raised when unable to extract context from model call"""
    pass