"""
Schemas Pydantic para modelos Sprint 5-6

SPRINT 5:
- CourseReportDB - Reportes Institucionales (HU-DOC-009)
- RemediationPlanDB - Planes de Remediación (HU-DOC-010)
- RiskAlertDB - Alertas de Riesgo Institucionales (HU-DOC-010)
- TraceSequenceDB - Secuencias de Trazas N4
- StudentProfileDB - Perfiles de Estudiantes

SPRINT 6:
- InterviewSessionDB - Entrevistas Técnicas (HU-EST-011)
- IncidentSimulationDB - Simulación de Incidentes (HU-EST-012)
- LTIDeploymentDB/LTISessionDB - Integración LTI 1.3 (HU-SYS-010)
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================


class InterviewType(str, Enum):
    """Tipos de entrevista técnica"""
    CONCEPTUAL = "CONCEPTUAL"
    ALGORITHMIC = "ALGORITHMIC"
    DESIGN = "DESIGN"
    BEHAVIORAL = "BEHAVIORAL"


class DifficultyLevel(str, Enum):
    """Nivel de dificultad"""
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class IncidentType(str, Enum):
    """Tipos de incidente"""
    API_ERROR = "API_ERROR"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    DATABASE = "DATABASE"
    DEPLOYMENT = "DEPLOYMENT"


class IncidentSeverity(str, Enum):
    """Severidad del incidente"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(str, Enum):
    """Tipos de alerta institucional"""
    CRITICAL_RISK_SURGE = "critical_risk_surge"
    AI_DEPENDENCY_SPIKE = "ai_dependency_spike"
    ACADEMIC_INTEGRITY = "academic_integrity"
    PATTERN_ANOMALY = "pattern_anomaly"


class AlertSeverity(str, Enum):
    """Severidad de alerta"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertScope(str, Enum):
    """Alcance de la alerta"""
    STUDENT = "student"
    ACTIVITY = "activity"
    COURSE = "course"
    INSTITUTION = "institution"


class AlertStatus(str, Enum):
    """Estado de la alerta"""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class PlanType(str, Enum):
    """Tipo de plan de remediación"""
    TUTORING = "tutoring"
    PRACTICE_EXERCISES = "practice_exercises"
    CONCEPTUAL_REVIEW = "conceptual_review"
    POLICY_CLARIFICATION = "policy_clarification"


class PlanStatus(str, Enum):
    """Estado del plan de remediación"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ReportType(str, Enum):
    """Tipo de reporte institucional"""
    COHORT_SUMMARY = "cohort_summary"
    RISK_DASHBOARD = "risk_dashboard"
    COMPETENCY_DISTRIBUTION = "competency_distribution"


# =============================================================================
# INTERVIEW SESSION SCHEMAS (HU-EST-011)
# =============================================================================


class InterviewQuestion(BaseModel):
    """Pregunta de entrevista técnica"""
    question: str = Field(..., description="Texto de la pregunta")
    type: str = Field(..., description="Tipo: conceptual, algorithmic, design")
    expected_key_points: List[str] = Field(
        default_factory=list,
        description="Puntos clave esperados en la respuesta"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la pregunta"
    )


class ResponseEvaluation(BaseModel):
    """Evaluación de una respuesta"""
    clarity_score: float = Field(ge=0.0, le=1.0, description="Claridad (0-1)")
    technical_accuracy: float = Field(ge=0.0, le=1.0, description="Precisión técnica (0-1)")
    thinking_aloud: bool = Field(default=False, description="Si el estudiante pensó en voz alta")
    key_points_covered: List[str] = Field(
        default_factory=list,
        description="Puntos clave cubiertos"
    )


class InterviewResponse(BaseModel):
    """Respuesta a una pregunta de entrevista"""
    question_id: int = Field(..., description="Índice de la pregunta")
    response: str = Field(..., description="Respuesta del estudiante")
    evaluation: ResponseEvaluation = Field(..., description="Evaluación de la respuesta")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la respuesta"
    )


class EvaluationBreakdown(BaseModel):
    """Desglose de evaluación de entrevista"""
    clarity: float = Field(ge=0.0, le=1.0, description="Claridad general")
    technical_accuracy: float = Field(ge=0.0, le=1.0, description="Precisión técnica")
    communication: float = Field(ge=0.0, le=1.0, description="Habilidades de comunicación")
    problem_solving: float = Field(ge=0.0, le=1.0, description="Resolución de problemas")


class InterviewSessionCreate(BaseModel):
    """Request para crear una sesión de entrevista"""
    session_id: str = Field(..., description="ID de la sesión de aprendizaje")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: Optional[str] = Field(None, description="ID de la actividad")
    interview_type: InterviewType = Field(..., description="Tipo de entrevista")
    difficulty_level: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIUM,
        description="Nivel de dificultad"
    )


class InterviewSessionResponse(BaseModel):
    """Response con información de sesión de entrevista"""
    id: str = Field(..., description="ID de la sesión de entrevista")
    session_id: str = Field(..., description="ID de la sesión de aprendizaje")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: Optional[str] = Field(None, description="ID de la actividad")
    interview_type: str = Field(..., description="Tipo de entrevista")
    difficulty_level: str = Field(..., description="Nivel de dificultad")
    questions_asked: List[InterviewQuestion] = Field(
        default_factory=list,
        description="Preguntas realizadas"
    )
    responses: List[InterviewResponse] = Field(
        default_factory=list,
        description="Respuestas del estudiante"
    )
    evaluation_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Score final")
    evaluation_breakdown: Optional[EvaluationBreakdown] = Field(None, description="Desglose")
    feedback: Optional[str] = Field(None, description="Feedback detallado")
    duration_minutes: Optional[int] = Field(None, description="Duración en minutos")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True


# =============================================================================
# INCIDENT SIMULATION SCHEMAS (HU-EST-012)
# =============================================================================


class DiagnosisStep(BaseModel):
    """Paso en el proceso de diagnóstico"""
    step: int = Field(..., description="Número de paso")
    action: str = Field(..., description="Acción realizada")
    finding: str = Field(..., description="Hallazgo")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp del paso"
    )


class IncidentEvaluation(BaseModel):
    """Evaluación de respuesta a incidente"""
    diagnosis_systematic: float = Field(
        ge=0.0, le=1.0,
        description="¿Siguió un enfoque sistemático?"
    )
    prioritization: float = Field(
        ge=0.0, le=1.0,
        description="¿Priorizó correctamente?"
    )
    documentation: float = Field(
        ge=0.0, le=1.0,
        description="Calidad del post-mortem"
    )
    communication: float = Field(
        ge=0.0, le=1.0,
        description="Comunicación del incidente"
    )


class IncidentSimulationCreate(BaseModel):
    """Request para crear simulación de incidente"""
    session_id: str = Field(..., description="ID de la sesión de aprendizaje")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: Optional[str] = Field(None, description="ID de la actividad")
    incident_type: IncidentType = Field(..., description="Tipo de incidente")
    severity: IncidentSeverity = Field(
        default=IncidentSeverity.HIGH,
        description="Severidad del incidente"
    )
    incident_description: str = Field(..., description="Descripción del incidente")


class IncidentSimulationResponse(BaseModel):
    """Response con información de simulación de incidente"""
    id: str = Field(..., description="ID de la simulación")
    session_id: str = Field(..., description="ID de la sesión de aprendizaje")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: Optional[str] = Field(None, description="ID de la actividad")
    incident_type: str = Field(..., description="Tipo de incidente")
    severity: str = Field(..., description="Severidad")
    incident_description: str = Field(..., description="Descripción")
    simulated_logs: Optional[str] = Field(None, description="Logs simulados")
    simulated_metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Métricas simuladas"
    )
    diagnosis_process: List[DiagnosisStep] = Field(
        default_factory=list,
        description="Proceso de diagnóstico"
    )
    solution_proposed: Optional[str] = Field(None, description="Solución propuesta")
    root_cause_identified: Optional[str] = Field(None, description="Causa raíz")
    time_to_diagnose_minutes: Optional[int] = Field(None, description="Tiempo de diagnóstico")
    time_to_resolve_minutes: Optional[int] = Field(None, description="Tiempo de resolución")
    post_mortem: Optional[str] = Field(None, description="Documentación post-mortem")
    evaluation: Optional[IncidentEvaluation] = Field(None, description="Evaluación")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True


# =============================================================================
# LTI INTEGRATION SCHEMAS (HU-SYS-010)
# =============================================================================


class LTIDeploymentCreate(BaseModel):
    """Request para registrar un deployment LTI"""
    platform_name: str = Field(..., max_length=100, description="Nombre de la plataforma")
    issuer: str = Field(..., description="LTI issuer URL")
    client_id: str = Field(..., description="OAuth2 client ID")
    deployment_id: str = Field(..., description="LTI deployment ID")
    auth_login_url: str = Field(..., description="OIDC auth login URL")
    auth_token_url: str = Field(..., description="OAuth2 token URL")
    public_keyset_url: str = Field(..., description="JWKS URL")
    access_token_url: Optional[str] = Field(None, description="Access token URL para AGS")


class LTIDeploymentResponse(BaseModel):
    """Response con información de deployment LTI"""
    id: str = Field(..., description="ID del deployment")
    platform_name: str = Field(..., description="Nombre de la plataforma")
    issuer: str = Field(..., description="LTI issuer URL")
    client_id: str = Field(..., description="OAuth2 client ID")
    deployment_id: str = Field(..., description="LTI deployment ID")
    auth_login_url: str = Field(..., description="OIDC auth login URL")
    auth_token_url: str = Field(..., description="OAuth2 token URL")
    public_keyset_url: str = Field(..., description="JWKS URL")
    access_token_url: Optional[str] = Field(None, description="Access token URL")
    is_active: bool = Field(..., description="Si está activo")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True


class LTISessionCreate(BaseModel):
    """Request para crear sesión LTI"""
    deployment_id: str = Field(..., description="ID del deployment LTI")
    lti_user_id: str = Field(..., description="User ID de Moodle")
    lti_user_name: Optional[str] = Field(None, description="Nombre del usuario")
    lti_user_email: Optional[str] = Field(None, description="Email del usuario")
    lti_context_id: Optional[str] = Field(None, description="Course ID de Moodle")
    lti_context_label: Optional[str] = Field(None, description="Código del curso")
    lti_context_title: Optional[str] = Field(None, description="Nombre del curso")
    resource_link_id: str = Field(..., description="ID del recurso LTI")
    session_id: Optional[str] = Field(None, description="ID de sesión AI-Native mapeada")
    launch_token: Optional[str] = Field(None, description="JWT token del launch")
    locale: Optional[str] = Field(None, description="Locale del usuario")


class LTISessionResponse(BaseModel):
    """Response con información de sesión LTI"""
    id: str = Field(..., description="ID de la sesión LTI")
    deployment_id: str = Field(..., description="ID del deployment")
    lti_user_id: str = Field(..., description="User ID de Moodle")
    lti_user_name: Optional[str] = Field(None, description="Nombre del usuario")
    lti_user_email: Optional[str] = Field(None, description="Email del usuario")
    lti_context_id: Optional[str] = Field(None, description="Course ID")
    lti_context_label: Optional[str] = Field(None, description="Código del curso")
    lti_context_title: Optional[str] = Field(None, description="Nombre del curso")
    resource_link_id: str = Field(..., description="ID del recurso")
    session_id: Optional[str] = Field(None, description="ID de sesión AI-Native")
    locale: Optional[str] = Field(None, description="Locale")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True


# =============================================================================
# COURSE REPORT SCHEMAS (HU-DOC-009)
# =============================================================================


class SummaryStats(BaseModel):
    """Estadísticas resumidas del curso"""
    total_students: int = Field(0, description="Total de estudiantes")
    total_sessions: int = Field(0, description="Total de sesiones")
    total_interactions: int = Field(0, description="Total de interacciones")
    avg_ai_dependency: float = Field(0.0, description="Dependencia promedio de IA")


class StudentSummary(BaseModel):
    """Resumen de un estudiante en el reporte"""
    student_id: str = Field(..., description="ID del estudiante")
    sessions: int = Field(0, description="Número de sesiones")
    ai_dependency: float = Field(0.0, description="Dependencia de IA")
    competency: Optional[str] = Field(None, description="Nivel de competencia")
    risks: int = Field(0, description="Riesgos detectados")


class CourseReportCreate(BaseModel):
    """Request para crear reporte de curso"""
    course_id: str = Field(..., description="ID del curso")
    teacher_id: str = Field(..., description="ID del docente")
    report_type: ReportType = Field(..., description="Tipo de reporte")
    period_start: datetime = Field(..., description="Inicio del período")
    period_end: datetime = Field(..., description="Fin del período")


class CourseReportResponse(BaseModel):
    """Response con información del reporte de curso"""
    id: str = Field(..., description="ID del reporte")
    course_id: str = Field(..., description="ID del curso")
    teacher_id: str = Field(..., description="ID del docente")
    report_type: str = Field(..., description="Tipo de reporte")
    period_start: datetime = Field(..., description="Inicio del período")
    period_end: datetime = Field(..., description="Fin del período")
    summary_stats: SummaryStats = Field(..., description="Estadísticas resumidas")
    competency_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribución de competencias"
    )
    risk_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribución de riesgos"
    )
    top_risks: List[str] = Field(default_factory=list, description="Top riesgos")
    student_summaries: List[StudentSummary] = Field(
        default_factory=list,
        description="Resúmenes por estudiante"
    )
    institutional_recommendations: List[str] = Field(
        default_factory=list,
        description="Recomendaciones institucionales"
    )
    at_risk_students: List[str] = Field(
        default_factory=list,
        description="Estudiantes en riesgo"
    )
    format: str = Field("json", description="Formato de exportación")
    file_path: Optional[str] = Field(None, description="Ruta del archivo exportado")
    exported_at: Optional[datetime] = Field(None, description="Fecha de exportación")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True


# =============================================================================
# REMEDIATION PLAN SCHEMAS (HU-DOC-010)
# =============================================================================


class RecommendedAction(BaseModel):
    """Acción recomendada en un plan de remediación"""
    action_type: str = Field(..., description="Tipo de acción")
    description: str = Field(..., description="Descripción de la acción")
    deadline: Optional[str] = Field(None, description="Fecha límite (YYYY-MM-DD)")
    status: str = Field("pending", description="Estado: pending, in_progress, completed")


class SuccessMetrics(BaseModel):
    """Métricas de éxito del plan"""
    ai_dependency_before: Optional[float] = Field(None, description="Dependencia IA antes")
    ai_dependency_after: Optional[float] = Field(None, description="Dependencia IA después")
    risks_resolved: int = Field(0, description="Riesgos resueltos")


class RemediationPlanCreate(BaseModel):
    """Request para crear plan de remediación"""
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: Optional[str] = Field(None, description="ID de la actividad")
    teacher_id: str = Field(..., description="ID del docente")
    trigger_risks: List[str] = Field(
        default_factory=list,
        description="IDs de riesgos que motivaron el plan"
    )
    plan_type: PlanType = Field(..., description="Tipo de plan")
    description: str = Field(..., description="Descripción del plan")
    objectives: List[str] = Field(default_factory=list, description="Objetivos")
    recommended_actions: List[RecommendedAction] = Field(
        default_factory=list,
        description="Acciones recomendadas"
    )
    start_date: datetime = Field(..., description="Fecha de inicio")
    target_completion_date: datetime = Field(..., description="Fecha objetivo de finalización")


class RemediationPlanUpdate(BaseModel):
    """Request para actualizar plan de remediación"""
    status: Optional[PlanStatus] = Field(None, description="Nuevo estado")
    progress_notes: Optional[str] = Field(None, description="Notas de progreso")
    completion_evidence: Optional[List[str]] = Field(None, description="Evidencia de completación")
    outcome_evaluation: Optional[str] = Field(None, description="Evaluación de resultados")
    success_metrics: Optional[SuccessMetrics] = Field(None, description="Métricas de éxito")
    actual_completion_date: Optional[datetime] = Field(None, description="Fecha real de completación")


class RemediationPlanResponse(BaseModel):
    """Response con información de plan de remediación"""
    id: str = Field(..., description="ID del plan")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: Optional[str] = Field(None, description="ID de la actividad")
    teacher_id: str = Field(..., description="ID del docente")
    trigger_risks: List[str] = Field(default_factory=list, description="Riesgos trigger")
    plan_type: str = Field(..., description="Tipo de plan")
    description: str = Field(..., description="Descripción")
    objectives: List[str] = Field(default_factory=list, description="Objetivos")
    recommended_actions: List[RecommendedAction] = Field(
        default_factory=list,
        description="Acciones"
    )
    start_date: datetime = Field(..., description="Fecha de inicio")
    target_completion_date: datetime = Field(..., description="Fecha objetivo")
    actual_completion_date: Optional[datetime] = Field(None, description="Fecha real")
    status: str = Field(..., description="Estado")
    progress_notes: Optional[str] = Field(None, description="Notas de progreso")
    completion_evidence: List[str] = Field(default_factory=list, description="Evidencia")
    outcome_evaluation: Optional[str] = Field(None, description="Evaluación")
    success_metrics: Optional[SuccessMetrics] = Field(None, description="Métricas")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True


# =============================================================================
# RISK ALERT SCHEMAS (HU-DOC-010)
# =============================================================================


class RiskAlertCreate(BaseModel):
    """Request para crear alerta de riesgo (generalmente automático)"""
    alert_type: AlertType = Field(..., description="Tipo de alerta")
    severity: AlertSeverity = Field(..., description="Severidad")
    scope: AlertScope = Field(..., description="Alcance")
    student_id: Optional[str] = Field(None, description="ID del estudiante")
    activity_id: Optional[str] = Field(None, description="ID de la actividad")
    course_id: Optional[str] = Field(None, description="ID del curso")
    title: str = Field(..., max_length=255, description="Título de la alerta")
    description: str = Field(..., description="Descripción detallada")
    evidence: List[str] = Field(default_factory=list, description="Evidencia")
    detection_rule: str = Field(..., description="Regla que detectó la alerta")
    threshold_value: Optional[float] = Field(None, description="Valor umbral")
    actual_value: Optional[float] = Field(None, description="Valor real")


class RiskAlertUpdate(BaseModel):
    """Request para actualizar alerta de riesgo"""
    status: Optional[AlertStatus] = Field(None, description="Nuevo estado")
    assigned_to: Optional[str] = Field(None, description="Asignar a usuario")
    resolution_notes: Optional[str] = Field(None, description="Notas de resolución")
    remediation_plan_id: Optional[str] = Field(None, description="Plan de remediación asociado")


class RiskAlertResponse(BaseModel):
    """Response con información de alerta de riesgo"""
    id: str = Field(..., description="ID de la alerta")
    alert_type: str = Field(..., description="Tipo de alerta")
    severity: str = Field(..., description="Severidad")
    scope: str = Field(..., description="Alcance")
    student_id: Optional[str] = Field(None, description="ID del estudiante")
    activity_id: Optional[str] = Field(None, description="ID de la actividad")
    course_id: Optional[str] = Field(None, description="ID del curso")
    title: str = Field(..., description="Título")
    description: str = Field(..., description="Descripción")
    evidence: List[str] = Field(default_factory=list, description="Evidencia")
    detected_at: datetime = Field(..., description="Fecha de detección")
    detection_rule: str = Field(..., description="Regla de detección")
    threshold_value: Optional[float] = Field(None, description="Valor umbral")
    actual_value: Optional[float] = Field(None, description="Valor real")
    assigned_to: Optional[str] = Field(None, description="Asignado a")
    assigned_at: Optional[datetime] = Field(None, description="Fecha de asignación")
    status: str = Field(..., description="Estado")
    acknowledged_at: Optional[datetime] = Field(None, description="Fecha de reconocimiento")
    acknowledged_by: Optional[str] = Field(None, description="Reconocido por")
    resolution_notes: Optional[str] = Field(None, description="Notas de resolución")
    resolved_at: Optional[datetime] = Field(None, description="Fecha de resolución")
    remediation_plan_id: Optional[str] = Field(None, description="Plan de remediación")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True


# =============================================================================
# TRACE SEQUENCE SCHEMAS
# =============================================================================


class TraceSequenceCreate(BaseModel):
    """Request para crear secuencia de trazas"""
    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    trace_ids: List[str] = Field(default_factory=list, description="IDs de trazas")


class TraceSequenceResponse(BaseModel):
    """Response con información de secuencia de trazas"""
    id: str = Field(..., description="ID de la secuencia")
    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    start_time: datetime = Field(..., description="Tiempo de inicio")
    end_time: Optional[datetime] = Field(None, description="Tiempo de fin")
    reasoning_path: List[str] = Field(default_factory=list, description="Camino de razonamiento")
    strategy_changes: int = Field(0, description="Cambios de estrategia")
    ai_dependency_score: float = Field(0.0, description="Score de dependencia IA")
    trace_ids: List[str] = Field(default_factory=list, description="IDs de trazas")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True


# =============================================================================
# STUDENT PROFILE SCHEMAS
# =============================================================================


class StudentProfileCreate(BaseModel):
    """Request para crear perfil de estudiante"""
    student_id: str = Field(..., description="ID del estudiante")
    name: Optional[str] = Field(None, max_length=200, description="Nombre")
    email: Optional[str] = Field(None, max_length=200, description="Email")


class StudentProfileUpdate(BaseModel):
    """Request para actualizar perfil de estudiante"""
    name: Optional[str] = Field(None, max_length=200, description="Nombre")
    email: Optional[str] = Field(None, max_length=200, description="Email")
    total_sessions: Optional[int] = Field(None, description="Total de sesiones")
    total_interactions: Optional[int] = Field(None, description="Total de interacciones")
    average_ai_dependency: Optional[float] = Field(None, description="Dependencia promedio")
    average_competency_level: Optional[str] = Field(None, description="Nivel promedio")
    total_risks: Optional[int] = Field(None, description="Total de riesgos")
    critical_risks: Optional[int] = Field(None, description="Riesgos críticos")


class StudentProfileResponse(BaseModel):
    """Response con información de perfil de estudiante"""
    id: str = Field(..., description="ID del perfil")
    student_id: str = Field(..., description="ID del estudiante")
    name: Optional[str] = Field(None, description="Nombre")
    email: Optional[str] = Field(None, description="Email")
    total_sessions: int = Field(0, description="Total de sesiones")
    total_interactions: int = Field(0, description="Total de interacciones")
    average_ai_dependency: float = Field(0.0, description="Dependencia promedio de IA")
    average_competency_level: Optional[str] = Field(None, description="Nivel de competencia promedio")
    total_risks: int = Field(0, description="Total de riesgos")
    critical_risks: int = Field(0, description="Riesgos críticos")
    risk_trends: Dict[str, Any] = Field(default_factory=dict, description="Tendencias de riesgo")
    competency_evolution: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Evolución de competencia"
    )
    last_activity_date: Optional[datetime] = Field(None, description="Última actividad")
    created_at: datetime = Field(..., description="Fecha de creación")
    updated_at: datetime = Field(..., description="Fecha de actualización")

    class Config:
        from_attributes = True