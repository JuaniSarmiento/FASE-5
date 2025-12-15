# Sprint 3: Roadmap Detallado - 41 Problemas Restantes

## Resumen Ejecutivo

**Objetivo**: Completar las mejoras de arquitectura, calidad de código y performance
**Problemas totales**: 41 (de los 57 originales, 16 ya resueltos)
**Tiempo estimado**: 2-3 semanas
**Prioridad**: MEDIUM-LOW (el sistema ya es seguro para producción)

---

## Categorización por Complejidad y Tiempo

### Categoría A: Quick Wins (1-2 horas c/u) - 15 problemas

**A1. Remover imports no utilizados** ⏱️ 1 hora
- **Archivos**: 58 archivos con imports potencialmente no usados
- **Tool**: Usar `autoflake` o verificación manual
- **Comando**:
  ```bash
  pip install autoflake
  autoflake --remove-all-unused-imports --in-place --recursive src/
  ```
- **Verificación**: Ejecutar tests después

**A2. Remover código comentado** ⏱️ 1 hora
- **Buscar**: Bloques de código comentado (no comments explicativos)
- **Criterio**: Eliminar código obsoleto, mantener TODOs útiles
- **Pattern**: Buscar `# [A-Z]` (código comentado típico)

**A3. Fix logging inconsistencies** ⏱️ 2 horas
- **Problema**: Mezcla de `print()`, `logger.info()`, `logger.debug()`
- **Solución**: Estandarizar todo a `logger.*` con niveles apropiados
- **Archivos principales**:
  - `src/ai_native_mvp/agents/` (varios usan print)
  - `src/ai_native_mvp/core/`

**A4. Extraer magic numbers en agents/** ⏱️ 2 horas
- **Archivos**:
  - `agents/tutor.py`: thresholds de ayuda
  - `agents/evaluator.py`: scores de competencia
  - `agents/risk_analyst.py`: thresholds de riesgo
- **Solución**: Agregar a `constants.py` y referenciar

**A5. Agregar docstrings a métodos privados** ⏱️ 2 horas
- **Target**: Métodos que empiezan con `_` sin docstring
- **Formato**:
  ```python
  def _private_method(self, arg: str) -> int:
      """
      Una línea de descripción.

      Args:
          arg: Descripción del argumento

      Returns:
          Descripción del retorno
      """
  ```

**A6-A15: Otros quick wins**
- Normalizar nombres de variables
- Extraer constantes de strings repetidos
- Agregar type hints faltantes
- Mejorar mensajes de error
- Documentar assumptions en código
- Agregar ejemplos en docstrings
- Verificar cobertura de edge cases
- Actualizar comentarios obsoletos
- Verificar  consistencia de nombres
- Ordenar imports (isort)

---

### Categoría B: Mejoras Medianas (4-8 horas c/u) - 12 problemas

**B1. Type hints con TypedDict** ⏱️ 6 horas
**Problema**: Uso extensivo de `Dict[str, Any]` sin estructura definida

**Solución**:
```python
# Antes
def process_context(context: Dict[str, Any]) -> Dict[str, Any]:
    pass

# Después
from typing import TypedDict

class TraceContext(TypedDict, total=False):
    """Contexto de una traza cognitiva."""
    code_snippet: str
    line_number: int
    file_path: str
    variables: Dict[str, Any]

class TraceMetadata(TypedDict, total=False):
    """Metadata de una traza."""
    agent_id: str
    processing_time_ms: float
    blocked: bool
    block_reason: Optional[str]

def process_context(context: TraceContext) -> TraceMetadata:
    pass
```

**Archivos a actualizar**:
- `models/trace.py`: TraceContext, TraceMetadata
- `models/risk.py`: RiskEvidence, RiskContext
- `core/ai_gateway.py`: Classification result, context dicts
- `agents/*.py`: Resultado de análisis

**Beneficios**:
- Autocompletion en IDE
- Type checking en desarrollo
- Documentación implícita
- Menos bugs

---

**B2. Sanitizar mensajes de error hacia cliente** ⏱️ 4 horas
**Problema**: Stack traces y detalles internos expuestos en API

**Solución**:
```python
# api/middleware/error_handler.py

def sanitize_error_message(error: Exception, is_production: bool) -> str:
    """Sanitiza mensajes de error según el entorno."""
    if is_production:
        # Mensajes genéricos en producción
        error_map = {
            ValidationError: "Invalid input data. Please check your request.",
            DatabaseError: "A database error occurred. Please try again later.",
            LLMError: "AI service temporarily unavailable. Please try again.",
        }
        return error_map.get(type(error), "An unexpected error occurred.")
    else:
        # Mensajes detallados en desarrollo
        return f"{type(error).__name__}: {str(error)}"
```

---

**B3. Extraer métodos de lógica booleana compleja** ⏱️ 6 horas
**Problema**: Condiciones largas y difíciles de leer

**Ejemplos**:
```python
# Antes (ai_gateway.py)
if trace.cognitive_state == "EXPLORACION" and \
   trace.ai_involvement > 0.6 and \
   len(prev_traces) > 5 and \
   all(t.ai_involvement > 0.5 for t in prev_traces[-3:]):
    # Detectar delegación

# Después
def _is_showing_delegation_pattern(
    trace: CognitiveTrace,
    prev_traces: List[CognitiveTrace]
) -> bool:
    """
    Detecta patrón de delegación excesiva.

    Criteria:
    - Estado exploratorio con alta dependencia de IA (>60%)
    - Historial de 5+ interacciones
    - Últimas 3 interacciones con >50% dependencia de IA

    Returns:
        True si se detecta patrón de delegación
    """
    if trace.cognitive_state != CognitiveState.EXPLORACION:
        return False

    if trace.ai_involvement <= AI_DEPENDENCY_MEDIUM_THRESHOLD:
        return False

    if len(prev_traces) < MIN_INTERACTIONS_FOR_RISK_ANALYSIS:
        return False

    recent_traces = prev_traces[-CONSECUTIVE_HIGH_AI_THRESHOLD:]
    return all(t.ai_involvement > 0.5 for t in recent_traces)

# Uso
if self._is_showing_delegation_pattern(trace, prev_traces):
    # Detectar delegación
```

**Archivos a refactorizar**:
- `core/ai_gateway.py`: process_interaction logic
- `agents/risk_analyst.py`: risk detection logic
- `agents/evaluator.py`: scoring logic

---

**B4. Implementar `_analyze_risks_async` o remover** ⏱️ 8 horas
**Problema**: Placeholder no implementado desde Sprint 1

**Opción 1: Implementar (recomendado)**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AIGateway:
    def __init__(self, ...):
        self._risk_executor = ThreadPoolExecutor(max_workers=2)

    async def _analyze_risks_async(
        self,
        session_id: str,
        input_trace: CognitiveTrace,
        response_trace: CognitiveTrace,
        classification: Dict[str, Any]
    ) -> List[Risk]:
        """
        Análisis de riesgos asíncrono usando AR-IA.

        Corre en background thread para no bloquear response.
        """
        loop = asyncio.get_event_loop()

        # Run risk analysis in thread pool
        risks = await loop.run_in_executor(
            self._risk_executor,
            self._analyze_risks_sync,
            session_id,
            input_trace,
            response_trace,
            classification
        )

        # Persist async
        for risk in risks:
            await loop.run_in_executor(
                None,
                self.risk_repo.create,
                risk
            )

        return risks

    def _analyze_risks_sync(self, ...) -> List[Risk]:
        """Análisis síncrono de riesgos (wrapper)."""
        return self.risk_analyst.analyze(...)
```

**Opción 2: Remover**
- Si el análisis de riesgos es rápido (<100ms), mantener síncrono
- Documentar decisión en código

---

**B5-B12: Otros problemas medianos**
- Rate limiting en cache operations
- Connection pooling configuración explícita
- Memory limits en cache
- Advanced health checks
- Performance metrics
- Documentation improvements
- Test coverage gaps
- Error handling edge cases

---

### Categoría C: Refactorizaciones Mayores (1-3 días c/u) - 14 problemas

**C1. Refactorizar AIGateway God Class** ⏱️ 3 días
**Problema**: 710 líneas, múltiples responsabilidades

**Plan de Refactorización**:

**Paso 1: Extraer `ResponseGenerator`**
```python
# NEW: core/response_generator.py
class ResponseGenerator:
    """Genera respuestas pedagógicas usando el agente apropiado."""

    def __init__(
        self,
        tutor: TutorCognitivoAgent,
        evaluator: ProcessEvaluatorAgent,
        simulators: Dict[str, SimulatorAgent],
        llm_provider: LLMProvider
    ):
        self.tutor = tutor
        self.evaluator = evaluator
        self.simulators = simulators
        self.llm_provider = llm_provider

    def generate_response(
        self,
        classification: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Genera respuesta usando el agente apropiado."""
        request_type = classification.get("type")

        if request_type == "help_request":
            return self.tutor.process_request(...)
        elif request_type == "evaluation_request":
            return self.evaluator.evaluate_process(...)
        elif request_type == "simulator_request":
            simulator_type = classification.get("simulator")
            return self.simulators[simulator_type].simulate(...)
        else:
            return self._generate_default_response(...)
```

**Paso 2: Extraer `TraceManager`**
```python
# NEW: core/trace_manager.py
class TraceManager:
    """Gestiona captura y persistencia de trazas N4."""

    def __init__(
        self,
        trace_repo: TraceRepository,
        sequence_repo: TraceSequenceRepository,
        traceability_agent: TrazabilidadN4Agent
    ):
        self.trace_repo = trace_repo
        self.sequence_repo = sequence_repo
        self.traceability_agent = traceability_agent

    def capture_input_trace(
        self,
        session_id: str,
        student_id: str,
        prompt: str,
        cognitive_state: CognitiveState,
        context: Dict[str, Any]
    ) -> CognitiveTrace:
        """Captura traza de entrada del estudiante."""
        trace = self.traceability_agent.capture_trace(
            session_id=session_id,
            student_id=student_id,
            interaction_type=InteractionType.STUDENT_PROMPT,
            content=prompt,
            cognitive_state=cognitive_state,
            context=context
        )

        # Persist
        self.trace_repo.create(trace)
        return trace

    def capture_output_trace(
        self,
        session_id: str,
        response: str,
        agent_used: str,
        ai_involvement: float
    ) -> CognitiveTrace:
        """Captura traza de salida del agente."""
        # ... similar
```

**Paso 3: Extraer `RiskAnalyzer`**
```python
# NEW: core/risk_analyzer.py
class RiskAnalyzer:
    """Analiza riesgos cognitivos, éticos y técnicos."""

    def __init__(
        self,
        risk_analyst: RiskAnalystAgent,
        risk_repo: RiskRepository
    ):
        self.risk_analyst = risk_analyst
        self.risk_repo = risk_repo

    async def analyze_interaction_risks(
        self,
        session_id: str,
        input_trace: CognitiveTrace,
        output_trace: CognitiveTrace,
        classification: Dict[str, Any]
    ) -> List[Risk]:
        """Analiza riesgos de una interacción."""
        # Run in background
        risks = await self._run_risk_analysis(...)

        # Persist
        for risk in risks:
            self.risk_repo.create(risk)

        return risks
```

**Paso 4: Refactorizar AIGateway**
```python
# REFACTORED: core/ai_gateway.py
class AIGateway:
    """
    Gateway principal del sistema AI-Native.

    Ahora es un orquestador ligero que delega a componentes especializados.
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        session_repo: SessionRepository,
        # ... repos
    ):
        # Initialize components
        self.cognitive_engine = CognitiveReasoningEngine(llm_provider)
        self.governance = GovernanceAgent()

        self.response_generator = ResponseGenerator(...)
        self.trace_manager = TraceManager(...)
        self.risk_analyzer = RiskAnalyzer(...)

    def process_interaction(
        self,
        session_id: str,
        student_id: str,
        activity_id: str,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesa una interacción estudiante-IA.

        Ahora es un método limpio de ~50 líneas que orquesta.
        """
        # 1. Classify
        classification = self.cognitive_engine.classify_interaction(prompt, context)

        # 2. Governance check
        governance_result = self.governance.check_compliance(classification)
        if governance_result["blocked"]:
            return self._build_blocked_response(governance_result)

        # 3. Capture input trace
        input_trace = self.trace_manager.capture_input_trace(
            session_id, student_id, prompt,
            classification["cognitive_state"], context
        )

        # 4. Generate response
        response = self.response_generator.generate_response(
            classification, context
        )

        # 5. Capture output trace
        output_trace = self.trace_manager.capture_output_trace(
            session_id, response,
            classification["agent"], classification["ai_involvement"]
        )

        # 6. Analyze risks (async, doesn't block)
        asyncio.create_task(
            self.risk_analyzer.analyze_interaction_risks(
                session_id, input_trace, output_trace, classification
            )
        )

        # 7. Build response
        return self._build_success_response(
            response, output_trace, classification
        )
```

**Beneficios de la refactorización**:
- ✅ AIGateway: 710 líneas → ~150 líneas
- ✅ Single Responsibility Principle
- ✅ Fácil testing individual de componentes
- ✅ Código más legible y mantenible
- ✅ Reducción de complejidad ciclomática

---

**C2. Eliminar code duplication (AIGateway ↔ TutorAgent)** ⏱️ 2 días
**Problema**: Lógica duplicada en routing y validación

**Solución**:
- Extraer lógica común a mixins o helpers
- Centralizar validaciones en schemas
- Usar herencia para comportamiento compartido

---

**C3. N+1 Query Prevention** ⏱️ 1 día
**Problema**: Conversión ORM → Pydantic puede generar queries adicionales

**Solución**:
```python
# repositories.py
def get_session_with_traces(self, session_id: str) -> SessionDB:
    """Obtiene sesión con eager loading de trazas."""
    return self.db.query(SessionDB).\
        options(
            selectinload(SessionDB.traces),
            selectinload(SessionDB.risks),
            selectinload(SessionDB.evaluations)
        ).\
        filter(SessionDB.id == session_id).\
        first()
```

---

**C4-C14: Otros problemas mayores**
- Tests unitarios (>80% coverage)
- Integration tests
- Performance benchmarking
- Load testing
- Security audit
- Accessibility compliance
- Documentation overhaul
- Monitoring integration
- Alerting setup
- Backup strategy
- Disaster recovery plan

---

## Recomendación de Orden de Ejecución

### Semana 1: Quick Wins (Categoría A)
**Días 1-2**:
- A1: Remover unused imports
- A2: Remover código comentado
- A3: Fix logging inconsistencies
- A4: Extraer magic numbers

**Días 3-5**:
- A5: Docstrings en métodos privados
- A6-A15: Otros quick wins

**Entregable**: 15 problemas resueltos, código más limpio

---

### Semana 2: Mejoras Medianas (Categoría B)
**Días 1-2**:
- B1: Type hints con TypedDict
- B2: Sanitizar mensajes de error

**Días 3-5**:
- B3: Extraer métodos de lógica compleja
- B4: Implementar _analyze_risks_async
- B5-B7: Rate limiting, connection pooling, memory limits

**Entregable**: 8 problemas resueltos, mejoras de type safety y performance

---

### Semana 3: Refactorizaciones Mayores (Categoría C)
**Días 1-3**:
- C1: Refactorizar AIGateway God Class (prioridad #1)
  - Día 1: Extraer ResponseGenerator
  - Día 2: Extraer TraceManager y RiskAnalyzer
  - Día 3: Refactorizar AIGateway, tests

**Días 4-5**:
- C2: Eliminar code duplication
- C3: N+1 Query prevention
- Tests de integración

**Entregable**: Arquitectura limpia, AIGateway refactorizado

---

### Semana 4 (Opcional): Testing & Polish
- Tests unitarios (>80% coverage)
- Performance benchmarking
- Documentation review
- Security audit
- Production readiness checklist

---

## Métricas de Éxito Sprint 3

| Métrica | Objetivo | Valor Actual |
|---------|----------|--------------|
| Problemas resueltos | 35+ / 41 | 0 |
| Test coverage | >80% | ~30% |
| Lines of code (AIGateway) | <200 | 710 |
| Cyclomatic complexity | <10 | ~25 |
| Type hints coverage | >90% | ~60% |
| Magic numbers | 0 | ~15 |
| Code duplication | <5% | ~15% |
| Performance (avg response) | <500ms | ~800ms |

---

## Conclusión

Sprint 3 es **opcional pero altamente recomendado**. El sistema ya es seguro y funcional, pero estas mejoras lo llevarán a un nivel enterprise-grade de calidad y mantenibilidad.

**Prioridad #1**: Refactorización de AIGateway God Class
**Prioridad #2**: Type hints con TypedDict
**Prioridad #3**: Tests unitarios >80% coverage

El resto de problemas se pueden abordar gradualmente según capacidad del equipo.

---

**Generado**: 2025-11-21
**Autor**: Mag. Alberto Cortez (con asistencia de Claude Code)
**Proyecto**: AI-Native MVP - Tesis Doctoral
