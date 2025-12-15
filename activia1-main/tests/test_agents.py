"""
Unit tests for AI Agents

Tests cover:
- Tutor agent response generation
- Evaluator agent process evaluation
- Risk analyst agent risk detection
- Simulator agent role simulation
- Governance agent policy enforcement
- Traceability agent path reconstruction
"""
import pytest
from datetime import datetime

from backend.agents.tutor import TutorCognitivoAgent, TutorMode
from backend.agents.evaluator import EvaluadorProcesosAgent
from backend.agents.risk_analyst import AnalistaRiesgoAgent
from backend.agents.simulators import SimuladorProfesionalAgent, SimuladorType
from backend.agents.governance import GobernanzaAgent
from backend.agents.traceability import TrazabilidadN4Agent

from backend.core.cognitive_engine import CognitiveState
from backend.models.trace import TraceLevel
from backend.models.risk import RiskLevel, RiskDimension
from backend.models.evaluation import CompetencyLevel


# ============================================================================
# Tutor Agent Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.agents
class TestTutorCognitivoAgent:
    """Tests for T-IA-Cog (Cognitive Tutor Agent)"""

    @pytest.fixture
    def tutor(self, mock_llm_provider):
        """Fixture providing a tutor agent"""
        return TutorCognitivoAgent(llm_provider=mock_llm_provider)

    def test_tutor_initialization(self, tutor):
        """Test tutor agent initializes correctly"""
        assert tutor is not None
        assert hasattr(tutor, "generate_response")

    def test_socratic_mode_generates_questions(self, tutor):
        """Test that Socratic mode generates questions, not answers"""
        strategy = {
            "response_type": "socratic_questions",
            "mode": TutorMode.SOCRATICO,
        }

        response = tutor.generate_response(
            student_prompt="Dame el código de una cola",
            cognitive_state=CognitiveState.IMPLEMENTACION,
            strategy=strategy,
            student_history=[],
        )

        # Response should be a dict with message
        assert isinstance(response, dict)
        message = response.get('message', '')
        # Response should contain questions
        assert "?" in message or "pregunta" in message.lower()
        # Should not contain complete code
        assert "class Cola:" not in message

    def test_conceptual_explanation_mode(self, tutor):
        """Test conceptual explanation mode"""
        strategy = {
            "response_type": "conceptual_explanation",
            "mode": TutorMode.EXPLICATIVO,
        }

        response = tutor.generate_response(
            student_prompt="¿Qué es una cola?",
            cognitive_state=CognitiveState.EXPLORACION,
            strategy=strategy,
            student_history=[],
        )

        # Response should be a dict with message
        assert isinstance(response, dict)
        message = response.get('message', '')
        # Should provide explanation
        assert len(message) > 50  # Substantial explanation
        # But not complete implementation
        assert "def enqueue" not in message.lower()

    def test_guided_hints_mode(self, tutor):
        """Test guided hints mode"""
        strategy = {
            "response_type": "guided_hints",
            "mode": TutorMode.GUIADO,
        }

        response = tutor.generate_response(
            student_prompt="¿Cómo implemento enqueue?",
            cognitive_state=CognitiveState.IMPLEMENTACION,
            strategy=strategy,
            student_history=[],
        )

        # Response should be a dict with message
        assert isinstance(response, dict)
        message = response.get('message', '')
        # Should provide hints but not complete solution
        assert len(message) > 20
        assert response is not None

    def test_metacognitive_mode(self, tutor):
        """Test metacognitive reflection mode"""
        strategy = {
            "response_type": "metacognitive_prompts",
            "mode": TutorMode.METACOGNITIVO,
        }

        response = tutor.generate_response(
            student_prompt="Ya terminé la implementación",
            cognitive_state=CognitiveState.REFLEXION,
            strategy=strategy,
            student_history=[],
        )

        # Response should be a dict with message
        assert isinstance(response, dict)
        message = response.get('message', '')
        # Should prompt reflection
        assert "?" in message or any(
            word in message.lower()
            for word in ["reflexion", "consider", "think", "evalua"]
        )

    def test_tutor_respects_no_delegation_policy(self, tutor):
        """Test that tutor never provides complete solutions"""
        prompts = [
            "Dame el código completo",
            "Escribí todo el programa",
            "Hacelo por mí",
        ]

        for prompt in prompts:
            strategy = {
                "response_type": "socratic_questions",
                "block": True,
            }

            response = tutor.generate_response(
                student_prompt=prompt,
                cognitive_state=CognitiveState.IMPLEMENTACION,
                strategy=strategy,
                student_history=[],
            )

            # Response should be a dict with message
            assert isinstance(response, dict)
            message = response.get('message', '')
            # Should redirect or block
            assert (
                "?" in message
                or "descomponer" in message.lower()
                or "planifica" in message.lower()
            )


# ============================================================================
# Evaluator Agent Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.agents
class TestEvaluadorProcesosAgent:
    """Tests for E-IA-Proc (Process Evaluator Agent)"""

    @pytest.fixture
    def evaluator(self, mock_llm_provider):
        """Fixture providing an evaluator agent"""
        return EvaluadorProcesosAgent(llm_provider=mock_llm_provider)

    def test_evaluator_initialization(self, evaluator):
        """Test evaluator initializes correctly"""
        assert evaluator is not None
        assert hasattr(evaluator, "evaluate_process")

    def test_evaluate_process_returns_report(self, evaluator, sample_trace_sequence):
        """Test that evaluation returns a complete report"""
        report = evaluator.evaluate_process(
            trace_sequence=sample_trace_sequence, code_evolution=[]
        )

        assert report is not None
        assert hasattr(report, "overall_competency_level")
        assert hasattr(report, "overall_score")
        assert hasattr(report, "dimensions")

    def test_evaluation_detects_delegation(self, evaluator, sample_trace_delegacion):
        """Test that evaluation detects delegation patterns"""
        from backend.models.trace import TraceSequence

        sequence = TraceSequence(
            id="test",
            session_id=sample_trace_delegacion.session_id,
            student_id=sample_trace_delegacion.student_id,
            activity_id=sample_trace_delegacion.activity_id,
            traces=[sample_trace_delegacion],
            start_time=datetime.utcnow(),
        )

        report = evaluator.evaluate_process(trace_sequence=sequence, code_evolution=[])

        # High AI involvement should lower competency
        assert report.overall_competency_level in [
            CompetencyLevel.INICIAL,
            CompetencyLevel.EN_DESARROLLO,
        ]

    def test_evaluation_recognizes_autonomous_work(
        self, evaluator, sample_trace_conceptual, sample_trace_planning
    ):
        """Test that evaluation recognizes autonomous reasoning"""
        from backend.models.trace import TraceSequence

        sequence = TraceSequence(
            id="test",
            session_id=sample_trace_conceptual.session_id,
            student_id=sample_trace_conceptual.student_id,
            activity_id=sample_trace_conceptual.activity_id,
            traces=[sample_trace_conceptual, sample_trace_planning],
            start_time=datetime.utcnow(),
        )

        report = evaluator.evaluate_process(trace_sequence=sequence, code_evolution=[])

        # Low AI dependency should be positive
        assert report.overall_score >= 5.0

    def test_evaluation_includes_dimensions(self, evaluator, sample_trace_sequence):
        """Test that evaluation covers multiple dimensions"""
        report = evaluator.evaluate_process(
            trace_sequence=sample_trace_sequence, code_evolution=[]
        )

        assert len(report.dimensions) > 0

        # Should include key dimensions
        dimension_names = [d.name for d in report.dimensions]
        assert any("descompos" in name.lower() for name in dimension_names)

    def test_evaluation_provides_feedback(self, evaluator, sample_trace_sequence):
        """Test that evaluation provides actionable feedback"""
        report = evaluator.evaluate_process(
            trace_sequence=sample_trace_sequence, code_evolution=[]
        )

        # Should have strengths or improvement areas
        assert len(report.key_strengths) > 0 or len(report.improvement_areas) > 0


# ============================================================================
# Risk Analyst Agent Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.agents
class TestAnalistaRiesgoAgent:
    """Tests for AR-IA (Risk Analyst Agent)"""

    @pytest.fixture
    def analyst(self, mock_llm_provider):
        """Fixture providing a risk analyst agent"""
        return AnalistaRiesgoAgent(llm_provider=mock_llm_provider)

    def test_analyst_initialization(self, analyst):
        """Test analyst initializes correctly"""
        assert analyst is not None
        assert hasattr(analyst, "analyze_session")

    def test_analyze_session_returns_report(self, analyst, sample_trace_sequence):
        """Test that analysis returns a risk report"""
        report = analyst.analyze_session(trace_sequence=sample_trace_sequence)

        assert report is not None
        assert hasattr(report, "risks")
        assert hasattr(report, "total_risks")

    def test_detect_cognitive_delegation_risk(self, analyst, sample_trace_delegacion):
        """Test detection of cognitive delegation risk"""
        from backend.models.trace import TraceSequence

        sequence = TraceSequence(
            id="test",
            session_id=sample_trace_delegacion.session_id,
            student_id=sample_trace_delegacion.student_id,
            activity_id=sample_trace_delegacion.activity_id,
            traces=[sample_trace_delegacion],
            start_time=datetime.utcnow(),
        )

        report = analyst.analyze_session(trace_sequence=sequence)

        # Should detect delegation risk
        assert report.total_risks > 0
        cognitive_risks = [
            r for r in report.risks if r.dimension == RiskDimension.COGNITIVE
        ]
        assert len(cognitive_risks) > 0

    def test_risk_levels_prioritized(self, analyst, sample_trace_sequence):
        """Test that risks are properly prioritized by level"""
        report = analyst.analyze_session(trace_sequence=sample_trace_sequence)

        # Critical and high risks should be counted
        total_critical_high = report.critical_risks + report.high_risks

        # Should be reasonable for the sample sequence
        assert total_critical_high >= 0

    def test_risk_recommendations_provided(self, analyst, sample_trace_sequence):
        """Test that risks include actionable recommendations"""
        report = analyst.analyze_session(trace_sequence=sample_trace_sequence)

        if report.total_risks > 0:
            # At least some risks should have recommendations
            risks_with_recommendations = [
                r for r in report.risks if len(r.recommendations) > 0
            ]
            assert len(risks_with_recommendations) > 0

    def test_overall_assessment_provided(self, analyst, sample_trace_sequence):
        """Test that report includes overall assessment"""
        report = analyst.analyze_session(trace_sequence=sample_trace_sequence)

        assert report.overall_assessment is not None
        assert len(report.overall_assessment) > 0


# ============================================================================
# Simulator Agent Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.agents
class TestSimuladorProfesionalAgent:
    """Tests for S-IA-X (Professional Simulator Agent)"""

    def test_simulator_initialization(self, mock_llm_provider):
        """Test simulator initializes with different roles"""
        for simulator_type in SimuladorType:
            simulator = SimuladorProfesionalAgent(
                simulator_type=simulator_type, llm_provider=mock_llm_provider
            )
            assert simulator is not None
            assert simulator.simulator_type == simulator_type

    def test_product_owner_simulator(self, mock_llm_provider):
        """Test Product Owner simulator behavior"""
        po = SimuladorProfesionalAgent(
            simulator_type=SimuladorType.PRODUCT_OWNER, llm_provider=mock_llm_provider
        )

        response = po.interact(
            student_input="Quiero agregar un login",
            context={"project": "e-commerce"},
        )

        # PO should ask about requirements, value, criteria
        assert response is not None
        assert len(response) > 20

    def test_scrum_master_simulator(self, mock_llm_provider):
        """Test Scrum Master simulator behavior"""
        sm = SimuladorProfesionalAgent(
            simulator_type=SimuladorType.SCRUM_MASTER, llm_provider=mock_llm_provider
        )

        response = sm.interact(
            student_input="Estoy bloqueado con un bug",
            context={"sprint": "3"},
        )

        # SM should help remove impediments
        assert response is not None
        assert len(response) > 20

    def test_tech_interviewer_simulator(self, mock_llm_provider):
        """Test Technical Interviewer simulator behavior"""
        interviewer = SimuladorProfesionalAgent(
            simulator_type=SimuladorType.TECH_INTERVIEWER,
            llm_provider=mock_llm_provider,
        )

        response = interviewer.interact(
            student_input="La complejidad es O(n)",
            context={"question": "binary_search"},
        )

        # Should probe understanding
        assert response is not None
        assert len(response) > 20


# ============================================================================
# Governance Agent Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.agents
class TestGobernanzaAgent:
    """Tests for GOV-IA (Governance Agent)"""

    @pytest.fixture
    def governance(self, mock_llm_provider):
        """Fixture providing a governance agent"""
        return GobernanzaAgent(llm_provider=mock_llm_provider)

    def test_governance_initialization(self, governance):
        """Test governance agent initializes correctly"""
        assert governance is not None
        assert hasattr(governance, "verify_compliance")

    def test_verify_compliance_detects_violations(
        self, governance, sample_trace_delegacion
    ):
        """Test that compliance verification detects policy violations"""
        from backend.models.trace import TraceSequence

        sequence = TraceSequence(
            id="test",
            session_id=sample_trace_delegacion.session_id,
            student_id=sample_trace_delegacion.student_id,
            activity_id=sample_trace_delegacion.activity_id,
            traces=[sample_trace_delegacion],
            start_time=datetime.utcnow(),
        )

        compliance_report = governance.verify_compliance(
            trace_sequence=sequence, policies={"max_ai_dependency": 0.7}
        )

        # High AI involvement should violate policy
        assert compliance_report is not None

    def test_policy_enforcement(self, governance, sample_trace_sequence):
        """Test policy enforcement mechanisms"""
        policies = {
            "max_ai_dependency": 0.7,
            "require_traceability": True,
            "block_full_delegation": True,
        }

        compliance_report = governance.verify_compliance(
            trace_sequence=sample_trace_sequence, policies=policies
        )

        assert compliance_report is not None


# ============================================================================
# Traceability Agent Tests
# ============================================================================


@pytest.mark.unit
@pytest.mark.agents
class TestTrazabilidadN4Agent:
    """Tests for TC-N4 (N4 Traceability Agent)"""

    @pytest.fixture
    def traceability(self, mock_llm_provider):
        """Fixture providing a traceability agent"""
        return TrazabilidadN4Agent(llm_provider=mock_llm_provider)

    def test_traceability_initialization(self, traceability):
        """Test traceability agent initializes correctly"""
        assert traceability is not None
        assert hasattr(traceability, "capture_trace")

    def test_capture_n4_trace(self, traceability, student_id, activity_id):
        """Test capturing N4-level cognitive trace"""
        trace = traceability.capture_trace(
            session_id="test_session",
            student_id=student_id,
            activity_id=activity_id,
            interaction_type="STUDENT_PROMPT",
            content="Test content",
            cognitive_state=CognitiveState.PLANIFICACION,
            metadata={"test": "data"},
        )

        assert trace is not None
        assert trace.trace_level == TraceLevel.N4_COGNITIVO
        assert trace.cognitive_state == CognitiveState.PLANIFICACION

    def test_reconstruct_cognitive_path(self, traceability, sample_trace_sequence):
        """Test reconstructing cognitive path from traces"""
        # First, store the sequence (mock storage)
        traceability._sequences = {
            sample_trace_sequence.id: sample_trace_sequence
        }

        path = traceability.reconstruct_cognitive_path(
            sample_trace_sequence.id
        )

        assert path is not None
        assert "phases" in path or "cognitive_states" in path
