import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';
// MIGRATED: Using new authService instead of legacy api
import { authService, User as AuthUser } from '../services/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Helper to convert AuthUser to User type
const toUser = (authUser: AuthUser): User => ({
  id: authUser.id,
  username: authUser.username,
  email: authUser.email,
  full_name: authUser.full_name || undefined,
  roles: authUser.roles,
  is_active: authUser.is_active,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      const token = authService.getAccessToken();
      if (token) {
        try {
          // First try to get from localStorage (faster)
          const cachedUser = authService.getCurrentUser();
          if (cachedUser) {
            setUser(toUser(cachedUser));
          } else {
            // Fallback to fetching from backend
            const userData = await authService.getProfile();
            setUser(toUser(userData));
          }
        } catch (error) {
          authService.logout();
        }
      }
      setIsLoading(false);
    };
    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    // authService expects email, but we receive username from form
    // The backend login endpoint accepts email field
    const response = await authService.login({ email: username, password });
    if (response.user) {
      setUser(toUser(response.user));
    }
  };

  const register = async (username: string, email: string, password: string, fullName?: string) => {
  const payload: any = {
    username,
    email,
    password,
  };
  
  // Solo agregar full_name si NO está vacío
  if (fullName && fullName.trim() !== '') {
    payload.full_name = fullName.trim();
  }
  
  await authService.register(payload);
};

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login,
      register,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
