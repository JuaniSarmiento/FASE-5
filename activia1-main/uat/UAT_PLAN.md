# User Acceptance Testing (UAT) Plan
# AI-Native MVP

**Autor**: Mag. Alberto Cortez
**Fecha**: 2025-11-24
**Versión**: 1.0
**Estado**: Ready for Execution

---

## 1. Resumen Ejecutivo

### Objetivo del UAT

Validar que el ecosistema AI-Native MVP cumple con las necesidades de los usuarios finales (estudiantes e instructores) en escenarios reales de uso, antes de su despliegue en producción.

### Alcance

- **Usuarios participantes**: 5 estudiantes + 1 instructor
- **Duración**: 2 semanas (10 días hábiles)
- **Ambiente**: Staging (https://app-staging.ai-native.tu-institucion.edu.ar)
- **Actividades**: 3 trabajos prácticos de Programación II
- **Criterio de éxito**: ≥80% satisfacción, <5 bugs críticos

---

## 2. Objetivos Específicos

### 2.1 Objetivos Funcionales

- [ ] Validar flujo de interacción estudiante-tutor AI
- [ ] Verificar calidad de respuestas pedagógicas (T-IA-Cog)
- [ ] Comprobar funcionamiento de simuladores profesionales (S-IA-X)
- [ ] Validar trazabilidad N4 (captura de proceso cognitivo)
- [ ] Verificar evaluación de procesos (E-IA-Proc)
- [ ] Comprobar detección de riesgos (AR-IA)

### 2.2 Objetivos No Funcionales

- [ ] Validar usabilidad de la interfaz (SUS score ≥70)
- [ ] Verificar tiempos de respuesta aceptables (<3s)
- [ ] Comprobar estabilidad (sin crashes durante sesiones)
- [ ] Validar accesibilidad básica (contraste, tamaño de fuente)

### 2.3 Objetivos Pedagógicos

- [ ] Verificar que el tutor AI NO resuelve problemas directamente
- [ ] Comprobar que promueve razonamiento autónomo
- [ ] Validar que detecta delegación total
- [ ] Verificar calidad de preguntas socráticas

---

## 3. Participantes

### 3.1 Perfil de Estudiantes (5 participantes)

| ID | Perfil | Nivel | Experiencia con IA | Objetivo |
|----|--------|-------|-------------------|----------|
| E01 | Estudiante avanzado | Alto | Alta | Validar límites del tutor |
| E02 | Estudiante promedio | Medio | Media | Caso típico |
| E03 | Estudiante con dificultades | Bajo | Baja | Caso edge |
| E04 | Estudiante autodidacta | Alto | Alta | Uso intensivo |
| E05 | Estudiante parte-time | Medio | Baja | Disponibilidad limitada |

**Criterios de selección**:
- Cursando Programación II (actual o reciente)
- Disponibilidad de 2 horas diarias durante 2 semanas
- Experiencia variada con IAs generativas
- Consentimiento informado firmado

### 3.2 Instructor (1 participante)

| ID | Rol | Experiencia | Objetivo |
|----|-----|-------------|----------|
| I01 | Docente Prog II | 5+ años | Validar utilidad pedagógica |

**Responsabilidades**:
- Crear actividades en el sistema
- Revisar trazas N4 de estudiantes
- Evaluar informes de proceso (E-IA-Proc)
- Proveer feedback sobre calidad pedagógica

---

## 4. Escenarios de Prueba

### Escenario 1: Primera Interacción (Onboarding)

**Objetivo**: Validar experiencia de primer uso

**Actor**: Todos los estudiantes (E01-E05)

**Pasos**:
1. Acceder a https://app-staging.ai-native.tu-institucion.edu.ar
2. Crear cuenta nueva
3. Iniciar primera sesión con T-IA-Cog
4. Hacer 3 preguntas sobre "Colas Circulares"
5. Finalizar sesión

**Criterios de Aceptación**:
- ✅ Onboarding completado en <5 minutos
- ✅ Sin errores durante registro
- ✅ Respuestas del tutor AI son claras y pedagógicas
- ✅ Usuario comprende cómo usar el sistema

**Métricas**:
- Tiempo de onboarding (target: <5 min)
- Número de errores encontrados
- SUS score inicial (survey post-onboarding)

---

### Escenario 2: Sesión de Trabajo Típica (T-IA-Cog)

**Objetivo**: Validar flujo completo de interacción con tutor cognitivo

**Actor**: E02, E03, E05 (3 estudiantes)

**Actividad**: Trabajo Práctico 1 - Colas Circulares

**Pasos**:
1. Iniciar sesión TUTOR para actividad "prog2_tp1_colas"
2. Hacer 10-15 preguntas sobre:
   - Conceptos teóricos (¿Qué es una cola circular?)
   - Planificación (¿Cómo estructuro el código?)
   - Implementación (Tengo este código, ¿es correcto?)
   - Depuración (¿Por qué falla mi enqueue?)
3. Finalizar sesión

**Criterios de Aceptación**:
- ✅ Tutor responde en modo socrático (no da código completo)
- ✅ Respuestas son pedagógicamente útiles
- ✅ Sistema detecta si hay delegación total
- ✅ Trazas N4 capturan intención cognitiva
- ✅ Sin errores técnicos durante sesión

**Métricas**:
- Número de interacciones por sesión
- Tiempo de respuesta del tutor (target: <3s)
- Calidad pedagógica (escala 1-5, evaluada por instructor)
- Riesgos detectados por AR-IA

---

### Escenario 3: Uso Intensivo (Stress Test de Usuario)

**Objetivo**: Validar sistema bajo uso intensivo por usuario avanzado

**Actor**: E01, E04 (2 estudiantes avanzados)

**Actividad**: Trabajo Práctico 2 - Pilas y Recursión

**Pasos**:
1. Iniciar sesión TUTOR
2. Hacer 30+ preguntas en una sesión larga (2-3 horas)
3. Probar múltiples estrategias:
   - Preguntas conceptuales profundas
   - Solicitar código completo (validar que sea bloqueado)
   - Preguntar sobre edge cases
   - Pedir explicaciones alternativas
4. Finalizar y revisar evaluación de proceso

**Criterios de Aceptación**:
- ✅ Sistema mantiene coherencia durante sesión larga
- ✅ No se degrada calidad de respuestas
- ✅ Gobernanza (GOV-IA) bloquea solicitudes inapropiadas
- ✅ Evaluación de proceso (E-IA-Proc) es coherente

**Métricas**:
- Duración de sesión (target: >2 horas sin crashes)
- Solicitudes bloqueadas por gobernanza
- Score de evaluación de proceso

---

### Escenario 4: Simuladores Profesionales (S-IA-X)

**Objetivo**: Validar funcionamiento de simuladores de roles profesionales

**Actor**: E01, E02, E04 (3 estudiantes)

**Actividad**: Trabajo Práctico 3 - Proyecto Ágil

**Pasos**:
1. **Sesión con PO-IA** (Product Owner):
   - Solicitar requerimientos para "Sistema de Biblioteca"
   - Aclarar dudas sobre user stories
   - Negociar prioridades
   - Duración: 30 minutos

2. **Sesión con SM-IA** (Scrum Master):
   - Participar en daily standup simulado
   - Reportar impedimentos
   - Recibir coaching ágil
   - Duración: 15 minutos

3. **Sesión con IT-IA** (Technical Interviewer):
   - Responder preguntas técnicas sobre estructuras de datos
   - Resolver problema algorítmico
   - Recibir feedback técnico
   - Duración: 45 minutos

**Criterios de Aceptación**:
- ✅ Simuladores mantienen rol coherentemente
- ✅ Diálogos son realistas y profesionales
- ✅ Feedback es constructivo y relevante
- ✅ Estudiantes perciben valor pedagógico

**Métricas**:
- Realismo del simulador (escala 1-5)
- Utilidad pedagógica (escala 1-5)
- Duración promedio de sesión

---

### Escenario 5: Evaluación de Proceso (E-IA-Proc)

**Objetivo**: Validar que la evaluación de proceso es útil para instructor

**Actor**: I01 (Instructor)

**Actividad**: Revisar informes de evaluación de proceso de E02, E03

**Pasos**:
1. Acceder al panel de instructor
2. Revisar traza cognitiva (N4) de sesión de E02
3. Leer informe de evaluación de proceso (IEC)
4. Verificar coherencia entre trazas y evaluación
5. Comparar con evaluación propia (gold standard)

**Criterios de Aceptación**:
- ✅ IEC contiene información accionable
- ✅ Identifica fortalezas y áreas de mejora
- ✅ Detecta errores conceptuales
- ✅ Evalúa razonamiento (no solo producto)
- ✅ Correlación ≥0.7 con evaluación de instructor

**Métricas**:
- Tiempo de revisión del IEC
- Correlación con evaluación manual
- Utilidad percibida (escala 1-5)

---

### Escenario 6: Detección de Riesgos (AR-IA)

**Objetivo**: Validar que el sistema detecta riesgos cognitivos y éticos

**Actor**: E03 (estudiante con dificultades)

**Actividad**: Trabajo Práctico 1 - Colas Circulares

**Pasos**:
1. Iniciar sesión TUTOR
2. Hacer preguntas que indican delegación total:
   - "Dame el código completo de la cola circular"
   - "Hazlo por mí"
   - "No entiendo nada, dame la solución"
3. Copiar código de internet y preguntar "¿Está bien?"
4. No justificar decisiones de diseño

**Criterios de Aceptación**:
- ✅ Sistema detecta delegación total (RC-01)
- ✅ Sistema detecta falta de justificación (RC-03)
- ✅ Sistema detecta posible plagio (RE-01)
- ✅ Genera alertas para instructor
- ✅ Recomendaciones son constructivas (no punitivas)

**Métricas**:
- Precisión de detección de riesgos
- False positives (<10%)
- Tiempo de detección (inmediato vs diferido)

---

### Escenario 7: Accesibilidad y Usabilidad

**Objetivo**: Validar que el sistema es usable y accesible

**Actor**: Todos los estudiantes (E01-E05)

**Pasos**:
1. Usar sistema con diferentes navegadores (Chrome, Firefox, Safari)
2. Usar en dispositivo móvil (responsive)
3. Ajustar tamaño de fuente
4. Usar solo teclado (sin mouse)
5. Completar survey de usabilidad (SUS)

**Criterios de Aceptación**:
- ✅ Funciona en Chrome, Firefox, Safari
- ✅ Responsive en móvil (viewport ≥375px)
- ✅ Contraste cumple WCAG 2.1 AA
- ✅ Navegable con teclado (Tab, Enter)
- ✅ SUS score ≥70 (Good usability)

**Métricas**:
- SUS score promedio
- Bugs de compatibilidad encontrados
- Tiempo para completar tarea estándar

---

## 5. Cronograma

### Semana 1 (Días 1-5)

| Día | Actividad | Participantes | Duración |
|-----|-----------|---------------|----------|
| 1 | Capacitación inicial + Escenario 1 | E01-E05, I01 | 2h |
| 2 | Escenario 2 (Sesión típica) | E02, E03, E05 | 1.5h |
| 3 | Escenario 3 (Uso intensivo) | E01, E04 | 3h |
| 4 | Escenario 4 (Simuladores) Parte 1 | E01, E02 | 2h |
| 5 | Escenario 4 (Simuladores) Parte 2 | E04 | 2h |

### Semana 2 (Días 6-10)

| Día | Actividad | Participantes | Duración |
|-----|-----------|---------------|----------|
| 6 | Escenario 6 (Detección riesgos) | E03 | 1.5h |
| 7 | Escenario 7 (Usabilidad) | E01-E05 | 1h |
| 8 | Escenario 5 (Evaluación proceso) | I01 | 2h |
| 9 | Sesiones de feedback | E01-E05, I01 | 2h |
| 10 | Análisis de resultados | Equipo técnico | 4h |

---

## 6. Instrumentos de Recolección de Datos

### 6.1 System Usability Scale (SUS)

**Cuándo**: Post-onboarding y final de UAT

**Preguntas** (escala 1-5: Strongly Disagree → Strongly Agree):
1. Creo que me gustaría usar este sistema frecuentemente
2. Encontré el sistema innecesariamente complejo
3. Pensé que el sistema era fácil de usar
4. Creo que necesitaría ayuda técnica para usar este sistema
5. Encontré que las funciones del sistema estaban bien integradas
6. Pensé que había demasiada inconsistencia en este sistema
7. Imagino que la mayoría de las personas aprenderían a usar este sistema rápidamente
8. Encontré el sistema muy engorroso de usar
9. Me sentí muy confiado usando el sistema
10. Necesité aprender muchas cosas antes de poder usar este sistema

**Cálculo**: `SUS Score = ((suma ítems impares - 5) + (25 - suma ítems pares)) * 2.5`

**Interpretación**:
- ≥80: Excellent
- 70-79: Good
- 50-69: OK
- <50: Poor

### 6.2 Pedagogical Quality Survey (Instructor)

**Cuándo**: Después de revisar cada IEC

**Preguntas** (escala 1-5):
1. El tutor AI promueve razonamiento autónomo
2. Las respuestas son pedagógicamente apropiadas
3. El sistema detecta errores conceptuales
4. La evaluación de proceso es precisa
5. El IEC provee información accionable
6. El sistema ayuda a identificar estudiantes en riesgo
7. Recomendaría este sistema a colegas

### 6.3 Student Satisfaction Survey

**Cuándo**: Final de UAT

**Preguntas** (escala 1-5):
1. El tutor AI me ayudó a comprender mejor los conceptos
2. Las respuestas fueron claras y útiles
3. El sistema respetó mi autonomía (no dio soluciones directas)
4. Me sentí frustrado usando el sistema (reverse)
5. Los simuladores profesionales fueron realistas
6. El feedback recibido fue constructivo
7. Usaría este sistema en futuras materias

### 6.4 Bug Report Form

**Campos**:
- Fecha/hora
- Usuario
- Escenario
- Descripción del bug
- Pasos para reproducir
- Severidad (Critical, High, Medium, Low)
- Screenshot/logs (opcional)

### 6.5 Session Observation Checklist (Instructor)

**Durante observación de sesiones**:
- [ ] Usuario completó tarea sin ayuda externa
- [ ] Respuestas del tutor fueron apropiadas
- [ ] Sistema detectó delegación (si aplica)
- [ ] No hubo errores técnicos
- [ ] Tiempo de respuesta aceptable
- [ ] Usuario expresó satisfacción/frustración (anotar)

---

## 7. Criterios de Éxito

### 7.1 Criterios Cuantitativos

| Métrica | Target | Criticidad |
|---------|--------|------------|
| SUS Score | ≥70 | HIGH |
| Student Satisfaction | ≥4.0/5.0 | HIGH |
| Pedagogical Quality (Instructor) | ≥4.0/5.0 | HIGH |
| Critical Bugs | ≤5 | CRITICAL |
| High Bugs | ≤10 | HIGH |
| Response Time (p95) | <3s | MEDIUM |
| Session Crashes | 0 | CRITICAL |
| Uptime | ≥99% | HIGH |

### 7.2 Criterios Cualitativos

- ✅ Estudiantes perciben valor pedagógico
- ✅ Instructor considera el sistema útil para evaluación
- ✅ No hay quejas sobre calidad de respuestas del tutor
- ✅ Simuladores son percibidos como realistas
- ✅ Sistema no causa frustración excesiva

---

## 8. Gestión de Riesgos

### Riesgo 1: Baja participación de usuarios

**Probabilidad**: Media
**Impacto**: Alto
**Mitigación**:
- Incentivar participación (crédito académico extra)
- Flexibilidad en horarios
- Seguimiento proactivo

### Riesgo 2: Bugs críticos durante UAT

**Probabilidad**: Media
**Impacto**: Alto
**Mitigación**:
- Hotfix process definido (deploy en <4h)
- Equipo técnico disponible durante UAT
- Rollback plan preparado

### Riesgo 3: Calidad pedagógica insatisfactoria

**Probabilidad**: Baja
**Impacto**: Crítico
**Mitigación**:
- Ajuste de prompts de T-IA-Cog
- Fine-tuning de LLM (si es necesario)
- Feedback loop rápido con instructor

### Riesgo 4: Problemas de infraestructura (staging)

**Probabilidad**: Baja
**Impacto**: Alto
**Mitigación**:
- Monitoring 24/7
- Alertas configuradas
- Equipo DevOps on-call

---

## 9. Entregables

### 9.1 Durante UAT

- [ ] Logs de sesiones (todas las interacciones)
- [ ] Bug reports (formularios completados)
- [ ] Screenshots de issues encontrados
- [ ] Notas de observación del instructor

### 9.2 Post-UAT

- [ ] **UAT Results Report** (este documento + resultados)
- [ ] **Bug Tracker** (Excel con todos los bugs)
- [ ] **User Feedback Compilation** (surveys compilados)
- [ ] **Metrics Dashboard** (SUS, satisfaction, performance)
- [ ] **Recommendations Document** (mejoras sugeridas)
- [ ] **Sign-off Document** (aprobación para producción)

---

## 10. Proceso de Sign-off

### Criterios para Aprobación

**Go/No-Go Decision**:

✅ **GO** (Aprobar para producción) si:
- SUS score ≥70
- Student satisfaction ≥4.0/5.0
- Pedagogical quality ≥4.0/5.0
- Critical bugs ≤5 (y todos resueltos)
- No crashes durante sesiones
- Instructor aprueba

⚠️ **CONDITIONAL GO** (Aprobar con condiciones) si:
- SUS score 60-69
- Student satisfaction 3.5-3.9
- 5-10 critical bugs (plan de fix definido)
- <3 crashes (no recurrentes)

❌ **NO-GO** (Rechazar, iterar) si:
- SUS score <60
- Student satisfaction <3.5
- >10 critical bugs
- Crashes recurrentes
- Instructor rechaza

### Stakeholders Requeridos para Sign-off

1. **Instructor Participante** (I01)
2. **Product Owner** (Mag. Alberto Cortez)
3. **Tech Lead** (Equipo técnico)
4. **Al menos 3/5 estudiantes** (feedback positivo)

---

## 11. Anexos

### Anexo A: Consentimiento Informado

(Plantilla separada en `CONSENTIMIENTO_INFORMADO.md`)

### Anexo B: Guías de Usuario

- Guía del Estudiante (Quick Start)
- Guía del Instructor (Panel de evaluación)

### Anexo C: Scripts de Prueba

- Escenarios detallados paso a paso
- Datos de prueba (actividades, prompts)

---

**Preparado por**: Mag. Alberto Cortez
**Fecha**: 2025-11-24
**Aprobado por**: [Pendiente]
**Versión**: 1.0