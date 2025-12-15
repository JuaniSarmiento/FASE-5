"""
Rate Limiting con slowapi para protección de API
"""
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
import logging

logger = logging.getLogger(__name__)


def _get_redis_storage_uri() -> str:
    """
    Obtiene la URI de Redis desde variables de entorno.

    Prioridad:
    1. REDIS_URL (URL completa)
    2. Construir desde REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
    3. Fallback a localhost (solo desarrollo)
    """
    # Opción 1: URL completa
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        return redis_url

    # Opción 2: Construir desde componentes
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = os.getenv("REDIS_PORT", "6379")
    redis_password = os.getenv("REDIS_PASSWORD")

    if redis_password:
        return f"redis://:{redis_password}@{redis_host}:{redis_port}/0"

    # Fallback para desarrollo local
    return f"redis://{redis_host}:{redis_port}/0"


# Configuración del limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/hour", "60/minute"],
    storage_uri=_get_redis_storage_uri(),
    strategy="fixed-window"
)

# Rate limits personalizados por endpoint
RATE_LIMITS = {
    # Endpoints críticos (más restrictivos)
    "create_interaction": "30/minute",
    "create_session": "10/minute",
    "generate_evaluation": "5/minute",
    
    # Endpoints de lectura (menos restrictivos)
    "get_session": "100/minute",
    "list_sessions": "50/minute",
    "get_health": "300/minute",
    
    # Endpoints de exportación (muy restrictivos)
    "export_pdf": "5/hour",
    "export_json": "10/hour",
    
    # Endpoints de autenticación
    "login": "5/minute",
    "register": "3/hour",
}

def get_user_identifier(request: Request) -> str:
    """
    Obtiene identificador único del usuario para rate limiting.
    
    Prioridad:
    1. User ID si está autenticado
    2. API Key si está presente
    3. IP address como fallback
    """
    # Autenticado
    if hasattr(request.state, 'user') and request.state.user:
        return f"user:{request.state.user.id}"
    
    # API Key
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return f"apikey:{api_key[:8]}"
    
    # IP address (fallback)
    return f"ip:{get_remote_address(request)}"

def create_user_limiter():
    """Crea limiter basado en usuario autenticado"""
    return Limiter(
        key_func=get_user_identifier,
        default_limits=["500/hour"],
        storage_uri=_get_redis_storage_uri(),
        strategy="fixed-window"
    )

# Limiter por usuario
user_limiter = create_user_limiter()

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    Handler personalizado para rate limit exceeded.
    Registra el evento y retorna respuesta JSON.
    """
    logger.warning(
        "Rate limit exceeded",
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": get_user_identifier(request),
            "limit": str(exc.detail)
        }
    )
    
    return _rate_limit_exceeded_handler(request, exc)
