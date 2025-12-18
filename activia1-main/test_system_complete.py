"""Prueba end-to-end del sistema con la nueva API key"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    print("1️⃣ Probando health check...")
    resp = requests.get(f"{BASE_URL}/health")
    if resp.status_code == 200:
        print(f"   ✅ Backend OK - Status: {resp.json()['status']}")
        return True
    else:
        print(f"   ❌ Error {resp.status_code}")
        return False

def test_tutor_interaction():
    print("\n2️⃣ Probando interacción con Tutor IA...")
    
    # Crear sesión
    session_data = {
        "student_id": "test_student_001",
        "activity_id": "test_activity",
        "mode": "TUTOR"
    }
    
    resp = requests.post(f"{BASE_URL}/sessions", json=session_data)
    if resp.status_code != 201:
        print(f"   ❌ Error creando sesión: {resp.status_code}")
        print(f"      {resp.text[:200]}")
        return False
    
    session = resp.json()['data']
    session_id = session['id']
    print(f"   ✅ Sesión creada: {session_id}")
    
    # Enviar interacción
    interaction_data = {
        "session_id": session_id,
        "prompt": "¿Qué es una lista en Python?",
        "context": {}
    }
    
    print("   🔄 Enviando pregunta al tutor...")
    resp = requests.post(f"{BASE_URL}/interactions", json=interaction_data)
    
    if resp.status_code == 201:
        result = resp.json()['data']
        response_text = result['response'][:100]
        print(f"   ✅ Respuesta recibida:")
        print(f"      {response_text}...")
        print(f"      Agente: {result.get('agent_used', 'N/A')}")
        return True
    else:
        print(f"   ❌ Error en interacción: {resp.status_code}")
        print(f"      {resp.text[:200]}")
        return False

def test_simulator():
    print("\n3️⃣ Probando simulador...")
    
    # Crear sesión de simulador
    session_data = {
        "student_id": "test_student_001",
        "activity_id": "test_simulator",
        "mode": "SIMULATOR",
        "simulator_type": "product_owner"
    }
    
    resp = requests.post(f"{BASE_URL}/sessions", json=session_data)
    if resp.status_code != 201:
        print(f"   ❌ Error creando sesión: {resp.status_code}")
        return False
    
    session = resp.json()['data']
    session_id = session['id']
    print(f"   ✅ Sesión de simulador creada: {session_id}")
    
    # Interactuar con simulador
    interaction_data = {
        "session_id": session_id,
        "simulator_type": "product_owner",
        "prompt": "Hola, necesito revisar los requisitos del proyecto"
    }
    
    print("   🔄 Interactuando con Product Owner...")
    resp = requests.post(f"{BASE_URL}/simulators/interact", json=interaction_data)
    
    if resp.status_code in [200, 201]:
        result = resp.json()['data']
        response_text = result['response'][:100]
        print(f"   ✅ Respuesta del simulador:")
        print(f"      {response_text}...")
        return True
    else:
        print(f"   ❌ Error en simulador: {resp.status_code}")
        print(f"      {resp.text[:200]}")
        return False

def main():
    print("="*60)
    print("PRUEBA END-TO-END DEL SISTEMA")
    print("="*60)
    print()
    
    results = {
        'health': test_health(),
        'tutor': test_tutor_interaction(),
        'simulator': test_simulator()
    }
    
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    for name, success in results.items():
        status = "✅ OK" if success else "❌ FALLÓ"
        print(f"{name.capitalize()}: {status}")
    
    all_ok = all(results.values())
    print(f"\n{'✅ SISTEMA FUNCIONANDO CORRECTAMENTE' if all_ok else '⚠️ HAY PROBLEMAS QUE REVISAR'}")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
