/**
 * Institutional Risks Service - Gestión de riesgos institucionales
 *
 * Backend router: /admin/risks
 * Sprint 5-6 - HU-DOC-010
 *
 * Provides access to:
 * - Risk scanning and alerts
 * - Remediation planning
 * - Institutional risk dashboard
 */
import { BaseApiService } from './base.service';

// =============================================================================
// TYPES
// =============================================================================

export type AlertSeverity = 'low' | 'medium' | 'high' | 'critical';
export type AlertStatus = 'pending' | 'acknowledged' | 'in_progress' | 'resolved';
export type AlertScope = 'student' | 'activity' | 'course' | 'institution';
export type PlanStatus = 'draft' | 'active' | 'completed' | 'cancelled';

/**
 * Risk Alert - Alerta de riesgo institucional
 */
export interface RiskAlert {
  id: string;
  alert_type: string;
  severity: AlertSeverity;
  scope: AlertScope;
  title: string;
  description: string;
  affected_students: string[];
  affected_activities: string[];
  evidence: string[];
  recommendations: string[];
  status: AlertStatus;
  assigned_to?: string;
  created_at: string;
  updated_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
  resolution_notes?: string;
}

/**
 * Risk Scan Request
 */
export interface RiskScanRequest {
  scope: AlertScope;
  activity_id?: string;
  course_id?: string;
  start_date?: string;
  end_date?: string;
  include_historical?: boolean;
}

/**
 * Risk Scan Response
 */
export interface RiskScanResponse {
  scan_id: string;
  scope: AlertScope;
  alerts_generated: number;
  alerts: RiskAlert[];
  scan_timestamp: string;
  next_scan_recommended?: string;
}

/**
 * Risk Dashboard Data
 */
export interface RiskDashboard {
  summary: {
    total_alerts: number;
    pending_alerts: number;
    critical_alerts: number;
    resolved_this_week: number;
  };
  alerts_by_severity: Record<AlertSeverity, number>;
  alerts_by_type: Record<string, number>;
  recent_alerts: RiskAlert[];
  trends: {
    date: string;
    alerts_created: number;
    alerts_resolved: number;
  }[];
}

/**
 * Recommended Action for Remediation Plan
 */
export interface RecommendedAction {
  action_id: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  estimated_effort: string;
  resources_needed?: string[];
  deadline?: string;
  completed: boolean;
}

/**
 * Success Metrics for Remediation Plan
 */
export interface SuccessMetrics {
  target_metric: string;
  current_value: number;
  target_value: number;
  measurement_method: string;
}

/**
 * Remediation Plan
 */
export interface RemediationPlan {
  id: string;
  student_id: string;
  alert_ids: string[];
  plan_type: string;
  title: string;
  description: string;
  status: PlanStatus;
  actions: RecommendedAction[];
  success_metrics: SuccessMetrics[];
  start_date: string;
  target_end_date: string;
  actual_end_date?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  notes?: string;
}

/**
 * Create Remediation Plan Request
 */
export interface CreateRemediationPlanRequest {
  student_id: string;
  alert_ids: string[];
  plan_type: string;
  title: string;
  description: string;
  actions: Omit<RecommendedAction, 'action_id' | 'completed'>[];
  success_metrics: SuccessMetrics[];
  start_date: string;
  target_end_date: string;
}

/**
 * Update Remediation Plan Status Request
 */
export interface UpdatePlanStatusRequest {
  status: PlanStatus;
  notes?: string;
  actual_end_date?: string;
}

// =============================================================================
// SERVICE
// =============================================================================

/**
 * InstitutionalRisksService - Backend router: /admin/risks
 */
class InstitutionalRisksService extends BaseApiService {
  constructor() {
    super('/admin/risks');
  }

  // ===========================================================================
  // RISK SCANNING
  // ===========================================================================

  /**
   * Scan for institutional risks
   * Backend route: POST /api/v1/admin/risks/scan
   */
  async scanForRisks(request: RiskScanRequest): Promise<RiskScanResponse> {
    return this.post<RiskScanResponse>('/scan', request);
  }

  // ===========================================================================
  // ALERTS
  // ===========================================================================

  /**
   * Get all risk alerts
   * Backend route: GET /api/v1/admin/risks/alerts
   */
  async getAlerts(params?: {
    severity?: AlertSeverity;
    status?: AlertStatus;
    scope?: AlertScope;
    limit?: number;
  }): Promise<RiskAlert[]> {
    const queryParams = new URLSearchParams();
    if (params?.severity) queryParams.append('severity', params.severity);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.scope) queryParams.append('scope', params.scope);
    if (params?.limit) queryParams.append('limit', params.limit.toString());

    const query = queryParams.toString();
    return this.get<RiskAlert[]>(`/alerts${query ? `?${query}` : ''}`);
  }

  /**
   * Get risk dashboard
   * Backend route: GET /api/v1/admin/risks/dashboard
   */
  async getDashboard(): Promise<RiskDashboard> {
    return this.get<RiskDashboard>('/dashboard');
  }

  /**
   * Assign alert to user
   * Backend route: POST /api/v1/admin/risks/alerts/{alert_id}/assign
   */
  async assignAlert(alertId: string, userId: string): Promise<RiskAlert> {
    return this.post<RiskAlert>(`/alerts/${alertId}/assign`, { user_id: userId });
  }

  /**
   * Acknowledge an alert
   * Backend route: POST /api/v1/admin/risks/alerts/{alert_id}/acknowledge
   */
  async acknowledgeAlert(alertId: string): Promise<RiskAlert> {
    return this.post<RiskAlert>(`/alerts/${alertId}/acknowledge`);
  }

  /**
   * Resolve an alert
   * Backend route: POST /api/v1/admin/risks/alerts/{alert_id}/resolve
   */
  async resolveAlert(alertId: string, resolutionNotes: string): Promise<RiskAlert> {
    return this.post<RiskAlert>(`/alerts/${alertId}/resolve`, {
      resolution_notes: resolutionNotes,
    });
  }

  // ===========================================================================
  // REMEDIATION PLANS
  // ===========================================================================

  /**
   * Create a remediation plan
   * Backend route: POST /api/v1/admin/risks/remediation
   */
  async createRemediationPlan(plan: CreateRemediationPlanRequest): Promise<RemediationPlan> {
    return this.post<RemediationPlan>('/remediation', plan);
  }

  /**
   * Get a remediation plan
   * Backend route: GET /api/v1/admin/risks/remediation/{plan_id}
   */
  async getRemediationPlan(planId: string): Promise<RemediationPlan> {
    return this.get<RemediationPlan>(`/remediation/${planId}`);
  }

  /**
   * Update remediation plan status
   * Backend route: PUT /api/v1/admin/risks/remediation/{plan_id}/status
   */
  async updatePlanStatus(planId: string, update: UpdatePlanStatusRequest): Promise<RemediationPlan> {
    return this.put<RemediationPlan>(`/remediation/${planId}/status`, update);
  }
}

export const institutionalRisksService = new InstitutionalRisksService();