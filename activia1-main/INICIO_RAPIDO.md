# 🚀 AI-Native MVP - Guía de Inicio Rápido

## ✅ Sistema Levantado y Operacional

El proyecto está completamente funcional con Docker Compose.

---

## 🌐 URLs de Acceso

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **API Swagger** | http://localhost:8000/docs | Documentación interactiva de la API |
| **Health Check** | http://localhost:8000/api/v1/health | Estado del sistema |
| **Frontend** | http://localhost:3001 | Interfaz de usuario (si está corriendo) |
| **PostgreSQL** | localhost:5432 | Base de datos |
| **Redis** | localhost:6379 | Cache y rate limiting |
| **Ollama** | localhost:11434 | Servidor LLM local |

---

## 👥 Usuarios de Prueba

### 1. 👨‍🎓 Estudiante

```
📧 Email: estudiante@activia.com
🔑 Password: estudiante123
👤 Rol: student
```

### 2. 👨‍🏫 Docente

```
📧 Email: docente@activia.com
🔑 Password: docente123
👤 Rol: student (puedes cambiar roles en la BD)
```

### 3. 👨‍💼 Administrador

```
📧 Email: admin@activia.com
🔑 Password: admin123
👤 Rol: student (puedes cambiar roles en la BD)
```

---

## 🔐 Ejemplo de Login (API)

### Usando cURL:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"estudiante@activia.com","password":"estudiante123"}'
```

### Usando PowerShell:

```powershell
$loginBody = '{"email":"estudiante@activia.com","password":"estudiante123"}'
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST -Body $loginBody -ContentType "application/json"

# Ver el token
$response.data.tokens.access_token
```

### Respuesta esperada:

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "...",
      "username": "estudiante",
      "email": "estudiante@activia.com",
      "full_name": "Estudiante de Prueba",
      "roles": ["student"],
      "is_active": true
    },
    "tokens": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "bearer"
    }
  },
  "message": "Login successful"
}
```

---

## 🤖 Agentes de IA Disponibles

Todos los agentes están operacionales:

1. **T-IA-Cog** - Tutor Cognitivo Socrático
2. **E-IA-Proc** - Evaluador de Procesos
3. **S-IA-X** - Simuladores Profesionales (11 roles)
4. **AR-IA** - Analista de Riesgos
5. **GOV-IA** - Gobernanza Institucional
6. **TC-N4** - Trazabilidad Cognitiva

---

## 📝 Crear una Sesión e Interactuar con el Tutor

### 1. Crear una sesión:

```bash
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{
    "student_id": "TU_USER_ID",
    "mode": "TUTOR"
  }'
```

### 2. Enviar una pregunta al tutor:

```bash
curl -X POST http://localhost:8000/api/v1/interactions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{
    "session_id": "TU_SESSION_ID",
    "prompt": "¿Cómo implemento una cola en Python?",
    "interaction_type": "tutor_query"
  }'
```

---

## 🐳 Comandos Docker Útiles

### Ver estado de los servicios:
```bash
docker ps
```

### Ver logs de un servicio:
```bash
docker logs -f ai-native-api
docker logs -f ai-native-postgres
docker logs -f ai-native-redis
docker logs -f ai-native-ollama
```

### Reiniciar un servicio:
```bash
docker restart ai-native-api
```

### Detener todo:
```bash
cd activia1-main
docker compose down
```

### Levantar todo:
```bash
cd activia1-main
docker compose up -d

# (Opcional) Levantar Ollama con GPU (NVIDIA):
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d
```

### Eliminar todo (incluyendo volúmenes - ⚠️ BORRA DATOS):
```bash
cd activia1-main
docker compose down -v
```

---

## 🧪 Verificar que Todo Funciona

### 1. Health Check:
```bash
curl http://localhost:8000/api/v1/health
```

Debería responder:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected",
  "agents": {
    "T-IA-Cog": "operational",
    "E-IA-Proc": "operational",
    "S-IA-X": "operational",
    "AR-IA": "operational",
    "GOV-IA": "operational",
    "TC-N4": "operational"
  }
}
```

### 2. Verificar modelo Phi-3 descargado:
```bash
docker exec ai-native-ollama ollama list
```

Debería mostrar:
```
NAME    ID              SIZE
phi3    latest          2.2 GB
```

---

## 🔧 Problemas Comunes

### Error 401 en login:
- Verificar que estás usando el email correcto (no username)
- Verificar que la contraseña es correcta
- Los usuarios de prueba ya están creados con las credenciales arriba

### Error "User not found":
- Crear un usuario nuevo usando el endpoint `/api/v1/auth/register`

### El modelo Phi-3 no responde:
- Verificar que se descargó completamente: `docker exec ai-native-ollama ollama list`
- Si no está, descargar: `docker exec ai-native-ollama ollama pull phi3`

### La API no responde:
- Verificar que el contenedor está corriendo: `docker ps`
- Ver logs: `docker logs ai-native-api`
- Reiniciar: `docker restart ai-native-api`

---

## 📊 Archivos de Configuración

- **`.env`** - Variables de entorno (credenciales, configuración)
- **`docker-compose.yml`** - Definición de servicios Docker
- **`requirements.txt`** - Dependencias Python del backend
- **`frontEnd/package.json`** - Dependencias del frontend

---

## 🎓 Próximos Pasos

1. ✅ Explorar la API en http://localhost:8000/docs
2. ✅ Probar el login con los usuarios de prueba
3. ✅ Crear una sesión de tutoría
4. ✅ Interactuar con el Tutor Socrático (T-IA-Cog)
5. ✅ Explorar los diferentes agentes de IA
6. ✅ Revisar la documentación en la carpeta `docs/`

---

## 📚 Documentación Adicional

- **Arquitectura completa**: `docs/AUDITORIA_ARQUITECTURA_COMPLETA.md`
- **Sistema de agentes**: `docs/Misagentes/integrador.md`
- **Trazabilidad N4**: `trazabilidad.md`
- **Tutor Socrático**: `docs/TUTOR_SOCRATICO_V2.md`
- **Índice de documentación**: `docs/INDICE_DOCUMENTACION.md`

---

**¡Proyecto listo para usar!** 🎉
