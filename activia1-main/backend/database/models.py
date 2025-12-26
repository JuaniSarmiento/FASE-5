"""
SQLAlchemy ORM models for persistence

Models:
- Session: Learning sessions
- CognitiveTraceDB: N4-level cognitive traces
- RiskDB: Detected risks
- EvaluationDB: Process evaluations
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, String, Text, Float, Integer, Boolean, ForeignKey, JSON, DateTime, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.types import TypeDecorator


class JSONBCompatible(TypeDecorator):
    """
    A JSON type that uses JSONB on PostgreSQL and JSON on other databases (e.g., SQLite).
    This allows tests to run with SQLite while production uses PostgreSQL with JSONB.
    """
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())

from .base import Base, BaseModel


def _utc_now():
    """Helper para SQLAlchemy default - retorna timestamp timezone-aware"""
    return datetime.now(timezone.utc)


class SessionDB(Base, BaseModel):
    """
    Database model for learning sessions

    IMPORTANTE: Incluye metadatos de Objetivo de Aprendizaje y Estado Cognitivo
    para cumplir con los requisitos de Trazabilidad N4.

    IMPORTANT: user_id is nullable to support:
    1. Anonymous sessions (guest users without authentication)
    2. Legacy data (sessions created before user authentication was implemented)
    3. Programmatic sessions (created by scripts, tests, or automated processes)

    When user_id is None:
    - student_id still identifies the student (can be temporary ID)
    - session.user will be None (not an error, expected behavior)
    - All other session functionality remains operational

    For production systems with mandatory authentication:
    - Consider making user_id NOT NULL and migrating legacy data
    - Add application-level validation to require user authentication
    - Update SessionRepository.create() to require user_id parameter

    SOFT DELETE (MEDIO-6 - Future Improvement):
    Currently uses hard delete which permanently removes records. Consider implementing
    soft delete pattern for data recovery and audit trails:
    - Add `deleted_at = Column(DateTime, nullable=True)` column
    - Add `is_deleted = Column(Boolean, default=False)` for simpler queries
    - Modify all queries to filter `WHERE deleted_at IS NULL`
    - Change delete() to set deleted_at instead of actual deletion
    - Add cascade soft delete to related traces, risks, evaluations
    """

    __tablename__ = "sessions"

    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=False, index=True)
    mode = Column(String(50), nullable=False, default="TUTOR")  # AgentMode

    # Simulator type (when mode=SIMULATOR)
    # V1 Values: product_owner, scrum_master, tech_interviewer, incident_responder, client, devsecops
    # V2 Values: senior_dev, qa_engineer, security_auditor, tech_lead, demanding_client
    simulator_type = Column(String(50), nullable=True, index=True)

    # NEW: User authentication relationship
    # nullable=True supports anonymous sessions, legacy data, and programmatic sessions
    # FIX 3.3 Cortez3: Added ondelete="SET NULL" to maintain sessions when user is deleted
    # FIX 2.1 Cortez7: Cambiado de String(100) a String(36) para consistencia con UUID
    user_id = Column(String(36), ForeignKey('users.id', ondelete="SET NULL"), nullable=True, index=True)

    # Session metadata
    start_time = Column(DateTime, default=_utc_now, nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="active")  # active, completed, abandoned

    # === TRAZABILIDAD N4: METADATOS DE SESIÓN ===
    
    # Objetivo de Aprendizaje de esta sesión
    learning_objective = Column(JSONBCompatible, default=dict, nullable=True)
    # {
    #   "title": "Implementar estructura de datos Cola",
    #   "description": "Comprender y aplicar el concepto de FIFO",
    #   "expected_competencies": ["abstraccion", "implementacion", "testing"],
    #   "difficulty_level": "intermediate"
    # }
    
    # Estado Cognitivo del alumno (actualizado dinámicamente)
    cognitive_status = Column(JSONBCompatible, default=dict, nullable=True)
    # {
    #   "current_phase": "exploration|planning|implementation|debugging|validation|reflection",
    #   "autonomy_level": 0.0-1.0,  # Nivel de autonomía actual
    #   "engagement_score": 0.0-1.0,  # Nivel de engagement
    #   "cognitive_load": "low|medium|high|overload",  # Carga cognitiva estimada
    #   "last_updated": "timestamp"
    # }
    
    # Métricas agregadas de la sesión (calculadas al finalizar)
    session_metrics = Column(JSONBCompatible, default=dict, nullable=True)
    # {
    #   "total_interactions": 15,
    #   "ai_dependency_score": 0.65,
    #   "risk_events": 3,
    #   "autonomy_progression": [0.3, 0.5, 0.7],  # Evolución
    #   "competencies_demonstrated": ["abstraccion", "debugging"]
    # }

    # Relationships
    user = relationship("UserDB", back_populates="sessions")  # NEW
    traces = relationship(
        "CognitiveTraceDB", back_populates="session", cascade="all, delete-orphan"
    )
    risks = relationship(
        "RiskDB", back_populates="session", cascade="all, delete-orphan"
    )
    evaluations = relationship(
        "EvaluationDB", back_populates="session", cascade="all, delete-orphan"
    )
    simulator_events = relationship(
        "SimulatorEventDB", back_populates="session", cascade="all, delete-orphan"
    )
    # Sprint 5 relationships
    # FIX DB-6: Add git_traces relationship with back_populates
    git_traces = relationship(
        "GitTraceDB", back_populates="session", cascade="all, delete-orphan"
    )
    # Sprint 6 relationships
    interview_sessions = relationship(
        "InterviewSessionDB", back_populates="session", cascade="all, delete-orphan"
    )
    incident_simulations = relationship(
        "IncidentSimulationDB", back_populates="session", cascade="all, delete-orphan"
    )
    lti_sessions = relationship(
        "LTISessionDB", back_populates="session", cascade="all, delete-orphan"
    )
    # FIX 3.4: Add trace_sequences relationship with back_populates
    trace_sequences = relationship(
        "TraceSequenceDB", back_populates="session", cascade="all, delete-orphan"
    )

    # Composite indexes for common query patterns
    __table_args__ = (
        # Query: Get all sessions for a student + activity
        Index('idx_session_student_activity', 'student_id', 'activity_id'),
        # Query: Filter sessions by status and order by creation date
        Index('idx_status_created', 'status', 'created_at'),
        # Query: Get active sessions for a student
        Index('idx_student_status', 'student_id', 'status'),
        # Query: Count sessions by status (dashboard metrics)
        Index('idx_session_status', 'status'),
        # Query: Get sessions by mode (TUTOR, SIMULATOR, etc.)
        Index('idx_session_mode_status', 'mode', 'status'),
        # FIX 1.6.2 Cortez4: Check constraint for valid status values
        CheckConstraint(
            "status IN ('active', 'completed', 'paused', 'aborted', 'abandoned')",
            name='ck_session_status_valid'
        ),
        # FIX 1.4 Cortez5: Check constraint for valid mode values
        CheckConstraint(
            "mode IN ('tutor', 'simulator', 'evaluator', 'risk_analyst', 'governance', 'practice', 'TUTOR', 'SIMULATOR', 'EVALUATOR', 'RISK_ANALYST', 'GOVERNANCE', 'PRACTICE')",
            name='ck_session_mode_valid'
        ),
        # FIX 1.4 Cortez5: Check constraint for valid simulator_type values (nullable)
        # FIX Cortez21 DEFECTO 9.2: Added V2 simulators (senior_dev, qa_engineer, security_auditor, tech_lead, demanding_client)
        CheckConstraint(
            "simulator_type IS NULL OR simulator_type IN ('product_owner', 'scrum_master', 'tech_interviewer', 'incident_responder', 'client', 'devsecops', 'senior_dev', 'qa_engineer', 'security_auditor', 'tech_lead', 'demanding_client')",
            name='ck_session_simulator_type_valid'
        ),
    )


class CognitiveTraceDB(Base, BaseModel):
    """Database model for cognitive traces (N4)"""

    __tablename__ = "cognitive_traces"

    # FIX 1.3.3 Cortez4: Added ondelete="CASCADE" to prevent orphan traces
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=False)

    # Trace metadata
    trace_level = Column(String(20), default="n4_cognitivo")  # TraceLevel
    interaction_type = Column(String(50), nullable=False)  # InteractionType

    # Content
    content = Column(Text, nullable=False)
    context = Column(JSON, default=dict)
    trace_metadata = Column(JSON, default=dict)  # NOTE: Use trace_metadata, NOT metadata (SQLAlchemy reserved word)

    # N4 Cognitive analysis - 6 DIMENSIONES DE TRAZABILIDAD
    cognitive_state = Column(String(50), nullable=True)  # CognitiveState
    cognitive_intent = Column(String(200), nullable=True)
    decision_justification = Column(Text, nullable=True)
    alternatives_considered = Column(JSON, default=list)
    strategy_type = Column(String(100), nullable=True)

    # AI involvement
    ai_involvement = Column(Float, default=0.0)  # 0.0 to 1.0

    # === LAS 6 DIMENSIONES DE TRAZABILIDAD N4 (Tesis) ===
    
    # 1. DIMENSIÓN SEMÁNTICA: ¿Qué entendió el alumno?
    semantic_understanding = Column(JSONBCompatible, default=dict, nullable=True)
    # {
    #   "problem_interpretation": "string",  # Interpretación del problema
    #   "key_concepts_identified": ["concept1", "concept2"],  # Conceptos identificados
    #   "misconceptions_detected": ["misconception1"],  # Malentendidos detectados
    #   "understanding_level": "superficial|partial|profundo"
    # }
    
    # 2. DIMENSIÓN ALGORÍTMICA: Evolución del código y alternativas
    algorithmic_evolution = Column(JSONBCompatible, default=dict, nullable=True)
    # {
    #   "code_versions": [{"version": 1, "code": "...", "timestamp": "..."}],
    #   "alternatives_explored": ["approach1", "approach2"],
    #   "design_decisions": [{"decision": "...", "rationale": "..."}],
    #   "complexity_analysis": "O(n) vs O(n^2) - eligió O(n)"
    # }
    
    # 3. DIMENSIÓN COGNITIVA: Razonamientos explícitos y justificaciones
    cognitive_reasoning = Column(JSONBCompatible, default=dict, nullable=True)
    # {
    #   "explicit_reasoning": "string",  # Razonamiento explicitado por el alumno
    #   "metacognitive_awareness": "high|medium|low",  # Conciencia metacognitiva
    #   "problem_decomposition": ["subproblem1", "subproblem2"],
    #   "strategy_justification": "Por qué eligió esta estrategia"
    # }
    
    # 4. DIMENSIÓN INTERACCIONAL: Prompts usados y tipo de intervención de IA
    interactional_data = Column(JSONBCompatible, default=dict, nullable=True)
    # {
    #   "prompt_type": "clarification|delegation|exploration|validation",
    #   "prompt_quality_score": 0.0-1.0,  # Calidad del prompt
    #   "ai_response_type": "socratic|explanatory|hint|code_sample",
    #   "interaction_depth": "superficial|elaborated|deep",
    #   "student_agency": 0.0-1.0  # Qué tanto lideró el alumno
    # }
    
    # 5. DIMENSIÓN ÉTICA/RIESGO: Detección de sesgos o intentos de fraude
    ethical_risk_data = Column(JSONBCompatible, default=dict, nullable=True)
    # {
    #   "plagiarism_indicators": ["indicator1"],  # Indicadores de plagio
    #   "delegation_attempts": 3,  # Intentos de delegación total
    #   "academic_integrity_score": 0.0-1.0,
    #   "bias_detected": ["bias_type1"],  # Sesgos detectados en código/razonamiento
    #   "ethical_concerns": ["concern1"]
    # }
    
    # 6. DIMENSIÓN PROCESUAL: Tiempos y secuencia lógica
    process_data = Column(JSONBCompatible, default=dict, nullable=True)
    # {
    #   "time_to_response": 123.45,  # Segundos hasta responder
    #   "sequence_position": 5,  # Posición en la secuencia
    #   "phase": "exploration|planning|implementation|debugging|validation",
    #   "process_efficiency": 0.0-1.0,  # Eficiencia del proceso
    #   "backtracking_count": 2,  # Veces que retrocedió
    #   "iteration_cycle": "plan->code->test->refine"
    # }

    # Relationships
    session = relationship("SessionDB", back_populates="traces")
    # FIX MEDIO-4: Add self-referential foreign key for trace hierarchy
    parent_trace_id = Column(
        String(36),
        ForeignKey("cognitive_traces.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    # Self-referential relationship for trace hierarchy
    # FIX Cortez25: Use string reference "CognitiveTraceDB.id" to avoid using Python's built-in id() function
    parent_trace = relationship(
        "CognitiveTraceDB",
        remote_side="CognitiveTraceDB.id",
        backref="child_traces",
        foreign_keys=[parent_trace_id]
    )
    agent_id = Column(String(100), nullable=True)

    # NOTE: Cannot add .metadata property here due to SQLAlchemy conflict
    # SQLAlchemy reserves 'metadata' for table metadata during class definition.
    # API layer must map trace_metadata -> metadata in response DTOs.
    # See: src/ai_native_mvp/api/schemas/traces.py for the mapping.

    # Composite indexes for common query patterns
    __table_args__ = (
        # Query: Get all traces for a session filtered by interaction type
        Index('idx_trace_session_interaction', 'session_id', 'interaction_type'),
        # Query: Get student traces ordered by creation date
        Index('idx_trace_student_created', 'student_id', 'created_at'),
        # Query: Analyze cognitive states for a student + activity
        Index('idx_student_activity_state', 'student_id', 'activity_id', 'cognitive_state'),
        # Query: Filter by trace level and session
        Index('idx_session_level', 'session_id', 'trace_level'),
        # FIX DB-4: Index for get_latest_by_session() - ORDER BY created_at DESC LIMIT 1
        # Prevents full table scan when fetching most recent trace for a session
        Index('idx_session_created_desc', 'session_id', 'created_at'),
        # FIX DB-5: Index for activity_id filtering (frequent in reports/analytics)
        Index('idx_trace_activity', 'activity_id'),
        # FIX 1.6.3 Cortez4: Check constraint for valid trace_level values
        CheckConstraint(
            "trace_level IN ('n1_superficial', 'n2_tecnico', 'n3_interaccional', 'n4_cognitivo')",
            name='ck_trace_level_valid'
        ),
        # FIX 1.2.1-1.2.6 Cortez4: GIN indexes for JSONB N4 dimension columns (PostgreSQL only)
        # These enable efficient queries on JSONB data for N4 cognitive traceability
        Index('idx_trace_semantic_gin', 'semantic_understanding', postgresql_using='gin'),
        Index('idx_trace_algorithmic_gin', 'algorithmic_evolution', postgresql_using='gin'),
        Index('idx_trace_cognitive_gin', 'cognitive_reasoning', postgresql_using='gin'),
        Index('idx_trace_interactional_gin', 'interactional_data', postgresql_using='gin'),
        Index('idx_trace_ethical_gin', 'ethical_risk_data', postgresql_using='gin'),
        Index('idx_trace_process_gin', 'process_data', postgresql_using='gin'),
        # FIX 2.15 Cortez6: Range constraint for ai_involvement
        CheckConstraint(
            "ai_involvement >= 0 AND ai_involvement <= 1",
            name='ck_trace_ai_involvement_range'
        ),
    )


class RiskDB(Base, BaseModel):
    """
    Database model for detected risks

    FIXED (2025-11-21): session_id is now REQUIRED (nullable=False).
    Un riesgo SIEMPRE debe estar asociado a una sesión, ya que sin sesión
    no hay contexto (estudiante, actividad, momento temporal, trazas relacionadas).

    Breaking change: Cualquier código que intente crear riesgos sin session_id
    ahora fallará con IntegrityError. Esto es intencional para prevenir data corruption.
    """

    __tablename__ = "risks"

    # REQUIRED: Un riesgo sin sesión no tiene contexto válido
    # FIX 1.3.1 Cortez4: Added ondelete="CASCADE" to prevent orphan risks
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=False)

    # Risk classification
    risk_type = Column(String(100), nullable=False)  # RiskType
    risk_level = Column(String(20), nullable=False)  # RiskLevel
    dimension = Column(String(50), nullable=False)  # RiskDimension

    # Description
    description = Column(Text, nullable=False)
    impact = Column(Text, nullable=True)
    evidence = Column(JSON, default=list)
    trace_ids = Column(JSON, default=list)

    # Analysis
    root_cause = Column(Text, nullable=True)
    impact_assessment = Column(Text, nullable=True)

    # Recommendations
    recommendations = Column(JSON, default=list)
    pedagogical_intervention = Column(Text, nullable=True)

    # Status
    # FIX 1.8.2 Cortez4: Added server_default for raw SQL compatibility
    resolved = Column(Boolean, default=False, server_default='false')
    # FIX 2.1 Cortez5: Added resolved_at timestamp for tracking resolution time
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    detected_by = Column(String(50), default="AR-IA")

    # Relationship
    session = relationship("SessionDB", back_populates="risks")

    # Composite indexes for common query patterns
    __table_args__ = (
        # Query: Get unresolved risks for a student
        Index('idx_student_resolved', 'student_id', 'resolved'),
        # Query: Filter critical risks by level and creation date
        Index('idx_level_created', 'risk_level', 'created_at'),
        # Query: Get risks for student + activity + dimension
        Index('idx_student_activity_dimension', 'student_id', 'activity_id', 'dimension'),
        # Query: Get session risks by type
        Index('idx_risk_session_type', 'session_id', 'risk_type'),
        # FIX 1.1.1 Cortez4: Composite index for "Get unresolved risks for a session"
        Index('idx_risk_session_resolved', 'session_id', 'resolved'),
        # FIX 1.1.2 Cortez4: Composite index for "Get critical/high risks for session"
        Index('idx_risk_session_level', 'session_id', 'risk_level'),
        # FIX 4.1 Cortez7: Index for resolved_at timestamp queries
        Index('idx_risk_resolved_at', 'resolved_at'),
        # FIX 1.6.1 Cortez4: Check constraint for valid risk_level values
        CheckConstraint(
            "risk_level IN ('low', 'medium', 'high', 'critical', 'info')",
            name='ck_risk_level_valid'
        ),
    )


class EvaluationDB(Base, BaseModel):
    """Database model for process evaluations"""

    __tablename__ = "evaluations"

    # FIX 1.3.2 Cortez4: Added ondelete="CASCADE" to prevent orphan evaluations
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=False)

    # Overall assessment
    overall_competency_level = Column(String(50), nullable=False)  # CompetencyLevel
    overall_score = Column(Float, nullable=False)  # 0.0 to 10.0

    # Dimensions (stored as JSON for flexibility)
    dimensions = Column(JSON, default=list)  # List of DimensionEvaluation dicts

    # Feedback
    key_strengths = Column(JSON, default=list)
    improvement_areas = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)

    # Analysis metadata
    reasoning_analysis = Column(JSON, nullable=True)
    git_analysis = Column(JSON, nullable=True)
    ai_dependency_score = Column(Float, default=0.0)  # Scalar AI dependency score (0-1)
    ai_dependency_metrics = Column(JSON, nullable=True)  # Detailed AI dependency metrics

    # Relationship
    session = relationship("SessionDB", back_populates="evaluations")

    # Composite indexes for common query patterns
    __table_args__ = (
        # Query: Get evaluations for student + activity
        Index('idx_eval_student_activity', 'student_id', 'activity_id'),
        # Query: Filter by competency level and score
        Index('idx_competency_score', 'overall_competency_level', 'overall_score'),
        # Query: Get recent evaluations ordered by creation date
        Index('idx_eval_student_created', 'student_id', 'created_at'),
        # FIX 1.1.4 Cortez4: Composite index for "Get latest evaluation for session"
        Index('idx_eval_session_created', 'session_id', 'created_at'),
        # FIX 2.15 Cortez6: Range constraint for overall_score (0-10)
        CheckConstraint(
            "overall_score >= 0 AND overall_score <= 10",
            name='ck_eval_score_range'
        ),
        # FIX 2.15 Cortez6: Range constraint for ai_dependency_score (0-1)
        CheckConstraint(
            "ai_dependency_score >= 0 AND ai_dependency_score <= 1",
            name='ck_eval_ai_dep_range'
        ),
    )


class TraceSequenceDB(Base, BaseModel):
    """
    Database model for trace sequences

    DESIGN DECISION: JSON Array vs Join Table for trace_ids

    Current implementation uses JSON array (trace_ids Column) instead of a proper
    many-to-many relationship table for the following reasons:

    Advantages of JSON array approach:
    1. Simplicity: No additional join table needed
    2. Read performance: Single query to get sequence with all trace IDs
    3. Order preservation: JSON array maintains insertion order (important for sequences)
    4. Flexibility: Can store additional metadata per trace if needed
    5. MVP scope: Sufficient for current use case (sequences are small, <100 traces typically)

    Disadvantages (why a join table might be better in future):
    1. No referential integrity: trace_ids can become orphaned if traces are deleted
    2. No cascade deletes: Deleting a trace doesn't remove it from sequences
    3. Query complexity: Can't JOIN directly to filter sequences by trace properties
    4. Index limitations: Can't create indexes on individual trace IDs in JSON array
    5. Database portability: JSON support varies across databases

    Migration path to join table (if needed in future):
    ```python
    class TraceSequenceTraceAssociation(Base):
        __tablename__ = "trace_sequence_traces"
        id = Column(String(36), primary_key=True)
        sequence_id = Column(String(36), ForeignKey("trace_sequences.id", ondelete="CASCADE"))
        trace_id = Column(String(36), ForeignKey("cognitive_traces.id", ondelete="CASCADE"))
        position = Column(Integer, nullable=False)  # Preserve order
        __table_args__ = (
            Index('idx_seq_trace', 'sequence_id', 'trace_id'),
            Index('idx_seq_position', 'sequence_id', 'position'),
        )

    class TraceSequenceDB:
        traces = relationship("CognitiveTraceDB",
                            secondary="trace_sequence_traces",
                            order_by="TraceSequenceTraceAssociation.position")
    ```

    When to migrate:
    - Sequences grow large (>100 traces per sequence consistently)
    - Need to query "all sequences containing trace X" frequently
    - Referential integrity becomes critical (production with strict compliance)
    - Moving to PostgreSQL with advanced JSON operators (then reassess)

    For now: JSON array is appropriate for MVP and early production.
    """

    __tablename__ = "trace_sequences"

    # FIX 2.1: Add FK constraint to ensure referential integrity
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=False)

    # Sequence metadata
    start_time = Column(DateTime, default=_utc_now, nullable=False)
    end_time = Column(DateTime, nullable=True)

    # Aggregated analysis
    reasoning_path = Column(JSON, default=list)
    strategy_changes = Column(Integer, default=0)
    ai_dependency_score = Column(Float, default=0.0)

    # FIX 4.3 Cortez11: Added cognitive_coherence to match schema expectations
    # Measures coherence of cognitive reasoning across the sequence (0-1 scale)
    cognitive_coherence = Column(Float, nullable=True)

    # References to traces stored as JSON array for simplicity
    # See class docstring for rationale and future migration path
    trace_ids = Column(JSON, default=list)

    # FIX 2.1 & 3.4: Add relationship to session with back_populates
    session = relationship("SessionDB", back_populates="trace_sequences", foreign_keys=[session_id])

    # Composite indexes for common query patterns
    __table_args__ = (
        # Query: Get sequences for student + activity
        Index('idx_trace_seq_student_activity', 'student_id', 'activity_id'),
        # Query: Get sequences ordered by start time
        Index('idx_student_start', 'student_id', 'start_time'),
        # FIX 2.1: Index for session_id FK
        Index('idx_trace_seq_session', 'session_id'),
        # FIX 2.15 Cortez6: Range constraint for ai_dependency_score (0-1)
        CheckConstraint(
            "ai_dependency_score >= 0 AND ai_dependency_score <= 1",
            name='ck_seq_ai_dep_range'
        ),
        # FIX 4.3 Cortez11: Range constraint for cognitive_coherence (0-1)
        CheckConstraint(
            "cognitive_coherence IS NULL OR (cognitive_coherence >= 0 AND cognitive_coherence <= 1)",
            name='ck_seq_cognitive_coherence_range'
        ),
    )


class StudentProfileDB(Base, BaseModel):
    """Database model for student learning profiles"""

    __tablename__ = "student_profiles"

    # FIX 2.2: Keep student_id as logical key, add user_id FK for authenticated users
    student_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Profile metadata
    name = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)

    # Learning analytics
    total_sessions = Column(Integer, default=0)
    total_interactions = Column(Integer, default=0)
    average_ai_dependency = Column(Float, default=0.0)
    average_competency_level = Column(String(50), nullable=True)
    # FIX 10.2 Cortez10: Added average_competency_score to match schema expectations
    average_competency_score = Column(Float, nullable=True)  # Score 0-10

    # Risk profile
    total_risks = Column(Integer, default=0)
    critical_risks = Column(Integer, default=0)
    risk_trends = Column(JSON, default=dict)

    # Progress tracking
    competency_evolution = Column(JSON, default=list)  # Time series data
    last_activity_date = Column(DateTime, nullable=True)

    # FIX 10.2 Cortez10: Added missing fields to match schema expectations
    preferred_language = Column(String(10), default="es", nullable=True)
    cognitive_preferences = Column(JSONBCompatible, default=dict, nullable=True)
    learning_patterns = Column(JSONBCompatible, default=dict, nullable=True)
    competency_levels = Column(JSONBCompatible, default=dict, nullable=True)  # {"area": "level"}
    strengths = Column(JSON, default=list, nullable=True)
    areas_for_improvement = Column(JSON, default=list, nullable=True)

    # FIX 2.2 & 3.4: Add relationship to UserDB with back_populates
    user = relationship("UserDB", back_populates="student_profiles", foreign_keys=[user_id])

    # FIX 2.15 Cortez6: Range constraint for average_ai_dependency
    # FIX 10.2 Cortez10: Added constraint for average_competency_score
    __table_args__ = (
        CheckConstraint(
            "average_ai_dependency >= 0 AND average_ai_dependency <= 1",
            name='ck_profile_ai_dep_range'
        ),
        CheckConstraint(
            "average_competency_score IS NULL OR (average_competency_score >= 0 AND average_competency_score <= 10)",
            name='ck_profile_competency_score_range'
        ),
    )


class ActivityDB(Base, BaseModel):
    """Database model for learning activities created by teachers"""

    __tablename__ = "activities"

    # Activity identification
    activity_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Activity details
    instructions = Column(Text, nullable=False)  # Consigna detallada
    evaluation_criteria = Column(JSON, default=list)  # Lista de criterios

    # Teacher who created it
    # FIX 2.3: Add FK to users table for teacher_id to ensure referential integrity
    teacher_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Pedagogical policies (JSON field for flexibility)
    policies = Column(JSON, default=dict, nullable=False)
    # Structure:
    # {
    #   "max_help_level": "MEDIO",  # MINIMO, BAJO, MEDIO, ALTO
    #   "block_complete_solutions": true,
    #   "require_justification": true,
    #   "allow_code_snippets": false,
    #   "risk_thresholds": {
    #     "ai_dependency": 0.6,
    #     "lack_justification": 0.3
    #   }
    # }

    # Metadata
    subject = Column(String(100), nullable=True)  # Ej: "Programación II"
    difficulty = Column(String(20), nullable=True)  # INICIAL, INTERMEDIO, AVANZADO
    estimated_duration_minutes = Column(Integer, nullable=True)

    # Tags for categorization
    tags = Column(JSON, default=list)  # ["colas", "estructuras", "arreglos"]

    # Activity status
    status = Column(String(20), default="draft")  # draft, active, archived
    published_at = Column(DateTime, nullable=True)

    # FIX 2.3 & 3.4: Add relationship to teacher/user with back_populates
    teacher = relationship("UserDB", back_populates="activities", foreign_keys=[teacher_id])

    # Composite indexes for common query patterns
    __table_args__ = (
        # Query: Get activities by teacher
        Index('idx_activity_teacher_status', 'teacher_id', 'status'),
        # Query: Get active activities
        Index('idx_activity_status_created', 'status', 'created_at'),
        # Query: Search by subject
        Index('idx_activity_subject_status', 'subject', 'status'),
        # FIX 2.5 Cortez6: Check constraint for valid status values
        CheckConstraint(
            "status IN ('draft', 'active', 'archived')",
            name='ck_activity_status_valid'
        ),
        # FIX 2.6 Cortez6: Check constraint for valid difficulty values
        CheckConstraint(
            "difficulty IS NULL OR difficulty IN ('INICIAL', 'INTERMEDIO', 'AVANZADO')",
            name='ck_activity_difficulty_valid'
        ),
    )


class UserDB(Base, BaseModel):
    """
    User model for authentication and authorization

    Stores user credentials, profile information, and roles.
    Used for JWT authentication in production.
    """

    __tablename__ = "users"

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(255), nullable=True)
    student_id = Column(String(100), nullable=True, unique=True, index=True)

    # Authorization
    roles = Column(JSONBCompatible, default=list, nullable=False)  # ["student", "instructor", "admin"]
    # FIX 4.4 Cortez7: Added server_default for raw SQL compatibility
    is_active = Column(Boolean, default=True, server_default='true', nullable=False)
    is_verified = Column(Boolean, default=False, server_default='false', nullable=False)

    # Metadata
    last_login = Column(DateTime, nullable=True)
    # FIX 1.8.1 Cortez4: Added server_default for raw SQL compatibility
    login_count = Column(Integer, default=0, server_default='0')

    # Relationships
    sessions = relationship("SessionDB", back_populates="user", foreign_keys="SessionDB.user_id")
    # FIX 3.4: Add back_populates for student_profiles and activities
    student_profiles = relationship("StudentProfileDB", back_populates="user", foreign_keys="StudentProfileDB.user_id")
    activities = relationship("ActivityDB", back_populates="teacher", foreign_keys="ActivityDB.teacher_id")
    # FIX 3.1 Cortez7: Add back_populates for course_reports
    course_reports = relationship(
        "CourseReportDB",
        back_populates="teacher",
        foreign_keys="CourseReportDB.teacher_id"
    )
    # FIX 3.2 Cortez7: Add back_populates for remediation_plans
    remediation_plans_created = relationship(
        "RemediationPlanDB",
        back_populates="teacher",
        foreign_keys="RemediationPlanDB.teacher_id"
    )
    # FIX 3.3 Cortez7: Add back_populates for risk_alerts (assigned and acknowledged)
    assigned_alerts = relationship(
        "RiskAlertDB",
        back_populates="assigned_to_user",
        foreign_keys="RiskAlertDB.assigned_to"
    )
    acknowledged_alerts = relationship(
        "RiskAlertDB",
        back_populates="acknowledged_by_user",
        foreign_keys="RiskAlertDB.acknowledged_by"
    )

    # Composite indexes for common query patterns
    __table_args__ = (
        # Query: Login (email + active status)
        Index('idx_email_active', 'email', 'is_active'),
        # Query: Login by username
        Index('idx_username_active', 'username', 'is_active'),
        # FIX DB-3: Enable GIN index for roles in PostgreSQL
        # This enables fast queries like "get all users with role 'instructor'"
        # Works only in PostgreSQL; SQLite will ignore postgresql_using parameter
        Index('idx_roles_gin', 'roles', postgresql_using='gin'),
    )


# =============================================================================
# SPRINT 5 MODELS: Git N2 Traceability + Analytics
# =============================================================================


class GitTraceDB(Base, BaseModel):
    """
    Database model for Git N2-level traceability

    SPRINT 5 - HU-SYS-008: Integración Git
    Captura eventos Git (commits, branches, merges) asociados a sesiones de aprendizaje.

    FIX 10.11 Cortez10: IMPORTANT - This model has TWO timestamps:
    - `timestamp`: When the git commit was made (external timestamp from git)
    - `created_at`: When this DB record was created (inherited from BaseModel)
    These are semantically different and should not be confused.
    """

    __tablename__ = "git_traces"

    # Session relationship - FIX 3.4: Add ondelete="CASCADE"
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=False)

    # Git metadata
    event_type = Column(String(20), nullable=False)  # GitEventType: commit, branch_create, merge, etc.
    # FIX 1.4 Cortez4: Removed unique=True - same commit can appear in multiple sessions
    # Composite unique constraint added to __table_args__ instead
    commit_hash = Column(String(40), nullable=False, index=True)  # SHA-1 hash (40 chars)
    commit_message = Column(Text, nullable=False)
    author_name = Column(String(255), nullable=False)
    author_email = Column(String(255), nullable=False)
    # FIX 10.11 Cortez10: This is the GIT commit timestamp, NOT the DB record creation time
    # Use created_at (from BaseModel) for when this record was inserted
    timestamp = Column(DateTime, nullable=False)  # Git commit timestamp (when code was committed)
    branch_name = Column(String(255), nullable=False)
    parent_commits = Column(JSON, default=list)  # List of parent commit hashes

    # Code changes
    files_changed = Column(JSON, default=list)  # List of GitFileChange dicts
    total_lines_added = Column(Integer, default=0)
    total_lines_deleted = Column(Integer, default=0)
    diff = Column(Text, default="")  # Full diff output

    # Analysis
    # FIX 4.4 Cortez7: Added server_default for raw SQL compatibility
    is_merge = Column(Boolean, default=False, server_default='false')
    is_revert = Column(Boolean, default=False, server_default='false')
    detected_patterns = Column(JSON, default=list)  # List of CodePattern strings
    complexity_delta = Column(Integer, nullable=True)  # Change in cyclomatic complexity

    # Correlation with N3/N4 traces
    related_cognitive_traces = Column(JSON, default=list)  # List of trace IDs
    cognitive_state_during_commit = Column(String(50), nullable=True)  # From nearest N4 trace
    time_since_last_interaction_minutes = Column(Integer, nullable=True)

    # Repository metadata
    repo_path = Column(String(500), nullable=True)
    remote_url = Column(String(500), nullable=True)

    # Relationship - FIX DB-6: Add back_populates for bidirectional relationship
    session = relationship("SessionDB", back_populates="git_traces")

    # Composite indexes for common query patterns
    __table_args__ = (
        # Query: Get all git events for a session
        Index('idx_git_session_timestamp', 'session_id', 'timestamp'),
        # Query: Get commits by student ordered by time
        Index('idx_git_student_timestamp', 'student_id', 'timestamp'),
        # Query: Filter by event type and student
        Index('idx_git_student_event', 'student_id', 'event_type'),
        # Query: Get commits for student + activity
        Index('idx_git_student_activity', 'student_id', 'activity_id'),
        # FIX 1.4 Cortez4: Composite unique constraint allows same commit in multiple sessions
        UniqueConstraint('session_id', 'commit_hash', name='uq_git_trace_session_commit'),
        # FIX 2.14 Cortez6: Check constraint for valid event_type values
        CheckConstraint(
            "event_type IN ('commit', 'branch_create', 'branch_delete', 'merge', 'tag', 'revert', 'cherry_pick')",
            name='ck_git_event_type_valid'
        ),
    )


class CourseReportDB(Base, BaseModel):
    """
    Database model for Course-level aggregate reports

    SPRINT 5 - HU-DOC-009: Reportes Institucionales
    Almacena reportes generados por docentes para análisis de cohortes completas.
    """

    __tablename__ = "course_reports"

    # Report identification
    course_id = Column(String(100), nullable=False, index=True)  # e.g., "PROG2_2025_1C"
    # FIX 1.1 Cortez6: Added FK constraint to users table
    teacher_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    report_type = Column(String(50), nullable=False)  # "cohort_summary", "risk_dashboard", "competency_distribution"

    # Time period
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)

    # Aggregate data (JSON for flexibility)
    summary_stats = Column(JSON, nullable=False)
    # Structure:
    # {
    #   "total_students": 45,
    #   "total_sessions": 320,
    #   "total_interactions": 1842,
    #   "avg_ai_dependency": 0.42
    # }

    competency_distribution = Column(JSON, nullable=False)
    # Structure:
    # {
    #   "AVANZADO": 12,
    #   "INTERMEDIO": 25,
    #   "BASICO": 8
    # }

    risk_distribution = Column(JSON, nullable=False)
    # Structure:
    # {
    #   "CRITICAL": 3,
    #   "HIGH": 8,
    #   "MEDIUM": 15,
    #   "LOW": 7
    # }

    top_risks = Column(JSON, default=list)  # Top 5 riesgos más frecuentes

    # Student-level aggregates
    student_summaries = Column(JSON, default=list)
    # List of:
    # {
    #   "student_id": "...",
    #   "sessions": 7,
    #   "ai_dependency": 0.45,
    #   "competency": "INTERMEDIO",
    #   "risks": 2
    # }

    # Recommendations
    institutional_recommendations = Column(JSON, default=list)
    at_risk_students = Column(JSON, default=list)  # Students requiring intervention

    # Export metadata
    format = Column(String(20), default="json")  # json, pdf, xlsx
    file_path = Column(String(500), nullable=True)  # Path to exported file
    exported_at = Column(DateTime, nullable=True)

    # FIX 1.1 Cortez6: Added relationship to teacher
    # FIX 3.1 Cortez7: Added back_populates for bidirectional relationship
    teacher = relationship("UserDB", back_populates="course_reports", foreign_keys=[teacher_id])

    # Composite indexes
    __table_args__ = (
        # Query: Get reports by teacher ordered by period
        Index('idx_report_teacher_period', 'teacher_id', 'period_start'),
        # Query: Get course reports by type
        Index('idx_report_course_type', 'course_id', 'report_type'),
        # Query: Get recent reports
        Index('idx_report_created', 'created_at'),
        # FIX 5.2 Cortez6: Added composite index for teacher + course
        Index('idx_report_teacher_course', 'teacher_id', 'course_id'),
    )


class RemediationPlanDB(Base, BaseModel):
    """
    Database model for student remediation plans

    SPRINT 5 - HU-DOC-010: Gestión de Riesgos Institucionales
    Planes de remediación creados por docentes para estudiantes en riesgo.
    """

    __tablename__ = "remediation_plans"

    # Target student
    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=True)  # Nullable: plan puede ser general
    # FIX 1.2 Cortez6: Added FK constraint to users table
    teacher_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Trigger risks (que motivaron el plan)
    trigger_risks = Column(JSON, default=list)  # List of Risk IDs

    # Plan details
    plan_type = Column(String(50), nullable=False)  # "tutoring", "practice_exercises", "conceptual_review", "policy_clarification"
    description = Column(Text, nullable=False)  # Descripción del plan
    objectives = Column(JSON, default=list)  # Objetivos específicos

    # Actions
    recommended_actions = Column(JSON, default=list)
    # List of:
    # {
    #   "action_type": "tutoring_session",
    #   "description": "Sesión de tutoría sobre...",
    #   "deadline": "2025-12-15",
    #   "status": "pending"
    # }

    # Timeline
    start_date = Column(DateTime, nullable=False)
    target_completion_date = Column(DateTime, nullable=False)
    actual_completion_date = Column(DateTime, nullable=True)

    # Progress tracking
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    progress_notes = Column(Text, nullable=True)
    completion_evidence = Column(JSON, default=list)  # Links to completed actions

    # Outcomes
    outcome_evaluation = Column(Text, nullable=True)  # Evaluación final del docente
    success_metrics = Column(JSON, nullable=True)
    # {
    #   "ai_dependency_before": 0.75,
    #   "ai_dependency_after": 0.45,
    #   "risks_resolved": 3
    # }

    # FIX 1.5 Cortez5: Add back_populates relationship to RiskAlertDB
    risk_alerts = relationship(
        "RiskAlertDB",
        back_populates="remediation_plan",
        foreign_keys="RiskAlertDB.remediation_plan_id"
    )
    # FIX 1.2 Cortez6: Added relationship to teacher
    # FIX 3.2 Cortez7: Added back_populates for bidirectional relationship
    teacher = relationship("UserDB", back_populates="remediation_plans_created", foreign_keys=[teacher_id])

    # Composite indexes
    __table_args__ = (
        # Query: Get plans for student by status
        Index('idx_plan_student_status', 'student_id', 'status'),
        # Query: Get plans by teacher ordered by deadline
        Index('idx_plan_teacher_deadline', 'teacher_id', 'target_completion_date'),
        # Query: Get active plans
        Index('idx_plan_status_start', 'status', 'start_date'),
        # FIX 4.1 Cortez7: Index for actual_completion_date timestamp queries
        Index('idx_plan_completion_date', 'actual_completion_date'),
        # FIX 2.7 Cortez6: Check constraint for valid plan_type values
        CheckConstraint(
            "plan_type IN ('tutoring', 'practice_exercises', 'conceptual_review', 'policy_clarification')",
            name='ck_plan_type_valid'
        ),
        # FIX 2.8 Cortez6: Check constraint for valid status values
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'cancelled')",
            name='ck_remediation_status_valid'
        ),
    )


class RiskAlertDB(Base, BaseModel):
    """
    Database model for institutional risk alerts

    SPRINT 5 - HU-DOC-010: Gestión de Riesgos Institucionales
    Alertas automáticas generadas cuando se detectan patrones de riesgo institucionales.
    """

    __tablename__ = "risk_alerts"

    # Alert metadata
    alert_type = Column(String(50), nullable=False)  # "critical_risk_surge", "ai_dependency_spike", "academic_integrity", "pattern_anomaly"
    severity = Column(String(20), nullable=False)  # "low", "medium", "high", "critical"
    scope = Column(String(20), nullable=False)  # "student", "activity", "course", "institution"

    # Scope identifiers
    student_id = Column(String(100), nullable=True, index=True)
    activity_id = Column(String(100), nullable=True, index=True)
    course_id = Column(String(100), nullable=True, index=True)

    # Alert details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence = Column(JSON, default=list)  # Links to risks, sessions, traces

    # Detection
    detected_at = Column(DateTime, default=_utc_now, nullable=False)
    detection_rule = Column(String(100), nullable=False)  # e.g., "ai_dependency > 0.7 for 3+ sessions"
    threshold_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)

    # Assignment
    # FIX 1.3 Cortez6: Added FK constraint to users table
    assigned_to = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    assigned_at = Column(DateTime, nullable=True)

    # Resolution
    status = Column(String(20), default="open")  # open, acknowledged, investigating, resolved, false_positive
    acknowledged_at = Column(DateTime, nullable=True)
    # FIX 1.4 Cortez6: Added FK constraint to users table
    # FIX Cortez20: Added index=True for FK performance
    acknowledged_by = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    resolution_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    # FIX 3.3 Cortez3: Added ondelete="SET NULL" to maintain alerts when plan is deleted
    # FIX Cortez20: Added index=True for FK performance
    remediation_plan_id = Column(String(36), ForeignKey("remediation_plans.id", ondelete="SET NULL"), nullable=True, index=True)

    # FIX 1.5 Cortez5: Updated relationship with back_populates
    remediation_plan = relationship(
        "RemediationPlanDB",
        back_populates="risk_alerts",
        foreign_keys=[remediation_plan_id]
    )
    # FIX 1.3 Cortez6: Added relationship to assigned user
    # FIX 3.3 Cortez7: Added back_populates for bidirectional relationship
    assigned_to_user = relationship("UserDB", back_populates="assigned_alerts", foreign_keys=[assigned_to])
    # FIX 1.4 Cortez6: Added relationship to acknowledger
    # FIX 3.3 Cortez7: Added back_populates for bidirectional relationship
    acknowledged_by_user = relationship("UserDB", back_populates="acknowledged_alerts", foreign_keys=[acknowledged_by])

    # Composite indexes
    __table_args__ = (
        # Query: Get open alerts by severity
        Index('idx_alert_status_severity', 'status', 'severity'),
        # Query: Get alerts for student
        Index('idx_alert_student_status', 'student_id', 'status'),
        # Query: Get alerts by course ordered by detection time
        Index('idx_alert_course_detected', 'course_id', 'detected_at'),
        # Query: Get assigned alerts for a teacher
        Index('idx_alert_assigned_status', 'assigned_to', 'status'),
        # FIX 4.1 Cortez7: Index for resolved_at timestamp queries
        Index('idx_alert_resolved_at', 'resolved_at'),
        # FIX 2.9 Cortez6: Check constraint for valid alert_type values
        CheckConstraint(
            "alert_type IN ('critical_risk_surge', 'ai_dependency_spike', 'academic_integrity', 'pattern_anomaly')",
            name='ck_alert_type_valid'
        ),
        # FIX 2.10 Cortez6: Check constraint for valid severity values
        CheckConstraint(
            "severity IN ('low', 'medium', 'high', 'critical')",
            name='ck_alert_severity_valid'
        ),
        # FIX 2.11 Cortez6: Check constraint for valid scope values
        CheckConstraint(
            "scope IN ('student', 'activity', 'course', 'institution')",
            name='ck_alert_scope_valid'
        ),
        # FIX 2.12 Cortez6: Check constraint for valid status values
        CheckConstraint(
            "status IN ('open', 'acknowledged', 'investigating', 'resolved', 'false_positive')",
            name='ck_alert_status_valid'
        ),
    )


# ===============================================================================
# SPRINT 6 MODELS - Professional Simulators & Advanced Features
# ===============================================================================


class InterviewSessionDB(Base, BaseModel):
    """
    Interview sessions conducted by Technical Interviewer Agent (IT-IA)

    Stores interview questions, responses, and evaluation for HU-EST-011
    """

    __tablename__ = "interview_sessions"

    # FIX 3.2 Cortez3: Added ondelete="CASCADE" to prevent orphan records
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=True)

    # Interview type
    interview_type = Column(String(50), nullable=False)  # "CONCEPTUAL", "ALGORITHMIC", "DESIGN", "BEHAVIORAL"
    difficulty_level = Column(String(20), default="MEDIUM")  # "EASY", "MEDIUM", "HARD"

    # Questions and responses
    questions_asked = Column(JSON, default=list)
    # List of:
    # {
    #   "question": "Explain polymorphism",
    #   "type": "conceptual",
    #   "expected_key_points": ["dynamic binding", "inheritance", "abstraction"],
    #   "timestamp": "2025-11-21T10:30:00Z"
    # }

    responses = Column(JSON, default=list)
    # List of:
    # {
    #   "question_id": 0,
    #   "response": "Student's answer",
    #   "evaluation": {
    #     "clarity_score": 0.8,
    #     "technical_accuracy": 0.7,
    #     "thinking_aloud": true,
    #     "key_points_covered": ["dynamic binding", "inheritance"]
    #   },
    #   "timestamp": "2025-11-21T10:32:00Z"
    # }

    # Overall evaluation
    evaluation_score = Column(Float, nullable=True)  # 0.0 - 1.0
    evaluation_breakdown = Column(JSON, default=dict)
    # {
    #   "clarity": 0.8,
    #   "technical_accuracy": 0.7,
    #   "communication": 0.9,
    #   "problem_solving": 0.75
    # }

    feedback = Column(Text, nullable=True)  # Detailed feedback for student

    # Duration
    duration_minutes = Column(Integer, nullable=True)

    # Relationship
    session = relationship("SessionDB", back_populates="interview_sessions")

    # Composite indexes
    __table_args__ = (
        # Query: Get interviews for a student ordered by date
        Index('idx_interview_student_created', 'student_id', 'created_at'),
        # Query: Get interviews by type and difficulty
        Index('idx_interview_type_difficulty', 'interview_type', 'difficulty_level'),
        # FIX 2.1 Cortez6: Check constraint for valid interview_type values
        CheckConstraint(
            "interview_type IN ('CONCEPTUAL', 'ALGORITHMIC', 'DESIGN', 'BEHAVIORAL')",
            name='ck_interview_type_valid'
        ),
        # FIX 2.2 Cortez6: Check constraint for valid difficulty_level values
        CheckConstraint(
            "difficulty_level IN ('EASY', 'MEDIUM', 'HARD')",
            name='ck_interview_difficulty_valid'
        ),
        # FIX 2.15 Cortez6: Range constraint for evaluation_score
        CheckConstraint(
            "evaluation_score IS NULL OR (evaluation_score >= 0 AND evaluation_score <= 1)",
            name='ck_interview_score_range'
        ),
    )


class IncidentSimulationDB(Base, BaseModel):
    """
    Incident response simulations conducted by Incident Responder Agent (IR-IA)

    Stores incident scenarios, diagnosis process, and evaluation for HU-EST-012
    """

    __tablename__ = "incident_simulations"

    # FIX 3.2 Cortez3: Added ondelete="CASCADE" to prevent orphan records
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=True)

    # Incident type
    incident_type = Column(String(50), nullable=False)  # "API_ERROR", "PERFORMANCE", "SECURITY", "DATABASE", "DEPLOYMENT"
    severity = Column(String(20), default="HIGH")  # "LOW", "MEDIUM", "HIGH", "CRITICAL"

    # Incident description
    incident_description = Column(Text, nullable=False)
    # e.g., "API is returning 500 in 30% of requests. Users reporting timeouts."

    simulated_logs = Column(Text, nullable=True)  # Simulated error logs
    simulated_metrics = Column(JSON, default=dict)  # Simulated monitoring metrics

    # Diagnosis process (captured as trace)
    diagnosis_process = Column(JSON, default=list)
    # List of:
    # {
    #   "step": 1,
    #   "action": "Checked application logs",
    #   "finding": "Found NullPointerException in UserService",
    #   "timestamp": "2025-11-21T11:00:00Z"
    # }

    # Solution proposed
    solution_proposed = Column(Text, nullable=True)
    root_cause_identified = Column(Text, nullable=True)

    # Timing
    time_to_diagnose_minutes = Column(Integer, nullable=True)
    time_to_resolve_minutes = Column(Integer, nullable=True)

    # Post-mortem documentation
    post_mortem = Column(Text, nullable=True)
    # Structured post-mortem with sections:
    # - What happened
    # - Root cause
    # - Resolution
    # - Prevention measures

    # Evaluation
    evaluation = Column(JSON, default=dict)
    # {
    #   "diagnosis_systematic": 0.8,  # Did they follow a systematic approach?
    #   "prioritization": 0.7,  # Did they prioritize correctly?
    #   "documentation": 0.9,  # Quality of post-mortem
    #   "communication": 0.85  # How well they communicated the incident
    # }

    # Relationship
    session = relationship("SessionDB", back_populates="incident_simulations")

    # Composite indexes
    __table_args__ = (
        # Query: Get incidents for a student ordered by date
        Index('idx_incident_student_created', 'student_id', 'created_at'),
        # Query: Get incidents by type and severity
        Index('idx_incident_type_severity', 'incident_type', 'severity'),
        # FIX 2.3 Cortez6: Check constraint for valid incident_type values
        CheckConstraint(
            "incident_type IN ('API_ERROR', 'PERFORMANCE', 'SECURITY', 'DATABASE', 'DEPLOYMENT')",
            name='ck_incident_type_valid'
        ),
        # FIX 2.4 Cortez6: Check constraint for valid severity values
        CheckConstraint(
            "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name='ck_incident_severity_valid'
        ),
    )


class LTIDeploymentDB(Base, BaseModel):
    """
    LTI 1.3 platform deployments (Moodle, Canvas, etc.)

    Stores LTI configuration for external platforms for HU-SYS-010
    """

    __tablename__ = "lti_deployments"

    # Platform information
    platform_name = Column(String(100), nullable=False)  # "Moodle", "Canvas", "Blackboard"
    issuer = Column(String(255), nullable=False)  # LTI issuer URL
    client_id = Column(String(255), nullable=False)  # OAuth2 client ID
    deployment_id = Column(String(255), nullable=False)  # LTI deployment ID

    # OIDC endpoints
    auth_login_url = Column(Text, nullable=False)  # OIDC auth login URL
    auth_token_url = Column(Text, nullable=False)  # OAuth2 token URL
    public_keyset_url = Column(Text, nullable=False)  # JWKS URL (for token validation)

    # Optional: Access token URL for LTI Advantage services
    access_token_url = Column(Text, nullable=True)

    # Status
    # FIX 4.4 Cortez7: Added server_default for raw SQL compatibility
    is_active = Column(Boolean, default=True, server_default='true', nullable=False)

    # Relationships
    lti_sessions = relationship("LTISessionDB", back_populates="deployment", cascade="all, delete-orphan")

    # Composite indexes
    __table_args__ = (
        # Unique constraint: One deployment per issuer + deployment_id
        Index('idx_lti_deployment_unique', 'issuer', 'deployment_id', unique=True),
        # Query: Get active deployments
        Index('idx_lti_deployment_active', 'is_active'),
    )


class SimulatorEventDB(Base, BaseModel):
    """
    Simulator Events - Captura eventos generados por simuladores
    
    Tipos de eventos:
    - backlog_created: Product Owner creó backlog
    - sprint_planning_complete: Scrum Master completó planning
    - sprint_planning_failed: Fallo en planificación
    - user_story_approved: Historia de usuario aprobada
    - technical_decision_made: Decisión técnica tomada
    - risk_identified_by_user: Usuario identificó un riesgo
    - test_executed: Test ejecutado
    - deployment_completed: Deployment completado
    - incident_resolved: Incidente resuelto
    - security_scan_complete: Scan de seguridad completado
    """

    __tablename__ = "simulator_events"

    # Event metadata
    # FIX 3.2 Cortez3: Added ondelete="CASCADE" to prevent orphan records
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    simulator_type = Column(String(50), nullable=False, index=True)  # PO, SM, TI, IR, Client, DSO
    
    # Event details
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSON, default=dict)  # Datos específicos del evento
    timestamp = Column(DateTime, default=_utc_now, nullable=False)
    
    # Context
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=True)  # info, warning, critical
    
    # Relationships
    session = relationship("SessionDB", back_populates="simulator_events")

    # Composite indexes
    __table_args__ = (
        # Query: Get all events for a session
        Index('idx_event_session', 'session_id', 'timestamp'),
        # Query: Get events by type for analysis
        Index('idx_event_type_student', 'event_type', 'student_id'),
        # Query: Get events by simulator
        Index('idx_event_simulator_session', 'simulator_type', 'session_id'),
        # FIX 2.13 Cortez6: Check constraint for valid simulator_type values
        # FIX Cortez21 DEFECTO 9.2: Added V2 simulators (senior_dev, qa_engineer, security_auditor, tech_lead, demanding_client)
        CheckConstraint(
            "simulator_type IN ('product_owner', 'scrum_master', 'tech_interviewer', 'incident_responder', 'client', 'devsecops', 'senior_dev', 'qa_engineer', 'security_auditor', 'tech_lead', 'demanding_client')",
            name='ck_simulator_event_type_valid'
        ),
    )


class LTISessionDB(Base, BaseModel):
    """
    LTI launch sessions (student launches from Moodle)

    Maps LTI users to AI-Native sessions for HU-SYS-010
    """

    __tablename__ = "lti_sessions"

    # LTI deployment
    # FIX 1.6 Cortez6: Added ondelete="CASCADE" to deployment FK
    deployment_id = Column(String(36), ForeignKey("lti_deployments.id", ondelete="CASCADE"), nullable=False, index=True)

    # LTI user information
    lti_user_id = Column(String(255), nullable=False, index=True)  # User ID from Moodle
    lti_user_name = Column(String(255), nullable=True)
    lti_user_email = Column(String(255), nullable=True)

    # LTI context (course)
    lti_context_id = Column(String(255), nullable=True)  # Course ID from Moodle
    lti_context_label = Column(String(100), nullable=True)  # Course code
    lti_context_title = Column(String(255), nullable=True)  # Course name

    # LTI resource link (activity within course)
    resource_link_id = Column(String(255), nullable=False, index=True)

    # Mapped to AI-Native session
    # DB-7 NOTE: session_id is intentionally nullable. An LTI launch from Moodle
    # creates an LTISessionDB first, before an AI-Native SessionDB is created.
    # The cascade="all, delete-orphan" on SessionDB.lti_sessions ensures cleanup
    # when the parent Session is deleted (correct parent->child direction).
    # FIX 1.7 Cortez6: Added ondelete="SET NULL" to session FK
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True, index=True)

    # Launch metadata
    launch_token = Column(Text, nullable=True)  # JWT token from LTI launch (for AGS)
    locale = Column(String(10), nullable=True)  # User's locale (e.g., "es_AR")

    # Relationships
    deployment = relationship("LTIDeploymentDB", back_populates="lti_sessions")
    session = relationship("SessionDB", back_populates="lti_sessions")

    # Composite indexes
    __table_args__ = (
        # Query: Get LTI sessions for a user
        Index('idx_lti_session_user', 'lti_user_id'),
        # Query: Get LTI sessions for a resource
        Index('idx_lti_session_resource', 'resource_link_id'),
        # Query: Get LTI session by AI-Native session
        Index('idx_lti_session_native', 'session_id'),
    )


# =============================================================================
# EJERCICIOS Y TRAINING DIGITAL (Migración JSON → PostgreSQL)
# =============================================================================

class SubjectDB(Base):
    """
    Database model for subjects/materias (Python, Java, etc.)

    Agrupa ejercicios por lenguaje de programación y materia.
    Migración desde JSON a PostgreSQL para centralizar datos.

    NOTE: No inherits from BaseModel because we use 'code' as PK instead of UUID 'id'
    """

    __tablename__ = "subjects"

    # Subject identification (using 'code' as PK)
    code = Column(String(50), primary_key=True)  # 'PYTHON', 'JAVA', 'PROG1'
    name = Column(String(100), nullable=False)  # 'Python', 'Java', 'Programación 1'
    description = Column(Text, nullable=True)
    language = Column(String(20), nullable=False)  # 'python', 'java'

    # Metadata
    total_units = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, nullable=False)

    # Timestamps (manual since not using BaseModel)
    created_at = Column(DateTime, default=_utc_now, nullable=False)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now, nullable=False)

    # Relationships
    exercises = relationship("ExerciseDB", back_populates="subject", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_subjects_language', 'language'),
        Index('idx_subjects_active', 'is_active'),
        CheckConstraint("language IN ('python', 'java')", name='check_subject_language'),
    )


class ExerciseDB(Base, BaseModel):
    """
    Database model for programming exercises

    Ejercicios de programación con consigna, código inicial, tests y pistas.
    Migración desde backend/data/exercises/*.json y backend/data/training/*.json
    """

    __tablename__ = "exercises"

    # References
    subject_code = Column(String(50), ForeignKey("subjects.code", ondelete="CASCADE"), nullable=False, index=True)

    # Basic metadata
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(20), nullable=False)  # 'Easy', 'Medium', 'Hard'
    time_min = Column(Integer, nullable=False)  # Tiempo estimado en minutos
    unit = Column(Integer, nullable=True)  # 1-7 (null for legacy exercises)
    language = Column(String(20), nullable=False)  # 'python', 'java'

    # Pedagogical content
    mission_markdown = Column(Text, nullable=False)  # Consigna completa
    story_markdown = Column(Text, nullable=True)  # Contexto/historia del ejercicio
    constraints = Column(JSON, default=list)  # Restricciones/requisitos como array

    # Code
    starter_code = Column(Text, nullable=False)  # Código inicial con TODOs
    solution_code = Column(Text, nullable=True)  # Solución de referencia (NO enviar a frontend)

    # Pedagogical metadata
    tags = Column(JSONBCompatible, default=list)  # ['Variables', 'Condicionales']
    learning_objectives = Column(JSONBCompatible, default=list)  # Objetivos de aprendizaje
    cognitive_level = Column(String(20), nullable=True)  # 'Recordar', 'Comprender', 'Aplicar', etc.

    # Scoring (FASE 1.5)
    max_score = Column(Integer, default=100, nullable=False)  # Puntaje máximo del ejercicio

    # Versioning and state
    version = Column(Integer, default=1, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete

    # Relationships
    subject = relationship("SubjectDB", back_populates="exercises")
    hints = relationship("ExerciseHintDB", back_populates="exercise", cascade="all, delete-orphan", order_by="ExerciseHintDB.hint_number")
    tests = relationship("ExerciseTestDB", back_populates="exercise", cascade="all, delete-orphan", order_by="ExerciseTestDB.test_number")
    attempts = relationship("ExerciseAttemptDB", back_populates="exercise", cascade="all, delete-orphan")
    rubric_criteria = relationship("ExerciseRubricCriterionDB", back_populates="exercise", cascade="all, delete-orphan", order_by="ExerciseRubricCriterionDB.display_order")

    # Indexes
    __table_args__ = (
        Index('idx_exercises_subject', 'subject_code'),
        Index('idx_exercises_unit', 'unit'),
        Index('idx_exercises_difficulty', 'difficulty'),
        Index('idx_exercises_language', 'language'),
        Index('idx_exercises_active', 'is_active'),
        Index('idx_exercises_tags', 'tags', postgresql_using='gin'),  # GIN index for JSONB
        CheckConstraint("difficulty IN ('Easy', 'Medium', 'Hard')", name='check_exercise_difficulty'),
        CheckConstraint("language IN ('python', 'java')", name='check_exercise_language'),
        CheckConstraint("time_min > 0", name='check_exercise_time_positive'),
    )


class ExerciseHintDB(Base, BaseModel):
    """
    Database model for exercise hints (pistas graduadas)

    Pistas con penalización creciente que se revelan una a una.
    """

    __tablename__ = "exercise_hints"

    # Reference to exercise
    exercise_id = Column(String(50), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True)

    # Hint content
    hint_number = Column(Integer, nullable=False)  # 1, 2, 3, 4 (orden de revelación)
    title = Column(String(200), nullable=True)  # "Estructura básica de validación"
    content = Column(Text, nullable=False)  # Contenido de la pista

    # Penalty
    penalty_points = Column(Integer, default=0, nullable=False)  # 5, 10, 15, 20

    # Relationship
    exercise = relationship("ExerciseDB", back_populates="hints")

    # Indexes and constraints
    __table_args__ = (
        Index('idx_hints_exercise', 'exercise_id'),
        Index('idx_hints_order', 'exercise_id', 'hint_number'),
        UniqueConstraint('exercise_id', 'hint_number', name='uq_exercise_hint_number'),
        CheckConstraint("hint_number > 0", name='check_hint_number_positive'),
        CheckConstraint("penalty_points >= 0", name='check_penalty_nonnegative'),
    )


class ExerciseTestDB(Base, BaseModel):
    """
    Database model for exercise unit tests

    Tests que el código del estudiante debe pasar.
    Pueden ser visibles (feedback durante desarrollo) u ocultos (evaluación final).
    """

    __tablename__ = "exercise_tests"

    # Reference to exercise
    exercise_id = Column(String(50), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True)

    # Test identification
    test_number = Column(Integer, nullable=False)  # Orden: 1, 2, 3...
    description = Column(Text, nullable=True)  # "Validación de límites exactos"

    # Test data
    input = Column(Text, nullable=False)  # "validar_nota(85)"
    expected = Column(Text, nullable=False)  # "True" o "85.0"

    # Configuration
    is_hidden = Column(Boolean, default=False, nullable=False)  # TRUE = no visible al estudiante
    timeout_seconds = Column(Integer, default=5, nullable=False)

    # Relationship
    exercise = relationship("ExerciseDB", back_populates="tests")

    # Indexes and constraints
    __table_args__ = (
        Index('idx_tests_exercise', 'exercise_id'),
        Index('idx_tests_hidden', 'exercise_id', 'is_hidden'),
        Index('idx_tests_order', 'exercise_id', 'test_number'),
        UniqueConstraint('exercise_id', 'test_number', name='uq_exercise_test_number'),
        CheckConstraint("test_number > 0", name='check_test_number_positive'),
        CheckConstraint("timeout_seconds > 0", name='check_timeout_positive'),
    )


class ExerciseAttemptDB(Base, BaseModel):
    """
    Database model for student exercise attempts

    Intentos de resolución de ejercicios por parte de estudiantes.
    Permite tracking completo, analytics y trazabilidad N4.
    """

    __tablename__ = "exercise_attempts"

    # References
    exercise_id = Column(String(50), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True, index=True)

    # Submitted code
    submitted_code = Column(Text, nullable=False)

    # Execution results
    tests_passed = Column(Integer, default=0, nullable=False)
    tests_total = Column(Integer, default=0, nullable=False)
    score = Column(Float, nullable=True)  # 0-10 scale
    status = Column(String(20), nullable=False)  # 'PASS', 'FAIL', 'ERROR', 'TIMEOUT'

    # Execution details
    execution_time_ms = Column(Integer, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)

    # AI feedback (from CodeEvaluator)
    ai_feedback_summary = Column(Text, nullable=True)  # Resumen corto para toast
    ai_feedback_detailed = Column(Text, nullable=True)  # Markdown completo
    ai_suggestions = Column(JSONBCompatible, default=list)  # Array de sugerencias

    # Rubric evaluation (FASE 1.5)
    rubric_evaluation = Column(JSONBCompatible, default=dict, nullable=True)
    # Formato: {
    #   "criteria": [
    #     {
    #       "criterion_name": "Funcionalidad",
    #       "level_achieved": "Bueno",
    #       "score": 8.0,
    #       "points": 80,
    #       "feedback": "Implementa la mayoría de casos correctamente..."
    #     }
    #   ],
    #   "total_score_rubric": 85.0,  # Antes de penalizaciones
    #   "penalty_from_hints": 15,
    #   "final_score": 70.0  # total_score_rubric - penalty
    # }

    # Hints usage
    hints_used = Column(Integer, default=0, nullable=False)
    penalty_applied = Column(Integer, default=0, nullable=False)  # Penalización total

    # Attempt metadata
    attempt_number = Column(Integer, default=1, nullable=False)  # 1er, 2do, 3er intento
    submitted_at = Column(DateTime, default=_utc_now, nullable=False)

    # Relationships
    exercise = relationship("ExerciseDB", back_populates="attempts")
    session = relationship("SessionDB")

    # Indexes for analytics
    __table_args__ = (
        Index('idx_attempts_exercise', 'exercise_id'),
        Index('idx_attempts_student', 'student_id'),
        Index('idx_attempts_session', 'session_id'),
        Index('idx_attempts_status', 'status'),
        Index('idx_attempts_submitted', 'submitted_at'),
        # Composite index for student progress queries
        Index('idx_attempts_student_exercise', 'student_id', 'exercise_id', 'submitted_at'),
        CheckConstraint("status IN ('PASS', 'FAIL', 'ERROR', 'TIMEOUT')", name='check_attempt_status'),
        CheckConstraint("score IS NULL OR (score >= 0 AND score <= 10)", name='check_score_range'),
        CheckConstraint("tests_passed >= 0 AND tests_passed <= tests_total", name='check_tests_valid'),
        CheckConstraint("hints_used >= 0", name='check_hints_nonnegative'),
        CheckConstraint("attempt_number > 0", name='check_attempt_number_positive'),
    )


class ExerciseRubricCriterionDB(Base, BaseModel):
    """
    Database model for exercise rubric criteria (FASE 1.5)

    Criterios de evaluación de un ejercicio con sus niveles de logro.
    Cada ejercicio tiene múltiples criterios (Funcionalidad, Calidad, Robustez)
    y cada criterio tiene 4 niveles (Excelente, Bueno, Regular, Insuficiente).

    Ejemplos de criterios:
    - Funcionalidad (40%): ¿Resuelve el problema correctamente?
    - Calidad de código (30%): ¿Es legible, mantiene buenas prácticas?
    - Robustez (30%): ¿Maneja casos edge, errores?
    """

    __tablename__ = "exercise_rubric_criteria"

    # Reference to exercise
    exercise_id = Column(String(50), ForeignKey("exercises.id", ondelete="CASCADE"), nullable=False, index=True)

    # Criterion metadata
    criterion_name = Column(String(100), nullable=False)  # "Funcionalidad", "Calidad de código", etc.
    description = Column(Text, nullable=True)  # Descripción detallada del criterio
    weight = Column(Float, nullable=False)  # 0.0-1.0 (ej: 0.4 = 40%)
    display_order = Column(Integer, nullable=False)  # Orden de presentación (1, 2, 3...)

    # Relationships
    exercise = relationship("ExerciseDB", back_populates="rubric_criteria")
    levels = relationship("RubricLevelDB", back_populates="criterion", cascade="all, delete-orphan", order_by="RubricLevelDB.min_score.desc()")

    # Indexes and constraints
    __table_args__ = (
        Index('idx_rubric_criteria_exercise', 'exercise_id'),
        Index('idx_rubric_criteria_order', 'exercise_id', 'display_order'),
        UniqueConstraint('exercise_id', 'criterion_name', name='uq_exercise_criterion_name'),
        UniqueConstraint('exercise_id', 'display_order', name='uq_exercise_criterion_order'),
        CheckConstraint("weight >= 0 AND weight <= 1", name='check_criterion_weight_range'),
        CheckConstraint("display_order > 0", name='check_criterion_order_positive'),
    )


class RubricLevelDB(Base, BaseModel):
    """
    Database model for rubric criterion levels (FASE 1.5)

    Niveles de logro para un criterio de rúbrica.
    Cada criterio tiene 4 niveles estándar:
    - Excelente (9.0-10.0): Cumplimiento excepcional
    - Bueno (7.0-8.9): Cumplimiento satisfactorio
    - Regular (5.0-6.9): Cumplimiento básico
    - Insuficiente (0.0-4.9): No cumple o cumple parcialmente

    Ejemplo para criterio "Funcionalidad":
    - Excelente: "Implementa todos los casos correctamente, incluidos edge cases"
    - Bueno: "Implementa la mayoría de casos, falta algunos edge cases"
    - Regular: "Implementa casos básicos, falla en casos intermedios"
    - Insuficiente: "No implementa correctamente o no funciona"
    """

    __tablename__ = "rubric_levels"

    # Reference to criterion
    criterion_id = Column(String(36), ForeignKey("exercise_rubric_criteria.id", ondelete="CASCADE"), nullable=False, index=True)

    # Level metadata
    level_name = Column(String(50), nullable=False)  # "Excelente", "Bueno", "Regular", "Insuficiente"
    description = Column(Text, nullable=False)  # Qué debe cumplir para alcanzar este nivel
    min_score = Column(Float, nullable=False)  # 9.0, 7.0, 5.0, 0.0
    max_score = Column(Float, nullable=False)  # 10.0, 8.9, 6.9, 4.9
    points = Column(Integer, nullable=False)  # Puntos otorgados si alcanza este nivel (0-100)

    # Relationship
    criterion = relationship("ExerciseRubricCriterionDB", back_populates="levels")

    # Indexes and constraints
    __table_args__ = (
        Index('idx_rubric_levels_criterion', 'criterion_id'),
        Index('idx_rubric_levels_score_range', 'criterion_id', 'min_score', 'max_score'),
        CheckConstraint("min_score >= 0 AND max_score <= 10", name='check_level_score_range'),
        CheckConstraint("min_score < max_score", name='check_level_score_order'),
        CheckConstraint("level_name IN ('Excelente', 'Bueno', 'Regular', 'Insuficiente')", name='check_level_name_valid'),
        CheckConstraint("points >= 0 AND points <= 100", name='check_level_points_range'),
    )
