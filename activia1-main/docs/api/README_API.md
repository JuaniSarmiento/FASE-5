# AI-Native MVP - REST API Documentation

**API REST para el sistema de enseñanza-aprendizaje de programación con IA generativa**

## Inicio Rápido

### 1. Instalar Dependencias

```bash
# Activar entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/macOS

# Instalar dependencias (incluye FastAPI, uvicorn, etc.)
pip install -r requirements.txt
```

### 2. Inicializar Base de Datos

```bash
python scripts/init_database.py
```

### 3. Iniciar Servidor API

```bash
# Modo desarrollo (auto-reload)
python scripts/run_api.py

# O directamente con uvicorn
uvicorn src.ai_native_mvp.api.main:app --reload

# Modo producción
python scripts/run_api.py --production
```

### 4. Acceder a la Documentación

Una vez iniciado el servidor, acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Arquitectura de la API

### Estructura de Carpetas

```
src/ai_native_mvp/api/
├── main.py                 # Aplicación FastAPI principal
├── deps.py                 # Dependency injection
├── exceptions.py           # Excepciones personalizadas
├── middleware/             # Middleware
│   ├── error_handler.py    # Manejo de errores
│   └── logging.py          # Request logging
├── routers/                # Endpoints REST
│   ├── health.py           # Health checks
│   ├── sessions.py         # Sesiones CRUD
│   ├── interactions.py     # Procesamiento de interacciones
│   ├── traces.py           # Trazabilidad N4
│   └── risks.py            # Riesgos y evaluaciones
└── schemas/                # DTOs (Request/Response models)
    ├── common.py           # Schemas comunes
    ├── session.py
    ├── interaction.py
    └── ...
```

### Patrones Arquitectónicos

1. **Clean Architecture**: Separación en capas (API → Core → Database)
2. **Repository Pattern**: Abstracción de persistencia
3. **Dependency Injection**: Desacoplamiento de componentes
4. **DTO Pattern**: Pydantic schemas para requests/responses
5. **Middleware Pattern**: Logging, error handling, CORS
6. **Factory Pattern**: Creación de LLM providers

## Endpoints Principales

### Health Check

```http
GET /api/v1/health
```

Verifica el estado del servicio, base de datos y agentes.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected",
  "agents": {
    "T-IA-Cog": "operational",
    "E-IA-Proc": "operational",
    "S-IA-X": "operational",
    "AR-IA": "operational",
    "GOV-IA": "operational",
    "TC-N4": "operational"
  },
  "timestamp": "2025-11-18T10:00:00Z"
}
```

### Crear Sesión

```http
POST /api/v1/sessions
Content-Type: application/json

{
  "student_id": "student_001",
  "activity_id": "prog2_tp1_colas",
  "mode": "TUTOR"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "session_abc123",
    "student_id": "student_001",
    "activity_id": "prog2_tp1_colas",
    "mode": "TUTOR",
    "status": "ACTIVE",
    "start_time": "2025-11-18T10:00:00Z",
    "trace_count": 0,
    "risk_count": 0
  },
  "message": "Session created successfully: session_abc123"
}
```

### Procesar Interacción (Endpoint Principal)

```http
POST /api/v1/interactions
Content-Type: application/json

{
  "session_id": "session_abc123",
  "prompt": "¿Cómo implemento una cola circular eficientemente?",
  "context": {
    "code_snippet": "class Queue:\n    def __init__(self)...",
    "line_number": 15
  },
  "cognitive_intent": "UNDERSTANDING"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "interaction_id": "interaction_xyz789",
    "session_id": "session_abc123",
    "response": "Para implementar una cola circular de manera eficiente...",
    "agent_used": "T-IA-Cog",
    "cognitive_state_detected": "EXPLORACION_CONCEPTUAL",
    "ai_involvement": 0.4,
    "blocked": false,
    "block_reason": null,
    "trace_id": "trace_123",
    "risks_detected": [],
    "timestamp": "2025-11-18T10:30:00Z"
  },
  "message": "Interaction processed successfully"
}
```

### Obtener Trazas N4

```http
GET /api/v1/traces/{session_id}?trace_level=N4_COGNITIVO
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "trace_123",
      "session_id": "session_abc123",
      "trace_level": "N4_COGNITIVO",
      "interaction_type": "STUDENT_PROMPT",
      "cognitive_state": "EXPLORACION_CONCEPTUAL",
      "cognitive_intent": "UNDERSTANDING",
      "content": "¿Cómo implemento una cola circular?",
      "ai_involvement": 0.4,
      "timestamp": "2025-11-18T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_items": 1,
    "total_pages": 1
  }
}
```

### Obtener Camino Cognitivo

```http
GET /api/v1/traces/{session_id}/cognitive-path
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "states_sequence": ["PLANIFICACION", "EXPLORACION_CONCEPTUAL", "IMPLEMENTACION"],
    "transitions": [
      {
        "from": "PLANIFICACION",
        "to": "EXPLORACION_CONCEPTUAL",
        "index": 0,
        "timestamp": "2025-11-18T10:30:00Z"
      }
    ],
    "total_traces": 5,
    "n4_traces_count": 3,
    "ai_dependency_evolution": [0.3, 0.4, 0.35, 0.5, 0.45],
    "strategy_changes": []
  }
}
```

### Obtener Riesgos de Sesión

```http
GET /api/v1/risks/session/{session_id}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "risk_001",
      "risk_type": "COGNITIVE_DELEGATION",
      "risk_level": "MEDIUM",
      "dimension": "COGNITIVE",
      "description": "Delegación parcial detectada",
      "evidence": ["Dame el código completo"],
      "recommendations": [
        "Replantear pregunta para solicitar guía conceptual",
        "Intentar implementación propia primero"
      ],
      "resolved": false
    }
  ]
}
```

### Listar Sesiones

```http
GET /api/v1/sessions?student_id=student_001&page=1&page_size=20
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "session_abc123",
      "student_id": "student_001",
      "activity_id": "prog2_tp1_colas",
      "mode": "TUTOR",
      "status": "ACTIVE",
      "trace_count": 5,
      "risk_count": 1
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 1,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

## Ejemplos de Uso

### Usando Python (requests)

Ver `examples/api_usage_example.py` para un ejemplo completo.

```python
import requests

API_BASE_URL = "http://localhost:8000/api/v1"

# 1. Crear sesión
response = requests.post(
    f"{API_BASE_URL}/sessions",
    json={
        "student_id": "student_001",
        "activity_id": "prog2_tp1",
        "mode": "TUTOR"
    }
)
session = response.json()["data"]
session_id = session["id"]

# 2. Procesar interacción
response = requests.post(
    f"{API_BASE_URL}/interactions",
    json={
        "session_id": session_id,
        "prompt": "¿Qué es una cola circular?",
        "cognitive_intent": "UNDERSTANDING"
    }
)
interaction = response.json()["data"]
print(interaction["response"])
```

### Usando cURL

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Crear sesión
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_001",
    "activity_id": "prog2_tp1",
    "mode": "TUTOR"
  }'

# Procesar interacción
curl -X POST http://localhost:8000/api/v1/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_abc123",
    "prompt": "¿Qué es una cola circular?",
    "cognitive_intent": "UNDERSTANDING"
  }'
```

### Usando JavaScript (fetch)

```javascript
const API_BASE_URL = "http://localhost:8000/api/v1";

// Crear sesión
const response = await fetch(`${API_BASE_URL}/sessions`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    student_id: "student_001",
    activity_id: "prog2_tp1",
    mode: "TUTOR"
  })
});

const { data: session } = await response.json();
console.log("Session created:", session.id);

// Procesar interacción
const interactionResponse = await fetch(`${API_BASE_URL}/interactions`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    session_id: session.id,
    prompt: "¿Qué es una cola circular?",
    cognitive_intent: "UNDERSTANDING"
  })
});

const { data: interaction } = await interactionResponse.json();
console.log("Response:", interaction.response);
```

## Manejo de Errores

La API utiliza códigos HTTP estándar y respuestas de error estructuradas.

### Formato de Error

```json
{
  "success": false,
  "error": {
    "error_code": "SESSION_NOT_FOUND",
    "message": "Session 'session_xyz' not found",
    "field": null,
    "extra": {
      "session_id": "session_xyz"
    }
  },
  "timestamp": "2025-11-18T10:00:00Z"
}
```

### Códigos de Error Comunes

| Código HTTP | Error Code | Descripción |
|------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Datos de entrada inválidos |
| 400 | `INVALID_INTERACTION` | Interacción mal formada |
| 401 | `AUTHENTICATION_FAILED` | Token de autenticación inválido |
| 403 | `GOVERNANCE_BLOCKED` | Bloqueado por políticas de gobernanza |
| 403 | `AUTHORIZATION_FAILED` | Sin permisos para la operación |
| 404 | `SESSION_NOT_FOUND` | Sesión no encontrada |
| 404 | `STUDENT_NOT_FOUND` | Estudiante no encontrado |
| 422 | `VALIDATION_ERROR` | Error de validación de Pydantic |
| 500 | `DATABASE_ERROR` | Error de base de datos |
| 500 | `INTERNAL_ERROR` | Error interno del servidor |
| 503 | `AGENT_NOT_AVAILABLE` | Agente no disponible |

## Autenticación (TODO en Producción)

**MVP**: La API actualmente NO requiere autenticación para facilitar el desarrollo.

**Producción**: Se implementará autenticación JWT:

```http
POST /api/v1/interactions
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "session_id": "session_abc123",
  "prompt": "¿Cómo implemento una cola?"
}
```

Para implementar autenticación en producción, ver `src/ai_native_mvp/api/deps.py` (funciones `get_current_user`, `require_role`).

## CORS Configuration

La API permite CORS desde:
- `http://localhost:3000` (React dev server)
- `http://localhost:5173` (Vite dev server)
- `http://localhost:8080` (Vue dev server)

Para producción, modificar `src/ai_native_mvp/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing

### Ejecutar Tests de API

```bash
# Instalar dependencias de testing
pip install pytest pytest-asyncio httpx

# Ejecutar tests (TODO: implementar)
pytest tests/api/ -v
```

### Testear Manualmente

1. Iniciar servidor: `python scripts/run_api.py`
2. Ejecutar ejemplo: `python examples/api_usage_example.py`
3. O usar Swagger UI: http://localhost:8000/docs

## Deployment

### Docker (TODO)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.ai_native_mvp.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose (TODO)

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/ai_native
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=ai_native
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Monitoring y Logging

La API incluye logging automático de todas las requests:

```
2025-11-18 10:30:00 - INFO - POST /api/v1/interactions - Status: 200 - Duration: 0.234s - Client: 127.0.0.1
```

Cada response incluye header `X-Process-Time` con el tiempo de procesamiento.

## Próximos Pasos

1. ✅ API REST completamente funcional
2. ⏳ Tests de integración para endpoints
3. ⏳ Autenticación JWT en producción
4. ⏳ Rate limiting y throttling
5. ⏳ Dashboard web (React/Vue)
6. ⏳ Integración con LTI para Moodle
7. ⏳ Containerización con Docker
8. ⏳ CI/CD pipeline
9. ⏳ Monitoring con Prometheus/Grafana

## Soporte

Para reportar issues o solicitar features:
- GitHub Issues: (TODO: agregar URL)
- Documentación completa: Ver `CLAUDE.md` y `README_MVP.md`

---

**Autor**: Mag. en Ing. de Software Alberto Cortez
**Versión**: 0.1.0
**Licencia**: MIT