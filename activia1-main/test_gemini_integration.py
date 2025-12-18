"""
Test de Gemini Provider - Verificación de Funcionalidad

Este script prueba la integración con Gemini API para verificar:
1. Conexión básica con Gemini
2. Selección automática de modelos (Flash vs Pro)
3. Prompts del tutor que evitan dar código
4. Streaming de respuestas

Uso:
    python test_gemini_integration.py
    
Requisitos:
    - Configurar GEMINI_API_KEY en .env
    - LLM_PROVIDER=gemini en .env
"""
import asyncio
import os
from dotenv import load_dotenv
from backend.llm import LLMProviderFactory, LLMMessage, LLMRole

# Cargar variables de entorno
load_dotenv()


async def test_basic_connection():
    """Test 1: Verificar conexión básica con Gemini"""
    print("\n" + "="*60)
    print("TEST 1: Conexión Básica con Gemini")
    print("="*60)
    
    try:
        provider = LLMProviderFactory.create_from_env("gemini")
        print("✅ Provider creado exitosamente")
        
        model_info = provider.get_model_info()
        print(f"📊 Información del modelo:")
        print(f"   - Provider: {model_info['provider']}")
        print(f"   - Modelo por defecto: {model_info['model']}")
        print(f"   - Flash: {model_info['flash_model']}")
        print(f"   - Pro: {model_info['pro_model']}")
        print(f"   - Soporta streaming: {model_info['supports_streaming']}")
        
        return provider
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


async def test_flash_model(provider):
    """Test 2: Verificar uso de modelo Flash para conversaciones"""
    print("\n" + "="*60)
    print("TEST 2: Modelo Flash (Conversación Normal)")
    print("="*60)
    
    try:
        messages = [
            LLMMessage(
                role=LLMRole.USER,
                content="¿Qué es un algoritmo? Responde brevemente."
            )
        ]
        
        print("📤 Enviando pregunta conceptual...")
        response = await provider.generate(
            messages,
            is_code_analysis=False,
            max_tokens=150
        )
        
        print(f"✅ Respuesta recibida")
        print(f"📊 Modelo usado: {response.model}")
        print(f"🔢 Tokens: {response.usage['total_tokens']}")
        print(f"\n💬 Respuesta:\n{response.content[:300]}...")
        
        if "flash" in response.model.lower():
            print("✅ Modelo Flash usado correctamente")
        else:
            print(f"⚠️  Se esperaba Flash pero se usó: {response.model}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_pro_model(provider):
    """Test 3: Verificar uso de modelo Pro para análisis de código"""
    print("\n" + "="*60)
    print("TEST 3: Modelo Pro (Análisis de Código)")
    print("="*60)
    
    try:
        messages = [
            LLMMessage(
                role=LLMRole.USER,
                content="Analiza la complejidad algorítmica de un algoritmo de búsqueda binaria. Sé breve."
            )
        ]
        
        print("📤 Enviando pregunta de análisis de código...")
        response = await provider.generate(
            messages,
            is_code_analysis=True,
            max_tokens=200
        )
        
        print(f"✅ Respuesta recibida")
        print(f"📊 Modelo usado: {response.model}")
        print(f"🔢 Tokens: {response.usage['total_tokens']}")
        print(f"\n💬 Respuesta:\n{response.content[:300]}...")
        
        if "pro" in response.model.lower():
            print("✅ Modelo Pro usado correctamente")
        else:
            print(f"⚠️  Se esperaba Pro pero se usó: {response.model}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_tutor_no_code():
    """Test 4: Verificar que el tutor NO da código"""
    print("\n" + "="*60)
    print("TEST 4: Tutor Socrático - NO Debe Dar Código")
    print("="*60)
    
    try:
        provider = LLMProviderFactory.create_from_env("gemini")
        
        # Simular prompt del tutor socrático
        messages = [
            LLMMessage(
                role=LLMRole.SYSTEM,
                content="""Eres un tutor socrático. Tu objetivo es guiar al estudiante mediante preguntas.

⚠️ REGLAS ESTRICTAS - NUNCA VIOLAR:
1. PROHIBIDO ABSOLUTAMENTE dar código de programación
2. NO des soluciones directas
3. NO escribas sintaxis de ningún lenguaje

Solo haz preguntas que guíen el razonamiento."""
            ),
            LLMMessage(
                role=LLMRole.USER,
                content="Dame el código para sumar dos números en Python"
            )
        ]
        
        print("📤 Pidiendo código al tutor (debería rechazar)...")
        response = await provider.generate(messages, max_tokens=200)
        
        print(f"✅ Respuesta recibida")
        print(f"\n💬 Respuesta del tutor:\n{response.content}")
        
        # Verificar que NO contiene código Python
        code_indicators = ["def ", "return ", "print(", "import ", "class ", "if __name__"]
        has_code = any(indicator in response.content for indicator in code_indicators)
        
        if has_code:
            print("❌ FALLO: El tutor dio código de programación")
        else:
            print("✅ ÉXITO: El tutor redirigió con preguntas (no dio código)")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_streaming():
    """Test 5: Verificar streaming de respuestas"""
    print("\n" + "="*60)
    print("TEST 5: Streaming de Respuestas")
    print("="*60)
    
    try:
        provider = LLMProviderFactory.create_from_env("gemini")
        
        messages = [
            LLMMessage(
                role=LLMRole.USER,
                content="Explica qué es una función en programación en 2 oraciones."
            )
        ]
        
        print("📤 Iniciando streaming...")
        print("💬 Respuesta (en tiempo real):\n")
        
        full_response = ""
        async for chunk in provider.generate_stream(messages, max_tokens=100):
            print(chunk, end="", flush=True)
            full_response += chunk
        
        print("\n\n✅ Streaming completado")
        print(f"📊 Caracteres recibidos: {len(full_response)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Ejecutar todos los tests"""
    print("\n" + "🚀"*30)
    print("TEST DE INTEGRACIÓN CON GEMINI API")
    print("🚀"*30)
    
    # Verificar que la API key está configurada
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\n❌ ERROR: GEMINI_API_KEY no está configurado en .env")
        print("\n📝 Pasos para configurar:")
        print("1. Obtén tu API key en: https://makersuite.google.com/app/apikey")
        print("2. Agrega a tu .env: GEMINI_API_KEY=tu_api_key_aqui")
        print("3. Agrega a tu .env: LLM_PROVIDER=gemini")
        return
    
    print(f"✅ API Key configurada: {api_key[:10]}...{api_key[-5:]}")
    
    # Test 1: Conexión básica
    provider = await test_basic_connection()
    if not provider:
        print("\n❌ No se pudo crear el provider. Verifica tu configuración.")
        return
    
    # Test 2: Modelo Flash
    await test_flash_model(provider)
    
    # Test 3: Modelo Pro
    await test_pro_model(provider)
    
    # Test 4: Tutor no da código
    await test_tutor_no_code()
    
    # Test 5: Streaming
    await test_streaming()
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE TESTS")
    print("="*60)
    print("✅ Si todos los tests pasaron, Gemini está funcionando correctamente")
    print("✅ El sistema está usando Flash para conversaciones y Pro para código")
    print("✅ El tutor socrático evita dar código directamente")
    print("\n💡 Próximos pasos:")
    print("   1. Reinicia el backend: python -m backend")
    print("   2. Prueba el tutor desde el frontend")
    print("   3. Verifica que las respuestas son rápidas y precisas")
    print("\n🎉 ¡Migración a Gemini completada!")


if __name__ == "__main__":
    asyncio.run(main())
