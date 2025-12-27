/**
 * Tipos para el sistema de Entrenador Digital
 */

export interface EjercicioInfo {
  id: string;
  titulo: string;
  dificultad: string;
  tiempo_estimado_min: number;
  puntos: number;
}

export interface LeccionInfo {
  id: string;
  nombre: string;
  descripcion: string;
  unit_number: number;
  ejercicios: EjercicioInfo[];
  total_puntos: number;
  dificultad: string;
}

export interface LenguajeInfo {
  language: string;
  nombre_completo: string;
  lecciones: LeccionInfo[];
}

export interface IniciarEntrenamientoRequest {
  language: string;
  unit_number: number;
}
