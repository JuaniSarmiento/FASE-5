"""
Dependency injection para FastAPI
Sistema centralizado para proveer dependencias a los endpoints
"""
from typing import Generator, Optional
import logging
import threading
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db_session
from ..database.repositories import (
    EvaluationRepository,
    RiskRepository,
    SessionRepository,
    TraceRepository,
    TraceSequenceRepository,
    UserRepository,
)
from ..core import AIGateway
from ..core.cache import get_llm_cache
from ..llm import LLMProviderFactory

logger = logging.getLogger(__name__)


# =============================================================================
# Database Dependencies
# =============================================================================


def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obtener una sesión de base de datos.
    Gestiona automáticamente commit/rollback y cierre de sesión.

    Yields:
        Session: Sesión de SQLAlchemy

    Example:
        @app.get("/sessions")
        def get_sessions(db: Session = Depends(get_db)):
            return db.query(SessionDB).all()
    """
    with get_db_session() as session:
        yield session


# =============================================================================
# Repository Dependencies
# =============================================================================


def get_session_repository(db: Session = Depends(get_db)) -> SessionRepository:
    """Dependency para obtener el repositorio de sesiones"""
    return SessionRepository(db)


def get_trace_repository(db: Session = Depends(get_db)) -> TraceRepository:
    """Dependency para obtener el repositorio de trazas"""
    return TraceRepository(db)


def get_risk_repository(db: Session = Depends(get_db)) -> RiskRepository:
    """Dependency para obtener el repositorio de riesgos"""
    return RiskRepository(db)


def get_evaluation_repository(db: Session = Depends(get_db)) -> EvaluationRepository:
    """Dependency para obtener el repositorio de evaluaciones"""
    return EvaluationRepository(db)


def get_sequence_repository(db: Session = Depends(get_db)) -> TraceSequenceRepository:
    """Dependency para obtener el repositorio de secuencias"""
    return TraceSequenceRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Dependency para obtener el repositorio de usuarios"""
    return UserRepository(db)


# =============================================================================
# AI Gateway Dependencies
# =============================================================================


# Cache del LLM provider (singleton - stateless, seguro para reutilizar)
_llm_provider_instance: Optional[LLMProviderFactory] = None
_llm_provider_lock = threading.Lock()  # Lock para thread-safety en singleton


def _initialize_llm_provider():
    """
    Inicializa el LLM provider desde variables de entorno.

    Lee LLM_PROVIDER (mock, openai, anthropic) y configura el provider correspondiente.
    Si no está configurado, usa Mock provider por defecto.

    Returns:
        LLMProvider: Instancia del proveedor configurado
    """
    import os
    from dotenv import load_dotenv

    # Cargar variables de entorno desde .env
    load_dotenv()

    # Obtener tipo de provider desde env (default: mock)
    provider_type = os.getenv("LLM_PROVIDER", "mock")

    try:
        # Crear provider desde variables de entorno
        provider = LLMProviderFactory.create_from_env(provider_type)

        # Obtener información del modelo
        model_info = provider.get_model_info()

        logger.info(
            "LLM Provider initialized successfully",
            extra={
                "provider_type": provider_type,
                "model": model_info.get('model', 'N/A'),
                "supports_streaming": model_info.get('supports_streaming', False)
            }
        )

        return provider

    except ValueError as e:
        # Si falta configuración (ej: API key), usar Mock como fallback
        logger.warning(
            f"Failed to initialize {provider_type} provider, falling back to mock",
            extra={
                "provider_type": provider_type,
                "error": str(e),
                "fallback": "mock"
            }
        )
        return LLMProviderFactory.create("mock")

    except ImportError as e:
        # Si falta paquete (ej: openai no instalado), usar Mock como fallback
        logger.warning(
            f"Missing dependency for {provider_type} provider, falling back to mock",
            extra={
                "provider_type": provider_type,
                "error": str(e),
                "fallback": "mock"
            }
        )
        return LLMProviderFactory.create("mock")


def get_llm_provider():
    """
    Dependency para obtener el LLM provider (singleton).

    SPRINT 4: Permite inyectar el LLM provider directamente en simuladores
    y otros agentes que necesiten generar respuestas con LLM.

    Thread-safe usando lock-first pattern para prevenir race conditions
    en ambientes multi-threaded (ej: uvicorn con múltiples workers).

    FIXED (2025-11-21): Corregida race condition del double-checked locking.
    Ahora usa lock-first pattern (más seguro en Python).

    Returns:
        LLMProvider: Instancia del proveedor configurado (Mock, OpenAI, Gemini, etc.)

    Example:
        @app.post("/simulators/interact")
        def interact(llm_provider: LLMProvider = Depends(get_llm_provider)):
            simulator = SimuladorProfesionalAgent(llm_provider=llm_provider)
            ...
    """
    global _llm_provider_instance

    # Lock-first pattern (más seguro que double-checked locking en Python)
    # El GIL no garantiza atomicidad en la evaluación de 'if', así que
    # adquirimos el lock ANTES de verificar el estado
    with _llm_provider_lock:
        if _llm_provider_instance is None:
            _llm_provider_instance = _initialize_llm_provider()

    return _llm_provider_instance


def get_ai_gateway(
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    risk_repo: RiskRepository = Depends(get_risk_repository),
    evaluation_repo: EvaluationRepository = Depends(get_evaluation_repository),
    sequence_repo: TraceSequenceRepository = Depends(get_sequence_repository),
) -> AIGateway:
    """
    Dependency para obtener el AI Gateway con Dependency Injection completa.
    Crea una nueva instancia por request con repositorios frescos.

    IMPORTANTE: No usar singleton para el gateway ya que los repositorios
    contienen sesiones de BD que deben ser únicas por request.
    El LLM provider y el cache sí se cachean (stateless).

    El LLM provider se inicializa desde variables de entorno:
    - LLM_PROVIDER=mock (default): Mock provider sin API calls
    - LLM_PROVIDER=openai: OpenAI GPT-4/GPT-3.5 (requiere OPENAI_API_KEY)
    - LLM_PROVIDER=anthropic: Claude (requiere ANTHROPIC_API_KEY)

    Cache LLM configurado desde variables de entorno:
    - LLM_CACHE_ENABLED=true (default): Cache habilitado
    - LLM_CACHE_TTL=3600 (default): TTL en segundos (1 hora)
    - LLM_CACHE_MAX_ENTRIES=1000 (default): Máximo de entradas

    Returns:
        AIGateway: Nueva instancia del orquestador central con repositorios inyectados

    Example:
        @app.post("/interactions")
        def process_interaction(
            request: InteractionRequest,
            gateway: AIGateway = Depends(get_ai_gateway)
        ):
            return gateway.process_interaction(...)
    """
    global _llm_provider_instance

    # ✅ FIXED (2025-11-22): Usar lock-first pattern (más seguro que double-checked en Python)
    # El GIL no garantiza atomicidad en evaluación de condiciones, así que
    # adquirimos el lock ANTES de verificar el estado
    with _llm_provider_lock:
        if _llm_provider_instance is None:
            _llm_provider_instance = _initialize_llm_provider()

    # Obtener cache LLM (singleton, compartido entre todos los requests)
    # Leer configuración desde variables de entorno
    import os
    cache_enabled = os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"
    cache_ttl = int(os.getenv("LLM_CACHE_TTL", "3600"))  # 1 hora por defecto
    cache_max_entries = int(os.getenv("LLM_CACHE_MAX_ENTRIES", "1000"))

    llm_cache = get_llm_cache(
        ttl_seconds=cache_ttl,
        max_entries=cache_max_entries,
        enabled=cache_enabled
    )

    # ✅ REFACTORIZADO: Crear NUEVA instancia de gateway por request
    # con TODOS los repositorios inyectados (Dependency Injection completa)
    return AIGateway(
        llm_provider=_llm_provider_instance,
        cognitive_engine=None,  # Usar default (backward compatibility)
        session_repo=session_repo,
        trace_repo=trace_repo,
        risk_repo=risk_repo,
        evaluation_repo=evaluation_repo,
        sequence_repo=sequence_repo,
        cache=llm_cache,  # ✅ Cache LLM inyectado
        config=None
    )


# =============================================================================
# Authentication Dependencies (JWT)
# =============================================================================


async def get_current_user(
    authorization: Optional[str] = Header(None, description="Bearer token"),
    user_repo: UserRepository = Depends(get_user_repository)
) -> dict:
    """
    Dependency para autenticación JWT.

    Valida el token JWT y retorna la información del usuario autenticado.
    En desarrollo, permite acceso sin autenticación.

    Args:
        authorization: Header Authorization con Bearer token
        user_repo: Repositorio de usuarios para verificar en BD

    Returns:
        dict: Información del usuario autenticado con estructura:
            {
                "user_id": str,
                "email": str,
                "username": str,
                "roles": List[str],
                "is_active": bool,
                "is_verified": bool
            }

    Raises:
        HTTPException: Si el token es inválido o el usuario no existe

    Example:
        @app.get("/protected")
        def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    """
    import os
    from .security import verify_token, get_user_id_from_token

    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    if ENVIRONMENT == "production":
        # ✅ Modo estricto en producción - JWT requerido
        if not authorization:
            logger.warning("Authentication required but no token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Please provide a valid token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not authorization.startswith("Bearer "):
            logger.warning("Invalid authorization header format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authorization.replace("Bearer ", "")

        # Verificar token JWT
        user_id = get_user_id_from_token(token)
        if not user_id:
            logger.warning("Invalid or expired JWT token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Buscar usuario en base de datos
        user = user_repo.get_by_id(user_id)
        if not user:
            logger.error(
                "User from valid token not found in database",
                extra={"user_id": user_id}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        # Verificar que el usuario esté activo
        if not user.is_active:
            logger.warning(
                "Inactive user attempted to access",
                extra={"user_id": user.id, "email": user.email}
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        logger.info(
            "User authenticated successfully",
            extra={
                "user_id": user.id,
                "email": user.email,
                "roles": user.roles
            }
        )

        return {
            "user_id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "student_id": user.student_id,
            "roles": user.roles,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
        }
    else:
        # ✅ Modo permisivo en desarrollo - opcional token JWT
        logger.debug("Development mode - permissive authentication")

        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")

            # Intentar validar token si se proporciona
            user_id = get_user_id_from_token(token)
            if user_id:
                user = user_repo.get_by_id(user_id)
                if user:
                    logger.debug(
                        "User authenticated with JWT in dev mode",
                        extra={"user_id": user.id, "email": user.email}
                    )
                    return {
                        "user_id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "full_name": user.full_name,
                        "student_id": user.student_id,
                        "roles": user.roles,
                        "is_active": user.is_active,
                        "is_verified": user.is_verified,
                    }

        # Permitir acceso sin autenticación solo en desarrollo
        logger.debug("Anonymous access allowed in development mode")
        return {
            "user_id": "anonymous",
            "email": "anonymous@example.com",
            "username": "anonymous",
            "full_name": "Anonymous User",
            "student_id": None,
            "roles": ["student"],
            "is_active": True,
            "is_verified": False,
        }


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Dependency para obtener usuario activo (no bloqueado/deshabilitado).

    Args:
        current_user: Usuario autenticado

    Returns:
        dict: Usuario activo

    Raises:
        HTTPException: Si el usuario está inactivo
    """
    # Verificar si el usuario está activo (desde el token JWT o verificación adicional)
    if not current_user.get("is_active", True):
        logger.warning(
            "Inactive user attempted access",
            extra={
                "user_id": current_user.get("user_id"),
                "email": current_user.get("email"),
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive. Please contact an administrator."
        )

    return current_user


async def require_role(required_role: str):
    """
    Dependency factory para requerir un rol específico.

    Args:
        required_role: Rol requerido (student, instructor, admin)

    Returns:
        Dependency function

    Example:
        require_instructor = Depends(require_role("instructor"))

        @app.post("/evaluations")
        def create_evaluation(user: dict = require_instructor):
            ...
    """

    async def role_checker(current_user: dict = Depends(get_current_active_user)) -> dict:
        user_roles = current_user.get("roles", [])
        if required_role not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role}",
            )
        return current_user

    return role_checker


async def require_teacher_role(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency to verify user has teacher/instructor role.

    Raises:
        HTTPException 403: If user is not a teacher
    """
    user_roles = current_user.get("roles", [])
    if "teacher" not in user_roles and "instructor" not in user_roles and "admin" not in user_roles:
        logger.warning(
            "Unauthorized teacher access attempt",
            extra={
                "user_id": current_user.get("user_id"),
                "email": current_user.get("email"),
                "roles": user_roles,
                "attempted_action": "teacher_tools_access"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher or admin role required. Your roles: " + ", ".join(user_roles)
        )
    return current_user


# FIX 1.2: Centralized role dependencies (Cortez2 audit)
async def require_admin_role(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency that requires admin role.

    Raises:
        HTTPException 403: If user is not an admin
    """
    user_roles = current_user.get("roles", [])
    if "admin" not in user_roles:
        logger.warning(
            "Unauthorized admin access attempt",
            extra={
                "user_id": current_user.get("user_id"),
                "email": current_user.get("email"),
                "roles": user_roles,
                "attempted_action": "admin_access"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required. Your roles: " + ", ".join(user_roles)
        )
    return current_user


async def require_student_role(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Dependency that requires student role.

    Raises:
        HTTPException 403: If user is not a student
    """
    user_roles = current_user.get("roles", [])
    if "student" not in user_roles and "admin" not in user_roles:
        logger.warning(
            "Unauthorized student access attempt",
            extra={
                "user_id": current_user.get("user_id"),
                "email": current_user.get("email"),
                "roles": user_roles,
                "attempted_action": "student_access"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student role required. Your roles: " + ", ".join(user_roles)
        )
    return current_user


# =============================================================================
# Validation Dependencies
# =============================================================================


async def validate_session_exists(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
):
    """
    Dependency para validar que una sesión existe.

    Args:
        session_id: ID de la sesión
        session_repo: Repositorio de sesiones

    Returns:
        SessionDB: Sesión encontrada

    Raises:
        HTTPException: Si la sesión no existe
    """
    from ..api.exceptions import SessionNotFoundError

    session = session_repo.get_by_id(session_id)
    if not session:
        raise SessionNotFoundError(session_id)

    return session