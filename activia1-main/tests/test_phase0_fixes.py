"""
Tests for Phase 0 Critical Fixes (2025-11-21)

Verifies that the 4 critical corrections applied prevent runtime errors:
1. timestamp ↔ created_at property mapping
2. metadata ↔ trace_metadata property mapping
3. AgentMode uppercase unification
4. recommendations field persistence
"""
import pytest
from datetime import datetime, timezone

from backend.database.models import CognitiveTraceDB, SessionDB, EvaluationDB
from backend.core.cognitive_engine import AgentMode
from backend.models.evaluation import (
    EvaluationReport,
    CompetencyLevel,
    EvaluationDimension,
    ReasoningAnalysis,
)
from backend.database.repositories import EvaluationRepository


# =============================================================================
# Fix 1: timestamp property in BaseModel
# =============================================================================


def test_orm_timestamp_property():
    """
    Verify BaseModel.timestamp property works correctly.

    BEFORE FIX: AttributeError: 'CognitiveTraceDB' object has no attribute 'timestamp'
    AFTER FIX: trace.timestamp returns trace.created_at
    """
    # Create trace with created_at
    trace = CognitiveTraceDB(
        id="trace_001",
        session_id="session_001",
        student_id="student_001",
        activity_id="prog2_tp1",
        trace_level="n4_cognitivo",
        interaction_type="student_prompt",
        content="¿Cómo implemento una cola circular?",
        created_at=datetime.now(timezone.utc),
    )

    # Verify timestamp property exists and works
    assert hasattr(trace, "timestamp"), "BaseModel should have 'timestamp' property"
    assert trace.timestamp == trace.created_at, "timestamp should return created_at"
    assert isinstance(trace.timestamp, datetime), "timestamp should be datetime"


def test_session_timestamp_property():
    """Verify SessionDB also has timestamp property (inherited from BaseModel)"""
    session = SessionDB(
        id="session_001",
        student_id="student_001",
        activity_id="prog2_tp1",
        mode="TUTOR",
        created_at=datetime.now(timezone.utc),
    )

    assert hasattr(session, "timestamp")
    assert session.timestamp == session.created_at


# =============================================================================
# Fix 2: metadata property in CognitiveTraceDB
# =============================================================================


def test_orm_metadata_property():
    """
    Verify CognitiveTraceDB.trace_metadata field works correctly.

    NOTE: SQLAlchemy reserves 'metadata' keyword, so we use 'trace_metadata'.
    API layer maps trace_metadata -> metadata in response DTOs.
    """
    # Create trace with trace_metadata
    trace = CognitiveTraceDB(
        id="trace_001",
        session_id="session_001",
        student_id="student_001",
        activity_id="prog2_tp1",
        trace_level="n4_cognitivo",
        interaction_type="student_prompt",
        content="Test content",
        trace_metadata={"agent_used": "T-IA-Cog", "blocked": False},
    )

    # Verify trace_metadata field exists and works
    assert hasattr(trace, "trace_metadata"), "CognitiveTraceDB should have 'trace_metadata' field"
    assert trace.trace_metadata.get("agent_used") == "T-IA-Cog"
    assert trace.trace_metadata.get("blocked") is False


def test_metadata_property_with_empty_dict():
    """Verify trace_metadata field works with empty dict (default)"""
    trace = CognitiveTraceDB(
        id="trace_001",
        session_id="session_001",
        student_id="student_001",
        activity_id="prog2_tp1",
        trace_level="n4_cognitivo",
        interaction_type="student_prompt",
        content="Test content",
        trace_metadata={},  # Empty dict
    )

    assert trace.trace_metadata == {}
    assert trace.trace_metadata.get("nonexistent") is None


# =============================================================================
# Fix 3: AgentMode uppercase unification
# =============================================================================


def test_agent_mode_uppercase_values():
    """
    Verify AgentMode uses UPPERCASE values consistently.

    BEFORE FIX: AgentMode.TUTOR == "tutor" (lowercase)
    AFTER FIX: AgentMode.TUTOR == "TUTOR" (uppercase)
    """
    assert AgentMode.TUTOR.value == "TUTOR", "AgentMode.TUTOR should be UPPERCASE"
    assert AgentMode.EVALUATOR.value == "EVALUATOR"
    assert AgentMode.SIMULATOR.value == "SIMULATOR"
    assert AgentMode.RISK_ANALYST.value == "RISK_ANALYST"
    assert AgentMode.GOVERNANCE.value == "GOVERNANCE"


def test_agent_mode_comparison_with_uppercase():
    """Verify AgentMode values can be compared with uppercase strings"""
    mode = AgentMode.TUTOR

    # This should work now (UPPERCASE comparison)
    assert mode.value == "TUTOR"
    assert mode == AgentMode.TUTOR

    # String comparison
    assert str(mode.value) == "TUTOR"


def test_agent_mode_database_compatibility():
    """Verify AgentMode can be stored in database as UPPERCASE"""
    session = SessionDB(
        id="session_001",
        student_id="student_001",
        activity_id="prog2_tp1",
        mode=AgentMode.TUTOR.value,  # Store as "TUTOR"
    )

    assert session.mode == "TUTOR"
    assert session.mode == AgentMode.TUTOR.value


def test_session_mode_alias_backward_compatibility():
    """
    Verify SessionMode is alias to AgentMode (backward compatibility).

    BEFORE FIX: SessionMode was separate enum with duplicate values
    AFTER FIX: SessionMode = AgentMode (alias)
    """
    from backend.api.schemas.enums import SessionMode

    # SessionMode should be the same as AgentMode
    assert SessionMode is AgentMode, "SessionMode should be alias to AgentMode"

    # Values should match
    assert SessionMode.TUTOR == AgentMode.TUTOR
    assert SessionMode.EVALUATOR == AgentMode.EVALUATOR


# =============================================================================
# Fix 4: recommendations field persistence in EvaluationRepository
# =============================================================================


def test_evaluation_recommendations_persistence(db_session):
    """
    Verify recommendations are persisted correctly in database.

    BEFORE FIX: getattr(evaluation, "recommendations", []) returns [] (field doesn't exist)
    AFTER FIX: Combines recommendations_student + recommendations_teacher into JSON
    """
    # Create evaluation with separate student/teacher recommendations
    evaluation = EvaluationReport(
        id="eval_001",
        session_id="session_001",
        student_id="student_001",
        activity_id="prog2_tp1",
        reasoning_analysis=ReasoningAnalysis(
            coherence_score=0.8,
            planning_quality=0.7,
            self_explanation_quality=0.75
        ),
        dimensions=[
            EvaluationDimension(
                name="Problem Solving",
                description="Ability to solve problems",
                level=CompetencyLevel.EN_DESARROLLO,
                score=7.5,
            )
        ],
        ai_dependency_score=0.35,
        overall_competency_level=CompetencyLevel.EN_DESARROLLO,
        overall_score=7.5,
        recommendations_student=[
            "Practica más con estructuras de datos",
            "Revisa conceptos de recursión",
        ],
        recommendations_teacher=[
            "Asignar ejercicios adicionales de colas",
            "Considerar sesión de tutoría",
        ],
    )

    # Persist to database
    repo = EvaluationRepository(db_session)
    db_eval = repo.create(evaluation)

    # Verify recommendations are combined correctly in database
    assert isinstance(
        db_eval.recommendations, dict
    ), "recommendations should be dict in DB"
    assert "student" in db_eval.recommendations, "Should have 'student' key"
    assert "teacher" in db_eval.recommendations, "Should have 'teacher' key"

    # Verify student recommendations
    student_recs = db_eval.recommendations["student"]
    assert len(student_recs) == 2
    assert "Practica más con estructuras de datos" in student_recs
    assert "Revisa conceptos de recursión" in student_recs

    # Verify teacher recommendations
    teacher_recs = db_eval.recommendations["teacher"]
    assert len(teacher_recs) == 2
    assert "Asignar ejercicios adicionales de colas" in teacher_recs
    assert "Considerar sesión de tutoría" in teacher_recs


def test_evaluation_recommendations_empty_lists(db_session):
    """Verify recommendations work with empty lists"""
    evaluation = EvaluationReport(
        id="eval_002",
        session_id="session_002",
        student_id="student_002",
        activity_id="prog2_tp1",
        reasoning_analysis=ReasoningAnalysis(
            coherence_score=0.9,
            planning_quality=0.85,
            self_explanation_quality=0.9
        ),
        dimensions=[],
        ai_dependency_score=0.2,
        overall_competency_level=CompetencyLevel.AUTONOMO,
        overall_score=9.0,
        recommendations_student=[],  # Empty
        recommendations_teacher=[],  # Empty
    )

    repo = EvaluationRepository(db_session)
    db_eval = repo.create(evaluation)

    # Should still create dict structure even with empty lists
    assert isinstance(db_eval.recommendations, dict)
    assert db_eval.recommendations["student"] == []
    assert db_eval.recommendations["teacher"] == []


# =============================================================================
# Integration test: All fixes together
# =============================================================================


def test_all_fixes_integration(db_session):
    """
    Integration test verifying all 4 fixes work together in realistic scenario.

    Simulates creating a complete learning session with traces and evaluation.
    """
    # 1. Create session with AgentMode (Fix 3)
    session = SessionDB(
        id="session_integration",
        student_id="student_001",
        activity_id="prog2_tp1",
        mode=AgentMode.TUTOR.value,  # ✅ UPPERCASE value
    )
    db_session.add(session)
    db_session.commit()

    # 2. Create trace with metadata (Fix 1 & 2)
    trace = CognitiveTraceDB(
        id="trace_integration",
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        trace_level="n4_cognitivo",
        interaction_type="student_prompt",
        content="¿Cómo implemento una cola?",
        trace_metadata={"agent_used": "T-IA-Cog", "ai_involvement": 0.3},
    )
    db_session.add(trace)
    db_session.commit()

    # Verify timestamp property (Fix 1)
    assert hasattr(trace, "timestamp")
    assert trace.timestamp is not None

    # Verify trace_metadata field (Fix 2)
    assert hasattr(trace, "trace_metadata")
    assert trace.trace_metadata.get("agent_used") == "T-IA-Cog"

    # 3. Create evaluation with recommendations (Fix 4)
    evaluation = EvaluationReport(
        id="eval_integration",
        session_id=session.id,
        student_id="student_001",
        activity_id="prog2_tp1",
        reasoning_analysis=ReasoningAnalysis(
            coherence_score=0.75,
            planning_quality=0.7,
            self_explanation_quality=0.72
        ),
        dimensions=[],
        ai_dependency_score=0.3,
        overall_competency_level=CompetencyLevel.EN_DESARROLLO,
        overall_score=7.0,
        recommendations_student=["Keep practicing"],
        recommendations_teacher=["Monitor progress"],
    )

    repo = EvaluationRepository(db_session)
    db_eval = repo.create(evaluation)

    # Verify recommendations persisted correctly (Fix 4)
    assert db_eval.recommendations["student"] == ["Keep practicing"]
    assert db_eval.recommendations["teacher"] == ["Monitor progress"]

    # Verify session mode (Fix 3)
    assert session.mode == "TUTOR"
    assert session.mode == AgentMode.TUTOR.value

    print("✅ All 4 Phase 0 fixes working correctly in integration scenario")


# =============================================================================
# Pytest configuration
# =============================================================================


@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.database.base import Base

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()


if __name__ == "__main__":
    """Run tests standalone"""
    pytest.main([__file__, "-v", "--tb=short"])
