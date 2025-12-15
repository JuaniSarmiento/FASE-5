import React, { useState, useEffect, useRef } from 'react';
import { simulatorsService, sessionsService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { Simulator, SimulatorType, Session, ChatMessage, SessionMode } from '../types';
import ReactMarkdown from 'react-markdown';
import {
  Users,
  UserCheck,
  Briefcase,
  AlertTriangle,
  HeadphonesIcon,
  Shield,
  Send,
  Loader2,
  ArrowRight,
  X
} from 'lucide-react';

// IMPORTANT: Use lowercase values to match backend enum values
const simulatorIcons: Record<string, React.ElementType> = {
  product_owner: Briefcase,
  scrum_master: UserCheck,
  tech_interviewer: Users,
  incident_responder: AlertTriangle,
  client: HeadphonesIcon,
  devsecops: Shield
};

const simulatorColors: Record<string, string> = {
  product_owner: 'from-blue-500 to-cyan-600',
  scrum_master: 'from-green-500 to-emerald-600',
  tech_interviewer: 'from-purple-500 to-pink-600',
  incident_responder: 'from-red-500 to-orange-600',
  client: 'from-yellow-500 to-orange-600',
  devsecops: 'from-indigo-500 to-purple-600'
};

export default function SimulatorsPage() {
  const { user } = useAuth();
  const [simulators, setSimulators] = useState<Simulator[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedSimulator, setSelectedSimulator] = useState<Simulator | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const abortController = new AbortController();

    const fetchSimulators = async () => {
      try {
        // FIX Cortez16: Use getAllSimulators() instead of list()
        const simulatorsList = await simulatorsService.getAllSimulators();

        // Only update state if component is still mounted
        if (!abortController.signal.aborted) {
          setSimulators(simulatorsList || []);
        }
      } catch (error) {
        // Don't log errors if the request was aborted
        if (!abortController.signal.aborted) {
          console.error('Error fetching simulators:', error);
          // Mock data - using lowercase values to match backend
          setSimulators([
            {
              type: 'product_owner' as SimulatorType,
              name: 'Product Owner (PO-IA)',
              description: 'Simula un Product Owner que revisa requisitos, prioriza backlog y cuestiona decisiones técnicas',
              competencies: ['comunicacion_tecnica', 'analisis_requisitos', 'priorizacion'],
              status: 'active'
            },
            {
              type: 'scrum_master' as SimulatorType,
              name: 'Scrum Master (SM-IA)',
              description: 'Simula un Scrum Master que facilita daily standups y gestiona impedimentos',
              competencies: ['gestion_tiempo', 'comunicacion', 'identificacion_impedimentos'],
              status: 'active'
            },
            {
              type: 'tech_interviewer' as SimulatorType,
              name: 'Technical Interviewer (IT-IA)',
              description: 'Simula un entrevistador técnico que evalúa conocimientos conceptuales y algorítmicos',
              competencies: ['dominio_conceptual', 'analisis_algoritmico', 'comunicacion_tecnica'],
              status: 'active'
            },
            {
              type: 'incident_responder' as SimulatorType,
              name: 'Incident Responder (IR-IA)',
              description: 'Simula un ingeniero DevOps que gestiona incidentes en producción',
              competencies: ['diagnostico_sistematico', 'priorizacion', 'documentacion'],
              status: 'development'
            },
            {
              type: 'client' as SimulatorType,
              name: 'Client (CX-IA)',
              description: 'Simula un cliente con requisitos ambiguos que requiere elicitación y negociación',
              competencies: ['elicitacion_requisitos', 'negociacion', 'empatia'],
              status: 'development'
            },
            {
              type: 'devsecops' as SimulatorType,
              name: 'DevSecOps (DSO-IA)',
              description: 'Simula un analista de seguridad que audita código y detecta vulnerabilidades',
              competencies: ['seguridad', 'analisis_vulnerabilidades', 'gestion_riesgo'],
              status: 'active'
            }
          ]);
        }
      } finally {
        if (!abortController.signal.aborted) {
          setIsLoading(false);
        }
      }
    };

    fetchSimulators();

    // Cleanup: abort pending requests when component unmounts
    return () => {
      abortController.abort();
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startSimulation = async (simulator: Simulator) => {
    setSelectedSimulator(simulator);
    setMessages([]);

    try {
      // FIX Cortez16: Use SessionMode enum instead of string literal
      const newSession = await sessionsService.create({
        student_id: user?.id || 'guest',
        activity_id: `simulator_${simulator.type.toLowerCase()}`,
        mode: SessionMode.SIMULATOR,
        simulator_type: simulator.type
      });
      setSession(newSession);

      // Welcome message from simulator - using lowercase keys to match backend
      const welcomeMessages: Record<string, string> = {
        product_owner: `¡Hola! Soy el Product Owner de tu equipo.

Estoy aquí para ayudarte a entender mejor los requisitos del negocio y cómo priorizar el trabajo.

**¿Cómo puedo ayudarte hoy?**
- Revisar historias de usuario
- Priorizar el backlog
- Discutir decisiones técnicas desde perspectiva de negocio
- Clarificar requisitos

¿Qué necesitas?`,
        scrum_master: `¡Buenos días! Soy el Scrum Master del equipo.

Mi rol es facilitar y eliminar impedimentos para que el equipo pueda entregar valor.

**Podemos trabajar en:**
- Simular una daily standup
- Identificar y resolver impedimentos
- Mejorar procesos del equipo
- Preparar retrospectivas

¿Cómo te fue ayer? ¿En qué estás trabajando hoy?`,
        tech_interviewer: `Hola, gracias por venir a esta entrevista técnica.

Vamos a evaluar tus conocimientos en programación y resolución de problemas.

**Áreas que cubriremos:**
- Estructuras de datos
- Algoritmos
- Diseño de sistemas
- Buenas prácticas

¿Estás listo para comenzar? Cuéntame un poco sobre tu experiencia.`,
        incident_responder: `🚨 **ALERTA: Incidente en Producción**

Soy el Incident Responder de turno. Tenemos un problema crítico que necesita atención inmediata.

**Situación actual:**
- Los usuarios reportan timeouts en la API
- El sistema de monitoreo muestra alta latencia
- El equipo de soporte está recibiendo múltiples tickets

¿Por dónde empezamos a diagnosticar?`,
        client: `Hola, soy el cliente de tu proyecto.

Necesito un sistema nuevo pero... no estoy seguro exactamente de lo que quiero.

Solo sé que el sistema actual no funciona bien y necesitamos algo mejor.

¿Me puedes ayudar a definir qué necesitamos?`,
        devsecops: `Hola, soy el analista de seguridad del equipo.

Necesito revisar el código del último sprint antes de que pase a producción.

**Áreas de revisión:**
- Vulnerabilidades de seguridad
- Manejo de datos sensibles
- Autenticación y autorización
- Dependencias inseguras

¿Tienes código listo para revisar?`
      };

      setMessages([{
        id: 'welcome',
        role: 'assistant',
        content: welcomeMessages[simulator.type] || '¡Hola! Estoy listo para comenzar la simulación.',
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || isSending || !session || !selectedSimulator) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsSending(true);

    try {
      // Construir contexto de conversación (últimos 10 mensajes)
      const conversationHistory = messages.slice(-10).map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      // FIX Cortez16: interact() takes (sessionId, interaction) - two arguments
      const result = await simulatorsService.interact(session.id, {
        simulator_type: selectedSimulator.type,
        prompt: userMessage.content,
        context: {
          conversation_history: conversationHistory,
          message_count: messages.length
        }
      });

      // FIX Cortez16: Use snake_case cognitive_state
      const aiMessage: ChatMessage = {
        id: Date.now().toString() + '-ai',
        role: 'assistant',
        content: result.response,
        timestamp: new Date(),
        metadata: {
          cognitive_state: 'simulator'
        }
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        id: 'error',
        role: 'assistant',
        content: 'Lo siento, ocurrió un error. Por favor, intenta de nuevo.',
        timestamp: new Date()
      }]);
    } finally {
      setIsSending(false);
    }
  };

  const closeSimulation = () => {
    setSelectedSimulator(null);
    setSession(null);
    setMessages([]);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 text-[var(--accent-primary)] animate-spin" />
      </div>
    );
  }

  // Simulation Chat View
  if (selectedSimulator && session) {
    const Icon = simulatorIcons[selectedSimulator.type] || Users;
    const colorClass = simulatorColors[selectedSimulator.type];

    return (
      <div className="h-[calc(100vh-8rem)] flex flex-col animate-fadeIn">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorClass} flex items-center justify-center`}>
              <Icon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-[var(--text-primary)]">{selectedSimulator.name}</h1>
              <p className="text-sm text-[var(--text-secondary)]">Simulación activa</p>
            </div>
          </div>
          <button
            onClick={closeSimulation}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:border-red-500 transition-all"
          >
            <X className="w-4 h-4" />
            Terminar
          </button>
        </div>

        {/* Chat Area */}
        <div className="flex-1 bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-6 space-y-4 chat-scroll">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] px-5 py-4 animate-slideIn ${
                    message.role === 'user'
                      ? `bg-gradient-to-br ${colorClass} text-white rounded-2xl rounded-br-md`
                      : 'bg-[var(--bg-tertiary)] text-[var(--text-primary)] rounded-2xl rounded-bl-md'
                  }`}
                >
                  {message.role === 'assistant' && (
                    <div className="flex items-center gap-2 mb-3 pb-2 border-b border-[var(--border-color)]">
                      <Icon className="w-4 h-4 text-[var(--accent-primary)]" />
                      <span className="text-sm font-medium text-[var(--accent-primary)]">
                        {selectedSimulator.name.split(' ')[0]}
                      </span>
                    </div>
                  )}
                  <div className="markdown-content">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                  <p className={`text-xs mt-2 ${message.role === 'user' ? 'text-white/60' : 'text-[var(--text-muted)]'}`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </div>
            ))}

            {isSending && (
              <div className="flex justify-start">
                <div className="bg-[var(--bg-tertiary)] rounded-2xl rounded-bl-md px-5 py-4">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-[var(--border-color)] bg-[var(--bg-secondary)]">
            <div className="flex items-center gap-4">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Escribe tu respuesta..."
                className="flex-1 px-4 py-3 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-color)] text-[var(--text-primary)] placeholder:text-[var(--text-muted)] focus:border-[var(--accent-primary)] focus:outline-none transition-colors"
                disabled={isSending}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isSending}
                className={`h-12 w-12 rounded-xl bg-gradient-to-br ${colorClass} text-white flex items-center justify-center hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all`}
              >
                {isSending ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Competencies */}
        <div className="mt-4 p-4 bg-[var(--bg-card)] rounded-xl border border-[var(--border-color)]">
          <p className="text-sm text-[var(--text-muted)] mb-2">Competencias evaluadas:</p>
          <div className="flex flex-wrap gap-2">
            {selectedSimulator.competencies.map((comp, i) => (
              <span key={i} className="px-3 py-1 rounded-full text-xs bg-[var(--bg-tertiary)] text-[var(--text-secondary)]">
                {comp.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Simulator Selection View
  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">
          Simuladores Profesionales
        </h1>
        <p className="text-[var(--text-secondary)]">
          Practica situaciones reales del mundo laboral con IA
        </p>
      </div>

      {/* Info Card */}
      <div className="bg-gradient-to-r from-indigo-500/10 via-purple-500/10 to-pink-500/10 rounded-2xl border border-[var(--accent-primary)]/20 p-6">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
            <Users className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
              ¿Qué son los simuladores?
            </h3>
            <p className="text-[var(--text-secondary)]">
              Los simuladores te permiten practicar interacciones profesionales reales. 
              Cada simulador adopta un rol específico (Product Owner, Scrum Master, etc.) 
              y evalúa tus competencias transversales como comunicación, análisis y resolución de problemas.
            </p>
          </div>
        </div>
      </div>

      {/* Simulators Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {simulators.map((simulator) => {
          const Icon = simulatorIcons[simulator.type] || Users;
          const colorClass = simulatorColors[simulator.type];
          const isAvailable = simulator.status === 'active';

          return (
            <div
              key={simulator.type}
              className={`bg-[var(--bg-card)] rounded-2xl border border-[var(--border-color)] p-6 transition-all duration-300 ${
                isAvailable 
                  ? 'hover:border-[var(--accent-primary)]/50 hover:shadow-lg hover:shadow-[var(--accent-primary)]/10 cursor-pointer' 
                  : 'opacity-60'
              }`}
              onClick={() => isAvailable && startSimulation(simulator)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${colorClass} flex items-center justify-center`}>
                  <Icon className="w-7 h-7 text-white" />
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  isAvailable 
                    ? 'bg-green-500/10 text-green-400' 
                    : 'bg-yellow-500/10 text-yellow-400'
                }`}>
                  {isAvailable ? 'Disponible' : 'En desarrollo'}
                </span>
              </div>

              <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
                {simulator.name}
              </h3>
              <p className="text-sm text-[var(--text-secondary)] mb-4">
                {simulator.description}
              </p>

              <div className="pt-4 border-t border-[var(--border-color)]">
                <p className="text-xs text-[var(--text-muted)] mb-2">Competencias:</p>
                <div className="flex flex-wrap gap-1">
                  {simulator.competencies.slice(0, 3).map((comp, i) => (
                    <span key={i} className="px-2 py-0.5 rounded text-xs bg-[var(--bg-tertiary)] text-[var(--text-secondary)]">
                      {comp.replace('_', ' ')}
                    </span>
                  ))}
                </div>
              </div>

              {isAvailable && (
                <div className="flex items-center justify-end mt-4 text-[var(--accent-primary)] text-sm font-medium">
                  Iniciar simulación
                  <ArrowRight className="w-4 h-4 ml-2" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
