# Interacción del Tutor con los Demás Agentes del Ecosistema AI-Native

## Documento de Análisis de Orquestación Multi-Agente

**Autor**: Análisis realizado por Claude Code
**Fecha**: Diciembre 2025
**Relación con**: `explicatuto1.md` (Documentación detallada del Tutor)
**Archivos Clave Analizados**:
- `backend/core/ai_gateway.py` - Orquestador central
- `backend/core/cognitive_engine.py` - Motor de razonamiento (CRPE)
- `backend/agents/governance.py` - Agente de Gobernanza (GOV-IA)
- `backend/agents/risk_analyst.py` - Analista de Riesgo (AR-IA)
- `backend/agents/traceability.py` - Trazabilidad N4 (TC-N4)
- `backend/agents/tutor.py` - Tutor Cognitivo (T-IA-Cog)

---

## 1. Visión General del Ecosistema de Agentes

### 1.1 Los 6 Agentes del Sistema

El ecosistema AI-Native implementa **6 agentes especializados** que trabajan de forma coordinada:

| Agente | Código | Archivo | Responsabilidad Principal |
|--------|--------|---------|---------------------------|
| **Tutor Cognitivo** | T-IA-Cog | `tutor.py` | Guiar aprendizaje con pedagogía socrática |
| **Evaluador de Procesos** | E-IA-Proc | `evaluator.py` | Evaluar el proceso (no solo el producto) |
| **Simuladores Profesionales** | S-IA-X | `simulators.py` | Simular roles profesionales (PO, SM, etc.) |
| **Analista de Riesgo** | AR-IA | `risk_analyst.py` | Detectar y clasificar riesgos cognitivos/éticos |
| **Gobernanza Institucional** | GOV-IA | `governance.py` | Verificar cumplimiento de políticas |
| **Trazabilidad Cognitiva** | TC-N4 | `traceability.py` | Capturar y reconstruir proceso cognitivo |

### 1.2 Principio Arquitectónico: AIGateway como Orquestador STATELESS

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AIGateway (STATELESS)                           │
│                    Orquestador Central del Ecosistema                   │
│                                                                         │
│  • No mantiene estado en memoria                                        │
│  • Todo se persiste en PostgreSQL vía repositorios                      │
│  • Escalable horizontalmente (múltiples instancias)                     │
│  • Dependency Injection completa                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Flujo Completo: Desde la Pregunta del Estudiante

### 2.1 Diagrama de Secuencia Principal

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│Estudiante│     │AIGateway │     │  GOV-IA  │     │   CRPE   │     │ T-IA-Cog │     │  AR-IA   │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │                │                │
     │  1. prompt     │                │                │                │                │
     │───────────────►│                │                │                │                │
     │                │                │                │                │                │
     │                │ 2. sanitize    │                │                │                │
     │                │   (filtrar PII)│                │                │                │
     │                │───────────────►│                │                │                │
     │                │◄───────────────│                │                │                │
     │                │                │                │                │                │
     │                │ 3. classify    │                │                │                │
     │                │───────────────────────────────►│                │                │
     │                │◄───────────────────────────────│                │                │
     │                │                │                │                │                │
     │                │ 4. should_block│                │                │                │
     │                │───────────────────────────────►│                │                │
     │                │◄───────────────────────────────│                │                │
     │                │                │                │                │                │
     │                │ 5. persist input_trace (N4)    │                │                │
     │                │─────────────────────────────────────────────────────────────────►│
     │                │                │                │                │                │
     │                │ 6. generate_strategy            │                │                │
     │                │───────────────────────────────►│                │                │
     │                │◄───────────────────────────────│                │                │
     │                │                │                │                │                │
     │                │ 7. process_tutor_mode          │                │                │
     │                │─────────────────────────────────────────────────►│                │
     │                │                │                │                │                │
     │                │                │                │   (pipeline    │                │
     │                │                │                │   interno del  │                │
     │                │                │                │   tutor:       │                │
     │                │                │                │   IPC→GSR→     │                │
     │                │                │                │   Andamiaje→   │                │
     │                │                │                │   LLM→Resp)    │                │
     │                │◄─────────────────────────────────────────────────│                │
     │                │                │                │                │                │
     │                │ 8. persist response_trace (N4) │                │                │
     │                │─────────────────────────────────────────────────────────────────►│
     │                │                │                │                │                │
     │                │ 9. analyze_risks_async         │                │                │
     │                │──────────────────────────────────────────────────────────────────►│
     │                │                │                │                │                │
     │                │                │                │                │   (Detectar    │
     │                │                │                │                │   RC1, RC2,    │
     │                │                │                │                │   RC3, RE1,    │
     │                │                │                │                │   REp1)        │
     │                │◄──────────────────────────────────────────────────────────────────│
     │                │                │                │                │                │
     │  10. response  │                │                │                │                │
     │◄───────────────│                │                │                │                │
     │                │                │                │                │                │
```

### 2.2 Las 10 Fases del Flujo

| Fase | Componente | Acción | Descripción |
|------|------------|--------|-------------|
| **1** | Cliente → Gateway | `process_interaction()` | Estudiante envía prompt |
| **2** | Gateway → GOV-IA | `sanitize_prompt()` | Filtrar PII (emails, DNI, teléfonos) |
| **3** | Gateway → CRPE | `classify_prompt()` | Detectar intención, estado cognitivo, delegación |
| **4** | Gateway → CRPE | `should_block_response()` | Verificar si bloquear por delegación total |
| **5** | Gateway → TC-N4 | `_persist_trace()` | Registrar traza de entrada N4 |
| **6** | Gateway → CRPE | `generate_pedagogical_response_strategy()` | Generar estrategia pedagógica |
| **7** | Gateway → T-IA-Cog | `_process_tutor_mode()` | Procesar con pipeline del tutor |
| **8** | Gateway → TC-N4 | `_persist_trace()` | Registrar traza de respuesta N4 |
| **9** | Gateway → AR-IA | `_analyze_risks_async()` | Análisis de riesgos en background |
| **10** | Gateway → Cliente | return response | Devolver respuesta al estudiante |

---

## 3. Interacción Detallada: AIGateway ↔ Agentes

### 3.1 FASE 2: GOV-IA - Filtrado de PII

**Archivo**: `backend/agents/governance.py`
**Método**: `sanitize_prompt()`

```python
# Ejemplo de flujo en ai_gateway.py:252-292
sanitized_prompt, pii_detected = self.governance_agent.sanitize_prompt(prompt)
if pii_detected:
    logger.warning("PII detectado y removido del prompt")
    prompt = sanitized_prompt
```

**Patrones detectados**:
| Tipo | Regex | Reemplazo |
|------|-------|-----------|
| Email | `[A-Za-z0-9._%+-]+@...` | `[EMAIL_REDACTED]` |
| DNI | `\d{7,8}` | `[DNI_REDACTED]` |
| Teléfono | `\d{2,4}[-.\s]?\d{4}...` | `[PHONE_REDACTED]` |
| Tarjeta | `\d{4}[-.\s]?\d{4}...` | `[CARD_REDACTED]` |

### 3.2 FASE 3-4: CRPE - Clasificación y Bloqueo

**Archivo**: `backend/core/cognitive_engine.py`
**Métodos**: `classify_prompt()`, `should_block_response()`

```python
# Clasificación del prompt (cognitive_engine.py:53-105)
classification = {
    "is_total_delegation": bool,     # ¿Pide código completo?
    "is_question": bool,             # ¿Es una pregunta?
    "requests_explanation": bool,    # ¿Pide explicación?
    "cognitive_state": CognitiveState,  # Estado cognitivo detectado
    "requires_intervention": bool,   # ¿Necesita intervención?
    "suggested_response_type": str   # Tipo de respuesta sugerido
}
```

**Estados Cognitivos Detectables**:
```python
class CognitiveState(str, Enum):
    EXPLORACION = "exploracion"       # "no entiendo", "no sé"
    PLANIFICACION = "planificacion"   # "cómo implemento", "cómo hago"
    IMPLEMENTACION = "implementacion" # Default
    DEPURACION = "depuracion"         # "error", "bug", "falla"
    VALIDACION = "validacion"         # "funciona", "correcto"
```

**Decisión de Bloqueo**:
```python
# Si es delegación total Y la política lo bloquea → BLOQUEAR
if classification["is_total_delegation"] and policies["block_total_delegation"]:
    return True, "Delegación total detectada"
```

### 3.3 FASE 5 y 8: TC-N4 - Trazabilidad

**Archivo**: `backend/agents/traceability.py`
**Flujo**: El Gateway persiste trazas directamente vía repositorios

```python
# Crear traza de entrada (ai_gateway.py:319-329)
input_trace = self._create_trace(
    session_id=session_id,
    student_id=student_id,
    activity_id=activity_id,
    interaction_type=InteractionType.STUDENT_PROMPT,
    content=prompt,
    level=TraceLevel.N4_COGNITIVO,
    cognitive_intent=classification.get("cognitive_state"),
    context={"classification": classification}
)
self._persist_trace(input_trace)

# Crear traza de respuesta (ai_gateway.py:401-411)
response_trace = self._create_trace(
    ...
    interaction_type=InteractionType.AI_RESPONSE,
    content=response.get("response"),
    agent_id=current_mode.value,
    context={"strategy": strategy}
)
self._persist_trace(response_trace)
```

**Niveles de Trazabilidad**:
```
N1: Superficial  → Archivos, entregas, versión final
N2: Técnico      → Commits, branches, tests
N3: Interaccional → Prompts, respuestas, reintentos
N4: Cognitivo    → Intención, decisiones, justificaciones, alternativas, riesgo
```

### 3.4 FASE 6: CRPE - Estrategia Pedagógica

**Archivo**: `backend/core/cognitive_engine.py`
**Método**: `generate_pedagogical_response_strategy()`

```python
# Generar estrategia (cognitive_engine.py:139-221)
strategy = {
    "response_type": "socratic_questioning" | "conceptual_explanation" | "guided_hints",
    "cognitive_state": CognitiveState,
    "max_help_level": 0.7,  # 0-1
    "instructions": [...],   # Instrucciones para el LLM
    "constraints": [...],    # Restricciones a aplicar
    "expected_elements": [...],  # Elementos esperados en respuesta
    "student_context": {...}  # Análisis del historial (si disponible)
}
```

**Mapeo Tipo de Respuesta → Instrucciones**:

| response_type | Instrucciones |
|---------------|---------------|
| `socratic_questioning` | No dar código, hacer preguntas guía, solicitar descomposición |
| `conceptual_explanation` | Explicar conceptos, usar ejemplos, evitar implementación |
| `guided_hints` | Pistas graduadas, pseudocódigo alto nivel, solicitar justificación |

### 3.5 FASE 7: T-IA-Cog - Procesamiento del Tutor

**Archivo**: `backend/agents/tutor.py` + `tutor_governance.py` + `tutor_rules.py`

El tutor tiene su **propio pipeline interno** de 6 fases (documentado en `explicatuto1.md`):

```
┌─────────────────────────────────────────────────────────────────┐
│              PIPELINE INTERNO DEL TUTOR (T-IA-Cog)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  FASE 1     │    │  FASE 2     │    │  FASE 3     │         │
│  │    IPC      │───►│    GSR      │───►│  ANDAMIAJE  │         │
│  │ (Ingesta)   │    │(Semáforos)  │    │ (Estrategia)│         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  • Detectar         • 🟢 VERDE        • response_type          │
│    intención        • 🟡 AMARILLO     • help_level             │
│  • Estado           • 🔴 ROJO         • restrictions           │
│    cognitivo                                                    │
│  • Autonomía                                                    │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  FASE 4     │    │  FASE 5     │    │  FASE 6     │         │
│  │  REGLAS     │───►│   LLM       │───►│ METADATA N4 │         │
│  │ PEDAGÓGICAS │    │ GENERACIÓN  │    │  REGISTRO   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│         │                  │                  │                 │
│         ▼                  ▼                  ▼                 │
│  • Anti-Solución    • Ollama/Phi-3    • TutorIntervention-    │
│  • Modo Socrático   • Templates        Metadata                │
│  • Explicitación      fallback       • Effectiveness          │
│  • Refuerzo                            tracking                │
│    Conceptual                                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Integración con AIGateway**:

```python
# ai_gateway.py:468-548
async def _process_tutor_mode(self, session_id, prompt, strategy, classification):
    response_type = strategy.get("response_type")

    if response_type == "socratic_questioning":
        message = await self._generate_socratic_response(prompt, strategy, session_id)
    elif response_type == "conceptual_explanation":
        message = await self._generate_conceptual_explanation(prompt, strategy, session_id)
    elif response_type == "guided_hints":
        message = await self._generate_guided_hints(prompt, strategy, session_id)

    return {
        "response": message,
        "strategy": strategy,
        "mode": "tutor",
        "metadata": {...}
    }
```

### 3.6 FASE 9: AR-IA - Análisis de Riesgos

**Archivo**: `backend/agents/risk_analyst.py`
**Método llamado**: `_analyze_risks_async()` en AIGateway

El análisis detecta **5 dimensiones de riesgo**:

```
┌─────────────────────────────────────────────────────────────────┐
│                   AR-IA: 5 DIMENSIONES DE RIESGO                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. RIESGOS COGNITIVOS (RC)                              │   │
│  │    • RC1: Delegación total                              │   │
│  │    • RC2: Dependencia excesiva de IA (>0.7)            │   │
│  │    • RC3: Falta de justificación                        │   │
│  │    • RC4: Razonamiento superficial                      │   │
│  │    • RC5: Sin autorregulación                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 2. RIESGOS ÉTICOS (RE)                                  │   │
│  │    • RE1: Integridad académica (código sospechoso)     │   │
│  │    • RE2: Uso no divulgado de IA                        │   │
│  │    • RE3: Plagio                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 3. RIESGOS EPISTÉMICOS (REp)                            │   │
│  │    • REp1: Aceptación acrítica de IA                   │   │
│  │    • REp2: Errores conceptuales                         │   │
│  │    • REp3: Falacias lógicas                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4. RIESGOS TÉCNICOS (RT)                                │   │
│  │    • RT1: Vulnerabilidades de seguridad                │   │
│  │    • RT2: Mala calidad de código (DRY)                 │   │
│  │    • RT3: Fallos arquitectónicos                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 5. RIESGOS DE GOBERNANZA (RG)                           │   │
│  │    • RG1: Sesión excesivamente larga (>4h)             │   │
│  │    • RG2: Uso automatizado sospechoso                   │   │
│  │    • RG3: Violación de políticas                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Flujo de Análisis en AIGateway**:

```python
# ai_gateway.py:1045-1226
def _analyze_risks_async(self, session_id, input_trace, response_trace, classification):

    # RC1: Delegación Total
    if classification.get("is_total_delegation"):
        risk = self._create_risk(
            risk_type=RiskType.COGNITIVE_DELEGATION,
            risk_level=RiskLevel.HIGH,
            dimension=RiskDimension.COGNITIVE,
            description="Intento de delegación total detectado",
            ...
        )
        self._persist_risk_object(risk)

    # RC2: Dependencia Excesiva de IA
    if input_trace.ai_involvement > 0.6:  # Umbral configurable
        risk = self._create_risk(
            risk_type=RiskType.AI_DEPENDENCY,
            risk_level=RiskLevel.MEDIUM,
            ...
        )
        self._persist_risk_object(risk)

    # RC3: Falta de Justificación
    if not has_justification and not is_question:
        risk = self._create_risk(
            risk_type=RiskType.LACK_JUSTIFICATION,
            risk_level=RiskLevel.LOW,
            ...
        )
        self._persist_risk_object(risk)

    # REp1: Aceptación Acrítica
    if len(alternatives_considered) == 0 and ai_involvement > 0.5:
        risk = self._create_risk(
            risk_type=RiskType.UNCRITICAL_ACCEPTANCE,
            risk_level=RiskLevel.MEDIUM,
            dimension=RiskDimension.EPISTEMIC,
            ...
        )
        self._persist_risk_object(risk)
```

---

## 4. Escenarios de Interacción

### 4.1 Escenario A: Estudiante pide código completo (Delegación Total)

```
Estudiante: "Dame el código completo para implementar un árbol binario"
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. GOV-IA.sanitize_prompt()                                     │
│    → No PII detectado                                           │
│    → prompt = original                                          │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. CRPE.classify_prompt()                                       │
│    → is_total_delegation = TRUE ⚠️                              │
│    → cognitive_state = IMPLEMENTACION                           │
│    → suggested_response_type = "socratic_questioning"           │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. CRPE.should_block_response()                                 │
│    → should_block = TRUE                                        │
│    → reason = "Delegación total detectada"                      │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. AIGateway._generate_blocked_response()                       │
│                                                                 │
│    RESPUESTA AL ESTUDIANTE:                                     │
│    ──────────────────────────────                               │
│    He detectado que tu solicitud implica una delegación total   │
│    del problema a la IA.                                        │
│                                                                 │
│    Para poder ayudarte efectivamente, necesito que:             │
│    1. Expliques tu comprensión del problema                     │
│    2. Descompongas el problema en partes                        │
│    3. Compartas tu plan inicial                                 │
│    4. Identifiques tus dudas específicas                        │
│                                                                 │
│    ¿Podés reformular tu consulta siguiendo estas pautas?        │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. AR-IA: Registrar riesgo                                      │
│    → risk_type = COGNITIVE_DELEGATION                           │
│    → risk_level = HIGH                                          │
│    → dimension = COGNITIVE                                      │
│    → detected_by = "GOV-IA"                                     │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. TC-N4: Registrar trazas                                      │
│    → input_trace (N4): prompt original + classification         │
│    → intervention_trace (N4): respuesta de bloqueo              │
│    → risk asociado a trace_ids                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Escenario B: Estudiante hace pregunta exploratoria válida

```
Estudiante: "Estoy intentando implementar una cola. Pensé en usar una lista,
             pero no estoy seguro de cómo manejar la operación dequeue
             de forma eficiente. ¿Qué consideraciones debería tener?"
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. GOV-IA.sanitize_prompt()                                     │
│    → No PII detectado                                           │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. CRPE.classify_prompt()                                       │
│    → is_total_delegation = FALSE ✓                              │
│    → is_question = TRUE                                         │
│    → requests_explanation = FALSE                               │
│    → cognitive_state = PLANIFICACION                            │
│    → suggested_response_type = "guided_hints"                   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. CRPE.should_block_response()                                 │
│    → should_block = FALSE ✓                                     │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. TC-N4: Registrar traza de entrada                            │
│    → trace_level = N4_COGNITIVO                                 │
│    → cognitive_intent = "PLANIFICACION"                         │
│    → context = {classification, student demuestra razonamiento} │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. CRPE.generate_pedagogical_response_strategy()                │
│    → response_type = "guided_hints"                             │
│    → instructions = [                                           │
│         "Proporcionar pistas graduadas",                        │
│         "Sugerir dirección sin revelar solución",               │
│         "Ofrecer pseudocódigo de alto nivel",                   │
│         "Pedir que justifique sus próximos pasos"               │
│       ]                                                         │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. T-IA-Cog: Pipeline interno del tutor                         │
│                                                                 │
│    IPC: intent=EXPLORACION, autonomy=0.7 (alto)                 │
│    GSR: semaforo=🟢 VERDE, restrictions=[]                      │
│    Andamiaje: help_level="bajo", intervention=PISTA_GRADUADA    │
│    Reglas: Modo Socrático activo                                │
│    LLM: Generar pistas graduadas                                │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. RESPUESTA AL ESTUDIANTE (via LLM Ollama/Phi-3):              │
│                                                                 │
│    ## Análisis del Problema                                     │
│                                                                 │
│    Excelente que ya identificaste la operación crítica.         │
│    Antes de decidir la estructura:                              │
│                                                                 │
│    **Pista 1**: ¿Qué complejidad temporal tiene eliminar el     │
│    primer elemento de una lista estándar en Python?             │
│                                                                 │
│    **Pista 2**: Pensá en estructuras que permitan acceso        │
│    O(1) a ambos extremos.                                       │
│                                                                 │
│    **Pista 3**: ¿Conocés el módulo `collections` de Python?     │
│                                                                 │
│    **Próximo paso**: Describí en pseudocódigo cómo manejarías   │
│    enqueue y dequeue antes de implementar.                      │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. TC-N4: Registrar traza de respuesta                          │
│    → agent_id = "TUTOR"                                         │
│    → context = {strategy, response_type="guided_hints"}         │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 9. AR-IA._analyze_risks_async()                                 │
│    → Analizar trazas input + response                           │
│    → Detectar posibles riesgos                                  │
│    → Resultado: No hay riesgos críticos (estudiante muestra     │
│      razonamiento propio y hace pregunta específica)            │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Escenario C: Estudiante con Alta Dependencia de IA

```
Estudiante: "¿Por qué mi código no funciona?"
[Contexto: ai_involvement histórico = 0.8, sin justificaciones previas]
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. CRPE.classify_prompt()                                       │
│    → cognitive_state = DEPURACION                               │
│    → is_question = TRUE                                         │
│    → suggested_response_type = "guided_hints"                   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. T-IA-Cog: Pipeline con perfil del estudiante                 │
│                                                                 │
│    IPC: intent=DEPURACION                                       │
│    GSR: semaforo=🟡 AMARILLO ⚠️                                 │
│         (avg_ai_dependency > 0.7)                               │
│         restrictions=["reduce_help_level", "increase_questions"]│
│                                                                 │
│    Estrategia modificada:                                       │
│    → response_type = "socratic_questioning" (en vez de hints)   │
│    → help_level = "bajo"                                        │
│    → require_justification = TRUE                               │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ RESPUESTA AL ESTUDIANTE:                                        │
│                                                                 │
│ ⚠️ **Nota**: Tus métricas muestran alta dependencia de IA.     │
│ Voy a pedirte más trabajo autónomo para desarrollar tus         │
│ habilidades.                                                    │
│                                                                 │
│ ## Antes de ayudarte con el debug:                              │
│                                                                 │
│ 1. ¿Qué error exacto estás viendo?                              │
│ 2. ¿Qué línea(s) crees que causan el problema?                  │
│ 3. ¿Qué esperabas que hiciera tu código vs qué hace?            │
│ 4. ¿Qué intentaste para solucionarlo?                           │
│                                                                 │
│ Respondé estas preguntas y después puedo orientarte.            │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ AR-IA: Registrar riesgo                                         │
│    → risk_type = AI_DEPENDENCY                                  │
│    → risk_level = MEDIUM                                        │
│    → recommendations = [                                        │
│        "Fomentar resolución autónoma",                          │
│        "Asignar ejercicios sin acceso a IA"                     │
│      ]                                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Matriz de Responsabilidades (RACI)

| Actividad | AIGateway | GOV-IA | CRPE | T-IA-Cog | AR-IA | TC-N4 |
|-----------|:---------:|:------:|:----:|:--------:|:-----:|:-----:|
| Recibir prompt | **R** | - | - | - | - | - |
| Filtrar PII | A | **R** | - | - | - | - |
| Clasificar prompt | A | - | **R** | - | - | - |
| Decidir bloqueo | A | C | **R** | - | - | - |
| Generar estrategia | A | - | **R** | C | - | - |
| Procesar con tutor | A | - | C | **R** | - | - |
| Aplicar reglas pedagógicas | I | - | - | **R** | - | - |
| Generar respuesta LLM | A | - | - | **R** | - | - |
| Registrar trazas N4 | A | - | - | I | I | **R** |
| Analizar riesgos | A | I | - | - | **R** | C |
| Persistir riesgos | A | - | - | - | **R** | - |
| Verificar políticas | I | **R** | - | - | C | - |

**Leyenda**: R=Responsable, A=Accountable, C=Consultado, I=Informado

---

## 6. Datos Compartidos entre Agentes

### 6.1 Flujo de Datos

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        FLUJO DE DATOS ENTRE AGENTES                      │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────┐                                                             │
│  │ prompt  │ ─────────────────────────────────────────────────────────►  │
│  └─────────┘                                                             │
│       │                                                                  │
│       ▼                                                                  │
│  ┌─────────────────┐                                                     │
│  │    GOV-IA       │                                                     │
│  │ sanitize_prompt │                                                     │
│  └────────┬────────┘                                                     │
│           │                                                              │
│           ▼                                                              │
│  ┌──────────────────┐    ┌──────────────────┐                           │
│  │ sanitized_prompt │───►│     CRPE         │                           │
│  │ pii_detected     │    │ classify_prompt  │                           │
│  └──────────────────┘    └────────┬─────────┘                           │
│                                   │                                      │
│                                   ▼                                      │
│                          ┌────────────────┐                              │
│                          │ classification │                              │
│                          │ • is_delegation│                              │
│                          │ • cognitive_st │                              │
│                          │ • response_type│                              │
│                          └───────┬────────┘                              │
│                                  │                                       │
│         ┌────────────────────────┼────────────────────────┐              │
│         │                        │                        │              │
│         ▼                        ▼                        ▼              │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────┐        │
│  │   TC-N4     │         │  T-IA-Cog   │         │   AR-IA     │        │
│  │ input_trace │         │   process   │         │ analyze_risk│        │
│  └──────┬──────┘         └──────┬──────┘         └──────┬──────┘        │
│         │                       │                       │                │
│         │                       ▼                       │                │
│         │               ┌─────────────┐                 │                │
│         │               │  response   │                 │                │
│         │               │  strategy   │                 │                │
│         │               │  metadata   │                 │                │
│         │               └──────┬──────┘                 │                │
│         │                      │                        │                │
│         ▼                      ▼                        ▼                │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │                    PostgreSQL (via Repositories)            │        │
│  │                                                             │        │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │        │
│  │  │  sessions   │  │   traces    │  │    risks    │         │        │
│  │  └─────────────┘  └─────────────┘  └─────────────┘         │        │
│  │                                                             │        │
│  └─────────────────────────────────────────────────────────────┘        │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Estructuras de Datos Compartidas

**Classification (CRPE → todos)**:
```python
{
    "is_total_delegation": bool,
    "is_question": bool,
    "requests_explanation": bool,
    "cognitive_state": CognitiveState,
    "requires_intervention": bool,
    "suggested_response_type": str,
    "delegation_signals": List[str]  # Señales detectadas
}
```

**Strategy (CRPE → T-IA-Cog)**:
```python
{
    "response_type": str,
    "cognitive_state": CognitiveState,
    "max_help_level": float,  # 0-1
    "instructions": List[str],
    "constraints": List[str],
    "expected_elements": List[str],
    "student_context": Dict  # Análisis de historial
}
```

**CognitiveTrace (TC-N4 → AR-IA)**:
```python
CognitiveTrace(
    id: str,
    session_id: str,
    student_id: str,
    activity_id: str,
    trace_level: TraceLevel,  # N1-N4
    interaction_type: InteractionType,
    content: str,
    cognitive_intent: str,
    decision_justification: str,
    alternatives_considered: List[str],
    ai_involvement: float,  # 0-1
    context: Dict,
    # 6 dimensiones N4
    semantic_understanding: Dict,
    algorithmic_evolution: Dict,
    cognitive_reasoning: Dict,
    interactional_data: Dict,
    ethical_risk_data: Dict,
    process_data: Dict
)
```

**Risk (AR-IA → BD)**:
```python
Risk(
    id: str,
    session_id: str,
    student_id: str,
    activity_id: str,
    risk_type: RiskType,
    risk_level: RiskLevel,
    dimension: RiskDimension,
    description: str,
    evidence: List[str],
    trace_ids: List[str],  # Trazas relacionadas
    root_cause: str,
    recommendations: List[str],
    pedagogical_intervention: str,
    resolved: bool
)
```

---

## 7. Resumen: Rol del Tutor en el Ecosistema

### 7.1 El Tutor como Agente Central

El **T-IA-Cog** es el agente más complejo del ecosistema porque:

1. **Interactúa directamente con el estudiante** - Es la "cara visible" del sistema
2. **Implementa pedagogía socrática** - No solo responde, guía el razonamiento
3. **Tiene su propio pipeline interno** - IPC → GSR → Andamiaje → Reglas → LLM
4. **Aplica reglas inquebrantables** - Anti-Solución, Modo Socrático, etc.
5. **Genera metadata rica para N4** - Todo queda trazado para análisis

### 7.2 Dependencias del Tutor

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPENDENCIAS DEL TUTOR                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ENTRADA:                                                       │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │ AIGateway   │────►│ classification │────►│ strategy    │       │
│  │ (prompt)    │     │ (de CRPE)   │     │ (de CRPE)   │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                 │
│  CONSULTAS:                                                     │
│  ┌─────────────┐     ┌─────────────┐                           │
│  │ StudentProfile │   │ TraceRepository │                       │
│  │ (avg_ai_dep) │     │ (historial) │                          │
│  └─────────────┘     └─────────────┘                           │
│                                                                 │
│  SALIDA:                                                        │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │ response    │────►│ TC-N4       │────►│ AR-IA       │       │
│  │ (al alumno) │     │ (trazas)    │     │ (riesgos)   │       │
│  └─────────────┘     └─────────────┘     └─────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 Conclusión

El ecosistema AI-Native funciona como un **sistema multi-agente coordinado** donde:

- **AIGateway** orquesta todo el flujo sin mantener estado
- **GOV-IA** asegura cumplimiento de políticas y filtra PII
- **CRPE** clasifica y genera estrategias pedagógicas
- **T-IA-Cog** procesa la interacción con pedagogía socrática
- **AR-IA** detecta y registra riesgos cognitivos/éticos
- **TC-N4** captura todo para reconstrucción del proceso cognitivo

Cada agente tiene responsabilidades claras y se comunican a través de estructuras de datos bien definidas, con todo persistido en PostgreSQL para escalabilidad y trazabilidad completa.

---

**Documento generado para análisis y documentación del sistema AI-Native MVP**
**Relacionado con**: `explicatuto1.md` (Documentación detallada del Tutor)