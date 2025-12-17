"""
Database package for AI-Native MVP

Provides:
- SQLAlchemy database configuration
- Database session management
- Base model for ORM
- ORM models (SessionDB, CognitiveTraceDB, etc.)
- Repository pattern implementations
- Transaction management utilities
- Background task session management (production pattern)
"""
from .config import DatabaseConfig, get_db_session, init_database, get_db_config
from .base import Base
from .transaction import transaction, transactional, TransactionManager

# Background task session management (NEW - Production Pattern)
from .background_session import (
    get_background_db_session,
    create_background_db_session,
    with_background_db_session,
    BackgroundUnitOfWork,
)

# ORM Models
from .models import (
    SessionDB,
    CognitiveTraceDB,
    RiskDB,
    EvaluationDB,
    TraceSequenceDB,
    StudentProfileDB,
    ActivityDB,
    UserDB,
    # Sprint 5 models
    GitTraceDB,
    CourseReportDB,
    RemediationPlanDB,
    RiskAlertDB,
    # Sprint 6 models
    InterviewSessionDB,
    IncidentSimulationDB,
    LTIDeploymentDB,
    LTISessionDB,
)

# Repositories
from .repositories import (
    SessionRepository,
    TraceRepository,
    RiskRepository,
    EvaluationRepository,
    TraceSequenceRepository,
    ActivityRepository,
    UserRepository,
    # Sprint 5 repositories
    GitTraceRepository,
    CourseReportRepository,
    RemediationPlanRepository,
    RiskAlertRepository,
    # Sprint 6 repositories
    InterviewSessionRepository,
    IncidentSimulationRepository,
    LTIDeploymentRepository,
    LTISessionRepository,
)

__all__ = [
    # Configuration
    "DatabaseConfig",
    "get_db_session",
    "init_database",
    "get_db_config",
    "Base",
    # Transaction management
    "transaction",
    "transactional",
    "TransactionManager",
    # Background task session management (NEW)
    "get_background_db_session",
    "create_background_db_session",
    "with_background_db_session",
    "BackgroundUnitOfWork",
    # ORM Models
    "SessionDB",
    "CognitiveTraceDB",
    "RiskDB",
    "EvaluationDB",
    "TraceSequenceDB",
    "StudentProfileDB",
    "ActivityDB",
    "UserDB",
    "GitTraceDB",
    "CourseReportDB",
    "RemediationPlanDB",
    "RiskAlertDB",
    "InterviewSessionDB",
    "IncidentSimulationDB",
    "LTIDeploymentDB",
    "LTISessionDB",
    # Repositories
    "SessionRepository",
    "TraceRepository",
    "RiskRepository",
    "EvaluationRepository",
    "TraceSequenceRepository",
    "ActivityRepository",
    "UserRepository",
    "GitTraceRepository",
    "CourseReportRepository",
    "RemediationPlanRepository",
    "RiskAlertRepository",
    "InterviewSessionRepository",
    "IncidentSimulationRepository",
    "LTIDeploymentRepository",
    "LTISessionRepository",
]