"""
Schemas para riesgos detectados (RiskDB)
FIX 3.1: Schemas faltantes para ORM models
FIX Cortez8: Correcciones de consistencia ORM vs Pydantic
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator

from .enums import RiskLevel, RiskDimension

# FIX 4.6 Cortez8: Lista de tipos de riesgo válidos
VALID_RISK_TYPES = [
    # Cognitive (RC)
    "cognitive_delegation", "superficial_reasoning", "ai_dependency",
    "lack_justification", "no_self_regulation",
    # Ethical (RE)
    "academic_integrity", "undisclosed_ai_use", "plagiarism",
    # Epistemic (REp)
    "conceptual_error", "logical_fallacy", "uncritical_acceptance",
    # Technical (RT)
    "security_vulnerability", "poor_code_quality", "architectural_flaw",
    # Governance (RG)
    "policy_violation", "unauthorized_use", "automation_suspected",
]


class RiskCreate(BaseModel):
    """
    Request para crear un nuevo riesgo.

    FIX 2.6 Cortez8: Agregado campo impact.
    FIX 3.5 Cortez8: mitigation se mapea a recommendations[0] en ORM.
    FIX 4.6 Cortez8: Agregado validator para risk_type.
    """

    session_id: str = Field(..., description="ID de la sesión (requerido)")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    risk_type: str = Field(..., description="Tipo de riesgo (ver RiskType enum)")
    risk_level: RiskLevel = Field(..., description="Nivel: low, medium, high, critical, info")
    dimension: RiskDimension = Field(..., description="Dimensión: cognitive, ethical, epistemic, technical, governance")
    description: str = Field(..., description="Descripción del riesgo")
    # FIX 2.6 Cortez8: Campo que existe en ORM
    impact: Optional[str] = Field(None, description="Impacto potencial del riesgo")
    evidence: List[str] = Field(default_factory=list, description="Evidencias detectadas")
    # FIX 3.5 Cortez8: Se mapea a recommendations en ORM
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones de mitigación")
    pedagogical_intervention: Optional[str] = Field(None, description="Intervención pedagógica sugerida")
    trace_ids: List[str] = Field(default_factory=list, description="IDs de trazas relacionadas")

    # FIX 4.6 Cortez8: Validator para risk_type
    # FIX Cortez22 DEFECTO 3.8: Fixed no-op logic (v.upper().replace('_', '_').lower() was identical to v.lower())
    @field_validator('risk_type')
    @classmethod
    def validate_risk_type(cls, v: str) -> str:
        """Valida que risk_type sea un valor conocido (normalizado a lowercase)."""
        # Normalize: lowercase and ensure underscores are preserved
        normalized = v.lower().strip()

        if normalized not in VALID_RISK_TYPES:
            # Try alternative formats: spaces to underscores, hyphens to underscores
            alt_normalized = normalized.replace(' ', '_').replace('-', '_')
            if alt_normalized in VALID_RISK_TYPES:
                return alt_normalized

            raise ValueError(
                f"Tipo de riesgo desconocido: '{v}'. "
                f"Valores válidos: {', '.join(VALID_RISK_TYPES[:5])}..."
            )
        return normalized

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "risk_type": "cognitive_delegation",
                "risk_level": "high",
                "dimension": "cognitive",
                "description": "Estudiante delegando razonamiento crítico a la IA",
                "impact": "Pérdida de aprendizaje profundo",
                "evidence": ["Copia directa de código sugerido", "Sin justificación propia"],
                "recommendations": ["Exigir explicación del código antes de aceptar"],
                "pedagogical_intervention": "Modo socrático con preguntas guiadas",
                "trace_ids": ["trace_123", "trace_124"]
            }
        }


class RiskResponse(BaseModel):
    """
    Response con información de un riesgo.

    FIX 2.1 Cortez8: Agregados campos faltantes del ORM.
    """

    id: str = Field(..., description="ID del riesgo")
    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    risk_type: str = Field(..., description="Tipo de riesgo")
    risk_level: str = Field(..., description="Nivel de riesgo: low, medium, high, critical, info")
    dimension: str = Field(..., description="Dimensión del riesgo: cognitive, ethical, epistemic, technical, governance")
    description: str = Field(..., description="Descripción del riesgo")
    # FIX 2.1 Cortez8: Campo que existe en ORM
    impact: Optional[str] = Field(None, description="Impacto del riesgo")
    evidence: List[str] = Field(default_factory=list, description="Evidencias del riesgo")
    # FIX 2.1 Cortez8: Campos que existen en ORM
    trace_ids: List[str] = Field(default_factory=list, description="IDs de trazas relacionadas")
    root_cause: Optional[str] = Field(None, description="Causa raíz identificada")
    impact_assessment: Optional[str] = Field(None, description="Evaluación del impacto")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones de mitigación")
    pedagogical_intervention: Optional[str] = Field(None, description="Intervención pedagógica sugerida")

    # Status
    resolved: bool = Field(False, description="Si el riesgo fue resuelto")
    resolved_at: Optional[datetime] = Field(None, description="Cuando se resolvió")
    resolution_notes: Optional[str] = Field(None, description="Notas de resolución")
    # FIX 2.1 Cortez8: Campo que existe en ORM
    detected_by: str = Field("AR-IA", description="Agente que detectó el riesgo")

    # Timestamps
    created_at: datetime = Field(..., description="Timestamp de detección")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "risk_xyz789",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "risk_type": "cognitive_delegation",
                "risk_level": "high",
                "dimension": "cognitive",
                "description": "Estudiante delegando razonamiento crítico a la IA",
                "impact": "Pérdida de aprendizaje profundo",
                "evidence": ["Copia directa de código sugerido"],
                "trace_ids": ["trace_123"],
                "root_cause": "Falta de comprensión del problema",
                "impact_assessment": "Alto impacto en desarrollo de competencias",
                "recommendations": ["Exigir explicación del código"],
                "pedagogical_intervention": "Modo socrático",
                "resolved": False,
                "resolved_at": None,
                "resolution_notes": None,
                "detected_by": "AR-IA",
                "created_at": "2025-11-18T10:30:00Z"
            }
        }


class RiskListResponse(BaseModel):
    """Response con lista de riesgos"""

    risks: List[RiskResponse] = Field(..., description="Lista de riesgos")
    total: int = Field(..., description="Total de riesgos")
    session_id: Optional[str] = Field(None, description="ID de sesión si se filtró")


class RiskDimensionAnalysis(BaseModel):
    """Análisis de una dimensión de riesgo"""

    score: float = Field(..., ge=0, le=10, description="Score de riesgo (0-10)")
    level: RiskLevel = Field(..., description="Nivel de riesgo")
    indicators: List[str] = Field(default_factory=list, description="Indicadores detectados")


class RiskAnalysis5DResponse(BaseModel):
    """
    Response del análisis de riesgos en 5 dimensiones (AR-IA).

    FIX 1.4 Cortez8: Documentación de escalas
    - overall_score: 0-100 (porcentaje de riesgo total)
    - RiskDimensionAnalysis.score: 0-10 (score individual por dimensión)
    - La conversión es: overall = (sum(dimensions) / 5) * 10
    """

    session_id: str = Field(..., description="ID de la sesión analizada")
    # FIX 1.4 Cortez8: Escala 0-100 es intencional (porcentaje)
    overall_score: float = Field(..., ge=0, le=100, description="Score de riesgo general (0-100, porcentaje)")
    risk_level: RiskLevel = Field(..., description="Nivel de riesgo general")

    # 5 Dimensions
    dimensions: Dict[str, RiskDimensionAnalysis] = Field(
        ...,
        description="Análisis por dimensión: cognitive, ethical, epistemic, technical, governance"
    )

    # Top risks
    top_risks: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Principales riesgos detectados"
    )

    # Recommendations
    recommendations: List[str] = Field(
        default_factory=list,
        description="Recomendaciones de mitigación"
    )

    # Metadata
    analyzed_at: datetime = Field(..., description="Timestamp del análisis")
    traces_analyzed: int = Field(0, description="Número de trazas analizadas")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "overall_score": 35,
                "risk_level": "medium",
                "dimensions": {
                    "cognitive": {"score": 4.5, "level": "medium", "indicators": ["Delegación detectada"]},
                    "ethical": {"score": 2.0, "level": "low", "indicators": []},
                    "epistemic": {"score": 3.0, "level": "low", "indicators": []},
                    "technical": {"score": 2.5, "level": "low", "indicators": []},
                    "governance": {"score": 1.0, "level": "low", "indicators": []}
                },
                "top_risks": [
                    {
                        "dimension": "cognitive",
                        "description": "Delegación de razonamiento",
                        "severity": "medium",
                        "mitigation": "Exigir justificación explícita"
                    }
                ],
                "recommendations": [
                    "Incentivar al estudiante a explicar su razonamiento",
                    "Usar modo socrático con más frecuencia"
                ],
                "analyzed_at": "2025-11-18T10:30:00Z",
                "traces_analyzed": 15
            }
        }


class RiskResolveRequest(BaseModel):
    """Request para marcar un riesgo como resuelto"""

    resolution_notes: Optional[str] = Field(None, description="Notas sobre la resolución")

    class Config:
        json_schema_extra = {
            "example": {
                "resolution_notes": "Estudiante demostró comprensión en interacciones posteriores"
            }
        }
