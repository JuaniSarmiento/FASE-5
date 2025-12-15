from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import subprocess
import tempfile
import os
import time
import json
import logging

from backend.database.config import get_db
from backend.models.exercise import Exercise, UserExerciseSubmission
from backend.api.routers.auth_new import get_current_user
# FIX Cortez25: Use UserDB from database.models to avoid duplicate table definition
from backend.database.models import UserDB as User
from backend.llm.ollama_provider import OllamaProvider
# FIX 1.3 Cortez3: Import rate limiter for code execution endpoint
from backend.api.middleware.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/exercises", tags=["Code Exercises"])


# Schemas
class ExerciseResponse(BaseModel):
    id: str
    title: str
    description: str
    difficulty_level: int
    starter_code: Optional[str]
    hints: Optional[List[str]]
    max_score: float
    time_limit_seconds: int


class CodeSubmission(BaseModel):
    exercise_id: str
    code: str


class SubmissionResult(BaseModel):
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


def execute_python_code(code: str, test_input: str, timeout_seconds: int = 5) -> tuple[str, str, int]:
    """
    Ejecuta código Python de forma segura con restricciones de sandbox.

    SECURITY MEASURES:
    1. Bloquea imports peligrosos (os, subprocess, sys, etc.)
    2. Bloquea funciones peligrosas (exec, eval, open, etc.)
    3. Limita tiempo de ejecución
    4. Limita memoria (si es posible)
    5. Ejecuta en proceso separado sin acceso a red

    Returns:
        tuple: (stdout, stderr, execution_time_ms)
    """
    # ==========================================================================
    # SECURITY: Validate code before execution
    # ==========================================================================
    DANGEROUS_IMPORTS = [
        'os', 'subprocess', 'sys', 'shutil', 'pathlib',
        'socket', 'requests', 'urllib', 'http',
        'multiprocessing', 'threading', 'asyncio',
        'pickle', 'marshal', 'shelve',
        'ctypes', 'cffi', 'importlib',
        'builtins', '__builtins__',
        'code', 'codeop', 'compile',
    ]

    DANGEROUS_PATTERNS = [
        '__import__', 'exec(', 'eval(', 'compile(',
        'open(', 'file(', 'input(',
        'globals(', 'locals(', 'vars(',
        'getattr(', 'setattr(', 'delattr(',
        '__class__', '__bases__', '__subclasses__',
        '__mro__', '__code__', '__globals__',
        'breakpoint(', 'help(',
    ]

    # Check for dangerous imports
    code_lower = code.lower()
    for dangerous_import in DANGEROUS_IMPORTS:
        patterns = [
            f'import {dangerous_import}',
            f'from {dangerous_import}',
            f'__import__("{dangerous_import}"',
            f"__import__('{dangerous_import}'",
        ]
        for pattern in patterns:
            if pattern.lower() in code_lower:
                return "", f"Error de seguridad: Import '{dangerous_import}' no permitido", 0

    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in code_lower:
            return "", f"Error de seguridad: Patrón '{pattern}' no permitido", 0

    # ==========================================================================
    # Create sandboxed execution script
    # ==========================================================================
    sandbox_wrapper = '''
import sys
import resource

# Limit resources (Linux/Mac only)
try:
    # Limit memory to 50MB
    resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, 50 * 1024 * 1024))
    # Limit CPU time to timeout + 1 second
    resource.setrlimit(resource.RLIMIT_CPU, ({timeout}, {timeout} + 1))
    # Disable file creation
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    # Limit number of processes
    resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
except (AttributeError, ValueError):
    pass  # Windows doesn't support resource limits

# Restrict builtins
restricted_builtins = {{
    'print': print,
    'len': len,
    'range': range,
    'int': int,
    'float': float,
    'str': str,
    'bool': bool,
    'list': list,
    'dict': dict,
    'set': set,
    'tuple': tuple,
    'abs': abs,
    'max': max,
    'min': min,
    'sum': sum,
    'sorted': sorted,
    'reversed': reversed,
    'enumerate': enumerate,
    'zip': zip,
    'map': map,
    'filter': filter,
    'any': any,
    'all': all,
    'isinstance': isinstance,
    'type': type,
    'round': round,
    'pow': pow,
    'divmod': divmod,
    'chr': chr,
    'ord': ord,
    'hex': hex,
    'bin': bin,
    'oct': oct,
    'format': format,
    'repr': repr,
    'hash': hash,
    'id': id,
    'slice': slice,
    'iter': iter,
    'next': next,
    'True': True,
    'False': False,
    'None': None,
    'Exception': Exception,
    'ValueError': ValueError,
    'TypeError': TypeError,
    'IndexError': IndexError,
    'KeyError': KeyError,
    'ZeroDivisionError': ZeroDivisionError,
}}

# User code below (executed with restricted builtins)
__builtins__ = restricted_builtins

'''.format(timeout=timeout_seconds)

    sandboxed_code = sandbox_wrapper + code

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(sandboxed_code)
        temp_file = f.name

    try:
        start_time = time.time()
        result = subprocess.run(
            ['python', '-I', temp_file],  # -I: isolated mode (no user site, PYTHONPATH ignored)
            input=test_input,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            env={  # Minimal environment
                'PATH': os.environ.get('PATH', ''),
                'PYTHONDONTWRITEBYTECODE': '1',
                'PYTHONUNBUFFERED': '1',
            }
        )
        execution_time = int((time.time() - start_time) * 1000)

        return result.stdout.strip(), result.stderr.strip(), execution_time
    except subprocess.TimeoutExpired:
        return "", "Error: Tiempo de ejecución excedido", timeout_seconds * 1000
    except Exception as e:
        return "", f"Error: {str(e)}", 0
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


async def evaluate_code_with_ai(code: str, exercise: Exercise, test_results: dict) -> dict:
    """
    Evalúa el código usando Ollama para obtener feedback cualitativo
    """
    # Configurar Ollama con variables de entorno
    ollama_config = {
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        "temperature": float(os.getenv("OLLAMA_TEMPERATURE", "0.7")),
        "timeout": float(os.getenv("OLLAMA_TIMEOUT", "120"))
    }
    llm = OllamaProvider(ollama_config)
    
    prompt = f"""Eres un profesor de programación experto. Evalúa el siguiente código Python:

EJERCICIO: {exercise.title}
DESCRIPCIÓN: {exercise.description}
NIVEL: {exercise.difficulty_level}/10

CÓDIGO DEL ESTUDIANTE:
```python
{code}
```

RESULTADOS DE TESTS:
- Tests pasados: {test_results['passed']}/{test_results['total']}
- Tests correctos: {test_results['passed'] == test_results['total']}

Proporciona una evaluación detallada en formato JSON con:
{{
  "overall_score": <float 0-10>,
  "code_quality": <float 0-10>,
  "readability": <float 0-10>,
  "efficiency": <float 0-10>,
  "best_practices": <float 0-10>,
  "feedback": "<string con feedback constructivo>",
  "strengths": ["<fortaleza1>", "<fortaleza2>"],
  "improvements": ["<mejora1>", "<mejora2>"]
}}

RESPONDE SOLO CON EL JSON, SIN TEXTO ADICIONAL."""

    try:
        response = await llm.generate(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Parsear respuesta JSON
        content = response.content.strip()
        # Remover markdown si existe
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        evaluation = json.loads(content.strip())
        return evaluation
    except Exception as e:
        logger.warning(f"Error en evaluación de IA: {e}", exc_info=True)
        # Fallback a evaluación básica
        base_score = (test_results['passed'] / test_results['total']) * 10 if test_results['total'] > 0 else 0
        return {
            "overall_score": base_score,
            "code_quality": base_score,
            "readability": base_score,
            "efficiency": base_score,
            "best_practices": base_score,
            "feedback": "Evaluación automática: " + ("Código correcto" if test_results['passed'] == test_results['total'] else "Hay errores en algunos tests"),
            "strengths": [],
            "improvements": []
        }


@router.get("", response_model=List[ExerciseResponse])
async def list_exercises(
    difficulty: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Lista todos los ejercicios disponibles"""
    query = db.query(Exercise)
    
    if difficulty is not None:
        query = query.filter(Exercise.difficulty_level == difficulty)
    
    exercises = query.order_by(Exercise.difficulty_level).all()
    
    return [
        {
            "id": ex.id,
            "title": ex.title,
            "description": ex.description,
            "difficulty_level": ex.difficulty_level,
            "starter_code": ex.starter_code,
            "hints": ex.hints,
            "max_score": ex.max_score,
            "time_limit_seconds": ex.time_limit_seconds
        }
        for ex in exercises
    ]


@router.get("/stats")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene estadísticas del usuario"""
    submissions = db.query(UserExerciseSubmission).filter(
        UserExerciseSubmission.user_id == current_user.id
    ).all()
    
    if not submissions:
        return {
            "total_submissions": 0,
            "completed_exercises": 0,
            "average_score": 0.0,
            "total_exercises": 0
        }
    
    correct_count = sum(1 for s in submissions if s.is_correct == "true")
    scores = [s.ai_score for s in submissions if s.ai_score is not None]
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    unique_exercises = len(set(s.exercise_id for s in submissions))
    
    return {
        "total_submissions": len(submissions),
        "completed_exercises": correct_count,
        "average_score": round(avg_score, 2),
        "total_exercises": unique_exercises
    }


@router.get("/{exercise_id}", response_model=ExerciseResponse)
async def get_exercise(
    exercise_id: str,
    db: Session = Depends(get_db)
):
    """Obtiene un ejercicio específico"""
    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    
    return {
        "id": exercise.id,
        "title": exercise.title,
        "description": exercise.description,
        "difficulty_level": exercise.difficulty_level,
        "starter_code": exercise.starter_code,
        "hints": exercise.hints,
        "max_score": exercise.max_score,
        "time_limit_seconds": exercise.time_limit_seconds
    }


@router.post("/submit", response_model=SubmissionResult)
@limiter.limit("5/minute")  # FIX 1.3 Cortez3: Rate limit code execution (DOS protection)
async def submit_code(
    request: Request,  # FIX 1.3 Cortez3: Required for rate limiter
    submission: CodeSubmission,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Envía código para evaluación (requiere autenticación)"""
    # Obtener ejercicio
    exercise = db.query(Exercise).filter(Exercise.id == submission.exercise_id).first()
    
    if not exercise:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    
    # Ejecutar tests
    test_results = []
    passed_tests = 0
    total_tests = len(exercise.test_cases)
    total_execution_time = 0
    
    for i, test_case in enumerate(exercise.test_cases):
        test_input = test_case.get("input", "")
        expected_output = test_case.get("expected_output", "")
        
        output, error, exec_time = execute_python_code(
            submission.code,
            test_input,
            exercise.time_limit_seconds
        )
        
        total_execution_time += exec_time
        
        is_correct = output == expected_output and not error
        if is_correct:
            passed_tests += 1
        
        test_results.append({
            "test_number": i + 1,
            "input": test_input,
            "expected_output": expected_output,
            "actual_output": output,
            "error": error,
            "passed": is_correct,
            "execution_time_ms": exec_time
        })
    
    # Evaluar con IA
    ai_evaluation = await evaluate_code_with_ai(
        submission.code,
        exercise,
        {"passed": passed_tests, "total": total_tests}
    )
    
    # Guardar submission con el usuario autenticado
    new_submission = UserExerciseSubmission(
        user_id=current_user.id,
        exercise_id=exercise.id,
        submitted_code=submission.code,
        passed_tests=passed_tests,
        total_tests=total_tests,
        execution_time_ms=total_execution_time,
        ai_score=ai_evaluation.get("overall_score"),
        ai_feedback=json.dumps(ai_evaluation.get("feedback", "")),
        code_quality_score=ai_evaluation.get("code_quality"),
        readability_score=ai_evaluation.get("readability"),
        efficiency_score=ai_evaluation.get("efficiency"),
        best_practices_score=ai_evaluation.get("best_practices"),
        is_correct="true" if passed_tests == total_tests else "false"
    )
    
    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)
    
    return {
        "id": new_submission.id,
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "is_correct": passed_tests == total_tests,
        "execution_time_ms": total_execution_time,
        "ai_score": ai_evaluation.get("overall_score"),
        "ai_feedback": json.dumps(ai_evaluation, ensure_ascii=False),
        "code_quality_score": ai_evaluation.get("code_quality"),
        "readability_score": ai_evaluation.get("readability"),
        "efficiency_score": ai_evaluation.get("efficiency"),
        "best_practices_score": ai_evaluation.get("best_practices"),
        "test_results": test_results
    }


@router.get("/user/submissions")
async def get_user_submissions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene todas las submissions del usuario actual"""
    submissions = db.query(UserExerciseSubmission).filter(
        UserExerciseSubmission.user_id == current_user.id
    ).order_by(UserExerciseSubmission.submitted_at.desc()).all()
    
    return {
        "total": len(submissions),
        "submissions": [
            {
                "id": s.id,
                "exercise_id": s.exercise_id,
                "passed_tests": s.passed_tests,
                "total_tests": s.total_tests,
                "is_correct": s.is_correct,
                "ai_score": s.ai_score,
                "submitted_at": s.submitted_at.isoformat() if s.submitted_at else None
            }
            for s in submissions
        ]
    }
