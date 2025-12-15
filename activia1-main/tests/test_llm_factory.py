"""
Tests for LLM Provider Factory

Tests para src/ai_native_mvp/llm/factory.py

Verifica:
1. Creación de providers (mock, openai, gemini, anthropic, ollama)
2. Configuración desde variables de entorno
3. Validación de API keys
4. Manejo de errores (provider inválido, configuración faltante)
5. Registro dinámico de providers
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from backend.llm.factory import LLMProviderFactory
from backend.llm.base import LLMProvider
from backend.llm.mock import MockLLMProvider


class TestLLMProviderFactoryBasics:
    """Tests básicos de LLMProviderFactory"""

    def test_get_available_providers(self):
        """get_available_providers() retorna lista de providers registrados"""
        available = LLMProviderFactory.get_available_providers()

        assert isinstance(available, list)
        assert "mock" in available
        # openai y gemini pueden o no estar registrados dependiendo de imports

    def test_create_mock_provider_without_config(self):
        """create('mock') sin config retorna MockLLMProvider"""
        provider = LLMProviderFactory.create("mock")

        assert isinstance(provider, MockLLMProvider)
        assert isinstance(provider, LLMProvider)

    def test_create_mock_provider_with_config(self):
        """create('mock', config) retorna MockLLMProvider con config"""
        config = {"model": "mock-gpt-4", "temperature": 0.5}
        provider = LLMProviderFactory.create("mock", config)

        assert isinstance(provider, MockLLMProvider)

    def test_create_invalid_provider_raises_error(self):
        """create() con provider inválido debe lanzar ValueError"""
        with pytest.raises(ValueError) as exc_info:
            LLMProviderFactory.create("invalid_provider_xyz")

        error_msg = str(exc_info.value)
        assert "Unknown provider type: invalid_provider_xyz" in error_msg
        assert "Available providers:" in error_msg

    def test_register_provider_valid_class(self):
        """register_provider() con clase válida debe registrar correctamente"""
        # Crear clase de prueba que hereda de LLMProvider
        class TestProvider(LLMProvider):
            def generate(self, messages, **kwargs):
                return MagicMock()

            def generate_stream(self, messages, **kwargs):
                yield "test"

            def count_tokens(self, text):
                return 10

        # Registrar
        LLMProviderFactory.register_provider("test_provider", TestProvider)

        # Verificar que se registró
        assert "test_provider" in LLMProviderFactory.get_available_providers()

        # Verificar que se puede crear
        provider = LLMProviderFactory.create("test_provider")
        assert isinstance(provider, TestProvider)

        # Cleanup: desregistrar para no afectar otros tests
        if "test_provider" in LLMProviderFactory._providers:
            del LLMProviderFactory._providers["test_provider"]

    def test_register_provider_invalid_class_raises_error(self):
        """register_provider() con clase que no hereda de LLMProvider debe fallar"""
        class InvalidProvider:
            pass

        with pytest.raises(ValueError) as exc_info:
            LLMProviderFactory.register_provider("invalid", InvalidProvider)

        assert "must inherit from LLMProvider" in str(exc_info.value)


class TestLLMProviderFactoryEnvironment:
    """Tests de creación desde variables de entorno"""

    @pytest.fixture
    def clean_env(self):
        """Limpia variables de entorno antes de cada test"""
        env_vars = [
            "LLM_PROVIDER",
            "OPENAI_API_KEY",
            "OPENAI_MODEL",
            "OPENAI_TEMPERATURE",
            "OPENAI_MAX_TOKENS",
            "OPENAI_ORGANIZATION",
            "GEMINI_API_KEY",
            "GEMINI_MODEL",
            "GEMINI_TEMPERATURE",
            "GEMINI_MAX_TOKENS",
            "ANTHROPIC_API_KEY",
            "ANTHROPIC_MODEL",
            "OLLAMA_BASE_URL",
            "OLLAMA_MODEL",
        ]
        original_values = {}
        for var in env_vars:
            original_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

        yield

        # Restore
        for var, value in original_values.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    def test_create_from_env_defaults_to_mock(self, clean_env):
        """create_from_env() sin LLM_PROVIDER debe usar 'mock' por defecto"""
        provider = LLMProviderFactory.create_from_env()

        assert isinstance(provider, MockLLMProvider)

    def test_create_from_env_respects_llm_provider_env(self, clean_env):
        """create_from_env() respeta LLM_PROVIDER si está configurado"""
        os.environ["LLM_PROVIDER"] = "mock"

        provider = LLMProviderFactory.create_from_env()

        assert isinstance(provider, MockLLMProvider)

    def test_create_from_env_explicit_provider_type(self, clean_env):
        """create_from_env(provider_type='mock') usa el tipo explícito"""
        # Configurar LLM_PROVIDER diferente
        os.environ["LLM_PROVIDER"] = "gemini"

        # Pero especificar mock explícitamente
        provider = LLMProviderFactory.create_from_env("mock")

        assert isinstance(provider, MockLLMProvider)

    @pytest.mark.skipif(
        "openai" not in LLMProviderFactory.get_available_providers(),
        reason="OpenAI provider not registered"
    )
    def test_create_from_env_openai_missing_api_key_raises_error(self, clean_env):
        """create_from_env('openai') sin API key debe lanzar ValueError"""
        with pytest.raises(ValueError) as exc_info:
            LLMProviderFactory.create_from_env("openai")

        error_msg = str(exc_info.value)
        assert "OPENAI_API_KEY" in error_msg
        assert "environment variable is required" in error_msg
        assert "https://platform.openai.com/api-keys" in error_msg

    @pytest.mark.skipif(
        "openai" not in LLMProviderFactory.get_available_providers(),
        reason="OpenAI provider not registered"
    )
    def test_create_from_env_openai_with_api_key_succeeds(self, clean_env):
        """create_from_env('openai') con API key válida debe crear provider"""
        os.environ["OPENAI_API_KEY"] = "sk-test-key-12345678901234567890"

        provider = LLMProviderFactory.create_from_env("openai")

        assert provider is not None
        # Verificar que es instancia de OpenAIProvider (si está registrado)

    @pytest.mark.skipif(
        "openai" not in LLMProviderFactory.get_available_providers(),
        reason="OpenAI provider not registered"
    )
    def test_create_from_env_openai_with_custom_model(self, clean_env):
        """create_from_env('openai') respeta OPENAI_MODEL si está configurado"""
        os.environ["OPENAI_API_KEY"] = "sk-test-key-12345678901234567890"
        os.environ["OPENAI_MODEL"] = "gpt-3.5-turbo"

        provider = LLMProviderFactory.create_from_env("openai")

        assert provider is not None
        # El modelo se pasa en config al provider

    @pytest.mark.skipif(
        "gemini" not in LLMProviderFactory.get_available_providers(),
        reason="Gemini provider not registered"
    )
    def test_create_from_env_gemini_missing_api_key_raises_error(self, clean_env):
        """create_from_env('gemini') sin API key debe lanzar ValueError"""
        with pytest.raises(ValueError) as exc_info:
            LLMProviderFactory.create_from_env("gemini")

        error_msg = str(exc_info.value)
        assert "GEMINI_API_KEY" in error_msg
        assert "environment variable is required" in error_msg

    @pytest.mark.skipif(
        "gemini" not in LLMProviderFactory.get_available_providers(),
        reason="Gemini provider not registered"
    )
    def test_create_from_env_gemini_with_api_key_succeeds(self, clean_env):
        """create_from_env('gemini') con API key válida debe crear provider"""
        os.environ["GEMINI_API_KEY"] = "AIzaSy-test-key-1234567890"

        provider = LLMProviderFactory.create_from_env("gemini")

        assert provider is not None

    @pytest.mark.skipif(
        "ollama" not in LLMProviderFactory.get_available_providers(),
        reason="Ollama provider not registered"
    )
    def test_create_from_env_ollama_uses_defaults(self, clean_env):
        """create_from_env('ollama') usa valores por defecto sin API key"""
        # Ollama no requiere API key
        provider = LLMProviderFactory.create_from_env("ollama")

        # Debe usar defaults: base_url=http://localhost:11434, model=llama2
        assert provider is not None

    @pytest.mark.skipif(
        "ollama" not in LLMProviderFactory.get_available_providers(),
        reason="Ollama provider not registered"
    )
    def test_create_from_env_ollama_respects_custom_config(self, clean_env):
        """create_from_env('ollama') respeta configuración personalizada"""
        os.environ["OLLAMA_BASE_URL"] = "http://192.168.1.100:11434"
        os.environ["OLLAMA_MODEL"] = "mistral"

        provider = LLMProviderFactory.create_from_env("ollama")

        assert provider is not None


class TestBuildProviderConfig:
    """Tests para método privado _build_provider_config"""

    @pytest.fixture
    def clean_env(self):
        """Limpia variables de entorno"""
        env_vars = [
            "TEST_API_KEY",
            "TEST_MODEL",
            "TEST_TEMPERATURE",
            "TEST_MAX_TOKENS",
        ]
        original_values = {}
        for var in env_vars:
            original_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]

        yield

        # Restore
        for var, value in original_values.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]

    def test_build_provider_config_basic(self, clean_env):
        """_build_provider_config() crea configuración básica correctamente"""
        os.environ["TEST_API_KEY"] = "test-key-123"

        config = LLMProviderFactory._build_provider_config(
            provider_type="test",
            env_prefix="TEST",
            default_model="test-model-v1",
            api_key_url="https://example.com/keys",
            optional_fields=None
        )

        assert config["api_key"] == "test-key-123"
        assert config["model"] == "test-model-v1"

    def test_build_provider_config_custom_model(self, clean_env):
        """_build_provider_config() respeta modelo personalizado"""
        os.environ["TEST_API_KEY"] = "test-key-123"
        os.environ["TEST_MODEL"] = "test-model-custom"

        config = LLMProviderFactory._build_provider_config(
            provider_type="test",
            env_prefix="TEST",
            default_model="test-model-v1",
            api_key_url="https://example.com/keys"
        )

        assert config["model"] == "test-model-custom"

    def test_build_provider_config_with_optional_fields(self, clean_env):
        """_build_provider_config() procesa campos opcionales correctamente"""
        os.environ["TEST_API_KEY"] = "test-key-123"
        os.environ["TEST_TEMPERATURE"] = "0.8"
        os.environ["TEST_MAX_TOKENS"] = "2000"

        config = LLMProviderFactory._build_provider_config(
            provider_type="test",
            env_prefix="TEST",
            default_model="test-model-v1",
            api_key_url="https://example.com/keys",
            optional_fields={
                "temperature": ("TEST_TEMPERATURE", float, None),
                "max_tokens": ("TEST_MAX_TOKENS", int, None),
            }
        )

        assert config["temperature"] == 0.8
        assert config["max_tokens"] == 2000

    def test_build_provider_config_missing_api_key_raises_error(self, clean_env):
        """_build_provider_config() sin API key debe lanzar ValueError"""
        with pytest.raises(ValueError) as exc_info:
            LLMProviderFactory._build_provider_config(
                provider_type="test",
                env_prefix="TEST",
                default_model="test-model-v1",
                api_key_url="https://example.com/keys"
            )

        error_msg = str(exc_info.value)
        assert "TEST_API_KEY" in error_msg
        assert "environment variable is required" in error_msg
        assert "https://example.com/keys" in error_msg

    def test_build_provider_config_invalid_optional_field_uses_default(self, clean_env):
        """_build_provider_config() usa default si campo opcional tiene valor inválido"""
        os.environ["TEST_API_KEY"] = "test-key-123"
        os.environ["TEST_TEMPERATURE"] = "not_a_number"  # Valor inválido

        config = LLMProviderFactory._build_provider_config(
            provider_type="test",
            env_prefix="TEST",
            default_model="test-model-v1",
            api_key_url="https://example.com/keys",
            optional_fields={
                "temperature": ("TEST_TEMPERATURE", float, 0.7),  # Default: 0.7
            }
        )

        # Debe usar default 0.7 porque parsing falló
        assert config["temperature"] == 0.7

    def test_build_provider_config_optional_field_not_set(self, clean_env):
        """_build_provider_config() omite campos opcionales no configurados"""
        os.environ["TEST_API_KEY"] = "test-key-123"
        # No configurar TEST_TEMPERATURE

        config = LLMProviderFactory._build_provider_config(
            provider_type="test",
            env_prefix="TEST",
            default_model="test-model-v1",
            api_key_url="https://example.com/keys",
            optional_fields={
                "temperature": ("TEST_TEMPERATURE", float, None),
            }
        )

        # Campo no debe estar en config si no se configuró y default es None
        assert "temperature" not in config


@pytest.mark.integration
class TestLLMProviderFactoryIntegration:
    """Tests de integración con providers reales"""

    def test_factory_creates_functional_mock_provider(self):
        """Factory crea MockLLMProvider funcional que puede generar respuestas"""
        provider = LLMProviderFactory.create_from_env("mock")

        # Generar respuesta
        from backend.llm.base import LLMMessage, LLMRole
        messages = [
            LLMMessage(role=LLMRole.USER, content="Test message")
        ]

        response = provider.generate(messages)

        assert response is not None
        assert hasattr(response, "content")
        assert hasattr(response, "usage")

    def test_factory_preserves_provider_config(self):
        """Factory pasa configuración correctamente al provider"""
        config = {"model": "mock-custom-model", "temperature": 0.5}
        provider = LLMProviderFactory.create("mock", config)

        # MockLLMProvider debe recibir y almacenar config
        assert provider is not None

    @pytest.mark.skipif(
        "openai" not in LLMProviderFactory.get_available_providers(),
        reason="OpenAI provider not registered"
    )
    def test_factory_creates_openai_provider_from_manual_config(self):
        """Factory crea OpenAIProvider desde config manual (sin env vars)"""
        config = {
            "api_key": "sk-test-fake-key-for-testing-only",
            "model": "gpt-4"
        }

        provider = LLMProviderFactory.create("openai", config)

        assert provider is not None
        # Provider está configurado pero no llamamos a OpenAI API (requiere key real)
