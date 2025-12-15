"""
Tests for Admin LLM Router

Verifies:
- GET /admin/llm/providers - List all LLM providers
- GET /admin/llm/providers/{name} - Get specific provider config
- PATCH /admin/llm/providers/{name} - Update provider config
- GET /admin/llm/usage/stats - Get usage statistics
- POST /admin/llm/test - Test LLM connection
- GET /admin/llm/metrics - Get system metrics
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import os

from backend.api.main import app


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    with TestClient(app) as test_client:
        yield test_client


# ============================================================================
# List Providers Tests
# ============================================================================

class TestListLLMProviders:
    """Tests for GET /admin/llm/providers"""

    def test_list_providers_success(self, client):
        """Test listing all LLM providers"""
        response = client.get("/api/v1/admin/llm/providers")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) >= 4  # mock, openai, gemini, anthropic

    def test_list_providers_includes_mock(self, client):
        """Test that mock provider is included"""
        response = client.get("/api/v1/admin/llm/providers")

        providers = response.json()["data"]
        mock_provider = next((p for p in providers if p["provider"] == "mock"), None)

        assert mock_provider is not None
        assert mock_provider["privacy_compliant"] is True
        assert mock_provider["cost_per_1k_tokens"] == 0.0

    def test_list_providers_includes_openai(self, client):
        """Test that OpenAI provider is included"""
        response = client.get("/api/v1/admin/llm/providers")

        providers = response.json()["data"]
        openai_provider = next((p for p in providers if p["provider"] == "openai"), None)

        assert openai_provider is not None
        assert "model" in openai_provider
        assert "temperature" in openai_provider

    def test_list_providers_includes_gemini(self, client):
        """Test that Gemini provider is included"""
        response = client.get("/api/v1/admin/llm/providers")

        providers = response.json()["data"]
        gemini_provider = next((p for p in providers if p["provider"] == "gemini"), None)

        assert gemini_provider is not None

    def test_list_providers_has_required_fields(self, client):
        """Test that each provider has required fields"""
        response = client.get("/api/v1/admin/llm/providers")

        for provider in response.json()["data"]:
            assert "provider" in provider
            assert "enabled" in provider
            assert "api_key_configured" in provider
            assert "privacy_compliant" in provider

    def test_list_providers_shows_limits(self, client):
        """Test that providers include usage limits"""
        response = client.get("/api/v1/admin/llm/providers")

        for provider in response.json()["data"]:
            if provider.get("limits"):
                assert "requests_per_day" in provider["limits"] or "tokens_per_month" in provider["limits"]

    def test_list_providers_message_includes_count(self, client):
        """Test response message includes provider count"""
        response = client.get("/api/v1/admin/llm/providers")

        message = response.json()["message"]
        assert "proveedores LLM" in message


# ============================================================================
# Get Provider Config Tests
# ============================================================================

class TestGetProviderConfig:
    """Tests for GET /admin/llm/providers/{provider_name}"""

    def test_get_mock_provider_success(self, client):
        """Test getting mock provider config"""
        response = client.get("/api/v1/admin/llm/providers/mock")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"]["provider"] == "mock"

    def test_get_openai_provider_success(self, client):
        """Test getting OpenAI provider config"""
        response = client.get("/api/v1/admin/llm/providers/openai")

        assert response.status_code == 200
        data = response.json()["data"]

        assert data["provider"] == "openai"
        assert "cost_per_1k_tokens" in data

    def test_get_nonexistent_provider(self, client):
        """Test getting non-existent provider returns 404"""
        response = client.get("/api/v1/admin/llm/providers/nonexistent")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_provider_includes_config_details(self, client):
        """Test that provider config includes detailed settings"""
        response = client.get("/api/v1/admin/llm/providers/openai")

        data = response.json()["data"]

        assert "model" in data
        assert "temperature" in data
        assert "max_tokens" in data


# ============================================================================
# Update Provider Config Tests
# ============================================================================

class TestUpdateProviderConfig:
    """Tests for PATCH /admin/llm/providers/{provider_name}"""

    def test_update_provider_success(self, client):
        """Test updating provider config"""
        response = client.patch(
            "/api/v1/admin/llm/providers/openai",
            json={
                "enabled": True,
                "model": "gpt-3.5-turbo",
                "temperature": 0.5
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "changes_applied" in data["data"]

    def test_update_provider_applies_changes(self, client):
        """Test that update returns applied changes"""
        response = client.patch(
            "/api/v1/admin/llm/providers/mock",
            json={
                "temperature": 0.8,
                "max_tokens": 1000
            }
        )

        changes = response.json()["data"]["changes_applied"]

        assert changes["temperature"] == 0.8
        assert changes["max_tokens"] == 1000

    def test_update_provider_includes_next_steps(self, client):
        """Test that update includes next steps"""
        response = client.patch(
            "/api/v1/admin/llm/providers/openai",
            json={"enabled": False}
        )

        data = response.json()["data"]
        assert "next_steps" in data
        assert len(data["next_steps"]) > 0

    def test_update_nonexistent_provider(self, client):
        """Test updating non-existent provider returns 404"""
        response = client.patch(
            "/api/v1/admin/llm/providers/invalid_provider",
            json={"enabled": True}
        )

        assert response.status_code == 404

    def test_update_provider_validates_temperature(self, client):
        """Test that temperature is validated"""
        response = client.patch(
            "/api/v1/admin/llm/providers/openai",
            json={"temperature": 3.0}  # Max is 2.0
        )

        assert response.status_code == 422

    def test_update_provider_validates_max_tokens(self, client):
        """Test that max_tokens is validated"""
        response = client.patch(
            "/api/v1/admin/llm/providers/openai",
            json={"max_tokens": -100}  # Must be > 0
        )

        assert response.status_code == 422

    def test_update_provider_partial_update(self, client):
        """Test partial update with single field"""
        response = client.patch(
            "/api/v1/admin/llm/providers/gemini",
            json={"daily_request_limit": 500}
        )

        assert response.status_code == 200
        changes = response.json()["data"]["changes_applied"]

        assert "daily_request_limit" in changes
        assert changes["daily_request_limit"] == 500


# ============================================================================
# Usage Stats Tests
# ============================================================================

class TestGetLLMUsageStats:
    """Tests for GET /admin/llm/usage/stats"""

    def test_get_usage_stats_success(self, client):
        """Test getting usage statistics"""
        response = client.get("/api/v1/admin/llm/usage/stats")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True

    def test_usage_stats_has_required_fields(self, client):
        """Test that usage stats has required fields"""
        response = client.get("/api/v1/admin/llm/usage/stats")

        stats = response.json()["data"]

        assert "total_requests" in stats
        assert "total_tokens" in stats
        assert "estimated_cost_usd" in stats
        assert "by_provider" in stats

    def test_usage_stats_includes_provider_breakdown(self, client):
        """Test that usage stats includes provider breakdown"""
        response = client.get("/api/v1/admin/llm/usage/stats")

        by_provider = response.json()["data"]["by_provider"]

        # Should have at least mock provider
        assert "mock" in by_provider
        assert "requests" in by_provider["mock"]
        assert "tokens" in by_provider["mock"]

    def test_usage_stats_includes_top_activities(self, client):
        """Test that usage stats includes top activities"""
        response = client.get("/api/v1/admin/llm/usage/stats")

        stats = response.json()["data"]
        assert "top_activities" in stats

        for activity in stats["top_activities"]:
            assert "activity_id" in activity
            assert "requests" in activity

    def test_usage_stats_includes_limits_status(self, client):
        """Test that usage stats includes limits status"""
        response = client.get("/api/v1/admin/llm/usage/stats")

        stats = response.json()["data"]
        assert "limits_status" in stats

        limits = stats["limits_status"]
        if "daily_limit" in limits:
            assert "used" in limits["daily_limit"]
            assert "limit" in limits["daily_limit"]


# ============================================================================
# Test LLM Connection Tests
# ============================================================================

class TestLLMConnection:
    """Tests for POST /admin/llm/test"""

    def test_test_connection_invalid_provider(self, client):
        """Test connection with invalid provider"""
        response = client.post("/api/v1/admin/llm/test?provider=invalid_provider")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is False
        assert data["data"]["status"] == "error"

    def test_test_connection_mock_provider(self, client):
        """Test connection with mock provider"""
        with patch('backend.api.routers.admin_llm.LLMProviderFactory') as mock_factory:
            mock_provider = AsyncMock()
            mock_provider.generate.return_value = "OK"
            mock_provider.model_name = "mock-model"
            mock_factory.create.return_value = mock_provider

            response = client.post("/api/v1/admin/llm/test?provider=mock")

            assert response.status_code == 200
            data = response.json()

            assert data["data"]["provider"] == "mock"

    def test_test_connection_reports_latency(self, client):
        """Test that connection test reports latency"""
        with patch('backend.api.routers.admin_llm.LLMProviderFactory') as mock_factory:
            mock_provider = AsyncMock()
            mock_provider.generate.return_value = "OK"
            mock_provider.model_name = "test-model"
            mock_factory.create.return_value = mock_provider

            response = client.post("/api/v1/admin/llm/test?provider=mock")

            if response.json()["success"]:
                assert "latency_ms" in response.json()["data"]

    def test_test_connection_with_specific_model(self, client):
        """Test connection with specific model parameter"""
        with patch('backend.api.routers.admin_llm.LLMProviderFactory') as mock_factory:
            mock_provider = AsyncMock()
            mock_provider.generate.return_value = "OK"
            mock_provider.model_name = "gpt-4"
            mock_factory.create.return_value = mock_provider

            response = client.post("/api/v1/admin/llm/test?provider=openai&model=gpt-4")

            assert response.status_code == 200

    def test_test_connection_handles_exception(self, client):
        """Test that connection errors are handled gracefully"""
        with patch('backend.api.routers.admin_llm.LLMProviderFactory') as mock_factory:
            mock_factory.create.side_effect = Exception("Connection failed")

            response = client.post("/api/v1/admin/llm/test?provider=openai")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is False
            assert data["data"]["status"] == "error"
            assert "error_type" in data["data"]


# ============================================================================
# System Metrics Tests
# ============================================================================

class TestGetSystemMetrics:
    """Tests for GET /admin/llm/metrics"""

    def test_get_metrics_success(self, client):
        """Test getting system metrics"""
        response = client.get("/api/v1/admin/llm/metrics")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True

    def test_metrics_has_required_fields(self, client):
        """Test that metrics has required fields"""
        response = client.get("/api/v1/admin/llm/metrics")

        metrics = response.json()["data"]

        assert "timestamp" in metrics
        assert "total_users" in metrics
        assert "active_sessions" in metrics
        assert "total_interactions" in metrics

    def test_metrics_includes_llm_usage(self, client):
        """Test that metrics includes LLM usage"""
        response = client.get("/api/v1/admin/llm/metrics")

        metrics = response.json()["data"]
        assert "llm_usage" in metrics

        for usage in metrics["llm_usage"]:
            assert "provider" in usage
            assert "total_requests" in usage
            assert "avg_response_time_ms" in usage

    def test_metrics_includes_service_status(self, client):
        """Test that metrics includes service status"""
        response = client.get("/api/v1/admin/llm/metrics")

        metrics = response.json()["data"]

        assert "database_status" in metrics
        assert "llm_status" in metrics

    def test_metrics_includes_storage_info(self, client):
        """Test that metrics includes storage info"""
        response = client.get("/api/v1/admin/llm/metrics")

        metrics = response.json()["data"]
        assert "storage_used_mb" in metrics

    def test_metrics_timestamp_format(self, client):
        """Test that timestamp is in valid format"""
        from datetime import datetime

        response = client.get("/api/v1/admin/llm/metrics")

        timestamp = response.json()["data"]["timestamp"]
        # Should parse as ISO format
        datetime.fromisoformat(timestamp)


# ============================================================================
# Environment-Based Tests
# ============================================================================

class TestEnvironmentConfiguration:
    """Tests for environment-based configuration"""

    def test_provider_enabled_based_on_env(self, client):
        """Test that provider enabled status reflects LLM_PROVIDER env"""
        current_provider = os.getenv("LLM_PROVIDER", "mock")

        response = client.get("/api/v1/admin/llm/providers")

        providers = response.json()["data"]
        for provider in providers:
            if provider["provider"] == current_provider:
                assert provider["enabled"] is True

    def test_api_key_configured_status(self, client):
        """Test that API key configured status is accurate"""
        response = client.get("/api/v1/admin/llm/providers")

        providers = response.json()["data"]

        # Mock should always have api_key_configured = True
        mock_provider = next(p for p in providers if p["provider"] == "mock")
        assert mock_provider["api_key_configured"] is True


# ============================================================================
# Integration Tests
# ============================================================================

class TestAdminLLMIntegration:
    """Integration tests for admin LLM endpoints"""

    def test_all_endpoints_follow_api_format(self, client):
        """Test that all endpoints follow consistent API format"""
        endpoints = [
            ("GET", "/api/v1/admin/llm/providers"),
            ("GET", "/api/v1/admin/llm/providers/mock"),
            ("GET", "/api/v1/admin/llm/usage/stats"),
            ("GET", "/api/v1/admin/llm/metrics"),
        ]

        for method, endpoint in endpoints:
            if method == "GET":
                response = client.get(endpoint)

            data = response.json()
            assert "success" in data
            assert "data" in data
            assert "message" in data

    def test_provider_workflow(self, client):
        """Test complete provider configuration workflow"""
        # 1. List providers
        list_response = client.get("/api/v1/admin/llm/providers")
        assert list_response.status_code == 200

        # 2. Get specific provider
        get_response = client.get("/api/v1/admin/llm/providers/openai")
        assert get_response.status_code == 200

        # 3. Update provider
        update_response = client.patch(
            "/api/v1/admin/llm/providers/openai",
            json={"temperature": 0.7}
        )
        assert update_response.status_code == 200

        # 4. Check usage stats
        stats_response = client.get("/api/v1/admin/llm/usage/stats")
        assert stats_response.status_code == 200

    def test_privacy_compliance_info(self, client):
        """Test that privacy compliance info is available"""
        response = client.get("/api/v1/admin/llm/providers")

        providers = response.json()["data"]

        # Mock should be privacy compliant
        mock = next(p for p in providers if p["provider"] == "mock")
        assert mock["privacy_compliant"] is True

        # Cloud providers should not be privacy compliant (data sent externally)
        openai = next(p for p in providers if p["provider"] == "openai")
        assert openai["privacy_compliant"] is False