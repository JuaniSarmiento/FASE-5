"""
Migration script: Make RiskDB.session_id required (nullable=False)

PROBLEM:
- RiskDB.session_id actualmente permite NULL en la base de datos
- Un riesgo sin session_id carece de contexto válido (no se puede determinar:
  el momento en que ocurrió, las trazas relacionadas, ni el flujo cognitivo)

SOLUTION:
1. Verificar si existen riesgos con session_id NULL
2. Si existen, intentar inferir session_id desde trace_ids
3. Si no se puede inferir, marcar como "orphan_session" (requiere revisión manual)
4. Luego, en la base de datos, cambiar columna a NOT NULL

USAGE:
    python scripts/migrate_risk_session_id_required.py

ENVIRONMENT:
    DATABASE_URL=sqlite:///ai_native.db (or PostgreSQL URL)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from backend.database import get_db_session
from backend.database.config import DatabaseConfig
from backend.database.models import RiskDB, CognitiveTraceDB
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_risks_session_id():
    """
    Migrate risks with NULL session_id

    Steps:
    1. Find all risks with session_id NULL
    2. Try to infer session_id from trace_ids
    3. If not possible, assign "orphan_session_{student_id}"
    4. Update database
    """
    logger.info("=" * 80)
    logger.info("Migration: Make RiskDB.session_id REQUIRED (nullable=False)")
    logger.info("=" * 80)

    with get_db_session() as db:
        # Step 1: Count risks with NULL session_id
        null_count = db.query(RiskDB).filter(RiskDB.session_id == None).count()

        if null_count == 0:
            logger.info("✅ No risks with NULL session_id found. Migration not needed.")
            logger.info("All risks have valid session_id. Database is consistent.")
            return

        logger.warning(f"⚠️  Found {null_count} risks with NULL session_id")
        logger.info("Attempting to infer session_id from trace_ids...")

        # Step 2: Get all risks with NULL session_id
        orphan_risks = db.query(RiskDB).filter(RiskDB.session_id == None).all()

        fixed_count = 0
        orphaned_count = 0

        for risk in orphan_risks:
            # Try to infer session_id from trace_ids
            if risk.trace_ids and len(risk.trace_ids) > 0:
                # Get session_id from first trace
                first_trace_id = risk.trace_ids[0]
                trace = db.query(CognitiveTraceDB).filter(
                    CognitiveTraceDB.id == first_trace_id
                ).first()

                if trace and trace.session_id:
                    risk.session_id = trace.session_id
                    logger.info(
                        f"  ✅ Risk {risk.id}: Inferred session_id='{trace.session_id}' from trace {first_trace_id}"
                    )
                    fixed_count += 1
                else:
                    # Cannot infer, create orphan session ID
                    orphan_session_id = f"orphan_session_{risk.student_id}_{risk.created_at.strftime('%Y%m%d')}"
                    risk.session_id = orphan_session_id
                    logger.warning(
                        f"  ⚠️  Risk {risk.id}: Created orphan session '{orphan_session_id}' (manual review needed)"
                    )
                    orphaned_count += 1
            else:
                # No trace_ids, create orphan session ID
                orphan_session_id = f"orphan_session_{risk.student_id}_{risk.created_at.strftime('%Y%m%d')}"
                risk.session_id = orphan_session_id
                logger.warning(
                    f"  ⚠️  Risk {risk.id}: Created orphan session '{orphan_session_id}' (no trace_ids, manual review needed)"
                )
                orphaned_count += 1

        # Step 3: Commit changes
        try:
            db.commit()
            logger.info("=" * 80)
            logger.info("✅ Migration completed successfully")
            logger.info(f"  - Total risks migrated: {null_count}")
            logger.info(f"  - Fixed (session_id inferred): {fixed_count}")
            logger.info(f"  - Orphaned (manual review needed): {orphaned_count}")

            if orphaned_count > 0:
                logger.warning("⚠️  Some risks were orphaned and need manual review:")
                logger.warning("  Look for sessions starting with 'orphan_session_'")

        except Exception as e:
            db.rollback()
            logger.error(f"❌ Migration failed: {e}")
            raise

    # Step 4: Verify migration
    logger.info("=" * 80)
    logger.info("Verifying migration...")

    with get_db_session() as db:
        remaining_null = db.query(RiskDB).filter(RiskDB.session_id == None).count()

        if remaining_null == 0:
            logger.info("✅ Verification PASSED: All risks now have session_id")
        else:
            logger.error(f"❌ Verification FAILED: {remaining_null} risks still have NULL session_id")

    logger.info("=" * 80)
    logger.info("Migration process completed")
    logger.info("=" * 80)


def verify_database_constraint():
    """
    Verify that the database constraint is properly set

    NOTE: This requires manual SQL for SQLite/PostgreSQL
    """
    logger.info("Checking database constraint status...")

    db_config = DatabaseConfig()
    engine = db_config.engine

    with engine.connect() as conn:
        # Get table info (SQLite specific)
        if "sqlite" in str(engine.url):
            result = conn.execute(text("PRAGMA table_info(risks)"))
            columns = result.fetchall()

            for column in columns:
                if column[1] == "session_id":  # column name
                    is_nullable = column[3] == 0  # notnull: 0=nullable, 1=not nullable
                    if is_nullable:
                        logger.warning(
                            "⚠️  Database constraint: session_id is still NULLABLE in schema"
                        )
                        logger.info("To fix, run manual SQL:")
                        logger.info("  SQLite: Requires table recreation (see SQLite docs)")
                        logger.info("  PostgreSQL: ALTER TABLE risks ALTER COLUMN session_id SET NOT NULL;")
                    else:
                        logger.info("✅ Database constraint: session_id is NOT NULL")
                    break


if __name__ == "__main__":
    try:
        migrate_risks_session_id()
        verify_database_constraint()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
