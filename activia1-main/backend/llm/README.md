# Sistema LLM - Proveedores Múltiples

Este directorio contiene la implementación de proveedores de Large Language Models (LLM) para el sistema AI-Native.

## 🎯 Arquitectura

El sistema usa el patrón **Factory** para soportar múltiples proveedores de LLM de forma intercambiable:

```
┌─────────────────────────────────────────┐
│        LLMProviderFactory               │
├─────────────────────────────────────────┤
│  + create(type, config)                 │
│  + create_from_env()                    │
│  + register_provider()                  │
└───────────────┬─────────────────────────┘
                │
        ┌───────┴───────┐
        │               │
┌───────▼──────┐ ┌─────▼────────┐
│ GeminiProvider│ │OllamaProvider│
├──────────────┤ ├──────────────┤
│ - Flash      │ │ - Llama2     │
│ - Pro        │ │ - Phi3       │
│ (Auto switch)│ │ - Mistral    │
└──────────────┘ └──────────────┘
```

## 📦 Proveedores Disponibles

### 1. **Gemini** (Recomendado) 🌟

**Características:**
- ✅ API de Google (cloud-based)
- ✅ Dos modelos: Flash (rápido) y Pro (avanzado)
- ✅ Selección automática según tipo de tarea
- ✅ Excelente calidad de respuestas
- ✅ Soporte para streaming
- ✅ Alta velocidad de respuesta

**Modelos:**
- `gemini-1.5-flash`: Conversaciones normales, tutorías, preguntas
- `gemini-1.5-pro`: Análisis de código, debugging, tareas complejas

**Configuración:**
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=tu_api_key
GEMINI_MODEL=gemini-1.5-flash  # Modelo por defecto
GEMINI_TEMPERATURE=0.7
```

**Uso:**
```python
from backend.llm import LLMProviderFactory, LLMMessage, LLMRole

# Crear provider desde variables de entorno
provider = LLMProviderFactory.create_from_env()

# Conversación normal (usa Flash automáticamente)
messages = [LLMMessage(role=LLMRole.USER, content="¿Qué es un bucle?")]
response = await provider.generate(messages, is_code_analysis=False)

# Análisis de código (usa Pro automáticamente)
messages = [LLMMessage(role=LLMRole.USER, content="Analiza este algoritmo...")]
response = await provider.generate(messages, is_code_analysis=True)
```

### 2. **Ollama** (Local, Privado)

**Características:**
- ✅ Ejecución local (sin enviar datos a la nube)
- ✅ Gratis (sin costos por token)
- ✅ Múltiples modelos open-source
- ✅ Privacidad total
- ⚠️ Requiere hardware potente
- ⚠️ Más lento que Gemini

**Modelos soportados:**
- `phi3`: Microsoft Phi-3 (rápido, 3.8B params)
- `llama2`: Meta Llama 2 (buena calidad)
- `mistral`: Mistral AI (equilibrado)
- `codellama`: Especializado en código

**Configuración:**
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3
OLLAMA_TEMPERATURE=0.7
OLLAMA_TIMEOUT=120
```

### 3. **Mock** (Testing)

**Características:**
- ✅ Para pruebas y desarrollo
- ✅ No requiere API keys
- ✅ Respuestas predefinidas
- ⚠️ Solo para testing, no producción

**Configuración:**
```bash
LLM_PROVIDER=mock
```

## 🔄 Selección Automática de Modelos (Gemini)

El sistema **detecta automáticamente** cuándo usar cada modelo:

### Palabras Clave que Activan Gemini Pro:

- Código: `código`, `code`, `función`, `function`, `class`, `método`
- Algoritmos: `algoritmo`, `algorithm`, `complejidad`, `complexity`
- Debugging: `bug`, `error`, `debug`, `refactor`
- Optimización: `optimizar`, `optimize`

### Flujo de Decisión:

```
User Input
    │
    ├─ Contiene palabras clave de código?
    │
    ├─ SÍ → Gemini Pro (análisis profundo)
    │
    └─ NO → Gemini Flash (rápido, económico)
```

## 📋 Interface Base

Todos los proveedores implementan la interface `LLMProvider`:

```python
class LLMProvider(ABC):
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generar respuesta"""
        pass

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generar respuesta en streaming"""
        pass

    def count_tokens(self, text: str) -> int:
        """Contar tokens en texto"""
        pass
```

## 🔧 Uso Avanzado

### Crear Provider Manualmente:

```python
from backend.llm import LLMProviderFactory

# Gemini con configuración personalizada
provider = LLMProviderFactory.create("gemini", {
    "api_key": "tu_api_key",
    "model": "gemini-1.5-pro",  # Forzar Pro
    "temperature": 0.5,
    "timeout": 30
})

# Ollama con modelo personalizado
provider = LLMProviderFactory.create("ollama", {
    "base_url": "http://localhost:11434",
    "model": "codellama",
    "temperature": 0.3
})
```

### Usar Streaming:

```python
async for chunk in provider.generate_stream(messages):
    print(chunk, end="", flush=True)
```

### Parámetros Adicionales:

```python
response = await provider.generate(
    messages,
    temperature=0.7,       # Creatividad (0.0-1.0)
    max_tokens=500,        # Límite de tokens
    is_code_analysis=True  # Gemini: forzar modelo Pro
)
```

## 📊 Métricas y Monitoreo

Cada proveedor reporta métricas automáticamente:

```python
# Las métricas están en response.usage
{
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
}

# También se registran en Prometheus (si está configurado)
llm_requests_total{provider="gemini", model="flash", status="success"}
llm_tokens_total{provider="gemini", model="flash", type="prompt"}
```

## 🔐 Seguridad

### API Keys:

- **Gemini**: Guardar en `.env`, nunca en código
- **Ollama**: No requiere API key
- Usar variables de entorno para todas las configuraciones sensibles

### Rate Limiting:

- Gemini: Implementa retry automático con backoff exponencial
- Ollama: Sin límites (local)

### Validación:

```python
# El factory valida la configuración automáticamente
try:
    provider = LLMProviderFactory.create_from_env("gemini")
except ValueError as e:
    print(f"Configuración inválida: {e}")
```

## 🧪 Testing

### Test Rápido:

```python
# tests/test_llm_providers.py
import pytest
from backend.llm import LLMProviderFactory, LLMMessage, LLMRole

@pytest.mark.asyncio
async def test_gemini_provider():
    provider = LLMProviderFactory.create("gemini", {
        "api_key": "test_key",
        "model": "gemini-1.5-flash"
    })
    
    messages = [LLMMessage(role=LLMRole.USER, content="Test")]
    response = await provider.generate(messages)
    
    assert response.content
    assert response.model == "gemini-1.5-flash"
    assert response.usage["total_tokens"] > 0
```

### Test de Selección de Modelo:

```python
@pytest.mark.asyncio
async def test_model_selection():
    provider = LLMProviderFactory.create_from_env("gemini")
    
    # Conversación normal → Flash
    messages = [LLMMessage(role=LLMRole.USER, content="Hola")]
    response = await provider.generate(messages, is_code_analysis=False)
    assert response.model == "gemini-1.5-flash"
    
    # Análisis de código → Pro
    messages = [LLMMessage(role=LLMRole.USER, content="Analiza código")]
    response = await provider.generate(messages, is_code_analysis=True)
    assert response.model == "gemini-1.5-pro"
```

## 📚 Archivos

```
backend/llm/
├── __init__.py           # Exports principales
├── base.py               # Interface LLMProvider
├── factory.py            # Factory para crear providers
├── gemini_provider.py    # Implementación Gemini ⭐
├── ollama_provider.py    # Implementación Ollama
├── mock.py               # Mock provider (testing)
└── README.md             # Esta documentación
```

## 🚀 Mejores Prácticas

1. **Usar Factory Pattern:**
   ```python
   # ✅ Correcto
   provider = LLMProviderFactory.create_from_env()
   
   # ❌ Evitar
   provider = GeminiProvider({"api_key": "..."})
   ```

2. **Manejar Errores:**
   ```python
   try:
       response = await provider.generate(messages)
   except httpx.HTTPStatusError as e:
       logger.error(f"LLM error: {e}")
       # Implementar fallback
   ```

3. **Configurar desde ENV:**
   ```python
   # ✅ Correcto
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=...
   
   # ❌ Evitar hardcodear
   provider = create("gemini", {"api_key": "sk-..."})
   ```

4. **Optimizar Costos (Gemini):**
   - Usar `is_code_analysis=False` cuando sea posible (Flash es más barato)
   - Cachear respuestas comunes
   - Limitar `max_tokens` apropiadamente

## 💡 Troubleshooting

### "Unknown provider type"
**Causa:** Provider no registrado
**Solución:** Verificar que el provider está en `factory.py`

### "GEMINI_API_KEY is required"
**Causa:** Falta API key en `.env`
**Solución:** Agregar `GEMINI_API_KEY=tu_key` en `.env`

### Respuestas lentas
**Causa:** Timeout muy alto o red lenta
**Solución:** Ajustar `GEMINI_TIMEOUT` o usar Ollama local

### Errores 429 (Rate Limit)
**Causa:** Demasiadas peticiones
**Solución:** Implementar rate limiting local o aumentar cuota

## 🔄 Changelog

### v2.0 (Actual)
- ✅ Soporte para Gemini API
- ✅ Selección automática Flash/Pro
- ✅ Prompts mejorados anti-código
- ✅ Detección inteligente de tareas

### v1.0
- Soporte básico para Ollama
- Mock provider para testing

---

**Próximos Pasos:**
1. Configurar tu API key de Gemini
2. Actualizar `.env` con `LLM_PROVIDER=gemini`
3. Probar el sistema con `test_gemini.py`
4. Ver `MIGRACION_GEMINI.md` para guía completa
