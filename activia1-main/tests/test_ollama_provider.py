"""
Tests for Ollama LLM Provider

Tests para src/ai_native_mvp/llm/ollama_provider.py

Verifica:
1. Inicialización del provider (config, defaults)
2. Generación de respuestas (generate)
3. Streaming de respuestas (generate_stream)
4. Manejo de errores (conexión, timeout, respuestas inválidas)
5. Conversión de mensajes a formato Ollama
6. Integración con metrics (HIGH-01)
"""

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List

from backend.llm.ollama_provider import OllamaProvider
from backend.llm.base import LLMMessage, LLMResponse, LLMRole


class TestOllamaProviderInitialization:
    """Tests de inicialización de OllamaProvider"""

    def test_init_with_defaults(self):
        """__init__() sin config usa valores por defecto"""
        provider = OllamaProvider()

        assert provider.base_url == "http://localhost:11434"
        assert provider.model == "llama2"
        assert provider.temperature == 0.7
        assert provider.timeout == 60.0
        assert provider.chat_endpoint == "http://localhost:11434/api/chat"

    def test_init_with_custom_config(self):
        """__init__() con config personalizada usa esos valores"""
        config = {
            "base_url": "http://192.168.1.100:11434",
            "model": "mistral",
            "temperature": 0.5,
            "timeout": 120.0
        }
        provider = OllamaProvider(config)

        assert provider.base_url == "http://192.168.1.100:11434"
        assert provider.model == "mistral"
        assert provider.temperature == 0.5
        assert provider.timeout == 120.0

    def test_init_removes_trailing_slash_from_base_url(self):
        """__init__() elimina trailing slash de base_url"""
        config = {"base_url": "http://ollama:11434/"}
        provider = OllamaProvider(config)

        assert provider.base_url == "http://ollama:11434"
        assert not provider.base_url.endswith("/")

    def test_init_lazy_client_initialization(self):
        """__init__() no crea cliente HTTP inmediatamente (lazy)"""
        provider = OllamaProvider()

        assert provider._client is None

    def test_get_client_creates_httpx_client(self):
        """_get_client() crea cliente httpx.AsyncClient con timeout configurado"""
        provider = OllamaProvider({"timeout": 90.0})

        client = provider._get_client()

        assert isinstance(client, httpx.AsyncClient)
        assert client.timeout.read == 90.0

    def test_get_client_returns_same_instance(self):
        """_get_client() retorna la misma instancia en llamadas subsecuentes"""
        provider = OllamaProvider()

        client1 = provider._get_client()
        client2 = provider._get_client()

        assert client1 is client2


class TestOllamaProviderMessageConversion:
    """Tests de conversión de mensajes a formato Ollama"""

    def test_convert_messages_single_user_message(self):
        """_convert_messages_to_ollama_format() convierte mensaje de usuario"""
        provider = OllamaProvider()
        messages = [
            LLMMessage(role=LLMRole.USER, content="Hello, Ollama!")
        ]

        ollama_messages = provider._convert_messages_to_ollama_format(messages)

        assert len(ollama_messages) == 1
        assert ollama_messages[0]["role"] == "user"
        assert ollama_messages[0]["content"] == "Hello, Ollama!"

    def test_convert_messages_with_system_message(self):
        """_convert_messages_to_ollama_format() incluye mensajes del sistema"""
        provider = OllamaProvider()
        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content="You are a helpful assistant"),
            LLMMessage(role=LLMRole.USER, content="What's 2+2?")
        ]

        ollama_messages = provider._convert_messages_to_ollama_format(messages)

        assert len(ollama_messages) == 2
        assert ollama_messages[0]["role"] == "system"
        assert ollama_messages[1]["role"] == "user"

    def test_convert_messages_full_conversation(self):
        """_convert_messages_to_ollama_format() convierte conversación completa"""
        provider = OllamaProvider()
        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content="You are a math tutor"),
            LLMMessage(role=LLMRole.USER, content="What's 5+3?"),
            LLMMessage(role=LLMRole.ASSISTANT, content="5+3 equals 8"),
            LLMMessage(role=LLMRole.USER, content="What about 10-2?")
        ]

        ollama_messages = provider._convert_messages_to_ollama_format(messages)

        assert len(ollama_messages) == 4
        assert ollama_messages[0]["role"] == "system"
        assert ollama_messages[1]["role"] == "user"
        assert ollama_messages[2]["role"] == "assistant"
        assert ollama_messages[3]["role"] == "user"


class TestOllamaProviderGenerate:
    """Tests de generación de respuestas (método generate)"""

    @pytest.mark.asyncio
    async def test_generate_successful_response(self):
        """generate() retorna LLMResponse con respuesta exitosa de Ollama"""
        provider = OllamaProvider()

        # Mock response de Ollama
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "This is a test response from Ollama"},
            "prompt_eval_count": 10,
            "eval_count": 20,
            "total_duration": 1500000000,
            "load_duration": 500000000,
            "prompt_eval_duration": 300000000,
            "eval_duration": 700000000,
        }

        # Mock httpx.AsyncClient.post y _get_metrics para evitar importar API config
        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post, \
             patch('backend.llm.ollama_provider._get_metrics', return_value=None):
            mock_post.return_value = mock_response

            messages = [LLMMessage(role=LLMRole.USER, content="Test")]
            response = await provider.generate(messages)

            assert isinstance(response, LLMResponse)
            assert response.content == "This is a test response from Ollama"
            assert response.model == "llama2"
            assert response.usage["prompt_tokens"] == 10
            assert response.usage["completion_tokens"] == 20
            assert response.usage["total_tokens"] == 30

    @pytest.mark.asyncio
    async def test_generate_with_custom_temperature(self):
        """generate() respeta parámetro temperature personalizado"""
        provider = OllamaProvider()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Response"},
            "prompt_eval_count": 5,
            "eval_count": 10,
        }

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            messages = [LLMMessage(role=LLMRole.USER, content="Test")]
            await provider.generate(messages, temperature=0.9)

            # Verificar que se envió temperature=0.9 en payload
            call_args = mock_post.call_args
            payload = call_args.kwargs["json"]
            assert payload["options"]["temperature"] == 0.9

    @pytest.mark.asyncio
    async def test_generate_with_max_tokens(self):
        """generate() incluye num_predict cuando se especifica max_tokens"""
        provider = OllamaProvider()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": "Response"},
            "prompt_eval_count": 5,
            "eval_count": 10,
        }

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            messages = [LLMMessage(role=LLMRole.USER, content="Test")]
            await provider.generate(messages, max_tokens=500)

            # Verificar que se envió num_predict en payload
            call_args = mock_post.call_args
            payload = call_args.kwargs["json"]
            assert payload["options"]["num_predict"] == 500

    @pytest.mark.asyncio
    async def test_generate_connect_error_raises_helpful_message(self):
        """generate() lanza ValueError con mensaje útil si Ollama no está disponible"""
        provider = OllamaProvider()

        # Simular error de conexión
        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.ConnectError("Connection refused")

            messages = [LLMMessage(role=LLMRole.USER, content="Test")]

            with pytest.raises(ValueError) as exc_info:
                await provider.generate(messages)

            error_msg = str(exc_info.value)
            assert "Cannot connect to Ollama server" in error_msg
            assert "http://localhost:11434" in error_msg
            assert "ollama serve" in error_msg
            assert "ollama pull" in error_msg

    @pytest.mark.asyncio
    async def test_generate_timeout_error_raises_helpful_message(self):
        """generate() lanza ValueError con mensaje útil si request timeout"""
        provider = OllamaProvider({"timeout": 5.0})

        # Simular timeout
        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = httpx.TimeoutException("Request timed out")

            messages = [LLMMessage(role=LLMRole.USER, content="Test")]

            with pytest.raises(ValueError) as exc_info:
                await provider.generate(messages)

            error_msg = str(exc_info.value)
            assert "timed out after 5.0s" in error_msg
            assert "increasing timeout" in error_msg.lower()

    @pytest.mark.asyncio
    async def test_generate_http_error_raises_helpful_message(self):
        """generate() lanza ValueError con detalles de HTTP error"""
        provider = OllamaProvider()

        # Simular HTTP 404
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Model not found"

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=mock_response
            )

            messages = [LLMMessage(role=LLMRole.USER, content="Test")]

            with pytest.raises(ValueError) as exc_info:
                await provider.generate(messages)

            error_msg = str(exc_info.value)
            assert "Ollama API error (404)" in error_msg
            assert "Model not found" in error_msg

    @pytest.mark.asyncio
    async def test_generate_empty_response_raises_error(self):
        """generate() lanza ValueError si Ollama retorna respuesta vacía"""
        provider = OllamaProvider()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": {"content": ""},  # Contenido vacío
        }

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            messages = [LLMMessage(role=LLMRole.USER, content="Test")]

            with pytest.raises(ValueError) as exc_info:
                await provider.generate(messages)

            assert "empty response" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_invalid_json_raises_error(self):
        """generate() lanza ValueError si respuesta de Ollama no es JSON válido"""
        provider = OllamaProvider()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_response.text = "Not a valid JSON response"

        with patch.object(httpx.AsyncClient, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            messages = [LLMMessage(role=LLMRole.USER, content="Test")]

            with pytest.raises(ValueError) as exc_info:
                await provider.generate(messages)

            assert "Invalid response format" in str(exc_info.value)


class TestOllamaProviderStreaming:
    """Tests de generación streaming (método generate_stream)"""

    @pytest.mark.asyncio
    async def test_generate_stream_yields_chunks(self):
        """generate_stream() genera chunks de contenido correctamente"""
        provider = OllamaProvider()

        # Simular respuesta streaming
        mock_stream_context = AsyncMock()
        mock_stream_context.__aenter__.return_value = mock_stream_context
        mock_stream_context.__aexit__.return_value = None

        # Simular líneas de respuesta
        async def mock_aiter_lines():
            yield '{"message": {"content": "Hello"}, "done": false}'
            yield '{"message": {"content": " world"}, "done": false}'
            yield '{"message": {"content": "!"}, "done": true}'

        mock_stream_context.aiter_lines = mock_aiter_lines
        mock_stream_context.raise_for_status = MagicMock()

        with patch.object(httpx.AsyncClient, 'stream', return_value=mock_stream_context):
            messages = [LLMMessage(role=LLMRole.USER, content="Test")]

            chunks = []
            async for chunk in provider.generate_stream(messages):
                chunks.append(chunk)

            assert chunks == ["Hello", " world", "!"]

    @pytest.mark.asyncio
    async def test_generate_stream_connect_error(self):
        """generate_stream() lanza ValueError si no puede conectar"""
        provider = OllamaProvider()

        with patch.object(httpx.AsyncClient, 'stream', side_effect=httpx.ConnectError("Connection refused")):
            messages = [LLMMessage(role=LLMRole.USER, content="Test")]

            with pytest.raises(ValueError) as exc_info:
                async for _ in provider.generate_stream(messages):
                    pass

            assert "Cannot connect to Ollama server" in str(exc_info.value)


class TestOllamaProviderUtilities:
    """Tests de métodos utilitarios"""

    def test_count_tokens_estimates_correctly(self):
        """count_tokens() estima tokens basado en longitud de caracteres"""
        provider = OllamaProvider()

        # Aproximadamente 1 token por 4 caracteres
        text = "This is a test message with some content"  # 41 caracteres
        tokens = provider.count_tokens(text)

        assert tokens == 10  # 41 // 4 = 10

    def test_count_tokens_empty_string(self):
        """count_tokens() retorna 0 para string vacío"""
        provider = OllamaProvider()

        assert provider.count_tokens("") == 0

    @pytest.mark.asyncio
    async def test_is_model_available_returns_true_when_found(self):
        """is_model_available() retorna True si modelo está disponible"""
        provider = OllamaProvider({"model": "llama2"})

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:latest"},
                {"name": "mistral:7b"}
            ]
        }

        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            available = await provider.is_model_available()

            assert available is True

    @pytest.mark.asyncio
    async def test_is_model_available_returns_false_when_not_found(self):
        """is_model_available() retorna False si modelo no está disponible"""
        provider = OllamaProvider({"model": "nonexistent-model"})

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:latest"},
                {"name": "mistral:7b"}
            ]
        }

        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            available = await provider.is_model_available()

            assert available is False

    @pytest.mark.asyncio
    async def test_list_available_models_returns_model_names(self):
        """list_available_models() retorna lista de nombres de modelos"""
        provider = OllamaProvider()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama2:latest"},
                {"name": "mistral:7b"},
                {"name": "codellama:13b"}
            ]
        }

        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            models = await provider.list_available_models()

            assert len(models) == 3
            assert "llama2:latest" in models
            assert "mistral:7b" in models
            assert "codellama:13b" in models

    @pytest.mark.asyncio
    async def test_list_available_models_error_returns_empty_list(self):
        """list_available_models() retorna lista vacía si hay error"""
        provider = OllamaProvider()

        with patch.object(httpx.AsyncClient, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection error")

            models = await provider.list_available_models()

            assert models == []


@pytest.mark.integration
class TestOllamaProviderIntegration:
    """Tests de integración (requieren Ollama funcionando)"""

    @pytest.mark.skipif(
        True,  # Skip by default, enable manually for local testing
        reason="Requires Ollama server running locally"
    )
    @pytest.mark.asyncio
    async def test_real_ollama_generate(self):
        """Test de integración real con Ollama (ejecutar solo si Ollama está corriendo)"""
        provider = OllamaProvider({
            "base_url": "http://localhost:11434",
            "model": "llama2",
            "timeout": 120.0
        })

        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content="You are a helpful assistant"),
            LLMMessage(role=LLMRole.USER, content="Say 'Hello, World!' and nothing else")
        ]

        response = await provider.generate(messages, temperature=0.1)

        assert isinstance(response, LLMResponse)
        assert len(response.content) > 0
        assert "hello" in response.content.lower()
        print(f"\n✅ Real Ollama response: {response.content}")

    @pytest.mark.skipif(
        True,  # Skip by default
        reason="Requires Ollama server running locally"
    )
    @pytest.mark.asyncio
    async def test_real_ollama_streaming(self):
        """Test de integración real con streaming (ejecutar solo si Ollama está corriendo)"""
        provider = OllamaProvider({
            "base_url": "http://localhost:11434",
            "model": "llama2"
        })

        messages = [
            LLMMessage(role=LLMRole.USER, content="Count from 1 to 5")
        ]

        chunks = []
        async for chunk in provider.generate_stream(messages):
            chunks.append(chunk)
            print(chunk, end="", flush=True)

        assert len(chunks) > 0
        print(f"\n✅ Received {len(chunks)} chunks from Ollama")
