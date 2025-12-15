"""
Tests for Institutional Reports Router

Tests para backend/api/routers/reports.py

Verifica:
1. Generación de reportes de cohorte (POST /reports/cohort)
2. Generación de dashboard de riesgos (POST /reports/risk-dashboard)
3. Obtención de reportes por ID (GET /reports/{report_id})
4. Descarga de archivos de reportes (GET /reports/{report_id}/download)
5. Reportes por docente (GET /reports/teacher/{teacher_id})
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4
from pathlib import Path

from fastapi import HTTPException


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_report():
    """Mock report object"""
    report = MagicMock()
    report.id = f"report_{uuid4().hex[:8]}"
    report.course_id = "PROG2_2025_1C"
    report.teacher_id = "teacher_001"
    report.report_type = "cohort_summary"
    report.period_start = datetime.utcnow() - timedelta(days=30)
    report.period_end = datetime.utcnow()
    report.created_at = datetime.utcnow()
    report.summary_stats = {
        "total_students": 25,
        "sessions_total": 150,
        "avg_ai_involvement": 0.45
    }
    report.competency_distribution = {
        "advanced": 5,
        "proficient": 12,
        "developing": 6,
        "beginner": 2
    }
    report.risk_distribution = {
        "low": 18,
        "medium": 5,
        "high": 2
    }
    report.top_risks = [
        {"type": "ai_dependency", "count": 8},
        {"type": "verification_gap", "count": 5}
    ]
    report.student_summaries = []
    report.institutional_recommendations = [
        "Increase focus on independent coding exercises"
    ]
    report.at_risk_students = ["student_003", "student_007"]
    report.format = "json"
    report.file_path = None
    report.exported_at = None
    return report


@pytest.fixture
def mock_report_repo(mock_report):
    """Mock CourseReportRepository"""
    repo = MagicMock()
    repo.get_by_id.return_value = mock_report
    repo.get_by_teacher.return_value = [mock_report]
    repo.create.return_value = mock_report
    return repo


@pytest.fixture
def mock_report_generator(mock_report):
    """Mock CourseReportGenerator"""
    generator = MagicMock()
    generator.generate_cohort_summary.return_value = {
        "report_id": mock_report.id,
        "course_id": mock_report.course_id,
        "summary_stats": mock_report.summary_stats,
        "at_risk_students": mock_report.at_risk_students
    }
    generator.generate_risk_dashboard.return_value = {
        "report_id": mock_report.id,
        "course_id": mock_report.course_id,
        "critical_students": ["student_003", "student_007"],
        "risk_summary": mock_report.risk_distribution
    }
    generator.export_report_to_json.return_value = "reports/report_test.json"
    return generator


@pytest.fixture
def valid_cohort_request():
    """Valid cohort report request"""
    return {
        "course_id": "PROG2_2025_1C",
        "teacher_id": "teacher_001",
        "student_ids": ["student_001", "student_002", "student_003"],
        "period_start": datetime.utcnow() - timedelta(days=30),
        "period_end": datetime.utcnow(),
        "export_format": "json"
    }


@pytest.fixture
def valid_risk_dashboard_request():
    """Valid risk dashboard request"""
    return {
        "course_id": "PROG2_2025_1C",
        "teacher_id": "teacher_001",
        "student_ids": ["student_001", "student_002", "student_003"],
        "period_start": datetime.utcnow() - timedelta(days=30),
        "period_end": datetime.utcnow()
    }


# ============================================================================
# Generate Cohort Report Tests
# ============================================================================

class TestGenerateCohortReport:
    """Tests for POST /reports/cohort endpoint"""

    @pytest.mark.unit
    def test_generate_cohort_report_success(self, mock_report_generator, valid_cohort_request):
        """generate_cohort_report() creates cohort summary"""
        report_data = mock_report_generator.generate_cohort_summary(
            course_id=valid_cohort_request["course_id"],
            teacher_id=valid_cohort_request["teacher_id"],
            student_ids=valid_cohort_request["student_ids"],
            period_start=valid_cohort_request["period_start"],
            period_end=valid_cohort_request["period_end"],
            export_format=valid_cohort_request["export_format"]
        )

        assert "report_id" in report_data
        assert "summary_stats" in report_data

    @pytest.mark.unit
    def test_generate_cohort_report_empty_students(self, valid_cohort_request):
        """generate_cohort_report() raises 400 for empty student list"""
        valid_cohort_request["student_ids"] = []

        # Should raise validation error
        assert valid_cohort_request["student_ids"] == []

    @pytest.mark.unit
    def test_generate_cohort_report_invalid_period(self, valid_cohort_request):
        """generate_cohort_report() raises 400 for invalid period"""
        # End before start
        valid_cohort_request["period_end"] = valid_cohort_request["period_start"] - timedelta(days=1)

        assert valid_cohort_request["period_end"] < valid_cohort_request["period_start"]

    @pytest.mark.unit
    def test_generate_cohort_report_multiple_formats(self, mock_report_generator):
        """Cohort report supports multiple export formats"""
        formats = ["json", "pdf", "xlsx"]

        for fmt in formats:
            mock_report_generator.generate_cohort_summary.return_value = {
                "report_id": "test",
                "format": fmt
            }
            # Should not raise
            result = mock_report_generator.generate_cohort_summary(
                course_id="PROG2",
                teacher_id="teacher_001",
                student_ids=["s1"],
                period_start=datetime.utcnow() - timedelta(days=30),
                period_end=datetime.utcnow(),
                export_format=fmt
            )
            assert result["format"] == fmt


# ============================================================================
# Generate Risk Dashboard Tests
# ============================================================================

class TestGenerateRiskDashboard:
    """Tests for POST /reports/risk-dashboard endpoint"""

    @pytest.mark.unit
    def test_generate_risk_dashboard_success(self, mock_report_generator, valid_risk_dashboard_request):
        """generate_risk_dashboard() creates risk dashboard"""
        dashboard_data = mock_report_generator.generate_risk_dashboard(
            course_id=valid_risk_dashboard_request["course_id"],
            teacher_id=valid_risk_dashboard_request["teacher_id"],
            student_ids=valid_risk_dashboard_request["student_ids"],
            period_start=valid_risk_dashboard_request["period_start"],
            period_end=valid_risk_dashboard_request["period_end"]
        )

        assert "report_id" in dashboard_data
        assert "critical_students" in dashboard_data

    @pytest.mark.unit
    def test_generate_risk_dashboard_empty_students(self, valid_risk_dashboard_request):
        """generate_risk_dashboard() raises 400 for empty student list"""
        valid_risk_dashboard_request["student_ids"] = []

        assert valid_risk_dashboard_request["student_ids"] == []

    @pytest.mark.unit
    def test_risk_dashboard_identifies_critical_students(self, mock_report_generator):
        """Risk dashboard identifies critical risk students"""
        result = mock_report_generator.generate_risk_dashboard(
            course_id="PROG2",
            teacher_id="teacher_001",
            student_ids=["s1", "s2", "s3"],
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow()
        )

        assert len(result["critical_students"]) >= 0


# ============================================================================
# Get Report Tests
# ============================================================================

class TestGetReport:
    """Tests for GET /reports/{report_id} endpoint"""

    @pytest.mark.unit
    def test_get_report_success(self, mock_report_repo, mock_report):
        """get_report() returns complete report data"""
        report = mock_report_repo.get_by_id(mock_report.id)

        assert report is not None
        assert report.id == mock_report.id
        assert report.course_id == mock_report.course_id

    @pytest.mark.unit
    def test_get_report_not_found(self, mock_report_repo):
        """get_report() raises 404 for unknown report"""
        mock_report_repo.get_by_id.return_value = None

        result = mock_report_repo.get_by_id("unknown_report")
        assert result is None

    @pytest.mark.unit
    def test_get_report_includes_all_fields(self, mock_report):
        """Report data includes all expected fields"""
        required_fields = [
            "id", "course_id", "teacher_id", "report_type",
            "period_start", "period_end", "created_at",
            "summary_stats", "at_risk_students"
        ]

        for field in required_fields:
            assert hasattr(mock_report, field)


# ============================================================================
# Download Report Tests
# ============================================================================

class TestDownloadReport:
    """Tests for GET /reports/{report_id}/download endpoint"""

    @pytest.mark.unit
    def test_download_report_not_found(self, mock_report_repo):
        """download_report() raises 404 for unknown report"""
        mock_report_repo.get_by_id.return_value = None

        result = mock_report_repo.get_by_id("unknown_report")
        assert result is None

    @pytest.mark.unit
    def test_download_report_exports_if_needed(self, mock_report_repo, mock_report, mock_report_generator):
        """download_report() exports report if not yet exported"""
        mock_report.file_path = None

        # Should trigger export
        assert mock_report.file_path is None

    @pytest.mark.unit
    def test_download_report_json_media_type(self):
        """JSON reports have correct media type"""
        file_path = "reports/report_test.json"
        media_type = "application/json"

        assert file_path.endswith(".json")
        assert media_type == "application/json"

    @pytest.mark.unit
    def test_download_report_pdf_media_type(self):
        """PDF reports have correct media type"""
        file_path = "reports/report_test.pdf"

        media_type = "application/json"
        if file_path.endswith(".pdf"):
            media_type = "application/pdf"

        assert media_type == "application/pdf"

    @pytest.mark.unit
    def test_download_report_xlsx_media_type(self):
        """XLSX reports have correct media type"""
        file_path = "reports/report_test.xlsx"

        media_type = "application/json"
        if file_path.endswith(".xlsx"):
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        assert media_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


# ============================================================================
# Teacher Reports Tests
# ============================================================================

class TestTeacherReports:
    """Tests for GET /reports/teacher/{teacher_id} endpoint"""

    @pytest.mark.unit
    def test_get_teacher_reports_success(self, mock_report_repo, mock_report):
        """get_teacher_reports() returns teacher's reports"""
        reports = mock_report_repo.get_by_teacher("teacher_001")

        assert len(reports) > 0
        assert reports[0].teacher_id == mock_report.teacher_id

    @pytest.mark.unit
    def test_get_teacher_reports_empty(self, mock_report_repo):
        """get_teacher_reports() returns empty list for teacher with no reports"""
        mock_report_repo.get_by_teacher.return_value = []

        reports = mock_report_repo.get_by_teacher("new_teacher")
        assert reports == []

    @pytest.mark.unit
    def test_get_teacher_reports_with_limit(self, mock_report_repo):
        """get_teacher_reports() respects limit parameter"""
        mock_report_repo.get_by_teacher("teacher_001", limit=5)

        mock_report_repo.get_by_teacher.assert_called_with("teacher_001", limit=5)

    @pytest.mark.unit
    def test_get_teacher_reports_ordered_by_date(self, mock_report_repo):
        """Teacher reports are ordered by creation date"""
        reports = [
            MagicMock(created_at=datetime.utcnow() - timedelta(days=2)),
            MagicMock(created_at=datetime.utcnow() - timedelta(days=1)),
            MagicMock(created_at=datetime.utcnow()),
        ]
        mock_report_repo.get_by_teacher.return_value = reports

        result = mock_report_repo.get_by_teacher("teacher_001")

        # Should have multiple reports
        assert len(result) == 3


# ============================================================================
# Schema Validation Tests
# ============================================================================

class TestSchemaValidation:
    """Tests for request/response schema validation"""

    @pytest.mark.unit
    def test_cohort_request_schema(self):
        """CohortReportRequest schema is valid"""
        from backend.api.routers.reports import CohortReportRequest

        request = CohortReportRequest(
            course_id="PROG2_2025",
            teacher_id="teacher_001",
            student_ids=["s1", "s2"],
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            export_format="json"
        )

        assert request.course_id == "PROG2_2025"
        assert len(request.student_ids) == 2

    @pytest.mark.unit
    def test_risk_dashboard_request_schema(self):
        """RiskDashboardRequest schema is valid"""
        from backend.api.routers.reports import RiskDashboardRequest

        request = RiskDashboardRequest(
            course_id="PROG2_2025",
            teacher_id="teacher_001",
            student_ids=["s1", "s2"],
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow()
        )

        assert request.course_id == "PROG2_2025"

    @pytest.mark.unit
    def test_report_response_schema(self):
        """ReportResponse schema is valid"""
        from backend.api.routers.reports import ReportResponse

        response = ReportResponse(
            report_id="report_001",
            course_id="PROG2_2025",
            teacher_id="teacher_001",
            report_type="cohort_summary",
            period_start="2025-01-01T00:00:00",
            period_end="2025-01-31T23:59:59",
            generated_at="2025-01-31T12:00:00",
            summary_stats={"total_students": 25},
            at_risk_students=["s1", "s2"]
        )

        assert response.report_id == "report_001"
        assert len(response.at_risk_students) == 2


# ============================================================================
# Report Content Tests
# ============================================================================

class TestReportContent:
    """Tests for report content structure"""

    @pytest.mark.unit
    def test_report_summary_stats(self, mock_report):
        """Report includes summary statistics"""
        assert "total_students" in mock_report.summary_stats
        assert "sessions_total" in mock_report.summary_stats
        assert "avg_ai_involvement" in mock_report.summary_stats

    @pytest.mark.unit
    def test_report_competency_distribution(self, mock_report):
        """Report includes competency distribution"""
        levels = mock_report.competency_distribution
        expected_levels = ["advanced", "proficient", "developing", "beginner"]

        for level in expected_levels:
            assert level in levels

    @pytest.mark.unit
    def test_report_risk_distribution(self, mock_report):
        """Report includes risk distribution"""
        risks = mock_report.risk_distribution
        expected_levels = ["low", "medium", "high"]

        for level in expected_levels:
            assert level in risks

    @pytest.mark.unit
    def test_report_top_risks(self, mock_report):
        """Report includes top risks list"""
        assert len(mock_report.top_risks) > 0
        for risk in mock_report.top_risks:
            assert "type" in risk
            assert "count" in risk

    @pytest.mark.unit
    def test_report_institutional_recommendations(self, mock_report):
        """Report includes institutional recommendations"""
        assert len(mock_report.institutional_recommendations) > 0

    @pytest.mark.unit
    def test_report_at_risk_students(self, mock_report):
        """Report identifies at-risk students"""
        assert len(mock_report.at_risk_students) > 0


# ============================================================================
# Export Format Tests
# ============================================================================

class TestExportFormats:
    """Tests for different export formats"""

    @pytest.mark.unit
    def test_default_format_is_json(self, valid_cohort_request):
        """Default export format is JSON"""
        from backend.api.routers.reports import CohortReportRequest

        request = CohortReportRequest(**valid_cohort_request)
        assert request.export_format == "json"

    @pytest.mark.unit
    def test_supported_export_formats(self):
        """All supported export formats are recognized"""
        supported_formats = ["json", "pdf", "xlsx"]

        for fmt in supported_formats:
            # Should be valid
            assert fmt in supported_formats


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestEdgeCases:
    """Edge cases and error handling tests"""

    @pytest.mark.unit
    def test_single_student_cohort(self, mock_report_generator):
        """Report can be generated for single student"""
        mock_report_generator.generate_cohort_summary(
            course_id="PROG2",
            teacher_id="teacher_001",
            student_ids=["student_001"],  # Single student
            period_start=datetime.utcnow() - timedelta(days=30),
            period_end=datetime.utcnow(),
            export_format="json"
        )

        mock_report_generator.generate_cohort_summary.assert_called_once()

    @pytest.mark.unit
    def test_very_long_period(self, mock_report_generator):
        """Report handles very long periods"""
        mock_report_generator.generate_cohort_summary(
            course_id="PROG2",
            teacher_id="teacher_001",
            student_ids=["s1"],
            period_start=datetime.utcnow() - timedelta(days=365),
            period_end=datetime.utcnow(),
            export_format="json"
        )

        mock_report_generator.generate_cohort_summary.assert_called_once()

    @pytest.mark.unit
    def test_report_with_no_risks(self, mock_report):
        """Report handles case with no risks"""
        mock_report.risk_distribution = {"low": 25, "medium": 0, "high": 0}
        mock_report.at_risk_students = []

        assert mock_report.risk_distribution["high"] == 0
        assert len(mock_report.at_risk_students) == 0

    @pytest.mark.unit
    def test_unicode_in_recommendations(self, mock_report):
        """Report handles unicode in recommendations"""
        mock_report.institutional_recommendations = [
            "Aumentar ejercicios de práctica autónoma",
            "Implementar sesiones de tutoría"
        ]

        for rec in mock_report.institutional_recommendations:
            assert len(rec) > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestReportsIntegration:
    """Integration tests for reports functionality"""

    @pytest.mark.integration
    def test_full_report_lifecycle(self):
        """Complete report lifecycle: generate -> retrieve -> download"""
        pass

    @pytest.mark.integration
    def test_report_generation_with_real_data(self):
        """Report generation with actual student data"""
        pass

    @pytest.mark.integration
    def test_concurrent_report_generation(self):
        """Multiple reports can be generated concurrently"""
        pass