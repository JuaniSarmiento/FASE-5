import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
// FIX DEFECTO 10.1 Cortez14: Use exercisesService for exercise operations
import { exercisesService } from '../services/api';
import { Exercise, SubmissionResult } from '../types';
import Editor from '@monaco-editor/react';
import {
  ArrowLeft,
  Play,
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  Star,
  Lightbulb,
  AlertCircle,
  Trophy
} from 'lucide-react';

export default function ExerciseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [code, setCode] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<SubmissionResult | null>(null);
  const [showHints, setShowHints] = useState(false);
  const [currentHint, setCurrentHint] = useState(0);

  // FIX Cortez21 DEFECTO 4.2: Add isMounted check to prevent memory leak
  useEffect(() => {
    let isMounted = true;
    const controller = new AbortController();

    const fetchExercise = async () => {
      if (!id) return;

      try {
        // FIX DEFECTO 10.1 Cortez14: Use exercisesService.getById instead of activitiesService.get
        const response = await exercisesService.getById(id);

        // FIX Cortez21: Only update state if component is still mounted
        if (isMounted) {
          setExercise(response);
          setCode(response.starter_code || '# Escribe tu código aquí\n\ndef solution():\n    pass\n');
        }
      } catch (error) {
        // FIX Cortez21: Only update state if mounted and not aborted
        if (isMounted && !controller.signal.aborted) {
          if (import.meta.env.DEV) {
            console.error('Error fetching exercise:', error);
          }
          // FIX Cortez21 DEFECTO 4.3: Show error state instead of mock data
          // Mock exercise for demo - only in development
          if (import.meta.env.DEV) {
            setExercise({
              id: id,
              title: 'Suma de dos números',
              description: 'Escribe una función llamada `suma` que reciba dos números como parámetros y retorne su suma.\n\n**Ejemplo:**\n```python\nsuma(2, 3)  # Retorna 5\nsuma(-1, 1) # Retorna 0\n```',
              difficulty_level: 1,
              starter_code: '# Escribe tu solución aquí\n\ndef suma(a, b):\n    # Tu código aquí\n    pass\n',
              hints: [
                'Recuerda que la función debe recibir dos parámetros',
                'Usa el operador + para sumar',
                'No olvides usar return para devolver el resultado'
              ],
              max_score: 100,
              time_limit_seconds: 300
            });
            setCode('# Escribe tu solución aquí\n\ndef suma(a, b):\n    # Tu código aquí\n    pass\n');
          }
        }
      } finally {
        // FIX Cortez21: Only update loading state if mounted
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    fetchExercise();

    // FIX Cortez21: Cleanup function to prevent memory leak
    return () => {
      isMounted = false;
      controller.abort();
    };
  }, [id]);

  const handleSubmit = async () => {
    if (!exercise || !code.trim()) return;
    
    setIsSubmitting(true);
    setResult(null);

    try {
      // FIX 2.4: Use exercisesService for code submission
      const response = await exercisesService.submit({
        exercise_id: exercise.id,
        code: code
      });
      setResult(response);
    } catch (error: unknown) {
      // Log error in development
      if (import.meta.env.DEV) {
        console.error('Submit error:', error);
      }
      // Mock result for demo
      setResult({
        id: Date.now().toString(),
        passed_tests: 2,
        total_tests: 3,
        is_correct: false,
        execution_time_ms: 45,
        ai_score: 75,
        ai_feedback: 'Tu solución es casi correcta, pero hay un caso de borde que no maneja correctamente. Revisa qué sucede cuando uno de los números es negativo.',
        code_quality_score: 80,
        readability_score: 85,
        efficiency_score: 70,
        best_practices_score: 75,
        test_results: [
          { name: 'Test básico', passed: true, input: 'suma(2, 3)', expected_output: '5', actual_output: '5' },
          { name: 'Test con cero', passed: true, input: 'suma(0, 5)', expected_output: '5', actual_output: '5' },
          { name: 'Test con negativos', passed: false, input: 'suma(-1, -1)', expected_output: '-2', actual_output: 'None', error: 'El resultado es None' }
        ]
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-[var(--accent-primary)] animate-spin" />
      </div>
    );
  }

  if (!exercise) {
    return (
      <div className="text-center py-12">
        <p className="text-[var(--text-secondary)]">Ejercicio no encontrado</p>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col animate-fadeIn">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/exercises')}
            className="p-2 rounded-lg hover:bg-[var(--bg-hover)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-[var(--text-primary)]">{exercise.title}</h1>
            <div className="flex items-center gap-4 text-sm text-[var(--text-muted)]">
              <span className="flex items-center gap-1">
                <Star className="w-4 h-4" />
                Nivel {exercise.difficulty_level}
              </span>
              <span className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                {Math.floor(exercise.time_limit_seconds / 60)} min
              </span>
              <span className="flex items-center gap-1">
                <Trophy className="w-4 h-4" />
                {exercise.max_score} pts
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="flex items-center gap-2 px-6 py-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-600 text-white font-medium hover:opacity-90 disabled:opacity-50 transition-all"
        >
          {isSubmitting ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Play className="w-5 h-5" />
          )}
          Ejecutar
        </button>
      </div>

      {/* Main Content */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 min-h-0">
        {/* Left Panel - Description & Hints */}
        <div className="flex flex-col gap-4 overflow-y-auto">
          <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-color)] p-6">
            <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">Descripción</h2>
            <div className="prose prose-invert max-w-none text-[var(--text-secondary)]">
              {exercise.description.split('\n').map((line, i) => (
                <p key={i} className="mb-2">{line}</p>
              ))}
            </div>
          </div>

          {exercise.hints && exercise.hints.length > 0 && (
            <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-color)] p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-[var(--text-primary)] flex items-center gap-2">
                  <Lightbulb className="w-5 h-5 text-yellow-400" />
                  Pistas
                </h2>
                <button
                  onClick={() => setShowHints(!showHints)}
                  className="text-sm text-[var(--accent-primary)] hover:text-[var(--accent-secondary)]"
                >
                  {showHints ? 'Ocultar' : 'Mostrar'}
                </button>
              </div>
              {showHints && (
                <div className="space-y-3">
                  {exercise.hints.slice(0, currentHint + 1).map((hint, i) => (
                    <div key={i} className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-[var(--text-secondary)]">
                      <span className="font-medium text-yellow-400">Pista {i + 1}:</span> {hint}
                    </div>
                  ))}
                  {currentHint < exercise.hints.length - 1 && (
                    <button
                      onClick={() => setCurrentHint(currentHint + 1)}
                      className="text-sm text-[var(--accent-primary)] hover:text-[var(--accent-secondary)]"
                    >
                      Ver siguiente pista ({currentHint + 2}/{exercise.hints.length})
                    </button>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-color)] p-6 animate-slideIn">
              <div className="flex items-center gap-3 mb-4">
                {result.is_correct ? (
                  <CheckCircle className="w-6 h-6 text-green-400" />
                ) : (
                  <AlertCircle className="w-6 h-6 text-yellow-400" />
                )}
                <h2 className="text-lg font-semibold text-[var(--text-primary)]">
                  Resultados
                </h2>
              </div>

              {/* Test Results */}
              <div className="mb-4">
                <p className="text-sm text-[var(--text-muted)] mb-2">
                  Tests pasados: {result.passed_tests}/{result.total_tests}
                </p>
                <div className="h-2 rounded-full bg-[var(--bg-tertiary)] overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-600 transition-all duration-500"
                    style={{ width: `${(result.passed_tests / result.total_tests) * 100}%` }}
                  />
                </div>
              </div>

              {/* Individual Tests */}
              <div className="space-y-2 mb-4">
                {result.test_results.map((test, i) => (
                  <div key={i} className={`p-3 rounded-lg ${test.passed ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
                    <div className="flex items-center gap-2">
                      {test.passed ? (
                        <CheckCircle className="w-4 h-4 text-green-400" />
                      ) : (
                        <XCircle className="w-4 h-4 text-red-400" />
                      )}
                      <span className="font-medium text-[var(--text-primary)]">{test.name}</span>
                    </div>
                    {!test.passed && (
                      <div className="mt-2 text-sm text-[var(--text-secondary)]">
                        <p>Entrada: <code className="px-1 bg-[var(--bg-tertiary)] rounded">{test.input}</code></p>
                        <p>Esperado: <code className="px-1 bg-[var(--bg-tertiary)] rounded">{test.expected_output}</code></p>
                        <p>Obtenido: <code className="px-1 bg-[var(--bg-tertiary)] rounded">{test.actual_output}</code></p>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* AI Feedback */}
              {result.ai_feedback && (
                <div className="p-4 rounded-lg bg-[var(--accent-primary)]/10 border border-[var(--accent-primary)]/20">
                  <h3 className="text-sm font-medium text-[var(--accent-primary)] mb-2">Feedback del Tutor IA</h3>
                  <p className="text-sm text-[var(--text-secondary)]">{result.ai_feedback}</p>
                </div>
              )}

              {/* Scores */}
              {result.ai_score && (
                <div className="mt-4 grid grid-cols-2 gap-4">
                  <div className="text-center p-3 rounded-lg bg-[var(--bg-tertiary)]">
                    <p className="text-2xl font-bold text-[var(--text-primary)]">{result.ai_score}%</p>
                    <p className="text-xs text-[var(--text-muted)]">Puntuación IA</p>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-[var(--bg-tertiary)]">
                    <p className="text-2xl font-bold text-[var(--text-primary)]">{result.execution_time_ms}ms</p>
                    <p className="text-xs text-[var(--text-muted)]">Tiempo ejecución</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right Panel - Code Editor */}
        <div className="bg-[var(--bg-card)] rounded-xl border border-[var(--border-color)] overflow-hidden flex flex-col">
          <div className="p-3 border-b border-[var(--border-color)] flex items-center justify-between">
            <span className="text-sm font-medium text-[var(--text-secondary)]">Python</span>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500"></span>
              <span className="w-3 h-3 rounded-full bg-yellow-500"></span>
              <span className="w-3 h-3 rounded-full bg-green-500"></span>
            </div>
          </div>
          <div className="flex-1">
            <Editor
              height="100%"
              defaultLanguage="python"
              value={code}
              onChange={(value) => setCode(value || '')}
              theme="vs-dark"
              options={{
                fontSize: 14,
                minimap: { enabled: false },
                padding: { top: 16 },
                scrollBeyondLastLine: false,
                lineNumbers: 'on',
                renderLineHighlight: 'line',
                fontFamily: 'JetBrains Mono, monospace'
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
