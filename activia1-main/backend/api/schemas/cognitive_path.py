"""
Schemas para camino cognitivo reconstructivo (HU-EST-006)

Sprint 3
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class CognitivePhase(BaseModel):
    """Fase del camino cognitivo"""
    phase_name: str = Field(..., description="Nombre de la fase (EXPLORACION, PLANIFICACION, etc.)")
    start_time: datetime = Field(..., description="Timestamp de inicio")
    end_time: Optional[datetime] = Field(None, description="Timestamp de fin")
    duration_minutes: Optional[float] = Field(None, description="Duración en minutos")
    interactions_count: int = Field(..., description="Número de interacciones en esta fase")
    ai_involvement_avg: float = Field(..., description="Promedio de dependencia de IA (0-1)")
    risks_detected: List[str] = Field(default_factory=list, description="Riesgos detectados en esta fase")
    key_decisions: List[str] = Field(default_factory=list, description="Decisiones clave tomadas")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "phase_name": "EXPLORACION_CONCEPTUAL",
                "start_time": "2025-11-20T10:00:00Z",
                "end_time": "2025-11-20T10:15:00Z",
                "duration_minutes": 15.0,
                "interactions_count": 3,
                "ai_involvement_avg": 0.25,
                "risks_detected": [],
                "key_decisions": ["Decidió investigar cola circular vs cola simple"]
            }]
        }
    }


class CognitiveTransition(BaseModel):
    """Transición entre fases cognitivas"""
    from_phase: str = Field(..., description="Fase de origen")
    to_phase: str = Field(..., description="Fase de destino")
    timestamp: datetime = Field(..., description="Momento de la transición")
    trigger: Optional[str] = Field(None, description="Qué disparó la transición")


class AIDependencyPoint(BaseModel):
    """Punto de evolución de dependencia de IA"""
    timestamp: datetime = Field(..., description="Momento del registro")
    ai_involvement: float = Field(..., ge=0.0, le=1.0, description="Nivel de dependencia de IA (0-1)")


class CognitivePathSummary(BaseModel):
    """Resumen del camino cognitivo"""
    total_interactions: int = Field(..., description="Total de interacciones")
    total_duration_minutes: float = Field(..., description="Duración total en minutos")
    blocked_interactions: int = Field(..., description="Interacciones bloqueadas por gobernanza")
    ai_dependency_average: float = Field(..., description="Dependencia promedio de IA (0-1)")
    strategy_changes: int = Field(..., description="Cantidad de cambios de estrategia")
    risks_total: int = Field(..., description="Total de riesgos detectados")
    risks_by_level: Dict[str, int] = Field(default_factory=dict, description="Riesgos por nivel")


class CognitivePath(BaseModel):
    """Camino cognitivo reconstructivo completo"""
    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    start_time: datetime = Field(..., description="Inicio de la sesión")
    end_time: Optional[datetime] = Field(None, description="Fin de la sesión")
    summary: CognitivePathSummary = Field(..., description="Resumen cuantitativo")
    phases: List[CognitivePhase] = Field(..., description="Fases cognitivas atravesadas")
    transitions: List[CognitiveTransition] = Field(..., description="Transiciones entre fases")
    ai_dependency_evolution: List[AIDependencyPoint] = Field(
        default_factory=list,
        description="Evolución temporal de la dependencia de IA"
    )
    strategy_changes: List[str] = Field(
        default_factory=list,
        description="Cambios de estrategia detectados durante la sesión"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "session_id": "session_abc123",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "start_time": "2025-11-20T10:00:00Z",
                "end_time": "2025-11-20T10:45:00Z",
                "summary": {
                    "total_interactions": 8,
                    "total_duration_minutes": 45.0,
                    "blocked_interactions": 1,
                    "ai_dependency_average": 0.35,
                    "strategy_changes": 2,
                    "risks_total": 1,
                    "risks_by_level": {"MEDIUM": 1}
                },
                "phases": [
                    {
                        "phase_name": "EXPLORACION_CONCEPTUAL",
                        "start_time": "2025-11-20T10:00:00Z",
                        "end_time": "2025-11-20T10:15:00Z",
                        "duration_minutes": 15.0,
                        "interactions_count": 3,
                        "ai_involvement_avg": 0.25,
                        "risks_detected": [],
                        "key_decisions": []
                    }
                ],
                "transitions": [
                    {
                        "from_phase": "EXPLORACION_CONCEPTUAL",
                        "to_phase": "PLANIFICACION",
                        "timestamp": "2025-11-20T10:15:00Z",
                        "trigger": "Completó comprensión conceptual"
                    }
                ]
            }]
        }
    }