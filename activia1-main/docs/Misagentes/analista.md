# AR-IA: Analista de Riesgo Cognitivo y Ético - Documentación Técnica Completa

## Informe Profesional del Submodelo 4 del Sistema AI-Native

**Archivo**: `backend/agents/risk_analyst.py`
**Versión**: 2.0 (Diciembre 2025)
**Autor del Análisis**: Claude Code
**Fecha**: Diciembre 2025 15

---

## 1. Visión General

El **AR-IA (Analista de Riesgo Cognitivo y Ético)** es el submodelo 4 del ecosistema AI-Native encargado de supervisar, detectar y clasificar riesgos en 5 dimensiones durante el proceso de aprendizaje del estudiante.

### 1.1 Propósito Principal

```
AR-IA supervisa el proceso de aprendizaje para detectar comportamientos de riesgo
que podrían comprometer:
- La integridad del aprendizaje (cognitivo)
- La integridad académica (ético)
- La construcción de conocimiento sólido (epistémico)
- La calidad del código producido (técnico)
- El cumplimiento de políticas institucionales (gobernanza)
```

### 1.2 Fundamentos Teóricos

El AR-IA se basa en estándares internacionales:

| Estándar | Año | Aplicación |
|----------|-----|------------|
| UNESCO - Ética de IA | 2021 | Marco ético para uso educativo de IA |
| OECD AI Principles | 2019 | Principios de transparencia y responsabilidad |
| IEEE Ethically Aligned Design | 2019 | Diseño ético de sistemas de IA |
| ISO/IEC 23894 | 2023 | Risk Management in AI |
| ISO/IEC 42001 | 2023 | AI Management System |

---

## 2. Las 5 Dimensiones de Riesgo (5D)

### 2.1 Diagrama de Dimensiones

```
                        ┌─────────────────────────────────────────────┐
                        │           AR-IA: ANÁLISIS 5D                │
                        │        Supervisión Multidimensional          │
                        └─────────────────────────────────────────────┘
                                            │
           ┌────────────────────────────────┼────────────────────────────────┐
           │                                │                                │
           ▼                                ▼                                ▼
┌─────────────────────┐          ┌─────────────────────┐          ┌─────────────────────┐
│     COGNITIVO       │          │       ÉTICO         │          │     EPISTÉMICO      │
│       (RC)          │          │       (RE)          │          │       (REp)         │
├─────────────────────┤          ├─────────────────────┤          ├─────────────────────┤
│ • Delegación total  │          │ • Integridad acad.  │          │ • Error conceptual  │
│ • Razonamiento sup. │          │ • Uso no declarado  │          │ • Falacia lógica    │
│ • Dependencia IA    │          │ • Plagio            │          │ • Aceptación acrít. │
│ • Falta justific.   │          │                     │          │                     │
│ • Sin autorregulac. │          │                     │          │                     │
└─────────────────────┘          └─────────────────────┘          └─────────────────────┘
           │                                                                 │
           │                    ┌─────────────────────────────────┐         │
           │                    │                                  │         │
           ▼                    ▼                                  ▼         ▼
┌─────────────────────┐          ┌─────────────────────┐
│      TÉCNICO        │          │    GOBERNANZA       │
│       (RT)          │          │       (RG)          │
├─────────────────────┤          ├─────────────────────┤
│ • Vulnerabilidad    │          │ • Violación políti. │
│ • Baja calidad cod. │          │ • Uso no autorizado │
│ • Fallo arquitect.  │          │ • Automatización    │
└─────────────────────┘          └─────────────────────┘
```

### 2.2 Detalle de Tipos de Riesgo por Dimensión

#### 2.2.1 Riesgos Cognitivos (RC)

| Código | Tipo | Descripción | Nivel Típico |
|--------|------|-------------|--------------|
| RC1 | `COGNITIVE_DELEGATION` | Solicitar código completo sin descomposición | HIGH |
| RC2 | `SUPERFICIAL_REASONING` | Razonamiento superficial sin profundidad | MEDIUM |
| RC3 | `AI_DEPENDENCY` | Dependencia excesiva de IA (>70%) | MEDIUM |
| RC4 | `LACK_JUSTIFICATION` | Decisiones sin justificación | MEDIUM |
| RC5 | `NO_SELF_REGULATION` | Falta de autorregulación del aprendizaje | LOW |

**Señales de Delegación Total**:
```python
delegation_signals = [
    "dame el código completo",
    "hacé todo",
    "resolvelo por mí",
    "código entero",
    "implementa todo",
    "haceme"
]
```

#### 2.2.2 Riesgos Éticos (RE)

| Código | Tipo | Descripción | Nivel Típico |
|--------|------|-------------|--------------|
| RE1 | `ACADEMIC_INTEGRITY` | Violación de integridad académica | HIGH |
| RE2 | `UNDISCLOSED_AI_USE` | Uso no declarado de IA | MEDIUM |
| RE3 | `PLAGIARISM` | Plagio de código o contenido | CRITICAL |

**Detección de Código Sospechoso**:
```python
# Detectar código enviado demasiado rápido
if time_diff < 5 and code_length > 100 and is_code:
    # ALERTA: Código sospechoso
    # Tiempo < 5 segundos + > 100 caracteres de código
    # = Posible copia de fuente externa
```

#### 2.2.3 Riesgos Epistémicos (REp)

| Código | Tipo | Descripción | Nivel Típico |
|--------|------|-------------|--------------|
| REp1 | `CONCEPTUAL_ERROR` | Error en comprensión conceptual | MEDIUM |
| REp2 | `LOGICAL_FALLACY` | Falacia lógica en razonamiento | MEDIUM |
| REp3 | `UNCRITICAL_ACCEPTANCE` | Aceptar respuestas de IA sin cuestionar | MEDIUM |

#### 2.2.4 Riesgos Técnicos (RT)

| Código | Tipo | Descripción | Nivel Típico |
|--------|------|-------------|--------------|
| RT1 | `SECURITY_VULNERABILITY` | Código con vulnerabilidades de seguridad | MEDIUM-HIGH |
| RT2 | `POOR_CODE_QUALITY` | Código de baja calidad (DRY violations) | LOW |
| RT3 | `ARCHITECTURAL_FLAW` | Fallo arquitectónico o de diseño | MEDIUM |

**Patrones de Seguridad Detectados**:
```python
security_patterns = [
    ("sql injection", ["execute(", "cursor.execute", "SELECT * FROM", "' OR '", "\" OR \""]),
    ("hardcoded secrets", ["password=", "api_key=", "secret=", "token="]),
    ("eval/exec", ["eval(", "exec(", "compile("]),
]
```

#### 2.2.5 Riesgos de Gobernanza (RG)

| Código | Tipo | Descripción | Nivel Típico |
|--------|------|-------------|--------------|
| RG1 | `POLICY_VIOLATION` | Violación de políticas institucionales | LOW-MEDIUM |
| RG2 | `UNAUTHORIZED_USE` | Uso no autorizado del sistema | MEDIUM |
| RG3 | `AUTOMATION_SUSPECTED` | Patrón de uso automatizado sospechoso | MEDIUM |

---

## 3. Niveles de Severidad

### 3.1 Clasificación de Niveles

```python
class RiskLevel(str, Enum):
    CRITICAL = "critical"  # Requiere intervención inmediata del docente
    HIGH = "high"          # Requiere atención prioritaria
    MEDIUM = "medium"      # Monitorear y guiar al estudiante
    LOW = "low"            # Informativo, registrar para análisis
    INFO = "info"          # Solo registro, sin acción requerida
```

### 3.2 Matriz de Decisión de Nivel

| Riesgos Críticos | Riesgos Altos | Riesgos Medios | Evaluación General |
|------------------|---------------|----------------|-------------------|
| > 0 | - | - | **CRÍTICO**: Intervención docente inmediata |
| 0 | > 2 | - | **ALTO**: Atención prioritaria |
| 0 | 1-2 | > 3 | **MODERADO**: Monitoreo + prevención |
| 0 | 0 | ≤ 3 | **BAJO**: Dentro de parámetros |

---

## 4. Umbrales de Detección

### 4.1 Configuración de Umbrales

```python
self.thresholds = {
    "ai_dependency": 0.7,              # 70% → Genera riesgo AI_DEPENDENCY
    "delegation_consecutive": 3,        # 3 intentos → Genera riesgo DELEGATION
    "no_justification_ratio": 0.6,      # 60% sin justificar → Genera riesgo
}
```

### 4.2 Umbrales del Sistema (constants.py)

```python
# Umbrales de dependencia de IA
AI_DEPENDENCY_LOW_THRESHOLD = 0.3      # 30% - Sin riesgo
AI_DEPENDENCY_MEDIUM_THRESHOLD = 0.6   # 60% - Riesgo MEDIUM
AI_DEPENDENCY_HIGH_THRESHOLD = 0.8     # 80% - Riesgo HIGH
GOVERNANCE_BLOCK_THRESHOLD = 0.9       # 90% - Bloqueo automático

# Configuración de sesión
max_session_hours = 4  # Sesiones > 4h → Riesgo POLICY_VIOLATION
```

---

## 5. Arquitectura Interna

### 5.1 Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AR-IA: AnalistaRiesgoAgent                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│   │   LLM Provider  │    │    Thresholds   │    │     Config      │        │
│   │   (Opcional)    │    │ (Configurables) │    │  (Dict[str,Any])│        │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                     analyze_session(trace_sequence)                   │  │
│   │                                                                        │  │
│   │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │  │
│   │   │  _analyze_   │  │  _analyze_   │  │  _analyze_   │               │  │
│   │   │  cognitive_  │  │  ethical_    │  │  epistemic_  │               │  │
│   │   │  risks()     │  │  risks()     │  │  risks()     │               │  │
│   │   └──────────────┘  └──────────────┘  └──────────────┘               │  │
│   │                                                                        │  │
│   │   ┌──────────────┐  ┌──────────────┐                                  │  │
│   │   │  _analyze_   │  │  _analyze_   │                                  │  │
│   │   │  technical_  │  │  governance_ │                                  │  │
│   │   │  risks()     │  │  risks()     │                                  │  │
│   │   └──────────────┘  └──────────────┘                                  │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                          Helpers                                       │  │
│   │                                                                        │  │
│   │   • _is_delegation(content)        • _looks_like_code(content)        │  │
│   │   • _count_delegation_attempts()   • _calculate_similarity()          │  │
│   │   • _calculate_justification_ratio()                                   │  │
│   │   • _generate_overall_assessment()  • _generate_priority_interventions()│  │
│   │   • _analyze_trends()                                                  │  │
│   └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│                                    ▼                                         │
│                         ┌─────────────────┐                                 │
│                         │   RiskReport    │                                 │
│                         │ (Output Model)  │                                 │
│                         └─────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Flujo de Análisis de Sesión

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    FLUJO: analyze_session(trace_sequence)                    │
└─────────────────────────────────────────────────────────────────────────────┘

                    TraceSequence
                          │
                          ▼
            ┌─────────────────────────┐
            │   Crear RiskReport      │
            │   vacío con metadata    │
            └─────────────┬───────────┘
                          │
          ┌───────────────┼───────────────┬───────────────┬───────────────┐
          │               │               │               │               │
          ▼               ▼               ▼               ▼               ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │Cognitivo │   │  Ético   │   │Epistémico│   │ Técnico  │   │Gobernanza│
    │ (RC)     │   │  (RE)    │   │  (REp)   │   │  (RT)    │   │  (RG)    │
    │          │   │          │   │          │   │          │   │          │
    │• RC1-RC5 │   │• RE1-RE3 │   │• REp1-3  │   │• RT1-RT3 │   │• RG1-RG3 │
    └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘
          │               │               │               │               │
          └───────────────┴───────────────┴───────────────┴───────────────┘
                                          │
                                          ▼
                            ┌─────────────────────────┐
                            │    report.add_risk()    │
                            │   (para cada riesgo)    │
                            └─────────────┬───────────┘
                                          │
                                          ▼
                            ┌─────────────────────────┐
                            │ _generate_overall_      │
                            │ assessment(report)      │
                            └─────────────┬───────────┘
                                          │
                                          ▼
                            ┌─────────────────────────┐
                            │ _generate_priority_     │
                            │ interventions(report)   │
                            └─────────────┬───────────┘
                                          │
                                          ▼
                            ┌─────────────────────────┐
                            │   _analyze_trends()     │
                            │ (mejorando/empeorando)  │
                            └─────────────┬───────────┘
                                          │
                                          ▼
                               ┌─────────────────┐
                               │   RiskReport    │
                               │   completo      │
                               └─────────────────┘
```

---

## 6. Relación con Otros Agentes

### 6.1 Diagrama de Interacciones

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTERACCIONES DEL AR-IA CON OTROS AGENTES                 │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │  AI GATEWAY │
                              │ (Orquestador)│
                              └──────┬──────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
                    ▼                ▼                ▼
           ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
           │   T-IA-Cog  │   │   AR-IA     │   │   GOV-IA   │
           │   (Tutor)   │◄──│  (Analista) │──►│(Gobernanza) │
           └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
                  │                 │                  │
                  │                 │                  │
                  ▼                 ▼                  ▼
           ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
           │ Ajustar modo│   │ Registrar   │   │  Verificar  │
           │ pedagógico  │   │ en TC-N4    │   │ compliance  │
           └─────────────┘   └─────────────┘   └─────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
           ┌─────────────┐                 ┌─────────────┐
           │   TC-N4     │                 │  E-IA-Proc  │
           │(Trazabilidad)│                 │ (Evaluador) │
           └─────────────┘                 └─────────────┘
```

### 6.2 Matriz de Interacciones (RACI)

| Agente | Relación con AR-IA | Tipo de Interacción |
|--------|-------------------|---------------------|
| **AI Gateway** | Invocador principal | Gateway llama a AR-IA después de cada interacción |
| **T-IA-Cog (Tutor)** | Receptor de señales | AR-IA informa al tutor para ajustar modo pedagógico |
| **GOV-IA (Gobernanza)** | Bidireccional | AR-IA reporta violaciones; GOV-IA define políticas |
| **TC-N4 (Trazabilidad)** | Proveedor de datos | AR-IA consume trazas para análisis |
| **E-IA-Proc (Evaluador)** | Consumidor | Evaluador usa reportes de riesgo para evaluación final |
| **S-IA-X (Simuladores)** | Fuente de eventos | AR-IA analiza eventos de simuladores |

### 6.3 Flujo de Datos entre Agentes

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    FLUJO DE DATOS: AR-IA EN EL ECOSISTEMA                  │
└───────────────────────────────────────────────────────────────────────────┘

1. ENTRADA DE DATOS
   ┌──────────────┐
   │  TC-N4       │ ──────► TraceSequence ──────► AR-IA
   │ (Trazas N4)  │         (CognitiveTrace[])
   └──────────────┘

   ┌──────────────┐
   │  S-IA-X      │ ──────► SimulatorEventDB[] ──────► AR-IA
   │ (Simuladores)│         (eventos de sesión)
   └──────────────┘

2. PROCESAMIENTO
   AR-IA analiza:
   • Patrones de delegación en prompts
   • Tiempos de respuesta (código sospechoso)
   • Aceptación acrítica de respuestas
   • Vulnerabilidades en código
   • Patrones de automatización

3. SALIDA DE DATOS
   AR-IA ──────► RiskReport ──────► AI Gateway
                                   │
                                   ├──► T-IA-Cog (ajustar andamiaje)
                                   ├──► GOV-IA (verificar compliance)
                                   └──► E-IA-Proc (incluir en evaluación)

4. PERSISTENCIA
   AR-IA ──────► RiskDB ──────► PostgreSQL
                │
                └──► RiskAlertDB (alertas institucionales)
```

---

## 7. Modelos de Datos

### 7.1 Modelo Risk (Pydantic)

```python
class Risk(BaseModel):
    """Representa un riesgo detectado por el AR-IA"""

    # Identificación
    id: str
    session_id: str          # REQUERIDO - contexto de la sesión
    student_id: str
    activity_id: str

    # Clasificación
    risk_type: RiskType      # cognitive_delegation, ai_dependency, etc.
    risk_level: RiskLevel    # critical, high, medium, low, info
    dimension: RiskDimension # cognitive, ethical, epistemic, technical, governance

    # Descripción
    description: str
    impact: Optional[str]
    evidence: List[str]      # Evidencias del riesgo
    trace_ids: List[str]     # IDs de trazas relacionadas

    # Análisis
    root_cause: Optional[str]
    impact_assessment: Optional[str]

    # Recomendaciones
    recommendations: List[str]
    pedagogical_intervention: Optional[str]

    # Estado
    resolved: bool = False
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]

    # Metadata
    detected_by: str = "AR-IA"
    created_at: datetime
```

### 7.2 Modelo RiskReport (Pydantic)

```python
class RiskReport(BaseModel):
    """Reporte agregado de riesgos para un estudiante/actividad"""

    id: str
    created_at: datetime
    student_id: str
    activity_id: Optional[str]

    # Estadísticas
    total_risks: int = 0
    critical_risks: int = 0
    high_risks: int = 0
    medium_risks: int = 0
    low_risks: int = 0

    # Distribución por tipo
    risk_distribution: Dict[str, int]

    # Riesgos individuales
    risks: List[Risk]

    # Análisis agregado
    overall_assessment: Optional[str]
    priority_interventions: List[str]
    trends: Dict[str, Any]

    def add_risk(self, risk: Risk) -> None:
        """Añade un riesgo al reporte con actualización de contadores"""
```

### 7.3 Modelo RiskDB (SQLAlchemy ORM)

```python
class RiskDB(Base, BaseModel):
    """Database model for detected risks"""

    __tablename__ = "risks"

    # Foreign Keys
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=False)

    # Classification
    risk_type = Column(String(100), nullable=False)
    risk_level = Column(String(20), nullable=False)  # CHECK constraint
    dimension = Column(String(50), nullable=False)

    # Content
    description = Column(Text, nullable=False)
    impact = Column(Text, nullable=True)
    evidence = Column(JSON, default=list)
    trace_ids = Column(JSON, default=list)

    # Analysis
    root_cause = Column(Text, nullable=True)
    impact_assessment = Column(Text, nullable=True)
    recommendations = Column(JSON, default=list)
    pedagogical_intervention = Column(Text, nullable=True)

    # Status
    resolved = Column(Boolean, default=False, server_default='false')
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    detected_by = Column(String(50), default="AR-IA")

    # Relationship
    session = relationship("SessionDB", back_populates="risks")

    # Composite Indexes
    __table_args__ = (
        Index('idx_student_resolved', 'student_id', 'resolved'),
        Index('idx_level_created', 'risk_level', 'created_at'),
        Index('idx_student_activity_dimension', 'student_id', 'activity_id', 'dimension'),
        Index('idx_risk_session_type', 'session_id', 'risk_type'),
        Index('idx_risk_session_resolved', 'session_id', 'resolved'),
        Index('idx_risk_session_level', 'session_id', 'risk_level'),
        Index('idx_risk_resolved_at', 'resolved_at'),
        CheckConstraint("risk_level IN ('low', 'medium', 'high', 'critical', 'info')",
                        name='ck_risk_level_valid'),
    )
```

---

## 8. Tablas de Base de Datos

### 8.1 Tablas Principales del AR-IA

| Tabla | Propósito | FK Principal |
|-------|-----------|--------------|
| `risks` | Riesgos detectados por AR-IA | `session_id` → sessions |
| `risk_alerts` | Alertas institucionales automáticas | `student_id`, `assigned_to` |
| `remediation_plans` | Planes de remediación para estudiantes | `student_id`, `teacher_id` |

### 8.2 Estructura de la Tabla `risks`

```sql
CREATE TABLE risks (
    id VARCHAR(36) PRIMARY KEY,
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100) NOT NULL,

    -- Clasificación
    risk_type VARCHAR(100) NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low','medium','high','critical','info')),
    dimension VARCHAR(50) NOT NULL,

    -- Contenido
    description TEXT NOT NULL,
    impact TEXT,
    evidence JSONB DEFAULT '[]',
    trace_ids JSONB DEFAULT '[]',

    -- Análisis
    root_cause TEXT,
    impact_assessment TEXT,
    recommendations JSONB DEFAULT '[]',
    pedagogical_intervention TEXT,

    -- Estado
    resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    detected_by VARCHAR(50) DEFAULT 'AR-IA',

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_risk_session_resolved ON risks(session_id, resolved);
CREATE INDEX idx_risk_session_level ON risks(session_id, risk_level);
CREATE INDEX idx_student_resolved ON risks(student_id, resolved);
CREATE INDEX idx_level_created ON risks(risk_level, created_at);
```

### 8.3 Estructura de la Tabla `risk_alerts`

```sql
CREATE TABLE risk_alerts (
    id VARCHAR(36) PRIMARY KEY,

    -- Metadata
    alert_type VARCHAR(50) NOT NULL CHECK (
        alert_type IN ('critical_risk_surge','ai_dependency_spike','academic_integrity','pattern_anomaly')
    ),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low','medium','high','critical')),
    scope VARCHAR(20) NOT NULL,  -- student, activity, course, institution

    -- Scope identifiers
    student_id VARCHAR(100),
    activity_id VARCHAR(100),
    course_id VARCHAR(100),

    -- Content
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    evidence JSONB DEFAULT '[]',

    -- Detection
    detected_at TIMESTAMP DEFAULT NOW(),
    detection_rule VARCHAR(100) NOT NULL,
    threshold_value FLOAT,
    actual_value FLOAT,

    -- Assignment
    assigned_to VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    assigned_at TIMESTAMP,

    -- Resolution
    status VARCHAR(20) DEFAULT 'open',
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    resolution_notes TEXT,
    resolved_at TIMESTAMP,
    remediation_plan_id VARCHAR(36) REFERENCES remediation_plans(id) ON DELETE SET NULL,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 8.4 Estructura de la Tabla `remediation_plans`

```sql
CREATE TABLE remediation_plans (
    id VARCHAR(36) PRIMARY KEY,

    -- Target
    student_id VARCHAR(100) NOT NULL,
    activity_id VARCHAR(100),
    teacher_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,

    -- Trigger
    trigger_risks JSONB DEFAULT '[]',  -- List of Risk IDs

    -- Plan details
    plan_type VARCHAR(50) NOT NULL CHECK (
        plan_type IN ('tutoring','practice_exercises','conceptual_review','policy_clarification')
    ),
    description TEXT NOT NULL,
    objectives JSONB DEFAULT '[]',
    recommended_actions JSONB DEFAULT '[]',

    -- Timeline
    start_date TIMESTAMP NOT NULL,
    target_completion_date TIMESTAMP NOT NULL,
    actual_completion_date TIMESTAMP,

    -- Progress
    status VARCHAR(20) DEFAULT 'pending' CHECK (
        status IN ('pending','in_progress','completed','cancelled')
    ),
    progress_notes TEXT,
    completion_evidence JSONB DEFAULT '[]',

    -- Outcomes
    outcome_evaluation TEXT,
    success_metrics JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## 9. Endpoints de la API

### 9.1 Análisis de Riesgos 5D

```
GET /api/v1/risk-analysis/{session_id}
```

**Descripción**: Analiza riesgos en 5 dimensiones usando LLM (Ollama).

**Respuesta**:
```json
{
    "success": true,
    "message": "Risk analysis completed",
    "data": {
        "session_id": "550e8400-e29b-41d4-a716-446655440000",
        "overall_score": 35,
        "risk_level": "medium",
        "dimensions": {
            "cognitive": {"score": 4.5, "level": "medium", "indicators": ["Delegación detectada"]},
            "ethical": {"score": 2.0, "level": "low", "indicators": []},
            "epistemic": {"score": 3.0, "level": "low", "indicators": []},
            "technical": {"score": 2.5, "level": "low", "indicators": []},
            "governance": {"score": 1.0, "level": "low", "indicators": []}
        },
        "top_risks": [...],
        "recommendations": [...]
    }
}
```

### 9.2 Obtener Riesgos de Sesión

```
GET /api/v1/risks/session/{session_id}
```

**Parámetros Query**:
- `resolved`: `true`/`false` (opcional)
- `dimension`: `cognitive`/`ethical`/`epistemic`/`technical`/`governance` (opcional)

### 9.3 Obtener Riesgos de Estudiante

```
GET /api/v1/risks/student/{student_id}
```

### 9.4 Estadísticas de Riesgos

```
GET /api/v1/risks/student/{student_id}/statistics
```

**Respuesta**:
```json
{
    "success": true,
    "data": {
        "total_risks": 15,
        "by_level": {"high": 3, "medium": 8, "low": 4},
        "by_dimension": {"cognitive": 6, "technical": 5, "ethical": 2, "epistemic": 2},
        "by_type": {"cognitive_delegation": 4, "poor_code_quality": 3, ...},
        "resolution_rate": 60.0
    }
}
```

### 9.5 Riesgos Críticos

```
GET /api/v1/risks/critical
```

**Descripción**: Obtiene todos los riesgos críticos no resueltos del sistema. Útil para dashboard de gobernanza.

### 9.6 Análisis Automático de Sesión

```
POST /api/v1/risks/analyze-session/{session_id}
```

**Descripción**: Engine de análisis automático (AR-IA-AUTO) que detecta riesgos basándose en eventos de simulador.

**Reglas de Detección**:
1. `backlog_created` sin `acceptance_criteria` → RIESGO TÉCNICO
2. `sprint_planning_failed` → RIESGO DE GOBERNANZA
3. `technical_decision_made` sin `justification` → RIESGO DE CALIDAD
4. `security_scan_complete` con `vulnerabilities` → RIESGO DE SEGURIDAD
5. `deployment_completed` sin `tests_executed` → RIESGO OPERACIONAL

---

## 10. Repositorio de Riesgos

### 10.1 RiskRepository

```python
class RiskRepository:
    """Repository for risk operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, risk: Risk) -> RiskDB:
        """Create a new risk with transaction safety"""

    def get_by_id(self, risk_id: str) -> Optional[RiskDB]:
        """Get risk by ID"""

    def get_by_session(
        self,
        session_id: str,
        resolved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[RiskDB]:
        """Get all risks for a session with pagination"""

    def get_by_student(
        self,
        student_id: str,
        resolved: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[RiskDB]:
        """Get risks for a student with eager loading"""

    def get_critical_risks(
        self,
        student_id: Optional[str] = None,
        load_session_relations: bool = False
    ) -> List[RiskDB]:
        """Get all critical risks with optional eager loading"""

    def clean_orphan_trace_ids(self, session_id: str) -> int:
        """Clean trace_ids that reference non-existent traces"""

    def clean_all_orphan_trace_ids(self) -> int:
        """Clean orphan trace_ids across all risks"""
```

---

## 11. Análisis de Tendencias

### 11.1 Método de Análisis

```python
def _analyze_trends(self, trace_sequence: TraceSequence) -> Dict[str, Any]:
    """Analiza tendencias en el comportamiento del estudiante"""

    if len(traces) < 10:
        return {"insufficient_data": True}

    # Dividir en mitades para detectar mejora/empeoramiento
    mid = len(traces) // 2
    first_half = traces[:mid]
    second_half = traces[mid:]

    delegation_first = sum(1 for t in first_half if self._is_delegation(t.content))
    delegation_second = sum(1 for t in second_half if self._is_delegation(t.content))

    return {
        "delegation_trend": (
            "mejorando" if delegation_second < delegation_first
            else "empeorando" if delegation_second > delegation_first
            else "estable"
        ),
        "delegation_first_half": delegation_first,
        "delegation_second_half": delegation_second,
    }
```

### 11.2 Interpretación de Tendencias

| Tendencia | Interpretación | Acción Sugerida |
|-----------|----------------|-----------------|
| `mejorando` | Estudiante reduciendo delegación | Mantener estrategia actual |
| `empeorando` | Estudiante aumentando delegación | Intervención pedagógica inmediata |
| `estable` | Sin cambios significativos | Monitorear y reforzar |

---

## 12. Intervenciones Pedagógicas

### 12.1 Tipos de Intervención Generadas

| Riesgo | Intervención Pedagógica |
|--------|------------------------|
| `COGNITIVE_DELEGATION` | "Modo socrático estricto: solo preguntas, sin pistas directas" |
| `ACADEMIC_INTEGRITY` | "Solicitar que explique línea por línea el código enviado" |
| `AI_DEPENDENCY` | "Fomentar resolución autónoma con menos asistencia de IA" |
| `LACK_JUSTIFICATION` | "Exigir explícitamente justificaciones" |
| `SECURITY_VULNERABILITY` | "Revisar OWASP Top 10 y mejores prácticas" |

### 12.2 Priorización de Intervenciones

```python
def _generate_priority_interventions(self, report: RiskReport) -> List[str]:
    """Genera intervenciones prioritarias"""
    interventions = []

    # Priorizar por nivel: CRITICAL primero, luego HIGH
    critical_risks = [r for r in report.risks if r.risk_level == RiskLevel.CRITICAL]
    high_risks = [r for r in report.risks if r.risk_level == RiskLevel.HIGH]

    for risk in critical_risks + high_risks[:3]:  # Top 3 high risks
        if risk.pedagogical_intervention:
            interventions.append(risk.pedagogical_intervention)
        else:
            interventions.extend(risk.recommendations[:1])

    return interventions
```

---

## 13. Escalas y Métricas

### 13.1 Escalas del Sistema

| Métrica | Escala | Descripción |
|---------|--------|-------------|
| `RiskDimensionAnalysis.score` | 0-10 | Score individual por dimensión |
| `RiskAnalysis5D.overall_score` | 0-100 | Porcentaje de riesgo total |
| `ai_dependency_score` | 0-1 | Score de dependencia de IA |
| `justification_ratio` | 0-1 | Ratio de decisiones con justificación |

### 13.2 Cálculo del Score Overall

```python
# overall_score = suma de los 5 dimension scores
overall_score = sum(dimension_scores)  # Max teórico: 50

# Nivel de riesgo según overall_score
if overall_score >= 40:
    risk_level = "critical"
elif overall_score >= 30:
    risk_level = "high"
elif overall_score >= 15:
    risk_level = "medium"
else:
    risk_level = "low"
```

---

## 14. Archivos Relacionados

| Archivo | Propósito |
|---------|-----------|
| `backend/agents/risk_analyst.py` | Agente principal AR-IA |
| `backend/models/risk.py` | Modelos Pydantic (Risk, RiskReport) |
| `backend/api/schemas/risk.py` | Schemas API (RiskCreate, RiskResponse) |
| `backend/api/schemas/enums.py` | Enums (RiskLevel, RiskDimension) |
| `backend/api/routers/risk_analysis.py` | Router análisis 5D |
| `backend/api/routers/risks.py` | Router CRUD de riesgos |
| `backend/database/models.py` | ORM (RiskDB, RiskAlertDB, RemediationPlanDB) |
| `backend/database/repositories.py` | RiskRepository |
| `backend/core/ai_gateway.py` | Invocación de AR-IA |

---

## 15. Resumen Ejecutivo

El **AR-IA (Analista de Riesgo Cognitivo y Ético)** es un componente crítico del ecosistema AI-Native que:

1. **Supervisa 5 dimensiones de riesgo**: Cognitivo, Ético, Epistémico, Técnico y Gobernanza

2. **Detecta 18 tipos de riesgo** específicos clasificados en 5 niveles de severidad

3. **Genera intervenciones pedagógicas** priorizadas según el nivel de riesgo

4. **Analiza tendencias** del comportamiento del estudiante (mejorando/empeorando/estable)

5. **Persiste en 3 tablas** de base de datos:
   - `risks`: Riesgos individuales detectados
   - `risk_alerts`: Alertas institucionales automáticas
   - `remediation_plans`: Planes de remediación

6. **Interactúa con todos los agentes** del ecosistema:
   - Consume trazas de TC-N4
   - Informa a T-IA-Cog para ajustar andamiaje
   - Reporta a GOV-IA para compliance
   - Alimenta a E-IA-Proc para evaluación final

7. **Implementa estándares internacionales** de gestión de riesgos en IA (ISO/IEC 23894, ISO/IEC 42001)

El AR-IA es fundamental para garantizar que el uso de IA en el proceso de aprendizaje no comprometa la integridad cognitiva, ética y académica del estudiante.