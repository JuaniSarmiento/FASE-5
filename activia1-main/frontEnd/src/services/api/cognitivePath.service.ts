/**
 * Cognitive Path Service - Camino cognitivo reconstructivo
 *
 * Backend router: /cognitive-path
 * Sprint 3 - HU-EST-006
 *
 * Proporciona acceso al camino cognitivo completo de una sesión,
 * incluyendo fases, transiciones, y evolución de dependencia de IA.
 *
 * NOTE: This is a separate router from /traces/{session_id}/cognitive-path
 * Both exist in backend, this service uses the dedicated /cognitive-path router.
 */
import { BaseApiService } from './base.service';
import type {
  CognitivePath,
  CognitivePathSummary,
} from '@/types/api.types';

/**
 * CognitivePathService - Backend router: /cognitive-path
 */
class CognitivePathService extends BaseApiService {
  constructor() {
    super('/cognitive-path');
  }

  /**
   * Get full cognitive path for a session
   * Backend route: GET /api/v1/cognitive-path/{session_id}
   *
   * Includes:
   * - Sequence of cognitive states
   * - Transitions with timestamps
   * - Help request points
   * - Risks detected per phase
   * - AI dependency evolution (0-100%)
   * - Summary metrics
   *
   * @param sessionId - Session ID
   * @returns Complete cognitive path reconstruction
   */
  async getCognitivePath(sessionId: string): Promise<CognitivePath> {
    return this.get<CognitivePath>(`/${sessionId}`);
  }

  /**
   * Get only the summary metrics of cognitive path
   * Backend route: GET /api/v1/cognitive-path/{session_id}/summary
   *
   * Useful for:
   * - Dashboards with many students
   * - Quick comparisons
   * - Aggregated visualizations
   *
   * @param sessionId - Session ID
   * @returns Quantitative summary only
   */
  async getCognitivePathSummary(sessionId: string): Promise<CognitivePathSummary> {
    return this.get<CognitivePathSummary>(`/${sessionId}/summary`);
  }
}

export const cognitivePathService = new CognitivePathService();