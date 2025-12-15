import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { sessionsService } from '../services/api';
import { Session } from '../types';
import {
  TrendingUp,
  Brain,
  Target,
  Activity,
  Calendar,
  ArrowUp,
  Minus,
  Loader2,
  PieChart
} from 'lucide-react';

export default function AnalyticsPage() {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const abortController = new AbortController();

    const fetchData = async () => {
      try {
        // FIX 2.5: Correct signature - sessionsService.list(studentId, pagination?)
        const response = await sessionsService.list(user?.id || '');

        // Only update state if component is still mounted
        if (!abortController.signal.aborted) {
          // FIX 2.5: Extract data array from paginated response
          setSessions(response?.data || []);
        }
      } catch (error) {
        // Don't log errors if the request was aborted
        if (!abortController.signal.aborted) {
          console.error('Error fetching data:', error);
        }
      } finally {
        if (!abortController.signal.aborted) {
          setIsLoading(false);
        }
      }
    };

    fetchData();

    // Cleanup: abort pending requests when component unmounts
    return () => {
      abortController.abort();
    };
  }, [user]);

  // Calculate statistics
  const totalSessions = sessions.length;
  const totalInteractions = sessions.reduce((acc, s) => acc + (s.trace_count || 0), 0);
  const avgInteractionsPerSession = totalSessions > 0 ? Math.round(totalInteractions / totalSessions) : 0;
  const completedSessions = sessions.filter(s => s.status === 'completed').length;
  const completionRate = totalSessions > 0 ? Math.round((completedSessions / totalSessions) * 100) : 0;

  // Sessions by mode
  const sessionsByMode = {
    TUTOR: sessions.filter(s => s.mode === 'TUTOR').length,
    SIMULATOR: sessions.filter(s => s.mode === 'SIMULATOR').length,
    PRACTICE: sessions.filter(s => s.mode === 'PRACTICE').length
  };

  // FIX 2.7: Calculate weekly activity from real session data
  const calculateWeeklyActivity = () => {
    const days = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    const weekData = days.map(day => ({ day, sessions: 0, interactions: 0 }));

    // Get sessions from last 7 days
    const now = new Date();
    const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);

    sessions
      .filter(s => new Date(s.created_at) >= weekAgo)
      .forEach(session => {
        const dayIndex = new Date(session.created_at).getDay();
        weekData[dayIndex].sessions += 1;
        weekData[dayIndex].interactions += session.trace_count || 0;
      });

    // Reorder to start with Monday (Lun)
    return [...weekData.slice(1), weekData[0]];
  };

  const weeklyActivity = calculateWeeklyActivity();
  const maxInteractions = Math.max(...weeklyActivity.map(d => d.interactions), 1);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-[var(--accent-primary)] animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">
          Analíticas de Aprendizaje
        </h1>
        <p className="text-[var(--text-secondary)]">
          Visualiza tu progreso y métricas de aprendizaje
        </p>
      </div>

      {/* Main Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <div className="flex items-center gap-1 text-green-400 text-sm">
              <ArrowUp className="w-4 h-4" />
              12%
            </div>
          </div>
          <p className="text-3xl font-bold text-[var(--text-primary)] mb-1">{totalSessions}</p>
          <p className="text-sm text-[var(--text-secondary)]">Sesiones totales</p>
        </div>

        <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div className="flex items-center gap-1 text-green-400 text-sm">
              <ArrowUp className="w-4 h-4" />
              8%
            </div>
          </div>
          <p className="text-3xl font-bold text-[var(--text-primary)] mb-1">{totalInteractions}</p>
          <p className="text-sm text-[var(--text-secondary)]">Interacciones</p>
        </div>

        <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
              <Target className="w-6 h-6 text-white" />
            </div>
            <div className="flex items-center gap-1 text-[var(--text-muted)] text-sm">
              <Minus className="w-4 h-4" />
              0%
            </div>
          </div>
          <p className="text-3xl font-bold text-[var(--text-primary)] mb-1">{completionRate}%</p>
          <p className="text-sm text-[var(--text-secondary)]">Tasa de completitud</p>
        </div>

        <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-white" />
            </div>
            <div className="flex items-center gap-1 text-green-400 text-sm">
              <ArrowUp className="w-4 h-4" />
              5%
            </div>
          </div>
          <p className="text-3xl font-bold text-[var(--text-primary)] mb-1">{avgInteractionsPerSession}</p>
          <p className="text-sm text-[var(--text-secondary)]">Promedio por sesión</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weekly Activity Chart */}
        <div className="lg:col-span-2 bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-[var(--text-primary)]">Actividad Semanal</h3>
              <p className="text-sm text-[var(--text-muted)]">Interacciones por día</p>
            </div>
            <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-[var(--bg-tertiary)]">
              <Calendar className="w-4 h-4 text-[var(--text-muted)]" />
              <span className="text-sm text-[var(--text-secondary)]">Esta semana</span>
            </div>
          </div>

          <div className="flex items-end justify-between h-48 gap-4">
            {weeklyActivity.map((day, i) => (
              <div key={i} className="flex-1 flex flex-col items-center">
                <div 
                  className="w-full rounded-t-lg bg-gradient-to-t from-indigo-500 to-purple-600 transition-all duration-500 hover:opacity-80"
                  style={{ 
                    height: `${maxInteractions > 0 ? (day.interactions / maxInteractions) * 100 : 0}%`,
                    minHeight: day.interactions > 0 ? '8px' : '0'
                  }}
                />
                <div className="mt-2 text-center">
                  <p className="text-xs text-[var(--text-muted)]">{day.day}</p>
                  <p className="text-sm font-medium text-[var(--text-secondary)]">{day.interactions}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sessions by Mode */}
        <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-[var(--text-primary)]">Por Modo</h3>
              <p className="text-sm text-[var(--text-muted)]">Distribución de sesiones</p>
            </div>
            <PieChart className="w-5 h-5 text-[var(--text-muted)]" />
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-[var(--text-secondary)]">Tutor IA</span>
                <span className="text-sm font-medium text-[var(--text-primary)]">{sessionsByMode.TUTOR}</span>
              </div>
              <div className="h-2 rounded-full bg-[var(--bg-tertiary)] overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-500 to-pink-600 transition-all duration-500"
                  style={{ width: `${totalSessions > 0 ? (sessionsByMode.TUTOR / totalSessions) * 100 : 0}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-[var(--text-secondary)]">Simuladores</span>
                <span className="text-sm font-medium text-[var(--text-primary)]">{sessionsByMode.SIMULATOR}</span>
              </div>
              <div className="h-2 rounded-full bg-[var(--bg-tertiary)] overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-cyan-600 transition-all duration-500"
                  style={{ width: `${totalSessions > 0 ? (sessionsByMode.SIMULATOR / totalSessions) * 100 : 0}%` }}
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-[var(--text-secondary)]">Práctica</span>
                <span className="text-sm font-medium text-[var(--text-primary)]">{sessionsByMode.PRACTICE}</span>
              </div>
              <div className="h-2 rounded-full bg-[var(--bg-tertiary)] overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 to-emerald-600 transition-all duration-500"
                  style={{ width: `${totalSessions > 0 ? (sessionsByMode.PRACTICE / totalSessions) * 100 : 0}%` }}
                />
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-[var(--border-color)]">
            <div className="flex items-center justify-between text-sm">
              <span className="text-[var(--text-muted)]">Total</span>
              <span className="font-medium text-[var(--text-primary)]">{totalSessions} sesiones</span>
            </div>
          </div>
        </div>
      </div>

      {/* Learning Insights */}
      <div className="bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 rounded-2xl border border-[var(--accent-primary)]/20 p-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
              📊 Insights de Aprendizaje
            </h3>
            <p className="text-[var(--text-secondary)] mb-4">
              Basado en tu actividad reciente, aquí hay algunas observaciones:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl bg-[var(--bg-card)]/50 backdrop-blur-sm">
                <p className="text-sm font-medium text-[var(--text-primary)] mb-1">Mejor día</p>
                <p className="text-xs text-[var(--text-muted)]">
                  {/* FIX 2.7: Calculate from real data */}
                  {weeklyActivity.reduce((best, day) => day.interactions > best.interactions ? day : best, weeklyActivity[0]).day} con {Math.max(...weeklyActivity.map(d => d.interactions))} interacciones
                </p>
              </div>
              <div className="p-4 rounded-xl bg-[var(--bg-card)]/50 backdrop-blur-sm">
                <p className="text-sm font-medium text-[var(--text-primary)] mb-1">Modo favorito</p>
                <p className="text-xs text-[var(--text-muted)]">
                  {/* FIX 2.7: Calculate from real data */}
                  {sessionsByMode.TUTOR >= sessionsByMode.SIMULATOR && sessionsByMode.TUTOR >= sessionsByMode.PRACTICE
                    ? `Tutor IA (${sessionsByMode.TUTOR} sesiones)`
                    : sessionsByMode.SIMULATOR >= sessionsByMode.PRACTICE
                    ? `Simuladores (${sessionsByMode.SIMULATOR} sesiones)`
                    : `Práctica (${sessionsByMode.PRACTICE} sesiones)`}
                </p>
              </div>
              <div className="p-4 rounded-xl bg-[var(--bg-card)]/50 backdrop-blur-sm">
                <p className="text-sm font-medium text-[var(--text-primary)] mb-1">Sesiones esta semana</p>
                <p className="text-xs text-[var(--text-muted)]">
                  {/* FIX 2.7: Calculate from real data */}
                  {weeklyActivity.reduce((sum, d) => sum + d.sessions, 0)} sesiones
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-6">
        <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Actividad Reciente</h3>
        
        {sessions.length === 0 ? (
          <p className="text-[var(--text-muted)] text-center py-8">
            No hay actividad reciente. ¡Comienza una sesión!
          </p>
        ) : (
          <div className="space-y-4">
            {sessions.slice(0, 5).map((session) => (
              <div 
                key={session.id}
                className="flex items-center justify-between p-4 rounded-xl bg-[var(--bg-tertiary)] hover:bg-[var(--bg-hover)] transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    session.mode === 'TUTOR' ? 'bg-purple-500/10 text-purple-400' :
                    session.mode === 'SIMULATOR' ? 'bg-blue-500/10 text-blue-400' :
                    'bg-green-500/10 text-green-400'
                  }`}>
                    {session.mode === 'TUTOR' ? <Brain className="w-5 h-5" /> :
                     session.mode === 'SIMULATOR' ? <Activity className="w-5 h-5" /> :
                     <Target className="w-5 h-5" />}
                  </div>
                  <div>
                    <p className="font-medium text-[var(--text-primary)]">{session.activity_id}</p>
                    <p className="text-sm text-[var(--text-muted)]">{session.mode}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-[var(--text-secondary)]">{session.trace_count} interacciones</p>
                  <p className="text-xs text-[var(--text-muted)]">
                    {new Date(session.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
