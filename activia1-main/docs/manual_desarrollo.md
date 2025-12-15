# 👨‍💻 Manual de Desarrollo - AI-Native MVP

## Guía Completa para Contribuyentes y Desarrolladores

Esta guía te ayudará a contribuir al desarrollo del **Ecosistema AI-Native**, entendiendo la arquitectura del código, convenciones, patrones de diseño y proceso de contribución.

---

## 📚 Índice

1. [Introducción](#introducción)
2. [Setup del Entorno de Desarrollo](#setup-del-entorno-de-desarrollo)
3. [Arquitectura del Código](#arquitectura-del-código)
4. [Convenciones de Código](#convenciones-de-código)
5. [Patrones de Diseño Utilizados](#patrones-de-diseño-utilizados)
6. [Testing](#testing)
7. [Agregar un Nuevo Agente](#agregar-un-nuevo-agente)
8. [Agregar un Nuevo LLM Provider](#agregar-un-nuevo-llm-provider)
9. [Agregar un Endpoint API](#agregar-un-endpoint-api)
10. [Debugging](#debugging)
11. [Pull Requests y Code Review](#pull-requests-y-code-review)
12. [Troubleshooting](#troubleshooting)

---

## Introducción

### ¿Quién puede contribuir?

- ✅ Desarrolladores backend (Python, FastAPI, SQLAlchemy)
- ✅ Desarrolladores frontend (React, TypeScript)
- ✅ Investigadores (pedagogía, IA, educación)
- ✅ Estudiantes (tesistas, pasantes)
- ✅ Docentes (casos de uso, mejoras pedagógicas)

### Stack Tecnológico

**Backend**:
- Python 3.12+
- FastAPI (async web framework)
- SQLAlchemy 2.0 (ORM)
- Pydantic 2.0 (validación, serialización)
- Pytest (testing)
- OpenAI SDK, Google Generative AI (LLM providers)

**Frontend**:
- React 18.2
- TypeScript 5.2
- Vite 5.0 (bundler)
- Axios (HTTP client)
- React Markdown

**Infraestructura**:
- PostgreSQL 15+ (producción)
- Redis 7+ (cache)
- Docker / Kubernetes
- Nginx (reverse proxy)

---

## Setup del Entorno de Desarrollo

### 1. Fork y Clonar Repositorio

```bash
# Fork en GitHub (botón "Fork")
# Clonar tu fork
git clone https://github.com/TU_USUARIO/ai-native-mvp.git
cd ai-native-mvp

# Agregar upstream
git remote add upstream https://github.com/REPO_ORIGINAL/ai-native-mvp.git
```

### 2. Crear Entorno Virtual

```bash
python3.12 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# o
.venv\Scripts\activate  # Windows

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Herramientas de desarrollo
```

### 3. Configurar Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install

# Hooks configurados:
# - black (formatting)
# - isort (imports)
# - flake8 (linting)
# - mypy (type checking)
```

### 4. Inicializar Base de Datos de Desarrollo

```bash
cp .env.example .env
# Editar .env con configuración de desarrollo

python scripts/init_database.py
```

### 5. Ejecutar Tests

```bash
pytest tests/ -v --cov
# Debe pasar 100% de tests
```

### 6. Iniciar Backend (modo desarrollo)

```bash
python scripts/run_api.py
# O con hot-reload:
uvicorn src.ai_native_mvp.api.main:app --reload
```

### 7. Iniciar Frontend (opcional)

```bash
cd frontEnd
npm install
npm run dev
```

---

## Arquitectura del Código

### Estructura de Directorios (Backend)

```
src/ai_native_mvp/
├── __init__.py              # Exports públicos
├── __main__.py              # Entry point CLI
├── cli.py                   # CLI interactivo
│
├── api/                     # REST API (FastAPI)
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── deps.py              # Dependency injection
│   ├── exceptions.py        # Custom exceptions
│   ├── config.py            # API configuration
│   │
│   ├── middleware/          # Middlewares
│   │   ├── error_handler.py
│   │   ├── logging.py
│   │   └── rate_limiter.py
│   │
│   ├── routers/             # API endpoints (controllers)
│   │   ├── health.py
│   │   ├── sessions.py
│   │   ├── interactions.py  # ⭐ Main endpoint
│   │   ├── traces.py
│   │   └── risks.py
│   │
│   └── schemas/             # DTOs (request/response models)
│       ├── common.py
│       ├── session.py
│       └── interaction.py
│
├── core/                    # Business logic core
│   ├── ai_gateway.py        # ⭐ Orchestrator (C1-C6)
│   ├── cognitive_engine.py  # CRPE (cognitive reasoning)
│   └── cache.py             # LLM response cache
│
├── agents/                  # 6 AI-Native submodels
│   ├── __init__.py
│   ├── tutor.py             # T-IA-Cog
│   ├── evaluator.py         # E-IA-Proc
│   ├── simulators.py        # S-IA-X
│   ├── risk_analyst.py      # AR-IA
│   ├── governance.py        # GOV-IA
│   └── traceability.py      # TC-N4
│
├── models/                  # Pydantic models (domain)
│   ├── __init__.py
│   ├── trace.py             # CognitiveTrace, TraceSequence
│   ├── risk.py              # Risk, RiskReport
│   └── evaluation.py        # EvaluationReport
│
├── database/                # Persistence layer (SQLAlchemy)
│   ├── __init__.py
│   ├── base.py              # Declarative base
│   ├── config.py            # DB config & session management
│   ├── models.py            # ORM models
│   ├── repositories.py      # Repository pattern
│   └── transaction.py       # Transaction management
│
└── llm/                     # LLM provider abstraction
    ├── __init__.py
    ├── base.py              # LLMProvider interface
    ├── mock.py              # Mock provider
    ├── openai_provider.py   # OpenAI integration
    ├── gemini_provider.py   # Google Gemini integration
    └── factory.py           # Provider factory
```

### Flujo de Datos (Request → Response)

```
1. HTTP Request → FastAPI router (api/routers/interactions.py)
2. Dependency injection (api/deps.py) → Repositories + Gateway
3. AIGateway.process_interaction() (core/ai_gateway.py)
   ├─ 3.1. CognitiveEngine.classify() → Detect cognitive state
   ├─ 3.2. GovernanceAgent.check_policies() → Validate
   ├─ 3.3. TrazabilidadN4.capture_input() → Save trace
   ├─ 3.4. Route to agent (Tutor, Simulator, etc.)
   ├─ 3.5. LLMProvider.generate() → Get AI response
   ├─ 3.6. TrazabilidadN4.capture_output() → Save trace
   └─ 3.7. RiskAnalyst.analyze() → Detect risks (async)
4. Persist via Repositories (database/repositories.py)
5. HTTP Response → JSON (api/schemas/interaction.py)
```

---

## Convenciones de Código

### 1. Naming Conventions

**Python (PEP 8)**:
```python
# Classes: PascalCase
class CognitiveEngine:
    pass

# Functions/methods: snake_case
def process_interaction(session_id: str) -> dict:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Private: prefix with _
def _internal_helper():
    pass

# Very private: prefix with __
def __double_underscore_for_name_mangling():
    pass
```

**TypeScript**:
```typescript
// Interfaces: PascalCase with I prefix (optional)
interface SessionResponse {
  id: string;
  studentId: string;
}

// Types: PascalCase
type AgentType = 'TUTOR' | 'EVALUATOR' | 'SIMULATOR';

// Functions: camelCase
function processInteraction(sessionId: string): Promise<void> {
  // ...
}

// Constants: UPPER_SNAKE_CASE
const MAX_MESSAGE_LENGTH = 5000;
```

### 2. Type Hints (Python)

**OBLIGATORIO** usar type hints en:
- Parámetros de funciones
- Retorno de funciones
- Atributos de clase

```python
from typing import List, Optional, Dict, Any

def get_traces_by_session(
    session_id: str,
    trace_level: Optional[str] = None
) -> List[CognitiveTrace]:
    """
    Obtiene trazas de una sesión.

    Args:
        session_id: ID de la sesión
        trace_level: Nivel de traza (N1, N2, N3, N4) o None para todos

    Returns:
        Lista de trazas cognitivas

    Raises:
        SessionNotFoundError: Si la sesión no existe
    """
    # Implementation
    pass
```

### 3. Docstrings

**Formato**: Google Style

```python
def complex_function(param1: str, param2: int) -> Dict[str, Any]:
    """Descripción breve de la función en una línea.

    Descripción más detallada en múltiples líneas si es necesario.
    Explica qué hace la función, no cómo lo hace (eso está en el código).

    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2

    Returns:
        Diccionario con las claves:
            - 'result': El resultado del cálculo
            - 'metadata': Información adicional

    Raises:
        ValueError: Si param2 es negativo
        DatabaseError: Si hay error de conexión a DB

    Example:
        >>> complex_function("test", 42)
        {'result': 'ok', 'metadata': {}}
    """
    if param2 < 0:
        raise ValueError("param2 must be non-negative")

    return {'result': 'ok', 'metadata': {}}
```

### 4. Imports

**Orden** (aplicado automáticamente por `isort`):
1. Standard library
2. Third-party packages
3. Local imports

```python
# Standard library
import os
import sys
from datetime import datetime
from typing import List, Optional

# Third-party
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Local
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import SessionRepository
from src.ai_native_mvp.models.trace import CognitiveTrace
```

### 5. Formatting

Usar **Black** con configuración default:

```bash
black src/ tests/
```

Configuración en `pyproject.toml`:

```toml
[tool.black]
line-length = 100
target-version = ['py312']
```

### 6. Linting

Usar **Flake8**:

```bash
flake8 src/ tests/
```

Configuración en `.flake8`:

```ini
[flake8]
max-line-length = 100
exclude = .venv,__pycache__,.git
ignore = E203,W503  # Compatibilidad con Black
```

### 7. Type Checking

Usar **mypy**:

```bash
mypy src/
```

Configuración en `mypy.ini`:

```ini
[mypy]
python_version = 3.12
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

---

## Patrones de Diseño Utilizados

### 1. Repository Pattern

**Dónde**: `database/repositories.py`

**Objetivo**: Abstraer operaciones de base de datos.

```python
# BAD (acceso directo a ORM)
def get_session(session_id: str, db: Session) -> SessionDB:
    return db.query(SessionDB).filter(SessionDB.id == session_id).first()

# GOOD (Repository pattern)
class SessionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, session_id: str) -> Optional[SessionDB]:
        return self.db.query(SessionDB).filter(SessionDB.id == session_id).first()

# Uso
with get_db_session() as db:
    session_repo = SessionRepository(db)
    session = session_repo.get("session_123")
```

### 2. Factory Pattern

**Dónde**: `llm/factory.py`

**Objetivo**: Crear instancias de providers dinámicamente.

```python
class LLMProviderFactory:
    _providers: Dict[str, Type[LLMProvider]] = {}

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]):
        cls._providers[name] = provider_class

    @classmethod
    def create(cls, provider_name: str, config: Dict[str, Any]) -> LLMProvider:
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")

        provider_class = cls._providers[provider_name]
        return provider_class(config)

# Registro
LLMProviderFactory.register_provider('openai', OpenAIProvider)
LLMProviderFactory.register_provider('mock', MockLLMProvider)

# Uso
provider = LLMProviderFactory.create('openai', {'api_key': '...'})
```

### 3. Strategy Pattern

**Dónde**: `agents/tutor.py`, `agents/evaluator.py`

**Objetivo**: Intercambiar algoritmos/estrategias dinámicamente.

```python
class TutorStrategy(ABC):
    @abstractmethod
    def generate_response(self, prompt: str, context: dict) -> str:
        pass

class SocraticStrategy(TutorStrategy):
    def generate_response(self, prompt: str, context: dict) -> str:
        # Genera preguntas socráticas
        return "¿Por qué elegiste esa estructura de datos?"

class ExplanationStrategy(TutorStrategy):
    def generate_response(self, prompt: str, context: dict) -> str:
        # Genera explicaciones conceptuales
        return "Una cola circular funciona..."

# Uso en TutorAgent
class TutorCognitivoAgent:
    def __init__(self, strategy: TutorStrategy):
        self.strategy = strategy

    def respond(self, prompt: str) -> str:
        return self.strategy.generate_response(prompt, {})
```

### 4. Dependency Injection

**Dónde**: `api/deps.py`, toda la API

**Objetivo**: Desacoplar componentes, facilitar testing.

```python
# api/deps.py
def get_db() -> Generator[Session, None, None]:
    with get_db_session() as session:
        yield session

def get_session_repository(db: Session = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db)

def get_ai_gateway(
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    # ... other repos
) -> AIGateway:
    return AIGateway(
        session_repo=session_repo,
        trace_repo=trace_repo,
        # ...
    )

# api/routers/interactions.py
@router.post("/")
async def process_interaction(
    request: InteractionRequest,
    gateway: AIGateway = Depends(get_ai_gateway),
):
    result = gateway.process_interaction(...)
    return result
```

### 5. Singleton Pattern (Lazy)

**Dónde**: `core/ai_gateway.py`, `database/config.py`

**Objetivo**: Una sola instancia compartida.

```python
_db_config: Optional[DatabaseConfig] = None

def get_db_config() -> DatabaseConfig:
    global _db_config
    if _db_config is None:
        _db_config = DatabaseConfig()
    return _db_config
```

---

## Testing

### Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidos
├── test_models.py           # Tests de Pydantic models
├── test_cognitive_engine.py # Tests del CRPE
├── test_agents.py           # Tests de agentes
├── test_gateway.py          # Tests de AIGateway
├── test_repositories.py     # Tests de repositories
└── test_api_endpoints.py    # Tests de API (integration)
```

### Fixtures Importantes (conftest.py)

```python
import pytest
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import SessionRepository
from src.ai_native_mvp.llm.mock import MockLLMProvider

@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing"""
    return MockLLMProvider()

@pytest.fixture
def test_db():
    """Test database session"""
    with get_db_session() as session:
        yield session
        session.rollback()  # Rollback after test

@pytest.fixture
def session_repo(test_db):
    """SessionRepository with test DB"""
    return SessionRepository(test_db)

@pytest.fixture
def sample_session(session_repo):
    """Create a sample session"""
    return session_repo.create(
        student_id="test_student",
        activity_id="test_activity",
        mode="TUTOR"
    )
```

### Escribir Tests

**Unit Test** (función pura):

```python
# tests/test_models.py
def test_cognitive_trace_validation():
    """Test CognitiveTrace validates required fields"""
    from src.ai_native_mvp.models.trace import CognitiveTrace, TraceLevel

    # Valid trace
    trace = CognitiveTrace(
        session_id="session_123",
        student_id="student_001",
        activity_id="activity_001",
        trace_level=TraceLevel.N4_COGNITIVO,
        content="Test content"
    )
    assert trace.session_id == "session_123"

    # Invalid trace (missing session_id)
    with pytest.raises(ValidationError):
        CognitiveTrace(
            student_id="student_001",
            activity_id="activity_001",
            content="Test"
        )
```

**Integration Test** (con DB):

```python
# tests/test_repositories.py
def test_session_repository_create(session_repo):
    """Test SessionRepository.create()"""
    session = session_repo.create(
        student_id="test_student",
        activity_id="test_activity",
        mode="TUTOR"
    )

    assert session.id is not None
    assert session.student_id == "test_student"
    assert session.status == "ACTIVE"
```

**API Test** (end-to-end):

```python
# tests/test_api_endpoints.py
from fastapi.testclient import TestClient
from src.ai_native_mvp.api.main import app

client = TestClient(app)

def test_create_session_endpoint():
    """Test POST /api/v1/sessions"""
    response = client.post(
        "/api/v1/sessions",
        json={
            "student_id": "test_student",
            "activity_id": "test_activity",
            "mode": "TUTOR"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "id" in data["data"]
```

### Ejecutar Tests

```bash
# Todos los tests
pytest tests/ -v

# Con coverage
pytest tests/ -v --cov

# Tests específicos
pytest tests/test_agents.py -v

# Por markers
pytest -m "unit" -v          # Solo unit tests
pytest -m "integration" -v   # Solo integration tests

# Con output
pytest tests/ -v -s  # -s muestra prints
```

### Coverage Mínimo

**Target**: 70% (configurado en `pytest.ini`)

```bash
pytest tests/ --cov --cov-report=html
# Abrir htmlcov/index.html en navegador
```

---

## Agregar un Nuevo Agente

**Ejemplo**: Agregar "A-IA-Doc" (Agente Documentador Automático)

### Paso 1: Crear archivo del agente

```python
# src/ai_native_mvp/agents/documenter.py

from typing import Optional, Dict, Any
from src.ai_native_mvp.llm.base import LLMProvider
from src.ai_native_mvp.models.trace import CognitiveTrace

class AutoDocumenterAgent:
    """
    A-IA-Doc: Agente Documentador Automático

    Genera documentación técnica a partir del código y trazas del estudiante.
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm_provider = llm_provider or self._get_default_provider()

    def _get_default_provider(self) -> LLMProvider:
        from src.ai_native_mvp.llm import LLMProviderFactory
        return LLMProviderFactory.create_from_env()

    def generate_documentation(
        self,
        code: str,
        traces: list[CognitiveTrace],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera documentación técnica del código.

        Args:
            code: Código fuente a documentar
            traces: Trazas cognitivas del proceso
            context: Contexto adicional

        Returns:
            Documentación en formato Markdown
        """
        # 1. Analizar código
        analysis = self._analyze_code(code)

        # 2. Reconstruir razonamiento desde trazas
        reasoning = self._extract_reasoning_from_traces(traces)

        # 3. Generar documentación con LLM
        prompt = self._build_documentation_prompt(code, analysis, reasoning)
        documentation = self.llm_provider.generate(
            messages=[
                {"role": "system", "content": "Eres un documentador técnico experto."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Más determinístico para docs
        )

        return documentation.content

    def _analyze_code(self, code: str) -> Dict[str, Any]:
        """Analiza estructura del código"""
        # TODO: Usar AST para análisis estático
        return {
            "functions": [],
            "classes": [],
            "complexity": 0
        }

    def _extract_reasoning_from_traces(self, traces: list[CognitiveTrace]) -> str:
        """Extrae razonamiento de trazas N4"""
        reasoning_steps = []
        for trace in traces:
            if trace.trace_level == "n4_cognitivo":
                reasoning_steps.append(trace.content)
        return "\n".join(reasoning_steps)

    def _build_documentation_prompt(
        self,
        code: str,
        analysis: Dict[str, Any],
        reasoning: str
    ) -> str:
        """Construye prompt para LLM"""
        return f"""
Genera documentación técnica para el siguiente código:

```python
{code}
```

Análisis estático:
{analysis}

Razonamiento del estudiante:
{reasoning}

Formato de salida:
# Documentación Técnica

## Descripción General
[Explicación de qué hace el código]

## Decisiones de Diseño
[Por qué se tomaron ciertas decisiones]

## Complejidad
[Análisis de complejidad temporal/espacial]

## Ejemplo de Uso
[Código de ejemplo]
"""
```

### Paso 2: Exportar en __init__.py

```python
# src/ai_native_mvp/agents/__init__.py

from .tutor import TutorCognitivoAgent
from .evaluator import EvaluadorProcesoAgent
from .simulators import SimuladorProfesionalAgent
from .risk_analyst import AnalistaRiesgosAgent
from .governance import GobernanzaAgent
from .traceability import TrazabilidadN4Agent
from .documenter import AutoDocumenterAgent  # NUEVO

__all__ = [
    'TutorCognitivoAgent',
    'EvaluadorProcesoAgent',
    'SimuladorProfesionalAgent',
    'AnalistaRiesgosAgent',
    'GobernanzaAgent',
    'TrazabilidadN4Agent',
    'AutoDocumenterAgent',  # NUEVO
]
```

### Paso 3: Integrar con AIGateway

```python
# src/ai_native_mvp/core/ai_gateway.py

class AIGateway:
    def __init__(self, ...):
        # ... existing agents
        self.documenter = AutoDocumenterAgent(llm_provider=self.llm_provider)

    def generate_documentation(self, session_id: str) -> str:
        """Genera documentación de una sesión"""
        # Obtener código y trazas
        traces = self.trace_repo.get_by_session(session_id)
        code = self._extract_final_code(traces)

        # Generar documentación
        documentation = self.documenter.generate_documentation(
            code=code,
            traces=traces
        )

        return documentation
```

### Paso 4: Agregar Endpoint API (opcional)

```python
# src/ai_native_mvp/api/routers/documentation.py

from fastapi import APIRouter, Depends
from src.ai_native_mvp.core.ai_gateway import AIGateway
from ..deps import get_ai_gateway
from ..schemas.common import APIResponse

router = APIRouter(prefix="/documentation", tags=["Documentation"])

@router.get("/{session_id}")
async def generate_documentation(
    session_id: str,
    gateway: AIGateway = Depends(get_ai_gateway)
) -> APIResponse[str]:
    """Genera documentación técnica de una sesión"""
    documentation = gateway.generate_documentation(session_id)
    return APIResponse(success=True, data=documentation)
```

Registrar router en `main.py`:

```python
from .routers import documentation
app.include_router(documentation.router, prefix="/api/v1")
```

### Paso 5: Escribir Tests

```python
# tests/test_documenter.py

import pytest
from src.ai_native_mvp.agents.documenter import AutoDocumenterAgent

@pytest.fixture
def documenter(mock_llm_provider):
    return AutoDocumenterAgent(llm_provider=mock_llm_provider)

def test_generate_documentation(documenter, sample_traces):
    """Test documentation generation"""
    code = """
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)
"""

    documentation = documenter.generate_documentation(code, sample_traces)

    assert "Documentación Técnica" in documentation
    assert "factorial" in documentation
```

### Paso 6: Documentar

Agregar sección en `README_MVP.md`:

```markdown
### A-IA-Doc: Agente Documentador Automático

**Propósito**: Genera documentación técnica automática del código del estudiante.

**Características**:
- Análisis estático del código (AST)
- Extracción de razonamiento desde trazas N4
- Generación de documentación con LLM
- Formato Markdown profesional

**Uso**:
```python
from src.ai_native_mvp.agents import AutoDocumenterAgent

documenter = AutoDocumenterAgent()
documentation = documenter.generate_documentation(code, traces)
print(documentation)
```
```

---

## Agregar un Nuevo LLM Provider

**Ejemplo**: Agregar soporte para Anthropic Claude

### Paso 1: Crear provider

```python
# src/ai_native_mvp/llm/anthropic_provider.py

import os
from typing import List, Optional, Iterator
from anthropic import Anthropic, Stream
from .base import LLMProvider, LLMMessage, LLMResponse

class AnthropicProvider(LLMProvider):
    """Provider para Anthropic Claude"""

    def __init__(self, config: Optional[dict] = None):
        config = config or {}
        self.api_key = config.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
        self.model = config.get('model', 'claude-3-sonnet-20240229')
        self.client = Anthropic(api_key=self.api_key)

    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> LLMResponse:
        """Genera respuesta con Claude"""
        # Convertir formato
        claude_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role != "system"
        ]

        # System prompt por separado
        system_prompt = next(
            (msg.content for msg in messages if msg.role == "system"),
            None
        )

        # Llamada a Claude
        response = self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=claude_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return LLMResponse(
            content=response.content[0].text,
            model=self.model,
            usage={
                'prompt_tokens': response.usage.input_tokens,
                'completion_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }
        )

    def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Iterator[str]:
        """Genera respuesta en streaming"""
        # Similar pero con stream=True
        with self.client.messages.stream(
            model=self.model,
            messages=[...],
            temperature=temperature,
            max_tokens=max_tokens
        ) as stream:
            for text in stream.text_stream:
                yield text

    def count_tokens(self, text: str) -> int:
        """Cuenta tokens (aproximado)"""
        # Claude usa ~1 token por 4 caracteres
        return len(text) // 4

    def validate_config(self) -> bool:
        """Valida configuración"""
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required")
        return True

    def get_model_info(self) -> dict:
        """Retorna información del modelo"""
        return {
            'provider': 'anthropic',
            'model': self.model,
            'max_tokens': 4096,
            'supports_streaming': True
        }
```

### Paso 2: Registrar en Factory

```python
# src/ai_native_mvp/llm/factory.py

from .anthropic_provider import AnthropicProvider

# Registro
LLMProviderFactory.register_provider('anthropic', AnthropicProvider)

# En create_from_env()
elif provider_name == 'anthropic':
    return AnthropicProvider({
        'api_key': os.getenv('ANTHROPIC_API_KEY'),
        'model': os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
    })
```

### Paso 3: Agregar a requirements.txt

```bash
anthropic>=0.7.0
```

### Paso 4: Documentar en .env.example

```bash
# Anthropic Claude configuration
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_TEMPERATURE=0.7
ANTHROPIC_MAX_TOKENS=4096
```

### Paso 5: Tests

```python
# tests/test_anthropic_provider.py

import pytest
from src.ai_native_mvp.llm.anthropic_provider import AnthropicProvider
from src.ai_native_mvp.llm.base import LLMMessage, LLMRole

@pytest.mark.skipif(
    not os.getenv('ANTHROPIC_API_KEY'),
    reason="ANTHROPIC_API_KEY not set"
)
def test_anthropic_generate():
    """Test Claude generation"""
    provider = AnthropicProvider()

    messages = [
        LLMMessage(role=LLMRole.SYSTEM, content="You are a helpful assistant"),
        LLMMessage(role=LLMRole.USER, content="Say hello")
    ]

    response = provider.generate(messages)

    assert response.content
    assert "hello" in response.content.lower()
    assert response.usage['total_tokens'] > 0
```

---

## Agregar un Endpoint API

**Ejemplo**: Endpoint para obtener estadísticas de un estudiante

### Paso 1: Crear Schema (DTO)

```python
# src/ai_native_mvp/api/schemas/statistics.py

from pydantic import BaseModel
from typing import Dict

class StudentStatistics(BaseModel):
    student_id: str
    total_sessions: int
    total_interactions: int
    average_ai_dependency: float
    total_risks: int
    competency_level: str
    competency_evolution: Dict[str, float]  # Date → score
```

### Paso 2: Crear Router

```python
# src/ai_native_mvp/api/routers/statistics.py

from fastapi import APIRouter, Depends
from ..deps import get_session_repository, get_trace_repository, get_risk_repository
from ..schemas.statistics import StudentStatistics
from ..schemas.common import APIResponse

router = APIRouter(prefix="/statistics", tags=["Statistics"])

@router.get("/student/{student_id}")
async def get_student_statistics(
    student_id: str,
    session_repo = Depends(get_session_repository),
    trace_repo = Depends(get_trace_repository),
    risk_repo = Depends(get_risk_repository)
) -> APIResponse[StudentStatistics]:
    """Obtiene estadísticas de un estudiante"""

    # Obtener datos
    sessions = session_repo.get_by_student(student_id)
    traces = trace_repo.get_by_student(student_id)
    risks = risk_repo.get_by_student(student_id)

    # Calcular estadísticas
    total_sessions = len(sessions)
    total_interactions = len([t for t in traces if t.interaction_type == "student_prompt"])

    ai_dependencies = [t.ai_involvement for t in traces if t.ai_involvement is not None]
    average_ai_dependency = sum(ai_dependencies) / len(ai_dependencies) if ai_dependencies else 0.0

    # Nivel de competencia (último)
    # TODO: Implementar lógica real
    competency_level = "EN_DESARROLLO"

    # Evolución (por fecha)
    competency_evolution = {}  # TODO

    stats = StudentStatistics(
        student_id=student_id,
        total_sessions=total_sessions,
        total_interactions=total_interactions,
        average_ai_dependency=average_ai_dependency,
        total_risks=len(risks),
        competency_level=competency_level,
        competency_evolution=competency_evolution
    )

    return APIResponse(success=True, data=stats)
```

### Paso 3: Registrar Router

```python
# src/ai_native_mvp/api/main.py

from .routers import statistics

app.include_router(statistics.router, prefix="/api/v1")
```

### Paso 4: Tests

```python
# tests/test_api_statistics.py

from fastapi.testclient import TestClient
from src.ai_native_mvp.api.main import app

client = TestClient(app)

def test_get_student_statistics():
    """Test GET /api/v1/statistics/student/{id}"""
    response = client.get("/api/v1/statistics/student/test_student")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_sessions" in data["data"]
```

---

## Debugging

### 1. Debugging en VSCode

Configurar `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.ai_native_mvp.api.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000"
      ],
      "jinja": true,
      "justMyCode": false
    },
    {
      "name": "Python: Current File",
      "type": "python",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal"
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "${file}",
        "-v",
        "-s"
      ]
    }
  ]
}
```

### 2. Logs de Debugging

```python
import logging

logger = logging.getLogger(__name__)

def process_interaction(...):
    logger.debug(f"Processing interaction: session_id={session_id}")

    try:
        result = gateway.process_interaction(...)
        logger.info(f"Interaction processed successfully: {result['trace_id']}")
        return result
    except Exception as e:
        logger.error(f"Error processing interaction", exc_info=True, extra={
            'session_id': session_id,
            'error': str(e)
        })
        raise
```

### 3. Debugging SQL Queries

```python
# Activar SQL logging
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Verás queries en consola:
# INFO sqlalchemy.engine.Engine SELECT sessions.id, sessions.student_id ...
```

### 4. IPython para Debugging Interactivo

```bash
pip install ipython

# En código, agregar:
import IPython; IPython.embed()
# Pausa ejecución y abre shell interactivo
```

---

## Pull Requests y Code Review

### Proceso de Contribución

1. **Crear issue** (opcional pero recomendado)
2. **Crear branch** desde `main`:
```bash
git checkout main
git pull upstream main
git checkout -b feature/nombre-descriptivo
```

3. **Desarrollar** con commits frecuentes:
```bash
git add .
git commit -m "feat: agregar agente documentador automático"
git push origin feature/nombre-descriptivo
```

4. **Abrir Pull Request** en GitHub:
   - Título claro
   - Descripción detallada
   - Referencias a issues
   - Screenshots (si UI)

5. **Code Review** (esperar feedback)

6. **Merge** (después de aprobación)

### Convenciones de Commits (Conventional Commits)

```bash
# Formato
<tipo>(<scope>): <descripción>

[cuerpo opcional]

[footer opcional]
```

**Tipos**:
- `feat`: Nueva funcionalidad
- `fix`: Bug fix
- `docs`: Documentación
- `style`: Formatting (sin cambios de código)
- `refactor`: Refactoring
- `test`: Agregar tests
- `chore`: Mantenimiento (deps, build, etc.)

**Ejemplos**:
```bash
feat(agents): agregar agente documentador automático

fix(api): corregir validación de session_id en endpoint /interactions

docs(readme): actualizar sección de instalación

refactor(database): simplificar lógica de repositories

test(agents): agregar tests para TutorAgent
```

### Checklist Pre-PR

Antes de abrir PR, verificar:

- [ ] Tests pasan (`pytest tests/ -v`)
- [ ] Coverage >70% (`pytest --cov`)
- [ ] Linting OK (`flake8 src/`)
- [ ] Formatting OK (`black src/ --check`)
- [ ] Type checking OK (`mypy src/`)
- [ ] Documentación actualizada
- [ ] CHANGELOG.md actualizado (si corresponde)

---

## Troubleshooting

### Problema: Tests fallan localmente pero pasan en CI

**Causa**: Diferencias de ambiente (Python version, dependencias).

**Solución**:
```bash
# Recrear venv limpio
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

### Problema: Import errors

**Causa**: Python path mal configurado.

**Solución**:
```bash
# Agregar proyecto al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# O ejecutar con python -m
python -m pytest tests/
```

### Problema: Pre-commit hooks fallan

**Solución**:
```bash
# Ejecutar manualmente
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/

# O saltear (NO recomendado)
git commit --no-verify -m "..."
```

---

## Recursos Adicionales

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Pydantic V2**: https://docs.pydantic.dev/2.0/
- **Pytest**: https://docs.pytest.org/

---

**¡Gracias por contribuir! 🚀**

**Mag. en Ing. de Software Alberto Cortez**
Universidad Tecnológica Nacional