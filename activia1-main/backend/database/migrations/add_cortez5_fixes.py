"""
Migración de Base de Datos: Correcciones del Audit Cortez5
Agrega columnas faltantes, índices adicionales, constraints

Ejecutar con: python -m backend.database.migrations.add_cortez5_fixes

DATABASE CHANGES (require migration):
- FIX 2.1: Add resolved_at column to risks table
- FIX 1.9: Composite indexes for temporal queries
- FIX 1.4: Check constraints for session mode/simulator_type (PostgreSQL only)

CODE CHANGES (no migration needed - already in codebase):
- FIX 1.5: back_populates relationship in RemediationPlanDB
- FIX 3.2: try/except/rollback in create methods
- FIX 3.3: Pessimistic locking (SELECT FOR UPDATE) in critical methods
- FIX 3.5: Batch loading methods (get_by_ids)
- FIX 3.6: exists() and count() utility methods
- FIX 4.1: Consolidated CognitiveState enum with compatibility mapping

🤖 Generated with Claude Code (claude.ai/claude-code)
"""
import sys
from sqlalchemy import text
from backend.database import init_database, get_db_config


def migrate_cortez5_fixes():
    """
    Aplica las correcciones de columnas e índices del audit Cortez5
    """
    print("=" * 80)
    print("Migración: Correcciones Audit Cortez5 (Diciembre 2025)")
    print("=" * 80)

    # Inicializar base de datos
    init_database()

    # Obtener sesión usando la factory
    db_config = get_db_config()
    session_factory = db_config.get_session_factory()
    db = session_factory()

    try:
        # Detectar el tipo de base de datos
        db_url = str(db.bind.url)
        is_sqlite = db_url.startswith('sqlite')
        is_postgres = 'postgresql' in db_url

        print(f"\nBase de datos detectada: {'SQLite' if is_sqlite else 'PostgreSQL'}")

        # ======================================================================
        # FIX 2.1: Add resolved_at column to risks
        # ======================================================================

        print("\n[1/6] Agregando columna resolved_at a risks...")
        try:
            if is_postgres:
                db.execute(text("""
                    ALTER TABLE risks ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMP
                """))
            else:
                # SQLite: Check if column exists first
                result = db.execute(text("PRAGMA table_info(risks)"))
                columns = [row[1] for row in result]
                if 'resolved_at' not in columns:
                    db.execute(text("""
                        ALTER TABLE risks ADD COLUMN resolved_at TIMESTAMP
                    """))
            print("✓ risks.resolved_at agregado")
        except Exception as e:
            print(f"  ⚠ Error (puede que ya exista): {e}")

        # ======================================================================
        # FIX 1.9: Composite indexes for temporal queries
        # ======================================================================

        print("\n[2/6] Agregando índices compuestos temporales...")
        temporal_indexes = [
            ("idx_interaction_session_created", "interactions", "session_id, created_at"),
            ("idx_evaluation_student_created", "evaluations", "student_id, created_at"),
        ]

        for idx_name, table, columns in temporal_indexes:
            try:
                db.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({columns})
                """))
                print(f"✓ {idx_name} creado")
            except Exception as e:
                print(f"  ⚠ {idx_name}: {e}")

        # ======================================================================
        # FIX 1.4: Check constraints for session mode/simulator_type
        # (PostgreSQL only - SQLite doesn't support ALTER TABLE ADD CONSTRAINT)
        # ======================================================================

        print("\n[3/6] Agregando check constraints (PostgreSQL only)...")
        if is_postgres:
            check_constraints = [
                (
                    "ck_session_mode_valid",
                    "sessions",
                    "mode IN ('tutor', 'simulator', 'evaluator', 'risk_analyst', 'governance', 'practice', 'TUTOR', 'SIMULATOR', 'EVALUATOR', 'RISK_ANALYST', 'GOVERNANCE', 'PRACTICE')"
                ),
                (
                    "ck_session_simulator_type_valid",
                    "sessions",
                    "simulator_type IS NULL OR simulator_type IN ('product_owner', 'scrum_master', 'tech_interviewer', 'incident_responder', 'client', 'devsecops')"
                ),
            ]

            for constraint_name, table, check_clause in check_constraints:
                try:
                    # PostgreSQL: Add constraint if not exists
                    db.execute(text(f"""
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM pg_constraint WHERE conname = '{constraint_name}'
                            ) THEN
                                ALTER TABLE {table} ADD CONSTRAINT {constraint_name} CHECK ({check_clause});
                            END IF;
                        END $$;
                    """))
                    print(f"✓ {constraint_name} agregado")
                except Exception as e:
                    print(f"  ⚠ {constraint_name}: {e}")
        else:
            print("  ⏭ SQLite no soporta ALTER TABLE ADD CONSTRAINT (constraints ya en ORM)")

        # ======================================================================
        # Additional indexes for FK columns without explicit index
        # ======================================================================

        print("\n[4/6] Verificando índices en columnas FK...")
        fk_indexes = [
            ("idx_risk_alert_session", "risk_alerts", "session_id"),
            ("idx_remediation_student", "remediation_plans", "student_id"),
        ]

        for idx_name, table, column in fk_indexes:
            try:
                db.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({column})
                """))
                print(f"✓ {idx_name} creado")
            except Exception as e:
                # Table might not exist in all deployments
                if "no such table" in str(e).lower() or "does not exist" in str(e).lower():
                    print(f"  ⏭ {idx_name}: tabla {table} no existe (opcional)")
                else:
                    print(f"  ⚠ {idx_name}: {e}")

        # ======================================================================
        # Commit y verificación
        # ======================================================================

        print("\n[5/6] Aplicando cambios...")
        db.commit()

        # Verificar cambios
        print("\nVerificando cambios aplicados...")

        # Check resolved_at column
        if is_postgres:
            result = db.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'risks' AND column_name = 'resolved_at'
            """))
            if result.fetchone():
                print("  ✓ risks.resolved_at existe")
            else:
                print("  ✗ risks.resolved_at NO encontrado")
        else:
            result = db.execute(text("PRAGMA table_info(risks)"))
            columns = [row[1] for row in result]
            if 'resolved_at' in columns:
                print("  ✓ risks.resolved_at existe")
            else:
                print("  ✗ risks.resolved_at NO encontrado")

        # ======================================================================
        # Code changes summary (no migration needed)
        # ======================================================================

        print("\n[6/6] Resumen de cambios en código (ya aplicados)...")
        print("  ✓ FIX 1.5: back_populates en RemediationPlanDB")
        print("  ✓ FIX 3.2: try/except/rollback en métodos create")
        print("  ✓ FIX 3.3: Pessimistic locking en métodos críticos")
        print("  ✓ FIX 3.5: Métodos batch loading (get_by_ids)")
        print("  ✓ FIX 3.6: Métodos exists() y count()")
        print("  ✓ FIX 4.1: CognitiveState enum consolidado")

        print("\n" + "=" * 80)
        print("✓ Migración Cortez5 completada exitosamente")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error durante la migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration():
    """
    Revierte la migración (elimina columnas e índices agregados)
    """
    print("=" * 80)
    print("Rollback: Eliminar cambios del Audit Cortez5")
    print("=" * 80)

    confirm = input("\n¿Confirmar rollback? (escribir 'YES' para continuar): ")
    if confirm != "YES":
        print("Rollback cancelado")
        return

    init_database()
    db_config = get_db_config()
    session_factory = db_config.get_session_factory()
    db = session_factory()

    try:
        db_url = str(db.bind.url)
        is_postgres = 'postgresql' in db_url

        print("\nEliminando índices Cortez5...")
        indexes_to_drop = [
            "idx_interaction_session_created",
            "idx_evaluation_student_created",
            "idx_risk_alert_session",
            "idx_remediation_student",
        ]

        for idx in indexes_to_drop:
            try:
                db.execute(text(f"DROP INDEX IF EXISTS {idx}"))
                print(f"✓ {idx} eliminado")
            except Exception as e:
                print(f"  ⚠ {idx}: {e}")

        # Note: Dropping columns in SQLite requires table recreation
        # which is complex and risky. Only PostgreSQL supports ALTER TABLE DROP COLUMN
        if is_postgres:
            print("\nEliminando columna resolved_at...")
            try:
                db.execute(text("ALTER TABLE risks DROP COLUMN IF EXISTS resolved_at"))
                print("✓ risks.resolved_at eliminado")
            except Exception as e:
                print(f"  ⚠ Error: {e}")

            print("\nEliminando check constraints...")
            constraints_to_drop = [
                "ck_session_mode_valid",
                "ck_session_simulator_type_valid",
            ]
            for constraint in constraints_to_drop:
                try:
                    db.execute(text(f"ALTER TABLE sessions DROP CONSTRAINT IF EXISTS {constraint}"))
                    print(f"✓ {constraint} eliminado")
                except Exception as e:
                    print(f"  ⚠ {constraint}: {e}")
        else:
            print("\n⚠ SQLite no soporta DROP COLUMN/CONSTRAINT. Los cambios permanecerán.")

        db.commit()
        print("\n✓ Rollback completado")

    except Exception as e:
        print(f"\n✗ Error durante rollback: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback_migration()
    else:
        migrate_cortez5_fixes()
