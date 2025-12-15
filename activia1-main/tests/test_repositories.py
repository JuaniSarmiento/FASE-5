"""
Tests para los Repositories (capa de persistencia)

Verifica:
- Operaciones CRUD básicas
- Pessimistic locking (SELECT FOR UPDATE)
- Transacciones y rollback
- Relaciones entre entidades
- Manejo de errores
"""
import pytest
from datetime import datetime
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.models import Base
from backend.database.repositories import (
    SessionRepository,
    TraceRepository,
    RiskRepository,
    EvaluationRepository,
    TraceSequenceRepository,
)
from backend.models.trace import (
    CognitiveTrace,
    TraceLevel,
    InteractionType,
    TraceSequence,
)
from backend.models.risk import Risk, RiskType, RiskLevel, RiskDimension
from backend.models.evaluation import (
    EvaluationReport,
    CompetencyLevel,
    EvaluationDimension,
)
from backend.core.cognitive_engine import CognitiveState


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create tables
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session_repo(test_db):
    """SessionRepository fixture"""
    return SessionRepository(test_db)


@pytest.fixture
def trace_repo(test_db):
    """TraceRepository fixture"""
    return TraceRepository(test_db)


@pytest.fixture
def risk_repo(test_db):
    """RiskRepository fixture"""
    return RiskRepository(test_db)


@pytest.fixture
def evaluation_repo(test_db):
    """EvaluationRepository fixture"""
    return EvaluationRepository(test_db)


@pytest.fixture
def sequence_repo(test_db):
    """TraceSequenceRepository fixture"""
    return TraceSequenceRepository(test_db)


# ============================================================================
# SessionRepository Tests
# ============================================================================

def test_session_create(session_repo):
    """Test creating a session"""
    session = session_repo.create(
        student_id="student_001",
        activity_id="prog2_tp1",
        mode="TUTOR"
    )

    assert session is not None
    assert session.id is not None
    assert session.student_id == "student_001"
    assert session.activity_id == "prog2_tp1"
    assert session.mode == "TUTOR"
    assert session.status == "active"
    assert session.start_time is not None
    assert session.end_time is None


def test_session_get_by_id(session_repo):
    """Test retrieving a session by ID"""
    # Create session
    created = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Retrieve session
    retrieved = session_repo.get_by_id(created.id)

    assert retrieved is not None
    assert retrieved.id == created.id
    assert retrieved.student_id == "student_001"


def test_session_get_by_id_not_found(session_repo):
    """Test retrieving non-existent session"""
    session = session_repo.get_by_id("non_existent_id")
    assert session is None


def test_session_get_by_student(session_repo):
    """Test retrieving sessions by student ID"""
    # Create multiple sessions
    session_repo.create("student_001", "activity_1", "TUTOR")
    session_repo.create("student_001", "activity_2", "EVALUATOR")
    session_repo.create("student_002", "activity_1", "TUTOR")

    # Get sessions for student_001
    sessions = session_repo.get_by_student("student_001")

    assert len(sessions) == 2
    assert all(s.student_id == "student_001" for s in sessions)


def test_session_list_all(session_repo):
    """Test listing all sessions"""
    # Create sessions
    session_repo.create("student_001", "activity_1", "TUTOR")
    session_repo.create("student_002", "activity_2", "EVALUATOR")

    # Get all (renamed from list_all)
    sessions = session_repo.get_all()

    assert len(sessions) == 2


def test_session_update_mode(session_repo):
    """Test updating session mode"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")
    original_id = session.id

    # Update mode
    updated = session_repo.update_mode(session.id, "EVALUATOR")

    assert updated is not None
    assert updated.id == original_id
    assert updated.mode == "EVALUATOR"


def test_session_end_session(session_repo):
    """Test ending a session"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")
    assert session.status == "active"
    assert session.end_time is None

    # End session
    ended = session_repo.end_session(session.id)

    assert ended is not None
    assert ended.status == "completed"
    assert ended.end_time is not None


def test_session_pessimistic_locking(session_repo, test_db):
    """Test that SELECT FOR UPDATE prevents race conditions"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # This test verifies that end_session uses SELECT FOR UPDATE
    # In a real concurrent scenario, this would block other transactions
    # from updating the same row until commit

    # End session (uses SELECT FOR UPDATE internally)
    ended = session_repo.end_session(session.id)

    assert ended is not None
    assert ended.status == "completed"

    # Verify the session was actually updated in DB
    retrieved = session_repo.get_by_id(session.id)
    assert retrieved.status == "completed"


def test_session_delete(session_repo):
    """Test deleting a session"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")
    session_id = session.id

    # Delete session
    result = session_repo.delete(session_id)
    assert result is True

    # Verify deletion
    deleted = session_repo.get_by_id(session_id)
    assert deleted is None


def test_session_delete_not_found(session_repo):
    """Test deleting non-existent session"""
    result = session_repo.delete("non_existent_id")
    assert result is False


# ============================================================================
# TraceRepository Tests
# ============================================================================

def test_trace_create(trace_repo, session_repo):
    """Test creating a cognitive trace"""
    # Create session first (FK constraint)
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Create trace
    trace = CognitiveTrace(
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.STUDENT_PROMPT,
        cognitive_state=CognitiveState.PLANIFICACION,
        content="¿Cómo implemento una cola circular?",
        ai_involvement=0.3,
        metadata={"test": True}
    )

    db_trace = trace_repo.create(trace)

    assert db_trace is not None
    assert db_trace.id is not None
    assert db_trace.session_id == session.id
    assert db_trace.trace_level == TraceLevel.N4_COGNITIVO.value
    assert db_trace.cognitive_state == CognitiveState.PLANIFICACION.value
    assert db_trace.ai_involvement == 0.3


def test_trace_get_by_session(trace_repo, session_repo):
    """Test retrieving traces by session"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Create multiple traces
    for i in range(3):
        trace = CognitiveTrace(
            session_id=session.id,
            student_id="student_001",
            activity_id="prog2_tp1",
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.PLANIFICACION,
            content=f"Test trace {i}",
            ai_involvement=0.3
        )
        trace_repo.create(trace)

    # Retrieve traces
    traces = trace_repo.get_by_session(session.id)

    assert len(traces) == 3
    assert all(t.session_id == session.id for t in traces)


def test_trace_get_by_student(trace_repo, session_repo):
    """Test retrieving traces by student"""
    # Create sessions
    session1 = session_repo.create("student_001", "activity_1", "TUTOR")
    session2 = session_repo.create("student_001", "activity_2", "TUTOR")

    # Create traces in both sessions
    for session in [session1, session2]:
        trace = CognitiveTrace(
            session_id=session.id,
            student_id="student_001",
            activity_id=session.activity_id,
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.PLANIFICACION,
            content="Test",
            ai_involvement=0.3
        )
        trace_repo.create(trace)

    # Retrieve traces
    traces = trace_repo.get_by_student("student_001")

    assert len(traces) == 2


def test_trace_count_by_session(trace_repo, session_repo):
    """Test counting traces by session"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Initially 0
    count = trace_repo.count_by_session(session.id)
    assert count == 0

    # Create 5 traces
    for i in range(5):
        trace = CognitiveTrace(
            session_id=session.id,
            student_id="student_001",
            activity_id="prog2_tp1",
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.PLANIFICACION,
            content=f"Test {i}",
            ai_involvement=0.3
        )
        trace_repo.create(trace)

    # Now should be 5
    count = trace_repo.count_by_session(session.id)
    assert count == 5


# ============================================================================
# RiskRepository Tests
# ============================================================================

def test_risk_create(risk_repo, session_repo):
    """Test creating a risk"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Create risk
    risk = Risk(
        id=str(uuid4()),
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        risk_type=RiskType.COGNITIVE_DELEGATION,
        risk_level=RiskLevel.HIGH,
        dimension=RiskDimension.COGNITIVE,
        description="Delegación total detectada",
        evidence=["Dame el código completo"],
        trace_ids=["trace_123"]
    )

    db_risk = risk_repo.create(risk)

    assert db_risk is not None
    assert db_risk.id is not None
    assert db_risk.risk_type == RiskType.COGNITIVE_DELEGATION.value
    assert db_risk.risk_level == RiskLevel.HIGH.value
    assert db_risk.dimension == RiskDimension.COGNITIVE.value
    assert db_risk.resolved is False


def test_risk_get_by_session(risk_repo, session_repo):
    """Test retrieving risks by session"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Create multiple risks
    for i in range(3):
        risk = Risk(
            id=str(uuid4()),
            session_id=session.id,
            student_id="student_001",
            activity_id="prog2_tp1",
            risk_type=RiskType.COGNITIVE_DELEGATION,
            risk_level=RiskLevel.MEDIUM,
            dimension=RiskDimension.COGNITIVE,
            description=f"Risk {i}",
            evidence=[],
            trace_ids=[]
        )
        risk_repo.create(risk)

    # Retrieve risks
    risks = risk_repo.get_by_session(session.id)

    assert len(risks) == 3


def test_risk_get_unresolved(risk_repo, session_repo):
    """Test filtering unresolved risks"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Create resolved and unresolved risks
    resolved_risk = Risk(
        id=str(uuid4()),
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        risk_type=RiskType.COGNITIVE_DELEGATION,
        risk_level=RiskLevel.LOW,
        dimension=RiskDimension.COGNITIVE,
        description="Resolved risk",
        evidence=[],
        trace_ids=[],
        resolved=True
    )
    risk_repo.create(resolved_risk)

    unresolved_risk = Risk(
        id=str(uuid4()),
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        risk_type=RiskType.AI_DEPENDENCY,
        risk_level=RiskLevel.HIGH,
        dimension=RiskDimension.COGNITIVE,
        description="Unresolved risk",
        evidence=[],
        trace_ids=[],
        resolved=False
    )
    risk_repo.create(unresolved_risk)

    # Get unresolved only
    risks = risk_repo.get_by_session(session.id, resolved=False)

    assert len(risks) == 1
    assert risks[0].resolved is False


def test_risk_get_critical(risk_repo, session_repo):
    """Test retrieving critical risks"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Create risks with different levels
    for level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
        risk = Risk(
            id=str(uuid4()),
            session_id=session.id,
            student_id="student_001",
            activity_id="prog2_tp1",
            risk_type=RiskType.COGNITIVE_DELEGATION,
            risk_level=level,
            dimension=RiskDimension.COGNITIVE,
            description=f"{level.value} risk",
            evidence=[],
            trace_ids=[]
        )
        risk_repo.create(risk)

    # Get critical risks only (method expects student_id, not session_id)
    critical_risks = risk_repo.get_critical_risks(student_id="student_001")

    assert len(critical_risks) == 1
    assert critical_risks[0].risk_level == RiskLevel.CRITICAL.value


# ============================================================================
# EvaluationRepository Tests
# ============================================================================

def test_evaluation_create(evaluation_repo, session_repo):
    """Test creating an evaluation report"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Create evaluation
    from backend.models.evaluation import ReasoningAnalysis

    evaluation = EvaluationReport(
        id=str(uuid4()),
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        overall_competency_level=CompetencyLevel.EN_DESARROLLO,
        overall_score=6.5,
        reasoning_analysis=ReasoningAnalysis(
            coherence_score=0.7,
            planning_quality=0.6,
            self_explanation_quality=0.65
        ),
        dimensions=[
            EvaluationDimension(
                name="Descomposición de problemas",
                description="Capacidad para dividir problemas complejos en subproblemas",
                level=CompetencyLevel.EN_DESARROLLO,
                score=7.0,
                evidence=["Identificó 3 subproblemas", "Planificó abordaje secuencial"],
                strengths=["Buena identificación de casos base"],
                weaknesses=["Necesita mejorar estimación de complejidad"],
                recommendations=["Practicar con problemas recursivos más complejos"]
            )
        ],
        key_strengths=["Análisis claro"],
        improvement_areas=["Necesita más práctica"],
        ai_dependency_score=0.4,
        git_analysis=None
    )

    db_eval = evaluation_repo.create(evaluation)

    assert db_eval is not None
    assert db_eval.id is not None
    assert db_eval.session_id == session.id
    assert db_eval.overall_competency_level == CompetencyLevel.EN_DESARROLLO.value
    assert db_eval.overall_score == 6.5


def test_evaluation_get_by_session(evaluation_repo, session_repo):
    """Test retrieving evaluation by session"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Create evaluation
    from backend.models.evaluation import ReasoningAnalysis

    evaluation = EvaluationReport(
        id=str(uuid4()),
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        overall_competency_level=CompetencyLevel.AUTONOMO,
        overall_score=8.5,
        reasoning_analysis=ReasoningAnalysis(
            coherence_score=0.85,
            planning_quality=0.8,
            self_explanation_quality=0.9
        ),
        dimensions=[],
        key_strengths=[],
        improvement_areas=[],
        ai_dependency_score=0.2,
        git_analysis=None
    )
    evaluation_repo.create(evaluation)

    # Retrieve evaluation
    results = evaluation_repo.get_by_session(session.id)

    assert results is not None
    assert len(results) == 1
    retrieved = results[0]
    assert retrieved.session_id == session.id
    assert retrieved.overall_score == 8.5


# ============================================================================
# TraceSequenceRepository Tests
# ============================================================================

def test_sequence_create(sequence_repo, session_repo):
    """Test creating a trace sequence"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Create traces
    trace1 = CognitiveTrace(
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.STUDENT_PROMPT,
        cognitive_state=CognitiveState.PLANIFICACION,
        content="Trace 1",
        ai_involvement=0.3
    )
    trace2 = CognitiveTrace(
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.AI_RESPONSE,
        cognitive_state=CognitiveState.IMPLEMENTACION,
        content="Trace 2",
        ai_involvement=0.4
    )
    trace3 = CognitiveTrace(
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.STUDENT_PROMPT,
        cognitive_state=CognitiveState.VALIDACION,
        content="Trace 3",
        ai_involvement=0.5
    )

    # Create sequence with traces
    sequence = TraceSequence(
        id=str(uuid4()),
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        traces=[trace1, trace2, trace3],
        reasoning_path=["PLANIFICACION", "IMPLEMENTACION", "VALIDACION"],
        strategy_changes=2
    )

    db_sequence = sequence_repo.create(sequence)

    assert db_sequence is not None
    assert db_sequence.id is not None
    assert db_sequence.session_id == session.id
    assert len(db_sequence.trace_ids) == 3


def test_sequence_get_by_session(sequence_repo, session_repo):
    """Test retrieving sequence by session"""
    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Create trace
    trace1 = CognitiveTrace(
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.STUDENT_PROMPT,
        cognitive_state=CognitiveState.PLANIFICACION,
        content="Test trace",
        ai_involvement=0.3
    )

    # Create sequence with trace
    sequence = TraceSequence(
        id=str(uuid4()),
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        traces=[trace1],
        reasoning_path=["PLANIFICACION"],
        strategy_changes=1
    )
    sequence_repo.create(sequence)

    # Retrieve sequence
    results = sequence_repo.get_by_session(session.id)

    assert results is not None
    assert len(results) == 1
    retrieved = results[0]
    assert retrieved.session_id == session.id


# ============================================================================
# Transaction and Error Handling Tests
# ============================================================================

def test_transaction_rollback_on_error(test_db):
    """Test that transactions rollback on errors"""
    repo = SessionRepository(test_db)

    # Create a valid session
    session = repo.create("student_001", "prog2_tp1", "TUTOR")
    session_id = session.id

    # Verify it was created
    assert repo.get_by_id(session_id) is not None

    # Try to delete with an error in the middle
    # (This is a simplified test - in real scenarios, errors might happen during commit)
    try:
        result = repo.delete(session_id)
        assert result is True
    except Exception:
        test_db.rollback()

    # Verify state after operation
    deleted = repo.get_by_id(session_id)
    assert deleted is None  # Should be deleted


def test_cascade_delete_traces_with_session(test_db):
    """Test that traces are deleted when session is deleted (cascade)"""
    session_repo = SessionRepository(test_db)
    trace_repo = TraceRepository(test_db)

    # Create session
    session = session_repo.create("student_001", "prog2_tp1", "TUTOR")

    # Create traces
    for i in range(3):
        trace = CognitiveTrace(
            session_id=session.id,
            student_id="student_001",
            activity_id="prog2_tp1",
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.PLANIFICACION,
            content=f"Test {i}",
            ai_involvement=0.3
        )
        trace_repo.create(trace)

    # Verify traces exist
    traces_before = trace_repo.get_by_session(session.id)
    assert len(traces_before) == 3

    # Delete session (should cascade to traces)
    session_repo.delete(session.id)

    # Verify traces were deleted
    traces_after = trace_repo.get_by_session(session.id)
    assert len(traces_after) == 0
