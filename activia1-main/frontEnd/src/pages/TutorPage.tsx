import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../shared/components/Toast/Toast';
import { sessionsService, interactionsService, tracesService, risksService } from '../services/api';
import { ChatMessage, Session, TraceabilityN4, RiskAnalysis5D, SessionMode } from '../types';
import ReactMarkdown from 'react-markdown';
import CreateSessionModal from '../components/CreateSessionModal';
import TraceabilityViewer from '../components/TraceabilityViewer';
import RiskAnalysisViewer from '../components/RiskAnalysisViewer';
import RiskMonitorPanel from '../components/RiskMonitorPanel';
// FIX Cortez24 DEFECTO 4.x: Remove unused imports (RefreshCw, MessageSquare, BarChart3)
import {
  Send,
  Loader2,
  Brain,
  Sparkles,
  AlertCircle,
  Info,
  Plus,
  Clock,
  GitBranch,
  Shield,
  ChevronRight,
  ChevronLeft
} from 'lucide-react';

export default function TutorPage() {
  const { user } = useAuth();
  const { showToast } = useToast();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [session, setSession] = useState<Session | null>(null);
  const [isCreatingSession, setIsCreatingSession] = useState(false);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTraceability, setShowTraceability] = useState(false);
  const [showRiskAnalysis, setShowRiskAnalysis] = useState(false);
  const [traceabilityData, setTraceabilityData] = useState<TraceabilityN4 | null>(null);
  const [riskAnalysisData, setRiskAnalysisData] = useState<RiskAnalysis5D | null>(null);
  const [lastTraceId, setLastTraceId] = useState<string | null>(null);
  const [isLoadingTraceability, setIsLoadingTraceability] = useState(false);
  const [isLoadingRisks, setIsLoadingRisks] = useState(false);
  const [showRiskPanel, setShowRiskPanel] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-refresh risk analysis when messages change
  useEffect(() => {
    if (session && messages.length > 1 && showRiskPanel) {
      // Debounce: only update after 2 seconds of no new messages
      const timer = setTimeout(() => {
        handleAnalyzeRisks(true); // Silent update
      }, 2000);

      return () => clearTimeout(timer);
    }
  }, [messages.length, session?.id, showRiskPanel]);

  // FIX Cortez22 DEFECTO 4.2: Added isMounted check to prevent memory leaks
  useEffect(() => {
    let isMounted = true;

    const initializeSession = async () => {
      if (session) return;

      setIsCreatingSession(true);
      try {
        // FIX Cortez16: Use SessionMode enum instead of string literal
        const newSession = await sessionsService.create({
          student_id: user?.id || 'guest',
          activity_id: 'general_learning',
          mode: SessionMode.TUTOR
        });

        if (!isMounted) return;

        setSession(newSession);

        // Welcome message
        setMessages([{
          id: 'welcome',
          role: 'assistant',
          content: `¡Hola ${user?.full_name || user?.username || 'estudiante'}! 👋

Soy tu tutor de IA, diseñado para ayudarte a aprender programación de manera efectiva.

**¿Cómo funciono?**
- Te guío con preguntas para que descubras las soluciones por ti mismo
- No te doy respuestas directas, sino pistas y orientación
- Analizo tu proceso de pensamiento para ayudarte mejor

**¿Qué puedo hacer por ti hoy?**
- Explicar conceptos de programación
- Ayudarte con ejercicios
- Revisar tu código
- Resolver dudas técnicas

¿En qué te puedo ayudar?`,
          timestamp: new Date()
        }]);
      } catch (error) {
        if (!isMounted) return;

        if (import.meta.env.DEV) {
          console.error('Error creating session:', error);
        }
        showToast('Error al crear la sesión. Intenta de nuevo.', 'error');
      } finally {
        if (isMounted) {
          setIsCreatingSession(false);
        }
      }
    };

    initializeSession();

    return () => {
      isMounted = false;
    };
  }, [session, user, showToast]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !session) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Construir contexto de conversación (últimos 10 mensajes)
      const conversationHistory = messages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const interactionResult = await interactionsService.process({
        session_id: session.id,
        prompt: userMessage.content,
        context: {
          conversation_history: conversationHistory,
          message_count: messages.length
        }
      });

      // Store trace_id for traceability analysis
      if (interactionResult.trace_id) {
        setLastTraceId(interactionResult.trace_id);
      }

      // FIX DEFECTO 5.2 Cortez14: Use correct field names from InteractionResponse
      const aiMessage: ChatMessage = {
        id: interactionResult.interaction_id,
        role: 'assistant',
        content: interactionResult.response,
        timestamp: new Date(),
        metadata: {
          agent_used: interactionResult.agent_used,
          cognitive_state: interactionResult.cognitive_state_detected,  // FIX: correct field name
          ai_involvement: interactionResult.ai_involvement,
          blocked: interactionResult.blocked,
          block_reason: interactionResult.block_reason ?? undefined,
          risks_detected: interactionResult.risks_detected
        }
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error: unknown) {
      const err = error as { error?: { message?: string }; message?: string };
      const errorMessage: ChatMessage = {
        id: 'error-' + Date.now(),
        role: 'assistant',
        content: `Lo siento, ocurrió un error al procesar tu mensaje. Por favor, intenta de nuevo.

*Error: ${err.error?.message || err.message || 'Error desconocido'}*`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // FIX Cortez22 DEFECTO 4.2: Reset session to trigger useEffect reinitialization
  const handleNewSession = (_sessionId: string) => {
    // Reset session to trigger useEffect which will create a new session
    setSession(null);
    setMessages([]);
    setLastTraceId(null);
    setShowCreateModal(false);
  };

  const handleAnalyzeTraceability = async () => {
    if (!lastTraceId) {
      showToast('No hay trace_id disponible. Envía un mensaje primero.', 'warning');
      return;
    }

    setIsLoadingTraceability(true);
    try {
      const data = await tracesService.getN4(lastTraceId);
      setTraceabilityData(data);
      setShowTraceability(true);
    } catch (error: unknown) {
      if (import.meta.env.DEV) {
        console.error('Error fetching traceability:', error);
      }
      const err = error as { error?: { message?: string }; message?: string };
      const errorMsg = err.error?.message || err.message || 'Error desconocido';
      showToast(`Error al obtener trazabilidad: ${errorMsg}`, 'error');
    } finally {
      setIsLoadingTraceability(false);
    }
  };

  const handleAnalyzeRisks = async (silent: boolean = false) => {
    if (!session) {
      if (!silent) {
        showToast('No hay sesión activa. Inicia una conversación primero.', 'warning');
      }
      return;
    }

    setIsLoadingRisks(true);
    try {
      const data = await risksService.analyze5D(session.id);
      // FIX Cortez16: Cast response to RiskAnalysis5D type
      setRiskAnalysisData({
        session_id: data.session_id,
        overall_score: data.overall_score,
        risk_level: data.risk_level as RiskAnalysis5D['risk_level'],
        dimensions: data.dimensions as RiskAnalysis5D['dimensions'],
        top_risks: data.top_risks as RiskAnalysis5D['top_risks'],
        recommendations: data.recommendations
      });
      if (!silent) {
        setShowRiskAnalysis(true);
      }
    } catch (error: unknown) {
      if (!silent) {
        if (import.meta.env.DEV) {
          console.error('Error analyzing risks:', error);
        }
        const err = error as { error?: { message?: string }; message?: string; code?: string };
        const errorMsg = err.error?.message || err.message || 'Error desconocido';

        if (err.code === 'ECONNABORTED') {
          showToast('El análisis está tomando demasiado tiempo. Verifica que Ollama esté corriendo.', 'error', 8000);
        } else if (err.message === 'Network Error') {
          showToast('Error de conexión. Verifica que el backend y Ollama estén activos.', 'error', 8000);
        } else {
          showToast(`Error al analizar riesgos: ${errorMsg}`, 'error');
        }
      }
    } finally {
      setIsLoadingRisks(false);
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-4 animate-fadeIn">
      {/* Modals */}
      <CreateSessionModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSessionCreated={handleNewSession}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[var(--text-primary)]">Tutor IA</h1>
              <p className="text-sm text-[var(--text-secondary)]">
                Aprende con guía cognitiva personalizada
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={handleAnalyzeTraceability}
              disabled={!lastTraceId || isLoadingTraceability}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--accent-primary)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              title="Ver trazabilidad N4 de la última interacción"
            >
              {isLoadingTraceability ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <GitBranch className="w-4 h-4" />
              )}
              <span className="hidden sm:inline">
                {isLoadingTraceability ? 'Cargando...' : 'Trazabilidad'}
              </span>
            </button>
            <button
              onClick={() => handleAnalyzeRisks(false)}
              disabled={!session || isLoadingRisks}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--accent-primary)] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              title="Ver análisis detallado de riesgos 5D"
            >
              {isLoadingRisks ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Shield className="w-4 h-4" />
              )}
              <span className="hidden sm:inline">
                {isLoadingRisks ? 'Analizando...' : 'Ver Reporte'}
              </span>
            </button>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--accent-primary)] transition-all"
            >
              <Plus className="w-4 h-4" />
              <span className="hidden sm:inline">Nueva Sesión</span>
            </button>
            <button
              onClick={() => setShowRiskPanel(!showRiskPanel)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--accent-primary)] transition-all"
              title={showRiskPanel ? 'Ocultar panel de riesgos' : 'Mostrar panel de riesgos'}
            >
              {showRiskPanel ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
            </button>
          </div>
        </div>

      {/* Traceability Modal */}
      {showTraceability && traceabilityData && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" style={{ zIndex: 9999 }}>
          <div className="bg-[var(--bg-primary)] rounded-2xl border border-gray-700 max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl">
            <TraceabilityViewer data={traceabilityData} />
            <button
              onClick={() => setShowTraceability(false)}
              className="mt-6 w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-medium hover:shadow-lg hover:scale-105 transition-all"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      {/* Risk Analysis Modal */}
      {showRiskAnalysis && riskAnalysisData && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4" style={{ zIndex: 9999 }}>
          <div className="bg-[var(--bg-primary)] rounded-2xl border border-gray-700 max-w-4xl w-full max-h-[90vh] overflow-y-auto p-6 shadow-2xl">
            <RiskAnalysisViewer data={riskAnalysisData} />
            <button
              onClick={() => setShowRiskAnalysis(false)}
              className="mt-6 w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg font-medium hover:shadow-lg hover:scale-105 transition-all"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      {/* Chat Container */}
      <div className="flex-1 bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] flex flex-col overflow-hidden">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 chat-scroll">
          {isCreatingSession ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader2 className="w-8 h-8 text-[var(--accent-primary)] animate-spin mx-auto mb-4" />
                <p className="text-[var(--text-secondary)]">Iniciando sesión...</p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] ${
                      message.role === 'user'
                        ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-2xl rounded-br-md'
                        : 'bg-[var(--bg-tertiary)] text-[var(--text-primary)] rounded-2xl rounded-bl-md'
                    } px-5 py-4 animate-slideIn`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[var(--border-color)]">
                        <Sparkles className="w-4 h-4 text-[var(--accent-primary)]" />
                        <span className="text-sm font-medium text-[var(--accent-primary)]">Tutor IA</span>
                        {/* FIX DEFECTO 5.2 Cortez14: Use correct field name cognitive_state */}
                        {message.metadata?.cognitive_state && (
                          <span className="ml-auto text-xs px-2 py-0.5 rounded-full bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]">
                            {message.metadata.cognitive_state}
                          </span>
                        )}
                      </div>
                    )}
                    
                    <div className={`markdown-content ${message.role === 'user' ? 'text-white' : ''}`}>
                      <ReactMarkdown>{message.content}</ReactMarkdown>
                    </div>

                    {/* FIX DEFECTO 5.2 Cortez14: Use correct field name risks_detected */}
                    {message.metadata?.risks_detected && message.metadata.risks_detected.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-[var(--border-color)]">
                        <div className="flex items-center gap-2 text-xs text-[var(--warning)]">
                          <AlertCircle className="w-3 h-3" />
                          <span>Riesgos detectados: {message.metadata.risks_detected.length}</span>
                        </div>
                      </div>
                    )}

                    {/* FIX Cortez16: Removed processingTime - not in ChatMessage.metadata */}
                    <div className={`mt-2 text-xs ${message.role === 'user' ? 'text-white/60' : 'text-[var(--text-muted)]'}`}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-[var(--bg-tertiary)] rounded-2xl rounded-bl-md px-5 py-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles className="w-4 h-4 text-[var(--accent-primary)]" />
                      <span className="text-sm font-medium text-[var(--accent-primary)]">Tutor IA</span>
                    </div>
                    <div className="typing-indicator">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-[var(--border-color)] bg-[var(--bg-secondary)]">
          <form onSubmit={handleSubmit} className="flex items-end gap-4">
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Escribe tu pregunta o comparte tu código..."
                rows={1}
                className="w-full px-4 py-3 pr-12 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-[var(--accent-primary)] focus:outline-none resize-none transition-all"
                style={{ minHeight: '48px', maxHeight: '200px' }}
                disabled={!session || isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={!input.trim() || isLoading || !session}
              className="h-12 w-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 text-white flex items-center justify-center hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </form>

          {/* Quick Tips */}
          <div className="flex items-center gap-4 mt-3 text-xs text-[var(--text-muted)]">
            <div className="flex items-center gap-1">
              <Info className="w-3 h-3" />
              <span>Enter para enviar, Shift+Enter para nueva línea</span>
            </div>
            {session && (
              <div className="flex items-center gap-1 ml-auto">
                <Clock className="w-3 h-3" />
                <span>Sesión: {session.id.slice(0, 8)}...</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Suggested Questions */}
      {messages.length <= 1 && (
        <div className="mt-4">
          <p className="text-sm text-[var(--text-muted)] mb-3">Preguntas sugeridas:</p>
          <div className="flex flex-wrap gap-2">
            {[
              '¿Cómo implemento una cola circular?',
              'Explícame el patrón Observer',
              '¿Cuál es la diferencia entre stack y heap?',
              'Ayúdame con recursión'
            ].map((question, i) => (
              <button
                key={i}
                onClick={() => setInput(question)}
                className="px-4 py-2 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-[var(--accent-primary)] transition-all"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}
      </div>

      {/* Risk Monitor Panel */}
      {showRiskPanel && (
        <div className="w-80 flex-shrink-0">
          <RiskMonitorPanel
            currentRiskLevel={riskAnalysisData?.risk_level || 'info'}
            dimensions={riskAnalysisData?.dimensions}
          />
        </div>
      )}
    </div>
  );
}
