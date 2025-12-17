"""
Ejemplo de integración del patrón Background Session en AIGateway

Demuestra cómo refactorizar código existente para usar sesiones de BD
independientes en BackgroundTasks, evitando ResourceClosedError.

ANTES (PROBLEMA - ResourceClosedError):
    
    @router.post("/chat")
    async def chat(
        request: ChatRequest,
        db: Session = Depends(get_db),  # Sesión del request
        background_tasks: BackgroundTasks
    ):
        # ... procesamiento síncrono ...
        
        # ❌ PROBLEMA: pasar 'db' a background task
        background_tasks.add_task(
            analyze_risks_background,
            session_id=session_id,
            db=db  # ❌ Esta sesión se cierra cuando se envía el response
        )
        
        return {"response": response}
    
    def analyze_risks_background(session_id: str, db: Session):
        # ❌ db ya está cerrada -> ResourceClosedError
        risks = db.query(RiskDB).filter_by(session_id=session_id).all()


DESPUÉS (SOLUCIÓN - Background Session Pattern):

    @router.post("/chat")
    async def chat(
        request: ChatRequest,
        db: Session = Depends(get_db),
        background_tasks: BackgroundTasks
    ):
        # ... procesamiento síncrono ...
        
        # ✅ NO pasar la sesión del request
        background_tasks.add_task(
            analyze_risks_background,
            session_id=session_id
            # NO pasar 'db'
        )
        
        return {"response": response}
    
    @with_background_db_session  # ✅ Decorador inyecta sesión fresca
    def analyze_risks_background(session_id: str, db: Session):
        # ✅ db es una sesión nueva e independiente
        risks = db.query(RiskDB).filter_by(session_id=session_id).all()
        # ... procesamiento ...
        # Commit automático al terminar
"""
from typing import Dict, Any, List, Optional
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

# Importar la utilidad de background sessions
from backend.database import (
    get_background_db_session,
    with_background_db_session,
    BackgroundUnitOfWork,
)

from backend.database.models import CognitiveTraceDB, RiskDB, SessionDB
from backend.database.repositories import RiskRepository, TraceRepository
from backend.models.risk import Risk, RiskType, RiskLevel, RiskDimension


# ============================================================================
# PATRÓN 1: Context Manager (Más flexible)
# ============================================================================

def analyze_risks_background_v1(session_id: str, student_id: str):
    """
    Versión usando context manager - más control manual
    
    Úsala cuando necesitas control fino sobre transacciones
    o quieres hacer múltiples commits dentro de la función.
    """
    with get_background_db_session() as db:
        # Obtener datos
        traces = db.query(CognitiveTraceDB).filter_by(
            session_id=session_id
        ).all()
        
        # Análisis de riesgos
        risks = []
        for trace in traces:
            if _detect_cognitive_risk(trace):
                risk = RiskDB(
                    session_id=session_id,
                    student_id=student_id,
                    risk_type=RiskType.COGNITIVE_DELEGATION.value,
                    risk_level=RiskLevel.HIGH.value,
                    dimension=RiskDimension.COGNITIVE.value,
                    description="Delegación cognitiva detectada",
                    evidence=[trace.content],
                    trace_ids=[trace.id]
                )
                risks.append(risk)
        
        # Persistir
        db.bulk_save_objects(risks)
        # Commit automático al salir del 'with'


# ============================================================================
# PATRÓN 2: Decorador (Más limpio)
# ============================================================================

@with_background_db_session
def analyze_risks_background_v2(session_id: str, student_id: str, db: Session):
    """
    Versión usando decorador - código más limpio
    
    La sesión 'db' se inyecta automáticamente por el decorador.
    Úsala cuando quieres código más limpio y no necesitas control fino.
    """
    # La sesión 'db' ya está inyectada
    traces = db.query(CognitiveTraceDB).filter_by(
        session_id=session_id
    ).all()
    
    risks = []
    for trace in traces:
        if _detect_cognitive_risk(trace):
            risk = RiskDB(
                session_id=session_id,
                student_id=student_id,
                risk_type=RiskType.COGNITIVE_DELEGATION.value,
                risk_level=RiskLevel.HIGH.value,
                dimension=RiskDimension.COGNITIVE.value,
                description="Delegación cognitiva detectada",
                evidence=[trace.content],
                trace_ids=[trace.id]
            )
            risks.append(risk)
    
    db.bulk_save_objects(risks)
    # Commit automático al terminar la función


# ============================================================================
# PATRÓN 3: Unit of Work (Complejo - múltiples repositorios)
# ============================================================================

def analyze_risks_background_v3(session_id: str):
    """
    Versión usando Unit of Work - para operaciones complejas
    
    Úsala cuando necesitas acceder a múltiples repositorios
    y quieres transaccionalidad atómica.
    """
    uow = BackgroundUnitOfWork()
    with uow:
        # Acceder a múltiples repositorios con la misma sesión
        session_data = uow.sessions.get(session_id)
        traces = uow.traces.get_by_session(session_id)
        existing_risks = uow.risks.get_by_session(session_id)
        
        # Análisis complejo usando múltiples fuentes de datos
        new_risks = []
        for trace in traces:
            if _detect_cognitive_risk(trace):
                risk = Risk(
                    session_id=session_id,
                    student_id=session_data.student_id,
                    risk_type=RiskType.COGNITIVE_DELEGATION,
                    risk_level=RiskLevel.HIGH,
                    dimension=RiskDimension.COGNITIVE,
                    description="Delegación cognitiva detectada",
                    evidence=[trace.content],
                    trace_ids=[trace.id]
                )
                new_risks.append(risk)
        
        # Crear riesgos usando el repository
        for risk in new_risks:
            uow.risks.create(risk)
        
        # Commit atómico de todas las operaciones
        uow.commit()


# ============================================================================
# INTEGRACIÓN EN AIGateway
# ============================================================================

class AIGatewayRefactored:
    """
    Ejemplo de cómo integrar el patrón en AIGateway
    """
    
    async def process_interaction(
        self,
        session_id: str,
        prompt: str,
        background_tasks: BackgroundTasks,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Proceso principal que responde al usuario y delega análisis pesados
        a background tasks
        """
        # 1. Procesamiento síncrono (responde rápido al usuario)
        response = await self._generate_response(session_id, prompt, context)
        
        # 2. Delegar análisis de riesgos a background (NO pasar db session)
        background_tasks.add_task(
            analyze_risks_background_v2,  # Usa decorador
            session_id=session_id,
            student_id=context.get("student_id")
            # NO pasar 'db' aquí
        )
        
        # 3. Retornar respuesta inmediata
        return {
            "response": response,
            "status": "processing",
            "metadata": {
                "session_id": session_id,
                "risk_analysis": "in_progress"
            }
        }
    
    async def _generate_response(
        self,
        session_id: str,
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generar respuesta del LLM (síncrono)"""
        # ... lógica existente ...
        return "Response from LLM"


# ============================================================================
# Helpers
# ============================================================================

def _detect_cognitive_risk(trace: CognitiveTraceDB) -> bool:
    """Detectar si una traza indica riesgo cognitivo"""
    # Lógica de detección
    delegation_keywords = [
        "dame la respuesta",
        "resuelve esto por mi",
        "cual es la solucion"
    ]
    return any(keyword in trace.content.lower() for keyword in delegation_keywords)


# ============================================================================
# USO EN ENDPOINT FASTAPI
# ============================================================================

"""
# En backend/api/routes/chat.py

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from backend.database import get_db

router = APIRouter()

@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # 1. Procesar chat síncrono (usa 'db' del request)
    session = db.query(SessionDB).filter_by(id=request.session_id).first()
    response = await ai_gateway.process_interaction(
        session_id=request.session_id,
        prompt=request.prompt,
        background_tasks=background_tasks,
        context={"student_id": session.student_id}
    )
    
    # 2. Background tasks YA están programadas dentro de process_interaction
    # (con sus propias sesiones independientes)
    
    return response
"""
