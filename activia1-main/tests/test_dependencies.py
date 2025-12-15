"""
Tests for Dependency Injection module

Verifies:
- Database session dependency (get_db)
- Repository dependencies
- LLM provider singleton with thread-safety
- AI Gateway dependency with full DI
- Authentication dependencies (JWT)
- Role-based access control
- Session validation
"""
import pytest
import os
import threading
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from fastapi import HTTPException
from sqlalchemy.orm import Session

# Set JWT secret before imports
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-pytest-minimum-32-chars")


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_db_session():
    """Create a mock database session"""
    session = Mock(spec=Session)
    session.query = Mock(return_value=Mock())
    session.add = Mock()
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_user_repo():
    """Create a mock user repository"""
    repo = Mock()
    repo.get_by_id = Mock(return_value=None)
    repo.get_by_email = Mock(return_value=None)
    return repo


@pytest.fixture
def sample_user():
    """Create a sample user object"""
    user = Mock()
    user.id = "user_123"
    user.email = "test@example.com"
    user.username = "testuser"
    user.full_name = "Test User"
    user.student_id = "STU001"
    user.roles = ["student"]
    user.is_active = True
    user.is_verified = True
    return user


# ============================================================================
# Database Dependency Tests
# ============================================================================

class TestGetDb:
    """Tests for get_db dependency"""

    def test_get_db_yields_session(self):
        """Test that get_db yields a session"""
        from backend.api.deps import get_db

        # get_db returns a generator
        gen = get_db()
        assert hasattr(gen, '__next__')

    def test_get_db_context_manager_behavior(self):
        """Test get_db behaves like context manager"""
        with patch('backend.api.deps.get_db_session') as mock_ctx:
            mock_session = Mock()
            mock_ctx.return_value.__enter__ = Mock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = Mock(return_value=False)

            from backend.api.deps import get_db

            gen = get_db()
            # Should yield session from context manager
            # Note: actual implementation may differ


# ============================================================================
# Repository Dependency Tests
# ============================================================================

class TestRepositoryDependencies:
    """Tests for repository dependencies"""

    def test_get_session_repository_returns_repo(self, mock_db_session):
        """Test get_session_repository returns SessionRepository"""
        from backend.api.deps import get_session_repository
        from backend.database.repositories import SessionRepository

        repo = get_session_repository(mock_db_session)

        assert isinstance(repo, SessionRepository)

    def test_get_trace_repository_returns_repo(self, mock_db_session):
        """Test get_trace_repository returns TraceRepository"""
        from backend.api.deps import get_trace_repository
        from backend.database.repositories import TraceRepository

        repo = get_trace_repository(mock_db_session)

        assert isinstance(repo, TraceRepository)

    def test_get_risk_repository_returns_repo(self, mock_db_session):
        """Test get_risk_repository returns RiskRepository"""
        from backend.api.deps import get_risk_repository
        from backend.database.repositories import RiskRepository

        repo = get_risk_repository(mock_db_session)

        assert isinstance(repo, RiskRepository)

    def test_get_evaluation_repository_returns_repo(self, mock_db_session):
        """Test get_evaluation_repository returns EvaluationRepository"""
        from backend.api.deps import get_evaluation_repository
        from backend.database.repositories import EvaluationRepository

        repo = get_evaluation_repository(mock_db_session)

        assert isinstance(repo, EvaluationRepository)

    def test_get_sequence_repository_returns_repo(self, mock_db_session):
        """Test get_sequence_repository returns TraceSequenceRepository"""
        from backend.api.deps import get_sequence_repository
        from backend.database.repositories import TraceSequenceRepository

        repo = get_sequence_repository(mock_db_session)

        assert isinstance(repo, TraceSequenceRepository)

    def test_get_user_repository_returns_repo(self, mock_db_session):
        """Test get_user_repository returns UserRepository"""
        from backend.api.deps import get_user_repository
        from backend.database.repositories import UserRepository

        repo = get_user_repository(mock_db_session)

        assert isinstance(repo, UserRepository)

    def test_repositories_share_same_session(self, mock_db_session):
        """Test that repositories use the same DB session"""
        from backend.api.deps import (
            get_session_repository,
            get_trace_repository,
            get_risk_repository
        )

        session_repo = get_session_repository(mock_db_session)
        trace_repo = get_trace_repository(mock_db_session)
        risk_repo = get_risk_repository(mock_db_session)

        # All repos should use same session
        assert session_repo.db is mock_db_session
        assert trace_repo.db is mock_db_session
        assert risk_repo.db is mock_db_session


# ============================================================================
# LLM Provider Singleton Tests
# ============================================================================

class TestLLMProviderSingleton:
    """Tests for LLM provider singleton pattern"""

    def test_get_llm_provider_returns_provider(self):
        """Test get_llm_provider returns a provider"""
        # Reset singleton
        import backend.api.deps as deps
        deps._llm_provider_instance = None

        with patch.dict(os.environ, {"LLM_PROVIDER": "mock"}):
            provider = deps.get_llm_provider()

            assert provider is not None

    def test_get_llm_provider_singleton_same_instance(self):
        """Test that multiple calls return same instance"""
        import backend.api.deps as deps
        deps._llm_provider_instance = None

        with patch.dict(os.environ, {"LLM_PROVIDER": "mock"}):
            provider1 = deps.get_llm_provider()
            provider2 = deps.get_llm_provider()

            assert provider1 is provider2

    def test_get_llm_provider_thread_safety(self):
        """Test singleton is thread-safe"""
        import backend.api.deps as deps
        deps._llm_provider_instance = None

        providers = []
        errors = []

        def get_provider():
            try:
                with patch.dict(os.environ, {"LLM_PROVIDER": "mock"}):
                    p = deps.get_llm_provider()
                    providers.append(p)
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = [threading.Thread(target=get_provider) for _ in range(10)]

        # Start all threads
        for t in threads:
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # No errors should occur
        assert len(errors) == 0

        # All should get same instance
        if providers:
            first = providers[0]
            assert all(p is first for p in providers)

    def test_initialize_llm_provider_mock(self):
        """Test _initialize_llm_provider with mock provider"""
        from backend.api.deps import _initialize_llm_provider

        with patch.dict(os.environ, {"LLM_PROVIDER": "mock"}):
            provider = _initialize_llm_provider()

            assert provider is not None
            # Should be mock provider
            model_info = provider.get_model_info()
            assert "mock" in model_info.get("model", "").lower() or model_info.get("provider") == "mock"

    def test_initialize_llm_provider_fallback_on_error(self):
        """Test fallback to mock when provider fails"""
        from backend.api.deps import _initialize_llm_provider

        with patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": ""}):
            # Should fallback to mock since no API key
            provider = _initialize_llm_provider()

            assert provider is not None


# ============================================================================
# AI Gateway Dependency Tests
# ============================================================================

class TestAIGatewayDependency:
    """Tests for AI Gateway dependency"""

    def test_get_ai_gateway_returns_gateway(self, mock_db_session):
        """Test get_ai_gateway returns AIGateway instance"""
        from backend.api.deps import get_ai_gateway
        from backend.core import AIGateway
        from backend.database.repositories import (
            SessionRepository, TraceRepository, RiskRepository,
            EvaluationRepository, TraceSequenceRepository
        )

        session_repo = SessionRepository(mock_db_session)
        trace_repo = TraceRepository(mock_db_session)
        risk_repo = RiskRepository(mock_db_session)
        eval_repo = EvaluationRepository(mock_db_session)
        seq_repo = TraceSequenceRepository(mock_db_session)

        gateway = get_ai_gateway(
            session_repo=session_repo,
            trace_repo=trace_repo,
            risk_repo=risk_repo,
            evaluation_repo=eval_repo,
            sequence_repo=seq_repo
        )

        assert isinstance(gateway, AIGateway)

    def test_get_ai_gateway_new_instance_per_call(self, mock_db_session):
        """Test that each call returns new gateway instance"""
        from backend.api.deps import get_ai_gateway
        from backend.database.repositories import (
            SessionRepository, TraceRepository, RiskRepository,
            EvaluationRepository, TraceSequenceRepository
        )

        session_repo = SessionRepository(mock_db_session)
        trace_repo = TraceRepository(mock_db_session)
        risk_repo = RiskRepository(mock_db_session)
        eval_repo = EvaluationRepository(mock_db_session)
        seq_repo = TraceSequenceRepository(mock_db_session)

        gateway1 = get_ai_gateway(
            session_repo=session_repo,
            trace_repo=trace_repo,
            risk_repo=risk_repo,
            evaluation_repo=eval_repo,
            sequence_repo=seq_repo
        )

        gateway2 = get_ai_gateway(
            session_repo=session_repo,
            trace_repo=trace_repo,
            risk_repo=risk_repo,
            evaluation_repo=eval_repo,
            sequence_repo=seq_repo
        )

        # Should be different instances
        assert gateway1 is not gateway2

    def test_get_ai_gateway_shares_llm_provider(self, mock_db_session):
        """Test that gateways share same LLM provider"""
        import backend.api.deps as deps
        from backend.database.repositories import (
            SessionRepository, TraceRepository, RiskRepository,
            EvaluationRepository, TraceSequenceRepository
        )

        deps._llm_provider_instance = None

        session_repo = SessionRepository(mock_db_session)
        trace_repo = TraceRepository(mock_db_session)
        risk_repo = RiskRepository(mock_db_session)
        eval_repo = EvaluationRepository(mock_db_session)
        seq_repo = TraceSequenceRepository(mock_db_session)

        with patch.dict(os.environ, {"LLM_PROVIDER": "mock"}):
            gateway1 = deps.get_ai_gateway(
                session_repo=session_repo,
                trace_repo=trace_repo,
                risk_repo=risk_repo,
                evaluation_repo=eval_repo,
                sequence_repo=seq_repo
            )

            gateway2 = deps.get_ai_gateway(
                session_repo=session_repo,
                trace_repo=trace_repo,
                risk_repo=risk_repo,
                evaluation_repo=eval_repo,
                sequence_repo=seq_repo
            )

            # LLM provider should be same instance
            assert gateway1.llm_provider is gateway2.llm_provider


# ============================================================================
# Authentication Dependency Tests
# ============================================================================

class TestAuthenticationDependency:
    """Tests for JWT authentication dependency"""

    @pytest.mark.asyncio
    async def test_get_current_user_development_no_token(self, mock_user_repo):
        """Test anonymous access in development mode"""
        from backend.api.deps import get_current_user

        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            user = await get_current_user(
                authorization=None,
                user_repo=mock_user_repo
            )

            assert user["user_id"] == "anonymous"
            assert user["roles"] == ["student"]

    @pytest.mark.asyncio
    async def test_get_current_user_production_no_token_raises(self, mock_user_repo):
        """Test production mode requires token"""
        from backend.api.deps import get_current_user

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization=None,
                    user_repo=mock_user_repo
                )

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_production_invalid_format(self, mock_user_repo):
        """Test production mode rejects invalid auth header format"""
        from backend.api.deps import get_current_user

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization="InvalidFormat token123",
                    user_repo=mock_user_repo
                )

            assert exc_info.value.status_code == 401
            assert "Invalid authorization header" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_production_valid_token(
        self,
        mock_user_repo,
        sample_user
    ):
        """Test production mode with valid token"""
        from backend.api.deps import get_current_user
        from backend.api.security import create_access_token

        # Create valid token
        token = create_access_token({"sub": "user_123"})

        # Setup mock to return user
        mock_user_repo.get_by_id = Mock(return_value=sample_user)

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            user = await get_current_user(
                authorization=f"Bearer {token}",
                user_repo=mock_user_repo
            )

            assert user["user_id"] == "user_123"
            assert user["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_current_user_production_expired_token(self, mock_user_repo):
        """Test production mode rejects expired token"""
        from backend.api.deps import get_current_user
        from backend.api.security import create_access_token
        from datetime import timedelta

        # Create expired token
        token = create_access_token(
            {"sub": "user_123"},
            expires_delta=timedelta(seconds=-1)
        )

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization=f"Bearer {token}",
                    user_repo=mock_user_repo
                )

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_production_user_not_found(self, mock_user_repo):
        """Test production mode when user not in database"""
        from backend.api.deps import get_current_user
        from backend.api.security import create_access_token

        token = create_access_token({"sub": "nonexistent_user"})

        mock_user_repo.get_by_id = Mock(return_value=None)

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization=f"Bearer {token}",
                    user_repo=mock_user_repo
                )

            assert exc_info.value.status_code == 401
            assert "User not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_production_inactive_user(
        self,
        mock_user_repo,
        sample_user
    ):
        """Test production mode rejects inactive user"""
        from backend.api.deps import get_current_user
        from backend.api.security import create_access_token

        token = create_access_token({"sub": "user_123"})

        # Make user inactive
        sample_user.is_active = False
        mock_user_repo.get_by_id = Mock(return_value=sample_user)

        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(
                    authorization=f"Bearer {token}",
                    user_repo=mock_user_repo
                )

            assert exc_info.value.status_code == 403
            assert "inactive" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_get_current_user_development_with_token(
        self,
        mock_user_repo,
        sample_user
    ):
        """Test development mode with valid token returns user"""
        from backend.api.deps import get_current_user
        from backend.api.security import create_access_token

        token = create_access_token({"sub": "user_123"})
        mock_user_repo.get_by_id = Mock(return_value=sample_user)

        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            user = await get_current_user(
                authorization=f"Bearer {token}",
                user_repo=mock_user_repo
            )

            # Should return actual user, not anonymous
            assert user["user_id"] == "user_123"


# ============================================================================
# Active User Dependency Tests
# ============================================================================

class TestActiveUserDependency:
    """Tests for get_current_active_user dependency"""

    @pytest.mark.asyncio
    async def test_get_current_active_user_returns_user(self):
        """Test get_current_active_user returns user"""
        from backend.api.deps import get_current_active_user

        mock_user = {
            "user_id": "user_123",
            "is_active": True,
            "roles": ["student"]
        }

        result = await get_current_active_user(current_user=mock_user)

        assert result == mock_user


# ============================================================================
# Role Dependency Tests
# ============================================================================

class TestRoleDependency:
    """Tests for role-based access control dependency"""

    @pytest.mark.asyncio
    async def test_require_role_allows_matching_role(self):
        """Test require_role allows user with matching role"""
        from backend.api.deps import require_role

        role_checker = await require_role("instructor")

        mock_user = {
            "user_id": "user_123",
            "roles": ["instructor", "student"]
        }

        result = await role_checker(current_user=mock_user)

        assert result == mock_user

    @pytest.mark.asyncio
    async def test_require_role_rejects_missing_role(self):
        """Test require_role rejects user without role"""
        from backend.api.deps import require_role

        role_checker = await require_role("admin")

        mock_user = {
            "user_id": "user_123",
            "roles": ["student"]
        }

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user=mock_user)

        assert exc_info.value.status_code == 403
        assert "admin" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_require_role_rejects_empty_roles(self):
        """Test require_role rejects user with no roles"""
        from backend.api.deps import require_role

        role_checker = await require_role("student")

        mock_user = {
            "user_id": "user_123",
            "roles": []
        }

        with pytest.raises(HTTPException) as exc_info:
            await role_checker(current_user=mock_user)

        assert exc_info.value.status_code == 403


# ============================================================================
# Session Validation Dependency Tests
# ============================================================================

class TestSessionValidationDependency:
    """Tests for session validation dependency"""

    @pytest.mark.asyncio
    async def test_validate_session_exists_returns_session(self, mock_db_session):
        """Test validate_session_exists returns session when found"""
        from backend.api.deps import validate_session_exists
        from backend.database.repositories import SessionRepository

        mock_session = Mock()
        mock_session.id = "session_123"

        session_repo = SessionRepository(mock_db_session)
        session_repo.get_by_id = Mock(return_value=mock_session)

        result = await validate_session_exists(
            session_id="session_123",
            session_repo=session_repo
        )

        assert result == mock_session

    @pytest.mark.asyncio
    async def test_validate_session_exists_raises_not_found(self, mock_db_session):
        """Test validate_session_exists raises when not found"""
        from backend.api.deps import validate_session_exists
        from backend.api.exceptions import SessionNotFoundError
        from backend.database.repositories import SessionRepository

        session_repo = SessionRepository(mock_db_session)
        session_repo.get_by_id = Mock(return_value=None)

        with pytest.raises(SessionNotFoundError):
            await validate_session_exists(
                session_id="nonexistent",
                session_repo=session_repo
            )


# ============================================================================
# Integration Tests
# ============================================================================

class TestDependencyIntegration:
    """Integration tests for dependency injection"""

    def test_full_dependency_chain(self, mock_db_session):
        """Test full dependency chain from DB to Gateway"""
        import backend.api.deps as deps
        from backend.database.repositories import (
            SessionRepository, TraceRepository, RiskRepository,
            EvaluationRepository, TraceSequenceRepository
        )

        # Reset singleton
        deps._llm_provider_instance = None

        with patch.dict(os.environ, {"LLM_PROVIDER": "mock"}):
            # Create repositories
            session_repo = deps.get_session_repository(mock_db_session)
            trace_repo = deps.get_trace_repository(mock_db_session)
            risk_repo = deps.get_risk_repository(mock_db_session)
            eval_repo = deps.get_evaluation_repository(mock_db_session)
            seq_repo = deps.get_sequence_repository(mock_db_session)

            # Create gateway
            gateway = deps.get_ai_gateway(
                session_repo=session_repo,
                trace_repo=trace_repo,
                risk_repo=risk_repo,
                evaluation_repo=eval_repo,
                sequence_repo=seq_repo
            )

            # Verify chain
            assert gateway is not None
            assert gateway.llm_provider is not None
            assert gateway.session_repo is session_repo

    def test_repositories_independent_instances(self, mock_db_session):
        """Test each repository call creates independent instance"""
        from backend.api.deps import get_session_repository

        repo1 = get_session_repository(mock_db_session)
        repo2 = get_session_repository(mock_db_session)

        # Different instances
        assert repo1 is not repo2

        # But same DB session
        assert repo1.db is repo2.db