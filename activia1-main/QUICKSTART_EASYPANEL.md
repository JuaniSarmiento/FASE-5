# ⚡ Deploy Rápido en EasyPanel

**5 pasos, 10 minutos** para tener Activia funcionando en EasyPanel.

---

## 📦 Lo que vamos a crear

```
PostgreSQL → Redis → Backend API → Frontend
```

---

## 🚀 Pasos Rápidos

### 1️⃣ PostgreSQL (2 min)
```yaml
Servicio: PostgreSQL
Nombre: activia-postgres
Database: activia
Usuario: activia_user
Password: [genera una segura]
```

### 2️⃣ Redis (1 min)
```yaml
Servicio: Redis
Nombre: activia-redis
Password: [genera una segura]
```

### 3️⃣ Backend API (3 min)
```yaml
Servicio: App (Docker)
Nombre: activia-backend
Dockerfile: Dockerfile.backend
Port: 8000
```

**Variables de entorno clave:**
```bash
DATABASE_URL=postgresql://activia_user:PASSWORD@activia-postgres:5432/activia
REDIS_URL=redis://:PASSWORD@activia-redis:6379/0
SECRET_KEY=[openssl rand -hex 32]
JWT_SECRET_KEY=[openssl rand -hex 32]
LLM_PROVIDER=mock
ALLOWED_ORIGINS=https://TU-FRONTEND.easypanel.host
```

### 4️⃣ Frontend (3 min)
```yaml
Servicio: App (Docker)
Nombre: activia-frontend
Dockerfile: Dockerfile.frontend
Port: 80
Public: ✅ SÍ
```

**Build Args:**
```bash
VITE_API_URL=https://activia-backend-TU-PROYECTO.easypanel.host
VITE_API_BASE_URL=https://activia-backend-TU-PROYECTO.easypanel.host/api/v1
```

### 5️⃣ Inicializar Datos (1 min)
```bash
# Desde Shell del backend en EasyPanel:
python backend/scripts/seed_dev.py
```

---

## ✅ Verificar

1. **Backend Health**: `https://activia-backend-XXX.easypanel.host/api/v1/health`
   - Debe responder: `{"status": "healthy"}`

2. **Frontend**: `https://activia-frontend-XXX.easypanel.host`
   - Debe mostrar login

3. **Login de prueba**:
   - Email: `estudiante@activia.com`
   - Password: `student123`

---

## 🔑 Generar Claves Seguras

```bash
# Opción 1: OpenSSL
openssl rand -hex 32

# Opción 2: Python
python -c "import secrets; print(secrets.token_hex(32))"

# Opción 3: Online
# https://generate-secret.vercel.app/32
```

---

## 📋 Checklist

- [ ] PostgreSQL creado y funcionando
- [ ] Redis creado y funcionando
- [ ] Backend desplegado (health check ✅)
- [ ] Frontend desplegado (acceso web ✅)
- [ ] Variables de entorno configuradas
- [ ] Datos iniciales cargados (seed)
- [ ] Login funciona

---

## 🐛 Problemas Comunes

### ❌ Backend no inicia
```bash
# Revisa logs en EasyPanel
# Verifica: DATABASE_URL tiene el host correcto (activia-postgres)
# Verifica: PostgreSQL está en la misma red interna
```

### ❌ Frontend muestra página en blanco
```bash
# Verifica: VITE_API_URL está configurado en Build Args
# Revisa logs del build
# Abre DevTools (F12) → Console para ver errores
```

### ❌ CORS Error
```bash
# En Backend, agrega a ALLOWED_ORIGINS:
ALLOWED_ORIGINS=https://activia-frontend-XXX.easypanel.host,http://localhost:5173
```

---

## 📚 Documentación Completa

Para guía detallada, ver: **`DEPLOY_EASYPANEL.md`**

---

## 🎯 Recursos Mínimos

- **1.5 CPU** | **1.5GB RAM** | **9GB Storage**
- Con Ollama: **+2 CPU** | **+4GB RAM** | **+5GB Storage**

---

## 💡 Tips

1. **Usa `mock` para LLM** (no requiere Ollama, ideal para testing)
2. **Habilita SSL** en todos los servicios públicos
3. **Configura backups** de PostgreSQL desde EasyPanel
4. **Monitorea logs** regularmente
5. **Cambia passwords seed** en producción

---

**¿Necesitas ayuda?** Ver documentación completa o crear un issue en GitHub.

---

**Tiempo total**: ~10 minutos ⏱️
