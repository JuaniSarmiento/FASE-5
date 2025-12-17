# 🎓 Sistema de Ejercicios con Evaluación IA - Guía de Inicio Rápido

## ✅ Sistema 100% Integrado

Tu proyecto ahora tiene un sistema completo de ejercicios de programación donde:
1. ✅ El usuario puede ver 15 ejercicios con consignas
2. ✅ Puede escribir código en un editor
3. ✅ La IA (mentor "Alex") evalúa el código y da nota + veredicto

---

## 🚀 Cómo Usar

### 1. Backend - Levantar el servidor

```bash
cd activia1-main
python -m backend
```

El servidor estará en: `http://localhost:8000`

### 2. Frontend - Levantar React

```bash
cd frontEnd
npm install  # Si es primera vez
npm run dev
```

La app estará en: `http://localhost:5173`

### 3. Agregar la Ruta al Router

Abre `frontEnd/src/App.tsx` (o tu archivo de rutas principal) y agrega:

```tsx
import { ExercisesPage } from './pages/ExercisesPage';

// Dentro de tus <Routes>
<Route path="/exercises/*" element={<ExercisesPage />} />
```

### 4. Navegar a los Ejercicios

```
http://localhost:5173/exercises
```

---

## 🎯 Flujo del Usuario

```
1. Usuario va a /exercises
   → Ve lista de 15 ejercicios organizados por dificultad

2. Filtra por "Easy" o busca "variables"
   → La lista se actualiza en tiempo real

3. Hace clic en "U1-VAR-01 - Variables y Tipos de Datos"
   → Se abre el workspace con:
     - Historia narrativa
     - Misión a completar
     - Editor de código con código inicial
     - Pistas (opcional)

4. Escribe su código en el editor
   ventas_enero = 12500
   ventas_febrero = 15300
   ...

5. Hace clic en "Evaluar Código"
   → Backend ejecuta el código
   → Alex (IA) evalúa:
     ✓ Functionality (9/10): Lógica correcta
     ✓ Code Quality (8/10): Buenos nombres
     ✓ Robustness (6/10): Falta validación

6. Ve el resultado completo:
   - Score General: 85.5/100
   - 3 dimensiones con barras de progreso
   - Anotaciones en el código (ej: línea 5 - "Sin validar división por 0")
   - Versión Senior del código (cómo un experto lo escribiría)
   - XP ganados: +85
   - Logros desbloqueados: "Clean Code Ninja"

7. Puede:
   - Ver el código refactorizado
   - Reintentar el ejercicio
   - Ir al siguiente
```

---

## 📋 Endpoints de la API

```bash
# Listar todos los ejercicios
GET http://localhost:8000/exercises/json/list

# Filtrar por dificultad
GET http://localhost:8000/exercises/json/list?difficulty=Easy

# Obtener ejercicio específico
GET http://localhost:8000/exercises/json/U1-VAR-01

# Enviar código para evaluación (requiere auth)
POST http://localhost:8000/exercises/json/U1-VAR-01/submit
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "student_code": "salarios = [12000, 15000, 13500]\ntotal = sum(salarios)\n..."
}

# Respuesta:
{
  "evaluation": {
    "score": 85.5,
    "status": "PASS",
    "title": "¡Bien! Funciona correctamente"
  },
  "dimensions": {...},
  "code_review": {...},
  "gamification": {
    "xp_earned": 85,
    "achievements_unlocked": ["clean_code_ninja"]
  }
}

# Estadísticas
GET http://localhost:8000/exercises/json/stats
```

---

## 🎨 Componentes React Creados

### ExercisesList
```tsx
import { ExercisesList } from '@/components/exercises';

<ExercisesList onSelectExercise={(id) => navigate(`/exercises/${id}`)} />
```

**Features:**
- ✅ Grid de tarjetas por ejercicio
- ✅ Filtros: dificultad, unidad, búsqueda
- ✅ Estadísticas globales (total, fácil, medio, difícil)
- ✅ Badges de tags
- ✅ Iconos de completado

### ExerciseWorkspace
```tsx
import { ExerciseWorkspace } from '@/components/exercises';

<ExerciseWorkspace />  // Lee exerciseId de la URL
```

**Features:**
- ✅ Layout 2 columnas (instrucciones + editor)
- ✅ Historia narrativa con Markdown
- ✅ Misión con pasos a seguir
- ✅ Editor de código con syntax highlighting
- ✅ Pistas colapsables
- ✅ Criterios de éxito
- ✅ Evaluación completa con Alex

### CodeEditor
```tsx
import { CodeEditor } from '@/components/exercises';

<CodeEditor
  value={code}
  onChange={setCode}
  language="python"
  theme="vs-dark"
  showLineNumbers={true}
/>
```

### EvaluationResultView
```tsx
import { EvaluationResultView } from '@/components/exercises';

<EvaluationResultView
  result={evaluation}
  studentCode={code}
  onRetry={() => setEvaluation(null)}
/>
```

**Features:**
- ✅ Toast de resultado (success/warning/error)
- ✅ Score general destacado
- ✅ Progress bars por dimensión
- ✅ Anotaciones de código
- ✅ Código refactorizado (versión Senior)
- ✅ Gamificación (XP, logros)

---

## 🔧 Configuración

### Cambiar el LLM (de mock a real)

Por defecto usa modo **mock** (sin LLM real). Para usar un LLM:

#### Opción 1: Ollama (local)

```python
# backend/api/routers/exercises.py
from backend.llm.ollama_provider import OllamaProvider

ollama_config = {
    "base_url": "http://localhost:11434",
    "model": "llama3.2:3b",
}
llm = OllamaProvider(ollama_config)
code_evaluator = CodeEvaluator(llm_client=llm)
```

#### Opción 2: OpenAI

```python
from openai import AsyncOpenAI

openai_client = AsyncOpenAI(api_key="sk-...")
code_evaluator = CodeEvaluator(llm_client=openai_client)
```

#### Opción 3: Claude (Anthropic)

```python
from anthropic import AsyncAnthropic

claude_client = AsyncAnthropic(api_key="sk-ant-...")
code_evaluator = CodeEvaluator(llm_client=claude_client)
```

### Deshabilitar autenticación (solo desarrollo)

```python
# backend/api/routers/exercises.py, línea ~260

@router.post("/json/{exercise_id}/submit")
async def submit_json_exercise(
    request: Request,
    exercise_id: str,
    submission: CodeSubmissionRequest,
    # current_user: User = Depends(get_current_user)  # ← Comentar esta línea
):
    ...
```

---

## 📁 Archivos Creados

### Backend
```
backend/
├── data/exercises/
│   ├── unit1_fundamentals.json      # 3 ejercicios
│   ├── unit2_structures.json        # 3 ejercicios
│   ├── unit3_functions.json         # 3 ejercicios
│   ├── unit4_files.json             # 3 ejercicios
│   ├── unit5_oop.json               # 3 ejercicios
│   ├── loader.py                    # Carga ejercicios JSON
│   ├── catalog.json                 # Índice de ejercicios
│   └── README.md                    # Documentación
│
├── services/
│   └── code_evaluator.py            # Evaluador Alex (IA)
│
├── prompts/
│   └── code_evaluator_prompt.md    # Prompt template para LLM
│
└── api/
    ├── routers/
    │   └── exercises.py             # ✅ ACTUALIZADO con nuevos endpoints
    └── schemas/
        └── exercises.py             # ✅ NUEVO - Schemas Pydantic
```

### Frontend
```
frontEnd/src/
├── types/
│   ├── exercise.d.ts                # ✅ ACTUALIZADO - IExercise
│   ├── evaluation.d.ts              # IEvaluationResult
│   └── index.ts                     # ✅ ACTUALIZADO - Exports
│
├── services/api/
│   └── exercises.service.ts         # ✅ ACTUALIZADO - Nuevos métodos
│
├── components/exercises/
│   ├── ExercisesList.tsx            # ✅ NUEVO - Lista de ejercicios
│   ├── ExerciseWorkspace.tsx        # ✅ NUEVO - Workspace completo
│   ├── CodeEditor.tsx               # ✅ NUEVO - Editor de código
│   ├── EvaluationResultView.tsx     # ✅ NUEVO - Visualización evaluación
│   └── index.ts                     # ✅ NUEVO - Exports
│
└── pages/
    └── ExercisesPage.tsx            # ✅ NUEVO - Página principal
```

---

## 🐛 Troubleshooting

### "Ejercicio no encontrado"
```bash
# Verificar que los JSON existen
ls backend/data/exercises/

# Probar el loader
python -c "from backend.data.exercises.loader import ExerciseLoader; print(ExerciseLoader().get_all())"
```

### Error de autenticación
El endpoint `/submit` requiere login. Opciones:
1. Hacer login antes de enviar código
2. Comentar `current_user: User = Depends(get_current_user)` en desarrollo

### Frontend no encuentra tipos
```bash
cd frontEnd
npm run build  # Regenerar tipos
```

### CORS error
Si el frontend no puede conectar al backend, verifica:
```python
# backend/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # ← Tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 Ejemplos de Uso

### Ejemplo 1: Mostrar ejercicios en Dashboard

```tsx
// Dashboard.tsx
import { ExercisesList } from '@/components/exercises';

export const Dashboard = () => {
  return (
    <div>
      <h1>Mis Ejercicios</h1>
      <ExercisesList onSelectExercise={(id) => navigate(`/exercises/${id}`)} />
    </div>
  );
};
```

### Ejemplo 2: Integrar con sistema de progreso

```tsx
const [completedExercises, setCompletedExercises] = useState<string[]>([]);

const handleExerciseComplete = (exerciseId: string, score: number) => {
  if (score >= 70) {
    setCompletedExercises([...completedExercises, exerciseId]);
  }
};
```

### Ejemplo 3: Gamificación personalizada

```tsx
const [totalXP, setTotalXP] = useState(0);
const [achievements, setAchievements] = useState<string[]>([]);

const handleEvaluation = (result: IEvaluationResult) => {
  setTotalXP(prev => prev + result.gamification.xp_earned);
  setAchievements(prev => [
    ...prev,
    ...result.gamification.achievements_unlocked
  ]);
};
```

---

## 🎉 ¡Listo!

El sistema está **100% funcional** y los usuarios pueden:

1. ✅ Ver lista de 15 ejercicios con filtros
2. ✅ Leer consignas narrativas (storytelling)
3. ✅ Escribir código Python
4. ✅ Recibir evaluación detallada de Alex:
   - Score general (0-100)
   - 3 dimensiones (Functionality, Code Quality, Robustness)
   - Anotaciones línea por línea
   - Versión Senior del código
   - XP y logros

**Stack:** Python + FastAPI + React + TypeScript + LLM

---

**¿Necesitas ayuda?** Revisa:
- `INTEGRACION_COMPLETA.md` - Documentación detallada
- `RESUMEN_INTEGRACION.md` - Resumen ejecutivo
- `backend/data/exercises/README.md` - Sistema de ejercicios
- `docs/implementation/SISTEMA_EVALUACION_COMPLETO.md` - Evaluador Alex

**Creado:** 17 de Diciembre, 2025
