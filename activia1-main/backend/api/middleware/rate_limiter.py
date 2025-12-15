"""
Rate Limiting middleware using slowapi
Protege contra abuso de API y controla costos de LLM

CRITICAL FIX (2025-11-25): Migrado de memory:// a Redis para producción.
Previene bypass de rate limiting en deployments multi-worker.
"""
import os
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# Rate Limiter Storage Configuration
# ============================================================================

def _get_storage_uri() -> str:
    """
    Obtiene la URI de storage para rate limiter.

    En producción, DEBE usar Redis para compartir estado entre workers.
    En desarrollo, puede usar memoria local.

    Returns:
        Storage URI para slowapi Limiter

    Raises:
        RuntimeError: Si ENVIRONMENT=production y REDIS_URL no está configurado
    """
    environment = os.getenv("ENVIRONMENT", "development")
    redis_url = os.getenv("REDIS_URL", "")

    # ✅ PRODUCCIÓN: Redis es REQUERIDO
    if environment == "production":
        if not redis_url:
            raise RuntimeError(
                "CRITICAL: REDIS_URL is REQUIRED in production for distributed rate limiting.\n"
                "Without Redis, rate limits can be bypassed with multiple uvicorn workers.\n"
                "Set REDIS_URL in your .env file:\n"
                "  REDIS_URL=redis://localhost:6379/0\n"
                "Or for Redis with password:\n"
                "  REDIS_URL=redis://:password@localhost:6379/0"
            )

        logger.info(
            "Rate limiter using Redis storage (production mode)",
            extra={"redis_url": redis_url.split("@")[-1]}  # Log sin password
        )
        return redis_url

    # ✅ DESARROLLO: Redis preferido, fallback a memoria con warning
    if redis_url:
        logger.info(
            "Rate limiter using Redis storage (development mode)",
            extra={"redis_url": redis_url.split("@")[-1]}
        )
        return redis_url
    else:
        logger.warning(
            "Rate limiter using in-memory storage (NOT suitable for production). "
            "Set REDIS_URL to use Redis. "
            "In multi-worker setups, each worker has independent rate limits."
        )
        return "memory://"


# ✅ Crear limiter con storage configurado
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/hour"],  # Límite por defecto: 100 requests/hora
    storage_uri=_get_storage_uri(),  # ✅ Redis en producción, memoria en dev
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Handler personalizado para errores de rate limit

    Retorna respuesta estructurada con información del límite
    """
    logger.warning(
        f"Rate limit exceeded for {get_remote_address(request)}",
        extra={
            "ip": get_remote_address(request),
            "path": request.url.path,
            "limit": str(exc.detail)
        }
    )

    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "error_code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please wait before retrying.",
                "field": None,
                "extra": {
                    "limit": str(exc.detail),
                    "retry_after": "60 seconds"
                }
            },
            "timestamp": None
        },
        headers={
            "Retry-After": "60"
        }
    )


# Límites específicos por tipo de endpoint
RATE_LIMITS = {
    # ========== SEGURIDAD: Auth endpoints (anti-brute-force) ==========
    "auth_login": "5/minute",      # Máximo 5 intentos de login por minuto por IP
    "auth_register": "3/minute",   # Máximo 3 registros por minuto por IP
    "auth_refresh": "10/minute",   # Máximo 10 refresh tokens por minuto
    "auth_password": "3/minute",   # Máximo 3 cambios de password por minuto

    # Endpoints críticos (usan LLM, tienen costo)
    "interactions": "10/minute",  # Máximo 10 interacciones por minuto
    "evaluations": "5/minute",    # Máximo 5 evaluaciones por minuto

    # Endpoints de consulta (menos restrictivos)
    "sessions": "50/minute",      # Máximo 50 sesiones por minuto
    "traces": "30/minute",        # Máximo 30 consultas de trazas por minuto
    "risks": "30/minute",         # Máximo 30 consultas de riesgos por minuto

    # Endpoints de salud (muy permisivos)
    "health": "100/minute",       # Máximo 100 health checks por minuto
}


def get_rate_limit(endpoint_type: str) -> str:
    """
    Obtiene el límite de rate correspondiente al tipo de endpoint

    Args:
        endpoint_type: Tipo de endpoint (interactions, sessions, etc.)

    Returns:
        String con el límite (ej: "10/minute")
    """
    return RATE_LIMITS.get(endpoint_type, "20/minute")