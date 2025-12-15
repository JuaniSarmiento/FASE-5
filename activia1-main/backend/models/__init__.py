"""
Modelos de datos para el ecosistema AI-Native

Provides:
- Cognitive traceability models (CognitiveTrace, TraceSequence)
- Risk detection models (Risk, RiskReport, RiskDimension)
- Process evaluation models (EvaluationReport, EvaluationDimension)
- Git N2 traceability models (GitTrace, CodeEvolution)
"""
# Trace models
from .trace import (
    CognitiveTrace,
    TraceLevel,
    InteractionType,
    CognitiveState,
    TraceSequence,
)

# Risk models
from .risk import (
    Risk,
    RiskType,
    RiskLevel,
    RiskDimension,
    RiskReport,
)

# Evaluation models
from .evaluation import (
    EvaluationReport,
    CompetencyLevel,
    EvaluationDimension,
    ReasoningAnalysis,
    GitAnalysis,
    CognitivePhase,
)

# Sprint 5: Git N2 traceability models
from .git_trace import (
    GitTrace,
    GitEventType,
    GitFileChange,
    CodePattern,
    CodeEvolution,
)

__all__ = [
    # Trace models
    "CognitiveTrace",
    "TraceLevel",
    "InteractionType",
    "CognitiveState",
    "TraceSequence",
    # Risk models
    "Risk",
    "RiskType",
    "RiskLevel",
    "RiskDimension",
    "RiskReport",
    # Evaluation models
    "EvaluationReport",
    "CompetencyLevel",
    "EvaluationDimension",
    "ReasoningAnalysis",
    "GitAnalysis",
    "CognitivePhase",
    # Sprint 5: Git N2 models
    "GitTrace",
    "GitEventType",
    "GitFileChange",
    "CodePattern",
    "CodeEvolution",
]