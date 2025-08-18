"""
Service layer exceptions for the waypoint backend.

This module contains custom exceptions used across the service layer
to provide clear error handling and better debugging capabilities.
"""


class ServiceError(Exception):
    """
    Base exception for all service layer errors.
    This provides a common base for all service-related exceptions,
    making it easier to catch and handle service errors generically.
    """
    pass


class FlightServiceError(ServiceError):
    """
    Custom exception for flight service errors.
    This provides a clear way to distinguish flight service errors
    from other types of exceptions in the application.
    """
    pass


class ValidationError(ServiceError):
    """
    Exception raised when input validation fails.
    Used when service methods receive invalid input parameters
    that don't meet the expected format or constraints.
    """
    pass


class ExternalServiceError(ServiceError):
    """
    Exception raised when external service calls fail.
    Used when interactions with external APIs or services
    (like MCP agents) encounter errors.
    """
    pass


class ConfigurationError(ServiceError):
    """
    Exception raised when service configuration is invalid.
    Used when required configuration parameters are missing
    or have invalid values.
    """
    pass
