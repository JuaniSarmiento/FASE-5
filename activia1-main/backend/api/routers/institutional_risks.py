"""
Institutional Risk Management API Endpoints - SPRINT 5 HU-DOC-010

Endpoints:
- POST /admin/risks/scan - Scan for risk alerts
- GET /admin/risks/alerts - Get all alerts (with filters)
- GET /admin/risks/dashboard - Get dashboard metrics
- POST /admin/risks/alerts/{alert_id}/assign - Assign alert to teacher
- POST /admin/risks/alerts/{alert_id}/acknowledge - Acknowledge alert
- POST /admin/risks/alerts/{alert_id}/resolve - Resolve alert
- POST /admin/risks/remediation - Create remediation plan
- GET /admin/risks/remediation/{plan_id} - Get remediation plan
- PUT /admin/risks/remediation/{plan_id}/status - Update plan status
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ..deps import get_db
from ...database.repositories import (
    RiskAlertRepository,
    RemediationPlanRepository,
)
from ...services.institutional_risk_manager import InstitutionalRiskManager
from ..schemas.common import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/risks", tags=["Institutional Risk Management"])


# =============================================================================
# REQUEST/RESPONSE SCHEMAS
# =============================================================================


class ScanAlertsRequest(BaseModel):
    """Request to scan for risk alerts"""

    student_ids: Optional[List[str]] = Field(None, description="Specific students (None = all)")
    activity_ids: Optional[List[str]] = Field(None, description="Specific activities (None = all)")
    course_ids: Optional[List[str]] = Field(None, description="Specific courses (None = all)")
    lookback_days: int = Field(default=7, description="Days to look back")


class RemediationPlanRequest(BaseModel):
    """Request to create remediation plan"""

    student_id: str = Field(description="Student ID")
    teacher_id: str = Field(description="Teacher creating plan")
    trigger_risk_ids: List[str] = Field(description="Risk IDs triggering plan")
    plan_type: str = Field(description="Plan type (tutoring, practice_exercises, etc.)")
    description: str = Field(description="Plan description")
    objectives: List[str] = Field(description="List of objectives")
    recommended_actions: List[Dict[str, Any]] = Field(description="List of actions")
    activity_id: Optional[str] = Field(None, description="Optional activity ID")
    duration_days: int = Field(default=14, description="Plan duration")


class AssignAlertRequest(BaseModel):
    """Request to assign alert"""

    teacher_id: str = Field(description="Teacher to assign to")


class AcknowledgeAlertRequest(BaseModel):
    """Request to acknowledge alert"""

    teacher_id: str = Field(description="Teacher acknowledging")


class ResolveAlertRequest(BaseModel):
    """Request to resolve alert"""

    resolution_notes: str = Field(description="Resolution notes")
    remediation_plan_id: Optional[str] = Field(None, description="Optional plan ID")


class UpdatePlanStatusRequest(BaseModel):
    """Request to update plan status"""

    status: str = Field(description="New status (pending, in_progress, completed, cancelled)")
    progress_notes: Optional[str] = Field(None, description="Progress notes")
    completion_evidence: Optional[List[str]] = Field(None, description="Evidence of completion")


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post(
    "/scan",
    response_model=APIResponse[List[dict]],
    summary="Scan for risk alerts",
    description="""
    Proactively scans for institutional risk patterns across students, activities, and courses.

    **Detection Rules**:
    - **AI Dependency Spike**: `ai_involvement > 0.7` for 3+ consecutive sessions
    - **Critical Risk Surge**: `critical_risks >= 2` in lookback window
    - **Academic Integrity**: `ethical_risks >= 1` (plagiarism, undisclosed AI use)
    - **Session Inactivity**: `days_since_last_session >= 7` for active students
    - **Low Competency**: `overall_score < 3.0/10` with no improvement trend

    **Thresholds** (configurable):
    - AI dependency: 0.7 (70% AI involvement)
    - Critical risk count: 2
    - Inactivity days: 7
    - Low competency score: 3.0/10

    **Returns**: List of created alerts with severity, evidence, and recommended actions.
    """,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Alerts created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "alert_id": "alert_abc123",
                                "alert_type": "ai_dependency_spike",
                                "severity": "high",
                                "scope": "student",
                                "title": "High AI Dependency Detected",
                                "description": "Student shows 85% AI involvement across 4 sessions",
                                "student_id": "student_001",
                                "detection_rule": "ai_involvement > 0.7 for 3+ sessions",
                                "threshold_value": 0.7,
                                "actual_value": 0.85,
                                "evidence": ["session_1", "session_2", "session_3", "session_4"],
                            }
                        ],
                        "message": "Scan completed: 1 alerts created",
                    }
                }
            },
        },
        500: {"description": "Internal server error during scan"},
    },
)
async def scan_for_alerts(
    request: ScanAlertsRequest,
    db: Session = Depends(get_db),
) -> APIResponse[List[dict]]:
    """
    Scan for risk alerts across institutional scope

    Proactively detects 5 types of risk patterns:
    1. **AI Dependency Spike** - Students over-relying on AI
    2. **Critical Risk Surge** - Multiple high-severity risks
    3. **Academic Integrity** - Ethical violations
    4. **Session Inactivity** - Students not engaging
    5. **Low Competency** - Consistently low performance

    Each alert includes:
    - Severity level (low, medium, high, critical)
    - Detection rule that triggered
    - Threshold vs actual values
    - Evidence (session IDs, risk IDs)
    - Recommended actions for teachers

    **Example Request**:
    ```json
    {
      "student_ids": null,
      "activity_ids": ["prog2_tp1"],
      "course_ids": ["PROG2_2025"],
      "lookback_days": 14
    }
    ```

    **Example Response**:
    ```json
    {
      "success": true,
      "data": [
        {
          "alert_id": "alert_abc123",
          "alert_type": "ai_dependency_spike",
          "severity": "high",
          "title": "High AI Dependency Detected",
          "student_id": "student_001",
          "actual_value": 0.85,
          "threshold_value": 0.7
        }
      ],
      "message": "Scan completed: 1 alerts created"
    }
    ```
    """
    try:
        manager = InstitutionalRiskManager(db)
        alerts = manager.scan_for_alerts(
            student_ids=request.student_ids,
            activity_ids=request.activity_ids,
            course_ids=request.course_ids,
            lookback_days=request.lookback_days,
        )

        logger.info(
            "Alert scan completed",
            extra={"alerts_created": len(alerts), "lookback_days": request.lookback_days},
        )

        return APIResponse(
            success=True,
            data=alerts,
            message=f"Scan completed: {len(alerts)} alerts created",
        )

    except Exception as e:
        logger.error("Error scanning for alerts", exc_info=True, extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error scanning: {str(e)}",
        )


@router.get(
    "/alerts",
    response_model=APIResponse[List[dict]],
    summary="Get risk alerts",
    description="Get all risk alerts with optional filters",
)
async def get_alerts(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    student_id: Optional[str] = Query(None, description="Filter by student"),
    assigned_to: Optional[str] = Query(None, description="Filter by assignee"),
    limit: int = Query(50, description="Max results"),
    db: Session = Depends(get_db),
) -> APIResponse[List[dict]]:
    """
    Get risk alerts with filters

    Supports filtering by status, severity, student, assignee.
    """
    alert_repo = RiskAlertRepository(db)

    # Apply filters
    if student_id:
        alerts = alert_repo.get_by_student(student_id, status=status_filter)
    elif assigned_to:
        alerts = alert_repo.get_assigned_to(assigned_to, status=status_filter)
    elif severity:
        alerts = alert_repo.get_by_severity(severity, status=status_filter)
    else:
        # Get all alerts (limited)
        from ...database.models import RiskAlertDB
        from sqlalchemy import desc

        query = db.query(RiskAlertDB).order_by(desc(RiskAlertDB.detected_at))
        if status_filter:
            query = query.filter(RiskAlertDB.status == status_filter)
        alerts = query.limit(limit).all()

    alerts_data = [
        {
            "alert_id": a.id,
            "alert_type": a.alert_type,
            "severity": a.severity,
            "scope": a.scope,
            "title": a.title,
            "description": a.description,
            "student_id": a.student_id,
            "activity_id": a.activity_id,
            "course_id": a.course_id,
            "detected_at": a.detected_at.isoformat(),
            "status": a.status,
            "assigned_to": a.assigned_to,
            "threshold_value": a.threshold_value,
            "actual_value": a.actual_value,
        }
        for a in alerts
    ]

    logger.info("Alerts retrieved", extra={"count": len(alerts_data)})

    return APIResponse(
        success=True,
        data=alerts_data,
        message=f"Retrieved {len(alerts_data)} alerts",
    )


@router.get(
    "/dashboard",
    response_model=APIResponse[dict],
    summary="Get dashboard metrics",
    description="Get risk management dashboard metrics",
)
async def get_dashboard(
    teacher_id: Optional[str] = Query(None, description="Filter by teacher"),
    course_id: Optional[str] = Query(None, description="Filter by course"),
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Get dashboard metrics

    Returns:
    - Open alerts count
    - Critical alerts count
    - Active remediation plans
    - Resolution rate
    """
    try:
        manager = InstitutionalRiskManager(db)
        metrics = manager.get_dashboard_metrics(teacher_id=teacher_id, course_id=course_id)

        logger.info("Dashboard metrics retrieved", extra={"teacher_id": teacher_id})

        return APIResponse(
            success=True,
            data=metrics,
            message="Dashboard metrics retrieved",
        )

    except Exception as e:
        logger.error("Error getting dashboard metrics", exc_info=True, extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving metrics: {str(e)}",
        )


@router.post(
    "/alerts/{alert_id}/assign",
    response_model=APIResponse[dict],
    summary="Assign alert to teacher",
    description="Assign a risk alert to a teacher for handling",
)
async def assign_alert(
    alert_id: str,
    request: AssignAlertRequest,
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Assign alert to teacher

    Teachers can then acknowledge and resolve assigned alerts.
    """
    try:
        manager = InstitutionalRiskManager(db)
        result = manager.assign_alert(alert_id, request.teacher_id)

        logger.info(
            "Alert assigned",
            extra={"alert_id": alert_id, "teacher_id": request.teacher_id},
        )

        return APIResponse(
            success=True,
            data=result,
            message=f"Alert assigned to {request.teacher_id}",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Error assigning alert", exc_info=True, extra={"alert_id": alert_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning alert: {str(e)}",
        )


@router.post(
    "/alerts/{alert_id}/acknowledge",
    response_model=APIResponse[dict],
    summary="Acknowledge alert",
    description="Teacher acknowledges they have seen the alert",
)
async def acknowledge_alert(
    alert_id: str,
    request: AcknowledgeAlertRequest,
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Acknowledge alert

    Changes status to 'acknowledged'.
    """
    try:
        manager = InstitutionalRiskManager(db)
        result = manager.acknowledge_alert(alert_id, request.teacher_id)

        logger.info(
            "Alert acknowledged",
            extra={"alert_id": alert_id, "teacher_id": request.teacher_id},
        )

        return APIResponse(
            success=True,
            data=result,
            message="Alert acknowledged",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Error acknowledging alert", exc_info=True, extra={"alert_id": alert_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error acknowledging alert: {str(e)}",
        )


@router.post(
    "/alerts/{alert_id}/resolve",
    response_model=APIResponse[dict],
    summary="Resolve alert",
    description="Mark alert as resolved with notes",
)
async def resolve_alert(
    alert_id: str,
    request: ResolveAlertRequest,
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Resolve alert

    Marks alert as resolved and optionally links to remediation plan.
    """
    try:
        manager = InstitutionalRiskManager(db)
        result = manager.resolve_alert(
            alert_id,
            request.resolution_notes,
            request.remediation_plan_id,
        )

        logger.info("Alert resolved", extra={"alert_id": alert_id})

        return APIResponse(
            success=True,
            data=result,
            message="Alert resolved",
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error("Error resolving alert", exc_info=True, extra={"alert_id": alert_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resolving alert: {str(e)}",
        )


@router.post(
    "/remediation",
    response_model=APIResponse[dict],
    summary="Create remediation plan",
    description="Create a remediation plan for a student at risk",
    status_code=status.HTTP_201_CREATED,
)
async def create_remediation_plan(
    request: RemediationPlanRequest,
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Create remediation plan

    Plans include objectives, actions, and deadlines.
    """
    try:
        manager = InstitutionalRiskManager(db)
        plan = manager.create_remediation_plan(
            student_id=request.student_id,
            teacher_id=request.teacher_id,
            trigger_risk_ids=request.trigger_risk_ids,
            plan_type=request.plan_type,
            description=request.description,
            objectives=request.objectives,
            recommended_actions=request.recommended_actions,
            activity_id=request.activity_id,
            duration_days=request.duration_days,
        )

        logger.info(
            "Remediation plan created",
            extra={"plan_id": plan["plan_id"], "student_id": request.student_id},
        )

        return APIResponse(
            success=True,
            data=plan,
            message="Remediation plan created",
        )

    except Exception as e:
        logger.error(
            "Error creating remediation plan",
            exc_info=True,
            extra={"student_id": request.student_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating plan: {str(e)}",
        )


@router.get(
    "/remediation/{plan_id}",
    response_model=APIResponse[dict],
    summary="Get remediation plan",
    description="Get remediation plan details",
)
async def get_remediation_plan(
    plan_id: str,
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Get remediation plan by ID

    Returns complete plan details.
    """
    plan_repo = RemediationPlanRepository(db)
    plan = plan_repo.get_by_id(plan_id)

    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Remediation plan '{plan_id}' not found",
        )

    plan_data = {
        "plan_id": plan.id,
        "student_id": plan.student_id,
        "teacher_id": plan.teacher_id,
        "activity_id": plan.activity_id,
        "plan_type": plan.plan_type,
        "description": plan.description,
        "objectives": plan.objectives,
        "recommended_actions": plan.recommended_actions,
        "start_date": plan.start_date.isoformat(),
        "target_completion_date": plan.target_completion_date.isoformat(),
        "actual_completion_date": plan.actual_completion_date.isoformat()
        if plan.actual_completion_date
        else None,
        "status": plan.status,
        "progress_notes": plan.progress_notes,
        "outcome_evaluation": plan.outcome_evaluation,
        "success_metrics": plan.success_metrics,
        "trigger_risks": plan.trigger_risks,
    }

    logger.info("Remediation plan retrieved", extra={"plan_id": plan_id})

    return APIResponse(
        success=True,
        data=plan_data,
        message="Remediation plan retrieved",
    )


@router.put(
    "/remediation/{plan_id}/status",
    response_model=APIResponse[dict],
    summary="Update plan status",
    description="Update remediation plan status and progress",
)
async def update_plan_status(
    plan_id: str,
    request: UpdatePlanStatusRequest,
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Update plan status

    Tracks progress through: pending → in_progress → completed.
    """
    plan_repo = RemediationPlanRepository(db)

    try:
        plan = plan_repo.update_status(
            plan_id=plan_id,
            status=request.status,
            progress_notes=request.progress_notes,
            completion_evidence=request.completion_evidence,
        )

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Remediation plan '{plan_id}' not found",
            )

        logger.info(
            "Plan status updated",
            extra={"plan_id": plan_id, "status": request.status},
        )

        return APIResponse(
            success=True,
            data={
                "plan_id": plan.id,
                "status": plan.status,
                "progress_notes": plan.progress_notes,
                "updated_at": plan.updated_at.isoformat(),
            },
            message=f"Plan status updated to {request.status}",
        )

    except Exception as e:
        logger.error(
            "Error updating plan status",
            exc_info=True,
            extra={"plan_id": plan_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating plan: {str(e)}",
        )
