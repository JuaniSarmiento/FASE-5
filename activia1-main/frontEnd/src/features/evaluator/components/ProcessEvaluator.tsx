/**
 * Evaluador de Procesos Cognitivos - Componente simplificado
 */
import React, { useState } from 'react';
import './ProcessEvaluator.css';

export const ProcessEvaluator: React.FC = () => {
  const [loading] = useState(false);

  return (
    <div className="evaluator">
      <div className="evaluator-header">
        <div>
          <h2>📊 Evaluador de Procesos Cognitivos</h2>
          <p>Análisis basado en el PROCESO, no en el producto final</p>
        </div>
      </div>

      <div className="evaluator-content">
        <main className="evaluation-panel">
          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Analizando proceso cognitivo...</p>
            </div>
          )}

          {!loading && (
            <div className="empty-state-large">
              <div className="empty-icon">📊</div>
              <h3>Evaluador de Procesos - E-IA-Proc</h3>
              <p>Análisis de 5 dimensiones cognitivas:</p>
              <ul style={{ textAlign: 'left', maxWidth: '600px', margin: '20px auto' }}>
                <li>🎯 <strong>Planificación</strong>: Cómo aborda problemas y descompone tareas</li>
                <li>⚡ <strong>Ejecución</strong>: Implementación de soluciones y buenas prácticas</li>
                <li>🐛 <strong>Debugging</strong>: Diagnóstico sistemático de errores</li>
                <li>💭 <strong>Reflexión</strong>: Metacognición y aprendizaje de errores</li>
                <li>🚀 <strong>Autonomía</strong>: Independencia vs delegación a IA</li>
              </ul>
              <p style={{ marginTop: '30px', color: '#6b7280' }}>
                Conectado a <code>/api/v1/evaluations/:sessionId/generate</code>
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
