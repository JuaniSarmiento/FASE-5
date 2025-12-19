# 🚀 Guía de Deploy en EasyPanel

Esta guía te llevará paso a paso para desplegar **Activia** en EasyPanel.

## 📋 Pre-requisitos

1. Cuenta en [EasyPanel](https://easypanel.io)
2. Proyecto conectado a GitHub/GitLab
3. 10 minutos de tu tiempo

---

## 🏗️ Arquitectura de Servicios

```
┌─────────────────────────────────────────┐
│           EASYPANEL PROJECT             │
├─────────────────────────────────────────┤
│  1. PostgreSQL (Base de datos)          │
│  2. Redis (Caché)                       │
│  3. Backend API (FastAPI)               │
│  4. Frontend (React/Nginx)              │
└─────────────────────────────────────────┘
```

---

## 🔧 PASO 1: Crear Base de Datos PostgreSQL

1. En EasyPanel → **Create Service** → **PostgreSQL**
2. Configuración:
   - **Name**: `activia-postgres`
   - **Database Name**: `activia`
   - **Username**: `activia_user`
   - **Password**: (genera una segura)
   - **Port**: `5432` (default)
3. **Deploy**
4. ⚠️ **GUARDA**: La **Internal URL** que aparece (ej: `activia-postgres:5432`)

---

## 🔧 PASO 2: Crear Redis

1. En EasyPanel → **Create Service** → **Redis**
2. Configuración:
   - **Name**: `activia-redis`
   - **Password**: (genera una segura, opcional)
   - **Port**: `6379` (default)
3. **Deploy**
4. ⚠️ **GUARDA**: La **Internal URL** (ej: `activia-redis:6379`)

---

## 🔧 PASO 3: Crear Backend API

1. En EasyPanel → **Create Service** → **App (Docker)**
2. Configuración básica:
   - **Name**: `activia-backend`
   - **Source**: Tu repositorio Git
   - **Branch**: `main`
   - **Dockerfile**: `Dockerfile.backend`
   - **Port**: `8000`

3. **Variables de Entorno** (Add Environment Variables):

```bash
# Database
DATABASE_URL=postgresql://activia_user:TU_PASSWORD@activia-postgres:5432/activia
POSTGRES_USER=activia_user
POSTGRES_PASSWORD=TU_PASSWORD_POSTGRES
POSTGRES_DB=activia

# Redis
REDIS_URL=redis://:TU_PASSWORD_REDIS@activia-redis:6379/0
REDIS_PASSWORD=TU_PASSWORD_REDIS

# Security (genera claves únicas)
SECRET_KEY=GENERAR_CON_openssl_rand_-hex_32
JWT_SECRET_KEY=GENERAR_CON_openssl_rand_-hex_32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM (usa mock para testing sin Ollama)
LLM_PROVIDER=mock

# CORS (ajusta con tu dominio de EasyPanel)
ALLOWED_ORIGINS=https://activia-frontend-TU-PROYECTO.easypanel.host

# App
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=False
```

4. **Networking**:
   - Enable **Internal Network**
   - Opcionalmente habilita **Public Domain**

5. **Deploy**

6. ⚠️ **VERIFICA**: Abre logs y verifica que inicia correctamente

---

## 🔧 PASO 4: Crear Frontend

1. En EasyPanel → **Create Service** → **App (Docker)**
2. Configuración básica:
   - **Name**: `activia-frontend`
   - **Source**: Tu repositorio Git
   - **Branch**: `main`
   - **Dockerfile**: `Dockerfile.frontend`
   - **Port**: `80`

3. **Variables de Entorno** (Build Args):

```bash
# URL del backend (usa la URL interna o pública del backend)
VITE_API_URL=https://activia-backend-TU-PROYECTO.easypanel.host
VITE_API_BASE_URL=https://activia-backend-TU-PROYECTO.easypanel.host/api/v1
```

4. **Networking**:
   - Enable **Public Domain** ✅ (para acceso web)
   - Habilita **SSL/TLS Certificate**

5. **Deploy**

---

## ✅ PASO 5: Verificar el Deploy

### 1. **Health Check del Backend**
Abre en el navegador:
```
https://activia-backend-TU-PROYECTO.easypanel.host/api/v1/health
```

Deberías ver:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production"
}
```

### 2. **Frontend**
Abre:
```
https://activia-frontend-TU-PROYECTO.easypanel.host
```

Deberías ver la página de login.

### 3. **Logs**
Revisa los logs de cada servicio en EasyPanel:
- Backend: Verifica que conecta a PostgreSQL y Redis
- Frontend: Verifica que el build fue exitoso

---

## 🔑 PASO 6: Inicializar Base de Datos

Para crear el usuario admin inicial, conecta al backend:

### Opción A: Desde EasyPanel Shell
1. Ve al servicio **activia-backend**
2. Abre **Shell/Console**
3. Ejecuta:
```bash
python backend/scripts/seed_dev.py
```

### Opción B: Endpoint de Admin
```bash
curl -X POST https://activia-backend-TU-PROYECTO.easypanel.host/api/v1/admin/seed
```

Esto creará usuarios de prueba:
- **Estudiante**: `estudiante@activia.com` / `student123`
- **Docente**: `docente@activia.com` / `teacher123`
- **Admin**: `admin@activia.com` / `admin123`

---

## 🔐 Generar Claves Seguras

Para generar `SECRET_KEY` y `JWT_SECRET_KEY`:

### Opción 1: OpenSSL (Linux/Mac/WSL)
```bash
openssl rand -hex 32
```

### Opción 2: Python
```python
import secrets
print(secrets.token_hex(32))
```

### Opción 3: Online
- https://generate-secret.vercel.app/32

⚠️ **IMPORTANTE**: Usa claves DIFERENTES para cada variable.

---

## 🎯 Configuraciones Opcionales

### A. **Ollama (LLM Local)**

Si quieres usar Ollama en lugar de `mock`:

1. Crea servicio adicional con Ollama:
   - Name: `activia-ollama`
   - Image: `ollama/ollama:latest`
   - Port: `11434`
   - Volume: `/root/.ollama` (persistent storage)

2. Actualiza variables en **Backend**:
```bash
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://activia-ollama:11434
OLLAMA_MODEL=phi3
```

3. Descarga modelo (desde Shell de ollama):
```bash
ollama pull phi3
```

⚠️ **Nota**: Ollama puede consumir muchos recursos (RAM/CPU).

---

### B. **Custom Domain**

1. En EasyPanel → Service → **Domains**
2. Agrega tu dominio personalizado
3. Actualiza `ALLOWED_ORIGINS` en Backend
4. Actualiza `VITE_API_URL` en Frontend

---

### C. **Monitoring (Opcional)**

EasyPanel tiene métricas integradas. Para ver:
- CPU/RAM usage
- Logs en tiempo real
- Restart automático si falla

---

## 🐛 Troubleshooting

### ❌ Backend no conecta a PostgreSQL
- Verifica que usas la **Internal URL** correcta
- Verifica que PostgreSQL está en la misma red interna
- Revisa logs del backend: `docker logs activia-backend`

### ❌ Frontend no se comunica con Backend
- Verifica `VITE_API_URL` en variables de entorno
- Verifica CORS en `ALLOWED_ORIGINS` del backend
- Verifica que el backend esté público o en la misma red

### ❌ Error 502 Bad Gateway
- Backend no inició correctamente
- Revisa logs del backend
- Verifica que el puerto 8000 está expuesto

### ❌ Frontend muestra página en blanco
- Verifica que el build fue exitoso (logs de deploy)
- Verifica rutas en `nginx.conf`
- Abre DevTools (F12) y revisa errores en Console

---

## 📊 Métricas de Recursos

Recursos mínimos recomendados:

| Servicio | CPU | RAM | Storage |
|----------|-----|-----|---------|
| PostgreSQL | 0.5 | 512MB | 5GB |
| Redis | 0.25 | 256MB | 1GB |
| Backend | 0.5 | 512MB | 2GB |
| Frontend | 0.25 | 256MB | 1GB |
| **TOTAL** | **1.5 CPU** | **1.5GB RAM** | **9GB** |

Con Ollama (phi3):
- **+2 CPU**, **+4GB RAM**, **+5GB storage**

---

## 🎉 ¡Listo!

Tu aplicación debería estar funcionando en:
```
🌐 Frontend: https://activia-frontend-TU-PROYECTO.easypanel.host
🔌 API: https://activia-backend-TU-PROYECTO.easypanel.host/api/v1
📚 API Docs: https://activia-backend-TU-PROYECTO.easypanel.host/docs
```

---

## 📚 Próximos Pasos

1. **Cambiar passwords por defecto** de los usuarios seed
2. **Configurar backups** de PostgreSQL en EasyPanel
3. **Configurar dominio personalizado**
4. **Monitorear logs** y métricas
5. **Habilitar SSL** en todos los servicios públicos

---

## 🆘 Soporte

- **Documentación**: Ver `CLAUDE.md` en el repositorio
- **Issues**: Crear issue en GitHub
- **EasyPanel Docs**: https://easypanel.io/docs

---

**Última actualización**: Diciembre 2025
