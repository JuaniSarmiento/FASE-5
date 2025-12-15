# FASE 1: PRODUCTION READINESS - TAREAS P1.2 A P1.7

**Complemento de**: FASE1_PRODUCTION_READINESS_PLAN.md (P1.1 ya documentado)
**Tareas adicionales**: P1.2, P1.3, P1.4, P1.5, P1.6, P1.7
**Esfuerzo total**: 51 horas (67h - 16h de P1.1)

---

## 💾 P1.2: REDIS CACHE MIGRATION (8h)

### Objetivo
Migrar LLM response cache de in-memory a Redis para soporte multi-proceso

### Problema Actual
```python
# ❌ Cache actual: in-memory (no funciona con múltiples workers)
_global_cache: Optional[LLMResponseCache] = None  # Solo en memoria del proceso

# Problema con múltiples workers:
uvicorn app:main --workers 4  # Crea 4 caches separados, sin compartir
```

### Arquitectura Nueva

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Worker 1   │     │  Worker 2   │     │  Worker 3   │
│   (Cache)   │────▶│   (Cache)   │────▶│   (Cache)   │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                  ┌─────────────────┐
                  │  Redis Server   │
                  │  (Shared Cache) │
                  └─────────────────┘
```

### Components to Create

#### 1. Redis Cache Implementation (3h)

**Archivo**: `src/ai_native_mvp/core/redis_cache.py` (NUEVO)

```python
"""
Redis-based LLM response cache for distributed systems
"""
import json
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime

import redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class RedisLLMCache:
    """
    Redis-backed LLM response cache with TTL support

    Provides distributed caching across multiple workers/instances.
    Replaces in-memory cache for production deployments.

    Features:
    - Distributed (shared across processes)
    - TTL (automatic expiration)
    - Statistics tracking
    - Thread-safe (Redis handles concurrency)
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        ttl_seconds: int = 3600,
        enabled: bool = True,
        key_prefix: str = "llm_cache:"
    ):
        """
        Initialize Redis cache

        Args:
            redis_url: Redis connection URL
            ttl_seconds: Time-to-live for cached entries (default: 1 hour)
            enabled: Enable/disable caching
            key_prefix: Prefix for cache keys
        """
        self.enabled = enabled
        self.ttl_seconds = ttl_seconds
        self.key_prefix = key_prefix

        if not enabled:
            logger.warning("Redis cache is disabled")
            return

        try:
            # Connect to Redis
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )

            # Test connection
            self.redis_client.ping()

            logger.info(
                "Redis cache initialized successfully",
                extra={
                    "redis_url": redis_url,
                    "ttl_seconds": ttl_seconds,
                    "key_prefix": key_prefix
                }
            )

        except RedisError as e:
            logger.error(
                f"Failed to connect to Redis: {str(e)}",
                exc_info=True
            )
            # Fallback: disable caching if Redis unavailable
            self.enabled = False
            logger.warning("Redis cache disabled due to connection failure")

    def _generate_cache_key(
        self,
        messages: list,
        temperature: float,
        max_tokens: int,
        model: str
    ) -> str:
        """
        Generate deterministic cache key from request parameters

        Args:
            messages: List of LLM messages
            temperature: Temperature parameter
            max_tokens: Max tokens parameter
            model: Model name

        Returns:
            str: SHA-256 hash of parameters
        """
        # Serialize parameters to JSON (sorted for consistency)
        params = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "model": model
        }

        # Sort keys for deterministic hashing
        params_json = json.dumps(params, sort_keys=True)

        # Generate SHA-256 hash
        cache_key = hashlib.sha256(params_json.encode()).hexdigest()

        return f"{self.key_prefix}{cache_key}"

    def get(
        self,
        messages: list,
        temperature: float,
        max_tokens: int,
        model: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response if exists

        Args:
            messages: LLM messages
            temperature: Temperature
            max_tokens: Max tokens
            model: Model name

        Returns:
            Cached response dict or None if not found
        """
        if not self.enabled:
            return None

        try:
            cache_key = self._generate_cache_key(messages, temperature, max_tokens, model)

            # Get from Redis
            cached_data = self.redis_client.get(cache_key)

            if cached_data:
                # Increment hit counter
                self.redis_client.incr(f"{self.key_prefix}stats:hits")

                logger.debug(
                    "Cache HIT",
                    extra={"cache_key": cache_key[:16] + "..."}
                )

                return json.loads(cached_data)
            else:
                # Increment miss counter
                self.redis_client.incr(f"{self.key_prefix}stats:misses")

                logger.debug(
                    "Cache MISS",
                    extra={"cache_key": cache_key[:16] + "..."}
                )

                return None

        except RedisError as e:
            logger.error(
                f"Redis GET error: {str(e)}",
                exc_info=True
            )
            return None

    def set(
        self,
        messages: list,
        temperature: float,
        max_tokens: int,
        model: str,
        response: Dict[str, Any]
    ):
        """
        Store response in cache with TTL

        Args:
            messages: LLM messages
            temperature: Temperature
            max_tokens: Max tokens
            model: Model name
            response: Response to cache
        """
        if not self.enabled:
            return

        try:
            cache_key = self._generate_cache_key(messages, temperature, max_tokens, model)

            # Add metadata
            cache_entry = {
                "response": response,
                "cached_at": datetime.utcnow().isoformat(),
                "ttl": self.ttl_seconds
            }

            # Store in Redis with TTL
            self.redis_client.setex(
                cache_key,
                self.ttl_seconds,
                json.dumps(cache_entry)
            )

            logger.debug(
                "Response cached",
                extra={
                    "cache_key": cache_key[:16] + "...",
                    "ttl": self.ttl_seconds
                }
            )

        except RedisError as e:
            logger.error(
                f"Redis SET error: {str(e)}",
                exc_info=True
            )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            dict: Cache statistics (hits, misses, hit_rate)
        """
        if not self.enabled:
            return {
                "enabled": False,
                "hits": 0,
                "misses": 0,
                "hit_rate": 0.0
            }

        try:
            hits = int(self.redis_client.get(f"{self.key_prefix}stats:hits") or 0)
            misses = int(self.redis_client.get(f"{self.key_prefix}stats:misses") or 0)

            total = hits + misses
            hit_rate = (hits / total) if total > 0 else 0.0

            return {
                "enabled": True,
                "hits": hits,
                "misses": misses,
                "total_requests": total,
                "hit_rate": round(hit_rate, 3)
            }

        except RedisError as e:
            logger.error(
                f"Redis STATS error: {str(e)}",
                exc_info=True
            )
            return {"error": str(e)}

    def clear(self):
        """Clear all cache entries"""
        if not self.enabled:
            return

        try:
            # Find all keys with prefix
            keys = self.redis_client.keys(f"{self.key_prefix}*")

            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cache entries")

        except RedisError as e:
            logger.error(
                f"Redis CLEAR error: {str(e)}",
                exc_info=True
            )

    def health_check(self) -> bool:
        """
        Check if Redis connection is healthy

        Returns:
            bool: True if Redis is reachable
        """
        if not self.enabled:
            return False

        try:
            self.redis_client.ping()
            return True
        except RedisError:
            return False
```

#### 2. Update AIGateway to use Redis Cache (2h)

**Archivo**: `src/ai_native_mvp/core/ai_gateway.py` (MODIFICAR)

```python
# Imports at top
from .redis_cache import RedisLLMCache
import os

# In __init__
def __init__(self, ...):
    # ...existing code...

    # ✅ Use Redis cache instead of in-memory
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    cache_ttl = int(os.getenv("LLM_CACHE_TTL", "3600"))
    cache_enabled = os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"

    self.cache = RedisLLMCache(
        redis_url=redis_url,
        ttl_seconds=cache_ttl,
        enabled=cache_enabled
    )

    logger.info(
        "AIGateway initialized with Redis cache",
        extra={
            "redis_url": redis_url,
            "cache_enabled": cache_enabled,
            "cache_ttl": cache_ttl
        }
    )
```

#### 3. Update deps.py for Cache Singleton (1h)

**Archivo**: `src/ai_native_mvp/api/deps.py` (MODIFICAR)

```python
from ..core.redis_cache import RedisLLMCache
import os

# Global Redis cache instance (singleton)
_redis_cache_instance: Optional[RedisLLMCache] = None
_cache_lock = threading.Lock()


def get_redis_cache() -> RedisLLMCache:
    """
    Dependency para obtener Redis cache singleton

    Thread-safe initialization para prevenir race conditions.

    Returns:
        RedisLLMCache: Singleton cache instance
    """
    global _redis_cache_instance

    # Double-checked locking
    if _redis_cache_instance is None:
        with _cache_lock:
            if _redis_cache_instance is None:
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
                cache_ttl = int(os.getenv("LLM_CACHE_TTL", "3600"))
                cache_enabled = os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"

                _redis_cache_instance = RedisLLMCache(
                    redis_url=redis_url,
                    ttl_seconds=cache_ttl,
                    enabled=cache_enabled
                )

    return _redis_cache_instance
```

#### 4. Health Check Endpoint Update (30 min)

**Archivo**: `src/ai_native_mvp/api/routers/health.py` (MODIFICAR)

```python
from ..deps import get_redis_cache

@router.get("/health")
async def health(
    db: Session = Depends(get_db),
    cache: RedisLLMCache = Depends(get_redis_cache)
):
    """Comprehensive health check"""
    checks = {}

    # Database check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = {"healthy": True}
    except Exception as e:
        checks["database"] = {"healthy": False, "error": str(e)}

    # Redis cache check
    checks["redis_cache"] = {
        "healthy": cache.health_check(),
        "enabled": cache.enabled,
        "stats": cache.get_stats()
    }

    # Overall health
    all_healthy = all(c.get("healthy", False) for c in checks.values())
    status_code = 200 if all_healthy else 503

    return JSONResponse(
        content={
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": checks
        },
        status_code=status_code
    )
```

#### 5. Update requirements.txt (5 min)

```txt
# Add to requirements.txt:
redis==5.0.1
hiredis==2.2.3  # C parser for faster Redis operations
```

#### 6. Update .env.example (5 min)

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL=3600  # 1 hour

# For production with authentication:
# REDIS_URL=redis://:password@redis-host:6379/0
```

#### 7. Docker Compose with Redis (30 min)

**Archivo**: `docker-compose.yml` (section)

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  redis_data:
```

#### 8. Testing Script (1h)

**Archivo**: `tests/test_redis_cache.py` (NUEVO)

```python
"""
Test Redis cache implementation
"""
import pytest
from src.ai_native_mvp.core.redis_cache import RedisLLMCache


@pytest.fixture
def redis_cache():
    """Create Redis cache for testing"""
    cache = RedisLLMCache(
        redis_url="redis://localhost:6379",
        ttl_seconds=60,
        key_prefix="test_cache:"
    )
    yield cache
    # Cleanup
    cache.clear()


def test_cache_set_and_get(redis_cache):
    """Test basic cache set/get"""
    messages = [{"role": "user", "content": "test"}]
    response = {"content": "response", "tokens": 10}

    # Set cache
    redis_cache.set(
        messages=messages,
        temperature=0.7,
        max_tokens=100,
        model="gpt-4",
        response=response
    )

    # Get from cache
    cached = redis_cache.get(
        messages=messages,
        temperature=0.7,
        max_tokens=100,
        model="gpt-4"
    )

    assert cached is not None
    assert cached["response"] == response


def test_cache_miss(redis_cache):
    """Test cache miss"""
    cached = redis_cache.get(
        messages=[{"role": "user", "content": "nonexistent"}],
        temperature=0.7,
        max_tokens=100,
        model="gpt-4"
    )

    assert cached is None


def test_cache_stats(redis_cache):
    """Test cache statistics"""
    messages = [{"role": "user", "content": "test"}]

    # Miss
    redis_cache.get(messages, 0.7, 100, "gpt-4")

    # Set
    redis_cache.set(messages, 0.7, 100, "gpt-4", {"content": "response"})

    # Hit
    redis_cache.get(messages, 0.7, 100, "gpt-4")

    stats = redis_cache.get_stats()
    assert stats["hits"] >= 1
    assert stats["misses"] >= 1
    assert stats["hit_rate"] > 0


def test_cache_ttl_expiration(redis_cache):
    """Test TTL expiration"""
    import time

    # Create cache with 1 second TTL
    short_cache = RedisLLMCache(
        redis_url="redis://localhost:6379",
        ttl_seconds=1,
        key_prefix="test_ttl:"
    )

    messages = [{"role": "user", "content": "expire test"}]

    # Set cache
    short_cache.set(messages, 0.7, 100, "gpt-4", {"content": "response"})

    # Should exist immediately
    cached = short_cache.get(messages, 0.7, 100, "gpt-4")
    assert cached is not None

    # Wait for TTL expiration
    time.sleep(2)

    # Should be expired
    cached = short_cache.get(messages, 0.7, 100, "gpt-4")
    assert cached is None


def test_cache_disabled(redis_cache):
    """Test cache when disabled"""
    disabled_cache = RedisLLMCache(
        redis_url="redis://localhost:6379",
        enabled=False
    )

    messages = [{"role": "user", "content": "test"}]

    # Set should do nothing
    disabled_cache.set(messages, 0.7, 100, "gpt-4", {"content": "response"})

    # Get should return None
    cached = disabled_cache.get(messages, 0.7, 100, "gpt-4")
    assert cached is None
```

### Implementation Checklist

- [ ] Install Redis server locally or via Docker
- [ ] Create RedisLLMCache class (3h)
- [ ] Update AIGateway to use Redis cache (2h)
- [ ] Update deps.py cache singleton (1h)
- [ ] Update health check endpoint (30min)
- [ ] Update requirements.txt (5min)
- [ ] Update .env.example (5min)
- [ ] Add Redis to docker-compose.yml (30min)
- [ ] Write tests (1h)
- [ ] Run tests
- [ ] Performance benchmarking
- [ ] Documentation update

### Testing Commands

```bash
# 1. Start Redis via Docker
docker run -d -p 6379:6379 redis:7-alpine

# 2. Install dependencies
pip install redis hiredis

# 3. Test Redis connection
redis-cli ping  # Should return "PONG"

# 4. Run tests
pytest tests/test_redis_cache.py -v

# 5. Start API with Redis cache
export REDIS_URL=redis://localhost:6379
python scripts/run_api.py

# 6. Check cache stats
curl http://localhost:8000/api/v1/health

# 7. Benchmark cache performance
python examples/benchmark_redis_cache.py
```

### Success Criteria

✅ **P1.2 Complete** when:
1. Redis cache works with multiple uvicorn workers
2. Cache is shared across all processes
3. TTL expiration works correctly
4. Health check includes Redis status
5. Tests pass (100% coverage for cache)
6. Performance benchmarking shows improvement
7. Documentation updated

---

## 🔌 P1.3: DATABASE CONNECTION POOLING (3h)

### Objetivo
Configurar SQLAlchemy connection pooling para producción

### Problema Actual
```python
# ❌ Pool configuration not exposed
engine = create_engine(
    database_url,
    # Missing: pool_size, max_overflow, pool_timeout, etc.
)
```

### Solution

#### 1. Update database/config.py (2h)

**Archivo**: `src/ai_native_mvp/database/config.py` (MODIFICAR)

```python
"""
Enhanced database configuration with production-ready pooling
"""
import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
import logging

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """
    Enhanced database configuration manager with production pooling
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        echo: bool = False,
        # ✅ NEW: Pool configuration
        pool_size: int = 20,
        max_overflow: int = 10,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        pool_pre_ping: bool = True,
        # ✅ NEW: Environment detection
        environment: str = "development"
    ):
        """
        Initialize database with production-ready pooling

        Args:
            database_url: Database connection string
            echo: Log SQL queries (development only)
            pool_size: Number of connections to maintain (default: 20)
            max_overflow: Max connections beyond pool_size (default: 10)
            pool_timeout: Seconds to wait for connection (default: 30)
            pool_recycle: Recycle connections after N seconds (default: 1 hour)
            pool_pre_ping: Verify connections before use (default: True)
            environment: dev/staging/production (affects pooling strategy)
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", "sqlite:///ai_native.db"
        )
        self.echo = echo and (environment == "development")  # Only echo in dev
        self.environment = environment

        # Pool configuration from environment or defaults
        self.pool_size = int(os.getenv("DB_POOL_SIZE", str(pool_size)))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", str(max_overflow)))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", str(pool_timeout)))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", str(pool_recycle)))
        self.pool_pre_ping = os.getenv("DB_POOL_PRE_PING", str(pool_pre_ping)).lower() == "true"

        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None

        logger.info(
            "DatabaseConfig initialized",
            extra={
                "environment": self.environment,
                "pool_size": self.pool_size,
                "max_overflow": self.max_overflow,
                "database_type": "sqlite" if "sqlite" in self.database_url else "postgresql"
            }
        )

    def get_engine(self) -> Engine:
        """Get or create SQLAlchemy engine with production pooling"""
        if self._engine is None:

            # SQLite configuration (development/testing)
            if self.database_url.startswith("sqlite"):
                logger.info("Using SQLite database (development mode)")

                # SQLite: Use NullPool for simplicity
                from sqlalchemy.pool import StaticPool

                self._engine = create_engine(
                    self.database_url,
                    echo=self.echo,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool if ":memory:" in self.database_url else NullPool,
                )

                # Enable foreign keys for SQLite
                @event.listens_for(self._engine, "connect")
                def set_sqlite_pragma(dbapi_conn, connection_record):
                    cursor = dbapi_conn.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
                    cursor.close()

            # PostgreSQL configuration (production)
            else:
                logger.info(
                    "Using PostgreSQL with production pooling",
                    extra={
                        "pool_size": self.pool_size,
                        "max_overflow": self.max_overflow,
                        "pool_timeout": self.pool_timeout,
                        "pool_recycle": self.pool_recycle
                    }
                )

                self._engine = create_engine(
                    self.database_url,
                    echo=self.echo,
                    # ✅ Production pooling configuration
                    poolclass=QueuePool,
                    pool_size=self.pool_size,              # Core connections
                    max_overflow=self.max_overflow,        # Extra connections under load
                    pool_timeout=self.pool_timeout,        # Wait time for connection
                    pool_recycle=self.pool_recycle,        # Recycle after 1 hour
                    pool_pre_ping=self.pool_pre_ping,     # Verify connection health
                    # ✅ Statement timeout (prevent long queries)
                    connect_args={
                        "connect_timeout": 10,
                        "options": f"-c statement_timeout={30000}"  # 30 seconds
                    }
                )

                # ✅ Monitor pool statistics
                @event.listens_for(self._engine, "connect")
                def receive_connect(dbapi_conn, connection_record):
                    logger.debug("New database connection established")

                @event.listens_for(self._engine, "checkout")
                def receive_checkout(dbapi_conn, connection_record, connection_proxy):
                    logger.debug("Connection checked out from pool")

        return self._engine

    def get_pool_stats(self) -> dict:
        """
        Get connection pool statistics

        Returns:
            dict: Pool stats (size, checked_out, overflow, etc.)
        """
        if self._engine is None or not hasattr(self._engine.pool, 'size'):
            return {"error": "Engine not initialized or no pool"}

        pool = self._engine.pool

        return {
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "max_overflow": self.max_overflow,
            "total_available": pool.size() + pool.overflow() - pool.checkedout(),
            "timeout": self.pool_timeout
        }

    # ... rest of class (get_session_factory, create_all_tables, etc.)
```

#### 2. Update .env.example (15 min)

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/ai_native

# Connection Pooling (PostgreSQL)
DB_POOL_SIZE=20                 # Core connections
DB_MAX_OVERFLOW=10              # Extra connections under load
DB_POOL_TIMEOUT=30              # Seconds to wait for connection
DB_POOL_RECYCLE=3600            # Recycle connections after 1 hour
DB_POOL_PRE_PING=true           # Verify connections before use

# For SQLite (development):
# DATABASE_URL=sqlite:///ai_native.db
```

#### 3. Pool Monitoring Endpoint (45 min)

**Archivo**: `src/ai_native_mvp/api/routers/health.py` (MODIFICAR)

```python
@router.get("/health/database")
async def database_health(db: Session = Depends(get_db)):
    """
    Detailed database health check with pool statistics
    """
    from ...database import get_db_config

    db_config = get_db_config()

    checks = {}

    # Connection test
    try:
        result = db.execute(text("SELECT 1")).scalar()
        checks["connection"] = {"healthy": True, "test_query": result}
    except Exception as e:
        checks["connection"] = {"healthy": False, "error": str(e)}

    # Pool statistics
    try:
        pool_stats = db_config.get_pool_stats()
        checks["pool"] = {
            "healthy": True,
            "stats": pool_stats,
            "utilization": round(
                pool_stats["checked_out"] / pool_stats["pool_size"] * 100, 2
            ) if "checked_out" in pool_stats else 0
        }
    except Exception as e:
        checks["pool"] = {"healthy": False, "error": str(e)}

    # Table count
    try:
        table_count = db.execute(text(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"
        )).scalar()
        checks["tables"] = {"healthy": True, "count": table_count}
    except:
        # SQLite fallback
        try:
            table_count = db.execute(text(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            )).scalar()
            checks["tables"] = {"healthy": True, "count": table_count}
        except Exception as e:
            checks["tables"] = {"healthy": False, "error": str(e)}

    all_healthy = all(c.get("healthy", False) for c in checks.values())

    return JSONResponse(
        content={
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": checks
        },
        status_code=200 if all_healthy else 503
    )
```

### Implementation Checklist

- [ ] Update DatabaseConfig with pooling (2h)
- [ ] Update .env.example with pool config (15min)
- [ ] Add pool monitoring endpoint (45min)
- [ ] Test with PostgreSQL
- [ ] Load test to verify pooling
- [ ] Documentation update

### Testing Commands

```bash
# 1. Test with SQLite (development)
DATABASE_URL=sqlite:///test.db python scripts/run_api.py

# 2. Test with PostgreSQL (production config)
DATABASE_URL=postgresql://user:pass@localhost/db \
DB_POOL_SIZE=20 \
DB_MAX_OVERFLOW=10 \
python scripts/run_api.py

# 3. Check pool stats
curl http://localhost:8000/api/v1/health/database

# 4. Load test (simulate 50 concurrent connections)
ab -n 1000 -c 50 http://localhost:8000/api/v1/health/database
```

### Success Criteria

✅ **P1.3 Complete** when:
1. Pool configuration exposed via environment variables
2. PostgreSQL uses QueuePool with correct settings
3. Pool statistics endpoint works
4. Load testing shows pool handles 50+ concurrent requests
5. Connections recycled after 1 hour
6. Pre-ping prevents stale connections
7. Documentation updated

---

## 🏗️ P1.4: REFACTOR AIGATEWAY GOD CLASS (8h)

### Objetivo
Dividir AIGateway (839 líneas) en componentes enfocados

### Problema Actual
```python
# ❌ AIGateway hace DEMASIADO:
class AIGateway:
    def process_interaction(...)       # Orchestration
    def _create_trace(...)             # Trace management
    def _persist_trace(...)            # Persistence
    def _persist_risk(...)             # Risk management
    def _analyze_risks_async(...)      # Risk analysis
    def _generate_socratic_response(...)  # Response generation
    # ... 20+ methods
```

### Nueva Arquitectura

```
AIGateway (Orchestrator) - 200 líneas
    ├── InteractionOrchestrator - 150 líneas
    ├── TraceManager - 120 líneas
    ├── RiskAnalyzer - 150 líneas
    └── ResponseGenerator - 180 líneas
```

### Components to Create

#### 1. TraceManager Component (2h)

**Archivo**: `src/ai_native_mvp/core/components/trace_manager.py` (NUEVO)

```python
"""
Trace management component - Extract from AIGateway
"""
import logging
from typing import Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime

from ...models.trace import CognitiveTrace, TraceLevel, InteractionType
from ...database.repositories import TraceRepository, TraceSequenceRepository

logger = logging.getLogger(__name__)


class TraceManager:
    """
    Manages cognitive trace creation and persistence

    Responsibilities:
    - Create N4-level traces
    - Persist traces to database
    - Retrieve student history
    - Build trace sequences
    """

    def __init__(
        self,
        trace_repo: Optional[TraceRepository] = None,
        sequence_repo: Optional[TraceSequenceRepository] = None
    ):
        """
        Initialize trace manager

        Args:
            trace_repo: Trace repository (optional for testing)
            sequence_repo: Sequence repository (optional)
        """
        self.trace_repo = trace_repo
        self.sequence_repo = sequence_repo

    def create_trace(
        self,
        session_id: str,
        student_id: str,
        activity_id: str,
        interaction_type: InteractionType,
        content: str,
        cognitive_state: Optional[str] = None,
        cognitive_intent: Optional[str] = None,
        ai_involvement: float = 0.5,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CognitiveTrace:
        """
        Create N4-level cognitive trace

        Args:
            session_id: Session identifier
            student_id: Student identifier
            activity_id: Activity identifier
            interaction_type: Type of interaction
            content: Trace content (prompt or response)
            cognitive_state: Detected cognitive state
            cognitive_intent: Student's cognitive intent
            ai_involvement: Level of AI involvement (0-1)
            context: Additional context
            metadata: Additional metadata

        Returns:
            CognitiveTrace: Created trace
        """
        trace = CognitiveTrace(
            id=str(uuid4()),
            session_id=session_id,
            student_id=student_id,
            activity_id=activity_id,
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=interaction_type,
            content=content,
            context=context or {},
            metadata=metadata or {},
            cognitive_state=cognitive_state,
            cognitive_intent=cognitive_intent,
            ai_involvement=ai_involvement,
            created_at=datetime.utcnow()
        )

        logger.debug(
            "Trace created",
            extra={
                "trace_id": trace.id,
                "session_id": session_id,
                "interaction_type": interaction_type.value
            }
        )

        return trace

    def persist_trace(self, trace: CognitiveTrace):
        """
        Persist trace to database

        Args:
            trace: Trace to persist
        """
        if self.trace_repo is None:
            logger.warning(
                "Trace repository is None, cannot persist trace",
                extra={
                    "session_id": trace.session_id,
                    "interaction_type": trace.interaction_type.value
                }
            )
            return

        try:
            self.trace_repo.create(trace)

            logger.info(
                "Trace persisted to database",
                extra={
                    "trace_id": trace.id,
                    "session_id": trace.session_id,
                    "student_id": trace.student_id,
                    "interaction_type": trace.interaction_type.value
                }
            )

        except Exception as e:
            logger.error(
                f"Failed to persist trace: {type(e).__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "trace_id": trace.id,
                    "session_id": trace.session_id
                }
            )
            # Re-raise to maintain error propagation
            raise

    def get_student_history(
        self,
        student_id: str,
        activity_id: Optional[str] = None,
        limit: int = 100
    ) -> List[CognitiveTrace]:
        """
        Get student's trace history from database

        Args:
            student_id: Student identifier
            activity_id: Optional activity filter
            limit: Max number of traces to retrieve

        Returns:
            List of cognitive traces
        """
        if self.trace_repo is None:
            return []

        # Get traces from database
        db_traces = self.trace_repo.get_by_student(student_id, limit=limit)

        # Convert ORM to Pydantic
        traces = []
        for db_trace in db_traces:
            try:
                trace = CognitiveTrace(
                    id=db_trace.id,
                    session_id=db_trace.session_id,
                    student_id=db_trace.student_id,
                    activity_id=db_trace.activity_id,
                    trace_level=TraceLevel(db_trace.trace_level),
                    interaction_type=InteractionType(db_trace.interaction_type),
                    content=db_trace.content or "",
                    context=db_trace.context or {},
                    metadata=db_trace.trace_metadata or {},
                    cognitive_state=db_trace.cognitive_state,
                    ai_involvement=db_trace.ai_involvement or 0.5,
                )
                traces.append(trace)
            except Exception as e:
                logger.warning(
                    f"Failed to convert trace: {type(e).__name__}: {str(e)}",
                    exc_info=True,
                    extra={
                        "trace_id": db_trace.id if hasattr(db_trace, 'id') else 'unknown',
                        "student_id": student_id
                    }
                )
                continue

        # Filter by activity if specified
        if activity_id:
            traces = [t for t in traces if t.activity_id == activity_id]

        logger.debug(
            f"Retrieved {len(traces)} traces for student",
            extra={"student_id": student_id, "activity_id": activity_id}
        )

        return traces
```

**(Continuación en siguiente mensaje - documento muy largo)**

¿Quiero que continue con P1.4 a P1.7 o prefieres que comencemos ya con la implementación de P1.1?