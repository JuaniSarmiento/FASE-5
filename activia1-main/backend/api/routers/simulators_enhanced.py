"""
Router para Simuladores Profesionales Mejorados

Endpoints para el Panel de Selección de Simuladores (Frontend)

NOTA: Todos los endpoints usan APIResponse wrapper para consistencia con el resto de la API.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from ...database import SessionRepository
from ...agents.simulators import SimuladorProfesionalAgent, SimuladorType
from ...core.ai_gateway import AIGateway
from ...llm import LLMProviderFactory
from sqlalchemy.orm import Session
from ..deps import get_db
from ..schemas.common import APIResponse

router = APIRouter(prefix="/simulators-v2", tags=["simulators-enhanced"])


class SimulatorInfo(BaseModel):
    """Información de un simulador disponible"""
    id: str
    name: str
    role: str
    description: str
    difficulty: str
    personality: str
    objectives: List[str]
    skills_tested: List[str]
    color: str
    gradient: str
    required_level: int


class StartSimulationRequest(BaseModel):
    """Solicitud para iniciar una simulación"""
    simulator_id: str
    student_id: str
    activity_id: str
    context: Optional[Dict[str, Any]] = None


@router.get("/available", response_model=APIResponse[List[SimulatorInfo]])
async def get_available_simulators(
    user_level: int = 1
) -> APIResponse[List[SimulatorInfo]]:
    """
    Retorna lista de simuladores disponibles
    """
    simulators = [
        SimulatorInfo(
            id="product_owner",
            name="Patricia Owner",
            role="Product Owner",
            description="Product Owner exigente que te desafía con requisitos ambiguos y cambiantes.",
            difficulty="intermediate",
            personality="Exigente, orientada a negocio, impaciente con detalles técnicos",
            objectives=[
                "Mejorar especificación de requisitos",
                "Aprender a hacer preguntas de aclaración",
                "Entender la perspectiva de negocio"
            ],
            skills_tested=["Requirements Engineering", "Communication", "Business Analysis"],
            color="blue",
            gradient="from-blue-500 to-blue-700",
            required_level=1
        ),
        SimulatorInfo(
            id="scrum_master",
            name="Sergio Master",
            role="Scrum Master",
            description="Scrum Master que facilita ceremonias ágiles y te desafía en estimación y planificación.",
            difficulty="intermediate",
            personality="Facilitador, preguntón, enfocado en el proceso",
            objectives=[
                "Practicar estimación de tareas",
                "Mejorar planificación ágil",
                "Aprender retrospectivas efectivas"
            ],
            skills_tested=["Agile Methodologies", "Planning", "Team Collaboration"],
            color="green",
            gradient="from-green-500 to-green-700",
            required_level=2
        ),
        SimulatorInfo(
            id="senior_dev",
            name="Santiago Developer",
            role="Senior Developer",
            description="Desarrollador senior que hace code reviews implacables.",
            difficulty="advanced",
            personality="Perfeccionista, técnico, mentor exigente",
            objectives=[
                "Mejorar calidad del código",
                "Aprender patrones de diseño",
                "Entender arquitectura de software"
            ],
            skills_tested=["Code Quality", "Design Patterns", "Best Practices"],
            color="purple",
            gradient="from-purple-500 to-purple-700",
            required_level=3
        ),
        SimulatorInfo(
            id="qa_engineer",
            name="Quintín QA",
            role="QA Engineer",
            description="QA Engineer que encuentra bugs donde nadie más los ve.",
            difficulty="intermediate",
            personality="Detallista, escéptico, orientado a calidad",
            objectives=[
                "Mejorar testing skills",
                "Aprender a pensar en edge cases",
                "Desarrollar mindset de calidad"
            ],
            skills_tested=["Testing", "Quality Assurance", "Bug Detection"],
            color="orange",
            gradient="from-orange-500 to-orange-700",
            required_level=2
        ),
        SimulatorInfo(
            id="security_auditor",
            name="Sara Security",
            role="Security Auditor",
            description="Auditora de seguridad que busca vulnerabilidades en tu código.",
            difficulty="expert",
            personality="Paranoia profesional, metódica, ethical hacker",
            objectives=[
                "Identificar vulnerabilidades comunes",
                "Aprender secure coding practices",
                "Desarrollar security mindset"
            ],
            skills_tested=["Security", "Vulnerability Assessment", "Secure Coding"],
            color="red",
            gradient="from-red-500 to-red-700",
            required_level=4
        ),
        SimulatorInfo(
            id="devsecops",
            name="Diego DevSecOps",
            role="DevSecOps Engineer",
            description="Ingeniero DevSecOps que te enseña sobre CI/CD e infraestructura.",
            difficulty="advanced",
            personality="Automatizador compulsivo, security-first, pragmático",
            objectives=[
                "Aprender CI/CD pipelines",
                "Entender IaC (Infrastructure as Code)",
                "Integrar seguridad en DevOps"
            ],
            skills_tested=["DevOps", "CI/CD", "Infrastructure", "Automation"],
            color="indigo",
            gradient="from-indigo-500 to-indigo-700",
            required_level=5
        ),
        SimulatorInfo(
            id="tech_lead",
            name="Tomás Lead",
            role="Tech Lead",
            description="Tech Lead que te desafía en decisiones arquitectónicas y liderazgo.",
            difficulty="expert",
            personality="Visionario, estratégico, balance entre negocio y técnica",
            objectives=[
                "Tomar decisiones arquitectónicas",
                "Evaluar trade-offs técnicos",
                "Desarrollar liderazgo técnico"
            ],
            skills_tested=["Architecture", "Technical Leadership", "Decision Making"],
            color="yellow",
            gradient="from-yellow-500 to-yellow-700",
            required_level=6
        ),
        SimulatorInfo(
            id="demanding_client",
            name="Clara Cliente",
            role="Cliente Exigente",
            description="Cliente que no entiende de tecnología pero sabe lo que quiere.",
            difficulty="beginner",
            personality="Impaciente, cambiante, orientada a resultados",
            objectives=[
                "Mejorar comunicación no-técnica",
                "Aprender a manejar cambios de alcance",
                "Desarrollar soft skills"
            ],
            skills_tested=["Communication", "Expectation Management", "Soft Skills"],
            color="pink",
            gradient="from-pink-500 to-pink-700",
            required_level=1
        )
    ]

    # Filtrar por nivel de usuario si es necesario
    available = [s for s in simulators if s.required_level <= user_level]

    return APIResponse(
        success=True,
        data=available,
        message=f"Found {len(available)} simulators available for level {user_level}"
    )


@router.post("/start", response_model=APIResponse[Dict[str, Any]])
async def start_simulation(
    request: StartSimulationRequest,
    db: Session = Depends(get_db)
) -> APIResponse[Dict[str, Any]]:
    """
    Inicia una nueva sesión de simulación
    """
    # Validar que el simulador existe
    simulator_type_map = {
        "product_owner": SimuladorType.PRODUCT_OWNER,
        "scrum_master": SimuladorType.SCRUM_MASTER,
        "senior_dev": SimuladorType.SENIOR_DEV,
        "qa_engineer": SimuladorType.QA_ENGINEER,
        "security_auditor": SimuladorType.SECURITY_AUDITOR,
        "devsecops": SimuladorType.DEVSECOPS,
        "tech_lead": SimuladorType.TECH_LEAD,
        "demanding_client": SimuladorType.DEMANDING_CLIENT
    }

    if request.simulator_id not in simulator_type_map:
        raise HTTPException(status_code=400, detail="Simulador no válido")

    # Crear sesión
    session_repo = SessionRepository(db)
    session = session_repo.create(
        student_id=request.student_id,
        activity_id=request.activity_id,
        mode="SIMULATOR",
        simulator_type=request.simulator_id
    )

    # Inicializar simulador
    simulator_type = simulator_type_map[request.simulator_id]
    simulator = SimuladorProfesionalAgent(
        simulator_type=simulator_type,
        llm_provider=None,  # Se inyectará en producción
        config=request.context or {}
    )

    # Generar mensaje de bienvenida
    welcome_message = simulator.generate_welcome_message()

    return APIResponse(
        success=True,
        data={
            "session_id": session.id,
            "simulator_id": request.simulator_id,
            "simulator_name": simulator_type_map[request.simulator_id].value,
            "welcome_message": welcome_message,
            "status": "started",
            "timestamp": datetime.now().isoformat()
        },
        message=f"Simulation started for {request.simulator_id}"
    )


@router.get("/{simulator_id}/scenarios", response_model=APIResponse[List[Dict[str, Any]]])
async def get_simulator_scenarios(
    simulator_id: str
) -> APIResponse[List[Dict[str, Any]]]:
    """
    Retorna escenarios disponibles para un simulador específico
    """
    # Escenarios predefinidos por simulador
    scenarios = {
        "product_owner": [
            {
                "id": "ambiguous_requirements",
                "title": "Requisitos Ambiguos",
                "description": "El PO te da requisitos vagos. Debes hacer las preguntas correctas.",
                "difficulty": "medium"
            },
            {
                "id": "scope_creep",
                "title": "Cambio de Alcance",
                "description": "A mitad del sprint, el PO quiere agregar funcionalidades.",
                "difficulty": "hard"
            }
        ],
        "scrum_master": [
            {
                "id": "sprint_planning",
                "title": "Planificación de Sprint",
                "description": "Debes estimar y planificar un sprint completo.",
                "difficulty": "medium"
            },
            {
                "id": "retrospective",
                "title": "Retrospectiva",
                "description": "Facilita una retrospectiva identificando mejoras.",
                "difficulty": "medium"
            }
        ],
        "senior_dev": [
            {
                "id": "code_review",
                "title": "Code Review Implacable",
                "description": "El senior dev revisa tu código en detalle.",
                "difficulty": "hard"
            },
            {
                "id": "refactoring",
                "title": "Refactorización",
                "description": "Te pide refactorizar código legacy aplicando patrones.",
                "difficulty": "expert"
            }
        ]
    }

    result = scenarios.get(simulator_id, [])
    return APIResponse(
        success=True,
        data=result,
        message=f"Found {len(result)} scenarios for {simulator_id}"
    )


@router.get("/stats/{student_id}", response_model=APIResponse[Dict[str, Any]])
async def get_student_simulator_stats(
    student_id: str,
    db: Session = Depends(get_db)
) -> APIResponse[Dict[str, Any]]:
    """
    Retorna estadísticas del estudiante en simuladores
    """
    session_repo = SessionRepository(db)

    # Obtener todas las sesiones de simuladores del estudiante
    all_sessions = session_repo.get_by_student(student_id)
    simulator_sessions = [s for s in all_sessions if s.mode == "SIMULATOR"]

    # Calcular estadísticas
    completed_simulators = list(set([
        s.simulator_type for s in simulator_sessions
        if s.status == "completed" and s.simulator_type
    ]))

    total_sessions = len(simulator_sessions)
    completion_rate = len([s for s in simulator_sessions if s.status == "completed"]) / max(total_sessions, 1)

    # Por tipo de simulador
    by_type = {}
    for session in simulator_sessions:
        sim_type = session.simulator_type or "unknown"
        if sim_type not in by_type:
            by_type[sim_type] = {"total": 0, "completed": 0}
        by_type[sim_type]["total"] += 1
        if session.status == "completed":
            by_type[sim_type]["completed"] += 1

    return APIResponse(
        success=True,
        data={
            "student_id": student_id,
            "total_simulator_sessions": total_sessions,
            "completed_simulators": completed_simulators,
            "completion_rate": round(completion_rate, 2),
            "by_simulator_type": by_type,
            "student_level": len(completed_simulators) + 1  # Nivel basado en simuladores completados
        },
        message=f"Stats retrieved for student {student_id}"
    )
