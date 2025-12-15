"""
Router para gestión de actividades creadas por docentes
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from ...database.repositories import ActivityRepository
from ...database.models import ActivityDB
from ..deps import get_db, require_teacher_role
from ..schemas.activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityListResponse,
    ActivityPublishRequest,
    ActivityArchiveRequest,
)
from ..schemas.common import APIResponse, PaginatedResponse, PaginationParams, PaginationMeta
from ..exceptions import AINativeAPIException
from ..config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, MIN_PAGE_SIZE

router = APIRouter(prefix="/activities", tags=["Activities"])


class ActivityNotFoundError(AINativeAPIException):
    """Excepción para actividad no encontrada"""

    def __init__(self, activity_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="ACTIVITY_NOT_FOUND",
            message=f"Activity '{activity_id}' not found",
            extra={"activity_id": activity_id},
        )


class ActivityAlreadyExistsError(AINativeAPIException):
    """Excepción para actividad que ya existe"""

    def __init__(self, activity_id: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="ACTIVITY_ALREADY_EXISTS",
            message=f"Activity '{activity_id}' already exists",
            extra={"activity_id": activity_id},
        )


def get_activity_repository(db: Session = Depends(get_db)) -> ActivityRepository:
    """Dependency para obtener el repositorio de actividades"""
    return ActivityRepository(db)


@router.post(
    "",
    response_model=APIResponse[ActivityResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Activity",
    description="Crea una nueva actividad con políticas pedagógicas configurables",
)
async def create_activity(
    activity_data: ActivityCreate,
    activity_repo: ActivityRepository = Depends(get_activity_repository),
    _current_user: dict = Depends(require_teacher_role),  # FIX Cortez19: Add teacher auth
) -> APIResponse[ActivityResponse]:
    """
    Crea una nueva actividad de aprendizaje.

    Args:
        activity_data: Datos de la actividad a crear
        activity_repo: Repositorio de actividades (inyectado)

    Returns:
        APIResponse con la actividad creada

    Raises:
        ActivityAlreadyExistsError: Si ya existe una actividad con ese activity_id

    Example:
        POST /api/v1/activities
        {
            "activity_id": "prog2_tp1_colas",
            "title": "Implementación de Cola Circular",
            "instructions": "Implementar una cola circular que...",
            "teacher_id": "teacher_001",
            "policies": {
                "max_help_level": "MEDIO",
                "block_complete_solutions": true,
                "require_justification": true,
                "allow_code_snippets": false,
                "risk_thresholds": {
                    "ai_dependency": 0.6
                }
            }
        }
    """
    # Verificar que no exista ya
    existing = activity_repo.get_by_activity_id(activity_data.activity_id)
    if existing:
        raise ActivityAlreadyExistsError(activity_data.activity_id)

    # Crear actividad en la base de datos
    db_activity = activity_repo.create(
        activity_id=activity_data.activity_id,
        title=activity_data.title,
        instructions=activity_data.instructions,
        teacher_id=activity_data.teacher_id,
        policies=activity_data.policies.model_dump(),  # Convertir PolicyConfig a dict
        description=activity_data.description,
        evaluation_criteria=activity_data.evaluation_criteria or [],
        subject=activity_data.subject,
        difficulty=activity_data.difficulty,
        estimated_duration_minutes=activity_data.estimated_duration_minutes,
        tags=activity_data.tags or [],
    )

    # Convertir a schema de respuesta
    response_data = ActivityResponse.model_validate(db_activity)

    return APIResponse(
        success=True,
        data=response_data,
        message=f"Activity created successfully: {db_activity.activity_id}",
    )


@router.get(
    "",
    response_model=PaginatedResponse[ActivityResponse],
    summary="List Activities",
    description="Lista todas las actividades con filtros opcionales y paginación",
)
async def list_activities(
    teacher_id: Optional[str] = Query(None, description="Filtrar por ID de docente"),
    status: Optional[str] = Query(None, description="Filtrar por estado (draft, active, archived)"),
    subject: Optional[str] = Query(None, description="Filtrar por materia"),
    difficulty: Optional[str] = Query(None, description="Filtrar por dificultad (INICIAL, INTERMEDIO, AVANZADO)"),
    page: int = Query(1, ge=MIN_PAGE_SIZE, description="Número de página"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE, description="Elementos por página"),
    activity_repo: ActivityRepository = Depends(get_activity_repository),
    db: Session = Depends(get_db),
) -> PaginatedResponse[ActivityResponse]:
    """
    Lista actividades con filtros y paginación.

    Args:
        teacher_id: Filtrar por docente (opcional)
        status: Filtrar por estado (opcional)
        subject: Filtrar por materia (opcional)
        difficulty: Filtrar por dificultad (opcional)
        page: Número de página (default: 1)
        page_size: Elementos por página (default: 20, max: 100)
        activity_repo: Repositorio de actividades (inyectado)
        db: Sesión de base de datos (inyectado)

    Returns:
        PaginatedResponse con lista de actividades
    """
    # Construir query base con filtros
    query = db.query(ActivityDB)

    if teacher_id:
        query = query.filter(ActivityDB.teacher_id == teacher_id)
    if status:
        query = query.filter(ActivityDB.status == status)
    if subject:
        query = query.filter(ActivityDB.subject == subject)
    if difficulty:
        query = query.filter(ActivityDB.difficulty == difficulty)

    # Contar total de elementos
    total_items = query.count()

    # Calcular paginación
    offset = (page - 1) * page_size
    total_pages = (total_items + page_size - 1) // page_size

    # Aplicar paginación y ordenar por fecha de creación descendente
    db_activities = (
        query.order_by(ActivityDB.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Convertir a schemas de respuesta
    activities_data = [
        ActivityResponse.model_validate(activity)
        for activity in db_activities
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
        data=activities_data,
        pagination=pagination_meta,
    )


@router.get(
    "/{activity_id}",
    response_model=APIResponse[ActivityResponse],
    summary="Get Activity",
    description="Obtiene detalles completos de una actividad específica",
)
async def get_activity(
    activity_id: str,
    activity_repo: ActivityRepository = Depends(get_activity_repository),
) -> APIResponse[ActivityResponse]:
    """
    Obtiene detalles completos de una actividad.

    Args:
        activity_id: ID de la actividad
        activity_repo: Repositorio de actividades (inyectado)

    Returns:
        APIResponse con detalles de la actividad

    Raises:
        ActivityNotFoundError: Si la actividad no existe
    """
    # Buscar actividad
    db_activity = activity_repo.get_by_activity_id(activity_id)
    if not db_activity:
        raise ActivityNotFoundError(activity_id)

    # Convertir a schema de respuesta
    response_data = ActivityResponse.model_validate(db_activity)

    return APIResponse(
        success=True,
        data=response_data,
        message=f"Activity retrieved: {activity_id}",
    )


@router.put(
    "/{activity_id}",
    response_model=APIResponse[ActivityResponse],
    summary="Update Activity",
    description="Actualiza una actividad existente",
)
async def update_activity(
    activity_id: str,
    activity_update: ActivityUpdate,
    activity_repo: ActivityRepository = Depends(get_activity_repository),
    _current_user: dict = Depends(require_teacher_role),  # FIX Cortez19: Add teacher auth
) -> APIResponse[ActivityResponse]:
    """
    Actualiza una actividad existente.

    Args:
        activity_id: ID de la actividad
        activity_update: Datos a actualizar
        activity_repo: Repositorio de actividades (inyectado)

    Returns:
        APIResponse con la actividad actualizada

    Raises:
        ActivityNotFoundError: Si la actividad no existe

    Example:
        PUT /api/v1/activities/prog2_tp1_colas
        {
            "title": "Implementación de Cola Circular (Actualizado)",
            "difficulty": "AVANZADO",
            "policies": {
                "max_help_level": "BAJO",
                "block_complete_solutions": true,
                "require_justification": true,
                "allow_code_snippets": false
            }
        }
    """
    # Verificar que la actividad existe
    db_activity = activity_repo.get_by_activity_id(activity_id)
    if not db_activity:
        raise ActivityNotFoundError(activity_id)

    # Preparar datos de actualización
    update_data = activity_update.model_dump(exclude_unset=True)

    # Convertir PolicyConfig a dict si está presente
    if "policies" in update_data and update_data["policies"] is not None:
        update_data["policies"] = update_data["policies"]

    # Actualizar actividad
    updated_activity = activity_repo.update(activity_id, **update_data)

    if not updated_activity:
        raise ActivityNotFoundError(activity_id)

    # Convertir a schema de respuesta
    response_data = ActivityResponse.model_validate(updated_activity)

    return APIResponse(
        success=True,
        data=response_data,
        message=f"Activity updated: {activity_id}",
    )


@router.post(
    "/{activity_id}/publish",
    response_model=APIResponse[ActivityResponse],
    summary="Publish Activity",
    description="Publica una actividad (cambia estado de draft a active)",
)
async def publish_activity(
    activity_id: str,
    activity_repo: ActivityRepository = Depends(get_activity_repository),
    _current_user: dict = Depends(require_teacher_role),  # FIX Cortez19: Add teacher auth
) -> APIResponse[ActivityResponse]:
    """
    Publica una actividad (cambia estado de draft a active).

    Args:
        activity_id: ID de la actividad
        activity_repo: Repositorio de actividades (inyectado)

    Returns:
        APIResponse con la actividad publicada

    Raises:
        ActivityNotFoundError: Si la actividad no existe

    Example:
        POST /api/v1/activities/prog2_tp1_colas/publish
    """
    # Publicar actividad
    published_activity = activity_repo.publish(activity_id)

    if not published_activity:
        raise ActivityNotFoundError(activity_id)

    # Convertir a schema de respuesta
    response_data = ActivityResponse.model_validate(published_activity)

    return APIResponse(
        success=True,
        data=response_data,
        message=f"Activity published: {activity_id}",
    )


@router.post(
    "/{activity_id}/archive",
    response_model=APIResponse[ActivityResponse],
    summary="Archive Activity",
    description="Archiva una actividad",
)
async def archive_activity(
    activity_id: str,
    activity_repo: ActivityRepository = Depends(get_activity_repository),
    _current_user: dict = Depends(require_teacher_role),  # FIX Cortez19: Add teacher auth
) -> APIResponse[ActivityResponse]:
    """
    Archiva una actividad.

    Args:
        activity_id: ID de la actividad
        activity_repo: Repositorio de actividades (inyectado)

    Returns:
        APIResponse con la actividad archivada

    Raises:
        ActivityNotFoundError: Si la actividad no existe

    Example:
        POST /api/v1/activities/prog2_tp1_colas/archive
    """
    # Archivar actividad
    archived_activity = activity_repo.archive(activity_id)

    if not archived_activity:
        raise ActivityNotFoundError(activity_id)

    # Convertir a schema de respuesta
    response_data = ActivityResponse.model_validate(archived_activity)

    return APIResponse(
        success=True,
        data=response_data,
        message=f"Activity archived: {activity_id}",
    )


@router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Activity",
    description="Elimina una actividad (soft delete, archiva en lugar de eliminar físicamente)",
)
async def delete_activity(
    activity_id: str,
    activity_repo: ActivityRepository = Depends(get_activity_repository),
    _current_user: dict = Depends(require_teacher_role),  # FIX Cortez19: Add teacher auth
):
    """
    Elimina una actividad (soft delete).

    NOTA: Esta operación archiva la actividad en lugar de eliminarla físicamente
    para preservar el historial.

    Args:
        activity_id: ID de la actividad
        activity_repo: Repositorio de actividades (inyectado)

    Raises:
        ActivityNotFoundError: Si la actividad no existe
    """
    # Verificar que la actividad existe
    db_activity = activity_repo.get_by_activity_id(activity_id)
    if not db_activity:
        raise ActivityNotFoundError(activity_id)

    # Eliminar (soft delete)
    success = activity_repo.delete(activity_id)

    if not success:
        raise ActivityNotFoundError(activity_id)

    # No retornar contenido (204 No Content)
    return None