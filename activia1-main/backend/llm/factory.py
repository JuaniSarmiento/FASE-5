"""
LLM Provider Factory

Centraliza la creación y configuración de proveedores LLM.
Implementa Factory Pattern para bajo acoplamiento y extensibilidad.

Soporta:
- mock: Provider simulado para testing/desarrollo (sin API calls)
- ollama: Ollama (LLMs locales - Llama 2, Mistral, etc.)

Usage:
    >>> from src.ai_native_mvp.llm import LLMProviderFactory
    >>>
    >>> # Método 1: Desde variables de entorno (recomendado)
    >>> provider = LLMProviderFactory.create_from_env()
    >>>
    >>> # Método 2: Configuración manual
    >>> provider = LLMProviderFactory.create("ollama", {
    ...     "base_url": "http://localhost:11434",
    ...     "model": "llama2"
    ... })
    >>>
    >>> # Generar respuesta
    >>> response = await provider.generate(messages, temperature=0.7)
"""
from typing import Optional, Dict, Any

from .base import LLMProvider
from .mock import MockLLMProvider


class LLMProviderFactory:
    """
    Factory for creating LLM providers

    Supports:
    - mock: Mock provider for testing/development
    - ollama: Ollama provider (local models)

    Usage:
        >>> factory = LLMProviderFactory()
        >>> provider = factory.create("mock")
        >>> provider = factory.create("ollama", {"base_url": "http://localhost:11434"})
    """

    # Registry of available providers
    _providers = {
        "mock": MockLLMProvider,
    }
    
    # Task type constants for model selection
    TASK_CONVERSATION = "conversation"
    TASK_CODE_ANALYSIS = "code_analysis"

    @classmethod
    def register_provider(cls, name: str, provider_class):
        """
        Register a new provider type

        Args:
            name: Provider identifier
            provider_class: Provider class (must inherit from LLMProvider)
        """
        if not issubclass(provider_class, LLMProvider):
            raise ValueError(f"{provider_class} must inherit from LLMProvider")

        cls._providers[name] = provider_class

    @classmethod
    def create(
        cls,
        provider_type: str,
        config: Optional[Dict[str, Any]] = None
    ) -> LLMProvider:
        """
        Create LLM provider instance

        Args:
            provider_type: Type of provider ("mock", "openai", etc.)
            config: Provider-specific configuration

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If provider type is not registered
        """
        if provider_type not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unknown provider type: {provider_type}. "
                f"Available providers: {available}"
            )

        provider_class = cls._providers[provider_type]
        return provider_class(config)

    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of registered provider types"""
        return list(cls._providers.keys())

    @classmethod
    def create_from_env(cls, provider_type: str = None) -> LLMProvider:
        """
        Create provider using environment variables

        Looks for:
        - LLM_PROVIDER to determine which provider to use (if provider_type not specified)
        - OLLAMA_BASE_URL, OLLAMA_MODEL for Ollama

        Args:
            provider_type: Type of provider (optional, reads from LLM_PROVIDER env var if not provided)

        Returns:
            Configured provider instance

        Example:
            >>> # Set LLM_PROVIDER=ollama in .env
            >>> provider = LLMProviderFactory.create_from_env()  # Uses Ollama
            >>>
            >>> # Or specify explicitly
            >>> provider = LLMProviderFactory.create_from_env("ollama")
        """
        import os

        # If provider_type not specified, read from environment
        if provider_type is None:
            provider_type = os.getenv("LLM_PROVIDER", "ollama")

        config = {}

        if provider_type == "ollama":
            # Ollama no requiere API key, solo base_url y model
            config["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            config["model"] = os.getenv("OLLAMA_MODEL", "llama2")
            config["temperature"] = float(os.getenv("OLLAMA_TEMPERATURE", "0.7"))
            timeout = os.getenv("OLLAMA_TIMEOUT")
            if timeout:
                config["timeout"] = float(timeout)

            # Keep model loaded in memory to avoid repeated cold starts
            keep_alive = os.getenv("OLLAMA_KEEP_ALIVE")
            if keep_alive:
                config["keep_alive"] = keep_alive

            # Optional performance-related parameters (passed to Ollama as options)
            # These can significantly affect latency depending on model + hardware.
            options: dict[str, object] = {}
            num_ctx = os.getenv("OLLAMA_NUM_CTX")
            if num_ctx:
                options["num_ctx"] = int(num_ctx)
            num_thread = os.getenv("OLLAMA_NUM_THREAD")
            if num_thread:
                options["num_thread"] = int(num_thread)
            num_gpu = os.getenv("OLLAMA_NUM_GPU")
            if num_gpu:
                options["num_gpu"] = int(num_gpu)

            if options:
                config["options"] = options
        
        elif provider_type == "gemini":
            # Gemini requires API key
            config["api_key"] = os.getenv("GEMINI_API_KEY")
            if not config["api_key"]:
                raise ValueError(
                    "GEMINI_API_KEY environment variable is required for Gemini provider. "
                    "Get your API key from https://makersuite.google.com/app/apikey"
                )
            
            # Default model (flash for conversations, pro for code analysis)
            config["model"] = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
            config["temperature"] = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
            
            timeout = os.getenv("GEMINI_TIMEOUT")
            if timeout:
                config["timeout"] = float(timeout)
            
            # Retry configuration
            max_retries = os.getenv("GEMINI_MAX_RETRIES")
            if max_retries:
                config["max_retries"] = int(max_retries)

        elif provider_type == "mistral":
            # Mistral requires API key
            config["api_key"] = os.getenv("MISTRAL_API_KEY")
            if not config["api_key"]:
                raise ValueError(
                    "MISTRAL_API_KEY environment variable is required for Mistral provider."
                )
            
            # Default model
            config["model"] = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
            config["temperature"] = float(os.getenv("MISTRAL_TEMPERATURE", "0.7"))
            
            timeout = os.getenv("MISTRAL_TIMEOUT")
            if timeout:
                config["timeout"] = float(timeout)
            
            # Retry configuration
            max_retries = os.getenv("MISTRAL_MAX_RETRIES")
            if max_retries:
                config["max_retries"] = int(max_retries)
        
        elif provider_type == "mock":
            # Mock provider doesn't need configuration
            pass

        return cls.create(provider_type, config)


# Register Ollama provider (lazy loading)
def _register_ollama():
    """Register Ollama provider if available"""
    try:
        from .ollama_provider import OllamaProvider
        LLMProviderFactory.register_provider("ollama", OllamaProvider)
    except ImportError:
        pass  # Ollama not available


# Register Gemini provider (lazy loading)
def _register_gemini():
    """Register Gemini provider if available"""
    try:
        from .gemini_provider import GeminiProvider
        LLMProviderFactory.register_provider("gemini", GeminiProvider)
    except ImportError:
        pass  # Gemini not available


# Register Mistral provider (lazy loading)
def _register_mistral():
    """Register Mistral provider if available"""
    try:
        from .mistral_provider import MistralProvider
        LLMProviderFactory.register_provider("mistral", MistralProvider)
    except ImportError:
        pass  # Mistral not available


# Auto-register available providers
_register_ollama()
_register_gemini()
_register_mistral()