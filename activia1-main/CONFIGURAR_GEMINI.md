# 🔧 Configuración Gemini - Guía Rápida

## ⚠️ Problema Actual

La API key de Gemini configurada está retornando error 404. Esto puede significar:

1. **La API key es inválida o expiró**
2. **La API key no tiene permisos correctos**
3. **El servicio de Gemini cambió**

## ✅ Solución: Obtener Nueva API Key

### Paso 1: Ir a Google AI Studio
Abre tu navegador y ve a:
```
https://makersuite.google.com/app/apikey
```

O también puedes usar:
```
https://aistudio.google.com/apikey
```

### Paso 2: Crear API Key
1. Inicia sesión con tu cuenta de Google
2. Click en "Create API Key" (Crear API key)
3. Selecciona un proyecto existente o crea uno nuevo
4. Copia la API key generada

### Paso 3: Actualizar .env
Abre el archivo `.env` y reemplaza la línea:
```bash
GEMINI_API_KEY=AIzaSyDxzTCLcsOIYGwrcAvXdRc4kU_h1oJP0hg
```

Con tu nueva API key:
```bash
GEMINI_API_KEY=tu_nueva_api_key_aqui
```

### Paso 4: Reiniciar Backend
```bash
docker compose restart api
```

## 🧪 Test Rápido

Para verificar que funciona:
```bash
cd C:\Users\juani\Desktop\activia3\activia1-main
$env:LLM_PROVIDER="gemini"
$env:GEMINI_API_KEY="tu_nueva_api_key"
python -c "
import asyncio
import httpx

async def test():
    api_key = 'tu_nueva_api_key'
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}'
    
    payload = {
        'contents': [{
            'parts': [{'text': 'Di hola'}]
        }]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            print('✅ API Key funciona!')
            print(response.json())
        else:
            print('❌ Error:', response.text)

asyncio.run(test())
"
```

## 📝 Notas Importantes

- **Gemini API es gratuita** hasta cierto límite de requests
- La API key NO debe compartirse públicamente
- NO subir el .env al repositorio (ya está en .gitignore)

## 🔗 Links Útiles

- Documentación: https://ai.google.dev/gemini-api/docs
- Límites y cuotas: https://ai.google.dev/gemini-api/docs/quota
- Modelos disponibles: https://ai.google.dev/gemini-api/docs/models/gemini

## 💡 Alternativa: Usar Modo Mock Temporalmente

Si no quieres configurar Gemini ahora, puedes volver a modo mock:

En `.env`, cambiar:
```bash
LLM_PROVIDER=mock
```

Y comentar:
```bash
# GEMINI_API_KEY=...
```

Luego reiniciar:
```bash
docker compose restart api
```

El sistema funcionará con respuestas simuladas hasta que configures Gemini.
