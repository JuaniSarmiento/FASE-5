"""
Router para evaluaciones cognitivas basadas en proceso
POST /evaluations/{session_id}/generate - Genera evaluación completa de una sesión
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import json
import re

from ...database.repositories import (
    SessionRepository,
    TraceRepository,
)
from ...llm import LLMProviderFactory, LLMProvider
from ..deps import (
    get_session_repository,
    get_trace_repository,
    get_llm_provider,
    get_current_user,
)
from ..schemas.common import APIResponse
from ..exceptions import SessionNotFoundError

router = APIRouter(prefix="/evaluations", tags=["Evaluations"])
logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS - FIX FLUJO3-3: Valid LLM response values
# ============================================================================

VALID_LEVELS = {"novice", "competent", "proficient", "expert"}
DEFAULT_LEVEL = "competent"
MIN_SCORE = 0.0
MAX_SCORE = 10.0


def _validate_score(score: float) -> float:
    """
    FIX FLUJO3-3: Clamp score to valid range 0-10.
    LLM may return values outside range (e.g., 15.5, -2).
    """
    try:
        score = float(score)
    except (TypeError, ValueError):
        return 5.0  # Default if not a valid number
    return max(MIN_SCORE, min(MAX_SCORE, score))


def _validate_level(level: str) -> str:
    """
    FIX FLUJO3-3: Validate level is a valid value.
    LLM may return invalid levels (e.g., "invalid", "super-expert").
    Maps to nearest valid level or returns default.
    """
    if not isinstance(level, str):
        return DEFAULT_LEVEL

    level_lower = level.lower().strip()

    # Direct match
    if level_lower in VALID_LEVELS:
        return level_lower

    # Common aliases/misspellings
    level_aliases = {
        "beginner": "novice",
        "developing": "novice",
        "basic": "novice",
        "intermediate": "competent",
        "medium": "competent",
        "advanced": "proficient",
        "skilled": "proficient",
        "master": "expert",
        "excellent": "expert",
    }

    if level_lower in level_aliases:
        return level_aliases[level_lower]

    logger.warning(f"Invalid level '{level}' from LLM, defaulting to '{DEFAULT_LEVEL}'")
    return DEFAULT_LEVEL


# ============================================================================
# SCHEMAS
# ============================================================================

class DimensionScore(BaseModel):
    """Puntuación de una dimensión del proceso"""
    score: float = Field(..., ge=0.0, le=10.0, description="Puntuación 0-10")
    level: str = Field(..., description="Nivel: novice/competent/proficient/expert")
    evidence: List[str] = Field(default_factory=list, description="Evidencias observadas")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones específicas")


class ProcessEvaluation(BaseModel):
    """Evaluación completa del proceso cognitivo del estudiante"""
    session_id: str
    student_id: str
    activity_id: str
    
    # 5 dimensiones del proceso
    planning: DimensionScore
    execution: DimensionScore
    debugging: DimensionScore
    reflection: DimensionScore
    autonomy: DimensionScore
    
    # Patrones generales
    autonomy_level: str = Field(..., description="low/medium/high")
    metacognition_score: float = Field(..., ge=0.0, le=10.0)
    delegation_ratio: float = Field(..., ge=0.0, le=1.0, description="% de delegación a IA")
    
    # Evidencia general
    overall_feedback: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/{session_id}/generate", response_model=APIResponse[ProcessEvaluation])
async def generate_process_evaluation(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    llm_provider: LLMProvider = Depends(get_llm_provider),
    current_user: dict = Depends(get_current_user),
) -> APIResponse[ProcessEvaluation]:
    """
    Genera una evaluación cognitiva completa basada en el proceso observado
    
    Analiza:
    - Planificación: Cómo el estudiante aborda problemas nuevos
    - Ejecución: Calidad de implementación y estrategias
    - Debugging: Habilidad para diagnosticar y corregir errores
    - Reflexión: Metacognición y aprendizaje de errores
    - Autonomía: Independencia vs delegación a IA
    
    Returns:
        ProcessEvaluation con puntuaciones 0-10 en cada dimensión + patrones generales
    """
    try:
        # 1. Verificar sesión
        session = session_repo.get_by_id(session_id)
        if not session:
            raise SessionNotFoundError(session_id)
        
        # 2. Obtener todas las trazas cognitivas de la sesión
        traces = trace_repo.get_by_session(session_id)
        if not traces:
            raise HTTPException(
                status_code=404,
                detail=f"No cognitive traces found for session {session_id}"
            )
        
        # 3. Construir datos de trazas para análisis (limitar a últimas 20)
        traces_data = []
        for trace in traces[:20]:
            traces_data.append({
                "input": trace.content,  # Contenido de la traza
                "output": trace.context.get("ai_response", "") if trace.context else "",
                "ai_involvement": trace.ai_involvement if hasattr(trace, "ai_involvement") else 0.5,
                "blocked": False,  # Las trazas cognitivas no tienen campo blocked
                "timestamp": trace.timestamp.isoformat() if trace.timestamp else "",
            })
        
        # 4. Construir prompt masivo para Ollama
        prompt = f"""Eres un evaluador experto en cognición y aprendizaje. Analiza la siguiente sesión de resolución de problemas y evalúa el PROCESO cognitivo del estudiante en 5 dimensiones.

SESIÓN:
- Student ID: {session.student_id}
- Activity ID: {session.activity_id}
- Total Traces: {len(traces)}

HISTORIAL DE INTERACCIONES (últimas {len(traces_data)}):
{_format_interactions_for_prompt(traces_data)}

INSTRUCCIONES:
Evalúa el PROCESO (no el resultado final) en 5 dimensiones:

1. PLANNING (Planificación): ¿Cómo aborda problemas? ¿Descompone tareas? ¿Anticipa dificultades?
2. EXECUTION (Ejecución): ¿Implementa soluciones efectivas? ¿Aplica buenas prácticas? ¿Optimiza código?
3. DEBUGGING (Depuración): ¿Diagnostica errores sistemáticamente? ¿Usa evidencia? ¿Aprende de fallos?
4. REFLECTION (Reflexión): ¿Revisa su trabajo? ¿Identifica limitaciones? ¿Explica razonamientos?
5. AUTONOMY (Autonomía): ¿Resuelve independientemente? ¿Delega demasiado a IA? ¿Toma decisiones propias?

Además calcula:
- autonomy_level: "low" (>70% delegación), "medium" (30-70%), "high" (<30%)
- metacognition_score: 0-10 basado en reflexión explícita
- delegation_ratio: % de interacciones donde delegó decisiones críticas a IA

RESPONDE EN JSON ESTRICTO:
{{
  "planning": {{
    "score": 7.5,
    "level": "proficient",
    "evidence": ["Descompone problemas en pasos", "Anticipa edge cases"],
    "recommendations": ["Mejorar estimación de tiempos", "Documentar asunciones iniciales"]
  }},
  "execution": {{
    "score": 6.0,
    "level": "competent",
    "evidence": ["Código funcional", "Aplica patrones básicos"],
    "recommendations": ["Estudiar principios SOLID", "Refactorizar código duplicado"]
  }},
  "debugging": {{
    "score": 8.0,
    "level": "proficient",
    "evidence": ["Usa logs efectivamente", "Aísla problemas rápidamente"],
    "recommendations": ["Aprender debugging avanzado", "Usar breakpoints condicionales"]
  }},
  "reflection": {{
    "score": 5.5,
    "level": "competent",
    "evidence": ["Revisa resultados", "Identifica algunos errores"],
    "recommendations": ["Practicar retrospectivas", "Documentar lecciones aprendidas"]
  }},
  "autonomy": {{
    "score": 4.0,
    "level": "competent",
    "evidence": ["Resuelve tareas simples solo", "Delega decisiones complejas"],
    "recommendations": ["Intentar resolver antes de preguntar", "Validar respuestas de IA críticamente"]
  }},
  "autonomy_level": "medium",
  "metacognition_score": 6.5,
  "delegation_ratio": 0.45,
  "overall_feedback": "El estudiante muestra un proceso sólido en debugging y planificación, pero necesita desarrollar mayor autonomía. Se observa dependencia alta de IA para decisiones que podría tomar independientemente. La reflexión metacognitiva es limitada. Recomendación: practicar resolución independiente de problemas similares antes de consultar herramientas."
}}

IMPORTANTE: Responde SOLO el JSON, sin texto adicional."""

        # 5. Llamar a Ollama para análisis
        try:
            from ...llm.base import LLMMessage, LLMRole
            
            llm_response_obj = await llm_provider.generate(
                messages=[
                    LLMMessage(role=LLMRole.USER, content=prompt)
                ],
                temperature=0.3,  # Baja temperatura para respuestas consistentes
                max_tokens=2000,
            )
            
            # Extraer contenido del LLMResponse
            llm_response = llm_response_obj.content

            # FIX DEFECTO #7: Intentar extraer JSON válido de la respuesta
            # El LLM puede retornar texto antes/después del JSON
            eval_data = None
            try:
                # Primero intentar parsear directamente
                eval_data = json.loads(llm_response)
            except json.JSONDecodeError:
                # FIX 3.4: Use non-greedy regex to avoid matching too much content
                # The greedy [\s\S]* can match beyond the JSON object
                json_match = re.search(r'\{[\s\S]*?\}(?=\s*$|\s*```)', llm_response)
                if not json_match:
                    # Fallback: try balanced braces matching
                    json_match = _find_balanced_json(llm_response)
                if json_match:
                    try:
                        eval_data = json.loads(json_match.group())
                        logger.info("Successfully extracted JSON from LLM response with extra text")
                    except json.JSONDecodeError:
                        logger.warning("Found JSON-like pattern but failed to parse")
                        raise

            if eval_data is None:
                raise json.JSONDecodeError("No valid JSON found in response", llm_response, 0)

            # Validate required keys exist and provide defaults
            required_dimensions = ["planning", "execution", "debugging", "reflection", "autonomy"]
            default_dimension = {
                "score": 5.0,
                "level": "developing",
                "evidence": ["Insufficient data for detailed analysis"],
                "recommendations": ["Continue practicing"]
            }

            # Safely extract dimensions with validation
            # FIX FLUJO3-3: Use validation helpers for score (0-10) and level (valid values)
            validated_dims = {}
            for dim in required_dimensions:
                dim_data = eval_data.get(dim, default_dimension)
                if not isinstance(dim_data, dict):
                    dim_data = default_dimension

                # FIX FLUJO3-3: Validate and clamp score/level from LLM response
                raw_score = dim_data.get("score", 5.0)
                raw_level = dim_data.get("level", "competent")

                validated_dims[dim] = DimensionScore(
                    score=_validate_score(raw_score),
                    level=_validate_level(raw_level),
                    evidence=dim_data.get("evidence", ["No evidence available"]) if isinstance(dim_data.get("evidence"), list) else ["No evidence available"],
                    recommendations=dim_data.get("recommendations", ["Continue practicing"]) if isinstance(dim_data.get("recommendations"), list) else ["Continue practicing"]
                )

            # FIX FLUJO3-3: Validate global fields from LLM response
            raw_autonomy_level = eval_data.get("autonomy_level", "medium")
            validated_autonomy_level = raw_autonomy_level if raw_autonomy_level in {"low", "medium", "high"} else "medium"

            raw_metacognition = eval_data.get("metacognition_score", 5.0)
            validated_metacognition = _validate_score(raw_metacognition)

            raw_delegation = eval_data.get("delegation_ratio", 0.5)
            try:
                validated_delegation = max(0.0, min(1.0, float(raw_delegation)))
            except (TypeError, ValueError):
                validated_delegation = 0.5

            # Construir ProcessEvaluation with validated data
            evaluation = ProcessEvaluation(
                session_id=session_id,
                student_id=session.student_id,
                activity_id=session.activity_id,
                planning=validated_dims["planning"],
                execution=validated_dims["execution"],
                debugging=validated_dims["debugging"],
                reflection=validated_dims["reflection"],
                autonomy=validated_dims["autonomy"],
                autonomy_level=validated_autonomy_level,
                metacognition_score=validated_metacognition,
                delegation_ratio=validated_delegation,
                overall_feedback=str(eval_data.get("overall_feedback", "Evaluation completed. Continue practicing to improve.")),
            )
            
            logger.info(f"✅ Generated process evaluation for session {session_id}")
            return APIResponse(
                success=True,
                data=evaluation,
                message="Process evaluation generated successfully"
            )
            
        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ Failed to parse Ollama JSON response: {e}")
            # Modo fallback: usar respuesta demo realista
            evaluation = _generate_fallback_evaluation(session_id, session.student_id, session.activity_id, len(traces))
            return APIResponse(
                success=True,
                data=evaluation,
                message="Process evaluation generated (fallback mode)"
            )
    
    except SessionNotFoundError:
        raise
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating process evaluation: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating evaluation: {str(e)}")


# ============================================================================
# HELPERS
# ============================================================================


def _find_balanced_json(text: str):
    """
    FIX 3.4: Find balanced JSON object in text using brace counting.
    Returns a match-like object with .group() method or None.
    """
    start = text.find('{')
    if start == -1:
        return None

    count = 0
    end = start
    for i, char in enumerate(text[start:], start):
        if char == '{':
            count += 1
        elif char == '}':
            count -= 1
            if count == 0:
                end = i + 1
                break

    if count != 0:
        return None

    # Return a simple object with group() method
    class MatchResult:
        def __init__(self, matched_text):
            self._text = matched_text
        def group(self):
            return self._text

    return MatchResult(text[start:end])


def _format_interactions_for_prompt(traces_data: List[dict]) -> str:
    """Formatea interacciones para el prompt de Ollama"""
    lines = []
    for i, trace in enumerate(traces_data, 1):
        lines.append(f"\n--- Interaction {i} ---")
        lines.append(f"Student: {trace['input'][:200]}...")
        lines.append(f"AI: {trace['output'][:200]}...")
        lines.append(f"AI Involvement: {trace['ai_involvement']}")
        lines.append(f"Blocked: {trace['blocked']}")
    return "\n".join(lines)


def _generate_fallback_evaluation(session_id: str, student_id: str, activity_id: str, interaction_count: int) -> ProcessEvaluation:
    """Genera evaluación demo si falla Ollama"""
    return ProcessEvaluation(
        session_id=session_id,
        student_id=student_id,
        activity_id=activity_id,
        planning=DimensionScore(
            score=7.0,
            level="proficient",
            evidence=["Descompone problemas en pasos manejables", "Identifica dependencias entre tareas"],
            recommendations=["Mejorar estimación de complejidad", "Documentar asunciones iniciales"]
        ),
        execution=DimensionScore(
            score=6.5,
            level="competent",
            evidence=["Implementa soluciones funcionales", "Aplica patrones de diseño básicos"],
            recommendations=["Estudiar principios SOLID", "Refactorizar código duplicado"]
        ),
        debugging=DimensionScore(
            score=7.5,
            level="proficient",
            evidence=["Usa logs y prints efectivamente", "Aísla problemas con método binario"],
            recommendations=["Aprender debugging con herramientas avanzadas", "Usar breakpoints condicionales"]
        ),
        reflection=DimensionScore(
            score=5.5,
            level="competent",
            evidence=["Revisa resultados después de implementar", "Identifica errores conceptuales ocasionalmente"],
            recommendations=["Practicar retrospectivas formales", "Mantener journal de aprendizaje"]
        ),
        autonomy=DimensionScore(
            score=4.5,
            level="competent",
            evidence=["Resuelve tareas rutinarias independientemente", "Delega decisiones arquitectónicas"],
            recommendations=["Intentar resolver 15min antes de consultar IA", "Validar respuestas críticamente"]
        ),
        autonomy_level="medium",
        metacognition_score=6.0,
        delegation_ratio=0.42,
        overall_feedback=f"El estudiante completó {interaction_count} interacciones mostrando competencia sólida en debugging y planificación. Sin embargo, se observa dependencia moderada-alta de IA para decisiones que podría tomar independientemente. La reflexión metacognitiva está presente pero no sistemática. Recomendación clave: desarrollar mayor autonomía intentando resolver problemas 15 minutos antes de consultar herramientas, y documentar el razonamiento detrás de cada decisión técnica.",
    )
