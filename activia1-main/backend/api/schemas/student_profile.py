"""
Schemas para perfiles de estudiantes (StudentProfileDB)
FIX 2.8 Cortez8: Schemas faltantes para ORM StudentProfileDB
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class StudentProfileCreate(BaseModel):
    """Request para crear un perfil de estudiante"""

    student_id: str = Field(..., max_length=100, description="ID único del estudiante")
    user_id: Optional[str] = Field(None, max_length=36, description="ID del usuario autenticado (UUID)")
    name: Optional[str] = Field(None, max_length=255, description="Nombre del estudiante")
    email: Optional[str] = Field(None, max_length=255, description="Email del estudiante")
    preferred_language: str = Field("es", max_length=10, description="Idioma preferido")
    cognitive_preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Preferencias cognitivas del estudiante"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Juan Pérez",
                "email": "juan.perez@university.edu",
                "preferred_language": "es",
                "cognitive_preferences": {
                    "learning_style": "visual",
                    "preferred_feedback": "detailed"
                }
            }
        }


class StudentProfileUpdate(BaseModel):
    """Request para actualizar un perfil de estudiante"""

    name: Optional[str] = Field(None, max_length=255, description="Nombre del estudiante")
    email: Optional[str] = Field(None, max_length=255, description="Email del estudiante")
    preferred_language: Optional[str] = Field(None, max_length=10, description="Idioma preferido")
    cognitive_preferences: Optional[Dict[str, Any]] = Field(
        None,
        description="Preferencias cognitivas del estudiante"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Juan Carlos Pérez",
                "cognitive_preferences": {
                    "learning_style": "kinesthetic"
                }
            }
        }


class StudentProfileResponse(BaseModel):
    """
    Response con información de un perfil de estudiante.

    FIX 2.8 Cortez8: Schema para ORM StudentProfileDB.
    """

    id: str = Field(..., description="ID del perfil")
    student_id: str = Field(..., description="ID único del estudiante")
    user_id: Optional[str] = Field(None, description="ID del usuario autenticado")
    name: Optional[str] = Field(None, description="Nombre del estudiante")
    email: Optional[str] = Field(None, description="Email del estudiante")
    preferred_language: str = Field("es", description="Idioma preferido")

    # Aggregate metrics from sessions
    total_sessions: int = Field(0, description="Total de sesiones")
    total_interactions: int = Field(0, description="Total de interacciones")
    average_ai_dependency: float = Field(0.0, ge=0, le=1, description="Dependencia promedio de IA (0-1)")
    average_competency_score: Optional[float] = Field(None, ge=0, le=10, description="Score promedio de competencia (0-10)")

    # Cognitive preferences and profile
    cognitive_preferences: Dict[str, Any] = Field(default_factory=dict, description="Preferencias cognitivas")
    learning_patterns: Dict[str, Any] = Field(default_factory=dict, description="Patrones de aprendizaje detectados")
    # FIX 10.2 Cortez10: ORM uses risk_trends, API uses risk_profile
    risk_trends: Dict[str, Any] = Field(default_factory=dict, alias="risk_profile", description="Perfil de riesgos")

    # Competency tracking
    competency_levels: Dict[str, str] = Field(
        default_factory=dict,
        description="Niveles de competencia por área"
    )
    strengths: List[str] = Field(default_factory=list, description="Fortalezas identificadas")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Áreas de mejora")

    # Timestamps
    # FIX 10.2 Cortez10: Renamed to match ORM field name with alias for backwards compatibility
    last_activity_date: Optional[datetime] = Field(None, alias="last_session_at", description="Fecha de última sesión")
    created_at: datetime = Field(..., description="Timestamp de creación")
    updated_at: datetime = Field(..., description="Timestamp de última actualización")

    class Config:
        from_attributes = True
        # FIX 10.2 Cortez10: Allow both field names and aliases
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "profile_xyz789",
                "student_id": "student_001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Juan Pérez",
                "email": "juan.perez@university.edu",
                "preferred_language": "es",
                "total_sessions": 25,
                "total_interactions": 342,
                "average_ai_dependency": 0.35,
                "average_competency_score": 7.2,
                "cognitive_preferences": {
                    "learning_style": "visual",
                    "preferred_feedback": "detailed"
                },
                "learning_patterns": {
                    "peak_hours": ["10:00", "15:00"],
                    "avg_session_duration_min": 45
                },
                "risk_profile": {
                    "cognitive_risk": "low",
                    "ethical_risk": "low"
                },
                "competency_levels": {
                    "data_structures": "en_desarrollo",
                    "algorithms": "autonomo"
                },
                "strengths": ["Buena comprensión conceptual", "Persistencia"],
                "areas_for_improvement": ["Justificación de decisiones"],
                "last_session_at": "2025-12-10T15:30:00Z",
                "created_at": "2025-09-01T10:00:00Z",
                "updated_at": "2025-12-10T15:30:00Z"
            }
        }


class StudentProfileListResponse(BaseModel):
    """Response con lista de perfiles de estudiantes"""

    profiles: List[StudentProfileResponse] = Field(..., description="Lista de perfiles")
    total: int = Field(..., description="Total de perfiles")


class StudentProgressSummary(BaseModel):
    """Resumen de progreso de un estudiante"""

    student_id: str = Field(..., description="ID del estudiante")
    name: Optional[str] = Field(None, description="Nombre del estudiante")

    # Overall metrics
    overall_competency_level: str = Field(..., description="Nivel de competencia general")
    overall_score: float = Field(..., ge=0, le=10, description="Score general (0-10)")
    ai_dependency_trend: str = Field(..., description="Tendencia de dependencia IA: improving, stable, worsening")

    # Activity breakdown
    sessions_by_activity: Dict[str, int] = Field(default_factory=dict, description="Sesiones por actividad")
    competency_by_activity: Dict[str, float] = Field(default_factory=dict, description="Competencia por actividad")

    # Time-based metrics
    sessions_this_week: int = Field(0, description="Sesiones esta semana")
    interactions_this_week: int = Field(0, description="Interacciones esta semana")

    # Risks
    active_risks: int = Field(0, description="Riesgos activos no resueltos")
    critical_risks: int = Field(0, description="Riesgos críticos activos")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": "student_001",
                "name": "Juan Pérez",
                "overall_competency_level": "en_desarrollo",
                "overall_score": 7.2,
                "ai_dependency_trend": "improving",
                "sessions_by_activity": {
                    "prog2_tp1_colas": 5,
                    "prog2_tp2_arboles": 3
                },
                "competency_by_activity": {
                    "prog2_tp1_colas": 7.5,
                    "prog2_tp2_arboles": 6.8
                },
                "sessions_this_week": 3,
                "interactions_this_week": 45,
                "active_risks": 2,
                "critical_risks": 0
            }
        }
