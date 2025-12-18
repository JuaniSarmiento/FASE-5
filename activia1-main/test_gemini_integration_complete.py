"""
Prueba de integración completa del sistema con Gemini 2.5
"""
import os
import asyncio
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from llm.factory import LLMProviderFactory
from llm.base import LLMMessage, LLMRole

async def test_factory_creation():
    """Prueba creación de provider desde factory"""
    print("\n1️⃣ Prueba de Factory")
    print("-"*60)
    
    try:
        provider = LLMProviderFactory.create_from_env()
        print(f"✅ Provider creado: {type(provider).__name__}")
        print(f"   Modelo: {provider.model}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def test_simple_conversation():
    """Prueba conversación simple"""
    print("\n2️⃣ Prueba de Conversación Simple")
    print("-"*60)
    
    try:
        provider = LLMProviderFactory.create_from_env()
        
        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content="Eres un asistente útil."),
            LLMMessage(role=LLMRole.USER, content="Di 'Hola' si me recibes")
        ]
        
        print("🔄 Generando respuesta...")
        response = await provider.generate(messages, temperature=0.7)
        
        print(f"✅ Respuesta recibida:")
        print(f"   {response.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def test_tutor_scenario():
    """Prueba escenario de tutor socrático"""
    print("\n3️⃣ Prueba de Escenario de Tutor")
    print("-"*60)
    
    try:
        provider = LLMProviderFactory.create_from_env()
        
        messages = [
            LLMMessage(
                role=LLMRole.SYSTEM, 
                content="Eres un tutor de programación que usa el método socrático. Haces preguntas para guiar al estudiante."
            ),
            LLMMessage(
                role=LLMRole.USER, 
                content="No entiendo qué es una variable en Python"
            )
        ]
        
        print("🔄 Generando respuesta de tutor...")
        response = await provider.generate(messages, temperature=0.8)
        
        print(f"✅ Respuesta del tutor:")
        print(f"   {response.content[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def test_code_analysis():
    """Prueba análisis de código"""
    print("\n4️⃣ Prueba de Análisis de Código")
    print("-"*60)
    
    try:
        provider = LLMProviderFactory.create_from_env()
        
        code = """
def calcular_promedio(numeros):
    suma = 0
    for n in numeros:
        suma = suma + n
    return suma / len(numeros)
"""
        
        messages = [
            LLMMessage(
                role=LLMRole.SYSTEM,
                content="Eres un experto en Python. Analiza el código y da feedback conciso."
            ),
            LLMMessage(
                role=LLMRole.USER,
                content=f"Analiza este código:\n{code}\n\n¿Está bien? ¿Qué mejorarías?"
            )
        ]
        
        print("🔄 Analizando código...")
        response = await provider.generate(messages, temperature=0.5)
        
        print(f"✅ Análisis recibido:")
        print(f"   {response.content[:200]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def test_streaming():
    """Prueba generación streaming"""
    print("\n5️⃣ Prueba de Streaming")
    print("-"*60)
    
    try:
        provider = LLMProviderFactory.create_from_env()
        
        messages = [
            LLMMessage(
                role=LLMRole.USER,
                content="Cuenta del 1 al 5"
            )
        ]
        
        print("🔄 Generando con streaming...")
        chunks = []
        
        async for chunk in provider.generate_stream(messages):
            chunks.append(chunk.content)
            print(".", end="", flush=True)
        
        full_response = "".join(chunks)
        print(f"\n✅ Streaming completado:")
        print(f"   Recibido: {len(chunks)} chunks")
        print(f"   Respuesta: {full_response[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Ejecuta todas las pruebas"""
    print("="*60)
    print("PRUEBA DE INTEGRACIÓN COMPLETA - GEMINI 2.5")
    print("="*60)
    
    # Verificar configuración
    print("\n📋 Configuración:")
    print(f"   LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
    print(f"   GEMINI_MODEL: {os.getenv('GEMINI_MODEL')}")
    print(f"   GEMINI_API_KEY: {'Configurada ✓' if os.getenv('GEMINI_API_KEY') else 'NO CONFIGURADA ✗'}")
    
    # Ejecutar pruebas
    results = []
    
    results.append(("Factory", await test_factory_creation()))
    results.append(("Conversación", await test_simple_conversation()))
    results.append(("Tutor", await test_tutor_scenario()))
    results.append(("Análisis", await test_code_analysis()))
    results.append(("Streaming", await test_streaming()))
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN DE PRUEBAS")
    print("="*60)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("   Sistema Gemini 2.5 funcionando correctamente")
    else:
        failed = [name for name, success in results if not success]
        print(f"\n⚠️ Pruebas fallidas: {', '.join(failed)}")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
