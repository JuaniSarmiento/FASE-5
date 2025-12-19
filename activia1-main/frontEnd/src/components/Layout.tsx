import React, { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Home,
  MessageSquare,
  Code,
  Users,
  BarChart3,
  Settings,
  LogOut,
  Menu,
  X,
  Sparkles,
  ChevronDown,
  Bell,
  Search
} from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: Home },
  { path: '/tutor', label: 'Tutor IA', icon: MessageSquare },
  { path: '/exercises', label: 'Entrenador Digital', icon: Code },
  { path: '/simulators', label: 'Simuladores', icon: Users },
  { path: '/analytics', label: 'Analíticas', icon: BarChart3 },
];

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-[var(--bg-primary)] flex">
      {/* Sidebar */}
      <aside 
        className={`fixed lg:static inset-y-0 left-0 z-50 flex flex-col transition-all duration-300 ${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-[var(--bg-secondary)] border-r border-[var(--border-color)]`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-[var(--border-color)]">
          {sidebarOpen && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-lg gradient-text">AI Native</span>
            </div>
          )}
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-[var(--bg-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-500/20 to-purple-500/20 text-[var(--accent-primary)] border border-[var(--accent-primary)]/30'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-primary)]'
                }`
              }
            >
              <item.icon className={`w-5 h-5 ${sidebarOpen ? '' : 'mx-auto'}`} />
              {sidebarOpen && <span className="font-medium">{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* User Section */}
        <div className="p-3 border-t border-[var(--border-color)]">
          <div 
            className={`flex items-center gap-3 p-3 rounded-xl bg-[var(--bg-tertiary)] ${
              sidebarOpen ? '' : 'justify-center'
            }`}
          >
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-semibold">
              {user?.username?.[0]?.toUpperCase() || 'U'}
            </div>
            {sidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="font-medium text-[var(--text-primary)] truncate">
                  {user?.full_name || user?.username}
                </p>
                <p className="text-xs text-[var(--text-muted)] truncate">
                  {user?.roles?.[0] || 'Estudiante'}
                </p>
              </div>
            )}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Header */}
        <header className="h-16 border-b border-[var(--border-color)] bg-[var(--bg-secondary)]/80 backdrop-blur-sm flex items-center justify-between px-6 sticky top-0 z-40">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)]" />
              <input
                type="text"
                placeholder="Buscar..."
                className="w-64 pl-10 pr-4 py-2 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-sm text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-[var(--accent-primary)] focus:outline-none transition-colors"
              />
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Notifications */}
            <button className="relative p-2 rounded-lg hover:bg-[var(--bg-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-[var(--error)] rounded-full"></span>
            </button>

            {/* Settings */}
            <button className="p-2 rounded-lg hover:bg-[var(--bg-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
              <Settings className="w-5 h-5" />
            </button>

            {/* User Menu */}
            <div className="relative">
              <button 
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center gap-2 p-2 rounded-lg hover:bg-[var(--bg-hover)] transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-sm font-semibold">
                  {user?.username?.[0]?.toUpperCase() || 'U'}
                </div>
                <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" />
              </button>

              {userMenuOpen && (
                <div className="absolute right-0 top-full mt-2 w-48 py-2 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl shadow-lg animate-scaleIn origin-top-right">
                  <div className="px-4 py-2 border-b border-[var(--border-color)]">
                    <p className="font-medium text-[var(--text-primary)]">{user?.username}</p>
                    <p className="text-xs text-[var(--text-muted)]">{user?.email}</p>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center gap-2 px-4 py-2 text-left text-[var(--error)] hover:bg-[var(--bg-hover)] transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>Cerrar Sesión</span>
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet />
        </main>
      </div>

      {/* Click outside to close user menu */}
      {userMenuOpen && (
        <div 
          className="fixed inset-0 z-30" 
          onClick={() => setUserMenuOpen(false)}
        />
      )}
    </div>
  );
}
