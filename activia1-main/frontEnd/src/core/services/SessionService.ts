/**
 * Servicio de sesiones - versión simplificada
 */
import { BaseService } from './BaseService';
import { API_ENDPOINTS } from '@/core/config/routes.config';
import { SessionCreate, SessionResponse } from '@/types/api.types';
import { sessionsCache, CacheManager } from '@/core/cache/CacheManager';

class SessionService extends BaseService<SessionResponse> {
  constructor() {
    super(API_ENDPOINTS.SESSIONS);
    this.cache = sessionsCache as CacheManager<SessionResponse>;
  }

  async create(data: SessionCreate): Promise<SessionResponse> {
    try {
      // Validar datos
      if (!data.student_id || !data.activity_id || !data.mode) {
        throw new Error('student_id, activity_id y mode son requeridos');
      }

      const response = await this.post(this.endpoint, data);
      this.cache?.clear();
      return response;
    } catch (error: unknown) {
      console.error(`❌ Error creating session:`, error);
      throw error;
    }
  }

  async listAll(): Promise<SessionResponse[]> {
    try {
      const response = await this.get(this.endpoint) as SessionResponse | SessionResponse[];
      return Array.isArray(response) ? response : [response];
    } catch (error: unknown) {
      console.error(`❌ Error listing sessions:`, error);
      return [];
    }
  }

  async getById(id: string): Promise<SessionResponse | null> {
    try {
      const cacheKey = `${this.endpoint}/${id}`;
      return await this.get(cacheKey);
    } catch (error: unknown) {
      console.error(`❌ Error getting session ${id}:`, error);
      return null;
    }
  }
}

export const sessionService = new SessionService();
