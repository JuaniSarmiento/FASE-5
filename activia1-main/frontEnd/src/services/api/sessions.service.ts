/**
 * Servicio para gestión de sesiones de aprendizaje
 *
 * Las sesiones representan el contexto de interacción entre un estudiante
 * y el sistema AI-Native para una actividad específica.
 *
 * Modos de sesión:
 * - TUTOR: Interacción con T-IA-Cog (Tutor Cognitivo)
 * - EVALUATOR: Interacción con E-IA-Proc (Evaluador de Procesos)
 * - SIMULATOR: Interacción con S-IA-X (Simuladores Profesionales)
 * - RISK_ANALYST: Interacción con AR-IA (Analista de Riesgos)
 */

import { BaseApiService } from './base.service';
import type {
  SessionCreate,
  SessionUpdate,
  SessionResponse,
  SessionDetailResponse,
  PaginatedResponse,
  PaginationParams,
} from '@/types/api.types';

/**
 * SessionsService - Gestión de sesiones usando base class
 *
 * @example
 * ```typescript
 * // Crear sesión de tutor
 * const session = await sessionsService.create({
 *   student_id: 'student_001',
 *   activity_id: 'prog2_tp1',
 *   mode: SessionMode.TUTOR,
 * });
 *
 * // Crear sesión de simulador
 * const simSession = await sessionsService.create({
 *   student_id: 'student_001',
 *   activity_id: 'prog2_tp1',
 *   mode: SessionMode.SIMULATOR,
 *   simulator_type: 'product_owner',
 * });
 * ```
 */
class SessionsService extends BaseApiService {
  constructor() {
    super('/sessions');
  }

  /**
   * Crear una nueva sesión de aprendizaje
   * @param data - Datos de la sesión (student_id, activity_id, mode, simulator_type?)
   * @returns SessionResponse con el ID de la nueva sesión
   */
  async create(data: SessionCreate): Promise<SessionResponse> {
    return this.post<SessionResponse, SessionCreate>('', data);
  }

  /**
   * Obtener sesión por ID con detalles completos
   * @param sessionId - ID de la sesión
   * @returns SessionDetailResponse con resumen de trazas, riesgos y score de dependencia IA
   */
  async getById(sessionId: string): Promise<SessionDetailResponse> {
    return this.get<SessionDetailResponse>(`/${sessionId}`);
  }

  /**
   * Listar sesiones del estudiante con paginación y filtros
   * FIX 1.1 Cortez12: Added activity_id, mode, status query params
   * @param studentId - ID del estudiante
   * @param filters - Filtros opcionales (activity_id, mode, status)
   * @param pagination - Parámetros de paginación opcionales
   * @returns Lista paginada de sesiones
   */
  async list(
    studentId: string,
    filters?: {
      activity_id?: string;
      mode?: string;
      status?: string;
    },
    pagination?: PaginationParams
  ): Promise<PaginatedResponse<SessionResponse>> {
    const params = new URLSearchParams();
    params.append('student_id', studentId);

    // FIX 1.1 Cortez12: Add optional filters
    if (filters?.activity_id) params.append('activity_id', filters.activity_id);
    if (filters?.mode) params.append('mode', filters.mode);
    if (filters?.status) params.append('status', filters.status);

    // Pagination
    if (pagination?.page) params.append('page', pagination.page.toString());
    if (pagination?.page_size) params.append('page_size', pagination.page_size.toString());

    return this.get<PaginatedResponse<SessionResponse>>(`?${params.toString()}`);
  }

  /**
   * Actualizar sesión (cambiar modo o estado)
   * @param sessionId - ID de la sesión
   * @param data - Datos a actualizar (mode?, status?)
   * @returns SessionResponse actualizada
   */
  async update(sessionId: string, data: SessionUpdate): Promise<SessionResponse> {
    return this.patch<SessionResponse, SessionUpdate>(`/${sessionId}`, data);
  }

  /**
   * Finalizar sesión (marcar como completada)
   * @param sessionId - ID de la sesión
   * @returns SessionResponse con status='completed'
   */
  async end(sessionId: string): Promise<SessionResponse> {
    return this.post<SessionResponse>(`/${sessionId}/end`);
  }

  /**
   * Eliminar sesión (soft delete)
   * @param sessionId - ID de la sesión
   */
  async remove(sessionId: string): Promise<void> {
    return this.delete<void>(`/${sessionId}`);
  }

  /**
   * Crear sesión de tutor socrático V2.0
   * @returns SessionResponse con session_id y mensaje de bienvenida
   */
  async createTutor(): Promise<{ session_id: string; welcome_message: string }> {
    return this.post<{ session_id: string; welcome_message: string }>('/sessions/create-tutor');
  }

  /**
   * Interactuar con el tutor socrático V2.0
   * FIX 1.3 Cortez12: Changed studentProfile to Record<string, any> for flexibility
   * @param sessionId - ID de la sesión
   * @param message - Mensaje del estudiante
   * @param studentProfile - Perfil actual del estudiante (diccionario genérico)
   * @returns Respuesta del tutor con metadata V2.0
   */
  async interact(
    sessionId: string,
    message: string,
    studentProfile?: Record<string, unknown>
  ): Promise<{
    response: string;
    metadata: {
      intervention_type?: string;
      semaforo?: 'verde' | 'amarillo' | 'rojo';
      help_level?: string;
      requires_student_response?: boolean;
      cognitive_events?: string[];
      rule_violations?: string[];
    };
  }> {
    return this.post<{
      response: string;
      metadata: {
        intervention_type?: string;
        semaforo?: 'verde' | 'amarillo' | 'rojo';
        help_level?: string;
        requires_student_response?: boolean;
        cognitive_events?: string[];
        rule_violations?: string[];
      };
    }, { message: string; student_profile?: Record<string, unknown> }>(`/sessions/${sessionId}/interact`, {
      message,
      student_profile: studentProfile,
    });
  }

  /**
   * Obtener analytics N4 de la sesión
   * @param sessionId - ID de la sesión
   * @returns Estadísticas completas de la sesión
   */
  async getAnalyticsN4(sessionId: string): Promise<{
    total_messages: number;
    semaforo_distribution: {
      verde: number;
      amarillo: number;
      rojo: number;
    };
    intervention_types: Record<string, number>;
    cognitive_events: string[];
    student_progression: Record<string, unknown>;
  }> {
    return this.get<{
      total_messages: number;
      semaforo_distribution: {
        verde: number;
        amarillo: number;
        rojo: number;
      };
      intervention_types: Record<string, number>;
      cognitive_events: string[];
      student_progression: Record<string, unknown>;
    }>(`/${sessionId}/analytics-n4`);
  }

  /**
   * Obtener historial completo de sesiones de un estudiante con agregaciones (HU-EST-008)
   * Backend route: GET /api/v1/sessions/history/{student_id}
   *
   * @param studentId - ID del estudiante
   * @param params - Filtros opcionales (fechas, actividad, modo, estado, competencia mínima)
   * @returns Historial con sesiones y agregaciones
   */
  async getHistory(
    studentId: string,
    params?: SessionHistoryParams
  ): Promise<SessionHistoryResponse> {
    const queryParams = new URLSearchParams();

    if (params?.start_date) queryParams.append('start_date', params.start_date);
    if (params?.end_date) queryParams.append('end_date', params.end_date);
    if (params?.activity_id) queryParams.append('activity_id', params.activity_id);
    if (params?.mode) queryParams.append('mode', params.mode);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.min_competency) queryParams.append('min_competency', params.min_competency);

    const query = queryParams.toString();
    return this.get<SessionHistoryResponse>(`/history/${studentId}${query ? `?${query}` : ''}`);
  }
}

/**
 * Parámetros de filtro para historial de sesiones
 */
export interface SessionHistoryParams {
  start_date?: string;  // ISO date string (YYYY-MM-DD)
  end_date?: string;    // ISO date string (YYYY-MM-DD)
  activity_id?: string;
  mode?: string;        // TUTOR, EVALUATOR, SIMULATOR, etc.
  status?: string;      // active, completed, paused, aborted
  min_competency?: string; // INICIAL, INTERMEDIO, AVANZADO
}

/**
 * Resumen de una sesión en el historial
 */
export interface SessionSummary {
  session_id: string;
  activity_id: string;
  mode: string;
  status: string;
  start_time: string;
  end_time: string | null;
  duration_minutes: number | null;
  interactions_count: number;
  ai_dependency_score: number | null;
  competency_level: string | null;
  overall_score: number | null;
  risks_detected: number;
  critical_risks: number;
}

/**
 * Agregaciones del historial de sesiones
 */
export interface ProgressAggregation {
  total_sessions: number;
  completed_sessions: number;
  total_interactions: number;
  average_ai_dependency: number;
  competency_evolution: Array<{
    date: string;
    level: string;
    score: number;
  }>;
  activity_breakdown: Record<string, number>;
  mode_breakdown: Record<string, number>;
  risk_summary: {
    total_risks: number;
    critical_risks: number;
    high_risks: number;
    medium_risks: number;
    low_risks: number;
    resolved_risks: number;
  };
}

/**
 * Respuesta completa del historial de sesiones (HU-EST-008)
 */
export interface SessionHistoryResponse {
  student_id: string;
  sessions: SessionSummary[];
  aggregations: ProgressAggregation;
  filters_applied: Record<string, string> | null;
}

// Export singleton instance
export const sessionsService = new SessionsService();