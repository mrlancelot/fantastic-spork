"""Exception Handling - Clean exception classes for TravelAI Backend

Custom exceptions for better error handling and user experience.
"""

from typing import Optional, Dict, Any

class TravelAIException(Exception):
    """Base exception class for TravelAI application"""
    
    def __init__(
        self,
        message: str,
        error_type: str = "GENERAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

class ServiceUnavailableError(TravelAIException):
    """Exception for when external services are unavailable"""
    
    def __init__(self, service_name: str, message: str):
        super().__init__(
            message=f"Service unavailable: {service_name} - {message}",
            error_type="SERVICE_UNAVAILABLE",
            status_code=503,
            details={"service": service_name}
        )

class ExternalAPIError(TravelAIException):
    """Exception for external API errors"""
    
    def __init__(self, api_name: str, message: str, status_code: int = 502):
        super().__init__(
            message=f"External API error: {api_name} - {message}",
            error_type="EXTERNAL_API_ERROR",
            status_code=status_code,
            details={"api": api_name}
        )

class ValidationError(TravelAIException):
    """Exception for request validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=f"Validation error: {message}",
            error_type="VALIDATION_ERROR",
            status_code=400,
            details={"field": field} if field else {}
        )

class AuthenticationError(TravelAIException):
    """Exception for authentication errors"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_type="AUTHENTICATION_ERROR",
            status_code=401
        )

class AuthorizationError(TravelAIException):
    """Exception for authorization errors"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_type="AUTHORIZATION_ERROR",
            status_code=403
        )

class NotFoundError(TravelAIException):
    """Exception for resource not found errors"""
    
    def __init__(self, resource: str, identifier: Optional[str] = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        
        super().__init__(
            message=message,
            error_type="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "identifier": identifier}
        )

class RateLimitError(TravelAIException):
    """Exception for rate limit errors"""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_type="RATE_LIMIT_ERROR",
            status_code=429
        )

class AIServiceError(TravelAIException):
    """Exception for AI service errors"""
    
    def __init__(self, message: str, service: str = "AI"):
        super().__init__(
            message=f"AI service error: {message}",
            error_type="AI_SERVICE_ERROR",
            status_code=502,
            details={"service": service}
        )

class ConfigurationError(TravelAIException):
    """Exception for configuration errors"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message=f"Configuration error: {message}",
            error_type="CONFIGURATION_ERROR",
            status_code=500,
            details={"config_key": config_key} if config_key else {}
        )
