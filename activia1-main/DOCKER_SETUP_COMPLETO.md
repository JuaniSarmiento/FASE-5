# 🐳 Proyecto Completamente Dockerizado

## ✅ Estado del Proyecto

**El proyecto completo está ahora dockerizado y funcionando:**

- ✅ **Backend API** (FastAPI) - Puerto 8000
- ✅ **Frontend** (React + Vite) - Puerto 3000
- ✅ **PostgreSQL** - Puerto 5432
- ✅ **Redis** - Puerto 6379

## 🚀 Comandos de Uso

### Iniciar todo el stack
```bash
docker compose up -d
```

### Ver estado de servicios
```bash
docker compose ps
```

### Ver logs
```bash
# Todos los servicios
docker compose logs -f

# Un servicio específico
docker compose logs -f api
docker compose logs -f frontend
docker compose logs -f postgres
docker compose logs -f redis
```

### Detener servicios
```bash
docker compose down
```

### Reconstruir y reiniciar
```bash
docker compose up -d --build
```

## 🌐 Acceso a los Servicios

### Backend API
- **URL**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

### Frontend
- **URL**: http://localhost:3000
- **Health Check**: http://localhost:3000/health

### PostgreSQL
- **Host**: localhost
- **Puerto**: 5432
- **Base de datos**: ai_native
- **Usuario**: ai_native
- **Password**: Ver archivo `.env`

### Redis
- **Host**: localhost
- **Puerto**: 6379
- **Password**: Ver archivo `.env`

## 📁 Archivos Creados/Modificados

### Nuevos Archivos
1. **`frontEnd/Dockerfile`** - Imagen optimizada multi-stage para React
2. **`frontEnd/nginx.conf`** - Configuración de nginx con proxy al backend

### Archivos Modificados
1. **`docker-compose.yml`** - Añadido servicio `frontend`
2. **`frontEnd/src/types/exercise.d.ts`** - Corregido error de sintaxis TypeScript
3. **`frontEnd/src/types/evaluation.d.ts`** - Añadido tipo 'PARTIAL' a EvaluationStatus

## 🏗️ Arquitectura Docker

```
┌─────────────────────────────────────────────┐
│           Docker Network (bridge)           │
├─────────────────────────────────────────────┤
│                                             │
│  ┌──────────────┐      ┌──────────────┐    │
│  │   Frontend   │────▶ │   Backend    │    │
│  │  nginx:alpine│      │  FastAPI     │    │
│  │  Port: 3000  │      │  Port: 8000  │    │
│  └──────────────┘      └──────┬───────┘    │
│                               │             │
│                        ┌──────┴────────┐    │
│                        │               │    │
│                  ┌─────▼─────┐  ┌─────▼────┐│
│                  │ PostgreSQL│  │  Redis   ││
│                  │ Port: 5432│  │Port: 6379││
│                  └───────────┘  └──────────┘│
│                                             │
└─────────────────────────────────────────────┘
```

## 🔧 Configuración

### Variables de Entorno
Todas las configuraciones están en el archivo `.env` en la raíz del proyecto:

- **Database**: Configuración de PostgreSQL
- **Redis**: Configuración de caché
- **Security**: JWT y secret keys
- **LLM**: Configuración de Gemini API
- **CORS**: Orígenes permitidos

### Build Multi-Stage

#### Frontend
1. **Stage 1 (Builder)**: Node.js 20 Alpine
   - Instala dependencias
   - Compila TypeScript + Vite
   - Genera build de producción optimizado

2. **Stage 2 (Production)**: Nginx Alpine
   - Copia archivos estáticos del build
   - Configura nginx como servidor + proxy
   - Imagen final ligera (~50MB)

#### Backend
- Python 3.11 slim
- Multi-stage build
- Usuario no-root para seguridad
- Health checks configurados

## 🔍 Verificación de Funcionamiento

### Backend
```bash
curl http://localhost:8000/api/v1/health
```

Respuesta esperada:
```json
{"status":"healthy","version":"0.1.0","database":"connected",...}
```

### Frontend
```bash
curl http://localhost:3000/
```

Debería retornar HTML de la aplicación React.

### Base de Datos
```bash
docker compose exec postgres psql -U ai_native -d ai_native -c "SELECT 1;"
```

### Redis
```bash
docker compose exec redis redis-cli -a <REDIS_PASSWORD> ping
```

## 🐛 Troubleshooting

### Frontend muestra "unhealthy"
El frontend puede mostrarse como "unhealthy" en Docker pero funcionar correctamente. Esto es normal durante los primeros 30-60 segundos después del inicio, ya que el healthcheck tiene un `start_period` y puede tardar en estabilizarse.

Para verificar manualmente:
```bash
docker compose exec frontend wget -q -O - http://127.0.0.1/health
```

### Backend no inicia
Verificar que las variables de entorno están configuradas correctamente en `.env`:
```bash
docker compose logs api
```

Error común: `GEMINI_API_KEY is required when LLM_PROVIDER='gemini'`
Solución: Verificar que `.env` tiene `GEMINI_API_KEY` configurado.

### PostgreSQL no conecta
```bash
docker compose exec postgres pg_isready -U ai_native
```

### Redis no conecta
```bash
docker compose exec redis redis-cli -a ${REDIS_PASSWORD} ping
```

## 📊 Recursos

### Límites de Memoria
- API: 2GB límite, 512MB reservado
- Frontend: 512MB límite, 128MB reservado
- PostgreSQL: 2GB límite, 512MB reservado
- Redis: 512MB límite, 128MB reservado

### Rotación de Logs
Todos los servicios tienen configurada rotación automática de logs:
- Tamaño máximo: 50-100MB por archivo
- Archivos retenidos: 3

## 🔐 Seguridad

### Producción
Antes de llevar a producción:

1. ✅ Cambiar todas las contraseñas en `.env`
2. ✅ Generar nuevos secrets (`JWT_SECRET_KEY`, `SECRET_KEY`)
3. ✅ Usar secretos externos (AWS Secrets Manager, Vault)
4. ✅ Configurar HTTPS/SSL
5. ✅ Implementar reverse proxy (nginx/traefik)
6. ✅ Configurar backups de PostgreSQL
7. ✅ Habilitar monitoreo (Prometheus/Grafana)

## 🎯 Próximos Pasos

- [ ] Añadir nginx como reverse proxy global
- [ ] Configurar HTTPS con Let's Encrypt
- [ ] Implementar CI/CD pipeline
- [ ] Añadir testing automatizado en containers
- [ ] Configurar backup automático de datos
- [ ] Documentar procedimiento de despliegue en producción

## 📝 Notas

- El archivo `version` en docker-compose.yml está marcado como obsoleto por Docker Compose v2, pero no afecta el funcionamiento
- El proyecto utiliza Gemini AI como proveedor LLM por defecto
- Todos los contenedores están en la misma red Docker para comunicación interna
- Los volúmenes persisten los datos de PostgreSQL y Redis
