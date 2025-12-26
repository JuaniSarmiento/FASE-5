# Archived Exercise Data

**Fecha de archivo**: 2025-12-26
**Razón**: Migración completa de ejercicios JSON → PostgreSQL

## Contenido Archivado

### `training/`
Archivos JSON del sistema antiguo de entrenamiento:
- `programacion1_temas.json` - 5 temas del sistema legacy

### `exercises/`
Catálogo de ejercicios por unidades:
- `catalog.json` - Metadatos del catálogo
- `unit1_fundamentals.json` - Ejercicios Python unidad 1
- `unit2_structures.json` - Ejercicios Python unidad 2
- `unit3_functions.json` - Ejercicios Python unidad 3
- `unit4_files.json` - Ejercicios Python unidad 4
- `unit5_oop.json` - Ejercicios Python unidad 5
- `unit6_java_fundamentals.json` - Ejercicios Java unidad 6
- `unit7_springboot.json` - Ejercicios Java unidad 7

**Total migrado**: ~23 ejercicios únicos + tests + hints

## Migración Completada

Todos estos ejercicios fueron migrados exitosamente a PostgreSQL usando el script:
```bash
python -m backend.scripts.seed_exercises
```

Las tablas de destino:
- `subjects` - Materias (Python, Java)
- `exercises` - Ejercicios individuales
- `exercise_hints` - Pistas graduadas con penalizaciones
- `exercise_tests` - Tests unitarios (visibles y ocultos)
- `exercise_attempts` - Intentos de estudiantes (nuevo)
- `exercise_rubric_criteria` - Criterios de rúbricas (nuevo)
- `rubric_levels` - Niveles de evaluación (nuevo)

## Estado de la API

Los endpoints de `/training/*` ahora leen desde PostgreSQL:
- ✅ `GET /training/materias` - Lee subjects y exercises desde BD
- ✅ `POST /training/iniciar` - Carga exercise, hints y tests desde BD
- ✅ `POST /training/submit-ejercicio` - Guarda attempts en BD
- ✅ `POST /training/pista` - Usa hints desde BD
- ✅ `POST /training/corregir-ia` - Usa tests desde BD
- ✅ `GET /training/exercises/{id}/details` - Endpoint de debugging (teachers)

## Archivos Originales

Los archivos JSON originales se mantienen en:
- `backend/data/training/` (activo)
- `backend/data/exercises/` (activo)

**No eliminar**: Se conservan como respaldo y documentación del formato original.

## Documentación

Ver plan completo en:
- `docs/plans/migracion-ejercicios-db.md`

---

**Migración ejecutada por**: Claude Code
**Script de seed**: `backend/scripts/seed_exercises.py`
**Fecha de completado**: 2025-12-26
