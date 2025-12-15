"""
Ejemplo básico de uso del ecosistema AI-Native

Demuestra:
1. Creación de sesión
2. Interacción con T-IA-Cog (Tutor)
3. Captura de trazabilidad N4
4. Evaluación de procesos (E-IA-Proc)
5. Análisis de riesgos (AR-IA)
"""
import sys
import io
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_native_mvp import AIGateway
from src.ai_native_mvp.agents import EvaluadorProcesosAgent, AnalistaRiesgoAgent
from src.ai_native_mvp.core.cognitive_engine import AgentMode


def main():
    print("=" * 70)
    print("EJEMPLO BÁSICO: Ecosistema AI-Native")
    print("=" * 70)

    # 1. Crear gateway
    print("\n[1] Inicializando AI Gateway...")
    gateway = AIGateway(llm_provider="mock")

    # 2. Crear sesión para un estudiante
    print("[2] Creando sesión de aprendizaje...")
    session_id = gateway.create_session(
        student_id="estudiante_001",
        activity_id="prog2_tp1_colas"
    )
    print(f"    ✓ Sesión creada: {session_id}")

    # 3. Configurar modo Tutor
    print("\n[3] Configurando modo T-IA-Cog (Tutor)...")
    gateway.set_mode(session_id, AgentMode.TUTOR)

    # 4. Simular interacciones del estudiante
    print("\n[4] Simulando interacciones estudiante-IA...\n")

    interacciones = [
        "Dame el código completo de una cola con arreglos",  # Delegación total
        "No entiendo qué es una cola. ¿Me podés explicar?",  # Búsqueda conceptual
        "Planeo usar un arreglo circular con dos índices. ¿Es correcto?",  # Planificación
    ]

    for i, prompt in enumerate(interacciones, 1):
        print(f"\n--- Interacción {i} ---")
        print(f"Estudiante: {prompt[:60]}...")

        # Procesar interacción
        response = gateway.process_interaction(
            session_id=session_id,
            prompt=prompt
        )

        # Mostrar resultado
        if response.get("blocked"):
            print(f"❌ BLOQUEADO: {response.get('reason')}")
        else:
            print(f"🤖 Tutor: {response['message'][:100]}...")
            print(f"   Tipo de respuesta: {response.get('strategy', {}).get('response_type', 'N/A')}")

    # 5. Obtener trazabilidad
    print("\n" + "=" * 70)
    print("[5] Análisis de Trazabilidad N4")
    print("=" * 70)

    trace_sequence = gateway.get_trace_sequence(session_id)
    print(f"\nTotal de trazas capturadas: {len(trace_sequence.traces)}")
    print(f"Cambios de estrategia: {trace_sequence.strategy_changes}")
    print(f"Dependencia de IA: {trace_sequence.ai_dependency_score:.1%}")

    print("\nCamino cognitivo:")
    cognitive_path = trace_sequence.get_cognitive_path()
    for i, step in enumerate(cognitive_path[:5], 1):
        print(f"  {i}. {step}")

    # 6. Generar evaluación del proceso
    print("\n" + "=" * 70)
    print("[6] Evaluación de Procesos Cognitivos (E-IA-Proc)")
    print("=" * 70)

    evaluator = EvaluadorProcesosAgent()
    evaluation = evaluator.evaluate_process(trace_sequence)

    print(f"\n📊 Nivel de competencia: {evaluation.overall_competency_level.value}")
    print(f"📈 Puntuación: {evaluation.overall_score:.1f}/10")

    print("\nDimensiones evaluadas:")
    for dim in evaluation.dimensions:
        print(f"  • {dim.name}: {dim.score:.1f}/10 ({dim.level.value})")

    if evaluation.key_strengths:
        print("\n✅ Fortalezas:")
        for strength in evaluation.key_strengths:
            print(f"  • {strength}")

    if evaluation.improvement_areas:
        print("\n⚠️  Áreas de mejora:")
        for area in evaluation.improvement_areas:
            print(f"  • {area}")

    # 7. Análisis de riesgos
    print("\n" + "=" * 70)
    print("[7] Análisis de Riesgos (AR-IA)")
    print("=" * 70)

    analyst = AnalistaRiesgoAgent()
    risk_report = analyst.analyze_session(trace_sequence)

    print(f"\n⚠️  Total de riesgos detectados: {risk_report.total_risks}")
    print(f"  🔴 Críticos: {risk_report.critical_risks}")
    print(f"  🟠 Altos: {risk_report.high_risks}")
    print(f"  🟡 Medios: {risk_report.medium_risks}")

    if risk_report.risks:
        print("\nRiesgos principales:")
        for risk in risk_report.risks[:3]:
            print(f"\n  • {risk.risk_type.value} ({risk.risk_level.value})")
            print(f"    {risk.description}")
            if risk.recommendations:
                print(f"    💡 Recomendación: {risk.recommendations[0]}")

    print("\nEvaluación general:")
    print(f"  {risk_report.overall_assessment}")

    # 8. Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE LA SESIÓN")
    print("=" * 70)
    print(f"""
Estudiante: {trace_sequence.student_id}
Actividad: {trace_sequence.activity_id}
Interacciones: {len(trace_sequence.traces)}
Nivel alcanzado: {evaluation.overall_competency_level.value}
Riesgos detectados: {risk_report.total_risks}
Dependencia IA: {trace_sequence.ai_dependency_score:.1%}

El ecosistema AI-Native capturó todo el proceso cognitivo híbrido humano-IA,
permitiendo una evaluación basada en el razonamiento y no solo en el producto final.
    """)

    print("=" * 70)
    print("✅ Ejemplo completado exitosamente")
    print("=" * 70)


if __name__ == "__main__":
    main()