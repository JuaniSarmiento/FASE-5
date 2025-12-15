"""
Interfaz CLI para interactuar con el ecosistema AI-Native
"""
import sys
import io
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.table import Table

from .core import AIGateway
from .core.cognitive_engine import AgentMode
from .agents import SimuladorType

# Fix Windows encoding for Unicode characters
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

console = Console()


class AINativeCLI:
    """CLI interactiva para el ecosistema AI-Native"""

    def __init__(self):
        self.gateway = AIGateway()
        self.current_session: Optional[str] = None
        self.student_id: Optional[str] = None
        self.activity_id: Optional[str] = None

    def run(self):
        """Ejecuta el CLI principal"""
        self.show_welcome()

        # Setup inicial
        self.student_id = Prompt.ask("\n👤 Ingrese su ID de estudiante")
        self.activity_id = Prompt.ask("📚 Ingrese el ID de la actividad")

        # Crear sesión
        self.current_session = self.gateway.create_session(
            student_id=self.student_id,
            activity_id=self.activity_id
        )

        console.print(f"\n✅ Sesión creada: [cyan]{self.current_session}[/cyan]\n")

        # Seleccionar modo
        mode = self.select_mode()
        self.gateway.set_mode(self.current_session, mode)

        # Loop principal
        self.interaction_loop(mode)

    def show_welcome(self):
        """Muestra mensaje de bienvenida"""
        welcome_text = """
# 🎓 Ecosistema AI-Native MVP

Sistema de enseñanza-aprendizaje de programación con IA generativa.

## Submodelos Disponibles:
- **T-IA-Cog**: Tutor IA Disciplinar Cognitivo
- **E-IA-Proc**: Evaluador de Procesos Cognitivos
- **S-IA-X**: Simuladores Profesionales
- **AR-IA**: Analista de Riesgo Cognitivo y Ético
- **GOV-IA**: Gobernanza Institucional
- **TC-N4**: Trazabilidad Cognitiva

Desarrollado conforme a:
- UNESCO (2021), OECD (2019), IEEE (2019)
- ISO/IEC 23894:2023, ISO/IEC 42001:2023
        """
        console.print(Panel(Markdown(welcome_text), border_style="blue"))

    def select_mode(self) -> AgentMode:
        """Permite al usuario seleccionar el modo de interacción"""
        console.print("\n[bold]Seleccione el modo de interacción:[/bold]\n")

        modes = [
            ("1", "Tutor IA Cognitivo (T-IA-Cog)", AgentMode.TUTOR),
            ("2", "Simulador Profesional (S-IA-X)", AgentMode.SIMULATOR),
            ("3", "Evaluador de Procesos (E-IA-Proc)", AgentMode.EVALUATOR),
        ]

        for key, name, _ in modes:
            console.print(f"  {key}. {name}")

        choice = Prompt.ask("\nOpción", choices=["1", "2", "3"], default="1")

        selected_mode = next(mode for key, _, mode in modes if key == choice)
        console.print(f"\n✅ Modo seleccionado: [green]{selected_mode.value}[/green]\n")

        return selected_mode

    def interaction_loop(self, mode: AgentMode):
        """Loop principal de interacción"""
        console.print("[bold cyan]Comenzando sesión de trabajo...[/bold cyan]")
        console.print("(Escribe 'salir' para terminar, 'eval' para generar evaluación, 'riesgos' para ver riesgos)\n")

        while True:
            try:
                # Solicitar entrada
                user_input = Prompt.ask("\n[bold green]Tu mensaje[/bold green]")

                if user_input.lower() in ["salir", "exit", "quit"]:
                    self.handle_exit()
                    break

                if user_input.lower() == "eval":
                    self.show_evaluation()
                    continue

                if user_input.lower() == "riesgos":
                    self.show_risks()
                    continue

                if user_input.lower() == "trazas":
                    self.show_traces()
                    continue

                # Procesar interacción
                response = self.gateway.process_interaction(
                    session_id=self.current_session,
                    prompt=user_input
                )

                # Mostrar respuesta
                self.display_response(response)

            except KeyboardInterrupt:
                console.print("\n\n[yellow]Sesión interrumpida[/yellow]")
                self.handle_exit()
                break
            except Exception as e:
                console.print(f"\n[red]Error: {str(e)}[/red]\n")

    def display_response(self, response: dict):
        """Muestra la respuesta del sistema"""
        message = response.get("message", "")
        mode = response.get("mode", "unknown")

        # Panel con la respuesta
        panel_title = f"🤖 Respuesta ({mode})"

        if response.get("blocked", False):
            panel_style = "red"
            panel_title = "🚫 Solicitud Bloqueada"
        else:
            panel_style = "blue"

        console.print(Panel(
            Markdown(message),
            title=panel_title,
            border_style=panel_style
        ))

        # Mostrar metadata si está disponible
        if "metadata" in response:
            metadata = response["metadata"]
            if "response_type" in metadata:
                console.print(f"\n💡 Tipo de respuesta: [cyan]{metadata['response_type']}[/cyan]")
            if "cognitive_state" in metadata:
                console.print(f"🧠 Estado cognitivo: [cyan]{metadata['cognitive_state']}[/cyan]")

    def show_evaluation(self):
        """Muestra evaluación del proceso"""
        console.print("\n[bold]📊 Generando Evaluación de Procesos...[/bold]\n")

        # Obtener secuencia de trazas
        trace_sequence = self.gateway.get_trace_sequence(self.current_session)

        if not trace_sequence or len(trace_sequence.traces) == 0:
            console.print("[yellow]No hay suficientes trazas para evaluar[/yellow]\n")
            return

        # Generar evaluación usando E-IA-Proc
        from .agents import EvaluadorProcesosAgent
        evaluator = EvaluadorProcesosAgent()
        report = evaluator.evaluate_process(trace_sequence)

        # Mostrar resumen
        table = Table(title="Resumen de Evaluación")
        table.add_column("Dimensión", style="cyan")
        table.add_column("Nivel", style="green")
        table.add_column("Puntuación", justify="right", style="yellow")

        for dim in report.dimensions:
            table.add_row(
                dim.name,
                dim.level.value,
                f"{dim.score:.1f}/10"
            )

        console.print(table)

        # Evaluación general
        console.print(f"\n[bold]Nivel General:[/bold] [green]{report.overall_competency_level.value}[/green]")
        console.print(f"[bold]Puntuación:[/bold] [yellow]{report.overall_score:.1f}/10[/yellow]")

        # Fortalezas
        if report.key_strengths:
            console.print("\n[bold green]✅ Fortalezas:[/bold green]")
            for strength in report.key_strengths:
                console.print(f"  • {strength}")

        # Áreas de mejora
        if report.improvement_areas:
            console.print("\n[bold yellow]⚠️  Áreas de Mejora:[/bold yellow]")
            for area in report.improvement_areas:
                console.print(f"  • {area}")

        # Recomendaciones
        if report.recommendations_student:
            console.print("\n[bold cyan]💡 Recomendaciones:[/bold cyan]")
            for rec in report.recommendations_student:
                console.print(f"  • {rec}")

    def show_risks(self):
        """Muestra análisis de riesgos"""
        console.print("\n[bold]⚠️  Análisis de Riesgos (AR-IA)...[/bold]\n")

        # Obtener reporte de riesgos
        risk_report = self.gateway.get_risk_report(self.student_id, self.activity_id)

        if not risk_report:
            console.print("[green]✅ No se detectaron riesgos[/green]\n")
            return

        # Resumen
        console.print(f"[bold]Total de riesgos:[/bold] {risk_report.total_risks}")
        console.print(f"  🔴 Críticos: {risk_report.critical_risks}")
        console.print(f"  🟠 Altos: {risk_report.high_risks}")
        console.print(f"  🟡 Medios: {risk_report.medium_risks}")
        console.print(f"  🟢 Bajos: {risk_report.low_risks}\n")

        # Riesgos individuales
        if risk_report.risks:
            console.print("[bold]Riesgos Detectados:[/bold]\n")
            for risk in risk_report.risks[:5]:  # Top 5
                level_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢"
                }
                emoji = level_emoji.get(risk.risk_level.value, "⚪")

                console.print(f"{emoji} [bold]{risk.risk_type.value}[/bold] ({risk.risk_level.value})")
                console.print(f"   {risk.description}")

                if risk.recommendations:
                    console.print(f"   💡 {risk.recommendations[0]}")
                console.print()

        # Evaluación general
        if risk_report.overall_assessment:
            console.print(f"[bold]Evaluación general:[/bold] {risk_report.overall_assessment}\n")

    def show_traces(self):
        """Muestra trazas cognitivas"""
        console.print("\n[bold]🔍 Trazabilidad Cognitiva N4...[/bold]\n")

        trace_sequence = self.gateway.get_trace_sequence(self.current_session)

        if not trace_sequence or len(trace_sequence.traces) == 0:
            console.print("[yellow]No hay trazas disponibles[/yellow]\n")
            return

        console.print(f"[bold]Total de interacciones:[/bold] {len(trace_sequence.traces)}")
        console.print(f"[bold]Cambios de estrategia:[/bold] {trace_sequence.strategy_changes}")
        console.print(f"[bold]Dependencia IA:[/bold] {trace_sequence.ai_dependency_score:.1%}\n")

        # Camino cognitivo
        cognitive_path = trace_sequence.get_cognitive_path()
        if cognitive_path:
            console.print("[bold cyan]Camino Cognitivo:[/bold cyan]")
            console.print(" → ".join(cognitive_path[:10]))
            console.print()

        # Últimas 5 trazas
        console.print("[bold]Últimas Interacciones:[/bold]\n")
        for trace in trace_sequence.traces[-5:]:
            console.print(f"[cyan]{trace.timestamp.strftime('%H:%M:%S')}[/cyan] "
                         f"[yellow]{trace.interaction_type.value}[/yellow]")
            console.print(f"  {trace.content[:80]}...")
            console.print()

    def handle_exit(self):
        """Maneja la salida del programa"""
        console.print("\n[bold]📊 Resumen de la Sesión:[/bold]\n")

        trace_sequence = self.gateway.get_trace_sequence(self.current_session)
        if trace_sequence:
            console.print(f"Total de interacciones: {len(trace_sequence.traces)}")
            console.print(f"Dependencia de IA: {trace_sequence.ai_dependency_score:.1%}")

        if Confirm.ask("\n¿Desea generar evaluación final?"):
            self.show_evaluation()

        if Confirm.ask("\n¿Desea ver análisis de riesgos?"):
            self.show_risks()

        console.print("\n[bold green]¡Hasta pronto! 👋[/bold green]\n")


def main():
    """Punto de entrada del CLI"""
    try:
        cli = AINativeCLI()
        cli.run()
    except Exception as e:
        console.print(f"\n[red]Error fatal: {str(e)}[/red]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()