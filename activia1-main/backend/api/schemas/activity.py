"""
Schemas para actividades creadas por docentes
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

from .enums import ActivityDifficulty, ActivityStatus, HelpLevel


class PolicyConfig(BaseModel):
    """Configuración de políticas pedagógicas"""

    max_help_level: Union[HelpLevel, str] = Field(
        ...,
        description="Nivel máximo de ayuda: minimo, bajo, medio, alto"
    )
    block_complete_solutions: bool = Field(
        True,
        description="Bloquear soluciones completas sin mediación"
    )
    require_justification: bool = Field(
        True,
        description="Requerir justificación explícita de decisiones"
    )
    allow_code_snippets: bool = Field(
        False,
        description="Permitir fragmentos de código como ayuda"
    )
    risk_thresholds: Dict[str, float] = Field(
        default_factory=dict,
        description="Umbrales de riesgo por dimensión (ej: {'ai_dependency': 0.6, 'lack_justification': 0.3})"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "max_help_level": "MEDIO",
                "block_complete_solutions": True,
                "require_justification": True,
                "allow_code_snippets": False,
                "risk_thresholds": {
                    "ai_dependency": 0.6,
                    "lack_justification": 0.3
                }
            }
        }


class ActivityCreate(BaseModel):
    """Request para crear una nueva actividad"""

    activity_id: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="ID único de la actividad (ej: 'prog2_tp1_colas')"
    )
    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Título de la actividad"
    )
    instructions: str = Field(
        ...,
        min_length=10,
        description="Consigna detallada de la actividad"
    )
    teacher_id: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="ID del docente creador"
    )
    policies: PolicyConfig = Field(
        ...,
        description="Políticas pedagógicas configurables"
    )
    description: Optional[str] = Field(
        None,
        description="Descripción breve de la actividad"
    )
    evaluation_criteria: Optional[List[str]] = Field(
        None,
        description="Lista de criterios de evaluación"
    )
    subject: Optional[str] = Field(
        None,
        max_length=100,
        description="Materia (ej: 'Programación II')"
    )
    difficulty: Optional[Union[ActivityDifficulty, str]] = Field(
        None,
        description="Nivel de dificultad: INICIAL, INTERMEDIO, AVANZADO"
    )
    estimated_duration_minutes: Optional[int] = Field(
        None,
        ge=1,
        description="Duración estimada en minutos"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Etiquetas para categorización (ej: ['colas', 'estructuras', 'arreglos'])"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "activity_id": "prog2_tp1_colas",
                "title": "Implementación de Cola Circular",
                "description": "Trabajo práctico sobre estructuras de datos tipo cola con implementación circular",
                "instructions": "Implementar una cola circular que...",
                "evaluation_criteria": [
                    "Correcta implementación de operaciones básicas (enqueue, dequeue)",
                    "Manejo apropiado de condiciones de overflow/underflow",
                    "Justificación de decisiones de diseño"
                ],
                "teacher_id": "teacher_001",
                "policies": {
                    "max_help_level": "MEDIO",
                    "block_complete_solutions": True,
                    "require_justification": True,
                    "allow_code_snippets": False,
                    "risk_thresholds": {
                        "ai_dependency": 0.6,
                        "lack_justification": 0.3
                    }
                },
                "subject": "Programación II",
                "difficulty": "INTERMEDIO",
                "estimated_duration_minutes": 120,
                "tags": ["colas", "estructuras", "arreglos"]
            }
        }


class ActivityUpdate(BaseModel):
    """Request para actualizar una actividad existente"""

    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200,
        description="Nuevo título"
    )
    description: Optional[str] = Field(
        None,
        description="Nueva descripción"
    )
    instructions: Optional[str] = Field(
        None,
        min_length=10,
        description="Nueva consigna"
    )
    policies: Optional[PolicyConfig] = Field(
        None,
        description="Nuevas políticas pedagógicas"
    )
    evaluation_criteria: Optional[List[str]] = Field(
        None,
        description="Nuevos criterios de evaluación"
    )
    subject: Optional[str] = Field(
        None,
        max_length=100,
        description="Nueva materia"
    )
    difficulty: Optional[Union[ActivityDifficulty, str]] = Field(
        None,
        description="Nuevo nivel de dificultad: INICIAL, INTERMEDIO, AVANZADO"
    )
    estimated_duration_minutes: Optional[int] = Field(
        None,
        ge=1,
        description="Nueva duración estimada en minutos"
    )
    tags: Optional[List[str]] = Field(
        None,
        description="Nuevas etiquetas"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Implementación de Cola Circular (Actualizado)",
                "difficulty": "AVANZADO",
                "policies": {
                    "max_help_level": "BAJO",
                    "block_complete_solutions": True,
                    "require_justification": True,
                    "allow_code_snippets": False,
                    "risk_thresholds": {
                        "ai_dependency": 0.5
                    }
                }
            }
        }


class ActivityResponse(BaseModel):
    """Response con información de una actividad"""

    id: str = Field(..., description="ID interno (UUID)")
    activity_id: str = Field(..., description="ID único de la actividad")
    title: str = Field(..., description="Título de la actividad")
    description: Optional[str] = Field(None, description="Descripción breve")
    instructions: str = Field(..., description="Consigna detallada")
    evaluation_criteria: List[str] = Field(default_factory=list, description="Criterios de evaluación")
    teacher_id: str = Field(..., description="ID del docente creador")
    policies: Dict[str, Any] = Field(..., description="Políticas pedagógicas")
    subject: Optional[str] = Field(None, description="Materia")
    difficulty: Optional[str] = Field(None, description="Nivel de dificultad")
    estimated_duration_minutes: Optional[int] = Field(None, description="Duración estimada en minutos")
    tags: List[str] = Field(default_factory=list, description="Etiquetas")
    status: str = Field(..., description="Estado: draft, active, archived")
    published_at: Optional[datetime] = Field(None, description="Fecha de publicación")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de última actualización")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "activity_id": "prog2_tp1_colas",
                "title": "Implementación de Cola Circular",
                "description": "Trabajo práctico sobre estructuras de datos tipo cola con implementación circular",
                "instructions": "Implementar una cola circular que...",
                "evaluation_criteria": [
                    "Correcta implementación de operaciones básicas",
                    "Manejo apropiado de condiciones de overflow/underflow",
                    "Justificación de decisiones de diseño"
                ],
                "teacher_id": "teacher_001",
                "policies": {
                    "max_help_level": "MEDIO",
                    "block_complete_solutions": True,
                    "require_justification": True,
                    "allow_code_snippets": False,
                    "risk_thresholds": {
                        "ai_dependency": 0.6,
                        "lack_justification": 0.3
                    }
                },
                "subject": "Programación II",
                "difficulty": "INTERMEDIO",
                "estimated_duration_minutes": 120,
                "tags": ["colas", "estructuras", "arreglos"],
                "status": "active",
                "published_at": "2025-11-18T10:00:00Z",
                "created_at": "2025-11-17T15:00:00Z",
                "updated_at": "2025-11-18T10:00:00Z"
            }
        }


class ActivityListResponse(BaseModel):
    """Response con lista de actividades"""

    activities: List[ActivityResponse] = Field(..., description="Lista de actividades")
    total: int = Field(..., description="Total de actividades")


class ActivityPublishRequest(BaseModel):
    """Request para publicar una actividad"""

    pass  # No requiere body, solo el activity_id en la URL


class ActivityArchiveRequest(BaseModel):
    """Request para archivar una actividad"""

    pass  # No requiere body, solo el activity_id en la URL