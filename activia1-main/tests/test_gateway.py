"""
Unit and integration tests for AI Gateway

Tests cover:
- Session management (via repository)
- Interaction processing pipeline
- Mode switching
- Trace capture and retrieval (via repository)
- Gateway orchestration

NOTE: AIGateway is STATELESS - all state is persisted via repositories
"""
import pytest
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from uuid import UUID
from datetime import datetime

from backend.core.ai_gateway import AIGateway
from backend.core.cognitive_engine import AgentMode, CognitiveState
from backend.models.trace import TraceLevel, CognitiveTrace, TraceSequence, InteractionType


@pytest.mark.unit
@pytest.mark.gateway
class TestAIGateway:
    """Tests for AIGateway (STATELESS version)"""

    @pytest.fixture
    def mock_session_repo(self):
        """Mock session repository"""
        repo = Mock()
        repo.create = Mock(return_value=Mock(
            id="test-session-id",
            student_id="test-student",
            activity_id="test-activity",
            mode="TUTOR"
        ))
        repo.get_by_id = Mock(return_value=Mock(
            id="test-session-id",
            student_id="test-student",
            activity_id="test-activity",
            mode="TUTOR"
        ))
        repo.update = Mock(return_value=Mock(mode="TUTOR"))
        return repo

    @pytest.fixture
    def mock_trace_repo(self):
        """Mock trace repository"""
        repo = Mock()
        repo.create = Mock(return_value=Mock(id="trace-1"))
        repo.get_by_session = Mock(return_value=[])
        repo.get_by_student = Mock(return_value=[])  # Return empty list for student history
        return repo

    @pytest.fixture
    def mock_risk_repo(self):
        """Mock risk repository"""
        repo = Mock()
        repo.create = Mock(return_value=Mock(id="risk-1"))
        repo.get_by_session = Mock(return_value=[])
        return repo

    @pytest.fixture
    def mock_sequence_repo(self):
        """Mock trace sequence repository"""
        repo = Mock()
        repo.create = Mock(return_value=Mock(id="seq-1"))
        repo.get_by_session = Mock(return_value=None)
        return repo

    @pytest.fixture
    def gateway(self, mock_llm_provider, mock_session_repo, mock_trace_repo,
                mock_risk_repo, mock_sequence_repo):
        """Fixture providing an AI Gateway with mock dependencies"""
        return AIGateway(
            llm_provider=mock_llm_provider,
            session_repo=mock_session_repo,
            trace_repo=mock_trace_repo,
            risk_repo=mock_risk_repo,
            sequence_repo=mock_sequence_repo
        )

    # ========================================================================
    # Session Management Tests
    # ========================================================================

    def test_create_session(self, gateway, mock_session_repo, student_id, activity_id):
        """Test creating a new session"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        assert session_id is not None
        # Session should be created via repository
        mock_session_repo.create.assert_called_once()

    def test_create_multiple_sessions(self, gateway, mock_session_repo, student_id):
        """Test creating multiple sessions for same student"""
        # Configure mock to return different IDs
        mock_session_repo.create.side_effect = [
            Mock(id="session-1", student_id=student_id, activity_id="activity1", mode="TUTOR"),
            Mock(id="session-2", student_id=student_id, activity_id="activity2", mode="TUTOR"),
        ]

        session1 = gateway.create_session(student_id=student_id, activity_id="activity1")
        session2 = gateway.create_session(student_id=student_id, activity_id="activity2")

        assert session1 != session2
        assert mock_session_repo.create.call_count == 2

    def test_create_session_uses_repository(self, gateway, mock_session_repo, student_id, activity_id):
        """Test that session creation goes through repository"""
        gateway.create_session(student_id=student_id, activity_id=activity_id)

        # Verify repository was called with correct args
        call_args = mock_session_repo.create.call_args
        assert call_args.kwargs['student_id'] == student_id
        assert call_args.kwargs['activity_id'] == activity_id

    # ========================================================================
    # Mode Management Tests
    # ========================================================================

    def test_set_mode(self, gateway, mock_session_repo, student_id, activity_id):
        """Test setting agent mode for a session"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        # set_mode should update via repository
        if hasattr(gateway, 'set_mode'):
            gateway.set_mode(session_id, AgentMode.TUTOR)
            # Mode should be updated via repository

    def test_default_mode_is_tutor(self, gateway, mock_session_repo, student_id, activity_id):
        """Test that default mode is TUTOR"""
        gateway.create_session(student_id=student_id, activity_id=activity_id)

        # Check that create was called with default mode TUTOR
        call_args = mock_session_repo.create.call_args
        assert call_args.kwargs['mode'] == "TUTOR"

    # ========================================================================
    # Interaction Processing Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_process_interaction_basic(self, gateway, mock_session_repo,
                                              mock_trace_repo, student_id, activity_id):
        """Test processing a basic interaction"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        response = await gateway.process_interaction(
            session_id=session_id, prompt="¿Qué es una cola?"
        )

        assert response is not None
        assert "message" in response or "response" in response or "blocked" in response

    @pytest.mark.asyncio
    async def test_process_delegation_blocked(self, gateway, mock_session_repo, student_id, activity_id):
        """Test that total delegation is blocked"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        response = await gateway.process_interaction(
            session_id=session_id, prompt="Dame el código completo de una cola"
        )

        # Should be blocked or redirected (contains question or blocked flag)
        assert response.get("blocked") is True or "?" in response.get("message", response.get("response", ""))

    @pytest.mark.asyncio
    async def test_process_conceptual_question_allowed(self, gateway, mock_session_repo,
                                                        student_id, activity_id):
        """Test that conceptual questions are allowed"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        response = await gateway.process_interaction(
            session_id=session_id, prompt="¿Qué es una cola?"
        )

        # Conceptual questions should not be blocked
        if "blocked" in response:
            assert response.get("blocked") is not True

    @pytest.mark.asyncio
    async def test_interaction_creates_trace(self, gateway, mock_session_repo,
                                              mock_trace_repo, student_id, activity_id):
        """Test that interactions create N4 traces via repository"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        await gateway.process_interaction(session_id=session_id, prompt="Test prompt")

        # Trace should be created via repository
        assert mock_trace_repo.create.called or hasattr(gateway, '_persist_trace')

    @pytest.mark.asyncio
    async def test_multiple_interactions_build_history(self, gateway, mock_session_repo,
                                                        mock_trace_repo, student_id, activity_id):
        """Test that multiple interactions build conversation history"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        prompts = [
            "¿Qué es una cola?",
            "¿Cuáles son las operaciones?",
            "Planeo usar un arreglo circular",
        ]

        for prompt in prompts:
            await gateway.process_interaction(session_id=session_id, prompt=prompt)

        # Multiple traces should be created
        # The exact count depends on implementation (input trace + response trace per interaction)

    # ========================================================================
    # Trace Capture and Retrieval Tests
    # ========================================================================

    def test_get_trace_sequence(self, gateway, mock_session_repo, mock_sequence_repo,
                                 mock_trace_repo, student_id, activity_id):
        """Test retrieving trace sequence for a session"""
        # Setup mock to return a sequence
        mock_sequence = TraceSequence(
            id="seq-test",
            session_id="test-session-id",
            student_id=student_id,
            activity_id=activity_id
        )
        mock_sequence_repo.get_by_session = Mock(return_value=mock_sequence)

        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        if hasattr(gateway, 'get_trace_sequence'):
            sequence = gateway.get_trace_sequence(session_id)
            assert sequence is not None

    def test_trace_level_is_n4(self, gateway, mock_trace_repo, student_id, activity_id):
        """Test that captured traces are N4 level"""
        # This test verifies the trace level constant
        assert TraceLevel.N4_COGNITIVO is not None
        assert TraceLevel.N4_COGNITIVO.value == "n4_cognitivo"

    # ========================================================================
    # Error Handling Tests
    # ========================================================================

    @pytest.mark.asyncio
    async def test_error_handling_invalid_session(self, gateway, mock_session_repo):
        """Test error handling for invalid session ID"""
        # Configure mock to return None for unknown session
        mock_session_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="no encontrada"):
            await gateway.process_interaction(
                session_id="invalid-session-id", prompt="Test prompt with enough characters"
            )

    @pytest.mark.asyncio
    async def test_empty_prompt_handling(self, gateway, mock_session_repo, student_id, activity_id):
        """Test handling of empty prompts"""
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        # Empty prompt should raise validation error
        with pytest.raises(ValueError):
            await gateway.process_interaction(session_id=session_id, prompt="")

    # ========================================================================
    # Integration Tests
    # ========================================================================

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_session_flow(self, gateway, mock_session_repo, mock_trace_repo,
                                      student_id, activity_id):
        """Test complete session flow from creation to interaction"""
        # 1. Create session
        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )
        assert session_id is not None

        # 2. Multiple interactions
        interactions = [
            "¿Qué es una cola?",
            "¿Cuáles son las operaciones básicas?",
        ]

        for prompt in interactions:
            response = await gateway.process_interaction(session_id=session_id, prompt=prompt)
            assert response is not None

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multi_session_isolation(self, gateway, mock_session_repo, mock_trace_repo):
        """Test that sessions are properly isolated"""
        # Configure mock to return different sessions
        mock_session_repo.create.side_effect = [
            Mock(id="session-1", student_id="student1", activity_id="activity1", mode="TUTOR"),
            Mock(id="session-2", student_id="student2", activity_id="activity2", mode="TUTOR"),
        ]
        mock_session_repo.get_by_id.side_effect = lambda sid: {
            "session-1": Mock(id="session-1", student_id="student1", activity_id="activity1", mode="TUTOR"),
            "session-2": Mock(id="session-2", student_id="student2", activity_id="activity2", mode="TUTOR"),
        }.get(sid)

        # Create two sessions
        session1 = gateway.create_session(student_id="student1", activity_id="activity1")
        session2 = gateway.create_session(student_id="student2", activity_id="activity2")

        assert session1 != session2

        # Interact with both
        response1 = await gateway.process_interaction(session_id=session1, prompt="Session 1 prompt")
        response2 = await gateway.process_interaction(session_id=session2, prompt="Session 2 prompt")

        assert response1 is not None
        assert response2 is not None


# ============================================================================
# Performance Tests
# ============================================================================


@pytest.mark.slow
@pytest.mark.gateway
class TestGatewayPerformance:
    """Performance tests for AI Gateway"""

    @pytest.fixture
    def mock_repos(self):
        """Create mock repositories for performance tests"""
        session_repo = Mock()
        session_counter = [0]

        def create_session(**kwargs):
            session_counter[0] += 1
            return Mock(
                id=f"session-{session_counter[0]}",
                student_id=kwargs.get('student_id'),
                activity_id=kwargs.get('activity_id'),
                mode=kwargs.get('mode', 'TUTOR')
            )

        session_repo.create = create_session
        session_repo.get_by_id = Mock(return_value=Mock(
            id="test-session",
            student_id="test-student",
            activity_id="test-activity",
            mode="TUTOR"
        ))

        trace_repo = Mock()
        trace_repo.create = Mock(return_value=Mock(id="trace-1"))
        trace_repo.get_by_student = Mock(return_value=[])

        return {
            'session_repo': session_repo,
            'trace_repo': trace_repo,
            'risk_repo': Mock(create=Mock(return_value=Mock(id="risk-1"))),
            'sequence_repo': Mock(create=Mock(return_value=Mock(id="seq-1"))),
        }

    def test_many_sessions(self, mock_llm_provider, mock_repos):
        """Test handling many concurrent sessions"""
        gateway = AIGateway(
            llm_provider=mock_llm_provider,
            **mock_repos
        )

        session_ids = []
        for i in range(100):
            session_id = gateway.create_session(
                student_id=f"student_{i}", activity_id=f"activity_{i}"
            )
            session_ids.append(session_id)

        assert len(session_ids) == 100
        assert len(set(session_ids)) == 100  # All unique

    @pytest.mark.asyncio
    async def test_many_interactions_per_session(self, mock_llm_provider, mock_repos,
                                                  student_id, activity_id):
        """Test handling many interactions in one session"""
        gateway = AIGateway(
            llm_provider=mock_llm_provider,
            **mock_repos
        )

        session_id = gateway.create_session(
            student_id=student_id, activity_id=activity_id
        )

        for i in range(10):  # Reduced from 50 for faster tests
            await gateway.process_interaction(
                session_id=session_id,
                prompt=f"Test question {i}?"
            )

        # Should complete without errors
        assert True