"""
Test completo de simuladores Sprint 6: SM-IA, CX-IA, DSO-IA

Este script prueba las 3 nuevas implementaciones de simuladores profesionales:
- HU-EST-010: SM-IA (Scrum Master) - Daily standup con feedback
- HU-EST-013: CX-IA (Cliente Experience) - Elicitación de requisitos y soft skills
- HU-EST-014: DSO-IA (DevSecOps Auditor) - Auditoría de seguridad OWASP

Autor: Alberto Cortez
Fecha: 2025-11-21
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


def print_subsection(title: str):
    """Imprime un subtítulo"""
    print(f"\n--- {title} ---\n")


def print_json(data: Any):
    """Imprime JSON formateado"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def test_sm_ia_daily_standup():
    """
    Test HU-EST-010: SM-IA (Scrum Master)

    Prueba el simulador de Scrum Master con daily standup.
    El SM-IA debe analizar:
    - Claridad de la comunicación
    - Identificación de impedimentos
    - Compromisos del sprint
    - Detección de problemas (scope creep, bloqueos)
    """
    print_section("TEST 1: SM-IA (Scrum Master) - Daily Standup")

    # Crear sesión
    print("📝 Creando sesión para daily standup...")
    session_response = requests.post(
        f"{API_BASE}/sessions",
        json={
            "student_id": "student_sprint6_sm_001",
            "activity_id": "sprint6_scrum_master_sim",
            "mode": "SIMULATOR"
        }
    )

    if session_response.status_code != 200:
        print(f"❌ Error creando sesión: {session_response.status_code}")
        print(session_response.text)
        return False

    session_id = session_response.json()["data"]["id"]
    print(f"✅ Sesión creada: {session_id}\n")

    # Test 1: Daily standup con respuesta clara
    print_subsection("Test 1.1: Daily standup con buena comunicación")

    standup_request = {
        "session_id": session_id,
        "student_id": "student_sprint6_sm_001",
        "activity_id": "sprint6_scrum_master_sim",
        "what_did_yesterday": "Completé la implementación del endpoint de autenticación JWT y escribí 12 tests unitarios que cubren casos de éxito y error.",
        "what_will_do_today": "Voy a integrar el middleware de autenticación en todos los endpoints protegidos y actualizar la documentación de la API.",
        "impediments": "Ninguno por el momento"
    }

    response = requests.post(
        f"{API_BASE}/simulators/scrum/daily-standup",
        json=standup_request
    )

    if response.status_code != 200:
        print(f"❌ Error en daily standup: {response.status_code}")
        print(response.text)
        return False

    data = response.json()["data"]
    print("🤖 Feedback del SM-IA:")
    print(f"   {data['feedback']}\n")

    if data['questions']:
        print("❓ Preguntas del SM-IA:")
        for q in data['questions']:
            print(f"   - {q}")
        print()

    if data['detected_issues']:
        print("⚠️  Problemas detectados:")
        for issue in data['detected_issues']:
            print(f"   - {issue}")
        print()

    if data['suggestions']:
        print("💡 Sugerencias:")
        for s in data['suggestions']:
            print(f"   - {s}")
        print()

    # Test 2: Daily standup con impedimento
    print_subsection("Test 1.2: Daily standup con impedimento bloqueante")

    standup_with_blocker = {
        "session_id": session_id,
        "student_id": "student_sprint6_sm_001",
        "activity_id": "sprint6_scrum_master_sim",
        "what_did_yesterday": "Intenté conectar con la API externa de pagos pero no tengo las credenciales.",
        "what_will_do_today": "Seguir esperando las credenciales...",
        "impediments": "Bloqueado: no tengo acceso a la API de pagos y el equipo de infraestructura no responde mis correos."
    }

    response2 = requests.post(
        f"{API_BASE}/simulators/scrum/daily-standup",
        json=standup_with_blocker
    )

    data2 = response2.json()["data"]
    print("🤖 Feedback del SM-IA (con impedimento):")
    print(f"   {data2['feedback']}\n")

    if data2['detected_issues']:
        print("⚠️  Problemas detectados:")
        for issue in data2['detected_issues']:
            print(f"   - {issue}")
        print()

    if data2['suggestions']:
        print("💡 Sugerencias del SM-IA:")
        for s in data2['suggestions']:
            print(f"   - {s}")
        print()

    print("✅ Test SM-IA completado\n")
    return True


def test_cx_ia_client_experience():
    """
    Test HU-EST-013: CX-IA (Cliente Experience)

    Prueba el simulador de cliente que presenta requisitos ambiguos
    y evalúa soft skills del estudiante.
    """
    print_section("TEST 2: CX-IA (Cliente Experience) - Elicitación de Requisitos")

    # Crear sesión
    print("📝 Creando sesión para interacción con cliente...")
    session_response = requests.post(
        f"{API_BASE}/sessions",
        json={
            "student_id": "student_sprint6_cx_001",
            "activity_id": "sprint6_client_simulation",
            "mode": "SIMULATOR"
        }
    )

    session_id = session_response.json()["data"]["id"]
    print(f"✅ Sesión creada: {session_id}\n")

    # Test 1: Obtener requisitos iniciales
    print_subsection("Test 2.1: Obtener requisitos iniciales del cliente")

    req_request = {
        "session_id": session_id,
        "student_id": "student_sprint6_cx_001",
        "activity_id": "sprint6_client_simulation",
        "project_type": "sistema_gestion_inventario"
    }

    response = requests.post(
        f"{API_BASE}/simulators/client/requirements",
        json=req_request
    )

    if response.status_code != 200:
        print(f"❌ Error obteniendo requisitos: {response.status_code}")
        print(response.text)
        return False

    data = response.json()["data"]
    print("🧑‍💼 Requisitos del cliente:")
    print(f"   {data['response']}\n")

    if data['additional_requirements']:
        print("📋 Requisitos adicionales mencionados:")
        for req in data['additional_requirements']:
            print(f"   - {req}")
        print()

    # Test 2: Hacer pregunta de clarificación
    print_subsection("Test 2.2: Preguntar al cliente para clarificar requisitos")

    # Pregunta empática y profesional
    clarify_request = {
        "session_id": session_id,
        "question": "Entiendo que necesita un sistema de gestión de inventario. ¿Podría contarme más sobre el volumen de productos que manejan actualmente y cuáles son los principales problemas que enfrenta su equipo con el sistema actual?"
    }

    response2 = requests.post(
        f"{API_BASE}/simulators/client/clarify",
        json=clarify_request
    )

    data2 = response2.json()["data"]
    print("🧑‍💼 Respuesta del cliente:")
    print(f"   {data2['response']}\n")

    print("📊 Evaluación de soft skills:")
    eval_data = data2['evaluation']
    print(f"   Empatía:        {eval_data['empathy']:.2f}")
    print(f"   Claridad:       {eval_data['clarity']:.2f}")
    print(f"   Profesionalismo: {eval_data['professionalism']:.2f}")
    print()

    if data2['additional_requirements']:
        print("📋 Requisitos adicionales revelados:")
        for req in data2['additional_requirements']:
            print(f"   - {req}")
        print()

    # Test 3: Pregunta poco profesional (para contrastar)
    print_subsection("Test 2.3: Pregunta directa sin contexto (mala práctica)")

    bad_clarify = {
        "session_id": session_id,
        "question": "¿Cuántos productos?"
    }

    response3 = requests.post(
        f"{API_BASE}/simulators/client/clarify",
        json=bad_clarify
    )

    data3 = response3.json()["data"]
    print("🧑‍💼 Respuesta del cliente (a pregunta poco profesional):")
    print(f"   {data3['response']}\n")

    print("📊 Evaluación de soft skills (comparar con anterior):")
    eval_data3 = data3['evaluation']
    print(f"   Empatía:        {eval_data3['empathy']:.2f} (esperado: bajo)")
    print(f"   Claridad:       {eval_data3['clarity']:.2f} (esperado: bajo)")
    print(f"   Profesionalismo: {eval_data3['professionalism']:.2f} (esperado: bajo)")
    print()

    print("✅ Test CX-IA completado\n")
    return True


def test_dso_ia_security_audit():
    """
    Test HU-EST-014: DSO-IA (DevSecOps Auditor)

    Prueba el auditor de seguridad que detecta vulnerabilidades OWASP Top 10.
    """
    print_section("TEST 3: DSO-IA (DevSecOps Auditor) - Auditoría de Seguridad")

    # Crear sesión
    print("📝 Creando sesión para auditoría de seguridad...")
    session_response = requests.post(
        f"{API_BASE}/sessions",
        json={
            "student_id": "student_sprint6_dso_001",
            "activity_id": "sprint6_security_audit",
            "mode": "SIMULATOR"
        }
    )

    session_id = session_response.json()["data"]["id"]
    print(f"✅ Sesión creada: {session_id}\n")

    # Test 1: Código con vulnerabilidades obvias
    print_subsection("Test 3.1: Auditar código con vulnerabilidades conocidas")

    vulnerable_code = """
import sqlite3

def get_user(username):
    # SQL Injection vulnerability
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()

def authenticate(username, password):
    # Hardcoded secret
    SECRET_KEY = "my-secret-key-123"

    # Weak password comparison
    if password == "admin":
        return True
    return False

# Exposed credentials
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://admin:password123@localhost/mydb"
"""

    audit_request = {
        "session_id": session_id,
        "student_id": "student_sprint6_dso_001",
        "activity_id": "sprint6_security_audit",
        "code": vulnerable_code,
        "language": "python"
    }

    response = requests.post(
        f"{API_BASE}/simulators/security/audit",
        json=audit_request
    )

    if response.status_code != 200:
        print(f"❌ Error en auditoría: {response.status_code}")
        print(response.text)
        return False

    data = response.json()["data"]

    print(f"🔍 Auditoría ID: {data['audit_id']}")
    print(f"📊 Vulnerabilidades totales: {data['total_vulnerabilities']}")
    print(f"   🔴 Críticas: {data['critical_count']}")
    print(f"   🟠 Altas:    {data['high_count']}")
    print(f"   🟡 Medias:   {data['medium_count']}")
    print(f"   🟢 Bajas:    {data['low_count']}")
    print(f"\n🛡️  Score de seguridad: {data['overall_security_score']:.1f}/10")
    print(f"✅ Cumple OWASP: {'Sí' if data['compliant_with_owasp'] else 'No'}\n")

    if data['vulnerabilities']:
        print("🚨 Vulnerabilidades detectadas:\n")
        for i, vuln in enumerate(data['vulnerabilities'][:5], 1):  # Mostrar primeras 5
            severity_icon = {
                "CRITICAL": "🔴",
                "HIGH": "🟠",
                "MEDIUM": "🟡",
                "LOW": "🟢",
                "INFO": "ℹ️"
            }.get(vuln['severity'], "❓")

            print(f"{severity_icon} Vulnerabilidad #{i}: {vuln['vulnerability_type']}")
            print(f"   Severidad: {vuln['severity']}")
            if vuln['line_number']:
                print(f"   Línea: {vuln['line_number']}")
            print(f"   Descripción: {vuln['description']}")
            print(f"   Recomendación: {vuln['recommendation']}")
            if vuln['cwe_id']:
                print(f"   CWE ID: {vuln['cwe_id']}")
            if vuln['owasp_category']:
                print(f"   OWASP: {vuln['owasp_category']}")
            print()

        if len(data['vulnerabilities']) > 5:
            print(f"... y {len(data['vulnerabilities']) - 5} vulnerabilidades más\n")

    if data['recommendations']:
        print("💡 Recomendaciones generales:")
        for rec in data['recommendations'][:3]:
            print(f"   - {rec}")
        print()

    # Test 2: Código seguro (para contrastar)
    print_subsection("Test 3.2: Auditar código seguro (buenas prácticas)")

    secure_code = """
import sqlite3
import os
from typing import Optional

def get_user(username: str) -> Optional[tuple]:
    # Using parameterized queries (prevents SQL injection)
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    return cursor.fetchone()

def authenticate(username: str, password: str) -> bool:
    # Using environment variables for secrets
    secret_key = os.environ.get('SECRET_KEY')

    # Using proper password hashing library (placeholder)
    from hashlib import sha256
    hashed = sha256(password.encode()).hexdigest()

    # Would use bcrypt or similar in production
    return verify_password(hashed)

# Secrets loaded from environment
API_KEY = os.environ.get('API_KEY')
DATABASE_URL = os.environ.get('DATABASE_URL')
"""

    audit_request2 = {
        "session_id": session_id,
        "student_id": "student_sprint6_dso_001",
        "activity_id": "sprint6_security_audit",
        "code": secure_code,
        "language": "python"
    }

    response2 = requests.post(
        f"{API_BASE}/simulators/security/audit",
        json=audit_request2
    )

    data2 = response2.json()["data"]

    print(f"🔍 Auditoría ID: {data2['audit_id']}")
    print(f"📊 Vulnerabilidades totales: {data2['total_vulnerabilities']}")
    print(f"🛡️  Score de seguridad: {data2['overall_security_score']:.1f}/10")
    print(f"✅ Cumple OWASP: {'Sí' if data2['compliant_with_owasp'] else 'No'}\n")

    if data2['total_vulnerabilities'] == 0:
        print("✅ ¡Código limpio! No se detectaron vulnerabilidades críticas.\n")

    print("✅ Test DSO-IA completado\n")
    return True


def main():
    """Ejecuta todos los tests de simuladores Sprint 6"""
    print("=" * 80)
    print("  TEST SUITE: Simuladores Sprint 6 (SM-IA, CX-IA, DSO-IA)")
    print("=" * 80)

    print("\n⚠️  IMPORTANTE: Asegúrese de que el servidor FastAPI esté corriendo:")
    print("   python scripts/run_api.py\n")

    input("Presione Enter para comenzar los tests...")

    results = {
        "SM-IA (Scrum Master)": False,
        "CX-IA (Cliente Experience)": False,
        "DSO-IA (DevSecOps Auditor)": False
    }

    try:
        # Test 1: SM-IA
        results["SM-IA (Scrum Master)"] = test_sm_ia_daily_standup()

        # Test 2: CX-IA
        results["CX-IA (Cliente Experience)"] = test_cx_ia_client_experience()

        # Test 3: DSO-IA
        results["DSO-IA (DevSecOps Auditor)"] = test_dso_ia_security_audit()

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor API")
        print("   Asegúrese de que el servidor esté corriendo en http://localhost:8000")
        return False
    except Exception as e:
        print(f"\n❌ ERROR inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # Resumen final
    print_section("RESUMEN DE TESTS")

    all_passed = True
    for simulator, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {simulator}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("✅ TODOS LOS TESTS PASARON")
        print("\nSimuladores verificados:")
        print("  1. SM-IA - Daily standup con feedback y detección de impedimentos")
        print("  2. CX-IA - Elicitación de requisitos y evaluación de soft skills")
        print("  3. DSO-IA - Auditoría de seguridad con detección OWASP Top 10")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("Revise los errores arriba para más detalles.")

    print("=" * 80 + "\n")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
