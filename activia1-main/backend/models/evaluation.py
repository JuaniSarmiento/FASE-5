"""
Modelos para el Evaluador de Procesos Cognitivos (E-IA-Proc)
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CompetencyLevel(str, Enum):
    """Nivel de competencia alcanzado"""
    INICIAL = "inicial"  # Principiante
    EN_DESARROLLO = "en_desarrollo"  # Desarrollando la competencia
    AUTONOMO = "autonomo"  # Autónomo
    EXPERTO = "experto"  # Nivel experto


class CognitivePhase(str, Enum):
    """Fases del proceso cognitivo"""
    PLANIFICACION = "planificacion"  # Planificación
    EXPLORACION = "exploracion"  # Exploración
    IMPLEMENTACION = "implementacion"  # Implementación
    DEPURACION = "depuracion"  # Depuración
    VALIDACION = "validacion"  # Validación
    REFLEXION = "reflexion"  # Reflexión metacognitiva


class EvaluationDimension(BaseModel):
    """Dimensión de evaluación"""
    name: str = Field(description="Nombre de la dimensión")
    description: str = Field(description="Descripción")
    level: CompetencyLevel = Field(description="Nivel alcanzado")
    score: float = Field(ge=0.0, le=10.0, description="Puntuación (0-10)")
    evidence: List[str] = Field(default_factory=list, description="Evidencias")
    strengths: List[str] = Field(default_factory=list, description="Fortalezas")
    weaknesses: List[str] = Field(default_factory=list, description="Debilidades")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones")


class ReasoningAnalysis(BaseModel):
    """Análisis del proceso de razonamiento"""
    cognitive_path: List[str] = Field(
        default_factory=list,
        description="Camino cognitivo seguido"
    )
    phases_completed: List[CognitivePhase] = Field(
        default_factory=list,
        description="Fases completadas"
    )
    strategy_changes: int = Field(0, description="Cambios de estrategia")
    self_corrections: int = Field(0, description="Autocorrecciones")
    ai_critiques: int = Field(0, description="Críticas a la IA")

    # Análisis de coherencia
    coherence_score: float = Field(
        ge=0.0, le=1.0,
        description="Coherencia entre decisiones y justificaciones"
    )
    conceptual_errors: List[str] = Field(
        default_factory=list,
        description="Errores conceptuales detectados"
    )
    logical_fallacies: List[str] = Field(
        default_factory=list,
        description="Falacias lógicas detectadas"
    )

    # Autorregulación
    planning_quality: float = Field(ge=0.0, le=1.0, description="Calidad de planificación")
    monitoring_evidence: List[str] = Field(
        default_factory=list,
        description="Evidencias de monitoreo"
    )
    self_explanation_quality: float = Field(
        ge=0.0, le=1.0,
        description="Calidad de autoexplicación"
    )


class GitAnalysis(BaseModel):
    """Análisis de evolución del código vía Git"""
    total_commits: int = Field(0, description="Total de commits")
    commit_messages_quality: float = Field(
        ge=0.0, le=1.0,
        description="Calidad de mensajes de commit"
    )
    suspicious_jumps: List[str] = Field(
        default_factory=list,
        description="Saltos abruptos sospechosos"
    )
    evolution_coherence: float = Field(
        ge=0.0, le=1.0,
        description="Coherencia de la evolución"
    )
    traces_linked: int = Field(0, description="Commits vinculados a trazas N4")


class EvaluationReport(BaseModel):
    """
    Informe de Evaluación Cognitiva (IEC) generado por E-IA-Proc.

    FIX 3.1 Cortez8: Cambiado timestamp a created_at para consistencia con ORM.
    Se mantiene alias 'timestamp' para backwards compatibility.
    """
    id: str = Field(description="ID del reporte")
    session_id: str = Field(description="ID de la sesión de aprendizaje")
    # FIX 3.1 Cortez8: Renombrado a created_at para consistencia con ORM
    created_at: datetime = Field(default_factory=datetime.now, alias="timestamp", description="Timestamp de creación")
    student_id: str = Field(description="ID del estudiante")
    activity_id: str = Field(description="ID de la actividad")

    # Análisis principal (Optional to align with ORM nullable=True)
    reasoning_analysis: Optional[ReasoningAnalysis] = Field(
        None,
        description="Análisis del razonamiento (puede ser None si aún no se ha procesado)"
    )
    git_analysis: Optional[GitAnalysis] = Field(
        None,
        description="Análisis de evolución Git"
    )

    # Dimensiones evaluadas
    dimensions: List[EvaluationDimension] = Field(
        default_factory=list,
        description="Dimensiones de evaluación"
    )

    # Análisis de dependencia IA
    ai_dependency_score: float = Field(
        ge=0.0, le=1.0,
        description="Nivel de dependencia de IA (0=independiente, 1=dependiente total)"
    )
    ai_usage_patterns: Dict[str, Any] = Field(
        default_factory=dict,
        description="Patrones de uso de IA"
    )

    # Mapa de razonamiento humano-IA
    reasoning_map: Dict[str, Any] = Field(
        default_factory=dict,
        description="Mapa visual del razonamiento híbrido"
    )

    # Riesgos cognitivos detectados
    cognitive_risks: List[str] = Field(
        default_factory=list,
        description="Riesgos cognitivos identificados"
    )

    # Evaluación general
    overall_competency_level: CompetencyLevel = Field(
        description="Nivel de competencia general"
    )
    overall_score: float = Field(
        ge=0.0, le=10.0,
        description="Puntuación general (0-10)"
    )

    # Fortalezas y áreas de mejora
    key_strengths: List[str] = Field(
        default_factory=list,
        description="Fortalezas principales"
    )
    improvement_areas: List[str] = Field(
        default_factory=list,
        description="Áreas de mejora"
    )

    # Recomendaciones
    recommendations_student: List[str] = Field(
        default_factory=list,
        description="Recomendaciones para el estudiante"
    )
    recommendations_teacher: List[str] = Field(
        default_factory=list,
        description="Recomendaciones para el docente"
    )

    # Metadata
    evaluator_version: str = Field(default="E-IA-Proc-v1.0")
    trace_sequences_analyzed: int = Field(0, description="Secuencias de trazas analizadas")

    class Config:
        # FIX 3.1 Cortez8: Permitir usar alias 'timestamp' para backwards compatibility
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "eval_001",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "student_123",
                "activity_id": "prog2_tp1",
                "created_at": "2025-11-18T10:30:00Z",
                "overall_competency_level": "en_desarrollo",
                "overall_score": 7.5,
                "key_strengths": [
                    "Buena descomposición del problema",
                    "Autocorrección efectiva"
                ],
                "improvement_areas": [
                    "Planificación inicial insuficiente",
                    "Justificación de decisiones mejorable"
                ]
            }
        }