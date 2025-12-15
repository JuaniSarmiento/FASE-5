"""
Demostración completa del Sprint 3: Docente y Gobernanza

Este script demuestra todas las funcionalidades implementadas en el Sprint 3:
- HU-EST-006: Camino cognitivo reconstructivo
- HU-EST-009: Simulador PO-IA (Product Owner)
- HU-DOC-002: Visualización de trazas (mejoras)
- HU-DOC-003: Comparación de estudiantes
- HU-DOC-004: Alertas en tiempo real
- HU-SYS-006: Simuladores profesionales (S-IA-X)
- HU-ADM-004: Configuración de proveedores LLM

Autor: Alberto Cortez
Fecha: 2025-11-20
"""
import sys
import io
import requests
import json
from typing import Dict, Any

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuración
API_BASE = "http://localhost:8000/api/v1"


def print_section(title: str):
    """Imprime un título de sección"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_json(data: Any):
    """Imprime JSON formateado"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def demo_simuladores():
    """Demuestra los simuladores profesionales (HU-EST-009, HU-SYS-006)"""
    print_section("DEMO 1: Simuladores Profesionales (S-IA-X)")

    # Listar simuladores disponibles
    print("📋 Listando simuladores disponibles...")
    response = requests.get(f"{API_BASE}/simulators")
    simulators = response.json()["data"]

    print(f"\n✅ {len(simulators)} simuladores encontrados:\n")
    for sim in simulators:
        status_icon = "✅" if sim["status"] == "active" else "🚧"
        print(f"{status_icon} {sim['name']}")
        print(f"   Descripción: {sim['description']}")
        print(f"   Competencias: {', '.join(sim['competencies'])}")
        print()

    # Crear sesión para interactuar con PO-IA
    print("\n📝 Creando sesión para interacción con Product Owner...")
    session_response = requests.post(
        f"{API_BASE}/sessions",
        json={
            "student_id": "student_sprint3_001",
            "activity_id": "sprint3_demo_simuladores",
            "mode": "SIMULATOR"
        }
    )
    session_id = session_response.json()["data"]["id"]
    print(f"✅ Sesión creada: {session_id}")

    # Interactuar con PO-IA
    print("\n💬 Interactuando con Product Owner (PO-IA)...")
    print("Prompt: 'Propongo usar una cola circular para el buffer de eventos...'")

    interaction_response = requests.post(
        f"{API_BASE}/simulators/interact",
        json={
            "session_id": session_id,
            "simulator_type": "product_owner",
            "prompt": "Propongo usar una cola circular para el buffer de eventos. Los criterios de aceptación son: O(1) para enqueue/dequeue, capacidad fija de 100 eventos, y manejo de overflow con política FIFO.",
            "context": {"iteration": 1}
        }
    )

    interaction_data = interaction_response.json()["data"]
    print(f"\n🤖 Respuesta del PO-IA:\n")
    print(interaction_data["response"])
    print(f"\n📊 Competencias evaluadas: {', '.join(interaction_data['competencies_evaluated'])}")
    print(f"🔍 Espera en próxima respuesta: {', '.join(interaction_data['expects'])}")

    return session_id


def demo_camino_cognitivo(session_id: str):
    """Demuestra el camino cognitivo reconstructivo (HU-EST-006)"""
    print_section("DEMO 2: Camino Cognitivo Reconstructivo (HU-EST-006)")

    print(f"🔍 Obteniendo camino cognitivo de sesión: {session_id}")

    response = requests.get(f"{API_BASE}/cognitive-path/{session_id}")
    cognitive_path = response.json()["data"]

    print("\n📊 RESUMEN DEL CAMINO COGNITIVO:")
    print(f"   Total de interacciones: {cognitive_path['summary']['total_interactions']}")
    print(f"   Duración: {cognitive_path['summary']['total_duration_minutes']} minutos")
    print(f"   Dependencia promedio de IA: {cognitive_path['summary']['ai_dependency_average']*100:.1f}%")
    print(f"   Interacciones bloqueadas: {cognitive_path['summary']['blocked_interactions']}")
    print(f"   Cambios de estrategia: {cognitive_path['summary']['strategy_changes']}")
    print(f"   Riesgos detectados: {cognitive_path['summary']['risks_total']}")

    print("\n🎯 FASES COGNITIVAS ATRAVESADAS:")
    for phase in cognitive_path["phases"]:
        print(f"\n  Fase: {phase['phase_name']}")
        print(f"    Duración: {phase['duration_minutes']} minutos")
        print(f"    Interacciones: {phase['interactions_count']}")
        print(f"    AI Involvement: {phase['ai_involvement_avg']*100:.0f}%")
        if phase['risks_detected']:
            print(f"    ⚠️ Riesgos: {', '.join(phase['risks_detected'])}")

    print("\n🔄 TRANSICIONES:")
    for transition in cognitive_path["transitions"]:
        print(f"  {transition['from_phase']} → {transition['to_phase']}")
        print(f"    Disparador: {transition['trigger']}")


def demo_comparacion_estudiantes():
    """Demuestra la comparación de estudiantes (HU-DOC-003)"""
    print_section("DEMO 3: Comparación de Estudiantes (HU-DOC-003)")

    # Crear múltiples sesiones para comparar
    print("📝 Creando sesiones de múltiples estudiantes...")

    students = ["student_A", "student_B", "student_C"]
    activity_id = "sprint3_demo_comparacion"

    for student_id in students:
        session_response = requests.post(
            f"{API_BASE}/sessions",
            json={
                "student_id": student_id,
                "activity_id": activity_id,
                "mode": "TUTOR"
            }
        )
        print(f"✅ Sesión creada para {student_id}")

        # Simular algunas interacciones
        for i in range(2):
            requests.post(
                f"{API_BASE}/interactions",
                json={
                    "session_id": session_response.json()["data"]["id"],
                    "prompt": f"Consulta {i+1}: ¿Cómo implemento una estructura de datos eficiente?",
                    "cognitive_intent": "UNDERSTANDING" if i == 0 else "PLANNING"
                }
            )

    # Comparar estudiantes
    print(f"\n🔍 Comparando estudiantes en actividad: {activity_id}")
    response = requests.get(
        f"{API_BASE}/teacher/students/compare",
        params={"activity_id": activity_id}
    )

    comparison = response.json()["data"]

    print("\n📊 ESTADÍSTICAS AGREGADAS:")
    stats = comparison["aggregate_statistics"]
    print(f"   Duración promedio: {stats['average_duration_minutes']:.1f} minutos")
    print(f"   Interacciones promedio: {stats['average_interactions']:.1f}")
    print(f"   Dependencia de IA promedio: {stats['average_ai_dependency']*100:.1f}%")

    print("\n👥 DETALLE POR ESTUDIANTE:")
    for student in comparison["students"][:3]:  # Primeros 3
        print(f"\n  {student['student_id']}:")
        print(f"    Interacciones: {student['total_interactions']}")
        print(f"    Duración: {student['duration_minutes']:.1f} min")
        print(f"    Dependencia IA: {student['ai_dependency_average']*100:.0f}%")
        print(f"    Estados visitados: {', '.join(student['cognitive_states_visited'])}")


def demo_alertas_tiempo_real():
    """Demuestra el sistema de alertas en tiempo real (HU-DOC-004)"""
    print_section("DEMO 4: Alertas en Tiempo Real (HU-DOC-004)")

    print("🚨 Obteniendo alertas activas para el docente...")
    response = requests.get(f"{API_BASE}/teacher/alerts")
    alerts_data = response.json()["data"]

    print(f"\n📊 RESUMEN DE ALERTAS:")
    print(f"   Total de alertas: {alerts_data['total_alerts']}")
    print(f"   Críticas: {alerts_data['by_severity']['critical']}")
    print(f"   Altas: {alerts_data['by_severity']['high']}")
    print(f"   Medias: {alerts_data['by_severity']['medium']}")

    if alerts_data['alerts']:
        print("\n🚨 ALERTAS ACTIVAS:")
        for alert in alerts_data['alerts'][:3]:  # Primeras 3
            severity_icon = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡"
            }[alert['severity']]

            print(f"\n  {severity_icon} Alerta {alert['alert_id']}")
            print(f"     Estudiante: {alert['student_id']}")
            print(f"     Severidad: {alert['severity'].upper()}")
            print(f"     Razones:")
            for reason in alert['reasons']:
                print(f"       - {reason}")
            print(f"     Sugerencias:")
            for suggestion in alert['suggestions']:
                print(f"       • {suggestion}")
    else:
        print("\n✅ No hay alertas activas en este momento")


def demo_configuracion_llm():
    """Demuestra la configuración de proveedores LLM (HU-ADM-004)"""
    print_section("DEMO 5: Configuración de Proveedores LLM (HU-ADM-004)")

    print("⚙️ Listando proveedores LLM configurados...")
    response = requests.get(f"{API_BASE}/admin/llm/providers")
    providers = response.json()["data"]

    print("\n📋 PROVEEDORES DISPONIBLES:\n")
    for provider in providers:
        enabled_icon = "✅" if provider["enabled"] else "❌"
        api_key_icon = "🔑" if provider["api_key_configured"] else "🚫"

        print(f"{enabled_icon} {provider['provider'].upper()}")
        print(f"   API Key: {api_key_icon}")
        print(f"   Modelo: {provider['model']}")
        print(f"   Costo por 1K tokens: ${provider['cost_per_1k_tokens']}")
        print(f"   Privacy compliant: {'✅' if provider['privacy_compliant'] else '❌'}")
        print(f"   Límites: {provider['limits']}")
        print()

    # Obtener estadísticas de uso
    print("\n📊 Estadísticas de uso de LLM:")
    response = requests.get(f"{API_BASE}/admin/llm/usage/stats")
    stats = response.json()["data"]

    print(f"\n   Mes actual: {stats['current_month']}")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Total tokens: {stats['total_tokens']:,}")
    print(f"   Costo estimado: ${stats['estimated_cost_usd']:.2f}")

    print("\n   Distribución por proveedor:")
    for provider_name, provider_stats in stats["by_provider"].items():
        if provider_stats["requests"] > 0:
            print(f"      {provider_name}: {provider_stats['requests']} requests ({provider_stats['percentage']:.1f}%)")


def main():
    """Función principal de demostración"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "     SPRINT 3: DOCENTE Y GOBERNANZA - DEMOSTRACIÓN COMPLETA".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + f"     {'7 Historias de Usuario | 79 Story Points'.center(78)}" + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        # Verificar que el servidor esté corriendo
        print("\n🔍 Verificando conexión con el servidor...")
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor disponible\n")
        else:
            print("❌ Error al conectar con el servidor")
            return

        # Ejecutar demos
        session_id = demo_simuladores()
        demo_camino_cognitivo(session_id)
        demo_comparacion_estudiantes()
        demo_alertas_tiempo_real()
        demo_configuracion_llm()

        # Resumen final
        print_section("✅ SPRINT 3 COMPLETADO")

        print("📦 FUNCIONALIDADES IMPLEMENTADAS:\n")
        print("✅ HU-EST-006: Camino cognitivo reconstructivo")
        print("✅ HU-EST-009: Simulador PO-IA (Product Owner)")
        print("✅ HU-DOC-002: Visualización de trazas mejorada")
        print("✅ HU-DOC-003: Comparación de estudiantes")
        print("✅ HU-DOC-004: Alertas en tiempo real")
        print("✅ HU-SYS-006: Simuladores profesionales (S-IA-X)")
        print("✅ HU-ADM-004: Configuración de proveedores LLM")

        print("\n🎯 ENDPOINTS NUEVOS:\n")
        print("  • GET  /api/v1/simulators")
        print("  • POST /api/v1/simulators/interact")
        print("  • GET  /api/v1/cognitive-path/{session_id}")
        print("  • GET  /api/v1/teacher/students/compare")
        print("  • GET  /api/v1/teacher/alerts")
        print("  • GET  /api/v1/admin/llm/providers")
        print("  • GET  /api/v1/admin/llm/usage/stats")

        print("\n📊 MÉTRICAS DEL SPRINT 3:")
        print("  • Story Points: 79")
        print("  • Historias completadas: 7/7")
        print("  • Endpoints nuevos: 7")
        print("  • Routers nuevos: 4")
        print("  • Schemas Pydantic nuevos: 15+")

        print("\n🚀 PRÓXIMOS PASOS (Sprints 4-6):")
        print("  • Completar simuladores restantes (SM-IA, IT-IA, IR-IA, CX-IA, DSO-IA)")
        print("  • Integración Git (trazabilidad N2)")
        print("  • Dashboard web con visualizaciones avanzadas")
        print("  • Reportes institucionales para acreditación")
        print("  • Integración LTI con Moodle")

        print("\n" + "=" * 80)
        print("✅ Demostración completada exitosamente")
        print("=" * 80 + "\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se puede conectar al servidor API")
        print("   Asegúrate de que el servidor esté corriendo:")
        print("   python scripts/run_api.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR durante la demostración: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()