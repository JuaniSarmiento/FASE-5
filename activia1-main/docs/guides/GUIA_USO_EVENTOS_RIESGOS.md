# 🚀 GUÍA DE USO - Sistema de Eventos, Riesgos y Trazabilidad

## ⚡ INICIO RÁPIDO (5 minutos)

### 1️⃣ Aplicar Migración de Base de Datos

La nueva tabla `simulator_events` debe crearse antes de usar el sistema.

**Opción A: Usando Alembic (recomendado)**
```bash
cd c:\Users\juani\Desktop\Fase-3-v2.0

# Generar migración automática
alembic revision --autogenerate -m "Add simulator_events table"

# Aplicar migración
alembic upgrade head
```

**Opción B: SQL Manual (alternativo)**
```sql
-- Ejecutar en PostgreSQL
CREATE TABLE simulator_events (
    id VARCHAR(36) PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    session_id VARCHAR(36) NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    student_id VARCHAR(100) NOT NULL,
    simulator_type VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    description TEXT,
    severity VARCHAR(20)
);

-- Crear índices para optimización
CREATE INDEX idx_event_session ON simulator_events(session_id, timestamp);
CREATE INDEX idx_event_type_student ON simulator_events(event_type, student_id);
CREATE INDEX idx_event_simulator_session ON simulator_events(simulator_type, session_id);
```

---

### 2️⃣ Cargar Datos de Prueba

```bash
cd c:\Users\juani\Desktop\Fase-3-v2.0

# Ejecutar script de seed
python -m backend.scripts.seed_dev
```

**Output esperado**:
```
================================================================================
SEED DEVELOPMENT DATA - AI-Native MVP
================================================================================

✅ Sesión creada: abc-123-def-456
   - Student: student_001
   - Simulador: Product Owner
   - Estado: completed

✅ 5 eventos de simulador creados
✅ 3 trazas cognitivas creadas
✅ 2 riesgos detectados
✅ Evaluación creada: 7.2/10

================================================================================
✅ SEED COMPLETADO EXITOSAMENTE
================================================================================

🎯 TESTING:
   - Session ID: {COPIAR_ESTE_ID}
```

**⚠️ IMPORTANTE**: Copiar el `Session ID` generado para usarlo en los tests.

---

### 3️⃣ Iniciar Backend

```powershell
cd c:\Users\juani\Desktop\Fase-3-v2.0

# Activar entorno virtual (si usas uno)
# .venv\Scripts\Activate.ps1

# Iniciar servidor
uvicorn backend.api.main:app --reload --port 8000
```

**Verificar**: Abrir http://localhost:8000/docs
- Deberías ver el endpoint `/api/v1/events` en Swagger UI

---

### 4️⃣ Ejecutar Tests Automáticos

En una **nueva terminal**:

```bash
cd c:\Users\juani\Desktop\Fase-3-v2.0

# Ejecutar script de testing
python backend/scripts/test_new_endpoints.py
```

**Output esperado**:
```
🚀 TESTING NEW ENDPOINTS - AI-Native MVP
Target: http://localhost:8000/api/v1

================================================================================
  TEST 1: GET /sessions?student_id=student_001
================================================================================

Status: 200
{
  "success": true,
  "data": [ ... ]
}

✅ Found 1 sessions

================================================================================
  TEST 2: GET /events?session_id=abc-123
================================================================================
...
```

---

### 5️⃣ Iniciar Frontend (Opcional)

```bash
cd c:\Users\juani\Desktop\Fase-3-v2.0\frontEnd

# Instalar dependencias (si es la primera vez)
npm install

# Iniciar dev server
npm run dev
```

**Verificar**: Abrir http://localhost:5173/sessions

---

## 📖 USO DE LOS NUEVOS ENDPOINTS

### 1. Crear Evento de Simulador

**Endpoint**: `POST /api/v1/events`

**Ejemplo (Postman/Thunder Client)**:
```http
POST http://localhost:8000/api/v1/events
Content-Type: application/json

{
  "session_id": "abc-123-def-456",
  "event_type": "backlog_created",
  "event_data": {
    "stories_count": 5,
    "has_acceptance_criteria": false
  },
  "description": "Product Owner creó backlog inicial con 5 user stories",
  "severity": "info"
}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "id": "evt-001",
    "session_id": "abc-123-def-456",
    "student_id": "student_001",
    "simulator_type": "product_owner",
    "event_type": "backlog_created",
    "event_data": { "stories_count": 5, "has_acceptance_criteria": false },
    "timestamp": "2025-12-09T10:00:00Z"
  },
  "message": "Event backlog_created created successfully"
}
```

---

### 2. Listar Eventos de una Sesión

**Endpoint**: `GET /api/v1/events?session_id={id}`

```http
GET http://localhost:8000/api/v1/events?session_id=abc-123-def-456
```

**Respuesta**:
```json
{
  "success": true,
  "data": [
    {
      "id": "evt-001",
      "event_type": "backlog_created",
      "timestamp": "2025-12-09T10:00:00Z",
      ...
    },
    {
      "id": "evt-002",
      "event_type": "sprint_planning_complete",
      "timestamp": "2025-12-09T10:20:00Z",
      ...
    }
  ],
  "pagination": {
    "page": 1,
    "total_items": 5,
    ...
  }
}
```

---

### 3. Analizar Riesgos Automáticamente

**Endpoint**: `POST /api/v1/risks/analyze-session/{session_id}`

```http
POST http://localhost:8000/api/v1/risks/analyze-session/abc-123-def-456
```

**Respuesta**:
```json
{
  "success": true,
  "data": [
    {
      "id": "risk-001",
      "risk_type": "TECHNICAL_DEBT",
      "risk_level": "HIGH",
      "dimension": "Técnico",
      "description": "User stories sin criterios de aceptación claros",
      "recommendations": [
        "Definir criterios de aceptación SMART para cada user story",
        "Incluir ejemplos concretos de comportamiento esperado"
      ],
      "detected_by": "AR-IA-AUTO"
    }
  ],
  "message": "Analyzed 5 events, detected 2 risks"
}
```

---

### 4. Obtener Grafo de Trazabilidad

**Endpoint**: `GET /api/v1/traceability/session/{session_id}`

```http
GET http://localhost:8000/api/v1/traceability/session/abc-123-def-456
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "session_id": "abc-123-def-456",
    "student_id": "student_001",
    "artifacts": [
      {
        "level": 1,
        "type": "event",
        "id": "evt-001",
        "name": "backlog_created",
        "children": [
          {
            "level": 2,
            "type": "trace",
            "id": "trace-001",
            "name": "question",
            "children": [
              {
                "level": 3,
                "type": "risk",
                "id": "risk-001",
                "name": "TECHNICAL_DEBT - HIGH"
              }
            ]
          }
        ]
      }
    ],
    "summary": {
      "total_events": 5,
      "total_traces": 3,
      "total_risks": 2,
      "total_evaluations": 1,
      "avg_ai_involvement": 0.27
    }
  }
}
```

---

### 5. Generar Evaluación con Feedback IA

**Endpoint**: `POST /api/v1/evaluations/{session_id}/generate`

```http
POST http://localhost:8000/api/v1/evaluations/abc-123-def-456/generate
```

**⚠️ NOTA**: Este endpoint puede tardar 30-60 segundos debido al procesamiento del LLM.

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "session_id": "abc-123-def-456",
    "overall_score": 7.2,
    "autonomy_level": "medium",
    "metacognition_score": 6.5,
    "delegation_ratio": 0.27,
    "planning": {
      "score": 8.0,
      "level": "proficient",
      "evidence": ["Priorizó correctamente usando value/effort"],
      "recommendations": ["Mejorar estimación de historias complejas"]
    },
    "overall_feedback": "Buen trabajo identificando historias clave..."
  }
}
```

---

## 🔗 INTEGRACIÓN EN SIMULADORES

### Ejemplo: Product Owner emite eventos

**Archivo**: `backend/agents/simulators/product_owner.py`

```python
import requests

class ProductOwnerSimulator:
    def __init__(self, session_id):
        self.session_id = session_id
    
    def create_backlog(self, stories):
        # Lógica de creación de backlog...
        
        # EMITIR EVENTO
        event_data = {
            "session_id": self.session_id,
            "event_type": "backlog_created",
            "event_data": {
                "stories_count": len(stories),
                "has_acceptance_criteria": all(s.get("acceptance_criteria") for s in stories)
            },
            "description": f"Product Owner creó backlog con {len(stories)} user stories",
            "severity": "info"
        }
        
        # POST al endpoint de eventos
        response = requests.post(
            "http://localhost:8000/api/v1/events",
            json=event_data
        )
        
        # DISPARAR ANÁLISIS DE RIESGOS
        requests.post(
            f"http://localhost:8000/api/v1/risks/analyze-session/{self.session_id}"
        )
        
        return response.json()
```

---

## 🎨 INTEGRACIÓN EN FRONTEND

### Ejemplo: Mostrar riesgos detectados

**Archivo**: `frontEnd/src/components/RiskAlert.tsx`

```tsx
import { useEffect, useState } from 'react';
import { apiClient } from '../services/apiClient';

export function RiskAlert({ sessionId }: { sessionId: string }) {
  const [risks, setRisks] = useState<any[]>([]);

  useEffect(() => {
    // Polling cada 5 segundos
    const interval = setInterval(async () => {
      try {
        const response = await apiClient.get(`/risks?session_id=${sessionId}`);
        const newRisks = response.data?.data || [];
        
        // Filtrar solo riesgos no resueltos
        const pendingRisks = newRisks.filter((r: any) => !r.resolved);
        
        setRisks(pendingRisks);
      } catch (error) {
        console.error('Error fetching risks:', error);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [sessionId]);

  if (risks.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 max-w-md">
      {risks.map((risk) => (
        <div
          key={risk.id}
          className={`mb-2 p-4 rounded-lg shadow-lg ${
            risk.risk_level === 'CRITICAL' ? 'bg-red-100 border-red-500' :
            risk.risk_level === 'HIGH' ? 'bg-orange-100 border-orange-500' :
            'bg-yellow-100 border-yellow-500'
          } border-l-4`}
        >
          <h3 className="font-bold">{risk.risk_level} Risk Detected</h3>
          <p className="text-sm mt-1">{risk.description}</p>
          <div className="mt-2">
            <button className="text-xs text-blue-600 hover:underline">
              View Details
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
```

**Uso**:
```tsx
// En cualquier página de simulador
<RiskAlert sessionId={currentSessionId} />
```

---

## 🐛 TROUBLESHOOTING

### Problema: Error "Table simulator_events doesn't exist"

**Solución**: Ejecutar migración de BD (ver paso 1)

```bash
alembic upgrade head
```

---

### Problema: Error "Cannot connect to backend"

**Solución**: Verificar que el backend esté corriendo

```bash
# En una terminal
uvicorn backend.api.main:app --reload --port 8000
```

---

### Problema: Error "No events found for session"

**Solución**: Cargar datos de prueba

```bash
python -m backend.scripts.seed_dev
```

---

### Problema: Evaluación tarda mucho (>60 segundos)

**Causa**: El modelo LLM (Ollama) está procesando demasiado contexto

**Soluciones**:
1. Reducir número de trazas enviadas al LLM (editar `backend/api/routers/evaluations.py`)
2. Usar un modelo más rápido (cambiar de `llama3` a `phi3` en configuración)
3. Implementar caché de respuestas frecuentes

---

## 📊 MONITOREO Y DEBUGGING

### Logs del Backend

```bash
# Ver logs en tiempo real
tail -f backend.log

# Buscar errores
grep ERROR backend.log
```

### Logs del Frontend (Browser Console)

```javascript
// Filtrar por categoría
// En Chrome DevTools Console:
console.filter = (level) => {
  // Mostrar solo logs de SessionsPage
  return message.includes('[SessionsPage]');
}
```

---

## 🎯 PRÓXIMOS PASOS

1. **Integrar eventos en todos los simuladores**
   - [ ] Product Owner
   - [ ] Scrum Master
   - [ ] Tech Interviewer
   - [ ] Incident Responder
   - [ ] DevSecOps

2. **Crear componentes de visualización**
   - [ ] RiskAlertComponent
   - [ ] TraceabilityGraphComponent
   - [ ] EvaluationFeedbackPanel

3. **Agregar más reglas de detección de riesgos**
   - [ ] Code smells en código generado
   - [ ] Riesgos de comunicación
   - [ ] Riesgos de estimación

4. **Optimizar performance**
   - [ ] Implementar streaming de respuestas LLM
   - [ ] Cachear evaluaciones frecuentes
   - [ ] Optimizar queries de trazabilidad

---

## 📚 RECURSOS ADICIONALES

- **Swagger UI**: http://localhost:8000/docs
- **Documentación del Proyecto**: Ver `docs/`
- **Testing Plan**: Ver `TESTING_PLAN.md`
- **Deployment Guide**: Ver `DEPLOY_GUIDE.md`

---

**¿Necesitas ayuda?** Consulta la documentación completa en `IMPLEMENTACION_EVENTOS_RIESGOS_TRAZABILIDAD.md`
