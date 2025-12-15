# GOBERNANZA INSTITUCIONAL (GOV-IA) - Documentacion Tecnica Detallada

## Tabla de Contenidos

1. [Vision General](#1-vision-general)
2. [Arquitectura del Sistema de Gobernanza](#2-arquitectura-del-sistema-de-gobernanza)
3. [GobernanzaAgent: Nucleo Principal](#3-gobernanzaagent-nucleo-principal)
4. [TutorGovernanceEngine: Sistema de Semaforos](#4-tutorgovernanceengine-sistema-de-semaforos)
5. [TutorRulesEngine: Reglas Pedagogicas Inquebrantables](#5-tutorrulesengine-reglas-pedagogicas-inquebrantables)
6. [Subsistema de Seguridad](#6-subsistema-de-seguridad)
7. [Tablas de Base de Datos](#7-tablas-de-base-de-datos)
8. [Sistema de Reportes Institucionales](#8-sistema-de-reportes-institucionales)
9. [Integracion con Otros Agentes](#9-integracion-con-otros-agentes)
10. [API Endpoints](#10-api-endpoints)
11. [Flujos de Decision](#11-flujos-de-decision)
12. [Resumen Ejecutivo](#12-resumen-ejecutivo)

---

## 1. Vision General

### 1.1 Proposito

El sistema de **Gobernanza Institucional (GOV-IA)** es el agente responsable de operacionalizar las politicas institucionales de IA generativa en el contexto educativo. Actua como guardian etico y pedagogico que garantiza:

- **Integridad Academica**: Prevencion de plagio y uso indebido de IA
- **Privacidad de Datos**: Sanitizacion de PII antes del procesamiento LLM
- **Cumplimiento Normativo**: Adherencia a marcos internacionales de gobernanza IA
- **Trazabilidad Completa**: Auditoria de todas las interacciones

### 1.2 Marcos Normativos Implementados

El agente GOV-IA implementa los siguientes marcos internacionales:

| Marco | Ano | Enfoque |
|-------|-----|---------|
| **UNESCO** | 2021 | Etica de IA en educacion |
| **OECD AI Principles** | 2019 | Principios de IA responsable |
| **IEEE Ethically Aligned Design** | 2019 | Diseno eticamente alineado |
| **ISO/IEC 23894:2023** | 2023 | Gestion de riesgos de IA |
| **ISO/IEC 42001:2023** | 2023 | Sistemas de gestion de IA |

### 1.3 Ubicacion en la Arquitectura

```
                        +------------------+
                        |   AIGateway      |
                        |   (Orquestador)  |
                        +--------+---------+
                                 |
                    +------------+------------+
                    |                         |
            +-------v-------+         +-------v-------+
            |   GOV-IA      |<------->|   AR-IA       |
            | (Gobernanza)  |         | (Riesgos)     |
            +-------+-------+         +---------------+
                    |
        +-----------+-----------+
        |           |           |
   +----v----+ +----v----+ +----v----+
   | T-IA-Cog| | E-IA    | | S-IA-X  |
   | (Tutor) | | (Eval)  | | (Sim)   |
   +---------+ +---------+ +---------+
```

**Archivo Principal**: `backend/agents/governance.py`

---

## 2. Arquitectura del Sistema de Gobernanza

### 2.1 Componentes Principales

El sistema de gobernanza se compone de tres capas fundamentales:

```
+===============================================================+
|                    CAPA 1: GOBERNANZA INSTITUCIONAL            |
|  GobernanzaAgent (governance.py)                               |
|  - Verificacion de cumplimiento                                |
|  - Sanitizacion de PII                                         |
|  - Generacion de reportes de auditoria                        |
+===============================================================+
                            |
                            v
+===============================================================+
|                    CAPA 2: GOBERNANZA PEDAGOGICA              |
|  TutorGovernanceEngine (tutor_governance.py)                  |
|  - Sistema de semaforos (VERDE/AMARILLO/ROJO)                 |
|  - Procesamiento en 3 fases (IPC, GSR, Andamiaje)             |
|  - Restricciones adaptativas                                   |
+===============================================================+
                            |
                            v
+===============================================================+
|                    CAPA 3: REGLAS PEDAGOGICAS                 |
|  TutorRulesEngine (tutor_rules.py)                            |
|  - 4 reglas inquebrantables                                    |
|  - Tipos de intervencion                                       |
|  - Niveles de andamiaje cognitivo                             |
+===============================================================+
```

### 2.2 Flujo de Gobernanza

```
Prompt Estudiante
       |
       v
+------+------+
| Sanitizacion |  <-- GOV-IA: Detecta y redacta PII
| de PII       |
+------+------+
       |
       v
+------+------+
| Verificacion |  <-- GOV-IA: Chequea politicas institucionales
| Cumplimiento |
+------+------+
       |
       v
+------+------+
| Semaforo de  |  <-- TutorGovernance: Evalua nivel de riesgo
| Riesgo       |
+------+------+
       |
       +----------+----------+
       |          |          |
   [VERDE]    [AMARILLO]   [ROJO]
       |          |          |
       v          v          v
   Normal    Reduccion   Bloqueo +
             de ayuda    Redireccion
```

---

## 3. GobernanzaAgent: Nucleo Principal

### 3.1 Clase GobernanzaAgent

**Ubicacion**: `backend/agents/governance.py`

```python
class GobernanzaAgent:
    """
    GOV-IA: Agente de Gobernanza Institucional

    Funciones:
    1. Verificar cumplimiento de politicas
    2. Gestion del riesgo en tiempo real
    3. Auditoria y trazabilidad
    4. Generacion de reportes institucionales
    """
```

### 3.2 Politicas Institucionales

El agente mantiene un diccionario configurable de politicas:

| Politica | Valor Default | Descripcion |
|----------|---------------|-------------|
| `max_ai_assistance_level` | 0.7 | Nivel maximo de ayuda IA (0-1) |
| `require_explicit_ai_usage` | True | Exigir declaracion explicita de uso de IA |
| `block_complete_solutions` | True | Bloquear solicitudes de codigo completo |
| `require_traceability` | True | Exigir trazabilidad N4 completa |
| `enforce_academic_integrity` | True | Aplicar politicas de integridad academica |

### 3.3 Sistema de Sanitizacion de PII

El agente implementa deteccion y redaccion de Informacion Personal Identificable (PII):

```python
pii_patterns = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "dni": r'\b\d{7,8}\b',           # DNI argentino
    "phone": r'\b\d{2,4}[-.\s]?\d{4}[-.\s]?\d{4}\b',
    "credit_card": r'\b\d{4}[-.\s]?\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b'
}
```

**Proceso de Sanitizacion**:

```
Input: "Mi email es juan@universidad.edu y mi DNI 12345678"

       |
       v [sanitize_prompt()]

Output: "Mi email es [EMAIL_REDACTED] y mi DNI [DNI_REDACTED]"
Return: (prompt_sanitizado, pii_found=True)
```

### 3.4 Metodo verify_compliance()

Verifica el cumplimiento de politicas antes de ejecutar acciones:

**Parametros**:
- `trace_sequence`: TraceSequence a verificar (nueva API)
- `policies`: Politicas especificas a verificar
- `action`: Accion a verificar (API antigua)
- `context`: Contexto de la accion (API antigua)

**Verificaciones Realizadas**:

| Verificacion | Condicion | Resultado |
|--------------|-----------|-----------|
| Dependencia IA | `ai_dependency_score > max_ai_dependency` | VIOLATION |
| Trazabilidad | `traces` vacio y `require_traceability=True` | VIOLATION |
| Delegacion Total | Detecta "codigo completo" o "hace todo" | VIOLATION |
| Soluciones Completas | `is_total_delegation=True` | VIOLATION |
| Nivel de Ayuda | `help_level > max_ai_assistance_level` | WARNING |

**Estados de Cumplimiento**:

```python
class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"    # Cumple todas las politicas
    WARNING = "warning"        # Advertencias, pero permite accion
    VIOLATION = "violation"    # Violacion, bloquea accion
```

### 3.5 Generacion de Reportes de Auditoria

```python
def generate_audit_report(
    self,
    time_period: Dict[str, datetime],
    scope: str = "institutional"
) -> Dict[str, Any]:
```

**Estructura del Reporte**:

```json
{
  "report_id": "audit_2025-12-13T10:30:00",
  "scope": "institutional",
  "time_period": {"start": "...", "end": "..."},
  "compliance_summary": {
    "total_interactions": 1500,
    "compliant_interactions": 1420,
    "violations": 35,
    "warnings": 45
  },
  "policy_effectiveness": {
    "block_complete_solutions": {"enforced": true, "violations": 12},
    "require_traceability": {"enforced": true, "coverage": "100%"}
  },
  "recommendations": [
    "Revisar umbrales de asistencia segun resultados de aprendizaje",
    "Actualizar politicas segun normativa vigente"
  ]
}
```

---

## 4. TutorGovernanceEngine: Sistema de Semaforos

### 4.1 Vision General

**Ubicacion**: `backend/agents/tutor_governance.py`

El TutorGovernanceEngine implementa un sistema de semaforos (VERDE/AMARILLO/ROJO) que controla dinamicamente el nivel de intervencion del tutor basandose en el analisis de riesgo en tiempo real.

### 4.2 Estados del Semaforo

```python
class SemaforoState(str, Enum):
    VERDE = "verde"      # Bajo riesgo, interaccion normal
    AMARILLO = "amarillo"  # Riesgo medio, monitorear
    ROJO = "rojo"        # Riesgo alto, intervencion restrictiva
```

| Estado | Color | Nivel de Riesgo | Comportamiento |
|--------|-------|-----------------|----------------|
| VERDE | Verde | Bajo | Interaccion normal, ayuda disponible |
| AMARILLO | Amarillo | Medio | Reduccion de ayuda, monitoreo activo |
| ROJO | Rojo | Alto | Bloqueo de codigo, redireccion pedagogica |

### 4.3 Procesamiento en 3 Fases

El motor procesa cada request del estudiante en 3 fases secuenciales:

```
                 Prompt Estudiante
                        |
                        v
        +===============================+
        |    FASE 1: IPC               |
        |    Ingesta y Comprension     |
        |    de Prompt                 |
        +===============================+
                        |
                        v
        +===============================+
        |    FASE 2: GSR               |
        |    Gobernanza y Semaforo     |
        |    de Riesgo                 |
        +===============================+
                        |
                        v
        +===============================+
        |    FASE 3: ANDAMIAJE         |
        |    Seleccion de Estrategia   |
        |    de Andamiaje              |
        +===============================+
                        |
                        v
               Respuesta Tutor
```

### 4.4 FASE 1: IPC (Ingesta y Comprension de Prompt)

**Objetivo**: Analizar el prompt para detectar intencion, estado cognitivo y nivel de autonomia.

**Deteccion de Intencion**:

```python
class PromptIntent(str, Enum):
    EXPLORACION = "exploracion"    # Explorando el problema
    DEPURACION = "depuracion"      # Debugueando codigo
    DELEGACION = "delegacion"      # Quiere que la IA resuelva todo
    CLARIFICACION = "clarificacion" # Necesita entender conceptos
    VALIDACION = "validacion"      # Quiere validar su enfoque
```

**Patrones de Deteccion**:

| Intencion | Patrones Detectados |
|-----------|---------------------|
| DELEGACION | "haceme", "resolve", "dame el codigo", "escribi el codigo" |
| DEPURACION | "no funciona", "error", "falla", "bug", "que esta mal" |
| CLARIFICACION | "que es", "como funciona", "explica", "no entiendo" |
| VALIDACION | "esta bien", "es correcto", "que te parece", "revisa" |
| EXPLORACION | Default (cualquier otro patron) |

**Estimacion de Autonomia** (0-1):

```
Base: 0.5
+0.2: Muestra codigo propio (``` en prompt)
+0.2: Explica razonamiento ("porque", "pense", "intente")
-0.3: Intencion de delegacion
-0.2: Mensaje muy corto (< 20 caracteres)
```

### 4.5 FASE 2: GSR (Gobernanza y Semaforo de Riesgo)

**Objetivo**: Evaluar riesgos eticos y pedagogicos para determinar el estado del semaforo.

**Umbrales de Riesgo**:

```python
risk_thresholds = {
    "high_ai_dependency": 0.7,  # Si AI involvement > 0.7 -> ROJO
    "plagiarism_keywords": [
        "generame", "escribi todo", "hace el proyecto",
        "dame la solucion completa", "resolvelo vos"
    ],
    "max_consecutive_requests": 5  # Max solicitudes sin autonomia
}
```

**Evaluacion de Riesgos**:

| Riesgo | Condicion | Semaforo | Restricciones |
|--------|-----------|----------|---------------|
| Delegacion Total | `intent == DELEGACION` | ROJO | `block_code_generation`, `require_justification` |
| Alta Dependencia IA | `avg_ai_involvement > 0.7` | AMARILLO | `reduce_help_level`, `increase_question_ratio` |
| Patron de Plagio | Keywords de plagio detectados | ROJO | `block_code_generation`, `educative_warning` |
| Solicitudes sin Trabajo | >= 5 consecutivas sin mostrar trabajo | AMARILLO | `require_work_shown` |

**Mensajes de Advertencia**:

Para DELEGACION_TOTAL:
```
## Advertencia Pedagogica

Detecte que estas pidiendo que resuelva el problema completo por vos.

**Esto NO es ayuda, es sabotaje a tu aprendizaje.**

Como tutor IA, mi responsabilidad es guiar tu razonamiento, no sustituirlo.
```

Para PATRON_PLAGIO_DETECTADO:
```
## Alerta Etica: Patron de Plagio Detectado

Tu solicitud viola las politicas academicas de integridad.

**No voy a generar codigo completo para proyectos o tareas.**
```

### 4.6 FASE 3: Seleccion de Estrategia de Andamiaje

**Objetivo**: Decidir tipo de respuesta, nivel de ayuda y restricciones basandose en IPC y GSR.

**Estrategias por Estado de Semaforo**:

| Semaforo | Tipo Respuesta | Nivel Ayuda | Permite Codigo | Permite Pseudocodigo |
|----------|----------------|-------------|----------------|----------------------|
| ROJO | `socratic_questioning` | Minimo | NO | NO |
| AMARILLO | `guided_hints` | Bajo | NO | SI |
| VERDE | Variable por intencion | Variable | NO | SI |

**Estrategias VERDE por Intencion**:

| Intencion | Tipo Respuesta | Nivel Ayuda | Tipo Intervencion |
|-----------|----------------|-------------|-------------------|
| EXPLORACION | Socratico | Variable por nivel | PREGUNTA_SOCRATICA |
| DEPURACION | Pistas guiadas | Medio | PISTA_GRADUADA |
| CLARIFICACION | Explicacion conceptual | Medio | CORRECCION_CONCEPTUAL |
| VALIDACION | Socratico | Bajo | PREGUNTA_SOCRATICA |

---

## 5. TutorRulesEngine: Reglas Pedagogicas Inquebrantables

### 5.1 Vision General

**Ubicacion**: `backend/agents/tutor_rules.py`

El TutorRulesEngine define las 4 reglas fundamentales que gobiernan el comportamiento del tutor. Estas reglas son **inquebrantables** y tienen precedencia sobre cualquier otra logica.

### 5.2 Las 4 Reglas Fundamentales

```python
class TutorRule(str, Enum):
    ANTI_SOLUCION = "anti_solucion_directa"
    MODO_SOCRATICO = "modo_socratico_prioritario"
    EXIGIR_EXPLICITACION = "exigir_explicitacion"
    REFUERZO_CONCEPTUAL = "refuerzo_conceptual"
```

### 5.3 Regla #1: Anti-Solucion Directa

**Principio**: "Ni a Palos" - Prohibido dar codigo completo bajo cualquier circunstancia.

**Patrones Bloqueados**:
```
"haceme", "dame el codigo", "muestrame el codigo",
"escribe el codigo", "cual es el codigo", "resuelve esto",
"soluciona", "hace el ejercicio", "implementa", "codifica"
```

**Respuesta al Bloqueo**:

```
## No puedo darte el codigo directamente

Entiendo que queres la solucion rapida, pero **mi trabajo es ayudarte a aprender**,
no a resolver el problema por vos.

Si te doy el codigo, no vas a desarrollar las habilidades que necesitas.
En cambio, trabajemos juntos para que **vos llegues a la solucion**.
```

### 5.4 Regla #2: Modo Socratico Prioritario

**Principio**: El default es preguntar, no responder.

**Logica**:
- Si dio >= 2 explicaciones sin hacer preguntas -> Forzar pregunta
- En primera interaccion -> Siempre comenzar con pregunta
- Priorizar preguntas orientadoras sobre respuestas directas

**Contra-Pregunta Tipica**:
```
## En vez de eso, respondeme:

1. **Que entendes que tenes que resolver?** (Explicalo con tus palabras)
2. **Que enfoque se te ocurre?** (No importa si no estas seguro)
3. **Que conceptos o herramientas crees que son relevantes?**
```

### 5.5 Regla #3: Exigencia de Explicitacion

**Principio**: Forzar conversion pensamiento -> palabras.

**Requerimientos**:
1. Plan antes de codear
2. Pseudocodigo
3. Justificacion de decisiones

**Deteccion de Justificacion**:
```python
justification_signals = [
    "porque", "ya que", "debido a", "considerando que",
    "mi razon es", "pense que", "decidi", "elegi"
]
```

**Deteccion de Planificacion**:
```python
planning_signals = [
    "voy a", "planeo", "mi estrategia", "mi plan",
    "primero", "luego", "despues", "paso"
]
```

### 5.6 Regla #4: Refuerzo Conceptual

**Principio**: Remitir a teoria, no dar parches.

**Mapeo Error -> Concepto**:

| Error Detectado | Concepto Teorico a Reforzar |
|-----------------|----------------------------|
| null_pointer | Invariantes y Precondiciones |
| array_bounds | Invariantes de Estructura de Datos |
| tight_coupling | Acoplamiento y Cohesion |
| complexity_high | Complejidad Algoritmica |
| memory_leak | Gestion de Recursos |
| race_condition | Concurrencia y Sincronizacion |
| duplicated_code | Principio DRY |
| god_class | Single Responsibility Principle |

### 5.7 Tipos de Intervencion

```python
class InterventionType(str, Enum):
    PREGUNTA_SOCRATICA = "pregunta_socratica"
    RECHAZO_PEDAGOGICO = "rechazo_pedagogico"
    PISTA_GRADUADA = "pista_graduada"
    CORRECCION_CONCEPTUAL = "correccion_conceptual"
    EXIGENCIA_JUSTIFICACION = "exigencia_justificacion"
    EXIGENCIA_PSEUDOCODIGO = "exigencia_pseudocodigo"
    REMISION_TEORIA = "remision_teoria"
```

### 5.8 Niveles de Andamiaje Cognitivo

```python
class CognitiveScaffoldingLevel(str, Enum):
    NOVATO = "novato"        # Mas explicaciones, ejemplos parciales
    INTERMEDIO = "intermedio"  # Balance entre guia y autonomia
    AVANZADO = "avanzado"    # Minima ayuda, maxima exigencia critica
```

**Determinacion de Nivel**:

| Condicion | Nivel Asignado |
|-----------|----------------|
| `ai_involvement > 0.7` OR `autonomous_solutions < 3` | NOVATO |
| `error_self_correction > 0.6` AND `ai_involvement < 0.4` | AVANZADO |
| Otros casos | INTERMEDIO |

---

## 6. Subsistema de Seguridad

### 6.1 Vision General

**Ubicacion**: `backend/core/security.py`

El subsistema de seguridad provee autenticacion JWT y hash de contrasenas para proteger el acceso al sistema.

### 6.2 Configuracion de Seguridad

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | **REQUERIDO** | Clave secreta para firmar JWT (min 32 chars en produccion) |
| `JWT_ALGORITHM` | HS256 | Algoritmo de firmado |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 30 | Expiracion de access token |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | 7 | Expiracion de refresh token |

### 6.3 Funciones de Contrasena

```python
# Hash de contrasena con bcrypt
get_password_hash(password: str) -> str

# Verificacion de contrasena
verify_password(plain_password: str, hashed_password: str) -> bool
```

**Nota**: bcrypt tiene limite de 72 bytes para contrasenas.

### 6.4 Funciones JWT

```python
# Crear access token
create_access_token(data: Dict, expires_delta: Optional[timedelta]) -> str

# Crear refresh token
create_refresh_token(data: Dict, expires_delta: Optional[timedelta]) -> str

# Decodificar y validar token
decode_access_token(token: str) -> Optional[Dict]

# Verificar token con tipo
verify_token(token: str, token_type: str) -> Optional[Dict]

# Crear par de tokens
create_token_pair(user_id: str, additional_claims: Optional[Dict]) -> Dict
```

### 6.5 Estructura de Token JWT

**Access Token**:
```json
{
  "sub": "user_id_123",
  "exp": 1702500000,
  "type": "access"
}
```

**Refresh Token**:
```json
{
  "sub": "user_id_123",
  "exp": 1703104800,
  "type": "refresh"
}
```

---

## 7. Tablas de Base de Datos

### 7.1 CourseReportDB

**Ubicacion**: `backend/database/models.py` (linea 835)
**Sprint**: SPRINT 5 - HU-DOC-009: Reportes Institucionales

```sql
CREATE TABLE course_reports (
    id VARCHAR(36) PRIMARY KEY,
    course_id VARCHAR(100) NOT NULL,        -- ej: "PROG2_2025_1C"
    teacher_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    report_type VARCHAR(50) NOT NULL,       -- "cohort_summary", "risk_dashboard"
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    summary_stats JSON NOT NULL,
    competency_distribution JSON NOT NULL,
    risk_distribution JSON NOT NULL,
    top_risks JSON DEFAULT '[]',
    student_summaries JSON DEFAULT '[]',
    institutional_recommendations JSON DEFAULT '[]',
    at_risk_students JSON DEFAULT '[]',
    format VARCHAR(20) DEFAULT 'json',
    file_path TEXT,
    exported_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_course_report_course ON course_reports(course_id);
CREATE INDEX idx_course_report_teacher ON course_reports(teacher_id);
CREATE INDEX idx_report_teacher_course ON course_reports(teacher_id, course_id);
```

**Estructura summary_stats**:
```json
{
  "total_students": 45,
  "total_sessions": 320,
  "total_interactions": 1842,
  "avg_ai_dependency": 0.42
}
```

**Estructura competency_distribution**:
```json
{
  "AVANZADO": 12,
  "INTERMEDIO": 25,
  "BASICO": 8
}
```

**Estructura risk_distribution**:
```json
{
  "CRITICAL": 3,
  "HIGH": 8,
  "MEDIUM": 15,
  "LOW": 7
}
```

### 7.2 LTIDeploymentDB

**Ubicacion**: `backend/database/models.py` (linea 1272)
**Sprint**: HU-SYS-010: Integracion LTI 1.3

```sql
CREATE TABLE lti_deployments (
    id VARCHAR(36) PRIMARY KEY,
    platform_name VARCHAR(100) NOT NULL,    -- "Moodle", "Canvas", "Blackboard"
    issuer VARCHAR(255) NOT NULL,           -- LTI issuer URL
    client_id VARCHAR(255) NOT NULL,        -- OAuth2 client ID
    deployment_id VARCHAR(255) NOT NULL,    -- LTI deployment ID
    auth_login_url TEXT NOT NULL,           -- OIDC auth login URL
    auth_token_url TEXT NOT NULL,           -- OAuth2 token URL
    public_keyset_url TEXT NOT NULL,        -- JWKS URL
    access_token_url TEXT,                  -- LTI Advantage services
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE UNIQUE INDEX idx_lti_deployment_unique ON lti_deployments(issuer, deployment_id);
CREATE INDEX idx_lti_deployment_active ON lti_deployments(is_active);
```

**Relaciones**:
- `lti_sessions`: Relationship con LTISessionDB (cascade="all, delete-orphan")

### 7.3 LTISessionDB

**Ubicacion**: `backend/database/models.py` (linea 1364)
**Sprint**: HU-SYS-010: Integracion LTI 1.3

```sql
CREATE TABLE lti_sessions (
    id VARCHAR(36) PRIMARY KEY,
    deployment_id VARCHAR(36) NOT NULL REFERENCES lti_deployments(id) ON DELETE CASCADE,
    lti_user_id VARCHAR(255) NOT NULL,      -- User ID from Moodle
    lti_user_name VARCHAR(255),
    lti_user_email VARCHAR(255),
    lti_context_id VARCHAR(255),            -- Course ID from Moodle
    lti_context_label VARCHAR(100),         -- Course code
    lti_context_title VARCHAR(255),         -- Course name
    resource_link_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(36) REFERENCES sessions(id) ON DELETE SET NULL,
    launch_token TEXT,                      -- JWT token from LTI launch
    locale VARCHAR(10),                     -- User's locale (ej: "es_AR")
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_lti_session_user ON lti_sessions(lti_user_id);
CREATE INDEX idx_lti_session_resource ON lti_sessions(resource_link_id);
CREATE INDEX idx_lti_session_native ON lti_sessions(session_id);
```

**Relaciones**:
- `deployment`: Relationship con LTIDeploymentDB
- `session`: Relationship con SessionDB

---

## 8. Sistema de Reportes Institucionales

### 8.1 Vision General

**Ubicacion**: `backend/api/routers/reports.py`
**Sprint**: SPRINT 5 - HU-DOC-009

El sistema de reportes permite a docentes generar informes agregados sobre cohortes de estudiantes para analisis institucional y acreditacion.

### 8.2 Tipos de Reportes

| Tipo | Descripcion | Uso |
|------|-------------|-----|
| `cohort_summary` | Resumen agregado de cohorte | Seguimiento general |
| `risk_dashboard` | Dashboard de riesgos | Intervencion proactiva |
| `activity_report` | Reporte por actividad | Analisis de ejercicio |
| `learning_analytics` | Analiticas de aprendizaje | Tendencias temporales |

### 8.3 Reporte de Cohorte

**Endpoint**: `POST /api/v1/reports/cohort`

**Request**:
```json
{
  "course_id": "PROG2_2025_1C",
  "teacher_id": "teacher_001",
  "student_ids": ["student_001", "student_002", "..."],
  "period_start": "2025-03-01T00:00:00Z",
  "period_end": "2025-06-30T23:59:59Z",
  "export_format": "json"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "rpt_abc123",
    "course_id": "PROG2_2025_1C",
    "summary_stats": {
      "total_students": 45,
      "total_sessions": 320,
      "avg_ai_dependency": 0.42
    },
    "competency_distribution": {...},
    "risk_distribution": {...},
    "at_risk_students": ["student_015", "student_023"]
  }
}
```

### 8.4 Dashboard de Riesgos

**Endpoint**: `POST /api/v1/reports/risk-dashboard`

**Request**:
```json
{
  "course_id": "PROG2_2025_1C",
  "teacher_id": "teacher_001",
  "student_ids": ["student_001", "student_002"],
  "period_start": "2025-03-01T00:00:00Z",
  "period_end": "2025-06-30T23:59:59Z"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "report_id": "rpt_xyz789",
    "critical_students": ["student_015"],
    "risk_breakdown": {
      "cognitive": {"count": 12, "severity": "high"},
      "ethical": {"count": 3, "severity": "medium"}
    }
  }
}
```

### 8.5 Reporte de Actividad

**Endpoint**: `GET /api/v1/reports/activity/{activity_id}`

**Response**:
```json
{
  "success": true,
  "data": {
    "activity_id": "act_001",
    "activity_name": "Implementar Lista Enlazada",
    "total_sessions": 45,
    "completion_rate": 78.5,
    "avg_score": 7.2,
    "avg_ai_dependency": 0.38,
    "student_performance": [...],
    "risk_summary": {
      "total_risks": 12,
      "critical_count": 1,
      "high_count": 3,
      "medium_count": 5,
      "low_count": 3
    }
  }
}
```

### 8.6 Analiticas de Aprendizaje

**Endpoint**: `GET /api/v1/reports/analytics?period=week`

**Periodos Validos**: `day`, `week`, `month`, `year`

**Response**:
```json
{
  "success": true,
  "data": {
    "period": "week",
    "total_students": 150,
    "total_sessions": 420,
    "avg_session_duration": 35.5,
    "most_used_agents": [
      {"agent": "TUTOR", "usage_count": 280, "avg_satisfaction": 0.85},
      {"agent": "SIMULATOR", "usage_count": 95, "avg_satisfaction": 0.78}
    ],
    "competency_trends": [...],
    "risk_trends": [...]
  }
}
```

---

## 9. Integracion con Otros Agentes

### 9.1 Diagrama de Integracion

```
+------------------+
|     AIGateway    |
|   (Orquestador)  |
+--------+---------+
         |
         | process_request()
         v
+--------+---------+
|     GOV-IA       |<---------------------------+
|   (Gobernanza)   |                            |
+--------+---------+                            |
         |                                      |
         | verify_compliance()                  | risk_alerts
         | sanitize_prompt()                    |
         |                                      |
+--------v---------+                    +-------+------+
| TutorGovernance  |                    |    AR-IA     |
| Engine (Semaforo)|                    | (Analista de |
+--------+---------+                    |   Riesgos)   |
         |                              +-------^------+
         | process_student_request()            |
         |                                      |
+--------v---------+        +----------+        |
|   T-IA-Cog       |        |  E-IA    |        |
|   (Tutor)        |------->|  (Eval)  |--------+
+------------------+        +----------+
         |                        |
         +------------------------+
                  |
         +--------v--------+
         |     S-IA-X      |
         |  (Simuladores)  |
         +-----------------+
```

### 9.2 GOV-IA <-> AIGateway

**Flujo de Interaccion**:

1. AIGateway recibe request del cliente
2. AIGateway invoca `GOV-IA.verify_compliance()` con context
3. Si `status == VIOLATION`: Bloquea y retorna mensaje educativo
4. Si `status == WARNING`: Procede con restricciones
5. Si `status == COMPLIANT`: Procede normalmente
6. GOV-IA sanitiza prompt antes de enviarlo a LLM

### 9.3 GOV-IA <-> T-IA-Cog (Tutor)

**Flujo de Interaccion**:

1. TutorAgent recibe prompt sanitizado
2. Invoca `TutorGovernanceEngine.process_student_request()`
3. Obtiene estado de semaforo (VERDE/AMARILLO/ROJO)
4. Aplica estrategia de andamiaje segun semaforo
5. `TutorRulesEngine` verifica las 4 reglas fundamentales
6. Si regla violada: Genera intervencion pedagogica

**Reglas Aplicadas**:

| Regla | Aplicacion |
|-------|------------|
| ANTI_SOLUCION | Bloquea solicitudes de codigo completo |
| MODO_SOCRATICO | Prioriza preguntas sobre respuestas |
| EXIGIR_EXPLICITACION | Requiere justificaciones |
| REFUERZO_CONCEPTUAL | Redirige a conceptos teoricos |

### 9.4 GOV-IA <-> AR-IA (Analista de Riesgos)

**Flujo de Interaccion**:

1. AR-IA detecta riesgo durante interaccion
2. Envia alerta a GOV-IA con dimension y severidad
3. GOV-IA actualiza politicas dinamicamente
4. GOV-IA puede escalar semaforo a ROJO
5. GOV-IA registra en auditoria

**Dimensiones Monitoreadas por AR-IA**:

| Dimension | Codigo | Impacto en Gobernanza |
|-----------|--------|----------------------|
| Cognitiva | RC | Ajusta nivel de andamiaje |
| Etica | RE | Puede bloquear interaccion |
| Epistemica | REp | Requiere refuerzo conceptual |
| Tecnica | RT | Notificacion al docente |
| Gobernanza | RG | Alerta de politica violada |

### 9.5 GOV-IA <-> E-IA (Evaluador)

**Flujo de Interaccion**:

1. E-IA genera evaluacion de proceso
2. Incluye `ai_dependency_score` (0-1)
3. GOV-IA consulta score para ajustar politicas
4. Si `ai_dependency > 0.7`: Escala a AMARILLO/ROJO
5. Resultados se persisten en reportes institucionales

### 9.6 GOV-IA <-> S-IA-X (Simuladores)

**Flujo de Interaccion**:

1. Simuladores generan eventos (backlog_created, sprint_planning, etc.)
2. Eventos se registran en `SimulatorEventDB`
3. GOV-IA verifica cumplimiento de politicas en contexto simulado
4. Restricciones especiales para roles sensibles (devsecops, security_auditor)

---

## 10. API Endpoints

### 10.1 Endpoints de Reportes

| Metodo | Ruta | Descripcion | Autenticacion |
|--------|------|-------------|---------------|
| POST | `/reports/cohort` | Generar reporte de cohorte | Teacher |
| POST | `/reports/risk-dashboard` | Generar dashboard de riesgos | Teacher |
| GET | `/reports/{report_id}` | Obtener reporte por ID | Teacher |
| GET | `/reports/{report_id}/download` | Descargar archivo de reporte | Teacher |
| GET | `/reports/teacher/{teacher_id}` | Listar reportes de docente | Teacher |
| GET | `/reports/activity/{activity_id}` | Reporte de actividad | Teacher |
| GET | `/reports/analytics` | Analiticas de aprendizaje | Teacher |

### 10.2 Dependencias de Autenticacion

```python
from backend.api.deps import require_teacher_role

@router.post("/cohort")
async def generate_cohort_report(
    request: CohortReportRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_role),  # REQUERIDO
):
    ...
```

---

## 11. Flujos de Decision

### 11.1 Flujo Completo: Request de Estudiante

```
                            Estudiante envia prompt
                                     |
                                     v
+====================================+====================================+
|                           FASE 1: SEGURIDAD                           |
+========================================================================+
|                                                                        |
|   +------------------+                                                 |
|   | sanitize_prompt()|   Detecta: email, DNI, telefono, tarjeta       |
|   +--------+---------+                                                 |
|            |                                                           |
|            v                                                           |
|   +------------------+                                                 |
|   | PII encontrado?  |---[SI]--> Reemplaza con [REDACTED]             |
|   +--------+---------+                                                 |
|            |[NO]                                                       |
|            v                                                           |
+========================================================================+
                                     |
                                     v
+====================================+====================================+
|                         FASE 2: CUMPLIMIENTO                          |
+========================================================================+
|                                                                        |
|   +-------------------+                                                |
|   | verify_compliance()|                                               |
|   +--------+----------+                                                |
|            |                                                           |
|    +-------+-------+-------+                                           |
|    |               |       |                                           |
|    v               v       v                                           |
| COMPLIANT     WARNING   VIOLATION                                      |
|    |               |       |                                           |
|    v               v       v                                           |
| Continuar    Advertir   Bloquear                                       |
|                          + Educar                                      |
+========================================================================+
                                     |
                                     v
+====================================+====================================+
|                         FASE 3: SEMAFORO                              |
+========================================================================+
|                                                                        |
|   +------------------------+                                           |
|   | process_student_request|                                           |
|   +--------+---------------+                                           |
|            |                                                           |
|   [IPC] -> [GSR] -> [ANDAMIAJE]                                       |
|            |                                                           |
|    +-------+-------+-------+                                           |
|    |               |       |                                           |
|    v               v       v                                           |
|  VERDE        AMARILLO   ROJO                                          |
|    |               |       |                                           |
|    v               v       v                                           |
| Normal       Reducir    Bloquear                                       |
|              ayuda      codigo                                         |
+========================================================================+
                                     |
                                     v
+====================================+====================================+
|                      FASE 4: REGLAS PEDAGOGICAS                       |
+========================================================================+
|                                                                        |
|   +--------------------+                                               |
|   | check_anti_solution|--[VIOLADA]--> Rechazo Pedagogico             |
|   +--------+-----------+                                               |
|            |[OK]                                                       |
|            v                                                           |
|   +---------------------+                                              |
|   | check_socratic_mode |--[FORZAR]--> Generar pregunta               |
|   +--------+------------+                                              |
|            |[OK]                                                       |
|            v                                                           |
|   +-----------------------+                                            |
|   | check_explicitacion   |--[FALTA]--> Exigir justificacion          |
|   +--------+--------------+                                            |
|            |[OK]                                                       |
|            v                                                           |
|   +------------------------+                                           |
|   | check_conceptual_reinf |--[ERROR]--> Remision a teoria            |
|   +--------+---------------+                                           |
|            |[OK]                                                       |
|            v                                                           |
+========================================================================+
                                     |
                                     v
                          Generar respuesta del tutor
```

### 11.2 Matriz de Decisiones por Semaforo

| Semaforo | Codigo? | Pseudocodigo? | Respuesta Tipo | Nivel Ayuda | Justificacion? |
|----------|---------|---------------|----------------|-------------|----------------|
| VERDE | NO | SI | Variable | Variable | SI |
| AMARILLO | NO | SI | Pistas | Bajo | SI (enfatico) |
| ROJO | NO | NO | Socratico | Minimo | OBLIGATORIO |

---

## 12. Resumen Ejecutivo

### 12.1 Componentes Clave

| Componente | Archivo | Responsabilidad |
|------------|---------|-----------------|
| GobernanzaAgent | `governance.py` | Politicas institucionales, PII, auditoria |
| TutorGovernanceEngine | `tutor_governance.py` | Semaforos, 3 fases, restricciones |
| TutorRulesEngine | `tutor_rules.py` | 4 reglas inquebrantables |
| Security Module | `core/security.py` | JWT, contrasenas |
| Reports Router | `routers/reports.py` | Reportes institucionales |

### 12.2 Tablas de Persistencia

| Tabla | Modelo | Funcion |
|-------|--------|---------|
| `course_reports` | CourseReportDB | Reportes agregados de cohortes |
| `lti_deployments` | LTIDeploymentDB | Configuracion de plataformas LMS |
| `lti_sessions` | LTISessionDB | Sesiones de lanzamiento LTI |

### 12.3 Estados de Cumplimiento

```
COMPLIANT -> Proceder normalmente
WARNING   -> Proceder con advertencia
VIOLATION -> Bloquear y educar
```

### 12.4 Estados de Semaforo

```
VERDE    -> Interaccion normal
AMARILLO -> Reducir ayuda, monitorear
ROJO     -> Bloquear codigo, redirigir
```

### 12.5 Las 4 Reglas Inquebrantables

1. **ANTI_SOLUCION**: Nunca dar codigo completo
2. **MODO_SOCRATICO**: Preguntar antes de responder
3. **EXIGIR_EXPLICITACION**: Forzar justificacion
4. **REFUERZO_CONCEPTUAL**: Ir a teoria, no parches

### 12.6 Integracion Inter-Agentes

```
GOV-IA <==> AIGateway (verificacion pre-proceso)
GOV-IA <==> T-IA-Cog (semaforos y reglas)
GOV-IA <==> AR-IA (alertas de riesgo)
GOV-IA <==> E-IA (ai_dependency_score)
GOV-IA <==> S-IA-X (politicas en simuladores)
```

---

**Documento generado**: Diciembre 2025
**Version**: 1.0
**Autor**: Claude Code (Arquitectura Backend)
**Proyecto**: AI-Native MVP - Tesis Doctoral

---

## Referencias

- `backend/agents/governance.py` - Agente GOV-IA principal
- `backend/agents/tutor_governance.py` - Motor de semaforos
- `backend/agents/tutor_rules.py` - Reglas pedagogicas
- `backend/core/security.py` - Seguridad JWT/bcrypt
- `backend/api/routers/reports.py` - Endpoints de reportes
- `backend/database/models.py` - Modelos ORM (CourseReportDB, LTI*)
- CLAUDE.md - Documentacion general del proyecto