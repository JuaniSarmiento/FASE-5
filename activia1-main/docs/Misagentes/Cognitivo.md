# Explicación Detallada del Agente Tutor Cognitivo (T-IA-Cog)

## Documento de Análisis Técnico-Pedagógico

**Autor**: Análisis realizado por Claude Code
**Fecha**: Diciembre 2025
**Versión del Código**: 2.0 (Tutor Socrático Personalizado)
**Archivo Principal**: `backend/agents/tutor.py`

---

## 1. Visión General

### 1.1 ¿Qué es el T-IA-Cog?

El **T-IA-Cog** (Tutor IA Disciplinar Cognitivo) es un agente de inteligencia artificial diseñado para funcionar como un **tutor socrático**. Su función principal es **guiar el razonamiento del estudiante** sin sustituirlo, aplicando principios pedagógicos fundamentados en teorías cognitivas.

### 1.2 Principio Fundamental

> **"Amplificar capacidades del estudiante sin sustituirlas"**

El tutor NUNCA entrega código completo ni soluciones directas. En su lugar, utiliza:
- Preguntas socráticas
- Pistas graduadas
- Refuerzo conceptual
- Exigencia de explicitación del pensamiento

### 1.3 Fundamentos Teóricos

El agente está basado en teorías pedagógicas reconocidas:

| Teoría | Autor | Aplicación en el Tutor |
|--------|-------|------------------------|
| Cognición Distribuida | Hutchins, 1995 | El conocimiento se construye entre el estudiante y el tutor |
| Cognición Extendida | Clark & Chalmers, 1998 | La IA extiende (no reemplaza) las capacidades cognitivas |
| Carga Cognitiva | Sweller, 1988 | Reducir carga extrínseca, favorecer carga germinal |
| Autorregulación | Zimmerman, 2002 | Fomentar metacognición y autoevaluación |

---

## 2. Arquitectura del Sistema

### 2.1 Componentes Principales

```
┌─────────────────────────────────────────────────────────────────┐
│                    TutorCognitivoAgent                          │
│                    (Clase Principal)                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────┐  ┌───────────────────┐                   │
│  │  TutorRulesEngine │  │TutorGovernanceEng │                   │
│  │  (tutor_rules.py) │  │(tutor_governance) │                   │
│  │                   │  │                   │                   │
│  │ • 4 Reglas        │  │ • IPC             │                   │
│  │   Inquebrantables │  │ • GSR             │                   │
│  │ • Validaciones    │  │ • Semáforos       │                   │
│  └───────────────────┘  └───────────────────┘                   │
│                                                                  │
│  ┌───────────────────┐  ┌───────────────────┐                   │
│  │TutorMetadataTrack │  │ TutorSystemPrompts│                   │
│  │(tutor_metadata.py)│  │ (tutor_prompts.py)│                   │
│  │                   │  │                   │                   │
│  │ • Registro N4     │  │ • Templates LLM   │                   │
│  │ • Analytics       │  │ • Personalización │                   │
│  └───────────────────┘  └───────────────────┘                   │
│                                                                  │
│  ┌───────────────────┐                                          │
│  │   LLM Provider    │ ← Ollama/Phi-3 (o Mock para testing)     │
│  └───────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Archivos del Subsistema Tutor

| Archivo | Propósito | Líneas ~|
|---------|-----------|---------|
| `tutor.py` | Clase principal `TutorCognitivoAgent` | ~1240 |
| `tutor_rules.py` | Motor de reglas pedagógicas | ~470 |
| `tutor_governance.py` | Sistema de semáforos y gobernanza | ~530 |
| `tutor_metadata.py` | Tracking y analytics N4 | ~490 |
| `tutor_prompts.py` | Templates de prompts para LLM | ~Variable |

---

## 3. Pipeline de Procesamiento

### 3.1 Flujo Completo de una Interacción

```
┌──────────────┐
│  Estudiante  │
│  (prompt)    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│ FASE 1: IPC (Ingesta y Comprensión de Prompt)                │
│                                                               │
│ • Detectar intención (exploración, depuración, delegación)   │
│ • Detectar estado cognitivo                                   │
│ • Estimar nivel de autonomía (0-1)                           │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ FASE 2: GSR (Gobernanza y Semáforo de Riesgo)                │
│                                                               │
│ • Evaluar riesgo de delegación                               │
│ • Evaluar dependencia de IA                                  │
│ • Detectar patrones de plagio                                │
│ • Asignar semáforo: 🟢 VERDE | 🟡 AMARILLO | 🔴 ROJO        │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ FASE 3: Selección de Estrategia de Andamiaje                 │
│                                                               │
│ • Determinar tipo de respuesta                               │
│ • Establecer nivel de ayuda                                  │
│ • Definir restricciones                                      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ FASE 4: Chequeo de Reglas Pedagógicas                        │
│                                                               │
│ • Regla Anti-Solución                                        │
│ • Modo Socrático Prioritario                                 │
│ • Exigencia de Explicitación                                 │
│ • Refuerzo Conceptual                                        │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ FASE 5: Generación de Respuesta                              │
│                                                               │
│ • Si hay violación crítica → Rechazo Pedagógico              │
│ • Si no → Generar respuesta según estrategia:                │
│   - socratic_questioning                                     │
│   - conceptual_explanation                                   │
│   - guided_hints                                             │
│   - clarification_request                                    │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────┐
│ FASE 6: Registro de Metadata N4                              │
│                                                               │
│ • Tipo de intervención                                       │
│ • Estado cognitivo detectado                                 │
│ • Nivel de ayuda otorgado                                    │
│ • Reglas aplicadas                                           │
│ • Semáforo activo                                            │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌──────────────┐
│  Respuesta   │
│  al alumno   │
└──────────────┘
```

### 3.2 Método Principal: `process_student_request()`

```python
async def process_student_request(
    self,
    session_id: str,           # ID de sesión
    student_prompt: str,        # Pregunta del estudiante
    student_profile: Dict,      # Perfil con métricas
    conversation_history: List  # Historial de conversación
) -> Dict[str, Any]:
    """
    Retorna:
    - message: Respuesta del tutor
    - intervention_type: Tipo de intervención
    - metadata: Metadata completa para N4
    - semaforo: Estado del semáforo
    """
```

---

## 4. Las 4 Reglas Pedagógicas Inquebrantables

### 4.1 Regla #1: Anti-Solución Directa (`ANTI_SOLUCION`)

**Principio**: El tutor NUNCA entrega código completo.

**Detección de solicitudes de código**:
```python
code_request_patterns = [
    "haceme", "dame el código", "muéstrame el código",
    "escribe el código", "cual es el código",
    "resuelve esto", "solucioná", "hacé el ejercicio",
    "implementá", "codificá", "programá esto"
]
```

**Respuesta ante violación**:
- Genera un **Rechazo Pedagógico** con mensaje explicativo
- Plantea una **contra-pregunta** para redirigir el pensamiento

### 4.2 Regla #2: Modo Socrático Prioritario (`MODO_SOCRATICO`)

**Principio**: El default es preguntar, no responder directamente.

**Comportamiento**:
- En primera interacción → Siempre preguntas socráticas
- Si dio >2 explicaciones sin preguntar → Forzar pregunta
- Priorizar que el estudiante verbalice su razonamiento

### 4.3 Regla #3: Exigencia de Explicitación (`EXIGIR_EXPLICITACION`)

**Principio**: Forzar al alumno a convertir pensamiento en palabras.

**Lo que exige**:
1. **Plan** antes de codificar
2. **Pseudocódigo** de alto nivel
3. **Justificación** de decisiones

**Umbral mínimo**: 50 caracteres de explicación

### 4.4 Regla #4: Refuerzo Conceptual (`REFUERZO_CONCEPTUAL`)

**Principio**: Cuando hay error, remitir al concepto teórico, no dar fix sintáctico.

**Mapeo error → concepto**:

| Error Detectado | Concepto Teórico |
|-----------------|------------------|
| `null_pointer` | Invariantes y precondiciones |
| `array_bounds` | Invariantes de estructura de datos |
| `tight_coupling` | Acoplamiento y cohesión |
| `complexity_high` | Complejidad algorítmica |
| `memory_leak` | Gestión de recursos |
| `race_condition` | Concurrencia y sincronización |
| `duplicated_code` | Principio DRY |
| `god_class` | Single Responsibility Principle |

---

## 5. Sistema de Semáforos (Gobernanza)

### 5.1 Estados del Semáforo

| Estado | Significado | Estrategia |
|--------|-------------|------------|
| 🟢 **VERDE** | Bajo riesgo | Interacción normal según intención |
| 🟡 **AMARILLO** | Riesgo medio | Reducir nivel de ayuda, monitorear |
| 🔴 **ROJO** | Riesgo alto | Intervención restrictiva, advertencias |

### 5.2 Criterios de Activación

```python
# ROJO - Riesgo Alto
if intent == DELEGACION:
    semaforo = ROJO
    restrictions = ["block_code_generation", "require_justification"]

# Detección de plagio
plagiarism_keywords = [
    "generame", "escribí todo", "hace el proyecto",
    "dame la solución completa", "resolvelo vos"
]

# AMARILLO - Dependencia Alta
if avg_ai_involvement > 0.7:
    semaforo = AMARILLO
    restrictions = ["reduce_help_level", "increase_question_ratio"]

# AMARILLO - Solicitudes sin trabajo propio
if consecutive_requests_without_work >= 5:
    semaforo = AMARILLO
    restrictions = ["require_work_shown"]
```

### 5.3 Intenciones del Estudiante (PromptIntent)

| Intención | Descripción | Estrategia de Respuesta |
|-----------|-------------|-------------------------|
| `EXPLORACION` | Está explorando el problema | Preguntas socráticas |
| `DEPURACION` | Está debugueando código | Pistas graduadas |
| `DELEGACION` | Quiere que la IA resuelva todo | **Rechazo + Contra-pregunta** |
| `CLARIFICACION` | Necesita entender conceptos | Explicación conceptual |
| `VALIDACION` | Quiere validar su enfoque | Preguntas reflexivas |

---

## 6. Tipos de Intervención Pedagógica

### 6.1 Catálogo de Intervenciones

| Tipo | Código Enum | Cuándo se Usa |
|------|-------------|---------------|
| Pregunta Socrática | `PREGUNTA_SOCRATICA` | Default, para guiar razonamiento |
| Rechazo Pedagógico | `RECHAZO_PEDAGOGICO` | Ante solicitud de código directo |
| Pista Graduada | `PISTA_GRADUADA` | Cuando necesita orientación sin solución |
| Corrección Conceptual | `CORRECCION_CONCEPTUAL` | Cuando hay error conceptual |
| Exigencia Justificación | `EXIGENCIA_JUSTIFICACION` | Cuando no explica su razonamiento |
| Exigencia Pseudocódigo | `EXIGENCIA_PSEUDOCODIGO` | Antes de implementar |
| Remisión a Teoría | `REMISION_TEORIA` | Para refuerzo conceptual |

### 6.2 Niveles de Ayuda (HelpLevel)

```python
class HelpLevel(str, Enum):
    MINIMO = "minimo"   # Solo preguntas orientadoras
    BAJO = "bajo"       # Pistas muy generales
    MEDIO = "medio"     # Pistas con algo de detalle
    ALTO = "alto"       # Explicaciones detalladas (sin código completo)
```

### 6.3 Niveles de Andamiaje Cognitivo

```python
class CognitiveScaffoldingLevel(str, Enum):
    NOVATO = "novato"       # Más explicaciones, ejemplos parciales
    INTERMEDIO = "intermedio"  # Balance entre guía y autonomía
    AVANZADO = "avanzado"   # Mínima ayuda, máxima exigencia crítica
```

---

## 7. Modos de Tutoría

### 7.1 TutorMode

```python
class TutorMode(str, Enum):
    SOCRATICO = "socratico"       # Preguntas socráticas (DEFAULT)
    EXPLICATIVO = "explicativo"    # Explicaciones conceptuales
    GUIADO = "guiado"             # Pistas graduadas
    METACOGNITIVO = "metacognitivo"  # Reflexión sobre el proceso
```

### 7.2 Generación de Respuestas por Modo

| Modo | Método | Descripción |
|------|--------|-------------|
| Socrático | `_generate_socratic_response()` | Preguntas que guían el razonamiento |
| Explicativo | `_generate_conceptual_explanation()` | Explicación conceptual sin implementación |
| Guiado | `_generate_guided_hints()` | Pistas graduadas por nivel |
| Clarificación | `_generate_clarification_request()` | Pedir más información |

---

## 8. Tablas de Base de Datos Utilizadas

### 8.1 Tablas Directamente Relacionadas

#### **8.1.1 SessionDB** (Tabla: `sessions`)

Almacena las sesiones de aprendizaje donde opera el tutor.

```sql
CREATE TABLE sessions (
    id VARCHAR(36) PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,
    mode VARCHAR(50) DEFAULT 'TUTOR',  -- 'TUTOR', 'SIMULATOR', etc.
    user_id VARCHAR(36),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(20) DEFAULT 'active',

    -- Trazabilidad N4
    learning_objective JSONB,    -- Objetivo de aprendizaje
    cognitive_status JSONB,      -- Estado cognitivo del alumno
    session_metrics JSONB,       -- Métricas agregadas

    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Campos relevantes para el Tutor**:
- `mode = 'TUTOR'`: Indica que la sesión usa el agente tutor
- `cognitive_status`: Estado cognitivo actualizado dinámicamente
- `session_metrics`: Incluye `ai_dependency_score`

#### **8.1.2 CognitiveTraceDB** (Tabla: `cognitive_traces`)

Almacena trazas cognitivas N4 de cada interacción con el tutor.

```sql
CREATE TABLE cognitive_traces (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    -- Clasificación
    trace_level VARCHAR(20) DEFAULT 'n4_cognitivo',
    interaction_type VARCHAR(50) NOT NULL,  -- 'tutor_query', 'hint_request', etc.

    -- Contenido
    content TEXT NOT NULL,
    context JSON,
    trace_metadata JSON,

    -- Estado Cognitivo
    cognitive_state VARCHAR(50),       -- 'exploracion', 'depuracion', etc.
    cognitive_intent VARCHAR(200),
    decision_justification TEXT,
    alternatives_considered JSON,
    strategy_type VARCHAR(100),

    -- AI Involvement
    ai_involvement FLOAT DEFAULT 0.0,  -- 0.0 a 1.0

    -- 6 DIMENSIONES N4
    semantic_understanding JSONB,   -- Dimensión Semántica
    algorithmic_evolution JSONB,    -- Dimensión Algorítmica
    cognitive_reasoning JSONB,      -- Dimensión Cognitiva
    interactional_data JSONB,       -- Dimensión Interaccional
    ethical_risk_data JSONB,        -- Dimensión Ética/Riesgo
    process_data JSONB,             -- Dimensión Procesual

    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Las 6 Dimensiones N4 almacenadas**:

| Dimensión | Campo JSONB | Qué Almacena |
|-----------|-------------|--------------|
| Semántica | `semantic_understanding` | Interpretación del problema, conceptos identificados |
| Algorítmica | `algorithmic_evolution` | Versiones de código, alternativas exploradas |
| Cognitiva | `cognitive_reasoning` | Razonamientos explícitos, justificaciones |
| Interaccional | `interactional_data` | Tipo de prompt, calidad, tipo de respuesta IA |
| Ética/Riesgo | `ethical_risk_data` | Indicadores de plagio, delegación |
| Procesual | `process_data` | Tiempos, secuencia lógica, eficiencia |

#### **8.1.3 RiskDB** (Tabla: `risks`)

Almacena riesgos detectados por el tutor.

```sql
CREATE TABLE risks (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    -- Clasificación
    risk_type VARCHAR(100) NOT NULL,    -- 'COGNITIVE_DELEGATION', 'AI_DEPENDENCY'
    risk_level VARCHAR(20) NOT NULL,    -- 'low', 'medium', 'high', 'critical'
    dimension VARCHAR(50) NOT NULL,     -- 'cognitive', 'ethical', etc.

    -- Descripción
    description TEXT NOT NULL,
    evidence JSON,
    trace_ids JSON,                     -- Trazas relacionadas

    -- Análisis
    root_cause TEXT,
    impact_assessment TEXT,

    -- Recomendaciones
    recommendations JSON,
    pedagogical_intervention TEXT,

    -- Estado
    resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP,
    detected_by VARCHAR(50) DEFAULT 'AR-IA',

    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Riesgos típicos detectados por el Tutor**:

| risk_type | dimension | Descripción |
|-----------|-----------|-------------|
| `COGNITIVE_DELEGATION` | `cognitive` | Estudiante delega todo a la IA |
| `AI_DEPENDENCY` | `cognitive` | Dependencia excesiva (>0.7) |
| `LACK_JUSTIFICATION` | `cognitive` | No justifica sus decisiones |
| `SUPERFICIAL_REASONING` | `cognitive` | Razonamiento superficial |
| `ACADEMIC_INTEGRITY` | `ethical` | Posible intento de plagio |

#### **8.1.4 EvaluationDB** (Tabla: `evaluations`)

Almacena evaluaciones de proceso generadas.

```sql
CREATE TABLE evaluations (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    -- Evaluación general
    overall_competency_level VARCHAR(50) NOT NULL,
    overall_score FLOAT NOT NULL,  -- 0.0 a 10.0

    -- Dimensiones (JSON para flexibilidad)
    dimensions JSON,

    -- Feedback
    key_strengths JSON,
    improvement_areas JSON,
    recommendations JSON,

    -- Análisis
    reasoning_analysis JSON,
    git_analysis JSON,
    ai_dependency_score FLOAT DEFAULT 0.0,
    ai_dependency_metrics JSON,

    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### **8.1.5 StudentProfileDB** (Tabla: `student_profiles`)

Perfil del estudiante usado para personalizar el andamiaje.

```sql
CREATE TABLE student_profiles (
    id VARCHAR(36) PRIMARY KEY,
    student_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(36),

    -- Datos básicos
    name VARCHAR(200),
    email VARCHAR(200),

    -- Analytics de aprendizaje
    total_sessions INTEGER DEFAULT 0,
    total_interactions INTEGER DEFAULT 0,
    average_ai_dependency FLOAT DEFAULT 0.0,
    average_competency_level VARCHAR(50),
    average_competency_score FLOAT,

    -- Perfil de riesgo
    total_risks INTEGER DEFAULT 0,
    critical_risks INTEGER DEFAULT 0,
    risk_trends JSON,

    -- Tracking de progreso
    competency_evolution JSON,
    last_activity_date TIMESTAMP,

    -- Preferencias y patrones
    preferred_language VARCHAR(10) DEFAULT 'es',
    cognitive_preferences JSONB,
    learning_patterns JSONB,
    competency_levels JSONB,
    strengths JSON,
    areas_for_improvement JSON,

    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Campos usados por el Tutor**:
- `average_ai_dependency`: Determina si activar semáforo AMARILLO/ROJO
- `learning_patterns`: Patrones de aprendizaje detectados
- `competency_levels`: Nivel por área de competencia

### 8.2 Tablas Auxiliares

#### **8.2.1 TraceSequenceDB** (Tabla: `trace_sequences`)

Secuencias de trazas para análisis de patrones.

```sql
CREATE TABLE trace_sequences (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,

    -- Análisis agregado
    reasoning_path JSON,
    strategy_changes INTEGER DEFAULT 0,
    ai_dependency_score FLOAT DEFAULT 0.0,

    trace_ids JSON,  -- Lista de IDs de trazas

    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### **8.2.2 UserDB** (Tabla: `users`)

Usuarios autenticados.

```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,

    full_name VARCHAR(255),
    student_id VARCHAR(100) UNIQUE,

    roles JSONB,  -- ["student", "instructor", "admin"]
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,

    last_login TIMESTAMP,
    login_count INTEGER DEFAULT 0,

    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## 9. Diagrama de Relaciones de Base de Datos

```
┌──────────────────┐
│     users        │
│  (UserDB)        │
└────────┬─────────┘
         │ 1:N
         ▼
┌──────────────────┐       ┌──────────────────┐
│    sessions      │◄──────│ student_profiles │
│   (SessionDB)    │  N:1  │(StudentProfileDB)│
└────────┬─────────┘       └──────────────────┘
         │
    ┌────┼────────────────────────┬──────────────────┐
    │    │                        │                  │
    │ 1:N│                     1:N│               1:N│
    ▼    ▼                        ▼                  ▼
┌────────────────┐  ┌──────────────────┐  ┌────────────────────┐
│cognitive_traces│  │      risks       │  │    evaluations     │
│(CognitiveTraceDB)│(RiskDB)           │  │  (EvaluationDB)    │
└────────────────┘  └──────────────────┘  └────────────────────┘
    │
    │ N:M (via trace_ids JSON)
    ▼
┌────────────────────┐
│  trace_sequences   │
│ (TraceSequenceDB)  │
└────────────────────┘
```

---

## 10. Flujo de Datos en una Interacción Típica

### 10.1 Escenario: Estudiante pide código directamente

```
Estudiante: "Dame el código para implementar una cola circular"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ FASE 1: IPC                                                     │
│ • intent = DELEGACION (detectado por "dame el código")          │
│ • cognitive_state = "delegacion_critica"                        │
│ • autonomy_level = 0.2 (muy bajo)                               │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ FASE 2: GSR                                                     │
│ • semaforo = 🔴 ROJO                                            │
│ • risk_type = "delegacion_total"                                │
│ • restrictions = ["block_code_generation", "require_justification"]
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ FASE 4: Chequeo de Reglas                                       │
│ • Regla ANTI_SOLUCION → VIOLADA                                 │
│ • intervention_type = RECHAZO_PEDAGOGICO                        │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ RESPUESTA AL ESTUDIANTE:                                        │
│                                                                 │
│ 🚫 No puedo darte el código directamente                        │
│                                                                 │
│ Entiendo que querés la solución rápida, pero mi trabajo es      │
│ ayudarte a aprender, no a resolver el problema por vos.         │
│                                                                 │
│ 💭 En vez de eso, respondeme:                                   │
│ 1. ¿Qué entendés que tenés que resolver?                        │
│ 2. ¿Qué enfoque se te ocurre?                                   │
│ 3. ¿Qué conceptos creés que son relevantes?                     │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ REGISTRO EN DB:                                                 │
│                                                                 │
│ → cognitive_traces: Nueva traza N4                              │
│   • interaction_type = "tutor_query"                            │
│   • cognitive_state = "delegacion_critica"                      │
│   • ai_involvement = 0.9 (alto - intento de delegación)         │
│   • interactional_data = {                                      │
│       "prompt_type": "delegation",                              │
│       "ai_response_type": "rejection",                          │
│       "student_agency": 0.1                                     │
│     }                                                           │
│                                                                 │
│ → risks: Nuevo riesgo                                           │
│   • risk_type = "COGNITIVE_DELEGATION"                          │
│   • risk_level = "high"                                         │
│   • dimension = "cognitive"                                     │
│   • detected_by = "T-IA-Cog"                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Escenario: Estudiante hace pregunta exploratoria

```
Estudiante: "Estoy tratando de entender cómo funciona una cola circular.
             Pensé en usar un arreglo pero no sé cómo manejar el wrap-around"
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ FASE 1: IPC                                                     │
│ • intent = EXPLORACION                                          │
│ • cognitive_state = "exploracion"                               │
│ • autonomy_level = 0.7 (alto - muestra pensamiento propio)      │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ FASE 2: GSR                                                     │
│ • semaforo = 🟢 VERDE                                           │
│ • risk_type = None                                              │
│ • restrictions = []                                             │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ FASE 3: Estrategia                                              │
│ • response_type = "socratic_questioning"                        │
│ • help_level = "bajo" (estudiante avanzado)                     │
│ • intervention_type = PREGUNTA_SOCRATICA                        │
│ • allow_pseudocode = true                                       │
└─────────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ RESPUESTA (generada por LLM con system prompt socrático):       │
│                                                                 │
│ ## Análisis del Problema                                        │
│                                                                 │
│ Excelente que ya identificaste el uso de un arreglo y el        │
│ desafío del wrap-around. Antes de avanzar:                      │
│                                                                 │
│ 1. ¿Qué operación matemática conocés que te permitiría          │
│    "volver al inicio" cuando llegás al final del arreglo?       │
│                                                                 │
│ 2. ¿Cómo distinguirías entre una cola vacía y una llena         │
│    si usás solo índices front y rear?                           │
│                                                                 │
│ 3. ¿Podés describir con palabras (no código) qué pasaría        │
│    al encolar un elemento cuando rear está en el último índice? │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Sistema de Metadata N4

### 11.1 TutorInterventionMetadata

Cada intervención del tutor genera metadata estructurada:

```python
metadata = {
    "interaction_id": "uuid-único",
    "session_id": "session-uuid",
    "timestamp": "2025-12-13T10:30:00",

    # Tipo de intervención
    "intervention_type": "pregunta_socratica",

    # Contexto del estudiante
    "student_level": "intermedio",
    "student_intent": "exploracion",
    "cognitive_state_detected": "exploracion",
    "student_autonomy_level": 0.7,

    # Estado del sistema
    "semaforo_state": "verde",
    "help_level": "bajo",

    # Reglas aplicadas
    "rules_applied": ["modo_socratico_prioritario"],
    "restrictions_applied": [],

    # Efectividad (post-análisis)
    "effectiveness": "efectiva",
    "student_cognitive_events": [
        "justificacion_decision",
        "descomposicion_problema"
    ]
}
```

### 11.2 Eventos Cognitivos del Estudiante

El sistema detecta eventos cognitivos positivos en las respuestas:

| Evento | Señales de Detección |
|--------|---------------------|
| `FORMULACION_HIPOTESIS` | "creo que", "supongo que", "podría ser" |
| `CAMBIO_ESTRATEGIA` | "voy a intentar", "mejor pruebo", "otra forma" |
| `AUTOCORRECCION` | "me equivoqué", "ahora veo el error" |
| `DESCOMPOSICION_PROBLEMA` | "primero", "después", "paso 1", "subproblema" |
| `JUSTIFICACION_DECISION` | "porque", "ya que", "debido a" |
| `REFLEXION_METACOGNITIVA` | "entiendo que", "me doy cuenta", "aprendí" |
| `PLANIFICACION` | "mi plan", "planeo", "mi estrategia" |
| `ABANDONO_DELEGACION` | Estudiante muestra trabajo propio tras rechazo |

### 11.3 Analytics N4 de Sesión

```python
analytics = tutor.get_session_analytics_n4(session_id)

# Retorna:
{
    "session_id": "...",
    "total_interventions": 15,

    "intervention_types_distribution": {
        "pregunta_socratica": 8,
        "pista_graduada": 5,
        "rechazo_pedagogico": 2
    },

    "effectiveness_distribution": {
        "muy_efectiva": 4,
        "efectiva": 7,
        "neutra": 3,
        "inefectiva": 1
    },

    "cognitive_events_detected": {
        "justificacion_decision": 6,
        "descomposicion_problema": 4,
        "autocorreccion": 2
    },

    "semaforo_states_distribution": {
        "verde": 12,
        "amarillo": 2,
        "rojo": 1
    },

    "autonomy_progression": [0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7],
    "autonomy_improvement": 0.4,

    "avg_help_level": 0.5  # 0-1 escala
}
```

---

## 12. Integración con LLM (Ollama/Phi-3)

### 12.1 Flujo de Generación

```python
# 1. Construir system prompt personalizado
system_prompt = self.prompts.get_intervention_prompt(
    intervention_type=PREGUNTA_SOCRATICA,
    student_level=INTERMEDIO,
    semaforo_state=VERDE,
    context={...}
)

# 2. Preparar mensajes con historial
messages = conversation_history + [
    {"role": "user", "content": student_prompt}
]

# 3. Llamar al LLM
llm_response = await self.llm_provider.generate(
    messages=messages,
    system_prompt=system_prompt,
    temperature=0.7,
    max_tokens=500
)
```

### 12.2 Fallback a Templates

Si el LLM no está disponible o falla, el tutor usa **templates predefinidos**:

```python
if not self.llm_provider:
    # Usar plantillas estáticas
    questions = self._formulate_socratic_questions(prompt, cognitive_state)
    message = self._format_questions(questions)
```

---

## 13. Resumen de Buenas Prácticas del Código

### 13.1 Patrones de Diseño Utilizados

| Patrón | Implementación |
|--------|----------------|
| **Strategy** | Diferentes estrategias de andamiaje según semáforo |
| **Chain of Responsibility** | Pipeline IPC → GSR → Andamiaje → Reglas |
| **Template Method** | Generación de respuestas con hooks personalizables |
| **Factory** | Creación de metadata y respuestas |
| **Observer** | Registro de eventos cognitivos |

### 13.2 Consideraciones de Seguridad

1. **Nunca confiar en input del estudiante** - Sanitización implícita
2. **Logs estructurados** para auditoría
3. **Separación de responsabilidades** entre componentes
4. **Metadata inmutable** para trazabilidad

### 13.3 Escalabilidad

- **Stateless design**: El tutor no mantiene estado en memoria
- **Todo persiste en PostgreSQL** vía repositories
- **Compatible con horizontal scaling**

---

## 14. Conclusiones

### 14.1 Fortalezas del Diseño

1. **Fundamentación pedagógica sólida**: Basado en teorías cognitivas reconocidas
2. **Reglas inquebrantables**: Garantizan comportamiento ético del tutor
3. **Sistema de semáforos**: Control graduado de riesgos
4. **Trazabilidad N4 completa**: Todo queda registrado para análisis
5. **Arquitectura modular**: Fácil de extender y mantener

### 14.2 Tablas de BD Involucradas (Resumen)

| Tabla | Propósito Principal |
|-------|---------------------|
| `sessions` | Sesiones de tutoría |
| `cognitive_traces` | Trazas N4 de cada interacción |
| `risks` | Riesgos detectados |
| `evaluations` | Evaluaciones de proceso |
| `student_profiles` | Perfiles para personalización |
| `trace_sequences` | Secuencias para análisis de patrones |
| `users` | Autenticación |

### 14.3 Métricas Clave del Sistema

- **AI Involvement**: 0.0-1.0 (objetivo: mantener bajo)
- **Autonomy Level**: 0.0-1.0 (objetivo: incrementar con el tiempo)
- **Intervention Effectiveness**: muy_efectiva → contraproducente
- **Semáforo dominante**: Verde = buen aprendizaje

---

**Documento generado para análisis y documentación del sistema AI-Native MVP**
**Versión del código analizado: 2.0**