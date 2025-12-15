import React, { useState, useEffect } from 'react';
import { Play, CheckCircle, XCircle, Clock, Award, ChevronRight, Code, Terminal, Sparkles, BarChart3 } from 'lucide-react';
// FIX DEFECTO 10.1 Cortez14: Use exercisesService for exercise operations
import { exercisesService } from '../services/api';
import { Exercise, SubmissionResult } from '../types';
import Editor from '@monaco-editor/react';

const ExercisesPageNew: React.FC = () => {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null);
  const [code, setCode] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<SubmissionResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<number | null>(null);

  // FIX Cortez22 DEFECTO 4.1, 4.5, 4.9, 4.10: Added isMounted check, error state, loading state
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadExercises = async () => {
      try {
        setLoading(true);
        setError(null);
        // FIX DEFECTO 10.1 Cortez14: Use exercisesService.list
        const exercises = await exercisesService.list();
        if (isMounted) {
          setExercises(exercises || []);
        }
      } catch (err) {
        if (isMounted) {
          const errorMessage = err instanceof Error ? err.message : 'Error loading exercises';
          setError(errorMessage);
          console.error('Error loading exercises:', err);
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadExercises();

    return () => {
      isMounted = false;
    };
  }, []);

  const selectExercise = (exercise: Exercise) => {
    setSelectedExercise(exercise);
    setCode(exercise.starter_code || '# Escribe tu código aquí\n');
    setResult(null);
  };

  const handleSubmit = async () => {
    if (!selectedExercise) return;

    setIsSubmitting(true);
    try {
      // FIX DEFECTO 10.1 Cortez14: Use exercisesService.submit
      const result = await exercisesService.submit({
        exercise_id: selectedExercise.id,
        code: code,
      });
      setResult(result);
    } catch (error) {
      console.error('Error submitting exercise:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getDifficultyColor = (level: number) => {
    if (level <= 3) return 'text-green-400 bg-green-400/10';
    if (level <= 6) return 'text-yellow-400 bg-yellow-400/10';
    return 'text-red-400 bg-red-400/10';
  };

  const getDifficultyLabel = (level: number) => {
    if (level <= 3) return 'Fácil';
    if (level <= 6) return 'Intermedio';
    return 'Avanzado';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-3">Ejercicios de Programación</h1>
          <p className="text-gray-400">Resuelve ejercicios y obtén feedback de IA en tiempo real</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sidebar - Lista de Ejercicios */}
          <div className="lg:col-span-1">
            <div className="glass rounded-2xl p-6 sticky top-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <Code className="w-5 h-5 text-purple-400" />
                  Ejercicios
                </h2>
              </div>

              {/* Filter */}
              <div className="flex gap-2 mb-4">
                <button
                  onClick={() => setFilter(null)}
                  className={`px-3 py-1 rounded-lg text-sm transition-all ${
                    filter === null
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700'
                  }`}
                >
                  Todos
                </button>
                {[1, 2, 3].map((level) => (
                  <button
                    key={level}
                    onClick={() => setFilter(level * 3)}
                    className={`px-3 py-1 rounded-lg text-sm transition-all ${
                      filter === level * 3
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-700/50 text-gray-400 hover:bg-gray-700'
                    }`}
                  >
                    {getDifficultyLabel(level * 3)}
                  </button>
                ))}
              </div>

              {/* Exercise List */}
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {loading ? (
                  <div className="text-center py-8 text-gray-400">Cargando...</div>
                ) : exercises.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">No hay ejercicios disponibles</div>
                ) : (
                  exercises
                    .filter((ex) => filter === null || Math.abs(ex.difficulty_level - filter) <= 3)
                    .map((exercise) => (
                      <button
                        key={exercise.id}
                        onClick={() => selectExercise(exercise)}
                        className={`w-full text-left p-4 rounded-xl transition-all ${
                          selectedExercise?.id === exercise.id
                            ? 'bg-purple-600/20 border-2 border-purple-500'
                            : 'bg-gray-800/50 border-2 border-transparent hover:border-gray-700'
                        }`}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-semibold text-white text-sm">{exercise.title}</h3>
                          <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
                        </div>
                        <div className="flex items-center gap-2">
                          <span
                            className={`text-xs px-2 py-1 rounded-full ${getDifficultyColor(
                              exercise.difficulty_level
                            )}`}
                          >
                            {getDifficultyLabel(exercise.difficulty_level)}
                          </span>
                          <span className="text-xs text-gray-500 flex items-center gap-1">
                            <Award className="w-3 h-3" />
                            {exercise.max_score} pts
                          </span>
                        </div>
                      </button>
                    ))
                )}
              </div>
            </div>
          </div>

          {/* Main Content - Editor y Console */}
          <div className="lg:col-span-2 space-y-6">
            {selectedExercise ? (
              <>
                {/* Exercise Details */}
                <div className="glass rounded-2xl p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h2 className="text-2xl font-bold text-white mb-2">{selectedExercise.title}</h2>
                      <p className="text-gray-400">{selectedExercise.description}</p>
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <Clock className="w-4 h-4" />
                      <span className="text-sm">{selectedExercise.time_limit_seconds}s</span>
                    </div>
                  </div>

                  {selectedExercise.hints && selectedExercise.hints.length > 0 && (
                    <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mb-4">
                      <h3 className="text-blue-400 font-semibold mb-2 text-sm">💡 Pistas:</h3>
                      <ul className="text-sm text-gray-300 space-y-1">
                        {selectedExercise.hints.map((hint, index) => (
                          <li key={index}>• {hint}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Code Editor */}
                <div className="glass rounded-2xl overflow-hidden">
                  <div className="bg-gray-800/50 px-6 py-3 flex items-center justify-between border-b border-gray-700/50">
                    <div className="flex items-center gap-2">
                      <Terminal className="w-4 h-4 text-purple-400" />
                      <span className="text-sm font-semibold text-white">Editor de Código</span>
                    </div>
                    <button
                      onClick={handleSubmit}
                      disabled={isSubmitting}
                      className="px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-semibold text-sm hover:shadow-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          Evaluando...
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4" />
                          Ejecutar y Evaluar
                        </>
                      )}
                    </button>
                  </div>
                  <div className="h-[400px]">
                    <Editor
                      height="100%"
                      defaultLanguage="python"
                      theme="vs-dark"
                      value={code}
                      onChange={(value) => setCode(value || '')}
                      options={{
                        minimap: { enabled: false },
                        fontSize: 14,
                        lineNumbers: 'on',
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                        tabSize: 4,
                      }}
                    />
                  </div>
                </div>

                {/* Results */}
                {result && (
                  <div className="glass rounded-2xl p-6 animate-slideIn">
                    <div className="flex items-center gap-3 mb-4">
                      {result.is_correct ? (
                        <CheckCircle className="w-6 h-6 text-green-400" />
                      ) : (
                        <XCircle className="w-6 h-6 text-red-400" />
                      )}
                      <h3 className="text-xl font-bold text-white">
                        {result.is_correct ? '¡Excelente! Código correcto' : 'Algunos tests fallaron'}
                      </h3>
                    </div>

                    {/* Test Results */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                      <div className="bg-gray-800/50 rounded-xl p-4">
                        <div className="text-gray-400 text-sm mb-1">Tests Pasados</div>
                        <div className="text-2xl font-bold text-white">
                          {result.passed_tests}/{result.total_tests}
                        </div>
                      </div>
                      <div className="bg-gray-800/50 rounded-xl p-4">
                        <div className="text-gray-400 text-sm mb-1">Tiempo</div>
                        <div className="text-2xl font-bold text-white">{result.execution_time_ms}ms</div>
                      </div>
                      {result.ai_score !== undefined && (
                        <div className="bg-gray-800/50 rounded-xl p-4">
                          <div className="text-gray-400 text-sm mb-1">Puntuación IA</div>
                          <div className="text-2xl font-bold text-purple-400">{result.ai_score.toFixed(1)}/10</div>
                        </div>
                      )}
                      {result.code_quality_score !== undefined && (
                        <div className="bg-gray-800/50 rounded-xl p-4">
                          <div className="text-gray-400 text-sm mb-1">Calidad</div>
                          <div className="text-2xl font-bold text-blue-400">
                            {result.code_quality_score.toFixed(1)}/10
                          </div>
                        </div>
                      )}
                    </div>

                    {/* AI Feedback */}
                    {result.ai_feedback && (
                      <div className="bg-gradient-to-r from-purple-900/20 to-pink-900/20 border border-purple-500/30 rounded-xl p-6">
                        <div className="flex items-center gap-2 mb-3">
                          <Sparkles className="w-5 h-5 text-purple-400" />
                          <h4 className="font-semibold text-white">Feedback de IA</h4>
                        </div>
                        <p className="text-gray-300 leading-relaxed">{result.ai_feedback}</p>
                      </div>
                    )}

                    {/* Detailed Scores */}
                    {(result.readability_score || result.efficiency_score || result.best_practices_score) && (
                      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                        {result.readability_score !== undefined && (
                          <div className="bg-gray-800/50 rounded-xl p-4">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm text-gray-400">Legibilidad</span>
                              <span className="text-sm font-bold text-white">
                                {result.readability_score.toFixed(1)}/10
                              </span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-2">
                              <div
                                className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all"
                                style={{ width: `${(result.readability_score / 10) * 100}%` }}
                              />
                            </div>
                          </div>
                        )}
                        {result.efficiency_score !== undefined && (
                          <div className="bg-gray-800/50 rounded-xl p-4">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm text-gray-400">Eficiencia</span>
                              <span className="text-sm font-bold text-white">
                                {result.efficiency_score.toFixed(1)}/10
                              </span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-2">
                              <div
                                className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full transition-all"
                                style={{ width: `${(result.efficiency_score / 10) * 100}%` }}
                              />
                            </div>
                          </div>
                        )}
                        {result.best_practices_score !== undefined && (
                          <div className="bg-gray-800/50 rounded-xl p-4">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-sm text-gray-400">Buenas Prácticas</span>
                              <span className="text-sm font-bold text-white">
                                {result.best_practices_score.toFixed(1)}/10
                              </span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-2">
                              <div
                                className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all"
                                style={{ width: `${(result.best_practices_score / 10) * 100}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Test Details */}
                    {result.test_results && result.test_results.length > 0 && (
                      <div className="mt-6">
                        <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                          <BarChart3 className="w-4 h-4 text-purple-400" />
                          Detalles de Tests
                        </h4>
                        <div className="space-y-2">
                          {result.test_results.map((test, index) => (
                            <div
                              key={index}
                              className={`p-3 rounded-lg border ${
                                test.passed
                                  ? 'bg-green-500/10 border-green-500/30'
                                  : 'bg-red-500/10 border-red-500/30'
                              }`}
                            >
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium text-white">{test.name}</span>
                                {test.passed ? (
                                  <CheckCircle className="w-4 h-4 text-green-400" />
                                ) : (
                                  <XCircle className="w-4 h-4 text-red-400" />
                                )}
                              </div>
                              {!test.passed && test.error && (
                                <p className="text-xs text-red-400 mt-2">{test.error}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              <div className="glass rounded-2xl p-12 text-center">
                <Code className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-400 mb-2">Selecciona un ejercicio</h3>
                <p className="text-gray-500">Elige un ejercicio de la lista para comenzar a programar</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExercisesPageNew;
