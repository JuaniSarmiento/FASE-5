# Historias de Usuario - Ecosistema AI-Native para Programación

## Información del Proyecto

**Proyecto**: Ecosistema AI-Native para Enseñanza-Aprendizaje de Programación
**Tipo**: MVP (Minimum Viable Product) - Tesis Doctoral
**Autor**: Mag. en Ing. de Software Alberto Cortez
**Fecha**: Noviembre 2025
**Versión**: 1.0

---

## Índice

1. [Roles y Actores](#roles-y-actores)
2. [Product Backlog](#product-backlog)
3. [Épicas](#épicas)
4. [Historias de Usuario por Rol](#historias-de-usuario-por-rol)
   - [Estudiante](#estudiante)
   - [Docente](#docente)
   - [Administrador Institucional](#administrador-institucional)
   - [Sistema (Historias Técnicas)](#sistema-historias-técnicas)
5. [Criterios de Aceptación Generales](#criterios-de-aceptación-generales)
6. [Definición de Done (DoD)](#definición-de-done-dod)

---

## Roles y Actores

### Roles Primarios

| Rol | Descripción | Responsabilidades |
|-----|-------------|-------------------|
| **Estudiante** | Alumno de programación que aprende con asistencia de IA | Resolver actividades, interactuar con IA, documentar razonamiento, autorregular aprendizaje |
| **Docente** | Profesor que supervisa y evalúa el proceso de aprendizaje | Diseñar actividades, analizar trazas cognitivas, evaluar procesos, intervenir pedagógicamente |
| **Administrador Institucional** | Responsable de gobernanza y políticas de IA | Configurar políticas, auditar uso de IA, generar reportes institucionales, gestionar riesgos |

### Roles Secundarios

| Rol | Descripción |
|-----|-------------|
| **Desarrollador/Integrador** | Técnico que integra el sistema con LMS (Moodle, Canvas) |
| **Auditor Externo** | Organismo de acreditación (CONEAU, etc.) que verifica cumplimiento normativo |

### Agentes del Sistema (No-humanos)

| Agente | Código | Descripción |
|--------|--------|-------------|
| **Tutor Cognitivo** | T-IA-Cog | Guía el razonamiento sin sustituir agencia cognitiva |
| **Evaluador de Procesos** | E-IA-Proc | Analiza y evalúa procesos cognitivos híbridos humano-IA |
| **Simuladores Profesionales** | S-IA-X | Recrean roles de la industria (PO, SM, entrevistador, etc.) |
| **Analista de Riesgos** | AR-IA | Detecta riesgos cognitivos, éticos, epistémicos y técnicos |
| **Gobernanza Institucional** | GOV-IA | Verifica cumplimiento de políticas y normativas |
| **Trazabilidad Cognitiva N4** | TC-N4 | Captura proceso cognitivo completo (4 niveles) |

---

## Product Backlog

### Priorización (Método MoSCoW)

#### Must Have (Esencial para MVP)
- Interacción básica estudiante-IA con trazabilidad N4
- Tutor cognitivo con bloqueo de delegación total
- Captura de trazas cognitivas (N3 y N4)
- Evaluación de procesos cognitivos
- Análisis de riesgos básico
- Políticas de gobernanza operativas

#### Should Have (Importante, no crítico)
- API REST completa
- Simuladores profesionales completos
- Dashboard docente con visualizaciones
- Integración Git para trazabilidad N2
- Reportes institucionales avanzados

#### Could Have (Deseable)
- Integración LTI con Moodle
- Múltiples proveedores LLM (OpenAI, Anthropic, local)
- Análisis predictivo de abandono
- Gamificación y badges

#### Won't Have (Fuera del alcance MVP)
- Integración con sistemas ERP institucionales
- Machine learning sobre patrones de aprendizaje
- Aplicación móvil nativa
- Internacionalización (i18n)

---

## Épicas

### Épica 1: Interacción Estudiante-IA con Trazabilidad
**Objetivo**: Permitir que estudiantes interactúen con IA de manera pedagógicamente supervisada, capturando todo el proceso cognitivo.

**Valor de Negocio**: Transformar la programación asistida por IA en una experiencia formativa verificable y evaluable.

**Historias Asociadas**: HU-EST-001 a HU-EST-008

---

### Épica 2: Evaluación de Procesos (No Productos)
**Objetivo**: Evaluar el razonamiento y las decisiones del estudiante, no solo el código final.

**Valor de Negocio**: Evidencia válida de aprendizaje en era de IA generativa.

**Historias Asociadas**: HU-DOC-001, HU-DOC-002, HU-DOC-005

---

### Épica 3: Gobernanza y Gestión de Riesgos
**Objetivo**: Operativizar políticas institucionales de uso ético y responsable de IA.

**Valor de Negocio**: Cumplimiento normativo (UNESCO, OECD, ISO/IEC 23894) y acreditación universitaria.

**Historias Asociadas**: HU-ADM-001 a HU-ADM-005

---

### Épica 4: Simulación de Roles Profesionales
**Objetivo**: Recrear escenarios auténticos de la industria del software.

**Valor de Negocio**: Competencias transversales y aprendizaje situado.

**Historias Asociadas**: HU-EST-009 a HU-EST-014

---

## Historias de Usuario por Rol

---

## ESTUDIANTE

### HU-EST-001: Iniciar Sesión de Aprendizaje con IA
**Como** estudiante de programación
**Quiero** iniciar una sesión de trabajo con el tutor IA cognitivo
**Para** resolver una actividad práctica con asistencia pedagógica supervisada

**Criterios de Aceptación**:
1. ✅ El sistema me permite crear una sesión especificando:
   - Mi ID de estudiante
   - ID de la actividad (ej: "prog2_tp1_colas")
   - Modo de trabajo (TUTOR, SIMULADOR, EVALUADOR)
2. ✅ El sistema genera un `session_id` único
3. ✅ La sesión queda registrada en la base de datos con timestamp de inicio
4. ✅ El sistema me confirma la creación con mensaje claro
5. ✅ Puedo ver qué agente AI está activo (T-IA-Cog, S-IA-X, etc.)

**Prioridad**: CRÍTICA
**Estimación**: 3 Story Points
**Sprint**: 1
**Dependencias**: Ninguna

**Notas Técnicas**:
- Endpoint API: `POST /api/v1/sessions`
- CLI: `python -m ai_native_mvp` → opción crear sesión
- Database: Registro en `SessionDB` con status `ACTIVE`

**Definición de Done**:
- [ ] Código implementado y revisado
- [ ] Tests unitarios pasando (cobertura >70%)
- [ ] Endpoint API documentado en Swagger
- [ ] Ejemplo CLI funcional
- [ ] Trazabilidad N4 capturando inicio de sesión

---

### HU-EST-002: Consultar Conceptos sin Recibir Código Completo
**Como** estudiante
**Quiero** hacer preguntas conceptuales al tutor IA
**Para** comprender fundamentos sin delegar la resolución del problema

**Descripción Detallada**:
El estudiante necesita aclarar conceptos (ej: "¿Qué es una cola circular?") sin que la IA le entregue código completo. El tutor debe responder con explicaciones conceptuales, ejemplos didácticos y preguntas socráticas que promuevan el razonamiento.

**Criterios de Aceptación**:
1. ✅ Cuando pregunto un concepto (sin pedir código), el tutor responde con:
   - Explicación conceptual clara
   - Analogías o ejemplos del mundo real
   - Preguntas que me ayuden a reflexionar
2. ✅ El tutor NO me entrega código completo ni soluciones directas
3. ✅ El tutor clasifica mi solicitud como "consulta conceptual" (no delegación)
4. ✅ La interacción se captura en una traza N4 con:
   - Mi pregunta original
   - Estado cognitivo detectado: "EXPLORACION_CONCEPTUAL"
   - Nivel de involucramiento de IA: bajo (0.2-0.3)
   - Intención cognitiva: "UNDERSTANDING"
5. ✅ El sistema NO bloquea la interacción (no es delegación total)

**Ejemplos**:

**Ejemplo 1 - Pregunta Válida**:
```
Estudiante: "¿Qué es una cola circular y en qué se diferencia de una cola simple?"

Tutor: "Excelente pregunta. Empecemos por lo fundamental:

Una **cola** es una estructura de datos que sigue el principio FIFO (First In, First Out):
el primer elemento en entrar es el primer elemento en salir, como una fila en un banco.

Una **cola circular** resuelve un problema específico de las colas implementadas con
arreglos estáticos: el desperdicio de espacio. Cuando hacés dequeue() en una cola simple,
el espacio al inicio del arreglo queda inutilizable.

Antes de continuar, responde esto:
1. ¿Por qué crees que se llama "circular"?
2. ¿Qué operaciones básicas debería tener una cola?
3. ¿Qué ventajas tendría reutilizar el espacio liberado?"

Estado capturado:
- cognitive_state: EXPLORACION_CONCEPTUAL
- ai_involvement: 0.3
- blocked: false
```

**Ejemplo 2 - Delegación Detectada (Bloqueada)**:
```
Estudiante: "Dame el código completo de una cola circular con arreglos"

Tutor: "❌ BLOQUEADO

He detectado que tu solicitud implica una delegación total del problema.
Para ayudarte efectivamente, necesito que:

1. Expliques tu comprensión actual del problema
2. Descompongas el problema en partes más pequeñas
3. Compartas tu plan o boceto inicial
4. Identifiques qué parte específica te genera dificultad

¿Por dónde querés empezar?"

Estado capturado:
- cognitive_state: DELEGACION_TOTAL
- ai_involvement: 1.0
- blocked: true
- risk_detected: COGNITIVE_DELEGATION (HIGH)
```

**Prioridad**: CRÍTICA
**Estimación**: 5 Story Points
**Sprint**: 1
**Dependencias**: HU-EST-001, HU-SYS-001 (CRPE)

**Notas Técnicas**:
- Componente: `TutorCognitivoAgent` (tutor.py)
- Modo: `TutorMode.EXPLICATIVO`
- CRPE debe detectar `request_type: conceptual_query`
- Captura: Traza N4 con `interaction_type: STUDENT_PROMPT`

---

### HU-EST-003: Recibir Bloqueo Pedagógico al Intentar Delegación Total
**Como** estudiante
**Quiero** que el sistema me bloquee cuando intento delegar completamente el problema a la IA
**Para** desarrollar autonomía cognitiva y no caer en dependencia pasiva de la IA

**Descripción Detallada**:
Cuando el estudiante solicita que la IA resuelva todo el problema (ej: "Dame el código completo", "Resolvelo vos"), el componente GOV-IA debe bloquearlo en tiempo real y redirigirlo hacia un proceso de descomposición del problema.

**Criterios de Aceptación**:
1. ✅ Cuando mi solicitud implica delegación total, el sistema:
   - Bloquea la generación de código completo
   - Me muestra un mensaje pedagógico explicando POR QUÉ fue bloqueado
   - Me guía a descomponer el problema
2. ✅ El bloqueo ocurre ANTES de que la IA genere código
3. ✅ El sistema captura una traza N4 con:
   - `blocked: true`
   - `governance_action: DELEGATION_BLOCKED`
   - Riesgo detectado: `COGNITIVE_DELEGATION` (nivel HIGH)
4. ✅ El sistema me ofrece preguntas guía para iniciar la descomposición
5. ✅ La interacción bloqueada cuenta para el análisis de riesgos

**Patrones de Delegación Detectados**:
- "Dame el código completo"
- "Resolvelo vos"
- "Haceme la implementación"
- "Necesito el programa terminado"
- "Escribí todo el código"

**Prioridad**: CRÍTICA
**Estimación**: 8 Story Points
**Sprint**: 1
**Dependencias**: HU-SYS-002 (GOV-IA), HU-SYS-005 (AR-IA)

**Definición de Done**:
- [ ] Lógica de detección de delegación implementada
- [ ] Patrones de delegación configurables
- [ ] Tests para cada patrón de delegación
- [ ] Mensaje pedagógico claro y formativo
- [ ] Traza N4 capturando bloqueo
- [ ] Riesgo registrado en RiskDB

---

### HU-EST-004: Solicitar Pistas Graduadas sin Perder Desafío Cognitivo
**Como** estudiante
**Quiero** pedir ayuda específica en una parte del problema que no comprendo
**Para** recibir orientación sin que me den la solución completa

**Descripción Detallada**:
El estudiante puede solicitar ayuda en aspectos específicos (ej: "¿Cómo gestiono el caso cuando el arreglo está lleno?"). El tutor debe dar pistas graduadas que preserven el desafío cognitivo.

**Criterios de Aceptación**:
1. ✅ Cuando pido ayuda específica (no delegación), el tutor:
   - Identifica la parte del problema que me genera dificultad
   - Me da una pista general primero (nivel BAJO)
   - Si pido más ayuda, escala gradualmente (nivel MEDIO)
   - NUNCA me da la solución completa
2. ✅ Las pistas son progresivas:
   - **Nivel 1 (Bajo)**: Pregunta socrática ("¿Qué pasa cuando front == rear?")
   - **Nivel 2 (Medio)**: Pista conceptual ("Considerá usar el operador módulo")
   - **Nivel 3 (Alto)**: Fragmento conceptual ("Un índice circular se logra con: (indice + 1) % tam")
3. ✅ El tutor ajusta el nivel según mi historial (si he recibido muchas pistas, reduce el detalle)
4. ✅ Cada pista se captura en traza N4 con:
   - Nivel de pista otorgado
   - Parte específica del problema consultada
   - `ai_involvement`: incrementa con cada pista (0.3 → 0.5 → 0.7)

**Ejemplo de Escalado de Pistas**:
```
Estudiante: "No entiendo cómo saber si la cola está llena"

Tutor (Nivel 1 - Pregunta):
"¿Qué relación existe entre los índices 'front' y 'rear' cuando la cola está llena?
Pensá en un arreglo de tamaño 5: ¿en qué posiciones están front y rear cuando
ya insertaste 5 elementos?"

[Si el estudiante pide más ayuda]

Tutor (Nivel 2 - Pista Conceptual):
"Hay dos condiciones que indican cola llena en implementación circular:
1. Los índices se 'alcanzan' de cierta manera
2. Necesitás distinguir entre cola vacía y cola llena (ambas pueden tener front == rear)

Algunas implementaciones usan un contador, otras dejan un espacio vacío.
¿Cuál te parece más simple de implementar?"

[Si el estudiante pide más ayuda]

Tutor (Nivel 3 - Fragmento Conceptual):
"Una estrategia común es:
- Cola llena cuando: (rear + 1) % capacidad == front
- Esto deja un espacio sin usar, pero simplifica la lógica

Otra estrategia usa un contador:
- Cola llena cuando: contador == capacidad

¿Cuál estrategia querés implementar? Justificá tu elección."
```

**Prioridad**: ALTA
**Estimación**: 8 Story Points
**Sprint**: 2
**Dependencias**: HU-EST-002

---

### HU-EST-005: Justificar Decisiones de Diseño con Trazabilidad N4
**Como** estudiante
**Quiero** documentar POR QUÉ tomé cada decisión de diseño
**Para** que mi razonamiento quede registrado y sea evaluable (no solo el código final)

**Descripción Detallada**:
El sistema debe exigir (o al menos capturar) las justificaciones del estudiante para decisiones clave. Esto convierte el "proceso invisible" de razonamiento en "proceso auditable".

**Criterios de Aceptación**:
1. ✅ En puntos clave de decisión, el tutor me pregunta:
   - "¿Por qué elegiste esta estructura de datos?"
   - "¿Qué alternativas consideraste?"
   - "¿Qué ventajas/desventajas tiene tu enfoque?"
2. ✅ Mis justificaciones se capturan en trazas N4 con:
   - `cognitive_intent: JUSTIFICATION`
   - Alternativas consideradas
   - Decisión final tomada
   - Razonamiento explicitado
3. ✅ El sistema puede detectar falta de justificación y emitir riesgo:
   - `risk_type: LACK_JUSTIFICATION` (nivel MEDIUM)
   - Recomendación: "Exigir justificaciones explícitas"
4. ✅ Las justificaciones alimentan la evaluación de procesos (E-IA-Proc)

**Ejemplo de Captura de Justificación**:
```
Tutor: "Veo que decidiste implementar la cola con un arreglo circular.
¿Por qué elegiste esta estructura en lugar de una lista enlazada?"

Estudiante: "Elegí arreglo porque:
1. Las colas tienen tamaño máximo predefinido en este TP
2. El acceso por índice es O(1) vs O(n) en listas enlazadas
3. No necesito gestionar nodos dinámicamente
4. La implementación circular evita desperdiciar espacio"

Traza N4 capturada:
{
  "cognitive_intent": "JUSTIFICATION",
  "decision": "Arreglo circular vs lista enlazada",
  "chosen_alternative": "Arreglo circular",
  "alternatives_considered": ["Lista enlazada", "Arreglo simple"],
  "reasoning": "Tamaño fijo, acceso O(1), no gestión dinámica, eficiencia espacial",
  "timestamp": "2025-11-18T10:30:45Z"
}
```

**Prioridad**: ALTA
**Estimación**: 5 Story Points
**Sprint**: 2
**Dependencias**: HU-SYS-003 (TC-N4)

---

### HU-EST-006: Ver Mi Camino Cognitivo Reconstructido
**Como** estudiante
**Quiero** visualizar mi trayectoria de razonamiento durante la sesión
**Para** reflexionar sobre mi proceso (metacognición) y mejorar mis estrategias

**Descripción Detallada**:
Al finalizar la sesión, el estudiante puede ver una reconstrucción visual de su camino cognitivo: qué estados cognitivos atravesó, dónde pidió ayuda, qué riesgos tuvo, cómo evolucionó su dependencia de la IA.

**Criterios de Aceptación**:
1. ✅ Puedo solicitar mi "Camino Cognitivo" al final de la sesión
2. ✅ El sistema me muestra:
   - Secuencia de estados cognitivos (exploración → planificación → implementación → validación)
   - Transiciones entre estados con timestamps
   - Puntos donde solicité ayuda (con nivel de pista)
   - Riesgos detectados en cada fase
   - Evolución de dependencia de IA (gráfico 0-100%)
3. ✅ El camino incluye:
   - Total de interacciones: N
   - Interacciones bloqueadas: M
   - Dependencia promedio de IA: X%
   - Cambios de estrategia: K
4. ✅ Puedo exportar mi camino en formato JSON o PDF

**Ejemplo de Salida**:
```
========================================
CAMINO COGNITIVO - Sesión: prog2_tp1_colas
Estudiante: estudiante_001
Duración: 45 minutos
========================================

Fase 1: EXPLORACION_CONCEPTUAL (10:00 - 10:15)
  └─ Interacciones: 3
  └─ Consultas: "¿Qué es cola circular?", "¿Diferencia con cola simple?"
  └─ AI Involvement: 25%
  └─ Riesgos: Ninguno

Fase 2: PLANIFICACION (10:15 - 10:25)
  └─ Interacciones: 2
  └─ Decisión: Arreglo circular (justificado)
  └─ AI Involvement: 30%
  └─ Riesgos: Ninguno

Fase 3: IMPLEMENTACION (10:25 - 10:40)
  └─ Interacciones: 5
  └─ Pistas solicitadas: 2 (nivel MEDIO)
  └─ AI Involvement: 55%
  └─ ⚠️ Riesgo: LACK_JUSTIFICATION (MEDIUM) - No justificó manejo de cola llena

Fase 4: VALIDACION (10:40 - 10:45)
  └─ Interacciones: 2
  └─ Tests implementados: 3
  └─ AI Involvement: 20%
  └─ Riesgos: Ninguno

RESUMEN:
✅ Competencia alcanzada: EN_DESARROLLO (6/10)
📊 Dependencia IA promedio: 32.5%
🔄 Cambios de estrategia: 1
⚠️ Riesgos totales: 1 (medio)
```

**Prioridad**: MEDIA
**Estimación**: 8 Story Points
**Sprint**: 3
**Dependencias**: HU-SYS-003 (TC-N4), HU-DOC-002

---

### HU-EST-007: Recibir Retroalimentación Formativa al Final de la Sesión
**Como** estudiante
**Quiero** recibir un reporte de evaluación formativa al cerrar mi sesión
**Para** comprender qué hice bien, qué debo mejorar y cómo evolucionar mi proceso

**Criterios de Aceptación**:
1. ✅ Al cerrar la sesión, el agente E-IA-Proc genera un reporte con:
   - Nivel de competencia alcanzado (INICIAL, EN_DESARROLLO, COMPETENTE, EXPERTO)
   - Puntuación por dimensiones:
     - Descomposición de problemas
     - Autorregulación y metacognición
     - Coherencia lógica
     - Verificación y testing
     - Documentación de decisiones
   - Fortalezas identificadas
   - Áreas de mejora concretas
2. ✅ El reporte es formativo (no punitivo): enfocado en el crecimiento
3. ✅ El reporte incluye recomendaciones accionables
4. ✅ El reporte queda almacenado y accesible posteriormente

**Ejemplo de Reporte**:
```
========================================
EVALUACIÓN FORMATIVA DE PROCESO
========================================
Estudiante: estudiante_001
Actividad: prog2_tp1_colas
Fecha: 2025-11-18
Duración: 45 minutos

NIVEL ALCANZADO: EN_DESARROLLO (6.0/10)

DIMENSIONES EVALUADAS:
├─ Descomposición de Problemas: 8/10 (COMPETENTE)
│  └─ Fortaleza: Dividiste el problema en partes manejables
├─ Autorregulación y Metacognición: 4/10 (EN_DESARROLLO)
│  └─ Mejora: Poca reflexión sobre errores cometidos
├─ Coherencia Lógica: 6/10 (EN_DESARROLLO)
│  └─ Mejora: Algunas decisiones de diseño sin justificar
├─ Verificación y Testing: 7/10 (COMPETENTE)
│  └─ Fortaleza: Creaste tests para casos límite
└─ Documentación: 5/10 (EN_DESARROLLO)
   └─ Mejora: Faltó documentar alternativas consideradas

FORTALEZAS PRINCIPALES:
✅ Buena planificación inicial
✅ Uso equilibrado de ayuda de IA (32% - óptimo)
✅ Implementaste tests sin que se te solicitara

ÁREAS DE MEJORA:
⚠️ Autorregulación: Reflexioná explícitamente sobre errores
⚠️ Justificación: Documentá POR QUÉ tomás cada decisión
⚠️ Alternativas: Considerá explícitamente otras opciones antes de decidir

RECOMENDACIONES ACCIONABLES:
1. Antes de implementar, escribí 2-3 alternativas y justificá tu elección
2. Al encontrar un error, preguntate: "¿Por qué falló? ¿Qué aprendí?"
3. Al pedir ayuda a la IA, primero intentá formular tu hipótesis

RIESGOS DETECTADOS:
⚠️ 1 riesgo medio: LACK_JUSTIFICATION
   └─ Recomendación: En próximas sesiones, justificá cada decisión clave

PRÓXIMOS PASOS:
→ Practicá con pilas (similar a colas) aplicando justificaciones explícitas
→ Enfocate en autorregulación: preguntate "¿qué aprendí?" al final
```

**Prioridad**: ALTA
**Estimación**: 13 Story Points
**Sprint**: 2
**Dependencias**: HU-SYS-004 (E-IA-Proc)

---

### HU-EST-008: Consultar Historial de Sesiones Previas
**Como** estudiante
**Quiero** ver el historial de mis sesiones anteriores con sus evaluaciones
**Para** monitorear mi progreso a lo largo del tiempo

**Criterios de Aceptación**:
1. ✅ Puedo listar todas mis sesiones previas con:
   - Fecha y duración
   - Actividad realizada
   - Nivel de competencia alcanzado
   - Dependencia de IA promedio
   - Riesgos detectados
2. ✅ Puedo filtrar por:
   - Rango de fechas
   - Actividad específica
   - Nivel de competencia
3. ✅ Puedo ver la evolución de mi dependencia de IA en gráfico temporal
4. ✅ Puedo acceder al detalle completo de cualquier sesión pasada

**Prioridad**: BAJA
**Estimación**: 5 Story Points
**Sprint**: 4
**Dependencias**: HU-EST-007

---

### HU-EST-009: Interactuar con Product Owner Simulado (PO-IA)
**Como** estudiante
**Quiero** presentar mi propuesta técnica a un Product Owner simulado
**Para** desarrollar habilidades de comunicación técnica y justificación de decisiones

**Descripción Detallada**:
El simulador PO-IA cuestiona decisiones técnicas, pide criterios de aceptación, analiza trade-offs y simula priorización de backlog. El estudiante debe justificar técnicamente sus elecciones.

**Criterios de Aceptación**:
1. ✅ Puedo activar el modo "PRODUCT_OWNER" en mi sesión
2. ✅ El PO-IA me hace preguntas típicas de negocio:
   - "¿Cuáles son los criterios de aceptación?"
   - "¿Qué alternativas consideraste?"
   - "¿Cuál es el impacto de esta decisión en el usuario final?"
   - "¿Por qué priorizaste X sobre Y?"
3. ✅ El PO-IA evalúa:
   - Claridad en la comunicación técnica
   - Capacidad de traducir términos técnicos a lenguaje de negocio
   - Justificación de decisiones con criterios objetivos
4. ✅ La interacción se captura como traza N4 con competencias evaluadas

**Prioridad**: MEDIA
**Estimación**: 8 Story Points
**Sprint**: 3
**Dependencias**: HU-SYS-006 (S-IA-X)

---

### HU-EST-010: Participar en Daily Scrum Simulado (SM-IA)
**Como** estudiante
**Quiero** reportar mi progreso a un Scrum Master simulado
**Para** practicar gestión ágil y comunicación de impedimentos

**Criterios de Aceptación**:
1. ✅ El SM-IA me pregunta las 3 preguntas del daily:
   - "¿Qué hiciste ayer?"
   - "¿Qué vas a hacer hoy?"
   - "¿Hay algún impedimento?"
2. ✅ El SM-IA detecta desviaciones en estimaciones y pregunta causas
3. ✅ El SM-IA me ayuda a identificar y documentar impedimentos

**Prioridad**: BAJA
**Estimación**: 5 Story Points
**Sprint**: 4
**Dependencias**: HU-SYS-006 (S-IA-X)

---

### HU-EST-011: Enfrentar Entrevista Técnica Simulada (IT-IA)
**Como** estudiante
**Quiero** ser entrevistado por un entrevistador técnico simulado
**Para** prepararme para procesos de selección reales

**Criterios de Aceptación**:
1. ✅ El IT-IA me hace preguntas técnicas progresivas:
   - Conceptuales ("Explicá qué es polimorfismo")
   - Algorítmicas ("¿Cómo invertirías una lista enlazada?")
   - De diseño ("¿Cómo diseñarías un sistema de caché?")
2. ✅ El IT-IA evalúa:
   - Claridad en la explicación
   - Capacidad de razonar en voz alta
   - Manejo de presión y preguntas desafiantes
3. ✅ Al finalizar, recibo feedback específico de la entrevista

**Prioridad**: BAJA
**Estimación**: 13 Story Points
**Sprint**: 5
**Dependencias**: HU-SYS-006 (S-IA-X)

---

### HU-EST-012: Responder Incidente en Producción (IR-IA)
**Como** estudiante
**Quiero** gestionar un incidente simulado en producción
**Para** desarrollar habilidades DevOps y manejo de presión

**Criterios de Aceptación**:
1. ✅ El IR-IA simula un incidente real:
   - "La API está retornando 500 en el 30% de requests"
   - "El tiempo de respuesta subió de 200ms a 5s"
2. ✅ Debo diagnosticar, proponer solución y documentar
3. ✅ El IR-IA evalúa:
   - Proceso de diagnóstico sistemático
   - Priorización (¿qué hacer primero?)
   - Documentación post-mortem

**Prioridad**: BAJA
**Estimación**: 13 Story Points
**Sprint**: 6
**Dependencias**: HU-SYS-006 (S-IA-X)

---

### HU-EST-013: Comunicarse con Cliente Simulado (CX-IA)
**Como** estudiante
**Quiero** negociar requisitos con un cliente simulado
**Para** desarrollar habilidades de elicitación y gestión de expectativas

**Criterios de Aceptación**:
1. ✅ El CX-IA presenta requisitos ambiguos o contradictorios
2. ✅ Debo hacer preguntas para clarificar
3. ✅ Debo negociar prioridades y plazos
4. ✅ El CX-IA evalúa soft skills: empatía, claridad, profesionalismo

**Prioridad**: BAJA
**Estimación**: 8 Story Points
**Sprint**: 5
**Dependencias**: HU-SYS-006 (S-IA-X)

---

### HU-EST-014: Auditar Seguridad con DevSecOps Simulado (DSO-IA)
**Como** estudiante
**Quiero** que mi código sea auditado por un agente DevSecOps
**Para** identificar vulnerabilidades y malas prácticas de seguridad

**Criterios de Aceptación**:
1. ✅ El DSO-IA analiza mi código en busca de:
   - Vulnerabilidades (SQL injection, XSS, etc.)
   - Secretos hardcodeados
   - Dependencias con CVEs conocidos
2. ✅ El DSO-IA genera un reporte de seguridad
3. ✅ Debo corregir las vulnerabilidades y justificar las correcciones

**Prioridad**: MEDIA
**Estimación**: 13 Story Points
**Sprint**: 4
**Dependencias**: HU-SYS-006 (S-IA-X)

---

## DOCENTE

### HU-DOC-001: Diseñar Actividad AI-Native con Políticas Configurables
**Como** docente
**Quiero** crear una actividad de programación asistida por IA configurando políticas pedagógicas
**Para** adaptar el nivel de ayuda permitido según objetivos de aprendizaje

**Descripción Detallada**:
El docente define actividades (ej: "Implementar cola con arreglos") y configura:
- Nivel máximo de ayuda permitido (MINIMO, BAJO, MEDIO, ALTO)
- Si se permite código parcial o solo orientación conceptual
- Qué competencias se evaluarán
- Umbrales de riesgo que disparan alertas

**Criterios de Aceptación**:
1. ✅ Puedo crear una actividad especificando:
   - ID único (ej: "prog2_tp1_colas")
   - Título y descripción
   - Consigna detallada
   - Criterios de evaluación
2. ✅ Puedo configurar políticas:
   ```json
   {
     "max_help_level": "MEDIO",
     "block_complete_solutions": true,
     "require_justification": true,
     "allow_code_snippets": false,
     "risk_thresholds": {
       "ai_dependency": 0.6,
       "lack_justification": 0.3
     }
   }
   ```
3. ✅ Las políticas se aplican automáticamente a todos los estudiantes en esa actividad
4. ✅ Puedo clonar actividades previas y modificar políticas

**Prioridad**: ALTA
**Estimación**: 13 Story Points
**Sprint**: 2
**Dependencias**: HU-SYS-002 (GOV-IA)

---

### HU-DOC-002: Visualizar Trazas Cognitivas de un Estudiante
**Como** docente
**Quiero** ver las trazas N4 completas de un estudiante en una actividad
**Para** comprender su proceso de razonamiento y toma de decisiones

**Criterios de Aceptación**:
1. ✅ Puedo seleccionar un estudiante y una sesión
2. ✅ El sistema me muestra:
   - Timeline completo de interacciones
   - Prompts enviados a la IA
   - Respuestas recibidas
   - Decisiones tomadas y justificaciones
   - Estados cognitivos atravesados
   - Riesgos detectados en cada punto
3. ✅ Puedo filtrar trazas por:
   - Tipo de interacción (pregunta conceptual, solicitud de código, validación)
   - Nivel de riesgo
   - Estado cognitivo
4. ✅ Puedo exportar las trazas en formato JSON o PDF

**Prioridad**: CRÍTICA
**Estimación**: 13 Story Points
**Sprint**: 3
**Dependencias**: HU-SYS-003 (TC-N4)

---

### HU-DOC-003: Comparar Procesos Cognitivos de Múltiples Estudiantes
**Como** docente
**Quiero** comparar los caminos cognitivos de diferentes estudiantes en la misma actividad
**Para** identificar patrones, dificultades comunes y estrategias exitosas

**Criterios de Aceptación**:
1. ✅ Puedo seleccionar una actividad
2. ✅ El sistema me muestra comparativa de todos los estudiantes:
   - Tiempo promedio de resolución
   - Dependencia promedio de IA
   - Cantidad de pistas solicitadas
   - Riesgos más frecuentes
   - Estrategias de resolución (agrupadas)
3. ✅ Puedo ver outliers:
   - Estudiantes con dependencia muy alta (>80%)
   - Estudiantes con múltiples riesgos críticos
   - Estudiantes con tiempos excesivos
4. ✅ Puedo agrupar por patrones de resolución

**Prioridad**: ALTA
**Estimación**: 13 Story Points
**Sprint**: 4
**Dependencias**: HU-DOC-002

---

### HU-DOC-004: Intervenir Pedagógicamente en Tiempo Real
**Como** docente
**Quiero** recibir alertas cuando un estudiante tiene dificultades o riesgos críticos
**Para** intervenir pedagógicamente antes de que se frustre o abandone

**Criterios de Aceptación**:
1. ✅ Recibo notificación en tiempo real cuando:
   - Un estudiante acumula 3+ riesgos medios
   - Un estudiante tiene 1+ riesgo crítico
   - Un estudiante lleva >2 horas en la misma fase
   - Un estudiante tiene dependencia de IA >85%
2. ✅ La alerta incluye:
   - Nombre del estudiante
   - Actividad en curso
   - Riesgos específicos detectados
   - Sugerencias de intervención
3. ✅ Puedo enviar mensaje directo al estudiante desde la alerta
4. ✅ Puedo marcar la alerta como "atendida"

**Prioridad**: ALTA
**Estimación**: 8 Story Points
**Sprint**: 3
**Dependencias**: HU-SYS-005 (AR-IA)

---

### HU-DOC-005: Evaluar Proceso Cognitivo (No Solo Producto)
**Como** docente
**Quiero** evaluar el proceso de razonamiento del estudiante además del código final
**Para** asignar calificaciones que reflejen comprensión real, no solo producto

**Descripción Detallada**:
El docente revisa el reporte de E-IA-Proc, analiza trazas N4, y asigna calificación considerando:
- Descomposición del problema
- Justificación de decisiones
- Manejo de errores y autocorrección
- Nivel de dependencia de IA
- Coherencia del proceso

**Criterios de Aceptación**:
1. ✅ Accedo al reporte de evaluación automática (E-IA-Proc)
2. ✅ El reporte me sugiere:
   - Nivel de competencia alcanzado (INICIAL, EN_DESARROLLO, COMPETENTE, EXPERTO)
   - Puntuación sugerida (0-10)
   - Dimensiones evaluadas con puntajes
3. ✅ Puedo:
   - Aceptar la evaluación sugerida
   - Ajustar puntajes por dimensión
   - Agregar comentarios cualitativos
   - Marcar para revisión (si hay inconsistencias)
4. ✅ La calificación final se compone de:
   - 40%: Producto final (código funcional, eficiente, bien documentado)
   - 60%: Proceso cognitivo (razonamiento, decisiones, autonomía)

**Prioridad**: CRÍTICA
**Estimación**: 13 Story Points
**Sprint**: 3
**Dependencias**: HU-SYS-004 (E-IA-Proc), HU-DOC-002

---

### HU-DOC-006: Generar Reporte de Curso Completo
**Como** docente
**Quiero** generar un reporte consolidado de todos los estudiantes del curso
**Para** identificar tendencias, ajustar la didáctica y reportar a la institución

**Criterios de Aceptación**:
1. ✅ Puedo generar reporte del curso con:
   - Estadísticas generales (promedio de competencia, tasa de aprobación)
   - Distribución de niveles de competencia
   - Riesgos más frecuentes
   - Actividades con mayor dificultad
   - Uso de IA (dependencia promedio del curso)
2. ✅ El reporte incluye gráficos:
   - Evolución temporal de competencias
   - Distribución de riesgos por tipo
   - Comparativa entre actividades
3. ✅ Puedo exportar en PDF o Excel

**Prioridad**: MEDIA
**Estimación**: 13 Story Points
**Sprint**: 5
**Dependencias**: HU-DOC-005

---

### HU-DOC-007: Configurar Umbrales de Riesgo Personalizados
**Como** docente
**Quiero** configurar qué nivel de dependencia de IA es aceptable para cada actividad
**Para** adaptar las alertas según el nivel del estudiante y la complejidad de la tarea

**Criterios de Aceptación**:
1. ✅ Puedo configurar umbrales por actividad:
   ```json
   {
     "ai_dependency_threshold": 0.5,  // Alertar si >50%
     "justification_required_ratio": 0.7,  // Al menos 70% de decisiones justificadas
     "max_blocked_interactions": 2  // Alertar si >2 bloqueos
   }
   ```
2. ✅ Los umbrales se aplican dinámicamente
3. ✅ Recibo alertas solo cuando se superan umbrales configurados

**Prioridad**: MEDIA
**Estimación**: 5 Story Points
**Sprint**: 4
**Dependencias**: HU-DOC-001, HU-SYS-005

---

## ADMINISTRADOR INSTITUCIONAL

### HU-ADM-001: Configurar Políticas Institucionales de IA
**Como** administrador institucional
**Quiero** definir políticas globales de uso de IA que apliquen a toda la institución
**Para** garantizar cumplimiento de normativas (UNESCO, OECD, ISO/IEC 23894)

**Descripción Detallada**:
El administrador configura políticas institucionales que sobrescriben configuraciones de docentes si es necesario. Ejemplos:
- Prohibir código completo en todos los cursos de nivel inicial
- Exigir trazabilidad N4 en todas las actividades evaluativas
- Limitar dependencia de IA a <60% en trabajos finales

**Criterios de Aceptación**:
1. ✅ Puedo definir políticas globales:
   ```json
   {
     "institution_name": "Universidad XYZ",
     "policies": {
       "max_ai_dependency_global": 0.6,
       "require_n4_traceability": true,
       "block_complete_solutions": true,
       "allowed_llm_providers": ["openai", "anthropic", "local"],
       "data_retention_days": 730,
       "audit_frequency_days": 90
     }
   }
   ```
2. ✅ Las políticas se propagan a todas las actividades
3. ✅ Los docentes pueden ser más restrictivos, pero no más permisivos
4. ✅ Cambios en políticas quedan auditados (quién, cuándo, qué cambió)

**Prioridad**: ALTA
**Estimación**: 13 Story Points
**Sprint**: 2
**Dependencias**: HU-SYS-002 (GOV-IA)

---

### HU-ADM-002: Auditar Uso de IA a Nivel Institucional
**Como** administrador institucional
**Quiero** ver reportes de uso de IA en toda la institución
**Para** demostrar cumplimiento normativo a organismos de acreditación (CONEAU, etc.)

**Criterios de Aceptación**:
1. ✅ Puedo generar reporte institucional con:
   - Total de sesiones registradas
   - Total de estudiantes usando IA
   - Dependencia promedio de IA institucional
   - Riesgos detectados por tipo y severidad
   - Cursos con mayor/menor uso de IA
   - Cumplimiento de políticas (% de conformidad)
2. ✅ Puedo filtrar por:
   - Rango de fechas
   - Facultad/carrera
   - Nivel (inicial, intermedio, avanzado)
3. ✅ El reporte incluye sección de cumplimiento normativo:
   - Trazabilidad: ✅ 100% de actividades con N4
   - Gobernanza: ✅ Políticas aplicadas en 100% de sesiones
   - Riesgos: ⚠️ 2% de sesiones con riesgos críticos
4. ✅ Puedo exportar en formato oficial para CONEAU

**Prioridad**: ALTA
**Estimación**: 13 Story Points
**Sprint**: 4
**Dependencias**: HU-ADM-001, HU-SYS-002

---

### HU-ADM-003: Gestionar Riesgos Críticos Institucionales
**Como** administrador institucional
**Quiero** ver un dashboard de riesgos críticos detectados
**Para** tomar acciones correctivas institucionales

**Criterios de Aceptación**:
1. ✅ Accedo a dashboard de riesgos con:
   - Total de riesgos por severidad (crítico, alto, medio, bajo)
   - Tendencia temporal (¿están aumentando o disminuyendo?)
   - Top 5 riesgos más frecuentes
   - Cursos/docentes con mayor incidencia de riesgos
2. ✅ Puedo drill-down a riesgos específicos:
   - Estudiantes afectados
   - Contexto de cada riesgo
   - Acciones tomadas
3. ✅ Puedo marcar riesgos como:
   - "Resuelto" (con nota de resolución)
   - "En seguimiento"
   - "Escalado a comité de ética"

**Prioridad**: ALTA
**Estimación**: 13 Story Points
**Sprint**: 5
**Dependencias**: HU-SYS-005 (AR-IA)

---

### HU-ADM-004: Configurar Proveedores LLM Permitidos
**Como** administrador institucional
**Quiero** definir qué proveedores de LLM están autorizados
**Para** controlar costos, privacidad de datos y cumplimiento legal

**Criterios de Aceptación**:
1. ✅ Puedo habilitar/deshabilitar proveedores:
   - OpenAI (GPT-4, GPT-3.5)
   - Anthropic (Claude)
   - Modelos locales (Ollama)
2. ✅ Puedo configurar por proveedor:
   - API keys institucionales
   - Límites de uso (requests/día, tokens/mes)
   - Restricciones de privacidad (¿permite almacenar datos?)
3. ✅ Los docentes solo pueden usar proveedores habilitados
4. ✅ El sistema registra costos por proveedor

**Prioridad**: MEDIA
**Estimación**: 8 Story Points
**Sprint**: 3
**Dependencias**: HU-SYS-001 (C1 - Motor LLM)

---

### HU-ADM-005: Exportar Datos para Investigación Institucional
**Como** administrador institucional
**Quiero** exportar datos anonimizados de trazas cognitivas
**Para** investigación educativa y mejora continua del modelo AI-Native

**Criterios de Aceptación**:
1. ✅ Puedo exportar dataset anonimizado con:
   - Trazas N4 (sin IDs de estudiantes)
   - Evaluaciones de procesos
   - Riesgos detectados
   - Patrones de uso de IA
2. ✅ La anonimización es robusta (cumple GDPR/LOPD)
3. ✅ Puedo especificar:
   - Rango de fechas
   - Cursos incluidos
   - Nivel de agregación
4. ✅ Exportación en formatos académicos (CSV, JSON, SPSS)

**Prioridad**: BAJA
**Estimación**: 13 Story Points
**Sprint**: 6
**Dependencias**: HU-SYS-003 (TC-N4)

---

## SISTEMA (Historias Técnicas)

### HU-SYS-001: Motor de Razonamiento Cognitivo-Pedagógico (CRPE)
**Como** sistema
**Quiero** analizar cada prompt del estudiante y clasificarlo cognitivamente
**Para** determinar la estrategia pedagógica apropiada

**Descripción Técnica**:
Componente C3 del AI Gateway. Analiza:
- Tipo de solicitud (conceptual, implementación, debugging, validación)
- Estado cognitivo (exploración, planificación, implementación, reflexión)
- Nivel de delegación (consulta guiada vs delegación total)
- Contexto histórico del estudiante

**Criterios de Aceptación Técnicos**:
1. ✅ Implementado en `src/ai_native_mvp/core/cognitive_engine.py`
2. ✅ Clasifica prompts en <500ms (latencia baja)
3. ✅ Determina:
   - `cognitive_state`: CognitiveState enum
   - `request_type`: RequestType enum
   - `delegation_level`: float (0.0 = consulta, 1.0 = delegación total)
4. ✅ Retorna estrategia pedagógica estructurada:
   ```python
   {
     "response_type": "socratic_questioning",
     "help_level": "MEDIO",
     "requires_justification": true
   }
   ```
5. ✅ Tests unitarios cubren todos los tipos de solicitud
6. ✅ Documentado en README_MVP.md

**Prioridad**: CRÍTICA
**Estimación**: 13 Story Points
**Sprint**: 1

---

### HU-SYS-002: Agente de Gobernanza (GOV-IA)
**Como** sistema
**Quiero** verificar cumplimiento de políticas institucionales antes de procesar cada interacción
**Para** bloquear solicitudes que violan principios pedagógicos o normativos

**Criterios de Aceptación Técnicos**:
1. ✅ Implementado en `src/ai_native_mvp/agents/governance.py`
2. ✅ Carga políticas desde:
   - Configuración global (administrador)
   - Configuración de actividad (docente)
3. ✅ Verifica ANTES de ejecutar:
   - `max_help_level` no excedido
   - `block_complete_solutions` respetado
   - Umbrales de riesgo no superados
4. ✅ Si viola política:
   - Bloquea la solicitud
   - Retorna mensaje pedagógico
   - Registra evento de gobernanza
5. ✅ Componente C4 (GSR) del AI Gateway
6. ✅ Tests para cada tipo de política

**Prioridad**: CRÍTICA
**Estimación**: 13 Story Points
**Sprint**: 1
**Dependencias**: HU-SYS-001

---

### HU-SYS-003: Agente de Trazabilidad Cognitiva N4 (TC-N4)
**Como** sistema
**Quiero** capturar cada interacción en 4 niveles de profundidad
**Para** reconstruir el proceso cognitivo completo

**Descripción Técnica**:
Niveles de trazabilidad:
- **N1**: Archivos finales
- **N2**: Commits Git, branches, tests
- **N3**: Prompts, respuestas IA, logs
- **N4**: Intenciones cognitivas, decisiones, justificaciones, alternativas

**Criterios de Aceptación Técnicos**:
1. ✅ Implementado en `src/ai_native_mvp/agents/traceability.py`
2. ✅ Cada interacción genera `CognitiveTrace` con:
   ```python
   {
     "session_id": str,
     "trace_level": TraceLevel.N4_COGNITIVO,
     "interaction_type": InteractionType.STUDENT_PROMPT,
     "cognitive_state": CognitiveState.PLANIFICACION,
     "cognitive_intent": "JUSTIFICATION",
     "content": "...",
     "ai_involvement": 0.4,
     "metadata": {...}
   }
   ```
3. ✅ Las trazas se persisten en `CognitiveTraceDB`
4. ✅ Forma secuencias (`TraceSequence`) que representan caminos cognitivos
5. ✅ Componente C6 (N4) del AI Gateway
6. ✅ Trazas son inmutables (no se modifican una vez creadas)

**Prioridad**: CRÍTICA
**Estimación**: 13 Story Points
**Sprint**: 1

---

### HU-SYS-004: Agente Evaluador de Procesos (E-IA-Proc)
**Como** sistema
**Quiero** analizar la secuencia completa de trazas N4 al finalizar una sesión
**Para** generar una evaluación del proceso cognitivo (no solo del producto)

**Criterios de Aceptación Técnicos**:
1. ✅ Implementado en `src/ai_native_mvp/agents/evaluator.py`
2. ✅ Analiza:
   - Coherencia del camino cognitivo
   - Calidad de justificaciones
   - Nivel de autorregulación
   - Manejo de errores (autocorrección)
   - Dependencia de IA (¿equilibrada o excesiva?)
3. ✅ Genera `EvaluationReport` con:
   ```python
   {
     "overall_competency_level": "EN_DESARROLLO",
     "overall_score": 6.0,
     "dimensions": {
       "problem_decomposition": 8.0,
       "self_regulation": 4.0,
       "logical_coherence": 6.0
     },
     "key_strengths": [...],
     "improvement_areas": [...]
   }
   ```
4. ✅ El reporte es formativo (no punitivo)
5. ✅ Se dispara automáticamente al cerrar sesión
6. ✅ Persiste en `EvaluationDB`

**Prioridad**: CRÍTICA
**Estimación**: 21 Story Points
**Sprint**: 2
**Dependencias**: HU-SYS-003

---

### HU-SYS-005: Agente Analista de Riesgos (AR-IA)
**Como** sistema
**Quiero** detectar riesgos en cada interacción en 5 dimensiones
**Para** alertar al docente y documentar para gobernanza

**Descripción Técnica**:
Dimensiones de riesgo:
1. **Cognitivo**: Delegación total, dependencia excesiva
2. **Ético**: Integridad académica, plagio
3. **Epistémico**: Aceptación acrítica, errores conceptuales
4. **Técnico**: Vulnerabilidades, código inseguro
5. **Gobernanza**: Violación de políticas

**Criterios de Aceptación Técnicos**:
1. ✅ Implementado en `src/ai_native_mvp/agents/risk_analyst.py`
2. ✅ Analiza en paralelo con cada interacción (no bloquea)
3. ✅ Genera `Risk` cuando detecta patrón problemático:
   ```python
   {
     "risk_type": RiskType.COGNITIVE_DELEGATION,
     "risk_level": RiskLevel.HIGH,
     "dimension": RiskDimension.COGNITIVE,
     "description": "Delegación total detectada",
     "evidence": ["Dame el código completo"],
     "recommendations": ["Exigir descomposición del problema"]
   }
   ```
4. ✅ Riesgos persisten en `RiskDB`
5. ✅ Riesgos críticos disparan alertas en tiempo real
6. ✅ Tests para cada tipo de riesgo

**Prioridad**: ALTA
**Estimación**: 13 Story Points
**Sprint**: 2
**Dependencias**: HU-SYS-003

---

### HU-SYS-006: Agente Simuladores Profesionales (S-IA-X)
**Como** sistema
**Quiero** simular 6 roles profesionales de la industria del software
**Para** ofrecer aprendizaje situado y competencias transversales

**Descripción Técnica**:
Simuladores implementados:
- **PO-IA**: Product Owner (requisitos, priorización)
- **SM-IA**: Scrum Master (daily, impedimentos)
- **IT-IA**: Technical Interviewer (entrevistas técnicas)
- **IR-IA**: Incident Responder (DevOps, troubleshooting)
- **CX-IA**: Client (requisitos ambiguos, negociación)
- **DSO-IA**: DevSecOps (seguridad, auditoría)

**Criterios de Aceptación Técnicos**:
1. ✅ Implementado en `src/ai_native_mvp/agents/simulators.py`
2. ✅ Cada simulador tiene:
   - Contexto específico del rol
   - Preguntas típicas del rol
   - Evaluación de competencias asociadas
3. ✅ El estudiante puede cambiar de simulador en una sesión
4. ✅ Las interacciones se capturan como trazas N4
5. ✅ Se evalúan competencias transversales (no solo técnicas)

**Prioridad**: MEDIA
**Estimación**: 21 Story Points
**Sprint**: 3

---

### HU-SYS-007: API REST Completa (FastAPI)
**Como** sistema
**Quiero** exponer toda la funcionalidad vía API REST
**Para** permitir integración con frontends web/móvil y LMS

**Criterios de Aceptación Técnicos**:
1. ✅ Implementado en `src/ai_native_mvp/api/`
2. ✅ Endpoints principales:
   - `POST /api/v1/sessions` - Crear sesión
   - `POST /api/v1/interactions` - Procesar interacción
   - `GET /api/v1/traces/{session_id}` - Obtener trazas
   - `GET /api/v1/risks/session/{session_id}` - Obtener riesgos
   - `GET /api/v1/evaluation/session/{session_id}` - Obtener evaluación
3. ✅ OpenAPI/Swagger auto-generado
4. ✅ Autenticación JWT (producción)
5. ✅ Rate limiting y CORS configurados
6. ✅ Logs estructurados de todas las requests
7. ✅ Tests de integración para todos los endpoints

**Prioridad**: ALTA
**Estimación**: 21 Story Points
**Sprint**: 2

---

### HU-SYS-008: Integración con Git para Trazabilidad N2
**Como** sistema
**Quiero** integrarme con repositorios Git del estudiante
**Para** capturar trazabilidad N2 (commits, branches, code evolution)

**Criterios de Aceptación Técnicos**:
1. ✅ El estudiante puede vincular su repo Git
2. ✅ El sistema captura:
   - Commits (mensaje, diff, timestamp)
   - Branches creados
   - Merges realizados
   - Tests ejecutados (CI/CD)
3. ✅ La evolución del código se correlaciona con trazas N4
4. ✅ E-IA-Proc analiza patrones de commits (¿commits atómicos? ¿mensajes claros?)

**Prioridad**: MEDIA
**Estimación**: 13 Story Points
**Sprint**: 5
**Dependencias**: HU-SYS-003, HU-SYS-004

---

### HU-SYS-009: Dashboard Docente con Visualizaciones
**Como** sistema
**Quiero** ofrecer un dashboard web al docente
**Para** visualizar trazas, riesgos y evaluaciones de forma intuitiva

**Criterios de Aceptación Técnicos**:
1. ✅ Frontend en React/Vue
2. ✅ Visualizaciones:
   - Timeline de camino cognitivo (D3.js/Recharts)
   - Gráfico de dependencia de IA temporal
   - Heatmap de riesgos por estudiante
   - Distribución de competencias (box plot)
3. ✅ Filtros dinámicos (por estudiante, actividad, fecha)
4. ✅ Exportación de gráficos (PNG, SVG, PDF)

**Prioridad**: MEDIA
**Estimación**: 21 Story Points
**Sprint**: 4
**Dependencias**: HU-SYS-007

---

### HU-SYS-010: Integración LTI con Moodle
**Como** sistema
**Quiero** integrarme vía LTI con Moodle
**Para** que los docentes no tengan que gestionar usuarios manualmente

**Criterios de Aceptación Técnicos**:
1. ✅ Implementación LTI 1.3
2. ✅ Single Sign-On (SSO) con Moodle
3. ✅ Sincronización de estudiantes y cursos
4. ✅ Envío de calificaciones de vuelta a Moodle
5. ✅ Documentación de instalación para administradores Moodle

**Prioridad**: BAJA
**Estimación**: 21 Story Points
**Sprint**: 6

---

## Criterios de Aceptación Generales

### Todos los Desarrollos Deben Cumplir

1. **Código**:
   - ✅ Sigue convenciones PEP 8 (Python)
   - ✅ Type hints en todas las funciones públicas
   - ✅ Docstrings en español para clases y métodos principales

2. **Tests**:
   - ✅ Cobertura mínima: 70% (pytest.ini)
   - ✅ Tests unitarios para lógica de negocio
   - ✅ Tests de integración para flujos completos
   - ✅ Tests parametrizados para casos límite

3. **Documentación**:
   - ✅ README actualizado si hay cambios arquitectónicos
   - ✅ API endpoints documentados en Swagger
   - ✅ Ejemplos de uso en `examples/`

4. **Performance**:
   - ✅ Interacciones procesadas en <2 segundos
   - ✅ Trazas persisten de forma asíncrona (no bloquean respuesta)
   - ✅ Queries optimizadas (no N+1)

5. **Seguridad**:
   - ✅ No hay secretos hardcodeados
   - ✅ Input validation en todos los endpoints
   - ✅ SQL injection prevenida (uso de ORMs)
   - ✅ CORS configurado correctamente

---

## Definición de Done (DoD)

Una historia de usuario se considera **DONE** cuando:

### Desarrollo
- [ ] Código implementado según criterios de aceptación
- [ ] Code review aprobado por al menos 1 revisor
- [ ] No hay comentarios TODO pendientes críticos
- [ ] Código mergeado a rama `main`

### Testing
- [ ] Tests unitarios escritos y pasando
- [ ] Tests de integración pasando (si aplica)
- [ ] Cobertura de código ≥70%
- [ ] Tests manuales ejecutados (si requiere UI)

### Documentación
- [ ] Docstrings actualizados
- [ ] README actualizado (si cambió arquitectura)
- [ ] API documentada en Swagger (si es endpoint)
- [ ] Ejemplo de uso agregado a `examples/` (si es feature principal)

### Base de Datos
- [ ] Modelos ORM actualizados (si cambió esquema)
- [ ] Repositorios actualizados (si nuevas queries)
- [ ] Migraciones creadas (si aplica Alembic en futuro)

### Validación
- [ ] Funcionalidad demostrada al Product Owner
- [ ] Criterios de aceptación verificados uno por uno
- [ ] Feedback incorporado

### Calidad
- [ ] No introduce regresiones (tests previos siguen pasando)
- [ ] No degrada performance (mediciones comparativas)
- [ ] Logs apropiados agregados
- [ ] Manejo de errores robusto

---

## Estimaciones y Priorización

### Escala de Estimación (Story Points)

| Story Points | Complejidad | Tiempo Estimado |
|--------------|-------------|-----------------|
| 1 | Trivial | 1-2 horas |
| 3 | Simple | 4-6 horas |
| 5 | Moderado | 1-2 días |
| 8 | Complejo | 2-3 días |
| 13 | Muy complejo | 1 semana |
| 21 | Épico (dividir) | 2 semanas |

### Priorización

**CRÍTICA** (Sprint 1):
- HU-EST-001, HU-EST-002, HU-EST-003
- HU-SYS-001, HU-SYS-002, HU-SYS-003
- HU-DOC-002, HU-DOC-005

**ALTA** (Sprint 2-3):
- HU-EST-004, HU-EST-005, HU-EST-007
- HU-SYS-004, HU-SYS-005, HU-SYS-007
- HU-DOC-001, HU-ADM-001, HU-ADM-002

**MEDIA** (Sprint 4-5):
- HU-EST-006, HU-EST-009, HU-EST-014
- HU-SYS-006, HU-SYS-008, HU-SYS-009
- HU-DOC-003, HU-DOC-006, HU-ADM-003, HU-ADM-004

**BAJA** (Sprint 6+):
- HU-EST-008, HU-EST-010, HU-EST-011, HU-EST-012, HU-EST-013
- HU-SYS-010
- HU-ADM-005

---

## Roadmap de Implementación

### Sprint 1 (MVP Core)
**Objetivo**: Sistema básico funcional de interacción estudiante-IA con trazabilidad

- HU-EST-001: Iniciar sesión
- HU-EST-002: Consultas conceptuales
- HU-EST-003: Bloqueo de delegación
- HU-SYS-001: CRPE
- HU-SYS-002: GOV-IA
- HU-SYS-003: TC-N4

**Entregable**: CLI funcional con tutor básico y trazabilidad N4

---

### Sprint 2 (Evaluación y API)
**Objetivo**: Evaluación de procesos + API REST

- HU-EST-004: Pistas graduadas
- HU-EST-005: Justificaciones
- HU-EST-007: Retroalimentación formativa
- HU-SYS-004: E-IA-Proc
- HU-SYS-005: AR-IA
- HU-SYS-007: API REST
- HU-DOC-001: Diseñar actividades
- HU-DOC-005: Evaluar procesos
- HU-ADM-001: Políticas institucionales

**Entregable**: Sistema completo con evaluación automática + API REST

---

### Sprint 3 (Docente y Gobernanza)
**Objetivo**: Herramientas para docentes y administradores

- HU-EST-006: Camino cognitivo reconstructido
- HU-EST-009: Simulador PO-IA
- HU-DOC-002: Visualizar trazas
- HU-DOC-003: Comparar estudiantes
- HU-DOC-004: Alertas en tiempo real
- HU-SYS-006: Simuladores profesionales
- HU-ADM-004: Configurar proveedores LLM

**Entregable**: Dashboard docente básico + simuladores iniciales

---

### Sprint 4-6 (Funcionalidades Avanzadas)
**Objetivo**: Completar simuladores, integraciones y analíticas avanzadas

- Resto de simuladores profesionales (SM-IA, IT-IA, IR-IA, CX-IA, DSO-IA)
- Integración Git (N2)
- Dashboard con visualizaciones avanzadas
- Reportes institucionales
- Exportación de datos
- Integración LTI con Moodle

**Entregable**: Sistema completo production-ready

---

## Glosario

| Término | Definición |
|---------|------------|
| **AI-Native** | Modelo formativo que asume la IA generativa como condición estructural |
| **Trazabilidad N4** | Captura de proceso cognitivo en 4 niveles (superficial, técnico, interaccional, cognitivo) |
| **CRPE** | Cognitive-Pedagogical Reasoning Engine - Motor de razonamiento del sistema |
| **Delegación Total** | Solicitud donde el estudiante pide a la IA que resuelva todo el problema |
| **Andamiaje Cognitivo** | Apoyo graduado que se retira progresivamente conforme el estudiante avanza |
| **Competencia Híbrida** | Capacidad de trabajar efectivamente en colaboración con IA |
| **Evaluación de Procesos** | Evaluar el razonamiento y decisiones, no solo el producto final |

---

## Apéndice: Frameworks Normativos

El ecosistema AI-Native se alinea con:

- **UNESCO (2021)**: Recomendación sobre la Ética de la IA
- **OECD (2019)**: Principios de IA
- **IEEE (2019)**: Ethically Aligned Design
- **ISO/IEC 23894:2023**: Sistemas de IA - Gestión de Riesgos
- **ISO/IEC 42001:2023**: Sistemas de Gestión de IA

---

**Documento Vivo**: Este backlog se actualizará conforme evolucione el proyecto.

**Versión**: 1.0
**Última Actualización**: 2025-11-18
**Autor**: Mag. Alberto Cortez (con asistencia de Claude Code)