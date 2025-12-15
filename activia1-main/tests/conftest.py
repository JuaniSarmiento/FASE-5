"""
Pytest fixtures and configuration

Provides reusable test fixtures for:
- Mock LLM providers
- Test sessions
- Sample cognitive traces
- Test data builders
"""
import os

# IMPORTANT: Set environment variables BEFORE importing any backend modules
# This prevents RuntimeError from backend.api.config requiring SECRET_KEY
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only-not-for-production-use-12345")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-for-pytest-only-not-for-production")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("ENVIRONMENT", "testing")

import pytest
from datetime import datetime
from typing import Dict, Any, List
from uuid import uuid4

from backend.models.trace import (
    CognitiveTrace,
    TraceSequence,
    TraceLevel,
    InteractionType,
)
from backend.core.cognitive_engine import CognitiveState
from backend.models.risk import (
    Risk,
    RiskType,
    RiskLevel,
    RiskDimension,
)
from backend.models.evaluation import (
    EvaluationReport,
    CompetencyLevel,
    EvaluationDimension,
)
from backend.llm.base import LLMProvider, LLMMessage, LLMRole, LLMResponse


# ============================================================================
# Mock LLM Provider
# ============================================================================

class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing without external API calls"""

    def __init__(self, responses: Dict[str, str] = None, config: Dict[str, Any] = None):
        super().__init__(config or {})
        self.responses = responses or {}
        self.call_count = 0
        self.last_messages = None

    def generate(self, messages: List[LLMMessage], temperature: float = 0.7, max_tokens: int = None, **kwargs) -> LLMResponse:
        """Generate mock response based on message patterns"""
        self.call_count += 1
        self.last_messages = messages

        # Get last user message
        user_messages = [m for m in messages if m.role == LLMRole.USER]
        last_message = user_messages[-1].content if user_messages else ""

        # Pattern matching for common prompts
        if "delegación total" in last_message.lower() or "dame el código completo" in last_message.lower():
            content = "DELEGACION_TOTAL"
        elif "qué es una cola" in last_message.lower() or "explain" in last_message.lower():
            content = "CONCEPTUAL_EXPLANATION"
        elif "planeo usar" in last_message.lower() or "plan" in last_message.lower():
            content = "PLANNING"
        else:
            content = self.responses.get(last_message, "Mock response from LLM")

        return LLMResponse(
            content=content,
            model="mock",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            metadata={"temperature": temperature, "max_tokens": max_tokens, "mock": True}
        )

    def generate_stream(self, messages: List[LLMMessage], **kwargs):
        """Generate streaming mock response"""
        response = self.generate(messages, **kwargs)
        for word in response.content.split():
            yield word + " "

    def count_tokens(self, text: str) -> int:
        """Mock token counting"""
        return len(text.split())

    def validate_config(self) -> bool:
        """Always valid for mock"""
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """Return mock model info"""
        return {"model": "mock", "max_tokens": 4096}

    def reset(self):
        """Reset call counter and last messages"""
        self.call_count = 0
        self.last_messages = None


@pytest.fixture
def mock_llm_provider():
    """Fixture providing a mock LLM provider"""
    return MockLLMProvider()


# ============================================================================
# Session and Student Data
# ============================================================================

@pytest.fixture
def student_id() -> str:
    """Fixture providing a test student ID"""
    return "test_student_001"


@pytest.fixture
def activity_id() -> str:
    """Fixture providing a test activity ID"""
    return "prog2_tp1_colas"


@pytest.fixture
def session_id() -> str:
    """Fixture providing a test session ID"""
    return str(uuid4())


# ============================================================================
# Database Session Fixture (Sprint 6)
# ============================================================================

@pytest.fixture(scope="module")
def db_engine():
    """Fixture providing a test database engine (module scope)"""
    from sqlalchemy import create_engine
    from backend.database.base import Base

    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:", echo=False)

    # Create all tables once per module
    Base.metadata.create_all(engine)

    yield engine

    # Cleanup
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Fixture providing a test database session"""
    from sqlalchemy.orm import sessionmaker

    # Create session from module-scoped engine
    Session = sessionmaker(bind=db_engine)
    session = Session()

    yield session

    # Cleanup
    session.rollback()
    session.close()


# ============================================================================
# Cognitive Trace Fixtures
# ============================================================================

@pytest.fixture
def sample_trace_delegacion(student_id: str, activity_id: str) -> CognitiveTrace:
    """Fixture providing a trace representing total delegation"""
    return CognitiveTrace(
        session_id=str(uuid4()),
        student_id=student_id,
        activity_id=activity_id,
        timestamp=datetime.utcnow(),
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.STUDENT_PROMPT,
        cognitive_state=CognitiveState.IMPLEMENTACION,
        content="Dame el código completo de una cola con arreglos",
        ai_involvement=1.0,
        metadata={
            "blocked": True,
            "reason": "Delegación total detectada",
            "prompt_classification": "DELEGACION_TOTAL",
        },
    )


@pytest.fixture
def sample_trace_conceptual(student_id: str, activity_id: str) -> CognitiveTrace:
    """Fixture providing a trace representing conceptual exploration"""
    return CognitiveTrace(
        session_id=str(uuid4()),
        student_id=student_id,
        activity_id=activity_id,
        timestamp=datetime.utcnow(),
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.STUDENT_PROMPT,
        cognitive_state=CognitiveState.EXPLORACION,
        content="¿Qué es una cola y para qué se usa?",
        ai_involvement=0.3,
        metadata={
            "blocked": False,
            "prompt_classification": "CONCEPTUAL_QUESTION",
            "response_type": "conceptual_explanation",
        },
    )


@pytest.fixture
def sample_trace_planning(student_id: str, activity_id: str) -> CognitiveTrace:
    """Fixture providing a trace representing planning"""
    return CognitiveTrace(
        session_id=str(uuid4()),
        student_id=student_id,
        activity_id=activity_id,
        timestamp=datetime.utcnow(),
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.STUDENT_PROMPT,
        cognitive_state=CognitiveState.PLANIFICACION,
        content="Planeo usar un arreglo circular con dos índices. ¿Es correcto?",
        ai_involvement=0.4,
        metadata={
            "blocked": False,
            "prompt_classification": "VALIDATION_REQUEST",
            "response_type": "socratic_question",
        },
    )


@pytest.fixture
def sample_trace_sequence(
    student_id: str,
    activity_id: str,
    sample_trace_delegacion: CognitiveTrace,
    sample_trace_conceptual: CognitiveTrace,
    sample_trace_planning: CognitiveTrace,
) -> TraceSequence:
    """Fixture providing a complete trace sequence"""
    session_id = str(uuid4())

    # Update all traces to same session
    sample_trace_delegacion.session_id = session_id
    sample_trace_conceptual.session_id = session_id
    sample_trace_planning.session_id = session_id

    sequence = TraceSequence(
        id=str(uuid4()),
        session_id=session_id,
        student_id=student_id,
        activity_id=activity_id,
        traces=[
            sample_trace_conceptual,
            sample_trace_planning,
            sample_trace_delegacion,
        ],
        start_time=datetime.utcnow(),
    )

    return sequence


# ============================================================================
# Risk Fixtures
# ============================================================================

@pytest.fixture
def sample_risk_delegacion() -> Risk:
    """Fixture providing a delegation risk"""
    return Risk(
        id=str(uuid4()),
        session_id=str(uuid4()),
        student_id="student_001",
        activity_id="prog2_tp1",
        risk_type=RiskType.COGNITIVE_DELEGATION,
        risk_level=RiskLevel.HIGH,
        dimension=RiskDimension.COGNITIVE,
        description="Estudiante solicitó código completo sin descomposición previa",
        evidence=["Dame el código completo de una cola"],
        impact="Pérdida de oportunidad de aprendizaje, dependencia de IA",
        recommendations=[
            "Promover descomposición del problema",
            "Enseñar estrategias de planificación",
        ],
    )


@pytest.fixture
def sample_risk_superficial() -> Risk:
    """Fixture providing a superficial reasoning risk"""
    return Risk(
        id=str(uuid4()),
        session_id=str(uuid4()),
        student_id="student_001",
        activity_id="prog2_tp1",
        risk_type=RiskType.SUPERFICIAL_REASONING,
        risk_level=RiskLevel.MEDIUM,
        dimension=RiskDimension.COGNITIVE,
        description="Razonamiento superficial sin validación crítica",
        evidence=["Aceptó respuesta sin verificar"],
        impact="Comprensión superficial, errores conceptuales",
        recommendations=[
            "Promover verificación crítica",
            "Enseñar debugging sistemático",
        ],
    )


# ============================================================================
# Evaluation Fixtures
# ============================================================================

@pytest.fixture
def sample_evaluation_report(student_id: str, activity_id: str) -> EvaluationReport:
    """Fixture providing a sample evaluation report"""
    from backend.models.evaluation import ReasoningAnalysis

    return EvaluationReport(
        id=f"eval_{uuid4()}",
        session_id=str(uuid4()),
        student_id=student_id,
        activity_id=activity_id,
        reasoning_analysis=ReasoningAnalysis(
            cognitive_path=["Exploración", "Planificación", "Implementación"],
            phases_completed=[],
            coherence_score=0.7,
            planning_quality=0.6,
            self_explanation_quality=0.65,
        ),
        ai_dependency_score=0.5,
        overall_competency_level=CompetencyLevel.EN_DESARROLLO,
        overall_score=6.5,
        dimensions=[
            EvaluationDimension(
                name="Descomposición de Problemas",
                description="Capacidad de descomponer problemas complejos",
                score=7.0,
                level=CompetencyLevel.EN_DESARROLLO,
                evidence=["Descompuso el problema en 3 pasos"],
            ),
            EvaluationDimension(
                name="Autorregulación",
                description="Capacidad de monitorear y regular el proceso",
                score=6.0,
                level=CompetencyLevel.EN_DESARROLLO,
                evidence=["Verificó resultados parcialmente"],
            ),
        ],
        key_strengths=[
            "Buena descomposición inicial del problema",
            "Identificó casos edge",
        ],
        improvement_areas=[
            "Necesita mejorar verificación sistemática",
            "Debería documentar decisiones de diseño",
        ],
    )


# ============================================================================
# Test Data Builders
# ============================================================================

class TraceBuilder:
    """Builder pattern for creating test traces"""

    def __init__(self):
        self.trace = CognitiveTrace(
            session_id=str(uuid4()),
            student_id="test_student",
            activity_id="test_activity",
            timestamp=datetime.utcnow(),
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.EXPLORACION,
            content="Test content",
            ai_involvement=0.5,
            metadata={},
        )

    def with_session(self, session_id: str) -> 'TraceBuilder':
        self.trace.session_id = session_id
        return self

    def with_student(self, student_id: str) -> 'TraceBuilder':
        self.trace.student_id = student_id
        return self

    def with_cognitive_state(self, state: CognitiveState) -> 'TraceBuilder':
        self.trace.cognitive_state = state
        return self

    def with_content(self, content: str) -> 'TraceBuilder':
        self.trace.content = content
        return self

    def with_ai_involvement(self, involvement: float) -> 'TraceBuilder':
        self.trace.ai_involvement = involvement
        return self

    def blocked(self, reason: str) -> 'TraceBuilder':
        self.trace.metadata["blocked"] = True
        self.trace.metadata["reason"] = reason
        return self

    def build(self) -> CognitiveTrace:
        return self.trace


@pytest.fixture
def trace_builder():
    """Fixture providing a trace builder"""
    return TraceBuilder


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def test_config() -> Dict[str, Any]:
    """Fixture providing test configuration"""
    return {
        "llm_provider": "mock",
        "max_ai_dependency": 0.7,
        "block_full_delegation": True,
        "enable_n4_traceability": True,
        "enable_risk_analysis": True,
    }


# ============================================================================
# Clean up
# ============================================================================

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset any singleton instances between tests"""
    yield
    # Add cleanup code here if needed
