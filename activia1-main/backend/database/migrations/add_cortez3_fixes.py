"""
Migración de Base de Datos: Correcciones del Audit Cortez3
Agrega FKs con CASCADE DELETE, índices y constraints identificados en cortez3

Ejecutar con: python -m backend.database.migrations.add_cortez3_fixes

Changes (FIX references from cortez3):
- FIX 3.2: CASCADE DELETE en InterviewSession, IncidentSimulation, SimulatorEvent
- FIX 3.4: Index idx_risk_session_dimension para análisis 5D
- FIX 3.5: Index idx_trace_activity_id para reportes por actividad
- FIX 3.8: Unique constraint en LTISessionDB

🤖 Generated with Claude Code (claude.ai/claude-code)
"""
import sys
from sqlalchemy import text
from backend.database import init_database, get_db_config


def migrate_cortez3_fixes():
    """
    Aplica las correcciones de FKs, índices y constraints del audit Cortez3
    """
    print("=" * 80)
    print("Migración: Correcciones Audit Cortez3 (Diciembre 2025)")
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
        # FIX 3.2: CASCADE DELETE en ForeignKeys
        # ======================================================================

        print("\n[1/6] Actualizando FK en interview_sessions con CASCADE DELETE...")
        if is_postgres:
            try:
                # Drop existing constraint
                db.execute(text("""
                    ALTER TABLE interview_sessions
                    DROP CONSTRAINT IF EXISTS interview_sessions_session_id_fkey
                """))
                # Add new constraint with CASCADE
                db.execute(text("""
                    ALTER TABLE interview_sessions
                    ADD CONSTRAINT interview_sessions_session_id_fkey
                    FOREIGN KEY (session_id)
                    REFERENCES sessions(id)
                    ON DELETE CASCADE
                """))
                print("✓ FK interview_sessions_session_id_fkey actualizado con CASCADE")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta ALTER TABLE ADD CONSTRAINT)")

        print("\n[2/6] Actualizando FK en incident_simulations con CASCADE DELETE...")
        if is_postgres:
            try:
                db.execute(text("""
                    ALTER TABLE incident_simulations
                    DROP CONSTRAINT IF EXISTS incident_simulations_session_id_fkey
                """))
                db.execute(text("""
                    ALTER TABLE incident_simulations
                    ADD CONSTRAINT incident_simulations_session_id_fkey
                    FOREIGN KEY (session_id)
                    REFERENCES sessions(id)
                    ON DELETE CASCADE
                """))
                print("✓ FK incident_simulations_session_id_fkey actualizado con CASCADE")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta ALTER TABLE ADD CONSTRAINT)")

        print("\n[3/6] Actualizando FK en simulator_events con CASCADE DELETE...")
        if is_postgres:
            try:
                db.execute(text("""
                    ALTER TABLE simulator_events
                    DROP CONSTRAINT IF EXISTS simulator_events_session_id_fkey
                """))
                db.execute(text("""
                    ALTER TABLE simulator_events
                    ADD CONSTRAINT simulator_events_session_id_fkey
                    FOREIGN KEY (session_id)
                    REFERENCES sessions(id)
                    ON DELETE CASCADE
                """))
                print("✓ FK simulator_events_session_id_fkey actualizado con CASCADE")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            print("  ⏭ Saltando (SQLite no soporta ALTER TABLE ADD CONSTRAINT)")

        # ======================================================================
        # FIX 3.4: Index para análisis 5D de riesgos
        # ======================================================================

        print("\n[4/6] Agregando índice idx_risk_session_dimension para análisis 5D...")
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_risk_session_dimension
                ON risks (session_id, dimension)
            """))
            print("✓ idx_risk_session_dimension creado")
        except Exception as e:
            print(f"  ⚠ Error: {e}")

        # ======================================================================
        # FIX 3.5: Index para CognitiveTraceDB.activity_id
        # ======================================================================

        print("\n[5/6] Agregando índice idx_trace_activity_id para reportes...")
        try:
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_trace_activity_id
                ON cognitive_traces (activity_id)
            """))
            print("✓ idx_trace_activity_id creado")
        except Exception as e:
            print(f"  ⚠ Error: {e}")

        # ======================================================================
        # FIX 3.8: Unique constraint en LTISessionDB
        # ======================================================================

        print("\n[6/6] Agregando unique constraint en lti_sessions...")
        if is_postgres:
            try:
                db.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_lti_unique_user_resource
                    ON lti_sessions (deployment_id, lti_user_id, resource_link_id)
                """))
                print("✓ idx_lti_unique_user_resource (unique) creado")
            except Exception as e:
                print(f"  ⚠ Error: {e}")
        else:
            # SQLite supports unique indexes
            try:
                db.execute(text("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_lti_unique_user_resource
                    ON lti_sessions (deployment_id, lti_user_id, resource_link_id)
                """))
                print("✓ idx_lti_unique_user_resource (unique) creado")
            except Exception as e:
                print(f"  ⚠ Error: {e}")

        # Commit
        db.commit()

        print("\n" + "=" * 80)
        print("✓ Migración Cortez3 completada exitosamente")
        print("=" * 80)

        # Verificar índices creados
        print("\n[Verificación] Consultando índices creados...")

        if is_sqlite:
            result = db.execute(text("""
                SELECT name FROM sqlite_master
                WHERE type = 'index'
                AND name LIKE 'idx_%'
                ORDER BY name
            """))
            print("\nÍndices creados:")
            for row in result:
                print(f"  - {row[0]}")
        else:
            result = db.execute(text("""
                SELECT indexname, tablename FROM pg_indexes
                WHERE schemaname = 'public'
                AND indexname IN (
                    'idx_risk_session_dimension',
                    'idx_trace_activity_id',
                    'idx_lti_unique_user_resource'
                )
                ORDER BY indexname
            """))
            print("\nÍndices Cortez3 creados:")
            for row in result:
                print(f"  - {row.indexname} en {row.tablename}")

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
    Nota: No revierte CASCADE DELETE ya que es una corrección de integridad
    """
    print("=" * 80)
    print("Rollback: Eliminar índices del Audit Cortez3")
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
        print("\nEliminando índices Cortez3...")
        indexes_to_drop = [
            "idx_risk_session_dimension",
            "idx_trace_activity_id",
            "idx_lti_unique_user_resource",
        ]

        for idx in indexes_to_drop:
            try:
                db.execute(text(f"DROP INDEX IF EXISTS {idx}"))
                print(f"✓ {idx} eliminado")
            except Exception as e:
                print(f"  ⚠ {idx}: {e}")

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
        migrate_cortez3_fixes()
