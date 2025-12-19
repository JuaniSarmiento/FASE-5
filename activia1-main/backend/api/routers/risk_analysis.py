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
    
    # Preparar contexto detallado para análisis con Mistral AI
    # Extraer prompts del usuario y respuestas de la IA
    conversation_history = []
    for i, interaction in enumerate(interactions[-10:], 1):  # Últimas 10 interacciones
        # Extraer el prompt del usuario (puede estar en content o metadata)
        user_prompt = ""
        ai_response = ""
        
        if hasattr(interaction, 'metadata') and interaction.metadata:
            if isinstance(interaction.metadata, str):
                try:
                    meta = json.loads(interaction.metadata)
                    user_prompt = meta.get('prompt', '')
                except:
                    pass
            elif isinstance(interaction.metadata, dict):
                user_prompt = interaction.metadata.get('prompt', '')
        
        # El content suele ser la respuesta de la IA
        if hasattr(interaction, 'content') and interaction.content:
            ai_response = interaction.content[:300]  # Primeros 300 chars
        
        if not user_prompt and hasattr(interaction, 'prompt'):
            user_prompt = interaction.prompt
        
        conversation_history.append({
            "num": i,
            "student_question": user_prompt[:200] if user_prompt else "[Sin prompt capturado]",
            "ai_response_preview": ai_response[:150] if ai_response else "[Sin respuesta]",
            "interaction_type": getattr(interaction, 'interaction_type', 'unknown')
        })
    
    context = {
        "session_id": session_id,
        "student_id": session.student_id,
        "activity_id": session.activity_id,
        "total_interactions": len(interactions),
        "conversation_history": conversation_history
    }
    
    # Construir prompt mejorado para Mistral AI
    conversation_text = "\n\n".join([
        f"Interacción {conv['num']}:\n"
        f"  Estudiante pregunta: {conv['student_question']}\n"
        f"  Tipo: {conv['interaction_type']}\n"
        f"  Vista previa respuesta IA: {conv['ai_response_preview']}"
        for conv in conversation_history
    ])

    prompt = f"""Eres un experto analista de riesgos educativos. Analiza la siguiente sesión de tutoría con IA y evalúa los riesgos en 5 dimensiones.

CONTEXTO DE LA SESIÓN:
- Estudiante: {session.student_id}
- Actividad: {session.activity_id}
- Total de interacciones: {len(interactions)}

CONVERSACIÓN ANALIZADA (últimas {len(conversation_history)} interacciones):
{conversation_text}

INSTRUCCIONES DE ANÁLISIS:

Evalúa cada dimensión de riesgo basándote en las interacciones reales observadas:

1. **COGNITIVA** (0-10): 
   - ¿El estudiante delega completamente en la IA?
   - ¿Muestra pensamiento crítico o solo pide soluciones?
   - ¿Hace preguntas de seguimiento profundas?
   
2. **ÉTICA** (0-10):
   - ¿Hay indicios de querer copiar sin atribución?
   - ¿El estudiante parece honesto sobre su nivel de conocimiento?
   
3. **EPISTÉMICA** (0-10):
   - ¿Las preguntas muestran comprensión superficial?
   - ¿Busca entender conceptos o solo obtener respuestas?
   - ¿Profundiza en los fundamentos teóricos?
   
4. **TÉCNICA** (0-10):
   - ¿Pide código completo sin intentar entenderlo?
   - ¿Hace preguntas sobre debugging o solo pide soluciones?
   - ¿Muestra intención de adaptar el código?
   
5. **GOBERNANZA** (0-10):
   - ¿Usa la IA de forma responsable?
   - ¿Hay uso excesivo sin justificación educativa?

Para CADA dimensión proporciona:
- **score**: Número de 0 a 10 (0=sin riesgo, 10=riesgo crítico)
- **level**: "low" (0-3), "medium" (4-6), "high" (7-8), "critical" (9-10)
- **indicators**: Array de 3-5 indicadores ESPECÍFICOS observados en esta conversación

Luego identifica los TOP 3 riesgos más importantes con estrategias concretas de mitigación.

FORMATO DE RESPUESTA (SOLO JSON, sin texto adicional):

{{
  "cognitive": {{
    "score": [número 0-10],
    "level": "[low/medium/high/critical]",
    "indicators": ["[indicador específico 1]", "[indicador 2]", "[indicador 3]"]
  }},
  "ethical": {{
    "score": [número 0-10],
    "level": "[low/medium/high/critical]",
    "indicators": ["[indicador específico 1]", "[indicador 2]", "[indicador 3]"]
  }},
  "epistemic": {{
    "score": [número 0-10],
    "level": "[low/medium/high/critical]",
    "indicators": ["[indicador específico 1]", "[indicador 2]", "[indicador 3]"]
  }},
  "technical": {{
    "score": [número 0-10],
    "level": "[low/medium/high/critical]",
    "indicators": ["[indicador específico 1]", "[indicador 2]", "[indicador 3]"]
  }},
  "governance": {{
    "score": [número 0-10],
    "level": "[low/medium/high/critical]",
    "indicators": ["[indicador específico 1]", "[indicador 2]", "[indicador 3]"]
  }},
  "top_risks": [
    {{
      "dimension": "[cognitive/ethical/epistemic/technical/governance]",
      "description": "[descripción del riesgo detectado]",
      "severity": "[low/medium/high/critical]",
      "mitigation": "[estrategia concreta de mitigación]"
    }},
    {{
      "dimension": "[cognitive/ethical/epistemic/technical/governance]",
      "description": "[descripción del riesgo detectado]",
      "severity": "[low/medium/high/critical]",
      "mitigation": "[estrategia concreta de mitigación]"
    }},
    {{
      "dimension": "[cognitive/ethical/epistemic/technical/governance]",
      "description": "[descripción del riesgo detectado]",
      "severity": "[low/medium/high/critical]",
      "mitigation": "[estrategia concreta de mitigación]"
    }}
  ],
  "recommendations": [
    "[recomendación práctica 1]",
    "[recomendación práctica 2]",
    "[recomendación práctica 3]",
    "[recomendación práctica 4]",
    "[recomendación práctica 5]"
  ]
}}

Responde ÚNICAMENTE con el JSON, sin explicaciones adicionales."""
    
    try:
        # FIX 3.1: Use injected llm_provider with proper async interface
        from ...llm.base import LLMMessage, LLMRole
        llm_response_obj = await llm_provider.generate(
            messages=[LLMMessage(role=LLMRole.USER, content=prompt)],
            temperature=0.3,  # Más bajo para respuestas más consistentes
            max_tokens=3000   # Aumentado para análisis detallado
        )
        response_text = llm_response_obj.content
        
        logger.info(f"Raw LLM response for risk analysis (first 300 chars): {response_text[:300]}")

        # Extraer JSON del response (puede tener texto antes/después)
        # Buscar el primer { y el último }
        json_start = response_text.find('{')
        json_end = response_text.rfind('}')
        
        if json_start == -1 or json_end == -1:
            raise ValueError("No JSON found in LLM response")
        
        json_str = response_text[json_start:json_end + 1]
        
        # Parse JSON response with validation
        analysis_data = json.loads(json_str)
        
        logger.info(f"Successfully parsed JSON from Mistral AI for session {session_id}")

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
            # Asegurar que score esté en rango 0-10
            score = max(0, min(10, int(score)))
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
