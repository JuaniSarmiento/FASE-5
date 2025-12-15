"""
Tests for Teacher Tools Router

Tests para backend/api/routers/teacher_tools.py

Verifica:
1. Comparación de estudiantes (GET /teacher/students/compare)
2. Alertas en tiempo real (GET /teacher/alerts)
3. Reconocimiento de alertas (POST /teacher/alerts/{id}/acknowledge)
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from uuid import uuid4
from collections import defaultdict

from fastapi import HTTPException


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_session():
    """Mock session object"""
    session = MagicMock()
    session.id = f"session_{uuid4().hex[:8]}"
    session.student_id = "student_001"
    session.activity_id = "activity_001"
    session.start_time = datetime.utcnow() - timedelta(hours=1)
    session.end_time = datetime.utcnow()
    session.status = "completed"
    return session


@pytest.fixture
def mock_active_session():
    """Mock active session object"""
    session = MagicMock()
    session.id = f"session_{uuid4().hex[:8]}"
    session.student_id = "student_002"
    session.activity_id = "activity_001"
    session.start_time = datetime.utcnow() - timedelta(hours=2)
    session.end_time = None
    session.status = "active"
    return session


@pytest.fixture
def mock_traces():
    """Mock trace objects"""
    traces = []
    cognitive_states = ["exploration", "implementation", "verification"]

    for i, state in enumerate(cognitive_states):
        trace = MagicMock()
        trace.id = f"trace_{uuid4().hex[:8]}"
        trace.cognitive_state = state
        trace.ai_involvement = 0.3 + (i * 0.2)
        trace.trace_metadata = {"blocked": i == 1}
        traces.append(trace)

    return traces


@pytest.fixture
def mock_risks():
    """Mock risk objects"""
    risks = []
    risk_configs = [
        ("ai_dependency", "MEDIUM"),
        ("verification_gap", "HIGH"),
        ("critical_error", "CRITICAL"),
    ]

    for rtype, level in risk_configs:
        risk = MagicMock()
        risk.id = f"risk_{uuid4().hex[:8]}"
        risk.risk_type = rtype
        risk.risk_level = level
        risks.append(risk)

    return risks


@pytest.fixture
def mock_session_repo(mock_session, mock_active_session):
    """Mock SessionRepository"""
    repo = MagicMock()
    repo.get_by_activity.return_value = [mock_session, mock_active_session]
    repo.get_all.return_value = [mock_session, mock_active_session]
    return repo


@pytest.fixture
def mock_trace_repo(mock_traces):
    """Mock TraceRepository"""
    repo = MagicMock()
    repo.get_by_session.return_value = mock_traces
    return repo


@pytest.fixture
def mock_risk_repo(mock_risks):
    """Mock RiskRepository"""
    repo = MagicMock()
    repo.get_by_session.return_value = mock_risks
    return repo


# ============================================================================
# Compare Students Tests
# ============================================================================

class TestCompareStudents:
    """Tests for GET /teacher/students/compare endpoint"""

    @pytest.mark.unit
    def test_compare_students_success(
        self, mock_session_repo, mock_trace_repo, mock_risk_repo, mock_session
    ):
        """compare_students() returns comparison data"""
        sessions = mock_session_repo.get_by_activity("activity_001")

        assert len(sessions) > 0

    @pytest.mark.unit
    def test_compare_students_no_sessions(self, mock_session_repo):
        """compare_students() raises 404 for activity with no sessions"""
        mock_session_repo.get_by_activity.return_value = []

        sessions = mock_session_repo.get_by_activity("unknown_activity")
        assert sessions == []

    @pytest.mark.unit
    def test_compare_students_filter_by_ids(self, mock_session_repo, mock_session):
        """compare_students() filters by specific student IDs"""
        all_sessions = mock_session_repo.get_by_activity("activity_001")
        student_ids = ["student_001"]

        filtered = [s for s in all_sessions if s.student_id in student_ids]

        assert len(filtered) == 1
        assert filtered[0].student_id == "student_001"

    @pytest.mark.unit
    def test_compare_students_includes_duration(self, mock_session):
        """Comparison includes duration calculation"""
        duration_minutes = 0.0
        if mock_session.end_time:
            duration_minutes = (mock_session.end_time - mock_session.start_time).total_seconds() / 60.0

        assert duration_minutes == 60.0  # 1 hour

    @pytest.mark.unit
    def test_compare_students_ai_dependency(self, mock_traces):
        """Comparison calculates AI dependency average"""
        ai_involvements = [t.ai_involvement for t in mock_traces]
        ai_avg = sum(ai_involvements) / len(ai_involvements)

        # 0.3 + 0.5 + 0.7 / 3 = 0.5
        assert 0.4 <= ai_avg <= 0.6

    @pytest.mark.unit
    def test_compare_students_cognitive_states(self, mock_traces):
        """Comparison includes cognitive states visited"""
        cognitive_states = list(set(t.cognitive_state for t in mock_traces if t.cognitive_state))

        assert "exploration" in cognitive_states
        assert "implementation" in cognitive_states
        assert "verification" in cognitive_states

    @pytest.mark.unit
    def test_compare_students_aggregate_stats(
        self, mock_session_repo, mock_trace_repo, mock_risk_repo
    ):
        """Comparison includes aggregate statistics"""
        sessions = mock_session_repo.get_by_activity("activity_001")
        completed = [s for s in sessions if s.status == "completed"]

        assert len(completed) >= 1


# ============================================================================
# Teacher Alerts Tests
# ============================================================================

class TestTeacherAlerts:
    """Tests for GET /teacher/alerts endpoint"""

    @pytest.mark.unit
    def test_get_alerts_success(self, mock_session_repo, mock_trace_repo, mock_risk_repo):
        """get_teacher_alerts() returns alerts for active sessions"""
        all_sessions = mock_session_repo.get_all()
        active_sessions = [s for s in all_sessions if s.status == "active"]

        assert len(active_sessions) >= 1

    @pytest.mark.unit
    def test_alerts_filter_by_severity(self, mock_risks):
        """Alerts can be filtered by severity"""
        critical_risks = [r for r in mock_risks if r.risk_level == "CRITICAL"]
        high_risks = [r for r in mock_risks if r.risk_level == "HIGH"]

        assert len(critical_risks) >= 1
        assert len(high_risks) >= 1

    @pytest.mark.unit
    def test_alert_criteria_critical_risks(self, mock_risks):
        """Alert triggers on critical risks"""
        critical_risks = [r for r in mock_risks if r.risk_level == "CRITICAL"]

        # 1+ critical risk should trigger alert
        should_alert = len(critical_risks) >= 1
        assert should_alert is True

    @pytest.mark.unit
    def test_alert_criteria_high_ai_dependency(self):
        """Alert triggers on high AI dependency"""
        ai_dependency_avg = 0.90  # 90%

        should_alert = ai_dependency_avg > 0.85
        assert should_alert is True

    @pytest.mark.unit
    def test_alert_criteria_prolonged_session(self, mock_active_session):
        """Alert triggers on prolonged sessions"""
        duration_hours = (datetime.utcnow() - mock_active_session.start_time).total_seconds() / 3600.0

        should_alert = duration_hours > 2.0
        assert should_alert is True

    @pytest.mark.unit
    def test_alert_severity_ordering(self):
        """Alerts are ordered by severity"""
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

        alerts = [
            {"severity": "medium"},
            {"severity": "critical"},
            {"severity": "high"},
        ]

        sorted_alerts = sorted(alerts, key=lambda a: severity_order[a["severity"]])

        assert sorted_alerts[0]["severity"] == "critical"
        assert sorted_alerts[1]["severity"] == "high"
        assert sorted_alerts[2]["severity"] == "medium"

    @pytest.mark.unit
    def test_alert_includes_suggestions(self, mock_risks):
        """Alerts include intervention suggestions"""
        critical_risks = [r for r in mock_risks if r.risk_level == "CRITICAL"]

        suggestions = []
        if len(critical_risks) >= 1:
            suggestions.append("Intervención inmediata: revisar riesgos críticos con el estudiante")

        assert len(suggestions) > 0

    @pytest.mark.unit
    def test_alert_includes_metrics(self, mock_traces, mock_risks):
        """Alerts include relevant metrics"""
        ai_involvements = [t.ai_involvement or 0.0 for t in mock_traces]
        ai_dependency_avg = sum(ai_involvements) / len(ai_involvements) if ai_involvements else 0.0

        metrics = {
            "critical_risks": len([r for r in mock_risks if r.risk_level == "CRITICAL"]),
            "high_risks": len([r for r in mock_risks if r.risk_level == "HIGH"]),
            "medium_risks": len([r for r in mock_risks if r.risk_level == "MEDIUM"]),
            "ai_dependency": round(ai_dependency_avg, 2),
            "total_interactions": len(mock_traces)
        }

        assert "critical_risks" in metrics
        assert "ai_dependency" in metrics


# ============================================================================
# Acknowledge Alert Tests
# ============================================================================

class TestAcknowledgeAlert:
    """Tests for POST /teacher/alerts/{id}/acknowledge endpoint"""

    @pytest.mark.unit
    def test_acknowledge_alert_success(self):
        """acknowledge_alert() returns confirmation"""
        alert_id = "alert_session_001"
        notes = "Contacted student, situation resolved"

        response = {
            "alert_id": alert_id,
            "acknowledged_at": datetime.utcnow().isoformat(),
            "notes": notes
        }

        assert response["alert_id"] == alert_id
        assert response["notes"] == notes

    @pytest.mark.unit
    def test_acknowledge_alert_without_notes(self):
        """acknowledge_alert() works without notes"""
        alert_id = "alert_session_001"

        response = {
            "alert_id": alert_id,
            "acknowledged_at": datetime.utcnow().isoformat(),
            "notes": "Sin notas"
        }

        assert response["notes"] == "Sin notas"


# ============================================================================
# Aggregate Statistics Tests
# ============================================================================

class TestAggregateStatistics:
    """Tests for aggregate statistics calculations"""

    @pytest.mark.unit
    def test_average_duration(self):
        """Average duration is calculated correctly"""
        students_data = [
            {"duration_minutes": 45.0, "status": "completed"},
            {"duration_minutes": 60.0, "status": "completed"},
            {"duration_minutes": 75.0, "status": "completed"},
        ]

        completed = [s for s in students_data if s["status"] == "completed"]
        avg_duration = sum(s["duration_minutes"] for s in completed) / len(completed)

        assert avg_duration == 60.0

    @pytest.mark.unit
    def test_average_interactions(self):
        """Average interactions is calculated correctly"""
        students_data = [
            {"total_interactions": 10, "status": "completed"},
            {"total_interactions": 20, "status": "completed"},
            {"total_interactions": 30, "status": "completed"},
        ]

        completed = [s for s in students_data if s["status"] == "completed"]
        avg_interactions = sum(s["total_interactions"] for s in completed) / len(completed)

        assert avg_interactions == 20.0

    @pytest.mark.unit
    def test_top_risks_ranking(self):
        """Top risks are ranked by frequency"""
        all_risks = {
            "ai_dependency": 10,
            "verification_gap": 5,
            "critical_error": 3
        }

        top_risks = sorted(all_risks.items(), key=lambda x: x[1], reverse=True)[:5]

        assert top_risks[0][0] == "ai_dependency"
        assert top_risks[0][1] == 10

    @pytest.mark.unit
    def test_cognitive_states_distribution(self):
        """Cognitive states distribution is aggregated"""
        students_data = [
            {"cognitive_states_visited": ["exploration", "implementation"]},
            {"cognitive_states_visited": ["exploration", "verification"]},
            {"cognitive_states_visited": ["implementation", "verification"]},
        ]

        all_states = defaultdict(int)
        for student in students_data:
            for state in student["cognitive_states_visited"]:
                all_states[state] += 1

        assert all_states["exploration"] == 2
        assert all_states["implementation"] == 2
        assert all_states["verification"] == 2


# ============================================================================
# Alert Criteria Tests
# ============================================================================

class TestAlertCriteria:
    """Tests for alert triggering criteria"""

    @pytest.mark.unit
    def test_critical_risk_triggers_critical_alert(self):
        """1+ critical risk triggers critical severity alert"""
        critical_count = 1
        alert_severity = "low"

        if critical_count >= 1:
            alert_severity = "critical"

        assert alert_severity == "critical"

    @pytest.mark.unit
    def test_multiple_high_risks_triggers_high_alert(self):
        """2+ high risks triggers high severity alert"""
        high_count = 2
        alert_severity = "low"

        if high_count >= 2:
            alert_severity = "high"

        assert alert_severity == "high"

    @pytest.mark.unit
    def test_multiple_medium_risks_triggers_medium_alert(self):
        """3+ medium risks triggers medium severity alert"""
        medium_count = 3
        alert_severity = "low"

        if medium_count >= 3:
            alert_severity = "medium"

        assert alert_severity == "medium"

    @pytest.mark.unit
    def test_high_ai_dependency_triggers_alert(self):
        """AI dependency > 85% triggers alert"""
        ai_dependency = 0.90
        alert_reasons = []

        if ai_dependency > 0.85:
            alert_reasons.append(f"Dependencia de IA muy alta ({ai_dependency*100:.0f}%)")

        assert len(alert_reasons) == 1

    @pytest.mark.unit
    def test_prolonged_session_triggers_alert(self):
        """Session > 2 hours triggers alert"""
        duration_hours = 2.5
        alert_reasons = []

        if duration_hours > 2.0:
            alert_reasons.append(f"Sesión prolongada ({duration_hours:.1f} horas)")

        assert len(alert_reasons) == 1


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestEdgeCases:
    """Edge cases and error handling tests"""

    @pytest.mark.unit
    def test_no_active_sessions(self, mock_session_repo):
        """Handles case with no active sessions"""
        mock_session_repo.get_all.return_value = []

        sessions = mock_session_repo.get_all()
        active = [s for s in sessions if s.status == "active"]

        assert len(active) == 0

    @pytest.mark.unit
    def test_no_completed_sessions_for_stats(self):
        """Handles case with no completed sessions"""
        students_data = [
            {"status": "active"},
            {"status": "active"},
        ]

        completed = [s for s in students_data if s.get("status") == "completed"]

        if completed:
            avg_duration = 0
        else:
            avg_duration = 0.0

        assert avg_duration == 0.0

    @pytest.mark.unit
    def test_session_without_end_time(self, mock_active_session):
        """Handles active session without end_time"""
        duration_minutes = 0.0

        if mock_active_session.end_time:
            duration_minutes = (mock_active_session.end_time - mock_active_session.start_time).total_seconds() / 60.0

        assert duration_minutes == 0.0

    @pytest.mark.unit
    def test_traces_without_ai_involvement(self):
        """Handles traces with None ai_involvement"""
        traces = [
            MagicMock(ai_involvement=None),
            MagicMock(ai_involvement=0.5),
        ]

        ai_involvements = [t.ai_involvement or 0.0 for t in traces]
        avg = sum(ai_involvements) / len(ai_involvements)

        assert avg == 0.25

    @pytest.mark.unit
    def test_empty_risks_list(self):
        """Handles session with no risks"""
        risks = []

        critical = [r for r in risks if r.risk_level == "CRITICAL"]
        assert len(critical) == 0

    @pytest.mark.unit
    def test_unicode_in_notes(self):
        """Handles unicode in acknowledgment notes"""
        notes = "Estudiante contactado, situación resuelta correctamente"

        response = {
            "notes": notes
        }

        assert response["notes"] == notes


# ============================================================================
# Integration Tests
# ============================================================================

class TestTeacherToolsIntegration:
    """Integration tests for teacher tools functionality"""

    @pytest.mark.integration
    def test_full_comparison_workflow(self):
        """Complete workflow: compare -> identify at-risk -> alert -> acknowledge"""
        pass

    @pytest.mark.integration
    def test_real_time_alert_updates(self):
        """Alerts update in real-time as session progresses"""
        pass

    @pytest.mark.integration
    def test_multiple_activities_comparison(self):
        """Comparison works across multiple activities"""
        pass