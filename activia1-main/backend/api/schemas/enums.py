"""
Enumeraciones para validación de schemas de la API
"""
from enum import Enum
from ...core.cognitive_engine import AgentMode

# DEPRECATED: Use AgentMode from cognitive_engine instead
# Mantener por compatibilidad temporal, pero usar AgentMode en código nuevo
SessionMode = AgentMode  # Alias for backward compatibility


class SessionStatus(str, Enum):
    """
    Estados de sesión válidos.
    FIX 1.4 Cortez7: Agregado ABANDONED para consistencia con check constraint en DB.
    """
    ACTIVE = "active"
    COMPLETED = "completed"
    ABORTED = "aborted"
    PAUSED = "paused"
    ABANDONED = "abandoned"  # FIX 1.4 Cortez7: Agregado para consistencia con DB


class CognitiveIntent(str, Enum):
    """Intenciones cognitivas del estudiante"""
    UNDERSTANDING = "UNDERSTANDING"  # Busca entender conceptos
    EXPLORATION = "EXPLORATION"  # Explora posibilidades
    PLANNING = "PLANNING"  # Planifica solución
    IMPLEMENTATION = "IMPLEMENTATION"  # Implementa código
    DEBUGGING = "DEBUGGING"  # Depura errores
    VALIDATION = "VALIDATION"  # Valida solución
    REFLECTION = "REFLECTION"  # Reflexiona sobre proceso
    UNKNOWN = "UNKNOWN"  # No determinado


# ==================== ACTIVITY ENUMS ====================

class ActivityDifficulty(str, Enum):
    """
    Niveles de dificultad de actividades

    Alineado con frontend ActivityDifficulty
    Valores en UPPERCASE para consistencia con otras enums del sistema
    """
    INICIAL = "INICIAL"       # Nivel principiante
    INTERMEDIO = "INTERMEDIO" # Nivel intermedio
    AVANZADO = "AVANZADO"     # Nivel avanzado


class ActivityStatus(str, Enum):
    """
    Estados del ciclo de vida de una actividad

    Alineado con frontend ActivityStatus
    Valores en lowercase para consistencia con SessionStatus
    """
    DRAFT = "draft"       # Borrador, no visible para estudiantes
    ACTIVE = "active"     # Publicada y activa
    ARCHIVED = "archived" # Archivada, no disponible


class HelpLevel(str, Enum):
    """
    Niveles de ayuda máxima permitida en políticas pedagógicas

    Alineado con frontend HelpLevel
    Valores en lowercase para consistencia con otras enums de políticas
    """
    MINIMO = "minimo"  # Solo hints muy generales
    BAJO = "bajo"      # Hints y preguntas guía
    MEDIO = "medio"    # Explicaciones conceptuales
    ALTO = "alto"      # Ayuda detallada pero sin soluciones completas


class SimulatorType(str, Enum):
    """
    Tipos de simulador profesional (S-IA-X)

    Alineado con frontend SimulatorType
    Valores en lowercase para consistencia con base de datos
    """
    PRODUCT_OWNER = "product_owner"          # Simulador de Product Owner
    SCRUM_MASTER = "scrum_master"            # Simulador de Scrum Master
    TECH_INTERVIEWER = "tech_interviewer"    # Simulador de entrevista técnica
    INCIDENT_RESPONDER = "incident_responder"  # Simulador de respuesta a incidentes
    CLIENT = "client"                        # Simulador de cliente
    DEVSECOPS = "devsecops"                  # Simulador DevSecOps


# ==================== RISK ENUMS (FIX 3.1) ====================

class RiskLevel(str, Enum):
    """
    Niveles de riesgo detectados por AR-IA
    Valores en lowercase para consistencia con base de datos
    """
    INFO = "info"          # Informativo, sin acción requerida
    LOW = "low"            # Riesgo bajo
    MEDIUM = "medium"      # Riesgo medio
    HIGH = "high"          # Riesgo alto
    CRITICAL = "critical"  # Riesgo crítico, requiere atención inmediata


class RiskDimension(str, Enum):
    """
    Dimensiones de riesgo del modelo 5D de AR-IA
    FIX 2.1 Cortez4: Values in lowercase for consistency with domain model (backend/models/risk.py)
    """
    COGNITIVE = "cognitive"      # Riesgo cognitivo (delegación de pensamiento)
    ETHICAL = "ethical"          # Riesgo ético (plagio, integridad académica)
    EPISTEMIC = "epistemic"      # Riesgo epistémico (conocimiento superficial)
    TECHNICAL = "technical"      # Riesgo técnico (mala calidad de código)
    GOVERNANCE = "governance"    # Riesgo de gobernanza (políticas, auditoría)


# ==================== TRACE ENUMS (FIX 3.1) ====================
# FIX 1.3 Cortez7: Reexportar TraceLevel desde domain model para evitar duplicación
from backend.models.trace import TraceLevel  # noqa: F401 - Reexported


class CognitiveState(str, Enum):
    """
    Estados cognitivos del estudiante durante la interacción.

    FIX 1.1 Cortez7: Estos valores son para API validation.
    El canonical source está en backend/models/trace.py con lowercase values.
    Usar COGNITIVE_STATE_API_TO_DB para convertir antes de guardar en DB.
    """
    CONFUSED = "CONFUSED"          # Confundido -> DB: "confusion"
    EXPLORING = "EXPLORING"        # Explorando opciones -> DB: "exploracion"
    UNDERSTANDING = "UNDERSTANDING"  # Entendiendo conceptos -> DB: "exploracion"
    IMPLEMENTING = "IMPLEMENTING"  # Implementando solución -> DB: "implementacion"
    STUCK = "STUCK"                # Atascado -> DB: "atascado"
    PROGRESSING = "PROGRESSING"    # Progresando -> DB: "progresando"
    VALIDATING = "VALIDATING"      # Validando solución -> DB: "validacion"
    REFLECTING = "REFLECTING"      # Reflexionando -> DB: "reflexion"


# FIX 1.1 Cortez7: Mapping API -> DB values for CognitiveState
# Import canonical mapping from domain model
from backend.models.trace import COGNITIVE_STATE_API_TO_DB, normalize_cognitive_state  # noqa: F401


class InteractionType(str, Enum):
    """
    Tipos de interacción estudiante-IA (API format).

    FIX 1.2 Cortez7: Valores para API validation.
    Usar INTERACTION_TYPE_API_TO_DB para convertir a valores de domain model.
    """
    QUESTION = "QUESTION"              # Pregunta del estudiante
    RESPONSE = "RESPONSE"              # Respuesta de IA
    CODE_SUBMISSION = "CODE_SUBMISSION"  # Envío de código
    HINT_REQUEST = "HINT_REQUEST"      # Solicitud de pista
    CLARIFICATION = "CLARIFICATION"    # Aclaración
    VALIDATION = "VALIDATION"          # Validación de solución
    FEEDBACK = "FEEDBACK"              # Feedback del sistema
    REFLECTION = "REFLECTION"          # Reflexión del estudiante
    # FIX 1.2 Cortez7: Agregados valores adicionales del domain model
    STUDENT_PROMPT = "student_prompt"  # Alias para compatibilidad
    AI_RESPONSE = "ai_response"        # Alias para compatibilidad
    CODE_COMMIT = "code_commit"        # Commit de código
    TUTOR_INTERVENTION = "tutor_intervention"  # Intervención del tutor
    TEACHER_FEEDBACK = "teacher_feedback"      # Feedback del docente
    STRATEGY_CHANGE = "strategy_change"        # Cambio de estrategia
    HYPOTHESIS_FORMULATION = "hypothesis_formulation"  # Formulación de hipótesis
    SELF_CORRECTION = "self_correction"        # Auto-corrección
    AI_CRITIQUE = "ai_critique"                # Crítica de IA


# FIX 1.2 Cortez7: Mapping API -> Domain values for InteractionType
INTERACTION_TYPE_API_TO_DB = {
    # API UPPERCASE -> domain lowercase
    "QUESTION": "student_prompt",
    "RESPONSE": "ai_response",
    "CODE_SUBMISSION": "code_commit",
    "HINT_REQUEST": "tutor_intervention",
    "CLARIFICATION": "tutor_intervention",
    "VALIDATION": "self_correction",
    "FEEDBACK": "teacher_feedback",
    "REFLECTION": "strategy_change",
    # Domain values pass through
    "student_prompt": "student_prompt",
    "ai_response": "ai_response",
    "code_commit": "code_commit",
    "tutor_intervention": "tutor_intervention",
    "teacher_feedback": "teacher_feedback",
    "strategy_change": "strategy_change",
    "hypothesis_formulation": "hypothesis_formulation",
    "self_correction": "self_correction",
    "ai_critique": "ai_critique",
}


def normalize_interaction_type(value: str) -> str:
    """
    FIX 1.2 Cortez7: Normalize interaction type value for database storage.

    Converts API-style UPPERCASE values to domain-style lowercase values.

    Args:
        value: Interaction type value (can be uppercase or lowercase)

    Returns:
        Normalized lowercase value for database storage
    """
    if value is None:
        return None
    # Check if it's in the mapping
    if value in INTERACTION_TYPE_API_TO_DB:
        return INTERACTION_TYPE_API_TO_DB[value]
    # Try uppercase version
    upper_value = value.upper()
    if upper_value in INTERACTION_TYPE_API_TO_DB:
        return INTERACTION_TYPE_API_TO_DB[upper_value]
    # Return lowercase as fallback
    return value.lower()