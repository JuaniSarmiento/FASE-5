# 🚀 SPRINT 5: Git N2 + Analíticas - Plan Detallado

**Fecha Inicio**: 2025-11-21
**Duración Estimada**: 2 semanas (13 días)
**Story Points**: 39 SP
**Prioridad**: MEDIA
**Estado**: 🔄 EN PROGRESO

---

## 📋 OBJETIVOS DEL SPRINT

### Objetivo Principal
Completar la trazabilidad en 4 niveles (N1-N2-N3-N4) mediante integración con Git, y proveer herramientas de analíticas avanzadas para docentes y administradores.

### Objetivos Específicos

1. **Trazabilidad N2 (Técnica)**:
   - Capturar commits, branches, merges automáticamente
   - Correlacionar eventos Git con sesiones de aprendizaje
   - Analizar evolución del código a través de commits

2. **Analíticas de Curso**:
   - Reportes agregados de todos los estudiantes
   - Métricas de progreso y competencias
   - Exportación PDF/Excel

3. **Gestión de Riesgos Institucional**:
   - Dashboard de riesgos agregados
   - Alertas automáticas para riesgos críticos
   - Planes de remediación

---

## 📊 HISTORIAS DE USUARIO

### HU-SYS-008: Integración con Git para Trazabilidad N2

**Como** sistema
**Quiero** integrarme con repositorios Git de los estudiantes
**Para** capturar trazabilidad N2 (commits, branches, diff) y correlacionar con N3/N4

**Prioridad**: MEDIA
**Estimación**: 13 Story Points
**Complejidad**: ALTA

#### Criterios de Aceptación

- [ ] Módulo `GitIntegrationAgent` captura eventos Git automáticamente
- [ ] Almacena commits con: hash, mensaje, autor, timestamp, diff
- [ ] Almacena branches creados/mergeados
- [ ] Correlaciona commits con sesiones activas (temporal)
- [ ] API endpoint: `POST /api/v1/git/sync` para sincronización manual
- [ ] API endpoint: `GET /api/v1/traces/git/{session_id}` para consulta N2
- [ ] Análisis de evolución: líneas agregadas/eliminadas, archivos modificados
- [ ] Detección de patrones: copy-paste masivo, código generado por IA sin edición

#### Arquitectura Propuesta

```python
# Nuevo modelo: GitTrace (Trazabilidad N2)
class GitTrace(BaseModel):
    id: str
    session_id: str
    student_id: str
    activity_id: str

    # Git metadata
    commit_hash: str
    commit_message: str
    author_name: str
    author_email: str
    timestamp: datetime
    branch_name: str
    parent_commits: List[str]

    # Code changes
    files_changed: List[str]
    lines_added: int
    lines_deleted: int
    diff: str  # Full diff

    # Analysis
    is_merge: bool
    is_revert: bool
    detected_patterns: List[str]  # ["copy_paste", "ai_generated", etc.]
    complexity_delta: Optional[int]  # Change in cyclomatic complexity

    # Correlation with N3/N4
    related_traces: List[str]  # IDs de CognitiveTrace cercanos temporalmente
    cognitive_state_during_commit: Optional[str]

# Nuevo agente: GitIntegrationAgent
class GitIntegrationAgent:
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)

    def capture_commit(self, commit_hash: str, session_id: str) -> GitTrace:
        """Captura un commit y genera GitTrace"""

    def analyze_commit_pattern(self, commit: git.Commit) -> List[str]:
        """Detecta patrones sospechosos (copy-paste, AI-generated)"""

    def correlate_with_cognitive_traces(
        self,
        git_trace: GitTrace,
        time_window_minutes: int = 30
    ) -> List[str]:
        """Correlaciona commit con trazas cognitivas cercanas temporalmente"""

    def get_code_evolution(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """Analiza evolución del código durante una sesión"""

# Nueva tabla DB
class GitTraceDB(Base, BaseModel):
    __tablename__ = "git_traces"

    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    student_id = Column(String(100), nullable=False, index=True)
    activity_id = Column(String(100), nullable=False)

    commit_hash = Column(String(40), nullable=False, unique=True)
    commit_message = Column(Text, nullable=False)
    author_name = Column(String(200))
    author_email = Column(String(200))
    timestamp = Column(DateTime, nullable=False)
    branch_name = Column(String(200))

    files_changed = Column(JSON, default=list)
    lines_added = Column(Integer, default=0)
    lines_deleted = Column(Integer, default=0)
    diff = Column(Text)

    is_merge = Column(Boolean, default=False)
    is_revert = Column(Boolean, default=False)
    detected_patterns = Column(JSON, default=list)
    complexity_delta = Column(Integer, nullable=True)

    related_traces = Column(JSON, default=list)
    cognitive_state_during_commit = Column(String(50), nullable=True)
```

#### Endpoints API

```python
# Sincronizar repositorio Git
POST /api/v1/git/sync
{
    "session_id": "session_123",
    "repo_path": "/path/to/student/repo",
    "branch": "main"
}

# Obtener trazas Git de una sesión
GET /api/v1/traces/git/{session_id}
Response: List[GitTrace]

# Obtener evolución de código
GET /api/v1/traces/git/{session_id}/evolution
Response: {
    "total_commits": 15,
    "total_lines_added": 342,
    "total_lines_deleted": 87,
    "files_modified": ["main.py", "utils.py"],
    "commit_frequency": [...],
    "complexity_trend": [...]
}

# Correlacionar N2 con N3/N4
GET /api/v1/traces/git/{session_id}/correlate
Response: {
    "correlations": [
        {
            "commit_hash": "abc123",
            "timestamp": "2025-11-21T10:00:00",
            "cognitive_traces_nearby": [
                {
                    "trace_id": "trace_456",
                    "cognitive_state": "IMPLEMENTACION",
                    "time_diff_seconds": 120
                }
            ]
        }
    ]
}
```

---

### HU-DOC-006: Generar Reporte de Curso Completo

**Como** docente
**Quiero** generar un reporte agregado de todo el curso
**Para** evaluar progreso global, identificar tendencias, y tomar decisiones pedagógicas

**Prioridad**: MEDIA
**Estimación**: 13 Story Points

#### Criterios de Aceptación

- [ ] Endpoint: `POST /api/v1/reports/course` genera reporte
- [ ] Parámetros: course_id, activity_ids[], date_range, format (JSON/PDF)
- [ ] Métricas agregadas:
  - Total de estudiantes, sesiones, interacciones
  - Distribución de estados cognitivos
  - Promedio de AI involvement
  - Riesgos detectados (por dimensión)
  - Competencias promedio por dimensión
- [ ] Análisis de tendencias temporales
- [ ] Identificación de outliers (estudiantes con dificultades)
- [ ] Exportación PDF con gráficos (matplotlib/plotly)
- [ ] Exportación Excel con datos tabulares (openpyxl)

#### Arquitectura

```python
# Nuevo modelo: CourseReport
class CourseReport(BaseModel):
    id: str
    course_id: str
    teacher_id: str
    generated_at: datetime

    # Scope
    activity_ids: List[str]
    student_ids: List[str]
    date_range: Dict[str, datetime]  # {"start": ..., "end": ...}

    # Aggregate metrics
    total_students: int
    total_sessions: int
    total_interactions: int
    total_traces: int

    # Cognitive metrics
    cognitive_states_distribution: Dict[str, int]  # {"EXPLORACION": 45, ...}
    avg_ai_involvement: float
    avg_session_duration_minutes: float

    # Risks
    risks_by_dimension: Dict[str, int]  # {"COGNITIVE": 12, ...}
    critical_risks_count: int
    students_with_critical_risks: List[str]

    # Competencies
    avg_competencies: Dict[str, float]  # {"comprension": 0.75, ...}
    competencies_by_student: Dict[str, Dict[str, float]]

    # Trends
    interaction_trend: List[Dict[str, Any]]  # Time series
    ai_involvement_trend: List[Dict[str, Any]]

    # Outliers
    struggling_students: List[Dict[str, Any]]  # Below threshold
    advanced_students: List[Dict[str, Any]]  # Above threshold

    # Recommendations
    pedagogical_recommendations: List[str]

# Nuevo servicio: CourseReportGenerator
class CourseReportGenerator:
    def __init__(
        self,
        session_repo: SessionRepository,
        trace_repo: TraceRepository,
        risk_repo: RiskRepository,
        eval_repo: EvaluationRepository,
        git_repo: GitTraceRepository
    ):
        self.session_repo = session_repo
        self.trace_repo = trace_repo
        self.risk_repo = risk_repo
        self.eval_repo = eval_repo
        self.git_repo = git_repo

    def generate_report(
        self,
        course_id: str,
        activity_ids: List[str],
        date_range: Optional[Dict[str, datetime]] = None
    ) -> CourseReport:
        """Genera reporte agregado del curso"""

    def export_to_pdf(self, report: CourseReport, output_path: str) -> None:
        """Exporta a PDF con gráficos"""

    def export_to_excel(self, report: CourseReport, output_path: str) -> None:
        """Exporta a Excel con tablas"""
```

#### Endpoints API

```python
# Generar reporte de curso
POST /api/v1/reports/course
{
    "course_id": "prog2_2025",
    "activity_ids": ["tp1", "tp2", "tp3"],
    "date_range": {
        "start": "2025-09-01T00:00:00Z",
        "end": "2025-11-21T23:59:59Z"
    },
    "format": "json"  # or "pdf", "excel"
}

# Listar reportes generados
GET /api/v1/reports/course?teacher_id={teacher_id}

# Descargar reporte
GET /api/v1/reports/course/{report_id}/download?format=pdf
```

---

### HU-ADM-003: Gestionar Riesgos Críticos Institucionales

**Como** administrador institucional
**Quiero** ver dashboard de riesgos agregados y recibir alertas automáticas
**Para** gestionar riesgos a nivel institucional y cumplir normativas

**Prioridad**: ALTA
**Estimación**: 13 Story Points

#### Criterios de Aceptación

- [ ] Dashboard endpoint: `GET /api/v1/admin/risks/dashboard`
- [ ] Métricas agregadas:
  - Riesgos por dimensión (COGNITIVE, ETHICAL, etc.)
  - Riesgos por nivel de severidad (CRITICAL, HIGH, MEDIUM, LOW)
  - Tendencia temporal de riesgos
  - Top 10 estudiantes con más riesgos
  - Top 10 actividades con más riesgos
- [ ] Alertas automáticas:
  - Email cuando surge riesgo CRÍTICO
  - Webhook para integración con sistemas externos
- [ ] Planes de remediación:
  - Templates de intervención por tipo de riesgo
  - Asignación de responsables
  - Seguimiento de estado (OPEN, IN_PROGRESS, RESOLVED)

#### Arquitectura

```python
# Nuevo modelo: RiskAlert
class RiskAlert(BaseModel):
    id: str
    risk_id: str
    alert_type: str  # "email", "webhook", "sms"
    sent_at: datetime
    recipient: str
    status: str  # "sent", "failed", "pending"
    retry_count: int

# Nuevo modelo: RemediationPlan
class RemediationPlan(BaseModel):
    id: str
    risk_id: str
    created_at: datetime
    created_by: str  # admin_id

    status: str  # "OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"
    priority: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"

    # Plan
    description: str
    intervention_template: str
    assigned_to: Optional[str]  # teacher_id or admin_id
    due_date: Optional[datetime]

    # Tracking
    actions_taken: List[Dict[str, Any]]
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]

# Nuevo servicio: InstitutionalRiskManager
class InstitutionalRiskManager:
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Genera métricas para dashboard"""

    def send_alert(self, risk: Risk, alert_type: str) -> RiskAlert:
        """Envía alerta para riesgo crítico"""

    def create_remediation_plan(
        self,
        risk_id: str,
        admin_id: str
    ) -> RemediationPlan:
        """Crea plan de remediación"""

    def get_trends(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """Analiza tendencias de riesgos"""
```

#### Endpoints API

```python
# Dashboard de riesgos institucionales
GET /api/v1/admin/risks/dashboard
Response: {
    "total_risks": 156,
    "by_dimension": {"COGNITIVE": 45, "ETHICAL": 23, ...},
    "by_severity": {"CRITICAL": 5, "HIGH": 28, ...},
    "trend_last_30_days": [...],
    "top_students_with_risks": [...],
    "top_activities_with_risks": [...]
}

# Crear plan de remediación
POST /api/v1/admin/risks/{risk_id}/remediation
{
    "description": "Reunión con estudiante para revisar...",
    "assigned_to": "teacher_001",
    "due_date": "2025-12-01"
}

# Actualizar plan de remediación
PATCH /api/v1/admin/risks/remediation/{plan_id}
{
    "status": "IN_PROGRESS",
    "actions_taken": [
        {
            "timestamp": "2025-11-22T10:00:00Z",
            "action": "Reunión realizada con estudiante",
            "outcome": "Estudiante comprende los riesgos"
        }
    ]
}

# Configurar alertas
POST /api/v1/admin/alerts/config
{
    "alert_type": "email",
    "risk_levels": ["CRITICAL", "HIGH"],
    "recipients": ["admin@university.edu"],
    "enabled": true
}
```

---

## 📁 ESTRUCTURA DE ARCHIVOS NUEVOS

```
src/ai_native_mvp/
├── agents/
│   └── git_integration.py          # NEW: GitIntegrationAgent
├── services/
│   ├── course_report.py            # NEW: CourseReportGenerator
│   └── risk_management.py          # NEW: InstitutionalRiskManager
├── models/
│   ├── git_trace.py                # NEW: GitTrace, GitCommit
│   ├── course_report.py            # NEW: CourseReport
│   └── remediation.py              # NEW: RemediationPlan, RiskAlert
├── database/
│   └── models.py                   # ADD: GitTraceDB, RemediationPlanDB, RiskAlertDB
├── api/
│   └── routers/
│       ├── git.py                  # NEW: Git integration endpoints
│       ├── reports.py              # NEW: Course reports endpoints
│       └── admin_risks.py          # NEW: Admin risk management endpoints
└── utils/
    ├── git_analyzer.py             # NEW: Git diff analysis utilities
    └── report_exporter.py          # NEW: PDF/Excel exporters

scripts/
├── sync_git_traces.py              # NEW: CLI tool for Git sync
└── generate_course_report.py      # NEW: CLI tool for reports

examples/
└── sprint5_demo_git_analytics.py  # NEW: Demo completo Sprint 5
```

---

## ⏱️ CRONOGRAMA DETALLADO

### Día 1-2: HU-SYS-008 - Diseño e Infraestructura
- [ ] Diseñar modelo GitTrace + GitTraceDB
- [ ] Crear migraciones de base de datos
- [ ] Implementar GitTraceRepository
- [ ] Setup GitPython + tests básicos

### Día 3-4: HU-SYS-008 - Captura Git
- [ ] Implementar GitIntegrationAgent.capture_commit()
- [ ] Implementar análisis de patrones (copy-paste, AI-generated)
- [ ] Implementar correlación temporal con N3/N4
- [ ] Tests unitarios

### Día 5-6: HU-SYS-008 - API Endpoints
- [ ] Endpoint POST /api/v1/git/sync
- [ ] Endpoint GET /api/v1/traces/git/{session_id}
- [ ] Endpoint GET /api/v1/traces/git/{session_id}/evolution
- [ ] Endpoint GET /api/v1/traces/git/{session_id}/correlate
- [ ] Tests de integración

### Día 7-8: HU-DOC-006 - Reportes de Curso
- [ ] Implementar CourseReportGenerator
- [ ] Implementar agregación de métricas
- [ ] Implementar análisis de tendencias
- [ ] Implementar exportación PDF (matplotlib)
- [ ] Implementar exportación Excel (openpyxl)

### Día 9-10: HU-DOC-006 - API Endpoints Reportes
- [ ] Endpoint POST /api/v1/reports/course
- [ ] Endpoint GET /api/v1/reports/course (listar)
- [ ] Endpoint GET /api/v1/reports/course/{id}/download
- [ ] Tests de integración

### Día 11: HU-ADM-003 - Gestión de Riesgos
- [ ] Implementar InstitutionalRiskManager
- [ ] Dashboard de métricas agregadas
- [ ] Sistema de alertas (email)
- [ ] RemediationPlan CRUD

### Día 12: HU-ADM-003 - API Endpoints Admin
- [ ] Endpoint GET /api/v1/admin/risks/dashboard
- [ ] Endpoint POST /api/v1/admin/risks/{id}/remediation
- [ ] Endpoint PATCH /api/v1/admin/risks/remediation/{id}
- [ ] Endpoint POST /api/v1/admin/alerts/config

### Día 13: Testing + Documentación
- [ ] Tests end-to-end de Sprint 5
- [ ] Demo completo: examples/sprint5_demo_git_analytics.py
- [ ] Actualizar README con nuevas funcionalidades
- [ ] Documentar SPRINT_5_COMPLETADO.md

---

## 📦 DEPENDENCIAS

### Nuevas Bibliotecas Python

```python
# requirements.txt - AGREGAR
GitPython>=3.1.40           # Git integration
matplotlib>=3.8.0           # PDF charts
plotly>=5.18.0              # Interactive charts
openpyxl>=3.1.2             # Excel export
reportlab>=4.0.7            # PDF generation
pandas>=2.1.4               # Data analysis
```

### Instalación

```bash
pip install GitPython matplotlib plotly openpyxl reportlab pandas
```

---

## 🧪 ESTRATEGIA DE TESTING

### Tests Unitarios

```python
# tests/test_git_integration.py
def test_capture_commit_creates_git_trace()
def test_analyze_commit_detects_copy_paste()
def test_correlate_with_cognitive_traces()
def test_get_code_evolution()

# tests/test_course_report.py
def test_generate_report_aggregates_metrics()
def test_export_to_pdf_creates_file()
def test_export_to_excel_creates_file()
def test_identify_struggling_students()

# tests/test_risk_management.py
def test_get_dashboard_metrics()
def test_send_alert_creates_alert_record()
def test_create_remediation_plan()
```

### Tests de Integración

```python
# tests/test_api_git.py
def test_sync_git_creates_traces()
def test_get_git_traces_returns_list()
def test_get_evolution_calculates_metrics()

# tests/test_api_reports.py
def test_generate_course_report_returns_json()
def test_download_report_pdf_returns_file()
def test_list_reports_filters_by_teacher()

# tests/test_api_admin_risks.py
def test_get_dashboard_returns_metrics()
def test_create_remediation_plan_succeeds()
def test_update_remediation_plan_tracks_actions()
```

### Demo End-to-End

```python
# examples/sprint5_demo_git_analytics.py
def demo_git_integration():
    # 1. Sincronizar repo Git
    # 2. Capturar commits
    # 3. Correlacionar con trazas cognitivas
    # 4. Mostrar evolución de código

def demo_course_reports():
    # 1. Generar reporte de curso
    # 2. Exportar a PDF
    # 3. Exportar a Excel
    # 4. Mostrar métricas agregadas

def demo_risk_management():
    # 1. Ver dashboard de riesgos
    # 2. Crear plan de remediación
    # 3. Simular alerta automática
    # 4. Actualizar estado del plan
```

---

## 📊 MÉTRICAS DE ÉXITO

| Métrica | Objetivo | Verificación |
|---------|----------|--------------|
| **Funcionalidades Completadas** | 3/3 (100%) | Todas las HU implementadas |
| **Endpoints API** | 12+ | Swagger UI actualizado |
| **Tests Unitarios** | 20+ | pytest passing |
| **Coverage** | >70% | pytest-cov |
| **Líneas de Código** | ~800-1000 | Git diff |
| **Documentación** | Completa | README, SPRINT_5_COMPLETADO.md |
| **Demo Funcional** | Ejecutable | examples/sprint5_demo_git_analytics.py |

---

## 🚀 ENTREGABLES

1. **Código**:
   - Módulo de integración Git (GitIntegrationAgent)
   - Generador de reportes de curso (CourseReportGenerator)
   - Gestor de riesgos institucional (InstitutionalRiskManager)
   - 12+ endpoints API REST

2. **Base de Datos**:
   - Tabla GitTraceDB
   - Tabla RemediationPlanDB
   - Tabla RiskAlertDB

3. **Tests**:
   - 20+ tests unitarios
   - 10+ tests de integración
   - 1 demo end-to-end

4. **Documentación**:
   - SPRINT_5_COMPLETADO.md (resumen de completitud)
   - README actualizado con nuevas funcionalidades
   - API docs actualizado (Swagger)
   - Ejemplos de uso

---

## 🔄 PRÓXIMOS PASOS INMEDIATOS

1. ✅ Crear modelos Pydantic (GitTrace, CourseReport, RemediationPlan)
2. ✅ Crear modelos ORM (GitTraceDB, RemediationPlanDB, RiskAlertDB)
3. ✅ Implementar GitIntegrationAgent
4. ✅ Crear repositorios (GitTraceRepository, etc.)
5. ✅ Implementar endpoints API
6. ✅ Crear tests
7. ✅ Crear demo completo

**Comenzar ahora**: ¿Proceder con creación de modelos base?

---

**Documento generado**: 2025-11-21
**Autor**: Claude Code Agent
**Sprint**: 5
**Estado**: 🔄 PLANIFICACIÓN COMPLETADA → LISTO PARA IMPLEMENTACIÓN
