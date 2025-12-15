"""
Métricas personalizadas de Prometheus para el backend
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from functools import wraps
import time
from typing import Callable

# ==================== METRICS ====================

# Interacciones
interactions_total = Counter(
    'ai_interactions_total',
    'Total de interacciones con el LLM',
    ['mode', 'cognitive_state', 'blocked']
)

interactions_duration = Histogram(
    'ai_interactions_duration_seconds',
    'Duración de las interacciones con el LLM',
    ['mode'],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
)

# Sesiones
sessions_active = Gauge(
    'ai_sessions_active',
    'Número de sesiones activas'
)

sessions_total = Counter(
    'ai_sessions_total',
    'Total de sesiones creadas',
    ['mode']
)

# LLM específico
llm_requests_total = Counter(
    'llm_requests_total',
    'Total de requests al LLM',
    ['provider', 'model', 'status']
)

llm_tokens_total = Counter(
    'llm_tokens_total',
    'Total de tokens consumidos',
    ['provider', 'model', 'type']  # type: prompt, completion
)

llm_latency = Histogram(
    'llm_latency_seconds',
    'Latencia de llamadas al LLM',
    ['provider', 'model'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 60.0]
)

# Circuit Breaker
circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Estado del circuit breaker (0=closed, 1=open, 2=half_open)',
    ['service']
)

circuit_breaker_trips = Counter(
    'circuit_breaker_trips_total',
    'Total de veces que el circuit breaker se abrió',
    ['service']
)

# Cache
cache_hits = Counter(
    'cache_hits_total',
    'Total de cache hits',
    ['cache_name']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total de cache misses',
    ['cache_name']
)

cache_size = Gauge(
    'cache_size_bytes',
    'Tamaño actual del caché en bytes',
    ['cache_name']
)

# Evaluaciones
evaluations_total = Counter(
    'evaluations_total',
    'Total de evaluaciones generadas',
    ['competency_level']
)

evaluations_duration = Histogram(
    'evaluations_duration_seconds',
    'Duración de las evaluaciones',
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

# Riesgos
risks_detected = Counter(
    'risks_detected_total',
    'Total de riesgos detectados',
    ['dimension', 'level']
)

# Sistema
app_info = Info('app', 'Información de la aplicación')
app_info.info({
    'version': '2.0.0',
    'environment': 'production',
    'model': 'llama3.2:3b'
})

# ==================== DECORATORS ====================

def track_interaction_time(mode: str):
    """Decorator para trackear duración de interacciones"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                interactions_duration.labels(mode=mode).observe(duration)
        return wrapper
    return decorator

def track_llm_call(provider: str, model: str):
    """Decorator para trackear llamadas al LLM"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'success'
            try:
                result = await func(*args, **kwargs)
                
                # Track tokens if available
                if hasattr(result, 'usage'):
                    llm_tokens_total.labels(
                        provider=provider,
                        model=model,
                        type='prompt'
                    ).inc(result.usage.prompt_tokens)
                    
                    llm_tokens_total.labels(
                        provider=provider,
                        model=model,
                        type='completion'
                    ).inc(result.usage.completion_tokens)
                
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                llm_latency.labels(provider=provider, model=model).observe(duration)
                llm_requests_total.labels(
                    provider=provider,
                    model=model,
                    status=status
                ).inc()
        return wrapper
    return decorator

def track_cache_usage(cache_name: str):
    """Decorator para trackear uso de caché"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Intenta obtener del caché (simulado)
            # En implementación real, verificarías el caché aquí
            result = await func(*args, **kwargs)
            
            # Este es un ejemplo simplificado
            # En producción, detectarías si fue hit o miss
            if hasattr(result, '_from_cache') and result._from_cache:
                cache_hits.labels(cache_name=cache_name).inc()
            else:
                cache_misses.labels(cache_name=cache_name).inc()
            
            return result
        return wrapper
    return decorator

# ==================== HELPER FUNCTIONS ====================

def record_interaction(
    mode: str,
    cognitive_state: str,
    blocked: bool
):
    """Registra una interacción"""
    interactions_total.labels(
        mode=mode,
        cognitive_state=cognitive_state,
        blocked=str(blocked).lower()
    ).inc()

def record_session(mode: str, active: bool):
    """Registra una sesión"""
    sessions_total.labels(mode=mode).inc()
    if active:
        sessions_active.inc()
    else:
        sessions_active.dec()

def record_circuit_breaker_state(service: str, state: str):
    """Registra estado del circuit breaker"""
    state_map = {'closed': 0, 'open': 1, 'half_open': 2}
    circuit_breaker_state.labels(service=service).set(state_map.get(state, 0))
    
    if state == 'open':
        circuit_breaker_trips.labels(service=service).inc()

def record_evaluation(competency_level: str, duration: float):
    """Registra una evaluación"""
    evaluations_total.labels(competency_level=competency_level).inc()
    evaluations_duration.observe(duration)

def record_risk(dimension: str, level: str):
    """Registra un riesgo detectado"""
    risks_detected.labels(dimension=dimension, level=level).inc()

def update_cache_size(cache_name: str, size_bytes: int):
    """Actualiza tamaño del caché"""
    cache_size.labels(cache_name=cache_name).set(size_bytes)
