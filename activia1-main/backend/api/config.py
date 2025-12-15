"""
Configuración compartida para la API

Centraliza todas las configuraciones de la aplicación FastAPI,
leyendo valores desde variables de entorno con valores por defecto seguros.
"""
import os
from typing import List
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
load_dotenv()


# =============================================================================
# Configuración de Paginación
# =============================================================================

from ..core.constants import (
    DEFAULT_PAGE_SIZE as _DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE as _MAX_PAGE_SIZE,
    MIN_PAGE_SIZE as _MIN_PAGE_SIZE,
)

DEFAULT_PAGE_SIZE = _DEFAULT_PAGE_SIZE
MAX_PAGE_SIZE = _MAX_PAGE_SIZE
MIN_PAGE_SIZE = _MIN_PAGE_SIZE


# =============================================================================
# Configuración de CORS
# =============================================================================

def get_allowed_origins() -> List[str]:
    """
    Obtiene la lista de orígenes permitidos para CORS desde variable de entorno.

    Variable de entorno: ALLOWED_ORIGINS
    Formato: URLs separadas por comas
    Ejemplo: "http://localhost:3000,http://localhost:5173,https://app.example.com"

    Returns:
        List[str]: Lista de orígenes permitidos

    Note:
        En desarrollo, se permiten localhost en puertos comunes (3000, 5173, 8080).
        En producción, DEBE configurarse ALLOWED_ORIGINS con los dominios reales.
    """
    origins_env = os.getenv(
        "ALLOWED_ORIGINS",
        # Valores por defecto para desarrollo local (incluye puerto 3001 del frontend)
        "http://localhost:3000,http://localhost:3001,http://localhost:5173,http://localhost:8080"
    )

    # Split por comas y limpiar espacios
    origins = [origin.strip() for origin in origins_env.split(",") if origin.strip()]

    logger.info(f"CORS allowed origins configured: {len(origins)} origins")

    return origins


# Lista de orígenes permitidos (calculada al importar el módulo)
CORS_ALLOWED_ORIGINS = get_allowed_origins()


# =============================================================================
# Configuración de Rate Limiting
# =============================================================================

RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))


# =============================================================================
# Configuración de Timeouts
# =============================================================================

REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))
DB_QUERY_TIMEOUT_SECONDS = int(os.getenv("DB_QUERY_TIMEOUT_SECONDS", "10"))


# =============================================================================
# Configuración de Seguridad
# =============================================================================

# Secret key para JWT (REQUERIDO - sin default inseguro)
# FIXED (2025-11-21): Eliminado default inseguro. Ahora DEBE configurarse.
SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "SECURITY ERROR: SECRET_KEY environment variable is REQUIRED.\n"
        "Generate a secure random key with:\n"
        "  python -c 'import secrets; print(secrets.token_urlsafe(32))'\n"
        "Then set it in your .env file:\n"
        "  SECRET_KEY=<generated_key>"
    )

# Validar longitud mínima (prevenir claves débiles)
if len(SECRET_KEY) < 32:
    raise RuntimeError(
        f"SECURITY ERROR: SECRET_KEY must be at least 32 characters long.\n"
        f"Current length: {len(SECRET_KEY)} characters.\n"
        f"Generate a new one with:\n"
        f"  python -c 'import secrets; print(secrets.token_urlsafe(32))'"
    )


# =============================================================================
# Configuración de Entorno
# =============================================================================

# Detectar si estamos en producción
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT.lower() == "production"

# Modo debug (NUNCA debe estar en True en producción)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


# =============================================================================
# Función de Validación
# =============================================================================

def validate_production_config() -> None:
    """
    Valida que la configuración sea segura para el entorno de producción.

    Raises:
        RuntimeError: Si la configuración no es segura para producción
    """
    if not IS_PRODUCTION:
        return  # Solo validar en producción

    errors = []

    # Validar SECRET_KEY
    if SECRET_KEY == "dev-secret-key-change-in-production":
        errors.append(
            "Cannot run in production with default SECRET_KEY! "
            "Set SECRET_KEY environment variable."
        )

    # Validar CORS
    if any("localhost" in origin for origin in CORS_ALLOWED_ORIGINS):
        errors.append(
            "Cannot run in production with localhost in ALLOWED_ORIGINS! "
            "Set ALLOWED_ORIGINS environment variable with production domains."
        )

    # Validar DEBUG
    if DEBUG:
        errors.append(
            "Cannot run in production with DEBUG=true! "
            "Debug mode exposes stack traces and internal errors. "
            "Set DEBUG=false or remove DEBUG environment variable."
        )

    # Si hay errores, fallar rápido
    if errors:
        error_msg = "Production configuration errors:\n" + "\n".join(f"  - {e}" for e in errors)
        raise RuntimeError(error_msg)