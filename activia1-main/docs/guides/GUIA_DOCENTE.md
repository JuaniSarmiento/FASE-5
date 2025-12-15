# 👨‍🏫 Guía del Docente - Ecosistema AI-Native

## Manual para la Gestión Pedagógica de Actividades AI-Native

Esta guía te ayudará a aprovechar al máximo el **Ecosistema AI-Native** para diseñar actividades, monitorear el proceso de aprendizaje de tus estudiantes y evaluar sus competencias en la era de la IA generativa.

---

## 📚 Índice

1. [Introducción al Modelo AI-Native](#introducción-al-modelo-ai-native)
2. [Acceso y Primeros Pasos](#acceso-y-primeros-pasos)
3. [Diseñar Actividades AI-Native](#diseñar-actividades-ai-native)
4. [Configurar Políticas Pedagógicas](#configurar-políticas-pedagógicas)
5. [Monitorear Trazas Cognitivas](#monitorear-trazas-cognitivas)
6. [Evaluar Procesos (No Solo Productos)](#evaluar-procesos-no-solo-productos)
7. [Intervención Pedagógica en Tiempo Real](#intervención-pedagógica-en-tiempo-real)
8. [Gestión de Riesgos Cognitivos](#gestión-de-riesgos-cognitivos)
9. [Reportes y Analíticas](#reportes-y-analíticas)
10. [Casos de Uso y Ejemplos](#casos-de-uso-y-ejemplos)
11. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Introducción al Modelo AI-Native

### ¿Qué es el Modelo AI-Native?

El **Ecosistema AI-Native** es un sistema educativo que asume la presencia de IA generativa como **condición estructural** de la enseñanza-aprendizaje de programación, y articula una respuesta pedagógica, cognitiva, tecnológica e institucional integral.

### La Transformación Epistemológica

En la era de ChatGPT, Copilot y Code LLMs, **"saber programar"** ya no significa solo escribir código manualmente. Ahora implica:

1. **Formular y descomponer problemas** para agentes de IA
2. **Evaluar críticamente** soluciones generadas algorítmicamente
3. **Detectar inconsistencias, vulnerabilidades y alucinaciones**
4. **Sostener procesos de auditoría continua**
5. **Documentar razonamiento y decisiones** en procesos híbridos humano-IA
6. **Operar bajo criterios éticos y de gobernanza** algorítmica

### Tu Rol como Docente AI-Native

Como docente, tu rol se transforma:

**Antes (modelo tradicional)**:
- Enseñar sintaxis y algoritmos
- Evaluar código final
- Detectar plagio manual

**Ahora (modelo AI-Native)**:
- Diseñar actividades que promuevan razonamiento crítico **con IA**
- Evaluar el **proceso cognitivo**, no solo el producto
- Configurar políticas pedagógicas que bloqueen delegación pasiva
- Monitorear trazas cognitivas (N4) en tiempo real
- Intervenir cuando detectás riesgos (dependencia excesiva, falta de justificación)
- Gestionar gobernanza institucional de IA generativa

---

## Acceso y Primeros Pasos

### 1. Acceso al Panel Docente

**Opción A: Interfaz Web**
```
1. Abre tu navegador: http://localhost:3000
2. Selecciona "Docente" en la página de inicio
3. Verás el panel de gestión de actividades
```

**Opción B: API REST**
```bash
# Crear actividad vía API
curl -X POST http://localhost:8000/api/v1/activities \
  -H "Content-Type: application/json" \
  -d '{
    "activity_id": "prog2_tp1_colas",
    "title": "Implementación de Colas Circulares",
    "teacher_id": "profesor_001",
    ...
  }'
```

**Opción C: Scripts Python**
```python
from ai_native_mvp.database import get_db_session
from ai_native_mvp.database.repositories import ActivityRepository

with get_db_session() as db:
    activity_repo = ActivityRepository(db)
    activity = activity_repo.create(
        activity_id="prog2_tp1_colas",
        title="Implementación de Colas Circulares",
        teacher_id="profesor_001",
        ...
    )
```

### 2. Navegación del Panel Docente

El panel tiene 3 vistas principales:

#### Vista de Listado
- Ver todas tus actividades
- Filtrar por estado (borrador, activa, archivada)
- Buscar por título, materia, dificultad
- Acciones rápidas: Editar, Publicar, Archivar, Clonar, Eliminar

#### Vista de Creación
- Formulario completo para diseñar actividades
- Configuración de políticas pedagógicas
- Criterios de evaluación
- Publicación inmediata o guardar como borrador

#### Vista de Monitoreo
- Ver trazas N4 de estudiantes
- Alertas de riesgos en tiempo real
- Evaluaciones de procesos generadas automáticamente
- Comparativas entre estudiantes

---

## Diseñar Actividades AI-Native

### Estructura de una Actividad

Una actividad AI-Native se compone de:

```
ACTIVIDAD: Implementación de Colas Circulares
├── Información Básica
│   ├── ID único: prog2_tp1_colas
│   ├── Título: "Implementación de Colas Circulares"
│   ├── Descripción: Contexto y motivación
│   └── Consigna: Instrucciones detalladas
│
├── Criterios de Evaluación
│   ├── Descomposición del problema
│   ├── Justificación de decisiones
│   ├── Calidad del código
│   ├── Tests implementados
│   └── Documentación del razonamiento
│
├── Políticas Pedagógicas (Configurables)
│   ├── Nivel máximo de ayuda permitido
│   ├── Bloqueo de soluciones completas
│   ├── Exigir justificaciones
│   ├── Permitir fragmentos de código
│   └── Umbrales de riesgo
│
└── Metadata
    ├── Materia: Programación 2
    ├── Dificultad: Intermedia
    ├── Duración estimada: 120 minutos
    └── Tags: ["estructuras-datos", "colas", "arreglos"]
```

### Ejemplo de Actividad Completa

```json
{
  "activity_id": "prog2_tp1_colas",
  "title": "Implementación de Colas Circulares",
  "description": "En este trabajo práctico implementarás una cola circular usando arreglos. Este tipo de estructura es fundamental en sistemas operativos, buffers de red y sistemas de colas de mensajes.",

  "instructions": "
    Deberás implementar una cola circular con las siguientes operaciones:
    - enqueue(item): Insertar un elemento
    - dequeue(): Eliminar y retornar el elemento del frente
    - is_full(): Verificar si la cola está llena
    - is_empty(): Verificar si la cola está vacía
    - peek(): Ver el elemento del frente sin eliminarlo

    Restricciones:
    - Usar un arreglo de tamaño fijo
    - No usar listas dinámicas
    - Implementar manejo de casos límite (cola llena, vacía)
    - Crear tests para validar tu implementación
  ",

  "evaluation_criteria": [
    "Descomposición del problema en operaciones básicas",
    "Justificación de decisiones de diseño (¿por qué arreglo? ¿por qué circular?)",
    "Manejo correcto de índices circulares (operador módulo)",
    "Implementación de casos límite (cola llena, vacía)",
    "Tests que cubran casos normales y límite",
    "Documentación del razonamiento en cada decisión clave"
  ],

  "policies": {
    "max_help_level": "MEDIO",
    "block_complete_solutions": true,
    "require_justification": true,
    "allow_code_snippets": false,
    "risk_thresholds": {
      "ai_dependency": 0.6,
      "lack_justification": 0.3
    }
  },

  "subject": "Programación 2",
  "difficulty": "INTERMEDIO",
  "estimated_duration_minutes": 120,
  "tags": ["estructuras-datos", "colas", "arreglos", "complejidad-temporal"]
}
```

### Consejos para Diseñar Actividades Efectivas

#### 1. Definí objetivos de aprendizaje claros

**Mal diseño**:
```
"Implementá una cola circular"
```

**Buen diseño**:
```
"Implementá una cola circular entendiendo:
- POR QUÉ usar arreglos circulares vs listas enlazadas
- CÓMO gestionar índices circulares
- QUÉ problemas resuelve vs cola simple
- CUÁNDO es apropiado usar esta estructura"
```

#### 2. Exigí justificaciones, no solo código

Agregá preguntas guía en las instrucciones:
```
"Antes de implementar:
1. ¿Por qué elegiste un arreglo en lugar de una lista enlazada?
2. ¿Qué alternativas consideraste para detectar si está llena?
3. ¿Cómo validarás que tu implementación es correcta?"
```

#### 3. Diseñá para promover metacognición

Incluí reflexiones al final:
```
"Al terminar, respondé:
1. ¿Qué fue lo más difícil? ¿Por qué?
2. ¿Cómo te ayudó la IA? ¿En qué no te ayudó?
3. Si tuvieras que volver a hacerlo, ¿qué cambiarías?"
```

#### 4. Configurá políticas apropiadas al nivel

**Nivel Inicial** (estudiantes nuevos con IA):
```json
{
  "max_help_level": "BAJO",
  "block_complete_solutions": true,
  "require_justification": true,
  "allow_code_snippets": false
}
```

**Nivel Avanzado** (estudiantes con autonomía):
```json
{
  "max_help_level": "ALTO",
  "block_complete_solutions": false,
  "require_justification": true,
  "allow_code_snippets": true
}
```

---

## Configurar Políticas Pedagógicas

### ¿Qué son las Políticas Pedagógicas?

Las políticas son **reglas automáticas** que el sistema aplica para garantizar que los estudiantes:
- No deleguen pasivamente en la IA
- Justifiquen sus decisiones de diseño
- Mantengan un nivel equilibrado de dependencia de IA
- Desarrollen autonomía cognitiva

### Políticas Configurables

#### 1. **max_help_level** (Nivel Máximo de Ayuda)

Define cuánta ayuda puede dar la IA:

- **MINIMO**: Solo explicaciones conceptuales, sin pistas de implementación
- **BAJO**: Pistas muy generales, preguntas socráticas
- **MEDIO**: Pistas específicas graduadas, sin código completo
- **ALTO**: Fragmentos de código, ejemplos detallados (pero no solución completa)

**Ejemplo**:
```python
"max_help_level": "MEDIO"
```

**Efecto**: El tutor puede dar pistas como:
```
"Para detectar si está llena, considerá la relación entre rear y front.
Una estrategia común es: (rear + 1) % capacidad == front"
```

Pero NO puede dar:
```python
def is_full(self):
    return (self.rear + 1) % self.capacity == self.front
```

#### 2. **block_complete_solutions** (Bloquear Soluciones Completas)

Si está en `true`, el sistema **bloquea** solicitudes como:
- "Dame el código completo"
- "Resolvelo vos"
- "Implementa todo"

**Recomendado**: `true` para **todas** las actividades evaluativas.

**Ejemplo de bloqueo**:
```
Estudiante: "Dame el código completo de enqueue()"

Sistema: 🛑 BLOQUEADO
"Tu solicitud implica delegación total. Necesito que:
1. Descompongas el problema
2. Identifiques qué parte específica te genera dificultad
3. Propongas tu plan inicial"
```

#### 3. **require_justification** (Exigir Justificación)

Si está en `true`, el sistema **solicita justificaciones** en decisiones clave.

**Ejemplo**:
```
Estudiante: "Voy a usar un arreglo"

Tutor: "¿Por qué elegiste un arreglo en lugar de una lista enlazada?
Justificá tu decisión considerando:
- Complejidad temporal
- Uso de memoria
- Requisitos del problema"
```

**Recomendado**: `true` para actividades de **diseño** y **arquitectura**.

#### 4. **allow_code_snippets** (Permitir Fragmentos de Código)

Si está en `true`, el tutor puede mostrar **fragmentos pequeños** de código como ejemplos.

**Ejemplo con `allow_code_snippets: true`**:
```
Tutor: "El operador módulo funciona así:
  índice_circular = (índice + 1) % capacidad

Ahora aplicalo a tu caso."
```

**Ejemplo con `allow_code_snippets: false`**:
```
Tutor: "Necesitás usar el operador módulo para circularidad.
¿Cómo lo aplicarías a tus índices front y rear?"
```

**Recomendado**:
- `false` para **actividades iniciales** (promover razonamiento desde cero)
- `true` para **actividades avanzadas** (acelerar implementación)

#### 5. **risk_thresholds** (Umbrales de Riesgo)

Define cuándo disparar alertas automáticas:

```python
"risk_thresholds": {
  "ai_dependency": 0.6,  # Alertar si dependencia IA >60%
  "lack_justification": 0.3  # Alertar si <30% de decisiones están justificadas
}
```

**Umbrales recomendados por nivel**:

| Nivel | ai_dependency | lack_justification |
|-------|---------------|-------------------|
| Inicial | 0.4 (40%) | 0.5 (50%) |
| Intermedio | 0.6 (60%) | 0.3 (30%) |
| Avanzado | 0.7 (70%) | 0.2 (20%) |

### Plantillas de Políticas

#### Plantilla: Actividad Inicial (Estudiantes Nuevos)
```json
{
  "max_help_level": "BAJO",
  "block_complete_solutions": true,
  "require_justification": true,
  "allow_code_snippets": false,
  "risk_thresholds": {
    "ai_dependency": 0.4,
    "lack_justification": 0.5
  }
}
```

#### Plantilla: Actividad Intermedia
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

#### Plantilla: Actividad Avanzada (Diseño de Sistemas)
```json
{
  "max_help_level": "ALTO",
  "block_complete_solutions": false,
  "require_justification": true,
  "allow_code_snippets": true,
  "risk_thresholds": {
    "ai_dependency": 0.7,
    "lack_justification": 0.2
  }
}
```

#### Plantilla: Trabajo Final (Máxima Exigencia)
```json
{
  "max_help_level": "MINIMO",
  "block_complete_solutions": true,
  "require_justification": true,
  "allow_code_snippets": false,
  "risk_thresholds": {
    "ai_dependency": 0.3,
    "lack_justification": 0.1
  }
}
```

---

## Monitorear Trazas Cognitivas

### ¿Qué son las Trazas Cognitivas N4?

El sistema captura **4 niveles de trazabilidad** del proceso de aprendizaje:

#### N1 - Superficial
- Código final entregado
- Archivos del proyecto

#### N2 - Técnico
- Commits de Git
- Branches creados
- Tests ejecutados

#### N3 - Interaccional
- Prompts enviados al tutor
- Respuestas recibidas
- Reintentos y correcciones

#### N4 - Cognitivo Completo
- **Intención cognitiva**: ¿Por qué preguntó eso?
- **Estado cognitivo**: EXPLORACION, PLANIFICACION, IMPLEMENTACION, VALIDACION
- **Decisiones de diseño**: ¿Por qué eligió esa estructura?
- **Justificaciones**: ¿Por qué descartó alternativas?
- **Cambios de estrategia**: ¿Cuándo cambió de enfoque?

### Acceder a las Trazas de un Estudiante

**Vía interfaz web**:
```
1. Panel Docente → Actividad → Ver Estudiantes
2. Seleccionar estudiante
3. Ver "Trazas Cognitivas N4"
```

**Vía API**:
```bash
curl http://localhost:8000/api/v1/traces/{session_id}/cognitive-path
```

**Vía Python**:
```python
from ai_native_mvp.database import get_db_session
from ai_native_mvp.database.repositories import TraceRepository

with get_db_session() as db:
    trace_repo = TraceRepository(db)
    traces = trace_repo.get_by_session(session_id)

    for trace in traces:
        print(f"Estado: {trace.cognitive_state}")
        print(f"Contenido: {trace.content}")
        print(f"AI Involvement: {trace.ai_involvement}")
```

### Interpretar el Camino Cognitivo

**Ejemplo de traza reconstructed**:

```
========================================
CAMINO COGNITIVO - Juan Pérez
========================================
Actividad: prog2_tp1_colas
Duración: 45 minutos
========================================

Fase 1: EXPLORACION (10:00 - 10:15)
  └─ 3 interacciones
  └─ Consultas: "¿Qué es cola circular?", "Diferencia con cola simple"
  └─ AI Involvement: 25% (bajo - óptimo)
  └─ Riesgos: Ninguno ✓

Fase 2: PLANIFICACION (10:15 - 10:25)
  └─ 2 interacciones
  └─ Decisión: Arreglo circular (justificado ✓)
  └─ Alternativas: Lista enlazada (descartada con razones ✓)
  └─ AI Involvement: 30%
  └─ Riesgos: Ninguno ✓

Fase 3: IMPLEMENTACION (10:25 - 10:40)
  └─ 5 interacciones
  └─ Pistas solicitadas: 2 (nivel MEDIO)
  └─ AI Involvement: 55% (moderado)
  └─ ⚠️ RIESGO: Falta justificación en manejo de cola llena
  └─ Autocorrección: Detectó error en condición while ✓

Fase 4: VALIDACION (10:40 - 10:45)
  └─ 2 interacciones
  └─ Tests creados: 3 (casos límite cubiertos ✓)
  └─ AI Involvement: 20% (bajo - óptimo)
  └─ Riesgos: Ninguno ✓

========================================
RESUMEN
========================================
✅ Competencia: EN_DESARROLLO (6/10)
📊 Dependencia IA: 32.5% (ÓPTIMO)
⚠️ Riesgos: 1 (medio - justificación faltante)
💪 Autocorrecciones: 2
🔄 Cambios de estrategia: 1
```

### Señales de Alerta en las Trazas

#### 🚨 CRÍTICO

- **Dependencia IA >80%**: Delegación casi total
- **0 justificaciones**: No razona, solo copia
- **Múltiples bloqueos** (>3): Insiste en delegar

**Acción**: Intervención inmediata del docente

#### ⚠️ ALTO

- **Dependencia IA 60-80%**: Uso excesivo
- **<20% de justificaciones**: Razonamiento superficial
- **1-2 bloqueos**: Tendencia a delegar

**Acción**: Alerta automática al docente

#### 🟡 MEDIO

- **Dependencia IA 40-60%**: Uso moderado
- **20-50% de justificaciones**: Razonamiento parcial

**Acción**: Monitoreo, sin intervención

#### ✅ ÓPTIMO

- **Dependencia IA 20-40%**: Uso estratégico
- **>50% de justificaciones**: Razonamiento sólido
- **Autocorrecciones**: Autorregulación activa

**Acción**: Ninguna, felicitar al estudiante

---

## Evaluar Procesos (No Solo Productos)

### El Cambio de Paradigma

**Evaluación Tradicional**:
```
Código funciona → 10
Código no funciona → 0
```

**Evaluación de Procesos AI-Native**:
```
40% Producto Final (código funcional, eficiente, documentado)
60% Proceso Cognitivo (razonamiento, decisiones, autonomía)
```

### Dimensiones del Proceso Evaluadas

El sistema genera automáticamente un **Reporte de Evaluación de Procesos** con 5 dimensiones:

#### 1. Descomposición de Problemas (0-10)

¿El estudiante dividió el problema en partes manejables?

**Indicadores**:
- ✅ Identificó operaciones básicas (enqueue, dequeue, is_full, is_empty)
- ✅ Resolvió cada operación por separado
- ✅ Integró las partes en una solución coherente

**Puntaje alto**: 8-10 (descomposición clara)
**Puntaje bajo**: 0-3 (intentó resolver todo de golpe)

#### 2. Autorregulación y Metacognición (0-10)

¿El estudiante monitoreó y reflexionó sobre su proceso?

**Indicadores**:
- ✅ Detectó errores por sí mismo
- ✅ Reflexionó sobre su estrategia
- ✅ Ajustó su enfoque cuando no funcionaba

**Puntaje alto**: 8-10 (metacognición activa)
**Puntaje bajo**: 0-3 (no reflexiona, solo ejecuta)

#### 3. Coherencia Lógica (0-10)

¿El razonamiento es consistente y justificado?

**Indicadores**:
- ✅ Decisiones justificadas con criterios objetivos
- ✅ Coherencia entre diseño e implementación
- ✅ Razonamiento lógico sin saltos

**Puntaje alto**: 8-10 (razonamiento sólido)
**Puntaje bajo**: 0-3 (decisiones arbitrarias, contradicciones)

#### 4. Verificación y Testing (0-10)

¿El estudiante validó su solución?

**Indicadores**:
- ✅ Creó tests (no solo ejecutó el código)
- ✅ Cubrió casos límite (cola vacía, llena)
- ✅ Validó complejidad temporal

**Puntaje alto**: 8-10 (testing sistemático)
**Puntaje bajo**: 0-3 (no testeó, o solo casos triviales)

#### 5. Documentación del Razonamiento (0-10)

¿El estudiante documentó POR QUÉ tomó cada decisión?

**Indicadores**:
- ✅ Justificó elecciones de diseño
- ✅ Documentó alternativas consideradas
- ✅ Explicó trade-offs

**Puntaje alto**: 8-10 (documentación exhaustiva)
**Puntaje bajo**: 0-3 (sin justificaciones)

### Niveles de Competencia

El sistema asigna un **nivel de competencia** basado en el puntaje global:

| Puntaje | Nivel | Descripción |
|---------|-------|-------------|
| 9-10 | **EXPERTO** | Uso estratégico de IA, autonomía completa, razonamiento sólido |
| 7-8 | **COMPETENTE** | Uso equilibrado de IA, autonomía sólida, justificaciones claras |
| 4-6 | **EN_DESARROLLO** | Uso moderado de IA, autonomía creciente, justificaciones parciales |
| 0-3 | **INICIAL** | Dependencia alta de IA, poca autonomía, razonamiento superficial |

### Ejemplo de Reporte Automático

```
========================================
EVALUACIÓN FORMATIVA DE PROCESO
========================================
Estudiante: Juan Pérez
Actividad: prog2_tp1_colas
Fecha: 2025-11-19
Duración: 45 minutos

NIVEL ALCANZADO: EN_DESARROLLO (6.0/10)

DIMENSIONES EVALUADAS:
├─ Descomposición de Problemas: 8/10 (COMPETENTE) ✓
│  └─ Fortaleza: Dividió el problema en operaciones básicas
│
├─ Autorregulación y Metacognición: 4/10 (EN_DESARROLLO)
│  └─ Mejora: Poca reflexión sobre errores cometidos
│
├─ Coherencia Lógica: 6/10 (EN_DESARROLLO)
│  └─ Mejora: Algunas decisiones sin justificar
│
├─ Verificación y Testing: 7/10 (COMPETENTE) ✓
│  └─ Fortaleza: Creó tests para casos límite
│
└─ Documentación: 5/10 (EN_DESARROLLO)
   └─ Mejora: Faltó documentar alternativas consideradas

FORTALEZAS PRINCIPALES:
✅ Buena planificación inicial
✅ Uso equilibrado de ayuda de IA (32%)
✅ Implementó tests sin que se le solicitara

ÁREAS DE MEJORA:
⚠️ Autorregulación: Reflexionar explícitamente sobre errores
⚠️ Justificación: Documentar POR QUÉ tomas cada decisión
⚠️ Alternativas: Considerar explícitamente otras opciones antes de decidir

RECOMENDACIONES ACCIONABLES:
1. Antes de implementar, escribir 2-3 alternativas y justificar elección
2. Al encontrar un error, preguntarse: "¿Por qué falló? ¿Qué aprendí?"
3. Al pedir ayuda a la IA, primero formular una hipótesis

RIESGOS DETECTADOS:
⚠️ 1 riesgo medio: LACK_JUSTIFICATION
   └─ Recomendación: En próximas sesiones, justificar cada decisión clave

PRÓXIMOS PASOS:
→ Practicar con pilas (similar a colas) aplicando justificaciones explícitas
→ Enfocarse en autorregulación: preguntarse "¿qué aprendí?" al final
```

### Ajustar la Evaluación Automática

El reporte es **una sugerencia**, no una imposición. Vos como docente podés:

- ✅ Aceptar la evaluación sugerida
- ✅ Ajustar puntajes por dimensión
- ✅ Agregar comentarios cualitativos
- ✅ Marcar para revisión manual

**Recomendación**: Usá la evaluación automática como **punto de partida**, pero siempre revisá casos atípicos.

---

## Intervención Pedagógica en Tiempo Real

### Alertas Automáticas

El sistema te envía **alertas en tiempo real** cuando detecta:

#### Alerta Crítica 🚨

- **Dependencia IA >85%**
- **3+ bloqueos por delegación**
- **0 justificaciones en 5+ decisiones**

**Ejemplo de alerta**:
```
🚨 ALERTA CRÍTICA
Estudiante: Juan Pérez
Actividad: prog2_tp1_colas
Sesión activa hace: 35 minutos

PROBLEMA DETECTADO:
- Dependencia IA: 87% (crítico)
- Bloqueos: 3 (delegación total)
- Justificaciones: 0%

SUGERENCIAS DE INTERVENCIÓN:
1. Pausar la sesión y reunirte con el estudiante
2. Preguntarle: "¿Qué entendés del problema?"
3. Guiarlo a descomponer el problema en partes
4. Reducir el nivel de ayuda permitido temporalmente

[Ver Trazas] [Enviar Mensaje] [Marcar como Atendida]
```

#### Alerta Media ⚠️

- **Dependencia IA 60-85%**
- **1-2 bloqueos**
- **<30% de justificaciones**

**Acción sugerida**: Monitorear, posible mensaje de orientación

#### Alerta de Progreso Lento 🐌

- **Sesión activa >2 horas en la misma fase**

**Acción sugerida**: Preguntarle al estudiante si necesita ayuda

### Intervenir desde el Panel

**Acciones disponibles**:

1. **Enviar mensaje directo**
```
"Hola Juan, veo que llevas 3 bloqueos por delegación.
¿Querés que hablemos para descomponer el problema juntos?"
```

2. **Ajustar políticas temporalmente**
```
Reducir max_help_level de MEDIO a BAJO
```

3. **Marcar alerta como atendida**
```
"Intervine, hablé con el estudiante. Está re-encaminado."
```

4. **Acceder a trazas completas**
```
Ver el camino cognitivo completo para entender dónde se trabó
```

### Buenas Prácticas de Intervención

#### ✅ HACER

- Intervenir **temprano** (antes de que se frustre)
- Hacer **preguntas guía** (no dar soluciones)
- Fomentar **metacognición**: "¿Por qué creés que te bloquearon?"
- Validar **emociones**: "Es normal sentirse trabado, hablemos"

#### ❌ NO HACER

- Dar la solución completa (contradice el modelo AI-Native)
- Ignorar alertas críticas
- Penalizar al estudiante por bloqueos (son señales pedagógicas, no faltas)
- Intervenir en exceso (si está progresando bien, dejalo)

---

## Gestión de Riesgos Cognitivos

### 5 Dimensiones de Riesgo

El sistema detecta **5 tipos de riesgos**:

#### 1. Riesgos COGNITIVOS

- **COGNITIVE_DELEGATION**: Delegación total del problema
- **AI_DEPENDENCY**: Dependencia excesiva de IA
- **LACK_JUSTIFICATION**: No justifica decisiones

**Nivel**: BAJO, MEDIO, ALTO, CRÍTICO

#### 2. Riesgos ÉTICOS

- **ACADEMIC_INTEGRITY**: Integridad académica cuestionable
- **UNDISCLOSED_AI_USE**: Uso de IA sin documentar
- **PLAGIARISM**: Posible plagio

#### 3. Riesgos EPISTÉMICOS

- **UNCRITICAL_ACCEPTANCE**: Acepta respuestas de IA sin evaluar
- **CONCEPTUAL_ERROR**: Errores conceptuales fundamentales
- **LOGICAL_FALLACY**: Falacias lógicas en razonamiento

#### 4. Riesgos TÉCNICOS

- **SECURITY_VULNERABILITY**: Vulnerabilidades en código
- **POOR_CODE_QUALITY**: Código de baja calidad

#### 5. Riesgos de GOBERNANZA

- **POLICY_VIOLATION**: Violación de políticas institucionales
- **UNAUTHORIZED_USE**: Uso no autorizado de herramientas

### Dashboard de Riesgos

**Acceso**:
```
Panel Docente → Riesgos → Actividad
```

**Vista**:
```
========================================
RIESGOS DETECTADOS - prog2_tp1_colas
========================================

Críticos: 2
Altos: 5
Medios: 12
Bajos: 8

RIESGOS CRÍTICOS:
├─ Juan Pérez: COGNITIVE_DELEGATION (CRÍTICO)
│  └─ Evidencia: 3 bloqueos, dependencia 87%
│  └─ Acción: Intervención inmediata
│
└─ María García: AI_DEPENDENCY (CRÍTICO)
   └─ Evidencia: Dependencia 92%, 0 autocorrecciones
   └─ Acción: Reunión con la estudiante

RIESGOS ALTOS:
├─ Pedro López: LACK_JUSTIFICATION (ALTO)
│  └─ Evidencia: 0% de decisiones justificadas
│  └─ Acción: Recordarle importancia de justificar
│
[Ver todos los riesgos]
```

### Resolver Riesgos

**Flujo de resolución**:

1. **Detectar**: Sistema detecta automáticamente
2. **Alertar**: Docente recibe notificación
3. **Intervenir**: Docente toma acción (mensaje, reunión, ajuste de políticas)
4. **Documentar**: Docente registra qué hizo
5. **Marcar como resuelto**: Riesgo cerrado con nota de resolución

**Ejemplo**:
```
Riesgo: COGNITIVE_DELEGATION (Juan Pérez)
Fecha: 2025-11-19 10:30

Acción tomada:
"Reuní con Juan, le expliqué el problema de delegar.
Hicimos juntos una descomposición del problema en el pizarrón.
Redujo su dependencia a 45% en las siguientes 2 sesiones.
Riesgo resuelto ✓"

Estado: RESUELTO
Fecha resolución: 2025-11-20
```

---

## Reportes y Analíticas

### Reporte de Actividad Individual

Ver performance de todos los estudiantes en una actividad:

```
========================================
REPORTE: prog2_tp1_colas
========================================
Estudiantes: 30
Completados: 28
En progreso: 2
========================================

ESTADÍSTICAS GENERALES:
- Tiempo promedio: 52 minutos
- Dependencia IA promedio: 38%
- Competencia promedio: 6.5/10 (EN_DESARROLLO)

DISTRIBUCIÓN DE COMPETENCIAS:
EXPERTO (9-10):       3 estudiantes (10%)
COMPETENTE (7-8):    12 estudiantes (40%)
EN_DESARROLLO (4-6): 14 estudiantes (47%)
INICIAL (0-3):        1 estudiante  (3%)

RIESGOS MÁS FRECUENTES:
1. LACK_JUSTIFICATION: 18 casos (60%)
2. AI_DEPENDENCY:       5 casos (17%)
3. COGNITIVE_DELEGATION: 3 casos (10%)

TOP 5 ESTUDIANTES:
1. María López:     9.2/10 (EXPERTO)
2. Carlos García:   8.8/10 (COMPETENTE)
3. Ana Martínez:    8.5/10 (COMPETENTE)
...

ESTUDIANTES EN RIESGO:
⚠️ Juan Pérez: Dependencia 87%, 3 bloqueos
⚠️ Pedro Gómez: 0% justificaciones
```

### Reporte de Curso Completo

Ver evolución del curso a lo largo del semestre:

```
========================================
REPORTE DE CURSO: Programación 2
========================================
Período: Agosto - Noviembre 2025
Estudiantes: 30
Actividades: 8
========================================

EVOLUCIÓN DE COMPETENCIAS:
Agosto:    4.2/10 (EN_DESARROLLO)
Septiembre: 5.1/10 (EN_DESARROLLO)
Octubre:    6.3/10 (EN_DESARROLLO)
Noviembre:  7.1/10 (COMPETENTE) ✓

EVOLUCIÓN DE DEPENDENCIA IA:
Agosto:    58% (alta)
Septiembre: 48% (moderada)
Octubre:    39% (óptima)
Noviembre:  35% (óptima) ✓

RIESGOS TOTALES: 87
- Resueltos: 72 (83%)
- En seguimiento: 12 (14%)
- Críticos abiertos: 3 (3%)

ACTIVIDADES CON MAYOR DIFICULTAD:
1. Árboles Binarios de Búsqueda: 4.8/10 promedio
2. Grafos y Recorridos: 5.2/10 promedio
3. Colas Circulares: 6.5/10 promedio

RECOMENDACIONES:
→ Reforzar conceptos de árboles binarios
→ Diseñar actividad complementaria de grafos
→ Celebrar mejora en autonomía (dependencia IA bajó 23%)
```

### Exportar Datos

**Formatos disponibles**:
- PDF: Reporte visual para imprimir
- Excel: Datos tabulados para análisis
- JSON: Datos crudos para investigación

**Acceso**:
```
Panel Docente → Reportes → Exportar
```

---

## Casos de Uso y Ejemplos

### Caso 1: Estudiante con Delegación Total

**Situación**: Juan intenta delegar todo el problema.

**Señales**:
- 3 bloqueos por delegación
- Dependencia IA: 87%
- 0 justificaciones

**Acción**:
1. Intervenir inmediatamente (reunión 1 a 1)
2. Explicarle el objetivo pedagógico
3. Hacer descomposición guiada en pizarrón
4. Reducir `max_help_level` a BAJO temporalmente
5. Monitorear próxima sesión

**Resultado esperado**: Dependencia baja a 40-50% en siguientes sesiones.

### Caso 2: Estudiante con Razonamiento Superficial

**Situación**: María completa actividades rápido, pero sin justificar.

**Señales**:
- Código funcional
- <20% de decisiones justificadas
- Poca metacognición

**Acción**:
1. Enviar mensaje: "Tu código funciona, pero quiero que expliques POR QUÉ tomaste estas decisiones"
2. Configurar `require_justification: true` más estrictamente
3. En próxima actividad, exigir justificaciones antes de permitir implementación

**Resultado esperado**: María desarrolla hábito de justificar.

### Caso 3: Curso con Dependencia Alta de IA

**Situación**: Todo el curso tiene dependencia >60%.

**Señales**:
- Promedio de dependencia: 68%
- Muchos riesgos COGNITIVE_DELEGATION

**Acción**:
1. Revisar diseño de actividades (¿son muy difíciles?)
2. Ajustar políticas globalmente (reducir `max_help_level`)
3. Dar clase teórica sobre uso estratégico de IA
4. Diseñar actividad específica sobre metacognición

**Resultado esperado**: Dependencia baja a 40-50% en próximas actividades.

---

## Preguntas Frecuentes

### ¿Debo revisar todas las trazas de todos los estudiantes?

**No**. El sistema te **alerta automáticamente** cuando hay riesgos críticos o altos. Revisá solo:
- Alertas críticas (inmediato)
- Alertas altas (dentro de 24hs)
- Casos atípicos (muy buena o muy mala performance)

### ¿Cómo sé si mis políticas son adecuadas?

Mirá las métricas del curso:
- Si dependencia IA promedio >60%: Políticas demasiado permisivas
- Si dependencia IA promedio <20%: Políticas demasiado restrictivas
- **Óptimo**: 30-50% de dependencia IA

### ¿Qué hago si un estudiante se queja de los bloqueos?

**Explicá el objetivo pedagógico**:
```
"Los bloqueos no son un castigo, son una redirección pedagógica.
El objetivo es que aprendas a razonar CON la IA, no a depender pasivamente de ella.
En la industria, vas a tener que evaluar críticamente soluciones de IA.
Si solo delegás, no desarrollás esa competencia."
```

### ¿Puedo desactivar los bloqueos?

**Técnicamente sí**, pero **no es recomendable** para actividades evaluativas.

Si lo hacés:
```json
"block_complete_solutions": false
```

Pero entonces **perdés el valor pedagógico** del sistema.

### ¿Cómo evalúo trabajos finales con este sistema?

**Recomendación**:
- **60%**: Evaluación automática de proceso (reporte E-IA-Proc)
- **40%**: Evaluación manual de producto (código, documentación)

**NO uses solo la evaluación automática** para nota final.

### ¿El sistema detecta plagio?

El sistema detecta **patrones sospechosos**:
- Código idéntico a soluciones de IA conocidas
- Cambios abruptos de estilo de código
- Dependencia 100% (copió y pegó todo)

Pero **NO es un detector de plagio definitivo**. Usá herramientas específicas de plagio si tenés sospechas.

---

## 📞 Soporte Técnico

Si tenés problemas con el sistema:
- Consultá el README_MVP.md
- Consultá el README_API.md
- Contactá al administrador institucional

---

**¡Éxito con tus actividades AI-Native! 🚀**

**Mag. en Ing. de Software Alberto Cortez**
Universidad Tecnológica Nacional