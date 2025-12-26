"""
Migration: Add exercises tables for Training Digital

Crea 7 nuevas tablas para migrar ejercicios desde JSON a PostgreSQL:
- subjects: Materias (Python, Java, PROG1)
- exercises: Ejercicios individuales
- exercise_hints: Pistas graduadas
- exercise_tests: Tests unitarios
- exercise_attempts: Intentos de estudiantes
- exercise_rubric_criteria: Criterios de rúbrica (FASE 1.5)
- rubric_levels: Niveles de cada criterio (FASE 1.5)

Usage:
    python -m backend.database.migrations.add_exercises_tables
    python -m backend.database.migrations.add_exercises_tables rollback
    python -m backend.database.migrations.add_exercises_tables verify
"""

import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "activia1-main"))

from backend.database.config import get_db_config
from backend.database.models import (
    SubjectDB,
    ExerciseDB,
    ExerciseHintDB,
    ExerciseTestDB,
    ExerciseAttemptDB,
    ExerciseRubricCriterionDB,
    RubricLevelDB,
    Base
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_engine():
    """Get database engine"""
    db_config = get_db_config()
    return db_config.get_engine()


def verify_tables_exist(engine) -> bool:
    """Verify that all exercise tables exist"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    required_tables = [
        "subjects",
        "exercises",
        "exercise_hints",
        "exercise_tests",
        "exercise_attempts",
        "exercise_rubric_criteria",
        "rubric_levels"
    ]

    all_exist = all(table in existing_tables for table in required_tables)

    if all_exist:
        logger.info("✅ All exercise tables exist:")
        for table in required_tables:
            logger.info(f"   - {table}")
    else:
        logger.warning("❌ Some tables are missing:")
        for table in required_tables:
            status = "✓" if table in existing_tables else "✗"
            logger.info(f"   {status} {table}")

    return all_exist


def create_tables(engine):
    """Create all exercise tables"""
    logger.info("🔨 Creating exercise tables...")

    try:
        # Create only the new exercise tables
        # NOTE: Base.metadata.create_all() is idempotent - won't fail if tables exist
        SubjectDB.__table__.create(engine, checkfirst=True)
        logger.info("✅ Created table: subjects")

        ExerciseDB.__table__.create(engine, checkfirst=True)
        logger.info("✅ Created table: exercises")

        ExerciseHintDB.__table__.create(engine, checkfirst=True)
        logger.info("✅ Created table: exercise_hints")

        ExerciseTestDB.__table__.create(engine, checkfirst=True)
        logger.info("✅ Created table: exercise_tests")

        ExerciseAttemptDB.__table__.create(engine, checkfirst=True)
        logger.info("✅ Created table: exercise_attempts")

        ExerciseRubricCriterionDB.__table__.create(engine, checkfirst=True)
        logger.info("✅ Created table: exercise_rubric_criteria")

        RubricLevelDB.__table__.create(engine, checkfirst=True)
        logger.info("✅ Created table: rubric_levels")

        logger.info("✅ All exercise tables created successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False


def drop_tables(engine):
    """Drop all exercise tables (for rollback)"""
    logger.info("🗑️  Dropping exercise tables...")

    try:
        with engine.connect() as conn:
            # Drop in reverse order due to foreign keys
            conn.execute(text("DROP TABLE IF EXISTS rubric_levels CASCADE"))
            logger.info("✅ Dropped table: rubric_levels")

            conn.execute(text("DROP TABLE IF EXISTS exercise_rubric_criteria CASCADE"))
            logger.info("✅ Dropped table: exercise_rubric_criteria")

            conn.execute(text("DROP TABLE IF EXISTS exercise_attempts CASCADE"))
            logger.info("✅ Dropped table: exercise_attempts")

            conn.execute(text("DROP TABLE IF EXISTS exercise_tests CASCADE"))
            logger.info("✅ Dropped table: exercise_tests")

            conn.execute(text("DROP TABLE IF EXISTS exercise_hints CASCADE"))
            logger.info("✅ Dropped table: exercise_hints")

            conn.execute(text("DROP TABLE IF EXISTS exercises CASCADE"))
            logger.info("✅ Dropped table: exercises")

            conn.execute(text("DROP TABLE IF EXISTS subjects CASCADE"))
            logger.info("✅ Dropped table: subjects")

            conn.commit()

        logger.info("✅ All exercise tables dropped successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Error dropping tables: {e}")
        return False


def verify_indexes(engine):
    """Verify that all indexes were created"""
    inspector = inspect(engine)

    tables_to_check = {
        "subjects": ["idx_subjects_language", "idx_subjects_active"],
        "exercises": [
            "idx_exercises_subject",
            "idx_exercises_unit",
            "idx_exercises_difficulty",
            "idx_exercises_language",
            "idx_exercises_active",
            "idx_exercises_tags"
        ],
        "exercise_hints": ["idx_hints_exercise", "idx_hints_order"],
        "exercise_tests": ["idx_tests_exercise", "idx_tests_hidden", "idx_tests_order"],
        "exercise_attempts": [
            "idx_attempts_exercise",
            "idx_attempts_student",
            "idx_attempts_session",
            "idx_attempts_status",
            "idx_attempts_submitted",
            "idx_attempts_student_exercise"
        ],
        "exercise_rubric_criteria": [
            "idx_rubric_criteria_exercise",
            "idx_rubric_criteria_order"
        ],
        "rubric_levels": [
            "idx_rubric_levels_criterion",
            "idx_rubric_levels_score_range"
        ]
    }

    logger.info("\n📊 Verifying indexes...")
    all_ok = True

    for table, expected_indexes in tables_to_check.items():
        actual_indexes = inspector.get_indexes(table)
        actual_index_names = {idx['name'] for idx in actual_indexes}

        logger.info(f"\n  Table: {table}")
        for idx in expected_indexes:
            if idx in actual_index_names:
                logger.info(f"    ✓ {idx}")
            else:
                logger.warning(f"    ✗ {idx} (missing)")
                all_ok = False

    return all_ok


def verify_constraints(engine):
    """Verify CHECK constraints"""
    inspector = inspect(engine)

    logger.info("\n🔒 Verifying CHECK constraints...")

    # Check constraints are database-specific
    # PostgreSQL: can query pg_constraint
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT
                    conrelid::regclass AS table_name,
                    conname AS constraint_name
                FROM pg_constraint
                WHERE conrelid::regclass::text LIKE '%exercise%'
                    OR conrelid::regclass::text LIKE '%subject%'
                ORDER BY table_name, constraint_name
            """))

            constraints = result.fetchall()
            if constraints:
                logger.info("  Found CHECK constraints:")
                for table, constraint in constraints:
                    logger.info(f"    ✓ {table}.{constraint}")
            else:
                logger.warning("  No CHECK constraints found (might be database-specific)")

    except Exception as e:
        logger.warning(f"  Could not verify constraints: {e}")


def main():
    """Main migration function"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
    else:
        command = "migrate"

    engine = get_engine()

    if command == "migrate":
        logger.info("="* 60)
        logger.info("MIGRATION: Creating exercise tables")
        logger.info("=" * 60)

        if create_tables(engine):
            logger.info("\n" + "=" * 60)
            logger.info("VERIFICATION")
            logger.info("=" * 60)
            verify_tables_exist(engine)
            verify_indexes(engine)
            verify_constraints(engine)
            logger.info("\n✅ Migration completed successfully!")
        else:
            logger.error("\n❌ Migration failed!")
            sys.exit(1)

    elif command == "rollback":
        logger.info("=" * 60)
        logger.info("ROLLBACK: Dropping exercise tables")
        logger.info("=" * 60)

        if drop_tables(engine):
            logger.info("\n✅ Rollback completed successfully!")
        else:
            logger.error("\n❌ Rollback failed!")
            sys.exit(1)

    elif command == "verify":
        logger.info("=" * 60)
        logger.info("VERIFICATION: Checking exercise tables")
        logger.info("=" * 60)

        if verify_tables_exist(engine):
            verify_indexes(engine)
            verify_constraints(engine)
            logger.info("\n✅ Verification passed!")
        else:
            logger.error("\n❌ Verification failed - some tables are missing!")
            sys.exit(1)

    else:
        logger.error(f"Unknown command: {command}")
        logger.info("Usage: python -m backend.database.migrations.add_exercises_tables [migrate|rollback|verify]")
        sys.exit(1)


if __name__ == "__main__":
    main()
