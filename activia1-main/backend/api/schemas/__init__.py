"""
Schemas (DTOs) para la API REST
"""
from .common import (
    APIResponse,
    ErrorDetail,
    ErrorResponse,
    HealthStatus,
    PaginatedResponse,
    PaginationMeta,
    PaginationParams,
    # FIX 7.4 Cortez8: Type aliases
    SessionId,
    StudentId,
    ActivityId,
    UserId,
    TraceId,
    RiskId,
    EvaluationId,
)
from .interaction import (
    InteractionHistory,
    InteractionRequest,
    InteractionResponse,
    InteractionSummary,
)
from .session import (
    SessionCreate,
    SessionDetailResponse,
    SessionListResponse,
    SessionResponse,
    SessionUpdate,
)
from .activity import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityListResponse,
    ActivityPublishRequest,
    ActivityArchiveRequest,
    PolicyConfig,
)
# FIX 3.1: New schemas for ORM models
# FIX Cortez8: Added TraceSequenceResponse, TraceSequenceListResponse
from .trace import (
    CognitiveTraceCreate,
    CognitiveTraceResponse,
    CognitiveTraceListResponse,
    TraceN4Response,
    TraceSequenceResponse,
    TraceSequenceListResponse,
)
from .risk import (
    RiskCreate,
    RiskResponse,
    RiskListResponse,
    RiskDimensionAnalysis,
    RiskAnalysis5DResponse,
    RiskResolveRequest,
)
from .evaluation import (
    EvaluationDimensionScore,
    EvaluationCreate,
    EvaluationResponse,
    EvaluationListResponse,
    ProcessEvaluationRequest,
    ProcessEvaluationResponse,
)
from .git_trace import (
    GitFileChange,
    GitTraceCreate,
    GitTraceResponse,
    GitTraceListResponse,
    GitEvolutionResponse,
)
from .simulator_event import (
    SimulatorEventCreate,
    SimulatorEventResponse,
    SimulatorEventListResponse,
    SimulatorTimelineResponse,
)
from .enums import (
    RiskLevel,
    RiskDimension,
    TraceLevel,
    CognitiveState,
    InteractionType,
)
# FIX 5.2: Tutor interaction schemas
from .tutor import (
    TutorInteractRequest,
    TutorInteractResponse,
    CreateTutorSessionRequest,
    CreateTutorSessionResponse,
    TutorSessionAnalytics,
)

# Sprint 5-6 schemas
from .sprint5_6 import (
    # Enums
    InterviewType,
    DifficultyLevel,
    IncidentType,
    IncidentSeverity,
    AlertType,
    AlertSeverity,
    AlertScope,
    AlertStatus,
    PlanType,
    PlanStatus,
    ReportType,
    # Interview Session (HU-EST-011)
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewQuestion,
    InterviewResponse as InterviewAnswerResponse,
    EvaluationBreakdown,
    # Incident Simulation (HU-EST-012)
    IncidentSimulationCreate,
    IncidentSimulationResponse,
    DiagnosisStep,
    IncidentEvaluation,
    # LTI Integration (HU-SYS-010)
    LTIDeploymentCreate,
    LTIDeploymentResponse,
    LTISessionCreate,
    LTISessionResponse,
    # Course Report (HU-DOC-009)
    CourseReportCreate,
    CourseReportResponse,
    SummaryStats,
    StudentSummary,
    # Remediation Plan (HU-DOC-010)
    RemediationPlanCreate,
    RemediationPlanUpdate,
    RemediationPlanResponse,
    RecommendedAction,
    SuccessMetrics,
    # Risk Alert (HU-DOC-010)
    RiskAlertCreate,
    RiskAlertUpdate,
    RiskAlertResponse,
    # Trace Sequence
    TraceSequenceCreate,
    TraceSequenceResponse,
    # Student Profile
    StudentProfileCreate,
    StudentProfileUpdate,
    StudentProfileResponse,
)

__all__ = [
    # Common
    "APIResponse",
    "ErrorDetail",
    "ErrorResponse",
    "HealthStatus",
    "PaginatedResponse",
    "PaginationMeta",
    "PaginationParams",
    # Session
    "SessionCreate",
    "SessionUpdate",
    "SessionResponse",
    "SessionListResponse",
    "SessionDetailResponse",
    # Interaction
    "InteractionRequest",
    "InteractionResponse",
    "InteractionHistory",
    "InteractionSummary",
    # Activity
    "ActivityCreate",
    "ActivityUpdate",
    "ActivityResponse",
    "ActivityListResponse",
    "ActivityPublishRequest",
    "ActivityArchiveRequest",
    "PolicyConfig",
    # FIX 3.1: Cognitive Trace schemas
    "CognitiveTraceCreate",
    "CognitiveTraceResponse",
    "CognitiveTraceListResponse",
    "TraceN4Response",
    # FIX 3.1: Risk schemas
    "RiskCreate",
    "RiskResponse",
    "RiskListResponse",
    "RiskDimensionAnalysis",
    "RiskAnalysis5DResponse",
    "RiskResolveRequest",
    # FIX 3.1: Evaluation schemas
    "EvaluationDimensionScore",
    "EvaluationCreate",
    "EvaluationResponse",
    "EvaluationListResponse",
    "ProcessEvaluationRequest",
    "ProcessEvaluationResponse",
    # FIX 3.1: Git Trace schemas
    "GitFileChange",
    "GitTraceCreate",
    "GitTraceResponse",
    "GitTraceListResponse",
    "GitEvolutionResponse",
    # FIX 3.1: Simulator Event schemas
    "SimulatorEventCreate",
    "SimulatorEventResponse",
    "SimulatorEventListResponse",
    "SimulatorTimelineResponse",
    # FIX 3.1: New enums
    "RiskLevel",
    "RiskDimension",
    "TraceLevel",
    "CognitiveState",
    "InteractionType",
    # FIX 5.2: Tutor schemas
    "TutorInteractRequest",
    "TutorInteractResponse",
    "CreateTutorSessionRequest",
    "CreateTutorSessionResponse",
    "TutorSessionAnalytics",
    # Sprint 5-6 Enums
    "InterviewType",
    "DifficultyLevel",
    "IncidentType",
    "IncidentSeverity",
    "AlertType",
    "AlertSeverity",
    "AlertScope",
    "AlertStatus",
    "PlanType",
    "PlanStatus",
    "ReportType",
    # Interview Session (HU-EST-011)
    "InterviewSessionCreate",
    "InterviewSessionResponse",
    "InterviewQuestion",
    "InterviewAnswerResponse",
    "EvaluationBreakdown",
    # Incident Simulation (HU-EST-012)
    "IncidentSimulationCreate",
    "IncidentSimulationResponse",
    "DiagnosisStep",
    "IncidentEvaluation",
    # LTI Integration (HU-SYS-010)
    "LTIDeploymentCreate",
    "LTIDeploymentResponse",
    "LTISessionCreate",
    "LTISessionResponse",
    # Course Report (HU-DOC-009)
    "CourseReportCreate",
    "CourseReportResponse",
    "SummaryStats",
    "StudentSummary",
    # Remediation Plan (HU-DOC-010)
    "RemediationPlanCreate",
    "RemediationPlanUpdate",
    "RemediationPlanResponse",
    "RecommendedAction",
    "SuccessMetrics",
    # Risk Alert (HU-DOC-010)
    "RiskAlertCreate",
    "RiskAlertUpdate",
    "RiskAlertResponse",
    # Trace Sequence
    "TraceSequenceCreate",
    "TraceSequenceResponse",
    # Student Profile
    "StudentProfileCreate",
    "StudentProfileUpdate",
    "StudentProfileResponse",
]