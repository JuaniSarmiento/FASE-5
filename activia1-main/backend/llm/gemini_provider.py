"""
Gemini LLM provider implementation

Provides integration with Google Gemini API

Supports:
- gemini-1.5-flash (fast, cost-effective for conversational AI)
- gemini-1.5-pro (advanced reasoning for code analysis)

Configuration:
    api_key: Google API key for Gemini
    model: Model name (default: gemini-1.5-flash)
    temperature: Sampling temperature (default: 0.7)
    timeout: Request timeout in seconds (default: 60)

Example:
    >>> provider = GeminiProvider({
    ...     "api_key": "your-api-key",
    ...     "model": "gemini-1.5-flash",
    ...     "temperature": 0.7
    ... })
    >>> response = await provider.generate(messages)

Features:
- Fast response times with Flash model
- Advanced reasoning with Pro model
- Automatic model selection based on task type
- Cost-effective pricing
"""
from typing import Optional, Dict, Any, List, AsyncIterator
import logging
import httpx
import json
import asyncio
from contextlib import asynccontextmanager

from .base import LLMProvider, LLMMessage, LLMResponse, LLMRole

# Prometheus metrics instrumentation
_metrics_module = None

def _get_metrics():
    """Lazy load metrics module to avoid circular imports."""
    global _metrics_module
    if _metrics_module is None:
        try:
            from ..api.monitoring.metrics import metrics_accessor
            _metrics_module = metrics_accessor
        except ImportError:
            _metrics_module = False
    return _metrics_module if _metrics_module else None

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """
    Google Gemini LLM provider

    Supports automatic model selection:
    - gemini-1.5-flash: Fast, efficient for tutoring and conversations
    - gemini-1.5-pro: Advanced reasoning for code analysis

    Configuration:
        api_key: Google API key (required)
        model: Default model name (default: gemini-1.5-flash)
        temperature: Sampling temperature (default: 0.7)
        timeout: Request timeout in seconds (default: 60)
        max_retries: Maximum retry attempts (default: 3)
    """

    # Model definitions (Updated to Gemini 2.5)
    FLASH_MODEL = "gemini-2.5-flash"
    PRO_MODEL = "gemini-2.5-pro"
    
    # Base URL for Gemini API
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

        # Configuration with sensible defaults
        self.api_key = self.config.get("api_key")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable.")
        
        self.model = self.config.get("model", self.FLASH_MODEL)
        self.temperature = self.config.get("temperature", 0.7)
        self.timeout = self.config.get("timeout", 60.0)
        
        # Retry configuration
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 1.0)
        self.retry_backoff = self.config.get("retry_backoff", 2.0)

        logger.info(
            f"GeminiProvider initialized",
            extra={
                "model": self.model,
                "temperature": self.temperature,
                "timeout": self.timeout
            }
        )

    def _convert_messages_to_gemini_format(self, messages: List[LLMMessage]) -> Dict[str, Any]:
        """
        Convert LLMMessage list to Gemini API format
        
        Gemini expects:
        {
            "contents": [
                {
                    "role": "user" | "model",
                    "parts": [{"text": "..."}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": "system prompt"}]
            }
        }
        """
        system_instruction = None
        contents = []
        
        for msg in messages:
            if msg.role == LLMRole.SYSTEM:
                # Gemini uses separate systemInstruction field
                system_instruction = {
                    "parts": [{"text": msg.content}]
                }
            else:
                # Convert user/assistant to Gemini format
                role = "user" if msg.role == LLMRole.USER else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg.content}]
                })
        
        payload = {"contents": contents}
        if system_instruction:
            payload["systemInstruction"] = system_instruction
            
        return payload

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from messages using Gemini API
        
        Args:
            messages: List of conversation messages
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response (optional)
            **kwargs: Additional parameters
                - model: Override default model
                - is_code_analysis: Use Pro model for code analysis
        
        Returns:
            LLMResponse with generated content and metadata
        """
        # Determine which model to use
        model = kwargs.get("model") or self.model
        
        # Auto-select model based on task type
        if kwargs.get("is_code_analysis", False) and model == self.FLASH_MODEL:
            model = self.PRO_MODEL
            logger.info("Switching to Pro model for code analysis")
        
        # Convert messages to Gemini format
        payload = self._convert_messages_to_gemini_format(messages)
        
        # Add generation config
        generation_config = {
            "temperature": temperature,
            "topP": 0.95,
            "topK": 40
        }
        
        if max_tokens:
            generation_config["maxOutputTokens"] = max_tokens
            
        payload["generationConfig"] = generation_config
        
        # Add safety settings (permissive for educational content)
        payload["safetySettings"] = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        # Make request with retries
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    url = f"{self.BASE_URL}/models/{model}:generateContent?key={self.api_key}"
                    
                    logger.debug(
                        f"Sending request to Gemini (attempt {attempt + 1}/{self.max_retries})",
                        extra={
                            "model": model,
                            "messages_count": len(messages),
                            "temperature": temperature
                        }
                    )
                    
                    response = await client.post(
                        url,
                        json=payload,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    response.raise_for_status()
                    result = response.json()
                    
                    # Extract content from response
                    if "candidates" not in result or not result["candidates"]:
                        raise ValueError("No candidates in Gemini response")
                    
                    candidate = result["candidates"][0]
                    content = candidate["content"]["parts"][0]["text"]
                    
                    # Extract usage metadata
                    usage_metadata = result.get("usageMetadata", {})
                    usage = {
                        "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
                        "completion_tokens": usage_metadata.get("candidatesTokenCount", 0),
                        "total_tokens": usage_metadata.get("totalTokenCount", 0)
                    }
                    
                    # Update metrics
                    metrics = _get_metrics()
                    if metrics:
                        metrics.llm_requests_total.labels(
                            provider="gemini",
                            model=model,
                            status="success"
                        ).inc()
                        metrics.llm_tokens_total.labels(
                            provider="gemini",
                            model=model,
                            token_type="prompt"
                        ).inc(usage["prompt_tokens"])
                        metrics.llm_tokens_total.labels(
                            provider="gemini",
                            model=model,
                            token_type="completion"
                        ).inc(usage["completion_tokens"])
                    
                    logger.info(
                        "Gemini request successful",
                        extra={
                            "model": model,
                            "usage": usage,
                            "finish_reason": candidate.get("finishReason", "STOP")
                        }
                    )
                    
                    return LLMResponse(
                        content=content,
                        model=model,
                        usage=usage,
                        metadata={
                            "finish_reason": candidate.get("finishReason", "STOP"),
                            "safety_ratings": candidate.get("safetyRatings", [])
                        }
                    )
                    
            except httpx.HTTPStatusError as e:
                logger.warning(
                    f"Gemini HTTP error (attempt {attempt + 1}/{self.max_retries}): {e.response.status_code}",
                    extra={"response": e.response.text}
                )
                
                # Don't retry on client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    metrics = _get_metrics()
                    if metrics:
                        metrics.llm_requests_total.labels(
                            provider="gemini",
                            model=model,
                            status="error"
                        ).inc()
                    raise
                
                # Retry on server errors (5xx)
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (self.retry_backoff ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    metrics = _get_metrics()
                    if metrics:
                        metrics.llm_requests_total.labels(
                            provider="gemini",
                            model=model,
                            status="error"
                        ).inc()
                    raise
                    
            except Exception as e:
                logger.error(
                    f"Gemini request failed (attempt {attempt + 1}/{self.max_retries}): {e}",
                    exc_info=True
                )
                
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (self.retry_backoff ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    metrics = _get_metrics()
                    if metrics:
                        metrics.llm_requests_total.labels(
                            provider="gemini",
                            model=model,
                            status="error"
                        ).inc()
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
        # Determine which model to use
        model = kwargs.get("model") or self.model
        
        if kwargs.get("is_code_analysis", False) and model == self.FLASH_MODEL:
            model = self.PRO_MODEL
        
        # Convert messages to Gemini format
        payload = self._convert_messages_to_gemini_format(messages)
        
        # Add generation config
        generation_config = {
            "temperature": temperature,
            "topP": 0.95,
            "topK": 40
        }
        
        if max_tokens:
            generation_config["maxOutputTokens"] = max_tokens
            
        payload["generationConfig"] = generation_config
        
        # Add safety settings
        payload["safetySettings"] = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = f"{self.BASE_URL}/models/{model}:streamGenerateContent?key={self.api_key}"
            
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    try:
                        # Parse JSON from stream
                        data = json.loads(line)
                        
                        if "candidates" in data and data["candidates"]:
                            candidate = data["candidates"][0]
                            if "content" in candidate:
                                parts = candidate["content"].get("parts", [])
                                for part in parts:
                                    if "text" in part:
                                        yield part["text"]
                    except json.JSONDecodeError:
                        logger.debug(f"Skipping non-JSON line: {line}")
                        continue

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (approximate)
        
        Gemini uses SentencePiece tokenizer, but we approximate
        using word count * 1.3 as a rough estimate
        
        Args:
            text: Input text
            
        Returns:
            Approximate token count
        """
        # Rough approximation: words * 1.3
        words = len(text.split())
        return int(words * 1.3)

    def supports_streaming(self) -> bool:
        """Check if provider supports streaming"""
        return True

    async def analyze_complexity(self, prompt: str) -> Dict[str, Any]:
        """
        Usa Flash para analizar si una consulta requiere el modelo Pro
        
        Este método permite que Flash decida inteligentemente si la consulta
        necesita análisis profundo (Pro) o puede responderse rápido (Flash).
        
        Args:
            prompt: La consulta del usuario
            
        Returns:
            Dict con:
                - needs_pro: bool - Si requiere modelo Pro
                - reason: str - Razón de la decisión
                - confidence: float - Confianza en la decisión (0-1)
        """
        analysis_prompt = f"""Analiza esta consulta y determina si requiere análisis profundo de código o puede responderse de forma simple.

Consulta: "{prompt}"

Responde SOLO con un JSON en este formato:
{{
  "needs_pro": true/false,
  "reason": "explicación breve",
  "confidence": 0.0-1.0
}}

Usa needs_pro=true si:
- Requiere análisis de complejidad algorítmica
- Necesita revisar código complejo o arquitectura
- Involucra debugging profundo o optimización
- Requiere análisis de patrones de diseño complejos

Usa needs_pro=false si:
- Es una pregunta conceptual simple
- Es conversación normal
- Pregunta sobre sintaxis básica
- Explicaciones de alto nivel"""

        try:
            messages = [
                LLMMessage(role=LLMRole.USER, content=analysis_prompt)
            ]
            
            # Usar Flash para el análisis (rápido y económico)
            response = await self.generate(
                messages,
                temperature=0.3,  # Baja temperatura para decisión consistente
                max_tokens=100,
                model=self.FLASH_MODEL  # Forzar Flash
            )
            
            # Parsear respuesta JSON
            import json
            import re
            
            # Extraer JSON de la respuesta
            json_match = re.search(r'\{[^}]+\}', response.content)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "needs_pro": result.get("needs_pro", False),
                    "reason": result.get("reason", ""),
                    "confidence": result.get("confidence", 0.5)
                }
            else:
                # Fallback: análisis heurístico simple
                logger.warning("Could not parse complexity analysis, using fallback")
                return {
                    "needs_pro": False,
                    "reason": "Could not analyze, defaulting to Flash",
                    "confidence": 0.3
                }
                
        except Exception as e:
            logger.error(f"Error in complexity analysis: {e}")
            # Fallback seguro: usar Flash
            return {
                "needs_pro": False,
                "reason": f"Analysis error: {e}",
                "confidence": 0.0
            }

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "provider": "gemini",
            "model": self.model,
            "flash_model": self.FLASH_MODEL,
            "pro_model": self.PRO_MODEL,
            "supports_streaming": True,
            "supports_code_analysis": True,
            "supports_smart_routing": True,
            "context_window": 1000000 if "pro" in self.model else 32000
        }
