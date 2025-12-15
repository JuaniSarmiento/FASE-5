"""
Router para herramientas de docentes

Sprint 3 - HU-DOC-002, HU-DOC-003, HU-DOC-004
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from collections import defaultdict
from datetime import datetime

from backend.core.constants import utc_now
from ..deps import get_db, get_session_repository, get_trace_repository, get_risk_repository, require_teacher_role
from ..schemas.common import APIResponse, PaginationParams
from ...database.repositories import SessionRepository, TraceRepository, RiskRepository

router = APIRouter(prefix="/teacher", tags=["Teacher Tools"])


# FIX EP-6: Maximum number of students for comparison to prevent performance issues
MAX_STUDENTS_COMPARE = 50


@router.get(
    "/students/compare",
    summary="Comparar procesos cognitivos de múltiples estudiantes",
    description="Compara los caminos cognitivos de diferentes estudiantes en la misma actividad (HU-DOC-003). Requiere rol teacher."
)
async def compare_students(
    activity_id: str = Query(..., description="ID de la actividad"),
    student_ids: List[str] = Query(None, description=f"IDs específicos de estudiantes (opcional, máximo {MAX_STUDENTS_COMPARE})"),
    db: Session = Depends(get_db),
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    risk_repo: RiskRepository = Depends(get_risk_repository),
    current_user: dict = Depends(require_teacher_role),
) -> APIResponse[Dict[str, Any]]:
    """
    Compara los procesos cognitivos de múltiples estudiantes en la misma actividad.

    **HU-DOC-003**: Permite al docente identificar patrones, dificultades comunes
    y estrategias exitosas.

    **Métricas comparadas:**
    - Tiempo promedio de resolución
    - Distribución de estados cognitivos
    - Patrones de uso de IA
    - Riesgos más frecuentes
    - Estrategias exitosas vs fallidas

    **Ejemplo:**
    ```bash
    GET /api/v1/teacher/students/compare?activity_id=prog2_tp1_colas
    GET /api/v1/teacher/students/compare?activity_id=prog2_tp1_colas&student_ids=student_001&student_ids=student_002
    ```
    """
    # FIX EP-6: Validate student_ids limit to prevent performance issues
    if student_ids and len(student_ids) > MAX_STUDENTS_COMPARE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many student_ids provided. Maximum allowed: {MAX_STUDENTS_COMPARE}, received: {len(student_ids)}"
        )

    # Obtener todas las sesiones de la actividad
    all_sessions = session_repo.get_by_activity(activity_id)

    if not all_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sessions found for activity '{activity_id}'"
        )

    # Filtrar por estudiantes específicos si se proporcionaron
    if student_ids:
        sessions = [s for s in all_sessions if s.student_id in student_ids]
    else:
        sessions = all_sessions

    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sessions found for specified students in activity '{activity_id}'"
        )

    # Construir comparativa
    students_data = []

    for session in sessions:
        # Obtener trazas del estudiante
        traces = trace_repo.get_by_session(session.id)
        risks = risk_repo.get_by_session(session.id)

        # Calcular duración
        duration_minutes = 0.0
        if session.end_time:
            duration_minutes = (session.end_time - session.start_time).total_seconds() / 60.0

        # Estados cognitivos visitados
        cognitive_states = list(set(t.cognitive_state for t in traces if t.cognitive_state))

        # Promedio de AI involvement
        ai_involvements = [t.ai_involvement or 0.0 for t in traces]
        ai_dependency_avg = sum(ai_involvements) / len(ai_involvements) if ai_involvements else 0.0

        # Riesgos por tipo
        risks_by_type = defaultdict(int)
        for risk in risks:
            risks_by_type[risk.risk_type] += 1

        # Interacciones bloqueadas
        blocked_count = sum(
            1 for t in traces
            if t.trace_metadata and t.trace_metadata.get("blocked")
        )

        students_data.append({
            "student_id": session.student_id,
            "session_id": session.id,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "duration_minutes": round(duration_minutes, 2),
            "total_interactions": len(traces),
            "blocked_interactions": blocked_count,
            "cognitive_states_visited": cognitive_states,
            "ai_dependency_average": round(ai_dependency_avg, 2),
            "risks_total": len(risks),
            "risks_by_type": dict(risks_by_type),
            "status": session.status
        })

    # Calcular estadísticas agregadas
    completed_sessions = [s for s in students_data if s["status"] == "completed"]

    if completed_sessions:
        avg_duration = sum(s["duration_minutes"] for s in completed_sessions) / len(completed_sessions)
        avg_interactions = sum(s["total_interactions"] for s in completed_sessions) / len(completed_sessions)
        avg_ai_dependency = sum(s["ai_dependency_average"] for s in completed_sessions) / len(completed_sessions)
    else:
        avg_duration = 0.0
        avg_interactions = 0.0
        avg_ai_dependency = 0.0

    # Riesgos más comunes
    all_risks = defaultdict(int)
    for student in students_data:
        for risk_type, count in student["risks_by_type"].items():
            all_risks[risk_type] += count

    top_risks = sorted(all_risks.items(), key=lambda x: x[1], reverse=True)[:5]

    # Estados cognitivos más frecuentes
    all_states = defaultdict(int)
    for student in students_data:
        for state in student["cognitive_states_visited"]:
            all_states[state] += 1

    # Preparar respuesta
    comparison = {
        "activity_id": activity_id,
        "students_count": len(students_data),
        "completed_count": len(completed_sessions),
        "in_progress_count": sum(1 for s in students_data if s["status"] == "active"),
        "aggregate_statistics": {
            "average_duration_minutes": round(avg_duration, 2),
            "average_interactions": round(avg_interactions, 2),
            "average_ai_dependency": round(avg_ai_dependency, 2),
            "top_risks": [{"type": r[0], "count": r[1]} for r in top_risks],
            "cognitive_states_distribution": dict(all_states)
        },
        "students": students_data
    }

    return APIResponse(
        success=True,
        data=comparison,
        message=f"Comparativa de {len(students_data)} estudiantes en actividad {activity_id}"
    )


@router.get(
    "/alerts",
    summary="Obtener alertas en tiempo real",
    description="Obtiene alertas de estudiantes con dificultades o riesgos críticos (HU-DOC-004). Requiere rol teacher."
)
async def get_teacher_alerts(
    severity: str = Query("all", description="Filtro por severidad: all, critical, high, medium"),
    db: Session = Depends(get_db),
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    risk_repo: RiskRepository = Depends(get_risk_repository),
    current_user: dict = Depends(require_teacher_role),
) -> APIResponse[Dict[str, Any]]:
    """
    Obtiene alertas en tiempo real de estudiantes que necesitan intervención pedagógica.

    **HU-DOC-004**: Permite al docente intervenir antes de que el estudiante
    se frustre o abandone.

    **Criterios de alerta:**
    - 3+ riesgos medios
    - 1+ riesgo crítico
    - Más de 2 horas en la misma fase
    - Dependencia de IA > 85%

    **Ejemplo:**
    ```bash
    GET /api/v1/teacher/alerts
    GET /api/v1/teacher/alerts?severity=critical
    ```
    """
    # Obtener todas las sesiones activas
    active_sessions = [s for s in session_repo.get_all() if s.status == "active"]

    alerts = []

    for session in active_sessions:
        # Obtener riesgos de la sesión
        risks = risk_repo.get_by_session(session.id)

        # Clasificar riesgos (DB almacena en lowercase)
        critical_risks = [r for r in risks if r.risk_level == "critical"]
        high_risks = [r for r in risks if r.risk_level == "high"]
        medium_risks = [r for r in risks if r.risk_level == "medium"]

        # Obtener trazas para calcular AI dependency
        traces = trace_repo.get_by_session(session.id)

        ai_involvements = [t.ai_involvement or 0.0 for t in traces]
        ai_dependency_avg = sum(ai_involvements) / len(ai_involvements) if ai_involvements else 0.0

        # Calcular duración de la sesión
        duration_hours = (utc_now() - session.start_time).total_seconds() / 3600.0

        # Determinar si genera alerta
        alert_reasons = []
        alert_severity = "low"

        if len(critical_risks) >= 1:
            alert_reasons.append(f"{len(critical_risks)} riesgo(s) crítico(s)")
            alert_severity = "critical"

        if len(high_risks) >= 2:
            alert_reasons.append(f"{len(high_risks)} riesgos altos")
            if alert_severity == "low":
                alert_severity = "high"

        if len(medium_risks) >= 3:
            alert_reasons.append(f"{len(medium_risks)} riesgos medios")
            if alert_severity == "low":
                alert_severity = "medium"

        if ai_dependency_avg > 0.85:
            alert_reasons.append(f"Dependencia de IA muy alta ({ai_dependency_avg*100:.0f}%)")
            if alert_severity == "low":
                alert_severity = "high"

        if duration_hours > 2.0:
            alert_reasons.append(f"Sesión prolongada ({duration_hours:.1f} horas)")
            if alert_severity == "low":
                alert_severity = "medium"

        # Si hay razones para alerta, agregarla
        if alert_reasons:
            # Filtrar por severidad si se especificó
            if severity != "all" and alert_severity != severity:
                continue

            # Sugerencias de intervención
            suggestions = []
            if len(critical_risks) >= 1:
                suggestions.append("Intervención inmediata: revisar riesgos críticos con el estudiante")
            if ai_dependency_avg > 0.85:
                suggestions.append("Fomentar autonomía: reducir dependencia de IA")
            if duration_hours > 2.0:
                suggestions.append("Chequear progreso: puede estar bloqueado o perdido")

            alerts.append({
                "alert_id": f"alert_{session.id}",
                "student_id": session.student_id,
                "session_id": session.id,
                "activity_id": session.activity_id,
                "severity": alert_severity,
                "reasons": alert_reasons,
                "suggestions": suggestions,
                "metrics": {
                    "critical_risks": len(critical_risks),
                    "high_risks": len(high_risks),
                    "medium_risks": len(medium_risks),
                    "ai_dependency": round(ai_dependency_avg, 2),
                    "duration_hours": round(duration_hours, 2),
                    "total_interactions": len(traces)
                },
                "timestamp": utc_now().isoformat()
            })

    # Ordenar por severidad
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    alerts.sort(key=lambda a: severity_order[a["severity"]])

    return APIResponse(
        success=True,
        data={
            "total_alerts": len(alerts),
            "by_severity": {
                "critical": sum(1 for a in alerts if a["severity"] == "critical"),
                "high": sum(1 for a in alerts if a["severity"] == "high"),
                "medium": sum(1 for a in alerts if a["severity"] == "medium"),
            },
            "alerts": alerts
        },
        message=f"Se encontraron {len(alerts)} alertas activas"
    )


@router.post(
    "/alerts/{alert_id}/acknowledge",
    summary="Marcar alerta como atendida",
    description="Marca una alerta como atendida por el docente. Requiere rol teacher."
)
async def acknowledge_alert(
    alert_id: str,
    notes: str = Query(None, description="Notas del docente sobre la intervención"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_role),
) -> APIResponse[Dict[str, Any]]:
    """
    Marca una alerta como atendida y opcionalmente agrega notas.

    **Nota**: En el MVP actual, esto solo retorna confirmación.
    En producción, se persistiría en una tabla `teacher_interventions`.
    """
    return APIResponse(
        success=True,
        data={
            "alert_id": alert_id,
            "acknowledged_at": utc_now().isoformat(),
            "notes": notes or "Sin notas"
        },
        message=f"Alerta {alert_id} marcada como atendida"
    )