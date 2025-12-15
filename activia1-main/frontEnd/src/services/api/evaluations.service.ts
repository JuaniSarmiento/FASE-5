/**
 * Evaluations Service - Evaluador de Procesos (E-IA-Proc)
 *
 * Refactored to use BaseApiService for consistent API response handling.
 * BaseApiService automatically extracts response.data.data from APIResponse wrapper.
 *
 * Types are imported from the central api.types.ts file to avoid duplication.
 */
import { BaseApiService } from './base.service';
import { get, post } from './client';
import {
  CompetencyLevel,
} from '@/types/api.types';
import type {
  EvaluationReport,
  EvaluationDimension,
  ReasoningAnalysis,
  GitAnalysis,
  ConceptualError,
} from '@/types/api.types';

// Re-export types for convenience
export type {
  EvaluationReport,
  EvaluationDimension,
  ReasoningAnalysis,
  GitAnalysis,
  ConceptualError,
};
export { CompetencyLevel };

/**
 * StudentComparison - Response from /teacher/students/compare endpoint
 * Updated to match backend response structure (teacher_tools.py:146-165)
 */
export interface StudentComparison {
  activity_id: string;
  students_count: number;
  completed_count: number;
  in_progress_count: number;
  aggregate_statistics: AggregateStatistics;
  students: StudentComparisonData[];
}

export interface AggregateStatistics {
  average_duration_minutes: number;
  average_interactions: number;
  average_ai_dependency: number;
  top_risks: Array<{ type: string; count: number }>;
  cognitive_states_distribution: Record<string, number>;
}

export interface StudentComparisonData {
  student_id: string;
  session_id: string;
  start_time: string;
  end_time: string | null;
  duration_minutes: number;
  total_interactions: number;
  blocked_interactions: number;
  cognitive_states_visited: string[];
  ai_dependency_average: number;
  risks_total: number;
  risks_by_type: Record<string, number>;
  status: string;
}

/**
 * @deprecated Use StudentComparisonData instead
 * Kept for backwards compatibility
 */
export interface StudentEvaluationSummary {
  student_id: string;
  overall_score: number;
  overall_level: string;
  ai_dependency: number;
  strengths: string[];
  weaknesses: string[];
}

/**
 * @deprecated Use AggregateStatistics instead
 * Kept for backwards compatibility
 */
export interface ComparisonMetric {
  metric: string;
  values: Record<string, number>;
  average: number;
}

/**
 * TeacherAlertsResponse - Structure returned by /teacher/alerts endpoint
 */
export interface TeacherAlertsResponse {
  total_alerts: number;
  by_severity: {
    critical: number;
    high: number;
    medium: number;
  };
  alerts: TeacherAlert[];
}

export interface TeacherAlert {
  alert_id: string;
  student_id: string;
  session_id: string;
  activity_id: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  reasons: string[];
  suggestions: string[];
  metrics: {
    critical_risks: number;
    high_risks: number;
    medium_risks: number;
    ai_dependency: number;
    duration_hours: number;
    total_interactions: number;
  };
  timestamp: string;
}

/**
 * Process Evaluation Response from /evaluations/{session_id}/generate
 * This is the LLM-generated evaluation with 5 dimensions
 */
export interface ProcessEvaluationResponse {
  session_id: string;
  student_id: string;
  activity_id: string;
  planning: EvaluationDimension;
  execution: EvaluationDimension;
  debugging: EvaluationDimension;
  reflection: EvaluationDimension;
  autonomy: EvaluationDimension;
  autonomy_level: 'low' | 'medium' | 'high';
  metacognition_score: number;
  delegation_ratio: number;
  overall_feedback: string;
  generated_at: string;
}

/**
 * EvaluationsService - Uses BaseApiService for consistent response handling
 *
 * Backend has TWO evaluation systems:
 * 1. /risks/evaluation/* - Stored evaluations from EvaluationDB (E-IA-Proc results)
 * 2. /evaluations/* - On-demand LLM-generated process evaluations
 *
 * Teacher tools are accessed via /teacher/* endpoints.
 */
class EvaluationsService extends BaseApiService {
  constructor() {
    // Using /risks as base since stored evaluations are under /risks/evaluation/*
    super('/risks');
  }

  /**
   * Get evaluation report by ID (uses session_id as fallback)
   * Backend route: GET /api/v1/risks/evaluation/session/{session_id}
   */
  async getReport(reportId: string): Promise<EvaluationReport> {
    // reportId is typically the session_id
    return this.get<EvaluationReport>(`/evaluation/session/${reportId}`);
  }

  /**
   * Get stored evaluation for session (from EvaluationDB)
   * Backend route: GET /api/v1/risks/evaluation/session/{session_id}
   */
  async getSessionEvaluation(sessionId: string): Promise<EvaluationReport> {
    return this.get<EvaluationReport>(`/evaluation/session/${sessionId}`);
  }

  /**
   * Generate a new process evaluation using LLM
   * Backend route: POST /api/v1/evaluations/{session_id}/generate
   * This triggers Ollama to analyze the session and generate a cognitive evaluation
   */
  async generateEvaluation(sessionId: string): Promise<ProcessEvaluationResponse> {
    // This endpoint is under /evaluations, not /risks, so use absolute path
    return post<ProcessEvaluationResponse>(`/evaluations/${sessionId}/generate`);
  }

  /**
   * Alias for generateEvaluation - triggers LLM-based evaluation
   * Use this when you want to force a new evaluation generation
   */
  async evaluateSession(sessionId: string): Promise<ProcessEvaluationResponse> {
    return this.generateEvaluation(sessionId);
  }

  /**
   * Get student's evaluation history
   * Backend route: GET /api/v1/risks/evaluation/student/{student_id}
   */
  async getStudentEvaluations(studentId: string): Promise<EvaluationReport[]> {
    return this.get<EvaluationReport[]>(`/evaluation/student/${studentId}`);
  }

  /**
   * Compare students (for teachers)
   * Backend route: GET /api/v1/teacher/students/compare
   * Note: This uses /teacher prefix, not /risks, so we use absolute path via get helper
   */
  async compareStudents(studentIds: string[], activityId: string): Promise<StudentComparison> {
    const params = new URLSearchParams();
    params.append('activity_id', activityId);
    studentIds.forEach(id => params.append('student_ids', id));

    // Use static import - endpoint is under /teacher, not /risks
    return get<StudentComparison>(`/teacher/students/compare?${params.toString()}`);
  }

  /**
   * Get real-time alerts for teacher
   * Backend route: GET /api/v1/teacher/alerts
   * Note: This uses /teacher prefix, not /risks
   */
  async getTeacherAlerts(severity?: string): Promise<TeacherAlertsResponse> {
    const params = severity ? `?severity=${severity}` : '';
    // Use static import - endpoint is under /teacher, not /risks
    return get<TeacherAlertsResponse>(`/teacher/alerts${params}`);
  }

  /**
   * Acknowledge a teacher alert
   * Backend route: POST /api/v1/teacher/alerts/{alert_id}/acknowledge
   * Note: This uses /teacher prefix, not /risks
   */
  async acknowledgeAlert(alertId: string, notes?: string): Promise<{
    alert_id: string;
    acknowledged_at: string;
    notes: string;
  }> {
    const params = notes ? `?notes=${encodeURIComponent(notes)}` : '';
    // Use POST method as defined in backend
    return post<{
      alert_id: string;
      acknowledged_at: string;
      notes: string;
    }>(`/teacher/alerts/${alertId}/acknowledge${params}`);
  }
}

export const evaluationsService = new EvaluationsService();