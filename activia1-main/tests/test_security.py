"""
Tests for Security Module

Verifies:
- Password hashing with bcrypt
- Password verification
- JWT access token creation and verification
- JWT refresh token creation and verification
- Token pair generation
- Token refresh flow
- User ID extraction from tokens
- Security configuration validation
"""
import pytest
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from jose import jwt

# Set required environment variables BEFORE importing security module
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest-minimum-32-chars")


# ============================================================================
# Password Hashing Tests
# ============================================================================

class TestPasswordHashing:
    """Tests for password hashing functions"""

    def test_hash_password_returns_hash(self):
        """Test that hash_password returns a bcrypt hash"""
        from backend.api.security import hash_password

        password = "my_secure_password"
        hashed = hash_password(password)

        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")  # bcrypt hash prefix

    def test_hash_password_different_for_same_input(self):
        """Test that hashing same password twice gives different hashes (salt)"""
        from backend.api.security import hash_password

        password = "my_secure_password"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # Different due to salt

    def test_hash_password_truncates_at_72_bytes(self):
        """Test that passwords longer than 72 bytes are truncated"""
        from backend.api.security import hash_password, verify_password

        # Create a password longer than 72 bytes
        long_password = "a" * 100

        hashed = hash_password(long_password)

        # Should verify with truncated version
        assert verify_password(long_password, hashed) is True

        # Should also verify with exactly 72 chars
        assert verify_password("a" * 72, hashed) is True

    def test_hash_password_handles_unicode(self):
        """Test that unicode passwords are handled correctly"""
        from backend.api.security import hash_password, verify_password

        password = "contraseña_segura_ñ_ü_é"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_hash_password_empty_string(self):
        """Test hashing empty password"""
        from backend.api.security import hash_password, verify_password

        password = ""
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password("", hashed) is True


class TestPasswordVerification:
    """Tests for password verification"""

    def test_verify_password_correct(self):
        """Test verification with correct password"""
        from backend.api.security import hash_password, verify_password

        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test verification with incorrect password"""
        from backend.api.security import hash_password, verify_password

        password = "correct_password"
        hashed = hash_password(password)

        assert verify_password("wrong_password", hashed) is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        from backend.api.security import hash_password, verify_password

        password = "MyPassword"
        hashed = hash_password(password)

        assert verify_password("MyPassword", hashed) is True
        assert verify_password("mypassword", hashed) is False
        assert verify_password("MYPASSWORD", hashed) is False

    def test_verify_password_invalid_hash(self):
        """Test verification with invalid hash returns False"""
        from backend.api.security import verify_password

        result = verify_password("password", "invalid_hash")
        assert result is False

    def test_verify_password_malformed_hash(self):
        """Test verification with malformed hash"""
        from backend.api.security import verify_password

        result = verify_password("password", "$2b$invalid")
        assert result is False

    def test_verify_password_none_hash(self):
        """Test verification with None hash"""
        from backend.api.security import verify_password

        # Should handle gracefully and return False
        try:
            result = verify_password("password", None)
            assert result is False
        except (TypeError, AttributeError):
            pass  # Expected behavior


# ============================================================================
# Access Token Tests
# ============================================================================

class TestAccessToken:
    """Tests for JWT access token functions"""

    def test_create_access_token_basic(self):
        """Test basic access token creation"""
        from backend.api.security import create_access_token

        data = {"sub": "user_123"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_payload(self):
        """Test that token contains expected payload"""
        from backend.api.security import create_access_token, SECRET_KEY, ALGORITHM

        data = {"sub": "user_123", "email": "user@example.com"}
        token = create_access_token(data)

        # Decode without verification to check payload
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["sub"] == "user_123"
        assert payload["email"] == "user@example.com"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_access_token_default_expiration(self):
        """Test default expiration time"""
        from backend.api.security import (
            create_access_token,
            SECRET_KEY,
            ALGORITHM,
            ACCESS_TOKEN_EXPIRE_MINUTES
        )

        data = {"sub": "user_123"}
        token = create_access_token(data)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.utcfromtimestamp(payload["exp"])

        # Should expire around ACCESS_TOKEN_EXPIRE_MINUTES from now
        expected_exp = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        diff = abs((exp_time - expected_exp).total_seconds())

        assert diff < 5  # Within 5 seconds tolerance

    def test_create_access_token_custom_expiration(self):
        """Test custom expiration time"""
        from backend.api.security import create_access_token, SECRET_KEY, ALGORITHM

        data = {"sub": "user_123"}
        custom_delta = timedelta(hours=2)
        token = create_access_token(data, expires_delta=custom_delta)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_time = datetime.utcfromtimestamp(payload["exp"])

        expected_exp = datetime.utcnow() + custom_delta
        diff = abs((exp_time - expected_exp).total_seconds())

        assert diff < 5

    def test_create_access_token_does_not_modify_input(self):
        """Test that input data is not modified"""
        from backend.api.security import create_access_token

        data = {"sub": "user_123"}
        original_keys = set(data.keys())

        create_access_token(data)

        assert set(data.keys()) == original_keys


# ============================================================================
# Refresh Token Tests
# ============================================================================

class TestRefreshToken:
    """Tests for JWT refresh token functions"""

    def test_create_refresh_token_basic(self):
        """Test basic refresh token creation"""
        from backend.api.security import create_refresh_token

        data = {"sub": "user_123"}
        token = create_refresh_token(data)

        assert token is not None
        assert isinstance(token, str)

    def test_create_refresh_token_type_is_refresh(self):
        """Test that refresh token has correct type"""
        from backend.api.security import create_refresh_token, SECRET_KEY, ALGORITHM

        data = {"sub": "user_123"}
        token = create_refresh_token(data)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["type"] == "refresh"

    def test_create_refresh_token_longer_expiration(self):
        """Test that refresh token has longer expiration than access token"""
        from backend.api.security import (
            create_access_token,
            create_refresh_token,
            SECRET_KEY,
            ALGORITHM
        )

        data = {"sub": "user_123"}
        access_token = create_access_token(data)
        refresh_token = create_refresh_token(data)

        access_payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        refresh_payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        access_exp = access_payload["exp"]
        refresh_exp = refresh_payload["exp"]

        assert refresh_exp > access_exp


# ============================================================================
# Token Verification Tests
# ============================================================================

class TestTokenVerification:
    """Tests for token verification"""

    def test_verify_token_valid_access(self):
        """Test verification of valid access token"""
        from backend.api.security import create_access_token, verify_token

        data = {"sub": "user_123"}
        token = create_access_token(data)

        payload = verify_token(token, token_type="access")

        assert payload is not None
        assert payload["sub"] == "user_123"
        assert payload["type"] == "access"

    def test_verify_token_valid_refresh(self):
        """Test verification of valid refresh token"""
        from backend.api.security import create_refresh_token, verify_token

        data = {"sub": "user_123"}
        token = create_refresh_token(data)

        payload = verify_token(token, token_type="refresh")

        assert payload is not None
        assert payload["sub"] == "user_123"
        assert payload["type"] == "refresh"

    def test_verify_token_type_mismatch(self):
        """Test verification fails when token type doesn't match"""
        from backend.api.security import create_access_token, verify_token

        data = {"sub": "user_123"}
        access_token = create_access_token(data)

        # Try to verify access token as refresh token
        payload = verify_token(access_token, token_type="refresh")

        assert payload is None

    def test_verify_token_invalid_token(self):
        """Test verification of invalid token"""
        from backend.api.security import verify_token

        payload = verify_token("invalid.token.string")

        assert payload is None

    def test_verify_token_tampered_token(self):
        """Test verification of tampered token"""
        from backend.api.security import create_access_token, verify_token

        data = {"sub": "user_123"}
        token = create_access_token(data)

        # Tamper with token
        parts = token.split(".")
        parts[1] = parts[1] + "tampered"
        tampered_token = ".".join(parts)

        payload = verify_token(tampered_token)

        assert payload is None

    def test_verify_token_expired(self):
        """Test verification of expired token"""
        from backend.api.security import create_access_token, verify_token

        data = {"sub": "user_123"}
        # Create token that expires immediately
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))

        payload = verify_token(token)

        assert payload is None

    def test_verify_token_wrong_secret(self):
        """Test verification with wrong secret key"""
        from backend.api.security import ALGORITHM

        # Create token with different secret
        data = {"sub": "user_123", "type": "access", "exp": datetime.utcnow() + timedelta(hours=1)}
        wrong_secret_token = jwt.encode(data, "wrong_secret_key", algorithm=ALGORITHM)

        from backend.api.security import verify_token
        payload = verify_token(wrong_secret_token)

        assert payload is None


# ============================================================================
# User ID Extraction Tests
# ============================================================================

class TestUserIdExtraction:
    """Tests for extracting user ID from tokens"""

    def test_get_user_id_from_valid_token(self):
        """Test extracting user ID from valid token"""
        from backend.api.security import create_access_token, get_user_id_from_token

        token = create_access_token({"sub": "user_123"})
        user_id = get_user_id_from_token(token)

        assert user_id == "user_123"

    def test_get_user_id_from_invalid_token(self):
        """Test extracting user ID from invalid token"""
        from backend.api.security import get_user_id_from_token

        user_id = get_user_id_from_token("invalid.token")

        assert user_id is None

    def test_get_user_id_from_refresh_token_fails(self):
        """Test that get_user_id_from_token fails for refresh tokens"""
        from backend.api.security import create_refresh_token, get_user_id_from_token

        refresh_token = create_refresh_token({"sub": "user_123"})
        user_id = get_user_id_from_token(refresh_token)

        # Should fail because it expects access token type
        assert user_id is None

    def test_get_user_id_token_without_sub(self):
        """Test extracting user ID from token without sub claim"""
        from backend.api.security import SECRET_KEY, ALGORITHM, get_user_id_from_token

        # Create token without sub
        data = {"type": "access", "exp": datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

        user_id = get_user_id_from_token(token)

        assert user_id is None


# ============================================================================
# Token Pair Tests
# ============================================================================

class TestTokenPair:
    """Tests for token pair generation"""

    def test_create_token_pair_returns_both_tokens(self):
        """Test that token pair contains both access and refresh tokens"""
        from backend.api.security import create_token_pair

        tokens = create_token_pair("user_123")

        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert "token_type" in tokens
        assert tokens["token_type"] == "bearer"

    def test_create_token_pair_tokens_are_valid(self):
        """Test that both tokens in pair are valid"""
        from backend.api.security import create_token_pair, verify_token

        tokens = create_token_pair("user_123")

        access_payload = verify_token(tokens["access_token"], token_type="access")
        refresh_payload = verify_token(tokens["refresh_token"], token_type="refresh")

        assert access_payload is not None
        assert access_payload["sub"] == "user_123"

        assert refresh_payload is not None
        assert refresh_payload["sub"] == "user_123"

    def test_create_token_pair_with_additional_claims(self):
        """Test token pair with additional claims"""
        from backend.api.security import create_token_pair, verify_token

        additional_claims = {"role": "student", "email": "user@example.com"}
        tokens = create_token_pair("user_123", additional_claims=additional_claims)

        access_payload = verify_token(tokens["access_token"], token_type="access")

        assert access_payload["role"] == "student"
        assert access_payload["email"] == "user@example.com"

    def test_create_token_pair_refresh_has_minimal_claims(self):
        """Test that refresh token only has user_id, not additional claims"""
        from backend.api.security import create_token_pair, verify_token

        additional_claims = {"role": "student", "email": "user@example.com"}
        tokens = create_token_pair("user_123", additional_claims=additional_claims)

        refresh_payload = verify_token(tokens["refresh_token"], token_type="refresh")

        # Refresh token should only have sub, not additional claims
        assert refresh_payload["sub"] == "user_123"
        assert "role" not in refresh_payload
        assert "email" not in refresh_payload


# ============================================================================
# Token Refresh Tests
# ============================================================================

class TestTokenRefresh:
    """Tests for token refresh functionality"""

    def test_refresh_access_token_valid(self):
        """Test refreshing access token with valid refresh token"""
        from backend.api.security import (
            create_token_pair,
            refresh_access_token,
            verify_token
        )

        tokens = create_token_pair("user_123")
        new_access_token = refresh_access_token(tokens["refresh_token"])

        assert new_access_token is not None

        payload = verify_token(new_access_token, token_type="access")
        assert payload["sub"] == "user_123"

    def test_refresh_access_token_invalid_refresh_token(self):
        """Test refresh with invalid refresh token"""
        from backend.api.security import refresh_access_token

        new_token = refresh_access_token("invalid.token")

        assert new_token is None

    def test_refresh_access_token_with_access_token_fails(self):
        """Test that using access token for refresh fails"""
        from backend.api.security import create_access_token, refresh_access_token

        access_token = create_access_token({"sub": "user_123"})
        new_token = refresh_access_token(access_token)

        assert new_token is None

    def test_refresh_access_token_expired_refresh(self):
        """Test refresh with expired refresh token"""
        from backend.api.security import create_refresh_token, refresh_access_token

        # Create expired refresh token
        expired_refresh = create_refresh_token(
            {"sub": "user_123"},
            expires_delta=timedelta(seconds=-1)
        )

        new_token = refresh_access_token(expired_refresh)

        assert new_token is None


# ============================================================================
# Security Configuration Tests
# ============================================================================

class TestSecurityConfiguration:
    """Tests for security configuration validation"""

    def test_validate_security_config_returns_true(self):
        """Test that validation returns True for valid config"""
        from backend.api.security import validate_security_config

        # Should return True for test environment
        result = validate_security_config()
        assert result is True

    def test_secret_key_minimum_length(self):
        """Test that SECRET_KEY meets minimum length requirement"""
        from backend.api.security import SECRET_KEY

        assert len(SECRET_KEY) >= 32

    def test_algorithm_is_configured(self):
        """Test that ALGORITHM is configured"""
        from backend.api.security import ALGORITHM

        assert ALGORITHM is not None
        assert ALGORITHM in ["HS256", "HS384", "HS512"]

    def test_token_expiration_configured(self):
        """Test that token expiration times are configured"""
        from backend.api.security import (
            ACCESS_TOKEN_EXPIRE_MINUTES,
            REFRESH_TOKEN_EXPIRE_DAYS
        )

        assert ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert REFRESH_TOKEN_EXPIRE_DAYS > 0
        assert REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 > ACCESS_TOKEN_EXPIRE_MINUTES


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling"""

    def test_empty_user_id(self):
        """Test token creation with empty user ID"""
        from backend.api.security import create_access_token, verify_token

        token = create_access_token({"sub": ""})
        payload = verify_token(token)

        assert payload is not None
        assert payload["sub"] == ""

    def test_special_characters_in_user_id(self):
        """Test token with special characters in user ID"""
        from backend.api.security import create_access_token, get_user_id_from_token

        special_user_id = "user@example.com/special:chars"
        token = create_access_token({"sub": special_user_id})

        extracted = get_user_id_from_token(token)
        assert extracted == special_user_id

    def test_very_long_user_id(self):
        """Test token with very long user ID"""
        from backend.api.security import create_access_token, get_user_id_from_token

        long_user_id = "user_" + "x" * 1000
        token = create_access_token({"sub": long_user_id})

        extracted = get_user_id_from_token(token)
        assert extracted == long_user_id

    def test_unicode_in_claims(self):
        """Test token with unicode in claims"""
        from backend.api.security import create_access_token, verify_token

        data = {"sub": "user_123", "name": "José García", "emoji": "🔐"}
        token = create_access_token(data)

        payload = verify_token(token)
        assert payload["name"] == "José García"
        assert payload["emoji"] == "🔐"

    def test_nested_claims(self):
        """Test token with nested claims"""
        from backend.api.security import create_access_token, verify_token

        data = {
            "sub": "user_123",
            "permissions": {"read": True, "write": False},
            "roles": ["student", "viewer"]
        }
        token = create_access_token(data)

        payload = verify_token(token)
        assert payload["permissions"]["read"] is True
        assert "student" in payload["roles"]