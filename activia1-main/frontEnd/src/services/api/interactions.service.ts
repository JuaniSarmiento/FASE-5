/**
 * Servicio para procesamiento de interacciones estudiante-IA
 */

import { BaseApiService } from './base.service';
import type {
  InteractionRequest,
  InteractionResponse,
  InteractionSummary,
  InteractionHistory,
} from '@/types/api.types';

/**
 * InteractionsService - Procesamiento de interacciones usando base class
 * Note: BaseApiService already extracts response.data.data from APIResponse wrapper
 */
class InteractionsService extends BaseApiService {
  constructor() {
    super('/interactions');
  }

  /**
   * Procesar una interacción (enviar mensaje al chatbot)
   * Este es el endpoint principal que orquesta todo el flujo AI-Native
   * Backend route: POST /api/v1/interactions
   */
  async process(data: InteractionRequest): Promise<InteractionResponse> {
    // BaseApiService.post already extracts data from APIResponse wrapper
    return this.post<InteractionResponse, InteractionRequest>('', data);
  }

  /**
   * Obtener historial completo de interacciones de una sesión
   * Backend route: GET /api/v1/interactions/{session_id}/history
   * Returns: InteractionHistory object with interactions array + aggregated metrics
   */
  async getHistoryFull(sessionId: string): Promise<InteractionHistory> {
    return this.get<InteractionHistory>(`/${sessionId}/history`);
  }

  /**
   * Obtener historial de interacciones de una sesión (solo lista)
   * Convenience method that extracts just the interactions array
   * Backend route: GET /api/v1/interactions/{session_id}/history
   */
  async getHistory(sessionId: string): Promise<InteractionSummary[]> {
    const history = await this.getHistoryFull(sessionId);
    return history.interactions || [];
  }

  /**
   * Obtener métricas del historial de interacciones
   * Backend route: GET /api/v1/interactions/{session_id}/history
   */
  async getHistoryMetrics(sessionId: string): Promise<{
    totalInteractions: number;
    avgAiInvolvement: number;
    blockedCount: number;
  }> {
    const history = await this.getHistoryFull(sessionId);
    return {
      totalInteractions: history.total_interactions || 0,
      avgAiInvolvement: history.avg_ai_involvement || 0,
      blockedCount: history.blocked_count || 0,
    };
  }
}

// Export singleton instance
export const interactionsService = new InteractionsService();