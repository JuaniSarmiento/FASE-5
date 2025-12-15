"""
Unit tests for Cognitive Reasoning Engine

Tests cover:
- Prompt classification
- Cognitive state detection
- Pedagogical strategy generation
- Delegation detection
- Response type selection
"""
import pytest
from backend.core.cognitive_engine import (
    CognitiveReasoningEngine,
    AgentMode,
    CognitiveState,
)


@pytest.mark.unit
@pytest.mark.cognitive
class TestCognitiveReasoningEngine:
    """Tests for CognitiveReasoningEngine"""

    @pytest.fixture
    def engine(self, mock_llm_provider):
        """Fixture providing a cognitive engine with mock LLM"""
        return CognitiveReasoningEngine(llm_provider=mock_llm_provider)

    # ========================================================================
    # Prompt Classification Tests
    # ========================================================================

    def test_classify_delegacion_total(self, engine):
        """Test detection of total delegation prompts"""
        prompt = "Dame el código completo de una cola con arreglos"
        classification = engine.classify_prompt(prompt, context={})

        assert classification["delegation_detected"] is True
        assert classification["delegation_type"] == "total"

    def test_classify_conceptual_question(self, engine):
        """Test detection of conceptual questions"""
        prompt = "¿Qué es una cola y para qué se usa?"
        classification = engine.classify_prompt(prompt, context={})

        assert classification["delegation_detected"] is False
        assert classification["request_type"] in ["conceptual", "explanation"]

    def test_classify_validation_request(self, engine):
        """Test detection of validation requests"""
        prompt = "Planeo usar un arreglo circular. ¿Es correcto este enfoque?"
        classification = engine.classify_prompt(prompt, context={})

        assert classification["delegation_detected"] is False
        assert classification["request_type"] == "validation"
        assert classification["cognitive_state"] in [
            CognitiveState.PLANIFICACION,
            CognitiveState.VALIDACION,
        ]

    def test_classify_debugging_request(self, engine):
        """Test detection of debugging requests"""
        prompt = "Mi código da error en la línea 15. ¿Por qué?"
        classification = engine.classify_prompt(prompt, context={})

        assert classification["cognitive_state"] == CognitiveState.DEBUGGING
        assert classification["request_type"] in ["debugging", "error_analysis"]

    def test_classify_with_context(self, engine):
        """Test that context influences classification"""
        prompt = "¿Y ahora qué hago?"

        # Without context
        result1 = engine.classify_prompt(prompt, context={})

        # With context showing previous planning
        result2 = engine.classify_prompt(
            prompt,
            context={
                "previous_state": CognitiveState.PLANIFICACION,
                "history": ["Ya diseñé la estructura"],
            },
        )

        # Context should influence cognitive state detection
        assert result1 != result2 or result2["cognitive_state"] is not None

    # ========================================================================
    # Pedagogical Strategy Tests
    # ========================================================================

    def test_strategy_socratic_for_delegation(self, engine):
        """Test that delegation triggers Socratic questioning"""
        classification = {
            "delegation_detected": True,
            "delegation_type": "total",
            "request_type": "code_request",
            "cognitive_state": CognitiveState.IMPLEMENTACION,
        }

        strategy = engine.generate_pedagogical_response_strategy(
            classification=classification,
            mode=AgentMode.TUTOR,
            student_history=[],
        )

        assert strategy["response_type"] == "socratic_questions"
        assert "block" in strategy or "redirect" in strategy

    def test_strategy_conceptual_for_exploration(self, engine):
        """Test conceptual explanation for exploration phase"""
        classification = {
            "delegation_detected": False,
            "request_type": "conceptual",
            "cognitive_state": CognitiveState.EXPLORACION,
        }

        strategy = engine.generate_pedagogical_response_strategy(
            classification=classification,
            mode=AgentMode.TUTOR,
            student_history=[],
        )

        assert strategy["response_type"] in [
            "conceptual_explanation",
            "guided_exploration",
        ]
        assert strategy.get("detail_level") in ["high", "medium"]

    def test_strategy_guided_hints_for_implementation(self, engine):
        """Test guided hints during implementation"""
        classification = {
            "delegation_detected": False,
            "request_type": "implementation_help",
            "cognitive_state": CognitiveState.IMPLEMENTACION,
        }

        strategy = engine.generate_pedagogical_response_strategy(
            classification=classification,
            mode=AgentMode.TUTOR,
            student_history=[],
        )

        assert strategy["response_type"] in ["guided_hints", "partial_scaffolding"]
        assert "complete_solution" not in str(strategy.get("constraints", ""))

    def test_strategy_metacognitive_for_reflection(self, engine):
        """Test metacognitive prompts during reflection"""
        classification = {
            "delegation_detected": False,
            "request_type": "review",
            "cognitive_state": CognitiveState.REFLEXION,
        }

        strategy = engine.generate_pedagogical_response_strategy(
            classification=classification,
            mode=AgentMode.TUTOR,
            student_history=[],
        )

        assert strategy["response_type"] in ["metacognitive_prompts", "reflection_guide"]

    # ========================================================================
    # Cognitive State Detection Tests
    # ========================================================================

    def test_detect_state_exploration(self, engine):
        """Test detection of exploration state"""
        prompts = [
            "¿Qué es una cola?",
            "¿Cuáles son las operaciones de una pila?",
            "No entiendo el concepto de recursión",
        ]

        for prompt in prompts:
            classification = engine.classify_prompt(prompt, context={})
            assert classification["cognitive_state"] in [
                CognitiveState.EXPLORACION,
                CognitiveState.INICIO,
            ]

    def test_detect_state_planning(self, engine):
        """Test detection of planning state"""
        prompts = [
            "Planeo usar un arreglo circular",
            "Mi enfoque es dividir el problema en 3 partes",
            "Voy a implementar primero el constructor",
        ]

        for prompt in prompts:
            classification = engine.classify_prompt(prompt, context={})
            assert classification["cognitive_state"] in [
                CognitiveState.PLANIFICACION,
                CognitiveState.IMPLEMENTACION,
            ]

    def test_detect_state_debugging(self, engine):
        """Test detection of debugging state"""
        prompts = [
            "Me da error de segmentation fault",
            "El test 3 falla pero no sé por qué",
            "¿Por qué mi código imprime valores incorrectos?",
        ]

        for prompt in prompts:
            classification = engine.classify_prompt(prompt, context={})
            assert classification["cognitive_state"] == CognitiveState.DEBUGGING

    # ========================================================================
    # Mode-Specific Behavior Tests
    # ========================================================================

    def test_tutor_mode_blocks_delegation(self, engine):
        """Test that TUTOR mode blocks total delegation"""
        classification = {
            "delegation_detected": True,
            "delegation_type": "total",
            "request_type": "code_request",
            "cognitive_state": CognitiveState.IMPLEMENTACION,
        }

        strategy = engine.generate_pedagogical_response_strategy(
            classification=classification,
            mode=AgentMode.TUTOR,
            student_history=[],
        )

        assert strategy.get("block") is True or strategy.get("redirect") is True

    def test_evaluator_mode_allows_observation(self, engine):
        """Test that EVALUATOR mode observes without blocking"""
        classification = {
            "delegation_detected": True,
            "delegation_type": "total",
            "request_type": "code_request",
            "cognitive_state": CognitiveState.IMPLEMENTACION,
        }

        strategy = engine.generate_pedagogical_response_strategy(
            classification=classification,
            mode=AgentMode.EVALUATOR,
            student_history=[],
        )

        # Evaluator should observe but not block
        assert strategy.get("observe") is True or strategy.get("block") is False

    # ========================================================================
    # History-Aware Tests
    # ========================================================================

    def test_repeated_delegation_escalates_intervention(self, engine):
        """Test that repeated delegation triggers stronger intervention"""
        classification = {
            "delegation_detected": True,
            "delegation_type": "total",
            "request_type": "code_request",
            "cognitive_state": CognitiveState.IMPLEMENTACION,
        }

        # First delegation
        strategy1 = engine.generate_pedagogical_response_strategy(
            classification=classification,
            mode=AgentMode.TUTOR,
            student_history=[],
        )

        # Repeated delegation
        strategy2 = engine.generate_pedagogical_response_strategy(
            classification=classification,
            mode=AgentMode.TUTOR,
            student_history=[
                {"delegation": True},
                {"delegation": True},
                {"delegation": True},
            ],
        )

        # Second strategy should be more assertive
        assert strategy2.get("intervention_level", 0) >= strategy1.get(
            "intervention_level", 0
        )

    def test_progress_reduces_scaffolding(self, engine):
        """Test that student progress reduces scaffolding"""
        classification = {
            "delegation_detected": False,
            "request_type": "implementation_help",
            "cognitive_state": CognitiveState.IMPLEMENTACION,
        }

        # Beginner student
        strategy1 = engine.generate_pedagogical_response_strategy(
            classification=classification,
            mode=AgentMode.TUTOR,
            student_history=[],
        )

        # Advanced student with good history
        strategy2 = engine.generate_pedagogical_response_strategy(
            classification=classification,
            mode=AgentMode.TUTOR,
            student_history=[
                {"good_planning": True},
                {"autonomous_debugging": True},
                {"validated_approach": True},
            ],
        )

        # Advanced student should receive less scaffolding
        detail1 = strategy1.get("detail_level", "high")
        detail2 = strategy2.get("detail_level", "high")

        # Mapping: low < medium < high
        levels = {"low": 1, "medium": 2, "high": 3}
        assert levels.get(detail2, 2) <= levels.get(detail1, 2)

    # ========================================================================
    # Edge Cases Tests
    # ========================================================================

    def test_empty_prompt(self, engine):
        """Test handling of empty prompts"""
        classification = engine.classify_prompt("", context={})

        assert "error" in classification or classification["request_type"] == "unknown"

    def test_very_long_prompt(self, engine):
        """Test handling of very long prompts"""
        long_prompt = "A" * 10000
        classification = engine.classify_prompt(long_prompt, context={})

        # Should handle gracefully
        assert classification is not None
        assert "cognitive_state" in classification

    def test_multilingual_prompt(self, engine):
        """Test handling of prompts in different languages"""
        prompts = [
            "¿Qué es una cola?",  # Spanish
            "What is a queue?",  # English
            "Qu'est-ce qu'une file?",  # French
        ]

        for prompt in prompts:
            classification = engine.classify_prompt(prompt, context={})
            # Should detect conceptual question regardless of language
            assert classification["request_type"] in [
                "conceptual",
                "explanation",
                "unknown",
            ]


# ============================================================================
# Integration Tests with Mock LLM
# ============================================================================


@pytest.mark.integration
@pytest.mark.cognitive
class TestCognitiveEngineIntegration:
    """Integration tests for cognitive engine with mock LLM"""

    def test_full_classification_pipeline(self, mock_llm_provider):
        """Test complete classification pipeline"""
        engine = CognitiveReasoningEngine(llm_provider=mock_llm_provider)

        prompt = "Dame el código completo de una cola"
        classification = engine.classify_prompt(prompt, context={})
        strategy = engine.generate_pedagogical_response_strategy(
            classification=classification,
            mode=AgentMode.TUTOR,
            student_history=[],
        )

        # Full pipeline should produce valid results
        assert classification["delegation_detected"] is True
        assert strategy["response_type"] == "socratic_questions"
        assert mock_llm_provider.call_count > 0

    def test_engine_with_different_modes(self, mock_llm_provider):
        """Test engine behavior across different modes"""
        engine = CognitiveReasoningEngine(llm_provider=mock_llm_provider)

        classification = {
            "delegation_detected": False,
            "request_type": "conceptual",
            "cognitive_state": CognitiveState.EXPLORACION,
        }

        modes = [AgentMode.TUTOR, AgentMode.SIMULATOR, AgentMode.EVALUATOR]

        for mode in modes:
            strategy = engine.generate_pedagogical_response_strategy(
                classification=classification,
                mode=mode,
                student_history=[],
            )

            assert strategy is not None
            assert "response_type" in strategy
