# 🚀 Guía Rápida: Migración de Ejercicios a PostgreSQL

## 📖 Para comenzar la implementación

El plan completo y detallado está en: `docs/plans/migracion-ejercicios-db.md`

## ✅ Checklist Ejecutivo de Fases

### ✅ FASE 1: Modelos y Migraciones (Base de Datos)
**Archivos a crear:**
- `backend/database/models.py` - Agregar 5 nuevos modelos
- `backend/database/migrations/add_exercises_tables.py` - Script de migración

**Comando de ejecución:**
```bash
cd activia1-main
python -m backend.database.migrations.add_exercises_tables
```

**Verificación:**
```bash
docker-compose exec postgres psql -U activia_user -d activia_db -c "\dt"
# Debe mostrar: subjects, exercises, exercise_hints, exercise_tests, exercise_attempts
```

---

### ✅ FASE 2: Schemas Pydantic y Repositorios
**Archivos a crear:**
- `backend/api/schemas/exercises.py` - Schemas Pydantic
- `backend/database/repositories/subject_repository.py`
- `backend/database/repositories/exercise_repository.py`
- `backend/database/repositories/exercise_test_repository.py`
- `backend/database/repositories/exercise_attempt_repository.py`

**Tests:**
```bash
pytest tests/test_repositories/test_exercise_repository.py -v
```

---

### ✅ FASE 3: Seed Database
**Archivo a crear:**
- `backend/scripts/seed_exercises.py` (script idempotente)

**Ejecución:**
```bash
# Ver qué se creará/actualizará sin escribir
python -m backend.scripts.seed_exercises --dry-run

# Seed normal (crear nuevos ejercicios)
python -m backend.scripts.seed_exercises

# Forzar actualización de todos
python -m backend.scripts.seed_exercises --force-update
```

**Verificación:**
```sql
SELECT subject_id, COUNT(*) FROM exercises GROUP BY subject_id;
SELECT COUNT(*) FROM exercise_tests;
SELECT COUNT(*) FROM exercise_hints;
```

---

### ✅ FASE 4: Actualizar API Endpoints
**Archivo a modificar:**
- `backend/api/routers/training.py`

**Cambios principales:**
- `GET /training/materias` - Lee de `subjects` + `exercises`
- `POST /training/iniciar` - Lee ejercicio de BD
- `POST /training/submit-ejercicio` - Guarda attempt en BD

**Verificación:**
```bash
# Frontend debe seguir funcionando igual
npm run dev
# Probar seleccionar materia → iniciar ejercicio → enviar código
```

---

### ✅ FASE 5: Testing y Validación
**Tests a ejecutar:**
```bash
# Suite completa
pytest tests/ -v --cov=backend --cov-report=html

# Solo tests de training
pytest tests/test_integration/test_training_flow_db.py -v

# Verificar cobertura > 70%
open htmlcov/index.html
```

---

### ✅ FASE 6: Archivar JSONs y Limpieza
**Comandos:**
```bash
# Crear carpetas archive
mkdir -p backend/data/archive/training
mkdir -p backend/data/archive/exercises

# Mover JSONs (NO eliminar)
mv backend/data/training/*.json backend/data/archive/training/
mv backend/data/exercises/*.json backend/data/archive/exercises/

# Crear README en archive
echo "# Ejercicios migrados a PostgreSQL el 2025-12-23" > backend/data/archive/README.md
```

---

## 🎯 Cómo continuar entre sesiones

### Al finalizar una sesión:
1. Marca las tareas completadas en `docs/plans/migracion-ejercicios-db.md`
2. Actualiza el checklist de la fase actual
3. Haz commit de los cambios:
   ```bash
   git add .
   git commit -m "feat: Fase X de migración ejercicios - [descripción]"
   ```

### Al iniciar una nueva sesión:
1. Abre `docs/plans/migracion-ejercicios-db.md`
2. Revisa el estado de cada fase (⬜ / ⏳ / ✅)
3. Continúa con la siguiente tarea pendiente
4. Verifica que la fase anterior funcionó correctamente

---

## 🔥 Comandos útiles durante la migración

### Verificar estado de PostgreSQL
```bash
# Ver tablas
docker-compose exec postgres psql -U activia_user -d activia_db -c "\dt"

# Ver cantidad de registros
docker-compose exec postgres psql -U activia_user -d activia_db -c "SELECT COUNT(*) FROM exercises;"

# Ver índices
docker-compose exec postgres psql -U activia_user -d activia_db -c "\di"
```

### Rollback si algo sale mal
```bash
# Rollback de migración
python -m backend.database.migrations.add_exercises_tables rollback

# Restaurar JSONs desde archive
cp backend/data/archive/training/*.json backend/data/training/
cp backend/data/archive/exercises/*.json backend/data/exercises/
```

### Backup de base de datos
```bash
# Antes de FASE 3 (migración de datos)
docker-compose exec postgres pg_dump -U activia_user activia_db > backup_pre_migration.sql

# Restaurar si es necesario
docker-compose exec -T postgres psql -U activia_user activia_db < backup_pre_migration.sql
```

---

## 📊 Métricas de éxito

Al finalizar, deberías tener:

- ✅ ~20-25 ejercicios en `exercises` table
- ✅ ~100-150 tests en `exercise_tests` table
- ✅ ~15-20 hints en `exercise_hints` table
- ✅ 3 subjects en `subjects` table (PYTHON, JAVA, PROG1)
- ✅ 0 attempts al inicio (se llenarán con uso)

---

## 🆘 Troubleshooting

### Error: "relation 'exercises' does not exist"
→ No ejecutaste FASE 1 correctamente
```bash
python -m backend.database.migrations.add_exercises_tables
```

### Error: "foreign key constraint fails"
→ Verifica que subjects existen antes de crear exercises
```sql
SELECT * FROM subjects;
```

### Error: "duplicate key value violates unique constraint"
→ Ejecutaste el script de migración dos veces
```sql
-- Limpiar y volver a migrar
TRUNCATE exercises, exercise_tests, exercise_hints CASCADE;
```

---

## 📞 Contacto

Si encuentras algún problema durante la implementación:
1. Revisa los logs detallados en el plan completo
2. Verifica que completaste todas las tareas de la fase anterior
3. Ejecuta los tests de la fase actual
4. Documenta el error en el plan para referencia futura

---

**Última actualización**: 2025-12-23
