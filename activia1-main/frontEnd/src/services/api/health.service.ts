/**
 * Health Service - System health checks
 *
 * Refactored to use BaseApiService for consistent API response handling.
 */

import { BaseApiService } from './base.service';
import type { HealthResponse } from '@/types/api.types';

/**
 * HealthService - Uses BaseApiService for consistent response handling
 */
class HealthService extends BaseApiService {
  constructor() {
    super('/health');
  }

  /**
   * Check system health status
   * Backend route: GET /api/v1/health
   */
  async check(): Promise<HealthResponse> {
    return this.get<HealthResponse>('');
  }

  /**
   * Simple ping check
   * Backend route: GET /api/v1/health/ping
   */
  async ping(): Promise<{ status: string }> {
    return this.get<{ status: string }>('/ping');
  }
}

export const healthService = new HealthService();