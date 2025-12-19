"""
Startup Configuration Validation

Validates critical environment variables at application startup to prevent
deployment with unsafe configuration.

CRITICAL: This module MUST run before the FastAPI app starts to ensure
production deployments have secure configuration.

Validations:
- JWT authentication configuration
- LLM provider configuration
- CORS origins (no localhost in production)
- Debug mode (disabled in production)
- Database URL format
- Rate limiting configuration
"""

import os
import re
import logging
from typing import List, Tuple, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or unsafe"""
    pass


class StartupValidator:
    """
    Validates environment configuration at startup

    Prevents unsafe deployments by checking critical settings before
    the application starts accepting requests.
    """

    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment == "production"
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validation checks

        Returns:
            Tuple of (is_valid, errors, warnings)

        Raises:
            ConfigurationError: If critical validation fails
        """
        logger.info(
            "Starting configuration validation",
            extra={"environment": self.environment}
        )

        # Run all validations
        self._validate_jwt_config()
        self._validate_llm_provider()
        self._validate_cors_origins()
        self._validate_debug_mode()
        self._validate_database_url()
        self._validate_rate_limiting()
        self._validate_secret_keys()

        # Log results
        if self.errors:
            logger.error(
                "Configuration validation FAILED",
                extra={
                    "environment": self.environment,
                    "errors": len(self.errors),
                    "warnings": len(self.warnings)
                }
            )
            for error in self.errors:
                logger.error(f"  [ERROR] {error}")

        if self.warnings:
            for warning in self.warnings:
                logger.warning(f"  [WARN] {warning}")

        if not self.errors:
            logger.info(
                "[OK] Configuration validation PASSED",
                extra={
                    "environment": self.environment,
                    "warnings": len(self.warnings)
                }
            )

        return (len(self.errors) == 0, self.errors, self.warnings)

    def _validate_jwt_config(self):
        """Validate JWT authentication configuration"""
        jwt_secret = os.getenv("JWT_SECRET_KEY")

        if not jwt_secret:
            self.errors.append(
                "JWT_SECRET_KEY is REQUIRED. "
                "Generate with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
            return

        # Check length (minimum 32 characters)
        if len(jwt_secret) < 32:
            self.errors.append(
                f"JWT_SECRET_KEY is too short ({len(jwt_secret)} chars). "
                f"Minimum: 32 characters. "
                f"Generate a new one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )

        # Check for default/weak values in production
        if self.is_production:
            weak_keys = [
                "development_secret_key",
                "change_in_production",
                "secret",
                "test",
                "demo",
                "password",
                "12345",
            ]
            jwt_lower = jwt_secret.lower()
            if any(weak in jwt_lower for weak in weak_keys):
                self.errors.append(
                    "JWT_SECRET_KEY appears to be a default/weak value in PRODUCTION. "
                    "Use a cryptographically secure random key."
                )

        # Validate token expiration
        try:
            access_expire = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
            if access_expire > 1440:  # 24 hours
                self.warnings.append(
                    f"JWT_ACCESS_TOKEN_EXPIRE_MINUTES is very long ({access_expire} min). "
                    f"Recommended: 15-60 minutes."
                )
        except ValueError:
            self.errors.append("JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be an integer")

        try:
            refresh_expire = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
            if refresh_expire > 90:
                self.warnings.append(
                    f"JWT_REFRESH_TOKEN_EXPIRE_DAYS is very long ({refresh_expire} days). "
                    f"Recommended: 7-30 days."
                )
        except ValueError:
            self.errors.append("JWT_REFRESH_TOKEN_EXPIRE_DAYS must be an integer")

    def _validate_llm_provider(self):
        """Validate LLM provider configuration"""
        llm_provider = os.getenv("LLM_PROVIDER", "mock")

        valid_providers = ["mock", "ollama", "openai", "gemini", "mistral", "anthropic"]
        if llm_provider not in valid_providers:
            self.errors.append(
                f"LLM_PROVIDER '{llm_provider}' is invalid. "
                f"Valid options: {', '.join(valid_providers)}"
            )

        # Warn if using mock in production
        if self.is_production and llm_provider == "mock":
            self.warnings.append(
                "LLM_PROVIDER is 'mock' in PRODUCTION. "
                "Consider using 'ollama', 'openai', 'gemini', 'mistral', or 'anthropic'."
            )

        # Validate API keys if using real providers
        if llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                self.errors.append(
                    "OPENAI_API_KEY is required when LLM_PROVIDER='openai'"
                )
            elif not api_key.startswith("sk-"):
                self.warnings.append(
                    "OPENAI_API_KEY does not start with 'sk-'. "
                    "Verify it's a valid OpenAI API key."
                )

        elif llm_provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                self.errors.append(
                    "GEMINI_API_KEY is required when LLM_PROVIDER='gemini'"
                )
        
        elif llm_provider == "mistral":
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                self.errors.append(
                    "MISTRAL_API_KEY is required when LLM_PROVIDER='mistral'"
                )

        elif llm_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                self.errors.append(
                    "ANTHROPIC_API_KEY is required when LLM_PROVIDER='anthropic'"
                )
            elif not api_key.startswith("sk-ant-"):
                self.warnings.append(
                    "ANTHROPIC_API_KEY does not start with 'sk-ant-'. "
                    "Verify it's a valid Anthropic API key."
                )

    def _validate_cors_origins(self):
        """Validate CORS configuration"""
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "")

        if not allowed_origins:
            if self.is_production:
                self.warnings.append(
                    "ALLOWED_ORIGINS is not set in PRODUCTION. "
                    "CORS will be disabled (no cross-origin requests allowed)."
                )
            return

        origins = [o.strip() for o in allowed_origins.split(",")]

        # Check for localhost/development origins in production
        if self.is_production:
            dev_origins = [
                o for o in origins
                if "localhost" in o or "127.0.0.1" in o or ":300" in o or ":8080" in o
            ]
            if dev_origins:
                self.errors.append(
                    f"ALLOWED_ORIGINS contains development URLs in PRODUCTION: {dev_origins}. "
                    f"Remove localhost/development origins."
                )

        # Validate URL format
        for origin in origins:
            if not origin.startswith(("http://", "https://")):
                self.errors.append(
                    f"ALLOWED_ORIGINS contains invalid origin '{origin}'. "
                    f"Must start with http:// or https://"
                )

    def _validate_debug_mode(self):
        """Validate debug mode configuration"""
        debug = os.getenv("DEBUG", "false").lower()

        if debug not in ("true", "false", "1", "0"):
            self.warnings.append(
                f"DEBUG has invalid value '{debug}'. "
                f"Expected: true/false or 1/0"
            )

        # ERROR if debug=true in production
        if self.is_production and debug in ("true", "1"):
            self.errors.append(
                "DEBUG=true in PRODUCTION environment. "
                "This exposes sensitive error details and stack traces. "
                "Set DEBUG=false or remove it."
            )

    def _validate_database_url(self):
        """Validate database URL format"""
        db_url = os.getenv("DATABASE_URL")

        if not db_url:
            # SQLite default is OK for development
            if self.is_production:
                self.warnings.append(
                    "DATABASE_URL not set in PRODUCTION. "
                    "Using SQLite (ai_native.db). "
                    "Consider PostgreSQL for production."
                )
            return

        # Validate URL format
        try:
            parsed = urlparse(db_url)
            valid_schemes = ["sqlite", "postgresql", "postgres", "mysql"]

            if parsed.scheme not in valid_schemes:
                self.errors.append(
                    f"DATABASE_URL has invalid scheme '{parsed.scheme}'. "
                    f"Supported: {', '.join(valid_schemes)}"
                )

            # Warn if using SQLite in production
            if self.is_production and parsed.scheme == "sqlite":
                self.warnings.append(
                    "Using SQLite in PRODUCTION. "
                    "Consider PostgreSQL/MySQL for better concurrency and performance."
                )

        except Exception as e:
            self.errors.append(
                f"DATABASE_URL is malformed: {str(e)}"
            )

    def _validate_rate_limiting(self):
        """Validate rate limiting configuration"""
        try:
            per_minute = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
            if per_minute < 1:
                self.errors.append(
                    f"RATE_LIMIT_PER_MINUTE must be >= 1 (got {per_minute})"
                )
            elif per_minute > 1000:
                self.warnings.append(
                    f"RATE_LIMIT_PER_MINUTE is very high ({per_minute}). "
                    f"Verify this is intentional."
                )
        except ValueError:
            self.errors.append("RATE_LIMIT_PER_MINUTE must be an integer")

        try:
            per_hour = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
            if per_hour < 1:
                self.errors.append(
                    f"RATE_LIMIT_PER_HOUR must be >= 1 (got {per_hour})"
                )
        except ValueError:
            self.errors.append("RATE_LIMIT_PER_HOUR must be an integer")

    def _validate_secret_keys(self):
        """Validate all secret keys for production safety"""
        if not self.is_production:
            return

        # Check for exposed secrets in logs
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        if log_level == "DEBUG":
            self.warnings.append(
                "LOG_LEVEL=DEBUG in PRODUCTION. "
                "This may expose sensitive information in logs. "
                "Set LOG_LEVEL=INFO or WARNING."
            )


def validate_startup_config() -> None:
    """
    Validate configuration at startup

    This function MUST be called before the FastAPI app starts.

    Raises:
        ConfigurationError: If critical configuration is invalid
    """
    validator = StartupValidator()
    is_valid, errors, warnings = validator.validate_all()

    if not is_valid:
        error_msg = "CRITICAL CONFIGURATION ERRORS:\n" + "\n".join(
            f"  ❌ {err}" for err in errors
        )
        raise ConfigurationError(error_msg)

    if warnings:
        logger.warning(
            "Configuration has warnings (non-critical)",
            extra={"warnings_count": len(warnings)}
        )


# Run validation on module import (for safety)
# This ensures validation happens even if validate_startup_config() is not called
try:
    validator = StartupValidator()
    is_valid, errors, warnings = validator.validate_all()

    if not is_valid and validator.is_production:
        # In production, fail immediately
        raise ConfigurationError(
            f"CRITICAL: Configuration validation failed with {len(errors)} errors. "
            f"See logs for details."
        )
except ConfigurationError:
    # Re-raise configuration errors
    raise
except Exception as e:
    # Log but don't fail on unexpected errors during validation
    logger.error(
        f"Unexpected error during startup validation: {e}",
        exc_info=True
    )