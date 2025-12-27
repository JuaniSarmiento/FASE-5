# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-Native MVP for teaching-learning programming with generative AI. Doctoral thesis project implementing **process-based evaluation** (not product-based) with N4-level cognitive traceability.

**Tech Stack**: Python 3.11+/FastAPI backend, React 18+/TypeScript/Vite frontend, PostgreSQL, Redis, Ollama/Phi-3 for LLM.

**Key Concept**: The system evaluates HOW students solve problems (cognitive process), not just the final code output. This is achieved through 6 AI agents and N4-level cognitive traceability.

**Last Audit**: Cortez27 (December 2025) - Frontend ESLint/TypeScript fixes: 60 problems resolved (36 `any` replacements, 19 unused imports, 5 hook/refresh warnings).

**Integrated Agent Documentation**: See `docs/Misagentes/integrador.md` for comprehensive multi-agent system documentation (all 6 agents, workflows, DB persistence, collaboration patterns).

## ✅ COMPLETED: Exercises JSON → PostgreSQL Migration

**Status**: 🟢 75% Complete (Phases 1-4 done, 5-6 pending)

The exercises migration from JSON to PostgreSQL is **functionally complete**. All core functionality is operational.

**Essential Documents**:
- **Full Plan**: `docs/plans/migracion-ejercicios-db.md` (42/56 tasks completed)

**✅ Completed Phases**:
- ✅ **FASE 1**: Database models and migrations (7 tables created)
- ✅ **FASE 2**: Pydantic schemas and repositories (all 7 repositories implemented)
- ✅ **FASE 3**: Seed database (23 exercises, 2 subjects loaded)
- ✅ **FASE 4**: API endpoints updated (all 6 endpoints migrated)

**⏳ Remaining Work** (non-blocking):
- ⬜ **FASE 5**: Integration tests (optional)
- ⬜ **FASE 6**: Code cleanup and legacy removal (optional)

**Migration Results**:
- ✅ 7 database tables: `subjects`, `exercises`, `exercise_hints`, `exercise_tests`, `exercise_attempts`, `exercise_rubric_criteria`, `rubric_levels`
- ✅ 23 exercises migrated from 8 JSON files
- ✅ All tests and hints associated correctly
- ✅ Student attempts now persist to database for N4 traceability
- ✅ Exercise analytics enabled (success rates, attempt tracking)

**Updated Endpoints** (all in `/training/*`):
- `GET /training/materias` - Reads from `subjects` and `exercises` tables
- `POST /training/iniciar` - Loads exercise with hints/tests from DB
- `POST /training/submit-ejercicio` - **Saves attempts to `exercise_attempts`**
- `POST /training/pista` - Uses hints from DB, tracks usage
- `POST /training/corregir-ia` - Uses tests from DB for AI feedback
- `GET /training/exercises/{id}/details` - Admin debugging endpoint (new)

See `docs/plans/migracion-ejercicios-db.md` for full details.

## ✅ NEW: Entrenador Digital - Estructura Jerárquica

**Status**: 🟢 COMPLETADO (Diciembre 27, 2025)

El Entrenador Digital ahora usa una estructura jerárquica de 3 niveles: **Lenguaje → Lección → Ejercicios**.

**Plan Completo**: `docs/plans/entrenador-digital-secuenciales.md`

### Cambios Implementados

**Backend:**
- ✅ **Nuevo endpoint**: `GET /api/v1/training/lenguajes` - Retorna estructura jerárquica
- ✅ **Schemas nuevos**: `LenguajeInfo`, `LeccionInfo`, `EjercicioInfo`
- ✅ **Endpoint actualizado**: `POST /api/v1/training/iniciar` - Acepta `language` + `unit_number`
- ✅ **Endpoint legacy mantenido**: `GET /api/v1/training/materias` (compatibilidad)

**Frontend:**
- ✅ **Nueva página**: `TrainingPageNew.tsx` - Selector de 3 pasos (Lenguaje → Lección → Iniciar)
- ✅ **Servicio actualizado**: `training.service.ts` - Método `getLenguajes()`
- ✅ **Nomenclatura corregida**: "Lenguaje" en lugar de "Materia"

**Ejercicios de Secuenciales:**
- ✅ **10 ejercicios** creados en Python (unit=1)
- ✅ **40 pistas** con penalizaciones graduales (5, 10, 15, 20 pts)
- ✅ **23 tests automáticos** (visibles y ocultos)
- ✅ **Script de seed**: `backend/scripts/seed_secuenciales.py` (1113 líneas)

### Estructura de Datos

```
Lenguaje: python
  └── Lección: Estructuras Secuenciales (unit=1)
      ├── SEC-01: Hola Mundo (12 pts, 5 min)
      ├── SEC-02: Saludo Personalizado (16 pts, 10 min)
      ├── SEC-03: Datos Personales (16 pts, 15 min)
      ├── SEC-04: Área y Perímetro (24 pts, 20 min)
      ├── SEC-05: Conversión Segundos→Horas (20 pts, 10 min)
      ├── SEC-06: Tabla de Multiplicar (20 pts, 15 min)
      ├── SEC-07: Operaciones Aritméticas (28 pts, 15 min)
      ├── SEC-08: IMC (24 pts, 15 min)
      ├── SEC-09: Celsius→Fahrenheit (20 pts, 10 min)
      └── SEC-10: Promedio de 3 Números (24 pts, 10 min)
      TOTAL: 204 puntos, 125 minutos
```

### Uso del Sistema

```bash
# Cargar ejercicios de Secuenciales
cd activia1-main
python -m backend.scripts.seed_secuenciales

# Preview sin guardar cambios
python -m backend.scripts.seed_secuenciales --dry-run
```

### API Endpoints

```python
# Obtener lenguajes con lecciones (nuevo)
GET /api/v1/training/lenguajes
Response: List[LenguajeInfo]
  └── LenguajeInfo {
        language: str,
        nombre_completo: str,
        lecciones: List[LeccionInfo]
      }
      └── LeccionInfo {
            id: str,
            nombre: str,
            unit_number: int,
            ejercicios: List[EjercicioInfo],
            total_puntos: int,
            dificultad: str
          }

# Iniciar entrenamiento de una lección
POST /api/v1/training/iniciar
Body: {
  "language": "python",
  "unit_number": 1
}
Response: SesionEntrenamiento
```

### Tests Automáticos

Los tests están almacenados en `exercise_tests` table y se ejecutan con el sandbox seguro:

```python
# Ejemplo de test (SEC-02 - Saludo Personalizado)
{
  "exercise_id": "SEC-02",
  "test_number": 1,
  "description": "Verifica saludo con nombre 'Marcos'",
  "input": "Marcos\n",           # Simulado como stdin
  "expected": ".*Hola Marcos.*", # Regex para stdout
  "is_hidden": False,            # Visible para estudiante
  "timeout_seconds": 5
}
```

**Flujo de evaluación**:
1. Estudiante envía código
2. Tests automáticos se ejecutan con `execute_python_code()` (sandbox)
3. CodeEvaluator (IA "Alex") analiza el código y da feedback
4. Nota final = Tests (40%) + IA (60%) - Penalizaciones por pistas
5. Attempt se guarda en `exercise_attempts` (trazabilidad N4)

## Quick Reference

```bash
# Start everything
docker-compose up -d

# Run backend tests
pytest tests/ -v --cov=backend

# Run frontend dev server
cd frontEnd && npm run dev

# Check API health
curl http://localhost:8000/api/v1/health

# View logs
docker-compose logs -f api
```

## Common Commands

### Docker (Recommended)
```bash
docker-compose up -d                    # Start full stack
docker-compose logs -f ollama           # Watch Phi-3 download (~2GB first time)
docker-compose logs -f api              # View API logs
docker-compose ps                       # Check service status
docker-compose down                     # Stop services

# Optional profiles (require additional env vars - see .env.example)
docker-compose --profile debug up -d      # Includes pgAdmin + Redis Commander
docker-compose --profile monitoring up -d # Includes Prometheus + Grafana
```

### Local Development (without Docker)
```bash
# Backend
pip install -r requirements.txt
python -m backend                       # Runs uvicorn on :8000
# Or: uvicorn backend.api.main:app --reload --port 8000

# Seed development data
python backend/scripts/seed_dev.py

# Run database migrations (after model changes)
python -m backend.database.migrations.add_n4_dimensions
python -m backend.database.migrations.add_cortez_audit_fixes
python -m backend.database.migrations.add_cortez1_fixes  # FKs + indexes from cortez1 audit
python -m backend.database.migrations.add_cortez3_fixes  # CASCADE DELETE + indexes from cortez3 audit
python -m backend.database.migrations.add_cortez4_fixes  # Composite indexes + GIN indexes + FK CASCADE from cortez4 audit
python -m backend.database.migrations.add_cortez5_fixes  # resolved_at column + temporal indexes from cortez5 audit
python -m backend.database.migrations.add_cortez6_fixes  # FK constraints + check constraints + sensitive field filtering from cortez6 audit
python -m backend.database.migrations.add_cortez7_fixes  # timestamp indexes + user_id type + server_default from cortez7 audit
python -m backend.database.migrations.add_simulator_events  # Simulator event tables (Sprint 6)
python -m backend.database.migrations.add_cortez11_fixes  # cognitive_coherence + activity-based queries from cortez11 audit

# Rollback migrations if needed
python -m backend.database.migrations.add_cortez1_fixes rollback
python -m backend.database.migrations.add_cortez3_fixes rollback
python -m backend.database.migrations.add_cortez4_fixes rollback
python -m backend.database.migrations.add_cortez5_fixes rollback
python -m backend.database.migrations.add_cortez6_fixes rollback
python -m backend.database.migrations.add_cortez7_fixes rollback
python -m backend.database.migrations.add_cortez11_fixes rollback

# Verify migration status
python -m backend.database.migrations.add_cortez11_fixes verify
```

### Backend Testing
```bash
pytest tests/ -v --cov=backend                    # All tests with coverage (70% min required)
pytest tests/ -v -m "unit"                        # Unit tests only
pytest tests/ -v -m "integration"                 # Integration tests
pytest tests/test_agents.py -v                    # Single file
pytest tests/test_agents.py::test_tutor_mode -v   # Single test function
pytest -k "test_tutor" -v                         # Pattern matching
```

Markers: `unit`, `integration`, `cognitive`, `agents`, `models`, `gateway`, `slow`

### Frontend
```bash
cd frontEnd
npm install && npm run dev              # Dev server (Vite default port)
npm run build                           # Production build (runs tsc first)
npm run lint                            # ESLint
npm run type-check                      # TypeScript check (tsc --noEmit)
npm test                                # Vitest tests
npm run test:ui                         # Vitest with UI
npm run test:coverage                   # Tests with coverage
npm run e2e                             # Playwright E2E tests
npm run e2e:ui                          # Playwright with UI
```

### Make Commands (WSL/Git Bash on Windows)
```bash
make dev                    # Start full stack
make test                   # All tests with coverage
make test-unit              # Unit tests only
make test-integration       # Integration tests only
make lint                   # pylint + flake8
make format                 # black formatting
make health-check           # Verify all services
make generate-secrets       # Generate JWT_SECRET_KEY and CACHE_SALT
make db-shell               # Open PostgreSQL shell
make redis-cli              # Open Redis CLI
```

### Windows-Specific Notes
```powershell
# Health check (PowerShell alternative to curl)
Invoke-RestMethod http://localhost:8000/api/v1/health

# Make commands require WSL, Git Bash, or similar Unix-like shell
# Alternatively, run commands directly:
docker-compose up -d                     # Instead of: make dev
pytest tests/ -v --cov=backend           # Instead of: make test
```

## Architecture

### Request Flow
```
Client → FastAPI Router → AIGateway (STATELESS) → CRPE → Governance Agent
    → Target Agent → LLM Provider → Response Generator → TC-N4 Traceability
    → Risk Analyzer → Repositories (PostgreSQL) → Response
```

### AI Gateway Processing (11 Phases)
```
1. Validation → 2. PII Sanitization (GOV-IA) → 3. Session Retrieval → 4. Prompt Classification (IPC)
→ 5. Governance Check → 6. Input Trace (N4) → 7. Strategy (CRPE) → 8. Agent Routing
→ 9. Response Trace (N4) → 10. Risk Analysis (AR-IA) → 11. Prometheus Metrics
```

### AI Gateway Components (C1-C6)
| Component | Name | Purpose |
|-----------|------|---------|
| C1 | LLM Motor | Connection to Ollama/Mock providers |
| C2 | IPC | Ingesta y Comprensión de Prompt (classification) |
| C3 | CRPE | Cognitive Reasoning Engine (pedagogical strategy) |
| C4 | GSR | Governance, Security & Risk (PII filtering) |
| C5 | OSM | Orchestration of Submodels (agent routing) |
| C6 | TC-N4 | Cognitive Traceability (N4 level) |

### 6 AI Agents (`backend/agents/`)
| Agent | File | Purpose |
|-------|------|---------|
| T-IA-Cog | `tutor.py` | Cognitive Tutor (4 modes: Socratic, Explicative, Guided, Metacognitive) |
| E-IA-Proc | `evaluator.py` | Process Evaluator |
| S-IA-X | `simulators.py` | Professional Role Simulators (6 roles) |
| AR-IA | `risk_analyst.py` | Risk Analyst (5 dimensions) |
| GOV-IA | `governance.py` | Governance & Delegation |
| TC-N4 | `traceability.py` | N4-level Traceability |

**Tutor subsystem files** (advanced pedagogical rules):
- `tutor_rules.py` - 4 unbreakable pedagogical rules (anti-solution, Socratic mode, explicitness, conceptual reinforcement)
- `tutor_governance.py` - Semaphore-based control (verde/amarillo/rojo states)
- `tutor_prompts.py` - Prompt templates for interventions
- `tutor_metadata.py` - N4 intervention metadata tracking
- `git_integration.py` - Git trace analysis for learning insights

### Session Modes (AgentMode)
Defined in `backend/core/cognitive_engine.py`:
- `TUTOR` - T-IA-Cog: Cognitive tutor with 4 pedagogical modes
- `SIMULATOR` - S-IA-X: Professional role simulators (requires `simulator_type`)
- `EVALUATOR` - E-IA-Proc: Process evaluation
- `RISK_ANALYST` - AR-IA: Risk analysis
- `GOVERNANCE` - GOV-IA: Governance and delegation
- `PRACTICE` - Free practice mode (minimal AI assistance)

### Key Files
| Component | Path |
|-----------|------|
| AI Gateway (orchestrator) | `backend/core/ai_gateway.py` |
| Cognitive Engine (CRPE) | `backend/core/cognitive_engine.py` |
| LLM Factory | `backend/llm/factory.py` |
| ORM Models | `backend/database/models.py` |
| Repositories | `backend/database/repositories.py` |
| Base Model (ORM) | `backend/database/base.py` |
| Transaction Manager | `backend/database/transaction.py` |
| DB Migrations | `backend/database/migrations/` |
| API Main | `backend/api/main.py` |
| API Routers | `backend/api/routers/` |
| Pydantic Schemas | `backend/api/schemas/` |
| Core Security | `backend/core/security.py` |
| Tutor Governance Engine | `backend/agents/tutor_governance.py` |
| Tutor Rules Engine | `backend/agents/tutor_rules.py` |
| Governance Agent | `backend/agents/governance.py` |
| Frontend API Services | `frontEnd/src/services/api/` |
| Frontend Types | `frontEnd/src/types/index.ts`, `frontEnd/src/types/api.types.ts` |
| Prometheus Alerts | `prometheus-alerts.yml` |

## Critical Rules

### ORM vs Pydantic Field Mappings
```python
# SQLAlchemy reserved words - use these mappings:
db_trace.trace_metadata   # ORM model uses trace_metadata
trace.trace_metadata      # Domain model also uses trace_metadata (FIX Cortez8)

# Timestamp mapping (FIX 3.1 Cortez8):
# ORM uses: created_at, updated_at
# Pydantic domain: created_at with alias="timestamp" for backwards compatibility
# Example: created_at: datetime = Field(default_factory=datetime.now, alias="timestamp")

# Enum storage - always lowercase strings in DB:
session.status = "active"        # NOT "ACTIVE"
risk.risk_level = "critical"     # NOT "CRITICAL"
risk.dimension = "cognitive"     # NOT "COGNITIVE" (FIX Cortez8)

# Score scales (FIX 1.1-1.6 Cortez8):
evaluation.overall_score         # 0-10 scale (was 0-1, now fixed)
evaluation.dimension.score       # 0-10 scale (was 0-1, now fixed)
session_summary.overall_score    # 0-1 normalized (documented)
risk_analysis.overall_score      # 0-100 percentage (documented)
risk_dimension.score             # 0-10 scale
ai_dependency_score              # 0-1 scale (always)
```

### Required Fields
```python
# CognitiveTrace ALWAYS needs session_id
CognitiveTrace(session_id="...", student_id="...", ...)

# Risk ALWAYS needs dimension AND session_id
Risk(session_id="...", dimension=RiskDimension.COGNITIVE, ...)

# Sessions with mode=SIMULATOR need simulator_type
# V1: product_owner, scrum_master, tech_interviewer, incident_responder, client, devsecops
# V2: senior_dev, qa_engineer, security_auditor, tech_lead, demanding_client

# Specialized simulator endpoints (Sprint 6):
# POST /simulators/interview/*       - IT-IA (Tech Interviewer)
# POST /simulators/incident/*        - IR-IA (Incident Responder)
# POST /simulators/scrum/daily-standup - SM-IA (Scrum Master)
# POST /simulators/security/audit    - DSO-IA (DevSecOps)
# POST /simulators/client/*          - CX-IA (Client)
```

### Frontend-Backend Type Alignment
```typescript
// InteractionCreate - MUST use 'prompt' not 'student_input'
const interaction = { session_id: "...", prompt: "user message", context: {} };

// Risk interface - field is 'resolved' NOT 'is_resolved'
interface Risk { resolved: boolean; }

// EvaluationDimension - use 'name' for dimension identifier
interface EvaluationDimension {
  name: string;       // Dimension name
  dimension?: string; // LEGACY: deprecated alias
}

// SessionMode - use enum, not string literal (FIX Cortez16)
import { SessionMode } from '../types';
const session = { mode: SessionMode.TUTOR };  // CORRECT
const session = { mode: 'TUTOR' };            // WRONG - string not assignable to enum

// Report requests - must match backend schemas (FIX Cortez19)
// CohortReportRequest and RiskDashboardRequest require all fields:
interface CohortReportRequest {
  course_id: string;      // Required
  teacher_id: string;     // Required
  student_ids: string[];  // Required
  period_start: string;   // ISO datetime
  period_end: string;     // ISO datetime
}
```

### AIGateway is STATELESS
- All state persists to PostgreSQL via repositories
- No in-memory sessions/traces/risks
- Supports horizontal scaling

### Authentication Required
After cortez1, cortez19, and cortez20 audit fixes, most endpoints require authentication:
```python
# Endpoints that require get_current_user:
# - POST/GET/PATCH/DELETE /sessions/*
# - POST /interactions
# - POST /evaluations/{session_id}/generate
# - GET /risk-analysis/{session_id}
# - POST/GET /events/*
# - GET /traces/session/{session_id} (FIX Cortez20)
# - GET /traces/student/{student_id} (FIX Cortez20)
# - GET /risks/session/{session_id} (FIX Cortez20)
# - GET /risks/student/{student_id} (FIX Cortez20)
# - GET /risks/evaluation/session/{session_id} (FIX Cortez20)
# - GET /cognitive-path/{session_id} (FIX Cortez20)

# Endpoints that require require_teacher_role (FIX Cortez19):
# - POST /activities (create)
# - PUT /activities/{id} (update)
# - POST /activities/{id}/publish
# - POST /activities/{id}/archive
# - DELETE /activities/{id}
# - POST /reports/cohort
# - POST /reports/risk-dashboard
# - GET /teacher/*

# Endpoints that still allow public access:
# - GET /health
# - GET /health/detailed
# - GET /activities (list/read)
```

### LLM Provider Methods are ASYNC
```python
response = await provider.generate(messages, temperature=0.7)  # CORRECT
response = provider.generate(messages)  # WRONG - missing await
```

### Thread Safety (Required for Singletons)
```python
_instance = None
_lock = threading.Lock()

def get_instance():
    global _instance
    if _instance is None:
        with _lock:
            if _instance is None:
                _instance = create_instance()
    return _instance
```

### Batch Loading for N+1 Prevention
```python
# CORRECT - single query for all sessions
traces_by_session = trace_repo.get_by_session_ids(session_ids)

# CORRECT - batch loading for student-activity pairs (Cortez3)
pairs = [("student1", "act1"), ("student2", "act1")]
traces_by_pair = trace_repo.get_by_student_activity_pairs(pairs)

# INCORRECT - N+1 queries
for session_id in session_ids:
    traces = trace_repo.get_by_session(session_id)  # DON'T loop
```

### Database Integrity (Cortez4)
```python
# All child tables MUST have CASCADE on session_id FK:
session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)

# Use atomic updates for counters (avoid race conditions):
self.db.query(UserDB).filter(UserDB.id == user_id).update(
    {UserDB.login_count: UserDB.login_count + 1},
    synchronize_session='fetch'
)

# Use with_for_update() for concurrent updates:
session = self.db.query(SessionDB).filter(SessionDB.id == session_id).with_for_update().first()

# Always wrap repository operations with rollback:
try:
    self.db.add(entity)
    self.db.commit()
except SQLAlchemyError as e:
    self.db.rollback()
    raise
```

### Required Composite Indexes (Cortez4)
These indexes are required for common query patterns:
- `idx_risk_session_resolved` - (session_id, resolved) on risks
- `idx_risk_session_level` - (session_id, risk_level) on risks
- `idx_trace_session_level` - (session_id, trace_level) on cognitive_traces
- `idx_eval_session_created` - (session_id, created_at) on evaluations
- `idx_interaction_session_created` - (session_id, created_at) on interactions

### Eager Loading Standards
```python
# Use selectinload for collections (one-to-many):
query.options(selectinload(SessionDB.interactions))

# Use joinedload for single objects (many-to-one):
query.options(joinedload(SessionDB.user))
```

### Transaction Management for Batch Operations
```python
from backend.database.transaction import transaction

# Wrap multiple DB operations in explicit transaction
with transaction(db, "Create session with traces and risks"):
    session = SessionDB(...)
    db.add(session)  # No commit yet
    trace = CognitiveTraceDB(...)
    db.add(trace)
    # Auto-commit on success, rollback on exception
```

### UUID Validation
```python
from backend.api.schemas.common import validate_uuid_format

# Validate session_id format before DB access
session_id = validate_uuid_format(session_id, "session_id")
```

### Sensitive Field Filtering (Cortez6)
```python
# BaseModel.to_dict() automatically filters sensitive fields
user.to_dict()  # Excludes hashed_password, launch_token

# To include sensitive fields (admin use only):
user.to_dict(include_sensitive=True)

# Sensitive fields defined in BaseModel._SENSITIVE_FIELDS:
# {'hashed_password', 'launch_token'}
```

### Input Validation Constants
```python
# From backend/core/constants.py - AI Gateway validation
PROMPT_MIN_LENGTH = 10              # Minimum prompt characters
PROMPT_MAX_LENGTH = 5000            # Maximum prompt characters
CONTEXT_MAX_SIZE_BYTES = 10240      # 10KB max context size
SESSION_ID_MAX_LENGTH = 100         # Max session_id length

# Risk detection thresholds
AI_DEPENDENCY_LOW_THRESHOLD = 0.3   # 30% - no risk
AI_DEPENDENCY_MEDIUM_THRESHOLD = 0.6 # 60% - triggers MEDIUM risk
AI_DEPENDENCY_HIGH_THRESHOLD = 0.8   # 80% - triggers HIGH risk
GOVERNANCE_BLOCK_THRESHOLD = 0.9     # 90% - automatic block
```

### Common Import Patterns (Cortez14 Fixes)
```python
# Backend - datetime imports (FIX: use datetime module correctly)
from datetime import datetime, timedelta, timezone
# CORRECT: datetime.now(timezone.utc)
# WRONG: datetime.datetime.now() - redundant if using 'from datetime import datetime'

# Backend - typing imports
from typing import Optional, List, Dict, Any, Union
```

```typescript
// Frontend - React imports pattern
import { useState, useEffect, useCallback } from 'react';
import type { FC, ReactNode } from 'react';

// Type guards for API responses
function isApiError(error: unknown): error is { message: string } {
  return typeof error === 'object' && error !== null && 'message' in error;
}

// Memory leak prevention pattern (FIX Cortez20)
// Always use isMounted check in async useEffect
useEffect(() => {
  let isMounted = true;
  const fetchData = async () => {
    const result = await service.getData();
    if (isMounted) setState(result);  // Only update if still mounted
  };
  fetchData();
  return () => { isMounted = false; };
}, [deps]);
```

## Frontend-Backend Integration

**API Base Path**: All routes are prefixed with `/api/v1/`

### Key Route Mappings
| Frontend Service | Backend Route |
|-----------------|---------------|
| Git traces | `/git/session/{id}` |
| Git analytics | `/git-analytics/...` |
| Risk analysis (5D) | `/risk-analysis/{session_id}` |
| Risks & evaluation | `/risks/evaluation/session/{id}` |
| Teacher tools | `/teacher/students/compare` |
| Simulators V1 | `POST /simulators/interact` |
| Simulators V2 | `POST /simulators-v2/...` |
| Auth login | `POST /auth/login` (JSON: email + password) |
| Cognitive path | `/cognitive-path/{session_id}` |
| Traceability N4 | `/traceability/{interaction_id}` |
| Reports | `/reports/...` |
| Export | `/export/...` |

### Enum Values
```typescript
// Lowercase (match backend):
SessionStatus: 'active' | 'completed' | 'paused' | 'aborted' | 'abandoned'
RiskLevel: 'low' | 'medium' | 'high' | 'critical' | 'info'
TraceLevel: 'n1_superficial' | 'n2_tecnico' | 'n3_interaccional' | 'n4_cognitivo'
// V1 + V2 simulators (Sprint 6):
SimulatorType: 'product_owner' | 'scrum_master' | 'tech_interviewer' | 'incident_responder' | 'client' | 'devsecops' | 'senior_dev' | 'qa_engineer' | 'security_auditor' | 'tech_lead' | 'demanding_client'

// UPPERCASE exceptions:
CognitiveIntent: 'UNDERSTANDING' | 'EXPLORATION' | 'PLANNING' | 'IMPLEMENTATION' | 'DEBUGGING' | 'VALIDATION' | 'REFLECTION'
ActivityDifficulty: 'INICIAL' | 'INTERMEDIO' | 'AVANZADO'
```

### Response Wrapper
All API responses use: `{ success: boolean, data: T, message?: string }`

### Frontend Services (modular pattern)
```typescript
// Use modular services from /services/api/
import { sessionsService, authService } from '../services/api';

// Core services from /core/services/
import { sessionService } from '@/core/services/SessionService';
import { interactionService } from '@/core/services/InteractionService';
```

Available API services: `authService`, `sessionsService`, `interactionsService`, `simulatorsService`, `tracesService`, `risksService`, `evaluationsService`, `healthService`, `cognitivePathService`, `activitiesService`, `adminService`, `reportsService`, `gitService`

### Frontend State Management
The frontend uses both **Zustand** (primary global state) and **Context API** (component-scoped state). Use `@tanstack/react-query` for server state management.

## LLM Provider Usage

```python
from backend.llm import LLMProviderFactory

# Create from environment (recommended)
provider = LLMProviderFactory.create_from_env()

# Or create specific provider
provider = LLMProviderFactory.create("ollama", {
    "base_url": "http://localhost:11434",
    "model": "phi3"
})

# Generate response (async)
response = await provider.generate(messages, temperature=0.7)
```

Available providers: `mock` (testing), `ollama` (local LLM, recommended), `openai` (GPT-4)

## Risk Dimensions (5D)

The AR-IA agent monitors 5 risk dimensions defined in `backend/models/risk.py`:

| Dimension | Code | Risk Types |
|-----------|------|------------|
| Cognitive (RC) | `COGNITIVE` | `COGNITIVE_DELEGATION`, `SUPERFICIAL_REASONING`, `AI_DEPENDENCY`, `LACK_JUSTIFICATION`, `NO_SELF_REGULATION` |
| Ethical (RE) | `ETHICAL` | `ACADEMIC_INTEGRITY`, `UNDISCLOSED_AI_USE`, `PLAGIARISM` |
| Epistemic (REp) | `EPISTEMIC` | `CONCEPTUAL_ERROR`, `LOGICAL_FALLACY`, `UNCRITICAL_ACCEPTANCE` |
| Technical (RT) | `TECHNICAL` | `SECURITY_VULNERABILITY`, `POOR_CODE_QUALITY`, `ARCHITECTURAL_FLAW` |
| Governance (RG) | `GOVERNANCE` | `POLICY_VIOLATION`, `UNAUTHORIZED_USE`, `AUTOMATION_SUSPECTED` |

## Tutor Pedagogical Rules

The Socratic Tutor (T-IA-Cog) enforces 4 unbreakable rules in `tutor_rules.py`:

| Rule | Enum | Behavior |
|------|------|----------|
| Anti-Solution | `ANTI_SOLUCION` | Never give complete code; blocks direct solution requests |
| Socratic Mode | `MODO_SOCRATICO` | Default: ask questions, don't answer directly |
| Explicitness | `EXIGIR_EXPLICITACION` | Force students to verbalize their thinking |
| Conceptual | `REFUERZO_CONCEPTUAL` | Redirect to theory, not quick fixes |

**Intervention types** (`InterventionType`): `PREGUNTA_SOCRATICA`, `RECHAZO_PEDAGOGICO`, `PISTA_GRADUADA`, `CORRECCION_CONCEPTUAL`, `EXIGENCIA_JUSTIFICACION`, `EXIGENCIA_PSEUDOCODIGO`, `REMISION_TEORIA`

**Scaffolding levels** (`CognitiveScaffoldingLevel`): `NOVATO`, `INTERMEDIO`, `AVANZADO`

## Governance Semaphore System

The TutorGovernanceEngine (`tutor_governance.py`) uses a traffic light system for risk-based intervention:

| State | Risk Level | Behavior |
|-------|------------|----------|
| `VERDE` | Low | Normal interaction, full help available |
| `AMARILLO` | Medium | Reduced help, monitoring active, require justification |
| `ROJO` | High | Block code generation, redirect pedagogically |

**3-Phase Processing (IPC-GSR-Andamiaje):**
1. **IPC** - Ingesta y Comprension de Prompt (intent detection, autonomy estimation)
2. **GSR** - Gobernanza y Semaforo de Riesgo (risk evaluation, semaphore determination)
3. **ANDAMIAJE** - Scaffolding strategy selection (response type, help level)

**PromptIntent types**: `EXPLORACION`, `DEPURACION`, `DELEGACION`, `CLARIFICACION`, `VALIDACION`

**Compliance Status** (from GOV-IA `governance.py`):
```python
COMPLIANT   # All policies satisfied, proceed normally
WARNING     # Warnings exist, proceed with caution
VIOLATION   # Policies violated, block action + educate

# PolicyLevel hierarchy:
INSTITUTIONAL > PROGRAM > COURSE > ACTIVITY
```

**PII Sanitization patterns**: `email`, `dni`, `phone`, `credit_card` - automatically redacted before LLM processing.

## Environment Configuration

Key `.env` variables (see `.env.example` for full template):

**Required:**
- `POSTGRES_PASSWORD`, `REDIS_PASSWORD` - Database credentials
- `JWT_SECRET_KEY`, `SECRET_KEY` - Generate with `make generate-secrets`

**LLM:**
- `LLM_PROVIDER`: `ollama` | `mock` | `openai`
- `OLLAMA_BASE_URL`: `http://localhost:11434` (local) or `http://ollama:11434` (Docker)
- `OLLAMA_MODEL`: `phi3` (recommended), `llama2`, `mistral`, `codellama`
- `OLLAMA_TEMPERATURE`: `0.7` default

**Application:**
- `DATABASE_URL`, `REDIS_URL` - Connection strings
- `ALLOWED_ORIGINS`: Include frontend ports (`http://localhost:3000,http://localhost:5173`)

**Debug Profile** (docker-compose --profile debug):
- `PGADMIN_EMAIL`, `PGADMIN_PASSWORD` - pgAdmin credentials
- `REDIS_COMMANDER_USER`, `REDIS_COMMANDER_PASSWORD` - Redis Commander HTTP basic auth

**Monitoring Profile** (docker-compose --profile monitoring):
- `GRAFANA_USER`, `GRAFANA_PASSWORD` - Grafana admin credentials

## N4 Traceability Levels

| Level | Name | What it Captures |
|-------|------|------------------|
| N1 | Superficial | Files, deliveries, final code version |
| N2 | Technical | Commits, branches, automated tests |
| N3 | Interactional | Prompts, responses, retries |
| N4 | Cognitive | Intention, decisions, justifications, alternatives, risk |

## Dependency Management

```bash
# Install from requirements.txt (development)
pip install -r requirements.txt

# Install from requirements.lock (reproducible builds)
pip install -r requirements.lock
```

## Documentation

### Essential Reading
| Document | Purpose |
|----------|---------|
| `docs/Misagentes/integrador.md` | **START HERE** - Complete multi-agent system (6 agents, workflows, DB, collaboration) |
| `docs/api/README_API.md` | REST API reference |
| `docs/llm/OLLAMA_QUICKSTART.md` | LLM setup guide |

### User Guides (root level)
`GUIA_ESTUDIANTE.md`, `GUIA_DOCENTE.md`, `GUIA_ADMINISTRADOR.md`, `GUIA_INTEGRACION_LLM.md`

### Agent Documentation (`docs/Misagentes/`)
Individual agent docs: `evaluador1.md` (E-IA-Proc), `simulador.md` (S-IA-X), `apigateway.md` (AI Gateway), `analista.md` (AR-IA), `gobernanza.md` (GOV-IA), `Flujo.md` (10-phase flow)

## Audit History

| Audit | Issues | Key Areas |
|-------|--------|-----------|
| Cortez | 70+ | Risk persistence, async/await, N+1 queries, GIN indexes |
| Cortez1 | 127 | Auth endpoints, Docker credentials, FK constraints |
| Cortez2 | 156 | Frontend pages, Pydantic schemas, Prometheus alerts |
| Cortez3 | 114 | Rate limiting, CORS, CASCADE DELETE, batch loading |
| Cortez4 | 75+ | Composite indexes, race conditions, check constraints |
| Cortez5 | 38 | Temporal queries, pessimistic locking, resolved_at |
| Cortez6 | 45+ | FK constraints, range constraints, sensitive fields |
| Cortez7 | 38 | Enum unification, relationships, server defaults |
| Cortez8 | 45 | Score scales (0-10), ORM/Pydantic consistency, N4 dimensions |
| Cortez9 | - | *Skipped (no audit performed)* |
| Cortez10 | 24 | DB-Backend consistency, ORM fields, repository methods |
| Cortez11 | 10 | Activity-based queries, cognitive_coherence field, repository methods |
| Cortez12 | 45 | Frontend-Backend API consistency, field names, types, query params |
| Cortez13 | - | *Skipped (no audit performed)* |
| Cortez14 | 47 | Execution errors: backend datetime import, frontend TypeScript errors |
| Cortez15 | - | *Skipped (no audit performed)* |
| Cortez16 | 34 | TypeScript fixes: SessionMode enum, named imports, type casting, snake_case |
| Cortez17 | - | *Skipped (no audit performed)* |
| Cortez18 | - | *Skipped (no errors found)* |
| Cortez19 | 23 | Frontend-Backend API consistency: schema mismatches, auth on activities, 3 false positives |
| Cortez20 | 67 | Senior anomaly analysis: auth on 7 endpoints, memory leaks, APIResponse wrapper bypass, type safety, FK indexes |
| Cortez21 | 50+ | SQL filtering in repositories, student traces optimization |
| Cortez22 | 98 | N+1 batch loading (CourseReportGenerator), React memory leaks (isMounted), risk_type validator no-op fix |
| Cortez23 | - | *Skipped (merged with Cortez24)* |
| Cortez24 | 81 | TypeScript: GitTrace event_type narrowing, CognitiveIntent enum duplicates, 42 `any` replacements |
| Cortez25 | 4 | Backend startup: JSONB/SQLite compatibility, User model consolidation, self-referential relationship fix |
| Cortez26 | - | *Skipped (no audit performed)* |
| Cortez27 | 60 | Frontend ESLint/TypeScript: 36 `any` replacements, 19 unused imports, 5 hook/refresh warnings |

**Note**: Cortez9, Cortez13, Cortez15, Cortez17, Cortez18, Cortez23 were skipped. Not all audits require migrations (cortez2, cortez8, cortez10, cortez12, cortez14, cortez16, cortez19, cortez20, cortez21, cortez22, cortez24, cortez25 were code-only changes).

Audit files in root: `cortez`, `cortez1` through `cortez8`, `cortez10`, `cortez11`, `cortez12`, `cortez14`, `cortez16`, `cortez19`, `cortez20`, `cortez21`, `cortez22`, `cortez24`, `cortez25`. Migration scripts in `backend/database/migrations/`.

## Critical SQLAlchemy Rules (Cortez25)

### User Model - Use UserDB Only
```python
# CORRECT - Use UserDB from database.models
from backend.database.models import UserDB as User
from backend.models.user import UserRole  # Only for enum

# WRONG - Don't import User class (removed in Cortez25)
from backend.models.user import User  # REMOVED - causes duplicate table conflict
```

### Self-Referential Relationships
```python
# CORRECT - Use string reference for remote_side
parent_trace = relationship(
    "CognitiveTraceDB",
    remote_side="CognitiveTraceDB.id",  # String reference
    foreign_keys=[parent_trace_id]
)

# WRONG - Using bare `id` calls Python's built-in id() function
remote_side=[id]  # ERROR: uses built-in id() not column
```

### JSONB Compatibility for SQLite
```python
# CORRECT - Use JSONBCompatible for cross-database support
from backend.database.models import JSONBCompatible
roles = Column(JSONBCompatible, default=list)

# WRONG - JSONB only works with PostgreSQL
from sqlalchemy.dialects.postgresql import JSONB
roles = Column(JSONB, default=list)  # Fails on SQLite
```

### OpenAPI Routes Count
Backend exposes **102 routes** across 22 categories:
- simulators (15), admin (15), sessions (9), risks (7), reports (7)
- health (5), exercises (5), auth (5), activities (4), git (4)
- simulators-v2 (4), traces (3), teacher (3), export (3)
- interactions (2), cognitive-path (2), traceability (2), events (2)
- risk-analysis (1), git-analytics (1), evaluations (1)