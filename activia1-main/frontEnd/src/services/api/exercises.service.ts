/**
 * Servicio para gestión de ejercicios de programación
 * FIX 2.6: Service for backend /exercises endpoints
 * FIX Cortez20: Added proper types instead of 'any'
 * NUEVO: Integración con sistema JSON y evaluador Alex
 */

import { BaseApiService } from './base.service';
import type { 
  SubmissionResult,
  IExercise,
  IEvaluationResult,
} from '@/types';

/**
 * Exercise response from backend (Legacy BD)
 * FIX Cortez20: Replaced 'any' with proper interface
 */
export interface Exercise {
  id: string;
  title: string;
  description: string;
  difficulty_level: number;
  starter_code?: string;
  hints?: string[];
  max_score: number;
  time_limit_seconds: number;
  category?: string;
  tags?: string[];
}

/**
 * Exercise list item (Sistema JSON)
 */
export interface ExerciseListItem {
  id: string;
  title: string;
  difficulty: string; // 'easy', 'medium', 'hard'
  estimated_time_minutes: number;
  points: number;
  tags: string[];
  is_completed: boolean;
}

/**
 * Exercise stats
 */
export interface ExerciseStats {
  total_exercises: number;
  by_difficulty: Record<string, number>;
  total_time_hours: number;
  unique_tags: number;
}

/**
 * Submission history item
 * FIX Cortez20: Proper type for submission history
 */
export interface SubmissionHistoryItem {
  id: string;
  exercise_id: string;
  passed_tests: number;
  total_tests: number;
  is_correct: boolean;
  ai_score: number | null;
  submitted_at: string | null;
}

/**
 * Request para enviar código
 */
export interface CodeSubmission {
  exercise_id: string;
  code: string;
}

/**
 * Request para enviar código (Sistema JSON)
 */
export interface CodeSubmissionRequest {
  student_code: string;
}

/**
 * ExercisesService - Gestión de ejercicios y submissions
 */
class ExercisesService extends BaseApiService {
  constructor() {
    super('/exercises');
  }

  // ==========================================================================
  // NUEVOS MÉTODOS - Sistema JSON con Alex
  // ==========================================================================

  /**
   * Listar ejercicios JSON
   * Backend: GET /exercises/json/list
   */
  async listJSON(params?: {
    difficulty?: string;
    unit?: string;
    tag?: string;
    language?: string;
    framework?: string;
  }): Promise<ExerciseListItem[]> {
    const searchParams = new URLSearchParams();
    if (params?.difficulty) searchParams.append('difficulty', params.difficulty);
    if (params?.unit) searchParams.append('unit', params.unit);
    if (params?.tag) searchParams.append('tag', params.tag);
    if (params?.language) searchParams.append('language', params.language);
    if (params?.framework) searchParams.append('framework', params.framework);

    const query = searchParams.toString();
    // FIX: Este endpoint devuelve array directo, no APIResponse wrapper
    const response = await this.client.get<ExerciseListItem[]>(`${this.baseUrl}/json/list${query ? `?${query}` : ''}`);
    return response.data;
  }

  /**
   * Obtener ejercicio JSON por ID
   * Backend: GET /exercises/json/{exercise_id}
   */
  async getJSONById(exerciseId: string): Promise<IExercise> {
    // FIX: Este endpoint devuelve objeto directo, no APIResponse wrapper
    const response = await this.client.get<IExercise>(`${this.baseUrl}/json/${exerciseId}`);
    return response.data;
  }

  /**
   * Enviar código para evaluación con Alex
   * Backend: POST /exercises/json/{exercise_id}/submit
   */
  async submitJSON(
    exerciseId: string,
    code: string
  ): Promise<IEvaluationResult> {
    // FIX: Este endpoint devuelve objeto directo, no APIResponse wrapper
    const response = await this.client.post<IEvaluationResult>(
      `${this.baseUrl}/json/${exerciseId}/submit`,
      { student_code: code }
    );
    return response.data;
  }

  /**
   * Obtener estadísticas de ejercicios JSON
   * Backend: GET /exercises/json/stats
   */
  async getJSONStats(): Promise<ExerciseStats> {
    // FIX: Este endpoint devuelve objeto directo, no APIResponse wrapper
    const response = await this.client.get<ExerciseStats>(`${this.baseUrl}/json/stats`);
    return response.data;
  }

  // ==========================================================================
  // MÉTODOS LEGACY - Sistema de BD (compatibilidad)
  // ==========================================================================

  /**
   * Obtener ejercicio por ID
   * FIX Cortez20: Use Exercise type instead of any
   */
  async getById(exerciseId: string): Promise<Exercise> {
    return this.get<Exercise>(`/${exerciseId}`);
  }

  /**
   * Listar ejercicios disponibles
   * FIX Cortez20: Use Exercise[] type instead of any[]
   */
  async list(params?: { difficulty?: string; category?: string }): Promise<Exercise[]> {
    const searchParams = new URLSearchParams();
    if (params?.difficulty) searchParams.append('difficulty', params.difficulty);
    if (params?.category) searchParams.append('category', params.category);

    const query = searchParams.toString();
    return this.get<Exercise[]>(query ? `?${query}` : '');
  }

  /**
   * Enviar código para evaluación
   * Backend: POST /exercises/submit
   */
  async submit(submission: CodeSubmission): Promise<SubmissionResult> {
    return this.post<SubmissionResult, CodeSubmission>('/submit', submission);
  }

  /**
   * Obtener historial de submissions del usuario
   * Backend: GET /exercises/submissions
   * FIX Cortez20: Use proper types instead of any
   */
  async getSubmissions(): Promise<{
    total: number;
    submissions: SubmissionHistoryItem[];
  }> {
    return this.get<{ total: number; submissions: SubmissionHistoryItem[] }>('/submissions');
  }
}

// Export singleton instance
export const exercisesService = new ExercisesService();
