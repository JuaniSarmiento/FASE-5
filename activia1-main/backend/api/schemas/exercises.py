"""
Schemas para el sistema de ejercicios de programación
Incluye tanto ejercicios de BD como ejercicios de JSON
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# =============================================================================
# SCHEMAS PARA EJERCICIOS JSON (Sistema nuevo con Alex)
# =============================================================================

class ExerciseMetaSchema(BaseModel):
    """Metadatos del ejercicio"""
    title: str
    difficulty: str  # 'Easy', 'Medium', 'Hard'
    estimated_time_min: Optional[int] = None
    estimated_time_minutes: Optional[int] = None  # Compatibilidad
    points: Optional[int] = 0
    tags: List[str]
    learning_objectives: Optional[List[str]] = []


class ExerciseUIConfigSchema(BaseModel):
    """Configuración de UI"""
    editor_language: str
    editor_theme: Optional[str] = "vs-dark"
    show_line_numbers: Optional[bool] = True
    enable_autocomplete: Optional[bool] = True
    show_hints_button: Optional[bool] = True
    read_only_lines: Optional[List[int]] = []
    placeholder_text: Optional[str] = ""


class ExerciseContentSchema(BaseModel):
    """Contenido del ejercicio"""
    story_markdown: str
    mission_markdown: str
    hints: Optional[List[str]] = []
    constraints: Optional[List[str]] = []  # Algunos usan constraints en vez de success_criteria
    success_criteria: Optional[List[str]] = []


class HiddenTestSchema(BaseModel):
    """Test oculto para validación"""
    id: Optional[str] = None
    description: Optional[str] = None
    input: Optional[str] = ""  # Algunos usan 'input' en vez de 'input_data'
    input_data: Optional[Any] = None
    expected: Optional[str] = None  # Algunos usan 'expected' en vez de 'expected_output'
    expected_output: Optional[Any] = None
    assertion_code: Optional[str] = None


class ExerciseJSONSchema(BaseModel):
    """Ejercicio completo del sistema JSON"""
    id: str
    meta: ExerciseMetaSchema
    ui_config: ExerciseUIConfigSchema
    content: ExerciseContentSchema
    starter_code: str
    hidden_tests: List[HiddenTestSchema]


class ExerciseListItemSchema(BaseModel):
    """Item de ejercicio para listado"""
    id: str
    title: str
    difficulty: str
    estimated_time_minutes: int
    points: int
    tags: List[str]
    is_completed: bool = False


# =============================================================================
# SCHEMAS PARA EVALUACIÓN CON ALEX
# =============================================================================

class DimensionScoreSchema(BaseModel):
    """Score de una dimensión de evaluación"""
    score: float = Field(..., ge=0, le=10, description="Score 0-10")
    comment: str


class CodeAnnotationSchema(BaseModel):
    """Anotación en una línea de código"""
    line_number: int
    severity: str  # 'info', 'warning', 'error'
    message: str


class EvaluationSchema(BaseModel):
    """Resultado de la evaluación general"""
    score: float = Field(..., ge=0, le=100)
    status: str  # 'PASS', 'PARTIAL', 'FAIL'
    title: str
    summary_markdown: str
    toast_type: str  # 'success', 'warning', 'error'
    toast_message: str


class DimensionsSchema(BaseModel):
    """Scores por dimensión"""
    functionality: DimensionScoreSchema
    code_quality: DimensionScoreSchema
    robustness: DimensionScoreSchema


class CodeReviewSchema(BaseModel):
    """Revisión de código línea por línea"""
    highlighted_lines: List[CodeAnnotationSchema]
    refactoring_suggestion: Optional[str] = None


class GamificationSchema(BaseModel):
    """Datos de gamificación"""
    xp_earned: int
    achievements_unlocked: List[str]


class EvaluationResultSchema(BaseModel):
    """Respuesta completa de evaluación"""
    evaluation: EvaluationSchema
    dimensions: DimensionsSchema
    code_review: CodeReviewSchema
    gamification: GamificationSchema
    metadata: Optional[Dict[str, Any]] = None


# =============================================================================
# SCHEMAS PARA SUBMISSIONS
# =============================================================================

class CodeSubmissionRequest(BaseModel):
    """Request para enviar código"""
    student_code: str


class SandboxResultSchema(BaseModel):
    """Resultado de ejecución en sandbox"""
    exit_code: int
    stdout: str
    stderr: str
    execution_time_ms: int
    tests_passed: int
    tests_total: int


class SubmissionResponseSchema(BaseModel):
    """Respuesta de submission"""
    submission_id: str
    exercise_id: str
    user_id: str
    submitted_at: datetime
    sandbox_result: SandboxResultSchema
    evaluation: EvaluationResultSchema


# =============================================================================
# SCHEMAS PARA EJERCICIOS BD (Sistema legacy)
# =============================================================================

class ExerciseResponse(BaseModel):
    """Ejercicio del sistema legacy (BD)"""
    id: str
    title: str
    description: str
    difficulty_level: int
    starter_code: Optional[str]
    hints: Optional[List[str]]
    max_score: float
    time_limit_seconds: int


class CodeSubmission(BaseModel):
    """Submission del sistema legacy"""
    exercise_id: str
    code: str


class SubmissionResult(BaseModel):
    """Resultado del sistema legacy"""
    id: str
    passed_tests: int
    total_tests: int
    is_correct: bool
    execution_time_ms: int
    ai_score: Optional[float]
    ai_feedback: Optional[str]
    code_quality_score: Optional[float]
    readability_score: Optional[float]
    efficiency_score: Optional[float]
    best_practices_score: Optional[float]
    test_results: List[Dict[str, Any]]


# =============================================================================
# SCHEMAS PARA ESTADÍSTICAS
# =============================================================================

class ExerciseStatsSchema(BaseModel):
    """Estadísticas de ejercicios"""
    total_exercises: int
    by_difficulty: Dict[str, int]
    total_time_hours: float
    unique_tags: int


class UserProgressSchema(BaseModel):
    """Progreso del usuario"""
    total_submissions: int
    completed_exercises: int
    average_score: float
    total_xp: int
    achievements: List[str]
    exercises_by_difficulty: Dict[str, int]
