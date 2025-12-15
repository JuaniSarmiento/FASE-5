"""
Router para gestión de eventos de simuladores

Endpoints:
- POST /events - Crear evento de simulador
- GET /events?session_id={id} - Listar eventos de una sesión
- POST /events/batch - Crear múltiples eventos en batch
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.core.constants import utc_now

from ...database.models import SimulatorEventDB, SessionDB
from ..deps import get_db, get_session_repository, get_current_user
from ...database.repositories import SessionRepository
from ..schemas.common import APIResponse, PaginatedResponse, PaginationMeta
from ..config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, MIN_PAGE_SIZE

router = APIRouter(prefix="/events", tags=["Simulator Events"])


# ============================================================================
# SCHEMAS
# ============================================================================

class EventCreate(BaseModel):
    """Schema para crear un evento"""
    session_id: str
    event_type: str
    event_data: dict = Field(default_factory=dict)
    description: Optional[str] = None
    severity: Optional[str] = Field(None, description="info, warning, critical")


class EventResponse(BaseModel):
    """Response con información de un evento"""
    id: str
    session_id: str
    student_id: str
    simulator_type: str
    event_type: str
    event_data: dict
    description: Optional[str]
    severity: Optional[str]
    timestamp: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "",
    response_model=APIResponse[EventResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Event",
    description="Crea un evento de simulador"
)
async def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    session_repo: SessionRepository = Depends(get_session_repository),
    current_user: dict = Depends(get_current_user),
) -> APIResponse[EventResponse]:
    """
    Crea un evento de simulador.
    
    Los eventos son disparados por los simuladores al completar acciones
    y sirven como input para el análisis de riesgos y evaluaciones.
    
    Ejemplos de eventos:
    - backlog_created: Se creó el backlog (Product Owner)
    - sprint_planning_complete: Se completó el sprint planning (Scrum Master)
    - technical_decision_made: Se tomó una decisión técnica
    - risk_identified_by_user: El usuario identificó un riesgo
    """
    # FIX 2.4: Use repository pattern instead of direct DB access
    session = session_repo.get_by_id(event_data.session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {event_data.session_id} not found"
        )
    
    # Crear evento
    db_event = SimulatorEventDB(
        session_id=event_data.session_id,
        student_id=session.student_id,
        simulator_type=session.simulator_type or "UNKNOWN",
        event_type=event_data.event_type,
        event_data=event_data.event_data,
        description=event_data.description,
        severity=event_data.severity,
        timestamp=utc_now(),
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # Convertir a response
    response_data = EventResponse(
        id=db_event.id,
        session_id=db_event.session_id,
        student_id=db_event.student_id,
        simulator_type=db_event.simulator_type,
        event_type=db_event.event_type,
        event_data=db_event.event_data,
        description=db_event.description,
        severity=db_event.severity,
        timestamp=db_event.timestamp,
        created_at=db_event.created_at,
    )
    
    return APIResponse(
        success=True,
        data=response_data,
        message=f"Event {event_data.event_type} created successfully"
    )


@router.get(
    "",
    response_model=PaginatedResponse[EventResponse],
    summary="List Events",
    description="Lista eventos con filtros opcionales"
)
async def list_events(
    session_id: Optional[str] = Query(None, description="Filtrar por sesión"),
    student_id: Optional[str] = Query(None, description="Filtrar por estudiante"),
    simulator_type: Optional[str] = Query(None, description="Filtrar por tipo de simulador"),
    event_type: Optional[str] = Query(None, description="Filtrar por tipo de evento"),
    page: int = Query(1, ge=MIN_PAGE_SIZE, description="Número de página"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> PaginatedResponse[EventResponse]:
    """
    Lista eventos con filtros y paginación.
    """
    # Construir query con filtros
    query = db.query(SimulatorEventDB)
    
    if session_id:
        query = query.filter(SimulatorEventDB.session_id == session_id)
    if student_id:
        query = query.filter(SimulatorEventDB.student_id == student_id)
    if simulator_type:
        query = query.filter(SimulatorEventDB.simulator_type == simulator_type)
    if event_type:
        query = query.filter(SimulatorEventDB.event_type == event_type)
    
    # Contar total
    total_items = query.count()
    
    # Paginación
    offset = (page - 1) * page_size
    total_pages = (total_items + page_size - 1) // page_size
    
    # Aplicar paginación y ordenar por timestamp descendente
    db_events = (
        query.order_by(SimulatorEventDB.timestamp.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    
    # Convertir a response
    events_data = [
        EventResponse(
            id=e.id,
            session_id=e.session_id,
            student_id=e.student_id,
            simulator_type=e.simulator_type,
            event_type=e.event_type,
            event_data=e.event_data,
            description=e.description,
            severity=e.severity,
            timestamp=e.timestamp,
            created_at=e.created_at,
        )
        for e in db_events
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
        data=events_data,
        pagination=pagination_meta,
    )


@router.post(
    "/batch",
    response_model=APIResponse[List[EventResponse]],
    status_code=status.HTTP_201_CREATED,
    summary="Create Batch Events",
    description="Crea múltiples eventos en una sola operación"
)
async def create_batch_events(
    events: List[EventCreate],
    db: Session = Depends(get_db),
    session_repo: SessionRepository = Depends(get_session_repository),
    current_user: dict = Depends(get_current_user),
) -> APIResponse[List[EventResponse]]:
    """
    Crea múltiples eventos en batch.
    
    Útil cuando un simulador genera múltiples eventos relacionados
    (ej: creación de backlog genera 5 eventos de user stories)
    """
    created_events = []
    
    for event_data in events:
        # FIX 2.4: Use repository pattern instead of direct DB access
        session = session_repo.get_by_id(event_data.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {event_data.session_id} not found"
            )
        
        # Crear evento
        db_event = SimulatorEventDB(
            session_id=event_data.session_id,
            student_id=session.student_id,
            simulator_type=session.simulator_type or "UNKNOWN",
            event_type=event_data.event_type,
            event_data=event_data.event_data,
            description=event_data.description,
            severity=event_data.severity,
            timestamp=utc_now(),
        )
        
        db.add(db_event)
        created_events.append(db_event)
    
    db.commit()
    
    # Refresh y convertir a response
    response_data = []
    for e in created_events:
        db.refresh(e)
        response_data.append(
            EventResponse(
                id=e.id,
                session_id=e.session_id,
                student_id=e.student_id,
                simulator_type=e.simulator_type,
                event_type=e.event_type,
                event_data=e.event_data,
                description=e.description,
                severity=e.severity,
                timestamp=e.timestamp,
                created_at=e.created_at,
            )
        )
    
    return APIResponse(
        success=True,
        data=response_data,
        message=f"{len(response_data)} events created successfully"
    )
