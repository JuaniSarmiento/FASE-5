-- Script SQL para crear índices compuestos en la base de datos existente
-- Ejecutar con: sqlite3 ai_native_mvp.db < create_indexes.sql

-- Nota: IF NOT EXISTS evita errores si ya existen

-- =============================================================================
-- Índices para SessionDB
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_student_activity ON sessions (student_id, activity_id);
CREATE INDEX IF NOT EXISTS idx_status_created ON sessions (status, created_at);
CREATE INDEX IF NOT EXISTS idx_student_status ON sessions (student_id, status);

-- =============================================================================
-- Índices para CognitiveTraceDB
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_session_type ON cognitive_traces (session_id, interaction_type);
CREATE INDEX IF NOT EXISTS idx_student_created ON cognitive_traces (student_id, created_at);
CREATE INDEX IF NOT EXISTS idx_student_activity_state ON cognitive_traces (student_id, activity_id, cognitive_state);
CREATE INDEX IF NOT EXISTS idx_session_level ON cognitive_traces (session_id, trace_level);

-- =============================================================================
-- Índices para RiskDB
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_student_resolved ON risks (student_id, resolved);
CREATE INDEX IF NOT EXISTS idx_level_created ON risks (risk_level, created_at);
CREATE INDEX IF NOT EXISTS idx_student_activity_dimension ON risks (student_id, activity_id, dimension);
CREATE INDEX IF NOT EXISTS idx_session_type_risks ON risks (session_id, risk_type);

-- =============================================================================
-- Índices para EvaluationDB
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_student_activity_eval ON evaluations (student_id, activity_id);
CREATE INDEX IF NOT EXISTS idx_competency_score ON evaluations (overall_competency_level, overall_score);
CREATE INDEX IF NOT EXISTS idx_student_created_eval ON evaluations (student_id, created_at);

-- =============================================================================
-- Índices para TraceSequenceDB
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_student_activity_seq ON trace_sequences (student_id, activity_id);
CREATE INDEX IF NOT EXISTS idx_student_start ON trace_sequences (student_id, start_time);