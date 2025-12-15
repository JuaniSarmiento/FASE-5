/**
 * Git Service - Integración Git (GIT-IA)
 *
 * Refactored to use BaseApiService for consistent API response handling.
 */
import { BaseApiService } from './base.service';
import { get } from './client';

export interface GitTrace {
  id: string;
  session_id: string;
  student_id: string;
  activity_id: string;
  timestamp: string;
  event_type: 'commit' | 'branch' | 'merge' | 'tag';
  commit_hash?: string;
  commit_message?: string;
  author_name?: string;
  author_email?: string;
  files_changed: GitFileChange[];
  patterns_detected: CodePattern[];
  lines_added: number;
  lines_deleted: number;
  complexity_delta?: number;
}

export interface GitFileChange {
  file_path: string;
  change_type: 'add' | 'modify' | 'delete' | 'rename';
  lines_added: number;
  lines_deleted: number;
  diff?: string;
}

export interface CodePattern {
  pattern_type: string;
  confidence: number;
  description: string;
  evidence: string[];
}

export interface GitEvolution {
  session_id: string;
  student_id: string;
  traces: GitTrace[];
  overall_quality: string;
  consistency_score: number;
  ai_assistance_indicators: string[];
  development_timeline: TimelineEvent[];
}

export interface TimelineEvent {
  timestamp: string;
  event_type: string;
  description: string;
  impact: 'low' | 'medium' | 'high';
}

export interface GitCorrelation {
  git_trace_id: string;
  cognitive_trace_ids: string[];
  correlation_score: number;
  insights: string[];
}

/**
 * Git Analytics response type
 * FIX Cortez20: Define type for reuse in method signature and get() call
 */
export interface GitAnalyticsResponse {
  repository: string;
  branch: string;
  period: { start: string; end: string };
  metrics: {
    total_commits: number;
    avg_commits_per_day: number;
    total_insertions: number;
    total_deletions: number;
    code_churn: number;
    avg_commit_size: number;
    refactoring_ratio: number;
  };
  contributors: Array<{
    name: string;
    email: string;
    commits: number;
    insertions: number;
    deletions: number;
    percentage: number;
  }>;
  trends: Array<{
    date: string;
    commits: number;
    insertions: number;
    deletions: number;
  }>;
  quality_indicators: {
    message_quality_score: number;
    avg_message_length: number;
    conventional_commits_ratio: number;
  };
}

interface SyncCommitsRequest {
  session_id: string;
  repo_path: string;
  since?: string;
  until?: string;
}

// FIX Cortez21 DEFECTO 3.5: Replace any[] with GitTrace[]
interface SyncCommitsResponse {
  session_id: string;
  commits_synced: number;
  git_traces: GitTrace[];
}

// FIX Cortez21 DEFECTO 3.6: Define types for data transformation
interface SessionListItem {
  id: string;
  student_id: string;
  activity_id?: string;
  status: string;
}

interface RawGitTrace {
  id: string;
  session_id: string;
  activity_id?: string;
  timestamp: string;
  event_type?: string;
  commit_hash?: string;
  commit_message?: string;
  author_name?: string;
  author_email?: string;
  files_changed?: GitFileChange[];
  detected_patterns?: string[];
  total_lines_added?: number;
  total_lines_deleted?: number;
  complexity_delta?: number;
}

/**
 * GitService - Uses BaseApiService for consistent response handling
 */
class GitService extends BaseApiService {
  constructor() {
    super('/git');
  }

  /**
   * Get Git traces for session
   * Backend route: GET /api/v1/git/session/{session_id}
   */
  async getSessionGitTraces(sessionId: string): Promise<GitTrace[]> {
    return this.get<GitTrace[]>(`/session/${sessionId}`);
  }

  /**
   * Sync Git commits for a session
   * Backend route: POST /api/v1/git/sync
   */
  async syncCommits(data: SyncCommitsRequest): Promise<SyncCommitsResponse> {
    return this.post<SyncCommitsResponse>('/sync', data);
  }

  /**
   * Get code evolution analysis
   * Backend route: GET /api/v1/git/session/{session_id}/evolution
   */
  async getCodeEvolution(sessionId: string): Promise<GitEvolution> {
    return this.get<GitEvolution>(`/session/${sessionId}/evolution`);
  }

  /**
   * Correlate Git with cognitive traces
   * Backend route: GET /api/v1/git/session/{session_id}/correlate
   */
  async correlateTraces(sessionId: string): Promise<GitCorrelation> {
    return this.get<GitCorrelation>(`/session/${sessionId}/correlate`);
  }

  /**
   * FIX 2.2: Get repository analytics for a period (Cortez2 audit)
   * Backend route: GET /api/v1/git-analytics?period={period}
   * FIX Cortez20: Use GitAnalyticsResponse type for consistency
   */
  async getAnalytics(period: string = '30d'): Promise<GitAnalyticsResponse> {
    // FIX Cortez20: Use get() helper which extracts data from APIResponse wrapper
    // git-analytics endpoint is different from /git baseUrl
    return get<GitAnalyticsResponse>(`/git-analytics?period=${period}`);
  }

  /**
   * Get student's Git history by querying their sessions
   * Backend doesn't have direct student endpoint, so we query sessions first
   * then aggregate git traces from each session
   *
   * FIX Cortez21 DEFECTO 3.6, 7.1: Replace any types and add logging to catch blocks
   */
  async getStudentGitHistory(studentId: string): Promise<GitTrace[]> {
    try {
      // Step 1: Get all sessions for the student using client helper
      // FIX Cortez21: Use typed SessionListItem instead of any
      const sessionsData = await get<SessionListItem[]>(`/sessions?student_id=${studentId}`);
      const sessions = Array.isArray(sessionsData) ? sessionsData : [];

      if (sessions.length === 0) {
        return [];
      }

      // Step 2: Get git traces for each session in parallel
      // FIX Cortez21: Use typed SessionListItem instead of any
      const tracePromises = sessions.map(async (session: SessionListItem) => {
        try {
          const traces = await this.get<GitTrace[]>(`/session/${session.id}`);
          return Array.isArray(traces) ? traces : [];
        } catch (error) {
          // FIX Cortez21 DEFECTO 7.1: Add logging with context
          if (import.meta.env.DEV) {
            console.warn(`Failed to get git traces for session ${session.id}:`, error);
          }
          return [];
        }
      });

      const traceResults = await Promise.all(tracePromises);

      // Step 3: Flatten and map to GitTrace interface
      // FIX Cortez21: Use typed RawGitTrace instead of any
      // FIX Cortez24 DEFECTO 1.1: Type narrowing for event_type
      const validEventTypes = ['commit', 'branch', 'merge', 'tag'] as const;
      const allTraces: GitTrace[] = traceResults
        .flat()
        .map((t: RawGitTrace) => ({
          id: t.id,
          session_id: t.session_id,
          student_id: studentId,
          activity_id: t.activity_id || '',
          timestamp: t.timestamp,
          event_type: (validEventTypes.includes(t.event_type as typeof validEventTypes[number])
            ? t.event_type as GitTrace['event_type']
            : 'commit'),
          commit_hash: t.commit_hash,
          commit_message: t.commit_message,
          author_name: t.author_name,
          author_email: t.author_email,
          files_changed: t.files_changed || [],
          patterns_detected: (t.detected_patterns || []).map((p: string) => ({
            pattern_type: p,
            confidence: 1.0,
            description: p,
            evidence: [],
          })),
          lines_added: t.total_lines_added || 0,
          lines_deleted: t.total_lines_deleted || 0,
          complexity_delta: t.complexity_delta,
        }));

      return allTraces;
    } catch (error) {
      // FIX Cortez21: Add context to error logging
      if (import.meta.env.DEV) {
        console.error(`Error fetching git history for student ${studentId}:`, error);
      }
      return [];
    }
  }
}

export const gitService = new GitService();