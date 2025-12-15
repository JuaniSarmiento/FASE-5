"""
Router para gestión de sesiones de aprendizaje
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, select, and_
from collections import Counter
import logging

from ...database.repositories import SessionRepository, TraceRepository, RiskRepository, EvaluationRepository
from ...database.models import SessionDB, CognitiveTraceDB, RiskDB, EvaluationDB
from ..deps import get_db, get_session_repository, get_trace_repository, get_risk_repository, get_current_user
from ..schemas.session import (
    SessionCreate,
    SessionResponse,
    SessionDetailResponse,
    SessionUpdate,
    SessionHistoryResponse,
    SessionSummary,
    ProgressAggregation,
)
from ..schemas.common import APIResponse, PaginatedResponse, PaginationParams, PaginationMeta
from ..exceptions import SessionNotFoundError
from ..config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, MIN_PAGE_SIZE

router = APIRouter(prefix="/sessions", tags=["Sessions"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=APIResponse[SessionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Session",
    description="Crea una nueva sesión de aprendizaje para un estudiante",
)
async def create_session(
    session_data: SessionCreate,
    session_repo: SessionRepository = Depends(get_session_repository),
    current_user: dict = Depends(get_current_user),
) -> APIResponse[SessionResponse]:
    """
    Crea una nueva sesión de aprendizaje.

    Args:
        session_data: Datos de la sesión a crear
        session_repo: Repositorio de sesiones (inyectado)

    Returns:
        APIResponse con la sesión creada

    Example:
        POST /api/v1/sessions
        {
            "student_id": "student_001",
            "activity_id": "prog2_tp1_colas",
            "mode": "TUTOR"
        }
    """
    # FIX 10.17 Cortez10: Validate simulator_type when mode is SIMULATOR
    if session_data.mode.value == "SIMULATOR" and not session_data.simulator_type:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="simulator_type is required when mode is SIMULATOR. "
                   "Valid values: product_owner, scrum_master, tech_interviewer, "
                   "incident_responder, client, devsecops, senior_dev, qa_engineer, "
                   "security_auditor, tech_lead, demanding_client"
        )

    # Crear sesión en la base de datos
    # Convertir enum a string para la BD
    db_session = session_repo.create(
        student_id=session_data.student_id,
        activity_id=session_data.activity_id,
        mode=session_data.mode.value,
        simulator_type=session_data.simulator_type,
    )

    # Convertir a schema de respuesta
    response_data = SessionResponse(
        id=db_session.id,
        student_id=db_session.student_id,
        activity_id=db_session.activity_id,
        mode=db_session.mode,
        status=db_session.status,
        simulator_type=db_session.simulator_type,
        start_time=db_session.start_time,
        end_time=db_session.end_time,
        trace_count=0,  # Nueva sesión, sin trazas aún
        risk_count=0,  # Nueva sesión, sin riesgos aún
        created_at=db_session.created_at,
        updated_at=db_session.updated_at,
    )

    return APIResponse(
        success=True,
        data=response_data,
        message=f"Session created successfully: {db_session.id}",
    )


@router.get(
    "",
    response_model=PaginatedResponse[SessionResponse],
    summary="List Sessions",
    description="Lista todas las sesiones con filtros opcionales y paginación",
)
async def list_sessions(
    student_id: Optional[str] = Query(None, description="Filtrar por ID de estudiante"),
    activity_id: Optional[str] = Query(None, description="Filtrar por ID de actividad"),
    mode: Optional[str] = Query(None, description="Filtrar por modo (TUTOR, EVALUATOR, etc.)"),
    status: Optional[str] = Query(None, description="Filtrar por estado (ACTIVE, COMPLETED, etc.)"),
    page: int = Query(1, ge=MIN_PAGE_SIZE, description="Número de página"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE, description="Elementos por página"),
    session_repo: SessionRepository = Depends(get_session_repository),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PaginatedResponse[SessionResponse]:
    """
    Lista sesiones con filtros y paginación.

    Args:
        student_id: Filtrar por estudiante (opcional)
        activity_id: Filtrar por actividad (opcional)
        mode: Filtrar por modo (opcional)
        status: Filtrar por estado (opcional)
        page: Número de página (default: 1)
        page_size: Elementos por página (default: 20, max: 100)
        session_repo: Repositorio de sesiones (inyectado)
        db: Sesión de base de datos (inyectado)

    Returns:
        PaginatedResponse con lista de sesiones
    """
    # Construir query base con filtros
    query = db.query(SessionDB)

    if student_id:
        query = query.filter(SessionDB.student_id == student_id)
    if activity_id:
        query = query.filter(SessionDB.activity_id == activity_id)
    if mode:
        query = query.filter(SessionDB.mode == mode)
    if status:
        query = query.filter(SessionDB.status == status)

    # Contar total de elementos
    total_items = query.count()

    # Calcular paginación
    offset = (page - 1) * page_size
    total_pages = (total_items + page_size - 1) // page_size

    # Aplicar eager loading para evitar N+1 queries
    # selectinload carga las relaciones en una query separada eficiente
    query_with_loading = query.options(
        selectinload(SessionDB.traces),
        selectinload(SessionDB.risks),
    )

    # Aplicar paginación y ordenar por fecha de creación descendente
    db_sessions = (
        query_with_loading.order_by(SessionDB.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Convertir a schemas de respuesta
    # Ahora len(s.traces) y len(s.risks) no causan queries adicionales
    sessions_data = [
        SessionResponse(
            id=s.id,
            student_id=s.student_id,
            activity_id=s.activity_id,
            mode=s.mode,
            status=s.status,
            simulator_type=s.simulator_type,
            start_time=s.start_time,
            end_time=s.end_time,
            trace_count=len(s.traces),
            risk_count=len(s.risks),
            created_at=s.created_at,
            updated_at=s.updated_at,
        )
        for s in db_sessions
    ]

    # Crear metadatos de paginación
    pagination_meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return PaginatedResponse(
        success=True,
        data=sessions_data,
        pagination=pagination_meta,
    )


@router.get(
    "/{session_id}",
    response_model=APIResponse[SessionDetailResponse],
    summary="Get Session",
    description="Obtiene detalles completos de una sesión específica",
)
async def get_session(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    risk_repo: RiskRepository = Depends(get_risk_repository),
    _current_user: dict = Depends(get_current_user),  # FIX Cortez20: Add auth
) -> APIResponse[SessionDetailResponse]:
    """
    Obtiene detalles completos de una sesión.

    Args:
        session_id: ID de la sesión
        session_repo: Repositorio de sesiones (inyectado)
        trace_repo: Repositorio de trazas (inyectado)
        risk_repo: Repositorio de riesgos (inyectado)

    Returns:
        APIResponse con detalles de la sesión

    Raises:
        SessionNotFoundError: Si la sesión no existe
    """
    # FIX N+1 #3: Usar eager loading para cargar session, traces y risks en pocas queries
    db_session = session_repo.get_by_id(session_id, load_relations=True)
    if not db_session:
        raise SessionNotFoundError(session_id)

    # Usar relaciones eager-loaded (ya cargadas, no generan queries adicionales)
    traces = db_session.traces
    risks = db_session.risks

    # Calcular resumen de trazas por nivel
    traces_summary = {}
    for trace in traces:
        level = trace.trace_level
        traces_summary[level] = traces_summary.get(level, 0) + 1

    # Calcular resumen de riesgos por tipo
    risks_summary = {}
    for risk in risks:
        risk_type = risk.risk_type
        risks_summary[risk_type] = risks_summary.get(risk_type, 0) + 1

    # Calcular score de dependencia de IA (promedio de ai_involvement en trazas)
    # FIX FLUJO2-2: Default a 0.0 en lugar de None para evitar errores en frontend
    ai_dependency_score = 0.0
    if traces:
        ai_involvements = [t.ai_involvement for t in traces if t.ai_involvement is not None]
        if ai_involvements:
            ai_dependency_score = sum(ai_involvements) / len(ai_involvements)

    # Construir respuesta detallada
    response_data = SessionDetailResponse(
        id=db_session.id,
        student_id=db_session.student_id,
        activity_id=db_session.activity_id,
        mode=db_session.mode,
        status=db_session.status,
        simulator_type=db_session.simulator_type,
        start_time=db_session.start_time,
        end_time=db_session.end_time,
        trace_count=len(traces),
        risk_count=len(risks),
        created_at=db_session.created_at,
        updated_at=db_session.updated_at,
        traces_summary=traces_summary,
        risks_summary=risks_summary,
        ai_dependency_score=ai_dependency_score,
    )

    return APIResponse(
        success=True,
        data=response_data,
        message=f"Session retrieved: {session_id}",
    )


@router.patch(
    "/{session_id}",
    response_model=APIResponse[SessionResponse],
    summary="Update Session",
    description="Actualiza una sesión existente (modo, estado, etc.)",
)
async def update_session(
    session_id: str,
    session_update: SessionUpdate,
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    risk_repo: RiskRepository = Depends(get_risk_repository),
    current_user: dict = Depends(get_current_user),
) -> APIResponse[SessionResponse]:
    """
    Actualiza una sesión existente.

    Args:
        session_id: ID de la sesión
        session_update: Datos a actualizar
        session_repo: Repositorio de sesiones (inyectado)

    Returns:
        APIResponse con la sesión actualizada

    Raises:
        SessionNotFoundError: Si la sesión no existe
    """
    # Verificar que la sesión existe
    db_session = session_repo.get_by_id(session_id)
    if not db_session:
        raise SessionNotFoundError(session_id)

    # Actualizar modo si se proporciona
    if session_update.mode:
        # Convertir enum a string
        db_session = session_repo.update_mode(session_id, session_update.mode.value)

    # Actualizar estado si se proporciona
    if session_update.status:
        # Convertir enum a string
        status_value = session_update.status.value

        # FIX 10.16 Cortez10: Use constant for terminal statuses instead of hardcoded list
        # Terminal statuses are those that end a session
        TERMINAL_STATUSES = {"completed", "aborted", "abandoned"}
        if status_value in TERMINAL_STATUSES:
            success = session_repo.end_session(session_id)
            if success:
                db_session = session_repo.get_by_id(session_id)
        else:
            # Actualizar estado usando el repositorio (no acceso directo)
            updated_session = session_repo.update_status(session_id, status_value)
            if updated_session:
                db_session = updated_session

    # Obtener conteos usando repositorios para asegurar datos correctos
    traces = trace_repo.get_by_session(session_id)
    risks = risk_repo.get_by_session(session_id)

    # Convertir a schema de respuesta
    response_data = SessionResponse(
        id=db_session.id,
        student_id=db_session.student_id,
        activity_id=db_session.activity_id,
        mode=db_session.mode,
        status=db_session.status,
        simulator_type=db_session.simulator_type,
        start_time=db_session.start_time,
        end_time=db_session.end_time,
        trace_count=len(traces),
        risk_count=len(risks),
        created_at=db_session.created_at,
        updated_at=db_session.updated_at,
    )

    return APIResponse(
        success=True,
        data=response_data,
        message=f"Session updated: {session_id}",
    )


@router.post(
    "/{session_id}/end",
    response_model=APIResponse[SessionResponse],
    summary="End Session",
    description="Finaliza una sesión activa marcándola como completada",
)
async def end_session(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    risk_repo: RiskRepository = Depends(get_risk_repository),
) -> APIResponse[SessionResponse]:
    """
    Finaliza una sesión activa.

    Marca la sesión como 'completed' y registra el tiempo de finalización.

    Args:
        session_id: ID de la sesión
        session_repo: Repositorio de sesiones (inyectado)
        trace_repo: Repositorio de trazas (inyectado)
        risk_repo: Repositorio de riesgos (inyectado)

    Returns:
        APIResponse con la sesión finalizada

    Raises:
        SessionNotFoundError: Si la sesión no existe

    Example:
        POST /api/v1/sessions/session_001/end
    """
    # Verificar que la sesión existe
    db_session = session_repo.get_by_id(session_id)
    if not db_session:
        raise SessionNotFoundError(session_id)

    # Finalizar sesión
    success = session_repo.end_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not end session '{session_id}'. It may already be completed."
        )

    # Recargar sesión actualizada
    db_session = session_repo.get_by_id(session_id)

    # Obtener conteos usando repositorios para asegurar datos correctos
    traces = trace_repo.get_by_session(session_id)
    risks = risk_repo.get_by_session(session_id)

    # Convertir a schema de respuesta
    response_data = SessionResponse(
        id=db_session.id,
        student_id=db_session.student_id,
        activity_id=db_session.activity_id,
        mode=db_session.mode,
        status=db_session.status,
        simulator_type=db_session.simulator_type,
        start_time=db_session.start_time,
        end_time=db_session.end_time,
        trace_count=len(traces),
        risk_count=len(risks),
        created_at=db_session.created_at,
        updated_at=db_session.updated_at,
    )

    return APIResponse(
        success=True,
        data=response_data,
        message=f"Session ended successfully: {session_id}",
    )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Session",
    description="Elimina una sesión y todos sus datos relacionados (trazas, riesgos, evaluaciones)",
)
async def delete_session(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Elimina una sesión y todos sus datos relacionados.

    ADVERTENCIA: Esta operación es irreversible y eliminará:
    - La sesión
    - Todas las trazas asociadas
    - Todos los riesgos asociados
    - Todas las evaluaciones asociadas

    Args:
        session_id: ID de la sesión
        session_repo: Repositorio de sesiones (inyectado)
        db: Sesión de base de datos (inyectado)

    Raises:
        SessionNotFoundError: Si la sesión no existe
    """
    # Verificar que la sesión existe
    db_session = session_repo.get_by_id(session_id)
    if not db_session:
        raise SessionNotFoundError(session_id)

    # Eliminar sesión con manejo de transacciones
    # Cascade eliminará trazas, riesgos, evaluaciones
    try:
        db.delete(db_session)
        db.commit()
    except Exception as e:
        db.rollback()
        # Re-lanzar como DatabaseOperationError para manejo consistente
        from ..exceptions import DatabaseOperationError
        raise DatabaseOperationError(
            operation=f"delete session '{session_id}'",
            details=str(e)
        )

    # No retornar contenido (204 No Content)
    return None
@router.get(
    "/history/{student_id}",
    response_model=APIResponse[SessionHistoryResponse],
    summary="Get Session History",
    description="Obtiene el historial completo de sesiones de un estudiante con agregaciones y métricas (HU-EST-008)",
)
async def get_session_history(
    student_id: str,
    start_date: Optional[date] = Query(None, description="Fecha de inicio del rango"),
    end_date: Optional[date] = Query(None, description="Fecha de fin del rango"),
    activity_id: Optional[str] = Query(None, description="Filtrar por actividad"),
    mode: Optional[str] = Query(None, description="Filtrar por modo (TUTOR, EVALUATOR, etc.)"),
    status: Optional[str] = Query(None, description="Filtrar por estado (ACTIVE, COMPLETED, etc.)"),
    min_competency: Optional[str] = Query(None, description="Competencia mínima (INICIAL, INTERMEDIO, AVANZADO)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> APIResponse[SessionHistoryResponse]:
    """
    Obtiene el historial de sesiones de un estudiante con filtros y agregaciones.

    **Filtros disponibles**:
    - `start_date` / `end_date`: Rango de fechas
    - `activity_id`: Actividad específica
    - `mode`: Modo de interacción
    - `status`: Estado de la sesión
    - `min_competency`: Nivel mínimo de competencia

    **Agregaciones incluidas**:
    - Total de sesiones y completadas
    - Total de interacciones
    - Dependencia promedio de IA
    - Evolución de competencia temporal
    - Breakdown por actividad y modo
    - Resumen de riesgos

    Args:
        student_id: ID del estudiante
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)
        activity_id: Filtrar por actividad (opcional)
        mode: Filtrar por modo (opcional)
        status: Filtrar por estado (opcional)
        min_competency: Competencia mínima (opcional)
        db: Sesión de base de datos (inyectada)

    Returns:
        APIResponse con historial de sesiones y agregaciones

    Example:
        GET /api/v1/sessions/history/student_001?start_date=2025-11-01&end_date=2025-11-30&activity_id=prog2_tp1
    """
    # FIX 3.2: Validate date range
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date must be before end_date"
        )

    # FIX 3.2: Validate min_competency
    valid_competencies = ["INICIAL", "INTERMEDIO", "AVANZADO", "EXPERTO"]
    if min_competency and min_competency.upper() not in valid_competencies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"min_competency must be one of {valid_competencies}"
        )

    logger.info(
        f"Fetching session history for student: {student_id}",
        extra={
            "student_id": student_id,
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "activity_id": activity_id,
                "mode": mode,
                "status": status,
                "min_competency": min_competency
            }
        }
    )

    # Construir query base con eager loading
    query = (
        select(SessionDB)
        .where(SessionDB.student_id == student_id)
        .options(
            selectinload(SessionDB.traces),
            selectinload(SessionDB.risks),
            selectinload(SessionDB.evaluations)
        )
    )

    # Aplicar filtros
    filters_applied = {}

    if start_date:
        query = query.where(SessionDB.start_time >= datetime.combine(start_date, datetime.min.time()))
        filters_applied["start_date"] = start_date.isoformat()

    if end_date:
        query = query.where(SessionDB.start_time <= datetime.combine(end_date, datetime.max.time()))
        filters_applied["end_date"] = end_date.isoformat()

    if activity_id:
        query = query.where(SessionDB.activity_id == activity_id)
        filters_applied["activity_id"] = activity_id

    if mode:
        query = query.where(SessionDB.mode == mode.upper())
        filters_applied["mode"] = mode

    if status:
        # Status is stored as lowercase in DB (e.g., 'active', 'completed')
        query = query.where(SessionDB.status == status.lower())
        filters_applied["status"] = status

    # Ejecutar query
    result = db.execute(query.order_by(SessionDB.start_time.desc()))
    sessions = result.scalars().all()

    logger.info(f"Found {len(sessions)} sessions for student {student_id}")

    # Construir lista de SessionSummary
    session_summaries: List[SessionSummary] = []

    for sess in sessions:
        # Calcular duración
        duration_minutes = None
        if sess.end_time:
            delta = sess.end_time - sess.start_time
            duration_minutes = int(delta.total_seconds() / 60)

        # Obtener evaluación si existe
        evaluation = sess.evaluations[0] if sess.evaluations else None
        competency_level = None
        overall_score = None

        if evaluation:
            competency_level = evaluation.overall_competency_level
            overall_score = evaluation.overall_score

        # Filtrar por competencia mínima si se especificó
        if min_competency and competency_level:
            competency_order = ["INICIAL", "INTERMEDIO", "AVANZADO", "EXPERTO"]
            try:
                min_idx = competency_order.index(min_competency.upper())
                curr_idx = competency_order.index(competency_level)
                if curr_idx < min_idx:
                    continue  # Skip esta sesión
            except ValueError:
                pass  # Si el nivel no es válido, incluir la sesión

        # Calcular AI dependency score promedio
        # FIX FLUJO2-2: Default a 0.0 en lugar de None
        ai_dependency_score = 0.0
        if sess.traces:
            ai_scores = [t.ai_involvement for t in sess.traces if t.ai_involvement is not None]
            if ai_scores:
                ai_dependency_score = sum(ai_scores) / len(ai_scores)

        # Contar riesgos (risk_level is stored as lowercase: 'critical', 'high', etc.)
        risks_detected = len(sess.risks)
        critical_risks = len([r for r in sess.risks if r.risk_level == "critical"])

        session_summaries.append(SessionSummary(
            session_id=sess.id,
            activity_id=sess.activity_id,
            mode=sess.mode,
            status=sess.status,
            start_time=sess.start_time,
            end_time=sess.end_time,
            duration_minutes=duration_minutes,
            interactions_count=len(sess.traces),
            ai_dependency_score=ai_dependency_score,
            competency_level=competency_level,
            overall_score=overall_score,
            risks_detected=risks_detected,
            critical_risks=critical_risks
        ))

    # Calcular agregaciones (status is stored as lowercase: 'completed', 'active', etc.)
    total_sessions = len(session_summaries)
    completed_sessions = len([s for s in session_summaries if s.status == "completed"])
    total_interactions = sum(s.interactions_count for s in session_summaries)

    # AI dependency promedio
    ai_scores = [s.ai_dependency_score for s in session_summaries if s.ai_dependency_score is not None]
    average_ai_dependency = sum(ai_scores) / len(ai_scores) if ai_scores else 0.0

    # Evolución de competencia temporal
    competency_evolution: List[Dict[str, Any]] = []
    sessions_with_eval = [s for s in session_summaries if s.competency_level and s.overall_score]

    # Agrupar por fecha (solo fecha, no hora)
    from collections import defaultdict
    by_date: Dict[date, List[SessionSummary]] = defaultdict(list)
    for s in sessions_with_eval:
        session_date = s.start_time.date()
        by_date[session_date].append(s)

    # Crear puntos de evolución (un punto por fecha con el mejor score)
    for session_date in sorted(by_date.keys()):
        sessions_on_date = by_date[session_date]
        # Tomar la sesión con mejor score de ese día
        best_session = max(sessions_on_date, key=lambda x: x.overall_score or 0)
        competency_evolution.append({
            "date": session_date.isoformat(),
            "level": best_session.competency_level,
            "score": best_session.overall_score
        })

    # Breakdown por actividad
    activity_breakdown = Counter(s.activity_id for s in session_summaries)

    # Breakdown por modo
    mode_breakdown = Counter(s.mode for s in session_summaries)

    # Resumen de riesgos
    total_risks = sum(s.risks_detected for s in session_summaries)
    total_critical = sum(s.critical_risks for s in session_summaries)

    # Calcular riesgos HIGH contando los no-CRITICAL
    all_risks_by_level = []
    for sess in sessions:
        for risk in sess.risks:
            all_risks_by_level.append(risk.risk_level)

    risk_counter = Counter(all_risks_by_level)

    # risk_level is stored as lowercase: 'critical', 'high', 'medium', 'low'
    risk_summary = {
        "total_risks": total_risks,
        "critical_risks": risk_counter.get("critical", 0),
        "high_risks": risk_counter.get("high", 0),
        "medium_risks": risk_counter.get("medium", 0),
        "low_risks": risk_counter.get("low", 0),
        "resolved_risks": len([r for sess in sessions for r in sess.risks if r.resolved])
    }

    # Construir agregaciones
    aggregations = ProgressAggregation(
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        total_interactions=total_interactions,
        average_ai_dependency=average_ai_dependency,
        competency_evolution=competency_evolution,
        activity_breakdown=dict(activity_breakdown),
        mode_breakdown=dict(mode_breakdown),
        risk_summary=risk_summary
    )

    # Construir response final
    history_response = SessionHistoryResponse(
        student_id=student_id,
        sessions=session_summaries,
        aggregations=aggregations,
        filters_applied=filters_applied if filters_applied else None
    )

    logger.info(
        f"Session history compiled successfully",
        extra={
            "student_id": student_id,
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "filters_applied": filters_applied
        }
    )

    return APIResponse(
        success=True,
        data=history_response,
        message=f"Session history retrieved successfully for student {student_id}"
    )


class CreateTutorRequest(BaseModel):
    """Request para crear sesión de tutor con parámetros opcionales"""
    student_id: Optional[str] = Field(None, description="ID del estudiante (opcional, default: demo_student)")
    activity_id: Optional[str] = Field(None, description="ID de la actividad (opcional, se genera automáticamente)")


@router.post(
    "/create-tutor",
    response_model=APIResponse[Dict[str, Any]],
    summary="Create Tutor Session V2.0",
    description="Crea una sesión de tutor socrático V2.0 y retorna mensaje de bienvenida",
)
async def create_tutor_session(
    request: Optional[CreateTutorRequest] = None,
    session_repo: SessionRepository = Depends(get_session_repository),
) -> APIResponse[Dict[str, Any]]:
    """
    Crea una nueva sesión para el Tutor Socrático V2.0.

    Args:
        request: Parámetros opcionales para crear la sesión
            - student_id: ID del estudiante (default: demo_student)
            - activity_id: ID de la actividad (se genera si no se proporciona)

    Returns:
        APIResponse con session_id y welcome_message
    """
    # Obtener valores del request o usar defaults
    student_id = request.student_id if request and request.student_id else "demo_student"
    activity_id = request.activity_id if request and request.activity_id else f"tutor_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Crear sesión en la base de datos
    db_session = session_repo.create(
        student_id=student_id,
        activity_id=activity_id,
        mode="TUTOR"
    )
    
    # Mensaje de bienvenida con las 4 reglas
    welcome_message = """¡Hola! Soy tu **Tutor Socrático IA V2.0**.

🎯 Mi objetivo es guiar tu aprendizaje, no darte soluciones directas.

Opero bajo **4 reglas inquebrantables**:

1. 🚫 **No daré código completo** - te guiaré con preguntas

2. ❓ **Modo socrático prioritario** - pregunto antes que responder

3. 💭 **Exijo que expliques tu razonamiento** - convierte tu pensamiento en palabras

4. 📚 **Refuerzo conceptual** - te enseño fundamentos, no parches

¿En qué necesitás ayuda hoy?"""
    
    logger.info(f"Tutor session created: {db_session.id}")
    
    return APIResponse(
        success=True,
        data={
            "session_id": db_session.id,
            "welcome_message": welcome_message
        },
        message="Tutor session created successfully"
    )


@router.post(
    "/{session_id}/interact",
    response_model=APIResponse[Dict[str, Any]],
    summary="Interact with Tutor V2.0",
    description="Procesa un mensaje del estudiante con el Tutor Socrático V2.0",
)
async def interact_with_tutor(
    session_id: str,
    request_data: Dict[str, Any] = Body(...),
    session_repo: SessionRepository = Depends(get_session_repository),
) -> APIResponse[Dict[str, Any]]:
    """
    Procesa la interacción del estudiante con el Tutor Socrático V2.0.
    
    Args:
        session_id: ID de la sesión
        request_data: Dict con 'message' y 'student_profile'
    
    Returns:
        Dict con response y metadata V2.0
    """
    from ...agents.tutor import TutorCognitivoAgent
    from ...llm import LLMProviderFactory
    
    message = request_data.get("message", "")
    student_profile = request_data.get("student_profile", {})
    
    # Verificar que la sesión existe
    db_session = session_repo.get_by_id(session_id)
    if not db_session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    # Inicializar LLM provider (Ollama) usando variables de entorno
    llm_provider = LLMProviderFactory.create_from_env()
    
    # Inicializar tutor con LLM
    try:
        tutor = TutorCognitivoAgent(llm_provider=llm_provider)
    except Exception as e:
        logger.error(f"Error initializing TutorCognitivoAgent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing tutor: {str(e)}"
        )
    
    # Procesar con Tutor V2.0
    try:
        result = await tutor.process_student_request(
            session_id=session_id,
            student_prompt=message,
            student_profile=student_profile or {},
            conversation_history=None
        )
        
        logger.info(
            f"Tutor V2.0 interaction processed",
            extra={
                "session_id": session_id,
                "intervention_type": result.get("intervention_type"),
                "semaforo": result.get("semaforo")
            }
        )
        
        return APIResponse(
            success=True,
            data={
                "response": result.get("message", ""),  # El método retorna 'message', no 'response'
                "metadata": {
                    "intervention_type": result.get("intervention_type"),
                    "semaforo": result.get("semaforo"),
                    "help_level": result.get("help_level"),
                    "requires_student_response": result.get("requires_student_response", True),
                    "cognitive_events": result.get("cognitive_events", []),
                    "rule_violations": result.get("rule_violations", [])
                }
            },
            message="Interaction processed successfully"
        )
    except Exception as e:
        logger.error(f"Error processing tutor interaction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing interaction: {str(e)}"
        )


@router.get(
    "/{session_id}/analytics-n4",
    response_model=APIResponse[Dict[str, Any]],
    summary="Get Session Analytics N4",
    description="Obtiene analytics completos de la sesión (trazabilidad N4)",
)
async def get_session_analytics_n4(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
) -> APIResponse[Dict[str, Any]]:
    """
    Obtiene analytics N4 de una sesión del tutor.
    
    Args:
        session_id: ID de la sesión
    
    Returns:
        Dict con estadísticas completas de la sesión
    """
    from ...agents.tutor import TutorCognitivoAgent
    
    # Verificar que la sesión existe
    db_session = session_repo.get_by_id(session_id)
    if not db_session:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )
    
    # Inicializar tutor y obtener analytics
    tutor = TutorCognitivoAgent()
    
    try:
        analytics = tutor.get_session_analytics_n4(session_id)
        
        logger.info(
            f"Analytics N4 retrieved",
            extra={
                "session_id": session_id,
                "total_messages": analytics.get("total_messages", 0)
            }
        )
        
        return APIResponse(
            success=True,
            data=analytics,
            message="Analytics retrieved successfully"
        )
    except Exception as e:
        logger.error(f"Error retrieving analytics: {str(e)}")
        # Retornar success=False para indicar que hubo un error
        # pero incluir estructura vacía para que el frontend no falle
        return APIResponse(
            success=False,
            data={
                "total_messages": 0,
                "semaforo_distribution": {"verde": 0, "amarillo": 0, "rojo": 0},
                "intervention_types": {},
                "cognitive_events": [],
                "student_progression": {},
                "error": str(e)
            },
            message=f"Error retrieving analytics: {str(e)}"
        )
