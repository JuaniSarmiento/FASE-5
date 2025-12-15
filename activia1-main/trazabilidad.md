# TRAZABILIDAD COGNITIVA N4 (TC-N4) - Documentacion Tecnica Detallada

## Tabla de Contenidos

1. [Vision General](#1-vision-general)
2. [Los 4 Niveles de Trazabilidad](#2-los-4-niveles-de-trazabilidad)
3. [Las 6 Dimensiones N4](#3-las-6-dimensiones-n4)
4. [TrazabilidadN4Agent: Nucleo Principal](#4-trazabilidadn4agent-nucleo-principal)
5. [Modelos de Dominio](#5-modelos-de-dominio)
6. [Tablas de Base de Datos](#6-tablas-de-base-de-datos)
7. [Repositorios](#7-repositorios)
8. [API Endpoints](#8-api-endpoints)
9. [Reconstruccion del Camino Cognitivo](#9-reconstruccion-del-camino-cognitivo)
10. [Grafo de Trazabilidad de Sesion](#10-grafo-de-trazabilidad-de-sesion)
11. [Integracion con Otros Agentes](#11-integracion-con-otros-agentes)
12. [Deteccion de Decisiones Sin Justificar](#12-deteccion-de-decisiones-sin-justificar)
13. [Exportacion para Evaluacion](#13-exportacion-para-evaluacion)
14. [Resumen Ejecutivo](#14-resumen-ejecutivo)

---

## 1. Vision General

### 1.1 Proposito

El **Sistema de Trazabilidad Cognitiva N4 (TC-N4)** es la columna vertebral del ecosistema AI-Native. Su funcion es capturar, almacenar y reconstruir el proceso completo de razonamiento hibrido humano-IA durante el aprendizaje de programacion.

**Objetivo Principal**: Permitir la evaluacion basada en PROCESO (no en producto), registrando:
- QUE hizo el estudiante (interacciones)
- COMO lo hizo (estrategias)
- POR QUE lo hizo (justificaciones)
- CON QUIEN lo hizo (dependencia de IA)

### 1.2 Diferenciador Clave

A diferencia de los sistemas tradicionales que solo registran entregas finales (codigo), TC-N4 captura:

```
TRADICIONAL: Estudiante → Codigo Final → Evaluacion

TC-N4:       Estudiante → [Exploracion → Planificacion → Implementacion → Depuracion → Validacion]
                            ↓              ↓                ↓               ↓            ↓
                         Traza N4       Traza N4         Traza N4       Traza N4     Traza N4
                            ↓              ↓                ↓               ↓            ↓
                      (6 dimensiones) (6 dimensiones)  (6 dimensiones) (6 dimensiones) (6 dimensiones)
```

### 1.3 Ubicacion en la Arquitectura

```
                        +------------------+
                        |   AIGateway      |
                        |   (Orquestador)  |
                        +--------+---------+
                                 |
                    +------------+------------+
                    |            |            |
            +-------v-------+    |    +-------v-------+
            |   GOV-IA      |    |    |   AR-IA       |
            | (Gobernanza)  |    |    | (Riesgos)     |
            +---------------+    |    +---------------+
                                 |
                        +--------v--------+
                        |     TC-N4       |  <-- ESTE AGENTE
                        | (Trazabilidad)  |
                        +--------+--------+
                                 |
         +-----------+-----------+-----------+-----------+
         |           |           |           |           |
    +----v----+ +----v----+ +----v----+ +----v----+ +----v----+
    | T-IA-Cog| | E-IA    | | S-IA-X  | | Traces  | | Sequences|
    | (Tutor) | | (Eval)  | | (Sim)   | |  (DB)   | |   (DB)   |
    +---------+ +---------+ +---------+ +---------+ +----------+
```

**Archivo Principal**: `backend/agents/traceability.py`

---

## 2. Los 4 Niveles de Trazabilidad

### 2.1 Jerarquia de Niveles

El sistema define 4 niveles progresivos de profundidad en el registro:

```python
class TraceLevel(str, Enum):
    N1_SUPERFICIAL = "n1_superficial"    # Archivos y entregas
    N2_TECNICO = "n2_tecnico"            # Commits y tests
    N3_INTERACCIONAL = "n3_interaccional" # Prompts y respuestas
    N4_COGNITIVO = "n4_cognitivo"        # Razonamiento completo
```

### 2.2 Detalle por Nivel

| Nivel | Nombre | Que Captura | Ejemplo |
|-------|--------|-------------|---------|
| N1 | Superficial | Archivos subidos, entregas finales, version de codigo | `archivo_tp1.py`, timestamp de entrega |
| N2 | Tecnico | Commits Git, branches, tests automaticos, metricas de codigo | `commit abc123`, test coverage 80% |
| N3 | Interaccional | Prompts del estudiante, respuestas de IA, reintentos | "Como implemento una cola?", respuesta del tutor |
| N4 | Cognitivo | Intenciones, decisiones, justificaciones, alternativas, riesgos | "Elegi arreglo circular porque O(1) en enqueue" |

### 2.3 Visualizacion del Pipeline N1-N4

```
    NIVEL 1: Raw Data                NIVEL 2: Preprocessed
    +-----------------+              +--------------------+
    | Input Original  |  ========>   | Validacion         |
    | - Texto crudo   |     2ms      | - Limpieza         |
    | - Encoding      |              | - Tokenizacion     |
    | - Length        |              | - Intent detection |
    +-----------------+              +--------------------+
                                              |
                                              v
    NIVEL 4: Postprocessed           NIVEL 3: LLM Processing
    +--------------------+           +--------------------+
    | Output Final       |  <======  | Inferencia LLM     |
    | - Response format  |   145ms   | - Prompt + Context |
    | - Cognitive state  |           | - Model output     |
    | - AI involvement   |           | - Tokens used      |
    | - Metadata enrich  |           | - Agent routing    |
    +--------------------+           +--------------------+
```

---

## 3. Las 6 Dimensiones N4

### 3.1 Vision General

El nivel N4 (Cognitivo) se subdivide en 6 dimensiones que capturan diferentes aspectos del proceso cognitivo:

```
+===============================================================+
|                     TRAZA COGNITIVA N4                        |
+===============================================================+
|                                                               |
|  +------------------+  +------------------+  +------------------+
|  | 1. SEMANTICA     |  | 2. ALGORITMICA   |  | 3. COGNITIVA     |
|  | Que entendio?    |  | Como evoluciono? |  | Por que decidio? |
|  +------------------+  +------------------+  +------------------+
|                                                               |
|  +------------------+  +------------------+  +------------------+
|  | 4. INTERACCIONAL |  | 5. ETICA/RIESGO  |  | 6. PROCESUAL     |
|  | Como pregunto?   |  | Hubo fraude?     |  | Cuanto tardo?    |
|  +------------------+  +------------------+  +------------------+
|                                                               |
+===============================================================+
```

### 3.2 Dimension 1: Semantica

**Pregunta clave**: Que entendio el estudiante del problema?

```python
semantic_understanding = Column(JSONBCompatible, default=dict)
# Estructura:
{
    "problem_interpretation": "string",  # Interpretacion del problema
    "key_concepts_identified": ["concept1", "concept2"],  # Conceptos identificados
    "misconceptions_detected": ["misconception1"],  # Malentendidos detectados
    "understanding_level": "superficial|partial|profundo"
}
```

**Ejemplo Real**:
```json
{
    "problem_interpretation": "Implementar una cola con operaciones enqueue/dequeue",
    "key_concepts_identified": ["FIFO", "estructura lineal", "punteros"],
    "misconceptions_detected": ["Confunde cola con pila"],
    "understanding_level": "partial"
}
```

### 3.3 Dimension 2: Algoritmica

**Pregunta clave**: Como evoluciono el codigo y que alternativas considero?

```python
algorithmic_evolution = Column(JSONBCompatible, default=dict)
# Estructura:
{
    "code_versions": [{"version": 1, "code": "...", "timestamp": "..."}],
    "alternatives_explored": ["approach1", "approach2"],
    "design_decisions": [{"decision": "...", "rationale": "..."}],
    "complexity_analysis": "O(n) vs O(n^2) - eligio O(n)"
}
```

**Ejemplo Real**:
```json
{
    "code_versions": [
        {"version": 1, "code": "class Cola: pass", "timestamp": "10:00"},
        {"version": 2, "code": "class Cola:\n  def __init__(self)...", "timestamp": "10:15"}
    ],
    "alternatives_explored": ["lista enlazada", "arreglo circular", "dos pilas"],
    "design_decisions": [
        {"decision": "Usar arreglo circular", "rationale": "O(1) en todas las operaciones"}
    ],
    "complexity_analysis": "Analizo O(n) para lista vs O(1) para arreglo circular"
}
```

### 3.4 Dimension 3: Cognitiva

**Pregunta clave**: Por que tomo esa decision? Que razonamiento explicito?

```python
cognitive_reasoning = Column(JSONBCompatible, default=dict)
# Estructura:
{
    "explicit_reasoning": "string",  # Razonamiento verbalizado
    "metacognitive_awareness": "high|medium|low",  # Conciencia metacognitiva
    "problem_decomposition": ["subproblem1", "subproblem2"],
    "strategy_justification": "Por que eligio esta estrategia"
}
```

**Ejemplo Real**:
```json
{
    "explicit_reasoning": "Pense que si uso un arreglo circular puedo reutilizar espacios",
    "metacognitive_awareness": "medium",
    "problem_decomposition": ["Manejar indice front", "Manejar indice rear", "Detectar lleno/vacio"],
    "strategy_justification": "Elegi circular porque evita desplazamientos costosos"
}
```

### 3.5 Dimension 4: Interaccional

**Pregunta clave**: Como interactuo con la IA? Que tipo de ayuda pidio?

```python
interactional_data = Column(JSONBCompatible, default=dict)
# Estructura:
{
    "prompt_type": "clarification|delegation|exploration|validation",
    "prompt_quality_score": 0.0-1.0,  # Calidad del prompt
    "ai_response_type": "socratic|explanatory|hint|code_sample",
    "interaction_depth": "superficial|elaborated|deep",
    "student_agency": 0.0-1.0  # Que tanto lidero el alumno
}
```

**Ejemplo Real**:
```json
{
    "prompt_type": "exploration",
    "prompt_quality_score": 0.75,
    "ai_response_type": "socratic",
    "interaction_depth": "elaborated",
    "student_agency": 0.8
}
```

### 3.6 Dimension 5: Etica/Riesgo

**Pregunta clave**: Hubo indicios de plagio, delegacion excesiva o sesgos?

```python
ethical_risk_data = Column(JSONBCompatible, default=dict)
# Estructura:
{
    "plagiarism_indicators": ["indicator1"],  # Indicadores de plagio
    "delegation_attempts": 3,  # Intentos de delegacion total
    "academic_integrity_score": 0.0-1.0,
    "bias_detected": ["bias_type1"],  # Sesgos en codigo/razonamiento
    "ethical_concerns": ["concern1"]
}
```

**Ejemplo Real**:
```json
{
    "plagiarism_indicators": [],
    "delegation_attempts": 1,
    "academic_integrity_score": 0.9,
    "bias_detected": [],
    "ethical_concerns": []
}
```

### 3.7 Dimension 6: Procesual

**Pregunta clave**: Cuanto tiempo tomo? Cual fue la secuencia logica?

```python
process_data = Column(JSONBCompatible, default=dict)
# Estructura:
{
    "phase_sequence": ["exploracion", "planificacion", "implementacion"],
    "time_per_phase_minutes": {"exploracion": 5, "planificacion": 10},
    "pause_patterns": [{"start": "10:15", "end": "10:20", "reason": "thinking"}],
    "iteration_count": 3,  # Cuantas veces itero sobre el problema
    "backtracking_events": 1  # Cuantas veces volvio atras
}
```

---

## 4. TrazabilidadN4Agent: Nucleo Principal

### 4.1 Clase Principal

**Ubicacion**: `backend/agents/traceability.py`

```python
class TrazabilidadN4Agent:
    """
    TC-N4: Sistema de Trazabilidad Cognitiva (4 niveles)

    Niveles:
    - N1: Superficial (archivos, entregas)
    - N2: Tecnico (commits, tests)
    - N3: Interaccional (prompts, respuestas)
    - N4: Cognitivo completo (razonamiento, decisiones, justificaciones)

    Este sistema es la columna vertebral del ecosistema AI-Native
    """
```

### 4.2 Metodos Principales

| Metodo | Proposito | Retorno |
|--------|-----------|---------|
| `capture_interaction()` | Captura una interaccion en el sistema | `CognitiveTrace` |
| `create_sequence()` | Crea una nueva secuencia de trazas | `TraceSequence` |
| `get_sequence()` | Obtiene una secuencia por ID | `Optional[TraceSequence]` |
| `get_student_traces()` | Obtiene todas las trazas de un estudiante | `List[CognitiveTrace]` |
| `reconstruct_cognitive_path()` | Reconstruye el camino cognitivo completo | `Dict[str, Any]` |
| `capture_design_decision()` | Captura una decision de diseno con justificacion | `CognitiveTrace` |
| `detect_unjustified_decisions()` | Detecta decisiones sin justificacion | `Dict[str, Any]` |
| `export_for_evaluation()` | Exporta trazas para evaluacion docente | `Dict[str, Any]` |

### 4.3 capture_interaction()

Captura una interaccion en el sistema de trazabilidad:

```python
def capture_interaction(
    self,
    student_id: str,
    activity_id: str,
    interaction_type: InteractionType,
    content: str,
    level: TraceLevel = TraceLevel.N4_COGNITIVO,
    **metadata
) -> CognitiveTrace:
```

**Parametros**:
- `student_id`: ID del estudiante
- `activity_id`: ID de la actividad
- `interaction_type`: Tipo de interaccion (enum)
- `content`: Contenido de la interaccion
- `level`: Nivel de trazabilidad (default N4)
- `**metadata`: Metadata adicional (cognitive_intent, decision_justification, etc.)

**Ejemplo de Uso**:
```python
trace = agent.capture_interaction(
    student_id="student_123",
    activity_id="prog2_tp1",
    interaction_type=InteractionType.STUDENT_PROMPT,
    content="Como implemento una cola circular?",
    cognitive_intent="UNDERSTANDING",
    context={"topic": "data_structures"}
)
```

### 4.4 capture_design_decision()

Captura una decision de diseno con su justificacion (HU-EST-005):

```python
def capture_design_decision(
    self,
    student_id: str,
    activity_id: str,
    session_id: str,
    decision: str,
    justification: str,
    alternatives_considered: Optional[List[str]] = None,
    context: Optional[Dict[str, Any]] = None
) -> CognitiveTrace:
```

**Ejemplo de Uso**:
```python
trace = agent.capture_design_decision(
    student_id="student_123",
    activity_id="prog2_tp1",
    session_id="session_abc",
    decision="Usar arreglo circular para la cola",
    justification="Porque permite O(1) en enqueue y dequeue sin desperdiciar memoria",
    alternatives_considered=["lista enlazada", "arreglo simple con desplazamiento"],
    context={"complexity_constraint": "O(1)"}
)
```

### 4.5 reconstruct_cognitive_path()

Reconstruye el camino cognitivo completo de una secuencia:

```python
def reconstruct_cognitive_path(
    self,
    sequence_id: str
) -> Dict[str, Any]:
```

**Retorno**:
```python
{
    "sequence_id": "seq_123",
    "student_id": "student_123",
    "activity_id": "prog2_tp1",
    "duration": 3600.0,  # segundos
    "total_interactions": 15,
    "cognitive_path": ["exploracion", "planificacion", "implementacion", ...],
    "phases": [
        {"phase": "exploracion", "start_time": "...", "trace_id": "..."},
        {"phase": "planificacion", "start_time": "...", "trace_id": "..."}
    ],
    "key_decisions": [
        {
            "trace_id": "trace_456",
            "timestamp": "...",
            "decision": "Usar arreglo circular",
            "justification": "O(1) en operaciones",
            "alternatives_considered": ["lista enlazada"]
        }
    ],
    "strategy_changes": 2,
    "ai_dependency_score": 0.35,
    "timeline": [...]
}
```

---

## 5. Modelos de Dominio

### 5.1 CognitiveTrace

**Ubicacion**: `backend/models/trace.py`

```python
class CognitiveTrace(BaseModel):
    """
    Representa una traza cognitiva en el sistema N4.
    Captura el proceso completo de razonamiento hibrido humano-IA.
    """

    # Identificadores
    id: str
    session_id: str
    student_id: str
    activity_id: str

    # Timestamp (FIX 3.1 Cortez8: created_at con alias timestamp)
    created_at: datetime = Field(alias="timestamp")

    # Niveles de trazabilidad
    trace_level: TraceLevel = TraceLevel.N4_COGNITIVO
    interaction_type: InteractionType

    # Contenido
    content: str
    context: Dict[str, Any] = {}
    trace_metadata: Dict[str, Any] = {}

    # Analisis cognitivo (N4)
    cognitive_state: Optional[str] = None
    cognitive_intent: Optional[str] = None
    decision_justification: Optional[str] = None
    alternatives_considered: List[str] = []
    strategy_type: Optional[str] = None

    # AI Involvement
    ai_involvement: float = Field(0.0, ge=0.0, le=1.0)

    # Metadata
    agent_id: Optional[str] = None
    parent_trace_id: Optional[str] = None
```

### 5.2 TraceSequence

```python
class TraceSequence(BaseModel):
    """
    Secuencia de trazas que representan un episodio cognitivo completo
    """
    id: str
    session_id: str
    student_id: str
    activity_id: str
    traces: List[CognitiveTrace] = []
    start_time: datetime
    end_time: Optional[datetime] = None

    # Analisis agregado
    reasoning_path: List[str] = []          # Camino de razonamiento
    strategy_changes: int = 0               # Cambios de estrategia
    ai_dependency_score: float = 0.0        # Dependencia de IA (0-1)

    def add_trace(self, trace: CognitiveTrace) -> None:
        """Anade una traza y recalcula ai_dependency_score"""

    def get_cognitive_path(self) -> List[str]:
        """Reconstruye el camino cognitivo"""
```

### 5.3 InteractionType (Enum)

```python
class InteractionType(str, Enum):
    """Tipos de interaccion humano-IA"""
    STUDENT_PROMPT = "student_prompt"
    AI_RESPONSE = "ai_response"
    CODE_COMMIT = "code_commit"
    TUTOR_INTERVENTION = "tutor_intervention"
    TEACHER_FEEDBACK = "teacher_feedback"
    STRATEGY_CHANGE = "strategy_change"
    HYPOTHESIS_FORMULATION = "hypothesis_formulation"
    SELF_CORRECTION = "self_correction"
    AI_CRITIQUE = "ai_critique"
```

### 5.4 CognitiveState (Enum)

```python
class CognitiveState(str, Enum):
    """Estados cognitivos del estudiante"""

    # Estados principales (lowercase para BD)
    EXPLORACION = "exploracion"
    PLANIFICACION = "planificacion"
    IMPLEMENTACION = "implementacion"
    DEPURACION = "depuracion"
    VALIDACION = "validacion"
    REFLEXION = "reflexion"

    # Estados adicionales
    CONFUSION = "confusion"
    PROGRESANDO = "progresando"
    ATASCADO = "atascado"

    # Aliases en ingles para compatibilidad
    EXPLORATION = "exploracion"
    PLANNING = "planificacion"
    # ... etc
```

---

## 6. Tablas de Base de Datos

### 6.1 CognitiveTraceDB

**Ubicacion**: `backend/database/models.py` (linea 189)

```sql
CREATE TABLE cognitive_traces (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    -- Trace metadata
    trace_level VARCHAR(20) DEFAULT 'n4_cognitivo',
    interaction_type VARCHAR(50) NOT NULL,

    -- Content
    content TEXT NOT NULL,
    context JSON DEFAULT '{}',
    trace_metadata JSON DEFAULT '{}',  -- NOTE: Use trace_metadata, NOT metadata

    -- N4 Cognitive analysis
    cognitive_state VARCHAR(50),
    cognitive_intent VARCHAR(200),
    decision_justification TEXT,
    alternatives_considered JSON DEFAULT '[]',
    strategy_type VARCHAR(100),

    -- AI involvement
    ai_involvement FLOAT DEFAULT 0.0,  -- 0.0 to 1.0

    -- === LAS 6 DIMENSIONES N4 ===
    semantic_understanding JSONB,       -- Dimension 1
    algorithmic_evolution JSONB,        -- Dimension 2
    cognitive_reasoning JSONB,          -- Dimension 3
    interactional_data JSONB,           -- Dimension 4
    ethical_risk_data JSONB,            -- Dimension 5
    process_data JSONB,                 -- Dimension 6

    -- Relationships
    agent_id VARCHAR(100),
    parent_trace_id VARCHAR(36),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_trace_session ON cognitive_traces(session_id);
CREATE INDEX idx_trace_student ON cognitive_traces(student_id);
CREATE INDEX idx_trace_session_level ON cognitive_traces(session_id, trace_level);

-- GIN indexes for JSONB dimensions (Cortez4)
CREATE INDEX idx_trace_semantic ON cognitive_traces USING GIN(semantic_understanding);
CREATE INDEX idx_trace_algorithmic ON cognitive_traces USING GIN(algorithmic_evolution);
CREATE INDEX idx_trace_cognitive ON cognitive_traces USING GIN(cognitive_reasoning);
CREATE INDEX idx_trace_interactional ON cognitive_traces USING GIN(interactional_data);
CREATE INDEX idx_trace_ethical ON cognitive_traces USING GIN(ethical_risk_data);
CREATE INDEX idx_trace_process ON cognitive_traces USING GIN(process_data);
```

### 6.2 TraceSequenceDB

**Ubicacion**: `backend/database/models.py` (linea 466)

```sql
CREATE TABLE trace_sequences (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    -- Sequence metadata
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,

    -- Aggregated analysis
    reasoning_path JSON DEFAULT '[]',
    strategy_changes INTEGER DEFAULT 0,
    ai_dependency_score FLOAT DEFAULT 0.0,

    -- References to traces (JSON array)
    trace_ids JSON DEFAULT '[]',

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,

    -- Constraints
    CONSTRAINT ck_seq_ai_dep_range CHECK (ai_dependency_score >= 0 AND ai_dependency_score <= 1)
);

-- Indexes
CREATE INDEX idx_trace_seq_student_activity ON trace_sequences(student_id, activity_id);
CREATE INDEX idx_student_start ON trace_sequences(student_id, start_time);
CREATE INDEX idx_trace_seq_session ON trace_sequences(session_id);
```

**Nota de Diseno**: La tabla usa JSON array para `trace_ids` en lugar de tabla de join. Ver docstring en models.py para rationale y plan de migracion futura.

---

## 7. Repositorios

### 7.1 TraceRepository

**Ubicacion**: `backend/database/repositories.py` (linea 627)

```python
class TraceRepository:
    """Repository for cognitive trace operations"""

    def __init__(self, db_session: Session):
        self.db = db_session
```

**Metodos Principales**:

| Metodo | Descripcion |
|--------|-------------|
| `create(trace)` | Crea una nueva traza cognitiva |
| `get_by_id(trace_id)` | Obtiene traza por ID |
| `get_by_session(session_id, limit, offset)` | Obtiene trazas de una sesion |
| `get_by_student(student_id, limit)` | Obtiene trazas de un estudiante |
| `get_by_session_filtered(...)` | Filtra por nivel, tipo, estado |
| `count_by_session_filtered(...)` | Cuenta trazas con filtros |
| `get_by_student_activity_pairs(pairs)` | Batch loading para N+1 prevention |

### 7.2 TraceSequenceRepository

**Ubicacion**: `backend/database/repositories.py` (linea 1390)

```python
class TraceSequenceRepository:
    """Repository for trace sequence operations"""
```

**Metodos Principales**:

| Metodo | Descripcion |
|--------|-------------|
| `create(sequence)` | Crea nueva secuencia (con rollback) |
| `get_by_id(sequence_id)` | Obtiene secuencia por ID |
| `get_by_session(session_id, limit, offset, load_relations)` | Secuencias de sesion |
| `get_by_student(student_id, limit)` | Secuencias de estudiante |
| `count_by_session(session_id)` | Cuenta secuencias (FIX 10.19) |
| `count_by_student(student_id)` | Cuenta por estudiante (FIX 10.19) |

---

## 8. API Endpoints

### 8.1 Router de Trazas

**Ubicacion**: `backend/api/routers/traces.py`

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/traces/{session_id}` | Obtiene trazas de una sesion con filtros |
| GET | `/traces/student/{student_id}` | Obtiene trazas de un estudiante |
| GET | `/traces/{session_id}/cognitive-path` | DEPRECATED - Redirige a /cognitive-path |

**Ejemplo: GET /traces/{session_id}**

```http
GET /api/v1/traces/session_abc123?trace_level=n4_cognitivo&page=1&page_size=50
```

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": "trace_xyz789",
      "session_id": "session_abc123",
      "student_id": "student_001",
      "trace_level": "n4_cognitivo",
      "interaction_type": "student_prompt",
      "content": "Como implemento una cola?",
      "cognitive_state": "exploracion",
      "cognitive_intent": "UNDERSTANDING",
      "ai_involvement": 0.3,
      "created_at": "2025-11-18T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_items": 15,
    "total_pages": 1
  }
}
```

### 8.2 Router de Trazabilidad N4

**Ubicacion**: `backend/api/routers/traceability.py`

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/traceability/{trace_id}` | Trazabilidad completa N1-N4 de una traza |
| GET | `/traceability/session/{session_id}` | Grafo de trazabilidad de sesion |

**Ejemplo: GET /traceability/{trace_id}**

```http
GET /api/v1/traceability/trace_xyz789
```

**Response**:
```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "trace_id": "trace_xyz789",
    "nodes": [
      {
        "id": "trace_xyz789-n1",
        "level": "N1",
        "timestamp": "2025-11-18T10:30:00Z",
        "data": {
          "raw_input": "Como implemento una cola circular?",
          "content_length": 35,
          "encoding": "utf-8"
        },
        "metadata": {
          "processing_time_ms": 2,
          "transformations": []
        }
      },
      {
        "id": "trace_xyz789-n2",
        "level": "N2",
        "data": {
          "cleaned_input": "Como implemento una cola circular?",
          "validation_passed": true,
          "intent": "UNDERSTANDING"
        },
        "metadata": {
          "processing_time_ms": 45,
          "transformations": ["Whitespace trimming", "Intent classification"]
        }
      },
      {
        "id": "trace_xyz789-n3",
        "level": "N3",
        "data": {
          "model_input": {"prompt": "...", "context": {}},
          "model_output": {"raw_response": "...", "finish_reason": "stop"},
          "agent": "T-IA-Cog"
        },
        "metadata": {
          "processing_time_ms": 1420,
          "tokens_used": 150,
          "model": "llama3.2:3b"
        }
      },
      {
        "id": "trace_xyz789-n4",
        "level": "N4",
        "data": {
          "final_response": "...",
          "cognitive_state": "exploracion",
          "ai_involvement": 0.3,
          "blocked": false
        },
        "metadata": {
          "processing_time_ms": 145,
          "transformations": ["Response formatting", "Cognitive state detection"]
        }
      }
    ],
    "total_latency_ms": 1612,
    "total_tokens": 150
  }
}
```

### 8.3 Router de Camino Cognitivo

**Ubicacion**: `backend/api/routers/cognitive_path.py`

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/cognitive-path/{session_id}` | Camino cognitivo completo (HU-EST-006) |
| GET | `/cognitive-path/{session_id}/summary` | Solo metricas resumen |

---

## 9. Reconstruccion del Camino Cognitivo

### 9.1 Endpoint Principal

**GET /api/v1/cognitive-path/{session_id}**

Este endpoint reconstruye y visualiza el camino cognitivo completo de un estudiante durante una sesion.

### 9.2 Estructura de Respuesta

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "student_id": "student_001",
    "activity_id": "prog2_tp1",
    "start_time": "2025-11-18T10:00:00Z",
    "end_time": "2025-11-18T11:30:00Z",

    "summary": {
      "total_interactions": 15,
      "total_duration_minutes": 90.0,
      "blocked_interactions": 2,
      "ai_dependency_average": 0.35,
      "strategy_changes": 3,
      "risks_total": 2,
      "risks_by_level": {"MEDIUM": 1, "LOW": 1}
    },

    "phases": [
      {
        "phase_name": "exploracion",
        "start_time": "2025-11-18T10:00:00Z",
        "end_time": "2025-11-18T10:15:00Z",
        "duration_minutes": 15.0,
        "interactions_count": 4,
        "ai_involvement_avg": 0.25,
        "risks_detected": [],
        "key_decisions": []
      },
      {
        "phase_name": "planificacion",
        "start_time": "2025-11-18T10:15:00Z",
        "end_time": "2025-11-18T10:35:00Z",
        "duration_minutes": 20.0,
        "interactions_count": 5,
        "ai_involvement_avg": 0.40,
        "risks_detected": ["COGNITIVE_DELEGATION"],
        "key_decisions": ["Usar arreglo circular por eficiencia O(1)"]
      }
    ],

    "transitions": [
      {
        "from_phase": "exploracion",
        "to_phase": "planificacion",
        "timestamp": "2025-11-18T10:15:00Z",
        "trigger": "PLANNING"
      }
    ],

    "ai_dependency_evolution": [
      {"timestamp": "2025-11-18T10:00:00Z", "ai_involvement": 0.2},
      {"timestamp": "2025-11-18T10:10:00Z", "ai_involvement": 0.3},
      {"timestamp": "2025-11-18T10:20:00Z", "ai_involvement": 0.5}
    ],

    "strategy_changes": [
      "Cambio de lista enlazada a arreglo circular",
      "Cambio de indices simples a modular arithmetic"
    ]
  }
}
```

### 9.3 Visualizacion del Camino

```
INICIO
   |
   v
+-------------+     +---------------+     +----------------+     +-----------+
| EXPLORACION | --> | PLANIFICACION | --> | IMPLEMENTACION | --> | VALIDACION|
|  15 min     |     |   20 min      |     |    35 min      |     |  20 min   |
|  AI: 0.25   |     |   AI: 0.40    |     |    AI: 0.45    |     |  AI: 0.20 |
+-------------+     +---------------+     +----------------+     +-----------+
                           |
                           v
                    DECISION CLAVE:
                    "Usar arreglo circular"
                    Justificacion: O(1)
```

---

## 10. Grafo de Trazabilidad de Sesion

### 10.1 Endpoint

**GET /api/v1/traceability/session/{session_id}**

Construye un grafo jerarquico de 4 niveles que conecta todos los artefactos de una sesion.

### 10.2 Estructura del Grafo

```
NIVEL 1: Eventos de Simulador
    |
    +-- Event: user_story_created
    |       |
    |       +-- NIVEL 2: Trazas Cognitivas
    |               |
    |               +-- Trace: student_prompt ("Como defino criterios?")
    |                       |
    |                       +-- NIVEL 3: Riesgos Detectados
    |                               |
    |                               +-- Risk: COGNITIVE_DELEGATION (MEDIUM)
    |
    +-- Event: sprint_planning_completed
            |
            +-- Trace: ai_response
                    |
                    +-- Risk: (ninguno)

NIVEL 4: Evaluaciones (a nivel de sesion)
    |
    +-- Evaluation: Score 7.5/10
            |
            +-- Competency: INTERMEDIO
            +-- AI Dependency: 0.35
```

### 10.3 Response del Grafo

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "student_id": "student_001",
    "activity_id": "simulator_po",
    "simulator_type": "product_owner",
    "start_time": "2025-11-18T10:00:00Z",
    "end_time": "2025-11-18T11:30:00Z",

    "artifacts": [
      {
        "level": 1,
        "type": "event",
        "id": "evt_001",
        "name": "user_story_created",
        "status": "completed",
        "timestamp": "2025-11-18T10:05:00Z",
        "data": {
          "simulator_type": "product_owner",
          "event_data": {"story_id": "US-001"}
        },
        "children": [
          {
            "level": 2,
            "type": "trace",
            "id": "trace_001",
            "name": "student_prompt",
            "data": {
              "content_preview": "Como defino criterios de aceptacion...",
              "cognitive_state": "exploracion",
              "ai_involvement": 0.3
            },
            "children": [
              {
                "level": 3,
                "type": "risk",
                "id": "risk_001",
                "name": "COGNITIVE_DELEGATION - MEDIUM",
                "status": "detected",
                "data": {
                  "dimension": "cognitive",
                  "description": "Delegacion parcial detectada"
                }
              }
            ]
          }
        ]
      },
      {
        "level": 4,
        "type": "evaluation",
        "id": "eval_001",
        "name": "Evaluacion - Score: 7.5",
        "status": "completed",
        "data": {
          "overall_score": 7.5,
          "overall_competency_level": "INTERMEDIO",
          "ai_dependency_score": 0.35
        }
      }
    ],

    "summary": {
      "total_events": 5,
      "total_traces": 12,
      "total_risks": 2,
      "total_evaluations": 1,
      "risks_by_level": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 1, "LOW": 1},
      "risks_resolved": 0,
      "risks_pending": 2,
      "avg_ai_involvement": 0.35,
      "session_duration_minutes": 90.0
    }
  }
}
```

---

## 11. Integracion con Otros Agentes

### 11.1 Diagrama de Integracion

```
+------------------+
|   AIGateway      |  ---- Registra traza de INPUT (N4)
+--------+---------+       Registra traza de OUTPUT (N4)
         |
         v
+--------+---------+
|      TC-N4       |<---------+----------+----------+
| (Trazabilidad)   |          |          |          |
+--------+---------+          |          |          |
         |                    |          |          |
         |         +----------+    +-----+----+     |
         |         |               |          |     |
         v         v               v          v     |
+--------+-+ +-----+-----+ +------+---+ +----+----+ |
| T-IA-Cog | | E-IA-Proc | | S-IA-X   | | AR-IA   | |
| (Tutor)  | | (Eval)    | | (Sim)    | | (Risk)  | |
+----+-----+ +-----+-----+ +-----+----+ +----+----+ |
     |             |             |           |      |
     |             |             |           |      |
     +-------------+-------------+-----------+------+
                         |
                         v
              capture_interaction()
              capture_design_decision()
```

### 11.2 TC-N4 <-> AIGateway

**Flujo de Interaccion**:

1. AIGateway recibe request del cliente
2. Crea traza de INPUT (level=N4) con content=prompt
3. Procesa con agente correspondiente
4. Crea traza de OUTPUT (level=N4) con content=response
5. Vincula ambas trazas a la sesion

**Codigo en AIGateway** (simplificado):
```python
# Traza de entrada
input_trace = tc_n4.capture_interaction(
    student_id=session.student_id,
    activity_id=session.activity_id,
    interaction_type=InteractionType.STUDENT_PROMPT,
    content=prompt,
    cognitive_intent=classified_intent
)

# Procesar con agente
response = await agent.process(prompt, context)

# Traza de salida
output_trace = tc_n4.capture_interaction(
    student_id=session.student_id,
    activity_id=session.activity_id,
    interaction_type=InteractionType.AI_RESPONSE,
    content=response,
    parent_trace_id=input_trace.id
)
```

### 11.3 TC-N4 <-> T-IA-Cog (Tutor)

**Flujo de Interaccion**:

1. Tutor recibe prompt del estudiante
2. Analiza estado cognitivo
3. Genera intervencion pedagogica
4. Registra traza con `cognitive_state`, `intervention_type`

**Datos Registrados**:
- `cognitive_state`: Estado cognitivo detectado
- `cognitive_intent`: Intencion clasificada
- `strategy_type`: Tipo de estrategia pedagogica
- `decision_justification`: Si el estudiante justifico

### 11.4 TC-N4 <-> E-IA-Proc (Evaluador)

**Flujo de Interaccion**:

1. Evaluador solicita trazas de la sesion
2. TC-N4 provee `reconstruct_cognitive_path()`
3. Evaluador analiza:
   - Progresion de estados cognitivos
   - Justificaciones de decisiones
   - Alternativas consideradas
   - Dependencia de IA a lo largo del tiempo

**Datos Utilizados**:
```python
cognitive_path = tc_n4.reconstruct_cognitive_path(sequence_id)

# Evaluador analiza:
phases = cognitive_path["phases"]
key_decisions = cognitive_path["key_decisions"]
ai_dependency = cognitive_path["ai_dependency_score"]
```

### 11.5 TC-N4 <-> AR-IA (Analista de Riesgos)

**Flujo de Interaccion**:

1. AR-IA detecta riesgo en traza
2. Crea RiskDB con `trace_ids` apuntando a trazas relacionadas
3. TC-N4 vincula riesgos en grafo de trazabilidad
4. Grafo muestra: Evento → Traza → Riesgo

**Vinculacion**:
```python
# AR-IA crea riesgo
risk = Risk(
    session_id=session_id,
    dimension=RiskDimension.COGNITIVE,
    trace_ids=[trace.id],  # Vinculo a trazas
    ...
)

# TC-N4 reconstruye grafo con riesgos vinculados
traceability_graph = get_session_traceability(session_id)
# -> artifacts[0].children[0].children contiene los riesgos
```

### 11.6 TC-N4 <-> S-IA-X (Simuladores)

**Flujo de Interaccion**:

1. Simulador genera eventos (SimulatorEventDB)
2. TC-N4 captura eventos como Nivel 1 del grafo
3. Trazas cognitivas se vinculan temporalmente a eventos
4. Grafo muestra: Evento_Simulador → Trazas → Riesgos

---

## 12. Deteccion de Decisiones Sin Justificar

### 12.1 Metodo detect_unjustified_decisions()

**Ubicacion**: `backend/agents/traceability.py` linea 311

Este metodo implementa HU-EST-005: Deteccion de decisiones sin justificacion.

```python
def detect_unjustified_decisions(
    self,
    session_id: str,
    threshold: float = 0.7  # 70% minimo de decisiones justificadas
) -> Dict[str, Any]:
```

### 12.2 Patrones de Deteccion

El metodo busca estos patrones en el contenido de las trazas:

```python
decision_keywords = [
    "elegi", "decidi", "voy a usar", "implemento con",
    "opto por", "selecciono", "usare", "aplico"
]
```

### 12.3 Niveles de Alerta

| Ratio de Justificacion | Nivel de Alerta | Recomendacion |
|------------------------|-----------------|---------------|
| < 30% | HIGH | CRITICO: Exigir documentacion explicita de POR QUE |
| 30% - 50% | MEDIUM | MODERADO: Solicitar justificaciones y alternativas |
| 50% - 70% | LOW | LEVE: Reforzar importancia de justificar decisiones |
| >= 70% | None | OK: Cumple umbral minimo |

### 12.4 Response del Analisis

```json
{
  "session_id": "session_abc123",
  "total_decisions": 10,
  "justified_decisions": 4,
  "unjustified_decisions": 6,
  "justification_ratio": 0.4,
  "threshold": 0.7,
  "alert": true,
  "alert_level": "MEDIUM",
  "unjustified_list": [
    {
      "trace_id": "trace_001",
      "decision": "Voy a usar un arreglo para la cola",
      "timestamp": "2025-11-18T10:15:00Z"
    }
  ],
  "recommendation": "MODERADO: Menos de la mitad de las decisiones estan justificadas. Se recomienda solicitar al estudiante que justifique sus elecciones y considere alternativas."
}
```

---

## 13. Exportacion para Evaluacion

### 13.1 Metodo export_for_evaluation()

```python
def export_for_evaluation(
    self,
    sequence_id: str,
    format: str = "json"
) -> Dict[str, Any]:
```

### 13.2 Estructura de Exportacion

```json
{
  "export_metadata": {
    "sequence_id": "seq_abc123",
    "export_date": "2025-11-18T12:00:00Z",
    "format": "json"
  },
  "student_info": {
    "student_id": "student_001",
    "activity_id": "prog2_tp1"
  },
  "cognitive_reconstruction": {
    "sequence_id": "seq_abc123",
    "duration": 3600.0,
    "total_interactions": 15,
    "cognitive_path": ["exploracion", "planificacion", "implementacion"],
    "phases": [...],
    "key_decisions": [...],
    "ai_dependency_score": 0.35
  },
  "full_traces": [
    {
      "id": "trace_001",
      "timestamp": "2025-11-18T10:00:00Z",
      "type": "student_prompt",
      "content": "Como implemento una cola?",
      "cognitive_intent": "UNDERSTANDING",
      "decision_justification": null
    },
    {
      "id": "trace_002",
      "timestamp": "2025-11-18T10:05:00Z",
      "type": "ai_response",
      "content": "Para implementar una cola, primero...",
      "cognitive_intent": null,
      "decision_justification": null
    }
  ]
}
```

---

## 14. Resumen Ejecutivo

### 14.1 Componentes Clave

| Componente | Archivo | Responsabilidad |
|------------|---------|-----------------|
| TrazabilidadN4Agent | `traceability.py` | Captura y reconstruccion de trazas |
| CognitiveTrace | `models/trace.py` | Modelo de dominio para trazas |
| TraceSequence | `models/trace.py` | Secuencia de trazas |
| CognitiveTraceDB | `database/models.py` | Modelo ORM con 6 dimensiones N4 |
| TraceSequenceDB | `database/models.py` | Modelo ORM para secuencias |
| TraceRepository | `repositories.py` | Persistencia de trazas |
| TraceSequenceRepository | `repositories.py` | Persistencia de secuencias |

### 14.2 Los 4 Niveles

```
N1 Superficial → N2 Tecnico → N3 Interaccional → N4 Cognitivo
```

### 14.3 Las 6 Dimensiones N4

```
1. Semantica (Que entendio?)
2. Algoritmica (Como evoluciono?)
3. Cognitiva (Por que decidio?)
4. Interaccional (Como pregunto?)
5. Etica/Riesgo (Hubo fraude?)
6. Procesual (Cuanto tardo?)
```

### 14.4 API Endpoints

| Endpoint | Proposito |
|----------|-----------|
| GET /traces/{session_id} | Listar trazas con filtros |
| GET /traces/student/{id} | Trazas de un estudiante |
| GET /traceability/{trace_id} | Pipeline N1-N4 de una traza |
| GET /traceability/session/{id} | Grafo completo de sesion |
| GET /cognitive-path/{session_id} | Camino cognitivo reconstructivo |
| GET /cognitive-path/{session_id}/summary | Solo metricas |

### 14.5 Tablas de Persistencia

| Tabla | Modelo | Contenido |
|-------|--------|-----------|
| `cognitive_traces` | CognitiveTraceDB | Trazas con 6 dimensiones JSONB |
| `trace_sequences` | TraceSequenceDB | Secuencias con trace_ids JSON |

### 14.6 Integracion Inter-Agentes

```
TC-N4 <==> AIGateway (registra INPUT/OUTPUT)
TC-N4 <==> T-IA-Cog (cognitive_state, intervention)
TC-N4 <==> E-IA-Proc (reconstruct_cognitive_path)
TC-N4 <==> AR-IA (trace_ids en riesgos)
TC-N4 <==> S-IA-X (eventos como Nivel 1)
```

---

**Documento generado**: Diciembre 2025
**Version**: 1.0
**Autor**: Claude Code (Arquitectura Backend)
**Proyecto**: AI-Native MVP - Tesis Doctoral

---

## Referencias

- `backend/agents/traceability.py` - Agente TC-N4 principal (455 lineas)
- `backend/models/trace.py` - Modelos de dominio (217 lineas)
- `backend/api/schemas/trace.py` - Schemas API (234 lineas)
- `backend/api/routers/traces.py` - Router de trazas (272 lineas)
- `backend/api/routers/traceability.py` - Router N4 (425 lineas)
- `backend/api/routers/cognitive_path.py` - Router camino cognitivo (306 lineas)
- `backend/database/models.py` - Modelos ORM (CognitiveTraceDB, TraceSequenceDB)
- `backend/database/repositories.py` - Repositorios (TraceRepository, TraceSequenceRepository)
- CLAUDE.md - Documentacion general del proyecto