"""
Mistral LLM provider implementation

Provides integration with Mistral AI API

Supports:
- mistral-small (fast, cost-effective)
- mistral-medium (balanced)
- mistral-large (advanced reasoning)

Configuration:
    api_key: Mistral API key
    model: Model name (default: mistral-small)
    temperature: Sampling temperature (default: 0.7)
    timeout: Request timeout in seconds (default: 60)
"""
from typing import Optional, Dict, Any, List, AsyncIterator
import logging
import httpx
import json
import asyncio

from .base import LLMProvider, LLMMessage, LLMResponse, LLMRole

logger = logging.getLogger(__name__)


class MistralProvider(LLMProvider):
    """
    Mistral AI LLM provider

    Supports models:
    - mistral-small: Fast, efficient
    - mistral-medium: Balanced performance
    - mistral-large: Advanced reasoning

    Configuration:
        api_key: Mistral API key (required)
        model: Default model name (default: mistral-small)
        temperature: Sampling temperature (default: 0.7)
        timeout: Request timeout in seconds (default: 60)
        max_retries: Maximum retry attempts (default: 3)
    """

    # Model definitions
    SMALL_MODEL = "mistral-small-latest"
    MEDIUM_MODEL = "mistral-medium-latest"
    LARGE_MODEL = "mistral-large-latest"
    
    # Base URL for Mistral API
    BASE_URL = "https://api.mistral.ai/v1"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        # Configuration with sensible defaults
        self.api_key = self.config.get("api_key")
        if not self.api_key:
            raise ValueError("Mistral API key is required. Set MISTRAL_API_KEY environment variable.")
        
        self.model = self.config.get("model", self.SMALL_MODEL)
        self.temperature = self.config.get("temperature", 0.7)
        self.timeout = self.config.get("timeout", 60.0)
        
        # Retry configuration
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 1.0)
        self.retry_backoff = self.config.get("retry_backoff", 2.0)

        logger.info(
            f"MistralProvider initialized",
            extra={
                "model": self.model,
                "temperature": self.temperature,
                "timeout": self.timeout
            }
        )

    def _convert_messages_to_mistral_format(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """
        Convert LLMMessage list to Mistral API format
        
        Mistral expects:
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ]
        """
        mistral_messages = []
        
        for msg in messages:
            role_mapping = {
                LLMRole.SYSTEM: "system",
                LLMRole.USER: "user",
                LLMRole.ASSISTANT: "assistant"
            }
            
            mistral_messages.append({
                "role": role_mapping.get(msg.role, "user"),
                "content": msg.content
            })
        
        return mistral_messages

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from messages using Mistral API
        
        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response (optional)
            **kwargs: Additional parameters
        
        Returns:
            LLMResponse with generated content and metadata
        """
        # Determine which model to use
        model = kwargs.get("model") or self.model
        
        # Auto-select model based on task type
        if kwargs.get("is_code_analysis", False) and model == self.SMALL_MODEL:
            model = self.LARGE_MODEL
            logger.info("Switching to Large model for code analysis")
        
        # Convert messages to Mistral format
        mistral_messages = self._convert_messages_to_mistral_format(messages)
        
        # Build request payload
        payload = {
            "model": model,
            "messages": mistral_messages,
            "temperature": temperature,
            "top_p": 0.95
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        # Make request with retries
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    url = f"{self.BASE_URL}/chat/completions"
                    
                    logger.debug(
                        f"Sending request to Mistral (attempt {attempt + 1}/{self.max_retries})",
                        extra={
                            "model": model,
                            "messages_count": len(messages),
                            "temperature": temperature
                        }
                    )
                    
                    response = await client.post(
                        url,
                        json=payload,
                        headers={
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {self.api_key}"
                        }
                    )
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    # Extract content from response
                    if "choices" not in result or not result["choices"]:
                        raise ValueError("No choices in Mistral response")
                    
                    choice = result["choices"][0]
                    content = choice["message"]["content"]
                    
                    # Extract usage metadata
                    usage_data = result.get("usage", {})
                    usage = {
                        "prompt_tokens": usage_data.get("prompt_tokens", 0),
                        "completion_tokens": usage_data.get("completion_tokens", 0),
                        "total_tokens": usage_data.get("total_tokens", 0)
                    }
                    
                    logger.info(
                        "Mistral request successful",
                        extra={
                            "model": model,
                            "usage": usage,
                            "finish_reason": choice.get("finish_reason", "stop")
                        }
                    )
                    
                    return LLMResponse(
                        content=content,
                        model=model,
                        usage=usage,
                        metadata={
                            "finish_reason": choice.get("finish_reason", "stop")
                        }
                    )
                    
            except httpx.HTTPStatusError as e:
                logger.warning(
                    f"Mistral HTTP error (attempt {attempt + 1}/{self.max_retries}): {e.response.status_code}",
                    extra={"response": e.response.text}
                )
                
                # Don't retry on client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    raise
                
                # Retry on server errors (5xx)
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (self.retry_backoff ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise
                    
            except Exception as e:
                logger.error(
                    f"Mistral request failed (attempt {attempt + 1}/{self.max_retries}): {e}",
                    exc_info=True
                )
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (self.retry_backoff ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming completion from messages
        
        Args:
            messages: List of conversation messages
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
        
        Yields:
            Chunks of generated content
        """
        model = kwargs.get("model") or self.model
        
        if kwargs.get("is_code_analysis", False) and model == self.SMALL_MODEL:
            model = self.LARGE_MODEL
        
        # Convert messages to Mistral format
        mistral_messages = self._convert_messages_to_mistral_format(messages)
        
        # Build request payload
        payload = {
            "model": model,
            "messages": mistral_messages,
            "temperature": temperature,
            "stream": True
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = f"{self.BASE_URL}/chat/completions"
            
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.strip() or line.strip() == "data: [DONE]":
                        continue
                    
                    if line.startswith("data: "):
                        try:
                            data = json.loads(line[6:])
                            
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            logger.debug(f"Skipping non-JSON line: {line}")
                            continue

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (approximate)
        
        Uses word count * 1.3 as rough estimate
        
        Args:
            text: Input text
            
        Returns:
            Approximate token count
        """
        words = len(text.split())
        return int(words * 1.3)

    def supports_streaming(self) -> bool:
        """Check if provider supports streaming"""
        return True

    async def analyze_complexity(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze if prompt needs advanced model
        
        Args:
            prompt: The user prompt
            
        Returns:
            Dict with needs_large, reason, confidence
        """
        # Simple heuristic for Mistral
        prompt_lower = prompt.lower()
        
        complex_keywords = [
            "algorithm", "complexity", "optimize", "debug",
            "architecture", "design pattern", "refactor"
        ]
        
        needs_large = any(keyword in prompt_lower for keyword in complex_keywords)
        
        return {
            "needs_pro": needs_large,  # Keep same interface as Gemini
            "reason": "Complex analysis detected" if needs_large else "Simple query",
            "confidence": 0.8 if needs_large else 0.7
        }

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "provider": "mistral",
            "model": self.model,
            "small_model": self.SMALL_MODEL,
            "large_model": self.LARGE_MODEL,
            "supports_streaming": True,
            "supports_code_analysis": True,
            "supports_smart_routing": True,
            "context_window": 32000
        }
