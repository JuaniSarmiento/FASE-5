/**
 * Layout principal de la aplicación
 */
import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import { useApp } from '@/core/context/AppContext';
import { ROUTES } from '@/core/config/routes.config';
import { wsService } from '@/core/websocket/WebSocketService';
import './MainLayout.css';

export const MainLayout: React.FC = () => {
  const { state, actions } = useApp();
  const [wsStatus, setWsStatus] = React.useState(wsService.getState());

  React.useEffect(() => {
    const unsubscribe = wsService.onEvent('connect', () => {
      setWsStatus(wsService.getState());
    });

    const unsubscribe2 = wsService.onEvent('disconnect', () => {
      setWsStatus(wsService.getState());
    });

    return () => {
      unsubscribe();
      unsubscribe2();
    };
  }, []);

  return (
    <div className={`main-layout ${state.theme}`}>
      {/* Sidebar */}
      <aside className={`sidebar ${state.sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <h1 className="logo">🎓 AI-Native</h1>
          <button
            className="collapse-btn"
            onClick={actions.toggleSidebar}
            aria-label="Toggle sidebar"
          >
            {state.sidebarCollapsed ? '→' : '←'}
          </button>
        </div>

        <nav className="sidebar-nav">
          <NavLink to={ROUTES.DASHBOARD} className="nav-item">
            <span className="nav-icon">📊</span>
            <span className="nav-label">Dashboard</span>
          </NavLink>

          <div className="nav-section">
            <div className="nav-section-title">Agentes IA</div>
            
            <NavLink to={ROUTES.AGENTS.TUTOR} className="nav-item">
              <span className="nav-icon">🎓</span>
              <span className="nav-label">Tutor Cognitivo</span>
            </NavLink>

            <NavLink to={ROUTES.AGENTS.EVALUATOR} className="nav-item">
              <span className="nav-icon">📈</span>
              <span className="nav-label">Evaluador</span>
            </NavLink>

            <NavLink to={ROUTES.AGENTS.SIMULATOR} className="nav-item">
              <span className="nav-icon">🎭</span>
              <span className="nav-label">Simuladores</span>
            </NavLink>

            <NavLink to={ROUTES.AGENTS.RISK_ANALYST} className="nav-item">
              <span className="nav-icon">⚠️</span>
              <span className="nav-label">Análisis de Riesgos</span>
            </NavLink>

            <NavLink to={ROUTES.AGENTS.TRACEABILITY} className="nav-item">
              <span className="nav-icon">🔍</span>
              <span className="nav-label">Trazabilidad N4</span>
            </NavLink>

            <NavLink to={ROUTES.AGENTS.GIT_ANALYTICS} className="nav-item">
              <span className="nav-icon">📊</span>
              <span className="nav-label">Git Analytics</span>
            </NavLink>
          </div>

          <div className="nav-section">
            <div className="nav-section-title">Herramientas</div>
            
            <NavLink to={ROUTES.TEACHER} className="nav-item">
              <span className="nav-icon">👨‍🏫</span>
              <span className="nav-label">Panel Docente</span>
            </NavLink>

            <NavLink to={ROUTES.PLAYGROUND} className="nav-item">
              <span className="nav-icon">🧪</span>
              <span className="nav-label">Playground</span>
            </NavLink>
          </div>
        </nav>

        <div className="sidebar-footer">
          <div className={`ws-status ${wsStatus === 'OPEN' ? 'connected' : 'disconnected'}`}>
            <span className="status-dot"></span>
            <span className="status-text">
              {wsStatus === 'OPEN' ? 'Conectado' : 'Desconectado'}
            </span>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="main-content">
        {/* Top Bar */}
        <header className="top-bar">
          <div className="top-bar-left">
            {state.currentSession && (
              <div className="session-indicator">
                <span className="session-badge">
                  Sesión activa: {state.currentSession.id.slice(0, 8)}
                </span>
              </div>
            )}
          </div>

          <div className="top-bar-right">
            <button
              className="theme-toggle"
              onClick={actions.toggleTheme}
              aria-label="Toggle theme"
            >
              {state.theme === 'light' ? '🌙' : '☀️'}
            </button>

            {state.user && (
              <div className="user-menu">
                <span className="user-name">{state.user.username}</span>
                <button onClick={actions.logout} className="logout-btn">
                  Salir
                </button>
              </div>
            )}
          </div>
        </header>

        {/* Page Content */}
        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
