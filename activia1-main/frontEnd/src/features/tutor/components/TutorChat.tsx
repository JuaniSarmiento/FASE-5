/**
 * Chat del Tutor Cognitivo - Componente minimalista
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { sessionService } from '@/core/services/SessionService';
import { interactionService } from '@/core/services/InteractionService';
import { SessionMode } from '@/types/api.types';
import { AGENT_PROMPTS } from '@/core/config/ollama.config';
import './TutorChat.css';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    cognitive_state?: string;
    ai_involvement?: number;
    blocked?: boolean;
    tokens_used?: number;
  };
}

type TutorMode = 'socratico' | 'explicativo' | 'guiado';

export const TutorChat: React.FC = () => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<TutorMode>('socratico');
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  useEffect(() => {
    initSession();
    return () => {
      // Cleanup: abort pending requests
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // FIX 7.1: Add proper dependency array (Cortez2 audit)
  useEffect(() => {
    // Update session config when mode changes
    if (sessionId) {
      updateSessionMode();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, sessionId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const initSession = async () => {
    try {
      const session = await sessionService.create({
        student_id: `student_${Date.now()}`,
        activity_id: 'tutor_session',
        mode: SessionMode.TUTOR
      });

      setSessionId(session.id);

      // Welcome message
      addSystemMessage(`¡Hola! Soy tu **Tutor Cognitivo** (T-IA-Cog).

Mi objetivo es ayudarte a **aprender a pensar**, no darte respuestas directas.

**Modo actual:** Socrático
**Principios:**
- ✅ Guío tu razonamiento con preguntas
- ✅ Promuevo la reflexión metacognitiva
- ❌ No doy soluciones completas
- ❌ No sustituyo tu agencia cognitiva

¿En qué necesitas ayuda hoy?`);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
      setError(`Error al inicializar sesión: ${errorMessage}`);
    }
  };

  const updateSessionMode = async () => {
    // En producción, llamaría a un endpoint PATCH para actualizar la sesión
    if (import.meta.env.DEV) {
      console.log(`[Tutor] Mode changed to: ${mode}`);
    }
  };

  const addSystemMessage = (content: string) => {
    const msg: Message = {
      id: `sys_${Date.now()}`,
      role: 'system',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, msg]);
  };

  const handleSend = useCallback(async () => {
    if (!input.trim() || !sessionId || loading) return;

    // Validation
    if (input.trim().length < 10) {
      addSystemMessage('⚠️ Por favor, describe tu duda con más detalle (mínimo 10 caracteres).');
      return;
    }

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    // Abort controller for cancellation
    abortControllerRef.current = new AbortController();

    try {
      const response = await interactionService.create({
        session_id: sessionId,
        prompt: input,  // FIXED: Changed from student_input to prompt (backend field name)
        context: {
          tutor_mode: mode,
          cognitive_intent: 'learning',
          system_prompt: AGENT_PROMPTS.TUTOR
        }
      });

      const assistantMessage: Message = {
        id: response.id || response.interaction_id,
        role: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp),
        metadata: {
          cognitive_state: response.cognitive_state_detected,
          ai_involvement: response.ai_involvement,
          blocked: response.blocked,
          tokens_used: response.tokens_used
        }
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Alert if blocked
      if (response.blocked) {
        addSystemMessage('🚫 Esta interacción fue bloqueada porque detecté un intento de delegación completa. Intenta reformular tu pregunta de forma más específica.');
      }

    } catch (err: unknown) {
      console.error('Error sending message:', err);
      const isAbortError = err instanceof Error && err.name === 'AbortError';
      if (!isAbortError) {
        const errorMessage = err instanceof Error ? err.message : 'Error desconocido';
        setError(`Error: ${errorMessage}`);
        addSystemMessage('❌ Error al procesar tu mensaje. Por favor, intenta nuevamente.');
      }
    } finally {
      setLoading(false);
      inputRef.current?.focus();
      abortControllerRef.current = null;
    }
  }, [input, sessionId, mode, loading]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getModeDescription = (m: TutorMode): string => {
    switch (m) {
      case 'socratico':
        return 'Preguntas guía (no respuestas directas)';
      case 'explicativo':
        return 'Explicación de conceptos fundamentales';
      case 'guiado':
        return 'Pasos incrementales con validación';
      default:
        return '';
    }
  };

  return (
    <div className="tutor-chat">
      <div className="tutor-header">
        <div className="header-title">
          <h2>🎓 Tutor Cognitivo</h2>
          <span className="session-id">Sesión: {sessionId?.slice(0, 8) || 'Cargando...'}</span>
        </div>
        <div className="header-controls">
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as TutorMode)}
            className="mode-selector"
            disabled={loading}
          >
            <option value="socratico">🤔 Socrático</option>
            <option value="explicativo">📚 Explicativo</option>
            <option value="guiado">🧭 Guiado</option>
          </select>
          <span className="mode-description">{getModeDescription(mode)}</span>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span>❌ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <div className="messages-container">
        {messages.map((msg) => (
          <div key={msg.id} className={`message message-${msg.role}`}>
            <div className="message-content">
              {msg.content.split('\n').map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>

            {msg.metadata && (
              <div className="message-metadata">
                {msg.metadata.cognitive_state && (
                  <span className="badge badge-state">
                    🧠 {msg.metadata.cognitive_state}
                  </span>
                )}
                {msg.metadata.ai_involvement !== undefined && (
                  <span
                    className={`badge ${
                      msg.metadata.ai_involvement > 0.7
                        ? 'badge-warning'
                        : 'badge-info'
                    }`}
                  >
                    IA: {(msg.metadata.ai_involvement * 100).toFixed(0)}%
                  </span>
                )}
                {msg.metadata.blocked && (
                  <span className="badge badge-danger">🚫 Bloqueado</span>
                )}
                {msg.metadata.tokens_used && (
                  <span className="badge badge-tokens">
                    {msg.metadata.tokens_used} tokens
                  </span>
                )}
              </div>
            )}

            <div className="message-timestamp">
              {msg.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message message-assistant">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <textarea
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe tu duda o problema con detalle... (mín. 10 caracteres)"
          rows={3}
          disabled={loading || !sessionId}
          maxLength={2000}
        />
        <div className="input-footer">
          <span className="char-counter">
            {input.length}/2000
          </span>
          <button
            onClick={handleSend}
            disabled={loading || !input.trim() || !sessionId}
            className="btn-send"
          >
            {loading ? '⏳ Pensando...' : '📤 Enviar'}
          </button>
        </div>
      </div>
    </div>
  );
};
