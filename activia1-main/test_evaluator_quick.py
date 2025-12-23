"""
Test rápido del code evaluator para debug
"""
import asyncio
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# NO importar nada de backend que requiera BD
# Importar solo lo necesario


async def test_evaluator():
    """Test del evaluator con un ejercicio real"""
    
    print("=" * 80)
    print("🧪 TEST DEL CODE EVALUATOR")
    print("=" * 80)
    
    # 1. Verificar configuración
    print("\n📋 CONFIGURACIÓN:")
    print(f"   LLM_PROVIDER: {os.getenv('LLM_PROVIDER', 'no configurado')}")
    print(f"   MISTRAL_API_KEY: {'✓ configurada' if os.getenv('MISTRAL_API_KEY') else '✗ no configurada'}")
    print(f"   MISTRAL_MODEL: {os.getenv('MISTRAL_MODEL', 'mistral-small-latest')}")
    
    # 2. Inicializar LLM provider (importar aquí para evitar imports de BD)
    print("\n🤖 Inicializando LLM provider...")
    try:
        # Import local para evitar cargar BD
        sys.path.insert(0, str(Path(__file__).parent))
        from backend.llm.factory import LLMProviderFactory
        
        llm_provider = LLMProviderFactory.create_from_env(os.getenv('LLM_PROVIDER', 'mock'))
        model_info = llm_provider.get_model_info()
        print(f"   ✓ Provider inicializado: {model_info.get('provider', 'unknown')}")
        print(f"   ✓ Model: {model_info.get('model', 'unknown')}")
    except Exception as e:
        print(f"   ✗ Error inicializando provider: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 3. Cargar ejercicio (importar aquí para evitar problemas de BD)
    print("\n📚 Cargando ejercicio U1-VAR-01...")
    try:
        from backend.data.exercises.loader import ExerciseLoader
        loader = ExerciseLoader()
        exercise = loader.get_by_id('U1-VAR-01')
        
        if not exercise:
            print("   ✗ Ejercicio no encontrado")
            return
        
        print(f"   ✓ Ejercicio cargado: {exercise['meta']['title']}")
    except Exception as e:
        print(f"   ✗ Error cargando ejercicio: {e}")
        return
    
    # 4. Código del estudiante (CORRECTO)
    student_code = """
ventas_enero = 12500
ventas_febrero = 15300
ventas_marzo = 14800

total = ventas_enero + ventas_febrero + ventas_marzo
promedio = total / 3

print(f"Total: ${total}")
print(f"Promedio: ${promedio:.2f}")
"""
    
    # 5. Simular sandbox result (código correcto)
    sandbox_result = {
        "exit_code": 0,
        "stdout": "Total: $42600\nPromedio: $14200.00",
        "stderr": "",
        "execution_time_ms": 10,
        "tests_passed": 1,
        "tests_total": 1,
        "language": "python",
        "evaluation_type": "execution"
    }
    
    print(f"\n🏃 Ejecutando evaluación...")
    print(f"   Tests: {sandbox_result['tests_passed']}/{sandbox_result['tests_total']}")
    
    # 6. Evaluar (importar aquí para evitar imports de BD)
    try:
        from backend.services.code_evaluator import CodeEvaluator
        evaluator = CodeEvaluator(llm_client=llm_provider)
    except Exception as e:
        print(f"   ✗ Error importando CodeEvaluator: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        result = await evaluator.evaluate(
            exercise=exercise,
            student_code=student_code,
            sandbox_result=sandbox_result
        )
        
        print("\n" + "=" * 80)
        print("📊 RESULTADO DE LA EVALUACIÓN")
        print("=" * 80)
        print(f"\n✅ Score: {result['evaluation']['score']}/100")
        print(f"   Status: {result['evaluation']['status']}")
        print(f"   Title: {result['evaluation']['title']}")
        print(f"\n📝 Summary:")
        print(f"   {result['evaluation']['summary_markdown'][:200]}...")
        print(f"\n🎮 Gamification:")
        print(f"   XP Earned: {result['gamification']['xp_earned']}")
        print(f"   Achievements: {result['gamification']['achievements_unlocked']}")
        
        print("\n✅ TEST EXITOSO!")
        
    except Exception as e:
        print(f"\n❌ ERROR EN EVALUACIÓN: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_evaluator())
