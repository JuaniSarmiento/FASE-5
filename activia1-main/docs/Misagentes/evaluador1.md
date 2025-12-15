# E-IA-Proc: Evaluador de Procesos Cognitivos

## Documentación Técnica Completa

---

## 1. Introducción y Propósito

### 1.1 ¿Qué es E-IA-Proc?

El **E-IA-Proc** (Evaluador IA de Procesos Cognitivos) es el **Submodelo 2** del ecosistema AI-Native. Su propósito fundamental es:

> **Analizar, reconstruir y evaluar el PROCESO cognitivo híbrido humano-IA que condujo a una solución técnica.**

A diferencia de los evaluadores tradicionales que califican solo el producto final (el código), E-IA-Proc evalúa **CÓMO** el estudiante llegó a la solución:
- ¿Planificó antes de codificar?
- ¿Justificó sus decisiones?
- ¿Se autocorrigió cuando encontró errores?
- ¿Usó la IA como herramienta o como muleta?

### 1.2 Principio Fundamental

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  E-IA-Proc NO CALIFICA NI APRUEBA                                              ║
║  Solo ANALIZA y GENERA EVIDENCIA para que el docente tome la decisión final   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

Este principio es crítico: el evaluador proporciona análisis objetivo y evidencia trazable, pero la evaluación final siempre es responsabilidad del docente humano.

### 1.3 Referencia Teórica

El E-IA-Proc se basa en el modelo de **autorregulación de Zimmerman (2002)**, que propone tres fases cíclicas del aprendizaje:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CICLO DE ZIMMERMAN                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│    │ PLANIFICACIÓN│───►│  EJECUCIÓN   │───►│  REFLEXIÓN   │   │
│    │  (Forethought)│    │ (Performance)│    │(Self-Reflect)│   │
│    └──────────────┘    └──────────────┘    └──────────────┘   │
│           ▲                                        │           │
│           └────────────────────────────────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Ubicación en el Ecosistema

### 2.1 Archivo Principal

```
backend/agents/evaluator.py
```

### 2.2 Archivos Relacionados

| Archivo | Propósito |
|---------|-----------|
| `backend/models/evaluation.py` | Modelos Pydantic para evaluación |
| `backend/api/routers/evaluations.py` | Endpoints REST de evaluación |
| `backend/api/schemas/evaluation.py` | Schemas de request/response |
| `backend/database/models.py` | Modelo ORM `EvaluationDB` |
| `backend/database/repositories.py` | `EvaluationRepository` |
| `backend/core/response_generator.py` | Integración con ResponseGenerator |
| `backend/core/ai_gateway.py` | Orquestador principal |

### 2.3 Posición en la Arquitectura

```
                    ┌─────────────────────────────────────────┐
                    │             AIGateway                    │
                    │         (Orquestador STATELESS)          │
                    └──────────────────┬──────────────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
    ┌───────────────┐         ┌───────────────┐         ┌───────────────┐
    │   T-IA-Cog    │         │  E-IA-Proc    │         │   S-IA-X      │
    │    (Tutor)    │         │  (EVALUADOR)  │◄────────│ (Simuladores) │
    └───────────────┘         └───────────────┘         └───────────────┘
            │                          │                          │
            │                          │                          │
            ▼                          ▼                          ▼
    ┌───────────────────────────────────────────────────────────────────┐
    │                          TC-N4                                     │
    │              (Sistema de Trazabilidad Cognitiva)                   │
    │                                                                     │
    │   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐          │
    │   │   N1    │   │   N2    │   │   N3    │   │   N4    │          │
    │   │Superfic.│   │ Técnico │   │Interacc.│   │Cognitivo│          │
    │   └─────────┘   └─────────┘   └─────────┘   └─────────┘          │
    └───────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
    ┌───────────────────────────────────────────────────────────────────┐
    │                        PostgreSQL                                  │
    │     evaluations │ cognitive_traces │ sessions │ trace_sequences   │
    └───────────────────────────────────────────────────────────────────┘
```

---

## 3. Estructura de la Clase Principal

### 3.1 Clase `EvaluadorProcesosAgent`

```python
class EvaluadorProcesosAgent:
    """
    E-IA-Proc: Evaluador de Procesos Cognitivos

    Funciones:
    1. Análisis de razonamiento (camino cognitivo)
    2. Detección de errores conceptuales y epistemológicos
    3. Evaluación de autorregulación (Zimmerman, 2002)
    4. Comparación y coherencia evolutiva vía Git
    5. Generación del Informe de Evaluación Cognitiva (IEC)

    NO califica ni aprueba - solo analiza y genera evidencia
    """
```

### 3.2 Constructor

```python
def __init__(self, llm_provider=None, config: Optional[Dict[str, Any]] = None):
    self.llm_provider = llm_provider  # Proveedor de LLM (Ollama/Phi-3)
    self.config = config or {}         # Configuración adicional
```

**Inyección de Dependencias:**
- El `llm_provider` se inyecta desde el `AIGateway`
- Permite usar diferentes modelos (Phi-3, Llama2, GPT-4) según configuración

---

## 4. Flujo de Evaluación Principal

### 4.1 Método Central: `evaluate_process()`

```python
def evaluate_process(
    self,
    trace_sequence: TraceSequence,  # Secuencia de trazas N4
    code_evolution: Optional[List[Dict[str, Any]]] = None  # Commits Git
) -> EvaluationReport:
```

### 4.2 Pipeline de Evaluación (7 Fases)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PIPELINE DE EVALUACIÓN E-IA-Proc                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ENTRADA: TraceSequence (secuencia de trazas cognitivas N4)               │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 1: Análisis del Razonamiento                                    │  │
│   │ _analyze_reasoning(trace_sequence)                                   │  │
│   │   • Reconstruir camino cognitivo                                     │  │
│   │   • Identificar fases completadas                                    │  │
│   │   • Contar cambios de estrategia, autocorrecciones                   │  │
│   │   • Calcular coherencia entre decisiones y justificaciones           │  │
│   │   • Detectar errores conceptuales y falacias lógicas                 │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                               │                                             │
│                               ▼                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 2: Análisis Git (opcional)                                      │  │
│   │ _analyze_git_evolution(code_evolution, trace_sequence)               │  │
│   │   • Evaluar calidad de mensajes de commit                            │  │
│   │   • Detectar "saltos sospechosos" (código copiado sin entender)      │  │
│   │   • Verificar coherencia de evolución                                 │  │
│   │   • Vincular commits a trazas N4                                     │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                               │                                             │
│                               ▼                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 3: Cálculo de Dependencia de IA                                 │  │
│   │ _calculate_ai_dependency(trace_sequence)                             │  │
│   │   • Obtener ai_dependency_score de la secuencia                      │  │
│   │   • Escala 0.0 (autónomo) a 1.0 (dependencia total)                  │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                               │                                             │
│                               ▼                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 4: Identificación de Riesgos Cognitivos                         │  │
│   │ _identify_cognitive_risks(trace_sequence, reasoning)                 │  │
│   │   • Sin cambios de estrategia → posible inflexibilidad               │  │
│   │   • Sin autocorrecciones → falta de revisión crítica                 │  │
│   │   • Planificación insuficiente                                        │  │
│   │   • Baja coherencia entre decisiones y justificaciones               │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                               │                                             │
│                               ▼                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 5: Evaluación de Dimensiones                                    │  │
│   │ _evaluate_dimensions(trace_sequence, reasoning)                      │  │
│   │   • Descomposición de Problemas                                       │  │
│   │   • Autorregulación y Metacognición                                  │  │
│   │   • Coherencia Lógica                                                 │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                               │                                             │
│                               ▼                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 6: Cálculo de Evaluación General                                │  │
│   │ _compute_overall_evaluation(dimensions)                              │  │
│   │   • Promedio de scores de dimensiones                                 │  │
│   │   • Mapeo a CompetencyLevel (INICIAL → EXPERTO)                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                               │                                             │
│                               ▼                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │ FASE 7: Generación de Recomendaciones                                │  │
│   │ _identify_strengths_and_improvements()                               │  │
│   │ _generate_recommendations()                                          │  │
│   │   • Fortalezas detectadas                                             │  │
│   │   • Áreas de mejora                                                   │  │
│   │   • Recomendaciones para estudiante                                   │  │
│   │   • Recomendaciones para docente                                      │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                               │                                             │
│                               ▼                                             │
│   SALIDA: EvaluationReport (Informe de Evaluación Cognitiva)              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Análisis del Razonamiento

### 5.1 Modelo `ReasoningAnalysis`

```python
class ReasoningAnalysis(BaseModel):
    """Análisis del proceso de razonamiento"""

    # Camino cognitivo
    cognitive_path: List[str]           # Estados cognitivos transitados
    phases_completed: List[CognitivePhase]  # Fases completadas

    # Métricas de proceso
    strategy_changes: int               # Cambios de estrategia
    self_corrections: int               # Autocorrecciones realizadas
    ai_critiques: int                   # Críticas a respuestas de IA

    # Coherencia
    coherence_score: float              # 0.0 - 1.0 (decisiones vs justificaciones)
    conceptual_errors: List[str]        # Errores conceptuales detectados
    logical_fallacies: List[str]        # Falacias lógicas detectadas

    # Autorregulación (Zimmerman)
    planning_quality: float             # Calidad de planificación (0.0 - 1.0)
    monitoring_evidence: List[str]      # Evidencias de automonitoreo
    self_explanation_quality: float     # Calidad de autoexplicación (0.0 - 1.0)
```

### 5.2 Fases Cognitivas Detectadas

```python
class CognitivePhase(str, Enum):
    """Fases del proceso cognitivo"""
    PLANIFICACION = "planificacion"     # Planificación inicial
    EXPLORACION = "exploracion"         # Exploración conceptual
    IMPLEMENTACION = "implementacion"   # Codificación
    DEPURACION = "depuracion"          # Debug y corrección
    VALIDACION = "validacion"          # Testing y verificación
    REFLEXION = "reflexion"            # Metacognición
```

### 5.3 Detección de Fases por Keywords

```python
phases_keywords = {
    CognitivePhase.PLANIFICACION: ["plan", "estrategia", "voy a", "primero"],
    CognitivePhase.EXPLORACION: ["entiendo", "qué es", "cómo funciona"],
    CognitivePhase.IMPLEMENTACION: ["implemento", "código", "función"],
    CognitivePhase.DEPURACION: ["error", "bug", "falla", "no funciona"],
    CognitivePhase.VALIDACION: ["prueba", "test", "verifica", "funciona"],
    CognitivePhase.REFLEXION: ["me doy cuenta", "entiendo que", "aprendí"]
}
```

---

## 6. Dimensiones de Evaluación

### 6.1 Las 3 Dimensiones Evaluadas

| Dimensión | Descripción | Indicadores |
|-----------|-------------|-------------|
| **Descomposición de Problemas** | Capacidad de dividir problemas complejos en subproblemas manejables | `planning_quality` |
| **Autorregulación y Metacognición** | Capacidad de monitorear y ajustar el propio proceso de aprendizaje | `self_explanation_quality`, `monitoring_evidence` |
| **Coherencia Lógica** | Coherencia entre razonamiento, decisiones y justificaciones | `coherence_score` |

### 6.2 Niveles de Competencia

```python
class CompetencyLevel(str, Enum):
    """Nivel de competencia alcanzado"""
    INICIAL = "inicial"           # < 5.0 puntos
    EN_DESARROLLO = "en_desarrollo"  # 5.0 - 6.9 puntos
    AUTONOMO = "autonomo"         # 7.0 - 8.4 puntos
    EXPERTO = "experto"           # >= 8.5 puntos
```

### 6.3 Conversión Score → Nivel

```python
def _score_to_level(self, score: float) -> CompetencyLevel:
    if score >= 8.5:
        return CompetencyLevel.EXPERTO
    elif score >= 7.0:
        return CompetencyLevel.AUTONOMO
    elif score >= 5.0:
        return CompetencyLevel.EN_DESARROLLO
    else:
        return CompetencyLevel.INICIAL
```

---

## 7. Análisis de Dependencia de IA

### 7.1 Concepto

El **ai_dependency_score** mide qué tan dependiente es el estudiante de la asistencia de IA:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ESCALA DE DEPENDENCIA DE IA                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  0.0 ────────────────────────────────────────────────────────── 1.0    │
│   │                                                               │     │
│   │  Autónomo                    Moderado               Dependiente│     │
│   │                                                               │     │
│   │  ✅ Trabaja                  ⚠️ Balance              ❌ Delega │     │
│   │     independiente               saludable               todo   │     │
│                                                                         │
│  Interpretación del score:                                              │
│  • < 0.3  → ✅ Muy autónomo                                            │
│  • 0.3-0.6 → ✅ Balance saludable                                       │
│  • 0.6-0.8 → ⚠️ Dependencia moderada-alta                              │
│  • > 0.8  → ❌ Dependencia muy alta (alerta)                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Cálculo del Score

El score se calcula como el promedio de `ai_involvement` de todas las trazas:

```python
# En TraceSequence._recalculate_ai_dependency()
if self.traces:
    total_involvement = sum(t.ai_involvement for t in self.traces)
    self.ai_dependency_score = total_involvement / len(self.traces)
else:
    self.ai_dependency_score = 0.0
```

### 7.3 Patrones de Uso de IA Analizados

```python
def _analyze_ai_usage_patterns(self, trace_sequence: TraceSequence) -> Dict[str, Any]:
    traces = trace_sequence.traces
    ai_interactions = [t for t in traces if t.interaction_type.value == "ai_response"]

    return {
        "total_ai_interactions": len(ai_interactions),
        "ai_interaction_rate": len(ai_interactions) / len(traces) if traces else 0,
        "delegation_attempts": 0,  # Calculado por el Tutor
    }
```

---

## 8. Identificación de Riesgos Cognitivos

### 8.1 Riesgos Detectados Automáticamente

```python
def _identify_cognitive_risks(self, trace_sequence, reasoning) -> List[str]:
    risks = []

    # 1. Sin cambios de estrategia
    if reasoning.strategy_changes == 0:
        risks.append("No se observan cambios de estrategia (posible inflexibilidad)")

    # 2. Sin autocorrecciones
    if reasoning.self_corrections == 0:
        risks.append("No se observan autocorrecciones (falta de revisión crítica)")

    # 3. Planificación insuficiente
    if reasoning.planning_quality < 0.3:
        risks.append("Planificación insuficiente")

    # 4. Baja coherencia
    if reasoning.coherence_score < 0.5:
        risks.append("Baja coherencia entre decisiones y justificaciones")

    return risks
```

### 8.2 Relación con AR-IA (Analista de Riesgos)

El E-IA-Proc detecta riesgos **cognitivos**, mientras que AR-IA analiza **5 dimensiones de riesgo**:

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    DIVISIÓN DE RIESGOS EN EL ECOSISTEMA                   │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   E-IA-Proc (Evaluador)                 AR-IA (Analista de Riesgos)       │
│   ─────────────────────                 ────────────────────────────       │
│   • Inflexibilidad cognitiva            • RC: Riesgo Cognitivo             │
│   • Falta de revisión crítica           • RE: Riesgo Ético                 │
│   • Planificación insuficiente          • REp: Riesgo Epistémico           │
│   • Baja coherencia decisión-           • RT: Riesgo Técnico               │
│     justificación                       • RG: Riesgo de Gobernanza         │
│                                                                           │
│   ► Enfocado en PROCESO                 ► Enfocado en COMPORTAMIENTO      │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Generación de Retroalimentación Formativa

### 9.1 Método `generate_formative_feedback()`

```python
def generate_formative_feedback(
    self,
    evaluation_report: EvaluationReport,
    student_friendly: bool = True
) -> str:
```

Este método genera retroalimentación en **dos formatos**:

| Formato | Método | Destinatario |
|---------|--------|--------------|
| `student_friendly=True` | `_generate_student_feedback()` | Estudiante |
| `student_friendly=False` | `_generate_teacher_feedback()` | Docente |

### 9.2 Estructura de Retroalimentación para Estudiante

```markdown
# 📊 Retroalimentación de tu Proceso de Aprendizaje

**Actividad**: prog2_tp1_colas
**Fecha**: 13/12/2025 10:30

---

## 🎯 Evaluación General

**Nivel de Competencia**: EN_DESARROLLO
**Puntaje**: 6.5/10

**¿Qué significa esto?** Vas por buen camino. Con más práctica alcanzarás mayor autonomía.

---

## ✅ Tus Fortalezas

- Buena planificación inicial
- Capacidad de autocorrección

---

## 🎓 Áreas para Mejorar

- Mejorar: Coherencia Lógica

---

## 🔍 Análisis de tu Proceso

### Fases que Completaste

- 📋 Planificación
- 🔍 Exploración Conceptual
- 💻 Implementación

### Eventos Clave

- **Cambios de estrategia**: 2 ✅
- **Autocorrecciones**: 1 ✅
- **Revisión crítica de IA**: 0 ⚠️

💡 **Tip**: No encontramos evidencia de cuestionamiento de las respuestas de IA.

---

## 🤖 Tu Colaboración con IA

**Nivel de asistencia de IA**: 45%

✅ Balance saludable entre tu trabajo y la asistencia de IA.

---

## 🎯 Recomendaciones para Seguir Mejorando

1. Dedicá más tiempo a planificar antes de implementar.
2. Practicá la revisión crítica: cuestioná tus propias soluciones.

---

🤖 *Retroalimentación generada automáticamente por E-IA-Proc basada en trazabilidad N4*
```

### 9.3 Estructura de Retroalimentación para Docente

```markdown
# 📊 Reporte de Evaluación de Proceso - Docente

**Estudiante**: student_123
**Actividad**: prog2_tp1_colas
**Sesión**: 550e8400-e29b-41d4-a716-446655440000
**Fecha**: 13/12/2025 10:30

---

## Resumen Ejecutivo

- **Nivel de Competencia**: EN_DESARROLLO
- **Puntaje General**: 6.5/10
- **Dependencia de IA**: 45%
- **Trazas Analizadas**: 1

---

## Análisis del Razonamiento

### Métricas Clave

| Métrica | Valor | Análisis |
|---------|-------|----------|
| Cambios de estrategia | 2 | ✅ Flexibilidad cognitiva |
| Autocorrecciones | 1 | ✅ Revisión crítica activa |
| Crítica a IA | 0 | ⚠️ Aceptación acrítica |
| Coherencia | 0.65 | ⚠️ Baja coherencia |
| Calidad de planificación | 0.75 | ✅ Buena planificación |

---

## Evaluación por Dimensiones

### Descomposición de Problemas

- **Nivel**: autonomo
- **Score**: 7.5/10
- **Evidencias**: 3 registradas

### Autorregulación y Metacognición

- **Nivel**: en_desarrollo
- **Score**: 5.5/10
- **Evidencias**: 2 registradas

---

## ⚠️ Riesgos Cognitivos Detectados

- Baja coherencia entre decisiones y justificaciones

---

## 🎓 Recomendaciones Pedagógicas

- Revisar proceso completo documentado en trazabilidad N4
- Solicitar planificación explícita antes de codificar

---

## 📝 Notas para Evaluación

Este reporte analiza el **proceso cognitivo**, no el producto final.
Considerar:

1. **Evaluación de proceso (60%) + producto (40%)**
2. Evidencia de trazabilidad N4 disponible para auditoría
3. Decisiones clave documentadas con justificación
4. Patrones de colaboración humano-IA

---

*Generado automáticamente por E-IA-Proc (Evaluador de Procesos Cognitivos)*
```

---

## 10. Interacción con Otros Agentes

### 10.1 Diagrama de Interacción

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTERACCIÓN E-IA-Proc CON OTROS AGENTES                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐                                                          │
│   │  TC-N4      │◄─────────── ENTRADA ────────────                         │
│   │ Trazabilidad│      TraceSequence con trazas cognitivas                 │
│   └─────────────┘                                                          │
│          │                                                                  │
│          │ Proporciona: CognitiveTrace[], ai_dependency_score              │
│          │              cognitive_path, strategy_changes                    │
│          ▼                                                                  │
│   ┌─────────────┐                                                          │
│   │  E-IA-Proc  │──── PROCESA ────►  EvaluationReport                     │
│   │  (Evaluador)│                                                          │
│   └─────────────┘                                                          │
│          │                                                                  │
│          │ Consulta (si disponible):                                        │
│          ▼                                                                  │
│   ┌─────────────┐                                                          │
│   │ Git Integr. │      code_evolution (commits)                            │
│   └─────────────┘                                                          │
│                                                                             │
│   ┌─────────────┐                                                          │
│   │   AR-IA     │◄─── COMPLEMENTA ───                                      │
│   │  (Riesgos)  │      cognitive_risks se agregan al reporte               │
│   └─────────────┘                                                          │
│                                                                             │
│   ┌─────────────┐                                                          │
│   │ AIGateway   │◄─── ORQUESTA ───                                         │
│   │             │      Invoca evaluate_process() cuando mode=EVALUATOR     │
│   └─────────────┘                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.2 Flujo de Datos

```
1. TC-N4 captura trazas durante toda la sesión
                    │
                    ▼
2. Las trazas se agregan a TraceSequence
                    │
                    ▼
3. Al finalizar sesión o solicitar evaluación:
   AIGateway invoca E-IA-Proc.evaluate_process(trace_sequence)
                    │
                    ▼
4. E-IA-Proc analiza las trazas y genera EvaluationReport
                    │
                    ▼
5. EvaluationRepository persiste el reporte en BD
                    │
                    ▼
6. El docente accede al reporte vía endpoint /evaluations
```

### 10.3 Integración con ResponseGenerator

```python
# En backend/core/response_generator.py

class ResponseGenerator:
    def __init__(
        self,
        tutor: TutorCognitivoAgent,
        evaluator: ProcessEvaluatorAgent,  # ◄── E-IA-Proc inyectado
        llm_provider: LLMProvider,
        config: Optional[Dict[str, Any]] = None
    ):
        self.tutor = tutor
        self.evaluator = evaluator
        ...

    def _generate_evaluation_response(
        self,
        session_id: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Genera respuesta de evaluación usando E-IA-Proc"""
        evaluation = self.evaluator.evaluate_process(
            session_id=session_id,
            context=context or {}
        )
        return evaluation
```

---

## 11. Interacción con Base de Datos

### 11.1 Tablas Utilizadas

```sql
-- TABLA PRINCIPAL: evaluations
CREATE TABLE evaluations (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    -- Evaluación general
    overall_competency_level VARCHAR(50) NOT NULL,  -- CompetencyLevel
    overall_score FLOAT NOT NULL CHECK (overall_score >= 0 AND overall_score <= 10),

    -- Dimensiones (JSON)
    dimensions JSON DEFAULT '[]',

    -- Retroalimentación (JSON)
    key_strengths JSON DEFAULT '[]',
    improvement_areas JSON DEFAULT '[]',
    recommendations JSON DEFAULT '{}',  -- {"student": [], "teacher": []}

    -- Análisis (JSON)
    reasoning_analysis JSON,
    git_analysis JSON,
    ai_dependency_score FLOAT DEFAULT 0.0 CHECK (ai_dependency_score >= 0 AND ai_dependency_score <= 1),
    ai_dependency_metrics JSON,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para consultas frecuentes
CREATE INDEX idx_eval_student_activity ON evaluations(student_id, activity_id);
CREATE INDEX idx_competency_score ON evaluations(overall_competency_level, overall_score);
CREATE INDEX idx_eval_student_created ON evaluations(student_id, created_at);
CREATE INDEX idx_eval_session_created ON evaluations(session_id, created_at);
```

### 11.2 Tablas de Lectura (Input)

```sql
-- cognitive_traces: Trazas que se analizan
CREATE TABLE cognitive_traces (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    trace_level VARCHAR(50) NOT NULL,     -- n1_superficial, n2_tecnico, n3_interaccional, n4_cognitivo
    interaction_type VARCHAR(50) NOT NULL, -- student_prompt, ai_response, etc.
    content TEXT NOT NULL,
    context JSON,

    -- N4: Análisis cognitivo
    cognitive_state VARCHAR(50),
    cognitive_intent VARCHAR(100),
    decision_justification TEXT,
    alternatives_considered JSON,
    ai_involvement FLOAT DEFAULT 0.0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- trace_sequences: Secuencias de trazas analizadas
CREATE TABLE trace_sequences (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES sessions(id),
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    trace_ids JSON DEFAULT '[]',          -- IDs de trazas en la secuencia
    reasoning_path JSON DEFAULT '[]',     -- Camino cognitivo reconstruido
    strategy_changes JSON DEFAULT '[]',
    ai_dependency_score FLOAT DEFAULT 0.0,

    start_time TIMESTAMP,
    end_time TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- sessions: Sesiones de aprendizaje
CREATE TABLE sessions (
    id VARCHAR(36) PRIMARY KEY,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,
    mode VARCHAR(50) NOT NULL,            -- TUTOR, EVALUATOR, SIMULATOR, etc.
    status VARCHAR(50) DEFAULT 'active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 11.3 Modelo ORM: `EvaluationDB`

```python
# backend/database/models.py

class EvaluationDB(Base, BaseModel):
    """Database model for process evaluations"""

    __tablename__ = "evaluations"

    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=False)

    # Overall assessment
    overall_competency_level = Column(String(50), nullable=False)  # CompetencyLevel
    overall_score = Column(Float, nullable=False)  # 0.0 to 10.0

    # Dimensions (stored as JSON for flexibility)
    dimensions = Column(JSON, default=list)  # List of DimensionEvaluation dicts

    # Feedback
    key_strengths = Column(JSON, default=list)
    improvement_areas = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)

    # Analysis metadata
    reasoning_analysis = Column(JSON, nullable=True)
    git_analysis = Column(JSON, nullable=True)
    ai_dependency_score = Column(Float, default=0.0)
    ai_dependency_metrics = Column(JSON, nullable=True)

    # Relationship
    session = relationship("SessionDB", back_populates="evaluations")
```

### 11.4 Repository: `EvaluationRepository`

```python
# backend/database/repositories.py

class EvaluationRepository:
    """Repository for evaluation operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, evaluation: EvaluationReport) -> EvaluationDB:
        """Crea una nueva evaluación"""
        # Combinar recomendaciones en estructura JSON única
        recommendations = {
            "student": evaluation.recommendations_student,
            "teacher": evaluation.recommendations_teacher,
        }

        db_evaluation = EvaluationDB(
            id=str(uuid4()),
            session_id=evaluation.session_id,
            student_id=evaluation.student_id,
            activity_id=evaluation.activity_id,
            overall_competency_level=evaluation.overall_competency_level.value,
            overall_score=evaluation.overall_score,
            dimensions=[d.model_dump() for d in evaluation.dimensions],
            key_strengths=evaluation.key_strengths,
            improvement_areas=evaluation.improvement_areas,
            recommendations=recommendations,
            reasoning_analysis=evaluation.reasoning_analysis.model_dump() if evaluation.reasoning_analysis else {},
            git_analysis=evaluation.git_analysis.model_dump() if evaluation.git_analysis else {},
            ai_dependency_metrics={
                "score": evaluation.ai_dependency_score,
                "usage_patterns": evaluation.ai_usage_patterns,
            },
        )
        self.db.add(db_evaluation)
        self.db.commit()
        self.db.refresh(db_evaluation)
        return db_evaluation

    def get_by_id(self, evaluation_id: str) -> Optional[EvaluationDB]:
        """Obtiene evaluación por ID"""
        return self.db.query(EvaluationDB).filter(EvaluationDB.id == evaluation_id).first()

    def get_by_session(self, session_id: str, limit: int = 100, offset: int = 0) -> List[EvaluationDB]:
        """Obtiene todas las evaluaciones de una sesión"""
        return (
            self.db.query(EvaluationDB)
            .filter(EvaluationDB.session_id == session_id)
            .order_by(desc(EvaluationDB.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_by_student(self, student_id: str, limit: int = 100, offset: int = 0) -> List[EvaluationDB]:
        """Obtiene todas las evaluaciones de un estudiante"""
        return (
            self.db.query(EvaluationDB)
            .filter(EvaluationDB.student_id == student_id)
            .order_by(desc(EvaluationDB.created_at))
            .limit(limit)
            .offset(offset)
            .all()
        )

    def get_latest_by_session_ids(self, session_ids: List[str]) -> Dict[str, EvaluationDB]:
        """Batch loading: obtiene la última evaluación de múltiples sesiones"""
        # Previene N+1 queries
        ...
```

---

## 12. Endpoint REST de Evaluación

### 12.1 Router: `/evaluations`

```python
# backend/api/routers/evaluations.py

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])

@router.post("/{session_id}/generate", response_model=APIResponse[ProcessEvaluation])
async def generate_process_evaluation(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    llm_provider: LLMProvider = Depends(get_llm_provider),
    current_user: dict = Depends(get_current_user),  # Requiere autenticación
) -> APIResponse[ProcessEvaluation]:
    """
    Genera una evaluación cognitiva completa basada en el proceso observado

    Analiza:
    - Planificación: Cómo el estudiante aborda problemas nuevos
    - Ejecución: Calidad de implementación y estrategias
    - Debugging: Habilidad para diagnosticar y corregir errores
    - Reflexión: Metacognición y aprendizaje de errores
    - Autonomía: Independencia vs delegación a IA

    Returns:
        ProcessEvaluation con puntuaciones 0-10 en cada dimensión
    """
```

### 12.2 Flujo del Endpoint

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO: POST /evaluations/{session_id}/generate            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   1. VERIFICAR SESIÓN                                                        │
│      session = session_repo.get_by_id(session_id)                           │
│      if not session: raise SessionNotFoundError                              │
│                                                                              │
│   2. OBTENER TRAZAS COGNITIVAS                                              │
│      traces = trace_repo.get_by_session(session_id)                         │
│      if not traces: raise HTTPException(404, "No traces found")             │
│                                                                              │
│   3. CONSTRUIR DATOS PARA LLM                                               │
│      traces_data = [                                                         │
│          {                                                                   │
│              "input": trace.content,                                         │
│              "output": trace.context.get("ai_response", ""),                │
│              "ai_involvement": trace.ai_involvement,                         │
│              "timestamp": trace.timestamp.isoformat()                        │
│          }                                                                   │
│          for trace in traces[:20]  # Limitar a últimas 20                   │
│      ]                                                                       │
│                                                                              │
│   4. CONSTRUIR PROMPT PARA OLLAMA                                           │
│      prompt = f"""                                                           │
│      Eres un evaluador experto en cognición y aprendizaje.                  │
│      Analiza la sesión y evalúa el PROCESO en 5 dimensiones:                │
│      1. PLANNING (Planificación)                                             │
│      2. EXECUTION (Ejecución)                                                │
│      3. DEBUGGING (Depuración)                                               │
│      4. REFLECTION (Reflexión)                                               │
│      5. AUTONOMY (Autonomía)                                                 │
│      ...                                                                     │
│      """                                                                     │
│                                                                              │
│   5. LLAMAR A OLLAMA                                                         │
│      llm_response = await llm_provider.generate(                            │
│          messages=[LLMMessage(role=LLMRole.USER, content=prompt)],          │
│          temperature=0.3  # Baja para respuestas consistentes               │
│      )                                                                       │
│                                                                              │
│   6. PARSEAR RESPUESTA JSON                                                 │
│      eval_data = json.loads(llm_response.content)                           │
│      # Validar scores (0-10), levels (novice/competent/proficient/expert)   │
│                                                                              │
│   7. CONSTRUIR ProcessEvaluation                                            │
│      evaluation = ProcessEvaluation(                                         │
│          session_id=session_id,                                              │
│          student_id=session.student_id,                                      │
│          planning=DimensionScore(...),                                       │
│          execution=DimensionScore(...),                                      │
│          ...                                                                 │
│      )                                                                       │
│                                                                              │
│   8. RETORNAR RESPUESTA                                                     │
│      return APIResponse(success=True, data=evaluation)                      │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 12.3 Schema de Respuesta

```python
class ProcessEvaluation(BaseModel):
    """Evaluación completa del proceso cognitivo del estudiante"""
    session_id: str
    student_id: str
    activity_id: str

    # 5 dimensiones del proceso
    planning: DimensionScore
    execution: DimensionScore
    debugging: DimensionScore
    reflection: DimensionScore
    autonomy: DimensionScore

    # Patrones generales
    autonomy_level: str  # low/medium/high
    metacognition_score: float  # 0-10
    delegation_ratio: float  # 0-1 (% de delegación a IA)

    # Evidencia general
    overall_feedback: str
    generated_at: datetime
```

---

## 13. Modelo Pydantic: `EvaluationReport`

### 13.1 Estructura Completa

```python
# backend/models/evaluation.py

class EvaluationReport(BaseModel):
    """Informe de Evaluación Cognitiva (IEC) generado por E-IA-Proc"""

    # Identificadores
    id: str
    session_id: str
    created_at: datetime = Field(default_factory=datetime.now, alias="timestamp")
    student_id: str
    activity_id: str

    # Análisis principal
    reasoning_analysis: Optional[ReasoningAnalysis]
    git_analysis: Optional[GitAnalysis]

    # Dimensiones evaluadas
    dimensions: List[EvaluationDimension] = []

    # Dependencia de IA
    ai_dependency_score: float  # 0-1
    ai_usage_patterns: Dict[str, Any] = {}
    reasoning_map: Dict[str, Any] = {}

    # Riesgos cognitivos
    cognitive_risks: List[str] = []

    # Evaluación general
    overall_competency_level: CompetencyLevel
    overall_score: float  # 0-10

    # Retroalimentación
    key_strengths: List[str] = []
    improvement_areas: List[str] = []
    recommendations_student: List[str] = []
    recommendations_teacher: List[str] = []

    # Metadata
    evaluator_version: str = "E-IA-Proc-v1.0"
    trace_sequences_analyzed: int = 0
```

### 13.2 Submodelos

```python
class EvaluationDimension(BaseModel):
    """Dimensión de evaluación"""
    name: str                              # "Descomposición de Problemas"
    description: str                       # Descripción de la dimensión
    level: CompetencyLevel                 # INICIAL, EN_DESARROLLO, AUTONOMO, EXPERTO
    score: float                           # 0-10
    evidence: List[str] = []               # Evidencias observadas
    strengths: List[str] = []              # Fortalezas en esta dimensión
    weaknesses: List[str] = []             # Debilidades
    recommendations: List[str] = []        # Recomendaciones específicas


class GitAnalysis(BaseModel):
    """Análisis de evolución del código vía Git"""
    total_commits: int = 0
    commit_messages_quality: float  # 0-1
    suspicious_jumps: List[str] = []       # Saltos abruptos (posible código copiado)
    evolution_coherence: float  # 0-1
    traces_linked: int = 0                 # Commits vinculados a trazas N4
```

---

## 14. Validación de Respuestas LLM

### 14.1 Problema

El LLM (Ollama/Phi-3) puede retornar valores fuera de rango:
- Scores como 15.5 o -2 (fuera de 0-10)
- Niveles inválidos como "super-expert" o "invalid"

### 14.2 Solución: Funciones de Validación

```python
# backend/api/routers/evaluations.py

VALID_LEVELS = {"novice", "competent", "proficient", "expert"}
DEFAULT_LEVEL = "competent"
MIN_SCORE = 0.0
MAX_SCORE = 10.0

def _validate_score(score: float) -> float:
    """Clamp score to valid range 0-10"""
    try:
        score = float(score)
    except (TypeError, ValueError):
        return 5.0  # Default if not a valid number
    return max(MIN_SCORE, min(MAX_SCORE, score))


def _validate_level(level: str) -> str:
    """Validate level is a valid value"""
    if not isinstance(level, str):
        return DEFAULT_LEVEL

    level_lower = level.lower().strip()

    # Direct match
    if level_lower in VALID_LEVELS:
        return level_lower

    # Common aliases/misspellings
    level_aliases = {
        "beginner": "novice",
        "developing": "novice",
        "basic": "novice",
        "intermediate": "competent",
        "medium": "competent",
        "advanced": "proficient",
        "skilled": "proficient",
        "master": "expert",
        "excellent": "expert",
    }

    if level_lower in level_aliases:
        return level_aliases[level_lower]

    logger.warning(f"Invalid level '{level}' from LLM, defaulting to '{DEFAULT_LEVEL}'")
    return DEFAULT_LEVEL
```

---

## 15. Escalas de Puntuación

### 15.1 Escalas Utilizadas

| Campo | Escala | Uso |
|-------|--------|-----|
| `overall_score` | 0-10 | Puntuación general del estudiante |
| `dimension.score` | 0-10 | Puntuación por dimensión |
| `ai_dependency_score` | 0-1 | Nivel de dependencia de IA |
| `coherence_score` | 0-1 | Coherencia decisión-justificación |
| `planning_quality` | 0-1 | Calidad de planificación |
| `self_explanation_quality` | 0-1 | Calidad de autoexplicación |

### 15.2 Importante (Fix Cortez8)

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  ESCALAS DE PUNTUACIÓN - CONSISTENCIA ORM vs PYDANTIC                         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║                                                                               ║
║  FIX 1.1-1.6 Cortez8: Las escalas fueron unificadas:                         ║
║                                                                               ║
║  • overall_score:      0-10 (era 0-1, ahora corregido)                       ║
║  • dimension.score:    0-10 (era 0-1, ahora corregido)                       ║
║  • ai_dependency_score: 0-1 (siempre fue así, sin cambios)                   ║
║                                                                               ║
║  El ORM (EvaluationDB) y el Pydantic (EvaluationReport) ahora usan las       ║
║  mismas escalas para evitar confusión.                                        ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 16. Resumen de Métodos Principales

### 16.1 Clase `EvaluadorProcesosAgent`

| Método | Propósito | Input | Output |
|--------|-----------|-------|--------|
| `evaluate_process()` | Pipeline principal de evaluación | `TraceSequence`, `code_evolution` | `EvaluationReport` |
| `_analyze_reasoning()` | Analiza camino cognitivo | `TraceSequence` | `ReasoningAnalysis` |
| `_identify_phases()` | Identifica fases completadas | `List[CognitiveTrace]` | `List[CognitivePhase]` |
| `_calculate_coherence()` | Calcula coherencia decisión-justificación | `List[CognitiveTrace]` | `float` (0-1) |
| `_detect_conceptual_errors()` | Detecta errores conceptuales | `List[CognitiveTrace]` | `List[str]` |
| `_analyze_git_evolution()` | Analiza commits Git | `code_evolution`, `TraceSequence` | `GitAnalysis` |
| `_calculate_ai_dependency()` | Obtiene score de dependencia IA | `TraceSequence` | `float` (0-1) |
| `_identify_cognitive_risks()` | Identifica riesgos cognitivos | `TraceSequence`, `ReasoningAnalysis` | `List[str]` |
| `_evaluate_dimensions()` | Evalúa 3 dimensiones | `TraceSequence`, `ReasoningAnalysis` | `List[EvaluationDimension]` |
| `_score_to_level()` | Convierte score a nivel | `float` | `CompetencyLevel` |
| `_compute_overall_evaluation()` | Calcula evaluación general | `List[EvaluationDimension]` | `(CompetencyLevel, float)` |
| `_generate_recommendations()` | Genera recomendaciones | dimensiones, reasoning, risks | `(List[str], List[str])` |
| `generate_formative_feedback()` | Genera retroalimentación | `EvaluationReport`, `student_friendly` | `str` (Markdown) |

---

## 17. Diagrama de Flujo Completo

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              FLUJO COMPLETO E-IA-Proc                                       │
├─────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                             │
│   [Estudiante trabaja en actividad]                                                         │
│                │                                                                            │
│                ▼                                                                            │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐    │
│   │                              TC-N4 (Trazabilidad)                                  │    │
│   │                                                                                     │    │
│   │   Captura continua de:                                                              │    │
│   │   • student_prompt, ai_response                                                     │    │
│   │   • cognitive_state, cognitive_intent                                               │    │
│   │   • decision_justification, alternatives_considered                                 │    │
│   │   • ai_involvement (0-1)                                                            │    │
│   │                                                                                     │    │
│   │   Almacena en: cognitive_traces (PostgreSQL)                                        │    │
│   │   Agrupa en: TraceSequence                                                          │    │
│   │                                                                                     │    │
│   └───────────────────────────────────────────────────────────────────────────────────┘    │
│                │                                                                            │
│                ▼                                                                            │
│   [Sesión finaliza o docente solicita evaluación]                                          │
│                │                                                                            │
│                ▼                                                                            │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐    │
│   │                    POST /evaluations/{session_id}/generate                         │    │
│   │                                                                                     │    │
│   │   1. Verificar sesión existe                                                        │    │
│   │   2. Obtener trazas de la sesión                                                    │    │
│   │   3. Construir TraceSequence                                                        │    │
│   │                                                                                     │    │
│   └───────────────────────────────────────────────────────────────────────────────────┘    │
│                │                                                                            │
│                ▼                                                                            │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐    │
│   │                         E-IA-Proc.evaluate_process()                               │    │
│   │                                                                                     │    │
│   │   FASE 1: _analyze_reasoning()                                                      │    │
│   │           └── cognitive_path, phases, strategy_changes, coherence                   │    │
│   │                                                                                     │    │
│   │   FASE 2: _analyze_git_evolution() [si disponible]                                 │    │
│   │           └── commits, quality, suspicious_jumps                                    │    │
│   │                                                                                     │    │
│   │   FASE 3: _calculate_ai_dependency()                                               │    │
│   │           └── ai_dependency_score (0-1)                                             │    │
│   │                                                                                     │    │
│   │   FASE 4: _identify_cognitive_risks()                                              │    │
│   │           └── riesgos: inflexibilidad, falta revisión, baja coherencia              │    │
│   │                                                                                     │    │
│   │   FASE 5: _evaluate_dimensions()                                                   │    │
│   │           └── Descomposición, Autorregulación, Coherencia                           │    │
│   │                                                                                     │    │
│   │   FASE 6: _compute_overall_evaluation()                                            │    │
│   │           └── overall_score (0-10), CompetencyLevel                                 │    │
│   │                                                                                     │    │
│   │   FASE 7: _generate_recommendations()                                              │    │
│   │           └── recomendaciones para estudiante y docente                             │    │
│   │                                                                                     │    │
│   └───────────────────────────────────────────────────────────────────────────────────┘    │
│                │                                                                            │
│                ▼                                                                            │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐    │
│   │                              EvaluationReport                                       │    │
│   │                                                                                     │    │
│   │   {                                                                                 │    │
│   │     "id": "eval_xxx",                                                               │    │
│   │     "session_id": "550e8400-...",                                                   │    │
│   │     "student_id": "student_123",                                                    │    │
│   │     "overall_score": 6.5,                                                           │    │
│   │     "overall_competency_level": "en_desarrollo",                                    │    │
│   │     "ai_dependency_score": 0.45,                                                    │    │
│   │     "dimensions": [...],                                                            │    │
│   │     "cognitive_risks": ["Baja coherencia..."],                                      │    │
│   │     "key_strengths": ["Buena planificación"],                                       │    │
│   │     "improvement_areas": ["Mejorar: Coherencia Lógica"],                            │    │
│   │     "recommendations_student": [...],                                               │    │
│   │     "recommendations_teacher": [...]                                                │    │
│   │   }                                                                                 │    │
│   │                                                                                     │    │
│   └───────────────────────────────────────────────────────────────────────────────────┘    │
│                │                                                                            │
│                ▼                                                                            │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐    │
│   │                         EvaluationRepository.create()                              │    │
│   │                                                                                     │    │
│   │   Persiste en PostgreSQL tabla `evaluations`                                        │    │
│   │                                                                                     │    │
│   └───────────────────────────────────────────────────────────────────────────────────┘    │
│                │                                                                            │
│                ▼                                                                            │
│   ┌───────────────────────────────────────────────────────────────────────────────────┐    │
│   │                        generate_formative_feedback()                               │    │
│   │                                                                                     │    │
│   │   Si student_friendly=True  → Retroalimentación para estudiante (Markdown)         │    │
│   │   Si student_friendly=False → Reporte técnico para docente (Markdown)              │    │
│   │                                                                                     │    │
│   └───────────────────────────────────────────────────────────────────────────────────┘    │
│                │                                                                            │
│                ▼                                                                            │
│   [Docente revisa y toma decisión final de evaluación]                                     │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 18. Conclusiones

### 18.1 Rol del E-IA-Proc en el Ecosistema

| Aspecto | Descripción |
|---------|-------------|
| **Propósito** | Evaluar el PROCESO cognitivo, no el producto final |
| **Input** | TraceSequence (trazas N4 capturadas por TC-N4) |
| **Output** | EvaluationReport con análisis, dimensiones, riesgos y recomendaciones |
| **Decisión Final** | SIEMPRE del docente humano (E-IA-Proc solo genera evidencia) |

### 18.2 Diferencias con Evaluadores Tradicionales

| Aspecto | Evaluador Tradicional | E-IA-Proc |
|---------|----------------------|-----------|
| **Foco** | Código final (producto) | Proceso cognitivo |
| **Datos** | Código entregado | Trazas N4 del camino completo |
| **Métricas** | Funcionalidad, style, tests | Planificación, autorregulación, coherencia |
| **Uso de IA** | No considerado | ai_dependency_score (0-1) |
| **Transparencia** | "Nota: 7.5" | Evidencia completa trazable |

### 18.3 Integración con Otros Agentes

```
TC-N4 ──► E-IA-Proc ──► EvaluationReport ──► Docente
  │                           │
  │                           ▼
  │                    Retroalimentación
  │                    formativa al estudiante
  │
  └──► AR-IA ──► Riesgos complementarios (5D)
```

---

## 19. Referencias

- **Archivo principal**: `backend/agents/evaluator.py`
- **Modelos**: `backend/models/evaluation.py`
- **Schemas API**: `backend/api/schemas/evaluation.py`
- **Router**: `backend/api/routers/evaluations.py`
- **ORM**: `backend/database/models.py` → `EvaluationDB`
- **Repository**: `backend/database/repositories.py` → `EvaluationRepository`
- **Base teórica**: Zimmerman, B. J. (2002). Becoming a Self-Regulated Learner: An Overview.

---

*Documentación generada por análisis de código del sistema AI-Native MVP*
*Fecha: 13 de Diciembre de 2025*