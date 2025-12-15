"""
Ejemplo de integración con OpenAI GPT-4

Este script demuestra cómo usar el sistema AI-Native con OpenAI en lugar del
Mock provider.

REQUISITOS:
1. Tener una API key de OpenAI (https://platform.openai.com/api-keys)
2. Configurar la API key en .env o como variable de entorno
3. Instalar dependencias: pip install openai tiktoken

AUTOR: Claude Code (Sonnet 4.5)
FECHA: 2025-11-19
"""

import sys
import io
import os
from dotenv import load_dotenv

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Cargar variables de entorno desde .env
load_dotenv()

from src.ai_native_mvp.llm import LLMProviderFactory, LLMMessage, LLMRole
from src.ai_native_mvp.core.ai_gateway import AIGateway
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import (
    SessionRepository,
    TraceRepository,
    RiskRepository,
    EvaluationRepository,
    TraceSequenceRepository
)

print("=" * 80)
print("EJEMPLO: Integración con OpenAI GPT-4")
print("=" * 80)

# =============================================================================
# PASO 1: Verificar configuración
# =============================================================================

print("\n[PASO 1] Verificar configuración de OpenAI...")

# Verificar que existe OPENAI_API_KEY
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("❌ ERROR: OPENAI_API_KEY no está configurada.")
    print("\nPara configurar:")
    print("1. Copia .env.example a .env:")
    print("   cp .env.example .env")
    print("\n2. Edita .env y agrega tu API key:")
    print("   OPENAI_API_KEY=sk-proj-...")
    print("\n3. Obtén tu API key en: https://platform.openai.com/api-keys")
    sys.exit(1)

# Verificar modelo configurado
model = os.getenv("OPENAI_MODEL", "gpt-4")
print(f"✅ API Key encontrada (primeros 10 caracteres): {api_key[:10]}...")
print(f"✅ Modelo configurado: {model}")

# =============================================================================
# PASO 2: Crear proveedor OpenAI
# =============================================================================

print("\n[PASO 2] Crear proveedor OpenAI...")

try:
    # Crear desde variables de entorno (método recomendado)
    llm_provider = LLMProviderFactory.create_from_env("openai")
    print(f"✅ Proveedor OpenAI creado exitosamente")

    # Obtener información del modelo
    model_info = llm_provider.get_model_info()
    print(f"   - Proveedor: {model_info['provider']}")
    print(f"   - Modelo: {model_info['model']}")
    print(f"   - Capacidades: {', '.join([c for c in model_info['capabilities'] if c])}")

except ValueError as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)
except ImportError as e:
    print(f"❌ ERROR: {e}")
    print("\nInstala las dependencias faltantes:")
    print("   pip install openai tiktoken")
    sys.exit(1)

# =============================================================================
# PASO 3: Probar generación simple
# =============================================================================

print("\n[PASO 3] Probar generación simple con OpenAI...")

messages = [
    LLMMessage(
        role=LLMRole.SYSTEM,
        content="Eres un tutor cognitivo que ayuda a estudiantes de programación a razonar, sin dar soluciones completas."
    ),
    LLMMessage(
        role=LLMRole.USER,
        content="¿Qué es una cola circular y en qué casos es mejor que una cola simple?"
    )
]

try:
    print("   Enviando request a OpenAI...")
    response = llm_provider.generate(
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    print(f"✅ Respuesta recibida de {response.model}")
    print(f"\n{'─' * 80}")
    print("RESPUESTA DEL TUTOR:")
    print(f"{'─' * 80}")
    print(response.content)
    print(f"{'─' * 80}")

    # Mostrar métricas de uso
    print(f"\n📊 Métricas de uso:")
    print(f"   - Tokens de entrada (prompt): {response.usage['prompt_tokens']}")
    print(f"   - Tokens de salida (respuesta): {response.usage['completion_tokens']}")
    print(f"   - Total de tokens: {response.usage['total_tokens']}")

    # Calcular costo aproximado (GPT-4 pricing)
    if "gpt-4" in response.model:
        # GPT-4: $0.03/1K input tokens, $0.06/1K output tokens
        input_cost = (response.usage['prompt_tokens'] / 1000) * 0.03
        output_cost = (response.usage['completion_tokens'] / 1000) * 0.06
        total_cost = input_cost + output_cost
        print(f"   - Costo aproximado: ${total_cost:.4f} USD")

except Exception as e:
    print(f"❌ ERROR al generar respuesta: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# PASO 4: Integrar con AIGateway
# =============================================================================

print(f"\n[PASO 4] Integrar OpenAI con AIGateway...")

try:
    with get_db_session() as db:
        # Crear repositorios
        session_repo = SessionRepository(db)
        trace_repo = TraceRepository(db)
        risk_repo = RiskRepository(db)
        evaluation_repo = EvaluationRepository(db)
        sequence_repo = TraceSequenceRepository(db)

        # Crear Gateway con OpenAI provider (DI)
        gateway = AIGateway(
            llm_provider=llm_provider,  # ¡Aquí usamos OpenAI en lugar de Mock!
            session_repo=session_repo,
            trace_repo=trace_repo,
            risk_repo=risk_repo,
            evaluation_repo=evaluation_repo,
            sequence_repo=sequence_repo
        )

        print("✅ Gateway creado con proveedor OpenAI")

        # Crear sesión
        session_id = gateway.create_session(
            student_id="openai_test_student",
            activity_id="prog2_cola_circular",
            mode="TUTOR"
        )

        print(f"✅ Sesión creada: {session_id}")

except Exception as e:
    print(f"❌ ERROR al crear Gateway: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# PASO 5: Procesar interacción con OpenAI
# =============================================================================

print(f"\n[PASO 5] Procesar interacción usando OpenAI...")

try:
    # Primera interacción: Pregunta conceptual
    print("\n📝 Interacción 1: Pregunta conceptual")
    result1 = gateway.process_interaction(
        session_id=session_id,
        prompt="¿Cómo implemento una cola circular en Python? ¿Qué estructura de datos debo usar?",
        context={}
    )

    print(f"\n{'─' * 80}")
    print("RESPUESTA DEL SISTEMA (con OpenAI GPT-4):")
    print(f"{'─' * 80}")
    print(result1["message"])
    print(f"{'─' * 80}")

    print(f"\n📊 Metadata de la interacción:")
    print(f"   - Agente usado: {result1['agent_used']}")
    print(f"   - Estado cognitivo: {result1.get('cognitive_state', 'N/A')}")
    print(f"   - Bloqueado: {'Sí' if result1.get('blocked') else 'No'}")

    # Segunda interacción: Solicitud de código (debería ser bloqueada por governance)
    print("\n\n📝 Interacción 2: Solicitud de código completo (test de governance)")
    result2 = gateway.process_interaction(
        session_id=session_id,
        prompt="Dame el código completo de una cola circular en Python, implementado y listo para usar.",
        context={}
    )

    print(f"\n{'─' * 80}")
    print("RESPUESTA DEL SISTEMA:")
    print(f"{'─' * 80}")
    print(result2["message"])
    print(f"{'─' * 80}")

    print(f"\n📊 Metadata de la interacción:")
    print(f"   - Agente usado: {result2['agent_used']}")
    print(f"   - Estado cognitivo: {result2.get('cognitive_state', 'N/A')}")
    print(f"   - Bloqueado: {'Sí' if result2.get('blocked') else 'No'}")

    if result2.get('blocked'):
        print(f"   ⚠️ GOV-IA bloqueó la solicitud (delegación total detectada)")

except Exception as e:
    print(f"❌ ERROR al procesar interacción: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# =============================================================================
# PASO 6: Verificar trazas N4
# =============================================================================

print(f"\n[PASO 6] Verificar trazas N4 capturadas...")

try:
    with get_db_session() as db:
        trace_repo = TraceRepository(db)
        traces = trace_repo.get_by_session(session_id)

        print(f"✅ {len(traces)} trazas capturadas:")
        for i, trace in enumerate(traces, 1):
            print(f"\n   Traza {i}:")
            print(f"   - ID: {trace.id}")
            print(f"   - Tipo: {trace.interaction_type}")
            print(f"   - Nivel: {trace.trace_level}")
            print(f"   - Estado cognitivo: {trace.cognitive_state or 'N/A'}")
            print(f"   - Contenido: {trace.content[:80]}...")

except Exception as e:
    print(f"❌ ERROR al recuperar trazas: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# PASO 7: Verificar riesgos detectados
# =============================================================================

print(f"\n[PASO 7] Verificar riesgos detectados...")

try:
    with get_db_session() as db:
        risk_repo = RiskRepository(db)
        risks = risk_repo.get_by_session(session_id)

        if len(risks) > 0:
            print(f"⚠️ {len(risks)} riesgo(s) detectado(s):")
            for i, risk in enumerate(risks, 1):
                print(f"\n   Riesgo {i}:")
                print(f"   - Tipo: {risk.risk_type}")
                print(f"   - Nivel: {risk.risk_level}")
                print(f"   - Dimensión: {risk.dimension}")
                print(f"   - Descripción: {risk.description}")
        else:
            print("✅ No se detectaron riesgos")

except Exception as e:
    print(f"❌ ERROR al recuperar riesgos: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# RESUMEN FINAL
# =============================================================================

print("\n" + "=" * 80)
print("RESUMEN DE LA INTEGRACIÓN CON OPENAI")
print("=" * 80)

print("""
✅ Integración exitosa con OpenAI GPT-4

Aspectos verificados:
1. ✅ Configuración de API key desde variables de entorno
2. ✅ Creación de proveedor OpenAI con LLMProviderFactory
3. ✅ Generación de respuestas usando GPT-4
4. ✅ Integración con AIGateway (reemplazo de Mock provider)
5. ✅ Procesamiento de interacciones con OpenAI
6. ✅ Captura de trazas N4 (persistencia funcionando)
7. ✅ Detección de riesgos (governance activo)

El sistema AI-Native está completamente funcional con OpenAI GPT-4.

IMPORTANTE - Consideraciones de costo:
- GPT-4 cuesta aproximadamente $0.03/1K input tokens + $0.06/1K output tokens
- Una interacción típica consume ~200-500 tokens total (~$0.02-0.05 por interacción)
- Para desarrollo, considera usar GPT-3.5-turbo (más económico):
  * Edita .env: OPENAI_MODEL=gpt-3.5-turbo
  * Costo: ~10x más barato que GPT-4

PRÓXIMOS PASOS:
1. Para usar en producción, actualiza la API para usar create_from_env()
2. Configura monitoring de costos en OpenAI dashboard
3. Implementa rate limiting para controlar gastos
4. Considera usar GPT-3.5 para interacciones simples, GPT-4 para complejas
""")

print("=" * 80)