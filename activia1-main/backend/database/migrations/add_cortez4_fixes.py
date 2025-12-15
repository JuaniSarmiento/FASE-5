"""
Migración de Base de Datos: Correcciones del Audit Cortez4
Agrega índices compuestos, GIN indexes, CASCADE en FKs, y check constraints

Ejecutar con: python -m backend.database.migrations.add_cortez4_fixes

Changes (FIX references from cortez4):
- FIX 1.1.1-1.1.5: Composite indexes for common query patterns
- FIX 1.2.1-1.2.6: GIN indexes for JSONB N4 dimension columns (PostgreSQL only)
- FIX 1.3.1-1.3.5: CASCADE DELETE on session_id FKs
- FIX 1.4: GitTraceDB unique constraint change
- FIX 1.6.1-1.6.3: Check constraints for enum columns
- FIX 1.8.1-1.8.2: Server defaults for login_count and resolved

🤖 Generated with Claude Code (claude.ai/claude-code)
"""
import sys
from sqlalchemy import text
from backend.database import init_database, get_db_config


def migrate_cortez4_fixes():
    """
    Aplica las correcciones de índices, FKs y constraints del audit Cortez4
    """
    print("=" * 80)
    print("Migración: Correcciones Audit Cortez4 (Diciembre 2025)")
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
        # FIX 1.1.1-1.1.5: Composite indexes for common query patterns
        # ======================================================================

        print("\n[1/10] Agregando índices compuestos para RiskDB...")
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_risk_session_resolved
                ON risks (session_id, resolved)
            """))
            print("✓ idx_risk_session_resolved creado")
        except Exception as e:
            print(f"  ⚠ Error: {e}")

        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_risk_session_level
                ON risks (session_id, risk_level)
            """))
            print("✓ idx_risk_session_level creado")
        except Exception as e:
            print(f"  ⚠ Error: {e}")

        print("\n[2/10] Agregando índice compuesto para EvaluationDB...")
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_eval_session_created
                ON evaluations (session_id, created_at)
            """))
            print("✓ idx_eval_session_created creado")
        except Exception as e:
            print(f"  ⚠ Error: {e}")

        # ======================================================================
        # FIX 1.2.1-1.2.6: GIN indexes for JSONB columns (PostgreSQL only)
        # ======================================================================

        print("\n[3/10] Agregando GIN indexes para columnas JSONB N4...")
        if is_postgres:
            gin_indexes = [
                ("idx_trace_semantic_gin", "semantic_understanding"),
                ("idx_trace_algorithmic_gin", "algorithmic_evolution"),
                ("idx_trace_cognitive_gin", "cognitive_reasoning"),
                ("idx_trace_interactional_gin", "interactional_data"),
                ("idx_trace_ethical_gin", "ethical_risk_data"),
                ("idx_trace_process_gin", "process_data"),
            ]

            for idx_name, column in gin_indexes:
                try:
                    db.execute(text(f"""
                        CREATE INDEX IF NOT EXISTS {idx_name}
                        ON cognitive_traces USING gin ({column})
                    """))
                    print(f"✓ {idx_name} (GIN) creado")
                except Exception as e:
                    print(f"  ⚠ {idx_name}: {e}")
        else:
            print("  ⏭ Saltando GIN indexes (solo disponibles en PostgreSQL)")

        # ======================================================================
        # FIX 1.3.1-1.3.5: CASCADE DELETE on session_id FKs
        # ======================================================================

        print("\n[4/10] Actualizando FK en cognitive_traces con CASCADE DELETE...")
        if is_postgres:
            try:
                db.execute(text("""
                    ALTER TABLE cognitive_traces
                    DROP CONSTRAINT IF EXISTS cognitive_traces_session_id_fkey
                """))
                db.execute(text("""
                    ALTER TABLE cognitive_traces
                    ADD CONSTRAINT cognitive_traces_session_id_fkey
                    FOREIGN KEY (session_id)
                    REFERENCES sessions(id)
                    ON DELETE CASCADE
                """))
                print("✓ FK cognitive_traces_session_id_fkey actualizado con CASCADE")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta ALTER TABLE ADD CONSTRAINT)")

        print("\n[5/10] Actualizando FK en risks con CASCADE DELETE...")
        if is_postgres:
            try:
                db.execute(text("""
                    ALTER TABLE risks
                    DROP CONSTRAINT IF EXISTS risks_session_id_fkey
                """))
                db.execute(text("""
                    ALTER TABLE risks
                    ADD CONSTRAINT risks_session_id_fkey
                    FOREIGN KEY (session_id)
                    REFERENCES sessions(id)
                    ON DELETE CASCADE
                """))
                print("✓ FK risks_session_id_fkey actualizado con CASCADE")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta ALTER TABLE ADD CONSTRAINT)")

        print("\n[6/10] Actualizando FK en evaluations con CASCADE DELETE...")
        if is_postgres:
            try:
                db.execute(text("""
                    ALTER TABLE evaluations
                    DROP CONSTRAINT IF EXISTS evaluations_session_id_fkey
                """))
                db.execute(text("""
                    ALTER TABLE evaluations
                    ADD CONSTRAINT evaluations_session_id_fkey
                    FOREIGN KEY (session_id)
                    REFERENCES sessions(id)
                    ON DELETE CASCADE
                """))
                print("✓ FK evaluations_session_id_fkey actualizado con CASCADE")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta ALTER TABLE ADD CONSTRAINT)")

        # ======================================================================
        # FIX 1.4: GitTraceDB unique constraint change
        # ======================================================================

        print("\n[7/10] Actualizando constraint en git_traces...")
        if is_postgres:
            try:
                # Remove old unique constraint on commit_hash if exists
                db.execute(text("""
                    ALTER TABLE git_traces
                    DROP CONSTRAINT IF EXISTS git_traces_commit_hash_key
                """))
                # Add new composite unique constraint
                db.execute(text("""
                    ALTER TABLE git_traces
                    ADD CONSTRAINT uq_git_trace_session_commit
                    UNIQUE (session_id, commit_hash)
                """))
                print("✓ Unique constraint actualizado a (session_id, commit_hash)")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            try:
                # SQLite: Create unique index instead
                db.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS uq_git_trace_session_commit
                    ON git_traces (session_id, commit_hash)
                """))
                print("✓ Unique index uq_git_trace_session_commit creado")
            except Exception as e:
                print(f"  ⚠ Error: {e}")

        # ======================================================================
        # FIX 1.6.1-1.6.3: Check constraints for enum columns
        # ======================================================================

        print("\n[8/10] Agregando check constraints para enums...")
        if is_postgres:
            check_constraints = [
                ("ck_risk_level_valid", "risks",
                 "risk_level IN ('low', 'medium', 'high', 'critical', 'info')"),
                ("ck_session_status_valid", "sessions",
                 "status IN ('active', 'completed', 'paused', 'aborted', 'abandoned')"),
                ("ck_trace_level_valid", "cognitive_traces",
                 "trace_level IN ('n1_superficial', 'n2_tecnico', 'n3_interaccional', 'n4_cognitivo')"),
            ]

            for ck_name, table, condition in check_constraints:
                try:
                    # First try to drop if exists
                    db.execute(text(f"""
                        ALTER TABLE {table}
                        DROP CONSTRAINT IF EXISTS {ck_name}
                    """))
                    # Then add the constraint
                    db.execute(text(f"""
                        ALTER TABLE {table}
                        ADD CONSTRAINT {ck_name}
                        CHECK ({condition})
                    """))
                    print(f"✓ {ck_name} creado en {table}")
                except Exception as e:
                    print(f"  ⚠ {ck_name}: {e}")
        else:
            print("  ⏭ Saltando check constraints (SQLite tiene soporte limitado)")

        # ======================================================================
        # FIX 1.8.1-1.8.2: Server defaults
        # ======================================================================

        print("\n[9/10] Configurando server defaults...")
        if is_postgres:
            try:
                db.execute(text("""
                    ALTER TABLE users
                    ALTER COLUMN login_count SET DEFAULT 0
                """))
                print("✓ Server default para users.login_count configurado")
            except Exception as e:
                print(f"  ⚠ Error: {e}")

            try:
                db.execute(text("""
                    ALTER TABLE risks
                    ALTER COLUMN resolved SET DEFAULT false
                """))
                print("✓ Server default para risks.resolved configurado")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta ALTER COLUMN SET DEFAULT)")

        # ======================================================================
        # Verificación final
        # ======================================================================

        print("\n[10/10] Verificando cambios...")
        db.commit()

        if is_postgres:
            # Verificar índices
            result = db.execute(text("""
                SELECT indexname, tablename FROM pg_indexes
                WHERE schemaname = 'public'
                AND indexname LIKE 'idx_%'
                ORDER BY tablename, indexname
            """))
            print("\nÍndices Cortez4 verificados:")
            cortez4_indexes = [
                'idx_risk_session_resolved', 'idx_risk_session_level',
                'idx_eval_session_created', 'idx_trace_semantic_gin',
                'idx_trace_algorithmic_gin', 'idx_trace_cognitive_gin',
                'idx_trace_interactional_gin', 'idx_trace_ethical_gin',
                'idx_trace_process_gin'
            ]
            for row in result:
                if row.indexname in cortez4_indexes:
                    print(f"  ✓ {row.indexname} en {row.tablename}")
        else:
            result = db.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type = 'index'
                AND name LIKE 'idx_%'
                ORDER BY name
            """))
            print("\nÍndices creados:")
            for row in result:
                print(f"  - {row[0]}")

        print("\n" + "=" * 80)
        print("✓ Migración Cortez4 completada exitosamente")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error durante la migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration():
    """
    Revierte la migración (elimina los índices agregados)
    Nota: No revierte CASCADE DELETE ya que es una corrección de integridad
    """
    print("=" * 80)
    print("Rollback: Eliminar índices y constraints del Audit Cortez4")
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

        print("\nEliminando índices Cortez4...")
        indexes_to_drop = [
            "idx_risk_session_resolved",
            "idx_risk_session_level",
            "idx_eval_session_created",
            "idx_trace_semantic_gin",
            "idx_trace_algorithmic_gin",
            "idx_trace_cognitive_gin",
            "idx_trace_interactional_gin",
            "idx_trace_ethical_gin",
            "idx_trace_process_gin",
        ]

        for idx in indexes_to_drop:
            try:
                db.execute(text(f"DROP INDEX IF EXISTS {idx}"))
                print(f"✓ {idx} eliminado")
            except Exception as e:
                print(f"  ⚠ {idx}: {e}")

        if is_postgres:
            print("\nEliminando check constraints...")
            constraints_to_drop = [
                ("ck_risk_level_valid", "risks"),
                ("ck_session_status_valid", "sessions"),
                ("ck_trace_level_valid", "cognitive_traces"),
            ]

            for ck_name, table in constraints_to_drop:
                try:
                    db.execute(text(f"""
                        ALTER TABLE {table}
                        DROP CONSTRAINT IF EXISTS {ck_name}
                    """))
                    print(f"✓ {ck_name} eliminado de {table}")
                except Exception as e:
                    print(f"  ⚠ {ck_name}: {e}")

        db.commit()
        print("\n✓ Rollback completado")
        print("\nNota: Las constraints CASCADE DELETE NO se revirtieron")
        print("porque son correcciones de integridad de datos.")

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
        migrate_cortez4_fixes()
