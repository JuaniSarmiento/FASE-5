"""
Schemas para interacciones estudiante-IA
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import base64
import re
from pydantic import BaseModel, Field, field_validator, model_validator

from .enums import CognitiveIntent


class InteractionRequest(BaseModel):
    """Request para procesar una interacción del estudiante"""

    session_id: str = Field(..., min_length=1, description="ID de la sesión activa")
    # FIX FLUJO1-2: Unificar validación de longitud con frontend (mínimo 10 chars)
    prompt: str = Field(..., min_length=10, max_length=5000, description="Prompt del estudiante (mínimo 10 caracteres)")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional (código, archivos, etc.)")
    cognitive_intent: Optional[CognitiveIntent] = Field(None, description="Intención cognitiva declarada por el estudiante")

    @field_validator("session_id")
    @classmethod
    def validate_session_id_format(cls, v: str) -> str:
        """
        Valida que session_id tenga formato UUID válido.
        Previene SQL injection y errores de tipo.
        """
        # Regex UUID v4 (8-4-4-4-12 hex digits)
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, v, re.IGNORECASE):
            raise ValueError(
                f"Invalid session_id format. Expected UUID format "
                f"(e.g., '550e8400-e29b-41d4-a716-446655440000'), got: {v[:50]}"
            )
        return v.lower()  # Normalizar a lowercase

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """
        Valida el prompt del estudiante para prevenir inyección de prompts y contenido malicioso.

        Detecta patrones sospechosos como:
        - Intentos de inyección de prompts ("ignore previous", "system:", etc.)
        - Comandos de manipulación de sistema
        - Patrones de jailbreak comunes
        - Prompts vacíos o con solo espacios en blanco

        Raises:
            ValueError: Si se detecta contenido sospechoso o prompt vacío
        """
        # Validar que el prompt no esté vacío después de quitar espacios
        v = v.strip()  # Normalizar whitespace primero
        if not v:
            raise ValueError(
                "Prompt cannot be empty or whitespace only. "
                "Please provide a meaningful question or request."
            )

        # Patrones peligrosos de inyección de prompts
        dangerous_patterns = [
            # Inyección directa
            r"ignore\s+previous",
            r"ignore\s+all\s+previous",
            r"disregard\s+previous",
            r"forget\s+previous",

            # Comandos de sistema
            r"system\s*:",
            r"assistant\s*:",
            r"###\s*instruction",
            r"###\s*system",

            # Jailbreak común
            r"pretend\s+you\s+are",
            r"act\s+as\s+if",
            r"you\s+are\s+now",
            r"new\s+instructions",

            # Manipulación de rol
            r"you\s+must\s+ignore",
            r"your\s+new\s+role",
            r"bypass\s+restrictions",
        ]

        v_lower = v.lower()

        for pattern in dangerous_patterns:
            if re.search(pattern, v_lower):
                raise ValueError(
                    f"Suspicious content detected. Prompts attempting to manipulate system behavior are not allowed."
                )

        # Detectar exceso de caracteres repetidos (posible intento de saturación)
        if re.search(r'(.)\1{50,}', v):
            raise ValueError("Excessive repeated characters detected")

        # Detectar líneas excesivamente largas (>1000 chars sin espacios)
        lines = v.split('\n')
        for line in lines:
            if len(line.replace(' ', '')) > 1000:
                raise ValueError("Line too long without spaces (max 1000 chars)")

        return v  # Return stripped version

    @field_validator("context")
    @classmethod
    def validate_context_size(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Valida el tamaño del contexto y detecta contenido embebido sospechoso.

        Límites:
        - Tamaño total JSON: 100KB
        - No permite base64 embebido grande (posible evasión)

        Raises:
            ValueError: Si el contexto es demasiado grande o contiene contenido sospechoso
        """
        if v is None:
            return v

        # Validar tamaño total del contexto
        context_json = json.dumps(v)
        context_size_bytes = len(context_json.encode('utf-8'))

        MAX_CONTEXT_SIZE = 100 * 1024  # 100KB

        if context_size_bytes > MAX_CONTEXT_SIZE:
            raise ValueError(
                f"Context too large: {context_size_bytes} bytes "
                f"(max {MAX_CONTEXT_SIZE} bytes / {MAX_CONTEXT_SIZE // 1024}KB)"
            )

        # Detectar base64 embebido sospechosamente largo
        # (posible intento de evadir validaciones embebiendo código/prompts)
        for key, value in v.items():
            if isinstance(value, str):
                # Detectar patrones base64 largos (>10KB)
                if len(value) > 10000:
                    try:
                        # Intentar decodificar como base64
                        decoded = base64.b64decode(value, validate=True)
                        if len(decoded) > 50000:  # >50KB decodificado
                            raise ValueError(
                                f"Suspicious large base64 encoded content detected in context field '{key}'"
                            )
                    except Exception:
                        # No es base64 válido, continuar
                        pass

        return v

    @model_validator(mode='after')
    def validate_overall_request(self):
        """
        Validación a nivel de modelo completo.

        Verifica:
        - Coherencia entre prompt y contexto
        - Límites globales de tamaño
        """
        # Calcular tamaño total del request
        total_size = len(self.prompt.encode('utf-8'))
        if self.context:
            total_size += len(json.dumps(self.context).encode('utf-8'))

        MAX_TOTAL_SIZE = 150 * 1024  # 150KB total

        if total_size > MAX_TOTAL_SIZE:
            raise ValueError(
                f"Total request size too large: {total_size} bytes "
                f"(max {MAX_TOTAL_SIZE} bytes / {MAX_TOTAL_SIZE // 1024}KB)"
            )

        return self

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "prompt": "¿Cómo puedo implementar una cola circular eficientemente?",
                "context": {
                    "code_snippet": "class Queue:\n    def __init__(self)...",
                    "line_number": 15
                },
                "cognitive_intent": "UNDERSTANDING"
            }
        }


class InteractionResponse(BaseModel):
    """Response de una interacción procesada"""

    interaction_id: str = Field(..., description="ID único de la interacción")
    session_id: str = Field(..., description="ID de la sesión")
    response: str = Field(..., description="Respuesta del agente")
    agent_used: str = Field(..., description="Agente que procesó la interacción")
    cognitive_state_detected: str = Field(..., description="Estado cognitivo detectado")
    ai_involvement: float = Field(..., ge=0, le=1, description="Nivel de involucramiento de IA (0-1)")
    blocked: bool = Field(False, description="Indica si la interacción fue bloqueada por gobernanza")
    block_reason: Optional[str] = Field(None, description="Razón del bloqueo si aplica")
    trace_id: str = Field(..., description="ID de la traza N4 generada")
    risks_detected: List[str] = Field(default_factory=list, description="IDs de riesgos detectados")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de la interacción")
    # FIX FLUJO1-1: Añadido tokens_used para compatibilidad con frontend
    tokens_used: Optional[int] = Field(None, description="Tokens utilizados en la generación (si disponible)")

    class Config:
        json_schema_extra = {
            "example": {
                "interaction_id": "interaction_xyz789",
                "session_id": "session_abc123",
                "response": "Para implementar una cola circular...",
                "agent_used": "T-IA-Cog",
                "cognitive_state_detected": "EXPLORACION_CONCEPTUAL",
                "ai_involvement": 0.4,
                "blocked": False,
                "block_reason": None,
                "trace_id": "trace_123",
                "risks_detected": [],
                "timestamp": "2025-11-18T10:30:00Z",
                "tokens_used": 150
            }
        }


class InteractionHistory(BaseModel):
    """Historial de interacciones de una sesión"""

    session_id: str = Field(..., description="ID de la sesión")
    interactions: List["InteractionSummary"] = Field(..., description="Lista de interacciones")
    total_interactions: int = Field(..., description="Total de interacciones")
    avg_ai_involvement: float = Field(..., description="Promedio de involucramiento de IA")
    blocked_count: int = Field(0, description="Cantidad de interacciones bloqueadas")


class InteractionSummary(BaseModel):
    """Resumen de una interacción"""

    id: str = Field(..., description="ID de la interacción")
    prompt_preview: str = Field(..., description="Vista previa del prompt (primeros 100 chars)")
    agent_used: str = Field(..., description="Agente utilizado")
    cognitive_state: str = Field(..., description="Estado cognitivo")
    ai_involvement: float = Field(..., description="Involucramiento de IA")
    blocked: bool = Field(..., description="Si fue bloqueada")
    timestamp: datetime = Field(..., description="Timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "interaction_xyz789",
                "prompt_preview": "¿Cómo puedo implementar una cola circular eficientemente?",
                "agent_used": "T-IA-Cog",
                "cognitive_state": "EXPLORACION_CONCEPTUAL",
                "ai_involvement": 0.4,
                "blocked": False,
                "timestamp": "2025-11-18T10:30:00Z"
            }
        }