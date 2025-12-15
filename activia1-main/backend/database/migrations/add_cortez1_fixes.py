"""
Migración de Base de Datos: Correcciones del Audit Cortez1
Agrega FKs, índices y constraints identificados en el audit técnico cortez1

Ejecutar con: python -m backend.database.migrations.add_cortez1_fixes

Changes (FIX references from cortez1):
- FIX 2.1: TraceSequenceDB.session_id FK + index
- FIX 2.2: StudentProfileDB.user_id FK
- FIX 2.3: ActivityDB.teacher_id FK
- FIX 2.5: Additional performance indexes
"""
import sys
from sqlalchemy import text
from backend.database import init_database, get_db_config


def migrate_cortez1_fixes():
    """
    Aplica las correcciones de FKs, índices y constraints del audit Cortez1
    """
    print("=" * 80)
    print("Migración: Correcciones Audit Cortez1 (Diciembre 2025)")
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
        # FIX 2.1: TraceSequenceDB.session_id FK
        # ======================================================================

        print("\n[1/8] Agregando FK para trace_sequences.session_id...")
        if is_postgres:
            try:
                # Check if constraint already exists
                result = db.execute(text("""
                    SELECT 1 FROM information_schema.table_constraints
                    WHERE constraint_name = 'fk_trace_seq_session'
                    AND table_name = 'trace_sequences'
                """))
                if result.fetchone() is None:
                    db.execute(text("""
                        ALTER TABLE trace_sequences
                        ADD CONSTRAINT fk_trace_seq_session
                        FOREIGN KEY (session_id)
                        REFERENCES sessions(id)
                        ON DELETE CASCADE
                    """))
                    print("✓ FK fk_trace_seq_session creado")
                else:
                    print("  ⏭ FK fk_trace_seq_session ya existe")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta ALTER TABLE ADD CONSTRAINT)")

        # ======================================================================
        # FIX 2.1: Index for trace_sequences.session_id
        # ======================================================================

        print("\n[2/8] Agregando índice para trace_sequences.session_id...")
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_trace_seq_session
                ON trace_sequences (session_id)
            """))
            print("✓ idx_trace_seq_session creado")
        except Exception as e:
            print(f"  ⚠ Error (puede que ya exista): {e}")

        # ======================================================================
        # FIX 2.2: StudentProfileDB.user_id FK
        # ======================================================================

        print("\n[3/8] Agregando columna user_id a student_profiles...")
        try:
            # Check if column exists
            if is_postgres:
                result = db.execute(text("""
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'student_profiles' AND column_name = 'user_id'
                """))
            else:
                result = db.execute(text("""
                    SELECT 1 FROM pragma_table_info('student_profiles') WHERE name = 'user_id'
                """))

            if result.fetchone() is None:
                db.execute(text("""
                    ALTER TABLE student_profiles
                    ADD COLUMN user_id VARCHAR(36)
                """))
                print("✓ Columna user_id agregada a student_profiles")
            else:
                print("  ⏭ Columna user_id ya existe en student_profiles")
        except Exception as e:
            print(f"  ⚠ Error: {e}")

        print("\n[4/8] Agregando FK para student_profiles.user_id...")
        if is_postgres:
            try:
                result = db.execute(text("""
                    SELECT 1 FROM information_schema.table_constraints
                    WHERE constraint_name = 'fk_student_profile_user'
                    AND table_name = 'student_profiles'
                """))
                if result.fetchone() is None:
                    db.execute(text("""
                        ALTER TABLE student_profiles
                        ADD CONSTRAINT fk_student_profile_user
                        FOREIGN KEY (user_id)
                        REFERENCES users(id)
                        ON DELETE SET NULL
                    """))
                    print("✓ FK fk_student_profile_user creado")
                else:
                    print("  ⏭ FK fk_student_profile_user ya existe")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta ALTER TABLE ADD CONSTRAINT)")

        # ======================================================================
        # FIX 2.3: ActivityDB.teacher_id FK change to proper FK
        # ======================================================================

        print("\n[5/8] Actualizando teacher_id en activities...")
        if is_postgres:
            try:
                result = db.execute(text("""
                    SELECT 1 FROM information_schema.table_constraints
                    WHERE constraint_name = 'fk_activity_teacher'
                    AND table_name = 'activities'
                """))
                if result.fetchone() is None:
                    # First, update teacher_id column type if needed
                    db.execute(text("""
                        ALTER TABLE activities
                        ADD CONSTRAINT fk_activity_teacher
                        FOREIGN KEY (teacher_id)
                        REFERENCES users(id)
                        ON DELETE SET NULL
                    """))
                    print("✓ FK fk_activity_teacher creado")
                else:
                    print("  ⏭ FK fk_activity_teacher ya existe")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta ALTER TABLE ADD CONSTRAINT)")

        # ======================================================================
        # FIX 2.5: Additional performance indexes
        # ======================================================================

        print("\n[6/8] Agregando índices de rendimiento adicionales...")
        indexes_to_create = [
            ("idx_student_profile_user", "student_profiles", "user_id"),
            ("idx_activity_difficulty", "activities", "difficulty"),
            ("idx_session_user_activity", "sessions", "user_id, activity_id"),
            ("idx_trace_session_created", "cognitive_traces", "session_id, created_at"),
        ]

        for idx_name, table, columns in indexes_to_create:
            try:
                db.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name}
                    ON {table} ({columns})
                """))
                print(f"✓ {idx_name} creado")
            except Exception as e:
                print(f"  ⚠ {idx_name}: {e}")

        # ======================================================================
        # FIX 2.5: Partial index for active sessions (PostgreSQL only)
        # ======================================================================

        print("\n[7/8] Agregando partial index para sesiones activas...")
        if is_postgres:
            try:
                db.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_sessions_active
                    ON sessions (student_id, activity_id)
                    WHERE status = 'active'
                """))
                print("✓ idx_sessions_active (partial) creado")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta partial indexes)")

        # ======================================================================
        # Additional indexes for risks and evaluations
        # ======================================================================

        print("\n[8/8] Agregando índices para risks y evaluations...")
        more_indexes = [
            ("idx_risk_session_level", "risks", "session_id, risk_level"),
            ("idx_risk_resolved", "risks", "session_id, resolved"),
            ("idx_eval_session", "evaluations", "session_id"),
        ]

        for idx_name, table, columns in more_indexes:
            try:
                db.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name}
                    ON {table} ({columns})
                """))
                print(f"✓ {idx_name} creado")
            except Exception as e:
                print(f"  ⚠ {idx_name}: {e}")

        # Commit
        db.commit()

        print("\n" + "=" * 80)
        print("✓ Migración Cortez1 completada exitosamente")
        print("=" * 80)

        # Verificar
        print("\n[Verificación] Consultando índices y FKs...")

        if is_sqlite:
            result = db.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type = 'index'
                ORDER BY name
            """))
            print("\nÍndices creados:")
            for row in result:
                if 'cortez' in row[0].lower() or 'idx_' in row[0]:
                    print(f"  - {row[0]}")
        else:
            result = db.execute(text("""
                SELECT indexname, tablename FROM pg_indexes
                WHERE schemaname = 'public'
                AND (indexname LIKE 'idx_%' OR indexname LIKE 'fk_%')
                ORDER BY tablename, indexname
            """))
            print("\nÍndices por tabla:")
            current_table = None
            for row in result:
                if row.tablename != current_table:
                    current_table = row.tablename
                    print(f"\n  [{current_table}]")
                print(f"    - {row.indexname}")

        print("\n✓ Verificación completa")

    except Exception as e:
        print(f"\n✗ Error durante la migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration():
    """
    Revierte la migración (elimina los índices y FKs agregados)
    """
    print("=" * 80)
    print("Rollback: Eliminar índices y FKs del Audit Cortez1")
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

        print("\nEliminando índices...")
        indexes_to_drop = [
            "idx_trace_seq_session",
            "idx_student_profile_user",
            "idx_activity_difficulty",
            "idx_session_user_activity",
            "idx_trace_session_created",
            "idx_sessions_active",
            "idx_risk_session_level",
            "idx_risk_resolved",
            "idx_eval_session",
        ]

        for idx in indexes_to_drop:
            try:
                db.execute(text(f"DROP INDEX IF EXISTS {idx}"))
                print(f"✓ {idx} eliminado")
            except Exception as e:
                print(f"  ⚠ {idx}: {e}")

        if is_postgres:
            print("\nEliminando FKs...")
            fks_to_drop = [
                ("trace_sequences", "fk_trace_seq_session"),
                ("student_profiles", "fk_student_profile_user"),
                ("activities", "fk_activity_teacher"),
            ]

            for table, fk in fks_to_drop:
                try:
                    db.execute(text(f"""
                        ALTER TABLE {table}
                        DROP CONSTRAINT IF EXISTS {fk}
                    """))
                    print(f"✓ {fk} eliminado de {table}")
                except Exception as e:
                    print(f"  ⚠ {fk}: {e}")

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
        migrate_cortez1_fixes()
