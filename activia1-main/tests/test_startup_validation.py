"""
Tests for Startup Configuration Validation

Tests para src/ai_native_mvp/api/startup_validation.py

Verifica que el sistema detecte y bloquee configuraciones inseguras
antes de iniciar el servidor.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from backend.api.startup_validation import (
    StartupValidator,
    ConfigurationError,
    validate_startup_config,
)


class TestStartupValidator:
    """Tests para StartupValidator class"""

    @pytest.fixture
    def clean_env(self):
        """Limpia variables de entorno antes de cada test"""
        env_vars = [
            "ENVIRONMENT",
            "JWT_SECRET_KEY",
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "JWT_REFRESH_TOKEN_EXPIRE_DAYS",
            "LLM_PROVIDER",
            "OPENAI_API_KEY",
            "GEMINI_API_KEY",
            "ANTHROPIC_API_KEY",
            "ALLOWED_ORIGINS",
            "DEBUG",
            "DATABASE_URL",
            "RATE_LIMIT_PER_MINUTE",
            "RATE_LIMIT_PER_HOUR",
            "LOG_LEVEL",
        ]
        original_values = {}
        for var in env_vars:
            original_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

        yield

        # Restore
        for var, value in original_values.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    # =========================================================================
    # JWT Configuration Tests
    # =========================================================================

    def test_jwt_secret_key_missing(self, clean_env):
        """JWT_SECRET_KEY no configurado debe generar error"""
        os.environ["ENVIRONMENT"] = "development"

        validator = StartupValidator()
        is_valid, errors, warnings = validator.validate_all()

        assert not is_valid
        assert any("JWT_SECRET_KEY is REQUIRED" in err for err in errors)

    def test_jwt_secret_key_too_short(self, clean_env):
        """JWT_SECRET_KEY < 32 caracteres debe generar error"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "short_key_123"  # Solo 14 chars

        validator = StartupValidator()
        is_valid, errors, warnings = validator.validate_all()

        assert not is_valid
        assert any("too short" in err and "32 characters" in err for err in errors)

    def test_jwt_secret_key_weak_in_production(self, clean_env):
        """Clave débil en producción debe generar error"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "development_secret_key_change_in_production_12345678"

        validator = StartupValidator()
        is_valid, errors, warnings = validator.validate_all()

        assert not is_valid
        assert any("default/weak value" in err for err in errors)

    def test_jwt_secret_key_valid(self, clean_env):
        """Clave JWT válida debe pasar validación"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32  # 32 caracteres válidos

        validator = StartupValidator()
        validator._validate_jwt_config()

        assert len(validator.errors) == 0

    def test_jwt_access_token_expire_too_long(self, clean_env):
        """Token de acceso con expiración muy larga debe generar warning"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["JWT_ACCESS_TOKEN_EXPIRE_MINUTES"] = "2000"  # > 24 horas

        validator = StartupValidator()
        validator._validate_jwt_config()

        assert any("very long" in warn for warn in validator.warnings)

    def test_jwt_refresh_token_expire_too_long(self, clean_env):
        """Token refresh con expiración muy larga debe generar warning"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["JWT_REFRESH_TOKEN_EXPIRE_DAYS"] = "100"  # > 90 días

        validator = StartupValidator()
        validator._validate_jwt_config()

        assert any("very long" in warn for warn in validator.warnings)

    # =========================================================================
    # LLM Provider Tests
    # =========================================================================

    def test_llm_provider_invalid(self, clean_env):
        """Proveedor LLM inválido debe generar error"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["LLM_PROVIDER"] = "invalid_provider"

        validator = StartupValidator()
        validator._validate_llm_provider()

        assert any("invalid" in err.lower() for err in validator.errors)

    def test_llm_provider_openai_missing_api_key(self, clean_env):
        """OpenAI sin API key debe generar error"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["LLM_PROVIDER"] = "openai"
        # No configurar OPENAI_API_KEY

        validator = StartupValidator()
        validator._validate_llm_provider()

        assert any("OPENAI_API_KEY is required" in err for err in validator.errors)

    def test_llm_provider_openai_invalid_api_key_format(self, clean_env):
        """OpenAI con API key sin prefijo sk- debe generar warning"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ["OPENAI_API_KEY"] = "invalid_key_format"

        validator = StartupValidator()
        validator._validate_llm_provider()

        assert any("does not start with 'sk-'" in warn for warn in validator.warnings)

    def test_llm_provider_gemini_missing_api_key(self, clean_env):
        """Gemini sin API key debe generar error"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["LLM_PROVIDER"] = "gemini"

        validator = StartupValidator()
        validator._validate_llm_provider()

        assert any("GEMINI_API_KEY is required" in err for err in validator.errors)

    def test_llm_provider_mock_in_production_warning(self, clean_env):
        """Mock provider en producción debe generar warning"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["LLM_PROVIDER"] = "mock"

        validator = StartupValidator()
        validator._validate_llm_provider()

        assert any("mock" in warn.lower() and "production" in warn.lower() for warn in validator.warnings)

    # =========================================================================
    # CORS Origins Tests
    # =========================================================================

    def test_cors_localhost_in_production(self, clean_env):
        """CORS con localhost en producción debe generar error"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000,https://app.example.com"

        validator = StartupValidator()
        validator._validate_cors_origins()

        assert any("localhost" in err and "PRODUCTION" in err for err in validator.errors)

    def test_cors_invalid_url_format(self, clean_env):
        """CORS con URL sin http/https debe generar error"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["ALLOWED_ORIGINS"] = "app.example.com,http://localhost:3000"

        validator = StartupValidator()
        validator._validate_cors_origins()

        assert any("invalid origin" in err.lower() for err in validator.errors)

    def test_cors_valid_origins(self, clean_env):
        """CORS con orígenes válidos debe pasar"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["ALLOWED_ORIGINS"] = "https://app.example.com,https://www.example.com"

        validator = StartupValidator()
        validator._validate_cors_origins()

        assert len(validator.errors) == 0

    # =========================================================================
    # Debug Mode Tests
    # =========================================================================

    def test_debug_true_in_production(self, clean_env):
        """DEBUG=true en producción debe generar error"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["DEBUG"] = "true"

        validator = StartupValidator()
        validator._validate_debug_mode()

        assert any("DEBUG=true in PRODUCTION" in err for err in validator.errors)

    def test_debug_false_in_production(self, clean_env):
        """DEBUG=false en producción debe pasar"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["DEBUG"] = "false"

        validator = StartupValidator()
        validator._validate_debug_mode()

        assert len(validator.errors) == 0

    def test_debug_invalid_value(self, clean_env):
        """DEBUG con valor inválido debe generar warning"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["DEBUG"] = "maybe"

        validator = StartupValidator()
        validator._validate_debug_mode()

        assert any("invalid value" in warn.lower() for warn in validator.warnings)

    # =========================================================================
    # Database URL Tests
    # =========================================================================

    def test_database_url_sqlite_in_production_warning(self, clean_env):
        """SQLite en producción debe generar warning"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["DATABASE_URL"] = "sqlite:///ai_native.db"

        validator = StartupValidator()
        validator._validate_database_url()

        assert any("SQLite in PRODUCTION" in warn for warn in validator.warnings)

    def test_database_url_invalid_scheme(self, clean_env):
        """Database URL con esquema inválido debe generar error"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["DATABASE_URL"] = "mongodb://localhost/db"

        validator = StartupValidator()
        validator._validate_database_url()

        assert any("invalid scheme" in err.lower() for err in validator.errors)

    def test_database_url_postgresql_valid(self, clean_env):
        """PostgreSQL URL válida debe pasar"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost:5432/ai_native"

        validator = StartupValidator()
        validator._validate_database_url()

        assert len(validator.errors) == 0

    # =========================================================================
    # Rate Limiting Tests
    # =========================================================================

    def test_rate_limit_per_minute_invalid(self, clean_env):
        """Rate limit con valor no numérico debe generar error"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["RATE_LIMIT_PER_MINUTE"] = "not_a_number"

        validator = StartupValidator()
        validator._validate_rate_limiting()

        assert any("must be an integer" in err for err in validator.errors)

    def test_rate_limit_per_minute_too_low(self, clean_env):
        """Rate limit < 1 debe generar error"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["RATE_LIMIT_PER_MINUTE"] = "0"

        validator = StartupValidator()
        validator._validate_rate_limiting()

        assert any("must be >= 1" in err for err in validator.errors)

    def test_rate_limit_very_high_warning(self, clean_env):
        """Rate limit muy alto debe generar warning"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["RATE_LIMIT_PER_MINUTE"] = "5000"

        validator = StartupValidator()
        validator._validate_rate_limiting()

        assert any("very high" in warn.lower() for warn in validator.warnings)

    # =========================================================================
    # Secret Keys Tests
    # =========================================================================

    def test_log_level_debug_in_production_warning(self, clean_env):
        """LOG_LEVEL=DEBUG en producción debe generar warning"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["LOG_LEVEL"] = "DEBUG"

        validator = StartupValidator()
        validator._validate_secret_keys()

        assert any("LOG_LEVEL=DEBUG in PRODUCTION" in warn for warn in validator.warnings)

    # =========================================================================
    # Integration Tests
    # =========================================================================

    def test_validate_all_development_valid_config(self, clean_env):
        """Configuración válida de desarrollo debe pasar todas las validaciones"""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["LLM_PROVIDER"] = "mock"
        os.environ["DEBUG"] = "true"
        os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"

        validator = StartupValidator()
        is_valid, errors, warnings = validator.validate_all()

        assert is_valid
        assert len(errors) == 0

    def test_validate_all_production_valid_config(self, clean_env):
        """Configuración válida de producción debe pasar todas las validaciones"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "a" * 32
        os.environ["LLM_PROVIDER"] = "openai"
        os.environ["OPENAI_API_KEY"] = "sk-proj-test123456789"
        os.environ["DEBUG"] = "false"
        os.environ["ALLOWED_ORIGINS"] = "https://app.example.com"
        os.environ["DATABASE_URL"] = "postgresql://user:pass@localhost/db"

        validator = StartupValidator()
        is_valid, errors, warnings = validator.validate_all()

        assert is_valid
        assert len(errors) == 0

    def test_validate_all_production_multiple_errors(self, clean_env):
        """Configuración insegura de producción debe generar múltiples errores"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "weak"  # Muy corta
        os.environ["DEBUG"] = "true"  # Debug en producción
        os.environ["ALLOWED_ORIGINS"] = "http://localhost:3000"  # Localhost en producción

        validator = StartupValidator()
        is_valid, errors, warnings = validator.validate_all()

        assert not is_valid
        assert len(errors) >= 3  # Al menos 3 errores críticos

    def test_validate_startup_config_blocks_on_error(self, clean_env):
        """validate_startup_config debe lanzar excepción si hay errores"""
        os.environ["ENVIRONMENT"] = "production"
        os.environ["JWT_SECRET_KEY"] = "short"  # Inválida
        os.environ["DEBUG"] = "true"

        with pytest.raises(ConfigurationError) as exc_info:
            validate_startup_config()

        assert "CRITICAL CONFIGURATION ERRORS" in str(exc_info.value)


class TestEnvironmentModes:
    """Tests para diferentes modos de ambiente"""

    def test_production_mode_is_strict(self):
        """Modo producción debe ser estricto con validaciones"""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "JWT_SECRET_KEY": "a" * 32,
            "DEBUG": "true"  # Error en producción
        }, clear=True):
            validator = StartupValidator()
            assert validator.is_production is True

            is_valid, errors, warnings = validator.validate_all()
            assert not is_valid  # Debe fallar

    def test_development_mode_is_permissive(self):
        """Modo desarrollo debe ser permisivo"""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "JWT_SECRET_KEY": "a" * 32,
            "DEBUG": "true"  # OK en desarrollo
        }, clear=True):
            validator = StartupValidator()
            assert validator.is_production is False

            is_valid, errors, warnings = validator.validate_all()
            # En desarrollo, DEBUG=true no genera error
            # Solo verificamos que no haya errores críticos
            assert all("DEBUG" not in err for err in errors)


@pytest.mark.integration
class TestStartupIntegration:
    """Tests de integración con el sistema completo"""

    def test_startup_validation_runs_on_import(self):
        """Validación debe ejecutarse al importar el módulo"""
        # Este test verifica que el código al final de startup_validation.py
        # se ejecuta correctamente sin errores fatales
        # (ya se ejecutó al importar al inicio del archivo)
        from backend.api import startup_validation
        assert hasattr(startup_validation, 'StartupValidator')
        assert hasattr(startup_validation, 'validate_startup_config')

    def test_can_create_multiple_validators(self):
        """Se pueden crear múltiples instancias de validator"""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "JWT_SECRET_KEY": "a" * 32
        }, clear=True):
            validator1 = StartupValidator()
            validator2 = StartupValidator()

            assert validator1 is not validator2
            assert validator1.environment == validator2.environment
