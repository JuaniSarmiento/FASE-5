# AI Gateway - Documentación Técnica Completa

## Informe Profesional del Orquestador Central AI-Native

**Archivo**: `backend/core/ai_gateway.py`
**Versión**: 2.0 (Refactorizado STATELESS - 2025-11-19)
**Autor del Análisis**: Claude Code
**Fecha**: Diciembre 2025

---

## 1. Visión General

El **AI Gateway** es el componente central del ecosistema AI-Native que actúa como orquestador maestro de todos los submodelos de inteligencia artificial. Implementa la arquitectura C4 (Context, Classification, Cognition, Control) y coordina el flujo completo desde la recepción de una petición del estudiante hasta la generación de una respuesta pedagógica.

### 1.1 Características Principales

| Característica | Descripción |
|----------------|-------------|
| **STATELESS** | No mantiene estado en memoria; toda persistencia vía repositorios BD |
| **Dependency Injection** | Todos los repositorios y providers son inyectados |
| **Escalable** | Soporta múltiples instancias (load balancer) |
| **Testeable** | Fácil mockeo de dependencias |
| **Cache LLM** | Reduce costos de LLM 30-50% en prompts repetidos |

### 1.2 Diagrama de Arquitectura C1-C6

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           AI GATEWAY                                     │
│                    (Orquestador Central STATELESS)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   C1: Motor LLM          C2: IPC                 C3: CRPE               │
│   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐        │
│   │  Ollama/Mock │       │ Clasificación│       │  Razonamiento│        │
│   │  Provider    │       │ de Prompts   │       │  Cognitivo   │        │
│   └──────────────┘       └──────────────┘       └──────────────┘        │
│                                                                          │
│   C4: GSR                C5: OSM                 C6: TC-N4              │
│   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐        │
│   │  Gobernanza  │       │ Orquestación │       │ Trazabilidad │        │
│   │  PII/Riesgo  │       │ de Agentes   │       │ Cognitiva    │        │
│   └──────────────┘       └──────────────┘       └──────────────┘        │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Componentes Internos (C1-C6)

### 2.1 C1: Motor LLM

**Archivo**: `backend/llm/factory.py`

El Motor LLM gestiona la conexión con proveedores de modelos de lenguaje.

```python
# Inicialización del provider
self.llm = llm_provider or LLMProviderFactory.create("mock", config)
```

**Proveedores Soportados**:

| Provider | Descripción | Configuración |
|----------|-------------|---------------|
| `mock` | Provider simulado para testing | Sin config requerida |
| `ollama` | LLMs locales (Phi-3, Llama 2, Mistral) | `OLLAMA_BASE_URL`, `OLLAMA_MODEL` |

**Factory Pattern**:
```python
# Crear desde variables de entorno (recomendado)
provider = LLMProviderFactory.create_from_env()

# Crear específico
provider = LLMProviderFactory.create("ollama", {
    "base_url": "http://localhost:11434",
    "model": "phi3"
})
```

### 2.2 C2: IPC (Ingesta y Comprensión de Prompt)

**Archivo**: `backend/core/cognitive_engine.py` → `classify_prompt()`

El IPC analiza el prompt del estudiante y extrae metadatos cruciales para el procesamiento.

```python
def classify_prompt(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clasifica el prompt del estudiante y determina el estado cognitivo

    Returns:
        {
            "is_total_delegation": bool,      # ¿Solicita código completo?
            "is_question": bool,               # ¿Es una pregunta?
            "requests_explanation": bool,      # ¿Solicita explicación?
            "cognitive_state": CognitiveState, # Estado cognitivo detectado
            "requires_intervention": bool,     # ¿Requiere intervención GOV-IA?
            "suggested_response_type": str     # Tipo de respuesta sugerido
        }
    """
```

**Detección de Delegación Total**:
```python
delegation_signals = [
    "dame el código completo",
    "hacé todo",
    "resolvelo por mí",
    "código entero",
    "implementa todo"
]
```

**Estados Cognitivos Detectados** (`CognitiveState`):

| Estado | Señales de Detección | Descripción |
|--------|---------------------|-------------|
| `EXPLORACION` | "no entiendo", "no sé" | Fase inicial de comprensión |
| `PLANIFICACION` | "cómo implemento", "cómo hago" | Diseño de solución |
| `IMPLEMENTACION` | (default) | Escribiendo código |
| `DEPURACION` | "error", "bug", "falla" | Resolviendo problemas |
| `VALIDACION` | "funciona", "correcto" | Verificando solución |

**Tipos de Respuesta Sugeridos**:

| Tipo | Cuándo se Aplica |
|------|------------------|
| `socratic_questioning` | Delegación detectada |
| `conceptual_explanation` | Solicita explicación |
| `guided_hints` | Pregunta general |
| `clarification_request` | Prompt ambiguo |

### 2.3 C3: CRPE (Motor de Razonamiento Cognitivo-Pedagógico)

**Archivo**: `backend/core/cognitive_engine.py` → `CognitiveReasoningEngine`

El CRPE genera estrategias pedagógicas basadas en la clasificación del prompt y el historial del estudiante.

```python
def generate_pedagogical_response_strategy(
    self,
    prompt: str,
    classification: Dict[str, Any],
    student_history: Optional[List[CognitiveTrace]] = None
) -> Dict[str, Any]:
    """
    Returns:
        {
            "response_type": str,           # Tipo de respuesta
            "cognitive_state": CognitiveState,
            "max_help_level": float,        # 0-1
            "instructions": List[str],      # Instrucciones para LLM
            "constraints": List[str],       # Restricciones
            "expected_elements": List[str], # Elementos esperados en respuesta
            "student_context": Dict         # Contexto del estudiante
        }
    """
```

**Políticas Pedagógicas Configurables**:

```python
self.pedagogical_policies = {
    "max_help_level": 0.7,              # Nivel máximo de ayuda (0-1)
    "require_justification": True,       # Exigir justificación
    "block_total_delegation": True,      # Bloquear delegación total
    "adaptive_difficulty": True,         # Dificultad adaptativa
}
```

**Estrategias por Tipo de Respuesta**:

#### Socratic Questioning
```python
strategy["instructions"] = [
    "No proporcionar código completo",
    "Hacer preguntas que guíen el razonamiento",
    "Solicitar que el estudiante explique su comprensión del problema",
    "Pedir que descomponga el problema en pasos"
]
```

#### Conceptual Explanation
```python
strategy["instructions"] = [
    "Explicar conceptos fundamentales relevantes",
    "Usar ejemplos simples y analogías",
    "Evitar dar la implementación específica",
    "Conectar con conocimientos previos"
]
```

#### Guided Hints
```python
strategy["instructions"] = [
    "Proporcionar pistas graduadas",
    "Sugerir dirección sin revelar la solución",
    "Ofrecer pseudocódigo de alto nivel si es apropiado",
    "Pedir que el estudiante justifique sus próximos pasos"
]
```

### 2.4 C4: GSR (Gobernanza, Seguridad y Riesgo)

**Archivo**: `backend/agents/governance.py` → `GobernanzaAgent`

El GSR implementa gobernanza institucional basada en marcos internacionales:
- UNESCO (2021): Ética de IA
- OECD AI Principles (2019)
- IEEE Ethically Aligned Design (2019)
- ISO/IEC 23894:2023: Risk Management
- ISO/IEC 42001:2023: AI Management System

#### Sanitización de PII (Información Personal Identificable)

```python
def sanitize_prompt(self, prompt: str) -> tuple[str, bool]:
    """
    Filtra PII del prompt antes de enviarlo al LLM.

    Detecta y reemplaza:
    - Emails → [EMAIL_REDACTED]
    - DNI → [DNI_REDACTED]
    - Teléfonos → [PHONE_REDACTED]
    - Tarjetas de crédito → [CARD_REDACTED]

    Returns:
        (prompt_sanitizado, pii_detectado)
    """
```

**Patrones Regex para PII**:
```python
self.pii_patterns = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "dni": r'\b\d{7,8}\b',  # DNI argentino
    "phone": r'\b\d{2,4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
    "credit_card": r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
}
```

#### Verificación de Cumplimiento

```python
def verify_compliance(
    self,
    trace_sequence=None,
    policies: Optional[Dict[str, Any]] = None,
    action: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Returns:
        {
            "compliant": bool,
            "status": ComplianceStatus,  # COMPLIANT, WARNING, VIOLATION
            "violations": List[Dict],
            "warnings": List[Dict],
            "allow_action": bool,
            "required_adjustments": List[str]
        }
    """
```

### 2.5 C5: OSM (Orquestación de Submodelos)

El OSM distribuye las peticiones a los agentes apropiados según el modo de sesión.

```python
# Routing por modo de agente
if current_mode == AgentMode.TUTOR:
    response = await self._process_tutor_mode(...)
elif current_mode == AgentMode.SIMULATOR:
    response = self._process_simulator_mode(...)
elif current_mode == AgentMode.EVALUATOR:
    response = self._process_evaluator_mode(...)
```

**Modos de Agente** (`AgentMode`):

| Modo | Agente | Descripción |
|------|--------|-------------|
| `TUTOR` | T-IA-Cog | Tutor cognitivo (4 modos pedagógicos) |
| `EVALUATOR` | E-IA-Proc | Evaluador de procesos |
| `SIMULATOR` | S-IA-X | Simuladores profesionales (11 roles) |
| `RISK_ANALYST` | AR-IA | Análisis de riesgos (5 dimensiones) |
| `GOVERNANCE` | GOV-IA | Gobernanza institucional |
| `PRACTICE` | - | Práctica libre (sin asistencia activa) |

### 2.6 C6: TC-N4 (Trazabilidad Cognitiva N4)

**Archivo**: `backend/agents/traceability.py` → `TrazabilidadN4Agent`

Captura todas las interacciones en 4 niveles de profundidad:

| Nivel | Nombre | Qué Captura |
|-------|--------|-------------|
| N1 | Superficial | Archivos, entregas, versión final |
| N2 | Técnico | Commits, branches, tests automatizados |
| N3 | Interaccional | Prompts, respuestas, reintentos |
| N4 | Cognitivo | Intención, decisiones, justificaciones, alternativas |

```python
def _create_trace(
    self,
    session_id: str,
    student_id: str,
    activity_id: str,
    interaction_type: InteractionType,
    content: str,
    level: TraceLevel,
    **kwargs
) -> CognitiveTrace:
    """Crea una traza cognitiva (no la persiste aún)"""
```

**Tipos de Interacción** (`InteractionType`):

| Tipo | Descripción |
|------|-------------|
| `STUDENT_PROMPT` | Mensaje del estudiante |
| `AI_RESPONSE` | Respuesta del agente IA |
| `TUTOR_INTERVENTION` | Intervención pedagógica |
| `SELF_CORRECTION` | Autocorrección del estudiante |
| `DESIGN_DECISION` | Decisión de diseño documentada |

---

## 3. Flujo de Procesamiento de Peticiones

### 3.1 Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE PROCESAMIENTO DE INTERACCIÓN                     │
└─────────────────────────────────────────────────────────────────────────────┘

Cliente (Frontend)
       │
       ▼
┌──────────────────┐
│ POST /api/v1/    │  InteractionRequest:
│   interactions   │  - session_id
│                  │  - prompt
│                  │  - context (optional)
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         FASE 1: VALIDACIÓN                            │
│                                                                       │
│  _validate_interaction_input()                                        │
│  ├─ Validar session_id (no vacío, máx 100 chars)                     │
│  ├─ Validar prompt (mín 10, máx 5000 chars)                          │
│  └─ Validar context (máx 10KB, serializable JSON)                    │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    FASE 2: SANITIZACIÓN PII (GOV-IA)                  │
│                                                                       │
│  governance_agent.sanitize_prompt(prompt)                             │
│  ├─ Detectar emails → [EMAIL_REDACTED]                               │
│  ├─ Detectar DNI → [DNI_REDACTED]                                    │
│  ├─ Detectar teléfonos → [PHONE_REDACTED]                            │
│  └─ Detectar tarjetas → [CARD_REDACTED]                              │
│                                                                       │
│  Si PII detectado → Log warning + usar prompt sanitizado              │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   FASE 3: OBTENER SESIÓN (STATELESS)                  │
│                                                                       │
│  session_repo.get_by_id(session_id)                                   │
│  ├─ Si no existe → raise ValueError                                  │
│  └─ Extraer: student_id, activity_id, current_mode                   │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                 FASE 4: CLASIFICACIÓN DE PROMPT (IPC)                 │
│                                                                       │
│  cognitive_engine.classify_prompt(prompt, context)                    │
│                                                                       │
│  Output:                                                              │
│  ├─ is_total_delegation: bool                                        │
│  ├─ is_question: bool                                                │
│  ├─ requests_explanation: bool                                       │
│  ├─ cognitive_state: CognitiveState                                  │
│  ├─ requires_intervention: bool                                      │
│  └─ suggested_response_type: str                                     │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│              FASE 5: VERIFICACIÓN DE GOBERNANZA (GSR)                 │
│                                                                       │
│  cognitive_engine.should_block_response(classification)               │
│                                                                       │
│  Si delegación total detectada Y block_total_delegation=True:         │
│  └─ should_block = True, reason = "Delegación total detectada..."    │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│               FASE 6: REGISTRO DE TRAZA DE ENTRADA (N4)               │
│                                                                       │
│  _create_trace(                                                       │
│      session_id, student_id, activity_id,                            │
│      InteractionType.STUDENT_PROMPT,                                  │
│      content=prompt,                                                  │
│      level=TraceLevel.N4_COGNITIVO,                                  │
│      cognitive_intent=classification["cognitive_state"]               │
│  )                                                                    │
│  _persist_trace(input_trace)                                          │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
                    ┌────────────┴────────────┐
                    │   ¿should_block?        │
                    └────────────┬────────────┘
                           │           │
                    ┌──────┘           └──────┐
                    │ SI                      │ NO
                    ▼                         ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐
│   RESPUESTA BLOQUEADA         │   │   FASE 7: ESTRATEGIA          │
│                               │   │   PEDAGÓGICA (CRPE)           │
│   _generate_blocked_response()│   │                               │
│   ├─ Mensaje pedagógico       │   │   _get_student_history()      │
│   ├─ Registrar intervención   │   │   generate_pedagogical_       │
│   └─ Registrar riesgo RC1     │   │   response_strategy()         │
│      (COGNITIVE_DELEGATION)   │   │                               │
└───────────────────────────────┘   └───────────────┬───────────────┘
                                                     │
                                                     ▼
                                    ┌────────────────────────────────┐
                                    │    FASE 8: ROUTING A AGENTE    │
                                    │    (OSM - Orquestación)        │
                                    └────────────────┬───────────────┘
                                                     │
                           ┌─────────────────────────┼─────────────────────────┐
                           │                         │                         │
                           ▼                         ▼                         ▼
                ┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
                │   TUTOR MODE     │      │  SIMULATOR MODE  │      │  EVALUATOR MODE  │
                │   (T-IA-Cog)     │      │   (S-IA-X)       │      │   (E-IA-Proc)    │
                │                  │      │                  │      │                  │
                │ _process_tutor_  │      │ _process_        │      │ _process_        │
                │ mode()           │      │ simulator_mode() │      │ evaluator_mode() │
                └────────┬─────────┘      └──────────────────┘      └──────────────────┘
                         │
                         ▼
          ┌──────────────┴──────────────┐
          │   Tipos de Respuesta        │
          └──────────────┬──────────────┘
                         │
     ┌───────────────────┼───────────────────┬───────────────────┐
     ▼                   ▼                   ▼                   ▼
┌──────────┐       ┌──────────┐       ┌──────────┐       ┌──────────┐
│ Socratic │       │Conceptual│       │ Guided   │       │Clarifica-│
│Questioning│      │Explanation│      │ Hints    │       │tion      │
└──────────┘       └──────────┘       └──────────┘       └──────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────────┐
│            FASE 9: REGISTRO DE TRAZA DE RESPUESTA (N4)               │
│                                                                       │
│  _create_trace(                                                       │
│      InteractionType.AI_RESPONSE,                                     │
│      content=response["message"],                                     │
│      agent_id=current_mode.value                                      │
│  )                                                                    │
│  _persist_trace(response_trace)                                       │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│              FASE 10: ANÁLISIS DE RIESGOS (AR-IA)                    │
│                                                                       │
│  _analyze_risks_async(session_id, input_trace, response_trace,       │
│                       classification)                                 │
│                                                                       │
│  Riesgos detectados:                                                  │
│  ├─ RC1: Delegación Total (COGNITIVE_DELEGATION)                     │
│  ├─ RC2: Dependencia Excesiva (AI_DEPENDENCY)                        │
│  ├─ RC3: Falta de Justificación (LACK_JUSTIFICATION)                 │
│  └─ REp1: Aceptación Acrítica (UNCRITICAL_ACCEPTANCE)                │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                FASE 11: MÉTRICAS PROMETHEUS                          │
│                                                                       │
│  metrics.record_interaction(session_id, student_id, agent, status)   │
│  metrics.record_cognitive_state(cognitive_state)                      │
│  metrics.record_trace_creation(trace_level, interaction_type)        │
│  metrics.record_risk_detection(risk_type, risk_level, dimension)     │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      RESPUESTA AL CLIENTE                             │
│                                                                       │
│  InteractionResponse:                                                 │
│  ├─ interaction_id: UUID                                             │
│  ├─ session_id: str                                                  │
│  ├─ response: str (mensaje del agente)                               │
│  ├─ agent_used: str                                                  │
│  ├─ cognitive_state_detected: str                                    │
│  ├─ ai_involvement: float (0-1)                                      │
│  ├─ blocked: bool                                                    │
│  ├─ block_reason: Optional[str]                                      │
│  ├─ trace_id: str                                                    │
│  ├─ risks_detected: List[str]                                        │
│  └─ timestamp: datetime                                              │
└──────────────────────────────────────────────────────────────────────┘
```

### 3.2 Código del Flujo Principal

```python
async def process_interaction(
    self,
    session_id: str,
    prompt: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Procesa una interacción del estudiante a través del gateway (STATELESS)

    Este es el flujo principal que:
    1. Valida entrada
    2. Obtiene sesión desde BD (no de memoria)
    3. Clasifica el prompt (IPC)
    4. Verifica gobernanza (GSR)
    5. Genera estrategia pedagógica (CRPE)
    6. Detecta riesgos (AR-IA)
    7. Registra en trazabilidad (N4) vía repositorio
    8. Genera respuesta según el agente activo
    """
```

---

## 4. Distribución a los Agentes

### 4.1 Modo TUTOR (T-IA-Cog)

**Archivo**: `backend/agents/tutor.py` → `TutorCognitivoAgent`

El modo Tutor implementa el andamiaje cognitivo con 4 tipos de respuesta:

```python
async def _process_tutor_mode(
    self,
    session_id: str,
    prompt: str,
    strategy: Dict[str, Any],
    classification: Dict[str, Any]
) -> Dict[str, Any]:
    """Procesa la interacción en modo T-IA-Cog (Tutor)"""

    response_type = strategy.get("response_type", "unknown")

    if response_type == "socratic_questioning":
        message = await self._generate_socratic_response(prompt, strategy, session_id)
    elif response_type == "conceptual_explanation":
        message = await self._generate_conceptual_explanation(prompt, strategy, session_id)
    elif response_type == "guided_hints":
        message = await self._generate_guided_hints(prompt, strategy, session_id)
    else:
        message = await self._generate_conceptual_explanation(prompt, strategy, session_id)
```

#### 4.1.1 Respuesta Socrática

```python
async def _generate_socratic_response(self, prompt, strategy, session_id):
    """Genera respuesta socrática con memoria de conversación"""

    messages = [
        LLMMessage(
            role=LLMRole.SYSTEM,
            content="""Eres un tutor socrático. Tu objetivo es guiar al estudiante
            a descubrir la respuesta por sí mismo mediante preguntas orientadoras.

            NO des la respuesta directa. Haz preguntas que:
            1. Exploren su comprensión actual
            2. Identifiquen sus suposiciones
            3. Lo guíen a descomponer el problema
            4. Lo ayuden a encontrar la solución por sí mismo

            Sé breve y preciso. Máximo 4-5 preguntas."""
        )
    ]

    # Agregar historial de conversación
    messages.extend(conversation_history)

    # Generar respuesta
    response = await self.llm.generate(messages, max_tokens=300, temperature=0.7)
```

#### 4.1.2 Explicación Conceptual

```python
async def _generate_conceptual_explanation(self, prompt, strategy, session_id):
    """Explicación conceptual sin código"""

    system_prompt = """Eres un tutor pedagógico. Explica conceptos
    fundamentales de manera clara y didáctica.

    Estructura tu explicación:
    1. Concepto clave (definición simple)
    2. Principio fundamental (por qué es importante)
    3. Ejemplo concreto y simple
    4. Aplicación práctica

    Usa markdown para formato. Sé claro y conciso (máximo 200 palabras)."""
```

#### 4.1.3 Pistas Guiadas

```python
async def _generate_guided_hints(self, prompt, strategy, session_id):
    """Pistas graduadas sin solución completa"""

    system_prompt = """Eres un tutor que da pistas graduadas.
    NO des la solución completa.

    Proporciona 3-4 pistas que:
    1. Sugieran cómo descomponer el problema
    2. Mencionen conceptos/estructuras relevantes
    3. Indiquen casos a considerar
    4. Sugieran un próximo paso concreto

    Cada pista debe acercar al estudiante a la solución
    sin dársela directamente."""
```

### 4.2 Modo SIMULATOR (S-IA-X)

El modo Simulador delega a los 11 simuladores profesionales:

**Simuladores V1**:
| ID | Simulador | Rol |
|----|-----------|-----|
| PO-IA | Product Owner | Priorización de backlog |
| SM-IA | Scrum Master | Gestión de sprints |
| IT-IA | Tech Interviewer | Entrevistas técnicas |
| IR-IA | Incident Responder | Respuesta a incidentes |
| CX-IA | Client | Cliente exigente |
| DSO-IA | DevSecOps | Auditoría de seguridad |

**Simuladores V2**:
| ID | Simulador | Rol |
|----|-----------|-----|
| SD-IA | Senior Developer | Code review |
| QA-IA | QA Engineer | Testing |
| SA-IA | Security Auditor | Seguridad |
| TL-IA | Tech Lead | Arquitectura |
| DC-IA | Demanding Client | Requisitos cambiantes |

### 4.3 Modo EVALUATOR (E-IA-Proc)

El modo Evaluador activa el pipeline de 7 fases basado en Zimmerman (2002):

1. **Forethought** - Planificación y establecimiento de metas
2. **Performance** - Ejecución con auto-monitoreo
3. **Self-Reflection** - Evaluación del proceso
4. **Cognitive** - Análisis de estrategias cognitivas
5. **Metacognitive** - Evaluación de autorregulación
6. **Behavioral** - Análisis de patrones de comportamiento
7. **Integration** - Síntesis y feedback formativo

---

## 5. Gestión de Memoria y Conversación

### 5.1 Carga del Historial de Conversación

```python
def _load_conversation_history(self, session_id: str) -> List[LLMMessage]:
    """
    Carga el historial de conversación de esta sesión como mensajes LLM.

    Recupera todas las trazas de la sesión y las convierte al formato
    de mensajes que espera el LLM provider, manteniendo el contexto
    completo de la conversación.
    """
    db_traces = self.trace_repo.get_by_session(session_id)

    messages = []
    for trace in db_traces:
        if trace.interaction_type == InteractionType.STUDENT_PROMPT.value:
            messages.append(LLMMessage(role=LLMRole.USER, content=trace.content))
        elif trace.interaction_type in [
            InteractionType.AI_RESPONSE.value,
            InteractionType.TUTOR_INTERVENTION.value
        ]:
            messages.append(LLMMessage(role=LLMRole.ASSISTANT, content=trace.content))

    return messages
```

### 5.2 Cache de Respuestas LLM

```python
# Verificar cache antes de generar
if self.cache is not None:
    cached_response = self.cache.get(
        prompt=prompt,
        context=cache_context,
        mode="TUTOR"
    )

if cached_response is not None:
    # Cache HIT - usar respuesta cacheada (ahorra llamada LLM)
    message = cached_response
else:
    # Cache MISS - generar respuesta nueva
    message = await self._generate_response(...)

    # Guardar en cache para futuras solicitudes
    self.cache.set(
        prompt=prompt,
        response=message,
        context=cache_context,
        mode="TUTOR"
    )
```

**Configuración del Cache**:
```python
cache_enabled = os.getenv("LLM_CACHE_ENABLED", "true")
cache_ttl = int(os.getenv("LLM_CACHE_TTL", "3600"))  # 1 hora
cache_max_entries = int(os.getenv("LLM_CACHE_MAX_ENTRIES", "1000"))
```

---

## 6. Análisis de Riesgos (AR-IA)

### 6.1 Riesgos Detectados

```python
def _analyze_risks_async(
    self,
    session_id: str,
    input_trace: CognitiveTrace,
    response_trace: CognitiveTrace,
    classification: Dict[str, Any]
) -> None:
    """
    Análisis de riesgos asíncrono (AR-IA)

    Detecta:
    - RC1: Delegación total (solicitudes de código completo)
    - RC2: Dependencia excesiva de IA (alto ai_involvement)
    - RC3: Falta de justificación (decisiones sin explicación)
    - RE1: Integridad académica (uso no divulgado de IA)
    - REp1: Aceptación acrítica (no cuestiona respuestas de IA)
    """
```

### 6.2 Dimensiones de Riesgo

| Dimensión | Código | Tipos de Riesgo |
|-----------|--------|-----------------|
| **Cognitivo** | RC | COGNITIVE_DELEGATION, SUPERFICIAL_REASONING, AI_DEPENDENCY, LACK_JUSTIFICATION |
| **Ético** | RE | ACADEMIC_INTEGRITY, UNDISCLOSED_AI_USE, PLAGIARISM |
| **Epistémico** | REp | CONCEPTUAL_ERROR, LOGICAL_FALLACY, UNCRITICAL_ACCEPTANCE |
| **Técnico** | RT | SECURITY_VULNERABILITY, POOR_CODE_QUALITY, ARCHITECTURAL_FLAW |
| **Gobernanza** | RG | POLICY_VIOLATION, UNAUTHORIZED_USE, AUTOMATION_SUSPECTED |

### 6.3 Umbrales de Detección

```python
# Constantes en backend/core/constants.py
AI_DEPENDENCY_LOW_THRESHOLD = 0.3    # 30%
AI_DEPENDENCY_MEDIUM_THRESHOLD = 0.6  # 60% - Genera riesgo MEDIUM
AI_DEPENDENCY_HIGH_THRESHOLD = 0.8    # 80%

# Umbral para bloqueo automático
GOVERNANCE_BLOCK_THRESHOLD_AI_DEPENDENCY = 0.9  # 90%
GOVERNANCE_BLOCK_CONSECUTIVE_DELEGATIONS = 5     # Intentos consecutivos
```

---

## 7. Dependency Injection

### 7.1 Archivo: `backend/api/deps.py`

```python
def get_ai_gateway(
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    risk_repo: RiskRepository = Depends(get_risk_repository),
    evaluation_repo: EvaluationRepository = Depends(get_evaluation_repository),
    sequence_repo: TraceSequenceRepository = Depends(get_sequence_repository),
) -> AIGateway:
    """
    Dependency para obtener el AI Gateway con DI completa.
    Crea NUEVA instancia por request con repositorios frescos.

    IMPORTANTE: No usar singleton para el gateway ya que los repositorios
    contienen sesiones de BD que deben ser únicas por request.
    El LLM provider y el cache sí se cachean (stateless).
    """

    return AIGateway(
        llm_provider=_llm_provider_instance,
        cognitive_engine=None,  # Usar default
        session_repo=session_repo,
        trace_repo=trace_repo,
        risk_repo=risk_repo,
        evaluation_repo=evaluation_repo,
        sequence_repo=sequence_repo,
        cache=llm_cache,
        config=None
    )
```

### 7.2 Thread Safety para Singletons

```python
# Lock para thread-safety en LLM provider singleton
_llm_provider_instance: Optional[LLMProviderFactory] = None
_llm_provider_lock = threading.Lock()

def get_llm_provider():
    """Thread-safe singleton para LLM provider"""
    global _llm_provider_instance

    # Lock-first pattern (más seguro en Python)
    with _llm_provider_lock:
        if _llm_provider_instance is None:
            _llm_provider_instance = _initialize_llm_provider()

    return _llm_provider_instance
```

---

## 8. Circuit Breaker y Fallbacks

### 8.1 Fallback cuando LLM no está disponible

```python
def _get_fallback_socratic_response(self, prompt: str) -> str:
    """Fallback cuando Ollama está inaccesible"""

    return """⚠️ El sistema de IA está experimentando dificultades temporales,
    pero puedo ayudarte con estas preguntas guía:

    **Para ayudarte mejor, necesito entender tu proceso de pensamiento:**

    1. ¿Qué entendés que te están pidiendo resolver?
    2. ¿Qué conceptos creés que son relevantes para este problema?
    3. ¿Cómo funcionaría una solución ideal?
    4. ¿Qué has intentado hasta ahora y qué resultados obtuviste?

    💡 **Tip**: Intenta descomponer el problema en partes más pequeñas.

    _Responde estas preguntas y podremos continuar cuando el sistema se recupere._"""
```

---

## 9. Métricas Prometheus

### 9.1 Métricas Registradas

```python
# Por cada interacción exitosa
metrics.record_interaction(
    session_id=session_id,
    student_id=student_id,
    agent_used=current_mode.value,
    status="success"
)

# Por cada estado cognitivo detectado
metrics.record_cognitive_state(cognitive_state.value)

# Por cada traza creada
metrics.record_trace_creation(
    trace_level=trace.trace_level.value,
    interaction_type=trace.interaction_type.value
)

# Por cada riesgo detectado
metrics.record_risk_detection(
    risk_type=risk_type.value,
    risk_level=risk_level.value,
    dimension=dimension.value
)

# Por cada bloqueo de gobernanza
metrics.record_governance_block(
    reason="total_delegation",
    session_id=session_id
)
```

---

## 10. Validación de Entrada

### 10.1 Constantes de Validación

```python
# backend/core/constants.py

PROMPT_MIN_LENGTH = 10          # Mínimo de caracteres
PROMPT_MAX_LENGTH = 5000        # Máximo de caracteres
CONTEXT_MAX_SIZE_BYTES = 10240  # 10KB máximo
SESSION_ID_MAX_LENGTH = 100     # Máximo de caracteres
```

### 10.2 Método de Validación

```python
def _validate_interaction_input(
    self,
    session_id: str,
    prompt: str,
    context: Optional[Dict[str, Any]]
) -> None:
    """
    Valida la entrada de una interacción.

    Raises:
        ValueError: Si la validación falla
    """
    # Validar session_id
    if not session_id or len(session_id) > SESSION_ID_MAX_LENGTH:
        raise ValueError("session_id inválido")

    # Validar prompt
    prompt_length = len(prompt.strip())
    if prompt_length < PROMPT_MIN_LENGTH or prompt_length > PROMPT_MAX_LENGTH:
        raise ValueError("Prompt fuera de rango")

    # Validar context
    if context is not None:
        context_size = len(json.dumps(context).encode('utf-8'))
        if context_size > CONTEXT_MAX_SIZE_BYTES:
            raise ValueError("Context demasiado grande")
```

---

## 11. Repositorios (Repository Protocol)

### 11.1 Interfaces Protocol

```python
@runtime_checkable
class SessionRepositoryProtocol(Protocol):
    """Protocol for session repository operations"""
    def create(self, student_id: str, activity_id: str, mode: str) -> Any: ...
    def get(self, session_id: str) -> Any: ...
    def update(self, session_id: str, **kwargs: Any) -> Any: ...

@runtime_checkable
class TraceRepositoryProtocol(Protocol):
    """Protocol for trace repository operations"""
    def create(self, trace: CognitiveTrace) -> Any: ...
    def get_by_session(self, session_id: str) -> List[CognitiveTrace]: ...

@runtime_checkable
class RiskRepositoryProtocol(Protocol):
    """Protocol for risk repository operations"""
    def create(self, risk: Risk) -> Any: ...
    def get_by_session(self, session_id: str) -> List[Risk]: ...
```

---

## 12. Tablas de Base de Datos Relacionadas

| Tabla | Propósito | FK Principal |
|-------|-----------|--------------|
| `sessions` | Sesiones de interacción | `user_id` |
| `cognitive_traces` | Trazas N4 | `session_id` |
| `trace_sequences` | Secuencias de trazas | `session_id` |
| `risks` | Riesgos detectados | `session_id` |
| `evaluations` | Evaluaciones generadas | `session_id` |
| `interactions` | Historial de interacciones | `session_id` |

---

## 13. Referencias Bibliográficas

El AI Gateway se basa en fundamentos teóricos de:

| Teoría | Autor | Aplicación |
|--------|-------|------------|
| Cognición Distribuida | Hutchins (1995) | Distribución de carga cognitiva |
| Cognición Extendida | Clark & Chalmers (1998) | IA como extensión cognitiva |
| Teoría de Carga Cognitiva | Sweller (1988) | Reducción de carga extrínseca |
| Autorregulación | Zimmerman (2002) | Modelo de 7 fases para evaluación |
| Andamiaje Cognitivo | Wood, Bruner & Ross (1976) | Scaffolding adaptativo |

---

## 14. Archivos Relacionados

| Archivo | Propósito |
|---------|-----------|
| `backend/core/ai_gateway.py` | Orquestador central |
| `backend/core/cognitive_engine.py` | Motor CRPE |
| `backend/core/constants.py` | Constantes y umbrales |
| `backend/agents/governance.py` | Agente GOV-IA |
| `backend/agents/tutor.py` | Agente T-IA-Cog |
| `backend/agents/traceability.py` | Sistema TC-N4 |
| `backend/agents/risk_analyst.py` | Agente AR-IA |
| `backend/api/deps.py` | Dependency Injection |
| `backend/api/routers/interactions.py` | Router principal |
| `backend/llm/factory.py` | Factory de LLM providers |

---

## 15. Resumen Ejecutivo

El **AI Gateway** es el corazón del sistema AI-Native MVP, implementando:

1. **Arquitectura STATELESS** que permite escalabilidad horizontal
2. **Pipeline de 11 fases** desde validación hasta respuesta
3. **6 componentes internos** (C1-C6) que coordinan el procesamiento
4. **Routing inteligente** a 6 agentes especializados según modo
5. **Gobernanza robusta** con sanitización de PII y políticas pedagógicas
6. **Trazabilidad N4 completa** de cada interacción
7. **Análisis de riesgos en tiempo real** en 5 dimensiones
8. **Cache LLM** para optimización de costos (30-50% ahorro)
9. **Circuit Breaker** con fallbacks cuando LLM no disponible
10. **Métricas Prometheus** para observabilidad

El sistema evalúa el **PROCESO** (cómo resuelve el estudiante) y no solo el **PRODUCTO** (código final), alineándose con la tesis doctoral de evaluación basada en procesos.