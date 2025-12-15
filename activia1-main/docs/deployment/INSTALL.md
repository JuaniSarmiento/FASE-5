# 📦 Guía de Instalación - AI-Native MVP

Esta guía te llevará paso a paso para ejecutar el proyecto en tu máquina.

---

## ⚡ Instalación Rápida (Recomendada)

**Tiempo estimado: 10 minutos**

### 1️⃣ Instalar Docker Desktop

#### Windows:
1. Descargar desde: https://www.docker.com/products/docker-desktop
2. Ejecutar el instalador
3. Reiniciar el sistema
4. Abrir Docker Desktop y esperar a que inicie

#### macOS:
```bash
brew install --cask docker
# O descargar desde: https://www.docker.com/products/docker-desktop
```

#### Linux (Ubuntu/Debian):
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar
```

### 2️⃣ Clonar el Repositorio

```bash
git clone https://github.com/JuaniSarmiento/AI-NATIVE.git
cd AI-NATIVE
```

### 3️⃣ Levantar la Aplicación

```bash
# Inicia: Backend + PostgreSQL + Redis + Ollama
docker-compose up -d
```

Esto creará 5 contenedores:
- `ai-native-api` - Backend FastAPI
- `ai-native-postgres` - Base de datos
- `ai-native-redis` - Cache
- `ai-native-ollama` - Servidor LLM local
- `ai-native-pgadmin` - Administrador de BD (opcional)

### 4️⃣ Esperar Descarga del Modelo (Primera Vez)

```bash
# Ver progreso de descarga de Phi-3 (~2.2 GB)
docker-compose logs -f ollama

# Verás algo como:
# pulling manifest
# pulling fe6a5bd... 100% ▕████████▏ 2.2 GB
# success
```

Esto solo ocurre la primera vez. El modelo se guarda en un volumen de Docker.

### 5️⃣ Verificar que Todo Funciona

```bash
# Ver estado de servicios
docker-compose ps

# Deberías ver 5 contenedores "healthy" o "running"
```

### 6️⃣ Probar el Backend

Abre tu navegador en:

**API Swagger UI**: http://localhost:8000/docs

Prueba el endpoint `/api/v1/health` - debe retornar:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "..."
}
```

### 7️⃣ (Opcional) Instalar y Correr el Frontend

```bash
cd frontEnd
npm install
npm run dev
```

Abre: http://localhost:3001

---

## 🎯 Uso Básico

### Crear una Sesión de Tutor

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "estudiante1",
    "mode": "TUTOR"
  }'
```

Respuesta:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "student_id": "estudiante1",
  "mode": "TUTOR",
  "created_at": "2025-12-05T10:30:00"
}
```

### Hacer una Pregunta al Tutor

```bash
curl -X POST http://localhost:8000/api/v1/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "prompt": "¿Qué es recursividad en programación?",
    "interaction_type": "tutor_query"
  }'
```

Respuesta (generada por Phi-3):
```json
{
  "response": "### Concepto clave\n\nLa **recursividad** es una técnica...",
  "response_type": "conceptual_explanation",
  "timestamp": "2025-12-05T10:31:00"
}
```

---

## 🔧 Comandos Útiles

### Ver Logs en Tiempo Real

```bash
# Todos los servicios
docker-compose logs -f

# Solo el backend
docker-compose logs -f api

# Solo Ollama
docker-compose logs -f ollama
```

### Reiniciar Servicios

```bash
# Reiniciar todo
docker-compose restart

# Solo el backend
docker-compose restart api
```

### Entrar a un Contenedor

```bash
# Shell en el backend
docker-compose exec api bash

# Shell en PostgreSQL
docker-compose exec postgres psql -U ai_native

# Listar modelos en Ollama
docker-compose exec ollama ollama list
```

### Detener Todo

```bash
# Detener pero mantener datos
docker-compose down

# Detener y BORRAR datos (⚠️ cuidado)
docker-compose down -v
```

---

## 🐛 Solución de Problemas

### ❌ Error: "Cannot connect to Docker daemon"

**Solución**: Asegúrate de que Docker Desktop esté corriendo.

```bash
# Windows: Abrir Docker Desktop desde el menú inicio
# Linux: sudo systemctl start docker
# macOS: Abrir Docker.app
```

### ❌ Error: "Port 8000 is already in use"

**Solución**: Otro proceso está usando el puerto 8000.

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8000 | xargs kill -9
```

### ❌ Error: "Ollama model not found"

**Solución**: El modelo Phi-3 no se descargó correctamente.

```bash
# Descargar manualmente
docker-compose exec ollama ollama pull phi3

# Verificar
docker-compose exec ollama ollama list
```

### ❌ Error: "Database connection failed"

**Solución**: PostgreSQL no está listo.

```bash
# Verificar estado
docker-compose ps postgres

# Reiniciar PostgreSQL
docker-compose restart postgres

# Ver logs
docker-compose logs postgres
```

### ❌ Frontend no conecta con backend

**Solución**: Verificar configuración de proxy en `frontEnd/vite.config.ts`:

```typescript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

---

## 🚀 Acceso a Interfaces

| Servicio | URL | Usuario | Contraseña |
|----------|-----|---------|------------|
| **Frontend** | http://localhost:3001 | - | - |
| **API Docs** | http://localhost:8000/docs | - | - |
| **API Health** | http://localhost:8000/api/v1/health | - | - |
| **pgAdmin** | http://localhost:5050 | admin@ai-native.local | admin |

---

## 📊 Verificar Instalación

Ejecuta este script para verificar que todo está bien:

```bash
# Verificar servicios
echo "🔍 Verificando servicios..."
docker-compose ps

echo ""
echo "🏥 Verificando health del backend..."
curl -s http://localhost:8000/api/v1/health | python -m json.tool

echo ""
echo "🤖 Verificando modelos de Ollama..."
docker-compose exec ollama ollama list

echo ""
echo "✅ Si todo muestra 'healthy' o 'running', la instalación es exitosa!"
```

---

## 🎓 Próximos Pasos

Una vez instalado:

1. **Lee la [GUIA_ESTUDIANTE.md](GUIA_ESTUDIANTE.md)** para aprender a usar la plataforma
2. **Explora el [README_API.md](README_API.md)** para ver todos los endpoints
3. **Prueba los 6 agentes IA** desde http://localhost:3001
4. **Revisa [GUIA_INTEGRACION_LLM.md](GUIA_INTEGRACION_LLM.md)** para cambiar de modelo

---

## 💡 Consejos

- **Modelo muy lento?** Usa `phi3` en vez de modelos más grandes
- **Quieres mejor calidad?** Usa `mistral` o `codellama`
- **Sin internet?** Ollama funciona 100% offline una vez descargado
- **Producción?** Lee [GUIA_ADMINISTRADOR.md](GUIA_ADMINISTRADOR.md)

---

## ❓ Ayuda

¿Problemas con la instalación?

1. Revisa los [Issues](https://github.com/JuaniSarmiento/AI-NATIVE/issues) en GitHub
2. Abre un nuevo Issue con:
   - Tu sistema operativo
   - Versión de Docker (`docker --version`)
   - Logs del error (`docker-compose logs`)

---

**¡Listo! 🎉** Ya puedes empezar a usar AI-Native.
