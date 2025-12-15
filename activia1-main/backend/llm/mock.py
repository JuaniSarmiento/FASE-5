"""
Mock LLM provider for development and testing

Provides predictable responses without calling real LLM APIs.
"""
from typing import Optional, Dict, Any, List, AsyncIterator
import asyncio

from .base import LLMProvider, LLMMessage, LLMResponse, LLMRole


class MockLLMProvider(LLMProvider):
    """
    Mock LLM provider for testing and development

    Returns predefined responses based on message content.
    Useful for:
    - Unit testing without API calls
    - Development without API keys
    - Predictable behavior for demos
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.model_name = config.get("model", "mock-gpt-4") if config else "mock-gpt-4"
        self.delay = config.get("delay", 0.1) if config else 0.1  # Simulate API latency

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate mock completion (async)"""
        # Simulate API latency without blocking
        await asyncio.sleep(self.delay)

        # Get last user message - handle both LLMMessage objects and dicts
        user_messages = []
        for m in messages:
            if isinstance(m, dict):
                if m.get("role") == "user" or m.get("role") == LLMRole.USER:
                    user_messages.append(m.get("content", ""))
            elif hasattr(m, 'role') and m.role == LLMRole.USER:
                user_messages.append(m.content)

        last_message = user_messages[-1] if user_messages else ""

        # Generate contextual response
        response_content = self._generate_contextual_response(last_message)

        # Calculate mock token usage - handle both types
        input_tokens = 0
        for m in messages:
            if isinstance(m, dict):
                input_tokens += self.count_tokens(m.get("content", ""))
            else:
                input_tokens += self.count_tokens(m.content)
        output_tokens = self.count_tokens(response_content)

        return LLMResponse(
            content=response_content,
            model=self.model_name,
            usage={
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens
            },
            metadata={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "mock": True
            }
        )

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Generate streaming mock completion (async)"""
        response = await self.generate(messages, temperature, max_tokens, **kwargs)

        # Simulate streaming by yielding words
        words = response.content.split()
        for word in words:
            await asyncio.sleep(self.delay / 10)  # Faster than full response
            yield word + " "

    def count_tokens(self, text: str) -> int:
        """
        Mock token counting (approximation)

        Real implementation would use tiktoken or similar.
        This uses simple heuristic: ~4 chars per token
        """
        return len(text) // 4

    def _generate_contextual_response(self, user_input: str) -> str:
        """Generate response based on input content"""
        user_lower = user_input.lower()

        # Tutoring responses
        if any(kw in user_lower for kw in ["ayuda", "help", "cómo", "como", "explicar"]):
            return """Te puedo ayudar con eso. Para resolver este problema, te sugiero:

1. Primero, descompone el problema en partes más pequeñas
2. ¿Qué información tienes? ¿Qué necesitás encontrar?
3. ¿Hay algún patrón o concepto similar que conozcas?

¿Qué parte te gustaría explorar primero?"""

        # Code review responses
        elif any(kw in user_lower for kw in ["código", "codigo", "implementación", "implementacion"]):
            return """Revisando tu código, observo algunos puntos:

**Fortalezas:**
- Buena estructura general
- Nombres de variables descriptivos

**Áreas de mejora:**
- Considerar casos extremos (edge cases)
- Agregar validación de entrada
- Documentar el propósito de las funciones complejas

¿Te gustaría que profundice en alguno de estos puntos?"""

        # Debugging responses
        elif any(kw in user_lower for kw in ["error", "bug", "falla", "no funciona"]):
            return """Entiendo que tenés un error. Sigamos un enfoque sistemático:

1. ¿Qué esperabas que suceda?
2. ¿Qué está sucediendo en cambio?
3. ¿Tenés el mensaje de error completo?

Con esta información podemos identificar la causa raíz del problema."""

        # Conceptual explanation responses
        elif "?" in user_input or any(kw in user_lower for kw in ["qué es", "que es", "explica"]):
            return """Buena pregunta. Ese concepto se refiere a un principio fundamental en programación.

Para entenderlo mejor, pensá en un ejemplo concreto: [ejemplo específico].

¿Te ayuda esta explicación? ¿Querés que profundice en algún aspecto particular?"""

        # Design/architecture responses
        elif any(kw in user_lower for kw in ["diseño", "arquitectura", "estructura", "pattern"]):
            return """En cuanto al diseño, hay varias aproximaciones que podrías considerar:

1. **Opción A**: Más simple, rápido de implementar, pero menos extensible
2. **Opción B**: Más flexible, mejor para proyectos grandes, requiere más tiempo inicial

¿Cuáles son las prioridades para tu proyecto: velocidad de desarrollo, mantenibilidad, o escalabilidad?"""

        # Testing responses
        elif any(kw in user_lower for kw in ["test", "prueba", "testing"]):
            return """Para testear esta funcionalidad, te recomiendo:

1. **Tests unitarios**: Verificar cada componente aislado
2. **Tests de integración**: Verificar que funcionen juntos
3. **Casos extremos**: Probar con valores límite

¿Empezamos por escribir algunos casos de prueba?"""

        # Default response
        else:
            return """Entiendo. Para ayudarte mejor, ¿podrías darme más detalles sobre:

- ¿Qué estás tratando de lograr?
- ¿Qué intentaste hasta ahora?
- ¿Hay algún requisito o restricción específica?

Así puedo darte una respuesta más precisa."""

    def validate_config(self) -> bool:
        """Mock provider is always valid"""
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information"""
        return {
            "provider": "MockLLMProvider",
            "model": self.model_name,
            "config": self.config,
            "is_mock": True,
            "capabilities": [
                "text_generation",
                "streaming",
                "contextual_responses"
            ]
        }