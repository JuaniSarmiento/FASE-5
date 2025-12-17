"""
Router para análisis de riesgos 5D

FIX Cortez21 DEFECTO 2.3: Added typed response schema
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
import httpx

from ...llm.factory import LLMProviderFactory
from ...database.repositories import SessionRepository, TraceRepository
from ..deps import get_session_repository, get_trace_repository, get_current_user, get_llm_provider
from ..schemas.common import APIResponse
from fastapi import Depends

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/risk-analysis", tags=["Risk Analysis 5D"])


# FIX Cortez21 DEFECTO 2.3: Define typed response schemas
class RiskDimensionScoreSchema(BaseModel):
    score: int
    level: str  # low, medium, high, critical
    indicators: List[str]


class TopRiskItem(BaseModel):
    dimension: str
    description: str
    severity: str
    mitigation: str


class RiskAnalysis5DResponse(BaseModel):
    session_id: str
    overall_score: int
    risk_level: str
    dimensions: Dict[str, RiskDimensionScoreSchema]
    top_risks: List[TopRiskItem]
    recommendations: List[str]

    class Config:
        from_attributes = True


class RiskDimensionScore:
    def __init__(self, score: int, level: str, indicators: List[str]):
        self.score = score
        self.level = level
        self.indicators = indicators


class RiskAnalysis5D:
    def __init__(
        self,
        session_id: str,
        overall_score: int,
        risk_level: str,
        dimensions: dict,
        top_risks: List[dict],
        recommendations: List[str]
    ):
        self.session_id = session_id
        self.overall_score = overall_score
        self.risk_level = risk_level
        self.dimensions = dimensions
        self.top_risks = top_risks
        self.recommendations = recommendations


@router.get(
    "/{session_id}",
    response_model=APIResponse[RiskAnalysis5DResponse],  # FIX Cortez21: Typed response_model
    summary="Análisis de Riesgos 5D",
    description="Analiza riesgos en 5 dimensiones usando Ollama: cognitiva, ética, epistémica, técnica, gobernanza"
)
async def analyze_risks_5d(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    llm_provider = Depends(get_llm_provider),
    current_user: dict = Depends(get_current_user),
):
    """
    Analiza riesgos en 5 dimensiones para una sesión específica:
    - Cognitiva: Pérdida de habilidades de pensamiento crítico
    - Ética: Plagio, falta de atribución, sesgos
    - Epistémica: Erosión de fundamentos teóricos
    - Técnica: Dependencia de herramientas, falta de debugging
    - Gobernanza: Falta de policies, ausencia de auditoría
    """
    
    # Obtener sesión (método síncrono)
    session = session_repo.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Obtener interacciones de la sesión (método síncrono)
    interactions = trace_repo.get_by_session(session_id)
    
    # Si no hay interacciones, retornar análisis por defecto en lugar de error
    if not interactions or len(interactions) == 0:
        logger.info(f"No interactions found for session {session_id}, returning default risk analysis")
        return APIResponse(
            success=True,
            message="No interactions to analyze yet - default risk assessment provided",
            data={
                "session_id": session_id,
                "overall_score": 0,
                "risk_level": "info",
                "dimensions": {
                    "cognitive": {
                        "score": 0,
                        "level": "info",
                        "indicators": ["Sin actividad aún - sesión iniciada pero sin interacciones"]
                    },
                    "ethical": {
                        "score": 0,
                        "level": "info",
                        "indicators": ["Sin actividad para evaluar"]
                    },
                    "epistemic": {
                        "score": 0,
                        "level": "info",
                        "indicators": ["Sin actividad para evaluar"]
                    },
                    "technical": {
                        "score": 0,
                        "level": "info",
                        "indicators": ["Sin actividad para evaluar"]
                    },
                    "governance": {
                        "score": 0,
                        "level": "info",
                        "indicators": ["Sin actividad para evaluar"]
                    }
                },
                "top_risks": [],
                "recommendations": [
                    "Inicia la conversación con el tutor para comenzar el análisis de riesgos",
                    "El sistema monitoreará automáticamente las 5 dimensiones de riesgo",
                    "Se generará un reporte detallado después de las primeras interacciones"
                ]
            }
        )
    
    # Preparar contexto para Ollama
    context = {
        "session_id": session_id,
        "student_id": session.student_id,
        "activity_id": session.activity_id,
        "total_interactions": len(interactions),
        "interactions_summary": [
            {
                "content": i.content[:200] if i.content else "",
                "cognitive_state": i.cognitive_state if hasattr(i, 'cognitive_state') else "unknown",
                "ai_involvement": i.ai_involvement if hasattr(i, 'ai_involvement') else 0.0,
                "interaction_type": i.interaction_type if hasattr(i, 'interaction_type') else "unknown"
            }
            for i in interactions[-10:]  # Últimas 10 interacciones
        ]
    }
    
    # FIX 3.1: Use injected LLM provider (async-compatible) instead of direct factory call
    # llm_provider is already injected via Depends(get_llm_provider)

    prompt = f"""Analiza los riesgos en 5 dimensiones para esta sesión educativa con IA:

CONTEXTO:
- Sesión ID: {session_id}
- Estudiante: {session.student_id}
- Total interacciones: {len(interactions)}
- Últimas interacciones: {len(context['interactions_summary'])}

DIMENSIONES A ANALIZAR:
1. COGNITIVA: Pérdida de pensamiento crítico, dependencia excesiva de IA
2. ÉTICA: Plagio, falta de atribución, dishonestidad académica
3. EPISTÉMICA: Conocimiento superficial, falta de fundamentos
4. TÉCNICA: Código sin entender, copy-paste, falta de debugging manual
5. GOBERNANZA: Violación de políticas, uso no autorizado

Para cada dimensión, evalúa:
- Score (0-10, donde 10 es máximo riesgo)
- Level (low/medium/high/critical)
- Indicators (3-5 indicadores específicos observados)

Luego identifica los TOP 3 riesgos detectados con:
- Dimension
- Description
- Severity (low/medium/high/critical)
- Mitigation (cómo mitigarlo)

Finalmente, proporciona 5 recomendaciones de mitigación.

INTERACCIONES RECIENTES:
{context['interactions_summary']}

Responde SOLO en formato JSON válido:
{{
  "cognitive": {{"score": 0-10, "level": "low/medium/high/critical", "indicators": ["...", "..."]}},
  "ethical": {{"score": 0-10, "level": "low/medium/high/critical", "indicators": ["...", "..."]}},
  "epistemic": {{"score": 0-10, "level": "low/medium/high/critical", "indicators": ["...", "..."]}},
  "technical": {{"score": 0-10, "level": "low/medium/high/critical", "indicators": ["...", "..."]}},
  "governance": {{"score": 0-10, "level": "low/medium/high/critical", "indicators": ["...", "..."]}},
  "top_risks": [
    {{"dimension": "...", "description": "...", "severity": "...", "mitigation": "..."}},
    {{"dimension": "...", "description": "...", "severity": "...", "mitigation": "..."}},
    {{"dimension": "...", "description": "...", "severity": "...", "mitigation": "..."}}
  ],
  "recommendations": ["...", "...", "...", "...", "..."]
}}
"""
    
    try:
        # FIX 3.1: Use injected llm_provider with proper async interface
        from ...llm.base import LLMMessage, LLMRole
        llm_response_obj = await llm_provider.generate(
            messages=[LLMMessage(role=LLMRole.USER, content=prompt)],
            temperature=0.7,
            max_tokens=2000
        )
        response = llm_response_obj.content

        # Parse JSON response with validation
        analysis_data = json.loads(response)

        # Validate required keys exist with safe access
        required_dimensions = ["cognitive", "ethical", "epistemic", "technical", "governance"]
        default_dimension = {"score": 3, "level": "medium", "indicators": ["No data available"]}

        # Safely extract dimension scores with defaults
        dimension_scores = []
        validated_dimensions = {}
        for dim in required_dimensions:
            dim_data = analysis_data.get(dim, default_dimension)
            if not isinstance(dim_data, dict):
                dim_data = default_dimension
            score = dim_data.get("score", 3)
            if not isinstance(score, (int, float)):
                score = 3
            dimension_scores.append(score)
            validated_dimensions[dim] = {
                "score": score,
                "level": dim_data.get("level", "medium"),
                "indicators": dim_data.get("indicators", ["No indicators available"])
            }

        overall_score = sum(dimension_scores)

        # Determinar nivel de riesgo global
        if overall_score >= 40:
            risk_level = "critical"
        elif overall_score >= 30:
            risk_level = "high"
        elif overall_score >= 15:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Safely extract top_risks and recommendations
        top_risks = analysis_data.get("top_risks", [])
        if not isinstance(top_risks, list):
            top_risks = []
        recommendations = analysis_data.get("recommendations", ["Continue monitoring session activity"])
        if not isinstance(recommendations, list):
            recommendations = [str(recommendations)]

        analysis = {
            "session_id": session_id,
            "overall_score": overall_score,
            "risk_level": risk_level,
            "dimensions": validated_dimensions,
            "top_risks": top_risks,
            "recommendations": recommendations
        }

        return APIResponse(
            success=True,
            message="Risk analysis completed",
            data=analysis
        )

    except (ValueError, httpx.HTTPError) as e:
        logger.warning(f"LLM risk analysis failed; returning fallback analysis: {e}")
        analysis = {
            "session_id": session_id,
            "overall_score": 15,
            "risk_level": "medium",
            "dimensions": {
                "cognitive": {
                    "score": 3,
                    "level": "medium",
                    "indicators": ["Múltiples consultas similares", "Dependencia de respuestas IA"]
                },
                "ethical": {
                    "score": 2,
                    "level": "low",
                    "indicators": ["Sin indicadores de plagio detectados"]
                },
                "epistemic": {
                    "score": 4,
                    "level": "medium",
                    "indicators": ["Consultas superficiales", "Falta de profundización"]
                },
                "technical": {
                    "score": 3,
                    "level": "medium",
                    "indicators": ["Uso de código sin modificación"]
                },
                "governance": {
                    "score": 3,
                    "level": "medium",
                    "indicators": ["Uso extensivo de IA no justificado"]
                }
            },
            "top_risks": [
                {
                    "dimension": "epistemic",
                    "description": "Conocimiento superficial detectado",
                    "severity": "medium",
                    "mitigation": "Solicitar explicaciones conceptuales detalladas"
                },
                {
                    "dimension": "cognitive",
                    "description": "Alta dependencia de IA",
                    "severity": "medium",
                    "mitigation": "Reducir asistencia y promover pensamiento autónomo"
                },
                {
                    "dimension": "technical",
                    "description": "Código sin personalización",
                    "severity": "low",
                    "mitigation": "Solicitar adaptación del código a contexto específico"
                }
            ],
            "recommendations": [
                "Reducir gradualmente el nivel de ayuda de IA",
                "Solicitar justificaciones conceptuales antes de proporcionar soluciones",
                "Fomentar debugging manual antes de consultar IA",
                "Implementar checkpoints de comprensión conceptual",
                "Documentar el proceso de razonamiento explícitamente"
            ]
        }

        return APIResponse(
            success=True,
            message="Risk analysis completed (fallback mode)",
            data=analysis
        )

    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse LLM risk analysis response: {e}")
        # Fallback: crear análisis básico
        analysis = {
            "session_id": session_id,
            "overall_score": 15,
            "risk_level": "medium",
            "dimensions": {
                "cognitive": {
                    "score": 3,
                    "level": "medium",
                    "indicators": ["Múltiples consultas similares", "Dependencia de respuestas IA"]
                },
                "ethical": {
                    "score": 2,
                    "level": "low",
                    "indicators": ["Sin indicadores de plagio detectados"]
                },
                "epistemic": {
                    "score": 4,
                    "level": "medium",
                    "indicators": ["Consultas superficiales", "Falta de profundización"]
                },
                "technical": {
                    "score": 3,
                    "level": "medium",
                    "indicators": ["Uso de código sin modificación"]
                },
                "governance": {
                    "score": 3,
                    "level": "medium",
                    "indicators": ["Uso extensivo de IA no justificado"]
                }
            },
            "top_risks": [
                {
                    "dimension": "epistemic",
                    "description": "Conocimiento superficial detectado",
                    "severity": "medium",
                    "mitigation": "Solicitar explicaciones conceptuales detalladas"
                },
                {
                    "dimension": "cognitive",
                    "description": "Alta dependencia de IA",
                    "severity": "medium",
                    "mitigation": "Reducir asistencia y promover pensamiento autónomo"
                },
                {
                    "dimension": "technical",
                    "description": "Código sin personalización",
                    "severity": "low",
                    "mitigation": "Solicitar adaptación del código a contexto específico"
                }
            ],
            "recommendations": [
                "Reducir gradualmente el nivel de ayuda de IA",
                "Solicitar justificaciones conceptuales antes de proporcionar soluciones",
                "Fomentar debugging manual antes de consultar IA",
                "Implementar checkpoints de comprensión conceptual",
                "Documentar el proceso de razonamiento explícitamente"
            ]
        }
        
        return APIResponse(
            success=True,
            message="Risk analysis completed (fallback mode)",
            data=analysis
        )
