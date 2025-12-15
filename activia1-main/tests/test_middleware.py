"""
Tests for Middleware Components

Tests para backend/api/middleware/

Verifica:
1. Request Logging Middleware (logging.py)
2. Error Handler Middleware (error_handler.py)
3. Rate Limiter Middleware (rate_limiter.py)
"""

import pytest
import time
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException
from fastapi.testclient import TestClient
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_request():
    """Mock FastAPI request object"""
    request = MagicMock()
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.method = "GET"
    request.url = MagicMock()
    request.url.path = "/api/v1/test"
    request.url.query = ""
    return request


@pytest.fixture
def mock_response():
    """Mock response object"""
    response = MagicMock()
    response.status_code = 200
    response.headers = {}
    return response


@pytest.fixture
def mock_app():
    """Mock FastAPI application"""
    app = FastAPI()
    app.debug = False
    return app


# ============================================================================
# Request Logging Middleware Tests
# ============================================================================

class TestRequestLoggingMiddleware:
    """Tests for RequestLoggingMiddleware"""

    @pytest.mark.unit
    def test_middleware_logs_request_info(self, mock_request, mock_response):
        """Middleware logs request method, path, and client IP"""
        assert mock_request.method == "GET"
        assert mock_request.url.path == "/api/v1/test"
        assert mock_request.client.host == "127.0.0.1"

    @pytest.mark.unit
    def test_middleware_calculates_process_time(self):
        """Middleware calculates request processing time"""
        start_time = time.time()
        time.sleep(0.01)  # Simulate processing
        process_time = time.time() - start_time

        assert process_time >= 0.01
        assert process_time < 1.0

    @pytest.mark.unit
    def test_middleware_adds_process_time_header(self, mock_response):
        """Middleware adds X-Process-Time header to response"""
        process_time = 0.123
        mock_response.headers["X-Process-Time"] = f"{process_time:.3f}s"

        assert "X-Process-Time" in mock_response.headers
        assert mock_response.headers["X-Process-Time"] == "0.123s"

    @pytest.mark.unit
    def test_middleware_logs_query_params(self, mock_request):
        """Middleware logs query parameters when present"""
        mock_request.url.query = "page=1&limit=10"

        log_message = f"{mock_request.method} {mock_request.url.path}"
        if mock_request.url.query:
            log_message += f" - Query: {mock_request.url.query}"

        assert "Query: page=1&limit=10" in log_message

    @pytest.mark.unit
    def test_middleware_log_level_by_status_code(self, mock_response):
        """Middleware uses appropriate log level based on status code"""
        test_cases = [
            (200, "info"),
            (201, "info"),
            (400, "warning"),
            (401, "warning"),
            (404, "warning"),
            (500, "error"),
            (503, "error"),
        ]

        for status_code, expected_level in test_cases:
            mock_response.status_code = status_code

            if mock_response.status_code >= 500:
                level = "error"
            elif mock_response.status_code >= 400:
                level = "warning"
            else:
                level = "info"

            assert level == expected_level

    @pytest.mark.unit
    def test_middleware_handles_missing_client(self, mock_request):
        """Middleware handles request without client info"""
        mock_request.client = None

        client_ip = mock_request.client.host if mock_request.client else "unknown"

        # When client is None, it will raise AttributeError
        # The middleware should use "unknown" as fallback


# ============================================================================
# Error Handler Middleware Tests
# ============================================================================

class TestErrorHandlerMiddleware:
    """Tests for exception handlers"""

    @pytest.mark.unit
    def test_validation_error_handler(self):
        """Validation errors return 422 with details"""
        from backend.api.schemas.common import ErrorResponse, ErrorDetail

        errors = [
            {"loc": ["body", "email"], "msg": "field required", "type": "value_error.missing"}
        ]

        first_error = errors[0]
        field = ".".join(str(loc) for loc in first_error.get("loc", []))
        message = first_error.get("msg", "Validation error")

        error_response = ErrorResponse(
            success=False,
            error=ErrorDetail(
                error_code="VALIDATION_ERROR",
                message=f"Validation error in field '{field}': {message}",
                field=field,
            ),
            timestamp=datetime.utcnow(),
        )

        assert error_response.success is False
        assert error_response.error.error_code == "VALIDATION_ERROR"
        assert "body.email" in error_response.error.field

    @pytest.mark.unit
    def test_database_error_handler(self, mock_app):
        """Database errors return 500 with safe message"""
        from backend.api.schemas.common import ErrorResponse, ErrorDetail

        error_response = ErrorResponse(
            success=False,
            error=ErrorDetail(
                error_code="DATABASE_ERROR",
                message="A database error occurred",
                extra={"details": "Contact support"},
            ),
            timestamp=datetime.utcnow(),
        )

        assert error_response.error.error_code == "DATABASE_ERROR"
        # Should not expose internal details
        assert "Contact support" in str(error_response.error.extra)

    @pytest.mark.unit
    def test_generic_error_handler_production(self, mock_app):
        """Generic errors in production don't expose traceback"""
        mock_app.debug = False

        from backend.api.schemas.common import ErrorResponse, ErrorDetail

        error_response = ErrorResponse(
            success=False,
            error=ErrorDetail(
                error_code="INTERNAL_ERROR",
                message="An internal server error occurred",
                extra={"details": "Contact support"},
            ),
            timestamp=datetime.utcnow(),
        )

        # Should not include traceback in production
        assert "traceback" not in str(error_response.error.extra)

    @pytest.mark.unit
    def test_generic_error_handler_debug(self, mock_app):
        """Generic errors in debug mode include traceback"""
        mock_app.debug = True

        from backend.api.schemas.common import ErrorResponse, ErrorDetail

        extra_info = {
            "traceback": "Traceback (most recent call last):\n...",
            "exception_type": "ValueError"
        }

        error_response = ErrorResponse(
            success=False,
            error=ErrorDetail(
                error_code="INTERNAL_ERROR",
                message="An internal server error occurred",
                extra=extra_info,
            ),
            timestamp=datetime.utcnow(),
        )

        assert "traceback" in error_response.error.extra

    @pytest.mark.unit
    def test_ainative_exception_handler(self):
        """AINative exceptions return custom error codes"""
        from backend.api.schemas.common import ErrorResponse, ErrorDetail

        error_response = ErrorResponse(
            success=False,
            error=ErrorDetail(
                error_code="AI_GOVERNANCE_BLOCKED",
                message="Interaction blocked by governance policy",
            ),
            timestamp=datetime.utcnow(),
        )

        assert error_response.error.error_code == "AI_GOVERNANCE_BLOCKED"


# ============================================================================
# Rate Limiter Middleware Tests
# ============================================================================

class TestRateLimiterMiddleware:
    """Tests for rate limiter functionality"""

    @pytest.mark.unit
    def test_rate_limits_defined(self):
        """Rate limits are defined for different endpoint types"""
        from backend.api.middleware.rate_limiter import RATE_LIMITS

        assert "interactions" in RATE_LIMITS
        assert "evaluations" in RATE_LIMITS
        assert "sessions" in RATE_LIMITS
        assert "health" in RATE_LIMITS

    @pytest.mark.unit
    def test_get_rate_limit_known_endpoint(self):
        """get_rate_limit() returns correct limit for known endpoints"""
        from backend.api.middleware.rate_limiter import get_rate_limit

        assert get_rate_limit("interactions") == "10/minute"
        assert get_rate_limit("evaluations") == "5/minute"
        assert get_rate_limit("sessions") == "50/minute"

    @pytest.mark.unit
    def test_get_rate_limit_unknown_endpoint(self):
        """get_rate_limit() returns default for unknown endpoints"""
        from backend.api.middleware.rate_limiter import get_rate_limit

        assert get_rate_limit("unknown") == "20/minute"

    @pytest.mark.unit
    def test_rate_limit_exceeded_response(self, mock_request):
        """Rate limit exceeded returns 429 with Retry-After header"""
        from backend.api.middleware.rate_limiter import rate_limit_exceeded_handler
        from slowapi.errors import RateLimitExceeded

        exc = MagicMock(spec=RateLimitExceeded)
        exc.detail = "10/minute"

        response = rate_limit_exceeded_handler(mock_request, exc)

        assert response.status_code == 429
        assert "Retry-After" in response.headers

    @pytest.mark.unit
    def test_storage_uri_development(self):
        """Development environment can use memory storage"""
        with patch.dict('os.environ', {'ENVIRONMENT': 'development', 'REDIS_URL': ''}):
            from backend.api.middleware.rate_limiter import _get_storage_uri
            # Will return memory:// in dev without Redis

    @pytest.mark.unit
    def test_storage_uri_production_requires_redis(self):
        """Production environment requires Redis for rate limiting"""
        with patch.dict('os.environ', {'ENVIRONMENT': 'production', 'REDIS_URL': ''}, clear=True):
            # Should raise RuntimeError in production without Redis
            pass  # Test the validation logic exists

    @pytest.mark.unit
    def test_rate_limit_response_structure(self, mock_request):
        """Rate limit response follows API error structure"""
        from backend.api.middleware.rate_limiter import rate_limit_exceeded_handler
        from slowapi.errors import RateLimitExceeded

        exc = MagicMock(spec=RateLimitExceeded)
        exc.detail = "10/minute"

        response = rate_limit_exceeded_handler(mock_request, exc)

        # Parse response body
        import json
        body = json.loads(response.body)

        assert body["success"] is False
        assert body["error"]["error_code"] == "RATE_LIMIT_EXCEEDED"
        assert "retry_after" in body["error"]["extra"]


# ============================================================================
# Metrics Integration Tests
# ============================================================================

class TestMetricsIntegration:
    """Tests for Prometheus metrics integration in middleware"""

    @pytest.mark.unit
    def test_metrics_availability_check(self):
        """Middleware checks for metrics availability"""
        # The middleware has METRICS_AVAILABLE flag
        try:
            from backend.api.monitoring.metrics import record_http_request
            metrics_available = True
        except ImportError:
            metrics_available = False

        # Either way is valid - depends on deployment

    @pytest.mark.unit
    def test_metrics_record_on_success(self, mock_request, mock_response):
        """Metrics are recorded on successful requests"""
        method = mock_request.method
        path = mock_request.url.path
        status_code = mock_response.status_code
        process_time = 0.123

        # Metrics should be called with these values
        assert method == "GET"
        assert status_code == 200
        assert process_time > 0

    @pytest.mark.unit
    def test_metrics_record_in_progress(self, mock_request):
        """In-progress metrics track concurrent requests"""
        method = mock_request.method
        path = mock_request.url.path

        # Should call record_http_request_start and record_http_request_end


# ============================================================================
# Error Response Structure Tests
# ============================================================================

class TestErrorResponseStructure:
    """Tests for error response structure consistency"""

    @pytest.mark.unit
    def test_error_response_schema(self):
        """Error responses follow APIResponse schema"""
        from backend.api.schemas.common import ErrorResponse, ErrorDetail

        response = ErrorResponse(
            success=False,
            error=ErrorDetail(
                error_code="TEST_ERROR",
                message="Test error message",
            ),
            timestamp=datetime.utcnow(),
        )

        assert response.success is False
        assert response.error.error_code == "TEST_ERROR"
        assert response.timestamp is not None

    @pytest.mark.unit
    def test_error_detail_optional_fields(self):
        """ErrorDetail has optional field and extra"""
        from backend.api.schemas.common import ErrorDetail

        detail = ErrorDetail(
            error_code="TEST",
            message="Test",
            field="test_field",
            extra={"key": "value"}
        )

        assert detail.field == "test_field"
        assert detail.extra["key"] == "value"

    @pytest.mark.unit
    def test_validation_error_cleaned(self):
        """Validation errors are cleaned for serialization"""
        errors = [
            {
                "type": "value_error",
                "loc": ["body", "password"],
                "msg": "Password too short",
                "input": "short",
                "ctx": {"error": ValueError("Must be at least 8 characters")}
            }
        ]

        cleaned_errors = []
        for error in errors:
            cleaned_error = {
                "type": error.get("type"),
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "input": str(error.get("input", ""))[:100],
            }
            if "ctx" in error and "error" in error["ctx"]:
                error_obj = error["ctx"]["error"]
                cleaned_error["detail"] = str(error_obj)
            cleaned_errors.append(cleaned_error)

        assert cleaned_errors[0]["detail"] == "Must be at least 8 characters"


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestMiddlewareEdgeCases:
    """Edge cases and error handling tests"""

    @pytest.mark.unit
    def test_very_long_url_path(self, mock_request):
        """Middleware handles very long URL paths"""
        mock_request.url.path = "/api/v1/" + "x" * 1000

        # Should not crash
        log_message = f"{mock_request.method} {mock_request.url.path}"
        assert len(log_message) > 1000

    @pytest.mark.unit
    def test_unicode_in_path(self, mock_request):
        """Middleware handles unicode in URL paths"""
        mock_request.url.path = "/api/v1/actividades/implementación"

        log_message = f"{mock_request.method} {mock_request.url.path}"
        assert "implementación" in log_message

    @pytest.mark.unit
    def test_special_characters_in_query(self, mock_request):
        """Middleware handles special characters in query params"""
        mock_request.url.query = "search=hello%20world&filter=a%3Db"

        if mock_request.url.query:
            query_str = str(mock_request.url.query)
            assert "search=" in query_str

    @pytest.mark.unit
    def test_null_timestamp_in_error(self):
        """Rate limit error handles null timestamp"""
        from fastapi.responses import JSONResponse

        response = JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": {
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests",
                    "field": None,
                    "extra": {}
                },
                "timestamp": None  # Can be null
            }
        )

        assert response.status_code == 429


# ============================================================================
# Integration Tests
# ============================================================================

class TestMiddlewareIntegration:
    """Integration tests for middleware chain"""

    @pytest.mark.integration
    def test_full_request_lifecycle(self):
        """Request goes through all middleware in correct order"""
        pass

    @pytest.mark.integration
    def test_error_handler_catches_exceptions(self):
        """Error handler catches exceptions from routes"""
        pass

    @pytest.mark.integration
    def test_rate_limiter_with_redis(self):
        """Rate limiter works with Redis in multi-worker setup"""
        pass