"""
Schemas para evaluaciones de proceso (EvaluationDB)
FIX 3.1: Schemas faltantes para ORM models
FIX Cortez8: Correcciones de consistencia ORM vs Pydantic
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class EvaluationDimensionScore(BaseModel):
    """
    Score de una dimensión de evaluación.

    FIX 1.2 Cortez8: Cambiado de escala 0-1 a 0-10 para consistencia con ORM y Pydantic domain.
    """

    name: str = Field(..., description="Nombre de la dimensión")
    # FIX 1.2 Cortez8: Escala 0-10 para consistencia con EvaluationDimension en models/evaluation.py
    score: float = Field(..., ge=0, le=10, description="Score (0-10)")
    feedback: str = Field("", description="Feedback para esta dimensión")
    indicators: List[str] = Field(default_factory=list, description="Indicadores observados")


class EvaluationCreate(BaseModel):
    """
    Request para crear una nueva evaluación.

    FIX 1.1 Cortez8: Cambiado overall_score de 0-1 a 0-10 para consistencia con ORM.
    FIX 2.10 Cortez8: Agregados student_id y activity_id requeridos.
    FIX 3.3 Cortez8: Renombrado competency_level a overall_competency_level.
    """

    session_id: str = Field(..., description="ID de la sesión evaluada")
    # FIX 2.10 Cortez8: Campos requeridos que existen en ORM
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    evaluator_type: str = Field("E-IA-PROC", description="Tipo de evaluador (no persiste en ORM)")
    # FIX 1.1 Cortez8: Escala 0-10 para consistencia con ORM EvaluationDB
    overall_score: float = Field(..., ge=0, le=10, description="Score general (0-10)")
    # FIX 3.3 Cortez8: Renombrado para consistencia con ORM
    overall_competency_level: str = Field(..., description="Nivel de competencia: inicial, en_desarrollo, autonomo, experto")

    # Dimension scores
    dimensions: List[EvaluationDimensionScore] = Field(
        default_factory=list,
        description="Scores por dimensión"
    )

    # Analysis
    reasoning_analysis: Optional[Dict[str, Any]] = Field(None, description="Análisis del razonamiento")
    git_analysis: Optional[Dict[str, Any]] = Field(None, description="Análisis de commits/código")
    conceptual_errors: List[Dict[str, Any]] = Field(default_factory=list, description="Errores conceptuales detectados")

    # Recommendations (stored as single JSON in DB, split here for API clarity)
    recommendations_student: List[str] = Field(default_factory=list, description="Recomendaciones para el estudiante")
    recommendations_teacher: List[str] = Field(default_factory=list, description="Recomendaciones para el docente")

    # Metadata
    evaluation_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadatos adicionales")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "evaluator_type": "E-IA-PROC",
                "overall_score": 7.5,
                "overall_competency_level": "en_desarrollo",
                "dimensions": [
                    {"name": "Comprensión", "score": 8.0, "feedback": "Buena comprensión del problema", "indicators": []},
                    {"name": "Diseño", "score": 7.0, "feedback": "Diseño adecuado", "indicators": []},
                    {"name": "Implementación", "score": 7.5, "feedback": "Código funcional", "indicators": []}
                ],
                "reasoning_analysis": {"depth": "medium", "quality": 0.7},
                "git_analysis": {"commits": 5, "quality": 0.8},
                "conceptual_errors": [],
                "recommendations_student": ["Practicar más con estructuras recursivas"],
                "recommendations_teacher": ["Reforzar conceptos de complejidad algorítmica"]
            }
        }


class EvaluationResponse(BaseModel):
    """
    Response con información de una evaluación.

    FIX 2.2 Cortez8: Agregado ai_dependency_metrics.
    FIX 2.10 Cortez8: Agregados student_id y activity_id.
    FIX 3.3 Cortez8: Renombrado competency_level a overall_competency_level.
    """

    id: str = Field(..., description="ID de la evaluación")
    session_id: str = Field(..., description="ID de la sesión")
    # FIX 2.10 Cortez8: Campos que existen en ORM
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    # FIX 3.3 Cortez8: Renombrado para consistencia con ORM
    overall_competency_level: str = Field(..., description="Nivel de competencia")
    overall_score: float = Field(..., ge=0, le=10, description="Score general (0-10)")

    # Dimension scores
    dimensions: List[EvaluationDimensionScore] = Field(default_factory=list, description="Scores por dimensión")

    # Analysis
    reasoning_analysis: Optional[Dict[str, Any]] = Field(None, description="Análisis del razonamiento")
    git_analysis: Optional[Dict[str, Any]] = Field(None, description="Análisis de código/commits")

    # AI Dependency
    ai_dependency_score: float = Field(0.0, ge=0, le=1, description="Score de dependencia de IA (0-1)")
    # FIX 2.2 Cortez8: Agregado campo que existe en ORM
    ai_dependency_metrics: Optional[Dict[str, Any]] = Field(None, description="Métricas detalladas de dependencia IA")

    # Strengths and areas
    key_strengths: List[str] = Field(default_factory=list, description="Fortalezas principales")
    improvement_areas: List[str] = Field(default_factory=list, description="Áreas de mejora")

    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones generales (JSON de ORM)")

    # Metadata
    created_at: datetime = Field(..., description="Timestamp de creación")
    updated_at: datetime = Field(..., description="Timestamp de actualización")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "eval_xyz789",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "overall_competency_level": "en_desarrollo",
                "overall_score": 7.5,
                "dimensions": [
                    {"name": "Comprensión", "score": 8.0, "feedback": "Buena", "indicators": []}
                ],
                "reasoning_analysis": None,
                "git_analysis": None,
                "ai_dependency_score": 0.35,
                "ai_dependency_metrics": {"delegation_count": 2, "copy_paste_ratio": 0.1},
                "key_strengths": ["Buena descomposición del problema"],
                "improvement_areas": ["Justificación de decisiones"],
                "recommendations": ["Practicar más", "Reforzar conceptos"],
                "created_at": "2025-11-18T10:30:00Z",
                "updated_at": "2025-11-18T10:30:00Z"
            }
        }


class EvaluationListResponse(BaseModel):
    """Response con lista de evaluaciones"""

    evaluations: List[EvaluationResponse] = Field(..., description="Lista de evaluaciones")
    total: int = Field(..., description="Total de evaluaciones")
    session_id: Optional[str] = Field(None, description="ID de sesión si se filtró")


class ProcessEvaluationRequest(BaseModel):
    """Request para solicitar evaluación de proceso por LLM"""

    session_id: str = Field(..., description="ID de la sesión a evaluar")
    include_git_analysis: bool = Field(False, description="Incluir análisis de Git")
    include_risk_analysis: bool = Field(True, description="Incluir análisis de riesgos")
    evaluation_focus: Optional[List[str]] = Field(
        None,
        description="Dimensiones específicas a evaluar"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "include_git_analysis": True,
                "include_risk_analysis": True,
                "evaluation_focus": ["comprehension", "design", "implementation"]
            }
        }


class ProcessEvaluationResponse(BaseModel):
    """
    Response de evaluación de proceso generada por LLM.

    FIX 1.3 Cortez8: Cambiado overall_score a escala 0-10.
    FIX 3.3 Cortez8: Renombrado competency_level a overall_competency_level.
    """

    session_id: str = Field(..., description="ID de la sesión evaluada")
    evaluation_id: str = Field(..., description="ID de la evaluación creada")

    # Scores - FIX 1.3 Cortez8: Escala 0-10 para consistencia
    overall_score: float = Field(..., ge=0, le=10, description="Score general (0-10)")
    # FIX 3.3 Cortez8: Renombrado para consistencia
    overall_competency_level: str = Field(..., description="Nivel de competencia")
    ai_dependency_score: float = Field(..., ge=0, le=1, description="Score de dependencia de IA (0-1)")

    # Detailed analysis
    dimensions: List[EvaluationDimensionScore] = Field(..., description="Análisis por dimensión")
    strengths: List[str] = Field(default_factory=list, description="Fortalezas identificadas")
    areas_for_improvement: List[str] = Field(default_factory=list, description="Áreas de mejora")

    # Recommendations
    recommendations_student: List[str] = Field(default_factory=list, description="Para el estudiante")
    recommendations_teacher: List[str] = Field(default_factory=list, description="Para el docente")

    # Metadata
    traces_analyzed: int = Field(0, description="Trazas analizadas")
    risks_detected: int = Field(0, description="Riesgos detectados")
    evaluated_at: datetime = Field(..., description="Timestamp de evaluación")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "evaluation_id": "eval_xyz789",
                "overall_score": 7.5,
                "overall_competency_level": "en_desarrollo",
                "ai_dependency_score": 0.35,
                "dimensions": [
                    {"name": "Comprensión", "score": 8.0, "feedback": "Buena", "indicators": []}
                ],
                "strengths": ["Buen uso de estructuras de control"],
                "areas_for_improvement": ["Mejorar documentación"],
                "recommendations_student": ["Practicar más"],
                "recommendations_teacher": ["Asignar ejercicios de recursión"],
                "traces_analyzed": 15,
                "risks_detected": 2,
                "evaluated_at": "2025-11-18T10:30:00Z"
            }
        }
