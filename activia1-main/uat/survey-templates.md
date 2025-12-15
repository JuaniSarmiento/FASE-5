# Plantillas de Encuestas - UAT AI-Native MVP

Este documento contiene las 4 encuestas que los participantes completarán durante la UAT.

---

## 📋 Tabla de Contenidos

1. [Encuesta SUS (System Usability Scale)](#1-encuesta-sus-system-usability-scale)
2. [Encuesta de Satisfacción General](#2-encuesta-de-satisfacción-general)
3. [Encuesta de Calidad Pedagógica](#3-encuesta-de-calidad-pedagógica)
4. [Encuesta de Feedback Final](#4-encuesta-de-feedback-final)

---

## 1. Encuesta SUS (System Usability Scale)

**Cuándo aplicar**: Al final de la Semana 1 (Día 5)
**Duración estimada**: 3-5 minutos
**Metodología**: Sistema de puntuación estandarizado (0-100)

---

### Instrucciones

Para cada afirmación, indica tu nivel de acuerdo en una escala del 1 al 5:

- **1** = Totalmente en desacuerdo
- **2** = En desacuerdo
- **3** = Neutral
- **4** = De acuerdo
- **5** = Totalmente de acuerdo

**IMPORTANTE**: Responde basándote en tu experiencia general con el sistema, no en una única interacción.

---

### Preguntas

| # | Afirmación | 1 | 2 | 3 | 4 | 5 |
|---|-----------|---|---|---|---|---|
| 1 | Creo que me gustaría usar este sistema frecuentemente | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | Encontré el sistema innecesariamente complejo | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3 | Pensé que el sistema era fácil de usar | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4 | Creo que necesitaría ayuda de una persona técnica para usar este sistema | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5 | Encontré que las diversas funciones del sistema estaban bien integradas | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6 | Pensé que había demasiada inconsistencia en este sistema | ☐ | ☐ | ☐ | ☐ | ☐ |
| 7 | Imagino que la mayoría de las personas aprenderían a usar este sistema rápidamente | ☐ | ☐ | ☐ | ☐ | ☐ |
| 8 | Encontré el sistema muy incómodo de usar | ☐ | ☐ | ☐ | ☐ | ☐ |
| 9 | Me sentí muy confiado/a usando el sistema | ☐ | ☐ | ☐ | ☐ | ☐ |
| 10 | Necesité aprender muchas cosas antes de poder usar este sistema | ☐ | ☐ | ☐ | ☐ | ☐ |

---

### Cálculo del Score SUS

**Para uso del instructor** (no mostrar a estudiantes):

```
Preguntas impares (1, 3, 5, 7, 9):
  Contribución = Respuesta - 1

Preguntas pares (2, 4, 6, 8, 10):
  Contribución = 5 - Respuesta

Score SUS = (Suma de contribuciones) × 2.5
```

**Interpretación**:
- **80-100**: Excelente usabilidad (Grade A)
- **70-79**: Buena usabilidad (Grade B)
- **60-69**: Usabilidad aceptable (Grade C) ← **Objetivo UAT: ≥70**
- **50-59**: Usabilidad marginal (Grade D)
- **0-49**: Usabilidad pobre (Grade F)

---

## 2. Encuesta de Satisfacción General

**Cuándo aplicar**: Al final de la Semana 1 (Día 5)
**Duración estimada**: 5-7 minutos

---

### Sección A: Satisfacción por Dimensiones

Califica tu satisfacción en cada dimensión usando una escala del 1 al 5:

- **1** = Muy insatisfecho
- **2** = Insatisfecho
- **3** = Neutral
- **4** = Satisfecho
- **5** = Muy satisfecho

| Dimensión | Descripción | 1 | 2 | 3 | 4 | 5 |
|-----------|-------------|---|---|---|---|---|
| **Facilidad de uso** | El sistema es intuitivo y fácil de navegar | ☐ | ☐ | ☐ | ☐ | ☐ |
| **Utilidad pedagógica** | El sistema me ayuda a aprender programación | ☐ | ☐ | ☐ | ☐ | ☐ |
| **Calidad de respuestas** | Las respuestas del tutor son útiles y precisas | ☐ | ☐ | ☐ | ☐ | ☐ |
| **Tiempo de respuesta** | El sistema responde en un tiempo razonable | ☐ | ☐ | ☐ | ☐ | ☐ |
| **Interfaz visual** | La interfaz es atractiva y clara | ☐ | ☐ | ☐ | ☐ | ☐ |
| **Feedback formativo** | Los reportes de evaluación son útiles | ☐ | ☐ | ☐ | ☐ | ☐ |
| **Simuladores profesionales** | Los simuladores (PO, SM, IT, etc.) son realistas | ☐ | ☐ | ☐ | ☐ | ☐ |
| **Satisfacción general** | Recomendaría este sistema a otros estudiantes | ☐ | ☐ | ☐ | ☐ | ☐ |

---

### Sección B: Preguntas Abiertas

**B1. ¿Qué es lo que MÁS te gustó del sistema?**

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

**B2. ¿Qué es lo que MENOS te gustó o lo que más te frustró?**

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

**B3. Si pudieras cambiar UNA COSA del sistema, ¿qué sería?**

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

### Sección C: Comparación con Herramientas Existentes

**C1. ¿Has usado otras herramientas de IA para programación? (marca todas las que apliquen)**

- [ ] ChatGPT (OpenAI)
- [ ] GitHub Copilot
- [ ] Google Bard / Gemini
- [ ] Claude (Anthropic)
- [ ] Otra: _____________________
- [ ] Ninguna

**C2. Si respondiste que SÍ has usado otras herramientas, ¿cómo compararías AI-Native MVP con ellas?**

| Aspecto | AI-Native es MEJOR | Son SIMILARES | Otras son MEJORES |
|---------|-------------------|---------------|-------------------|
| Calidad de respuestas | ☐ | ☐ | ☐ |
| Enfoque pedagógico (no da código completo) | ☐ | ☐ | ☐ |
| Feedback sobre tu proceso de aprendizaje | ☐ | ☐ | ☐ |
| Facilidad de uso | ☐ | ☐ | ☐ |

**C3. ¿Por qué razón principal?**

```
_________________________________________________________________

_________________________________________________________________
```

---

## 3. Encuesta de Calidad Pedagógica

**Cuándo aplicar**: Al final de la Semana 2 (Día 10)
**Duración estimada**: 8-10 minutos
**Objetivo**: Evaluar efectividad pedagógica específica de agentes

---

### Sección A: Tutor Cognitivo (T-IA-Cog)

Califica tu experiencia con el Tutor Cognitivo usando una escala del 1 al 5:

- **1** = Totalmente en desacuerdo
- **2** = En desacuerdo
- **3** = Neutral
- **4** = De acuerdo
- **5** = Totalmente de acuerdo

| Afirmación | 1 | 2 | 3 | 4 | 5 |
|-----------|---|---|---|---|---|
| El tutor promueve mi razonamiento crítico en lugar de darme respuestas directas | ☐ | ☐ | ☐ | ☐ | ☐ |
| Las preguntas socráticas del tutor me ayudan a reflexionar | ☐ | ☐ | ☐ | ☐ | ☐ |
| El tutor adapta su nivel de ayuda según mi necesidad | ☐ | ☐ | ☐ | ☐ | ☐ |
| Siento que aprendo MÁS con este tutor que si me dieran código completo | ☐ | ☐ | ☐ | ☐ | ☐ |
| El tutor detecta correctamente cuándo necesito más orientación | ☐ | ☐ | ☐ | ☐ | ☐ |

**A1. ¿El tutor te bloqueó alguna vez por solicitar código completo?**
- [ ] Sí → ¿Te pareció justificado? [ ] Sí [ ] No
- [ ] No

**A2. Si respondiste que SÍ fue bloqueado, ¿cómo te sentiste?**

```
_________________________________________________________________

_________________________________________________________________
```

---

### Sección B: Evaluador de Procesos (E-IA-Proc)

| Afirmación | 1 | 2 | 3 | 4 | 5 |
|-----------|---|---|---|---|---|
| El reporte de evaluación refleja mi proceso de aprendizaje real | ☐ | ☐ | ☐ | ☐ | ☐ |
| Las fortalezas identificadas son precisas | ☐ | ☐ | ☐ | ☐ | ☐ |
| Las áreas de mejora son útiles y accionables | ☐ | ☐ | ☐ | ☐ | ☐ |
| Prefiero este tipo de evaluación (proceso) vs exámenes tradicionales (producto) | ☐ | ☐ | ☐ | ☐ | ☐ |
| El score (0-100) refleja mi nivel de competencia real | ☐ | ☐ | ☐ | ☐ | ☐ |

**B1. ¿La evaluación de proceso te parece más justa que un examen tradicional? ¿Por qué?**

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

### Sección C: Simuladores Profesionales (S-IA-X)

**C1. ¿Qué simuladores usaste? (marca todos los que apliquen)**
- [ ] PO-IA (Product Owner)
- [ ] SM-IA (Scrum Master)
- [ ] IT-IA (Technical Interviewer)
- [ ] IR-IA (Incident Responder)
- [ ] CX-IA (Client Experience)
- [ ] DSO-IA (DevSecOps)

**C2. Califica cada simulador que usaste:**

| Simulador | Realismo (1-5) | Utilidad Pedagógica (1-5) | Dificultad Apropiada (1-5) |
|-----------|----------------|---------------------------|---------------------------|
| PO-IA | ☐☐☐☐☐ | ☐☐☐☐☐ | ☐☐☐☐☐ |
| SM-IA | ☐☐☐☐☐ | ☐☐☐☐☐ | ☐☐☐☐☐ |
| IT-IA | ☐☐☐☐☐ | ☐☐☐☐☐ | ☐☐☐☐☐ |
| IR-IA | ☐☐☐☐☐ | ☐☐☐☐☐ | ☐☐☐☐☐ |
| CX-IA | ☐☐☐☐☐ | ☐☐☐☐☐ | ☐☐☐☐☐ |
| DSO-IA | ☐☐☐☐☐ | ☐☐☐☐☐ | ☐☐☐☐☐ |

**C3. ¿Los simuladores te prepararon mejor para situaciones laborales reales?**

- [ ] Sí, definitivamente
- [ ] Sí, un poco
- [ ] Neutral / No estoy seguro
- [ ] No, no mucho
- [ ] No, para nada

**C4. Comentarios sobre simuladores (opcional):**

```
_________________________________________________________________

_________________________________________________________________
```

---

### Sección D: Trazabilidad Cognitiva (TC-N4)

| Afirmación | 1 | 2 | 3 | 4 | 5 |
|-----------|---|---|---|---|---|
| El panel de trazabilidad me ayudó a entender mi proceso de aprendizaje | ☐ | ☐ | ☐ | ☐ | ☐ |
| Me sorprendió ver mi "camino cognitivo" visualizado | ☐ | ☐ | ☐ | ☐ | ☐ |
| La métrica de "AI Dependency" me hizo reflexionar sobre mi uso de IA | ☐ | ☐ | ☐ | ☐ | ☐ |
| Cambié mi forma de interactuar con el sistema después de ver las trazas | ☐ | ☐ | ☐ | ☐ | ☐ |

**D1. ¿Te parece valioso que tus profesores puedan ver tu proceso cognitivo (no solo el código final)?**

- [ ] Sí, muy valioso
- [ ] Sí, algo valioso
- [ ] Neutral
- [ ] No, poco valioso
- [ ] No, nada valioso

**D2. ¿Por qué?**

```
_________________________________________________________________

_________________________________________________________________
```

---

### Sección E: Análisis de Riesgos (AR-IA)

**E1. ¿Viste alertas de riesgos durante tus sesiones?**
- [ ] Sí → ¿Qué tipo? (marca todas las que apliquen)
  - [ ] Delegación excesiva
  - [ ] Razonamiento superficial
  - [ ] Error conceptual
  - [ ] Otro: _________________
- [ ] No vi ninguna alerta

**E2. Si viste alertas, ¿te parecieron útiles o intrusivas?**

- [ ] Muy útiles (me ayudaron a mejorar)
- [ ] Algo útiles
- [ ] Neutral
- [ ] Algo intrusivas (molestas pero comprensibles)
- [ ] Muy intrusivas (deberían eliminarse)

**E3. Comentarios sobre detección de riesgos:**

```
_________________________________________________________________

_________________________________________________________________
```

---

## 4. Encuesta de Feedback Final

**Cuándo aplicar**: Último día de UAT (Día 10)
**Duración estimada**: 10-15 minutos
**Objetivo**: Recolectar feedback exhaustivo para decisión Go/No-Go

---

### Sección A: Evaluación Final

**A1. En general, ¿cumplió el sistema tus expectativas?**

- [ ] Superó mis expectativas
- [ ] Cumplió mis expectativas
- [ ] Estuvo cerca de cumplir mis expectativas
- [ ] No cumplió mis expectativas
- [ ] Estuvo muy por debajo de mis expectativas

**A2. ¿Volverías a usar este sistema en futuros cursos de programación?**

- [ ] Definitivamente sí
- [ ] Probablemente sí
- [ ] No estoy seguro
- [ ] Probablemente no
- [ ] Definitivamente no

**A3. ¿Recomendarías este sistema a otros estudiantes?**

- [ ] Sí, sin dudas (Net Promoter Score: 9-10)
- [ ] Probablemente sí (NPS: 7-8)
- [ ] Tal vez / No estoy seguro (NPS: 5-6)
- [ ] Probablemente no (NPS: 3-4)
- [ ] Definitivamente no (NPS: 0-2)

**A4. Si este sistema estuviera disponible, ¿lo usarías en lugar de ChatGPT/Copilot para aprender programación?**

- [ ] Sí, exclusivamente
- [ ] Sí, como herramienta principal (80% del tiempo)
- [ ] Sí, pero alternando con otras herramientas (50/50)
- [ ] No, lo usaría como complemento (20% del tiempo)
- [ ] No, prefiero otras herramientas

---

### Sección B: Percepción de Valor

**B1. ¿Qué TAN importante es cada característica para ti?**

Califica del 1 al 5:
- **1** = Nada importante
- **2** = Poco importante
- **3** = Moderadamente importante
- **4** = Muy importante
- **5** = Extremadamente importante

| Característica | 1 | 2 | 3 | 4 | 5 |
|----------------|---|---|---|---|---|
| Tutor que NO da código completo (enfoque socrático) | ☐ | ☐ | ☐ | ☐ | ☐ |
| Evaluación de proceso (no solo producto) | ☐ | ☐ | ☐ | ☐ | ☐ |
| Simuladores profesionales (PO, SM, IT, etc.) | ☐ | ☐ | ☐ | ☐ | ☐ |
| Trazabilidad cognitiva (ver mi camino de aprendizaje) | ☐ | ☐ | ☐ | ☐ | ☐ |
| Detección de riesgos (delegación, errores conceptuales) | ☐ | ☐ | ☐ | ☐ | ☐ |
| Gobernanza (bloqueo de delegación total) | ☐ | ☐ | ☐ | ☐ | ☐ |

**B2. Si tuvieras que eliminar UNA característica, ¿cuál sería?**

```
_________________________________________________________________
```

**B3. Si pudieras agregar UNA característica, ¿cuál sería?**

```
_________________________________________________________________

_________________________________________________________________
```

---

### Sección C: Comparación con Enseñanza Tradicional

**C1. ¿Cómo comparas aprender con AI-Native MVP vs una clase tradicional con profesor humano?**

| Aspecto | AI-Native es MEJOR | Son SIMILARES | Profesor humano es MEJOR |
|---------|-------------------|---------------|--------------------------|
| Disponibilidad 24/7 | ☐ | ☐ | ☐ |
| Paciencia / No juzga | ☐ | ☐ | ☐ |
| Calidad de explicaciones | ☐ | ☐ | ☐ |
| Adaptación a mi ritmo | ☐ | ☐ | ☐ |
| Feedback inmediato | ☐ | ☐ | ☐ |
| Motivación / Inspiración | ☐ | ☐ | ☐ |
| Comprensión de contexto | ☐ | ☐ | ☐ |

**C2. ¿Cuál sería el escenario ideal para ti?**

- [ ] Solo AI-Native MVP (sin clases presenciales)
- [ ] AI-Native MVP como herramienta principal + clases de consulta
- [ ] Clases presenciales + AI-Native como complemento
- [ ] Solo clases tradicionales (sin IA)

**C3. ¿Por qué?**

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

### Sección D: Impacto en el Aprendizaje

**D1. ¿Sientes que aprendiste MÁS usando este sistema vs tus métodos habituales?**

- [ ] Sí, mucho más (30%+ más)
- [ ] Sí, algo más (10-30% más)
- [ ] Aproximadamente igual
- [ ] No, algo menos
- [ ] No, mucho menos

**D2. ¿En qué aspectos específicos sientes que mejoraste?** (marca todas las que apliquen)

- [ ] Comprensión de conceptos fundamentales
- [ ] Capacidad de descomponer problemas
- [ ] Habilidad para debuggear código
- [ ] Razonamiento algorítmico
- [ ] Comprensión de estructuras de datos
- [ ] Capacidad de explicar mi razonamiento
- [ ] Uso responsable de IA para programación
- [ ] Preparación para entrevistas técnicas
- [ ] Soft skills (comunicación con PO/Cliente)
- [ ] Ninguno / No noté mejoras

**D3. ¿Qué tan seguro/a te sientes ahora para enfrentar problemas de programación nuevos?**

- [ ] Mucho más seguro/a que antes
- [ ] Algo más seguro/a
- [ ] Igual que antes
- [ ] Menos seguro/a
- [ ] Mucho menos seguro/a

---

### Sección E: Reflexión sobre IA y Aprendizaje

**E1. Después de usar AI-Native MVP, ¿cambió tu opinión sobre el uso de IA para aprender programación?**

- [ ] Sí, ahora creo que es MÁS beneficioso de lo que pensaba
- [ ] Sí, ahora creo que es MENOS beneficioso de lo que pensaba
- [ ] No, mi opinión no cambió

**E2. ¿Qué aprendiste sobre el uso responsable de IA?**

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

**E3. ¿Crees que la "delegación total" a la IA es un problema real en la educación?**

- [ ] Sí, es un problema muy grave
- [ ] Sí, es un problema moderado
- [ ] No estoy seguro
- [ ] No, no es un problema real
- [ ] No, es una preocupación exagerada

**E4. ¿Te parece correcto que el sistema bloquee solicitudes de código completo?**

- [ ] Sí, definitivamente (es pedagógicamente necesario)
- [ ] Sí, en general (aunque a veces frustra)
- [ ] Neutral
- [ ] No, en general (debería ser más permisivo)
- [ ] No, definitivamente (debería permitir todo)

---

### Sección F: Feedback Abierto Final

**F1. Tres cosas que definitivamente deberían MANTENERSE en la versión final:**

```
1. __________________________________________________________________

2. __________________________________________________________________

3. __________________________________________________________________
```

**F2. Tres cosas que definitivamente deberían CAMBIARSE antes del lanzamiento:**

```
1. __________________________________________________________________

2. __________________________________________________________________

3. __________________________________________________________________
```

**F3. ¿Algo más que quieras compartir sobre tu experiencia?**

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

**¡Gracias por tu tiempo y tu feedback detallado!**

Tu participación en esta UAT es fundamental para hacer de AI-Native MVP una herramienta valiosa para futuros estudiantes de programación. 🚀

---

**Versión**: 1.0
**Última actualización**: 2025-11-24
**Confidencialidad**: Los datos serán anonimizados (k≥5) antes de cualquier publicación.