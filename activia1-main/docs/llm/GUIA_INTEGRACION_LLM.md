# Guía de Integración de LLM Providers

**Fecha**: 2025-11-19
**Versión**: 1.0

---

## Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura de Abstracción LLM](#arquitectura-de-abstracción-llm)
3. [Configuración Rápida](#configuración-rápida)
4. [Proveedores Disponibles](#proveedores-disponibles)
5. [Uso en Modo CLI](#uso-en-modo-cli)
6. [Uso en Modo API](#uso-en-modo-api)
7. [Guía de Migración](#guía-de-migración)
8. [Consideraciones de Costo](#consideraciones-de-costo)
9. [Troubleshooting](#troubleshooting)
10. [Mejores Prácticas](#mejores-prácticas)

---

## Resumen Ejecutivo

El sistema AI-Native MVP implementa **abstracción completa de proveedores LLM**, permitiendo cambiar entre diferentes modelos (Mock, OpenAI GPT-4, Google Gemini, Anthropic Claude) sin modificar código.

**Características clave**:
- ✅ Abstracción mediante patrón **Factory + Strategy**
- ✅ Configuración mediante **variables de entorno**
- ✅ Soporte para **Mock** (default, sin API calls)
- ✅ Soporte para **OpenAI** (GPT-4, GPT-3.5-turbo)
- ✅ Soporte para **Google Gemini** (1.5 Pro/Flash, GRATIS)
- ✅ Soporte para **Anthropic Claude** (preparado, requiere implementación completa)
- ✅ **Fallback automático** a Mock si falla configuración
- ✅ **Streaming** y **conteo de tokens** incluidos

**Casos de uso**:
- **Desarrollo**: Mock provider (gratis, sin API calls)
- **Testing**: Mock provider con respuestas predecibles
- **Producción económica**: Google Gemini 1.5 Flash (GRATIS hasta límites generosos)
- **Producción premium**: OpenAI GPT-4 o Claude con API keys reales

---

## Arquitectura de Abstracción LLM

### Patrón de Diseño

```
┌─────────────────────────────────────────────────────────────┐
│                    LLMProviderFactory                        │
│  (Factory Pattern - Centraliza creación de providers)       │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ├──────┬──────────┬──────────┬─────────┐
                 │      │          │          │         │
        ┌────────▼──┐ ┌─▼────────┐ ┌─▼──────┐ ┌───▼────┐
        │ LLMBase   │ │MockLLM   │ │OpenAI  │ │Anthrop.│
        │ (Abstract)│ │Provider  │ │Provider│ │Provider│
        └───────────┘ └──────────┘ └────────┘ └────────┘
                 │          │          │          │
                 │          │          │          │
        ┌────────▼──────────▼──────────▼──────────▼────────┐
        │          Interfaz Común (Strategy Pattern)        │
        │  - generate(messages, temperature, ...)           │
        │  - generate_stream(messages, ...)                 │
        │  - count_tokens(text)                             │
        │  - validate_config()                              │
        │  - get_model_info()                               │
        └───────────────────────────────────────────────────┘
```

### Componentes Clave

**1. LLMProvider (Base Abstract Class)**
- Ubicación: `src/ai_native_mvp/llm/base.py`
- Define interfaz común para todos los providers
- Métodos abstractos: `generate()`, `generate_stream()`, `count_tokens()`

**2. LLMProviderFactory**
- Ubicación: `src/ai_native_mvp/llm/factory.py`
- Crea instancias de providers según configuración
- Soporta creación desde variables de entorno con `create_from_env()`

**3. Providers Concretos**
- **MockLLMProvider**: `src/ai_native_mvp/llm/mock.py`
- **OpenAIProvider**: `src/ai_native_mvp/llm/openai_provider.py`
- **AnthropicProvider**: (futuro) `src/ai_native_mvp/llm/anthropic_provider.py`

**4. Dependency Injection (FastAPI)**
- Ubicación: `src/ai_native_mvp/api/deps.py`
- Función `_initialize_llm_provider()` lee variables de entorno
- Provider se cachea como singleton (stateless, seguro)

---

## Configuración Rápida

### Paso 1: Copiar archivo de ejemplo

```bash
cp .env.example .env
```

### Paso 2: Editar .env

```bash
# Modo desarrollo (gratis, sin API calls)
LLM_PROVIDER=mock

# O modo producción con OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
```

### Paso 3: Instalar dependencias (solo si usas OpenAI)

```bash
pip install openai tiktoken
# Ya incluidos en requirements.txt
```

### Paso 4: Verificar configuración

```bash
# Ejecutar script de ejemplo
python examples/ejemplo_openai_integration.py
```

---

## Proveedores Disponibles

### 1. Mock Provider (Default)

**Propósito**: Desarrollo y testing sin API calls

**Ventajas**:
- ✅ Gratis (sin costos de API)
- ✅ Rápido (sin latencia de red)
- ✅ Predecible (respuestas basadas en keywords)
- ✅ No requiere API key

**Limitaciones**:
- ❌ Respuestas simplificadas (no usa LLM real)
- ❌ No aprende de contexto complejo
- ❌ Limitado a patrones predefinidos

**Configuración**:
```bash
LLM_PROVIDER=mock
# No requiere más configuración
```

**Uso**:
```python
from src.ai_native_mvp.llm import LLMProviderFactory

provider = LLMProviderFactory.create("mock")
```

---

### 2. OpenAI Provider (GPT-4, GPT-3.5)

**Propósito**: Producción con modelos de OpenAI

**Modelos soportados**:
- `gpt-4` - Mejor calidad, más caro (~$0.03/1K input tokens)
- `gpt-4-turbo` - Más rápido, menor costo
- `gpt-3.5-turbo` - Económico, buena calidad (~10x más barato que GPT-4)

**Configuración**:

```bash
# 1. Obtener API key en: https://platform.openai.com/api-keys
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...

# 2. Elegir modelo
OPENAI_MODEL=gpt-4  # o gpt-3.5-turbo

# 3. Configuraciones opcionales
OPENAI_TEMPERATURE=0.7       # 0.0 (determinístico) a 1.0 (creativo)
OPENAI_MAX_TOKENS=2000       # Límite de tokens por respuesta
OPENAI_ORGANIZATION=org-...  # Solo si usas múltiples organizaciones
```

**Uso programático**:

```python
from src.ai_native_mvp.llm import LLMProviderFactory, LLMMessage, LLMRole

# Crear desde variables de entorno
provider = LLMProviderFactory.create_from_env("openai")

# O crear manualmente
provider = LLMProviderFactory.create("openai", {
    "api_key": "sk-proj-...",
    "model": "gpt-4",
    "temperature": 0.7
})

# Generar respuesta
messages = [
    LLMMessage(role=LLMRole.SYSTEM, content="Eres un tutor cognitivo"),
    LLMMessage(role=LLMRole.USER, content="¿Qué es una cola circular?")
]

response = provider.generate(messages, temperature=0.7)
print(response.content)

# Ver métricas
print(f"Tokens usados: {response.usage['total_tokens']}")
```

**Streaming** (para UI en tiempo real):

```python
for chunk in provider.generate_stream(messages):
    print(chunk, end="", flush=True)
```

**Conteo de tokens**:

```python
tokens = provider.count_tokens("Texto a contar")
print(f"Tokens: {tokens}")
```

---

### 3. Google Gemini Provider (1.5 Pro/Flash) - ¡NUEVO!

**Propósito**: Producción económica con API gratuita

**Modelos soportados**:
- `gemini-1.5-flash` - Muy rápido, económico, 2M token context (RECOMENDADO)
- `gemini-1.5-pro` - Alta calidad, 2M token context
- `gemini-pro` - Versión anterior, 32K context

**Ventajas**:
- ✅ **COMPLETAMENTE GRATIS** hasta límites generosos:
  - Gemini 1.5 Flash: 60 requests/min, 1M tokens/día
  - Gemini 1.5 Pro: 2 requests/min, 32K tokens/día
- ✅ **Sin tarjeta de crédito** requerida
- ✅ **Contexto enorme**: 2M tokens (vs 128K de GPT-4)
- ✅ **Muy rápido**: Gemini 1.5 Flash es más rápido que GPT-3.5
- ✅ **Multimodal**: Soporta texto, imágenes, video

**Configuración**:

```bash
# 1. Obtener API key GRATIS en: https://makersuite.google.com/app/apikey
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...

# 2. Elegir modelo (recomendado: flash para velocidad)
GEMINI_MODEL=gemini-1.5-flash  # o gemini-1.5-pro

# 3. Configuraciones opcionales
GEMINI_TEMPERATURE=0.7       # 0.0 (determinístico) a 1.0 (creativo)
GEMINI_MAX_TOKENS=8192       # Límite de tokens por respuesta
```

**Uso programático**:

```python
from src.ai_native_mvp.llm import LLMProviderFactory, LLMMessage, LLMRole

# Crear desde variables de entorno
provider = LLMProviderFactory.create_from_env("gemini")

# O crear manualmente
provider = LLMProviderFactory.create("gemini", {
    "api_key": "AIzaSy...",
    "model": "gemini-1.5-flash"
})

# Generar respuesta (igual que OpenAI)
messages = [
    LLMMessage(role=LLMRole.SYSTEM, content="Eres un tutor cognitivo"),
    LLMMessage(role=LLMRole.USER, content="¿Qué es una cola circular?")
]

response = provider.generate(messages, temperature=0.7)
print(response.content)

# Ver métricas
print(f"Tokens usados: {response.usage['total_tokens']}")
print(f"Costo: $0.00 (GRATIS)")
```

**Streaming y conteo de tokens**:
- ✅ Soporta `generate_stream()` para UI en tiempo real
- ✅ Soporta `count_tokens()` usando API nativa de Gemini

**Cuándo usar Gemini**:
- ✅ **Desarrollo y testing** (gratis, sin límites restrictivos)
- ✅ **Producción de bajo volumen** (hasta 60 req/min)
- ✅ **Tareas que requieren contexto grande** (2M tokens)
- ✅ **Presupuesto limitado** (totalmente gratuito)

Ver ejemplo completo en: `examples/ejemplo_gemini_integration.py`

---

### 4. Anthropic Provider (Claude)

**Estado**: Preparado pero requiere implementación completa

**Configuración prevista**:

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

**TODO**: Implementar `anthropic_provider.py` siguiendo patrón de OpenAI

---

## Uso en Modo CLI

### Con Mock Provider (default)

```python
# examples/ejemplo_basico.py (ya usa Mock por defecto)
from src.ai_native_mvp.core.ai_gateway import AIGateway

gateway = AIGateway()  # Usa Mock provider interno
result = gateway.process_interaction(
    session_id="...",
    prompt="¿Qué es una cola?"
)
```

### Con OpenAI

```python
from dotenv import load_dotenv
load_dotenv()  # Cargar .env

from src.ai_native_mvp.llm import LLMProviderFactory
from src.ai_native_mvp.core.ai_gateway import AIGateway
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import *

# Crear provider OpenAI desde .env
llm_provider = LLMProviderFactory.create_from_env("openai")

# Inyectar en Gateway
with get_db_session() as db:
    session_repo = SessionRepository(db)
    trace_repo = TraceRepository(db)
    # ... otros repos

    gateway = AIGateway(
        llm_provider=llm_provider,  # ¡OpenAI en lugar de Mock!
        session_repo=session_repo,
        trace_repo=trace_repo,
        # ... otros repos
    )

    # Usar normalmente
    session_id = gateway.create_session(...)
    result = gateway.process_interaction(...)
```

Ver ejemplo completo en: `examples/ejemplo_openai_integration.py`

---

## Uso en Modo API

El servidor FastAPI **automáticamente** lee `LLM_PROVIDER` desde `.env`.

### Configuración

1. **Editar `.env`**:
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-...
   OPENAI_MODEL=gpt-4
   ```

2. **Iniciar servidor**:
   ```bash
   python scripts/run_api.py
   ```

3. **Verificar en logs**:
   ```
   [INFO] LLM Provider inicializado: openai
   [INFO] Modelo: gpt-4
   ```

### Cómo Funciona (Internamente)

El archivo `src/ai_native_mvp/api/deps.py` contiene:

```python
def _initialize_llm_provider():
    """Lee LLM_PROVIDER desde .env y crea provider"""
    load_dotenv()
    provider_type = os.getenv("LLM_PROVIDER", "mock")
    return LLMProviderFactory.create_from_env(provider_type)

def get_ai_gateway(...):
    """Dependency injection - crea Gateway con provider correcto"""
    global _llm_provider_instance
    if _llm_provider_instance is None:
        _llm_provider_instance = _initialize_llm_provider()

    return AIGateway(llm_provider=_llm_provider_instance, ...)
```

**Beneficios**:
- ✅ **Cero cambios de código** para cambiar provider
- ✅ **Singleton pattern** (provider se reutiliza entre requests)
- ✅ **Fallback automático** a Mock si falla configuración

### Cambiar Provider en Caliente

**Para desarrollo local**:
1. Editar `.env`: cambiar `LLM_PROVIDER=mock` a `LLM_PROVIDER=openai`
2. Reiniciar servidor: `Ctrl+C` y `python scripts/run_api.py`
3. El nuevo provider se carga automáticamente

**Para producción**:
- Usar variables de entorno del sistema (no `.env`)
- Reiniciar servicio tras cambios

---

## Guía de Migración

### Escenario 1: De Mock a OpenAI (Desarrollo → Producción)

**Antes (Mock)**:
```bash
# .env
LLM_PROVIDER=mock
```

**Después (OpenAI)**:
```bash
# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4
```

**Código**: Sin cambios necesarios ✅

---

### Escenario 2: De GPT-4 a GPT-3.5 (Reducir costos)

```bash
# Antes
OPENAI_MODEL=gpt-4          # $0.03/1K input tokens

# Después
OPENAI_MODEL=gpt-3.5-turbo  # $0.0015/1K input tokens (~20x más barato)
```

**Código**: Sin cambios necesarios ✅

---

### Escenario 3: Usar diferentes modelos por endpoint (Avanzado)

**TODO**: Requiere modificar `deps.py` para aceptar parámetro opcional de modelo

Idea:
```python
# En request body
{
  "prompt": "...",
  "preferred_model": "gpt-3.5-turbo"  # Override del modelo default
}
```

---

## Consideraciones de Costo

### Google Gemini (¡GRATIS!)

**Pricing** (a Nov 2025):
- **Gemini 1.5 Flash**: GRATIS hasta 60 requests/min, 1M tokens/día
- **Gemini 1.5 Pro**: GRATIS hasta 2 requests/min, 32K tokens/día

**Ejemplo típico** (interacción de tutoría):
- Prompt sistema: ~100 tokens
- Prompt usuario: ~50 tokens
- Respuesta: ~200 tokens
- **Costo**: $0.00 USD ✅

**Estimación mensual** (100 estudiantes, 20 interacciones c/u):
- Total interacciones: 2,000
- **Costo total**: $0.00 USD ✅
- **Requiere**: Solo API key (sin tarjeta de crédito)

**Límites**:
- **Gemini 1.5 Flash**: 60 req/min = 3,600 req/hora = ~86,400 req/día
- **Suficiente para**: Hasta ~400 estudiantes activos con 20 interacciones/día c/u

---

### OpenAI GPT-4

**Pricing** (a Nov 2025):
- Input: $0.03 por 1,000 tokens
- Output: $0.06 por 1,000 tokens

**Ejemplo típico** (interacción de tutoría):
- Prompt sistema: ~100 tokens
- Prompt usuario: ~50 tokens
- Respuesta: ~200 tokens
- **Costo**: ~$0.015 por interacción

**Estimación mensual** (100 estudiantes, 20 interacciones c/u):
- Total interacciones: 2,000
- **Costo total**: ~$30/mes

---

### OpenAI GPT-3.5-turbo

**Pricing**:
- Input: $0.0015 por 1,000 tokens
- Output: $0.002 por 1,000 tokens

**Mismo ejemplo**:
- **Costo**: ~$0.0007 por interacción (~20x más barato que GPT-4)

**Estimación mensual** (100 estudiantes):
- **Costo total**: ~$1.40/mes

---

### Tabla Comparativa de Costos

| Provider | Costo/interacción | 100 estudiantes (mes) | Límites | Calidad |
|----------|-------------------|------------------------|---------|---------|
| **Mock** | $0.00 | $0.00 | Ilimitado | Baja (respuestas simples) |
| **Gemini 1.5 Flash** | $0.00 | $0.00 | 60 req/min | Alta (más rápido que GPT-3.5) |
| **Gemini 1.5 Pro** | $0.00 | $0.00 | 2 req/min | Muy alta (contexto 2M tokens) |
| **GPT-3.5-turbo** | ~$0.0007 | ~$1.40 | Según tier | Buena |
| **GPT-4** | ~$0.015 | ~$30.00 | Según tier | Excelente |

---

### Recomendaciones de Costo

1. **Desarrollo**: Usar Mock (gratis, sin latencia)
2. **Testing y Producción inicial**: **Usar Gemini 1.5 Flash** (gratis, muy buena calidad)
3. **Producción de alto volumen**: Gemini 1.5 Flash (hasta 60 req/min gratis)
4. **Producción premium**: GPT-4 solo para tareas críticas
5. **Híbrido**: Gemini para mayoría, GPT-4 para evaluaciones complejas

**Estrategia recomendada 2025**:
```python
# Nueva recomendación considerando Gemini
if interaction_type == "simple_question" or interaction_type == "tutorial":
    model = "gemini-1.5-flash"  # GRATIS, rápido
elif interaction_type == "evaluation" and complexity == "high":
    model = "gpt-4"  # Premium para evaluaciones críticas
else:
    model = "gemini-1.5-flash"  # Default: Gemini (GRATIS)
```

**Estrategia híbrida** (requiere lógica custom):
```python
# Pseudo-código
if interaction_type == "simple_question":
    model = "gpt-3.5-turbo"
elif interaction_type == "evaluation" or interaction_type == "complex":
    model = "gpt-4"
```

---

## Troubleshooting

### Error: "OPENAI_API_KEY environment variable is required"

**Causa**: Variable de entorno no configurada

**Solución**:
1. Verificar que `.env` existe: `ls -la .env`
2. Verificar contenido: `cat .env | grep OPENAI_API_KEY`
3. Verificar que `python-dotenv` está instalado: `pip install python-dotenv`
4. Verificar que script llama `load_dotenv()`:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # DEBE ir antes de importar código del proyecto
   ```

---

### Error: "OpenAI package not installed"

**Causa**: Paquete `openai` faltante

**Solución**:
```bash
pip install openai tiktoken
```

---

### Error: "Rate limit exceeded" (429)

**Causa**: Excediste límite de requests de OpenAI

**Soluciones**:
1. **Upgrade tier**: OpenAI tiene límites según tier de cuenta
2. **Implementar rate limiting**:
   ```python
   import time
   time.sleep(1)  # Esperar entre requests
   ```
3. **Usar exponential backoff**:
   ```python
   from openai import OpenAI
   client = OpenAI(max_retries=3)  # Retry automático
   ```

---

### Servidor API usa Mock en lugar de OpenAI

**Causa**: El servidor no encuentra la configuración de OpenAI

**Verificación**:
```bash
# Ver logs al iniciar servidor
python scripts/run_api.py

# Buscar línea:
[INFO] LLM Provider inicializado: openai  # ✅ Correcto
# o
[WARN] Usando Mock provider as fallback    # ❌ Falló configuración
```

**Solución**:
1. Verificar que `.env` está en el directorio raíz del proyecto
2. Verificar que `OPENAI_API_KEY` tiene valor válido
3. Reiniciar servidor completamente

---

## Mejores Prácticas

### 1. Gestión de API Keys

```bash
# ❌ MAL: Hardcodear en código
provider = OpenAIProvider({"api_key": "sk-proj-abc123"})

# ✅ BIEN: Variables de entorno
provider = LLMProviderFactory.create_from_env("openai")
```

**Seguridad**:
- Nunca comitear `.env` a Git
- Usar `.gitignore` para excluir `.env`
- En producción, usar secrets manager (AWS Secrets Manager, etc.)

---

### 2. Manejo de Errores

```python
try:
    provider = LLMProviderFactory.create_from_env("openai")
except ValueError as e:
    # API key faltante
    logger.error(f"LLM config error: {e}")
    provider = LLMProviderFactory.create("mock")  # Fallback
except ImportError as e:
    # Paquete faltante
    logger.error(f"LLM package missing: {e}")
    provider = LLMProviderFactory.create("mock")  # Fallback
```

---

### 3. Logging y Monitoring

```python
# Log cada request a OpenAI
response = provider.generate(messages)
logger.info(f"OpenAI request: {response.usage['total_tokens']} tokens")

# Monitor costos
cost = calculate_cost(response.usage)
logger.info(f"Request cost: ${cost:.4f}")
```

**Métricas clave**:
- Total de tokens consumidos
- Costo acumulado
- Latencia promedio
- Tasa de errores

---

### 4. Optimización de Prompts

**Reducir costos** sin perder calidad:

```python
# ❌ MAL: Prompt verboso
system_prompt = """
Eres un tutor muy inteligente que ayuda a estudiantes de programación.
Debes responder de forma clara, concisa y pedagógica.
Nunca des soluciones completas, solo guía al estudiante.
Usa el método socrático para hacer preguntas.
...
"""  # 150+ tokens

# ✅ BIEN: Prompt conciso
system_prompt = "Tutor cognitivo: guía con preguntas socráticas, no des soluciones completas."
# 20 tokens (~87% reducción)
```

---

### 5. Caching de Respuestas

Para preguntas frecuentes:

```python
import hashlib

cache = {}

def generate_with_cache(messages, temperature):
    # Hash del input
    key = hashlib.md5(str(messages).encode()).hexdigest()

    if key in cache:
        return cache[key]  # Respuesta cacheada (gratis)

    # Generar con LLM (cuesta dinero)
    response = provider.generate(messages, temperature)
    cache[key] = response
    return response
```

---

## Roadmap Futuro

### Corto plazo
- ✅ OpenAI GPT-4 integrado
- ⏳ Anthropic Claude integration
- ⏳ Ollama (modelos locales) integration

### Mediano plazo
- ⏳ Modelo híbrido (GPT-3.5 + GPT-4 según complejidad)
- ⏳ Rate limiting y retry logic
- ⏳ Caching de respuestas
- ⏳ Monitoring dashboard (costos, uso, latencia)

### Largo plazo
- ⏳ Fine-tuning de modelos específicos para pedagogía
- ⏳ Embeddings para búsqueda semántica en documentación
- ⏳ Multi-model ensembles (combinar varios LLMs)

---

## Apéndice: Variables de Entorno Completas

```bash
# ============================================================================
# LLM PROVIDER CONFIGURATION
# ============================================================================

# Provider type: mock, openai, gemini, anthropic
LLM_PROVIDER=mock

# ----------------------------------------------------------------------------
# OpenAI (GPT-4, GPT-3.5)
# ----------------------------------------------------------------------------
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-4                 # gpt-4, gpt-4-turbo, gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7             # 0.0 to 1.0
OPENAI_MAX_TOKENS=2000             # Optional, max tokens per response
OPENAI_ORGANIZATION=org-...        # Optional, for multiple orgs

# ----------------------------------------------------------------------------
# Google Gemini (1.5 Pro/Flash) - GRATIS
# ----------------------------------------------------------------------------
GEMINI_API_KEY=AIzaSy...
GEMINI_MODEL=gemini-1.5-flash      # gemini-1.5-flash, gemini-1.5-pro, gemini-pro
GEMINI_TEMPERATURE=0.7             # 0.0 to 1.0
GEMINI_MAX_TOKENS=8192             # Optional, max tokens per response

# ----------------------------------------------------------------------------
# Anthropic (Claude)
# ----------------------------------------------------------------------------
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-sonnet-20240229  # or opus, haiku

# ----------------------------------------------------------------------------
# Ollama (Local models)
# ----------------------------------------------------------------------------
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

---

**Autor**: Claude Code (Sonnet 4.5)
**Fecha**: 2025-11-19
**Versión**: 1.0

---

## Contacto y Soporte

Para preguntas o issues:
- GitHub Issues: https://github.com/tu-repo/issues
- Documentación API: http://localhost:8000/docs (con servidor corriendo)
- Documentación MVP: `README_MVP.md`