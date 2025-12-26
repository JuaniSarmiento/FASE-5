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


# =============================================================================
# SCHEMAS PARA EJERCICIOS PostgreSQL (NUEVA MIGRACIÓN)
# =============================================================================

from pydantic import validator


class SubjectBase(BaseModel):
    """Base schema for Subject"""
    code: str = Field(..., min_length=1, max_length=50, description="Subject code (e.g., 'PYTHON', 'JAVA')")
    name: str = Field(..., min_length=1, max_length=100, description="Subject name")
    description: Optional[str] = Field(None, description="Subject description")
    language: str = Field(..., pattern="^(python|java)$", description="Programming language")
    total_units: int = Field(default=0, ge=0, description="Total number of units")
    is_active: bool = Field(default=True, description="Whether subject is active")


class SubjectCreate(SubjectBase):
    """Schema for creating a subject"""
    pass


class SubjectUpdate(BaseModel):
    """Schema for updating a subject"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    language: Optional[str] = Field(None, pattern="^(python|java)$")
    total_units: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class SubjectRead(SubjectBase):
    """Schema for reading a subject"""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExerciseHintBase(BaseModel):
    """Base schema for Exercise Hint"""
    hint_number: int = Field(..., ge=1, description="Hint number (1, 2, 3, 4)")
    title: Optional[str] = Field(None, max_length=200, description="Hint title")
    content: str = Field(..., min_length=1, description="Hint content")
    penalty_points: int = Field(default=0, ge=0, description="Penalty points for using this hint")


class ExerciseHintCreate(ExerciseHintBase):
    """Schema for creating a hint"""
    pass


class ExerciseHintRead(ExerciseHintBase):
    """Schema for reading a hint"""
    id: str
    exercise_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseTestBase(BaseModel):
    """Base schema for Exercise Test"""
    test_number: int = Field(..., ge=1, description="Test number")
    description: Optional[str] = Field(None, description="Test description")
    input: str = Field(..., min_length=1, description="Test input (e.g., 'validar_nota(85)')")
    expected: str = Field(..., min_length=1, description="Expected output (e.g., 'True')")
    is_hidden: bool = Field(default=False, description="Whether test is hidden from student")
    timeout_seconds: int = Field(default=5, ge=1, description="Timeout in seconds")


class ExerciseTestCreate(ExerciseTestBase):
    """Schema for creating a test"""
    pass


class ExerciseTestRead(ExerciseTestBase):
    """Schema for reading a test"""
    id: str
    exercise_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseTestReadPublic(BaseModel):
    """Schema for reading a test (student view - no expected for hidden tests)"""
    id: str
    test_number: int
    description: Optional[str]
    input: str
    expected: Optional[str] = Field(None, description="Only shown for visible tests")
    is_hidden: bool
    timeout_seconds: int

    class Config:
        from_attributes = True


class ExerciseDBBase(BaseModel):
    """Base schema for Exercise from PostgreSQL"""
    title: str = Field(..., min_length=1, max_length=200, description="Exercise title")
    description: Optional[str] = Field(None, description="Exercise description")
    difficulty: str = Field(..., pattern="^(Easy|Medium|Hard)$", description="Difficulty level")
    time_min: int = Field(..., ge=1, description="Estimated time in minutes")
    unit: Optional[int] = Field(None, ge=1, le=10, description="Unit number (1-10)")
    language: str = Field(..., pattern="^(python|java)$", description="Programming language")

    mission_markdown: str = Field(..., min_length=1, description="Exercise mission/consigna in markdown")
    story_markdown: Optional[str] = Field(None, description="Exercise story/context in markdown")
    constraints: List[str] = Field(default_factory=list, description="Exercise constraints/requirements")

    starter_code: str = Field(..., min_length=1, description="Starter code template")
    solution_code: Optional[str] = Field(None, description="Reference solution (NOT sent to frontend)")

    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    learning_objectives: List[str] = Field(default_factory=list, description="Learning objectives")
    cognitive_level: Optional[str] = Field(None, description="Cognitive level (Bloom's taxonomy)")

    max_score: int = Field(default=100, ge=1, le=100, description="Maximum score for this exercise (FASE 1.5)")

    version: int = Field(default=1, ge=1, description="Exercise version")
    is_active: bool = Field(default=True, description="Whether exercise is active")


class ExerciseDBCreate(ExerciseDBBase):
    """Schema for creating an exercise"""
    subject_code: str = Field(..., min_length=1, max_length=50, description="Subject code")


class ExerciseDBUpdate(BaseModel):
    """Schema for updating an exercise"""
    subject_code: Optional[str] = Field(None, min_length=1, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    difficulty: Optional[str] = Field(None, pattern="^(Easy|Medium|Hard)$")
    time_min: Optional[int] = Field(None, ge=1)
    unit: Optional[int] = Field(None, ge=1, le=10)
    language: Optional[str] = Field(None, pattern="^(python|java)$")
    mission_markdown: Optional[str] = Field(None, min_length=1)
    story_markdown: Optional[str] = None
    constraints: Optional[List[str]] = None
    starter_code: Optional[str] = Field(None, min_length=1)
    solution_code: Optional[str] = None
    tags: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    cognitive_level: Optional[str] = None
    max_score: Optional[int] = Field(None, ge=1, le=100)
    version: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class ExerciseDBRead(ExerciseDBBase):
    """Schema for reading an exercise (full details, including solution for admins)"""
    id: str
    subject_code: str
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExerciseDBReadStudent(BaseModel):
    """Schema for reading an exercise (student view - NO solution_code)"""
    id: str
    subject_code: str
    title: str
    description: Optional[str]
    difficulty: str
    time_min: int
    unit: Optional[int]
    language: str
    mission_markdown: str
    story_markdown: Optional[str]
    constraints: List[str]
    starter_code: str
    # solution_code: EXCLUDED for students
    tags: List[str]
    learning_objectives: List[str]
    cognitive_level: Optional[str]
    max_score: int
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExerciseDBListItem(BaseModel):
    """Schema for exercise list (minimal info for browsing)"""
    id: str
    subject_code: str
    title: str
    description: Optional[str]
    difficulty: str
    time_min: int
    unit: Optional[int]
    tags: List[str]
    is_active: bool

    class Config:
        from_attributes = True


class ExerciseDBWithDetails(ExerciseDBReadStudent):
    """Schema for exercise with hints, tests, and rubric (student view)"""
    hints: List[ExerciseHintRead] = []
    tests: List[ExerciseTestReadPublic] = []
    rubric: Optional['ExerciseRubricRead'] = Field(None, description="Rubric criteria (FASE 1.5)")

    class Config:
        from_attributes = True


class ExerciseAttemptBase(BaseModel):
    """Base schema for Exercise Attempt"""
    exercise_id: str = Field(..., description="Exercise ID")
    student_id: str = Field(..., description="Student ID")
    session_id: Optional[str] = Field(None, description="Session ID (optional)")
    submitted_code: str = Field(..., min_length=1, description="Code submitted by student")

    tests_passed: int = Field(default=0, ge=0, description="Number of tests passed")
    tests_total: int = Field(default=0, ge=0, description="Total number of tests")
    score: Optional[float] = Field(None, ge=0, le=10, description="Score (0-10 scale)")
    status: str = Field(..., pattern="^(PASS|FAIL|ERROR|TIMEOUT)$", description="Attempt status")

    execution_time_ms: Optional[int] = Field(None, ge=0, description="Execution time in milliseconds")
    stdout: Optional[str] = Field(None, description="Standard output")
    stderr: Optional[str] = Field(None, description="Standard error")

    ai_feedback_summary: Optional[str] = Field(None, description="AI feedback summary")
    ai_feedback_detailed: Optional[str] = Field(None, description="AI feedback detailed")
    ai_suggestions: List[str] = Field(default_factory=list, description="AI suggestions")

    hints_used: int = Field(default=0, ge=0, description="Number of hints used")
    penalty_applied: int = Field(default=0, ge=0, description="Penalty points applied")
    attempt_number: int = Field(default=1, ge=1, description="Attempt number")

    @validator('tests_passed')
    def validate_tests_passed(cls, v, values):
        """Ensure tests_passed <= tests_total"""
        if 'tests_total' in values and v > values['tests_total']:
            raise ValueError('tests_passed cannot exceed tests_total')
        return v


class ExerciseAttemptCreate(ExerciseAttemptBase):
    """Schema for creating an attempt"""
    pass


class ExerciseAttemptRead(ExerciseAttemptBase):
    """Schema for reading an attempt"""
    id: str
    submitted_at: datetime

    class Config:
        from_attributes = True


class ExerciseAttemptSummary(BaseModel):
    """Schema for attempt summary (for analytics)"""
    id: str
    exercise_id: str
    student_id: str
    status: str
    score: Optional[float]
    tests_passed: int
    tests_total: int
    hints_used: int
    attempt_number: int
    submitted_at: datetime

    class Config:
        from_attributes = True


class SubjectWithExercises(SubjectRead):
    """Schema for subject with its exercises"""
    exercises: List[ExerciseDBListItem] = []

    class Config:
        from_attributes = True


# =============================================================================
# SCHEMAS PARA RÚBRICAS (FASE 1.5)
# =============================================================================

class RubricLevelBase(BaseModel):
    """Base schema for Rubric Level"""
    level_name: str = Field(..., pattern="^(Excelente|Bueno|Regular|Insuficiente)$", description="Level name")
    description: str = Field(..., min_length=1, description="What student must achieve for this level")
    min_score: float = Field(..., ge=0, le=10, description="Minimum score for this level (0-10)")
    max_score: float = Field(..., ge=0, le=10, description="Maximum score for this level (0-10)")
    points: int = Field(..., ge=0, le=100, description="Points awarded for this level (0-100)")

    @validator('max_score')
    def validate_score_order(cls, v, values):
        """Ensure min_score < max_score"""
        if 'min_score' in values and v <= values['min_score']:
            raise ValueError('max_score must be greater than min_score')
        return v


class RubricLevelCreate(RubricLevelBase):
    """Schema for creating a rubric level"""
    pass


class RubricLevelRead(RubricLevelBase):
    """Schema for reading a rubric level"""
    id: str
    criterion_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RubricCriterionBase(BaseModel):
    """Base schema for Rubric Criterion"""
    criterion_name: str = Field(..., min_length=1, max_length=100, description="Criterion name (e.g., 'Funcionalidad', 'Calidad de código')")
    description: Optional[str] = Field(None, description="Detailed description of the criterion")
    weight: float = Field(..., ge=0, le=1, description="Weight of this criterion (0-1, sum must be 1.0)")
    display_order: int = Field(..., ge=1, description="Display order (1, 2, 3...)")


class RubricCriterionCreate(RubricCriterionBase):
    """Schema for creating a rubric criterion"""
    levels: List[RubricLevelCreate] = Field(..., min_items=4, max_items=4, description="Must have exactly 4 levels")

    @validator('levels')
    def validate_levels(cls, v):
        """Ensure we have exactly 4 levels with correct names"""
        level_names = {level.level_name for level in v}
        expected_names = {'Excelente', 'Bueno', 'Regular', 'Insuficiente'}
        if level_names != expected_names:
            raise ValueError(f'Levels must include exactly: {expected_names}')
        return v


class RubricCriterionRead(RubricCriterionBase):
    """Schema for reading a rubric criterion"""
    id: str
    exercise_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RubricCriterionWithLevels(RubricCriterionRead):
    """Schema for rubric criterion with its levels"""
    levels: List[RubricLevelRead] = []

    class Config:
        from_attributes = True


class ExerciseRubricCreate(BaseModel):
    """Schema for creating complete rubric for an exercise"""
    criteria: List[RubricCriterionCreate] = Field(..., min_items=1, description="List of criteria with levels")

    @validator('criteria')
    def validate_weights_sum(cls, v):
        """Ensure weights sum to 1.0 (with tolerance for floating point)"""
        total_weight = sum(criterion.weight for criterion in v)
        if not (0.99 <= total_weight <= 1.01):  # Tolerance of 0.01
            raise ValueError(f'Criterion weights must sum to 1.0, got {total_weight}')
        return v


class ExerciseRubricRead(BaseModel):
    """Schema for reading complete rubric"""
    exercise_id: str
    criteria: List[RubricCriterionWithLevels] = []

    class Config:
        from_attributes = True


class RubricEvaluationCriterionResult(BaseModel):
    """Schema for individual criterion evaluation result"""
    criterion_name: str
    level_achieved: str = Field(..., pattern="^(Excelente|Bueno|Regular|Insuficiente)$")
    score: float = Field(..., ge=0, le=10, description="Score achieved (0-10)")
    points: int = Field(..., ge=0, le=100, description="Points awarded")
    feedback: str = Field(..., description="AI feedback for this criterion")


class RubricEvaluationResult(BaseModel):
    """Schema for complete rubric evaluation result"""
    criteria: List[RubricEvaluationCriterionResult]
    total_score_rubric: float = Field(..., ge=0, le=100, description="Total score from rubric before penalties")
    penalty_from_hints: int = Field(..., ge=0, description="Penalty points from hints used")
    final_score: float = Field(..., ge=0, le=100, description="Final score after penalties")

    @validator('final_score')
    def validate_final_score(cls, v, values):
        """Ensure final_score = total_score_rubric - penalty_from_hints (clamped to 0)"""
        if 'total_score_rubric' in values and 'penalty_from_hints' in values:
            expected = max(0, values['total_score_rubric'] - values['penalty_from_hints'])
            if abs(v - expected) > 0.01:  # Tolerance for floating point
                raise ValueError(f'final_score must be total_score_rubric - penalty_from_hints, got {v}, expected {expected}')
        return v
