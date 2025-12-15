/**
 * Tipos TypeScript para la API del ecosistema AI-Native
 * Basados en los schemas de Pydantic del backend
 */

// ==================== ENUMS ====================

/**
 * SessionMode - Modos operativos del motor cognitivo
 *
 * Alineado con backend/core/cognitive_engine.py AgentMode
 */
export enum SessionMode {
  TUTOR = 'TUTOR',           // T-IA-Cog - Tutor cognitivo
  EVALUATOR = 'EVALUATOR',   // E-IA-Proc - Evaluador de procesos
  SIMULATOR = 'SIMULATOR',   // S-IA-X - Simuladores profesionales
  RISK_ANALYST = 'RISK_ANALYST', // AR-IA - Analista de riesgos
  GOVERNANCE = 'GOVERNANCE', // GOV-IA - Gobernanza y delegación
  PRACTICE = 'PRACTICE',     // Práctica libre (minimal AI assistance)
}

// FIX 1.4 Cortez12: Added ABANDONED status from backend
export enum SessionStatus {
  ACTIVE = 'active',
  COMPLETED = 'completed',
  PAUSED = 'paused',
  ABORTED = 'aborted',
  ABANDONED = 'abandoned',
}

export enum CognitiveIntent {
  UNDERSTANDING = 'UNDERSTANDING',
  EXPLORATION = 'EXPLORATION',
  PLANNING = 'PLANNING',
  IMPLEMENTATION = 'IMPLEMENTATION',
  DEBUGGING = 'DEBUGGING',
  VALIDATION = 'VALIDATION',
  REFLECTION = 'REFLECTION',
  UNKNOWN = 'UNKNOWN',
}

// FIX Cortez24 DEFECTO 2.1: Remove duplicate enum values
// Use single enum with Spanish values (matching backend) and export alias object for English compatibility
export enum CognitiveState {
  EXPLORACION = 'exploracion',
  PLANIFICACION = 'planificacion',
  IMPLEMENTACION = 'implementacion',
  DEPURACION = 'depuracion',
  VALIDACION = 'validacion',
  REFLEXION = 'reflexion',
}

// English aliases for backwards compatibility
export const CognitiveStateAlias = {
  EXPLORATION: CognitiveState.EXPLORACION,
  PLANNING: CognitiveState.PLANIFICACION,
  IMPLEMENTATION: CognitiveState.IMPLEMENTACION,
  DEBUGGING: CognitiveState.DEPURACION,
  VALIDATION: CognitiveState.VALIDACION,
  REFLECTION: CognitiveState.REFLEXION,
} as const;

export enum TraceLevel {
  N1_SUPERFICIAL = 'n1_superficial',
  N2_TECNICO = 'n2_tecnico',
  N3_INTERACCIONAL = 'n3_interaccional',
  N4_COGNITIVO = 'n4_cognitivo',
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
  INFO = 'info',
}

/**
 * RiskType - Tipos de riesgo según AR-IA
 *
 * Alineado con backend/models/risk.py RiskType
 */
export enum RiskType {
  // Riesgos Cognitivos (RC)
  COGNITIVE_DELEGATION = 'cognitive_delegation',
  SUPERFICIAL_REASONING = 'superficial_reasoning',
  AI_DEPENDENCY = 'ai_dependency',
  LACK_JUSTIFICATION = 'lack_justification',
  NO_SELF_REGULATION = 'no_self_regulation',
  // Riesgos Éticos (RE)
  ACADEMIC_INTEGRITY = 'academic_integrity',
  UNDISCLOSED_AI_USE = 'undisclosed_ai_use',
  PLAGIARISM = 'plagiarism',
  // Riesgos Epistémicos (REp)
  CONCEPTUAL_ERROR = 'conceptual_error',
  LOGICAL_FALLACY = 'logical_fallacy',
  UNCRITICAL_ACCEPTANCE = 'uncritical_acceptance',
  // Riesgos Técnicos (RT)
  SECURITY_VULNERABILITY = 'security_vulnerability',
  POOR_CODE_QUALITY = 'poor_code_quality',
  ARCHITECTURAL_FLAW = 'architectural_flaw',
  // Riesgos de Gobernanza (RG)
  POLICY_VIOLATION = 'policy_violation',
  UNAUTHORIZED_USE = 'unauthorized_use',
  // FIX 3.4 Cortez12: Added missing RiskType from backend
  AUTOMATION_SUSPECTED = 'automation_suspected',
}

/**
 * RiskDimension - Dimensiones de riesgo según ISO/IEC 23894
 *
 * Alineado con backend/models/risk.py RiskDimension
 */
export enum RiskDimension {
  COGNITIVE = 'cognitive',   // Riesgos cognitivos (RC)
  ETHICAL = 'ethical',       // Riesgos éticos (RE)
  EPISTEMIC = 'epistemic',   // Riesgos epistémicos (REp)
  TECHNICAL = 'technical',   // Riesgos técnicos (RT)
  GOVERNANCE = 'governance', // Riesgos de gobernanza (RG)
}

/**
 * Helper labels para RiskType en UI
 */
export const RiskTypeLabels: Record<RiskType, string> = {
  [RiskType.COGNITIVE_DELEGATION]: 'Delegación Cognitiva',
  [RiskType.SUPERFICIAL_REASONING]: 'Razonamiento Superficial',
  [RiskType.AI_DEPENDENCY]: 'Dependencia de IA',
  [RiskType.LACK_JUSTIFICATION]: 'Falta de Justificación',
  [RiskType.NO_SELF_REGULATION]: 'Sin Autorregulación',
  [RiskType.ACADEMIC_INTEGRITY]: 'Integridad Académica',
  [RiskType.UNDISCLOSED_AI_USE]: 'Uso No Declarado de IA',
  [RiskType.PLAGIARISM]: 'Plagio',
  [RiskType.CONCEPTUAL_ERROR]: 'Error Conceptual',
  [RiskType.LOGICAL_FALLACY]: 'Falacia Lógica',
  [RiskType.UNCRITICAL_ACCEPTANCE]: 'Aceptación Acrítica',
  [RiskType.SECURITY_VULNERABILITY]: 'Vulnerabilidad de Seguridad',
  [RiskType.POOR_CODE_QUALITY]: 'Baja Calidad de Código',
  [RiskType.ARCHITECTURAL_FLAW]: 'Fallo Arquitectónico',
  [RiskType.POLICY_VIOLATION]: 'Violación de Políticas',
  [RiskType.UNAUTHORIZED_USE]: 'Uso No Autorizado',
  // FIX 3.4 Cortez12: Added label for AUTOMATION_SUSPECTED
  [RiskType.AUTOMATION_SUSPECTED]: 'Automatización Sospechada',
};

/**
 * Helper labels para RiskDimension en UI
 */
export const RiskDimensionLabels: Record<RiskDimension, string> = {
  [RiskDimension.COGNITIVE]: 'Cognitivo',
  [RiskDimension.ETHICAL]: 'Ético',
  [RiskDimension.EPISTEMIC]: 'Epistémico',
  [RiskDimension.TECHNICAL]: 'Técnico',
  [RiskDimension.GOVERNANCE]: 'Gobernanza',
};

// ==================== SESSION ====================

export interface SessionCreate {
  student_id: string;
  activity_id: string;
  mode: SessionMode;
  simulator_type?: string;
}

export interface SessionUpdate {
  mode?: SessionMode;
  status?: SessionStatus;
}

export interface SessionResponse {
  id: string;
  student_id: string;
  activity_id: string;
  user_id: string | null;  // ID del usuario autenticado (null para sesiones anónimas/legacy)
  mode: string;
  status: string;
  simulator_type?: string | null;
  start_time: string;
  end_time: string | null;
  trace_count: number;
  risk_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * SessionDetailResponse - Detalle completo de una sesión
 * FIX 1.2 Cortez12: Added missing optional fields from backend
 */
// FIX Cortez24 DEFECTO 3.1: Replace any with unknown for dynamic backend fields
export interface SessionDetailResponse extends SessionResponse {
  traces_summary: Record<string, number>;
  risks_summary: Record<string, number>;
  ai_dependency_score: number | null;
  // FIX 1.2 Cortez12: Optional fields from backend
  learning_objective?: Record<string, unknown> | null;
  cognitive_status?: Record<string, unknown> | null;
  session_metrics?: Record<string, unknown> | null;
}

// ==================== INTERACTION ====================

/**
 * InteractionCreate - Legacy alias for InteractionRequest
 * @deprecated Use InteractionRequest instead
 *
 * Backend expects: session_id, prompt, context?, cognitive_intent?
 */
// FIX Cortez24 DEFECTO 3.1: Replace any with unknown
export interface InteractionCreate {
  session_id: string;
  prompt: string;  // FIXED: Changed from student_input to prompt (backend field name)
  context?: Record<string, unknown>;
  cognitive_intent?: CognitiveIntent;
}

export interface InteractionRequest {
  session_id: string;
  prompt: string;
  context?: Record<string, unknown>;
  cognitive_intent?: CognitiveIntent;
}

export interface InteractionResponse {
  /**
   * FIX 2.1 Cortez12: 'id' is deprecated, use 'interaction_id' instead
   * Backend uses 'interaction_id' as the primary identifier
   * @deprecated Use interaction_id instead - will be removed in v2.0
   */
  id?: string;
  interaction_id: string;  // Primary identifier from backend
  session_id: string;
  response: string;
  agent_used: string;
  cognitive_state_detected: string;
  ai_involvement: number;
  blocked: boolean;
  block_reason: string | null;
  trace_id: string;
  risks_detected: string[];
  timestamp: string;
  tokens_used?: number;  // Optional metadata
}

export interface InteractionSummary {
  id: string;
  prompt_preview: string;
  agent_used: string;
  cognitive_state: string;
  ai_involvement: number;
  blocked: boolean;
  timestamp: string;
}

/**
 * InteractionHistory - Historial completo de interacciones de una sesión
 *
 * Alineado con backend/api/schemas/interaction.py InteractionHistory
 * Wrapper que incluye lista de interacciones + métricas agregadas
 */
export interface InteractionHistory {
  session_id: string;
  interactions: InteractionSummary[];
  total_interactions: number;
  avg_ai_involvement: number;
  blocked_count: number;
}

// ==================== TRACES ====================

/**
 * CognitiveTrace - Traza cognitiva N4 completa
 *
 * Alineado con backend/api/routers/traces.py TraceResponse
 * Incluye todos los campos N4 para análisis cognitivo profundo
 */
// FIX Cortez24 DEFECTO 3.1: Replace any with unknown
export interface CognitiveTrace {
  id: string;
  session_id: string;
  student_id: string;
  activity_id: string;
  trace_level: TraceLevel | string;
  interaction_type: string;
  cognitive_state: string | null;
  cognitive_intent: string | null;
  content: string;
  ai_involvement: number | null;
  // N4 Cognitive fields
  context: Record<string, unknown> | null;
  // FIX 6.1 Cortez12: Primary field name from backend (ORM uses trace_metadata)
  trace_metadata?: Record<string, unknown>;
  metadata?: Record<string, unknown>;  // Legacy alias for backwards compatibility
  decision_justification: string | null;
  alternatives_considered: string[] | null;
  strategy_type: string | null;
  // Relationships
  agent_id: string | null;
  parent_trace_id: string | null;
  // Timestamps
  timestamp: string;
  created_at?: string;
}

/**
 * Punto de evolución de dependencia de IA
 * Alineado con backend/api/schemas/cognitive_path.py AIDependencyPoint
 */
export interface AIDependencyPoint {
  timestamp: string;
  ai_involvement: number;
}

/**
 * Fase cognitiva del camino
 * Alineado con backend/api/schemas/cognitive_path.py CognitivePhase
 */
export interface CognitivePhase {
  phase_name: string;
  start_time: string;
  end_time: string | null;
  duration_minutes: number | null;
  interactions_count: number;
  ai_involvement_avg: number;
  risks_detected: string[];
  key_decisions: string[];
}

/**
 * Transición entre fases cognitivas
 * Alineado con backend/api/schemas/cognitive_path.py CognitiveTransition
 */
export interface CognitiveTransition {
  from_phase: string;
  to_phase: string;
  timestamp: string;
  trigger: string | null;
}

/**
 * Resumen del camino cognitivo
 * Alineado con backend/api/schemas/cognitive_path.py CognitivePathSummary
 */
export interface CognitivePathSummary {
  total_interactions: number;
  total_duration_minutes: number;
  blocked_interactions: number;
  ai_dependency_average: number;
  strategy_changes: number;
  risks_total: number;
  risks_by_level: Record<string, number>;
}

/**
 * Camino cognitivo reconstructivo completo
 * Alineado con backend/api/schemas/cognitive_path.py CognitivePath
 */
export interface CognitivePath {
  session_id: string;
  student_id: string;
  activity_id: string;
  start_time: string;
  end_time: string | null;
  summary: CognitivePathSummary;
  phases: CognitivePhase[];
  transitions: CognitiveTransition[];
  ai_dependency_evolution: AIDependencyPoint[];
  strategy_changes: string[];
}

// ==================== RISKS ====================

/**
 * Risk - Riesgo detectado por AR-IA
 *
 * Alineado con backend/api/routers/risks.py RiskResponse
 * FIX 3.3 Cortez12: Added missing fields from backend RiskResponse
 */
export interface Risk {
  id: string;
  session_id: string;
  student_id: string;
  activity_id: string;
  risk_type: string;
  risk_level: RiskLevel | string;
  dimension: string;
  description: string;
  // FIX 3.3 Cortez12: Added optional fields from backend
  impact?: string | null;
  root_cause?: string | null;
  impact_assessment?: string | null;
  evidence: string[];
  trace_ids: string[];
  recommendations: string[];
  pedagogical_intervention?: string | null;
  resolved: boolean;
  resolution_notes: string | null;
  resolved_at?: string | null;
  detected_by?: string;
  created_at: string;
  timestamp?: string;  // Legacy alias for created_at (frontend compatibility)
}

// ==================== EVALUATION ====================

/**
 * CompetencyLevel - Niveles de competencia del estudiante
 *
 * Alineado con backend/models/evaluation.py CompetencyLevel
 * Valores en español (lowercase) como usa el backend
 */
export enum CompetencyLevel {
  INICIAL = 'inicial',           // Principiante
  EN_DESARROLLO = 'en_desarrollo', // Desarrollando la competencia
  AUTONOMO = 'autonomo',         // Autónomo
  EXPERTO = 'experto',           // Nivel experto
}

/**
 * Helper para mostrar CompetencyLevel en UI de forma amigable
 */
export const CompetencyLevelLabels: Record<CompetencyLevel, string> = {
  [CompetencyLevel.INICIAL]: 'Inicial',
  [CompetencyLevel.EN_DESARROLLO]: 'En Desarrollo',
  [CompetencyLevel.AUTONOMO]: 'Autónomo',
  [CompetencyLevel.EXPERTO]: 'Experto',
};

/**
 * EvaluationDimension - Dimensión de evaluación
 * Alineado con backend/models/evaluation.py EvaluationDimension
 */
export interface EvaluationDimension {
  name: string;  // Nombre de la dimensión
  description: string;  // Descripción
  level: CompetencyLevel | string;  // Nivel alcanzado
  score: number;  // Puntuación (0-10)
  evidence: string[];  // Evidencias
  strengths: string[];  // Fortalezas
  weaknesses: string[];  // Debilidades
  recommendations: string[];  // Recomendaciones
  // Legacy fields for backwards compatibility
  dimension?: string;  // @deprecated Use name instead
  feedback?: string;  // @deprecated Use recommendations instead
}

/**
 * ConceptualError - Error conceptual detectado
 * Used in simplified frontend views
 */
export interface ConceptualError {
  error_type: string;
  description: string;
  location: string;
  severity: 'low' | 'medium' | 'high';
  recommendation: string;
}

/**
 * ReasoningAnalysis - Análisis del proceso de razonamiento
 * Alineado con backend/models/evaluation.py ReasoningAnalysis
 */
export interface ReasoningAnalysis {
  // Camino cognitivo
  cognitive_path: string[];  // Camino cognitivo seguido
  phases_completed: string[];  // Fases completadas (CognitivePhase enum values)
  strategy_changes: number;  // Cambios de estrategia
  self_corrections: number;  // Autocorrecciones
  ai_critiques: number;  // Críticas a la IA

  // Análisis de coherencia
  coherence_score: number;  // Coherencia entre decisiones y justificaciones (0-1)
  conceptual_errors: string[];  // Errores conceptuales detectados
  logical_fallacies: string[];  // Falacias lógicas detectadas

  // Autorregulación
  planning_quality: number;  // Calidad de planificación (0-1)
  monitoring_evidence: string[];  // Evidencias de monitoreo
  self_explanation_quality: number;  // Calidad de autoexplicación (0-1)

  // Legacy fields for backwards compatibility
  phases_identified?: string[];  // @deprecated Use cognitive_path
  phase_transitions?: string[];  // @deprecated
  reasoning_quality?: string;  // @deprecated Use coherence_score
  metacognitive_evidence?: string[];  // @deprecated Use monitoring_evidence
  problem_solving_strategy?: string;  // @deprecated
  completeness_score?: number;  // @deprecated
}

/**
 * GitAnalysis - Análisis de evolución del código vía Git
 * Alineado con backend/models/evaluation.py GitAnalysis
 */
export interface GitAnalysis {
  total_commits: number;  // Total de commits
  commit_messages_quality: number;  // Calidad de mensajes de commit (0-1)
  suspicious_jumps: string[];  // Saltos abruptos sospechosos
  evolution_coherence: number;  // Coherencia de la evolución (0-1)
  traces_linked: number;  // Commits vinculados a trazas N4

  // Legacy fields for backwards compatibility
  commits_analyzed?: number;  // @deprecated Use total_commits
  code_evolution_quality?: string;  // @deprecated Use evolution_coherence
  consistency_score?: number;  // @deprecated Use evolution_coherence
  patterns_detected?: string[];  // @deprecated Use suspicious_jumps
  ai_generated_code_percentage?: number;  // @deprecated
  copy_paste_detected?: boolean;  // @deprecated
}

/**
 * EvaluationReport - Reporte de evaluación completo
 * FIX 4.4 Cortez12: Changed overall_competency_level to use CompetencyLevel type
 */
export interface EvaluationReport {
  id: string;
  session_id: string;
  student_id: string;
  activity_id: string;
  overall_competency_level: CompetencyLevel | string;  // FIX 4.4: Use CompetencyLevel type
  overall_score: number;  // 0-10 scale
  dimensions: EvaluationDimension[];
  key_strengths: string[];
  improvement_areas: string[];
  reasoning_analysis: ReasoningAnalysis | null;
  git_analysis: GitAnalysis | null;
  ai_dependency_score: number;  // Score de dependencia de IA (0-1)
  ai_dependency_metrics: Record<string, unknown>;  // FIX Cortez24: Replace any with unknown
  timestamp: string;  // Alias for created_at (frontend compatibility)
  created_at?: string;
}

// ==================== API RESPONSE WRAPPERS ====================

export interface APIResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp?: string;
}

// FIX Cortez24 DEFECTO 3.1: Replace any with unknown
export interface APIError {
  success: false;
  error: {
    error_code: string;
    message: string;
    field: string | null;
    extra?: Record<string, unknown>;
  };
  timestamp: string;
}

export interface PaginationParams {
  page: number;
  page_size: number;
}

export interface PaginationMeta {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  success: boolean;
  data: T[];
  pagination: PaginationMeta;
  message?: string;
}

// ==================== HEALTH ====================

/**
 * HealthResponse - Response from GET /api/v1/health
 *
 * FIX 11.1 Cortez12: Note on HealthResponse vs HealthStatus
 * - HealthResponse (api.types.ts): Used for API response from /health endpoint
 * - HealthStatus (index.ts): Used for frontend health check UI with more detailed status
 *
 * Both are intentionally different:
 * - HealthResponse matches backend HealthCheck schema
 * - HealthStatus provides frontend-specific status values for UI rendering
 */
export interface HealthResponse {
  status: string;
  version: string;
  database: string;
  agents: Record<string, string>;
  timestamp: string;
}

// ==================== MESSAGE (for Chat UI) ====================

/**
 * Estados posibles de un mensaje durante el envío
 */
export type MessageStatus = 'pending' | 'sent' | 'retrying' | 'failed';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  status?: MessageStatus;  // Estado del mensaje (solo para user messages)
  retry_count?: number;    // Contador de reintentos
  metadata?: {
    agent_used?: string;
    cognitive_state?: string;
    ai_involvement?: number;
    blocked?: boolean;
    block_reason?: string;
    risks_detected?: string[];
  };
}

// ==================== ACTIVITIES ====================

export enum ActivityDifficulty {
  INICIAL = 'INICIAL',
  INTERMEDIO = 'INTERMEDIO',
  AVANZADO = 'AVANZADO',
}

export enum ActivityStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  ARCHIVED = 'archived',
}

export enum HelpLevel {
  MINIMO = 'minimo',
  BAJO = 'bajo',
  MEDIO = 'medio',
  ALTO = 'alto',
}

export interface PolicyConfig {
  max_help_level: HelpLevel;
  block_complete_solutions: boolean;
  require_justification: boolean;
  allow_code_snippets: boolean;
  risk_thresholds: Record<string, number>;
}

export interface ActivityCreate {
  activity_id: string;
  title: string;
  instructions: string;
  teacher_id: string;
  policies: PolicyConfig;
  description?: string;
  evaluation_criteria?: string[];
  subject?: string;
  difficulty?: ActivityDifficulty;
  estimated_duration_minutes?: number;
  tags?: string[];
}

export interface ActivityUpdate {
  title?: string;
  description?: string;
  instructions?: string;
  policies?: PolicyConfig;
  evaluation_criteria?: string[];
  subject?: string;
  difficulty?: ActivityDifficulty;
  estimated_duration_minutes?: number;
  tags?: string[];
}

export interface ActivityResponse {
  id: string;
  activity_id: string;
  title: string;
  description: string | null;
  instructions: string;
  evaluation_criteria: string[];
  teacher_id: string;
  policies: PolicyConfig;
  subject: string | null;
  difficulty: string | null;
  estimated_duration_minutes: number | null;
  tags: string[];
  status: string;
  published_at: string | null;
  created_at: string;
  updated_at: string;
}

// ==================== RISK ANALYSIS ====================

export interface RiskDimensionScore {
  score: number;  // 0-10 scale per dimension
  level: RiskLevel;
  indicators: string[];
}

/**
 * RiskAnalysis - Análisis de riesgo 5D completo
 *
 * FIX 3.5 Cortez12: Score scale clarification
 * - overall_score: Sum of 5 dimensions (each 0-10) = range 0-50
 * - Individual dimension scores: 0-10 scale
 * - risk_level: Derived from overall_score thresholds
 */
export interface RiskAnalysis {
  session_id: string;
  overall_score: number;  // 0-50 (sum of 5 dimensions, each 0-10)
  risk_level: RiskLevel;
  dimensions: {
    cognitive: RiskDimensionScore;
    ethical: RiskDimensionScore;
    epistemic: RiskDimensionScore;
    technical: RiskDimensionScore;
    governance: RiskDimensionScore;
  };
  top_risks: Array<{
    dimension: string;
    description: string;
    severity: RiskLevel;
    mitigation: string;
  }>;
  recommendations: string[];
}

// ==================== TRACEABILITY ====================

// FIX Cortez24 DEFECTO 3.1: Replace any with unknown
export interface TraceNode {
  id: string;
  level: 'N1' | 'N2' | 'N3' | 'N4';
  timestamp: string;
  data: unknown;
  metadata: {
    processing_time_ms?: number;
    tokens_used?: number;
    model?: string;
    transformations?: string[];
  };
}

export interface Trace {
  session_id: string;
  interaction_id: string;
  nodes: TraceNode[];
  total_latency_ms: number;
  total_tokens: number;
}

// ==================== GIT ANALYTICS ====================

export interface CommitMetrics {
  total_commits: number;
  avg_commits_per_day: number;
  total_insertions: number;
  total_deletions: number;
  code_churn: number;
  avg_commit_size: number;
  refactoring_ratio: number;
}

export interface Contributor {
  name: string;
  email: string;
  commits: number;
  insertions: number;
  deletions: number;
  percentage: number;
}

export interface CommitTrend {
  date: string;
  commits: number;
  insertions: number;
  deletions: number;
}

export interface GitAnalyticsData {
  repository: string;
  branch: string;
  period: {
    start: string;
    end: string;
  };
  metrics: CommitMetrics;
  contributors: Contributor[];
  trends: CommitTrend[];
  quality_indicators: {
    message_quality_score: number;
    avg_message_length: number;
    conventional_commits_ratio: number;
  };
}

// ==================== SIMULATORS ====================

/**
 * SimulatorRole - Roles de simulador profesional
 *
 * FIX 7.1-7.2 Cortez12: Updated to match backend SimulatorType enum
 * @deprecated Use SimulatorType from index.ts instead (union type is more accurate)
 */
export enum SimulatorRole {
  // V1 - Original simulators
  PRODUCT_OWNER = 'product_owner',
  SCRUM_MASTER = 'scrum_master',
  TECH_INTERVIEWER = 'tech_interviewer',
  INCIDENT_RESPONDER = 'incident_responder',
  CLIENT = 'client',
  DEVSECOPS = 'devsecops',
  // V2 - Enhanced simulators (Sprint 6)
  SENIOR_DEV = 'senior_dev',
  QA_ENGINEER = 'qa_engineer',
  SECURITY_AUDITOR = 'security_auditor',
  TECH_LEAD = 'tech_lead',
  DEMANDING_CLIENT = 'demanding_client',
}

// FIX Cortez24 DEFECTO 3.1: Replace any with unknown
export interface SimulatorInteractionRequest {
  role: SimulatorRole;
  message: string;
  context?: Record<string, unknown>;
}

export interface SimulatorInteractionResponse {
  role: SimulatorRole;
  response: string;
  evaluation: {
    score: number;
    feedback: string;
    suggestions: string[];
  };
  metadata: {
    model: string;
    tokens_used: number;
    processing_time_ms: number;
  };
}

// ==================== PROCESS EVALUATION (LLM-generated) ====================

/**
 * FIX 4.3 Cortez12: Type literal for autonomy level values
 */
export type AutonomyLevel = 'low' | 'medium' | 'high';

/**
 * FIX 4.3 Cortez12: Type literal for dimension level values
 */
export type DimensionLevel = 'novice' | 'competent' | 'proficient' | 'expert';

/**
 * DimensionScore - Puntuación de una dimensión del proceso
 * Alineado con backend/api/routers/evaluations.py DimensionScore
 */
export interface DimensionScore {
  score: number;  // 0-10
  level: DimensionLevel | string;  // FIX 4.3: Use type literal with string fallback
  evidence: string[];
  recommendations: string[];
}

/**
 * ProcessEvaluation - Evaluación completa del proceso cognitivo
 * Alineado con backend/api/routers/evaluations.py ProcessEvaluation
 *
 * Generated via POST /evaluations/{session_id}/generate
 */
export interface ProcessEvaluation {
  session_id: string;
  student_id: string;
  activity_id: string;

  // 5 dimensiones del proceso
  planning: DimensionScore;
  execution: DimensionScore;
  debugging: DimensionScore;
  reflection: DimensionScore;
  autonomy: DimensionScore;

  // Patrones generales
  autonomy_level: AutonomyLevel | string;  // FIX 4.3: Use type literal with string fallback
  metacognition_score: number;  // 0-10
  delegation_ratio: number;  // 0-1 (% delegación a IA)

  // Evidencia general
  overall_feedback: string;
  generated_at: string;
}