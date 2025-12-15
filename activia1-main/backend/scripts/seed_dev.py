"""
Script de seed para desarrollo - Carga datos de prueba

Genera:
- 1 sesión de simulador Product Owner completada
- 5 eventos del simulador
- 3 trazas cognitivas
- 2 riesgos detectados
- 1 evaluación con feedback

USO:
    python -m backend.scripts.seed_dev

REQUIREMENTS:
    - Backend debe estar corriendo (para API) O
    - Acceso directo a BD (para inserts directos)
"""
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Agregar backend al path
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from backend.core.constants import utc_now

from backend.database.models import (
    SessionDB,
    SimulatorEventDB,
    CognitiveTraceDB,
    RiskDB,
    EvaluationDB,
)
from backend.database import get_session_factory


def seed_development_data():
    """
    Crea datos de desarrollo para testing local
    """
    print("=" * 80)
    print("SEED DEVELOPMENT DATA - AI-Native MVP")
    print("=" * 80)
    
    SessionFactory = get_session_factory()
    db = SessionFactory()
    
    try:
        # Timestamps
        now = utc_now()
        session_start = now - timedelta(hours=2)
        session_end = now - timedelta(hours=1)
        
        # ========================================================================
        # 1. CREAR SESIÓN
        # ========================================================================
        session_id = str(uuid.uuid4())
        session = SessionDB(
            id=session_id,
            student_id="student_001",
            activity_id="scrum_simulation_001",
            mode="SIMULATOR",
            simulator_type="product_owner",
            start_time=session_start,
            end_time=session_end,
            status="completed",
        )
        db.add(session)
        print(f"\n✅ Sesión creada: {session_id}")
        print(f"   - Student: student_001")
        print(f"   - Simulador: Product Owner")
        print(f"   - Estado: completed")
        
        # ========================================================================
        # 2. CREAR EVENTOS DE SIMULADOR
        # ========================================================================
        events = [
            {
                "event_type": "backlog_created",
                "timestamp": session_start + timedelta(minutes=5),
                "event_data": {
                    "stories_count": 5,
                    "has_acceptance_criteria": False,  # ← TRIGGER DE RIESGO
                    "stories": [
                        {"id": "US-001", "title": "Como cliente quiero crear cuenta"},
                        {"id": "US-002", "title": "Como cliente quiero login"},
                        {"id": "US-003", "title": "Como cliente quiero ver productos"},
                        {"id": "US-004", "title": "Como cliente quiero agregar al carrito"},
                        {"id": "US-005", "title": "Como cliente quiero pagar"},
                    ]
                },
                "description": "Product Owner creó backlog inicial con 5 user stories",
                "severity": "info",
            },
            {
                "event_type": "sprint_planning_complete",
                "timestamp": session_start + timedelta(minutes=20),
                "event_data": {
                    "velocity_estimated": 21,
                    "stories_selected": 3,
                    "team_confirmed": True,
                },
                "description": "Sprint planning completado exitosamente",
                "severity": "info",
            },
            {
                "event_type": "user_story_approved",
                "timestamp": session_start + timedelta(minutes=30),
                "event_data": {
                    "story_id": "US-001",
                    "acceptance_criteria_count": 3,
                    "has_definition_of_done": True,
                },
                "description": "User story US-001 aprobada con criterios de aceptación",
                "severity": "info",
            },
            {
                "event_type": "technical_decision_made",
                "timestamp": session_start + timedelta(minutes=45),
                "event_data": {
                    "decision": "Usar PostgreSQL como base de datos principal",
                    "justification": None,  # ← TRIGGER DE RIESGO
                    "alternatives_considered": [],
                },
                "description": "Decisión técnica sobre base de datos",
                "severity": "warning",
            },
            {
                "event_type": "sprint_review_complete",
                "timestamp": session_start + timedelta(minutes=90),
                "event_data": {
                    "stories_completed": 3,
                    "stories_total": 3,
                    "velocity_actual": 21,
                    "stakeholder_feedback": "Positivo",
                },
                "description": "Sprint review completado - 100% de historias completadas",
                "severity": "info",
            },
        ]
        
        event_objects = []
        for evt in events:
            event_obj = SimulatorEventDB(
                id=str(uuid.uuid4()),
                session_id=session_id,
                student_id="student_001",
                simulator_type="product_owner",
                event_type=evt["event_type"],
                event_data=evt["event_data"],
                description=evt["description"],
                severity=evt["severity"],
                timestamp=evt["timestamp"],
            )
            db.add(event_obj)
            event_objects.append(event_obj)
        
        print(f"\n✅ {len(events)} eventos de simulador creados:")
        for evt in events:
            print(f"   - {evt['event_type']} ({evt['severity']})")
        
        # ========================================================================
        # 3. CREAR TRAZAS COGNITIVAS
        # ========================================================================
        traces = [
            {
                "content": "¿Cómo debo priorizar las user stories en el backlog?",
                "timestamp": session_start + timedelta(minutes=10),
                "interaction_type": "question",
                "cognitive_state": "planning",
                "cognitive_intent": "SEEK_GUIDANCE",
                "ai_involvement": 0.3,
                "context": {
                    "ai_response": "Prioriza según valor de negocio y riesgo técnico. Usa MoSCoW o Value/Effort matrix."
                }
            },
            {
                "content": "Voy a ordenar por value/effort. Primero login, luego productos, luego carrito.",
                "timestamp": session_start + timedelta(minutes=15),
                "interaction_type": "reflection",
                "cognitive_state": "executing",
                "cognitive_intent": "SELF_EXPLANATION",
                "ai_involvement": 0.1,
                "context": {}
            },
            {
                "content": "¿Qué pasa si no defino criterios de aceptación claros?",
                "timestamp": session_start + timedelta(minutes=25),
                "interaction_type": "question",
                "cognitive_state": "debugging",
                "cognitive_intent": "UNDERSTAND_ERROR",
                "ai_involvement": 0.4,
                "context": {
                    "ai_response": "Sin criterios claros, el equipo no sabrá cuándo la historia está Done. Alto riesgo de retrabajo."
                }
            },
        ]
        
        trace_objects = []
        for trc in traces:
            trace_obj = CognitiveTraceDB(
                id=str(uuid.uuid4()),
                session_id=session_id,
                student_id="student_001",
                activity_id="scrum_simulation_001",
                trace_level="n4_cognitivo",
                interaction_type=trc["interaction_type"],
                content=trc["content"],
                context=trc["context"],
                cognitive_state=trc["cognitive_state"],
                cognitive_intent=trc["cognitive_intent"],
                ai_involvement=trc["ai_involvement"],
            )
            db.add(trace_obj)
            trace_objects.append(trace_obj)
        
        print(f"\n✅ {len(traces)} trazas cognitivas creadas:")
        for trc in traces:
            print(f"   - {trc['interaction_type']}: {trc['content'][:60]}...")
        
        # ========================================================================
        # 4. CREAR RIESGOS DETECTADOS
        # ========================================================================
        risks = [
            {
                "risk_type": "TECHNICAL_DEBT",
                "risk_level": "HIGH",
                "dimension": "Técnico",
                "title": "User stories sin criterios de aceptación claros",
                "description": "El backlog inicial fue creado sin criterios de aceptación en 4 de 5 historias",
                "impact": "Riesgo de implementación incorrecta, retrabajo y bugs en producción",
                "evidence": [
                    "Backlog creado con 5 historias",
                    "Solo 1 historia tiene criterios de aceptación",
                    "Evento detectado: backlog_created"
                ],
                "recommendations": [
                    "Definir criterios de aceptación SMART para cada user story",
                    "Incluir ejemplos concretos de comportamiento esperado",
                    "Revisar criterios con el equipo antes de comenzar desarrollo"
                ],
                "timestamp": session_start + timedelta(minutes=6),
            },
            {
                "risk_type": "TECHNICAL_DEBT",
                "risk_level": "MEDIUM",
                "dimension": "Técnico",
                "title": "Decisión técnica sin justificación documentada",
                "description": "Se eligió PostgreSQL sin documentar el razonamiento ni las alternativas consideradas",
                "impact": "Dificultad para mantener y evolucionar el sistema a futuro",
                "evidence": [
                    "Decisión: Usar PostgreSQL como base de datos principal",
                    "No hay justificación documentada",
                    "No se consideraron alternativas"
                ],
                "recommendations": [
                    "Documentar el razonamiento detrás de decisiones arquitecturales",
                    "Explicar alternativas consideradas y por qué se descartaron",
                    "Incluir trade-offs y limitaciones conocidas"
                ],
                "timestamp": session_start + timedelta(minutes=46),
            },
        ]
        
        risk_objects = []
        for rsk in risks:
            risk_obj = RiskDB(
                id=str(uuid.uuid4()),
                session_id=session_id,
                student_id="student_001",
                activity_id="scrum_simulation_001",
                risk_type=rsk["risk_type"],
                risk_level=rsk["risk_level"],
                dimension=rsk["dimension"],
                description=rsk["description"],
                impact=rsk["impact"],
                evidence=rsk["evidence"],
                recommendations=rsk["recommendations"],
                detected_by="AR-IA-AUTO",
                resolved=False,
            )
            db.add(risk_obj)
            risk_objects.append(risk_obj)
        
        print(f"\n✅ {len(risks)} riesgos detectados:")
        for rsk in risks:
            print(f"   - {rsk['risk_level']}: {rsk['title'][:60]}...")
        
        # ========================================================================
        # 5. CREAR EVALUACIÓN CON FEEDBACK IA
        # ========================================================================
        evaluation = EvaluationDB(
            id=str(uuid.uuid4()),
            session_id=session_id,
            student_id="student_001",
            activity_id="scrum_simulation_001",
            overall_competency_level="competent",
            overall_score=7.2,
            dimensions=[
                {
                    "dimension": "planning",
                    "score": 8.0,
                    "level": "proficient",
                    "evidence": ["Priorizó correctamente usando value/effort", "Planificó sprint con velocity realista"],
                    "recommendations": ["Mejorar estimación de historias complejas"]
                },
                {
                    "dimension": "execution",
                    "score": 7.5,
                    "level": "competent",
                    "evidence": ["Completó 100% de las historias del sprint", "Aplicó Definition of Done"],
                    "recommendations": ["Agregar más tests automatizados"]
                },
                {
                    "dimension": "risk_awareness",
                    "score": 6.0,
                    "level": "competent",
                    "evidence": ["Identificó riesgo de criterios de aceptación"],
                    "recommendations": ["Detectar riesgos más temprano", "Documentar decisiones técnicas"]
                },
                {
                    "dimension": "communication",
                    "score": 7.5,
                    "level": "competent",
                    "evidence": ["Sprint review con feedback positivo", "Comunicó bien con stakeholders"],
                    "recommendations": ["Mejorar documentación técnica"]
                },
                {
                    "dimension": "autonomy",
                    "score": 7.0,
                    "level": "competent",
                    "evidence": ["Tomó decisiones independientes", "AI involvement promedio: 27%"],
                    "recommendations": ["Incrementar confianza en decisiones arquitecturales"]
                }
            ],
            key_strengths=[
                "Excelente priorización de backlog usando técnicas value/effort",
                "100% de historias completadas en el sprint",
                "Buena comunicación con stakeholders en sprint review"
            ],
            improvement_areas=[
                "Definir criterios de aceptación desde el inicio",
                "Documentar justificación de decisiones técnicas",
                "Detectar riesgos más temprano en el proceso"
            ],
            recommendations=[
                "Practicar técnicas de Definition of Done antes de comenzar desarrollo",
                "Usar ADR (Architecture Decision Records) para decisiones técnicas",
                "Implementar checklist de riesgos en planning"
            ],
            ai_dependency_score=0.27,
            ai_dependency_metrics={
                "total_interactions": 3,
                "ai_assisted_decisions": 1,
                "autonomous_decisions": 4,
                "delegation_ratio": 0.20
            }
        )
        db.add(evaluation)
        
        print(f"\n✅ Evaluación creada:")
        print(f"   - Score overall: {evaluation.overall_score}/10")
        print(f"   - Nivel: {evaluation.overall_competency_level}")
        print(f"   - AI dependency: {evaluation.ai_dependency_score * 100:.0f}%")
        print(f"   - Dimensiones evaluadas: {len(evaluation.dimensions)}")
        
        # ========================================================================
        # COMMIT
        # ========================================================================
        db.commit()
        
        print("\n" + "=" * 80)
        print("✅ SEED COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        print(f"\n📊 RESUMEN:")
        print(f"   - Sesiones: 1")
        print(f"   - Eventos: {len(events)}")
        print(f"   - Trazas cognitivas: {len(traces)}")
        print(f"   - Riesgos: {len(risks)}")
        print(f"   - Evaluaciones: 1")
        print(f"\n🎯 TESTING:")
        print(f"   - Session ID: {session_id}")
        print(f"   - GET /api/v1/sessions?student_id=student_001")
        print(f"   - GET /api/v1/events?session_id={session_id}")
        print(f"   - GET /api/v1/risks?session_id={session_id}")
        print(f"   - GET /api/v1/traceability/session/{session_id}")
        print(f"   - POST /api/v1/evaluations/{session_id}/generate")
        print()
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_development_data()
