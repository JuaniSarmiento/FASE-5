"""
Core security utilities for JWT authentication and password hashing.

This module provides the canonical security implementation for the AI-Native MVP.
It consolidates security functions to avoid duplicate implementations.

Provides:
- Password hashing with bcrypt (via passlib)
- JWT token creation and verification
- Secure configuration from environment variables

SECURITY NOTES:
- JWT_SECRET_KEY is REQUIRED (no insecure defaults)
- Minimum key length: 32 characters
- bcrypt is used for password hashing (secure against rainbow tables)
"""
import os
import logging
from datetime import timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
import bcrypt

from backend.core.constants import utc_now

logger = logging.getLogger(__name__)

# JWT configuration from environment
# SECURITY: No default value - must be explicitly set
SECRET_KEY = os.getenv("JWT_SECRET_KEY")

# Environment check
_is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"

# Validate SECRET_KEY
if not SECRET_KEY:
    if _is_production:
        raise RuntimeError(
            "SECURITY ERROR: JWT_SECRET_KEY environment variable is REQUIRED.\n"
            "Generate a secure random key with:\n"
            "  python -c 'import secrets; print(secrets.token_urlsafe(32))'\n"
            "Then set it in your .env file:\n"
            "  JWT_SECRET_KEY=<generated_key>"
        )
    else:
        # Development fallback with clear warning
        SECRET_KEY = "dev-only-insecure-key-do-not-use-in-production-123456"
        logger.warning(
            "⚠️  Using development SECRET_KEY - NOT secure for production!\n"
            "Set JWT_SECRET_KEY in your .env file for production use."
        )

# Validate key length in production
if _is_production and len(SECRET_KEY) < 32:
    raise RuntimeError(
        f"SECURITY ERROR: JWT_SECRET_KEY must be at least 32 characters long.\n"
        f"Current length: {len(SECRET_KEY)} characters.\n"
        f"Generate a new one with:\n"
        f"  python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


# =============================================================================
# Password Functions
# =============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.

    Args:
        plain_password: Plain text password from user
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    try:
        # Apply 72-byte truncation (bcrypt limitation)
        password_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}")
        return False


def get_password_hash(password: str) -> str:
    """
    Generate a bcrypt hash of a password.

    Bcrypt has a maximum password length of 72 bytes. Passwords longer than
    72 bytes are automatically truncated.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    # Apply 72-byte truncation (bcrypt limitation)
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12)).decode('utf-8')


# Alias for consistency with api/security.py
hash_password = get_password_hash


# =============================================================================
# JWT Token Functions
# =============================================================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data to encode (typically {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = utc_now() + expires_delta
    else:
        expire = utc_now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT refresh token (longer expiration).

    Args:
        data: Payload data to encode (typically {"sub": user_id})
        expires_delta: Optional custom expiration time

    Returns:
        JWT refresh token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = utc_now() + expires_delta
    else:
        expire = utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.debug(f"JWT decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Token decode error: {str(e)}")
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token with type checking.

    Args:
        token: JWT token string
        token_type: Expected token type ("access" or "refresh")

    Returns:
        Decoded payload dict if valid, None if invalid
    """
    payload = decode_access_token(token)
    if not payload:
        return None

    # Verify token type if present
    if payload.get("type") and payload.get("type") != token_type:
        logger.warning(
            f"Token type mismatch: expected {token_type}, got {payload.get('type')}"
        )
        return None

    return payload


def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from JWT token.

    Args:
        token: JWT access token string

    Returns:
        User ID string if valid, None if invalid
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None


def create_token_pair(
    user_id: str,
    additional_claims: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Create both access and refresh tokens for a user.

    Args:
        user_id: User ID
        additional_claims: Optional additional claims to include

    Returns:
        Dict with "access_token", "refresh_token", and "token_type" keys
    """
    payload = {"sub": user_id}
    if additional_claims:
        payload.update(additional_claims)

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token({"sub": user_id})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Generate a new access token from a refresh token.

    Args:
        refresh_token: Valid refresh token

    Returns:
        New access token if refresh token is valid, None otherwise
    """
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    return create_access_token({"sub": user_id})