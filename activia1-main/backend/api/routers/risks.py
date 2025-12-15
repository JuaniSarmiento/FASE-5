"""
Router para gestión de riesgos y evaluaciones
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.orm import Session

from ...database.repositories import (
    RiskRepository,
    EvaluationRepository,
    SessionRepository,
)
from ...database.models import SimulatorEventDB, SessionDB, RiskDB
from ...models.risk import Risk, RiskLevel, RiskDimension, RiskType
from ...models.evaluation import EvaluationReport
from ..deps import (
    get_risk_repository,
    get_evaluation_repository,
    get_session_repository,
    get_db,
    get_current_user,  # FIX Cortez20: Add for auth
)
from ..schemas.common import APIResponse, PaginatedResponse, PaginationMeta, validate_uuid_format
from ..exceptions import SessionNotFoundError, InvalidInteractionError

router = APIRouter(prefix="/risks", tags=["Risks & Evaluation"])


# Schemas para risks
class RiskResponse(BaseModel):
    """
    Response con información de un riesgo.

    FIX 10.3 Cortez10: Added missing fields from RiskDB ORM model.
    """

    id: str
    session_id: str  # REQUIRED - Un riesgo siempre tiene sesión asociada
    student_id: str
    activity_id: str
    risk_type: str
    risk_level: str
    dimension: str
    description: str
    # FIX 10.3 Cortez10: Added missing ORM fields
    impact: Optional[str] = None
    root_cause: Optional[str] = None
    impact_assessment: Optional[str] = None
    evidence: List[str]
    trace_ids: List[str]
    recommendations: List[str]
    pedagogical_intervention: Optional[str] = None
    resolved: bool
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    detected_by: str = "AR-IA"
    created_at: datetime

    class Config:
        from_attributes = True


class RiskStatistics(BaseModel):
    """Estadísticas de riesgos"""

    total_risks: int
    by_level: dict
    by_dimension: dict
    by_type: dict
    resolution_rate: float  # Porcentaje de riesgos resueltos


# Schemas para evaluaciones
class DimensionEvaluation(BaseModel):
    """
    Evaluación de una dimensión específica

    FIX 10.15 Cortez10: Refactored to use proper Pydantic Field alias instead of __init__ override.
    Both 'dimension' and 'name' are accepted, with 'dimension' as the primary field.
    """
    # FIX 10.15 Cortez10: Use Field with alias for proper Pydantic v2 compatibility
    dimension: str = Field(..., alias="name")  # Primary field, accepts both 'dimension' and 'name'
    score: float
    level: str  # 'novice', 'advanced_beginner', 'competent', 'proficient', 'expert'
    evidence: List[str] = []
    feedback: str = ""
    # FIX: Campos adicionales para compatibilidad con frontend EvaluationDimension
    description: Optional[str] = None
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendations: List[str] = []

    class Config:
        # FIX 10.15 Cortez10: Allow using both 'dimension' and 'name'
        populate_by_name = True


class ReasoningAnalysisResponse(BaseModel):
    """
    Análisis del razonamiento del estudiante

    FIX DISC #2: Añadidos campos de compatibilidad con frontend ReasoningAnalysis
    """
    # Campos backend originales
    phases_identified: List[str] = []
    phase_transitions: List[str] = []
    reasoning_quality: str = ""
    conceptual_errors: List[dict] = []
    metacognitive_evidence: List[str] = []
    problem_solving_strategy: str = ""
    completeness_score: float = 0.0
    # FIX: Campos adicionales para compatibilidad con frontend
    cognitive_path: List[str] = []  # Alias para phases_identified
    phases_completed: List[str] = []  # Alias para phases_identified
    strategy_changes: int = 0
    self_corrections: int = 0
    ai_critiques: int = 0
    coherence_score: float = 0.0  # Alias para reasoning_quality (normalizado a 0-1)
    logical_fallacies: List[str] = []
    planning_quality: float = 0.0
    monitoring_evidence: List[str] = []  # Alias para metacognitive_evidence
    self_explanation_quality: float = 0.0


class GitAnalysisResponse(BaseModel):
    """
    Análisis de código Git

    FIX DISC #3: Añadidos campos de compatibilidad con frontend GitAnalysis
    """
    # Campos backend originales
    commits_analyzed: int = 0
    code_evolution_quality: str = ""
    consistency_score: float = 0.0
    patterns_detected: List[str] = []
    ai_generated_code_percentage: float = 0.0
    copy_paste_detected: bool = False
    # FIX: Campos adicionales para compatibilidad con frontend
    total_commits: int = 0  # Alias para commits_analyzed
    commit_messages_quality: float = 0.0
    suspicious_jumps: List[str] = []  # Alias para patterns_detected
    evolution_coherence: float = 0.0  # Alias para consistency_score
    traces_linked: int = 0


class EvaluationResponse(BaseModel):
    """
    Response con información de una evaluación.

    FIX 10.6 Cortez10: Added separate recommendations_student and recommendations_teacher
    to match ORM structure {"student": [], "teacher": []}.
    FIX 10.9 Cortez10: Added validation for ai_dependency_score (0-1 range).
    """

    id: str
    session_id: str
    student_id: str
    activity_id: str
    overall_competency_level: str
    overall_score: float
    dimensions: List[DimensionEvaluation] = []  # List of dimension evaluations
    key_strengths: List[str] = []
    improvement_areas: List[str] = []
    # FIX 10.6 Cortez10: Split recommendations to match ORM structure
    recommendations_student: List[str] = []
    recommendations_teacher: List[str] = []
    reasoning_analysis: Optional[ReasoningAnalysisResponse] = None  # JSON object, not string
    git_analysis: Optional[GitAnalysisResponse] = None  # JSON object, not string
    # FIX 10.9 Cortez10: Added validation to match ORM constraint
    ai_dependency_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Score de dependencia de IA (0-1)")
    ai_dependency_metrics: dict = {}  # Métricas detalladas de dependencia de IA
    created_at: datetime

    class Config:
        from_attributes = True


@router.get(
    "/session/{session_id}",
    response_model=APIResponse[List[RiskResponse]],
    summary="Get Session Risks",
    description="Obtiene todos los riesgos detectados en una sesión",
)
async def get_session_risks(
    session_id: str,
    resolved: Optional[bool] = Query(None, description="Filtrar por estado de resolución"),
    dimension: Optional[str] = Query(None, description="Filtrar por dimensión de riesgo"),
    session_repo: SessionRepository = Depends(get_session_repository),
    risk_repo: RiskRepository = Depends(get_risk_repository),
    _current_user: dict = Depends(get_current_user),  # FIX Cortez20: Add auth
) -> APIResponse[List[RiskResponse]]:
    """
    Obtiene riesgos de una sesión con filtros opcionales.

    Args:
        session_id: ID de la sesión
        resolved: Filtrar por riesgos resueltos/no resueltos
        dimension: Filtrar por dimensión (COGNITIVE, ETHICAL, etc.)
        session_repo: Repositorio de sesiones (inyectado)
        risk_repo: Repositorio de riesgos (inyectado)

    Returns:
        APIResponse con lista de riesgos

    Raises:
        SessionNotFoundError: Si la sesión no existe
    """
    # Verificar que la sesión existe
    db_session = session_repo.get_by_id(session_id)
    if not db_session:
        raise SessionNotFoundError(session_id)

    # Obtener riesgos
    risks = risk_repo.get_by_session(session_id)

    # Aplicar filtros
    if resolved is not None:
        risks = [r for r in risks if r.resolved == resolved]

    if dimension:
        risks = [r for r in risks if r.dimension == dimension]

    # Convertir a schemas de respuesta
    # FIX 10.3 Cortez10: Include all ORM fields in response
    risks_data = [
        RiskResponse(
            id=r.id,
            session_id=r.session_id,
            student_id=r.student_id,
            activity_id=r.activity_id,
            risk_type=r.risk_type,
            risk_level=r.risk_level,
            dimension=r.dimension,
            description=r.description,
            impact=r.impact,
            root_cause=r.root_cause,
            impact_assessment=r.impact_assessment,
            evidence=r.evidence or [],
            trace_ids=r.trace_ids or [],
            recommendations=r.recommendations or [],
            pedagogical_intervention=r.pedagogical_intervention,
            resolved=r.resolved,
            resolution_notes=r.resolution_notes,
            resolved_at=getattr(r, 'resolved_at', None),
            detected_by=getattr(r, 'detected_by', 'AR-IA'),
            created_at=r.created_at,
        )
        for r in risks
    ]

    return APIResponse(
        success=True,
        data=risks_data,
        message=f"Retrieved {len(risks_data)} risks for session {session_id}",
    )


@router.get(
    "/student/{student_id}",
    response_model=APIResponse[List[RiskResponse]],
    summary="Get Student Risks",
    description="Obtiene todos los riesgos de un estudiante a través de todas sus sesiones",
)
async def get_student_risks(
    student_id: str,
    resolved: Optional[bool] = Query(None),
    dimension: Optional[str] = Query(None),
    risk_repo: RiskRepository = Depends(get_risk_repository),
    _current_user: dict = Depends(get_current_user),  # FIX Cortez20: Add auth
) -> APIResponse[List[RiskResponse]]:
    """
    Obtiene riesgos de un estudiante.

    Útil para análisis de perfil de riesgo del estudiante.

    Args:
        student_id: ID del estudiante
        resolved: Filtrar por estado de resolución
        dimension: Filtrar por dimensión
        risk_repo: Repositorio de riesgos (inyectado)

    Returns:
        APIResponse con lista de riesgos del estudiante
    """
    # Obtener riesgos del estudiante
    risks = risk_repo.get_by_student(student_id)

    # Aplicar filtros
    if resolved is not None:
        risks = [r for r in risks if r.resolved == resolved]

    if dimension:
        risks = [r for r in risks if r.dimension == dimension]

    # Convertir a schemas de respuesta
    # FIX 10.3 Cortez10: Include all ORM fields in response
    risks_data = [
        RiskResponse(
            id=r.id,
            session_id=r.session_id,
            student_id=r.student_id,
            activity_id=r.activity_id,
            risk_type=r.risk_type,
            risk_level=r.risk_level,
            dimension=r.dimension,
            description=r.description,
            impact=r.impact,
            root_cause=r.root_cause,
            impact_assessment=r.impact_assessment,
            evidence=r.evidence or [],
            trace_ids=r.trace_ids or [],
            recommendations=r.recommendations or [],
            pedagogical_intervention=r.pedagogical_intervention,
            resolved=r.resolved,
            resolution_notes=r.resolution_notes,
            resolved_at=getattr(r, 'resolved_at', None),
            detected_by=getattr(r, 'detected_by', 'AR-IA'),
            created_at=r.created_at,
        )
        for r in risks
    ]

    return APIResponse(
        success=True,
        data=risks_data,
        message=f"Retrieved {len(risks_data)} risks for student {student_id}",
    )


@router.get(
    "/student/{student_id}/statistics",
    response_model=APIResponse[RiskStatistics],
    summary="Get Student Risk Statistics",
    description="Obtiene estadísticas de riesgos de un estudiante",
)
async def get_student_risk_statistics(
    student_id: str,
    risk_repo: RiskRepository = Depends(get_risk_repository),
) -> APIResponse[RiskStatistics]:
    """
    Calcula estadísticas de riesgos del estudiante.

    Args:
        student_id: ID del estudiante
        risk_repo: Repositorio de riesgos (inyectado)

    Returns:
        APIResponse con estadísticas de riesgos
    """
    # Obtener todos los riesgos del estudiante
    all_risks = risk_repo.get_by_student(student_id)

    # Calcular estadísticas por nivel
    by_level = {}
    for risk in all_risks:
        level = risk.risk_level
        by_level[level] = by_level.get(level, 0) + 1

    # Calcular estadísticas por dimensión
    by_dimension = {}
    for risk in all_risks:
        dim = risk.dimension
        by_dimension[dim] = by_dimension.get(dim, 0) + 1

    # Calcular estadísticas por tipo
    by_type = {}
    for risk in all_risks:
        rtype = risk.risk_type
        by_type[rtype] = by_type.get(rtype, 0) + 1

    # Calcular tasa de resolución
    resolved_count = sum(1 for r in all_risks if r.resolved)
    resolution_rate = (resolved_count / len(all_risks) * 100) if all_risks else 0

    # Construir estadísticas
    statistics = RiskStatistics(
        total_risks=len(all_risks),
        by_level=by_level,
        by_dimension=by_dimension,
        by_type=by_type,
        resolution_rate=round(resolution_rate, 2),
    )

    return APIResponse(
        success=True,
        data=statistics,
        message=f"Calculated risk statistics for student {student_id}",
    )


@router.get(
    "/critical",
    response_model=APIResponse[List[RiskResponse]],
    summary="Get Critical Risks",
    description="Obtiene todos los riesgos críticos no resueltos del sistema",
)
async def get_critical_risks(
    student_id: Optional[str] = Query(None, description="Filtrar por estudiante"),
    risk_repo: RiskRepository = Depends(get_risk_repository),
) -> APIResponse[List[RiskResponse]]:
    """
    Obtiene riesgos críticos no resueltos.

    Útil para dashboard de instructores y gobernanza.

    Args:
        student_id: Filtro opcional por estudiante
        risk_repo: Repositorio de riesgos (inyectado)

    Returns:
        APIResponse con lista de riesgos críticos
    """
    # Obtener riesgos críticos (DB stores lowercase)
    if student_id:
        all_risks = risk_repo.get_by_student(student_id)
        critical_risks = [
            r for r in all_risks
            if r.risk_level == "critical" and not r.resolved
        ]
    else:
        critical_risks = risk_repo.get_critical_risks()

    # Convertir a schemas de respuesta
    # FIX 10.3 Cortez10: Include all ORM fields in response
    risks_data = [
        RiskResponse(
            id=r.id,
            session_id=r.session_id,
            student_id=r.student_id,
            activity_id=r.activity_id,
            risk_type=r.risk_type,
            risk_level=r.risk_level,
            dimension=r.dimension,
            description=r.description,
            impact=r.impact,
            root_cause=r.root_cause,
            impact_assessment=r.impact_assessment,
            evidence=r.evidence or [],
            trace_ids=r.trace_ids or [],
            recommendations=r.recommendations or [],
            pedagogical_intervention=r.pedagogical_intervention,
            resolved=r.resolved,
            resolution_notes=r.resolution_notes,
            resolved_at=getattr(r, 'resolved_at', None),
            detected_by=getattr(r, 'detected_by', 'AR-IA'),
            created_at=r.created_at,
        )
        for r in critical_risks
    ]

    return APIResponse(
        success=True,
        data=risks_data,
        message=f"Retrieved {len(risks_data)} critical risks",
    )


# =============================================================================
# Endpoints de Evaluaciones
# =============================================================================


@router.get(
    "/evaluation/session/{session_id}",
    response_model=APIResponse[EvaluationResponse],
    summary="Get Session Evaluation",
    description="Obtiene el reporte de evaluación de una sesión",
)
async def get_session_evaluation(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
    eval_repo: EvaluationRepository = Depends(get_evaluation_repository),
    _current_user: dict = Depends(get_current_user),  # FIX Cortez20: Add auth
) -> APIResponse[EvaluationResponse]:
    """
    Obtiene la evaluación de proceso de una sesión.

    La evaluación es generada por E-IA-Proc al finalizar la sesión.

    Args:
        session_id: ID de la sesión
        session_repo: Repositorio de sesiones (inyectado)
        eval_repo: Repositorio de evaluaciones (inyectado)

    Returns:
        APIResponse con el reporte de evaluación

    Raises:
        SessionNotFoundError: Si la sesión no existe
        HTTPException(404): Si no hay evaluación para la sesión
    """
    # Verificar que la sesión existe
    db_session = session_repo.get_by_id(session_id)
    if not db_session:
        raise SessionNotFoundError(session_id)

    # Obtener evaluación
    evaluations = eval_repo.get_by_session(session_id)

    if not evaluations:
        raise HTTPException(
            status_code=404,
            detail=f"No evaluation found for session {session_id}. Session may not be completed yet.",
        )

    # Tomar la evaluación más reciente
    latest_eval = evaluations[-1]

    # Convertir dimensions de JSON a lista de DimensionEvaluation
    dimensions_list = []
    if latest_eval.dimensions:
        for dim in latest_eval.dimensions:
            if isinstance(dim, dict):
                dimensions_list.append(DimensionEvaluation(**dim))

    # Convertir reasoning_analysis de JSON a ReasoningAnalysisResponse
    reasoning = None
    if latest_eval.reasoning_analysis and isinstance(latest_eval.reasoning_analysis, dict):
        reasoning = ReasoningAnalysisResponse(**latest_eval.reasoning_analysis)

    # Convertir git_analysis de JSON a GitAnalysisResponse
    git_analysis = None
    if latest_eval.git_analysis and isinstance(latest_eval.git_analysis, dict):
        git_analysis = GitAnalysisResponse(**latest_eval.git_analysis)

    # FIX 10.6 Cortez10: Extract recommendations from JSON structure
    recommendations = latest_eval.recommendations or {}
    recommendations_student = recommendations.get("student", []) if isinstance(recommendations, dict) else []
    recommendations_teacher = recommendations.get("teacher", []) if isinstance(recommendations, dict) else []

    # Convertir a schema de respuesta
    eval_data = EvaluationResponse(
        id=latest_eval.id,
        session_id=latest_eval.session_id,
        student_id=latest_eval.student_id,
        activity_id=latest_eval.activity_id,
        overall_competency_level=latest_eval.overall_competency_level,
        overall_score=latest_eval.overall_score,
        dimensions=dimensions_list,
        key_strengths=latest_eval.key_strengths or [],
        improvement_areas=latest_eval.improvement_areas or [],
        recommendations_student=recommendations_student,
        recommendations_teacher=recommendations_teacher,
        reasoning_analysis=reasoning,
        git_analysis=git_analysis,
        ai_dependency_score=latest_eval.ai_dependency_score or 0.0,
        ai_dependency_metrics=latest_eval.ai_dependency_metrics or {},
        created_at=latest_eval.created_at,
    )

    return APIResponse(
        success=True,
        data=eval_data,
        message=f"Retrieved evaluation for session {session_id}",
    )


@router.get(
    "/evaluation/student/{student_id}",
    response_model=APIResponse[List[EvaluationResponse]],
    summary="Get Student Evaluations",
    description="Obtiene todas las evaluaciones de un estudiante",
)
async def get_student_evaluations(
    student_id: str,
    eval_repo: EvaluationRepository = Depends(get_evaluation_repository),
) -> APIResponse[List[EvaluationResponse]]:
    """
    Obtiene todas las evaluaciones de un estudiante.

    Útil para análisis de progreso y evolución del estudiante.

    Args:
        student_id: ID del estudiante
        eval_repo: Repositorio de evaluaciones (inyectado)

    Returns:
        APIResponse con lista de evaluaciones
    """
    # Obtener evaluaciones del estudiante
    evaluations = eval_repo.get_by_student(student_id)

    # Convertir a schemas de respuesta
    evals_data = []
    for e in evaluations:
        # Convertir dimensions
        dimensions_list = []
        if e.dimensions:
            for dim in e.dimensions:
                if isinstance(dim, dict):
                    dimensions_list.append(DimensionEvaluation(**dim))

        # Convertir reasoning_analysis
        reasoning = None
        if e.reasoning_analysis and isinstance(e.reasoning_analysis, dict):
            reasoning = ReasoningAnalysisResponse(**e.reasoning_analysis)

        # Convertir git_analysis
        git_analysis = None
        if e.git_analysis and isinstance(e.git_analysis, dict):
            git_analysis = GitAnalysisResponse(**e.git_analysis)

        # FIX 10.6 Cortez10: Extract recommendations from JSON structure
        recommendations = e.recommendations or {}
        recs_student = recommendations.get("student", []) if isinstance(recommendations, dict) else []
        recs_teacher = recommendations.get("teacher", []) if isinstance(recommendations, dict) else []

        evals_data.append(EvaluationResponse(
            id=e.id,
            session_id=e.session_id,
            student_id=e.student_id,
            activity_id=e.activity_id,
            overall_competency_level=e.overall_competency_level,
            overall_score=e.overall_score,
            dimensions=dimensions_list,
            key_strengths=e.key_strengths or [],
            improvement_areas=e.improvement_areas or [],
            recommendations_student=recs_student,
            recommendations_teacher=recs_teacher,
            reasoning_analysis=reasoning,
            git_analysis=git_analysis,
            ai_dependency_score=e.ai_dependency_score or 0.0,
            ai_dependency_metrics=e.ai_dependency_metrics or {},
            created_at=e.created_at,
        ))

    return APIResponse(
        success=True,
        data=evals_data,
        message=f"Retrieved {len(evals_data)} evaluations for student {student_id}",
    )


# ============================================================================
# AUTOMATIC RISK ANALYSIS ENGINE (AR-IA)
# ============================================================================

@router.post(
    "/analyze-session/{session_id}",
    response_model=APIResponse[List[RiskResponse]],
    summary="Analyze Session for Risks",
    description="Analiza eventos de una sesión y detecta riesgos automáticamente"
)
async def analyze_session_risks(
    session_id: str,
    session_repo: SessionRepository = Depends(get_session_repository),
    risk_repo: RiskRepository = Depends(get_risk_repository),
    db: Session = Depends(get_db),  # FIX: Sólo para SimulatorEventDB query (pendiente crear repo)
) -> APIResponse[List[RiskResponse]]:
    """
    Engine de Análisis de Riesgos (AR-IA)

    Analiza los eventos de una sesión y detecta riesgos automáticamente basándose en:
    - Eventos del simulador
    - Patrones de comportamiento
    - Decisiones tomadas
    - Omisiones críticas

    Reglas de detección:
    1. backlog_created sin acceptance_criteria → RIESGO TÉCNICO (ALTA probabilidad, MEDIO impacto)
    2. sprint_planning_failed → RIESGO DE GOBERNANZA (MEDIA probabilidad, ALTO impacto)
    3. technical_decision sin justification → RIESGO DE CALIDAD (ALTA probabilidad, MEDIO impacto)
    4. security_scan con vulnerabilities → RIESGO DE SEGURIDAD (ALTA probabilidad, CRÍTICO impacto)
    5. deployment sin tests → RIESGO OPERACIONAL (ALTA probabilidad, ALTO impacto)
    """
    # FIX EP-5: Validar formato UUID de session_id antes de acceder a BD
    try:
        session_id = validate_uuid_format(session_id, "session_id")
    except ValueError as e:
        raise InvalidInteractionError(
            str(e),
            {"session_id": session_id, "error": "invalid_uuid_format"}
        )

    # Verificar sesión
    session = session_repo.get_by_id(session_id)
    if not session:
        raise SessionNotFoundError(session_id)
    
    # Obtener todos los eventos de la sesión
    events = db.query(SimulatorEventDB).filter(
        SimulatorEventDB.session_id == session_id
    ).order_by(SimulatorEventDB.timestamp).all()
    
    if not events:
        return APIResponse(
            success=True,
            data=[],
            message=f"No events found for session {session_id}, no risks to analyze"
        )
    
    detected_risks = []
    
    # REGLA 1: Backlog sin criterios de aceptación
    for event in events:
        if event.event_type == "backlog_created":
            event_data = event.event_data or {}
            if not event_data.get("has_acceptance_criteria", False):
                # FIX: Usar modelo Risk (Pydantic) + risk_repo.create()
                risk = Risk(
                    id=f"risk_{session_id[:8]}_{len(detected_risks)}",
                    session_id=session_id,
                    student_id=session.student_id,
                    activity_id=session.activity_id,
                    risk_type=RiskType.POOR_CODE_QUALITY,  # Mapeo: TECHNICAL_DEBT → POOR_CODE_QUALITY
                    risk_level=RiskLevel.HIGH,
                    dimension=RiskDimension.TECHNICAL,
                    description="User stories sin criterios de aceptación claros",
                    impact="Riesgo de implementación incorrecta, retrabajo y bugs en producción",
                    evidence=[
                        f"Backlog creado con {event_data.get('stories_count', 0)} historias",
                        "No se definieron criterios de aceptación",
                        f"Evento detectado: {event.timestamp.isoformat()}"
                    ],
                    trace_ids=[],
                    recommendations=[
                        "Definir criterios de aceptación SMART para cada user story",
                        "Incluir ejemplos concretos de comportamiento esperado",
                        "Revisar criterios con el equipo antes de comenzar desarrollo"
                    ],
                    detected_by="AR-IA-AUTO",
                    resolved=False,
                )
                db_risk = risk_repo.create(risk)
                detected_risks.append(db_risk)
    
    # REGLA 2: Sprint planning fallido
    for event in events:
        if event.event_type == "sprint_planning_failed":
            event_data = event.event_data or {}
            # FIX: Usar modelo Risk (Pydantic) + risk_repo.create()
            risk = Risk(
                id=f"risk_{session_id[:8]}_{len(detected_risks)}",
                session_id=session_id,
                student_id=session.student_id,
                activity_id=session.activity_id,
                risk_type=RiskType.POLICY_VIOLATION,  # Mapeo: PROCESS → POLICY_VIOLATION
                risk_level=RiskLevel.HIGH,
                dimension=RiskDimension.GOVERNANCE,
                description="Sprint planning incompleto o fallido",
                impact="Riesgo de retrasos, scope creep y falta de alineación del equipo",
                evidence=[
                    f"Planning falló: {event_data.get('reason', 'No especificado')}",
                    f"Evento detectado: {event.timestamp.isoformat()}"
                ],
                trace_ids=[],
                recommendations=[
                    "Revisar capacidad del equipo y velocity histórico",
                    "Asegurar presencia de todo el equipo en planning",
                    "Definir Definition of Done clara antes de comenzar"
                ],
                detected_by="AR-IA-AUTO",
                resolved=False,
            )
            db_risk = risk_repo.create(risk)
            detected_risks.append(db_risk)
    
    # REGLA 3: Decisión técnica sin justificación
    for event in events:
        if event.event_type == "technical_decision_made":
            event_data = event.event_data or {}
            if not event_data.get("justification"):
                # FIX: Usar modelo Risk (Pydantic) + risk_repo.create()
                risk = Risk(
                    id=f"risk_{session_id[:8]}_{len(detected_risks)}",
                    session_id=session_id,
                    student_id=session.student_id,
                    activity_id=session.activity_id,
                    risk_type=RiskType.LACK_JUSTIFICATION,  # Mapeo exacto disponible
                    risk_level=RiskLevel.MEDIUM,
                    dimension=RiskDimension.TECHNICAL,
                    description="Decisión técnica sin justificación documentada",
                    impact="Dificultad para mantener y evolucionar el sistema",
                    evidence=[
                        f"Decisión: {event_data.get('decision', 'No especificada')}",
                        "No hay justificación documentada",
                        f"Evento detectado: {event.timestamp.isoformat()}"
                    ],
                    trace_ids=[],
                    recommendations=[
                        "Documentar el razonamiento detrás de decisiones arquitecturales",
                        "Explicar alternativas consideradas y por qué se descartaron",
                        "Incluir trade-offs y limitaciones conocidas"
                    ],
                    detected_by="AR-IA-AUTO",
                    resolved=False,
                )
                db_risk = risk_repo.create(risk)
                detected_risks.append(db_risk)
    
    # REGLA 4: Security scan con vulnerabilidades
    for event in events:
        if event.event_type == "security_scan_complete":
            event_data = event.event_data or {}
            vulnerabilities = event_data.get("vulnerabilities", [])
            if vulnerabilities:
                severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
                for vuln in vulnerabilities:
                    sev = vuln.get("severity", "low").lower()
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1

                risk_level = RiskLevel.CRITICAL if severity_counts["critical"] > 0 else RiskLevel.HIGH

                # FIX: Usar modelo Risk (Pydantic) + risk_repo.create()
                risk = Risk(
                    id=f"risk_{session_id[:8]}_{len(detected_risks)}",
                    session_id=session_id,
                    student_id=session.student_id,
                    activity_id=session.activity_id,
                    risk_type=RiskType.SECURITY_VULNERABILITY,  # Mapeo exacto disponible
                    risk_level=risk_level,
                    dimension=RiskDimension.TECHNICAL,
                    description=f"Vulnerabilidades de seguridad detectadas: {len(vulnerabilities)} total",
                    impact="Riesgo de brechas de seguridad, exposición de datos y ataques",
                    evidence=[
                        f"Critical: {severity_counts['critical']}, High: {severity_counts['high']}, Medium: {severity_counts['medium']}, Low: {severity_counts['low']}",
                        f"Scan realizado: {event.timestamp.isoformat()}",
                        f"Herramienta: {event_data.get('tool', 'Unknown')}"
                    ],
                    trace_ids=[],
                    recommendations=[
                        "Priorizar corrección de vulnerabilidades críticas y altas",
                        "Implementar security hardening según OWASP",
                        "Configurar análisis de seguridad en CI/CD pipeline"
                    ],
                    detected_by="AR-IA-AUTO",
                    resolved=False,
                )
                db_risk = risk_repo.create(risk)
                detected_risks.append(db_risk)
    
    # REGLA 5: Deployment sin tests
    for event in events:
        if event.event_type == "deployment_completed":
            event_data = event.event_data or {}
            if not event_data.get("tests_executed", False):
                # FIX: Usar modelo Risk (Pydantic) + risk_repo.create()
                risk = Risk(
                    id=f"risk_{session_id[:8]}_{len(detected_risks)}",
                    session_id=session_id,
                    student_id=session.student_id,
                    activity_id=session.activity_id,
                    risk_type=RiskType.ARCHITECTURAL_FLAW,  # Mapeo: OPERATIONAL → ARCHITECTURAL_FLAW
                    risk_level=RiskLevel.HIGH,
                    dimension=RiskDimension.TECHNICAL,
                    description="Deployment a producción sin ejecutar tests",
                    impact="Alto riesgo de bugs en producción y downtime",
                    evidence=[
                        f"Deployment realizado: {event_data.get('environment', 'production')}",
                        "No se ejecutaron tests previos al deployment",
                        f"Evento detectado: {event.timestamp.isoformat()}"
                    ],
                    trace_ids=[],
                    recommendations=[
                        "Implementar test suite automatizado (unit, integration, e2e)",
                        "Configurar CI/CD para ejecutar tests antes de deployment",
                        "Establecer política de 0% deployments sin tests"
                    ],
                    detected_by="AR-IA-AUTO",
                    resolved=False,
                )
                db_risk = risk_repo.create(risk)
                detected_risks.append(db_risk)

    # FIX: Eliminado db.commit() - risk_repo.create() ya hace commit internamente
    
    # FIX: risk_repo.create() ya retorna objetos RiskDB refresheados, no necesita db.refresh()
    # FIX 10.3 Cortez10: Include all ORM fields in response
    response_data = []
    for db_risk in detected_risks:
        response_data.append(
            RiskResponse(
                id=db_risk.id,
                session_id=db_risk.session_id,
                student_id=db_risk.student_id,
                activity_id=db_risk.activity_id,
                risk_type=db_risk.risk_type,
                risk_level=db_risk.risk_level,
                dimension=db_risk.dimension,
                description=db_risk.description,
                impact=db_risk.impact,
                root_cause=db_risk.root_cause,
                impact_assessment=db_risk.impact_assessment,
                evidence=db_risk.evidence or [],
                trace_ids=db_risk.trace_ids or [],
                recommendations=db_risk.recommendations or [],
                pedagogical_intervention=db_risk.pedagogical_intervention,
                resolved=db_risk.resolved,
                resolution_notes=db_risk.resolution_notes,
                resolved_at=getattr(db_risk, 'resolved_at', None),
                detected_by=getattr(db_risk, 'detected_by', 'AR-IA'),
                created_at=db_risk.created_at,
            )
        )
    
    return APIResponse(
        success=True,
        data=response_data,
        message=f"Analyzed {len(events)} events, detected {len(detected_risks)} risks"
    )
