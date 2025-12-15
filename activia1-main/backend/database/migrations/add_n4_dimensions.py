"""
Migración de Base de Datos: Trazabilidad N4 Completa
Agrega las 6 dimensiones de trazabilidad y metadatos de sesión

Ejecutar con: python -m backend.database.migrations.add_n4_dimensions
"""
import sys
from sqlalchemy import text
from backend.database import init_database, get_db_config

def migrate_add_n4_dimensions():
    """
    Agrega las columnas de las 6 dimensiones de Trazabilidad N4
    y los metadatos de sesión mejorados
    """
    print("=" * 80)
    print("Migración: Agregar Dimensiones de Trazabilidad N4")
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
        
        print(f"\nBase de datos detectada: {'SQLite' if is_sqlite else 'PostgreSQL'}")
        
        # ======================================================================
        # TABLA: cognitive_traces - Agregar 6 dimensiones
        # ======================================================================
        
        print("\n[1/7] Agregando dimensión SEMÁNTICA...")
        if is_sqlite:
            # SQLite usa TEXT para JSON y no soporta IF NOT EXISTS
            try:
                db.execute(text("""
                    ALTER TABLE cognitive_traces 
                    ADD COLUMN semantic_understanding TEXT DEFAULT '{}'
                """))
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("  ⚠ Columna ya existe, saltando...")
                else:
                    raise
        else:
            # PostgreSQL soporta JSONB
            db.execute(text("""
                ALTER TABLE cognitive_traces 
                ADD COLUMN IF NOT EXISTS semantic_understanding JSONB DEFAULT '{}'::jsonb
            """))
        print("✓ Dimensión semántica agregada")
        
        print("\n[2/7] Agregando dimensión ALGORÍTMICA...")
        if is_sqlite:
            try:
                db.execute(text("""
                    ALTER TABLE cognitive_traces 
                    ADD COLUMN algorithmic_evolution TEXT DEFAULT '{}'
                """))
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("  ⚠ Columna ya existe, saltando...")
                else:
                    raise
        else:
            db.execute(text("""
                ALTER TABLE cognitive_traces 
                ADD COLUMN IF NOT EXISTS algorithmic_evolution JSONB DEFAULT '{}'::jsonb
            """))
        print("✓ Dimensión algorítmica agregada")
        
        print("\n[3/7] Agregando dimensión COGNITIVA...")
        if is_sqlite:
            try:
                db.execute(text("""
                    ALTER TABLE cognitive_traces 
                    ADD COLUMN cognitive_reasoning TEXT DEFAULT '{}'
                """))
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("  ⚠ Columna ya existe, saltando...")
                else:
                    raise
        else:
            db.execute(text("""
                ALTER TABLE cognitive_traces 
                ADD COLUMN IF NOT EXISTS cognitive_reasoning JSONB DEFAULT '{}'::jsonb
            """))
        print("✓ Dimensión cognitiva agregada")
        
        print("\n[4/7] Agregando dimensión INTERACCIONAL...")
        if is_sqlite:
            try:
                db.execute(text("""
                    ALTER TABLE cognitive_traces 
                    ADD COLUMN interactional_data TEXT DEFAULT '{}'
                """))
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("  ⚠ Columna ya existe, saltando...")
                else:
                    raise
        else:
            db.execute(text("""
                ALTER TABLE cognitive_traces 
                ADD COLUMN IF NOT EXISTS interactional_data JSONB DEFAULT '{}'::jsonb
            """))
        print("✓ Dimensión interaccional agregada")
        
        print("\n[5/7] Agregando dimensión ÉTICA/RIESGO...")
        if is_sqlite:
            try:
                db.execute(text("""
                    ALTER TABLE cognitive_traces 
                    ADD COLUMN ethical_risk_data TEXT DEFAULT '{}'
                """))
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("  ⚠ Columna ya existe, saltando...")
                else:
                    raise
        else:
            db.execute(text("""
                ALTER TABLE cognitive_traces 
                ADD COLUMN IF NOT EXISTS ethical_risk_data JSONB DEFAULT '{}'::jsonb
            """))
        print("✓ Dimensión ética/riesgo agregada")
        
        print("\n[6/7] Agregando dimensión PROCESUAL...")
        if is_sqlite:
            try:
                db.execute(text("""
                    ALTER TABLE cognitive_traces 
                    ADD COLUMN process_data TEXT DEFAULT '{}'
                """))
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("  ⚠ Columna ya existe, saltando...")
                else:
                    raise
        else:
            db.execute(text("""
                ALTER TABLE cognitive_traces 
                ADD COLUMN IF NOT EXISTS process_data JSONB DEFAULT '{}'::jsonb
            """))
        print("✓ Dimensión procesual agregada")
        
        # ======================================================================
        # TABLA: sessions - Agregar metadatos de sesión
        # ======================================================================
        
        print("\n[7/7] Agregando metadatos de sesión...")
        
        if is_sqlite:
            try:
                db.execute(text("""
                    ALTER TABLE sessions 
                    ADD COLUMN learning_objective TEXT DEFAULT '{}'
                """))
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("  ⚠ learning_objective ya existe, saltando...")
                else:
                    raise
            
            try:
                db.execute(text("""
                    ALTER TABLE sessions 
                    ADD COLUMN cognitive_status TEXT DEFAULT '{}'
                """))
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("  ⚠ cognitive_status ya existe, saltando...")
                else:
                    raise
            
            try:
                db.execute(text("""
                    ALTER TABLE sessions 
                    ADD COLUMN session_metrics TEXT DEFAULT '{}'
                """))
            except Exception as e:
                if 'duplicate column' in str(e).lower():
                    print("  ⚠ session_metrics ya existe, saltando...")
                else:
                    raise
        else:
            db.execute(text("""
                ALTER TABLE sessions 
                ADD COLUMN IF NOT EXISTS learning_objective JSONB DEFAULT '{}'::jsonb
            """))
            
            db.execute(text("""
                ALTER TABLE sessions 
                ADD COLUMN IF NOT EXISTS cognitive_status JSONB DEFAULT '{}'::jsonb
            """))
            
            db.execute(text("""
                ALTER TABLE sessions 
                ADD COLUMN IF NOT EXISTS session_metrics JSONB DEFAULT '{}'::jsonb
            """))
        
        print("✓ Metadatos de sesión agregados")
        
        # Commit
        db.commit()
        
        print("\n" + "=" * 80)
        print("✓ Migración completada exitosamente")
        print("=" * 80)
        
        # Verificar
        print("\n[Verificación] Consultando estructura de tablas...")
        
        if is_sqlite:
            # SQLite usa PRAGMA table_info
            result = db.execute(text("PRAGMA table_info(cognitive_traces)"))
            print("\nColumnas en cognitive_traces:")
            for row in result:
                # row[1] es el nombre de la columna, row[2] es el tipo
                col_name = row[1]
                if any(keyword in col_name for keyword in ['_data', 'understanding', 'evolution', 'reasoning']):
                    print(f"  - {col_name}: {row[2]}")
            
            result = db.execute(text("PRAGMA table_info(sessions)"))
            print("\nColumnas en sessions:")
            for row in result:
                col_name = row[1]
                if any(keyword in col_name for keyword in ['objective', 'status', 'metrics']):
                    print(f"  - {col_name}: {row[2]}")
        else:
            # PostgreSQL usa information_schema
            result = db.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'cognitive_traces' 
                AND (column_name LIKE '%_data' OR column_name LIKE '%understanding' 
                     OR column_name LIKE '%evolution' OR column_name LIKE '%reasoning')
                ORDER BY column_name
            """))
            
            print("\nColumnas en cognitive_traces:")
            for row in result:
                print(f"  - {row.column_name}: {row.data_type}")
            
            result = db.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'sessions' 
                AND (column_name LIKE '%objective' OR column_name LIKE '%status' OR column_name LIKE '%metrics')
                ORDER BY column_name
            """))
            
            print("\nColumnas en sessions:")
            for row in result:
                print(f"  - {row.column_name}: {row.data_type}")
        
        print("\n✓ Verificación completa")
        
    except Exception as e:
        print(f"\n✗ Error durante la migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration():
    """
    Revierte la migración (elimina las columnas agregadas)
    """
    print("=" * 80)
    print("Rollback: Eliminar Dimensiones de Trazabilidad N4")
    print("=" * 80)
    print("⚠️  ADVERTENCIA: Esto eliminará datos permanentemente")
    
    confirm = input("\n¿Confirmar rollback? (escribir 'YES' para continuar): ")
    if confirm != "YES":
        print("Rollback cancelado")
        return
    
    init_database()
    db_config = get_db_config()
    session_factory = db_config.get_session_factory()
    db = session_factory()
    
    try:
        # Eliminar columnas de cognitive_traces
        print("\nEliminando columnas de cognitive_traces...")
        db.execute(text("ALTER TABLE cognitive_traces DROP COLUMN IF EXISTS semantic_understanding"))
        db.execute(text("ALTER TABLE cognitive_traces DROP COLUMN IF EXISTS algorithmic_evolution"))
        db.execute(text("ALTER TABLE cognitive_traces DROP COLUMN IF EXISTS cognitive_reasoning"))
        db.execute(text("ALTER TABLE cognitive_traces DROP COLUMN IF EXISTS interactional_data"))
        db.execute(text("ALTER TABLE cognitive_traces DROP COLUMN IF EXISTS ethical_risk_data"))
        db.execute(text("ALTER TABLE cognitive_traces DROP COLUMN IF EXISTS process_data"))
        
        # Eliminar columnas de sessions
        print("Eliminando columnas de sessions...")
        db.execute(text("ALTER TABLE sessions DROP COLUMN IF EXISTS learning_objective"))
        db.execute(text("ALTER TABLE sessions DROP COLUMN IF EXISTS cognitive_status"))
        db.execute(text("ALTER TABLE sessions DROP COLUMN IF EXISTS session_metrics"))
        
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
        migrate_add_n4_dimensions()
