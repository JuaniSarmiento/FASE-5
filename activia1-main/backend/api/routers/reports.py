"""
Institutional Reports API Endpoints - SPRINT 5 HU-DOC-009

Endpoints:
- POST /reports/cohort - Generate cohort summary report
- POST /reports/risk-dashboard - Generate risk dashboard
- GET /reports/{report_id} - Get report by ID
- GET /reports/{report_id}/download - Download report file
- GET /reports/teacher/{teacher_id} - Get reports by teacher
- GET /reports/activity/{activity_id} - Get activity report (Frontend compatibility)
- GET /reports/analytics - Get learning analytics (Frontend compatibility)
"""

import logging
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query

from backend.core.constants import utc_now
from fastapi.responses import FileResponse
from ..deps import require_teacher_role
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..deps import get_db
from ...database.repositories import CourseReportRepository, SessionRepository, TraceRepository, RiskRepository, EvaluationRepository
from ...database.models import SessionDB, CognitiveTraceDB, RiskDB, EvaluationDB, ActivityDB
from ...services.course_report_generator import CourseReportGenerator
from ..schemas.common import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Institutional Reports"])


# =============================================================================
# REQUEST/RESPONSE SCHEMAS
# =============================================================================


class CohortReportRequest(BaseModel):
    """Request to generate cohort summary report"""

    course_id: str = Field(description="Course identifier (e.g., PROG2_2025_1C)")
    teacher_id: str = Field(description="Teacher generating the report")
    student_ids: List[str] = Field(description="List of student IDs in cohort")
    period_start: datetime = Field(description="Start of reporting period")
    period_end: datetime = Field(description="End of reporting period")
    export_format: str = Field(default="json", description="Export format (json, pdf, xlsx)")


class RiskDashboardRequest(BaseModel):
    """Request to generate risk dashboard"""

    course_id: str = Field(description="Course identifier")
    teacher_id: str = Field(description="Teacher generating the report")
    student_ids: List[str] = Field(description="List of student IDs")
    period_start: datetime = Field(description="Start of period")
    period_end: datetime = Field(description="End of period")


class ReportResponse(BaseModel):
    """Response with report summary"""

    report_id: str
    course_id: str
    teacher_id: str
    report_type: str
    period_start: str
    period_end: str
    generated_at: str
    summary_stats: dict
    at_risk_students: List[str]


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post(
    "/cohort",
    response_model=APIResponse[dict],
    summary="Generate cohort summary report",
    description="Generate aggregate report for a cohort of students. Requires teacher role.",
    status_code=status.HTTP_201_CREATED,
)
async def generate_cohort_report(
    request: CohortReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_role),
) -> APIResponse[dict]:
    """
    Generate cohort summary report

    Aggregates data from multiple students to provide institutional insights.
    """
    if not request.student_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="student_ids cannot be empty",
        )

    if request.period_end <= request.period_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="period_end must be after period_start",
        )

    try:
        generator = CourseReportGenerator(db)
        report_data = generator.generate_cohort_summary(
            course_id=request.course_id,
            teacher_id=request.teacher_id,
            student_ids=request.student_ids,
            period_start=request.period_start,
            period_end=request.period_end,
            export_format=request.export_format,
        )

        logger.info(
            "Cohort report generated",
            extra={
                "report_id": report_data["report_id"],
                "course_id": request.course_id,
                "student_count": len(request.student_ids),
            },
        )

        return APIResponse(
            success=True,
            data=report_data,
            message=f"Cohort report generated for {len(request.student_ids)} students",
        )

    except Exception as e:
        logger.error(
            "Error generating cohort report",
            exc_info=True,
            extra={"course_id": request.course_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}",
        )


@router.post(
    "/risk-dashboard",
    response_model=APIResponse[dict],
    summary="Generate risk dashboard",
    description="Generate risk-focused dashboard for proactive intervention. Requires teacher role.",
    status_code=status.HTTP_201_CREATED,
)
async def generate_risk_dashboard(
    request: RiskDashboardRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_role),
) -> APIResponse[dict]:
    """
    Generate risk dashboard

    Provides detailed risk analysis for a cohort.
    """
    if not request.student_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="student_ids cannot be empty",
        )

    try:
        generator = CourseReportGenerator(db)
        dashboard_data = generator.generate_risk_dashboard(
            course_id=request.course_id,
            teacher_id=request.teacher_id,
            student_ids=request.student_ids,
            period_start=request.period_start,
            period_end=request.period_end,
        )

        logger.info(
            "Risk dashboard generated",
            extra={
                "report_id": dashboard_data["report_id"],
                "course_id": request.course_id,
                "critical_students": len(dashboard_data["critical_students"]),
            },
        )

        return APIResponse(
            success=True,
            data=dashboard_data,
            message=f"Risk dashboard generated for {len(request.student_ids)} students",
        )

    except Exception as e:
        logger.error(
            "Error generating risk dashboard",
            exc_info=True,
            extra={"course_id": request.course_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating dashboard: {str(e)}",
        )


@router.get(
    "/{report_id}",
    response_model=APIResponse[dict],
    summary="Get report by ID",
    description="Retrieve a previously generated report. Requires teacher role.",
)
async def get_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_role),
) -> APIResponse[dict]:
    """
    Get report by ID

    Returns complete report data.
    """
    report_repo = CourseReportRepository(db)
    report = report_repo.get_by_id(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found",
        )

    report_data = {
        "report_id": report.id,
        "course_id": report.course_id,
        "teacher_id": report.teacher_id,
        "report_type": report.report_type,
        "period_start": report.period_start.isoformat(),
        "period_end": report.period_end.isoformat(),
        "generated_at": report.created_at.isoformat(),
        "summary_stats": report.summary_stats,
        "competency_distribution": report.competency_distribution,
        "risk_distribution": report.risk_distribution,
        "top_risks": report.top_risks,
        "student_summaries": report.student_summaries,
        "institutional_recommendations": report.institutional_recommendations,
        "at_risk_students": report.at_risk_students,
        "format": report.format,
        "file_path": report.file_path,
        "exported_at": report.exported_at.isoformat() if report.exported_at else None,
    }

    logger.info("Report retrieved", extra={"report_id": report_id})

    return APIResponse(
        success=True,
        data=report_data,
        message="Report retrieved successfully",
    )


@router.get(
    "/{report_id}/download",
    summary="Download report file",
    description="Download exported report file (JSON, PDF, XLSX). Requires teacher role.",
)
async def download_report(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_role),
) -> FileResponse:
    """
    Download report file

    Returns the exported file if available.
    """
    report_repo = CourseReportRepository(db)
    report = report_repo.get_by_id(report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report '{report_id}' not found",
        )

    # If not yet exported, export now
    if not report.file_path:
        generator = CourseReportGenerator(db, report_repo)
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"report_{report_id}.json"

        file_path = generator.export_report_to_json(report_id, str(output_path))
    else:
        file_path = report.file_path

    # Validate file exists
    if not Path(file_path).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report file not found: {file_path}",
        )

    logger.info(
        "Report downloaded",
        extra={"report_id": report_id, "file_path": file_path},
    )

    # Determine media type
    media_type = "application/json"
    if file_path.endswith(".pdf"):
        media_type = "application/pdf"
    elif file_path.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=Path(file_path).name,
    )


@router.get(
    "/teacher/{teacher_id}",
    response_model=APIResponse[List[dict]],
    summary="Get reports by teacher",
    description="Get all reports generated by a teacher. Requires teacher role.",
)
async def get_teacher_reports(
    teacher_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_role),
) -> APIResponse[List[dict]]:
    """
    Get reports by teacher

    Returns list of reports ordered by creation date.
    """
    report_repo = CourseReportRepository(db)
    reports = report_repo.get_by_teacher(teacher_id, limit=limit)

    reports_data = [
        {
            "report_id": r.id,
            "course_id": r.course_id,
            "report_type": r.report_type,
            "period_start": r.period_start.isoformat(),
            "period_end": r.period_end.isoformat(),
            "generated_at": r.created_at.isoformat(),
            "format": r.format,
            "exported": r.exported_at is not None,
        }
        for r in reports
    ]

    logger.info(
        "Teacher reports retrieved",
        extra={"teacher_id": teacher_id, "count": len(reports_data)},
    )

    return APIResponse(
        success=True,
        data=reports_data,
        message=f"Retrieved {len(reports_data)} reports",
    )


# =============================================================================
# FRONTEND COMPATIBILITY ENDPOINTS
# These endpoints were missing and are required by the frontend
# =============================================================================


class StudentPerformance(BaseModel):
    """Student performance summary"""
    student_id: str
    sessions_count: int
    avg_score: float
    competency_level: str
    ai_dependency: float
    risks_detected: int


class RiskSummary(BaseModel):
    """Risk distribution summary"""
    total_risks: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int


class ActivityReportResponse(BaseModel):
    """Activity report response matching frontend expectations"""
    activity_id: str
    activity_name: str
    total_sessions: int
    completion_rate: float
    avg_score: float
    avg_ai_dependency: float
    student_performance: List[StudentPerformance]
    risk_summary: RiskSummary
    competency_distribution: dict


class AgentUsage(BaseModel):
    """Agent usage statistics"""
    agent: str
    usage_count: int
    avg_satisfaction: float


class CompetencyTrend(BaseModel):
    """Competency trend over time"""
    date: str
    competency: str
    avg_score: float


class RiskTrendData(BaseModel):
    """Risk trend data"""
    date: str
    risk_level: str
    count: int


class LearningAnalyticsResponse(BaseModel):
    """Learning analytics response matching frontend expectations"""
    period: str
    total_students: int
    total_sessions: int
    avg_session_duration: float
    most_used_agents: List[AgentUsage]
    competency_trends: List[CompetencyTrend]
    risk_trends: List[RiskTrendData]


@router.get(
    "/activity/{activity_id}",
    response_model=APIResponse[ActivityReportResponse],
    summary="Get activity report",
    description="Get comprehensive report for a specific activity (Frontend compatibility). Requires teacher role.",
)
async def get_activity_report(
    activity_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_role),
) -> APIResponse[ActivityReportResponse]:
    """
    Get activity report with performance metrics.

    This endpoint provides aggregate statistics for all sessions
    related to a specific activity, including:
    - Total sessions and completion rate
    - Average scores and AI dependency
    - Per-student performance breakdown
    - Risk distribution summary
    - Competency level distribution
    """
    try:
        # Get activity info
        activity = db.query(ActivityDB).filter(ActivityDB.id == activity_id).first()
        activity_name = activity.title if activity else activity_id

        # Get all sessions for this activity
        sessions = db.query(SessionDB).filter(
            SessionDB.activity_id == activity_id
        ).all()

        if not sessions:
            # Return empty report if no sessions
            return APIResponse(
                success=True,
                data=ActivityReportResponse(
                    activity_id=activity_id,
                    activity_name=activity_name,
                    total_sessions=0,
                    completion_rate=0.0,
                    avg_score=0.0,
                    avg_ai_dependency=0.0,
                    student_performance=[],
                    risk_summary=RiskSummary(
                        total_risks=0,
                        critical_count=0,
                        high_count=0,
                        medium_count=0,
                        low_count=0,
                    ),
                    competency_distribution={},
                ),
                message=f"No sessions found for activity {activity_id}",
            )

        session_ids = [s.id for s in sessions]
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.status == "completed"])
        completion_rate = (completed_sessions / total_sessions) * 100 if total_sessions > 0 else 0.0

        # Calculate average AI dependency from traces
        traces = db.query(CognitiveTraceDB).filter(
            CognitiveTraceDB.session_id.in_(session_ids)
        ).all()

        avg_ai_dependency = 0.0
        if traces:
            ai_involvements = [t.ai_involvement for t in traces if t.ai_involvement is not None]
            avg_ai_dependency = sum(ai_involvements) / len(ai_involvements) if ai_involvements else 0.0

        # Get evaluations for average score
        evaluations = db.query(EvaluationDB).filter(
            EvaluationDB.session_id.in_(session_ids)
        ).all()

        avg_score = 0.0
        competency_distribution = {}
        if evaluations:
            scores = [e.overall_score for e in evaluations if e.overall_score is not None]
            avg_score = sum(scores) / len(scores) if scores else 0.0

            # Count competency levels
            for e in evaluations:
                level = e.overall_competency_level or "UNKNOWN"
                competency_distribution[level] = competency_distribution.get(level, 0) + 1

        # Get risks summary
        risks = db.query(RiskDB).filter(
            RiskDB.session_id.in_(session_ids)
        ).all()

        risk_summary = RiskSummary(
            total_risks=len(risks),
            critical_count=len([r for r in risks if r.risk_level == "critical"]),
            high_count=len([r for r in risks if r.risk_level == "high"]),
            medium_count=len([r for r in risks if r.risk_level == "medium"]),
            low_count=len([r for r in risks if r.risk_level == "low"]),
        )

        # Build per-student performance
        student_ids = list(set(s.student_id for s in sessions))
        student_performance = []

        for student_id in student_ids:
            student_sessions = [s for s in sessions if s.student_id == student_id]
            student_session_ids = [s.id for s in student_sessions]

            student_evals = [e for e in evaluations if e.session_id in student_session_ids]
            student_risks = [r for r in risks if r.session_id in student_session_ids]
            student_traces = [t for t in traces if t.session_id in student_session_ids]

            student_avg_score = 0.0
            competency_level = "INICIAL"
            if student_evals:
                scores = [e.overall_score for e in student_evals if e.overall_score]
                student_avg_score = sum(scores) / len(scores) if scores else 0.0
                competency_level = student_evals[-1].overall_competency_level or "INICIAL"

            student_ai_dep = 0.0
            if student_traces:
                ai_invs = [t.ai_involvement for t in student_traces if t.ai_involvement is not None]
                student_ai_dep = sum(ai_invs) / len(ai_invs) if ai_invs else 0.0

            student_performance.append(StudentPerformance(
                student_id=student_id,
                sessions_count=len(student_sessions),
                avg_score=student_avg_score,
                competency_level=competency_level,
                ai_dependency=student_ai_dep,
                risks_detected=len(student_risks),
            ))

        logger.info(
            "Activity report generated",
            extra={"activity_id": activity_id, "total_sessions": total_sessions},
        )

        return APIResponse(
            success=True,
            data=ActivityReportResponse(
                activity_id=activity_id,
                activity_name=activity_name,
                total_sessions=total_sessions,
                completion_rate=completion_rate,
                avg_score=avg_score,
                avg_ai_dependency=avg_ai_dependency,
                student_performance=student_performance,
                risk_summary=risk_summary,
                competency_distribution=competency_distribution,
            ),
            message=f"Activity report generated for {total_sessions} sessions",
        )

    except Exception as e:
        logger.error(
            "Error generating activity report",
            exc_info=True,
            extra={"activity_id": activity_id, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating activity report: {str(e)}",
        )


VALID_ANALYTICS_PERIODS = {"day", "week", "month", "year"}


@router.get(
    "/analytics",
    response_model=APIResponse[LearningAnalyticsResponse],
    summary="Get learning analytics",
    description="Get learning analytics for a time period (Frontend compatibility). Requires teacher role.",
)
async def get_learning_analytics(
    period: str = Query(
        default="week",
        description="Time period: day, week, month, year",
        pattern="^(day|week|month|year)$",
    ),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_role),
) -> APIResponse[LearningAnalyticsResponse]:
    """
    Get learning analytics with trends and usage statistics.

    Provides aggregate analytics including:
    - Total students and sessions
    - Average session duration
    - Most used AI agents
    - Competency trends over time
    - Risk trends over time

    Valid period values: day, week, month, year
    """
    # Validate period parameter
    if period not in VALID_ANALYTICS_PERIODS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period '{period}'. Valid values: {', '.join(sorted(VALID_ANALYTICS_PERIODS))}",
        )

    try:
        # Calculate date range based on period
        now = utc_now()
        if period == "day":
            start_date = now - timedelta(days=1)
        elif period == "week":
            start_date = now - timedelta(weeks=1)
        elif period == "month":
            start_date = now - timedelta(days=30)
        else:  # year
            start_date = now - timedelta(days=365)

        # Get sessions in period
        sessions = db.query(SessionDB).filter(
            SessionDB.start_time >= start_date
        ).all()

        if not sessions:
            return APIResponse(
                success=True,
                data=LearningAnalyticsResponse(
                    period=period,
                    total_students=0,
                    total_sessions=0,
                    avg_session_duration=0.0,
                    most_used_agents=[],
                    competency_trends=[],
                    risk_trends=[],
                ),
                message=f"No data found for period: {period}",
            )

        session_ids = [s.id for s in sessions]
        total_sessions = len(sessions)
        total_students = len(set(s.student_id for s in sessions))

        # Calculate average session duration (in minutes)
        durations = []
        for s in sessions:
            if s.end_time and s.start_time:
                duration = (s.end_time - s.start_time).total_seconds() / 60
                durations.append(duration)
        avg_session_duration = sum(durations) / len(durations) if durations else 0.0

        # Get agent usage from traces
        traces = db.query(CognitiveTraceDB).filter(
            CognitiveTraceDB.session_id.in_(session_ids)
        ).all()

        # Count agent usage (using session mode as proxy)
        agent_counts = {}
        for s in sessions:
            mode = s.mode or "TUTOR"
            agent_counts[mode] = agent_counts.get(mode, 0) + 1

        most_used_agents = [
            AgentUsage(
                agent=agent,
                usage_count=count,
                avg_satisfaction=0.8,  # Placeholder - would need satisfaction data
            )
            for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

        # Build competency trends (simplified - group by date)
        evaluations = db.query(EvaluationDB).filter(
            EvaluationDB.session_id.in_(session_ids)
        ).all()

        competency_by_date = {}
        for e in evaluations:
            date_str = e.created_at.strftime("%Y-%m-%d") if e.created_at else "unknown"
            if date_str not in competency_by_date:
                competency_by_date[date_str] = {"scores": [], "level": "INICIAL"}
            if e.overall_score:
                competency_by_date[date_str]["scores"].append(e.overall_score)

        competency_trends = [
            CompetencyTrend(
                date=date,
                competency="overall",
                avg_score=sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0.0,
            )
            for date, data in sorted(competency_by_date.items())
        ]

        # Build risk trends
        risks = db.query(RiskDB).filter(
            RiskDB.session_id.in_(session_ids)
        ).all()

        risk_by_date_level = {}
        for r in risks:
            date_str = r.created_at.strftime("%Y-%m-%d") if r.created_at else "unknown"
            level = r.risk_level or "unknown"
            key = (date_str, level)
            risk_by_date_level[key] = risk_by_date_level.get(key, 0) + 1

        risk_trends = [
            RiskTrendData(
                date=key[0],
                risk_level=key[1],
                count=count,
            )
            for key, count in sorted(risk_by_date_level.items())
        ]

        logger.info(
            "Learning analytics generated",
            extra={"period": period, "total_sessions": total_sessions},
        )

        return APIResponse(
            success=True,
            data=LearningAnalyticsResponse(
                period=period,
                total_students=total_students,
                total_sessions=total_sessions,
                avg_session_duration=avg_session_duration,
                most_used_agents=most_used_agents,
                competency_trends=competency_trends,
                risk_trends=risk_trends,
            ),
            message=f"Analytics generated for {total_sessions} sessions",
        )

    except Exception as e:
        logger.error(
            "Error generating learning analytics",
            exc_info=True,
            extra={"period": period, "error": str(e)},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating analytics: {str(e)}",
        )
