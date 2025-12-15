"""
Router para simuladores profesionales (S-IA-X)

Sprint 3 - HU-EST-009, HU-SYS-006
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..deps import get_db, get_session_repository, get_trace_repository, get_llm_provider, get_current_user
from ..schemas.common import APIResponse
from ..schemas.simulator import (
    SimulatorInteractionRequest,
    SimulatorInteractionResponse,
    SimulatorInfoResponse,
    SimulatorType
)
# Sprint 6 schemas
from ..schemas.simulators import (
    DailyStandupRequest,
    DailyStandupResponse,
    ClientRequirementRequest,
    ClientClarificationRequest,
    ClientResponse,
    SecurityAuditRequest,
    SecurityAuditResponse,
    SecurityVulnerability
)
from ...agents.simulators import SimuladorProfesionalAgent, SimuladorType as AgentSimulatorType
from ...database.repositories import SessionRepository, TraceRepository
from ...models.trace import CognitiveTrace, TraceLevel, InteractionType
from ...llm.base import LLMProvider
from ...llm.factory import LLMProviderFactory

router = APIRouter(prefix="/simulators", tags=["Simulators"])


@router.get(
    "",
    response_model=APIResponse[List[SimulatorInfoResponse]],
    summary="Listar simuladores disponibles",
    description="Obtiene la lista de todos los simuladores profesionales disponibles"
)
async def list_simulators(
    _current_user: dict = Depends(get_current_user),  # FIX Cortez22 DEFECTO 2.1: Require auth
) -> APIResponse[List[SimulatorInfoResponse]]:
    """
    Lista todos los simuladores profesionales disponibles en el sistema.

    **Simuladores implementados:**
    - PO-IA: Product Owner
    - SM-IA: Scrum Master
    - IT-IA: Technical Interviewer
    - IR-IA: Incident Responder
    - CX-IA: Client
    - DSO-IA: DevSecOps
    """
    simulators = [
        SimulatorInfoResponse(
            type=SimulatorType.PRODUCT_OWNER,
            name="Product Owner (PO-IA)",
            description="Simula un Product Owner que revisa requisitos, prioriza backlog y cuestiona decisiones técnicas",
            competencies=["comunicacion_tecnica", "analisis_requisitos", "priorizacion"],
            status="active"
        ),
        SimulatorInfoResponse(
            type=SimulatorType.SCRUM_MASTER,
            name="Scrum Master (SM-IA)",
            description="Simula un Scrum Master que facilita daily standups y gestiona impedimentos",
            competencies=["gestion_tiempo", "comunicacion", "identificacion_impedimentos"],
            status="active"
        ),
        SimulatorInfoResponse(
            type=SimulatorType.TECH_INTERVIEWER,
            name="Technical Interviewer (IT-IA)",
            description="Simula un entrevistador técnico que evalúa conocimientos conceptuales y algorítmicos",
            competencies=["dominio_conceptual", "analisis_algoritmico", "comunicacion_tecnica"],
            status="active"
        ),
        SimulatorInfoResponse(
            type=SimulatorType.INCIDENT_RESPONDER,
            name="Incident Responder (IR-IA)",
            description="Simula un ingeniero DevOps que gestiona incidentes en producción",
            competencies=["diagnostico_sistematico", "priorizacion", "documentacion"],
            status="development"
        ),
        SimulatorInfoResponse(
            type=SimulatorType.CLIENT,
            name="Client (CX-IA)",
            description="Simula un cliente con requisitos ambiguos que requiere elicitación y negociación",
            competencies=["elicitacion_requisitos", "negociacion", "empatia"],
            status="development"
        ),
        SimulatorInfoResponse(
            type=SimulatorType.DEVSECOPS,
            name="DevSecOps (DSO-IA)",
            description="Simula un analista de seguridad que audita código y detecta vulnerabilidades",
            competencies=["seguridad", "analisis_vulnerabilidades", "gestion_riesgo"],
            status="active"
        ),
    ]

    return APIResponse(
        success=True,
        data=simulators,
        message=f"Se encontraron {len(simulators)} simuladores"
    )


@router.post(
    "/interact",
    response_model=APIResponse[SimulatorInteractionResponse],
    summary="Interactuar con simulador",
    description="Procesa una interacción con un simulador profesional (HU-EST-009). SPRINT 4: Usa LLM real (Gemini/OpenAI) para respuestas dinámicas"
)
async def interact_with_simulator(
    request: SimulatorInteractionRequest,
    db: Session = Depends(get_db),
    session_repo: SessionRepository = Depends(get_session_repository),
    trace_repo: TraceRepository = Depends(get_trace_repository),
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> APIResponse[SimulatorInteractionResponse]:
    """
    Procesa una interacción entre el estudiante y un simulador profesional.

    **SPRINT 4**: Ahora usa LLM real (Gemini/OpenAI configurado en .env) para
    generar respuestas dinámicas y contextuales en lugar de respuestas predefinidas.

    **Flujo:**
    1. Valida que la sesión exista y esté activa
    2. Crea el simulador del tipo solicitado **con LLM provider inyectado**
    3. Procesa la entrada del estudiante (usa LLM si disponible, fallback a predefinidas)
    4. Analiza competencias transversales cuantitativamente
    5. Captura traza N4 de la interacción con métricas de competencias
    6. Retorna la respuesta del simulador con scores de competencias

    **HU-EST-009**: Permite al estudiante interactuar con Product Owner simulado
    para desarrollar habilidades de comunicación técnica.
    """
    # Validar sesión
    db_session = session_repo.get_by_id(request.session_id)
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{request.session_id}' not found"
        )

    if db_session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session '{request.session_id}' is not active (status: {db_session.status})"
        )

    # Mapear tipo de simulador
    simulator_type_map = {
        SimulatorType.PRODUCT_OWNER: AgentSimulatorType.PRODUCT_OWNER,
        SimulatorType.SCRUM_MASTER: AgentSimulatorType.SCRUM_MASTER,
        SimulatorType.TECH_INTERVIEWER: AgentSimulatorType.TECH_INTERVIEWER,
        SimulatorType.INCIDENT_RESPONDER: AgentSimulatorType.INCIDENT_RESPONDER,
        SimulatorType.CLIENT: AgentSimulatorType.CLIENT,
        SimulatorType.DEVSECOPS: AgentSimulatorType.DEVSECOPS,
    }

    agent_simulator_type = simulator_type_map[request.simulator_type]

    # Crear simulador (SPRINT 4: con LLM provider inyectado)
    # ✅ NUEVO: Ahora también inyectamos trace_repo para memoria de conversación
    simulator = SimuladorProfesionalAgent(
        simulator_type=agent_simulator_type,
        llm_provider=llm_provider,  # SPRINT 4: Usa Gemini/OpenAI configurado en .env
        trace_repo=trace_repo,  # ✅ Para cargar historial de conversación
        config={"context": request.context or {}}
    )

    # Procesar interacción
    # ✅ NUEVO: Ahora pasamos session_id para habilitar memoria de conversación
    response = await simulator.interact(
        student_input=request.prompt,
        context=request.context,
        session_id=request.session_id
    )

    # Capturar traza N4 de input
    input_trace = CognitiveTrace(
        session_id=request.session_id,
        student_id=db_session.student_id,
        activity_id=db_session.activity_id,
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.STUDENT_PROMPT,
        content=request.prompt,
        cognitive_state="exploracion",
        cognitive_intent=f"Interactuar con simulador {request.simulator_type.value}",
        ai_involvement=0.0,  # Es el estudiante quien habla
        metadata={
            "simulator_type": request.simulator_type.value,
            "context": request.context or {}
        }
    )

    # Capturar traza N4 de output
    output_trace = CognitiveTrace(
        session_id=request.session_id,
        student_id=db_session.student_id,
        activity_id=db_session.activity_id,
        trace_level=TraceLevel.N4_COGNITIVO,
        interaction_type=InteractionType.AI_RESPONSE,
        content=response["message"],
        cognitive_state="reflexion",
        cognitive_intent=f"Respuesta de simulador {request.simulator_type.value}",
        ai_involvement=1.0,  # Es el simulador quien responde
        metadata={
            "simulator_type": request.simulator_type.value,
            "role": response.get("role"),
            "expects": response.get("expects", []),
            "competencies_evaluated": response.get("metadata", {}).get("competencies_evaluated", [])
        }
    )

    # Persistir trazas
    db_input_trace = trace_repo.create(input_trace)
    db_output_trace = trace_repo.create(output_trace)

    # Preparar respuesta
    simulator_response = SimulatorInteractionResponse(
        interaction_id=f"{db_input_trace.id}_{db_output_trace.id}",
        simulator_type=request.simulator_type,
        response=response["message"],
        role=response.get("role", request.simulator_type.value),
        expects=response.get("expects", []),
        competencies_evaluated=response.get("metadata", {}).get("competencies_evaluated", []),
        trace_id_input=db_input_trace.id,
        trace_id_output=db_output_trace.id,
        metadata={
            "session_id": request.session_id,
            "simulator_context": request.context or {}
        }
    )

    return APIResponse(
        success=True,
        data=simulator_response,
        message=f"Interacción procesada con simulador {request.simulator_type.value}"
    )


@router.get(
    "/{simulator_type}",
    response_model=APIResponse[SimulatorInfoResponse],
    summary="Obtener información de simulador",
    description="Obtiene información detallada de un simulador específico"
)
async def get_simulator_info(
    simulator_type: SimulatorType
) -> APIResponse[SimulatorInfoResponse]:
    """
    Obtiene información detallada de un simulador profesional específico.
    """
    simulators_map = {
        SimulatorType.PRODUCT_OWNER: SimulatorInfoResponse(
            type=SimulatorType.PRODUCT_OWNER,
            name="Product Owner (PO-IA)",
            description="Simula un Product Owner que revisa requisitos, prioriza backlog y cuestiona decisiones técnicas. Evalúa la capacidad del estudiante para comunicar ideas técnicas en lenguaje de negocio y justificar decisiones arquitectónicas.",
            competencies=["comunicacion_tecnica", "analisis_requisitos", "priorizacion", "justificacion_decisiones"],
            status="active",
            example_questions=[
                "¿Cuáles son los criterios de aceptación?",
                "¿Cómo agrega valor al usuario final?",
                "¿Qué alternativas consideraste?",
                "¿Cuál es el impacto si lo postergamos?"
            ]
        ),
        SimulatorType.SCRUM_MASTER: SimulatorInfoResponse(
            type=SimulatorType.SCRUM_MASTER,
            name="Scrum Master (SM-IA)",
            description="Simula un Scrum Master que facilita daily standups, gestiona impedimentos y ayuda al equipo a mejorar procesos ágiles.",
            competencies=["gestion_tiempo", "comunicacion", "identificacion_impedimentos", "auto_organizacion"],
            status="active",
            example_questions=[
                "¿Qué lograste ayer?",
                "¿Qué vas a hacer hoy?",
                "¿Hay algún impedimento?",
                "¿Por qué llevás más tiempo del estimado?"
            ]
        ),
        SimulatorType.TECH_INTERVIEWER: SimulatorInfoResponse(
            type=SimulatorType.TECH_INTERVIEWER,
            name="Technical Interviewer (IT-IA)",
            description="Simula un entrevistador técnico que evalúa conocimientos conceptuales, algorítmicos y de diseño de sistemas.",
            competencies=["dominio_conceptual", "analisis_algoritmico", "comunicacion_tecnica", "razonamiento_en_voz_alta"],
            status="active",
            example_questions=[
                "Explicá la diferencia entre O(n) y O(log n)",
                "¿Cómo invertirías una lista enlazada?",
                "¿Cómo diseñarías un sistema de caché?"
            ]
        ),
        SimulatorType.INCIDENT_RESPONDER: SimulatorInfoResponse(
            type=SimulatorType.INCIDENT_RESPONDER,
            name="Incident Responder (IR-IA)",
            description="Simula un ingeniero DevOps que gestiona incidentes en producción bajo presión.",
            competencies=["diagnostico_sistematico", "priorizacion", "documentacion", "manejo_presion"],
            status="development"
        ),
        SimulatorType.CLIENT: SimulatorInfoResponse(
            type=SimulatorType.CLIENT,
            name="Client (CX-IA)",
            description="Simula un cliente con requisitos ambiguos que requiere elicitación, negociación y gestión de expectativas.",
            competencies=["elicitacion_requisitos", "negociacion", "empatia", "gestion_expectativas"],
            status="development"
        ),
        SimulatorType.DEVSECOPS: SimulatorInfoResponse(
            type=SimulatorType.DEVSECOPS,
            name="DevSecOps (DSO-IA)",
            description="Simula un analista de seguridad que audita código, detecta vulnerabilidades y exige planes de remediación.",
            competencies=["seguridad", "analisis_vulnerabilidades", "gestion_riesgo", "cumplimiento"],
            status="active",
            example_questions=[
                "¿Cómo vas a remediar esta SQL injection?",
                "¿Por qué hardcodeaste credenciales?",
                "¿Cuál es tu plan de actualización de dependencias?"
            ]
        ),
    }

    simulator_info = simulators_map.get(simulator_type)
    if not simulator_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulator '{simulator_type}' not found"
        )

    return APIResponse(
        success=True,
        data=simulator_info,
        message=f"Información de simulador {simulator_type.value}"
    )


# ============================================================================
# SPRINT 6: SPECIALIZED ENDPOINTS WITH DATABASE PERSISTENCE
# ============================================================================
# New specialized endpoints for IT-IA and IR-IA that use InterviewSessionDB
# and IncidentSimulationDB tables (Sprint 6 HU-EST-011, HU-EST-012)

from ..schemas.simulators import (
    # Interview Simulator (IT-IA)
    InterviewStartRequest,
    InterviewResponseRequest,
    InterviewCompleteRequest,
    InterviewResponse,
    # Incident Simulator (IR-IA)
    IncidentStartRequest,
    DiagnosisStepRequest,
    IncidentSolutionRequest,
    IncidentResponse,
)
from ...database.repositories import (
    InterviewSessionRepository,
    IncidentSimulationRepository,
)
import logging

logger_sprint6 = logging.getLogger(__name__)


# ============================================================================
# INTERVIEW SIMULATOR (IT-IA) - HU-EST-011 - SPRINT 6
# ============================================================================


@router.post(
    "/interview/start",
    response_model=APIResponse[InterviewResponse],
    summary="Start Technical Interview (Sprint 6)",
    description="Inicia una simulación de entrevista técnica con IT-IA (Technical Interviewer Agent)",
)
async def start_interview(
    request: InterviewStartRequest,
    db: Session = Depends(get_db),
) -> APIResponse[InterviewResponse]:
    """
    Inicia una sesión de entrevista técnica simulada (SPRINT 6).

    El agente IT-IA generará preguntas basadas en:
    - Tipo de entrevista (CONCEPTUAL, ALGORITHMIC, DESIGN, BEHAVIORAL)
    - Nivel de dificultad (EASY, MEDIUM, HARD)
    - Contexto de la sesión AI-Native

    Returns:
        InterviewResponse con la primera pregunta generada
    """
    try:
        # Validate session exists
        session_repo = SessionRepository(db)
        session_db = session_repo.get_by_id(request.session_id)
        if not session_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found",
            )

        # Create interview session
        interview_repo = InterviewSessionRepository(db)
        interview = interview_repo.create(
            session_id=request.session_id,
            student_id=request.student_id,
            interview_type=request.interview_type,
            activity_id=request.activity_id,
            difficulty_level=request.difficulty_level,
        )

        # Initialize simulator and generate first question
        llm_provider = LLMProviderFactory.create_from_env()
        simulator = SimuladorProfesionalAgent(llm_provider=llm_provider)

        first_question = await simulator.generar_pregunta_entrevista(
            tipo_entrevista=request.interview_type,
            dificultad=request.difficulty_level,
            contexto=f"Estudiante: {request.student_id}, Actividad: {request.activity_id}",
        )

        # Add first question to interview
        question_data = {
            "question": first_question,
            "type": request.interview_type,
            "timestamp": interview.created_at.isoformat(),
        }
        interview = interview_repo.add_question(interview.id, question_data)

        logger_sprint6.info(
            "Interview started",
            extra={
                "interview_id": interview.id,
                "student_id": request.student_id,
                "interview_type": request.interview_type,
            },
        )

        return APIResponse(
            success=True,
            data=InterviewResponse(
                interview_id=interview.id,
                session_id=interview.session_id,
                student_id=interview.student_id,
                interview_type=interview.interview_type,
                difficulty_level=interview.difficulty_level,
                questions_asked=interview.questions_asked,
                responses=interview.responses,
                created_at=interview.created_at,
                updated_at=interview.updated_at,
            ),
            message="Technical interview started successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error(
            "Error starting interview",
            exc_info=True,
            extra={"student_id": request.student_id},
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start interview: {str(e)}",
        )


@router.post(
    "/interview/respond",
    response_model=APIResponse[InterviewResponse],
    summary="Submit Interview Response (Sprint 6)",
    description="Envía la respuesta del estudiante a una pregunta de entrevista",
)
async def submit_interview_response(
    request: InterviewResponseRequest,
    db: Session = Depends(get_db),
) -> APIResponse[InterviewResponse]:
    """
    Procesa la respuesta del estudiante y genera la siguiente pregunta (SPRINT 6).

    El agente IT-IA evaluará:
    - Claridad de comunicación
    - Precisión técnica
    - Proceso de pensamiento (thinking aloud)
    - Puntos clave cubiertos
    """
    try:
        interview_repo = InterviewSessionRepository(db)
        interview = interview_repo.get_by_id(request.interview_id)

        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview '{request.interview_id}' not found",
            )

        # Evaluate response with IT-IA
        llm_provider = LLMProviderFactory.create_from_env()
        simulator = SimuladorProfesionalAgent(llm_provider=llm_provider)

        last_question = interview.questions_asked[-1] if interview.questions_asked else {}

        evaluation = await simulator.evaluar_respuesta_entrevista(
            pregunta=last_question.get("question", ""),
            respuesta=request.response,
            tipo_entrevista=interview.interview_type,
        )

        # Add response with evaluation
        response_data = {
            "response": request.response,
            "timestamp": interview.updated_at.isoformat(),
            "evaluation": evaluation,
        }
        interview = interview_repo.add_response(interview.id, response_data)

        # Generate next question if interview not complete
        if len(interview.questions_asked) < 5:  # Max 5 questions per interview
            next_question = await simulator.generar_pregunta_entrevista(
                tipo_entrevista=interview.interview_type,
                dificultad=interview.difficulty_level,
                contexto=f"Preguntas previas: {len(interview.questions_asked)}",
            )

            question_data = {
                "question": next_question,
                "type": interview.interview_type,
                "timestamp": interview.updated_at.isoformat(),
            }
            interview = interview_repo.add_question(interview.id, question_data)

        logger_sprint6.info(
            "Interview response processed",
            extra={"interview_id": interview.id, "question_count": len(interview.questions_asked)},
        )

        return APIResponse(
            success=True,
            data=InterviewResponse(
                interview_id=interview.id,
                session_id=interview.session_id,
                student_id=interview.student_id,
                interview_type=interview.interview_type,
                difficulty_level=interview.difficulty_level,
                questions_asked=interview.questions_asked,
                responses=interview.responses,
                created_at=interview.created_at,
                updated_at=interview.updated_at,
            ),
            message="Response evaluated successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error("Error processing interview response", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process response: {str(e)}",
        )


@router.post(
    "/interview/complete",
    response_model=APIResponse[InterviewResponse],
    summary="Complete Interview (Sprint 6)",
    description="Finaliza la entrevista y genera evaluación final",
)
async def complete_interview(
    request: InterviewCompleteRequest,
    db: Session = Depends(get_db),
) -> APIResponse[InterviewResponse]:
    """
    Completa la entrevista técnica y genera evaluación final (SPRINT 6).

    Calcula:
    - Score global (0.0 - 1.0)
    - Breakdown por dimensión (clarity, technical_accuracy, communication)
    - Feedback narrativo del evaluador
    """
    try:
        interview_repo = InterviewSessionRepository(db)
        interview = interview_repo.get_by_id(request.interview_id)

        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview '{request.interview_id}' not found",
            )

        # Generate final evaluation
        llm_provider = LLMProviderFactory.create_from_env()
        simulator = SimuladorProfesionalAgent(llm_provider=llm_provider)

        final_evaluation = await simulator.generar_evaluacion_entrevista(
            preguntas=interview.questions_asked,
            respuestas=interview.responses,
            tipo_entrevista=interview.interview_type,
        )

        # Calculate duration
        duration = int((interview.updated_at - interview.created_at).total_seconds() / 60)

        # Complete interview with evaluation
        interview = interview_repo.complete_interview(
            interview_id=interview.id,
            evaluation_score=final_evaluation.get("overall_score", 0.0),
            evaluation_breakdown=final_evaluation.get("breakdown", {}),
            feedback=final_evaluation.get("feedback", ""),
            duration_minutes=duration,
        )

        logger_sprint6.info(
            "Interview completed",
            extra={
                "interview_id": interview.id,
                "score": interview.evaluation_score,
                "duration_minutes": duration,
            },
        )

        return APIResponse(
            success=True,
            data=InterviewResponse(
                interview_id=interview.id,
                session_id=interview.session_id,
                student_id=interview.student_id,
                interview_type=interview.interview_type,
                difficulty_level=interview.difficulty_level,
                questions_asked=interview.questions_asked,
                responses=interview.responses,
                evaluation_score=interview.evaluation_score,
                evaluation_breakdown=interview.evaluation_breakdown,
                feedback=interview.feedback,
                duration_minutes=interview.duration_minutes,
                created_at=interview.created_at,
                updated_at=interview.updated_at,
            ),
            message="Interview completed successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error("Error completing interview", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to complete interview: {str(e)}",
        )


@router.get(
    "/interview/{interview_id}",
    response_model=APIResponse[InterviewResponse],
    summary="Get Interview Details (Sprint 6)",
    description="Obtiene detalles completos de una sesión de entrevista",
)
async def get_interview(
    interview_id: str,
    db: Session = Depends(get_db),
) -> APIResponse[InterviewResponse]:
    """Obtiene detalles completos de una entrevista técnica (SPRINT 6)"""
    try:
        interview_repo = InterviewSessionRepository(db)
        interview = interview_repo.get_by_id(interview_id)

        if not interview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Interview '{interview_id}' not found",
            )

        return APIResponse(
            success=True,
            data=InterviewResponse(
                interview_id=interview.id,
                session_id=interview.session_id,
                student_id=interview.student_id,
                interview_type=interview.interview_type,
                difficulty_level=interview.difficulty_level,
                questions_asked=interview.questions_asked,
                responses=interview.responses,
                evaluation_score=interview.evaluation_score,
                evaluation_breakdown=interview.evaluation_breakdown,
                feedback=interview.feedback,
                duration_minutes=interview.duration_minutes,
                created_at=interview.created_at,
                updated_at=interview.updated_at,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error("Error retrieving interview", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve interview: {str(e)}",
        )


# ============================================================================
# INCIDENT SIMULATOR (IR-IA) - HU-EST-012 - SPRINT 6
# ============================================================================


@router.post(
    "/incident/start",
    response_model=APIResponse[IncidentResponse],
    summary="Start Incident Simulation (Sprint 6)",
    description="Inicia una simulación de incidente en producción con IR-IA",
)
async def start_incident(
    request: IncidentStartRequest,
    db: Session = Depends(get_db),
) -> APIResponse[IncidentResponse]:
    """
    Inicia una simulación de respuesta a incidentes (SPRINT 6).

    El agente IR-IA generará:
    - Descripción realista del incidente
    - Logs simulados del sistema
    - Métricas simuladas (CPU, memory, requests, errors)
    """
    try:
        # Validate session
        session_repo = SessionRepository(db)
        session_db = session_repo.get_by_id(request.session_id)
        if not session_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found",
            )

        # Initialize simulator
        llm_provider = LLMProviderFactory.create_from_env()
        simulator = SimuladorProfesionalAgent(llm_provider=llm_provider)

        # Generate incident scenario
        incident_scenario = await simulator.generar_incidente(
            tipo_incidente=request.incident_type,
            severidad=request.severity,
        )

        # Create incident simulation
        incident_repo = IncidentSimulationRepository(db)
        incident = incident_repo.create(
            session_id=request.session_id,
            student_id=request.student_id,
            incident_type=request.incident_type,
            activity_id=request.activity_id,
            severity=request.severity,
            incident_description=incident_scenario.get("description", ""),
            simulated_logs=incident_scenario.get("logs", ""),
            simulated_metrics=incident_scenario.get("metrics", {}),
        )

        logger_sprint6.info(
            "Incident simulation started",
            extra={
                "incident_id": incident.id,
                "incident_type": request.incident_type,
                "severity": request.severity,
            },
        )

        return APIResponse(
            success=True,
            data=IncidentResponse(
                incident_id=incident.id,
                session_id=incident.session_id,
                student_id=incident.student_id,
                incident_type=incident.incident_type,
                severity=incident.severity,
                incident_description=incident.incident_description,
                simulated_logs=incident.simulated_logs,
                simulated_metrics=incident.simulated_metrics,
                diagnosis_process=incident.diagnosis_process,
                created_at=incident.created_at,
                updated_at=incident.updated_at,
            ),
            message="Incident simulation started successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error("Error starting incident simulation", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start incident: {str(e)}",
        )


@router.post(
    "/incident/diagnose",
    response_model=APIResponse[IncidentResponse],
    summary="Add Diagnosis Step (Sprint 6)",
    description="Agrega un paso de diagnóstico al proceso de resolución",
)
async def add_diagnosis_step(
    request: DiagnosisStepRequest,
    db: Session = Depends(get_db),
) -> APIResponse[IncidentResponse]:
    """
    Registra un paso en el proceso de diagnóstico del incidente (SPRINT 6).

    Captura:
    - Acción tomada (ej: "Revisar logs de la API")
    - Hallazgo (ej: "Error 500 en endpoint /users")
    """
    try:
        incident_repo = IncidentSimulationRepository(db)
        incident = incident_repo.get_by_id(request.incident_id)

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident '{request.incident_id}' not found",
            )

        # Add diagnosis step
        diagnosis_step = {
            "action": request.action,
            "finding": request.finding,
            "timestamp": incident.updated_at.isoformat(),
        }
        incident = incident_repo.add_diagnosis_step(incident.id, diagnosis_step)

        logger_sprint6.info(
            "Diagnosis step added",
            extra={
                "incident_id": incident.id,
                "step_count": len(incident.diagnosis_process),
            },
        )

        return APIResponse(
            success=True,
            data=IncidentResponse(
                incident_id=incident.id,
                session_id=incident.session_id,
                student_id=incident.student_id,
                incident_type=incident.incident_type,
                severity=incident.severity,
                incident_description=incident.incident_description,
                simulated_logs=incident.simulated_logs,
                simulated_metrics=incident.simulated_metrics,
                diagnosis_process=incident.diagnosis_process,
                solution_proposed=incident.solution_proposed,
                root_cause_identified=incident.root_cause_identified,
                created_at=incident.created_at,
                updated_at=incident.updated_at,
            ),
            message="Diagnosis step added successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error("Error adding diagnosis step", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add diagnosis step: {str(e)}",
        )


@router.post(
    "/incident/resolve",
    response_model=APIResponse[IncidentResponse],
    summary="Resolve Incident (Sprint 6)",
    description="Envía solución propuesta y finaliza el incidente",
)
async def resolve_incident(
    request: IncidentSolutionRequest,
    db: Session = Depends(get_db),
) -> APIResponse[IncidentResponse]:
    """
    Completa la resolución del incidente (SPRINT 6).

    El agente IR-IA evaluará:
    - Sistematización del diagnóstico
    - Priorización correcta
    - Calidad de la documentación post-mortem
    - Comunicación clara
    """
    try:
        incident_repo = IncidentSimulationRepository(db)
        incident = incident_repo.get_by_id(request.incident_id)

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident '{request.incident_id}' not found",
            )

        # Evaluate resolution with IR-IA
        llm_provider = LLMProviderFactory.create_from_env()
        simulator = SimuladorProfesionalAgent(llm_provider=llm_provider)

        evaluation = await simulator.evaluar_resolucion_incidente(
            proceso_diagnostico=incident.diagnosis_process,
            solucion=request.solution_proposed,
            causa_raiz=request.root_cause_identified,
            post_mortem=request.post_mortem,
        )

        # Calculate time metrics
        time_to_diagnose = len(incident.diagnosis_process) * 5  # Estimate 5 min per step
        time_to_resolve = int((incident.updated_at - incident.created_at).total_seconds() / 60)

        # Complete incident
        incident = incident_repo.complete_incident(
            incident_id=incident.id,
            solution_proposed=request.solution_proposed,
            root_cause_identified=request.root_cause_identified,
            post_mortem=request.post_mortem,
            time_to_diagnose_minutes=time_to_diagnose,
            time_to_resolve_minutes=time_to_resolve,
            evaluation=evaluation,
        )

        logger_sprint6.info(
            "Incident resolved",
            extra={
                "incident_id": incident.id,
                "time_to_resolve": time_to_resolve,
                "evaluation_score": evaluation.get("overall_score", 0.0),
            },
        )

        return APIResponse(
            success=True,
            data=IncidentResponse(
                incident_id=incident.id,
                session_id=incident.session_id,
                student_id=incident.student_id,
                incident_type=incident.incident_type,
                severity=incident.severity,
                incident_description=incident.incident_description,
                simulated_logs=incident.simulated_logs,
                simulated_metrics=incident.simulated_metrics,
                diagnosis_process=incident.diagnosis_process,
                solution_proposed=incident.solution_proposed,
                root_cause_identified=incident.root_cause_identified,
                time_to_diagnose_minutes=incident.time_to_diagnose_minutes,
                time_to_resolve_minutes=incident.time_to_resolve_minutes,
                post_mortem=incident.post_mortem,
                evaluation=incident.evaluation,
                created_at=incident.created_at,
                updated_at=incident.updated_at,
            ),
            message="Incident resolved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error("Error resolving incident", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve incident: {str(e)}",
        )


@router.get(
    "/incident/{incident_id}",
    response_model=APIResponse[IncidentResponse],
    summary="Get Incident Details (Sprint 6)",
    description="Obtiene detalles completos de una simulación de incidente",
)
async def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
) -> APIResponse[IncidentResponse]:
    """Obtiene detalles completos de un incidente simulado (SPRINT 6)"""
    try:
        incident_repo = IncidentSimulationRepository(db)
        incident = incident_repo.get_by_id(incident_id)

        if not incident:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident '{incident_id}' not found",
            )

        return APIResponse(
            success=True,
            data=IncidentResponse(
                incident_id=incident.id,
                session_id=incident.session_id,
                student_id=incident.student_id,
                incident_type=incident.incident_type,
                severity=incident.severity,
                incident_description=incident.incident_description,
                simulated_logs=incident.simulated_logs,
                simulated_metrics=incident.simulated_metrics,
                diagnosis_process=incident.diagnosis_process,
                solution_proposed=incident.solution_proposed,
                root_cause_identified=incident.root_cause_identified,
                time_to_diagnose_minutes=incident.time_to_diagnose_minutes,
                time_to_resolve_minutes=incident.time_to_resolve_minutes,
                post_mortem=incident.post_mortem,
                evaluation=incident.evaluation,
                created_at=incident.created_at,
                updated_at=incident.updated_at,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error("Error retrieving incident", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve incident: {str(e)}",
        )


# ============================================================================
# SCRUM MASTER SIMULATOR (SM-IA) - HU-EST-010
# ============================================================================

@router.post(
    "/scrum/daily-standup",
    response_model=APIResponse[DailyStandupResponse],
    summary="Daily Standup with Scrum Master (SM-IA)",
    description="Participar en daily standup simulado con feedback del Scrum Master",
)
async def daily_standup(
    request: DailyStandupRequest,
    db: Session = Depends(get_db),
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> APIResponse[DailyStandupResponse]:
    """
    Procesa la participación del estudiante en un daily standup simulado.

    El Scrum Master (SM-IA) analiza:
    - Claridad y concisión de la comunicación
    - Identificación de impedimentos
    - Comprensión de compromisos del sprint
    - Detección de problemas (scope creep, bloqueos, falta de foco)

    Args:
        request: Daily standup data
        db: Database session
        llm_provider: LLM provider

    Returns:
        APIResponse con feedback del SM-IA
    """
    logger_sprint6.info(
        f"Processing daily standup for student {request.student_id}",
        extra={
            "student_id": request.student_id,
            "session_id": request.session_id,
            "activity_id": request.activity_id
        }
    )

    try:
        # Verificar que la sesión existe
        session_repo = SessionRepository(db)
        session_db = session_repo.get_by_id(request.session_id)
        if not session_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found",
            )

        # Crear agente SM-IA
        sm_agent = SimuladorProfesionalAgent(
            simulator_type=None,  # SM-IA no requiere tipo específico
            llm_provider=llm_provider
        )

        # Procesar daily standup
        feedback_data = sm_agent.procesar_daily_standup(
            ayer=request.what_did_yesterday,
            hoy=request.what_will_do_today,
            impedimentos=request.impediments
        )

        # Crear trace de la interacción
        trace_repo = TraceRepository(db)
        trace_repo.create(
            student_id=request.student_id,
            activity_id=request.activity_id or "daily_standup",
            trace_level=TraceLevel.N3_INTERACCIONAL,
            interaction_type=InteractionType.STUDENT_PROMPT,
            content=f"Daily standup: {request.what_did_yesterday[:50]}...",
            ai_involvement=0.5,  # Moderada participación del AI
        )

        logger_sprint6.info(
            f"Daily standup processed successfully",
            extra={
                "student_id": request.student_id,
                "issues_detected": len(feedback_data.get("detected_issues", []))
            }
        )

        # Construir response
        response = DailyStandupResponse(
            feedback=feedback_data.get("feedback", ""),
            questions=feedback_data.get("questions", []),
            detected_issues=feedback_data.get("detected_issues", []),
            suggestions=feedback_data.get("suggestions", [])
        )

        return APIResponse(
            success=True,
            data=response,
            message="Daily standup feedback generated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error("Error processing daily standup", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process daily standup: {str(e)}",
        )


# ============================================================================
# CLIENT SIMULATOR (CX-IA) - HU-EST-013
# ============================================================================

@router.post(
    "/client/requirements",
    response_model=APIResponse[ClientResponse],
    summary="Get Client Requirements (CX-IA)",
    description="Obtener requisitos iniciales del cliente simulado",
)
async def get_client_requirements(
    request: ClientRequirementRequest,
    db: Session = Depends(get_db),
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> APIResponse[ClientResponse]:
    """
    Obtiene los requisitos iniciales del cliente simulado (CX-IA).

    El cliente presenta requisitos ambiguos, contradictorios o incompletos
    para entrenar habilidades de elicitación y comunicación.

    Args:
        request: Client requirement request
        db: Database session
        llm_provider: LLM provider

    Returns:
        APIResponse con requisitos del cliente
    """
    logger_sprint6.info(
        f"Generating client requirements for student {request.student_id}",
        extra={
            "student_id": request.student_id,
            "project_type": request.project_type
        }
    )

    try:
        # Verificar sesión
        session_repo = SessionRepository(db)
        session_db = session_repo.get_by_id(request.session_id)
        if not session_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found",
            )

        # Crear agente CX-IA
        cx_agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=llm_provider
        )

        # Generar requisitos del cliente
        client_data = cx_agent.generar_requerimientos_cliente(
            tipo_proyecto=request.project_type
        )

        # Crear trace
        trace_repo = TraceRepository(db)
        trace_repo.create(
            student_id=request.student_id,
            activity_id=request.activity_id or "client_requirements",
            trace_level=TraceLevel.N3_INTERACCIONAL,
            interaction_type=InteractionType.STUDENT_PROMPT,
            content=f"Client requirements request: {request.project_type}",
            ai_involvement=0.7,  # Alta participación del AI en generación
        )

        logger_sprint6.info(f"Client requirements generated successfully")

        # Construir response
        response = ClientResponse(
            response=client_data.get("requirements", ""),
            additional_requirements=client_data.get("additional_requirements"),
            evaluation={"empathy": 0.0, "clarity": 0.0, "professionalism": 0.0}  # Aún no hay evaluación
        )

        return APIResponse(
            success=True,
            data=response,
            message="Client requirements generated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error("Error generating client requirements", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate client requirements: {str(e)}",
        )


@router.post(
    "/client/clarify",
    response_model=APIResponse[ClientResponse],
    summary="Ask Client Clarification (CX-IA)",
    description="Hacer pregunta de clarificación al cliente",
)
async def ask_client_clarification(
    request: ClientClarificationRequest,
    db: Session = Depends(get_db),
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> APIResponse[ClientResponse]:
    """
    Envía una pregunta de clarificación al cliente simulado (CX-IA).

    El cliente evalúa las soft skills del estudiante:
    - Empatía (tono, consideración)
    - Claridad (precisión de la pregunta)
    - Profesionalismo (formalidad, respeto)

    Args:
        request: Clarification question
        db: Database session
        llm_provider: LLM provider

    Returns:
        APIResponse con respuesta del cliente y evaluación de soft skills
    """
    logger_sprint6.info(
        f"Processing client clarification question",
        extra={"session_id": request.session_id}
    )

    try:
        # Verificar sesión
        session_repo = SessionRepository(db)
        session_db = session_repo.get_by_id(request.session_id)
        if not session_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found",
            )

        # Crear agente CX-IA
        cx_agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=llm_provider
        )

        # Responder clarificación
        client_data = cx_agent.responder_clarificacion(
            pregunta=request.question
        )

        # Crear trace
        trace_repo = TraceRepository(db)
        trace_repo.create(
            student_id=session_db.student_id,
            activity_id=session_db.activity_id,
            trace_level=TraceLevel.N3_INTERACCIONAL,
            interaction_type=InteractionType.STUDENT_PROMPT,
            content=f"Client clarification: {request.question[:100]}...",
            ai_involvement=0.6,
        )

        logger_sprint6.info("Client clarification processed successfully")

        # Construir response
        response = ClientResponse(
            response=client_data.get("response", ""),
            additional_requirements=client_data.get("additional_requirements"),
            evaluation=client_data.get("soft_skills", {
                "empathy": 0.5,
                "clarity": 0.5,
                "professionalism": 0.5
            })
        )

        return APIResponse(
            success=True,
            data=response,
            message="Client clarification answered successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error("Error processing client clarification", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process clarification: {str(e)}",
        )


# ============================================================================
# DEVSECOPS AUDITOR (DSO-IA) - HU-EST-014
# ============================================================================

@router.post(
    "/security/audit",
    response_model=APIResponse[SecurityAuditResponse],
    summary="Security Code Audit (DSO-IA)",
    description="Auditar código en busca de vulnerabilidades de seguridad (OWASP Top 10)",
)
async def security_audit(
    request: SecurityAuditRequest,
    db: Session = Depends(get_db),
    llm_provider: LLMProvider = Depends(get_llm_provider),
) -> APIResponse[SecurityAuditResponse]:
    """
    Realiza una auditoría de seguridad del código proporcionado (DSO-IA).

    Detecta vulnerabilidades de OWASP Top 10:
    - SQL Injection
    - XSS (Cross-Site Scripting)
    - CSRF (Cross-Site Request Forgery)
    - Secrets hardcodeados
    - Code injection (eval, exec)
    - Path traversal
    - Weak crypto
    - Etc.

    Args:
        request: Security audit request with code
        db: Database session
        llm_provider: LLM provider

    Returns:
        APIResponse con reporte completo de seguridad
    """
    logger_sprint6.info(
        f"Starting security audit for student {request.student_id}",
        extra={
            "student_id": request.student_id,
            "language": request.language,
            "code_length": len(request.code)
        }
    )

    try:
        # Verificar sesión
        session_repo = SessionRepository(db)
        session_db = session_repo.get_by_id(request.session_id)
        if not session_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found",
            )

        # Crear agente DSO-IA
        dso_agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=llm_provider
        )

        # Realizar auditoría de seguridad
        audit_data = dso_agent.auditar_seguridad(
            codigo=request.code,
            lenguaje=request.language
        )

        # Crear trace
        trace_repo = TraceRepository(db)
        trace_repo.create(
            student_id=request.student_id,
            activity_id=request.activity_id or "security_audit",
            trace_level=TraceLevel.N3_INTERACCIONAL,
            interaction_type=InteractionType.STUDENT_PROMPT,
            content=f"Security audit ({request.language}): {len(request.code)} chars",
            ai_involvement=0.8,  # Alta participación del AI en análisis
        )

        # Convertir vulnerabilidades a SecurityVulnerability objects
        vulnerabilities = []
        for vuln in audit_data.get("vulnerabilities", []):
            vulnerabilities.append(SecurityVulnerability(
                severity=vuln.get("severity", "INFO"),
                vulnerability_type=vuln.get("vulnerability_type", "UNKNOWN"),
                line_number=vuln.get("line_number"),
                description=vuln.get("description", ""),
                recommendation=vuln.get("recommendation", ""),
                cwe_id=vuln.get("cwe_id"),
                owasp_category=vuln.get("owasp_category")
            ))

        logger_sprint6.info(
            f"Security audit completed",
            extra={
                "total_vulnerabilities": audit_data.get("total_vulnerabilities", 0),
                "critical_count": audit_data.get("critical_count", 0),
                "security_score": audit_data.get("security_score", 10.0)
            }
        )

        # Construir response
        response = SecurityAuditResponse(
            audit_id=f"audit_{session_db.id[:8]}",
            total_vulnerabilities=audit_data.get("total_vulnerabilities", 0),
            critical_count=audit_data.get("critical_count", 0),
            high_count=audit_data.get("high_count", 0),
            medium_count=audit_data.get("medium_count", 0),
            low_count=audit_data.get("low_count", 0),
            vulnerabilities=vulnerabilities,
            overall_security_score=audit_data.get("security_score", 10.0),
            recommendations=audit_data.get("recommendations", []),
            compliant_with_owasp=audit_data.get("owasp_compliant", True)
        )

        return APIResponse(
            success=True,
            data=response,
            message=f"Security audit completed: {len(vulnerabilities)} vulnerabilities found"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger_sprint6.error("Error performing security audit", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform security audit: {str(e)}",
        )
