# S-IA-X: Simuladores Profesionales IA

## Documentación Técnica Completa

---

## 1. Introducción y Propósito

### 1.1 ¿Qué es S-IA-X?

El **S-IA-X** (Simulador IA - X, donde X representa el rol profesional) es el **Submodelo 3** del ecosistema AI-Native. Su propósito fundamental es:

> **Recrear roles profesionales auténticos de la industria del software para que los estudiantes desarrollen competencias transversales en entornos situados de práctica.**

A diferencia de la enseñanza teórica tradicional, S-IA-X pone al estudiante en situaciones reales donde debe:
- Comunicar ideas técnicas a stakeholders no técnicos
- Defender decisiones arquitectónicas
- Manejar presión y urgencia
- Negociar requisitos ambiguos
- Responder a incidentes de producción

### 1.2 Filosofía Pedagógica

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    APRENDIZAJE SITUADO Y AUTÉNTICO                            ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║   "Aprender haciendo" en contextos que simulan el mundo profesional real      ║
║                                                                               ║
║   Ventajas:                                                                   ║
║   • Desarrolla competencias transversales (soft skills)                       ║
║   • Entrena la interacción humano-IA contextualizada                         ║
║   • Prepara para el mundo laboral real                                        ║
║   • Genera evidencia para evaluación formativa                                ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

### 1.3 Los 11 Simuladores Disponibles

#### Versión 1 (V1) - 6 Simuladores Originales

| Código | Nombre | Rol Simulado |
|--------|--------|--------------|
| **PO-IA** | Product Owner | Prioriza backlog, cuestiona valor de negocio |
| **SM-IA** | Scrum Master | Facilita dailies, gestiona impedimentos |
| **IT-IA** | Tech Interviewer | Evalúa conocimientos técnicos |
| **IR-IA** | Incident Responder | Gestiona incidentes de producción |
| **CX-IA** | Client | Cliente con requisitos ambiguos |
| **DSO-IA** | DevSecOps | Audita seguridad, detecta vulnerabilidades |

#### Versión 2 (V2) - 5 Simuladores Enhanced (Sprint 6)

| Código | Nombre | Rol Simulado |
|--------|--------|--------------|
| **SD-IA** | Senior Developer | Code review, mentoría técnica |
| **QA-IA** | QA Engineer | Testing, calidad de código |
| **SA-IA** | Security Auditor | Auditoría de seguridad avanzada |
| **TL-IA** | Tech Lead | Decisiones arquitectónicas |
| **DC-IA** | Demanding Client | Cliente exigente (versión difícil) |

---

## 2. Arquitectura del Agente

### 2.1 Archivo Principal

```
backend/agents/simulators.py
```

### 2.2 Clase `SimuladorProfesionalAgent`

```python
class SimuladorProfesionalAgent:
    """
    S-IA-X: Simuladores Profesionales

    Funciones:
    1. Crear condiciones situadas de práctica profesional
    2. Desarrollar competencias transversales
    3. Entrenar interacción humano-IA contextualizada
    4. Modelar decisiones profesionales con trazabilidad
    5. Generar evidencia para evaluación formativa
    """

    def __init__(
        self,
        simulator_type: SimuladorType,    # Tipo de simulador
        llm_provider=None,                 # Proveedor LLM (Ollama/Phi-3)
        trace_repo=None,                   # Repositorio para memoria de conversación
        config: Optional[Dict[str, Any]] = None
    ):
        self.simulator_type = simulator_type
        self.llm_provider = llm_provider
        self.trace_repo = trace_repo
        self.config = config or {}
        self.context = {}
```

### 2.3 Enum `SimuladorType`

```python
class SimuladorType(str, Enum):
    """Tipos de simuladores profesionales"""

    # V1 - Original simulators
    PRODUCT_OWNER = "product_owner"       # PO-IA
    SCRUM_MASTER = "scrum_master"         # SM-IA
    TECH_INTERVIEWER = "tech_interviewer" # IT-IA
    INCIDENT_RESPONDER = "incident_responder"  # IR-IA
    CLIENT = "client"                     # CX-IA
    DEVSECOPS = "devsecops"              # DSO-IA

    # V2 - Enhanced simulators (Sprint 6)
    SENIOR_DEV = "senior_dev"            # SD-IA
    QA_ENGINEER = "qa_engineer"          # QA-IA
    SECURITY_AUDITOR = "security_auditor"  # SA-IA
    TECH_LEAD = "tech_lead"              # TL-IA
    DEMANDING_CLIENT = "demanding_client"  # DC-IA
```

---

## 3. Flujo de Interacción Principal

### 3.1 Método `interact()`

```python
async def interact(
    self,
    student_input: str,
    context: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
```

### 3.2 Pipeline de Procesamiento

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     PIPELINE DE INTERACCIÓN S-IA-X                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   ENTRADA: student_input, context, session_id                                  │
│                                                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 1: Determinar Tipo de Simulador                                     │  │
│   │ switch(self.simulator_type)                                              │  │
│   │   PRODUCT_OWNER → _interact_as_product_owner()                          │  │
│   │   SCRUM_MASTER → _interact_as_scrum_master()                            │  │
│   │   TECH_INTERVIEWER → _interact_as_interviewer()                         │  │
│   │   INCIDENT_RESPONDER → _interact_as_incident_responder()                │  │
│   │   CLIENT → _interact_as_client()                                         │  │
│   │   DEVSECOPS → _interact_as_devsecops()                                  │  │
│   └─────────────────────────────────────────────────────────────────────────┘  │
│                               │                                                 │
│                               ▼                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 2: Verificar LLM Provider                                           │  │
│   │ if self.llm_provider:                                                    │  │
│   │   → Usar respuestas dinámicas con Ollama/Phi-3                          │  │
│   │ else:                                                                    │  │
│   │   → Usar respuestas predefinidas (fallback)                             │  │
│   └─────────────────────────────────────────────────────────────────────────┘  │
│                               │                                                 │
│                               ▼                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 3: Cargar Historial de Conversación (si hay session_id)            │  │
│   │ _load_conversation_history(session_id)                                   │  │
│   │   → Recupera trazas previas de la sesión                                │  │
│   │   → Convierte a formato LLMMessage (USER/ASSISTANT)                     │  │
│   │   → Mantiene contexto completo de la conversación                       │  │
│   └─────────────────────────────────────────────────────────────────────────┘  │
│                               │                                                 │
│                               ▼                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 4: Construir Prompt con System Prompt del Rol                       │  │
│   │ messages = [                                                             │  │
│   │   LLMMessage(SYSTEM, "Eres un {rol} experimentado...")                  │  │
│   │   ...conversation_history...                                             │  │
│   │   LLMMessage(USER, student_input)                                        │  │
│   │ ]                                                                        │  │
│   └─────────────────────────────────────────────────────────────────────────┘  │
│                               │                                                 │
│                               ▼                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 5: Generar Respuesta con LLM                                        │  │
│   │ response = await llm_provider.generate(                                  │  │
│   │   messages=messages,                                                     │  │
│   │   temperature=0.7,  # Creatividad moderada                               │  │
│   │   max_tokens=500                                                         │  │
│   │ )                                                                        │  │
│   └─────────────────────────────────────────────────────────────────────────┘  │
│                               │                                                 │
│                               ▼                                                 │
│   ┌─────────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 6: Analizar Competencias del Estudiante                             │  │
│   │ _analyze_competencies(student_input, response, competencies)             │  │
│   │   → Evalúa comunicación, claridad, profundidad técnica                   │  │
│   │   → Genera scores 0.0-1.0 por competencia                                │  │
│   └─────────────────────────────────────────────────────────────────────────┘  │
│                               │                                                 │
│                               ▼                                                 │
│   SALIDA: {                                                                    │
│     "message": "Respuesta del simulador...",                                   │
│     "role": "product_owner",                                                   │
│     "expects": ["criterios_aceptacion", "justificacion_tecnica"],             │
│     "metadata": {                                                              │
│       "competencies_evaluated": ["comunicacion", "priorizacion"],             │
│       "competency_scores": {"comunicacion": 0.7, "priorizacion": 0.8}         │
│     }                                                                          │
│   }                                                                            │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Descripción de Cada Simulador

### 4.1 PO-IA: Product Owner

**Archivo**: `simulators.py:97-141`

**Rol**: Cuestionar propuestas técnicas, pedir criterios de aceptación claros, evaluar valor para el usuario final, priorizar backlog por ROI.

**System Prompt**:
```
Eres un Product Owner experimentado de una empresa de software.
Tu rol es cuestionar propuestas técnicas, pedir criterios de aceptación claros,
evaluar el valor para el usuario final, y priorizar el backlog por ROI.
Debes ser exigente pero constructivo. Pide justificaciones técnicas sólidas.
```

**Competencias Evaluadas**:
- `comunicacion_tecnica`
- `analisis_requisitos`
- `priorizacion`
- `justificacion_decisiones`

**Qué Espera del Estudiante**:
- Criterios de aceptación claros
- Justificación técnica sólida
- Análisis de alternativas

**Ejemplo de Respuesta**:
```
Como Product Owner, necesito que me aclares algunos puntos:

1. ¿Cuáles son los criterios de aceptación específicos para esta funcionalidad?
2. ¿Cómo pensás que esto agrega valor al usuario final?
3. ¿Qué alternativas consideraste y por qué elegiste este enfoque?
4. ¿Cuál es el impacto si postergamos esta funcionalidad un sprint?

Necesito justificaciones técnicas sólidas para priorizar esto en el backlog.
```

---

### 4.2 SM-IA: Scrum Master

**Archivo**: `simulators.py:143-186`

**Rol**: Facilitar daily standups, identificar impedimentos, ayudar al equipo a auto-organizarse, mejorar procesos ágiles.

**System Prompt**:
```
Eres un Scrum Master certificado facilitando ceremonias ágiles.
Tu rol es hacer daily standups, identificar impedimentos, ayudar al equipo a
auto-organizarse, y mejorar procesos. Debes ser empático pero directo cuando
hay problemas de estimación o bloqueos.
```

**Competencias Evaluadas**:
- `gestion_tiempo`
- `comunicacion`
- `identificacion_impedimentos`
- `auto_organizacion`

**Qué Espera del Estudiante**:
- Status update claro
- Identificación de impedimentos
- Plan de acción

**Ejemplo de Respuesta**:
```
En nuestro daily:

1. ¿Qué lograste ayer?
2. ¿Qué vas a hacer hoy?
3. ¿Hay algún impedimento que te esté bloqueando?

Noto que tu estimación original era de 3 puntos y llevás 5 días. ¿Qué está
pasando? ¿Necesitamos re-estimar o hay deuda técnica no considerada?
```

---

### 4.3 IT-IA: Tech Interviewer

**Archivo**: `simulators.py:188-231`

**Rol**: Hacer preguntas conceptuales sobre algoritmos y estructuras de datos, pedir análisis de complejidad, evaluar razonamiento en voz alta.

**System Prompt**:
```
Eres un entrevistador técnico senior evaluando candidatos.
Tu rol es hacer preguntas conceptuales sobre algoritmos y estructuras de datos,
pedir análisis de complejidad, y evaluar razonamiento en voz alta.
Debes hacer follow-up questions para profundizar.
```

**Competencias Evaluadas**:
- `dominio_conceptual`
- `analisis_algoritmico`
- `comunicacion_tecnica`
- `razonamiento_en_voz_alta`

**Qué Espera del Estudiante**:
- Explicación conceptual clara
- Ejemplos concretos
- Análisis de complejidad

**Métodos Especializados (Sprint 6)**:

```python
# Generar pregunta de entrevista
await generar_pregunta_entrevista(
    tipo_entrevista="CONCEPTUAL",  # CONCEPTUAL, ALGORITHMIC, DESIGN, BEHAVIORAL
    dificultad="MEDIUM",           # EASY, MEDIUM, HARD
    contexto="..."
) -> str

# Evaluar respuesta del estudiante
await evaluar_respuesta_entrevista(
    pregunta="...",
    respuesta="...",
    tipo_entrevista="ALGORITHMIC"
) -> {
    "clarity_score": 0.8,
    "technical_accuracy": 0.7,
    "thinking_aloud": True,
    "key_points_covered": ["punto1", "punto2"],
    "feedback": "..."
}

# Generar evaluación final de entrevista
await generar_evaluacion_entrevista(
    preguntas=[...],
    respuestas=[...],
    tipo_entrevista="CONCEPTUAL"
) -> {
    "overall_score": 0.75,
    "breakdown": {"clarity": 0.8, "technical_accuracy": 0.7, "communication": 0.75},
    "feedback": "Buen desempeño en la entrevista..."
}
```

---

### 4.4 IR-IA: Incident Responder

**Archivo**: `simulators.py:281-343`

**Rol**: Gestionar incidentes de producción bajo presión, hacer triage, diagnosticar problemas, priorizar acciones, coordinar hotfixes, documentar post-mortem.

**System Prompt**:
```
Eres un ingeniero DevOps senior gestionando un incidente en producción.
Tu rol es hacer triage, diagnosticar el problema, priorizar acciones bajo presión,
coordinar hotfixes, y documentar post-mortem.
Debes ser sistemático, priorizar por impacto, y requerir evidencia (logs, métricas).
```

**Competencias Evaluadas**:
- `diagnostico_sistematico`
- `priorizacion`
- `documentacion`
- `manejo_presion`

**Qué Espera del Estudiante**:
- Diagnóstico inicial
- Plan de acción inmediato
- Hotfix propuesto
- Documentación post-mortem

**Métodos Especializados (Sprint 6)**:

```python
# Generar escenario de incidente
await generar_incidente(
    tipo_incidente="API_ERROR",  # API_ERROR, PERFORMANCE, SECURITY, DATABASE, DEPLOYMENT
    severidad="HIGH"             # LOW, MEDIUM, HIGH, CRITICAL
) -> {
    "description": "🚨 API endpoint /users devuelve HTTP 500...",
    "logs": "[2025-11-21 14:32:15] ERROR - NullPointerException...",
    "metrics": {
        "cpu_usage_percent": 45,
        "memory_usage_percent": 78,
        "requests_per_second": 1200,
        "error_rate_percent": 85,
        "response_time_ms": 8500
    }
}

# Evaluar resolución del incidente
await evaluar_resolucion_incidente(
    proceso_diagnostico=[...],
    solucion="...",
    causa_raiz="...",
    post_mortem="..."
) -> {
    "overall_score": 0.72,
    "diagnosis_systematic": 0.8,
    "prioritization": 0.7,
    "documentation_quality": 0.65,
    "communication_clarity": 0.75,
    "feedback": "..."
}
```

**Ejemplo de Incidente Generado**:
```
🚨 INCIDENTE CRÍTICO EN PRODUCCIÓN 🚨

**Severidad**: P1 (crítico)
**Impacto**: El servidor de API está caído. 5000 usuarios afectados.
**Tiempo de inactividad**: 12 minutos

**Síntomas**:
- HTTP 503 Service Unavailable
- Logs muestran: "OutOfMemoryError: Java heap space"
- CPU al 100% en todos los nodos
- Base de datos respondiendo normalmente

**Tu turno**:
1. ¿Cuál es tu hipótesis inicial?
2. ¿Qué comandos ejecutarías para diagnosticar?
3. ¿Cuál es tu plan de acción inmediato?
4. ¿Cómo prevenimos que vuelva a ocurrir?

Necesito respuestas en <5 minutos. El CEO está preguntando cuándo volvemos online.
```

---

### 4.5 CX-IA: Client

**Archivo**: `simulators.py:345-400`

**Rol**: Cliente no técnico con requisitos ambiguos, a veces contradictorios, que cambia de opinión. Valora explicaciones simples y justificaciones de negocio.

**System Prompt**:
```
Eres un cliente no técnico con una idea de negocio.
Tus requisitos son ambiguos, a veces contradictorios, y cambias de opinión.
El estudiante debe hacer elicitación efectiva, negociar prioridades,
y gestionar expectativas. No entiendes jerga técnica.
```

**Competencias Evaluadas**:
- `elicitacion_requisitos`
- `negociacion`
- `empatia`
- `gestion_expectativas`

**Qué Espera del Estudiante**:
- Clarificación de requisitos
- Propuesta de alternativas
- Justificación de negocio

**Ejemplo de Respuesta**:
```
Hola, necesito una app "como Uber pero para delivery de comida".

Quiero que:
- Los usuarios puedan pedir comida
- Los restaurantes reciban los pedidos
- Los repartidores... no sé, algo con GPS
- Pagos con tarjeta, pero también efectivo
- Notificaciones cuando llegue el pedido

Ah, y tiene que estar lista en 2 semanas porque mi cuñado dijo que puede
conseguir inversores.

¿Cuánto sale? ¿Podés empezar ya?
```

---

### 4.6 DSO-IA: DevSecOps

**Archivo**: `simulators.py:233-279`

**Rol**: Auditar código, detectar vulnerabilidades (SQL injection, XSS, CSRF, etc.), analizar dependencias obsoletas, exigir planes de remediación con timeline.

**System Prompt**:
```
Eres un analista de seguridad DevSecOps experimentado.
Tu rol es auditar código, detectar vulnerabilidades (SQL injection, XSS, CSRF, etc.),
analizar dependencias obsoletas, y exigir planes de remediación con timeline.
Debes ser directo, enfocarte en riesgos críticos, y pedir evidencia de mitigación.
```

**Competencias Evaluadas**:
- `seguridad`
- `analisis_vulnerabilidades`
- `gestion_riesgo`
- `cumplimiento`

**Qué Espera del Estudiante**:
- Plan de remediación
- Análisis de riesgo
- Estrategia de testing

**Método de Auditoría**:
```python
auditar_seguridad(codigo: str, lenguaje: str) -> {
    "audit_id": "uuid",
    "total_vulnerabilities": 3,
    "critical_count": 1,
    "high_count": 2,
    "medium_count": 0,
    "low_count": 0,
    "vulnerabilities": [
        {
            "severity": "CRITICAL",
            "vulnerability_type": "CODE_INJECTION",
            "description": "Uso de eval/exec permite ejecución de código arbitrario",
            "recommendation": "Nunca uses eval/exec con input de usuario"
        },
        {
            "severity": "HIGH",
            "vulnerability_type": "SQL_INJECTION",
            "description": "Posible SQL injection por concatenación de strings",
            "recommendation": "Usa queries parametrizadas"
        }
    ],
    "security_score": 4.0,  # 0-10
    "owasp_compliant": False
}
```

---

## 5. Análisis de Competencias

### 5.1 Método `_analyze_competencies()`

```python
def _analyze_competencies(
    self,
    student_input: str,
    simulator_response: str,
    competencies: List[str]
) -> Dict[str, float]:
```

### 5.2 Heurísticas de Evaluación

| Competencia | Indicadores Positivos | Score Base |
|-------------|----------------------|------------|
| `comunicacion_tecnica` | Longitud > 30 palabras, términos técnicos, estructura | 0.5 + 0.5 max |
| `analisis_algoritmico` | Términos de complejidad, longitud > 50 palabras | 0.5 + 0.5 max |
| `elicitacion_requisitos` | Preguntas (?), longitud > 20 palabras | 0.5 + 0.5 max |
| `gestion_tiempo` | Palabras de priorización (urgente, crítico, primero) | 0.5 + 0.3 max |

### 5.3 Términos Técnicos Detectados

```python
technical_terms = [
    "complejidad", "algoritmo", "estructura", "patrón", "arquitectura",
    "performance", "escalabilidad", "mantenibilidad", "testing", "refactor"
]
```

---

## 6. Memoria de Conversación

### 6.1 Método `_load_conversation_history()`

```python
def _load_conversation_history(self, session_id: str) -> List[LLMMessage]:
    """
    Carga el historial de conversación de esta sesión como mensajes LLM.

    Recupera todas las trazas de la sesión y las convierte al formato
    de mensajes que espera el LLM provider.
    """
```

### 6.2 Flujo de Memoria

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MEMORIA DE CONVERSACIÓN S-IA-X                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   1. Estudiante envía mensaje                                               │
│      └── session_id: "abc123"                                               │
│                                                                             │
│   2. Simulador recupera historial                                           │
│      └── trace_repo.get_by_session("abc123")                               │
│                                                                             │
│   3. Convierte trazas a mensajes LLM                                        │
│      ┌─────────────────────────────────────────────────────────────────┐   │
│      │ STUDENT_PROMPT → LLMMessage(role=USER, content=...)             │   │
│      │ AI_RESPONSE → LLMMessage(role=ASSISTANT, content=...)           │   │
│      │ TUTOR_INTERVENTION → LLMMessage(role=ASSISTANT, content=...)    │   │
│      └─────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   4. Construye mensajes completos                                           │
│      messages = [                                                           │
│        LLMMessage(SYSTEM, "Eres un Product Owner...")                      │
│        LLMMessage(USER, "Hola, quiero implementar X")        # Historial   │
│        LLMMessage(ASSISTANT, "Necesito más detalles...")     # Historial   │
│        LLMMessage(USER, student_input)                        # Actual     │
│      ]                                                                      │
│                                                                             │
│   5. Genera respuesta con contexto completo                                 │
│      └── El LLM "recuerda" la conversación anterior                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Interacción con Otros Agentes

### 7.1 Diagrama de Interacción

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTERACCIÓN S-IA-X CON OTROS AGENTES                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐                                                          │
│   │  AIGateway  │─────────► mode == SIMULATOR                              │
│   │ (Orquestador)│         └── _process_simulator_mode()                   │
│   └─────────────┘                                                          │
│          │                                                                  │
│          │ Inyecta:                                                         │
│          │   • llm_provider (Ollama/Phi-3)                                 │
│          │   • trace_repo (para memoria)                                    │
│          ▼                                                                  │
│   ┌─────────────┐                                                          │
│   │   S-IA-X    │◄─────────── Router /simulators/interact                  │
│   │ (Simulador) │              Crea instancia según simulator_type         │
│   └─────────────┘                                                          │
│          │                                                                  │
│          │ Genera:                                                          │
│          │   • Respuesta del rol profesional                                │
│          │   • Competency scores                                            │
│          ▼                                                                  │
│   ┌─────────────┐                                                          │
│   │   TC-N4     │◄─────────── Captura trazas N4                            │
│   │ Trazabilidad│              • STUDENT_PROMPT (ai_involvement=0.0)       │
│   └─────────────┘              • AI_RESPONSE (ai_involvement=1.0)          │
│          │                                                                  │
│          │                                                                  │
│          ▼                                                                  │
│   ┌─────────────┐                                                          │
│   │   AR-IA     │◄─────────── Analiza riesgos (opcional)                   │
│   │  (Riesgos)  │              • Riesgo ético si usa código de IA          │
│   └─────────────┘              • Riesgo técnico si vulnerabilidades        │
│          │                                                                  │
│          │                                                                  │
│          ▼                                                                  │
│   ┌─────────────┐                                                          │
│   │  E-IA-Proc  │◄─────────── Evaluación de proceso (bajo demanda)         │
│   │ (Evaluador) │              • Usa trazas de simuladores                 │
│   └─────────────┘              • Evalúa competencias transversales         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Integración con AIGateway

El AIGateway detecta el modo SIMULATOR y delega al método correspondiente:

```python
# backend/core/ai_gateway.py:389-399

elif current_mode == AgentMode.SIMULATOR:
    response = self._process_simulator_mode(
        session_id, prompt, strategy, classification
    )

# El método actual es un placeholder:
def _process_simulator_mode(self, session_id, prompt, strategy, classification):
    return {
        "message": "[Modo Simulador - En desarrollo]",
        "mode": "simulator",
        "metadata": {}
    }
```

**Nota**: La integración principal de simuladores se hace vía el router `/simulators`, no directamente por el AIGateway.

---

## 8. Tablas de Base de Datos

### 8.1 Tabla Principal: `simulator_events`

```sql
CREATE TABLE simulator_events (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    simulator_type VARCHAR(50) NOT NULL,  -- product_owner, scrum_master, etc.

    -- Evento
    event_type VARCHAR(100) NOT NULL,     -- backlog_created, sprint_planning_complete, etc.
    event_data JSON DEFAULT '{}',         -- Datos específicos del evento
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Contexto
    description TEXT,
    severity VARCHAR(20),                 -- info, warning, critical

    -- Constraints
    CONSTRAINT ck_simulator_event_type_valid CHECK (
        simulator_type IN ('product_owner', 'scrum_master', 'tech_interviewer',
                           'incident_responder', 'client', 'devsecops')
    )
);

-- Índices compuestos
CREATE INDEX idx_event_session ON simulator_events(session_id, timestamp);
CREATE INDEX idx_event_type_student ON simulator_events(event_type, student_id);
CREATE INDEX idx_event_simulator_session ON simulator_events(simulator_type, session_id);
```

### 8.2 Tabla: `interview_sessions` (IT-IA - Sprint 6)

```sql
CREATE TABLE interview_sessions (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100),

    -- Tipo de entrevista
    interview_type VARCHAR(50) NOT NULL,  -- CONCEPTUAL, ALGORITHMIC, DESIGN, BEHAVIORAL
    difficulty_level VARCHAR(20) DEFAULT 'MEDIUM',  -- EASY, MEDIUM, HARD

    -- Preguntas y respuestas (JSON arrays)
    questions_asked JSON DEFAULT '[]',
    -- [{
    --   "question": "Explain polymorphism",
    --   "type": "conceptual",
    --   "expected_key_points": ["dynamic binding", "inheritance"],
    --   "timestamp": "2025-11-21T10:30:00Z"
    -- }]

    responses JSON DEFAULT '[]',
    -- [{
    --   "question_id": 0,
    --   "response": "Student's answer",
    --   "evaluation": {
    --     "clarity_score": 0.8,
    --     "technical_accuracy": 0.7,
    --     "thinking_aloud": true,
    --     "key_points_covered": ["dynamic binding"]
    --   },
    --   "timestamp": "2025-11-21T10:32:00Z"
    -- }]

    -- Evaluación final
    evaluation_score FLOAT,           -- 0.0 - 1.0
    evaluation_breakdown JSON,        -- {"clarity": 0.8, "accuracy": 0.7, "communication": 0.9}
    feedback TEXT,
    duration_minutes INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interview_student ON interview_sessions(student_id);
CREATE INDEX idx_interview_session ON interview_sessions(session_id);
```

### 8.3 Tabla: `incident_simulations` (IR-IA - Sprint 6)

```sql
CREATE TABLE incident_simulations (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100),

    -- Tipo de incidente
    incident_type VARCHAR(50) NOT NULL,   -- API_ERROR, PERFORMANCE, SECURITY, DATABASE, DEPLOYMENT
    severity VARCHAR(20) DEFAULT 'HIGH',  -- LOW, MEDIUM, HIGH, CRITICAL

    -- Descripción del incidente
    incident_description TEXT NOT NULL,
    simulated_logs TEXT,                  -- Logs simulados
    simulated_metrics JSON DEFAULT '{}',  -- {"cpu": 98, "memory": 95, "error_rate": 12}

    -- Proceso de diagnóstico
    diagnosis_process JSON DEFAULT '[]',
    -- [{
    --   "step": 1,
    --   "action": "Checked application logs",
    --   "finding": "Found NullPointerException in UserService",
    --   "timestamp": "2025-11-21T11:00:00Z"
    -- }]

    -- Solución
    solution_proposed TEXT,
    root_cause_identified TEXT,

    -- Timing
    time_to_diagnose_minutes INTEGER,
    time_to_resolve_minutes INTEGER,

    -- Post-mortem
    post_mortem TEXT,

    -- Evaluación
    evaluation JSON DEFAULT '{}',
    -- {
    --   "overall_score": 0.72,
    --   "diagnosis_systematic": 0.8,
    --   "prioritization": 0.7,
    --   "documentation_quality": 0.65,
    --   "feedback": "..."
    -- }

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_incident_student ON incident_simulations(student_id);
CREATE INDEX idx_incident_session ON incident_simulations(session_id);
```

### 8.4 Relación con `cognitive_traces`

Las interacciones con simuladores también se registran en `cognitive_traces`:

```sql
-- Traza de input del estudiante
INSERT INTO cognitive_traces (
    session_id, student_id, activity_id,
    trace_level, interaction_type,
    content, cognitive_state, cognitive_intent,
    ai_involvement, trace_metadata
) VALUES (
    'session_123', 'student_001', 'prog2_tp1',
    'n4_cognitivo', 'student_prompt',
    'Quiero implementar una cola de prioridad',
    'exploracion', 'Interactuar con simulador product_owner',
    0.0,  -- El estudiante habla
    '{"simulator_type": "product_owner", "context": {}}'
);

-- Traza de respuesta del simulador
INSERT INTO cognitive_traces (
    session_id, student_id, activity_id,
    trace_level, interaction_type,
    content, cognitive_state, cognitive_intent,
    ai_involvement, trace_metadata
) VALUES (
    'session_123', 'student_001', 'prog2_tp1',
    'n4_cognitivo', 'ai_response',
    'Como Product Owner, necesito que me aclares...',
    'reflexion', 'Respuesta de simulador product_owner',
    1.0,  -- El simulador responde
    '{"simulator_type": "product_owner", "role": "product_owner",
      "expects": ["criterios_aceptacion"],
      "competencies_evaluated": ["comunicacion_tecnica"]}'
);
```

---

## 9. Endpoints REST

### 9.1 Router Principal: `/simulators`

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/simulators` | Lista todos los simuladores disponibles |
| GET | `/simulators/{type}` | Info detallada de un simulador |
| POST | `/simulators/interact` | Interactuar con simulador |

### 9.2 Endpoints Especializados (Sprint 6)

#### IT-IA (Entrevistas Técnicas)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/simulators/interview/start` | Iniciar entrevista técnica |
| POST | `/simulators/interview/respond` | Enviar respuesta a pregunta |
| POST | `/simulators/interview/complete` | Finalizar entrevista |
| GET | `/simulators/interview/{id}` | Obtener detalles de entrevista |

#### IR-IA (Incidentes de Producción)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/simulators/incident/start` | Iniciar simulación de incidente |
| POST | `/simulators/incident/diagnose` | Agregar paso de diagnóstico |
| POST | `/simulators/incident/resolve` | Resolver incidente |
| GET | `/simulators/incident/{id}` | Obtener detalles de incidente |

#### SM-IA (Daily Standup)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/simulators/scrum/daily-standup` | Participar en daily standup |

#### CX-IA (Cliente)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/simulators/client/requirements` | Obtener requisitos del cliente |
| POST | `/simulators/client/clarify` | Hacer pregunta de clarificación |

#### DSO-IA (Seguridad)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/simulators/security/audit` | Auditar código (OWASP Top 10) |

### 9.3 Flujo del Endpoint `/simulators/interact`

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO: POST /simulators/interact                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. VALIDAR SESIÓN                                                          │
│      session = session_repo.get_by_id(request.session_id)                   │
│      if not session or session.status != "active":                          │
│          raise HTTPException(404 o 400)                                      │
│                                                                              │
│   2. MAPEAR TIPO DE SIMULADOR                                               │
│      SimulatorType.PRODUCT_OWNER → AgentSimulatorType.PRODUCT_OWNER         │
│                                                                              │
│   3. CREAR INSTANCIA DE SIMULADOR                                           │
│      simulator = SimuladorProfesionalAgent(                                  │
│          simulator_type=agent_simulator_type,                                │
│          llm_provider=llm_provider,   # Inyectado                           │
│          trace_repo=trace_repo,        # Para memoria                        │
│          config={"context": request.context}                                 │
│      )                                                                       │
│                                                                              │
│   4. PROCESAR INTERACCIÓN                                                   │
│      response = await simulator.interact(                                    │
│          student_input=request.prompt,                                       │
│          context=request.context,                                            │
│          session_id=request.session_id   # Para memoria                      │
│      )                                                                       │
│                                                                              │
│   5. CAPTURAR TRAZAS N4                                                     │
│      input_trace = CognitiveTrace(                                           │
│          interaction_type=STUDENT_PROMPT,                                    │
│          ai_involvement=0.0                                                  │
│      )                                                                       │
│      output_trace = CognitiveTrace(                                          │
│          interaction_type=AI_RESPONSE,                                       │
│          ai_involvement=1.0                                                  │
│      )                                                                       │
│      trace_repo.create(input_trace)                                          │
│      trace_repo.create(output_trace)                                         │
│                                                                              │
│   6. RETORNAR RESPUESTA                                                     │
│      return APIResponse(                                                     │
│          success=True,                                                       │
│          data=SimulatorInteractionResponse(...)                              │
│      )                                                                       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 10. Repositorios de Base de Datos

### 10.1 `SimulatorEventRepository`

```python
class SimulatorEventRepository:
    """Repository for simulator events (S-IA-X)"""

    def create(self, session_id, student_id, simulator_type, event_type,
               event_data, description=None, severity=None) -> SimulatorEventDB

    def get_by_id(self, event_id: str) -> Optional[SimulatorEventDB]

    def get_by_session(self, session_id: str, limit: int = 100) -> List[SimulatorEventDB]

    def get_by_student(self, student_id: str, limit: int = 100) -> List[SimulatorEventDB]

    def get_by_simulator_type(self, simulator_type: str, limit: int = 100) -> List[SimulatorEventDB]

    def get_timeline(self, session_id: str) -> Dict[str, Any]
```

### 10.2 `InterviewSessionRepository`

```python
class InterviewSessionRepository:
    """Repository for interview session operations (IT-IA)"""

    def create(self, session_id, student_id, interview_type,
               activity_id=None, difficulty_level="MEDIUM") -> InterviewSessionDB

    def add_question(self, interview_id: str, question: dict) -> Optional[InterviewSessionDB]

    def add_response(self, interview_id: str, response: dict) -> Optional[InterviewSessionDB]

    def complete_interview(self, interview_id, evaluation_score, evaluation_breakdown,
                          feedback, duration_minutes) -> Optional[InterviewSessionDB]

    def get_by_id(self, interview_id: str) -> Optional[InterviewSessionDB]

    def get_by_student(self, student_id: str, limit: int = 20) -> List[InterviewSessionDB]

    def get_by_session(self, session_id: str) -> List[InterviewSessionDB]
```

### 10.3 `IncidentSimulationRepository`

```python
class IncidentSimulationRepository:
    """Repository for incident simulation operations (IR-IA)"""

    def create(self, session_id, student_id, incident_type, incident_description,
               activity_id=None, severity="HIGH", simulated_logs=None,
               simulated_metrics=None) -> IncidentSimulationDB

    def add_diagnosis_step(self, incident_id: str, step: dict) -> Optional[IncidentSimulationDB]

    def complete_incident(self, incident_id, solution_proposed, root_cause_identified,
                         post_mortem, time_to_diagnose_minutes, time_to_resolve_minutes,
                         evaluation) -> Optional[IncidentSimulationDB]

    def get_by_id(self, incident_id: str) -> Optional[IncidentSimulationDB]

    def get_by_student(self, student_id: str, limit: int = 20) -> List[IncidentSimulationDB]

    def get_by_session(self, session_id: str) -> List[IncidentSimulationDB]
```

---

## 11. Schemas de Request/Response

### 11.1 Interacción General

```python
class SimulatorInteractionRequest(BaseModel):
    session_id: str
    simulator_type: SimulatorType  # product_owner, scrum_master, etc.
    prompt: str
    context: Optional[Dict[str, Any]] = None


class SimulatorInteractionResponse(BaseModel):
    interaction_id: str
    simulator_type: SimulatorType
    response: str                           # Mensaje del simulador
    role: str                               # "product_owner", "scrum_master", etc.
    expects: List[str]                      # Qué espera del estudiante
    competencies_evaluated: List[str]       # Competencias evaluadas
    trace_id_input: str
    trace_id_output: str
    metadata: Dict[str, Any] = {}
```

### 11.2 Información de Simulador

```python
class SimulatorInfoResponse(BaseModel):
    type: SimulatorType
    name: str                               # "Product Owner (PO-IA)"
    description: str
    competencies: List[str]                 # Competencias que evalúa
    status: str                             # "active", "development"
    example_questions: Optional[List[str]]  # Preguntas de ejemplo
```

### 11.3 Eventos de Simulador

```python
class SimulatorEventResponse(BaseModel):
    id: str
    session_id: str
    student_id: str
    simulator_type: str
    event_type: str                         # backlog_created, sprint_planning_complete
    event_data: Dict[str, Any]
    description: Optional[str]
    severity: Optional[str]                 # info, warning, critical
    timestamp: datetime
    created_at: datetime
```

---

## 12. Resumen de Métodos Principales

### 12.1 Clase `SimuladorProfesionalAgent`

| Método | Propósito | Input | Output |
|--------|-----------|-------|--------|
| `interact()` | Interacción principal | student_input, context, session_id | Dict con mensaje y metadata |
| `_interact_as_product_owner()` | Simula PO | student_input, context, session_id | Dict |
| `_interact_as_scrum_master()` | Simula SM | student_input, context, session_id | Dict |
| `_interact_as_interviewer()` | Simula entrevistador | student_input, context, session_id | Dict |
| `_interact_as_incident_responder()` | Simula IR | student_input, context, session_id | Dict |
| `_interact_as_client()` | Simula cliente | student_input, context, session_id | Dict |
| `_interact_as_devsecops()` | Simula DSO | student_input, context, session_id | Dict |
| `_generate_llm_response()` | Genera respuesta con LLM | role, system_prompt, ... | Dict |
| `_analyze_competencies()` | Evalúa competencias | student_input, response, competencies | Dict[str, float] |
| `_load_conversation_history()` | Carga historial | session_id | List[LLMMessage] |
| `generar_pregunta_entrevista()` | Genera pregunta IT-IA | tipo, dificultad, contexto | str |
| `evaluar_respuesta_entrevista()` | Evalúa respuesta IT-IA | pregunta, respuesta, tipo | Dict |
| `generar_evaluacion_entrevista()` | Evaluación final IT-IA | preguntas, respuestas, tipo | Dict |
| `generar_incidente()` | Genera escenario IR-IA | tipo, severidad | Dict |
| `evaluar_resolucion_incidente()` | Evalúa resolución IR-IA | proceso, solución, causa, postmortem | Dict |
| `procesar_daily_standup()` | Procesa daily SM-IA | ayer, hoy, impedimentos | Dict |
| `generar_requerimientos_cliente()` | Genera requisitos CX-IA | tipo_proyecto | Dict |
| `responder_clarificacion()` | Responde pregunta CX-IA | pregunta | Dict |
| `auditar_seguridad()` | Audita código DSO-IA | codigo, lenguaje | Dict |

---

## 13. Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              FLUJO COMPLETO S-IA-X                                          │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│   [Estudiante selecciona simulador y escribe mensaje]                                       │
│                │                                                                            │
│                ▼                                                                            │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐    │
│   │                    POST /simulators/interact                                       │    │
│   │    {                                                                               │    │
│   │      "session_id": "abc123",                                                       │    │
│   │      "simulator_type": "product_owner",                                            │    │
│   │      "prompt": "Quiero implementar autenticación con OAuth2"                       │    │
│   │    }                                                                               │    │
│   └───────────────────────────────────────────────────────────────────────────────────┘    │
│                │                                                                            │
│                ▼                                                                            │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐    │
│   │                         VALIDACIÓN                                                 │    │
│   │    • Sesión existe y está activa                                                   │    │
│   │    • Mapear SimulatorType → AgentSimulatorType                                    │    │
│   └───────────────────────────────────────────────────────────────────────────────────┘    │
│                │                                                                            │
│                ▼                                                                            │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐    │
│   │                   SimuladorProfesionalAgent.interact()                             │    │
│   │                                                                                     │    │
│   │    1. Determinar tipo de simulador (switch)                                         │    │
│   │    2. Si hay llm_provider → _generate_llm_response()                               │    │
│   │       Si no → Usar respuesta predefinida (fallback)                                │    │
│   │    3. Cargar historial de conversación (si hay session_id)                         │    │
│   │    4. Construir messages con system prompt del rol                                 │    │
│   │    5. Generar respuesta con LLM (temperature=0.7)                                  │    │
│   │    6. Analizar competencias del estudiante                                          │    │
│   └───────────────────────────────────────────────────────────────────────────────────┘    │
│                │                                                                            │
│                ▼                                                                            │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐    │
│   │                         RESPUESTA DEL SIMULADOR                                    │    │
│   │    {                                                                               │    │
│   │      "message": "Como Product Owner, tengo algunas preguntas:                     │    │
│   │                  1. ¿Cuáles son los criterios de aceptación?                      │    │
│   │                  2. ¿Cómo agrega valor al usuario final?                          │    │
│   │                  3. ¿Qué alternativas consideraste?",                             │    │
│   │      "role": "product_owner",                                                      │    │
│   │      "expects": ["criterios_aceptacion", "justificacion_tecnica"],               │    │
│   │      "metadata": {                                                                 │    │
│   │        "competencies_evaluated": ["comunicacion_tecnica", "priorizacion"],        │    │
│   │        "competency_scores": {"comunicacion_tecnica": 0.7, "priorizacion": 0.6}    │    │
│   │      }                                                                             │    │
│   │    }                                                                               │    │
│   └───────────────────────────────────────────────────────────────────────────────────┘    │
│                │                                                                            │
│                ▼                                                                            │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐    │
│   │                    TRAZABILIDAD N4 (TC-N4)                                         │    │
│   │                                                                                     │    │
│   │    input_trace = CognitiveTrace(                                                   │    │
│   │      interaction_type=STUDENT_PROMPT,                                              │    │
│   │      ai_involvement=0.0,                                                           │    │
│   │      cognitive_intent="Interactuar con simulador product_owner"                   │    │
│   │    )                                                                               │    │
│   │                                                                                     │    │
│   │    output_trace = CognitiveTrace(                                                  │    │
│   │      interaction_type=AI_RESPONSE,                                                 │    │
│   │      ai_involvement=1.0,                                                           │    │
│   │      metadata={competencies_evaluated, competency_scores}                          │    │
│   │    )                                                                               │    │
│   │                                                                                     │    │
│   │    trace_repo.create(input_trace)                                                  │    │
│   │    trace_repo.create(output_trace)                                                 │    │
│   └───────────────────────────────────────────────────────────────────────────────────┘    │
│                │                                                                            │
│                ▼                                                                            │
│   [Estudiante recibe respuesta y continúa la interacción]                                  │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 14. Conclusiones

### 14.1 Rol de S-IA-X en el Ecosistema

| Aspecto | Descripción |
|---------|-------------|
| **Propósito** | Desarrollar competencias transversales en entornos situados |
| **Input** | Mensaje del estudiante + contexto + session_id |
| **Output** | Respuesta del rol profesional + análisis de competencias |
| **Persistencia** | Trazas N4, eventos de simulador, sesiones especializadas |

### 14.2 Competencias Desarrolladas

| Simulador | Competencias Clave |
|-----------|-------------------|
| PO-IA | Comunicación técnica, análisis de requisitos, priorización |
| SM-IA | Gestión de tiempo, comunicación, identificación de impedimentos |
| IT-IA | Dominio conceptual, análisis algorítmico, razonamiento en voz alta |
| IR-IA | Diagnóstico sistemático, priorización bajo presión, documentación |
| CX-IA | Elicitación de requisitos, negociación, empatía |
| DSO-IA | Seguridad, análisis de vulnerabilidades, gestión de riesgo |

### 14.3 Integración con el Sistema

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────►│   /simulators   │────►│    S-IA-X       │
│  (React/TS)     │     │    Router       │     │    Agent        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                        ┌─────────────────────────────────────────┐
                        │               PostgreSQL                 │
                        │                                         │
                        │  ┌─────────────────────────────────┐   │
                        │  │ cognitive_traces                 │   │
                        │  │ simulator_events                 │   │
                        │  │ interview_sessions               │   │
                        │  │ incident_simulations             │   │
                        │  └─────────────────────────────────┘   │
                        │                                         │
                        └─────────────────────────────────────────┘
```

---

## 15. Referencias

- **Archivo principal**: `backend/agents/simulators.py`
- **Router**: `backend/api/routers/simulators.py`
- **Schemas**: `backend/api/schemas/simulator.py`, `backend/api/schemas/simulators.py`, `backend/api/schemas/simulator_event.py`
- **ORM Models**: `backend/database/models.py` → `SimulatorEventDB`, `InterviewSessionDB`, `IncidentSimulationDB`
- **Repositories**: `backend/database/repositories.py` → `SimulatorEventRepository`, `InterviewSessionRepository`, `IncidentSimulationRepository`
- **Historia de Usuario**: HU-EST-009 (Product Owner), HU-EST-010 (Daily Standup), HU-EST-011 (Entrevista Técnica), HU-EST-012 (Incidentes), HU-EST-013 (Cliente), HU-EST-014 (Seguridad)

---

*Documentación generada por análisis de código del sistema AI-Native MVP*
*Fecha: 13 de Diciembre de 2025*