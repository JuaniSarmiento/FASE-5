/**
 * Servicio para gestión de ejercicios de programación
 * FIX 2.6: Service for backend /exercises endpoints
 * FIX Cortez20: Added proper types instead of 'any'
 */

import { BaseApiService } from './base.service';
import type { SubmissionResult } from '@/types';

/**
 * Exercise response from backend
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
 * ExercisesService - Gestión de ejercicios y submissions
 */
class ExercisesService extends BaseApiService {
  constructor() {
    super('/exercises');
  }

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
