# Guía para Instructores - UAT AI-Native MVP

## Panel de Administración y Supervisión

Esta guía describe el uso del **Panel de Instructor** durante las pruebas de aceptación de usuarios (UAT), permitiendo supervisión en tiempo real, análisis de trazabilidad y gestión de feedback.

---

## 📋 Tabla de Contenidos

1. [Acceso y Configuración Inicial](#acceso-y-configuración-inicial)
2. [Dashboard Principal](#dashboard-principal)
3. [Supervisión de Sesiones en Tiempo Real](#supervisión-de-sesiones-en-tiempo-real)
4. [Panel de Trazabilidad Cognitiva](#panel-de-trazabilidad-cognitiva)
5. [Análisis de Riesgos y Alertas](#análisis-de-riesgos-y-alertas)
6. [Gestión de Bugs y Feedback](#gestión-de-bugs-y-feedback)
7. [Reportes y Analytics](#reportes-y-analytics)
8. [Intervención y Moderación](#intervención-y-moderación)
9. [Exportación de Datos](#exportación-de-datos)
10. [Troubleshooting](#troubleshooting)

---

## 1. Acceso y Configuración Inicial

### 1.1 Credenciales de Instructor

**URL**: `https://staging.ai-native.example.com/instructor`

**Credenciales**:
```
Usuario: instructor@institution.edu
Contraseña: [contraseña segura proporcionada]
Rol: INSTRUCTOR
```

**Permisos**:
- ✅ Ver todas las sesiones de estudiantes
- ✅ Acceder a trazabilidad N4 completa
- ✅ Revisar reportes de evaluación (E-IA-Proc)
- ✅ Gestionar bugs y feedback
- ✅ Exportar datos anonimizados
- ❌ NO puede modificar interacciones pasadas (inmutabilidad)
- ❌ NO puede eliminar trazas (integridad)

### 1.2 Configuración Inicial

Al primer acceso, configura:

**Notificaciones**:
- [ ] Email en tiempo real para bugs críticos
- [ ] Resumen diario de actividad
- [ ] Alertas de riesgos de alta severidad

**Preferencias de Dashboard**:
- Vista predeterminada: Sesiones activas / Resumen general
- Zona horaria: [Tu zona horaria]
- Idioma: Español

---

## 2. Dashboard Principal

### 2.1 Vista General

El dashboard muestra 4 paneles principales:

```
┌─────────────────────────────────────────────────────────────┐
│  📊 Dashboard UAT - AI-Native MVP                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │ Sesiones      │  │ Bugs          │  │ Satisfacción  │  │
│  │ Activas: 3/5  │  │ Críticos: 2   │  │ SUS: 75.2     │  │
│  │ Total: 47     │  │ Total: 15     │  │ Avg: 4.2/5    │  │
│  └───────────────┘  └───────────────┘  └───────────────┘  │
│                                                              │
│  📈 Actividad de las últimas 24h                            │
│  [Gráfico de líneas: Sesiones por hora]                     │
│                                                              │
│  👥 Estudiantes Activos                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ E01 • Última actividad: Hace 5min • T-IA-Cog        │   │
│  │ E03 • Última actividad: Hace 12min • S-IA-X (PO)    │   │
│  │ E05 • Última actividad: Hace 18min • E-IA-Proc      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  🚨 Alertas Recientes                                       │
│  • [10:45] E02 - Riesgo Cognitivo ALTO (Delegación)        │
│  • [11:20] E04 - Bug CRÍTICO reportado (API timeout)       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Métricas Clave

**Métricas de Uso**:
- **Sesiones totales**: 47 (objetivo: 50-70)
- **Tiempo promedio por sesión**: 32 min (objetivo: 30-45 min)
- **Interacciones totales**: 423 (promedio 9 por sesión)
- **Tasa de finalización**: 85% (objetivo: >80%)

**Métricas de Calidad**:
- **SUS Score**: 75.2 (objetivo: ≥70)
- **Satisfacción promedio**: 4.2/5.0 (objetivo: ≥4.0)
- **Bugs críticos**: 2 (objetivo: ≤5)
- **Tiempo promedio de respuesta**: 2.3s (SLA: <3s)

**Métricas Pedagógicas**:
- **Detección de delegación**: 12 casos bloqueados por GOV-IA
- **Nivel de competencia promedio**: INTERMEDIO
- **Score promedio (E-IA-Proc)**: 68/100
- **Riesgos detectados**: 34 (28 MEDIUM, 5 HIGH, 1 CRITICAL)

---

## 3. Supervisión de Sesiones en Tiempo Real

### 3.1 Ver Sesiones Activas

**Acceso**: Dashboard → "Sesiones Activas"

**Vista de Lista**:
```
┌──────────────────────────────────────────────────────────┐
│ Sesiones Activas (3)                                     │
├──────────────────────────────────────────────────────────┤
│ ID         │ Estudiante │ Actividad      │ Modo  │ Dur. │
│ session_01 │ E01        │ TP1 - Colas    │ TUTOR │ 25m  │
│ session_02 │ E03        │ TP1 - Colas    │ PO    │ 18m  │
│ session_03 │ E05        │ TP1 - Colas    │ EVAL  │ 40m  │
└──────────────────────────────────────────────────────────┘
```

**Haz clic en una sesión** para ver detalles:

### 3.2 Vista Detallada de Sesión

```
┌─────────────────────────────────────────────────────────┐
│ Sesión: session_01 (E01 - Estudiante 1)                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Información General:                                    │
│  • Actividad: TP1 - Colas Circulares                   │
│  • Modo: TUTOR (T-IA-Cog)                              │
│  • Inicio: 2025-11-24 10:15:00                         │
│  • Duración: 25 minutos                                 │
│  • Interacciones: 7                                     │
│                                                          │
│ Estado Cognitivo Actual: PLANIFICACION                  │
│ AI Dependency: 35% (saludable)                          │
│                                                          │
│ Historial de Interacciones (últimas 3):                │
│ ┌───────────────────────────────────────────────────┐  │
│ │ [10:38] Estudiante:                                │  │
│ │ "¿Cómo implemento el método dequeue()?"           │  │
│ │                                                     │  │
│ │ [10:39] T-IA-Cog (GUIADO, AI: 40%):               │  │
│ │ "Antes de implementar, reflexionemos:             │  │
│ │  ¿Qué índice debe actualizarse al remover?..."    │  │
│ └───────────────────────────────────────────────────┘  │
│                                                          │
│ Riesgos Detectados: 1 MEDIUM                            │
│  • Razonamiento superficial (10:25)                    │
│                                                          │
│ Acciones:                                                │
│  [Ver Trazas] [Ver Evaluación] [Enviar Mensaje]        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Modo de Observación (Live View)

**Activar**: Click en "Live View" en la sesión activa

**Funcionalidad**:
- Actualización en tiempo real (WebSocket)
- Ver prompts y respuestas conforme ocurren
- Observar cambios de estado cognitivo
- Recibir alertas de riesgos inmediatamente

**Uso recomendado**:
- Supervisar sesiones de estudiantes con dificultades
- Observar primeras sesiones de cada estudiante
- Validar funcionamiento de agentes en casos edge

**Privacidad**: El estudiante NO ve que estás observando (no invasivo)

---

## 4. Panel de Trazabilidad Cognitiva

### 4.1 Acceder a Trazas N4

**Acceso**: Dashboard → "Trazabilidad" → Seleccionar estudiante

**Vista de Camino Cognitivo**:

```
┌─────────────────────────────────────────────────────────┐
│ Camino Cognitivo - E02 (Estudiante 2)                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Sesión: session_04 (TP1 - Colas, TUTOR)                │
│ Duración: 42 minutos                                     │
│                                                          │
│ Secuencia de Estados:                                   │
│  [10:00] EXPLORACION_CONCEPTUAL (15min)                │
│     └─> Preguntó: "¿Qué es una cola circular?"         │
│     └─> Preguntó: "¿Cuándo usar cola vs lista?"        │
│                                                          │
│  [10:15] PLANIFICACION (10min)                          │
│     └─> Indicó: "Voy a usar un arreglo de tamaño fijo" │
│     └─> Preguntó: "¿Cómo manejo índices wrap-around?"  │
│                                                          │
│  [10:25] IMPLEMENTACION (12min)                         │
│     └─> Compartió código del método enqueue()          │
│     └─> Preguntó: "¿Está correcto este código?"        │
│                                                          │
│  [10:37] DEBUGGING (5min)                               │
│     └─> Reportó: "Falla cuando la cola está llena"     │
│     └─> Solicitó: Ayuda con condición de lleno         │
│                                                          │
│ Evolución de AI Dependency:                             │
│  [Gráfico de líneas]                                    │
│   60% ┤                                  ╭─╮            │
│   50% ┤                        ╭────╮    │ │            │
│   40% ┤           ╭────────────╯    ╰────╯ │            │
│   30% ┤   ╭───────╯                        │            │
│   20% ┤───╯                                ╰───         │
│       └───────────────────────────────────────> tiempo  │
│       EXPLOR  PLAN   IMPL   DEBUG                      │
│                                                          │
│ Métricas:                                               │
│  • AI Dependency promedio: 38%                          │
│  • Cambios de estrategia: 2                             │
│  • Tiempo en delegación: 8% (saludable <15%)           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Análisis de Trazas

**Filtros disponibles**:
- Por estudiante
- Por actividad
- Por rango de fechas
- Por estado cognitivo
- Por nivel de AI Dependency (bajo, medio, alto)

**Exports**:
- CSV: Trazas tabulares para análisis en Excel/R/Python
- JSON: Datos estructurados completos
- Visualización PDF: Informe visual del camino cognitivo

### 4.3 Detección de Patrones

El sistema automáticamente identifica:

**Patrones Positivos**:
- ✅ **Exploración sistemática**: Secuencia coherente EXPLOR→PLAN→IMPL
- ✅ **Autorregulación**: Estudiante detecta errores y autocorrige
- ✅ **Razonamiento profundo**: AI Dependency baja (<30%) con preguntas específicas

**Patrones de Riesgo**:
- ⚠️ **Delegación excesiva**: AI Dependency >60% sostenida
- ⚠️ **Razonamiento superficial**: Preguntas genéricas sin follow-up
- ⚠️ **Aceptación acrítica**: No cuestiona respuestas del agente

---

## 5. Análisis de Riesgos y Alertas

### 5.1 Panel de Riesgos

**Acceso**: Dashboard → "Riesgos Detectados"

**Vista de Lista**:
```
┌──────────────────────────────────────────────────────────┐
│ Riesgos Detectados (34 totales)                         │
├──────────────────────────────────────────────────────────┤
│ Severidad │ Dimensión  │ Estudiante │ Descripción       │
├───────────┼────────────┼────────────┼───────────────────┤
│ 🔴 HIGH   │ Cognitivo  │ E02        │ Delegación total  │
│ 🟠 MEDIUM │ Epistémico │ E03        │ Error conceptual  │
│ 🟠 MEDIUM │ Cognitivo  │ E01        │ Razonamiento sup. │
│ 🟡 LOW    │ Ético      │ E04        │ Uso no declarado  │
└──────────────────────────────────────────────────────────┘
```

### 5.2 Detalles de Riesgo

**Haz clic en un riesgo** para ver:

```
┌─────────────────────────────────────────────────────────┐
│ Riesgo #12 - Delegación Total (HIGH)                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Estudiante: E02 (Estudiante 2)                         │
│ Sesión: session_04                                      │
│ Timestamp: 2025-11-24 10:30:15                          │
│ Dimensión: Cognitivo (RC)                               │
│ Tipo: COGNITIVE_DELEGATION                              │
│                                                          │
│ Evidencia:                                              │
│  • Prompt: "Dame el código completo de ColaCircular"   │
│  • AI Dependency: 85% (umbral crítico: 70%)            │
│  • No hay preguntas de comprensión previas             │
│                                                          │
│ Contexto (trazas relacionadas):                         │
│  [10:28] Pregunta genérica sobre colas                 │
│  [10:30] ⚠️ Solicitud de código completo               │
│  [10:30] 🚫 Bloqueado por GOV-IA                       │
│                                                          │
│ Recomendaciones (generadas por AR-IA):                  │
│  1. Intervenir con feedback formativo sobre delegación │
│  2. Sugerir descomposición del problema en pasos       │
│  3. Monitorear próximas sesiones para recurrencia      │
│                                                          │
│ Acciones:                                                │
│  [Marcar como Revisado]                                 │
│  [Enviar Feedback al Estudiante]                        │
│  [Añadir a Reporte]                                     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 5.3 Configurar Alertas

**Acceso**: Configuración → "Alertas de Riesgos"

**Configuración recomendada**:
```yaml
alertas:
  critical_risks:
    enabled: true
    channels:
      - email_inmediato
      - dashboard_popup
    umbrales:
      - delegation_score > 70%
      - conceptual_error_severity: HIGH

  high_risks:
    enabled: true
    channels:
      - email_resumen_diario
    umbrales:
      - ai_dependency_sustained > 60% for 15min

  pattern_alerts:
    enabled: true
    patterns:
      - "3+ consecutive generic questions"
      - "No follow-up questions after AI response"
```

---

## 6. Gestión de Bugs y Feedback

### 6.1 Panel de Bugs

**Acceso**: Dashboard → "Bugs Reportados"

**Vista de Kanban**:
```
┌──────────────────────────────────────────────────────────┐
│ Bugs Reportados (15 totales)                            │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  🆕 NUEVO (5)      🔍 TRIAGED (3)   ✅ RESUELTO (7)      │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐      │
│  │ BUG-001    │   │ BUG-003    │   │ BUG-002    │      │
│  │ CRITICAL   │   │ HIGH       │   │ MEDIUM     │      │
│  │ E04        │   │ E01        │   │ E03        │      │
│  │ API timeout│   │ Traza no   │   │ UI: botón  │      │
│  │            │   │ guarda     │   │ deshabili. │      │
│  └────────────┘   └────────────┘   └────────────┘      │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

### 6.2 Priorizar y Asignar Bugs

**Click en un bug** para ver detalles:

```
┌─────────────────────────────────────────────────────────┐
│ BUG-001 - API Timeout en Prompts Largos (CRITICAL)     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ Reportado por: E04 (Estudiante 4)                      │
│ Fecha: 2025-11-24 11:20:00                              │
│ Severidad: CRITICAL                                     │
│ Estado: NUEVO                                            │
│                                                          │
│ Descripción:                                            │
│  "Cuando envío un prompt de más de 500 palabras,       │
│   el servidor responde con 504 Gateway Timeout después │
│   de 30 segundos. La sesión queda colgada."            │
│                                                          │
│ Pasos para Reproducir:                                  │
│  1. Crear sesión con T-IA-Cog                          │
│  2. Pegar prompt de >500 palabras en el campo          │
│  3. Hacer click en "Enviar"                            │
│  4. Esperar 30 segundos                                 │
│  5. Ver error 504                                       │
│                                                          │
│ Frecuencia: 3 veces en 2 horas                         │
│ Navegador: Chrome 120.0 / Windows 11                   │
│ Screenshot: [bug-001-screenshot.png]                    │
│                                                          │
│ Análisis Automático (Sistema):                          │
│  • Logs: Timeout en LLM provider (OpenAI API)          │
│  • Prompt length: 1,200 tokens (límite: 2,000)         │
│  • Recomendación: Aumentar timeout de 30s a 60s        │
│                                                          │
│ Acciones:                                                │
│  Severidad: [CRITICAL ▼]                                │
│  Asignar a: [Backend Team ▼]                            │
│  Prioridad: [P0 - Inmediato ▼]                          │
│  [Comentar] [Cambiar Estado] [Notificar a E04]         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 6.3 Criterios de Severidad

**CRITICAL** (P0 - Resolver en 24h):
- Sistema inutilizable
- Pérdida de datos
- Vulnerabilidad de seguridad

**HIGH** (P1 - Resolver en 3 días):
- Funcionalidad principal no funciona
- Afecta a mayoría de usuarios
- Workaround no trivial

**MEDIUM** (P2 - Resolver en 1 semana):
- Funcionalidad secundaria afectada
- Workaround disponible
- Afecta a pocos usuarios

**LOW** (P3 - Resolver en 2 semanas):
- Problema cosmético
- No afecta funcionalidad
- Nice-to-have

### 6.4 Feedback Cualitativo

**Acceso**: Dashboard → "Feedback de Usuarios"

**Vista de Comentarios**:
```
┌─────────────────────────────────────────────────────────┐
│ Feedback Cualitativo (23 comentarios)                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 😊 Positivo (15)    😐 Neutral (5)    😞 Negativo (3)   │
│                                                          │
│ [E01] "El tutor es muy paciente, me ayudó a entender   │
│       la diferencia entre cola y pila sin darme el     │
│       código directamente. ¡Aprendí más así!"          │
│       Tags: [pedagogia] [socratico]                     │
│                                                          │
│ [E03] "Los simuladores son interesantes, pero el PO-IA │
│       a veces da requerimientos demasiado vagos..."    │
│       Tags: [simuladores] [claridad]                    │
│                                                          │
│ [E05] "Me gustaría poder ver el código de otros        │
│       estudiantes de forma anónima para comparar."     │
│       Tags: [feature-request] [comparacion]             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Etiquetar feedback** con:
- Categorías: pedagogía, usabilidad, funcionalidad, performance
- Sentiment: positivo, neutral, negativo
- Acción requerida: none, considerar, implementar

---

## 7. Reportes y Analytics

### 7.1 Reporte de UAT Diario

**Generación automática**: Cada día a las 8:00 AM

**Contenido**:
```markdown
# UAT Daily Report - 2025-11-24

## Resumen Ejecutivo
- Sesiones completadas ayer: 12
- Nuevos bugs: 4 (1 CRITICAL, 3 MEDIUM)
- SUS Score actual: 75.2 (+2.1 vs ayer)
- Satisfacción promedio: 4.2/5.0

## Actividad por Estudiante
| Estudiante | Sesiones | Tiempo Total | Estado Cognitivo Predominante |
|------------|----------|--------------|-------------------------------|
| E01        | 3        | 2h 15min     | IMPLEMENTACION (45%)          |
| E02        | 2        | 1h 30min     | EXPLORACION_CONCEPTUAL (60%)  |
| ...        | ...      | ...          | ...                           |

## Riesgos Nuevos
- [HIGH] E02 - Delegación total detectada (10:30)
- [MEDIUM] E03 - Error conceptual sobre complejidad (14:45)

## Bugs Críticos
- BUG-001: API timeout en prompts largos (reportado por E04)
  - Status: TRIAGED → Backend team
  - ETA: 2025-11-25

## Acciones Requeridas
1. Revisar riesgo HIGH de E02 (delegación)
2. Validar fix de BUG-001 en staging
3. Responder a feedback de E05 sobre feature request
```

### 7.2 Reporte de Progreso de UAT (Semanal)

**Generación**: Viernes de cada semana a las 18:00

**Secciones**:
1. **Cobertura de Escenarios**: % completado por cada uno de los 7 escenarios
2. **Métricas de Calidad**: SUS, satisfacción, bugs por severidad
3. **Análisis Pedagógico**: Competencia promedio, AI Dependency, patrones cognitivos
4. **Recomendaciones**: Go/No-Go preliminar, ajustes necesarios

### 7.3 Dashboard de Analytics

**Acceso**: Dashboard → "Analytics"

**Gráficos disponibles**:

**1. Evolución de SUS Score**:
```
 80 ┤                                    ╭─────╮
 75 ┤                          ╭─────────╯     │
 70 ┤                  ╭───────╯               │
 65 ┤          ╭───────╯                       │
 60 ┤  ╭───────╯                               │
    └──────────────────────────────────────────> días
     1   2   3   4   5   6   7   8   9   10
```

**2. Distribución de Riesgos**:
```
Cognitivos  ████████████████████ 20 (59%)
Epistémicos █████████ 9 (26%)
Éticos      ████ 4 (12%)
Técnicos    █ 1 (3%)
```

**3. Uso de Agentes**:
```
T-IA-Cog    ████████████████████████████████ 65%
S-IA-X      ██████████ 20%
E-IA-Proc   ████ 8%
AR-IA       ██ 5%
GOV-IA      █ 2%
```

**4. Tiempo de Respuesta (p95)**:
```
 5s ┤
 4s ┤                     ╭╮
 3s ┤         ╭───╮   ╭───╯╰───╮
 2s ┤  ╭──────╯   ╰───╯         ╰──────╮
 1s ┤──╯                                ╰───
    └────────────────────────────────────────> días
    SLA: < 3s (cumplido 92% del tiempo)
```

---

## 8. Intervención y Moderación

### 8.1 Enviar Mensaje a Estudiante

**Acceso**: Sesión → "Enviar Mensaje"

**Casos de uso**:
- Feedback formativo sobre riesgo detectado
- Aclaración sobre bug reportado
- Orientación pedagógica personalizada
- Agradecimiento por feedback útil

**Template de mensaje formativo**:
```
Asunto: Feedback sobre tu sesión del 2025-11-24

Hola [Nombre del estudiante],

He revisado tu sesión de hoy con el Tutor Cognitivo (T-IA-Cog) y
quería compartir algunas observaciones que pueden ayudarte:

**Fortalezas observadas**:
- Exploración sistemática del concepto de cola circular
- Preguntas específicas y bien formuladas
- Buena capacidad de reflexión sobre errores

**Área de mejora**:
He notado que en un momento solicitaste "el código completo"
de la clase. Esto fue bloqueado por el sistema (GOV-IA) porque:

1. Disminuye tu oportunidad de razonamiento autónomo
2. Genera dependencia excesiva de la IA
3. No te permite construir comprensión profunda

**Recomendación**:
En lugar de pedir código completo, intenta:
- Descomponer el problema en métodos individuales
- Preguntar sobre la lógica de una operación específica
- Solicitar validación de tu propio diseño

Si necesitas ayuda, estoy disponible.

Saludos,
Instructor
```

### 8.2 Moderación de Interacciones

**Capacidades**:
- ❌ **NO** puedes editar prompts/respuestas pasados (inmutabilidad)
- ❌ **NO** puedes eliminar trazas (integridad)
- ✅ Puedes marcar sesiones como "Requiere revisión manual"
- ✅ Puedes añadir notas privadas para ti (no visibles para estudiante)
- ✅ Puedes suspender temporalmente acceso de estudiante (caso extremo)

### 8.3 Intervención en Tiempo Real

**Activar**: Durante Live View de sesión → "Intervenir"

**Opciones**:
1. **Enviar sugerencia al agente**: El agente ajusta su próxima respuesta
2. **Mensaje directo al estudiante**: Aparece como notificación en su interfaz
3. **Pausar sesión**: Para casos de mal funcionamiento crítico

**Uso ético**: Solo intervenir en casos de:
- Bug crítico que afecta la experiencia
- Riesgo de seguridad o privacidad
- Estudiante bloqueado por problema técnico (no pedagógico)

---

## 9. Exportación de Datos

### 9.1 Exportar Datos de UAT

**Acceso**: Dashboard → "Exportar Datos"

**Opciones de export**:

**1. Export Completo (Investigación)**:
```yaml
formato: JSON
incluye:
  - Todas las trazas N4 (anonimizadas)
  - Todos los riesgos detectados
  - Todas las evaluaciones de E-IA-Proc
  - Feedback de usuarios (SUS, satisfacción)
  - Bugs reportados (sin info de infraestructura sensible)
anonimizacion:
  k_anonymity: 5
  hash_salt: "institution_2025_uat"
  suppress_pii: true
tamaño_estimado: 25 MB
```

**2. Export de Métricas (Análisis)**:
```yaml
formato: CSV
incluye:
  - Métricas agregadas por estudiante
  - Evolución de SUS Score
  - Distribución de riesgos
  - Uso de agentes
tamaño_estimado: 500 KB
```

**3. Export de Feedback (Cualitativo)**:
```yaml
formato: Excel (XLSX)
incluye:
  - Comentarios textuales
  - Respuestas a encuestas
  - Bugs con descripciones
  - Sugerencias de mejora
tamaño_estimado: 2 MB
```

### 9.2 Privacidad en Exports

**Garantías GDPR**:
- ✅ k-anonymity ≥5 (cada registro indistinguible de al menos 4 otros)
- ✅ Pseudonimización irreversible (SHA-256 con salt institucional)
- ✅ Supresión de PII (emails, IPs, nombres reales)
- ✅ Generalización temporal (timestamps → semana ISO)

**Validación automática**:
Antes de generar export, el sistema valida:
- No hay emails, teléfonos, o IDs reales
- Tamaño de clases de equivalencia ≥k
- Identificadores hasheados correctamente

---

## 10. Troubleshooting

### 10.1 Problemas Comunes

**"No veo sesiones de un estudiante"**:
- ✅ Verifica que el estudiante haya iniciado sesión al menos una vez
- ✅ Refresca el dashboard (Ctrl+R)
- ✅ Revisa filtros aplicados (por defecto: últimas 24h)

**"Las trazas no se actualizan en tiempo real"**:
- ✅ Verifica que Live View esté activado (ícono 🔴 LIVE debe estar visible)
- ✅ Revisa conexión WebSocket en DevTools → Network → WS
- ✅ Si persiste, recarga la página

**"Exportación falla con error de privacidad"**:
- ✅ Verifica que k-anonymity sea alcanzable (mínimo 5 estudiantes con datos)
- ✅ Aumenta generalización temporal si hay pocos datos
- ✅ Contacta soporte técnico con error code

**"Bug reportado pero no aparece en dashboard"**:
- ✅ Espera 30 segundos (indexación asíncrona)
- ✅ Verifica filtros (por defecto: solo NUEVO y TRIAGED)
- ✅ Busca por ID del bug en barra de búsqueda

### 10.2 Contacto de Soporte Técnico

**Durante UAT**:
- Email: [email soporte técnico]
- Slack: #uat-instructor-support
- Teléfono urgencias: [teléfono]

**Horario**: Lunes a Viernes, 8:00-20:00

---

## 📚 Recursos Adicionales

**Documentación Completa**:
- `UAT_PLAN.md` - Plan completo de UAT
- `student-quick-start.md` - Guía para estudiantes
- `README_MVP.md` - Documentación técnica del sistema

**Videos Tutoriales** (próximamente):
- "Tour del Dashboard de Instructor" (10 min)
- "Análisis de Trazabilidad Cognitiva" (15 min)
- "Gestión de Bugs y Feedback" (8 min)

---

**¡Gracias por tu rol fundamental en la UAT!**

Tu supervisión y análisis son clave para validar la efectividad pedagógica del sistema AI-Native MVP.

---

**Versión**: 1.0
**Última actualización**: 2025-11-24
**Contacto**: Mag. Alberto Cortez - [email]