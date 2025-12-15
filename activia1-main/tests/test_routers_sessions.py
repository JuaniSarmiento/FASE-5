"""
Tests for Sessions Router

Verifies:
- POST /sessions - Create session
- GET /sessions - List sessions with filters and pagination
- GET /sessions/{id} - Get session details
- PATCH /sessions/{id} - Update session
- DELETE /sessions/{id} - Delete session
- GET /sessions/history/{student_id} - Get session history with aggregations
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, date, timedelta

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
# Create Session Tests
# ============================================================================

class TestCreateSession:
    """Tests for POST /sessions endpoint"""

    def test_create_session_success(self, client):
        """Test successful session creation"""
        response = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })

        assert response.status_code == 201
        data = response.json()

        assert data["success"] is True
        assert data["data"]["student_id"] == "student_001"
        assert data["data"]["activity_id"] == "activity_001"
        assert data["data"]["mode"] == "TUTOR"
        assert data["data"]["status"] == "active"
        assert data["data"]["id"] is not None

    def test_create_session_evaluator_mode(self, client):
        """Test session creation with EVALUATOR mode"""
        response = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "EVALUATOR"
        })

        assert response.status_code == 201
        assert response.json()["data"]["mode"] == "EVALUATOR"

    def test_create_session_simulator_mode(self, client):
        """Test session creation with SIMULATOR mode"""
        response = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "SIMULATOR"
        })

        assert response.status_code == 201
        assert response.json()["data"]["mode"] == "SIMULATOR"

    def test_create_session_invalid_mode(self, client):
        """Test session creation with invalid mode"""
        response = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "INVALID_MODE"
        })

        assert response.status_code == 422

    def test_create_session_missing_student_id(self, client):
        """Test session creation without student_id"""
        response = client.post("/api/v1/sessions", json={
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })

        assert response.status_code == 422

    def test_create_session_missing_activity_id(self, client):
        """Test session creation without activity_id"""
        response = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "mode": "TUTOR"
        })

        assert response.status_code == 422

    def test_create_session_missing_mode(self, client):
        """Test session creation without mode"""
        response = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001"
        })

        assert response.status_code == 422

    def test_create_session_returns_timestamps(self, client):
        """Test that created session includes timestamps"""
        response = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })

        data = response.json()["data"]
        assert "start_time" in data
        assert "created_at" in data


# ============================================================================
# List Sessions Tests
# ============================================================================

class TestListSessions:
    """Tests for GET /sessions endpoint"""

    def test_list_sessions_empty(self, client):
        """Test listing sessions when none exist"""
        response = client.get("/api/v1/sessions")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"] == []
        assert data["pagination"]["total_items"] == 0

    def test_list_sessions_with_data(self, client):
        """Test listing sessions with data"""
        # Create sessions
        for i in range(3):
            client.post("/api/v1/sessions", json={
                "student_id": f"student_{i:03d}",
                "activity_id": "activity_001",
                "mode": "TUTOR"
            })

        response = client.get("/api/v1/sessions")

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 3
        assert data["pagination"]["total_items"] == 3

    def test_list_sessions_filter_by_student(self, client):
        """Test filtering sessions by student_id"""
        # Create sessions for different students
        client.post("/api/v1/sessions", json={
            "student_id": "student_A",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })
        client.post("/api/v1/sessions", json={
            "student_id": "student_B",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })

        response = client.get("/api/v1/sessions?student_id=student_A")

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 1
        assert data["data"][0]["student_id"] == "student_A"

    def test_list_sessions_filter_by_activity(self, client):
        """Test filtering sessions by activity_id"""
        client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_A",
            "mode": "TUTOR"
        })
        client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_B",
            "mode": "TUTOR"
        })

        response = client.get("/api/v1/sessions?activity_id=activity_A")

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 1
        assert data["data"][0]["activity_id"] == "activity_A"

    def test_list_sessions_filter_by_mode(self, client):
        """Test filtering sessions by mode"""
        client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })
        client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "EVALUATOR"
        })

        response = client.get("/api/v1/sessions?mode=TUTOR")

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 1
        assert data["data"][0]["mode"] == "TUTOR"

    def test_list_sessions_filter_by_status(self, client):
        """Test filtering sessions by status"""
        # Create and complete one session
        create_resp = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })
        session_id = create_resp.json()["data"]["id"]
        client.patch(f"/api/v1/sessions/{session_id}", json={"status": "completed"})

        # Create active session
        client.post("/api/v1/sessions", json={
            "student_id": "student_002",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })

        response = client.get("/api/v1/sessions?status=active")

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 1
        assert data["data"][0]["status"] == "active"

    def test_list_sessions_pagination(self, client):
        """Test session listing pagination"""
        # Create 25 sessions
        for i in range(25):
            client.post("/api/v1/sessions", json={
                "student_id": f"student_{i:03d}",
                "activity_id": "activity_001",
                "mode": "TUTOR"
            })

        # Get first page
        response1 = client.get("/api/v1/sessions?page=1&page_size=10")
        data1 = response1.json()

        assert len(data1["data"]) == 10
        assert data1["pagination"]["total_items"] == 25
        assert data1["pagination"]["total_pages"] == 3
        assert data1["pagination"]["has_next"] is True
        assert data1["pagination"]["has_prev"] is False

        # Get second page
        response2 = client.get("/api/v1/sessions?page=2&page_size=10")
        data2 = response2.json()

        assert len(data2["data"]) == 10
        assert data2["pagination"]["has_next"] is True
        assert data2["pagination"]["has_prev"] is True

        # Get third page
        response3 = client.get("/api/v1/sessions?page=3&page_size=10")
        data3 = response3.json()

        assert len(data3["data"]) == 5
        assert data3["pagination"]["has_next"] is False
        assert data3["pagination"]["has_prev"] is True

    def test_list_sessions_combined_filters(self, client):
        """Test combining multiple filters"""
        # Create varied sessions
        client.post("/api/v1/sessions", json={
            "student_id": "student_A",
            "activity_id": "activity_1",
            "mode": "TUTOR"
        })
        client.post("/api/v1/sessions", json={
            "student_id": "student_A",
            "activity_id": "activity_2",
            "mode": "EVALUATOR"
        })
        client.post("/api/v1/sessions", json={
            "student_id": "student_B",
            "activity_id": "activity_1",
            "mode": "TUTOR"
        })

        response = client.get(
            "/api/v1/sessions?student_id=student_A&mode=TUTOR"
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 1
        assert data["data"][0]["student_id"] == "student_A"
        assert data["data"][0]["mode"] == "TUTOR"


# ============================================================================
# Get Session Tests
# ============================================================================

class TestGetSession:
    """Tests for GET /sessions/{id} endpoint"""

    def test_get_session_success(self, client):
        """Test getting a session by ID"""
        # Create session
        create_resp = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })
        session_id = create_resp.json()["data"]["id"]

        response = client.get(f"/api/v1/sessions/{session_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"]["id"] == session_id
        assert data["data"]["student_id"] == "student_001"

    def test_get_session_not_found(self, client):
        """Test getting non-existent session"""
        response = client.get("/api/v1/sessions/non_existent_id")

        assert response.status_code == 404
        assert response.json()["success"] is False

    def test_get_session_includes_detail_fields(self, client):
        """Test that session detail includes additional fields"""
        create_resp = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })
        session_id = create_resp.json()["data"]["id"]

        response = client.get(f"/api/v1/sessions/{session_id}")
        data = response.json()["data"]

        # Should include detail fields
        assert "traces_summary" in data
        assert "risks_summary" in data
        assert "ai_dependency_score" in data


# ============================================================================
# Update Session Tests
# ============================================================================

class TestUpdateSession:
    """Tests for PATCH /sessions/{id} endpoint"""

    def test_update_session_mode(self, client):
        """Test updating session mode"""
        create_resp = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })
        session_id = create_resp.json()["data"]["id"]

        response = client.patch(f"/api/v1/sessions/{session_id}", json={
            "mode": "EVALUATOR"
        })

        assert response.status_code == 200
        assert response.json()["data"]["mode"] == "EVALUATOR"

    def test_update_session_status_to_completed(self, client):
        """Test updating session status to completed"""
        create_resp = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })
        session_id = create_resp.json()["data"]["id"]

        response = client.patch(f"/api/v1/sessions/{session_id}", json={
            "status": "completed"
        })

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "completed"
        assert data["end_time"] is not None

    def test_update_session_status_to_aborted(self, client):
        """Test updating session status to aborted"""
        create_resp = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })
        session_id = create_resp.json()["data"]["id"]

        response = client.patch(f"/api/v1/sessions/{session_id}", json={
            "status": "aborted"
        })

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["status"] == "aborted"

    def test_update_session_not_found(self, client):
        """Test updating non-existent session"""
        response = client.patch("/api/v1/sessions/non_existent_id", json={
            "mode": "EVALUATOR"
        })

        assert response.status_code == 404

    def test_update_session_invalid_mode(self, client):
        """Test updating session with invalid mode"""
        create_resp = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })
        session_id = create_resp.json()["data"]["id"]

        response = client.patch(f"/api/v1/sessions/{session_id}", json={
            "mode": "INVALID_MODE"
        })

        assert response.status_code == 422


# ============================================================================
# Delete Session Tests
# ============================================================================

class TestDeleteSession:
    """Tests for DELETE /sessions/{id} endpoint"""

    def test_delete_session_success(self, client):
        """Test successful session deletion"""
        create_resp = client.post("/api/v1/sessions", json={
            "student_id": "student_001",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })
        session_id = create_resp.json()["data"]["id"]

        response = client.delete(f"/api/v1/sessions/{session_id}")

        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/v1/sessions/{session_id}")
        assert get_response.status_code == 404

    def test_delete_session_not_found(self, client):
        """Test deleting non-existent session"""
        response = client.delete("/api/v1/sessions/non_existent_id")

        assert response.status_code == 404


# ============================================================================
# Session History Tests
# ============================================================================

class TestSessionHistory:
    """Tests for GET /sessions/history/{student_id} endpoint"""

    def test_get_session_history_empty(self, client):
        """Test getting history for student with no sessions"""
        response = client.get("/api/v1/sessions/history/student_no_sessions")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert data["data"]["student_id"] == "student_no_sessions"
        assert data["data"]["sessions"] == []
        assert data["data"]["aggregations"]["total_sessions"] == 0

    def test_get_session_history_with_sessions(self, client):
        """Test getting history for student with sessions"""
        # Create sessions for student
        for i in range(3):
            client.post("/api/v1/sessions", json={
                "student_id": "student_history",
                "activity_id": f"activity_{i}",
                "mode": "TUTOR"
            })

        response = client.get("/api/v1/sessions/history/student_history")

        assert response.status_code == 200
        data = response.json()

        assert data["data"]["student_id"] == "student_history"
        assert len(data["data"]["sessions"]) == 3
        assert data["data"]["aggregations"]["total_sessions"] == 3

    def test_get_session_history_filter_by_activity(self, client):
        """Test filtering history by activity"""
        # Create sessions with different activities
        client.post("/api/v1/sessions", json={
            "student_id": "student_filter",
            "activity_id": "activity_A",
            "mode": "TUTOR"
        })
        client.post("/api/v1/sessions", json={
            "student_id": "student_filter",
            "activity_id": "activity_B",
            "mode": "TUTOR"
        })

        response = client.get(
            "/api/v1/sessions/history/student_filter?activity_id=activity_A"
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]["sessions"]) == 1
        assert data["data"]["sessions"][0]["activity_id"] == "activity_A"

    def test_get_session_history_filter_by_mode(self, client):
        """Test filtering history by mode"""
        client.post("/api/v1/sessions", json={
            "student_id": "student_mode",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })
        client.post("/api/v1/sessions", json={
            "student_id": "student_mode",
            "activity_id": "activity_001",
            "mode": "EVALUATOR"
        })

        response = client.get(
            "/api/v1/sessions/history/student_mode?mode=TUTOR"
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]["sessions"]) == 1

    def test_get_session_history_includes_aggregations(self, client):
        """Test that history includes aggregations"""
        # Create sessions
        for i in range(3):
            resp = client.post("/api/v1/sessions", json={
                "student_id": "student_agg",
                "activity_id": "activity_001",
                "mode": "TUTOR"
            })
            # Complete some sessions
            if i < 2:
                session_id = resp.json()["data"]["id"]
                client.patch(f"/api/v1/sessions/{session_id}", json={
                    "status": "completed"
                })

        response = client.get("/api/v1/sessions/history/student_agg")

        assert response.status_code == 200
        aggregations = response.json()["data"]["aggregations"]

        assert aggregations["total_sessions"] == 3
        assert aggregations["completed_sessions"] == 2
        assert "total_interactions" in aggregations
        assert "average_ai_dependency" in aggregations
        assert "activity_breakdown" in aggregations
        assert "mode_breakdown" in aggregations
        assert "risk_summary" in aggregations

    def test_get_session_history_includes_filters_applied(self, client):
        """Test that response includes applied filters"""
        client.post("/api/v1/sessions", json={
            "student_id": "student_filters",
            "activity_id": "activity_001",
            "mode": "TUTOR"
        })

        response = client.get(
            "/api/v1/sessions/history/student_filters?activity_id=activity_001&mode=TUTOR"
        )

        assert response.status_code == 200
        data = response.json()

        filters = data["data"]["filters_applied"]
        assert filters is not None
        assert filters.get("activity_id") == "activity_001"
        assert filters.get("mode") == "TUTOR"


# ============================================================================
# Integration Tests
# ============================================================================

class TestSessionIntegration:
    """Integration tests for session lifecycle"""

    def test_full_session_lifecycle(self, client):
        """Test complete session lifecycle: create -> update -> complete"""
        # 1. Create session
        create_resp = client.post("/api/v1/sessions", json={
            "student_id": "lifecycle_student",
            "activity_id": "lifecycle_activity",
            "mode": "TUTOR"
        })
        assert create_resp.status_code == 201
        session_id = create_resp.json()["data"]["id"]

        # 2. Get session details
        get_resp = client.get(f"/api/v1/sessions/{session_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["data"]["status"] == "active"

        # 3. Update mode
        update_resp = client.patch(f"/api/v1/sessions/{session_id}", json={
            "mode": "EVALUATOR"
        })
        assert update_resp.status_code == 200
        assert update_resp.json()["data"]["mode"] == "EVALUATOR"

        # 4. Complete session
        complete_resp = client.patch(f"/api/v1/sessions/{session_id}", json={
            "status": "completed"
        })
        assert complete_resp.status_code == 200
        assert complete_resp.json()["data"]["status"] == "completed"

        # 5. Verify in history
        history_resp = client.get(
            "/api/v1/sessions/history/lifecycle_student"
        )
        assert history_resp.status_code == 200
        sessions = history_resp.json()["data"]["sessions"]
        assert len(sessions) == 1
        assert sessions[0]["status"] == "COMPLETED"

    def test_multiple_sessions_same_student(self, client):
        """Test multiple sessions for same student"""
        student_id = "multi_session_student"

        # Create multiple sessions
        session_ids = []
        for i in range(5):
            resp = client.post("/api/v1/sessions", json={
                "student_id": student_id,
                "activity_id": f"activity_{i}",
                "mode": "TUTOR"
            })
            session_ids.append(resp.json()["data"]["id"])

        # Verify list filtering
        list_resp = client.get(f"/api/v1/sessions?student_id={student_id}")
        assert len(list_resp.json()["data"]) == 5

        # Verify history
        history_resp = client.get(f"/api/v1/sessions/history/{student_id}")
        assert history_resp.json()["data"]["aggregations"]["total_sessions"] == 5