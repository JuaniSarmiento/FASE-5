"""
Schemas para trazas de Git (GitTraceDB)
FIX 3.1: Schemas faltantes para ORM models
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class GitFileChange(BaseModel):
    """Cambio en un archivo"""

    filename: str = Field(..., description="Nombre del archivo")
    status: str = Field(..., description="Estado: added, modified, deleted")
    additions: int = Field(0, description="Líneas añadidas")
    deletions: int = Field(0, description="Líneas eliminadas")
    patch: Optional[str] = Field(None, description="Diff del archivo")


class GitTraceCreate(BaseModel):
    """Request para crear una nueva traza de Git"""

    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")

    # Git data
    commit_hash: str = Field(..., description="Hash del commit")
    commit_message: str = Field(..., description="Mensaje del commit")
    branch: str = Field("main", description="Rama del commit")
    author: str = Field(..., description="Autor del commit")
    timestamp: datetime = Field(..., description="Timestamp del commit")

    # File changes
    files_changed: List[GitFileChange] = Field(default_factory=list, description="Archivos cambiados")

    # Analysis
    code_patterns: Optional[List[str]] = Field(None, description="Patrones de código detectados")
    quality_score: Optional[float] = Field(None, ge=0, le=1, description="Score de calidad")
    complexity_delta: Optional[float] = Field(None, description="Cambio en complejidad")

    # Metadata
    git_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadatos adicionales")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "commit_hash": "abc123def456",
                "commit_message": "Implementar método enqueue",
                "branch": "feature/queue",
                "author": "student_001",
                "timestamp": "2025-11-18T10:30:00Z",
                "files_changed": [
                    {"filename": "queue.py", "status": "modified", "additions": 15, "deletions": 2}
                ],
                "code_patterns": ["loop", "condition"],
                "quality_score": 0.8,
                "complexity_delta": 0.1
            }
        }


class GitTraceResponse(BaseModel):
    """Response con información de una traza de Git"""

    id: str = Field(..., description="ID de la traza")
    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")
    activity_id: str = Field(..., description="ID de la actividad")

    # Git data
    commit_hash: str = Field(..., description="Hash del commit")
    commit_message: str = Field(..., description="Mensaje del commit")
    branch: str = Field(..., description="Rama")
    author: str = Field(..., description="Autor")
    timestamp: datetime = Field(..., description="Timestamp del commit")

    # File changes
    files_changed: List[GitFileChange] = Field(default_factory=list, description="Archivos cambiados")
    total_additions: int = Field(0, description="Total líneas añadidas")
    total_deletions: int = Field(0, description="Total líneas eliminadas")

    # Analysis
    code_patterns: List[str] = Field(default_factory=list, description="Patrones detectados")
    quality_score: Optional[float] = Field(None, description="Score de calidad")
    complexity_delta: Optional[float] = Field(None, description="Cambio en complejidad")

    # Metadata
    git_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadatos")
    created_at: datetime = Field(..., description="Timestamp de creación en sistema")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "git_xyz789",
                "session_id": "session_abc123",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "commit_hash": "abc123def456",
                "commit_message": "Implementar método enqueue",
                "branch": "feature/queue",
                "author": "student_001",
                "timestamp": "2025-11-18T10:30:00Z",
                "files_changed": [],
                "total_additions": 15,
                "total_deletions": 2,
                "code_patterns": ["loop"],
                "quality_score": 0.8,
                "complexity_delta": 0.1,
                "git_metadata": {},
                "created_at": "2025-11-18T10:35:00Z"
            }
        }


class GitTraceListResponse(BaseModel):
    """Response con lista de trazas de Git"""

    traces: List[GitTraceResponse] = Field(..., description="Lista de trazas")
    total: int = Field(..., description="Total de trazas")
    session_id: Optional[str] = Field(None, description="ID de sesión si se filtró")


class GitEvolutionResponse(BaseModel):
    """Response con evolución del código a través de commits"""

    session_id: str = Field(..., description="ID de la sesión")
    student_id: str = Field(..., description="ID del estudiante")

    # Timeline
    commits: List[GitTraceResponse] = Field(..., description="Commits en orden cronológico")
    total_commits: int = Field(0, description="Total de commits")

    # Aggregated metrics
    total_additions: int = Field(0, description="Total líneas añadidas")
    total_deletions: int = Field(0, description="Total líneas eliminadas")
    files_touched: List[str] = Field(default_factory=list, description="Archivos tocados")
    average_quality: Optional[float] = Field(None, description="Calidad promedio")

    # Evolution analysis
    complexity_trend: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tendencia de complejidad por commit"
    )
    pattern_frequency: Dict[str, int] = Field(
        default_factory=dict,
        description="Frecuencia de patrones de código"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_abc123",
                "student_id": "student_001",
                "commits": [],
                "total_commits": 5,
                "total_additions": 150,
                "total_deletions": 30,
                "files_touched": ["queue.py", "test_queue.py"],
                "average_quality": 0.75,
                "complexity_trend": [
                    {"commit": 1, "complexity": 0.3},
                    {"commit": 2, "complexity": 0.4},
                    {"commit": 3, "complexity": 0.35}
                ],
                "pattern_frequency": {"loop": 5, "condition": 8, "function_call": 12}
            }
        }
