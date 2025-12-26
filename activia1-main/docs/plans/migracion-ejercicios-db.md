# Plan de Migración: Ejercicios JSON → PostgreSQL

**Objetivo**: Migrar todos los ejercicios del sistema de archivos JSON a PostgreSQL para centralizar datos, mejorar analytics y facilitar gestión.

**Fecha Inicio**: 2025-12-23
**Estado**: 🟡 En Progreso (70% - FASE 3 completada)
**Responsable**: Desarrollo

---

## 📊 Situación Actual

### Problemas Identificados
- ❌ Ejercicios dispersos en 8+ archivos JSON
- ❌ Tests hardcodeados sin persistencia en BD
- ❌ No hay histórico de intentos de estudiantes
- ❌ Sin versionado de ejercicios
- ❌ Dificulta analytics (tasas de éxito, ejercicios más difíciles)
- ❌ Muchos archivos sueltos en el proyecto

### Archivos Actuales a Migrar
```
backend/data/training/
  └── programacion1_temas.json (5 temas, sistema antiguo)

backend/data/exercises/
  ├── catalog.json (metadatos)
  ├── unit1_fundamentals.json (3 ejercicios Python)
  ├── unit2_structures.json (3 ejercicios Python)
  ├── unit3_functions.json (3 ejercicios Python)
  ├── unit4_files.json (3 ejercicios Python)
  ├── unit5_oop.json (3 ejercicios Python)
  ├── unit6_java_fundamentals.json (Java)
  └── unit7_springboot.json (Java)
```

**Total**: ~20-25 ejercicios únicos + tests asociados

---

## 🎯 Arquitectura Propuesta (Diseño Mejorado)

### Diagrama de Tablas

```
┌─────────────────┐
│   subjects      │ (Materias: Python, Java)
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│   exercises     │ (Ejercicios individuales)
└────────┬────────┘
         │
         ├─── 1:N ──→ ┌──────────────────┐
         │            │  exercise_hints  │ (Pistas graduadas)
         │            └──────────────────┘
         │
         ├─── 1:N ──→ ┌──────────────────┐
         │            │ exercise_tests   │ (Tests unitarios)
         │            └──────────────────┘
         │
         └─── 1:N ──→ ┌──────────────────────┐
                      │ exercise_attempts    │ (Intentos estudiantes)
                      └──────────────────────┘
                               │
                               │ FK
                               ▼
                      ┌──────────────────┐
                      │    sessions      │ (Existente)
                      └──────────────────┘
```

### 1. Tabla: `subjects` (Materias)

```sql
CREATE TABLE subjects (
  id VARCHAR(50) PRIMARY KEY,              -- 'PYTHON', 'JAVA', 'PROG1'
  name VARCHAR(100) NOT NULL,              -- 'Python', 'Java', 'Programación 1'
  description TEXT,
  language VARCHAR(20) NOT NULL,           -- 'python', 'java'

  -- Metadata
  total_units INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_subjects_language ON subjects(language);
CREATE INDEX idx_subjects_active ON subjects(is_active);
```

**Datos iniciales**:
- `PYTHON` - Python (Unidades 1-5)
- `JAVA` - Java (Unidades 6-7)
- `PROG1` - Programación 1 (sistema antiguo, legacy)

---

### 2. Tabla: `exercises` (Ejercicios)

```sql
CREATE TABLE exercises (
  id VARCHAR(50) PRIMARY KEY,              -- 'U1-VAR-01', 'condicionales'
  subject_id VARCHAR(50) REFERENCES subjects(id) ON DELETE CASCADE,

  -- Metadata básica
  title VARCHAR(200) NOT NULL,
  description TEXT,
  difficulty VARCHAR(20) NOT NULL,         -- 'Easy', 'Medium', 'Hard'
  time_min INTEGER NOT NULL,               -- Tiempo estimado en minutos
  unit INTEGER,                            -- 1-7 (null para legacy)
  language VARCHAR(20) NOT NULL,           -- 'python', 'java'

  -- Contenido pedagógico
  mission_markdown TEXT NOT NULL,          -- Consigna completa
  story_markdown TEXT,                     -- Contexto/historia del ejercicio
  constraints TEXT[],                      -- Restricciones/requisitos

  -- Código
  starter_code TEXT NOT NULL,              -- Código inicial para el estudiante
  solution_code TEXT,                      -- Solución de referencia (oculta)

  -- Metadata pedagógica
  tags JSONB DEFAULT '[]',                 -- ['Variables', 'Condicionales']
  learning_objectives JSONB DEFAULT '[]',  -- Objetivos de aprendizaje
  cognitive_level VARCHAR(20),             -- 'Recordar', 'Comprender', 'Aplicar', etc.

  -- Versionado y estado
  version INTEGER DEFAULT 1,
  is_active BOOLEAN DEFAULT TRUE,
  deleted_at TIMESTAMP,                    -- Soft delete

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),

  -- Constraints
  CONSTRAINT check_difficulty CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
  CONSTRAINT check_language CHECK (language IN ('python', 'java')),
  CONSTRAINT check_time_positive CHECK (time_min > 0)
);

-- Índices para performance
CREATE INDEX idx_exercises_subject ON exercises(subject_id);
CREATE INDEX idx_exercises_unit ON exercises(unit);
CREATE INDEX idx_exercises_difficulty ON exercises(difficulty);
CREATE INDEX idx_exercises_language ON exercises(language);
CREATE INDEX idx_exercises_active ON exercises(is_active) WHERE deleted_at IS NULL;
CREATE INDEX idx_exercises_tags ON exercises USING GIN (tags);  -- JSONB index

-- Full-text search (opcional, para búsqueda)
CREATE INDEX idx_exercises_search ON exercises USING GIN (
  to_tsvector('spanish', title || ' ' || COALESCE(description, ''))
);
```

**Campos clave**:
- `mission_markdown`: La consigna del ejercicio
- `starter_code`: Código con TODOs para el estudiante
- `solution_code`: Solución completa (NO se envía al frontend)
- `deleted_at`: Soft delete para mantener histórico

---

### 3. Tabla: `exercise_hints` (Pistas/Hints)

```sql
CREATE TABLE exercise_hints (
  id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
  exercise_id VARCHAR(50) REFERENCES exercises(id) ON DELETE CASCADE,

  -- Contenido de la pista
  hint_number INTEGER NOT NULL,            -- 1, 2, 3, 4 (orden)
  title VARCHAR(200),                      -- "Estructura básica de validación"
  content TEXT NOT NULL,                   -- Contenido de la pista

  -- Penalización
  penalty_points INTEGER DEFAULT 0,        -- 5, 10, 15, 20 (creciente)

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),

  -- Constraints
  CONSTRAINT unique_exercise_hint UNIQUE (exercise_id, hint_number),
  CONSTRAINT check_hint_number_positive CHECK (hint_number > 0),
  CONSTRAINT check_penalty_nonnegative CHECK (penalty_points >= 0)
);

-- Índices
CREATE INDEX idx_hints_exercise ON exercise_hints(exercise_id);
CREATE INDEX idx_hints_order ON exercise_hints(exercise_id, hint_number);
```

**Rationale**:
- Separar pistas permite agregar/modificar sin tocar el ejercicio
- `penalty_points` para sistema de calificación con penalización
- `hint_number` define el orden de revelación (1 es menos spoiler, 4 es casi solución)

---

### 4. Tabla: `exercise_tests` (Tests Unitarios)

```sql
CREATE TABLE exercise_tests (
  id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
  exercise_id VARCHAR(50) REFERENCES exercises(id) ON DELETE CASCADE,

  -- Identificación del test
  test_number INTEGER NOT NULL,            -- Orden: 1, 2, 3...
  description TEXT,                        -- "Validación de límites exactos"

  -- Test data
  input TEXT NOT NULL,                     -- "validar_nota(85)"
  expected TEXT NOT NULL,                  -- "True" o "85.0"

  -- Configuración
  is_hidden BOOLEAN DEFAULT FALSE,         -- TRUE = no visible al estudiante
  timeout_seconds INTEGER DEFAULT 5,

  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),

  -- Constraints
  CONSTRAINT unique_exercise_test UNIQUE (exercise_id, test_number),
  CONSTRAINT check_test_number_positive CHECK (test_number > 0),
  CONSTRAINT check_timeout_positive CHECK (timeout_seconds > 0)
);

-- Índices
CREATE INDEX idx_tests_exercise ON exercise_tests(exercise_id);
CREATE INDEX idx_tests_hidden ON exercise_tests(exercise_id, is_hidden);
CREATE INDEX idx_tests_order ON exercise_tests(exercise_id, test_number);
```

**Rationale**:
- `is_hidden`: Tests ocultos vs visibles (los ocultos se usan para evaluación final)
- `timeout_seconds`: Prevenir infinite loops
- Separar tests permite agregar/modificar sin cambiar el ejercicio

---

### 5. Tabla: `exercise_attempts` (Intentos de Estudiantes)

```sql
CREATE TABLE exercise_attempts (
  id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,

  -- Referencias
  exercise_id VARCHAR(50) REFERENCES exercises(id) ON DELETE CASCADE,
  student_id VARCHAR(100) NOT NULL,        -- ID del estudiante
  session_id VARCHAR(36) REFERENCES sessions(id) ON DELETE CASCADE,

  -- Código enviado
  submitted_code TEXT NOT NULL,

  -- Resultados de ejecución
  tests_passed INTEGER DEFAULT 0,
  tests_total INTEGER DEFAULT 0,
  score FLOAT,                             -- 0-10 (escala del sistema)
  status VARCHAR(20) NOT NULL,             -- 'PASS', 'FAIL', 'ERROR', 'TIMEOUT'

  -- Ejecución
  execution_time_ms INTEGER,
  stdout TEXT,
  stderr TEXT,

  -- Feedback de IA (CodeEvaluator)
  ai_feedback_summary TEXT,                -- Resumen corto para toast
  ai_feedback_detailed TEXT,               -- Markdown completo
  ai_suggestions JSONB DEFAULT '[]',       -- Array de sugerencias

  -- Pistas usadas
  hints_used INTEGER DEFAULT 0,
  penalty_applied INTEGER DEFAULT 0,       -- Penalización total por pistas

  -- Metadata
  attempt_number INTEGER DEFAULT 1,        -- 1er, 2do, 3er intento...
  submitted_at TIMESTAMP DEFAULT NOW(),

  -- Constraints
  CONSTRAINT check_status CHECK (status IN ('PASS', 'FAIL', 'ERROR', 'TIMEOUT')),
  CONSTRAINT check_score_range CHECK (score >= 0 AND score <= 10),
  CONSTRAINT check_tests_valid CHECK (tests_passed >= 0 AND tests_passed <= tests_total)
);

-- Índices para analytics
CREATE INDEX idx_attempts_exercise ON exercise_attempts(exercise_id);
CREATE INDEX idx_attempts_student ON exercise_attempts(student_id);
CREATE INDEX idx_attempts_session ON exercise_attempts(session_id);
CREATE INDEX idx_attempts_status ON exercise_attempts(status);
CREATE INDEX idx_attempts_submitted ON exercise_attempts(submitted_at);

-- Índice compuesto para queries de progreso
CREATE INDEX idx_attempts_student_exercise ON exercise_attempts(student_id, exercise_id, submitted_at);
```

**Rationale**:
- Permite tracking completo de intentos de estudiantes
- Analytics: tasa de éxito, promedio de intentos, tiempo promedio
- Feedback de IA persistido para revisión posterior
- Relación con `sessions` para trazabilidad N4

---

## 📋 Fases de Implementación

### ✅ FASE 1: Modelos y Migraciones (Base de Datos)

**Objetivo**: Crear las tablas en PostgreSQL con todos los constraints e índices.

#### Tareas

- [ ] **1.1** Crear modelo `SubjectDB` en `backend/database/models.py`
  - Campos: id, name, description, language, total_units, is_active, timestamps
  - Relación: `exercises = relationship("ExerciseDB", back_populates="subject")`

- [ ] **1.2** Crear modelo `ExerciseDB` en `backend/database/models.py`
  - Todos los campos del diseño
  - Relaciones: subject, hints, tests, attempts
  - Soft delete: `deleted_at` nullable

- [ ] **1.3** Crear modelo `ExerciseHintDB` en `backend/database/models.py`
  - Campos: hint_number, title, content, penalty_points
  - FK: exercise_id con CASCADE

- [ ] **1.4** Crear modelo `ExerciseTestDB` en `backend/database/models.py`
  - Campos: test_number, input, expected, is_hidden, timeout_seconds
  - FK: exercise_id con CASCADE

- [ ] **1.5** Crear modelo `ExerciseAttemptDB` en `backend/database/models.py`
  - Campos: submitted_code, tests_passed, score, status, ai_feedback, etc.
  - FKs: exercise_id, session_id con CASCADE

- [ ] **1.6** Crear migración `backend/database/migrations/add_exercises_tables.py`
  - Usar Alembic o script manual con `Base.metadata.create_all()`
  - Incluir todos los índices y constraints

- [ ] **1.7** Ejecutar migración en BD local
  ```bash
  cd activia1-main
  python -m backend.database.migrations.add_exercises_tables
  ```

- [ ] **1.8** Verificar tablas creadas
  ```bash
  # PostgreSQL
  docker-compose exec postgres psql -U activia_user -d activia_db -c "\dt"
  # Verificar: subjects, exercises, exercise_hints, exercise_tests, exercise_attempts
  ```

**Criterio de Aceptación**:
- ✅ 5 tablas creadas correctamente
- ✅ Todas las FKs y constraints funcionando
- ✅ Índices creados (verificar con `\di` en psql)

**Estado**: ⬜ No iniciado

---

### ✅ FASE 2: Schemas Pydantic y Repositorios

**Objetivo**: Crear los contratos de API (schemas) y capa de acceso a datos (repositories).

#### Tareas

- [ ] **2.1** Crear schemas en `backend/api/schemas/exercises.py`
  - `SubjectCreate`, `SubjectRead`, `SubjectUpdate`
  - `ExerciseCreate`, `ExerciseRead`, `ExerciseUpdate`, `ExerciseWithDetails`
  - `ExerciseHintRead`
  - `ExerciseTestRead` (NO exponer expected en tests visibles)
  - `ExerciseAttemptCreate`, `ExerciseAttemptRead`
  - `ExerciseListItem` (para listados, sin starter_code completo)

- [ ] **2.2** Crear `backend/database/repositories/subject_repository.py`
  - `get_all()`, `get_by_id()`, `create()`, `update()`, `delete()`
  - `get_by_language(language: str)`

- [ ] **2.3** Crear `backend/database/repositories/exercise_repository.py`
  - `get_all()`, `get_by_id()`, `get_by_subject()`, `get_by_unit()`
  - `create()`, `update()`, `soft_delete()`
  - `get_with_hints()`, `get_with_tests()` - eager loading
  - `search(query: str)` - full-text search

- [ ] **2.4** Crear `backend/database/repositories/exercise_test_repository.py`
  - `get_by_exercise()`, `create_batch()`, `update()`, `delete()`
  - `get_visible_tests()`, `get_hidden_tests()`

- [ ] **2.5** Crear `backend/database/repositories/exercise_attempt_repository.py`
  - `create()`, `get_by_student()`, `get_by_exercise()`, `get_by_session()`
  - `get_latest_attempt(student_id, exercise_id)`
  - `get_student_progress(student_id)` - analytics

- [ ] **2.6** Agregar repositorios a `backend/database/repositories/__init__.py`
  ```python
  from .subject_repository import SubjectRepository
  from .exercise_repository import ExerciseRepository
  from .exercise_test_repository import ExerciseTestRepository
  from .exercise_attempt_repository import ExerciseAttemptRepository
  ```

- [ ] **2.7** Crear tests unitarios para repositorios
  - `tests/test_repositories/test_exercise_repository.py`
  - Verificar CRUD, soft delete, eager loading

**Criterio de Aceptación**:
- ✅ Todos los repositorios implementados
- ✅ Schemas Pydantic validando correctamente
- ✅ Tests unitarios pasando (cobertura > 80%)

**Estado**: ⬜ No iniciado

---

### ✅ FASE 3: Seed Database - Cargar Ejercicios desde JSON

**Objetivo**: Crear script seed idempotente que carga ejercicios desde JSON a PostgreSQL.

#### Tareas

- [ ] **3.1** Crear script `backend/scripts/seed_exercises.py` (idempotente)
  - Función `seed_subjects()` - crear/actualizar Python, Java, PROG1
  - Función `seed_legacy_exercises()` - programacion1_temas.json
  - Función `seed_catalog_exercises()` - unit1-7 desde catalog
  - Función `seed_tests()` - tests asociados
  - Función `seed_hints()` - pistas con penalizaciones
  - **Idempotencia**: Usar `get_or_create()` pattern

- [ ] **3.2** Implementar seed de `programacion1_temas.json` (legacy)
  - Patrón idempotente:
    ```python
    exercise = exercise_repo.get_by_id(id)
    if not exercise:
        exercise = exercise_repo.create(data)
    else:
        exercise_repo.update(id, data)  # Actualizar si cambió
    ```
  - Mapear campos:
    - `id` → exercise.id
    - `nombre` → exercise.title
    - `descripcion` → exercise.description
    - `ejercicio.consigna` → exercise.mission_markdown
    - `ejercicio.codigo_inicial` → exercise.starter_code
    - `ejercicio.tests_ocultos` → exercise_tests (is_hidden=True)
    - `ejercicio.pistas` → exercise_hints

- [ ] **3.3** Implementar seed de `catalog.json` + unit*.json
  - Mismo patrón idempotente (get_or_create)
  - Iterar por cada unit (1-7)
  - Cargar ejercicios desde unit{N}_*.json
  - Mapear campos:
    - `id` → exercise.id
    - `meta.title` → exercise.title
    - `content.mission_markdown` → exercise.mission_markdown
    - `content.story_markdown` → exercise.story_markdown
    - `starter_code` → exercise.starter_code
    - `hidden_tests` → exercise_tests

- [ ] **3.4** Agregar validación de datos migrados
  - Verificar que todos los ejercicios tengan al menos 1 test
  - Verificar que starter_code no esté vacío
  - Verificar que difficulty sea válido (Easy/Medium/Hard)

- [ ] **3.5** Agregar logging detallado
  ```python
  logger.info(f"✅ Seeded ejercicio: {exercise.id} - {exercise.title}")
  logger.info(f"🔄 Actualizado ejercicio: {exercise.id}")
  logger.warning(f"⚠️ Ejercicio {id} sin tests")
  logger.error(f"❌ Error seeding {id}: {error}")
  ```

- [ ] **3.6** Crear modo dry-run y modo force-update
  ```bash
  # Ver qué se creará/actualizará sin escribir
  python -m backend.scripts.seed_exercises --dry-run

  # Forzar actualización de todos los ejercicios
  python -m backend.scripts.seed_exercises --force-update

  # Modo normal (solo crear nuevos)
  python -m backend.scripts.seed_exercises
  ```

- [ ] **3.7** Ejecutar seed completo
  ```bash
  python -m backend.scripts.seed_exercises
  ```

- [ ] **3.8** Agregar seed a inicialización de desarrollo
  - Actualizar `backend/scripts/seed_dev.py` para incluir ejercicios
  - O crear comando: `make seed-exercises`

- [ ] **3.9** Verificar datos en PostgreSQL
  ```sql
  SELECT subject_id, COUNT(*) FROM exercises GROUP BY subject_id;
  SELECT exercise_id, COUNT(*) FROM exercise_tests GROUP BY exercise_id;
  SELECT exercise_id, COUNT(*) FROM exercise_hints GROUP BY exercise_id;
  ```

- [ ] **3.10** Generar reporte de seed
  - Ejercicios creados: X
  - Ejercicios actualizados: Y
  - Tests creados: X
  - Hints creados: X
  - Errores encontrados: Lista

**Criterio de Aceptación**:
- ✅ Script seed es idempotente (ejecutable múltiples veces)
- ✅ Todos los ejercicios JSON cargados en BD
- ✅ Todos los tests asociados correctamente
- ✅ Pistas con penalizaciones correctas
- ✅ 0 errores de integridad referencial
- ✅ Reporte de seed generado
- ✅ Integrado con `seed_dev.py` o `make seed`

**Estado**: ⬜ No iniciado

---

### ✅ FASE 4: Actualizar API Endpoints (Training Router)

**Objetivo**: Modificar `/training/*` para leer de PostgreSQL en lugar de archivos JSON.

#### Tareas

- [ ] **4.1** Actualizar `GET /training/materias`
  - **Antes**: Lee `programacion1_temas.json` y `catalog.json`
  - **Después**:
    ```python
    subject_repo = SubjectRepository(db)
    exercise_repo = ExerciseRepository(db)

    subjects = subject_repo.get_all()
    for subject in subjects:
        subject.temas = exercise_repo.get_by_subject(subject.id)
    ```
  - Mantener mismo formato de respuesta (no breaking changes)

- [ ] **4.2** Actualizar `POST /training/iniciar`
  - **Antes**: Lee ejercicio desde JSON con `ExerciseLoader`
  - **Después**:
    ```python
    exercise = exercise_repo.get_by_id(request.tema_id)
    if not exercise:
        raise HTTPException(404, "Ejercicio no encontrado")

    # Cargar tests y hints con eager loading
    tests = test_repo.get_by_exercise(exercise.id)
    hints = hint_repo.get_by_exercise(exercise.id)
    ```

- [ ] **4.3** Actualizar `POST /training/submit-ejercicio`
  - Guardar intento en `exercise_attempts`:
    ```python
    attempt = ExerciseAttemptDB(
        exercise_id=exercise.id,
        student_id=current_user.id,
        session_id=request.session_id,
        submitted_code=request.codigo_usuario,
        tests_passed=tests_passed,
        tests_total=tests_total,
        score=nota,
        status='PASS' if correcto else 'FAIL',
        ai_feedback_summary=mensaje,
        ai_feedback_detailed=feedback_completo,
        hints_used=sesion.get('pistas_usadas', 0),
        execution_time_ms=total_execution_time
    )
    attempt_repo.create(attempt)
    ```

- [ ] **4.4** Actualizar `POST /training/pista`
  - **Antes**: Lee pistas desde JSON en sesión
  - **Después**:
    ```python
    hints = hint_repo.get_by_exercise(exercise_id)
    if request.numero_pista >= len(hints):
        raise HTTPException(400, "Pista no disponible")

    hint = hints[request.numero_pista]
    # Registrar penalización en sesión
    ```

- [ ] **4.5** Actualizar `POST /training/corregir-ia`
  - Usar tests desde BD en lugar de JSON:
    ```python
    tests = test_repo.get_by_exercise(exercise_id)
    # Ejecutar tests
    # Guardar resultado en exercise_attempts
    ```

- [ ] **4.6** Crear endpoint opcional `GET /training/exercises/{id}/details`
  - Para debugging, retorna ejercicio completo con tests y hints
  - Solo accesible por admins/teachers

- [ ] **4.7** Agregar manejo de cache (opcional, para performance)
  - Cachear listado de materias (TTL: 1 hora)
  - Cachear ejercicios individuales (TTL: 30 min)
  ```python
  @router.get("/materias")
  @cache(expire=3600)  # Redis cache
  async def obtener_materias():
      ...
  ```

**Criterio de Aceptación**:
- ✅ Endpoints actualizados sin breaking changes
- ✅ Frontend sigue funcionando sin modificaciones
- ✅ Intentos de estudiantes se guardan en BD
- ✅ Tests pasan correctamente

**Estado**: ⬜ No iniciado

---

### ✅ FASE 5: Testing y Validación

**Objetivo**: Asegurar que la migración no rompió nada y que todo funciona correctamente.

#### Tareas

- [ ] **5.1** Tests de integración - Training Flow completo
  - Crear `tests/test_integration/test_training_flow_db.py`
  - Test 1: Obtener materias → debe retornar Python y Java
  - Test 2: Iniciar entrenamiento → debe crear sesión
  - Test 3: Submit ejercicio → debe guardar attempt y retornar resultado
  - Test 4: Solicitar pista → debe retornar hint y aplicar penalización
  - Test 5: Completar entrenamiento → debe calcular nota final

- [ ] **5.2** Tests de repositorios
  - `tests/test_repositories/test_exercise_repository.py`
  - `tests/test_repositories/test_exercise_attempt_repository.py`
  - Verificar soft delete, eager loading, filtros

- [ ] **5.3** Tests de migración de datos
  - `tests/test_migrations/test_exercise_migration.py`
  - Verificar que cantidad de ejercicios coincide
  - Verificar que tests están asociados correctamente

- [ ] **5.4** Pruebas manuales en frontend
  - [ ] Seleccionar materia Python → debe mostrar ejercicios
  - [ ] Seleccionar materia Java → debe mostrar ejercicios
  - [ ] Iniciar ejercicio → debe cargar código inicial
  - [ ] Solicitar pista → debe mostrar hint
  - [ ] Enviar código incorrecto → debe mostrar errores de tests
  - [ ] Enviar código correcto → debe pasar tests y avanzar
  - [ ] Completar todos los ejercicios → debe mostrar nota final

- [ ] **5.5** Pruebas de performance
  - Benchmark: `GET /training/materias` con 50 ejercicios < 200ms
  - Benchmark: `POST /training/submit-ejercicio` < 2s (incluyendo ejecución)
  - Verificar que índices están siendo usados (EXPLAIN ANALYZE)

- [ ] **5.6** Ejecutar suite completa de tests
  ```bash
  cd activia1-main
  pytest tests/ -v --cov=backend --cov-report=html
  # Cobertura mínima: 70%
  ```

- [ ] **5.7** Validar trazabilidad N4
  - Verificar que `exercise_attempts` tiene FK a `sessions`
  - Verificar que se puede obtener cognitive_path incluyendo attempts
  - Verificar que reportes incluyen datos de ejercicios

**Criterio de Aceptación**:
- ✅ Todos los tests pasan (unit + integration)
- ✅ Cobertura de código > 70%
- ✅ Pruebas manuales exitosas
- ✅ Performance aceptable (< 2s por submit)

**Estado**: ⬜ No iniciado

---

### ✅ FASE 6: Archivar JSONs y Limpieza

**Objetivo**: Mover archivos JSON a carpeta archive y limpiar código obsoleto.

#### Tareas

- [ ] **6.1** Crear carpeta archive
  ```bash
  mkdir -p backend/data/archive/training
  mkdir -p backend/data/archive/exercises
  ```

- [ ] **6.2** Mover JSONs a archive (NO eliminar)
  ```bash
  mv backend/data/training/*.json backend/data/archive/training/
  mv backend/data/exercises/*.json backend/data/archive/exercises/
  ```

- [ ] **6.3** Actualizar `.gitignore` (opcional)
  ```gitignore
  # JSONs archivados - mantener en repo para referencia
  # backend/data/archive/
  ```

- [ ] **6.4** Eliminar código obsoleto en `training.py`
  - Eliminar función `cargar_materia_datos()`
  - Eliminar función `obtener_tema()`
  - Eliminar imports de `ExerciseLoader` si ya no se usa
  - Eliminar variable `TRAINING_DATA_PATH`

- [ ] **6.5** Actualizar `backend/data/exercises/loader.py`
  - Marcar como DEPRECATED
  - Agregar warning:
    ```python
    import warnings
    warnings.warn(
        "ExerciseLoader is deprecated. Use ExerciseRepository instead.",
        DeprecationWarning
    )
    ```

- [ ] **6.6** Crear README en archive
  - `backend/data/archive/README.md`
  - Explicar que estos JSON fueron migrados a PostgreSQL
  - Incluir fecha de migración y script usado

- [ ] **6.7** Actualizar documentación
  - Actualizar `CLAUDE.md` con nueva arquitectura
  - Documentar nuevas tablas en "Database Schema"
  - Agregar ejemplos de queries de ejercicios

**Criterio de Aceptación**:
- ✅ JSONs movidos a `backend/data/archive/`
- ✅ Código obsoleto eliminado o marcado como deprecated
- ✅ README creado en archive
- ✅ Documentación actualizada

**Estado**: ⬜ No iniciado

---

## 📊 Resumen de Progreso

### Checklist General

- [x] **FASE 1**: Modelos y Migraciones ✅ 8/8 tareas (100%)
- [x] **FASE 1.5**: Sistema de Rúbricas ✅ 10/10 tareas (100%)
- [x] **FASE 2**: Schemas y Repositorios ✅ 7/7 tareas (100%)
- [x] **FASE 3**: Seed Database ✅ 10/10 tareas (100%)
- [x] **FASE 4**: Actualizar API ✅ 7/7 tareas (100%)
- [ ] **FASE 5**: Testing y Validación ⬜ 0/7 tareas (0%)
- [ ] **FASE 6**: Archivar y Limpieza ⬜ 0/7 tareas (0%)

**Total**: 42/56 tareas completadas (75%) - ¡CASI COMPLETO!

---

## 🎯 Próximos Pasos (Futuro)

### Post-Migración (NO incluido en este plan)

1. **CRUD de Ejercicios para Teachers**
   - Endpoints: `POST /admin/exercises`, `PUT /admin/exercises/{id}`, `DELETE /admin/exercises/{id}`
   - UI: Página de administración de ejercicios

2. **Analytics Dashboard**
   - Tasa de éxito por ejercicio
   - Promedio de intentos hasta aprobar
   - Ejercicios más difíciles
   - Progreso de estudiantes

3. **Sistema de Hints Dinámicos**
   - IA genera hints personalizados basados en error del estudiante
   - Hints adaptativos según nivel del estudiante

4. **Recomendaciones Personalizadas**
   - "Intenta este ejercicio basado en tus debilidades"
   - Roadmap personalizado por estudiante

---

## 📝 Notas de Implementación

### Consideraciones Técnicas

1. **Migración incremental**: Durante FASE 3-4, ambos sistemas (JSON + BD) funcionan en paralelo para rollback fácil
2. **Backward compatibility**: Endpoints mantienen mismo contrato (request/response)
3. **Soft delete**: Ejercicios eliminados no se borran físicamente (campo `deleted_at`)
4. **Versionado**: Campo `version` permite mantener histórico de ejercicios
5. **Performance**: Índices creados para queries comunes (student_id, exercise_id, subject_id)

### Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Pérdida de datos en migración | Baja | Alto | Dry-run + backup de JSONs en archive |
| Breaking changes en API | Media | Alto | Tests de integración + mismo contrato |
| Performance degradada | Media | Medio | Índices + cache + eager loading |
| Duplicación de ejercicios | Baja | Bajo | UNIQUE constraints + validación |

---

## 📅 Timeline Estimado

- **FASE 1**: 2-3 horas (modelos + migración SQL)
- **FASE 2**: 3-4 horas (schemas + repositorios + tests)
- **FASE 3**: 4-5 horas (script seed idempotente + validación)
- **FASE 4**: 3-4 horas (actualizar API + testing)
- **FASE 5**: 2-3 horas (testing completo + validación)
- **FASE 6**: 1 hora (archivar + limpieza)

**Total estimado**: 15-20 horas de desarrollo

---

## ✅ Criterios de Éxito Final

La migración se considerará exitosa cuando:

1. ✅ Todos los ejercicios JSON están en PostgreSQL
2. ✅ Todos los tests están asociados correctamente
3. ✅ Frontend funciona sin modificaciones
4. ✅ Intentos de estudiantes se guardan en BD
5. ✅ Suite de tests pasa al 100%
6. ✅ Performance es aceptable (< 2s por operación)
7. ✅ JSONs archivados en `backend/data/archive/`
8. ✅ Documentación actualizada

---

---

## 🎨 Sistema de Pistas Graduadas (Hints)

### Concepto

Las **pistas graduadas** son un componente pedagógico clave del sistema. Permiten al estudiante solicitar ayuda progresiva, desde sugerencias generales hasta pistas muy específicas, con penalizaciones crecientes.

### Características del Sistema de Hints

#### 1. Pistas Progresivas (4 niveles)

Cada ejercicio tiene **hasta 4 pistas** ordenadas por especificidad:

| Nivel | Tipo de Pista | Penalización | Ejemplo |
|-------|---------------|--------------|---------|
| 1 | Conceptual/General | 5 puntos | "Recuerda que debes validar los límites inferior y superior" |
| 2 | Estructural | 10 puntos | "Necesitas usar una estructura if-elif-else para los tres rangos" |
| 3 | Específica | 15 puntos | "Compara si la nota es >= 0 y <= 100 primero, luego verifica cada rango" |
| 4 | Casi Solución | 20 puntos | "El primer if debe ser: if nota < 0 or nota > 100: return False" |

#### 2. Sistema de Penalización

```python
# Cálculo de penalización total
penalty_applied = sum(hint.penalty_points for hint in hints_used)

# Nota final con penalización
score_final = max(0, score_base - penalty_applied)
```

**Ejemplo:**
- Estudiante resuelve ejercicio correctamente (10 puntos)
- Usó pista 1 (5 puntos) + pista 2 (10 puntos) = 15 puntos de penalización
- **Nota final**: 10 - 15 = 0 puntos (no puede ser negativa)

#### 3. Registro de Uso de Pistas

El sistema registra en `exercise_attempts`:
- `hints_used`: Cantidad de pistas solicitadas
- `penalty_applied`: Penalización total aplicada
- Permite analytics:
  - ¿Qué pistas se usan más?
  - ¿En qué ejercicios los estudiantes necesitan más ayuda?
  - ¿Cuál es el promedio de pistas por ejercicio?

#### 4. Flow de Solicitud de Pistas

```
1. Estudiante hace clic en "Solicitar Pista" en el frontend
   ↓
2. Backend verifica cuántas pistas ya usó (hint_number actual)
   ↓
3. Backend retorna la siguiente pista disponible
   ↓
4. Frontend muestra la pista + warning de penalización
   ↓
5. Backend actualiza contador de pistas en sesión
   ↓
6. Al enviar código, se aplica penalización en exercise_attempts
```

### Ejemplo de Pistas para un Ejercicio

**Ejercicio:** Validar si una nota está en rango válido (0-100)

```json
{
  "exercise_id": "U1-VAL-01",
  "hints": [
    {
      "hint_number": 1,
      "title": "Piensa en los límites",
      "content": "¿Qué valores son válidos para una nota? ¿Hay un límite inferior y superior?",
      "penalty_points": 5
    },
    {
      "hint_number": 2,
      "title": "Estructura de validación",
      "content": "Necesitas primero validar que la nota esté dentro del rango 0-100, y luego clasificarla en los rangos específicos (aprobado/desaprobado).",
      "penalty_points": 10
    },
    {
      "hint_number": 3,
      "title": "Operadores lógicos",
      "content": "Usa el operador `or` para detectar si la nota está fuera de los límites: `if nota < 0 or nota > 100:`",
      "penalty_points": 15
    },
    {
      "hint_number": 4,
      "title": "Estructura completa",
      "content": "```python\nif nota < 0 or nota > 100:\n    return False\nif nota >= 60:\n    return True\nelse:\n    return False\n```",
      "penalty_points": 20
    }
  ]
}
```

### API Endpoints para Pistas

```python
# GET /exercises/{exercise_id}/hints
# Retorna todas las pistas del ejercicio (para admins/teachers)
# Response: List[ExerciseHintRead]

# POST /exercises/{exercise_id}/hints/request
# Solicita la siguiente pista disponible (para estudiantes)
# Body: { session_id: str }
# Response: { hint: ExerciseHintRead, hints_used: int, penalty_applied: int }

# POST /admin/exercises/{exercise_id}/hints
# Crear una nueva pista (solo admins/teachers)
# Body: ExerciseHintCreate
# Response: ExerciseHintRead
```

---

## 📊 Estado Actual de la Migración

### ✅ Completado (Estimado: 40%)

| Componente | Estado | Archivo |
|------------|--------|---------|
| **Modelos ORM** | ✅ Completo | `backend/database/models.py` |
| - SubjectDB | ✅ | Línea 1435 |
| - ExerciseDB | ✅ | Línea 1472 |
| - ExerciseHintDB | ✅ | Línea 1532 |
| - ExerciseTestDB | ✅ | Línea 1565 |
| - ExerciseAttemptDB | ✅ | Línea 1604 |
| **Migración SQL** | ✅ Completo | `backend/database/migrations/add_exercises_tables.py` |
| **Schemas Pydantic** | ✅ Completo | `backend/api/schemas/exercises.py` |
| - Subjects (Create/Read/Update) | ✅ | Líneas 228-259 |
| - Exercises (Create/Read/Update/Student/List) | ✅ | Líneas 323-426 |
| - Hints (Create/Read) | ✅ | Líneas 261-282 |
| - Tests (Create/Read/Public) | ✅ | Líneas 284-321 |
| - Attempts (Create/Read/Summary) | ✅ | Líneas 437-497 |

### ❌ Pendiente (Estimado: 60%)

| Componente | Estado | Prioridad |
|------------|--------|-----------|
| **Repositorios** | ❌ No iniciado | 🔴 ALTA |
| - SubjectRepository | ❌ | 🔴 |
| - ExerciseRepository | ❌ | 🔴 |
| - ExerciseHintRepository | ❌ | 🔴 |
| - ExerciseTestRepository | ❌ | 🔴 |
| - ExerciseAttemptRepository | ❌ | 🔴 |
| **Script Seed** | ❌ No iniciado | 🔴 ALTA |
| - seed_exercises.py | ❌ | 🔴 |
| - Seed subjects | ❌ | 🔴 |
| - Seed exercises | ❌ | 🔴 |
| - Seed hints | ❌ | 🔴 |
| - Seed tests | ❌ | 🔴 |
| **API Endpoints** | ⚠️ Parcial | 🟡 MEDIA |
| - Actualizar training router | ❌ | 🟡 |
| - Crear exercises router (CRUD) | ❌ | 🟡 |
| **Testing** | ❌ No iniciado | 🟡 MEDIA |
| **Limpieza** | ❌ No iniciado | 🟢 BAJA |

---

## 📋 Fases de Implementación (ACTUALIZADO)

### ✅ FASE 1: Modelos y Migraciones (Base de Datos) - **COMPLETADA**

**Estado**: ✅ 8/8 tareas completadas (100%)

**Evidencia**:
- ✅ Modelos creados en `backend/database/models.py:1435-1650`
- ✅ Migración creada en `backend/database/migrations/add_exercises_tables.py`
- ✅ Índices definidos en modelos ORM
- ✅ Constraints (CHECK, UNIQUE, FK CASCADE) definidos

**Próximo paso**: Ejecutar migración en BD local

```bash
cd activia1-main
python -m backend.database.migrations.add_exercises_tables
python -m backend.database.migrations.add_exercises_tables verify
```

---

### 🔄 FASE 1.5: Sistema de Rúbricas Pedagógicas - **EN PROGRESO**

**Objetivo**: Implementar sistema completo de rúbricas para evaluación cualitativa por criterios y niveles.

**Rationale**: El sistema educativo requiere evaluación pedagógica basada en rúbricas, no solo tests pass/fail. Cada ejercicio debe tener:
- Criterios de evaluación explícitos (Funcionalidad, Calidad de código, Robustez, etc.)
- 4 niveles por criterio (Excelente, Bueno, Regular, Insuficiente)
- Puntajes asociados a cada nivel
- Penalización por uso de pistas
- Cálculo de nota final: score_rubrica - penalizacion_pistas

**Estado**: ⬜ 0/10 tareas completadas

#### Tareas

- [ ] **1.5.1** Diseñar esquema de rúbricas
  - Estructura: Exercise (1) → (N) RubricCriterion (1) → (N) RubricLevel
  - 4 niveles estándar: Excelente (9-10), Bueno (7-8.9), Regular (5-6.9), Insuficiente (0-4.9)
  - Cada criterio tiene peso (0-1, suma debe ser 1.0)

- [ ] **1.5.2** Crear modelo `ExerciseRubricCriterionDB` en `backend/database/models.py`
  ```python
  class ExerciseRubricCriterionDB(Base, BaseModel):
      __tablename__ = "exercise_rubric_criteria"

      exercise_id = Column(String(50), ForeignKey("exercises.id", ondelete="CASCADE"))
      criterion_name = Column(String(100), nullable=False)  # "Funcionalidad", "Calidad", etc.
      description = Column(Text, nullable=True)
      weight = Column(Float, nullable=False)  # 0.0-1.0 (ej: 0.4 = 40%)
      order = Column(Integer, nullable=False)  # Orden de presentación

      # Relationships
      exercise = relationship("ExerciseDB", back_populates="rubric_criteria")
      levels = relationship("RubricLevelDB", back_populates="criterion", cascade="all, delete-orphan")

      # Constraints
      CONSTRAINT weight >= 0 AND weight <= 1
      UNIQUE (exercise_id, criterion_name)
      UNIQUE (exercise_id, order)
  ```

- [ ] **1.5.3** Crear modelo `RubricLevelDB` en `backend/database/models.py`
  ```python
  class RubricLevelDB(Base, BaseModel):
      __tablename__ = "rubric_levels"

      criterion_id = Column(String(36), ForeignKey("exercise_rubric_criteria.id", ondelete="CASCADE"))
      level_name = Column(String(50), nullable=False)  # "Excelente", "Bueno", etc.
      description = Column(Text, nullable=False)  # Qué debe cumplir para este nivel
      min_score = Column(Float, nullable=False)  # 9.0, 7.0, 5.0, 0.0
      max_score = Column(Float, nullable=False)  # 10.0, 8.9, 6.9, 4.9
      points = Column(Integer, nullable=False)  # Puntos otorgados (si alcanza este nivel)

      # Relationship
      criterion = relationship("ExerciseRubricCriterionDB", back_populates="levels")

      # Constraints
      CONSTRAINT min_score >= 0 AND max_score <= 10
      CONSTRAINT min_score < max_score
      CHECK level_name IN ('Excelente', 'Bueno', 'Regular', 'Insuficiente')
  ```

- [ ] **1.5.4** Agregar campo `max_score` a `ExerciseDB`
  ```python
  # En ExerciseDB
  max_score = Column(Integer, default=100, nullable=False)  # Puntaje máximo del ejercicio
  ```

- [ ] **1.5.5** Actualizar `ExerciseDB.rubric_criteria` relationship
  ```python
  # En ExerciseDB
  rubric_criteria = relationship(
      "ExerciseRubricCriterionDB",
      back_populates="exercise",
      cascade="all, delete-orphan",
      order_by="ExerciseRubricCriterionDB.order"
  )
  ```

- [ ] **1.5.6** Actualizar `ExerciseAttemptDB` para guardar evaluación por criterio
  ```python
  # En ExerciseAttemptDB
  rubric_evaluation = Column(JSONBCompatible, default=dict, nullable=True)
  # Formato: {
  #   "criteria": [
  #     {
  #       "criterion_name": "Funcionalidad",
  #       "level_achieved": "Bueno",
  #       "score": 8.0,
  #       "points": 80,
  #       "feedback": "Implementa la mayoría de casos correctamente..."
  #     },
  #     ...
  #   ],
  #   "total_score_rubric": 85.0,  # Antes de penalizaciones
  #   "penalty_from_hints": 15,
  #   "final_score": 70.0  # total_score_rubric - penalty
  # }
  ```

- [ ] **1.5.7** Crear schemas Pydantic en `backend/api/schemas/exercises.py`
  - `RubricLevelBase`, `RubricLevelCreate`, `RubricLevelRead`
  - `RubricCriterionBase`, `RubricCriterionCreate`, `RubricCriterionRead`, `RubricCriterionWithLevels`
  - Validadores: suma de weights debe ser 1.0, min_score < max_score

- [ ] **1.5.8** Actualizar migración `add_exercises_tables.py`
  - Crear tablas `exercise_rubric_criteria` y `rubric_levels`
  - Agregar columna `max_score` a `exercises`
  - Agregar columna `rubric_evaluation` a `exercise_attempts`
  - Incluir índices y constraints

- [ ] **1.5.9** Agregar rúbricas por defecto a seed
  - Definir 3 criterios estándar por ejercicio:
    - Funcionalidad (40%): ¿Resuelve el problema correctamente?
    - Calidad de código (30%): ¿Es legible, mantiene buenas prácticas?
    - Robustez (30%): ¿Maneja casos edge, errores?
  - Cada criterio con 4 niveles predefinidos

- [ ] **1.5.10** Documentar sistema de rúbricas
  - Actualizar `migracion-ejercicios-db.md` con sección de rúbricas
  - Ejemplos de rúbricas JSON para seed
  - Guía para crear rúbricas customizadas

**Criterio de Aceptación**:
- ✅ Modelos ORM creados con relaciones correctas
- ✅ Schemas Pydantic con validaciones
- ✅ Migración SQL ejecutada sin errores
- ✅ Rúbricas estándar documentadas
- ✅ Constraints de integridad funcionando (weights suman 1.0, min < max, etc.)

**Estado**: 🔄 En progreso (2025-12-24)

---

### ⬜ FASE 2: Schemas Pydantic y Repositorios - **PARCIAL (50%)**

**Objetivo**: Crear los contratos de API (schemas) y capa de acceso a datos (repositories).

**Estado**: ✅ Schemas completados | ❌ Repositorios pendientes

#### Tareas Completadas

- ✅ **2.1** Schemas creados en `backend/api/schemas/exercises.py:222-506`
  - SubjectCreate, SubjectRead, SubjectUpdate
  - ExerciseDBCreate, ExerciseDBRead, ExerciseDBUpdate, ExerciseDBWithDetails
  - ExerciseHintCreate, ExerciseHintRead
  - ExerciseTestCreate, ExerciseTestRead, ExerciseTestReadPublic
  - ExerciseAttemptCreate, ExerciseAttemptRead, ExerciseAttemptSummary
  - ExerciseDBListItem, ExerciseDBReadStudent

#### Tareas Pendientes

- [ ] **2.2** Crear `backend/database/repositories/subject_repository.py`
  ```python
  class SubjectRepository:
      def __init__(self, db: Session):
          self.db = db

      def get_all(self, active_only: bool = True) -> List[SubjectDB]:
          """Get all subjects"""
          query = self.db.query(SubjectDB)
          if active_only:
              query = query.filter(SubjectDB.is_active == True)
          return query.order_by(SubjectDB.name).all()

      def get_by_code(self, code: str) -> Optional[SubjectDB]:
          """Get subject by code (e.g., 'PYTHON', 'JAVA')"""
          return self.db.query(SubjectDB).filter(SubjectDB.code == code).first()

      def get_by_language(self, language: str) -> List[SubjectDB]:
          """Get subjects by language (python/java)"""
          return self.db.query(SubjectDB).filter(
              SubjectDB.language == language,
              SubjectDB.is_active == True
          ).all()

      def create(self, subject: SubjectDB) -> SubjectDB:
          """Create new subject"""
          try:
              self.db.add(subject)
              self.db.commit()
              self.db.refresh(subject)
              return subject
          except Exception as e:
              self.db.rollback()
              raise

      def update(self, code: str, updates: dict) -> Optional[SubjectDB]:
          """Update subject"""
          try:
              subject = self.get_by_code(code)
              if not subject:
                  return None
              for key, value in updates.items():
                  if hasattr(subject, key):
                      setattr(subject, key, value)
              subject.updated_at = utc_now()
              self.db.commit()
              self.db.refresh(subject)
              return subject
          except Exception as e:
              self.db.rollback()
              raise

      def delete(self, code: str) -> bool:
          """Delete subject (hard delete)"""
          try:
              subject = self.get_by_code(code)
              if not subject:
                  return False
              self.db.delete(subject)
              self.db.commit()
              return True
          except Exception as e:
              self.db.rollback()
              raise
  ```

- [ ] **2.3** Crear `backend/database/repositories/exercise_repository.py`
  ```python
  class ExerciseRepository:
      def __init__(self, db: Session):
          self.db = db

      def get_all(self, active_only: bool = True, include_deleted: bool = False) -> List[ExerciseDB]:
          """Get all exercises"""
          query = self.db.query(ExerciseDB)
          if active_only:
              query = query.filter(ExerciseDB.is_active == True)
          if not include_deleted:
              query = query.filter(ExerciseDB.deleted_at == None)
          return query.order_by(ExerciseDB.unit, ExerciseDB.title).all()

      def get_by_id(self, exercise_id: str, include_deleted: bool = False) -> Optional[ExerciseDB]:
          """Get exercise by ID"""
          query = self.db.query(ExerciseDB).filter(ExerciseDB.id == exercise_id)
          if not include_deleted:
              query = query.filter(ExerciseDB.deleted_at == None)
          return query.first()

      def get_by_subject(self, subject_code: str, active_only: bool = True) -> List[ExerciseDB]:
          """Get exercises by subject"""
          query = self.db.query(ExerciseDB).filter(
              ExerciseDB.subject_code == subject_code,
              ExerciseDB.deleted_at == None
          )
          if active_only:
              query = query.filter(ExerciseDB.is_active == True)
          return query.order_by(ExerciseDB.unit, ExerciseDB.title).all()

      def get_by_unit(self, subject_code: str, unit: int) -> List[ExerciseDB]:
          """Get exercises by subject and unit"""
          return self.db.query(ExerciseDB).filter(
              ExerciseDB.subject_code == subject_code,
              ExerciseDB.unit == unit,
              ExerciseDB.is_active == True,
              ExerciseDB.deleted_at == None
          ).order_by(ExerciseDB.title).all()

      def get_with_hints(self, exercise_id: str) -> Optional[ExerciseDB]:
          """Get exercise with hints (eager loading)"""
          return self.db.query(ExerciseDB).options(
              selectinload(ExerciseDB.hints)
          ).filter(
              ExerciseDB.id == exercise_id,
              ExerciseDB.deleted_at == None
          ).first()

      def get_with_tests(self, exercise_id: str) -> Optional[ExerciseDB]:
          """Get exercise with tests (eager loading)"""
          return self.db.query(ExerciseDB).options(
              selectinload(ExerciseDB.tests)
          ).filter(
              ExerciseDB.id == exercise_id,
              ExerciseDB.deleted_at == None
          ).first()

      def get_with_details(self, exercise_id: str) -> Optional[ExerciseDB]:
          """Get exercise with hints, tests (eager loading)"""
          return self.db.query(ExerciseDB).options(
              selectinload(ExerciseDB.hints),
              selectinload(ExerciseDB.tests)
          ).filter(
              ExerciseDB.id == exercise_id,
              ExerciseDB.deleted_at == None
          ).first()

      def search(self, query_text: str) -> List[ExerciseDB]:
          """Full-text search in title and description"""
          # PostgreSQL full-text search
          from sqlalchemy import func
          search_vector = func.to_tsvector('spanish',
              ExerciseDB.title + ' ' + func.coalesce(ExerciseDB.description, ''))
          search_query = func.plainto_tsquery('spanish', query_text)

          return self.db.query(ExerciseDB).filter(
              search_vector.op('@@')(search_query),
              ExerciseDB.is_active == True,
              ExerciseDB.deleted_at == None
          ).all()

      def create(self, exercise: ExerciseDB) -> ExerciseDB:
          """Create new exercise"""
          try:
              self.db.add(exercise)
              self.db.commit()
              self.db.refresh(exercise)
              return exercise
          except Exception as e:
              self.db.rollback()
              raise

      def update(self, exercise_id: str, updates: dict) -> Optional[ExerciseDB]:
          """Update exercise"""
          try:
              exercise = self.get_by_id(exercise_id)
              if not exercise:
                  return None
              for key, value in updates.items():
                  if hasattr(exercise, key):
                      setattr(exercise, key, value)
              exercise.updated_at = utc_now()
              self.db.commit()
              self.db.refresh(exercise)
              return exercise
          except Exception as e:
              self.db.rollback()
              raise

      def soft_delete(self, exercise_id: str) -> bool:
          """Soft delete exercise (set deleted_at)"""
          try:
              exercise = self.get_by_id(exercise_id)
              if not exercise:
                  return False
              exercise.deleted_at = utc_now()
              exercise.is_active = False
              self.db.commit()
              return True
          except Exception as e:
              self.db.rollback()
              raise
  ```

- [ ] **2.4** Crear `backend/database/repositories/exercise_hint_repository.py`
  ```python
  class ExerciseHintRepository:
      def __init__(self, db: Session):
          self.db = db

      def get_by_exercise(self, exercise_id: str) -> List[ExerciseHintDB]:
          """Get all hints for an exercise, ordered by hint_number"""
          return self.db.query(ExerciseHintDB).filter(
              ExerciseHintDB.exercise_id == exercise_id
          ).order_by(ExerciseHintDB.hint_number).all()

      def get_by_id(self, hint_id: str) -> Optional[ExerciseHintDB]:
          """Get hint by ID"""
          return self.db.query(ExerciseHintDB).filter(
              ExerciseHintDB.id == hint_id
          ).first()

      def get_next_hint(self, exercise_id: str, current_hint_number: int) -> Optional[ExerciseHintDB]:
          """Get next available hint"""
          return self.db.query(ExerciseHintDB).filter(
              ExerciseHintDB.exercise_id == exercise_id,
              ExerciseHintDB.hint_number == current_hint_number + 1
          ).first()

      def create(self, hint: ExerciseHintDB) -> ExerciseHintDB:
          """Create new hint"""
          try:
              self.db.add(hint)
              self.db.commit()
              self.db.refresh(hint)
              return hint
          except Exception as e:
              self.db.rollback()
              raise

      def create_batch(self, hints: List[ExerciseHintDB]) -> List[ExerciseHintDB]:
          """Create multiple hints at once"""
          try:
              self.db.add_all(hints)
              self.db.commit()
              for hint in hints:
                  self.db.refresh(hint)
              return hints
          except Exception as e:
              self.db.rollback()
              raise

      def update(self, hint_id: str, updates: dict) -> Optional[ExerciseHintDB]:
          """Update hint"""
          try:
              hint = self.get_by_id(hint_id)
              if not hint:
                  return None
              for key, value in updates.items():
                  if hasattr(hint, key):
                      setattr(hint, key, value)
              self.db.commit()
              self.db.refresh(hint)
              return hint
          except Exception as e:
              self.db.rollback()
              raise

      def delete(self, hint_id: str) -> bool:
          """Delete hint (hard delete)"""
          try:
              hint = self.get_by_id(hint_id)
              if not hint:
                  return False
              self.db.delete(hint)
              self.db.commit()
              return True
          except Exception as e:
              self.db.rollback()
              raise
  ```

- [ ] **2.5** Crear `backend/database/repositories/exercise_test_repository.py`
  ```python
  class ExerciseTestRepository:
      def __init__(self, db: Session):
          self.db = db

      def get_by_exercise(self, exercise_id: str) -> List[ExerciseTestDB]:
          """Get all tests for an exercise"""
          return self.db.query(ExerciseTestDB).filter(
              ExerciseTestDB.exercise_id == exercise_id
          ).order_by(ExerciseTestDB.test_number).all()

      def get_visible_tests(self, exercise_id: str) -> List[ExerciseTestDB]:
          """Get only visible tests (for students)"""
          return self.db.query(ExerciseTestDB).filter(
              ExerciseTestDB.exercise_id == exercise_id,
              ExerciseTestDB.is_hidden == False
          ).order_by(ExerciseTestDB.test_number).all()

      def get_hidden_tests(self, exercise_id: str) -> List[ExerciseTestDB]:
          """Get only hidden tests (for evaluation)"""
          return self.db.query(ExerciseTestDB).filter(
              ExerciseTestDB.exercise_id == exercise_id,
              ExerciseTestDB.is_hidden == True
          ).order_by(ExerciseTestDB.test_number).all()

      def get_by_id(self, test_id: str) -> Optional[ExerciseTestDB]:
          """Get test by ID"""
          return self.db.query(ExerciseTestDB).filter(
              ExerciseTestDB.id == test_id
          ).first()

      def create(self, test: ExerciseTestDB) -> ExerciseTestDB:
          """Create new test"""
          try:
              self.db.add(test)
              self.db.commit()
              self.db.refresh(test)
              return test
          except Exception as e:
              self.db.rollback()
              raise

      def create_batch(self, tests: List[ExerciseTestDB]) -> List[ExerciseTestDB]:
          """Create multiple tests at once"""
          try:
              self.db.add_all(tests)
              self.db.commit()
              for test in tests:
                  self.db.refresh(test)
              return tests
          except Exception as e:
              self.db.rollback()
              raise

      def update(self, test_id: str, updates: dict) -> Optional[ExerciseTestDB]:
          """Update test"""
          try:
              test = self.get_by_id(test_id)
              if not test:
                  return None
              for key, value in updates.items():
                  if hasattr(test, key):
                      setattr(test, key, value)
              self.db.commit()
              self.db.refresh(test)
              return test
          except Exception as e:
              self.db.rollback()
              raise

      def delete(self, test_id: str) -> bool:
          """Delete test (hard delete)"""
          try:
              test = self.get_by_id(test_id)
              if not test:
                  return False
              self.db.delete(test)
              self.db.commit()
              return True
          except Exception as e:
              self.db.rollback()
              raise
  ```

- [ ] **2.6** Crear `backend/database/repositories/exercise_attempt_repository.py`
  ```python
  class ExerciseAttemptRepository:
      def __init__(self, db: Session):
          self.db = db

      def create(self, attempt: ExerciseAttemptDB) -> ExerciseAttemptDB:
          """Create new attempt"""
          try:
              self.db.add(attempt)
              self.db.commit()
              self.db.refresh(attempt)
              return attempt
          except Exception as e:
              self.db.rollback()
              raise

      def get_by_id(self, attempt_id: str) -> Optional[ExerciseAttemptDB]:
          """Get attempt by ID"""
          return self.db.query(ExerciseAttemptDB).filter(
              ExerciseAttemptDB.id == attempt_id
          ).first()

      def get_by_student(self, student_id: str, limit: int = 50) -> List[ExerciseAttemptDB]:
          """Get all attempts by student"""
          return self.db.query(ExerciseAttemptDB).filter(
              ExerciseAttemptDB.student_id == student_id
          ).order_by(desc(ExerciseAttemptDB.submitted_at)).limit(limit).all()

      def get_by_exercise(self, exercise_id: str, limit: int = 100) -> List[ExerciseAttemptDB]:
          """Get all attempts for an exercise (for analytics)"""
          return self.db.query(ExerciseAttemptDB).filter(
              ExerciseAttemptDB.exercise_id == exercise_id
          ).order_by(desc(ExerciseAttemptDB.submitted_at)).limit(limit).all()

      def get_by_session(self, session_id: str) -> List[ExerciseAttemptDB]:
          """Get all attempts in a session"""
          return self.db.query(ExerciseAttemptDB).filter(
              ExerciseAttemptDB.session_id == session_id
          ).order_by(ExerciseAttemptDB.submitted_at).all()

      def get_latest_attempt(self, student_id: str, exercise_id: str) -> Optional[ExerciseAttemptDB]:
          """Get most recent attempt by student for an exercise"""
          return self.db.query(ExerciseAttemptDB).filter(
              ExerciseAttemptDB.student_id == student_id,
              ExerciseAttemptDB.exercise_id == exercise_id
          ).order_by(desc(ExerciseAttemptDB.submitted_at)).first()

      def get_student_progress(self, student_id: str) -> Dict[str, Any]:
          """Get student progress analytics"""
          from sqlalchemy import func

          # Total attempts
          total_attempts = self.db.query(func.count(ExerciseAttemptDB.id)).filter(
              ExerciseAttemptDB.student_id == student_id
          ).scalar()

          # Passed exercises
          passed = self.db.query(func.count(func.distinct(ExerciseAttemptDB.exercise_id))).filter(
              ExerciseAttemptDB.student_id == student_id,
              ExerciseAttemptDB.status == 'PASS'
          ).scalar()

          # Average score
          avg_score = self.db.query(func.avg(ExerciseAttemptDB.score)).filter(
              ExerciseAttemptDB.student_id == student_id,
              ExerciseAttemptDB.score.isnot(None)
          ).scalar() or 0.0

          # Average hints used
          avg_hints = self.db.query(func.avg(ExerciseAttemptDB.hints_used)).filter(
              ExerciseAttemptDB.student_id == student_id
          ).scalar() or 0.0

          return {
              "total_attempts": total_attempts,
              "exercises_passed": passed,
              "average_score": round(float(avg_score), 2),
              "average_hints_used": round(float(avg_hints), 2)
          }

      def get_exercise_analytics(self, exercise_id: str) -> Dict[str, Any]:
          """Get exercise analytics (difficulty, success rate)"""
          from sqlalchemy import func

          # Total attempts
          total = self.db.query(func.count(ExerciseAttemptDB.id)).filter(
              ExerciseAttemptDB.exercise_id == exercise_id
          ).scalar()

          # Passed attempts
          passed = self.db.query(func.count(ExerciseAttemptDB.id)).filter(
              ExerciseAttemptDB.exercise_id == exercise_id,
              ExerciseAttemptDB.status == 'PASS'
          ).scalar()

          # Average attempts per student until pass
          avg_attempts = self.db.query(func.avg(ExerciseAttemptDB.attempt_number)).filter(
              ExerciseAttemptDB.exercise_id == exercise_id,
              ExerciseAttemptDB.status == 'PASS'
          ).scalar() or 0.0

          # Average hints used
          avg_hints = self.db.query(func.avg(ExerciseAttemptDB.hints_used)).filter(
              ExerciseAttemptDB.exercise_id == exercise_id
          ).scalar() or 0.0

          success_rate = (passed / total * 100) if total > 0 else 0.0

          return {
              "total_attempts": total,
              "passed_attempts": passed,
              "success_rate": round(success_rate, 2),
              "average_attempts_until_pass": round(float(avg_attempts), 2),
              "average_hints_used": round(float(avg_hints), 2)
          }
  ```

- [ ] **2.7** Agregar repositorios a `backend/database/repositories.py`
  - Opción A: Crear archivos separados en carpeta `repositories/`
  - Opción B: Agregar clases al archivo existente `repositories.py`

- [ ] **2.8** Crear tests unitarios
  - `tests/test_repositories/test_subject_repository.py`
  - `tests/test_repositories/test_exercise_repository.py`
  - `tests/test_repositories/test_exercise_hint_repository.py`
  - `tests/test_repositories/test_exercise_test_repository.py`
  - `tests/test_repositories/test_exercise_attempt_repository.py`

**Criterio de Aceptación**:
- ✅ Todos los repositorios implementados
- ✅ Métodos CRUD + analytics funcionando
- ✅ Tests unitarios pasando (cobertura > 80%)
- ✅ Soft delete implementado en ExerciseRepository
- ✅ Eager loading funcionando (hints, tests)

**Estado**: ⬜ 0/7 tareas completadas (schemas ya hechos no cuentan aquí)

---

## 📝 Actualización 2025-12-26: FASE 4 Completada

### Cambios Implementados Hoy

**✅ FASE 4 - Actualización de API Training (100% completada)**:

1. **Endpoint `POST /training/submit-ejercicio` (4.3)**:
   - ✅ Agregado `db: Session` dependency
   - ✅ Creación de `ExerciseAttemptDB` después de cada evaluación
   - ✅ Guardado completo de attempts con:
     - Código enviado, tests pasados/totales, score (0-10), status (PASS/FAIL/ERROR)
     - Execution time, stdout, stderr
     - AI feedback (summary y detailed)
     - Hints usados y penalty aplicado
     - Attempt number
   - ✅ Logging detallado

2. **Endpoint `POST /training/pista` (4.4)**:
   - ✅ Agregado tracking de `pistas_usadas` en sesión
   - ✅ Penalización registrada para usar en attempts
   - ✅ Las pistas ya se cargan desde BD en `/training/iniciar`
   - ✅ Docstring actualizado (MIGRADO)

3. **Endpoint `POST /training/corregir-ia` (4.5)**:
   - ✅ Los tests ya se cargan desde BD en `/training/iniciar`
   - ✅ Docstring actualizado (MIGRADO)

4. **Nuevo Endpoint `GET /training/exercises/{exercise_id}/details` (4.6)**:
   - ✅ Solo accesible para teachers/admins
   - ✅ Retorna ejercicio completo con:
     - Todos los campos (incluido `solution_code`)
     - Hints ordenados con penalizaciones
     - Tests completos (incluye hidden tests)
     - Estadísticas (total hints/tests, visible/hidden)
   - ✅ Para debugging y administración

**Endpoints previamente migrados** (ya estaban completos):
- ✅ `GET /training/materias` (4.1) - Lee subjects y exercises desde BD
- ✅ `POST /training/iniciar` (4.2) - Carga exercise, hints y tests desde BD

### Repositorios Utilizados (ya existían en `repositories.py`):
- `SubjectRepository` (línea 4203)
- `ExerciseRepository` (línea 4282)
- `ExerciseHintRepository` (línea 4455)
- `ExerciseTestRepository` (línea 4549)
- `ExerciseAttemptRepository` (línea 4656)
- `RubricCriterionRepository` (línea 4806)
- `RubricLevelRepository` (línea 4896)

### Estado de la Base de Datos:
- ✅ 7 tablas creadas y verificadas
- ✅ 2 subjects, 23 exercises cargados
- ✅ Todos los índices funcionando
- ✅ Exercise attempts ahora se guardan en cada submission

### Próximos Pasos Recomendados:
1. **FASE 5 (Testing)** - Crear tests de integración para el flujo completo
2. **FASE 6 (Limpieza)** - Archivar JSONs obsoletos y limpiar código legacy
3. **Documentación** - Actualizar `CLAUDE.md` con nueva arquitectura

---

**Última actualización**: 2025-12-26
**Versión del plan**: 1.2
