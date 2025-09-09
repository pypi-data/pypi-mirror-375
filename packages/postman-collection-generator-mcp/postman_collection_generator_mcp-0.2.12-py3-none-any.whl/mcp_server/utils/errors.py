"""
Custom error types and error handling utilities.
"""
from typing import Optional, Any, Dict
from rich.console import Console

console = Console()


class PostmanGeneratorError(Exception):
    """Base exception for all postman generator errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


class ConfigurationError(PostmanGeneratorError):
    """Error in configuration or environment setup."""
    pass


class AnalysisError(PostmanGeneratorError):
    """Error during codebase analysis."""
    pass


class GenerationError(PostmanGeneratorError):
    """Error during Postman collection generation."""
    pass


class ValidationError(PostmanGeneratorError):
    """Error in input validation."""
    pass


def log_error(error: Exception, context: str = ""):
    """Log an error with rich formatting."""
    console.print(f"[red bold]Error{f' in {context}' if context else ''}:[/red bold] {str(error)}")
    
    if isinstance(error, PostmanGeneratorError) and error.details:
        console.print("[red]Details:[/red]")
        for key, value in error.details.items():
            console.print(f"  {key}: {value}")


def handle_error(func):
    """Decorator for consistent error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PostmanGeneratorError:
            raise  # Re-raise our custom errors
        except Exception as e:
            # Wrap unexpected errors
            raise PostmanGeneratorError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                {"function": func.__name__, "error_type": type(e).__name__}
            )
    return wrapper