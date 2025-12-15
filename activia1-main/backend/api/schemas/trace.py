"""
Schemas para trazas cognitivas (CognitiveTraceDB)
FIX 3.1: Schemas faltantes para ORM models
FIX Cortez8: Correcciones de consistencia ORM vs Pydantic
"""
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field, field_validator

from .enums import TraceLevel, CognitiveState, InteractionType, normalize_interaction_type


class CognitiveTraceCreate(BaseModel):
    """
    Request para crear una nueva traza cognitiva.

    FIX 2.4 Cortez8: Agregadas las 6 dimensiones N4.
    FIX 4.8 Cortez8: Agregado validator para interaction_type.
    """

    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    trace_level: TraceLevel = Field(
        default=TraceLevel.N4_COGNITIVO,
        description="Nivel de traza: n1_superficial, n2_tecnico, n3_interaccional, n4_cognitivo"
    )
    interaction_type: str = Field(..., description="Tipo de interacción (se normaliza a lowercase)")
    content: str = Field(..., description="Contenido de la interacción")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Contexto adicional")
    trace_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadatos de la traza")
    cognitive_state: Optional[str] = Field(None, description="Estado cognitivo del estudiante")
    cognitive_intent: Optional[str] = Field(None, description="Intención cognitiva detectada")
    ai_involvement: float = Field(default=0.0, ge=0.0, le=1.0, description="Nivel de involucramiento de IA (0-1)")

    # N4 Decision tracking
    decision_justification: Optional[str] = Field(None, description="Justificación de decisiones tomadas")
    alternatives_considered: List[str] = Field(default_factory=list, description="Alternativas consideradas")
    strategy_type: Optional[str] = Field(None, description="Tipo de estrategia utilizada")

    # FIX 2.4 Cortez8: 6 dimensiones N4 que existen en ORM
    semantic_understanding: Optional[Dict[str, Any]] = Field(None, description="Dimensión semántica N4")
    algorithmic_evolution: Optional[Dict[str, Any]] = Field(None, description="Dimensión algorítmica N4")
    cognitive_reasoning: Optional[Dict[str, Any]] = Field(None, description="Dimensión cognitiva N4")
    interactional_data: Optional[Dict[str, Any]] = Field(None, description="Dimensión interaccional N4")
    ethical_risk_data: Optional[Dict[str, Any]] = Field(None, description="Dimensión ética/riesgo N4")
    process_data: Optional[Dict[str, Any]] = Field(None, description="Dimensión procesual N4")

    # FIX 4.8 Cortez8: Normalizar interaction_type
    @field_validator('interaction_type')
    @classmethod
    def normalize_interaction_type_value(cls, v: str) -> str:
        """Normaliza interaction_type a valores de dominio (lowercase)."""
        return normalize_interaction_type(v)

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "trace_level": "n4_cognitivo",
                "interaction_type": "student_prompt",
                "content": "¿Cómo implemento una cola circular?",
                "context": {"topic": "data_structures"},
                "trace_metadata": {"tokens": 150, "model": "phi3"},
                "cognitive_state": "exploracion",
                "cognitive_intent": "UNDERSTANDING",
                "ai_involvement": 0.3,
                "decision_justification": "Decidí usar arreglo circular por eficiencia",
                "alternatives_considered": ["lista enlazada", "dos pilas"],
                "semantic_understanding": {"conceptos_clave": ["FIFO", "circular buffer"]},
                "cognitive_reasoning": {"razonamiento": "Analicé la complejidad temporal"}
            }
        }


class CognitiveTraceResponse(BaseModel):
    """Response con información de una traza cognitiva"""

    id: str = Field(..., description="ID de la traza")
    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")
    trace_level: str = Field(..., description="Nivel de traza")
    interaction_type: str = Field(..., description="Tipo de interacción")
    content: str = Field(..., description="Contenido")
    context: Dict[str, Any] = Field(default_factory=dict, description="Contexto")
    trace_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos")
    cognitive_state: Optional[str] = Field(None, description="Estado cognitivo")
    cognitive_intent: Optional[str] = Field(None, description="Intención cognitiva")
    decision_justification: Optional[str] = Field(None, description="Justificación de decisiones")
    alternatives_considered: List[str] = Field(default_factory=list, description="Alternativas consideradas")
    strategy_type: Optional[str] = Field(None, description="Tipo de estrategia")
    ai_involvement: float = Field(0.0, description="Involucramiento de IA")
    created_at: datetime = Field(..., description="Timestamp de creación")

    # N4 Cognitive Dimensions (optional, populated for N4 traces)
    semantic_understanding: Optional[Dict[str, Any]] = Field(None, description="Dimensión semántica")
    algorithmic_evolution: Optional[Dict[str, Any]] = Field(None, description="Dimensión algorítmica")
    cognitive_reasoning: Optional[Dict[str, Any]] = Field(None, description="Dimensión cognitiva")
    interactional_data: Optional[Dict[str, Any]] = Field(None, description="Dimensión interaccional")
    ethical_risk_data: Optional[Dict[str, Any]] = Field(None, description="Dimensión ética/riesgo")
    process_data: Optional[Dict[str, Any]] = Field(None, description="Dimensión procesual")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "trace_xyz789",
                "session_id": "session_abc123",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "trace_level": "n4_cognitivo",
                "interaction_type": "QUESTION",
                "content": "¿Cómo implemento una cola circular?",
                "context": {},
                "trace_metadata": {"tokens": 150},
                "cognitive_state": "EXPLORATION",
                "cognitive_intent": "UNDERSTANDING",
                "ai_involvement": 0.3,
                "created_at": "2025-11-18T10:30:00Z"
            }
        }


class CognitiveTraceListResponse(BaseModel):
    """Response con lista de trazas"""

    traces: List[CognitiveTraceResponse] = Field(..., description="Lista de trazas")
    total: int = Field(..., description="Total de trazas")
    session_id: Optional[str] = Field(None, description="ID de sesión si se filtró")


class TraceN4Response(BaseModel):
    """Response detallado de trazabilidad N4 para una interacción"""

    trace_id: str = Field(..., description="ID de la traza")
    session_id: str = Field(..., description="ID de la sesión")
    interaction_id: str = Field(..., description="ID de la interacción")

    # N4 Processing nodes
    nodes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Nodos de procesamiento N1-N4"
    )

    # Aggregated metrics
    total_processing_time_ms: int = Field(0, description="Tiempo total de procesamiento")
    total_tokens: int = Field(0, description="Tokens totales usados")

    # Metadata
    created_at: datetime = Field(..., description="Timestamp de creación")

    class Config:
        json_schema_extra = {
            "example": {
                "trace_id": "trace_xyz789",
                "session_id": "session_abc123",
                "interaction_id": "interaction_456",
                "nodes": [
                    {"id": "n1", "level": "N1", "timestamp": "2025-11-18T10:30:00Z", "data": {}},
                    {"id": "n2", "level": "N2", "timestamp": "2025-11-18T10:30:01Z", "data": {}},
                    {"id": "n3", "level": "N3", "timestamp": "2025-11-18T10:30:02Z", "data": {}},
                    {"id": "n4", "level": "N4", "timestamp": "2025-11-18T10:30:03Z", "data": {}}
                ],
                "total_processing_time_ms": 1500,
                "total_tokens": 500,
                "created_at": "2025-11-18T10:30:00Z"
            }
        }


# FIX 6.4 Cortez8: Schema para TraceSequenceDB
class TraceSequenceResponse(BaseModel):
    """
    Response con información de una secuencia de trazas.

    FIX 6.4 Cortez8: Schema faltante para ORM TraceSequenceDB.
    Representa una secuencia de eventos cognitivos durante una sesión.
    """

    id: str = Field(..., description="ID de la secuencia")
    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")

    # Timing
    start_time: datetime = Field(..., description="Inicio de la secuencia")
    end_time: Optional[datetime] = Field(None, description="Fin de la secuencia")

    # Cognitive path
    reasoning_path: List[str] = Field(default_factory=list, description="Camino de razonamiento seguido")
    strategy_changes: int = Field(0, description="Número de cambios de estrategia")

    # Metrics
    ai_dependency_score: float = Field(0.0, ge=0, le=1, description="Score de dependencia de IA (0-1)")
    cognitive_coherence: Optional[float] = Field(None, ge=0, le=1, description="Coherencia cognitiva (0-1)")

    # Linked traces
    trace_ids: List[str] = Field(default_factory=list, description="IDs de trazas en esta secuencia")

    # Timestamps
    created_at: datetime = Field(..., description="Timestamp de creación")
    updated_at: datetime = Field(..., description="Timestamp de última actualización")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "seq_xyz789",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "start_time": "2025-11-18T10:00:00Z",
                "end_time": "2025-11-18T11:30:00Z",
                "reasoning_path": ["comprension", "planificacion", "implementacion", "validacion"],
                "strategy_changes": 2,
                "ai_dependency_score": 0.35,
                "cognitive_coherence": 0.8,
                "trace_ids": ["trace_001", "trace_002", "trace_003"],
                "created_at": "2025-11-18T10:00:00Z",
                "updated_at": "2025-11-18T11:30:00Z"
            }
        }


class TraceSequenceListResponse(BaseModel):
    """Response con lista de secuencias de trazas"""

    sequences: List[TraceSequenceResponse] = Field(..., description="Lista de secuencias")
    total: int = Field(..., description="Total de secuencias")
    session_id: Optional[str] = Field(None, description="ID de sesión si se filtró")
