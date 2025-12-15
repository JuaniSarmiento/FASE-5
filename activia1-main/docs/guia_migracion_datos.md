# 🔄 Guía de Migración de Datos - AI-Native MVP

## Manual Completo para Migrar Datos desde Sistemas Legacy

Esta guía te ayudará a migrar datos desde sistemas educativos existentes (Moodle, Canvas, GitHub Classroom, etc.) hacia el **Ecosistema AI-Native**, preservando la integridad, trazabilidad y continuidad del proceso de aprendizaje.

---

## 📚 Índice

1. [Introducción](#introducción)
2. [Escenarios de Migración](#escenarios-de-migración)
3. [Pre-Migración: Análisis y Planificación](#pre-migración-análisis-y-planificación)
4. [Migración desde Moodle](#migración-desde-moodle)
5. [Migración desde GitHub Classroom](#migración-desde-github-classroom)
6. [Migración desde Canvas LMS](#migración-desde-canvas-lms)
7. [Migración desde Sistemas Propietarios](#migración-desde-sistemas-propietarios)
8. [Migración de Usuarios (LDAP/AD)](#migración-de-usuarios-ldapad)
9. [Validación Post-Migración](#validación-post-migración)
10. [Rollback y Contingencia](#rollback-y-contingencia)
11. [Casos de Estudio](#casos-de-estudio)
12. [Troubleshooting](#troubleshooting)

---

## Introducción

### ¿Por qué Migrar?

El **Ecosistema AI-Native** ofrece capacidades que los LMS tradicionales no tienen:

- ✅ **Trazabilidad N4 cognitiva** (no solo N1 superficial)
- ✅ **Evaluación de procesos** (no solo productos)
- ✅ **Detección automática de riesgos** (delegación, plagio, vulnerabilidades)
- ✅ **Gobernanza institucional** de IA generativa

### Datos que se Pueden Migrar

| Tipo de Dato | Moodle | GitHub | Canvas | AI-Native |
|--------------|--------|--------|--------|-----------|
| **Usuarios** | ✅ | ✅ | ✅ | ✅ |
| **Actividades/Tareas** | ✅ | ✅ | ✅ | ✅ |
| **Entregas/Submissions** | ✅ | ✅ | ✅ | ✅ (Sesiones) |
| **Calificaciones** | ✅ | ❌ | ✅ | ✅ (Evaluaciones) |
| **Retroalimentación** | ✅ | ✅ | ✅ | ✅ (Trazas) |
| **Commits Git** | ❌ | ✅ | ❌ | ✅ (Trazas N2) |
| **Logs de Interacción** | ⚠️ | ❌ | ⚠️ | ✅ (Trazas N3/N4) |

**Leyenda**:
- ✅ = Migración completa
- ⚠️ = Migración parcial
- ❌ = No disponible en origen

### Principios de Migración

1. **No destructivo**: Los sistemas legacy NO se eliminan hasta confirmar migración exitosa
2. **Incremental**: Migrar curso por curso, no todo de golpe
3. **Reversible**: Mantener plan de rollback
4. **Validado**: Verificar integridad de datos post-migración
5. **Documentado**: Registrar cada paso para auditoría

---

## Escenarios de Migración

### Escenario 1: Migración Completa (Greenfield)

**Situación**: Institución nueva o sin sistema previo.

**Estrategia**: Instalación desde cero.

```bash
# No requiere migración
python scripts/init_database.py
python scripts/import_users.py users.csv
```

### Escenario 2: Migración Paralela (Coexistencia)

**Situación**: Institución con Moodle existente, quiere probar AI-Native en paralelo.

**Estrategia**:
1. Mantener Moodle operativo
2. Integrar AI-Native vía LTI 1.3
3. Migrar solo cursos piloto
4. Sincronización bidireccional (opcional)

```
Moodle (sistema principal)
    ↕ LTI 1.3
AI-Native (piloto en 2-3 cursos)
```

### Escenario 3: Reemplazo Gradual (Phased Migration)

**Situación**: Institución quiere reemplazar Moodle gradualmente.

**Estrategia** (por semestre):
- Semestre 1: Migrar 2 cursos piloto
- Semestre 2: Migrar 10 cursos adicionales
- Semestre 3: Migrar todos los cursos de programación
- Semestre 4: Deprecar Moodle para programación

### Escenario 4: Migración de Archivos Históricos

**Situación**: Migrar datos de cursos finalizados para investigación/auditoría.

**Estrategia**: Exportar datos históricos a formato AI-Native sin afectar operaciones actuales.

---

## Pre-Migración: Análisis y Planificación

### Paso 1: Inventario de Datos

**Ejecutar script de análisis**:

```bash
python scripts/analyze_legacy_system.py --source moodle --database moodle_db
```

**Output esperado**:

```
========================================
ANÁLISIS DE SISTEMA LEGACY: MOODLE
========================================

USUARIOS:
- Estudiantes: 1,245
- Docentes: 38
- Administradores: 5
Total: 1,288

CURSOS:
- Activos: 42
- Archivados: 128
Total: 170

ACTIVIDADES (por tipo):
- Tareas (assignments): 1,847
- Foros: 432
- Quizzes: 289
- Archivos: 3,201

ENTREGAS:
- Submissions totales: 12,456
- Con calificación: 11,023 (88%)
- Sin calificar: 1,433 (12%)

TAMAÑO DE DATOS:
- Base de datos: 4.2 GB
- Archivos adjuntos: 38.7 GB
- Total: 42.9 GB

ESTIMACIÓN DE MIGRACIÓN:
- Tiempo estimado: 6-8 horas
- Espacio requerido: 45 GB (10% buffer)
```

### Paso 2: Mapeo de Entidades

**Moodle → AI-Native**:

| Moodle Entity | AI-Native Entity | Mapeo |
|---------------|------------------|-------|
| `mdl_user` | `users` | Directo (email, name, role) |
| `mdl_course` | `activities` (parcial) | 1 curso = N actividades |
| `mdl_assign` | `activities` | 1 assignment = 1 activity |
| `mdl_assign_submission` | `sessions` | 1 submission = 1 session |
| `mdl_assign_grades` | `evaluations` | Directo |
| `mdl_logstore_standard_log` | `cognitive_traces` (N3) | Parcial |

**GitHub Classroom → AI-Native**:

| GitHub Entity | AI-Native Entity | Mapeo |
|---------------|------------------|-------|
| Organization members | `users` | Directo |
| Assignments | `activities` | Directo |
| Student repos | `sessions` | 1 repo = 1 session |
| Commits | `cognitive_traces` (N2) | 1 commit = 1 trace |
| Pull requests | `cognitive_traces` (N3) | 1 PR = 1 trace |

### Paso 3: Plan de Migración

**Documento de planificación**:

```markdown
# Plan de Migración - Programación 2

## Información General
- Curso: Programación 2 (Sistemas)
- Semestre: 2/2025
- Estudiantes: 87
- Docentes: 2
- Fecha planificada: 2025-12-15 a 2025-12-16

## Datos a Migrar
1. ✅ Usuarios (87 estudiantes + 2 docentes)
2. ✅ 8 actividades (TPs 1-8)
3. ✅ 696 submissions (87 * 8)
4. ⚠️ Logs de Moodle (mapeo parcial a N3)
5. ❌ Foros (no migrar, mantener en Moodle como referencia)

## Fases
### Fase 1: Pre-Migración (Viernes 13/12, 18:00-20:00)
- Backup completo de Moodle
- Exportar datos a CSV
- Validar integridad

### Fase 2: Migración (Sábado 14/12, 08:00-16:00)
- Importar usuarios
- Importar actividades
- Importar submissions → sessions
- Validación automática

### Fase 3: Validación (Domingo 15/12, 10:00-14:00)
- Verificación manual (docentes)
- Corrección de inconsistencias
- Go/No-Go decision

### Fase 4: Rollback (si falla)
- Restaurar Moodle desde backup
- Documentar problemas

## Criterios de Éxito
- [ ] 100% de usuarios migrados correctamente
- [ ] 100% de actividades recreadas
- [ ] >95% de submissions mapeadas a sessions
- [ ] 0 errores críticos en validación

## Responsables
- Administrador: Juan Pérez (admin@inst.edu.ar)
- Docente: María García (prof@inst.edu.ar)
- Soporte técnico: 24/7 durante migración
```

---

## Migración desde Moodle

### Paso 1: Backup de Moodle

```bash
# Backup de base de datos
mysqldump -u moodle_user -p moodle_db > moodle_backup_$(date +%Y%m%d).sql

# Backup de archivos
tar -czf moodledata_backup_$(date +%Y%m%d).tar.gz /var/moodledata/
```

### Paso 2: Exportar Datos de Moodle

**Script SQL para exportar usuarios**:

```sql
-- export_moodle_users.sql
SELECT
    u.id AS moodle_id,
    u.email,
    CONCAT(u.firstname, ' ', u.lastname) AS name,
    CASE
        WHEN u.username LIKE 'student%' THEN 'STUDENT'
        WHEN EXISTS (
            SELECT 1 FROM mdl_role_assignments ra
            WHERE ra.userid = u.id AND ra.roleid = 3
        ) THEN 'TEACHER'
        ELSE 'STUDENT'
    END AS role,
    u.username AS student_id,
    FROM_UNIXTIME(u.timecreated) AS created_at
FROM mdl_user u
WHERE u.deleted = 0
  AND u.suspended = 0
  AND u.email != 'admin@example.com'
INTO OUTFILE '/tmp/moodle_users.csv'
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

**Script SQL para exportar actividades**:

```sql
-- export_moodle_assignments.sql
SELECT
    a.id AS moodle_assignment_id,
    c.shortname AS course_code,
    a.name AS title,
    a.intro AS description,
    FROM_UNIXTIME(a.timemodified) AS modified_at,
    FROM_UNIXTIME(a.duedate) AS due_date,
    a.grade AS max_grade
FROM mdl_assign a
JOIN mdl_course c ON a.course = c.id
WHERE c.shortname IN ('PROG2-2025', 'ALG-2025')
INTO OUTFILE '/tmp/moodle_assignments.csv'
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

**Script SQL para exportar submissions**:

```sql
-- export_moodle_submissions.sql
SELECT
    s.id AS submission_id,
    s.assignment AS assignment_id,
    s.userid AS moodle_user_id,
    u.email AS student_email,
    s.status,
    FROM_UNIXTIME(s.timecreated) AS created_at,
    FROM_UNIXTIME(s.timemodified) AS modified_at,
    g.grade,
    g.grader AS grader_id,
    FROM_UNIXTIME(g.timemodified) AS graded_at
FROM mdl_assign_submission s
JOIN mdl_user u ON s.userid = u.id
LEFT JOIN mdl_assign_grades g ON g.assignment = s.assignment AND g.userid = s.userid
WHERE s.status != 'new'
ORDER BY s.assignment, s.userid
INTO OUTFILE '/tmp/moodle_submissions.csv'
FIELDS TERMINATED BY ',' ENCLOSED BY '"'
LINES TERMINATED BY '\n';
```

### Paso 3: Importar a AI-Native

**Script de importación**:

```python
# scripts/migrate_from_moodle.py

import csv
import sys
from datetime import datetime
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import (
    UserRepository, ActivityRepository, SessionRepository, EvaluationRepository
)
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def migrate_users(csv_path):
    """Migrar usuarios desde CSV de Moodle"""
    with get_db_session() as db:
        user_repo = UserRepository(db)
        migrated = 0
        errors = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # Generar contraseña temporal
                    temp_password = secrets.token_urlsafe(12)

                    user = user_repo.create(
                        email=row['email'],
                        name=row['name'],
                        role=row['role'],
                        student_id=row.get('student_id'),
                        hashed_password=pwd_context.hash(temp_password),
                        metadata={
                            'moodle_id': row['moodle_id'],
                            'migrated_from': 'moodle',
                            'migrated_at': datetime.now().isoformat(),
                            'temp_password': temp_password  # Enviar por email
                        }
                    )

                    migrated += 1
                    print(f"✓ Usuario migrado: {row['email']} (password: {temp_password})")

                except Exception as e:
                    errors.append(f"Error en {row['email']}: {str(e)}")

        print(f"\n✅ Usuarios migrados: {migrated}")
        if errors:
            print(f"⚠️ Errores: {len(errors)}")
            for error in errors:
                print(f"  - {error}")

        return migrated, errors


def migrate_activities(csv_path, teacher_id):
    """Migrar actividades desde CSV de Moodle"""
    with get_db_session() as db:
        activity_repo = ActivityRepository(db)
        migrated = 0
        errors = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    activity = activity_repo.create(
                        activity_id=f"moodle_{row['moodle_assignment_id']}",
                        title=row['title'],
                        description=row['description'],
                        teacher_id=teacher_id,
                        subject=row['course_code'],
                        difficulty='INTERMEDIO',  # Ajustar manualmente después
                        policies={
                            'max_help_level': 'MEDIO',
                            'block_complete_solutions': True,
                            'require_justification': True,
                        },
                        metadata={
                            'moodle_id': row['moodle_assignment_id'],
                            'migrated_from': 'moodle',
                            'due_date': row.get('due_date'),
                            'max_grade': row.get('max_grade')
                        }
                    )

                    migrated += 1
                    print(f"✓ Actividad migrada: {row['title']}")

                except Exception as e:
                    errors.append(f"Error en {row['title']}: {str(e)}")

        print(f"\n✅ Actividades migradas: {migrated}")
        if errors:
            print(f"⚠️ Errores: {len(errors)}")

        return migrated, errors


def migrate_submissions(csv_path):
    """Migrar submissions como sessions en AI-Native"""
    with get_db_session() as db:
        session_repo = SessionRepository(db)
        eval_repo = EvaluationRepository(db)
        migrated = 0
        errors = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    # Crear sesión
                    session = session_repo.create(
                        student_id=row['student_email'],
                        activity_id=f"moodle_{row['assignment_id']}",
                        mode='LEGACY_IMPORT',
                        metadata={
                            'moodle_submission_id': row['submission_id'],
                            'migrated_from': 'moodle',
                            'original_status': row['status'],
                            'original_created_at': row['created_at']
                        }
                    )

                    # Finalizar sesión inmediatamente (es dato histórico)
                    session_repo.end_session(session.id)

                    # Si tiene calificación, crear evaluación
                    if row.get('grade'):
                        eval_repo.create(
                            session_id=session.id,
                            student_id=row['student_email'],
                            activity_id=f"moodle_{row['assignment_id']}",
                            overall_score=float(row['grade']) / 10.0,  # Normalizar a 0-10
                            overall_competency_level='MIGRATED',
                            metadata={
                                'moodle_grader_id': row.get('grader_id'),
                                'graded_at': row.get('graded_at'),
                                'migrated_from': 'moodle'
                            }
                        )

                    migrated += 1
                    print(f"✓ Submission migrada: {row['student_email']} → {row['assignment_id']}")

                except Exception as e:
                    errors.append(f"Error en submission {row['submission_id']}: {str(e)}")

        print(f"\n✅ Submissions migradas: {migrated}")
        if errors:
            print(f"⚠️ Errores: {len(errors)}")

        return migrated, errors


def main():
    print("=" * 60)
    print("MIGRACIÓN DESDE MOODLE A AI-NATIVE")
    print("=" * 60)

    # Fase 1: Usuarios
    print("\n[1/3] Migrando usuarios...")
    users_migrated, users_errors = migrate_users('/tmp/moodle_users.csv')

    # Fase 2: Actividades
    print("\n[2/3] Migrando actividades...")
    activities_migrated, activities_errors = migrate_activities(
        '/tmp/moodle_assignments.csv',
        teacher_id='teacher_001'  # Ajustar según tu caso
    )

    # Fase 3: Submissions
    print("\n[3/3] Migrando submissions...")
    submissions_migrated, submissions_errors = migrate_submissions('/tmp/moodle_submissions.csv')

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE MIGRACIÓN")
    print("=" * 60)
    print(f"✅ Usuarios migrados: {users_migrated}")
    print(f"✅ Actividades migradas: {activities_migrated}")
    print(f"✅ Submissions migradas: {submissions_migrated}")

    total_errors = len(users_errors) + len(activities_errors) + len(submissions_errors)
    if total_errors > 0:
        print(f"\n⚠️ Total de errores: {total_errors}")
        print("Ver detalles arriba.")
    else:
        print("\n🎉 Migración completada SIN errores!")


if __name__ == "__main__":
    main()
```

### Paso 4: Ejecutar Migración

```bash
# 1. Exportar datos de Moodle
mysql -u moodle_user -p moodle_db < export_moodle_users.sql
mysql -u moodle_user -p moodle_db < export_moodle_assignments.sql
mysql -u moodle_user -p moodle_db < export_moodle_submissions.sql

# 2. Copiar CSVs al servidor AI-Native
scp /tmp/moodle_*.csv user@ai-native-server:/tmp/

# 3. Ejecutar script de migración
python scripts/migrate_from_moodle.py

# Output esperado:
# ============================================================
# MIGRACIÓN DESDE MOODLE A AI-NATIVE
# ============================================================
#
# [1/3] Migrando usuarios...
# ✓ Usuario migrado: estudiante001@inst.edu.ar (password: xYz123...)
# ...
# ✅ Usuarios migrados: 89
#
# [2/3] Migrando actividades...
# ✓ Actividad migrada: TP1 - Colas Circulares
# ...
# ✅ Actividades migradas: 8
#
# [3/3] Migrando submissions...
# ✓ Submission migrada: estudiante001@inst.edu.ar → moodle_42
# ...
# ✅ Submissions migradas: 696
#
# ============================================================
# RESUMEN DE MIGRACIÓN
# ============================================================
# ✅ Usuarios migrados: 89
# ✅ Actividades migradas: 8
# ✅ Submissions migradas: 696
#
# 🎉 Migración completada SIN errores!
```

---

## Migración desde GitHub Classroom

### Paso 1: Obtener Datos vía GitHub API

```python
# scripts/migrate_from_github.py

import os
import requests
from datetime import datetime
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import (
    UserRepository, ActivityRepository, SessionRepository, TraceRepository
)

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
ORG_NAME = 'tu-organizacion-classroom'

headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def get_organization_members():
    """Obtener miembros de la organización"""
    url = f'https://api.github.com/orgs/{ORG_NAME}/members'
    response = requests.get(url, headers=headers)
    return response.json()


def get_repositories():
    """Obtener repositorios de asignaciones"""
    url = f'https://api.github.com/orgs/{ORG_NAME}/repos'
    response = requests.get(url, headers=headers)
    return response.json()


def get_commits(repo_name):
    """Obtener commits de un repositorio"""
    url = f'https://api.github.com/repos/{ORG_NAME}/{repo_name}/commits'
    response = requests.get(url, headers=headers)
    return response.json()


def migrate_users():
    """Migrar usuarios desde GitHub"""
    members = get_organization_members()

    with get_db_session() as db:
        user_repo = UserRepository(db)
        migrated = 0

        for member in members:
            # Obtener detalles del usuario
            user_url = member['url']
            user_data = requests.get(user_url, headers=headers).json()

            try:
                user = user_repo.create(
                    email=user_data.get('email') or f"{member['login']}@github.com",
                    name=user_data.get('name') or member['login'],
                    role='STUDENT',
                    student_id=member['login'],
                    metadata={
                        'github_id': member['id'],
                        'github_username': member['login'],
                        'migrated_from': 'github'
                    }
                )

                migrated += 1
                print(f"✓ Usuario migrado: {member['login']}")

            except Exception as e:
                print(f"✗ Error en {member['login']}: {e}")

        print(f"\n✅ Usuarios migrados: {migrated}")


def migrate_assignments():
    """Migrar repositorios como actividades"""
    repos = get_repositories()

    # Filtrar solo repos de asignaciones (ej: prefix "tp1-", "tp2-", etc.)
    assignment_repos = [r for r in repos if r['name'].startswith('tp')]

    # Agrupar por asignación base (sin sufijo de estudiante)
    assignments = {}
    for repo in assignment_repos:
        # ej: "tp1-colas-estudiante123" → base: "tp1-colas"
        parts = repo['name'].rsplit('-', 1)
        if len(parts) == 2:
            base_name = parts[0]
            if base_name not in assignments:
                assignments[base_name] = repo

    with get_db_session() as db:
        activity_repo = ActivityRepository(db)
        migrated = 0

        for base_name, repo in assignments.items():
            try:
                activity = activity_repo.create(
                    activity_id=f"github_{base_name}",
                    title=repo['name'].replace('-', ' ').title(),
                    description=repo['description'] or 'Migrado desde GitHub Classroom',
                    teacher_id='teacher_001',  # Ajustar
                    subject='Programación',
                    difficulty='INTERMEDIO',
                    metadata={
                        'github_repo': repo['full_name'],
                        'migrated_from': 'github'
                    }
                )

                migrated += 1
                print(f"✓ Actividad migrada: {base_name}")

            except Exception as e:
                print(f"✗ Error en {base_name}: {e}")

        print(f"\n✅ Actividades migradas: {migrated}")


def migrate_commits_as_traces():
    """Migrar commits como trazas N2"""
    repos = get_repositories()
    student_repos = [r for r in repos if r['name'].startswith('tp')]

    with get_db_session() as db:
        session_repo = SessionRepository(db)
        trace_repo = TraceRepository(db)
        migrated_sessions = 0
        migrated_traces = 0

        for repo in student_repos:
            # Extraer: tp1-colas-estudiante123 → activity: "github_tp1-colas", student: "estudiante123"
            parts = repo['name'].rsplit('-', 1)
            if len(parts) != 2:
                continue

            activity_id = f"github_{parts[0]}"
            student_id = parts[1]

            try:
                # Crear sesión
                session = session_repo.create(
                    student_id=student_id,
                    activity_id=activity_id,
                    mode='LEGACY_IMPORT',
                    metadata={
                        'github_repo': repo['full_name'],
                        'migrated_from': 'github'
                    }
                )
                migrated_sessions += 1

                # Obtener commits y crear trazas N2
                commits = get_commits(repo['name'])

                for commit in commits:
                    trace = trace_repo.create(
                        session_id=session.id,
                        student_id=student_id,
                        activity_id=activity_id,
                        trace_level='N2_TECNICO',
                        interaction_type='GIT_COMMIT',
                        content=commit['commit']['message'],
                        metadata={
                            'sha': commit['sha'],
                            'author': commit['commit']['author']['name'],
                            'date': commit['commit']['author']['date'],
                            'url': commit['html_url'],
                            'migrated_from': 'github'
                        }
                    )
                    migrated_traces += 1

                # Finalizar sesión
                session_repo.end_session(session.id)

                print(f"✓ Repo migrado: {repo['name']} ({len(commits)} commits)")

            except Exception as e:
                print(f"✗ Error en {repo['name']}: {e}")

        print(f"\n✅ Sesiones migradas: {migrated_sessions}")
        print(f"✅ Trazas N2 migradas: {migrated_traces}")


def main():
    print("=" * 60)
    print("MIGRACIÓN DESDE GITHUB CLASSROOM A AI-NATIVE")
    print("=" * 60)

    print("\n[1/3] Migrando usuarios...")
    migrate_users()

    print("\n[2/3] Migrando actividades...")
    migrate_assignments()

    print("\n[3/3] Migrando commits como trazas N2...")
    migrate_commits_as_traces()

    print("\n🎉 Migración completada!")


if __name__ == "__main__":
    main()
```

### Paso 2: Configurar GitHub Token

```bash
# Crear Personal Access Token en GitHub:
# Settings → Developer settings → Personal access tokens → Generate new token
# Permisos necesarios: repo, read:org

export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"

python scripts/migrate_from_github.py
```

---

## Migración desde Canvas LMS

Canvas tiene una API REST muy completa. El proceso es similar a Moodle:

```python
# scripts/migrate_from_canvas.py

import requests
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import UserRepository

CANVAS_URL = 'https://canvas.tu-institucion.edu'
CANVAS_TOKEN = 'tu_token_aqui'

headers = {
    'Authorization': f'Bearer {CANVAS_TOKEN}'
}

def get_canvas_users():
    url = f'{CANVAS_URL}/api/v1/accounts/1/users'
    response = requests.get(url, headers=headers)
    return response.json()

def migrate_users():
    users = get_canvas_users()

    with get_db_session() as db:
        user_repo = UserRepository(db)

        for canvas_user in users:
            user_repo.create(
                email=canvas_user['login_id'],
                name=canvas_user['name'],
                role='STUDENT',
                student_id=canvas_user['sis_user_id'],
                metadata={
                    'canvas_id': canvas_user['id'],
                    'migrated_from': 'canvas'
                }
            )

            print(f"✓ Usuario migrado: {canvas_user['name']}")

# Similar para courses, assignments, submissions...
```

---

## Migración de Usuarios (LDAP/AD)

Ver **GUIA_ADMINISTRADOR.md** → Sección "Sincronización con Active Directory (LDAP)".

Script resumido:

```python
import ldap
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import UserRepository

def sync_ldap():
    conn = ldap.initialize('ldap://ad.tu-institucion.edu.ar')
    conn.simple_bind_s('CN=ServiceAccount,DC=inst,DC=edu,DC=ar', 'password')

    results = conn.search_s(
        'OU=Students,DC=inst,DC=edu,DC=ar',
        ldap.SCOPE_SUBTREE,
        '(objectClass=person)'
    )

    with get_db_session() as db:
        user_repo = UserRepository(db)

        for dn, attrs in results:
            user_repo.create(
                email=attrs['mail'][0].decode(),
                name=attrs['displayName'][0].decode(),
                role='STUDENT',
                student_id=attrs['sAMAccountName'][0].decode(),
                auth_method='LDAP'
            )
```

---

## Validación Post-Migración

### Script de Validación Automática

```python
# scripts/validate_migration.py

from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import (
    UserRepository, ActivityRepository, SessionRepository
)

def validate_migration():
    print("=" * 60)
    print("VALIDACIÓN POST-MIGRACIÓN")
    print("=" * 60)

    with get_db_session() as db:
        user_repo = UserRepository(db)
        activity_repo = ActivityRepository(db)
        session_repo = SessionRepository(db)

        # 1. Verificar usuarios
        users = user_repo.get_all()
        students = [u for u in users if u.role == 'STUDENT']
        teachers = [u for u in users if u.role == 'TEACHER']

        print(f"\n✓ Usuarios totales: {len(users)}")
        print(f"  - Estudiantes: {len(students)}")
        print(f"  - Docentes: {len(teachers)}")

        # 2. Verificar actividades
        activities = activity_repo.get_all()
        print(f"\n✓ Actividades totales: {len(activities)}")

        # 3. Verificar sesiones
        sessions = session_repo.get_all()
        completed_sessions = [s for s in sessions if s.status == 'COMPLETED']

        print(f"\n✓ Sesiones totales: {len(sessions)}")
        print(f"  - Completadas: {len(completed_sessions)}")

        # 4. Verificar integridad referencial
        orphan_sessions = []
        for session in sessions:
            student_exists = any(u.student_id == session.student_id for u in students)
            activity_exists = any(a.activity_id == session.activity_id for a in activities)

            if not student_exists:
                orphan_sessions.append((session.id, 'student not found'))
            if not activity_exists:
                orphan_sessions.append((session.id, 'activity not found'))

        if orphan_sessions:
            print(f"\n⚠️ Sesiones huérfanas detectadas: {len(orphan_sessions)}")
            for session_id, reason in orphan_sessions[:5]:
                print(f"  - {session_id}: {reason}")
        else:
            print(f"\n✓ Integridad referencial: OK")

        # 5. Verificar duplicados
        emails = [u.email for u in users]
        duplicates = [email for email in set(emails) if emails.count(email) > 1]

        if duplicates:
            print(f"\n⚠️ Emails duplicados detectados: {len(duplicates)}")
            for email in duplicates:
                print(f"  - {email}")
        else:
            print(f"\n✓ Sin duplicados: OK")

        # Resumen
        print("\n" + "=" * 60)
        if not orphan_sessions and not duplicates:
            print("✅ VALIDACIÓN EXITOSA - Migración correcta")
            return True
        else:
            print("⚠️ VALIDACIÓN CON ADVERTENCIAS - Revisar manualmente")
            return False


if __name__ == "__main__":
    success = validate_migration()
    exit(0 if success else 1)
```

Ejecutar:

```bash
python scripts/validate_migration.py

# Si devuelve exit code 0 → Éxito
# Si devuelve exit code 1 → Hay problemas
```

---

## Rollback y Contingencia

### Plan de Rollback

**Si la migración falla**:

1. **Detener AI-Native**:
```bash
sudo systemctl stop ai-native.service
```

2. **Restaurar backup de Moodle** (si fue afectado):
```bash
mysql -u moodle_user -p moodle_db < moodle_backup_20251215.sql
```

3. **Eliminar datos migrados en AI-Native**:
```bash
# Conectar a PostgreSQL
psql -U ai_native -d ai_native

-- Eliminar datos migrados (identificados por metadata)
DELETE FROM sessions WHERE metadata->>'migrated_from' = 'moodle';
DELETE FROM activities WHERE metadata->>'migrated_from' = 'moodle';
DELETE FROM users WHERE metadata->>'migrated_from' = 'moodle';

-- Verificar
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM activities;
SELECT COUNT(*) FROM sessions;
```

4. **Documentar problemas**:
```bash
# Crear reporte de incidente
cat > migration_rollback_report.md <<EOF
# Reporte de Rollback - Migración Moodle

Fecha: $(date)
Responsable: Juan Pérez

## Problemas Detectados
1. [Descripción del problema 1]
2. [Descripción del problema 2]

## Acciones Tomadas
1. Rollback ejecutado
2. Moodle restaurado
3. AI-Native limpiado

## Próximos Pasos
1. Revisar script de migración
2. Corregir errores
3. Re-intentar en fecha TBD
EOF
```

---

## Casos de Estudio

### Caso 1: UTN FRM - Programación 2

**Contexto**:
- 87 estudiantes
- 2 docentes
- 8 TPs en Moodle

**Migración**:
- Duración: 4 horas
- Usuarios: 89 (100% éxito)
- Actividades: 8 (100% éxito)
- Submissions: 696 (98.5% éxito - 10 duplicadas eliminadas)

**Resultado**: ✅ Exitoso

### Caso 2: Universidad XYZ - GitHub Classroom

**Contexto**:
- 120 estudiantes
- 15 asignaciones
- 1,800 commits totales

**Migración**:
- Duración: 6 horas
- Usuarios: 120 (100% éxito)
- Actividades: 15 (100% éxito)
- Commits → Trazas N2: 1,800 (100% éxito)

**Resultado**: ✅ Exitoso

---

## Troubleshooting

### Problema: Emails duplicados

**Síntoma**: Error `IntegrityError: duplicate key value violates unique constraint "users_email_key"`

**Solución**:
```python
# Agregar sufijo a duplicados
for i, duplicate in enumerate(duplicates):
    duplicate.email = f"{duplicate.email}.{i}"
```

### Problema: Actividades sin docente

**Síntoma**: Actividades migradas sin teacher_id válido.

**Solución**:
```sql
UPDATE activities
SET teacher_id = 'default_teacher_001'
WHERE teacher_id IS NULL;
```

### Problema: Sesiones sin finalizar

**Síntoma**: Todas las sesiones quedan en estado ACTIVE.

**Solución**:
```python
for session in sessions:
    session_repo.end_session(session.id)
```

---

## Recursos Adicionales

- **Moodle API**: https://docs.moodle.org/dev/Web_services
- **GitHub API**: https://docs.github.com/en/rest
- **Canvas API**: https://canvas.instructure.com/doc/api/

---

**¡Migración exitosa! 🚀**

**Mag. en Ing. de Software Alberto Cortez**
Universidad Tecnológica Nacional