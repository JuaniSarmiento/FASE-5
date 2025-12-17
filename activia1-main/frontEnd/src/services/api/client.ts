/**
 * Cliente HTTP configurado con Axios
 * Incluye interceptores para manejo de errores y logging
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import type { APIResponse, APIError } from '@/types/api.types';

// Development-only logging helpers
const isDev = import.meta.env.DEV;
const devLog = (message: string, ...args: unknown[]) => { if (isDev) console.log(message, ...args); };
const devError = (message: string, ...args: unknown[]) => { if (isDev) console.error(message, ...args); };

// En desarrollo usa el proxy de Vite (/api), en producción usa variable de entorno
// IMPORTANTE: En producción, VITE_API_BASE_URL debe estar configurada
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (isDev ? '/api/v1' : '/api/v1');

// Crear instancia de axios
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 180000, // 180 segundos (3 minutos) - Aumentado para manejar tiempos de respuesta largos de Ollama en CPU
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==================== REQUEST INTERCEPTOR ====================

apiClient.interceptors.request.use(
  (config) => {
    // Log de request (solo en desarrollo)
    devLog(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, config.data);

    // Agregar token de autenticación si existe
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    devError('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// ==================== RESPONSE INTERCEPTOR ====================

apiClient.interceptors.response.use(
  (response: AxiosResponse<APIResponse<unknown>>) => {
    // Log de response (solo en desarrollo)
    devLog(`[API Response] ${response.config.url}`, response.data);

    return response;
  },
  (error: AxiosError<APIError>) => {
    // Log de error (solo en desarrollo)
    devError('[API Response Error]', error.response?.data || error.message);

    // Manejo de errores específicos
    if (error.response) {
      // El servidor respondió con un código de error
      const { status, data } = error.response;

      switch (status) {
        case 400:
          devError('[Validation Error]', data.error?.message);
          break;
        case 401:
          devError('[Unauthorized]', data.error?.message);
          // Redirigir a login si fuera necesario
          // window.location.href = '/login';
          break;
        case 403:
          devError('[Forbidden - Governance Block]', data.error?.message);
          break;
        case 404:
          devError('[Not Found]', data.error?.message);
          break;
        case 500:
          devError('[Server Error]', data.error?.message);
          break;
        case 503:
          devError('[Service Unavailable]', data.error?.message);
          break;
        default:
          devError('[Unknown Error]', data.error?.message);
      }

      return Promise.reject(data);
    } else if (error.request) {
      // La request fue hecha pero no hubo respuesta
      devError('[Network Error] No response received from server');
      return Promise.reject({
        success: false,
        error: {
          error_code: 'NETWORK_ERROR',
          message: 'No se pudo conectar con el servidor. Verifica tu conexión.',
          field: null,
        },
      } as APIError);
    } else {
      // Error al configurar la request
      devError('[Request Setup Error]', error.message);
      return Promise.reject({
        success: false,
        error: {
          error_code: 'REQUEST_ERROR',
          message: error.message,
          field: null,
        },
      } as APIError);
    }
  }
);

// ==================== UTILITY FUNCTIONS ====================

/**
 * Wrapper para hacer requests GET
 */
export async function get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.get<APIResponse<T>>(url, config);
  return response.data.data;
}

/**
 * Wrapper para hacer requests POST
 */
export async function post<T, D = unknown>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.post<APIResponse<T>>(url, data, config);
  return response.data.data;
}

/**
 * Wrapper para hacer requests PUT
 */
export async function put<T, D = unknown>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.put<APIResponse<T>>(url, data, config);
  return response.data.data;
}

/**
 * Wrapper para hacer requests PATCH
 */
export async function patch<T, D = unknown>(
  url: string,
  data?: D,
  config?: AxiosRequestConfig
): Promise<T> {
  const response = await apiClient.patch<APIResponse<T>>(url, data, config);
  return response.data.data;
}

/**
 * Wrapper para hacer requests DELETE
 */
export async function del<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const response = await apiClient.delete<APIResponse<T>>(url, config);
  return response.data.data;
}

export default apiClient;