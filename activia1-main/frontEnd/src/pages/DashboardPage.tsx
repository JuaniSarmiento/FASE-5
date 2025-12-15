import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { sessionsService, healthService } from '../services/api';
// FIX Cortez16: Use HealthResponse from api (healthService.check returns HealthResponse)
import { Session, HealthResponse } from '../types';
import {
  Sparkles,
  MessageSquare,
  Code,
  Users,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  Activity,
  Brain,
  Target,
  Zap
} from 'lucide-react';

interface StatCard {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: React.ElementType;
  color: string;
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<Session[]>([]);
  // FIX Cortez16: Use HealthResponse type to match healthService.check() return type
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const abortController = new AbortController();

    const fetchData = async () => {
      try {
        // FIX 2.5: Correct signature - sessionsService.list(studentId, pagination?)
        const [sessionsRes, healthRes] = await Promise.all([
          sessionsService.list(user?.id || ''),
          healthService.check()
        ]);

        // Only update state if component is still mounted
        if (!abortController.signal.aborted) {
          // FIX 2.5: Extract data array from paginated response
          setSessions(sessionsRes?.data || []);
          setHealth(healthRes);
        }
      } catch (error) {
        // Don't log errors if the request was aborted
        if (!abortController.signal.aborted) {
          console.error('Error fetching dashboard data:', error);
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

  const activeSessions = sessions.filter(s => s.status === 'active').length;
  const completedSessions = sessions.filter(s => s.status === 'completed').length;
  const totalInteractions = sessions.reduce((acc, s) => acc + (s.trace_count || 0), 0);

  const stats: StatCard[] = [
    {
      title: 'Sesiones Activas',
      value: activeSessions,
      // FIX 4.6: Use real data instead of hardcoded mock
      change: activeSessions > 0 ? 'En progreso' : 'Sin sesiones',
      changeType: activeSessions > 0 ? 'positive' : 'neutral',
      icon: Activity,
      color: 'from-green-500 to-emerald-600'
    },
    {
      title: 'Sesiones Completadas',
      value: completedSessions,
      change: `${sessions.length} total`,
      changeType: 'neutral',
      icon: CheckCircle,
      color: 'from-blue-500 to-cyan-600'
    },
    {
      title: 'Interacciones',
      value: totalInteractions,
      change: 'Con tutor IA',
      changeType: 'neutral',
      icon: MessageSquare,
      color: 'from-purple-500 to-pink-600'
    },
    {
      title: 'Progreso General',
      // FIX 4.6: Calculate from real data instead of hardcoded mock
      value: completedSessions > 0 ? `${Math.round((completedSessions / Math.max(sessions.length, 1)) * 100)}%` : '0%',
      change: `${sessions.length} sesiones`,
      changeType: sessions.length > 0 ? 'neutral' : 'neutral',
      icon: TrendingUp,
      color: 'from-orange-500 to-red-600'
    }
  ];

  const quickActions = [
    {
      title: 'Continuar Aprendiendo',
      description: 'Retoma tu última sesión con el tutor IA',
      icon: Brain,
      path: '/tutor',
      gradient: 'from-indigo-500 to-purple-600'
    },
    {
      title: 'Practicar Código',
      description: 'Resuelve ejercicios de programación',
      icon: Code,
      path: '/exercises',
      gradient: 'from-green-500 to-emerald-600'
    },
    {
      title: 'Simuladores',
      description: 'Practica con roles profesionales',
      icon: Users,
      path: '/simulators',
      gradient: 'from-orange-500 to-pink-600'
    }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-4 border-[var(--accent-primary)] border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Welcome Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">
            ¡Bienvenido, {user?.full_name || user?.username}! 👋
          </h1>
          <p className="text-[var(--text-secondary)]">
            Continúa tu viaje de aprendizaje con inteligencia artificial
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm ${
            health?.status === 'healthy' 
              ? 'bg-green-500/10 text-green-500' 
              : 'bg-yellow-500/10 text-yellow-500'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              health?.status === 'healthy' ? 'bg-green-500' : 'bg-yellow-500'
            } animate-pulse`}></span>
            Sistema {health?.status === 'healthy' ? 'Online' : 'Degradado'}
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div 
            key={index}
            className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-6 hover:border-[var(--border-light)] transition-all duration-300 group"
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
              {stat.change && (
                <span className={`text-xs px-2 py-1 rounded-full ${
                  stat.changeType === 'positive' ? 'bg-green-500/10 text-green-500' :
                  stat.changeType === 'negative' ? 'bg-red-500/10 text-red-500' :
                  'bg-[var(--bg-tertiary)] text-[var(--text-muted)]'
                }`}>
                  {stat.change}
                </span>
              )}
            </div>
            <h3 className="text-3xl font-bold text-[var(--text-primary)] mb-1">
              {stat.value}
            </h3>
            <p className="text-sm text-[var(--text-secondary)]">{stat.title}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-xl font-semibold text-[var(--text-primary)] mb-4">
          Acciones Rápidas
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action, index) => (
            <Link
              key={index}
              to={action.path}
              className="group bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-6 hover:border-[var(--accent-primary)]/50 transition-all duration-300 hover:shadow-lg hover:shadow-[var(--accent-primary)]/10"
            >
              <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${action.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                <action.icon className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2 group-hover:text-[var(--accent-primary)] transition-colors">
                {action.title}
              </h3>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                {action.description}
              </p>
              <div className="flex items-center text-[var(--accent-primary)] text-sm font-medium">
                Comenzar
                <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-2 transition-transform" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Sessions */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-[var(--text-primary)]">
            Sesiones Recientes
          </h2>
          <Link 
            to="/sessions" 
            className="text-sm text-[var(--accent-primary)] hover:text-[var(--accent-secondary)] flex items-center gap-1"
          >
            Ver todas
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {sessions.length === 0 ? (
          <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-12 text-center">
            <div className="w-16 h-16 rounded-2xl bg-[var(--bg-tertiary)] flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-8 h-8 text-[var(--text-muted)]" />
            </div>
            <h3 className="text-lg font-medium text-[var(--text-primary)] mb-2">
              No hay sesiones aún
            </h3>
            <p className="text-[var(--text-secondary)] mb-6">
              Comienza tu primera sesión con el tutor IA
            </p>
            <Link
              to="/tutor"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-medium hover:opacity-90 transition-opacity"
            >
              <MessageSquare className="w-5 h-5" />
              Iniciar Sesión
            </Link>
          </div>
        ) : (
          <div className="bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[var(--border-color)]">
                  <th className="px-6 py-4 text-left text-sm font-medium text-[var(--text-muted)]">Actividad</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-[var(--text-muted)]">Modo</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-[var(--text-muted)]">Estado</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-[var(--text-muted)]">Interacciones</th>
                  <th className="px-6 py-4 text-left text-sm font-medium text-[var(--text-muted)]">Fecha</th>
                </tr>
              </thead>
              <tbody>
                {sessions.slice(0, 5).map((session) => (
                  <tr 
                    key={session.id} 
                    className="border-b border-[var(--border-color)] hover:bg-[var(--bg-hover)] transition-colors"
                  >
                    <td className="px-6 py-4">
                      <span className="text-[var(--text-primary)] font-medium">
                        {session.activity_id}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                        session.mode === 'TUTOR' ? 'bg-purple-500/10 text-purple-400' :
                        session.mode === 'SIMULATOR' ? 'bg-blue-500/10 text-blue-400' :
                        'bg-green-500/10 text-green-400'
                      }`}>
                        {session.mode === 'TUTOR' && <Brain className="w-3 h-3" />}
                        {session.mode === 'SIMULATOR' && <Users className="w-3 h-3" />}
                        {session.mode === 'PRACTICE' && <Target className="w-3 h-3" />}
                        {session.mode}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${
                        session.status === 'active' ? 'bg-green-500/10 text-green-400' :
                        session.status === 'completed' ? 'bg-blue-500/10 text-blue-400' :
                        'bg-yellow-500/10 text-yellow-400'
                      }`}>
                        {session.status === 'active' && <Zap className="w-3 h-3" />}
                        {session.status === 'completed' && <CheckCircle className="w-3 h-3" />}
                        {session.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-[var(--text-secondary)]">
                        {session.trace_count}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-[var(--text-muted)] text-sm">
                        {new Date(session.created_at).toLocaleDateString()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* AI Tips */}
      <div className="bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 rounded-2xl border border-[var(--accent-primary)]/20 p-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
            <Sparkles className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
              💡 Consejo del Tutor IA
            </h3>
            <p className="text-[var(--text-secondary)]">
              Recuerda que el tutor IA está diseñado para guiarte, no para darte las respuestas directamente. 
              Intenta formular tus dudas de manera específica y explica tu razonamiento. 
              Así el tutor podrá ayudarte a desarrollar tu pensamiento crítico.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
