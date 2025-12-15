"""
Tests for Risks Router

Verifies:
- GET /risks/session/{session_id} - Get session risks
- GET /risks/student/{student_id} - Get student risks
- GET /risks/student/{student_id}/statistics - Risk statistics
- GET /risks/critical - Get critical unresolved risks
- GET /risks/evaluation/session/{session_id} - Get session evaluation
- GET /risks/evaluation/student/{student_id} - Get student evaluations
"""
import pytest
from unittest.mock import Mock, patch
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
        status="completed"
    )
    test_db.add(session)
    test_db.commit()
    test_db.refresh(session)
    return session


@pytest.fixture
def sample_risks(test_db, sample_session):
    """Create sample risks for testing"""
    from backend.database.models import RiskDB

    risks = []
    risk_data = [
        {
            "risk_type": "DELEGATION",
            "risk_level": "HIGH",
            "dimension": "ETHICAL",
            "description": "Possible delegation detected",
            "resolved": False
        },
        {
            "risk_type": "SUPERFICIAL_REASONING",
            "risk_level": "MEDIUM",
            "dimension": "COGNITIVE",
            "description": "Superficial reasoning pattern",
            "resolved": True
        },
        {
            "risk_type": "EXCESSIVE_AI_DEPENDENCY",
            "risk_level": "CRITICAL",
            "dimension": "COGNITIVE",
            "description": "Very high AI dependency",
            "resolved": False
        },
        {
            "risk_type": "LOOP_DETECTED",
            "risk_level": "LOW",
            "dimension": "PROCEDURAL",
            "description": "Interaction loop detected",
            "resolved": True
        }
    ]

    for data in risk_data:
        risk = RiskDB(
            id=str(uuid.uuid4()),
            session_id=sample_session.id,
            student_id=sample_session.student_id,
            activity_id=sample_session.activity_id,
            risk_type=data["risk_type"],
            risk_level=data["risk_level"],
            dimension=data["dimension"],
            description=data["description"],
            evidence=["evidence1", "evidence2"],
            trace_ids=["trace1", "trace2"],
            recommendations=["recommendation1"],
            resolved=data["resolved"],
            resolution_notes="Resolved by student" if data["resolved"] else None
        )
        test_db.add(risk)
        risks.append(risk)

    test_db.commit()
    for r in risks:
        test_db.refresh(r)
    return risks


@pytest.fixture
def sample_evaluation(test_db, sample_session):
    """Create sample evaluation for testing"""
    from backend.database.models import EvaluationDB

    evaluation = EvaluationDB(
        id=str(uuid.uuid4()),
        session_id=sample_session.id,
        student_id=sample_session.student_id,
        activity_id=sample_session.activity_id,
        overall_competency_level="INTERMEDIATE",
        overall_score=0.75,
        dimensions={
            "cognitive": 0.8,
            "procedural": 0.7,
            "ethical": 0.75
        },
        key_strengths=["problem_solving", "critical_thinking"],
        improvement_areas=["documentation", "testing"],
        reasoning_analysis="Good reasoning with minor gaps",
        git_analysis="Regular commits with clear messages",
        ai_dependency_metrics={
            "average_involvement": 0.45,
            "trend": "decreasing"
        }
    )
    test_db.add(evaluation)
    test_db.commit()
    test_db.refresh(evaluation)
    return evaluation


# ============================================================================
# Session Risks Tests
# ============================================================================

class TestGetSessionRisks:
    """Tests for GET /risks/session/{session_id}"""

    def test_get_session_risks_success(self, client, sample_session, sample_risks):
        """Test getting risks for a session"""
        response = client.get(f"/api/v1/risks/session/{sample_session.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert len(data["data"]) == 4

    def test_get_session_risks_has_required_fields(self, client, sample_session, sample_risks):
        """Test that risk has all required fields"""
        response = client.get(f"/api/v1/risks/session/{sample_session.id}")

        risk = response.json()["data"][0]

        assert "id" in risk
        assert "student_id" in risk
        assert "activity_id" in risk
        assert "risk_type" in risk
        assert "risk_level" in risk
        assert "dimension" in risk
        assert "description" in risk
        assert "evidence" in risk
        assert "trace_ids" in risk
        assert "recommendations" in risk
        assert "resolved" in risk
        assert "created_at" in risk

    def test_get_session_risks_filter_resolved(self, client, sample_session, sample_risks):
        """Test filtering risks by resolved status"""
        response = client.get(
            f"/api/v1/risks/session/{sample_session.id}",
            params={"resolved": True}
        )

        assert response.status_code == 200
        data = response.json()["data"]

        # 2 resolved risks
        assert len(data) == 2
        for risk in data:
            assert risk["resolved"] is True

    def test_get_session_risks_filter_unresolved(self, client, sample_session, sample_risks):
        """Test filtering unresolved risks"""
        response = client.get(
            f"/api/v1/risks/session/{sample_session.id}",
            params={"resolved": False}
        )

        data = response.json()["data"]

        # 2 unresolved risks
        assert len(data) == 2
        for risk in data:
            assert risk["resolved"] is False

    def test_get_session_risks_filter_by_dimension(self, client, sample_session, sample_risks):
        """Test filtering risks by dimension"""
        response = client.get(
            f"/api/v1/risks/session/{sample_session.id}",
            params={"dimension": "COGNITIVE"}
        )

        data = response.json()["data"]

        # 2 cognitive risks
        assert len(data) == 2
        for risk in data:
            assert risk["dimension"] == "COGNITIVE"

    def test_get_session_risks_session_not_found(self, client):
        """Test getting risks for non-existent session"""
        response = client.get("/api/v1/risks/session/nonexistent-session")

        assert response.status_code == 404

    def test_get_session_risks_message(self, client, sample_session, sample_risks):
        """Test response message includes count"""
        response = client.get(f"/api/v1/risks/session/{sample_session.id}")

        message = response.json()["message"]
        assert "4 risks" in message


# ============================================================================
# Student Risks Tests
# ============================================================================

class TestGetStudentRisks:
    """Tests for GET /risks/student/{student_id}"""

    def test_get_student_risks_success(self, client, sample_session, sample_risks):
        """Test getting risks for a student"""
        response = client.get(f"/api/v1/risks/student/{sample_session.student_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert len(data["data"]) == 4

    def test_get_student_risks_filter_resolved(self, client, sample_session, sample_risks):
        """Test filtering student risks by resolved status"""
        response = client.get(
            f"/api/v1/risks/student/{sample_session.student_id}",
            params={"resolved": False}
        )

        data = response.json()["data"]
        for risk in data:
            assert risk["resolved"] is False

    def test_get_student_risks_filter_dimension(self, client, sample_session, sample_risks):
        """Test filtering student risks by dimension"""
        response = client.get(
            f"/api/v1/risks/student/{sample_session.student_id}",
            params={"dimension": "ETHICAL"}
        )

        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["dimension"] == "ETHICAL"

    def test_get_student_risks_empty(self, client):
        """Test getting risks for student with no risks"""
        response = client.get("/api/v1/risks/student/student-with-no-risks")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert len(data["data"]) == 0


# ============================================================================
# Risk Statistics Tests
# ============================================================================

class TestGetStudentRiskStatistics:
    """Tests for GET /risks/student/{student_id}/statistics"""

    def test_get_risk_statistics_success(self, client, sample_session, sample_risks):
        """Test getting risk statistics for a student"""
        response = client.get(f"/api/v1/risks/student/{sample_session.student_id}/statistics")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        stats = data["data"]

        assert "total_risks" in stats
        assert "by_level" in stats
        assert "by_dimension" in stats
        assert "by_type" in stats
        assert "resolution_rate" in stats

    def test_risk_statistics_total_count(self, client, sample_session, sample_risks):
        """Test that total risks count is correct"""
        response = client.get(f"/api/v1/risks/student/{sample_session.student_id}/statistics")

        stats = response.json()["data"]
        assert stats["total_risks"] == 4

    def test_risk_statistics_by_level(self, client, sample_session, sample_risks):
        """Test risks breakdown by level"""
        response = client.get(f"/api/v1/risks/student/{sample_session.student_id}/statistics")

        by_level = response.json()["data"]["by_level"]

        assert by_level.get("HIGH", 0) == 1
        assert by_level.get("MEDIUM", 0) == 1
        assert by_level.get("CRITICAL", 0) == 1
        assert by_level.get("LOW", 0) == 1

    def test_risk_statistics_by_dimension(self, client, sample_session, sample_risks):
        """Test risks breakdown by dimension"""
        response = client.get(f"/api/v1/risks/student/{sample_session.student_id}/statistics")

        by_dimension = response.json()["data"]["by_dimension"]

        assert by_dimension.get("COGNITIVE", 0) == 2
        assert by_dimension.get("ETHICAL", 0) == 1
        assert by_dimension.get("PROCEDURAL", 0) == 1

    def test_risk_statistics_resolution_rate(self, client, sample_session, sample_risks):
        """Test resolution rate calculation"""
        response = client.get(f"/api/v1/risks/student/{sample_session.student_id}/statistics")

        stats = response.json()["data"]

        # 2 out of 4 resolved = 50%
        assert stats["resolution_rate"] == 50.0

    def test_risk_statistics_empty_student(self, client):
        """Test statistics for student with no risks"""
        response = client.get("/api/v1/risks/student/no-risks-student/statistics")

        assert response.status_code == 200
        stats = response.json()["data"]

        assert stats["total_risks"] == 0
        assert stats["resolution_rate"] == 0


# ============================================================================
# Critical Risks Tests
# ============================================================================

class TestGetCriticalRisks:
    """Tests for GET /risks/critical"""

    def test_get_critical_risks_success(self, client, sample_session, sample_risks):
        """Test getting all critical unresolved risks"""
        response = client.get("/api/v1/risks/critical")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True

    def test_get_critical_risks_only_critical(self, client, sample_session, sample_risks):
        """Test that only critical risks are returned"""
        response = client.get("/api/v1/risks/critical")

        for risk in response.json()["data"]:
            assert risk["risk_level"] == "CRITICAL"

    def test_get_critical_risks_only_unresolved(self, client, sample_session, sample_risks):
        """Test that only unresolved risks are returned"""
        response = client.get("/api/v1/risks/critical")

        for risk in response.json()["data"]:
            assert risk["resolved"] is False

    def test_get_critical_risks_filter_by_student(self, client, sample_session, sample_risks):
        """Test filtering critical risks by student"""
        response = client.get(
            "/api/v1/risks/critical",
            params={"student_id": sample_session.student_id}
        )

        assert response.status_code == 200
        data = response.json()["data"]

        for risk in data:
            assert risk["student_id"] == sample_session.student_id

    def test_get_critical_risks_nonexistent_student(self, client, sample_risks):
        """Test critical risks for student with no risks"""
        response = client.get(
            "/api/v1/risks/critical",
            params={"student_id": "nonexistent-student"}
        )

        assert response.status_code == 200
        assert len(response.json()["data"]) == 0


# ============================================================================
# Session Evaluation Tests
# ============================================================================

class TestGetSessionEvaluation:
    """Tests for GET /risks/evaluation/session/{session_id}"""

    def test_get_session_evaluation_success(self, client, sample_session, sample_evaluation):
        """Test getting evaluation for a session"""
        response = client.get(f"/api/v1/risks/evaluation/session/{sample_session.id}")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True

    def test_session_evaluation_has_required_fields(self, client, sample_session, sample_evaluation):
        """Test that evaluation has all required fields"""
        response = client.get(f"/api/v1/risks/evaluation/session/{sample_session.id}")

        eval_data = response.json()["data"]

        assert "id" in eval_data
        assert "session_id" in eval_data
        assert "student_id" in eval_data
        assert "activity_id" in eval_data
        assert "overall_competency_level" in eval_data
        assert "overall_score" in eval_data
        assert "dimensions" in eval_data
        assert "key_strengths" in eval_data
        assert "improvement_areas" in eval_data
        assert "reasoning_analysis" in eval_data
        assert "ai_dependency_metrics" in eval_data

    def test_session_evaluation_values(self, client, sample_session, sample_evaluation):
        """Test evaluation values are correct"""
        response = client.get(f"/api/v1/risks/evaluation/session/{sample_session.id}")

        eval_data = response.json()["data"]

        assert eval_data["overall_competency_level"] == "INTERMEDIATE"
        assert eval_data["overall_score"] == 0.75
        assert "cognitive" in eval_data["dimensions"]

    def test_session_evaluation_session_not_found(self, client):
        """Test evaluation for non-existent session"""
        response = client.get("/api/v1/risks/evaluation/session/nonexistent-session")

        assert response.status_code == 404

    def test_session_evaluation_no_evaluation(self, client, sample_session):
        """Test session without evaluation"""
        # sample_session exists but has no evaluation (sample_evaluation not used)
        response = client.get(f"/api/v1/risks/evaluation/session/{sample_session.id}")

        assert response.status_code == 404
        assert "evaluation" in response.json()["detail"].lower()


# ============================================================================
# Student Evaluations Tests
# ============================================================================

class TestGetStudentEvaluations:
    """Tests for GET /risks/evaluation/student/{student_id}"""

    def test_get_student_evaluations_success(self, client, sample_session, sample_evaluation):
        """Test getting all evaluations for a student"""
        response = client.get(f"/api/v1/risks/evaluation/student/{sample_session.student_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert len(data["data"]) == 1

    def test_student_evaluations_multiple(self, client, test_db, sample_session, sample_evaluation):
        """Test getting multiple evaluations for a student"""
        from backend.database.models import SessionDB, EvaluationDB

        # Create second session and evaluation
        session2 = SessionDB(
            id=str(uuid.uuid4()),
            student_id=sample_session.student_id,
            activity_id="activity-2",
            status="completed"
        )
        test_db.add(session2)

        eval2 = EvaluationDB(
            id=str(uuid.uuid4()),
            session_id=session2.id,
            student_id=sample_session.student_id,
            activity_id="activity-2",
            overall_competency_level="ADVANCED",
            overall_score=0.85,
            dimensions={"cognitive": 0.9},
            key_strengths=["expertise"],
            improvement_areas=[],
            reasoning_analysis="Excellent reasoning"
        )
        test_db.add(eval2)
        test_db.commit()

        response = client.get(f"/api/v1/risks/evaluation/student/{sample_session.student_id}")

        data = response.json()["data"]
        assert len(data) == 2

    def test_student_evaluations_empty(self, client):
        """Test getting evaluations for student with none"""
        response = client.get("/api/v1/risks/evaluation/student/student-no-evals")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert len(data["data"]) == 0

    def test_student_evaluations_message(self, client, sample_session, sample_evaluation):
        """Test response message includes count"""
        response = client.get(f"/api/v1/risks/evaluation/student/{sample_session.student_id}")

        message = response.json()["message"]
        assert "1 evaluations" in message or "1 evaluation" in message


# ============================================================================
# Integration Tests
# ============================================================================

class TestRisksIntegration:
    """Integration tests for risks endpoints"""

    def test_risks_response_format_consistency(self, client, sample_session, sample_risks, sample_evaluation):
        """Test that all risk endpoints follow consistent format"""
        endpoints = [
            f"/api/v1/risks/session/{sample_session.id}",
            f"/api/v1/risks/student/{sample_session.student_id}",
            f"/api/v1/risks/student/{sample_session.student_id}/statistics",
            "/api/v1/risks/critical",
            f"/api/v1/risks/evaluation/session/{sample_session.id}",
            f"/api/v1/risks/evaluation/student/{sample_session.student_id}"
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()

            assert "success" in data
            assert "data" in data
            assert "message" in data

    def test_risk_evidence_and_traces_preserved(self, client, sample_session, sample_risks):
        """Test that risk evidence and trace IDs are preserved"""
        response = client.get(f"/api/v1/risks/session/{sample_session.id}")

        for risk in response.json()["data"]:
            assert isinstance(risk["evidence"], list)
            assert isinstance(risk["trace_ids"], list)
            assert len(risk["evidence"]) > 0

    def test_evaluation_dimensions_structure(self, client, sample_session, sample_evaluation):
        """Test evaluation dimensions are properly structured"""
        response = client.get(f"/api/v1/risks/evaluation/session/{sample_session.id}")

        dimensions = response.json()["data"]["dimensions"]

        assert isinstance(dimensions, dict)
        assert "cognitive" in dimensions
        assert isinstance(dimensions["cognitive"], (int, float))