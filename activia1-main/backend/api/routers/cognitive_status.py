"""
Router para Estado Cognitivo en Tiempo Real

Endpoints para la Barra de Estado Cognitivo (Frontend)
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from ...database import SessionRepository, TraceRepository, RiskRepository
from ...core.cognitive_engine import CognitiveState
from ..deps import get_db

router = APIRouter(tags=["cognitive-status"])


@router.get("/sessions/{session_id}/cognitive-status")
async def get_cognitive_status(
    session_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Obtiene el estado cognitivo actual de una sesión
    
    Retorna:
    - autonomyLevel: Nivel de autonomía (0.0-1.0)
    - riskLevel: Nivel de riesgo (low/medium/high/critical)
    - currentPhase: Fase cognitiva actual
    - cognitiveLoad: Carga cognitiva estimada
    - aiDependency: Dependencia de IA (0.0-1.0)
    - engagementScore: Score de engagement (0.0-1.0)
    """
    # Obtener sesión
    session_repo = SessionRepository(db)
    session = session_repo.get_by_id(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    # Obtener trazas recientes
    trace_repo = TraceRepository(db)
    all_traces = trace_repo.get_by_session(session_id)
    # Ordenar por timestamp descendente y tomar las últimas 20
    traces = sorted(all_traces, key=lambda t: t.timestamp, reverse=True)[:20]
    
    # Obtener riesgos
    risk_repo = RiskRepository(db)
    risks = risk_repo.get_by_session(session_id)
    
    # Calcular autonomía (inverso de dependencia de IA)
    if traces:
        ai_involvement_avg = sum(t.ai_involvement for t in traces) / len(traces)
        autonomy_level = 1.0 - ai_involvement_avg
    else:
        autonomy_level = 0.5
    
    # Determinar nivel de riesgo
    unresolved_risks = [r for r in risks if not r.resolved]
    critical_risks = [r for r in unresolved_risks if r.risk_level == "critical"]
    high_risks = [r for r in unresolved_risks if r.risk_level == "high"]
    
    if critical_risks:
        risk_level = "critical"
    elif high_risks:
        risk_level = "high"
    elif len(unresolved_risks) > 3:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    # Determinar fase actual (de las trazas más recientes)
    current_phase = "exploration"
    if traces:
        latest_trace = traces[0]
        if latest_trace.cognitive_state:
            # Mapear estados a fases
            state_to_phase = {
                "exploracion": "exploration",
                "planificacion": "planning",
                "implementacion": "implementation",
                "depuracion": "debugging",
                "validacion": "validation",
                "reflexion": "reflection"
            }
            current_phase = state_to_phase.get(
                latest_trace.cognitive_state.lower(), 
                "exploration"
            )
    
    # Estimar carga cognitiva
    # Basado en: complejidad de prompts, frecuencia de cambios de estado, errores
    cognitive_load = "medium"
    if traces:
        # Si hay muchos cambios de estado rápidos = alta carga
        state_changes = len(set(t.cognitive_state for t in traces[-10:] if t.cognitive_state))
        if state_changes > 5:
            cognitive_load = "high"
        elif state_changes < 2:
            cognitive_load = "low"
        
        # Si hay muchos errores/debugging = sobrecarga
        debug_traces = [t for t in traces[-10:] if t.cognitive_state == "depuracion"]
        if len(debug_traces) > 6:
            cognitive_load = "overload"
    
    # Calcular engagement (basado en frecuencia y calidad de interacciones)
    engagement_score = 0.5
    if traces:
        # Más trazas = más engagement
        engagement_score = min(1.0, len(traces) / 50.0)
        
        # Ajustar por calidad (trazas con justificaciones = mayor engagement)
        traces_with_justification = [
            t for t in traces 
            if t.decision_justification and len(t.decision_justification) > 20
        ]
        if traces:
            justification_ratio = len(traces_with_justification) / len(traces)
            engagement_score = (engagement_score + justification_ratio) / 2
    
    return {
        "autonomyLevel": round(autonomy_level, 2),
        "riskLevel": risk_level,
        "currentPhase": current_phase,
        "cognitiveLoad": cognitive_load,
        "aiDependency": round(1.0 - autonomy_level, 2),
        "engagementScore": round(engagement_score, 2),
        "lastUpdate": datetime.now().isoformat()
    }


@router.post("/sessions/{session_id}/update-cognitive-status")
async def update_cognitive_status(
    session_id: str,
    status: Dict[str, Any],
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Actualiza manualmente el estado cognitivo de una sesión
    (Útil para ajustes del docente)
    """
    session_repo = SessionRepository(db)
    session = session_repo.get_by_id(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    
    # Actualizar cognitive_status en SessionDB
    if not session.cognitive_status:
        session.cognitive_status = {}
    
    session.cognitive_status.update({
        "current_phase": status.get("currentPhase"),
        "autonomy_level": status.get("autonomyLevel"),
        "engagement_score": status.get("engagementScore"),
        "cognitive_load": status.get("cognitiveLoad"),
        "last_updated": datetime.now().isoformat()
    })
    
    db.commit()
    
    return {"status": "updated"}
