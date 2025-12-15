# Ecosistema AI-Native para Programación

## 🎓 Marco Conceptual y Epistemológico

Este MVP (Minimum Viable Product) implementa el **modelo AI-Native** conceptualizado en la tesis doctoral "Enseñanza-Aprendizaje de Programación en la Era de IA Generativa", que aborda la transformación epistemológica fundamental de lo que significa **"saber programar"** en el contexto de la inteligencia artificial generativa.

### La Mutación Epistemológica: De Escribir Código a Razonar con IA

La llegada de los modelos de lenguaje de gran escala (LLMs) y modelos especializados en código (Code LLMs) no representa una mejora incremental de herramientas existentes, sino una **reconfiguración estructural** del ciclo de ingeniería de software y de las competencias fundamentales del programador.

Tradicionalmente, "saber programar" significaba dominar sintaxis, estructuras de datos, algoritmos y patrones de diseño para **escribir código manualmente**. En la era de la IA generativa, esta definición se transforma radicalmente. Ahora, "saber programar" implica la capacidad de:

1. **Formular y descomponer problemas** en términos operables para agentes de IA
2. **Evaluar críticamente** propuestas generadas algorítmicamente
3. **Detectar inconsistencias, vulnerabilidades y alucinaciones** en código generado
4. **Sostener procesos de auditoría continua** en entornos DevOps y MLOps
5. **Documentar el razonamiento y las decisiones** en procesos híbridos humano-IA
6. **Operar bajo criterios éticos y de gobernanza** algorítmica

Esta mutación epistemológica requiere un nuevo modelo formativo que esta tesis denomina **AI-Native**: un ecosistema socio-técnico educativo que asume la presencia de IA generativa como condición estructural y articula una respuesta pedagógica, cognitiva, tecnológica e institucional integral.

---

## 🧠 Fundamentos Teóricos del Modelo AI-Native

El ecosistema AI-Native se sustenta en cuatro marcos teóricos convergentes:

### 1. Cognición Distribuida (Hutchins, 1995)

La programación con IA generativa se configura como una actividad de **razonamiento distribuido** donde el conocimiento, las decisiones y el proceso de resolución emergen de la interacción entre:

- El agente humano (estudiante/programador)
- Los sistemas de IA generativa (LLMs, Code LLMs)
- Los artefactos técnicos (código, documentación, tests, Git)

El razonamiento ya no reside exclusivamente en la mente individual, sino que emerge del **sistema socio-técnico completo**. Por tanto, evaluar solo el producto final (el código) ignora el proceso cognitivo distribuido que lo generó.

### 2. Cognición Extendida (Clark & Chalmers, 1998)

Los sistemas de IA generativa funcionan como **extensiones materiales de la mente humana**, análogos funcionales a cómo una libreta extiende la memoria o una calculadora extiende la capacidad aritmética.

Sin embargo, a diferencia de herramientas pasivas, los LLMs:
- Generan razonamientos completos
- Proponen alternativas de diseño
- Explican conceptos
- Corrigen errores

Esta capacidad activa convierte a la IA en un **co-agente cognitivo**, lo que obliga a redefinir los límites de la agencia epistémica del estudiante.

### 3. Teoría de la Carga Cognitiva (Sweller, 1988)

La IA generativa redistribuye radicalmente la carga cognitiva:

- **Reduce carga extrínseca**: La producción manual de código repetitivo o sintáctico
- **Libera carga germinal**: Para diseño, arquitectura, verificación y análisis crítico
- **Introduce nueva carga**: Auditoría de código generado, detección de alucinaciones, verificación de corrección

El modelo AI-Native aprovecha esta redistribución para elevar el nivel cognitivo de la formación: menos tiempo en sintaxis, más tiempo en razonamiento, diseño y verificación.

### 4. Autorregulación del Aprendizaje (Zimmerman, 2002)

En entornos híbridos humano-IA, la **metacognición** y la **autorregulación** se vuelven competencias centrales:

- **Planificación**: ¿Qué problema intento resolver? ¿Cómo descomponerlo? ¿Qué le pido a la IA?
- **Monitoreo**: ¿La IA comprendió mi solicitud? ¿Su respuesta es correcta? ¿Qué errores contiene?
- **Evaluación**: ¿Logré mi objetivo? ¿Qué aprendí? ¿Qué estrategias funcionaron?

El modelo AI-Native hace **explícitas** estas fases metacognitivas mediante trazabilidad cognitiva (N4) y submodelos pedagógicos especializados.

---

## 🏗️ Arquitectura C4 Extended: Integración Técnico-Pedagógica

El MVP implementa la **arquitectura C4 Extended**, que articula seis componentes técnico-pedagógicos en el **AI Gateway**:

```
┌─────────────────────────────────────────────────────────────┐
│                      AI GATEWAY (Orquestador)                │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  C3: Motor de Razonamiento Cognitivo-Pedagógico       │  │
│  │      (CRPE - Cognitive-Pedagogical Reasoning Engine)  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────┐ ┌──────────┐  │
│  │ C2: IPC     │ │ C4: GSR     │ │ C5: OSM  │ │ C6: N4   │  │
│  │ (Ingesta    │ │ (Gobernanza,│ │ (Orquest.│ │ (Trazab. │  │
│  │  Comprensión│ │  Seguridad, │ │  Submod.)│ │  Cogn.)  │  │
│  │  Prompts)   │ │  Riesgo)    │ │          │ │          │  │
│  └─────────────┘ └─────────────┘ └──────────┘ └──────────┘  │
│                                                               │
│  ┌─────────────┐                                             │
│  │ C1: Motor   │  ← Conexión a LLMs (OpenAI, Anthropic,     │
│  │     LLM     │    Claude, Gemini, modelos locales)        │
│  └─────────────┘                                             │
└───────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┴────────────────┐
           ▼                                 ▼
    ┌──────────────┐                  ┌──────────────┐
    │  SUBMODELOS  │                  │  SUBMODELOS  │
    │  PEDAGÓGICOS │                  │ INSTITUCIONAL│
    └──────────────┘                  └──────────────┘
           │                                 │
    ┌──────┴──────┬───────────┬──────┐     │
    ▼             ▼           ▼      ▼     ▼
┌─────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌─────────┐
│T-IA-Cog │ │E-IA-Proc │ │S-IA-X  │ │ AR-IA  │ │ GOV-IA  │
│         │ │          │ │        │ │        │ │         │
│ Tutor   │ │Evaluador │ │Simula- │ │Analista│ │Goberna- │
│ Cogni-  │ │Procesos  │ │dores   │ │Riesgo  │ │ción     │
│ tivo    │ │Cognitivos│ │Profes. │ │Cogn.   │ │Instit.  │
└─────────┘ └──────────┘ └────────┘ └────────┘ └─────────┘
                                                      │
                                                      ▼
                                                ┌──────────┐
                                                │  TC-N4   │
                                                │Trazabil. │
                                                │Cognitiva │
                                                └──────────┘
```

### Componentes del AI Gateway

#### C1 - Motor LLM (✅ IMPLEMENTADO con abstracción completa)
**Propósito**: Conexión estandarizada a modelos de lenguaje de gran escala mediante capa de abstracción intercambiable.

**Implementación MVP**:
El motor LLM está implementado mediante un **patrón de abstracción con factory** que permite cambiar fácilmente entre diferentes proveedores:

```python
from ai_native_mvp.llm import LLMProviderFactory, LLMMessage, LLMRole

# Mock provider (default, sin API calls)
provider = LLMProviderFactory.create("mock")

# OpenAI provider (requiere API key)
provider = LLMProviderFactory.create("openai", {"api_key": "sk-..."})

# Desde variables de entorno
provider = LLMProviderFactory.create_from_env("openai")

# Generar respuesta
messages = [
    LLMMessage(role=LLMRole.SYSTEM, content="Sos un tutor cognitivo..."),
    LLMMessage(role=LLMRole.USER, content="¿Qué es una cola?")
]
response = provider.generate(messages, temperature=0.7)
```

**Providers disponibles**:
- ✅ **MockLLMProvider**: Default para MVP, respuestas contextuales sin API calls
- ✅ **OpenAIProvider**: GPT-4, GPT-3.5-turbo (requiere `pip install openai`)
- 🔜 **AnthropicProvider**: Claude (futuro)
- 🔜 **OllamaProvider**: Modelos locales (futuro)

**Características**:
- Interfaz unificada independiente del provider
- Streaming support (para respuestas en tiempo real)
- Token counting (para control de costos)
- Configuración por environment variables
- Testeable sin costos de API (MockLLMProvider)
- Extensible: agregar nuevos providers es trivial

**Ventaja pedagógica**: El sistema funciona completamente sin conexión a APIs externas (usando MockLLM), lo que permite desarrollo, testing y demos sin costos ni dependencias de servicios cloud.

#### C2 - IPC (Ingesta y Comprensión de Prompts)
**Propósito**: Clasificar y comprender la intención cognitiva del estudiante.

**Funcionalidad**:
- Detecta el tipo de solicitud (conceptual, implementación, debugging, validación)
- Identifica el estado cognitivo (exploración, planificación, implementación, reflexión)
- Clasifica el nivel de delegación (consulta guiada vs. delegación total)
- Alimenta al CRPE con análisis semántico y pragmático del prompt

#### C3 - CRPE (Motor de Razonamiento Cognitivo-Pedagógico)
**Propósito**: **Núcleo inteligente** que decide cómo responder pedagógicamente.

**Funcionalidad**:
- Analiza el historial del estudiante (trazas previas, nivel, progreso)
- Determina la estrategia pedagógica apropiada:
  - Socrática (preguntas guía)
  - Explicativa (conceptos fundamentales)
  - Andamiada (pistas graduadas)
  - Metacognitiva (reflexión sobre el proceso)
- Evita delegación cognitiva mediante reglas pedagógicas explícitas
- Modula el nivel de ayuda según competencia y contexto

#### C4 - GSR (Gobernanza, Seguridad y Riesgo)
**Propósito**: Implementar políticas institucionales y normativas de IA.

**Funcionalidad**:
- Verifica cumplimiento de políticas en tiempo real
- Bloquea solicitudes que violan principios pedagógicos (ej: "dame el código completo")
- Aplica restricciones según nivel de estudiante y tipo de actividad
- Audita uso de IA según marcos UNESCO, OECD, ISO/IEC 23894, IEEE

#### C5 - OSM (Orquestación de Submodelos)
**Propósito**: Coordinar qué submodelo debe procesar cada interacción.

**Funcionalidad**:
- Enruta solicitudes al submodelo apropiado (tutor, evaluador, simulador)
- Gestiona transiciones entre modos (ej: de tutoría a evaluación)
- Sincroniza flujos de información entre submodelos
- Mantiene coherencia en la experiencia del estudiante

#### C6 - N4 (Trazabilidad Cognitiva de 4 Niveles)
**Propósito**: **Centro de gravedad epistémico** del sistema - captura el proceso completo.

**Funcionalidad**:
- **N1 (Superficial)**: Archivos finales, entregas
- **N2 (Técnico)**: Commits Git, branches, tests
- **N3 (Interaccional)**: Prompts, respuestas IA, logs
- **N4 (Cognitivo completo)**: Intenciones, decisiones, justificaciones, alternativas consideradas, cambios de estrategia

La trazabilidad N4 transforma el **proceso invisible** de razonamiento en un **objeto auditable**, permitiendo evaluación basada en procesos, no solo en productos.

---

## 🤖 Los 6 Submodelos AI-Native: Operativización Pedagógica

Los submodelos son agentes de IA especializados que implementan roles pedagógicos, profesionales e institucionales específicos. Representan la **traducción operativa** del modelo AI-Native.

### 1. T-IA-Cog: Tutor IA Disciplinar Cognitivo

**Propósito Pedagógico**: Guiar el razonamiento del estudiante **sin sustituir** su agencia cognitiva.

**Fundamento Teórico**:
- Cognición distribuida (Hutchins, 1995)
- Cognición extendida (Clark & Chalmers, 1998)
- Teoría de carga cognitiva (Sweller, 1988)
- Autorregulación del aprendizaje (Zimmerman, 2002)

**Principio Central**: El tutor NO entrega soluciones completas. En su lugar, aplica estrategias pedagógicas que:
- Promueven la descomposición explícita de problemas
- Exigen justificación de decisiones
- Fomentan exploración de alternativas
- Desarrollan metacognición

**Modos de Tutoría**:

1. **Modo Socrático**: Preguntas guía para inducir razonamiento
   - *Ejemplo*: "¿Qué parte del problema te genera mayor dificultad? ¿Por qué?"

2. **Modo Explicativo**: Explicaciones conceptuales profundas
   - *Ejemplo*: Explicar el concepto de cola antes de implementación

3. **Modo Guiado**: Pistas graduadas que preservan el desafío cognitivo
   - *Ejemplo*: "Considerá usar dos índices para el arreglo circular"

4. **Modo Metacognitivo**: Reflexión sobre el proceso de aprendizaje
   - *Ejemplo*: "¿Qué estrategias te ayudaron? ¿Cuáles no funcionaron?"

**Arquitectura Interna**:
- **Módulo de Diagnóstico Cognitivo Instantáneo (DCI)**: Detecta fase cognitiva actual
- **Módulo Socrático Adaptativo (MSA)**: Genera preguntas contextuales
- **Módulo de Andamiaje Controlado (MAC)**: Gradúa el nivel de ayuda
- **Módulo de Explicación Profunda (MEP)**: Explica el "por qué", no solo el "qué"

**Ejemplo de Uso**:
```python
from src.ai_native_mvp import AIGateway
from src.ai_native_mvp.core.cognitive_engine import AgentMode

gateway = AIGateway()
session_id = gateway.create_session("estudiante_001", "prog2_tp1_colas")
gateway.set_mode(session_id, AgentMode.TUTOR)

# Estudiante solicita delegación total
response = gateway.process_interaction(
    session_id,
    "Dame el código completo de una cola con arreglos"
)

# El tutor BLOQUEA la delegación y solicita descomposición
print(response['blocked'])  # True
print(response['message'])
# "He detectado que tu solicitud implica una delegación total...
#  Para ayudarte efectivamente, necesito que:
#  1. Expliques tu comprensión del problema
#  2. Descompongas el problema en partes
#  3. Compartas tu plan inicial
#  4. Identifiques tus dudas específicas"
```

---

### 2. E-IA-Proc: Evaluador de Procesos Cognitivos

**Propósito Pedagógico**: Analizar y evaluar el **proceso cognitivo híbrido humano-IA**, no solo el producto final.

**Cambio de Paradigma Evaluativo**:
- **Tradicional**: ¿El código funciona? ¿Es eficiente? ¿Sigue buenas prácticas?
- **AI-Native**: ¿Cómo razonó el estudiante? ¿Comprendió el problema? ¿Verificó críticamente la IA? ¿Documentó decisiones?

**Fundamento Epistemológico**:

En entornos con IA generativa, evaluar solo el código final es epistemológicamente inválido porque:
1. El código puede ser generado totalmente por IA
2. No hay evidencia de comprensión conceptual
3. No se puede distinguir entre razonamiento auténtico y delegación acrítica

La evaluación debe desplazarse del **producto** al **proceso de razonamiento asistido-auditado**.

**Dimensiones de Evaluación**:

1. **Descomposición de Problemas**: ¿El estudiante descompuso el problema antes de solicitar ayuda?
2. **Autorregulación y Metacognición**: ¿Planificó, monitoreó y evaluó su proceso?
3. **Coherencia Lógica**: ¿Sus decisiones son coherentes con sus justificaciones?
4. **Auditoría de IA**: ¿Verificó críticamente el código generado?
5. **Manejo de Errores**: ¿Diagnosticó errores sistemáticamente o trial-error?
6. **Documentación de Razonamiento**: ¿Explicó sus decisiones de diseño?

**Generación del IEC (Informe de Evaluación Cognitiva)**:

El evaluador produce un reporte estructurado con:
- **Nivel de competencia alcanzado** (Inicial, En desarrollo, Autónomo, Experto)
- **Puntuación por dimensión** (0-10 en cada dimensión)
- **Fortalezas clave** identificadas en el proceso
- **Áreas de mejora** específicas y accionables
- **Recomendaciones pedagógicas** para el estudiante y el docente
- **Análisis del camino cognitivo** (fases recorridas, estrategias usadas)
- **Métricas de dependencia de IA** (ratio de delegación vs. razonamiento propio)

**Lo que NO hace**:
- ❌ No asigna notas numéricas automáticamente (el docente mantiene soberanía evaluativa)
- ❌ No reemplaza al docente
- ❌ No corrige código directamente

**Ejemplo de Uso**:
```python
from src.ai_native_mvp.agents import EvaluadorProcesosAgent

evaluator = EvaluadorProcesosAgent()
trace_sequence = gateway.get_trace_sequence(session_id)
report = evaluator.evaluate_process(trace_sequence)

print(f"Nivel alcanzado: {report.overall_competency_level}")
# "en_desarrollo"

print(f"Puntuación global: {report.overall_score}/10")
# 6.5/10

print("Dimensiones evaluadas:")
for dimension in report.dimensions:
    print(f"  {dimension.name}: {dimension.score}/10 ({dimension.level})")
#   Descomposición de Problemas: 8.0/10 (autónomo)
#   Autorregulación: 5.0/10 (en_desarrollo)
#   Coherencia Lógica: 7.0/10 (en_desarrollo)

print(f"Fortalezas: {report.key_strengths}")
# ["Buena descomposición inicial", "Verificó casos edge"]

print(f"Áreas de mejora: {report.improvement_areas}")
# ["Mejorar documentación de decisiones", "Aumentar verificación crítica de IA"]
```

---

### 3. S-IA-X: Simuladores Profesionales

**Propósito Pedagógico**: Recrear **roles profesionales auténticos** de la industria del software mediante IA.

**Fundamento**: Cognición situada (Lave & Wenger, 1991) - El aprendizaje es más efectivo cuando ocurre en contextos auténticos de práctica profesional.

**Simuladores Disponibles**:

#### PO-IA (Product Owner)
- **Rol**: Análisis de requisitos, criterios de aceptación, priorización de backlog
- **Interacciones**:
  - Solicita clarificación de requisitos ambiguos
  - Pregunta por valor al usuario
  - Desafía supuestos técnicos
  - Evalúa trade-offs (tiempo, calidad, features)

#### SM-IA (Scrum Master)
- **Rol**: Facilitación de ceremonias ágiles, gestión de impedimentos
- **Interacciones**:
  - Conduce daily standup
  - Facilita retrospectivas
  - Ayuda a resolver blockers
  - Promueve mejora continua

#### IT-IA (Technical Interviewer)
- **Rol**: Evaluación técnica en formato entrevista real
- **Interacciones**:
  - Plantea problemas algorítmicos
  - Evalúa razonamiento en voz alta
  - Solicita análisis de complejidad
  - Pregunta por trade-offs de diseño

#### IR-IA (Incident Responder - DevOps)
- **Rol**: Gestión de incidentes en producción
- **Interacciones**:
  - Simula caídas de servicio
  - Solicita diagnóstico bajo presión
  - Evalúa análisis de logs
  - Pregunta por estrategias de rollback

#### CX-IA (Cliente Simulado)
- **Rol**: Cliente real con requisitos ambiguos y cambiantes
- **Interacciones**:
  - Plantea requisitos poco claros
  - Cambia de opinión (como cliente real)
  - Evalúa habilidades de comunicación
  - Desafía propuestas técnicas

#### DSO-IA (DevSecOps)
- **Rol**: Seguridad, vulnerabilidades, auditoría
- **Interacciones**:
  - Revisa código en busca de vulnerabilidades
  - Plantea escenarios de ataque
  - Evalúa conocimiento de OWASP Top 10
  - Solicita estrategias de mitigación

**Ejemplo de Uso**:
```python
from src.ai_native_mvp.agents import SimuladorProfesionalAgent, SimuladorType

# Simular entrevista técnica
simulator = SimuladorProfesionalAgent(SimuladorType.TECHNICAL_INTERVIEWER)
response = simulator.interact(
    "Necesito implementar un sistema de cache",
    context={"difficulty": "senior", "time_limit": "30min"}
)

# IT-IA pregunta:
# "¿Qué políticas de evicción consideraste? ¿LRU, LFU, FIFO?
#  ¿Cómo manejarías la concurrencia? ¿Qué complejidad temporal buscás?"
```

---

### 4. AR-IA: Analista de Riesgo Cognitivo y Ético

**Propósito**: Detectar y clasificar **riesgos derivados de la interacción humano-IA** en tiempo real.

**Aporte Original**: Este submodelo **no tiene precedente en la literatura** - es una contribución doctoral inédita.

**Fundamento**: Las fragilidades de la IA generativa (alucinaciones, sesgos, opacidad) no son anomalías aisladas sino **limitaciones estructurales del paradigma generativo** (Bender et al., 2021; Ji et al., 2023). Por tanto, se requiere monitoreo activo de riesgos.

**Las 5 Dimensiones de Riesgo**:

#### 1. Riesgos Cognitivos (RC)
**Descripción**: Deterioro del proceso de aprendizaje por uso inadecuado de IA.

**Tipos**:
- **Delegación Total (RC-DT)**: Solicitar soluciones completas sin razonamiento previo
- **Razonamiento Superficial (RC-RS)**: Aceptar respuestas sin comprensión profunda
- **Dependencia de IA (RC-DIA)**: Incapacidad de resolver sin asistencia de IA
- **Falta de Justificación (RC-FJ)**: No explicar decisiones propias

**Ejemplo detectado**:
```
Prompt: "Dame el código completo de una cola con arreglos"
↓
AR-IA detecta: RC-DT (Delegación Total)
Nivel: ALTO
Recomendación: "Bloquear y solicitar descomposición del problema"
```

#### 2. Riesgos Éticos (RE)
**Descripción**: Violaciones de integridad académica.

**Tipos**:
- **Plagio por IA (RE-PIA)**: Presentar código generado por IA como propio
- **Uso No Declarado (RE-UND)**: No documentar cuándo y cómo se usó IA
- **Fraude Académico (RE-FA)**: Engaño intencional sobre autoría

#### 3. Riesgos Epistémicos (REp)
**Descripción**: Errores conceptuales y aceptación acrítica.

**Tipos**:
- **Aceptación Acrítica (REp-AA)**: No verificar corrección de código generado
- **Error Conceptual (REp-EC)**: Malinterpretar conceptos explicados por IA
- **Falacia Lógica (REp-FL)**: Razonamiento inválido en interacción con IA

#### 4. Riesgos Técnicos (RT)
**Descripción**: Vulnerabilidades y mala calidad de código.

**Tipos**:
- **Vulnerabilidad de Seguridad (RT-VS)**: Código generado con fallos de seguridad
- **Baja Calidad (RT-BQ)**: Código ineficiente o mal estructurado
- **Deuda Técnica (RT-DT)**: Soluciones rápidas que generan problemas futuros

#### 5. Riesgos de Gobernanza (RG)
**Descripción**: Violación de políticas institucionales.

**Tipos**:
- **Violación de Política (RG-VP)**: Uso de IA fuera de lineamientos
- **Uso No Autorizado (RG-UNA)**: Herramientas no aprobadas institucionalmente

**Marcos Normativos Implementados**:
- UNESCO (2021): Recomendación sobre Ética de IA
- OECD (2019): Principios de IA
- IEEE (2019): Ethically Aligned Design
- ISO/IEC 23894:2023: Risk Management in AI
- ISO/IEC 42001:2023: AI Management System

**Generación del Reporte de Riesgo**:
```python
from src.ai_native_mvp.agents import AnalistaRiesgoAgent

analyst = AnalistaRiesgoAgent()
risk_report = analyst.analyze_session(trace_sequence)

print(f"Total de riesgos: {risk_report.total_risks}")
print(f"  Críticos: {risk_report.critical_risks}")
print(f"  Altos: {risk_report.high_risks}")
print(f"  Medios: {risk_report.medium_risks}")

for risk in risk_report.risks:
    print(f"\n{risk.risk_type} ({risk.risk_level})")
    print(f"  Dimensión: {risk.dimension}")
    print(f"  Descripción: {risk.description}")
    print(f"  Recomendaciones: {risk.recommendations}")
```

---

### 5. GOV-IA: Gobernanza Institucional

**Propósito**: Operacionalizar la gobernanza de IA de manera **activa, automatizada y verificable**.

**Cambio de Paradigma**: La gobernanza deja de ser un documento declarativo externo para convertirse en parte **operativa** del sistema educativo.

**Funciones Principales**:

1. **Verificación de Cumplimiento en Tiempo Real**
   - Evalúa cada interacción estudiante-IA contra políticas institucionales
   - Bloquea solicitudes que violan principios pedagógicos
   - Registra todas las verificaciones para auditoría

2. **Gestión del Riesgo según ISO/IEC 23894**
   - Implementa el ciclo completo de gestión de riesgo:
     - Identificación
     - Análisis
     - Evaluación
     - Tratamiento
     - Monitoreo continuo

3. **Auditoría y Trazabilidad para Acreditación**
   - Genera reportes para CONEAU (Argentina)
   - Demuestra cumplimiento de estándares de calidad
   - Provee evidencia objetiva de gobernanza efectiva

4. **Generación de Reportes Institucionales**
   - Estadísticas de uso de IA por asignatura
   - Análisis de riesgos a nivel carrera
   - Efectividad de políticas implementadas

**Políticas Implementadas**:

```python
# Ejemplo de política: Nivel máximo de asistencia
MAX_AI_ASSISTANCE_LEVEL = 0.7  # 70% del proceso debe ser del estudiante

# Política: Bloqueo de delegación total
if prompt_classification == "FULL_DELEGATION":
    block_request()
    request_problem_decomposition()

# Política: Trazabilidad obligatoria
if interaction_with_ai:
    require_trace_n4()
    document_reasoning()

# Política: Restricción por nivel
if student_level == "BEGINNER" and request_type == "ADVANCED_PATTERN":
    suggest_fundamentals_first()
```

**Ejemplo de Verificación**:
```python
# GOV-IA en acción
response = gateway.process_interaction(
    session_id,
    "Resolveme este ejercicio completo"
)

# GOV-IA detecta violación de política y bloquea
assert response['blocked'] == True
assert "delegación total" in response['reason'].lower()

# Se registra en auditoría institucional
audit_log = {
    "student_id": "estudiante_001",
    "timestamp": "2025-11-18T10:30:00",
    "policy_violated": "NO_FULL_DELEGATION",
    "action_taken": "BLOCKED_AND_REDIRECTED",
    "pedagogical_intent": "PROMOTE_AUTONOMY"
}
```

---

### 6. TC-N4: Trazabilidad Cognitiva de 4 Niveles

**Propósito**: Capturar y reconstruir el **proceso completo de razonamiento híbrido humano-IA**.

**Aporte Central**: Transforma el **razonamiento invisible** en un **objeto auditable**, permitiendo evaluación epistémicamente válida.

**Los 4 Niveles de Trazabilidad**:

#### N1 - Nivel Superficial (Producto Final)
**Qué captura**:
- Archivos finales entregados
- Versión final del código
- Documentación final

**Limitación**: No hay evidencia de proceso, comprensión o autoría.

#### N2 - Nivel Técnico (Control de Versiones)
**Qué captura**:
- Commits Git con mensajes
- Branches y merges
- Tests automatizados
- Code reviews

**Avance**: Permite reconstruir evolución del código, pero no razonamiento.

#### N3 - Nivel Interaccional (Logs de Interacción)
**Qué captura**:
- Prompts enviados a IA
- Respuestas de IA
- Reintentos y refinamientos
- Logs de ejecución
- Errores y correcciones

**Avance**: Documenta la interacción humano-IA, pero no la intención cognitiva.

#### N4 - Nivel Cognitivo Completo (Razonamiento Explícito)
**Qué captura**:
- **Intención cognitiva**: ¿Qué intento lograr? ¿Por qué?
- **Decisiones**: ¿Qué alternativas consideré? ¿Por qué elegí esta?
- **Justificaciones**: ¿Cuál es mi razonamiento? ¿En qué me baso?
- **Alternativas consideradas**: ¿Qué otros enfoques evalué?
- **Cambios de estrategia**: ¿Cuándo cambié de enfoque? ¿Por qué?
- **Auditorías**: ¿Qué verificaciones hice del código generado?
- **Metacognición**: ¿Qué aprendí? ¿Qué estrategias funcionaron?

**Estructura de una Traza N4**:
```python
from src.ai_native_mvp.models.trace import CognitiveTrace, TraceLevel, InteractionType
from src.ai_native_mvp.core.cognitive_engine import CognitiveState

trace = CognitiveTrace(
    id="trace_12345",
    session_id="session_001",
    student_id="estudiante_001",
    activity_id="prog2_tp1_colas",

    # Nivel N4 - Campos cognitivos
    trace_level=TraceLevel.N4_COGNITIVO,
    interaction_type=InteractionType.STUDENT_PROMPT,
    cognitive_state=CognitiveState.PLANIFICACION,

    # Contenido y contexto
    content="Planeo usar un arreglo circular con dos índices front y rear",

    # Metadatos cognitivos N4
    cognitive_intent="Validar mi diseño antes de implementar",
    decision_justification="Elegí arreglo circular porque es O(1) para enqueue y dequeue",
    alternatives_considered=[
        "Lista enlazada simple (descartada por overhead de punteros)",
        "Arreglo con desplazamiento (descartado por O(n) en dequeue)"
    ],
    strategy_type="design_validation",

    # Nivel de involucramiento de IA
    ai_involvement=0.3,  # 30% - Solo validación, diseño es propio

    # Metadatos adicionales
    metadata={
        "blocked": False,
        "response_type": "socratic_question",
        "pedagogical_strategy": "validate_reasoning"
    }
)
```

**Reconstrucción del Camino Cognitivo**:
```python
from src.ai_native_mvp.agents import TrazabilidadN4Agent

n4 = TrazabilidadN4Agent()
cognitive_path = n4.reconstruct_cognitive_path(session_id)

print("Camino cognitivo completo:")
print(f"  Fases recorridas: {cognitive_path['phases']}")
# ['exploracion', 'planificacion', 'implementacion', 'validacion']

print(f"  Decisiones clave: {len(cognitive_path['key_decisions'])}")
# 7 decisiones de diseño documentadas

print(f"  Cambios de estrategia: {cognitive_path['strategy_changes']}")
# 2 pivotes significativos

print(f"  Dependencia de IA: {cognitive_path['ai_dependency_score']:.1%}")
# 35% - Balance saludable entre autonomía y asistencia

print(f"  Auditorías realizadas: {cognitive_path['audits_performed']}")
# 4 verificaciones críticas del código generado
```

**Valor para Acreditación**:

La trazabilidad N4 permite responder a CONEAU:

❓ *¿Cómo garantizan que el estudiante aprendió?*
✅ Evidencia N4 de razonamiento, decisiones y metacognición

❓ *¿Cómo previenen el plagio con IA?*
✅ Trazabilidad completa documenta autoría del proceso

❓ *¿Cómo evalúan en era de IA generativa?*
✅ Evaluación basada en proceso cognitivo, no solo producto

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.10 o superior
- Git (para trazabilidad N2)
- 4GB RAM mínimo
- Sistema operativo: Windows, Linux o macOS

### Instalación

```bash
# 1. Clonar el repositorio
cd Tesis

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
# En Windows:
.venv\Scripts\activate

# En Unix/macOS:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Inicializar base de datos (SQLite por defecto)
python scripts/init_database.py

# 6. Verificar instalación
python -c "from src.ai_native_mvp import AIGateway; print('✅ Instalación exitosa')"
```

### Configuración Opcional

```bash
# Inicializar con PostgreSQL (producción)
python scripts/init_database.py \
  --database-url "postgresql://user:pass@localhost/ai_native"

# Inicializar con datos de ejemplo
python scripts/init_database.py --sample-data

# Generar reporte de cobertura de tests
pytest tests/ -v --cov --cov-report=html
```

---

## 💻 Uso del Sistema

### 1. Interfaz CLI Interactiva

La CLI permite interacción directa con todos los submodelos:

```bash
python -m src.ai_native_mvp.cli
```

**Flujo de la CLI**:
1. Identificación del estudiante
2. Selección de actividad
3. Elección de modo (Tutor, Simulador, Evaluador)
4. Interacción continua
5. Visualización de trazas N4
6. Generación de evaluación
7. Análisis de riesgos

**Comandos disponibles**:
- `salir` - Terminar sesión
- `eval` - Generar evaluación de procesos
- `riesgos` - Ver análisis de riesgos
- `trazas` - Ver trazabilidad N4

### 2. Uso Programático (API Python)

#### Ejemplo Básico: Sesión de Tutoría

```python
from src.ai_native_mvp import AIGateway
from src.ai_native_mvp.core.cognitive_engine import AgentMode

# 1. Crear gateway
gateway = AIGateway()

# 2. Crear sesión de aprendizaje
session_id = gateway.create_session(
    student_id="estudiante_001",
    activity_id="prog2_tp1_colas"
)

# 3. Configurar modo Tutor
gateway.set_mode(session_id, AgentMode.TUTOR)

# 4. Primera interacción: Exploración conceptual
response1 = gateway.process_interaction(
    session_id=session_id,
    prompt="No entiendo qué es una cola. ¿Me podés explicar?"
)
print(response1['message'])
# Tutor proporciona explicación conceptual

# 5. Segunda interacción: Planificación
response2 = gateway.process_interaction(
    session_id=session_id,
    prompt="Planeo usar un arreglo circular con dos índices. ¿Es correcto?"
)
print(response2['message'])
# Tutor valida el diseño con preguntas socráticas

# 6. Tercera interacción: Intento de delegación (será bloqueado)
response3 = gateway.process_interaction(
    session_id=session_id,
    prompt="Dame el código completo de la cola"
)
print(response3['blocked'])  # True
print(response3['message'])
# "He detectado delegación total. Necesito que descompongas el problema..."
```

#### Ejemplo Avanzado: Flujo Completo con Evaluación

```python
from src.ai_native_mvp import AIGateway
from src.ai_native_mvp.agents import (
    EvaluadorProcesosAgent,
    AnalistaRiesgoAgent,
    TrazabilidadN4Agent
)

# 1. Configurar sesión
gateway = AIGateway()
session_id = gateway.create_session("estudiante_002", "prog2_tp2_arboles")

# 2. Simular secuencia de interacciones
prompts = [
    "¿Qué es un árbol binario de búsqueda?",
    "¿Cómo implemento la inserción?",
    "Planeo usar recursión. ¿Hay alternativa iterativa?",
    "¿Cómo valido que el árbol mantiene la propiedad BST?"
]

for prompt in prompts:
    gateway.process_interaction(session_id, prompt)

# 3. Obtener trazabilidad N4
n4_agent = TrazabilidadN4Agent()
trace_sequence = gateway.get_trace_sequence(session_id)
cognitive_path = n4_agent.reconstruct_cognitive_path(trace_sequence)

print("Camino cognitivo:")
print(f"  Fases: {cognitive_path.get_cognitive_path()}")
print(f"  Cambios de estrategia: {trace_sequence.strategy_changes}")
print(f"  Dependencia IA: {trace_sequence.ai_dependency_score:.1%}")

# 4. Evaluación de procesos (E-IA-Proc)
evaluator = EvaluadorProcesosAgent()
evaluation = evaluator.evaluate_process(trace_sequence)

print("\nEvaluación:")
print(f"  Nivel: {evaluation.overall_competency_level}")
print(f"  Puntuación: {evaluation.overall_score}/10")
print(f"  Fortalezas: {evaluation.key_strengths}")
print(f"  Mejoras: {evaluation.improvement_areas}")

# 5. Análisis de riesgos (AR-IA)
analyst = AnalistaRiesgoAgent()
risk_report = analyst.analyze_session(trace_sequence)

print("\nRiesgos:")
print(f"  Total: {risk_report.total_risks}")
print(f"  Críticos: {risk_report.critical_risks}")
print(f"  Evaluación: {risk_report.overall_assessment}")

# 6. Generar reporte consolidado para docente
docente_report = {
    "estudiante": "estudiante_002",
    "actividad": "prog2_tp2_arboles",
    "interacciones": len(trace_sequence.traces),
    "nivel_competencia": evaluation.overall_competency_level.value,
    "puntuacion": evaluation.overall_score,
    "dependencia_ia": f"{trace_sequence.ai_dependency_score:.1%}",
    "riesgos_detectados": risk_report.total_risks,
    "camino_cognitivo": cognitive_path.get_cognitive_path(),
    "recomendaciones": evaluation.recommendations_teacher
}

print("\nReporte para docente:", docente_report)
```

#### Ejemplo: Simulador Profesional

```python
from src.ai_native_mvp.agents import SimuladorProfesionalAgent, SimuladorType

# Simular entrevista técnica
interviewer = SimuladorProfesionalAgent(SimuladorType.TECHNICAL_INTERVIEWER)

# Primera pregunta
response1 = interviewer.interact(
    "Implementá un algoritmo que detecte ciclos en un grafo",
    context={
        "difficulty": "senior",
        "time_limit": "45min",
        "allow_hints": True
    }
)

print("Entrevistador:", response1['message'])
# "Interesante problema. Antes de que empieces a codear,
#  ¿podrías explicarme qué enfoques conocés para detectar ciclos?
#  ¿Qué diferencias hay entre grafos dirigidos y no dirigidos?"

# Respuesta del estudiante
response2 = interviewer.interact(
    "Puedo usar DFS con un set de visitados...",
    context={"previous_response": response1}
)

print("Entrevistador:", response2['message'])
# "Bien, DFS es un enfoque válido. ¿Pero cómo distinguís entre
#  un nodo ya visitado en el camino actual vs. visitado en otro camino?
#  Esto es clave para grafos dirigidos..."
```

---

## 📊 Ejemplo Completo de Ejecución

El repositorio incluye `examples/ejemplo_basico.py` que demuestra todo el flujo:

```bash
python examples/ejemplo_basico.py
```

**Salida esperada**:

```
======================================================================
EJEMPLO BÁSICO: Ecosistema AI-Native
======================================================================

[1] Inicializando AI Gateway...
[2] Creando sesión de aprendizaje...
    ✓ Sesión creada: 8e83faae-1bd8-4afe-aa4d-1f48d57fddd0

[3] Configurando modo T-IA-Cog (Tutor)...

[4] Simulando interacciones estudiante-IA...

--- Interacción 1 ---
Estudiante: Dame el código completo de una cola con arreglos...
❌ BLOQUEADO: Delegación total detectada.

Tutor: "He detectado que tu solicitud implica una delegación total
del problema a la IA. Para poder ayudarte efectivamente, necesito que:

1. Expliques tu comprensión del problema
2. Descompongas el problema en partes
3. Compartas tu plan inicial
4. Identifiques tus dudas específicas"

--- Interacción 2 ---
Estudiante: No entiendo qué es una cola. ¿Me podés explicar?
🤖 Tutor: [Explicación conceptual profunda]

--- Interacción 3 ---
Estudiante: Planeo usar un arreglo circular con dos índices...
🤖 Tutor: [Preguntas socráticas de validación]

======================================================================
[5] Análisis de Trazabilidad N4
======================================================================

Total de trazas capturadas: 6
Cambios de estrategia: 0
Dependencia de IA: 0.0%

Camino cognitivo:
  1. implementacion (delegación - bloqueada)
  2. exploracion (conceptual)
  3. validacion (diseño propio)

======================================================================
[6] Evaluación de Procesos Cognitivos (E-IA-Proc)
======================================================================

📊 Nivel de competencia: en_desarrollo
📈 Puntuación: 5.0/10

Dimensiones evaluadas:
  • Descomposición de Problemas: 10.0/10 (experto)
  • Autorregulación y Metacognición: 0.0/10 (inicial)
  • Coherencia Lógica: 5.0/10 (en_desarrollo)

✅ Fortalezas:
  • Buena planificación inicial

⚠️  Áreas de mejora:
  • Mejorar: Autorregulación y Metacognición
  • Mejorar: Coherencia Lógica

======================================================================
[7] Análisis de Riesgos (AR-IA)
======================================================================

⚠️  Total de riesgos detectados: 1
  🔴 Críticos: 0
  🟠 Altos: 0
  🟡 Medios: 1

Riesgos principales:
  • lack_justification (medium)
    Baja tasa de justificación de decisiones: 0.00%
    💡 Recomendación: Exigir explícitamente justificaciones

Evaluación general:
  BAJO: Proceso dentro de parámetros esperados

======================================================================
✅ Ejemplo completado exitosamente
======================================================================
```

---

## 🔬 Contribución Doctoral Original

Este MVP materializa **seis aportes originales** para la literatura científica y la educación superior en ingeniería:

### 1. Primera Implementación de Submodelos IA Pedagógicos Especializados

**Novedad**: No existe precedente de un sistema que articule:
- Tutor IA con teoría cognitiva explícita (T-IA-Cog)
- Evaluador de procesos híbridos humano-IA (E-IA-Proc)
- Simuladores profesionales situados (S-IA-X)
- Analista de riesgo cognitivo y ético (AR-IA)
- Gobernanza algorítmica operativa (GOV-IA)
- Trazabilidad cognitiva de 4 niveles (TC-N4)

**Estado del arte**: Los sistemas existentes solo implementan asistencia técnica (copilots), no pedagogía cognitiva ni gobernanza.

### 2. Arquitectura Cognitivo-Pedagógica C4 Extended

**Novedad**: Integra dimensiones técnicas (C1-C6) con marcos cognitivos (cognición distribuida, carga cognitiva, autorregulación).

**Diferencia con C4 clásico**: El C4 tradicional (Context, Containers, Components, Code) es puramente técnico. El C4 Extended incorpora componentes pedagógicos (CRPE, GSR, N4).

### 3. Sistema de Trazabilidad Cognitiva N4

**Novedad**: Primer sistema que captura **razonamiento explícito** en interacciones humano-IA.

**Transformación epistemológica**: Convierte el proceso invisible en objeto auditable, permitiendo evaluación válida en era de IA generativa.

**Impacto**: Resuelve el problema de validez evaluativa que enfrenta toda la educación superior con IA generativa.

### 4. Analista de Riesgo Cognitivo y Ético (AR-IA)

**Novedad absoluta**: No existe precedente en la literatura de un sistema que:
- Detecte riesgos cognitivos en tiempo real
- Clasifique en 5 dimensiones (cognitivo, ético, epistémico, técnico, gobernanza)
- Opere bajo marcos UNESCO, OECD, IEEE, ISO/IEC

**Valor preventivo**: Protege la "salud cognitiva" del aprendizaje, detectando deterioro antes de que se cristalice.

### 5. Gobernanza Activa y Automatizada

**Novedad**: La gobernanza deja de ser declarativa (documento PDF) para convertirse en **componente operativo** del sistema educativo.

**Cumplimiento normativo**:
- UNESCO (2021): Ética de IA en educación
- OECD (2019): AI Principles
- ISO/IEC 23894:2023: Risk Management
- ISO/IEC 42001:2023: AI Management System
- IEEE (2019): Ethically Aligned Design

### 6. Evaluación de Procesos Cognitivos Híbridos Humano-IA

**Cambio de paradigma evaluativo**:
- Tradicional: ¿El código funciona?
- AI-Native: ¿Cómo razonó el estudiante con asistencia de IA?

**Validez epistémica**: En era de IA generativa, evaluar solo productos es inválido. Este modelo evalúa **procesos de razonamiento asistido-auditado**.

---

## 📋 Limitaciones del MVP

Este es un MVP con fines de **demostración académica y validación conceptual**. Para implementación en producción se requeriría:

### Integraciones Técnicas Faltantes

1. **LLM Real**:
   - ❌ MVP: Mock provider simulado
   - ✅ Producción: OpenAI GPT-4, Anthropic Claude, Google Gemini, modelos locales

2. **Base de Datos Escalable**:
   - ❌ MVP: SQLite en archivo
   - ✅ Producción: PostgreSQL, MongoDB, time-series DB para trazas

3. **Autenticación y Autorización**:
   - ❌ MVP: Sin auth
   - ✅ Producción: OAuth2, SAML, integración con directorio institucional

4. **Integración con LMS**:
   - ❌ MVP: Standalone
   - ✅ Producción: LTI 1.3 con Moodle, Canvas, Blackboard

5. **Integración con Git Institucional**:
   - ❌ MVP: Sin integración
   - ✅ Producción: GitLab/GitHub Enterprise para trazabilidad N2

6. **APIs RESTful/GraphQL**:
   - ❌ MVP: Solo API Python
   - ✅ Producción: FastAPI con OpenAPI spec completa

7. **Dashboard para Docentes**:
   - ❌ MVP: Solo CLI y scripts
   - ✅ Producción: React/Vue dashboard con visualización de trazas N4

8. **Orquestación de Workflows**:
   - ❌ MVP: Lógica embebida
   - ✅ Producción: n8n, Apache Airflow para workflows complejos

9. **Observabilidad**:
   - ❌ MVP: Logs básicos
   - ✅ Producción: Prometheus, Grafana, ELK stack

10. **Testing Exhaustivo**:
    - ⚠️ MVP: 70% coverage básico
    - ✅ Producción: >90% coverage, integration tests, E2E tests

11. **Escalabilidad**:
    - ❌ MVP: Monolito single-threaded
    - ✅ Producción: Microservicios, async/await, caching, load balancing

### Limitaciones Pedagógicas del MVP

1. **Contenido Curricular Limitado**:
   - MVP: Solo ejemplos de colas y árboles
   - Producción: Currículum completo de Tecnicatura (8 semestres)

2. **Simuladores Simplificados**:
   - MVP: Respuestas template-based
   - Producción: LLM fine-tuned con casos reales de industria

3. **Análisis de Código Estático**:
   - MVP: Sin análisis AST
   - Producción: SonarQube, ESLint, análisis de complejidad

4. **Feedback Adaptativo Limitado**:
   - MVP: Reglas básicas
   - Producción: ML models para personalización

---

## 🎯 Impacto Esperado y Transferibilidad

### Para Universidades

El modelo AI-Native es **replicable y transferible** a:

1. **Otras carreras de programación/ingeniería**:
   - Tecnicaturas en Desarrollo de Software
   - Ingenierías en Sistemas/Computación
   - Licenciaturas en Ciencias de la Computación

2. **Otras disciplinas con IA generativa**:
   - Redacción académica (IA para escritura)
   - Diseño gráfico (IA generativa visual)
   - Análisis de datos (IA para Data Science)

3. **Acreditación y calidad**:
   - Evidencia objetiva para CONEAU (Argentina)
   - Cumplimiento de estándares ACM/IEEE-CS 2023
   - Demostración de gobernanza efectiva de IA

### Para Estudiantes

1. **Competencias del siglo XXI**:
   - Pensamiento crítico con IA
   - Auditoría algorítmica
   - Razonamiento híbrido humano-IA
   - Documentación de decisiones
   - Ética aplicada en tecnología

2. **Empleabilidad**:
   - Experiencia con workflows reales de industria
   - Portfolio de proceso (no solo productos)
   - Certificación de gobernanza de IA

### Para Docentes

1. **Evidencia objetiva de aprendizaje**:
   - Trazabilidad N4 completa
   - Evaluaciones basadas en proceso
   - Reportes automatizados

2. **Reducción de carga administrativa**:
   - E-IA-Proc genera pre-evaluaciones
   - AR-IA detecta riesgos automáticamente
   - GOV-IA audita cumplimiento

3. **Foco en mediación pedagógica**:
   - Menos tiempo corrigiendo código
   - Más tiempo guiando razonamiento

---

## 📚 Referencias Bibliográficas

### Teorías Cognitivas

- **Hutchins, E. (1995)**. *Cognition in the Wild*. MIT Press.
- **Clark, A. & Chalmers, D. (1998)**. "The Extended Mind". *Analysis*, 58(1), 7-19.
- **Sweller, J. (1988)**. "Cognitive Load During Problem Solving: Effects on Learning". *Cognitive Science*, 12(2), 257-285.
- **Zimmerman, B. J. (2002)**. "Becoming a Self-Regulated Learner: An Overview". *Theory Into Practice*, 41(2), 64-70.
- **Hollan, J., Hutchins, E., & Kirsh, D. (2000)**. "Distributed Cognition: Toward a New Foundation for Human-Computer Interaction Research". *ACM TOCHI*, 7(2), 174-196.

### IA Generativa y Educación

- **Denny, P., et al. (2024)**. "Computing Education in the Era of Generative AI". *Communications of the ACM*, 67(2), 56-67.
- **Bender, E. M., et al. (2021)**. "On the Dangers of Stochastic Parrots: Can Language Models Be Too Big?" *ACM FAccT*.
- **Ji, Z., et al. (2023)**. "Survey of Hallucination in Natural Language Generation". *ACM Computing Surveys*, 55(12), 1-38.
- **Sarsa, S., et al. (2022)**. "Automatic Generation of Programming Exercises and Code Explanations Using Large Language Models". *ICER 2022*.

### Marcos Normativos

- **UNESCO (2021)**. *Recommendation on the Ethics of Artificial Intelligence*.
- **OECD (2019)**. *OECD Principles on Artificial Intelligence*.
- **IEEE (2019)**. *Ethically Aligned Design: A Vision for Prioritizing Human Well-being with Autonomous and Intelligent Systems*.
- **ISO/IEC 23894:2023**. *Information Technology — Artificial Intelligence — Guidance on Risk Management*.
- **ISO/IEC 42001:2023**. *Information Technology — Artificial Intelligence — Management System*.
- **ACM/IEEE-CS (2023)**. *Computing Curricula 2023: A Comprehensive Guide to Undergraduate Degree Programs in Computing*.

### Metodología de Investigación

- **Design-Based Research Collective (2003)**. "Design-Based Research: An Emerging Paradigm for Educational Inquiry". *Educational Researcher*, 32(1), 5-8.
- **McKenney, S. & Reeves, T. C. (2018)**. *Conducting Educational Design Research*. Routledge.

---

## 👥 Autoría y Contexto

### Autor

**Mag. en Ing. de Software Alberto Cortez**

Tesis Doctoral: "Enseñanza-Aprendizaje de Programación en la Era de IA Generativa"

### Institución

**Tecnicatura Universitaria en Programación con IA Nativa**

Proyecto piloto para validación del modelo AI-Native en contexto real.

### Metodología de Investigación

**Design-Based Research (DBR)**:
1. Análisis del problema (Capítulos 1-3)
2. Diseño del modelo (Capítulo 6)
3. Implementación del MVP (este repositorio)
4. Piloto en aula real (Capítulo 7)
5. Iteración y refinamiento

---

## 📄 Licencia y Uso Académico

Este MVP es parte de una investigación doctoral y está disponible para:

✅ **Uso académico y de investigación**
✅ **Replicación en otras instituciones** (citando la tesis)
✅ **Adaptación para otras disciplinas**
✅ **Pilotaje experimental**

⚠️ **Se requiere citar**:
```
Cortez, A. (2025). Ecosistema AI-Native para Programación: Implementación
de un Modelo Formativo con Trazabilidad Cognitiva y Gobernanza Algorítmica
en la Era de IA Generativa. Tesis Doctoral, [Universidad].
```

---

## 🔗 Recursos Adicionales

### Documentación Completa

- **Tesis completa**: `tesis.txt` (2,619 líneas, fundamentación teórica completa)
- **Guía de implementación**: `CLAUDE.md` (guía técnica para desarrolladores)
- **Mejoras arquitecturales**: `IMPLEMENTACIONES_ARQUITECTURALES.md`

### Ejemplos de Código

- **Ejemplo básico**: `examples/ejemplo_basico.py`
- **Tests de componentes**: `tests/`
- **Scripts de inicialización**: `scripts/init_database.py`

### Contacto

Para consultas académicas, colaboraciones o réplicas del modelo:
- Repositorio: [Incluir URL cuando esté público]
- Email: [Contacto institucional]

---

**Última actualización**: 18 de noviembre de 2025

**Estado del MVP**: ✅ **Totalmente funcional y ejecutable**

**Próximos pasos**: Pilotaje en aula real (Capítulo 7 de la tesis)