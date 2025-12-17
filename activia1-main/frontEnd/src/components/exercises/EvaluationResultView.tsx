/**
 * EvaluationResultView Component
 * Muestra el resultado de la evaluación de Alex con todas las dimensiones
 */
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Trophy,
  Award,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  Code,
  Info,
} from 'lucide-react';
import { IEvaluationResult, ACHIEVEMENTS_CATALOG } from '@/types';

interface EvaluationResultViewProps {
  result: IEvaluationResult;
  studentCode: string;
  onRetry?: () => void;
}

export const EvaluationResultView: React.FC<EvaluationResultViewProps> = ({
  result,
  studentCode,
  onRetry,
}) => {
  const [showRefactoring, setShowRefactoring] = useState(false);

  const getStatusIcon = () => {
    switch (result.evaluation.status) {
      case 'PASS':
        return <CheckCircle className="text-green-500" size={32} />;
      case 'PARTIAL':
      case 'WARNING':
        return <AlertTriangle className="text-yellow-500" size={32} />;
      case 'FAIL':
        return <XCircle className="text-red-500" size={32} />;
      default:
        return <Info className="text-blue-500" size={32} />;
    }
  };

  const getStatusColor = () => {
    switch (result.evaluation.toast_type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'info':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getDimensionColor = (score: number) => {
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="space-y-6">
      {/* Header con resultado general */}
      <div className={`rounded-lg shadow-lg border-2 p-6 ${getStatusColor()}`}>
        <div className="flex items-start gap-4">
          <div>{getStatusIcon()}</div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold mb-2 text-gray-900">{result.evaluation.title}</h2>
            <div className="prose prose-gray max-w-none text-gray-900">
              <ReactMarkdown>{result.evaluation.summary_markdown}</ReactMarkdown>
            </div>
            <div className="mt-4 flex items-center gap-4">
              <div className="bg-white rounded-lg px-4 py-2 shadow">
                <span className="text-sm text-gray-600">Score General</span>
                <div className="text-3xl font-bold text-blue-600">
                  {result.evaluation.score.toFixed(1)}<span className="text-lg text-gray-500">/100</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Dimensiones */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h3 className="text-xl font-bold mb-4 text-gray-900">📊 Evaluación por Dimensiones</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Functionality */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-gray-900">⚙️ Funcionalidad</span>
              <span className={`text-2xl font-bold ${getDimensionColor(result.dimensions.functionality.score)}`}>
                {result.dimensions.functionality.score.toFixed(1)}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div
                className={`h-2 rounded-full ${
                  result.dimensions.functionality.score >= 8 ? 'bg-green-500' :
                  result.dimensions.functionality.score >= 6 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${(result.dimensions.functionality.score / 10) * 100}%` }}
              />
            </div>
            <p className="text-sm text-gray-600">{result.dimensions.functionality.comment}</p>
          </div>

          {/* Code Quality */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-gray-900">✨ Calidad</span>
              <span className={`text-2xl font-bold ${getDimensionColor(result.dimensions.code_quality.score)}`}>
                {result.dimensions.code_quality.score.toFixed(1)}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div
                className={`h-2 rounded-full ${
                  result.dimensions.code_quality.score >= 8 ? 'bg-green-500' :
                  result.dimensions.code_quality.score >= 6 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${(result.dimensions.code_quality.score / 10) * 100}%` }}
              />
            </div>
            <p className="text-sm text-gray-600">{result.dimensions.code_quality.comment}</p>
          </div>

          {/* Robustness */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="font-semibold text-gray-900">🛡️ Robustez</span>
              <span className={`text-2xl font-bold ${getDimensionColor(result.dimensions.robustness.score)}`}>
                {result.dimensions.robustness.score.toFixed(1)}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div
                className={`h-2 rounded-full ${
                  result.dimensions.robustness.score >= 8 ? 'bg-green-500' :
                  result.dimensions.robustness.score >= 6 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${(result.dimensions.robustness.score / 10) * 100}%` }}
              />
            </div>
            <p className="text-sm text-gray-600">{result.dimensions.robustness.comment}</p>
          </div>
        </div>
      </div>

      {/* Anotaciones de código */}
      {result.code_review.highlighted_lines.length > 0 && (
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h3 className="text-xl font-bold mb-4 text-gray-900">💬 Comentarios en el Código</h3>
          <div className="space-y-3">
            {result.code_review.highlighted_lines.map((annotation, idx) => (
              <div
                key={idx}
                className={`border rounded-lg p-4 ${getSeverityColor(annotation.severity)}`}
              >
                <div className="flex items-start gap-3">
                  <span className="font-mono text-sm font-bold">Línea {annotation.line_number}</span>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${getSeverityColor(annotation.severity)}`}>
                    {annotation.severity.toUpperCase()}
                  </span>
                  <p className="flex-1 text-sm">{annotation.message}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Refactoring sugerido */}
      {result.code_review.refactoring_suggestion && (
        <div className="bg-white rounded-lg shadow border border-gray-200">
          <button
            onClick={() => setShowRefactoring(!showRefactoring)}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Code className="text-purple-600" size={20} />
              <h3 className="font-bold text-lg text-gray-900">Versión Senior (Cómo un experto lo escribiría)</h3>
            </div>
            {showRefactoring ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
          </button>
          {showRefactoring && (
            <div className="p-4 border-t border-gray-200">
              <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                <code>{result.code_review.refactoring_suggestion}</code>
              </pre>
            </div>
          )}
        </div>
      )}

      {/* Gamificación */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg shadow border-2 border-purple-200 p-6">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2 text-gray-900">
          <Trophy className="text-yellow-500" />
          Recompensas
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* XP */}
          <div className="bg-white rounded-lg p-4 shadow">
            <div className="text-sm text-gray-600 mb-1">XP Ganados</div>
            <div className="text-4xl font-bold text-blue-600">
              +{result.gamification.xp_earned}
            </div>
          </div>

          {/* Logros */}
          {result.gamification.achievements_unlocked.length > 0 && (
            <div className="bg-white rounded-lg p-4 shadow">
              <div className="text-sm text-gray-600 mb-2">Logros Desbloqueados</div>
              <div className="space-y-2">
                {result.gamification.achievements_unlocked.map((achievementId) => {
                  const achievement = ACHIEVEMENTS_CATALOG.find(a => a.id === achievementId);
                  if (!achievement) return null;
                  
                  return (
                    <div
                      key={achievementId}
                      className="flex items-center gap-2 bg-gradient-to-r from-yellow-100 to-orange-100 rounded-lg p-2 border border-yellow-300"
                    >
                      <span className="text-2xl">{achievement.icon}</span>
                      <div className="flex-1">
                        <div className="font-semibold text-sm">{achievement.name}</div>
                        <div className="text-xs text-gray-600">{achievement.description}</div>
                      </div>
                      <Award className="text-yellow-600" size={20} />
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Botón de reintentar */}
      {onRetry && (
        <div className="flex justify-center">
          <button
            onClick={onRetry}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-lg transition-colors shadow-lg"
          >
            <RotateCcw size={20} />
            Intentar de Nuevo
          </button>
        </div>
      )}
    </div>
  );
};
