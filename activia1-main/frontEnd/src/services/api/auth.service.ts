/**
 * Auth Service - Authentication & Authorization
 *
 * Refactored to use BaseApiService for consistent API response handling.
 * Note: Auth endpoints have special response structures that need custom handling.
 */
import { BaseApiService } from './base.service';
import { post, get } from './client';

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string | null;
  student_id?: string | null;
  roles: string[];
  created_at: string;
  is_active: boolean;
  is_verified?: boolean;
}

/**
 * LoginRequest - Uses email field to match backend expectation
 * Backend expects: { email: string, password: string }
 */
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role?: string;
}

/**
 * RegisterResponse - Full response from register endpoint
 * Includes user and optionally tokens for auto-login
 */
export interface RegisterResponse {
  user: User;
  tokens?: {
    access_token: string;
    refresh_token?: string;
    token_type: string;
  };
}

/**
 * Backend response structure for login/register
 */
interface AuthApiResponse {
  user: User;
  tokens: {
    access_token: string;
    refresh_token?: string;
    token_type: string;
  };
}

/**
 * AuthService - Uses BaseApiService for consistent response handling
 *
 * Special handling for auth endpoints that return nested { user, tokens } structure.
 */
class AuthService extends BaseApiService {
  constructor() {
    super('/auth');
  }

  /**
   * Login
   * Backend route: POST /api/v1/auth/login
   * Backend expects JSON with email and password (not FormData)
   * Response: APIResponse[UserWithTokenResponse] = { success, data: { user, tokens } }
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    // Use post helper which extracts response.data.data automatically
    const apiResponse = await post<AuthApiResponse>('/auth/login', {
      email: credentials.email,
      password: credentials.password,
    });

    const result: LoginResponse = {
      access_token: apiResponse.tokens?.access_token || '',
      refresh_token: apiResponse.tokens?.refresh_token,
      token_type: apiResponse.tokens?.token_type || 'bearer',
      user: apiResponse.user,
    };

    // Store tokens
    if (result.access_token) {
      localStorage.setItem('access_token', result.access_token);
    }
    if (result.refresh_token) {
      localStorage.setItem('refresh_token', result.refresh_token);
    }
    if (result.user) {
      localStorage.setItem('user', JSON.stringify(result.user));
    }

    return result;
  }

  /**
   * Register
   * Backend route: POST /api/v1/auth/register
   * Response: APIResponse[UserWithTokenResponse] = { success, data: { user, tokens } }
   *
   * @param data - Registration data
   * @param autoLogin - If true, stores tokens for automatic login (default: false)
   * @returns RegisterResponse with user and optionally tokens
   */
  async register(data: RegisterRequest, autoLogin: boolean = false): Promise<RegisterResponse> {
    const apiResponse = await post<AuthApiResponse>('/auth/register', data);

    const result: RegisterResponse = {
      user: apiResponse.user,
      tokens: apiResponse.tokens ? {
        access_token: apiResponse.tokens.access_token,
        refresh_token: apiResponse.tokens.refresh_token,
        token_type: apiResponse.tokens.token_type || 'bearer',
      } : undefined,
    };

    // Optionally store tokens for auto-login after registration
    if (autoLogin && result.tokens) {
      if (result.tokens.access_token) {
        localStorage.setItem('access_token', result.tokens.access_token);
      }
      if (result.tokens.refresh_token) {
        localStorage.setItem('refresh_token', result.tokens.refresh_token);
      }
      if (result.user) {
        localStorage.setItem('user', JSON.stringify(result.user));
      }
    }

    return result;
  }

  /**
   * Logout
   */
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  /**
   * Get current user from localStorage
   */
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  /**
   * Check if authenticated
   */
  isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }

  /**
   * Get access token
   */
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * Get user profile from backend
   * Backend route: GET /api/v1/auth/me
   */
  async getProfile(): Promise<User> {
    return get<User>('/auth/me');
  }

  /**
   * Get refresh token from localStorage
   */
  getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  /**
   * Refresh token
   * Backend route: POST /api/v1/auth/refresh
   * Backend expects { refresh_token: string } in request body
   */
  async refreshToken(): Promise<{ access_token: string }> {
    const refreshToken = this.getRefreshToken();

    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    interface TokenResponse {
      access_token: string;
      refresh_token?: string;
      token_type: string;
    }

    const apiResponse = await post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });

    const newAccessToken = apiResponse.access_token || '';
    const newRefreshToken = apiResponse.refresh_token;

    if (newAccessToken) {
      localStorage.setItem('access_token', newAccessToken);
    }
    if (newRefreshToken) {
      localStorage.setItem('refresh_token', newRefreshToken);
    }

    return { access_token: newAccessToken };
  }
}

export const authService = new AuthService();
