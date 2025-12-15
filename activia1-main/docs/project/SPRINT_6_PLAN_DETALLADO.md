# SPRINT 6 - PLAN DETALLADO 🚀

**Integración Final + Funcionalidades Avanzadas + Production Readiness**

Fecha de inicio: 2025-11-21
Autor: Mag. en Ing. de Software Alberto Cortez
Sprint: 6 de 6 (FINAL)

---

## 📋 Resumen Ejecutivo

Sprint 6 es el **sprint final del proyecto AI-Native MVP**, enfocado en:

1. **Funcionalidades avanzadas** (BAJA prioridad pero alta calidad de vida)
2. **Integraciones externas** (LTI con Moodle)
3. **Production readiness** (deploy, monitoring, docs)
4. **Simuladores profesionales completos** (SM-IA, IT-IA, IR-IA, CX-IA, DSO-IA)
5. **Exportación de datos** para investigación

### Estado Actual (Pre-Sprint 6)

✅ **Sprints 1-5 completados**:
- Sprint 1: MVP Core (CLI + Tutor + Trazabilidad N4)
- Sprint 2: Evaluación de procesos + API REST
- Sprint 3: Dashboard docente + Gobernanza
- Sprint 4: Simuladores iniciales (PO-IA) + Analíticas
- Sprint 5: Git N2 + Reportes institucionales + Risk management

✅ **Backend completo**:
- 14 routers API REST
- 10 tablas en base de datos
- 6 agentes AI-Native
- LLM provider abstraction (OpenAI, Gemini, Mock)
- Arquitectura limpia y refactorizada (calidad 9.0/10)

✅ **Frontend**:
- React + TypeScript chatbot
- Integración completa con API
- Service layer con arquitectura limpia

❌ **Pendiente** (Sprint 6):
- Simuladores profesionales completos (5 de 6 faltan)
- Integración LTI con Moodle
- Exportación de datos anonimizados
- Historial de sesiones mejorado
- Deploy a producción
- Documentación final

---

## 🎯 Historias de Usuario del Sprint 6

### 1. HU-EST-008: Consultar Historial de Sesiones Previas

**Como** estudiante
**Quiero** ver el historial de mis sesiones anteriores con sus evaluaciones
**Para** monitorear mi progreso a lo largo del tiempo

**Prioridad**: BAJA
**Estimación**: 5 Story Points

**Criterios de Aceptación**:
1. ✅ Puedo listar todas mis sesiones previas con:
   - Fecha y duración
   - Actividad realizada
   - Nivel de competencia alcanzado
   - Dependencia de IA promedio
   - Riesgos detectados
2. ✅ Puedo filtrar por:
   - Rango de fechas
   - Actividad específica
   - Nivel de competencia
3. ✅ Puedo ver gráfico de progreso temporal
4. ✅ Puedo comparar mi desempeño en diferentes actividades

**Tareas de Implementación**:
- [ ] Endpoint API: `GET /api/v1/sessions/history/{student_id}`
- [ ] Componente React: `SessionHistory.tsx` con filtros
- [ ] Gráfico de progreso temporal (Chart.js o Recharts)
- [ ] Exportar historial a CSV/PDF

---

### 2. HU-EST-010: Participar en Daily Scrum Simulado (SM-IA)

**Como** estudiante
**Quiero** reportar mi progreso a un Scrum Master simulado
**Para** practicar gestión ágil y comunicación de impedimentos

**Prioridad**: BAJA
**Estimación**: 5 Story Points

**Criterios de Aceptación**:
1. ✅ El SM-IA me pregunta las 3 preguntas del daily:
   - "¿Qué hiciste ayer?"
   - "¿Qué vas a hacer hoy?"
   - "¿Hay algún impedimento?"
2. ✅ El SM-IA detecta desviaciones en estimaciones y pregunta causas
3. ✅ El SM-IA me ayuda a identificar y documentar impedimentos

**Tareas de Implementación**:
- [ ] Agente `ScrumMasterAgent` en `agents/simulators.py`
- [ ] Sistema de tracking de tareas y estimaciones
- [ ] Detección de impedimentos mediante NLP
- [ ] Feedback sobre comunicación en ceremonias ágiles

---

### 3. HU-EST-011: Enfrentar Entrevista Técnica Simulada (IT-IA)

**Como** estudiante
**Quiero** ser entrevistado por un entrevistador técnico simulado
**Para** prepararme para procesos de selección reales

**Prioridad**: BAJA
**Estimación**: 8 Story Points

**Criterios de Aceptación**:
1. ✅ El IT-IA me hace preguntas técnicas progresivas:
   - Conceptuales ("Explicá qué es polimorfismo")
   - Algorítmicas ("¿Cómo invertirías una lista enlazada?")
   - De diseño ("¿Cómo diseñarías un sistema de caché?")
2. ✅ El IT-IA evalúa:
   - Claridad en la explicación
   - Capacidad de razonar en voz alta
   - Manejo de presión y preguntas desafiantes
3. ✅ Al finalizar, recibo feedback específico de la entrevista

**Tareas de Implementación**:
- [ ] Agente `TechnicalInterviewerAgent` con banco de preguntas
- [ ] Sistema de evaluación de respuestas (claridad, precisión técnica)
- [ ] Detección de "thinking aloud" vs lectura de IA
- [ ] Reporte de entrevista con áreas de mejora

---

### 4. HU-EST-012: Responder Incidente en Producción (IR-IA)

**Como** estudiante
**Quiero** gestionar un incidente simulado en producción
**Para** desarrollar habilidades DevOps y manejo de presión

**Prioridad**: BAJA
**Estimación**: 8 Story Points

**Criterios de Aceptación**:
1. ✅ El IR-IA simula un incidente real:
   - "La API está retornando 500 en el 30% de requests"
   - "El tiempo de respuesta subió de 200ms a 5s"
2. ✅ Debo diagnosticar, proponer solución y documentar
3. ✅ El IR-IA evalúa:
   - Proceso de diagnóstico sistemático
   - Priorización (¿qué hacer primero?)
   - Documentación post-mortem

**Tareas de Implementación**:
- [ ] Agente `IncidentResponderAgent` con escenarios de incidentes
- [ ] Simulación de logs, métricas y trazas distribuidas
- [ ] Evaluación de proceso de diagnóstico (árbol de decisión)
- [ ] Template de post-mortem con secciones requeridas

---

### 5. HU-EST-013: Comunicarse con Cliente Simulado (CX-IA)

**Como** estudiante
**Quiero** negociar requisitos con un cliente simulado
**Para** desarrollar habilidades de elicitación y gestión de expectativas

**Prioridad**: BAJA
**Estimación**: 8 Story Points

**Criterios de Aceptación**:
1. ✅ El CX-IA presenta requisitos ambiguos o contradictorios
2. ✅ Debo hacer preguntas para clarificar
3. ✅ Debo negociar prioridades y plazos
4. ✅ El CX-IA evalúa soft skills: empatía, claridad, profesionalismo

**Tareas de Implementación**:
- [ ] Agente `ClientExperienceAgent` con personalidades configurables
- [ ] Generación de requisitos ambiguos con GPT-4
- [ ] Evaluación de soft skills (análisis de sentimiento, claridad)
- [ ] Feedback sobre habilidades de comunicación

---

### 6. HU-EST-014: Auditar Seguridad con DSO-IA (Faltó en lista)

**Como** estudiante
**Quiero** recibir auditoría de seguridad de mi código
**Para** aprender a identificar vulnerabilidades y aplicar DevSecOps

**Prioridad**: MEDIA
**Estimación**: 8 Story Points

**Criterios de Aceptación**:
1. ✅ El DSO-IA analiza mi código en busca de:
   - SQL injection, XSS, CSRF
   - Secretos hardcodeados (API keys, passwords)
   - Dependencias vulnerables
   - Configuraciones inseguras
2. ✅ Recibo informe de seguridad con severidad (CRITICAL, HIGH, MEDIUM, LOW)
3. ✅ El DSO-IA me explica cada vulnerabilidad y cómo mitigarla
4. ✅ Puedo solicitar re-audit después de corregir

**Tareas de Implementación**:
- [ ] Agente `DevSecOpsAgent` con reglas de seguridad OWASP Top 10
- [ ] Integración con herramientas de SAST (bandit, semgrep)
- [ ] Generación de informe de seguridad estilo Snyk/SonarQube
- [ ] Endpoint API: `POST /api/v1/audit/security`

---

### 7. HU-SYS-010: Integración LTI con Moodle

**Como** sistema
**Quiero** integrarme vía LTI con Moodle
**Para** que los docentes no tengan que gestionar usuarios manualmente

**Prioridad**: BAJA
**Estimación**: 21 Story Points

**Criterios de Aceptación Técnicos**:
1. ✅ Implementación LTI 1.3 (IMS Global)
2. ✅ Single Sign-On (SSO) con Moodle
3. ✅ Sincronización de estudiantes y cursos
4. ✅ Envío de calificaciones de vuelta a Moodle (AGS - Assignment and Grade Services)
5. ✅ Documentación de instalación para administradores Moodle

**Tareas de Implementación**:
- [ ] Implementar LTI 1.3 Provider (OAuth 2.0 + OIDC)
- [ ] Endpoints LTI: `/lti/login`, `/lti/launch`, `/lti/jwks`
- [ ] LTI AGS: Envío de scores a Moodle gradebook
- [ ] LTI NRPS: Sincronización de roster (estudiantes del curso)
- [ ] Configuración: LTI keys, deployment IDs
- [ ] Documentación: Guía de instalación para administradores Moodle
- [ ] Plugin Moodle (opcional): Instalación simplificada

---

### 8. HU-ADM-005: Exportar Datos para Investigación Institucional

**Como** administrador institucional
**Quiero** exportar datos anonimizados de trazas cognitivas
**Para** investigación educativa y mejora continua del modelo AI-Native

**Prioridad**: BAJA
**Estimación**: 8 Story Points

**Criterios de Aceptación**:
1. ✅ Puedo exportar dataset anonimizado con:
   - Trazas N4 (sin IDs de estudiantes)
   - Evaluaciones de procesos
   - Riesgos detectados
   - Patrones de uso de IA
2. ✅ La anonimización es robusta (cumple GDPR/LOPD)
3. ✅ Puedo especificar:
   - Rango de fechas
   - Cursos incluidos
   - Nivel de agregación
4. ✅ Formatos de exportación: CSV, JSON, Parquet

**Tareas de Implementación**:
- [ ] Endpoint API: `POST /api/v1/admin/export/research-data`
- [ ] Anonimización con hash irreversible (SHA-256 + salt)
- [ ] Generación de datasets en múltiples formatos
- [ ] Validación de cumplimiento GDPR (k-anonymity, l-diversity)
- [ ] Documentación de esquema de datos exportados

---

## 🏗️ Arquitectura del Sprint 6

### Nuevos Componentes

**1. Simuladores Profesionales Completos**

```
agents/simulators.py (EXTENSIÓN)
├── ScrumMasterAgent (SM-IA)
├── TechnicalInterviewerAgent (IT-IA)
├── IncidentResponderAgent (IR-IA)
├── ClientExperienceAgent (CX-IA)
└── DevSecOpsAgent (DSO-IA)
```

**2. LTI Integration**

```
src/ai_native_mvp/lti/
├── __init__.py
├── provider.py         # LTI 1.3 Provider
├── oauth.py            # OAuth 2.0 + OIDC
├── ags.py              # Assignment and Grade Services
├── nrps.py             # Names and Role Provisioning Service
└── config.py           # LTI configuration
```

**3. Data Export & Anonymization**

```
src/ai_native_mvp/export/
├── __init__.py
├── anonymizer.py       # Anonimización GDPR-compliant
├── exporter.py         # Exportación multi-formato
└── schemas.py          # Esquemas de datos exportados
```

**4. API Routes Nuevos**

```
src/ai_native_mvp/api/routers/
├── session_history.py  # HU-EST-008
├── simulators.py       # HU-EST-010 a HU-EST-013 (extensión)
├── lti.py              # HU-SYS-010
└── data_export.py      # HU-ADM-005
```

---

## 📊 Nuevas Tablas en Base de Datos

### 1. `interview_sessions` (IT-IA)

```sql
CREATE TABLE interview_sessions (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES sessions(id),
    student_id VARCHAR(100) NOT NULL,
    interview_type VARCHAR(50),  -- CONCEPTUAL, ALGORITHMIC, DESIGN
    questions_asked JSON,
    responses JSON,
    evaluation_score FLOAT,
    feedback TEXT,
    created_at DATETIME,
    INDEX idx_interview_student (student_id, created_at)
);
```

### 2. `incident_simulations` (IR-IA)

```sql
CREATE TABLE incident_simulations (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES sessions(id),
    student_id VARCHAR(100) NOT NULL,
    incident_type VARCHAR(50),  -- API_ERROR, PERFORMANCE, SECURITY
    incident_description TEXT,
    diagnosis_process JSON,
    solution_proposed TEXT,
    time_to_resolve_minutes INT,
    post_mortem TEXT,
    evaluation JSON,
    created_at DATETIME,
    INDEX idx_incident_student (student_id, created_at)
);
```

### 3. `lti_deployments` (LTI)

```sql
CREATE TABLE lti_deployments (
    id VARCHAR(36) PRIMARY KEY,
    platform_name VARCHAR(100),  -- "Moodle", "Canvas", etc.
    issuer VARCHAR(255),
    client_id VARCHAR(255),
    deployment_id VARCHAR(255),
    public_keyset_url TEXT,
    access_token_url TEXT,
    auth_login_url TEXT,
    auth_token_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME,
    UNIQUE INDEX idx_lti_deployment (issuer, deployment_id)
);
```

### 4. `lti_sessions` (LTI)

```sql
CREATE TABLE lti_sessions (
    id VARCHAR(36) PRIMARY KEY,
    deployment_id VARCHAR(36) REFERENCES lti_deployments(id),
    lti_user_id VARCHAR(255),     -- ID del usuario en Moodle
    session_id VARCHAR(36) REFERENCES sessions(id),
    course_id VARCHAR(100),
    resource_link_id VARCHAR(255),
    created_at DATETIME,
    INDEX idx_lti_user (lti_user_id),
    INDEX idx_lti_session (session_id)
);
```

---

## 🔧 Dependencias Nuevas

Agregar a `requirements.txt`:

```txt
# LTI 1.3 Support
pylti1p3==3.0.0           # LTI 1.3 implementation
jwcrypto==1.5.0           # JWT/JWK handling for LTI

# Data Export
pyarrow==14.0.1           # Parquet format support
openpyxl==3.1.2           # Excel export (opcional)

# Security Auditing (DSO-IA)
bandit==1.7.5             # Python SAST tool
safety==2.3.5             # Dependency vulnerability scanner

# Visualization (opcional, para gráficos en frontend)
# Ya tenemos Recharts en frontend, no necesitamos backend viz
```

---

## 📝 Plan de Implementación (5 Fases)

### Fase 1: Simuladores Profesionales (Días 1-3)

**Objetivo**: Completar los 5 simuladores faltantes

**Tareas**:
1. Implementar `ScrumMasterAgent` (SM-IA)
   - Daily standup flow
   - Impediment tracking
   - Velocity analysis
2. Implementar `TechnicalInterviewerAgent` (IT-IA)
   - Question bank (conceptual, algorithmic, design)
   - Response evaluation
   - Feedback generation
3. Implementar `IncidentResponderAgent` (IR-IA)
   - Incident scenarios (API errors, performance, security)
   - Diagnosis evaluation
   - Post-mortem template
4. Implementar `ClientExperienceAgent` (CX-IA)
   - Requirements generation (ambiguous, contradictory)
   - Soft skills evaluation
   - Negotiation tracking
5. Implementar `DevSecOpsAgent` (DSO-IA)
   - OWASP Top 10 rules
   - SAST integration (bandit)
   - Security report generation

**Entregables**:
- `agents/simulators.py` con 5 agentes nuevos
- Endpoints API para cada simulador
- Tests unitarios (pytest)
- Documentación de cada simulador

---

### Fase 2: Historial de Sesiones (Día 4)

**Objetivo**: Implementar HU-EST-008 (Session History)

**Tareas**:
1. Backend:
   - Endpoint `GET /api/v1/sessions/history/{student_id}`
   - Filtros: fecha, actividad, competencia
   - Agregaciones: progreso temporal, comparación actividades
2. Frontend:
   - Componente `SessionHistory.tsx`
   - Filtros interactivos
   - Gráfico de progreso (Recharts)
   - Exportar a CSV

**Entregables**:
- API endpoint funcional
- Componente React con gráficos
- Tests E2E (Cypress opcional)

---

### Fase 3: Integración LTI con Moodle (Días 5-8)

**Objetivo**: Implementar HU-SYS-010 (LTI 1.3)

**Tareas**:
1. Implementar LTI 1.3 Provider:
   - OAuth 2.0 + OIDC flow
   - JWKS endpoint (`/lti/jwks`)
   - Launch endpoint (`/lti/launch`)
2. Implementar LTI AGS:
   - Envío de scores a Moodle gradebook
3. Implementar LTI NRPS:
   - Sincronización de roster (estudiantes)
4. Configuración:
   - LTI keys, deployment IDs
   - Almacenamiento en `lti_deployments`
5. Documentación:
   - Guía de instalación para administradores Moodle
   - Screenshots de configuración

**Entregables**:
- Módulo `src/ai_native_mvp/lti/` completo
- Endpoints LTI funcionales
- Base de datos actualizada con tablas LTI
- Documentación de instalación

**Nota**: Esta es la tarea más compleja del Sprint (21 SP)

---

### Fase 4: Exportación de Datos (Día 9)

**Objetivo**: Implementar HU-ADM-005 (Data Export)

**Tareas**:
1. Implementar anonimización:
   - Hash irreversible (SHA-256 + salt)
   - Validación k-anonymity
2. Implementar exportación multi-formato:
   - CSV, JSON, Parquet
3. Endpoint API:
   - `POST /api/v1/admin/export/research-data`
   - Filtros: fecha, cursos, nivel agregación
4. Documentación:
   - Esquema de datos exportados
   - Guía de cumplimiento GDPR

**Entregables**:
- Módulo `src/ai_native_mvp/export/` completo
- Endpoint API funcional
- Tests de anonimización
- Documentación de esquema

---

### Fase 5: Production Readiness (Días 10-12)

**Objetivo**: Preparar sistema para producción

**Tareas**:
1. **Deploy Configuration**:
   - Docker Compose production
   - Nginx reverse proxy
   - SSL/TLS certificates (Let's Encrypt)
   - Environment variables (`.env.production`)
2. **Monitoring & Logging**:
   - Structured logging (JSON format)
   - Log aggregation (ELK stack opcional)
   - Health checks avanzados
   - Metrics (Prometheus + Grafana opcional)
3. **Security Hardening**:
   - Rate limiting por IP (ya implementado)
   - CORS restrictivo (production domains only)
   - Secrets management (no hardcoded keys)
   - Security headers (HSTS, CSP, X-Frame-Options)
4. **Database**:
   - Migration scripts (SQLite → PostgreSQL)
   - Backup strategy
   - Connection pooling optimizado
5. **Documentation**:
   - README final con arquitectura completa
   - API documentation (OpenAPI/Swagger)
   - Deployment guide
   - User guides (estudiante, docente, admin)
6. **Testing**:
   - Coverage mínimo 80% (pytest)
   - E2E tests (Cypress opcional)
   - Load testing (Locust opcional)

**Entregables**:
- Docker Compose production-ready
- Documentación completa (5+ guides)
- Tests con coverage ≥80%
- Deployment checklist

---

## 📈 Métricas de Éxito

### Criterios de Aceptación del Sprint

1. ✅ **Funcionalidad**:
   - Los 8 HUs implementadas y funcionando
   - Todos los simuladores operativos
   - Integración LTI testeada con Moodle real
   - Exportación de datos validada con dataset real

2. ✅ **Calidad**:
   - Cobertura de tests ≥80%
   - 0 vulnerabilidades críticas (Bandit, Safety)
   - Código refactorizado según Clean Architecture
   - Documentación completa y actualizada

3. ✅ **Performance**:
   - API response time <500ms (p95)
   - LTI launch time <2s
   - Data export <30s para 10k trazas

4. ✅ **Seguridad**:
   - Cumplimiento GDPR en exportación
   - LTI OAuth 2.0 implementado correctamente
   - Secrets no hardcodeados
   - Rate limiting activo

5. ✅ **Deploy**:
   - Sistema deployable en 1 comando (docker-compose up)
   - Documentación de deploy completa
   - Backup strategy documentada

---

## 🚀 Definition of Done (DoD)

Para considerar el Sprint 6 COMPLETADO:

- [ ] 8 Historias de Usuario implementadas y funcionando
- [ ] 5 Simuladores profesionales completos (SM-IA, IT-IA, IR-IA, CX-IA, DSO-IA)
- [ ] Integración LTI 1.3 con Moodle funcional
- [ ] Exportación de datos anonimizados operativa
- [ ] Coverage de tests ≥80%
- [ ] Docker Compose production-ready
- [ ] Documentación completa:
  - README final
  - API documentation
  - Deployment guide
  - User guides (3)
- [ ] Zero vulnerabilidades críticas
- [ ] Sistema deployado en ambiente staging
- [ ] Presentación final del MVP completada

---

## 📚 Entregables Finales del Proyecto

Al completar Sprint 6, el proyecto AI-Native MVP estará COMPLETO con:

### Documentación Técnica (15+ documentos)
1. README.md (overview)
2. README_MVP.md (1,301 líneas - arquitectura completa)
3. README_API.md (400+ líneas - API documentation)
4. README_FRONTEND.md (500+ líneas - frontend guide)
5. DEPLOYMENT_GUIDE.md (NEW - guía de deploy)
6. USER_GUIDE_STUDENT.md (NEW - guía estudiante)
7. USER_GUIDE_TEACHER.md (NEW - guía docente)
8. USER_GUIDE_ADMIN.md (NEW - guía administrador)
9. LTI_INTEGRATION_GUIDE.md (NEW - guía LTI)
10. CLAUDE.md (project instructions)
11. Sprints 1-6 completados (6 documentos)
12. Phase corrections (Fases 0-3, 4 documentos)
13. USER_STORIES.md (backlog completo)

### Codebase Completo
- **Backend**: 6 agentes, 14+ routers API, 10+ tablas DB
- **Frontend**: React + TypeScript chatbot completo
- **LTI**: Integración Moodle funcional
- **Tests**: Coverage ≥80%
- **Deploy**: Docker Compose production

### Métricas del Proyecto
- **Líneas de código**: ~15,000 (backend) + ~5,000 (frontend)
- **Tests**: 150+ test cases
- **API endpoints**: 50+ endpoints REST
- **Documentación**: 10,000+ líneas
- **Calidad de código**: 9.0/10
- **Sprints completados**: 6 de 6

---

## 🎯 Próximos Pasos

1. **Comenzar Fase 1**: Implementar simuladores profesionales
2. **Review diario**: Verificar progreso contra este plan
3. **Adaptar si necesario**: Este es un plan vivo

---

**Estado**: 🟡 PLANIFICADO (Pendiente de ejecución)
**Fecha de inicio prevista**: 2025-11-21
**Fecha de fin prevista**: 2025-12-05 (2 semanas)