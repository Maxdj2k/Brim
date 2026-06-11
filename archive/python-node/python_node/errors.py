"""
Error handling module for Brim CLI
"""

import sys
from typing import Callable, Any
from rich.console import Console

console = Console()

class BrimCLIError(Exception):
    """Base exception for Brim CLI errors"""
    def __init__(self, message: str, error_code: int = 1):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(BrimCLIError):
    """Raised when input validation fails"""
    def __init__(self, message: str):
        super().__init__(message, error_code=2)

class AuthenticationError(BrimCLIError):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, error_code=3)

class AuthorizationError(BrimCLIError):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message, error_code=4)

class NetworkError(BrimCLIError):
    """Raised when network operations fail"""
    def __init__(self, message: str = "Network operation failed"):
        super().__init__(message, error_code=5)

class ResourceNotFoundError(BrimCLIError):
    """Raised when a resource is not found"""
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(f"{resource_type} '{resource_id}' not found", error_code=6)

class ConfigurationError(BrimCLIError):
    """Raised when configuration is invalid"""
    def __init__(self, message: str = "Configuration error"):
        super().__init__(message, error_code=7)

class TimeoutError(BrimCLIError):
    """Raised when an operation times out"""
    def __init__(self, operation: str, timeout_seconds: int):
        super().__init__(f"{operation} timed out after {timeout_seconds} seconds", error_code=8)

def handle_errors(func: Callable) -> Callable:
    """Decorator to handle CLI errors consistently"""
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except BrimCLIError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            sys.exit(e.error_code)
        except KeyboardInterrupt:
            console.print("\n[yellow]Operation cancelled by user[/yellow]")
            sys.exit(130)
        except Exception as e:
            console.print(f"[red]Unexpected error: {str(e)}[/red]")
            console.print("[dim]This might be a bug. Please report it with the error details.[/dim]")
            sys.exit(1)
    return wrapper

def validate_required(value: Any, name: str) -> None:
    """Validate that a required value is provided"""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(f"{name} is required")

def validate_length(value: str, name: str, min_length: int, max_length: int = None) -> None:
    """Validate string length"""
    if not isinstance(value, str):
        raise ValidationError(f"{name} must be a string")
    
    if len(value) < min_length:
        raise ValidationError(f"{name} must be at least {min_length} characters long")
    
    if max_length and len(value) > max_length:
        raise ValidationError(f"{name} must be no more than {max_length} characters long")

def validate_choice(value: Any, name: str, choices: list) -> None:
    """Validate that a value is one of the allowed choices"""
    if value not in choices:
        raise ValidationError(f"{name} must be one of: {', '.join(choices)}")

def validate_uuid(value: str, name: str) -> None:
    """Validate that a value is a valid UUID"""
    import uuid
    try:
        uuid.UUID(value)
    except ValueError:
        raise ValidationError(f"{name} must be a valid UUID") 