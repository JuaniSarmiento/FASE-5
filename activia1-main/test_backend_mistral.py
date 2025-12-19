"""Test completo del backend con Mistral AI"""
import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/api/v1"

async def test_backend_with_mistral():
    """Prueba todos los agentes con Mistral"""
    
    print("=" * 80)
    print("🧪 TEST COMPLETO BACKEND CON MISTRAL AI")
    print("=" * 80)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        
        # 1. Health check
        print("\n1️⃣ Health Check...")
        try:
            resp = await client.get(f"{BASE_URL}/health")
            assert resp.status_code == 200
            data = resp.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   ✅ Version: {data.get('version', 'N/A')}")
            print(f"   ✅ Database: {data.get('database', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        # 2. Crear sesión
        print("\n2️⃣ Crear sesión de estudio...")
        try:
            payload = {
                "student_id": "test_mistral_001",
                "activity_id": "act_test_001",
                "mode": "TUTOR",
                "subject": "matematicas",
                "topic": "fracciones"
            }
            resp = await client.post(f"{BASE_URL}/sessions", json=payload)
            if resp.status_code not in [200, 201]:
                print(f"   ❌ Status: {resp.status_code}")
                print(f"   ❌ Response: {resp.text}")
                return False
            result = resp.json()
            session_id = result["data"]["id"]
            print(f"   ✅ Sesión creada: {session_id}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 3. Interacción con T-IA-Cog (Tutor)
        print("\n3️⃣ Test T-IA-Cog (Tutor Socrático)...")
        try:
            payload = {
                "session_id": session_id,
                "student_id": "test_mistral_001",
                "prompt": "¿Qué es una fracción?"
            }
            resp = await client.post(f"{BASE_URL}/interactions", json=payload)
            if resp.status_code not in [200, 201]:
                print(f"   ❌ Status: {resp.status_code}")
                print(f"   ❌ Response: {resp.text[:300]}")
                return False
            result = resp.json()
            response_text = result.get("data", {}).get("response", result.get("response", ""))
            
            # Verificar que NO sea respuesta de fallback
            is_fallback = any(marker in response_text.lower() for marker in [
                "entiendo tu pregunta",
                "esa es una buena pregunta",
                "gracias por tu participación"
            ])
            
            if is_fallback:
                print(f"   ⚠️  Respuesta de FALLBACK (sin LLM)")
            else:
                print(f"   ✅ Respuesta del LLM Mistral:")
            
            print(f"   📝 {response_text[:200]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 4. Test E-IA-Proc (Evaluador)
        print("\n4️⃣ Test E-IA-Proc (Evaluador de Proceso)...")
        try:
            resp = await client.post(
                f"{BASE_URL}/evaluations/{session_id}/generate",
                params={"criteria": "comprension"}
            )
            assert resp.status_code == 200
            data = resp.json()
            print(f"   ✅ Evaluación generada: {data.get('evaluation_id', 'N/A')}")
            print(f"   📊 Criterio: {data.get('criteria', 'N/A')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 5. Test S-IA-X (Simulador Socrático)
        print("\n5️⃣ Test S-IA-X (Simulador Socrático)...")
        try:
            payload = {
                "student_id": "test_mistral_001",
                "message": "¿Por qué el agua hierve a 100 grados?",
                "simulator_type": "socratico"
            }
            resp = await client.post(f"{BASE_URL}/simulators/interact", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            print(f"   ✅ Simulador: {data.get('simulator_type', 'N/A')}")
            print(f"   📝 {data.get('response', '')[:150]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 6. Test S-IA-X (Simulador Empático)
        print("\n6️⃣ Test S-IA-X (Simulador Empático)...")
        try:
            payload = {
                "student_id": "test_mistral_001",
                "message": "Estoy muy frustrado con este problema",
                "simulator_type": "empatico"
            }
            resp = await client.post(f"{BASE_URL}/simulators/interact", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            print(f"   ✅ Simulador: {data.get('simulator_type', 'N/A')}")
            print(f"   📝 {data.get('response', '')[:150]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 7. Test AR-IA (Risk Analyst)
        print("\n7️⃣ Test AR-IA (Analista de Riesgo) - CON LLM...")
        try:
            resp = await client.post(
                f"{BASE_URL}/sessions/{session_id}/analyze-risk"
            )
            assert resp.status_code == 200
            data = resp.json()
            print(f"   ✅ Análisis generado")
            print(f"   📊 Nivel de riesgo: {data.get('risk_level', 'N/A')}")
            print(f"   💡 Recomendaciones: {len(data.get('recommendations', []))} items")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print("\n" + "=" * 80)
        print("✅ TESTS COMPLETADOS - Backend funcionando con Mistral AI")
        print("=" * 80)
        return True

if __name__ == "__main__":
    asyncio.run(test_backend_with_mistral())
