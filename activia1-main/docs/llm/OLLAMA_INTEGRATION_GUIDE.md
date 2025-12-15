# Guía de Integración Ollama - Phoenix MVP

## 📋 Índice
1. [¿Qué es Ollama?](#qué-es-ollama)
2. [Instalación](#instalación)
3. [Configuración](#configuración)
4. [Uso](#uso)
5. [Modelos Disponibles](#modelos-disponibles)
6. [Docker Deployment](#docker-deployment)
7. [Troubleshooting](#troubleshooting)
8. [Comparación con otros Proveedores](#comparación)

---

## 🤖 ¿Qué es Ollama?

**Ollama** es un framework ligero para ejecutar modelos de lenguaje (LLMs) **localmente** en tu infraestructura. 

### Ventajas
- ✅ **100% Local**: Sin envío de datos a servicios externos
- ✅ **Sin API Keys**: No necesita claves de acceso
- ✅ **Privacidad Total**: Datos sensibles nunca salen de tu servidor
- ✅ **Sin Costos por Token**: No hay cargos por uso
- ✅ **Offline**: Funciona sin conexión a Internet
- ✅ **Modelos Open Source**: Llama 2, Mistral, Gemma, Code Llama, etc.

### Casos de Uso Ideales
- 🏥 **Sector Salud**: Datos médicos sensibles (HIPAA compliance)
- 🏦 **Sector Financiero**: Información confidencial de clientes
- 🏭 **Empresas**: Código propietario, documentación interna
- 🎓 **Educación**: Privacidad de estudiantes (FERPA)
- 🧪 **Desarrollo/Testing**: Entorno local sin costos

---

## 📦 Instalación

### Windows

```powershell
# Descargar instalador oficial
# https://ollama.ai/download/windows

# Ejecutar instalador
# El servicio se inicia automáticamente
```

### Linux

```bash
# Instalación con un comando
curl -fsSL https://ollama.ai/install.sh | sh

# Verificar instalación
ollama --version
```

### macOS

```bash
# Descargar desde https://ollama.ai/download/mac
# O instalar con Homebrew
brew install ollama
```

### Docker (Recomendado para Producción)

Ya incluido en `docker-compose.yml`:

```bash
# Iniciar Ollama con el stack completo
docker-compose --profile ollama up -d

# O solo Ollama
docker-compose up -d ollama
```

---

## 🎯 Configuración

### 1. Instalar y Descargar Modelos

```bash
# Descargar modelo Llama 2 (4GB)
ollama pull llama2

# Descargar Mistral 7B (más rápido, similar calidad)
ollama pull mistral

# Descargar Code Llama (optimizado para código)
ollama pull codellama

# Descargar Gemma (modelo de Google)
ollama pull gemma:7b

# Ver modelos instalados
ollama list
```

### 2. Configurar Variables de Entorno

Editar archivo `.env` en la raíz del proyecto:

```bash
# Seleccionar Ollama como proveedor
LLM_PROVIDER=ollama

# Configuración de Ollama (opcional, estos son los defaults)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### 3. Configuración Programática

```python
from src.ai_native_mvp.llm import LLMProviderFactory

# Método 1: Desde variables de entorno
provider = LLMProviderFactory.create_from_env("ollama")

# Método 2: Configuración manual
provider = LLMProviderFactory.create("ollama", {
    "base_url": "http://localhost:11434",
    "model": "mistral",
    "temperature": 0.7,
    "timeout": 120.0
})
```

---

## 🚀 Uso

### Generación de Respuestas

```python
from src.ai_native_mvp.llm import LLMProviderFactory
from src.ai_native_mvp.llm.base import LLMMessage, LLMRole

# Crear provider
provider = LLMProviderFactory.create_from_env("ollama")

# Preparar mensajes
messages = [
    LLMMessage(
        role=LLMRole.SYSTEM,
        content="Sos un profesor de matemáticas experto."
    ),
    LLMMessage(
        role=LLMRole.USER,
        content="¿Cuál es la fórmula del área de un círculo?"
    )
]

# Generar respuesta
response = await provider.generate(
    messages=messages,
    temperature=0.5,  # Más determinístico
    max_tokens=500
)

print(response.content)
print(f"Tokens usados: {response.usage['total_tokens']}")
```

### Streaming (Respuestas en Tiempo Real)

```python
# Streaming para UX interactiva
async for chunk in provider.generate_stream(messages):
    print(chunk, end="", flush=True)
```

### Verificar Modelos Disponibles

```python
# Listar modelos instalados en Ollama
models = await provider.list_available_models()
print(f"Modelos disponibles: {models}")

# Verificar si un modelo específico está disponible
is_available = await provider.is_model_available()
if not is_available:
    print(f"⚠️  Modelo {provider.model} no encontrado. Instalar con:")
    print(f"   ollama pull {provider.model}")
```

---

## 🎭 Modelos Disponibles

### Modelos Recomendados

| Modelo | Tamaño | Velocidad | Calidad | Uso Ideal | Comando |
|--------|--------|-----------|---------|-----------|---------|
| **Llama 2 7B** | 4GB | ⚡⚡⚡ | ⭐⭐⭐ | General purpose | `ollama pull llama2` |
| **Mistral 7B** | 4GB | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | Conversación, análisis | `ollama pull mistral` |
| **Code Llama 7B** | 4GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Programación | `ollama pull codellama` |
| **Gemma 7B** | 5GB | ⚡⚡⚡ | ⭐⭐⭐⭐ | Google, multilingüe | `ollama pull gemma:7b` |
| **Llama 2 13B** | 7GB | ⚡⚡ | ⭐⭐⭐⭐ | Mejor calidad | `ollama pull llama2:13b` |
| **Mixtral 8x7B** | 26GB | ⚡ | ⭐⭐⭐⭐⭐ | Máxima calidad | `ollama pull mixtral` |

### Variantes por Idioma

```bash
# Modelos optimizados para español
ollama pull gemma:7b        # Google, excelente español
ollama pull llama2          # Multilingüe con buen español

# Modelos especializados
ollama pull codellama       # Código (Python, JS, etc.)
ollama pull llama2:70b      # Máxima calidad (requiere GPU potente)
```

### Comparación de Rendimiento

```bash
# Test rápido de un modelo
ollama run mistral "Explica qué es FastAPI en una frase"

# Benchmarks (aproximados en CPU moderna)
# - Llama 2 7B:    ~20 tokens/segundo
# - Mistral 7B:    ~25 tokens/segundo  
# - Code Llama 7B: ~20 tokens/segundo
# - Gemma 7B:      ~18 tokens/segundo

# Con GPU (NVIDIA RTX 3090):
# - Llama 2 7B:    ~100 tokens/segundo
# - Mistral 7B:    ~120 tokens/segundo
```

---

## 🐳 Docker Deployment

### Opción 1: Servicio Independiente (Producción)

Ollama ya está configurado en `docker-compose.yml`:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ai-native-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama  # Persistencia de modelos
    networks:
      - ai-native-network
    restart: unless-stopped
    profiles:
      - ollama  # Activar con --profile ollama
```

### Iniciar Stack con Ollama

```bash
# Iniciar API + PostgreSQL + Redis + Ollama
docker-compose --profile ollama up -d

# Ver logs
docker-compose logs -f ollama

# Descargar modelos en container
docker-compose exec ollama ollama pull llama2
docker-compose exec ollama ollama pull mistral

# Listar modelos descargados
docker-compose exec ollama ollama list
```

### Opción 2: Con GPU (NVIDIA)

Descomentar sección en `docker-compose.yml`:

```yaml
ollama:
  # ... (config anterior)
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

**Prerequisitos:**
- Instalar [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- Drivers NVIDIA actualizados

```bash
# Verificar GPU disponible
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Iniciar con GPU
docker-compose --profile ollama up -d
```

---

## 🔧 Troubleshooting

### Problema: "Cannot connect to Ollama server"

```python
❌ ValueError: Cannot connect to Ollama server at http://localhost:11434
```

**Soluciones:**

1. **Verificar que Ollama está corriendo:**
   ```bash
   # Linux/macOS
   ps aux | grep ollama
   systemctl status ollama  # Si se instaló como servicio
   
   # Windows
   Get-Process ollama
   
   # Docker
   docker-compose ps ollama
   ```

2. **Iniciar Ollama:**
   ```bash
   # Local
   ollama serve
   
   # Docker
   docker-compose up -d ollama
   ```

3. **Verificar puerto:**
   ```bash
   # Verificar que puerto 11434 está escuchando
   netstat -an | grep 11434
   curl http://localhost:11434/api/tags
   ```

### Problema: "Model not found"

```python
❌ Ollama API error (404): Model 'mistral' not found
```

**Solución:**

```bash
# Descargar modelo
ollama pull mistral

# Verificar modelos instalados
ollama list

# Docker
docker-compose exec ollama ollama pull mistral
```

### Problema: Respuestas muy lentas

**Causas comunes:**

1. **Modelo muy grande para tu hardware**
   ```bash
   # Usar modelo más pequeño
   ollama pull mistral      # En lugar de llama2:70b
   ```

2. **Sin GPU** (esperado, es normal que sea más lento)
   - Modelos 7B: ~20 tokens/seg en CPU moderna
   - Modelos 13B: ~10 tokens/seg en CPU moderna
   - Solución: Habilitar GPU o usar modelo más pequeño

3. **Aumentar timeout:**
   ```python
   provider = OllamaProvider({
       "timeout": 300.0  # 5 minutos
   })
   ```

### Problema: "Out of Memory"

```bash
# Usar modelo más pequeño
ollama pull llama2:7b      # En lugar de llama2:70b

# O configurar límite de memoria en Docker
docker-compose.yml:
  ollama:
    mem_limit: 8g
```

---

## 📊 Comparación con Otros Proveedores

### Ollama vs OpenAI vs Gemini

| Característica | Ollama | OpenAI | Gemini |
|----------------|--------|--------|--------|
| **Privacidad** | ✅ 100% local | ❌ Datos en cloud | ❌ Datos en cloud |
| **Costo** | ✅ Gratis | ❌ $0.002-$0.06/1K tokens | ✅ Gratis (con límites) |
| **API Key** | ✅ No requiere | ❌ Requiere | ❌ Requiere |
| **Velocidad** | ⚡⚡⚡ (depende HW) | ⚡⚡⚡⚡⚡ | ⚡⚡⚡⚡ |
| **Calidad** | ⭐⭐⭐ (7B), ⭐⭐⭐⭐ (70B) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Offline** | ✅ Sí | ❌ No | ❌ No |
| **Setup** | ⚡ Muy simple | ⚡⚡ API Key | ⚡⚡ API Key |
| **Hardware** | 🖥️ CPU/GPU local | ☁️ Cloud | ☁️ Cloud |

### Cuándo Usar Cada Proveedor

**Usar Ollama cuando:**
- ✅ Privacidad es crítica (datos médicos, financieros)
- ✅ Budget limitado (proyectos educativos, startups)
- ✅ Offline/air-gapped environments
- ✅ Control total sobre infraestructura
- ✅ Compliance (HIPAA, GDPR, etc.)

**Usar OpenAI cuando:**
- ✅ Máxima calidad de respuestas (GPT-4)
- ✅ Latencia ultra-baja
- ✅ Escalabilidad ilimitada
- ✅ Budget disponible

**Usar Gemini cuando:**
- ✅ Contextos ultra-largos (2M tokens)
- ✅ Capacidades multimodales (imágenes)
- ✅ Free tier generoso
- ✅ Integración con Google Cloud

---

## 🎯 Roadmap y Mejoras Futuras

### ✅ Implementado
- [x] Integración básica con Ollama API
- [x] Soporte para streaming
- [x] Manejo de errores robusto
- [x] Docker deployment
- [x] Tests unitarios completos
- [x] Métricas de Prometheus

### 🚧 En Desarrollo
- [ ] Fine-tuning de modelos locales
- [ ] Cuantización automática (GGUF)
- [ ] Cache inteligente de embeddings
- [ ] Load balancing entre múltiples instancias

### 💡 Planeado
- [ ] Soporte para modelos multimodales (LLaVA)
- [ ] Auto-scaling basado en demanda
- [ ] Benchmarking automático de modelos
- [ ] Integración con Ray para inferencia distribuida

---

## 📚 Recursos Adicionales

### Documentación Oficial
- [Ollama Website](https://ollama.ai)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [Ollama Model Library](https://ollama.ai/library)
- [Ollama API Reference](https://github.com/ollama/ollama/blob/main/docs/api.md)

### Modelos Open Source
- [Llama 2 (Meta)](https://ai.meta.com/llama/)
- [Mistral AI](https://mistral.ai)
- [Google Gemma](https://ai.google.dev/gemma)
- [Code Llama](https://ai.meta.com/blog/code-llama-large-language-model-coding/)

### Comunidad
- [Ollama Discord](https://discord.gg/ollama)
- [Awesome Ollama](https://github.com/jmorganca/awesome-ollama)

---

## 🤝 Soporte

¿Preguntas o problemas? 

1. **Revisar logs:**
   ```bash
   docker-compose logs -f ollama
   docker-compose logs -f api
   ```

2. **Verificar health check:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

3. **Reportar issue:** [GitHub Issues](https://github.com/tu-repo/issues)

---

**Última actualización:** Diciembre 2025  
**Versión:** 1.0.0  
**Autor:** Phoenix Development Team
