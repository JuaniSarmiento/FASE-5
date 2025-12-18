"""
Script para verificar qué modelos de Gemini están disponibles
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

async def list_available_models():
    """Lista los modelos disponibles en Gemini API"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ ERROR: GEMINI_API_KEY no encontrada")
        return
    
    # URL para listar modelos
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    print("🔄 Consultando modelos disponibles...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                print("\n✅ Modelos disponibles:")
                print("="*60)
                
                for model in data.get("models", []):
                    name = model.get("name", "")
                    display_name = model.get("displayName", "")
                    supported_methods = model.get("supportedGenerationMethods", [])
                    
                    if "generateContent" in supported_methods:
                        print(f"\n📦 {name}")
                        print(f"   Display Name: {display_name}")
                        print(f"   Métodos: {', '.join(supported_methods)}")
                
                print("\n" + "="*60)
            else:
                print(f"❌ ERROR: Status {response.status_code}")
                print(response.text)
                
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")

async def test_specific_model(model_name: str):
    """Prueba un modelo específico"""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    # Probar con diferentes versiones de API
    versions = ["v1beta", "v1"]
    
    for version in versions:
        url = f"https://generativelanguage.googleapis.com/{version}/models/{model_name}:generateContent?key={api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": "Hola"}]
                }
            ]
        }
        
        print(f"\n🔄 Probando {model_name} con API {version}...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    print(f"✅ FUNCIONA con {version}")
                    data = response.json()
                    if "candidates" in data:
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        print(f"Respuesta: {text}")
                    return True
                else:
                    print(f"❌ Error {response.status_code} con {version}")
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    return False

async def main():
    print("="*60)
    print("VERIFICACIÓN DE MODELOS GEMINI")
    print("="*60)
    
    # Listar modelos disponibles
    await list_available_models()
    
    # Probar modelos comunes
    print("\n" + "="*60)
    print("PRUEBA DE MODELOS COMUNES")
    print("="*60)
    
    models_to_test = [
        "gemini-pro",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-2.0-flash-exp"
    ]
    
    for model in models_to_test:
        await test_specific_model(model)

if __name__ == "__main__":
    asyncio.run(main())
