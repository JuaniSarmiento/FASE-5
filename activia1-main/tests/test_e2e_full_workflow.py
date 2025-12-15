"""
TEST INTEGRAL END-TO-END - Sistema Completo AI-Native MVP
==========================================================

Prueba el flujo completo del sistema desde cero incluyendo:
1. Creación de sesión
2. Interacción con Tutor IA
3. Prueba de todos los simuladores profesionales
4. Creación de eventos de simulador
5. Análisis automático de riesgos (AR-IA)
6. Generación de evaluación (E-IA-Proc)
7. Trazabilidad completa (TC-N4)

Este test simula la experiencia real de un estudiante usando el sistema completo.

Uso:
    pytest tests/test_e2e_full_workflow.py -v -s
    
    O ejecutar directamente:
    python tests/test_e2e_full_workflow.py
"""
import pytest
import requests
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional, List


# ============================================================================
# CONFIGURACIÓN
# ============================================================================

BASE_URL = "http://localhost:8000/api/v1"
STUDENT_ID = "e2e_test_student_001"
ACTIVITY_ID = "e2e_test_scrum_simulation"

# Timeouts
TIMEOUT_SHORT = 10
TIMEOUT_MEDIUM = 60  # Aumentado para Tutor IA (puede tardar 30-60s)
TIMEOUT_LONG = 120  # Aumentado para evaluaciones (puede tardar 60-120s)


# ============================================================================
# UTILIDADES
# ============================================================================

class Colors:
    """Colores ANSI para output en terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_section(title: str):
    """Imprime separador de sección con estilo"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_success(message: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_info(message: str):
    """Imprime información"""
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")


def print_warning(message: str):
    """Imprime advertencia"""
    print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")


def print_error(message: str):
    """Imprime error"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_data(label: str, data: Any):
    """Imprime datos formateados en JSON"""
    print(f"{Colors.OKBLUE}📊 {label}:{Colors.ENDC}")
    print(json.dumps(data, indent=2, ensure_ascii=False))


def api_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    params: Optional[Dict] = None,
    timeout: int = TIMEOUT_SHORT
) -> requests.Response:
    """
    Realiza petición HTTP con manejo de errores
    """
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=timeout)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=data, timeout=timeout)
        elif method.upper() == "DELETE":
            response = requests.delete(url, timeout=timeout)
        else:
            raise ValueError(f"Método HTTP no soportado: {method}")
        
        return response
        
    except requests.exceptions.Timeout:
        print_error(f"Timeout en petición: {method} {endpoint} (>{timeout}s)")
        raise
    except requests.exceptions.ConnectionError:
        print_error(f"No se pudo conectar al backend en {BASE_URL}")
        print_warning("Asegúrate de que el backend esté ejecutándose:")
        print_warning("  uvicorn backend.api.main:app --reload --port 8000")
        raise
    except Exception as e:
        print_error(f"Error en petición: {str(e)}")
        raise


# ============================================================================
# TEST PRINCIPAL
# ============================================================================

def test_full_e2e_workflow():
    """
    Test End-to-End completo que simula todo el flujo de un estudiante
    """
    
    print_section("🚀 INICIO - TEST END-TO-END COMPLETO")
    print_info(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Backend: {BASE_URL}")
    print_info(f"Student ID: {STUDENT_ID}")
    print_info(f"Activity ID: {ACTIVITY_ID}")
    
    session_id = None
    simulator_sessions = []
    
    try:
        # ====================================================================
        # PASO 1: CREAR SESIÓN PRINCIPAL
        # ====================================================================
        print_section("PASO 1/7: Crear Sesión Principal")
        
        print_info("Creando sesión de aprendizaje...")
        response = api_request(
            "POST",
            "/sessions",
            data={
                "student_id": STUDENT_ID,
                "activity_id": ACTIVITY_ID,
                "mode": "TUTOR"
            }
        )
        
        assert response.status_code == 201, f"Error al crear sesión: {response.text}"
        
        data = response.json()
        session_id = data["data"]["id"]
        
        print_success(f"Sesión creada: {session_id}")
        print_data("Detalles de sesión", {
            "id": session_id,
            "student_id": STUDENT_ID,
            "mode": data["data"]["mode"],
            "status": data["data"]["status"]
        })
        
        # ====================================================================
        # PASO 2: INTERACTUAR CON TUTOR IA
        # ====================================================================
        print_section("PASO 2/7: Interactuar con Tutor IA (T-IA-Cog)")
        
        tutor_questions = [
            {
                "prompt": "¿Cómo implemento una estructura de datos de cola en Python?",
                "expected_keywords": ["queue", "enqueue", "dequeue", "FIFO"]
            },
            {
                "prompt": "Explícame la diferencia entre una lista y una tupla",
                "expected_keywords": ["mutable", "inmutable", "list", "tuple"]
            },
            {
                "prompt": "Necesito ayuda para entender recursión. ¿Puedes explicarme con un ejemplo?",
                "expected_keywords": ["recursión", "caso base", "llamada"]
            }
        ]
        
        traces_ids = []
        
        for i, question in enumerate(tutor_questions, 1):
            print_info(f"\nPregunta {i}/{len(tutor_questions)}:")
            print(f"   {question['prompt']}")
            
            response = api_request(
                "POST",
                "/interactions",
                data={
                    "session_id": session_id,
                    "prompt": question["prompt"],
                    "context": {"question_number": i}
                },
                timeout=TIMEOUT_MEDIUM
            )
            
            assert response.status_code == 200, f"Error en interacción {i}: {response.text}"
            
            interaction_data = response.json()["data"]
            trace_id = interaction_data.get("trace_id")
            ai_response = interaction_data.get("response", "")
            
            if trace_id:
                traces_ids.append(trace_id)
                print_success(f"Traza cognitiva creada: {trace_id}")
            
            # Mostrar preview de respuesta
            if ai_response:
                preview = ai_response[:150] + "..." if len(ai_response) > 150 else ai_response
                print(f"   Respuesta IA: {preview}")
            
            time.sleep(1)  # Pausa entre preguntas
        
        print_success(f"\nCompletadas {len(tutor_questions)} interacciones con el Tutor IA")
        print_info(f"Trazas cognitivas generadas: {len(traces_ids)}")
        
        # ====================================================================
        # PASO 3: PROBAR SIMULADORES PROFESIONALES
        # ====================================================================
        print_section("PASO 3/7: Probar Simuladores Profesionales (S-IA-X)")
        
        simulators = [
            {
                "type": "product_owner",
                "prompt": "Ayúdame a crear un backlog de producto para un sistema de e-commerce. Necesito definir las historias de usuario principales.",
                "description": "Product Owner - Creación de Backlog"
            },
            {
                "type": "scrum_master",
                "prompt": "¿Cómo organizo un sprint planning efectivo para un equipo de 5 desarrolladores con velocity de 30 puntos?",
                "description": "Scrum Master - Sprint Planning"
            },
            {
                "type": "tech_interviewer",
                "prompt": "Explícame qué es el principio de responsabilidad única (SRP) y dame un ejemplo práctico",
                "description": "Tech Interviewer - Principios SOLID"
            },
            {
                "type": "devsecops",
                "prompt": "¿Cómo configuro un pipeline de CI/CD que incluya análisis de seguridad con OWASP?",
                "description": "DevSecOps - CI/CD con Seguridad"
            }
        ]
        
        for sim in simulators:
            print_info(f"\n🎭 Simulador: {sim['description']}")
            
            # Crear sesión específica para el simulador
            sim_response = api_request(
                "POST",
                "/sessions",
                data={
                    "student_id": STUDENT_ID,
                    "activity_id": f"{ACTIVITY_ID}_sim_{sim['type']}",
                    "mode": "SIMULATOR",
                    "simulator_type": sim["type"]
                }
            )
            
            assert sim_response.status_code == 201, f"Error al crear sesión del simulador {sim['type']}"
            sim_session_id = sim_response.json()["data"]["id"]
            simulator_sessions.append(sim_session_id)
            
            print(f"   Sesión simulador: {sim_session_id}")
            print(f"   Prompt: {sim['prompt'][:80]}...")
            
            # Interactuar con el simulador
            interaction_response = api_request(
                "POST",
                "/simulators/interact",
                data={
                    "session_id": sim_session_id,
                    "simulator_type": sim["type"],
                    "prompt": sim["prompt"],
                    "context": {}
                },
                timeout=TIMEOUT_LONG
            )
            
            assert interaction_response.status_code == 200, f"Error en simulador {sim['type']}: {interaction_response.text}"
            
            result = interaction_response.json()["data"]
            response_text = result.get("response", "")
            response_preview = response_text[:150] + "..." if len(response_text) > 150 else response_text
            
            print_success(f"Simulador {sim['type']} respondió correctamente")
            print(f"   Respuesta: {response_preview}")
            
            time.sleep(1)
        
        print_success(f"\n✅ Completados {len(simulators)} simuladores profesionales")
        
        # ====================================================================
        # PASO 4: CREAR EVENTOS DE SIMULADOR
        # ====================================================================
        print_section("PASO 4/7: Crear Eventos de Simulador")
        
        print_info("Creando eventos que simulan acciones del estudiante...")
        
        events = [
            {
                "event_type": "backlog_created",
                "event_data": {
                    "stories_count": 8,
                    "has_acceptance_criteria": False,  # ⚠️ Debería generar RIESGO
                    "priority_defined": True,
                    "stories": [
                        {"id": "US-001", "title": "Login de usuario"},
                        {"id": "US-002", "title": "Registro de usuario"},
                        {"id": "US-003", "title": "Catálogo de productos"},
                        {"id": "US-004", "title": "Carrito de compras"},
                        {"id": "US-005", "title": "Checkout"},
                        {"id": "US-006", "title": "Pago con tarjeta"},
                        {"id": "US-007", "title": "Historial de pedidos"},
                        {"id": "US-008", "title": "Panel de administración"}
                    ]
                },
                "description": "Product Owner creó backlog inicial sin criterios de aceptación",
                "severity": "warning"
            },
            {
                "event_type": "sprint_planning_complete",
                "event_data": {
                    "velocity_estimated": 34,
                    "stories_selected": 5,
                    "team_size": 5,
                    "sprint_duration": 2,
                    "team_confirmed": True,
                    "definition_of_done": True
                },
                "description": "Sprint planning completado con velocity de 34 puntos",
                "severity": "info"
            },
            {
                "event_type": "technical_decision_made",
                "event_data": {
                    "decision": "Usar arquitectura de microservicios",
                    "justification": None,  # ⚠️ Debería generar RIESGO
                    "alternatives_considered": [],
                    "team_agreement": False
                },
                "description": "Decisión técnica de arquitectura sin justificación documentada",
                "severity": "warning"
            },
            {
                "event_type": "user_story_approved",
                "event_data": {
                    "story_id": "US-001",
                    "acceptance_criteria_count": 4,
                    "has_definition_of_done": True,
                    "estimated_points": 5
                },
                "description": "User story US-001 aprobada con criterios completos",
                "severity": "info"
            },
            {
                "event_type": "deployment_completed",
                "event_data": {
                    "environment": "production",
                    "tests_executed": False,  # ⚠️ Debería generar RIESGO CRÍTICO
                    "rollback_plan": True,
                    "version": "v1.0.0"
                },
                "description": "Deployment a producción sin ejecutar tests",
                "severity": "critical"
            },
            {
                "event_type": "security_scan_complete",
                "event_data": {
                    "tool": "OWASP ZAP",
                    "scan_duration_minutes": 15,
                    "vulnerabilities": [  # ⚠️ Debería generar RIESGO CRÍTICO
                        {"severity": "high", "type": "SQL Injection", "cve": "CWE-89"},
                        {"severity": "medium", "type": "XSS", "cve": "CWE-79"}
                    ]
                },
                "description": "Scan de seguridad detectó 2 vulnerabilidades",
                "severity": "critical"
            }
        ]
        
        events_created = []
        
        for event in events:
            response = api_request(
                "POST",
                "/events",
                data={
                    "session_id": session_id,
                    **event
                }
            )
            
            assert response.status_code == 201, f"Error al crear evento {event['event_type']}: {response.text}"
            
            event_data = response.json()["data"]
            events_created.append(event_data["id"])
            
            severity_icon = "🔴" if event["severity"] == "critical" else "🟡" if event["severity"] == "warning" else "🟢"
            print_success(f"{severity_icon} Evento creado: {event['event_type']} ({event['severity']})")
        
        print_success(f"\n✅ Creados {len(events_created)} eventos de simulador")
        
        # ====================================================================
        # PASO 5: ANALIZAR RIESGOS AUTOMÁTICAMENTE
        # ====================================================================
        print_section("PASO 5/7: Analizar Riesgos Automáticamente (AR-IA)")
        
        print_info(f"Ejecutando análisis de riesgos en sesión: {session_id}")
        print_info("El engine AR-IA analizará los eventos y detectará riesgos automáticamente...")
        
        response = api_request(
            "POST",
            f"/risks/analyze-session/{session_id}",
            timeout=TIMEOUT_MEDIUM
        )
        
        assert response.status_code == 200, f"Error al analizar riesgos: {response.text}"
        
        risks_data = response.json()["data"]
        message = response.json()["message"]
        
        print_success(message)
        
        # Analizar riesgos por nivel
        risk_summary = {
            "CRITICAL": [r for r in risks_data if r["risk_level"] == "CRITICAL"],
            "HIGH": [r for r in risks_data if r["risk_level"] == "HIGH"],
            "MEDIUM": [r for r in risks_data if r["risk_level"] == "MEDIUM"],
            "LOW": [r for r in risks_data if r["risk_level"] == "LOW"]
        }
        
        print_data("Resumen de riesgos detectados", {
            "total": len(risks_data),
            "critical": len(risk_summary["CRITICAL"]),
            "high": len(risk_summary["HIGH"]),
            "medium": len(risk_summary["MEDIUM"]),
            "low": len(risk_summary["LOW"])
        })
        
        # Mostrar detalles de riesgos críticos y altos
        critical_and_high = risk_summary["CRITICAL"] + risk_summary["HIGH"]
        
        if critical_and_high:
            print_info(f"\n⚠️  Riesgos CRÍTICOS y ALTOS detectados ({len(critical_and_high)}):")
            for i, risk in enumerate(critical_and_high[:5], 1):  # Mostrar máximo 5
                icon = "🔴" if risk["risk_level"] == "CRITICAL" else "🟠"
                print(f"\n   {icon} Riesgo {i}: [{risk['risk_level']}] {risk['dimension']}")
                print(f"      Descripción: {risk['description'][:80]}...")
                if risk.get("recommendations"):
                    print(f"      Recomendación: {risk['recommendations'][0][:80]}...")
        
        # Verificaciones
        assert len(risks_data) >= 3, f"Se esperaban al menos 3 riesgos, se detectaron {len(risks_data)}"
        assert len(critical_and_high) > 0, "Debería haber al menos un riesgo CRITICAL o HIGH"
        
        print_success(f"\n✅ Análisis de riesgos completado: {len(risks_data)} riesgos detectados")
        
        # ====================================================================
        # PASO 6: GENERAR EVALUACIÓN DE PROCESO
        # ====================================================================
        print_section("PASO 6/7: Generar Evaluación de Proceso (E-IA-Proc)")
        
        print_info(f"Generando evaluación cognitiva para sesión: {session_id}")
        print_warning("Este proceso puede tardar 30-90 segundos debido al procesamiento del LLM...")
        
        start_time = time.time()
        
        response = api_request(
            "POST",
            f"/evaluations/{session_id}/generate",
            timeout=TIMEOUT_LONG
        )
        
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200, f"Error al generar evaluación: {response.text}"
        
        eval_data = response.json()["data"]
        
        print_success(f"Evaluación generada en {elapsed_time:.1f} segundos")
        
        # Mostrar resultados principales
        print_data("Resultados de evaluación", {
            "session_id": eval_data.get("session_id"),
            "overall_score": f"{eval_data.get('overall_score', 0):.2f}/10",
            "autonomy_level": eval_data.get("autonomy_level", "N/A"),
            "metacognition_score": f"{eval_data.get('metacognition_score', 0):.2f}/10",
            "delegation_ratio": f"{eval_data.get('delegation_ratio', 0):.2%}",
            "total_dimensions": len(eval_data.get("dimensions", []))
        })
        
        # Mostrar dimensiones evaluadas
        dimensions = ["planning", "execution", "debugging", "reflection", "autonomy"]
        print_info("\n📊 Dimensiones evaluadas:")
        for dim in dimensions:
            dim_data = eval_data.get(dim)
            if dim_data:
                score = dim_data.get('score', 0)
                level = dim_data.get('level', 'N/A')
                icon = "🟢" if score >= 7 else "🟡" if score >= 5 else "🔴"
                print(f"   {icon} {dim.capitalize():12} → {score:.1f}/10 ({level})")
        
        # Verificaciones
        assert eval_data.get("overall_score", 0) >= 0, "Score debe ser >= 0"
        assert eval_data.get("overall_score", 0) <= 10, "Score debe ser <= 10"
        assert eval_data.get("overall_feedback"), "Debe haber feedback general"
        
        print_success("\n✅ Evaluación de proceso completada correctamente")
        
        # ====================================================================
        # PASO 7: OBTENER TRAZABILIDAD COMPLETA
        # ====================================================================
        print_section("PASO 7/7: Obtener Trazabilidad Completa (TC-N4)")
        
        print_info(f"Generando grafo de trazabilidad para sesión: {session_id}")
        print_info("El motor TC-N4 conecta Eventos → Trazas → Riesgos → Evaluaciones...")
        
        response = api_request(
            "GET",
            f"/traceability/session/{session_id}",
            timeout=TIMEOUT_MEDIUM
        )
        
        assert response.status_code == 200, f"Error al obtener trazabilidad: {response.text}"
        
        trace_data = response.json()["data"]
        summary = trace_data.get("summary", {})
        artifacts = trace_data.get("artifacts", [])
        
        print_success("Grafo de trazabilidad generado correctamente")
        
        print_data("Resumen de trazabilidad", {
            "total_events": summary.get("total_events", 0),
            "total_traces": summary.get("total_traces", 0),
            "total_risks": summary.get("total_risks", 0),
            "total_evaluations": summary.get("total_evaluations", 0),
            "avg_ai_involvement": f"{summary.get('avg_ai_involvement', 0):.2%}",
            "session_duration_minutes": summary.get("session_duration_minutes"),
            "artifacts_root_count": len(artifacts)
        })
        
        # Analizar estructura del grafo por niveles
        level_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        
        def count_artifacts_recursive(artifact_list, depth=0):
            """Cuenta artefactos recursivamente"""
            if depth > 4:
                return
            for artifact in artifact_list:
                level = artifact.get("level", 0)
                level_counts[level] = level_counts.get(level, 0) + 1
                children = artifact.get("children", [])
                if children:
                    count_artifacts_recursive(children, depth + 1)
        
        count_artifacts_recursive(artifacts)
        
        print_info("\n📊 Distribución de artefactos en el grafo (4 niveles):")
        print(f"   Nivel 1 (Eventos de Simulador):  {level_counts[1]} artefactos")
        print(f"   Nivel 2 (Trazas Cognitivas):     {level_counts[2]} artefactos")
        print(f"   Nivel 3 (Riesgos Detectados):    {level_counts[3]} artefactos")
        print(f"   Nivel 4 (Evaluaciones):          {level_counts[4]} artefactos")
        
        # Mostrar resumen de riesgos
        risks_by_level = summary.get("risks_by_level", {})
        if risks_by_level:
            print_info("\n⚠️  Riesgos en el grafo:")
            for level, count in risks_by_level.items():
                if count > 0:
                    icon = "🔴" if level == "CRITICAL" else "🟠" if level == "HIGH" else "🟡" if level == "MEDIUM" else "🟢"
                    print(f"   {icon} {level}: {count}")
        
        # Verificaciones
        assert summary.get("total_events", 0) > 0, "Debería haber eventos en el grafo"
        assert summary.get("total_risks", 0) > 0, "Debería haber riesgos en el grafo"
        assert len(artifacts) > 0, "Debería haber artefactos raíz en el grafo"
        assert level_counts[1] > 0, "Debería haber eventos (Nivel 1)"
        
        print_success("\n✅ Trazabilidad completa verificada correctamente")
        
        # ====================================================================
        # RESUMEN FINAL
        # ====================================================================
        print_section("✅ RESUMEN FINAL - TEST END-TO-END COMPLETADO")
        
        print_success("🎉 Todos los pasos del flujo completados exitosamente!")
        print()
        print(f"{Colors.BOLD}📊 Estadísticas Finales:{Colors.ENDC}")
        print(f"   {Colors.OKGREEN}✅ Sesión principal:{Colors.ENDC} {session_id}")
        print(f"   {Colors.OKGREEN}✅ Interacciones con Tutor IA:{Colors.ENDC} {len(tutor_questions)}")
        print(f"   {Colors.OKGREEN}✅ Simuladores probados:{Colors.ENDC} {len(simulators)}")
        print(f"   {Colors.OKGREEN}✅ Eventos creados:{Colors.ENDC} {len(events_created)}")
        print(f"   {Colors.OKGREEN}✅ Riesgos detectados:{Colors.ENDC} {len(risks_data)}")
        print(f"   {Colors.OKGREEN}✅ Evaluación generada:{Colors.ENDC} Score {eval_data.get('overall_score', 0):.1f}/10")
        print(f"   {Colors.OKGREEN}✅ Trazabilidad completa:{Colors.ENDC} {level_counts[1] + level_counts[2] + level_counts[3] + level_counts[4]} artefactos")
        print()
        print(f"{Colors.OKGREEN}{Colors.BOLD}✅ FLUJO COMPLETO VERIFICADO CORRECTAMENTE{Colors.ENDC}")
        print()
        
    except AssertionError as e:
        print_error(f"Assertion falló: {str(e)}")
        raise
    
    except Exception as e:
        print_error(f"Error durante el test: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    finally:
        # ====================================================================
        # CLEANUP
        # ====================================================================
        print_section("🧹 CLEANUP - Limpiando datos de prueba")
        
        # Eliminar sesión principal
        if session_id:
            try:
                response = api_request("DELETE", f"/sessions/{session_id}")
                if response.status_code == 200:
                    print_success(f"Sesión principal eliminada: {session_id}")
            except:
                print_warning(f"No se pudo eliminar sesión principal: {session_id}")
        
        # Eliminar sesiones de simuladores
        for sim_session_id in simulator_sessions:
            try:
                response = api_request("DELETE", f"/sessions/{sim_session_id}")
                if response.status_code == 200:
                    print_success(f"Sesión de simulador eliminada: {sim_session_id}")
            except:
                print_warning(f"No se pudo eliminar sesión de simulador: {sim_session_id}")
        
        print_success("Cleanup completado")


# ============================================================================
# EJECUCIÓN DIRECTA (sin pytest)
# ============================================================================

if __name__ == "__main__":
    """
    Permite ejecutar el test directamente sin pytest
    """
    print("\n" + "=" * 80)
    print("  TEST END-TO-END COMPLETO - AI-Native MVP")
    print("  Ejecutando sin pytest...")
    print("=" * 80)
    print("\n⚠️  RECOMENDACIÓN: Ejecutar con pytest para mejor output:")
    print("   pytest tests/test_e2e_full_workflow.py -v -s\n")
    
    try:
        test_full_e2e_workflow()
    except KeyboardInterrupt:
        print_warning("\n\nTest interrumpido por el usuario")
    except Exception as e:
        print_error(f"\n\nTest falló: {str(e)}")
        import sys
        sys.exit(1)
