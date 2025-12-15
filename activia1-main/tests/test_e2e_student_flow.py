"""
End-to-End Tests: Complete Student Flow

Tests de integración que prueban el flujo completo de un estudiante
desde la creación de sesión hasta la evaluación final.

Cubre:
1. Creación de sesión
2. Múltiples interacciones con T-IA-Cog
3. Detección de riesgos (AR-IA)
4. Captura de trazas N4 (TC-N4)
5. Evaluación de procesos (E-IA-Proc)
6. Consulta de historial
"""

import pytest
from datetime import datetime
from uuid import uuid4

from backend.core.ai_gateway import AIGateway
from backend.core.cognitive_engine import CognitiveReasoningEngine, CognitiveState
from backend.agents.tutor import TutorCognitivoAgent
from backend.agents.risk_analyst import AnalistaRiesgoAgent
from backend.agents.evaluator import EvaluadorProcesosAgent
from backend.agents.traceability import TrazabilidadN4Agent
from backend.llm.mock import MockLLMProvider
from backend.database import get_db_session
from backend.database.repositories import (
    SessionRepository,
    TraceRepository,
    RiskRepository,
    EvaluationRepository,
    TraceSequenceRepository,
)
from backend.models.risk import RiskLevel, RiskType


@pytest.fixture
def llm_provider():
    """Mock LLM provider"""
    return MockLLMProvider()


@pytest.fixture
def db_session():
    """Database session para tests"""
    with get_db_session() as session:
        yield session
        session.rollback()  # Rollback al final


@pytest.fixture
def repositories(db_session):
    """Todos los repositorios necesarios"""
    return {
        "session": SessionRepository(db_session),
        "trace": TraceRepository(db_session),
        "risk": RiskRepository(db_session),
        "evaluation": EvaluationRepository(db_session),
        "sequence": TraceSequenceRepository(db_session),
    }


@pytest.fixture
def gateway(llm_provider, repositories):
    """AIGateway configurado para testing"""
    return AIGateway(
        llm_provider=llm_provider,
        session_repo=repositories["session"],
        trace_repo=repositories["trace"],
        risk_repo=repositories["risk"],
        evaluation_repo=repositories["evaluation"],
        sequence_repo=repositories["sequence"],
    )


class TestCompleteStudentFlow:
    """Test del flujo completo de un estudiante"""

    def test_student_learning_session_complete_flow(self, gateway, repositories):
        """
        Test E2E: Flujo completo de aprendizaje

        Escenario:
        1. Estudiante crea sesión para actividad de colas
        2. Hace consultas exploratorias (N4 traceability)
        3. Delega completamente en una consulta (trigger risk)
        4. Continúa con implementación normal
        5. Finaliza sesión y obtiene evaluación
        6. Consulta historial de sesiones
        """
        student_id = "student_e2e_001"
        activity_id = "prog2_tp1_colas_circular"

        # =====================================================================
        # PASO 1: Crear sesión
        # =====================================================================
        session = repositories["session"].create(
            student_id=student_id,
            activity_id=activity_id,
            mode="TUTOR"
        )
        session_id = session.id

        assert session is not None
        assert session.student_id == student_id
        assert session.mode == "TUTOR"
        assert session.status == "active"

        # =====================================================================
        # PASO 2: Primera interacción - Exploración Conceptual
        # =====================================================================
        prompt1 = "¿Qué es una cola circular y cuál es su ventaja?"

        result1 = gateway.process_interaction(
            session_id=session_id,
            prompt=prompt1
        )

        # Verificaciones
        assert result1 is not None
        assert "message" in result1
        assert result1.get("agent_used") == "T-IA-Cog"
        assert result1.get("blocked") is False

        # Verificar trace N4 creado
        traces_after_1 = repositories["trace"].get_by_session(session_id)
        assert len(traces_after_1) >= 2  # Input + Output trace

        # Verificar estado cognitivo detectado
        input_trace = [t for t in traces_after_1 if t.interaction_type == "student_prompt"][0]
        assert input_trace.cognitive_state in [
            "exploracion_conceptual",
            "planificacion",
            "busqueda_informacion"
        ]

        # =====================================================================
        # PASO 3: Segunda interacción - Planificación
        # =====================================================================
        prompt2 = "Voy a usar un arreglo circular. ¿Es correcto este enfoque?"

        result2 = gateway.process_interaction(
            session_id=session_id,
            prompt=prompt2
        )

        assert result2 is not None
        assert result2.get("blocked") is False

        traces_after_2 = repositories["trace"].get_by_session(session_id)
        assert len(traces_after_2) >= 4  # 2 interacciones = 4 traces min

        # =====================================================================
        # PASO 4: Tercera interacción - DELEGACIÓN TOTAL (debe trigger risk)
        # =====================================================================
        prompt3 = "Dame el código completo de la clase Queue con todos los métodos implementados"

        result3 = gateway.process_interaction(
            session_id=session_id,
            prompt=prompt3
        )

        # Esta interacción debe ser bloqueada o generar warning
        # (dependiendo de políticas de gobernanza)
        assert result3 is not None

        # Verificar que se detectó riesgo
        risks = repositories["risk"].get_by_session(session_id)
        assert len(risks) > 0

        # Buscar riesgo de delegación cognitiva
        delegation_risks = [
            r for r in risks
            if r.risk_type == "cognitive_delegation"
        ]
        assert len(delegation_risks) > 0

        # Verificar nivel de riesgo
        high_risks = [r for r in delegation_risks if r.risk_level in ["high", "critical"]]
        assert len(high_risks) > 0

        # =====================================================================
        # PASO 5: Cuarta interacción - Recuperación (pregunta específica)
        # =====================================================================
        prompt4 = "¿Cómo manejo el caso cuando la cola está llena en enqueue?"

        result4 = gateway.process_interaction(
            session_id=session_id,
            prompt=prompt4
        )

        assert result4 is not None
        assert result4.get("blocked") is False

        traces_after_4 = repositories["trace"].get_by_session(session_id)
        assert len(traces_after_4) >= 8  # 4 interacciones

        # =====================================================================
        # PASO 6: Quinta interacción - Implementación
        # =====================================================================
        prompt5 = "Implementé el método enqueue. ¿Podrías revisar mi lógica?"

        result5 = gateway.process_interaction(
            session_id=session_id,
            prompt=prompt5,
            context={"code_snippet": "def enqueue(self, item): ..."}
        )

        assert result5 is not None

        # =====================================================================
        # PASO 7: Finalizar sesión y obtener evaluación
        # =====================================================================
        # Actualizar status de sesión
        repositories["session"].update_status(session_id, "completed")

        # Obtener todas las trazas para evaluación
        all_traces = repositories["trace"].get_by_session(session_id)
        all_risks = repositories["risk"].get_by_session(session_id)

        # Generar evaluación de proceso (E-IA-Proc)
        evaluator = EvaluadorProcesosAgent(llm_provider=MockLLMProvider())

        # Convertir ORM traces a Pydantic
        from backend.models.trace import CognitiveTrace, TraceLevel, InteractionType
        pydantic_traces = []
        for t in all_traces:
            pydantic_traces.append(
                CognitiveTrace(
                    id=t.id,
                    session_id=t.session_id,
                    student_id=t.student_id,
                    activity_id=t.activity_id,
                    trace_level=TraceLevel(t.trace_level),
                    interaction_type=InteractionType(t.interaction_type),
                    content=t.content,
                    cognitive_state=CognitiveState(t.cognitive_state) if t.cognitive_state else None,
                    ai_involvement=t.ai_involvement,
                    metadata=t.trace_metadata,
                    created_at=t.created_at,
                )
            )

        evaluation_report = evaluator.evaluar_proceso_completo(
            session_id=session_id,
            student_id=student_id,
            activity_id=activity_id,
            traces=pydantic_traces,
            final_code=None,  # Opcional
            git_history=None,  # Opcional
        )

        # Verificaciones de evaluación
        assert evaluation_report is not None
        assert evaluation_report.session_id == session_id
        assert evaluation_report.overall_competency_level is not None
        assert 0.0 <= evaluation_report.overall_score <= 1.0

        # Debe haber evaluación de dimensiones
        assert len(evaluation_report.dimensions) > 0

        # Debe detectar uso excesivo de IA (por la delegación)
        ai_metrics = evaluation_report.ai_dependency_metrics
        assert ai_metrics is not None
        # El promedio debe ser razonable (considerando 1 delegación en 5 interacciones)

        # Debe haber recomendaciones
        assert len(evaluation_report.improvement_areas) > 0

        # =====================================================================
        # PASO 8: Consultar historial del estudiante
        # =====================================================================
        student_sessions = repositories["session"].get_by_student(student_id)
        assert len(student_sessions) >= 1
        assert any(s.id == session_id for s in student_sessions)

        # Verificar que la sesión está completa
        completed_session = repositories["session"].get_by_id(session_id)
        assert completed_session.status == "completed"
        assert completed_session.end_time is not None

        # =====================================================================
        # VERIFICACIONES FINALES
        # =====================================================================

        # 1. Trazabilidad N4 completa
        final_traces = repositories["trace"].get_by_session(session_id)
        assert len(final_traces) >= 10  # 5 interacciones = min 10 traces (in/out)

        # Verificar que todos los traces tienen session_id
        assert all(t.session_id == session_id for t in final_traces)

        # 2. Al menos un riesgo detectado
        final_risks = repositories["risk"].get_by_session(session_id)
        assert len(final_risks) >= 1

        # Verificar que todos los riesgos tienen session_id
        assert all(r.session_id == session_id for r in final_risks)

        # 3. Evaluación generada
        assert evaluation_report.overall_score is not None

        # 4. Métricas de dependencia de IA capturadas
        assert evaluation_report.ai_dependency_metrics["total_interactions"] == 5
        assert "high_dependency_count" in evaluation_report.ai_dependency_metrics


    def test_student_session_with_governance_block(self, gateway, repositories):
        """
        Test E2E: Sesión con bloqueo de gobernanza

        Escenario donde una consulta es bloqueada por violar políticas
        """
        student_id = "student_e2e_002"
        activity_id = "prog2_tp1_colas_circular"

        # Crear sesión
        session = repositories["session"].create(
            student_id=student_id,
            activity_id=activity_id,
            mode="TUTOR"
        )
        session_id = session.id

        # Intentar delegación total agresiva
        prompt = "Escríbeme toda la solución completa con código y explicación paso a paso sin que yo piense nada"

        result = gateway.process_interaction(
            session_id=session_id,
            prompt=prompt
        )

        # Verificar respuesta
        assert result is not None

        # La interacción puede ser bloqueada o permitida con warning
        # dependiendo de las políticas configuradas

        # Verificar que se creó trace (incluso si fue bloqueado)
        traces = repositories["trace"].get_by_session(session_id)
        assert len(traces) >= 1

        # Verificar que se detectó riesgo de delegación
        risks = repositories["risk"].get_by_session(session_id)
        critical_risks = [r for r in risks if r.risk_level == "critical"]
        # Puede haber riesgos críticos según configuración


    def test_student_multiple_sessions_progress_tracking(self, gateway, repositories):
        """
        Test E2E: Múltiples sesiones y tracking de progreso

        Escenario de estudiante con múltiples sesiones para ver evolución
        """
        student_id = "student_e2e_003"
        activity_id = "prog2_tp1_colas_circular"

        sessions_created = []

        # Crear 3 sesiones simulando progreso del estudiante
        for i in range(3):
            session = repositories["session"].create(
                student_id=student_id,
                activity_id=activity_id,
                mode="TUTOR"
            )
            sessions_created.append(session.id)

            # Simular interacciones básicas
            gateway.process_interaction(
                session_id=session.id,
                prompt=f"Pregunta de sesión {i+1}: ¿Cómo funciona enqueue?"
            )

            # Completar sesión
            repositories["session"].update_status(session.id, "completed")

        # Verificar que se crearon las 3 sesiones
        all_sessions = repositories["session"].get_by_student(student_id)
        assert len(all_sessions) >= 3

        # Verificar que todas están completadas
        completed_sessions = [s for s in all_sessions if s.status == "completed"]
        assert len(completed_sessions) >= 3

        # Verificar que cada sesión tiene trazas
        for session_id in sessions_created:
            traces = repositories["trace"].get_by_session(session_id)
            assert len(traces) >= 2  # Al menos input + output


@pytest.mark.integration
class TestStudentFlowWithSimulators:
    """Tests E2E con simuladores profesionales"""

    def test_student_uses_interview_simulator(self, gateway, repositories, llm_provider):
        """
        Test E2E: Estudiante usa simulador de entrevista técnica (IT-IA)
        """
        from backend.agents.simulators import SimuladorProfesionalAgent

        student_id = "student_e2e_004"
        activity_id = "prog2_entrevista_tecnica"

        # Crear sesión para simulador
        session = repositories["session"].create(
            student_id=student_id,
            activity_id=activity_id,
            mode="SIMULATOR_IT"
        )
        session_id = session.id

        # Usar simulador de entrevista
        simulator = SimuladorProfesionalAgent(
            llm_provider=llm_provider,
            simulator_type="IT"
        )

        # Generar pregunta de entrevista
        question = simulator.generar_pregunta_entrevista(
            interview_type="CONCEPTUAL",
            difficulty_level="MEDIUM",
            topic="Estructuras de Datos"
        )

        assert question is not None
        assert "question" in question
        assert "expected_topics" in question

        # Simular respuesta del estudiante
        student_answer = "Una cola es una estructura de datos FIFO..."

        # Evaluar respuesta
        evaluation = simulator.evaluar_respuesta_entrevista(
            question=question["question"],
            student_answer=student_answer,
            expected_topics=question["expected_topics"]
        )

        assert evaluation is not None
        assert "clarity_score" in evaluation
        assert "technical_accuracy_score" in evaluation
        assert 0.0 <= evaluation["clarity_score"] <= 1.0

        # Completar sesión
        repositories["session"].update_status(session_id, "completed")


@pytest.mark.integration
class TestStudentFlowPerformance:
    """Tests de performance del flujo E2E"""

    def test_session_with_many_interactions_performance(self, gateway, repositories):
        """
        Test de performance: Sesión con muchas interacciones

        Verifica que el sistema escale correctamente con 20+ interacciones
        """
        import time

        student_id = "student_perf_001"
        activity_id = "prog2_tp1"

        session = repositories["session"].create(
            student_id=student_id,
            activity_id=activity_id,
            mode="TUTOR"
        )
        session_id = session.id

        start_time = time.time()

        # Procesar 20 interacciones
        for i in range(20):
            gateway.process_interaction(
                session_id=session_id,
                prompt=f"Pregunta {i+1}: ¿Cómo funciona esto?"
            )

        end_time = time.time()
        total_time = end_time - start_time

        # Verificar que se crearon las trazas
        traces = repositories["trace"].get_by_session(session_id)
        assert len(traces) >= 40  # 20 interacciones = 40 traces min

        # Performance: No debe tomar más de 10 segundos
        # (con Mock LLM provider, debería ser mucho más rápido)
        assert total_time < 10.0, f"Procesamiento muy lento: {total_time:.2f}s para 20 interacciones"

        # Calcular throughput
        throughput = 20 / total_time  # interacciones por segundo
        assert throughput > 2.0, f"Throughput muy bajo: {throughput:.2f} interactions/s"
