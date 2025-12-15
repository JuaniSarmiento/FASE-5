"""
Schemas para interacciones con el Tutor Cognitivo (T-IA-Cog)
FIX 5.2: Create typed schemas for tutor interactions (Cortez2 audit)
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from .enums import CognitiveIntent


class TutorInteractRequest(BaseModel):
    """Request para interacción con el tutor"""

    message: str = Field(..., min_length=1, description="Mensaje del estudiante")
    student_profile: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Perfil del estudiante (nivel, historial, preferencias)"
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contexto adicional de la interacción"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "No entiendo cómo implementar una cola con arreglos",
                "student_profile": {
                    "level": "intermedio",
                    "previous_topics": ["listas", "pilas"]
                },
                "context": {
                    "current_exercise": "prog2_tp1_colas",
                    "attempts": 2
                }
            }
        }


class TutorInteractResponse(BaseModel):
    """Response de interacción con el tutor"""

    response: str = Field(..., description="Respuesta del tutor")
    intervention_type: str = Field(
        ...,
        description="Tipo de intervención: PREGUNTA_SOCRATICA, PISTA_GRADUADA, RECHAZO_PEDAGOGICO, etc."
    )
    semaforo: str = Field(
        ...,
        description="Estado del semáforo pedagógico: verde, amarillo, rojo"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata de la intervención (trace_id, timing, etc.)"
    )

    # Campos N4 opcionales
    cognitive_intent_detected: Optional[str] = Field(
        None,
        description="Intención cognitiva detectada en el mensaje del estudiante"
    )
    scaffolding_level: Optional[str] = Field(
        None,
        description="Nivel de andamiaje aplicado: NOVATO, INTERMEDIO, AVANZADO"
    )
    rules_applied: List[str] = Field(
        default_factory=list,
        description="Reglas pedagógicas aplicadas en esta intervención"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "response": "¿Qué característica define a una cola respecto a otras estructuras de datos?",
                "intervention_type": "PREGUNTA_SOCRATICA",
                "semaforo": "verde",
                "metadata": {
                    "trace_id": "trace_xyz789",
                    "processing_time_ms": 234
                },
                "cognitive_intent_detected": "UNDERSTANDING",
                "scaffolding_level": "INTERMEDIO",
                "rules_applied": ["MODO_SOCRATICO", "REFUERZO_CONCEPTUAL"]
            }
        }


class CreateTutorSessionRequest(BaseModel):
    """Request para crear una nueva sesión de tutor"""

    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    mode: str = Field(
        default="TUTOR",
        description="Modo de sesión: TUTOR, EVALUATOR, etc."
    )
    initial_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Contexto inicial de la sesión"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "mode": "TUTOR",
                "initial_context": {
                    "learning_objective": "Implementar estructura Cola",
                    "difficulty": "INTERMEDIO"
                }
            }
        }


class CreateTutorSessionResponse(BaseModel):
    """Response al crear una sesión de tutor"""

    session_id: str = Field(..., description="ID de la sesión creada")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    mode: str = Field(..., description="Modo de sesión")
    status: str = Field(..., description="Estado de la sesión")
    created_at: datetime = Field(..., description="Timestamp de creación")
    welcome_message: Optional[str] = Field(
        None,
        description="Mensaje de bienvenida del tutor"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "mode": "TUTOR",
                "status": "active",
                "created_at": "2025-12-12T10:30:00Z",
                "welcome_message": "¡Hola! Soy tu tutor de Programación II. ¿En qué puedo ayudarte hoy?"
            }
        }


class TutorSessionAnalytics(BaseModel):
    """Analytics N4 de una sesión de tutor"""

    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")

    # Métricas de interacción
    total_interactions: int = Field(0, description="Total de interacciones")
    total_questions_asked: int = Field(0, description="Preguntas realizadas por el estudiante")
    total_hints_given: int = Field(0, description="Pistas proporcionadas")

    # Métricas cognitivas
    ai_dependency_score: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Score de dependencia de IA (0-1)"
    )
    autonomy_progression: List[float] = Field(
        default_factory=list,
        description="Evolución del nivel de autonomía durante la sesión"
    )
    cognitive_states_visited: List[str] = Field(
        default_factory=list,
        description="Estados cognitivos visitados durante la sesión"
    )

    # Métricas de semáforo
    semaforo_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribución de estados del semáforo: {verde: N, amarillo: M, rojo: K}"
    )

    # Intervenciones pedagógicas
    interventions_by_type: Dict[str, int] = Field(
        default_factory=dict,
        description="Conteo de intervenciones por tipo"
    )
    rules_applied_count: Dict[str, int] = Field(
        default_factory=dict,
        description="Conteo de reglas pedagógicas aplicadas"
    )

    # Riesgos detectados
    risks_detected: int = Field(0, description="Número de riesgos detectados")
    critical_risks: int = Field(0, description="Número de riesgos críticos")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "student_id": "student_001",
                "total_interactions": 15,
                "total_questions_asked": 8,
                "total_hints_given": 3,
                "ai_dependency_score": 0.45,
                "autonomy_progression": [0.3, 0.4, 0.5, 0.6],
                "cognitive_states_visited": ["EXPLORING", "UNDERSTANDING", "IMPLEMENTING"],
                "semaforo_distribution": {"verde": 10, "amarillo": 4, "rojo": 1},
                "interventions_by_type": {
                    "PREGUNTA_SOCRATICA": 5,
                    "PISTA_GRADUADA": 3,
                    "REFUERZO_CONCEPTUAL": 2
                },
                "rules_applied_count": {
                    "MODO_SOCRATICO": 8,
                    "ANTI_SOLUCION": 2,
                    "REFUERZO_CONCEPTUAL": 5
                },
                "risks_detected": 2,
                "critical_risks": 0
            }
        }
