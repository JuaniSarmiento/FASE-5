# Plan de Implementación: Entrenador Digital - Ejercicios Secuenciales

**Fecha de Creación:** 27 de Diciembre 2025
**Autor:** Sistema de Planificación Activia1
**Estado:** En Implementación
**Prioridad:** Alta

---

## Índice
1. [Visión General](#visión-general)
2. [Estado Actual del Sistema](#estado-actual-del-sistema)
3. [Objetivos del Plan](#objetivos-del-plan)
4. [Arquitectura Propuesta](#arquitectura-propuesta)
5. [Fases de Implementación](#fases-de-implementación)
6. [Cronograma de Checks](#cronograma-de-checks)
7. [Consideraciones Técnicas](#consideraciones-técnicas)
8. [Referencias](#referencias)

---

## Visión General

El **Entrenador Digital** es un módulo del sistema Activia1 que permite a los estudiantes practicar programación en modo examen, con:
- Ejercicios autocorregibles mediante tests automáticos
- Feedback pedagógico generado por IA (CodeEvaluator "Alex")
- Sistema de pistas graduales con penalización
- Trazabilidad N4 de cada intento de solución
- Evaluación procesual (no solo resultado final)

Este plan documenta la corrección y mejora del Entrenador Digital para incluir:
1. Nomenclatura correcta: "Lenguaje" en lugar de "Materia"
2. Navegación jerárquica: Lenguaje → Lección → Ejercicios
3. 10 ejercicios de "Estructuras Secuenciales" en Python con tests automáticos

---

## Estado Actual del Sistema

### Backend
**Archivos principales:**
- `backend/api/routers/training.py` - Endpoints del entrenador
- `backend/database/models.py` - Modelos ORM (SubjectDB, ExerciseDB, ExerciseHintDB, ExerciseTestDB, ExerciseAttemptDB)
- `backend/scripts/seed_exercises.py` - Script de carga de ejercicios
- `backend/services/code_evaluator.py` - Evaluador de código con IA

**Modelos de datos:**
```python
SubjectDB:
  - code: str (PK) - "PROG1", "PROG2"
  - name: str - "Programación 1"
  - language: str - "python", "java"  ← YA EXISTE
  - total_units: int - Cantidad de lecciones

ExerciseDB:
  - id: str (PK)
  - subject_code: str (FK)
  - unit: int - Número de lección (1-7)  ← YA EXISTE
  - title: str
  - difficulty: str
  - mission_markdown: text - Consigna
  - starter_code: text - Código inicial
  - solution_code: text - Solución (no visible para estudiantes)
```

**Endpoints actuales:**
- `GET /training/materias` - Lista materias con temas
- `POST /training/iniciar` - Inicia sesión de entrenamiento
- `POST /training/submit-ejercicio` - Evalúa código (tests + IA)
- `POST /training/pista` - Solicita pista con penalización

### Frontend
**Archivos principales:**
- `frontEnd/src/pages/TrainingPage.tsx` - Selector de materia/tema
- `frontEnd/src/pages/TrainingExamPage.tsx` - Página de examen
- `frontEnd/src/services/api/training.service.ts` - Servicio API

**Flujo actual:**
1. Usuario selecciona "Materia" (dice "materia" pero debería decir "lenguaje")
2. Usuario selecciona "Tema" (muestra ejercicios individuales, falta nivel de "lección")
3. Usuario hace clic en "Iniciar Entrenamiento"

### Problemas Identificados
❌ **P1:** Frontend dice "Selecciona una Materia" cuando debería decir "Selecciona un Lenguaje"
❌ **P2:** Falta nivel intermedio de "Lección" (ej: Secuenciales, Condicionales, Bucles)
❌ **P3:** No existen ejercicios de "Estructuras Secuenciales" en la base de datos
❌ **P4:** Los tests automáticos necesitan ser creados para cada ejercicio

---

## Objetivos del Plan

### Objetivos Principales
1. ✅ **Corregir nomenclatura:** Cambiar "Materia" → "Lenguaje" en toda la interfaz
2. ✅ **Agregar navegación de 3 niveles:** Lenguaje → Lección → Ejercicios
3. ✅ **Crear 10 ejercicios de Secuenciales** con:
   - Consignas claras basadas en `SecuencialesCo.txt`
   - 4 pistas graduales por ejercicio (de `PistasSecuenciales.txt`)
   - 3-5 tests automáticos por ejercicio
   - Rúbricas de evaluación (de `rubricaSecuenciales.pdf`)

### Objetivos Secundarios
- Mantener compatibilidad con sistema de evaluación existente (tests + IA)
- Garantizar trazabilidad N4 de todos los intentos
- Documentar el sistema para futuros mantenedores

---

## Arquitectura Propuesta

### Estructura de Datos (3 Niveles)

```
Lenguaje (Language)
  ├── Python 3.11+
  │   ├── Lección 1: Estructuras Secuenciales
  │   │   ├── Ejercicio 1: Hola Mundo (12 pts)
  │   │   ├── Ejercicio 2: Saludo Personalizado (16 pts)
  │   │   ├── ...
  │   │   └── Ejercicio 10: Promedio de Tres Números (24 pts)
  │   ├── Lección 2: Estructuras Condicionales
  │   └── Lección 3: Bucles
  └── Java 17
      └── Lección 1: Fundamentos de Java
```

### Flujo de Usuario

```
┌─────────────────────────────────────────────────────────────┐
│ 1. TrainingPage - Selección de Lenguaje                    │
│    [Dropdown: Python | Java | JavaScript]                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. TrainingPage - Selección de Lección                     │
│    [Grid Cards: Secuenciales | Condicionales | Bucles]     │
│    Cada card muestra: nombre, descripción, # ejercicios    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. TrainingPage - Botón "Iniciar Entrenamiento"            │
│    Muestra resumen: 10 ejercicios, 204 pts, 120 min        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. TrainingExamPage - Examen en tiempo real                │
│    - Editor Monaco con starter_code                         │
│    - Temporizador de cuenta regresiva                       │
│    - Botón "Solicitar Pista" (penalización gradual)        │
│    - Botón "Enviar Código"                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Evaluación Automática                                    │
│    1. Ejecutar tests automáticos (execute_python_code)     │
│    2. Evaluar con IA (CodeEvaluator "Alex")                │
│    3. Guardar intento en ExerciseAttemptDB (N4)            │
│    4. Calcular nota final (tests + IA - penalizaciones)    │
│    5. Mostrar feedback + siguiente ejercicio                │
└─────────────────────────────────────────────────────────────┘
```

### Sistema de Evaluación

**Flujo de Evaluación:**
```python
POST /training/submit-ejercicio
  ↓
1. execute_python_code(codigo_estudiante, tests)
   → Ejecuta en sandbox seguro con resource limits
   → Retorna: exit_code, stdout, stderr, tests_passed
  ↓
2. CodeEvaluator.evaluate(exercise, codigo, sandbox_result)
   → Llama a LLM (Ollama/Phi-3) con prompt de "Alex"
   → Retorna: score (0-100), dimensions, code_review, achievements
  ↓
3. Calcular nota final:
   - tests_score = (tests_passed / tests_total) * 40%
   - ai_score = evaluation.score * 60%
   - penalty = hints_used_penalty
   - final_score = tests_score + ai_score - penalty
  ↓
4. ExerciseAttemptRepository.create()
   → Persiste en PostgreSQL para trazabilidad N4
  ↓
5. Retornar feedback al estudiante
```

**Sistema de Pistas:**
- Pista 1: -5 puntos
- Pista 2: -10 puntos
- Pista 3: -15 puntos
- Pista 4: -20 puntos
- **Total máximo de penalización:** -50 puntos

**Nota mínima de aprobación:** 60/100 (6.0/10)

---

## Fases de Implementación

### FASE 1: Corrección de Nomenclatura en Frontend
**Duración estimada:** 30 minutos
**Archivos modificados:** 1

**Tareas:**
- [ ] 1.1: Cambiar labels en TrainingPage.tsx
  - "Selecciona una Materia" → "Selecciona un Lenguaje"
  - "Elige una materia..." → "Elige un lenguaje..."
  - Actualizar comentarios JSDoc

**Checks:**
- ✅ 1.1: TrainingPage muestra "Lenguaje" en todos los textos visibles

---

### FASE 2: Reestructuración del Backend
**Duración estimada:** 2 horas
**Archivos modificados:** 1 (training.py)

**Tareas:**
- [ ] 2.1: Crear nuevos schemas Pydantic
  - LenguajeInfo (language, nombre_completo, lecciones[])
  - LeccionInfo (id, nombre, descripcion, unit_number, ejercicios[], total_puntos)
  - EjercicioInfo (id, titulo, dificultad, tiempo_estimado_min, puntos)

- [ ] 2.2: Modificar endpoint GET /training/materias
  - Consultar SubjectRepository
  - Agrupar ejercicios por (language, unit)
  - Retornar estructura jerárquica

- [ ] 2.3: Modificar endpoint POST /training/iniciar
  - Cambiar request: materia_codigo → language, tema_id → unit_number
  - Cargar ejercicios filtrados por language + unit

**Checks:**
- ✅ 2.1: Schemas definidos correctamente
- ✅ 2.2: GET /training/materias retorna estructura Lenguaje → Lecciones → Ejercicios
- ✅ 2.3: POST /training/iniciar funciona con language + unit_number

---

### FASE 3: Actualización del Frontend - Selector de Lección
**Duración estimada:** 2 horas
**Archivos modificados:** 2 (TrainingPage.tsx, training.service.ts)

**Tareas:**
- [ ] 3.1: Actualizar interfaces TypeScript
  - Crear LenguajeInfo, LeccionInfo, EjercicioInfo
  - Actualizar training.service.ts

- [ ] 3.2: Modificar TrainingPage.tsx
  - Cambiar estado: materias → lenguajes, materiaSeleccionada → lenguajeSeleccionado
  - Agregar estado: leccionSeleccionada
  - Implementar flujo de 3 pasos (Lenguaje → Lección → Botón)
  - Grid de lecciones con cards visuales

- [ ] 3.3: Actualizar llamadas API
  - Modificar iniciarEntrenamiento() para enviar language + unit_number
  - Actualizar navegación a TrainingExamPage

**Checks:**
- ✅ 3.1: Interfaces TypeScript alineadas con backend
- ✅ 3.2: Flujo de 3 pasos implementado correctamente
- ✅ 3.3: Navegación funciona con nuevos parámetros

---

### FASE 4: Creación de Tests Automáticos
**Duración estimada:** 3 horas
**Archivos creados:** 0 (solo análisis)

**Tareas:**
- [ ] 4.1: Analizar requerimientos de tests por ejercicio
  - Ejercicio 1 (Hola Mundo): 1 test de stdout
  - Ejercicio 2 (Saludo): 2 tests con inputs simulados
  - Ejercicio 3 (Datos): 1 test con 4 inputs
  - Ejercicio 4 (Círculo): 2 tests con cálculos matemáticos
  - Ejercicio 5 (Segundos): 2 tests de conversión
  - Ejercicio 6 (Tabla): 1 test de formato multilínea
  - Ejercicio 7 (Operaciones): 1 test con 4 operaciones
  - Ejercicio 8 (IMC): 1 test de fórmula
  - Ejercicio 9 (Temperatura): 2 tests de conversión
  - Ejercicio 10 (Promedio): 1 test de cálculo

- [ ] 4.2: Definir estrategia de validación
  - Tests con input(): usar simulación de stdin
  - Tests de cálculo: validar stdout con regex
  - Tests ocultos vs visibles (ratio 2:1)

**Checks:**
- ✅ 4.1: Tests documentados para 10 ejercicios
- ✅ 4.2: Estrategia de validación definida

---

### FASE 5: Seed de Base de Datos
**Duración estimada:** 4 horas
**Archivos modificados:** 1 (seed_exercises.py)

**Tareas:**
- [ ] 5.1: Preparar estructura de 10 ejercicios
  - Crear diccionarios con todos los campos (id, title, difficulty, mission, etc.)
  - Asignar puntajes según rubrica (12, 16, 16, 24, 20, 20, 28, 24, 20, 24 pts)
  - Definir starter_code para cada ejercicio
  - Incluir solution_code (no visible)

- [ ] 5.2: Crear 40 pistas (4 por ejercicio)
  - Extraer de PistasSecuenciales.txt
  - Asignar penalizaciones (5, 10, 15, 20 pts)
  - Formatear como ExerciseHintDB

- [ ] 5.3: Crear 30-50 tests automáticos
  - 3-5 tests por ejercicio
  - Mezcla de visibles (33%) y ocultos (67%)
  - Tests con input() simulado para ejercicios interactivos
  - Tests de regex para ejercicios de cálculo

- [ ] 5.4: Asociar rúbricas estándar
  - Usar rúbrica estándar del sistema (Funcionalidad 40%, Calidad 30%, Robustez 30%)
  - CodeEvaluator usará criterios del PDF como guía interna

- [ ] 5.5: Ejecutar seed y verificar
  - Correr: `python -m backend.scripts.seed_exercises`
  - Verificar counts en PostgreSQL
  - Validar que no hay duplicados

**Checks:**
- ✅ 5.1: 10 ejercicios con estructura completa
- ✅ 5.2: 40 pistas creadas
- ✅ 5.3: 30-50 tests creados
- ✅ 5.4: Rúbricas asociadas
- ✅ 5.5: Datos insertados en PostgreSQL correctamente

---

### FASE 6: Pruebas de Integración Completa
**Duración estimada:** 2 horas
**Archivos modificados:** 0 (solo testing)

**Tareas:**
- [ ] 6.1: Prueba de flujo frontend
  - Abrir /training
  - Seleccionar Python
  - Seleccionar Secuenciales
  - Iniciar entrenamiento

- [ ] 6.2: Prueba de ejercicio individual
  - Resolver SEC-01 (Hola Mundo)
  - Verificar tests automáticos
  - Verificar feedback de IA
  - Verificar cálculo de nota

- [ ] 6.3: Prueba de sistema de pistas
  - Solicitar 4 pistas en un ejercicio
  - Verificar penalizaciones acumulativas
  - Verificar descuento en nota final

- [ ] 6.4: Prueba de tests con inputs
  - Ejercicio SEC-02 con input()
  - Verificar simulación de stdin
  - Verificar validación de stdout

- [ ] 6.5: Prueba de trazabilidad N4
  - Verificar inserción en exercise_attempts
  - Verificar campos: submitted_code, score, hints_used, ai_feedback

**Checks:**
- ✅ 6.1: Flujo frontend completo funcional
- ✅ 6.2: Ejercicio individual funciona (tests + IA)
- ✅ 6.3: Sistema de pistas correcto
- ✅ 6.4: Tests con input() validados
- ✅ 6.5: Trazabilidad N4 persistiendo

---

### FASE 7: Documentación y Ajustes Finales
**Duración estimada:** 1 hora
**Archivos modificados:** 2 (CLAUDE.md, nuevo README)

**Tareas:**
- [ ] 7.1: Actualizar CLAUDE.md
  - Agregar sección de Entrenador Digital
  - Documentar estructura Lenguaje → Lección → Ejercicios
  - Ejemplos de uso de endpoints

- [ ] 7.2: Crear README del entrenador (este documento)
  - Visión general
  - Flujo de usuario
  - Arquitectura
  - Cómo agregar ejercicios

- [ ] 7.3: Ajustes de UX/UI
  - Animaciones de transición
  - Mensajes de error claros
  - Toast de confirmación al usar pistas

**Checks:**
- ✅ 7.1: CLAUDE.md actualizado
- ✅ 7.2: README completo
- ✅ 7.3: UX/UI mejorada

---

## Cronograma de Checks

**Total de Checks:** 22

### Por Fase
- FASE 1: 1 check
- FASE 2: 3 checks
- FASE 3: 3 checks
- FASE 4: 2 checks
- FASE 5: 5 checks
- FASE 6: 5 checks
- FASE 7: 3 checks

### Orden de Validación
1. ✅ Frontend muestra "Lenguaje" (FASE 1)
2. ✅ Backend retorna estructura jerárquica (FASE 2)
3. ✅ Frontend implementa selector de 3 niveles (FASE 3)
4. ✅ Tests documentados (FASE 4)
5. ✅ Datos cargados en DB (FASE 5)
6. ✅ Sistema funciona end-to-end (FASE 6)
7. ✅ Documentación completa (FASE 7)

---

## Consideraciones Técnicas

### Sistema de Evaluación Automática

**Sandbox de Seguridad:**
```python
# Imports bloqueados:
DANGEROUS_IMPORTS = ['os', 'subprocess', 'sys', 'shutil', 'socket', ...]

# Patterns bloqueados:
DANGEROUS_PATTERNS = ['__import__', 'exec(', 'eval(', 'open(', ...]

# Resource limits (Linux/Mac):
- Memory: 50MB
- CPU time: timeout + 1s
- File creation: 0
- Processes: 0
```

**Ejecución de Tests:**
```python
# Código del estudiante se ejecuta con:
python -I -c "restricted_code_wrapper" < input.txt

# Se captura:
- exit_code (0 = éxito, !=0 = error)
- stdout (salida del programa)
- stderr (errores)
- execution_time_ms
```

**Validación de Tests:**
```python
# Test simple (sin input):
{
  "input": "",
  "expected": "Hola Mundo!",  # Match exacto en stdout
  "is_hidden": False
}

# Test con input (simulado):
{
  "input": "Marcos\n",  # Se inyecta como stdin
  "expected": ".*Hola Marcos.*",  # Regex match en stdout
  "is_hidden": False
}

# Test de cálculo:
{
  "input": "5\n",  # Radio del círculo
  "expected": ".*78\\.5.*",  # Área ~78.54
  "is_hidden": True  # No visible para estudiante
}
```

### Integración con CodeEvaluator (IA)

**Prompt Template:** `backend/prompts/code_evaluator_prompt.md`

**Variables reemplazadas:**
- `{{exercise_title}}` - Título del ejercicio
- `{{exercise_mission}}` - Consigna
- `{{student_code}}` - Código del estudiante
- `{{sandbox_stdout}}` - Salida capturada
- `{{sandbox_stderr}}` - Errores capturados
- `{{rubric_json}}` - Criterios de evaluación

**Respuesta de Alex (IA):**
```json
{
  "evaluation": {
    "score": 85,  // 0-100
    "status": "PASS",
    "summary_markdown": "Excelente trabajo...",
    "toast_message": "¡Aprobado! 85/100"
  },
  "dimensions": {
    "functionality": { "score": 9, "comment": "..." },
    "code_quality": { "score": 8, "comment": "..." },
    "robustness": { "score": 7, "comment": "..." }
  },
  "code_review": {
    "highlighted_lines": [
      { "line_number": 5, "severity": "info", "message": "..." }
    ],
    "refactoring_suggestion": "..."
  },
  "gamification": {
    "xp_earned": 85,
    "achievements_unlocked": ["Clean Code Ninja"]
  }
}
```

### Trazabilidad N4

**ExerciseAttemptDB (PostgreSQL):**
```python
{
  "id": "uuid",
  "exercise_id": "SEC-01",
  "student_id": "user_123",
  "session_id": "training_session_xyz",
  "submitted_code": "print('Hola Mundo!')",
  "tests_passed": 1,
  "tests_total": 1,
  "score": 9.5,  # Escala 0-10
  "status": "PASS",
  "execution_time_ms": 45,
  "stdout": "Hola Mundo!\n",
  "stderr": "",
  "ai_feedback_summary": "Excelente primer programa...",
  "ai_feedback_detailed": "Tu código cumple perfectamente...",
  "ai_suggestions": ["Podrías agregar comentarios..."],
  "rubric_evaluation": {
    "criteria": [...],
    "total_score_rubric": 95,
    "penalty_from_hints": 10,
    "final_score": 85
  },
  "hints_used": 2,
  "penalty_applied": 15,
  "attempt_number": 3,
  "submitted_at": "2025-12-27T10:30:00Z"
}
```

**Utilidad para analytics:**
- ¿Cuántos intentos necesitó el estudiante?
- ¿Qué errores cometió repetidamente?
- ¿En qué ejercicios se traba?
- ¿Usa muchas pistas o resuelve solo?

---

## Referencias

### Documentos Fuente
- `PARA HACER EJERCICIOS/SecuencialesCo.txt` - Soluciones completas de los 10 ejercicios
- `PARA HACER EJERCICIOS/PistasSecuenciales.txt` - 4 pistas graduales por ejercicio
- `PARA HACER EJERCICIOS/rubricaSecuenciales.pdf` - Criterios de evaluación detallados
- `PARA HACER EJERCICIOS/ComoHacerlo.txt` - Fundamentos pedagógicos

### Código Relacionado
- `backend/api/routers/training.py` - Router del entrenador digital
- `backend/api/routers/exercises.py` - Router de ejercicios JSON (sistema dual)
- `backend/services/code_evaluator.py` - Evaluador con IA "Alex"
- `backend/prompts/code_evaluator_prompt.md` - Prompt template
- `backend/database/models.py` - Modelos ORM
- `backend/scripts/seed_exercises.py` - Script de carga de datos

### Documentación del Sistema
- `activia1-main/CLAUDE.md` - Guía general del proyecto
- `docs/Misagentes/integrador.md` - Sistema de 6 agentes de IA
- `docs/api/README_API.md` - Referencia de API
- `GUIA_ESTUDIANTE.md` - Guía para estudiantes

---

## Notas de Implementación

### Decisiones de Diseño

**1. ¿Por qué tests automáticos + IA?**
- **Tests automáticos:** Validación objetiva de funcionalidad (¿funciona?)
- **IA (CodeEvaluator):** Feedback pedagógico sobre calidad, estilo, mejores prácticas (¿es buen código?)
- **Resultado:** Evaluación integral (resultado + proceso)

**2. ¿Por qué no crear rúbricas personalizadas por ejercicio?**
- Las rúbricas del PDF son excelentes como **guía pedagógica**
- El sistema usa rúbricas estándar (Funcionalidad, Calidad, Robustez)
- CodeEvaluator (Alex) aplica los criterios del PDF internamente en su prompt
- Esto simplifica la DB y mantiene flexibilidad

**3. ¿Por qué estructura de 3 niveles?**
- **Nivel 1 (Lenguaje):** Python, Java, JavaScript → Escalabilidad
- **Nivel 2 (Lección/Unit):** Secuenciales, Condicionales, Bucles → Organización pedagógica
- **Nivel 3 (Ejercicio):** Hola Mundo, Saludo, etc. → Práctica granular
- **Beneficio:** Navegación intuitiva + fácil expansión del contenido

### Extensiones Futuras

**Lección 2: Estructuras Condicionales**
- 10-15 ejercicios con if/elif/else
- Tests de validación de lógica condicional
- Mismo modelo de pistas + evaluación IA

**Lección 3: Bucles (for/while)**
- 10-15 ejercicios con iteración
- Tests de validación de iteración correcta
- Detección de bucles infinitos en sandbox

**Análisis de Aprendizaje:**
- Dashboard de analytics para docentes
- Identificación de patrones de error comunes
- Recomendaciones personalizadas por estudiante

**Gamificación:**
- Sistema de logros (badges)
- Leaderboard por lección
- Desafíos especiales con recompensas

---

**Fin del documento**
