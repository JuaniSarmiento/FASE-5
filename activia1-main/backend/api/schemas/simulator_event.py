"""
Schemas para eventos de simulador (SimulatorEventDB)
FIX 3.1: Schemas faltantes para ORM models
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class SimulatorEventCreate(BaseModel):
    """Request para crear un nuevo evento de simulador"""

    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    simulator_type: str = Field(..., description="Tipo de simulador: product_owner, scrum_master, etc.")
    event_type: str = Field(..., description="Tipo de evento: interaction, milestone, decision, etc.")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Datos del evento")
    description: Optional[str] = Field(None, description="Descripción del evento")
    severity: Optional[str] = Field(None, description="Severidad: info, warning, error, critical")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "student_id": "student_001",
                "simulator_type": "product_owner",
                "event_type": "user_story_created",
                "event_data": {
                    "story_id": "US-001",
                    "title": "Login de usuario",
                    "acceptance_criteria": ["Validar email", "Validar password"]
                },
                "description": "Estudiante creó historia de usuario",
                "severity": "info"
            }
        }


class SimulatorEventResponse(BaseModel):
    """Response con información de un evento de simulador"""

    id: str = Field(..., description="ID del evento")
    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    simulator_type: str = Field(..., description="Tipo de simulador")
    event_type: str = Field(..., description="Tipo de evento")
    event_data: Dict[str, Any] = Field(default_factory=dict, description="Datos del evento")
    description: Optional[str] = Field(None, description="Descripción")
    severity: Optional[str] = Field(None, description="Severidad")
    timestamp: datetime = Field(..., description="Timestamp del evento")
    created_at: datetime = Field(..., description="Timestamp de creación")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "evt_xyz789",
                "session_id": "session_abc123",
                "student_id": "student_001",
                "simulator_type": "product_owner",
                "event_type": "user_story_created",
                "event_data": {"story_id": "US-001"},
                "description": "Historia creada",
                "severity": "info",
                "timestamp": "2025-11-18T10:30:00Z",
                "created_at": "2025-11-18T10:30:00Z"
            }
        }


class SimulatorEventListResponse(BaseModel):
    """Response con lista de eventos de simulador"""

    events: List[SimulatorEventResponse] = Field(..., description="Lista de eventos")
    total: int = Field(..., description="Total de eventos")
    session_id: Optional[str] = Field(None, description="ID de sesión si se filtró")


class SimulatorTimelineResponse(BaseModel):
    """Response con timeline de eventos de una sesión de simulador"""

    session_id: str = Field(..., description="ID de la sesión")
    simulator_type: str = Field(..., description="Tipo de simulador")
    student_id: str = Field(..., description="ID del estudiante")

    # Timeline
    events: List[SimulatorEventResponse] = Field(..., description="Eventos en orden cronológico")
    total_events: int = Field(0, description="Total de eventos")

    # Aggregated metrics
    event_types_count: Dict[str, int] = Field(
        default_factory=dict,
        description="Conteo por tipo de evento"
    )
    milestones_reached: List[str] = Field(
        default_factory=list,
        description="Hitos alcanzados"
    )
    decisions_made: int = Field(0, description="Decisiones tomadas")
    warnings_count: int = Field(0, description="Advertencias generadas")

    # Duration
    start_time: Optional[datetime] = Field(None, description="Inicio de la sesión")
    end_time: Optional[datetime] = Field(None, description="Fin de la sesión")
    duration_minutes: Optional[int] = Field(None, description="Duración en minutos")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "simulator_type": "product_owner",
                "student_id": "student_001",
                "events": [],
                "total_events": 15,
                "event_types_count": {
                    "interaction": 10,
                    "milestone": 3,
                    "decision": 2
                },
                "milestones_reached": ["backlog_created", "sprint_planned"],
                "decisions_made": 5,
                "warnings_count": 2,
                "start_time": "2025-11-18T10:00:00Z",
                "end_time": "2025-11-18T11:30:00Z",
                "duration_minutes": 90
            }
        }
