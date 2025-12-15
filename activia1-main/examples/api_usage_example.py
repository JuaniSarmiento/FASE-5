"""
Ejemplo completo de uso de la API REST AI-Native

Este script demuestra cómo interactuar con la API usando requests.

PREREQUISITOS:
    1. Instalar requests: pip install requests
    2. Ejecutar el servidor API: python scripts/run_api.py
    3. El servidor debe estar corriendo en http://localhost:8000
"""
import sys
import io
import requests
import json
from datetime import datetime

# Fix para encoding en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuración de la API
API_BASE_URL = "http://localhost:8000/api/v1"


def print_section(title: str):
    """Imprime una sección con formato"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_response(response: requests.Response, title: str = "Response"):
    """Imprime una respuesta HTTP con formato"""
    print(f"\n{title}:")
    print(f"  Status: {response.status_code}")
    try:
        data = response.json()
        print(f"  Body: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"  Body: {response.text}")


def main():
    """Flujo completo de uso de la API"""

    print("=" * 80)
    print("  AI-Native MVP - API Usage Example")
    print("=" * 80)

    # 1. Health Check
    print_section("1. Health Check")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print_response(response, "Health Status")

        if response.status_code == 200:
            health_data = response.json()
            print(f"\n  ✅ Service Status: {health_data['status']}")
            print(f"  ✅ Database: {health_data['database']}")
        else:
            print("\n  ❌ Service is not healthy!")
            return
    except requests.exceptions.ConnectionError:
        print("\n  ❌ ERROR: Cannot connect to API server!")
        print("  Please start the server with: python scripts/run_api.py")
        return

    # 2. Crear sesión
    print_section("2. Create Learning Session")
    session_data = {
        "student_id": "student_api_001",
        "activity_id": "prog2_tp1_colas_api",
        "mode": "TUTOR"
    }

    response = requests.post(
        f"{API_BASE_URL}/sessions",
        json=session_data
    )
    print_response(response, "Create Session")

    if response.status_code != 201:
        print("\n  ❌ Failed to create session!")
        return

    session = response.json()["data"]
    session_id = session["id"]
    print(f"\n  ✅ Session created: {session_id}")

    # 3. Procesar interacción 1 - Pregunta conceptual
    print_section("3. Process Interaction 1 - Conceptual Question")
    interaction_1 = {
        "session_id": session_id,
        "prompt": "¿Qué es una cola circular y cuándo debería usarla?",
        "cognitive_intent": "UNDERSTANDING"
    }

    response = requests.post(
        f"{API_BASE_URL}/interactions",
        json=interaction_1
    )
    print_response(response, "Interaction 1")

    if response.status_code == 200:
        interaction_result = response.json()["data"]
        print(f"\n  ✅ Agent used: {interaction_result['agent_used']}")
        print(f"  ✅ Cognitive state: {interaction_result['cognitive_state_detected']}")
        print(f"  ✅ AI involvement: {interaction_result['ai_involvement']}")
        print(f"\n  Response preview: {interaction_result['response'][:200]}...")

    # 4. Procesar interacción 2 - Solicitud de código (debería generar warning)
    print_section("4. Process Interaction 2 - Code Request (May Trigger Risk)")
    interaction_2 = {
        "session_id": session_id,
        "prompt": "Dame el código completo de una cola circular en Python",
        "cognitive_intent": "IMPLEMENTATION"
    }

    response = requests.post(
        f"{API_BASE_URL}/interactions",
        json=interaction_2
    )
    print_response(response, "Interaction 2")

    if response.status_code == 200:
        interaction_result = response.json()["data"]
        print(f"\n  Agent used: {interaction_result['agent_used']}")
        print(f"  Blocked: {interaction_result['blocked']}")
        if interaction_result['blocked']:
            print(f"  ⚠️  Block reason: {interaction_result['block_reason']}")

    # 5. Consultar historial de interacciones
    print_section("5. Get Interaction History")
    response = requests.get(
        f"{API_BASE_URL}/interactions/{session_id}/history"
    )
    print_response(response, "Interaction History")

    if response.status_code == 200:
        history = response.json()["data"]
        print(f"\n  ✅ Total interactions: {history['total_interactions']}")
        print(f"  ✅ Avg AI involvement: {history['avg_ai_involvement']:.2f}")
        print(f"  ✅ Blocked count: {history['blocked_count']}")

    # 6. Consultar trazas N4
    print_section("6. Get Cognitive Traces")
    response = requests.get(
        f"{API_BASE_URL}/traces/{session_id}",
        params={"trace_level": "N4_COGNITIVO"}
    )
    print_response(response, "N4 Traces")

    if response.status_code == 200:
        traces_data = response.json()
        print(f"\n  ✅ N4 traces found: {traces_data['pagination']['total_items']}")

    # 7. Obtener camino cognitivo
    print_section("7. Get Cognitive Path")
    response = requests.get(
        f"{API_BASE_URL}/traces/{session_id}/cognitive-path"
    )
    print_response(response, "Cognitive Path")

    if response.status_code == 200:
        path = response.json()["data"]
        print(f"\n  ✅ Total traces: {path['total_traces']}")
        print(f"  ✅ N4 traces: {path['n4_traces_count']}")
        print(f"  ✅ State transitions: {len(path['transitions'])}")
        print(f"  ✅ Strategy changes: {len(path['strategy_changes'])}")

    # 8. Consultar riesgos detectados
    print_section("8. Get Detected Risks")
    response = requests.get(
        f"{API_BASE_URL}/risks/session/{session_id}"
    )
    print_response(response, "Session Risks")

    if response.status_code == 200:
        risks = response.json()["data"]
        print(f"\n  ✅ Risks detected: {len(risks)}")
        for risk in risks:
            print(f"\n  Risk: {risk['risk_type']}")
            print(f"    Level: {risk['risk_level']}")
            print(f"    Dimension: {risk['dimension']}")
            print(f"    Description: {risk['description']}")

    # 9. Finalizar sesión
    print_section("9. Update Session Status")
    update_data = {
        "status": "completed"  # Lowercase según el enum SessionStatus
    }

    response = requests.patch(
        f"{API_BASE_URL}/sessions/{session_id}",
        json=update_data
    )
    print_response(response, "Update Session")

    if response.status_code == 200:
        print(f"\n  ✅ Session status updated to: COMPLETED")

    # 10. Obtener detalles completos de la sesión
    print_section("10. Get Session Details")
    response = requests.get(
        f"{API_BASE_URL}/sessions/{session_id}"
    )
    print_response(response, "Session Details")

    if response.status_code == 200:
        session_details = response.json()["data"]
        print(f"\n  ✅ Session Summary:")
        print(f"    Student: {session_details['student_id']}")
        print(f"    Activity: {session_details['activity_id']}")
        print(f"    Status: {session_details['status']}")
        print(f"    Traces: {session_details['trace_count']}")
        print(f"    Risks: {session_details['risk_count']}")
        print(f"    AI Dependency Score: {session_details.get('ai_dependency_score', 'N/A')}")

    print("\n" + "=" * 80)
    print("  ✅ Example completed successfully!")
    print("=" * 80)
    print("\n  Next steps:")
    print("    1. Explore Swagger UI: http://localhost:8000/docs")
    print("    2. Try ReDoc documentation: http://localhost:8000/redoc")
    print("    3. Test other endpoints (evaluations, student profiles, etc.)")
    print("=" * 80)


if __name__ == "__main__":
    main()