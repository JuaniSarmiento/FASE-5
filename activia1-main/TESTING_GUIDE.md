# 🧪 Guía de Testing - Migración Ejercicios PostgreSQL

Esta guía te ayudará a **verificar que la migración de ejercicios funciona correctamente** después de descargar el proyecto.

## ✅ Setup Automático (Recomendado)

### 1. Iniciar el Stack

```bash
cd activia1-main
docker-compose up -d
```

### 2. Ver Logs del API (Verificar Auto-Seed)

```bash
docker-compose logs -f api
```

**Busca estos mensajes en los logs**:

```
✅ SEED AUTOMÁTICO EXITOSO:
🌱 DATABASE IS EMPTY - Starting seed process
🚀 Running seed_exercises script...
✅ Seeded subject: PROG1 - Programación 1
✅ Seeded exercise: variables - Variables y Tipos de Datos
...
📊 SEED RESULTS:
   ✅ Subjects: 2
   ✅ Exercises: 23
```

**O si ya tenía datos**:
```
📚 DATABASE ALREADY SEEDED - Skipping initialization
   Found: 2 subjects, 23 exercises
```

### 3. Verificar Datos en Base de Datos

```bash
# Ver cantidad de ejercicios
docker-compose exec api python -c "from backend.database.config import SessionLocal; from backend.database.models import ExerciseDB; db = SessionLocal(); print(f'✅ {db.query(ExerciseDB).count()} ejercicios cargados'); db.close()"

# Ver subjects
docker-compose exec api python -c "from backend.database.config import SessionLocal; from backend.database.models import SubjectDB; db = SessionLocal(); subjects = db.query(SubjectDB).all(); [print(f'  - {s.code}: {s.name}') for s in subjects]; db.close()"
```

**Output esperado**:
```
✅ 23 ejercicios cargados
  - PROG1: Programación 1
  - PROG2: Python - Programación 2
```

---

## 🧪 Testing Manual de Endpoints

### 1. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Esperado**:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### 2. Obtener Materias (GET /training/materias)

```bash
curl http://localhost:8000/api/v1/training/materias | python -m json.tool
```

**Esperado**: JSON con 2 materias (Python y Java/PROG1) y ~23 ejercicios totales.

### 3. Login y Obtener Token

Primero crea un usuario de prueba:

```bash
docker-compose exec api python -c "
from backend.database.config import SessionLocal
from backend.database.models import UserDB
from backend.core.security import get_password_hash
db = SessionLocal()
user = UserDB(
    id='test-student',
    email='student@test.com',
    full_name='Test Student',
    hashed_password=get_password_hash('password123'),
    role='student',
    is_active=True
)
db.add(user)
db.commit()
print('✅ Usuario de prueba creado')
"
```

Login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@test.com",
    "password": "password123"
  }' | python -m json.tool
```

**Guarda el token** del response en una variable:

```bash
export TOKEN="<tu-token-aqui>"
```

### 4. Iniciar Entrenamiento (POST /training/iniciar)

```bash
curl -X POST http://localhost:8000/api/v1/training/iniciar \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "materia_codigo": "PYTHON",
    "tema_id": "variables"
  }' | python -m json.tool
```

**Esperado**: Respuesta con `session_id`, `ejercicio_actual` con código inicial, consigna, etc.

**Guarda el session_id**:

```bash
export SESSION_ID="<session-id-aqui>"
```

### 5. Enviar Código (POST /training/submit-ejercicio)

```bash
curl -X POST http://localhost:8000/api/v1/training/submit-ejercicio \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"codigo_usuario\": \"def suma(a, b):\n    return a + b\"
  }" | python -m json.tool
```

**Esperado**: Evaluación del código con tests ejecutados.

### 6. Verificar Attempt Guardado en BD

```bash
docker-compose exec api python -c "
from backend.database.config import SessionLocal
from backend.database.models import ExerciseAttemptDB
db = SessionLocal()
attempts = db.query(ExerciseAttemptDB).all()
print(f'✅ {len(attempts)} attempts guardados')
if attempts:
    latest = attempts[-1]
    print(f'   Último attempt:')
    print(f'   - Exercise: {latest.exercise_id}')
    print(f'   - Status: {latest.status}')
    print(f'   - Score: {latest.score}/10')
    print(f'   - Tests: {latest.tests_passed}/{latest.tests_total}')
db.close()
"
```

**Esperado**: Ver el attempt que acabas de enviar.

### 7. Solicitar Pista (POST /training/pista)

```bash
curl -X POST http://localhost:8000/api/v1/training/pista \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"numero_pista\": 0
  }" | python -m json.tool
```

**Esperado**: Contenido de la primera pista del ejercicio.

---

## 🔍 Testing con Frontend (Manual)

### 1. Iniciar Frontend

```bash
cd activia1-main/frontEnd
npm install
npm run dev
```

### 2. Abrir en Navegador

```
http://localhost:5173
```

### 3. Flujo Completo de Usuario

1. **Login**: `student@test.com` / `password123`
2. **Ir a Entrenador Digital**
3. **Seleccionar Materia**: Python
4. **Seleccionar Ejercicio**: Variables y Tipos de Datos
5. **Iniciar Entrenamiento**
6. **Escribir código** (puede ser incorrecto al principio)
7. **Enviar código** → Ver evaluación
8. **Solicitar pista** (si hay disponibles)
9. **Corregir código** → Enviar de nuevo
10. **Verificar nota final**

### 4. Verificar en BD que se Guardó el Attempt

```bash
docker-compose exec api python -c "
from backend.database.config import SessionLocal
from backend.database.models import ExerciseAttemptDB
db = SessionLocal()
attempts = db.query(ExerciseAttemptDB).order_by(ExerciseAttemptDB.submitted_at.desc()).limit(5).all()
print(f'Últimos 5 attempts:')
for a in attempts:
    print(f'  - {a.exercise_id}: {a.status} ({a.score:.1f}/10) - {a.tests_passed}/{a.tests_total} tests')
db.close()
"
```

---

## 🗄️ Verificación Directa de PostgreSQL

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U ai_native -d ai_native

# Ver ejercicios
SELECT id, title, difficulty FROM exercises LIMIT 5;

# Ver subjects
SELECT code, name FROM subjects;

# Ver hints de un ejercicio
SELECT exercise_id, hint_number, penalty_points FROM exercise_hints WHERE exercise_id = 'variables';

# Ver tests de un ejercicio
SELECT exercise_id, test_number, is_hidden FROM exercise_tests WHERE exercise_id = 'variables';

# Ver attempts
SELECT exercise_id, student_id, status, score FROM exercise_attempts ORDER BY submitted_at DESC LIMIT 5;

# Salir
\q
```

---

## ❌ Troubleshooting

### Problema: No se cargaron ejercicios automáticamente

**Verificar logs**:
```bash
docker-compose logs api | grep -i seed
```

**Ejecutar seed manualmente**:
```bash
docker-compose exec api python -m backend.scripts.seed_exercises
```

### Problema: Error de autenticación

**Crear usuario de prueba**:
```bash
docker-compose exec api python -m backend.scripts.seed_dev
```

### Problema: Base de datos vacía

**Reiniciar stack y forzar seed**:
```bash
docker-compose down -v  # CUIDADO: Borra todos los datos
docker-compose up -d
# El auto-seed debería ejecutarse automáticamente
```

### Problema: Ejercicios duplicados

**Limpiar y re-seed**:
```bash
docker-compose exec api python -c "
from backend.database.config import SessionLocal
from backend.database.models import ExerciseDB, SubjectDB
db = SessionLocal()
db.query(ExerciseDB).delete()
db.query(SubjectDB).delete()
db.commit()
print('✅ Ejercicios eliminados. Reinicia el contenedor para auto-seed.')
"

docker-compose restart api
```

---

## ✅ Checklist de Verificación Final

Marca cada item después de verificarlo:

- [ ] `docker-compose up -d` arranca sin errores
- [ ] Logs muestran auto-seed exitoso (o skip si ya tenía datos)
- [ ] `GET /training/materias` retorna 2+ materias con ejercicios
- [ ] Puedo hacer login y obtener token
- [ ] `POST /training/iniciar` carga un ejercicio con código inicial
- [ ] `POST /training/submit-ejercicio` evalúa el código
- [ ] Se guardan attempts en la tabla `exercise_attempts`
- [ ] `POST /training/pista` retorna pistas del ejercicio
- [ ] Frontend se conecta al backend correctamente
- [ ] Puedo completar un ejercicio end-to-end

---

## 📊 Scripts Útiles para Debugging

### Ver Estadísticas Completas

```bash
docker-compose exec api python -c "
from backend.database.config import SessionLocal
from backend.database.models import SubjectDB, ExerciseDB, ExerciseHintDB, ExerciseTestDB, ExerciseAttemptDB

db = SessionLocal()

subjects = db.query(SubjectDB).count()
exercises = db.query(ExerciseDB).count()
hints = db.query(ExerciseHintDB).count()
tests = db.query(ExerciseTestDB).count()
attempts = db.query(ExerciseAttemptDB).count()

print('=' * 60)
print('📊 DATABASE STATISTICS')
print('=' * 60)
print(f'Subjects:  {subjects}')
print(f'Exercises: {exercises}')
print(f'Hints:     {hints}')
print(f'Tests:     {tests}')
print(f'Attempts:  {attempts}')
print('=' * 60)

db.close()
"
```

### Verificar Migración Completa

```bash
docker-compose exec api python -m backend.database.migrations.add_exercises_tables verify
```

---

**Última actualización**: 2025-12-26
**Versión del plan**: 1.2

¿Necesitas ayuda? Revisa `docs/plans/migracion-ejercicios-db.md`
