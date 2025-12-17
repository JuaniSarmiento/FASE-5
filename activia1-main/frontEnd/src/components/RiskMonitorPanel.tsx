/**
 * RiskMonitorPanel - Panel lateral para monitoreo de riesgos en tiempo real
 * Muestra los indicadores de las 5 dimensiones de riesgo durante la sesión
 */
import React from 'react';
import { Shield, AlertTriangle, TrendingDown, TrendingUp, Activity } from 'lucide-react';

interface RiskDimensionStatus {
  dimension: string;
  score: number;
  level: string;
  icon: string;
  color: string;
  name: string;
}

interface RiskMonitorPanelProps {
  currentRiskLevel?: string;
  dimensions?: Record<string, { score: number; level: string; indicators: string[] }>;
  isCompact?: boolean;
}

const DIMENSION_CONFIG: Record<string, { icon: string; name: string; color: string }> = {
  cognitive: { icon: '🧠', name: 'Cognitiva', color: 'text-purple-400' },
  ethical: { icon: '⚖️', name: 'Ética', color: 'text-blue-400' },
  epistemic: { icon: '📚', name: 'Epistémica', color: 'text-cyan-400' },
  technical: { icon: '⚙️', name: 'Técnica', color: 'text-orange-400' },
  governance: { icon: '🏛️', name: 'Gobernanza', color: 'text-green-400' }
};

const RiskMonitorPanel: React.FC<RiskMonitorPanelProps> = ({ 
  currentRiskLevel = 'info', 
  dimensions,
  isCompact = false 
}) => {
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'info':
        return { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400', bar: 'bg-blue-500' };
      case 'low':
        return { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-400', bar: 'bg-green-500' };
      case 'medium':
        return { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400', bar: 'bg-yellow-500' };
      case 'high':
        return { bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400', bar: 'bg-orange-500' };
      case 'critical':
        return { bg: 'bg-red-500/10', border: 'border-red-500/30', text: 'text-red-400', bar: 'bg-red-500' };
      default:
        return { bg: 'bg-gray-500/10', border: 'border-gray-500/30', text: 'text-gray-400', bar: 'bg-gray-500' };
    }
  };

  const overallColor = getRiskColor(currentRiskLevel);

  const dimensionStatuses: RiskDimensionStatus[] = Object.entries(dimensions || {}).map(([key, data]) => ({
    dimension: key,
    score: data.score,
    level: data.level,
    icon: DIMENSION_CONFIG[key]?.icon || '🔍',
    color: DIMENSION_CONFIG[key]?.color || 'text-gray-400',
    name: DIMENSION_CONFIG[key]?.name || key
  }));

  if (isCompact) {
    return (
      <div className="glass rounded-xl p-3 border border-gray-700">
        <div className="flex items-center gap-2 mb-2">
          <Shield className={`w-4 h-4 ${overallColor.text}`} />
          <span className="text-xs font-semibold text-white">Monitor de Riesgos</span>
        </div>
        <div className="space-y-1.5">
          {dimensionStatuses.map((dim) => {
            const dimColor = getRiskColor(dim.level);
            return (
              <div key={dim.dimension} className="flex items-center gap-2">
                <span className="text-sm">{dim.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="w-full bg-gray-800 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full ${dimColor.bar}`}
                      style={{ width: `${Math.min(dim.score * 10, 100)}%` }}
                    />
                  </div>
                </div>
                <span className={`text-xs ${dimColor.text} font-medium`}>{dim.level}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div className="glass rounded-xl p-4 border border-gray-700">
      {/* Header */}
      <div className="flex items-center gap-2 mb-4">
        <Shield className={`w-5 h-5 ${overallColor.text}`} />
        <div className="flex-1">
          <h3 className="text-sm font-bold text-white">Monitor de Riesgos 5D</h3>
          <p className="text-xs text-gray-400">Análisis en tiempo real</p>
        </div>
        <Activity className={`w-4 h-4 ${overallColor.text} animate-pulse`} />
      </div>

      {/* Overall Status */}
      <div className={`${overallColor.bg} ${overallColor.border} border rounded-lg p-3 mb-4`}>
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-400">Nivel General</span>
          <span className={`text-sm font-bold ${overallColor.text} uppercase`}>
            {currentRiskLevel}
          </span>
        </div>
      </div>

      {/* Dimensions */}
      <div className="space-y-3">
        {dimensionStatuses.map((dim) => {
          const dimColor = getRiskColor(dim.level);
          return (
            <div key={dim.dimension} className="space-y-1.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{dim.icon}</span>
                  <span className="text-xs font-medium text-white">{dim.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs ${dimColor.text}`}>{dim.score}/10</span>
                  {dim.level === 'low' || dim.level === 'info' ? (
                    <TrendingDown className="w-3 h-3 text-green-400" />
                  ) : dim.level === 'high' || dim.level === 'critical' ? (
                    <TrendingUp className="w-3 h-3 text-red-400" />
                  ) : (
                    <AlertTriangle className="w-3 h-3 text-yellow-400" />
                  )}
                </div>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${dimColor.bar}`}
                  style={{ width: `${Math.min(dim.score * 10, 100)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-gray-700">
        <div className="flex items-center gap-1.5 text-xs text-gray-400">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span>Bajo</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-yellow-500" />
            <span>Medio</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-orange-500" />
            <span>Alto</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-red-500" />
            <span>Crítico</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskMonitorPanel;
