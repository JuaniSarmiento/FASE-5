# Load Testing - AI-Native MVP

**Autor**: Mag. Alberto Cortez
**Fecha**: 2025-11-24
**Versión**: 1.0

Este directorio contiene la infraestructura completa para realizar load testing del ecosistema AI-Native MVP.

---

## 📁 Estructura de Archivos

```
load-testing/
├── artillery-config.yml     # Configuración principal de Artillery
├── test-data.csv            # Datos de prueba (students, prompts)
├── run-load-test.sh         # Script interactivo para ejecutar tests
├── analyze-results.py       # Analizador de resultados (Python)
├── reports/                 # Reportes generados (HTML + JSON)
└── README.md                # Este archivo
```

---

## 🎯 Objetivos del Load Testing

1. **Verificar SLAs**:
   - Mean response time < 1000 ms
   - p95 response time < 2000 ms
   - p99 response time < 5000 ms
   - Error rate < 5%

2. **Validar HPA (Horizontal Pod Autoscaler)**:
   - Verificar que escale de 3 a 10 pods bajo carga
   - Confirmar que escala rápido (< 60s)
   - Validar que los nuevos pods son healthy

3. **Identificar Bottlenecks**:
   - Database connection pooling
   - Redis cache performance
   - LLM provider latency
   - Network I/O

4. **Medir Throughput**:
   - Requests por segundo (RPS)
   - Usuarios concurrentes soportados
   - Tasa de éxito

---

## 🚀 Quick Start

### Prerrequisitos

```bash
# Node.js 18+ y npm
node --version  # v18.0.0+
npm --version   # 9.0.0+

# Artillery (se instala automáticamente si no está)
npm install -g artillery

# Python 3.8+ (para análisis)
python --version  # 3.8+
```

### Ejecución Rápida

```bash
# 1. Navegar al directorio
cd load-testing

# 2. Dar permisos de ejecución
chmod +x run-load-test.sh
chmod +x analyze-results.py

# 3. Ejecutar test interactivo
./run-load-test.sh

# Opciones disponibles:
# 1) Quick test (1 minute, 10 RPS)
# 2) Standard test (5 minutes, 30 RPS)
# 3) Stress test (10 minutes, 50-100 RPS)
# 4) Full test (15 minutes, as configured)
# 5) Spike test (2 minutes, sudden spike to 200 RPS)
```

---

## 📊 Tipos de Tests

### 1. Quick Test (Smoke Test)

**Duración**: 1 minuto
**Carga**: 10 RPS constante
**Objetivo**: Verificar que el sistema responde correctamente

```bash
./run-load-test.sh
# Opción 1
```

**Uso**: Antes de tests más pesados, para detectar errores básicos.

### 2. Standard Test (Load Test)

**Duración**: 5 minutos
**Carga**: 30 RPS constante
**Objetivo**: Simular carga normal de producción

```bash
./run-load-test.sh
# Opción 2
```

**Uso**: Validar comportamiento bajo carga típica (50-100 estudiantes concurrentes).

### 3. Stress Test

**Duración**: 10 minutos
**Carga**: Ramp-up de 20 → 50 → 100 RPS
**Objetivo**: Identificar límites del sistema

```bash
./run-load-test.sh
# Opción 3
```

**Uso**: Descubrir en qué punto el sistema comienza a degradarse.

**Fases**:
- 0-5 min: Warm-up (20 RPS)
- 5-10 min: Stress phase 1 (50 RPS)
- 10-15 min: Stress phase 2 (100 RPS)

### 4. Full Test (Comprehensive)

**Duración**: 15 minutos
**Carga**: 5 → 50 → 100 → 200 RPS (configurado en `artillery-config.yml`)
**Objetivo**: Test completo con todos los escenarios

```bash
./run-load-test.sh
# Opción 4
```

**Fases**:
1. Warm-up: 2 min @ 5 RPS
2. Ramp-up: 3 min @ 5→50 RPS
3. Sustained load: 5 min @ 50 RPS
4. Peak load: 3 min @ 100 RPS
5. Spike test: 1 min @ 200 RPS

**Escenarios** (weighted):
- 10% Health checks
- 20% Create session
- 15% Get session
- 40% Process interaction (heavy)
- 10% List sessions
- 5% Get cognitive path

### 5. Spike Test

**Duración**: 2.5 minutos
**Carga**: 10 RPS → 200 RPS (spike) → 10 RPS
**Objetivo**: Verificar recuperación después de picos

```bash
./run-load-test.sh
# Opción 5
```

**Uso**: Simular tráfico repentino (ej: inicio de clase con 200 estudiantes simultáneos).

---

## 📈 Análisis de Resultados

### Generación de Reportes

Artillery genera automáticamente:

1. **JSON Report**: Datos crudos en `/tmp/artillery-report-*.json`
2. **HTML Report**: Dashboard visual en `./reports/artillery-report-*.html`

### Análisis Automático con Python

```bash
# Ejecutar analizador
python analyze-results.py /tmp/artillery-report-full.json
```

**Output**:
- ✅ Executive summary (requests, status codes, response times)
- 📊 Performance analysis (SLA compliance)
- 🚀 Scalability analysis (HPA behavior over time)
- 💡 Recommendations (optimizaciones sugeridas)

**Ejemplo de salida**:

```
==============================================================
LOAD TEST RESULTS - EXECUTIVE SUMMARY
==============================================================

📊 Virtual Users:
   Created:   5000
   Completed: 4985
   Success Rate: 99.70%

🌐 HTTP Requests:
   Total Requests:  12500
   Total Responses: 12485

📈 HTTP Status Codes:
   ✅ 200: 12200 (97.7%)
   ⚠️ 400: 150 (1.2%)
   ❌ 500: 135 (1.1%)

⏱️  Response Times:
   Min:    45 ms
   Max:    3850 ms
   Mean:   780 ms
   Median: 650 ms
   p95:    1650 ms
   p99:    2900 ms

❌ Errors:
   Timeouts:         15
   Connection Refused: 0
   Not Found:        0
   Total Errors:     15
   Error Rate:       0.12%

🚀 Throughput:
   Requests/sec (mean): 83.3
   Requests/sec (max):  195.2

==============================================================
PERFORMANCE ANALYSIS (SLA Compliance)
==============================================================

SLA Targets:
   Mean response time:  < 1000 ms
   95th percentile:     < 2000 ms
   99th percentile:     < 5000 ms

Actual Performance:
   MEAN: 780 ms (target: 1000 ms) ✅ PASS
   P95: 1650 ms (target: 2000 ms) ✅ PASS
   P99: 2900 ms (target: 5000 ms) ✅ PASS

Error Rate: 0.12% (target: < 5.0%) ✅ PASS

==============================================================
RECOMMENDATIONS
==============================================================

✅ No critical issues found. System performing within SLAs.
```

---

## 🔍 Monitoreo Durante Tests

### Terminal 1: Ejecutar Load Test

```bash
./run-load-test.sh
```

### Terminal 2: Monitorear HPA

```bash
# Monitorear scaling en tiempo real
watch -n 2 kubectl get hpa -n ai-native-staging

# Output esperado:
# NAME                    REFERENCE                       TARGETS   MINPODS   MAXPODS   REPLICAS
# ai-native-backend-hpa   Deployment/ai-native-backend   75%/70%   3         10        7
```

### Terminal 3: Monitorear Pods

```bash
# Ver pods escalando
watch -n 2 'kubectl get pods -n ai-native-staging -l app=ai-native-backend'

# Ver resource usage
watch -n 5 'kubectl top pods -n ai-native-staging'
```

### Terminal 4: Logs del Backend

```bash
# Ver logs en tiempo real
kubectl logs -f -l app=ai-native-backend -n ai-native-staging --tail=50
```

---

## 🎯 Escenarios de Test

Los escenarios están configurados en `artillery-config.yml`:

### 1. Health Check (Weight: 10%)

**Endpoint**: `GET /api/v1/health`
**Propósito**: Baseline ligero para medir overhead mínimo

```yaml
- get:
    url: "/api/v1/health"
    expect:
      - statusCode: 200
      - contentType: json
```

### 2. Create Session (Weight: 20%)

**Endpoint**: `POST /api/v1/sessions`
**Propósito**: Operación común, crea sesión nueva

```yaml
- post:
    url: "/api/v1/sessions"
    json:
      student_id: "load_test_{{ $randomString() }}"
      activity_id: "prog2_tp1_colas"
      mode: "TUTOR"
```

### 3. Get Session (Weight: 15%)

**Endpoint**: `GET /api/v1/sessions/{id}`
**Propósito**: Read operation, test database query performance

### 4. Process Interaction (Weight: 40%)

**Endpoint**: `POST /api/v1/interactions`
**Propósito**: Operación más pesada (LLM, CRPE, N4 traces)

**Flow**:
1. Create session
2. Process interaction (prompt from CSV)
3. Think time (3s) - simula usuario leyendo respuesta

### 5. List Sessions (Weight: 10%)

**Endpoint**: `GET /api/v1/sessions?page=1&page_size=20`
**Propósito**: Test pagination y queries complejas

### 6. Get Cognitive Path (Weight: 5%)

**Endpoint**: `GET /api/v1/traces/{session_id}/cognitive-path`
**Propósito**: Query más compleja (joins, aggregations)

---

## 📋 Métricas Clave

### Response Time (Latencia)

- **Mean**: Promedio de todos los requests
- **Median**: Valor en el percentil 50
- **p95**: 95% de requests por debajo de este valor
- **p99**: 99% de requests por debajo de este valor

**SLAs**:
- Mean < 1000 ms
- p95 < 2000 ms
- p99 < 5000 ms

### Throughput (Rendimiento)

- **RPS**: Requests por segundo
- **Concurrent Users**: Usuarios simultáneos
- **Requests Total**: Total de requests en el test

**Target**: 50-100 RPS sostenido

### Error Rate (Confiabilidad)

- **HTTP 2xx**: Success rate
- **HTTP 4xx**: Client errors
- **HTTP 5xx**: Server errors
- **Timeouts**: ETIMEDOUT, ECONNREFUSED

**SLA**: < 5% error rate

### Scalability (HPA)

- **Pod count**: Número de pods en cada momento
- **Scaling time**: Tiempo desde detección hasta pod ready
- **Resource usage**: CPU/Memory por pod

**Target**: Scale de 3 a 10 pods en < 60s

---

## 🔧 Configuración Avanzada

### Personalizar Test en `artillery-config.yml`

```yaml
config:
  target: "https://api-staging.ai-native.tu-institucion.edu.ar"

  phases:
    # Personaliza fases aquí
    - duration: 60      # 1 minuto
      arrivalRate: 10   # 10 usuarios/segundo
      name: "Custom phase"

  # Timeouts
  http:
    timeout: 30        # 30 segundos
    pool: 50           # 50 conexiones simultáneas

  # SLAs
  ensure:
    maxErrorRate: 5    # Max 5% errores
    p95: 2000          # p95 < 2000ms
    p99: 5000          # p99 < 5000ms
```

### Agregar Nuevos Escenarios

```yaml
scenarios:
  - name: "My Custom Scenario"
    weight: 10
    flow:
      - post:
          url: "/api/v1/custom-endpoint"
          json:
            key: "value"
          expect:
            - statusCode: 200
```

### Usar Datos Dinámicos

El archivo `test-data.csv` contiene datos de prueba que se rotan en cada request:

```csv
student_id,activity_id,prompt
student_001,prog2_tp1,¿Qué es una cola?
student_002,prog2_tp1,¿Cómo implemento enqueue?
```

**Variables disponibles**:
- `{{ student_id }}`
- `{{ activity_id }}`
- `{{ prompt }}`
- `{{ $randomString() }}` - String aleatorio
- `{{ $randomNumber() }}` - Número aleatorio

---

## 🐛 Troubleshooting

### Error: "Cannot connect to target"

```bash
# Verificar que el backend esté corriendo
curl http://localhost:8000/api/v1/health

# O en staging
curl https://api-staging.ai-native.tu-institucion.edu.ar/api/v1/health
```

### Error: "ECONNREFUSED"

**Causa**: Backend no está escuchando en el puerto esperado

**Solución**:
```bash
# Verificar pods
kubectl get pods -n ai-native-staging

# Ver logs
kubectl logs -f -l app=ai-native-backend -n ai-native-staging
```

### Error: "ETIMEDOUT"

**Causa**: Requests tardan más del timeout (default: 30s)

**Solución**: Aumentar timeout en `artillery-config.yml`:
```yaml
http:
  timeout: 60  # 60 segundos
```

### High Error Rate (>5%)

**Causas posibles**:
1. Database connection pool exhausted
2. Redis cache no configurado
3. LLM provider rate limits
4. HPA no escala rápido suficiente

**Soluciones**:
```bash
# 1. Verificar DB connections
kubectl logs -f postgresql-0 -n ai-native-staging | grep "connection"

# 2. Verificar Redis
kubectl logs -f -l app=redis -n ai-native-staging

# 3. Verificar HPA
kubectl describe hpa ai-native-backend-hpa -n ai-native-staging

# 4. Aumentar replicas mínimas
kubectl patch hpa ai-native-backend-hpa -n ai-native-staging -p '{"spec":{"minReplicas":5}}'
```

### Slow Response Times

**Checklist**:
- [ ] ¿Redis cache habilitado?
- [ ] ¿Database pooling configurado? (P1.3)
- [ ] ¿Índices creados en database?
- [ ] ¿LLM provider respondiendo rápido?
- [ ] ¿HPA escaló suficientemente?

**Profile endpoint lento**:
```bash
# Ver logs con tiempos de respuesta
kubectl logs -f -l app=ai-native-backend -n ai-native-staging | grep "Process time"
```

---

## 📚 Referencias

- **Artillery Docs**: https://www.artillery.io/docs
- **Kubernetes HPA**: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/
- **Staging Deployment**: `../kubernetes/staging/README.md`
- **Fase 1 Completada**: `../FASE1_COMPLETADA.md`

---

## ✅ Checklist de Verificación

Antes de aprobar el sistema para producción:

### Pre-Test
- [ ] Staging environment deployed
- [ ] All pods healthy
- [ ] Database initialized
- [ ] Redis cache enabled
- [ ] HPA configured

### During Test
- [ ] Monitor HPA scaling
- [ ] Watch pod resource usage
- [ ] Check backend logs for errors
- [ ] Verify database connections

### Post-Test
- [ ] Analyze Artillery HTML report
- [ ] Run Python analyzer
- [ ] Review recommendations
- [ ] Document findings
- [ ] Address critical issues

### SLAs
- [ ] Mean response time < 1000 ms
- [ ] p95 < 2000 ms
- [ ] p99 < 5000 ms
- [ ] Error rate < 5%
- [ ] HPA scales correctly

---

**Próximo Paso**: Paso 3 - Security Audit

---

**Autor**: Mag. Alberto Cortez
**Fecha**: 2025-11-24
**Versión**: 1.0