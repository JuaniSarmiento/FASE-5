# 🎓 Sistema de Evaluación de Código con Mentor "Alex"

## 📋 Visión General

Sistema completo de evaluación inteligente de código que usa un LLM (Claude, GPT-4, etc.) actuando como **"Alex"**, un Arquitecto de Software Senior que realiza code reviews pedagógicos.

**Características:**
- ✅ Evaluación en 3 dimensiones (Functionality, Code Quality, Robustness)
- ✅ Feedback narrativo personalizado en Markdown
- ✅ Anotaciones línea por línea en el código
- ✅ Sugerencias de refactoring (versión Senior)
- ✅ Sistema de gamificación (XP, logros)
- ✅ Type-safe con TypeScript

---

## 📁 Archivos Creados

```
activia1-main/
├── backend/
│   ├── prompts/
│   │   └── code_evaluator_prompt.md      # ⭐ Prompt template para LLM
│   └── services/
│       └── code_evaluator.py             # ⭐ Servicio de evaluación
│
├── frontEnd/
│   └── src/
│       └── types/
│           ├── evaluation.d.ts           # ⭐ Interfaces TypeScript
│           └── index.ts                  # ✅ ACTUALIZADO con exports
│
└── examples/
    └── ejemplo_evaluacion_ui.tsx         # ⭐ Componentes React
```

---

## 🔧 Integración Backend

### 1. Instalación del Servicio

```python
# backend/services/code_evaluator.py
from backend.services.code_evaluator import CodeEvaluator

# Con cliente LLM (Claude, OpenAI, etc.)
from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key="tu-api-key")
evaluator = CodeEvaluator(llm_client=client)

# Modo mock (para testing sin LLM)
evaluator = CodeEvaluator()  # Sin cliente
```

### 2. Endpoint de Evaluación

```python
# backend/api/routers/exercises.py
from backend.services.code_evaluator import evaluate_code
from backend.data.exercises.loader import get_exercise

@router.post("/exercises/{exercise_id}/evaluate")
async def evaluate_exercise(
    exercise_id: str,
    request: EvaluationRequest,
    current_user: User = Depends(get_current_user)
):
    """Evalúa el código del estudiante con mentor Alex"""
    
    # 1. Cargar ejercicio
    exercise = get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(404, "Ejercicio no encontrado")
    
    # 2. Ejecutar código en sandbox
    sandbox_result = await execute_in_sandbox(
        code=request.student_code,
        language=exercise['ui_config']['editor_language'],
        tests=exercise['hidden_tests']
    )
    
    # 3. Evaluar con Alex
    evaluation = await evaluate_code(
        exercise=exercise,
        student_code=request.student_code,
        sandbox_result=sandbox_result,
        llm_client=llm_client  # Tu cliente LLM
    )
    
    # 4. Guardar en BD
    save_evaluation(
        user_id=current_user.id,
        exercise_id=exercise_id,
        evaluation=evaluation
    )
    
    return evaluation
```

### 3. Schemas Pydantic

```python
# backend/api/schemas/evaluation.py
from pydantic import BaseModel
from typing import List, Optional

class EvaluationRequest(BaseModel):
    student_code: str

class DimensionScore(BaseModel):
    score: float  # 0-10
    comment: str

class CodeAnnotation(BaseModel):
    line_number: int
    severity: str  # 'info' | 'warning' | 'error'
    message: str

class EvaluationResponse(BaseModel):
    evaluation: dict
    dimensions: dict
    code_review: dict
    gamification: dict
    metadata: Optional[dict] = None
```

---

## 🎨 Integración Frontend

### 1. Tipos TypeScript

```typescript
import { 
  IEvaluationResult, 
  IEvaluationRequest,
  ACHIEVEMENTS_CATALOG 
} from '@/types';

// Todos los tipos están disponibles globalmente
```

### 2. Servicio API

```typescript
// frontEnd/src/services/api/evaluation.service.ts
import { BaseApiService } from './base.service';
import { IEvaluationResult, IEvaluationRequest } from '@/types';

class EvaluationService extends BaseApiService {
  constructor() {
    super('/exercises');
  }

  async evaluate(
    exerciseId: string,
    request: IEvaluationRequest
  ): Promise<IEvaluationResult> {
    return this.post<IEvaluationResult>(
      `/${exerciseId}/evaluate`,
      request
    );
  }

  async getHistory(userId: string) {
    return this.get(`/users/${userId}/evaluations`);
  }

  async getProgress(userId: string) {
    return this.get(`/users/${userId}/progress`);
  }
}

export const evaluationService = new EvaluationService();
```

### 3. Componente React

Ver archivo completo: `examples/ejemplo_evaluacion_ui.tsx`

```tsx
import { EvaluationResultView } from '@/components/evaluation';
import { evaluationService } from '@/services/api';

// En tu componente de ejercicio
const handleSubmit = async () => {
  const result = await evaluationService.evaluate('U1-VAR-01', {
    student_code: code
  });
  
  setEvaluationResult(result);
};

// Renderizar
{evaluationResult && (
  <EvaluationResultView
    result={evaluationResult}
    studentCode={code}
    onRetry={() => setEvaluationResult(null)}
  />
)}
```

---

## 📊 Estructura de la Respuesta

### Ejemplo de JSON Completo

```json
{
  "evaluation": {
    "score": 85.5,
    "status": "PASS",
    "title": "Lógica correcta, pero frágil",
    "summary_markdown": "Tu solución **cumple la misión**, pero presenta **vulnerabilidades** en el manejo de errores.",
    "toast_type": "success",
    "toast_message": "¡Bien! Funcionó, pero podría ser más robusto."
  },
  "dimensions": {
    "functionality": {
      "score": 9,
      "comment": "La lógica cumple con todos los requisitos."
    },
    "code_quality": {
      "score": 8,
      "comment": "Buen uso de nombres descriptivos."
    },
    "robustness": {
      "score": 6,
      "comment": "Falta validación de inputs."
    }
  },
  "code_review": {
    "highlighted_lines": [
      {
        "line_number": 12,
        "severity": "warning",
        "message": "División sin validar denominador."
      }
    ],
    "refactoring_suggestion": "def calcular_promedio(valores):\n    if not valores:\n        return 0.0\n    ..."
  },
  "gamification": {
    "xp_earned": 85,
    "achievements_unlocked": ["Clean Code Ninja", "First Blood"]
  },
  "metadata": {
    "exercise_id": "U1-VAR-01",
    "evaluated_at": "2025-12-17T10:30:00Z",
    "llm_model": "claude-sonnet-4.5"
  }
}
```

---

## 🎯 Criterios de Evaluación

### Functionality (0-10)
| Score | Descripción |
|-------|-------------|
| 10 | Cumple 100% la misión. Output exacto. |
| 7-9 | Funciona pero con pequeñas desviaciones. |
| 4-6 | Lógica parcial, algunos tests fallan. |
| 0-3 | No funciona o hardcoded. |

### Code Quality (0-10)
| Score | Descripción |
|-------|-------------|
| 10 | Código limpio, naming perfecto, bien estructurado. |
| 7-9 | Buen código, pequeños detalles de naming. |
| 4-6 | Código funcional pero desorganizado. |
| 0-3 | Spaghetti code, variables `x`, `y`, `z`. |

### Robustness (0-10)
| Score | Descripción |
|-------|-------------|
| 10 | Maneja todos los edge cases, excepciones bien tratadas. |
| 7-9 | Maneja casos básicos, falta validación exhaustiva. |
| 4-6 | Código frágil, crashea con inputs inesperados. |
| 0-3 | Sin manejo de errores, bare excepts. |

---

## 🏆 Sistema de Logros

### Logros Disponibles

| Logro | Condición | XP Bonus | Rareza |
|-------|-----------|----------|--------|
| 🎯 First Blood | Primer ejercicio completado | 50 | Common |
| 🥋 Clean Code Ninja | code_quality >= 9 | 100 | Rare |
| 🛡️ Error Handler | Try-except correcto | 75 | Common |
| 🐍 Pythonista | Features pythonic | 150 | Epic |
| 🛡️ Defensive Programmer | Valida inputs, edge cases | 200 | Epic |
| ♻️ DRY Master | Código modular, sin repetición | 100 | Rare |
| ⚡ Speed Demon | < 50% tiempo estimado | 150 | Rare |
| 💎 Perfectionist | Score 100/100 | 500 | Legendary |

### Integración de Logros

```typescript
import { ACHIEVEMENTS_CATALOG } from '@/types';

// Buscar logro
const achievement = ACHIEVEMENTS_CATALOG.find(
  a => a.id === 'clean_code_ninja'
);

// Mostrar detalles
<div>
  <span>{achievement.icon}</span>
  <span>{achievement.name}</span>
  <span>+{achievement.xp_bonus} XP</span>
</div>
```

---

## 🔥 Features Clave

### 1. **Detección de Hardcoding**
El evaluador detecta cuando el estudiante imprime directamente la respuesta:

```python
# Hardcoding detectado (Score 0)
print("Total: $42600")
print("Promedio: $14200.00")
```

### 2. **Anotaciones Contextuales**
Comentarios específicos en líneas problemáticas:

```typescript
{
  line_number: 12,
  severity: "warning",
  message: "División sin validar denominador. Si 'total' es 0, esto crashea."
}
```

### 3. **Refactoring Senior**
Muestra cómo un Senior escribiría el código:

```python
# Versión Senior (más robusta)
def calcular_promedio(valores):
    if not valores:  # Validar lista vacía
        return 0.0
    try:
        total = sum(valores)
        promedio = total / len(valores)
        return round(promedio, 2)
    except (TypeError, ValueError) as e:
        print(f'Error: {e}')
        return None
```

### 4. **Feedback Pedagógico**
Tono constructivo que empieza validando, señala el gap y cierra con consejo:

> Tu solución **funciona correctamente** y el uso de **f-strings** es excelente. Sin embargo, no validas si la lista está **vacía**, lo que causaría un error. Un Senior siempre pregunta: *"¿Qué puede romper esto?"*. Agrega `if not valores: return 0.0` al inicio.

---

## 🧪 Testing

### Modo Mock (Sin LLM)

```python
# Útil para desarrollo y testing
evaluator = CodeEvaluator()  # Sin cliente LLM
result = await evaluator.evaluate(exercise, code, sandbox_result)

# Retorna evaluación básica basada en tests
```

### Prueba del Prompt

```python
# backend/services/code_evaluator.py
python code_evaluator.py

# Output:
# {
#   "evaluation": {
#     "score": 100,
#     "status": "PASS",
#     ...
#   }
# }
```

---

## 📝 Ejemplo de Uso Completo

### Backend

```python
from backend.services.code_evaluator import CodeEvaluator
from backend.data.exercises.loader import get_exercise

async def evaluate_student_code(exercise_id: str, code: str):
    # 1. Cargar ejercicio
    exercise = get_exercise(exercise_id)
    
    # 2. Ejecutar en sandbox
    sandbox_result = {
        "exit_code": 0,
        "stdout": "Total: $42600\nPromedio: $14200.00\n",
        "stderr": "",
        "tests_passed": 2,
        "tests_total": 2
    }
    
    # 3. Evaluar
    evaluator = CodeEvaluator(llm_client)
    result = await evaluator.evaluate(
        exercise=exercise,
        student_code=code,
        sandbox_result=sandbox_result
    )
    
    return result
```

### Frontend

```tsx
const ExerciseWithEvaluation = () => {
  const [code, setCode] = useState('');
  const [result, setResult] = useState<IEvaluationResult | null>(null);
  
  const handleSubmit = async () => {
    const evaluation = await evaluationService.evaluate('U1-VAR-01', {
      student_code: code
    });
    setResult(evaluation);
  };
  
  return (
    <div>
      <Editor value={code} onChange={setCode} />
      <button onClick={handleSubmit}>Evaluar</button>
      
      {result && (
        <EvaluationResultView
          result={result}
          studentCode={code}
          onRetry={() => setResult(null)}
        />
      )}
    </div>
  );
};
```

---

## 🚀 Próximos Pasos

### Implementación Inmediata
1. ✅ Integrar cliente LLM (Claude/OpenAI)
2. ✅ Crear endpoint `/exercises/{id}/evaluate`
3. ✅ Implementar sandbox de ejecución
4. ✅ Guardar evaluaciones en BD

### Mejoras Futuras
- [ ] Evaluación comparativa (vs otros estudiantes)
- [ ] Detección de plagio
- [ ] Hints progresivos antes de evaluar
- [ ] Evaluación de complejidad algorítmica (Big O)
- [ ] Análisis de seguridad de código

---

## 📞 Referencias

- **Prompt Template:** `backend/prompts/code_evaluator_prompt.md`
- **Servicio Python:** `backend/services/code_evaluator.py`
- **Tipos TS:** `frontEnd/src/types/evaluation.d.ts`
- **Componente UI:** `examples/ejemplo_evaluacion_ui.tsx`

---

**Generado:** 17 de Diciembre, 2025  
**Versión:** 1.0  
**Stack:** Python + FastAPI + React + TypeScript + LLM
