/**
 * Ejemplo de uso del sistema de ejercicios
 * Este archivo demuestra cómo integrar los tipos IExercise en componentes React
 */

import React, { useState, useEffect } from 'react';
import { IExercise, IExerciseSubmission, ExerciseDifficulty } from '@/types';
import { exercisesService } from '@/services/api';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import { Play, CheckCircle, XCircle, Clock, Award } from 'lucide-react';

/**
 * Card de ejercicio para listado
 */
export const ExerciseCard: React.FC<{ 
  exercise: IExercise;
  onSelect: (exercise: IExercise) => void;
}> = ({ exercise, onSelect }) => {
  
  const getDifficultyColor = (difficulty: ExerciseDifficulty): string => {
    const colors = {
      'Easy': 'bg-green-500/20 text-green-400 border-green-500',
      'Medium': 'bg-yellow-500/20 text-yellow-400 border-yellow-500',
      'Hard': 'bg-red-500/20 text-red-400 border-red-500',
    };
    return colors[difficulty];
  };

  return (
    <div 
      onClick={() => onSelect(exercise)}
      className="bg-gray-800/50 border-2 border-gray-700 rounded-xl p-4 hover:border-purple-500 cursor-pointer transition-all"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <h3 className="font-semibold text-white text-lg">
          {exercise.meta.title}
        </h3>
        <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getDifficultyColor(exercise.meta.difficulty)}`}>
          {exercise.meta.difficulty}
        </span>
      </div>

      {/* Tags */}
      <div className="flex gap-2 mb-3 flex-wrap">
        {exercise.meta.tags.map((tag, idx) => (
          <span 
            key={idx}
            className="px-2 py-1 bg-purple-600/20 text-purple-300 rounded text-xs"
          >
            {tag}
          </span>
        ))}
      </div>

      {/* Metadata */}
      <div className="flex items-center gap-4 text-gray-400 text-sm">
        <div className="flex items-center gap-1">
          <Clock size={14} />
          <span>{exercise.meta.estimated_time_min} min</span>
        </div>
        <div className="flex items-center gap-1">
          <Award size={14} />
          <span>{exercise.ui_config.editor_language}</span>
        </div>
      </div>
    </div>
  );
};

/**
 * Vista detallada del ejercicio con editor
 */
export const ExerciseDetailView: React.FC<{ 
  exercise: IExercise;
}> = ({ exercise }) => {
  const [code, setCode] = useState<string>(exercise.starter_code);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const submission: IExerciseSubmission = {
        exercise_id: exercise.id,
        code: code,
      };
      
      const response = await exercisesService.submit(submission);
      setResult(response);
    } catch (error) {
      console.error('Error submitting exercise:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-full">
      {/* Panel Izquierdo: Instrucciones */}
      <div className="space-y-6 overflow-y-auto max-h-[calc(100vh-200px)] pr-4">
        {/* Story */}
        <div className="bg-gray-800/50 rounded-xl p-6">
          <ReactMarkdown className="prose prose-invert max-w-none">
            {exercise.content.story_markdown}
          </ReactMarkdown>
        </div>

        {/* Mission */}
        <div className="bg-purple-900/20 rounded-xl p-6 border border-purple-500/30">
          <ReactMarkdown className="prose prose-invert max-w-none">
            {exercise.content.mission_markdown}
          </ReactMarkdown>
        </div>

        {/* Constraints */}
        <div className="bg-yellow-900/20 rounded-xl p-6 border border-yellow-500/30">
          <h4 className="text-yellow-400 font-semibold mb-3">⚠️ Restricciones</h4>
          <ul className="space-y-2">
            {exercise.content.constraints.map((constraint, idx) => (
              <li key={idx} className="text-gray-300 text-sm">
                • {constraint}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Panel Derecho: Editor */}
      <div className="space-y-4">
        {/* Editor */}
        <div className="bg-gray-900 rounded-xl overflow-hidden border border-gray-700">
          <div className="bg-gray-800 px-4 py-2 flex items-center justify-between">
            <span className="text-gray-400 text-sm font-mono">
              {exercise.ui_config.editor_language}
            </span>
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                  Ejecutando...
                </>
              ) : (
                <>
                  <Play size={16} />
                  Ejecutar
                </>
              )}
            </button>
          </div>
          
          <Editor
            height="500px"
            language={exercise.ui_config.editor_language}
            value={code}
            onChange={(value) => setCode(value || '')}
            theme="vs-dark"
            options={{
              fontSize: 14,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              wordWrap: 'on',
              tabSize: 4,
            }}
          />
        </div>

        {/* Resultado */}
        {result && (
          <div className={`rounded-xl p-6 border-2 ${
            result.success 
              ? 'bg-green-900/20 border-green-500' 
              : 'bg-red-900/20 border-red-500'
          }`}>
            <div className="flex items-center gap-3 mb-4">
              {result.success ? (
                <CheckCircle className="text-green-400" size={24} />
              ) : (
                <XCircle className="text-red-400" size={24} />
              )}
              <h4 className="font-semibold text-white">
                {result.success ? '✅ ¡Correcto!' : '❌ Intenta de nuevo'}
              </h4>
            </div>

            {/* Output */}
            {result.output && (
              <div className="bg-black/30 rounded p-4 mb-4">
                <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                  {result.output}
                </pre>
              </div>
            )}

            {/* Tests */}
            <div className="flex items-center gap-2 text-sm text-gray-300 mb-3">
              <span>Tests pasados: {result.passed_tests}/{result.total_tests}</span>
            </div>

            {/* AI Feedback */}
            {result.ai_feedback && (
              <div className="text-sm text-gray-300">
                <strong>Feedback:</strong> {result.ai_feedback}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Página completa de ejercicios con filtros
 */
export const ExercisesPage: React.FC = () => {
  const [exercises, setExercises] = useState<IExercise[]>([]);
  const [selectedExercise, setSelectedExercise] = useState<IExercise | null>(null);
  const [loading, setLoading] = useState(true);
  const [difficultyFilter, setDifficultyFilter] = useState<ExerciseDifficulty | null>(null);

  useEffect(() => {
    loadExercises();
  }, []);

  const loadExercises = async () => {
    try {
      setLoading(true);
      // Cargar todos los ejercicios desde los archivos JSON
      const allExercises = await exercisesService.list();
      setExercises(allExercises);
    } catch (error) {
      console.error('Error loading exercises:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredExercises = difficultyFilter
    ? exercises.filter(ex => ex.meta.difficulty === difficultyFilter)
    : exercises;

  if (selectedExercise) {
    return (
      <div className="p-6">
        <button
          onClick={() => setSelectedExercise(null)}
          className="mb-6 text-purple-400 hover:text-purple-300 flex items-center gap-2"
        >
          ← Volver a la lista
        </button>
        <ExerciseDetailView exercise={selectedExercise} />
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-white mb-6">
        📚 Ejercicios de Programación
      </h1>

      {/* Filtros */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={() => setDifficultyFilter(null)}
          className={`px-4 py-2 rounded-lg ${
            !difficultyFilter 
              ? 'bg-purple-600 text-white' 
              : 'bg-gray-800 text-gray-400'
          }`}
        >
          Todos
        </button>
        {(['Easy', 'Medium', 'Hard'] as ExerciseDifficulty[]).map(diff => (
          <button
            key={diff}
            onClick={() => setDifficultyFilter(diff)}
            className={`px-4 py-2 rounded-lg ${
              difficultyFilter === diff
                ? 'bg-purple-600 text-white'
                : 'bg-gray-800 text-gray-400'
            }`}
          >
            {diff}
          </button>
        ))}
      </div>

      {/* Lista de ejercicios */}
      {loading ? (
        <div className="text-center text-gray-400 py-12">Cargando ejercicios...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredExercises.map(exercise => (
            <ExerciseCard
              key={exercise.id}
              exercise={exercise}
              onSelect={setSelectedExercise}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default ExercisesPage;
