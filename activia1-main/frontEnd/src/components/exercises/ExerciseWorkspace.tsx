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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => navigate('/exercises')}
                className="text-gray-600 hover:text-gray-800 hover:bg-gray-100 p-2 rounded-lg transition-all"
              >
                <ArrowLeft size={24} />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">{exercise.meta.title}</h1>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-gray-500 text-sm font-mono">{exercise.id}</span>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    exercise.meta.difficulty === 'Easy' ? 'bg-green-100 text-green-800' :
                    exercise.meta.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {exercise.meta.difficulty === 'Easy' ? 'Fácil' :
                     exercise.meta.difficulty === 'Medium' ? 'Medio' : 'Difícil'}
                  </span>
                  <span className="text-gray-600 text-sm flex items-center gap-1">
                    <Clock size={14} />
                    {exercise.meta.estimated_time_min || exercise.meta.estimated_time_minutes || 0} min
                  </span>
                  <span className="text-gray-600 text-sm flex items-center gap-1">
                    <Award size={14} />
                    {exercise.meta.points || 0} pts
                  </span>
                </div>
              </div>
            </div>
            <button
              onClick={handleSubmit}
              disabled={submitting || !code.trim()}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold px-6 py-3 rounded-lg shadow-md hover:shadow-lg transition-all disabled:cursor-not-allowed"
            >
              <Play size={20} />
              {submitting ? 'Evaluando...' : 'Evaluar Código'}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Panel izquierdo: Instrucciones */}
          <div className="space-y-4">
            {/* Historia */}
            <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
              <button
                onClick={() => setShowStory(!showStory)}
                className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-all"
              >
                <div className="flex items-center gap-3">
                  <BookOpen className="text-blue-600" size={20} />
                  <h2 className="font-bold text-lg text-gray-800">Historia</h2>
                </div>
                {showStory ? <ChevronUp size={20} className="text-gray-500" /> : <ChevronDown size={20} className="text-gray-500" />}
              </button>
              {showStory && (
                <div className="p-4 border-t border-gray-200 bg-gray-50 prose prose-gray max-w-none text-gray-800">
                  <ReactMarkdown>{exercise.content.story_markdown}</ReactMarkdown>
                </div>
              )}
            </div>

            {/* Misión */}
            <div className="bg-blue-50 rounded-lg shadow-md border border-blue-200 p-5">
              <div className="flex items-center gap-3 mb-4">
                <Code className="text-blue-600" size={24} />
                <h2 className="font-bold text-xl text-gray-800">Tu Misión</h2>
              </div>
              <div className="prose prose-blue max-w-none text-gray-700">
                <ReactMarkdown>{exercise.content.mission_markdown}</ReactMarkdown>
              </div>
            </div>

            {/* Criterios de éxito */}
            {(exercise.content.success_criteria?.length || exercise.content.constraints?.length) ? (
              <div className="bg-white rounded-lg shadow-md border border-green-200 p-5">
                <h3 className="font-bold text-lg mb-4 text-gray-800 flex items-center gap-2">
                  <CheckCircle className="text-green-600" size={20} />
                  Criterios de Éxito
                </h3>
                <ul className="space-y-2">
                  {(exercise.content.success_criteria || exercise.content.constraints || []).map((criterion: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2 bg-green-50 p-3 rounded-lg">
                      <span className="text-green-600 mt-0.5 flex-shrink-0">✓</span>
                      <span className="text-gray-700 text-sm">{criterion}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            {/* Hints */}
            {exercise.content.hints && exercise.content.hints.length > 0 && (
              <div className="bg-white rounded-lg shadow-md border border-yellow-200 overflow-hidden">
                <button
                  onClick={() => setShowHints(!showHints)}
                  className="w-full flex items-center justify-between p-4 hover:bg-yellow-50 transition-all"
                >
                  <div className="flex items-center gap-3">
                    <Lightbulb className="text-yellow-600" size={20} />
                    <h2 className="font-bold text-lg text-gray-800">Pistas ({exercise.content.hints.length})</h2>
                  </div>
                  {showHints ? <ChevronUp size={20} className="text-gray-500" /> : <ChevronDown size={20} className="text-gray-500" />}
                </button>
                {showHints && (
                  <div className="p-4 border-t border-yellow-200 bg-yellow-50 space-y-2">
                    {exercise.content.hints.map((hint: string, idx: number) => (
                      <div key={idx} className="bg-white rounded-lg p-3 border border-yellow-200">
                        <span className="font-semibold text-yellow-700 text-sm">Pista {idx + 1}:</span>{' '}
                        <span className="text-gray-700 text-sm">{hint}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Objetivos de aprendizaje */}
            {exercise.meta.learning_objectives && exercise.meta.learning_objectives.length > 0 && (
              <div className="bg-white rounded-lg shadow-md border border-gray-200 p-5">
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
