"""
Redis Cache Implementation - Caché distribuido para producción

Implementa un caché basado en Redis con fallback automático a caché en memoria
si Redis no está disponible.

Características:
- Persistencia entre reinicios
- Compartido entre múltiples workers/instancias
- Soporte para TTL nativo de Redis
- Fallback automático a caché en memoria
- Thread-safe
"""
import os
import json
import logging
import hashlib
import threading
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Try to import Redis, but make it optional
try:
    import redis
    from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis package not installed. Install with: pip install redis")


class RedisCache:
    """
    Redis-based cache implementation with automatic fallback to in-memory cache.

    Ventajas sobre caché en memoria:
    - Persistencia: Sobrevive reinicios del servidor
    - Distribuido: Compartido entre múltiples workers/pods
    - Escalable: Mayor capacidad de almacenamiento
    - TTL nativo: Redis maneja expiración automáticamente
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        ttl_seconds: int = 3600,
        enabled: bool = True,
        prefix: str = "llm_cache:"
    ):
        """
        Inicializa el caché Redis con fallback a memoria.

        Args:
            redis_url: URL de conexión a Redis (default: desde REDIS_URL env var)
            ttl_seconds: Tiempo de vida por defecto para las entradas
            enabled: Si el caché está habilitado
            prefix: Prefijo para todas las claves en Redis
        """
        self.ttl_seconds = ttl_seconds
        self.enabled = enabled
        self.prefix = prefix
        self._redis_client: Optional[Any] = None
        self._using_redis = False
        self._connection_error_logged = False

        # Estadísticas thread-safe
        self._hits = 0
        self._misses = 0
        self._stats_lock = threading.Lock()

        # Intentar conectar a Redis si está disponible
        if not REDIS_AVAILABLE:
            logger.warning(
                "Redis library not available. Using in-memory cache fallback. "
                "Install with: pip install redis"
            )
            self._initialize_fallback()
        else:
            redis_url = redis_url or os.getenv("REDIS_URL")

            if not redis_url:
                logger.warning(
                    "REDIS_URL not configured. Using in-memory cache fallback. "
                    "Set REDIS_URL environment variable for distributed caching."
                )
                self._initialize_fallback()
            else:
                self._initialize_redis(redis_url)

    def _initialize_redis(self, redis_url: str):
        """
        Inicializa conexión a Redis.

        Args:
            redis_url: URL de conexión (redis://host:port/db)
        """
        try:
            self._redis_client = redis.from_url(
                redis_url,
                decode_responses=True,  # Decodificar respuestas como strings
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )

            # Verificar conexión
            self._redis_client.ping()
            self._using_redis = True

            logger.info(
                f"✅ Redis cache connected successfully: {redis_url.split('@')[-1]} "
                f"(TTL: {self.ttl_seconds}s, prefix: '{self.prefix}')"
            )

        except (RedisConnectionError, RedisError) as e:
            logger.error(
                f"❌ Failed to connect to Redis: {e}. "
                f"Falling back to in-memory cache."
            )
            self._initialize_fallback()
        except Exception as e:
            logger.error(
                f"❌ Unexpected error connecting to Redis: {e}. "
                f"Falling back to in-memory cache."
            )
            self._initialize_fallback()

    def _initialize_fallback(self):
        """Inicializa caché en memoria como fallback."""
        from .cache import LRUCache

        self._fallback_cache = LRUCache(max_size=1000)
        self._using_redis = False

        logger.info(
            "📦 Using in-memory LRU cache (fallback mode). "
            "For production, configure Redis with REDIS_URL."
        )

    def _generate_cache_key(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        mode: Optional[str] = None
    ) -> str:
        """
        Genera clave de caché única.

        Args:
            prompt: Prompt del usuario
            context: Contexto adicional
            mode: Modo del agente

        Returns:
            Clave prefijada para Redis
        """
        data = {
            "prompt": prompt,
            "context": context or {},
            "mode": mode or "TUTOR"
        }

        json_str = json.dumps(data, sort_keys=True, ensure_ascii=True)
        hash_obj = hashlib.sha256(json_str.encode('utf-8'))
        key_hash = hash_obj.hexdigest()

        return f"{self.prefix}{key_hash}"

    def get(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        mode: Optional[str] = None
    ) -> Optional[str]:
        """
        Obtiene una respuesta del caché.

        Args:
            prompt: Prompt del usuario
            context: Contexto adicional
            mode: Modo del agente

        Returns:
            Respuesta cacheada o None si no existe
        """
        if not self.enabled:
            return None

        cache_key = self._generate_cache_key(prompt, context, mode)

        try:
            if self._using_redis and self._redis_client:
                # Intentar obtener de Redis
                try:
                    cached_value = self._redis_client.get(cache_key)

                    if cached_value is not None:
                        with self._stats_lock:
                            self._hits += 1
                        logger.debug(f"Redis cache HIT for key: {cache_key[:16]}...")
                        return cached_value
                    else:
                        with self._stats_lock:
                            self._misses += 1
                        return None

                except (RedisConnectionError, RedisError) as e:
                    if not self._connection_error_logged:
                        logger.error(
                            f"Redis connection error during GET: {e}. "
                            f"Falling back to memory cache."
                        )
                        self._connection_error_logged = True

                    # Fallback a caché en memoria
                    return self._fallback_cache.get(cache_key)
            else:
                # Usar fallback directamente
                cached_value = self._fallback_cache.get(cache_key)

                if cached_value is not None:
                    with self._stats_lock:
                        self._hits += 1
                    return cached_value
                else:
                    with self._stats_lock:
                        self._misses += 1
                    return None

        except Exception as e:
            logger.error(f"Unexpected error in cache GET: {e}")
            with self._stats_lock:
                self._misses += 1
            return None

    def set(
        self,
        prompt: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
        mode: Optional[str] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Guarda una respuesta en el caché.

        Args:
            prompt: Prompt del usuario
            response: Respuesta del LLM
            context: Contexto adicional
            mode: Modo del agente
            ttl: TTL personalizado (usa self.ttl_seconds si no se especifica)

        Returns:
            True si se guardó exitosamente, False en caso contrario
        """
        if not self.enabled:
            return False

        cache_key = self._generate_cache_key(prompt, context, mode)
        ttl_to_use = ttl or self.ttl_seconds

        try:
            if self._using_redis and self._redis_client:
                # Guardar en Redis con TTL
                try:
                    self._redis_client.setex(
                        cache_key,
                        ttl_to_use,
                        response
                    )
                    logger.debug(
                        f"Redis cache SET for key: {cache_key[:16]}... "
                        f"(TTL: {ttl_to_use}s, response length: {len(response)} chars)"
                    )
                    return True

                except (RedisConnectionError, RedisError) as e:
                    if not self._connection_error_logged:
                        logger.error(
                            f"Redis connection error during SET: {e}. "
                            f"Falling back to memory cache."
                        )
                        self._connection_error_logged = True

                    # Fallback a caché en memoria
                    self._fallback_cache.set(cache_key, response)
                    return True
            else:
                # Usar fallback directamente
                self._fallback_cache.set(cache_key, response)
                return True

        except Exception as e:
            logger.error(f"Unexpected error in cache SET: {e}")
            return False

    def clear(self) -> bool:
        """
        Limpia todo el caché.

        Returns:
            True si se limpió exitosamente
        """
        try:
            if self._using_redis and self._redis_client:
                # Eliminar todas las claves con el prefijo
                try:
                    keys = self._redis_client.keys(f"{self.prefix}*")
                    if keys:
                        self._redis_client.delete(*keys)
                        logger.info(f"Redis cache cleared: {len(keys)} keys deleted")

                    with self._stats_lock:
                        self._hits = 0
                        self._misses = 0
                    return True

                except (RedisConnectionError, RedisError) as e:
                    logger.error(f"Redis error during CLEAR: {e}")
                    self._fallback_cache.clear()
                    return True
            else:
                # Limpiar fallback
                self._fallback_cache.clear()
                with self._stats_lock:
                    self._hits = 0
                    self._misses = 0
                return True

        except Exception as e:
            logger.error(f"Unexpected error in cache CLEAR: {e}")
            return False

    def invalidate_by_pattern(self, pattern: str) -> int:
        """
        Invalida entradas del caché que coincidan con un patrón.

        Útil para invalidar cache relacionado con entidades específicas:
        - session:* - Invalida todo el cache de una sesión
        - student:* - Invalida cache de un estudiante
        - evaluation:* - Invalida evaluaciones

        Args:
            pattern: Patrón de búsqueda (ej: "session:abc123*")

        Returns:
            Número de claves eliminadas
        """
        full_pattern = f"{self.prefix}{pattern}"
        deleted_count = 0

        try:
            if self._using_redis and self._redis_client:
                try:
                    # Usar SCAN para evitar bloqueos en Redis con muchas claves
                    cursor = 0
                    keys_to_delete = []

                    while True:
                        cursor, keys = self._redis_client.scan(
                            cursor=cursor,
                            match=full_pattern,
                            count=100
                        )
                        keys_to_delete.extend(keys)

                        if cursor == 0:
                            break

                    if keys_to_delete:
                        deleted_count = self._redis_client.delete(*keys_to_delete)
                        logger.info(
                            f"Cache invalidated by pattern '{pattern}': "
                            f"{deleted_count} keys deleted"
                        )

                except (RedisConnectionError, RedisError) as e:
                    logger.error(f"Redis error during pattern invalidation: {e}")
                    # Fallback: limpiar todo el cache en memoria si hay error
                    self._fallback_cache.clear()
                    deleted_count = -1  # Indica que se limpió todo
            else:
                # En memoria: buscar claves que coincidan manualmente
                # Nota: LRUCache no soporta patrones, así que limpiamos todo como fallback seguro
                self._fallback_cache.clear()
                logger.info(
                    f"In-memory cache cleared (pattern invalidation not supported)"
                )
                deleted_count = -1

        except Exception as e:
            logger.error(f"Unexpected error in cache pattern invalidation: {e}")

        return deleted_count

    def invalidate_session(self, session_id: str) -> int:
        """
        Invalida todo el cache relacionado con una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            Número de claves eliminadas
        """
        return self.invalidate_by_pattern(f"*session*{session_id}*")

    def invalidate_student(self, student_id: str) -> int:
        """
        Invalida todo el cache relacionado con un estudiante.

        Args:
            student_id: ID del estudiante

        Returns:
            Número de claves eliminadas
        """
        return self.invalidate_by_pattern(f"*student*{student_id}*")

    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del caché.

        Returns:
            Diccionario con estadísticas
        """
        with self._stats_lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0

            stats = {
                "enabled": self.enabled,
                "backend": "redis" if self._using_redis else "memory",
                "ttl_seconds": self.ttl_seconds,
                "hits": self._hits,
                "misses": self._misses,
                "total_requests": total,
                "hit_rate_percent": round(hit_rate, 2)
            }

        # Agregar info específica de Redis si está disponible
        if self._using_redis and self._redis_client:
            try:
                info = self._redis_client.info("memory")
                stats["redis_memory_used_mb"] = round(
                    int(info.get("used_memory", 0)) / (1024 * 1024), 2
                )
                stats["redis_connected_clients"] = self._redis_client.info("clients").get("connected_clients", 0)
            except Exception as e:
                logger.debug(f"Could not fetch Redis stats: {e}")

        return stats

    def health_check(self) -> Dict[str, Any]:
        """
        Verifica la salud de la conexión a Redis.

        Returns:
            Diccionario con estado de salud
        """
        if not self._using_redis:
            return {
                "healthy": True,
                "backend": "memory",
                "message": "Using in-memory cache (fallback mode)"
            }

        try:
            if self._redis_client:
                self._redis_client.ping()
                return {
                    "healthy": True,
                    "backend": "redis",
                    "message": "Redis connection OK"
                }
        except Exception as e:
            return {
                "healthy": False,
                "backend": "redis",
                "message": f"Redis connection failed: {e}"
            }

        return {
            "healthy": False,
            "backend": "unknown",
            "message": "Cache not initialized"
        }


# Instancia global (singleton) con thread-safety
_global_redis_cache: Optional[RedisCache] = None
_cache_lock = threading.Lock()


def get_redis_cache(
    redis_url: Optional[str] = None,
    ttl_seconds: int = 3600,
    enabled: bool = True
) -> RedisCache:
    """
    Obtiene la instancia global del caché Redis (singleton).

    Thread-safe usando double-checked locking pattern.

    Args:
        redis_url: URL de conexión a Redis
        ttl_seconds: TTL para nuevas instancias
        enabled: Si el caché está habilitado

    Returns:
        Instancia del caché Redis
    """
    global _global_redis_cache

    # First check (without lock, fast path)
    if _global_redis_cache is None:
        # Second check (with lock, ensures only one thread initializes)
        with _cache_lock:
            if _global_redis_cache is None:
                _global_redis_cache = RedisCache(
                    redis_url=redis_url,
                    ttl_seconds=ttl_seconds,
                    enabled=enabled
                )

    return _global_redis_cache