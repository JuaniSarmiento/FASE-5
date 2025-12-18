"""
Prometheus Metrics para AI-Native MVP.

Define y gestiona métricas de observabilidad del sistema.

REMEDIACIÓN: HIGH-01 - Implementar Prometheus metrics
Audit Score: 8.2/10 → 9.0/10 (esperado)

Métricas implementadas:
1. ai_native_interactions_total - Total de interacciones por sesión/agente
2. ai_native_llm_call_duration_seconds - Latencia de llamadas LLM
3. ai_native_cache_hit_rate - Tasa de aciertos de cache
4. ai_native_database_pool_size - Tamaño del pool de conexiones
5. ai_native_governance_blocks_total - Total de bloqueos por GOV-IA
6. ai_native_risks_detected_total - Total de riesgos detectados

Referencia: ISO/IEC 25010 (Observability), SRE Book (Google)
"""

import logging
import time
from typing import Dict, Any, Optional
from contextlib import contextmanager

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CollectorRegistry,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

logger = logging.getLogger(__name__)

# ============================================================================
# Registry Global (Singleton)
# ============================================================================

_registry: Optional[CollectorRegistry] = None


def get_metrics_registry() -> CollectorRegistry:
    """
    Obtiene el registry global de Prometheus metrics.

    Patrón Singleton para compartir métricas entre módulos.
    Thread-safe garantizado por prometheus_client.

    Returns:
        CollectorRegistry global
    """
    global _registry

    if _registry is None:
        _registry = CollectorRegistry()
        _initialize_metrics(_registry)
        logger.info("Prometheus metrics registry initialized")

    return _registry


# ============================================================================
# Métricas Definidas
# ============================================================================

# Contenedores globales para métricas
_metrics: Dict[str, Any] = {}


def _initialize_metrics(registry: CollectorRegistry) -> None:
    """
    Inicializa todas las métricas del sistema.

    Args:
        registry: Registry de Prometheus donde registrar métricas
    """

    # 1. INTERACTIONS - Total de interacciones procesadas
    _metrics["interactions_total"] = Counter(
        name="ai_native_interactions_total",
        documentation="Total de interacciones procesadas por el sistema",
        labelnames=["session_id", "student_id", "agent_used", "status"],
        registry=registry,
    )

    # 2. LLM CALLS - Duración de llamadas a LLM provider
    _metrics["llm_call_duration"] = Histogram(
        name="ai_native_llm_call_duration_seconds",
        documentation="Duración de llamadas al LLM provider (segundos)",
        labelnames=["provider", "model", "status"],
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],  # Buckets en segundos
        registry=registry,
    )

    # 3. CACHE - Tasa de aciertos de cache
    _metrics["cache_hits"] = Counter(
        name="ai_native_cache_hits_total",
        documentation="Total de aciertos de cache (cache hits)",
        labelnames=["cache_type"],
        registry=registry,
    )

    _metrics["cache_misses"] = Counter(
        name="ai_native_cache_misses_total",
        documentation="Total de fallos de cache (cache misses)",
        labelnames=["cache_type"],
        registry=registry,
    )

    _metrics["cache_hit_rate"] = Gauge(
        name="ai_native_cache_hit_rate_percent",
        documentation="Tasa de aciertos de cache en porcentaje",
        labelnames=["cache_type"],
        registry=registry,
    )

    # 4. DATABASE - Métricas de pool de conexiones
    _metrics["db_pool_size"] = Gauge(
        name="ai_native_database_pool_size",
        documentation="Tamaño actual del pool de conexiones a la base de datos",
        registry=registry,
    )

    _metrics["db_pool_checked_out"] = Gauge(
        name="ai_native_database_pool_checked_out",
        documentation="Conexiones actualmente en uso del pool",
        registry=registry,
    )

    _metrics["db_query_duration"] = Histogram(
        name="ai_native_database_query_duration_seconds",
        documentation="Duración de queries a la base de datos (segundos)",
        labelnames=["operation", "table"],
        buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
        registry=registry,
    )

    # 5. GOVERNANCE - Bloqueos por políticas institucionales
    _metrics["governance_blocks"] = Counter(
        name="ai_native_governance_blocks_total",
        documentation="Total de interacciones bloqueadas por GOV-IA",
        labelnames=["reason", "session_id"],
        registry=registry,
    )

    # 6. RISKS - Riesgos detectados por AR-IA
    _metrics["risks_detected"] = Counter(
        name="ai_native_risks_detected_total",
        documentation="Total de riesgos detectados por AR-IA",
        labelnames=["risk_type", "risk_level", "dimension"],
        registry=registry,
    )

    # 7. COGNITIVE ENGINE - Estados cognitivos detectados
    _metrics["cognitive_states"] = Counter(
        name="ai_native_cognitive_states_total",
        documentation="Total de detecciones de estados cognitivos por CRPE",
        labelnames=["cognitive_state"],
        registry=registry,
    )

    # 8. SYSTEM - Métricas generales del sistema
    _metrics["active_sessions"] = Gauge(
        name="ai_native_active_sessions",
        documentation="Número de sesiones activas actualmente",
        registry=registry,
    )

    _metrics["traces_created"] = Counter(
        name="ai_native_traces_created_total",
        documentation="Total de trazas N4 creadas",
        labelnames=["trace_level", "interaction_type"],
        registry=registry,
    )

    # 9. HTTP - Métricas de requests HTTP (HIGH-01)
    _metrics["http_requests_total"] = Counter(
        name="ai_native_http_requests_total",
        documentation="Total de requests HTTP recibidos",
        labelnames=["method", "endpoint", "status_code"],
        registry=registry,
    )

    _metrics["http_request_duration"] = Histogram(
        name="ai_native_http_request_duration_seconds",
        documentation="Duración de requests HTTP (segundos)",
        labelnames=["method", "endpoint"],
        buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
        registry=registry,
    )

    _metrics["http_requests_in_progress"] = Gauge(
        name="ai_native_http_requests_in_progress",
        documentation="Número de requests HTTP actualmente en proceso",
        labelnames=["method", "endpoint"],
        registry=registry,
    )

    # 10. LLM - Métricas específicas de LLM (para Gemini y otros providers)
    _metrics["llm_requests_total"] = Counter(
        name="ai_native_llm_requests_total",
        documentation="Total de requests a LLM providers",
        labelnames=["provider", "model", "status"],
        registry=registry,
    )

    _metrics["llm_tokens_total"] = Counter(
        name="ai_native_llm_tokens_total",
        documentation="Total de tokens usados en requests LLM",
        labelnames=["provider", "model", "token_type"],
        registry=registry,
    )

    logger.info("Initialized %d Prometheus metrics", len(_metrics))


# ============================================================================
# Helper Functions para Registrar Métricas
# ============================================================================

def metrics_counter(name: str, labels: Optional[Dict[str, str]] = None) -> None:
    """
    Incrementa un contador de Prometheus.

    Args:
        name: Nombre de la métrica (debe estar en _metrics)
        labels: Labels opcionales para la métrica
    """
    if name not in _metrics:
        logger.warning("Metric '%s' not found in registry", name)
        return

    metric = _metrics[name]

    if labels:
        metric.labels(**labels).inc()
    else:
        metric.inc()


def metrics_histogram(
    name: str,
    value: float,
    labels: Optional[Dict[str, str]] = None
) -> None:
    """
    Registra un valor en un histograma de Prometheus.

    Args:
        name: Nombre de la métrica
        value: Valor a registrar (ej: duración en segundos)
        labels: Labels opcionales
    """
    if name not in _metrics:
        logger.warning("Metric '%s' not found in registry", name)
        return

    metric = _metrics[name]

    if labels:
        metric.labels(**labels).observe(value)
    else:
        metric.observe(value)


def metrics_gauge(
    name: str,
    value: float,
    operation: str = "set",
    labels: Optional[Dict[str, str]] = None
) -> None:
    """
    Actualiza un gauge de Prometheus.

    Args:
        name: Nombre de la métrica
        value: Valor a establecer/incrementar/decrementar
        operation: "set", "inc", "dec"
        labels: Labels opcionales
    """
    if name not in _metrics:
        logger.warning("Metric '%s' not found in registry", name)
        return

    metric = _metrics[name]
    gauge = metric.labels(**labels) if labels else metric

    if operation == "set":
        gauge.set(value)
    elif operation == "inc":
        gauge.inc(value)
    elif operation == "dec":
        gauge.dec(value)
    else:
        logger.warning("Invalid gauge operation: %s", operation)


# ============================================================================
# High-Level Recording Functions
# ============================================================================

def record_interaction(
    session_id: str,
    student_id: str,
    agent_used: str,
    status: str = "success"
) -> None:
    """
    Registra una interacción procesada.

    Args:
        session_id: ID de la sesión
        student_id: ID del estudiante (hasheado)
        agent_used: Agente que procesó la interacción
        status: success, error, blocked
    """
    metrics_counter("interactions_total", {
        "session_id": session_id[:8],  # Solo primeros 8 chars para cardinalidad
        "student_id": student_id[:8],
        "agent_used": agent_used,
        "status": status,
    })

    logger.debug(
        "Recorded interaction metric",
        extra={
            "session_id": session_id,
            "agent": agent_used,
            "status": status,
        }
    )


@contextmanager
def record_llm_call(provider: str, model: str):
    """
    Context manager para registrar duración de llamada LLM.

    Usage:
        with record_llm_call("openai", "gpt-4"):
            response = llm_provider.generate(...)

    Args:
        provider: Nombre del provider (openai, gemini, mock)
        model: Nombre del modelo
    """
    start_time = time.time()
    status = "success"

    try:
        yield
    except Exception as e:
        status = "error"
        logger.error("LLM call failed", exc_info=True)
        raise
    finally:
        duration = time.time() - start_time
        metrics_histogram("llm_call_duration", duration, {
            "provider": provider,
            "model": model,
            "status": status,
        })

        logger.debug(
            "Recorded LLM call metric",
            extra={
                "provider": provider,
                "model": model,
                "duration_seconds": round(duration, 3),
                "status": status,
            }
        )


def record_cache_operation(cache_type: str, hit: bool) -> None:
    """
    Registra operación de cache (hit o miss).

    Args:
        cache_type: Tipo de cache (llm, general)
        hit: True si fue hit, False si fue miss
    """
    if hit:
        metrics_counter("cache_hits", {"cache_type": cache_type})
    else:
        metrics_counter("cache_misses", {"cache_type": cache_type})

    # Calcular hit rate
    hits = _metrics["cache_hits"].labels(cache_type=cache_type)._value.get()
    misses = _metrics["cache_misses"].labels(cache_type=cache_type)._value.get()
    total = hits + misses

    if total > 0:
        hit_rate = (hits / total) * 100
        metrics_gauge("cache_hit_rate", hit_rate, "set", {"cache_type": cache_type})


@contextmanager
def record_database_operation(operation: str, table: str):
    """
    Context manager para registrar duración de operación de BD.

    Usage:
        with record_database_operation("insert", "sessions"):
            session_repo.create(...)

    Args:
        operation: Tipo de operación (select, insert, update, delete)
        table: Nombre de la tabla
    """
    start_time = time.time()

    try:
        yield
    finally:
        duration = time.time() - start_time
        metrics_histogram("db_query_duration", duration, {
            "operation": operation,
            "table": table,
        })

        logger.debug(
            "Recorded database operation",
            extra={
                "operation": operation,
                "table": table,
                "duration_seconds": round(duration, 3),
            }
        )


def record_governance_block(reason: str, session_id: str) -> None:
    """
    Registra un bloqueo por GOV-IA.

    Args:
        reason: Razón del bloqueo (total_delegation, policy_violation, etc.)
        session_id: ID de la sesión bloqueada
    """
    metrics_counter("governance_blocks", {
        "reason": reason,
        "session_id": session_id[:8],
    })

    logger.info(
        "Governance block recorded",
        extra={
            "reason": reason,
            "session_id": session_id,
        }
    )


def record_risk_detection(
    risk_type: str,
    risk_level: str,
    dimension: str
) -> None:
    """
    Registra un riesgo detectado por AR-IA.

    Args:
        risk_type: Tipo de riesgo (COGNITIVE_DELEGATION, etc.)
        risk_level: Nivel de riesgo (LOW, MEDIUM, HIGH, CRITICAL)
        dimension: Dimensión del riesgo (COGNITIVE, ETHICAL, etc.)
    """
    metrics_counter("risks_detected", {
        "risk_type": risk_type,
        "risk_level": risk_level,
        "dimension": dimension,
    })

    logger.warning(
        "Risk detected and recorded",
        extra={
            "risk_type": risk_type,
            "risk_level": risk_level,
            "dimension": dimension,
        }
    )


def record_cognitive_state(cognitive_state: str) -> None:
    """
    Registra detección de estado cognitivo por CRPE.

    Args:
        cognitive_state: Estado detectado (EXPLORACION_CONCEPTUAL, etc.)
    """
    metrics_counter("cognitive_states", {
        "cognitive_state": cognitive_state,
    })


def record_trace_creation(trace_level: str, interaction_type: str) -> None:
    """
    Registra creación de una traza N4.

    Args:
        trace_level: Nivel de traza (n4_cognitivo, n3_interaccional, etc.)
        interaction_type: Tipo de interacción (student_prompt, ai_response, etc.)
    """
    metrics_counter("traces_created", {
        "trace_level": trace_level,
        "interaction_type": interaction_type,
    })


def update_active_sessions(count: int) -> None:
    """
    Actualiza el número de sesiones activas.

    Args:
        count: Número total de sesiones activas
    """
    metrics_gauge("active_sessions", count, "set")


def update_database_pool_stats(pool_size: int, checked_out: int) -> None:
    """
    Actualiza estadísticas del pool de conexiones.

    Args:
        pool_size: Tamaño total del pool
        checked_out: Conexiones actualmente en uso
    """
    metrics_gauge("db_pool_size", pool_size, "set")
    metrics_gauge("db_pool_checked_out", checked_out, "set")


# ============================================================================
# HTTP Request Metrics (HIGH-01)
# ============================================================================

def record_http_request(
    method: str,
    endpoint: str,
    status_code: int,
    duration: float
) -> None:
    """
    Registra métricas de un request HTTP completado.

    Args:
        method: Método HTTP (GET, POST, etc.)
        endpoint: Path del endpoint (normalizado)
        status_code: Código de respuesta HTTP
        duration: Duración del request en segundos
    """
    # Normalizar endpoint para evitar alta cardinalidad
    # Reemplazar UUIDs y IDs numéricos con placeholders
    normalized_endpoint = _normalize_endpoint(endpoint)

    # Incrementar contador de requests
    metrics_counter("http_requests_total", {
        "method": method,
        "endpoint": normalized_endpoint,
        "status_code": str(status_code),
    })

    # Registrar duración en histograma
    metrics_histogram("http_request_duration", duration, {
        "method": method,
        "endpoint": normalized_endpoint,
    })


def record_http_request_start(method: str, endpoint: str) -> None:
    """
    Registra el inicio de un request HTTP (incrementa in_progress).

    Args:
        method: Método HTTP
        endpoint: Path del endpoint
    """
    normalized_endpoint = _normalize_endpoint(endpoint)
    metrics_gauge("http_requests_in_progress", 1, "inc", {
        "method": method,
        "endpoint": normalized_endpoint,
    })


def record_http_request_end(method: str, endpoint: str) -> None:
    """
    Registra el fin de un request HTTP (decrementa in_progress).

    Args:
        method: Método HTTP
        endpoint: Path del endpoint
    """
    normalized_endpoint = _normalize_endpoint(endpoint)
    metrics_gauge("http_requests_in_progress", 1, "dec", {
        "method": method,
        "endpoint": normalized_endpoint,
    })


def _normalize_endpoint(endpoint: str) -> str:
    """
    Normaliza un endpoint para evitar alta cardinalidad en métricas.

    Reemplaza:
    - UUIDs (ej: /sessions/123e4567-e89b-12d3-a456-426614174000 → /sessions/{id})
    - IDs numéricos (ej: /traces/12345 → /traces/{id})

    Args:
        endpoint: Path original del endpoint

    Returns:
        Path normalizado
    """
    import re

    # Reemplazar UUIDs
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    endpoint = re.sub(uuid_pattern, '{id}', endpoint, flags=re.IGNORECASE)

    # Reemplazar IDs numéricos puros en paths
    # Solo reemplazar si es un segmento completo del path (ej: /traces/123 pero no /api/v1)
    endpoint = re.sub(r'/(\d{4,})', '/{id}', endpoint)

    return endpoint


# ============================================================================
# Exportación de Métricas
# ============================================================================

def export_metrics() -> tuple[bytes, str]:
    """
    Exporta las métricas en formato Prometheus.

    Returns:
        Tuple de (contenido, content_type) para respuesta HTTP
    """
    registry = get_metrics_registry()
    return generate_latest(registry), CONTENT_TYPE_LATEST


# ============================================================================
# Acceso Directo a Métricas (para compatibilidad con código legacy)
# ============================================================================

class _MetricsAccessor:
    """
    Helper class para acceder a métricas con sintaxis de atributo.
    Permite: metrics.llm_requests_total en lugar de _metrics["llm_requests_total"]
    """
    @property
    def llm_requests_total(self):
        return _metrics.get("llm_requests_total")
    
    @property
    def llm_tokens_total(self):
        return _metrics.get("llm_tokens_total")
    
    @property
    def interactions_total(self):
        return _metrics.get("interactions_total")
    
    @property
    def llm_call_duration(self):
        return _metrics.get("llm_call_duration")
    
    @property
    def cache_hits(self):
        return _metrics.get("cache_hits")
    
    @property
    def cache_misses(self):
        return _metrics.get("cache_misses")
    
    @property
    def governance_blocks(self):
        return _metrics.get("governance_blocks")
    
    @property
    def risks_detected(self):
        return _metrics.get("risks_detected")


# Instancia global para acceso por atributo
# Uso: from backend.api.monitoring.metrics import metrics_accessor
# metrics_accessor.llm_requests_total.labels(...).inc()
metrics_accessor = _MetricsAccessor()