# Quick Start: Ollama en Phoenix MVP

## 🚀 5 Minutos para Estar Corriendo

### 1. Instalar Ollama

**Windows:**
```powershell
# Descargar e instalar desde:
# https://ollama.ai/download/windows
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

### 2. Descargar un Modelo

```bash
# Opción 1: Mistral (recomendado - rápido y buena calidad)
ollama pull mistral

# Opción 2: Llama 2 (popular, good for general use)
ollama pull llama2

# Opción 3: Code Llama (optimizado para programación)
ollama pull codellama
```

### 3. Configurar Phoenix

Editar `.env`:

```bash
# Cambiar proveedor a Ollama
LLM_PROVIDER=ollama

# Configurar modelo (el que descargaste en paso 2)
OLLAMA_MODEL=mistral

# URL de Ollama (default: localhost)
OLLAMA_BASE_URL=http://localhost:11434
```

### 4. Iniciar Sistema

**Opción A: Local (sin Docker)**

```bash
# Terminal 1: Iniciar Ollama (si no se inició automáticamente)
ollama serve

# Terminal 2: Iniciar Phoenix API
python scripts/run_api.py
```

**Opción B: Docker (con todos los servicios)**

```bash
# Iniciar stack completo con Ollama
docker-compose --profile ollama up -d

# Descargar modelo en container
docker-compose exec ollama ollama pull mistral
```

### 5. Probar

```bash
# Test rápido desde terminal
curl http://localhost:8000/api/v1/chat/tutor \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <tu-token>" \
  -d '{
    "user_id": 1,
    "message": "Explica qué es una función en Python"
  }'
```

O abrir en navegador:
- 📖 API Docs: http://localhost:8000/docs
- 🤖 Ollama UI: http://localhost:11434 (para verificar)

---

## 🎯 Uso Programático

```python
from src.ai_native_mvp.llm import LLMProviderFactory
from src.ai_native_mvp.llm.base import LLMMessage, LLMRole

# Crear provider
provider = LLMProviderFactory.create_from_env("ollama")

# Generar respuesta
messages = [
    LLMMessage(role=LLMRole.USER, content="¿Qué es FastAPI?")
]

response = await provider.generate(messages)
print(response.content)
```

---

## ⚡ Tips Rápidos

### Cambiar Modelo

```bash
# Ver modelos instalados
ollama list

# Descargar otro modelo
ollama pull gemma:7b

# Actualizar .env
OLLAMA_MODEL=gemma:7b

# Reiniciar API
```

### Verificar que Funciona

```bash
# Test directo a Ollama
ollama run mistral "Di hola"

# Test a Phoenix API
curl http://localhost:8000/api/v1/health
```

### Troubleshooting Express

**Problema: "Cannot connect to Ollama"**
```bash
# Verificar que está corriendo
ps aux | grep ollama  # Linux/Mac
Get-Process ollama    # Windows

# Si no está corriendo:
ollama serve
```

**Problema: "Model not found"**
```bash
# Verificar modelos instalados
ollama list

# Descargar el modelo que configuraste
ollama pull mistral  # o el que uses
```

---

## 📚 Siguiente Paso

Lee la guía completa: [OLLAMA_INTEGRATION_GUIDE.md](OLLAMA_INTEGRATION_GUIDE.md)

- ✅ Comparación de modelos
- ✅ Configuración avanzada
- ✅ Deployment en producción
- ✅ GPU acceleration
- ✅ Troubleshooting detallado
