"""
Script de prueba rápida con Gemini 2.5
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

async def test_gemini_25():
    """Prueba con Gemini 2.5 Flash"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    model = "gemini-2.5-flash"
    
    # URL con el modelo correcto
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {
        "contents": [
            {
                "parts": [{"text": "Hola, ¿puedes responder 'Sistema funcionando correctamente' si me recibes?"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 100
        }
    }
    
    print(f"🔄 Probando {model}...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"✅ ÉXITO!")
                print(f"Respuesta: {text}")
                return True
            else:
                print(f"❌ Error: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def test_provider():
    """Prueba con el provider actualizado"""
    
    print("\n" + "="*60)
    print("PRUEBA CON GEMINI PROVIDER 2.5")
    print("="*60)
    
    try:
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        
        from llm.gemini_provider import GeminiProvider
        from llm.base import LLMMessage, LLMRole
        
        provider = GeminiProvider({
            "api_key": os.getenv("GEMINI_API_KEY"),
            "model": "gemini-2.5-flash",
            "temperature": 0.7,
            "timeout": 30
        })
        
        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content="Eres un tutor de programación útil y conciso."),
            LLMMessage(role=LLMRole.USER, content="¿Qué es Python en una frase?")
        ]
        
        print("🔄 Generando respuesta con provider...")
        response = await provider.generate(messages)
        
        print(f"✅ ÉXITO!")
        print(f"Respuesta: {response.content}")
        if hasattr(response, 'usage'):
            print(f"Tokens: {response.usage.get('total_tokens', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("="*60)
    print("VERIFICACIÓN GEMINI 2.5")
    print("="*60)
    
    # Prueba 1: API directa
    print("\n1️⃣ Prueba API directa")
    print("-"*60)
    test1 = await test_gemini_25()
    
    # Prueba 2: Provider
    test2 = await test_provider()
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"API directa: {'✅' if test1 else '❌'}")
    print(f"Provider: {'✅' if test2 else '❌'}")
    
    if test1 and test2:
        print("\n🎉 ¡Gemini 2.5 funcionando perfectamente!")
        return True
    else:
        print("\n⚠️ Revisar errores arriba")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
