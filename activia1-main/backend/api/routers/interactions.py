"""
Router para procesar interacciones estudiante-IA
Este es el endpoint principal del sistema AI-Native
"""
import logging
from typing import List
from uuid import uuid4
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.core.constants import utc_now
from sqlalchemy.exc import OperationalError, IntegrityError
from pydantic import ValidationError

from ...core import AIGateway
from ...database.repositories import SessionRepository, TraceRepository
from ...database.transaction import transaction
from ..deps import get_ai_gateway, get_session_repository, get_trace_repository, get_db, get_current_user
from ..schemas.interaction import (
    InteractionRequest,
    InteractionResponse,
    InteractionHistory,
    InteractionSummary,
)

logger = logging.getLogger(__name__)
from ..schemas.common import APIResponse
from ..exceptions import SessionNotFoundError, InvalidInteractionError, GovernanceBlockedError

router = APIRouter(prefix="/interactions", tags=["Interactions"])


@router.post(
    "",
    response_model=APIResponse[InteractionResponse],
    status_code=status.HTTP_201_CREATED,  # POST creating resource should return 201
    summary="Process Interaction",
    description="""
    Procesa una interacción del estudiante con el sistema AI-Native.

    Este endpoint:
    1. Valida que la sesión existe y está activa
    2. Clasifica la interacción (estado cognitivo, tipo)
    3. Verifica políticas de gobernanza
    4. Procesa con el agente apropiado (T-IA-Cog, S-IA-X, etc.)
    5. Captura traza N4 de la interacción
    6. Detecta riesgos en paralelo
    7. Retorna respuesta pedagógica

    **Rate Limit**: 100 requests per hour (global, protección contra abuso y control de costos LLM)
    """,
)
async def process_interaction(
    request: InteractionRequest,
    db: Session = Depends(get_db),
    gateway: AIGateway = Depends(get_ai_gateway),
    current_user: dict = Depends(get_current_user),
) -> APIResponse[InteractionResponse]:
    """
    Procesa una interacción del estudiante con el sistema AI-Native.

    Este es el endpoint principal que orquesta todo el flujo de procesamiento:
    - Clasificación cognitiva (CRPE)
    - Verificación de gobernanza (GOV-IA)
    - Procesamiento pedagógico (T-IA-Cog, S-IA-X, etc.)
    - Captura de trazabilidad N4 (TC-N4)
    - Análisis de riesgos (AR-IA)

    Args:
        request: Datos de la interacción
        gateway: AI Gateway orquestador (inyectado)
        session_repo: Repositorio de sesiones (inyectado)
        trace_repo: Repositorio de trazas (inyectado)

    Returns:
        APIResponse con la respuesta del sistema

    Raises:
        SessionNotFoundError: Si la sesión no existe
        InvalidInteractionError: Si la interacción es inválida
        GovernanceBlockedError: Si la interacción es bloqueada por gobernanza

    Example:
        POST /api/v1/interactions
        {
            "session_id": "session_abc123",
            "prompt": "¿Cómo implemento una cola circular?",
            "context": {"code_snippet": "class Queue..."},
            "cognitive_intent": "UNDERSTANDING"
        }
    """
    # ✅ TRANSACTION MANAGEMENT: Wrap entire interaction processing in explicit transaction
    # Ensures atomicity: all DB operations (traces, risks, etc.) commit together or rollback together
    with transaction(db, "Process student interaction"):
        # Create repositories with the shared DB session
        session_repo = SessionRepository(db)
        trace_repo = TraceRepository(db)

        # 1. Validar que la sesión existe y está activa
        db_session = session_repo.get_by_id(request.session_id)
        if not db_session:
            raise SessionNotFoundError(request.session_id)

        if db_session.status != "active":
            raise InvalidInteractionError(
                f"Session is not active: {db_session.status}",
                {"session_id": request.session_id, "status": db_session.status}
            )

        # ✅ ELIMINADO: Ya no es necesaria sincronización manual DB → Gateway
        # El Gateway ahora es STATELESS y obtiene la sesión directamente de BD
        # ❌ ANTIGUA SINCRONIZACIÓN MANUAL:
        # if request.session_id not in gateway.active_sessions:
        #     gateway.create_session(...)

        # 2. Procesar interacción a través del AI Gateway (STATELESS)
        # El gateway orquestará todos los componentes (CRPE, GOV-IA, agentes, TC-N4, AR-IA)
        # y obtendrá la sesión directamente desde BD vía session_repo inyectado
        # FIXED (2025-11-21): Excepciones específicas en lugar de Exception genérico
        try:
            result = await gateway.process_interaction(
                session_id=request.session_id,
                prompt=request.prompt,
                context=request.context or {},
            )
        except ValidationError as e:
            # Error de validación de datos (Pydantic)
            logger.error(
                "Validation error in interaction processing",
                exc_info=True,
                extra={"session_id": request.session_id, "validation_errors": e.errors()}
            )
            raise InvalidInteractionError(
                f"Invalid data in interaction: {e}",
                {"session_id": request.session_id, "validation_errors": e.errors()}
            )
        except KeyError as e:
            # Error de clave faltante en diccionarios (probablemente config o context)
            logger.error(
                "Missing required key in interaction",
                exc_info=True,
                extra={"session_id": request.session_id, "missing_key": str(e)}
            )
            raise InvalidInteractionError(
                f"Missing required data: {e}",
                {"session_id": request.session_id, "error": str(e)}
            )
        except ValueError as e:
            # Error de valor inválido (puede incluir "bloqueada" de gobernanza)
            error_msg = str(e)
            logger.warning(
                "Value error in interaction processing",
                exc_info=True,
                extra={"session_id": request.session_id, "error": error_msg}
            )

            # Verificar si fue bloqueado por gobernanza
            if "bloqueada" in error_msg.lower() or "blocked" in error_msg.lower():
                raise GovernanceBlockedError(
                    reason=error_msg,
                    policy="GOVERNANCE_POLICY_CHECK"
                )

            raise InvalidInteractionError(
                f"Invalid value in interaction: {error_msg}",
                {"session_id": request.session_id, "error": error_msg}
            )
        except OperationalError as e:
            # Error de base de datos (conexión perdida, timeout, etc.)
            logger.error(
                "Database error during interaction processing",
                exc_info=True,
                extra={"session_id": request.session_id, "db_error": str(e)}
            )
            raise InvalidInteractionError(
                "Database error occurred while processing interaction",
                {"session_id": request.session_id, "error": "database_error"}
            )
        except Exception as e:
            # Catch-all para errores inesperados (con logging crítico)
            logger.critical(
                "Unexpected error in interaction processing",
                exc_info=True,  # Stack trace completo
                extra={"session_id": request.session_id, "error_type": type(e).__name__, "error": str(e)}
            )
            raise InvalidInteractionError(
                f"Unexpected error processing interaction: {type(e).__name__}",
                {"session_id": request.session_id, "error": str(e)}
            )

        # 3. Obtener la traza más reciente (corresponde a esta interacción)
        # FIX N+1 #1: Usar get_latest_by_session() en lugar de cargar TODAS las trazas
        latest_trace = trace_repo.get_latest_by_session(request.session_id)

        # 4. Determinar si la interacción fue bloqueada
        blocked = result.get("blocked", False)
        block_reason = result.get("block_reason", None)

        # 5. Obtener riesgos detectados en esta interacción
        # (AR-IA puede haber detectado riesgos en paralelo)
        risks_detected = result.get("risks_detected", [])

        # 6. Construir respuesta con UUID (seguro y único)
        interaction_id = str(uuid4())

        response_data = InteractionResponse(
            interaction_id=interaction_id,
            session_id=request.session_id,
            response=result.get("response", ""),
            agent_used=result.get("agent_used", db_session.mode),
            cognitive_state_detected=result.get("cognitive_state", "UNKNOWN"),
            ai_involvement=latest_trace.ai_involvement if latest_trace else 0.5,
            blocked=blocked,
            block_reason=block_reason,
            trace_id=latest_trace.id if latest_trace else "",
            risks_detected=risks_detected,
            timestamp=utc_now(),
            # FIX FLUJO1-1: Incluir tokens_used del resultado del LLM
            tokens_used=result.get("tokens_used"),
        )

    # Transaction committed successfully - return response
    return APIResponse(
        success=True,
        data=response_data,
        message="Interaction processed successfully" if not blocked else "Interaction blocked by governance",
    )


@router.get(
    "/{session_id}/history",
    response_model=APIResponse[InteractionHistory],
    summary="Get Interaction History",
    description="Obtiene el historial completo de interacciones de una sesión",
)
async def get_interaction_history(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
) -> APIResponse[InteractionHistory]:
    """
    Obtiene el historial de interacciones de una sesión.

    Reconstruye todas las interacciones desde las trazas N4 capturadas.

    Args:
        session_id: ID de la sesión
        session_repo: Repositorio de sesiones (inyectado)
        trace_repo: Repositorio de trazas (inyectado)

    Returns:
        APIResponse con el historial de interacciones

    Raises:
        SessionNotFoundError: Si la sesión no existe
    """
    # Verificar que la sesión existe
    db_session = session_repo.get_by_id(session_id)
    if not db_session:
        raise SessionNotFoundError(session_id)

    # Obtener todas las trazas de la sesión
    traces = trace_repo.get_by_session(session_id)

    # Filtrar solo trazas de tipo STUDENT_PROMPT (interacciones del estudiante)
    student_traces = [
        t for t in traces
        if t.interaction_type == "STUDENT_PROMPT"
    ]

    # Construir resúmenes de interacciones
    interaction_summaries = []
    blocked_count = 0

    for trace in student_traces:
        # Verificar si fue bloqueada
        # NOTE: ORM uses trace_metadata, not metadata (SQLAlchemy reserved word)
        trace_meta = trace.trace_metadata or {}
        is_blocked = trace_meta.get("blocked", False)
        if is_blocked:
            blocked_count += 1

        # Crear resumen
        prompt_preview = trace.content[:100] if trace.content else ""
        if len(trace.content or "") > 100:
            prompt_preview += "..."

        summary = InteractionSummary(
            id=trace.id,
            prompt_preview=prompt_preview,
            agent_used=trace_meta.get("agent_used", "UNKNOWN"),
            cognitive_state=trace.cognitive_state or "UNKNOWN",
            ai_involvement=trace.ai_involvement or 0.5,
            blocked=is_blocked,
            timestamp=trace.timestamp,
        )
        interaction_summaries.append(summary)

    # Calcular promedio de AI involvement
    ai_involvements = [t.ai_involvement for t in student_traces if t.ai_involvement is not None]
    avg_ai_involvement = sum(ai_involvements) / len(ai_involvements) if ai_involvements else 0.5

    # Construir historial
    history = InteractionHistory(
        session_id=session_id,
        interactions=interaction_summaries,
        total_interactions=len(interaction_summaries),
        avg_ai_involvement=avg_ai_involvement,
        blocked_count=blocked_count,
    )

    return APIResponse(
        success=True,
        data=history,
        message=f"Retrieved {len(interaction_summaries)} interactions for session {session_id}",
    )