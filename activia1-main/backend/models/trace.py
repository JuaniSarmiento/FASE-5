"""
Modelos para el sistema de Trazabilidad Cognitiva N4
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TraceLevel(str, Enum):
    """Niveles de trazabilidad N1-N4"""
    N1_SUPERFICIAL = "n1_superficial"  # Archivos y entregas
    N2_TECNICO = "n2_tecnico"  # Commits y tests
    N3_INTERACCIONAL = "n3_interaccional"  # Prompts y respuestas
    N4_COGNITIVO = "n4_cognitivo"  # Razonamiento completo


class InteractionType(str, Enum):
    """Tipos de interacción humano-IA"""
    STUDENT_PROMPT = "student_prompt"
    AI_RESPONSE = "ai_response"
    CODE_COMMIT = "code_commit"
    TUTOR_INTERVENTION = "tutor_intervention"
    TEACHER_FEEDBACK = "teacher_feedback"
    STRATEGY_CHANGE = "strategy_change"
    HYPOTHESIS_FORMULATION = "hypothesis_formulation"
    SELF_CORRECTION = "self_correction"
    AI_CRITIQUE = "ai_critique"


class CognitiveState(str, Enum):
    """
    Estados cognitivos del estudiante durante el proceso de aprendizaje.

    FIX 4.1 Cortez5: Consolidated enum with both Spanish and English values
    for backwards compatibility. Database stores lowercase values.

    NOTE: This is the canonical enum for cognitive states. The enum in
    backend/api/schemas/enums.py is for API validation and uses UPPERCASE.

    Movido desde core.cognitive_engine para evitar dependencia circular
    (repositories no deben importar desde core).
    """
    # Estados principales (lowercase para BD)
    EXPLORACION = "exploracion"
    PLANIFICACION = "planificacion"
    IMPLEMENTACION = "implementacion"
    DEPURACION = "depuracion"
    VALIDACION = "validacion"
    REFLEXION = "reflexion"

    # Estados adicionales (FIX 4.1 Cortez5: Added from schema enum)
    CONFUSION = "confusion"
    PROGRESANDO = "progresando"
    ATASCADO = "atascado"

    # Aliases en inglés para compatibilidad con tests y API
    EXPLORATION = "exploracion"
    PLANNING = "planificacion"
    IMPLEMENTATION = "implementacion"
    DEBUGGING = "depuracion"
    VALIDATION = "validacion"
    REFLECTION = "reflexion"

    # Aliases adicionales para compatibilidad con API (FIX 4.1)
    CONFUSED = "confusion"
    EXPLORING = "exploracion"
    UNDERSTANDING = "exploracion"  # Maps to exploration
    IMPLEMENTING = "implementacion"
    STUCK = "atascado"
    PROGRESSING = "progresando"
    VALIDATING = "validacion"
    REFLECTING = "reflexion"

    # Alias adicional para estado inicial
    INICIO = "exploracion"


# FIX 4.1 Cortez5: Mapping for API values to DB values
COGNITIVE_STATE_API_TO_DB = {
    "CONFUSED": "confusion",
    "EXPLORING": "exploracion",
    "UNDERSTANDING": "exploracion",
    "IMPLEMENTING": "implementacion",
    "STUCK": "atascado",
    "PROGRESSING": "progresando",
    "VALIDATING": "validacion",
    "REFLECTING": "reflexion",
}


def normalize_cognitive_state(value: str) -> str:
    """
    FIX 4.1 Cortez5: Normalize cognitive state value for database storage.

    Converts API-style UPPERCASE values to DB-style lowercase values.

    Args:
        value: Cognitive state value (can be uppercase or lowercase)

    Returns:
        Normalized lowercase value for database storage
    """
    if value is None:
        return None
    upper_value = value.upper()
    if upper_value in COGNITIVE_STATE_API_TO_DB:
        return COGNITIVE_STATE_API_TO_DB[upper_value]
    return value.lower()


class CognitiveTrace(BaseModel):
    """
    Representa una traza cognitiva en el sistema N4.
    Captura el proceso completo de razonamiento híbrido humano-IA.

    FIX 3.1 Cortez8: Cambiado timestamp a created_at para consistencia con ORM.
    Se mantiene alias 'timestamp' para backwards compatibility.
    """
    id: str = Field(default="", description="Identificador único de la traza")
    session_id: str = Field(description="ID de la sesión")
    # FIX 3.1 Cortez8: Renombrado a created_at para consistencia con ORM
    created_at: datetime = Field(default_factory=datetime.now, alias="timestamp", description="Timestamp de creación")
    student_id: str = Field(description="ID del estudiante")
    activity_id: str = Field(description="ID de la actividad")

    # Niveles de trazabilidad
    trace_level: TraceLevel = Field(default=TraceLevel.N4_COGNITIVO, description="Nivel de trazabilidad (N1-N4)")
    interaction_type: InteractionType = Field(description="Tipo de interacción")

    # Contenido de la traza
    content: str = Field(description="Contenido de la interacción")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexto adicional")
    trace_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata adicional (use trace_metadata for ORM consistency)")

    # Análisis cognitivo (N4)
    cognitive_state: Optional[str] = Field(None, description="Estado cognitivo durante la interacción")
    cognitive_intent: Optional[str] = Field(None, description="Intención cognitiva detectada")
    decision_justification: Optional[str] = Field(None, description="Justificación de decisiones")
    alternatives_considered: List[str] = Field(default_factory=list, description="Alternativas consideradas")
    strategy_type: Optional[str] = Field(None, description="Tipo de estrategia utilizada")

    # AI Involvement
    ai_involvement: float = Field(default=0.0, ge=0.0, le=1.0, description="Nivel de involucramiento de IA (0-1)")

    # Metadata
    agent_id: Optional[str] = Field(None, description="ID del agente que generó la traza")
    parent_trace_id: Optional[str] = Field(None, description="Traza padre (para secuencias)")

    class Config:
        # FIX 3.1 Cortez8: Permitir usar alias 'timestamp' para backwards compatibility
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "trace_001",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "student_123",
                "activity_id": "prog2_tp1",
                "created_at": "2025-11-18T10:30:00Z",
                "trace_level": "n4_cognitivo",
                "interaction_type": "student_prompt",
                "content": "¿Cómo implemento una cola con arreglos?",
                "cognitive_intent": "comprension_estructura_datos",
                "alternatives_considered": ["lista_enlazada", "arreglo_circular"]
            }
        }


class TraceSequence(BaseModel):
    """
    Secuencia de trazas que representan un episodio cognitivo completo
    """
    id: str = Field(description="ID de la secuencia")
    session_id: str = Field(description="ID de la sesión")
    student_id: str = Field(description="ID del estudiante")
    activity_id: str = Field(description="ID de la actividad")
    traces: List[CognitiveTrace] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    # Análisis agregado
    reasoning_path: List[str] = Field(default_factory=list, description="Camino de razonamiento")
    strategy_changes: int = Field(0, description="Número de cambios de estrategia")
    ai_dependency_score: float = Field(0.0, description="Nivel de dependencia de IA (0-1)")

    def _recalculate_ai_dependency(self) -> None:
        """
        Recalcula el score de dependencia de IA basado en las trazas actuales.

        Extrae la lógica duplicada de calcular el promedio de ai_involvement.
        """
        if self.traces:
            total_involvement = sum(t.ai_involvement for t in self.traces)
            self.ai_dependency_score = total_involvement / len(self.traces)
        else:
            self.ai_dependency_score = 0.0

    def model_post_init(self, __context):
        """Calculate AI dependency score from traces after initialization"""
        self._recalculate_ai_dependency()

    def add_trace(self, trace: CognitiveTrace) -> None:
        """Añade una traza a la secuencia"""
        self.traces.append(trace)
        self.end_time = datetime.now()
        # Recalculate AI dependency using extracted method
        self._recalculate_ai_dependency()

    def get_cognitive_path(self) -> List[str]:
        """Reconstruye el camino cognitivo"""
        path = []
        for t in self.traces:
            if t.cognitive_state:
                path.append(f"{t.cognitive_state}")
            elif t.cognitive_intent:
                path.append(f"{t.cognitive_intent}")
        return path