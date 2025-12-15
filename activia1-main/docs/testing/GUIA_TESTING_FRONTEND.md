# 🧪 Guía de Testing del Frontend - Sistema Completo

## ✅ Estado de Integración

### **COMPLETAMENTE INTEGRADO** - Listo para probar

Todos los módulos del backend están integrados en el frontend y funcionando:

## 📋 Componentes Disponibles

### 1️⃣ **Sesiones** (`/sessions`)
- ✅ Crear nuevas sesiones de aprendizaje
- ✅ Listar sesiones existentes
- ✅ Ver detalles de cada sesión
- **Endpoint**: `/api/v1/sessions`

### 2️⃣ **Tutor IA (T-IA-Cog)** (`/tutor`)
- ✅ Chat interactivo con el tutor cognitivo
- ✅ Generación de trazas cognitivas automáticas
- ✅ Historial de conversaciones
- **Endpoint**: `/api/v1/interactions`

### 3️⃣ **Simuladores Profesionales (S-IA-X)** (`/simulators`)
- ✅ 4 simuladores disponibles:
  - **Product Owner**: Gestión de backlog y user stories
  - **Scrum Master**: Sprint planning y ceremonias ágiles
  - **Tech Interviewer**: Entrevistas técnicas y SOLID
  - **DevSecOps**: CI/CD y seguridad
- **Endpoint**: `/api/v1/simulators/interact`
- **Timeout**: 60 segundos

### 4️⃣ **Análisis de Riesgos (AR-IA)** (`/risks`)
- ✅ **NUEVO**: Análisis automático por sesión
- ✅ Detección de riesgos en 5 dimensiones
- ✅ Recomendaciones y estrategias de mitigación
- ✅ Visualización por nivel (CRITICAL, HIGH, MEDIUM, LOW)
- **Endpoints**:
  - `POST /api/v1/risks/analyze-session/{session_id}` ⭐ NUEVO
  - `GET /api/v1/events` (lista eventos del simulador)
  - `POST /api/v1/events` (crear eventos)

### 5️⃣ **Evaluaciones (E-IA-Proc)** (`/evaluations`)
- ✅ Generación de evaluación cognitiva con LLM
- ✅ 5 dimensiones evaluadas:
  - Planning (Planificación)
  - Execution (Ejecución)
  - Debugging (Depuración)
  - Reflection (Reflexión)
  - Autonomy (Autonomía)
- ✅ Score de metacognición
- ✅ Ratio de delegación a IA
- **Endpoint**: `POST /api/v1/evaluations/{session_id}/generate`
- **Timeout**: 120 segundos (procesamiento LLM)

### 6️⃣ **Trazabilidad (TC-N4)** (`/traceability`)
- ✅ **NUEVO**: Grafo completo de 4 niveles por sesión
- ✅ Niveles:
  - **Nivel 1**: Eventos de Simulador
  - **Nivel 2**: Trazas Cognitivas
  - **Nivel 3**: Riesgos Detectados
  - **Nivel 4**: Evaluaciones
- ✅ Resumen estadístico
- ✅ Distribución de riesgos
- ✅ Promedio de involucramiento de IA
- **Endpoint**: `GET /api/v1/traceability/session/{session_id}` ⭐ NUEVO
- **Timeout**: 45 segundos

### 7️⃣ **Git Analytics** (`/analytics`)
- ✅ Análisis de commits y contribuciones
- ✅ Métricas de calidad de código
- **Endpoint**: `/api/v1/git-analytics/{session_id}`

---

## 🚀 Cómo Probar el Sistema Completo

### **PASO 1: Verificar que todo está corriendo**

```powershell
# Backend (Docker)
docker ps
# Deberías ver: ai-native-api, ai-native-postgres, ai-native-redis, ai-native-ollama

# Verificar salud del backend
curl http://localhost:8000/api/v1/health

# Frontend
# Debería estar en http://localhost:5173
```

### **PASO 2: Flujo Completo de Testing Manual**

#### 1. **Crear Sesión** (`/sessions`)
1. Ve a http://localhost:5173/sessions
2. Haz clic en "Nueva Sesión"
3. Completa:
   - Student ID: `test_student_001`
   - Activity ID: `test_scrum_project`
   - Mode: `TUTOR`
4. **Copia el Session ID generado** (lo necesitarás para los siguientes pasos)

#### 2. **Interactuar con Tutor IA** (`/tutor`)
1. Ve a http://localhost:5173/tutor
2. Ingresa el Session ID de arriba
3. Haz 2-3 preguntas de programación, por ejemplo:
   - "¿Cómo implemento una cola en Python?"
   - "Explícame la diferencia entre lista y tupla"
   - "¿Qué es recursión?"
4. Verás respuestas del LLM y trazas cognitivas creadas

#### 3. **Probar Simuladores** (`/simulators`)
1. Ve a http://localhost:5173/simulators
2. Crea **sesiones nuevas** para cada simulador (cada uno necesita su propia sesión):

**Product Owner:**
- Session ID: (nueva sesión con mode=SIMULATOR, simulator_type=product_owner)
- Pregunta: "Ayúdame a crear un backlog para un e-commerce"

**Scrum Master:**
- Session ID: (nueva sesión)
- Pregunta: "¿Cómo hago un sprint planning para 5 devs?"

**Tech Interviewer:**
- Session ID: (nueva sesión)
- Pregunta: "Explícame el principio de responsabilidad única"

**DevSecOps:**
- Session ID: (nueva sesión)
- Pregunta: "¿Cómo configuro CI/CD con OWASP?"

#### 4. **Crear Eventos Manualmente** (Opcional)
Usa Postman o curl para crear eventos que generen riesgos:

```bash
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "TU_SESSION_ID",
    "event_type": "deployment_completed",
    "event_data": {
      "environment": "production",
      "tests_executed": false,
      "version": "v1.0.0"
    },
    "description": "Deploy sin tests",
    "severity": "critical"
  }'
```

#### 5. **Analizar Riesgos** (`/risks`) ⭐ NUEVO
1. Ve a http://localhost:5173/risks
2. Ingresa el **Session ID de la sesión ORIGINAL** (del paso 1)
3. Haz clic en "Analizar Riesgos"
4. **Espera 5-10 segundos**
5. Verás:
   - Lista de riesgos detectados automáticamente
   - Nivel de cada riesgo (CRITICAL, HIGH, MEDIUM, LOW)
   - Dimensión (Técnico, Seguridad, Operacional, etc.)
   - Recomendaciones específicas
   - Estrategias de mitigación

**Eventos que generan riesgos automáticamente:**
- `backlog_created` sin `has_acceptance_criteria` → Riesgo HIGH
- `technical_decision_made` sin `justification` → Riesgo MEDIUM
- `deployment_completed` sin `tests_executed` → Riesgo HIGH
- `security_scan_complete` con `vulnerabilities` → Riesgo CRITICAL

#### 6. **Generar Evaluación** (`/evaluations`)
1. Ve a http://localhost:5173/evaluations
2. Ingresa el **mismo Session ID** del paso 1
3. Haz clic en "Generar Evaluación"
4. **Espera 30-90 segundos** (procesamiento LLM con Ollama)
5. Verás:
   - 5 scores de 0-10 (Planning, Execution, Debugging, Reflection, Autonomy)
   - Nivel de competencia (novice/competent/proficient/expert)
   - Score de metacognición
   - Ratio de delegación a IA
   - Feedback general detallado

#### 7. **Ver Trazabilidad Completa** (`/traceability`) ⭐ NUEVO
1. Ve a http://localhost:5173/traceability
2. Ingresa el **mismo Session ID**
3. Haz clic en "Obtener Trazabilidad"
4. Verás:
   - **Resumen**: Total de eventos, trazas, riesgos, evaluaciones
   - **Grafo de 4 niveles**: Eventos → Trazas → Riesgos → Evaluaciones
   - **Artefactos relacionados**: Cada elemento con sus hijos
   - **Distribución de riesgos**: Por nivel (CRITICAL, HIGH, etc.)
   - **Promedio de involucramiento de IA**

---

## 🎯 Flujo de Testing Rápido (5 minutos)

Si quieres probar todo rápidamente:

```bash
# 1. Verificar backend
curl http://localhost:8000/api/v1/health

# 2. Crear sesión
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "quick_test_001",
    "activity_id": "quick_test",
    "mode": "TUTOR"
  }'
# COPIA EL SESSION_ID DE LA RESPUESTA

# 3. Interacción con tutor
curl -X POST http://localhost:8000/api/v1/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID_AQUI",
    "prompt": "¿Cómo implemento una cola en Python?"
  }'

# 4. Crear evento problemático
curl -X POST http://localhost:8000/api/v1/events \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID_AQUI",
    "event_type": "deployment_completed",
    "event_data": {"tests_executed": false},
    "severity": "critical"
  }'

# 5. Analizar riesgos
curl -X POST http://localhost:8000/api/v1/risks/analyze-session/SESSION_ID_AQUI

# 6. Generar evaluación (TARDA 30-90s)
curl -X POST http://localhost:8000/api/v1/evaluations/SESSION_ID_AQUI/generate

# 7. Ver trazabilidad
curl http://localhost:8000/api/v1/traceability/session/SESSION_ID_AQUI
```

---

## 📊 Test End-to-End Automatizado

Ya existe un test automatizado que prueba todo el flujo:

```bash
pytest tests/test_e2e_full_workflow.py -v --no-cov
```

**Duración**: ~4-5 minutos  
**Pasos**: 7 (sesión, tutor, simuladores, eventos, riesgos, evaluación, trazabilidad)  
**Estado**: ✅ **PASANDO** (validado el 2025-12-09)

---

## 🔍 Endpoints Nuevos Integrados

| Endpoint | Método | Descripción | Timeout |
|----------|--------|-------------|---------|
| `/api/v1/events` | POST | Crear evento de simulador | 10s |
| `/api/v1/events` | GET | Listar eventos (filtros: session_id, student_id) | 10s |
| `/api/v1/risks/analyze-session/{id}` | POST | ⭐ Análisis automático de riesgos | 60s |
| `/api/v1/traceability/session/{id}` | GET | ⭐ Grafo completo de 4 niveles | 45s |
| `/api/v1/evaluations/{id}/generate` | POST | Evaluación con LLM (Ollama) | 120s |

---

## ⚙️ Configuración de Timeouts

Los siguientes timeouts están configurados en `apiClient.ts`:

- **Default**: 30 segundos
- **Simuladores**: 60 segundos
- **Análisis de Riesgos**: 60 segundos
- **Trazabilidad**: 45 segundos
- **Evaluaciones**: 120 segundos (procesamiento LLM)

---

## 🐛 Troubleshooting

### Error: "Backend no responde"
```bash
docker ps  # Verificar que ai-native-api está corriendo
docker logs ai-native-api --tail 50  # Ver logs
docker restart ai-native-api  # Reiniciar
```

### Error: "Timeout en evaluación"
- Es normal que tarde 30-90 segundos
- Ollama necesita cargar el modelo la primera vez
- Si persiste, verifica: `docker logs ai-native-ollama`

### Error: "No se detectan riesgos"
- Asegúrate de haber creado **eventos** primero
- Los eventos deben tener condiciones específicas (ej: `tests_executed: false`)
- Usa `POST /api/v1/events` para crear eventos manualmente

### Frontend no actualiza
```bash
cd frontEnd
npm run dev  # Reiniciar servidor de desarrollo
```

---

## 📝 Notas Importantes

1. **Session ID único**: Cada simulador necesita su propia sesión
2. **Eventos generan riesgos**: El AR-IA analiza eventos automáticamente
3. **LLM tarda**: La evaluación puede tardar 30-90s la primera vez
4. **Trazabilidad completa**: Conecta eventos → trazas → riesgos → evaluaciones
5. **Limpieza automática**: El test e2e limpia sesiones al finalizar

---

## ✅ Checklist de Funcionalidades

- [x] Crear sesiones
- [x] Tutor IA con trazas cognitivas
- [x] 4 simuladores profesionales
- [x] Crear eventos de simulador
- [x] Análisis automático de riesgos (AR-IA)
- [x] Evaluación con LLM (E-IA-Proc)
- [x] Trazabilidad de 4 niveles (TC-N4)
- [x] Frontend integrado completamente
- [x] Test end-to-end automatizado

---

## 🎉 ¡Todo Listo para Probar!

El sistema está **100% integrado** y listo para testing manual. Abre http://localhost:5173 y sigue el flujo de arriba.

**Disfruta probando el sistema completo!** 🚀
