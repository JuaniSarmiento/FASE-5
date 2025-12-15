# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-Native MVP for teaching-learning programming with generative AI. Doctoral thesis project implementing process-based evaluation (not product-based) with N4-level cognitive traceability.

**Tech Stack**: Python 3.11+/FastAPI backend, React 18+/TypeScript/Vite frontend, PostgreSQL, Redis, Ollama/Phi-3 for LLM.

**Key Concept**: The system evaluates HOW students solve problems (cognitive process), not just the final code output. This is achieved through 6 AI agents and N4-level cognitive traceability.

## Quick Start

```bash
# 1. Start with Docker (recommended)
docker-compose up -d
# Wait for Phi-3 model download (~2GB, first time only)
docker-compose logs -f ollama

# 2. Access
# Backend API: http://localhost:8000/docs
# Frontend: cd frontEnd && npm install && npm run dev → http://localhost:3000
```

## Common Commands

> **Note for Windows**: The `make` commands require WSL, Git Bash, or similar. Alternatively, run the Docker/pytest commands directly.

```bash
# Development
make dev                    # Start full stack (API + DB + Redis + Ollama)
make dev-debug              # Add pgAdmin + Redis Commander
make dev-monitoring         # Add Prometheus + Grafana

# Testing
make test                   # Run all tests with coverage
make test-unit              # Unit tests only (pytest -m unit)
make test-integration       # Integration tests only
pytest tests/test_agents.py -v  # Run single test file
pytest -k "test_tutor" -v   # Run tests matching pattern

# Code Quality
make lint                   # Run pylint + flake8
make format                 # Format with black
make type-check             # mypy type checking
make security-check         # bandit security scan

# Database
make db-init                # Initialize PostgreSQL
make db-shell               # PostgreSQL CLI
make db-backup              # Backup database

# Utilities
make health-check           # Verify all services
make clean                  # Clean temp files

# Frontend
cd frontEnd && npm install && npm run dev   # Development server (port 3000)
cd frontEnd && npm run build                # Production build
cd frontEnd && npm run lint                 # ESLint check
cd frontEnd && npm run type-check           # TypeScript check

# Generate secrets (for .env JWT_SECRET_KEY)
make generate-secrets

# Direct pytest commands (Windows without make)
pytest tests/ -v --cov=backend                    # All tests with coverage
pytest tests/ -v -m "unit"                        # Unit tests only
pytest tests/ -v -m "integration"                 # Integration tests
pytest tests/test_agents.py::test_tutor_mode -v   # Single test function
```

## Architecture

### C4 Extended Model (6 Components)
- **C1**: LLM Motor (OpenAI/Ollama/Gemini abstraction via Factory pattern)
- **C2**: Prompt Ingestion & Comprehension
- **C3**: CRPE - Cognitive Reasoning Engine (`backend/core/cognitive_engine.py`)
- **C4**: GSR - Governance, Security, Risk
- **C5**: OSM - Submodel Orchestration (6 agents in `backend/agents/`)
- **C6**: N4 Cognitive Traceability

### Request Flow
```
Client → FastAPI Router → AIGateway (STATELESS) → CRPE → Governance Agent
    → Target Agent (Tutor/Evaluator/Simulators/RiskAnalyst)
    → LLM Provider → Response Generator → TC-N4 Traceability
    → Risk Analyzer → Repositories (PostgreSQL) → Response
```

### 6 AI Agents (`backend/agents/`)
- `tutor.py` - T-IA-Cog: Cognitive Tutor (4 modes: Socratic, Explicative, Guided, Metacognitive)
- `evaluator.py` - E-IA-Proc: Process Evaluator
- `simulators.py` - S-IA-X: Professional Role Simulators (6 roles: product_owner, scrum_master, tech_interviewer, incident_responder, client, devsecops)
- `risk_analyst.py` - AR-IA: Risk Analyst (5 dimensions: cognitive, ethical, epistemic, technical, governance)
- `governance.py` - GOV-IA: Governance & Delegation
- `traceability.py` - TC-N4: N4-level Traceability
- `git_integration.py` - Git trace analysis (N2 technical traceability)

### Key Design Patterns
- **Factory**: `LLMProviderFactory` in `backend/llm/factory.py`
- **Repository**: 14 ORM models in `backend/database/models.py`, abstracted in `repositories.py`
- **Dependency Injection**: FastAPI `Depends()` throughout routers
- **Double-Checked Locking**: Thread-safe singletons in `llm/factory.py`, `core/cache.py`

## Critical Rules

### ORM vs Pydantic/Domain Model Field Mappings
```python
# SQLAlchemy reserved words - use these mappings in routers/repositories:
db_trace.trace_metadata   # ORM model uses trace_metadata
trace.metadata            # Domain model (Pydantic) uses metadata

# When reading from DB in routers:
trace_meta = trace.trace_metadata or {}  # NOT trace.metadata
is_blocked = trace_meta.get("blocked", False)

# When creating traces in repositories (repositories.py):
db_trace = CognitiveTraceDB(
    trace_metadata=trace.metadata,  # Map domain → ORM
    ...
)

# When reconstructing domain from ORM (traceability.py):
domain_trace = CognitiveTrace(
    metadata=db_trace.trace_metadata,  # Map ORM → domain
    ...
)

# Timestamp mapping:
# ORM uses: created_at, updated_at (SQLAlchemy columns)
# Domain/API uses: timestamp (Pydantic field)

# Enum storage - always lowercase strings in DB:
session.status = "active"        # NOT "ACTIVE"
risk.risk_level = "critical"     # NOT "CRITICAL"
trace.trace_level = "n4_cognitivo"
```

### Thread Safety Pattern (Required for Singletons)
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

### Required Fields
```python
# CognitiveTrace ALWAYS needs session_id
CognitiveTrace(session_id="...", student_id="...", ...)

# Risk ALWAYS needs dimension AND session_id
Risk(
    session_id="...",  # REQUIRED - Risk must be associated to a session
    dimension=RiskDimension.COGNITIVE,
    risk_type=...,
    ...
)

# Sessions with mode=SIMULATOR need simulator_type
# SessionCreate schema validates this automatically with @model_validator
session_repo.create(
    student_id="...",
    activity_id="...",
    mode="SIMULATOR",
    simulator_type="product_owner"  # REQUIRED for SIMULATOR mode
    # Valid values: product_owner, scrum_master, tech_interviewer, incident_responder, client, devsecops
)

# EvaluationResponse includes ai_dependency_score
EvaluationResponse(
    ...
    ai_dependency_score=eval.ai_dependency_score or 0.0,  # Score 0-1
    ai_dependency_metrics=eval.ai_dependency_metrics or {},  # Detailed metrics
    ...
)
```

### Batch Loading for Performance (N+1 Query Prevention)
```python
# Use batch loading methods when loading data for multiple sessions
from backend.database.repositories import TraceRepository, RiskRepository

# CORRECT - single query for all sessions
traces_by_session = trace_repo.get_by_session_ids(session_ids)  # Dict[str, List[CognitiveTraceDB]]
risks_by_session = risk_repo.get_by_session_ids(session_ids)    # Dict[str, List[RiskDB]]

# INCORRECT - N+1 queries (one per session)
for session_id in session_ids:
    traces = trace_repo.get_by_session(session_id)  # DON'T do this in a loop
```

### AIGateway is STATELESS
- All state persists to PostgreSQL via repositories
- No in-memory sessions/traces/risks
- Supports horizontal scaling with load balancer

## LLM Provider Usage

```python
# Create provider from environment (recommended)
from backend.llm import LLMProviderFactory
provider = LLMProviderFactory.create_from_env()

# Or create specific provider
provider = LLMProviderFactory.create("ollama", {
    "base_url": "http://localhost:11434",
    "model": "phi3"
})

# Generate response (async)
response = await provider.generate(messages, temperature=0.7)
```

Available providers: `mock` (testing), `ollama` (local LLM), `openai` (GPT-4)

### JSONBCompatible for DB Portability
```python
# backend/database/models.py uses JSONBCompatible type
# - Uses JSONB on PostgreSQL (production)
# - Falls back to JSON on SQLite (testing)
# This allows tests to run with SQLite while production uses PostgreSQL
```

## Frontend-Backend API Integration

### Key Route Mappings (Frontend → Backend)
```
Frontend Service          Backend Route
─────────────────────────────────────────────────────────
Git traces               /git/session/{id} (NOT /git-traces/)
Evaluations              /risks/evaluation/session/{id} (NOT /evaluations/)
Teacher tools            /teacher/students/compare (NOT /teacher-tools/)
Admin LLM                /admin/llm/providers (NOT /admin/llm/config)
Simulators               POST /simulators/interact (needs session_id + prompt)
Auth login               POST /auth/login (JSON: email + password, NOT FormData)
Export research          /export/research-data (NOT /export/research)
Reports activity         /reports/activity/{id}
Reports analytics        /reports/analytics
Export session           /export/session/{id}
Export activity          /export/activity/{id}
Cognitive path           /cognitive-path/{session_id} (canonical endpoint)
                         /traces/{session_id}/cognitive-path (DEPRECATED - redirects to above)
```

### Enum Value Mappings (Frontend ↔ Backend)
```typescript
// Frontend enums MUST use lowercase values to match backend:
SessionStatus: 'active' | 'completed' | 'paused' | 'aborted'  // NOT uppercase
RiskLevel: 'low' | 'medium' | 'high' | 'critical' | 'info'    // NOT uppercase
TraceLevel: 'n1_superficial' | 'n2_tecnico' | 'n3_interaccional' | 'n4_cognitivo'
CognitiveState: 'exploracion' | 'planificacion' | 'implementacion' | 'depuracion' | 'validacion' | 'reflexion'
HelpLevel: 'minimo' | 'bajo' | 'medio' | 'alto'  // NOT uppercase
SimulatorType: 'product_owner' | 'scrum_master' | 'tech_interviewer' | 'incident_responder' | 'client' | 'devsecops'  // lowercase, NOT uppercase
ActivityStatus: 'draft' | 'active' | 'archived'  // lowercase

// CognitiveIntent and ActivityDifficulty use UPPERCASE (exceptions):
CognitiveIntent: 'UNDERSTANDING' | 'EXPLORATION' | 'PLANNING' | 'IMPLEMENTATION' | 'DEBUGGING' | 'VALIDATION' | 'REFLECTION' | 'UNKNOWN'
ActivityDifficulty: 'INICIAL' | 'INTERMEDIO' | 'AVANZADO'  // UPPERCASE

// RiskType (16 types across 5 dimensions - from backend/models/risk.py):
// Cognitive: 'cognitive_delegation' | 'superficial_reasoning' | 'ai_dependency' | 'lack_justification' | 'no_self_regulation'
// Ethical: 'academic_integrity' | 'undisclosed_ai_use' | 'plagiarism'
// Epistemic: 'conceptual_error' | 'logical_fallacy' | 'uncritical_acceptance'
// Technical: 'security_vulnerability' | 'poor_code_quality' | 'architectural_flaw'
// Governance: 'policy_violation' | 'unauthorized_use'

// RiskDimension (5 dimensions - ISO/IEC 23894):
RiskDimension: 'cognitive' | 'ethical' | 'epistemic' | 'technical' | 'governance'
```

### Authentication
- Backend uses JWT with `email` field for login (not username)
- Frontend stores token in `localStorage.access_token`
- HTTP client auto-attaches `Authorization: Bearer` header

### Response Wrapper (APIResponse)
All API responses use: `{ success: boolean, data: T, message?: string }`

```typescript
// Frontend services using BaseApiService (sessions, activities, traces, risks, interactions)
// automatically extract response.data.data via helper functions in client.ts

// Services using apiClient directly MUST extract data manually:
const response = await apiClient.get('/endpoint');
const data = response.data.data || response.data;  // Handle both wrapped and unwrapped

// For arrays, also validate:
const items = response.data.data || response.data;
return Array.isArray(items) ? items : [];
```

## Testing

pytest markers: `unit`, `integration`, `cognitive`, `agents`, `models`, `gateway`

Fixtures in `tests/conftest.py` provide: mock LLM provider, sample traces, risks, sessions, etc.

Coverage requirement: 70% minimum (enforced in `pytest.ini`)

## Environment Configuration

Key `.env` variables:
- `LLM_PROVIDER`: `ollama` | `mock` | `openai`
- `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TEMPERATURE`
- `DATABASE_URL`, `REDIS_URL`
- `JWT_SECRET_KEY` (generate with `make generate-secrets`)
- `ALLOWED_ORIGINS`: Include `http://localhost:3000` for frontend

## API Endpoints

17 routers in `backend/api/routers/`: health, sessions, interactions, traces, risks, activities, simulators, cognitive_path, teacher_tools, admin_llm, auth, git_traces, reports, institutional_risks, export, metrics.

Key endpoints:
- Health: `GET /api/v1/health`
- Metrics: `GET /metrics` (Prometheus format)
- LLM Test: `POST /api/v1/admin/llm/test?provider=ollama`
- System Metrics: `GET /api/v1/admin/llm/metrics`

## File Locations Quick Reference

| Component | Path |
|-----------|------|
| AI Gateway (orchestrator) | `backend/core/ai_gateway.py` |
| Cognitive Engine (CRPE) | `backend/core/cognitive_engine.py` |
| LLM Factory | `backend/llm/factory.py` |
| ORM Models | `backend/database/models.py` |
| Repositories | `backend/database/repositories.py` |
| API Main | `backend/api/main.py` |
| API Routers | `backend/api/routers/` |
| Pydantic Schemas | `backend/api/schemas/` |
| Frontend API Services | `frontEnd/src/services/api/` |
| Frontend Types (central) | `frontEnd/src/types/api.types.ts` |
| Frontend Pages | `frontEnd/src/pages/` |

## Frontend Service Architecture

### BaseApiService Pattern
All frontend API services should extend `BaseApiService` for consistent response handling:

```typescript
// frontEnd/src/services/api/base.service.ts
// Provides: get, post, put, patch, delete methods
// Automatically extracts response.data.data from APIResponse wrapper

class MyService extends BaseApiService {
  constructor() {
    super('/my-endpoint');  // Base URL prefix
  }

  async getItem(id: string): Promise<MyItem> {
    return this.get<MyItem>(`/${id}`);  // Calls /my-endpoint/{id}
  }
}
```

### Service Responsibilities
| Service | Responsibility | Backend Prefix |
|---------|---------------|----------------|
| `sessionsService` | Session CRUD, end session | `/sessions` |
| `interactionsService` | Process prompts, get history | `/interactions` |
| `tracesService` | Query N4 traces, cognitive path | `/traces` |
| `risksService` | Query risks only (NOT evaluations) | `/risks` |
| `evaluationsService` | Evaluations + teacher tools | `/risks/evaluation/*`, `/teacher/*` |
| `simulatorsService` | Professional simulators | `/simulators` |
| `gitService` | Git trace analysis | `/git` |
| `reportsService` | Reports + export (Blobs) | `/reports`, `/export` |
| `authService` | Login, register, tokens | `/auth` |
| `adminService` | LLM config, system metrics | `/admin/llm` |

### Central Types Location
Main API types are in `frontEnd/src/types/api.types.ts`:
- Enums: `SessionMode`, `SessionStatus`, `RiskLevel`, `TraceLevel`, `CognitiveIntent`, `CompetencyLevel`
- Interfaces: `SessionResponse`, `InteractionResponse`, `Risk`, `EvaluationReport`, `CognitivePath`, etc.

Service-specific types (not shared) can remain in service files:
- `User`, `LoginRequest` → `auth.service.ts`
- `SimulatorSession` → `simulators.service.ts`
- `TeacherAlert` → `evaluations.service.ts`

### CompetencyLevel Enum (Frontend ↔ Backend)
```typescript
// Frontend MUST use Spanish values to match backend (evaluator.py):
enum CompetencyLevel {
  INICIAL = 'inicial',           // Beginner
  EN_DESARROLLO = 'en_desarrollo', // Developing
  AUTONOMO = 'autonomo',         // Autonomous
  EXPERTO = 'experto',           // Expert
}
// NOT the Dreyfus Model values (novice, advanced_beginner, etc.)
```

### CognitivePath Structure
```typescript
// Backend schema (cognitive_path.py) includes:
interface CognitivePath {
  session_id: string;
  student_id: string;
  activity_id: string;
  start_time: string;
  end_time: string | null;
  summary: CognitivePathSummary;
  phases: CognitivePhase[];
  transitions: CognitiveTransition[];
  ai_dependency_evolution: AIDependencyPoint[];  // Array of {timestamp, ai_involvement}
  strategy_changes: string[];
}
```

### CognitiveTrace N4 Fields
```typescript
// Frontend CognitiveTrace must include all N4 cognitive fields from backend TraceResponse:
interface CognitiveTrace {
  id: string;
  session_id: string;
  student_id: string;       // Required for student tracking
  activity_id: string;      // Required for activity context
  trace_level: TraceLevel | string;
  interaction_type: string;
  cognitive_state: string | null;
  cognitive_intent: string | null;
  content: string;
  ai_involvement: number | null;
  // N4 Cognitive analysis fields
  context: Record<string, any> | null;          // Contextual information
  metadata?: Record<string, any>;               // Mapped from trace_metadata in ORM
  decision_justification: string | null;        // Why decisions were made
  alternatives_considered: string[] | null;     // Alternative approaches considered
  strategy_type: string | null;                 // Problem-solving strategy
  // Relationships
  agent_id: string | null;                      // Which agent processed this
  parent_trace_id: string | null;               // For hierarchical traces
  // Timestamps
  timestamp: string;                            // Primary timestamp field
  created_at?: string;                          // ORM created_at (alias)
}
```

## Session Response trace_count and risk_count

When returning `SessionResponse`, always use repository queries to get accurate counts:

```python
# CORRECT - use repositories for accurate counts
traces = trace_repo.get_by_session(session_id)
risks = risk_repo.get_by_session(session_id)
response = SessionResponse(
    ...
    trace_count=len(traces),
    risk_count=len(risks),
)

# INCORRECT - hasattr may fail with lazy loading
trace_count=len(db_session.traces) if hasattr(db_session, "traces") else 0  # DON'T USE
```

## Parameter Validation in Endpoints

Use Query parameter validation with patterns when possible:

```python
# Example from reports.py - analytics endpoint
VALID_ANALYTICS_PERIODS = {"day", "week", "month", "year"}

@router.get("/analytics")
async def get_learning_analytics(
    period: str = Query(
        default="week",
        description="Time period: day, week, month, year",
        pattern="^(day|week|month|year)$",  # Regex validation
    ),
):
    if period not in VALID_ANALYTICS_PERIODS:
        raise HTTPException(status_code=400, detail=f"Invalid period '{period}'")
```

## Thesis Documentation Reference

The system implements the architecture defined in **Chapter 6 of the doctoral thesis** (`capitulo6.docx`). Key theoretical-implementation mappings:

### 6 AI-Native Submodels (from thesis sections 6.6-6.11)

| Submodel | Thesis Section | Implementation | Purpose |
|----------|---------------|----------------|---------|
| T-IA-Cog | 6.6 | `backend/agents/tutor.py` | Cognitive Tutor (4 modes: Socratic, Explicative, Guided, Metacognitive) |
| E-IA-Proc | 6.7 | `backend/agents/evaluator.py` | Process Evaluator (evaluates HOW, not WHAT) |
| S-IA-X | 6.8 | `backend/agents/simulators.py` | Professional Simulators (6 roles) |
| AR-IA | 6.9 | `backend/agents/risk_analyst.py` | Risk Analyst (5 dimensions: cognitive, ethical, epistemic, technical, governance) |
| GOV-IA | 6.10 | `backend/agents/governance.py` | Governance Agent (UNESCO, ISO/IEC 23894, IEEE compliance) |
| TC-N4 | 6.11 | `backend/agents/traceability.py` | N4 Cognitive Traceability (4 levels) |

### N4 Traceability Levels (from thesis section 6.11.2)

| Level | Name | What it Captures |
|-------|------|------------------|
| N1 | Superficial | Files, deliveries, final code version |
| N2 | Technical | Commits, branches, automated tests |
| N3 | Interactional | Prompts, responses, retries, partial explanations |
| N4 | Cognitive | Intention, decisions, justifications, alternatives, audits, risk |

### Theoretical Foundations (from thesis section 6.6.1)

The T-IA-Cog tutor is grounded in:
- **Distributed Cognition** (Hutchins, 1995): AI as cognitive artifact in socio-technical system
- **Extended Cognition** (Clark & Chalmers, 1998): AI as functional extension of student's thinking
- **Cognitive Load Theory** (Sweller, 1988): Redistribute load toward higher-value processes
- **Self-Regulation** (Zimmerman, 2002): Support planning, monitoring, evaluation

For detailed analysis, see `analisisTesis.md` in repository root.