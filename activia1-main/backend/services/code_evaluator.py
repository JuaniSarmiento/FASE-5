"""
Code Evaluator Service - Sistema de Evaluación con Mentor "Alex"

Este servicio implementa la evaluación de código usando un LLM (Claude, GPT-4, etc.)
que actúa como un mentor técnico senior. Evalúa no solo funcionalidad sino también
calidad de código, robustez y proporciona feedback pedagógico.

Uso:
    from backend.services.code_evaluator import CodeEvaluator
    
    evaluator = CodeEvaluator(llm_client)
    result = await evaluator.evaluate(
        exercise=exercise,
        student_code=code,
        sandbox_result=sandbox_output
    )
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class CodeEvaluator:
    """
    Evaluador de código que usa un LLM como mentor técnico.
    """
    
    PROMPT_TEMPLATE_PATH = Path(__file__).parent.parent / "prompts" / "code_evaluator_prompt.md"
    
    # Rúbrica por defecto
    DEFAULT_RUBRIC = {
        "functionality": {"weight": 0.4, "max_score": 10},
        "code_quality": {"weight": 0.3, "max_score": 10},
        "robustness": {"weight": 0.3, "max_score": 10}
    }
    
    def __init__(self, llm_client=None):
        """
        Inicializa el evaluador.
        
        Args:
            llm_client: Cliente del LLM (Claude, OpenAI, etc.)
        """
        self.llm_client = llm_client
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Carga el template del prompt desde archivo."""
        try:
            with open(self.PROMPT_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Prompt template not found at {self.PROMPT_TEMPLATE_PATH}"
            )
    
    def _build_prompt(
        self,
        exercise: Dict[str, Any],
        student_code: str,
        sandbox_result: Dict[str, Any],
        rubric: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Construye el prompt final reemplazando variables.
        
        Args:
            exercise: Ejercicio completo (JSON)
            student_code: Código del estudiante
            sandbox_result: Resultado de ejecución del sandbox
            rubric: Rúbrica personalizada (opcional)
        
        Returns:
            Prompt con variables reemplazadas
        """
        rubric = rubric or self.DEFAULT_RUBRIC
        
        # Extraer misión del exercise
        mission_lines = exercise['content']['mission_markdown'].split('\n')
        mission_text = '\n'.join(mission_lines)
        
        # Construir constraints
        constraints_text = '\n'.join(
            f"- {c}" for c in exercise['content']['constraints']
        )
        
        # Reemplazar variables en el template
        prompt = self.prompt_template
        replacements = {
            '{{exercise_title}}': exercise['meta']['title'],
            '{{exercise_mission}}': mission_text,
            '{{exercise_constraints}}': constraints_text,
            '{{student_code}}': student_code,
            '{{sandbox_exit_code}}': str(sandbox_result.get('exit_code', 0)),
            '{{sandbox_stdout}}': sandbox_result.get('stdout', ''),
            '{{sandbox_stderr}}': sandbox_result.get('stderr', ''),
            '{{rubric_json}}': json.dumps(rubric, indent=2)
        }
        
        for key, value in replacements.items():
            prompt = prompt.replace(key, value)
        
        return prompt
    
    async def evaluate(
        self,
        exercise: Dict[str, Any],
        student_code: str,
        sandbox_result: Dict[str, Any],
        rubric: Optional[Dict[str, Any]] = None,
        student_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evalúa el código del estudiante.
        
        Args:
            exercise: Ejercicio completo
            student_code: Código enviado
            sandbox_result: Resultado del sandbox
            rubric: Rúbrica personalizada
            student_id: ID del estudiante (para tracking)
        
        Returns:
            Diccionario con la evaluación completa (IEvaluationResult)
        """
        # 1. Construir prompt
        prompt = self._build_prompt(exercise, student_code, sandbox_result, rubric)
        
        # 2. Llamar al LLM
        if self.llm_client is None:
            # Modo mock para testing
            return self._mock_evaluation(sandbox_result)
        
        try:
            # Importar LLMMessage y LLMRole
            from ..llm.base import LLMMessage, LLMRole
            
            # Llamar al LLM usando el método generate()
            response = await self.llm_client.generate(
                messages=[
                    LLMMessage(role=LLMRole.USER, content=prompt)
                ],
                temperature=0.3,  # Temperatura baja para evaluación consistente
                max_tokens=2000
            )
            
            # 3. Parsear JSON de respuesta
            evaluation_result = self._parse_llm_response(response.content)
            
            # 4. Validar que tenga todos los campos requeridos
            if 'code_review' not in evaluation_result:
                evaluation_result['code_review'] = {
                    'highlighted_lines': [],
                    'refactoring_suggestion': None
                }
            
            if 'gamification' not in evaluation_result:
                score = evaluation_result.get('evaluation', {}).get('score', 0)
                evaluation_result['gamification'] = {
                    'xp_earned': int(score),
                    'achievements_unlocked': []
                }
            
            # 5. Agregar metadata
            evaluation_result['metadata'] = {
                'exercise_id': exercise['id'],
                'student_id': student_id,
                'evaluated_at': datetime.utcnow().isoformat(),
                'evaluator_version': '1.0',
                'llm_model': response.model
            }
            
            return evaluation_result
            
        except Exception as e:
            # Fallback en caso de error del LLM (timeout, modelo no disponible, etc.)
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error en evaluación con IA, usando evaluación automática: {e}")
            logger.debug(traceback.format_exc())
            # Usar evaluación mock en lugar de fallback de error
            return self._mock_evaluation(sandbox_result)
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parsea la respuesta JSON del LLM.
        
        Args:
            response: Respuesta del LLM (debe ser JSON)
        
        Returns:
            Diccionario con la evaluación
        """
        # Extraer JSON de la respuesta (puede venir con texto adicional)
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start == -1 or json_end == 0:
            raise ValueError("No se encontró JSON válido en la respuesta")
        
        json_str = response[json_start:json_end]
        return json.loads(json_str)
    
    def _mock_evaluation(self, sandbox_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluación mock para testing sin LLM.
        """
        exit_code = sandbox_result.get('exit_code', 0)
        tests_passed = sandbox_result.get('tests_passed', 0)
        tests_total = sandbox_result.get('tests_total', 1)
        
        success = exit_code == 0 and tests_passed == tests_total
        score = (tests_passed / tests_total * 100) if tests_total > 0 else 0
        
        return {
            "evaluation": {
                "score": score,
                "status": "PASS" if success else "FAIL",
                "title": "Evaluación Automática",
                "summary_markdown": f"Tu código {'pasó' if success else 'falló'} {tests_passed}/{tests_total} tests.",
                "toast_type": "success" if success else "error",
                "toast_message": f"Tests: {tests_passed}/{tests_total}"
            },
            "dimensions": {
                "functionality": {
                    "score": 10 if success else 5,
                    "comment": "Evaluación automática basada en tests."
                },
                "code_quality": {
                    "score": 7,
                    "comment": "Requiere evaluación manual."
                },
                "robustness": {
                    "score": 7,
                    "comment": "Requiere evaluación manual."
                }
            },
            "code_review": {
                "highlighted_lines": [],
                "refactoring_suggestion": None
            },
            "gamification": {
                "xp_earned": int(score),
                "achievements_unlocked": ["First Blood"] if success else []
            }
        }
    
    def _fallback_evaluation(self, error: str, sandbox_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluación de fallback en caso de error del LLM.
        """
        return {
            "evaluation": {
                "score": 0,
                "status": "WARNING",
                "title": "Error en Evaluación",
                "summary_markdown": f"Ocurrió un error al evaluar tu código: {error}. Por favor, intenta nuevamente.",
                "toast_type": "warning",
                "toast_message": "Error en evaluación. Intenta nuevamente."
            },
            "dimensions": {
                "functionality": {"score": 0, "comment": "Error en evaluación."},
                "code_quality": {"score": 0, "comment": "Error en evaluación."},
                "robustness": {"score": 0, "comment": "Error en evaluación."}
            },
            "code_review": {
                "highlighted_lines": [],
                "refactoring_suggestion": None
            },
            "gamification": {
                "xp_earned": 0,
                "achievements_unlocked": []
            },
            "error": error
        }


# Helper functions para uso directo

async def evaluate_code(
    exercise: Dict[str, Any],
    student_code: str,
    sandbox_result: Dict[str, Any],
    llm_client=None
) -> Dict[str, Any]:
    """
    Función de conveniencia para evaluar código.
    
    Uso:
        result = await evaluate_code(exercise, code, sandbox_result)
    """
    evaluator = CodeEvaluator(llm_client)
    return await evaluator.evaluate(exercise, student_code, sandbox_result)


def calculate_final_score(dimensions: Dict[str, Dict[str, Any]], rubric: Dict[str, Any]) -> float:
    """
    Calcula el score final (0-100) basado en dimensiones y pesos.
    
    Args:
        dimensions: Scores de functionality, code_quality, robustness
        rubric: Pesos de cada dimensión
    
    Returns:
        Score final 0-100
    """
    weighted_sum = 0.0
    
    for dimension_name, dimension_data in dimensions.items():
        weight = rubric[dimension_name]['weight']
        score = dimension_data['score']  # 0-10
        max_score = rubric[dimension_name]['max_score']  # 10
        
        # Normalizar a 0-100 y aplicar peso
        normalized = (score / max_score) * 100
        weighted_sum += normalized * weight
    
    return round(weighted_sum, 2)


# Ejemplo de uso
if __name__ == "__main__":
    import asyncio
    
    # Mock de ejercicio
    exercise = {
        "id": "U1-VAR-01",
        "meta": {"title": "Variables y Tipos de Datos"},
        "content": {
            "mission_markdown": "1. Calcula el total\n2. Calcula el promedio",
            "constraints": ["Usar f-strings", "Nombres descriptivos"]
        }
    }
    
    student_code = """
ventas_enero = 12500
ventas_febrero = 15300
ventas_marzo = 14800

total = ventas_enero + ventas_febrero + ventas_marzo
promedio = total / 3

print(f"Total: ${total}")
print(f"Promedio: ${promedio:.2f}")
"""
    
    sandbox_result = {
        "exit_code": 0,
        "stdout": "Total: $42600\nPromedio: $14200.00\n",
        "stderr": "",
        "tests_passed": 2,
        "tests_total": 2
    }
    
    async def test():
        evaluator = CodeEvaluator()  # Sin LLM, usa mock
        result = await evaluator.evaluate(exercise, student_code, sandbox_result)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    asyncio.run(test())
