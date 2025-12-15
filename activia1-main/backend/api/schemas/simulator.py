"""
Schemas Pydantic para simuladores profesionales (S-IA-X)

Sprint 3 - HU-EST-009, HU-SYS-006
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List

# Import SimulatorType from centralized enums to avoid duplication
from .enums import SimulatorType


class SimulatorInteractionRequest(BaseModel):
    """Request para interactuar con un simulador"""
    session_id: str = Field(..., description="ID de la sesión activa")
    simulator_type: SimulatorType = Field(..., description="Tipo de simulador")
    prompt: str = Field(..., min_length=10, max_length=5000, description="Mensaje del estudiante al simulador")

    context: Optional[Dict[str, Any]] = Field(default=None, description="Contexto adicional de la interacción")

    @field_validator('simulator_type', mode='before')
    @classmethod
    def normalize_simulator_type(cls, v):
        """Normalize simulator_type to lowercase before enum validation"""
        if isinstance(v, str):
            return v.lower()
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "session_id": "session_abc123",
                "simulator_type": "product_owner",
                "prompt": "Propongo implementar una cola circular con arreglo para optimizar el uso de memoria. Los criterios de aceptación son: O(1) para enqueue/dequeue, capacidad fija de 100 elementos, y manejo de overflow.",
                "context": {
                    "activity": "prog2_tp1_colas",
                    "iteration": 1
                }
            }]
        }
    }


class SimulatorInteractionResponse(BaseModel):
    """Response de interacción con simulador"""
    interaction_id: str = Field(..., description="ID único de la interacción")
    simulator_type: SimulatorType = Field(..., description="Tipo de simulador")
    response: str = Field(..., description="Respuesta del simulador")
    role: str = Field(..., description="Rol del simulador (product_owner, scrum_master, etc.)")
    expects: List[str] = Field(default_factory=list, description="Qué espera el simulador en la próxima respuesta")
    competencies_evaluated: List[str] = Field(default_factory=list, description="Competencias evaluadas")
    trace_id_input: str = Field(..., description="ID de la traza N4 del input")
    trace_id_output: str = Field(..., description="ID de la traza N4 del output")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata adicional")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "interaction_id": "trace_input_123_trace_output_456",
                "simulator_type": "product_owner",
                "response": "Como Product Owner, necesito que me aclares: ¿Cuál es el impacto de fijar la capacidad en 100? ¿Qué alternativas consideraste para el manejo de overflow?",
                "role": "product_owner",
                "expects": ["justificacion_tecnica", "analisis_alternativas"],
                "competencies_evaluated": ["comunicacion_tecnica", "analisis_requisitos"],
                "trace_id_input": "trace_input_123",
                "trace_id_output": "trace_output_456",
                "metadata": {
                    "session_id": "session_abc123"
                }
            }]
        }
    }


class SimulatorInfoResponse(BaseModel):
    """Información de un simulador profesional"""
    type: SimulatorType = Field(..., description="Tipo de simulador")
    name: str = Field(..., description="Nombre descriptivo del simulador")
    description: str = Field(..., description="Descripción del rol y objetivos")
    competencies: List[str] = Field(..., description="Competencias que evalúa")
    status: str = Field(..., description="Estado: active, development, deprecated")
    example_questions: Optional[List[str]] = Field(default=None, description="Preguntas ejemplo que hace el simulador")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "type": "product_owner",
                "name": "Product Owner (PO-IA)",
                "description": "Simula un Product Owner que revisa requisitos y prioriza backlog",
                "competencies": ["comunicacion_tecnica", "analisis_requisitos", "priorizacion"],
                "status": "active",
                "example_questions": [
                    "¿Cuáles son los criterios de aceptación?",
                    "¿Cómo agrega valor al usuario final?"
                ]
            }]
        }
    }