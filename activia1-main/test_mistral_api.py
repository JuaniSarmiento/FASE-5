"""Test Mistral API directly"""
import os
import httpx
import asyncio
import json

async def test_mistral_api():
    api_key = "dIP8GSbBnLhyGCSOiHvZn96W7CLgYM2J"
    
    url = "https://api.mistral.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistral-small-latest",
        "messages": [
            {
                "role": "user",
                "content": "Di 'Hola' en una sola palabra"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 10
    }
    
    print("🔍 Probando conexión a Mistral API...")
    print(f"URL: {url}")
    print(f"Modelo: {payload['model']}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            
            print(f"\n✅ Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"✅ Respuesta de Mistral: {content}")
                print(f"✅ Tokens usados: {data['usage']}")
                return True
            else:
                print(f"❌ Error {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error al conectar con Mistral: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_mistral_api())
