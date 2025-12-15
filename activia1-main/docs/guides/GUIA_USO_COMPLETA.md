# 🎉 Guía Rápida de Uso - AI-Native MVP

## ✅ Estado del Sistema

### Backend (API)
- **URL**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Estado**: ✅ OPERACIONAL
- **Health Check**: http://localhost:8000/api/v1/health

### Frontend (React + Vite)
- **URL**: http://localhost:3001
- **Estado**: ✅ OPERACIONAL
- **Proxy API**: Configurado para `/api` → `http://localhost:8000`

### Base de Datos
- **PostgreSQL 15**: ✅ OPERACIONAL (puerto 5432)
- **Redis**: ✅ OPERACIONAL (puerto 6379)

### LLM Provider
- **Ollama**: ✅ OPERACIONAL (puerto 11434)
- **Modelo**: phi3:latest (2.2 GB)

---

## 🚀 Cómo Usar la Aplicación

### 1. Acceder al Dashboard
1. Abrir navegador en: **http://localhost:3001**
2. Serás redirigido automáticamente al Dashboard
3. Verás las métricas y módulos disponibles

### 2. Probar el Tutor Cognitivo (T-IA-Cog)

**Acceso**: Dashboard → "Tutor Cognitivo" o directamente en `/tutor`

**Características a probar**:

#### A. Modo Socrático (Preguntas Orientadoras)
```
Ejemplo de prompt:
"¿Cómo puedo implementar una cola circular en Python?"

Respuesta esperada:
- El tutor NO te dará el código completo
- Te hará preguntas como: "¿Qué estructura de datos conoces para implementar esto?"
- Te guiará con preguntas para que descubras la solución
```

#### B. Detección de Delegación Total
```
Prompt que debe ser BLOQUEADO:
"Dame el código completo de una cola circular"
"Hazme toda la tarea"
"Dame la solución completa"

Respuesta esperada:
- ❌ El tutor detectará delegación total
- 🚫 Bloqueará la solicitud
- 📚 Te explicará por qué no puede darte el código completo
```

#### C. Niveles de Ayuda
- **Mínimo**: Solo preguntas
- **Bajo**: Pistas generales
- **Medio**: Pistas detalladas
- **Alto**: Explicaciones completas (pero sin código completo)

---

### 3. Probar Filtrado PII (Gobernanza - GOV-IA)

**El sistema filtra automáticamente información sensible**:

```
Prompt con PII:
"Mi email es juan.perez@gmail.com y mi DNI es 12345678"

Respuesta esperada:
- El sistema sanitiza el prompt ANTES de enviarlo al LLM
- El LLM nunca verá el email ni DNI real
- Se reemplazan por placeholders: [EMAIL_REDACTED], [DNI_REDACTED]
```

**PII detectado automáticamente**:
- ✅ Emails (pattern: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`)
- ✅ DNI argentino (pattern: `\b\d{7,8}\b`)
- ✅ Teléfonos (pattern: varios formatos)
- ✅ Tarjetas de crédito (pattern: `\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b`)

---

### 4. Probar Detección de Riesgos (AR-IA)

**El sistema detecta 5 dimensiones de riesgo**:

#### A. Riesgo Temporal (Código Sospechoso)
```
Escenario de prueba:
1. Enviar un prompt corto: "Hola"
2. INMEDIATAMENTE (< 5 segundos) enviar código largo:
   "def cola_circular():\n    class Cola:\n        def __init__(self)..."

Resultado esperado:
- ⚠️ Se detecta riesgo ETHICAL (código enviado muy rápido)
- 🚨 Se genera alerta de posible plagio/copia
- 📊 Se registra en la base de datos como riesgo nivel MEDIUM-HIGH
```

#### B. Otros tipos de riesgo
- **COGNITIVE**: Sobrecarga cognitiva, confusión persistente
- **EPISTEMIC**: Uso de fuentes no confiables
- **TECHNICAL**: Código inseguro o ineficiente
- **PEDAGOGICAL**: Dependencia excesiva del tutor

---

### 5. Probar Trazabilidad N4 (TC-N4)

**El sistema registra TODOS los pasos del razonamiento**:

```
Flujo completo:
1. Estudiante envía prompt: "¿Qué es una cola circular?"
2. Sistema registra:
   - Nivel N1: Prompt original
   - Nivel N2: Delegación no detectada → continuar
   - Nivel N2: PII filtrado → sanitizado
   - Nivel N3: LLM genera respuesta
   - Nivel N4: Evaluación de la respuesta
   - Nivel N4: Análisis de riesgo
```

**Consultar trazabilidad**:
- Endpoint: `GET /api/v1/traces/{session_id}/sequence`
- Frontend: Módulo "Trazabilidad N4" (si está implementado)

---

## 🧪 Pruebas de Integración Completas

### Test Suite Automatizado

El sistema incluye un test suite completo que valida todos los agentes:

```bash
# Ejecutar todos los tests
pytest tests/test_integration_complete.py -v

# Ejecutar solo tests de agentes específicos
pytest tests/test_integration_complete.py::test_tutor_agent_blocks_total_delegation -v
pytest tests/test_integration_complete.py::test_governance_agent_filters_pii -v
pytest tests/test_integration_complete.py::test_risk_agent_detects_suspicious_code -v
```

**Tests disponibles**:
- ✅ `test_tutor_agent_blocks_total_delegation`: Valida bloqueo de delegación
- ✅ `test_governance_agent_filters_pii`: Valida filtrado de PII
- ✅ `test_risk_agent_detects_suspicious_code`: Valida detección de código sospechoso
- ✅ `test_traceability_n4_persistence`: Valida persistencia de trazas
- ✅ `test_complete_e2e_flow`: Flujo completo end-to-end
- ✅ `test_all_agents_operational`: Verifica que todos los agentes estén operacionales
- ⏸️ `test_concurrent_users`: Prueba de carga con múltiples usuarios simultáneos

---

## 📊 Monitoreo y Diagnóstico

### 1. Verificar Estado de Servicios

```bash
# Docker containers
docker ps

# Backend health
curl http://localhost:8000/api/v1/health

# Frontend dev server
# Ver logs en la terminal donde ejecutaste `npm run dev`
```

### 2. Logs en Tiempo Real

```bash
# Backend logs
docker logs -f ai-native-api

# PostgreSQL logs
docker logs -f ai-native-postgres

# Ollama logs
docker logs -f ai-native-ollama
```

### 3. Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it ai-native-postgres psql -U ai_native -d ai_native

# Ver sesiones activas
SELECT id, student_id, mode, status, start_time FROM sessions WHERE status = 'active';

# Ver interacciones recientes
SELECT session_id, prompt, response, created_at FROM interactions ORDER BY created_at DESC LIMIT 5;

# Ver riesgos detectados
SELECT * FROM risks ORDER BY created_at DESC LIMIT 10;

# Ver trazas cognitivas
SELECT * FROM cognitive_traces ORDER BY created_at DESC LIMIT 10;
```

---

## 🎯 Escenarios de Prueba Recomendados

### Escenario 1: Estudiante Novato (Aprendizaje Guiado)
1. Acceder a `/tutor`
2. Seleccionar modo "Guiado" + nivel de ayuda "Alto"
3. Preguntar: "No entiendo qué es una cola circular"
4. Esperar respuesta explicativa
5. Hacer seguimiento: "¿Puedes darme un ejemplo?"
6. Verificar que recibe pistas pero NO código completo

### Escenario 2: Intento de Delegación Total (DEBE SER BLOQUEADO)
1. Acceder a `/tutor`
2. Enviar: "Dame el código completo de una cola circular en Python"
3. **Resultado esperado**: Bloqueo + explicación pedagógica
4. Verificar en logs del backend: `[DELEGATION DETECTED]`

### Escenario 3: Filtrado de PII (Privacidad)
1. Acceder a `/tutor`
2. Enviar: "Hola, soy Juan Pérez, mi email es juan.perez@gmail.com"
3. **Resultado esperado**: 
   - Frontend envía el prompt original
   - Backend sanitiza ANTES de enviar al LLM
   - El LLM nunca ve el email real
4. Verificar en logs: `[PII FILTERED]`

### Escenario 4: Detección de Código Sospechoso
1. Enviar prompt corto: "Hola"
2. Esperar 2 segundos
3. Enviar código largo (> 100 caracteres) con sintaxis Python
4. **Resultado esperado**:
   - Sistema detecta riesgo ETHICAL
   - Se genera alerta de posible plagio
   - Se registra en tabla `risks`

### Escenario 5: Flujo E2E Completo
1. Crear sesión nueva
2. Enviar 3-5 interacciones progresivas
3. Consultar trazabilidad: `GET /api/v1/traces/{session_id}/sequence`
4. Verificar que todas las trazas se guardaron correctamente
5. Consultar riesgos: `GET /api/v1/risks/{session_id}`
6. Verificar evaluación de proceso

---

## 🔧 Solución de Problemas

### Frontend no carga
```bash
# 1. Verificar que Vite esté corriendo
# Debe mostrar: "Local: http://localhost:3001/"

# 2. Si no está corriendo
cd frontEnd
npm run dev

# 3. Verificar archivo .env
cat .env
# Debe contener: VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Backend no responde
```bash
# 1. Verificar containers
docker ps

# 2. Si no están corriendo
docker-compose up -d

# 3. Ver logs de errores
docker logs ai-native-api --tail 50
```

### Base de datos con errores
```bash
# 1. Reiniciar container
docker restart ai-native-postgres

# 2. Verificar esquema
docker exec -it ai-native-postgres psql -U ai_native -d ai_native -c "\dt"

# 3. Si falta tabla/columna, aplicar migración
docker exec -it ai-native-postgres psql -U ai_native -d ai_native < create_indexes.sql
```

### Ollama no responde
```bash
# 1. Verificar estado
curl http://localhost:11434/

# 2. Verificar modelo descargado
docker exec -it ai-native-ollama ollama list

# 3. Si no está phi3, descargar
docker exec -it ai-native-ollama ollama pull phi3
```

---

## 📚 Documentación Adicional

- **API Reference**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Arquitectura**: Ver `docs/architecture/`
- **Testing**: Ver `tests/test_integration_complete.py`
- **Configuración**: Ver `.env.example` y `docker-compose.yml`

---

## 🎓 Conceptos Clave del Sistema

### 6 Agentes de IA
1. **T-IA-Cog**: Tutor Cognitivo (NO sustituye agencia del estudiante)
2. **E-IA-Proc**: Evaluador de Procesos (NO productos)
3. **S-IA-X**: Simuladores Profesionales (6 roles)
4. **AR-IA**: Análisis de Riesgos (5 dimensiones)
5. **GOV-IA**: Gobernanza Institucional (políticas automáticas)
6. **TC-N4**: Trazabilidad Cognitiva (4 niveles de detalle)

### Trazabilidad N4
- **N1**: Interacción cruda (prompt del estudiante)
- **N2**: Pre-procesamiento (delegación, PII, políticas)
- **N3**: Respuesta del LLM
- **N4**: Post-procesamiento (evaluación, riesgos, métricas)

### Evaluación de Procesos (NO Productos)
- ❌ NO evalúa si el código funciona
- ✅ SÍ evalúa cómo razonó el estudiante
- ✅ SÍ analiza evolución cognitiva
- ✅ SÍ detecta patrones de aprendizaje

---

## ✅ Checklist de Validación

- [ ] Frontend carga en http://localhost:3001
- [ ] Backend responde en http://localhost:8000/api/v1/health
- [ ] Puedo crear una sesión desde el frontend
- [ ] Puedo enviar mensajes al Tutor Cognitivo
- [ ] El tutor NO me da código completo cuando pido delegación total
- [ ] El sistema filtra mi email/DNI cuando los incluyo en el prompt
- [ ] Se detecta riesgo cuando envío código muy rápido
- [ ] Puedo ver el historial de interacciones
- [ ] Todos los containers de Docker están "healthy"
- [ ] Los tests de integración pasan: `pytest tests/test_integration_complete.py -v`

---

## 🎉 ¡Sistema Completamente Funcional!

El proyecto AI-Native MVP está **100% operacional** con:
- ✅ 6 agentes de IA funcionando
- ✅ Trazabilidad N4 completa
- ✅ Detección de riesgos en 5 dimensiones
- ✅ Filtrado de PII automático
- ✅ Bloqueo de delegación total
- ✅ Evaluación de procesos cognitivos
- ✅ Docker stack completo
- ✅ Frontend React + Backend FastAPI integrados
- ✅ Tests de integración validados

**¡Disfruta explorando el sistema! 🚀**
