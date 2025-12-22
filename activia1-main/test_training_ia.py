"""
Script de prueba para verificar evaluación con IA en Training
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_training_flow():
    print("\n=== PROBANDO FLUJO DE TRAINING CON IA ===\n")
    
    # 1. Registrar usuario de prueba
    print("1. Registrando usuario de prueba...")
    timestamp = int(time.time())
    register_data = {
        "username": f"test_ia_{timestamp}",
        "email": f"test_ia_{timestamp}@test.com",
        "password": "test123",
        "full_name": "Test IA User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"   Registro: {response.status_code}")
        
        if response.status_code == 201:
            # Registro exitoso
            auth_data = response.json()
            token = auth_data['data']['tokens']['access_token']
        elif response.status_code == 200:
            # Login exitoso
            auth_data = response.json()
            token = auth_data['data']['tokens']['access_token']
        else:
            print(f"   Error: {response.text}")
            # Intentar login con usuario existente
            print("   Intentando login con usuario test existente...")
            response = requests.post(f"{BASE_URL}/auth/login", json={
                "username": "test",
                "password": "test123"
            })
            auth_data = response.json()
            token = auth_data['data']['tokens']['access_token']
        
        print(f"   ✅ Token obtenido")
    except Exception as e:
        print(f"   ❌ Error en autenticación: {e}")
        import traceback
        traceback.print_exc()
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Iniciar sesión de training
    print("\n2. Iniciando sesión de training en Secuenciales...")
    try:
        response = requests.post(
            f"{BASE_URL}/training/iniciar",
            json={"materia_codigo": "PROG1", "tema_id": "secuenciales"},
            headers=headers
        )
        print(f"   Iniciar: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return
        
        sesion_data = response.json()
        session_id = sesion_data['session_id']
        print(f"   ✅ Sesión creada: {session_id}")
        print(f"   Ejercicio actual: {sesion_data['ejercicio_actual']['numero']}")
        print(f"   Consigna: {sesion_data['ejercicio_actual']['consigna'][:80]}...")
    except Exception as e:
        print(f"   ❌ Error iniciando sesión: {e}")
        return
    
    # 3. Enviar código correcto para ejercicio 1 (sumar)
    print("\n3. Enviando código CORRECTO para ejercicio 1 (sumar)...")
    codigo_correcto = """def sumar(a, b):
    return a + b"""
    
    try:
        response = requests.post(
            f"{BASE_URL}/training/submit-ejercicio",
            json={
                "session_id": session_id,
                "codigo_usuario": codigo_correcto
            },
            headers=headers
        )
        print(f"   Submit: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return
        
        resultado = response.json()
        print(f"\n   📊 RESULTADO DE EVALUACIÓN CON IA:")
        print(f"   Correcto: {resultado['resultado']['correcto']}")
        print(f"   Tests pasados: {resultado['resultado']['tests_pasados']}/{resultado['resultado']['tests_totales']}")
        print(f"   Mensaje: {resultado['resultado']['mensaje']}")
        print(f"   Hay siguiente: {resultado['hay_siguiente']}")
        
        if resultado['resultado']['tests_pasados'] > 0:
            print(f"\n   ✅ LA IA EVALUÓ CORRECTAMENTE!")
        else:
            print(f"\n   ⚠️  La IA no aprobó el ejercicio (puede ser por la lógica de evaluación)")
        
    except Exception as e:
        print(f"   ❌ Error enviando código: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 4. Enviar código INCORRECTO para ver evaluación negativa
    print("\n4. Enviando código INCORRECTO para ejercicio 2...")
    codigo_incorrecto = """def area_rectangulo(base, altura):
    return base + altura  # INCORRECTO: debe ser multiplicación"""
    
    try:
        response = requests.post(
            f"{BASE_URL}/training/submit-ejercicio",
            json={
                "session_id": session_id,
                "codigo_usuario": codigo_incorrecto
            },
            headers=headers
        )
        print(f"   Submit: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return
        
        resultado = response.json()
        print(f"\n   📊 RESULTADO DE EVALUACIÓN CON IA:")
        print(f"   Correcto: {resultado['resultado']['correcto']}")
        print(f"   Tests pasados: {resultado['resultado']['tests_pasados']}/{resultado['resultado']['tests_totales']}")
        print(f"   Mensaje: {resultado['resultado']['mensaje']}")
        
        if not resultado['resultado']['correcto']:
            print(f"\n   ✅ LA IA DETECTÓ EL ERROR CORRECTAMENTE!")
        
    except Exception as e:
        print(f"   ❌ Error enviando código incorrecto: {e}")
        return
    
    print("\n=== PRUEBA COMPLETADA ===\n")

if __name__ == "__main__":
    test_training_flow()
