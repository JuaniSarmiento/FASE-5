"""
Tests for RiskAnalyzer component

Verifies:
- Interaction risk analysis (delegation, superficial reasoning, integrity)
- Session-level risk analysis via AR-IA agent
- Risk persistence and retrieval
- Risk report generation
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4
from datetime import datetime

from backend.core.risk_analyzer import RiskAnalyzer
from backend.models.trace import CognitiveTrace, TraceSequence, TraceLevel, InteractionType
from backend.models.risk import Risk, RiskType, RiskLevel, RiskDimension, RiskReport
from backend.core.cognitive_engine import CognitiveState


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_risk_repo():
    """Mock risk repository"""
    repo = Mock()
    repo.create = Mock(return_value=None)
    repo.get_by_student = Mock(return_value=[])
    repo.get_by_session = Mock(return_value=[])
    return repo


@pytest.fixture
def mock_risk_agent():
    """Mock AR-IA risk analyst agent"""
    agent = Mock()
    agent.analyze_session = Mock(return_value=RiskReport(
        id=str(uuid4()),
        student_id="test_student",
        activity_id="test_activity",
        risks=[]
    ))
    return agent


@pytest.fixture
def risk_analyzer(mock_risk_repo, mock_risk_agent):
    """RiskAnalyzer instance with mocked dependencies"""
    return RiskAnalyzer(
        risk_repo=mock_risk_repo,
        risk_agent=mock_risk_agent,
        config={}
    )


@pytest.fixture
def sample_input_trace():
    """Sample input trace from student"""
    return CognitiveTrace(
        id=str(uuid4()),
        session_id=str(uuid4()),
        student_id="test_student",
        activity_id="test_activity",
        timestamp=datetime.utcnow(),
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.STUDENT_PROMPT,
        cognitive_state=CognitiveState.IMPLEMENTACION,
        content="¿Cómo implemento una cola?",
        ai_involvement=0.3,
    )


@pytest.fixture
def sample_response_trace():
    """Sample response trace from agent"""
    return CognitiveTrace(
        id=str(uuid4()),
        session_id=str(uuid4()),
        student_id="test_student",
        activity_id="test_activity",
        timestamp=datetime.utcnow(),
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.AI_RESPONSE,
        cognitive_state=CognitiveState.IMPLEMENTACION,
        content="Para implementar una cola...",
        ai_involvement=0.5,
    )


# ============================================================================
# Initialization Tests
# ============================================================================

class TestRiskAnalyzerInit:
    """Tests for RiskAnalyzer initialization"""

    def test_init_with_dependencies(self, mock_risk_repo, mock_risk_agent):
        """Test initialization with all dependencies"""
        analyzer = RiskAnalyzer(
            risk_repo=mock_risk_repo,
            risk_agent=mock_risk_agent,
            config={"threshold": 0.7}
        )

        assert analyzer.risk_repo == mock_risk_repo
        assert analyzer.risk_agent == mock_risk_agent
        assert analyzer.config["threshold"] == 0.7

    def test_init_with_default_config(self, mock_risk_repo, mock_risk_agent):
        """Test initialization with default config"""
        analyzer = RiskAnalyzer(
            risk_repo=mock_risk_repo,
            risk_agent=mock_risk_agent
        )

        assert analyzer.config == {}


# ============================================================================
# Delegation Risk Detection Tests
# ============================================================================

class TestDelegationRiskDetection:
    """Tests for cognitive delegation risk detection"""

    @pytest.mark.parametrize("delegation_prompt", [
        "dame el código completo",
        "escribe el código por mí",
        "resuelve esto por favor",
        "hazlo por mi",
        "genera el código completo de la cola",
        "completa el código del algoritmo",
    ])
    def test_detect_delegation_patterns(
        self,
        risk_analyzer,
        sample_response_trace,
        delegation_prompt
    ):
        """Test detection of various delegation patterns"""
        input_trace = CognitiveTrace(
            id=str(uuid4()),
            session_id=str(uuid4()),
            student_id="test_student",
            activity_id="test_activity",
            timestamp=datetime.utcnow(),
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.IMPLEMENTACION,
            content=delegation_prompt,
            ai_involvement=0.3,
        )

        risks = risk_analyzer.analyze_interaction(
            session_id=input_trace.session_id,
            input_trace=input_trace,
            response_trace=sample_response_trace,
            classification={"type": "delegation"}
        )

        # Should detect delegation risk
        assert len(risks) >= 1
        delegation_risks = [r for r in risks if r.risk_type == RiskType.COGNITIVE_DELEGATION]
        assert len(delegation_risks) == 1
        assert delegation_risks[0].risk_level == RiskLevel.HIGH
        assert delegation_risks[0].dimension == RiskDimension.COGNITIVE

    def test_no_delegation_for_conceptual_question(
        self,
        risk_analyzer,
        sample_response_trace
    ):
        """Test no delegation risk for valid conceptual questions"""
        input_trace = CognitiveTrace(
            id=str(uuid4()),
            session_id=str(uuid4()),
            student_id="test_student",
            activity_id="test_activity",
            timestamp=datetime.utcnow(),
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.EXPLORACION,
            content="¿Cuál es la diferencia entre una cola y una pila? Estoy tratando de entender cuándo usar cada una.",
            ai_involvement=0.3,
        )

        risks = risk_analyzer.analyze_interaction(
            session_id=input_trace.session_id,
            input_trace=input_trace,
            response_trace=sample_response_trace,
            classification={"type": "conceptual"}
        )

        # Should not detect delegation risk
        delegation_risks = [r for r in risks if r.risk_type == RiskType.COGNITIVE_DELEGATION]
        assert len(delegation_risks) == 0


# ============================================================================
# Superficial Reasoning Risk Detection Tests
# ============================================================================

class TestSuperficialReasoningDetection:
    """Tests for superficial reasoning risk detection"""

    def test_detect_very_short_prompt(self, risk_analyzer, sample_response_trace):
        """Test detection of very short prompts without context"""
        input_trace = CognitiveTrace(
            id=str(uuid4()),
            session_id=str(uuid4()),
            student_id="test_student",
            activity_id="test_activity",
            timestamp=datetime.utcnow(),
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.IMPLEMENTACION,
            content="ayuda",  # Very short - less than 20 chars
            ai_involvement=0.3,
        )

        risks = risk_analyzer.analyze_interaction(
            session_id=input_trace.session_id,
            input_trace=input_trace,
            response_trace=sample_response_trace,
            classification={"type": "unknown"}
        )

        # Should detect superficial reasoning risk
        superficial_risks = [r for r in risks if r.risk_type == RiskType.LACK_JUSTIFICATION]
        assert len(superficial_risks) == 1
        assert superficial_risks[0].risk_level == RiskLevel.MEDIUM

    def test_no_superficial_for_detailed_prompt(
        self,
        risk_analyzer,
        sample_response_trace
    ):
        """Test no superficial risk for detailed prompts"""
        input_trace = CognitiveTrace(
            id=str(uuid4()),
            session_id=str(uuid4()),
            student_id="test_student",
            activity_id="test_activity",
            timestamp=datetime.utcnow(),
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.PLANIFICACION,
            content="Estoy implementando una cola circular y tengo dudas sobre cómo manejar el caso cuando el arreglo está lleno. He pensado en usar un contador pero no estoy seguro si es eficiente.",
            ai_involvement=0.3,
        )

        risks = risk_analyzer.analyze_interaction(
            session_id=input_trace.session_id,
            input_trace=input_trace,
            response_trace=sample_response_trace,
            classification={"type": "planning"}
        )

        # Should not detect superficial reasoning risk
        superficial_risks = [r for r in risks if r.risk_type == RiskType.LACK_JUSTIFICATION]
        assert len(superficial_risks) == 0


# ============================================================================
# Session Analysis Tests
# ============================================================================

class TestSessionAnalysis:
    """Tests for complete session risk analysis"""

    def test_analyze_session_delegates_to_agent(
        self,
        risk_analyzer,
        mock_risk_agent
    ):
        """Test that session analysis delegates to AR-IA agent"""
        sequence = TraceSequence(
            id=str(uuid4()),
            session_id=str(uuid4()),
            student_id="test_student",
            activity_id="test_activity",
            traces=[],  # Empty list of CognitiveTrace objects
            start_time=datetime.utcnow(),
        )

        report = risk_analyzer.analyze_session(sequence)

        # Should call agent's analyze_session
        mock_risk_agent.analyze_session.assert_called_once()
        assert isinstance(report, RiskReport)

    def test_analyze_session_persists_detected_risks(
        self,
        risk_analyzer,
        mock_risk_repo,
        mock_risk_agent
    ):
        """Test that detected risks are persisted to repository"""
        session_id = str(uuid4())
        # Configure agent to return risks
        detected_risk = Risk(
            id=str(uuid4()),
            session_id=session_id,
            student_id="test_student",
            activity_id="test_activity",
            risk_type=RiskType.COGNITIVE_DELEGATION,
            risk_level=RiskLevel.HIGH,
            dimension=RiskDimension.COGNITIVE,
            description="Test risk",
            evidence=["evidence1"],
            trace_ids=["trace1"],
        )

        mock_risk_agent.analyze_session.return_value = RiskReport(
            id=str(uuid4()),
            student_id="test_student",
            activity_id="test_activity",
            risks=[detected_risk]
        )

        sequence = TraceSequence(
            id=str(uuid4()),
            session_id=session_id,
            student_id="test_student",
            activity_id="test_activity",
            traces=[],
            start_time=datetime.utcnow(),
        )

        risk_analyzer.analyze_session(sequence)

        # Should persist the risk
        mock_risk_repo.create.assert_called_once_with(detected_risk)

    def test_analyze_session_handles_persistence_error(
        self,
        risk_analyzer,
        mock_risk_repo,
        mock_risk_agent
    ):
        """Test graceful handling of persistence errors"""
        session_id = str(uuid4())
        # Configure agent to return risks
        detected_risk = Risk(
            id=str(uuid4()),
            session_id=session_id,
            student_id="test_student",
            activity_id="test_activity",
            risk_type=RiskType.COGNITIVE_DELEGATION,
            risk_level=RiskLevel.HIGH,
            dimension=RiskDimension.COGNITIVE,
            description="Test risk",
            evidence=["evidence1"],
            trace_ids=["trace1"],
        )

        mock_risk_agent.analyze_session.return_value = RiskReport(
            id=str(uuid4()),
            student_id="test_student",
            activity_id="test_activity",
            risks=[detected_risk]
        )

        # Configure repo to fail
        mock_risk_repo.create.side_effect = Exception("DB Error")

        sequence = TraceSequence(
            id=str(uuid4()),
            session_id=session_id,
            student_id="test_student",
            activity_id="test_activity",
            traces=[],
            start_time=datetime.utcnow(),
        )

        # Should not raise, just log error
        report = risk_analyzer.analyze_session(sequence)
        assert report is not None


# ============================================================================
# Risk Report Retrieval Tests
# ============================================================================

class TestRiskReportRetrieval:
    """Tests for risk report retrieval from database"""

    def test_get_risk_report_returns_none_when_empty(
        self,
        risk_analyzer,
        mock_risk_repo
    ):
        """Test get_risk_report returns None when no risks exist"""
        mock_risk_repo.get_by_student.return_value = []

        report = risk_analyzer.get_risk_report("student1", "activity1")

        assert report is None

    def test_get_risk_report_filters_by_activity(
        self,
        risk_analyzer,
        mock_risk_repo
    ):
        """Test that get_risk_report filters by activity_id"""
        session_id = str(uuid4())
        # Create mock DB risks with lowercase enum values
        mock_risk1 = Mock()
        mock_risk1.id = str(uuid4())
        mock_risk1.session_id = session_id
        mock_risk1.student_id = "student1"
        mock_risk1.activity_id = "activity1"
        mock_risk1.risk_type = "cognitive_delegation"  # lowercase
        mock_risk1.risk_level = "high"  # lowercase
        mock_risk1.dimension = "cognitive"  # lowercase
        mock_risk1.description = "Test"
        mock_risk1.evidence = []
        mock_risk1.trace_ids = []
        mock_risk1.recommendations = []
        mock_risk1.resolved = False
        mock_risk1.resolution_notes = None

        mock_risk2 = Mock()
        mock_risk2.id = str(uuid4())
        mock_risk2.session_id = session_id
        mock_risk2.student_id = "student1"
        mock_risk2.activity_id = "activity2"  # Different activity
        mock_risk2.risk_type = "lack_justification"  # lowercase
        mock_risk2.risk_level = "medium"  # lowercase
        mock_risk2.dimension = "cognitive"  # lowercase
        mock_risk2.description = "Test 2"
        mock_risk2.evidence = []
        mock_risk2.trace_ids = []
        mock_risk2.recommendations = []
        mock_risk2.resolved = False
        mock_risk2.resolution_notes = None

        mock_risk_repo.get_by_student.return_value = [mock_risk1, mock_risk2]

        report = risk_analyzer.get_risk_report("student1", "activity1")

        # Should only include risks for activity1
        assert report is not None
        assert len(report.risks) == 1
        assert report.risks[0].activity_id == "activity1"


# ============================================================================
# Risk Persistence Tests
# ============================================================================

class TestRiskPersistence:
    """Tests for risk persistence"""

    def test_persist_risk_success(self, risk_analyzer, mock_risk_repo):
        """Test successful risk persistence"""
        risk = risk_analyzer.persist_risk(
            student_id="student1",
            activity_id="activity1",
            risk_type=RiskType.COGNITIVE_DELEGATION,
            risk_level=RiskLevel.HIGH,
            dimension=RiskDimension.COGNITIVE,
            description="Test delegation risk",
            evidence=["Dame el código"],
            trace_ids=["trace1"],
            recommendations=["Descomponer el problema"],
            session_id=str(uuid4())  # Required field
        )

        assert risk is not None
        assert risk.student_id == "student1"
        assert risk.risk_type == RiskType.COGNITIVE_DELEGATION
        mock_risk_repo.create.assert_called_once()

    def test_persist_risk_failure_returns_none(
        self,
        risk_analyzer,
        mock_risk_repo
    ):
        """Test persist_risk returns None on failure"""
        mock_risk_repo.create.side_effect = Exception("DB Error")

        risk = risk_analyzer.persist_risk(
            student_id="student1",
            activity_id="activity1",
            risk_type=RiskType.COGNITIVE_DELEGATION,
            risk_level=RiskLevel.HIGH,
            dimension=RiskDimension.COGNITIVE,
            description="Test risk",
            evidence=[],
            trace_ids=[],
            session_id=str(uuid4())  # Required field
        )

        assert risk is None


# ============================================================================
# Integration Tests
# ============================================================================

class TestRiskAnalyzerIntegration:
    """Integration tests for RiskAnalyzer"""

    def test_full_interaction_analysis_flow(
        self,
        risk_analyzer,
        mock_risk_repo
    ):
        """Test complete flow: analyze interaction and persist risks"""
        session_id = str(uuid4())

        # Create delegation trace
        input_trace = CognitiveTrace(
            id=str(uuid4()),
            session_id=session_id,
            student_id="test_student",
            activity_id="test_activity",
            timestamp=datetime.utcnow(),
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.IMPLEMENTACION,
            content="Dame el código completo del algoritmo de ordenamiento",
            ai_involvement=0.3,
        )

        response_trace = CognitiveTrace(
            id=str(uuid4()),
            session_id=session_id,
            student_id="test_student",
            activity_id="test_activity",
            timestamp=datetime.utcnow(),
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.AI_RESPONSE,
            cognitive_state=CognitiveState.IMPLEMENTACION,
            content="Te sugiero que primero pienses en...",
            ai_involvement=0.5,
        )

        risks = risk_analyzer.analyze_interaction(
            session_id=session_id,
            input_trace=input_trace,
            response_trace=response_trace,
            classification={"type": "implementation"}
        )

        # Should detect and persist delegation risk
        assert len(risks) >= 1
        assert mock_risk_repo.create.called

    def test_multiple_risks_in_single_interaction(
        self,
        risk_analyzer,
        mock_risk_repo
    ):
        """Test detection of multiple risks in one interaction"""
        session_id = str(uuid4())

        # Very short delegation prompt - triggers both risks
        # Must be short (<20 chars) AND contain delegation pattern
        input_trace = CognitiveTrace(
            id=str(uuid4()),
            session_id=session_id,
            student_id="test_student",
            activity_id="test_activity",
            timestamp=datetime.utcnow(),
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.IMPLEMENTACION,
            content="hazlo por mi",  # Short (12 chars) AND delegation pattern
            ai_involvement=0.3,
        )

        response_trace = CognitiveTrace(
            id=str(uuid4()),
            session_id=session_id,
            student_id="test_student",
            activity_id="test_activity",
            timestamp=datetime.utcnow(),
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.AI_RESPONSE,
            cognitive_state=CognitiveState.IMPLEMENTACION,
            content="Response",
            ai_involvement=0.5,
        )

        risks = risk_analyzer.analyze_interaction(
            session_id=session_id,
            input_trace=input_trace,
            response_trace=response_trace,
            classification={"type": "unknown"}
        )

        # Should detect both delegation and superficial reasoning risks
        risk_types = [r.risk_type for r in risks]
        assert RiskType.COGNITIVE_DELEGATION in risk_types
        assert RiskType.LACK_JUSTIFICATION in risk_types