# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Location

The actual project is located in `activia1-main/` subdirectory. **All commands should be run from there.**

```bash
cd activia1-main
```

## Project Overview

AI-Native MVP for teaching-learning programming with generative AI. Doctoral thesis project implementing **process-based evaluation** (not product-based) with N4-level cognitive traceability.

**Tech Stack**: Python 3.11+/FastAPI backend, React 18+/TypeScript/Vite frontend, PostgreSQL, Redis, Ollama/Phi-3 for LLM.

**Key Concept**: The system evaluates HOW students solve problems (cognitive process), not just the final code output. This is achieved through 6 AI agents and N4-level cognitive traceability.

**Last Updated**: Cortez27 audit (December 2025) - Frontend ESLint/TypeScript fixes (60 problems resolved).

## Quick Commands

```bash
# Navigate to project directory first
cd activia1-main

# Start everything with Docker
docker-compose up -d

# Run backend tests
pytest tests/ -v --cov=backend

# Run frontend dev server
cd frontEnd && npm run dev

# Check API health
curl http://localhost:8000/api/v1/health
```

## Common Development Commands

### Docker (Recommended)
```bash
docker-compose up -d                    # Start full stack
docker-compose logs -f api              # View API logs
docker-compose down                     # Stop services
docker-compose --profile debug up -d    # Includes pgAdmin + Redis Commander
docker-compose --profile monitoring up -d # Includes Prometheus + Grafana
```

### Backend (Local Development)
```bash
pip install -r requirements.txt
python -m backend                       # Runs uvicorn on :8000

# Run database migrations
python -m backend.database.migrations.add_n4_dimensions
python -m backend.database.migrations.add_cortez_audit_fixes
```

### Backend Testing
```bash
pytest tests/ -v --cov=backend          # All tests (70% min coverage required)
pytest tests/ -v -m "unit"              # Unit tests only
pytest tests/ -v -m "integration"       # Integration tests
pytest tests/test_agents.py -v          # Single file
pytest tests/test_agents.py::test_tutor_mode -v  # Single test function
```

Test markers: `unit`, `integration`, `cognitive`, `agents`, `models`, `gateway`, `slow`

### Frontend
```bash
cd frontEnd
npm install && npm run dev              # Dev server
npm run build                           # Production build
npm run lint                            # ESLint
npm run type-check                      # TypeScript check
npm test                                # Vitest tests
npm run e2e                             # Playwright E2E tests
```

### Make Commands (WSL/Git Bash on Windows)
```bash
make dev                    # Start full stack
make test                   # All tests with coverage
make lint                   # pylint + flake8
make format                 # black formatting
make health-check           # Verify all services
```

## Architecture

### Request Flow
```
Client -> FastAPI Router -> AIGateway (STATELESS) -> CRPE -> Governance Agent
    -> Target Agent -> LLM Provider -> Response Generator -> TC-N4 Traceability
    -> Risk Analyzer -> Repositories (PostgreSQL) -> Response
```

### 6 AI Agents (`backend/agents/`)
| Agent | File | Purpose |
|-------|------|---------|
| T-IA-Cog | `tutor.py` | Cognitive Tutor (4 modes: Socratic, Explicative, Guided, Metacognitive) |
| E-IA-Proc | `evaluator.py` | Process Evaluator |
| S-IA-X | `simulators.py` | Professional Role Simulators (6 roles) |
| AR-IA | `risk_analyst.py` | Risk Analyst (5 dimensions) |
| GOV-IA | `governance.py` | Governance & Delegation |
| TC-N4 | `traceability.py` | N4-level Traceability |

### Key Files
| Component | Path |
|-----------|------|
| AI Gateway (orchestrator) | `backend/core/ai_gateway.py` |
| Cognitive Engine (CRPE) | `backend/core/cognitive_engine.py` |
| LLM Factory | `backend/llm/factory.py` |
| ORM Models | `backend/database/models.py` |
| API Main | `backend/api/main.py` |
| Frontend API Services | `frontEnd/src/services/api/` |

## Critical Development Rules

### ORM vs Pydantic Field Mappings
```python
# Enum storage - always lowercase strings in DB:
session.status = "active"        # NOT "ACTIVE"
risk.risk_level = "critical"     # NOT "CRITICAL"

# Score scales:
evaluation.overall_score         # 0-10 scale
session_summary.overall_score    # 0-1 normalized
risk_analysis.overall_score      # 0-100 percentage
```

### Frontend-Backend Type Alignment
```typescript
// InteractionCreate - MUST use 'prompt' not 'student_input'
const interaction = { session_id: "...", prompt: "user message", context: {} };

// SessionMode - use enum, not string literal
import { SessionMode } from '../types';
const session = { mode: SessionMode.TUTOR };  // CORRECT
```

### AIGateway is STATELESS
- All state persists to PostgreSQL via repositories
- No in-memory sessions/traces/risks
- Supports horizontal scaling

### LLM Provider Methods are ASYNC
```python
response = await provider.generate(messages, temperature=0.7)  # CORRECT
```

### Authentication Required
Most endpoints require authentication after cortez audits:
- Sessions, interactions, evaluations, traces, risks endpoints
- Teacher role required for activities management and reports

## Environment Configuration

Key `.env` variables (see `.env.example` for full template):

**Required:**
- `POSTGRES_PASSWORD`, `REDIS_PASSWORD` - Database credentials
- `JWT_SECRET_KEY`, `SECRET_KEY` - Generate with `make generate-secrets`

**LLM:**
- `LLM_PROVIDER`: `ollama` | `mock` | `openai`
- `OLLAMA_BASE_URL`: `http://localhost:11434` (local) or `http://ollama:11434` (Docker)
- `OLLAMA_MODEL`: `phi3` (recommended)

## Documentation

**Essential Reading:**
- `docs/Misagentes/integrador.md` - Complete multi-agent system documentation
- `docs/api/README_API.md` - REST API reference
- `docs/llm/OLLAMA_QUICKSTART.md` - LLM setup guide

**User Guides:**
- `GUIA_ESTUDIANTE.md`, `GUIA_DOCENTE.md`, `GUIA_ADMINISTRADOR.md`

## Recent Fixes (Cortez27)

Key frontend ESLint/TypeScript fixes (60 problems resolved):
- **Replaced `any` with proper types** (36 errors): Use `unknown` with type guards, proper interfaces
- **Removed unused imports/variables** (19 warnings): Clean imports across pages and services
- **Fixed React Hook warnings** (2): Proper dependency arrays, eslint-disable where intentional
- **Fixed Fast Refresh warnings** (3): eslint-disable for context hook exports

### Cortez25 (Backend Startup)
- **JSONB/SQLite Compatibility**: `JSONBCompatible` type for cross-database support
- **User Model Consolidation**: Removed duplicate `User` class, use `UserDB` from `database.models`
- **Self-Referential Relationship Fix**: `CognitiveTraceDB.parent_trace` uses string reference for `remote_side`

## Detailed Documentation

For comprehensive guidance including all critical rules, field mappings, audit history (27 audits), and detailed architecture, see:

**`activia1-main/CLAUDE.md`** (700+ lines of detailed guidance)

This file contains:
- Complete ORM vs Pydantic field mappings
- All 102 API routes across 22 categories
- N4 Traceability levels and cognitive dimensions
- Governance semaphore system (verde/amarillo/rojo)
- Tutor pedagogical rules (4 unbreakable rules)
- Risk dimensions (5D) and risk types (16 types)