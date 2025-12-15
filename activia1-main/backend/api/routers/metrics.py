"""
Endpoint de Prometheus Metrics.

Expone métricas de observabilidad para scraping de Prometheus.

REMEDIACIÓN: HIGH-01 - Implementar Prometheus metrics
Audit Score: 8.2/10 → 9.0/10 (esperado)

Endpoint:
- GET /metrics - Métricas en formato Prometheus

Referencias:
- Prometheus Exposition Formats: https://prometheus.io/docs/instrumenting/exposition_formats/
- FastAPI + Prometheus: https://github.com/trallnag/prometheus-fastapi-instrumentator
"""

import logging
from fastapi import APIRouter, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from ...core.metrics import (
    interactions_total,
    sessions_active,
    llm_requests_total,
    cache_hits,
    cache_misses
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Monitoring"])


@router.get(
    "/metrics",
    summary="Prometheus Metrics",
    description="""
    Expone métricas del sistema en formato Prometheus.

    Este endpoint debe ser scrapeado por Prometheus cada 15-30 segundos.

    **Métricas disponibles**:
    - `ai_native_interactions_total` - Total de interacciones procesadas
    - `ai_native_llm_call_duration_seconds` - Latencia de llamadas LLM
    - `ai_native_cache_hit_rate_percent` - Tasa de aciertos de cache
    - `ai_native_database_pool_size` - Tamaño del pool de conexiones
    - `ai_native_governance_blocks_total` - Total de bloqueos por GOV-IA
    - `ai_native_risks_detected_total` - Total de riesgos detectados
    - `ai_native_cognitive_states_total` - Estados cognitivos detectados
    - `ai_native_active_sessions` - Sesiones activas actualmente
    - `ai_native_traces_created_total` - Total de trazas N4 creadas

    **Configuración de Prometheus**:
    ```yaml
    scrape_configs:
      - job_name: 'ai-native-mvp'
        scrape_interval: 15s
        static_configs:
          - targets: ['localhost:8000']
    ```

    **Alertas recomendadas**:
    - High LLM latency (> 10s)
    - Low cache hit rate (< 50%)
    - High risk detection rate
    - Database pool saturation
    """,
    response_class=Response,
    responses={
        200: {
            "description": "Métricas en formato Prometheus",
            "content": {
                "text/plain": {
                    "example": """# HELP ai_native_interactions_total Total de interacciones procesadas
# TYPE ai_native_interactions_total counter
ai_native_interactions_total{agent_used="T-IA-Cog",session_id="abc123",status="success",student_id="def456"} 42.0

# HELP ai_native_llm_call_duration_seconds Duración de llamadas al LLM provider
# TYPE ai_native_llm_call_duration_seconds histogram
ai_native_llm_call_duration_seconds_bucket{le="0.1",model="gpt-4",provider="openai",status="success"} 0.0
ai_native_llm_call_duration_seconds_bucket{le="0.5",model="gpt-4",provider="openai",status="success"} 3.0
ai_native_llm_call_duration_seconds_sum{model="gpt-4",provider="openai",status="success"} 4.2
ai_native_llm_call_duration_seconds_count{model="gpt-4",provider="openai",status="success"} 5.0
"""
                }
            }
        }
    }
)
async def get_metrics() -> Response:
    """
    Expone métricas de Prometheus para scraping.

    Returns:
        Response con métricas en formato text/plain
    """
    try:
        metrics_output = generate_latest()
        
        logger.debug("Exported Prometheus metrics", extra={"size_bytes": len(metrics_output)})

        return Response(
            content=metrics_output,
            media_type=CONTENT_TYPE_LATEST,
        )

    except Exception as e:
        # FIX Cortez20: Removed unreachable code after return
        logger.error(f"Error exporting metrics: {e}", exc_info=True)
        return Response(
            content="# Error exporting metrics\n",
            media_type="text/plain",
            status_code=500
        )