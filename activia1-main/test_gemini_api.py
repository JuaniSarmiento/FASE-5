"""
Script de verificación de API de Gemini
Prueba la nueva API key configurada
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

async def test_gemini_api():
    """Prueba básica de la API de Gemini"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY no encontrada en .env")
        return False
    
    print(f"✓ API Key encontrada: {api_key[:20]}...")
    
    # URL de la API de Gemini
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # Payload de prueba simple
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "Hola, responde con 'OK' si puedes verme"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 100
        }
    }
    
    print("\n🔄 Probando conexión con Gemini API...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extraer respuesta
                if "candidates" in data and len(data["candidates"]) > 0:
                    text = data["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"✅ ÉXITO: API funcionando correctamente")
                    print(f"Respuesta de Gemini: {text}")
                    return True
                else:
                    print("❌ ERROR: Respuesta sin contenido")
                    print(f"Data: {data}")
                    return False
            else:
                print(f"❌ ERROR: Status {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except httpx.TimeoutException:
        print("❌ ERROR: Timeout al conectar con Gemini")
        return False
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        return False

async def test_gemini_provider():
    """Prueba usando el GeminiProvider del proyecto"""
    print("\n" + "="*60)
    print("PRUEBA CON GEMINI PROVIDER")
    print("="*60)
    
    try:
        # Importar el provider
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        
        from llm.gemini_provider import GeminiProvider
        from llm.base import LLMMessage, LLMRole
        
        # Crear provider
        provider = GeminiProvider({
            "api_key": os.getenv("GEMINI_API_KEY"),
            "model": "gemini-1.5-flash",
            "temperature": 0.7,
            "timeout": 30
        })
        
        # Crear mensajes de prueba
        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content="Eres un asistente útil."),
            LLMMessage(role=LLMRole.USER, content="Di 'Hola desde el provider' si funcionas correctamente")
        ]
        
        print("🔄 Generando respuesta...")
        response = await provider.generate(messages)
        
        print(f"✅ ÉXITO: Provider funcionando")
        print(f"Respuesta: {response.content[:200]}...")
        print(f"Tokens usados: {response.total_tokens}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en provider: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Ejecuta todas las pruebas"""
    print("="*60)
    print("VERIFICACIÓN DE API DE GEMINI")
    print("="*60)
    
    # Prueba 1: API directa
    print("\n1️⃣ Prueba de API directa")
    print("-" * 60)
    test1 = await test_gemini_api()
    
    # Prueba 2: Provider del proyecto
    print("\n2️⃣ Prueba de GeminiProvider")
    print("-" * 60)
    test2 = await test_gemini_provider()
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"API directa: {'✅ OK' if test1 else '❌ FALLO'}")
    print(f"Provider: {'✅ OK' if test2 else '❌ FALLO'}")
    
    if test1 and test2:
        print("\n🎉 ¡Todo funcionando correctamente!")
        return True
    else:
        print("\n⚠️ Hay problemas que corregir")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
