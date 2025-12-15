"""
Script de migración: Agregar campo user_id a tabla sessions

Este script añade la columna user_id a la tabla sessions de manera segura,
preservando los datos existentes.
"""
import sqlite3
import sys
from pathlib import Path

def migrate_add_user_id(db_path: str = "ai_native_mvp.db"):
    """
    Añade la columna user_id a la tabla sessions

    Args:
        db_path: Ruta al archivo de base de datos SQLite
    """
    print("=" * 70)
    print("Migración: Agregar user_id a tabla sessions")
    print("=" * 70)
    print()

    if not Path(db_path).exists():
        print(f"ERROR: Base de datos '{db_path}' no encontrada")
        print("Ejecutar primero: python scripts/init_database.py")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(sessions)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        if 'user_id' in column_names:
            print("OK: La columna user_id ya existe en la tabla sessions")
            print("   No se requiere migración")
            return

        print("Agregando columna user_id a tabla sessions...")

        # SQLite no soporta ALTER TABLE ADD COLUMN con FOREIGN KEY directamente
        # Necesitamos recrear la tabla

        # 1. Crear tabla temporal con nueva estructura
        cursor.execute("""
            CREATE TABLE sessions_new (
                student_id VARCHAR(100) NOT NULL,
                activity_id VARCHAR(100) NOT NULL,
                mode VARCHAR(50) NOT NULL DEFAULT 'TUTOR',
                user_id VARCHAR(100),
                start_time DATETIME NOT NULL,
                end_time DATETIME,
                status VARCHAR(20) DEFAULT 'active',
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        print("  [1/6] Tabla temporal creada")

        # 2. Copiar datos existentes
        cursor.execute("""
            INSERT INTO sessions_new
            (student_id, activity_id, mode, start_time, end_time, status, id, created_at, updated_at)
            SELECT student_id, activity_id, mode, start_time, end_time, status, id, created_at, updated_at
            FROM sessions
        """)
        print("  [2/6] Datos copiados a tabla temporal")

        # 3. Eliminar tabla original
        cursor.execute("DROP TABLE sessions")
        print("  [3/6] Tabla original eliminada")

        # 4. Renombrar tabla temporal
        cursor.execute("ALTER TABLE sessions_new RENAME TO sessions")
        print("  [4/6] Tabla temporal renombrada a sessions")

        # 5. Recrear índices
        cursor.execute("CREATE INDEX idx_session_student_activity ON sessions (student_id, activity_id)")
        cursor.execute("CREATE INDEX idx_status_created ON sessions (status, created_at)")
        cursor.execute("CREATE INDEX idx_student_status ON sessions (student_id, status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_user ON sessions (user_id)")
        print("  [5/6] Índices recreados")

        # 6. Commit
        conn.commit()
        print("  [6/6] Cambios confirmados")

        print()
        print("=" * 70)
        print("Migración completada exitosamente")
        print("=" * 70)
        print()
        print("Resumen:")
        print("  - Columna user_id agregada a tabla sessions")
        print("  - Foreign key a tabla users configurada")
        print("  - Datos existentes preservados")
        print("  - Índices recreados")

    except Exception as e:
        conn.rollback()
        print()
        print("ERROR durante la migración:")
        print(f"  {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Migración: Agregar user_id a sessions")
    parser.add_argument(
        "--database",
        default="ai_native_mvp.db",
        help="Ruta al archivo de base de datos (default: ai_native_mvp.db)"
    )

    args = parser.parse_args()
    migrate_add_user_id(args.database)
