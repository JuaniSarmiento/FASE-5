# 📚 Sistema de Ejercicios de Programación

## 🎯 Visión General

Este sistema permite crear y gestionar ejercicios de programación estructurados para una plataforma educativa con React + TypeScript en el frontend y Python en el backend.

## 📁 Estructura de Archivos

```
activia1-main/
├── backend/
│   └── data/
│       └── exercises/          # ⭐ Ejercicios en JSON
│           ├── unit1_fundamentals.json   # Unidad 1: Variables, condicionales, bucles
│           ├── unit2_structures.json     # Unidad 2: Listas, diccionarios, tuplas
│           ├── unit3_functions.json      # Unidad 3: Funciones, recursión, lambda
│           ├── unit4_files.json          # Unidad 4: CSV, JSON, archivos de texto
│           └── unit5_oop.json            # Unidad 5: POO, herencia, composición
│
└── frontEnd/
    └── src/
        └── types/
            ├── exercise.d.ts   # ⭐ Definiciones TypeScript
            └── index.ts        # Export central (ya actualizado)
```

## 🏗️ Estructura del JSON

Cada ejercicio sigue esta estructura **frontend-ready**:

```json
{
  "id": "U4-CSV-01",
  "meta": {
    "title": "Procesamiento de CSV: Análisis de Ventas",
    "difficulty": "Medium",
    "estimated_time_min": 35,
    "tags": ["CSV", "Data Cleaning", "File I/O"]
  },
  "ui_config": {
    "editor_language": "python",
    "read_only_lines": [1, 2, 3],
    "placeholder_text": "# Procesa el archivo CSV..."
  },
  "content": {
    "story_markdown": "## Contexto\n\nEres un **Data Engineer**...",
    "mission_markdown": "### Tu Misión\n\n1. Lee el archivo...",
    "constraints": ["No usar Pandas", "Manejar FileNotFoundError"]
  },
  "starter_code": "import csv\n\ndef procesar_ventas(archivo):\n    pass",
  "hidden_tests": [
    {
      "input": "ventas.csv",
      "expected": "producto_top == 'Laptop' and gran_total == 8432.50"
    }
  ]
}
```

## 🎨 Interfaz TypeScript

**Archivo:** `frontEnd/src/types/exercise.d.ts`

```typescript
export interface IExercise {
  id: string;
  meta: IExerciseMeta;
  ui_config: IExerciseUIConfig;
  content: IExerciseContent;
  starter_code: string;
  hidden_tests: IHiddenTest[];
}
```

### Uso en React

```tsx
import { IExercise } from '@/types';

const ExerciseCard: React.FC<{ exercise: IExercise }> = ({ exercise }) => {
  return (
    <div>
      <h3>{exercise.meta.title}</h3>
      <span className={getDifficultyClass(exercise.meta.difficulty)}>
        {exercise.meta.difficulty}
      </span>
      <ReactMarkdown>{exercise.content.story_markdown}</ReactMarkdown>
    </div>
  );
};
```

## 📝 Contenido de los Ejercicios

### Unidad 1: Fundamentos (3 ejercicios)
- **U1-VAR-01**: Variables y Tipos de Datos (Easy, 15 min)
- **U1-COND-01**: Estructuras Condicionales (Easy, 20 min)
- **U1-LOOP-01**: Bucles: Análisis de Temperaturas (Medium, 25 min)

### Unidad 2: Estructuras de Datos (3 ejercicios)
- **U2-LIST-01**: Listas: Gestión de Inventario (Easy, 20 min)
- **U2-DICT-01**: Diccionarios: Sistema de Contactos (Medium, 30 min)
- **U2-TUPLE-01**: Tuplas: Coordenadas Geográficas (Easy, 15 min)

### Unidad 3: Funciones (3 ejercicios)
- **U3-FUNC-01**: Funciones: Calculadora de IMC (Easy, 20 min)
- **U3-RECUR-01**: Recursión: Factorial y Fibonacci (Medium, 30 min)
- **U3-LAMBDA-01**: Funciones Lambda y Map/Filter (Medium, 25 min)

### Unidad 4: Manejo de Archivos (3 ejercicios)
- **U4-CSV-01**: Procesamiento de CSV (Medium, 35 min)
- **U4-JSON-01**: JSON: API de Usuarios (Medium, 30 min)
- **U4-TXT-01**: Procesamiento de Texto: Análisis de Log (Hard, 40 min)

### Unidad 5: Programación Orientada a Objetos (3 ejercicios)
- **U5-OOP-01**: POO: Sistema de Biblioteca (Hard, 45 min)
- **U5-INHERIT-01**: Herencia: Jerarquía de Empleados (Medium, 35 min)
- **U5-COMP-01**: Composición: Sistema de Pedidos (Hard, 40 min)

## ✅ Características "Frontend-Ready"

### 1. **Markdown Rico**
Todos los campos de texto usan Markdown con soporte para:
- **Negritas**, *itálicas*
- Listas numeradas/bullet
- Bloques de código con sintaxis
- Fórmulas matemáticas LaTeX: `$$IMC = \frac{peso}{altura^2}$$`

```markdown
## Contexto

Eres un **Data Analyst Junior** en una startup...

**Datos del trimestre:**
- Enero: $12,500
- Febrero: $15,300
```

### 2. **Starter Code Ejecutable**
El código inicial es **siempre ejecutable** (sin errores de sintaxis):

```python
# NO TOCAR ESTA LÍNEA
def obtener_letra(nota):
    """
    Convierte una nota numérica a letra.
    """
    # TODO: Implementa la lógica
    pass
```

### 3. **Editor Configuration**
```json
"ui_config": {
  "editor_language": "python",
  "read_only_lines": [1, 2, 3],  // Líneas protegidas
  "placeholder_text": "# Escribe tu solución aquí..."
}
```

### 4. **Hidden Tests**
Tests para el sandbox backend (invisible para el estudiante):

```json
"hidden_tests": [
  {
    "input": "95",
    "expected": "A"
  },
  {
    "input": "105",
    "expected": "INVALID"
  }
]
```

## 🔧 Integración con el Sistema Existente

### Backend
```python
# backend/api/routers/exercises.py
from fastapi import APIRouter
import json

@router.get("/exercises")
async def list_exercises(unit: Optional[str] = None):
    """Lista ejercicios por unidad"""
    exercises = []
    if unit:
        with open(f'backend/data/exercises/{unit}.json') as f:
            exercises = json.load(f)
    return exercises
```

### Frontend Service
```typescript
// frontEnd/src/services/api/exercises.service.ts
import { IExercise, IExerciseSubmission } from '@/types';

class ExercisesService extends BaseApiService {
  async getExercise(id: string): Promise<IExercise> {
    return this.get<IExercise>(`/${id}`);
  }
  
  async submit(submission: IExerciseSubmission) {
    return this.post('/submit', submission);
  }
}
```

## 🎓 Pedagogía

Cada ejercicio sigue el patrón:

1. **Contexto Real** (Story-based learning)
   - Rol profesional: "Eres un Data Engineer..."
   - Situación realista del mundo laboral

2. **Misión Clara**
   - Pasos específicos numerados
   - Objetivos medibles

3. **Constraints**
   - Limitaciones técnicas (no usar librerías X)
   - Buenas prácticas a seguir

4. **Scaffolding**
   - Código inicial con estructura
   - Comentarios TODO estratégicos
   - Líneas protegidas (read_only_lines)

## 🚀 Próximos Pasos

### Para usar en el frontend:

1. **Cargar ejercicios:**
```typescript
const exercise = await exercisesService.getById('U1-VAR-01');
```

2. **Renderizar:**
```tsx
<ReactMarkdown>{exercise.content.story_markdown}</ReactMarkdown>
<MonacoEditor
  language={exercise.ui_config.editor_language}
  value={exercise.starter_code}
  readOnlyLines={exercise.ui_config.read_only_lines}
/>
```

3. **Enviar código:**
```typescript
const result = await exercisesService.submit({
  exercise_id: 'U1-VAR-01',
  code: editorCode
});
```

## 📦 Total de Ejercicios

- **15 ejercicios** distribuidos en 5 unidades
- **Niveles:** 6 Easy, 6 Medium, 3 Hard
- **Tiempo estimado total:** ~450 minutos (7.5 horas)
- **Cobertura:** Fundamentos completos de Python

## 📚 Referencias

- **Tipos:** `frontEnd/src/types/exercise.d.ts`
- **Datos:** `backend/data/exercises/*.json`
- **Exportación:** `frontEnd/src/types/index.ts` (líneas 352+)

---

**Generado:** 2025-01-17  
**Arquitecto:** Lead Full-Stack Architect  
**Stack:** React + TypeScript + Python
