/**
 * ExercisesPage - Página principal de ejercicios
 * Router completo para el sistema de ejercicios con evaluación IA
 */
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ExercisesList } from '@/components/exercises/ExercisesList';
import { ExerciseWorkspace } from '@/components/exercises/ExerciseWorkspace';

/**
 * Página de Ejercicios
 * 
 * Rutas:
 * - /exercises -> Lista de ejercicios
 * - /exercises/:exerciseId -> Workspace del ejercicio
 * 
 * @example
 * // En tu App.tsx o main router:
 * import { ExercisesPage } from '@/pages/ExercisesPage';
 * 
 * <Routes>
 *   <Route path="/exercises/*" element={<ExercisesPage />} />
 * </Routes>
 */
export const ExercisesPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Lista de ejercicios */}
        <Route path="/" element={<ExercisesList />} />
        
        {/* Workspace de ejercicio específico */}
        <Route path="/:exerciseId" element={<ExerciseWorkspace />} />
        
        {/* Redirect para rutas inválidas */}
        <Route path="*" element={<Navigate to="/exercises" replace />} />
      </Routes>
    </div>
  );
};

export default ExercisesPage;
