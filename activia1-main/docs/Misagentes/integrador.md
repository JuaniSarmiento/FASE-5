# Sistema Multi-Agente AI-Native: Documentación Integral

## Informe Técnico Completo del Ecosistema de Agentes de Inteligencia Artificial

**Versión**: 1.0
**Fecha**: Diciembre 2025
**Proyecto**: AI-Native MVP - Tesis Doctoral
**Autor**: Claude Code (Análisis Arquitectónico)

---

## Tabla de Contenidos

1. [Visión General del Ecosistema](#1-visión-general-del-ecosistema)
2. [Arquitectura Global del Sistema](#2-arquitectura-global-del-sistema)
3. [AI Gateway - Orquestador Central](#3-ai-gateway---orquestador-central)
4. [Los 6 Agentes de IA](#4-los-6-agentes-de-ia)
   - [4.1 T-IA-Cog: Tutor Cognitivo](#41-t-ia-cog-tutor-cognitivo)
   - [4.2 E-IA-Proc: Evaluador de Procesos](#42-e-ia-proc-evaluador-de-procesos)
   - [4.3 S-IA-X: Simuladores Profesionales](#43-s-ia-x-simuladores-profesionales)
   - [4.4 AR-IA: Analista de Riesgos](#44-ar-ia-analista-de-riesgos)
   - [4.5 GOV-IA: Gobernanza Institucional](#45-gov-ia-gobernanza-institucional)
   - [4.6 TC-N4: Trazabilidad Cognitiva](#46-tc-n4-trazabilidad-cognitiva)
5. [Flujo de Procesamiento de 10 Fases](#5-flujo-de-procesamiento-de-10-fases)
6. [Sistema de Trazabilidad N4](#6-sistema-de-trazabilidad-n4)
7. [Sistema de Gobernanza y Semáforos](#7-sistema-de-gobernanza-y-semáforos)
8. [Análisis de Riesgos 5D](#8-análisis-de-riesgos-5d)
9. [Persistencia en Base de Datos](#9-persistencia-en-base-de-datos)
10. [Colaboración Inter-Agentes](#10-colaboración-inter-agentes)
11. [Endpoints de la API](#11-endpoints-de-la-api)
12. [Referencias Bibliográficas](#12-referencias-bibliográficas)

---

## 1. Visión General del Ecosistema

### 1.1 Propósito del Sistema

El **Sistema Multi-Agente AI-Native** es una plataforma educativa que implementa **evaluación basada en procesos** (no en productos) con trazabilidad cognitiva de nivel N4. El sistema evalúa **CÓMO** los estudiantes resuelven problemas de programación, no solo el código final producido.

### 1.2 Principios Fundamentales

| Principio | Descripción |
|-----------|-------------|
| **Evaluación de Proceso** | Evaluar el proceso cognitivo, no el producto final |
| **Trazabilidad N4** | Capturar intención, decisiones, justificaciones y alternativas |
| **Andamiaje Cognitivo** | Scaffolding adaptativo según nivel del estudiante |
| **Gobernanza Ética** | Cumplimiento de marcos internacionales de IA en educación |
| **Arquitectura STATELESS** | Escalabilidad horizontal sin estado en memoria |

### 1.3 Marcos Normativos Implementados

| Marco | Año | Enfoque |
|-------|-----|---------|
| **UNESCO** | 2021 | Ética de IA en educación |
| **OECD AI Principles** | 2019 | Principios de IA responsable |
| **IEEE Ethically Aligned Design** | 2019 | Diseño éticamente alineado |
| **ISO/IEC 23894:2023** | 2023 | Gestión de riesgos de IA |
| **ISO/IEC 42001:2023** | 2023 | Sistemas de gestión de IA |

### 1.4 Fundamentos Teóricos

| Teoría | Autor | Aplicación en el Sistema |
|--------|-------|-------------------------|
| Cognición Distribuida | Hutchins (1995) | Distribución de carga cognitiva entre agentes |
| Cognición Extendida | Clark & Chalmers (1998) | IA como extensión cognitiva del estudiante |
| Teoría de Carga Cognitiva | Sweller (1988) | Reducción de carga extrínseca |
| Autorregulación | Zimmerman (2002) | Modelo de 7 fases para evaluación |
| Andamiaje Cognitivo | Wood, Bruner & Ross (1976) | Scaffolding adaptativo |

---

## 2. Arquitectura Global del Sistema

### 2.1 Diagrama Maestro de Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           ECOSISTEMA AI-NATIVE MVP                                    │
│                        Sistema Multi-Agente de 6 Componentes                          │
└─────────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────┐
                                    │    FRONTEND     │
                                    │   React + TS    │
                                    └────────┬────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              FastAPI Backend                                          │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│   ┌─────────────────────────────────────────────────────────────────────────────┐   │
│   │                         AI GATEWAY (STATELESS)                                │   │
│   │                        Orquestador Central C1-C6                              │   │
│   ├─────────────────────────────────────────────────────────────────────────────┤   │
│   │                                                                               │   │
│   │   C1: Motor LLM          C2: IPC                 C3: CRPE                    │   │
│   │   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐             │   │
│   │   │  Ollama/Mock │       │ Clasificación│       │  Razonamiento│             │   │
│   │   │  Provider    │       │ de Prompts   │       │  Cognitivo   │             │   │
│   │   └──────────────┘       └──────────────┘       └──────────────┘             │   │
│   │                                                                               │   │
│   │   C4: GSR                C5: OSM                 C6: TC-N4                    │   │
│   │   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐             │   │
│   │   │  Gobernanza  │       │ Orquestación │       │ Trazabilidad │             │   │
│   │   │  PII/Riesgo  │       │ de Agentes   │       │ Cognitiva    │             │   │
│   │   └──────────────┘       └──────────────┘       └──────────────┘             │   │
│   │                                                                               │   │
│   └─────────────────────────────────────────────────────────────────────────────┘   │
│                                         │                                            │
│            ┌────────────────────────────┼────────────────────────────┐              │
│            │                            │                            │              │
│            ▼                            ▼                            ▼              │
│   ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐    │
│   │   T-IA-Cog      │          │   E-IA-Proc     │          │   S-IA-X        │    │
│   │   (Tutor)       │          │   (Evaluador)   │          │   (Simuladores) │    │
│   │                 │          │                 │          │   11 roles      │    │
│   │  4 modos        │          │  7 fases        │          │                 │    │
│   │  pedagógicos    │          │  Zimmerman      │          │  V1: 6 roles    │    │
│   └─────────────────┘          └─────────────────┘          │  V2: 5 roles    │    │
│                                                              └─────────────────┘    │
│            │                            │                            │              │
│            └────────────────────────────┼────────────────────────────┘              │
│                                         │                                            │
│                                         ▼                                            │
│   ┌─────────────────┐          ┌─────────────────┐          ┌─────────────────┐    │
│   │   AR-IA         │◄────────►│   GOV-IA        │◄────────►│   TC-N4         │    │
│   │   (Riesgos)     │          │   (Gobernanza)  │          │   (Trazabilidad)│    │
│   │                 │          │                 │          │                 │    │
│   │  5 dimensiones  │          │  Semáforos      │          │  4 niveles      │    │
│   │  18 tipos       │          │  4 reglas       │          │  N1-N4          │    │
│   └─────────────────┘          └─────────────────┘          └─────────────────┘    │
│                                                                                       │
└────────────────────────────────────────┬────────────────────────────────────────────┘
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              CAPA DE PERSISTENCIA                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                       │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐                 │
│   │   PostgreSQL    │    │     Redis       │    │     Ollama      │                 │
│   │                 │    │                 │    │                 │                 │
│   │  - sessions     │    │  - Cache LLM    │    │  - Phi-3        │                 │
│   │  - traces       │    │  - Rate limit   │    │  - Llama 2      │                 │
│   │  - risks        │    │  - Sessions     │    │  - Mistral      │                 │
│   │  - evaluations  │    │                 │    │                 │                 │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘                 │
│                                                                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Flujo de Request Simplificado

```
Cliente → FastAPI Router → AIGateway (STATELESS) → CRPE → Governance Agent
    → Target Agent → LLM Provider → Response Generator → TC-N4 Traceability
    → Risk Analyzer → Repositories (PostgreSQL) → Response
```

### 2.3 Componentes del AI Gateway (C1-C6)

| Componente | Nombre | Archivo | Propósito |
|------------|--------|---------|-----------|
| C1 | Motor LLM | `backend/llm/factory.py` | Conexión a Ollama/Mock providers |
| C2 | IPC | `backend/core/cognitive_engine.py` | Ingesta y Comprensión de Prompt |
| C3 | CRPE | `backend/core/cognitive_engine.py` | Motor de Razonamiento Cognitivo-Pedagógico |
| C4 | GSR | `backend/agents/governance.py` | Gobernanza, Seguridad y Riesgo |
| C5 | OSM | `backend/core/ai_gateway.py` | Orquestación de Submodelos |
| C6 | TC-N4 | `backend/agents/traceability.py` | Trazabilidad Cognitiva N4 |

---

## 3. AI Gateway - Orquestador Central

### 3.1 Características Principales

| Característica | Descripción |
|----------------|-------------|
| **STATELESS** | No mantiene estado en memoria; toda persistencia vía repositorios BD |
| **Dependency Injection** | Todos los repositorios y providers son inyectados |
| **Escalable** | Soporta múltiples instancias (load balancer) |
| **Testeable** | Fácil mockeo de dependencias |
| **Cache LLM** | Reduce costos de LLM 30-50% en prompts repetidos |

### 3.2 Pipeline de 11 Fases

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

### 3.3 Constantes de Validación

```python
# backend/core/constants.py
PROMPT_MIN_LENGTH = 10          # Mínimo de caracteres
PROMPT_MAX_LENGTH = 5000        # Máximo de caracteres
CONTEXT_MAX_SIZE_BYTES = 10240  # 10KB máximo
SESSION_ID_MAX_LENGTH = 100     # Máximo de caracteres

# Umbrales de dependencia de IA
AI_DEPENDENCY_LOW_THRESHOLD = 0.3    # 30% - Sin riesgo
AI_DEPENDENCY_MEDIUM_THRESHOLD = 0.6  # 60% - Riesgo MEDIUM
AI_DEPENDENCY_HIGH_THRESHOLD = 0.8    # 80% - Riesgo HIGH
GOVERNANCE_BLOCK_THRESHOLD = 0.9      # 90% - Bloqueo automático
```

---

## 4. Los 6 Agentes de IA

### 4.1 T-IA-Cog: Tutor Cognitivo

#### 4.1.1 Visión General

**Archivo**: `backend/agents/tutor.py`

El T-IA-Cog (Tutor Cognitivo) es el agente principal de interacción con estudiantes. Implementa andamiaje cognitivo adaptativo con 4 modos pedagógicos.

#### 4.1.2 Diagrama de Arquitectura del Tutor

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          T-IA-Cog: TUTOR COGNITIVO                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │                    TutorCognitivoAgent                               │   │
│   │                    (backend/agents/tutor.py)                         │   │
│   └───────────────────────────────┬─────────────────────────────────────┘   │
│                                   │                                          │
│           ┌───────────────────────┼───────────────────────┐                 │
│           │                       │                       │                 │
│           ▼                       ▼                       ▼                 │
│   ┌───────────────┐       ┌───────────────┐       ┌───────────────┐        │
│   │ TutorRules    │       │TutorGovernance│       │ TutorPrompts  │        │
│   │ Engine        │       │    Engine     │       │               │        │
│   │               │       │               │       │               │        │
│   │ 4 Reglas      │       │ Semáforos     │       │ Templates     │        │
│   │ Inquebrantables│      │ VERDE/AMARILLO│       │ de Respuesta  │        │
│   │               │       │ /ROJO         │       │               │        │
│   └───────────────┘       └───────────────┘       └───────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 4.1.3 Las 4 Reglas Pedagógicas Inquebrantables

**Archivo**: `backend/agents/tutor_rules.py`

```python
class TutorRule(str, Enum):
    ANTI_SOLUCION = "anti_solucion_directa"
    MODO_SOCRATICO = "modo_socratico_prioritario"
    EXIGIR_EXPLICITACION = "exigir_explicitacion"
    REFUERZO_CONCEPTUAL = "refuerzo_conceptual"
```

| Regla | Principio | Comportamiento |
|-------|-----------|----------------|
| **ANTI_SOLUCION** | "Ni a Palos" | Prohibido dar código completo bajo cualquier circunstancia |
| **MODO_SOCRATICO** | Preguntar antes de responder | El default es hacer preguntas, no dar respuestas directas |
| **EXIGIR_EXPLICITACION** | Forzar pensamiento → palabras | Requerir justificaciones y planes antes de código |
| **REFUERZO_CONCEPTUAL** | Ir a teoría, no parches | Redirigir a conceptos fundamentales, no soluciones rápidas |

#### 4.1.4 Patrones de Delegación Bloqueados

```python
delegation_signals = [
    "dame el código completo",
    "hacé todo",
    "resolvelo por mí",
    "código entero",
    "implementa todo",
    "haceme",
    "muestrame el código"
]
```

#### 4.1.5 Tipos de Intervención

```python
class InterventionType(str, Enum):
    PREGUNTA_SOCRATICA = "pregunta_socratica"
    RECHAZO_PEDAGOGICO = "rechazo_pedagogico"
    PISTA_GRADUADA = "pista_graduada"
    CORRECCION_CONCEPTUAL = "correccion_conceptual"
    EXIGENCIA_JUSTIFICACION = "exigencia_justificacion"
    EXIGENCIA_PSEUDOCODIGO = "exigencia_pseudocodigo"
    REMISION_TEORIA = "remision_teoria"
```

#### 4.1.6 Niveles de Andamiaje Cognitivo

```python
class CognitiveScaffoldingLevel(str, Enum):
    NOVATO = "novato"        # Más explicaciones, ejemplos parciales
    INTERMEDIO = "intermedio"  # Balance entre guía y autonomía
    AVANZADO = "avanzado"    # Mínima ayuda, máxima exigencia crítica
```

**Determinación de Nivel**:

| Condición | Nivel Asignado |
|-----------|----------------|
| `ai_involvement > 0.7` OR `autonomous_solutions < 3` | NOVATO |
| `error_self_correction > 0.6` AND `ai_involvement < 0.4` | AVANZADO |
| Otros casos | INTERMEDIO |

#### 4.1.7 Modos Pedagógicos del Tutor

| Modo | Descripción | Cuándo se Usa |
|------|-------------|---------------|
| **Socrático** | Preguntas orientadoras | Delegación detectada, primera interacción |
| **Explicativo** | Explicación conceptual | Solicita explicación de conceptos |
| **Guiado** | Pistas graduadas | Preguntas generales, debugging |
| **Metacognitivo** | Reflexión sobre el proceso | Validación, autocorrección |

---

### 4.2 E-IA-Proc: Evaluador de Procesos

#### 4.2.1 Visión General

**Archivo**: `backend/agents/evaluator.py`

El E-IA-Proc (Evaluador de Procesos) evalúa el proceso de aprendizaje del estudiante, no solo el producto final. Implementa el modelo de autorregulación de Zimmerman (2002).

#### 4.2.2 Diagrama del Pipeline de Evaluación

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    E-IA-Proc: PIPELINE DE 7 FASES                            │
│                    Basado en Modelo Zimmerman (2002)                         │
└─────────────────────────────────────────────────────────────────────────────┘

TraceSequence (Input)
        │
        ▼
┌───────────────────┐
│  FASE 1:          │    Análisis de metas establecidas
│  FORETHOUGHT      │    Estrategias de planificación
│  (Planificación)  │    Expectativas de autoeficacia
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  FASE 2:          │    Auto-monitoreo durante ejecución
│  PERFORMANCE      │    Estrategias de control
│  (Ejecución)      │    Gestión del tiempo
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  FASE 3:          │    Auto-evaluación
│  SELF-REFLECTION  │    Atribuciones causales
│  (Reflexión)      │    Satisfacción/insatisfacción
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  FASE 4:          │    Estrategias cognitivas usadas
│  COGNITIVE        │    Profundidad de procesamiento
│  ANALYSIS         │    Transferencia de conocimiento
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  FASE 5:          │    Conciencia metacognitiva
│  METACOGNITIVE    │    Regulación del aprendizaje
│  EVALUATION       │    Adaptación de estrategias
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  FASE 6:          │    Patrones de comportamiento
│  BEHAVIORAL       │    Persistencia ante dificultades
│  ANALYSIS         │    Búsqueda de ayuda apropiada
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  FASE 7:          │    Síntesis de hallazgos
│  INTEGRATION &    │    Feedback formativo
│  FEEDBACK         │    Recomendaciones personalizadas
└─────────┬─────────┘
          │
          ▼
   EvaluationReport
```

#### 4.2.3 Niveles de Competencia

```python
class CompetencyLevel(str, Enum):
    EXPERTO = "experto"          # Score > 0.85
    AVANZADO = "avanzado"        # Score 0.70 - 0.85
    INTERMEDIO = "intermedio"    # Score 0.50 - 0.70
    BASICO = "basico"           # Score 0.30 - 0.50
    INICIAL = "inicial"         # Score < 0.30
```

#### 4.2.4 Dimensiones de Evaluación

| Dimensión | Peso | Descripción |
|-----------|------|-------------|
| **Planificación** | 20% | Establecimiento de metas y estrategias |
| **Ejecución** | 25% | Implementación con automonitoreo |
| **Reflexión** | 15% | Autoevaluación y atribuciones |
| **Cognitivo** | 15% | Estrategias de pensamiento |
| **Metacognitivo** | 15% | Regulación del aprendizaje |
| **Comportamental** | 10% | Patrones de persistencia |

#### 4.2.5 Estructura del Reporte de Evaluación

```python
class EvaluationReport(BaseModel):
    id: str
    student_id: str
    activity_id: str
    session_id: str

    # Scores (escala 0-10)
    overall_score: float
    dimensions: List[EvaluationDimension]

    # Análisis
    competency_level: CompetencyLevel
    strengths: List[str]
    areas_for_improvement: List[str]

    # Feedback formativo
    formative_feedback: str
    recommendations: List[str]

    # Metadata
    trace_count: int
    evaluation_date: datetime
```

---

### 4.3 S-IA-X: Simuladores Profesionales

#### 4.3.1 Visión General

**Archivo**: `backend/agents/simulators.py`

El S-IA-X (Simuladores de Roles Profesionales) proporciona 11 simuladores que recrean escenarios profesionales reales del desarrollo de software.

#### 4.3.2 Diagrama de Arquitectura de Simuladores

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         S-IA-X: SISTEMA DE SIMULADORES                       │
│                         11 Roles Profesionales                               │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │  SimuladoresXAgent│
                              │  (Orquestador)   │
                              └────────┬────────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           │                           │                           │
           ▼                           ▼                           ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│    SIMULADORES V1    │     │    SIMULADORES V2    │     │   ESPECIALIZADOS    │
│    (6 roles)         │     │    (5 roles)         │     │                     │
├─────────────────────┤     ├─────────────────────┤     ├─────────────────────┤
│                     │     │                     │     │                     │
│  PO-IA              │     │  SD-IA              │     │  IT-IA              │
│  (Product Owner)    │     │  (Senior Dev)       │     │  (Tech Interviewer) │
│                     │     │                     │     │  Endpoint: /interview│
│  SM-IA              │     │  QA-IA              │     │                     │
│  (Scrum Master)     │     │  (QA Engineer)      │     │  IR-IA              │
│                     │     │                     │     │  (Incident Responder)│
│  IT-IA              │     │  SA-IA              │     │  Endpoint: /incident │
│  (Tech Interviewer) │     │  (Security Auditor) │     │                     │
│                     │     │                     │     │                     │
│  IR-IA              │     │  TL-IA              │     │                     │
│  (Incident Responder)│    │  (Tech Lead)        │     │                     │
│                     │     │                     │     │                     │
│  CX-IA              │     │  DC-IA              │     │                     │
│  (Client)           │     │  (Demanding Client) │     │                     │
│                     │     │                     │     │                     │
│  DSO-IA             │     │                     │     │                     │
│  (DevSecOps)        │     │                     │     │                     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

#### 4.3.3 Simuladores V1 (Sprint 4)

| ID | Simulador | Rol | Competencias Evaluadas |
|----|-----------|-----|------------------------|
| PO-IA | Product Owner | Priorización de backlog | Negociación, priorización, comunicación |
| SM-IA | Scrum Master | Gestión de sprints | Facilitación, resolución de conflictos |
| IT-IA | Tech Interviewer | Entrevistas técnicas | Comunicación técnica, resolución de problemas |
| IR-IA | Incident Responder | Respuesta a incidentes | Trabajo bajo presión, toma de decisiones |
| CX-IA | Client | Cliente exigente | Manejo de expectativas, comunicación |
| DSO-IA | DevSecOps | Auditoría de seguridad | Seguridad, mejores prácticas |

#### 4.3.4 Simuladores V2 (Sprint 6)

| ID | Simulador | Rol | Competencias Evaluadas |
|----|-----------|-----|------------------------|
| SD-IA | Senior Developer | Code review | Calidad de código, mentoring |
| QA-IA | QA Engineer | Testing | Estrategias de testing, cobertura |
| SA-IA | Security Auditor | Seguridad | OWASP, vulnerabilidades |
| TL-IA | Tech Lead | Arquitectura | Decisiones arquitectónicas, liderazgo |
| DC-IA | Demanding Client | Requisitos cambiantes | Adaptabilidad, comunicación |

#### 4.3.5 IT-IA: Sistema de Entrevistas Técnicas

**Endpoint Especializado**: `POST /simulators/interview/*`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IT-IA: FLUJO DE ENTREVISTA TÉCNICA                        │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────────┐
                    │  POST /interview/start  │
                    │  {difficulty, topic}    │
                    └───────────┬─────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │  InterviewSessionDB     │
                    │  Created (status=active)│
                    └───────────┬─────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    ▼                       ▼
        ┌───────────────────┐   ┌───────────────────┐
        │ POST /interview/  │   │ POST /interview/  │
        │ {interview_id}/   │   │ {interview_id}/   │
        │ response          │   │ hint              │
        └─────────┬─────────┘   └───────────────────┘
                  │
                  ▼
        ┌───────────────────┐
        │  Evaluate         │
        │  Response         │
        │  (LLM Analysis)   │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │  Generate         │
        │  Follow-up        │
        │  Question         │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │  POST /interview/ │
        │  {id}/end         │
        └─────────┬─────────┘
                  │
                  ▼
        ┌───────────────────┐
        │  InterviewReport  │
        │  Generated        │
        └───────────────────┘
```

#### 4.3.6 IR-IA: Sistema de Respuesta a Incidentes

**Endpoint Especializado**: `POST /simulators/incident/*`

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    IR-IA: FLUJO DE SIMULACIÓN DE INCIDENTE                   │
└─────────────────────────────────────────────────────────────────────────────┘

            ┌─────────────────────────────┐
            │  POST /incident/start       │
            │  {severity, incident_type}  │
            └─────────────┬───────────────┘
                          │
                          ▼
            ┌─────────────────────────────┐
            │  IncidentSimulationDB       │
            │  Created (status=active)    │
            │  Timer Started              │
            └─────────────┬───────────────┘
                          │
            ┌─────────────┴─────────────┐
            │                           │
            ▼                           ▼
┌───────────────────────┐   ┌───────────────────────┐
│  POST /incident/      │   │  POST /incident/      │
│  {id}/action          │   │  {id}/escalate        │
│  {action_type,        │   │  {escalation_level}   │
│   description}        │   │                       │
└───────────┬───────────┘   └───────────────────────┘
            │
            ▼
┌───────────────────────┐
│  Evaluate Action      │
│  Update Severity      │
│  Generate Consequence │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  POST /incident/      │
│  {id}/resolve         │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  IncidentReport       │
│  Response Time        │
│  Actions Taken        │
│  Effectiveness Score  │
└───────────────────────┘
```

#### 4.3.7 Competencias Evaluadas por Simulador

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPETENCIAS POR SIMULADOR                                │
└─────────────────────────────────────────────────────────────────────────────┘

PO-IA (Product Owner)
├── Comunicación con stakeholders
├── Priorización de backlog
├── Definición de criterios de aceptación
└── Negociación de alcance

SM-IA (Scrum Master)
├── Facilitación de ceremonias
├── Resolución de impedimentos
├── Protección del equipo
└── Mejora continua

IT-IA (Tech Interviewer)
├── Resolución de problemas algorítmicos
├── Comunicación técnica
├── Pensamiento estructurado
└── Manejo de presión

IR-IA (Incident Responder)
├── Diagnóstico bajo presión
├── Toma de decisiones rápidas
├── Comunicación de crisis
├── Documentación de incidentes
└── Gestión de escalaciones

CX-IA (Client)
├── Manejo de expectativas
├── Comunicación no técnica
├── Gestión de cambios
└── Resolución de conflictos

DSO-IA (DevSecOps)
├── Identificación de vulnerabilidades
├── Mejores prácticas de seguridad
├── Cumplimiento normativo
└── Respuesta a amenazas
```

---

### 4.4 AR-IA: Analista de Riesgos

#### 4.4.1 Visión General

**Archivo**: `backend/agents/risk_analyst.py`

El AR-IA (Analista de Riesgo Cognitivo y Ético) supervisa el proceso de aprendizaje para detectar comportamientos de riesgo en 5 dimensiones.

#### 4.4.2 Diagrama de las 5 Dimensiones de Riesgo

```
                        ┌─────────────────────────────────────────────┐
                        │           AR-IA: ANÁLISIS 5D                │
                        │        Supervisión Multidimensional          │
                        └─────────────────────────────────────────────┘
                                            │
           ┌────────────────────────────────┼────────────────────────────────┐
           │                                │                                │
           ▼                                ▼                                ▼
┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────────┐
│     COGNITIVO       │          │       ÉTICO         │          │     EPISTÉMICO      │
│       (RC)          │          │       (RE)          │          │       (REp)         │
├─────────────────────┤          ├─────────────────────┤          ├─────────────────────┤
│ • Delegación total  │          │ • Integridad acad.  │          │ • Error conceptual  │
│ • Razonamiento sup. │          │ • Uso no declarado  │          │ • Falacia lógica    │
│ • Dependencia IA    │          │ • Plagio            │          │ • Aceptación acrít. │
│ • Falta justific.   │          │                     │          │                     │
│ • Sin autorregulac. │          │                     │          │                     │
└─────────────────────┘          └─────────────────────┘          └─────────────────────┘
           │                                                                 │
           │                    ┌─────────────────────────────────┐         │
           │                    │                                  │         │
           ▼                    ▼                                  ▼         ▼
┌─────────────────────┐          ┌─────────────────────┐
│      TÉCNICO        │          │    GOBERNANZA       │
│       (RT)          │          │       (RG)          │
├─────────────────────┤          ├─────────────────────┤
│ • Vulnerabilidad    │          │ • Violación políti. │
│ • Baja calidad cod. │          │ • Uso no autorizado │
│ • Fallo arquitect.  │          │ • Automatización    │
└─────────────────────┘          └─────────────────────┘
```

#### 4.4.3 Los 18 Tipos de Riesgo

**Riesgos Cognitivos (RC)**:

| Código | Tipo | Descripción | Nivel Típico |
|--------|------|-------------|--------------|
| RC1 | `COGNITIVE_DELEGATION` | Solicitar código completo sin descomposición | HIGH |
| RC2 | `SUPERFICIAL_REASONING` | Razonamiento superficial sin profundidad | MEDIUM |
| RC3 | `AI_DEPENDENCY` | Dependencia excesiva de IA (>70%) | MEDIUM |
| RC4 | `LACK_JUSTIFICATION` | Decisiones sin justificación | MEDIUM |
| RC5 | `NO_SELF_REGULATION` | Falta de autorregulación del aprendizaje | LOW |

**Riesgos Éticos (RE)**:

| Código | Tipo | Descripción | Nivel Típico |
|--------|------|-------------|--------------|
| RE1 | `ACADEMIC_INTEGRITY` | Violación de integridad académica | HIGH |
| RE2 | `UNDISCLOSED_AI_USE` | Uso no declarado de IA | MEDIUM |
| RE3 | `PLAGIARISM` | Plagio de código o contenido | CRITICAL |

**Riesgos Epistémicos (REp)**:

| Código | Tipo | Descripción | Nivel Típico |
|--------|------|-------------|--------------|
| REp1 | `CONCEPTUAL_ERROR` | Error en comprensión conceptual | MEDIUM |
| REp2 | `LOGICAL_FALLACY` | Falacia lógica en razonamiento | MEDIUM |
| REp3 | `UNCRITICAL_ACCEPTANCE` | Aceptar respuestas de IA sin cuestionar | MEDIUM |

**Riesgos Técnicos (RT)**:

| Código | Tipo | Descripción | Nivel Típico |
|--------|------|-------------|--------------|
| RT1 | `SECURITY_VULNERABILITY` | Código con vulnerabilidades de seguridad | MEDIUM-HIGH |
| RT2 | `POOR_CODE_QUALITY` | Código de baja calidad (DRY violations) | LOW |
| RT3 | `ARCHITECTURAL_FLAW` | Fallo arquitectónico o de diseño | MEDIUM |

**Riesgos de Gobernanza (RG)**:

| Código | Tipo | Descripción | Nivel Típico |
|--------|------|-------------|--------------|
| RG1 | `POLICY_VIOLATION` | Violación de políticas institucionales | LOW-MEDIUM |
| RG2 | `UNAUTHORIZED_USE` | Uso no autorizado del sistema | MEDIUM |
| RG3 | `AUTOMATION_SUSPECTED` | Patrón de uso automatizado sospechoso | MEDIUM |

#### 4.4.4 Niveles de Severidad

```python
class RiskLevel(str, Enum):
    CRITICAL = "critical"  # Requiere intervención inmediata del docente
    HIGH = "high"          # Requiere atención prioritaria
    MEDIUM = "medium"      # Monitorear y guiar al estudiante
    LOW = "low"            # Informativo, registrar para análisis
    INFO = "info"          # Solo registro, sin acción requerida
```

#### 4.4.5 Flujo de Análisis de Sesión

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO: analyze_session(trace_sequence)                    │
└─────────────────────────────────────────────────────────────────────────────┘

                    TraceSequence
                          │
                          ▼
            ┌─────────────────────────┐
            │   Crear RiskReport      │
            │   vacío con metadata    │
            └─────────────┬───────────┘
                          │
          ┌───────────────┼───────────────┬───────────────┬───────────────┐
          │               │               │               │               │
          ▼               ▼               ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │Cognitivo │   │  Ético   │   │Epistémico│   │ Técnico  │   │Gobernanza│
    │ (RC)     │   │  (RE)    │   │  (REp)   │   │  (RT)    │   │  (RG)    │
    │          │   │          │   │          │   │          │   │          │
    │• RC1-RC5 │   │• RE1-RE3 │   │• REp1-3  │   │• RT1-RT3 │   │• RG1-RG3 │
    └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
          │               │               │               │               │
          └───────────────┴───────────────┴───────────────┴───────────────┘
                                          │
                                          ▼
                            ┌─────────────────────────┐
                            │    report.add_risk()    │
                            │   (para cada riesgo)    │
                            └─────────────┬───────────┘
                                          │
                                          ▼
                            ┌─────────────────────────┐
                            │ _generate_overall_      │
                            │ assessment(report)      │
                            └─────────────┬───────────┘
                                          │
                                          ▼
                            ┌─────────────────────────┐
                            │ _generate_priority_     │
                            │ interventions(report)   │
                            └─────────────┬───────────┘
                                          │
                                          ▼
                            ┌─────────────────────────┐
                            │   _analyze_trends()     │
                            │ (mejorando/empeorando)  │
                            └─────────────┬───────────┘
                                          │
                                          ▼
                               ┌─────────────────┐
                               │   RiskReport    │
                               │   completo      │
                               └─────────────────┘
```

#### 4.4.6 Intervenciones Pedagógicas por Riesgo

| Riesgo | Intervención Pedagógica |
|--------|------------------------|
| `COGNITIVE_DELEGATION` | "Modo socrático estricto: solo preguntas, sin pistas directas" |
| `ACADEMIC_INTEGRITY` | "Solicitar que explique línea por línea el código enviado" |
| `AI_DEPENDENCY` | "Fomentar resolución autónoma con menos asistencia de IA" |
| `LACK_JUSTIFICATION` | "Exigir explícitamente justificaciones" |
| `SECURITY_VULNERABILITY` | "Revisar OWASP Top 10 y mejores prácticas" |

---

### 4.5 GOV-IA: Gobernanza Institucional

#### 4.5.1 Visión General

**Archivo**: `backend/agents/governance.py`

El GOV-IA (Gobernanza Institucional) es el agente responsable de operacionalizar las políticas institucionales de IA generativa en el contexto educativo.

#### 4.5.2 Arquitectura del Sistema de Gobernanza

```
+===============================================================+
|                    CAPA 1: GOBERNANZA INSTITUCIONAL            |
|  GobernanzaAgent (governance.py)                               |
|  - Verificación de cumplimiento                                |
|  - Sanitización de PII                                         |
|  - Generación de reportes de auditoría                        |
+===============================================================+
                            |
                            v
+===============================================================+
|                    CAPA 2: GOBERNANZA PEDAGÓGICA              |
|  TutorGovernanceEngine (tutor_governance.py)                  |
|  - Sistema de semáforos (VERDE/AMARILLO/ROJO)                 |
|  - Procesamiento en 3 fases (IPC, GSR, Andamiaje)             |
|  - Restricciones adaptativas                                   |
+===============================================================+
                            |
                            v
+===============================================================+
|                    CAPA 3: REGLAS PEDAGÓGICAS                 |
|  TutorRulesEngine (tutor_rules.py)                            |
|  - 4 reglas inquebrantables                                    |
|  - Tipos de intervención                                       |
|  - Niveles de andamiaje cognitivo                             |
+===============================================================+
```

#### 4.5.3 Sistema de Sanitización de PII

**Patrones Detectados**:

```python
pii_patterns = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "dni": r'\b\d{7,8}\b',           # DNI argentino
    "phone": r'\b\d{2,4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
    "credit_card": r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b'
}
```

**Proceso de Sanitización**:

```
Input: "Mi email es juan@universidad.edu y mi DNI 12345678"

       |
       v [sanitize_prompt()]

Output: "Mi email es [EMAIL_REDACTED] y mi DNI [DNI_REDACTED]"
Return: (prompt_sanitizado, pii_found=True)
```

#### 4.5.4 Estados de Cumplimiento

```python
class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"    # Cumple todas las políticas
    WARNING = "warning"        # Advertencias, pero permite acción
    VIOLATION = "violation"    # Violación, bloquea acción
```

#### 4.5.5 Sistema de Semáforos

```python
class SemaforoState(str, Enum):
    VERDE = "verde"      # Bajo riesgo, interacción normal
    AMARILLO = "amarillo"  # Riesgo medio, monitorear
    ROJO = "rojo"        # Riesgo alto, intervención restrictiva
```

| Estado | Color | Nivel de Riesgo | Comportamiento |
|--------|-------|-----------------|----------------|
| VERDE | Verde | Bajo | Interacción normal, ayuda disponible |
| AMARILLO | Amarillo | Medio | Reducción de ayuda, monitoreo activo |
| ROJO | Rojo | Alto | Bloqueo de código, redirección pedagógica |

#### 4.5.6 Procesamiento en 3 Fases

```
                 Prompt Estudiante
                        |
                        v
        +===============================+
        |    FASE 1: IPC               |
        |    Ingesta y Comprensión     |
        |    de Prompt                 |
        +===============================+
                        |
                        v
        +===============================+
        |    FASE 2: GSR               |
        |    Gobernanza y Semáforo     |
        |    de Riesgo                 |
        +===============================+
                        |
                        v
        +===============================+
        |    FASE 3: ANDAMIAJE         |
        |    Selección de Estrategia   |
        |    de Andamiaje              |
        +===============================+
                        |
                        v
               Respuesta Tutor
```

#### 4.5.7 Detección de Intención (PromptIntent)

```python
class PromptIntent(str, Enum):
    EXPLORACION = "exploracion"    # Explorando el problema
    DEPURACION = "depuracion"      # Debugueando código
    DELEGACION = "delegacion"      # Quiere que la IA resuelva todo
    CLARIFICACION = "clarificacion" # Necesita entender conceptos
    VALIDACION = "validacion"      # Quiere validar su enfoque
```

| Intención | Patrones Detectados |
|-----------|---------------------|
| DELEGACION | "haceme", "resolve", "dame el código", "escribí el código" |
| DEPURACION | "no funciona", "error", "falla", "bug", "qué está mal" |
| CLARIFICACION | "qué es", "cómo funciona", "explica", "no entiendo" |
| VALIDACION | "está bien", "es correcto", "qué te parece", "revisa" |
| EXPLORACION | Default (cualquier otro patrón) |

#### 4.5.8 Matriz de Decisiones por Semáforo

| Semáforo | Código? | Pseudocódigo? | Respuesta Tipo | Nivel Ayuda | Justificación? |
|----------|---------|---------------|----------------|-------------|----------------|
| VERDE | NO | SI | Variable | Variable | SI |
| AMARILLO | NO | SI | Pistas | Bajo | SI (enfático) |
| ROJO | NO | NO | Socrático | Mínimo | OBLIGATORIO |

---

### 4.6 TC-N4: Trazabilidad Cognitiva

#### 4.6.1 Visión General

**Archivo**: `backend/agents/traceability.py`

El TC-N4 (Trazabilidad Cognitiva de Nivel 4) captura todas las interacciones en 4 niveles de profundidad para permitir la evaluación del proceso de aprendizaje.

#### 4.6.2 Los 4 Niveles de Trazabilidad

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TC-N4: NIVELES DE TRAZABILIDAD                       │
└─────────────────────────────────────────────────────────────────────────────┘

    N1: SUPERFICIAL                N2: TÉCNICO
    ┌─────────────────┐            ┌─────────────────┐
    │  • Archivos     │            │  • Commits      │
    │  • Entregas     │            │  • Branches     │
    │  • Versión final│            │  • Tests auto   │
    │                 │            │  • CI/CD logs   │
    └─────────────────┘            └─────────────────┘
            │                              │
            │         ┌────────────────────┘
            │         │
            ▼         ▼
    ┌─────────────────────────────────────────────────┐
    │              COGNITIVE TRACE DB                  │
    │                                                  │
    │  session_id | student_id | trace_level | ...    │
    └─────────────────────────────────────────────────┘
            ▲         ▲
            │         │
            │         └────────────────────┐
            │                              │
    N3: INTERACCIONAL              N4: COGNITIVO
    ┌─────────────────┐            ┌─────────────────┐
    │  • Prompts      │            │  • Intención    │
    │  • Respuestas   │            │  • Decisiones   │
    │  • Reintentos   │            │  • Justificac.  │
    │  • Correcciones │            │  • Alternativas │
    └─────────────────┘            │  • Riesgos      │
                                   └─────────────────┘
```

| Nivel | Nombre | Qué Captura |
|-------|--------|-------------|
| N1 | Superficial | Archivos, entregas, versión final del código |
| N2 | Técnico | Commits, branches, tests automatizados, logs CI/CD |
| N3 | Interaccional | Prompts, respuestas, reintentos, correcciones |
| N4 | Cognitivo | Intención, decisiones, justificaciones, alternativas, riesgos |

#### 4.6.3 Las 6 Dimensiones del N4

| Dimensión | Descripción | Datos Capturados |
|-----------|-------------|------------------|
| **Semántica** | Comprensión del problema | Interpretación, definición del problema |
| **Algorítmica** | Diseño de solución | Estrategia, estructuras de datos, complejidad |
| **Cognitiva** | Proceso mental | Estado cognitivo, carga cognitiva, dudas |
| **Interaccional** | Uso de IA | Prompts, respuestas aceptadas/rechazadas |
| **Ética** | Integridad académica | Declaración de uso de IA, atribuciones |
| **Proceso** | Metodología | Planificación, iteraciones, testing |

#### 4.6.4 Tipos de Interacción

```python
class InteractionType(str, Enum):
    STUDENT_PROMPT = "student_prompt"       # Mensaje del estudiante
    AI_RESPONSE = "ai_response"             # Respuesta del agente IA
    TUTOR_INTERVENTION = "tutor_intervention"  # Intervención pedagógica
    SELF_CORRECTION = "self_correction"     # Autocorrección del estudiante
    DESIGN_DECISION = "design_decision"     # Decisión de diseño documentada
```

#### 4.6.5 Estados Cognitivos

```python
class CognitiveState(str, Enum):
    EXPLORACION = "exploracion"       # Fase inicial de comprensión
    PLANIFICACION = "planificacion"   # Diseño de solución
    IMPLEMENTACION = "implementacion" # Escribiendo código
    DEPURACION = "depuracion"         # Resolviendo problemas
    VALIDACION = "validacion"         # Verificando solución
```

---

## 5. Flujo de Procesamiento de 10 Fases

### 5.1 Diagrama Completo del Flujo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FLUJO DE 10 FASES: PREGUNTA A RESPUESTA                         │
│              Orquestación Multi-Agente AI-Native                             │
└─────────────────────────────────────────────────────────────────────────────┘

FASE 1: RECEPCIÓN
┌─────────────────────────────────────────────────────────────────────────────┐
│  Frontend → POST /api/v1/interactions                                        │
│  {session_id, prompt, context}                                               │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
FASE 2: VALIDACIÓN Y SANITIZACIÓN
┌─────────────────────────────────────────────────────────────────────────────┐
│  AIGateway._validate_interaction_input()                                     │
│  GOV-IA.sanitize_prompt()                                                    │
│  ├─ Validar session_id, prompt length, context size                         │
│  └─ Detectar y redactar PII (emails, DNI, teléfonos, tarjetas)             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
FASE 3: OBTENCIÓN DE CONTEXTO
┌─────────────────────────────────────────────────────────────────────────────┐
│  session_repo.get_by_id(session_id)                                          │
│  ├─ Cargar sesión desde PostgreSQL (STATELESS)                              │
│  ├─ Extraer: student_id, activity_id, current_mode                          │
│  └─ Cargar historial de conversación (trace_repo.get_by_session)            │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
FASE 4: CLASIFICACIÓN (IPC)
┌─────────────────────────────────────────────────────────────────────────────┐
│  CognitiveEngine.classify_prompt(prompt, context)                            │
│  ├─ Detectar delegación total                                                │
│  ├─ Identificar estado cognitivo (EXPLORACION, PLANIFICACION, etc.)         │
│  ├─ Determinar si es pregunta                                                │
│  ├─ Detectar solicitud de explicación                                        │
│  └─ Sugerir tipo de respuesta                                                │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
FASE 5: VERIFICACIÓN DE GOBERNANZA (GSR)
┌─────────────────────────────────────────────────────────────────────────────┐
│  GOV-IA.verify_compliance(trace_sequence, policies)                          │
│  TutorGovernanceEngine.process_student_request()                             │
│  ├─ Evaluar políticas institucionales                                        │
│  ├─ Determinar estado del semáforo (VERDE/AMARILLO/ROJO)                    │
│  ├─ Verificar 4 reglas inquebrantables                                       │
│  └─ Decidir si bloquear o permitir                                           │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
            [BLOQUEADO]                        [PERMITIDO]
                    │                                 │
                    ▼                                 ▼
FASE 6A: RESPUESTA BLOQUEADA          FASE 6B: TRAZA DE ENTRADA
┌───────────────────────────┐         ┌───────────────────────────┐
│ _generate_blocked_response│         │ TC-N4._create_trace()     │
│ ├─ Mensaje pedagógico     │         │ ├─ STUDENT_PROMPT         │
│ ├─ Registrar intervención │         │ ├─ N4_COGNITIVO           │
│ └─ Registrar riesgo RC1   │         │ └─ cognitive_intent       │
└───────────────────────────┘         └─────────────┬─────────────┘
                                                     │
                                                     ▼
                                      FASE 7: ESTRATEGIA PEDAGÓGICA (CRPE)
                                      ┌───────────────────────────────────┐
                                      │ CognitiveEngine.generate_         │
                                      │ pedagogical_response_strategy()   │
                                      │ ├─ Cargar historial del estudiante│
                                      │ ├─ Aplicar políticas pedagógicas  │
                                      │ ├─ Determinar max_help_level      │
                                      │ └─ Generar instrucciones y        │
                                      │    constraints para LLM           │
                                      └─────────────┬─────────────────────┘
                                                     │
                                                     ▼
                                      FASE 8: ROUTING A AGENTE (OSM)
                                      ┌───────────────────────────────────┐
                                      │ Según current_mode:               │
                                      │ ├─ TUTOR → T-IA-Cog              │
                                      │ ├─ SIMULATOR → S-IA-X            │
                                      │ ├─ EVALUATOR → E-IA-Proc         │
                                      │ ├─ RISK_ANALYST → AR-IA          │
                                      │ └─ GOVERNANCE → GOV-IA           │
                                      └─────────────┬─────────────────────┘
                                                     │
                                                     ▼
                                      FASE 9: GENERACIÓN DE RESPUESTA
                                      ┌───────────────────────────────────┐
                                      │ Agente activo genera respuesta:   │
                                      │ ├─ Construir prompt de sistema    │
                                      │ ├─ Incluir historial conversación │
                                      │ ├─ Verificar cache LLM            │
                                      │ ├─ Llamar a Ollama/Mock           │
                                      │ └─ Aplicar restricciones          │
                                      └─────────────┬─────────────────────┘
                                                     │
                                                     ▼
                                      FASE 10: POST-PROCESAMIENTO
                                      ┌───────────────────────────────────┐
                                      │ ├─ TC-N4: Registrar traza respuesta│
                                      │ ├─ AR-IA: Analizar riesgos        │
                                      │ ├─ Persistir en PostgreSQL        │
                                      │ ├─ Guardar en cache LLM           │
                                      │ └─ Registrar métricas Prometheus  │
                                      └─────────────┬─────────────────────┘
                                                     │
                                                     ▼
                                      ┌───────────────────────────────────┐
                                      │        InteractionResponse        │
                                      │        → Frontend                  │
                                      └───────────────────────────────────┘
```

### 5.2 Matriz RACI de Responsabilidades

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MATRIZ RACI: RESPONSABILIDADES POR AGENTE                 │
│                                                                              │
│   R = Responsible (Ejecuta)      A = Accountable (Aprueba)                  │
│   C = Consulted (Consultado)     I = Informed (Informado)                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┬────────┬────────┬────────┬────────┬────────┬────────┐
│      Actividad       │AIGateway│T-IA-Cog│E-IA-Proc│ S-IA-X │ AR-IA │GOV-IA │
├──────────────────────┼────────┼────────┼────────┼────────┼────────┼────────┤
│ Recibir request      │   R/A  │   I    │   I    │   I    │   I    │   I    │
│ Validar input        │   R    │   -    │   -    │   -    │   -    │   C    │
│ Sanitizar PII        │   C    │   -    │   -    │   -    │   -    │   R/A  │
│ Clasificar prompt    │   R    │   C    │   -    │   -    │   C    │   C    │
│ Verificar gobernanza │   C    │   -    │   -    │   -    │   C    │   R/A  │
│ Decidir semáforo     │   I    │   C    │   -    │   -    │   C    │   R/A  │
│ Registrar traza N4   │   R    │   I    │   I    │   I    │   I    │   I    │
│ Generar estrategia   │   R    │   C    │   -    │   -    │   -    │   C    │
│ Routing a agente     │   R/A  │   I    │   I    │   I    │   I    │   I    │
│ Respuesta tutorial   │   I    │   R/A  │   -    │   -    │   C    │   C    │
│ Respuesta simulador  │   I    │   -    │   -    │   R/A  │   C    │   C    │
│ Evaluar proceso      │   I    │   C    │   R/A  │   -    │   C    │   I    │
│ Analizar riesgos     │   C    │   I    │   I    │   I    │   R/A  │   C    │
│ Persistir datos      │   R    │   -    │   -    │   -    │   -    │   -    │
│ Métricas Prometheus  │   R    │   -    │   -    │   -    │   -    │   -    │
└──────────────────────┴────────┴────────┴────────┴────────┴────────┴────────┘
```

---

## 6. Sistema de Trazabilidad N4

### 6.1 Modelo de Datos CognitiveTrace

```python
class CognitiveTrace(BaseModel):
    """Representa una traza cognitiva en el sistema"""

    # Identificación
    id: str
    session_id: str          # REQUERIDO
    student_id: str
    activity_id: str

    # Clasificación
    trace_level: TraceLevel  # n1_superficial, n2_tecnico, n3_interaccional, n4_cognitivo
    interaction_type: InteractionType

    # Contenido
    content: str
    trace_metadata: Dict[str, Any]  # Metadata adicional

    # Contexto cognitivo (N4)
    cognitive_intent: Optional[CognitiveIntent]
    cognitive_state: Optional[CognitiveState]

    # Análisis
    ai_involvement: float    # 0-1
    autonomy_level: float    # 0-1

    # Agente
    agent_id: Optional[str]

    # Timestamps
    created_at: datetime
```

### 6.2 Estructura de TraceSequence

```python
class TraceSequence(BaseModel):
    """Secuencia de trazas para una sesión completa"""

    id: str
    session_id: str
    student_id: str
    activity_id: str

    # Trazas ordenadas cronológicamente
    traces: List[CognitiveTrace]

    # Métricas agregadas
    total_traces: int
    avg_ai_involvement: float
    dominant_cognitive_state: Optional[CognitiveState]

    # Análisis temporal
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[float]
```

### 6.3 Flujo de Captura de Trazas

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE CAPTURA DE TRAZAS N4                             │
└─────────────────────────────────────────────────────────────────────────────┘

Estudiante envía prompt
        │
        ▼
┌───────────────────────┐
│  TRAZA N3:            │
│  STUDENT_PROMPT       │
│  - content: prompt    │
│  - cognitive_state    │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  ANÁLISIS N4:         │
│  - cognitive_intent   │
│  - is_delegation      │
│  - ai_involvement     │
│  - autonomy_level     │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  TRAZA N4:            │
│  STUDENT_PROMPT +     │
│  cognitive_metadata   │
└───────────┬───────────┘
            │
            ▼
    [Procesamiento del agente]
            │
            ▼
┌───────────────────────┐
│  TRAZA N4:            │
│  AI_RESPONSE          │
│  - content: response  │
│  - agent_id           │
│  - strategy_used      │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│  PERSISTENCIA:        │
│  cognitive_traces     │
│  trace_sequences      │
└───────────────────────┘
```

---

## 7. Sistema de Gobernanza y Semáforos

### 7.1 Flujo Completo de Decisión

```
                            Estudiante envía prompt
                                     |
                                     v
+====================================+====================================+
|                           FASE 1: SEGURIDAD                           |
+========================================================================+
|                                                                        |
|   +------------------+                                                 |
|   | sanitize_prompt()|   Detecta: email, DNI, teléfono, tarjeta       |
|   +--------+---------+                                                 |
|            |                                                           |
|            v                                                           |
|   +------------------+                                                 |
|   | PII encontrado?  |---[SI]--> Reemplaza con [REDACTED]             |
|   +--------+---------+                                                 |
|            |[NO]                                                       |
|            v                                                           |
+========================================================================+
                                     |
                                     v
+====================================+====================================+
|                         FASE 2: CUMPLIMIENTO                          |
+========================================================================+
|                                                                        |
|   +-------------------+                                                |
|   | verify_compliance()|                                               |
|   +--------+----------+                                                |
|            |                                                           |
|    +-------+-------+-------+                                           |
|    |               |       |                                           |
|    v               v       v                                           |
| COMPLIANT     WARNING   VIOLATION                                      |
|    |               |       |                                           |
|    v               v       v                                           |
| Continuar    Advertir   Bloquear                                       |
|                          + Educar                                      |
+========================================================================+
                                     |
                                     v
+====================================+====================================+
|                         FASE 3: SEMÁFORO                              |
+========================================================================+
|                                                                        |
|   +------------------------+                                           |
|   | process_student_request|                                           |
|   +--------+---------------+                                           |
|            |                                                           |
|   [IPC] -> [GSR] -> [ANDAMIAJE]                                       |
|            |                                                           |
|    +-------+-------+-------+                                           |
|    |               |       |                                           |
|    v               v       v                                           |
|  VERDE        AMARILLO   ROJO                                          |
|    |               |       |                                           |
|    v               v       v                                           |
| Normal       Reducir    Bloquear                                       |
|              ayuda      código                                         |
+========================================================================+
                                     |
                                     v
+====================================+====================================+
|                      FASE 4: REGLAS PEDAGÓGICAS                       |
+========================================================================+
|                                                                        |
|   +--------------------+                                               |
|   | check_anti_solution|--[VIOLADA]--> Rechazo Pedagógico             |
|   +--------+-----------+                                               |
|            |[OK]                                                       |
|            v                                                           |
|   +---------------------+                                              |
|   | check_socratic_mode |--[FORZAR]--> Generar pregunta               |
|   +--------+------------+                                              |
|            |[OK]                                                       |
|            v                                                           |
|   +-----------------------+                                            |
|   | check_explicitacion   |--[FALTA]--> Exigir justificación          |
|   +--------+--------------+                                            |
|            |[OK]                                                       |
|            v                                                           |
|   +------------------------+                                           |
|   | check_conceptual_reinf |--[ERROR]--> Remisión a teoría            |
|   +--------+---------------+                                           |
|            |[OK]                                                       |
|            v                                                           |
+========================================================================+
                                     |
                                     v
                          Generar respuesta del tutor
```

### 7.2 Políticas Institucionales Configurables

| Política | Valor Default | Descripción |
|----------|---------------|-------------|
| `max_ai_assistance_level` | 0.7 | Nivel máximo de ayuda IA (0-1) |
| `require_explicit_ai_usage` | True | Exigir declaración explícita de uso de IA |
| `block_complete_solutions` | True | Bloquear solicitudes de código completo |
| `require_traceability` | True | Exigir trazabilidad N4 completa |
| `enforce_academic_integrity` | True | Aplicar políticas de integridad académica |

---

## 8. Análisis de Riesgos 5D

### 8.1 Relación AR-IA con Otros Agentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTERACCIONES DEL AR-IA CON OTROS AGENTES                 │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │  AI GATEWAY │
                              │ (Orquestador)│
                              └──────┬──────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
           ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
           │   T-IA-Cog  │   │   AR-IA     │   │   GOV-IA   │
           │   (Tutor)   │◄──│  (Analista) │──►│(Gobernanza) │
           └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
                  │                 │                  │
                  │                 │                  │
                  ▼                 ▼                  ▼
           ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
           │ Ajustar modo│   │ Registrar   │   │  Verificar  │
           │ pedagógico  │   │ en TC-N4    │   │ compliance  │
           └─────────────┘   └─────────────┘   └─────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
           ┌─────────────┐                 ┌─────────────┐
           │   TC-N4     │                 │  E-IA-Proc  │
           │(Trazabilidad)│                 │ (Evaluador) │
           └─────────────┘                 └─────────────┘
```

### 8.2 Flujo de Datos entre Agentes

```
1. ENTRADA DE DATOS
   ┌──────────────┐
   │  TC-N4       │ ──────► TraceSequence ──────► AR-IA
   │ (Trazas N4)  │         (CognitiveTrace[])
   └──────────────┘

   ┌──────────────┐
   │  S-IA-X      │ ──────► SimulatorEventDB[] ──────► AR-IA
   │ (Simuladores)│         (eventos de sesión)
   └──────────────┘

2. PROCESAMIENTO
   AR-IA analiza:
   • Patrones de delegación en prompts
   • Tiempos de respuesta (código sospechoso)
   • Aceptación acrítica de respuestas
   • Vulnerabilidades en código
   • Patrones de automatización

3. SALIDA DE DATOS
   AR-IA ──────► RiskReport ──────► AI Gateway
                                   │
                                   ├──► T-IA-Cog (ajustar andamiaje)
                                   ├──► GOV-IA (verificar compliance)
                                   └──► E-IA-Proc (incluir en evaluación)

4. PERSISTENCIA
   AR-IA ──────► RiskDB ──────► PostgreSQL
                │
                └──► RiskAlertDB (alertas institucionales)
```

### 8.3 Cálculo del Score Overall

```python
# overall_score = suma de los 5 dimension scores
overall_score = sum(dimension_scores)  # Max teórico: 50

# Nivel de riesgo según overall_score
if overall_score >= 40:
    risk_level = "critical"
elif overall_score >= 30:
    risk_level = "high"
elif overall_score >= 15:
    risk_level = "medium"
else:
    risk_level = "low"
```

---

## 9. Persistencia en Base de Datos

### 9.1 Diagrama de Tablas Principales

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MODELO DE DATOS - POSTGRESQL                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│     users       │      │    sessions     │      │  activities     │
├─────────────────┤      ├─────────────────┤      ├─────────────────┤
│ id (PK)         │◄─────│ user_id (FK)    │      │ id (PK)         │
│ email           │      │ id (PK)         │◄─────│ session_id (FK) │
│ hashed_password │      │ activity_id     │      │ name            │
│ role            │      │ mode            │      │ difficulty      │
│ created_at      │      │ status          │      │                 │
└─────────────────┘      │ created_at      │      └─────────────────┘
                         └────────┬────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│cognitive_traces │      │     risks       │      │  evaluations    │
├─────────────────┤      ├─────────────────┤      ├─────────────────┤
│ id (PK)         │      │ id (PK)         │      │ id (PK)         │
│ session_id (FK) │      │ session_id (FK) │      │ session_id (FK) │
│ student_id      │      │ risk_type       │      │ overall_score   │
│ trace_level     │      │ risk_level      │      │ dimensions      │
│ interaction_type│      │ dimension       │      │ competency_level│
│ content         │      │ description     │      │ feedback        │
│ trace_metadata  │      │ resolved        │      │ created_at      │
│ cognitive_intent│      │ evidence        │      └─────────────────┘
│ ai_involvement  │      │ created_at      │
│ created_at      │      └─────────────────┘
└─────────────────┘
        │
        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│trace_sequences  │      │  interactions   │      │ simulator_events│
├─────────────────┤      ├─────────────────┤      ├─────────────────┤
│ id (PK)         │      │ id (PK)         │      │ id (PK)         │
│ session_id (FK) │      │ session_id (FK) │      │ session_id (FK) │
│ traces          │      │ prompt          │      │ event_type      │
│ avg_ai_involve  │      │ response        │      │ event_data      │
│ created_at      │      │ agent_used      │      │ created_at      │
└─────────────────┘      │ created_at      │      └─────────────────┘
                         └─────────────────┘
```

### 9.2 Tablas por Agente

#### 9.2.1 Tablas del T-IA-Cog (Tutor)

| Tabla | Propósito |
|-------|-----------|
| `sessions` | Sesiones de tutoría |
| `interactions` | Historial de interacciones |
| `cognitive_traces` | Trazas de nivel N4 |

#### 9.2.2 Tablas del E-IA-Proc (Evaluador)

| Tabla | Propósito |
|-------|-----------|
| `evaluations` | Evaluaciones generadas |
| `evaluation_dimensions` | Dimensiones de evaluación |
| `trace_sequences` | Secuencias de trazas analizadas |

#### 9.2.3 Tablas del S-IA-X (Simuladores)

| Tabla | Propósito |
|-------|-----------|
| `simulator_events` | Eventos de simuladores |
| `interview_sessions` | Sesiones de entrevista (IT-IA) |
| `incident_simulations` | Simulaciones de incidentes (IR-IA) |

#### 9.2.4 Tablas del AR-IA (Riesgos)

| Tabla | Propósito |
|-------|-----------|
| `risks` | Riesgos detectados |
| `risk_alerts` | Alertas institucionales |
| `remediation_plans` | Planes de remediación |

#### 9.2.5 Tablas del GOV-IA (Gobernanza)

| Tabla | Propósito |
|-------|-----------|
| `course_reports` | Reportes institucionales |
| `lti_deployments` | Configuración LTI 1.3 |
| `lti_sessions` | Sesiones de lanzamiento LTI |

### 9.3 Estructura Detallada de Tablas Clave

#### 9.3.1 Tabla `risks`

```sql
CREATE TABLE risks (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    -- Clasificación
    risk_type VARCHAR(100) NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low','medium','high','critical','info')),
    dimension VARCHAR(50) NOT NULL,

    -- Contenido
    description TEXT NOT NULL,
    impact TEXT,
    evidence JSONB DEFAULT '[]',
    trace_ids JSONB DEFAULT '[]',

    -- Análisis
    root_cause TEXT,
    impact_assessment TEXT,
    recommendations JSONB DEFAULT '[]',
    pedagogical_intervention TEXT,

    -- Estado
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    detected_by VARCHAR(50) DEFAULT 'AR-IA',

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_risk_session_resolved ON risks(session_id, resolved);
CREATE INDEX idx_risk_session_level ON risks(session_id, risk_level);
CREATE INDEX idx_student_resolved ON risks(student_id, resolved);
```

#### 9.3.2 Tabla `evaluations`

```sql
CREATE TABLE evaluations (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    -- Scores (escala 0-10)
    overall_score FLOAT NOT NULL,
    competency_level VARCHAR(20) NOT NULL,

    -- Dimensiones (JSON)
    dimensions JSONB NOT NULL,
    strengths JSONB DEFAULT '[]',
    areas_for_improvement JSONB DEFAULT '[]',

    -- Feedback
    formative_feedback TEXT,
    recommendations JSONB DEFAULT '[]',

    -- Metadata
    trace_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_eval_session_created ON evaluations(session_id, created_at);
```

#### 9.3.3 Tabla `cognitive_traces`

```sql
CREATE TABLE cognitive_traces (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    -- Clasificación
    trace_level VARCHAR(30) NOT NULL,
    interaction_type VARCHAR(50) NOT NULL,

    -- Contenido
    content TEXT NOT NULL,
    trace_metadata JSONB DEFAULT '{}',

    -- Contexto cognitivo
    cognitive_intent VARCHAR(50),
    cognitive_state VARCHAR(50),

    -- Análisis
    ai_involvement FLOAT DEFAULT 0.0,
    autonomy_level FLOAT DEFAULT 1.0,

    -- Agente
    agent_id VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_trace_session_level ON cognitive_traces(session_id, trace_level);
CREATE INDEX idx_trace_session_created ON cognitive_traces(session_id, created_at);
```

---

## 10. Colaboración Inter-Agentes

### 10.1 Diagrama de Integración Completa

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTEGRACIÓN COMPLETA DE AGENTES                           │
└─────────────────────────────────────────────────────────────────────────────┘

+------------------+
|     AIGateway    |
|   (Orquestador)  |
+--------+---------+
         |
         | process_request()
         v
+--------+---------+
|     GOV-IA       |<---------------------------+
|   (Gobernanza)   |                            |
+--------+---------+                            |
         |                                      |
         | verify_compliance()                  | risk_alerts
         | sanitize_prompt()                    |
         |                                      |
+--------v---------+                    +-------+------+
| TutorGovernance  |                    |    AR-IA     |
| Engine (Semáforo)|                    | (Analista de |
+--------+---------+                    |   Riesgos)   |
         |                              +-------^------+
         | process_student_request()            |
         |                                      |
+--------v---------+        +----------+        |
|   T-IA-Cog       |        |  E-IA    |        |
|   (Tutor)        |------->|  (Eval)  |--------+
+------------------+        +----------+
         |                        |
         +------------------------+
                  |
         +--------v--------+
         |     S-IA-X      |
         |  (Simuladores)  |
         +-----------------+
                  |
         +--------v--------+
         |     TC-N4       |
         | (Trazabilidad)  |
         +-----------------+
```

### 10.2 Flujos de Colaboración

#### 10.2.1 GOV-IA ↔ AIGateway

1. AIGateway recibe request del cliente
2. AIGateway invoca `GOV-IA.verify_compliance()` con context
3. Si `status == VIOLATION`: Bloquea y retorna mensaje educativo
4. Si `status == WARNING`: Procede con restricciones
5. Si `status == COMPLIANT`: Procede normalmente
6. GOV-IA sanitiza prompt antes de enviarlo a LLM

#### 10.2.2 GOV-IA ↔ T-IA-Cog (Tutor)

1. TutorAgent recibe prompt sanitizado
2. Invoca `TutorGovernanceEngine.process_student_request()`
3. Obtiene estado de semáforo (VERDE/AMARILLO/ROJO)
4. Aplica estrategia de andamiaje según semáforo
5. `TutorRulesEngine` verifica las 4 reglas fundamentales
6. Si regla violada: Genera intervención pedagógica

#### 10.2.3 GOV-IA ↔ AR-IA (Riesgos)

1. AR-IA detecta riesgo durante interacción
2. Envía alerta a GOV-IA con dimensión y severidad
3. GOV-IA actualiza políticas dinámicamente
4. GOV-IA puede escalar semáforo a ROJO
5. GOV-IA registra en auditoría

#### 10.2.4 GOV-IA ↔ E-IA (Evaluador)

1. E-IA genera evaluación de proceso
2. Incluye `ai_dependency_score` (0-1)
3. GOV-IA consulta score para ajustar políticas
4. Si `ai_dependency > 0.7`: Escala a AMARILLO/ROJO
5. Resultados se persisten en reportes institucionales

#### 10.2.5 AR-IA ↔ T-IA-Cog

| Riesgo Detectado | Ajuste en Tutor |
|------------------|-----------------|
| RC1: Delegación | Semáforo → ROJO, solo preguntas |
| RC3: Alta dependencia | Reducir nivel de ayuda |
| RC4: Sin justificación | Exigir justificaciones |
| REp3: Aceptación acrítica | Modo socrático estricto |

---

## 11. Endpoints de la API

### 11.1 Endpoints Principales

| Endpoint | Método | Agente | Descripción |
|----------|--------|--------|-------------|
| `/api/v1/interactions` | POST | AIGateway | Procesar interacción |
| `/api/v1/sessions` | POST/GET | AIGateway | Gestión de sesiones |
| `/api/v1/evaluations/{session_id}/generate` | POST | E-IA-Proc | Generar evaluación |
| `/api/v1/risk-analysis/{session_id}` | GET | AR-IA | Análisis 5D |
| `/api/v1/risks/session/{session_id}` | GET | AR-IA | Riesgos de sesión |
| `/api/v1/cognitive-path/{session_id}` | GET | TC-N4 | Camino cognitivo |
| `/api/v1/traceability/{interaction_id}` | GET | TC-N4 | Trazas N4 |

### 11.2 Endpoints de Simuladores

| Endpoint | Método | Simulador | Descripción |
|----------|--------|-----------|-------------|
| `/api/v1/simulators/interact` | POST | S-IA-X | Interacción genérica |
| `/api/v1/simulators/interview/start` | POST | IT-IA | Iniciar entrevista |
| `/api/v1/simulators/interview/{id}/response` | POST | IT-IA | Responder pregunta |
| `/api/v1/simulators/interview/{id}/end` | POST | IT-IA | Finalizar entrevista |
| `/api/v1/simulators/incident/start` | POST | IR-IA | Iniciar incidente |
| `/api/v1/simulators/incident/{id}/action` | POST | IR-IA | Ejecutar acción |
| `/api/v1/simulators/incident/{id}/resolve` | POST | IR-IA | Resolver incidente |

### 11.3 Endpoints de Reportes (GOV-IA)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/v1/reports/cohort` | POST | Generar reporte de cohorte |
| `/api/v1/reports/risk-dashboard` | POST | Dashboard de riesgos |
| `/api/v1/reports/{report_id}` | GET | Obtener reporte |
| `/api/v1/reports/activity/{activity_id}` | GET | Reporte de actividad |
| `/api/v1/reports/analytics` | GET | Analíticas de aprendizaje |

---

## 12. Referencias Bibliográficas

### 12.1 Fundamentos Teóricos

| Referencia | Aplicación en el Sistema |
|------------|--------------------------|
| Hutchins, E. (1995). Cognition in the Wild. MIT Press. | Cognición Distribuida - Distribución de carga cognitiva entre agentes |
| Clark, A., & Chalmers, D. (1998). The Extended Mind. Analysis, 58(1), 7-19. | Cognición Extendida - IA como extensión cognitiva |
| Sweller, J. (1988). Cognitive Load During Problem Solving. Cognitive Science, 12(2), 257-285. | Teoría de Carga Cognitiva - Reducción de carga extrínseca |
| Zimmerman, B. J. (2002). Becoming a Self-Regulated Learner. Theory into Practice, 41(2), 64-70. | Autorregulación - Modelo de 7 fases para evaluación |
| Wood, D., Bruner, J. S., & Ross, G. (1976). The Role of Tutoring in Problem Solving. Journal of Child Psychology and Psychiatry, 17(2), 89-100. | Andamiaje Cognitivo - Scaffolding adaptativo |

### 12.2 Marcos Normativos

| Estándar | Año | Aplicación |
|----------|-----|------------|
| UNESCO - Recommendation on the Ethics of AI | 2021 | Ética de IA en educación |
| OECD AI Principles | 2019 | Principios de transparencia y responsabilidad |
| IEEE Ethically Aligned Design | 2019 | Diseño ético de sistemas de IA |
| ISO/IEC 23894:2023 | 2023 | Risk Management in AI |
| ISO/IEC 42001:2023 | 2023 | AI Management System |

---

## Archivos del Sistema

### Archivos de Agentes

| Archivo | Agente | Propósito |
|---------|--------|-----------|
| `backend/core/ai_gateway.py` | AIGateway | Orquestador central |
| `backend/core/cognitive_engine.py` | CRPE | Motor de razonamiento cognitivo |
| `backend/agents/tutor.py` | T-IA-Cog | Tutor cognitivo |
| `backend/agents/tutor_rules.py` | T-IA-Cog | 4 reglas inquebrantables |
| `backend/agents/tutor_governance.py` | T-IA-Cog | Sistema de semáforos |
| `backend/agents/evaluator.py` | E-IA-Proc | Evaluador de procesos |
| `backend/agents/simulators.py` | S-IA-X | Simuladores profesionales |
| `backend/agents/risk_analyst.py` | AR-IA | Analista de riesgos |
| `backend/agents/governance.py` | GOV-IA | Gobernanza institucional |
| `backend/agents/traceability.py` | TC-N4 | Trazabilidad cognitiva |

### Archivos de Modelos y Schemas

| Archivo | Propósito |
|---------|-----------|
| `backend/database/models.py` | Modelos ORM (SQLAlchemy) |
| `backend/database/repositories.py` | Repositorios de datos |
| `backend/api/schemas/` | Schemas Pydantic |
| `backend/models/risk.py` | Modelos de riesgo |
| `backend/models/evaluation.py` | Modelos de evaluación |

### Archivos de Configuración

| Archivo | Propósito |
|---------|-----------|
| `backend/core/constants.py` | Constantes y umbrales |
| `backend/core/security.py` | Seguridad JWT/bcrypt |
| `backend/llm/factory.py` | Factory de LLM providers |
| `.env.example` | Plantilla de variables de entorno |

---

**Documento generado**: Diciembre 2025
**Versión**: 1.0
**Autor**: Claude Code (Análisis Arquitectónico)
**Proyecto**: AI-Native MVP - Tesis Doctoral
**Total de Agentes**: 6 (T-IA-Cog, E-IA-Proc, S-IA-X, AR-IA, GOV-IA, TC-N4)
**Total de Simuladores**: 11 (6 V1 + 5 V2)
**Niveles de Trazabilidad**: 4 (N1-N4)
**Dimensiones de Riesgo**: 5 (RC, RE, REp, RT, RG)
**Tipos de Riesgo**: 18