"""
Constantes del sistema AI-Native MVP

Centraliza todos los números mágicos y configuraciones hardcodeadas
para facilitar mantenimiento y prevenir errores.
"""

# =============================================================================
# Cache Configuration
# =============================================================================

# LRU Cache defaults
DEFAULT_CACHE_MAX_SIZE = 1000
"""Tamaño máximo del cache LRU (número de entradas)"""

DEFAULT_CACHE_TTL_SECONDS = 3600
"""Time-to-live por defecto para entradas de cache (1 hora)"""

CACHE_CLEANUP_INTERVAL_SECONDS = 300
"""Intervalo entre limpiezas automáticas del cache (5 minutos)"""

# =============================================================================
# Risk Analysis Thresholds
# =============================================================================

# AI Dependency thresholds
AI_DEPENDENCY_LOW_THRESHOLD = 0.3
"""Umbral bajo de dependencia de IA (30%)"""

AI_DEPENDENCY_MEDIUM_THRESHOLD = 0.6
"""Umbral medio de dependencia de IA (60%)"""

AI_DEPENDENCY_HIGH_THRESHOLD = 0.8
"""Umbral alto de dependencia de IA (80%)"""

# Interaction count thresholds
MIN_INTERACTIONS_FOR_RISK_ANALYSIS = 5
"""Mínimo de interacciones requeridas para análisis de riesgos significativo"""

CONSECUTIVE_HIGH_AI_THRESHOLD = 3
"""Número consecutivo de interacciones con alta dependencia que indica riesgo"""

# =============================================================================
# Input Validation
# =============================================================================

# Prompt validation
PROMPT_MIN_LENGTH = 10
"""Longitud mínima de un prompt del estudiante (caracteres)"""

PROMPT_MAX_LENGTH = 5000
"""Longitud máxima de un prompt del estudiante (caracteres)"""

CONTEXT_MAX_SIZE_BYTES = 10240
"""Tamaño máximo del contexto serializado (10KB)"""

SESSION_ID_MAX_LENGTH = 100
"""Longitud máxima del session_id"""

# =============================================================================
# Traceability Configuration
# =============================================================================

# N4 Trace limits
MAX_TRACE_SEQUENCE_LENGTH = 100
"""Longitud máxima de una secuencia de trazas"""

TRACE_CONTENT_MAX_LENGTH = 10000
"""Longitud máxima del contenido de una traza (caracteres)"""

# =============================================================================
# Cognitive Engine Configuration
# =============================================================================

# Confidence thresholds para clasificación cognitiva
COGNITIVE_STATE_MIN_CONFIDENCE = 0.6
"""Confianza mínima para asignar un estado cognitivo (60%)"""

COGNITIVE_TRANSITION_THRESHOLD = 0.7
"""Umbral de confianza para transición entre estados cognitivos (70%)"""

# =============================================================================
# Evaluation Configuration
# =============================================================================

# Competency level thresholds (scores 0-10)
COMPETENCY_BASICO_MAX_SCORE = 4.0
"""Score máximo para nivel BASICO (4.0/10)"""

COMPETENCY_INTERMEDIO_MAX_SCORE = 7.0
"""Score máximo para nivel INTERMEDIO (7.0/10)"""

COMPETENCY_AVANZADO_MIN_SCORE = 7.01
"""Score mínimo para nivel AVANZADO (7.01/10)"""

# =============================================================================
# API Configuration
# =============================================================================

# Request validation
MIN_PROMPT_LENGTH = 1
"""Longitud mínima de un prompt (caracteres)"""

MAX_PROMPT_LENGTH = 5000
"""Longitud máxima de un prompt (caracteres)"""

MAX_CONTEXT_SIZE_BYTES = 100 * 1024
"""Tamaño máximo del contexto (100KB)"""

MAX_TOTAL_REQUEST_SIZE_BYTES = 150 * 1024
"""Tamaño total máximo de un request (150KB)"""

# Pagination
DEFAULT_PAGE_SIZE = 20
"""Tamaño de página por defecto para paginación"""

MAX_PAGE_SIZE = 100
"""Tamaño máximo de página permitido"""

MIN_PAGE_SIZE = 1
"""Tamaño mínimo de página"""

# =============================================================================
# LLM Configuration
# =============================================================================

# Token limits
DEFAULT_MAX_TOKENS = 2000
"""Número máximo de tokens por defecto para respuestas LLM"""

MAX_TOKEN_LIMIT = 8000
"""Límite absoluto de tokens para prevenir costos excesivos"""

# Temperature ranges
MIN_TEMPERATURE = 0.0
"""Temperatura mínima (más determinista)"""

MAX_TEMPERATURE = 2.0
"""Temperatura máxima (más aleatorio)"""

DEFAULT_TEMPERATURE = 0.7
"""Temperatura por defecto (balance entre creatividad y coherencia)"""

# =============================================================================
# Session Configuration
# =============================================================================

# Timeouts
SESSION_INACTIVE_TIMEOUT_SECONDS = 3600
"""Timeout de inactividad de sesión (1 hora)"""

SESSION_MAX_DURATION_SECONDS = 10800
"""Duración máxima de una sesión (3 horas)"""

# =============================================================================
# Governance Configuration
# =============================================================================

# Blocking thresholds
GOVERNANCE_BLOCK_THRESHOLD_AI_DEPENDENCY = 0.9
"""Umbral de dependencia de IA para bloqueo automático (90%)"""

GOVERNANCE_BLOCK_CONSECUTIVE_DELEGATIONS = 5
"""Número consecutivo de delegaciones totales que activa bloqueo"""

# =============================================================================
# Datetime Utilities
# =============================================================================

from datetime import datetime, timezone


def utc_now() -> datetime:
    """
    Retorna el timestamp actual con timezone UTC.

    Reemplaza el uso de datetime.utcnow() (naive) con datetime.now(timezone.utc) (aware).

    Returns:
        datetime: Timestamp actual con timezone UTC

    Example:
        >>> now = utc_now()
        >>> now.tzinfo  # <UTC>
        >>> now.isoformat()  # '2025-11-21T10:30:00+00:00'
    """
    return datetime.now(timezone.utc)


# =============================================================================
# Helper Functions
# =============================================================================


def get_ai_dependency_level(ai_involvement: float) -> str:
    """
    Determina el nivel de dependencia de IA basado en el score.

    Args:
        ai_involvement: Score de involucramiento de IA (0.0 a 1.0)

    Returns:
        Nivel de dependencia: "LOW", "MEDIUM", "HIGH", "CRITICAL"
    """
    if ai_involvement < AI_DEPENDENCY_LOW_THRESHOLD:
        return "LOW"
    elif ai_involvement < AI_DEPENDENCY_MEDIUM_THRESHOLD:
        return "MEDIUM"
    elif ai_involvement < AI_DEPENDENCY_HIGH_THRESHOLD:
        return "HIGH"
    else:
        return "CRITICAL"


def is_competency_advanced(score: float) -> bool:
    """Verifica si un score corresponde a nivel AVANZADO"""
    return score >= COMPETENCY_AVANZADO_MIN_SCORE


def is_competency_intermediate(score: float) -> bool:
    """Verifica si un score corresponde a nivel INTERMEDIO"""
    return COMPETENCY_BASICO_MAX_SCORE < score <= COMPETENCY_INTERMEDIO_MAX_SCORE


def is_competency_basic(score: float) -> bool:
    """Verifica si un score corresponde a nivel BASICO"""
    return score <= COMPETENCY_BASICO_MAX_SCORE
