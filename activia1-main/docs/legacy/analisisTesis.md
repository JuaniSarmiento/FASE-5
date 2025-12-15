# Análisis del Capítulo 6 de la Tesis Doctoral

**Documento analizado**: `capitulo6.docx`
**Fecha de análisis**: 2025-12-07
**Propósito**: Mapear la arquitectura teórica del ecosistema AI-Native con su implementación en código.

---

## 1. Estructura del Documento

El Capítulo 6 define la **arquitectura del ecosistema AI-Native** para enseñanza de programación con IA generativa. Contiene las siguientes secciones principales:

| Sección | Contenido |
|---------|-----------|
| **6.4** | Arquitectura C4 extendida (4 niveles) |
| **6.5** | Integración curricular y operacional |
| **6.6** | Submodelo 1: T-IA-Cog (Tutor Cognitivo) |
| **6.7** | Submodelo 2: E-IA-Proc (Evaluador de Procesos) |
| **6.8** | Submodelo 3: S-IA-X (Simuladores Profesionales) |
| **6.9** | Submodelo 4: AR-IA (Analista de Riesgo Cognitivo) |
| **6.10** | Submodelo 5: GOV-IA (Gobernanza Institucional) |
| **6.11** | Submodelo 6: N4 (Trazabilidad Cognitiva) |

---

## 2. Arquitectura C4 Extendida

El documento define **4 niveles arquitectónicos** que extienden el marco C4 tradicional hacia una lectura socio-técnica y cognitiva:

### 2.1. Nivel 1 – Contexto

Ubica al ecosistema AI-Native en relación con:
- Estudiantes
- Docentes
- Gestión académica
- Servicios de IA
- Sistemas institucionales
- Marcos normativos

### 2.2. Nivel 2 – Contenedores (9 contenedores)

| Contenedor | Descripción | Implementación en Código |
|------------|-------------|-------------------------|
| A. Moodle-LMS | Aula virtual UTN | Integración LTI (schema existe, pendiente integración completa) |
| B. ai-gateway | FastAPI + orquestación cognitiva | ✅ `backend/core/ai_gateway.py` |
| C. Servicios IA generativa | LLM externos o locales | ✅ `backend/llm/` (Ollama, OpenAI, Mock) |
| D. Repositorio Git | Institucional | ✅ `backend/agents/git_integration.py` |
| E. Base N4 | Trazabilidad cognitiva | ✅ `backend/database/models.py` → `CognitiveTraceDB` |
| F. n8n | Orquestador institucional de flujos | ❌ Pendiente integración |
| G. Sistema gobernanza/riesgo | Ética y riesgo | ✅ `backend/agents/governance.py`, `risk_analyst.py` |
| H. Observabilidad | Logging y telemetría | ✅ Prometheus metrics, structured logging |
| I. Docente/estudiante | Agentes cognitivos | Frontend React |

Cada contenedor se caracteriza por:
- **Responsabilidad técnica**: funciones de software o infraestructura
- **Responsabilidad cognitiva**: papel en la distribución del razonamiento
- **Responsabilidad pedagógica**: contribución a la formación y evaluación
- **Responsabilidad normativa**: marco legal, ético y de riesgo
- **Interfaces**: conexiones con otros contenedores
- **Riesgos asociados**: vulnerabilidades técnicas, cognitivas o éticas
- **Dependencias**: otros contenedores necesarios

### 2.3. Nivel 3 – Componentes del ai-gateway (7 componentes)

| Componente | Descripción | Implementación |
|------------|-------------|----------------|
| C1. Autenticación/Autorización/LTI | Determina usuario, rol, niveles de agencia IA | ✅ `backend/api/security.py` (JWT) |
| C2. IPC (Ingesta y Comprensión de Prompt) | Analiza intención, estructura, calidad cognitiva | ✅ `backend/api/schemas/interaction.py` |
| C3. CRPE (Motor de Razonamiento Cognitivo-Pedagógico) | Selecciona modo cognitivo, evalúa profundidad | ✅ `backend/core/cognitive_engine.py` |
| C4. GSR (Gobernanza, Seguridad y Riesgo) | Implementa marcos ISO/IEC 23894, UNESCO, OECD, IEEE | ✅ `backend/agents/governance.py` |
| C5. LLM-Orchestrator | Orquesta interacción con distintos modelos IA | ✅ `backend/llm/factory.py` |
| C6. Trazabilidad Cognitiva N4 | Registra cada interacción, construye mapa de pensamiento | ✅ `backend/agents/traceability.py` |
| C7. Integración Git/n8n/Moodle | Conecta con sistemas institucionales | ✅ `backend/agents/git_integration.py` |

### 2.4. Nivel 4 – Dinámica

Modela el funcionamiento del ecosistema en tiempo real mediante un **flujo universal de 11 fases**:

1. Inicialización del contexto pedagógico vía LTI desde Moodle
2. Análisis del primer prompt por el componente IPC
3. Selección del modo cognitivo y modelo IA por CRPE y LLM-Orchestrator
4. Generación y filtrado de la respuesta IA bajo control GSR
5. Iteración estudiante-IA con registro de decisiones
6. Commits en Git como trazas de evolución técnica
7. Activación de flujos n8n para retroalimentación automática
8. Consolidación de trazabilidad cognitiva en N4
9. Intervención docente sobre base de evidencias procesuales
10. Cierre evaluativo con integración a calificaciones
11. Alimentación de indicadores para gestión y calidad

---

## 3. Los 6 Submodelos AI-Native

### 3.1. Submodelo 1: T-IA-Cog (Tutor IA Disciplinar Cognitivo)

**Sección**: 6.6
**Propósito**: Guía el razonamiento del estudiante, NO provee soluciones directas.

#### Fundamentación Teórica

| Teoría | Autor | Aplicación |
|--------|-------|------------|
| Cognición distribuida | Hutchins (1995) | IA como artefacto cognitivo del sistema |
| Cognición extendida | Clark & Chalmers (1998) | IA como extensión funcional del pensamiento |
| Carga cognitiva | Sweller (1988) | Redistribuir carga hacia procesos de mayor valor |
| Autorregulación | Zimmerman (2002) | Apoyo en planificación, monitoreo, evaluación |

#### 4 Modos de Operación

1. **Socrático**: Preguntas orientadoras, no respuestas directas
2. **Explicativo**: Conceptos fundamentales, principios
3. **Guiado**: Pistas graduadas, descomposición de problemas
4. **Metacognitivo**: Reflexión sobre el propio proceso

#### Reglas de Actuación

- Priorizar preguntas sobre respuestas directas
- Exigir justificación cuando el estudiante adopta solución de IA
- Escalar dificultad cognitiva conforme aumenta competencia
- Registrar en N4: hipótesis, cambios de estrategia, correcciones, críticas a IA

#### Implementación

✅ `backend/agents/tutor.py` → clase `CognitiveTutor`

---

### 3.2. Submodelo 2: E-IA-Proc (Evaluador IA de Procesos Cognitivos)

**Sección**: 6.7
**Propósito**: Analiza, reconstruye y evalúa el proceso cognitivo híbrido humano-IA.

#### Funciones Principales

| Función | Descripción |
|---------|-------------|
| Análisis de razonamiento | Examina secuencia de prompts, alternativas, coherencia |
| Detección de errores | Identifica confusiones de paradigmas, fallas de abstracción |
| Evaluación de autorregulación | Analiza planificación, monitoreo, revisión crítica |
| Comparación vía Git | Revisa commits, detecta saltos abruptos, patrones sospechosos |
| Generación de IEC | Produce Informe de Evaluación Cognitiva estructurado |

#### Funciones que NO Cumple

- ❌ No asigna notas
- ❌ No aprueba ni desaprueba
- ❌ No realiza juicios disciplinarios
- ❌ No reemplaza autoridad evaluadora del docente
- ❌ No corrige código automáticamente
- ❌ No sanciona casos de integridad académica

#### Implementación

✅ `backend/agents/evaluator.py` → clase `ProcessEvaluator`

---

### 3.3. Submodelo 3: S-IA-X (Simuladores de Roles Profesionales)

**Sección**: 6.8
**Propósito**: Simula roles profesionales reales para preparar al estudiante para la industria.

#### 6 Roles Definidos

| Rol | Código | Función Simulada |
|-----|--------|------------------|
| Product Owner | `product_owner` | Requiere historias de usuario, prioriza features, negocia alcance |
| Scrum Master | `scrum_master` | Gestiona impedimentos, facilita ceremonias, promueve mejora |
| Tech Interviewer | `tech_interviewer` | Entrevista técnica realista, evalúa competencias |
| Incident Responder | `incident_responder` | Gestión de incidentes en producción, troubleshooting |
| Client | `client` | Stakeholder con requisitos cambiantes, expectativas |
| DevSecOps | `devsecops` | Seguridad, CI/CD, infraestructura, observabilidad |

#### Características

- Actúa en modo "simulación cerrada" (no da soluciones)
- Registra en N4 todas las interacciones
- Evalúa competencias profesionales específicas
- Genera feedback formativo

#### Implementación

✅ `backend/agents/simulators.py` → 6 clases de simuladores
✅ `backend/api/schemas/enums.py` → `SimulatorType` enum

---

### 3.4. Submodelo 4: AR-IA (Analista de Riesgo Cognitivo)

**Sección**: 6.9
**Propósito**: Detecta riesgos cognitivos, éticos y epistémicos en tiempo real.

#### 5 Dimensiones de Riesgo (ISO/IEC 23894)

| Dimensión | Tipos de Riesgo |
|-----------|-----------------|
| **Cognitiva** | `cognitive_delegation`, `superficial_reasoning`, `ai_dependency`, `lack_justification`, `no_self_regulation` |
| **Ética** | `academic_integrity`, `undisclosed_ai_use`, `plagiarism` |
| **Epistémica** | `conceptual_error`, `logical_fallacy`, `uncritical_acceptance` |
| **Técnica** | `security_vulnerability`, `poor_code_quality`, `architectural_flaw` |
| **Gobernanza** | `policy_violation`, `unauthorized_use` |

#### Niveles de Riesgo

- `info` - Informativo
- `low` - Bajo
- `medium` - Medio
- `high` - Alto
- `critical` - Crítico

#### Funciones

1. Monitoreo en tiempo real de interacciones
2. Clasificación de riesgo por dimensión y nivel
3. Generación de alertas para docentes
4. Registro en N4 para auditoría
5. Recomendaciones de mitigación

#### Implementación

✅ `backend/agents/risk_analyst.py` → clase `RiskAnalyst`
✅ `backend/models/risk.py` → `RiskDimension`, `RiskType`, `RiskLevel` enums

---

### 3.5. Submodelo 5: GOV-IA (Agente de Gobernanza Institucional)

**Sección**: 6.10
**Propósito**: Garantiza cumplimiento normativo y ético en todas las interacciones.

#### Marcos Normativos Integrados

| Marco | Organismo | Ámbito |
|-------|-----------|--------|
| Recomendación sobre ética de la IA | UNESCO (2021) | Ética en IA educativa |
| ISO/IEC 23894 | ISO (2023) | Gestión de riesgo en IA |
| Ethically Aligned Design | IEEE (2019) | Diseño ético de sistemas |
| AI Principles | OECD | Principios generales IA |
| Ley 25.326 | Argentina | Protección de datos personales |
| GDPR | UE | Protección de datos |

#### Funciones

1. Validación de políticas por actividad
2. Bloqueo de interacciones que violen normas
3. Auditoría de cumplimiento
4. Generación de reportes para acreditación (CONEAU)
5. Gestión de consentimiento informado

#### Implementación

✅ `backend/agents/governance.py` → clase `GovernanceAgent`

---

### 3.6. Submodelo 6: N4 (Sistema de Trazabilidad Cognitiva)

**Sección**: 6.11
**Propósito**: Registra y reconstruye el proceso cognitivo completo del estudiante.

#### Problema que Resuelve

1. **Evaluación tradicional insuficiente**: No captura razonamiento, errores intermedios, auditoría de IA
2. **Invalidez de evidencia tradicional**: Producto final no garantiza autoría ni aprendizaje
3. **Ausencia de mecanismos de trazabilidad**: Ningún sistema captura interacciones humano-IA sistemáticamente

#### 4 Niveles de Trazabilidad

| Nivel | Nombre | Qué Captura |
|-------|--------|-------------|
| **N1** | Superficial | Archivos, entregas, versión final del código |
| **N2** | Técnico | Evolución de commits, branches, tests automatizados |
| **N3** | Interaccional | Prompts, respuestas, reintentos, explicaciones parciales |
| **N4** | Cognitivo | Intención, decisiones, justificaciones, alternativas, auditorías, riesgo |

#### 7 Módulos Internos del N4

| Módulo | Código | Función |
|--------|--------|---------|
| Captura Multicanal | CM-N4 | Recolecta en tiempo real: prompts, respuestas, commits, logs |
| Análisis Cognitivo | AC-N4 | Clasifica tipo de razonamiento, profundidad, delegación |
| Reconstrucción Temporal | RTR-N4 | Ordena y reconstruye proceso completo |
| Evaluación de Riesgo | RCE-N4 | Clasifica riesgos cognitivo-epistémicos |
| Métricas Cognitivas | MCP-N4 | Genera indicadores IPC, IAR, IAI, IRE |
| Integración Institucional | II-N4 | Integra con Moodle, Git, sistemas de evaluación |
| Evidencia Evaluativa | EE-N4 | Produce informes para evaluación y acreditación |

#### Métricas Cognitivas Definidas

| Métrica | Nombre | Descripción |
|---------|--------|-------------|
| **IPC** | Índice de Profundidad Cognitiva | Mide profundidad del razonamiento |
| **IAR** | Índice de Autenticidad del Razonamiento | Evalúa originalidad vs delegación |
| **IAI** | Índice de Auditoría de IA | Mide capacidad de revisar salidas de IA |
| **IRE** | Índice de Riesgo Epistémico | Evalúa riesgos en el conocimiento adquirido |

#### Implementación

✅ `backend/agents/traceability.py` → clase `TraceabilityAgent`
✅ `backend/database/models.py` → `CognitiveTraceDB` con campo `trace_level`
✅ `backend/api/schemas/enums.py` → `TraceLevel` enum con valores N1-N4

---

## 4. Integración Curricular

### 4.1. Tres Niveles de Integración

| Nivel | Descripción |
|-------|-------------|
| **Macro-curricular** | Perfil de egreso incluye competencias de programación asistida por IA |
| **Meso-curricular** | Trayectos AI-Native atraviesan materias de programación, arquitectura, DevOps |
| **Micro-curricular** | Actividades prácticas incluyen uso del ecosistema con documentación y justificación |

### 4.2. Tipología de Actividades AI-Native

1. **Co-programación crítica**: Estudiante trabaja con Code LLM como "par programador artificial"
2. **Auditoría de código generado**: IA produce solución, estudiante debe auditarla
3. **Simulaciones con IA en roles**: IA actúa como cliente, PO, revisor, etc.
4. **Meta-reflexión y gobernanza**: Análisis de logs, trazas N4, políticas de uso

### 4.3. Rúbricas AI-Native

Las rúbricas de evaluación ponderan:
- Calidad técnica del código
- Calidad del razonamiento y auditoría
- Uso crítico de IA
- Cumplimiento de principios éticos y normativos
- Capacidad de reflexión sobre el propio proceso

---

## 5. Alineación Documento ↔ Código

### 5.1. Componentes Implementados

| Concepto de la Tesis | Estado | Ubicación en Código |
|---------------------|--------|---------------------|
| Arquitectura C4 | ✅ Implementado | Estructura de carpetas backend/ |
| ai-gateway stateless | ✅ Implementado | `backend/core/ai_gateway.py` |
| 6 agentes IA | ✅ Implementado | `backend/agents/` |
| Trazabilidad N4 (4 niveles) | ✅ Implementado | `CognitiveTraceDB`, `TraceLevel` enum |
| 5 dimensiones de riesgo | ✅ Implementado | `RiskDimension` enum |
| 6 simuladores profesionales | ✅ Implementado | `SimulatorType` enum |
| LLM multi-proveedor | ✅ Implementado | `LLMProviderFactory` |
| JWT autenticación | ✅ Implementado | `backend/api/security.py` |
| Integración Git | ✅ Implementado | `backend/agents/git_integration.py` |
| Validación de prompts (IPC) | ✅ Implementado | `backend/api/schemas/interaction.py` |
| Motor CRPE | ✅ Implementado | `backend/core/cognitive_engine.py` |

### 5.2. Componentes Parcialmente Implementados

| Concepto | Estado | Notas |
|----------|--------|-------|
| Integración Moodle/LTI | ⚠️ Parcial | Schema `LTIIntegrationDB` existe, falta integración completa |
| Métricas IPC, IAR, IAI, IRE | ⚠️ Parcial | `ai_dependency_score` implementado, otras métricas pendientes |

### 5.3. Componentes Pendientes

| Concepto | Estado | Prioridad |
|----------|--------|-----------|
| Integración n8n | ❌ Pendiente | Media - orquestación de flujos automáticos |
| Dashboard docente completo | ⚠️ Parcial | Alta - visualización de trazas N4 |
| Reportes para CONEAU | ❌ Pendiente | Baja - acreditación institucional |

---

## 6. Hallazgos Clave

### 6.1. Fortalezas de la Implementación

1. **Fidelidad arquitectónica**: El código implementa fielmente la arquitectura teórica del Capítulo 6.

2. **Submodelos operativos**: Los 6 submodelos están implementados con sus funciones principales.

3. **Trazabilidad completa**: El sistema N4 captura los 4 niveles de trazabilidad definidos.

4. **Gobernanza integrada**: El módulo GSR implementa los marcos normativos especificados.

5. **Extensibilidad**: La arquitectura de Factory para LLMs permite agregar nuevos proveedores.

### 6.2. Áreas de Mejora

1. **Métricas cognitivas avanzadas**: Implementar IPC, IAR, IAI, IRE como indicadores calculables.

2. **Integración LTI**: Completar integración con Moodle para contexto pedagógico automático.

3. **Orquestación n8n**: Implementar flujos automáticos de retroalimentación.

4. **Dashboard docente**: Mejorar visualización de trazas cognitivas y alertas.

### 6.3. Recomendaciones

1. **Documentar métricas**: Crear documentación técnica de cómo calcular IPC, IAR, IAI, IRE.

2. **Tests de integración**: Agregar tests que validen flujos completos del Nivel 4 dinámico.

3. **Validación pedagógica**: Realizar pruebas piloto con docentes para validar efectividad del T-IA-Cog.

4. **Auditoría de cumplimiento**: Verificar cumplimiento efectivo de marcos UNESCO, ISO/IEC 23894.

---

## 7. Conclusión

El Capítulo 6 de la tesis doctoral constituye la **especificación formal** del ecosistema AI-Native. La implementación en código está **altamente alineada** con esta especificación, con los 6 submodelos operativos y la arquitectura C4 fielmente representada.

El sistema transforma la enseñanza de programación de un modelo centrado en productos (código final) a uno centrado en **procesos cognitivos** (cómo piensa el estudiante), utilizando IA generativa como herramienta de andamiaje y no como sustituto del razonamiento humano.

**Aporte original de la tesis**: Definir submodelos IA específicos para educación superior en programación, anclados en arquitectura con gobernanza y trazabilidad, integrados en procesos cognitivos y pedagógicos reproducibles y evaluables.

---

*Documento generado automáticamente mediante análisis del archivo `capitulo6.docx`*
*Última actualización: 2025-12-07*