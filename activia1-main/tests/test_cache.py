"""
Tests for Cache Layer

Tests para backend/core/cache.py y backend/core/redis_cache.py

Verifica:
1. LRU Cache (en memoria)
2. LLM Response Cache con TTL
3. Redis Cache con fallback
4. Thread-safety
5. Generación de cache keys
6. Estadísticas y métricas
"""

import pytest
import time
import threading
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime
from uuid import uuid4


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def lru_cache():
    """Create fresh LRU cache instance"""
    from backend.core.cache import LRUCache
    return LRUCache(max_size=5)


@pytest.fixture
def llm_cache():
    """Create fresh LLM response cache instance"""
    from backend.core.cache import LLMResponseCache
    return LLMResponseCache(ttl_seconds=60, max_entries=100, enabled=True)


@pytest.fixture
def llm_cache_disabled():
    """Create disabled LLM cache instance"""
    from backend.core.cache import LLMResponseCache
    return LLMResponseCache(ttl_seconds=60, max_entries=100, enabled=False)


@pytest.fixture
def redis_cache_mock():
    """Create Redis cache with mocked Redis client"""
    with patch('backend.core.redis_cache.REDIS_AVAILABLE', True):
        with patch('backend.core.redis_cache.redis') as mock_redis:
            mock_client = MagicMock()
            mock_client.ping.return_value = True
            mock_client.get.return_value = None
            mock_client.setex.return_value = True
            mock_redis.from_url.return_value = mock_client

            from backend.core.redis_cache import RedisCache
            cache = RedisCache(
                redis_url="redis://localhost:6379/0",
                ttl_seconds=3600,
                enabled=True
            )
            cache._mock_client = mock_client
            return cache


# ============================================================================
# LRU Cache Tests
# ============================================================================

class TestLRUCache:
    """Tests for LRU Cache implementation"""

    @pytest.mark.unit
    def test_lru_cache_set_and_get(self, lru_cache):
        """LRU cache stores and retrieves values"""
        lru_cache.set("key1", "value1")
        result = lru_cache.get("key1")

        assert result == "value1"

    @pytest.mark.unit
    def test_lru_cache_miss(self, lru_cache):
        """LRU cache returns None for missing keys"""
        result = lru_cache.get("nonexistent")

        assert result is None

    @pytest.mark.unit
    def test_lru_cache_eviction(self, lru_cache):
        """LRU cache evicts oldest entry when full"""
        # Fill cache (max_size=5)
        for i in range(5):
            lru_cache.set(f"key{i}", f"value{i}")

        # Add one more - should evict key0
        lru_cache.set("key5", "value5")

        # key0 should be evicted
        assert lru_cache.get("key0") is None
        # key5 should exist
        assert lru_cache.get("key5") == "value5"

    @pytest.mark.unit
    def test_lru_cache_access_updates_recency(self, lru_cache):
        """Accessing a key moves it to most recent position"""
        # Fill cache
        for i in range(5):
            lru_cache.set(f"key{i}", f"value{i}")

        # Access key0 to make it recent
        lru_cache.get("key0")

        # Add new entry - should evict key1 (now oldest)
        lru_cache.set("key5", "value5")

        # key0 should still exist (was accessed recently)
        assert lru_cache.get("key0") == "value0"
        # key1 should be evicted
        assert lru_cache.get("key1") is None

    @pytest.mark.unit
    def test_lru_cache_stats(self, lru_cache):
        """LRU cache tracks hit/miss statistics"""
        lru_cache.set("key1", "value1")

        # Hit
        lru_cache.get("key1")
        # Miss
        lru_cache.get("nonexistent")

        stats = lru_cache.get_stats()

        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["total_requests"] == 2
        assert stats["hit_rate_percent"] == 50.0

    @pytest.mark.unit
    def test_lru_cache_clear(self, lru_cache):
        """LRU cache clear removes all entries"""
        lru_cache.set("key1", "value1")
        lru_cache.set("key2", "value2")

        lru_cache.clear()

        assert lru_cache.get("key1") is None
        assert lru_cache.get("key2") is None

        stats = lru_cache.get_stats()
        assert stats["current_size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0

    @pytest.mark.unit
    def test_lru_cache_update_existing_key(self, lru_cache):
        """LRU cache updates existing keys"""
        lru_cache.set("key1", "value1")
        lru_cache.set("key1", "new_value")

        result = lru_cache.get("key1")

        assert result == "new_value"


# ============================================================================
# LLM Response Cache Tests
# ============================================================================

class TestLLMResponseCache:
    """Tests for LLM Response Cache with TTL"""

    @pytest.mark.unit
    def test_llm_cache_set_and_get(self, llm_cache):
        """LLM cache stores and retrieves responses"""
        prompt = "Test prompt"
        response = "Test response"

        llm_cache.set(prompt, response)
        result = llm_cache.get(prompt)

        assert result == response

    @pytest.mark.unit
    def test_llm_cache_disabled(self, llm_cache_disabled):
        """Disabled cache returns None and doesn't store"""
        prompt = "Test prompt"
        response = "Test response"

        llm_cache_disabled.set(prompt, response)
        result = llm_cache_disabled.get(prompt)

        assert result is None

    @pytest.mark.unit
    def test_llm_cache_ttl_expiration(self):
        """LLM cache entries expire after TTL"""
        from backend.core.cache import LLMResponseCache

        # Short TTL for testing
        cache = LLMResponseCache(ttl_seconds=1, max_entries=100, enabled=True)

        prompt = "Test prompt"
        response = "Test response"

        cache.set(prompt, response)
        assert cache.get(prompt) == response

        # Wait for expiration
        time.sleep(1.1)

        result = cache.get(prompt)
        assert result is None

    @pytest.mark.unit
    def test_llm_cache_context_affects_key(self, llm_cache):
        """Different contexts generate different cache keys"""
        prompt = "Test prompt"
        context1 = {"file": "main.py"}
        context2 = {"file": "test.py"}

        llm_cache.set(prompt, "response1", context=context1)
        llm_cache.set(prompt, "response2", context=context2)

        result1 = llm_cache.get(prompt, context=context1)
        result2 = llm_cache.get(prompt, context=context2)

        assert result1 == "response1"
        assert result2 == "response2"

    @pytest.mark.unit
    def test_llm_cache_mode_affects_key(self, llm_cache):
        """Different modes generate different cache keys"""
        prompt = "Test prompt"

        llm_cache.set(prompt, "tutor_response", mode="TUTOR")
        llm_cache.set(prompt, "evaluator_response", mode="EVALUATOR")

        result_tutor = llm_cache.get(prompt, mode="TUTOR")
        result_eval = llm_cache.get(prompt, mode="EVALUATOR")

        assert result_tutor == "tutor_response"
        assert result_eval == "evaluator_response"

    @pytest.mark.unit
    def test_llm_cache_stats(self, llm_cache):
        """LLM cache tracks statistics"""
        llm_cache.set("prompt1", "response1")

        # Hit
        llm_cache.get("prompt1")
        # Miss
        llm_cache.get("prompt2")

        stats = llm_cache.get_stats()

        assert stats["enabled"] is True
        assert stats["hits"] >= 1
        assert stats["misses"] >= 1
        assert "ttl_seconds" in stats

    @pytest.mark.unit
    def test_llm_cache_clear(self, llm_cache):
        """LLM cache clear removes all entries"""
        llm_cache.set("prompt1", "response1")
        llm_cache.set("prompt2", "response2")

        llm_cache.clear()

        assert llm_cache.get("prompt1") is None
        assert llm_cache.get("prompt2") is None

    @pytest.mark.unit
    def test_llm_cache_cleanup_expired(self):
        """LLM cache cleanup removes expired entries"""
        from backend.core.cache import LLMResponseCache

        cache = LLMResponseCache(ttl_seconds=1, max_entries=100, enabled=True)

        cache.set("prompt1", "response1")
        time.sleep(1.1)

        removed = cache.cleanup_expired()

        assert removed >= 1


# ============================================================================
# Cache Key Generation Tests
# ============================================================================

class TestCacheKeyGeneration:
    """Tests for cache key generation"""

    @pytest.mark.unit
    def test_cache_key_deterministic(self, llm_cache):
        """Same inputs generate same cache key"""
        prompt = "Test prompt"
        context = {"file": "main.py"}
        mode = "TUTOR"

        key1 = llm_cache._generate_cache_key(prompt, context, mode)
        key2 = llm_cache._generate_cache_key(prompt, context, mode)

        assert key1 == key2

    @pytest.mark.unit
    def test_cache_key_different_for_different_inputs(self, llm_cache):
        """Different inputs generate different cache keys"""
        key1 = llm_cache._generate_cache_key("prompt1", None, "TUTOR")
        key2 = llm_cache._generate_cache_key("prompt2", None, "TUTOR")

        assert key1 != key2

    @pytest.mark.unit
    def test_cache_key_is_hash(self, llm_cache):
        """Cache key is a valid SHA256 hash"""
        key = llm_cache._generate_cache_key("test prompt", None, None)

        # SHA256 produces 64 character hex string
        assert len(key) == 64
        assert all(c in '0123456789abcdef' for c in key)

    @pytest.mark.unit
    def test_cache_key_handles_unicode(self, llm_cache):
        """Cache key generation handles unicode"""
        prompt = "Pregunta sobre código: función calcular_área()"
        context = {"variable": "número"}

        key = llm_cache._generate_cache_key(prompt, context, "TUTOR")

        assert len(key) == 64

    @pytest.mark.unit
    def test_cache_key_handles_special_characters(self, llm_cache):
        """Cache key generation handles special characters"""
        prompt = 'Code: print("Hello\\nWorld")'
        context = {"code": "def foo():\n\treturn 42"}

        key = llm_cache._generate_cache_key(prompt, context, "EVALUATOR")

        assert len(key) == 64


# ============================================================================
# Redis Cache Tests
# ============================================================================

class TestRedisCache:
    """Tests for Redis Cache implementation"""

    @pytest.mark.unit
    def test_redis_cache_set_and_get(self, redis_cache_mock):
        """Redis cache stores and retrieves values"""
        redis_cache_mock._mock_client.get.return_value = "cached_response"

        result = redis_cache_mock.get("test prompt")

        assert result == "cached_response"

    @pytest.mark.unit
    def test_redis_cache_miss(self, redis_cache_mock):
        """Redis cache returns None for missing keys"""
        redis_cache_mock._mock_client.get.return_value = None

        result = redis_cache_mock.get("nonexistent prompt")

        assert result is None

    @pytest.mark.unit
    def test_redis_cache_set_with_ttl(self, redis_cache_mock):
        """Redis cache sets values with TTL"""
        redis_cache_mock.set("test prompt", "test response")

        redis_cache_mock._mock_client.setex.assert_called_once()
        # Verify TTL is passed
        call_args = redis_cache_mock._mock_client.setex.call_args
        assert call_args[0][1] == 3600  # Default TTL

    @pytest.mark.unit
    def test_redis_cache_custom_ttl(self, redis_cache_mock):
        """Redis cache supports custom TTL"""
        redis_cache_mock.set("test prompt", "test response", ttl=120)

        call_args = redis_cache_mock._mock_client.setex.call_args
        assert call_args[0][1] == 120

    @pytest.mark.unit
    def test_redis_cache_stats(self, redis_cache_mock):
        """Redis cache tracks statistics"""
        # Simulate hit
        redis_cache_mock._mock_client.get.return_value = "response"
        redis_cache_mock.get("prompt1")

        # Simulate miss
        redis_cache_mock._mock_client.get.return_value = None
        redis_cache_mock.get("prompt2")

        stats = redis_cache_mock.get_stats()

        assert stats["backend"] == "redis"
        assert stats["hits"] == 1
        assert stats["misses"] == 1

    @pytest.mark.unit
    def test_redis_cache_health_check(self, redis_cache_mock):
        """Redis cache health check returns status"""
        health = redis_cache_mock.health_check()

        assert health["healthy"] is True
        assert health["backend"] == "redis"

    @pytest.mark.unit
    def test_redis_cache_fallback_on_error(self):
        """Redis cache falls back to memory on connection error"""
        with patch('backend.core.redis_cache.REDIS_AVAILABLE', True):
            with patch('backend.core.redis_cache.redis') as mock_redis:
                mock_redis.from_url.side_effect = Exception("Connection failed")

                from backend.core.redis_cache import RedisCache
                cache = RedisCache(
                    redis_url="redis://localhost:6379/0",
                    enabled=True
                )

                assert cache._using_redis is False

    @pytest.mark.unit
    def test_redis_cache_disabled(self):
        """Disabled Redis cache returns None"""
        with patch('backend.core.redis_cache.REDIS_AVAILABLE', True):
            from backend.core.redis_cache import RedisCache
            cache = RedisCache(enabled=False)

            result = cache.get("any prompt")

            assert result is None


# ============================================================================
# Thread Safety Tests
# ============================================================================

class TestThreadSafety:
    """Tests for thread safety of cache implementations"""

    @pytest.mark.unit
    def test_lru_cache_concurrent_access(self):
        """LRU cache handles concurrent access"""
        from backend.core.cache import LRUCache

        cache = LRUCache(max_size=100)
        errors = []

        def worker(worker_id):
            try:
                for i in range(50):
                    key = f"key_{worker_id}_{i}"
                    cache.set(key, f"value_{i}")
                    cache.get(key)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    @pytest.mark.unit
    def test_llm_cache_concurrent_access(self):
        """LLM cache handles concurrent access"""
        from backend.core.cache import LLMResponseCache

        cache = LLMResponseCache(ttl_seconds=60, max_entries=100, enabled=True)
        errors = []

        def worker(worker_id):
            try:
                for i in range(50):
                    prompt = f"prompt_{worker_id}_{i}"
                    cache.set(prompt, f"response_{i}")
                    cache.get(prompt)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0

    @pytest.mark.unit
    def test_cache_stats_concurrent_updates(self):
        """Cache stats are thread-safe"""
        from backend.core.cache import LRUCache

        cache = LRUCache(max_size=1000)
        cache.set("shared_key", "value")

        def reader():
            for _ in range(100):
                cache.get("shared_key")
                cache.get("nonexistent")

        threads = [threading.Thread(target=reader) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        stats = cache.get_stats()
        # 5 threads * 100 iterations * 2 requests (1 hit + 1 miss) = 1000 total
        assert stats["total_requests"] == 1000


# ============================================================================
# Singleton Tests
# ============================================================================

class TestCacheSingleton:
    """Tests for cache singleton patterns"""

    @pytest.mark.unit
    def test_get_llm_cache_singleton(self):
        """get_llm_cache returns singleton instance"""
        # Reset global cache for test
        import backend.core.cache as cache_module
        cache_module._global_cache = None

        from backend.core.cache import get_llm_cache

        cache1 = get_llm_cache(ttl_seconds=60, max_entries=100)
        cache2 = get_llm_cache(ttl_seconds=120, max_entries=200)  # Different params

        # Should return same instance
        assert cache1 is cache2

        # Clean up
        cache_module._global_cache = None

    @pytest.mark.unit
    def test_get_redis_cache_singleton(self):
        """get_redis_cache returns singleton instance"""
        # Reset global cache for test
        import backend.core.redis_cache as redis_cache_module
        redis_cache_module._global_redis_cache = None

        with patch('backend.core.redis_cache.REDIS_AVAILABLE', False):
            from backend.core.redis_cache import get_redis_cache

            cache1 = get_redis_cache()
            cache2 = get_redis_cache()

            assert cache1 is cache2

            # Clean up
            redis_cache_module._global_redis_cache = None


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestCacheEdgeCases:
    """Edge cases and error handling tests"""

    @pytest.mark.unit
    def test_empty_prompt(self, llm_cache):
        """Cache handles empty prompt"""
        llm_cache.set("", "response")
        result = llm_cache.get("")

        assert result == "response"

    @pytest.mark.unit
    def test_very_long_prompt(self, llm_cache):
        """Cache handles very long prompts"""
        long_prompt = "A" * 100000
        response = "response"

        llm_cache.set(long_prompt, response)
        result = llm_cache.get(long_prompt)

        assert result == response

    @pytest.mark.unit
    def test_special_json_characters(self, llm_cache):
        """Cache handles special JSON characters in prompt"""
        prompt = '{"code": "print(\\"hello\\")\\n\\ttab"}'
        response = "response"

        llm_cache.set(prompt, response)
        result = llm_cache.get(prompt)

        assert result == response

    @pytest.mark.unit
    def test_null_context(self, llm_cache):
        """Cache handles null/None context"""
        prompt = "test prompt"
        response = "response"

        llm_cache.set(prompt, response, context=None)
        result = llm_cache.get(prompt, context=None)

        assert result == response

    @pytest.mark.unit
    def test_empty_context(self, llm_cache):
        """Cache handles empty context dict"""
        prompt = "test prompt"
        response = "response"

        llm_cache.set(prompt, response, context={})
        result = llm_cache.get(prompt, context={})

        assert result == response

    @pytest.mark.unit
    def test_complex_nested_context(self, llm_cache):
        """Cache handles complex nested context"""
        prompt = "test prompt"
        context = {
            "files": ["main.py", "test.py"],
            "metadata": {
                "user": "student_001",
                "course": "PROG2"
            },
            "flags": [True, False, None]
        }
        response = "response"

        llm_cache.set(prompt, response, context=context)
        result = llm_cache.get(prompt, context=context)

        assert result == response


# ============================================================================
# Sanitization Tests
# ============================================================================

class TestSanitization:
    """Tests for log sanitization functions"""

    @pytest.mark.unit
    def test_sanitize_for_logs_empty(self):
        """Sanitization handles empty text"""
        from backend.core.cache import _sanitize_for_logs

        result = _sanitize_for_logs("")

        assert result == "[empty]"

    @pytest.mark.unit
    def test_sanitize_for_logs_normal(self):
        """Sanitization hashes normal text"""
        from backend.core.cache import _sanitize_for_logs

        text = "Some user prompt with personal info"
        result = _sanitize_for_logs(text)

        # Should contain hash and length, not original text
        assert "content_hash:" in result
        assert "length:" in result
        assert "personal info" not in result

    @pytest.mark.unit
    def test_sanitize_for_logs_consistent(self):
        """Sanitization produces consistent output"""
        from backend.core.cache import _sanitize_for_logs

        text = "Same text"
        result1 = _sanitize_for_logs(text)
        result2 = _sanitize_for_logs(text)

        assert result1 == result2


# ============================================================================
# Integration Tests
# ============================================================================

class TestCacheIntegration:
    """Integration tests for cache system"""

    @pytest.mark.integration
    def test_cache_with_real_redis(self):
        """Test cache with real Redis instance"""
        # This test requires running Redis
        # Skip if Redis not available
        pass

    @pytest.mark.integration
    def test_cache_performance(self, llm_cache):
        """Test cache performance under load"""
        import time

        start = time.time()

        # Write 1000 entries
        for i in range(1000):
            llm_cache.set(f"prompt_{i}", f"response_{i}")

        # Read 1000 entries
        for i in range(1000):
            llm_cache.get(f"prompt_{i}")

        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 5.0  # Less than 5 seconds for 2000 operations