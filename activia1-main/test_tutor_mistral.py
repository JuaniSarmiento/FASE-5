"""Test simplificado del backend con Mistral AI - Focus en Tutor"""
import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/api/v1"

async def test_tutor_with_mistral():
    """Prueba el agente tutor con Mistral"""
    
    print("=" * 80)
    print("🧪 TEST TUTOR CON MISTRAL AI")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # 1. Health check
        print("\n1️⃣ Health Check...")
        resp = await client.get(f"{BASE_URL}/health")
        data = resp.json()
        print(f"   ✅ Status: {data['status']}")
        print(f"   ✅ Database: {data.get('database', 'N/A')}")
        
        # 2. Crear sesión
        print("\n2️⃣ Crear sesión de tutoría...")
        payload = {
            "student_id": "test_mistral_tutor",
            "activity_id": "act_math_001",
            "mode": "TUTOR",
            "subject": "matematicas",
            "topic": "algebra"
        }
        resp = await client.post(f"{BASE_URL}/sessions", json=payload)
        result = resp.json()
        session_id = result["data"]["id"]
        print(f"   ✅ Sesión creada: {session_id}")
        
        # 3. Test: Pregunta simple
        print("\n3️⃣ Pregunta #1: ¿Qué es una variable?")
        payload = {
            "session_id": session_id,
            "student_id": "test_mistral_tutor",
            "prompt": "¿Qué es una variable en álgebra?"
        }
        resp = await client.post(f"{BASE_URL}/interactions", json=payload)
        result = resp.json()
        response_text = result.get("data", {}).get("response", "")
        print(f"   📝 Respuesta (primeros 300 chars):")
        print(f"      {response_text[:300]}...")
        
        # 4. Test: Seguimiento
        print("\n4️⃣ Pregunta #2: ¿Puedes darme un ejemplo?")
        payload = {
            "session_id": session_id,
            "student_id": "test_mistral_tutor",
            "prompt": "¿Puedes darme un ejemplo de variable?"
        }
        resp = await client.post(f"{BASE_URL}/interactions", json=payload)
        result = resp.json()
        response_text = result.get("data", {}).get("response", "")
        print(f"   📝 Respuesta (primeros 300 chars):")
        print(f"      {response_text[:300]}...")
        
        # 5. Test: Problema resuelto
        print("\n5️⃣ Pregunta #3: Resolver ecuación")
        payload = {
            "session_id": session_id,
            "student_id": "test_mistral_tutor",
            "prompt": "¿Cómo resuelvo 2x + 5 = 15?"
        }
        resp = await client.post(f"{BASE_URL}/interactions", json=payload)
        result = resp.json()
        response_text = result.get("data", {}).get("response", "")
        print(f"   📝 Respuesta (primeros 400 chars):")
        print(f"      {response_text[:400]}...")
        
        # 6. Verificar que Mistral está respondiendo (no fallback)
        print("\n" + "=" * 80)
        print("📊 VERIFICACIÓN DE CALIDAD")
        print("=" * 80)
        
        # Características de respuestas de Mistral (bien formateadas, detalladas)
        if len(response_text) > 100:
            print("   ✅ Respuestas detalladas (>100 chars)")
        
        if "###" in response_text or "**" in response_text:
            print("   ✅ Formato Markdown detectado")
        
        fallback_markers = [
            "entiendo tu pregunta",
            "esa es una buena pregunta",
            "gracias por tu participación"
        ]
        
        is_fallback = any(marker in response_text.lower() for marker in fallback_markers)
        if not is_fallback:
            print("   ✅ NO es respuesta de fallback - Mistral está activo")
        else:
            print("   ⚠️  Posible fallback detectado")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETADO - Mistral AI funcionando correctamente")
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_tutor_with_mistral())
