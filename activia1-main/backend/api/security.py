"""
API Security utilities - Re-exports from core.security

This module provides a convenient import path for security utilities
used in the API layer. All implementations are in backend.core.security.

Usage:
    from backend.api.security import (
        hash_password,
        verify_password,
        create_access_token,
        verify_token,
    )

For detailed documentation, see backend.core.security
"""

# Re-export all security functions from the canonical location
from backend.core.security import (
    # Configuration
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,

    # Password functions
    verify_password,
    get_password_hash,
    hash_password,  # Alias for get_password_hash

    # JWT Token functions
    create_access_token,
    create_refresh_token,
    decode_access_token,
    verify_token,
    get_user_id_from_token,
    create_token_pair,
    refresh_access_token,
)

# For backwards compatibility, expose validate_security_config
def validate_security_config() -> bool:
    """
    Validate security configuration.

    Security validation is now performed at module import time
    in backend.core.security. This function is kept for backwards
    compatibility but always returns True (validation happens on import).

    Returns:
        True (validation happens on import, errors raise exceptions)
    """
    return True


__all__ = [
    # Configuration
    "SECRET_KEY",
    "ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "REFRESH_TOKEN_EXPIRE_DAYS",

    # Password functions
    "verify_password",
    "get_password_hash",
    "hash_password",

    # JWT Token functions
    "create_access_token",
    "create_refresh_token",
    "decode_access_token",
    "verify_token",
    "get_user_id_from_token",
    "create_token_pair",
    "refresh_access_token",

    # Validation
    "validate_security_config",
]