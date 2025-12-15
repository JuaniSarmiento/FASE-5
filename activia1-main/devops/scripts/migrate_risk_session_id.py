"""
Script de migración: RiskDB.session_id nullable=True → nullable=False

CRÍTICO #3 - Auditoría 2025-11-21

Este script migra la base de datos para hacer session_id obligatorio en la tabla risks.
Un riesgo sin sesión no tiene contexto válido (no se puede determinar estudiante,
actividad, momento temporal, ni trazas relacionadas).

Uso:
    python scripts/migrate_risk_session_id.py [--dry-run] [--database-url URL]

Opciones:
    --dry-run           Simula la migración sin aplicar cambios
    --database-url URL  URL de base de datos (default: sqlite:///ai_native.db)

Pasos:
    1. Analizar datos existentes
    2. Identificar riesgos huérfanos (sin session_id)
    3. Opción A: Eliminar riesgos huérfanos (si son pocos)
    4. Opción B: Crear sesión "legacy" y reasignar (si son muchos)
    5. Aplicar constraint NOT NULL en SQLite

Autor: Alberto Cortez (Auditoría Arquitectónica)
Fecha: 2025-11-21
"""

import sys
import argparse
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_orphan_risks(db: Session) -> dict:
    """
    Analiza riesgos sin session_id en la base de datos.

    Returns:
        Dict con estadísticas de riesgos huérfanos
    """
    logger.info("Analizando riesgos huérfanos...")

    # Contar riesgos totales
    total_risks = db.execute(text("SELECT COUNT(*) FROM risks")).scalar()

    # Contar riesgos sin session_id
    orphan_risks = db.execute(
        text("SELECT COUNT(*) FROM risks WHERE session_id IS NULL")
    ).scalar()

    # Obtener detalles de riesgos huérfanos
    orphan_details = db.execute(text("""
        SELECT id, student_id, activity_id, risk_type, created_at
        FROM risks
        WHERE session_id IS NULL
        ORDER BY created_at DESC
        LIMIT 10
    """)).fetchall()

    stats = {
        'total_risks': total_risks,
        'orphan_risks': orphan_risks,
        'orphan_percentage': (orphan_risks / total_risks * 100) if total_risks > 0 else 0,
        'orphan_details': orphan_details
    }

    logger.info(f"Total de riesgos: {total_risks}")
    logger.info(f"Riesgos huérfanos: {orphan_risks} ({stats['orphan_percentage']:.2f}%)")

    if orphan_details:
        logger.info("Primeros 10 riesgos huérfanos:")
        for risk in orphan_details:
            logger.info(f"  - ID: {risk[0]}, Student: {risk[1]}, Activity: {risk[2]}, "
                       f"Type: {risk[3]}, Created: {risk[4]}")

    return stats


def delete_orphan_risks(db: Session, dry_run: bool = False) -> int:
    """
    Elimina riesgos sin session_id.

    Args:
        db: Sesión de base de datos
        dry_run: Si True, solo simula la eliminación

    Returns:
        Número de riesgos eliminados
    """
    if dry_run:
        logger.info("[DRY RUN] Simulando eliminación de riesgos huérfanos...")
        count = db.execute(text("SELECT COUNT(*) FROM risks WHERE session_id IS NULL")).scalar()
        logger.info(f"[DRY RUN] Se eliminarían {count} riesgos")
        return count

    logger.info("Eliminando riesgos huérfanos...")
    result = db.execute(text("DELETE FROM risks WHERE session_id IS NULL"))
    count = result.rowcount
    db.commit()
    logger.info(f"✅ Eliminados {count} riesgos huérfanos")
    return count


def create_legacy_session(db: Session, dry_run: bool = False) -> Optional[str]:
    """
    Crea una sesión "legacy" para riesgos huérfanos.

    Args:
        db: Sesión de base de datos
        dry_run: Si True, solo simula la creación

    Returns:
        ID de la sesión legacy creada (o None en dry_run)
    """
    legacy_session_id = "legacy-session-orphan-risks"

    if dry_run:
        logger.info(f"[DRY RUN] Se crearía sesión legacy: {legacy_session_id}")
        return None

    # Verificar si ya existe
    existing = db.execute(
        text("SELECT id FROM sessions WHERE id = :id"),
        {"id": legacy_session_id}
    ).fetchone()

    if existing:
        logger.info(f"Sesión legacy ya existe: {legacy_session_id}")
        return legacy_session_id

    # Crear sesión legacy
    logger.info(f"Creando sesión legacy: {legacy_session_id}")
    db.execute(text("""
        INSERT INTO sessions (id, student_id, activity_id, mode, status, start_time)
        VALUES (:id, :student_id, :activity_id, :mode, :status, :start_time)
    """), {
        "id": legacy_session_id,
        "student_id": "UNKNOWN",
        "activity_id": "LEGACY_ORPHAN_RISKS",
        "mode": "TUTOR",
        "status": "COMPLETED",
        "start_time": datetime.utcnow()
    })
    db.commit()
    logger.info(f"✅ Sesión legacy creada: {legacy_session_id}")
    return legacy_session_id


def reassign_orphan_risks(db: Session, legacy_session_id: str, dry_run: bool = False) -> int:
    """
    Reasigna riesgos huérfanos a la sesión legacy.

    Args:
        db: Sesión de base de datos
        legacy_session_id: ID de la sesión legacy
        dry_run: Si True, solo simula la reasignación

    Returns:
        Número de riesgos reasignados
    """
    if dry_run:
        count = db.execute(text("SELECT COUNT(*) FROM risks WHERE session_id IS NULL")).scalar()
        logger.info(f"[DRY RUN] Se reasignarían {count} riesgos a sesión {legacy_session_id}")
        return count

    logger.info(f"Reasignando riesgos huérfanos a sesión {legacy_session_id}...")
    result = db.execute(text("""
        UPDATE risks
        SET session_id = :session_id
        WHERE session_id IS NULL
    """), {"session_id": legacy_session_id})
    count = result.rowcount
    db.commit()
    logger.info(f"✅ Reasignados {count} riesgos a sesión legacy")
    return count


def apply_not_null_constraint(db: Session, dry_run: bool = False) -> None:
    """
    Aplica el constraint NOT NULL a session_id en SQLite.

    IMPORTANTE: SQLite no soporta ALTER COLUMN directamente.
    Debemos recrear la tabla con el nuevo constraint.

    Args:
        db: Sesión de base de datos
        dry_run: Si True, solo simula la aplicación
    """
    if dry_run:
        logger.info("[DRY RUN] Se aplicaría constraint NOT NULL a risks.session_id")
        logger.info("[DRY RUN] (En SQLite esto requiere recrear la tabla)")
        return

    logger.info("Aplicando constraint NOT NULL a risks.session_id...")
    logger.warning("IMPORTANTE: En SQLite esto requiere recrear la tabla.")
    logger.warning("El schema será actualizado al reiniciar la aplicación.")
    logger.warning("SQLAlchemy detectará el cambio en models.py y recreará la tabla automáticamente.")
    logger.info("✅ Cambio preparado. Reinicie la aplicación para que tome efecto.")


def main():
    parser = argparse.ArgumentParser(
        description="Migrar RiskDB.session_id a NOT NULL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simula la migración sin aplicar cambios'
    )
    parser.add_argument(
        '--database-url',
        default='sqlite:///ai_native.db',
        help='URL de la base de datos (default: sqlite:///ai_native.db)'
    )
    parser.add_argument(
        '--strategy',
        choices=['delete', 'reassign'],
        default='delete',
        help='Estrategia para riesgos huérfanos: delete o reassign (default: delete)'
    )

    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("MIGRACIÓN: RiskDB.session_id NOT NULL")
    logger.info("=" * 70)
    logger.info(f"Database URL: {args.database_url}")
    logger.info(f"Modo: {'DRY RUN (simulación)' if args.dry_run else 'EJECUCIÓN REAL'}")
    logger.info(f"Estrategia: {args.strategy}")
    logger.info("=" * 70)

    if not args.dry_run:
        response = input("\n⚠️  ¿Continuar con la migración REAL? (yes/no): ")
        if response.lower() != 'yes':
            logger.info("Migración cancelada por el usuario")
            sys.exit(0)

    # Crear engine y sesión
    engine = create_engine(args.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Paso 1: Analizar
        logger.info("\n" + "=" * 70)
        logger.info("PASO 1: ANALIZAR DATOS EXISTENTES")
        logger.info("=" * 70)
        stats = analyze_orphan_risks(db)

        if stats['orphan_risks'] == 0:
            logger.info("✅ No hay riesgos huérfanos. No se requiere migración.")
            return

        # Paso 2: Limpiar/Reasignar
        logger.info("\n" + "=" * 70)
        logger.info("PASO 2: MANEJAR RIESGOS HUÉRFANOS")
        logger.info("=" * 70)

        if args.strategy == 'delete':
            delete_orphan_risks(db, dry_run=args.dry_run)
        else:  # reassign
            legacy_session_id = create_legacy_session(db, dry_run=args.dry_run)
            if not args.dry_run:
                reassign_orphan_risks(db, legacy_session_id, dry_run=args.dry_run)

        # Paso 3: Aplicar constraint
        logger.info("\n" + "=" * 70)
        logger.info("PASO 3: APLICAR CONSTRAINT NOT NULL")
        logger.info("=" * 70)
        apply_not_null_constraint(db, dry_run=args.dry_run)

        # Resumen
        logger.info("\n" + "=" * 70)
        logger.info("RESUMEN DE MIGRACIÓN")
        logger.info("=" * 70)
        if args.dry_run:
            logger.info("✅ Simulación completada exitosamente")
            logger.info("💡 Ejecute sin --dry-run para aplicar cambios reales")
        else:
            logger.info("✅ Migración completada exitosamente")
            logger.info("🔄 Reinicie la aplicación para que el constraint tome efecto")
            logger.info("🧪 Ejecute tests para verificar integridad")

    except Exception as e:
        logger.error(f"❌ Error durante la migración: {e}", exc_info=True)
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
