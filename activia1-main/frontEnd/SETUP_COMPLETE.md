# Frontend AI-Native Student App - Setup Completo

## 🎯 Estado del Proyecto

✅ Configuración base completada (Vite + React + TypeScript)
✅ Tipos TypeScript para toda la API
✅ Capa de servicios con axios (interceptores, manejo de errores)
✅ Context API para gestión de estado
✅ Componentes principales del chat creados

## 📁 Archivos Pendientes de Crear

Para completar la aplicación, ejecuta los siguientes comandos o crea estos archivos manualmente:

### 1. Componentes Faltantes

**frontEnd/src/components/Chat/ChatInput.tsx**
```typescript
import { useState, FormEvent } from 'react';
import { useChat } from '@/contexts/ChatContext';

export function ChatInput() {
  const [input, setInput] = useState('');
  const { sendMessage, isSendingMessage, isSessionActive } = useChat();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSendingMessage) return;

    await sendMessage(input.trim());
    setInput('');
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Escribe tu pregunta aquí..."
        disabled={!isSessionActive || isSendingMessage}
        className="chat-input"
        rows={3}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
          }
        }}
      />
      <button
        type="submit"
        disabled={!isSessionActive || isSendingMessage || !input.trim()}
        className="btn-send"
      >
        {isSendingMessage ? 'Enviando...' : 'Enviar'}
      </button>
    </form>
  );
}
```

**frontEnd/src/components/Chat/SessionStarter.tsx**
```typescript
import { useState, FormEvent } from 'react';
import { useChat } from '@/contexts/ChatContext';
import { SessionMode } from '@/types/api.types';

export function SessionStarter() {
  const [studentId, setStudentId] = useState('');
  const [activityId, setActivityId] = useState('');
  const [mode, setMode] = useState<SessionMode>(SessionMode.TUTOR);
  const { createSession, isLoading, error } = useChat();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!studentId.trim() || !activityId.trim()) return;

    await createSession(studentId.trim(), activityId.trim(), mode);
  };

  return (
    <div className="session-starter">
      <div className="session-starter-card">
        <h1>🎓 Ecosistema AI-Native</h1>
        <p className="subtitle">Aprendizaje de Programación con IA Generativa</p>

        <form onSubmit={handleSubmit} className="session-form">
          <div className="form-group">
            <label htmlFor="studentId">ID de Estudiante</label>
            <input
              id="studentId"
              type="text"
              value={studentId}
              onChange={(e) => setStudentId(e.target.value)}
              placeholder="student_001"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="activityId">ID de Actividad</label>
            <input
              id="activityId"
              type="text"
              value={activityId}
              onChange={(e) => setActivityId(e.target.value)}
              placeholder="prog2_tp1_colas"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="mode">Modo de Aprendizaje</label>
            <select
              id="mode"
              value={mode}
              onChange={(e) => setMode(e.target.value as SessionMode)}
            >
              <option value={SessionMode.TUTOR}>Tutor Cognitivo</option>
              <option value={SessionMode.SIMULATOR}>Simulador Profesional</option>
              <option value={SessionMode.EVALUATOR}>Evaluador de Procesos</option>
            </select>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" disabled={isLoading} className="btn-start-session">
            {isLoading ? 'Creando Sesión...' : 'Iniciar Sesión'}
          </button>
        </form>

        <div className="info-box">
          <h3>ℹ️ Sobre el Sistema</h3>
          <p>
            Este sistema implementa un modelo AI-Native que evalúa tu <strong>proceso cognitivo</strong>, no solo el producto final.
            El tutor te guiará sin sustituir tu razonamiento.
          </p>
        </div>
      </div>
    </div>
  );
}
```

**frontEnd/src/components/Chat/Chat.css**
```css
/* Variables CSS */
:root {
  --primary-color: #4f46e5;
  --primary-hover: #4338ca;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --error-color: #ef4444;
  --bg-color: #f9fafb;
  --card-bg: #ffffff;
  --text-color: #111827;
  --text-secondary: #6b7280;
  --border-color: #e5e7eb;
  --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

/* Chat Container */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--bg-color);
}

/* Chat Header */
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  background-color: var(--card-bg);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow);
}

.chat-header-info h2 {
  margin: 0;
  font-size: 1.25rem;
  color: var(--text-color);
}

.session-info {
  margin: 0.25rem 0 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.status-active {
  color: var(--success-color);
  font-weight: 600;
}

.status-completed {
  color: var(--text-secondary);
}

/* Chat Messages */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background-color: var(--bg-color);
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: var(--text-secondary);
}

/* Individual Message */
.message {
  margin-bottom: 1.5rem;
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.message-role {
  font-weight: 600;
  color: var(--text-color);
}

.message-time {
  color: var(--text-secondary);
}

.message-content {
  background-color: var(--card-bg);
  padding: 1rem;
  border-radius: 0.5rem;
  box-shadow: var(--shadow);
}

.message-user .message-content {
  background-color: var(--primary-color);
  color: white;
  margin-left: auto;
  max-width: 80%;
}

.message-assistant .message-content {
  background-color: var(--card-bg);
  max-width: 85%;
}

.message-system .message-content {
  background-color: #fef3c7;
  border-left: 4px solid var(--warning-color);
  font-style: italic;
}

.message-metadata {
  margin-top: 0.5rem;
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.metadata-tag {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  background-color: var(--bg-color);
  border-radius: 0.25rem;
  color: var(--text-secondary);
}

.metadata-tag.blocked {
  background-color: var(--error-color);
  color: white;
}

/* Chat Input */
.chat-input-container {
  display: flex;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background-color: var(--card-bg);
  border-top: 1px solid var(--border-color);
}

.chat-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  font-family: inherit;
  font-size: 1rem;
  resize: none;
}

.chat-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

/* Buttons */
.btn-send,
.btn-end-session,
.btn-start-session {
  padding: 0.75rem 1.5rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-send:hover:not(:disabled),
.btn-end-session:hover:not(:disabled),
.btn-start-session:hover:not(:disabled) {
  background-color: var(--primary-hover);
}

.btn-send:disabled,
.btn-end-session:disabled,
.btn-start-session:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Session Starter */
.session-starter {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.session-starter-card {
  max-width: 500px;
  width: 100%;
  background-color: var(--card-bg);
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: var(--shadow-lg);
}

.session-starter-card h1 {
  margin: 0 0 0.5rem;
  text-align: center;
  color: var(--text-color);
}

.subtitle {
  text-align: center;
  color: var(--text-secondary);
  margin: 0 0 2rem;
}

.session-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: var(--text-color);
}

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 1px solid var(--border-color);
  border-radius: 0.5rem;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.info-box {
  margin-top: 2rem;
  padding: 1rem;
  background-color: #eff6ff;
  border-left: 4px solid var(--primary-color);
  border-radius: 0.5rem;
}

.info-box h3 {
  margin: 0 0 0.5rem;
  font-size: 1rem;
  color: var(--text-color);
}

.info-box p {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.error-message {
  padding: 0.75rem;
  background-color: #fee2e2;
  color: var(--error-color);
  border-radius: 0.5rem;
  font-size: 0.875rem;
}
```

### 2. Archivos de Entrada

**frontEnd/src/App.tsx**
```typescript
import { ChatProvider } from '@/contexts/ChatContext';
import { ChatContainer } from '@/components/Chat/ChatContainer';
import './App.css';

function App() {
  return (
    <ChatProvider>
      <ChatContainer />
    </ChatProvider>
  );
}

export default App;
```

**frontEnd/src/App.css**
```css
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}

#root {
  min-height: 100vh;
}
```

**frontEnd/src/main.tsx**
```typescript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.tsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**frontEnd/src/index.css**
```css
:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;

  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  font-weight: 500;
  color: #646cff;
  text-decoration: inherit;
}

a:hover {
  color: #535bf2;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

h1 {
  font-size: 3.2em;
  line-height: 1.1;
}

button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
  background-color: #1a1a1a;
  cursor: pointer;
  transition: border-color 0.25s;
}

button:hover {
  border-color: #646cff;
}

button:focus,
button:focus-visible {
  outline: 4px auto -webkit-focus-ring-color;
}

@media (prefers-color-scheme: light) {
  :root {
    color: #213547;
    background-color: #ffffff;
  }

  a:hover {
    color: #747bff;
  }

  button {
    background-color: #f9f9f9;
  }
}
```

**frontEnd/index.html**
```html
<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI-Native Student App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**frontEnd/.env.example**
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### 3. README del Frontend

Ver archivo README.md en la raíz de frontEnd.

## 🚀 Instalación y Ejecución

```bash
cd frontEnd

# Instalar dependencias
npm install

# Ejecutar en modo desarrollo
npm run dev

# Compilar para producción
npm run build

# Previsualizar build de producción
npm run preview
```

## 🎯 Características Implementadas

- ✅ Interfaz de chat en tiempo real
- ✅ Creación y gestión de sesiones
- ✅ Visualización de metadatos (agente usado, estado cognitivo, nivel de IA)
- ✅ Detección de bloqueos por gobernanza
- ✅ Alertas de riesgos detectados
- ✅ Soporte para Markdown en respuestas del tutor
- ✅ Indicadores de carga
- ✅ Manejo de errores robusto
- ✅ Responsive design

## 📚 Próximas Mejoras

- [ ] Vista de trazabilidad N4 (camino cognitivo)
- [ ] Dashboard de evaluación de procesos
- [ ] Gráficos de dependencia de IA
- [ ] Historial de sesiones
- [ ] Modo oscuro
- [ ] Tests unitarios con Vitest
- [ ] Tests E2E con Playwright