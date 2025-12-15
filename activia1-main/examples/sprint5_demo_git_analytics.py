"""
Demo completo de Sprint 5 - Git N2 Traceability + Analytics + Risk Management

SPRINT 5 - HU-SYS-008, HU-DOC-009, HU-DOC-010

Este script demuestra:
1. Captura de eventos Git (N2) con GitIntegrationAgent
2. Correlación Git ↔ Cognición (N2 ↔ N4)
3. Análisis de evolución de código
4. Generación de reportes institucionales (cohort summary, risk dashboard)
5. Gestión de riesgos institucionales (alertas automáticas, planes de remediación)

IMPORTANTE: Este demo requiere GitPython instalado:
    pip install GitPython

Autor: Alberto Cortez - Sprint 5 Implementation
Fecha: 2025-11-21
"""

import sys
import io
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.ai_native_mvp.database import get_db_session, init_database
from src.ai_native_mvp.database.repositories import (
    SessionRepository,
    TraceRepository,
    RiskRepository,
    GitTraceRepository,
    CourseReportRepository,
    RiskAlertRepository,
    RemediationPlanRepository,
)
from src.ai_native_mvp.agents.git_integration import GitIntegrationAgent
from src.ai_native_mvp.services.course_report_generator import CourseReportGenerator
from src.ai_native_mvp.services.institutional_risk_manager import InstitutionalRiskManager
from src.ai_native_mvp.models.trace import CognitiveTrace, InteractionType, TraceLevel
from src.ai_native_mvp.core.cognitive_engine import CognitiveState
from src.ai_native_mvp.models.risk import Risk, RiskType, RiskLevel, RiskDimension

console = Console()


def print_header(title: str):
    """Print section header"""
    console.print()
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))
    console.print()


def print_success(message: str):
    """Print success message"""
    console.print(f"[bold green]✅ {message}[/bold green]")


def print_info(message: str):
    """Print info message"""
    console.print(f"[bold blue]ℹ️  {message}[/bold blue]")


def print_warning(message: str):
    """Print warning message"""
    console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")


def print_error(message: str):
    """Print error message"""
    console.print(f"[bold red]❌ {message}[/bold red]")


def demo_git_integration():
    """
    DEMO 1: Integración Git - Captura de eventos N2
    """
    print_header("DEMO 1: Integración Git (N2 Traceability)")

    with get_db_session() as db:
        # Crear sesión de aprendizaje
        session_repo = SessionRepository(db)
        session = session_repo.create(
            student_id="student_001",
            activity_id="prog2_tp1_colas",
            mode="TUTOR"
        )
        print_success(f"Sesión creada: {session.id}")

        # Crear algunas trazas cognitivas N4 para correlación
        trace_repo = TraceRepository(db)
        now = datetime.now(timezone.utc)

        cognitive_traces = []
        for i in range(3):
            trace = trace_repo.create(
                session_id=session.id,
                student_id="student_001",
                activity_id="prog2_tp1_colas",
                trace_level="n4_cognitivo",
                interaction_type="student_prompt",
                content=f"Consulta {i+1}: ¿Cómo implemento una cola circular?",
                cognitive_state=CognitiveState.IMPLEMENTACION.value,
                ai_involvement=0.4,
            )
            cognitive_traces.append(trace)

        print_success(f"Creadas {len(cognitive_traces)} trazas cognitivas N4")

        # IMPORTANTE: Para este demo, usaremos el repositorio actual como ejemplo
        # En producción, sería el repositorio del estudiante
        repo_path = Path(__file__).parent.parent
        print_info(f"Usando repositorio: {repo_path}")

        # Verificar que GitPython esté disponible
        try:
            from git import Repo
            repo = Repo(repo_path)
            print_success(f"Repositorio Git encontrado: {repo.working_dir}")

            # Obtener últimos 5 commits
            commits = list(repo.iter_commits(max_count=5))
            print_info(f"Últimos {len(commits)} commits encontrados")

            # Crear agente Git
            git_trace_repo = GitTraceRepository(db)
            git_agent = GitIntegrationAgent(git_trace_repo=git_trace_repo)

            # Capturar commits
            git_traces = []
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Capturando commits Git...", total=len(commits))

                for commit in commits[:3]:  # Solo primeros 3 para el demo
                    try:
                        git_trace = git_agent.capture_commit(
                            repo_path=str(repo_path),
                            commit_hash=commit.hexsha,
                            session_id=session.id,
                            student_id="student_001",
                            activity_id="prog2_tp1_colas",
                            cognitive_traces=cognitive_traces,
                        )
                        git_traces.append(git_trace)
                        progress.advance(task)
                    except Exception as e:
                        print_warning(f"Error capturando commit {commit.hexsha[:8]}: {e}")

            print_success(f"Capturados {len(git_traces)} commits como trazas N2")

            # Mostrar trazas Git en tabla
            if git_traces:
                table = Table(title="Trazas Git N2 Capturadas")
                table.add_column("Commit Hash", style="cyan")
                table.add_column("Mensaje", style="white")
                table.add_column("Archivos", style="green")
                table.add_column("Líneas +/-", style="yellow")
                table.add_column("Patrones", style="magenta")

                for trace in git_traces[:5]:
                    table.add_row(
                        trace.commit_hash[:8],
                        trace.commit_message[:40] + "...",
                        str(len(trace.files_changed)),
                        f"+{trace.total_lines_added}/-{trace.total_lines_deleted}",
                        ", ".join([p.value for p in trace.detected_patterns]),
                    )

                console.print(table)

            # Análisis de evolución de código
            if len(git_traces) > 0:
                print_info("Analizando evolución de código...")
                evolution = git_agent.analyze_code_evolution(session.id, git_traces)

                console.print()
                console.print("[bold]Evolución de Código:[/bold]")
                console.print(f"  Total commits: {evolution.total_commits}")
                console.print(f"  Líneas agregadas: {evolution.total_lines_added}")
                console.print(f"  Líneas eliminadas: {evolution.total_lines_deleted}")
                console.print(f"  Cambio neto: {evolution.net_lines_change}")
                console.print(f"  Archivos únicos: {evolution.unique_files_count}")
                console.print(f"  Patrones: {evolution.pattern_distribution}")

                # Correlación Git-Cognición
                print_info("Correlacionando Git (N2) con Cognición (N4)...")
                correlation = git_agent.correlate_git_with_cognitive_traces(
                    git_traces, cognitive_traces
                )

                console.print()
                console.print("[bold]Correlación N2 ↔ N4:[/bold]")
                console.print(f"  Correlaciones encontradas: {len(correlation.correlations)}")
                console.print(f"  Tiempo promedio commit→interacción: "
                            f"{correlation.avg_time_between_commit_and_interaction:.1f} min"
                            if correlation.avg_time_between_commit_and_interaction else "N/A")
                console.print(f"  Commits sin interacciones cercanas: "
                            f"{correlation.commits_without_nearby_interactions}")
                console.print(f"  Ratio interacción/commit: "
                            f"{correlation.interaction_to_commit_ratio:.2f}"
                            if correlation.interaction_to_commit_ratio else "N/A")

        except ImportError:
            print_error("GitPython no está instalado. Instalar con: pip install GitPython")
        except Exception as e:
            print_error(f"Error en demo Git: {e}")


def demo_course_reports():
    """
    DEMO 2: Reportes Institucionales - Agregación de cohortes
    """
    print_header("DEMO 2: Reportes Institucionales (Cohort Summary + Risk Dashboard)")

    with get_db_session() as db:
        # Crear datos de ejemplo: 5 estudiantes con sesiones y riesgos
        session_repo = SessionRepository(db)
        trace_repo = TraceRepository(db)
        risk_repo = RiskRepository(db)

        student_ids = [f"student_{i:03d}" for i in range(1, 6)]
        period_start = datetime.now(timezone.utc) - timedelta(days=30)
        period_end = datetime.now(timezone.utc)

        print_info("Creando datos de ejemplo para 5 estudiantes...")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Generando sesiones y trazas...", total=len(student_ids))

            for student_id in student_ids:
                # Crear 3 sesiones por estudiante
                for i in range(3):
                    session = session_repo.create(
                        student_id=student_id,
                        activity_id="prog2_tp1_colas",
                        mode="TUTOR"
                    )

                    # Crear 5 trazas por sesión con AI involvement variable
                    ai_involvement = 0.3 if student_id in ["student_001", "student_002"] else 0.8
                    for _ in range(5):
                        trace_repo.create(
                            session_id=session.id,
                            student_id=student_id,
                            activity_id="prog2_tp1_colas",
                            trace_level="n4_cognitivo",
                            interaction_type="student_prompt",
                            content="Consulta sobre colas circulares",
                            cognitive_state=CognitiveState.IMPLEMENTACION.value,
                            ai_involvement=ai_involvement,
                        )

                    # Crear riesgos para algunos estudiantes
                    if student_id in ["student_003", "student_004", "student_005"]:
                        risk_repo.create(
                            session_id=session.id,
                            student_id=student_id,
                            activity_id="prog2_tp1_colas",
                            risk_type=RiskType.AI_DEPENDENCY.value,
                            risk_level=RiskLevel.HIGH.value if student_id == "student_005" else RiskLevel.MEDIUM.value,
                            dimension=RiskDimension.COGNITIVE.value,
                            description=f"Alta dependencia de IA detectada en {student_id}",
                            evidence=["AI involvement > 0.7"],
                        )

                progress.advance(task)

        print_success(f"Datos creados: {len(student_ids)} estudiantes, 15 sesiones, 75 trazas")

        # Generar reporte de cohorte
        print_info("Generando reporte de cohorte...")
        generator = CourseReportGenerator(db)

        cohort_report = generator.generate_cohort_summary(
            course_id="PROG2_2025_1C",
            teacher_id="teacher_001",
            student_ids=student_ids,
            period_start=period_start,
            period_end=period_end,
            export_format="json",
        )

        print_success(f"Reporte de cohorte generado: {cohort_report['report_id']}")

        # Mostrar estadísticas del reporte
        table = Table(title="Reporte de Cohorte - Estadísticas")
        table.add_column("Métrica", style="cyan")
        table.add_column("Valor", style="green")

        stats = cohort_report['summary_stats']
        table.add_row("Total estudiantes", str(stats['total_students']))
        table.add_row("Total sesiones", str(stats['total_sessions']))
        table.add_row("Total interacciones", str(stats['total_interactions']))
        table.add_row("Promedio sesiones/estudiante", str(stats['avg_sessions_per_student']))
        table.add_row("Dependencia IA promedio", f"{stats['avg_ai_dependency']:.2f}")
        table.add_row("Total riesgos", str(stats['total_risks']))

        console.print(table)

        # Distribución de riesgos
        if cohort_report['risk_distribution']:
            risk_table = Table(title="Distribución de Riesgos")
            risk_table.add_column("Nivel", style="cyan")
            risk_table.add_column("Cantidad", style="red")

            for level, count in cohort_report['risk_distribution'].items():
                risk_table.add_row(level, str(count))

            console.print(risk_table)

        # Estudiantes en riesgo
        if cohort_report['at_risk_students']:
            console.print()
            console.print(f"[bold red]⚠️  Estudiantes en riesgo:[/bold red] "
                        f"{', '.join(cohort_report['at_risk_students'])}")

        # Recomendaciones institucionales
        if cohort_report['institutional_recommendations']:
            console.print()
            console.print("[bold yellow]Recomendaciones Institucionales:[/bold yellow]")
            for i, rec in enumerate(cohort_report['institutional_recommendations'], 1):
                console.print(f"  {i}. {rec}")

        # Generar dashboard de riesgos
        print_info("Generando dashboard de riesgos...")
        risk_dashboard = generator.generate_risk_dashboard(
            course_id="PROG2_2025_1C",
            teacher_id="teacher_001",
            student_ids=student_ids,
            period_start=period_start,
            period_end=period_end,
        )

        print_success(f"Dashboard de riesgos generado: {risk_dashboard['report_id']}")

        console.print()
        console.print(f"[bold]Estudiantes críticos:[/bold] {len(risk_dashboard['critical_students'])}")


def demo_institutional_risk_management():
    """
    DEMO 3: Gestión de Riesgos Institucionales - Alertas automáticas y planes de remediación
    """
    print_header("DEMO 3: Gestión de Riesgos Institucionales (Alerts + Remediation Plans)")

    with get_db_session() as db:
        # Crear estudiante con patrones de riesgo
        print_info("Creando estudiante con patrones de riesgo...")

        session_repo = SessionRepository(db)
        trace_repo = TraceRepository(db)
        risk_repo = RiskRepository(db)

        student_id = "student_at_risk_001"

        # Crear sesiones con alta dependencia de IA
        for i in range(5):
            session = session_repo.create(
                student_id=student_id,
                activity_id="prog2_tp1_colas",
                mode="TUTOR"
            )

            # Trazas con AI involvement alto (0.85)
            for _ in range(10):
                trace_repo.create(
                    session_id=session.id,
                    student_id=student_id,
                    activity_id="prog2_tp1_colas",
                    trace_level="n4_cognitivo",
                    interaction_type="student_prompt",
                    content="Dame el código completo",
                    cognitive_state=CognitiveState.IMPLEMENTACION.value,
                    ai_involvement=0.85,  # MUY ALTO
                )

            # Crear riesgos críticos
            if i >= 3:  # Últimas 2 sesiones
                risk_repo.create(
                    session_id=session.id,
                    student_id=student_id,
                    activity_id="prog2_tp1_colas",
                    risk_type=RiskType.COGNITIVE_DELEGATION.value,
                    risk_level=RiskLevel.CRITICAL.value,
                    dimension=RiskDimension.COGNITIVE.value,
                    description="Delegación total detectada",
                    evidence=["Solicita código completo sin razonamiento previo"],
                )

        print_success(f"Estudiante {student_id} creado con 5 sesiones y 2 riesgos críticos")

        # Escanear alertas automáticamente
        print_info("Escaneando alertas de riesgo...")
        manager = InstitutionalRiskManager(db)

        alerts = manager.scan_for_alerts(
            student_ids=[student_id],
            lookback_days=7,
        )

        print_success(f"Alertas detectadas: {len(alerts)}")

        # Mostrar alertas
        if alerts:
            alert_table = Table(title="Alertas Detectadas")
            alert_table.add_column("Tipo", style="yellow")
            alert_table.add_column("Severidad", style="red")
            alert_table.add_column("Valor Real", style="cyan")
            alert_table.add_column("Umbral", style="green")

            for alert in alerts:
                alert_table.add_row(
                    alert['alert_type'],
                    alert['severity'],
                    f"{alert['actual_value']:.2f}",
                    str(alert.get('threshold_value', 'N/A')),
                )

            console.print(alert_table)

            # Crear plan de remediación para primera alerta
            if alerts:
                first_alert = alerts[0]
                print_info("Creando plan de remediación...")

                plan = manager.create_remediation_plan(
                    student_id=student_id,
                    teacher_id="teacher_001",
                    trigger_risk_ids=[],
                    plan_type="tutoring",
                    description="Plan de intervención para reducir dependencia de IA",
                    objectives=[
                        "Reducir AI involvement de 0.85 a < 0.5",
                        "Fomentar razonamiento autónomo",
                        "Mejorar habilidades de descomposición de problemas",
                    ],
                    recommended_actions=[
                        {
                            "action_type": "tutoring_session",
                            "description": "Sesión de tutoría sobre autonomía cognitiva",
                            "deadline": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
                            "status": "pending",
                        },
                        {
                            "action_type": "practice_exercises",
                            "description": "Ejercicios guiados sin acceso a IA",
                            "deadline": (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
                            "status": "pending",
                        },
                    ],
                    duration_days=14,
                )

                print_success(f"Plan de remediación creado: {plan['plan_id']}")

                console.print()
                console.print("[bold]Detalles del Plan:[/bold]")
                console.print(f"  Tipo: {plan['plan_type']}")
                console.print(f"  Descripción: {plan['description']}")
                console.print(f"  Objetivos: {len(plan['objectives'])}")
                console.print(f"  Acciones: {len(plan['recommended_actions'])}")
                console.print(f"  Duración: {plan['duration_days']} días")
                console.print(f"  Estado: {plan['status']}")

        # Obtener métricas del dashboard
        print_info("Obteniendo métricas del dashboard...")
        dashboard_metrics = manager.get_dashboard_metrics(teacher_id="teacher_001")

        metrics_table = Table(title="Dashboard de Riesgos Institucionales")
        metrics_table.add_column("Métrica", style="cyan")
        metrics_table.add_column("Valor", style="green")

        metrics_table.add_row("Alertas abiertas", str(dashboard_metrics['open_alerts']))
        metrics_table.add_row("Alertas críticas", str(dashboard_metrics['critical_alerts']))
        metrics_table.add_row("Planes de remediación activos", str(dashboard_metrics['active_remediation_plans']))
        metrics_table.add_row("Tasa de resolución (30d)", f"{dashboard_metrics['resolution_rate_30d']:.1f}%")

        console.print(metrics_table)


def main():
    """Ejecutar todos los demos de Sprint 5"""
    console.print()
    console.print(Panel.fit(
        "[bold cyan]SPRINT 5 - Demo Completo[/bold cyan]\n"
        "[yellow]Git N2 Traceability + Analytics + Risk Management[/yellow]\n\n"
        "HU-SYS-008: Integración Git\n"
        "HU-DOC-009: Reportes Institucionales\n"
        "HU-DOC-010: Gestión de Riesgos Institucionales",
        border_style="cyan"
    ))

    # Inicializar base de datos
    print_info("Inicializando base de datos...")
    init_database()
    print_success("Base de datos inicializada")

    try:
        # DEMO 1: Git Integration
        demo_git_integration()

        # DEMO 2: Course Reports
        demo_course_reports()

        # DEMO 3: Institutional Risk Management
        demo_institutional_risk_management()

        # Resumen final
        print_header("RESUMEN FINAL - Sprint 5 Completado")

        summary_table = Table(title="Funcionalidades Demostradas")
        summary_table.add_column("Funcionalidad", style="cyan")
        summary_table.add_column("Estado", style="green")

        summary_table.add_row("✅ Captura de commits Git (N2)", "Completado")
        summary_table.add_row("✅ Detección de patrones de código", "Completado")
        summary_table.add_row("✅ Correlación Git ↔ Cognición (N2 ↔ N4)", "Completado")
        summary_table.add_row("✅ Análisis de evolución de código", "Completado")
        summary_table.add_row("✅ Reportes de cohorte", "Completado")
        summary_table.add_row("✅ Dashboard de riesgos", "Completado")
        summary_table.add_row("✅ Alertas automáticas", "Completado")
        summary_table.add_row("✅ Planes de remediación", "Completado")

        console.print(summary_table)

        console.print()
        print_success("Demo de Sprint 5 completado exitosamente")
        console.print()
        console.print("[bold cyan]Próximos pasos:[/bold cyan]")
        console.print("  1. Probar endpoints API REST en http://localhost:8000/docs")
        console.print("  2. Ejecutar tests: pytest tests/ -v")
        console.print("  3. Revisar documentación en SPRINT_5_COMPLETADO.md")
        console.print()

    except Exception as e:
        print_error(f"Error en demo: {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
