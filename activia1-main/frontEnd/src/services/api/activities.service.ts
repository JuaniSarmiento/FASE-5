/**
 * Servicio para gestión de actividades creadas por docentes
 */

import { BaseApiService } from './base.service';
import { ActivityDifficulty } from '@/types/api.types';
import type {
  ActivityCreate,
  ActivityUpdate,
  ActivityResponse,
  PaginatedResponse,
  PaginationParams,
} from '@/types/api.types';

/**
 * Parámetros para filtrar actividades
 */
export interface ActivityListParams extends Partial<PaginationParams> {
  teacher_id?: string;
  status?: 'draft' | 'active' | 'archived';
  subject?: string;
  difficulty?: 'INICIAL' | 'INTERMEDIO' | 'AVANZADO';
}

/**
 * ActivitiesService - Gestión de actividades usando base class
 */
class ActivitiesService extends BaseApiService {
  constructor() {
    super('/activities');
  }

  /**
   * Crear una nueva actividad
   */
  async create(data: ActivityCreate): Promise<ActivityResponse> {
    return this.post<ActivityResponse, ActivityCreate>('', data);
  }

  /**
   * Obtener actividad por ID
   */
  async getById(activityId: string): Promise<ActivityResponse> {
    return this.get<ActivityResponse>(`/${activityId}`);
  }

  /**
   * Listar actividades con filtros opcionales
   */
  async list(
    params?: ActivityListParams
  ): Promise<PaginatedResponse<ActivityResponse>> {
    const searchParams = new URLSearchParams();

    if (params) {
      if (params.teacher_id) searchParams.append('teacher_id', params.teacher_id);
      if (params.status) searchParams.append('status', params.status);
      if (params.subject) searchParams.append('subject', params.subject);
      if (params.difficulty) searchParams.append('difficulty', params.difficulty);
      if (params.page) searchParams.append('page', params.page.toString());
      if (params.page_size) searchParams.append('page_size', params.page_size.toString());
    }

    const queryString = searchParams.toString();
    return this.get<PaginatedResponse<ActivityResponse>>(
      queryString ? `?${queryString}` : ''
    );
  }

  /**
   * Listar actividades de un docente específico
   */
  async listByTeacher(
    teacherId: string,
    pagination?: PaginationParams
  ): Promise<PaginatedResponse<ActivityResponse>> {
    return this.list({
      teacher_id: teacherId,
      ...pagination,
    });
  }

  /**
   * Listar actividades activas (publicadas)
   */
  async listActive(
    pagination?: PaginationParams
  ): Promise<PaginatedResponse<ActivityResponse>> {
    return this.list({
      status: 'active',
      ...pagination,
    });
  }

  /**
   * Actualizar actividad
   */
  async update(
    activityId: string,
    data: ActivityUpdate
  ): Promise<ActivityResponse> {
    return this.put<ActivityResponse, ActivityUpdate>(`/${activityId}`, data);
  }

  /**
   * Publicar actividad (cambiar de draft a active)
   */
  async publish(activityId: string): Promise<ActivityResponse> {
    return this.post<ActivityResponse>(`/${activityId}/publish`);
  }

  /**
   * Archivar actividad
   */
  async archive(activityId: string): Promise<ActivityResponse> {
    return this.post<ActivityResponse>(`/${activityId}/archive`);
  }

  /**
   * Eliminar actividad (soft delete)
   */
  async remove(activityId: string): Promise<void> {
    return this.delete<void>(`/${activityId}`);
  }

  /**
   * Clonar actividad (helper para duplicar una actividad existente)
   */
  async clone(
    sourceActivityId: string,
    newActivityId: string,
    teacherId: string
  ): Promise<ActivityResponse> {
    // Obtener la actividad original
    const source = await this.getById(sourceActivityId);

    // Crear una copia con nuevo ID
    const clonedData: ActivityCreate = {
      activity_id: newActivityId,
      title: `${source.title} (Copia)`,
      instructions: source.instructions,
      teacher_id: teacherId,
      policies: source.policies,
      description: source.description || undefined,
      evaluation_criteria: source.evaluation_criteria.length > 0 ? source.evaluation_criteria : undefined,
      subject: source.subject || undefined,
      difficulty: source.difficulty as ActivityDifficulty | undefined,
      estimated_duration_minutes: source.estimated_duration_minutes || undefined,
      tags: source.tags.length > 0 ? source.tags : undefined,
    };

    return this.create(clonedData);
  }
}

// Export singleton instance
export const activitiesService = new ActivitiesService();