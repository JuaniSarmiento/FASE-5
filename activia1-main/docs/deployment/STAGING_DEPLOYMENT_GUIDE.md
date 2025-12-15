# 🚀 STAGING DEPLOYMENT GUIDE - AI-Native MVP

**Ambiente**: Staging
**Objetivo**: Despliegue completo del sistema AI-Native MVP en Kubernetes para testing pre-producción
**Fecha**: 2025-11-24

---

## 📋 Índice

1. [Pre-requisitos](#pre-requisitos)
2. [Arquitectura de Staging](#arquitectura-de-staging)
3. [Namespace y RBAC](#namespace-y-rbac)
4. [Secrets Management](#secrets-management)
5. [ConfigMaps](#configmaps)
6. [PostgreSQL Deployment](#postgresql-deployment)
7. [Redis Deployment](#redis-deployment)
8. [Backend Deployment](#backend-deployment)
9. [Frontend Deployment](#frontend-deployment)
10. [Ingress Configuration](#ingress-configuration)
11. [Monitoring Setup](#monitoring-setup)
12. [Verification Steps](#verification-steps)
13. [Rollback Procedures](#rollback-procedures)

---

## Pre-requisitos

### Cluster Kubernetes

**Mínimo para staging**:
- **Nodos**: 2 worker nodes
- **CPU por nodo**: 4 cores
- **RAM por nodo**: 16 GB
- **Disco por nodo**: 100 GB SSD
- **Kubernetes**: v1.28+

### Herramientas Requeridas

```bash
# Verificar instalación
kubectl version --client
helm version
docker --version

# Verificar acceso al cluster
kubectl cluster-info
kubectl get nodes
```

### Dominios y DNS

**Dominio staging**: `staging.ai-native.tu-institucion.edu.ar`

**Subdominios necesarios**:
- API: `api-staging.ai-native.tu-institucion.edu.ar`
- Frontend: `app-staging.ai-native.tu-institucion.edu.ar`
- Grafana: `grafana-staging.ai-native.tu-institucion.edu.ar`

**Configurar DNS**:
```bash
# Obtener IP del LoadBalancer
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Crear registros A en tu DNS provider:
# api-staging.ai-native.tu-institucion.edu.ar → <EXTERNAL-IP>
# app-staging.ai-native.tu-institucion.edu.ar → <EXTERNAL-IP>
```

---

## Arquitectura de Staging

```
┌─────────────────────────────────────────────────────────────┐
│                    Ingress Controller                        │
│              (Nginx + Cert-Manager SSL/TLS)                  │
│  api-staging.ai-native.* | app-staging.ai-native.*          │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
┌───────────────┐           ┌───────────────┐
│  Frontend     │           │  Backend API  │
│  Deployment   │           │  Deployment   │
│  (2 replicas) │           │  (3 replicas) │
└───────┬───────┘           └───────┬───────┘
        │                           │
        └───────────┬───────────────┘
                    ▼
        ┌───────────────────────┐
        │    PostgreSQL         │
        │    StatefulSet        │
        │    (1 replica)        │
        └───────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
   ┌─────────┐            ┌──────────┐
   │  Redis  │            │ Prometheus│
   │  (Cache)│            │ + Grafana │
   └─────────┘            └──────────┘
```

---

## Namespace y RBAC

### 1. Crear Namespace

```yaml
# kubernetes/staging/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-native-staging
  labels:
    name: ai-native-staging
    environment: staging
```

```bash
kubectl apply -f kubernetes/staging/namespace.yaml
```

### 2. Resource Quotas

```yaml
# kubernetes/staging/resource-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ai-native-staging-quota
  namespace: ai-native-staging
spec:
  hard:
    requests.cpu: "20"
    requests.memory: 40Gi
    limits.cpu: "40"
    limits.memory: 80Gi
    persistentvolumeclaims: "5"
    services.loadbalancers: "0"  # Use Ingress instead
```

```bash
kubectl apply -f kubernetes/staging/resource-quota.yaml
```

### 3. Service Account

```yaml
# kubernetes/staging/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ai-native-backend
  namespace: ai-native-staging
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ai-native-backend-role
  namespace: ai-native-staging
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ai-native-backend-binding
  namespace: ai-native-staging
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ai-native-backend-role
subjects:
- kind: ServiceAccount
  name: ai-native-backend
  namespace: ai-native-staging
```

```bash
kubectl apply -f kubernetes/staging/serviceaccount.yaml
```

---

## Secrets Management

### Generar Secrets

```bash
# 1. Generar JWT secret key
JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# 2. Generar PostgreSQL password
POSTGRES_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")

# 3. Crear secret en Kubernetes
kubectl create secret generic ai-native-secrets \
  --namespace=ai-native-staging \
  --from-literal=JWT_SECRET_KEY="$JWT_SECRET" \
  --from-literal=DATABASE_URL="postgresql://ai_native:$POSTGRES_PASSWORD@ai-native-postgresql:5432/ai_native" \
  --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
  --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY:-sk-test-123}" \
  --from-literal=GEMINI_API_KEY="${GEMINI_API_KEY:-test-123}" \
  --dry-run=client -o yaml | kubectl apply -f -

# 4. Verificar secret creado
kubectl get secret ai-native-secrets -n ai-native-staging
```

### Verificar Secrets

```bash
# Listar keys en el secret
kubectl describe secret ai-native-secrets -n ai-native-staging

# Decodificar un valor (para debug)
kubectl get secret ai-native-secrets -n ai-native-staging -o jsonpath='{.data.JWT_SECRET_KEY}' | base64 --decode
```

---

## ConfigMaps

```yaml
# kubernetes/staging/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-native-config
  namespace: ai-native-staging
data:
  # Environment
  ENVIRONMENT: "staging"
  DEBUG: "false"

  # API Server
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"

  # Database
  DB_POOL_SIZE: "20"
  DB_MAX_OVERFLOW: "40"
  DB_POOL_TIMEOUT: "30"
  DB_POOL_RECYCLE: "3600"

  # Redis Cache
  LLM_CACHE_ENABLED: "true"
  LLM_CACHE_BACKEND: "redis"
  REDIS_URL: "redis://ai-native-redis:6379/0"
  LLM_CACHE_TTL: "3600"
  LLM_CACHE_MAX_ENTRIES: "1000"

  # LLM Provider
  LLM_PROVIDER: "mock"  # Change to "openai" or "gemini" when ready
  OPENAI_MODEL: "gpt-4"
  GEMINI_MODEL: "gemini-1.5-flash"

  # CORS
  ALLOWED_ORIGINS: "https://app-staging.ai-native.tu-institucion.edu.ar"

  # Rate Limiting
  RATE_LIMIT_PER_MINUTE: "60"
  RATE_LIMIT_PER_HOUR: "1000"

  # JWT
  JWT_ALGORITHM: "HS256"
  JWT_ACCESS_TOKEN_EXPIRE_MINUTES: "30"
  JWT_REFRESH_TOKEN_EXPIRE_DAYS: "7"

  # Governance
  MAX_AI_INVOLVEMENT: "0.8"
  BLOCK_COMPLETE_SOLUTIONS: "true"
  REQUIRE_TRACEABILITY: "true"

  # Feature Flags
  ENABLE_N4_TRACEABILITY: "true"
  ENABLE_RISK_ANALYSIS: "true"
  ENABLE_PROCESS_EVALUATION: "true"
  ENABLE_GIT_INTEGRATION: "false"
```

```bash
kubectl apply -f kubernetes/staging/configmap.yaml
```

---

## PostgreSQL Deployment

### StatefulSet

```yaml
# kubernetes/staging/postgresql-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
  namespace: ai-native-staging
spec:
  serviceName: ai-native-postgresql
  replicas: 1
  selector:
    matchLabels:
      app: postgresql
  template:
    metadata:
      labels:
        app: postgresql
    spec:
      containers:
      - name: postgresql
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
          name: postgresql
        env:
        - name: POSTGRES_DB
          value: ai_native
        - name: POSTGRES_USER
          value: ai_native
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ai-native-secrets
              key: POSTGRES_PASSWORD
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        resources:
          requests:
            cpu: 500m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 8Gi
        volumeMounts:
        - name: postgresql-data
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U ai_native
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U ai_native
          initialDelaySeconds: 10
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgresql-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: standard  # Change to your storage class
      resources:
        requests:
          storage: 50Gi
```

### Service

```yaml
# kubernetes/staging/postgresql-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-native-postgresql
  namespace: ai-native-staging
  labels:
    app: postgresql
spec:
  type: ClusterIP
  ports:
  - port: 5432
    targetPort: 5432
    protocol: TCP
    name: postgresql
  selector:
    app: postgresql
```

```bash
kubectl apply -f kubernetes/staging/postgresql-statefulset.yaml
kubectl apply -f kubernetes/staging/postgresql-service.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgresql -n ai-native-staging --timeout=120s
```

### Initialize Database

```yaml
# kubernetes/staging/init-db-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: init-database
  namespace: ai-native-staging
spec:
  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: init-db
        image: your-registry.com/ai-native-backend:latest
        command:
        - python
        - scripts/init_database.py
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ai-native-secrets
              key: DATABASE_URL
```

```bash
kubectl apply -f kubernetes/staging/init-db-job.yaml
kubectl logs -f job/init-database -n ai-native-staging
```

---

## Redis Deployment

```yaml
# kubernetes/staging/redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: ai-native-staging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
          name: redis
        command:
        - redis-server
        - --appendonly
        - "yes"
        - --maxmemory
        - "512mb"
        - --maxmemory-policy
        - "allkeys-lru"
        resources:
          requests:
            cpu: 100m
            memory: 512Mi
          limits:
            cpu: 500m
            memory: 1Gi
        volumeMounts:
        - name: redis-data
          mountPath: /data
        livenessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - redis-cli
            - ping
          initialDelaySeconds: 5
          periodSeconds: 5
      volumes:
      - name: redis-data
        emptyDir: {}  # For staging, use emptyDir. For production, use PVC
---
apiVersion: v1
kind: Service
metadata:
  name: ai-native-redis
  namespace: ai-native-staging
spec:
  type: ClusterIP
  ports:
  - port: 6379
    targetPort: 6379
    name: redis
  selector:
    app: redis
```

```bash
kubectl apply -f kubernetes/staging/redis-deployment.yaml

# Verify Redis
kubectl wait --for=condition=ready pod -l app=redis -n ai-native-staging --timeout=60s
```

---

## Backend Deployment

```yaml
# kubernetes/staging/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-native-backend
  namespace: ai-native-staging
  labels:
    app: ai-native-backend
    tier: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-native-backend
  template:
    metadata:
      labels:
        app: ai-native-backend
        tier: backend
    spec:
      serviceAccountName: ai-native-backend

      # Init container to wait for PostgreSQL
      initContainers:
      - name: wait-for-db
        image: busybox:1.35
        command:
        - sh
        - -c
        - |
          until nc -z ai-native-postgresql 5432; do
            echo "Waiting for PostgreSQL..."
            sleep 2
          done
          echo "PostgreSQL is ready!"

      containers:
      - name: backend
        image: your-registry.com/ai-native-backend:latest
        imagePullPolicy: Always

        ports:
        - containerPort: 8000
          name: http
          protocol: TCP

        # Environment from Secret
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ai-native-secrets
              key: DATABASE_URL
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ai-native-secrets
              key: JWT_SECRET_KEY
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-native-secrets
              key: OPENAI_API_KEY
              optional: true

        # Environment from ConfigMap
        envFrom:
        - configMapRef:
            name: ai-native-config

        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi

        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2

        volumeMounts:
        - name: logs
          mountPath: /app/logs

      volumes:
      - name: logs
        emptyDir: {}

      # Anti-affinity to spread pods across nodes
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - ai-native-backend
              topologyKey: kubernetes.io/hostname
---
apiVersion: v1
kind: Service
metadata:
  name: ai-native-backend
  namespace: ai-native-staging
  labels:
    app: ai-native-backend
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: ai-native-backend
```

```bash
kubectl apply -f kubernetes/staging/backend-deployment.yaml

# Wait for backend pods
kubectl wait --for=condition=ready pod -l app=ai-native-backend -n ai-native-staging --timeout=180s

# Check logs
kubectl logs -f -l app=ai-native-backend -n ai-native-staging --tail=50
```

---

## Frontend Deployment

```yaml
# kubernetes/staging/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-native-frontend
  namespace: ai-native-staging
  labels:
    app: ai-native-frontend
    tier: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ai-native-frontend
  template:
    metadata:
      labels:
        app: ai-native-frontend
        tier: frontend
    spec:
      containers:
      - name: frontend
        image: your-registry.com/ai-native-frontend:latest
        imagePullPolicy: Always

        ports:
        - containerPort: 80
          name: http
          protocol: TCP

        env:
        - name: VITE_API_BASE_URL
          value: "https://api-staging.ai-native.tu-institucion.edu.ar/api/v1"

        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi

        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10

        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: ai-native-frontend
  namespace: ai-native-staging
  labels:
    app: ai-native-frontend
spec:
  type: ClusterIP
  ports:
  - port: 80
    targetPort: 80
    protocol: TCP
    name: http
  selector:
    app: ai-native-frontend
```

```bash
kubectl apply -f kubernetes/staging/frontend-deployment.yaml

# Wait for frontend pods
kubectl wait --for=condition=ready pod -l app=ai-native-frontend -n ai-native-staging --timeout=120s
```

---

## Ingress Configuration

### Install Nginx Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.service.type=LoadBalancer
```

### Install Cert-Manager (SSL/TLS)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
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
```

### Ingress Resource

```yaml
# kubernetes/staging/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-native-ingress
  namespace: ai-native-staging
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-staging
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/limit-rps: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api-staging.ai-native.tu-institucion.edu.ar
    - app-staging.ai-native.tu-institucion.edu.ar
    secretName: ai-native-staging-tls
  rules:
  - host: api-staging.ai-native.tu-institucion.edu.ar
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-native-backend
            port:
              number: 8000
  - host: app-staging.ai-native.tu-institucion.edu.ar
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-native-frontend
            port:
              number: 80
```

```bash
kubectl apply -f kubernetes/staging/ingress.yaml

# Wait for cert-manager to issue certificate
kubectl get certificate -n ai-native-staging -w

# Get Ingress external IP
kubectl get ingress -n ai-native-staging
```

---

## Monitoring Setup

### Install Prometheus + Grafana

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.retention=7d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=20Gi \
  --set grafana.ingress.enabled=true \
  --set grafana.ingress.hosts[0]=grafana-staging.ai-native.tu-institucion.edu.ar
```

### Access Grafana

```bash
# Get Grafana password
kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
echo

# Port-forward (if ingress not ready)
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Access: http://localhost:3000
# User: admin
# Pass: <from above command>
```

---

## Verification Steps

### 1. Check All Pods Running

```bash
kubectl get pods -n ai-native-staging

# Expected output:
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
# API health check
curl https://api-staging.ai-native.tu-institucion.edu.ar/api/v1/health

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "cache": "redis",
#   "timestamp": "2025-11-24T15:30:00Z"
# }
```

### 3. Test Authentication Flow

```bash
# Register user
curl -X POST https://api-staging.ai-native.tu-institucion.edu.ar/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@staging.com",
    "username": "testuser",
    "password": "Test123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST https://api-staging.ai-native.tu-institucion.edu.ar/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@staging.com",
    "password": "Test123!"
  }'
```

### 4. Test Frontend

```bash
# Open in browser
https://app-staging.ai-native.tu-institucion.edu.ar

# Expected: React app loads, can create session and interact
```

### 5. Check Logs

```bash
# Backend logs
kubectl logs -f -l app=ai-native-backend -n ai-native-staging --tail=100

# PostgreSQL logs
kubectl logs -f postgresql-0 -n ai-native-staging --tail=50

# Redis logs
kubectl logs -f -l app=redis -n ai-native-staging --tail=50
```

### 6. Check Metrics

```bash
# Prometheus targets
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# Open: http://localhost:9090/targets

# Grafana dashboards
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Open: http://localhost:3000
```

---

## Rollback Procedures

### Rollback Backend Deployment

```bash
# View rollout history
kubectl rollout history deployment/ai-native-backend -n ai-native-staging

# Rollback to previous version
kubectl rollout undo deployment/ai-native-backend -n ai-native-staging

# Rollback to specific revision
kubectl rollout undo deployment/ai-native-backend -n ai-native-staging --to-revision=2

# Check rollout status
kubectl rollout status deployment/ai-native-backend -n ai-native-staging
```

### Rollback Database Migration

```bash
# Connect to PostgreSQL pod
kubectl exec -it postgresql-0 -n ai-native-staging -- psql -U ai_native -d ai_native

# Run rollback SQL
-- (Your rollback SQL here)

# Or restore from backup
kubectl cp backup.sql postgresql-0:/tmp/backup.sql -n ai-native-staging
kubectl exec -it postgresql-0 -n ai-native-staging -- psql -U ai_native -d ai_native < /tmp/backup.sql
```

### Complete Rollback (Nuclear Option)

```bash
# Delete all resources
kubectl delete namespace ai-native-staging

# Re-deploy from scratch
# (Follow deployment steps again)
```

---

## Troubleshooting

### Pod CrashLoopBackOff

```bash
# Check pod events
kubectl describe pod <pod-name> -n ai-native-staging

# Check logs
kubectl logs <pod-name> -n ai-native-staging --previous

# Common issues:
# - Database not ready → Wait for PostgreSQL
# - Missing env vars → Check configmap/secrets
# - Port already in use → Check service config
```

### Database Connection Issues

```bash
# Test connection from backend pod
kubectl exec -it <backend-pod> -n ai-native-staging -- /bin/bash
python -c "from src.ai_native_mvp.database import get_db_session; \
           with get_db_session() as s: print('Connected!')"

# Check PostgreSQL logs
kubectl logs postgresql-0 -n ai-native-staging | grep ERROR
```

### Ingress Not Working

```bash
# Check ingress status
kubectl describe ingress ai-native-ingress -n ai-native-staging

# Check certificate
kubectl describe certificate ai-native-staging-tls -n ai-native-staging

# Check nginx controller logs
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller
```

---

## Success Criteria

Staging deployment is successful when:

- [x] All pods in `Running` state
- [x] Health endpoint returns 200 OK
- [x] Authentication flow works (register → login → access)
- [x] Frontend loads and connects to API
- [x] Database queries execute successfully
- [x] Redis cache hit rate > 0%
- [x] Metrics visible in Prometheus
- [x] Dashboards working in Grafana
- [x] SSL/TLS certificates issued
- [x] No errors in logs (except expected warnings)

---

## Next Steps

After successful staging deployment:

1. **Load Testing** → Verify performance under load
2. **Security Audit** → Penetration testing
3. **UAT (User Acceptance Testing)** → Test with real users
4. **Production Deployment** → Replicate to production

---

**Autor**: Mag. en Ing. de Software Alberto Cortez
**Fecha**: 2025-11-24
**Versión**: 1.0