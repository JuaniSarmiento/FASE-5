# 🔄 Seed Database vs Migración: ¿Por qué Seed es Mejor?

## 📊 Comparación

| Aspecto | Migración (Script One-Time) | Seed Database (Idempotente) |
|---------|----------------------------|----------------------------|
| **Ejecuciones** | Solo una vez | Múltiples veces sin romper |
| **Desarrollo** | Requiere reset manual de BD | `make seed` y listo |
| **Tests** | Difícil setup de datos | Fácil: `seed_exercises()` antes de tests |
| **CI/CD** | Complejidad adicional | Parte del pipeline estándar |
| **Agregar ejercicios** | Nuevo script cada vez | Modificar JSON + re-ejecutar seed |
| **Actualizar ejercicios** | Complejo (UPDATE manual) | Automático con `--force-update` |
| **Rollback** | Manual y propenso a errores | Truncar + re-seed |
| **Patrón** | Ad-hoc, no estándar | Patrón estándar en desarrollo |

---

## ✅ Ventajas del Seed Database

### 1. **Idempotencia**
```bash
# Puedes ejecutarlo 100 veces sin problemas
python -m backend.scripts.seed_exercises

# Primera vez: Crea 25 ejercicios
# ✅ Creado: U1-VAR-01
# ✅ Creado: U1-COND-01
# ...

# Segunda vez: No hace nada (ya existen)
# ⏭️ Saltado: U1-VAR-01 (ya existe)
# ⏭️ Saltado: U1-COND-01 (ya existe)
```

### 2. **Desarrollo Local Rápido**
```bash
# Resetear BD y empezar de cero
docker-compose down -v
docker-compose up -d
python -m backend.scripts.seed_exercises

# ¡Listo en 30 segundos!
```

### 3. **Actualización de Ejercicios**
```bash
# 1. Editas un JSON (cambias un test, mejoras descripción)
vim backend/data/exercises/unit1_fundamentals.json

# 2. Re-seed con force-update
python -m backend.scripts.seed_exercises --force-update

# 3. El ejercicio se actualiza en BD automáticamente
# 🔄 Actualizado: U1-VAR-01 (nueva versión)
```

### 4. **Integración con Tests**
```python
# tests/conftest.py
@pytest.fixture(scope="session")
def seed_database(db):
    """Seed database antes de tests"""
    from backend.scripts.seed_exercises import seed_all
    seed_all(db)
    yield
    # Cleanup automático después de tests

# tests/test_training.py
def test_get_exercises(client, seed_database):
    # DB ya tiene ejercicios, test es simple
    response = client.get("/training/materias")
    assert len(response.json()) == 3  # PYTHON, JAVA, PROG1
```

### 5. **CI/CD Pipeline**
```yaml
# .github/workflows/tests.yml
- name: Run tests
  run: |
    docker-compose up -d postgres
    python -m backend.scripts.seed_exercises  # Seed automático
    pytest tests/ -v
```

### 6. **Agregar Ejercicios Nuevos**
```bash
# 1. Creas un nuevo JSON
vim backend/data/exercises/unit8_advanced.json

# 2. Re-ejecutas seed
python -m backend.scripts.seed_exercises

# 3. Solo crea los nuevos, no toca los existentes
# ⏭️ Saltado: U1-VAR-01 (ya existe)
# ✅ Creado: U8-ADV-01 (nuevo!)
# ✅ Creado: U8-ADV-02 (nuevo!)
```

---

## ❌ Problemas con Migración One-Time

### Problema 1: No es Re-ejecutable
```bash
# Primera vez: OK
python -m backend.scripts.migrate_exercises_to_db
# ✅ Migrados 25 ejercicios

# Segunda vez: ERROR
python -m backend.scripts.migrate_exercises_to_db
# ❌ IntegrityError: duplicate key value violates unique constraint "exercises_pkey"
```

**Solución Seed**:
```python
# Patrón idempotente
exercise = exercise_repo.get_by_id(id)
if not exercise:
    exercise_repo.create(data)  # Solo crear si no existe
else:
    pass  # O actualizar si cambió
```

### Problema 2: Difícil para Desarrollo
```bash
# Desarrollador nuevo clona el repo
git clone ...

# Necesita ejercicios en su BD local
# Opción A (migración): ¿Dónde está el script? ¿Se ejecutó ya? ¿Está actualizado?
# Opción B (seed): make seed  ← Simple y obvio
```

### Problema 3: Actualizar un Ejercicio es Complejo
```bash
# Quiero cambiar la descripción de U1-VAR-01
# Con migración: Escribir SQL manual
UPDATE exercises
SET description = 'Nueva descripción'
WHERE id = 'U1-VAR-01';

# Con seed: Editar JSON + re-ejecutar
vim backend/data/exercises/unit1_fundamentals.json
python -m backend.scripts.seed_exercises --force-update
```

---

## 🎯 Implementación de Seed Idempotente

### Patrón Get-or-Create
```python
def seed_exercise(exercise_data):
    """Seed un ejercicio (idempotente)"""
    exercise_id = exercise_data['id']

    # 1. Intentar obtener existente
    existing = exercise_repo.get_by_id(exercise_id)

    if existing:
        # 2a. Ya existe - skip o update
        if args.force_update:
            exercise_repo.update(exercise_id, exercise_data)
            logger.info(f"🔄 Actualizado: {exercise_id}")
        else:
            logger.info(f"⏭️ Saltado: {exercise_id} (ya existe)")
    else:
        # 2b. No existe - crear
        exercise_repo.create(exercise_data)
        logger.info(f"✅ Creado: {exercise_id}")
```

### Patrón Upsert (PostgreSQL)
```python
from sqlalchemy.dialects.postgresql import insert

def upsert_exercise(exercise_data):
    """Upsert usando ON CONFLICT (PostgreSQL)"""
    stmt = insert(ExerciseDB).values(exercise_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=['id'],
        set_=exercise_data
    )
    db.execute(stmt)
```

---

## 📚 Ejemplos del Mundo Real

### Django
```python
# Django usa fixtures (seed data)
python manage.py loaddata exercises.json  # Idempotente
```

### Rails
```ruby
# Rails usa seeds.rb
rails db:seed  # Idempotente
```

### Laravel
```php
// Laravel usa seeders
php artisan db:seed  # Idempotente
```

### NestJS
```typescript
// NestJS usa seeders
npm run seed  // Idempotente
```

**Todos estos frameworks usan SEED, no "migrations one-time".**

---

## 🔄 Flujo Recomendado

### 1. Desarrollo Local
```bash
# Setup inicial
docker-compose up -d
python -m backend.scripts.seed_exercises

# Agregar nuevo ejercicio
vim backend/data/exercises/unit1_fundamentals.json
python -m backend.scripts.seed_exercises  # Solo crea el nuevo

# Actualizar ejercicio existente
vim backend/data/exercises/unit1_fundamentals.json
python -m backend.scripts.seed_exercises --force-update
```

### 2. Tests
```bash
# Tests resetean BD automáticamente
pytest tests/  # seed_exercises() en conftest.py
```

### 3. Staging/Producción
```bash
# Deploy
git pull
python -m backend.scripts.seed_exercises --force-update

# O integrado en make deploy:
make deploy  # Incluye seed automáticamente
```

---

## ✅ Conclusión

**Seed Database** es:
- ✅ Más profesional (patrón estándar)
- ✅ Más fácil de usar (re-ejecutable)
- ✅ Más mantenible (actualizar es trivial)
- ✅ Mejor para desarrollo (resetear BD rápido)
- ✅ Mejor para tests (setup simple)
- ✅ Mejor para CI/CD (pipeline limpio)

**Migración One-Time** es:
- ❌ Propenso a errores (no re-ejecutable)
- ❌ Complejo de mantener (scripts acumulados)
- ❌ Difícil para desarrollo (requiere tracking manual)
- ❌ No es estándar (ad-hoc)

---

**Decisión**: Usar **Seed Database** (`backend/scripts/seed_exercises.py`) en lugar de script de migración one-time.

---

**Última actualización**: 2025-12-23
