/**
 * Context global de la aplicación con estado optimizado
 */
import React, { createContext, useContext, useReducer, useMemo, useEffect } from 'react';

interface User {
  id: string;
  username: string;
  email: string;
  role: 'student' | 'teacher' | 'admin';
}

interface Session {
  id: string;
  mode: string;
  student_id: string;
  is_active: boolean;
}

interface AppState {
  user: User | null;
  currentSession: Session | null;
  theme: 'light' | 'dark';
  sidebarCollapsed: boolean;
}

type AppAction =
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_SESSION'; payload: Session | null }
  | { type: 'TOGGLE_THEME' }
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'RESET_STATE' };

const initialState: AppState = {
  user: null,
  currentSession: null,
  theme: 'light',
  sidebarCollapsed: false
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    
    case 'SET_SESSION':
      return { ...state, currentSession: action.payload };
    
    case 'TOGGLE_THEME':
      return { ...state, theme: state.theme === 'light' ? 'dark' : 'light' };
    
    case 'TOGGLE_SIDEBAR':
      return { ...state, sidebarCollapsed: !state.sidebarCollapsed };
    
    case 'RESET_STATE':
      return initialState;
    
    default:
      return state;
  }
}

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  actions: {
    setUser: (user: User | null) => void;
    setSession: (session: Session | null) => void;
    toggleTheme: () => void;
    toggleSidebar: () => void;
    logout: () => void;
  };
}

const AppContext = createContext<AppContextType | null>(null);

// eslint-disable-next-line react-refresh/only-export-components
export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState, (initial) => {
    // Cargar estado desde localStorage
    if (typeof window === 'undefined') return initial;

    try {
      const savedTheme = localStorage.getItem('theme');
      const savedSidebarState = localStorage.getItem('sidebarCollapsed');

      return {
        ...initial,
        theme: (savedTheme as 'light' | 'dark') || initial.theme,
        sidebarCollapsed: savedSidebarState === 'true'
      };
    } catch (error) {
      console.warn('Failed to load state from localStorage:', error);
      return initial;
    }
  });

  // Persistir cambios en localStorage
  useEffect(() => {
    if (typeof window === 'undefined') return;

    try {
      localStorage.setItem('theme', state.theme);
      localStorage.setItem('sidebarCollapsed', String(state.sidebarCollapsed));
    } catch (error) {
      console.warn('Failed to save state to localStorage:', error);
    }
  }, [state.theme, state.sidebarCollapsed]);

  // Aplicar tema al documento
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', state.theme);
  }, [state.theme]);

  // Memoized actions
  const actions = useMemo(() => ({
    setUser: (user: User | null) => {
      dispatch({ type: 'SET_USER', payload: user });
    },

    setSession: (session: Session | null) => {
      dispatch({ type: 'SET_SESSION', payload: session });
    },

    toggleTheme: () => {
      dispatch({ type: 'TOGGLE_THEME' });
    },

    toggleSidebar: () => {
      dispatch({ type: 'TOGGLE_SIDEBAR' });
    },

    logout: () => {
      // Clear localStorage
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
      dispatch({ type: 'RESET_STATE' });
    }
  }), []);

  const value = useMemo(
    () => ({ state, dispatch, actions }),
    [state, actions]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};
