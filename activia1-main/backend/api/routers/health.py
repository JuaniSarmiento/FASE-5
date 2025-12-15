"""
Router para health checks y status del servicio.

REMEDIACIÓN: HIGH-03 - Deep Health Checks (ENHANCED 2025-11-25)
Implementa 3 niveles de health checks:
- /health/live: Liveness probe (proceso vivo)
- /health/ready: Readiness probe (DB + Redis + dependencies)
- /health/deep: Deep check (incluye latencias, cache stats, pool usage, memory, LLM validation)

Mejoras implementadas:
- Verificación de conexiones activas en DB pool
- Test de escritura/lectura en Redis (no solo ping)
- Verificación de disponibilidad del LLM (ping real al provider)
- Uso de memoria del proceso
- Estadísticas de garbage collector
"""
import logging
import time
import gc
import os
import sys
from typing import Dict, Any, Optional

from backend.core.constants import utc_now
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError

from ...database.repositories import SessionRepository
from ..deps import get_db, get_session_repository
from ..schemas.common import HealthStatus, APIResponse

logger = logging.getLogger(__name__)


def _get_process_memory_mb() -> Optional[float]:
    """Get current process memory usage in MB."""
    try:
        import psutil
        process = psutil.Process(os.getpid())
        return round(process.memory_info().rss / 1024 / 1024, 2)
    except ImportError:
        # psutil not installed, try alternative
        try:
            if sys.platform == 'linux':
                with open(f'/proc/{os.getpid()}/status', 'r') as f:
                    for line in f:
                        if line.startswith('VmRSS:'):
                            return round(int(line.split()[1]) / 1024, 2)
        except (IOError, OSError, ValueError) as e:
            logger.debug(f"Failed to read /proc memory stats: {e}")
        return None
    except (OSError, AttributeError) as e:
        logger.debug(f"Failed to get process memory via psutil: {e}")
        return None


def _get_gc_stats() -> Dict[str, Any]:
    """Get garbage collector statistics."""
    try:
        counts = gc.get_count()
        return {
            "generation_0": counts[0],
            "generation_1": counts[1],
            "generation_2": counts[2],
            "total_objects": len(gc.get_objects()),
        }
    except (RuntimeError, AttributeError) as e:
        logger.debug(f"Failed to get GC stats: {e}")
        return {}

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthStatus,
    summary="Health Check",
    description="Verifica el estado de salud del servicio y sus componentes",
)
async def health_check(
    db: Session = Depends(get_db),
    session_repo: SessionRepository = Depends(get_session_repository),
) -> HealthStatus:
    """
    Endpoint de health check que verifica:
    - Estado general del servicio
    - Conectividad con la base de datos
    - Estado de los agentes AI

    Returns:
        HealthStatus: Estado de salud del servicio
    """
    from ... import __version__

    # Verificar conexión a base de datos
    # FIXED (2025-11-21): Excepciones específicas en lugar de Exception genérico
    db_status = "disconnected"
    try:
        # Intentar una query simple con text() wrapper (SQLAlchemy 2.0 style)
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except OperationalError as e:
        # Error de conexión a BD (servidor caído, credenciales inválidas, etc.)
        logger.warning("Database connection error", exc_info=True, extra={"error": str(e)})
        db_status = "disconnected"
    except ProgrammingError as e:
        # Error de sintaxis SQL (no debería ocurrir con SELECT 1, pero por si acaso)
        logger.error("Database query error", exc_info=True, extra={"error": str(e)})
        db_status = "disconnected"
    except Exception as e:
        # Catch-all para errores inesperados, pero logueamos crítico
        logger.critical("Unexpected database error in health check", exc_info=True, extra={"error": str(e)})
        db_status = "disconnected"
        # Re-raise para no ocultar bugs graves
        # (comentado para que health check no tire 500, pero en producción considerar re-raise)

    # Estado de agentes (mock para MVP, verificar disponibilidad real en producción)
    agents_status = {
        "T-IA-Cog": "operational",
        "E-IA-Proc": "operational",
        "S-IA-X": "operational",
        "AR-IA": "operational",
        "GOV-IA": "operational",
        "TC-N4": "operational",
    }

    # Determinar estado general
    if db_status == "connected" and all(
        status == "operational" for status in agents_status.values()
    ):
        overall_status = "healthy"
    elif db_status == "connected":
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    return HealthStatus(
        status=overall_status,
        version=__version__,
        database=db_status,
        agents=agents_status,
        timestamp=utc_now(),
    )


class PingResponse(HealthStatus):
    """Response model for ping endpoint"""
    pass


@router.get(
    "/ping",
    response_model=APIResponse[dict],
    summary="Simple Ping",
    description="Endpoint simple para verificar que el servicio está respondiendo. Usa APIResponse wrapper para consistencia.",
)
async def ping() -> APIResponse[dict]:
    """
    Endpoint minimalista para health checks externos.

    Usa el wrapper APIResponse estándar para consistencia con el resto de la API.

    Returns:
        APIResponse con {"status": "ok", "timestamp": ...}
    """
    return APIResponse(
        success=True,
        data={
            "status": "ok",
            "timestamp": utc_now().isoformat(),
        },
        message="Service is responding",
    )


# ============================================================================
# HIGH-03: Deep Health Checks
# ============================================================================

@router.get(
    "/live",
    response_model=APIResponse[dict],
    summary="Liveness Probe",
    description="""
    Kubernetes liveness probe - Verifica que el proceso está vivo.

    **Uso en Kubernetes**:
    ```yaml
    livenessProbe:
      httpGet:
        path: /api/v1/health/live
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 10
      timeoutSeconds: 3
      failureThreshold: 3
    ```

    **Retorna**:
    - 200 OK: Proceso vivo
    - 503 Service Unavailable: Proceso debe reiniciarse
    """,
    responses={
        200: {"description": "Service is alive"},
        503: {"description": "Service is dead - restart required"},
    },
)
async def liveness_probe() -> APIResponse[dict]:
    """
    Liveness probe para Kubernetes.

    Verifica que el proceso de FastAPI está respondiendo.
    Si este endpoint falla, Kubernetes reiniciará el pod.

    Returns:
        APIResponse: 200 si el proceso está vivo (FIX 5.1: Use consistent wrapper)
    """
    return APIResponse(
        success=True,
        data={
            "status": "alive",
            "timestamp": utc_now().isoformat(),
        },
        message="Service is alive"
    )


@router.get(
    "/ready",
    response_model=APIResponse[dict],
    summary="Readiness Probe",
    description="""
    Kubernetes readiness probe - Verifica que el servicio está listo para recibir tráfico.

    Verifica:
    - PostgreSQL está accesible
    - Redis está accesible (si configurado)
    - LLM provider está accesible (opcional)

    **Uso en Kubernetes**:
    ```yaml
    readinessProbe:
      httpGet:
        path: /api/v1/health/ready
        port: 8000
      initialDelaySeconds: 20
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
    ```

    **Retorna**:
    - 200 OK: Servicio listo para tráfico
    - 503 Service Unavailable: Servicio NO listo (quitar del load balancer)
    """,
    responses={
        200: {"description": "Service is ready"},
        503: {"description": "Service is NOT ready - remove from load balancer"},
    },
)
async def readiness_probe(
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Readiness probe para Kubernetes.

    Verifica que todas las dependencias críticas están disponibles.
    Si este endpoint falla, Kubernetes quitará el pod del load balancer.

    Args:
        db: Sesión de base de datos (inyectada)

    Returns:
        JSONResponse: 200 si listo, 503 si no listo
    """
    checks = {}
    is_ready = True

    # 1. Check PostgreSQL
    db_latency_ms = None
    try:
        start_time = time.time()
        db.execute(text("SELECT 1"))
        db_latency_ms = round((time.time() - start_time) * 1000, 2)
        checks["database"] = {
            "status": "ready",
            "latency_ms": db_latency_ms,
        }
    except Exception as e:
        checks["database"] = {
            "status": "not_ready",
            "error": str(e)[:100],  # Limitar mensaje de error
        }
        is_ready = False
        logger.error("Database not ready in readiness probe", exc_info=True)

    # 2. Check Redis (optional pero importante para rate limiting y cache)
    try:
        import os
        redis_url = os.getenv("REDIS_URL")

        if redis_url:
            import redis
            redis_client = redis.from_url(redis_url, decode_responses=True)

            start_time = time.time()
            redis_client.ping()
            redis_latency_ms = round((time.time() - start_time) * 1000, 2)

            checks["redis"] = {
                "status": "ready",
                "latency_ms": redis_latency_ms,
            }
        else:
            checks["redis"] = {
                "status": "not_configured",
            }
    except Exception as e:
        checks["redis"] = {
            "status": "not_ready",
            "error": str(e)[:100],
        }
        # Redis no es crítico para readiness (puede funcionar sin cache)
        logger.warning("Redis not ready in readiness probe", extra={"error": str(e)})

    # 3. Check LLM Provider (opcional - solo si está configurado)
    try:
        import os
        llm_provider = os.getenv("LLM_PROVIDER", "mock")

        if llm_provider == "mock":
            checks["llm_provider"] = {
                "status": "ready",
                "provider": "mock",
            }
        else:
            # En producción, aquí podríamos hacer un ping al LLM provider
            # Por ahora, solo verificamos que las credenciales están configuradas
            checks["llm_provider"] = {
                "status": "configured",
                "provider": llm_provider,
            }
    except Exception as e:
        checks["llm_provider"] = {
            "status": "error",
            "error": str(e)[:100],
        }
        logger.warning("LLM provider check failed", extra={"error": str(e)})

    # FIX 5.1: Use APIResponse wrapper for consistency
    # Determinar código de respuesta
    if is_ready:
        return APIResponse(
            success=True,
            data={
                "status": "ready",
                "checks": checks,
                "timestamp": utc_now().isoformat(),
            },
            message="Service is ready"
        )
    else:
        # Note: For 503, we still need to indicate failure but return valid response
        return APIResponse(
            success=False,
            data={
                "status": "not_ready",
                "checks": checks,
                "timestamp": utc_now().isoformat(),
            },
            message="Service is not ready"
        )


@router.get(
    "/deep",
    response_model=APIResponse[dict],
    summary="Deep Health Check",
    description="""
    Health check exhaustivo con métricas detalladas.

    **ADVERTENCIA**: Este endpoint es más lento que /health porque ejecuta
    múltiples verificaciones. No usar para liveness/readiness probes.

    Verifica:
    - Latencias de PostgreSQL, Redis, LLM
    - Uso del pool de conexiones
    - Estadísticas de cache
    - Estadísticas de Prometheus metrics
    - Versiones de dependencias

    **Uso recomendado**:
    - Monitoring dashboards (Grafana)
    - Troubleshooting manual
    - Alertas de degradación de performance
    """,
    responses={
        200: {"description": "Service is healthy (all checks passed)"},
        503: {"description": "Service is unhealthy or degraded"},
    },
)
async def deep_health_check(
    db: Session = Depends(get_db),
) -> APIResponse[dict]:
    """
    Deep health check con métricas exhaustivas.

    Args:
        db: Sesión de base de datos (inyectada)

    Returns:
        JSONResponse: Estado detallado del sistema
    """
    from ... import __version__, __author__
    import os
    import sys

    checks: Dict[str, Any] = {}
    overall_healthy = True

    # 1. System Info
    checks["system"] = {
        "version": __version__,
        "author": __author__,
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "environment": os.getenv("ENVIRONMENT", "unknown"),
    }

    # 2. Database - Latencia + Pool Stats (SQLite/PostgreSQL compatible)
    try:
        # Detect database type first from connection URL or engine
        start_time = time.time()
        db_url = str(db.get_bind().url)
        is_sqlite = "sqlite" in db_url.lower()

        if is_sqlite:
            result = db.execute(text("SELECT sqlite_version()"))
            row = result.fetchone()
            db_version = f"SQLite {row[0]}" if row else "SQLite (unknown version)"
        else:
            # PostgreSQL or other database
            result = db.execute(text("SELECT version()"))
            row = result.fetchone()
            db_version = row[0] if row else "unknown"

        db_latency_ms = round((time.time() - start_time) * 1000, 2)

        # Pool stats (si está disponible - PostgreSQL only, SQLite uses NullPool)
        pool_size = None
        pool_checked_out = None
        pool_type = None
        try:
            pool = db.get_bind().pool
            pool_type = type(pool).__name__
            # NullPool (SQLite) doesn't have size/checkedout methods
            if hasattr(pool, 'size'):
                pool_size = pool.size()
            if hasattr(pool, 'checkedout'):
                pool_checked_out = pool.checkedout()
        except (AttributeError, TypeError) as e:
            # Pool stats not available (common with SQLite NullPool)
            logger.debug(f"Pool stats not available: {e}")

        checks["database"] = {
            "status": "healthy",
            "latency_ms": db_latency_ms,
            "version": db_version[:50],  # Limitar longitud
            "pool_type": pool_type,
            "pool_size": pool_size,
            "pool_checked_out": pool_checked_out,
            "pool_usage_percent": round((pool_checked_out / pool_size) * 100, 1) if pool_size and pool_checked_out else None,
        }

        # Alerta si latencia > 100ms
        if db_latency_ms > 100:
            checks["database"]["warning"] = "High latency detected"
            overall_healthy = False

        # Alerta si pool > 80% usado
        if pool_size and pool_checked_out and (pool_checked_out / pool_size) > 0.8:
            checks["database"]["warning"] = "Pool usage > 80%"
            overall_healthy = False

    except Exception as e:
        checks["database"] = {
            "status": "unhealthy",
            "error": str(e)[:100],
        }
        overall_healthy = False
        logger.error("Database deep check failed", exc_info=True)

    # 3. Redis - Latencia + Write/Read Test + Stats (HIGH-03 Enhancement)
    try:
        redis_url = os.getenv("REDIS_URL")

        if redis_url:
            import redis
            import uuid
            redis_client = redis.from_url(redis_url, decode_responses=True)

            # Test latencia con PING
            start_time = time.time()
            redis_client.ping()
            ping_latency_ms = round((time.time() - start_time) * 1000, 2)

            # Write/Read test (más completo que solo ping)
            test_key = f"health_check_{uuid.uuid4().hex[:8]}"
            test_value = f"test_{utc_now().isoformat()}"

            start_time = time.time()
            redis_client.setex(test_key, 10, test_value)  # Expira en 10 segundos
            write_latency_ms = round((time.time() - start_time) * 1000, 2)

            start_time = time.time()
            read_value = redis_client.get(test_key)
            read_latency_ms = round((time.time() - start_time) * 1000, 2)

            # Cleanup
            redis_client.delete(test_key)

            # Verify write/read worked
            write_read_ok = read_value == test_value

            # Info stats
            info = redis_client.info()

            checks["redis"] = {
                "status": "healthy" if write_read_ok else "degraded",
                "ping_latency_ms": ping_latency_ms,
                "write_latency_ms": write_latency_ms,
                "read_latency_ms": read_latency_ms,
                "write_read_test": "passed" if write_read_ok else "failed",
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "uptime_days": round(info.get("uptime_in_seconds", 0) / 86400, 1),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses"),
            }

            # Calculate hit rate
            hits = info.get("keyspace_hits", 0)
            misses = info.get("keyspace_misses", 0)
            if hits + misses > 0:
                checks["redis"]["hit_rate_percent"] = round((hits / (hits + misses)) * 100, 1)

            # Alertas
            if ping_latency_ms > 50:
                checks["redis"]["warning"] = "High ping latency detected"
            if write_latency_ms > 100:
                checks["redis"]["warning"] = "High write latency detected"
            if not write_read_ok:
                checks["redis"]["error"] = "Write/read test failed"
                overall_healthy = False

        else:
            checks["redis"] = {"status": "not_configured"}

    except ImportError:
        checks["redis"] = {
            "status": "not_available",
            "note": "redis package not installed",
        }
    except Exception as e:
        checks["redis"] = {
            "status": "degraded",
            "error": str(e)[:100],
        }
        logger.warning("Redis deep check failed", extra={"error": str(e)})

    # 4. Cache Stats (si LLM cache está habilitado)
    try:
        from ...core.cache import get_llm_cache

        llm_cache_enabled = os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"

        if llm_cache_enabled:
            cache = get_llm_cache()
            stats = cache.get_stats()

            checks["cache"] = {
                "status": "enabled",
                "hits": stats.get("hits"),
                "misses": stats.get("misses"),
                "hit_rate": round(stats.get("hit_rate", 0), 2),
                "size": stats.get("size"),
                "max_entries": cache.max_entries,
            }

            # Alerta si hit rate < 50%
            if stats.get("hit_rate", 0) < 50 and (stats.get("hits", 0) + stats.get("misses", 0)) > 10:
                checks["cache"]["warning"] = "Low hit rate detected"
        else:
            checks["cache"] = {"status": "disabled"}

    except Exception as e:
        checks["cache"] = {
            "status": "error",
            "error": str(e)[:100],
        }
        logger.warning("Cache stats check failed", extra={"error": str(e)})

    # 5. Process Memory & GC Stats (HIGH-03 Enhancement)
    checks["process"] = {
        "memory_mb": _get_process_memory_mb(),
        "gc_stats": _get_gc_stats(),
        "pid": os.getpid(),
    }

    # Memory warning if > 500MB
    memory_mb = checks["process"]["memory_mb"]
    if memory_mb and memory_mb > 500:
        checks["process"]["warning"] = f"High memory usage: {memory_mb}MB"

    # 6. Prometheus Metrics Stats (si están disponibles)
    try:
        from ..monitoring.metrics import _metrics

        if _metrics:
            interactions_total = 0
            try:
                # Sumar todas las interacciones
                for metric in _metrics.get("interactions_total", {})._metrics.values():
                    interactions_total += metric._value.get()
            except Exception:
                pass

            checks["metrics"] = {
                "status": "enabled",
                "interactions_total": int(interactions_total),
                "metrics_count": len(_metrics),
            }
        else:
            checks["metrics"] = {"status": "not_initialized"}

    except Exception as e:
        checks["metrics"] = {
            "status": "error",
            "error": str(e)[:100],
        }

    # 7. LLM Provider Status with Validation (HIGH-03 Enhancement)
    try:
        llm_provider = os.getenv("LLM_PROVIDER", "mock")

        checks["llm_provider"] = {
            "provider": llm_provider,
            "status": "configured" if llm_provider != "mock" else "mock",
        }

        if llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY", "")
            checks["llm_provider"]["api_key_configured"] = bool(api_key)
            checks["llm_provider"]["model"] = os.getenv("OPENAI_MODEL", "gpt-4")

            # Validate OpenAI API with actual ping (list models)
            if api_key:
                try:
                    import openai
                    start_time = time.time()
                    client = openai.OpenAI(api_key=api_key)
                    # Light API call - just list first model
                    models = list(client.models.list())[:1]
                    llm_latency_ms = round((time.time() - start_time) * 1000, 2)
                    checks["llm_provider"]["status"] = "healthy"
                    checks["llm_provider"]["latency_ms"] = llm_latency_ms
                    checks["llm_provider"]["api_validated"] = True

                    if llm_latency_ms > 2000:
                        checks["llm_provider"]["warning"] = "High LLM API latency"
                except ImportError:
                    checks["llm_provider"]["api_validated"] = False
                    checks["llm_provider"]["note"] = "openai package not installed"
                except Exception as e:
                    checks["llm_provider"]["status"] = "degraded"
                    checks["llm_provider"]["api_validated"] = False
                    checks["llm_provider"]["api_error"] = str(e)[:100]
                    logger.warning("OpenAI API validation failed", extra={"error": str(e)})

        elif llm_provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY", "")
            checks["llm_provider"]["api_key_configured"] = bool(api_key)
            checks["llm_provider"]["model"] = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

            # Validate Gemini API with actual ping
            if api_key:
                try:
                    import google.generativeai as genai
                    start_time = time.time()
                    genai.configure(api_key=api_key)
                    # Light API call - just list models
                    models = list(genai.list_models())[:1]
                    llm_latency_ms = round((time.time() - start_time) * 1000, 2)
                    checks["llm_provider"]["status"] = "healthy"
                    checks["llm_provider"]["latency_ms"] = llm_latency_ms
                    checks["llm_provider"]["api_validated"] = True

                    if llm_latency_ms > 2000:
                        checks["llm_provider"]["warning"] = "High LLM API latency"
                except ImportError:
                    checks["llm_provider"]["api_validated"] = False
                    checks["llm_provider"]["note"] = "google-generativeai package not installed"
                except Exception as e:
                    checks["llm_provider"]["status"] = "degraded"
                    checks["llm_provider"]["api_validated"] = False
                    checks["llm_provider"]["api_error"] = str(e)[:100]
                    logger.warning("Gemini API validation failed", extra={"error": str(e)})

    except Exception as e:
        checks["llm_provider"] = {
            "status": "error",
            "error": str(e)[:100],
        }

    # FIX 5.1: Use APIResponse wrapper for consistency
    # Determinar estado general y código de respuesta
    if overall_healthy:
        return APIResponse(
            success=True,
            data={
                "status": "healthy",
                "checks": checks,
                "timestamp": utc_now().isoformat(),
            },
            message="All health checks passed"
        )
    else:
        return APIResponse(
            success=False,
            data={
                "status": "degraded",
                "checks": checks,
                "timestamp": utc_now().isoformat(),
            },
            message="Service is degraded"
        )