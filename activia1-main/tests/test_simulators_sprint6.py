"""
Tests para simuladores profesionales Sprint 6

Cubre:
- Repositorios: InterviewSessionRepository, IncidentSimulationRepository
- Endpoints API: /simulators/interview/*, /simulators/incident/*
- Métodos de agentes: generar_pregunta_entrevista, generar_incidente, etc.
"""
import pytest
from datetime import datetime

from backend.database.repositories import (
    InterviewSessionRepository,
    IncidentSimulationRepository,
)
from backend.agents.simulators import SimuladorProfesionalAgent


# ============================================================================
# FIXTURES - Reutilizamos las del conftest.py global
# ============================================================================


@pytest.fixture
def interview_repo(db_session):
    """Repository de entrevistas"""
    return InterviewSessionRepository(db_session)


@pytest.fixture
def incident_repo(db_session):
    """Repository de incidentes"""
    return IncidentSimulationRepository(db_session)


# ============================================================================
# TESTS DE REPOSITORIOS
# ============================================================================


class TestInterviewSessionRepository:
    """Tests para InterviewSessionRepository"""

    def test_create_interview_session(self, interview_repo, session_id):
        """Test: Crear sesión de entrevista"""
        interview = interview_repo.create(
            session_id=session_id,
            student_id="student_test_001",
            interview_type="CONCEPTUAL",
            difficulty_level="MEDIUM"
        )

        assert interview is not None
        assert interview.session_id == session_id
        assert interview.student_id == "student_test_001"
        assert interview.interview_type == "CONCEPTUAL"
        assert interview.difficulty_level == "MEDIUM"
        assert interview.questions_asked == []
        assert interview.responses == []
        assert interview.evaluation_score is None

    def test_add_question(self, interview_repo, session_id):
        """Test: Agregar pregunta a entrevista"""
        interview = interview_repo.create(
            session_id=session_id,
            student_id="student_test_001",
            interview_type="ALGORITHMIC",
            difficulty_level="HARD"
        )

        question_data = {
            "question": "¿Cómo invertirías una lista enlazada?",
            "type": "ALGORITHMIC",
            "timestamp": datetime.utcnow().isoformat()
        }

        updated = interview_repo.add_question(interview.id, question_data)

        assert updated is not None
        assert len(updated.questions_asked) == 1
        assert updated.questions_asked[0]["question"] == question_data["question"]

    def test_add_response(self, interview_repo, session_id):
        """Test: Agregar respuesta del estudiante"""
        interview = interview_repo.create(
            session_id=session_id,
            student_id="student_test_001",
            interview_type="DESIGN",
            difficulty_level="MEDIUM"
        )

        # Agregar pregunta primero
        question_data = {"question": "Diseñá un sistema de caché", "type": "DESIGN"}
        interview = interview_repo.add_question(interview.id, question_data)

        # Agregar respuesta
        response_data = {
            "response": "Usaría Redis con LRU eviction policy...",
            "timestamp": datetime.utcnow().isoformat(),
            "evaluation": {
                "clarity_score": 0.8,
                "technical_accuracy": 0.9
            }
        }

        updated = interview_repo.add_response(interview.id, response_data)

        assert updated is not None
        assert len(updated.responses) == 1
        assert updated.responses[0]["response"] == response_data["response"]
        assert updated.responses[0]["evaluation"]["clarity_score"] == 0.8

    def test_complete_interview(self, interview_repo, session_id):
        """Test: Completar entrevista con evaluación final"""
        interview = interview_repo.create(
            session_id=session_id,
            student_id="student_test_001",
            interview_type="BEHAVIORAL",
            difficulty_level="EASY"
        )

        # Agregar preguntas y respuestas
        interview = interview_repo.add_question(interview.id, {"question": "Q1"})
        interview = interview_repo.add_response(interview.id, {"response": "R1", "evaluation": {}})

        # Completar
        completed = interview_repo.complete_interview(
            interview_id=interview.id,
            evaluation_score=0.75,
            evaluation_breakdown={"clarity": 0.8, "technical_accuracy": 0.7},
            feedback="Buen desempeño general",
            duration_minutes=25
        )

        assert completed is not None
        assert completed.evaluation_score == 0.75
        assert completed.evaluation_breakdown["clarity"] == 0.8
        assert completed.feedback == "Buen desempeño general"
        assert completed.duration_minutes == 25

    def test_get_by_student(self, interview_repo, session_id):
        """Test: Obtener entrevistas por estudiante"""
        # Crear 3 entrevistas
        for i in range(3):
            interview_repo.create(
                session_id=session_id,
                student_id="student_test_001",
                interview_type="CONCEPTUAL",
                difficulty_level="MEDIUM"
            )

        interviews = interview_repo.get_by_student("student_test_001")

        # Module-scoped DB means records accumulate, so check at least 3
        assert len(interviews) >= 3
        assert all(i.student_id == "student_test_001" for i in interviews)


class TestIncidentSimulationRepository:
    """Tests para IncidentSimulationRepository"""

    def test_create_incident_simulation(self, incident_repo, session_id):
        """Test: Crear simulación de incidente"""
        incident = incident_repo.create(
            session_id=session_id,
            student_id="student_test_001",
            incident_type="API_ERROR",
            severity="HIGH",
            incident_description="API endpoint /users devuelve HTTP 500",
            simulated_logs="[ERROR] NullPointerException...",
            simulated_metrics={"cpu_usage_percent": 45, "error_rate_percent": 85}
        )

        assert incident is not None
        assert incident.incident_type == "API_ERROR"
        assert incident.severity == "HIGH"
        assert incident.simulated_metrics["cpu_usage_percent"] == 45
        assert incident.diagnosis_process == []

    def test_add_diagnosis_step(self, incident_repo, session_id):
        """Test: Agregar paso de diagnóstico"""
        incident = incident_repo.create(
            session_id=session_id,
            student_id="student_test_001",
            incident_type="PERFORMANCE",
            severity="CRITICAL",
            incident_description="Degradación severa de performance"
        )

        diagnosis_step = {
            "action": "Revisar logs de la aplicación",
            "finding": "Slow query detectada: 12,345ms",
            "timestamp": datetime.utcnow().isoformat()
        }

        updated = incident_repo.add_diagnosis_step(incident.id, diagnosis_step)

        assert updated is not None
        assert len(updated.diagnosis_process) == 1
        assert updated.diagnosis_process[0]["action"] == diagnosis_step["action"]
        assert updated.diagnosis_process[0]["finding"] == diagnosis_step["finding"]

    def test_complete_incident(self, incident_repo, session_id):
        """Test: Completar incidente con solución"""
        incident = incident_repo.create(
            session_id=session_id,
            student_id="student_test_001",
            incident_type="DATABASE",
            severity="CRITICAL",
            incident_description="Base de datos no responde"
        )

        # Agregar pasos de diagnóstico
        incident = incident_repo.add_diagnosis_step(incident.id, {
            "action": "Verificar conexiones DB",
            "finding": "Connection pool exhausted"
        })

        # Completar
        completed = incident_repo.complete_incident(
            incident_id=incident.id,
            solution_proposed="Aumentar pool size y agregar connection timeout",
            root_cause_identified="Pool size insuficiente para carga actual",
            post_mortem="El incidente fue causado por...",
            time_to_diagnose_minutes=10,
            time_to_resolve_minutes=25,
            evaluation={
                "overall_score": 0.8,
                "diagnosis_systematic": 0.85,
                "prioritization": 0.75
            }
        )

        assert completed is not None
        assert completed.solution_proposed is not None
        assert completed.root_cause_identified is not None
        assert completed.time_to_diagnose_minutes == 10
        assert completed.evaluation["overall_score"] == 0.8

    def test_get_by_student(self, incident_repo, session_id):
        """Test: Obtener incidentes por estudiante"""
        # Crear 2 incidentes
        for i in range(2):
            incident_repo.create(
                session_id=session_id,
                student_id="student_test_001",
                incident_type="SECURITY",
                severity="HIGH",
                incident_description="SQL injection detectado"
            )

        incidents = incident_repo.get_by_student("student_test_001")

        # Module-scoped DB means records accumulate, so check at least 2
        assert len(incidents) >= 2
        assert all(i.student_id == "student_test_001" for i in incidents)


# ============================================================================
# TESTS DE AGENTES
# ============================================================================


class TestSimuladorProfesionalAgentITIA:
    """Tests para métodos de IT-IA (Technical Interviewer)"""

    def test_generar_pregunta_entrevista_sin_llm(self):
        """Test: Generar pregunta sin LLM (fallback)"""
        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=None
        )

        question = agent.generar_pregunta_entrevista(
            tipo_entrevista="CONCEPTUAL",
            dificultad="MEDIUM"
        )

        assert question is not None
        assert isinstance(question, str)
        assert len(question) > 10
        assert "herencia" in question.lower() or "composición" in question.lower()

    def test_generar_pregunta_entrevista_con_llm(self, mock_llm_provider):
        """Test: Generar pregunta con LLM"""
        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=mock_llm_provider
        )

        question = agent.generar_pregunta_entrevista(
            tipo_entrevista="ALGORITHMIC",
            dificultad="HARD",
            contexto="Preguntas previas: 2"
        )

        assert question is not None
        assert isinstance(question, str)
        # Mock provider debería retornar algo
        assert len(question) > 0

    def test_evaluar_respuesta_entrevista_sin_llm(self):
        """Test: Evaluar respuesta sin LLM (heurística)"""
        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=None
        )

        evaluation = agent.evaluar_respuesta_entrevista(
            pregunta="¿Qué es un algoritmo?",
            respuesta="Un algoritmo es una secuencia de pasos que resuelve un problema. Por ejemplo, un algoritmo de ordenamiento como quicksort tiene complejidad O(n log n) en promedio.",
            tipo_entrevista="CONCEPTUAL"
        )

        assert evaluation is not None
        assert "clarity_score" in evaluation
        assert "technical_accuracy" in evaluation
        assert "thinking_aloud" in evaluation
        assert 0.0 <= evaluation["clarity_score"] <= 1.0
        assert 0.0 <= evaluation["technical_accuracy"] <= 1.0
        assert isinstance(evaluation["thinking_aloud"], bool)

    def test_generar_evaluacion_entrevista(self):
        """Test: Generar evaluación final"""
        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=None
        )

        preguntas = [
            {"question": "¿Qué es recursión?", "type": "CONCEPTUAL"},
            {"question": "Implementá factorial recursivo", "type": "ALGORITHMIC"}
        ]

        respuestas = [
            {
                "response": "Recursión es cuando una función se llama a sí misma",
                "evaluation": {"clarity_score": 0.7, "technical_accuracy": 0.8, "thinking_aloud": True}
            },
            {
                "response": "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
                "evaluation": {"clarity_score": 0.9, "technical_accuracy": 0.95, "thinking_aloud": False}
            }
        ]

        final_eval = agent.generar_evaluacion_entrevista(
            preguntas=preguntas,
            respuestas=respuestas,
            tipo_entrevista="CONCEPTUAL"
        )

        assert final_eval is not None
        assert "overall_score" in final_eval
        assert "breakdown" in final_eval
        assert "feedback" in final_eval
        assert 0.0 <= final_eval["overall_score"] <= 1.0
        assert "clarity" in final_eval["breakdown"]
        assert "technical_accuracy" in final_eval["breakdown"]


class TestSimuladorProfesionalAgentIRIA:
    """Tests para métodos de IR-IA (Incident Responder)"""

    def test_generar_incidente_sin_llm(self):
        """Test: Generar incidente sin LLM (fallback)"""
        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=None
        )

        incident = agent.generar_incidente(
            tipo_incidente="API_ERROR",
            severidad="HIGH"
        )

        assert incident is not None
        assert "description" in incident
        assert "logs" in incident
        assert "metrics" in incident
        assert "cpu_usage_percent" in incident["metrics"]
        assert "error_rate_percent" in incident["metrics"]
        assert "🚨" in incident["description"]

    def test_generar_incidente_tipos_diferentes(self):
        """Test: Generar diferentes tipos de incidentes"""
        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=None
        )

        tipos = ["API_ERROR", "PERFORMANCE", "SECURITY", "DATABASE", "DEPLOYMENT"]

        for tipo in tipos:
            incident = agent.generar_incidente(tipo_incidente=tipo, severidad="CRITICAL")

            assert incident is not None
            assert incident["description"] is not None
            assert incident["logs"] is not None
            assert len(incident["logs"]) > 0
            assert incident["metrics"]["cpu_usage_percent"] >= 0

    def test_evaluar_resolucion_incidente_sin_llm(self):
        """Test: Evaluar resolución sin LLM (heurística)"""
        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=None
        )

        proceso_diagnostico = [
            {"action": "Revisar logs", "finding": "OutOfMemoryError detectado"},
            {"action": "Verificar métricas", "finding": "Memory usage al 98%"},
            {"action": "Analizar heap dump", "finding": "Memory leak en cache"}
        ]

        evaluation = agent.evaluar_resolucion_incidente(
            proceso_diagnostico=proceso_diagnostico,
            solucion="Implementar eviction policy en cache y aumentar heap size",
            causa_raiz="Cache sin límite de tamaño causaba memory leak",
            post_mortem="El incidente fue causado por falta de eviction policy en el cache. Implementamos LRU eviction y aumentamos heap size de 2GB a 4GB. Métricas de memory estables después del fix."
        )

        assert evaluation is not None
        assert "overall_score" in evaluation
        assert "diagnosis_systematic" in evaluation
        assert "prioritization" in evaluation
        assert "documentation_quality" in evaluation
        assert "communication_clarity" in evaluation
        assert 0.0 <= evaluation["overall_score"] <= 1.0


class TestSimuladorProfesionalAgentOtros:
    """Tests para otros métodos de simuladores"""

    def test_procesar_daily_standup(self):
        """Test: Procesar daily standup (SM-IA)"""
        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=None
        )

        response = agent.procesar_daily_standup(
            que_hizo_ayer="Implementé la autenticación JWT",
            que_hara_hoy="Voy a agregar tests de integración",
            impedimentos="Necesito acceso a la base de datos de staging"
        )

        assert response is not None
        assert "feedback" in response
        assert "questions" in response
        assert "detected_issues" in response
        assert "suggestions" in response
        assert len(response["questions"]) > 0  # Debe preguntar sobre impedimento

    def test_generar_requerimientos_cliente(self):
        """Test: Generar requerimientos cliente (CX-IA)"""
        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=None
        )

        response = agent.generar_requerimientos_cliente("WEB_APP")

        assert response is not None
        assert "requirements" in response
        assert "additional" in response
        assert isinstance(response["additional"], list)
        assert "WEB_APP" in response["requirements"]

    def test_auditar_seguridad_sin_vulnerabilidades(self):
        """Test: Auditar código seguro (DSO-IA)"""
        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=None
        )

        codigo_seguro = """
def get_user(user_id):
    query = "SELECT * FROM users WHERE id = ?"
    return db.execute(query, (user_id,))
"""

        audit = agent.auditar_seguridad(codigo=codigo_seguro, lenguaje="python")

        assert audit is not None
        assert audit["total_vulnerabilities"] == 0
        assert audit["security_score"] == 10.0
        assert audit["owasp_compliant"] is True

    def test_auditar_seguridad_con_vulnerabilidades(self):
        """Test: Auditar código con vulnerabilidades (DSO-IA)"""
        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=None
        )

        codigo_inseguro = """
password = "admin123"
user_input = request.GET['name']
query = "SELECT * FROM users WHERE name = '%s'" % user_input
result = eval(user_input)
"""

        audit = agent.auditar_seguridad(codigo=codigo_inseguro, lenguaje="python")

        assert audit is not None
        assert audit["total_vulnerabilities"] > 0
        assert audit["critical_count"] > 0
        assert audit["security_score"] < 10.0
        assert audit["owasp_compliant"] is False

        # Verificar que detectó al menos algunas vulnerabilidades esperadas
        vuln_types = [v["vulnerability_type"] for v in audit["vulnerabilities"]]
        assert "CODE_INJECTION" in vuln_types  # eval() detectado
        assert "HARDCODED_CREDENTIALS" in vuln_types  # password hardcoded detectado
        # SQL injection se detecta cuando hay SELECT * FROM y % juntos
        assert len(vuln_types) >= 2  # Al menos 2 vulnerabilidades críticas


# ============================================================================
# TESTS DE INTEGRACIÓN
# ============================================================================


class TestIntegracionCompleta:
    """Tests de integración end-to-end"""

    def test_flujo_completo_entrevista(self, interview_repo, session_id, db_session, mock_llm_provider):
        """Test: Flujo completo de entrevista técnica"""
        from backend.database.models import SessionDB
        from backend.database.repositories import SessionRepository

        # Crear sesión en DB primero
        session_repo = SessionRepository(db_session)
        session_db = session_repo.create(
            student_id="student_test_001",
            activity_id="prog2_tp1",
            mode="TUTOR"
        )

        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=mock_llm_provider
        )

        # 1. Crear entrevista
        interview = interview_repo.create(
            session_id=session_db.id,
            student_id="student_test_001",
            interview_type="CONCEPTUAL",
            difficulty_level="MEDIUM"
        )
        assert interview is not None

        # 2. Generar pregunta
        question = agent.generar_pregunta_entrevista("CONCEPTUAL", "MEDIUM")
        interview = interview_repo.add_question(interview.id, {
            "question": question,
            "type": "CONCEPTUAL",
            "timestamp": datetime.utcnow().isoformat()
        })
        assert len(interview.questions_asked) == 1

        # 3. Estudiante responde
        student_response = "La herencia permite reutilizar código de una clase base..."

        # 4. Evaluar respuesta
        evaluation = agent.evaluar_respuesta_entrevista(
            pregunta=question,
            respuesta=student_response,
            tipo_entrevista="CONCEPTUAL"
        )

        interview = interview_repo.add_response(interview.id, {
            "response": student_response,
            "evaluation": evaluation,
            "timestamp": datetime.utcnow().isoformat()
        })
        assert len(interview.responses) == 1

        # 5. Generar evaluación final
        final_eval = agent.generar_evaluacion_entrevista(
            preguntas=interview.questions_asked,
            respuestas=interview.responses,
            tipo_entrevista="CONCEPTUAL"
        )

        # 6. Completar entrevista
        completed = interview_repo.complete_interview(
            interview_id=interview.id,
            evaluation_score=final_eval["overall_score"],
            evaluation_breakdown=final_eval["breakdown"],
            feedback=final_eval["feedback"],
            duration_minutes=20
        )

        assert completed.evaluation_score is not None
        assert completed.feedback is not None
        assert completed.duration_minutes == 20

    def test_flujo_completo_incidente(self, incident_repo, session_id, db_session):
        """Test: Flujo completo de resolución de incidente"""
        from backend.database.repositories import SessionRepository

        # Crear sesión en DB primero
        session_repo = SessionRepository(db_session)
        session_db = session_repo.create(
            student_id="student_test_001",
            activity_id="prog2_tp1",
            mode="TUTOR"
        )

        agent = SimuladorProfesionalAgent(
            simulator_type=None,
            llm_provider=None
        )

        # 1. Generar incidente
        incident_data = agent.generar_incidente("PERFORMANCE", "CRITICAL")

        # 2. Crear simulación
        incident = incident_repo.create(
            session_id=session_db.id,
            student_id="student_test_001",
            incident_type="PERFORMANCE",
            severity="CRITICAL",
            incident_description=incident_data["description"],
            simulated_logs=incident_data["logs"],
            simulated_metrics=incident_data["metrics"]
        )
        assert incident is not None

        # 3. Proceso de diagnóstico
        diagnosis_steps = [
            {"action": "Revisar logs", "finding": "Slow query detectada"},
            {"action": "Analizar query", "finding": "Missing index en WHERE clause"},
            {"action": "Verificar índices", "finding": "No hay índice en user_id"}
        ]

        for step in diagnosis_steps:
            incident = incident_repo.add_diagnosis_step(incident.id, step)

        assert len(incident.diagnosis_process) == 3

        # 4. Proponer solución
        solution = "Crear índice compuesto en (user_id, created_at)"
        root_cause = "Falta de índice causaba full table scan"
        post_mortem = "Incidente causado por query sin índice. Agregamos índice y tiempos bajaron de 12s a 50ms."

        # 5. Evaluar resolución
        evaluation = agent.evaluar_resolucion_incidente(
            proceso_diagnostico=incident.diagnosis_process,
            solucion=solution,
            causa_raiz=root_cause,
            post_mortem=post_mortem
        )

        # 6. Completar incidente
        completed = incident_repo.complete_incident(
            incident_id=incident.id,
            solution_proposed=solution,
            root_cause_identified=root_cause,
            post_mortem=post_mortem,
            time_to_diagnose_minutes=15,
            time_to_resolve_minutes=30,
            evaluation=evaluation
        )

        assert completed.solution_proposed is not None
        assert completed.evaluation["overall_score"] > 0.0
        assert completed.time_to_resolve_minutes == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
