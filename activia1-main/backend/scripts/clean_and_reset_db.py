"""
Script para limpiar la base de datos y dejar solo:
- Usuarios de prueba (estudiante1, profesor1, admin1)
- Subject PROG1 (Python)
- Ejercicios SEC-* (Estructuras Secuenciales)
- Pistas y tests de SEC-*

ELIMINA:
- Todos los ejercicios que NO sean SEC-*
- Subject PROG2 (Java) y sus ejercicios
- Otros subjects que no sean PROG1

Usage:
    cd activia1-main
    docker-compose exec api python -m backend.scripts.clean_and_reset_db
"""

import sys
import logging
from pathlib import Path
from sqlalchemy import text

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.database.config import get_db_config
from backend.database.models import (
    SubjectDB,
    ExerciseDB,
    ExerciseHintDB,
    ExerciseTestDB,
    ExerciseRubricCriterionDB,
    RubricLevelDB,
    ExerciseAttemptDB,
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def clean_database():
    """Limpia la base de datos manteniendo solo datos esenciales"""

    logger.info("=" * 70)
    logger.info("LIMPIEZA DE BASE DE DATOS")
    logger.info("=" * 70)

    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine

    # Crear conexión
    config = get_db_config()
    engine = create_engine(config.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        stats = {
            'exercises_deleted': 0,
            'hints_deleted': 0,
            'tests_deleted': 0,
            'subjects_deleted': 0,
            'attempts_deleted': 0,
        }

        # 1. Eliminar intentos de ejercicios que no sean SEC-*
        logger.info("\n[1/5] Eliminando intentos de ejercicios no-SEC...")
        non_sec_attempts = session.query(ExerciseAttemptDB).filter(
            ~ExerciseAttemptDB.exercise_id.like('SEC-%')
        ).all()
        for attempt in non_sec_attempts:
            session.delete(attempt)
            stats['attempts_deleted'] += 1
        session.commit()
        logger.info(f"  Intentos eliminados: {stats['attempts_deleted']}")

        # 2. Eliminar pistas de ejercicios que no sean SEC-*
        logger.info("\n[2/5] Eliminando pistas de ejercicios no-SEC...")
        non_sec_hints = session.query(ExerciseHintDB).filter(
            ~ExerciseHintDB.exercise_id.like('SEC-%')
        ).all()
        for hint in non_sec_hints:
            session.delete(hint)
            stats['hints_deleted'] += 1
        session.commit()
        logger.info(f"  Pistas eliminadas: {stats['hints_deleted']}")

        # 3. Eliminar tests de ejercicios que no sean SEC-*
        logger.info("\n[3/5] Eliminando tests de ejercicios no-SEC...")
        non_sec_tests = session.query(ExerciseTestDB).filter(
            ~ExerciseTestDB.exercise_id.like('SEC-%')
        ).all()
        for test in non_sec_tests:
            session.delete(test)
            stats['tests_deleted'] += 1
        session.commit()
        logger.info(f"  Tests eliminados: {stats['tests_deleted']}")

        # 4. Eliminar ejercicios que no sean SEC-*
        logger.info("\n[4/5] Eliminando ejercicios no-SEC...")
        non_sec_exercises = session.query(ExerciseDB).filter(
            ~ExerciseDB.id.like('SEC-%')
        ).all()

        for exercise in non_sec_exercises:
            logger.info(f"  - Eliminando: {exercise.id} ({exercise.title})")
            session.delete(exercise)
            stats['exercises_deleted'] += 1
        session.commit()
        logger.info(f"  Total ejercicios eliminados: {stats['exercises_deleted']}")

        # 5. Eliminar subjects que no sean PROG1
        logger.info("\n[5/5] Eliminando subjects no-PROG1...")
        non_prog1_subjects = session.query(SubjectDB).filter(
            SubjectDB.code != 'PROG1'
        ).all()

        for subject in non_prog1_subjects:
            logger.info(f"  - Eliminando subject: {subject.code} ({subject.name})")
            session.delete(subject)
            stats['subjects_deleted'] += 1
        session.commit()
        logger.info(f"  Total subjects eliminados: {stats['subjects_deleted']}")

        # Verificación final
        logger.info("\n" + "=" * 70)
        logger.info("VERIFICACIÓN FINAL")
        logger.info("=" * 70)

        remaining_subjects = session.query(SubjectDB).all()
        logger.info(f"Subjects restantes: {len(remaining_subjects)}")
        for subject in remaining_subjects:
            logger.info(f"  - {subject.code}: {subject.name}")

        remaining_exercises = session.query(ExerciseDB).all()
        logger.info(f"\nEjercicios restantes: {len(remaining_exercises)}")
        for exercise in remaining_exercises:
            logger.info(f"  - {exercise.id}: {exercise.title} (unit={exercise.unit})")

        remaining_hints = session.query(ExerciseHintDB).count()
        logger.info(f"\nPistas restantes: {remaining_hints}")

        remaining_tests = session.query(ExerciseTestDB).count()
        logger.info(f"Tests restantes: {remaining_tests}")

        # Resumen
        logger.info("\n" + "=" * 70)
        logger.info("RESUMEN DE LIMPIEZA")
        logger.info("=" * 70)
        logger.info(f"Intentos eliminados:   {stats['attempts_deleted']}")
        logger.info(f"Pistas eliminadas:     {stats['hints_deleted']}")
        logger.info(f"Tests eliminados:      {stats['tests_deleted']}")
        logger.info(f"Ejercicios eliminados: {stats['exercises_deleted']}")
        logger.info(f"Subjects eliminados:   {stats['subjects_deleted']}")
        logger.info("=" * 70)
        logger.info("LIMPIEZA COMPLETADA")
        logger.info("=" * 70)

    except Exception as e:
        session.rollback()
        logger.error(f"Error durante la limpieza: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    clean_database()
