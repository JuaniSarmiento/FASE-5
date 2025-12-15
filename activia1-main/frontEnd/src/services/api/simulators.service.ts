/**
 * Simulators Service - Simuladores Profesionales (S-IA-X)
 *
 * Refactored to use BaseApiService for consistent API response handling.
 *
 * Session operations (create, get, update, list) delegate to sessionsService
 * since simulator sessions are regular sessions with mode=SIMULATOR.
 */
import { BaseApiService } from './base.service';
import { get, post } from './client';
import { sessionsService } from './sessions.service';
import { SessionMode } from '@/types/api.types';
import type { SessionResponse } from '@/types/api.types';

/**
 * SimulatorType - All available simulator types
 *
 * V1 (Original - 6 types): product_owner, scrum_master, tech_interviewer, incident_responder, client, devsecops
 * V2 (Sprint 6 - 5 additional): senior_dev, qa_engineer, security_auditor, tech_lead, demanding_client
 */
export type SimulatorType =
  // V1 - Original simulators
  | 'product_owner'
  | 'scrum_master'
  | 'tech_interviewer'
  | 'incident_responder'
  | 'client'
  | 'devsecops'
  // V2 - Enhanced simulators (Sprint 6)
  | 'senior_dev'
  | 'qa_engineer'
  | 'security_auditor'
  | 'tech_lead'
  | 'demanding_client';

export type SimulatorStatus = 'active' | 'development' | 'deprecated';

export interface SimulatorInfo {
  type: SimulatorType;
  name: string;
  description: string;
  competencies: string[];
  status: SimulatorStatus;
  example_questions?: string[];
}

export interface SimulatorInteraction {
  simulator_type: SimulatorType;
  prompt: string;  // FIXED: Changed from student_input to prompt (backend field name)
  context?: Record<string, unknown>;
}

export interface SimulatorResponse {
  interaction_id: string;
  simulator_type: SimulatorType;
  response: string;
  role: string;
  expects: string[];
  competencies_evaluated: string[];
  trace_id_input: string;
  trace_id_output: string;
  metadata: Record<string, unknown>;
}

export interface SimulatorSession {
  id: string;
  student_id: string;
  simulator_type: SimulatorType;
  scenario: string;
  created_at: string;
  updated_at: string;
  interactions: SimulatorInteraction[];
  completed: boolean;
  evaluation?: SimulatorEvaluation;
}

export interface SimulatorEvaluation {
  competencies: Record<string, number>;
  overall_score: number;
  strengths: string[];
  improvements: string[];
  professional_readiness: number;
}

// =============================================================================
// SPRINT 6 TYPES - Enhanced Simulators (S-IA-X v2)
// =============================================================================

/**
 * SimulatorInfoV2 - Enhanced simulator info from /simulators-v2/available
 */
export interface SimulatorInfoV2 {
  id: string;
  name: string;
  role: string;
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  personality: string;
  objectives: string[];
  skills_tested: string[];
  color: string;
  gradient: string;
  required_level: number;
}

/**
 * SimulatorScenario - Predefined scenarios for simulators
 */
export interface SimulatorScenario {
  id: string;
  title: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard' | 'expert';
}

/**
 * StartSimulationRequest - Request body for starting a simulation
 */
export interface StartSimulationRequest {
  simulator_id: string;
  student_id: string;
  activity_id: string;
  context?: Record<string, unknown>;
}

/**
 * StartSimulationResponse - Response from starting a simulation
 */
export interface StartSimulationResponse {
  session_id: string;
  simulator_id: string;
  simulator_name: string;
  welcome_message: string;
  status: 'started' | 'in_progress' | 'completed';
  timestamp: string;
}

/**
 * StudentSimulatorStats - Statistics for a student's simulator usage
 */
export interface StudentSimulatorStats {
  student_id: string;
  total_simulator_sessions: number;
  completed_simulators: string[];
  completion_rate: number;
  by_simulator_type: Record<string, { total: number; completed: number }>;
  student_level: number;
}

/**
 * SimulatorsService - Uses BaseApiService for consistent response handling
 *
 * Backend has TWO simulator APIs:
 * 1. /simulators - Original endpoints (interact, list)
 * 2. /simulators-v2 - Enhanced endpoints (available, start, scenarios, stats)
 */
class SimulatorsService extends BaseApiService {
  constructor() {
    super('/simulators');
  }

  // ===========================================================================
  // SPRINT 6 - Enhanced Simulator Endpoints (/simulators-v2)
  // ===========================================================================

  /**
   * Get available simulators with full info (V2)
   * Backend route: GET /api/v1/simulators-v2/available
   */
  async getAvailableSimulatorsV2(userLevel: number = 1): Promise<SimulatorInfoV2[]> {
    return get<SimulatorInfoV2[]>(`/simulators-v2/available?user_level=${userLevel}`);
  }

  /**
   * Start a simulation session (V2)
   * Backend route: POST /api/v1/simulators-v2/start
   */
  async startSimulation(request: StartSimulationRequest): Promise<StartSimulationResponse> {
    return post<StartSimulationResponse>('/simulators-v2/start', request);
  }

  /**
   * Get scenarios for a specific simulator
   * Backend route: GET /api/v1/simulators-v2/{simulator_id}/scenarios
   */
  async getSimulatorScenarios(simulatorId: string): Promise<SimulatorScenario[]> {
    return get<SimulatorScenario[]>(`/simulators-v2/${simulatorId}/scenarios`);
  }

  /**
   * Get student's simulator statistics
   * Backend route: GET /api/v1/simulators-v2/stats/{student_id}
   */
  async getStudentSimulatorStats(studentId: string): Promise<StudentSimulatorStats> {
    return get<StudentSimulatorStats>(`/simulators-v2/stats/${studentId}`);
  }

  // ===========================================================================
  // Original Simulator Endpoints (/simulators)
  // ===========================================================================

  /**
   * Interact with a simulator
   * Backend route: POST /api/v1/simulators/interact
   */
  async interact(sessionId: string, interaction: SimulatorInteraction): Promise<SimulatorResponse> {
    return this.post<SimulatorResponse>('/interact', {
      session_id: sessionId,
      simulator_type: interaction.simulator_type,
      prompt: interaction.prompt,  // FIXED: Now aligned with SimulatorInteraction interface
      context: interaction.context,
    });
  }

  /**
   * Start a simulator session
   * Delegates to sessionsService since simulator sessions are regular sessions
   * with mode=SIMULATOR and simulator_type set.
   */
  async startSession(
    studentId: string,
    simulatorType: SimulatorType,
    activityId: string
  ): Promise<SimulatorSession> {
    // Use sessionsService for consistent session creation
    const session: SessionResponse = await sessionsService.create({
      student_id: studentId,
      activity_id: activityId,
      mode: SessionMode.SIMULATOR,
      simulator_type: simulatorType,
    });

    return this.mapSessionToSimulatorSession(session, simulatorType);
  }

  /**
   * Get simulator session info
   * Delegates to sessionsService for consistent session retrieval.
   */
  async getSession(sessionId: string): Promise<SimulatorSession> {
    const session = await sessionsService.getById(sessionId);
    return this.mapSessionToSimulatorSession(session);
  }

  /**
   * Complete simulator session
   * Delegates to sessionsService.end() for proper session completion.
   * Fetches the evaluation generated by E-IA-Proc after session ends.
   */
  async completeSession(sessionId: string): Promise<SimulatorEvaluation> {
    // Use sessionsService.end() which properly marks session as completed
    await sessionsService.end(sessionId);

    // Try to fetch actual evaluation from evaluations endpoint
    try {
      const { evaluationsService } = await import('./evaluations.service');
      const evaluation = await evaluationsService.getSessionEvaluation(sessionId);

      if (evaluation) {
        // Map EvaluationReport to SimulatorEvaluation
        const competencies: Record<string, number> = {};
        evaluation.dimensions?.forEach((dim) => {
          // Use name (new field) or dimension (legacy fallback)
          const dimName = dim.name || dim.dimension || 'unknown';
          competencies[dimName] = dim.score;
        });

        return {
          competencies,
          overall_score: evaluation.overall_score || 0,
          strengths: evaluation.key_strengths || [],
          improvements: evaluation.improvement_areas || [],
          professional_readiness: evaluation.ai_dependency_score
            ? Math.round((1 - evaluation.ai_dependency_score) * 100)
            : 0,
        };
      }
    } catch (error) {
      // FIX Cortez21 DEFECTO 7.2: Add logging with context
      if (import.meta.env.DEV) {
        console.warn(`Failed to fetch evaluation for session ${sessionId}:`, error);
      }
      // Evaluation not yet available, return placeholder
    }

    // Fallback if evaluation not available
    return {
      competencies: {},
      overall_score: 0,
      strengths: [],
      improvements: [],
      professional_readiness: 0,
    };
  }

  /**
   * Helper to map SessionResponse to SimulatorSession
   * @private
   */
  private mapSessionToSimulatorSession(
    session: SessionResponse,
    defaultSimulatorType?: SimulatorType
  ): SimulatorSession {
    const simulatorType = (session.simulator_type || defaultSimulatorType || 'product_owner') as SimulatorType;
    return {
      id: session.id,
      student_id: session.student_id,
      simulator_type: simulatorType,
      scenario: '',
      created_at: session.created_at,
      updated_at: session.updated_at,
      interactions: [],
      completed: session.status === 'completed',
    };
  }

  /**
   * Get available simulators (simplified info)
   * Backend route: GET /api/v1/simulators
   * @deprecated Use getAllSimulators() for complete info
   */
  async getAvailableSimulators(): Promise<{ type: SimulatorType; name: string; description: string }[]> {
    // Delegate to getAllSimulators and map to simplified format
    const simulators = await this.getAllSimulators();
    return simulators.map((s) => ({
      type: s.type,
      name: s.name,
      description: s.description,
    }));
  }

  /**
   * Get student's simulator history
   * Delegates to sessionsService.list() and filters by SIMULATOR mode.
   */
  async getStudentHistory(studentId: string): Promise<SimulatorSession[]> {
    try {
      // Use sessionsService for consistent session listing
      const response = await sessionsService.list(studentId);

      // Filter sessions with mode=SIMULATOR and map to SimulatorSession
      const simulatorSessions = (response.data || [])
        .filter((s: SessionResponse) => s.mode === SessionMode.SIMULATOR)
        .map((s: SessionResponse) => this.mapSessionToSimulatorSession(s));

      return simulatorSessions;
    } catch (error) {
      // FIX Cortez21 DEFECTO 7.3: Add logging with context
      if (import.meta.env.DEV) {
        console.warn(`Failed to fetch simulator history for student ${studentId}:`, error);
      }
      // Return empty array on error to maintain backwards compatibility
      return [];
    }
  }

  /**
   * Get specific simulator info
   * Backend route: GET /api/v1/simulators/{simulator_type}
   * FIX Cortez21 DEFECTO 3.7: Replace any with SimulatorInfo type
   */
  async getSimulatorInfo(simulatorType: SimulatorType): Promise<SimulatorInfo> {
    const info = await this.get<SimulatorInfo>(`/${simulatorType}`);
    return {
      type: ((info?.type || '') as string).toLowerCase() as SimulatorType,
      name: info?.name || '',
      description: info?.description || '',
      competencies: info?.competencies || [],
      status: info?.status || 'active',
      example_questions: info?.example_questions,
    };
  }

  /**
   * Get all simulators with full info
   * Backend route: GET /api/v1/simulators
   * FIX Cortez21 DEFECTO 3.7: Replace any[] with SimulatorInfo[] type
   */
  async getAllSimulators(): Promise<SimulatorInfo[]> {
    const simulators = await this.get<SimulatorInfo[]>('');
    if (!Array.isArray(simulators)) return [];
    return simulators.map((s: SimulatorInfo) => ({
      type: ((s?.type || '') as string).toLowerCase() as SimulatorType,
      name: s?.name || '',
      description: s?.description || '',
      competencies: s?.competencies || [],
      status: s?.status || 'active',
      example_questions: s?.example_questions,
    }));
  }
}

export const simulatorsService = new SimulatorsService();