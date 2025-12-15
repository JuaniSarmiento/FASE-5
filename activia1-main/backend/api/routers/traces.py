"""
Router para consultas de trazabilidad N4
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from ...database.repositories import TraceRepository, SessionRepository
from ...models.trace import CognitiveTrace
from ..deps import get_trace_repository, get_session_repository, get_current_user
from ..schemas.common import APIResponse, PaginatedResponse, PaginationParams, PaginationMeta
from ..exceptions import SessionNotFoundError
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(prefix="/traces", tags=["Traceability"])


# Schemas específicos para trazas
class TraceResponse(BaseModel):
    """
    Response con información de una traza N4

    FIX 10.4 Cortez10: Unified timestamp field - use created_at as primary,
    timestamp as alias for backwards compatibility.
    FIX 10.5 Cortez10: Use trace_metadata as field name to match ORM.

    Alineado con CognitiveTraceDB en database/models.py
    """

    id: str
    session_id: str
    student_id: str
    activity_id: str
    trace_level: str
    interaction_type: str
    cognitive_state: Optional[str] = None
    cognitive_intent: Optional[str] = None
    content: str
    ai_involvement: Optional[float] = None
    # N4 Cognitive fields
    context: Optional[dict] = None
    # FIX 10.5 Cortez10: Use trace_metadata to match ORM field name
    trace_metadata: Optional[dict] = Field(None, alias="metadata")
    decision_justification: Optional[str] = None
    alternatives_considered: Optional[List[str]] = None
    strategy_type: Optional[str] = None
    # Relationships
    agent_id: Optional[str] = None
    parent_trace_id: Optional[str] = None
    # FIX 10.4 Cortez10: Use created_at as primary timestamp, with alias for backwards compat
    created_at: datetime = Field(..., alias="timestamp")

    class Config:
        from_attributes = True
        # FIX 10.4 Cortez10: Allow both field names and aliases
        populate_by_name = True


@router.get(
    "/{session_id}",
    response_model=PaginatedResponse[TraceResponse],
    summary="Get Session Traces",
    description="Obtiene todas las trazas de una sesión con filtros opcionales",
)
async def get_session_traces(
    session_id: str,
    # FIX 10.8 Cortez10: Updated documentation to match DB values
    trace_level: Optional[str] = Query(None, description="Filtrar por nivel: n1_superficial, n2_tecnico, n3_interaccional, n4_cognitivo"),
    interaction_type: Optional[str] = Query(None, description="Filtrar por tipo de interacción"),
    cognitive_state: Optional[str] = Query(None, description="Filtrar por estado cognitivo"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    _current_user: dict = Depends(get_current_user),  # FIX Cortez20: Add auth
) -> PaginatedResponse[TraceResponse]:
    """
    Obtiene todas las trazas de una sesión.

    Permite filtrar por nivel, tipo de interacción y estado cognitivo.

    Args:
        session_id: ID de la sesión
        trace_level: Filtro por nivel (N1, N2, N3, N4)
        interaction_type: Filtro por tipo de interacción
        cognitive_state: Filtro por estado cognitivo
        page: Número de página
        page_size: Elementos por página
        session_repo: Repositorio de sesiones (inyectado)
        trace_repo: Repositorio de trazas (inyectado)

    Returns:
        PaginatedResponse con lista de trazas

    Raises:
        SessionNotFoundError: Si la sesión no existe
    """
    # Verificar que la sesión existe
    db_session = session_repo.get_by_id(session_id)
    if not db_session:
        raise SessionNotFoundError(session_id)

    # FIX N+1 #2: Filtrar y paginar en SQL en lugar de Python
    offset = (page - 1) * page_size

    # Obtener conteo total con filtros (para metadata de paginación)
    total_items = trace_repo.count_by_session_filtered(
        session_id=session_id,
        trace_level=trace_level,
        interaction_type=interaction_type,
        cognitive_state=cognitive_state
    )

    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0

    # Obtener trazas filtradas y paginadas directamente en SQL
    paginated_traces = trace_repo.get_by_session_filtered(
        session_id=session_id,
        trace_level=trace_level,
        interaction_type=interaction_type,
        cognitive_state=cognitive_state,
        limit=page_size,
        offset=offset
    )

    # Convertir a schemas de respuesta
    traces_data = [
        TraceResponse(
            id=t.id,
            session_id=t.session_id,
            student_id=t.student_id,
            activity_id=t.activity_id,
            trace_level=t.trace_level,
            interaction_type=t.interaction_type,
            cognitive_state=t.cognitive_state,
            cognitive_intent=t.cognitive_intent,
            content=t.content,
            ai_involvement=t.ai_involvement,
            context=t.context,
            trace_metadata=t.trace_metadata,  # FIX 10.5 Cortez10: Use trace_metadata directly
            decision_justification=t.decision_justification,
            alternatives_considered=t.alternatives_considered,
            strategy_type=t.strategy_type,
            agent_id=t.agent_id,
            parent_trace_id=t.parent_trace_id,
            created_at=t.created_at,  # FIX 10.4 Cortez10: Use created_at (timestamp is alias)
        )
        for t in paginated_traces
    ]

    # Metadatos de paginación
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
        data=traces_data,
        pagination=pagination_meta,
    )


@router.get(
    "/{session_id}/cognitive-path",
    summary="Get Cognitive Path (DEPRECATED)",
    description="DEPRECATED: Use GET /cognitive-path/{session_id} instead. This endpoint redirects to the canonical location.",
    deprecated=True,
)
async def get_cognitive_path_deprecated(
    session_id: str,
):
    """
    DEPRECATED: Use GET /api/v1/cognitive-path/{session_id} instead.

    This endpoint is deprecated and will be removed in a future version.
    The canonical endpoint provides more detailed cognitive path reconstruction
    with phases, transitions, and AI dependency evolution.
    """
    from fastapi.responses import RedirectResponse
    return RedirectResponse(
        url=f"/api/v1/cognitive-path/{session_id}",
        status_code=307  # Temporary redirect, preserves method
    )


@router.get(
    "/student/{student_id}",
    response_model=PaginatedResponse[TraceResponse],
    summary="Get Student Traces",
    description="Obtiene todas las trazas de un estudiante a través de todas sus sesiones",
)
async def get_student_traces(
    student_id: str,
    activity_id: Optional[str] = Query(None, description="Filtrar por actividad"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    _current_user: dict = Depends(get_current_user),  # FIX Cortez20: Add auth
) -> PaginatedResponse[TraceResponse]:
    """
    Obtiene todas las trazas de un estudiante.

    Útil para análisis longitudinal del progreso del estudiante.

    FIX Cortez21 DEFECTO 5.1: Use SQL filtering instead of Python filtering

    Args:
        student_id: ID del estudiante
        activity_id: Filtro opcional por actividad
        page: Número de página
        page_size: Elementos por página
        trace_repo: Repositorio de trazas (inyectado)

    Returns:
        PaginatedResponse con lista de trazas del estudiante
    """
    # FIX Cortez21 DEFECTO 5.1: Filter directly in SQL instead of loading all traces
    # Get total count with filter
    total_items = trace_repo.count_by_student_filtered(
        student_id=student_id,
        activity_id=activity_id
    )

    # Calculate pagination
    offset = (page - 1) * page_size
    total_pages = (total_items + page_size - 1) // page_size if total_items > 0 else 0

    # Get paginated traces with filter applied in SQL
    paginated_traces = trace_repo.get_by_student_filtered(
        student_id=student_id,
        activity_id=activity_id,
        limit=page_size,
        offset=offset
    )

    # Convertir a schemas de respuesta
    traces_data = [
        TraceResponse(
            id=t.id,
            session_id=t.session_id,
            student_id=t.student_id,
            activity_id=t.activity_id,
            trace_level=t.trace_level,
            interaction_type=t.interaction_type,
            cognitive_state=t.cognitive_state,
            cognitive_intent=t.cognitive_intent,
            content=t.content,
            ai_involvement=t.ai_involvement,
            context=t.context,
            trace_metadata=t.trace_metadata,  # FIX 10.5 Cortez10: Use trace_metadata directly
            decision_justification=t.decision_justification,
            alternatives_considered=t.alternatives_considered,
            strategy_type=t.strategy_type,
            agent_id=t.agent_id,
            parent_trace_id=t.parent_trace_id,
            created_at=t.created_at,  # FIX 10.4 Cortez10: Use created_at (timestamp is alias)
        )
        for t in paginated_traces
    ]

    # Metadatos de paginación
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
        data=traces_data,
        pagination=pagination_meta,
    )