# 📚 API Interna Reference - AI-Native MVP

## Documentación Completa de APIs Internas para Desarrolladores

Esta guía documenta todas las APIs internas (Python) del **Ecosistema AI-Native**, incluyendo clases, métodos, parámetros, retornos y ejemplos de uso. Es una referencia técnica para desarrolladores que extienden el sistema.

---

## 📚 Índice

1. [Introducción](#introducción)
2. [AIGateway (Orchestrator)](#aigateway-orchestrator)
3. [CognitiveEngine (CRPE)](#cognitiveengine-crpe)
4. [Agents (6 AI-Native Submodels)](#agents-6-ai-native-submodels)
5. [Models (Pydantic Domain Models)](#models-pydantic-domain-models)
6. [Repositories (Database Access)](#repositories-database-access)
7. [LLM Providers](#llm-providers)
8. [Utilities](#utilities)

---

## Introducción

### Convenciones de Documentación

```python
def example_function(
    param1: str,
    param2: int,
    optional_param: Optional[str] = None
) -> Dict[str, Any]:
    """
    Descripción breve de la función.

    Args:
        param1: Descripción del parámetro 1
        param2: Descripción del parámetro 2
        optional_param: Parámetro opcional, default None

    Returns:
        Diccionario con las claves:
            - 'result': Resultado del procesamiento
            - 'metadata': Información adicional

    Raises:
        ValueError: Si param2 es negativo
        DatabaseError: Si hay error de conexión

    Example:
        >>> result = example_function("test", 42)
        >>> print(result['result'])
        'success'
    """
    pass
```

---

## AIGateway (Orchestrator)

**Ubicación**: `src/ai_native_mvp/core/ai_gateway.py`

**Propósito**: Orquestador central que coordina los 6 componentes (C1-C6) y delega a agentes apropiados.

### Clase: `AIGateway`

```python
class AIGateway:
    """
    Gateway central del ecosistema AI-Native.

    Coordina:
    - C1: Motor LLM
    - C2: IPC (Prompt Ingestion)
    - C3: CRPE (Cognitive Reasoning)
    - C4: GSR (Governance, Security, Risk)
    - C5: OSM (Orchestration)
    - C6: N4 Traceability

    Attributes:
        llm_provider: Provider de LLM (OpenAI, Gemini, Mock)
        cognitive_engine: Motor de razonamiento cognitivo-pedagógico
        tutor: Agente T-IA-Cog
        evaluator: Agente E-IA-Proc
        simulators: Agente S-IA-X
        risk_analyst: Agente AR-IA
        governance: Agente GOV-IA
        traceability: Agente TC-N4
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        session_repo: Optional[SessionRepository] = None,
        trace_repo: Optional[TraceRepository] = None,
        risk_repo: Optional[RiskRepository] = None,
        evaluation_repo: Optional[EvaluationRepository] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa AIGateway.

        Args:
            llm_provider: Provider de LLM. Si None, usa factory desde .env
            session_repo: Repositorio de sesiones. Si None, crea uno nuevo
            trace_repo: Repositorio de trazas. Si None, crea uno nuevo
            risk_repo: Repositorio de riesgos. Si None, crea uno nuevo
            evaluation_repo: Repositorio de evaluaciones. Si None, crea uno nuevo
            config: Configuración adicional

        Example:
            >>> from src.ai_native_mvp import AIGateway
            >>> gateway = AIGateway()  # Usa defaults
            >>> # O con providers específicos:
            >>> gateway = AIGateway(
            ...     llm_provider=my_provider,
            ...     session_repo=my_session_repo
            ... )
        """
        pass
```

### Método: `process_interaction()`

```python
def process_interaction(
    self,
    session_id: str,
    student_id: str,
    activity_id: str,
    prompt: str,
    context: Optional[Dict[str, Any]] = None,
    cognitive_intent: Optional[str] = None
) -> Dict[str, Any]:
    """
    Procesa una interacción estudiante-IA (método principal).

    Flujo:
    1. Clasificar interacción (CRPE)
    2. Verificar gobernanza (GOV-IA)
    3. Capturar traza input (TC-N4)
    4. Delegar a agente apropiado (OSM)
    5. Capturar traza output (TC-N4)
    6. Analizar riesgos en paralelo (AR-IA)
    7. Retornar respuesta

    Args:
        session_id: ID de la sesión activa
        student_id: ID del estudiante
        activity_id: ID de la actividad
        prompt: Prompt del estudiante
        context: Contexto adicional (código, archivos, etc.)
        cognitive_intent: Intención cognitiva explícita del estudiante
                          (ej: "UNDERSTANDING", "PLANNING", "IMPLEMENTING")

    Returns:
        Diccionario con:
            - 'response': Respuesta pedagógica del agente
            - 'agent_used': Nombre del agente que procesó (ej: "T-IA-Cog")
            - 'cognitive_state': Estado cognitivo detectado
            - 'ai_involvement': Nivel de involucramiento de IA (0.0-1.0)
            - 'blocked': True si fue bloqueado por gobernanza
            - 'trace_id': ID de la traza generada
            - 'risks_detected': Lista de riesgos detectados

    Raises:
        SessionNotFoundError: Si session_id no existe
        GovernanceBlockError: Si la solicitud viola políticas institucionales
        AgentNotAvailableError: Si el agente requerido no está disponible

    Example:
        >>> result = gateway.process_interaction(
        ...     session_id="session_123",
        ...     student_id="student_001",
        ...     activity_id="prog2_tp1",
        ...     prompt="¿Cómo implemento una cola circular?",
        ...     cognitive_intent="UNDERSTANDING"
        ... )
        >>> print(result['response'])
        'Una cola circular es una estructura de datos...'
        >>> print(result['ai_involvement'])
        0.35
    """
    pass
```

### Método: `create_session()`

```python
def create_session(
    self,
    student_id: str,
    activity_id: str,
    mode: str = "TUTOR"
) -> Dict[str, Any]:
    """
    Crea una nueva sesión de aprendizaje.

    Args:
        student_id: ID del estudiante
        activity_id: ID de la actividad
        mode: Modo de la sesión:
              - "TUTOR": Tutor cognitivo (default)
              - "EVALUATOR": Evaluación de procesos
              - "SIMULATOR": Simulador profesional (PO, SM, etc.)

    Returns:
        Diccionario con:
            - 'session_id': ID de la sesión creada
            - 'student_id': ID del estudiante
            - 'activity_id': ID de la actividad
            - 'mode': Modo de la sesión
            - 'start_time': Timestamp de inicio
            - 'status': Estado ('ACTIVE')

    Raises:
        ValidationError: Si algún parámetro es inválido

    Example:
        >>> session = gateway.create_session(
        ...     student_id="student_001",
        ...     activity_id="prog2_tp1",
        ...     mode="TUTOR"
        ... )
        >>> print(session['session_id'])
        'session_abc123def456'
    """
    pass
```

### Método: `end_session()`

```python
def end_session(self, session_id: str) -> Dict[str, Any]:
    """
    Finaliza una sesión y genera evaluación de proceso.

    Args:
        session_id: ID de la sesión a finalizar

    Returns:
        Diccionario con:
            - 'session_id': ID de la sesión
            - 'status': 'COMPLETED'
            - 'end_time': Timestamp de finalización
            - 'duration_minutes': Duración en minutos
            - 'evaluation': Evaluación generada por E-IA-Proc (si aplica)

    Raises:
        SessionNotFoundError: Si session_id no existe

    Example:
        >>> result = gateway.end_session("session_123")
        >>> print(result['evaluation']['overall_competency_level'])
        'EN_DESARROLLO'
    """
    pass
```

### Método: `get_cognitive_path()`

```python
def get_cognitive_path(self, session_id: str) -> Dict[str, Any]:
    """
    Reconstruye el camino cognitivo completo de una sesión.

    Args:
        session_id: ID de la sesión

    Returns:
        Diccionario con:
            - 'session_id': ID de la sesión
            - 'phases': Lista de fases cognitivas:
                - 'phase_name': Nombre de la fase (ej: "EXPLORACION")
                - 'start_time': Inicio de la fase
                - 'end_time': Fin de la fase
                - 'interactions': Cantidad de interacciones
                - 'ai_involvement': Involucramiento IA promedio
                - 'risks': Riesgos detectados en esta fase
            - 'state_transitions': Lista de transiciones de estado
            - 'overall_ai_dependency': Dependencia IA promedio global
            - 'self_corrections': Cantidad de autocorrecciones

    Example:
        >>> path = gateway.get_cognitive_path("session_123")
        >>> for phase in path['phases']:
        ...     print(f"{phase['phase_name']}: {phase['interactions']} interactions")
        EXPLORACION: 3 interactions
        PLANIFICACION: 2 interactions
        IMPLEMENTACION: 5 interactions
    """
    pass
```

---

## CognitiveEngine (CRPE)

**Ubicación**: `src/ai_native_mvp/core/cognitive_engine.py`

**Propósito**: Motor de Razonamiento Cognitivo-Pedagógico (Cognitive-Pedagogical Reasoning Engine).

### Clase: `CognitiveEngine`

```python
class CognitiveEngine:
    """
    Motor de razonamiento cognitivo-pedagógico (CRPE).

    Clasifica interacciones y detecta estados cognitivos.
    """

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """
        Inicializa el motor cognitivo.

        Args:
            llm_provider: Provider de LLM para clasificación semántica
        """
        pass

    def classify_interaction(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Clasifica una interacción estudiante-IA.

        Args:
            prompt: Prompt del estudiante
            context: Contexto adicional (código, historial, etc.)

        Returns:
            Diccionario con:
                - 'cognitive_state': Estado cognitivo detectado (enum CognitiveState)
                - 'cognitive_intent': Intención cognitiva (ej: "UNDERSTANDING")
                - 'request_type': Tipo de solicitud (ej: "CONCEPTUAL_QUERY")
                - 'requires_justification': True si requiere justificación
                - 'complexity_level': Nivel de complejidad (1-5)
                - 'confidence': Confianza de la clasificación (0.0-1.0)

        Example:
            >>> result = engine.classify_interaction(
            ...     "¿Qué es una cola circular?",
            ...     context={'previous_interactions': 0}
            ... )
            >>> print(result['cognitive_state'])
            CognitiveState.EXPLORACION_CONCEPTUAL
        """
        pass

    def detect_cognitive_state(
        self,
        prompt: str,
        previous_states: List[str]
    ) -> CognitiveState:
        """
        Detecta el estado cognitivo del estudiante.

        Estados posibles (CognitiveState enum):
        - EXPLORACION_CONCEPTUAL: Explorando conceptos
        - PLANIFICACION: Planificando solución
        - IMPLEMENTACION: Implementando código
        - VALIDACION: Validando solución
        - DEPURACION: Debugging
        - REFLEXION: Reflexión metacognitiva

        Args:
            prompt: Prompt del estudiante
            previous_states: Estados cognitivos previos (historial)

        Returns:
            CognitiveState detectado

        Example:
            >>> state = engine.detect_cognitive_state(
            ...     "Implementé enqueue() así: [código]",
            ...     previous_states=[
            ...         'EXPLORACION_CONCEPTUAL',
            ...         'PLANIFICACION'
            ...     ]
            ... )
            >>> print(state)
            CognitiveState.IMPLEMENTACION
        """
        pass
```

### Enum: `CognitiveState`

```python
from enum import Enum

class CognitiveState(str, Enum):
    """
    Estados cognitivos del estudiante en el proceso de aprendizaje.
    """
    EXPLORACION_CONCEPTUAL = "EXPLORACION_CONCEPTUAL"
    """Explorando conceptos y definiciones"""

    PLANIFICACION = "PLANIFICACION"
    """Planificando diseño y arquitectura de solución"""

    IMPLEMENTACION = "IMPLEMENTACION"
    """Implementando código"""

    VALIDACION = "VALIDACION"
    """Validando y testeando solución"""

    DEPURACION = "DEPURACION"
    """Debugging y corrección de errores"""

    REFLEXION = "REFLEXION"
    """Reflexión metacognitiva sobre el proceso"""

    ESTANCAMIENTO = "ESTANCAMIENTO"
    """Estudiante estancado, requiere intervención"""
```

---

## Agents (6 AI-Native Submodels)

### T-IA-Cog: Tutor Cognitivo

**Ubicación**: `src/ai_native_mvp/agents/tutor.py`

```python
class TutorCognitivoAgent:
    """
    T-IA-Cog: Tutor Cognitivo Disciplinar

    Propósito: Guiar razonamiento sin sustituir agencia cognitiva.

    Modos de operación:
    - SOCRATICO: Preguntas socráticas
    - EXPLICATIVO: Explicaciones conceptuales
    - GUIADO: Pistas graduadas
    - METACOGNITIVO: Reflexión sobre proceso
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa el tutor cognitivo.

        Args:
            llm_provider: Provider de LLM
            config: Configuración:
                - 'max_help_level': Nivel máximo de ayuda
                - 'require_justification': Exigir justificaciones
        """
        pass

    def respond(
        self,
        prompt: str,
        cognitive_state: CognitiveState,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera respuesta pedagógica.

        Args:
            prompt: Prompt del estudiante
            cognitive_state: Estado cognitivo detectado
            context: Contexto (código, historial, etc.)

        Returns:
            Respuesta pedagógica del tutor

        Example:
            >>> response = tutor.respond(
            ...     "¿Cómo implemento enqueue()?",
            ...     CognitiveState.IMPLEMENTACION,
            ...     context={'previous_attempts': 2}
            ... )
            >>> print(response)
            '¿Qué deberías verificar antes de insertar un elemento?'
        """
        pass

    def generate_socratic_question(
        self,
        topic: str,
        student_statement: str
    ) -> str:
        """
        Genera pregunta socrática para promover razonamiento.

        Args:
            topic: Tema de la pregunta
            student_statement: Afirmación del estudiante

        Returns:
            Pregunta socrática

        Example:
            >>> question = tutor.generate_socratic_question(
            ...     topic="cola circular",
            ...     student_statement="Voy a usar un arreglo"
            ... )
            >>> print(question)
            '¿Por qué elegiste un arreglo en lugar de una lista enlazada?'
        """
        pass
```

### E-IA-Proc: Evaluador de Procesos

**Ubicación**: `src/ai_native_mvp/agents/evaluator.py`

```python
class EvaluadorProcesoAgent:
    """
    E-IA-Proc: Evaluador de Procesos Cognitivos

    Propósito: Evaluar el PROCESO de razonamiento, no solo el producto final.

    Dimensiones evaluadas:
    - Descomposición de problemas
    - Autorregulación y metacognición
    - Coherencia lógica
    - Verificación y testing
    - Documentación del razonamiento
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        pass

    def evaluate_session(
        self,
        session_id: str,
        traces: List[CognitiveTrace]
    ) -> EvaluationReport:
        """
        Evalúa el proceso cognitivo de una sesión completa.

        Args:
            session_id: ID de la sesión
            traces: Trazas cognitivas de la sesión

        Returns:
            EvaluationReport con:
                - overall_competency_level: Nivel de competencia (INICIAL, EN_DESARROLLO, etc.)
                - overall_score: Puntaje global (0-10)
                - dimensions: Puntajes por dimensión
                - key_strengths: Fortalezas identificadas
                - improvement_areas: Áreas de mejora
                - recommendations: Recomendaciones accionables

        Example:
            >>> evaluation = evaluator.evaluate_session(
            ...     session_id="session_123",
            ...     traces=traces
            ... )
            >>> print(evaluation.overall_competency_level)
            'EN_DESARROLLO'
            >>> print(evaluation.overall_score)
            6.5
        """
        pass

    def analyze_decomposition(
        self,
        traces: List[CognitiveTrace]
    ) -> float:
        """
        Analiza la capacidad de descomposición de problemas.

        Args:
            traces: Trazas cognitivas

        Returns:
            Puntaje 0.0-10.0

        Example:
            >>> score = evaluator.analyze_decomposition(traces)
            >>> print(score)
            7.5
        """
        pass
```

### S-IA-X: Simuladores Profesionales

**Ubicación**: `src/ai_native_mvp/agents/simulators.py`

```python
class SimuladorProfesionalAgent:
    """
    S-IA-X: Simuladores Profesionales

    Simuladores disponibles:
    - PO-IA: Product Owner
    - SM-IA: Scrum Master
    - IT-IA: Technical Interviewer
    - IR-IA: Incident Responder (DevOps)
    - CX-IA: Cliente (ambiguous requirements)
    - DSO-IA: DevSecOps
    """

    def __init__(
        self,
        simulator_type: str,
        llm_provider: Optional[LLMProvider] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa simulador.

        Args:
            simulator_type: Tipo de simulador (ej: "PO", "SM", "IT")
            llm_provider: Provider de LLM
            config: Configuración específica del simulador
        """
        pass

    def simulate_interaction(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Simula interacción profesional.

        Args:
            prompt: Prompt del estudiante
            context: Contexto de la simulación

        Returns:
            Respuesta del rol simulado

        Example:
            >>> po = SimuladorProfesionalAgent(simulator_type="PO")
            >>> response = po.simulate_interaction(
            ...     "¿Cuáles son los requisitos del sistema?",
            ...     context={'sprint': 1}
            ... )
            >>> print(response)
            'Como PO, necesito que el sistema permita...'
        """
        pass
```

### AR-IA: Analista de Riesgos

**Ubicación**: `src/ai_native_mvp/agents/risk_analyst.py`

```python
class AnalistaRiesgosAgent:
    """
    AR-IA: Analista de Riesgos Cognitivos y Éticos

    Detecta 5 dimensiones de riesgo:
    1. Cognitivo (RC): Delegación, dependencia IA
    2. Ético (RE): Integridad académica, plagio
    3. Epistémico (REp): Errores conceptuales, aceptación acrítica
    4. Técnico (RT): Vulnerabilidades, código inseguro
    5. Gobernanza (RG): Violaciones de políticas
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        pass

    def analyze_risks(
        self,
        session_id: str,
        traces: List[CognitiveTrace],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Risk]:
        """
        Analiza riesgos en una sesión.

        Args:
            session_id: ID de la sesión
            traces: Trazas cognitivas
            context: Contexto adicional

        Returns:
            Lista de riesgos detectados (Risk objects)

        Example:
            >>> risks = analyst.analyze_risks(
            ...     session_id="session_123",
            ...     traces=traces
            ... )
            >>> for risk in risks:
            ...     print(f"{risk.risk_type}: {risk.risk_level}")
            COGNITIVE_DELEGATION: HIGH
        """
        pass

    def detect_total_delegation(self, prompt: str) -> bool:
        """
        Detecta si el prompt implica delegación total.

        Patrones detectados:
        - "Dame el código completo"
        - "Resolvelo vos"
        - "Implementa todo"

        Args:
            prompt: Prompt del estudiante

        Returns:
            True si es delegación total

        Example:
            >>> is_delegation = analyst.detect_total_delegation(
            ...     "Dame el código completo de la cola"
            ... )
            >>> print(is_delegation)
            True
        """
        pass
```

### GOV-IA: Gobernanza

**Ubicación**: `src/ai_native_mvp/agents/governance.py`

```python
class GobernanzaAgent:
    """
    GOV-IA: Agente de Gobernanza Institucional

    Propósito: Operacionalizar políticas institucionales de IA.

    Políticas verificadas:
    - Nivel máximo de ayuda permitido
    - Bloqueo de soluciones completas
    - Exigencia de justificaciones
    - Umbrales de riesgo
    """

    def __init__(self, policies: Optional[Dict[str, Any]] = None):
        """
        Inicializa agente de gobernanza.

        Args:
            policies: Políticas institucionales:
                - 'max_help_level': Nivel máximo de ayuda
                - 'block_complete_solutions': True/False
                - 'require_justification': True/False
                - 'risk_thresholds': Umbrales de riesgo
        """
        pass

    def check_compliance(
        self,
        prompt: str,
        cognitive_state: CognitiveState,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Verifica cumplimiento de políticas institucionales.

        Args:
            prompt: Prompt del estudiante
            cognitive_state: Estado cognitivo
            context: Contexto adicional

        Returns:
            Diccionario con:
                - 'allowed': True si la solicitud es permitida
                - 'blocked_reason': Razón del bloqueo (si blocked=True)
                - 'policy_violated': Política violada
                - 'recommendations': Recomendaciones para reformular

        Raises:
            GovernanceBlockError: Si la solicitud está bloqueada

        Example:
            >>> result = governance.check_compliance(
            ...     "Dame el código completo",
            ...     CognitiveState.IMPLEMENTACION
            ... )
            >>> print(result['allowed'])
            False
            >>> print(result['blocked_reason'])
            'Delegación total detectada'
        """
        pass
```

### TC-N4: Trazabilidad N4

**Ubicación**: `src/ai_native_mvp/agents/traceability.py`

```python
class TrazabilidadN4Agent:
    """
    TC-N4: Trazabilidad Cognitiva de Nivel N4

    Propósito: Capturar proceso cognitivo completo (N4).

    Niveles de trazabilidad:
    - N1: Superficial (archivos finales)
    - N2: Técnico (commits Git)
    - N3: Interaccional (prompts, respuestas)
    - N4: Cognitivo Completo (intención, decisiones, justificaciones)
    """

    def __init__(
        self,
        trace_repo: Optional[TraceRepository] = None,
        sequence_repo: Optional[TraceSequenceRepository] = None
    ):
        pass

    def capture_trace(
        self,
        session_id: str,
        student_id: str,
        activity_id: str,
        trace_level: str,
        interaction_type: str,
        content: str,
        cognitive_state: Optional[CognitiveState] = None,
        cognitive_intent: Optional[str] = None,
        ai_involvement: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CognitiveTrace:
        """
        Captura una traza cognitiva.

        Args:
            session_id: ID de la sesión
            student_id: ID del estudiante
            activity_id: ID de la actividad
            trace_level: Nivel de traza (N1, N2, N3, N4)
            interaction_type: Tipo de interacción (STUDENT_PROMPT, AI_RESPONSE, etc.)
            content: Contenido de la traza
            cognitive_state: Estado cognitivo
            cognitive_intent: Intención cognitiva
            ai_involvement: Nivel de involucramiento IA (0.0-1.0)
            metadata: Metadata adicional

        Returns:
            CognitiveTrace creada

        Example:
            >>> trace = traceability.capture_trace(
            ...     session_id="session_123",
            ...     student_id="student_001",
            ...     activity_id="prog2_tp1",
            ...     trace_level="N4_COGNITIVO",
            ...     interaction_type="STUDENT_PROMPT",
            ...     content="¿Cómo implemento enqueue()?",
            ...     cognitive_state=CognitiveState.IMPLEMENTACION,
            ...     ai_involvement=0.4
            ... )
            >>> print(trace.id)
            'trace_abc123'
        """
        pass

    def reconstruct_cognitive_path(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Reconstruye el camino cognitivo desde trazas.

        Args:
            session_id: ID de la sesión

        Returns:
            Diccionario con el camino cognitivo reconstructed

        Example:
            >>> path = traceability.reconstruct_cognitive_path("session_123")
            >>> print(path['phases'])
            [
                {'phase': 'EXPLORACION', 'duration': 600, ...},
                {'phase': 'IMPLEMENTACION', 'duration': 1200, ...}
            ]
        """
        pass
```

---

## Models (Pydantic Domain Models)

### CognitiveTrace

**Ubicación**: `src/ai_native_mvp/models/trace.py`

```python
class CognitiveTrace(BaseModel):
    """
    Traza cognitiva N4.

    Representa una captura del proceso cognitivo en un momento específico.
    """
    id: str = Field(default_factory=lambda: f"trace_{uuid4().hex[:12]}")
    session_id: str
    student_id: str
    activity_id: str

    # Nivel de trazabilidad
    trace_level: TraceLevel
    interaction_type: InteractionType

    # Contenido
    content: str
    code_snippet: Optional[str] = None

    # Cognitivo
    cognitive_state: Optional[CognitiveState] = None
    cognitive_intent: Optional[str] = None

    # Involucramiento IA
    ai_involvement: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Nivel de involucramiento de IA (0=solo estudiante, 1=solo IA)"
    )

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(use_enum_values=True)
```

### Risk

**Ubicación**: `src/ai_native_mvp/models/risk.py`

```python
class Risk(BaseModel):
    """
    Riesgo detectado en interacción humano-IA.
    """
    id: str = Field(default_factory=lambda: f"risk_{uuid4().hex[:12]}")
    session_id: Optional[str] = None
    student_id: str
    activity_id: str

    # Tipo y nivel
    risk_type: RiskType
    risk_level: RiskLevel
    dimension: RiskDimension

    # Detalles
    description: str
    evidence: List[str] = Field(default_factory=list)
    trace_ids: List[str] = Field(default_factory=list)

    # Recomendaciones
    recommendations: List[str] = Field(default_factory=list)

    # Resolución
    resolved: bool = False
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.now)
```

### EvaluationReport

**Ubicación**: `src/ai_native_mvp/models/evaluation.py`

```python
class EvaluationReport(BaseModel):
    """
    Reporte de evaluación de proceso cognitivo.
    """
    id: str = Field(default_factory=lambda: f"eval_{uuid4().hex[:12]}")
    session_id: str
    student_id: str
    activity_id: str

    # Evaluación global
    overall_competency_level: CompetencyLevel
    overall_score: float = Field(ge=0.0, le=10.0)

    # Dimensiones (5 dimensiones evaluadas)
    dimensions: Dict[str, EvaluationDimension]

    # Feedback
    key_strengths: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    # Análisis
    reasoning_analysis: Optional[str] = None
    git_analysis: Optional[Dict[str, Any]] = None
    ai_dependency_metrics: Optional[Dict[str, float]] = None

    created_at: datetime = Field(default_factory=datetime.now)
```

---

## Repositories (Database Access)

### SessionRepository

**Ubicación**: `src/ai_native_mvp/database/repositories.py`

```python
class SessionRepository:
    """
    Repository para operaciones CRUD de sesiones.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        student_id: str,
        activity_id: str,
        mode: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionDB:
        """
        Crea una nueva sesión.

        Args:
            student_id: ID del estudiante
            activity_id: ID de la actividad
            mode: Modo de la sesión (TUTOR, EVALUATOR, SIMULATOR)
            metadata: Metadata adicional

        Returns:
            SessionDB creada

        Example:
            >>> session = session_repo.create(
            ...     student_id="student_001",
            ...     activity_id="prog2_tp1",
            ...     mode="TUTOR"
            ... )
            >>> print(session.id)
            'session_abc123'
        """
        pass

    def get(self, session_id: str) -> Optional[SessionDB]:
        """Obtiene sesión por ID"""
        pass

    def get_by_student(
        self,
        student_id: str,
        status: Optional[str] = None
    ) -> List[SessionDB]:
        """Obtiene sesiones de un estudiante"""
        pass

    def end_session(self, session_id: str) -> SessionDB:
        """Finaliza una sesión"""
        pass
```

### TraceRepository

```python
class TraceRepository:
    """Repository para trazas cognitivas"""

    def create(self, trace: CognitiveTrace) -> CognitiveTraceDB:
        """Crea nueva traza"""
        pass

    def get_by_session(
        self,
        session_id: str,
        trace_level: Optional[str] = None
    ) -> List[CognitiveTraceDB]:
        """Obtiene trazas de una sesión"""
        pass

    def count_by_student(
        self,
        student_id: str,
        interaction_type: Optional[str] = None
    ) -> int:
        """Cuenta trazas de un estudiante"""
        pass
```

---

## LLM Providers

### Base Interface

**Ubicación**: `src/ai_native_mvp/llm/base.py`

```python
class LLMProvider(ABC):
    """
    Interfaz base para proveedores de LLM.

    Implementaciones:
    - MockLLMProvider: Mock para testing
    - OpenAIProvider: OpenAI (GPT-4, GPT-3.5)
    - GeminiProvider: Google Gemini
    - AnthropicProvider: Anthropic Claude
    """

    @abstractmethod
    def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> LLMResponse:
        """
        Genera respuesta del LLM.

        Args:
            messages: Lista de mensajes (rol, contenido)
            temperature: Temperatura (0.0-1.0)
            max_tokens: Máximo de tokens en respuesta

        Returns:
            LLMResponse con contenido y metadata

        Example:
            >>> messages = [
            ...     LLMMessage(role=LLMRole.SYSTEM, content="Eres un tutor"),
            ...     LLMMessage(role=LLMRole.USER, content="¿Qué es una cola?")
            ... ]
            >>> response = provider.generate(messages)
            >>> print(response.content)
            'Una cola es una estructura de datos...'
        """
        pass

    @abstractmethod
    def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Iterator[str]:
        """Genera respuesta en streaming"""
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Cuenta tokens en un texto"""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Valida configuración del provider"""
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna información del modelo"""
        pass
```

---

## Utilities

### Transaction Management

**Ubicación**: `src/ai_native_mvp/database/transaction.py`

```python
@contextmanager
def transaction(
    session: Session,
    description: str = "Database transaction"
) -> Generator[Session, None, None]:
    """
    Context manager para transacciones atómicas.

    Args:
        session: SQLAlchemy session
        description: Descripción de la transacción (para logging)

    Yields:
        Session activa

    Example:
        >>> from src.ai_native_mvp.database import get_db_session, transaction
        >>> with get_db_session() as db:
        ...     with transaction(db, "Create session and traces"):
        ...         session_repo.create(...)
        ...         trace_repo.create(...)
        ...         # Auto-commit si todo OK, rollback si exception
    """
    pass


def transactional(description: str = ""):
    """
    Decorator para funciones transaccionales.

    Example:
        >>> @transactional("Process interaction")
        ... def process_and_save(db, ...):
        ...     # All operations are atomic
        ...     session_repo.create(...)
        ...     trace_repo.create(...)
    """
    pass
```

### Cache Management

**Ubicación**: `src/ai_native_mvp/core/cache.py`

```python
class LLMCache:
    """
    Cache LRU con TTL para respuestas de LLM.

    Reduce costos y latencia al cachear respuestas repetidas.
    """

    def __init__(
        self,
        max_entries: int = 1000,
        ttl_seconds: int = 3600,
        backend: str = 'memory'
    ):
        """
        Inicializa cache.

        Args:
            max_entries: Máximo de entradas en cache
            ttl_seconds: Time-to-live en segundos
            backend: Backend ('memory' o 'redis')
        """
        pass

    def get(self, key: str) -> Optional[str]:
        """Obtiene valor del cache"""
        pass

    def set(self, key: str, value: str, ttl: Optional[int] = None):
        """Guarda valor en cache"""
        pass

    def clear(self):
        """Limpia todo el cache"""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas del cache.

        Returns:
            Dict con:
                - 'hits': Cantidad de hits
                - 'misses': Cantidad de misses
                - 'hit_rate': Tasa de hits (0.0-1.0)
                - 'size': Cantidad de entradas actuales
        """
        pass
```

---

## Ejemplos de Uso Completos

### Ejemplo 1: Procesar Interacción Completa

```python
from src.ai_native_mvp import AIGateway
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import SessionRepository

# Inicializar
with get_db_session() as db:
    session_repo = SessionRepository(db)

    # Crear sesión
    session = session_repo.create(
        student_id="student_001",
        activity_id="prog2_tp1",
        mode="TUTOR"
    )

# Procesar interacción
gateway = AIGateway()
result = gateway.process_interaction(
    session_id=session.id,
    student_id="student_001",
    activity_id="prog2_tp1",
    prompt="¿Cómo implemento una cola circular?",
    cognitive_intent="UNDERSTANDING"
)

print(f"Respuesta: {result['response']}")
print(f"Agente: {result['agent_used']}")
print(f"AI Involvement: {result['ai_involvement']}")
```

### Ejemplo 2: Evaluar Sesión Completa

```python
from src.ai_native_mvp.core.ai_gateway import AIGateway
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import TraceRepository

gateway = AIGateway()

# Finalizar sesión (genera evaluación automática)
result = gateway.end_session("session_123")

evaluation = result['evaluation']
print(f"Nivel: {evaluation.overall_competency_level}")
print(f"Score: {evaluation.overall_score}")
print(f"\nFortalezas:")
for strength in evaluation.key_strengths:
    print(f"  - {strength}")
print(f"\nÁreas de mejora:")
for area in evaluation.improvement_areas:
    print(f"  - {area}")
```

### Ejemplo 3: Análisis de Riesgos

```python
from src.ai_native_mvp.agents.risk_analyst import AnalistaRiesgosAgent
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import TraceRepository

# Obtener trazas
with get_db_session() as db:
    trace_repo = TraceRepository(db)
    traces = trace_repo.get_by_session("session_123")

# Analizar riesgos
analyst = AnalistaRiesgosAgent()
risks = analyst.analyze_risks(
    session_id="session_123",
    traces=traces
)

print(f"Riesgos detectados: {len(risks)}")
for risk in risks:
    print(f"  - {risk.risk_type}: {risk.risk_level}")
    print(f"    {risk.description}")
```

---

## Changelog de API

### v0.1.0 (2025-11-19)
- Release inicial con 6 agentes
- API REST completa
- Trazabilidad N4

### v0.2.0 (Futuro)
- Agregar streaming para respuestas LLM
- Soporte para múltiples idiomas
- Webhooks para eventos

---

**API Reference completa! 📚**

**Mag. en Ing. de Software Alberto Cortez**
Universidad Tecnológica Nacional