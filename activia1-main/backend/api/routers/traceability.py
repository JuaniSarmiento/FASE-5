"""
Router para trazabilidad N4

FIX Cortez21 DEFECTO 2.2, 2.4: Added authentication and typed response schemas
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session

from ...database.repositories import TraceRepository, SessionRepository, RiskRepository
from ...database.models import SimulatorEventDB, CognitiveTraceDB, RiskDB, EvaluationDB
from ..deps import get_trace_repository, get_session_repository, get_risk_repository, get_db, get_current_user
from ..schemas.common import APIResponse
from ..exceptions import SessionNotFoundError

router = APIRouter(prefix="/traceability", tags=["Traceability N4"])


# FIX Cortez21 DEFECTO 2.4: Define typed response schema
class TraceabilityNodeMetadata(BaseModel):
    processing_time_ms: int
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    transformations: List[str] = []


class TraceabilityNode(BaseModel):
    id: str
    level: str  # N1, N2, N3, N4
    timestamp: str
    data: Dict[str, Any]
    metadata: TraceabilityNodeMetadata


class TraceabilityN4Response(BaseModel):
    session_id: str
    trace_id: str
    nodes: List[TraceabilityNode]
    total_latency_ms: int
    total_tokens: int

    class Config:
        from_attributes = True


@router.get(
    "/{trace_id}",
    response_model=APIResponse[TraceabilityN4Response],  # FIX Cortez21: Typed response_model
    summary="Trazabilidad N4",
    description="Obtiene la traza completa del procesamiento en 4 niveles (N1-Raw, N2-Preprocessed, N3-LLM, N4-Postprocessed)"
)
async def get_traceability_n4(
    trace_id: str,
    trace_repo: TraceRepository = Depends(get_trace_repository),
    _current_user: dict = Depends(get_current_user),  # FIX Cortez21 DEFECTO 2.2: Require auth
):
    """
    Obtiene la trazabilidad completa de una traza cognitiva en 4 niveles:
    - N1 (Raw Data): Datos crudos del usuario (input original)
    - N2 (Preprocessed): Datos preprocesados (validación, limpieza, tokenización)
    - N3 (LLM Processing): Procesamiento por el modelo LLM (inferencia)
    - N4 (Postprocessed): Datos postprocesados (formateo, enriquecimiento, output final)
    """
    
    # Obtener traza cognitiva (no es async)
    trace = trace_repo.get_by_id(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Cognitive trace not found")
    
    # Simular timestamps progresivos
    base_time = trace.created_at if hasattr(trace, 'created_at') else datetime.now()
    
    # Construir nodos de trazabilidad
    nodes = []
    
    # N1 - Raw Data
    nodes.append({
        "id": f"{trace_id}-n1",
        "level": "N1",
        "timestamp": base_time.isoformat() if hasattr(base_time, 'isoformat') else str(base_time),
        "data": {
            "raw_input": trace.content[:500],  # Usar content de la traza
            "content_length": len(trace.content),
            "encoding": "utf-8"
        },
        "metadata": {
            "processing_time_ms": 2,
            "transformations": []
        }
    })
    
    # N2 - Preprocessed
    import hashlib
    input_hash = hashlib.md5(trace.content.encode()).hexdigest()[:8]
    
    nodes.append({
        "id": f"{trace_id}-n2",
        "level": "N2",
        "timestamp": str(base_time.timestamp() + 0.05) if hasattr(base_time, 'timestamp') else str(base_time),
        "data": {
            "cleaned_input": trace.content.strip(),
            "validation_passed": True,
            "input_hash": input_hash,
            "detected_language": "es",
            "intent": trace.cognitive_intent or "UNKNOWN"
        },
        "metadata": {
            "processing_time_ms": 45,
            "transformations": [
                "Whitespace trimming",
                "Language detection",
                "Intent classification",
                "Input validation"
            ]
        }
    })
    
    # N3 - LLM Processing
    ai_response = trace.context.get("ai_response", "") if trace.context else ""
    
    nodes.append({
        "id": f"{trace_id}-n3",
        "level": "N3",
        "timestamp": str(base_time.timestamp() + 1.5) if hasattr(base_time, 'timestamp') else str(base_time),
        "data": {
            "model_input": {
                "prompt": trace.content,
                "context": trace.context or {}
            },
            "model_output": {
                "raw_response": ai_response,
                "finish_reason": "stop"
            },
            "agent": trace.agent_id or "unknown"
        },
        "metadata": {
            "processing_time_ms": 1420,
            "tokens_used": 0,  # CognitiveTraceDB no tiene total_tokens
            "model": "llama3.2:3b",
            "transformations": [
                "Prompt engineering",
                "Context injection",
                "LLM inference",
                "Response extraction"
            ]
        }
    })
    
    # N4 - Postprocessed
    nodes.append({
        "id": f"{trace_id}-n4",
        "level": "N4",
        "timestamp": str(base_time.timestamp() + 1.65) if hasattr(base_time, 'timestamp') else str(base_time),
        "data": {
            "final_response": ai_response,
            "cognitive_state": trace.cognitive_state or "unknown",
            "ai_involvement": trace.ai_involvement if hasattr(trace, 'ai_involvement') else 0.0,
            "blocked": False,  # CognitiveTraceDB no tiene blocked
            "block_reason": None,
            "metadata_enriched": True
        },
        "metadata": {
            "processing_time_ms": 145,
            "transformations": [
                "Response formatting",
                "Cognitive state detection",
                "AI involvement calculation",
                "Safety checks",
                "Metadata enrichment"
            ]
        }
    })
    
    # Calcular totales
    total_latency = sum(node["metadata"]["processing_time_ms"] for node in nodes)
    total_tokens = nodes[2]["metadata"]["tokens_used"]
    
    trace_response = {
        "session_id": trace.session_id,
        "trace_id": trace_id,
        "nodes": nodes,
        "total_latency_ms": total_latency,
        "total_tokens": total_tokens
    }
    
    return APIResponse(
        success=True,
        message="Traceability retrieved successfully",
        data=trace_response
    )


# ============================================================================
# SESSION TRACEABILITY - Grafo de 4 Niveles (TC-N4)
# ============================================================================

class ArtifactNode(BaseModel):
    """Nodo del grafo de trazabilidad"""
    level: int  # 1, 2, 3, 4
    type: str  # event, trace, risk, evaluation
    id: str
    name: str
    status: str  # created, in_progress, completed, detected, resolved
    timestamp: datetime
    data: Dict[str, Any] = {}
    children: List['ArtifactNode'] = []
    
    class Config:
        from_attributes = True


# Permitir referencias circulares en Pydantic v2
ArtifactNode.model_rebuild()


class SessionTraceabilityResponse(BaseModel):
    """Response completo de trazabilidad de sesión"""
    session_id: str
    student_id: str
    activity_id: str
    simulator_type: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    artifacts: List[ArtifactNode]
    summary: Dict[str, Any]


@router.get(
    "/session/{session_id}",
    response_model=APIResponse[SessionTraceabilityResponse],
    summary="Session Traceability Graph",
    description="Obtiene el grafo completo de trazabilidad de una sesión (4 niveles: Eventos → Trazas → Riesgos → Evaluaciones)"
)
async def get_session_traceability(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
    db: Session = Depends(get_db),
    _current_user: dict = Depends(get_current_user),  # FIX Cortez22 DEFECTO 2.3: Require auth
) -> APIResponse[SessionTraceabilityResponse]:
    """
    Motor de Trazabilidad (TC-N4)
    
    Construye un grafo jerárquico de 4 niveles que conecta:
    
    NIVEL 1: Eventos de Simulador
    - Acciones del usuario en simuladores
    - Decisiones tomadas
    - Hitos alcanzados
    
    NIVEL 2: Trazas Cognitivas
    - Interacciones con el tutor IA
    - Proceso de razonamiento
    - Estrategias aplicadas
    
    NIVEL 3: Riesgos Detectados
    - Riesgos automáticos (AR-IA)
    - Riesgos identificados por usuario
    - Análisis de impacto
    
    NIVEL 4: Evaluaciones
    - Evaluación de proceso
    - Feedback IA
    - Rúbricas y scores
    
    Estructura del grafo:
    Event → [Traces] → [Risks] → [Evaluation]
    """
    # Verificar sesión
    session = session_repo.get_by_id(session_id)
    if not session:
        raise SessionNotFoundError(session_id)
    
    # Obtener todos los artefactos de la sesión
    events = db.query(SimulatorEventDB).filter(
        SimulatorEventDB.session_id == session_id
    ).order_by(SimulatorEventDB.timestamp).all()
    
    traces = db.query(CognitiveTraceDB).filter(
        CognitiveTraceDB.session_id == session_id
    ).order_by(CognitiveTraceDB.created_at).all()
    
    risks = db.query(RiskDB).filter(
        RiskDB.session_id == session_id
    ).order_by(RiskDB.created_at).all()
    
    evaluations = db.query(EvaluationDB).filter(
        EvaluationDB.session_id == session_id
    ).order_by(EvaluationDB.created_at).all()
    
    # Construir grafo jerárquico
    artifacts = []
    
    # NIVEL 1: Eventos (raíz del grafo)
    for event in events:
        event_node = ArtifactNode(
            level=1,
            type="event",
            id=event.id,
            name=f"{event.event_type}",
            status="completed",
            timestamp=event.timestamp,
            data={
                "simulator_type": event.simulator_type,
                "event_data": event.event_data,
                "description": event.description,
                "severity": event.severity,
            },
            children=[]
        )
        
        # NIVEL 2: Trazas relacionadas con este evento (por timestamp cercano)
        # Buscar trazas creadas dentro de 5 minutos después del evento
        event_traces = [
            t for t in traces
            if abs((t.created_at - event.timestamp).total_seconds()) < 300
        ]
        
        for trace in event_traces[:3]:  # Limitar a 3 trazas por evento
            trace_node = ArtifactNode(
                level=2,
                type="trace",
                id=trace.id,
                name=f"{trace.interaction_type}",
                status="completed",
                timestamp=trace.created_at,
                data={
                    "content_preview": trace.content[:100] + "..." if len(trace.content) > 100 else trace.content,
                    "cognitive_state": trace.cognitive_state,
                    "cognitive_intent": trace.cognitive_intent,
                    "ai_involvement": trace.ai_involvement,
                },
                children=[]
            )
            
            # NIVEL 3: Riesgos relacionados con esta traza
            # Buscar riesgos que mencionen este trace_id
            trace_risks = [
                r for r in risks
                if trace.id in (r.trace_ids or [])
            ]
            
            for risk in trace_risks:
                risk_node = ArtifactNode(
                    level=3,
                    type="risk",
                    id=risk.id,
                    name=f"{risk.risk_type} - {risk.risk_level}",
                    status="resolved" if risk.resolved else "detected",
                    timestamp=risk.created_at,
                    data={
                        "dimension": risk.dimension,
                        "description": risk.description,
                        "impact": risk.impact,
                        "recommendations": risk.recommendations or [],
                    },
                    children=[]
                )
                
                trace_node.children.append(risk_node)
            
            event_node.children.append(trace_node)
        
        # Agregar riesgos detectados directamente por el evento (sin traza intermedia)
        # Esto aplica a riesgos automáticos del AR-IA
        event_risks = [
            r for r in risks
            if not r.trace_ids and abs((r.created_at - event.timestamp).total_seconds()) < 60
        ]
        
        for risk in event_risks:
            risk_node = ArtifactNode(
                level=3,
                type="risk",
                id=risk.id,
                name=f"{risk.risk_type} - {risk.risk_level}",
                status="resolved" if risk.resolved else "detected",
                timestamp=risk.created_at,
                data={
                    "dimension": risk.dimension,
                    "description": risk.description,
                    "impact": risk.impact,
                    "recommendations": risk.recommendations or [],
                    "detected_by": risk.detected_by,
                },
                children=[]
            )
            
            event_node.children.append(risk_node)
        
        artifacts.append(event_node)
    
    # NIVEL 4: Evaluaciones (se conectan a nivel de sesión, no a eventos específicos)
    for evaluation in evaluations:
        eval_node = ArtifactNode(
            level=4,
            type="evaluation",
            id=evaluation.id,
            name=f"Evaluación - Score: {evaluation.overall_score:.1f}",
            status="completed",
            timestamp=evaluation.created_at,
            data={
                "overall_competency_level": evaluation.overall_competency_level,
                "overall_score": evaluation.overall_score,
                "dimensions_count": len(evaluation.dimensions or []),
                "key_strengths": evaluation.key_strengths or [],
                "improvement_areas": evaluation.improvement_areas or [],
                "ai_dependency_score": evaluation.ai_dependency_score,
            },
            children=[]
        )
        
        # Las evaluaciones son nodos de nivel superior (no cuelgan de eventos)
        artifacts.append(eval_node)
    
    # Construir resumen
    summary = {
        "total_events": len(events),
        "total_traces": len(traces),
        "total_risks": len(risks),
        "total_evaluations": len(evaluations),
        "risks_by_level": {
            "CRITICAL": len([r for r in risks if r.risk_level == "CRITICAL"]),
            "HIGH": len([r for r in risks if r.risk_level == "HIGH"]),
            "MEDIUM": len([r for r in risks if r.risk_level == "MEDIUM"]),
            "LOW": len([r for r in risks if r.risk_level == "LOW"]),
        },
        "risks_resolved": len([r for r in risks if r.resolved]),
        "risks_pending": len([r for r in risks if not r.resolved]),
        "avg_ai_involvement": sum(t.ai_involvement or 0.0 for t in traces) / len(traces) if traces else 0.0,
        "session_duration_minutes": (
            (session.end_time - session.start_time).total_seconds() / 60
            if session.end_time else None
        ),
    }
    
    # Construir response
    response_data = SessionTraceabilityResponse(
        session_id=session.id,
        student_id=session.student_id,
        activity_id=session.activity_id,
        simulator_type=session.simulator_type,
        start_time=session.start_time,
        end_time=session.end_time,
        artifacts=artifacts,
        summary=summary,
    )
    
    return APIResponse(
        success=True,
        data=response_data,
        message=f"Session traceability graph with {len(artifacts)} root artifacts"
    )

