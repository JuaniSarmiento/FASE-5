import React from 'react';
import { Shield, AlertTriangle, TrendingUp, CheckCircle, XCircle } from 'lucide-react';
import { RiskAnalysis5D } from '../types';

interface RiskAnalysisViewerProps {
  data: RiskAnalysis5D;
}

const RiskAnalysisViewer: React.FC<RiskAnalysisViewerProps> = ({ data }) => {
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'info':
        return { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400' };
      case 'low':
        return { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-400' };
      case 'medium':
        return { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400' };
      case 'high':
        return { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400' };
      case 'critical':
        return { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400' };
      default:
        return { bg: 'bg-gray-500/10', border: 'border-gray-500/30', text: 'text-gray-400' };
    }
  };

  const getDimensionIcon = (dimension: string) => {
    switch (dimension) {
      case 'cognitive':
        return '🧠';
      case 'ethical':
        return '⚖️';
      case 'epistemic':
        return '📚';
      case 'technical':
        return '⚙️';
      case 'governance':
        return '🏛️';
      default:
        return '🔍';
    }
  };

  const getDimensionTitle = (dimension: string) => {
    switch (dimension) {
      case 'cognitive':
        return 'Cognitiva';
      case 'ethical':
        return 'Ética';
      case 'epistemic':
        return 'Epistémica';
      case 'technical':
        return 'Técnica';
      case 'governance':
        return 'Gobernanza';
      default:
        return dimension;
    }
  };

  const riskColorClasses = getRiskColor(data.risk_level);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Shield className="w-6 h-6 text-purple-400" />
        <div>
          <h3 className="text-xl font-bold text-white">Análisis de Riesgos 5D</h3>
          <p className="text-sm text-gray-400">
            Evaluación multidimensional de riesgos en el uso de IA
          </p>
        </div>
      </div>

      {/* Overall Score */}
      <div className={`${riskColorClasses.bg} ${riskColorClasses.border} border rounded-2xl p-6`}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h4 className={`text-2xl font-bold ${riskColorClasses.text}`}>
              Nivel de Riesgo: {data.risk_level.toUpperCase()}
            </h4>
            <p className="text-sm text-gray-400 mt-1">Puntuación general del análisis</p>
          </div>
          <div className="text-right">
            <div className={`text-4xl font-bold ${riskColorClasses.text}`}>{data.overall_score}</div>
            <div className="text-sm text-gray-400">/100</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-800 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all ${
              data.risk_level === 'low'
                ? 'bg-gradient-to-r from-green-500 to-emerald-500'
                : data.risk_level === 'medium'
                ? 'bg-gradient-to-r from-yellow-500 to-orange-500'
                : data.risk_level === 'high'
                ? 'bg-gradient-to-r from-orange-500 to-red-500'
                : 'bg-gradient-to-r from-red-500 to-rose-500'
            }`}
            style={{ width: `${data.overall_score}%` }}
          />
        </div>
      </div>

      {/* 5 Dimensions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(data.dimensions).map(([key, dimension]) => {
          const dimColorClasses = getRiskColor(dimension.level);
          return (
            <div key={key} className="glass rounded-xl p-5 hover:border-purple-500/50 transition-all">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-2xl">{getDimensionIcon(key)}</span>
                  <h5 className="font-bold text-white">{getDimensionTitle(key)}</h5>
                </div>
                <span className={`text-lg font-bold ${dimColorClasses.text}`}>{dimension.score}</span>
              </div>

              <div className="mb-3">
                <div className="w-full bg-gray-800 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      dimension.level === 'info'
                        ? 'bg-blue-500'
                        : dimension.level === 'low'
                        ? 'bg-green-500'
                        : dimension.level === 'medium'
                        ? 'bg-yellow-500'
                        : dimension.level === 'high'
                        ? 'bg-orange-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${(dimension.score / 100) * 100}%` }}
                  />
                </div>
              </div>

              {dimension.indicators.length > 0 && (
                <div className="space-y-1">
                  <h6 className="text-xs font-semibold text-gray-400 mb-1">Indicadores:</h6>
                  {/* FIX Cortez16: Add explicit types for map parameters */}
                  {dimension.indicators.slice(0, 3).map((indicator: string, index: number) => (
                    <div key={index} className="flex items-start gap-2">
                      <AlertTriangle className="w-3 h-3 text-gray-500 mt-0.5 flex-shrink-0" />
                      <p className="text-xs text-gray-400">{indicator}</p>
                    </div>
                  ))}
                  {dimension.indicators.length > 3 && (
                    <p className="text-xs text-gray-500">+{dimension.indicators.length - 3} más...</p>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Top Risks */}
      {data.top_risks && data.top_risks.length > 0 && (
        <div className="glass rounded-xl p-6">
          <h4 className="font-bold text-white mb-4 flex items-center gap-2">
            <XCircle className="w-5 h-5 text-red-400" />
            Principales Riesgos Detectados
          </h4>
          <div className="space-y-3">
            {data.top_risks.map((risk, index) => {
              const riskColors = getRiskColor(risk.severity.toLowerCase());
              return (
                <div key={index} className={`${riskColors.bg} ${riskColors.border} border rounded-lg p-4`}>
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-xs font-semibold text-gray-400 uppercase">
                          {risk.dimension}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${riskColors.bg} ${riskColors.text}`}>
                          {risk.severity}
                        </span>
                      </div>
                      <p className="text-sm text-white font-medium">{risk.description}</p>
                    </div>
                  </div>
                  {/* FIX DEFECTO 8.1 Cortez14: Field is 'mitigation' not 'recommendation' */}
                  {risk.mitigation && (
                    <div className="mt-2 flex items-start gap-2">
                      <TrendingUp className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                      <p className="text-xs text-gray-300">{risk.mitigation}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {data.recommendations && data.recommendations.length > 0 && (
        <div className="glass rounded-xl p-6">
          <h4 className="font-bold text-white mb-4 flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-400" />
            Recomendaciones
          </h4>
          <div className="space-y-2">
            {data.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-purple-600/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span className="text-xs font-bold text-purple-400">{index + 1}</span>
                </div>
                <p className="text-sm text-gray-300">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskAnalysisViewer;
