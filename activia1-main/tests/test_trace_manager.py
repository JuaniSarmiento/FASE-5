"""
Tests for TraceManager component

Verifies:
- Input trace capture (N4 level)
- Output trace capture with AI involvement metrics
- Trace sequence creation
- Session trace retrieval
- Trace statistics calculation
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from backend.core.trace_manager import TraceManager
from backend.models.trace import (
    CognitiveTrace,
    TraceSequence,
    TraceLevel,
    InteractionType,
    CognitiveState,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_trace_repo():
    """Mock trace repository"""
    repo = Mock()
    repo.create = Mock(return_value=None)
    repo.get_by_session = Mock(return_value=[])
    repo.get_by_id = Mock(return_value=None)
    return repo


@pytest.fixture
def mock_sequence_repo():
    """Mock trace sequence repository"""
    repo = Mock()
    repo.create = Mock(return_value=None)
    repo.get_by_session = Mock(return_value=None)
    return repo


@pytest.fixture
def mock_traceability_agent():
    """Mock TC-N4 traceability agent"""
    agent = Mock()

    def capture_trace_side_effect(**kwargs):
        return CognitiveTrace(
            id=str(uuid4()),
            session_id=kwargs.get("session_id"),
            student_id=kwargs.get("student_id"),
            activity_id=kwargs.get("activity_id"),
            timestamp=datetime.utcnow(),
            trace_level=kwargs.get("trace_level", TraceLevel.N4_COGNITIVO),
            interaction_type=kwargs.get("interaction_type"),
            cognitive_state=kwargs.get("cognitive_state"),
            content=kwargs.get("content", ""),
            ai_involvement=kwargs.get("ai_involvement", 0.0),
            decision_justification=kwargs.get("decision_justification"),
            alternatives_considered=kwargs.get("alternatives_considered", []),
            agent_id=kwargs.get("agent_id"),
            parent_trace_id=kwargs.get("parent_trace_id"),
            trace_metadata=kwargs.get("metadata", {}),
        )

    agent.capture_trace = Mock(side_effect=capture_trace_side_effect)
    return agent


@pytest.fixture
def trace_manager(mock_trace_repo, mock_sequence_repo, mock_traceability_agent):
    """TraceManager instance with mocked dependencies"""
    return TraceManager(
        trace_repo=mock_trace_repo,
        sequence_repo=mock_sequence_repo,
        traceability_agent=mock_traceability_agent
    )


# ============================================================================
# Initialization Tests
# ============================================================================

class TestTraceManagerInit:
    """Tests for TraceManager initialization"""

    def test_init_with_dependencies(
        self,
        mock_trace_repo,
        mock_sequence_repo,
        mock_traceability_agent
    ):
        """Test initialization with all dependencies"""
        manager = TraceManager(
            trace_repo=mock_trace_repo,
            sequence_repo=mock_sequence_repo,
            traceability_agent=mock_traceability_agent
        )

        assert manager.trace_repo == mock_trace_repo
        assert manager.sequence_repo == mock_sequence_repo
        assert manager.traceability_agent == mock_traceability_agent


# ============================================================================
# Input Trace Capture Tests
# ============================================================================

class TestInputTraceCapture:
    """Tests for capturing input traces from students"""

    def test_capture_input_trace_basic(self, trace_manager, mock_trace_repo):
        """Test basic input trace capture"""
        session_id = str(uuid4())

        trace = trace_manager.capture_input_trace(
            session_id=session_id,
            student_id="student_001",
            activity_id="activity_001",
            prompt="¿Qué es una cola circular?",
            cognitive_state=CognitiveState.EXPLORACION,
            context={"code": "# empty"}
        )

        assert trace is not None
        assert trace.session_id == session_id
        assert trace.student_id == "student_001"
        assert trace.interaction_type == InteractionType.STUDENT_PROMPT
        assert trace.trace_level == TraceLevel.N4_COGNITIVO
        mock_trace_repo.create.assert_called_once()

    def test_capture_input_trace_with_context(
        self,
        trace_manager,
        mock_traceability_agent
    ):
        """Test input trace capture includes context"""
        context = {
            "code_snippet": "def enqueue(self, item):",
            "current_file": "cola.py",
            "line_number": 10
        }

        trace_manager.capture_input_trace(
            session_id=str(uuid4()),
            student_id="student_001",
            activity_id="activity_001",
            prompt="¿Cómo implemento enqueue?",
            cognitive_state=CognitiveState.IMPLEMENTACION,
            context=context
        )

        # Verify agent received context
        call_kwargs = mock_traceability_agent.capture_trace.call_args[1]
        assert call_kwargs["context"] == context

    def test_capture_input_trace_without_context(
        self,
        trace_manager,
        mock_traceability_agent
    ):
        """Test input trace capture without context uses empty dict"""
        trace_manager.capture_input_trace(
            session_id=str(uuid4()),
            student_id="student_001",
            activity_id="activity_001",
            prompt="Pregunta simple",
            cognitive_state=CognitiveState.EXPLORACION,
            context=None
        )

        call_kwargs = mock_traceability_agent.capture_trace.call_args[1]
        assert call_kwargs["context"] == {}

    @pytest.mark.parametrize("cognitive_state", [
        CognitiveState.EXPLORACION,
        CognitiveState.PLANIFICACION,
        CognitiveState.IMPLEMENTACION,
        CognitiveState.VALIDACION,
        CognitiveState.REFLEXION,
    ])
    def test_capture_input_trace_all_cognitive_states(
        self,
        trace_manager,
        cognitive_state
    ):
        """Test input trace capture for all cognitive states"""
        trace = trace_manager.capture_input_trace(
            session_id=str(uuid4()),
            student_id="student_001",
            activity_id="activity_001",
            prompt="Test prompt",
            cognitive_state=cognitive_state
        )

        assert trace.cognitive_state == cognitive_state


# ============================================================================
# Output Trace Capture Tests
# ============================================================================

class TestOutputTraceCapture:
    """Tests for capturing output traces from agents"""

    def test_capture_output_trace_basic(self, trace_manager, mock_trace_repo):
        """Test basic output trace capture"""
        session_id = str(uuid4())
        parent_trace_id = str(uuid4())

        trace = trace_manager.capture_output_trace(
            session_id=session_id,
            student_id="student_001",
            activity_id="activity_001",
            response="Una cola circular es una estructura de datos...",
            agent_used="T-IA-Cog",
            cognitive_state=CognitiveState.EXPLORACION,
            ai_involvement=0.6,
            decision_justification="Respuesta conceptual para fase de exploración",
            alternatives_considered=["Modo socrático", "Modo explicativo"],
            parent_trace_id=parent_trace_id
        )

        assert trace is not None
        assert trace.session_id == session_id
        assert trace.interaction_type == InteractionType.AI_RESPONSE
        assert trace.ai_involvement == 0.6
        mock_trace_repo.create.assert_called_once()

    def test_capture_output_trace_with_high_ai_involvement(
        self,
        trace_manager,
        mock_traceability_agent
    ):
        """Test output trace capture with high AI involvement"""
        trace = trace_manager.capture_output_trace(
            session_id=str(uuid4()),
            student_id="student_001",
            activity_id="activity_001",
            response="Aquí tienes un ejemplo completo...",
            agent_used="T-IA-Cog",
            cognitive_state=CognitiveState.IMPLEMENTACION,
            ai_involvement=0.9
        )

        assert trace.ai_involvement == 0.9

    def test_capture_output_trace_includes_agent_id(
        self,
        trace_manager,
        mock_traceability_agent
    ):
        """Test that agent ID is included in output trace"""
        trace_manager.capture_output_trace(
            session_id=str(uuid4()),
            student_id="student_001",
            activity_id="activity_001",
            response="Response",
            agent_used="E-IA-Proc",
            cognitive_state=CognitiveState.VALIDACION,
            ai_involvement=0.5
        )

        call_kwargs = mock_traceability_agent.capture_trace.call_args[1]
        assert call_kwargs["agent_id"] == "E-IA-Proc"

    def test_capture_output_trace_links_to_parent(
        self,
        trace_manager,
        mock_traceability_agent
    ):
        """Test output trace links to parent input trace"""
        parent_id = str(uuid4())

        trace_manager.capture_output_trace(
            session_id=str(uuid4()),
            student_id="student_001",
            activity_id="activity_001",
            response="Response",
            agent_used="T-IA-Cog",
            cognitive_state=CognitiveState.EXPLORACION,
            ai_involvement=0.3,
            parent_trace_id=parent_id
        )

        call_kwargs = mock_traceability_agent.capture_trace.call_args[1]
        assert call_kwargs["parent_trace_id"] == parent_id


# ============================================================================
# Trace Sequence Tests
# ============================================================================

class TestTraceSequenceCreation:
    """Tests for trace sequence creation"""

    def test_create_trace_sequence_basic(
        self,
        trace_manager,
        mock_sequence_repo
    ):
        """Test basic trace sequence creation"""
        session_id = str(uuid4())
        trace_ids = [str(uuid4()) for _ in range(5)]

        sequence = trace_manager.create_trace_sequence(
            session_id=session_id,
            student_id="student_001",
            activity_id="activity_001",
            trace_ids=trace_ids,
            reasoning_path=["Exploración", "Planificación", "Implementación"],
            strategy_changes=2,
            ai_dependency_score=0.45
        )

        assert sequence is not None
        assert sequence.session_id == session_id
        assert len(sequence.trace_ids) == 5
        assert sequence.strategy_changes == 2
        assert sequence.ai_dependency_score == 0.45
        mock_sequence_repo.create.assert_called_once()

    def test_create_trace_sequence_with_defaults(
        self,
        trace_manager
    ):
        """Test trace sequence creation with default values"""
        sequence = trace_manager.create_trace_sequence(
            session_id=str(uuid4()),
            student_id="student_001",
            activity_id="activity_001",
            trace_ids=["t1", "t2"]
        )

        assert sequence.reasoning_path == []
        assert sequence.strategy_changes == 0
        assert sequence.ai_dependency_score == 0.0

    def test_create_trace_sequence_timestamps(self, trace_manager):
        """Test that sequence includes timestamps"""
        sequence = trace_manager.create_trace_sequence(
            session_id=str(uuid4()),
            student_id="student_001",
            activity_id="activity_001",
            trace_ids=["t1"]
        )

        assert sequence.start_time is not None
        assert sequence.end_time is not None


# ============================================================================
# Session Traces Retrieval Tests
# ============================================================================

class TestSessionTracesRetrieval:
    """Tests for retrieving session traces"""

    def test_get_session_traces_empty(self, trace_manager, mock_trace_repo):
        """Test getting traces from empty session"""
        mock_trace_repo.get_by_session.return_value = []

        traces = trace_manager.get_session_traces("session_001")

        assert traces == []
        mock_trace_repo.get_by_session.assert_called_once_with("session_001")

    def test_get_session_traces_with_data(self, trace_manager, mock_trace_repo):
        """Test getting traces from session with data"""
        mock_traces = [
            CognitiveTrace(
                id=str(uuid4()),
                session_id="session_001",
                student_id="student_001",
                activity_id="activity_001",
                timestamp=datetime.utcnow(),
                trace_level=TraceLevel.N4_COGNITIVO,
                interaction_type=InteractionType.STUDENT_PROMPT,
                cognitive_state=CognitiveState.EXPLORACION,
                content="Question 1",
            ),
            CognitiveTrace(
                id=str(uuid4()),
                session_id="session_001",
                student_id="student_001",
                activity_id="activity_001",
                timestamp=datetime.utcnow(),
                trace_level=TraceLevel.N4_COGNITIVO,
                interaction_type=InteractionType.AI_RESPONSE,
                cognitive_state=CognitiveState.EXPLORACION,
                content="Answer 1",
            ),
        ]
        mock_trace_repo.get_by_session.return_value = mock_traces

        traces = trace_manager.get_session_traces("session_001")

        assert len(traces) == 2

    def test_get_session_traces_with_type_filter(
        self,
        trace_manager,
        mock_trace_repo
    ):
        """Test filtering traces by interaction type"""
        mock_traces = [
            CognitiveTrace(
                id=str(uuid4()),
                session_id="session_001",
                student_id="student_001",
                activity_id="activity_001",
                timestamp=datetime.utcnow(),
                trace_level=TraceLevel.N4_COGNITIVO,
                interaction_type=InteractionType.STUDENT_PROMPT,
                cognitive_state=CognitiveState.EXPLORACION,
                content="Question",
            ),
            CognitiveTrace(
                id=str(uuid4()),
                session_id="session_001",
                student_id="student_001",
                activity_id="activity_001",
                timestamp=datetime.utcnow(),
                trace_level=TraceLevel.N4_COGNITIVO,
                interaction_type=InteractionType.AI_RESPONSE,
                cognitive_state=CognitiveState.EXPLORACION,
                content="Answer",
            ),
        ]
        mock_trace_repo.get_by_session.return_value = mock_traces

        # Filter for student prompts only
        traces = trace_manager.get_session_traces(
            "session_001",
            interaction_type=InteractionType.STUDENT_PROMPT
        )

        assert len(traces) == 1
        assert traces[0].interaction_type == InteractionType.STUDENT_PROMPT


# ============================================================================
# Trace Statistics Tests
# ============================================================================

class TestTraceStatistics:
    """Tests for trace statistics calculation"""

    def test_get_trace_statistics_empty_session(
        self,
        trace_manager,
        mock_trace_repo
    ):
        """Test statistics for empty session"""
        mock_trace_repo.get_by_session.return_value = []

        stats = trace_manager.get_trace_statistics("session_001")

        assert stats["total_traces"] == 0
        assert stats["input_traces"] == 0
        assert stats["output_traces"] == 0
        assert stats["avg_ai_involvement"] == 0.0
        assert stats["cognitive_states"] == []

    def test_get_trace_statistics_with_traces(
        self,
        trace_manager,
        mock_trace_repo
    ):
        """Test statistics calculation with traces"""
        mock_traces = [
            CognitiveTrace(
                id=str(uuid4()),
                session_id="session_001",
                student_id="student_001",
                activity_id="activity_001",
                timestamp=datetime.utcnow(),
                trace_level=TraceLevel.N4_COGNITIVO,
                interaction_type=InteractionType.STUDENT_PROMPT,
                cognitive_state=CognitiveState.EXPLORACION,
                content="Q1",
                ai_involvement=0.2,
            ),
            CognitiveTrace(
                id=str(uuid4()),
                session_id="session_001",
                student_id="student_001",
                activity_id="activity_001",
                timestamp=datetime.utcnow(),
                trace_level=TraceLevel.N4_COGNITIVO,
                interaction_type=InteractionType.AI_RESPONSE,
                cognitive_state=CognitiveState.EXPLORACION,
                content="A1",
                ai_involvement=0.6,
            ),
            CognitiveTrace(
                id=str(uuid4()),
                session_id="session_001",
                student_id="student_001",
                activity_id="activity_001",
                timestamp=datetime.utcnow(),
                trace_level=TraceLevel.N4_COGNITIVO,
                interaction_type=InteractionType.STUDENT_PROMPT,
                cognitive_state=CognitiveState.IMPLEMENTACION,
                content="Q2",
                ai_involvement=0.3,
            ),
            CognitiveTrace(
                id=str(uuid4()),
                session_id="session_001",
                student_id="student_001",
                activity_id="activity_001",
                timestamp=datetime.utcnow(),
                trace_level=TraceLevel.N4_COGNITIVO,
                interaction_type=InteractionType.AI_RESPONSE,
                cognitive_state=CognitiveState.IMPLEMENTACION,
                content="A2",
                ai_involvement=0.5,
            ),
        ]
        mock_trace_repo.get_by_session.return_value = mock_traces

        stats = trace_manager.get_trace_statistics("session_001")

        assert stats["total_traces"] == 4
        assert stats["input_traces"] == 2
        assert stats["output_traces"] == 2
        # avg = (0.2 + 0.6 + 0.3 + 0.5) / 4 = 0.4
        assert stats["avg_ai_involvement"] == 0.4
        assert CognitiveState.EXPLORACION in stats["cognitive_states"]
        assert CognitiveState.IMPLEMENTACION in stats["cognitive_states"]

    def test_get_trace_statistics_unique_cognitive_states(
        self,
        trace_manager,
        mock_trace_repo
    ):
        """Test that cognitive states are unique in statistics"""
        mock_traces = [
            CognitiveTrace(
                id=str(uuid4()),
                session_id="session_001",
                student_id="student_001",
                activity_id="activity_001",
                timestamp=datetime.utcnow(),
                trace_level=TraceLevel.N4_COGNITIVO,
                interaction_type=InteractionType.STUDENT_PROMPT,
                cognitive_state=CognitiveState.EXPLORACION,
                content="Q1",
                ai_involvement=0.3,
            ),
            CognitiveTrace(
                id=str(uuid4()),
                session_id="session_001",
                student_id="student_001",
                activity_id="activity_001",
                timestamp=datetime.utcnow(),
                trace_level=TraceLevel.N4_COGNITIVO,
                interaction_type=InteractionType.AI_RESPONSE,
                cognitive_state=CognitiveState.EXPLORACION,  # Same state
                content="A1",
                ai_involvement=0.5,
            ),
        ]
        mock_trace_repo.get_by_session.return_value = mock_traces

        stats = trace_manager.get_trace_statistics("session_001")

        # Should have only one unique cognitive state
        assert len(stats["cognitive_states"]) == 1


# ============================================================================
# Integration Tests
# ============================================================================

class TestTraceManagerIntegration:
    """Integration tests for TraceManager"""

    def test_full_interaction_flow(
        self,
        trace_manager,
        mock_trace_repo,
        mock_sequence_repo
    ):
        """Test complete flow: input -> output -> sequence"""
        session_id = str(uuid4())

        # 1. Capture input trace
        input_trace = trace_manager.capture_input_trace(
            session_id=session_id,
            student_id="student_001",
            activity_id="activity_001",
            prompt="¿Cómo implemento una cola?",
            cognitive_state=CognitiveState.PLANIFICACION
        )

        # 2. Capture output trace
        output_trace = trace_manager.capture_output_trace(
            session_id=session_id,
            student_id="student_001",
            activity_id="activity_001",
            response="Para implementar una cola, primero piensa en...",
            agent_used="T-IA-Cog",
            cognitive_state=CognitiveState.PLANIFICACION,
            ai_involvement=0.4,
            parent_trace_id=input_trace.id
        )

        # 3. Create sequence
        sequence = trace_manager.create_trace_sequence(
            session_id=session_id,
            student_id="student_001",
            activity_id="activity_001",
            trace_ids=[input_trace.id, output_trace.id],
            reasoning_path=["Planificación"],
            ai_dependency_score=0.4
        )

        # Verify all components were created and persisted
        assert mock_trace_repo.create.call_count == 2
        assert mock_sequence_repo.create.call_count == 1
        assert len(sequence.trace_ids) == 2

    def test_multiple_interactions_in_session(
        self,
        trace_manager,
        mock_trace_repo
    ):
        """Test multiple interactions in a single session"""
        session_id = str(uuid4())
        trace_ids = []

        # Simulate 3 interaction pairs
        for i in range(3):
            input_trace = trace_manager.capture_input_trace(
                session_id=session_id,
                student_id="student_001",
                activity_id="activity_001",
                prompt=f"Question {i}",
                cognitive_state=CognitiveState.IMPLEMENTACION
            )
            trace_ids.append(input_trace.id)

            output_trace = trace_manager.capture_output_trace(
                session_id=session_id,
                student_id="student_001",
                activity_id="activity_001",
                response=f"Answer {i}",
                agent_used="T-IA-Cog",
                cognitive_state=CognitiveState.IMPLEMENTACION,
                ai_involvement=0.5,
                parent_trace_id=input_trace.id
            )
            trace_ids.append(output_trace.id)

        # 6 traces total (3 pairs)
        assert mock_trace_repo.create.call_count == 6
        assert len(trace_ids) == 6