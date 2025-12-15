"""
Repository pattern for database operations

Provides:
- SessionRepository: Manage learning sessions
- TraceRepository: Manage cognitive traces
- RiskRepository: Manage risks
- EvaluationRepository: Manage evaluations
- UserRepository: Manage user authentication and authorization

TRANSACTION MANAGEMENT (DB-8):
----------------------------
Individual repository methods commit immediately after each operation.
For batch operations that need atomicity, use the transaction context manager:

    from backend.database.transaction import transaction

    with transaction(db, "Batch create session with traces and risks"):
        # Disable auto-commit in repositories by NOT calling commit()
        # Use the session directly for batch operations
        session = SessionDB(...)
        db.add(session)  # No commit yet

        trace = CognitiveTraceDB(...)
        db.add(trace)  # No commit yet

        risk = RiskDB(...)
        db.add(risk)  # No commit yet

        # Transaction commits all or rolls back all on exit

For simpler batch operations within a single repository, use the
TransactionManager from backend/database/transaction.py.
"""
from typing import List, Optional, Any, Type, Dict, Tuple
from uuid import uuid4
from enum import Enum

from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import desc, select

from backend.core.constants import utc_now

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
    # FIX 3.2: Add SimulatorEventDB
    SimulatorEventDB,
    LTIDeploymentDB,
    LTISessionDB,
)
from ..models.trace import CognitiveTrace, TraceSequence, CognitiveState, TraceLevel, InteractionType
from ..models.risk import Risk, RiskReport, RiskType, RiskLevel
from ..models.evaluation import EvaluationReport, CompetencyLevel
import logging
from datetime import datetime  # FIX cortez14 DEFECTO 1.1

logger = logging.getLogger(__name__)


def _safe_cognitive_state_to_str(cognitive_state: Optional[CognitiveState]) -> Optional[str]:
    """
    Convierte CognitiveState a string de forma segura, validando el tipo.

    Args:
        cognitive_state: Estado cognitivo (puede ser CognitiveState enum, str, o None)

    Returns:
        String con el valor del enum, o None

    Raises:
        ValueError: Si cognitive_state no es None, str, ni CognitiveState válido
    """
    if cognitive_state is None:
        return None

    # Si ya es un string, validar que sea un valor válido del enum
    if isinstance(cognitive_state, str):
        # Intentar convertir a enum para validar
        try:
            CognitiveState(cognitive_state)
            return cognitive_state
        except ValueError:
            logger.warning(
                f"Invalid cognitive_state string: '{cognitive_state}'. "
                f"Expected one of: {[s.value for s in CognitiveState]}"
            )
            raise ValueError(
                f"Invalid cognitive_state: '{cognitive_state}'. "
                f"Must be one of: {[s.value for s in CognitiveState]}"
            )

    # Si es un enum CognitiveState, extraer su valor
    if isinstance(cognitive_state, CognitiveState):
        return cognitive_state.value

    # Tipo no válido
    logger.error(
        f"cognitive_state must be CognitiveState enum or str, got {type(cognitive_state)}"
    )
    raise TypeError(
        f"cognitive_state must be CognitiveState enum or str, got {type(cognitive_state).__name__}"
    )


def _safe_enum_to_str(value: Any, enum_class: Type[Enum]) -> Optional[str]:
    """
    Convierte un valor a string de forma defensiva con validación de enum.

    ✅ FIXED (2025-11-22): Previene crashes por valores inválidos en queries
    con enums (TraceLevel, InteractionType, RiskType, RiskLevel, etc.)

    Args:
        value: Puede ser Enum, str, o None
        enum_class: Clase del enum para validación

    Returns:
        String lowercase del valor, o None si value es None

    Raises:
        ValueError: Si el valor no es válido para el enum
        TypeError: Si el tipo no es soportado

    Example:
        >>> from src.ai_native_mvp.models.trace import TraceLevel
        >>> # Acepta enum
        >>> _safe_enum_to_str(TraceLevel.N4_COGNITIVO, TraceLevel)
        'n4_cognitivo'
        >>> # Acepta string válido
        >>> _safe_enum_to_str("N4_COGNITIVO", TraceLevel)
        'n4_cognitivo'
        >>> # Rechaza string inválido
        >>> _safe_enum_to_str("INVALID", TraceLevel)
        ValueError: Invalid TraceLevel: 'INVALID'. Valid values: [...]
        >>> # Acepta None
        >>> _safe_enum_to_str(None, TraceLevel)
        None
    """
    if value is None:
        return None

    # Ya es un enum válido
    if isinstance(value, enum_class):
        return value.value.lower()

    # Es un string, validar que sea un valor válido del enum
    if isinstance(value, str):
        try:
            # Intentar crear enum desde el string (case-insensitive)
            # Buscar el valor en el enum ignorando case
            value_upper = value.upper()
            for enum_member in enum_class:
                if enum_member.value.upper() == value_upper:
                    return enum_member.value.lower()

            # Si no se encontró, lanzar error con valores válidos
            valid_values = [e.value for e in enum_class]
            raise ValueError(
                f"Invalid {enum_class.__name__}: '{value}'. "
                f"Valid values: {valid_values}"
            )
        except AttributeError:
            # El enum no tiene .value (enum mal formado)
            logger.error(
                f"Malformed enum class: {enum_class.__name__}",
                extra={"enum_class": enum_class}
            )
            raise TypeError(f"Malformed enum class: {enum_class.__name__}")

    # Tipo no válido
    logger.error(
        f"Expected {enum_class.__name__} or str, got {type(value)}",
        extra={"value": value, "type": type(value).__name__}
    )
    raise TypeError(
        f"Expected {enum_class.__name__} or str, got {type(value).__name__}"
    )


class SessionRepository:
    """Repository for session operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        student_id: str,
        activity_id: str,
        mode: str = "TUTOR",
        simulator_type: Optional[str] = None,
    ) -> SessionDB:
        """
        Create a new learning session.

        ✅ FIX 3.2 Cortez5: Added try/except/rollback for transaction safety

        Args:
            student_id: Student identifier
            activity_id: Activity identifier
            mode: Session mode (TUTOR, EVALUATOR, SIMULATOR, RISK_ANALYST)
            simulator_type: Type of simulator when mode=SIMULATOR
                           (product_owner, scrum_master, tech_interviewer,
                            incident_responder, client, devsecops)

        Returns:
            Created SessionDB instance

        Raises:
            Exception: Re-raises after rollback if creation fails
        """
        try:
            session = SessionDB(
                id=str(uuid4()),
                student_id=student_id,
                activity_id=activity_id,
                mode=mode,
                simulator_type=simulator_type,
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create session: {e}", extra={
                "student_id": student_id,
                "activity_id": activity_id,
                "mode": mode
            })
            raise

    def get_by_id(self, session_id: str, load_relations: bool = False) -> Optional[SessionDB]:
        """
        Get session by ID with optional eager loading.

        ✅ REFACTORED (2025-11-22): Agregado eager loading opcional (H3)

        Args:
            session_id: Session ID to retrieve
            load_relations: If True, loads traces and risks in same query (prevents N+1)

        Returns:
            SessionDB instance if found, None otherwise

        Performance:
            - Without eager loading: 1 query (base session only)
            - With eager loading: 1-3 queries total (session + traces + risks)
            - Use load_relations=True when accessing session.traces or session.risks
        """
        query = self.db.query(SessionDB).filter(SessionDB.id == session_id)

        if load_relations:
            # ✅ REFACTORED (2025-11-22): Eager loading para prevenir N+1 queries (H3)
            # selectinload() carga relaciones en queries separadas eficientes
            query = query.options(
                selectinload(SessionDB.traces),
                selectinload(SessionDB.risks),
                selectinload(SessionDB.evaluations)
            )

        return query.first()

    def get_by_student(
        self,
        student_id: str,
        load_relations: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[SessionDB]:
        """
        Get all sessions for a student with optional eager loading.

        ✅ REFACTORED (2025-11-22): Agregado eager loading opcional (H3)
        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries

        Args:
            student_id: Student ID
            load_relations: If True, loads traces and risks to prevent N+1 queries
            limit: Maximum records to return (default 100)
            offset: Records to skip (default 0)

        Returns:
            List of SessionDB instances

        Performance:
            - Without eager loading: 1 query (sessions only)
            - With eager loading: 1-3 queries total (sessions + traces + risks)
            - Use load_relations=True when iterating and accessing session.traces/risks
        """
        query = self.db.query(SessionDB).filter(SessionDB.student_id == student_id)

        if load_relations:
            # ✅ REFACTORED (2025-11-22): Eager loading para prevenir N+1 queries (H3)
            query = query.options(
                selectinload(SessionDB.traces),
                selectinload(SessionDB.risks),
                selectinload(SessionDB.evaluations)
            )

        return query.order_by(desc(SessionDB.created_at)).limit(limit).offset(offset).all()

    def get_by_activity(
        self,
        activity_id: str,
        load_relations: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[SessionDB]:
        """
        Get all sessions for an activity with optional eager loading.

        ✅ REFACTORED (2025-11-22): Agregado eager loading opcional (H3)
        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries

        Args:
            activity_id: Activity ID
            load_relations: If True, loads traces and risks to prevent N+1 queries
            limit: Maximum records to return (default 100)
            offset: Records to skip (default 0)

        Returns:
            List of SessionDB instances

        Performance:
            - Without eager loading: 1 query (sessions only)
            - With eager loading: 1-3 queries total (sessions + traces + risks)
            - Use load_relations=True when iterating and accessing session.traces/risks
        """
        query = self.db.query(SessionDB).filter(SessionDB.activity_id == activity_id)

        if load_relations:
            # ✅ REFACTORED (2025-11-22): Eager loading para prevenir N+1 queries (H3)
            query = query.options(
                selectinload(SessionDB.traces),
                selectinload(SessionDB.risks),
                selectinload(SessionDB.evaluations)
            )

        return query.order_by(desc(SessionDB.created_at)).limit(limit).offset(offset).all()

    def get_all(
        self,
        load_relations: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[SessionDB]:
        """
        Get all sessions with optional eager loading.

        ✅ REFACTORED (2025-11-22): Agregado eager loading opcional (H3)
        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries

        Args:
            load_relations: If True, loads traces and risks to prevent N+1 queries
            limit: Maximum records to return (default 100)
            offset: Records to skip (default 0)

        Returns:
            List of SessionDB instances

        Performance:
            - Without eager loading: 1 query (sessions only)
            - With eager loading: 1-3 queries total (sessions + traces + risks)
            - Use load_relations=True when iterating and accessing session.traces/risks
        """
        query = self.db.query(SessionDB)

        if load_relations:
            # ✅ REFACTORED (2025-11-22): Eager loading para prevenir N+1 queries (H3)
            query = query.options(
                selectinload(SessionDB.traces),
                selectinload(SessionDB.risks),
                selectinload(SessionDB.evaluations)
            )

        return query.order_by(desc(SessionDB.created_at)).limit(limit).offset(offset).all()

    def end_session(self, session_id: str) -> Optional[SessionDB]:
        """
        Mark session as completed with pessimistic locking

        Uses SELECT FOR UPDATE to prevent race conditions when multiple
        requests try to end the same session simultaneously.

        Returns:
            SessionDB if session was ended successfully, None otherwise
        """
        try:
            # ✅ Pessimistic lock: SELECT ... FOR UPDATE
            stmt = select(SessionDB).where(SessionDB.id == session_id).with_for_update()
            session = self.db.execute(stmt).scalar_one_or_none()

            if session:
                session.end_time = utc_now()
                session.status = "completed"
                self.db.commit()
                self.db.refresh(session)
                return session

            return None
        except Exception:
            self.db.rollback()
            raise

    def update_mode(self, session_id: str, mode: str) -> Optional[SessionDB]:
        """
        Update session mode with pessimistic locking

        Uses SELECT FOR UPDATE to prevent race conditions.
        """
        try:
            # ✅ Pessimistic lock: SELECT ... FOR UPDATE
            stmt = select(SessionDB).where(SessionDB.id == session_id).with_for_update()
            session = self.db.execute(stmt).scalar_one_or_none()

            if session:
                session.mode = mode
                self.db.commit()
                self.db.refresh(session)
                return session

            return None
        except Exception:
            self.db.rollback()
            raise

    def update_status(self, session_id: str, status: str) -> Optional[SessionDB]:
        """
        Update session status with pessimistic locking

        Uses SELECT FOR UPDATE to prevent race conditions.
        """
        try:
            # ✅ Pessimistic lock: SELECT ... FOR UPDATE
            stmt = select(SessionDB).where(SessionDB.id == session_id).with_for_update()
            session = self.db.execute(stmt).scalar_one_or_none()

            if session:
                session.status = status
                self.db.commit()
                self.db.refresh(session)
                return session

            return None
        except Exception:
            self.db.rollback()
            raise

    def exists(self, session_id: str) -> bool:
        """
        FIX 3.6.1 Cortez4: Check if session exists without loading full object.
        More efficient than get_by_id() when only checking existence.

        Args:
            session_id: Session ID to check

        Returns:
            True if session exists, False otherwise
        """
        from sqlalchemy import exists
        return self.db.query(
            exists().where(SessionDB.id == session_id)
        ).scalar()

    def delete(self, session_id: str, validate_cascade: bool = True) -> bool:
        """
        Delete a session (hard delete with CASCADE to related entities)

        ⚠️ WARNING: This will also delete all related traces, risks, evaluations,
        git_traces, interview_sessions, incident_simulations, and lti_sessions
        due to CASCADE foreign key constraints.

        Args:
            session_id: Session ID to delete
            validate_cascade: If True, logs cascade impact before deletion (DB-9 fix)

        Returns:
            True if session was deleted, False if session not found

        Note:
            Uses try/except with rollback for transaction safety.
            All related entities are automatically deleted by SQLAlchemy CASCADE.
        """
        try:
            session = self.db.query(SessionDB).filter(SessionDB.id == session_id).first()
            if not session:
                return False

            # FIX DB-9: Validate and log cascade impact before deletion
            if validate_cascade:
                cascade_counts = {
                    "traces": self.db.query(CognitiveTraceDB).filter(
                        CognitiveTraceDB.session_id == session_id
                    ).count(),
                    "risks": self.db.query(RiskDB).filter(
                        RiskDB.session_id == session_id
                    ).count(),
                    "evaluations": self.db.query(EvaluationDB).filter(
                        EvaluationDB.session_id == session_id
                    ).count(),
                    "git_traces": self.db.query(GitTraceDB).filter(
                        GitTraceDB.session_id == session_id
                    ).count(),
                    "interview_sessions": self.db.query(InterviewSessionDB).filter(
                        InterviewSessionDB.session_id == session_id
                    ).count(),
                    "incident_simulations": self.db.query(IncidentSimulationDB).filter(
                        IncidentSimulationDB.session_id == session_id
                    ).count(),
                }

                total_cascaded = sum(cascade_counts.values())
                if total_cascaded > 0:
                    logger.warning(
                        f"Deleting session {session_id} will CASCADE delete {total_cascaded} related entities",
                        extra={
                            "session_id": session_id,
                            "cascade_counts": cascade_counts,
                            "student_id": session.student_id,
                            "activity_id": session.activity_id,
                        }
                    )

            self.db.delete(session)
            self.db.commit()

            logger.info(
                f"Session {session_id} deleted successfully",
                extra={"session_id": session_id}
            )
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(
                f"Failed to delete session {session_id}",
                extra={"session_id": session_id, "error": str(e)},
                exc_info=True
            )
            raise

    def get_by_ids(
        self,
        session_ids: List[str],
        load_relations: bool = False
    ) -> Dict[str, SessionDB]:
        """
        Get multiple sessions by IDs in a single query (batch loading).

        ✅ FIX 3.5 Cortez5: Batch loading to prevent N+1 queries

        Args:
            session_ids: List of session IDs to fetch
            load_relations: If True, eagerly loads traces, risks, evaluations

        Returns:
            Dictionary mapping session_id to SessionDB (missing IDs not in dict)
        """
        if not session_ids:
            return {}

        query = self.db.query(SessionDB).filter(SessionDB.id.in_(session_ids))

        if load_relations:
            query = query.options(
                selectinload(SessionDB.traces),
                selectinload(SessionDB.risks),
                selectinload(SessionDB.evaluations)
            )

        sessions = query.all()
        return {session.id: session for session in sessions}

    # FIX 10.1 Cortez10: Removed duplicate exists() method
    # The efficient version using sqlalchemy.exists() is at line 463-477

    def count_by_student(self, student_id: str) -> int:
        """
        Count sessions for a student.

        ✅ FIX 3.6 Cortez5: Efficient count without loading objects

        Args:
            student_id: Student ID

        Returns:
            Number of sessions
        """
        return (
            self.db.query(SessionDB)
            .filter(SessionDB.student_id == student_id)
            .count()
        )

    def count_by_activity(self, activity_id: str) -> int:
        """
        Count sessions for an activity.

        ✅ FIX 3.6 Cortez5: Efficient count without loading objects

        Args:
            activity_id: Activity ID

        Returns:
            Number of sessions
        """
        return (
            self.db.query(SessionDB)
            .filter(SessionDB.activity_id == activity_id)
            .count()
        )

    # ==========================================================================
    # FIX Cortez11: Missing update methods
    # ==========================================================================

    def update_simulator_type(
        self, session_id: str, simulator_type: str
    ) -> Optional[SessionDB]:
        """
        Update session simulator_type with pessimistic locking.

        FIX Cortez11 2.1: Added missing method for simulator_type updates.

        Args:
            session_id: Session ID
            simulator_type: New simulator type

        Returns:
            Updated SessionDB or None if not found
        """
        try:
            stmt = select(SessionDB).where(SessionDB.id == session_id).with_for_update()
            session = self.db.execute(stmt).scalar_one_or_none()

            if session:
                session.simulator_type = simulator_type
                session.updated_at = utc_now()
                self.db.commit()
                self.db.refresh(session)
                return session

            return None
        except Exception:
            self.db.rollback()
            raise

    def update_cognitive_status(
        self, session_id: str, cognitive_status: dict
    ) -> Optional[SessionDB]:
        """
        Update session cognitive status for N4 traceability.

        FIX Cortez11 2.2: Added missing method for cognitive_status updates.

        Args:
            session_id: Session ID
            cognitive_status: Cognitive status dictionary

        Returns:
            Updated SessionDB or None if not found
        """
        try:
            stmt = select(SessionDB).where(SessionDB.id == session_id).with_for_update()
            session = self.db.execute(stmt).scalar_one_or_none()

            if session:
                session.cognitive_status = cognitive_status
                session.updated_at = utc_now()
                self.db.commit()
                self.db.refresh(session)
                return session

            return None
        except Exception:
            self.db.rollback()
            raise

    def update_session_metrics(
        self, session_id: str, session_metrics: dict
    ) -> Optional[SessionDB]:
        """
        Update session metrics (aggregated statistics).

        FIX Cortez11 2.3: Added missing method for session_metrics updates.

        Args:
            session_id: Session ID
            session_metrics: Session metrics dictionary

        Returns:
            Updated SessionDB or None if not found
        """
        try:
            stmt = select(SessionDB).where(SessionDB.id == session_id).with_for_update()
            session = self.db.execute(stmt).scalar_one_or_none()

            if session:
                session.session_metrics = session_metrics
                session.updated_at = utc_now()
                self.db.commit()
                self.db.refresh(session)
                return session

            return None
        except Exception:
            self.db.rollback()
            raise

    def update_learning_objective(
        self, session_id: str, learning_objective: dict
    ) -> Optional[SessionDB]:
        """
        Update session learning objective.

        FIX Cortez11 2.4: Added missing method for learning_objective updates.

        Args:
            session_id: Session ID
            learning_objective: Learning objective dictionary

        Returns:
            Updated SessionDB or None if not found
        """
        try:
            stmt = select(SessionDB).where(SessionDB.id == session_id).with_for_update()
            session = self.db.execute(stmt).scalar_one_or_none()

            if session:
                session.learning_objective = learning_objective
                session.updated_at = utc_now()
                self.db.commit()
                self.db.refresh(session)
                return session

            return None
        except Exception:
            self.db.rollback()
            raise


class TraceRepository:
    """Repository for cognitive trace operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, trace: CognitiveTrace) -> CognitiveTraceDB:
        """
        Create a new cognitive trace.

        ✅ FIX 3.2 Cortez5: Added try/except/rollback for transaction safety
        """
        try:
            # ✅ FIXED (2025-11-22): Conversión defensiva de enums (C5)
            db_trace = CognitiveTraceDB(
                id=trace.id or str(uuid4()),
                session_id=trace.session_id,
                student_id=trace.student_id,
                activity_id=trace.activity_id,
                trace_level=_safe_enum_to_str(trace.trace_level, TraceLevel),
                interaction_type=_safe_enum_to_str(trace.interaction_type, InteractionType),
                content=trace.content,
                context=trace.context,
                trace_metadata=trace.metadata,
                cognitive_state=_safe_cognitive_state_to_str(trace.cognitive_state),
                cognitive_intent=trace.cognitive_intent,
                decision_justification=trace.decision_justification,
                alternatives_considered=trace.alternatives_considered,
                strategy_type=trace.strategy_type,
                ai_involvement=trace.ai_involvement,
                parent_trace_id=trace.parent_trace_id,
                agent_id=trace.agent_id,
            )
            self.db.add(db_trace)
            self.db.commit()
            self.db.refresh(db_trace)
            return db_trace
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create trace: {e}", extra={
                "session_id": trace.session_id,
                "student_id": trace.student_id
            })
            raise

    def get_by_id(self, trace_id: str) -> Optional[CognitiveTraceDB]:
        """Get trace by ID"""
        return self.db.query(CognitiveTraceDB).filter(CognitiveTraceDB.id == trace_id).first()

    def get_by_session(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[CognitiveTraceDB]:
        """
        Get all traces for a session.

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries

        Args:
            session_id: Session ID
            limit: Maximum records to return (default 100)
            offset: Records to skip (default 0)
        """
        return (
            self.db.query(CognitiveTraceDB)
            .filter(CognitiveTraceDB.session_id == session_id)
            .order_by(CognitiveTraceDB.created_at)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_latest_by_session(self, session_id: str) -> Optional[CognitiveTraceDB]:
        """
        FIX N+1 #1: Get only the latest trace for a session.
        Uses ORDER BY DESC + LIMIT 1 instead of loading all traces.
        """
        return (
            self.db.query(CognitiveTraceDB)
            .filter(CognitiveTraceDB.session_id == session_id)
            .order_by(desc(CognitiveTraceDB.created_at))
            .first()
        )

    def get_by_session_filtered(
        self,
        session_id: str,
        trace_level: Optional[str] = None,
        interaction_type: Optional[str] = None,
        cognitive_state: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CognitiveTraceDB]:
        """
        FIX N+1 #2: Get traces with filtering in SQL instead of Python.
        Supports filtering by trace_level, interaction_type, cognitive_state.
        """
        query = self.db.query(CognitiveTraceDB).filter(
            CognitiveTraceDB.session_id == session_id
        )

        if trace_level:
            query = query.filter(CognitiveTraceDB.trace_level == trace_level)
        if interaction_type:
            query = query.filter(CognitiveTraceDB.interaction_type == interaction_type)
        if cognitive_state:
            query = query.filter(CognitiveTraceDB.cognitive_state == cognitive_state)

        return (
            query
            .order_by(CognitiveTraceDB.created_at)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_by_session_filtered(
        self,
        session_id: str,
        trace_level: Optional[str] = None,
        interaction_type: Optional[str] = None,
        cognitive_state: Optional[str] = None
    ) -> int:
        """Count traces with filtering in SQL for pagination metadata."""
        query = self.db.query(CognitiveTraceDB).filter(
            CognitiveTraceDB.session_id == session_id
        )

        if trace_level:
            query = query.filter(CognitiveTraceDB.trace_level == trace_level)
        if interaction_type:
            query = query.filter(CognitiveTraceDB.interaction_type == interaction_type)
        if cognitive_state:
            query = query.filter(CognitiveTraceDB.cognitive_state == cognitive_state)

        return query.count()

    def get_by_student(self, student_id: str, limit: int = 100) -> List[CognitiveTraceDB]:
        """
        Get recent traces for a student with eager loading to prevent N+1 queries.
        Uses joinedload to fetch related session data in a single query.
        """
        from sqlalchemy.orm import joinedload

        return (
            self.db.query(CognitiveTraceDB)
            .filter(CognitiveTraceDB.student_id == student_id)
            .options(joinedload(CognitiveTraceDB.session))  # ✅ Eager loading
            .order_by(desc(CognitiveTraceDB.created_at))
            .limit(limit)
            .all()
        )

    def get_by_student_filtered(
        self,
        student_id: str,
        activity_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[CognitiveTraceDB]:
        """
        FIX Cortez21 DEFECTO 5.1: Get student traces with SQL filtering.
        Filters directly in SQL instead of loading all traces and filtering in Python.

        Args:
            student_id: Student ID
            activity_id: Optional activity ID filter
            limit: Maximum records to return
            offset: Records to skip

        Returns:
            List of filtered and paginated traces
        """
        query = self.db.query(CognitiveTraceDB).filter(
            CognitiveTraceDB.student_id == student_id
        )

        if activity_id:
            query = query.filter(CognitiveTraceDB.activity_id == activity_id)

        return (
            query
            .order_by(desc(CognitiveTraceDB.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_by_student_filtered(
        self,
        student_id: str,
        activity_id: Optional[str] = None
    ) -> int:
        """
        FIX Cortez21 DEFECTO 5.1: Count student traces with SQL filtering.

        Args:
            student_id: Student ID
            activity_id: Optional activity ID filter

        Returns:
            Count of traces matching the filters
        """
        query = self.db.query(CognitiveTraceDB).filter(
            CognitiveTraceDB.student_id == student_id
        )

        if activity_id:
            query = query.filter(CognitiveTraceDB.activity_id == activity_id)

        return query.count()

    def count_by_session(self, session_id: str) -> int:
        """Count traces in a session"""
        return (
            self.db.query(CognitiveTraceDB)
            .filter(CognitiveTraceDB.session_id == session_id)
            .count()
        )

    def get_by_session_ids(self, session_ids: List[str]) -> Dict[str, List[CognitiveTraceDB]]:
        """
        Get all traces for multiple sessions in a single query (batch loading).

        This prevents N+1 query problems when loading traces for multiple sessions.

        Args:
            session_ids: List of session IDs to fetch traces for

        Returns:
            Dictionary mapping session_id to list of traces for that session
        """
        if not session_ids:
            return {}

        traces = (
            self.db.query(CognitiveTraceDB)
            .filter(CognitiveTraceDB.session_id.in_(session_ids))
            .order_by(CognitiveTraceDB.session_id, CognitiveTraceDB.created_at)
            .all()
        )

        # Group traces by session_id
        result: Dict[str, List[CognitiveTraceDB]] = {sid: [] for sid in session_ids}
        for trace in traces:
            if trace.session_id in result:
                result[trace.session_id].append(trace)

        return result

    def get_by_student_activity_pairs(
        self,
        pairs: List[Tuple[str, str]]
    ) -> Dict[Tuple[str, str], List[CognitiveTraceDB]]:
        """
        FIX 3.7 Cortez3: Batch loading for student-activity pairs.

        Loads traces for multiple (student_id, activity_id) combinations
        in a single query to prevent N+1 queries in reports.

        Args:
            pairs: List of tuples (student_id, activity_id)

        Returns:
            Dictionary mapping each (student_id, activity_id) pair to its traces

        Example:
            pairs = [("student1", "act1"), ("student2", "act1")]
            traces_by_pair = repo.get_by_student_activity_pairs(pairs)
            student1_traces = traces_by_pair[("student1", "act1")]
        """
        if not pairs:
            return {}

        from sqlalchemy import or_, and_

        # Build OR filter for all (student_id, activity_id) combinations
        filters = [
            and_(
                CognitiveTraceDB.student_id == student_id,
                CognitiveTraceDB.activity_id == activity_id
            )
            for student_id, activity_id in pairs
        ]

        traces = (
            self.db.query(CognitiveTraceDB)
            .filter(or_(*filters))
            .order_by(
                CognitiveTraceDB.student_id,
                CognitiveTraceDB.activity_id,
                CognitiveTraceDB.created_at
            )
            .all()
        )

        # Group traces by (student_id, activity_id) pair
        result: Dict[Tuple[str, str], List[CognitiveTraceDB]] = {
            pair: [] for pair in pairs
        }

        for trace in traces:
            key = (trace.student_id, trace.activity_id)
            if key in result:
                result[key].append(trace)

        return result

    def get_by_activity(
        self,
        activity_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[CognitiveTraceDB]:
        """
        Get all traces for an activity.

        FIX 2.5 Cortez11: Added missing method for activity-based trace queries.

        Args:
            activity_id: Activity ID to filter by
            limit: Maximum records to return (default 100)
            offset: Records to skip (default 0)

        Returns:
            List of traces for the activity, ordered by creation date (newest first)
        """
        return (
            self.db.query(CognitiveTraceDB)
            .filter(CognitiveTraceDB.activity_id == activity_id)
            .order_by(desc(CognitiveTraceDB.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )


class RiskRepository:
    """Repository for risk operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, risk: Risk) -> RiskDB:
        """
        Create a new risk.

        ✅ FIX 3.2 Cortez5: Added try/except/rollback for transaction safety

        Note: All getattr() calls removed - Pydantic models guarantee all fields exist
        with appropriate defaults (Optional fields default to None, lists to [], etc.)
        """
        try:
            # ✅ FIXED (2025-11-22): Conversión defensiva de enums (C5)
            db_risk = RiskDB(
                id=risk.id or str(uuid4()),
                session_id=risk.session_id,  # REQUIRED field (Phase 0 fix)
                student_id=risk.student_id,
                activity_id=risk.activity_id,
                risk_type=_safe_enum_to_str(risk.risk_type, RiskType),
                risk_level=_safe_enum_to_str(risk.risk_level, RiskLevel),
                dimension=risk.dimension.value,  # RiskDimension - mantener .value por ahora (no hay import)
                description=risk.description,
                impact=risk.impact,  # Optional[str], defaults to None
                evidence=risk.evidence,  # List[str], defaults to []
                trace_ids=risk.trace_ids,  # List[str], defaults to []
                root_cause=risk.root_cause,  # Optional[str], defaults to None
                impact_assessment=risk.impact_assessment,  # Optional[str], defaults to None
                recommendations=risk.recommendations,  # List[str], defaults to []
                pedagogical_intervention=risk.pedagogical_intervention,  # Optional[str], defaults to None
                resolved=risk.resolved,  # bool, defaults to False
                resolution_notes=risk.resolution_notes,  # Optional[str], defaults to None
                detected_by=risk.detected_by,  # str, defaults to "AR-IA"
            )
            self.db.add(db_risk)
            self.db.commit()
            self.db.refresh(db_risk)
            return db_risk
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create risk: {e}", extra={
                "session_id": risk.session_id,
                "risk_level": str(risk.risk_level)
            })
            raise

    def get_by_id(self, risk_id: str) -> Optional[RiskDB]:
        """Get risk by ID"""
        return self.db.query(RiskDB).filter(RiskDB.id == risk_id).first()

    def get_by_session(
        self,
        session_id: str,
        resolved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[RiskDB]:
        """
        Get all risks for a session

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries

        Args:
            session_id: Session ID to filter by
            resolved: Optional filter by resolution status (True/False/None for all)
            limit: Maximum records to return (default 100)
            offset: Records to skip (default 0)

        Returns:
            List of risks for the session, ordered by creation date (newest first)
        """
        query = self.db.query(RiskDB).filter(RiskDB.session_id == session_id)

        if resolved is not None:
            query = query.filter(RiskDB.resolved == resolved)

        return query.order_by(desc(RiskDB.created_at)).limit(limit).offset(offset).all()

    def get_by_student(
        self,
        student_id: str,
        resolved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[RiskDB]:
        """
        Get risks for a student with eager loading to prevent N+1 queries.

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries

        Uses joinedload to fetch related session data in a single query.
        """
        from sqlalchemy.orm import joinedload

        query = self.db.query(RiskDB)\
            .filter(RiskDB.student_id == student_id)\
            .options(joinedload(RiskDB.session))  # ✅ Eager loading

        if resolved is not None:
            query = query.filter(RiskDB.resolved == resolved)

        return query.order_by(desc(RiskDB.created_at)).limit(limit).offset(offset).all()

    def get_critical_risks(
        self,
        student_id: Optional[str] = None,
        load_session_relations: bool = False
    ) -> List[RiskDB]:
        """
        Get all critical risks with eager loading to prevent N+1 queries.

        FIX 3.6 Cortez3: Enhanced with optional nested eager loading.

        Args:
            student_id: Filtrar por estudiante (opcional)
            load_session_relations: Si True, precarga traces y evaluations de la sesión

        Returns:
            List of RiskDB with session (and optionally nested relations) preloaded
        """
        from sqlalchemy.orm import joinedload, selectinload

        query = self.db.query(RiskDB)\
            .filter(RiskDB.risk_level == "critical")\
            .filter(RiskDB.resolved == False)

        if student_id:
            query = query.filter(RiskDB.student_id == student_id)

        # FIX 3.6 Cortez3: Use selectinload for nested relations to avoid N+1
        if load_session_relations:
            query = query.options(
                selectinload(RiskDB.session).selectinload(SessionDB.traces),
                selectinload(RiskDB.session).selectinload(SessionDB.evaluations)
            )
        else:
            query = query.options(joinedload(RiskDB.session))

        return query.order_by(desc(RiskDB.created_at)).all()

    def resolve_risk(self, risk_id: str, resolution_notes: str) -> bool:
        """
        Mark risk as resolved.

        ✅ FIX 2.1 Cortez5: Now sets resolved_at timestamp
        ✅ FIX 3.3 Cortez5: Added pessimistic locking for concurrent safety
        """
        try:
            # Pessimistic lock: SELECT ... FOR UPDATE
            stmt = select(RiskDB).where(RiskDB.id == risk_id).with_for_update()
            risk = self.db.execute(stmt).scalar_one_or_none()

            if risk:
                risk.resolved = True
                risk.resolved_at = utc_now()  # FIX 2.1 Cortez5
                risk.resolution_notes = resolution_notes
                risk.updated_at = utc_now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to resolve risk {risk_id}: {e}")
            raise

    def get_by_session_ids(self, session_ids: List[str]) -> Dict[str, List[RiskDB]]:
        """
        Get all risks for multiple sessions in a single query (batch loading).

        This prevents N+1 query problems when loading risks for multiple sessions.

        Args:
            session_ids: List of session IDs to fetch risks for

        Returns:
            Dictionary mapping session_id to list of risks for that session
        """
        if not session_ids:
            return {}

        risks = (
            self.db.query(RiskDB)
            .filter(RiskDB.session_id.in_(session_ids))
            .order_by(RiskDB.session_id, desc(RiskDB.created_at))
            .all()
        )

        # Group risks by session_id
        result: Dict[str, List[RiskDB]] = {sid: [] for sid in session_ids}
        for risk in risks:
            if risk.session_id in result:
                result[risk.session_id].append(risk)

        return result

    def exists(self, risk_id: str) -> bool:
        """
        Check if a risk exists without loading the full object.

        ✅ FIX 3.6 Cortez5: Efficient existence check

        Args:
            risk_id: Risk ID to check

        Returns:
            True if risk exists, False otherwise
        """
        return (
            self.db.query(RiskDB.id)
            .filter(RiskDB.id == risk_id)
            .first() is not None
        )

    def count_by_session(self, session_id: str, include_resolved: bool = True) -> int:
        """
        Count risks for a session.

        ✅ FIX 3.6 Cortez5: Efficient count without loading objects

        Args:
            session_id: Session ID
            include_resolved: If False, only count unresolved risks

        Returns:
            Number of risks
        """
        query = self.db.query(RiskDB).filter(RiskDB.session_id == session_id)
        if not include_resolved:
            query = query.filter(RiskDB.resolved == False)
        return query.count()

    def count_by_level(self, session_id: str, level: str) -> int:
        """
        Count risks of a specific level for a session.

        ✅ FIX 3.6 Cortez5: Efficient count by risk level

        Args:
            session_id: Session ID
            level: Risk level (low, medium, high, critical)

        Returns:
            Number of risks at specified level
        """
        return (
            self.db.query(RiskDB)
            .filter(
                RiskDB.session_id == session_id,
                RiskDB.risk_level == level.lower()
            )
            .count()
        )

    def clean_orphan_trace_ids(self, risk_id: str) -> int:
        """
        FIX 5.1 Cortez7: Remove trace_ids that reference deleted traces.

        Cleans up the trace_ids JSON array by removing IDs that no longer
        exist in the cognitive_traces table.

        Args:
            risk_id: Risk ID to clean

        Returns:
            Number of orphan IDs removed

        Example:
            >>> removed = risk_repo.clean_orphan_trace_ids("risk_123")
            >>> print(f"Removed {removed} orphan trace IDs")
        """
        try:
            risk = self.db.query(RiskDB).filter(RiskDB.id == risk_id).first()
            if not risk or not risk.trace_ids:
                return 0

            # Get valid trace IDs that still exist
            valid_ids = self.db.query(CognitiveTraceDB.id).filter(
                CognitiveTraceDB.id.in_(risk.trace_ids)
            ).all()
            valid_ids_set = {id for (id,) in valid_ids}

            # Filter out orphan IDs
            original_count = len(risk.trace_ids)
            risk.trace_ids = [id for id in risk.trace_ids if id in valid_ids_set]
            removed_count = original_count - len(risk.trace_ids)

            if removed_count > 0:
                self.db.commit()
                logger.info(
                    f"Cleaned {removed_count} orphan trace IDs from risk {risk_id}",
                    extra={"risk_id": risk_id, "removed_count": removed_count}
                )

            return removed_count
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to clean orphan trace IDs for risk {risk_id}: {e}")
            raise

    def clean_all_orphan_trace_ids(self) -> Dict[str, int]:
        """
        FIX 5.1 Cortez7: Clean orphan trace_ids from all risks.

        Iterates through all risks with trace_ids and removes references
        to traces that no longer exist.

        Returns:
            Dictionary with total_risks_processed and total_orphans_removed

        Example:
            >>> result = risk_repo.clean_all_orphan_trace_ids()
            >>> print(f"Processed {result['total_risks_processed']} risks")
        """
        try:
            risks_with_traces = self.db.query(RiskDB).filter(
                RiskDB.trace_ids != None,
                RiskDB.trace_ids != []
            ).all()

            total_removed = 0
            risks_processed = 0

            for risk in risks_with_traces:
                removed = self.clean_orphan_trace_ids(risk.id)
                total_removed += removed
                risks_processed += 1

            return {
                "total_risks_processed": risks_processed,
                "total_orphans_removed": total_removed
            }
        except Exception as e:
            logger.error(f"Failed to clean all orphan trace IDs: {e}")
            raise

    def get_by_activity(
        self,
        activity_id: str,
        resolved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[RiskDB]:
        """
        Get all risks for an activity.

        FIX 2.6 Cortez11: Added missing method for activity-based risk queries.

        Args:
            activity_id: Activity ID to filter by
            resolved: Optional filter by resolution status (True/False/None for all)
            limit: Maximum records to return (default 100)
            offset: Records to skip (default 0)

        Returns:
            List of risks for the activity, ordered by creation date (newest first)
        """
        query = self.db.query(RiskDB).filter(RiskDB.activity_id == activity_id)

        if resolved is not None:
            query = query.filter(RiskDB.resolved == resolved)

        return query.order_by(desc(RiskDB.created_at)).limit(limit).offset(offset).all()

    def get_by_dimension(
        self,
        dimension: str,
        resolved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[RiskDB]:
        """
        Get all risks for a specific dimension.

        FIX 2.7 Cortez11: Added missing method for dimension-based risk queries.

        Args:
            dimension: Risk dimension to filter by (cognitive, ethical, epistemic, technical, governance)
            resolved: Optional filter by resolution status (True/False/None for all)
            limit: Maximum records to return (default 100)
            offset: Records to skip (default 0)

        Returns:
            List of risks for the dimension, ordered by creation date (newest first)
        """
        query = self.db.query(RiskDB).filter(RiskDB.dimension == dimension.lower())

        if resolved is not None:
            query = query.filter(RiskDB.resolved == resolved)

        return query.order_by(desc(RiskDB.created_at)).limit(limit).offset(offset).all()


class EvaluationRepository:
    """Repository for evaluation operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, evaluation: EvaluationReport) -> EvaluationDB:
        """
        Create a new evaluation.

        Note: The EvaluationReport Pydantic model has separate fields
        (recommendations_student, recommendations_teacher), but the database
        stores them combined in a single 'recommendations' JSON field with
        structure: {"student": [...], "teacher": [...]}.
        """
        # Combine student and teacher recommendations into single JSON structure
        recommendations = {
            "student": evaluation.recommendations_student,
            "teacher": evaluation.recommendations_teacher,
        }

        # Handle reasoning_analysis (Optional field despite comment, add defensive check)
        reasoning_analysis_dict = {}
        if evaluation.reasoning_analysis is not None:
            reasoning_analysis_dict = evaluation.reasoning_analysis.model_dump()

        # Handle git_analysis (Optional field, can be None or Pydantic model)
        git_analysis_dict = {}
        if evaluation.git_analysis is not None:
            git_analysis_dict = evaluation.git_analysis.model_dump()

        # Map ai_dependency_score + ai_usage_patterns to ai_dependency_metrics JSON
        # Note: Database has ai_dependency_metrics JSON, but Pydantic has separate fields
        ai_dependency_metrics = {
            "score": evaluation.ai_dependency_score,
            "usage_patterns": evaluation.ai_usage_patterns,
            "reasoning_map": evaluation.reasoning_map,
        }

        # ✅ FIXED (2025-11-22): Conversión defensiva de enums (C5)
        db_evaluation = EvaluationDB(
            id=str(uuid4()),
            session_id=evaluation.session_id,
            student_id=evaluation.student_id,
            activity_id=evaluation.activity_id,
            overall_competency_level=_safe_enum_to_str(evaluation.overall_competency_level, CompetencyLevel),
            overall_score=evaluation.overall_score,
            dimensions=[d.model_dump() for d in evaluation.dimensions],
            key_strengths=evaluation.key_strengths,
            improvement_areas=evaluation.improvement_areas,
            recommendations=recommendations,  # Combined structure (Phase 0 fix)
            reasoning_analysis=reasoning_analysis_dict,  # Required, always present
            git_analysis=git_analysis_dict,  # Optional, empty dict if None
            ai_dependency_metrics=ai_dependency_metrics,  # Combined AI metrics
        )
        self.db.add(db_evaluation)
        self.db.commit()
        self.db.refresh(db_evaluation)
        return db_evaluation

    def get_by_id(self, evaluation_id: str) -> Optional[EvaluationDB]:
        """Get evaluation by ID"""
        return self.db.query(EvaluationDB).filter(EvaluationDB.id == evaluation_id).first()

    def get_by_session(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[EvaluationDB]:
        """
        Get all evaluations for a session.

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries
        """
        return (
            self.db.query(EvaluationDB)
            .filter(EvaluationDB.session_id == session_id)
            .order_by(desc(EvaluationDB.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_by_student(self, student_id: str, limit: int = 100, offset: int = 0) -> List[EvaluationDB]:
        """
        Get evaluations for a student with pagination.

        FIX 3.5 Cortez4: Added pagination to prevent unbounded queries.

        Args:
            student_id: Student ID
            limit: Maximum records to return (default 100)
            offset: Records to skip (default 0)

        Returns:
            List of evaluations for the student
        """
        return (
            self.db.query(EvaluationDB)
            .filter(EvaluationDB.student_id == student_id)
            .order_by(desc(EvaluationDB.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def get_latest_by_session_ids(self, session_ids: List[str]) -> Dict[str, EvaluationDB]:
        """
        FIX 3.4.2 Cortez4: Get latest evaluation per session in single query.
        Prevents N+1 queries when loading latest evaluations for multiple sessions.

        Args:
            session_ids: List of session IDs to fetch evaluations for

        Returns:
            Dictionary mapping session_id to the latest evaluation for that session
        """
        if not session_ids:
            return {}

        from sqlalchemy import func, and_

        # Subquery to get max created_at per session
        subq = self.db.query(
            EvaluationDB.session_id,
            func.max(EvaluationDB.created_at).label('max_created')
        ).filter(
            EvaluationDB.session_id.in_(session_ids)
        ).group_by(EvaluationDB.session_id).subquery()

        # Join to get full evaluation records
        evals = self.db.query(EvaluationDB).join(
            subq,
            and_(
                EvaluationDB.session_id == subq.c.session_id,
                EvaluationDB.created_at == subq.c.max_created
            )
        ).all()

        return {e.session_id: e for e in evals}

    def get_by_session_ids(self, session_ids: List[str]) -> Dict[str, List[EvaluationDB]]:
        """
        FIX 3.4.2 Cortez4: Get all evaluations for multiple sessions in single query.
        Prevents N+1 queries when loading evaluations for multiple sessions.

        Args:
            session_ids: List of session IDs to fetch evaluations for

        Returns:
            Dictionary mapping session_id to list of evaluations for that session
        """
        if not session_ids:
            return {}

        evals = (
            self.db.query(EvaluationDB)
            .filter(EvaluationDB.session_id.in_(session_ids))
            .order_by(EvaluationDB.session_id, desc(EvaluationDB.created_at))
            .all()
        )

        # Group evaluations by session_id
        result: Dict[str, List[EvaluationDB]] = {sid: [] for sid in session_ids}
        for eval in evals:
            if eval.session_id in result:
                result[eval.session_id].append(eval)

        return result

    def get_by_activity(
        self,
        activity_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[EvaluationDB]:
        """
        Get all evaluations for an activity.

        FIX 2.8 Cortez11: Added missing method for activity-based evaluation queries.

        Args:
            activity_id: Activity ID to filter by
            limit: Maximum records to return (default 100)
            offset: Records to skip (default 0)

        Returns:
            List of evaluations for the activity, ordered by creation date (newest first)
        """
        return (
            self.db.query(EvaluationDB)
            .filter(EvaluationDB.activity_id == activity_id)
            .order_by(desc(EvaluationDB.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )


class TraceSequenceRepository:
    """Repository for trace sequence operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, sequence: TraceSequence) -> TraceSequenceDB:
        """
        Create a new trace sequence.

        FIX 10.7 Cortez10: Added transaction safety with try/except/rollback.
        """
        try:
            db_sequence = TraceSequenceDB(
                id=sequence.id,
                session_id=sequence.session_id,
                student_id=sequence.student_id,
                activity_id=sequence.activity_id,
                start_time=sequence.start_time,
                end_time=sequence.end_time,
                reasoning_path=sequence.reasoning_path,
                strategy_changes=sequence.strategy_changes,
                ai_dependency_score=sequence.ai_dependency_score,
                trace_ids=[t.id for t in sequence.traces],
            )
            self.db.add(db_sequence)
            self.db.commit()
            self.db.refresh(db_sequence)
            return db_sequence
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create trace sequence: {e}")
            raise

    def get_by_id(self, sequence_id: str) -> Optional[TraceSequenceDB]:
        """Get sequence by ID"""
        return (
            self.db.query(TraceSequenceDB)
            .filter(TraceSequenceDB.id == sequence_id)
            .first()
        )

    def get_by_session(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0,
        load_relations: bool = False
    ) -> List[TraceSequenceDB]:
        """
        Get all sequences for a session.

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries
        FIX 10.12 Cortez10: Added load_relations option for eager loading
        """
        query = self.db.query(TraceSequenceDB).filter(
            TraceSequenceDB.session_id == session_id
        )

        if load_relations:
            query = query.options(selectinload(TraceSequenceDB.session))

        return (
            query
            .order_by(TraceSequenceDB.start_time)
            .limit(limit)
            .offset(offset)
            .all()
        )

    # FIX 10.19 Cortez10: Added count methods for consistency with other repositories
    def count_by_session(self, session_id: str) -> int:
        """Count trace sequences for a session."""
        return (
            self.db.query(TraceSequenceDB)
            .filter(TraceSequenceDB.session_id == session_id)
            .count()
        )

    def count_by_student(self, student_id: str) -> int:
        """Count trace sequences for a student."""
        return (
            self.db.query(TraceSequenceDB)
            .filter(TraceSequenceDB.student_id == student_id)
            .count()
        )


class ActivityRepository:
    """Repository for activity operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        activity_id: str,
        title: str,
        instructions: str,
        teacher_id: str,
        policies: dict,
        description: Optional[str] = None,
        evaluation_criteria: Optional[List[str]] = None,
        subject: Optional[str] = None,
        difficulty: Optional[str] = None,
        estimated_duration_minutes: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> ActivityDB:
        """Create a new activity"""
        # Verificar que activity_id no exista
        existing = self.get_by_activity_id(activity_id)
        if existing:
            raise ValueError(f"Activity with ID '{activity_id}' already exists")

        activity = ActivityDB(
            id=str(uuid4()),
            activity_id=activity_id,
            title=title,
            description=description,
            instructions=instructions,
            evaluation_criteria=evaluation_criteria or [],
            teacher_id=teacher_id,
            policies=policies,
            subject=subject,
            difficulty=difficulty,
            estimated_duration_minutes=estimated_duration_minutes,
            tags=tags or [],
            status="draft",
        )
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def get_by_id(self, activity_id: str) -> Optional[ActivityDB]:
        """Get activity by ID

        FIX Cortez20: Renamed param from 'id' to 'activity_id' for consistency
        """
        return self.db.query(ActivityDB).filter(ActivityDB.id == activity_id).first()

    def get_by_activity_id(self, activity_id: str) -> Optional[ActivityDB]:
        """Get activity by activity_id (unique identifier)"""
        return self.db.query(ActivityDB).filter(ActivityDB.activity_id == activity_id).first()

    def get_by_teacher(
        self, teacher_id: str, status: Optional[str] = None
    ) -> List[ActivityDB]:
        """Get all activities created by a teacher"""
        query = self.db.query(ActivityDB).filter(ActivityDB.teacher_id == teacher_id)
        if status:
            query = query.filter(ActivityDB.status == status)
        return query.order_by(desc(ActivityDB.created_at)).all()

    def get_all(
        self,
        status: Optional[str] = None,
        subject: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 100,
    ) -> List[ActivityDB]:
        """Get all activities with optional filters"""
        query = self.db.query(ActivityDB)

        if status:
            query = query.filter(ActivityDB.status == status)
        if subject:
            query = query.filter(ActivityDB.subject == subject)
        if difficulty:
            query = query.filter(ActivityDB.difficulty == difficulty)

        return query.order_by(desc(ActivityDB.created_at)).limit(limit).all()

    def update(
        self,
        activity_id: str,
        **kwargs,
    ) -> Optional[ActivityDB]:
        """
        Update activity fields.

        Only allows updating safe, user-modifiable fields via whitelist.

        Raises:
            ValueError: If attempting to update a protected field
            TypeError: If field value has incorrect type
        """
        # Whitelist de campos actualizables (seguridad)
        UPDATEABLE_FIELDS = {
            "title": str,
            "description": str,
            "instructions": str,
            "difficulty": str,
            "tags": list,
            "learning_objectives": list,
            "evaluation_criteria": dict,
            "estimated_duration_minutes": int,
            "max_ai_assistance": float,
        }

        activity = self.get_by_activity_id(activity_id)
        if not activity:
            return None

        # Validar y actualizar solo campos permitidos
        for key, value in kwargs.items():
            # Seguridad: Verificar que el campo esté en whitelist
            if key not in UPDATEABLE_FIELDS:
                raise ValueError(
                    f"Cannot update field '{key}'. "
                    f"Allowed fields: {', '.join(UPDATEABLE_FIELDS.keys())}"
                )

            # Validar tipo si no es None
            if value is not None:
                expected_type = UPDATEABLE_FIELDS[key]
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"Invalid type for field '{key}': "
                        f"expected {expected_type.__name__}, got {type(value).__name__}"
                    )

                # ✅ FIXED (2025-11-22): Validación de rangos para prevenir corrupción de datos
                # Validar rangos/valores permitidos según el campo
                if key == "max_ai_assistance":
                    if not (0.0 <= value <= 1.0):
                        raise ValueError(
                            f"max_ai_assistance must be in range [0.0, 1.0], got {value}"
                        )

                elif key == "estimated_duration_minutes":
                    if value <= 0:
                        raise ValueError(
                            f"estimated_duration_minutes must be positive, got {value}"
                        )

                elif key == "difficulty":
                    VALID_DIFFICULTIES = ["INICIAL", "INTERMEDIO", "AVANZADO"]
                    if value not in VALID_DIFFICULTIES:
                        raise ValueError(
                            f"difficulty must be one of {VALID_DIFFICULTIES}, got '{value}'"
                        )

                elif key == "title":
                    if not (3 <= len(value) <= 200):
                        raise ValueError(
                            f"title length must be between 3 and 200 characters, got {len(value)}"
                        )

                elif key == "description":
                    if len(value) > 2000:
                        raise ValueError(
                            f"description length must be <= 2000 characters, got {len(value)}"
                        )

                elif key == "tags":
                    if len(value) == 0:
                        raise ValueError("tags list cannot be empty")
                    if not all(isinstance(tag, str) for tag in value):
                        raise TypeError("tags must be a list of strings")
                    if not all(len(tag) >= 2 for tag in value):
                        raise ValueError("each tag must have at least 2 characters")

                setattr(activity, key, value)

        activity.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(activity)
        return activity

    def publish(self, activity_id: str) -> Optional[ActivityDB]:
        """
        Publish an activity (change status from draft to active)

        ✅ FIX 3.3 Cortez5: Added pessimistic locking for concurrent safety
        """
        try:
            # Pessimistic lock: SELECT ... FOR UPDATE
            stmt = select(ActivityDB).where(ActivityDB.activity_id == activity_id).with_for_update()
            activity = self.db.execute(stmt).scalar_one_or_none()

            if not activity:
                return None

            activity.status = "active"
            activity.published_at = utc_now()
            activity.updated_at = utc_now()
            self.db.commit()
            self.db.refresh(activity)
            return activity
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to publish activity {activity_id}: {e}")
            raise

    def archive(self, activity_id: str) -> Optional[ActivityDB]:
        """
        Archive an activity

        ✅ FIX 3.3 Cortez5: Added pessimistic locking for concurrent safety
        """
        try:
            # Pessimistic lock: SELECT ... FOR UPDATE
            stmt = select(ActivityDB).where(ActivityDB.activity_id == activity_id).with_for_update()
            activity = self.db.execute(stmt).scalar_one_or_none()

            if not activity:
                return None

            activity.status = "archived"
            activity.updated_at = utc_now()
            self.db.commit()
            self.db.refresh(activity)
            return activity
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to archive activity {activity_id}: {e}")
            raise

    def delete(self, activity_id: str) -> bool:
        """
        Delete an activity (soft delete by archiving)

        ✅ FIX 3.3 Cortez5: Added pessimistic locking for concurrent safety
        """
        try:
            # Pessimistic lock: SELECT ... FOR UPDATE
            stmt = select(ActivityDB).where(ActivityDB.activity_id == activity_id).with_for_update()
            activity = self.db.execute(stmt).scalar_one_or_none()

            if not activity:
                return False

            # Soft delete: archive instead of physical deletion
            activity.status = "archived"
            activity.updated_at = utc_now()
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete activity {activity_id}: {e}")
            raise

    def get_by_ids(self, activity_ids: List[str]) -> Dict[str, ActivityDB]:
        """
        Get multiple activities by IDs in a single query (batch loading).

        ✅ FIX 3.5 Cortez5: Batch loading to prevent N+1 queries

        Args:
            activity_ids: List of activity IDs to fetch

        Returns:
            Dictionary mapping activity_id to ActivityDB (missing IDs not in dict)
        """
        if not activity_ids:
            return {}

        activities = (
            self.db.query(ActivityDB)
            .filter(ActivityDB.activity_id.in_(activity_ids))
            .all()
        )
        return {activity.activity_id: activity for activity in activities}


class UserRepository:
    """Repository for user authentication and authorization operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        email: str,
        username: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        student_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
    ) -> UserDB:
        """
        Create a new user

        Args:
            email: User email (unique)
            username: Username (unique)
            hashed_password: Bcrypt hashed password
            full_name: Optional full name
            student_id: Optional student ID (for linking to StudentProfileDB)
            roles: List of roles (default: ["student"])

        Returns:
            Created UserDB instance
        """
        if roles is None:
            roles = ["student"]

        # FIX 3.1.1 Cortez4: Added try/except with rollback for transaction safety
        try:
            user = UserDB(
                id=str(uuid4()),
                email=email.lower(),  # Normalize email to lowercase
                username=username,
                hashed_password=hashed_password,
                full_name=full_name,
                student_id=student_id,
                roles=roles,
                is_active=True,
                is_verified=False,  # Require email verification in production
                login_count=0,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

            logger.info(
                "User created successfully",
                extra={"user_id": user.id, "email": user.email, "roles": user.roles},
            )
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create user: {e}", extra={"email": email})
            raise

    def get_by_id(self, user_id: str) -> Optional[UserDB]:
        """Get user by ID"""
        return self.db.query(UserDB).filter(UserDB.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[UserDB]:
        """
        Get user by email (case-insensitive)

        Args:
            email: User email

        Returns:
            UserDB if found, None otherwise
        """
        return (
            self.db.query(UserDB)
            .filter(UserDB.email == email.lower())
            .first()
        )

    def exists_by_email(self, email: str) -> bool:
        """
        FIX 3.6.2 Cortez4: Check if user exists by email without loading full object.
        More efficient than get_by_email() when only checking existence.

        Args:
            email: User email

        Returns:
            True if user with email exists, False otherwise
        """
        from sqlalchemy import exists
        return self.db.query(
            exists().where(UserDB.email == email.lower())
        ).scalar()

    def get_by_username(self, username: str) -> Optional[UserDB]:
        """
        Get user by username

        Args:
            username: Username

        Returns:
            UserDB if found, None otherwise
        """
        return (
            self.db.query(UserDB)
            .filter(UserDB.username == username)
            .first()
        )

    def get_by_student_id(self, student_id: str) -> Optional[UserDB]:
        """
        Get user by student_id

        Args:
            student_id: Student ID

        Returns:
            UserDB if found, None otherwise
        """
        return (
            self.db.query(UserDB)
            .filter(UserDB.student_id == student_id)
            .first()
        )

    def get_all(
        self,
        include_inactive: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[UserDB]:
        """
        Get all users

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries

        Args:
            include_inactive: If True, include inactive users
            limit: Maximum records to return (default 100)
            offset: Records to skip (default 0)

        Returns:
            List of UserDB instances
        """
        query = self.db.query(UserDB).order_by(desc(UserDB.created_at))
        if not include_inactive:
            query = query.filter(UserDB.is_active == True)
        return query.limit(limit).offset(offset).all()

    def get_by_role(self, role: str) -> List[UserDB]:
        """
        Get all users with a specific role

        Args:
            role: Role name (e.g., "student", "instructor", "admin")

        Returns:
            List of UserDB instances with the role

        Performance Note:
            FIX N+1 #4: Now uses database-specific optimizations.
            - PostgreSQL: Uses ARRAY contains operator (@>) with GIN index for O(log n)
            - SQLite: Uses LIKE on JSON for reasonable performance
        """
        from sqlalchemy import text
        from sqlalchemy.engine import Engine

        # Detect database dialect
        dialect_name = self.db.bind.dialect.name if self.db.bind else "unknown"

        if dialect_name == "postgresql":
            # PostgreSQL: Use ARRAY contains operator with GIN index
            # Assumes roles is stored as ARRAY type in PostgreSQL
            return (
                self.db.query(UserDB)
                .filter(UserDB.is_active == True)
                .filter(text("roles @> ARRAY[:role]::varchar[]"))
                .params(role=role)
                .all()
            )
        elif dialect_name == "sqlite":
            # SQLite: Use JSON LIKE pattern (more efficient than loading all)
            # This works because roles is stored as JSON array string
            return (
                self.db.query(UserDB)
                .filter(UserDB.is_active == True)
                .filter(text("roles LIKE :pattern"))
                .params(pattern=f'%"{role}"%')
                .all()
            )
        else:
            # Fallback for unknown dialects: Load and filter in Python
            all_users = self.db.query(UserDB).filter(UserDB.is_active == True).all()
            return [user for user in all_users if role in user.roles]

    def update_password(self, user_id: str, new_hashed_password: str) -> Optional[UserDB]:
        """
        Update user password

        Args:
            user_id: User ID
            new_hashed_password: New bcrypt hashed password

        Returns:
            Updated UserDB if found, None otherwise
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        user.hashed_password = new_hashed_password
        user.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(user)

        logger.info("User password updated", extra={"user_id": user.id})
        return user

    def update_profile(
        self,
        user_id: str,
        full_name: Optional[str] = None,
        student_id: Optional[str] = None,
    ) -> Optional[UserDB]:
        """
        Update user profile

        Args:
            user_id: User ID
            full_name: New full name (optional)
            student_id: New student ID (optional)

        Returns:
            Updated UserDB if found, None otherwise
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        if full_name is not None:
            user.full_name = full_name
        if student_id is not None:
            user.student_id = student_id

        user.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(user)

        logger.info("User profile updated", extra={"user_id": user.id})
        return user

    def add_role(self, user_id: str, role: str) -> Optional[UserDB]:
        """
        Add role to user

        Args:
            user_id: User ID
            role: Role to add

        Returns:
            Updated UserDB if found, None otherwise
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        if role not in user.roles:
            user.roles = user.roles + [role]  # Create new list for SQLAlchemy to detect change
            user.updated_at = utc_now()
            self.db.commit()
            self.db.refresh(user)

            logger.info(
                "Role added to user", extra={"user_id": user.id, "role": role}
            )

        return user

    def remove_role(self, user_id: str, role: str) -> Optional[UserDB]:
        """
        Remove role from user

        Args:
            user_id: User ID
            role: Role to remove

        Returns:
            Updated UserDB if found, None otherwise
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        if role in user.roles:
            user.roles = [r for r in user.roles if r != role]
            user.updated_at = utc_now()
            self.db.commit()
            self.db.refresh(user)

            logger.info(
                "Role removed from user", extra={"user_id": user.id, "role": role}
            )

        return user

    def update_last_login(self, user_id: str) -> Optional[UserDB]:
        """
        Update last login timestamp and increment login count

        FIX 3.2 Cortez4: Use atomic update to prevent race conditions on login_count.
        Previous implementation used read-modify-write which could lose updates
        under concurrent logins.

        Args:
            user_id: User ID

        Returns:
            Updated UserDB if found, None otherwise
        """
        try:
            # FIX 3.2 Cortez4: Atomic update - prevents race condition
            rows_updated = self.db.query(UserDB).filter(UserDB.id == user_id).update(
                {
                    UserDB.last_login: utc_now(),
                    UserDB.login_count: UserDB.login_count + 1  # Atomic increment
                },
                synchronize_session='fetch'
            )

            if rows_updated == 0:
                return None

            self.db.commit()

            # Fetch the updated user to return
            user = self.get_by_id(user_id)

            logger.info(
                "User login recorded",
                extra={"user_id": user_id, "login_count": user.login_count if user else 0},
            )
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update last login for user {user_id}: {e}")
            raise

    def verify_user(self, user_id: str) -> Optional[UserDB]:
        """
        Mark user as verified (after email verification)

        Args:
            user_id: User ID

        Returns:
            Updated UserDB if found, None otherwise
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        user.is_verified = True
        user.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(user)

        logger.info("User verified", extra={"user_id": user.id})
        return user

    def deactivate_user(self, user_id: str) -> Optional[UserDB]:
        """
        Deactivate user account

        Args:
            user_id: User ID

        Returns:
            Updated UserDB if found, None otherwise
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        user.is_active = False
        user.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(user)

        logger.info("User deactivated", extra={"user_id": user.id})
        return user

    def reactivate_user(self, user_id: str) -> Optional[UserDB]:
        """
        Reactivate user account

        Args:
            user_id: User ID

        Returns:
            Updated UserDB if found, None otherwise
        """
        user = self.get_by_id(user_id)
        if not user:
            return None

        user.is_active = True
        user.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(user)

        logger.info("User reactivated", extra={"user_id": user.id})
        return user

    def delete(self, user_id: str) -> bool:
        """
        Delete user (hard delete - use with caution!)

        Note: In production, consider soft delete (deactivate_user) instead
        to preserve referential integrity and audit trail.

        Args:
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        user = self.get_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()

        logger.warning("User deleted (hard delete)", extra={"user_id": user.id})
        return True


# =============================================================================
# SPRINT 5 REPOSITORIES: Git N2 Traceability + Analytics
# =============================================================================


class GitTraceRepository:
    """
    Repository for Git N2-level traceability operations

    SPRINT 5 - HU-SYS-008: Integración Git
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        session_id: str,
        student_id: str,
        activity_id: str,
        event_type: str,
        commit_hash: str,
        commit_message: str,
        author_name: str,
        author_email: str,
        timestamp: datetime,
        branch_name: str,
        parent_commits: List[str],
        files_changed: List[dict],
        total_lines_added: int = 0,
        total_lines_deleted: int = 0,
        diff: str = "",
        is_merge: bool = False,
        is_revert: bool = False,
        detected_patterns: Optional[List[str]] = None,
        complexity_delta: Optional[int] = None,
        related_cognitive_traces: Optional[List[str]] = None,
        cognitive_state_during_commit: Optional[str] = None,
        time_since_last_interaction_minutes: Optional[int] = None,
        repo_path: Optional[str] = None,
        remote_url: Optional[str] = None,
    ) -> GitTraceDB:
        """
        Create a new Git trace

        Args:
            session_id: Session ID
            student_id: Student ID
            activity_id: Activity ID
            event_type: GitEventType (commit, branch_create, merge, etc.)
            commit_hash: SHA-1 hash (40 chars)
            commit_message: Commit message
            author_name: Author name
            author_email: Author email
            timestamp: Commit timestamp
            branch_name: Branch name
            parent_commits: List of parent commit hashes
            files_changed: List of GitFileChange dicts
            total_lines_added: Total lines added
            total_lines_deleted: Total lines deleted
            diff: Full diff output
            is_merge: True if merge commit
            is_revert: True if revert commit
            detected_patterns: List of CodePattern strings
            complexity_delta: Change in cyclomatic complexity
            related_cognitive_traces: Related N4 trace IDs
            cognitive_state_during_commit: Cognitive state from nearest N4 trace
            time_since_last_interaction_minutes: Minutes since last interaction
            repo_path: Repository local path
            remote_url: Repository remote URL

        Returns:
            Created GitTraceDB instance
        """
        git_trace = GitTraceDB(
            id=str(uuid4()),
            session_id=session_id,
            student_id=student_id,
            activity_id=activity_id,
            event_type=event_type,
            commit_hash=commit_hash,
            commit_message=commit_message,
            author_name=author_name,
            author_email=author_email,
            timestamp=timestamp,
            branch_name=branch_name,
            parent_commits=parent_commits,
            files_changed=files_changed,
            total_lines_added=total_lines_added,
            total_lines_deleted=total_lines_deleted,
            diff=diff,
            is_merge=is_merge,
            is_revert=is_revert,
            detected_patterns=detected_patterns or [],
            complexity_delta=complexity_delta,
            related_cognitive_traces=related_cognitive_traces or [],
            cognitive_state_during_commit=cognitive_state_during_commit,
            time_since_last_interaction_minutes=time_since_last_interaction_minutes,
            repo_path=repo_path,
            remote_url=remote_url,
        )
        self.db.add(git_trace)
        self.db.commit()
        self.db.refresh(git_trace)

        logger.info(
            "Git trace created",
            extra={
                "trace_id": git_trace.id,
                "session_id": session_id,
                "commit_hash": commit_hash,
                "event_type": event_type,
            },
        )
        return git_trace

    def get_by_session(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[GitTraceDB]:
        """
        Get all Git traces for a session ordered by timestamp.

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries
        """
        return (
            self.db.query(GitTraceDB)
            .filter(GitTraceDB.session_id == session_id)
            .order_by(GitTraceDB.timestamp)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_by_student(
        self, student_id: str, limit: Optional[int] = None
    ) -> List[GitTraceDB]:
        """Get Git traces by student ordered by timestamp"""
        query = (
            self.db.query(GitTraceDB)
            .filter(GitTraceDB.student_id == student_id)
            .order_by(desc(GitTraceDB.timestamp))
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_by_commit_hash(self, commit_hash: str) -> Optional[GitTraceDB]:
        """Get Git trace by commit hash"""
        return (
            self.db.query(GitTraceDB)
            .filter(GitTraceDB.commit_hash == commit_hash)
            .first()
        )

    def get_by_student_activity(
        self,
        student_id: str,
        activity_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[GitTraceDB]:
        """
        Get Git traces for student + activity ordered by timestamp.

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries
        """
        return (
            self.db.query(GitTraceDB)
            .filter(
                GitTraceDB.student_id == student_id,
                GitTraceDB.activity_id == activity_id,
            )
            .order_by(GitTraceDB.timestamp)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def count_by_student(self, student_id: str) -> int:
        """Count total commits by student"""
        return (
            self.db.query(GitTraceDB)
            .filter(GitTraceDB.student_id == student_id)
            .count()
        )


class CourseReportRepository:
    """
    Repository for course-level aggregate reports

    SPRINT 5 - HU-DOC-009: Reportes Institucionales
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        course_id: str,
        teacher_id: str,
        report_type: str,
        period_start: datetime,
        period_end: datetime,
        summary_stats: dict,
        competency_distribution: dict,
        risk_distribution: dict,
        top_risks: Optional[List[dict]] = None,
        student_summaries: Optional[List[dict]] = None,
        institutional_recommendations: Optional[List[str]] = None,
        at_risk_students: Optional[List[str]] = None,
        format: str = "json",
        file_path: Optional[str] = None,
    ) -> CourseReportDB:
        """
        Create a new course report

        Args:
            course_id: Course identifier (e.g., "PROG2_2025_1C")
            teacher_id: Teacher who generated the report
            report_type: Type of report (cohort_summary, risk_dashboard, etc.)
            period_start: Start of reporting period
            period_end: End of reporting period
            summary_stats: Aggregate statistics dict
            competency_distribution: Competency level distribution dict
            risk_distribution: Risk level distribution dict
            top_risks: Top 5 most frequent risks
            student_summaries: List of student summary dicts
            institutional_recommendations: Institutional recommendations
            at_risk_students: List of student IDs requiring intervention
            format: Export format (json, pdf, xlsx)
            file_path: Path to exported file

        Returns:
            Created CourseReportDB instance
        """
        report = CourseReportDB(
            id=str(uuid4()),
            course_id=course_id,
            teacher_id=teacher_id,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            summary_stats=summary_stats,
            competency_distribution=competency_distribution,
            risk_distribution=risk_distribution,
            top_risks=top_risks or [],
            student_summaries=student_summaries or [],
            institutional_recommendations=institutional_recommendations or [],
            at_risk_students=at_risk_students or [],
            format=format,
            file_path=file_path,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        logger.info(
            "Course report created",
            extra={
                "report_id": report.id,
                "course_id": course_id,
                "report_type": report_type,
                "teacher_id": teacher_id,
            },
        )
        return report

    def get_by_id(self, report_id: str) -> Optional[CourseReportDB]:
        """Get report by ID"""
        return self.db.query(CourseReportDB).filter(CourseReportDB.id == report_id).first()

    def get_by_course(
        self, course_id: str, limit: Optional[int] = None
    ) -> List[CourseReportDB]:
        """Get reports for a course ordered by period"""
        query = (
            self.db.query(CourseReportDB)
            .filter(CourseReportDB.course_id == course_id)
            .order_by(desc(CourseReportDB.period_start))
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def get_by_teacher(
        self, teacher_id: str, limit: Optional[int] = None
    ) -> List[CourseReportDB]:
        """Get reports by teacher ordered by period"""
        query = (
            self.db.query(CourseReportDB)
            .filter(CourseReportDB.teacher_id == teacher_id)
            .order_by(desc(CourseReportDB.period_start))
        )
        if limit:
            query = query.limit(limit)
        return query.all()

    def mark_exported(self, report_id: str, file_path: str) -> Optional[CourseReportDB]:
        """Mark report as exported with file path"""
        report = self.get_by_id(report_id)
        if not report:
            return None

        report.file_path = file_path
        report.exported_at = utc_now()
        report.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(report)

        logger.info(
            "Course report exported",
            extra={"report_id": report.id, "file_path": file_path},
        )
        return report


class RemediationPlanRepository:
    """
    Repository for remediation plan operations

    SPRINT 5 - HU-DOC-010: Gestión de Riesgos Institucionales
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        student_id: str,
        teacher_id: str,
        plan_type: str,
        description: str,
        start_date: datetime,
        target_completion_date: datetime,
        activity_id: Optional[str] = None,
        trigger_risks: Optional[List[str]] = None,
        objectives: Optional[List[str]] = None,
        recommended_actions: Optional[List[dict]] = None,
    ) -> RemediationPlanDB:
        """
        Create a new remediation plan

        Args:
            student_id: Target student ID
            teacher_id: Teacher creating the plan
            plan_type: Type of plan (tutoring, practice_exercises, etc.)
            description: Plan description
            start_date: Plan start date
            target_completion_date: Target completion date
            activity_id: Optional activity ID (null if general plan)
            trigger_risks: Risk IDs that triggered this plan
            objectives: List of specific objectives
            recommended_actions: List of action dicts

        Returns:
            Created RemediationPlanDB instance
        """
        plan = RemediationPlanDB(
            id=str(uuid4()),
            student_id=student_id,
            teacher_id=teacher_id,
            plan_type=plan_type,
            description=description,
            start_date=start_date,
            target_completion_date=target_completion_date,
            activity_id=activity_id,
            trigger_risks=trigger_risks or [],
            objectives=objectives or [],
            recommended_actions=recommended_actions or [],
            status="pending",
        )
        self.db.add(plan)
        self.db.commit()
        self.db.refresh(plan)

        logger.info(
            "Remediation plan created",
            extra={
                "plan_id": plan.id,
                "student_id": student_id,
                "teacher_id": teacher_id,
                "plan_type": plan_type,
            },
        )
        return plan

    def get_by_id(self, plan_id: str) -> Optional[RemediationPlanDB]:
        """Get plan by ID"""
        return (
            self.db.query(RemediationPlanDB)
            .filter(RemediationPlanDB.id == plan_id)
            .first()
        )

    def get_by_student(
        self,
        student_id: str,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[RemediationPlanDB]:
        """
        Get plans for student, optionally filtered by status.

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries
        """
        query = self.db.query(RemediationPlanDB).filter(
            RemediationPlanDB.student_id == student_id
        )
        if status:
            query = query.filter(RemediationPlanDB.status == status)
        return query.order_by(desc(RemediationPlanDB.start_date)).limit(limit).offset(offset).all()

    def get_by_teacher(
        self, teacher_id: str, status: Optional[str] = None
    ) -> List[RemediationPlanDB]:
        """Get plans by teacher, optionally filtered by status"""
        query = self.db.query(RemediationPlanDB).filter(
            RemediationPlanDB.teacher_id == teacher_id
        )
        if status:
            query = query.filter(RemediationPlanDB.status == status)
        return query.order_by(desc(RemediationPlanDB.target_completion_date)).all()

    def update_status(
        self,
        plan_id: str,
        status: str,
        progress_notes: Optional[str] = None,
        completion_evidence: Optional[List[str]] = None,
    ) -> Optional[RemediationPlanDB]:
        """Update plan status"""
        plan = self.get_by_id(plan_id)
        if not plan:
            return None

        plan.status = status
        if progress_notes:
            plan.progress_notes = progress_notes
        if completion_evidence:
            plan.completion_evidence = completion_evidence

        if status == "completed":
            plan.actual_completion_date = utc_now()

        plan.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(plan)

        logger.info(
            "Remediation plan status updated",
            extra={"plan_id": plan.id, "status": status},
        )
        return plan

    def complete_plan(
        self,
        plan_id: str,
        outcome_evaluation: str,
        success_metrics: Optional[dict] = None,
    ) -> Optional[RemediationPlanDB]:
        """Complete a remediation plan with evaluation"""
        plan = self.get_by_id(plan_id)
        if not plan:
            return None

        plan.status = "completed"
        plan.actual_completion_date = utc_now()
        plan.outcome_evaluation = outcome_evaluation
        if success_metrics:
            plan.success_metrics = success_metrics

        plan.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(plan)

        logger.info(
            "Remediation plan completed",
            extra={"plan_id": plan.id, "success_metrics": success_metrics},
        )
        return plan


class RiskAlertRepository:
    """
    Repository for institutional risk alert operations

    SPRINT 5 - HU-DOC-010: Gestión de Riesgos Institucionales
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        alert_type: str,
        severity: str,
        scope: str,
        title: str,
        description: str,
        detection_rule: str,
        student_id: Optional[str] = None,
        activity_id: Optional[str] = None,
        course_id: Optional[str] = None,
        evidence: Optional[List[str]] = None,
        threshold_value: Optional[float] = None,
        actual_value: Optional[float] = None,
    ) -> RiskAlertDB:
        """
        Create a new risk alert

        Args:
            alert_type: Type of alert (critical_risk_surge, ai_dependency_spike, etc.)
            severity: Severity level (low, medium, high, critical)
            scope: Scope (student, activity, course, institution)
            title: Alert title
            description: Alert description
            detection_rule: Rule that triggered the alert
            student_id: Student ID (if scope=student)
            activity_id: Activity ID (if scope=activity)
            course_id: Course ID (if scope=course)
            evidence: Links to risks, sessions, traces
            threshold_value: Threshold value for detection rule
            actual_value: Actual value that triggered the alert

        Returns:
            Created RiskAlertDB instance
        """
        alert = RiskAlertDB(
            id=str(uuid4()),
            alert_type=alert_type,
            severity=severity,
            scope=scope,
            title=title,
            description=description,
            detection_rule=detection_rule,
            student_id=student_id,
            activity_id=activity_id,
            course_id=course_id,
            evidence=evidence or [],
            threshold_value=threshold_value,
            actual_value=actual_value,
            status="open",
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)

        logger.warning(
            f"Risk alert created: {alert_type}",
            extra={
                "alert_id": alert.id,
                "severity": severity,
                "scope": scope,
                "student_id": student_id,
            },
        )
        return alert

    def get_by_id(self, alert_id: str) -> Optional[RiskAlertDB]:
        """Get alert by ID"""
        return self.db.query(RiskAlertDB).filter(RiskAlertDB.id == alert_id).first()

    def get_by_student(
        self,
        student_id: str,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[RiskAlertDB]:
        """
        Get alerts for student, optionally filtered by status.

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries
        """
        query = self.db.query(RiskAlertDB).filter(
            RiskAlertDB.student_id == student_id
        )
        if status:
            query = query.filter(RiskAlertDB.status == status)
        return query.order_by(desc(RiskAlertDB.detected_at)).limit(limit).offset(offset).all()

    def get_by_course(
        self, course_id: str, status: Optional[str] = None
    ) -> List[RiskAlertDB]:
        """Get alerts for course, optionally filtered by status"""
        query = self.db.query(RiskAlertDB).filter(RiskAlertDB.course_id == course_id)
        if status:
            query = query.filter(RiskAlertDB.status == status)
        return query.order_by(desc(RiskAlertDB.detected_at)).all()

    def get_by_severity(
        self, severity: str, status: Optional[str] = "open"
    ) -> List[RiskAlertDB]:
        """Get alerts by severity level"""
        query = self.db.query(RiskAlertDB).filter(RiskAlertDB.severity == severity)
        if status:
            query = query.filter(RiskAlertDB.status == status)
        return query.order_by(desc(RiskAlertDB.detected_at)).all()

    def get_assigned_to(
        self, teacher_id: str, status: Optional[str] = None
    ) -> List[RiskAlertDB]:
        """Get alerts assigned to a teacher"""
        query = self.db.query(RiskAlertDB).filter(
            RiskAlertDB.assigned_to == teacher_id
        )
        if status:
            query = query.filter(RiskAlertDB.status == status)
        return query.order_by(desc(RiskAlertDB.detected_at)).all()

    def assign_to(self, alert_id: str, teacher_id: str) -> Optional[RiskAlertDB]:
        """Assign alert to a teacher"""
        alert = self.get_by_id(alert_id)
        if not alert:
            return None

        alert.assigned_to = teacher_id
        alert.assigned_at = utc_now()
        alert.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(alert)

        logger.info(
            "Risk alert assigned",
            extra={"alert_id": alert.id, "assigned_to": teacher_id},
        )
        return alert

    def acknowledge(
        self, alert_id: str, acknowledged_by: str
    ) -> Optional[RiskAlertDB]:
        """Acknowledge an alert"""
        alert = self.get_by_id(alert_id)
        if not alert:
            return None

        alert.status = "acknowledged"
        alert.acknowledged_at = utc_now()
        alert.acknowledged_by = acknowledged_by
        alert.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(alert)

        logger.info(
            "Risk alert acknowledged",
            extra={"alert_id": alert.id, "acknowledged_by": acknowledged_by},
        )
        return alert

    def resolve(
        self,
        alert_id: str,
        resolution_notes: str,
        remediation_plan_id: Optional[str] = None,
    ) -> Optional[RiskAlertDB]:
        """Resolve an alert"""
        alert = self.get_by_id(alert_id)
        if not alert:
            return None

        alert.status = "resolved"
        alert.resolution_notes = resolution_notes
        alert.resolved_at = utc_now()
        if remediation_plan_id:
            alert.remediation_plan_id = remediation_plan_id
        alert.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(alert)

        logger.info(
            "Risk alert resolved",
            extra={
                "alert_id": alert.id,
                "remediation_plan_id": remediation_plan_id,
            },
        )
        return alert

    def mark_false_positive(self, alert_id: str) -> Optional[RiskAlertDB]:
        """Mark alert as false positive"""
        alert = self.get_by_id(alert_id)
        if not alert:
            return None

        alert.status = "false_positive"
        alert.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(alert)

        logger.info(
            "Risk alert marked as false positive", extra={"alert_id": alert.id}
        )
        return alert


# =============================================================================
# SPRINT 6 REPOSITORIES: Professional Simulators & Advanced Features
# =============================================================================


class InterviewSessionRepository:
    """
    Repository for interview session operations

    SPRINT 6 - HU-EST-011: Enfrentar Entrevista Técnica Simulada (IT-IA)
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        session_id: str,
        student_id: str,
        interview_type: str,
        activity_id: Optional[str] = None,
        difficulty_level: str = "MEDIUM",
        questions_asked: Optional[List[dict]] = None,
    ) -> InterviewSessionDB:
        """
        Create a new interview session

        Args:
            session_id: Session ID
            student_id: Student ID
            interview_type: Type of interview (CONCEPTUAL, ALGORITHMIC, DESIGN, BEHAVIORAL)
            activity_id: Optional activity ID
            difficulty_level: Difficulty (EASY, MEDIUM, HARD)
            questions_asked: Initial questions

        Returns:
            Created InterviewSessionDB instance
        """
        interview = InterviewSessionDB(
            id=str(uuid4()),
            session_id=session_id,
            student_id=student_id,
            activity_id=activity_id,
            interview_type=interview_type,
            difficulty_level=difficulty_level,
            questions_asked=questions_asked or [],
            responses=[],
        )
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)

        logger.info(
            "Interview session created",
            extra={
                "interview_id": interview.id,
                "session_id": session_id,
                "interview_type": interview_type,
            },
        )
        return interview

    def add_question(
        self, interview_id: str, question: dict
    ) -> Optional[InterviewSessionDB]:
        """Add a question to an interview"""
        interview = self.get_by_id(interview_id)
        if not interview:
            return None

        interview.questions_asked = interview.questions_asked + [question]
        interview.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def add_response(
        self, interview_id: str, response: dict
    ) -> Optional[InterviewSessionDB]:
        """Add a student response to an interview"""
        interview = self.get_by_id(interview_id)
        if not interview:
            return None

        interview.responses = interview.responses + [response]
        interview.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def complete_interview(
        self,
        interview_id: str,
        evaluation_score: float,
        evaluation_breakdown: dict,
        feedback: str,
        duration_minutes: int,
    ) -> Optional[InterviewSessionDB]:
        """Complete an interview with final evaluation"""
        interview = self.get_by_id(interview_id)
        if not interview:
            return None

        interview.evaluation_score = evaluation_score
        interview.evaluation_breakdown = evaluation_breakdown
        interview.feedback = feedback
        interview.duration_minutes = duration_minutes
        interview.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(interview)

        logger.info(
            "Interview completed",
            extra={
                "interview_id": interview.id,
                "evaluation_score": evaluation_score,
            },
        )
        return interview

    def get_by_id(self, interview_id: str) -> Optional[InterviewSessionDB]:
        """Get interview by ID"""
        return (
            self.db.query(InterviewSessionDB)
            .filter(InterviewSessionDB.id == interview_id)
            .first()
        )

    def get_by_session(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[InterviewSessionDB]:
        """
        Get all interviews for a session.

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries
        """
        return (
            self.db.query(InterviewSessionDB)
            .filter(InterviewSessionDB.session_id == session_id)
            .order_by(InterviewSessionDB.created_at)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_by_student(
        self, student_id: str, limit: Optional[int] = None
    ) -> List[InterviewSessionDB]:
        """Get interviews by student"""
        query = (
            self.db.query(InterviewSessionDB)
            .filter(InterviewSessionDB.student_id == student_id)
            .order_by(desc(InterviewSessionDB.created_at))
        )
        if limit:
            query = query.limit(limit)
        return query.all()


class IncidentSimulationRepository:
    """
    Repository for incident simulation operations

    SPRINT 6 - HU-EST-012: Responder Incidente en Producción (IR-IA)
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        session_id: str,
        student_id: str,
        incident_type: str,
        incident_description: str,
        activity_id: Optional[str] = None,
        severity: str = "HIGH",
        simulated_logs: Optional[str] = None,
        simulated_metrics: Optional[dict] = None,
    ) -> IncidentSimulationDB:
        """
        Create a new incident simulation

        Args:
            session_id: Session ID
            student_id: Student ID
            incident_type: Type (API_ERROR, PERFORMANCE, SECURITY, DATABASE, DEPLOYMENT)
            incident_description: Description of the simulated incident
            activity_id: Optional activity ID
            severity: Severity (LOW, MEDIUM, HIGH, CRITICAL)
            simulated_logs: Simulated error logs
            simulated_metrics: Simulated monitoring metrics

        Returns:
            Created IncidentSimulationDB instance
        """
        incident = IncidentSimulationDB(
            id=str(uuid4()),
            session_id=session_id,
            student_id=student_id,
            activity_id=activity_id,
            incident_type=incident_type,
            severity=severity,
            incident_description=incident_description,
            simulated_logs=simulated_logs,
            simulated_metrics=simulated_metrics or {},
            diagnosis_process=[],
        )
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)

        logger.info(
            "Incident simulation created",
            extra={
                "incident_id": incident.id,
                "session_id": session_id,
                "incident_type": incident_type,
                "severity": severity,
            },
        )
        return incident

    def add_diagnosis_step(
        self, incident_id: str, diagnosis_step: dict
    ) -> Optional[IncidentSimulationDB]:
        """Add a diagnosis step to the incident"""
        incident = self.get_by_id(incident_id)
        if not incident:
            return None

        incident.diagnosis_process = incident.diagnosis_process + [diagnosis_step]
        incident.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def complete_incident(
        self,
        incident_id: str,
        solution_proposed: str,
        root_cause_identified: str,
        time_to_diagnose_minutes: int,
        time_to_resolve_minutes: int,
        post_mortem: str,
        evaluation: dict,
    ) -> Optional[IncidentSimulationDB]:
        """Complete an incident with solution and evaluation"""
        incident = self.get_by_id(incident_id)
        if not incident:
            return None

        incident.solution_proposed = solution_proposed
        incident.root_cause_identified = root_cause_identified
        incident.time_to_diagnose_minutes = time_to_diagnose_minutes
        incident.time_to_resolve_minutes = time_to_resolve_minutes
        incident.post_mortem = post_mortem
        incident.evaluation = evaluation
        incident.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(incident)

        logger.info(
            "Incident simulation completed",
            extra={
                "incident_id": incident.id,
                "time_to_resolve": time_to_resolve_minutes,
            },
        )
        return incident

    def get_by_id(self, incident_id: str) -> Optional[IncidentSimulationDB]:
        """Get incident by ID"""
        return (
            self.db.query(IncidentSimulationDB)
            .filter(IncidentSimulationDB.id == incident_id)
            .first()
        )

    def get_by_session(
        self,
        session_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[IncidentSimulationDB]:
        """
        Get all incidents for a session.

        ✅ FIX 3.1 Cortez5: Added limit/offset to prevent unbounded queries
        """
        return (
            self.db.query(IncidentSimulationDB)
            .filter(IncidentSimulationDB.session_id == session_id)
            .order_by(IncidentSimulationDB.created_at)
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_by_student(
        self, student_id: str, limit: Optional[int] = None
    ) -> List[IncidentSimulationDB]:
        """Get incidents by student"""
        query = (
            self.db.query(IncidentSimulationDB)
            .filter(IncidentSimulationDB.student_id == student_id)
            .order_by(desc(IncidentSimulationDB.created_at))
        )
        if limit:
            query = query.limit(limit)
        return query.all()


class LTIDeploymentRepository:
    """
    Repository for LTI deployment operations

    SPRINT 6 - HU-SYS-010: Integración LTI con Moodle
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        platform_name: str,
        issuer: str,
        client_id: str,
        deployment_id: str,
        auth_login_url: str,
        auth_token_url: str,
        public_keyset_url: str,
        access_token_url: Optional[str] = None,
    ) -> LTIDeploymentDB:
        """
        Create a new LTI deployment

        Args:
            platform_name: Platform name (Moodle, Canvas, etc.)
            issuer: LTI issuer URL
            client_id: OAuth2 client ID
            deployment_id: LTI deployment ID
            auth_login_url: OIDC auth login URL
            auth_token_url: OAuth2 token URL
            public_keyset_url: JWKS URL
            access_token_url: Optional access token URL

        Returns:
            Created LTIDeploymentDB instance
        """
        deployment = LTIDeploymentDB(
            id=str(uuid4()),
            platform_name=platform_name,
            issuer=issuer,
            client_id=client_id,
            deployment_id=deployment_id,
            auth_login_url=auth_login_url,
            auth_token_url=auth_token_url,
            public_keyset_url=public_keyset_url,
            access_token_url=access_token_url,
            is_active=True,
        )
        self.db.add(deployment)
        self.db.commit()
        self.db.refresh(deployment)

        logger.info(
            "LTI deployment created",
            extra={
                "deployment_db_id": deployment.id,
                "platform_name": platform_name,
                "issuer": issuer,
                "deployment_id": deployment_id,
            },
        )
        return deployment

    def get_by_id(self, deployment_db_id: str) -> Optional[LTIDeploymentDB]:
        """Get deployment by database ID"""
        return (
            self.db.query(LTIDeploymentDB)
            .filter(LTIDeploymentDB.id == deployment_db_id)
            .first()
        )

    def get_by_issuer_and_deployment(
        self, issuer: str, deployment_id: str
    ) -> Optional[LTIDeploymentDB]:
        """Get deployment by issuer + deployment_id (unique constraint)"""
        return (
            self.db.query(LTIDeploymentDB)
            .filter(
                LTIDeploymentDB.issuer == issuer,
                LTIDeploymentDB.deployment_id == deployment_id,
            )
            .first()
        )

    def get_active_deployments(self) -> List[LTIDeploymentDB]:
        """Get all active LTI deployments"""
        return (
            self.db.query(LTIDeploymentDB)
            .filter(LTIDeploymentDB.is_active == True)
            .order_by(LTIDeploymentDB.platform_name)
            .all()
        )

    def deactivate(self, deployment_db_id: str) -> Optional[LTIDeploymentDB]:
        """Deactivate an LTI deployment"""
        deployment = self.get_by_id(deployment_db_id)
        if not deployment:
            return None

        deployment.is_active = False
        deployment.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(deployment)

        logger.info(
            "LTI deployment deactivated",
            extra={"deployment_db_id": deployment.id},
        )
        return deployment


class LTISessionRepository:
    """
    Repository for LTI session operations

    SPRINT 6 - HU-SYS-010: Integración LTI con Moodle
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        deployment_id: str,
        lti_user_id: str,
        resource_link_id: str,
        lti_user_name: Optional[str] = None,
        lti_user_email: Optional[str] = None,
        lti_context_id: Optional[str] = None,
        lti_context_label: Optional[str] = None,
        lti_context_title: Optional[str] = None,
        session_id: Optional[str] = None,
        launch_token: Optional[str] = None,
        locale: Optional[str] = None,
    ) -> LTISessionDB:
        """
        Create a new LTI session

        Args:
            deployment_id: LTI deployment ID (FK)
            lti_user_id: User ID from Moodle
            resource_link_id: Resource link ID from LTI launch
            lti_user_name: Optional user name
            lti_user_email: Optional user email
            lti_context_id: Optional course ID
            lti_context_label: Optional course code
            lti_context_title: Optional course name
            session_id: Mapped AI-Native session ID
            launch_token: JWT token from LTI launch
            locale: User's locale

        Returns:
            Created LTISessionDB instance
        """
        lti_session = LTISessionDB(
            id=str(uuid4()),
            deployment_id=deployment_id,
            lti_user_id=lti_user_id,
            lti_user_name=lti_user_name,
            lti_user_email=lti_user_email,
            lti_context_id=lti_context_id,
            lti_context_label=lti_context_label,
            lti_context_title=lti_context_title,
            resource_link_id=resource_link_id,
            session_id=session_id,
            launch_token=launch_token,
            locale=locale,
        )
        self.db.add(lti_session)
        self.db.commit()
        self.db.refresh(lti_session)

        logger.info(
            "LTI session created",
            extra={
                "lti_session_id": lti_session.id,
                "lti_user_id": lti_user_id,
                "session_id": session_id,
            },
        )
        return lti_session

    def get_by_id(self, lti_session_id: str) -> Optional[LTISessionDB]:
        """Get LTI session by ID"""
        return (
            self.db.query(LTISessionDB)
            .filter(LTISessionDB.id == lti_session_id)
            .first()
        )

    def get_by_session_id(self, session_id: str) -> Optional[LTISessionDB]:
        """Get LTI session by AI-Native session ID"""
        return (
            self.db.query(LTISessionDB)
            .filter(LTISessionDB.session_id == session_id)
            .first()
        )

    def get_by_lti_user(self, lti_user_id: str) -> List[LTISessionDB]:
        """Get all LTI sessions for a user"""
        return (
            self.db.query(LTISessionDB)
            .filter(LTISessionDB.lti_user_id == lti_user_id)
            .order_by(desc(LTISessionDB.created_at))
            .all()
        )

    def link_to_session(
        self, lti_session_id: str, session_id: str
    ) -> Optional[LTISessionDB]:
        """Link LTI session to AI-Native session"""
        lti_session = self.get_by_id(lti_session_id)
        if not lti_session:
            return None

        lti_session.session_id = session_id
        lti_session.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(lti_session)

        logger.info(
            "LTI session linked to AI-Native session",
            extra={"lti_session_id": lti_session.id, "session_id": session_id},
        )
        return lti_session


# =============================================================================
# FIX 3.2: SimulatorEventRepository
# =============================================================================


class SimulatorEventRepository:
    """
    Repository for simulator events (S-IA-X)

    Provides access to SimulatorEventDB records without direct queries in routers.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        session_id: str,
        student_id: str,
        simulator_type: str,
        event_type: str,
        event_data: dict,
        description: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> SimulatorEventDB:
        """Create a new simulator event"""
        event = SimulatorEventDB(
            id=str(uuid4()),
            session_id=session_id,
            student_id=student_id,
            simulator_type=simulator_type,
            event_type=event_type,
            event_data=event_data or {},
            description=description,
            severity=severity,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        logger.info(
            "Simulator event created",
            extra={
                "event_id": event.id,
                "session_id": session_id,
                "simulator_type": simulator_type,
                "event_type": event_type,
            },
        )
        return event

    def get_by_id(self, event_id: str) -> Optional[SimulatorEventDB]:
        """Get simulator event by ID"""
        return (
            self.db.query(SimulatorEventDB)
            .filter(SimulatorEventDB.id == event_id)
            .first()
        )

    def get_by_session(
        self, session_id: str, limit: int = 100
    ) -> List[SimulatorEventDB]:
        """Get all events for a session ordered by timestamp"""
        return (
            self.db.query(SimulatorEventDB)
            .filter(SimulatorEventDB.session_id == session_id)
            .order_by(SimulatorEventDB.timestamp)
            .limit(limit)
            .all()
        )

    def get_by_student(
        self, student_id: str, limit: int = 100
    ) -> List[SimulatorEventDB]:
        """Get all events for a student ordered by timestamp descending"""
        return (
            self.db.query(SimulatorEventDB)
            .filter(SimulatorEventDB.student_id == student_id)
            .order_by(desc(SimulatorEventDB.timestamp))
            .limit(limit)
            .all()
        )

    def get_by_simulator_type(
        self, session_id: str, simulator_type: str
    ) -> List[SimulatorEventDB]:
        """Get events for a specific simulator type in a session"""
        return (
            self.db.query(SimulatorEventDB)
            .filter(
                SimulatorEventDB.session_id == session_id,
                SimulatorEventDB.simulator_type == simulator_type,
            )
            .order_by(SimulatorEventDB.timestamp)
            .all()
        )

    def get_by_event_type(
        self, session_id: str, event_type: str
    ) -> List[SimulatorEventDB]:
        """Get events of a specific type in a session"""
        return (
            self.db.query(SimulatorEventDB)
            .filter(
                SimulatorEventDB.session_id == session_id,
                SimulatorEventDB.event_type == event_type,
            )
            .order_by(SimulatorEventDB.timestamp)
            .all()
        )

    def count_by_session(self, session_id: str) -> int:
        """Count total events in a session"""
        return (
            self.db.query(SimulatorEventDB)
            .filter(SimulatorEventDB.session_id == session_id)
            .count()
        )

    def get_event_types_count(self, session_id: str) -> Dict[str, int]:
        """Get count of events by type for a session"""
        from sqlalchemy import func

        results = (
            self.db.query(
                SimulatorEventDB.event_type,
                func.count(SimulatorEventDB.id).label("count"),
            )
            .filter(SimulatorEventDB.session_id == session_id)
            .group_by(SimulatorEventDB.event_type)
            .all()
        )
        return {event_type: count for event_type, count in results}

    def delete_by_session(self, session_id: str) -> int:
        """Delete all events for a session (cascade from session delete)"""
        deleted = (
            self.db.query(SimulatorEventDB)
            .filter(SimulatorEventDB.session_id == session_id)
            .delete()
        )
        self.db.commit()
        return deleted


# =============================================================================
# CORTEZ3 FIX 3.1: StudentProfileRepository
# =============================================================================


class StudentProfileRepository:
    """
    Repository for student profile operations (Cortez3 Fix 3.1)

    Manages student profiles with analytics and risk metrics.

    FIX Cortez11: Aligned field names with ORM StudentProfileDB
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(
        self,
        student_id: str,
        user_id: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        preferred_language: str = "es",
        cognitive_preferences: Optional[Dict[str, Any]] = None,
    ) -> StudentProfileDB:
        """
        Create a new student profile.

        Args:
            student_id: Unique student identifier
            user_id: Optional user ID for authenticated students
            name: Student name
            email: Student email
            preferred_language: Preferred language (default: "es")
            cognitive_preferences: Cognitive preferences dict

        Returns:
            Created StudentProfileDB instance

        FIX Cortez11: Removed non-existent fields (academic_program, current_semester),
        aligned with actual ORM fields
        """
        profile = StudentProfileDB(
            id=str(uuid4()),
            student_id=student_id,
            user_id=user_id,
            name=name,
            email=email,
            preferred_language=preferred_language,
            cognitive_preferences=cognitive_preferences or {},
            # Analytics - initialized to defaults
            total_sessions=0,
            total_interactions=0,
            average_ai_dependency=0.0,
            average_competency_level=None,
            average_competency_score=None,
            # Risk profile
            total_risks=0,
            critical_risks=0,
            risk_trends={},
            # Progress tracking
            competency_evolution=[],
            last_activity_date=None,
            learning_patterns={},
            competency_levels={},
            strengths=[],
            areas_for_improvement=[],
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        logger.info(
            "Student profile created",
            extra={"student_id": student_id, "profile_id": profile.id}
        )
        return profile

    def get_by_id(self, profile_id: str) -> Optional[StudentProfileDB]:
        """Get profile by internal ID.

        FIX Cortez20: Renamed param from 'id' to 'profile_id' for consistency
        """
        return self.db.query(StudentProfileDB).filter(
            StudentProfileDB.id == profile_id
        ).first()

    def get_by_student_id(self, student_id: str) -> Optional[StudentProfileDB]:
        """Get profile by student_id (unique identifier)."""
        return self.db.query(StudentProfileDB).filter(
            StudentProfileDB.student_id == student_id
        ).first()

    def get_by_user_id(self, user_id: str) -> Optional[StudentProfileDB]:
        """Get profile by user_id (authenticated user)."""
        return self.db.query(StudentProfileDB).filter(
            StudentProfileDB.user_id == user_id
        ).first()

    def get_all(self, limit: int = 100, offset: int = 0) -> List[StudentProfileDB]:
        """
        List all profiles with pagination.

        Args:
            limit: Maximum number of records (default 100)
            offset: Number of records to skip

        Returns:
            List of StudentProfileDB instances
        """
        return (
            self.db.query(StudentProfileDB)
            .order_by(desc(StudentProfileDB.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def update_analytics(
        self,
        student_id: str,
        total_sessions: int,
        total_interactions: int,
        average_ai_dependency: float,
        total_risks: int = 0,
        critical_risks: int = 0,
        risk_trends: Optional[Dict[str, Any]] = None,
        competency_evolution: Optional[List[Any]] = None,
        average_competency_level: Optional[str] = None,
        average_competency_score: Optional[float] = None,
    ) -> Optional[StudentProfileDB]:
        """
        Update student analytics metrics.

        FIX Cortez11: Aligned with ORM field names.

        Args:
            student_id: Student identifier
            total_sessions: Total number of sessions
            total_interactions: Total number of interactions
            average_ai_dependency: Average AI dependency score (0.0-1.0)
            total_risks: Total number of risks detected
            critical_risks: Number of critical risks
            risk_trends: Risk trends dictionary
            competency_evolution: Evolution of competencies over time (list)
            average_competency_level: Average competency level string
            average_competency_score: Average competency score (0-10)

        Returns:
            Updated StudentProfileDB or None if not found
        """
        profile = self.get_by_student_id(student_id)
        if not profile:
            return None

        profile.total_sessions = total_sessions
        profile.total_interactions = total_interactions
        profile.average_ai_dependency = average_ai_dependency
        profile.total_risks = total_risks
        profile.critical_risks = critical_risks
        if risk_trends is not None:
            profile.risk_trends = risk_trends
        if competency_evolution is not None:
            profile.competency_evolution = competency_evolution
        if average_competency_level is not None:
            profile.average_competency_level = average_competency_level
        if average_competency_score is not None:
            profile.average_competency_score = average_competency_score
        profile.last_activity_date = utc_now()
        profile.updated_at = utc_now()

        self.db.commit()
        self.db.refresh(profile)

        logger.info(
            "Student analytics updated",
            extra={
                "student_id": student_id,
                "total_sessions": total_sessions,
                "average_ai_dependency": average_ai_dependency
            }
        )
        return profile

    def get_at_risk_students(
        self,
        ai_dependency_threshold: float = 0.7
    ) -> List[StudentProfileDB]:
        """
        Get students with high AI dependency risk.

        FIX Cortez11: Uses average_ai_dependency instead of avg_ai_dependency.

        Args:
            ai_dependency_threshold: Minimum AI dependency score to consider at-risk

        Returns:
            List of at-risk student profiles, ordered by AI dependency (descending)
        """
        return (
            self.db.query(StudentProfileDB)
            .filter(StudentProfileDB.average_ai_dependency >= ai_dependency_threshold)
            .order_by(desc(StudentProfileDB.average_ai_dependency))
            .all()
        )

    def get_by_competency_level(
        self,
        competency_level: str,
        limit: int = 100
    ) -> List[StudentProfileDB]:
        """
        Get students by average competency level.

        FIX Cortez11: Replaced get_by_academic_program (non-existent field)
        with get_by_competency_level.

        Args:
            competency_level: Competency level (e.g., "basico", "intermedio", "avanzado")
            limit: Maximum number of records

        Returns:
            List of StudentProfileDB instances
        """
        return (
            self.db.query(StudentProfileDB)
            .filter(StudentProfileDB.average_competency_level == competency_level)
            .order_by(desc(StudentProfileDB.created_at))
            .limit(limit)
            .all()
        )

    def update_profile(
        self,
        student_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        preferred_language: Optional[str] = None,
        cognitive_preferences: Optional[Dict[str, Any]] = None,
        learning_patterns: Optional[Dict[str, Any]] = None,
        competency_levels: Optional[Dict[str, str]] = None,
        strengths: Optional[List[str]] = None,
        areas_for_improvement: Optional[List[str]] = None,
    ) -> Optional[StudentProfileDB]:
        """
        Update student profile information.

        FIX Cortez11: Aligned with ORM fields, removed non-existent fields.

        Args:
            student_id: Student identifier
            name: New name (optional)
            email: New email (optional)
            preferred_language: Preferred language (optional)
            cognitive_preferences: Cognitive preferences dict (optional)
            learning_patterns: Learning patterns dict (optional)
            competency_levels: Competency levels by area (optional)
            strengths: List of identified strengths (optional)
            areas_for_improvement: List of areas needing improvement (optional)

        Returns:
            Updated StudentProfileDB or None if not found
        """
        profile = self.get_by_student_id(student_id)
        if not profile:
            return None

        if name is not None:
            profile.name = name
        if email is not None:
            profile.email = email
        if preferred_language is not None:
            profile.preferred_language = preferred_language
        if cognitive_preferences is not None:
            profile.cognitive_preferences = cognitive_preferences
        if learning_patterns is not None:
            profile.learning_patterns = learning_patterns
        if competency_levels is not None:
            profile.competency_levels = competency_levels
        if strengths is not None:
            profile.strengths = strengths
        if areas_for_improvement is not None:
            profile.areas_for_improvement = areas_for_improvement

        profile.updated_at = utc_now()
        self.db.commit()
        self.db.refresh(profile)

        logger.info("Student profile updated", extra={"student_id": student_id})
        return profile

    def delete(self, student_id: str) -> bool:
        """
        Delete student profile.

        Args:
            student_id: Student identifier

        Returns:
            True if deleted, False if not found
        """
        profile = self.get_by_student_id(student_id)
        if not profile:
            return False

        self.db.delete(profile)
        self.db.commit()

        logger.warning("Student profile deleted", extra={"student_id": student_id})
        return True

    def get_by_ids(self, student_ids: List[str]) -> Dict[str, StudentProfileDB]:
        """
        Get multiple student profiles by IDs in a single query (batch loading).

        ✅ FIX 3.5 Cortez5: Batch loading to prevent N+1 queries

        Args:
            student_ids: List of student IDs to fetch

        Returns:
            Dictionary mapping student_id to StudentProfileDB (missing IDs not in dict)
        """
        if not student_ids:
            return {}

        profiles = (
            self.db.query(StudentProfileDB)
            .filter(StudentProfileDB.student_id.in_(student_ids))
            .all()
        )
        return {profile.student_id: profile for profile in profiles}
