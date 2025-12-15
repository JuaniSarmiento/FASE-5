"""
Base abstraction for LLM providers

Provides unified interface for different LLM providers (OpenAI, Anthropic, local models, etc.)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class LLMRole(str, Enum):
    """Standard message roles"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class LLMMessage:
    """Standard message format"""
    role: LLMRole
    content: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMResponse:
    """Standard response format"""
    content: str
    model: str
    usage: Dict[str, int]  # tokens used
    metadata: Optional[Dict[str, Any]] = None


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers

    All LLM integrations must implement this interface to ensure
    consistency and interchangeability across the system.

    IMPORTANT: All generate methods are async to support both sync and async implementations.
    Sync implementations should use asyncio.to_thread() or return directly from async.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from messages (async)

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters

        Returns:
            LLMResponse with generated content and metadata
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Generate streaming completion from messages (async)

        Args:
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific parameters

        Yields:
            Chunks of generated content
        """
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        pass

    def validate_config(self) -> bool:
        """
        Validate provider configuration

        Returns:
            True if configuration is valid
        """
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model

        Returns:
            Dictionary with model information
        """
        return {
            "provider": self.__class__.__name__,
            "config": self.config
        }