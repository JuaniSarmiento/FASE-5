"""
Tests for Admin LLM Configuration Router

Tests para backend/api/routers/admin_llm.py

Verifica:
1. Listar proveedores LLM (GET /admin/llm/providers)
2. Obtener configuración de proveedor (GET /admin/llm/providers/{name})
3. Actualizar configuración (PATCH /admin/llm/providers/{name})
4. Estadísticas de uso (GET /admin/llm/usage/stats)
5. Probar conexión LLM (POST /admin/llm/test)
6. Métricas del sistema (GET /admin/llm/metrics)
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for LLM configuration"""
    return {
        "LLM_PROVIDER": "mock",
        "OPENAI_API_KEY": "sk-test-key",
        "OPENAI_MODEL": "gpt-4",
        "OPENAI_TEMPERATURE": "0.7",
        "OPENAI_MAX_TOKENS": "2000",
        "GEMINI_API_KEY": "",
        "GEMINI_MODEL": "gemini-1.5-flash",
        "ANTHROPIC_API_KEY": "sk-ant-test",
        "ANTHROPIC_MODEL": "claude-3-sonnet",
    }


@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing"""
    provider = MagicMock()
    provider.model_name = "mock-model"
    provider.generate = AsyncMock(return_value="OK")
    return provider


@pytest.fixture
def provider_config():
    """Sample provider configuration"""
    return {
        "provider": "openai",
        "enabled": True,
        "api_key_configured": True,
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000,
        "privacy_compliant": False,
        "cost_per_1k_tokens": 0.03,
        "limits": {
            "requests_per_day": "1000",
            "tokens_per_month": "500000"
        }
    }


@pytest.fixture
def provider_update_data():
    """Sample provider update request"""
    return {
        "enabled": True,
        "model": "gpt-3.5-turbo",
        "temperature": 0.5,
        "max_tokens": 1500,
        "daily_request_limit": 500,
        "monthly_token_limit": 250000
    }


# ============================================================================
# List Providers Tests
# ============================================================================

class TestListProviders:
    """Tests for GET /admin/llm/providers endpoint"""

    @pytest.mark.unit
    def test_list_providers_returns_all(self, mock_env_vars):
        """list_llm_providers() returns all configured providers"""
        with patch.dict('os.environ', mock_env_vars):
            from backend.api.routers.admin_llm import list_llm_providers
            import asyncio

            response = asyncio.get_event_loop().run_until_complete(list_llm_providers())

            assert response.success is True
            assert len(response.data) >= 4  # mock, openai, gemini, anthropic
            provider_names = [p.provider for p in response.data]
            assert "mock" in provider_names
            assert "openai" in provider_names
            assert "gemini" in provider_names
            assert "anthropic" in provider_names

    @pytest.mark.unit
    def test_list_providers_includes_required_fields(self, mock_env_vars):
        """Each provider includes all required configuration fields"""
        with patch.dict('os.environ', mock_env_vars):
            from backend.api.routers.admin_llm import list_llm_providers
            import asyncio

            response = asyncio.get_event_loop().run_until_complete(list_llm_providers())

            for provider in response.data:
                assert hasattr(provider, 'provider')
                assert hasattr(provider, 'enabled')
                assert hasattr(provider, 'api_key_configured')
                assert hasattr(provider, 'privacy_compliant')

    @pytest.mark.unit
    def test_list_providers_detects_api_keys(self, mock_env_vars):
        """list_llm_providers() correctly detects API key configuration"""
        with patch.dict('os.environ', mock_env_vars):
            from backend.api.routers.admin_llm import list_llm_providers
            import asyncio

            response = asyncio.get_event_loop().run_until_complete(list_llm_providers())

            providers_dict = {p.provider: p for p in response.data}

            # OpenAI has key configured
            assert providers_dict["openai"].api_key_configured is True
            # Gemini doesn't have key
            assert providers_dict["gemini"].api_key_configured is False

    @pytest.mark.unit
    def test_list_providers_shows_current_enabled(self, mock_env_vars):
        """list_llm_providers() shows which provider is currently enabled"""
        with patch.dict('os.environ', mock_env_vars):
            from backend.api.routers.admin_llm import list_llm_providers
            import asyncio

            response = asyncio.get_event_loop().run_until_complete(list_llm_providers())

            providers_dict = {p.provider: p for p in response.data}

            # Mock is the current provider
            assert providers_dict["mock"].enabled is True
            assert providers_dict["openai"].enabled is False


# ============================================================================
# Get Provider Config Tests
# ============================================================================

class TestGetProviderConfig:
    """Tests for GET /admin/llm/providers/{name} endpoint"""

    @pytest.mark.unit
    def test_get_provider_success(self, mock_env_vars):
        """get_provider_config() returns specific provider configuration"""
        with patch.dict('os.environ', mock_env_vars):
            from backend.api.routers.admin_llm import get_provider_config
            import asyncio

            response = asyncio.get_event_loop().run_until_complete(
                get_provider_config("openai")
            )

            assert response.success is True
            assert response.data.provider == "openai"

    @pytest.mark.unit
    def test_get_provider_not_found(self, mock_env_vars):
        """get_provider_config() raises 404 for unknown provider"""
        with patch.dict('os.environ', mock_env_vars):
            from backend.api.routers.admin_llm import get_provider_config
            import asyncio

            with pytest.raises(HTTPException) as exc_info:
                asyncio.get_event_loop().run_until_complete(
                    get_provider_config("unknown_provider")
                )

            assert exc_info.value.status_code == 404

    @pytest.mark.unit
    def test_get_provider_includes_limits(self, mock_env_vars):
        """get_provider_config() includes usage limits"""
        with patch.dict('os.environ', mock_env_vars):
            from backend.api.routers.admin_llm import get_provider_config
            import asyncio

            response = asyncio.get_event_loop().run_until_complete(
                get_provider_config("openai")
            )

            assert response.data.limits is not None
            assert "requests_per_day" in response.data.limits


# ============================================================================
# Update Provider Config Tests
# ============================================================================

class TestUpdateProviderConfig:
    """Tests for PATCH /admin/llm/providers/{name} endpoint"""

    @pytest.mark.unit
    def test_update_provider_success(self, provider_update_data):
        """update_provider_config() returns confirmation"""
        from backend.api.routers.admin_llm import update_provider_config, LLMProviderUpdate
        import asyncio

        update = LLMProviderUpdate(**provider_update_data)
        response = asyncio.get_event_loop().run_until_complete(
            update_provider_config("openai", update)
        )

        assert response.success is True
        assert response.data["provider"] == "openai"
        assert "changes_applied" in response.data

    @pytest.mark.unit
    def test_update_provider_not_found(self, provider_update_data):
        """update_provider_config() raises 404 for unknown provider"""
        from backend.api.routers.admin_llm import update_provider_config, LLMProviderUpdate
        import asyncio

        update = LLMProviderUpdate(**provider_update_data)

        with pytest.raises(HTTPException) as exc_info:
            asyncio.get_event_loop().run_until_complete(
                update_provider_config("unknown_provider", update)
            )

        assert exc_info.value.status_code == 404

    @pytest.mark.unit
    def test_update_provider_partial(self):
        """update_provider_config() accepts partial updates"""
        from backend.api.routers.admin_llm import update_provider_config, LLMProviderUpdate
        import asyncio

        # Only update temperature
        update = LLMProviderUpdate(temperature=0.5)
        response = asyncio.get_event_loop().run_until_complete(
            update_provider_config("openai", update)
        )

        assert response.success is True
        assert "temperature" in response.data["changes_applied"]
        assert response.data["changes_applied"]["temperature"] == 0.5

    @pytest.mark.unit
    def test_update_provider_includes_next_steps(self, provider_update_data):
        """update_provider_config() includes next steps for applying changes"""
        from backend.api.routers.admin_llm import update_provider_config, LLMProviderUpdate
        import asyncio

        update = LLMProviderUpdate(**provider_update_data)
        response = asyncio.get_event_loop().run_until_complete(
            update_provider_config("openai", update)
        )

        assert "next_steps" in response.data
        assert len(response.data["next_steps"]) > 0


# ============================================================================
# Usage Stats Tests
# ============================================================================

class TestUsageStats:
    """Tests for GET /admin/llm/usage/stats endpoint"""

    @pytest.mark.unit
    def test_get_usage_stats_success(self):
        """get_llm_usage_stats() returns usage statistics"""
        from backend.api.routers.admin_llm import get_llm_usage_stats
        import asyncio

        response = asyncio.get_event_loop().run_until_complete(get_llm_usage_stats())

        assert response.success is True
        assert "total_requests" in response.data
        assert "total_tokens" in response.data
        assert "estimated_cost_usd" in response.data

    @pytest.mark.unit
    def test_usage_stats_includes_by_provider(self):
        """Usage stats include breakdown by provider"""
        from backend.api.routers.admin_llm import get_llm_usage_stats
        import asyncio

        response = asyncio.get_event_loop().run_until_complete(get_llm_usage_stats())

        assert "by_provider" in response.data
        assert isinstance(response.data["by_provider"], dict)

    @pytest.mark.unit
    def test_usage_stats_includes_top_activities(self):
        """Usage stats include top activities"""
        from backend.api.routers.admin_llm import get_llm_usage_stats
        import asyncio

        response = asyncio.get_event_loop().run_until_complete(get_llm_usage_stats())

        assert "top_activities" in response.data
        assert isinstance(response.data["top_activities"], list)

    @pytest.mark.unit
    def test_usage_stats_includes_limits_status(self):
        """Usage stats include limits status"""
        from backend.api.routers.admin_llm import get_llm_usage_stats
        import asyncio

        response = asyncio.get_event_loop().run_until_complete(get_llm_usage_stats())

        assert "limits_status" in response.data
        limits = response.data["limits_status"]
        assert "daily_limit" in limits
        assert "monthly_limit" in limits


# ============================================================================
# Test LLM Connection Tests
# ============================================================================

class TestLLMConnection:
    """Tests for POST /admin/llm/test endpoint"""

    @pytest.mark.unit
    def test_test_connection_invalid_provider(self):
        """test_llm_connection() returns error for invalid provider"""
        from backend.api.routers.admin_llm import test_llm_connection
        import asyncio

        response = asyncio.get_event_loop().run_until_complete(
            test_llm_connection("invalid_provider")
        )

        assert response.success is False
        assert response.data["status"] == "error"

    @pytest.mark.unit
    def test_test_connection_success(self, mock_llm_provider):
        """test_llm_connection() returns success for working provider"""
        from backend.api.routers.admin_llm import test_llm_connection
        import asyncio

        with patch('backend.api.routers.admin_llm.LLMProviderFactory') as mock_factory:
            mock_factory.create.return_value = mock_llm_provider

            response = asyncio.get_event_loop().run_until_complete(
                test_llm_connection("mock")
            )

            assert response.success is True
            assert response.data["status"] == "ok"
            assert "latency_ms" in response.data

    @pytest.mark.unit
    def test_test_connection_includes_latency(self, mock_llm_provider):
        """test_llm_connection() includes latency measurement"""
        from backend.api.routers.admin_llm import test_llm_connection
        import asyncio

        with patch('backend.api.routers.admin_llm.LLMProviderFactory') as mock_factory:
            mock_factory.create.return_value = mock_llm_provider

            response = asyncio.get_event_loop().run_until_complete(
                test_llm_connection("mock")
            )

            assert "latency_ms" in response.data
            assert isinstance(response.data["latency_ms"], (int, float))

    @pytest.mark.unit
    def test_test_connection_handles_error(self):
        """test_llm_connection() handles provider errors gracefully"""
        from backend.api.routers.admin_llm import test_llm_connection
        import asyncio

        with patch('backend.api.routers.admin_llm.LLMProviderFactory') as mock_factory:
            mock_factory.create.side_effect = Exception("Connection failed")

            response = asyncio.get_event_loop().run_until_complete(
                test_llm_connection("openai")
            )

            assert response.success is False
            assert response.data["status"] == "error"
            assert "error_type" in response.data

    @pytest.mark.unit
    def test_test_connection_with_custom_model(self, mock_llm_provider):
        """test_llm_connection() accepts custom model parameter"""
        from backend.api.routers.admin_llm import test_llm_connection
        import asyncio

        with patch('backend.api.routers.admin_llm.LLMProviderFactory') as mock_factory:
            mock_factory.create.return_value = mock_llm_provider

            response = asyncio.get_event_loop().run_until_complete(
                test_llm_connection("openai", model="gpt-3.5-turbo")
            )

            assert response.success is True


# ============================================================================
# System Metrics Tests
# ============================================================================

class TestSystemMetrics:
    """Tests for GET /admin/llm/metrics endpoint"""

    @pytest.mark.unit
    def test_get_metrics_success(self):
        """get_system_metrics() returns system metrics"""
        from backend.api.routers.admin_llm import get_system_metrics
        import asyncio

        response = asyncio.get_event_loop().run_until_complete(get_system_metrics())

        assert response.success is True
        assert "timestamp" in response.data

    @pytest.mark.unit
    def test_metrics_includes_user_stats(self):
        """System metrics include user statistics"""
        from backend.api.routers.admin_llm import get_system_metrics
        import asyncio

        response = asyncio.get_event_loop().run_until_complete(get_system_metrics())

        assert "total_users" in response.data
        assert "active_sessions" in response.data

    @pytest.mark.unit
    def test_metrics_includes_llm_usage(self):
        """System metrics include LLM usage data"""
        from backend.api.routers.admin_llm import get_system_metrics
        import asyncio

        response = asyncio.get_event_loop().run_until_complete(get_system_metrics())

        assert "llm_usage" in response.data
        assert isinstance(response.data["llm_usage"], list)

    @pytest.mark.unit
    def test_metrics_includes_service_status(self):
        """System metrics include service health status"""
        from backend.api.routers.admin_llm import get_system_metrics
        import asyncio

        response = asyncio.get_event_loop().run_until_complete(get_system_metrics())

        assert "database_status" in response.data
        assert "redis_status" in response.data
        assert "llm_status" in response.data

    @pytest.mark.unit
    def test_metrics_includes_performance(self):
        """System metrics include performance indicators"""
        from backend.api.routers.admin_llm import get_system_metrics
        import asyncio

        response = asyncio.get_event_loop().run_until_complete(get_system_metrics())

        assert "avg_response_time_ms" in response.data
        assert "total_interactions" in response.data


# ============================================================================
# Schema Validation Tests
# ============================================================================

class TestSchemaValidation:
    """Tests for request/response schema validation"""

    @pytest.mark.unit
    def test_provider_config_schema(self):
        """LLMProviderConfig schema is valid"""
        from backend.api.routers.admin_llm import LLMProviderConfig

        config = LLMProviderConfig(
            provider="openai",
            enabled=True,
            api_key_configured=True,
            privacy_compliant=False
        )

        assert config.provider == "openai"
        assert config.enabled is True

    @pytest.mark.unit
    def test_provider_update_schema_validation(self):
        """LLMProviderUpdate validates field ranges"""
        from backend.api.routers.admin_llm import LLMProviderUpdate
        from pydantic import ValidationError

        # Valid update
        update = LLMProviderUpdate(temperature=0.5, max_tokens=1000)
        assert update.temperature == 0.5

        # Invalid temperature (> 2.0)
        with pytest.raises(ValidationError):
            LLMProviderUpdate(temperature=3.0)

        # Invalid temperature (< 0.0)
        with pytest.raises(ValidationError):
            LLMProviderUpdate(temperature=-0.5)

    @pytest.mark.unit
    def test_provider_update_optional_fields(self):
        """LLMProviderUpdate allows all fields to be optional"""
        from backend.api.routers.admin_llm import LLMProviderUpdate

        # Empty update is valid
        update = LLMProviderUpdate()

        assert update.enabled is None
        assert update.model is None
        assert update.temperature is None


# ============================================================================
# Privacy Compliance Tests
# ============================================================================

class TestPrivacyCompliance:
    """Tests for privacy compliance indicators"""

    @pytest.mark.unit
    def test_mock_provider_is_privacy_compliant(self, mock_env_vars):
        """Mock provider is marked as privacy compliant"""
        with patch.dict('os.environ', mock_env_vars):
            from backend.api.routers.admin_llm import get_provider_config
            import asyncio

            response = asyncio.get_event_loop().run_until_complete(
                get_provider_config("mock")
            )

            assert response.data.privacy_compliant is True

    @pytest.mark.unit
    def test_external_providers_not_privacy_compliant(self, mock_env_vars):
        """External providers (OpenAI, Gemini, Anthropic) are not privacy compliant"""
        with patch.dict('os.environ', mock_env_vars):
            from backend.api.routers.admin_llm import list_llm_providers
            import asyncio

            response = asyncio.get_event_loop().run_until_complete(list_llm_providers())

            providers_dict = {p.provider: p for p in response.data}

            assert providers_dict["openai"].privacy_compliant is False
            assert providers_dict["gemini"].privacy_compliant is False
            assert providers_dict["anthropic"].privacy_compliant is False


# ============================================================================
# Cost Tracking Tests
# ============================================================================

class TestCostTracking:
    """Tests for cost tracking functionality"""

    @pytest.mark.unit
    def test_providers_include_cost(self, mock_env_vars):
        """Providers include cost per 1K tokens"""
        with patch.dict('os.environ', mock_env_vars):
            from backend.api.routers.admin_llm import list_llm_providers
            import asyncio

            response = asyncio.get_event_loop().run_until_complete(list_llm_providers())

            for provider in response.data:
                assert hasattr(provider, 'cost_per_1k_tokens')

    @pytest.mark.unit
    def test_usage_stats_include_costs(self):
        """Usage stats include cost breakdown"""
        from backend.api.routers.admin_llm import get_llm_usage_stats
        import asyncio

        response = asyncio.get_event_loop().run_until_complete(get_llm_usage_stats())

        assert "estimated_cost_usd" in response.data
        for provider_name, stats in response.data["by_provider"].items():
            assert "cost_usd" in stats


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestEdgeCases:
    """Edge cases and error handling tests"""

    @pytest.mark.unit
    def test_empty_environment(self):
        """Handles missing environment variables gracefully"""
        with patch.dict('os.environ', {}, clear=True):
            from backend.api.routers.admin_llm import list_llm_providers
            import asyncio

            # Should not raise exception
            response = asyncio.get_event_loop().run_until_complete(list_llm_providers())
            assert response.success is True

    @pytest.mark.unit
    def test_provider_names_case_sensitivity(self):
        """Provider names are case-sensitive"""
        from backend.api.routers.admin_llm import get_provider_config
        import asyncio

        with pytest.raises(HTTPException):
            asyncio.get_event_loop().run_until_complete(
                get_provider_config("OpenAI")  # Wrong case
            )

    @pytest.mark.unit
    def test_update_with_no_changes(self):
        """Update with empty data returns confirmation"""
        from backend.api.routers.admin_llm import update_provider_config, LLMProviderUpdate
        import asyncio

        update = LLMProviderUpdate()  # No changes
        response = asyncio.get_event_loop().run_until_complete(
            update_provider_config("openai", update)
        )

        assert response.success is True
        assert response.data["changes_applied"] == {}


# ============================================================================
# Integration Tests
# ============================================================================

class TestAdminLLMIntegration:
    """Integration tests for admin LLM configuration"""

    @pytest.mark.integration
    def test_full_provider_management_flow(self):
        """Complete flow: list -> get -> update -> test"""
        pass

    @pytest.mark.integration
    def test_metrics_consistency(self):
        """Metrics are consistent with actual usage"""
        pass

    @pytest.mark.integration
    def test_provider_switching(self):
        """Switching between providers works correctly"""
        pass