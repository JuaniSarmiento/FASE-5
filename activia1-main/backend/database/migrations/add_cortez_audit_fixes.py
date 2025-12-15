"""
Migración de Base de Datos: Correcciones del Audit Cortez
Agrega índices y constraints identificados en el audit técnico

Ejecutar con: python -m backend.database.migrations.add_cortez_audit_fixes

Changes:
- idx_roles_gin: GIN index for user roles (PostgreSQL only)
- idx_session_created_desc: Index for get_latest_by_session()
- idx_trace_activity: Index for activity_id filtering
- parent_trace_id FK: Foreign key constraint for trace hierarchy
"""
import sys
from sqlalchemy import text
from backend.database import init_database, get_db_config


def migrate_cortez_fixes():
    """
    Aplica las correcciones de índices y constraints del audit Cortez
    """
    print("=" * 80)
    print("Migración: Correcciones Audit Cortez (Diciembre 2025)")
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
        # FIX DB-3: GIN index for roles (PostgreSQL only)
        # ======================================================================

        print("\n[1/5] Agregando GIN index para roles (solo PostgreSQL)...")
        if is_postgres:
            try:
                db.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_roles_gin
                    ON users USING gin (roles)
                """))
                print("✓ idx_roles_gin creado")
            except Exception as e:
                print(f"  ⚠ Error (puede que ya exista): {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta GIN index)")

        # ======================================================================
        # FIX DB-4: Index for get_latest_by_session()
        # ======================================================================

        print("\n[2/5] Agregando índice para get_latest_by_session()...")
        try:
            if is_sqlite:
                db.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_session_created_desc
                    ON cognitive_traces (session_id, created_at)
                """))
            else:
                db.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_session_created_desc
                    ON cognitive_traces (session_id, created_at DESC)
                """))
            print("✓ idx_session_created_desc creado")
        except Exception as e:
            print(f"  ⚠ Error (puede que ya exista): {e}")

        # ======================================================================
        # FIX DB-5: Index for activity_id filtering
        # ======================================================================

        print("\n[3/5] Agregando índice para filtrado por activity_id...")
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_trace_activity
                ON cognitive_traces (activity_id)
            """))
            print("✓ idx_trace_activity creado")
        except Exception as e:
            print(f"  ⚠ Error (puede que ya exista): {e}")

        # ======================================================================
        # FIX MEDIO-4: parent_trace_id foreign key
        # ======================================================================

        print("\n[4/5] Agregando FK para parent_trace_id...")
        if is_postgres:
            try:
                # Check if constraint already exists
                result = db.execute(text("""
                    SELECT 1 FROM information_schema.table_constraints
                    WHERE constraint_name = 'fk_parent_trace'
                    AND table_name = 'cognitive_traces'
                """))
                if result.fetchone() is None:
                    db.execute(text("""
                        ALTER TABLE cognitive_traces
                        ADD CONSTRAINT fk_parent_trace
                        FOREIGN KEY (parent_trace_id)
                        REFERENCES cognitive_traces(id)
                        ON DELETE SET NULL
                    """))
                    print("✓ FK fk_parent_trace creado")
                else:
                    print("  ⏭ FK fk_parent_trace ya existe")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            # SQLite doesn't support adding FK after table creation
            print("  ⏭ Saltando (SQLite no soporta ALTER TABLE ADD CONSTRAINT)")

        # ======================================================================
        # Index on parent_trace_id for hierarchy queries
        # ======================================================================

        print("\n[5/5] Agregando índice para parent_trace_id...")
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_parent_trace
                ON cognitive_traces (parent_trace_id)
            """))
            print("✓ idx_parent_trace creado")
        except Exception as e:
            print(f"  ⚠ Error (puede que ya exista): {e}")

        # Commit
        db.commit()

        print("\n" + "=" * 80)
        print("✓ Migración Cortez completada exitosamente")
        print("=" * 80)

        # Verificar
        print("\n[Verificación] Consultando índices...")

        if is_sqlite:
            result = db.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type = 'index'
                AND tbl_name = 'cognitive_traces'
            """))
            print("\nÍndices en cognitive_traces:")
            for row in result:
                print(f"  - {row[0]}")
        else:
            result = db.execute(text("""
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'cognitive_traces'
                ORDER BY indexname
            """))
            print("\nÍndices en cognitive_traces:")
            for row in result:
                print(f"  - {row.indexname}")

        print("\n✓ Verificación completa")

    except Exception as e:
        print(f"\n✗ Error durante la migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration():
    """
    Revierte la migración (elimina los índices agregados)
    """
    print("=" * 80)
    print("Rollback: Eliminar índices del Audit Cortez")
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
        db.execute(text("DROP INDEX IF EXISTS idx_session_created_desc"))
        db.execute(text("DROP INDEX IF EXISTS idx_trace_activity"))
        db.execute(text("DROP INDEX IF EXISTS idx_parent_trace"))

        if is_postgres:
            db.execute(text("DROP INDEX IF EXISTS idx_roles_gin"))
            db.execute(text("""
                ALTER TABLE cognitive_traces
                DROP CONSTRAINT IF EXISTS fk_parent_trace
            """))

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
        migrate_cortez_fixes()
