"""
Error handling utilities and custom exceptions.
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel

from backend.utils.logger import logger


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None


class APIError(Exception):
    """Base API error class."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = None, 
        details: Dict[str, Any] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class ValidationError(APIError):
    """Validation error."""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details=details,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


class AuthenticationError(APIError):
    """Authentication error."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class RateLimitError(APIError):
    """Rate limit exceeded error."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )


class TokenLimitError(APIError):
    """Token limit exceeded error."""
    
    def __init__(self, message: str = "Token limit exceeded"):
        super().__init__(
            message=message,
            error_code="TOKEN_LIMIT_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ExternalAPIError(APIError):
    """External API error (e.g., OpenAI API)."""
    
    def __init__(self, message: str, service: str = "external_api"):
        super().__init__(
            message=message,
            error_code="EXTERNAL_API_ERROR",
            details={"service": service},
            status_code=status.HTTP_502_BAD_GATEWAY
        )


class CacheError(APIError):
    """Cache-related error."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def handle_openai_error(error: Exception) -> APIError:
    """Convert OpenAI errors to our custom error types."""
    import openai
    
    if isinstance(error, openai.AuthenticationError):
        return AuthenticationError("Invalid OpenAI API key")
    
    elif isinstance(error, openai.RateLimitError):
        return RateLimitError("OpenAI API rate limit exceeded")
    
    elif isinstance(error, openai.APITimeoutError):
        return ExternalAPIError("OpenAI API request timed out", "openai")
    
    elif isinstance(error, openai.APIConnectionError):
        return ExternalAPIError("Failed to connect to OpenAI API", "openai")
    
    elif isinstance(error, openai.BadRequestError):
        return ValidationError(f"Invalid request to OpenAI API: {str(error)}")
    
    elif isinstance(error, openai.APIError):
        return ExternalAPIError(f"OpenAI API error: {str(error)}", "openai")
    
    else:
        return APIError(f"Unexpected error: {str(error)}")


def create_error_response(error: APIError) -> ErrorResponse:
    """Create standardized error response."""
    return ErrorResponse(
        error=error.__class__.__name__,
        message=error.message,
        details=error.details,
        error_code=error.error_code
    )


def log_and_raise_http_error(
    error: Exception,
    operation: str = "Unknown operation"
) -> None:
    """Log error and raise appropriate HTTPException."""
    
    # Convert to our custom error type if needed
    if not isinstance(error, APIError):
        if hasattr(error, '__module__') and 'openai' in error.__module__:
            api_error = handle_openai_error(error)
        else:
            api_error = APIError(str(error))
    else:
        api_error = error
    
    # Log the error
    logger.error(
        f"Error in {operation}",
        error_type=api_error.__class__.__name__,
        error_code=api_error.error_code,
        message=api_error.message,
        details=api_error.details
    )
    
    # Create error response
    error_response = create_error_response(api_error)
    
    # Raise HTTPException
    raise HTTPException(
        status_code=api_error.status_code,
        detail=error_response.dict()
    )


class ErrorHandler:
    """Centralized error handling class."""
    
    @staticmethod
    def handle_chat_error(error: Exception, messages: list = None) -> None:
        """Handle errors specific to chat operations."""
        context = {"messages_count": len(messages) if messages else 0}
        
        if isinstance(error, Exception) and 'token' in str(error).lower():
            raise TokenLimitError(
                "Request exceeds token limits. Try reducing message length or history."
            )
        
        log_and_raise_http_error(error, "chat_completion")
    
    @staticmethod
    def handle_cache_error(error: Exception, operation: str = "cache") -> None:
        """Handle cache-related errors."""
        logger.warning(f"Cache error in {operation}: {str(error)}")
        # Don't raise cache errors, just log them
        # The system should continue to work without cache
    
    @staticmethod
    def handle_validation_error(error: Exception, field: str = None) -> None:
        """Handle validation errors."""
        details = {"field": field} if field else None
        raise ValidationError(str(error), details)


# Global error handler instance
error_handler = ErrorHandler()
