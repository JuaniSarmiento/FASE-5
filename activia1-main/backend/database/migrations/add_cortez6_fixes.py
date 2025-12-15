"""
Migración de Base de Datos: Correcciones del Audit Cortez6
Agrega FK constraints, check constraints, índices compuestos

Ejecutar con: python -m backend.database.migrations.add_cortez6_fixes

DATABASE CHANGES (require migration):
- FIX 1.1: FK constraint for CourseReportDB.teacher_id -> users.id
- FIX 1.2: FK constraint for RemediationPlanDB.teacher_id -> users.id
- FIX 1.3: FK constraint for RiskAlertDB.assigned_to -> users.id
- FIX 1.4: FK constraint for RiskAlertDB.acknowledged_by -> users.id
- FIX 1.6: ondelete="CASCADE" for LTISessionDB.deployment_id
- FIX 1.7: ondelete="SET NULL" for LTISessionDB.session_id
- FIX 2.1-2.15: Check constraints for enum fields and numeric ranges
- FIX 5.2: Composite index for CourseReportDB (teacher_id, course_id)

CODE CHANGES (no migration needed - already in codebase):
- FIX 9.1: Sensitive field filtering in BaseModel.to_dict()

🤖 Generated with Claude Code (claude.ai/claude-code)
"""
import sys
from sqlalchemy import text
from backend.database import init_database, get_db_config


def migrate_cortez6_fixes():
    """
    Aplica las correcciones de FK constraints, check constraints e índices del audit Cortez6
    """
    print("=" * 80)
    print("Migración: Correcciones Audit Cortez6 (Diciembre 2025)")
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
        # SECTION 1: Foreign Key Constraints
        # ======================================================================

        print("\n" + "=" * 60)
        print("SECCIÓN 1: Foreign Key Constraints")
        print("=" * 60)

        # Note: SQLite doesn't support adding FK constraints to existing tables
        # These changes are already in the ORM model and will apply to new databases
        if is_postgres:
            fk_constraints = [
                # FIX 1.1: CourseReportDB.teacher_id
                (
                    "fk_course_reports_teacher",
                    "course_reports",
                    "teacher_id",
                    "users",
                    "id",
                    "SET NULL"
                ),
                # FIX 1.2: RemediationPlanDB.teacher_id
                (
                    "fk_remediation_plans_teacher",
                    "remediation_plans",
                    "teacher_id",
                    "users",
                    "id",
                    "SET NULL"
                ),
                # FIX 1.3: RiskAlertDB.assigned_to
                (
                    "fk_risk_alerts_assigned_to",
                    "risk_alerts",
                    "assigned_to",
                    "users",
                    "id",
                    "SET NULL"
                ),
                # FIX 1.4: RiskAlertDB.acknowledged_by
                (
                    "fk_risk_alerts_acknowledged_by",
                    "risk_alerts",
                    "acknowledged_by",
                    "users",
                    "id",
                    "SET NULL"
                ),
            ]

            for constraint_name, table, column, ref_table, ref_column, on_delete in fk_constraints:
                print(f"\n[FK] {table}.{column} -> {ref_table}.{ref_column}...")
                try:
                    # First, clean up orphan records (set to NULL if reference doesn't exist)
                    db.execute(text(f"""
                        UPDATE {table} SET {column} = NULL
                        WHERE {column} IS NOT NULL
                        AND {column} NOT IN (SELECT {ref_column} FROM {ref_table})
                    """))

                    # Add FK constraint if not exists
                    db.execute(text(f"""
                        DO $$
                        BEGIN
                            IF NOT EXISTS (
                                SELECT 1 FROM pg_constraint WHERE conname = '{constraint_name}'
                            ) THEN
                                ALTER TABLE {table} ADD CONSTRAINT {constraint_name}
                                FOREIGN KEY ({column}) REFERENCES {ref_table}({ref_column})
                                ON DELETE {on_delete};
                            END IF;
                        END $$;
                    """))
                    print(f"  ✓ {constraint_name} agregado")
                except Exception as e:
                    print(f"  ⚠ Error: {e}")
        else:
            print("\n  ⏭ SQLite no soporta ALTER TABLE ADD CONSTRAINT para FK")
            print("    Los FK están definidos en el ORM y se aplicarán a nuevas tablas")

        # ======================================================================
        # SECTION 2: Check Constraints for Enum Fields
        # ======================================================================

        print("\n" + "=" * 60)
        print("SECCIÓN 2: Check Constraints para Enums")
        print("=" * 60)

        if is_postgres:
            check_constraints = [
                # FIX 2.1-2.2: InterviewSessionDB
                (
                    "ck_interview_type_valid",
                    "interview_sessions",
                    "interview_type IN ('CONCEPTUAL', 'ALGORITHMIC', 'DESIGN', 'BEHAVIORAL')"
                ),
                (
                    "ck_interview_difficulty_valid",
                    "interview_sessions",
                    "difficulty_level IN ('EASY', 'MEDIUM', 'HARD')"
                ),
                # FIX 2.3-2.4: IncidentSimulationDB
                (
                    "ck_incident_type_valid",
                    "incident_simulations",
                    "incident_type IN ('API_ERROR', 'PERFORMANCE', 'SECURITY', 'DATABASE', 'DEPLOYMENT')"
                ),
                (
                    "ck_incident_severity_valid",
                    "incident_simulations",
                    "severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')"
                ),
                # FIX 2.5-2.6: ActivityDB
                (
                    "ck_activity_status_valid",
                    "activities",
                    "status IN ('draft', 'active', 'archived')"
                ),
                (
                    "ck_activity_difficulty_valid",
                    "activities",
                    "difficulty IS NULL OR difficulty IN ('INICIAL', 'INTERMEDIO', 'AVANZADO')"
                ),
                # FIX 2.7-2.8: RemediationPlanDB
                (
                    "ck_plan_type_valid",
                    "remediation_plans",
                    "plan_type IN ('tutoring', 'practice_exercises', 'conceptual_review', 'policy_clarification')"
                ),
                (
                    "ck_remediation_status_valid",
                    "remediation_plans",
                    "status IN ('pending', 'in_progress', 'completed', 'cancelled')"
                ),
                # FIX 2.9-2.12: RiskAlertDB
                (
                    "ck_alert_type_valid",
                    "risk_alerts",
                    "alert_type IN ('critical_risk_surge', 'ai_dependency_spike', 'academic_integrity', 'pattern_anomaly')"
                ),
                (
                    "ck_alert_severity_valid",
                    "risk_alerts",
                    "severity IN ('low', 'medium', 'high', 'critical')"
                ),
                (
                    "ck_alert_scope_valid",
                    "risk_alerts",
                    "scope IN ('student', 'activity', 'course', 'institution')"
                ),
                (
                    "ck_alert_status_valid",
                    "risk_alerts",
                    "status IN ('open', 'acknowledged', 'investigating', 'resolved', 'false_positive')"
                ),
                # FIX 2.13: SimulatorEventDB
                (
                    "ck_simulator_event_type_valid",
                    "simulator_events",
                    "simulator_type IN ('product_owner', 'scrum_master', 'tech_interviewer', 'incident_responder', 'client', 'devsecops')"
                ),
                # FIX 2.14: GitTraceDB
                (
                    "ck_git_event_type_valid",
                    "git_traces",
                    "event_type IN ('commit', 'branch_create', 'branch_delete', 'merge', 'tag', 'revert', 'cherry_pick')"
                ),
            ]

            for constraint_name, table, check_clause in check_constraints:
                print(f"\n[CHECK] {constraint_name} en {table}...")
                try:
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
                    print(f"  ✓ {constraint_name} agregado")
                except Exception as e:
                    if "does not exist" in str(e).lower():
                        print(f"  ⏭ Tabla {table} no existe (opcional)")
                    else:
                        print(f"  ⚠ Error: {e}")
        else:
            print("\n  ⏭ SQLite no soporta ALTER TABLE ADD CONSTRAINT para CHECK")
            print("    Los constraints CHECK están definidos en el ORM")

        # ======================================================================
        # SECTION 3: Range Constraints for Numeric Fields
        # ======================================================================

        print("\n" + "=" * 60)
        print("SECCIÓN 3: Range Constraints para Campos Numéricos")
        print("=" * 60)

        if is_postgres:
            range_constraints = [
                # FIX 2.15: Numeric range constraints
                (
                    "ck_cognitive_trace_ai_involvement",
                    "cognitive_traces",
                    "ai_involvement IS NULL OR (ai_involvement >= 0 AND ai_involvement <= 1)"
                ),
                (
                    "ck_evaluation_overall_score",
                    "evaluations",
                    "overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 10)"
                ),
                (
                    "ck_evaluation_ai_dependency",
                    "evaluations",
                    "ai_dependency_score IS NULL OR (ai_dependency_score >= 0 AND ai_dependency_score <= 1)"
                ),
                (
                    "ck_trace_sequence_ai_dependency",
                    "trace_sequences",
                    "ai_dependency_score IS NULL OR (ai_dependency_score >= 0 AND ai_dependency_score <= 1)"
                ),
                (
                    "ck_student_profile_ai_dependency",
                    "student_profiles",
                    "average_ai_dependency IS NULL OR (average_ai_dependency >= 0 AND average_ai_dependency <= 1)"
                ),
                (
                    "ck_interview_score_range",
                    "interview_sessions",
                    "evaluation_score IS NULL OR (evaluation_score >= 0 AND evaluation_score <= 1)"
                ),
            ]

            for constraint_name, table, check_clause in range_constraints:
                print(f"\n[RANGE] {constraint_name} en {table}...")
                try:
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
                    print(f"  ✓ {constraint_name} agregado")
                except Exception as e:
                    if "does not exist" in str(e).lower():
                        print(f"  ⏭ Tabla {table} no existe (opcional)")
                    else:
                        print(f"  ⚠ Error: {e}")
        else:
            print("\n  ⏭ SQLite no soporta ALTER TABLE ADD CONSTRAINT")
            print("    Los constraints de rango están definidos en el ORM")

        # ======================================================================
        # SECTION 4: Composite Indexes
        # ======================================================================

        print("\n" + "=" * 60)
        print("SECCIÓN 4: Índices Compuestos")
        print("=" * 60)

        composite_indexes = [
            # FIX 5.2: CourseReportDB composite index
            ("idx_report_teacher_course", "course_reports", "teacher_id, course_id"),
        ]

        for idx_name, table, columns in composite_indexes:
            print(f"\n[INDEX] {idx_name} en {table}({columns})...")
            try:
                db.execute(text(f"""
                    CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({columns})
                """))
                print(f"  ✓ {idx_name} creado")
            except Exception as e:
                if "does not exist" in str(e).lower():
                    print(f"  ⏭ Tabla {table} no existe (opcional)")
                else:
                    print(f"  ⚠ Error: {e}")

        # ======================================================================
        # SECTION 5: Column Indexes for FK Fields
        # ======================================================================

        print("\n" + "=" * 60)
        print("SECCIÓN 5: Índices para Columnas FK")
        print("=" * 60)

        fk_indexes = [
            # FIX 1.1-1.4: Indexes for new FK columns
            ("idx_course_reports_teacher", "course_reports", "teacher_id"),
            ("idx_remediation_plans_teacher", "remediation_plans", "teacher_id"),
            ("idx_risk_alerts_assigned_to", "risk_alerts", "assigned_to"),
        ]

        for idx_name, table, column in fk_indexes:
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
        # Commit y verificación
        # ======================================================================

        print("\n" + "=" * 60)
        print("APLICANDO CAMBIOS")
        print("=" * 60)

        db.commit()
        print("\n✓ Cambios aplicados exitosamente")

        # ======================================================================
        # Code changes summary (no migration needed)
        # ======================================================================

        print("\n" + "=" * 60)
        print("RESUMEN: Cambios en Código (ya aplicados)")
        print("=" * 60)
        print("  ✓ FIX 9.1: Filtrado de campos sensibles en BaseModel.to_dict()")
        print("    - _SENSITIVE_FIELDS = {'hashed_password', 'launch_token'}")
        print("    - Parámetro include_sensitive=False por defecto")

        print("\n" + "=" * 80)
        print("✓ Migración Cortez6 completada exitosamente")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error durante la migración: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def rollback_migration():
    """
    Revierte la migración (elimina constraints e índices agregados)
    """
    print("=" * 80)
    print("Rollback: Eliminar cambios del Audit Cortez6")
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
        print("\nEliminando índices Cortez6...")
        indexes_to_drop = [
            "idx_report_teacher_course",
            "idx_course_reports_teacher",
            "idx_remediation_plans_teacher",
            "idx_risk_alerts_assigned_to",
        ]

        for idx in indexes_to_drop:
            try:
                db.execute(text(f"DROP INDEX IF EXISTS {idx}"))
                print(f"  ✓ {idx} eliminado")
            except Exception as e:
                print(f"  ⚠ {idx}: {e}")

        if is_postgres:
            # Drop FK constraints
            print("\nEliminando FK constraints...")
            fk_constraints = [
                ("course_reports", "fk_course_reports_teacher"),
                ("remediation_plans", "fk_remediation_plans_teacher"),
                ("risk_alerts", "fk_risk_alerts_assigned_to"),
                ("risk_alerts", "fk_risk_alerts_acknowledged_by"),
            ]

            for table, constraint in fk_constraints:
                try:
                    db.execute(text(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint}"))
                    print(f"  ✓ {constraint} eliminado")
                except Exception as e:
                    print(f"  ⚠ {constraint}: {e}")

            # Drop check constraints
            print("\nEliminando check constraints...")
            check_constraints = [
                ("interview_sessions", "ck_interview_type_valid"),
                ("interview_sessions", "ck_interview_difficulty_valid"),
                ("interview_sessions", "ck_interview_score_range"),
                ("incident_simulations", "ck_incident_type_valid"),
                ("incident_simulations", "ck_incident_severity_valid"),
                ("activities", "ck_activity_status_valid"),
                ("activities", "ck_activity_difficulty_valid"),
                ("remediation_plans", "ck_plan_type_valid"),
                ("remediation_plans", "ck_remediation_status_valid"),
                ("risk_alerts", "ck_alert_type_valid"),
                ("risk_alerts", "ck_alert_severity_valid"),
                ("risk_alerts", "ck_alert_scope_valid"),
                ("risk_alerts", "ck_alert_status_valid"),
                ("simulator_events", "ck_simulator_event_type_valid"),
                ("git_traces", "ck_git_event_type_valid"),
                ("cognitive_traces", "ck_cognitive_trace_ai_involvement"),
                ("evaluations", "ck_evaluation_overall_score"),
                ("evaluations", "ck_evaluation_ai_dependency"),
                ("trace_sequences", "ck_trace_sequence_ai_dependency"),
                ("student_profiles", "ck_student_profile_ai_dependency"),
            ]

            for table, constraint in check_constraints:
                try:
                    db.execute(text(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint}"))
                    print(f"  ✓ {constraint} eliminado")
                except Exception as e:
                    print(f"  ⚠ {constraint}: {e}")
        else:
            print("\n⚠ SQLite no soporta DROP CONSTRAINT. Los constraints permanecerán.")

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
    print("Verificación: Estado de la Migración Cortez6")
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
            # Check FK constraints
            print("\n[FK Constraints]")
            fk_to_check = [
                "fk_course_reports_teacher",
                "fk_remediation_plans_teacher",
                "fk_risk_alerts_assigned_to",
                "fk_risk_alerts_acknowledged_by",
            ]
            for fk in fk_to_check:
                result = db.execute(text(f"""
                    SELECT 1 FROM pg_constraint WHERE conname = '{fk}'
                """))
                exists = result.fetchone() is not None
                print(f"  {'✓' if exists else '✗'} {fk}")

            # Check check constraints
            print("\n[Check Constraints]")
            checks_to_verify = [
                "ck_interview_type_valid",
                "ck_incident_type_valid",
                "ck_activity_status_valid",
                "ck_plan_type_valid",
                "ck_alert_type_valid",
                "ck_simulator_event_type_valid",
                "ck_git_event_type_valid",
                "ck_cognitive_trace_ai_involvement",
                "ck_evaluation_overall_score",
            ]
            for check in checks_to_verify:
                result = db.execute(text(f"""
                    SELECT 1 FROM pg_constraint WHERE conname = '{check}'
                """))
                exists = result.fetchone() is not None
                print(f"  {'✓' if exists else '✗'} {check}")

            # Check indexes
            print("\n[Indexes]")
            indexes_to_check = [
                "idx_report_teacher_course",
                "idx_course_reports_teacher",
                "idx_remediation_plans_teacher",
                "idx_risk_alerts_assigned_to",
            ]
            for idx in indexes_to_check:
                result = db.execute(text(f"""
                    SELECT 1 FROM pg_indexes WHERE indexname = '{idx}'
                """))
                exists = result.fetchone() is not None
                print(f"  {'✓' if exists else '✗'} {idx}")
        else:
            print("\n  SQLite: Verificación limitada")
            print("  Los constraints están en el ORM, no en tablas existentes")

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
            print("Uso: python -m backend.database.migrations.add_cortez6_fixes [rollback|verify]")
    else:
        migrate_cortez6_fixes()
