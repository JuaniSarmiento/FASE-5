"""
Modelos Pydantic para Trazabilidad N2 (Git)

SPRINT 5 - HU-SYS-008: Integración Git
Captura trazas técnicas de commits, branches, y evolución de código.

Correlación:
- N1 (Superficial): Archivos, entregables finales
- N2 (Técnico): Commits, diffs, branches ← ESTE MÓDULO
- N3 (Interaccional): Prompts, respuestas IA
- N4 (Cognitivo): Estados cognitivos, intenciones, justificaciones
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class GitEventType(str, Enum):
    """
    Tipo de evento Git capturado.

    FIX 2.11 Cortez8: Agregado CHERRY_PICK para consistencia con ORM constraint.
    """
    COMMIT = "commit"
    BRANCH_CREATE = "branch_create"
    BRANCH_DELETE = "branch_delete"
    MERGE = "merge"
    REVERT = "revert"
    TAG = "tag"
    # FIX 2.11 Cortez8: Agregado para consistencia con ORM
    CHERRY_PICK = "cherry_pick"


class CodePattern(str, Enum):
    """Patrones detectados en commits"""
    NORMAL = "normal"  # Commit normal
    COPY_PASTE = "copy_paste"  # Copy-paste masivo detectado
    AI_GENERATED = "ai_generated"  # Código generado por IA sin edición
    REFACTORING = "refactoring"  # Refactoring detectado
    DEBUGGING = "debugging"  # Código de debugging (print, logs)
    COMMENTED_CODE = "commented_code"  # Código comentado masivo


class GitFileChange(BaseModel):
    """Cambio en un archivo individual"""
    file_path: str = Field(description="Ruta del archivo modificado")
    change_type: str = Field(description="added, modified, deleted, renamed")
    lines_added: int = Field(default=0, description="Líneas agregadas")
    lines_deleted: int = Field(default=0, description="Líneas eliminadas")
    is_binary: bool = Field(default=False, description="Si es archivo binario")


class GitTrace(BaseModel):
    """
    Trazabilidad N2 (Nivel Técnico): Captura de eventos Git

    Representa un evento Git (commit, branch, merge) asociado a una sesión
    de aprendizaje, permitiendo reconstruir la evolución técnica del código.
    """
    id: str = Field(description="ID único de la traza Git")
    session_id: str = Field(description="ID de la sesión de aprendizaje asociada")
    student_id: str = Field(description="ID del estudiante")
    activity_id: str = Field(description="ID de la actividad")

    # Git metadata
    event_type: GitEventType = Field(description="Tipo de evento Git")
    commit_hash: str = Field(description="Hash SHA del commit (40 chars)")
    commit_message: str = Field(description="Mensaje del commit")
    author_name: str = Field(description="Nombre del autor del commit")
    author_email: str = Field(description="Email del autor")
    timestamp: datetime = Field(description="Timestamp del commit")
    branch_name: str = Field(description="Nombre del branch")
    parent_commits: List[str] = Field(
        default_factory=list,
        description="Hashes de commits padres (merge tiene 2+)"
    )

    # Code changes
    files_changed: List[GitFileChange] = Field(
        default_factory=list,
        description="Archivos modificados en este commit"
    )
    total_lines_added: int = Field(default=0, description="Total de líneas agregadas")
    total_lines_deleted: int = Field(default=0, description="Total de líneas eliminadas")
    diff: str = Field(default="", description="Diff completo del commit")

    # Analysis
    is_merge: bool = Field(default=False, description="Si es un merge commit")
    is_revert: bool = Field(default=False, description="Si es un revert commit")
    detected_patterns: List[CodePattern] = Field(
        default_factory=list,
        description="Patrones detectados en el commit"
    )
    complexity_delta: Optional[int] = Field(
        None,
        description="Cambio en complejidad ciclomática (+ aumenta, - disminuye)"
    )

    # Correlation with N3/N4
    related_cognitive_traces: List[str] = Field(
        default_factory=list,
        description="IDs de CognitiveTrace cercanos temporalmente (ventana ±30 min)"
    )
    cognitive_state_during_commit: Optional[str] = Field(
        None,
        description="Estado cognitivo inferido durante el commit (de traza N4 más cercana)"
    )
    time_since_last_interaction_minutes: Optional[int] = Field(
        None,
        description="Minutos desde última interacción con IA"
    )

    # Metadata
    repo_path: Optional[str] = Field(None, description="Ruta del repositorio local")
    remote_url: Optional[str] = Field(None, description="URL del repositorio remoto")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "git_trace_001",
                "session_id": "session_123",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "event_type": "commit",
                "commit_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
                "commit_message": "Implementa clase Queue con arreglo circular",
                "author_name": "Juan Pérez",
                "author_email": "juan.perez@university.edu",
                "timestamp": "2025-11-21T10:30:00Z",
                "branch_name": "main",
                "parent_commits": ["parent_hash_123"],
                "files_changed": [
                    {
                        "file_path": "queue.py",
                        "change_type": "modified",
                        "lines_added": 45,
                        "lines_deleted": 12,
                        "is_binary": False
                    }
                ],
                "total_lines_added": 45,
                "total_lines_deleted": 12,
                "diff": "diff --git a/queue.py b/queue.py\\n...",
                "is_merge": False,
                "is_revert": False,
                "detected_patterns": ["normal"],
                "complexity_delta": 3,
                "related_cognitive_traces": ["trace_456", "trace_457"],
                "cognitive_state_during_commit": "IMPLEMENTACION",
                "time_since_last_interaction_minutes": 15
            }
        }


class CodeEvolution(BaseModel):
    """
    Análisis de evolución del código durante una sesión

    Agrega múltiples GitTrace para mostrar cómo evolucionó el código
    a lo largo de la sesión de aprendizaje.
    """
    session_id: str = Field(description="ID de la sesión analizada")
    student_id: str = Field(description="ID del estudiante")
    activity_id: str = Field(description="ID de la actividad")

    # Aggregate metrics
    total_commits: int = Field(description="Total de commits en la sesión")
    total_lines_added: int = Field(description="Total de líneas agregadas")
    total_lines_deleted: int = Field(description="Total de líneas eliminadas")
    net_lines_change: int = Field(description="Cambio neto (added - deleted)")

    # Files
    files_modified: List[str] = Field(
        default_factory=list,
        description="Lista de archivos modificados"
    )
    unique_files_count: int = Field(description="Cantidad de archivos únicos modificados")

    # Patterns
    pattern_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribución de patrones detectados"
    )

    # Complexity
    initial_complexity: Optional[int] = Field(None, description="Complejidad inicial")
    final_complexity: Optional[int] = Field(None, description="Complejidad final")
    complexity_delta: Optional[int] = Field(None, description="Cambio en complejidad")

    # Timeline
    commit_timeline: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Timeline de commits con timestamps"
    )
    commit_frequency: Dict[str, int] = Field(
        default_factory=dict,
        description="Frecuencia de commits por hora"
    )

    # Correlation with cognitive states
    commits_by_cognitive_state: Dict[str, int] = Field(
        default_factory=dict,
        description="Commits agrupados por estado cognitivo"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "student_id": "student_001",
                "activity_id": "prog2_tp1_colas",
                "total_commits": 15,
                "total_lines_added": 342,
                "total_lines_deleted": 87,
                "net_lines_change": 255,
                "files_modified": ["queue.py", "test_queue.py", "main.py"],
                "unique_files_count": 3,
                "pattern_distribution": {
                    "normal": 12,
                    "ai_generated": 2,
                    "debugging": 1
                },
                "commits_by_cognitive_state": {
                    "PLANIFICACION": 2,
                    "IMPLEMENTACION": 10,
                    "DEPURACION": 3
                }
            }
        }


class GitN2CorrelationResult(BaseModel):
    """
    Resultado de correlación entre N2 (Git) y N3/N4 (Cognición)

    Permite analizar la relación temporal entre eventos técnicos (commits)
    y eventos cognitivos (consultas a IA, estados mentales).
    """
    session_id: str = Field(description="ID de la sesión analizada")

    correlations: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de correlaciones entre commits y trazas cognitivas"
    )

    # Aggregate insights
    avg_time_between_commit_and_interaction: Optional[float] = Field(
        None,
        description="Promedio de minutos entre commit y consulta a IA"
    )

    commits_without_nearby_interactions: int = Field(
        default=0,
        description="Commits sin interacciones cercanas (posible copy-paste o IA externa)"
    )

    interaction_to_commit_ratio: Optional[float] = Field(
        None,
        description="Ratio de interacciones con IA por commit (> 1 = consulta mucho)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "session_123",
                "correlations": [
                    {
                        "commit_hash": "abc123",
                        "commit_timestamp": "2025-11-21T10:30:00Z",
                        "commit_message": "Implementa método enqueue",
                        "cognitive_traces_nearby": [
                            {
                                "trace_id": "trace_456",
                                "cognitive_state": "IMPLEMENTACION",
                                "timestamp": "2025-11-21T10:28:00Z",
                                "time_diff_minutes": 2,
                                "interaction_type": "STUDENT_PROMPT",
                                "content_preview": "¿Cómo manejo el overflow en cola circular?"
                            }
                        ]
                    }
                ],
                "avg_time_between_commit_and_interaction": 8.5,
                "commits_without_nearby_interactions": 2,
                "interaction_to_commit_ratio": 1.3
            }
        }
