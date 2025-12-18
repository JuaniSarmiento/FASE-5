"""Prueba con diferentes modelos de Gemini"""
import asyncio
import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_model(model_name):
    api_key = os.getenv('GEMINI_API_KEY')
    
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}'
    
    payload = {
        'contents': [{
            'parts': [{
                'text': '¿Cuál es 2+2? Responde solo el número.'
            }]
        }]
    }
    
    print(f"🔄 Probando {model_name}...", end=" ")
    
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(url, json=payload)
            
            if resp.status_code == 200:
                result = resp.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    print(f"✅ {resp.status_code} - Respuesta: {text}")
                    return model_name
                else:
                    print(f"⚠️  {resp.status_code} - Respuesta inesperada")
            else:
                error_msg = resp.json().get('error', {}).get('message', 'Unknown')[:50]
                print(f"❌ {resp.status_code} - {error_msg}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)[:50]}")
    
    return None

async def main():
    print("="*60)
    print("PROBANDO MODELOS GEMINI DISPONIBLES")
    print("="*60)
    
    models_to_test = [
        'gemini-2.5-flash',
        'gemini-2.5-pro',
        'gemini-2.0-flash',
        'gemini-flash-latest',
        'gemini-pro-latest',
        'gemini-2.0-flash-lite',
        'gemini-2.5-flash-lite'
    ]
    
    working_models = []
    
    for model in models_to_test:
        result = await test_model(model)
        if result:
            working_models.append(result)
        await asyncio.sleep(1)  # Esperar 1 segundo entre requests
    
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    if working_models:
        print(f"\n✅ Modelos funcionando ({len(working_models)}):")
        for model in working_models:
            print(f"   - {model}")
        print(f"\n💡 Recomendación: Usar '{working_models[0]}' en el .env")
        return working_models[0]
    else:
        print("\n❌ Ningún modelo disponible en este momento")
        print("   Esto puede deberse a:")
        print("   - Sobrecarga temporal del servicio")
        print("   - Rate limiting")
        print("   - Restricciones de la API key")
        return None

if __name__ == "__main__":
    best_model = asyncio.run(main())
    exit(0 if best_model else 1)
