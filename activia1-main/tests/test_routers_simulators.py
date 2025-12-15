"""
Tests for Simulators Router (S-IA-X)

Verifies:
- GET /simulators - List available simulators
- POST /simulators/interact - Main simulator interaction
- GET /simulators/{type} - Get simulator info
- POST /simulators/interview/* - Technical interview flow (Sprint 6)
- POST /simulators/incident/* - Incident simulation flow (Sprint 6)
- POST /simulators/scrum/daily-standup - Scrum Master interaction
- POST /simulators/client/* - Client interaction
- POST /simulators/security/audit - Security audit (DSO-IA)
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
from backend.api.deps import get_db, get_llm_provider


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
def mock_llm_provider():
    """Create mock LLM provider for simulator tests"""
    mock_provider = Mock()
    mock_provider.generate.return_value = {
        "content": "Mock response from LLM",
        "usage": {"prompt_tokens": 10, "completion_tokens": 20}
    }
    return mock_provider


@pytest.fixture(scope="function")
def client(test_db, mock_llm_provider):
    """Create test client with database and LLM mocks"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    def override_get_llm():
        return mock_llm_provider

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_llm_provider] = override_get_llm

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_session(test_db):
    """Create a sample active session for testing"""
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
def inactive_session(test_db):
    """Create an inactive session for testing"""
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


# ============================================================================
# List Simulators Tests
# ============================================================================

class TestListSimulators:
    """Tests for GET /simulators endpoint"""

    def test_list_simulators_success(self, client):
        """Test listing all available simulators"""
        response = client.get("/api/v1/simulators")

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert "data" in data
        assert len(data["data"]) == 6  # 6 simulators

    def test_list_simulators_includes_all_types(self, client):
        """Test that list includes all simulator types"""
        response = client.get("/api/v1/simulators")

        simulators = response.json()["data"]
        types = [s["type"] for s in simulators]

        expected_types = [
            "product_owner",
            "scrum_master",
            "tech_interviewer",
            "incident_responder",
            "client",
            "devsecops"
        ]

        for expected in expected_types:
            assert expected in types

    def test_list_simulators_has_required_fields(self, client):
        """Test that each simulator has required fields"""
        response = client.get("/api/v1/simulators")

        for simulator in response.json()["data"]:
            assert "type" in simulator
            assert "name" in simulator
            assert "description" in simulator
            assert "competencies" in simulator
            assert "status" in simulator

    def test_list_simulators_shows_status(self, client):
        """Test that simulators show active/development status"""
        response = client.get("/api/v1/simulators")

        statuses = [s["status"] for s in response.json()["data"]]

        # At least some should be active
        assert "active" in statuses

    def test_list_simulators_message_includes_count(self, client):
        """Test response message includes count"""
        response = client.get("/api/v1/simulators")

        data = response.json()
        assert "6 simuladores" in data["message"]


# ============================================================================
# Get Simulator Info Tests
# ============================================================================

class TestGetSimulatorInfo:
    """Tests for GET /simulators/{type} endpoint"""

    def test_get_product_owner_info(self, client):
        """Test getting Product Owner simulator info"""
        response = client.get("/api/v1/simulators/product_owner")

        assert response.status_code == 200
        data = response.json()["data"]

        assert data["type"] == "product_owner"
        assert "PO-IA" in data["name"]
        assert "comunicacion_tecnica" in data["competencies"]

    def test_get_scrum_master_info(self, client):
        """Test getting Scrum Master simulator info"""
        response = client.get("/api/v1/simulators/scrum_master")

        assert response.status_code == 200
        data = response.json()["data"]

        assert data["type"] == "scrum_master"
        assert "SM-IA" in data["name"]

    def test_get_tech_interviewer_info(self, client):
        """Test getting Tech Interviewer simulator info"""
        response = client.get("/api/v1/simulators/tech_interviewer")

        assert response.status_code == 200
        data = response.json()["data"]

        assert data["type"] == "tech_interviewer"
        assert "IT-IA" in data["name"]

    def test_get_devsecops_info(self, client):
        """Test getting DevSecOps simulator info"""
        response = client.get("/api/v1/simulators/devsecops")

        assert response.status_code == 200
        data = response.json()["data"]

        assert data["type"] == "devsecops"
        assert "DSO-IA" in data["name"]
        assert "seguridad" in data["competencies"]

    def test_get_simulator_includes_example_questions(self, client):
        """Test that active simulators have example questions"""
        response = client.get("/api/v1/simulators/product_owner")

        data = response.json()["data"]
        assert "example_questions" in data
        assert len(data["example_questions"]) > 0

    def test_get_invalid_simulator_type(self, client):
        """Test getting non-existent simulator returns 422"""
        response = client.get("/api/v1/simulators/invalid_type")

        # FastAPI returns 422 for invalid enum values
        assert response.status_code == 422


# ============================================================================
# Simulator Interaction Tests
# ============================================================================

class TestSimulatorInteraction:
    """Tests for POST /simulators/interact endpoint"""

    def test_interact_success(self, client, sample_session):
        """Test successful simulator interaction"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.interact.return_value = {
                "message": "Response from simulator",
                "role": "product_owner",
                "expects": ["clarification"],
                "metadata": {"competencies_evaluated": ["comunicacion_tecnica"]}
            }
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/interact", json={
                "session_id": sample_session.id,
                "simulator_type": "product_owner",
                "prompt": "This is a test interaction with the simulator for testing purposes"
            })

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert "data" in data
            assert data["data"]["simulator_type"] == "product_owner"

    def test_interact_creates_traces(self, client, sample_session, test_db):
        """Test that interaction creates input and output traces"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.interact.return_value = {
                "message": "Simulator response",
                "role": "product_owner",
                "expects": [],
                "metadata": {}
            }
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/interact", json={
                "session_id": sample_session.id,
                "simulator_type": "product_owner",
                "prompt": "Test prompt for creating traces in the system"
            })

            assert response.status_code == 200
            data = response.json()["data"]

            # Should have both trace IDs
            assert "trace_id_input" in data
            assert "trace_id_output" in data

    def test_interact_session_not_found(self, client):
        """Test interaction with non-existent session"""
        response = client.post("/api/v1/simulators/interact", json={
            "session_id": "nonexistent-session-id",
            "simulator_type": "product_owner",
            "prompt": "This should fail because session doesn't exist"
        })

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_interact_inactive_session(self, client, inactive_session):
        """Test interaction with inactive session"""
        response = client.post("/api/v1/simulators/interact", json={
            "session_id": inactive_session.id,
            "simulator_type": "product_owner",
            "prompt": "This should fail because session is not active"
        })

        assert response.status_code == 400
        assert "not active" in response.json()["detail"].lower()

    def test_interact_prompt_too_short(self, client, sample_session):
        """Test interaction with prompt that's too short"""
        response = client.post("/api/v1/simulators/interact", json={
            "session_id": sample_session.id,
            "simulator_type": "product_owner",
            "prompt": "short"  # Less than min_length=10
        })

        assert response.status_code == 422

    def test_interact_with_context(self, client, sample_session):
        """Test interaction with additional context"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.interact.return_value = {
                "message": "Response with context",
                "role": "product_owner",
                "expects": [],
                "metadata": {}
            }
            mock_agent.return_value = mock_instance

            context = {"activity": "test_activity", "iteration": 1}

            response = client.post("/api/v1/simulators/interact", json={
                "session_id": sample_session.id,
                "simulator_type": "product_owner",
                "prompt": "Test with context that should be passed to the simulator",
                "context": context
            })

            assert response.status_code == 200

            # Verify context was passed to simulator
            call_args = mock_instance.interact.call_args
            assert call_args.kwargs.get("context") == context

    def test_interact_returns_competencies(self, client, sample_session):
        """Test that interaction returns evaluated competencies"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.interact.return_value = {
                "message": "Response",
                "role": "product_owner",
                "expects": ["justificacion"],
                "metadata": {
                    "competencies_evaluated": ["comunicacion_tecnica", "analisis_requisitos"]
                }
            }
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/interact", json={
                "session_id": sample_session.id,
                "simulator_type": "product_owner",
                "prompt": "Test prompt for checking competencies evaluation"
            })

            data = response.json()["data"]
            assert "competencies_evaluated" in data
            assert "comunicacion_tecnica" in data["competencies_evaluated"]


# ============================================================================
# Daily Standup Tests (SM-IA)
# ============================================================================

class TestDailyStandup:
    """Tests for POST /simulators/scrum/daily-standup"""

    def test_daily_standup_success(self, client, sample_session):
        """Test successful daily standup"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.procesar_daily_standup.return_value = {
                "feedback": "Good standup summary",
                "questions": ["Any blockers?"],
                "detected_issues": [],
                "suggestions": ["Keep updates brief"]
            }
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/scrum/daily-standup", json={
                "session_id": sample_session.id,
                "student_id": "test-student",
                "what_did_yesterday": "Completed the authentication module",
                "what_will_do_today": "Start working on API endpoints",
                "impediments": "None"
            })

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert "feedback" in data["data"]

    def test_daily_standup_detects_issues(self, client, sample_session):
        """Test that daily standup detects issues"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.procesar_daily_standup.return_value = {
                "feedback": "Some issues detected",
                "questions": [],
                "detected_issues": ["scope_creep", "unclear_task"],
                "suggestions": ["Focus on sprint goals"]
            }
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/scrum/daily-standup", json={
                "session_id": sample_session.id,
                "student_id": "test-student",
                "what_did_yesterday": "Worked on many things and also added extra features",
                "what_will_do_today": "Continue with everything",
                "impediments": "Maybe something"
            })

            data = response.json()["data"]
            assert len(data["detected_issues"]) > 0

    def test_daily_standup_session_not_found(self, client):
        """Test daily standup with invalid session"""
        response = client.post("/api/v1/simulators/scrum/daily-standup", json={
            "session_id": "invalid-session",
            "student_id": "test-student",
            "what_did_yesterday": "Something",
            "what_will_do_today": "Something else",
            "impediments": "None"
        })

        assert response.status_code == 404


# ============================================================================
# Client Simulator Tests (CX-IA)
# ============================================================================

class TestClientSimulator:
    """Tests for /simulators/client/* endpoints"""

    def test_get_client_requirements(self, client, sample_session):
        """Test getting client requirements"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.generar_requerimientos_cliente.return_value = {
                "requirements": "I need a system that does everything",
                "additional_requirements": None
            }
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/client/requirements", json={
                "session_id": sample_session.id,
                "student_id": "test-student",
                "project_type": "web_application"
            })

            assert response.status_code == 200
            data = response.json()["data"]

            assert "response" in data
            assert "evaluation" in data

    def test_ask_client_clarification(self, client, sample_session):
        """Test asking clarification from client"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.responder_clarificacion.return_value = {
                "response": "Let me explain further...",
                "additional_requirements": "Also needs reporting",
                "soft_skills": {
                    "empathy": 0.8,
                    "clarity": 0.7,
                    "professionalism": 0.9
                }
            }
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/client/clarify", json={
                "session_id": sample_session.id,
                "question": "Could you clarify what you mean by 'does everything'?"
            })

            assert response.status_code == 200
            data = response.json()["data"]

            assert "evaluation" in data
            assert "empathy" in data["evaluation"]

    def test_client_requirements_session_not_found(self, client):
        """Test client requirements with invalid session"""
        response = client.post("/api/v1/simulators/client/requirements", json={
            "session_id": "invalid-session",
            "student_id": "test-student",
            "project_type": "web_application"
        })

        assert response.status_code == 404


# ============================================================================
# Security Audit Tests (DSO-IA)
# ============================================================================

class TestSecurityAudit:
    """Tests for POST /simulators/security/audit"""

    def test_security_audit_success(self, client, sample_session):
        """Test successful security audit"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.auditar_seguridad.return_value = {
                "vulnerabilities": [
                    {
                        "severity": "HIGH",
                        "vulnerability_type": "SQL_INJECTION",
                        "line_number": 10,
                        "description": "SQL injection vulnerability",
                        "recommendation": "Use parameterized queries"
                    }
                ],
                "total_vulnerabilities": 1,
                "critical_count": 0,
                "high_count": 1,
                "medium_count": 0,
                "low_count": 0,
                "security_score": 7.0,
                "recommendations": ["Use prepared statements"],
                "owasp_compliant": False
            }
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/security/audit", json={
                "session_id": sample_session.id,
                "student_id": "test-student",
                "code": "SELECT * FROM users WHERE id = '" + "user_input" + "'",
                "language": "python"
            })

            assert response.status_code == 200
            data = response.json()["data"]

            assert data["total_vulnerabilities"] == 1
            assert len(data["vulnerabilities"]) == 1
            assert data["vulnerabilities"][0]["severity"] == "HIGH"

    def test_security_audit_clean_code(self, client, sample_session):
        """Test security audit on clean code"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.auditar_seguridad.return_value = {
                "vulnerabilities": [],
                "total_vulnerabilities": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "security_score": 10.0,
                "recommendations": [],
                "owasp_compliant": True
            }
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/security/audit", json={
                "session_id": sample_session.id,
                "student_id": "test-student",
                "code": "def hello():\n    print('Hello World')",
                "language": "python"
            })

            data = response.json()["data"]

            assert data["total_vulnerabilities"] == 0
            assert data["overall_security_score"] == 10.0
            assert data["compliant_with_owasp"] is True

    def test_security_audit_returns_audit_id(self, client, sample_session):
        """Test that security audit returns audit ID"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.auditar_seguridad.return_value = {
                "vulnerabilities": [],
                "total_vulnerabilities": 0,
                "critical_count": 0,
                "high_count": 0,
                "medium_count": 0,
                "low_count": 0,
                "security_score": 10.0,
                "recommendations": [],
                "owasp_compliant": True
            }
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/security/audit", json={
                "session_id": sample_session.id,
                "student_id": "test-student",
                "code": "print('test')",
                "language": "python"
            })

            data = response.json()["data"]
            assert "audit_id" in data
            assert data["audit_id"].startswith("audit_")

    def test_security_audit_session_not_found(self, client):
        """Test security audit with invalid session"""
        response = client.post("/api/v1/simulators/security/audit", json={
            "session_id": "invalid-session",
            "student_id": "test-student",
            "code": "print('test')",
            "language": "python"
        })

        assert response.status_code == 404


# ============================================================================
# Interview Simulator Tests (IT-IA) - Sprint 6
# ============================================================================

class TestInterviewSimulator:
    """Tests for /simulators/interview/* endpoints"""

    def test_start_interview(self, client, sample_session):
        """Test starting a technical interview"""
        with patch('backend.api.routers.simulators.LLMProviderFactory') as mock_factory:
            mock_llm = Mock()
            mock_factory.create_from_env.return_value = mock_llm

            with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
                mock_instance = Mock()
                mock_instance.generar_pregunta_entrevista.return_value = "What is Big O notation?"
                mock_agent.return_value = mock_instance

                with patch('backend.api.routers.simulators.InterviewSessionRepository') as mock_repo:
                    mock_interview = Mock()
                    mock_interview.id = "interview-123"
                    mock_interview.session_id = sample_session.id
                    mock_interview.student_id = "test-student"
                    mock_interview.interview_type = "CONCEPTUAL"
                    mock_interview.difficulty_level = "MEDIUM"
                    mock_interview.questions_asked = []
                    mock_interview.responses = []
                    mock_interview.created_at = datetime.now()
                    mock_interview.updated_at = datetime.now()

                    mock_repo_instance = Mock()
                    mock_repo_instance.create.return_value = mock_interview
                    mock_repo_instance.add_question.return_value = mock_interview
                    mock_repo.return_value = mock_repo_instance

                    response = client.post("/api/v1/simulators/interview/start", json={
                        "session_id": sample_session.id,
                        "student_id": "test-student",
                        "interview_type": "CONCEPTUAL",
                        "difficulty_level": "MEDIUM"
                    })

                    assert response.status_code == 200

    def test_get_interview_not_found(self, client):
        """Test getting non-existent interview"""
        with patch('backend.api.routers.simulators.InterviewSessionRepository') as mock_repo:
            mock_repo_instance = Mock()
            mock_repo_instance.get_by_id.return_value = None
            mock_repo.return_value = mock_repo_instance

            response = client.get("/api/v1/simulators/interview/nonexistent-id")

            assert response.status_code == 404


# ============================================================================
# Incident Simulator Tests (IR-IA) - Sprint 6
# ============================================================================

class TestIncidentSimulator:
    """Tests for /simulators/incident/* endpoints"""

    def test_start_incident(self, client, sample_session):
        """Test starting an incident simulation"""
        with patch('backend.api.routers.simulators.LLMProviderFactory') as mock_factory:
            mock_llm = Mock()
            mock_factory.create_from_env.return_value = mock_llm

            with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
                mock_instance = Mock()
                mock_instance.generar_incidente.return_value = {
                    "description": "Database connection timeout",
                    "logs": "ERROR: Connection refused",
                    "metrics": {"cpu": 95, "memory": 80}
                }
                mock_agent.return_value = mock_instance

                with patch('backend.api.routers.simulators.IncidentSimulationRepository') as mock_repo:
                    mock_incident = Mock()
                    mock_incident.id = "incident-123"
                    mock_incident.session_id = sample_session.id
                    mock_incident.student_id = "test-student"
                    mock_incident.incident_type = "DATABASE_OUTAGE"
                    mock_incident.severity = "HIGH"
                    mock_incident.incident_description = "Database timeout"
                    mock_incident.simulated_logs = "ERROR logs"
                    mock_incident.simulated_metrics = {"cpu": 95}
                    mock_incident.diagnosis_process = []
                    mock_incident.created_at = datetime.now()
                    mock_incident.updated_at = datetime.now()

                    mock_repo_instance = Mock()
                    mock_repo_instance.create.return_value = mock_incident
                    mock_repo.return_value = mock_repo_instance

                    response = client.post("/api/v1/simulators/incident/start", json={
                        "session_id": sample_session.id,
                        "student_id": "test-student",
                        "incident_type": "DATABASE_OUTAGE",
                        "severity": "HIGH"
                    })

                    assert response.status_code == 200

    def test_get_incident_not_found(self, client):
        """Test getting non-existent incident"""
        with patch('backend.api.routers.simulators.IncidentSimulationRepository') as mock_repo:
            mock_repo_instance = Mock()
            mock_repo_instance.get_by_id.return_value = None
            mock_repo.return_value = mock_repo_instance

            response = client.get("/api/v1/simulators/incident/nonexistent-id")

            assert response.status_code == 404


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestSimulatorErrorHandling:
    """Tests for error handling in simulator endpoints"""

    def test_interact_handles_agent_error(self, client, sample_session):
        """Test that agent errors are handled gracefully"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_agent.side_effect = RuntimeError("Agent initialization failed")

            response = client.post("/api/v1/simulators/interact", json={
                "session_id": sample_session.id,
                "simulator_type": "product_owner",
                "prompt": "This should trigger an error in the agent"
            })

            assert response.status_code == 500

    def test_daily_standup_handles_error(self, client, sample_session):
        """Test daily standup error handling"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.procesar_daily_standup.side_effect = Exception("Processing failed")
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/scrum/daily-standup", json={
                "session_id": sample_session.id,
                "student_id": "test-student",
                "what_did_yesterday": "Something",
                "what_will_do_today": "Something else",
                "impediments": "None"
            })

            assert response.status_code == 500

    def test_security_audit_handles_error(self, client, sample_session):
        """Test security audit error handling"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.auditar_seguridad.side_effect = Exception("Audit failed")
            mock_agent.return_value = mock_instance

            response = client.post("/api/v1/simulators/security/audit", json={
                "session_id": sample_session.id,
                "student_id": "test-student",
                "code": "print('test')",
                "language": "python"
            })

            assert response.status_code == 500


# ============================================================================
# Integration Tests
# ============================================================================

class TestSimulatorIntegration:
    """Integration tests for simulator endpoints"""

    def test_full_interaction_flow(self, client, sample_session):
        """Test complete interaction flow with traces"""
        with patch('backend.api.routers.simulators.SimuladorProfesionalAgent') as mock_agent:
            mock_instance = Mock()
            mock_instance.interact.return_value = {
                "message": "PO Response",
                "role": "product_owner",
                "expects": ["clarification"],
                "metadata": {"competencies_evaluated": ["comunicacion"]}
            }
            mock_agent.return_value = mock_instance

            # First interaction
            response1 = client.post("/api/v1/simulators/interact", json={
                "session_id": sample_session.id,
                "simulator_type": "product_owner",
                "prompt": "I want to implement a queue using circular array"
            })

            assert response1.status_code == 200
            data1 = response1.json()["data"]

            # Verify traces were created
            assert data1["trace_id_input"] is not None
            assert data1["trace_id_output"] is not None

    def test_all_simulator_types_accessible(self, client):
        """Test that all simulator types can be queried"""
        types = [
            "product_owner",
            "scrum_master",
            "tech_interviewer",
            "incident_responder",
            "client",
            "devsecops"
        ]

        for sim_type in types:
            response = client.get(f"/api/v1/simulators/{sim_type}")
            assert response.status_code == 200, f"Failed for {sim_type}"

    def test_response_format_consistency(self, client):
        """Test that all responses follow API response format"""
        # List simulators
        response = client.get("/api/v1/simulators")
        data = response.json()

        assert "success" in data
        assert "data" in data
        assert "message" in data

        # Get specific simulator
        response = client.get("/api/v1/simulators/product_owner")
        data = response.json()

        assert "success" in data
        assert "data" in data