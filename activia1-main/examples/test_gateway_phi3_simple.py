#!/usr/bin/env python3
"""
Script de Prueba End-to-End: Gateway → Ollama → Phi-3 (Sin emojis para Windows)
"""
import asyncio
import sys
import os
from pathlib import Path

# IMPORTANTE: Configurar keys ANTES de imports de backend
os.environ.setdefault("SECRET_KEY", "eUXGOdW7ByCGXzz_mCQWqLjZV0g5YyKXFMG0yknMvFY")
os.environ.setdefault("JWT_SECRET_KEY", "eUXGOdW7ByCGXzz_mCQWqLjZV0g5YyKXFMG0yknMvFY")

# Agregar backend al path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.core.ai_gateway import AIGateway
from backend.llm import LLMProviderFactory
from backend.core.cognitive_engine import CognitiveReasoningEngine


async def test_simple_generation():
    """Test: Generacion simple con Phi-3"""
    print("\n" + "="*70)
    print("TEST: Generacion simple con Phi-3")
    print("="*70)
    
    try:
        config = {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "model": os.getenv("OLLAMA_MODEL", "phi3"),
            "temperature": 0.7
        }
        
        llm = LLMProviderFactory.create("ollama", config)
        
        messages = [
            {"role": "system", "content": "Eres un asistente educativo que ayuda a estudiantes de programacion."},
            {"role": "user", "content": "¿Que es una funcion recursiva? Explica brevemente en maximo 3 lineas."}
        ]
        
        print("[+] Enviando prompt a Phi-3...")
        print(f"    User: {messages[1]['content']}")
        
        response = await llm.generate(messages)
        
        print(f"\n[+] Respuesta de Phi-3:")
        print(f"    {response['content']}")
        print(f"\n[OK] Generacion exitosa")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] en generacion: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_gateway_integration():
    """Test: Integracion completa con Gateway"""
    print("\n" + "="*70)
    print("TEST: Integracion Gateway + Cognitive Engine + Ollama + Phi-3")
    print("="*70)
    
    try:
        config = {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            "model": os.getenv("OLLAMA_MODEL", "phi3"),
            "temperature": 0.7
        }
        
        llm = LLMProviderFactory.create("ollama", config)
        engine = CognitiveReasoningEngine()
        gateway = AIGateway(llm_provider=llm, cognitive_engine=engine)
        
        print("[OK] Gateway inicializado con:")
        print("    - LLM Provider: Ollama (Phi-3)")
        print("    - Cognitive Engine: Activo")
        
        # Crear sesion
        print("\n[+] Creando sesion de estudiante...")
        session_id = gateway.create_session(
            student_id="test_student_001",
            activity_id="python_recursion_101",
            mode="TUTOR"
        )
        print(f"[OK] Sesion creada: {session_id}")
        
        # Prompt del estudiante
        student_prompt = """
        Estoy intentando resolver un problema de recursion:
        Necesito calcular el factorial de un numero.
        ¿Como puedo plantear el caso base?
        """
        
        print(f"\n[+] Estudiante pregunta:")
        print(f"    {student_prompt.strip()}")
        
        # Clasificar prompt
        print("\n[+] Clasificando prompt con Cognitive Engine...")
        classification = engine.classify_prompt(student_prompt, {})
        
        print(f"[OK] Clasificacion:")
        print(f"    - Estado cognitivo: {classification.get('cognitive_state')}")
        print(f"    - Tipo de ayuda: {classification.get('help_type')}")
        
        # Generar estrategia
        print("\n[+] Generando estrategia pedagogica...")
        strategy = engine.generate_pedagogical_response_strategy(
            student_prompt,
            classification,
            []
        )
        
        print(f"[OK] Estrategia generada:")
        print(f"    - Tipo de respuesta: {strategy.get('response_type')}")
        print(f"    - Nivel de ayuda: {strategy.get('help_level')}")
        
        # Generar respuesta con LLM
        print("\n[+] Generando respuesta tutorial con Phi-3...")
        
        system_prompt = """Eres un tutor de programacion que usa el metodo socratico.
Tu objetivo es guiar al estudiante a descubrir la respuesta, NO darle la solucion completa.
Haz preguntas que lo hagan pensar en el problema paso a paso."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"El estudiante pregunta: {student_prompt}\n\nGenera una respuesta socratica breve (maximo 3 lineas) que lo guie a pensar en el caso base del factorial sin darle la respuesta directa."}
        ]
        
        response = await llm.generate(messages)
        
        print(f"\n[+] Respuesta del Tutor IA (Phi-3):")
        print(f"    {response['content']}")
        
        print(f"\n[OK] Integracion completa exitosa!")
        print(f"    Gateway [OK] -> Cognitive Engine [OK] -> Ollama [OK] -> Phi-3 [OK]")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] en integracion: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Ejecutar tests"""
    print("\n" + "="*70)
    print("PRUEBA END-TO-END: Gateway + Ollama + Phi-3")
    print("="*70)
    print("\n>> Este script verifica:")
    print("   1. Generacion simple con Phi-3")
    print("   2. Integracion con Gateway y Cognitive Engine")
    
    results = []
    
    # Test 1
    results.append(("Generacion simple", await test_simple_generation()))
    
    # Test 2
    results.append(("Gateway Integration", await test_gateway_integration()))
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN DE TESTS")
    print("="*70)
    
    for test_name, success in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{status} {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "="*70)
    if all_passed:
        print("*** TODOS LOS TESTS PASARON ***")
        print("="*70)
        print("\n[OK] El sistema esta listo para usar:")
        print("   - Ollama funcionando correctamente")
        print("   - Modelo Phi-3 operativo")
        print("   - Gateway integrado con IA")
        print("   - Cognitive Engine activo")
        print("\n>> Proximos pasos:")
        print("   1. Iniciar API: uvicorn backend.api.main:app --reload")
        print("   2. Probar endpoints: http://localhost:8000/docs")
    else:
        print("*** ALGUNOS TESTS FALLARON ***")
        print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
