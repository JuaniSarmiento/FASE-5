# Guía de Migración de Ollama a Gemini API

## 📋 Resumen de Cambios

Este proyecto ha sido actualizado para usar **Google Gemini API** en lugar de Ollama como proveedor de LLM principal. Los cambios incluyen:

### 🎯 Características Principales

1. **Integración con Gemini API**
   - ✅ Gemini 1.5 Flash para conversaciones normales (rápido y económico)
   - ✅ Gemini 1.5 Pro para análisis de código y tareas complejas (automático)
   - ✅ Detección automática del tipo de tarea

2. **Mejoras en el Tutor Socrático**
   - ✅ Prompts mejorados para **NUNCA** dar código de programación
   - ✅ El tutor solo explica conceptos y guía con preguntas
   - ✅ Refuerzo de reglas pedagógicas estrictas

3. **Selección Inteligente de Modelos**
   - Flash para: Conversaciones, preguntas socráticas, explicaciones conceptuales
   - Pro para: Análisis de código, debugging, optimizaciones, algoritmos complejos

---

## 🚀 Pasos para Migrar

### 1. Obtener API Key de Gemini

1. Visita: https://makersuite.google.com/app/apikey
2. Inicia sesión con tu cuenta de Google
3. Crea una nueva API key
4. Copia la clave (la necesitarás en el siguiente paso)

### 2. Configurar Variables de Entorno

Edita tu archivo `.env` (o crea uno desde `.env.example`):

```bash
# Cambiar el proveedor a Gemini
LLM_PROVIDER=gemini

# Agregar tu API key de Gemini
GEMINI_API_KEY=TU_API_KEY_AQUI

# Configuración opcional (con valores por defecto)
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_TIMEOUT=60
GEMINI_MAX_RETRIES=3
```

### 3. Actualizar Dependencias (si es necesario)

El proveedor de Gemini usa `httpx` que ya debería estar instalado. Si no:

```bash
pip install httpx
```

### 4. Reiniciar el Backend

```bash
# Si usas Docker
docker-compose restart backend

# Si ejecutas localmente
# Ctrl+C para detener
python -m backend
```

---

## 🔄 Rollback a Ollama (si es necesario)

Si necesitas volver a usar Ollama, simplemente cambia en `.env`:

```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3
```

---

## 📊 Comparación: Ollama vs Gemini

| Aspecto | Ollama | Gemini |
|---------|--------|--------|
| **Costo** | Gratis (local) | Pago por uso ($) |
| **Velocidad** | Depende del hardware | Muy rápido (Flash) |
| **Privacidad** | 100% local | Datos enviados a Google |
| **Mantenimiento** | Requiere infraestructura | Administrado por Google |
| **Modelos** | Open source (Llama, Phi, etc.) | Gemini Flash & Pro |
| **Calidad** | Buena (depende del modelo) | Excelente |

---

## 🤖 Cómo Funciona la Selección Automática de Modelos

El sistema detecta automáticamente si una consulta requiere análisis de código basándose en palabras clave:

### Palabras Clave que Activan el Modelo Pro:
- `código`, `code`
- `función`, `function`
- `clase`, `class`
- `método`, `method`
- `algoritmo`, `algorithm`
- `complejidad`, `complexity`
- `bug`, `error`, `debug`
- `refactor`, `optimizar`, `optimize`

### Ejemplos:

**Conversación Normal (Flash):**
```
Usuario: "¿Qué es un bucle?"
Sistema: Usa Gemini Flash → Respuesta rápida y clara
```

**Análisis de Código (Pro):**
```
Usuario: "¿Cómo puedo optimizar este algoritmo de ordenamiento?"
Sistema: Detecta "optimizar" + "algoritmo" → Usa Gemini Pro
```

---

## 🔒 Mejoras en el Tutor Socrático

### Nuevas Reglas Estrictas:

El tutor ahora tiene instrucciones **muy claras** para:

1. **NUNCA dar código de programación**
   - ❌ No sintaxis de ningún lenguaje
   - ❌ No fragmentos de código funcional
   - ❌ No pseudocódigo detallado

2. **Solo explicar conceptos**
   - ✅ Explicaciones en lenguaje natural
   - ✅ Preguntas socráticas que guían
   - ✅ Conceptos teóricos y estrategias

3. **Rechazar solicitudes de código**
   - Si el estudiante pide código, el tutor redirige con preguntas
   - Ejemplo: "En vez de darte el código, ayúdame a entender: ¿qué intentaste?"

### Ejemplo de Interacción:

**Antes (podría dar código):**
```
Usuario: "Dame el código para sumar dos números"
Tutor: "Claro, usa: def suma(a, b): return a + b"
```

**Ahora (solo guía):**
```
Usuario: "Dame el código para sumar dos números"
Tutor: "🤔 Antes de escribir código, explicame:
1. ¿Qué entradas necesita tu función?
2. ¿Qué operación matemática querés realizar?
3. ¿Qué resultado esperás obtener?

Contame tu plan en lenguaje natural primero."
```

---

## 🧪 Pruebas

### Verificar que Gemini Funciona:

```python
# test_gemini.py
import asyncio
from backend.llm import LLMProviderFactory, LLMMessage, LLMRole

async def test():
    provider = LLMProviderFactory.create_from_env("gemini")
    
    messages = [
        LLMMessage(role=LLMRole.USER, content="¿Qué es un algoritmo?")
    ]
    
    response = await provider.generate(messages)
    print(f"Modelo: {response.model}")
    print(f"Respuesta: {response.content}")
    print(f"Tokens: {response.usage}")

asyncio.run(test())
```

### Verificar Selección de Modelos:

```python
# Test 1: Conversación normal (debería usar Flash)
messages = [LLMMessage(role=LLMRole.USER, content="Hola, ¿cómo estás?")]
response = await provider.generate(messages, is_code_analysis=False)
# response.model == "gemini-1.5-flash"

# Test 2: Análisis de código (debería usar Pro)
messages = [LLMMessage(role=LLMRole.USER, content="Analiza este código")]
response = await provider.generate(messages, is_code_analysis=True)
# response.model == "gemini-1.5-pro"
```

---

## 💰 Costos Estimados

**Gemini API Pricing (aproximado):**

| Modelo | Input (1M tokens) | Output (1M tokens) |
|--------|------------------|-------------------|
| Flash  | $0.075          | $0.30             |
| Pro    | $1.25           | $5.00             |

**Ejemplo de uso mensual moderado:**
- 1,000 conversaciones/mes
- ~500 tokens por conversación
- Costo estimado: **$5-15/mes**

*Nota: Precios sujetos a cambios. Verifica en: https://ai.google.dev/pricing*

---

## 🛠️ Troubleshooting

### Error: "GEMINI_API_KEY is required"
**Solución:** Verifica que tu `.env` tiene `GEMINI_API_KEY=tu_key_aqui`

### Error: 429 (Rate Limit)
**Solución:** 
- Espera 1 minuto y reintenta
- Considera aumentar `GEMINI_MAX_RETRIES`
- Verifica límites de tu API key en Google Cloud Console

### Error: 401 (Unauthorized)
**Solución:** 
- Verifica que tu API key es válida
- Regenera la key en https://makersuite.google.com/app/apikey

### El tutor sigue dando código
**Solución:**
- Verifica que estás usando la versión actualizada de `ai_gateway.py`
- Los prompts actualizados están en `backend/core/ai_gateway.py` y `backend/agents/tutor_prompts.py`

---

## 📝 Archivos Modificados

### Nuevos Archivos:
- `backend/llm/gemini_provider.py` - Proveedor de Gemini

### Archivos Actualizados:
- `backend/llm/factory.py` - Registro del proveedor Gemini
- `backend/core/ai_gateway.py` - Selección automática de modelos y prompts mejorados
- `backend/agents/tutor_prompts.py` - Prompts reforzados anti-código
- `.env.example` - Configuración de Gemini

---

## ✅ Checklist de Migración

- [ ] Obtener API key de Gemini
- [ ] Actualizar `.env` con `LLM_PROVIDER=gemini`
- [ ] Agregar `GEMINI_API_KEY` al `.env`
- [ ] Verificar que `httpx` está instalado
- [ ] Reiniciar el backend
- [ ] Probar una conversación normal (debería usar Flash)
- [ ] Probar análisis de código (debería usar Pro)
- [ ] Verificar que el tutor NO da código

---

## 🎓 Filosofía del Tutor

El tutor ha sido diseñado con una filosofía pedagógica estricta:

> **"No te doy el pescado, te enseño a pescar"**

- ❌ No resolver el problema por el estudiante
- ✅ Guiar el razonamiento con preguntas
- ✅ Fomentar la explicitación del pensamiento
- ✅ Reforzar conceptos teóricos
- ✅ Promover la autonomía y el aprendizaje profundo

---

## 📞 Soporte

Si tienes problemas con la migración:
1. Verifica la sección Troubleshooting
2. Revisa los logs del backend
3. Prueba con Ollama temporalmente para descartar otros problemas
4. Verifica que tu API key de Gemini tiene cuota disponible

---

**¡Migración completada! 🎉**

El sistema ahora usa Gemini API para respuestas más rápidas y precisas, con un tutor que realmente enseña en vez de solo dar respuestas.
