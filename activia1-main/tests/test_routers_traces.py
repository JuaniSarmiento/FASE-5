"""
Tests for Traces Router (N4 Traceability)

Verifies:
- GET /traces/{session_id} - Get session traces with filters
- GET /traces/{session_id}/cognitive-path - Reconstruct cognitive path
- GET /traces/student/{student_id} - Get student traces across sessions
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
import uuid

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


@pytest.fixture
def sample_session(test_db):
    """Create a sample session for testing"""
    from backend.database.models import SessionDB

    session = SessionDB(
        id=str(uuid.uuid4()),
        student_id="test-student-123",
        activity_id="test-activity-456",
        status="active"
    )
    test_db.add(session)
    test_db.commit()
    test_db.refresh(session)
    return session


@pytest.fixture
def sample_traces(test_db, sample_session):
    """Create sample traces for testing"""
    from backend.database.models import CognitiveTraceDB

    traces = []
    ai_involvements = [0.2, 0.3, 0.5, 0.8, 0.4]
    states = ["exploracion", "exploracion", "comprension", "aplicacion", "reflexion"]
    levels = ["n1_operativo", "n2_tactico", "n3_interaccional", "n4_cognitivo", "n4_cognitivo"]
    types = ["student_prompt", "ai_response", "student_prompt", "ai_response", "student_prompt"]

    for i in range(5):
        trace = CognitiveTraceDB(
            id=str(uuid.uuid4()),
            session_id=sample_session.id,
            student_id=sample_session.student_id,
            activity_id=sample_session.activity_id,
            trace_level=levels[i],
            interaction_type=types[i],
            cognitive_state=states[i],
            cognitive_intent=f"Test intent {i}",
            content=f"Test content {i}",
            ai_involvement=ai_involvements[i],
            trace_metadata={"index": i}
        )
        test_db.add(trace)
        traces.append(trace)

    test_db.commit()
    for t in traces:
        test_db.refresh(t)
    return traces


# ============================================================================
# Get Session Traces Tests
# ============================================================================

class TestGetSessionTraces:
    """Tests for GET /traces/{session_id}"""

    def test_get_session_traces_success(self, client, sample_session, sample_traces):
        """Test getting traces for a session"""
        response = client.get(f"/api/v1/traces/{sample_session.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) == 5

    def test_get_session_traces_returns_trace_fields(self, client, sample_session, sample_traces):
        """Test that traces have all required fields"""
        response = client.get(f"/api/v1/traces/{sample_session.id}")

        trace = response.json()["data"][0]

        assert "id" in trace
        assert "session_id" in trace
        assert "student_id" in trace
        assert "activity_id" in trace
        assert "trace_level" in trace
        assert "interaction_type" in trace
        assert "cognitive_state" in trace
        assert "content" in trace
        assert "ai_involvement" in trace
        assert "timestamp" in trace

    def test_get_session_traces_filter_by_level(self, client, sample_session, sample_traces):
        """Test filtering traces by trace level"""
        response = client.get(
            f"/api/v1/traces/{sample_session.id}",
            params={"trace_level": "n4_cognitivo"}
        )

        assert response.status_code == 200
        data = response.json()["data"]

        # Should only return N4 traces
        assert len(data) == 2
        for trace in data:
            assert trace["trace_level"] == "n4_cognitivo"

    def test_get_session_traces_filter_by_interaction_type(self, client, sample_session, sample_traces):
        """Test filtering traces by interaction type"""
        response = client.get(
            f"/api/v1/traces/{sample_session.id}",
            params={"interaction_type": "student_prompt"}
        )

        assert response.status_code == 200
        data = response.json()["data"]

        for trace in data:
            assert trace["interaction_type"] == "student_prompt"

    def test_get_session_traces_filter_by_cognitive_state(self, client, sample_session, sample_traces):
        """Test filtering traces by cognitive state"""
        response = client.get(
            f"/api/v1/traces/{sample_session.id}",
            params={"cognitive_state": "exploracion"}
        )

        assert response.status_code == 200
        data = response.json()["data"]

        for trace in data:
            assert trace["cognitive_state"] == "exploracion"

    def test_get_session_traces_pagination(self, client, sample_session, sample_traces):
        """Test traces pagination"""
        response = client.get(
            f"/api/v1/traces/{sample_session.id}",
            params={"page": 1, "page_size": 2}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 2
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 2
        assert data["pagination"]["total_items"] == 5
        assert data["pagination"]["has_next"] is True

    def test_get_session_traces_pagination_page_2(self, client, sample_session, sample_traces):
        """Test getting second page of traces"""
        response = client.get(
            f"/api/v1/traces/{sample_session.id}",
            params={"page": 2, "page_size": 2}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 2
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["has_prev"] is True

    def test_get_session_traces_session_not_found(self, client):
        """Test getting traces for non-existent session"""
        response = client.get("/api/v1/traces/nonexistent-session-id")

        assert response.status_code == 404

    def test_get_session_traces_combined_filters(self, client, sample_session, sample_traces):
        """Test combining multiple filters"""
        response = client.get(
            f"/api/v1/traces/{sample_session.id}",
            params={
                "trace_level": "n4_cognitivo",
                "interaction_type": "ai_response"
            }
        )

        assert response.status_code == 200
        data = response.json()["data"]

        for trace in data:
            assert trace["trace_level"] == "n4_cognitivo"
            assert trace["interaction_type"] == "ai_response"


# ============================================================================
# Cognitive Path Tests
# ============================================================================

class TestGetCognitivePath:
    """Tests for GET /traces/{session_id}/cognitive-path"""

    def test_get_cognitive_path_success(self, client, sample_session, sample_traces):
        """Test getting cognitive path for a session"""
        response = client.get(f"/api/v1/traces/{sample_session.id}/cognitive-path")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data

    def test_cognitive_path_has_required_fields(self, client, sample_session, sample_traces):
        """Test that cognitive path has all required fields"""
        response = client.get(f"/api/v1/traces/{sample_session.id}/cognitive-path")

        path = response.json()["data"]

        assert "session_id" in path
        assert "student_id" in path
        assert "activity_id" in path
        assert "states_sequence" in path
        assert "transitions" in path
        assert "total_traces" in path
        assert "n4_traces_count" in path
        assert "ai_dependency_evolution" in path
        assert "strategy_changes" in path

    def test_cognitive_path_states_sequence(self, client, sample_session, sample_traces):
        """Test that states sequence is extracted correctly"""
        response = client.get(f"/api/v1/traces/{sample_session.id}/cognitive-path")

        path = response.json()["data"]

        # Should have states from traces
        assert len(path["states_sequence"]) > 0
        assert "exploracion" in path["states_sequence"]

    def test_cognitive_path_transitions(self, client, sample_session, sample_traces):
        """Test that transitions between states are detected"""
        response = client.get(f"/api/v1/traces/{sample_session.id}/cognitive-path")

        path = response.json()["data"]

        # Should detect transitions when state changes
        if len(path["transitions"]) > 0:
            transition = path["transitions"][0]
            assert "from" in transition
            assert "to" in transition
            assert transition["from"] != transition["to"]

    def test_cognitive_path_ai_evolution(self, client, sample_session, sample_traces):
        """Test that AI dependency evolution is tracked"""
        response = client.get(f"/api/v1/traces/{sample_session.id}/cognitive-path")

        path = response.json()["data"]

        assert len(path["ai_dependency_evolution"]) == 5
        # Check values are floats between 0 and 1
        for val in path["ai_dependency_evolution"]:
            assert 0.0 <= val <= 1.0

    def test_cognitive_path_strategy_changes(self, client, sample_session, sample_traces):
        """Test that significant strategy changes are detected"""
        response = client.get(f"/api/v1/traces/{sample_session.id}/cognitive-path")

        path = response.json()["data"]

        # Strategy changes detected for >0.3 AI involvement change
        # Our test data has: [0.2, 0.3, 0.5, 0.8, 0.4]
        # Changes: 0.1, 0.2, 0.3, -0.4 -> should detect 0.3 and 0.4
        for change in path["strategy_changes"]:
            assert "from_involvement" in change
            assert "to_involvement" in change
            assert abs(change["change"]) > 0.3

    def test_cognitive_path_counts_traces(self, client, sample_session, sample_traces):
        """Test that trace counts are correct"""
        response = client.get(f"/api/v1/traces/{sample_session.id}/cognitive-path")

        path = response.json()["data"]

        assert path["total_traces"] == 5
        assert path["n4_traces_count"] == 2  # We have 2 N4 traces

    def test_cognitive_path_session_not_found(self, client):
        """Test cognitive path for non-existent session"""
        response = client.get("/api/v1/traces/nonexistent-session/cognitive-path")

        assert response.status_code == 404

    def test_cognitive_path_message(self, client, sample_session, sample_traces):
        """Test that response message includes trace count"""
        response = client.get(f"/api/v1/traces/{sample_session.id}/cognitive-path")

        message = response.json()["message"]
        assert "5 traces" in message


# ============================================================================
# Student Traces Tests
# ============================================================================

class TestGetStudentTraces:
    """Tests for GET /traces/student/{student_id}"""

    def test_get_student_traces_success(self, client, sample_session, sample_traces):
        """Test getting all traces for a student"""
        response = client.get(f"/api/v1/traces/student/{sample_session.student_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert len(data["data"]) == 5

    def test_get_student_traces_filter_by_activity(self, client, sample_session, sample_traces):
        """Test filtering student traces by activity"""
        response = client.get(
            f"/api/v1/traces/student/{sample_session.student_id}",
            params={"activity_id": sample_session.activity_id}
        )

        assert response.status_code == 200
        data = response.json()["data"]

        for trace in data:
            assert trace["activity_id"] == sample_session.activity_id

    def test_get_student_traces_pagination(self, client, sample_session, sample_traces):
        """Test student traces pagination"""
        response = client.get(
            f"/api/v1/traces/student/{sample_session.student_id}",
            params={"page": 1, "page_size": 3}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["data"]) == 3
        assert data["pagination"]["total_items"] == 5

    def test_get_student_traces_empty_result(self, client):
        """Test getting traces for student with no traces"""
        response = client.get("/api/v1/traces/student/nonexistent-student")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert len(data["data"]) == 0

    def test_get_student_traces_across_sessions(self, client, test_db, sample_session, sample_traces):
        """Test getting traces from multiple sessions"""
        from backend.database.models import SessionDB, CognitiveTraceDB

        # Create second session for same student
        session2 = SessionDB(
            id=str(uuid.uuid4()),
            student_id=sample_session.student_id,
            activity_id="activity-2",
            status="active"
        )
        test_db.add(session2)

        # Add traces to second session
        trace2 = CognitiveTraceDB(
            id=str(uuid.uuid4()),
            session_id=session2.id,
            student_id=sample_session.student_id,
            activity_id="activity-2",
            trace_level="n4_cognitivo",
            interaction_type="student_prompt",
            content="Content from session 2",
            ai_involvement=0.5
        )
        test_db.add(trace2)
        test_db.commit()

        response = client.get(f"/api/v1/traces/student/{sample_session.student_id}")

        assert response.status_code == 200
        data = response.json()["data"]

        # Should have traces from both sessions
        assert len(data) == 6

        # Verify traces from different activities
        activities = set(t["activity_id"] for t in data)
        assert len(activities) == 2


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestTracesErrorHandling:
    """Tests for error handling in traces endpoints"""

    def test_invalid_page_number(self, client, sample_session, sample_traces):
        """Test invalid page number is rejected"""
        response = client.get(
            f"/api/v1/traces/{sample_session.id}",
            params={"page": 0}  # Invalid: must be >= 1
        )

        assert response.status_code == 422

    def test_invalid_page_size(self, client, sample_session, sample_traces):
        """Test page size over limit is rejected"""
        response = client.get(
            f"/api/v1/traces/{sample_session.id}",
            params={"page_size": 500}  # Max is 200
        )

        assert response.status_code == 422

    def test_negative_page_size(self, client, sample_session, sample_traces):
        """Test negative page size is rejected"""
        response = client.get(
            f"/api/v1/traces/{sample_session.id}",
            params={"page_size": -1}
        )

        assert response.status_code == 422


# ============================================================================
# Integration Tests
# ============================================================================

class TestTracesIntegration:
    """Integration tests for traces endpoints"""

    def test_traces_response_format_consistency(self, client, sample_session, sample_traces):
        """Test that all trace endpoints follow consistent format"""
        # Session traces
        response1 = client.get(f"/api/v1/traces/{sample_session.id}")
        assert "success" in response1.json()
        assert "data" in response1.json()
        assert "pagination" in response1.json()

        # Cognitive path
        response2 = client.get(f"/api/v1/traces/{sample_session.id}/cognitive-path")
        assert "success" in response2.json()
        assert "data" in response2.json()
        assert "message" in response2.json()

        # Student traces
        response3 = client.get(f"/api/v1/traces/student/{sample_session.student_id}")
        assert "success" in response3.json()
        assert "data" in response3.json()
        assert "pagination" in response3.json()

    def test_trace_metadata_preserved(self, client, sample_session, sample_traces):
        """Test that trace metadata is preserved correctly"""
        response = client.get(f"/api/v1/traces/{sample_session.id}")

        traces = response.json()["data"]

        # At least one trace should have metadata
        traces_with_metadata = [t for t in traces if t.get("metadata")]
        assert len(traces_with_metadata) > 0

    def test_timestamp_format(self, client, sample_session, sample_traces):
        """Test that timestamps are in valid ISO format"""
        response = client.get(f"/api/v1/traces/{sample_session.id}")

        for trace in response.json()["data"]:
            timestamp = trace["timestamp"]
            # Should parse as datetime
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))