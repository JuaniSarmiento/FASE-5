"""
Módulo de Monitoring y Métricas.

Proporciona observabilidad del sistema mediante Prometheus metrics.

HIGH-01 Implementation (2025-11-25):
- Métricas de interacciones (interactions_total, governance_blocks)
- Métricas de LLM (llm_call_duration_seconds)
- Métricas de cache (cache_hits, cache_misses, cache_hit_rate)
- Métricas de riesgos (risks_detected_total)
- Métricas de trazas (traces_created_total)
- Métricas HTTP (http_requests_total, http_request_duration_seconds)
"""

from .metrics import (
    # Registry
    get_metrics_registry,
    # Low-level metric operations
    metrics_counter,
    metrics_histogram,
    metrics_gauge,
    # Business metrics
    record_interaction,
    record_llm_call,
    record_cache_operation,
    record_database_operation,
    record_governance_block,
    record_risk_detection,
    record_cognitive_state,
    record_trace_creation,
    update_active_sessions,
    update_database_pool_stats,
    # HTTP metrics (HIGH-01)
    record_http_request,
    record_http_request_start,
    record_http_request_end,
    # Export
    export_metrics,
)

__all__ = [
    # Registry
    "get_metrics_registry",
    # Low-level metric operations
    "metrics_counter",
    "metrics_histogram",
    "metrics_gauge",
    # Business metrics
    "record_interaction",
    "record_llm_call",
    "record_cache_operation",
    "record_database_operation",
    "record_governance_block",
    "record_risk_detection",
    "record_cognitive_state",
    "record_trace_creation",
    "update_active_sessions",
    "update_database_pool_stats",
    # HTTP metrics (HIGH-01)
    "record_http_request",
    "record_http_request_start",
    "record_http_request_end",
    # Export
    "export_metrics",
]
