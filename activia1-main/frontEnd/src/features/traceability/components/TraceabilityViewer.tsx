/**
 * Trazabilidad N4 - Visualización de procesamiento en 4 niveles
 */
import React, { useState, useEffect } from 'react';
import { sessionService } from '@/core/services/SessionService';
import { httpClient } from '@/core/http/HttpClient';
import { SessionMode } from '@/types/api.types';
import { useToast } from '@/shared/components/Toast/Toast';
import './TraceabilityViewer.css';

interface TraceNode {
  id: string;
  level: 'N1' | 'N2' | 'N3' | 'N4';
  timestamp: string;
  data: Record<string, unknown>;
  metadata: {
    processing_time_ms?: number;
    tokens_used?: number;
    model?: string;
    transformations?: string[];
  };
}

interface Trace {
  session_id: string;
  interaction_id: string;
  nodes: TraceNode[];
  total_latency_ms: number;
  total_tokens: number;
}

interface InteractionSimple {
  id: string;
  timestamp?: string;
  [key: string]: unknown;
}

interface InteractionsResponse {
  interactions?: InteractionSimple[];
}

const LEVEL_CONFIG = {
  N1: {
    name: 'Raw Data',
    icon: '📥',
    color: '#3b82f6',
    description: 'Datos crudos del usuario (input original)'
  },
  N2: {
    name: 'Preprocessed',
    icon: '🔧',
    color: '#10b981',
    description: 'Datos preprocesados (validación, limpieza, tokenización)'
  },
  N3: {
    name: 'LLM Processing',
    icon: '🤖',
    color: '#8b5cf6',
    description: 'Procesamiento por el modelo LLM (inferencia)'
  },
  N4: {
    name: 'Postprocessed',
    icon: '📤',
    color: '#f59e0b',
    description: 'Datos postprocesados (formateo, enriquecimiento, output final)'
  }
};

// FIX DEFECTO 5.3 Cortez14: Add created_at to match backend SessionResponse
interface SessionSummary {
  id: string;
  activity_id: string;
  student_id: string;
  mode?: SessionMode;
  status?: string;
  created_at?: string;  // FIX DEFECTO 5.3
  updated_at?: string;
}

// FIX Cortez16: Changed from Interaction to InteractionSimple to match API response
// user_input is optional since API may return different field names
interface InteractionItem {
  id: string;
  user_input?: string;
  prompt?: string;  // Alternative field name from backend
  timestamp?: string;
}

export const TraceabilityViewer: React.FC = () => {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  // FIX Cortez16: Use InteractionItem type instead of Interaction
  const [interactions, setInteractions] = useState<InteractionItem[]>([]);
  const [selectedInteraction, setSelectedInteraction] = useState<string | null>(null);
  const [trace, setTrace] = useState<Trace | null>(null);
  const [loading, setLoading] = useState(false);
  const { showToast } = useToast();

  // FIX Cortez20: Add cleanup to prevent memory leak on unmount
  useEffect(() => {
    let isMounted = true;

    const loadSessions = async () => {
      try {
        const data = await sessionService.listAll();
        if (isMounted) {
          setSessions(data as SessionSummary[]);
        }
      } catch (error: unknown) {
        if (isMounted) {
          const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
          showToast(`Error cargando sesiones: ${errorMessage}`, 'error');
        }
      }
    };

    loadSessions();

    return () => {
      isMounted = false;
    };
  }, [showToast]);

  const loadInteractions = async (sessionId: string) => {
    setSelectedSession(sessionId);
    setSelectedInteraction(null);
    setTrace(null);

    try {
      const response = await httpClient.get<InteractionsResponse>(`/sessions/${sessionId}/interactions`);
      setInteractions(response.interactions || []);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      showToast(`Error cargando interacciones: ${errorMessage}`, 'error');
      setInteractions([]);
    }
  };

  const loadTrace = async (interactionId: string) => {
    setLoading(true);
    setSelectedInteraction(interactionId);

    try {
      const response = await httpClient.get<Trace>(`/traceability/${interactionId}`);
      setTrace(response);
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Error desconocido';
      showToast(`Error cargando traza: ${errorMessage}`, 'error');
      setTrace(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="traceability-viewer">
      <div className="viewer-header">
        <div>
          <h1>🔍 Trazabilidad N4</h1>
          <p>Visualización del procesamiento cognitivo en 4 niveles</p>
        </div>
      </div>

      <div className="viewer-content">
        <aside className="sessions-sidebar">
          <h3>Sesiones</h3>
          {sessions.length === 0 ? (
            <div className="empty-state">
              <p>📭 No hay sesiones</p>
            </div>
          ) : (
            <ul className="sessions-list">
              {sessions.map((session) => (
                <li
                  key={session.id}
                  className={`session-item ${selectedSession === session.id ? 'active' : ''}`}
                  onClick={() => loadInteractions(session.id)}
                >
                  <div className="session-title">
                    <strong>{session.activity_id}</strong>
                  </div>
                  <div className="session-meta">
                    <span>👤 {session.student_id}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <aside className="interactions-sidebar">
          <h3>Interacciones</h3>
          {interactions.length === 0 ? (
            <div className="empty-state">
              <p>👈 Selecciona sesión</p>
            </div>
          ) : (
            <ul className="interactions-list">
              {interactions.map((interaction, idx) => (
                <li
                  key={interaction.id}
                  className={`interaction-item ${selectedInteraction === interaction.id ? 'active' : ''}`}
                  onClick={() => loadTrace(interaction.id)}
                >
                  <div className="interaction-index">#{idx + 1}</div>
                  {/* FIX Cortez16: Handle both user_input and prompt fields */}
                  <div className="interaction-preview">
                    {(interaction.user_input || interaction.prompt || '').substring(0, 50)}...
                  </div>
                </li>
              ))}
            </ul>
          )}
        </aside>

        <main className="trace-panel">
          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Cargando traza N4...</p>
            </div>
          )}

          {!loading && !trace && (
            <div className="empty-state-large">
              <div className="empty-icon">🔍</div>
              <p>👈 Selecciona una interacción para ver su traza</p>
              <small>La traza muestra el recorrido de los datos en 4 niveles</small>
            </div>
          )}

          {!loading && trace && (
            <div className="trace-results">
              {/* Metrics Summary */}
              <div className="metrics-summary">
                <div className="metric">
                  <div className="metric-icon">⏱️</div>
                  <div>
                    <div className="metric-label">Latencia Total</div>
                    <div className="metric-value">{trace.total_latency_ms}ms</div>
                  </div>
                </div>
                <div className="metric">
                  <div className="metric-icon">🎯</div>
                  <div>
                    <div className="metric-label">Tokens Totales</div>
                    <div className="metric-value">{trace.total_tokens}</div>
                  </div>
                </div>
                <div className="metric">
                  <div className="metric-icon">📊</div>
                  <div>
                    <div className="metric-label">Nodos Procesados</div>
                    <div className="metric-value">{trace.nodes.length}</div>
                  </div>
                </div>
              </div>

              {/* Flowchart */}
              <div className="flowchart-section">
                <h2>🌊 Flujo de Procesamiento</h2>
                <div className="flowchart">
                  {trace.nodes.map((node, idx) => (
                    <React.Fragment key={node.id}>
                      <TraceNodeCard node={node} />
                      {idx < trace.nodes.length - 1 && (
                        <div className="flow-arrow">
                          <div className="arrow-line"></div>
                          <div className="arrow-head">▼</div>
                        </div>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              {/* Timeline */}
              <div className="timeline-section">
                <h2>⏱️ Timeline de Eventos</h2>
                <div className="timeline">
                  {trace.nodes.map((node) => {
                    const config = LEVEL_CONFIG[node.level];
                    return (
                      <div key={node.id} className="timeline-event">
                        <div className="timeline-marker" style={{ borderColor: config.color }}>
                          <div
                            className="timeline-dot"
                            style={{ backgroundColor: config.color }}
                          ></div>
                        </div>
                        <div className="timeline-content">
                          <div className="timeline-header">
                            <span className="timeline-level" style={{ color: config.color }}>
                              {config.icon} {node.level}
                            </span>
                            <span className="timeline-time">
                              {new Date(node.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <div className="timeline-details">
                            {node.metadata.processing_time_ms && (
                              <span>⏱️ {node.metadata.processing_time_ms}ms</span>
                            )}
                            {node.metadata.tokens_used && (
                              <span>🎯 {node.metadata.tokens_used} tokens</span>
                            )}
                            {node.metadata.model && <span>🤖 {node.metadata.model}</span>}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

const TraceNodeCard: React.FC<{ node: TraceNode }> = ({ node }) => {
  const config = LEVEL_CONFIG[node.level];
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="trace-node" style={{ borderColor: config.color }}>
      <div className="node-header" onClick={() => setExpanded(!expanded)}>
        <div className="node-level" style={{ backgroundColor: config.color }}>
          <span className="node-icon">{config.icon}</span>
          <span className="node-label">{node.level}</span>
        </div>
        <div className="node-info">
          <div className="node-name">{config.name}</div>
          <div className="node-desc">{config.description}</div>
        </div>
        <button className="expand-btn">{expanded ? '▲' : '▼'}</button>
      </div>

      {expanded && (
        <div className="node-details">
          <div className="detail-section">
            <strong>⏱️ Timestamp:</strong>
            <div>{new Date(node.timestamp).toLocaleString()}</div>
          </div>

          {node.metadata.processing_time_ms && (
            <div className="detail-section">
              <strong>⚡ Processing Time:</strong>
              <div>{node.metadata.processing_time_ms}ms</div>
            </div>
          )}

          {node.metadata.tokens_used && (
            <div className="detail-section">
              <strong>🎯 Tokens:</strong>
              <div>{node.metadata.tokens_used}</div>
            </div>
          )}

          {node.metadata.model && (
            <div className="detail-section">
              <strong>🤖 Model:</strong>
              <div>{node.metadata.model}</div>
            </div>
          )}

          {node.metadata.transformations && node.metadata.transformations.length > 0 && (
            <div className="detail-section">
              <strong>🔄 Transformations:</strong>
              <ul className="transformations-list">
                {node.metadata.transformations.map((t, idx) => (
                  <li key={idx}>{t}</li>
                ))}
              </ul>
            </div>
          )}

          <div className="detail-section">
            <strong>📦 Data:</strong>
            <pre className="data-preview">{JSON.stringify(node.data, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};
