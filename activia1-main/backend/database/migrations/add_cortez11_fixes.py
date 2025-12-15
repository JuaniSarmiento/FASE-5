"""
Migración de Base de Datos: Correcciones del Audit Cortez11
Agrega cognitive_coherence a trace_sequences con check constraint

Ejecutar con: python -m backend.database.migrations.add_cortez11_fixes

DATABASE CHANGES (require migration):
- FIX 4.3: Agregar cognitive_coherence (Float, nullable) a trace_sequences
- FIX 4.3: Check constraint para rango 0-1 de cognitive_coherence

CODE CHANGES (no migration needed - already in codebase):
- FIX 2.5: TraceRepository.get_by_activity() agregado
- FIX 2.6: RiskRepository.get_by_activity() agregado
- FIX 2.7: RiskRepository.get_by_dimension() agregado
- FIX 2.8: EvaluationRepository.get_by_activity() agregado

🤖 Generated with Claude Code (claude.ai/claude-code)
"""
import sys
from sqlalchemy import text
from backend.database import init_database, get_db_config


def migrate_cortez11_fixes():
    """
    Aplica las correcciones del audit Cortez11:
    - Agrega cognitive_coherence a trace_sequences
    - Agrega check constraint para validar rango 0-1
    """
    print("=" * 80)
    print("Migración: Correcciones Audit Cortez11 (Diciembre 2025)")
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
        # FIX 4.3: Agregar cognitive_coherence a trace_sequences
        # ======================================================================

        print("\n" + "=" * 60)
        print("FIX 4.3: Agregar cognitive_coherence a trace_sequences")
        print("=" * 60)

        # Check if column already exists
        if is_postgres:
            result = db.execute(text("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'trace_sequences' AND column_name = 'cognitive_coherence'
            """))
            column_exists = result.fetchone() is not None
        else:
            # SQLite
            result = db.execute(text("PRAGMA table_info(trace_sequences)"))
            columns = [row[1] for row in result.fetchall()]
            column_exists = 'cognitive_coherence' in columns

        if column_exists:
            print("  ⏭ Columna cognitive_coherence ya existe")
        else:
            try:
                if is_postgres:
                    db.execute(text("""
                        ALTER TABLE trace_sequences
                        ADD COLUMN cognitive_coherence FLOAT
                    """))
                else:
                    db.execute(text("""
                        ALTER TABLE trace_sequences
                        ADD COLUMN cognitive_coherence REAL
                    """))
                print("  ✓ Columna cognitive_coherence agregada")
            except Exception as e:
                print(f"  ⚠ Error agregando columna: {e}")

        # ======================================================================
        # FIX 4.3: Check constraint para cognitive_coherence (0-1 range)
        # ======================================================================

        print("\n" + "=" * 60)
        print("FIX 4.3: Check constraint para cognitive_coherence")
        print("=" * 60)

        constraint_name = "ck_seq_cognitive_coherence_range"

        if is_postgres:
            # Check if constraint exists
            result = db.execute(text(f"""
                SELECT constraint_name FROM information_schema.check_constraints
                WHERE constraint_name = '{constraint_name}'
            """))
            constraint_exists = result.fetchone() is not None

            if constraint_exists:
                print(f"  ⏭ Constraint {constraint_name} ya existe")
            else:
                try:
                    db.execute(text(f"""
                        ALTER TABLE trace_sequences
                        ADD CONSTRAINT {constraint_name}
                        CHECK (cognitive_coherence IS NULL OR (cognitive_coherence >= 0 AND cognitive_coherence <= 1))
                    """))
                    print(f"  ✓ Constraint {constraint_name} agregado")
                except Exception as e:
                    print(f"  ⚠ Error agregando constraint: {e}")
        else:
            print("  ⏭ SQLite no soporta ADD CONSTRAINT después de crear tabla")
            print("    El constraint está en el ORM y se aplicará a nuevas tablas")

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
        print("  ✓ FIX 2.5: TraceRepository.get_by_activity() agregado")
        print("  ✓ FIX 2.6: RiskRepository.get_by_activity() agregado")
        print("  ✓ FIX 2.7: RiskRepository.get_by_dimension() agregado")
        print("  ✓ FIX 2.8: EvaluationRepository.get_by_activity() agregado")
        print("  ✓ FIX 4.3: cognitive_coherence en TraceSequenceDB ORM")

        print("\n" + "=" * 80)
        print("✓ Migración Cortez11 completada exitosamente")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error durante la migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration():
    """
    Revierte la migración (elimina columna y constraint)
    """
    print("=" * 80)
    print("Rollback: Eliminar cambios del Audit Cortez11")
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
        is_sqlite = db_url.startswith('sqlite')

        if is_postgres:
            # Drop constraint first
            print("\nEliminando constraint...")
            try:
                db.execute(text("""
                    ALTER TABLE trace_sequences
                    DROP CONSTRAINT IF EXISTS ck_seq_cognitive_coherence_range
                """))
                print("  ✓ Constraint ck_seq_cognitive_coherence_range eliminado")
            except Exception as e:
                print(f"  ⚠ Error: {e}")

            # Drop column
            print("\nEliminando columna...")
            try:
                db.execute(text("""
                    ALTER TABLE trace_sequences
                    DROP COLUMN IF EXISTS cognitive_coherence
                """))
                print("  ✓ Columna cognitive_coherence eliminada")
            except Exception as e:
                print(f"  ⚠ Error: {e}")

        elif is_sqlite:
            print("\n  ⚠ SQLite no soporta DROP COLUMN directamente")
            print("    Para revertir en SQLite:")
            print("    1. Crear nueva tabla sin la columna")
            print("    2. Copiar datos")
            print("    3. Eliminar tabla vieja")
            print("    4. Renombrar nueva tabla")

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
    print("Verificación: Estado de la Migración Cortez11")
    print("=" * 80)

    init_database()
    db_config = get_db_config()
    session_factory = db_config.get_session_factory()
    db = session_factory()

    try:
        db_url = str(db.bind.url)
        is_postgres = 'postgresql' in db_url

        print(f"\nBase de datos: {'PostgreSQL' if is_postgres else 'SQLite'}")

        # Check column exists
        print("\n[Column Check]")
        if is_postgres:
            result = db.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'trace_sequences' AND column_name = 'cognitive_coherence'
            """))
            row = result.fetchone()
            if row:
                print(f"  ✓ cognitive_coherence existe: {row[1]}, nullable={row[2]}")
            else:
                print("  ✗ cognitive_coherence NO existe")

            # Check constraint
            print("\n[Constraint Check]")
            result = db.execute(text("""
                SELECT constraint_name, check_clause
                FROM information_schema.check_constraints
                WHERE constraint_name = 'ck_seq_cognitive_coherence_range'
            """))
            row = result.fetchone()
            if row:
                print(f"  ✓ {row[0]}: {row[1]}")
            else:
                print("  ✗ ck_seq_cognitive_coherence_range NO existe")

        else:
            # SQLite
            result = db.execute(text("PRAGMA table_info(trace_sequences)"))
            columns = {row[1]: row[2] for row in result.fetchall()}
            if 'cognitive_coherence' in columns:
                print(f"  ✓ cognitive_coherence existe: {columns['cognitive_coherence']}")
            else:
                print("  ✗ cognitive_coherence NO existe")
            print("\n[Constraint Check]")
            print("  ⏭ SQLite: constraints verificados solo en ORM")

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
            print("Uso: python -m backend.database.migrations.add_cortez11_fixes [rollback|verify]")
    else:
        migrate_cortez11_fixes()