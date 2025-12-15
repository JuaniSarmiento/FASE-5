/**
 * Servicio de interacciones con el LLM
 */
import { BaseService } from './BaseService';
import { API_ENDPOINTS } from '@/core/config/routes.config';
import { interactionsCache, CacheManager } from '@/core/cache/CacheManager';
import { InteractionCreate, InteractionResponse } from '@/types/api.types';

class InteractionService extends BaseService<InteractionResponse> {
  constructor() {
    super(API_ENDPOINTS.INTERACTIONS);
    this.cache = interactionsCache as CacheManager<InteractionResponse>;
  }

  async create(data: InteractionCreate): Promise<InteractionResponse> {
    try {
      this.validateInteractionCreate(data);
      
      // No usar caché para interacciones (siempre fresh)
      return await this.post(this.endpoint, data);
    } catch (error) {
      return this.handleError(error, 'Failed to create interaction');
    }
  }

  async getBySession(sessionId: string): Promise<InteractionResponse[]> {
    try {
      const url = `${this.endpoint}?session_id=${sessionId}`;
      return await this.list(url, true);
    } catch (error) {
      return this.handleError(error, `Failed to get interactions for session ${sessionId}`);
    }
  }

  async getById(id: string): Promise<InteractionResponse> {
    try {
      return await this.get(`${this.endpoint}/${id}`);
    } catch (error) {
      return this.handleError(error, `Failed to get interaction ${id}`);
    }
  }

  // Streaming interaction (Server-Sent Events)
  async *createStreaming(data: InteractionCreate): AsyncGenerator<string, void, unknown> {
    this.validateInteractionCreate(data);

    const response = await fetch(`${API_ENDPOINTS.BASE}${this.endpoint}/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      throw new Error(`Streaming failed: ${response.statusText}`);
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('No reader available');
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') return;
            yield data;
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  private validateInteractionCreate(data: InteractionCreate): void {
    if (!data.session_id || data.session_id.trim().length === 0) {
      throw new Error('session_id is required');
    }

    // FIXED: Changed from student_input to prompt (backend field name)
    if (!data.prompt || data.prompt.trim().length === 0) {
      throw new Error('prompt is required');
    }

    if (data.prompt.trim().length < 3) {
      throw new Error('prompt must be at least 3 characters');
    }
  }
}

export const interactionService = new InteractionService();
