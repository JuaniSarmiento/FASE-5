/**
 * Admin Service - Administración del sistema
 *
 * Refactored to use BaseApiService for consistent API response handling.
 */
import { BaseApiService } from './base.service';

export interface LLMConfiguration {
  provider: 'ollama' | 'openai' | 'anthropic' | 'gemini' | 'mock';
  model: string;
  api_key?: string;
  api_key_configured: boolean;
  base_url?: string;
  temperature?: number;
  max_tokens?: number;
  enabled: boolean;
  limits?: {
    requests_per_day: string | number;
    tokens_per_month: string | number;
  };
  privacy_compliant: boolean;
  cost_per_1k_tokens?: number;
}

export interface LLMUsageStats {
  provider: string;
  model: string;
  total_requests: number;
  total_tokens: number;
  avg_response_time_ms: number;
  error_rate: number;
  last_used: string;
}

export interface SystemMetrics {
  total_users: number;
  active_sessions: number;
  total_sessions_today: number;
  total_interactions: number;
  avg_response_time_ms: number;
  llm_usage: LLMUsageStats[];
  storage_used_mb: number;
}

/**
 * Backend response for usage stats
 */
interface UsageStatsResponse {
  by_provider?: Record<string, {
    model?: string;
    requests?: number;
    tokens?: number;
  }>;
}

/**
 * Backend response for LLM test
 */
interface LLMTestResponse {
  status: string;
  message?: string;
}

// FIX Cortez21 DEFECTO 3.3: Define typed response for backend providers
interface LLMProviderResponse {
  provider: string;
  model: string;
  temperature?: number;
  max_tokens?: number;
  enabled: boolean;
  api_key_configured: boolean;
  limits?: {
    requests_per_day: string | number;
    tokens_per_month: string | number;
  };
  privacy_compliant: boolean;
  cost_per_1k_tokens?: number;
}

/**
 * AdminService - Uses BaseApiService for consistent response handling
 */
class AdminService extends BaseApiService {
  constructor() {
    super('/admin/llm');
  }

  /**
   * Get LLM providers configuration
   * Backend route: GET /api/v1/admin/llm/providers
   * FIX Cortez21 DEFECTO 3.3: Replace any[] with typed LLMProviderResponse[]
   */
  async getLLMConfig(): Promise<LLMConfiguration[]> {
    const providers = await this.get<LLMProviderResponse[]>('/providers');
    if (!Array.isArray(providers)) return [];
    return providers.map((p: LLMProviderResponse) => ({
      provider: p.provider as LLMConfiguration['provider'],
      model: p.model,
      temperature: p.temperature,
      max_tokens: p.max_tokens,
      enabled: p.enabled,
      api_key_configured: p.api_key_configured,
      limits: p.limits,
      privacy_compliant: p.privacy_compliant,
      cost_per_1k_tokens: p.cost_per_1k_tokens,
      // Backend doesn't expose api_key or base_url for security
      api_key: undefined,
      base_url: undefined,
    }));
  }

  /**
   * Update LLM provider configuration
   * Backend route: PATCH /api/v1/admin/llm/providers/{provider_name}
   */
  async updateLLMConfig(config: LLMConfiguration): Promise<LLMConfiguration> {
    return this.patch<LLMConfiguration>(`/providers/${config.provider}`, {
      enabled: config.enabled,
      model: config.model,
      temperature: config.temperature,
      max_tokens: config.max_tokens,
    });
  }

  /**
   * Get LLM usage statistics
   * Backend route: GET /api/v1/admin/llm/usage/stats
   */
  async getLLMUsageStats(): Promise<LLMUsageStats[]> {
    const apiData = await this.get<UsageStatsResponse>('/usage/stats');
    if (apiData.by_provider) {
      return Object.entries(apiData.by_provider).map(([provider, stats]) => ({
        provider,
        model: stats.model || 'unknown',
        total_requests: stats.requests || 0,
        total_tokens: stats.tokens || 0,
        avg_response_time_ms: 0, // Not provided by backend
        error_rate: 0, // Not provided by backend
        last_used: '', // Not provided by backend
      }));
    }
    return [];
  }

  /**
   * Get system metrics
   * Backend route: GET /api/v1/admin/llm/metrics
   * FIX Cortez21 DEFECTO 3.4: Replace any with SystemMetrics type
   */
  async getSystemMetrics(): Promise<SystemMetrics> {
    const data = await this.get<SystemMetrics>('/metrics');
    return {
      total_users: data?.total_users || 0,
      active_sessions: data?.active_sessions || 0,
      total_sessions_today: data?.total_sessions_today || 0,
      total_interactions: data?.total_interactions || 0,
      avg_response_time_ms: data?.avg_response_time_ms || 0,
      llm_usage: data?.llm_usage || [],
      storage_used_mb: data?.storage_used_mb || 0,
    };
  }

  /**
   * Test LLM connection
   * Backend route: POST /api/v1/admin/llm/test
   */
  async testLLMConnection(provider: string, model?: string): Promise<{ success: boolean; message: string }> {
    const params = new URLSearchParams({ provider });
    if (model) params.append('model', model);

    const data = await this.post<LLMTestResponse>(`/test?${params.toString()}`);
    return {
      success: data.status === 'ok',
      message: data.message || 'Connection test completed',
    };
  }
}

export const adminService = new AdminService();