"""
Tests for Health Router

Verifies:
- GET /health - Main health check
- GET /health/ping - Simple ping
- GET /health/live - Kubernetes liveness probe
- GET /health/ready - Kubernetes readiness probe
- GET /health/deep - Deep health check with metrics
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import OperationalError
from datetime import datetime

from backend.api.main import app
from backend.database.models import Base
from backend.api.deps import get_db


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with test database"""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ============================================================================
# Main Health Check Tests
# ============================================================================

class TestHealthCheck:
    """Tests for GET /health endpoint"""

    def test_health_check_success(self, client):
        """Test successful health check"""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "database" in data
        assert "agents" in data
        assert "timestamp" in data

    def test_health_check_returns_healthy_status(self, client):
        """Test health check returns healthy when DB is connected"""
        response = client.get("/api/v1/health")

        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"

    def test_health_check_shows_all_agents(self, client):
        """Test that health check shows all 6 AI agents"""
        response = client.get("/api/v1/health")

        agents = response.json()["agents"]

        expected_agents = [
            "T-IA-Cog",
            "E-IA-Proc",
            "S-IA-X",
            "AR-IA",
            "GOV-IA",
            "TC-N4"
        ]

        for agent in expected_agents:
            assert agent in agents
            assert agents[agent] == "operational"

    def test_health_check_includes_version(self, client):
        """Test that health check includes version"""
        response = client.get("/api/v1/health")

        data = response.json()
        assert "version" in data

    def test_health_check_includes_timestamp(self, client):
        """Test that health check includes timestamp"""
        response = client.get("/api/v1/health")

        data = response.json()
        assert "timestamp" in data
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))


class TestHealthCheckDatabaseFailure:
    """Tests for health check when database fails"""

    def test_health_check_db_disconnected(self):
        """Test health check when database is disconnected"""
        # Create mock DB that raises OperationalError
        mock_db = Mock()
        mock_db.execute = Mock(side_effect=OperationalError("Connection refused", None, None))

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as test_client:
            response = test_client.get("/api/v1/health")

            assert response.status_code == 200
            data = response.json()

            # Should still return but with unhealthy status
            assert data["database"] == "disconnected"
            assert data["status"] in ["unhealthy", "degraded"]

        app.dependency_overrides.clear()


# ============================================================================
# Ping Tests
# ============================================================================

class TestPing:
    """Tests for GET /health/ping endpoint"""

    def test_ping_success(self, client):
        """Test simple ping returns ok"""
        response = client.get("/api/v1/health/ping")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ok"
        assert "timestamp" in data

    def test_ping_fast_response(self, client):
        """Test that ping responds quickly"""
        import time

        start = time.time()
        response = client.get("/api/v1/health/ping")
        elapsed = time.time() - start

        assert response.status_code == 200
        # Ping should respond in under 100ms
        assert elapsed < 0.1


# ============================================================================
# Liveness Probe Tests
# ============================================================================

class TestLivenessProbe:
    """Tests for GET /health/live endpoint (Kubernetes liveness probe)"""

    def test_liveness_probe_returns_200(self, client):
        """Test liveness probe returns 200 when process is alive"""
        response = client.get("/api/v1/health/live")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "alive"
        assert "timestamp" in data

    def test_liveness_probe_no_db_dependency(self):
        """Test that liveness probe doesn't depend on database"""
        # Even without DB override, liveness should work
        with TestClient(app) as test_client:
            response = test_client.get("/api/v1/health/live")
            assert response.status_code == 200


# ============================================================================
# Readiness Probe Tests
# ============================================================================

class TestReadinessProbe:
    """Tests for GET /health/ready endpoint (Kubernetes readiness probe)"""

    def test_readiness_probe_success(self, client):
        """Test readiness probe with healthy database"""
        response = client.get("/api/v1/health/ready")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "ready"
        assert "checks" in data
        assert "database" in data["checks"]
        assert data["checks"]["database"]["status"] == "ready"

    def test_readiness_probe_includes_latency(self, client):
        """Test that readiness probe includes database latency"""
        response = client.get("/api/v1/health/ready")

        data = response.json()
        assert "latency_ms" in data["checks"]["database"]

    def test_readiness_probe_includes_redis_check(self, client):
        """Test that readiness probe includes Redis check"""
        response = client.get("/api/v1/health/ready")

        data = response.json()
        assert "redis" in data["checks"]
        # Redis may be not_configured in test environment
        assert data["checks"]["redis"]["status"] in [
            "ready", "not_configured", "not_ready"
        ]

    def test_readiness_probe_includes_llm_check(self, client):
        """Test that readiness probe includes LLM provider check"""
        response = client.get("/api/v1/health/ready")

        data = response.json()
        assert "llm_provider" in data["checks"]

    def test_readiness_probe_db_failure_returns_503(self):
        """Test readiness returns 503 when database fails"""
        mock_db = Mock()
        mock_db.execute = Mock(side_effect=Exception("DB Connection failed"))

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as test_client:
            response = test_client.get("/api/v1/health/ready")

            assert response.status_code == 503
            data = response.json()

            assert data["status"] == "not_ready"
            assert data["checks"]["database"]["status"] == "not_ready"

        app.dependency_overrides.clear()


# ============================================================================
# Deep Health Check Tests
# ============================================================================

class TestDeepHealthCheck:
    """Tests for GET /health/deep endpoint"""

    def test_deep_health_check_success(self, client):
        """Test deep health check returns comprehensive data"""
        response = client.get("/api/v1/health/deep")

        assert response.status_code in [200, 503]
        data = response.json()

        assert "status" in data
        assert "checks" in data
        assert "timestamp" in data

    def test_deep_health_check_includes_system_info(self, client):
        """Test that deep check includes system information"""
        response = client.get("/api/v1/health/deep")

        data = response.json()
        assert "system" in data["checks"]

        system = data["checks"]["system"]
        assert "version" in system
        assert "python_version" in system
        assert "platform" in system
        assert "environment" in system

    def test_deep_health_check_includes_database_details(self, client):
        """Test that deep check includes database details"""
        response = client.get("/api/v1/health/deep")

        data = response.json()
        assert "database" in data["checks"]

        db_check = data["checks"]["database"]
        assert "status" in db_check
        assert "latency_ms" in db_check

    def test_deep_health_check_includes_process_info(self, client):
        """Test that deep check includes process information"""
        response = client.get("/api/v1/health/deep")

        data = response.json()
        assert "process" in data["checks"]

        process = data["checks"]["process"]
        assert "pid" in process
        assert "gc_stats" in process

    def test_deep_health_check_includes_cache_info(self, client):
        """Test that deep check includes cache information"""
        response = client.get("/api/v1/health/deep")

        data = response.json()
        assert "cache" in data["checks"]

    def test_deep_health_check_includes_llm_provider(self, client):
        """Test that deep check includes LLM provider info"""
        response = client.get("/api/v1/health/deep")

        data = response.json()
        assert "llm_provider" in data["checks"]

        llm = data["checks"]["llm_provider"]
        assert "provider" in llm
        assert "status" in llm

    def test_deep_health_check_db_version(self, client):
        """Test that deep check shows database version"""
        response = client.get("/api/v1/health/deep")

        data = response.json()
        db_check = data["checks"]["database"]

        # Should have version info
        assert "version" in db_check

    def test_deep_health_check_redis_write_read_test(self, client):
        """Test that deep check includes Redis write/read test"""
        response = client.get("/api/v1/health/deep")

        data = response.json()

        # Redis may be not configured in test, but key should exist
        assert "redis" in data["checks"]

    def test_deep_health_check_gc_stats(self, client):
        """Test that deep check includes garbage collector stats"""
        response = client.get("/api/v1/health/deep")

        data = response.json()
        gc_stats = data["checks"]["process"].get("gc_stats", {})

        # GC stats should include generation counts
        if gc_stats:
            assert "generation_0" in gc_stats or "total_objects" in gc_stats


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestHealthErrorHandling:
    """Tests for health endpoint error handling"""

    def test_health_handles_db_programming_error(self):
        """Test health handles ProgrammingError gracefully"""
        from sqlalchemy.exc import ProgrammingError

        mock_db = Mock()
        mock_db.execute = Mock(side_effect=ProgrammingError("SQL Error", None, None))

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as test_client:
            response = test_client.get("/api/v1/health")

            # Should not raise 500
            assert response.status_code == 200
            assert response.json()["database"] == "disconnected"

        app.dependency_overrides.clear()

    def test_health_handles_unexpected_exception(self):
        """Test health handles unexpected exceptions gracefully"""
        mock_db = Mock()
        mock_db.execute = Mock(side_effect=RuntimeError("Unexpected error"))

        def override_get_db():
            yield mock_db

        app.dependency_overrides[get_db] = override_get_db

        with TestClient(app) as test_client:
            response = test_client.get("/api/v1/health")

            # Should handle gracefully
            assert response.status_code == 200
            assert response.json()["database"] == "disconnected"

        app.dependency_overrides.clear()


# ============================================================================
# Performance Tests
# ============================================================================

class TestHealthPerformance:
    """Tests for health endpoint performance"""

    def test_ping_is_fastest(self, client):
        """Test that /ping is faster than other health endpoints"""
        import time

        # Warm up
        client.get("/api/v1/health/ping")

        # Measure ping
        start = time.time()
        for _ in range(10):
            client.get("/api/v1/health/ping")
        ping_avg = (time.time() - start) / 10

        # Measure live
        start = time.time()
        for _ in range(10):
            client.get("/api/v1/health/live")
        live_avg = (time.time() - start) / 10

        # Both should be fast (under 50ms average)
        assert ping_avg < 0.05
        assert live_avg < 0.05

    def test_deep_check_slower_than_ready(self, client):
        """Test that /deep is slower than /ready (more checks)"""
        import time

        # Measure ready
        start = time.time()
        client.get("/api/v1/health/ready")
        ready_time = time.time() - start

        # Measure deep
        start = time.time()
        client.get("/api/v1/health/deep")
        deep_time = time.time() - start

        # Deep should take longer or similar (not 10x faster)
        # This is a sanity check that deep is doing more work
        assert deep_time >= ready_time * 0.5  # Allow some variance


# ============================================================================
# Integration Tests
# ============================================================================

class TestHealthIntegration:
    """Integration tests for health endpoints"""

    def test_all_health_endpoints_respond(self, client):
        """Test that all health endpoints respond"""
        endpoints = [
            "/api/v1/health",
            "/api/v1/health/ping",
            "/api/v1/health/live",
            "/api/v1/health/ready",
            "/api/v1/health/deep",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 503], f"Failed for {endpoint}"

    def test_health_response_format_consistency(self, client):
        """Test that health endpoints have consistent response format"""
        # Main health
        health_resp = client.get("/api/v1/health")
        assert "status" in health_resp.json()

        # Ready
        ready_resp = client.get("/api/v1/health/ready")
        assert "status" in ready_resp.json()

        # Deep
        deep_resp = client.get("/api/v1/health/deep")
        assert "status" in deep_resp.json()

    def test_kubernetes_probe_compatibility(self, client):
        """Test endpoints are compatible with Kubernetes probes"""
        # Liveness - must return 200 for healthy
        live = client.get("/api/v1/health/live")
        assert live.status_code == 200

        # Readiness - must return 200 or 503
        ready = client.get("/api/v1/health/ready")
        assert ready.status_code in [200, 503]

        # Both should have JSON response
        assert live.headers["content-type"].startswith("application/json")
        assert ready.headers["content-type"].startswith("application/json")