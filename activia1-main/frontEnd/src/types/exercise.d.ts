/**
 * Definición de tipos TypeScript para el sistema de ejercicios de programación.
 * Este archivo mapea EXACTAMENTE la estructura JSON de los ejercicios.
 * 
 * @module exercise.d.ts
 * @description Frontend-ready exercise types para componentes React
 */

/**
 * Nivel de dificultad del ejercicio
 */
export type ExerciseDifficulty = 'Easy' | 'Medium' | 'Hard';

/**
 * Lenguaje de programación del editor
 */
export type EditorLanguage = 'python' | 'javascript' | 'typescript' | 'java' | 'cpp';

/**
 * Metadata del ejercicio - información para Cards y filtros
 */
export interface IExerciseMeta {
  /** Título corto para mostrar en la Card UI */
  title: string;
  
  /** Nivel de dificultad */
  difficulty: ExerciseDifficulty;
  
  /** Tiempo estimado en minutos */
  estimated_time_min?: number;
  
  /** Compatibilidad (algunos usan este nombre) */
  estimated_time_minutes?: number;
  
  /** Puntos XP */
  points?: number;
  
  /** Tags para filtrado y búsqueda */
  tags: string[];
  
  /** Objetivos de aprendizaje */
  learning_objectives?: string[];
}

/**
 * Configuración de UI para el editor de código
 */
export interface IExerciseUIConfig {
  /** Lenguaje del editor Monaco */
  editor_language: EditorLanguage;
  
  /** Tema del editor */
  editor_theme?: string;
  
  /** Mostrar números de línea */
  show_line_numbers?: boolean;
  
  /** Líneas que NO se pueden editar (1-indexed) */
  read_only_lines?: number[];
  
  /** Texto placeholder cuando el editor está vacío */
  placeholder_text?: string;
}

/**
 * Contenido pedagógico del ejercicio (Markdown)
 */
export interface IExerciseContent {
  /** 
   * Historia/contexto del ejercicio en Markdown.
   * Debe renderizarse con ReactMarkdown.
   * Incluye: negritas, listas, bloques de código, LaTeX
   */
  story_markdown: string;
  
  /** 
   * Descripción de la misión/tarea en Markdown.
   * Lista numerada de pasos a seguir
   */
  mission_markdown: string;
  
  /** 
   * Restricciones/reglas del ejercicio.
   * Array de strings para mostrar como bullets
   */
  constraints?: string[];
  
  /**
   * Criterios de éxito (algunos ejercicios usan esto en vez de constraints)
   */
  success_criteria?: string[];
  
  /**
   * Pistas opcionales
   */
  hints?: string[];
}
  constraints: string[];
}

/**
 * Test oculto para validación en sandbox
 */
export interface IHiddenTest {
  /** Input de prueba (puede ser vacío) */
  input: string;
  
  /** 
   * Resultado esperado.
   * Puede ser un valor directo o una expresión booleana
   * Ejemplo: "total == 42600 and promedio == 14200.00"
   */
  expected: string;
}

/**
 * INTERFAZ PRINCIPAL: Ejercicio de programación completo
 * 
 * Esta interfaz mapea EXACTAMENTE el JSON generado.
 * Usar para tipar:
 * - Componentes React (ExerciseCard, ExerciseDetail)
 * - Servicios API (exercisesService)
 * - Redux/Context state
 */
export interface IExercise {
  /** 
   * Identificador único del ejercicio.
   * Formato: "U{unidad}-{CATEGORIA}-{numero}"
   * Ejemplo: "U1-VAR-01", "U4-CSV-01"
   */
  id: string;
  
  /** Metadata para UI */
  meta: IExerciseMeta;
  
  /** Configuración del editor de código */
  ui_config: IExerciseUIConfig;
  
  /** Contenido pedagógico (Markdown) */
  content: IExerciseContent;
  
  /** 
   * Código inicial que ve el estudiante.
   * DEBE ser ejecutable sin errores de sintaxis.
   * Escapar correctamente comillas y caracteres especiales.
   */
  starter_code: string;
  
  /** 
   * Tests ocultos para el sandbox backend.
   * El estudiante NO ve estos tests
   */
  hidden_tests: IHiddenTest[];
}

/**
 * Resultado de la ejecución de un ejercicio
 */
export interface IExerciseSubmissionResult {
  /** Indica si el código pasó todos los tests */
  success: boolean;
  
  /** Output del código ejecutado */
  output: string;
  
  /** Errores de ejecución (si los hay) */
  error?: string;
  
  /** Tests que pasaron */
  passed_tests: number;
  
  /** Total de tests */
  total_tests: number;
  
  /** Puntuación de la IA (0-100) */
  ai_score?: number;
  
  /** Feedback de la IA */
  ai_feedback?: string;
}

/**
 * Request para enviar un ejercicio
 */
export interface IExerciseSubmission {
  /** ID del ejercicio */
  exercise_id: string;
  
  /** Código del estudiante */
  code: string;
  
  /** ID de sesión (opcional) */
  session_id?: string;
}

/**
 * Filtros para listar ejercicios
 */
export interface IExerciseFilters {
  /** Filtrar por dificultad */
  difficulty?: ExerciseDifficulty;
  
  /** Filtrar por tags */
  tags?: string[];
  
  /** Filtrar por lenguaje */
  language?: EditorLanguage;
  
  /** Búsqueda por texto */
  search?: string;
}

/**
 * Estadísticas de progreso del estudiante
 */
export interface IExerciseProgress {
  /** Total de ejercicios completados */
  completed: number;
  
  /** Total de ejercicios disponibles */
  total: number;
  
  /** Porcentaje de completitud */
  percentage: number;
  
  /** Tiempo promedio por ejercicio (minutos) */
  avg_time_min: number;
  
  /** Puntuación promedio */
  avg_score: number;
}
