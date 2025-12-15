# Frontend Tutor Socrático V2.0

## 📋 Resumen

Interfaz de usuario completa para el sistema de Tutor Socrático V2.0 con reglas pedagógicas inquebrantables, sistema de semáforos, y analytics de aprendizaje.

## 🎯 Características Principales

### 1. Pantalla de Bienvenida
- **4 Reglas Pedagógicas** mostradas visualmente:
  - 🚫 **Anti-Solución Directa**: No código completo, solo guía con preguntas
  - ❓ **Modo Socrático**: Preguntas antes que respuestas
  - 💭 **Explicitación**: Justificación obligatoria del razonamiento
  - 📚 **Refuerzo Conceptual**: Fundamentos teóricos sobre parches sintácticos

- **Sistema de Semáforos** explicado:
  - 🟢 **VERDE**: Bajo riesgo - Interacción normal
  - 🟡 **AMARILLO**: Alta dependencia - Reducir ayuda
  - 🔴 **ROJO**: Delegación total - Solo preguntas socráticas

### 2. Panel de Perfil del Estudiante
Visualización en tiempo real de métricas clave:
- **Dependencia de IA**: Barra de progreso con color semafórico
  - Verde < 40%
  - Amarillo 40-70%
  - Rojo > 70%
- **Soluciones Autónomas**: Contador de éxitos sin ayuda de IA
- **Auto-corrección**: Tasa de errores corregidos por el estudiante

### 3. Chat con Metadata
Cada mensaje del tutor muestra:
- **Badge de Semáforo**: Color e ícono del estado actual (🟢/🟡/🔴)
- **Tipo de Intervención**: 
  - ❓ Pregunta Socrática
  - 🚫 Rechazo Pedagógico
  - 💡 Pista Graduada
  - 📚 Corrección Conceptual
  - 💭 Exigencia de Justificación
- **Nivel de Ayuda**: Bajo/Medio/Alto

### 4. Analytics de Sesión
Modal completo con estadísticas:
- **Total de Mensajes**: Contador general
- **Distribución de Semáforos**: Conteo Verde/Amarillo/Rojo
- **Tipos de Intervención**: Desglose por tipo de interacción
- **Perfil Actual**: Snapshot del estado del estudiante

## 🔧 Arquitectura Técnica

### Componente Principal: TutorPage.tsx

```typescript
interface Message {
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    intervention_type?: string;
    semaforo?: 'verde' | 'amarillo' | 'rojo';
    help_level?: string;
    requires_student_response?: boolean;
    cognitive_events?: string[];
  };
}

interface StudentProfile {
  avg_ai_involvement: number;      // 0.0 - 1.0
  successful_autonomous_solutions: number;
  error_self_correction_rate: number; // 0.0 - 1.0
}
```

### Flujo de Datos

1. **Crear Sesión**:
   ```
   POST /sessions/create-tutor
   → session_id
   → Mensaje de bienvenida con 4 reglas
   ```

2. **Enviar Mensaje**:
   ```
   POST /sessions/{session_id}/interact
   Body: {
     message: "...",
     student_profile: {
       avg_ai_involvement,
       successful_autonomous_solutions,
       error_self_correction_rate
     }
   }
   → Respuesta con metadata completa
   ```

3. **Actualizar Perfil** (automático):
   - Detecta bloques de código en mensajes del usuario
   - Evalúa presencia de justificación textual
   - Analiza semáforo de la respuesta del tutor
   - Ajusta métricas dinámicamente

4. **Cargar Analytics**:
   ```
   GET /sessions/{session_id}/analytics-n4
   → Estadísticas completas de la sesión
   ```

## 🎨 Estilos y Diseño

### Paleta de Colores
- **Primario**: Gradiente púrpura (#667eea → #764ba2)
- **Semáforos**:
  - Verde: #d1fae5 / #065f46
  - Amarillo: #fef3c7 / #92400e
  - Rojo: #fee2e2 / #991b1b

### Componentes Clave
- **TutorPage.css**: 450+ líneas de estilos modulares
- Animaciones suaves (slideIn, bounce, modalSlideIn)
- Diseño responsive (desktop/tablet/mobile)
- Grid system flexible para reglas y analytics

## 🚀 Uso y Testing

### Iniciar Frontend
```powershell
cd frontEnd
npm run dev
```

### Flujo de Usuario
1. Abrir `/tutor` en el navegador
2. Leer las 4 reglas pedagógicas en la pantalla de bienvenida
3. Click en "Iniciar Sesión de Tutoría"
4. Interactuar enviando preguntas o código
5. Observar badges de semáforo y tipo de intervención
6. Monitorear perfil del estudiante en sidebar
7. Revisar analytics con botón "Ver Analytics"

### Escenarios de Test

#### ✅ Escenario 1: Solicitud de Código Directo
**Usuario**: "Dame el código para ordenar un array"
**Esperado**: 
- 🔴 Semáforo ROJO
- 🚫 Rechazo Pedagógico
- Respuesta con pregunta socrática
- Incremento en `avg_ai_involvement`

#### ✅ Escenario 2: Pregunta Conceptual
**Usuario**: "¿Qué diferencia hay entre mergesort y quicksort?"
**Esperado**:
- 🟢 Semáforo VERDE
- 📚 Corrección Conceptual o ❓ Pregunta Socrática
- Respuesta con contra-pregunta sobre complejidad

#### ✅ Escenario 3: Código Sin Justificación
**Usuario**: 
```python
def sort(arr):
    return sorted(arr)
```
**Esperado**:
- 🟡 Semáforo AMARILLO
- 💭 Exigencia de Justificación
- Pregunta: "¿Por qué elegiste sorted()?"

#### ✅ Escenario 4: Solución Autónoma Completa
**Usuario**: "Implementé quicksort usando partición Lomuto porque..."
**Esperado**:
- 🟢 Semáforo VERDE
- Incremento en `successful_autonomous_solutions`
- Mejora en `error_self_correction_rate`

## 📊 Integración con Backend

### Endpoints Utilizados
1. **POST /sessions/create-tutor**
   - Crea sesión de tutoría
   - Retorna `session_id`

2. **POST /sessions/{id}/interact**
   - Envía mensaje del estudiante
   - Recibe respuesta con metadata V2.0

3. **GET /sessions/{id}/analytics-n4**
   - Obtiene estadísticas completas
   - Distribución de semáforos
   - Tipos de intervención
   - Eventos cognitivos detectados

### Metadata Backend → Frontend
El backend (tutor.py) envía:
```python
{
  "response": "...",
  "metadata": {
    "intervention_type": "pregunta_socratica",
    "semaforo": "verde",
    "help_level": "bajo",
    "requires_student_response": true,
    "cognitive_events": ["confusion_detected"],
    "rule_violations": []
  }
}
```

Frontend mapea a interfaz visual:
- `intervention_type` → Badge con ícono
- `semaforo` → Color de badge y clase CSS
- `help_level` → Badge adicional
- `cognitive_events` → Análisis interno

## 🔄 Actualización Dinámica del Perfil

### Algoritmo de Actualización
```typescript
updateStudentProfile(message: string, response: Message) {
  // 1. Detectar bloques de código
  const hasCode = /```/.test(message);
  
  // 2. Detectar justificación
  const hasJustification = message.split(' ').length > 20 && 
                           /porque|ya que|debido/.test(message);
  
  // 3. Analizar semáforo
  const semaforo = response.metadata?.semaforo;
  
  // 4. Ajustar métricas
  if (hasCode && !hasJustification) {
    avg_ai_involvement += 0.05; // Incrementar dependencia
  }
  
  if (hasJustification && semaforo === 'verde') {
    successful_autonomous_solutions++; // Solución exitosa
    error_self_correction_rate += 0.02;
  }
  
  if (semaforo === 'rojo') {
    avg_ai_involvement += 0.1; // Penalización fuerte
  }
}
```

## 🎓 Pedagogía Visible

### Transparencia Cognitiva
El frontend hace visibles los procesos pedagógicos:
- **Semáforos**: El estudiante ve en tiempo real su nivel de dependencia
- **Tipos de Intervención**: Comprende por qué el tutor responde de cierta forma
- **Métricas**: Autoevaluación cuantitativa de su autonomía

### Andamiaje Metacognitivo
- Badges de intervención fomentan reflexión sobre el tipo de ayuda recibida
- Gráficos de analytics permiten identificar patrones de aprendizaje
- Perfil dinámico motiva mejora continua

## 📝 Próximos Pasos

### Mejoras Futuras
- [ ] Gráficos interactivos en analytics (Chart.js / Recharts)
- [ ] Exportar historial de sesión a PDF
- [ ] Comparación de sesiones (progreso temporal)
- [ ] Recomendaciones personalizadas basadas en perfil
- [ ] Modo oscuro para el chat
- [ ] Notificaciones cuando semáforo cambia a ROJO

### Optimizaciones
- [ ] Lazy loading de mensajes antiguos
- [ ] Cache de analytics en localStorage
- [ ] Debounce en actualización de perfil
- [ ] Websockets para chat en tiempo real

## 📚 Referencias

- **Backend**: `backend/agents/tutor.py`
- **Reglas**: `backend/agents/tutor_rules.py`
- **Governance**: `backend/agents/tutor_governance.py`
- **Metadata**: `backend/agents/tutor_metadata.py`
- **Prompts**: `backend/agents/tutor_prompts.py`
- **Documentación Backend**: `docs/TUTOR_SOCRATICO_V2.md`

---

**Versión**: 2.0  
**Fecha**: 2024  
**Estado**: ✅ Completo y Funcional
