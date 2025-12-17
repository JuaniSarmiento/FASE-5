/**
 * Componente de Evaluación de Código - UI para mostrar resultados del mentor "Alex"
 * 
 * Este componente recibe IEvaluationResult y renderiza:
 * - Score y status
 * - Feedback narrativo
 * - Anotaciones de código línea por línea
 * - Sugerencias de refactoring
 * - Gamificación (XP, logros)
 */

import React, { useState } from 'react';
import { 
  IEvaluationResult, 
  ICodeAnnotation, 
  Severity,
  IAchievement,
  ACHIEVEMENTS_CATALOG 
} from '@/types';
import ReactMarkdown from 'react-markdown';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Award,
  Zap,
  Code,
  AlertCircle,
  Info
} from 'lucide-react';

interface EvaluationResultViewProps {
  result: IEvaluationResult;
  studentCode: string;
  onRetry?: () => void;
}

/**
 * Vista principal del resultado de evaluación
 */
export const EvaluationResultView: React.FC<EvaluationResultViewProps> = ({
  result,
  studentCode,
  onRetry
}) => {
  const [showRefactoring, setShowRefactoring] = useState(false);

  const getStatusIcon = () => {
    switch (result.evaluation.status) {
      case 'PASS':
        return <CheckCircle className="text-green-400" size={32} />;
      case 'FAIL':
        return <XCircle className="text-red-400" size={32} />;
      case 'WARNING':
        return <AlertTriangle className="text-yellow-400" size={32} />;
    }
  };

  const getStatusColor = () => {
    switch (result.evaluation.status) {
      case 'PASS':
        return 'border-green-500 bg-green-900/20';
      case 'FAIL':
        return 'border-red-500 bg-red-900/20';
      case 'WARNING':
        return 'border-yellow-500 bg-yellow-900/20';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="space-y-6">
      {/* Header con Score */}
      <div className={`rounded-xl p-6 border-2 ${getStatusColor()}`}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-4">
            {getStatusIcon()}
            <div>
              <h3 className="text-2xl font-bold text-white">
                {result.evaluation.title}
              </h3>
              <p className="text-gray-400 text-sm mt-1">
                Evaluado por Alex - Mentor Técnico
              </p>
            </div>
          </div>
          
          {/* Score Badge */}
          <div className="text-center">
            <div className={`text-5xl font-bold ${getScoreColor(result.evaluation.score)}`}>
              {result.evaluation.score}
            </div>
            <div className="text-gray-400 text-sm">/ 100</div>
          </div>
        </div>

        {/* Feedback Summary */}
        <div className="bg-black/30 rounded-lg p-4">
          <ReactMarkdown className="prose prose-invert max-w-none text-gray-300">
            {result.evaluation.summary_markdown}
          </ReactMarkdown>
        </div>
      </div>

      {/* Dimensions Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <DimensionCard
          title="Functionality"
          icon="⚙️"
          score={result.dimensions.functionality.score}
          comment={result.dimensions.functionality.comment}
        />
        <DimensionCard
          title="Code Quality"
          icon="✨"
          score={result.dimensions.code_quality.score}
          comment={result.dimensions.code_quality.comment}
        />
        <DimensionCard
          title="Robustness"
          icon="🛡️"
          score={result.dimensions.robustness.score}
          comment={result.dimensions.robustness.comment}
        />
      </div>

      {/* Code Review Annotations */}
      {result.code_review.highlighted_lines.length > 0 && (
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <h4 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <Code size={20} />
            Code Review
          </h4>
          <div className="space-y-3">
            {result.code_review.highlighted_lines.map((annotation, idx) => (
              <CodeAnnotationItem
                key={idx}
                annotation={annotation}
                code={studentCode}
              />
            ))}
          </div>
        </div>
      )}

      {/* Refactoring Suggestion */}
      {result.code_review.refactoring_suggestion && (
        <div className="bg-purple-900/20 rounded-xl p-6 border border-purple-500/30">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-xl font-semibold text-purple-300 flex items-center gap-2">
              <Zap size={20} />
              Versión Senior
            </h4>
            <button
              onClick={() => setShowRefactoring(!showRefactoring)}
              className="text-purple-400 hover:text-purple-300 text-sm"
            >
              {showRefactoring ? 'Ocultar' : 'Mostrar'}
            </button>
          </div>
          
          {showRefactoring && (
            <pre className="bg-black/40 rounded-lg p-4 overflow-x-auto">
              <code className="text-sm text-gray-300">
                {result.code_review.refactoring_suggestion}
              </code>
            </pre>
          )}
        </div>
      )}

      {/* Gamification */}
      <GamificationPanel
        xp={result.gamification.xp_earned}
        achievements={result.gamification.achievements_unlocked}
      />

      {/* Action Buttons */}
      <div className="flex gap-4">
        {onRetry && result.evaluation.status !== 'PASS' && (
          <button
            onClick={onRetry}
            className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            Intentar de Nuevo
          </button>
        )}
        {result.evaluation.status === 'PASS' && (
          <button
            className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            Siguiente Ejercicio →
          </button>
        )}
      </div>
    </div>
  );
};

/**
 * Card de dimensión individual
 */
const DimensionCard: React.FC<{
  title: string;
  icon: string;
  score: number;
  comment: string;
}> = ({ title, icon, score, comment }) => {
  const getScoreColor = () => {
    if (score >= 9) return 'text-green-400';
    if (score >= 7) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getProgressColor = () => {
    if (score >= 9) return 'bg-green-500';
    if (score >= 7) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="bg-gray-800/50 rounded-xl p-5 border border-gray-700">
      <div className="flex items-center gap-3 mb-3">
        <span className="text-2xl">{icon}</span>
        <div className="flex-1">
          <h5 className="font-semibold text-white">{title}</h5>
          <div className={`text-2xl font-bold ${getScoreColor()}`}>
            {score}/10
          </div>
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="w-full bg-gray-700 rounded-full h-2 mb-3">
        <div
          className={`${getProgressColor()} h-2 rounded-full transition-all`}
          style={{ width: `${(score / 10) * 100}%` }}
        />
      </div>
      
      <p className="text-gray-400 text-sm">{comment}</p>
    </div>
  );
};

/**
 * Item de anotación de código
 */
const CodeAnnotationItem: React.FC<{
  annotation: ICodeAnnotation;
  code: string;
}> = ({ annotation, code }) => {
  const getSeverityIcon = (severity: Severity) => {
    switch (severity) {
      case 'error':
        return <AlertCircle className="text-red-400" size={18} />;
      case 'warning':
        return <AlertTriangle className="text-yellow-400" size={18} />;
      case 'info':
        return <Info className="text-blue-400" size={18} />;
    }
  };

  const getSeverityColor = (severity: Severity) => {
    switch (severity) {
      case 'error':
        return 'border-red-500 bg-red-900/20';
      case 'warning':
        return 'border-yellow-500 bg-yellow-900/20';
      case 'info':
        return 'border-blue-500 bg-blue-900/20';
    }
  };

  // Extraer la línea de código
  const lines = code.split('\n');
  const codeLine = lines[annotation.line_number - 1] || '';

  return (
    <div className={`rounded-lg p-4 border ${getSeverityColor(annotation.severity)}`}>
      <div className="flex items-start gap-3">
        {getSeverityIcon(annotation.severity)}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-white font-semibold">Línea {annotation.line_number}</span>
            <span className="text-xs text-gray-500 uppercase">{annotation.severity}</span>
          </div>
          
          {/* Código */}
          <pre className="bg-black/40 rounded p-2 mb-2 overflow-x-auto">
            <code className="text-sm text-gray-300">{codeLine}</code>
          </pre>
          
          {/* Mensaje */}
          <p className="text-gray-300 text-sm">{annotation.message}</p>
        </div>
      </div>
    </div>
  );
};

/**
 * Panel de gamificación
 */
const GamificationPanel: React.FC<{
  xp: number;
  achievements: string[];
}> = ({ xp, achievements }) => {
  if (xp === 0 && achievements.length === 0) {
    return null;
  }

  // Mapear achievements a sus datos completos
  const achievementData = achievements.map(name =>
    ACHIEVEMENTS_CATALOG.find(a => a.name === name)
  ).filter(Boolean) as IAchievement[];

  return (
    <div className="bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-xl p-6 border border-purple-500/30">
      <div className="flex items-center gap-4 mb-4">
        <Award className="text-yellow-400" size={28} />
        <div>
          <h4 className="text-xl font-semibold text-white">Recompensas</h4>
          <p className="text-gray-400 text-sm">¡Sigue así!</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* XP Earned */}
        <div className="bg-black/30 rounded-lg p-4 flex items-center gap-3">
          <Zap className="text-yellow-400" size={24} />
          <div>
            <div className="text-2xl font-bold text-yellow-400">+{xp} XP</div>
            <div className="text-gray-400 text-sm">Experiencia ganada</div>
          </div>
        </div>

        {/* Achievements */}
        {achievementData.length > 0 && (
          <div className="bg-black/30 rounded-lg p-4">
            <h5 className="text-white font-semibold mb-2">Logros Desbloqueados</h5>
            <div className="space-y-1">
              {achievementData.map((achievement, idx) => (
                <div key={idx} className="flex items-center gap-2 text-sm">
                  <span>{achievement.icon}</span>
                  <span className="text-gray-300">{achievement.name}</span>
                  {achievement.rarity === 'legendary' && (
                    <span className="text-yellow-400 text-xs">★</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default EvaluationResultView;
