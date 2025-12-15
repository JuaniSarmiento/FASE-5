# Guía de Testing Integral - Sprint 1 y Sprint 2

**Proyecto**: Ecosistema AI-Native para Enseñanza-Aprendizaje de Programación
**Fecha**: 2025-11-20
**Autor**: Mag. Alberto Cortez
**Versión**: 1.0

---

## Resumen Ejecutivo

Este documento describe el plan y ejecución de testing integral para validar las funcionalidades implementadas en Sprint 1 (MVP Core) y Sprint 2 (Evaluación + API).

### Objetivos del Testing

✅ Validar todas las historias de usuario de Sprint 1 (6 HUs - 55 SP)
✅ Validar todas las historias de usuario de Sprint 2 (9 HUs - 120 SP)
✅ Asegurar cobertura de código ≥70% (requisito en pytest.ini)
✅ Validar flujos end-to-end completos de estudiante, docente y administrador
✅ Garantizar cumplimiento de TODOS los criterios de aceptación

### Alcance Total

| Sprint | Historias | Story Points | Tests Planeados |
|--------|-----------|--------------|-----------------|
| Sprint 1 | 6 HUs | 55 SP | ~90 tests |
| Sprint 2 | 9 HUs | 120 SP | ~145 tests |
| **TOTAL** | **15 HUs** | **175 SP** | **~235 tests** |

---

## Manual de Ejecución de Tests

### Prerequisitos

```bash
# 1. Activar entorno virtual
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Unix/macOS

# 2. Instalar dependencias de testing
pip install -r requirements.txt
# Incluye: pytest, pytest-cov, pytest-mock, httpx (para tests API)

# 3. Inicializar base de datos de testing
python scripts/init_database.py --database-url "sqlite:///test_ai_native.db"
```

### Comandos de Ejecución

#### 1. Ejecutar TODOS los tests con coverage

```bash
pytest tests/ -v --cov=src/ai_native_mvp --cov-report=html --cov-report=term
```

**Salida esperada**:
- Número total de tests ejecutados
- Cobertura ≥70% (pytest.ini)
- Reporte HTML en `htmlcov/index.html`

#### 2. Tests de Sprint 1 solamente

```bash
pytest tests/test_sprint1_*.py -v
```

**Tests incluidos**:
- `test_sprint1_sessions.py` (HU-EST-001)
- `test_sprint1_tutor.py` (HU-EST-002)
- `test_sprint1_governance.py` (HU-EST-003)
- `test_sprint1_crpe.py` (HU-SYS-001)
- `test_sprint1_governance_agent.py` (HU-SYS-002)
- `test_sprint1_traceability.py` (HU-SYS-003)

#### 3. Tests de Sprint 2 solamente

```bash
pytest tests/test_sprint2_*.py -v
```

**Tests incluidos**:
- `test_sprint2_adaptive_hints.py` (HU-EST-004)
- `test_sprint2_justifications.py` (HU-EST-005)
- `test_sprint2_formative_feedback.py` (HU-EST-007)
- `test_sprint2_evaluator.py` (HU-SYS-004)
- `test_sprint2_risk_analyst.py` (HU-SYS-005)
- `test_sprint2_api_endpoints.py` (HU-SYS-007)
- `test_sprint2_activities.py` (HU-DOC-001)

#### 4. Tests de Integración y E2E

```bash
pytest tests/test_integration_e2e.py -v
```

**Escenarios validados**:
- Sesión exitosa completa
- Sesión con delegación bloqueada
- Sesión con múltiples riesgos
- Workflow docente completo
- API end-to-end completo

#### 5. Tests de API específicamente

```bash
pytest tests/test_api_endpoints.py tests/test_sprint2_api_endpoints.py -v
```

**Endpoints testeados**: 15+ endpoints REST

#### 6. Tests por marcadores (pytest markers)

```bash
pytest -m "sprint1" -v      # Solo Sprint 1
pytest -m "sprint2" -v      # Solo Sprint 2
pytest -m "integration" -v  # Solo integración
pytest -m "api" -v          # Solo API
pytest -m "unit" -v         # Solo unitarios
```

#### 7. Tests de Performance

```bash
pytest tests/test_performance.py -v
```

**Métricas validadas**:
- Procesamiento de interacción <2 segundos
- CRPE clasifica en <500ms
- Queries optimizadas (no N+1)
- API responde <2 segundos

---

## Sprint 1 - Tests Implementados

### HU-EST-001: Iniciar Sesión (8 tests)

**Archivo**: `tests/test_sprint1_sessions.py`

```python
def test_create_session_success()
def test_create_session_generates_unique_id()
def test_create_session_sets_active_status()
def test_create_session_validates_mode()
def test_create_session_persists_to_database()
def test_api_create_session_endpoint()
def test_api_create_session_invalid_mode()
def test_api_get_session_by_id()
```

**Criterios validados**:
- ✅ Sistema permite crear sesión con student_id, activity_id, mode
- ✅ Sistema genera session_id único
- ✅ Sesión se registra en DB con timestamp
- ✅ Sistema confirma creación
- ✅ Usuario ve qué agente AI está activo

---

### HU-EST-002: Consultar Conceptos (10 tests)

**Archivo**: `tests/test_sprint1_tutor.py`

```python
def test_conceptual_query_returns_explanation()
def test_conceptual_query_no_complete_code()
def test_conceptual_query_includes_socratic_questions()
def test_conceptual_query_classified_correctly()
def test_conceptual_query_n4_trace_captured()
def test_conceptual_query_cognitive_state_exploration()
def test_conceptual_query_low_ai_involvement()
def test_conceptual_query_not_blocked()
def test_complete_conceptual_interaction_flow()
def test_multiple_conceptual_queries_sequence()
```

**Criterios validados**:
- ✅ Tutor responde con explicación conceptual, analogías, preguntas
- ✅ Tutor NO entrega código completo
- ✅ Solicitud clasificada correctamente por CRPE
- ✅ Traza N4 captura estado EXPLORACION_CONCEPTUAL
- ✅ AI involvement bajo (0.2-0.3)
- ✅ Sistema no bloquea consulta conceptual

---

### HU-EST-003: Bloqueo Delegación (13 tests)

**Archivo**: `tests/test_sprint1_governance.py`

```python
def test_delegation_detection_explicit()
def test_delegation_detection_variants()
def test_delegation_blocks_before_generation()
def test_delegation_returns_pedagogical_message()
def test_delegation_n4_trace_blocked_true()
def test_delegation_governance_action_logged()
def test_delegation_risk_detected()
def test_delegation_offers_decomposition_guide()
def test_delegation_counts_for_risk_analysis()
def test_configurable_delegation_patterns()
def test_delegation_full_workflow()
def test_multiple_delegation_attempts()
def test_delegation_after_valid_interactions()
```

**Criterios validados**:
- ✅ Sistema bloquea delegación total
- ✅ Mensaje pedagógico explica POR QUÉ
- ✅ Guía a descomponer problema
- ✅ Bloqueo ANTES de generar código
- ✅ Traza N4 con blocked=true
- ✅ Riesgo COGNITIVE_DELEGATION registrado
- ✅ Interacción cuenta para análisis de riesgos

---

### HU-SYS-001: CRPE (20 tests)

**Archivo**: `tests/test_sprint1_crpe.py`

Tests de clasificación cognitiva:
- Clasifica consulta conceptual
- Clasifica delegación total
- Clasifica implementación
- Clasifica debugging
- Clasifica validación

Tests de estados cognitivos:
- Detecta EXPLORACION_CONCEPTUAL
- Detecta PLANIFICACION
- Detecta IMPLEMENTACION
- Detecta VALIDACION

Tests de estrategia pedagógica:
- Calcula delegation_level
- Considera historial estudiante
- Retorna estrategia estructurada
- Determina help_level
- Requiere justificación flag
- Performance <500ms

**Criterios validados**:
- ✅ Clasificación de tipo de solicitud
- ✅ Determinación de estado cognitivo
- ✅ Cálculo de nivel de delegación
- ✅ Consideración de historial
- ✅ Retorno de estrategia pedagógica
- ✅ Performance <500ms
- ✅ Tests cubren todos los tipos

---

### HU-SYS-002: GOV-IA (15 tests)

**Archivo**: `tests/test_sprint1_governance_agent.py`

Tests de políticas:
- Carga políticas globales
- Carga políticas de actividad
- Verifica max_help_level
- Bloquea soluciones completas si policy
- Enforcea umbrales de riesgo

Tests de bloqueo:
- Bloquea ANTES de ejecución
- Retorna mensaje pedagógico
- Registra evento de gobernanza
- Permite solicitudes válidas

Tests de integración:
- GOV-IA + CRPE integración
- Jerarquía de políticas
- Consistencia en múltiples sesiones

**Criterios validados**:
- ✅ Carga políticas global + actividad
- ✅ Verifica max_help_level, block_complete_solutions, umbrales
- ✅ Bloquea ANTES si viola política
- ✅ Retorna mensaje pedagógico
- ✅ Registra evento de gobernanza
- ✅ Tests para cada tipo de política

---

### HU-SYS-003: TC-N4 (20 tests)

**Archivo**: `tests/test_sprint1_traceability.py`

Tests de trazas N4:
- Creación con todos campos N4
- Incluye session_id
- trace_level = N4_COGNITIVO
- interaction_type apropiado
- cognitive_state capturado
- cognitive_intent capturado
- content capturado completo
- ai_involvement calculado
- metadata incluida
- Persiste en DB
- Trazas inmutables
- Timestamps precisos
- Ordenamiento correcto

Tests de secuencias:
- TraceSequence creación
- Representa camino cognitivo
- Reconstrucción completa
- Múltiples estados cognitivos
- Correlación con riesgos
- Query de camino cognitivo

**Criterios validados**:
- ✅ Cada interacción genera CognitiveTrace con N4
- ✅ Incluye session_id, trace_level=N4_COGNITIVO
- ✅ interaction_type, cognitive_state, cognitive_intent capturados
- ✅ content, ai_involvement, metadata incluidos
- ✅ Persiste en CognitiveTraceDB
- ✅ Forma TraceSequence
- ✅ Trazas inmutables

---

## Sprint 2 - Tests a Implementar

### HU-EST-004: Pistas Graduadas (15 tests)

**Archivo**: `tests/test_sprint2_adaptive_hints.py`

Tests de niveles de pistas:
- Nivel MINIMO: pregunta socrática
- Nivel BAJO: pregunta + orientación
- Nivel MEDIO: pista conceptual + ejemplo
- Nivel ALTO: fragmento + pseudocódigo

Tests de adaptación:
- Reduce nivel después de >5 pistas
- Reduce nivel si AI dependency >60%
- Considera historial estudiante
- AI involvement incrementa (0.3→0.5→0.7)

Tests de pistas:
- Enfocada en parte específica
- Traza N4 captura nivel
- Nunca da solución completa
- Escalado progresivo BAJO→MEDIO→ALTO

Tests de integración:
- Escalado completo workflow
- Adaptación basada en performance
- Correlación con evaluación

**Criterios esperados**:
- ✅ Pistas en 4 niveles
- ✅ Ajuste según historial
- ✅ AI involvement incrementa
- ✅ Enfocada en parte específica
- ✅ Traza N4 captura nivel
- ✅ Nunca solución completa

---

### HU-EST-005: Justificación Decisiones (12 tests)

**Archivo**: `tests/test_sprint2_justifications.py`

Tests de captura:
- Captura decisión con justificación
- Traza N4 con cognitive_intent=JUSTIFICATION
- Incluye alternativas consideradas
- Incluye razonamiento explícito

Tests de detección:
- Detecta decisiones sin justificación
- Calcula ratio justificadas/no justificadas
- Alerta LOW (50-70%)
- Alerta MEDIUM (30-50%)
- Alerta HIGH (<30%)
- Justificaciones alimentan evaluación

Tests de integración:
- Workflow completo: decisión→captura→análisis→alerta
- Decisiones mixtas (justificadas + no justificadas)

**Criterios esperados**:
- ✅ Tutor pregunta "¿Por qué elegiste X?"
- ✅ Justificación en traza N4 con cognitive_intent=JUSTIFICATION
- ✅ Alternativas capturadas
- ✅ Detecta falta de justificación
- ✅ Riesgo LACK_JUSTIFICATION emitido
- ✅ Alimenta E-IA-Proc

---

### HU-EST-007: Feedback Formativo (12 tests)

**Archivo**: `tests/test_sprint2_formative_feedback.py`

Tests de generación:
- Genera feedback al cerrar sesión
- Incluye nivel de competencia
- Incluye puntajes por dimensión
- Incluye fortalezas identificadas
- Incluye áreas de mejora
- Incluye recomendaciones accionables

Tests de versiones:
- Versión student-friendly
- Versión técnica para docentes
- Enfoque formativo (no punitivo)
- Persiste y es accesible

Tests de integración:
- Sesión completa → evaluación → feedback
- Evolución entre sesiones

**Criterios esperados**:
- ✅ E-IA-Proc genera reporte con competencia y score
- ✅ Dimensiones evaluadas
- ✅ Fortalezas y mejoras identificadas
- ✅ Formativo, no punitivo
- ✅ Recomendaciones accionables
- ✅ Almacenado y accesible

---

### HU-SYS-004: E-IA-Proc (18 tests)

**Archivo**: `tests/test_sprint2_evaluator.py`

Tests de análisis:
- Analiza secuencia de trazas N4
- Coherencia del camino cognitivo
- Calidad de justificaciones
- Nivel de autorregulación
- Manejo de errores
- Dependencia de IA

Tests de reporte:
- Genera EvaluationReport completo
- overall_competency_level
- overall_score (0-10)
- Dimensiones con puntajes
- key_strengths
- improvement_areas
- Formativo (no punitivo)
- Se dispara al cerrar sesión
- Persiste en EvaluationDB

Tests de integración:
- Workflow completo: sesión→trazas→análisis→reporte→persistencia
- Múltiples estados cognitivos
- Correlación con riesgos

**Criterios esperados**:
- ✅ Analiza coherencia, justificaciones, autorregulación, errores, AI dependency
- ✅ Genera EvaluationReport completo
- ✅ Dimensiones evaluadas
- ✅ Fortalezas y mejoras
- ✅ Formativo
- ✅ Automático al cerrar sesión
- ✅ Persiste en DB

---

### HU-SYS-005: AR-IA (24 tests)

**Archivo**: `tests/test_sprint2_risk_analyst.py`

Tests de detección (5 dimensiones):
- Detecta COGNITIVE_DELEGATION
- Detecta AI_DEPENDENCY (>70%)
- Detecta LACK_JUSTIFICATION
- Detecta UNCRITICAL_ACCEPTANCE (epistémico)
- Corre en paralelo (no bloquea)

Tests de niveles:
- CRITICAL
- HIGH
- MEDIUM
- LOW

Tests de dimensiones:
- COGNITIVE
- ETHICAL
- EPISTEMIC
- TECHNICAL
- GOVERNANCE

Tests de objeto Risk:
- Genera Risk completo
- Incluye evidencia
- Incluye recomendaciones
- Persiste en RiskDB
- Riesgo crítico dispara alerta

Tests de integración:
- Detección a lo largo de sesión
- Múltiples riesgos misma dimensión
- Correlación con gobernanza
- Generación de RiskReport

**Criterios esperados**:
- ✅ Análisis en paralelo
- ✅ Genera Risk cuando detecta patrón
- ✅ 5 dimensiones cubiertas
- ✅ Risk completo con todos los campos
- ✅ Persiste en RiskDB
- ✅ Críticos disparan alertas
- ✅ Tests para cada tipo

---

### HU-SYS-007: API REST (35+ tests)

**Archivo**: `tests/test_sprint2_api_endpoints.py`

Tests de Sessions (5):
- POST /api/v1/sessions
- GET /api/v1/sessions
- GET /api/v1/sessions/{id}
- PUT /api/v1/sessions/{id}
- POST /api/v1/sessions/{id}/end

Tests de Interactions (3):
- POST /api/v1/interactions (principal)
- Invalid session → 404
- Governance block → 403

Tests de Traces (3):
- GET /api/v1/traces/{session_id}
- GET /api/v1/traces/{session_id}/cognitive-path
- GET /api/v1/traces con filtros

Tests de Risks (3):
- GET /api/v1/risks/session/{session_id}
- GET /api/v1/risks?level=CRITICAL
- GET /api/v1/risks?resolved=false

Tests de Evaluation (1):
- GET /api/v1/evaluation/session/{session_id}

Tests de Activities (7):
- POST /api/v1/activities
- GET /api/v1/activities
- GET /api/v1/activities/{id}
- PUT /api/v1/activities/{id}
- POST /api/v1/activities/{id}/publish
- POST /api/v1/activities/{id}/archive
- DELETE /api/v1/activities/{id}

Tests de OpenAPI (2):
- GET /openapi.json
- GET /docs (Swagger UI)

Tests de Performance (5):
- POST /api/v1/interactions <2s
- List sessions paginación eficiente
- 10 requests concurrentes
- Rate limiting funciona
- Percentiles (P50, P95, P99)

Tests de Seguridad (5):
- No secretos hardcodeados
- Input validation
- SQL injection prevention
- CORS configurado
- Error messages no exponen internals

**Criterios esperados**:
- ✅ 15+ endpoints implementados
- ✅ OpenAPI/Swagger auto-generado
- ✅ Rate limiting y CORS
- ✅ Logs estructurados
- ✅ Tests integración todos los endpoints
- ✅ Performance <2s
- ✅ Input validation
- ✅ SQL injection prevenida

---

## Tests de Integración E2E

**Archivo**: `tests/test_integration_e2e.py`

### Escenario 1: Sesión Exitosa Completa (20+ assertions)

```python
def test_complete_successful_session():
    # 1. Crear sesión
    # 2. Consulta conceptual (no bloqueada)
    # 3. Solicitar pista graduada
    # 4. Justificar decisión de diseño
    # 5. Cerrar sesión
    # 6. Recibir evaluación formativa
    # 7. Validar trazas N4
    # 8. Validar riesgos (ninguno o bajo)
```

### Escenario 2: Sesión con Delegación (15+ assertions)

```python
def test_session_with_delegation_blocked():
    # 1. Crear sesión
    # 2. Intentar delegación → bloqueado
    # 3. Recibir mensaje pedagógico
    # 4. Reformular con consulta → permitido
    # 5. Cerrar sesión
    # 6. Validar riesgo COGNITIVE_DELEGATION
    # 7. Validar traza blocked=true
```

### Escenario 3: Múltiples Riesgos (20+ assertions)

```python
def test_session_with_multiple_risks():
    # 1. Crear sesión
    # 2. Delegación → riesgo cognitivo
    # 3. Sin justificar → riesgo falta justificación
    # 4. Aceptación acrítica → riesgo epistémico
    # 5. Cerrar sesión
    # 6. Validar 3+ riesgos
    # 7. Validar evaluación refleja riesgos
    # 8. Validar recomendaciones en feedback
```

### Escenario 4: Workflow Docente (25+ assertions)

```python
def test_teacher_workflow_complete():
    # 1. Docente crea actividad con políticas
    # 2. Publica actividad
    # 3. Estudiante crea sesión en actividad
    # 4. Políticas se aplican
    # 5. Estudiante completa sesión
    # 6. Docente visualiza trazas N4
    # 7. Docente accede evaluación
    # 8. Docente revisa riesgos
    # 9. Docente ajusta calificación
```

### Escenario 5: API End-to-End (30+ assertions)

```python
def test_api_end_to_end_workflow():
    # Flujo completo vía API
    # 1-8: Todos los endpoints principales
    # 9: Validar respuestas completas
```

---

## Checklist de Validación

### Sprint 1 - Completado ✅

- [x] HU-EST-001: Iniciar sesión (8 tests)
- [x] HU-EST-002: Consultar conceptos (10 tests)
- [x] HU-EST-003: Bloqueo delegación (13 tests)
- [x] HU-SYS-001: CRPE (20 tests)
- [x] HU-SYS-002: GOV-IA (15 tests)
- [x] HU-SYS-003: TC-N4 (20 tests)

**Total Sprint 1**: 86 tests implementados

### Sprint 2 - A Implementar 🔄

- [ ] HU-EST-004: Pistas graduadas (15 tests)
- [ ] HU-EST-005: Justificaciones (12 tests)
- [ ] HU-EST-007: Feedback formativo (12 tests)
- [ ] HU-DOC-001: Actividades (7 tests) - YA VALIDADOS en test_api_endpoints.py
- [ ] HU-SYS-004: E-IA-Proc (18 tests)
- [ ] HU-SYS-005: AR-IA (24 tests)
- [ ] HU-SYS-007: API REST (35 tests)

**Total Sprint 2**: 123 tests esperados

### Integración - A Implementar 🔄

- [ ] Escenario 1: Sesión exitosa completa
- [ ] Escenario 2: Sesión con delegación
- [ ] Escenario 3: Múltiples riesgos
- [ ] Escenario 4: Workflow docente
- [ ] Escenario 5: API end-to-end

**Total Integración**: 5 escenarios

---

## Resultados Esperados

### Cobertura de Código

| Componente | Objetivo |
|------------|----------|
| CRPE | ≥85% |
| GOV-IA | ≥80% |
| TC-N4 | ≥90% |
| T-IA-Cog | ≥75% |
| E-IA-Proc | ≥75% |
| AR-IA | ≥80% |
| API | ≥70% |
| Models | ≥90% |
| **TOTAL** | **≥70%** |

### Total de Tests

- **Tests unitarios**: ~200
- **Tests integración**: ~30
- **Tests E2E**: 5 escenarios
- **Total**: ~235 tests

---

## Próximos Pasos

1. ✅ Plan de testing creado (este documento)
2. 🔄 Implementar tests Sprint 2 faltantes
3. 🔄 Implementar tests E2E
4. 🔄 Ejecutar suite completa
5. 🔄 Validar cobertura ≥70%
6. 🔄 Generar reporte final

---

**Versión**: 1.0
**Fecha**: 2025-11-20
**Autor**: Mag. Alberto Cortez