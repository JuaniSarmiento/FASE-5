# 🏗️ Arquitectura: Sistema de Ejercicios en PostgreSQL

## 📐 Diagrama de Tablas y Relaciones

```
┌────────────────────────────────────────────────────────────────────────┐
│                         SISTEMA DE EJERCICIOS                          │
└────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│     subjects        │  ← Materias (Python, Java)
├─────────────────────┤
│ PK  id              │  'PYTHON', 'JAVA', 'PROG1'
│     name            │  'Python', 'Java'
│     description     │
│     language        │  'python', 'java'
│     total_units     │
│     is_active       │
│     created_at      │
│     updated_at      │
└──────────┬──────────┘
           │
           │ 1:N
           ▼
┌─────────────────────┐
│     exercises       │  ← Ejercicios individuales
├─────────────────────┤
│ PK  id              │  'U1-VAR-01', 'condicionales'
│ FK  subject_id      │  → subjects.id
│     title           │
│     description     │
│     difficulty      │  'Easy', 'Medium', 'Hard'
│     time_min        │
│     unit            │  1-7
│     language        │  'python', 'java'
│                     │
│   ┌─ CONTENIDO ─┐  │
│   │ mission_md  │  │  ← Consigna completa
│   │ story_md    │  │  ← Contexto/historia
│   │ constraints │  │  ← Restricciones/requisitos
│   └─────────────┘  │
│                     │
│   ┌─ CÓDIGO ────┐  │
│   │ starter_code│  │  ← Código inicial (con TODOs)
│   │ solution    │  │  ← Solución (oculta, NO al frontend)
│   └─────────────┘  │
│                     │
│   ┌─ METADATA ──┐  │
│   │ tags (JSON) │  │  ← ['Variables', 'Condicionales']
│   │ objectives  │  │  ← Objetivos de aprendizaje
│   │ cog_level   │  │  ← Nivel cognitivo (Bloom)
│   └─────────────┘  │
│                     │
│   ┌─ VERSIONADO┐   │
│   │ version     │  │  ← Versionado de ejercicios
│   │ is_active   │  │
│   │ deleted_at  │  │  ← Soft delete
│   └─────────────┘  │
│                     │
│     created_at      │
│     updated_at      │
└──────────┬──────────┘
           │
           ├────────── 1:N ──────────┐
           │                         │
           │                         │
           ▼                         ▼
┌─────────────────────┐   ┌─────────────────────┐
│  exercise_hints     │   │  exercise_tests     │
├─────────────────────┤   ├─────────────────────┤
│ PK  id              │   │ PK  id              │
│ FK  exercise_id     │   │ FK  exercise_id     │
│     hint_number     │   │     test_number     │
│     title           │   │     description     │
│     content         │   │     input           │  ← "validar_nota(85)"
│     penalty_points  │   │     expected        │  ← "True"
│     created_at      │   │     is_hidden       │  ← Tests ocultos vs visibles
└─────────────────────┘   │     timeout_sec     │
                          │     created_at      │
                          └──────────┬──────────┘
                                     │
                          ┌──────────┘
                          │
                          │ FK (para validación)
                          ▼
┌─────────────────────────────────────────────────┐
│          exercise_attempts                       │  ← Intentos de estudiantes
├─────────────────────────────────────────────────┤
│ PK  id                                          │
│ FK  exercise_id      → exercises.id             │
│     student_id                                  │
│ FK  session_id       → sessions.id (existente)  │
│                                                 │
│   ┌─ CÓDIGO ENVIADO ────────────────────────┐  │
│   │ submitted_code                          │  │  ← Código del estudiante
│   └─────────────────────────────────────────┘  │
│                                                 │
│   ┌─ RESULTADOS ────────────────────────────┐  │
│   │ tests_passed                            │  │
│   │ tests_total                             │  │
│   │ score (0-10)                            │  │
│   │ status ('PASS', 'FAIL', 'ERROR')        │  │
│   └─────────────────────────────────────────┘  │
│                                                 │
│   ┌─ EJECUCIÓN ─────────────────────────────┐  │
│   │ execution_time_ms                       │  │
│   │ stdout                                  │  │
│   │ stderr                                  │  │
│   └─────────────────────────────────────────┘  │
│                                                 │
│   ┌─ FEEDBACK IA ───────────────────────────┐  │
│   │ ai_feedback_summary                     │  │  ← Toast corto
│   │ ai_feedback_detailed                    │  │  ← Markdown completo
│   │ ai_suggestions (JSON)                   │  │  ← Array de sugerencias
│   └─────────────────────────────────────────┘  │
│                                                 │
│   ┌─ PISTAS ────────────────────────────────┐  │
│   │ hints_used                              │  │
│   │ penalty_applied                         │  │
│   └─────────────────────────────────────────┘  │
│                                                 │
│     attempt_number                              │
│     submitted_at                                │
└─────────────────────────────────────────────────┘
           │
           │ FK
           ▼
┌─────────────────────┐
│     sessions        │  ← Tabla existente (Trazabilidad N4)
├─────────────────────┤
│ PK  id              │
│     student_id      │
│     activity_id     │
│     mode            │
│     ...             │
└─────────────────────┘
```

---

## 🔄 Flujo de Datos: Estudiante Resuelve Ejercicio

```
┌─────────────────────────────────────────────────────────────────┐
│  1. SELECCIÓN DE MATERIA                                        │
└─────────────────────────────────────────────────────────────────┘

Frontend: GET /training/materias
    ↓
Backend: SubjectRepository.get_all()
    ↓
PostgreSQL: SELECT * FROM subjects WHERE is_active = TRUE
    ↓
Backend: ExerciseRepository.get_by_subject(subject_id)
    ↓
PostgreSQL: SELECT * FROM exercises
            WHERE subject_id = 'PYTHON'
            AND deleted_at IS NULL
    ↓
Frontend: Muestra lista de ejercicios


┌─────────────────────────────────────────────────────────────────┐
│  2. INICIO DE ENTRENAMIENTO                                     │
└─────────────────────────────────────────────────────────────────┘

Frontend: POST /training/iniciar
    {
        "materia_codigo": "PYTHON",
        "tema_id": "U1-VAR-01"
    }
    ↓
Backend: ExerciseRepository.get_by_id("U1-VAR-01")
    ↓
PostgreSQL: SELECT * FROM exercises WHERE id = 'U1-VAR-01'
            + JOIN exercise_tests ON exercises.id = exercise_tests.exercise_id
            + JOIN exercise_hints ON exercises.id = exercise_hints.exercise_id
    ↓
Backend: Crear sesión en Redis/Memoria
    ↓
Frontend: Recibe:
    {
        "session_id": "abc-123",
        "ejercicio_actual": {
            "consigna": "...",
            "codigo_inicial": "def sumar(a, b):\n    pass"
        }
    }


┌─────────────────────────────────────────────────────────────────┐
│  3. ESTUDIANTE SOLICITA PISTA                                   │
└─────────────────────────────────────────────────────────────────┘

Frontend: POST /training/pista
    {
        "session_id": "abc-123",
        "numero_pista": 0
    }
    ↓
Backend: ExerciseHintRepository.get_by_exercise(exercise_id)
    ↓
PostgreSQL: SELECT * FROM exercise_hints
            WHERE exercise_id = 'U1-VAR-01'
            ORDER BY hint_number
    ↓
Backend:
    - Retorna hint[0]
    - Registra penalización en sesión (Redis/Memoria)
    ↓
Frontend: Muestra pista al estudiante


┌─────────────────────────────────────────────────────────────────┐
│  4. ESTUDIANTE ENVÍA CÓDIGO                                     │
└─────────────────────────────────────────────────────────────────┘

Frontend: POST /training/submit-ejercicio
    {
        "session_id": "abc-123",
        "codigo_usuario": "def sumar(a, b):\n    return a + b"
    }
    ↓
Backend: ExerciseTestRepository.get_by_exercise(exercise_id)
    ↓
PostgreSQL: SELECT * FROM exercise_tests
            WHERE exercise_id = 'U1-VAR-01'
            ORDER BY test_number
    ↓
Backend:
    - Ejecutar cada test con execute_python_code()
    - Comparar resultado vs expected
    - Contar tests_passed / tests_total
    ↓
Backend: CodeEvaluator.evaluate()
    - LLM analiza código
    - Genera feedback
    ↓
Backend: ExerciseAttemptRepository.create()
    ↓
PostgreSQL: INSERT INTO exercise_attempts (
                exercise_id,
                student_id,
                session_id,
                submitted_code,
                tests_passed,
                tests_total,
                score,
                status,
                ai_feedback_summary,
                ai_feedback_detailed,
                hints_used,
                execution_time_ms,
                submitted_at
            ) VALUES (...)
    ↓
Frontend: Muestra resultado
    {
        "resultado": {
            "correcto": true,
            "tests_pasados": 3,
            "tests_totales": 3,
            "mensaje": "¡Excelente! Todos los tests pasaron"
        },
        "hay_siguiente": true
    }
```

---

## 📊 Queries Comunes y sus Índices

### Query 1: Obtener ejercicios de una materia
```sql
SELECT * FROM exercises
WHERE subject_id = 'PYTHON'
  AND deleted_at IS NULL
ORDER BY unit, id;
```
**Índice usado**: `idx_exercises_subject`

---

### Query 2: Obtener tests de un ejercicio
```sql
SELECT * FROM exercise_tests
WHERE exercise_id = 'U1-VAR-01'
ORDER BY test_number;
```
**Índice usado**: `idx_tests_exercise`, `idx_tests_order`

---

### Query 3: Histórico de intentos de un estudiante
```sql
SELECT
    ea.*,
    e.title,
    e.difficulty
FROM exercise_attempts ea
JOIN exercises e ON ea.exercise_id = e.id
WHERE ea.student_id = 'student123'
ORDER BY ea.submitted_at DESC;
```
**Índice usado**: `idx_attempts_student`

---

### Query 4: Analytics - Tasa de éxito por ejercicio
```sql
SELECT
    e.id,
    e.title,
    e.difficulty,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN ea.status = 'PASS' THEN 1 ELSE 0 END) as passed_attempts,
    ROUND(
        SUM(CASE WHEN ea.status = 'PASS' THEN 1 ELSE 0 END)::DECIMAL / COUNT(*) * 100,
        2
    ) as success_rate
FROM exercises e
LEFT JOIN exercise_attempts ea ON e.id = ea.exercise_id
WHERE e.deleted_at IS NULL
GROUP BY e.id, e.title, e.difficulty
ORDER BY success_rate ASC;
```
**Índices usados**: `idx_attempts_exercise`, `idx_attempts_status`

---

### Query 5: Ejercicios más difíciles (más intentos promedio hasta aprobar)
```sql
WITH first_pass AS (
    SELECT
        ea.exercise_id,
        ea.student_id,
        MIN(ea.attempt_number) as attempts_to_pass
    FROM exercise_attempts ea
    WHERE ea.status = 'PASS'
    GROUP BY ea.exercise_id, ea.student_id
)
SELECT
    e.id,
    e.title,
    e.difficulty,
    ROUND(AVG(fp.attempts_to_pass), 2) as avg_attempts_to_pass
FROM exercises e
JOIN first_pass fp ON e.id = fp.exercise_id
GROUP BY e.id, e.title, e.difficulty
ORDER BY avg_attempts_to_pass DESC
LIMIT 10;
```
**Índices usados**: `idx_attempts_student_exercise`

---

### Query 6: Progreso de un estudiante
```sql
SELECT
    s.name as subject_name,
    COUNT(DISTINCT e.id) as total_exercises,
    COUNT(DISTINCT CASE WHEN ea.status = 'PASS' THEN e.id END) as completed_exercises,
    ROUND(
        COUNT(DISTINCT CASE WHEN ea.status = 'PASS' THEN e.id END)::DECIMAL
        / COUNT(DISTINCT e.id) * 100,
        2
    ) as completion_percentage
FROM subjects s
JOIN exercises e ON s.id = e.subject_id
LEFT JOIN exercise_attempts ea ON e.id = ea.exercise_id
    AND ea.student_id = 'student123'
WHERE e.deleted_at IS NULL
GROUP BY s.id, s.name;
```

---

## 🔐 Seguridad y Permisos

### Datos sensibles que NO se envían al frontend

1. **Solución completa**: `exercises.solution_code`
2. **Tests ocultos expected**: `exercise_tests.expected` cuando `is_hidden = TRUE`
3. **Feedback detallado de otros estudiantes**: Solo sus propios attempts

### Control de acceso

```python
# Students: Solo pueden ver sus propios attempts
if current_user.role == 'STUDENT':
    attempts = attempt_repo.get_by_student(current_user.id)

# Teachers: Pueden ver attempts de sus estudiantes
if current_user.role == 'TEACHER':
    attempts = attempt_repo.get_by_student(student_id)
    # Validar que student pertenece al curso del teacher

# Admins: Acceso total
if current_user.role == 'ADMIN':
    attempts = attempt_repo.get_all()
```

---

## 📈 Métricas y Analytics Disponibles

### Por Ejercicio
- Tasa de éxito (% de attempts que pasan)
- Promedio de intentos hasta aprobar
- Tiempo promedio de resolución
- Pistas más solicitadas
- Tests que más fallan

### Por Estudiante
- Ejercicios completados / totales
- Porcentaje de completitud por materia
- Promedio de score
- Ejercicios donde necesitó más intentos
- Uso de pistas (frecuencia)

### Por Materia
- Ejercicios más difíciles
- Ejercicios más fáciles
- Distribución de dificultad
- Tiempo total invertido por estudiantes

---

## 🎯 Integración con Sistema Existente

### Relación con Trazabilidad N4

```
exercise_attempts.session_id → sessions.id
    ↓
sessions → interactions → cognitive_traces
    ↓
Trazabilidad N4 completa:
- N1: Entrega de código (exercise_attempts.submitted_code)
- N2: Tests ejecutados (exercise_attempts.tests_*)
- N3: Interacciones con pistas (hints_used)
- N4: Feedback de IA + Decisiones cognitivas
```

### Relación con Risk Analysis

```python
# Detectar riesgo de AI_DEPENDENCY
if attempt.hints_used >= 3 and attempt.status == 'PASS':
    create_risk(
        session_id=attempt.session_id,
        dimension=RiskDimension.COGNITIVE,
        risk_type=RiskType.AI_DEPENDENCY,
        severity=RiskLevel.MEDIUM
    )
```

---

**Última actualización**: 2025-12-23
