/**
 * Servicio para consulta de riesgos detectados por AR-IA
 *
 * Detecta riesgos en 5 dimensiones:
 * - Cognitiva: Dependencia excesiva de IA, falta de comprensión
 * - Ética: Plagio, uso inapropiado de código generado
 * - Técnica: Errores conceptuales, malas prácticas
 * - Metacognitiva: Falta de reflexión, estrategias ineficientes
 * - Social: Aislamiento, falta de colaboración
 *
 * Niveles de riesgo: info, low, medium, high, critical
 *
 * NOTA: Para evaluaciones de proceso, usar evaluationsService
 */

import { BaseApiService } from './base.service';
import { get } from './client';  // FIX Cortez20: Import for unwrapped requests
import type { Risk } from '@/types/api.types';

/**
 * RisksService - Consulta de riesgos usando base class
 *
 * Para evaluaciones de proceso, usar evaluationsService:
 * - evaluationsService.getSessionEvaluation(sessionId)
 * - evaluationsService.getStudentEvaluations(studentId)
 *
 * @example
 * ```typescript
 * // Obtener riesgos no resueltos
 * const risks = await risksService.getBySession(sessionId, false);
 *
 * // Obtener solo riesgos críticos
 * const critical = await risksService.getCritical(sessionId);
 *
 * // Obtener riesgos por estudiante
 * const studentRisks = await risksService.getByStudent(studentId);
 *
 * // Obtener estadísticas de riesgos
 * const stats = await risksService.getStatistics(studentId);
 * ```
 */
class RisksService extends BaseApiService {
  constructor() {
    super('/risks');
  }

  /**
   * Obtener riesgos de una sesión
   * FIX 3.1-3.2 Cortez12: Added dimension and level query parameters
   * @param sessionId - ID de la sesión
   * @param filters - Filtros opcionales (resolved, dimension, level)
   * @returns Lista de riesgos detectados
   */
  async getBySession(
    sessionId: string,
    filters?: {
      resolved?: boolean;
      dimension?: string;  // FIX 3.1: Added dimension filter
      level?: string;      // FIX 3.2: Backend uses 'level' not 'risk_level'
    }
  ): Promise<Risk[]> {
    const queryParams = new URLSearchParams();
    if (filters?.resolved !== undefined) queryParams.append('resolved', String(filters.resolved));
    if (filters?.dimension) queryParams.append('dimension', filters.dimension);
    if (filters?.level) queryParams.append('level', filters.level);

    const queryString = queryParams.toString();
    return this.get<Risk[]>(`/session/${sessionId}${queryString ? `?${queryString}` : ''}`);
  }

  /**
   * Obtener riesgos de un estudiante (todas las sesiones)
   * FIX 3.1-3.2 Cortez12: Added dimension and level query parameters
   * @param studentId - ID del estudiante
   * @param filters - Filtros opcionales (resolved, dimension, level)
   * @returns Lista de riesgos del estudiante
   */
  async getByStudent(
    studentId: string,
    filters?: {
      resolved?: boolean;
      dimension?: string;  // FIX 3.1: Added dimension filter
      level?: string;      // FIX 3.2: Backend uses 'level' not 'risk_level'
    }
  ): Promise<Risk[]> {
    const queryParams = new URLSearchParams();
    if (filters?.resolved !== undefined) queryParams.append('resolved', String(filters.resolved));
    if (filters?.dimension) queryParams.append('dimension', filters.dimension);
    if (filters?.level) queryParams.append('level', filters.level);

    const queryString = queryParams.toString();
    return this.get<Risk[]>(`/student/${studentId}${queryString ? `?${queryString}` : ''}`);
  }

  /**
   * Obtener riesgos críticos (nivel critical o high)
   * @param studentId - ID del estudiante (opcional)
   * @returns Lista de riesgos críticos no resueltos
   */
  async getCritical(studentId?: string): Promise<Risk[]> {
    const params = studentId ? `?student_id=${studentId}` : '';
    return this.get<Risk[]>(`/critical${params}`);
  }

  /**
   * Obtener estadísticas de riesgos de un estudiante
   * @param studentId - ID del estudiante
   * @returns Estadísticas agregadas de riesgos
   */
  async getStatistics(studentId: string): Promise<{
    total_risks: number;
    by_level: Record<string, number>;
    by_dimension: Record<string, number>;
    by_type: Record<string, number>;
    resolution_rate: number;
  }> {
    return this.get(`/student/${studentId}/statistics`);
  }

  /**
   * Analizar una sesión para detectar riesgos automáticamente (AR-IA)
   * Backend route: POST /api/v1/risks/analyze-session/{session_id}
   *
   * Este endpoint dispara el motor AR-IA que analiza:
   * - Patrones de código y calidad técnica
   * - Dependencia de IA
   * - Riesgos cognitivos y éticos
   * - Violaciones de gobernanza
   *
   * @param sessionId - ID de la sesión a analizar
   * @returns Lista de riesgos detectados por AR-IA
   */
  async analyze(sessionId: string): Promise<Risk[]> {
    return this.post<Risk[]>(`/analyze-session/${sessionId}`);
  }

  /**
   * FIX 2.2: Análisis 5D de riesgos (Cortez2 audit)
   * Backend route: GET /api/v1/risk-analysis/{session_id}
   *
   * Obtiene el análisis de riesgos en las 5 dimensiones:
   * - Cognitiva (RC)
   * - Ética (RE)
   * - Epistémica (REp)
   * - Técnica (RT)
   * - Gobernanza (RG)
   *
   * @param sessionId - ID de la sesión a analizar
   * @returns Análisis completo de 5 dimensiones
   */
  async analyze5D(sessionId: string): Promise<{
    session_id: string;
    overall_score: number;
    risk_level: string;
    dimensions: Record<string, {
      score: number;
      level: string;
      indicators: string[];
    }>;
    top_risks: Array<{
      dimension: string;
      description: string;
      severity: string;
      mitigation: string;
    }>;
    recommendations: string[];
  }> {
    // FIX Cortez20: Use get() helper which extracts data from APIResponse wrapper
    // risk-analysis endpoint is different from /risks baseUrl
    return get<{
      session_id: string;
      overall_score: number;
      risk_level: string;
      dimensions: {
        cognitive: { score: number; level: string; indicators: string[] };
        ethical: { score: number; level: string; indicators: string[] };
        epistemic: { score: number; level: string; indicators: string[] };
        technical: { score: number; level: string; indicators: string[] };
        governance: { score: number; level: string; indicators: string[] };
      };
      top_risks: Array<{
        dimension: string;
        description: string;
        severity: string;
        mitigation: string;
      }>;
      recommendations: string[];
    }>(`/risk-analysis/${sessionId}`);
  }
}

// Export singleton instance
export const risksService = new RisksService();