/**
 * Frontend Types - Central Export File
 *
 * FIX 4.1: Consolidated types to avoid duplication between index.ts and api.types.ts
 * This file re-exports from api.types.ts (canonical source) and adds unique types.
 *
 * FIX Cortez16: Import types for local use in type aliases
 */

// ============================================================================
// IMPORTS FOR LOCAL USE (needed for type aliases below)
// FIX Cortez16: Types must be imported to use locally, not just re-exported
// ============================================================================
import type {
  SessionResponse,
  SessionCreate,
  InteractionRequest,
  ActivityResponse,
  PolicyConfig,
  RiskDimensionScore,
} from './api.types';

// ============================================================================
// RE-EXPORTS FROM api.types.ts (Canonical Source)
// ============================================================================

// API Response Wrappers
export type {
  APIResponse,
  APIError,
  PaginationParams,
  PaginationMeta,
  PaginatedResponse,
} from './api.types';

// Enums
export {
  SessionMode,
  SessionStatus,
  CognitiveIntent,
  CognitiveState,
  TraceLevel,
  RiskLevel,
  RiskType,
  RiskDimension,
  CompetencyLevel,
  ActivityDifficulty,
  ActivityStatus,
  HelpLevel,
  SimulatorRole,
} from './api.types';

// Label helpers
export {
  RiskTypeLabels,
  RiskDimensionLabels,
  CompetencyLevelLabels,
} from './api.types';

// Session Types
export type {
  SessionCreate,
  SessionUpdate,
  SessionResponse,
  SessionDetailResponse,
} from './api.types';

// Interaction Types
export type {
  InteractionCreate,
  InteractionRequest,
  InteractionResponse,
  InteractionSummary,
  InteractionHistory,
} from './api.types';

// Trace Types
export type {
  CognitiveTrace,
  AIDependencyPoint,
  CognitivePhase,
  CognitiveTransition,
  CognitivePathSummary,
  CognitivePath,
  TraceNode,
  Trace,
} from './api.types';

// Risk Types
export type {
  Risk,
  RiskDimensionScore,
  RiskAnalysis,
} from './api.types';

// Evaluation Types
export type {
  EvaluationDimension,
  ConceptualError,
  ReasoningAnalysis,
  GitAnalysis,
  EvaluationReport,
  DimensionScore,
  ProcessEvaluation,
  // FIX 4.3 Cortez12: Export new type literals
  AutonomyLevel,
  DimensionLevel,
} from './api.types';

// Activity Types
export type {
  PolicyConfig,
  ActivityCreate,
  ActivityUpdate,
  ActivityResponse,
} from './api.types';

// Health Types
export type { HealthResponse } from './api.types';

// Chat Types
export type { MessageStatus, ChatMessage } from './api.types';

// Git Analytics Types
export type {
  CommitMetrics,
  Contributor,
  CommitTrend,
  GitAnalyticsData,
} from './api.types';

// Simulator Types
export type {
  SimulatorInteractionRequest,
  SimulatorInteractionResponse,
} from './api.types';

// ============================================================================
// UNIQUE TYPES (Not in api.types.ts)
// ============================================================================

// ===== Auth Types =====
// FIX 5.1 Cortez12: Added missing fields from backend UserResponse
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  student_id?: string;  // FIX 5.1: Added from backend
  roles: string[];
  is_active: boolean;
  is_verified?: boolean;  // FIX 5.1: Added from backend
  created_at?: string;  // FIX 5.1: Added from backend
}

// FIX 5.3 Cortez12: Added missing fields from backend TokenResponse
export interface TokenResponse {
  access_token: string;
  refresh_token?: string;  // FIX 5.3: Added from backend
  token_type: string;
  expires_in?: number;  // FIX 5.3: Added from backend
}

// FIX 5.2 Cortez12: Changed 'username' to 'email' to match backend LoginRequest
export interface LoginCredentials {
  email: string;  // FIX 5.2: Backend uses 'email' not 'username'
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role?: string;
}

// ===== Session Aliases (for backwards compatibility) =====
export type Session = SessionResponse;
export type CreateSessionData = SessionCreate;

// ===== Interaction Aliases =====
export type Interaction = InteractionRequest;

// ===== Simulator Types =====
// Use lowercase to match backend enum values
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

// FIX Cortez16: Added 'deprecated' to match SimulatorStatus from service
export interface Simulator {
  type: SimulatorType;
  name: string;
  description: string;
  competencies: string[];
  status: 'active' | 'development' | 'deprecated';
  icon?: string;
}

export interface SimulatorInteraction {
  session_id: string;
  simulator_type: SimulatorType;
  prompt: string;
  context?: Record<string, unknown>;
}

export interface SimulatorResponse {
  response: string;
  competency_scores: Record<string, number>;
  feedback: string;
  suggestions: string[];
}

// ===== Exercise Types =====
export interface Exercise {
  id: string;
  title: string;
  description: string;
  difficulty_level: number;
  starter_code?: string;
  hints?: string[];
  max_score: number;
  time_limit_seconds: number;
  category?: string;
  tags?: string[];
}

export interface ExerciseSubmission {
  exercise_id: string;
  code: string;
}

export interface SubmissionResult {
  id: string;
  passed_tests: number;
  total_tests: number;
  is_correct: boolean;
  execution_time_ms: number;
  ai_score?: number;
  ai_feedback?: string;
  code_quality_score?: number;
  readability_score?: number;
  efficiency_score?: number;
  best_practices_score?: number;
  test_results: TestResult[];
}

export interface TestResult {
  name: string;
  passed: boolean;
  input: string;
  expected_output: string;
  actual_output: string;
  error?: string;
}

// ===== Activity Aliases =====
export type Activity = ActivityResponse;
export type ActivityPolicies = PolicyConfig;

// ===== Health Types =====
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  version: string;
  database: 'connected' | 'disconnected';
  timestamp: string;
  components?: Record<string, ComponentHealth>;
}

export interface ComponentHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  latency_ms?: number;
  message?: string;
}

// ===== Traceability N4 Types =====
export interface TraceabilityN4 {
  trace_id: string;
  nodes: TraceabilityNode[];
  metadata: {
    total_processing_time_ms: number;
    created_at: string;
  };
}

export interface TraceabilityNode {
  id: string;
  level: 'N1' | 'N2' | 'N3' | 'N4';
  timestamp: string;
  data: Record<string, unknown>;
  metadata: {
    processing_time_ms?: number;  // FIX Cortez16: Make optional
    tokens_used?: number;
    model?: string;
    transformations?: string[];   // FIX Cortez16: Make optional
  };
}

// ===== Risk Analysis 5D Types =====
export interface RiskAnalysis5D {
  session_id: string;
  overall_score: number;
  risk_level: 'info' | 'low' | 'medium' | 'high' | 'critical';
  dimensions: {
    cognitive: RiskDimensionScore;
    ethical: RiskDimensionScore;
    epistemic: RiskDimensionScore;
    technical: RiskDimensionScore;
    governance: RiskDimensionScore;
  };
  top_risks: RiskItem[];
  recommendations: string[];
}

export interface RiskItem {
  dimension: string;
  description: string;
  severity: string;
  recommendation?: string;
  mitigation?: string;  // FIX Cortez16: Add mitigation field used in RiskAnalysisViewer
}

// ===== User Stats Types =====
export interface UserStats {
  total_sessions: number;
  completed_exercises: number;
  average_score: number;
  total_interactions: number;
  ai_dependency_ratio: number;
  top_competencies: Array<{
    name: string;
    score: number;
  }>;
  recent_activity: Array<{
    date: string;
    count: number;
  }>;
}

// ===== Type Aliases for RiskSeverity (backwards compat) =====
export type RiskSeverity = 'info' | 'low' | 'medium' | 'high' | 'critical';
