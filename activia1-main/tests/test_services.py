"""
Tests for Service Layer components

Verifies:
- CourseReportGenerator: cohort summary, risk dashboard, report export
- InstitutionalRiskManager: alert scanning, remediation plans, alert lifecycle
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_db_session():
    """Create a mock SQLAlchemy session"""
    session = Mock(spec=Session)
    session.query = Mock(return_value=Mock())
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    return session


@pytest.fixture
def mock_report_repo():
    """Mock CourseReportRepository"""
    repo = Mock()
    repo.create = Mock()
    repo.get_by_id = Mock(return_value=None)
    repo.mark_exported = Mock()
    return repo


@pytest.fixture
def mock_alert_repo():
    """Mock RiskAlertRepository"""
    repo = Mock()
    repo.create = Mock()
    repo.assign_to = Mock()
    repo.acknowledge = Mock()
    repo.resolve = Mock()
    repo.get_by_id = Mock()
    return repo


@pytest.fixture
def mock_plan_repo():
    """Mock RemediationPlanRepository"""
    repo = Mock()
    repo.create = Mock()
    repo.get_by_id = Mock()
    repo.update_status = Mock()
    return repo


@pytest.fixture
def mock_risk_repo():
    """Mock RiskRepository"""
    repo = Mock()
    repo.get_by_student = Mock(return_value=[])
    repo.get_by_session = Mock(return_value=[])
    return repo


# ============================================================================
# CourseReportGenerator Tests
# ============================================================================

class TestCourseReportGenerator:
    """Tests for CourseReportGenerator service"""

    def test_init_with_dependencies(self, mock_db_session, mock_report_repo):
        """Test CourseReportGenerator initialization"""
        from backend.services.course_report_generator import CourseReportGenerator

        generator = CourseReportGenerator(
            db_session=mock_db_session,
            report_repository=mock_report_repo
        )

        assert generator.db == mock_db_session
        assert generator.report_repo == mock_report_repo

    def test_generate_cohort_summary_empty_cohort(
        self,
        mock_db_session,
        mock_report_repo
    ):
        """Test generating report for empty cohort"""
        from backend.services.course_report_generator import CourseReportGenerator

        # Setup mock to return empty results
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.count = Mock(return_value=0)
        mock_query.scalar = Mock(return_value=0.0)
        mock_query.group_by = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[])
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=None)
        mock_query.limit = Mock(return_value=mock_query)
        mock_db_session.query = Mock(return_value=mock_query)

        # Setup report repo to return mock report
        mock_report = Mock()
        mock_report.id = str(uuid4())
        mock_report_repo.create = Mock(return_value=mock_report)

        generator = CourseReportGenerator(
            db_session=mock_db_session,
            report_repository=mock_report_repo
        )

        result = generator.generate_cohort_summary(
            course_id="PROG2_2025_1C",
            teacher_id="teacher_001",
            student_ids=[],
            period_start=datetime(2025, 1, 1, tzinfo=timezone.utc),
            period_end=datetime(2025, 6, 30, tzinfo=timezone.utc)
        )

        assert result is not None
        assert result["course_id"] == "PROG2_2025_1C"
        mock_report_repo.create.assert_called_once()

    def test_generate_cohort_summary_with_students(
        self,
        mock_db_session,
        mock_report_repo
    ):
        """Test generating report with students"""
        from backend.services.course_report_generator import CourseReportGenerator

        # Setup complex mock chain
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.count = Mock(return_value=10)
        mock_query.scalar = Mock(return_value=0.45)
        mock_query.group_by = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[])
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=None)
        mock_query.limit = Mock(return_value=mock_query)
        mock_db_session.query = Mock(return_value=mock_query)

        mock_report = Mock()
        mock_report.id = str(uuid4())
        mock_report_repo.create = Mock(return_value=mock_report)

        generator = CourseReportGenerator(
            db_session=mock_db_session,
            report_repository=mock_report_repo
        )

        student_ids = [f"student_{i:03d}" for i in range(5)]

        result = generator.generate_cohort_summary(
            course_id="PROG2_2025_1C",
            teacher_id="teacher_001",
            student_ids=student_ids,
            period_start=datetime(2025, 1, 1, tzinfo=timezone.utc),
            period_end=datetime(2025, 6, 30, tzinfo=timezone.utc)
        )

        assert result is not None
        assert "summary_stats" in result
        assert "competency_distribution" in result
        assert "risk_distribution" in result
        assert "institutional_recommendations" in result

    def test_generate_risk_dashboard(self, mock_db_session, mock_report_repo):
        """Test generating risk dashboard"""
        from backend.services.course_report_generator import CourseReportGenerator

        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.count = Mock(return_value=5)
        mock_query.scalar = Mock(return_value=0.6)
        mock_query.group_by = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[])
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=None)
        mock_query.limit = Mock(return_value=mock_query)
        mock_db_session.query = Mock(return_value=mock_query)

        mock_report = Mock()
        mock_report.id = str(uuid4())
        mock_report_repo.create = Mock(return_value=mock_report)

        generator = CourseReportGenerator(
            db_session=mock_db_session,
            report_repository=mock_report_repo
        )

        result = generator.generate_risk_dashboard(
            course_id="PROG2_2025_1C",
            teacher_id="teacher_001",
            student_ids=["student_001", "student_002"],
            period_start=datetime(2025, 1, 1, tzinfo=timezone.utc),
            period_end=datetime(2025, 6, 30, tzinfo=timezone.utc)
        )

        assert result is not None
        assert "risk_distribution" in result
        assert "dimension_distribution" in result
        assert "top_risks" in result

    def test_export_report_to_json(self, mock_db_session, mock_report_repo, tmp_path):
        """Test exporting report to JSON file"""
        from backend.services.course_report_generator import CourseReportGenerator

        # Create mock report
        mock_report = Mock()
        mock_report.id = "report_123"
        mock_report.course_id = "PROG2_2025_1C"
        mock_report.teacher_id = "teacher_001"
        mock_report.report_type = "cohort_summary"
        mock_report.period_start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        mock_report.period_end = datetime(2025, 6, 30, tzinfo=timezone.utc)
        mock_report.created_at = datetime.now(timezone.utc)
        mock_report.summary_stats = {"total_students": 10}
        mock_report.competency_distribution = {"BASICO": 2}
        mock_report.risk_distribution = {"LOW": 5}
        mock_report.top_risks = []
        mock_report.student_summaries = []
        mock_report.institutional_recommendations = ["Recommendation 1"]
        mock_report.at_risk_students = []

        mock_report_repo.get_by_id = Mock(return_value=mock_report)

        generator = CourseReportGenerator(
            db_session=mock_db_session,
            report_repository=mock_report_repo
        )

        output_path = str(tmp_path / "report.json")
        result = generator.export_report_to_json("report_123", output_path)

        assert result == output_path
        mock_report_repo.mark_exported.assert_called_once_with("report_123", output_path)

    def test_export_report_not_found(self, mock_db_session, mock_report_repo):
        """Test export with non-existent report"""
        from backend.services.course_report_generator import CourseReportGenerator

        mock_report_repo.get_by_id = Mock(return_value=None)

        generator = CourseReportGenerator(
            db_session=mock_db_session,
            report_repository=mock_report_repo
        )

        with pytest.raises(ValueError, match="not found"):
            generator.export_report_to_json("non_existent", "/tmp/report.json")

    def test_identify_at_risk_students(self, mock_db_session, mock_report_repo):
        """Test identification of at-risk students"""
        from backend.services.course_report_generator import CourseReportGenerator

        generator = CourseReportGenerator(
            db_session=mock_db_session,
            report_repository=mock_report_repo
        )

        student_summaries = [
            {
                "student_id": "student_001",
                "sessions": 5,
                "ai_dependency": 0.3,
                "competency": "INTERMEDIO",
                "risks": 2,
                "critical_risks": 0
            },
            {
                "student_id": "student_002",
                "sessions": 1,  # Low sessions
                "ai_dependency": 0.4,
                "competency": "BASICO",  # Low competency
                "risks": 1,
                "critical_risks": 0
            },
            {
                "student_id": "student_003",
                "sessions": 10,
                "ai_dependency": 0.8,  # High AI dependency
                "competency": "AVANZADO",
                "risks": 0,
                "critical_risks": 0
            },
            {
                "student_id": "student_004",
                "sessions": 8,
                "ai_dependency": 0.5,
                "competency": "INTERMEDIO",
                "risks": 3,
                "critical_risks": 1  # Has critical risk
            },
        ]

        at_risk = generator._identify_at_risk_students(student_summaries)

        # student_002 (low sessions, basic competency)
        # student_003 (high AI dependency)
        # student_004 (critical risks)
        assert "student_002" in at_risk
        assert "student_003" in at_risk
        assert "student_004" in at_risk
        assert "student_001" not in at_risk

    def test_generate_institutional_recommendations(
        self,
        mock_db_session,
        mock_report_repo
    ):
        """Test recommendation generation based on data"""
        from backend.services.course_report_generator import CourseReportGenerator

        generator = CourseReportGenerator(
            db_session=mock_db_session,
            report_repository=mock_report_repo
        )

        # High AI dependency scenario
        summary_stats_high_ai = {
            "avg_ai_dependency": 0.75,
            "avg_sessions_per_student": 5
        }
        competency_dist = {"BASICO": 2, "INTERMEDIO": 5, "AVANZADO": 3}
        risk_dist = {"LOW": 5, "MEDIUM": 3, "HIGH": 1, "CRITICAL": 2}
        top_risks = [{"risk_type": "COGNITIVE_DELEGATION", "count": 5}]

        recommendations = generator._generate_institutional_recommendations(
            summary_stats_high_ai,
            competency_dist,
            risk_dist,
            top_risks
        )

        # Should include AI dependency warning
        assert any("IA" in r or "dependencia" in r.lower() for r in recommendations)
        # Should include critical risk warning
        assert any("URGENTE" in r or "crítico" in r.lower() for r in recommendations)


# ============================================================================
# InstitutionalRiskManager Tests
# ============================================================================

class TestInstitutionalRiskManager:
    """Tests for InstitutionalRiskManager service"""

    def test_init_with_dependencies(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test InstitutionalRiskManager initialization"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        assert manager.db == mock_db_session
        assert manager.alert_repo == mock_alert_repo
        assert manager.plan_repo == mock_plan_repo

    def test_scan_for_alerts_no_students(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test alert scan with no active students"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.distinct = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[])
        mock_db_session.query = Mock(return_value=mock_query)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        alerts = manager.scan_for_alerts()

        assert alerts == []

    def test_scan_for_alerts_with_specific_students(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test alert scan with specific student list"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.scalar = Mock(return_value=0.3)  # Low AI dependency
        mock_query.all = Mock(return_value=[])
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=None)
        mock_db_session.query = Mock(return_value=mock_query)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        alerts = manager.scan_for_alerts(
            student_ids=["student_001", "student_002"],
            lookback_days=7
        )

        # With low AI dependency and no risks, should have no alerts
        assert isinstance(alerts, list)

    def test_create_remediation_plan(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test creating a remediation plan"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        mock_plan = Mock()
        mock_plan.id = str(uuid4())
        mock_plan_repo.create = Mock(return_value=mock_plan)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        result = manager.create_remediation_plan(
            student_id="student_001",
            teacher_id="teacher_001",
            trigger_risk_ids=["risk_001", "risk_002"],
            plan_type="tutoring",
            description="Plan de tutoria personalizada",
            objectives=["Mejorar comprension conceptual", "Reducir dependencia de IA"],
            recommended_actions=[
                {"action": "Sesion de tutoria", "deadline": "2025-02-01"},
                {"action": "Ejercicios adicionales", "deadline": "2025-02-15"}
            ],
            duration_days=14
        )

        assert result is not None
        assert result["student_id"] == "student_001"
        assert result["plan_type"] == "tutoring"
        assert result["status"] == "pending"
        mock_plan_repo.create.assert_called_once()

    def test_assign_alert(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test assigning an alert to a teacher"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        mock_alert = Mock()
        mock_alert.id = "alert_001"
        mock_alert.assigned_to = "teacher_001"
        mock_alert.assigned_at = datetime.now(timezone.utc)
        mock_alert.status = "assigned"
        mock_alert_repo.assign_to = Mock(return_value=mock_alert)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        result = manager.assign_alert("alert_001", "teacher_001")

        assert result["alert_id"] == "alert_001"
        assert result["assigned_to"] == "teacher_001"
        mock_alert_repo.assign_to.assert_called_once_with("alert_001", "teacher_001")

    def test_assign_alert_not_found(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test assigning non-existent alert"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        mock_alert_repo.assign_to = Mock(return_value=None)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        with pytest.raises(ValueError, match="not found"):
            manager.assign_alert("non_existent", "teacher_001")

    def test_acknowledge_alert(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test acknowledging an alert"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        mock_alert = Mock()
        mock_alert.id = "alert_001"
        mock_alert.acknowledged_by = "teacher_001"
        mock_alert.acknowledged_at = datetime.now(timezone.utc)
        mock_alert.status = "acknowledged"
        mock_alert_repo.acknowledge = Mock(return_value=mock_alert)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        result = manager.acknowledge_alert("alert_001", "teacher_001")

        assert result["alert_id"] == "alert_001"
        assert result["acknowledged_by"] == "teacher_001"
        assert result["status"] == "acknowledged"

    def test_resolve_alert(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test resolving an alert"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        mock_alert = Mock()
        mock_alert.id = "alert_001"
        mock_alert.status = "resolved"
        mock_alert.resolution_notes = "Issue addressed through tutoring"
        mock_alert.resolved_at = datetime.now(timezone.utc)
        mock_alert.remediation_plan_id = "plan_001"
        mock_alert_repo.resolve = Mock(return_value=mock_alert)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        result = manager.resolve_alert(
            "alert_001",
            "Issue addressed through tutoring",
            "plan_001"
        )

        assert result["alert_id"] == "alert_001"
        assert result["status"] == "resolved"
        assert result["remediation_plan_id"] == "plan_001"

    def test_thresholds_configuration(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test that thresholds are properly configured"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        # Verify default thresholds
        assert manager.THRESHOLDS["ai_dependency_spike"] == 0.7
        assert manager.THRESHOLDS["critical_risk_surge"] == 2
        assert manager.THRESHOLDS["session_inactivity_days"] == 7
        assert manager.THRESHOLDS["low_competency_threshold"] == 3.0
        assert manager.THRESHOLDS["academic_integrity_threshold"] == 1


# ============================================================================
# Alert Detection Tests
# ============================================================================

class TestAlertDetection:
    """Tests for specific alert detection methods"""

    def test_check_ai_dependency_spike_detected(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test AI dependency spike detection"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        # Mock high AI dependency
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.scalar = Mock(return_value=0.85)  # Above 0.7 threshold
        mock_db_session.query = Mock(return_value=mock_query)

        mock_alert = Mock()
        mock_alert.id = str(uuid4())
        mock_alert_repo.create = Mock(return_value=mock_alert)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        result = manager._check_ai_dependency_spike(
            "student_001",
            datetime.now(timezone.utc) - timedelta(days=7)
        )

        assert result is not None
        assert result["alert_type"] == "ai_dependency_spike"
        assert result["severity"] == "high"
        mock_alert_repo.create.assert_called_once()

    def test_check_ai_dependency_spike_not_detected(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test AI dependency below threshold"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.scalar = Mock(return_value=0.5)  # Below threshold
        mock_db_session.query = Mock(return_value=mock_query)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        result = manager._check_ai_dependency_spike(
            "student_001",
            datetime.now(timezone.utc) - timedelta(days=7)
        )

        assert result is None
        mock_alert_repo.create.assert_not_called()

    def test_check_critical_risk_surge_detected(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test critical risk surge detection"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        # Mock critical risks
        mock_risk1 = Mock()
        mock_risk1.id = "risk_001"
        mock_risk2 = Mock()
        mock_risk2.id = "risk_002"

        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.all = Mock(return_value=[mock_risk1, mock_risk2])  # 2 critical risks
        mock_db_session.query = Mock(return_value=mock_query)

        mock_alert = Mock()
        mock_alert.id = str(uuid4())
        mock_alert_repo.create = Mock(return_value=mock_alert)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        result = manager._check_critical_risk_surge(
            "student_001",
            datetime.now(timezone.utc) - timedelta(days=7)
        )

        assert result is not None
        assert result["alert_type"] == "critical_risk_surge"
        assert result["severity"] == "critical"

    def test_check_session_inactivity_detected(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test session inactivity detection"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        # Mock old session
        mock_session = Mock()
        mock_session.start_time = datetime.now(timezone.utc) - timedelta(days=10)

        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.first = Mock(return_value=mock_session)
        mock_db_session.query = Mock(return_value=mock_query)

        mock_alert = Mock()
        mock_alert.id = str(uuid4())
        mock_alert_repo.create = Mock(return_value=mock_alert)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        result = manager._check_session_inactivity("student_001")

        assert result is not None
        assert result["alert_type"] == "session_inactivity"
        assert result["severity"] == "medium"


# ============================================================================
# Integration Tests
# ============================================================================

class TestServicesIntegration:
    """Integration tests for service layer"""

    def test_full_alert_lifecycle(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test complete alert lifecycle: create -> assign -> acknowledge -> resolve"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        alert_id = str(uuid4())

        # Step 1: Alert created (simulated by scan)
        mock_alert_created = Mock()
        mock_alert_created.id = alert_id
        mock_alert_created.status = "open"
        mock_alert_repo.create = Mock(return_value=mock_alert_created)

        # Step 2: Alert assigned
        mock_alert_assigned = Mock()
        mock_alert_assigned.id = alert_id
        mock_alert_assigned.assigned_to = "teacher_001"
        mock_alert_assigned.assigned_at = datetime.now(timezone.utc)
        mock_alert_assigned.status = "assigned"
        mock_alert_repo.assign_to = Mock(return_value=mock_alert_assigned)

        # Step 3: Alert acknowledged
        mock_alert_acked = Mock()
        mock_alert_acked.id = alert_id
        mock_alert_acked.acknowledged_by = "teacher_001"
        mock_alert_acked.acknowledged_at = datetime.now(timezone.utc)
        mock_alert_acked.status = "acknowledged"
        mock_alert_repo.acknowledge = Mock(return_value=mock_alert_acked)

        # Step 4: Alert resolved
        mock_alert_resolved = Mock()
        mock_alert_resolved.id = alert_id
        mock_alert_resolved.status = "resolved"
        mock_alert_resolved.resolution_notes = "Addressed via tutoring"
        mock_alert_resolved.resolved_at = datetime.now(timezone.utc)
        mock_alert_resolved.remediation_plan_id = None
        mock_alert_repo.resolve = Mock(return_value=mock_alert_resolved)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        # Execute lifecycle
        assign_result = manager.assign_alert(alert_id, "teacher_001")
        assert assign_result["status"] == "assigned"

        ack_result = manager.acknowledge_alert(alert_id, "teacher_001")
        assert ack_result["status"] == "acknowledged"

        resolve_result = manager.resolve_alert(alert_id, "Addressed via tutoring")
        assert resolve_result["status"] == "resolved"

    def test_alert_with_remediation_plan(
        self,
        mock_db_session,
        mock_alert_repo,
        mock_plan_repo,
        mock_risk_repo
    ):
        """Test creating remediation plan and linking to alert resolution"""
        from backend.services.institutional_risk_manager import InstitutionalRiskManager

        # Create plan
        plan_id = str(uuid4())
        mock_plan = Mock()
        mock_plan.id = plan_id
        mock_plan_repo.create = Mock(return_value=mock_plan)

        # Resolve alert with plan
        mock_alert = Mock()
        mock_alert.id = "alert_001"
        mock_alert.status = "resolved"
        mock_alert.resolution_notes = "Created tutoring plan"
        mock_alert.resolved_at = datetime.now(timezone.utc)
        mock_alert.remediation_plan_id = plan_id
        mock_alert_repo.resolve = Mock(return_value=mock_alert)

        manager = InstitutionalRiskManager(
            db_session=mock_db_session,
            alert_repo=mock_alert_repo,
            plan_repo=mock_plan_repo,
            risk_repo=mock_risk_repo
        )

        # Create remediation plan
        plan_result = manager.create_remediation_plan(
            student_id="student_001",
            teacher_id="teacher_001",
            trigger_risk_ids=["risk_001"],
            plan_type="tutoring",
            description="Intensive tutoring program",
            objectives=["Improve conceptual understanding"],
            recommended_actions=[{"action": "Weekly sessions", "deadline": "2025-03-01"}]
        )

        # Resolve alert with plan reference
        resolve_result = manager.resolve_alert(
            "alert_001",
            "Created tutoring plan",
            plan_id
        )

        assert plan_result["plan_id"] == plan_id
        assert resolve_result["remediation_plan_id"] == plan_id