/**
 * Training Service - Entrenador Digital
 * 
 * Maneja:
 * - Obtención de materias y temas disponibles
 * - Inicio de sesiones de entrenamiento
 * - Solicitud de pistas
 * - Envío de código para evaluación
 * - Estado de sesiones activas
 */

import apiClient from './client';

// ============================================================================
// TIPOS / INTERFACES
// ============================================================================

export interface TemaInfo {
  id: string;
  nombre: string;
  descripcion: string;
  dificultad: string;
  tiempo_estimado_min: number;
}

export interface MateriaInfo {
  materia: string;
  codigo: string;
  temas: TemaInfo[];
}

export interface IniciarEntrenamientoRequest {
  materia_codigo: string;
  tema_id: string;
}

export interface EjercicioActual {
  numero: number;
  consigna: string;
  codigo_inicial: string;
}

export interface SesionEntrenamiento {
  session_id: string;
  materia: string;
  tema: string;
  ejercicio_actual: EjercicioActual;
  total_ejercicios: number;
  ejercicios_completados: number;
  tiempo_limite_min: number;
  inicio: string;
  fin_estimado: string;
}

export interface SolicitarPistaRequest {
  session_id: string;
  numero_pista: number;
}

export interface PistaResponse {
  contenido: string;
  numero: number;
  total_pistas: number;
}

export interface SolicitarPistaRequest {
  session_id: string;
  numero_pista: number;
}

export interface CorreccionIARequest {
  session_id: string;
  codigo_usuario: string;
}

export interface CorreccionIAResponse {
  analisis: string;
  sugerencias: string[];
  codigo_corregido?: string;
}

export interface SubmitEjercicioRequest {
  session_id: string;
  codigo_usuario: string;
}

export interface ResultadoEjercicio {
  numero: number;
  correcto: boolean;
  tests_pasados: number;
  tests_totales: number;
  mensaje: string;
}

export interface ResultadoFinal {
  session_id: string;
  nota_final: number;
  ejercicios_correctos: number;
  total_ejercicios: number;
  porcentaje: number;
  aprobado: boolean;
  tiempo_usado_min: number;
  resultados_detalle: ResultadoEjercicio[];
}

export interface SubmitEjercicioResponse {
  resultado: ResultadoEjercicio;
  hay_siguiente: boolean;
  siguiente_ejercicio?: EjercicioActual;
  resultado_final?: ResultadoFinal;
}

export interface EstadoSesion {
  session_id: string;
  finalizado: boolean;
  tiempo_transcurrido_min: number;
  tiempo_restante_min: number;
  pistas_usadas: number;
  penalizacion_actual: number;
  pistas_disponibles: number;
}

// ============================================================================
// SERVICIO
// ============================================================================

export const trainingService = {
  /**
   * Obtiene las materias disponibles con sus temas
   */
  async getMaterias(): Promise<MateriaInfo[]> {
    const response = await apiClient.get<MateriaInfo[]>('/training/materias');
    return response.data;
  },

  /**
   * Inicia una nueva sesión de entrenamiento
   */
  async iniciarEntrenamiento(request: IniciarEntrenamientoRequest): Promise<SesionEntrenamiento> {
    const response = await apiClient.post<SesionEntrenamiento>('/training/iniciar', request);
    return response.data;
  },

  /**
   * Envía el código de un ejercicio para evaluación
   * Retorna el resultado y el siguiente ejercicio si hay más
   */
  async submitEjercicio(request: SubmitEjercicioRequest): Promise<SubmitEjercicioResponse> {
    const response = await apiClient.post<SubmitEjercicioResponse>('/training/submit-ejercicio', request);
    return response.data;
  },

  /**
   * Solicita una pista para el ejercicio actual
   */
  async solicitarPista(request: SolicitarPistaRequest): Promise<PistaResponse> {
    const response = await apiClient.post<PistaResponse>('/training/pista', request);
    return response.data;
  },

  /**
   * Solicita corrección con IA para el código actual
   */
  async corregirConIA(request: CorreccionIARequest): Promise<CorreccionIAResponse> {
    const response = await apiClient.post<CorreccionIAResponse>('/training/corregir-ia', request);
    return response.data;
  },
};
