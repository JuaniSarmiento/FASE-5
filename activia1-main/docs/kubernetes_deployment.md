# ☸️ Deployment en Kubernetes - AI-Native MVP

## Guía Completa de Deployment Enterprise en Kubernetes

Esta guía te ayudará a deployar el **Ecosistema AI-Native** en Kubernetes para ambientes de producción con alta disponibilidad, escalabilidad automática y gestión avanzada de recursos.

---

## 📚 Índice

1. [Introducción](#introducción)
2. [Requisitos Previos](#requisitos-previos)
3. [Arquitectura Kubernetes](#arquitectura-kubernetes)
4. [Configuración del Cluster](#configuración-del-cluster)
5. [Namespaces y RBAC](#namespaces-y-rbac)
6. [ConfigMaps y Secrets](#configmaps-y-secrets)
7. [Deployments](#deployments)
8. [Services y Networking](#services-y-networking)
9. [Ingress Controller](#ingress-controller)
10. [StatefulSets (PostgreSQL)](#statefulsets-postgresql)
11. [Persistent Volumes](#persistent-volumes)
12. [Horizontal Pod Autoscaling](#horizontal-pod-autoscaling)
13. [Monitoring con Prometheus](#monitoring-con-prometheus)
14. [Logging con EFK](#logging-con-efk)
15. [CI/CD con GitLab/GitHub Actions](#cicd)
16. [Disaster Recovery](#disaster-recovery)
17. [Troubleshooting](#troubleshooting)

---

## Introducción

### ¿Por qué Kubernetes?

Para instituciones con **500+ estudiantes concurrentes**, Kubernetes ofrece:

- ✅ **Alta disponibilidad**: Pods distribuidos en múltiples nodos
- ✅ **Escalamiento automático**: HPA (Horizontal Pod Autoscaler)
- ✅ **Auto-healing**: Reinicio automático de pods fallidos
- ✅ **Rolling updates**: Actualizaciones sin downtime
- ✅ **Gestión declarativa**: Infrastructure as Code (IaC)
- ✅ **Multi-tenancy**: Aislamiento de recursos por namespace

### Arquitectura Target

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (Ingress)                  │
│                  (SSL/TLS Termination)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
┌───────────────┐           ┌───────────────┐
│  Frontend     │           │  Backend API  │
│  Deployment   │           │  Deployment   │
│  (3 replicas) │           │  (5 replicas) │
└───────┬───────┘           └───────┬───────┘
        │                           │
        └───────────┬───────────────┘
                    ▼
        ┌───────────────────────┐
        │    PostgreSQL         │
        │    StatefulSet        │
        │  (Primary + Replicas) │
        └───────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
   ┌─────────┐            ┌──────────┐
   │  Redis  │            │ RabbitMQ │
   │  (Cache)│            │ (Queues) │
   └─────────┘            └──────────┘
```

---

## Requisitos Previos

### Cluster Kubernetes

**Mínimo recomendado para producción**:

- **Nodos**: 3+ worker nodes
- **CPU por nodo**: 8 cores
- **RAM por nodo**: 32 GB
- **Disco por nodo**: 200 GB SSD
- **Kubernetes**: v1.28+
- **CNI**: Calico o Cilium (recomendado)
- **Storage Class**: SSD-backed (gp3 en AWS, pd-ssd en GCP)

### Herramientas Necesarias

```bash
# kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client

# Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version

# kustomize (opcional)
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
sudo mv kustomize /usr/local/bin/

# k9s (dashboard interactivo - opcional pero útil)
curl -sS https://webinstall.dev/k9s | bash
```

### Verificar Acceso al Cluster

```bash
kubectl cluster-info
kubectl get nodes
kubectl get namespaces
```

---

## Arquitectura Kubernetes

### Estructura de Directorios

```
kubernetes/
├── base/                       # Manifests base (común a todos los ambientes)
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── hpa.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── postgresql/
│   │   ├── statefulset.yaml
│   │   ├── service.yaml
│   │   └── pvc.yaml
│   ├── redis/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── ingress.yaml
├── overlays/                   # Overlays por ambiente (kustomize)
│   ├── development/
│   │   └── kustomization.yaml
│   ├── staging/
│   │   └── kustomization.yaml
│   └── production/
│       └── kustomization.yaml
└── helm/                       # Helm charts (alternativa a kustomize)
    └── ai-native/
        ├── Chart.yaml
        ├── values.yaml
        ├── values-dev.yaml
        ├── values-prod.yaml
        └── templates/
```

---

## Configuración del Cluster

### Crear Namespace

```yaml
# kubernetes/base/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-native
  labels:
    name: ai-native
    environment: production
```

Aplicar:

```bash
kubectl apply -f kubernetes/base/namespace.yaml
```

### Configurar Resource Quotas

```yaml
# kubernetes/base/resource-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: ai-native-quota
  namespace: ai-native
spec:
  hard:
    requests.cpu: "50"
    requests.memory: 100Gi
    persistentvolumeclaims: "10"
    services.loadbalancers: "1"
```

### Configurar Limit Ranges

```yaml
# kubernetes/base/limit-range.yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: ai-native-limits
  namespace: ai-native
spec:
  limits:
  - max:
      cpu: "4"
      memory: "8Gi"
    min:
      cpu: "100m"
      memory: "128Mi"
    default:
      cpu: "500m"
      memory: "512Mi"
    defaultRequest:
      cpu: "200m"
      memory: "256Mi"
    type: Container
```

---

## Namespaces y RBAC

### Service Account para Backend

```yaml
# kubernetes/base/backend/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ai-native-backend
  namespace: ai-native
```

### Role y RoleBinding

```yaml
# kubernetes/base/backend/role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ai-native-backend-role
  namespace: ai-native
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
  namespace: ai-native
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: ai-native-backend-role
subjects:
- kind: ServiceAccount
  name: ai-native-backend
  namespace: ai-native
```

---

## ConfigMaps y Secrets

### ConfigMap para Configuración No Sensible

```yaml
# kubernetes/base/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-native-config
  namespace: ai-native
data:
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"

  # LLM Cache
  LLM_CACHE_ENABLED: "true"
  LLM_CACHE_TTL: "3600"
  LLM_CACHE_MAX_ENTRIES: "1000"
  LLM_CACHE_BACKEND: "redis"

  # Rate Limiting
  RATE_LIMIT_PER_MINUTE: "60"
  RATE_LIMIT_PER_HOUR: "1000"

  # CORS
  ALLOWED_ORIGINS: "https://ai-native.tu-institucion.edu.ar"

  # Redis URL (no sensible)
  REDIS_URL: "redis://ai-native-redis:6379/0"
```

### Secret para Datos Sensibles

```bash
# Crear secret desde archivo .env
kubectl create secret generic ai-native-secrets \
  --from-literal=DATABASE_URL="postgresql://ai_native:PASSWORD@ai-native-postgresql:5432/ai_native" \
  --from-literal=SECRET_KEY="tu-secret-key-seguro" \
  --from-literal=OPENAI_API_KEY="sk-proj-..." \
  --from-literal=GEMINI_API_KEY="AIzaSy..." \
  --from-literal=SMTP_PASSWORD="smtp-password" \
  --namespace ai-native

# O desde YAML (codificado en base64)
```

```yaml
# kubernetes/base/secrets.yaml (ejemplo)
apiVersion: v1
kind: Secret
metadata:
  name: ai-native-secrets
  namespace: ai-native
type: Opaque
data:
  DATABASE_URL: cG9zdGdyZXNxbDovL2FpX25hdGl2ZTpQQVNTV09SREBhaS1uYXRpdmUtcG9zdGdyZXNxbDo1NDMyL2FpX25hdGl2ZQ==
  SECRET_KEY: dHUtc2VjcmV0LWtleS1zZWd1cm8=
  OPENAI_API_KEY: c2stcHJvai14eHh4eHg=
```

**Nota**: NUNCA commitees secrets en Git. Usa herramientas como:
- **Sealed Secrets** (Bitnami)
- **External Secrets Operator**
- **HashiCorp Vault**

---

## Deployments

### Backend Deployment

```yaml
# kubernetes/base/backend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-native-backend
  namespace: ai-native
  labels:
    app: ai-native-backend
    tier: backend
spec:
  replicas: 5
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

      # Init container para esperar PostgreSQL
      initContainers:
      - name: wait-for-db
        image: busybox:1.35
        command:
        - sh
        - -c
        - |
          until nc -z ai-native-postgresql 5432; do
            echo "Esperando PostgreSQL..."
            sleep 2
          done

      containers:
      - name: backend
        image: tu-registry.com/ai-native-backend:latest
        imagePullPolicy: Always

        ports:
        - containerPort: 8000
          name: http
          protocol: TCP

        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: ai-native-secrets
              key: DATABASE_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: ai-native-secrets
              key: SECRET_KEY
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-native-secrets
              key: OPENAI_API_KEY

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
```

### Frontend Deployment

```yaml
# kubernetes/base/frontend/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-native-frontend
  namespace: ai-native
  labels:
    app: ai-native-frontend
    tier: frontend
spec:
  replicas: 3
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
        image: tu-registry.com/ai-native-frontend:latest
        imagePullPolicy: Always

        ports:
        - containerPort: 80
          name: http
          protocol: TCP

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
```

---

## Services y Networking

### Backend Service

```yaml
# kubernetes/base/backend/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-native-backend
  namespace: ai-native
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

### Frontend Service

```yaml
# kubernetes/base/frontend/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-native-frontend
  namespace: ai-native
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

### PostgreSQL Service

```yaml
# kubernetes/base/postgresql/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-native-postgresql
  namespace: ai-native
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

---

## Ingress Controller

### Instalar Nginx Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.service.type=LoadBalancer
```

### Ingress para AI-Native

```yaml
# kubernetes/base/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-native-ingress
  namespace: ai-native
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/limit-rps: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - ai-native.tu-institucion.edu.ar
    secretName: ai-native-tls
  rules:
  - host: ai-native.tu-institucion.edu.ar
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: ai-native-backend
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-native-frontend
            port:
              number: 80
```

### Instalar Cert-Manager (SSL/TLS Automático)

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Crear ClusterIssuer para Let's Encrypt
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@tu-institucion.edu.ar
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

---

## StatefulSets (PostgreSQL)

### PostgreSQL StatefulSet

```yaml
# kubernetes/base/postgresql/statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
  namespace: ai-native
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
        image: postgres:15
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
            cpu: 1000m
            memory: 4Gi
          limits:
            cpu: 4000m
            memory: 16Gi
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
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 200Gi
```

### PostgreSQL con Replicación (Primary + Replica)

Para alta disponibilidad, usa **Patroni** o **Stolon**:

```bash
# Con Helm (recomendado)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql-ha bitnami/postgresql-ha \
  --namespace ai-native \
  --set postgresql.replicaCount=2 \
  --set postgresql.database=ai_native \
  --set postgresql.username=ai_native \
  --set postgresql.password=PASSWORD \
  --set persistence.size=200Gi
```

---

## Persistent Volumes

### StorageClass SSD

```yaml
# kubernetes/base/storageclass.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/aws-ebs  # o gce-pd, azure-disk según cloud
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

### PersistentVolumeClaim para Logs

```yaml
# kubernetes/base/backend/pvc-logs.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: backend-logs
  namespace: ai-native
spec:
  accessModes:
  - ReadWriteMany
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 50Gi
```

---

## Horizontal Pod Autoscaling

### HPA para Backend

```yaml
# kubernetes/base/backend/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-native-backend-hpa
  namespace: ai-native
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-native-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 5
        periodSeconds: 60
      selectPolicy: Max
```

### Instalar Metrics Server (requerido para HPA)

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

---

## Monitoring con Prometheus

### Instalar Prometheus Stack con Helm

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=100Gi
```

### ServiceMonitor para Backend

```yaml
# kubernetes/base/backend/servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ai-native-backend
  namespace: ai-native
  labels:
    app: ai-native-backend
spec:
  selector:
    matchLabels:
      app: ai-native-backend
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Grafana Dashboards

Acceder a Grafana:

```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Abrir: http://localhost:3000
# Usuario: admin
# Password: kubectl get secret -n monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 --decode
```

Importar dashboard: ID 14282 (FastAPI)

---

## Logging con EFK

### Instalar Elasticsearch, Fluentd, Kibana

```bash
helm repo add elastic https://helm.elastic.co
helm repo update

# Elasticsearch
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --create-namespace \
  --set replicas=3 \
  --set volumeClaimTemplate.resources.requests.storage=200Gi

# Kibana
helm install kibana elastic/kibana \
  --namespace logging \
  --set service.type=LoadBalancer

# Fluentd (como DaemonSet)
kubectl apply -f https://raw.githubusercontent.com/fluent/fluentd-kubernetes-daemonset/master/fluentd-daemonset-elasticsearch.yaml
```

---

## CI/CD

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy-k8s.yml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Build Docker Images
      run: |
        docker build -t ${{ secrets.REGISTRY }}/ai-native-backend:${{ github.sha }} .
        docker build -t ${{ secrets.REGISTRY }}/ai-native-frontend:${{ github.sha }} ./frontEnd

    - name: Push to Registry
      run: |
        echo ${{ secrets.REGISTRY_PASSWORD }} | docker login -u ${{ secrets.REGISTRY_USER }} --password-stdin
        docker push ${{ secrets.REGISTRY }}/ai-native-backend:${{ github.sha }}
        docker push ${{ secrets.REGISTRY }}/ai-native-frontend:${{ github.sha }}

    - name: Deploy to Kubernetes
      uses: azure/k8s-deploy@v1
      with:
        manifests: |
          kubernetes/base/
        images: |
          ${{ secrets.REGISTRY }}/ai-native-backend:${{ github.sha }}
          ${{ secrets.REGISTRY }}/ai-native-frontend:${{ github.sha }}
        kubectl-version: 'latest'
```

---

## Disaster Recovery

### Backup Automático de PostgreSQL

```yaml
# kubernetes/base/postgresql/cronjob-backup.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgresql-backup
  namespace: ai-native
spec:
  schedule: "0 2 * * *"  # Cada día a las 2am
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15
            command:
            - /bin/sh
            - -c
            - |
              BACKUP_FILE="/backups/ai_native_$(date +\%Y-\%m-\%d_\%H-\%M-\%S).sql.gz"
              pg_dump -h ai-native-postgresql -U ai_native ai_native | gzip > $BACKUP_FILE
              echo "Backup creado: $BACKUP_FILE"
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: ai-native-secrets
                  key: POSTGRES_PASSWORD
            volumeMounts:
            - name: backups
              mountPath: /backups
          restartPolicy: OnFailure
          volumes:
          - name: backups
            persistentVolumeClaim:
              claimName: postgresql-backups
```

### Restaurar desde Backup

```bash
# Copiar backup del PVC al local
kubectl cp ai-native/postgresql-0:/backups/ai_native_2025-11-19.sql.gz ./backup.sql.gz

# Restaurar
gunzip < backup.sql.gz | kubectl exec -i -n ai-native postgresql-0 -- psql -U ai_native -d ai_native
```

---

## Troubleshooting

### Ver Logs de un Pod

```bash
# Logs en tiempo real
kubectl logs -f -n ai-native deployment/ai-native-backend

# Logs de múltiples pods
kubectl logs -f -n ai-native -l app=ai-native-backend --all-containers=true

# Logs previos (si el pod crasheó)
kubectl logs -n ai-native ai-native-backend-xyz --previous
```

### Ejecutar Comandos en un Pod

```bash
kubectl exec -it -n ai-native ai-native-backend-xyz -- /bin/bash

# Dentro del pod
python
>>> from src.ai_native_mvp.database import get_db_session
>>> # Debugging...
```

### Verificar Eventos

```bash
kubectl get events -n ai-native --sort-by='.lastTimestamp'
```

### Debug de Networking

```bash
# Desde un pod temporal
kubectl run -it --rm debug --image=nicolaka/netshoot -n ai-native -- /bin/bash

# Dentro del pod
curl http://ai-native-backend:8000/api/v1/health
nslookup ai-native-postgresql
ping ai-native-redis
```

### Verificar Recursos

```bash
# Uso actual de recursos
kubectl top pods -n ai-native
kubectl top nodes

# Describir pod con problemas
kubectl describe pod -n ai-native ai-native-backend-xyz
```

---

## Comandos Útiles

```bash
# Ver todos los recursos
kubectl get all -n ai-native

# Aplicar todos los manifests
kubectl apply -f kubernetes/base/ -R

# Eliminar deployment
kubectl delete deployment ai-native-backend -n ai-native

# Escalar manualmente
kubectl scale deployment ai-native-backend --replicas=10 -n ai-native

# Rolling restart
kubectl rollout restart deployment/ai-native-backend -n ai-native

# Ver historial de rollouts
kubectl rollout history deployment/ai-native-backend -n ai-native

# Rollback
kubectl rollout undo deployment/ai-native-backend -n ai-native

# Port-forward para debugging
kubectl port-forward -n ai-native svc/ai-native-backend 8000:8000
```

---

## Recursos Adicionales

- **Kubernetes Docs**: https://kubernetes.io/docs/
- **Helm Charts**: https://artifacthub.io/
- **Best Practices**: https://kubernetes.io/docs/concepts/configuration/overview/
- **Security**: https://kubernetes.io/docs/concepts/security/

---

**¡Deployment exitoso en Kubernetes! ☸️**

**Mag. en Ing. de Software Alberto Cortez**
Universidad Tecnológica Nacional