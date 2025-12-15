"""
Ejemplo Completo del Tutor Socrático V2.0

Demuestra el uso completo del sistema de tutor personalizado con:
1. Pipeline completo IPC -> GSR -> Andamiaje
2. Sistema de semáforos (Verde/Amarillo/Rojo)
3. Detección de eventos cognitivos
4. Analytics N4
"""
import sys
import os

# Añadir el backend al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.agents import (
    TutorCognitivoAgent,
    TutorRulesEngine,
    TutorGovernanceEngine,
    TutorMetadataTracker,
    CognitiveScaffoldingLevel,
    SemaforoState,
    InterventionType,
    StudentCognitiveEvent
)


def print_section(title: str):
    """Imprime sección con formato"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_response(response: dict):
    """Imprime respuesta del tutor con formato"""
    print(f"🎓 TUTOR:")
    print("-" * 80)
    print(response["message"])
    print("-" * 80)
    print(f"📊 Metadata:")
    print(f"  - Semáforo: {response.get('semaforo', 'N/A')}")
    print(f"  - Intervención: {response.get('intervention_type', 'N/A')}")
    print(f"  - Nivel de ayuda: {response.get('help_level', 'N/A')}")
    print(f"  - Requiere respuesta: {response.get('requires_student_response', False)}")
    print()


def ejemplo_1_rechazo_codigo_directo():
    """
    Ejemplo 1: Estudiante pide código directo
    Resultado esperado: Semáforo ROJO, Rechazo Pedagógico
    """
    print_section("EJEMPLO 1: Solicitud de Código Directo (Regla Anti-Solución)")
    
    tutor = TutorCognitivoAgent()
    
    # Perfil de estudiante novato con poca autonomía
    student_profile = {
        "avg_ai_involvement": 0.8,  # Alta dependencia de IA
        "successful_autonomous_solutions": 2,
        "error_self_correction_rate": 0.1
    }
    
    # Request del estudiante
    student_request = "Haceme el código completo de una cola con arreglos en Python"
    
    print(f"👨‍🎓 ESTUDIANTE: {student_request}\n")
    
    # Procesar request
    response = tutor.process_student_request(
        session_id="ejemplo_1",
        student_prompt=student_request,
        student_profile=student_profile,
        conversation_history=[]
    )
    
    print_response(response)
    
    # Verificaciones
    assert response["semaforo"] == "rojo", "Debería activar semáforo ROJO"
    assert "no puedo" in response["message"].lower() or "prohibido" in response["message"].lower()
    
    print("✅ VERIFICACIÓN: Semáforo ROJO activado correctamente\n")


def ejemplo_2_pregunta_socratica():
    """
    Ejemplo 2: Estudiante hace pregunta exploratoria
    Resultado esperado: Semáforo VERDE, Preguntas Socráticas
    """
    print_section("EJEMPLO 2: Pregunta Exploratoria (Modo Socrático)")
    
    tutor = TutorCognitivoAgent()
    
    # Perfil de estudiante intermedio con autonomía moderada
    student_profile = {
        "avg_ai_involvement": 0.4,
        "successful_autonomous_solutions": 8,
        "error_self_correction_rate": 0.5
    }
    
    student_request = "No entiendo cómo implementar una cola. ¿Me podés ayudar?"
    
    print(f"👨‍🎓 ESTUDIANTE: {student_request}\n")
    
    response = tutor.process_student_request(
        session_id="ejemplo_2",
        student_prompt=student_request,
        student_profile=student_profile,
        conversation_history=[]
    )
    
    print_response(response)
    
    # Verificaciones
    assert response["semaforo"] == "verde", "Debería estar en VERDE"
    assert "?" in response["message"], "Debería contener preguntas"
    
    print("✅ VERIFICACIÓN: Modo socrático activado correctamente\n")


def ejemplo_3_evaluacion_respuesta():
    """
    Ejemplo 3: Evaluación de respuesta del estudiante
    Detecta eventos cognitivos y efectividad
    """
    print_section("EJEMPLO 3: Evaluación de Respuesta del Estudiante")
    
    tutor = TutorCognitivoAgent()
    
    student_profile = {
        "avg_ai_involvement": 0.5,
        "successful_autonomous_solutions": 5,
        "error_self_correction_rate": 0.4
    }
    
    # Primera interacción
    print(f"👨‍🎓 ESTUDIANTE: ¿Cómo funciona una pila?\n")
    
    response = tutor.process_student_request(
        session_id="ejemplo_3",
        student_prompt="¿Cómo funciona una pila?",
        student_profile=student_profile,
        conversation_history=[]
    )
    
    print_response(response)
    
    interaction_id = response["metadata"]["interaction_id"]
    
    # Respuesta del estudiante (con justificación y planificación)
    student_response = """
    Entiendo que una pila es una estructura LIFO (Last In, First Out).
    
    Mi plan es implementarla con un arreglo porque:
    1. Es simple de entender
    2. Permite acceso directo al tope
    3. Las operaciones push/pop son O(1)
    
    Primero voy a crear la clase con el arreglo interno.
    Luego implementaré push() que agrega al final.
    Finalmente pop() que quita del final.
    
    ¿Está bien este enfoque?
    """
    
    print(f"👨‍🎓 RESPUESTA DEL ESTUDIANTE:\n{student_response}\n")
    
    # Evaluar respuesta
    evaluation = tutor.evaluate_student_response_v2(
        session_id="ejemplo_3",
        interaction_id=interaction_id,
        student_response=student_response,
        time_to_response_minutes=3.5
    )
    
    print("📊 EVALUACIÓN:")
    print(f"  - Eventos cognitivos: {evaluation['cognitive_events']}")
    print(f"  - Efectividad: {evaluation['effectiveness']}")
    print(f"  - Ajustar estrategia: {evaluation['should_adjust_strategy']}")
    
    # Verificaciones
    assert len(evaluation['cognitive_events']) > 0, "Debería detectar eventos cognitivos"
    assert 'justificacion_decision' in evaluation['cognitive_events']
    assert 'planificacion' in evaluation['cognitive_events']
    
    print("\n✅ VERIFICACIÓN: Eventos cognitivos detectados correctamente\n")


def ejemplo_4_alta_dependencia_ia():
    """
    Ejemplo 4: Estudiante con alta dependencia de IA
    Resultado esperado: Semáforo AMARILLO, Reducción de ayuda
    """
    print_section("EJEMPLO 4: Alta Dependencia de IA (Semáforo Amarillo)")
    
    tutor = TutorCognitivoAgent()
    
    # Perfil con alta dependencia de IA
    student_profile = {
        "avg_ai_involvement": 0.75,  # Alta dependencia (>0.7)
        "successful_autonomous_solutions": 1,
        "error_self_correction_rate": 0.1
    }
    
    student_request = "¿Cómo ordenar un array?"
    
    print(f"👨‍🎓 ESTUDIANTE: {student_request}\n")
    
    response = tutor.process_student_request(
        session_id="ejemplo_4",
        student_prompt=student_request,
        student_profile=student_profile,
        conversation_history=[]
    )
    
    print_response(response)
    
    # Verificaciones
    assert response["semaforo"] == "amarillo", "Debería activar semáforo AMARILLO por alta dependencia"
    
    print("✅ VERIFICACIÓN: Semáforo AMARILLO activado por alta dependencia de IA\n")


def ejemplo_5_analytics_n4():
    """
    Ejemplo 5: Generar analytics N4 de una sesión completa
    """
    print_section("EJEMPLO 5: Analytics N4 de Sesión Completa")
    
    tutor = TutorCognitivoAgent()
    session_id = "ejemplo_5"
    
    # Simular múltiples interacciones
    interactions = [
        ("Haceme el código de un árbol binario", 0.8),  # Alta dependencia
        ("Ok, ¿qué es un árbol binario?", 0.7),
        ("Creo que cada nodo tiene dos hijos. Mi plan es...", 0.5),
        ("Implementé esto [muestra código]. ¿Está bien?", 0.4),
        ("Me di cuenta del error, lo corrijo", 0.3),
    ]
    
    for i, (prompt, ai_involvement) in enumerate(interactions, 1):
        print(f"\n--- Interacción {i} ---")
        print(f"👨‍🎓 ESTUDIANTE: {prompt}")
        
        student_profile = {
            "avg_ai_involvement": ai_involvement,
            "successful_autonomous_solutions": i,
            "error_self_correction_rate": 0.3 + (i * 0.1)
        }
        
        response = tutor.process_student_request(
            session_id=session_id,
            student_prompt=prompt,
            student_profile=student_profile,
            conversation_history=[]
        )
        
        print(f"🎓 TUTOR: [Semáforo: {response['semaforo']}] {response['intervention_type']}")
    
    # Generar analytics
    print("\n" + "=" * 80)
    print("📊 ANALYTICS N4 DE LA SESIÓN")
    print("=" * 80)
    
    analytics = tutor.get_session_analytics_n4(session_id)
    
    print(f"\n📈 Resumen de Sesión: {analytics['session_id']}")
    print(f"   Total de intervenciones: {analytics['total_interventions']}")
    print(f"\n📊 Distribución de Intervenciones:")
    for intervention_type, count in analytics['intervention_types_distribution'].items():
        print(f"   - {intervention_type}: {count}")
    
    print(f"\n🎯 Distribución de Semáforos:")
    for semaforo, count in analytics['semaforo_states_distribution'].items():
        print(f"   - {semaforo}: {count}")
    
    print(f"\n📈 Progresión de Autonomía:")
    print(f"   - Autonomía inicial: {analytics['initial_autonomy']:.2f}")
    print(f"   - Autonomía final: {analytics['final_autonomy']:.2f}")
    print(f"   - Mejora: {analytics['autonomy_improvement']:.2f}")
    
    if analytics['cognitive_events_detected']:
        print(f"\n🧠 Eventos Cognitivos Detectados:")
        for event, count in analytics['cognitive_events_detected'].items():
            print(f"   - {event}: {count}")
    
    print(f"\n🎓 Nivel de Ayuda Promedio: {analytics['avg_help_level']:.2f}")
    
    print("\n✅ Analytics N4 generados exitosamente\n")


def ejemplo_6_exigencia_justificacion():
    """
    Ejemplo 6: Estudiante da respuesta sin justificación
    Resultado esperado: Exigencia de explicitación
    """
    print_section("EJEMPLO 6: Exigencia de Justificación (Regla de Explicitación)")
    
    tutor = TutorCognitivoAgent()
    
    student_profile = {
        "avg_ai_involvement": 0.5,
        "successful_autonomous_solutions": 5,
        "error_self_correction_rate": 0.4
    }
    
    # Primera interacción - pregunta del tutor
    print("👨‍🎓 ESTUDIANTE: ¿Cuál es la mejor estructura para esto?\n")
    
    response1 = tutor.process_student_request(
        session_id="ejemplo_6",
        student_prompt="¿Cuál es la mejor estructura para esto?",
        student_profile=student_profile,
        conversation_history=[]
    )
    
    print_response(response1)
    
    # Respuesta corta sin justificación
    short_response = "Un HashMap"
    
    print(f"👨‍🎓 ESTUDIANTE: {short_response}\n")
    
    # Segunda interacción - debería exigir justificación
    response2 = tutor.process_student_request(
        session_id="ejemplo_6",
        student_prompt=short_response,
        student_profile=student_profile,
        conversation_history=[
            {"role": "tutor", "content": response1["message"]},
            {"role": "student", "content": short_response}
        ]
    )
    
    print_response(response2)
    
    # Verificaciones
    assert "justifi" in response2["message"].lower() or "por qué" in response2["message"].lower()
    
    print("✅ VERIFICACIÓN: Exigencia de justificación activada correctamente\n")


def main():
    """Ejecuta todos los ejemplos"""
    print("\n" + "🎓" * 40)
    print("  EJEMPLOS COMPLETOS - TUTOR SOCRÁTICO V2.0")
    print("🎓" * 40)
    
    try:
        ejemplo_1_rechazo_codigo_directo()
        ejemplo_2_pregunta_socratica()
        ejemplo_3_evaluacion_respuesta()
        ejemplo_4_alta_dependencia_ia()
        ejemplo_5_analytics_n4()
        ejemplo_6_exigencia_justificacion()
        
        print_section("🎉 TODOS LOS EJEMPLOS EJECUTADOS EXITOSAMENTE")
        
    except AssertionError as e:
        print(f"\n❌ ERROR EN VERIFICACIÓN: {e}\n")
        raise
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}\n")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
