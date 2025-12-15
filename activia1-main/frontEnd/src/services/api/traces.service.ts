/**
 * Servicio para consulta de trazabilidad cognitiva N4
 *
 * Sistema de Trazabilidad Cognitiva con 4 niveles:
 * - N1 Superficial: Registro básico de interacciones
 * - N2 Técnico: Análisis de código y patrones
 * - N3 Interaccional: Flujo de diálogo estudiante-IA
 * - N4 Cognitivo: Estados mentales y estrategias de resolución
 *
 * Las trazas capturan el proceso de razonamiento del estudiante,
 * permitiendo evaluación basada en proceso (no solo producto).
 */

import { BaseApiService } from './base.service';
import { cognitivePathService } from './cognitivePath.service';
import type { CognitiveTrace, CognitivePath, TraceLevel, PaginationMeta } from '@/types/api.types';

/**
 * PaginatedTracesResponse - Response from backend traces endpoints
 * Backend returns PaginatedResponse[TraceResponse] which includes pagination metadata
 */
export interface PaginatedTracesResponse {
  data: CognitiveTrace[];
  pagination: PaginationMeta;
}

/**
 * Query parameters for paginated traces endpoints
 * FIX 6.2-6.3 Cortez12: Added activity_id parameter
 */
export interface TracesQueryParams {
  trace_level?: TraceLevel | string;
  interaction_type?: string;
  cognitive_state?: string;
  activity_id?: string;  // FIX 6.2: Added activity_id filter
  page?: number;
  page_size?: number;
}

/**
 * TracesService - Consulta de trazabilidad usando base class
 *
 * NOTA: El backend retorna PaginatedResponse con metadata de paginación.
 * Los métodos simples (getBySession, getByStudent) retornan solo el array de trazas.
 * Para acceder a la paginación, usar los métodos *Paginated.
 *
 * @example
 * ```typescript
 * // Obtener todas las trazas N4 de una sesión (sin paginación expuesta)
 * const traces = await tracesService.getBySession(sessionId, TraceLevel.N4_COGNITIVO);
 *
 * // Obtener trazas con metadata de paginación
 * const { data, pagination } = await tracesService.getBySessionPaginated(sessionId, {
 *   trace_level: TraceLevel.N4_COGNITIVO,
 *   page: 1,
 *   page_size: 20
 * });
 * console.log(`Mostrando ${data.length} de ${pagination.total_items} trazas`);
 *
 * // Obtener el camino cognitivo completo
 * const path = await tracesService.getCognitivePath(sessionId);
 * console.log(path.states_sequence); // ['exploracion', 'planificacion', 'implementacion', ...]
 * ```
 */
class TracesService extends BaseApiService {
  constructor() {
    super('/traces');
  }

  /**
   * Obtener trazas de una sesión (método simple, sin paginación expuesta)
   * @param sessionId - ID de la sesión
   * @param traceLevel - Nivel de traza opcional (N1-N4)
   * @returns Lista de trazas cognitivas (primera página por defecto, 50 items)
   */
  async getBySession(
    sessionId: string,
    traceLevel?: TraceLevel
  ): Promise<CognitiveTrace[]> {
    const params = traceLevel ? `?trace_level=${traceLevel}` : '';
    return this.get<CognitiveTrace[]>(`/${sessionId}${params}`);
  }

  /**
   * Obtener trazas de una sesión CON metadata de paginación
   * Backend route: GET /api/v1/traces/{session_id}
   *
   * @param sessionId - ID de la sesión
   * @param params - Parámetros de query (filtros y paginación)
   * @returns Objeto con data (trazas) y pagination metadata
   */
  async getBySessionPaginated(
    sessionId: string,
    params?: TracesQueryParams
  ): Promise<PaginatedTracesResponse> {
    const queryParams = new URLSearchParams();

    if (params?.trace_level) queryParams.append('trace_level', params.trace_level);
    if (params?.interaction_type) queryParams.append('interaction_type', params.interaction_type);
    if (params?.cognitive_state) queryParams.append('cognitive_state', params.cognitive_state);
    if (params?.activity_id) queryParams.append('activity_id', params.activity_id);  // FIX 6.2
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());

    const queryString = queryParams.toString();
    const url = `/${sessionId}${queryString ? `?${queryString}` : ''}`;

    // El cliente extrae response.data.data, pero PaginatedResponse tiene estructura diferente
    // Backend PaginatedResponse: { success, data: [...], pagination: {...} }
    // El get<> extraerá el 'data' del APIResponse, que es el array de trazas
    // Para obtener pagination, necesitamos hacer la request raw
    const response = await this.getRaw<PaginatedTracesResponse>(url);
    return response;
  }

  /**
   * Método raw que retorna la respuesta completa del backend
   * Útil para endpoints que usan PaginatedResponse
   *
   * FIX: Extracción explícita para evitar confusión con doble .data
   */
  private async getRaw<T>(endpoint: string): Promise<T> {
    const { default: apiClient } = await import('./client');
    const response = await apiClient.get(`${this.baseUrl}${endpoint}`);

    // response.data es el APIResponse del backend: { success, data, pagination }
    // Extraer explícitamente para claridad
    const apiResponse = response.data;

    return {
      data: apiResponse.data,
      pagination: apiResponse.pagination,
    } as T;
  }

  /**
   * Obtener camino cognitivo completo de una sesión
   * Incluye: secuencia de estados, transiciones, evolución de dependencia IA
   * @param sessionId - ID de la sesión
   * @returns CognitivePath con análisis completo del proceso cognitivo
   * @deprecated Use cognitivePathService.getCognitivePath() instead for the canonical endpoint
   */
  async getCognitivePath(sessionId: string): Promise<CognitivePath> {
    // Delegate to cognitivePathService which uses the canonical /cognitive-path endpoint
    return cognitivePathService.getCognitivePath(sessionId);
  }

  /**
   * FIX DEFECTO 5.1 Cortez14: Get N4 traceability data for an interaction
   * Backend route: GET /api/v1/traceability/{interaction_id}
   *
   * FIX Cortez21 DEFECTO 3.1: Use get() helper instead of raw apiClient
   *
   * @param interactionId - ID of the interaction (or trace_id from interaction response)
   * @returns N4 traceability data with nodes and metadata
   */
  async getN4(interactionId: string): Promise<{
    trace_id: string;
    nodes: Array<{
      id: string;
      level: 'N1' | 'N2' | 'N3' | 'N4';
      timestamp: string;
      data: Record<string, unknown>;
      metadata: {
        processing_time_ms?: number;
        tokens_used?: number;
        model?: string;
        transformations?: string[];
      };
    }>;
    metadata: {
      total_processing_time_ms: number;
      created_at: string;
    };
  }> {
    // FIX Cortez21: Use get() helper which automatically extracts data from APIResponse
    const { get } = await import('./client');
    return get(`/traceability/${interactionId}`);
  }

  /**
   * Obtener trazas por estudiante (método simple, sin paginación expuesta)
   * @param studentId - ID del estudiante
   * @returns Lista de trazas cognitivas del estudiante (primera página por defecto)
   */
  async getByStudent(studentId: string): Promise<CognitiveTrace[]> {
    return this.get<CognitiveTrace[]>(`/student/${studentId}`);
  }

  /**
   * Obtener trazas por estudiante CON metadata de paginación
   * Backend route: GET /api/v1/traces/student/{student_id}
   *
   * @param studentId - ID del estudiante
   * @param params - Parámetros de query (filtros y paginación)
   * @returns Objeto con data (trazas) y pagination metadata
   */
  async getByStudentPaginated(
    studentId: string,
    params?: { activity_id?: string; page?: number; page_size?: number }
  ): Promise<PaginatedTracesResponse> {
    const queryParams = new URLSearchParams();

    if (params?.activity_id) queryParams.append('activity_id', params.activity_id);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.page_size) queryParams.append('page_size', params.page_size.toString());

    const queryString = queryParams.toString();
    const url = `/student/${studentId}${queryString ? `?${queryString}` : ''}`;

    return this.getRaw<PaginatedTracesResponse>(url);
  }
}

// Export singleton instance
export const tracesService = new TracesService();