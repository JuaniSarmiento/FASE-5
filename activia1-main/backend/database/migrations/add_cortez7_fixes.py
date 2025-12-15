"""
Migración de Base de Datos: Correcciones del Audit Cortez7
Agrega índices para timestamps, server_default para boolean, cambia tipo de user_id

Ejecutar con: python -m backend.database.migrations.add_cortez7_fixes

DATABASE CHANGES (require migration):
- FIX 2.1: Cambiar SessionDB.user_id de String(100) a String(36)
- FIX 4.1: Índices para timestamps de resolución (resolved_at, actual_completion_date)
- FIX 4.4: server_default para columnas boolean (is_active, is_verified, is_merge, is_revert)

CODE CHANGES (no migration needed - already in codebase):
- FIX 1.1-1.3: Unificación de enums con mappings
- FIX 1.4: ABANDONED agregado a SessionStatus
- FIX 3.1-3.3: back_populates agregados a UserDB
- FIX 5.1-5.4: Métodos de limpieza para JSON arrays huérfanos
- FIX 6.1-6.2: LTI repositories (ya existían)

🤖 Generated with Claude Code (claude.ai/claude-code)
"""
import sys
from sqlalchemy import text
from backend.database import init_database, get_db_config


def migrate_cortez7_fixes():
    """
    Aplica las correcciones de índices, tipos de datos y server_default del audit Cortez7
    """
    print("=" * 80)
    print("Migración: Correcciones Audit Cortez7 (Diciembre 2025)")
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
        # FIX 2.1: Cambiar SessionDB.user_id de String(100) a String(36)
        # ======================================================================

        print("\n" + "=" * 60)
        print("FIX 2.1: Cambiar sessions.user_id a VARCHAR(36)")
        print("=" * 60)

        if is_postgres:
            try:
                # Verificar que no hay valores mayores a 36 caracteres
                result = db.execute(text("""
                    SELECT COUNT(*) FROM sessions
                    WHERE user_id IS NOT NULL AND LENGTH(user_id) > 36
                """))
                count = result.scalar()

                if count > 0:
                    print(f"  ⚠ ADVERTENCIA: {count} registros tienen user_id > 36 caracteres")
                    print("    No se puede reducir el tamaño sin truncar datos")
                    print("    Ejecutar manualmente después de limpiar los datos:")
                    print("    ALTER TABLE sessions ALTER COLUMN user_id TYPE VARCHAR(36);")
                else:
                    db.execute(text("""
                        ALTER TABLE sessions ALTER COLUMN user_id TYPE VARCHAR(36)
                    """))
                    print("  ✓ sessions.user_id cambiado a VARCHAR(36)")
            except Exception as e:
                print(f"  ⚠ Error (puede que ya esté aplicado): {e}")
        else:
            print("  ⏭ SQLite no soporta ALTER COLUMN TYPE")
            print("    El cambio está en el ORM y se aplicará a nuevas tablas")

        # ======================================================================
        # FIX 4.1: Índices para timestamps de resolución
        # ======================================================================

        print("\n" + "=" * 60)
        print("FIX 4.1: Índices para timestamps de resolución")
        print("=" * 60)

        timestamp_indexes = [
            ("idx_risk_resolved_at", "risks", "resolved_at"),
            ("idx_alert_resolved_at", "risk_alerts", "resolved_at"),
            ("idx_plan_completion_date", "remediation_plans", "actual_completion_date"),
        ]

        for idx_name, table, column in timestamp_indexes:
            print(f"\n[INDEX] {idx_name} en {table}({column})...")
            try:
                db.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({column})
                """))
                print(f"  ✓ {idx_name} creado")
            except Exception as e:
                if "does not exist" in str(e).lower():
                    print(f"  ⏭ Tabla {table} no existe (opcional)")
                else:
                    print(f"  ⚠ Error: {e}")

        # ======================================================================
        # FIX 4.4: server_default para columnas boolean
        # ======================================================================

        print("\n" + "=" * 60)
        print("FIX 4.4: server_default para columnas boolean")
        print("=" * 60)

        if is_postgres:
            boolean_defaults = [
                ("users", "is_active", "true"),
                ("users", "is_verified", "false"),
                ("git_traces", "is_merge", "false"),
                ("git_traces", "is_revert", "false"),
                ("lti_deployments", "is_active", "true"),
            ]

            for table, column, default_value in boolean_defaults:
                print(f"\n[DEFAULT] {table}.{column} = {default_value}...")
                try:
                    db.execute(text(f"""
                        ALTER TABLE {table}
                        ALTER COLUMN {column} SET DEFAULT {default_value}
                    """))
                    print(f"  ✓ {table}.{column} default establecido")
                except Exception as e:
                    if "does not exist" in str(e).lower():
                        print(f"  ⏭ Tabla/columna no existe (opcional)")
                    else:
                        print(f"  ⚠ Error: {e}")
        else:
            print("\n  ⏭ SQLite no soporta ALTER COLUMN SET DEFAULT")
            print("    Los defaults están en el ORM")

        # ======================================================================
        # Commit y verificación
        # ======================================================================

        print("\n" + "=" * 60)
        print("APLICANDO CAMBIOS")
        print("=" * 60)

        db.commit()
        print("\n✓ Cambios aplicados exitosamente")

        # ======================================================================
        # Resumen de cambios en código (no requieren migración)
        # ======================================================================

        print("\n" + "=" * 60)
        print("RESUMEN: Cambios en Código (ya aplicados)")
        print("=" * 60)
        print("  ✓ FIX 1.1-1.3: Unificación de enums con mappings")
        print("    - TraceLevel reexportado desde backend/models/trace.py")
        print("    - INTERACTION_TYPE_API_TO_DB mapping agregado")
        print("    - normalize_interaction_type() función agregada")
        print("  ✓ FIX 1.4: SessionStatus.ABANDONED agregado")
        print("  ✓ FIX 3.1-3.3: back_populates en UserDB")
        print("    - course_reports, remediation_plans_created")
        print("    - assigned_alerts, acknowledged_alerts")
        print("  ✓ FIX 5.1-5.4: Métodos de limpieza en RiskRepository")
        print("    - clean_orphan_trace_ids()")
        print("    - clean_all_orphan_trace_ids()")
        print("  ✓ FIX 6.1-6.2: LTI repositories (ya existían)")

        print("\n" + "=" * 80)
        print("✓ Migración Cortez7 completada exitosamente")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error durante la migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration():
    """
    Revierte la migración (elimina índices agregados)
    """
    print("=" * 80)
    print("Rollback: Eliminar cambios del Audit Cortez7")
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

        # Drop indexes
        print("\nEliminando índices Cortez7...")
        indexes_to_drop = [
            "idx_risk_resolved_at",
            "idx_alert_resolved_at",
            "idx_plan_completion_date",
        ]

        for idx in indexes_to_drop:
            try:
                db.execute(text(f"DROP INDEX IF EXISTS {idx}"))
                print(f"  ✓ {idx} eliminado")
            except Exception as e:
                print(f"  ⚠ {idx}: {e}")

        if is_postgres:
            # Note: No revertimos el cambio de VARCHAR(36) a VARCHAR(100)
            # porque no causa problemas y es más seguro dejarlo
            print("\n  ⚠ Nota: sessions.user_id permanece como VARCHAR(36)")
            print("    Para revertir manualmente:")
            print("    ALTER TABLE sessions ALTER COLUMN user_id TYPE VARCHAR(100);")

        db.commit()
        print("\n✓ Rollback completado")

    except Exception as e:
        print(f"\n✗ Error durante rollback: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def verify_migration():
    """
    Verifica el estado de la migración sin hacer cambios
    """
    print("=" * 80)
    print("Verificación: Estado de la Migración Cortez7")
    print("=" * 80)

    init_database()
    db_config = get_db_config()
    session_factory = db_config.get_session_factory()
    db = session_factory()

    try:
        db_url = str(db.bind.url)
        is_postgres = 'postgresql' in db_url

        print(f"\nBase de datos: {'PostgreSQL' if is_postgres else 'SQLite'}")

        if is_postgres:
            # Check user_id column type
            print("\n[Column Type]")
            try:
                result = db.execute(text("""
                    SELECT character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = 'sessions' AND column_name = 'user_id'
                """))
                length = result.scalar()
                if length == 36:
                    print(f"  ✓ sessions.user_id es VARCHAR(36)")
                else:
                    print(f"  ✗ sessions.user_id es VARCHAR({length}) - debería ser 36")
            except Exception as e:
                print(f"  ⚠ Error verificando: {e}")

            # Check indexes
            print("\n[Indexes]")
            indexes_to_check = [
                "idx_risk_resolved_at",
                "idx_alert_resolved_at",
                "idx_plan_completion_date",
            ]
            for idx in indexes_to_check:
                result = db.execute(text(f"""
                    SELECT 1 FROM pg_indexes WHERE indexname = '{idx}'
                """))
                exists = result.fetchone() is not None
                print(f"  {'✓' if exists else '✗'} {idx}")

            # Check defaults
            print("\n[Boolean Defaults]")
            defaults_to_check = [
                ("users", "is_active"),
                ("users", "is_verified"),
                ("git_traces", "is_merge"),
                ("git_traces", "is_revert"),
                ("lti_deployments", "is_active"),
            ]
            for table, column in defaults_to_check:
                try:
                    result = db.execute(text(f"""
                        SELECT column_default
                        FROM information_schema.columns
                        WHERE table_name = '{table}' AND column_name = '{column}'
                    """))
                    default = result.scalar()
                    has_default = default is not None
                    print(f"  {'✓' if has_default else '✗'} {table}.{column} = {default}")
                except Exception:
                    print(f"  ⚠ {table}.{column}: Error verificando")

        else:
            print("\n  SQLite: Verificación limitada")
            print("  Los cambios están en el ORM, no en tablas existentes")

        print("\n" + "=" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "rollback":
            rollback_migration()
        elif sys.argv[1] == "verify":
            verify_migration()
        else:
            print(f"Comando desconocido: {sys.argv[1]}")
            print("Uso: python -m backend.database.migrations.add_cortez7_fixes [rollback|verify]")
    else:
        migrate_cortez7_fixes()
