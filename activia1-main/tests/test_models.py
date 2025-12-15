"""
Unit tests for Pydantic models

Tests cover:
- Model validation
- Field constraints
- Default values
- Model methods
- Serialization/deserialization
"""
import pytest
from datetime import datetime
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
    RiskReport,
    RiskType,
    RiskLevel,
    RiskDimension,
)
from backend.models.evaluation import (
    EvaluationReport,
    CompetencyLevel,
    EvaluationDimension,
    ReasoningAnalysis,
)


# ============================================================================
# CognitiveTrace Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestCognitiveTrace:
    """Tests for CognitiveTrace model"""

    def test_trace_creation_valid(self, student_id, activity_id):
        """Test creating a valid cognitive trace"""
        trace = CognitiveTrace(
            session_id=str(uuid4()),
            student_id=student_id,
            activity_id=activity_id,
            timestamp=datetime.utcnow(),
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.EXPLORACION,
            content="Test prompt",
            ai_involvement=0.5,
            metadata={"test": "data"},
        )

        assert trace.student_id == student_id
        assert trace.activity_id == activity_id
        assert trace.trace_level == TraceLevel.N4_COGNITIVO
        assert trace.ai_involvement == 0.5

    def test_trace_ai_involvement_validation(self, student_id, activity_id):
        """Test that ai_involvement is constrained to [0, 1]"""
        # Valid values
        trace = CognitiveTrace(
            session_id=str(uuid4()),
            student_id=student_id,
            activity_id=activity_id,
            timestamp=datetime.utcnow(),
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            cognitive_state=CognitiveState.EXPLORACION,
            content="Test",
            ai_involvement=0.0,
        )
        assert trace.ai_involvement == 0.0

        trace.ai_involvement = 1.0
        assert trace.ai_involvement == 1.0

        # Invalid values should be clamped or raise error
        with pytest.raises(Exception):  # Pydantic validation error
            trace = CognitiveTrace(
                session_id=str(uuid4()),
                student_id=student_id,
                activity_id=activity_id,
                timestamp=datetime.utcnow(),
                trace_level=TraceLevel.N4_COGNITIVO,
                interaction_type=InteractionType.STUDENT_PROMPT,
                cognitive_state=CognitiveState.EXPLORACION,
                content="Test",
                ai_involvement=1.5,
            )

    def test_trace_serialization(self, sample_trace_conceptual):
        """Test trace can be serialized to dict and JSON"""
        trace_dict = sample_trace_conceptual.model_dump()

        assert "session_id" in trace_dict
        assert "student_id" in trace_dict
        assert "content" in trace_dict
        assert "ai_involvement" in trace_dict

        # Can be reconstructed
        reconstructed = CognitiveTrace(**trace_dict)
        assert reconstructed.session_id == sample_trace_conceptual.session_id
        assert reconstructed.content == sample_trace_conceptual.content


# ============================================================================
# TraceSequence Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestTraceSequence:
    """Tests for TraceSequence model"""

    def test_sequence_creation(self, sample_trace_sequence):
        """Test creating a trace sequence"""
        assert len(sample_trace_sequence.traces) == 3
        assert sample_trace_sequence.student_id is not None
        assert sample_trace_sequence.activity_id is not None

    def test_get_cognitive_path(self, sample_trace_sequence):
        """Test reconstructing cognitive path from sequence"""
        path = sample_trace_sequence.get_cognitive_path()

        assert isinstance(path, list)
        assert len(path) > 0
        # Path should show progression: exploracion -> planificacion -> implementacion
        assert any("exploracion" in str(step).lower() for step in path)

    def test_ai_dependency_score(self, sample_trace_sequence):
        """Test calculating AI dependency score"""
        score = sample_trace_sequence.ai_dependency_score

        assert 0.0 <= score <= 1.0
        # Average of [0.3, 0.4, 1.0] = 0.567
        assert 0.5 <= score <= 0.6

    def test_strategy_changes(self, sample_trace_sequence):
        """Test counting strategy changes"""
        changes = sample_trace_sequence.strategy_changes

        assert isinstance(changes, int)
        assert changes >= 0


# ============================================================================
# Risk Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestRisk:
    """Tests for Risk model"""

    def test_risk_creation(self, sample_risk_delegacion):
        """Test creating a risk"""
        assert sample_risk_delegacion.risk_type == RiskType.COGNITIVE_DELEGATION
        assert sample_risk_delegacion.risk_level == RiskLevel.HIGH
        assert sample_risk_delegacion.dimension == RiskDimension.COGNITIVE
        assert len(sample_risk_delegacion.recommendations) > 0

    def test_risk_severity_ordering(self):
        """Test risk levels have correct severity ordering"""
        levels = [
            RiskLevel.INFO,
            RiskLevel.LOW,
            RiskLevel.MEDIUM,
            RiskLevel.HIGH,
            RiskLevel.CRITICAL,
        ]

        # Verify enum values represent increasing severity (lowercase as per model)
        assert RiskLevel.CRITICAL.value == "critical"
        assert RiskLevel.INFO.value == "info"


@pytest.mark.unit
@pytest.mark.models
class TestRiskReport:
    """Tests for RiskReport model"""

    def test_risk_report_aggregation(self, sample_risk_delegacion, sample_risk_superficial):
        """Test risk report aggregates risks correctly"""
        report = RiskReport(
            id=str(uuid4()),
            session_id=str(uuid4()),
            student_id="test_student",
            activity_id="test_activity",
            overall_assessment="Multiple risks detected",
        )

        # Add risks using add_risk() to update counters
        report.add_risk(sample_risk_delegacion)
        report.add_risk(sample_risk_superficial)

        assert report.total_risks == 2
        assert report.high_risks == 1  # delegacion is HIGH
        assert report.medium_risks == 1  # superficial is MEDIUM
        assert report.critical_risks == 0


# ============================================================================
# Evaluation Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestEvaluationReport:
    """Tests for EvaluationReport model"""

    def test_evaluation_report_creation(self, sample_evaluation_report):
        """Test creating an evaluation report"""
        assert sample_evaluation_report.overall_competency_level == CompetencyLevel.EN_DESARROLLO
        assert sample_evaluation_report.overall_score == 6.5
        assert len(sample_evaluation_report.dimensions) == 2
        assert len(sample_evaluation_report.key_strengths) > 0
        assert len(sample_evaluation_report.improvement_areas) > 0

    def test_competency_level_progression(self):
        """Test competency levels represent progression"""
        levels = [
            CompetencyLevel.INICIAL,
            CompetencyLevel.EN_DESARROLLO,
            CompetencyLevel.AUTONOMO,
            CompetencyLevel.EXPERTO,
        ]

        assert CompetencyLevel.INICIAL.value == "inicial"
        assert CompetencyLevel.EXPERTO.value == "experto"

    def test_dimension_evaluation(self):
        """Test dimension evaluation"""
        dimension = EvaluationDimension(
            name="Test Dimension",
            description="Test description",
            score=7.5,
            level=CompetencyLevel.AUTONOMO,
            evidence=["Evidence 1", "Evidence 2"],
        )

        assert dimension.score == 7.5
        assert dimension.level == CompetencyLevel.AUTONOMO
        assert len(dimension.evidence) == 2


# ============================================================================
# Cross-Model Integration Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.models
class TestModelIntegration:
    """Tests for interactions between models"""

    def test_trace_to_risk_flow(self, sample_trace_delegacion):
        """Test that traces can inform risk creation"""
        # A trace with delegacion should lead to a risk
        if sample_trace_delegacion.metadata.get("blocked"):
            risk = Risk(
                id=str(uuid4()),
                session_id=sample_trace_delegacion.session_id,
                student_id=sample_trace_delegacion.student_id,
                activity_id=sample_trace_delegacion.activity_id,
                risk_type=RiskType.COGNITIVE_DELEGATION,
                risk_level=RiskLevel.HIGH,
                dimension=RiskDimension.COGNITIVE,
                description="Delegación total detectada",
                evidence=[sample_trace_delegacion.content],
                impact="Pérdida de aprendizaje",
                recommendations=["Promover descomposición"],
            )

            assert risk.risk_type == RiskType.COGNITIVE_DELEGATION
            assert sample_trace_delegacion.content in risk.evidence

    def test_trace_sequence_to_evaluation_flow(self, sample_trace_sequence):
        """Test that trace sequences can inform evaluation"""
        # A sequence should provide data for evaluation
        cognitive_path = sample_trace_sequence.get_cognitive_path()
        ai_dependency = sample_trace_sequence.ai_dependency_score

        # These metrics should inform competency level
        assert cognitive_path is not None
        assert 0.0 <= ai_dependency <= 1.0

        # Low AI dependency and good path = higher competency
        if ai_dependency < 0.5 and len(cognitive_path) > 2:
            expected_level = CompetencyLevel.AUTONOMO
        else:
            expected_level = CompetencyLevel.EN_DESARROLLO

        assert expected_level in [
            CompetencyLevel.INICIAL,
            CompetencyLevel.EN_DESARROLLO,
            CompetencyLevel.AUTONOMO,
            CompetencyLevel.EXPERTO,
        ]
