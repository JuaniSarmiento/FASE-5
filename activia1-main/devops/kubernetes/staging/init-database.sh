#!/bin/bash

# AI-Native MVP - Database Initialization Script for Staging
# Author: Mag. Alberto Cortez
# Date: 2025-11-24

set -e

echo "=========================================="
echo "Database Initialization - Staging"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

NAMESPACE="ai-native-staging"
POSTGRES_POD="postgresql-0"
DB_NAME="ai_native"
DB_USER="ai_native"

# Check prerequisites
echo "Step 1: Checking prerequisites..."
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}ERROR: kubectl is not installed${NC}"; exit 1; }
echo -e "${GREEN}✓ kubectl is installed${NC}"
echo ""

# Check if PostgreSQL pod is ready
echo "Step 2: Verifying PostgreSQL pod..."
if ! kubectl get pod $POSTGRES_POD -n $NAMESPACE >/dev/null 2>&1; then
    echo -e "${RED}ERROR: PostgreSQL pod not found${NC}"
    echo "Make sure you've deployed PostgreSQL first:"
    echo "  kubectl apply -f 04-postgresql.yaml"
    exit 1
fi

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
kubectl wait --for=condition=ready pod/$POSTGRES_POD -n $NAMESPACE --timeout=120s || {
    echo -e "${RED}ERROR: PostgreSQL pod not ready${NC}"
    kubectl describe pod $POSTGRES_POD -n $NAMESPACE
    exit 1
}
echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
echo ""

# Create initialization SQL script
echo "Step 3: Preparing database schema..."
cat > /tmp/init_schema.sql <<'EOF'
-- AI-Native MVP - Database Schema
-- Generated: 2025-11-24

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables (matching ORM models)

-- Base Model (inherited by all tables)
-- Fields: id (UUID), created_at, updated_at

-- 1. Sessions
CREATE TABLE IF NOT EXISTS sessions (
    id VARCHAR(255) PRIMARY KEY,
    student_id VARCHAR(255) NOT NULL,
    activity_id VARCHAR(255) NOT NULL,
    mode VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_student ON sessions(student_id);
CREATE INDEX IF NOT EXISTS idx_sessions_activity ON sessions(activity_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_student_activity ON sessions(student_id, activity_id);

-- 2. Activities
CREATE TABLE IF NOT EXISTS activities (
    id VARCHAR(255) PRIMARY KEY,
    activity_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    instructions TEXT,
    subject VARCHAR(255),
    difficulty VARCHAR(50),
    estimated_duration_minutes INTEGER,
    teacher_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'draft',
    pedagogical_policies JSONB,
    evaluation_criteria JSONB,
    tags JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_activity_teacher_status ON activities(teacher_id, status);
CREATE INDEX IF NOT EXISTS idx_activity_status_created ON activities(status, created_at);
CREATE INDEX IF NOT EXISTS idx_activity_subject_status ON activities(subject, status);

-- 3. Cognitive Traces
CREATE TABLE IF NOT EXISTS cognitive_traces (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    student_id VARCHAR(255) NOT NULL,
    activity_id VARCHAR(255) NOT NULL,
    trace_level VARCHAR(50) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,
    cognitive_state VARCHAR(100),
    cognitive_intent VARCHAR(100),
    content TEXT,
    ai_involvement FLOAT,
    response_content TEXT,
    trace_metadata JSONB,
    blocked BOOLEAN DEFAULT FALSE,
    block_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_traces_session ON cognitive_traces(session_id);
CREATE INDEX IF NOT EXISTS idx_traces_student ON cognitive_traces(student_id);
CREATE INDEX IF NOT EXISTS idx_traces_activity ON cognitive_traces(activity_id);
CREATE INDEX IF NOT EXISTS idx_session_type ON cognitive_traces(session_id, interaction_type);

-- 4. Risks
CREATE TABLE IF NOT EXISTS risks (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255),
    student_id VARCHAR(255) NOT NULL,
    activity_id VARCHAR(255),
    risk_type VARCHAR(100) NOT NULL,
    risk_level VARCHAR(50) NOT NULL,
    dimension VARCHAR(50) NOT NULL,
    description TEXT,
    evidence JSONB,
    trace_ids JSONB,
    recommendations JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_risks_session ON risks(session_id);
CREATE INDEX IF NOT EXISTS idx_risks_student ON risks(student_id);
CREATE INDEX IF NOT EXISTS idx_risks_resolved ON risks(resolved);
CREATE INDEX IF NOT EXISTS idx_student_resolved ON risks(student_id, resolved);

-- 5. Evaluations
CREATE TABLE IF NOT EXISTS evaluations (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    student_id VARCHAR(255) NOT NULL,
    activity_id VARCHAR(255) NOT NULL,
    overall_competency_level VARCHAR(50),
    overall_score FLOAT,
    dimensions JSONB,
    key_strengths JSONB,
    improvement_areas JSONB,
    recommendations JSONB,
    reasoning_analysis TEXT,
    git_analysis TEXT,
    ai_dependency_metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_evaluations_session ON evaluations(session_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_student ON evaluations(student_id);
CREATE INDEX IF NOT EXISTS idx_student_activity_eval ON evaluations(student_id, activity_id);

-- 6. Trace Sequences
CREATE TABLE IF NOT EXISTS trace_sequences (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    trace_ids JSONB NOT NULL,
    reasoning_path TEXT,
    strategy_changes JSONB,
    ai_dependency_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_sequences_session ON trace_sequences(session_id);

-- 7. Student Profiles
CREATE TABLE IF NOT EXISTS student_profiles (
    id VARCHAR(255) PRIMARY KEY,
    student_id VARCHAR(255) UNIQUE NOT NULL,
    total_sessions INTEGER DEFAULT 0,
    average_ai_dependency FLOAT DEFAULT 0.0,
    total_risks INTEGER DEFAULT 0,
    critical_risks INTEGER DEFAULT 0,
    risk_trends JSONB,
    competency_evolution JSONB,
    last_activity_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_profiles_student ON student_profiles(student_id);

-- 8. Interview Sessions (Sprint 6 - IT-IA)
CREATE TABLE IF NOT EXISTS interview_sessions (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    student_id VARCHAR(255) NOT NULL,
    interview_type VARCHAR(50) NOT NULL,
    difficulty_level VARCHAR(50) NOT NULL,
    questions_asked JSONB,
    responses JSONB,
    evaluation_score FLOAT,
    evaluation_breakdown JSONB,
    status VARCHAR(50) DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_interview_session ON interview_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_interview_student ON interview_sessions(student_id);

-- 9. Incident Simulations (Sprint 6 - IR-IA)
CREATE TABLE IF NOT EXISTS incident_simulations (
    id VARCHAR(255) PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    student_id VARCHAR(255) NOT NULL,
    incident_type VARCHAR(50) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    metrics JSONB,
    diagnosis_steps JSONB,
    resolution TEXT,
    resolution_score FLOAT,
    resolution_time_minutes INTEGER,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_incident_session ON incident_simulations(session_id);
CREATE INDEX IF NOT EXISTS idx_incident_student ON incident_simulations(student_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE format('DROP TRIGGER IF EXISTS update_%I_updated_at ON %I', t, t);
        EXECUTE format('CREATE TRIGGER update_%I_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()', t, t);
    END LOOP;
END;
$$ language 'plpgsql';

-- Verify schema
SELECT 'Schema created successfully!' AS status;
EOF

echo -e "${GREEN}✓ Schema prepared${NC}"
echo ""

# Execute schema creation
echo "Step 4: Creating database schema..."
kubectl exec -i $POSTGRES_POD -n $NAMESPACE -- psql -U $DB_USER -d $DB_NAME < /tmp/init_schema.sql

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Schema created successfully${NC}"
else
    echo -e "${RED}✗ Schema creation failed${NC}"
    exit 1
fi
echo ""

# Verify tables
echo "Step 5: Verifying tables..."
kubectl exec -i $POSTGRES_POD -n $NAMESPACE -- psql -U $DB_USER -d $DB_NAME -c "\dt" | grep -E "sessions|activities|cognitive_traces|risks|evaluations"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Tables verified${NC}"
else
    echo -e "${YELLOW}⚠ Could not verify tables${NC}"
fi
echo ""

# Create sample data (optional)
read -p "Do you want to create sample data? (y/N): " CREATE_SAMPLE
if [[ $CREATE_SAMPLE =~ ^[Yy]$ ]]; then
    echo "Step 6: Creating sample data..."

    cat > /tmp/sample_data.sql <<'EOF'
-- Sample activity
INSERT INTO activities (id, activity_id, title, description, subject, difficulty, status, teacher_id, created_at)
VALUES (
    'act_001',
    'prog2_tp1_colas',
    'Trabajo Práctico 1: Colas Circulares',
    'Implementar una cola circular en C con operaciones básicas',
    'Programación II',
    'INTERMEDIO',
    'active',
    'teacher_001',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

-- Sample session
INSERT INTO sessions (id, student_id, activity_id, mode, start_time, status, created_at)
VALUES (
    'session_sample_001',
    'student_demo',
    'prog2_tp1_colas',
    'TUTOR',
    CURRENT_TIMESTAMP,
    'active',
    CURRENT_TIMESTAMP
) ON CONFLICT DO NOTHING;

SELECT 'Sample data created!' AS status;
EOF

    kubectl exec -i $POSTGRES_POD -n $NAMESPACE -- psql -U $DB_USER -d $DB_NAME < /tmp/sample_data.sql
    echo -e "${GREEN}✓ Sample data created${NC}"
    echo ""
fi

# Cleanup
rm -f /tmp/init_schema.sql /tmp/sample_data.sql

# Summary
echo "=========================================="
echo "Database Initialization Complete!"
echo "=========================================="
echo ""
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo ""
echo "Tables created:"
echo "  - sessions"
echo "  - activities"
echo "  - cognitive_traces"
echo "  - risks"
echo "  - evaluations"
echo "  - trace_sequences"
echo "  - student_profiles"
echo "  - interview_sessions (Sprint 6)"
echo "  - incident_simulations (Sprint 6)"
echo ""
echo "Next steps:"
echo "  1. Deploy backend: kubectl apply -f 06-backend.yaml"
echo "  2. Verify backend logs: kubectl logs -f -l app=ai-native-backend -n $NAMESPACE"
echo "  3. Test API: curl http://\$INGRESS_IP/api/v1/health"
echo ""