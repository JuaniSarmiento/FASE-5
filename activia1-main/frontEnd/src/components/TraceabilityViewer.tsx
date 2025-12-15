/**
 * TraceabilityViewer - Modal component for viewing N4 traceability data
 * FIX 2.3: Recreated deleted component
 */
import React, { useState } from 'react';
import { GitBranch, Clock, Layers, ChevronDown, ChevronUp, Cpu, Zap } from 'lucide-react';
import { TraceabilityN4, TraceabilityNode } from '../types';

interface TraceabilityViewerProps {
  data: TraceabilityN4;
}

const LEVEL_CONFIG = {
  N1: {
    name: 'Superficial',
    icon: '📥',
    color: '#3b82f6',
    description: 'Datos crudos del usuario'
  },
  N2: {
    name: 'Técnico',
    icon: '🔧',
    color: '#10b981',
    description: 'Preprocesamiento y validación'
  },
  N3: {
    name: 'Interaccional',
    icon: '🤖',
    color: '#8b5cf6',
    description: 'Procesamiento LLM'
  },
  N4: {
    name: 'Cognitivo',
    icon: '🧠',
    color: '#f59e0b',
    description: 'Análisis cognitivo profundo'
  }
};

const TraceabilityViewer: React.FC<TraceabilityViewerProps> = ({ data }) => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <GitBranch className="w-6 h-6 text-purple-400" />
        <div>
          <h3 className="text-xl font-bold text-white">Trazabilidad N4</h3>
          <p className="text-sm text-gray-400">
            Visualización del procesamiento cognitivo en 4 niveles
          </p>
        </div>
      </div>

      {/* Metadata Summary */}
      <div className="grid grid-cols-3 gap-4">
        <div className="glass rounded-xl p-4 text-center">
          <div className="text-2xl mb-1">⏱️</div>
          <div className="text-lg font-bold text-white">{data.metadata.total_processing_time_ms}ms</div>
          <div className="text-xs text-gray-400">Tiempo total</div>
        </div>
        <div className="glass rounded-xl p-4 text-center">
          <div className="text-2xl mb-1">📊</div>
          <div className="text-lg font-bold text-white">{data.nodes.length}</div>
          <div className="text-xs text-gray-400">Nodos procesados</div>
        </div>
        <div className="glass rounded-xl p-4 text-center">
          <div className="text-2xl mb-1">🔗</div>
          <div className="text-lg font-bold text-white">{data.trace_id.slice(0, 8)}...</div>
          <div className="text-xs text-gray-400">Trace ID</div>
        </div>
      </div>

      {/* Trace Flow */}
      <div className="glass rounded-xl p-6">
        <h4 className="font-bold text-white mb-4 flex items-center gap-2">
          <Layers className="w-5 h-5 text-purple-400" />
          Flujo de Procesamiento N4
        </h4>

        <div className="space-y-4">
          {data.nodes.map((node, index) => (
            <TraceNodeCard key={node.id} node={node} isLast={index === data.nodes.length - 1} />
          ))}
        </div>
      </div>

      {/* Timeline */}
      <div className="glass rounded-xl p-6">
        <h4 className="font-bold text-white mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-blue-400" />
          Timeline de Eventos
        </h4>

        <div className="relative">
          {data.nodes.map((node, index) => {
            const config = LEVEL_CONFIG[node.level];
            return (
              <div key={node.id} className="flex items-start gap-4 mb-4 last:mb-0">
                <div className="relative">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-lg"
                    style={{ backgroundColor: `${config.color}20`, border: `2px solid ${config.color}` }}
                  >
                    {config.icon}
                  </div>
                  {index < data.nodes.length - 1 && (
                    <div className="absolute top-10 left-1/2 -translate-x-1/2 w-0.5 h-8 bg-gray-700" />
                  )}
                </div>
                <div className="flex-1 pt-1">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-white" style={{ color: config.color }}>
                      {node.level} - {config.name}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(node.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mt-1">{config.description}</p>
                  {/* FIX Cortez16: Handle optional processing_time_ms */}
                  {(node.metadata.processing_time_ms ?? 0) > 0 && (
                    <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                      <Zap className="w-3 h-3" />
                      {node.metadata.processing_time_ms}ms
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Created At */}
      <div className="text-center text-xs text-gray-500">
        Generado: {new Date(data.metadata.created_at).toLocaleString()}
      </div>
    </div>
  );
};

const TraceNodeCard: React.FC<{ node: TraceabilityNode; isLast: boolean }> = ({ node, isLast }) => {
  const [expanded, setExpanded] = useState(false);
  const config = LEVEL_CONFIG[node.level];

  return (
    <div className="relative">
      <div
        className="border rounded-xl p-4 cursor-pointer transition-all hover:border-purple-500/50"
        style={{ borderColor: `${config.color}40`, backgroundColor: `${config.color}08` }}
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
              style={{ backgroundColor: config.color }}
            >
              {config.icon}
            </div>
            <div>
              <div className="font-bold text-white">{node.level}</div>
              <div className="text-sm text-gray-400">{config.name}</div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            {/* FIX Cortez16: Handle optional processing_time_ms */}
            {(node.metadata.processing_time_ms ?? 0) > 0 && (
              <div className="text-sm text-gray-400">
                <Cpu className="w-4 h-4 inline mr-1" />
                {node.metadata.processing_time_ms}ms
              </div>
            )}
            {expanded ? (
              <ChevronUp className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            )}
          </div>
        </div>

        {expanded && (
          <div className="mt-4 pt-4 border-t border-gray-700 space-y-3">
            <div>
              <h6 className="text-xs font-semibold text-gray-400 mb-1">Timestamp</h6>
              <p className="text-sm text-white">{new Date(node.timestamp).toLocaleString()}</p>
            </div>

            {node.metadata.transformations && node.metadata.transformations.length > 0 && (
              <div>
                <h6 className="text-xs font-semibold text-gray-400 mb-1">Transformaciones</h6>
                <div className="flex flex-wrap gap-2">
                  {node.metadata.transformations.map((t, i) => (
                    <span key={i} className="px-2 py-1 text-xs rounded-full bg-purple-500/20 text-purple-300">
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {Object.keys(node.data).length > 0 && (
              <div>
                <h6 className="text-xs font-semibold text-gray-400 mb-1">Datos</h6>
                <pre className="text-xs text-gray-300 bg-gray-800/50 rounded-lg p-3 overflow-x-auto max-h-40">
                  {JSON.stringify(node.data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Connection line */}
      {!isLast && (
        <div className="absolute left-1/2 -translate-x-1/2 w-0.5 h-4 bg-gray-700" />
      )}
    </div>
  );
};

export default TraceabilityViewer;
