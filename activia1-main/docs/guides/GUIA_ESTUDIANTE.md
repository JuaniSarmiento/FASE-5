# 🎓 Guía del Estudiante - Ecosistema AI-Native

## Bienvenido al Sistema de Enseñanza-Aprendizaje con IA Generativa

Esta guía te ayudará a aprovechar al máximo el **Tutor Cognitivo AI-Native** (T-IA-Cog) para aprender programación de manera efectiva en la era de la inteligencia artificial.

---

## 📚 Índice

1. [¿Qué es el Ecosistema AI-Native?](#qué-es-el-ecosistema-ai-native)
2. [Primeros Pasos](#primeros-pasos)
3. [Cómo Usar el Tutor Cognitivo](#cómo-usar-el-tutor-cognitivo)
4. [Tipos de Interacciones](#tipos-de-interacciones)
5. [Bloqueos Pedagógicos (¿Por qué me bloquea?)](#bloqueos-pedagógicos)
6. [Tu Camino Cognitivo](#tu-camino-cognitivo)
7. [Evaluación de Procesos](#evaluación-de-procesos)
8. [Consejos y Mejores Prácticas](#consejos-y-mejores-prácticas)
9. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## ¿Qué es el Ecosistema AI-Native?

El **Ecosistema AI-Native** es un sistema educativo diseñado para enseñarte a programar **en colaboración con la IA**, no delegando pasivamente en ella.

### ¿Por qué es diferente?

En la era de ChatGPT, Copilot y otras IAs generativas, **"saber programar"** ya no significa solo escribir código manualmente. Ahora incluye:

- ✅ **Formular problemas** de manera clara para que la IA te ayude
- ✅ **Evaluar críticamente** las soluciones que la IA propone
- ✅ **Detectar errores** y vulnerabilidades en código generado
- ✅ **Justificar decisiones** de diseño y arquitectura
- ✅ **Documentar tu razonamiento** durante el proceso

### El Tutor Cognitivo (T-IA-Cog)

Tu tutor AI-Native **NO te dará el código completo**. En su lugar:

- 🤔 Te hace **preguntas socráticas** para que razones
- 💡 Te da **pistas graduadas** según tu nivel
- 📚 Te explica **conceptos** sin resolver el problema por ti
- ⚠️ Te **bloquea** si intentas delegar todo el trabajo
- 📊 **Registra tu proceso** de razonamiento (no solo el resultado)

---

## Primeros Pasos

### 1. Acceso al Sistema

**Opción A: Interfaz Web**
```
1. Abre tu navegador y ve a: http://localhost:3000
2. Selecciona "Estudiante" en la página de inicio
3. Verás la interfaz de chat con el tutor
```

**Opción B: Línea de Comandos (CLI)**
```bash
# En la carpeta del proyecto
python -m ai_native_mvp
```

### 2. Iniciar una Sesión

Cada vez que trabajes en una actividad, se crea una **sesión de aprendizaje**:

- **Session ID**: Identificador único de tu sesión
- **Actividad**: El ejercicio o trabajo práctico asignado (ej: "prog2_tp1_colas")
- **Modo**: TUTOR (para aprender) o SIMULATOR (para practicar con roles profesionales)

**Ejemplo de inicio de sesión:**
```
========================================
NUEVA SESIÓN DE APRENDIZAJE
========================================
Estudiante: estudiante_001
Actividad: prog2_tp1_colas (Colas Circulares)
Agente: T-IA-Cog (Tutor Cognitivo)
Estado: Activa
Inicio: 2025-11-19 10:30:00
========================================
```

### 3. Tu Primera Interacción

**Empieza con una pregunta conceptual:**

```
Tú: "¿Qué es una cola circular?"

Tutor T-IA-Cog:
"Excelente pregunta para empezar. Vamos a construir tu comprensión paso a paso.

Una **cola** es una estructura de datos FIFO (First In, First Out): el primer
elemento en entrar es el primero en salir, como una fila en un banco.

Antes de explicarte qué hace que una cola sea "circular", quiero que reflexiones:

1. Si implementás una cola con un arreglo de tamaño fijo, ¿qué pasa cuando hacés
   muchos dequeue()? ¿Queda espacio desperdiciado al principio?

2. ¿Cómo podrías reutilizar ese espacio liberado al principio del arreglo?

Respondé estas preguntas primero, y luego seguimos profundizando."
```

**✅ Esto es una consulta conceptual válida**: El tutor te explica y te hace reflexionar.

---

## Cómo Usar el Tutor Cognitivo

### Modos de Ayuda del Tutor

El tutor tiene **4 modos** según el tipo de ayuda que necesites:

#### 1. 🧐 Modo SOCRÁTICO
**Cuándo**: Cuando necesites entender un concepto fundamental

**El tutor hace**:
- Preguntas que te guían a descubrir la respuesta
- No te da la solución directamente
- Te ayuda a descomponer el problema

**Ejemplo:**
```
Tú: "No entiendo cómo detectar si una cola circular está llena"

Tutor:
"Pensemos juntos. En una cola circular:
- Tenés un índice 'front' (frente)
- Tenés un índice 'rear' (final)
- El arreglo tiene un tamaño fijo

Pregunta 1: Si la cola está llena, ¿qué relación hay entre 'front' y 'rear'?
Pregunta 2: ¿Cómo diferenciás una cola llena de una cola vacía si ambas pueden
            tener front == rear?"
```

#### 2. 📖 Modo EXPLICATIVO
**Cuándo**: Cuando necesites que te expliquen un concepto

**El tutor hace**:
- Explicaciones conceptuales claras
- Analogías y ejemplos del mundo real
- Diagramas y descripciones visuales

**Ejemplo:**
```
Tú: "Explicame qué es el índice módulo en una cola circular"

Tutor:
"El operador módulo (%) es clave en las colas circulares.

Imagina un reloj analógico:
- Cuando llegas a las 12, volvés a 1 (no seguís a 13, 14, 15...)
- Esto es circularidad: después del último elemento, volvés al primero

En código: (índice + 1) % capacidad

Ejemplo con capacidad = 5:
- índice 0 → (0+1) % 5 = 1 ✓
- índice 4 → (4+1) % 5 = 0 ✓ (vuelve al principio!)

Es como si el arreglo fuera circular: después del final está el inicio."
```

#### 3. 🛤️ Modo GUIADO
**Cuándo**: Cuando estés trabado en un paso específico de la implementación

**El tutor hace**:
- Pistas graduadas (de general a específica)
- NO te da código completo
- Te orienta hacia la solución

**Ejemplo:**
```
Tú: "Cómo implemento el método enqueue() sin que se sobrescriban elementos?"

Tutor (Pista Nivel 1):
"Antes de insertar un nuevo elemento, ¿qué deberías verificar?"

[Si pedís más ayuda]

Tutor (Pista Nivel 2):
"Necesitás verificar dos cosas:
1. Si la cola está llena → rechazar inserción
2. Si hay espacio → insertar y actualizar 'rear' circularmente

¿Cómo verificarías si está llena?"

[Si pedís más ayuda]

Tutor (Pista Nivel 3):
"Una estrategia común es:
  if (rear + 1) % capacidad == front:
      # Cola llena
  else:
      # Insertar en arr[rear]
      # rear = (rear + 1) % capacidad

Ahora implementalo y mostrámelo."
```

#### 4. 🤯 Modo METACOGNITIVO
**Cuándo**: Después de resolver un problema, para reflexionar

**El tutor hace**:
- Te pregunta sobre tu proceso de pensamiento
- Te ayuda a identificar errores de razonamiento
- Fortalece tu capacidad de autorregulación

**Ejemplo:**
```
Tutor:
"Ya implementaste la cola circular. Reflexionemos sobre tu proceso:

1. ¿Qué fue lo más difícil? ¿Por qué?
2. ¿Consideraste alternativas antes de elegir esta implementación?
3. ¿Cómo validaste que funciona correctamente?
4. Si tuvieras que volver a hacerlo, ¿cambiarías algo?"
```

---

## Tipos de Interacciones

### ✅ Interacciones Permitidas (NO bloqueadas)

#### 1. Consultas Conceptuales
```
✅ "¿Qué diferencia hay entre una pila y una cola?"
✅ "¿Por qué usar una cola circular en lugar de una simple?"
✅ "Explicame el concepto de complejidad temporal"
```

**Respuesta del tutor**: Explicación conceptual sin código completo.

#### 2. Solicitud de Pistas Específicas
```
✅ "No sé cómo manejar el caso cuando la cola está vacía en dequeue()"
✅ "¿Cómo detecto si un índice está 'dando la vuelta'?"
✅ "Ayudame con la condición del while en esta función"
```

**Respuesta del tutor**: Pistas graduadas que preservan el desafío cognitivo.

#### 3. Validación de Diseño
```
✅ "Planeo usar un contador para saber si está llena. ¿Es correcto?"
✅ "Mi estrategia es dejar un espacio vacío siempre. ¿Tiene sentido?"
✅ "¿Hay algún problema con mi enfoque?"
```

**Respuesta del tutor**: Retroalimentación sobre tu diseño, sin darte la solución completa.

#### 4. Revisión de Código
```
✅ "Implementé enqueue() así: [tu código]. ¿Está bien?"
✅ "¿Este código tiene errores? [tu código]"
✅ "¿Podría optimizar esto? [tu código]"
```

**Respuesta del tutor**: Análisis de tu código, identificación de errores, sugerencias de mejora.

---

### ❌ Interacciones Bloqueadas (Delegación Total)

El sistema **bloqueará** estas solicitudes porque implican **delegación total**:

#### Ejemplos de Delegación Total

```
❌ "Dame el código completo de una cola circular"
❌ "Haceme el código entero"
❌ "Resolvelo vos"
❌ "Necesito el programa terminado"
❌ "Implementa todo y dame el resultado"
```

#### ¿Qué pasa cuando te bloquean?

**Verás un mensaje como este:**

```
🛑 BLOQUEADO POR GOBERNANZA INSTITUCIONAL

Tu solicitud ha sido bloqueada porque detectamos delegación total del problema.

¿POR QUÉ?
El objetivo de este sistema NO es que la IA resuelva el problema por vos, sino
que aprendas a resolverlo CON la ayuda de la IA.

Delegar completamente el problema:
- ❌ No desarrolla tu capacidad de razonamiento
- ❌ No fortalece tu autonomía cognitiva
- ❌ No te prepara para la industria real (donde tenés que evaluar soluciones,
     no solo generarlas)

¿CÓMO CONTINUAR?
Para ayudarte efectivamente, necesito que:

1. Descompongas el problema en partes más pequeñas
2. Identifiques qué parte específica te genera dificultad
3. Compartas tu comprensión actual del problema
4. Propongas un plan inicial (aunque sea incompleto)

PREGUNTAS GUÍA:
- ¿Qué operaciones debe tener una cola?
- ¿Cuál es la diferencia entre una cola simple y una circular?
- ¿Qué estructura de datos usarías para implementarla?
- ¿Qué problemas específicos anticipás?

Reformulá tu consulta y empecemos de nuevo. Estoy aquí para guiarte, no para
sustituir tu razonamiento. 💪
```

#### Registro de Bloqueos

Cada bloqueo queda registrado en tu sesión como:
- ⚠️ Riesgo COGNITIVO: Delegación Total (ALTO)
- 📊 Afecta tu evaluación de proceso
- 🔍 Queda en tu trazabilidad N4

**No es una "penalización"**, es un indicador de que necesitás fortalecer tu autonomía.

---

## Bloqueos Pedagógicos

### ¿Por qué me bloquea el sistema?

Los bloqueos pedagógicos ocurren cuando:

1. **Delegación Total**: Pedís que la IA resuelva todo el problema
2. **Nivel de Ayuda Excesivo**: El tutor detecta que estás dependiendo demasiado de la IA
3. **Falta de Justificación**: No explicás tus decisiones de diseño
4. **Violación de Políticas**: Incumplís las políticas pedagógicas configuradas por el docente

### ¿Qué hacer cuando te bloquean?

**Paso 1: Leé el mensaje completo**
- El sistema te explica POR QUÉ fue bloqueado
- Te da preguntas guía para reformular tu solicitud

**Paso 2: Descomponé el problema**
```
En lugar de: "Dame el código completo"

Preguntá:
1. "¿Qué operaciones básicas debe tener una cola?"
2. "¿Cómo se representa una cola circular en memoria?"
3. "Planeo usar un arreglo y dos índices. ¿Es correcto?"
4. "Ayudame a pensar cómo detectar si está llena"
```

**Paso 3: Mostrá tu proceso**
```
"Estoy implementando enqueue(). Mi idea es:
1. Verificar si hay espacio
2. Insertar en arr[rear]
3. Actualizar rear circularmente

¿Está bien orientado? ¿Qué me falta considerar?"
```

### Los bloqueos son parte del aprendizaje

- ✅ Te ayudan a desarrollar autonomía
- ✅ Te preparan para la industria real
- ✅ Fortalecen tu capacidad de razonamiento

**No son un castigo**: son una redirección pedagógica.

---

## Tu Camino Cognitivo

### ¿Qué es el Camino Cognitivo?

El sistema captura **todo tu proceso de razonamiento**, no solo el resultado final. Esto se llama **Trazabilidad Cognitiva de Nivel N4**.

### Los 4 Niveles de Trazabilidad

#### N1 - Superficial
- ✅ Tu código final entregado
- ✅ Archivos del proyecto

#### N2 - Técnico
- ✅ Commits de Git
- ✅ Branches creados
- ✅ Tests ejecutados

#### N3 - Interaccional
- ✅ Prompts que enviaste al tutor
- ✅ Respuestas que recibiste
- ✅ Reintentos y correcciones

#### N4 - Cognitivo Completo
- ✅ **Intención cognitiva**: ¿Por qué preguntaste eso?
- ✅ **Decisiones de diseño**: ¿Por qué elegiste esa estructura?
- ✅ **Justificaciones**: ¿Por qué descartaste alternativas?
- ✅ **Cambios de estrategia**: ¿Cuándo cambiaste de enfoque?
- ✅ **Autocorrecciones**: ¿Detectaste errores solo?

### Ver tu Camino Cognitivo

Al finalizar una sesión, podés solicitar tu **Camino Cognitivo Reconstructed**:

```
========================================
CAMINO COGNITIVO
========================================
Sesión: prog2_tp1_colas
Estudiante: estudiante_001
Duración: 45 minutos
========================================

Fase 1: EXPLORACIÓN CONCEPTUAL (10:00 - 10:15)
  └─ Interacciones: 3
  └─ Consultas: "¿Qué es cola circular?", "Diferencia con cola simple"
  └─ Involucramiento IA: 25%
  └─ Riesgos: Ninguno
  └─ Estado: Sólido ✓

Fase 2: PLANIFICACIÓN (10:15 - 10:25)
  └─ Interacciones: 2
  └─ Decisión: Arreglo circular con dos índices (justificado ✓)
  └─ Alternativas consideradas: Lista enlazada (descartada)
  └─ Involucramiento IA: 30%
  └─ Riesgos: Ninguno

Fase 3: IMPLEMENTACIÓN (10:25 - 10:40)
  └─ Interacciones: 5
  └─ Pistas solicitadas: 2 (nivel MEDIO)
  └─ Involucramiento IA: 55%
  └─ ⚠️ Riesgo: Falta de justificación en manejo de cola llena
  └─ Autocorrección: Detectaste error en condición del while ✓

Fase 4: VALIDACIÓN (10:40 - 10:45)
  └─ Interacciones: 2
  └─ Tests implementados: 3 (casos límite cubiertos ✓)
  └─ Involucramiento IA: 20%
  └─ Riesgos: Ninguno

RESUMEN:
✅ Competencia alcanzada: EN_DESARROLLO (6/10)
📊 Dependencia IA promedio: 32.5% (ÓPTIMO - rango 20-50%)
🔄 Cambios de estrategia: 1 (planificación → implementación)
⚠️ Riesgos totales: 1 (medio)
💪 Autocorrecciones: 2

RECOMENDACIONES:
1. Mejoraste tu capacidad de descomposición ✓
2. Seguí documentando tus decisiones de diseño
3. Practicá justificar ANTES de implementar
```

---

## Evaluación de Procesos

### ¿Cómo te evalúan?

**NO te evalúan solo por el código final**. Se evalúa tu **proceso cognitivo**:

#### Dimensiones Evaluadas

1. **Descomposición de Problemas** (20%)
   - ¿Dividiste el problema en partes manejables?
   - ¿Identificaste subproblemas?

2. **Autorregulación y Metacognición** (20%)
   - ¿Monitoreaste tu progreso?
   - ¿Reflexionaste sobre tu proceso?
   - ¿Detectaste y corregiste errores?

3. **Coherencia Lógica** (20%)
   - ¿Tu razonamiento es consistente?
   - ¿Justificaste tus decisiones?

4. **Verificación y Testing** (20%)
   - ¿Creaste tests?
   - ¿Validaste casos límite?

5. **Documentación del Razonamiento** (20%)
   - ¿Documentaste POR QUÉ tomaste cada decisión?
   - ¿Consideraste alternativas?

### Niveles de Competencia

- **INICIAL** (0-3): Dependencia alta de IA, poca autonomía
- **EN_DESARROLLO** (4-6): Uso equilibrado de IA, autonomía creciente
- **COMPETENTE** (7-8): Uso estratégico de IA, autonomía sólida
- **EXPERTO** (9-10): IA como herramienta de auditoría, autonomía completa

### Reporte de Evaluación

Al finalizar, recibirás un **Reporte de Evaluación Formativa**:

```
========================================
EVALUACIÓN FORMATIVA DE PROCESO
========================================
Estudiante: estudiante_001
Actividad: prog2_tp1_colas
Fecha: 2025-11-19

NIVEL ALCANZADO: EN_DESARROLLO (6.0/10)

DIMENSIONES:
├─ Descomposición de Problemas: 8/10 (COMPETENTE) ✓
├─ Autorregulación: 4/10 (EN_DESARROLLO)
├─ Coherencia Lógica: 6/10 (EN_DESARROLLO)
├─ Verificación y Testing: 7/10 (COMPETENTE) ✓
└─ Documentación: 5/10 (EN_DESARROLLO)

FORTALEZAS:
✅ Excelente descomposición del problema
✅ Uso equilibrado de ayuda de IA (32%)
✅ Implementaste tests sin que se te solicitara

ÁREAS DE MEJORA:
⚠️ Autorregulación: Reflexioná más sobre tus errores
⚠️ Justificación: Documentá POR QUÉ tomás cada decisión
⚠️ Alternativas: Considerá otras opciones antes de decidir

RECOMENDACIONES:
1. Antes de implementar, escribí 2-3 alternativas y justificá tu elección
2. Al encontrar un error, preguntate: "¿Por qué falló? ¿Qué aprendí?"
3. Al pedir ayuda a la IA, primero formulá tu hipótesis

PRÓXIMOS PASOS:
→ Practicá con pilas (similar a colas) aplicando justificaciones explícitas
→ Enfocate en autorregulación: preguntate "¿qué aprendí?" al final
```

---

## Consejos y Mejores Prácticas

### 1. Empezá siempre con preguntas conceptuales

✅ **BIEN**:
```
"¿Qué es una cola circular?"
"¿Por qué se usa el operador módulo?"
```

❌ **MAL**:
```
"Dame el código"
```

### 2. Descomponé el problema ANTES de pedir ayuda

✅ **BIEN**:
```
"El problema tiene 3 partes:
1. Insertar elementos (enqueue)
2. Eliminar elementos (dequeue)
3. Verificar si está llena/vacía

Empiezo con enqueue. Mi plan es..."
```

❌ **MAL**:
```
"No sé por dónde empezar, hacelo vos"
```

### 3. Justificá tus decisiones

✅ **BIEN**:
```
"Elegí usar un arreglo porque:
- El tamaño máximo está definido
- Acceso O(1) por índice
- No necesito gestión dinámica de memoria

¿Tiene sentido?"
```

❌ **MAL**:
```
"Uso un arreglo porque sí"
```

### 4. Mostrá tu código ANTES de pedir correcciones

✅ **BIEN**:
```
"Implementé enqueue() así:

def enqueue(self, item):
    if self.is_full():
        raise Exception("Cola llena")
    self.arr[self.rear] = item
    self.rear = (self.rear + 1) % self.capacity

¿Tiene errores?"
```

❌ **MAL**:
```
"No me funciona enqueue, arreglalo"
```

### 5. Pedí pistas graduadas, no soluciones completas

✅ **BIEN**:
```
"No sé cómo detectar si está llena. Dame una pista general"
[Si necesitás más] "Todavía no lo veo, dame una pista más específica"
```

❌ **MAL**:
```
"Dame la condición exacta para detectar si está llena"
```

### 6. Reflexioná sobre tu proceso

✅ **BIEN**:
```
"Cometí un error: mi condición era (rear + 1) == front, pero
olvidé el módulo. Me di cuenta cuando probé con un arreglo de tamaño 5.
Aprendí que siempre debo pensar en la circularidad."
```

❌ **MAL**:
```
"No anda, arreglalo"
```

### 7. Usá la IA como co-piloto, no como piloto

```
Vos: Piloto (decidís, diseñás, implementás)
IA: Co-piloto (te asesora, te advierte, te guía)

NO al revés.
```

---

## Preguntas Frecuentes

### ¿Por qué el tutor no me da el código directamente?

Porque el objetivo es que aprendas a **razonar con IA**, no a **depender pasivamente de ella**. En la industria real, vas a tener que:
- Evaluar si el código generado es correcto
- Detectar vulnerabilidades y bugs
- Justificar decisiones de diseño
- Auditar soluciones propuestas

Si solo copiás y pegás código de la IA, no desarrollás esas competencias.

### ¿Cuándo puedo usar ChatGPT o Copilot afuera del sistema?

Podés usarlos, pero **documentá su uso**:
- ¿Qué le pediste a la IA?
- ¿Qué te respondió?
- ¿Por qué aceptaste o rechazaste su propuesta?

El sistema valora la **transparencia**: usar IA no es trampa si lo documentás y justificás.

### ¿Cómo sé si mi nivel de dependencia de IA es adecuado?

Rangos recomendados:
- **20-40%**: Óptimo (uso estratégico de IA)
- **40-60%**: Aceptable (dependencia moderada)
- **60-80%**: Alto (riesgo cognitivo)
- **>80%**: Crítico (delegación excesiva)

El sistema te avisa si superás los umbrales.

### ¿Qué pasa si me bloquean varias veces?

Los bloqueos quedan registrados y generan:
- ⚠️ Riesgos cognitivos (DELEGACIÓN TOTAL)
- 📊 Afectan tu evaluación de proceso
- 💬 El docente recibe una alerta para intervenir pedagógicamente

**No es una penalización**: es un indicador de que necesitás fortalecer tu autonomía.

### ¿Puedo ver mis trazas cognitivas?

Sí, en cualquier momento podés solicitar:
- Tu camino cognitivo de la sesión actual
- Historial de sesiones previas
- Evolución de tu dependencia de IA
- Tus fortalezas y áreas de mejora

### ¿El docente ve todo lo que hago?

El docente tiene acceso a:
- ✅ Tus trazas cognitivas N4
- ✅ Riesgos detectados
- ✅ Evaluación de tu proceso
- ✅ Prompts que enviaste al tutor
- ✅ Respuestas que recibiste

**Esto NO es vigilancia**: es trazabilidad pedagógica. El objetivo es ayudarte, no espiarte.

### ¿Cómo mejoro mi nivel de competencia?

1. **Descomponé problemas** antes de pedir ayuda
2. **Justificá decisiones** siempre
3. **Reflexioná sobre errores** (metacognición)
4. **Usá IA estratégicamente**, no pasivamente
5. **Documentá tu razonamiento**, no solo tu código

---

## 💪 Últimos Consejos

### El objetivo NO es que no uses IA

**El objetivo ES que la uses de manera inteligente y crítica.**

En la industria, vas a trabajar **con IA**, no sin ella. Pero necesitás saber:
- Cuándo confiar en la IA
- Cuándo desconfiar
- Cómo validar lo que genera
- Cómo detectar alucinaciones y errores

Este sistema te prepara para eso.

### Desarrollá tu autonomía cognitiva

La IA es poderosa, pero **vos sos el que decide, diseña y valida**.

Fortalecé:
- Tu capacidad de razonamiento
- Tu criterio técnico
- Tu habilidad de detectar errores
- Tu metacognición

### Aprendé a aprender con IA

La era de la IA generativa requiere nuevas competencias:
- ✅ Formular problemas claramente
- ✅ Evaluar críticamente soluciones
- ✅ Justificar decisiones
- ✅ Documentar razonamiento
- ✅ Auditar continuamente

Este sistema te enseña eso.

---

## 📞 Soporte

Si tenés dudas sobre el sistema:
- Consultá con tu docente
- Revisá esta guía
- Consultá el README_MVP.md del proyecto

---

**¡Buen aprendizaje! 🚀**

**Mag. en Ing. de Software Alberto Cortez**
Universidad Tecnológica Nacional