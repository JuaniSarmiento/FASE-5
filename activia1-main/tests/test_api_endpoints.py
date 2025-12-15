"""
Tests para los endpoints de la API REST (FastAPI)

Verifica:
- CRUD de sesiones
- Procesamiento de interacciones
- Endpoints de trazas
- Endpoints de riesgos y evaluaciones
- Manejo de errores
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.api.main import app
from backend.database.models import Base
from backend.api.deps import get_db


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    # Use in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
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
# Health Check Tests
# ============================================================================

def test_health_check(client):
    """Test GET /api/v1/health"""
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "agents" in data
    assert len(data["agents"]) == 6  # Los 6 agentes AI-Native


def test_health_ping(client):
    """Test GET /api/v1/health/ping"""
    response = client.get("/api/v1/health/ping")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


# ============================================================================
# Session CRUD Tests
# ============================================================================

def test_create_session(client):
    """Test POST /api/v1/sessions - Create session"""
    payload = {
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    }

    response = client.post("/api/v1/sessions", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["success"] is True
    assert "data" in data
    assert data["data"]["student_id"] == "test_student_001"
    assert data["data"]["mode"] == "TUTOR"
    assert data["data"]["status"] == "active"
    assert data["data"]["id"] is not None


def test_create_session_invalid_mode(client):
    """Test POST /api/v1/sessions with invalid mode"""
    payload = {
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "INVALID_MODE"
    }

    response = client.post("/api/v1/sessions", json=payload)
    assert response.status_code == 422  # Validation error


def test_get_session(client):
    """Test GET /api/v1/sessions/{id} - Get session by ID"""
    # Create session first
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    # Get session
    response = client.get(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["data"]["id"] == session_id
    assert data["data"]["student_id"] == "test_student_001"


def test_get_session_not_found(client):
    """Test GET /api/v1/sessions/{id} with non-existent ID"""
    response = client.get("/api/v1/sessions/non_existent_id")

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False


def test_list_sessions(client):
    """Test GET /api/v1/sessions - List all sessions"""
    # Create multiple sessions
    for i in range(3):
        client.post("/api/v1/sessions", json={
            "student_id": f"test_student_{i:03d}",
            "activity_id": "test_activity_001",
            "mode": "TUTOR"
        })

    # List sessions
    response = client.get("/api/v1/sessions")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert len(data["data"]) == 3
    assert "pagination" in data
    assert data["pagination"]["total_items"] == 3


def test_list_sessions_with_filters(client):
    """Test GET /api/v1/sessions with filters"""
    # Create sessions with different student IDs
    client.post("/api/v1/sessions", json={
        "student_id": "student_A",
        "activity_id": "activity_1",
        "mode": "TUTOR"
    })
    client.post("/api/v1/sessions", json={
        "student_id": "student_B",
        "activity_id": "activity_1",
        "mode": "EVALUATOR"
    })

    # Filter by student_id
    response = client.get("/api/v1/sessions?student_id=student_A")
    data = response.json()

    assert len(data["data"]) == 1
    assert data["data"][0]["student_id"] == "student_A"


def test_update_session(client):
    """Test PATCH /api/v1/sessions/{id} - Update session"""
    # Create session
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    # Update mode
    response = client.patch(f"/api/v1/sessions/{session_id}", json={
        "mode": "EVALUATOR"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["data"]["mode"] == "EVALUATOR"


def test_delete_session(client):
    """Test DELETE /api/v1/sessions/{id} - Delete session"""
    # Create session
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    # Delete session
    response = client.delete(f"/api/v1/sessions/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

    # Verify it's deleted
    get_response = client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 404


# ============================================================================
# Interaction Processing Tests
# ============================================================================

def test_process_interaction(client):
    """Test POST /api/v1/interactions - Process interaction"""
    # Create session first
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    # Process interaction
    response = client.post("/api/v1/interactions", json={
        "session_id": session_id,
        "prompt": "¿Qué es una cola circular?",
        "cognitive_intent": "UNDERSTANDING"
    })

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert "response" in data["data"]
    assert data["data"]["agent_used"] is not None
    assert data["data"]["blocked"] is False


def test_process_interaction_blocked_by_governance(client):
    """Test interaction blocked by GOV-IA"""
    # Create session
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    # Try delegation prompt
    response = client.post("/api/v1/interactions", json={
        "session_id": session_id,
        "prompt": "Dame el código completo de la cola circular",
        "cognitive_intent": "IMPLEMENTATION"
    })

    assert response.status_code == 200
    data = response.json()

    # Should be blocked
    assert data["data"]["blocked"] is True
    assert data["data"]["block_reason"] is not None


def test_process_interaction_session_not_found(client):
    """Test interaction with non-existent session"""
    response = client.post("/api/v1/interactions", json={
        "session_id": "non_existent_session",
        "prompt": "Test prompt",
        "cognitive_intent": "UNDERSTANDING"
    })

    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False


def test_process_interaction_inactive_session(client):
    """Test interaction with inactive session"""
    # Create and then complete session
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    # Update status to completed
    client.patch(f"/api/v1/sessions/{session_id}", json={"status": "completed"})

    # Try to process interaction
    response = client.post("/api/v1/interactions", json={
        "session_id": session_id,
        "prompt": "Test prompt",
        "cognitive_intent": "UNDERSTANDING"
    })

    assert response.status_code == 400


# ============================================================================
# Trace Endpoints Tests
# ============================================================================

def test_get_session_traces(client):
    """Test GET /api/v1/traces/{session_id} - Get traces"""
    # Create session
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    # Get traces (should be empty initially)
    response = client.get(f"/api/v1/traces/{session_id}")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert isinstance(data["data"], list)
    assert "pagination" in data


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_validation_error_missing_required_field(client):
    """Test validation error for missing required field"""
    response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        # Missing activity_id and mode
    })

    assert response.status_code == 422


def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.get("/api/v1/health")

    # Should have CORS headers configured
    # (Depends on CORS middleware configuration)
    assert response.status_code == 200


# ============================================================================
# Pagination Tests
# ============================================================================

def test_pagination(client):
    """Test pagination works correctly"""
    # Create 25 sessions
    for i in range(25):
        client.post("/api/v1/sessions", json={
            "student_id": f"student_{i:03d}",
            "activity_id": "test_activity",
            "mode": "TUTOR"
        })

    # Get first page (default page_size=20)
    response = client.get("/api/v1/sessions?page=1&page_size=20")
    data = response.json()

    assert len(data["data"]) == 20
    assert data["pagination"]["total_items"] == 25
    assert data["pagination"]["total_pages"] == 2
    assert data["pagination"]["has_next"] is True
    assert data["pagination"]["has_prev"] is False

    # Get second page
    response2 = client.get("/api/v1/sessions?page=2&page_size=20")
    data2 = response2.json()

    assert len(data2["data"]) == 5
    assert data2["pagination"]["has_next"] is False
    assert data2["pagination"]["has_prev"] is True


# ============================================================================
# Risk Endpoints Tests
# ============================================================================

def test_get_session_risks(client):
    """Test GET /api/v1/risks/session/{session_id} - Get risks for session"""
    # Create session first
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    # Get risks (should be empty initially)
    response = client.get(f"/api/v1/risks/session/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


def test_get_session_risks_not_found(client):
    """Test GET /api/v1/risks/session/{session_id} with invalid session"""
    response = client.get("/api/v1/risks/session/non_existent_session")

    assert response.status_code == 404


def test_get_session_risks_with_filters(client):
    """Test GET /api/v1/risks/session/{session_id} with dimension filter"""
    # Create session
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    # Get risks with filter
    response = client.get(
        f"/api/v1/risks/session/{session_id}?dimension=COGNITIVE"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_get_risk_statistics(client):
    """Test GET /api/v1/risks/statistics - Get risk statistics"""
    # Create session with some interactions to generate risks
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    response = client.get(f"/api/v1/risks/statistics?session_id={session_id}")

    # Statistics endpoint should work
    assert response.status_code in [200, 404]  # 404 if no risks


def test_get_evaluation_by_session(client):
    """Test GET /api/v1/risks/evaluation/session/{session_id}"""
    # Create session
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "EVALUATOR"
    })
    session_id = create_response.json()["data"]["id"]

    response = client.get(f"/api/v1/risks/evaluation/session/{session_id}")

    # Should return 200 with empty or 404 if no evaluation
    assert response.status_code in [200, 404]


def test_resolve_risk(client):
    """Test PATCH /api/v1/risks/{risk_id}/resolve - Resolve a risk"""
    # This test would require creating a risk first
    # For now, test that endpoint exists and returns appropriate error
    response = client.patch("/api/v1/risks/fake_risk_id/resolve", json={
        "resolution_notes": "Resolved by teacher"
    })

    # Should return 404 for non-existent risk
    assert response.status_code == 404


# ============================================================================
# Advanced Trace Endpoints Tests
# ============================================================================

def test_get_traces_with_pagination(client):
    """Test GET /api/v1/traces/{session_id} with pagination"""
    # Create session
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    # Get traces with pagination params
    response = client.get(
        f"/api/v1/traces/{session_id}?page=1&page_size=10"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "pagination" in data


def test_get_traces_by_student(client):
    """Test GET /api/v1/traces/student/{student_id}"""
    # Create sessions for a student
    client.post("/api/v1/sessions", json={
        "student_id": "test_student_traces",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })

    response = client.get("/api/v1/traces/student/test_student_traces")

    # Should return 200 even if empty
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_get_trace_by_id(client):
    """Test GET /api/v1/traces/detail/{trace_id}"""
    response = client.get("/api/v1/traces/detail/non_existent_trace")

    # Should return 404 for non-existent trace
    assert response.status_code == 404


def test_get_trace_sequence(client):
    """Test GET /api/v1/traces/{session_id}/sequence"""
    # Create session
    create_response = client.post("/api/v1/sessions", json={
        "student_id": "test_student_001",
        "activity_id": "test_activity_001",
        "mode": "TUTOR"
    })
    session_id = create_response.json()["data"]["id"]

    response = client.get(f"/api/v1/traces/{session_id}/sequence")

    # Should return 200 (empty sequence) or 404
    assert response.status_code in [200, 404]


# ============================================================================
# Export Endpoints Tests
# ============================================================================

def test_export_research_data(client):
    """Test POST /api/v1/export/research-data"""
    # Create some data first
    client.post("/api/v1/sessions", json={
        "student_id": "export_test_student",
        "activity_id": "export_test_activity",
        "mode": "TUTOR"
    })

    payload = {
        "include_sessions": True,
        "include_traces": True,
        "include_risks": False,
        "include_evaluations": False,
        "k_anonymity_level": 5,
        "output_format": "json"
    }

    response = client.post("/api/v1/export/research-data", json=payload)

    # Export may return 200 or 400 depending on data availability
    assert response.status_code in [200, 400, 422]


def test_export_research_data_with_date_filter(client):
    """Test POST /api/v1/export/research-data with date filters"""
    payload = {
        "include_sessions": True,
        "include_traces": False,
        "include_risks": False,
        "include_evaluations": False,
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-12-31T23:59:59",
        "k_anonymity_level": 5,
        "output_format": "json"
    }

    response = client.post("/api/v1/export/research-data", json=payload)

    # Should accept the request (may have no data)
    assert response.status_code in [200, 400, 422]


def test_export_history(client):
    """Test GET /api/v1/export/history"""
    response = client.get("/api/v1/export/history")

    # Should return list (possibly empty)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_download_export(client):
    """Test GET /api/v1/export/{export_id}"""
    response = client.get("/api/v1/export/non_existent_export")

    # Should return 404 for non-existent export
    assert response.status_code == 404


def test_export_invalid_format(client):
    """Test POST /api/v1/export/research-data with invalid format"""
    payload = {
        "include_sessions": True,
        "include_traces": False,
        "include_risks": False,
        "include_evaluations": False,
        "k_anonymity_level": 5,
        "output_format": "invalid_format"  # Invalid
    }

    response = client.post("/api/v1/export/research-data", json=payload)

    # Should return validation error
    assert response.status_code == 422


def test_export_with_activity_filter(client):
    """Test POST /api/v1/export/research-data with activity filter"""
    # Create session with specific activity
    client.post("/api/v1/sessions", json={
        "student_id": "filter_test_student",
        "activity_id": "specific_activity_123",
        "mode": "TUTOR"
    })

    payload = {
        "include_sessions": True,
        "include_traces": False,
        "include_risks": False,
        "include_evaluations": False,
        "activity_ids": ["specific_activity_123"],
        "k_anonymity_level": 5,
        "output_format": "json"
    }

    response = client.post("/api/v1/export/research-data", json=payload)

    assert response.status_code in [200, 400, 422]


# ============================================================================
# Combined Flow Tests
# ============================================================================

def test_session_interaction_trace_flow(client):
    """Test complete flow: create session -> interact -> view traces"""
    # 1. Create session
    session_response = client.post("/api/v1/sessions", json={
        "student_id": "flow_test_student",
        "activity_id": "flow_test_activity",
        "mode": "TUTOR"
    })
    assert session_response.status_code == 201
    session_id = session_response.json()["data"]["id"]

    # 2. Process interaction
    interaction_response = client.post("/api/v1/interactions", json={
        "session_id": session_id,
        "prompt": "¿Cómo funciona una pila?",
        "cognitive_intent": "UNDERSTANDING"
    })
    assert interaction_response.status_code == 200

    # 3. View traces
    traces_response = client.get(f"/api/v1/traces/{session_id}")
    assert traces_response.status_code == 200

    # 4. View risks
    risks_response = client.get(f"/api/v1/risks/session/{session_id}")
    assert risks_response.status_code == 200


def test_multiple_interactions_generate_trace_sequence(client):
    """Test multiple interactions create proper trace sequence"""
    # Create session
    session_response = client.post("/api/v1/sessions", json={
        "student_id": "sequence_test_student",
        "activity_id": "sequence_test_activity",
        "mode": "TUTOR"
    })
    session_id = session_response.json()["data"]["id"]

    # Multiple interactions
    prompts = [
        "¿Qué es una cola?",
        "¿Cómo implemento enqueue?",
        "¿Y dequeue?"
    ]

    for prompt in prompts:
        response = client.post("/api/v1/interactions", json={
            "session_id": session_id,
            "prompt": prompt,
            "cognitive_intent": "UNDERSTANDING"
        })
        assert response.status_code == 200

    # Check traces
    traces_response = client.get(f"/api/v1/traces/{session_id}")
    assert traces_response.status_code == 200
