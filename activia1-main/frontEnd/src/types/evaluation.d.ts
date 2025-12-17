/**
 * Tipos TypeScript para el Sistema de Evaluación de Código
 * 
 * Este archivo define las interfaces para la respuesta del evaluador "Alex".
 * El evaluador recibe código del estudiante y retorna un análisis completo
 * con score, feedback pedagógico, anotaciones de código y gamificación.
 * 
 * @module evaluation.d.ts
 * @see backend/prompts/code_evaluator_prompt.md
 */

/**
 * Estado final de la evaluación
 */
export type EvaluationStatus = 'PASS' | 'FAIL' | 'WARNING';

/**
 * Tipo de notificación toast para la UI
 */
export type ToastType = 'success' | 'error' | 'warning';

/**
 * Severidad de una anotación en el código
 */
export type Severity = 'info' | 'warning' | 'error';

/**
 * Puntuación de una dimensión de evaluación (0-10)
 */
export interface IDimensionScore {
  /** Puntuación 0-10 */
  score: number;
  
  /** Comentario específico sobre esta dimensión */
  comment: string;
}

/**
 * Anotación/comentario sobre una línea específica del código
 * Se muestra en el editor con highlight
 */
export interface ICodeAnnotation {
  /** Número de línea (1-indexed) */
  line_number: number;
  
  /** Nivel de severidad del issue */
  severity: Severity;
  
  /** Mensaje descriptivo del problema o sugerencia */
  message: string;
}

/**
 * Resultado completo de la evaluación de código
 * Esta es la interfaz principal que devuelve el evaluador Alex
 */
export interface IEvaluationResult {
  /** Información general de la evaluación */
  evaluation: {
    /** Puntuación total 0-100 */
    score: number;
    
    /** Estado final (pasa/falla/advertencia) */
    status: EvaluationStatus;
    
    /** Título corto del feedback (ej: "Lógica correcta, pero frágil") */
    title: string;
    
    /** 
     * Resumen narrativo en Markdown (2-3 líneas).
     * Usa negritas para conceptos clave.
     */
    summary_markdown: string;
    
    /** Tipo de toast para notificación UI */
    toast_type: ToastType;
    
    /** Mensaje flash de 1 línea para toast */
    toast_message: string;
  };
  
  /** Puntuaciones desglosadas por dimensión */
  dimensions: {
    /** ¿Cumple la misión? ¿Funciona correctamente? */
    functionality: IDimensionScore;
    
    /** ¿Código limpio, naming, estructura? */
    code_quality: IDimensionScore;
    
    /** ¿Maneja errores, edge cases? */
    robustness: IDimensionScore;
  };
  
  /** Code review detallado */
  code_review: {
    /** Anotaciones línea por línea */
    highlighted_lines: ICodeAnnotation[];
    
    /** 
     * Código refactorizado por un Senior (opcional).
     * Solo se incluye si hay margen significativo de mejora.
     */
    refactoring_suggestion?: string;
  };
  
  /** Sistema de gamificación */
  gamification: {
    /** XP ganados (basado en score) */
    xp_earned: number;
    
    /** Lista de logros desbloqueados en esta evaluación */
    achievements_unlocked: string[];
  };
}

/**
 * Request para evaluar un ejercicio
 */
export interface IEvaluationRequest {
  /** ID del ejercicio */
  exercise_id: string;
  
  /** Código del estudiante */
  student_code: string;
  
  /** Output del sandbox (stdout) */
  sandbox_stdout?: string;
  
  /** Errores del sandbox (stderr) */
  sandbox_stderr?: string;
  
  /** Exit code del sandbox (0 = success) */
  sandbox_exit_code?: number;
  
  /** Tests pasados */
  tests_passed?: number;
  
  /** Total de tests */
  tests_total?: number;
}

/**
 * Rúbrica de evaluación configurable
 */
export interface IEvaluationRubric {
  /** Configuración de functionality */
  functionality: {
    weight: number; // Peso 0-1
    max_score: number; // Máximo 10
  };
  
  /** Configuración de code_quality */
  code_quality: {
    weight: number;
    max_score: number;
  };
  
  /** Configuración de robustness */
  robustness: {
    weight: number;
    max_score: number;
  };
}

/**
 * Historial de evaluaciones del estudiante
 */
export interface IEvaluationHistory {
  /** ID de la evaluación */
  id: string;
  
  /** ID del ejercicio */
  exercise_id: string;
  
  /** Timestamp */
  evaluated_at: string;
  
  /** Score obtenido */
  score: number;
  
  /** Estado */
  status: EvaluationStatus;
  
  /** XP ganados */
  xp_earned: number;
  
  /** Logros desbloqueados */
  achievements: string[];
}

/**
 * Progreso del estudiante (agregado)
 */
export interface IStudentProgress {
  /** Total XP acumulado */
  total_xp: number;
  
  /** Nivel actual (calculado desde XP) */
  level: number;
  
  /** XP requerido para siguiente nivel */
  xp_to_next_level: number;
  
  /** Score promedio */
  average_score: number;
  
  /** Total de ejercicios completados */
  exercises_completed: number;
  
  /** Todos los logros desbloqueados */
  all_achievements: string[];
  
  /** Racha de días */
  streak_days: number;
  
  /** Desglose por dimensión */
  dimension_averages: {
    functionality: number;
    code_quality: number;
    robustness: number;
  };
}

/**
 * Logro/Achievement
 */
export interface IAchievement {
  /** ID único del logro */
  id: string;
  
  /** Nombre del logro */
  name: string;
  
  /** Descripción */
  description: string;
  
  /** Icono/emoji */
  icon: string;
  
  /** XP bonus al desbloquear */
  xp_bonus: number;
  
  /** Rareza */
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  
  /** Condición para desbloquear */
  unlock_condition: string;
}

/**
 * Catálogo de logros disponibles
 */
export const ACHIEVEMENTS_CATALOG: IAchievement[] = [
  {
    id: 'first_blood',
    name: 'First Blood',
    description: 'Completaste tu primer ejercicio',
    icon: '🎯',
    xp_bonus: 50,
    rarity: 'common',
    unlock_condition: 'exercises_completed === 1'
  },
  {
    id: 'clean_code_ninja',
    name: 'Clean Code Ninja',
    description: 'Code quality score >= 9',
    icon: '🥋',
    xp_bonus: 100,
    rarity: 'rare',
    unlock_condition: 'code_quality >= 9'
  },
  {
    id: 'error_handler',
    name: 'Error Handler',
    description: 'Manejo correcto de excepciones',
    icon: '🛡️',
    xp_bonus: 75,
    rarity: 'common',
    unlock_condition: 'uses_try_except_correctly'
  },
  {
    id: 'pythonista',
    name: 'Pythonista',
    description: 'Usa features pythonic (comprehensions, f-strings)',
    icon: '🐍',
    xp_bonus: 150,
    rarity: 'epic',
    unlock_condition: 'uses_pythonic_features'
  },
  {
    id: 'defensive_programmer',
    name: 'Defensive Programmer',
    description: 'Valida inputs y maneja edge cases',
    icon: '🛡️',
    xp_bonus: 200,
    rarity: 'epic',
    unlock_condition: 'handles_edge_cases'
  },
  {
    id: 'dry_master',
    name: 'DRY Master',
    description: "Don't Repeat Yourself - código modular",
    icon: '♻️',
    xp_bonus: 100,
    rarity: 'rare',
    unlock_condition: 'no_code_repetition'
  },
  {
    id: 'speed_demon',
    name: 'Speed Demon',
    description: 'Resolviste en < 50% del tiempo estimado',
    icon: '⚡',
    xp_bonus: 150,
    rarity: 'rare',
    unlock_condition: 'completion_time < estimated_time * 0.5'
  },
  {
    id: 'perfectionist',
    name: 'Perfectionist',
    description: 'Score 100/100',
    icon: '💎',
    xp_bonus: 500,
    rarity: 'legendary',
    unlock_condition: 'score === 100'
  }
];
