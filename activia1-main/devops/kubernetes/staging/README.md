# Kubernetes Staging Deployment - AI-Native MVP

Este directorio contiene todos los manifests necesarios para desplegar el ecosistema AI-Native MVP en un ambiente de staging en Kubernetes.

## 📁 Estructura de Archivos

```
kubernetes/staging/
├── 01-namespace.yaml          # Namespace, ResourceQuota, LimitRange
├── 02-configmap.yaml          # Configuración no sensible
├── 03-secrets.yaml.example    # Template para secrets (NO COMMITEAR)
├── 04-postgresql.yaml         # PostgreSQL StatefulSet + Service
├── 05-redis.yaml              # Redis Deployment + Service (P1.2)
├── 06-backend.yaml            # Backend API + HPA
├── 07-frontend.yaml           # Frontend React
├── 08-ingress.yaml            # Ingress con SSL/TLS
├── deploy.sh                  # Script de deployment automático
├── setup-ingress.sh           # Setup de Nginx Ingress + Cert-Manager
├── verify.sh                  # Verificación completa del deployment
├── init-database.sh           # Inicialización del schema de base de datos
├── rollback.sh                # Herramienta de rollback y cleanup
├── monitor.sh                 # Dashboard de monitoreo en tiempo real
└── README.md                  # Este archivo
```

## 🚀 Quick Start

### Prerrequisitos

1. **Cluster Kubernetes** con acceso configurado
2. **kubectl** instalado y configurado
3. **helm** instalado (para Nginx Ingress y Cert-Manager)
4. **jq** instalado (para scripts de verificación)

### Deployment Rápido

```bash
# 0. Setup Nginx Ingress + Cert-Manager (primera vez)
chmod +x setup-ingress.sh
./setup-ingress.sh

# 1. Generar secrets
JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
POSTGRES_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")

kubectl create secret generic ai-native-secrets \
  --namespace=ai-native-staging \
  --from-literal=JWT_SECRET_KEY="$JWT_SECRET" \
  --from-literal=DATABASE_URL="postgresql://ai_native:$POSTGRES_PASSWORD@ai-native-postgresql:5432/ai_native" \
  --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
  --from-literal=GEMINI_API_KEY="${GEMINI_API_KEY:-}"

# 2. Ejecutar script de deployment
chmod +x deploy.sh
./deploy.sh

# 3. Inicializar base de datos
chmod +x init-database.sh
./init-database.sh

# 4. Verificar deployment
chmod +x verify.sh
./verify.sh

# 5. Monitorear (opcional)
chmod +x monitor.sh
./monitor.sh
```

## 📝 Deployment Manual (Paso a Paso)

### 1. Namespace y Base

```bash
kubectl apply -f 01-namespace.yaml
```

Crea:
- Namespace `ai-native-staging`
- ResourceQuota (límites de recursos)
- LimitRange (defaults para contenedores)

### 2. ConfigMap

```bash
kubectl apply -f 02-configmap.yaml
```

Configura variables de entorno no sensibles:
- Environment: staging
- Database pool: 20 conexiones (P1.3)
- Redis cache: habilitado (P1.2)
- LLM Provider: mock (cambiar a openai/gemini cuando esté listo)
- Rate limiting: 60/min, 1000/hora

### 3. Secrets

```bash
# Generar secrets seguros
JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
POSTGRES_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")

# Crear secret en Kubernetes
kubectl create secret generic ai-native-secrets \
  --namespace=ai-native-staging \
  --from-literal=JWT_SECRET_KEY="$JWT_SECRET" \
  --from-literal=DATABASE_URL="postgresql://ai_native:$POSTGRES_PASSWORD@ai-native-postgresql:5432/ai_native" \
  --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
  --from-literal=GEMINI_API_KEY="${GEMINI_API_KEY:-}"
```

**IMPORTANTE**: NUNCA commitear secrets al repositorio!

### 4. PostgreSQL

```bash
kubectl apply -f 04-postgresql.yaml

# Esperar a que esté listo
kubectl wait --for=condition=ready pod -l app=postgresql -n ai-native-staging --timeout=120s

# Verificar logs
kubectl logs -f postgresql-0 -n ai-native-staging
```

Despliega:
- StatefulSet con 1 replica
- Persistent Volume (50Gi)
- Service ClusterIP en puerto 5432
- Health checks (liveness + readiness)

### 5. Redis

```bash
kubectl apply -f 05-redis.yaml

# Esperar a que esté listo
kubectl wait --for=condition=ready pod -l app=redis -n ai-native-staging --timeout=60s
```

Despliega:
- Deployment con 1 replica
- Configurado para LRU eviction
- Max memory: 512MB
- AOF persistence habilitada

### 6. Backend API

```bash
kubectl apply -f 06-backend.yaml

# Esperar a que esté listo
kubectl wait --for=condition=ready pod -l app=ai-native-backend -n ai-native-staging --timeout=180s

# Ver logs
kubectl logs -f -l app=ai-native-backend -n ai-native-staging --tail=50
```

Despliega:
- Deployment con 3 replicas
- HPA: min 3, max 10 (escala automático)
- Init containers: espera PostgreSQL + Redis
- Anti-affinity: distribuye pods en nodos diferentes
- Health checks en `/api/v1/health`

### 7. Frontend

```bash
kubectl apply -f 07-frontend.yaml

# Esperar a que esté listo
kubectl wait --for=condition=ready pod -l app=ai-native-frontend -n ai-native-staging --timeout=120s
```

Despliega:
- Deployment con 2 replicas
- Configurado con VITE_API_BASE_URL apuntando a staging

### 8. Ingress

```bash
# Primero instalar Nginx Ingress Controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Instalar Cert-Manager (para SSL/TLS automático)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Crear ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    email: admin@tu-institucion.edu.ar
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Desplegar Ingress
kubectl apply -f 08-ingress.yaml

# Ver status
kubectl get ingress -n ai-native-staging
kubectl describe ingress ai-native-ingress -n ai-native-staging
```

## ✅ Verificación

### 1. Verificar Pods

```bash
kubectl get pods -n ai-native-staging

# Expected:
# NAME                                  READY   STATUS    RESTARTS   AGE
# ai-native-backend-xxx                 1/1     Running   0          5m
# ai-native-backend-yyy                 1/1     Running   0          5m
# ai-native-backend-zzz                 1/1     Running   0          5m
# ai-native-frontend-aaa                1/1     Running   0          5m
# ai-native-frontend-bbb                1/1     Running   0          5m
# postgresql-0                          1/1     Running   0          10m
# redis-xxx                             1/1     Running   0          8m
```

### 2. Test Health Endpoint

```bash
# Obtener IP del Ingress
INGRESS_IP=$(kubectl get ingress ai-native-ingress -n ai-native-staging -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test con curl (antes de configurar DNS)
curl -H "Host: api-staging.ai-native.tu-institucion.edu.ar" http://$INGRESS_IP/api/v1/health

# Después de configurar DNS
curl https://api-staging.ai-native.tu-institucion.edu.ar/api/v1/health
```

### 3. Ver Logs

```bash
# Backend logs
kubectl logs -f -l app=ai-native-backend -n ai-native-staging --tail=100

# PostgreSQL logs
kubectl logs -f postgresql-0 -n ai-native-staging --tail=50

# Redis logs
kubectl logs -f -l app=redis -n ai-native-staging --tail=50
```

### 4. Verificar HPA

```bash
kubectl get hpa -n ai-native-staging

# Ver métricas
kubectl top pods -n ai-native-staging
```

## 🔧 Troubleshooting

### Pod en CrashLoopBackOff

```bash
# Ver eventos
kubectl describe pod <pod-name> -n ai-native-staging

# Ver logs previos
kubectl logs <pod-name> -n ai-native-staging --previous
```

### Database Connection Issues

```bash
# Conectar a PostgreSQL
kubectl exec -it postgresql-0 -n ai-native-staging -- psql -U ai_native -d ai_native

# Test desde backend pod
kubectl exec -it <backend-pod> -n ai-native-staging -- python -c \
  "from src.ai_native_mvp.database import get_db_session; \
   with get_db_session() as s: print('DB Connected!')"
```

### Ingress No Funciona

```bash
# Ver status del certificado
kubectl get certificate -n ai-native-staging
kubectl describe certificate ai-native-staging-tls -n ai-native-staging

# Ver logs del ingress controller
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

## 🔄 Actualización

### Update Backend Image

```bash
# Editar deployment
kubectl set image deployment/ai-native-backend \
  backend=your-registry.com/ai-native-backend:v2.0.0 \
  -n ai-native-staging

# Ver progreso
kubectl rollout status deployment/ai-native-backend -n ai-native-staging

# Rollback si hay problemas
kubectl rollout undo deployment/ai-native-backend -n ai-native-staging
```

### Update ConfigMap

```bash
# Editar configmap
kubectl edit configmap ai-native-config -n ai-native-staging

# Reiniciar pods para aplicar cambios
kubectl rollout restart deployment/ai-native-backend -n ai-native-staging
```

## 🗑️ Cleanup

```bash
# Eliminar todo el namespace
kubectl delete namespace ai-native-staging

# O eliminar recursos individualmente
kubectl delete -f 08-ingress.yaml
kubectl delete -f 07-frontend.yaml
kubectl delete -f 06-backend.yaml
kubectl delete -f 05-redis.yaml
kubectl delete -f 04-postgresql.yaml
kubectl delete -f 02-configmap.yaml
kubectl delete secret ai-native-secrets -n ai-native-staging
kubectl delete -f 01-namespace.yaml
```

## 🛠️ Scripts Auxiliares

El directorio incluye scripts para facilitar operaciones comunes:

### 1. setup-ingress.sh

Instala y configura Nginx Ingress Controller y Cert-Manager automáticamente.

```bash
chmod +x setup-ingress.sh
./setup-ingress.sh
```

**Qué hace**:
- Añade repositorios Helm (ingress-nginx, jetstack)
- Instala Nginx Ingress Controller con 2 replicas
- Instala Cert-Manager v1.13.0 con CRDs
- Crea ClusterIssuers para Let's Encrypt (staging + production)
- Descubre la IP del LoadBalancer
- Muestra instrucciones para configurar DNS

**Cuándo usar**: Primera vez que despliegas en un cluster nuevo.

### 2. verify.sh

Verifica el estado completo del deployment staging.

```bash
chmod +x verify.sh
./verify.sh
```

**Qué hace**:
- Verifica prerrequisitos (kubectl, curl, jq)
- Comprueba namespace, ConfigMap, Secrets
- Valida estado de todos los pods (PostgreSQL, Redis, Backend, Frontend)
- Verifica servicios y LoadBalancer IP
- Comprueba certificado SSL/TLS
- Test de endpoints API (/health, /ping)
- Muestra resource usage y HPA status
- Genera reporte de verificación con errores/warnings

**Resultado**:
- ✅ Exit 0: Todo OK
- ⚠️ Exit 0: Warnings (normal en los primeros minutos)
- ✗ Exit 1: Errores críticos (necesita corrección)

### 3. init-database.sh

Inicializa el schema de base de datos en PostgreSQL.

```bash
chmod +x init-database.sh
./init-database.sh
```

**Qué hace**:
- Verifica que PostgreSQL pod esté ready
- Crea todas las tablas (sessions, activities, cognitive_traces, risks, evaluations, etc.)
- Crea índices compuestos para optimizar queries
- Configura triggers para updated_at automático
- Opcionalmente crea datos de ejemplo

**Cuándo usar**: Después de desplegar PostgreSQL, antes de iniciar el backend.

### 4. monitor.sh

Dashboard interactivo de monitoreo en tiempo real.

```bash
chmod +x monitor.sh
./monitor.sh
```

**Opciones disponibles**:
1. Watch all pods (live updates)
2. Watch backend logs (live)
3. Watch frontend logs (live)
4. Watch PostgreSQL logs (live)
5. Watch Redis logs (live)
6. Show resource usage (CPU/Memory)
7. Show recent events
8. Show ingress status
9. Test API endpoints
10. Show HPA status
11. Full dashboard (combined view)

**Uso típico**: Mantener abierto en una terminal para ver logs en tiempo real durante troubleshooting.

### 5. rollback.sh

Herramienta de rollback y cleanup.

```bash
chmod +x rollback.sh
./rollback.sh
```

**Opciones**:
1. Rollback backend deployment (a versión previa)
2. Rollback frontend deployment (a versión previa)
3. Delete all resources (⚠️ PELIGRO: elimina todo)
4. Rollback backend a revisión específica
5. Rollback frontend a revisión específica
6. Show deployment history

**Uso típico**: Cuando un deployment nuevo causa problemas y necesitas volver a la versión anterior.

**Ejemplo de rollback**:
```bash
./rollback.sh
# Opción 1: Rollback backend
# Espera a que complete
# Verifica: kubectl get pods -n ai-native-staging
```

## 📊 Monitoring

Para configurar monitoring completo (Prometheus + Grafana), ver:
- `../../docs/kubernetes_deployment.md` (sección Monitoring)
- `../../STAGING_DEPLOYMENT_GUIDE.md` (sección Monitoring Setup)

### Workflow Típico de Deployment

```bash
# 1. Primera vez en cluster nuevo
./setup-ingress.sh

# 2. Crear secrets (ver Quick Start)

# 3. Desplegar todo
./deploy.sh

# 4. Inicializar base de datos
./init-database.sh

# 5. Verificar deployment
./verify.sh

# 6. Si hay errores: monitorear logs
./monitor.sh
# Seleccionar opción 2 (Backend logs) o 11 (Dashboard completo)

# 7. Configurar DNS según output de setup-ingress.sh
# Ejemplo:
#   api-staging.ai-native.tu-institucion.edu.ar → 34.123.45.67
#   app-staging.ai-native.tu-institucion.edu.ar → 34.123.45.67

# 8. Esperar certificado SSL (5-10 minutos)
watch kubectl get certificate -n ai-native-staging

# 9. Test final
curl https://api-staging.ai-native.tu-institucion.edu.ar/api/v1/health
```

## 🔐 Security

**Checklist de seguridad**:
- [x] Secrets nunca commiteados
- [x] JWT secret key generado aleatoriamente
- [x] PostgreSQL password generado aleatoriamente
- [x] SSL/TLS habilitado (Cert-Manager)
- [x] Rate limiting configurado
- [x] Security headers en Ingress
- [x] RBAC limitado (ServiceAccount con permisos mínimos)
- [x] Resource limits configurados
- [x] Network policies (TODO - opcional)

## 📚 Referencias

- **Documentación completa**: `../../STAGING_DEPLOYMENT_GUIDE.md`
- **Kubernetes deployment**: `../../docs/kubernetes_deployment.md`
- **Fase 1 Production Readiness**: `../../FASE1_COMPLETADA.md`

---

**Autor**: Mag. Alberto Cortez
**Fecha**: 2025-11-24
**Versión**: 1.0