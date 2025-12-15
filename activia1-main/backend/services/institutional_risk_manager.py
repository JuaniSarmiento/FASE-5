"""
InstitutionalRiskManager - SPRINT 5 HU-DOC-010

Servicio para gestión proactiva de riesgos a nivel institucional.

Funcionalidades:
- Detección automática de alertas basadas en umbrales
- Creación de planes de remediación para estudiantes en riesgo
- Asignación de alertas a docentes
- Seguimiento de resolución de alertas
- Métricas de efectividad de intervenciones

Audiencia: Coordinadores, administradores, docentes
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..database.models import (
    SessionDB,
    CognitiveTraceDB,
    RiskDB,
    EvaluationDB,
)
from ..database.repositories import (
    RiskAlertRepository,
    RemediationPlanRepository,
    RiskRepository,
)
from ..models.risk import RiskLevel, RiskDimension

logger = logging.getLogger(__name__)


class InstitutionalRiskManager:
    """
    Gestor de riesgos institucionales

    Monitorea patrones de riesgo a nivel estudiante, actividad, curso
    e institución, generando alertas automáticas y planes de remediación.
    """

    # Detection thresholds
    THRESHOLDS = {
        "ai_dependency_spike": 0.7,  # AI involvement > 0.7
        "critical_risk_surge": 2,  # 2+ critical risks in period
        "session_inactivity_days": 7,  # No sessions for 7 days
        "low_competency_threshold": 3.0,  # Overall score < 3.0/10
        "academic_integrity_threshold": 1,  # 1+ integrity risk
    }

    def __init__(
        self,
        db_session: Session,
        alert_repo: Optional[RiskAlertRepository] = None,
        plan_repo: Optional[RemediationPlanRepository] = None,
        risk_repo: Optional[RiskRepository] = None,
    ):
        """
        Initialize InstitutionalRiskManager

        Args:
            db_session: SQLAlchemy database session
            alert_repo: Repository for alerts (optional)
            plan_repo: Repository for remediation plans (optional)
            risk_repo: Repository for risks (optional)
        """
        self.db = db_session
        self.alert_repo = alert_repo or RiskAlertRepository(db_session)
        self.plan_repo = plan_repo or RemediationPlanRepository(db_session)
        self.risk_repo = risk_repo or RiskRepository(db_session)

    def scan_for_alerts(
        self,
        student_ids: Optional[List[str]] = None,
        activity_ids: Optional[List[str]] = None,
        course_ids: Optional[List[str]] = None,
        lookback_days: int = 7,
    ) -> List[Dict[str, Any]]:
        """
        Scan for risk alerts based on detection rules

        Args:
            student_ids: Specific students to scan (None = all)
            activity_ids: Specific activities to scan (None = all)
            course_ids: Specific courses to scan (None = all)
            lookback_days: Days to look back for analysis

        Returns:
            List of created alerts
        """
        logger.info(
            "Scanning for risk alerts",
            extra={
                "student_count": len(student_ids) if student_ids else "all",
                "lookback_days": lookback_days,
            },
        )

        alerts_created = []
        period_start = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        # Get students to scan
        if student_ids is None:
            # Get all active students (with sessions in period)
            student_ids = [
                s[0]
                for s in self.db.query(SessionDB.student_id)
                .filter(SessionDB.start_time >= period_start)
                .distinct()
                .all()
            ]

        # Scan each student for alerts
        for student_id in student_ids:
            # AI Dependency Spike
            alert = self._check_ai_dependency_spike(student_id, period_start)
            if alert:
                alerts_created.append(alert)

            # Critical Risk Surge
            alert = self._check_critical_risk_surge(student_id, period_start)
            if alert:
                alerts_created.append(alert)

            # Academic Integrity
            alert = self._check_academic_integrity(student_id, period_start)
            if alert:
                alerts_created.append(alert)

            # Session Inactivity
            alert = self._check_session_inactivity(student_id)
            if alert:
                alerts_created.append(alert)

            # Low Competency
            alert = self._check_low_competency(student_id, period_start)
            if alert:
                alerts_created.append(alert)

        logger.info(
            "Alert scan completed",
            extra={
                "alerts_created": len(alerts_created),
                "students_scanned": len(student_ids),
            },
        )
        return alerts_created

    def create_remediation_plan(
        self,
        student_id: str,
        teacher_id: str,
        trigger_risk_ids: List[str],
        plan_type: str,
        description: str,
        objectives: List[str],
        recommended_actions: List[Dict[str, Any]],
        activity_id: Optional[str] = None,
        duration_days: int = 14,
    ) -> Dict[str, Any]:
        """
        Create a remediation plan for a student

        Args:
            student_id: Student ID
            teacher_id: Teacher creating the plan
            trigger_risk_ids: Risk IDs that triggered this plan
            plan_type: Type of plan (tutoring, practice_exercises, etc.)
            description: Plan description
            objectives: List of objectives
            recommended_actions: List of actions with deadlines
            activity_id: Optional activity ID
            duration_days: Plan duration in days (default: 14)

        Returns:
            Created plan data
        """
        start_date = datetime.now(timezone.utc)
        target_completion = start_date + timedelta(days=duration_days)

        plan = self.plan_repo.create(
            student_id=student_id,
            teacher_id=teacher_id,
            plan_type=plan_type,
            description=description,
            start_date=start_date,
            target_completion_date=target_completion,
            activity_id=activity_id,
            trigger_risks=trigger_risk_ids,
            objectives=objectives,
            recommended_actions=recommended_actions,
        )

        logger.info(
            "Remediation plan created",
            extra={
                "plan_id": plan.id,
                "student_id": student_id,
                "teacher_id": teacher_id,
                "duration_days": duration_days,
            },
        )

        return {
            "plan_id": plan.id,
            "student_id": student_id,
            "teacher_id": teacher_id,
            "plan_type": plan_type,
            "description": description,
            "start_date": start_date.isoformat(),
            "target_completion_date": target_completion.isoformat(),
            "objectives": objectives,
            "recommended_actions": recommended_actions,
            "status": "pending",
        }

    def assign_alert(self, alert_id: str, teacher_id: str) -> Dict[str, Any]:
        """
        Assign an alert to a teacher

        Args:
            alert_id: Alert ID
            teacher_id: Teacher to assign to

        Returns:
            Updated alert data
        """
        alert = self.alert_repo.assign_to(alert_id, teacher_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        logger.info(
            "Alert assigned",
            extra={"alert_id": alert_id, "teacher_id": teacher_id},
        )

        return {
            "alert_id": alert.id,
            "assigned_to": alert.assigned_to,
            "assigned_at": alert.assigned_at.isoformat() if alert.assigned_at else None,
            "status": alert.status,
        }

    def acknowledge_alert(self, alert_id: str, teacher_id: str) -> Dict[str, Any]:
        """
        Acknowledge an alert (teacher has seen it)

        Args:
            alert_id: Alert ID
            teacher_id: Teacher acknowledging

        Returns:
            Updated alert data
        """
        alert = self.alert_repo.acknowledge(alert_id, teacher_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        logger.info(
            "Alert acknowledged",
            extra={"alert_id": alert_id, "teacher_id": teacher_id},
        )

        return {
            "alert_id": alert.id,
            "acknowledged_by": alert.acknowledged_by,
            "acknowledged_at": alert.acknowledged_at.isoformat()
            if alert.acknowledged_at
            else None,
            "status": alert.status,
        }

    def resolve_alert(
        self,
        alert_id: str,
        resolution_notes: str,
        remediation_plan_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Resolve an alert

        Args:
            alert_id: Alert ID
            resolution_notes: Notes on resolution
            remediation_plan_id: Optional plan ID if plan was created

        Returns:
            Updated alert data
        """
        alert = self.alert_repo.resolve(alert_id, resolution_notes, remediation_plan_id)
        if not alert:
            raise ValueError(f"Alert {alert_id} not found")

        logger.info(
            "Alert resolved",
            extra={
                "alert_id": alert_id,
                "remediation_plan_id": remediation_plan_id,
            },
        )

        return {
            "alert_id": alert.id,
            "status": alert.status,
            "resolution_notes": alert.resolution_notes,
            "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
            "remediation_plan_id": alert.remediation_plan_id,
        }

    def get_dashboard_metrics(
        self, teacher_id: Optional[str] = None, course_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get dashboard metrics for risk management

        Args:
            teacher_id: Filter by teacher (optional)
            course_id: Filter by course (optional)

        Returns:
            Dashboard metrics
        """
        # Open alerts
        query = self.db.query(self.alert_repo.db.query().count())
        if teacher_id:
            # Get alerts assigned to teacher or unassigned
            open_alerts_count = (
                self.db.query(func.count())
                .select_from(
                    self.alert_repo.db.query()
                    .filter(
                        and_(
                            self.alert_repo.status == "open",
                            (
                                self.alert_repo.assigned_to == teacher_id,
                                self.alert_repo.assigned_to.is_(None),
                            ),
                        )
                    )
                )
                .scalar()
            )
        else:
            from ..database.models import RiskAlertDB

            open_alerts_count = (
                self.db.query(RiskAlertDB).filter(RiskAlertDB.status == "open").count()
            )

        # Critical alerts
        from ..database.models import RiskAlertDB

        critical_alerts_count = (
            self.db.query(RiskAlertDB)
            .filter(
                RiskAlertDB.severity == "critical", RiskAlertDB.status.in_(["open", "acknowledged"])
            )
            .count()
        )

        # Active remediation plans
        from ..database.models import RemediationPlanDB

        active_plans_query = self.db.query(RemediationPlanDB).filter(
            RemediationPlanDB.status.in_(["pending", "in_progress"])
        )
        if teacher_id:
            active_plans_query = active_plans_query.filter(
                RemediationPlanDB.teacher_id == teacher_id
            )
        active_plans_count = active_plans_query.count()

        # Resolution rate (last 30 days)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        total_alerts_30d = (
            self.db.query(RiskAlertDB)
            .filter(RiskAlertDB.detected_at >= thirty_days_ago)
            .count()
        )
        resolved_alerts_30d = (
            self.db.query(RiskAlertDB)
            .filter(
                RiskAlertDB.detected_at >= thirty_days_ago,
                RiskAlertDB.status == "resolved",
            )
            .count()
        )
        resolution_rate = (
            round(resolved_alerts_30d / total_alerts_30d * 100, 1)
            if total_alerts_30d > 0
            else 0
        )

        return {
            "open_alerts": open_alerts_count,
            "critical_alerts": critical_alerts_count,
            "active_remediation_plans": active_plans_count,
            "resolution_rate_30d": resolution_rate,
            "total_alerts_30d": total_alerts_30d,
            "resolved_alerts_30d": resolved_alerts_30d,
        }

    # ==========================================================================
    # PRIVATE DETECTION METHODS
    # ==========================================================================

    def _check_ai_dependency_spike(
        self, student_id: str, period_start: datetime
    ) -> Optional[Dict[str, Any]]:
        """Check for AI dependency spike"""
        avg_ai_dependency = (
            self.db.query(func.avg(CognitiveTraceDB.ai_involvement))
            .filter(
                CognitiveTraceDB.student_id == student_id,
                CognitiveTraceDB.created_at >= period_start,
            )
            .scalar()
            or 0.0
        )

        threshold = self.THRESHOLDS["ai_dependency_spike"]
        if avg_ai_dependency > threshold:
            alert = self.alert_repo.create(
                alert_type="ai_dependency_spike",
                severity="high",
                scope="student",
                student_id=student_id,
                title=f"Alta dependencia de IA detectada: {student_id}",
                description=f"El estudiante presenta un promedio de dependencia de IA de {avg_ai_dependency:.2f} (umbral: {threshold})",
                detection_rule=f"ai_dependency > {threshold}",
                threshold_value=threshold,
                actual_value=float(avg_ai_dependency),
                evidence=[],
            )

            logger.warning(
                "AI dependency spike detected",
                extra={
                    "student_id": student_id,
                    "avg_ai_dependency": float(avg_ai_dependency),
                    "alert_id": alert.id,
                },
            )

            return {
                "alert_id": alert.id,
                "student_id": student_id,
                "alert_type": "ai_dependency_spike",
                "severity": "high",
                "actual_value": float(avg_ai_dependency),
            }

        return None

    def _check_critical_risk_surge(
        self, student_id: str, period_start: datetime
    ) -> Optional[Dict[str, Any]]:
        """Check for critical risk surge"""
        # DB stores lowercase values
        critical_risks = (
            self.db.query(RiskDB)
            .filter(
                RiskDB.student_id == student_id,
                RiskDB.risk_level == "critical",
                RiskDB.created_at >= period_start,
            )
            .all()
        )

        threshold = self.THRESHOLDS["critical_risk_surge"]
        if len(critical_risks) >= threshold:
            alert = self.alert_repo.create(
                alert_type="critical_risk_surge",
                severity="critical",
                scope="student",
                student_id=student_id,
                title=f"Múltiples riesgos críticos: {student_id}",
                description=f"El estudiante presenta {len(critical_risks)} riesgos críticos (umbral: {threshold})",
                detection_rule=f"critical_risks >= {threshold}",
                threshold_value=float(threshold),
                actual_value=float(len(critical_risks)),
                evidence=[r.id for r in critical_risks],
            )

            logger.critical(
                "Critical risk surge detected",
                extra={
                    "student_id": student_id,
                    "critical_risks_count": len(critical_risks),
                    "alert_id": alert.id,
                },
            )

            return {
                "alert_id": alert.id,
                "student_id": student_id,
                "alert_type": "critical_risk_surge",
                "severity": "critical",
                "actual_value": len(critical_risks),
            }

        return None

    def _check_academic_integrity(
        self, student_id: str, period_start: datetime
    ) -> Optional[Dict[str, Any]]:
        """Check for academic integrity risks"""
        # DB stores lowercase values
        integrity_risks = (
            self.db.query(RiskDB)
            .filter(
                RiskDB.student_id == student_id,
                RiskDB.dimension == "ethical",
                RiskDB.created_at >= period_start,
            )
            .all()
        )

        threshold = self.THRESHOLDS["academic_integrity_threshold"]
        if len(integrity_risks) >= threshold:
            alert = self.alert_repo.create(
                alert_type="academic_integrity",
                severity="high",
                scope="student",
                student_id=student_id,
                title=f"Riesgo de integridad académica: {student_id}",
                description=f"Detectados {len(integrity_risks)} riesgos éticos/integridad",
                detection_rule=f"ethical_risks >= {threshold}",
                threshold_value=float(threshold),
                actual_value=float(len(integrity_risks)),
                evidence=[r.id for r in integrity_risks],
            )

            logger.warning(
                "Academic integrity risk detected",
                extra={
                    "student_id": student_id,
                    "integrity_risks_count": len(integrity_risks),
                    "alert_id": alert.id,
                },
            )

            return {
                "alert_id": alert.id,
                "student_id": student_id,
                "alert_type": "academic_integrity",
                "severity": "high",
                "actual_value": len(integrity_risks),
            }

        return None

    def _check_session_inactivity(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Check for session inactivity"""
        threshold_days = self.THRESHOLDS["session_inactivity_days"]
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=threshold_days)

        last_session = (
            self.db.query(SessionDB)
            .filter(SessionDB.student_id == student_id)
            .order_by(SessionDB.start_time.desc())
            .first()
        )

        if last_session and last_session.start_time < cutoff_date:
            days_inactive = (datetime.now(timezone.utc) - last_session.start_time).days

            alert = self.alert_repo.create(
                alert_type="session_inactivity",
                severity="medium",
                scope="student",
                student_id=student_id,
                title=f"Inactividad prolongada: {student_id}",
                description=f"El estudiante lleva {days_inactive} días sin sesiones (umbral: {threshold_days} días)",
                detection_rule=f"days_since_last_session >= {threshold_days}",
                threshold_value=float(threshold_days),
                actual_value=float(days_inactive),
                evidence=[],
            )

            logger.info(
                "Session inactivity detected",
                extra={
                    "student_id": student_id,
                    "days_inactive": days_inactive,
                    "alert_id": alert.id,
                },
            )

            return {
                "alert_id": alert.id,
                "student_id": student_id,
                "alert_type": "session_inactivity",
                "severity": "medium",
                "actual_value": days_inactive,
            }

        return None

    def _check_low_competency(
        self, student_id: str, period_start: datetime
    ) -> Optional[Dict[str, Any]]:
        """Check for low competency scores"""
        latest_eval = (
            self.db.query(EvaluationDB)
            .filter(
                EvaluationDB.student_id == student_id,
                EvaluationDB.created_at >= period_start,
            )
            .order_by(EvaluationDB.created_at.desc())
            .first()
        )

        threshold = self.THRESHOLDS["low_competency_threshold"]
        if latest_eval and latest_eval.overall_score < threshold:
            alert = self.alert_repo.create(
                alert_type="low_competency",
                severity="medium",
                scope="student",
                student_id=student_id,
                title=f"Competencia baja detectada: {student_id}",
                description=f"Evaluación con puntaje {latest_eval.overall_score}/10 (umbral: {threshold})",
                detection_rule=f"overall_score < {threshold}",
                threshold_value=threshold,
                actual_value=latest_eval.overall_score,
                evidence=[latest_eval.id],
            )

            logger.warning(
                "Low competency detected",
                extra={
                    "student_id": student_id,
                    "overall_score": latest_eval.overall_score,
                    "alert_id": alert.id,
                },
            )

            return {
                "alert_id": alert.id,
                "student_id": student_id,
                "alert_type": "low_competency",
                "severity": "medium",
                "actual_value": latest_eval.overall_score,
            }

        return None
