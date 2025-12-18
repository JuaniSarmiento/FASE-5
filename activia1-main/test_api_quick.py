"""Prueba rápida de la nueva API key de Gemini"""
import asyncio
import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_gemini():
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"✓ API Key: {api_key[:20]}...")
    
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
    
    payload = {
        'contents': [{
            'parts': [{
                'text': '¿Cuál es la capital de Francia? Responde en una palabra.'
            }]
        }]
    }
    
    print("🔄 Enviando request a Gemini 2.5 Flash...")
    
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(url, json=payload)
            print(f"Status Code: {resp.status_code}")
            
            if resp.status_code == 200:
                result = resp.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"\n✅ ÉXITO! Respuesta de Gemini:")
                    print(f"   {text}")
                    return True
                else:
                    print(f"❌ Respuesta inesperada: {json.dumps(result, indent=2)[:300]}")
            else:
                print(f"❌ Error {resp.status_code}")
                print(f"   {resp.text[:300]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini())
    exit(0 if success else 1)
