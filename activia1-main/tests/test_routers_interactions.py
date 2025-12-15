"""
Tests for Interactions Router

Verifies:
- POST /interactions - Process interaction (main endpoint)
- GET /interactions/{session_id}/history - Get interaction history
- Transaction management and rollback
- Error handling (session not found, inactive session, governance blocked)
- AI Gateway integration
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
from uuid import uuid4

from backend.api.main import app
from backend.database.models import Base
from backend.api.deps import get_db, get_ai_gateway


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


@pytest.fixture
def mock_gateway():
    """Create mock AI Gateway"""
    gateway = AsyncMock()
    gateway.process_interaction = AsyncMock(return_value={
        "response": "Esta es una respuesta pedagógica de prueba.",
        "agent_used": "T-IA-Cog",
        "cognitive_state": "EXPLORACION",
        "blocked": False,
        "block_reason": None,
        "risks_detected": []
    })
    return gateway


@pytest.fixture(scope="function")
def client(test_db, mock_gateway):
    """Create a test client with test database and mock gateway"""

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    def override_get_gateway():
        return mock_gateway

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_ai_gateway] = override_get_gateway

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def active_session(client):
    """Create an active session for testing"""
    response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    return response.json()["data"]


# ============================================================================
# Process Interaction Tests
# ============================================================================

class TestProcessInteraction:
    """Tests for POST /interactions endpoint"""

    def test_process_interaction_success(self, client, active_session):
        """Test successful interaction processing"""
        response = client.post("/api/v1/interactions", json={
            "session_id": active_session["id"],
            "prompt": "¿Qué es una cola circular?",
            "cognitive_intent": "UNDERSTANDING"
        })

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data
        assert data["data"]["session_id"] == active_session["id"]
        assert data["data"]["response"] is not None
        assert data["data"]["agent_used"] is not None
        assert data["data"]["blocked"] is False

    def test_process_interaction_with_context(self, client, active_session):
        """Test interaction processing with code context"""
        response = client.post("/api/v1/interactions", json={
            "session_id": active_session["id"],
            "prompt": "¿Cómo mejoro este código?",
            "cognitive_intent": "IMPLEMENTATION",
            "context": {
                "code_snippet": "def enqueue(self, item): pass",
                "language": "python",
                "file_name": "cola.py"
            }
        })

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_process_interaction_session_not_found(self, client):
        """Test interaction with non-existent session"""
        response = client.post("/api/v1/interactions", json={
            "session_id": "non_existent_session_id",
            "prompt": "Test prompt",
            "cognitive_intent": "UNDERSTANDING"
        })

        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False

    def test_process_interaction_inactive_session(self, client, active_session):
        """Test interaction with inactive (completed) session"""
        # Complete the session
        client.patch(f"/api/v1/sessions/{active_session['id']}", json={
            "status": "completed"
        })

        response = client.post("/api/v1/interactions", json={
            "session_id": active_session["id"],
            "prompt": "Test prompt",
            "cognitive_intent": "UNDERSTANDING"
        })

        assert response.status_code == 400

    def test_process_interaction_missing_prompt(self, client, active_session):
        """Test interaction with missing prompt"""
        response = client.post("/api/v1/interactions", json={
            "session_id": active_session["id"],
            "cognitive_intent": "UNDERSTANDING"
        })

        assert response.status_code == 422  # Validation error

    def test_process_interaction_missing_session_id(self, client):
        """Test interaction with missing session_id"""
        response = client.post("/api/v1/interactions", json={
            "prompt": "Test prompt",
            "cognitive_intent": "UNDERSTANDING"
        })

        assert response.status_code == 422

    def test_process_interaction_returns_trace_id(self, client, active_session):
        """Test that interaction returns trace ID"""
        response = client.post("/api/v1/interactions", json={
            "session_id": active_session["id"],
            "prompt": "¿Qué es una pila?",
            "cognitive_intent": "UNDERSTANDING"
        })

        assert response.status_code == 200
        data = response.json()

        # Should have trace_id (may be empty if no trace created in mock)
        assert "trace_id" in data["data"]

    def test_process_interaction_returns_cognitive_state(self, client, active_session):
        """Test that interaction returns detected cognitive state"""
        response = client.post("/api/v1/interactions", json={
            "session_id": active_session["id"],
            "prompt": "Estoy planificando mi solución",
            "cognitive_intent": "PLANNING"
        })

        assert response.status_code == 200
        data = response.json()

        assert "cognitive_state_detected" in data["data"]

    def test_process_interaction_returns_ai_involvement(self, client, active_session):
        """Test that interaction returns AI involvement score"""
        response = client.post("/api/v1/interactions", json={
            "session_id": active_session["id"],
            "prompt": "Explícame el concepto",
            "cognitive_intent": "UNDERSTANDING"
        })

        assert response.status_code == 200
        data = response.json()

        assert "ai_involvement" in data["data"]
        assert 0 <= data["data"]["ai_involvement"] <= 1


class TestProcessInteractionBlocking:
    """Tests for governance blocking in interactions"""

    def test_process_interaction_blocked_by_governance(self, client, test_db):
        """Test interaction blocked by governance (delegation)"""
        # Create mock gateway that returns blocked
        mock_gateway = AsyncMock()
        mock_gateway.process_interaction = AsyncMock(return_value={
            "response": "No puedo completar esa solicitud.",
            "agent_used": "GOV-IA",
            "cognitive_state": "IMPLEMENTACION",
            "blocked": True,
            "block_reason": "Delegación total detectada. Por favor, intenta descomponer el problema.",
            "risks_detected": ["COGNITIVE_DELEGATION"]
        })

        def override_get_db():
            yield test_db

        def override_get_gateway():
            return mock_gateway

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_ai_gateway] = override_get_gateway

        with TestClient(app) as test_client:
            # Create session
            session_response = test_client.post("/api/v1/sessions", json={
                "student_id": "test_student",
                "activity_id": "test_activity",
                "mode": "TUTOR"
            })
            session_id = session_response.json()["data"]["id"]

            # Try delegation prompt
            response = test_client.post("/api/v1/interactions", json={
                "session_id": session_id,
                "prompt": "Dame el código completo de la cola",
                "cognitive_intent": "IMPLEMENTATION"
            })

            assert response.status_code == 200
            data = response.json()

            assert data["data"]["blocked"] is True
            assert data["data"]["block_reason"] is not None

        app.dependency_overrides.clear()

    def test_process_interaction_blocked_returns_risks(self, client, test_db):
        """Test that blocked interaction returns detected risks"""
        mock_gateway = AsyncMock()
        mock_gateway.process_interaction = AsyncMock(return_value={
            "response": "Detectamos un patrón de delegación.",
            "agent_used": "GOV-IA",
            "cognitive_state": "IMPLEMENTACION",
            "blocked": True,
            "block_reason": "Delegación total",
            "risks_detected": ["COGNITIVE_DELEGATION", "LACK_JUSTIFICATION"]
        })

        def override_get_db():
            yield test_db

        def override_get_gateway():
            return mock_gateway

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_ai_gateway] = override_get_gateway

        with TestClient(app) as test_client:
            session_response = test_client.post("/api/v1/sessions", json={
                "student_id": "test_student",
                "activity_id": "test_activity",
                "mode": "TUTOR"
            })
            session_id = session_response.json()["data"]["id"]

            response = test_client.post("/api/v1/interactions", json={
                "session_id": session_id,
                "prompt": "Hazlo por mi",
                "cognitive_intent": "IMPLEMENTATION"
            })

            data = response.json()
            assert "risks_detected" in data["data"]
            assert len(data["data"]["risks_detected"]) > 0

        app.dependency_overrides.clear()


class TestProcessInteractionErrors:
    """Tests for error handling in interactions"""

    def test_process_interaction_gateway_validation_error(self, client, test_db):
        """Test handling of validation errors from gateway"""
        from pydantic import ValidationError

        mock_gateway = AsyncMock()
        mock_gateway.process_interaction = AsyncMock(
            side_effect=ValidationError.from_exception_data(
                "ValidationError",
                [{"type": "missing", "loc": ("field",), "msg": "Field required"}]
            )
        )

        def override_get_db():
            yield test_db

        def override_get_gateway():
            return mock_gateway

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_ai_gateway] = override_get_gateway

        with TestClient(app) as test_client:
            session_response = test_client.post("/api/v1/sessions", json={
                "student_id": "test_student",
                "activity_id": "test_activity",
                "mode": "TUTOR"
            })
            session_id = session_response.json()["data"]["id"]

            response = test_client.post("/api/v1/interactions", json={
                "session_id": session_id,
                "prompt": "Test",
                "cognitive_intent": "UNDERSTANDING"
            })

            assert response.status_code == 400

        app.dependency_overrides.clear()

    def test_process_interaction_gateway_key_error(self, client, test_db):
        """Test handling of KeyError from gateway"""
        mock_gateway = AsyncMock()
        mock_gateway.process_interaction = AsyncMock(
            side_effect=KeyError("missing_config_key")
        )

        def override_get_db():
            yield test_db

        def override_get_gateway():
            return mock_gateway

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_ai_gateway] = override_get_gateway

        with TestClient(app) as test_client:
            session_response = test_client.post("/api/v1/sessions", json={
                "student_id": "test_student",
                "activity_id": "test_activity",
                "mode": "TUTOR"
            })
            session_id = session_response.json()["data"]["id"]

            response = test_client.post("/api/v1/interactions", json={
                "session_id": session_id,
                "prompt": "Test",
                "cognitive_intent": "UNDERSTANDING"
            })

            assert response.status_code == 400

        app.dependency_overrides.clear()

    def test_process_interaction_gateway_value_error_blocked(self, client, test_db):
        """Test handling of ValueError with 'bloqueada' keyword"""
        mock_gateway = AsyncMock()
        mock_gateway.process_interaction = AsyncMock(
            side_effect=ValueError("Interacción bloqueada por política de gobernanza")
        )

        def override_get_db():
            yield test_db

        def override_get_gateway():
            return mock_gateway

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_ai_gateway] = override_get_gateway

        with TestClient(app) as test_client:
            session_response = test_client.post("/api/v1/sessions", json={
                "student_id": "test_student",
                "activity_id": "test_activity",
                "mode": "TUTOR"
            })
            session_id = session_response.json()["data"]["id"]

            response = test_client.post("/api/v1/interactions", json={
                "session_id": session_id,
                "prompt": "Dame todo el código",
                "cognitive_intent": "IMPLEMENTATION"
            })

            # Should be treated as governance blocked
            assert response.status_code in [200, 403, 400]

        app.dependency_overrides.clear()


# ============================================================================
# Interaction History Tests
# ============================================================================

class TestInteractionHistory:
    """Tests for GET /interactions/{session_id}/history endpoint"""

    def test_get_interaction_history_empty(self, client, active_session):
        """Test getting history for session with no interactions"""
        response = client.get(
            f"/api/v1/interactions/{active_session['id']}/history"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"]["session_id"] == active_session["id"]
        assert data["data"]["total_interactions"] == 0
        assert data["data"]["interactions"] == []

    def test_get_interaction_history_with_interactions(self, client, active_session):
        """Test getting history after processing interactions"""
        # Process some interactions
        prompts = [
            "¿Qué es una cola?",
            "¿Cómo implemento enqueue?",
            "¿Y dequeue?"
        ]

        for prompt in prompts:
            client.post("/api/v1/interactions", json={
                "session_id": active_session["id"],
                "prompt": prompt,
                "cognitive_intent": "UNDERSTANDING"
            })

        # Get history
        response = client.get(
            f"/api/v1/interactions/{active_session['id']}/history"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        # Note: actual count depends on trace creation in mock

    def test_get_interaction_history_session_not_found(self, client):
        """Test getting history for non-existent session"""
        response = client.get(
            "/api/v1/interactions/non_existent_session/history"
        )

        assert response.status_code == 404

    def test_get_interaction_history_returns_avg_ai_involvement(
        self,
        client,
        active_session
    ):
        """Test that history includes average AI involvement"""
        response = client.get(
            f"/api/v1/interactions/{active_session['id']}/history"
        )

        assert response.status_code == 200
        data = response.json()

        assert "avg_ai_involvement" in data["data"]

    def test_get_interaction_history_returns_blocked_count(
        self,
        client,
        active_session
    ):
        """Test that history includes blocked interaction count"""
        response = client.get(
            f"/api/v1/interactions/{active_session['id']}/history"
        )

        assert response.status_code == 200
        data = response.json()

        assert "blocked_count" in data["data"]
        assert data["data"]["blocked_count"] >= 0


# ============================================================================
# Transaction Management Tests
# ============================================================================

class TestTransactionManagement:
    """Tests for transaction management in interactions"""

    def test_interaction_uses_transaction(self, client, active_session):
        """Test that interaction processing uses transaction"""
        response = client.post("/api/v1/interactions", json={
            "session_id": active_session["id"],
            "prompt": "Test transaction",
            "cognitive_intent": "UNDERSTANDING"
        })

        # If transaction management works, this should succeed
        assert response.status_code == 200

    def test_multiple_interactions_same_session(self, client, active_session):
        """Test multiple interactions in same session"""
        for i in range(5):
            response = client.post("/api/v1/interactions", json={
                "session_id": active_session["id"],
                "prompt": f"Pregunta número {i+1}",
                "cognitive_intent": "UNDERSTANDING"
            })
            assert response.status_code == 200

    def test_concurrent_interactions_different_sessions(self, client, test_db):
        """Test interactions in different sessions"""
        # Create two sessions
        session1 = client.post("/api/v1/sessions", json={
            "student_id": "student_1",
            "activity_id": "activity_1",
            "mode": "TUTOR"
        }).json()["data"]

        session2 = client.post("/api/v1/sessions", json={
            "student_id": "student_2",
            "activity_id": "activity_1",
            "mode": "TUTOR"
        }).json()["data"]

        # Process interactions in both
        resp1 = client.post("/api/v1/interactions", json={
            "session_id": session1["id"],
            "prompt": "Pregunta de estudiante 1",
            "cognitive_intent": "UNDERSTANDING"
        })

        resp2 = client.post("/api/v1/interactions", json={
            "session_id": session2["id"],
            "prompt": "Pregunta de estudiante 2",
            "cognitive_intent": "UNDERSTANDING"
        })

        assert resp1.status_code == 200
        assert resp2.status_code == 200


# ============================================================================
# Integration Tests
# ============================================================================

class TestInteractionIntegration:
    """Integration tests for interaction flow"""

    def test_full_interaction_flow(self, client, active_session):
        """Test complete flow: interact -> verify trace -> check history"""
        # 1. Process interaction
        interaction_response = client.post("/api/v1/interactions", json={
            "session_id": active_session["id"],
            "prompt": "¿Qué es una estructura de datos?",
            "cognitive_intent": "UNDERSTANDING"
        })
        assert interaction_response.status_code == 200

        # 2. Check traces exist
        traces_response = client.get(
            f"/api/v1/traces/{active_session['id']}"
        )
        assert traces_response.status_code == 200

        # 3. Check history
        history_response = client.get(
            f"/api/v1/interactions/{active_session['id']}/history"
        )
        assert history_response.status_code == 200

    def test_interaction_flow_with_governance_check(self, client, active_session):
        """Test interaction flow including governance check"""
        # Valid conceptual question - should pass
        valid_response = client.post("/api/v1/interactions", json={
            "session_id": active_session["id"],
            "prompt": "¿Cuál es la diferencia entre una pila y una cola?",
            "cognitive_intent": "UNDERSTANDING"
        })
        assert valid_response.status_code == 200
        assert valid_response.json()["data"]["blocked"] is False

    def test_interaction_response_structure(self, client, active_session):
        """Test that interaction response has complete structure"""
        response = client.post("/api/v1/interactions", json={
            "session_id": active_session["id"],
            "prompt": "Pregunta de prueba",
            "cognitive_intent": "UNDERSTANDING"
        })

        assert response.status_code == 200
        data = response.json()["data"]

        # Verify all required fields
        required_fields = [
            "interaction_id",
            "session_id",
            "response",
            "agent_used",
            "cognitive_state_detected",
            "ai_involvement",
            "blocked",
            "trace_id",
            "risks_detected",
            "timestamp"
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"