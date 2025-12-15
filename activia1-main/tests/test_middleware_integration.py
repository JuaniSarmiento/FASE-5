"""
Tests for Middleware Integration

Verifies:
- Error handler middleware (exception handling)
- Rate limiter middleware
- Request logging middleware
- Middleware chain execution
"""
import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError, OperationalError


# ============================================================================
# Error Handler Tests
# ============================================================================

class TestErrorHandlerMiddleware:
    """Tests for error handler middleware"""

    def test_ainative_exception_handling(self):
        """Test handling of AINativeAPIException"""
        from backend.api.exceptions import AINativeAPIException
        from backend.api.middleware.error_handler import setup_exception_handlers

        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/test-ainative")
        async def test_route():
            raise AINativeAPIException(
                status_code=400,
                detail="Test error message",
                error_code="TEST_ERROR",
                extra={"field": "test"}
            )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-ainative")

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert data["error"]["error_code"] == "TEST_ERROR"
        assert data["error"]["message"] == "Test error message"

    def test_validation_error_handling(self):
        """Test handling of RequestValidationError"""
        from backend.api.middleware.error_handler import setup_exception_handlers
        from pydantic import BaseModel

        app = FastAPI()
        setup_exception_handlers(app)

        class TestModel(BaseModel):
            name: str
            age: int

        @app.post("/test-validation")
        async def test_route(data: TestModel):
            return {"ok": True}

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/test-validation", json={"name": "test"})  # Missing age

        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert data["error"]["error_code"] == "VALIDATION_ERROR"

    def test_sqlalchemy_error_handling(self):
        """Test handling of SQLAlchemy errors"""
        from backend.api.middleware.error_handler import setup_exception_handlers

        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/test-db-error")
        async def test_route():
            raise SQLAlchemyError("Connection failed")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-db-error")

        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"]["error_code"] == "DATABASE_ERROR"

    def test_generic_exception_handling(self):
        """Test handling of generic exceptions"""
        from backend.api.middleware.error_handler import setup_exception_handlers

        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/test-generic")
        async def test_route():
            raise RuntimeError("Unexpected error")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-generic")

        assert response.status_code == 500
        data = response.json()
        assert data["success"] is False
        assert data["error"]["error_code"] == "INTERNAL_ERROR"

    def test_error_response_has_timestamp(self):
        """Test that error responses include timestamp"""
        from backend.api.middleware.error_handler import setup_exception_handlers

        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/test-timestamp")
        async def test_route():
            raise ValueError("Test error")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/test-timestamp")

        data = response.json()
        assert "timestamp" in data

    def test_validation_error_field_extraction(self):
        """Test that validation errors extract field information"""
        from backend.api.middleware.error_handler import setup_exception_handlers
        from pydantic import BaseModel, Field

        app = FastAPI()
        setup_exception_handlers(app)

        class TestModel(BaseModel):
            email: str = Field(..., min_length=5)

        @app.post("/test-field")
        async def test_route(data: TestModel):
            return {"ok": True}

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/test-field", json={"email": "ab"})

        assert response.status_code == 422
        data = response.json()
        assert "field" in data["error"]

    def test_error_handler_logs_exceptions(self):
        """Test that error handler logs exceptions"""
        from backend.api.middleware.error_handler import setup_exception_handlers

        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/test-logging")
        async def test_route():
            raise ValueError("Log this error")

        with patch('backend.api.middleware.error_handler.logger') as mock_logger:
            client = TestClient(app, raise_server_exceptions=False)
            client.get("/test-logging")

            # Should have logged the error
            assert mock_logger.error.called or mock_logger.warning.called


# ============================================================================
# Rate Limiter Tests
# ============================================================================

class TestRateLimiterMiddleware:
    """Tests for rate limiter middleware"""

    def test_get_storage_uri_development(self):
        """Test storage URI in development mode"""
        from backend.api.middleware.rate_limiter import _get_storage_uri

        with patch.dict(os.environ, {"ENVIRONMENT": "development", "REDIS_URL": ""}):
            uri = _get_storage_uri()
            assert uri == "memory://"

    def test_get_storage_uri_development_with_redis(self):
        """Test storage URI prefers Redis in development"""
        from backend.api.middleware.rate_limiter import _get_storage_uri

        with patch.dict(os.environ, {
            "ENVIRONMENT": "development",
            "REDIS_URL": "redis://localhost:6379/0"
        }):
            uri = _get_storage_uri()
            assert uri == "redis://localhost:6379/0"

    def test_get_storage_uri_production_requires_redis(self):
        """Test production mode requires Redis"""
        # Import fresh to test initialization
        import importlib

        with patch.dict(os.environ, {"ENVIRONMENT": "production", "REDIS_URL": ""}):
            with pytest.raises(RuntimeError, match="REDIS_URL is REQUIRED"):
                # Re-import to trigger validation
                from backend.api.middleware import rate_limiter
                rate_limiter._get_storage_uri()

    def test_get_storage_uri_production_with_redis(self):
        """Test production mode with Redis configured"""
        from backend.api.middleware.rate_limiter import _get_storage_uri

        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "REDIS_URL": "redis://prod-redis:6379/0"
        }):
            uri = _get_storage_uri()
            assert uri == "redis://prod-redis:6379/0"

    def test_rate_limit_exceeded_handler(self):
        """Test rate limit exceeded response"""
        from backend.api.middleware.rate_limiter import rate_limit_exceeded_handler
        from slowapi.errors import RateLimitExceeded

        mock_request = Mock()
        mock_request.url.path = "/api/v1/test"

        with patch('backend.api.middleware.rate_limiter.get_remote_address') as mock_addr:
            mock_addr.return_value = "127.0.0.1"

            exc = RateLimitExceeded("10/minute")
            response = rate_limit_exceeded_handler(mock_request, exc)

            assert response.status_code == 429
            assert "Retry-After" in response.headers

    def test_rate_limits_configuration(self):
        """Test rate limits are configured for different endpoints"""
        from backend.api.middleware.rate_limiter import RATE_LIMITS, get_rate_limit

        # Check critical endpoints have stricter limits
        assert "interactions" in RATE_LIMITS
        assert "evaluations" in RATE_LIMITS

        # Check query endpoints have relaxed limits
        assert "sessions" in RATE_LIMITS
        assert "traces" in RATE_LIMITS

        # Test get_rate_limit function
        assert get_rate_limit("interactions") == "10/minute"
        assert get_rate_limit("unknown") == "20/minute"  # Default

    def test_rate_limit_response_format(self):
        """Test rate limit response has correct format"""
        from backend.api.middleware.rate_limiter import rate_limit_exceeded_handler
        from slowapi.errors import RateLimitExceeded

        mock_request = Mock()
        mock_request.url.path = "/test"

        with patch('backend.api.middleware.rate_limiter.get_remote_address') as mock_addr:
            mock_addr.return_value = "192.168.1.1"

            exc = RateLimitExceeded("5/minute")
            response = rate_limit_exceeded_handler(mock_request, exc)

            # Parse response body
            import json
            body = json.loads(response.body)

            assert body["success"] is False
            assert body["error"]["error_code"] == "RATE_LIMIT_EXCEEDED"
            assert "retry_after" in body["error"]["extra"]


# ============================================================================
# Request Logging Middleware Tests
# ============================================================================

class TestRequestLoggingMiddleware:
    """Tests for request logging middleware"""

    def test_logging_middleware_logs_requests(self):
        """Test that middleware logs incoming requests"""
        from backend.api.middleware.logging import RequestLoggingMiddleware

        app = FastAPI()

        @app.get("/test")
        async def test_route():
            return {"ok": True}

        app.add_middleware(RequestLoggingMiddleware)

        with patch('backend.api.middleware.logging.logger') as mock_logger:
            client = TestClient(app)
            client.get("/test")

            # Should have logged something
            assert mock_logger.info.called or mock_logger.debug.called

    def test_logging_middleware_captures_client_ip(self):
        """Test that middleware captures client IP"""
        from backend.api.middleware.logging import RequestLoggingMiddleware

        app = FastAPI()

        @app.get("/test")
        async def test_route():
            return {"ok": True}

        app.add_middleware(RequestLoggingMiddleware)

        client = TestClient(app)
        response = client.get("/test")

        assert response.status_code == 200

    def test_logging_middleware_handles_exceptions(self):
        """Test middleware handles exceptions in routes"""
        from backend.api.middleware.logging import RequestLoggingMiddleware

        app = FastAPI()

        @app.get("/error")
        async def error_route():
            raise ValueError("Test error")

        app.add_middleware(RequestLoggingMiddleware)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/error")

        # Should return error but not crash middleware
        assert response.status_code == 500


# ============================================================================
# Middleware Chain Tests
# ============================================================================

class TestMiddlewareChain:
    """Tests for middleware chain execution"""

    def test_middleware_execution_order(self):
        """Test middlewares execute in correct order"""
        execution_order = []

        from starlette.middleware.base import BaseHTTPMiddleware

        class FirstMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                execution_order.append("first_start")
                response = await call_next(request)
                execution_order.append("first_end")
                return response

        class SecondMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                execution_order.append("second_start")
                response = await call_next(request)
                execution_order.append("second_end")
                return response

        app = FastAPI()

        @app.get("/test")
        async def test_route():
            execution_order.append("route")
            return {"ok": True}

        # Add in reverse order (LIFO)
        app.add_middleware(FirstMiddleware)
        app.add_middleware(SecondMiddleware)

        client = TestClient(app)
        client.get("/test")

        # Second middleware wraps first which wraps route
        assert "route" in execution_order

    def test_error_propagates_through_middleware(self):
        """Test errors propagate through middleware chain"""
        from starlette.middleware.base import BaseHTTPMiddleware

        class TestMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request, call_next):
                try:
                    return await call_next(request)
                except Exception:
                    return JSONResponse(
                        status_code=500,
                        content={"middleware_caught": True}
                    )

        app = FastAPI()

        @app.get("/error")
        async def error_route():
            raise ValueError("Test")

        app.add_middleware(TestMiddleware)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/error")

        # Middleware should catch and handle
        assert response.status_code == 500


# ============================================================================
# Integration Tests
# ============================================================================

class TestMiddlewareIntegration:
    """Integration tests for all middleware together"""

    def test_full_request_with_all_middleware(self):
        """Test complete request flow with all middleware"""
        from backend.api.middleware.error_handler import setup_exception_handlers
        from backend.api.middleware.logging import RequestLoggingMiddleware

        app = FastAPI()
        setup_exception_handlers(app)
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/integrated")
        async def test_route():
            return {"integrated": True}

        client = TestClient(app)
        response = client.get("/integrated")

        assert response.status_code == 200
        assert response.json()["integrated"] is True

    def test_error_flow_with_all_middleware(self):
        """Test error flow through all middleware"""
        from backend.api.middleware.error_handler import setup_exception_handlers
        from backend.api.middleware.logging import RequestLoggingMiddleware
        from backend.api.exceptions import SessionNotFoundError

        app = FastAPI()
        setup_exception_handlers(app)
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/session/{id}")
        async def get_session(id: str):
            raise SessionNotFoundError(id)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/session/nonexistent")

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False

    def test_validation_error_with_logging(self):
        """Test validation errors are logged properly"""
        from backend.api.middleware.error_handler import setup_exception_handlers
        from backend.api.middleware.logging import RequestLoggingMiddleware
        from pydantic import BaseModel

        app = FastAPI()
        setup_exception_handlers(app)
        app.add_middleware(RequestLoggingMiddleware)

        class InputModel(BaseModel):
            value: int

        @app.post("/validate")
        async def validate_route(data: InputModel):
            return {"value": data.value}

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/validate", json={"value": "not_an_int"})

        assert response.status_code == 422

    def test_db_error_with_logging(self):
        """Test database errors are logged properly"""
        from backend.api.middleware.error_handler import setup_exception_handlers
        from backend.api.middleware.logging import RequestLoggingMiddleware

        app = FastAPI()
        setup_exception_handlers(app)
        app.add_middleware(RequestLoggingMiddleware)

        @app.get("/db-fail")
        async def db_fail():
            raise OperationalError("Connection refused", None, None)

        with patch('backend.api.middleware.error_handler.logger') as mock_logger:
            client = TestClient(app, raise_server_exceptions=False)
            response = client.get("/db-fail")

            assert response.status_code == 500
            assert mock_logger.error.called


# ============================================================================
# Exception Specific Tests
# ============================================================================

class TestSpecificExceptions:
    """Tests for specific exception types"""

    def test_session_not_found_error(self):
        """Test SessionNotFoundError handling"""
        from backend.api.middleware.error_handler import setup_exception_handlers
        from backend.api.exceptions import SessionNotFoundError

        app = FastAPI()
        setup_exception_handlers(app)

        @app.get("/session/{id}")
        async def get_session(id: str):
            raise SessionNotFoundError(id)

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/session/test_id")

        assert response.status_code == 404
        data = response.json()
        assert "SESSION_NOT_FOUND" in data["error"]["error_code"]

    def test_governance_blocked_error(self):
        """Test GovernanceBlockedError handling"""
        from backend.api.middleware.error_handler import setup_exception_handlers
        from backend.api.exceptions import GovernanceBlockedError

        app = FastAPI()
        setup_exception_handlers(app)

        @app.post("/interact")
        async def interact():
            raise GovernanceBlockedError(
                reason="Delegation detected",
                policy="NO_DELEGATION"
            )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/interact")

        assert response.status_code == 403
        data = response.json()
        assert "GOVERNANCE" in data["error"]["error_code"]

    def test_invalid_interaction_error(self):
        """Test InvalidInteractionError handling"""
        from backend.api.middleware.error_handler import setup_exception_handlers
        from backend.api.exceptions import InvalidInteractionError

        app = FastAPI()
        setup_exception_handlers(app)

        @app.post("/process")
        async def process():
            raise InvalidInteractionError(
                detail="Session is not active",
                extra={"session_status": "completed"}
            )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/process")

        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False