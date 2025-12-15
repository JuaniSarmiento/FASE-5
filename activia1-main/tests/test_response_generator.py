"""
Tests for ResponseGenerator module

Covers:
- Response routing to different agents
- Tutor response generation
- Evaluation response generation
- Simulator response generation
- Default response handling
"""
import pytest
from unittest.mock import Mock, MagicMock, patch

from backend.core.response_generator import ResponseGenerator
from backend.agents.tutor import TutorCognitivoAgent
from backend.agents.evaluator import ProcessEvaluatorAgent
from backend.llm.base import LLMProvider


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_tutor():
    """Create a mock TutorCognitivoAgent"""
    tutor = Mock(spec=TutorCognitivoAgent)
    tutor.process_request = Mock(return_value="Tutor response: Let me help you understand this concept.")
    return tutor


@pytest.fixture
def mock_evaluator():
    """Create a mock ProcessEvaluatorAgent"""
    evaluator = Mock(spec=ProcessEvaluatorAgent)
    evaluator.evaluate_process = Mock(return_value="Evaluation: Your process shows good problem decomposition.")
    return evaluator


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider"""
    provider = Mock(spec=LLMProvider)
    return provider


@pytest.fixture
def response_generator(mock_tutor, mock_evaluator, mock_llm_provider):
    """Create a ResponseGenerator instance with mocked dependencies"""
    return ResponseGenerator(
        tutor=mock_tutor,
        evaluator=mock_evaluator,
        llm_provider=mock_llm_provider,
        config={"max_tokens": 500}
    )


# ============================================================================
# Initialization Tests
# ============================================================================

class TestResponseGeneratorInit:
    """Tests for ResponseGenerator initialization"""

    def test_init_with_all_params(self, mock_tutor, mock_evaluator, mock_llm_provider):
        """Test initialization with all parameters"""
        config = {"max_tokens": 1000}
        generator = ResponseGenerator(
            tutor=mock_tutor,
            evaluator=mock_evaluator,
            llm_provider=mock_llm_provider,
            config=config
        )

        assert generator.tutor == mock_tutor
        assert generator.evaluator == mock_evaluator
        assert generator.llm_provider == mock_llm_provider
        assert generator.config == config
        assert generator._simulators == {}

    def test_init_without_config(self, mock_tutor, mock_evaluator, mock_llm_provider):
        """Test initialization without optional config"""
        generator = ResponseGenerator(
            tutor=mock_tutor,
            evaluator=mock_evaluator,
            llm_provider=mock_llm_provider
        )

        assert generator.config == {}


# ============================================================================
# Response Routing Tests
# ============================================================================

class TestGenerateResponse:
    """Tests for generate_response method"""

    def test_routes_help_request_to_tutor(self, response_generator, mock_tutor):
        """Test that help requests are routed to tutor"""
        classification = {
            "type": "help_request",
            "cognitive_state": "exploration"
        }

        response = response_generator.generate_response(
            classification=classification,
            prompt="What is a queue?",
            context={"code": "queue = []"}
        )

        mock_tutor.process_request.assert_called_once()
        assert "Tutor response" in response

    def test_routes_evaluation_request_to_evaluator(self, response_generator, mock_evaluator):
        """Test that evaluation requests are routed to evaluator"""
        classification = {
            "type": "evaluation_request",
            "cognitive_state": "reflection"
        }

        response = response_generator.generate_response(
            classification=classification,
            prompt="Evaluate my work",
            session_id="session-123"
        )

        mock_evaluator.evaluate_process.assert_called_once()
        assert "Evaluation" in response

    def test_routes_simulator_request_to_simulator(self, response_generator):
        """Test that simulator requests are routed to simulators"""
        classification = {
            "type": "simulator_request",
            "simulator": "PO",
            "cognitive_state": "implementation"
        }

        # Mock the simulator
        with patch.object(response_generator, '_generate_simulator_response') as mock_sim:
            mock_sim.return_value = "Product Owner: Great user story!"

            response = response_generator.generate_response(
                classification=classification,
                prompt="Review my user story"
            )

            mock_sim.assert_called_once_with("PO", "Review my user story", None)

    def test_returns_default_for_unknown_type(self, response_generator):
        """Test that unknown request types get default response"""
        classification = {
            "type": "unknown_type",
            "cognitive_state": "unknown"
        }

        response = response_generator.generate_response(
            classification=classification,
            prompt="Something unusual"
        )

        assert "No puedo procesar tu solicitud" in response


# ============================================================================
# Tutor Response Tests
# ============================================================================

class TestTutorResponse:
    """Tests for tutor response generation"""

    def test_tutor_receives_correct_request(self, response_generator, mock_tutor):
        """Test that tutor receives properly formatted request"""
        classification = {"type": "help_request", "cognitive_state": "planning"}

        response_generator.generate_response(
            classification=classification,
            prompt="How do I implement a circular queue?",
            context={"code": "def enqueue():"}
        )

        # Verify the tutor received correct data
        call_args = mock_tutor.process_request.call_args
        tutor_request = call_args[0][0]

        assert tutor_request["prompt"] == "How do I implement a circular queue?"
        assert tutor_request["cognitive_state"] == "planning"
        assert "code" in tutor_request["context"]

    def test_tutor_response_with_empty_context(self, response_generator, mock_tutor):
        """Test tutor response when context is None"""
        classification = {"type": "help_request", "cognitive_state": "exploration"}

        response_generator.generate_response(
            classification=classification,
            prompt="What is recursion?",
            context=None
        )

        call_args = mock_tutor.process_request.call_args
        tutor_request = call_args[0][0]

        assert tutor_request["context"] == {}


# ============================================================================
# Evaluation Response Tests
# ============================================================================

class TestEvaluationResponse:
    """Tests for evaluation response generation"""

    def test_evaluator_receives_session_id(self, response_generator, mock_evaluator):
        """Test that evaluator receives session ID"""
        classification = {"type": "evaluation_request", "cognitive_state": "reflection"}

        response_generator.generate_response(
            classification=classification,
            prompt="Evaluate",
            session_id="test-session-456"
        )

        mock_evaluator.evaluate_process.assert_called_once_with(
            session_id="test-session-456",
            context={}
        )

    def test_evaluator_receives_context(self, response_generator, mock_evaluator):
        """Test that evaluator receives context"""
        classification = {"type": "evaluation_request", "cognitive_state": "reflection"}
        context = {"traces": ["trace1", "trace2"], "activity": "queue_implementation"}

        response_generator.generate_response(
            classification=classification,
            prompt="Evaluate my work",
            context=context,
            session_id="session-789"
        )

        mock_evaluator.evaluate_process.assert_called_once_with(
            session_id="session-789",
            context=context
        )


# ============================================================================
# Simulator Response Tests
# ============================================================================

class TestSimulatorResponse:
    """Tests for simulator response generation"""

    def test_get_simulator_creates_po_simulator(self, response_generator):
        """Test that PO simulator is created on first access"""
        simulator = response_generator._get_simulator("PO")

        assert simulator is not None
        assert "PO" in response_generator._simulators

    def test_get_simulator_creates_sm_simulator(self, response_generator):
        """Test that SM simulator is created on first access"""
        simulator = response_generator._get_simulator("SM")

        assert simulator is not None
        assert "SM" in response_generator._simulators

    def test_get_simulator_creates_it_simulator(self, response_generator):
        """Test that IT simulator is created on first access"""
        simulator = response_generator._get_simulator("IT")

        assert simulator is not None
        assert "IT" in response_generator._simulators

    def test_get_simulator_returns_none_for_unknown(self, response_generator):
        """Test that unknown simulator type returns None"""
        simulator = response_generator._get_simulator("UNKNOWN")

        assert simulator is None

    def test_get_simulator_reuses_existing(self, response_generator):
        """Test that simulators are reused (lazy loading)"""
        simulator1 = response_generator._get_simulator("PO")
        simulator2 = response_generator._get_simulator("PO")

        assert simulator1 is simulator2

    def test_simulator_unavailable_message(self, response_generator):
        """Test message when simulator is unavailable"""
        response = response_generator._generate_simulator_response(
            simulator_type="NONEXISTENT",
            prompt="Test",
            context=None
        )

        assert "no disponible" in response


# ============================================================================
# Default Response Tests
# ============================================================================

class TestDefaultResponse:
    """Tests for default response generation"""

    def test_default_response_content(self, response_generator):
        """Test that default response has appropriate content"""
        response = response_generator._generate_default_response("Some unrecognized prompt")

        assert "No puedo procesar tu solicitud" in response
        assert "reformular" in response.lower() or "específico" in response.lower()


# ============================================================================
# Integration Tests
# ============================================================================

class TestResponseGeneratorIntegration:
    """Integration tests for ResponseGenerator"""

    def test_full_help_request_flow(self, mock_tutor, mock_evaluator, mock_llm_provider):
        """Test complete flow for help request"""
        mock_tutor.process_request.return_value = "Let me explain queues step by step..."

        generator = ResponseGenerator(
            tutor=mock_tutor,
            evaluator=mock_evaluator,
            llm_provider=mock_llm_provider
        )

        response = generator.generate_response(
            classification={"type": "help_request", "cognitive_state": "exploration"},
            prompt="Explain queues",
            context={"activity": "queue_tp"},
            session_id="integration-test-session"
        )

        assert response == "Let me explain queues step by step..."

    def test_multiple_request_types_in_sequence(self, response_generator, mock_tutor, mock_evaluator):
        """Test handling multiple request types"""
        # First request: help
        response1 = response_generator.generate_response(
            classification={"type": "help_request", "cognitive_state": "exploration"},
            prompt="What is a stack?"
        )

        # Second request: evaluation
        response2 = response_generator.generate_response(
            classification={"type": "evaluation_request", "cognitive_state": "reflection"},
            prompt="Evaluate",
            session_id="session-multi"
        )

        # Verify both were called
        assert mock_tutor.process_request.called
        assert mock_evaluator.evaluate_process.called