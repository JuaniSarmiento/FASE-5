"""
Schemas para sesiones de aprendizaje
FIX Cortez8: Correcciones de consistencia ORM vs Pydantic
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, model_validator

from .enums import SessionMode, SessionStatus, SimulatorType


class SessionCreate(BaseModel):
    """Request para crear una nueva sesión"""

    student_id: str = Field(..., min_length=1, max_length=255, description="ID del estudiante")
    activity_id: str = Field(..., min_length=1, max_length=255, description="ID de la actividad")
    mode: SessionMode = Field(..., description="Modo de interacción: TUTOR, EVALUATOR, SIMULATOR, etc.")
    simulator_type: Optional[str] = Field(
        None,
        max_length=50,
        description="Tipo de simulador cuando mode=SIMULATOR: product_owner, scrum_master, tech_interviewer, incident_responder, client, devsecops"
    )

    @model_validator(mode='after')
    def validate_simulator_type_required(self) -> 'SessionCreate':
        """
        Validates that simulator_type is provided and valid when mode=SIMULATOR.

        Raises:
            ValueError: If mode is SIMULATOR but simulator_type is missing or invalid.
        """
        # Check if mode is SIMULATOR
        if self.mode == SessionMode.SIMULATOR:
            # simulator_type is required for SIMULATOR mode
            if not self.simulator_type:
                raise ValueError(
                    "simulator_type is required when mode=SIMULATOR. "
                    f"Valid values are: {', '.join([e.value for e in SimulatorType])}"
                )

            # Validate that simulator_type is a valid value
            valid_types = [e.value for e in SimulatorType]
            if self.simulator_type.lower() not in valid_types:
                raise ValueError(
                    f"Invalid simulator_type '{self.simulator_type}'. "
                    f"Valid values are: {', '.join(valid_types)}"
                )

            # Normalize to lowercase for consistency with DB storage
            self.simulator_type = self.simulator_type.lower()

        # If mode is not SIMULATOR, simulator_type should be None (ignore if provided)
        elif self.simulator_type is not None:
            # Silently set to None - simulator_type is only relevant for SIMULATOR mode
            self.simulator_type = None

        return self

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "summary": "Tutor session",
                    "value": {
                        "student_id": "student_001",
                        "activity_id": "prog2_tp1_colas",
                        "mode": "TUTOR",
                        "simulator_type": None
                    }
                },
                {
                    "summary": "Simulator session (Product Owner)",
                    "value": {
                        "student_id": "student_001",
                        "activity_id": "prog2_tp1_colas",
                        "mode": "SIMULATOR",
                        "simulator_type": "product_owner"
                    }
                }
            ]
        }


class SessionUpdate(BaseModel):
    """Request para actualizar una sesión"""

    mode: Optional[SessionMode] = Field(None, description="Nuevo modo de interacción")
    status: Optional[SessionStatus] = Field(None, description="Nuevo estado: active, completed, aborted, paused")

    class Config:
        json_schema_extra = {
            "example": {
                "mode": "EVALUATOR",
                "status": "COMPLETED"
            }
        }


class SessionResponse(BaseModel):
    """Response con información de una sesión"""

    id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    user_id: Optional[str] = Field(
        None,
        description="ID del usuario autenticado (puede ser None para sesiones anónimas/legacy)"
    )
    mode: str = Field(..., description="Modo de interacción")
    status: str = Field(..., description="Estado de la sesión")
    simulator_type: Optional[str] = Field(
        None,
        description="Tipo de simulador cuando mode=SIMULATOR"
    )
    start_time: datetime = Field(..., description="Timestamp de inicio")
    end_time: Optional[datetime] = Field(None, description="Timestamp de finalización")
    trace_count: int = Field(0, description="Número de trazas capturadas")
    risk_count: int = Field(0, description="Número de riesgos detectados")
    created_at: datetime = Field(..., description="Timestamp de creación")
    updated_at: datetime = Field(..., description="Timestamp de última actualización")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "session_abc123",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "mode": "TUTOR",
                "status": "ACTIVE",
                "simulator_type": None,
                "start_time": "2025-11-18T10:00:00Z",
                "end_time": None,
                "trace_count": 5,
                "risk_count": 1,
                "created_at": "2025-11-18T10:00:00Z",
                "updated_at": "2025-11-18T10:30:00Z"
            }
        }


class SessionListResponse(BaseModel):
    """Response con lista de sesiones"""

    sessions: List[SessionResponse] = Field(..., description="Lista de sesiones")
    total: int = Field(..., description="Total de sesiones")


class SessionDetailResponse(SessionResponse):
    """
    Response con detalles completos de una sesión.

    FIX 2.3 Cortez8: Agregados campos N4 que existen en ORM.
    """

    traces_summary: dict = Field(..., description="Resumen de trazas por nivel")
    risks_summary: dict = Field(..., description="Resumen de riesgos por tipo")
    ai_dependency_score: Optional[float] = Field(None, ge=0, le=1, description="Score de dependencia de IA (0-1)")

    # FIX 2.3 Cortez8: Campos N4 que existen en ORM SessionDB
    learning_objective: Optional[Dict[str, Any]] = Field(
        None,
        description="Objetivo de aprendizaje de la sesión"
    )
    cognitive_status: Optional[Dict[str, Any]] = Field(
        None,
        description="Estado cognitivo actual del estudiante"
    )
    session_metrics: Optional[Dict[str, Any]] = Field(
        None,
        description="Métricas agregadas de la sesión"
    )

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "mode": "TUTOR",
                "status": "active",
                "start_time": "2025-11-18T10:00:00Z",
                "end_time": None,
                "trace_count": 5,
                "risk_count": 1,
                "created_at": "2025-11-18T10:00:00Z",
                "updated_at": "2025-11-18T10:30:00Z",
                "traces_summary": {
                    "n1_superficial": 0,
                    "n2_tecnico": 1,
                    "n3_interaccional": 2,
                    "n4_cognitivo": 2
                },
                "risks_summary": {
                    "cognitive_delegation": 1,
                    "uncritical_acceptance": 0
                },
                "ai_dependency_score": 0.35,
                "learning_objective": {
                    "title": "Implementar estructura de datos Cola",
                    "expected_competencies": ["abstraccion", "implementacion"]
                },
                "cognitive_status": {
                    "current_phase": "implementation",
                    "autonomy_level": 0.6,
                    "cognitive_load": "medium"
                },
                "session_metrics": {
                    "total_interactions": 15,
                    "ai_dependency_score": 0.35,
                    "risk_events": 1
                }
            }
        }


# ============================================================================
# SCHEMAS PARA HISTORIAL DE SESIONES (HU-EST-008) - Sprint 6
# ============================================================================


class SessionHistoryFilters(BaseModel):
    """Filtros para consultar historial de sesiones"""

    start_date: Optional[date] = Field(None, description="Fecha de inicio del rango")
    end_date: Optional[date] = Field(None, description="Fecha de fin del rango")
    activity_id: Optional[str] = Field(None, description="Filtrar por actividad específica")
    mode: Optional[SessionMode] = Field(None, description="Filtrar por modo de interacción")
    status: Optional[SessionStatus] = Field(None, description="Filtrar por estado")
    min_competency: Optional[str] = Field(None, description="Competencia mínima: INICIAL, INTERMEDIO, AVANZADO, EXPERTO")

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2025-11-01",
                "end_date": "2025-11-30",
                "activity_id": "prog2_tp1_colas",
                "mode": "TUTOR",
                "status": "COMPLETED",
                "min_competency": "INTERMEDIO"
            }
        }


class SessionSummary(BaseModel):
    """
    Resumen de una sesión para el historial.

    FIX 1.5 Cortez8: Documentación de escalas de scores.
    - overall_score: 0-1 (normalizado para visualización en listas)
    - ai_dependency_score: 0-1 (consistente con otras métricas)
    Para evaluaciones detalladas usar EvaluationResponse con escala 0-10.
    """

    session_id: str = Field(..., description="ID de la sesión")
    activity_id: str = Field(..., description="ID de la actividad")
    mode: str = Field(..., description="Modo de interacción")
    status: str = Field(..., description="Estado")
    start_time: datetime = Field(..., description="Inicio")
    end_time: Optional[datetime] = Field(None, description="Fin")
    duration_minutes: Optional[int] = Field(None, description="Duración en minutos")
    interactions_count: int = Field(0, description="Número de interacciones")
    # FIX 1.5 Cortez8: Documentar escala
    ai_dependency_score: Optional[float] = Field(None, ge=0, le=1, description="Score de dependencia de IA (0-1)")
    competency_level: Optional[str] = Field(None, description="Nivel de competencia alcanzado")
    # FIX 1.5 Cortez8: overall_score normalizado (0-1) para resúmenes, diferente a evaluation (0-10)
    overall_score: Optional[float] = Field(None, ge=0, le=1, description="Puntaje general normalizado (0-1). Para detalle usar EvaluationResponse (0-10)")
    risks_detected: int = Field(0, description="Riesgos detectados")
    critical_risks: int = Field(0, description="Riesgos críticos")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "activity_id": "prog2_tp1_colas",
                "mode": "TUTOR",
                "status": "completed",
                "start_time": "2025-11-18T10:00:00Z",
                "end_time": "2025-11-18T11:30:00Z",
                "duration_minutes": 90,
                "interactions_count": 12,
                "ai_dependency_score": 0.35,
                "competency_level": "en_desarrollo",
                "overall_score": 0.75,
                "risks_detected": 2,
                "critical_risks": 0
            }
        }


class ProgressAggregation(BaseModel):
    """Agregaciones de progreso temporal"""

    total_sessions: int = Field(..., description="Total de sesiones")
    completed_sessions: int = Field(..., description="Sesiones completadas")
    total_interactions: int = Field(..., description="Total de interacciones")
    average_ai_dependency: float = Field(..., description="Dependencia promedio de IA (0-1)")
    competency_evolution: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Evolución de competencia por fecha"
    )
    activity_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Sesiones por actividad"
    )
    mode_breakdown: Dict[str, int] = Field(
        default_factory=dict,
        description="Sesiones por modo"
    )
    risk_summary: Dict[str, int] = Field(
        default_factory=dict,
        description="Resumen de riesgos"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total_sessions": 15,
                "completed_sessions": 12,
                "total_interactions": 180,
                "average_ai_dependency": 0.42,
                "competency_evolution": [
                    {"date": "2025-11-01", "level": "INICIAL", "score": 0.5},
                    {"date": "2025-11-15", "level": "INTERMEDIO", "score": 0.7},
                    {"date": "2025-11-30", "level": "AVANZADO", "score": 0.85}
                ],
                "activity_breakdown": {
                    "prog2_tp1_colas": 5,
                    "prog2_tp2_arboles": 4,
                    "prog2_tp3_grafos": 6
                },
                "mode_breakdown": {
                    "TUTOR": 10,
                    "EVALUATOR": 3,
                    "SIMULATOR": 2
                },
                "risk_summary": {
                    "total_risks": 8,
                    "critical_risks": 1,
                    "high_risks": 3,
                    "resolved_risks": 6
                }
            }
        }


class SessionHistoryResponse(BaseModel):
    """Response completo del historial de sesiones"""

    student_id: str = Field(..., description="ID del estudiante")
    sessions: List[SessionSummary] = Field(..., description="Lista de sesiones")
    aggregations: ProgressAggregation = Field(..., description="Agregaciones y métricas")
    filters_applied: Optional[Dict[str, Any]] = Field(None, description="Filtros aplicados")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_001",
                "sessions": [
                    {
                        "session_id": "session_abc123",
                        "activity_id": "prog2_tp1_colas",
                        "mode": "TUTOR",
                        "status": "COMPLETED",
                        "start_time": "2025-11-18T10:00:00Z",
                        "end_time": "2025-11-18T11:30:00Z",
                        "duration_minutes": 90,
                        "interactions_count": 12,
                        "ai_dependency_score": 0.35,
                        "competency_level": "INTERMEDIO",
                        "overall_score": 0.75,
                        "risks_detected": 2,
                        "critical_risks": 0
                    }
                ],
                "aggregations": {
                    "total_sessions": 15,
                    "completed_sessions": 12,
                    "total_interactions": 180,
                    "average_ai_dependency": 0.42,
                    "competency_evolution": [],
                    "activity_breakdown": {},
                    "mode_breakdown": {},
                    "risk_summary": {}
                },
                "filters_applied": {
                    "start_date": "2025-11-01",
                    "end_date": "2025-11-30"
                }
            }
        }