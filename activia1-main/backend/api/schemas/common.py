"""
Schemas comunes para la API REST
FIX 7.4 Cortez8: Agregados type aliases para IDs
"""
import re
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field


# FIX 7.4 Cortez8: Type aliases for common ID patterns
# Usage: from .common import SessionId, StudentId
# Note: These are documentation hints, not runtime validators
SessionId = str  # UUID format: 550e8400-e29b-41d4-a716-446655440000
StudentId = str  # max 100 chars
ActivityId = str  # max 100 chars
UserId = str  # UUID format, max 36 chars
TraceId = str  # UUID format
RiskId = str  # UUID format
EvaluationId = str  # UUID format


DataT = TypeVar("DataT")

# UUID v4 validation pattern (8-4-4-4-12 hex digits)
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)


def validate_uuid_format(value: str, field_name: str = "session_id") -> str:
    """
    Validates that a string has UUID format.
    Prevents SQL injection and type errors.

    Args:
        value: The string to validate
        field_name: Name of the field for error messages

    Returns:
        Normalized lowercase UUID string

    Raises:
        ValueError: If the value is not a valid UUID format
    """
    if not value or not isinstance(value, str):
        raise ValueError(f"{field_name} must be a non-empty string")

    if not UUID_PATTERN.match(value):
        raise ValueError(
            f"Invalid {field_name} format. Expected UUID format "
            f"(e.g., '550e8400-e29b-41d4-a716-446655440000'), got: {value[:50]}"
        )
    return value.lower()  # Normalize to lowercase


class APIResponse(BaseModel, Generic[DataT]):
    """Respuesta estándar de la API"""

    success: bool = Field(..., description="Indica si la operación fue exitosa")
    data: Optional[DataT] = Field(None, description="Datos de la respuesta")
    message: Optional[str] = Field(None, description="Mensaje descriptivo")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de la respuesta")


class ErrorDetail(BaseModel):
    """Detalle de error"""

    error_code: str = Field(..., description="Código de error")
    message: str = Field(..., description="Mensaje de error")
    field: Optional[str] = Field(None, description="Campo que causó el error")
    extra: Optional[Dict[str, Any]] = Field(None, description="Información adicional")


class ErrorResponse(BaseModel):
    """Respuesta de error estándar"""

    success: bool = Field(False, description="Siempre False para errores")
    error: ErrorDetail = Field(..., description="Detalle del error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp del error")


class PaginationParams(BaseModel):
    """Parámetros de paginación"""

    page: int = Field(1, ge=1, description="Número de página (inicia en 1)")
    page_size: int = Field(20, ge=1, le=100, description="Elementos por página (máximo 100)")

    @property
    def offset(self) -> int:
        """Calcula el offset para la consulta"""
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Respuesta paginada"""

    success: bool = Field(True, description="Indica si la operación fue exitosa")
    data: List[DataT] = Field(..., description="Lista de elementos")
    pagination: "PaginationMeta" = Field(..., description="Metadatos de paginación")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp de la respuesta")


class PaginationMeta(BaseModel):
    """Metadatos de paginación"""

    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Elementos por página")
    total_items: int = Field(..., description="Total de elementos")
    total_pages: int = Field(..., description="Total de páginas")
    has_next: bool = Field(..., description="Indica si hay página siguiente")
    has_prev: bool = Field(..., description="Indica si hay página anterior")


class HealthStatus(BaseModel):
    """Estado de salud del servicio"""

    status: str = Field(..., description="Estado del servicio: 'healthy', 'degraded', 'unhealthy'")
    version: str = Field(..., description="Versión de la aplicación")
    database: str = Field(..., description="Estado de la base de datos: 'connected', 'disconnected'")
    agents: Dict[str, str] = Field(..., description="Estado de cada agente")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp del check")