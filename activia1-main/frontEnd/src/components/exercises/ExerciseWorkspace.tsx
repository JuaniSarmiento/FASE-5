/**
 * ExerciseWorkspace Component
 * Workspace completo para resolver ejercicios con editor de código y evaluación
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { 
  ArrowLeft, 
  Play, 
  BookOpen, 
  Lightbulb,
  Code,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { exercisesService } from '@/services/api/exercises.service';
import { IExercise, IEvaluationResult } from '@/types';
import { CodeEditor } from './CodeEditor';
import { EvaluationResultView } from './EvaluationResultView';

export const ExerciseWorkspace: React.FC = () => {
  const { exerciseId } = useParams<{ exerciseId: string }>();
  const navigate = useNavigate();

  const [exercise, setExercise] = useState<IExercise | null>(null);
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluation, setEvaluation] = useState<IEvaluationResult | null>(null);

  // UI State
  const [showHints, setShowHints] = useState(false);
  const [showStory, setShowStory] = useState(true);

  useEffect(() => {
    if (exerciseId) {
      loadExercise();
    }
  }, [exerciseId]);

  const loadExercise = async () => {
    if (!exerciseId) return;

    try {
      setLoading(true);
      const data = await exercisesService.getJSONById(exerciseId);
      setExercise(data);
      // Iniciar con código vacío en lugar del starter_code
      setCode('');
      setError(null);
    } catch (err) {
      setError('Error al cargar el ejercicio');
      console.error('Error loading exercise:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!exerciseId || !code.trim()) return;

    try {
      setSubmitting(true);
      setError(null);
      
      const result = await exercisesService.submitJSON(exerciseId, code);
      setEvaluation(result);
      
      // Scroll al resultado
      setTimeout(() => {
        document.getElementById('evaluation-result')?.scrollIntoView({ 
          behavior: 'smooth' 
        });
      }, 100);
    } catch (err: any) {
      setError(err.message || 'Error al evaluar el código');
      console.error('Error submitting code:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleRetry = () => {
    setEvaluation(null);
    // Limpiar el código para reiniciar
    setCode('');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error && !exercise) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          {error}
        </div>
        <button
          onClick={() => navigate('/exercises')}
          className="mt-4 text-blue-600 hover:text-blue-800 flex items-center gap-2"
        >
          <ArrowLeft size={20} />
          Volver al Entrenador
        </button>
      </div>
    );
  }

  if (!exercise) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dient-to-br from-indigo-50 via-purple-50 to-pink-50">
      {/* Header */}
      {/* Header con gradiente */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/exercises')}
                className="text-white hover:bg-white/20 p-2 rounded-lg transition-all"
              >
                <ArrowLeft size={24} />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-white">{exercise.meta.title}</h1>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-indigo-100 text-sm font-mono">{exercise.id}</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                    exercise.meta.difficulty === 'Easy' ? 'bg-green-400 text-green-900' :
                    exercise.meta.difficulty === 'Medium' ? 'bg-yellow-400 text-yellow-900' :
                    'bg-red-400 text-red-900'
                  }`}>
                    {exercise.meta.difficulty === 'Easy' ? '⭐ Fácil' :
                     exercise.meta.difficulty === 'Medium' ? '⭐⭐ Medio' : '⭐⭐⭐ Difícil'}
                  </span>
                  <span className="text-white/90 text-sm bg-white/20 px-3 py-1 rounded-full">
                    ⏱️ {exercise.meta.estimated_time_min || exercise.meta.estimated_time_minutes || 0} min
                  </span>
                  <span className="text-white/90 text-sm bg-white/20 px-3 py-1 rounded-full">
                    🏆 {exercise.meta.points || 0} XP
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={handleSubmit}
              disabled={submitting || !code.trim()}
              className="flex items-center gap-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 disabled:from-gray-400 disabled:to-gray-500 text-white font-bold px-8 py-4 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
            >
              <Play size={24} />
              {submitting ? '⏳ Evaluando...' : '✨ Evaluar Código'}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Panel izquierdo: Instrucciones */}
          <div className="space-y-4">
            {/* Historia */}
            <div className="bg-white rounded-xl shadow-lg border border-indigo-100 overflow-hidden">
              <button
                onClick={() => setShowStory(!showStory)}
                className="w-full flex items-center justify-between p-5 hover:bg-gradient-to-r hover:from-indigo-50 hover:to-purple-50 transition-all"
              >
                <div className="flex items-center gap-3">
                  <div className="bg-gradient-to-br from-indigo-500 to-purple-600 p-2 rounded-lg">
                    <BookOpen className="text-white" size={20} />
                  </div>
                  <h2 className="font-bold text-xl text-gray-800">📖 Historia</h2>
                </div>
                {showStory ? <ChevronUp size={24} className="text-gray-500" /> : <ChevronDown size={24} className="text-gray-500" />}
              </button>
              {showStory && (
                <div className="p-6 border-t border-indigo-100 bg-gradient-to-br from-indigo-50/50 to-purple-50/50 prose prose-gray max-w-none text-gray-900">
                  <ReactMarkdown>{exercise.content.story_markdown}</ReactMarkdown>
                </div>
              )}
            </div>

            {/* Misión */}
            <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl shadow-xl p-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-white/20 p-2 rounded-lg">
                  <Code className="text-white" size={24} />
                </div>
                <h2 className="font-bold text-2xl">🎯 Tu Misión</h2>
              </div>
              <div className="prose prose-invert max-w-none">
                <ReactMarkdown>{exercise.content.mission_markdown}</ReactMarkdown>
              </div>
            </div>

            {/* Criterios de éxito */}
            {(exercise.content.success_criteria?.length || exercise.content.constraints?.length) ? (
              <div className="bg-white rounded-xl shadow-lg border-2 border-green-200 p-5">
                <h3 className="font-bold text-xl mb-4 text-gray-800 flex items-center gap-2">
                  <span className="text-2xl">✅</span> Criterios de Éxito
                </h3>
                <ul className="space-y-3">
                  {(exercise.content.success_criteria || exercise.content.constraints || []).map((criterion: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-3 bg-green-50 p-3 rounded-lg">
                      <span className="text-green-600 text-xl mt-0.5 flex-shrink-0">✓</span>
                      <span className="text-gray-700">{criterion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {/* Hints */}
            {exercise.content.hints && exercise.content.hints.length > 0 && (
              <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl shadow-lg border-2 border-yellow-300 overflow-hidden">
                <button
                  onClick={() => setShowHints(!showHints)}
                  className="w-full flex items-center justify-between p-5 hover:bg-yellow-100/50 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <div className="bg-gradient-to-br from-yellow-400 to-orange-500 p-2 rounded-lg">
                      <Lightbulb className="text-white" size={20} />
                    </div>
                    <h2 className="font-bold text-xl text-gray-800">💡 Pistas ({exercise.content.hints.length})</h2>
                  </div>
                  {showHints ? <ChevronUp size={24} className="text-gray-500" /> : <ChevronDown size={24} className="text-gray-500" />}
                </button>
                {showHints && (
                  <div className="p-5 border-t border-yellow-300 space-y-3">
                    {exercise.content.hints.map((hint: string, idx: number) => (
                      <div key={idx} className="bg-white rounded-lg p-4 shadow border border-yellow-200">
                        <span className="font-bold text-yellow-700 text-sm">💡 Pista {idx + 1}:</span>{' '}
                        <span className="text-gray-700">{hint}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Objetivos de aprendizaje */}
            {exercise.meta.learning_objectives && exercise.meta.learning_objectives.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg border border-purple-200 p-5">
                <h3 className="font-bold text-xl mb-4 text-gray-800 flex items-center gap-2">
                  <span className="text-2xl">🎓</span> Aprenderás
                </h3>
                <div className="flex flex-wrap gap-2">
                  {exercise.meta.learning_objectives.map((objective: string, idx: number) => (
                    <span
                      key={idx}
                      className="px-4 py-2 bg-gradient-to-r from-purple-100 to-pink-100 text-purple-700 font-semibold text-sm rounded-full border border-purple-200"
                    >
                      {objective}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Panel derecho: Editor */}
          <div className="space-y-4">
            <CodeEditor
              value={code}
              onChange={setCode}
              language={exercise.ui_config.editor_language}
              theme={exercise.ui_config.editor_theme}
              showLineNumbers={exercise.ui_config.show_line_numbers}
            />

            {/* Error message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Resultado de evaluación */}
        {evaluation && (
          <div id="evaluation-result" className="mt-8">
            <EvaluationResultView
              result={evaluation}
              studentCode={code}
              onRetry={handleRetry}
            />
          </div>
        )}
      </div>
    </div>
  );
};
