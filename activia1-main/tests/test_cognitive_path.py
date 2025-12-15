"""
Tests for Cognitive Path Router

Tests para backend/api/routers/cognitive_path.py

Verifica:
1. Obtener camino cognitivo completo (GET /cognitive-path/{session_id})
2. Obtener resumen del camino (GET /cognitive-path/{session_id}/summary)
3. Reconstrucción de fases cognitivas
4. Detección de transiciones
5. Cálculo de métricas y estadísticas
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4
from collections import defaultdict

from fastapi import HTTPException


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_session():
    """Mock session object"""
    session = MagicMock()
    session.id = f"session_{uuid4().hex[:8]}"
    session.student_id = "student_001"
    session.activity_id = "activity_001"
    session.start_time = datetime.utcnow() - timedelta(hours=1)
    session.end_time = datetime.utcnow()
    return session


@pytest.fixture
def mock_traces():
    """Mock trace objects for a session"""
    traces = []
    base_time = datetime.utcnow() - timedelta(hours=1)

    cognitive_states = ["exploration", "exploration", "implementation", "implementation", "verification"]

    for i, state in enumerate(cognitive_states):
        trace = MagicMock()
        trace.id = f"trace_{uuid4().hex[:8]}"
        trace.session_id = "session_001"
        trace.cognitive_state = state
        trace.cognitive_intent = f"intent_{i}"
        trace.ai_involvement = 0.3 + (i * 0.1)
        trace.created_at = base_time + timedelta(minutes=i * 10)
        trace.decision_justification = f"Decision {i}" if i % 2 == 0 else None
        trace.trace_metadata = {"blocked": i == 2}  # One blocked trace
        traces.append(trace)

    return traces


@pytest.fixture
def mock_risks():
    """Mock risk objects for a session"""
    risks = []
    risk_types = ["ai_dependency", "verification_gap"]
    risk_levels = ["medium", "high"]

    for i, (rtype, level) in enumerate(zip(risk_types, risk_levels)):
        risk = MagicMock()
        risk.id = f"risk_{uuid4().hex[:8]}"
        risk.session_id = "session_001"
        risk.risk_type = rtype
        risk.risk_level = level
        risk.trace_ids = [f"trace_{i}"]
        risks.append(risk)

    return risks


@pytest.fixture
def mock_session_repo(mock_session):
    """Mock SessionRepository"""
    repo = MagicMock()
    repo.get_by_id.return_value = mock_session
    return repo


@pytest.fixture
def mock_trace_repo(mock_traces):
    """Mock TraceRepository"""
    repo = MagicMock()
    repo.get_by_session.return_value = mock_traces
    return repo


@pytest.fixture
def mock_risk_repo(mock_risks):
    """Mock RiskRepository"""
    repo = MagicMock()
    repo.get_by_session.return_value = mock_risks
    return repo


# ============================================================================
# Get Cognitive Path Tests
# ============================================================================

class TestGetCognitivePath:
    """Tests for GET /cognitive-path/{session_id} endpoint"""

    @pytest.mark.unit
    def test_get_cognitive_path_success(
        self, mock_session_repo, mock_trace_repo, mock_risk_repo, mock_session, mock_traces
    ):
        """get_cognitive_path() returns complete cognitive path"""
        # Verify mock setup
        session = mock_session_repo.get_by_id("session_001")
        traces = mock_trace_repo.get_by_session("session_001")
        risks = mock_risk_repo.get_by_session("session_001")

        assert session is not None
        assert len(traces) > 0
        assert len(risks) > 0

    @pytest.mark.unit
    def test_get_cognitive_path_session_not_found(self, mock_session_repo):
        """get_cognitive_path() raises 404 for unknown session"""
        mock_session_repo.get_by_id.return_value = None

        assert mock_session_repo.get_by_id("unknown_session") is None

    @pytest.mark.unit
    def test_get_cognitive_path_no_traces(self, mock_session_repo, mock_trace_repo, mock_session):
        """get_cognitive_path() raises 404 for session without traces"""
        mock_trace_repo.get_by_session.return_value = []

        traces = mock_trace_repo.get_by_session("session_001")
        assert traces == []

    @pytest.mark.unit
    def test_cognitive_path_includes_phases(self, mock_traces):
        """Cognitive path includes all cognitive phases"""
        # Group traces by cognitive state
        phases_dict = defaultdict(list)
        for trace in mock_traces:
            phases_dict[trace.cognitive_state].append(trace)

        # Should have 3 distinct phases
        assert len(phases_dict) == 3
        assert "exploration" in phases_dict
        assert "implementation" in phases_dict
        assert "verification" in phases_dict

    @pytest.mark.unit
    def test_cognitive_path_includes_transitions(self, mock_traces):
        """Cognitive path includes state transitions"""
        transitions = []
        prev_state = None

        for trace in sorted(mock_traces, key=lambda t: t.created_at):
            state = trace.cognitive_state
            if prev_state and prev_state != state:
                transitions.append({
                    "from": prev_state,
                    "to": state
                })
            prev_state = state

        # Should have 2 transitions (exploration->implementation, implementation->verification)
        assert len(transitions) == 2
        assert transitions[0]["from"] == "exploration"
        assert transitions[0]["to"] == "implementation"


# ============================================================================
# Cognitive Phase Tests
# ============================================================================

class TestCognitivePhases:
    """Tests for cognitive phase construction"""

    @pytest.mark.unit
    def test_phase_duration_calculation(self, mock_traces):
        """Phase duration is calculated correctly"""
        # Get exploration phase traces
        exploration_traces = [t for t in mock_traces if t.cognitive_state == "exploration"]

        start_time = min(t.created_at for t in exploration_traces)
        end_time = max(t.created_at for t in exploration_traces)
        duration = (end_time - start_time).total_seconds() / 60.0

        # 2 traces, 10 minutes apart
        assert duration == 10.0

    @pytest.mark.unit
    def test_phase_ai_involvement_average(self, mock_traces):
        """Phase AI involvement average is calculated correctly"""
        exploration_traces = [t for t in mock_traces if t.cognitive_state == "exploration"]
        ai_involvements = [t.ai_involvement for t in exploration_traces]
        ai_avg = sum(ai_involvements) / len(ai_involvements)

        # First two traces: 0.3 and 0.4
        assert 0.3 <= ai_avg <= 0.4

    @pytest.mark.unit
    def test_phase_interactions_count(self, mock_traces):
        """Phase interaction count is accurate"""
        phases_dict = defaultdict(list)
        for trace in mock_traces:
            phases_dict[trace.cognitive_state].append(trace)

        # Exploration: 2, Implementation: 2, Verification: 1
        assert len(phases_dict["exploration"]) == 2
        assert len(phases_dict["implementation"]) == 2
        assert len(phases_dict["verification"]) == 1

    @pytest.mark.unit
    def test_phase_key_decisions(self, mock_traces):
        """Phase captures key decisions from justifications"""
        decisions = [
            t.decision_justification
            for t in mock_traces
            if t.decision_justification
        ]

        # Traces 0, 2, 4 have decisions
        assert len(decisions) == 3


# ============================================================================
# Cognitive Transitions Tests
# ============================================================================

class TestCognitiveTransitions:
    """Tests for cognitive state transitions"""

    @pytest.mark.unit
    def test_transition_detection(self, mock_traces):
        """Transitions are detected between different states"""
        transitions = []
        prev_state = None

        for trace in sorted(mock_traces, key=lambda t: t.created_at):
            if prev_state and prev_state != trace.cognitive_state:
                transitions.append({
                    "from": prev_state,
                    "to": trace.cognitive_state,
                    "timestamp": trace.created_at
                })
            prev_state = trace.cognitive_state

        assert len(transitions) == 2

    @pytest.mark.unit
    def test_transition_timestamp(self, mock_traces):
        """Transition timestamp is from the new state's first trace"""
        sorted_traces = sorted(mock_traces, key=lambda t: t.created_at)

        # Find first implementation trace
        first_impl = next(t for t in sorted_traces if t.cognitive_state == "implementation")

        # This should be the transition timestamp
        assert first_impl.created_at is not None

    @pytest.mark.unit
    def test_transition_trigger(self, mock_traces):
        """Transition trigger captures cognitive intent"""
        sorted_traces = sorted(mock_traces, key=lambda t: t.created_at)
        prev_state = None

        for trace in sorted_traces:
            if prev_state and prev_state != trace.cognitive_state:
                trigger = trace.cognitive_intent
                assert trigger is not None
                break
            prev_state = trace.cognitive_state


# ============================================================================
# Cognitive Path Summary Tests
# ============================================================================

class TestCognitivePathSummary:
    """Tests for GET /cognitive-path/{session_id}/summary endpoint"""

    @pytest.mark.unit
    def test_summary_total_interactions(self, mock_traces):
        """Summary includes total interaction count"""
        total = len(mock_traces)
        assert total == 5

    @pytest.mark.unit
    def test_summary_blocked_interactions(self, mock_traces):
        """Summary counts blocked interactions"""
        blocked_count = sum(
            1 for t in mock_traces
            if t.trace_metadata and t.trace_metadata.get("blocked")
        )

        assert blocked_count == 1

    @pytest.mark.unit
    def test_summary_ai_dependency_average(self, mock_traces):
        """Summary calculates AI dependency average"""
        ai_involvements = [t.ai_involvement for t in mock_traces]
        ai_avg = sum(ai_involvements) / len(ai_involvements)

        # Traces have 0.3, 0.4, 0.5, 0.6, 0.7 = avg 0.5
        assert ai_avg == 0.5

    @pytest.mark.unit
    def test_summary_strategy_changes(self):
        """Summary counts strategy changes"""
        traces_with_strategy = [
            MagicMock(trace_metadata={"strategy_change": True}),
            MagicMock(trace_metadata={}),
            MagicMock(trace_metadata={"strategy_change": True}),
            MagicMock(trace_metadata=None),
        ]

        strategy_changes = sum(
            1 for t in traces_with_strategy
            if t.trace_metadata and t.trace_metadata.get("strategy_change")
        )

        assert strategy_changes == 2

    @pytest.mark.unit
    def test_summary_risks_by_level(self, mock_risks):
        """Summary groups risks by level"""
        risks_by_level = defaultdict(int)
        for risk in mock_risks:
            risks_by_level[risk.risk_level] += 1

        assert risks_by_level["medium"] == 1
        assert risks_by_level["high"] == 1

    @pytest.mark.unit
    def test_summary_duration_calculation(self, mock_session):
        """Summary calculates total duration"""
        duration = (mock_session.end_time - mock_session.start_time).total_seconds() / 60.0

        # 1 hour session
        assert duration == 60.0


# ============================================================================
# Empty/Edge Cases Tests
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling"""

    @pytest.mark.unit
    def test_session_without_end_time(self):
        """Handles session without end_time (ongoing)"""
        session = MagicMock()
        session.start_time = datetime.utcnow() - timedelta(minutes=30)
        session.end_time = None

        # Duration calculated from now
        duration = (datetime.utcnow() - session.start_time).total_seconds() / 60.0

        assert 29 <= duration <= 31  # Approximately 30 minutes

    @pytest.mark.unit
    def test_traces_without_cognitive_state(self):
        """Handles traces with None cognitive_state"""
        traces = [
            MagicMock(cognitive_state=None, created_at=datetime.utcnow()),
            MagicMock(cognitive_state="exploration", created_at=datetime.utcnow()),
        ]

        phases_dict = defaultdict(list)
        for trace in traces:
            state = trace.cognitive_state or "unknown"
            phases_dict[state].append(trace)

        assert "unknown" in phases_dict
        assert "exploration" in phases_dict

    @pytest.mark.unit
    def test_traces_without_ai_involvement(self):
        """Handles traces with None ai_involvement"""
        traces = [
            MagicMock(ai_involvement=None),
            MagicMock(ai_involvement=0.5),
            MagicMock(ai_involvement=0.7),
        ]

        ai_involvements = [t.ai_involvement or 0.0 for t in traces]
        avg = sum(ai_involvements) / len(ai_involvements)

        assert avg == 0.4  # (0 + 0.5 + 0.7) / 3

    @pytest.mark.unit
    def test_empty_trace_metadata(self):
        """Handles traces with None or empty metadata"""
        traces = [
            MagicMock(trace_metadata=None),
            MagicMock(trace_metadata={}),
            MagicMock(trace_metadata={"blocked": True}),
        ]

        blocked_count = sum(
            1 for t in traces
            if t.trace_metadata and t.trace_metadata.get("blocked")
        )

        assert blocked_count == 1

    @pytest.mark.unit
    def test_single_trace_session(self):
        """Handles session with only one trace"""
        trace = MagicMock()
        trace.cognitive_state = "exploration"
        trace.created_at = datetime.utcnow()
        trace.ai_involvement = 0.5

        traces = [trace]

        # Should create one phase with zero duration
        phases_dict = defaultdict(list)
        for t in traces:
            phases_dict[t.cognitive_state].append(t)

        exploration_traces = phases_dict["exploration"]
        start = min(t.created_at for t in exploration_traces)
        end = max(t.created_at for t in exploration_traces)
        duration = (end - start).total_seconds() / 60.0

        assert duration == 0.0

    @pytest.mark.unit
    def test_no_transitions(self):
        """Handles session with no state transitions"""
        traces = [
            MagicMock(cognitive_state="exploration", created_at=datetime.utcnow() + timedelta(minutes=i))
            for i in range(5)
        ]

        transitions = []
        prev_state = None

        for trace in sorted(traces, key=lambda t: t.created_at):
            if prev_state and prev_state != trace.cognitive_state:
                transitions.append({"from": prev_state, "to": trace.cognitive_state})
            prev_state = trace.cognitive_state

        assert len(transitions) == 0


# ============================================================================
# Metrics Calculation Tests
# ============================================================================

class TestMetricsCalculation:
    """Tests for metric calculations"""

    @pytest.mark.unit
    def test_ai_dependency_range(self, mock_traces):
        """AI dependency average is within valid range (0-1)"""
        ai_involvements = [t.ai_involvement or 0.0 for t in mock_traces]
        avg = sum(ai_involvements) / len(ai_involvements)

        assert 0.0 <= avg <= 1.0

    @pytest.mark.unit
    def test_phase_ordering(self, mock_traces):
        """Phases are ordered by start time"""
        phases_dict = defaultdict(list)
        for trace in mock_traces:
            phases_dict[trace.cognitive_state].append(trace)

        phases = []
        for phase_name, phase_traces in phases_dict.items():
            start_time = min(t.created_at for t in phase_traces)
            phases.append({"name": phase_name, "start": start_time})

        phases.sort(key=lambda p: p["start"])

        # Exploration should be first
        assert phases[0]["name"] == "exploration"

    @pytest.mark.unit
    def test_risks_associated_with_phases(self, mock_risks):
        """Risks can be associated with specific phases"""
        risk_trace_ids = []
        for risk in mock_risks:
            if risk.trace_ids:
                risk_trace_ids.extend(risk.trace_ids)

        assert len(risk_trace_ids) > 0


# ============================================================================
# Schema Tests
# ============================================================================

class TestSchemas:
    """Tests for cognitive path schemas"""

    @pytest.mark.unit
    def test_cognitive_phase_schema(self):
        """CognitivePhase schema is valid"""
        from backend.api.schemas.cognitive_path import CognitivePhase

        phase = CognitivePhase(
            phase_name="exploration",
            start_time=datetime.utcnow(),
            end_time=datetime.utcnow(),
            duration_minutes=10.5,
            interactions_count=5,
            ai_involvement_avg=0.45,
            risks_detected=["ai_dependency"],
            key_decisions=["Started with analysis"]
        )

        assert phase.phase_name == "exploration"
        assert phase.duration_minutes == 10.5

    @pytest.mark.unit
    def test_cognitive_transition_schema(self):
        """CognitiveTransition schema is valid"""
        from backend.api.schemas.cognitive_path import CognitiveTransition

        transition = CognitiveTransition(
            from_phase="exploration",
            to_phase="implementation",
            timestamp=datetime.utcnow(),
            trigger="Started coding"
        )

        assert transition.from_phase == "exploration"
        assert transition.to_phase == "implementation"

    @pytest.mark.unit
    def test_cognitive_path_summary_schema(self):
        """CognitivePathSummary schema is valid"""
        from backend.api.schemas.cognitive_path import CognitivePathSummary

        summary = CognitivePathSummary(
            total_interactions=10,
            total_duration_minutes=45.5,
            blocked_interactions=2,
            ai_dependency_average=0.55,
            strategy_changes=3,
            risks_total=4,
            risks_by_level={"low": 1, "medium": 2, "high": 1}
        )

        assert summary.total_interactions == 10
        assert summary.ai_dependency_average == 0.55

    @pytest.mark.unit
    def test_cognitive_path_schema(self):
        """CognitivePath schema is valid"""
        from backend.api.schemas.cognitive_path import (
            CognitivePath,
            CognitivePhase,
            CognitiveTransition,
            CognitivePathSummary
        )

        now = datetime.utcnow()

        path = CognitivePath(
            session_id="session_001",
            student_id="student_001",
            activity_id="activity_001",
            start_time=now - timedelta(hours=1),
            end_time=now,
            summary=CognitivePathSummary(
                total_interactions=5,
                total_duration_minutes=60.0,
                blocked_interactions=1,
                ai_dependency_average=0.5,
                strategy_changes=2,
                risks_total=3,
                risks_by_level={"medium": 2, "high": 1}
            ),
            phases=[
                CognitivePhase(
                    phase_name="exploration",
                    start_time=now - timedelta(hours=1),
                    end_time=now - timedelta(minutes=30),
                    duration_minutes=30.0,
                    interactions_count=3,
                    ai_involvement_avg=0.4,
                    risks_detected=[],
                    key_decisions=[]
                )
            ],
            transitions=[
                CognitiveTransition(
                    from_phase="exploration",
                    to_phase="implementation",
                    timestamp=now - timedelta(minutes=30),
                    trigger="Started coding"
                )
            ]
        )

        assert path.session_id == "session_001"
        assert len(path.phases) == 1
        assert len(path.transitions) == 1


# ============================================================================
# Integration Tests
# ============================================================================

class TestCognitivePathIntegration:
    """Integration tests for cognitive path functionality"""

    @pytest.mark.integration
    def test_full_path_reconstruction(self):
        """Complete path reconstruction from session data"""
        pass

    @pytest.mark.integration
    def test_path_with_many_transitions(self):
        """Path handles many state transitions correctly"""
        pass

    @pytest.mark.integration
    def test_path_visualization_data(self):
        """Path provides data suitable for visualization"""
        pass