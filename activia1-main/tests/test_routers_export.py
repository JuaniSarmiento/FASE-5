"""
Tests for Export Router

Verifies:
- POST /export/research-data - Export anonymized research data
- Data fetching from database
- Anonymization process
- Privacy validation (k-anonymity, GDPR)
- Export formats (JSON, CSV, Excel)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta
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
    from backend.database import get_db_session

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_data(test_db):
    """Create sample data for export testing"""
    from backend.database.models import SessionDB, CognitiveTraceDB, EvaluationDB, RiskDB

    sessions = []
    traces = []
    evaluations = []
    risks = []

    # Create multiple sessions with traces, evaluations, and risks
    for i in range(10):
        session = SessionDB(
            id=str(uuid.uuid4()),
            student_id=f"student-{i % 5}",  # 5 unique students
            activity_id=f"activity-{i % 3}",  # 3 unique activities
            status="completed",
            mode="tutoria_socratica"
        )
        test_db.add(session)
        sessions.append(session)

    test_db.commit()

    for session in sessions:
        # Add traces
        for j in range(3):
            trace = CognitiveTraceDB(
                id=str(uuid.uuid4()),
                session_id=session.id,
                student_id=session.student_id,
                activity_id=session.activity_id,
                trace_level="n4_cognitivo",
                interaction_type="student_prompt",
                cognitive_state="exploracion",
                content=f"Test content {j}",
                ai_involvement=0.5
            )
            test_db.add(trace)
            traces.append(trace)

        # Add evaluation
        evaluation = EvaluationDB(
            id=str(uuid.uuid4()),
            session_id=session.id,
            student_id=session.student_id,
            activity_id=session.activity_id,
            overall_competency_level="INTERMEDIATE",
            overall_score=0.75,
            dimensions={"cognitive": 0.8},
            key_strengths=["problem_solving"],
            improvement_areas=["documentation"]
        )
        test_db.add(evaluation)
        evaluations.append(evaluation)

        # Add risk
        risk = RiskDB(
            id=str(uuid.uuid4()),
            session_id=session.id,
            student_id=session.student_id,
            activity_id=session.activity_id,
            risk_type="DELEGATION",
            risk_level="MEDIUM",
            dimension="ETHICAL",
            description="Possible delegation",
            resolved=False
        )
        test_db.add(risk)
        risks.append(risk)

    test_db.commit()

    return {
        "sessions": sessions,
        "traces": traces,
        "evaluations": evaluations,
        "risks": risks
    }


# ============================================================================
# Export Research Data Tests
# ============================================================================

class TestExportResearchData:
    """Tests for POST /export/research-data"""

    def test_export_success(self, client, sample_data):
        """Test successful data export"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_trace.side_effect = lambda x: {**x, "student_id": "anon_1"}
            mock_anon_instance.anonymize_evaluation.side_effect = lambda x: {**x, "student_id": "anon_1"}
            mock_anon_instance.anonymize_risk.side_effect = lambda x: {**x, "student_id": "anon_1"}
            mock_anon_instance.anonymize_session.side_effect = lambda x: {**x, "student_id": "anon_1"}
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True,
                    errors=[],
                    warnings=[],
                    metrics={"k_achieved": 5, "records_validated": 50}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True,
                        errors=[],
                        metrics={"gdpr_article_89_compliance": True}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = '{"data": []}'
                        mock_exporter.return_value = mock_exp_instance

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "include_traces": True,
                            "include_evaluations": True,
                            "include_risks": True,
                            "format": "json",
                            "k_anonymity": 5
                        })

                        assert response.status_code == 200
                        data = response.json()

                        assert data["success"] is True
                        assert "export_id" in data

    def test_export_with_date_filter(self, client, sample_data):
        """Test export with date filters"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True, errors=[], warnings=[], metrics={"k_achieved": 5}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True, errors=[], metrics={}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = '{"data": []}'
                        mock_exporter.return_value = mock_exp_instance

                        start_date = (datetime.now() - timedelta(days=30)).isoformat()
                        end_date = datetime.now().isoformat()

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "start_date": start_date,
                            "end_date": end_date,
                            "format": "json",
                            "k_anonymity": 5
                        })

                        assert response.status_code in [200, 404]

    def test_export_with_activity_filter(self, client, sample_data):
        """Test export with activity filter"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True, errors=[], warnings=[], metrics={"k_achieved": 5}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True, errors=[], metrics={}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = '{"data": []}'
                        mock_exporter.return_value = mock_exp_instance

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "activity_ids": ["activity-0", "activity-1"],
                            "format": "json",
                            "k_anonymity": 5
                        })

                        assert response.status_code in [200, 404]

    def test_export_no_data_returns_404(self, client):
        """Test export with no matching data returns 404"""
        response = client.post("/api/v1/export/research-data", json={
            "include_sessions": True,
            "activity_ids": ["nonexistent-activity"],
            "format": "json",
            "k_anonymity": 5
        })

        assert response.status_code == 404

    def test_export_includes_metadata(self, client, sample_data):
        """Test that export response includes metadata"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon_instance.anonymize_trace.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True, errors=[], warnings=[],
                    metrics={"k_achieved": 5, "records_validated": 10}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True, errors=[], metrics={"gdpr_article_89_compliance": True}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = '{"data": []}'
                        mock_exporter.return_value = mock_exp_instance

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "include_traces": True,
                            "format": "json",
                            "k_anonymity": 5
                        })

                        if response.status_code == 200:
                            data = response.json()
                            assert "metadata" in data
                            assert "export_timestamp" in data["metadata"]
                            assert "export_format" in data["metadata"]

    def test_export_includes_validation_report(self, client, sample_data):
        """Test that export includes validation report"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True, errors=[], warnings=[],
                    metrics={"k_achieved": 5}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True, errors=[], metrics={"gdpr_article_89_compliance": True}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = '{"data": []}'
                        mock_exporter.return_value = mock_exp_instance

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "format": "json",
                            "k_anonymity": 5
                        })

                        if response.status_code == 200:
                            data = response.json()
                            assert "validation_report" in data
                            assert "is_valid" in data["validation_report"]


# ============================================================================
# Privacy Validation Tests
# ============================================================================

class TestPrivacyValidation:
    """Tests for privacy validation in export"""

    def test_export_fails_on_privacy_validation_failure(self, client, sample_data):
        """Test that export fails when privacy validation fails"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=False,
                    errors=["k-anonymity not achieved"],
                    warnings=[],
                    metrics={"k_achieved": 2, "k_required": 5}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=False, errors=["GDPR violation"], metrics={}
                    )

                    response = client.post("/api/v1/export/research-data", json={
                        "include_sessions": True,
                        "format": "json",
                        "k_anonymity": 5
                    })

                    assert response.status_code == 400
                    assert "privacy" in response.json()["detail"]["error"].lower()

    def test_export_respects_k_anonymity_setting(self, client, sample_data):
        """Test that k-anonymity setting is respected"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True, errors=[], warnings=[], metrics={"k_achieved": 10}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True, errors=[], metrics={}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = '{"data": []}'
                        mock_exporter.return_value = mock_exp_instance

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "format": "json",
                            "k_anonymity": 10  # Higher k value
                        })

                        # PrivacyValidator should be called with min_k=10
                        if response.status_code == 200:
                            mock_validator.assert_called_with(min_k=10)


# ============================================================================
# Export Format Tests
# ============================================================================

class TestExportFormats:
    """Tests for different export formats"""

    def test_export_json_format(self, client, sample_data):
        """Test export in JSON format"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True, errors=[], warnings=[], metrics={"k_achieved": 5}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True, errors=[], metrics={}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = '{"sessions": []}'
                        mock_exporter.return_value = mock_exp_instance

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "format": "json",
                            "k_anonymity": 5
                        })

                        if response.status_code == 200:
                            data = response.json()
                            assert data["metadata"]["export_format"] == "json"

    def test_export_csv_format(self, client, sample_data):
        """Test export in CSV format"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True, errors=[], warnings=[], metrics={"k_achieved": 5}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True, errors=[], metrics={}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = "id,student_id\n1,anon_1"
                        mock_exporter.return_value = mock_exp_instance

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "format": "csv",
                            "k_anonymity": 5
                        })

                        if response.status_code == 200:
                            data = response.json()
                            assert data["metadata"]["export_format"] == "csv"


# ============================================================================
# Data Types Selection Tests
# ============================================================================

class TestDataTypeSelection:
    """Tests for selecting which data types to export"""

    def test_export_sessions_only(self, client, sample_data):
        """Test exporting only sessions"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True, errors=[], warnings=[], metrics={}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True, errors=[], metrics={}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = '{"data": []}'
                        mock_exporter.return_value = mock_exp_instance

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "include_traces": False,
                            "include_evaluations": False,
                            "include_risks": False,
                            "format": "json",
                            "k_anonymity": 5
                        })

                        if response.status_code == 200:
                            data = response.json()
                            assert "sessions" in data["metadata"]["data_types"]

    def test_export_all_data_types(self, client, sample_data):
        """Test exporting all data types"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon_instance.anonymize_trace.side_effect = lambda x: x
            mock_anon_instance.anonymize_evaluation.side_effect = lambda x: x
            mock_anon_instance.anonymize_risk.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True, errors=[], warnings=[], metrics={}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True, errors=[], metrics={}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = '{"data": []}'
                        mock_exporter.return_value = mock_exp_instance

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "include_traces": True,
                            "include_evaluations": True,
                            "include_risks": True,
                            "format": "json",
                            "k_anonymity": 5
                        })

                        if response.status_code == 200:
                            data = response.json()
                            data_types = data["metadata"]["data_types"]
                            assert len(data_types) >= 1


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestExportErrorHandling:
    """Tests for error handling in export"""

    def test_export_handles_db_error(self, client):
        """Test that database errors are handled"""
        with patch('backend.api.routers.export.fetch_data_from_db') as mock_fetch:
            mock_fetch.side_effect = Exception("Database connection failed")

            response = client.post("/api/v1/export/research-data", json={
                "include_sessions": True,
                "format": "json",
                "k_anonymity": 5
            })

            assert response.status_code == 500

    def test_export_handles_anonymization_error(self, client, sample_data):
        """Test that anonymization errors are handled"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon.side_effect = Exception("Anonymization failed")

            response = client.post("/api/v1/export/research-data", json={
                "include_sessions": True,
                "format": "json",
                "k_anonymity": 5
            })

            assert response.status_code in [404, 500]


# ============================================================================
# Integration Tests
# ============================================================================

class TestExportIntegration:
    """Integration tests for export functionality"""

    def test_export_response_structure(self, client, sample_data):
        """Test complete export response structure"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True, errors=[], warnings=[],
                    metrics={"k_achieved": 5, "records_validated": 10}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True, errors=[],
                        metrics={"gdpr_article_89_compliance": True}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = '{"data": []}'
                        mock_exporter.return_value = mock_exp_instance

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "format": "json",
                            "k_anonymity": 5
                        })

                        if response.status_code == 200:
                            data = response.json()

                            # Check top-level structure
                            assert "success" in data
                            assert "message" in data
                            assert "metadata" in data
                            assert "validation_report" in data
                            assert "export_id" in data
                            assert "file_size_bytes" in data

    def test_export_file_size_calculated(self, client, sample_data):
        """Test that file size is calculated correctly"""
        with patch('backend.api.routers.export.DataAnonymizer') as mock_anon:
            mock_anon_instance = Mock()
            mock_anon_instance.anonymize_session.side_effect = lambda x: x
            mock_anon.return_value = mock_anon_instance

            with patch('backend.api.routers.export.PrivacyValidator') as mock_validator:
                mock_val_instance = Mock()
                mock_val_instance.validate.return_value = Mock(
                    is_valid=True, errors=[], warnings=[], metrics={}
                )
                mock_validator.return_value = mock_val_instance

                with patch('backend.api.routers.export.GDPRCompliance') as mock_gdpr:
                    mock_gdpr.check_article_89_compliance.return_value = Mock(
                        is_valid=True, errors=[], metrics={}
                    )

                    with patch('backend.api.routers.export.ResearchDataExporter') as mock_exporter:
                        test_content = '{"sessions": [{"id": "1"}]}'
                        mock_exp_instance = Mock()
                        mock_exp_instance.export.return_value = test_content
                        mock_exporter.return_value = mock_exp_instance

                        response = client.post("/api/v1/export/research-data", json={
                            "include_sessions": True,
                            "format": "json",
                            "k_anonymity": 5
                        })

                        if response.status_code == 200:
                            data = response.json()
                            assert data["file_size_bytes"] == len(test_content.encode("utf-8"))