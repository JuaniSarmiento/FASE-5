"""
Test de Integración Frontend-Backend del Tutor Socrático V2.0

Este script valida que el backend esté correctamente configurado para
responder con la metadata esperada por el frontend.

Ejecutar:
    python examples/test_tutor_frontend_integration.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_create_tutor_session():
    """Test 1: Crear sesión de tutoría"""
    print("\n🧪 TEST 1: Crear Sesión de Tutoría")
    print("=" * 60)
    
    response = requests.post(f"{BASE_URL}/sessions/create-tutor")
    
    if response.status_code == 200:
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Sesión creada exitosamente")
        print(f"   Session ID: {session_id}")
        return session_id
    else:
        print(f"❌ Error al crear sesión: {response.status_code}")
        print(f"   {response.text}")
        return None


def test_send_code_request(session_id):
    """Test 2: Solicitar código directo (debe rechazar)"""
    print("\n🧪 TEST 2: Solicitar Código Directo")
    print("=" * 60)
    
    payload = {
        "message": "Dame el código para ordenar un array en Python",
        "student_profile": {
            "avg_ai_involvement": 0.5,
            "successful_autonomous_solutions": 2,
            "error_self_correction_rate": 0.3
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/sessions/{session_id}/interact",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Respuesta recibida")
        print(f"\n📝 Mensaje del Tutor:")
        print(f"   {data['response'][:200]}...")
        
        metadata = data.get('metadata', {})
        print(f"\n🔍 Metadata:")
        print(f"   • Tipo de Intervención: {metadata.get('intervention_type', 'N/A')}")
        print(f"   • Semáforo: {metadata.get('semaforo', 'N/A').upper()}")
        print(f"   • Nivel de Ayuda: {metadata.get('help_level', 'N/A')}")
        print(f"   • Requiere Respuesta: {metadata.get('requires_student_response', 'N/A')}")
        
        # Validaciones frontend
        assert metadata.get('semaforo') in ['verde', 'amarillo', 'rojo'], \
            "⚠️ Semáforo debe ser verde/amarillo/rojo"
        
        assert metadata.get('intervention_type') in [
            'pregunta_socratica', 'rechazo_pedagogico', 'pista_graduada',
            'correccion_conceptual', 'exigencia_justificacion'
        ], "⚠️ Tipo de intervención inválido"
        
        print(f"\n✅ Metadata válida para frontend")
        
        # Esperamos rechazo pedagógico o pregunta socrática
        if metadata.get('intervention_type') in ['rechazo_pedagogico', 'pregunta_socratica']:
            print(f"✅ Tipo de intervención correcto (no dio código directo)")
        else:
            print(f"⚠️ Se esperaba rechazo pedagógico o pregunta socrática")
        
        return True
    else:
        print(f"❌ Error en interacción: {response.status_code}")
        return False


def test_conceptual_question(session_id):
    """Test 3: Pregunta conceptual (debe responder con pregunta)"""
    print("\n🧪 TEST 3: Pregunta Conceptual")
    print("=" * 60)
    
    payload = {
        "message": "¿Qué es mejor, mergesort o quicksort?",
        "student_profile": {
            "avg_ai_involvement": 0.3,
            "successful_autonomous_solutions": 5,
            "error_self_correction_rate": 0.7
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/sessions/{session_id}/interact",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Respuesta recibida")
        print(f"\n📝 Mensaje del Tutor:")
        print(f"   {data['response'][:200]}...")
        
        metadata = data.get('metadata', {})
        print(f"\n🔍 Metadata:")
        print(f"   • Tipo de Intervención: {metadata.get('intervention_type', 'N/A')}")
        print(f"   • Semáforo: {metadata.get('semaforo', 'N/A').upper()}")
        
        # Esperamos semáforo verde (bajo riesgo)
        if metadata.get('semaforo') == 'verde':
            print(f"✅ Semáforo correcto (verde = bajo riesgo)")
        else:
            print(f"⚠️ Se esperaba semáforo verde para pregunta conceptual")
        
        return True
    else:
        print(f"❌ Error en interacción: {response.status_code}")
        return False


def test_code_without_justification(session_id):
    """Test 4: Enviar código sin justificación (debe exigir explicación)"""
    print("\n🧪 TEST 4: Código Sin Justificación")
    print("=" * 60)
    
    payload = {
        "message": """
```python
def ordenar(arr):
    return sorted(arr)
```
        """,
        "student_profile": {
            "avg_ai_involvement": 0.6,
            "successful_autonomous_solutions": 3,
            "error_self_correction_rate": 0.4
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/sessions/{session_id}/interact",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Respuesta recibida")
        print(f"\n📝 Mensaje del Tutor:")
        print(f"   {data['response'][:200]}...")
        
        metadata = data.get('metadata', {})
        print(f"\n🔍 Metadata:")
        print(f"   • Tipo de Intervención: {metadata.get('intervention_type', 'N/A')}")
        print(f"   • Semáforo: {metadata.get('semaforo', 'N/A').upper()}")
        
        # Esperamos exigencia de justificación
        if metadata.get('intervention_type') == 'exigencia_justificacion':
            print(f"✅ Tipo de intervención correcto (exige justificación)")
        else:
            print(f"⚠️ Se esperaba exigencia de justificación")
        
        # Puede ser amarillo o rojo dependiendo del perfil
        if metadata.get('semaforo') in ['amarillo', 'rojo']:
            print(f"✅ Semáforo adecuado (alta dependencia detectada)")
        
        return True
    else:
        print(f"❌ Error en interacción: {response.status_code}")
        return False


def test_get_analytics(session_id):
    """Test 5: Obtener analytics de la sesión"""
    print("\n🧪 TEST 5: Analytics N4")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/sessions/{session_id}/analytics-n4")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Analytics obtenidos correctamente")
        
        print(f"\n📊 Estadísticas:")
        print(f"   • Total de Mensajes: {data.get('total_messages', 0)}")
        
        semaforo_dist = data.get('semaforo_distribution', {})
        print(f"   • Distribución de Semáforos:")
        print(f"     - Verde: {semaforo_dist.get('verde', 0)}")
        print(f"     - Amarillo: {semaforo_dist.get('amarillo', 0)}")
        print(f"     - Rojo: {semaforo_dist.get('rojo', 0)}")
        
        intervention_types = data.get('intervention_types', {})
        print(f"   • Tipos de Intervención:")
        for tipo, count in intervention_types.items():
            print(f"     - {tipo}: {count}")
        
        print(f"\n✅ Formato de analytics válido para frontend")
        return True
    else:
        print(f"❌ Error al obtener analytics: {response.status_code}")
        return False


def main():
    """Ejecutar todos los tests de integración"""
    print("\n" + "=" * 60)
    print("🚀 TEST DE INTEGRACIÓN FRONTEND-BACKEND TUTOR V2.0")
    print("=" * 60)
    
    # Test 1: Crear sesión
    session_id = test_create_tutor_session()
    if not session_id:
        print("\n❌ No se pudo crear sesión. Verifica que el backend esté corriendo.")
        return
    
    # Test 2: Solicitar código (debe rechazar)
    test_send_code_request(session_id)
    
    # Test 3: Pregunta conceptual
    test_conceptual_question(session_id)
    
    # Test 4: Código sin justificación
    test_code_without_justification(session_id)
    
    # Test 5: Analytics
    test_get_analytics(session_id)
    
    print("\n" + "=" * 60)
    print("✅ TESTS DE INTEGRACIÓN COMPLETADOS")
    print("=" * 60)
    print("\n💡 Próximo paso: Abrir frontend en http://localhost:5173/tutor")
    print("   y verificar que los badges de semáforo y tipos de intervención")
    print("   se muestren correctamente en la interfaz.")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se puede conectar al backend")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:8000")
        print("\n   Ejecuta:")
        print("   cd backend")
        print("   uvicorn api.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
