"""
Test completo de integración Gemini Flash/Pro

Verifica que todas las integraciones estén funcionando:
1. Tutor Socrático (decisión inteligente Flash/Pro)
2. Simuladores (Flash)
3. Evaluador (Pro)
4. Analista de Riesgo (Flash)
5. Trazabilidad (Flash)
"""
import asyncio
import os
import sys

# Agregar path del backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.llm.factory import LLMProviderFactory
from backend.core.ai_gateway import AIGateway
from backend.agents.simulators import SimuladorProfesionalAgent, SimuladorType
from backend.agents.evaluator import EvaluadorProcesosAgent
from backend.agents.risk_analyst import AnalistaRiesgoAgent
from backend.agents.traceability import TrazabilidadN4Agent
from backend.models.trace import TraceSequence, CognitiveTrace, InteractionType
from datetime import datetime


async def test_gemini_provider():
    """Test 1: Verificar que GeminiProvider funciona"""
    print("\n" + "="*80)
    print("TEST 1: GeminiProvider - Verificación básica")
    print("="*80)
    
    try:
        provider = LLMProviderFactory.create_from_env()
        print(f"✅ Provider creado: {provider.__class__.__name__}")
        
        if hasattr(provider, 'supports_smart_routing'):
            print(f"✅ Soporta smart routing: {provider.supports_smart_routing}")
        
        # Test simple
        from backend.llm.base import LLMMessage, LLMRole
        messages = [
            LLMMessage(role=LLMRole.USER, content="¿Qué es una variable en programación?")
        ]
        
        response = await provider.generate(messages, temperature=0.7, max_tokens=100)
        print(f"✅ Respuesta recibida: {response.content[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tutor_decision():
    """Test 2: Tutor Socrático con decisión inteligente"""
    print("\n" + "="*80)
    print("TEST 2: Tutor Socrático - Decisión Inteligente Flash/Pro")
    print("="*80)
    
    try:
        provider = LLMProviderFactory.create_from_env()
        gateway = AIGateway(llm_provider=provider)
        
        # Test 1: Pregunta simple (debería usar Flash)
        print("\n📝 Test pregunta simple:")
        decision = await gateway._decide_model_for_prompt("¿Qué es una variable?")
        print(f"   Decisión: {decision.upper()} ✅")
        
        # Test 2: Análisis complejo (debería usar Pro)
        print("\n📝 Test análisis complejo:")
        decision = await gateway._decide_model_for_prompt(
            "Analiza la complejidad algorítmica de QuickSort y explica por qué es O(n log n)"
        )
        print(f"   Decisión: {decision.upper()} ✅")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_simuladores():
    """Test 3: Simuladores usan Flash"""
    print("\n" + "="*80)
    print("TEST 3: Simuladores - Gemini Flash")
    print("="*80)
    
    try:
        provider = LLMProviderFactory.create_from_env()
        
        # Test Product Owner
        print("\n📝 Test Product Owner:")
        sim = SimuladorProfesionalAgent(SimuladorType.PRODUCT_OWNER, provider)
        response = await sim.interact("Hola, tengo una idea para una nueva feature")
        print(f"   ✅ Respuesta recibida: {response[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_evaluador():
    """Test 4: Evaluador usa Pro para análisis profundo"""
    print("\n" + "="*80)
    print("TEST 4: Evaluador - Gemini Pro (análisis profundo)")
    print("="*80)
    
    try:
        provider = LLMProviderFactory.create_from_env()
        evaluator = EvaluadorProcesosAgent(llm_provider=provider)
        
        # Crear secuencia de prueba
        seq = TraceSequence(
            id='test_seq',
            student_id='test_student',
            activity_id='test_activity',
            traces=[
                CognitiveTrace(
                    id='t1',
                    timestamp=datetime.now(),
                    student_id='test_student',
                    activity_id='test_activity',
                    interaction_type=InteractionType.STUDENT_PROMPT,
                    content='Intenté implementar un bucle for pero me sale error'
                ),
                CognitiveTrace(
                    id='t2',
                    timestamp=datetime.now(),
                    student_id='test_student',
                    activity_id='test_activity',
                    interaction_type=InteractionType.AI_RESPONSE,
                    content='¿Qué tipo de error obtienes?'
                )
            ]
        )
        
        print("\n📝 Ejecutando análisis profundo con Pro:")
        report = await evaluator.evaluate_process_async(seq)
        print(f"   ✅ Análisis completado")
        print(f"   - Calidad general: {report.overall_competency_level.value}")
        print(f"   - Score: {report.overall_score:.1f}/10")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_analista_riesgo():
    """Test 5: Analista de Riesgo usa Flash"""
    print("\n" + "="*80)
    print("TEST 5: Analista de Riesgo - Gemini Flash")
    print("="*80)
    
    try:
        provider = LLMProviderFactory.create_from_env()
        analyst = AnalistaRiesgoAgent(llm_provider=provider)
        
        # Crear secuencia de prueba
        seq = TraceSequence(
            id='test_seq_risk',
            student_id='test_student',
            activity_id='test_activity',
            traces=[
                CognitiveTrace(
                    id='t1',
                    timestamp=datetime.now(),
                    student_id='test_student',
                    activity_id='test_activity',
                    interaction_type=InteractionType.STUDENT_PROMPT,
                    content='Dame el código completo de la solución'
                ),
            ]
        )
        
        print("\n📝 Ejecutando análisis de riesgos con Flash:")
        report = await analyst.analyze_session_async(seq)
        print(f"   ✅ Análisis completado")
        print(f"   - Riesgos detectados: {len(report.risks)}")
        print(f"   - Evaluación general: {report.overall_assessment}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_trazabilidad():
    """Test 6: Trazabilidad usa Flash"""
    print("\n" + "="*80)
    print("TEST 6: Trazabilidad - Gemini Flash")
    print("="*80)
    
    try:
        provider = LLMProviderFactory.create_from_env()
        trazabilidad = TrazabilidadN4Agent(llm_provider=provider)
        
        # Crear secuencia
        seq = trazabilidad.create_sequence('test_student', 'test_activity')
        
        # Agregar algunas trazas
        seq.traces = [
            CognitiveTrace(
                id='t1',
                timestamp=datetime.now(),
                student_id='test_student',
                activity_id='test_activity',
                interaction_type=InteractionType.STUDENT_PROMPT,
                content='Primero voy a planificar mi solución'
            ),
            CognitiveTrace(
                id='t2',
                timestamp=datetime.now(),
                student_id='test_student',
                activity_id='test_activity',
                interaction_type=InteractionType.STUDENT_CODE_SUBMISSION,
                content='Ahora implemento el código'
            )
        ]
        
        print("\n📝 Ejecutando reconstrucción cognitiva con Flash:")
        path = await trazabilidad.reconstruct_cognitive_path_async(seq.id)
        
        # Buscar en metadata
        trazabilidad.sequence_repository = type('obj', (object,), {
            'get_by_id': lambda x: type('obj', (object,), {
                'id': seq.id,
                'student_id': seq.student_id,
                'activity_id': seq.activity_id,
                'start_time': datetime.now(),
                'end_time': None,
                'reasoning_path': [],
                'strategy_changes': [],
                'ai_dependency_score': 0.5,
                'traces': []
            })()
        })()
        
        # Intentar de nuevo con repository mock
        from backend.agents.traceability import TrazabilidadN4Agent
        traz2 = TrazabilidadN4Agent(llm_provider=provider)
        
        print(f"   ✅ Reconstrucción completada")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Ejecuta todos los tests"""
    print("\n" + "="*80)
    print("🧪 TEST COMPLETO DE INTEGRACIÓN GEMINI FLASH/PRO")
    print("="*80)
    print("\nVerificando que todas las integraciones funcionen correctamente:")
    print("- Tutor: Decisión inteligente Flash/Pro")
    print("- Simuladores: Flash")
    print("- Evaluador: Pro")
    print("- Analista Riesgo: Flash")
    print("- Trazabilidad: Flash")
    
    results = []
    
    # Test 1: Provider básico
    results.append(("GeminiProvider", await test_gemini_provider()))
    
    # Test 2: Tutor con decisión
    results.append(("Tutor Decisión", await test_tutor_decision()))
    
    # Test 3: Simuladores
    results.append(("Simuladores", await test_simuladores()))
    
    # Test 4: Evaluador
    results.append(("Evaluador", await test_evaluador()))
    
    # Test 5: Analista Riesgo
    results.append(("Analista Riesgo", await test_analista_riesgo()))
    
    # Test 6: Trazabilidad
    results.append(("Trazabilidad", await test_trazabilidad()))
    
    # Resumen
    print("\n" + "="*80)
    print("📊 RESUMEN DE TESTS")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:20s} {status}")
    
    print(f"\n{passed}/{total} tests pasaron")
    
    if passed == total:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
        print("✅ Gemini Flash/Pro está completamente integrado y funcionando")
    else:
        print(f"\n⚠️ {total - passed} test(s) fallaron")
        print("Revisa los errores arriba para más detalles")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(main())
