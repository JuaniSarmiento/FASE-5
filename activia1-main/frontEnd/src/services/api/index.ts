/**
 * Punto de entrada para todos los servicios de API
 *
 * Servicios disponibles:
 * - sessionsService: Gestión de sesiones de aprendizaje
 * - interactionsService: Procesamiento de interacciones estudiante-IA
 * - tracesService: Consulta de trazabilidad cognitiva N4
 * - risksService: Consulta de riesgos detectados (AR-IA)
 * - healthService: Health checks del sistema
 * - activitiesService: Gestión de actividades (docentes)
 * - simulatorsService: Simuladores profesionales (S-IA-X)
 * - evaluationsService: Evaluador de procesos (E-IA-Proc)
 * - gitService: Integración Git (GIT-IA)
 * - reportsService: Generación de reportes
 * - authService: Autenticación y autorización
 * - adminService: Administración del sistema
 * - cognitivePathService: Camino cognitivo reconstructivo (/cognitive-path)
 * - institutionalRisksService: Gestión de riesgos institucionales (/admin/risks)
 *
 * NOTA: Los tipos principales están en @/types/api.types.ts
 * Importar desde allí para evitar duplicación.
 */

// === Services ===
export { sessionsService } from './sessions.service';
export type {
  SessionHistoryParams,
  SessionSummary,
  ProgressAggregation,
  SessionHistoryResponse,
} from './sessions.service';
export { interactionsService } from './interactions.service';
export { tracesService } from './traces.service';
export type { PaginatedTracesResponse, TracesQueryParams } from './traces.service';
export { risksService } from './risks.service';
export { healthService } from './health.service';
export { activitiesService } from './activities.service';
export { exercisesService } from './exercises.service';
export type { CodeSubmission } from './exercises.service';
export { simulatorsService } from './simulators.service';
export { evaluationsService } from './evaluations.service';
export { gitService } from './git.service';
export { reportsService } from './reports.service';
export { authService } from './auth.service';
export { adminService } from './admin.service';
export { cognitivePathService } from './cognitivePath.service';
export { institutionalRisksService } from './institutionalRisks.service';

// === Types from auth.service (user-specific) ===
export type { User, LoginRequest, LoginResponse, RegisterRequest, RegisterResponse } from './auth.service';

// === Types from admin.service (admin-specific) ===
export type { LLMConfiguration, LLMUsageStats, SystemMetrics } from './admin.service';

// === Types from simulators.service ===
export type {
  SimulatorType,
  SimulatorStatus,
  SimulatorInfo,
  SimulatorInteraction,
  SimulatorResponse,
  SimulatorSession,
  SimulatorEvaluation,
  // Sprint 6 - Enhanced Simulators (S-IA-X v2)
  SimulatorInfoV2,
  SimulatorScenario,
  StartSimulationRequest,
  StartSimulationResponse,
  StudentSimulatorStats,
} from './simulators.service';

// === Types from git.service ===
export type {
  GitTrace,
  GitFileChange,
  CodePattern,
  GitEvolution,
  TimelineEvent,
  GitCorrelation,
} from './git.service';

// === Types from reports.service ===
export type {
  ActivityReport,
  StudentPerformance,
  RiskSummary,
  LearningAnalytics,
  AgentUsage,
  CompetencyTrend,
  RiskTrendData,
  CohortReportRequest,
  CohortReport,
  RiskDashboardRequest,
  RiskDashboardReport,
  TeacherReport,
  ExportHistoryItem,
} from './reports.service';

// === Types from institutionalRisks.service ===
export type {
  RiskAlert,
  RiskScanRequest,
  RiskScanResponse,
  RiskDashboard,
  RemediationPlan,
  RecommendedAction,
  SuccessMetrics,
  CreateRemediationPlanRequest,
  UpdatePlanStatusRequest,
  AlertSeverity,
  AlertStatus,
  AlertScope,
  PlanStatus,
} from './institutionalRisks.service';

// === Types from evaluations.service (teacher tools + LLM evaluations) ===
export type {
  StudentComparison,
  StudentComparisonData,
  AggregateStatistics,
  StudentEvaluationSummary,  // @deprecated - use StudentComparisonData
  ComparisonMetric,          // @deprecated - use AggregateStatistics
  TeacherAlertsResponse,
  TeacherAlert,
  // LLM-generated process evaluation
  ProcessEvaluationResponse,
} from './evaluations.service';

// Re-export central types for convenience (canonical source: @/types/api.types.ts)
export {
  CompetencyLevel,
} from './evaluations.service';

export type {
  EvaluationReport,
  EvaluationDimension,
  ReasoningAnalysis,
  GitAnalysis,
  ConceptualError,
} from './evaluations.service';

// === Types from activities.service ===
export type { ActivityListParams } from './activities.service';

// === Re-export client for advanced usage ===
export { default as apiClient } from './client';

// === Re-export base service for custom services ===
export { BaseApiService } from './base.service';