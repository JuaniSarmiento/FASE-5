# 🐳 Deployment con Docker - Guía Completa

**Última actualización**: 2025-11-25
**Remediación**: CRITICAL-02 de auditoría arquitectónica

---

## 📋 Tabla de Contenidos

1. [Quick Start (5 minutos)](#quick-start-5-minutos)
2. [Prerequisitos](#prerequisitos)
3. [Configuración](#configuración)
4. [Comandos Comunes](#comandos-comunes)
5. [Arquitectura del Stack](#arquitectura-del-stack)
6. [Troubleshooting](#troubleshooting)
7. [Production Deployment](#production-deployment)

---

## 🚀 Quick Start (5 minutos)

```bash
# 1. Clonar repositorio
git clone <repo_url>
cd Tesis

# 2. Copiar archivo de configuración
cp .env.example .env

# 3. Generar secrets
make generate-secrets
# Copiar JWT_SECRET_KEY y CACHE_SALT al archivo .env

# 4. Iniciar stack completo
make dev
# O: docker-compose up -d

# 5. Verificar que servicios están healthy
make ps
# O: docker-compose ps

# 6. Acceder a la aplicación
# API Swagger: http://localhost:8000/docs
# API Health:  http://localhost:8000/api/v1/health
# API Metrics: http://localhost:8000/metrics  # NEW: Prometheus metrics

# 7. (Opcional) Iniciar con monitoreo (Prometheus + Grafana)
make dev-monitoring
# O: docker-compose --profile monitoring up -d
# Grafana UI: http://localhost:3001 (admin/admin)
# Prometheus:  http://localhost:9090
```

**Resultado esperado**: API funcionando en 2-3 minutos

---

## 📦 Prerequisitos

### Software Requerido

- **Docker**: >= 20.10
- **Docker Compose**: >= 2.0
- **Make** (opcional, para shortcuts)

### Instalación Docker

#### Linux
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER  # Agregar usuario a grupo docker
```

#### Windows
Descargar e instalar [Docker Desktop](https://www.docker.com/products/docker-desktop)

#### macOS
```bash
brew install --cask docker
```

### Verificar Instalación
```bash
docker --version
# Docker version 24.0.0, build ...

docker-compose --version
# Docker Compose version v2.20.0
```

---

## ⚙️ Configuración

### 1. Archivo .env

Copiar `.env.example` a `.env` y configurar:

```bash
cp .env.example .env
```

**Variables Críticas**:

```bash
# === LLM Provider ===
LLM_PROVIDER=openai  # mock, openai, gemini
OPENAI_API_KEY=sk-proj-...  # Tu API key de OpenAI

# === Security (GENERAR NUEVOS!) ===
JWT_SECRET_KEY=<generated_with_make_generate-secrets>
CACHE_SALT=<generated_with_make_generate-secrets>

# === Database ===
DATABASE_URL=postgresql://ai_native:ai_native_password@postgres:5432/ai_native

# === Redis ===
REDIS_URL=redis://redis:6379/0

# === Environment ===
ENVIRONMENT=development  # development, staging, production
DEBUG=false
```

### 2. Generar Secrets

```bash
# Opción 1: Con Makefile
make generate-secrets

# Opción 2: Manual
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('CACHE_SALT=' + secrets.token_hex(32))"
```

**IMPORTANTE**: NO usar valores default en producción!

### 3. CORS Origins

Configurar dominios permitidos:

```bash
# Desarrollo
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Producción
ALLOWED_ORIGINS=https://app.example.com,https://www.example.com
```

---

## 🎯 Comandos Comunes

### Con Makefile (Recomendado)

```bash
make help                 # Ver todos los comandos disponibles
make dev                  # Iniciar stack de desarrollo
make dev-debug            # Iniciar con pgAdmin + Redis Commander
make stop                 # Detener stack
make down                 # Detener y eliminar containers
make logs                 # Ver logs de todos los servicios
make logs-api             # Ver logs solo del API
make ps                   # Ver estado de servicios
make db-shell             # Abrir PostgreSQL shell
make redis-cli            # Abrir Redis CLI
make test                 # Ejecutar tests
make health-check         # Verificar health de servicios
make clean                # Limpiar archivos temporales
```

### Sin Makefile

```bash
# Iniciar stack
docker-compose up -d

# Ver logs
docker-compose logs -f
docker-compose logs -f api

# Ver estado
docker-compose ps

# Detener
docker-compose stop

# Detener y eliminar containers
docker-compose down

# Detener y eliminar volúmenes (¡DANGER!)
docker-compose down -v

# Shell en container API
docker-compose exec api bash

# PostgreSQL shell
docker-compose exec postgres psql -U ai_native -d ai_native

# Redis CLI
docker-compose exec redis redis-cli
```

---

## 🏗️ Arquitectura del Stack

### Servicios Incluidos

```
┌─────────────────────────────────────────────────────────┐
│                     AI-Native Stack                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   FastAPI    │  │  PostgreSQL  │  │    Redis     │ │
│  │  (Port 8000) │  │  (Port 5432) │  │  (Port 6379) │ │
│  │              │  │              │  │              │ │
│  │ - API REST   │  │ - Sessions   │  │ - Rate Limit │ │
│  │ - 4 workers  │  │ - Traces     │  │ - LLM Cache  │ │
│  │ - Health OK  │  │ - Risks      │  │ - AOF Persist│ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘ │
│         │                 │                 │          │
│         └─────────────────┴─────────────────┘          │
│                   ai-native-network                     │
│                                                          │
│  Debug Tools (solo con --profile debug):                │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │   pgAdmin    │  │ Redis Cmdr   │                    │
│  │ (Port 5050)  │  │ (Port 8081)  │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
```

### Volúmenes Persistentes

```bash
# Ver volúmenes creados
docker volume ls | grep ai-native

# Resultado:
ai-native-postgres-data    # Datos de PostgreSQL
ai-native-redis-data       # Datos de Redis (AOF)
ai-native-pgadmin-data     # Configuración de pgAdmin
```

**IMPORTANTE**: Los volúmenes persisten entre restarts. Para eliminarlos:
```bash
docker-compose down -v  # ⚠️ ELIMINA TODOS LOS DATOS
```

---

## 🔍 Troubleshooting

### API no inicia

**Síntomas**:
```bash
docker-compose ps
# api | Restarting | unhealthy
```

**Diagnóstico**:
```bash
# Ver logs
docker-compose logs api

# Errores comunes:
# 1. "ModuleNotFoundError: No module named 'fastapi'"
#    → Problema con build de imagen
#    → Solución: docker-compose build --no-cache api

# 2. "psycopg2.OperationalError: could not connect to server"
#    → PostgreSQL no está ready
#    → Solución: Esperar 30s, PostgreSQL se está inicializando

# 3. "redis.exceptions.ConnectionError"
#    → Redis no está ready
#    → Solución: Esperar 10s, Redis se está inicializando
```

**Solución**:
```bash
# Rebuild imagen desde cero
docker-compose build --no-cache api
docker-compose up -d api
```

### PostgreSQL no conecta

**Síntomas**:
```bash
curl http://localhost:8000/api/v1/health
# Error: Database connection failed
```

**Diagnóstico**:
```bash
# Verificar que PostgreSQL está running
docker-compose ps postgres
# Debe estar en estado "healthy"

# Test de conexión manual
docker-compose exec postgres pg_isready -U ai_native
# Resultado esperado: accepting connections
```

**Solución**:
```bash
# Restart PostgreSQL
docker-compose restart postgres

# Verificar logs
docker-compose logs postgres
```

### Redis no conecta

**Síntomas**:
```bash
# Rate limiting no funciona
# Cache no funciona
```

**Diagnóstico**:
```bash
# Verificar que Redis está running
docker-compose ps redis

# Test de conexión manual
docker-compose exec redis redis-cli ping
# Resultado esperado: PONG
```

**Solución**:
```bash
# Restart Redis
docker-compose restart redis
```

### Port Already in Use

**Síntomas**:
```bash
docker-compose up -d
# Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solución**:
```bash
# Encontrar proceso usando el puerto
# Linux/macOS:
lsof -ti:8000

# Windows:
netstat -ano | findstr :8000

# Matar proceso
kill -9 <PID>  # Linux/macOS
taskkill /PID <PID> /F  # Windows

# O cambiar puerto en docker-compose.yml:
# ports:
#   - "8001:8000"  # Host:Container
```

### Slow Performance

**Síntomas**:
- API responde lento (>2s)
- Health checks timeout

**Diagnóstico**:
```bash
# Verificar uso de CPU/memoria
docker stats

# Ver logs de performance
docker-compose logs api | grep "Process-Time"
```

**Soluciones**:
1. **Aumentar workers**: Editar `Dockerfile`, cambiar `--workers 4` a `--workers 8`
2. **Aumentar recursos de Docker**: Docker Desktop → Settings → Resources
3. **Optimizar queries**: Ver logs de queries lentos en PostgreSQL

---

## 🚀 Production Deployment

### Checklist Pre-Deployment

- [ ] **Secrets generados** (JWT_SECRET_KEY, CACHE_SALT)
- [ ] **ENVIRONMENT=production** en .env
- [ ] **DEBUG=false** en .env
- [ ] **CORS origins configurados** (NO localhost)
- [ ] **Database URL apunta a PostgreSQL production**
- [ ] **Redis URL apunta a Redis production**
- [ ] **LLM provider configurado** (OpenAI API key)
- [ ] **Backup automático configurado** para PostgreSQL
- [ ] **Monitoring configurado** (Prometheus + Grafana)
- [ ] **Alertas configuradas** (Alertmanager)

### Build Production Image

```bash
# Build con tag de versión
docker build -t ai-native-mvp:v1.0.0 .

# Tag para registry
docker tag ai-native-mvp:v1.0.0 registry.example.com/ai-native-mvp:v1.0.0

# Push a registry
docker push registry.example.com/ai-native-mvp:v1.0.0
```

### Deploy con Docker Compose (Single Server)

```bash
# 1. Copiar archivos a servidor
scp docker-compose.yml user@server:/opt/ai-native/
scp .env user@server:/opt/ai-native/

# 2. SSH al servidor
ssh user@server

# 3. Iniciar stack
cd /opt/ai-native
docker-compose up -d

# 4. Verificar health
curl http://localhost:8000/api/v1/health
```

### Deploy con Kubernetes (Cluster)

Ver archivo `kubernetes_deployment.md` para deployment completo en K8s.

**Quick Kubernetes Deploy**:
```bash
# 1. Crear namespace
kubectl create namespace ai-native

# 2. Crear secrets
kubectl create secret generic ai-native-secrets \
  --from-literal=jwt-secret-key=<generated> \
  --from-literal=cache-salt=<generated> \
  --from-literal=openai-api-key=<key> \
  -n ai-native

# 3. Aplicar manifests
kubectl apply -f kubernetes/ -n ai-native

# 4. Verificar deployment
kubectl get pods -n ai-native
kubectl logs -f deployment/ai-native-api -n ai-native
```

### Backup y Restore

**Backup PostgreSQL**:
```bash
# Backup manual
docker-compose exec -T postgres pg_dump -U ai_native ai_native > backup_$(date +%Y%m%d).sql

# Backup automático (cron job)
0 2 * * * docker-compose -f /opt/ai-native/docker-compose.yml exec -T postgres pg_dump -U ai_native ai_native > /backups/ai_native_$(date +\%Y\%m\%d).sql
```

**Restore**:
```bash
docker-compose exec -T postgres psql -U ai_native -d ai_native < backup_20251125.sql
```

### Monitoring

**Health Check**:
```bash
# Health endpoint
curl http://localhost:8000/api/v1/health

# Prometheus metrics (después de implementar HIGH-01)
curl http://localhost:8000/metrics
```

**Logs**:
```bash
# Centralizar logs con ELK Stack
docker-compose logs -f | logstash ...

# O usar Docker logging driver
# docker-compose.yml:
# services:
#   api:
#     logging:
#       driver: "json-file"
#       options:
#         max-size: "10m"
#         max-file: "3"
```

---

## 📝 Comandos de Mantenimiento

### Database Maintenance

```bash
# Vacuum PostgreSQL
docker-compose exec postgres psql -U ai_native -d ai_native -c "VACUUM ANALYZE;"

# Ver tamaño de tablas
docker-compose exec postgres psql -U ai_native -d ai_native -c "SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Ver conexiones activas
docker-compose exec postgres psql -U ai_native -d ai_native -c "SELECT count(*) FROM pg_stat_activity;"
```

### Redis Maintenance

```bash
# Ver info de Redis
docker-compose exec redis redis-cli INFO

# Ver memoria usada
docker-compose exec redis redis-cli INFO memory

# Ver keys count
docker-compose exec redis redis-cli DBSIZE

# Flush cache (⚠️ DANGER)
docker-compose exec redis redis-cli FLUSHALL
```

### Docker Maintenance

```bash
# Ver uso de disco
docker system df

# Limpiar imágenes huérfanas
docker image prune -f

# Limpiar containers stopped
docker container prune -f

# Limpiar volúmenes no usados (⚠️ DANGER)
docker volume prune -f

# Limpiar todo (⚠️ DANGER)
docker system prune -a -f --volumes
```

---

## 📚 Referencias

- **Docker Docs**: https://docs.docker.com/
- **Docker Compose Docs**: https://docs.docker.com/compose/
- **PostgreSQL Tuning**: https://pgtune.leopard.in.ua/
- **Redis Best Practices**: https://redis.io/docs/management/optimization/

---

## 🎯 Próximos Pasos

Después de completar el deployment con Docker:

1. ✅ **CRITICAL-01**: Rate limiter con Redis → COMPLETADO
2. ✅ **CRITICAL-02**: Docker + docker-compose → COMPLETADO
3. ✅ **CRITICAL-03**: Cache salt → COMPLETADO
4. ✅ **HIGH-01**: Implementar Prometheus metrics → COMPLETADO
5. ⏭️ **HIGH-03**: Deep health checks (6h estimadas)

Ver `REMEDIACION_CRITICA_APLICADA.md` para detalles de las correcciones críticas.
Ver `HIGH_01_PROMETHEUS_METRICS_COMPLETADO.md` para detalles de observabilidad.

---

**Última actualización**: 2025-11-25
**Siguiente milestone**: Deep health checks (Sprint 2)