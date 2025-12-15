"""
Middleware para la API REST
"""
from .error_handler import setup_exception_handlers
from .logging import setup_logging_middleware

__all__ = [
    "setup_exception_handlers",
    "setup_logging_middleware",
]