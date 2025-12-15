# Guía Rápida para Estudiantes - UAT AI-Native MVP

## Bienvenido/a a las Pruebas de Usuario

Esta guía te ayudará a empezar rápidamente con la plataforma **AI-Native MVP** durante las pruebas de aceptación de usuarios (UAT).

---

## 📋 Antes de Empezar

### 1. Confirmar Pre-requisitos

**Acceso**:
- [ ] Recibiste email con credenciales (usuario + contraseña temporal)
- [ ] Tienes acceso a la URL: `https://staging.ai-native.example.com`
- [ ] Firmaste el consentimiento informado

**Equipo**:
- [ ] Navegador moderno (Chrome 90+, Firefox 88+, Edge 90+, Safari 14+)
- [ ] Conexión estable a internet (mínimo 5 Mbps)
- [ ] Resolución de pantalla: 1280x720 o superior

**Opcional** (para escenarios avanzados):
- [ ] Git instalado (para compartir repositorio en escenario 5)
- [ ] IDE/Editor de código (VS Code recomendado)

---

## 🚀 Paso 1: Primer Acceso (5 minutos)

### 1.1 Iniciar Sesión

1. Abre el navegador y ve a: `https://staging.ai-native.example.com`
2. Ingresa tus credenciales:
   ```
   Usuario: [tu email institucional]
   Contraseña: [contraseña temporal]
   ```
3. **IMPORTANTE**: Cambia tu contraseña en el primer acceso
   - Mínimo 8 caracteres
   - Incluir mayúsculas, minúsculas, números y símbolos

### 1.2 Verificar Perfil

Después de iniciar sesión, verifica tu perfil:
- **Nombre**: [Tu nombre]
- **ID de estudiante**: E01, E02, E03, E04, o E05
- **Actividades asignadas**: Trabajo Práctico 1 (Colas Circulares)

---

## 🎓 Paso 2: Tu Primera Sesión (15 minutos)

### 2.1 Crear una Sesión de Trabajo

1. En el dashboard, haz clic en **"Nueva Sesión"**
2. Completa el formulario:
   - **Actividad**: Selecciona "TP1 - Colas Circulares"
   - **Modo**: Selecciona "TUTOR" (T-IA-Cog)
   - **Descripción** (opcional): Ej. "Primera sesión de exploración"
3. Haz clic en **"Crear Sesión"**

### 2.2 Interactuar con el Tutor (T-IA-Cog)

La plataforma te presentará una interfaz de chat. Prueba con estos prompts de ejemplo:

**Exploración Conceptual**:
```
¿Qué es una cola circular?
```

**Planificación**:
```
Estoy pensando en implementar una cola circular con un arreglo.
¿Es correcto este enfoque?
```

**Pedir Ayuda (Delegación Parcial)**:
```
No logro entender cómo funciona el índice del frente.
¿Podrías explicármelo con un ejemplo?
```

**Debugging**:
```
Mi método enqueue() no funciona cuando la cola está casi llena.
¿Qué podría estar fallando?
```

### 2.3 Observar las Respuestas

Presta atención a:
- **Estilo pedagógico**: El tutor NO te dará código completo
- **Preguntas socráticas**: Te hará preguntas para guiar tu razonamiento
- **Hints graduales**: Pistas incrementales según tu nivel
- **Metadata**: Al final de cada respuesta verás:
  - `Agente: T-IA-Cog`
  - `Estado Cognitivo: EXPLORACION_CONCEPTUAL` (u otro)
  - `IA Involvement: 40%` (qué tan activa fue la IA)

### 2.4 Experimentar con Delegación Total (Provocar Bloqueo)

Intenta este prompt deliberadamente:
```
Dame el código completo de la clase ColaCircular con todos los métodos.
```

**Resultado esperado**:
- 🚫 El sistema debería **bloquearte** con un mensaje de GOV-IA
- Mensaje tipo: "Solicitud bloqueada por política institucional: Delegación Total"
- Esto es intencional para evitar que dependas completamente de la IA

---

## 🛠️ Paso 3: Explorar Funcionalidades (30 minutos)

### 3.1 Panel de Trazabilidad (TC-N4)

1. Haz clic en **"Ver Trazas"** en el menú lateral
2. Observa tu **Camino Cognitivo**:
   - Secuencia de estados: EXPLORACION → PLANIFICACION → DEBUGGING
   - Gráfico de evolución de AI Dependency (%)
   - Momentos de cambio de estrategia

3. **Experiment**: Haz varias preguntas y observa cómo cambia tu trazabilidad

### 3.2 Panel de Riesgos (AR-IA)

1. Haz clic en **"Riesgos Detectados"**
2. Revisa si hay alertas:
   - 🟡 **Riesgo Cognitivo**: Delegación excesiva, razonamiento superficial
   - 🟠 **Riesgo Ético**: Uso no declarado de IA
   - 🔴 **Riesgo Epistémico**: Error conceptual, aceptación acrítica

3. **Nota**: Esto NO es una calificación, es feedback formativo

### 3.3 Evaluación de Proceso (E-IA-Proc)

1. Al finalizar tu sesión (después de 30-45 minutos de trabajo), haz clic en **"Finalizar Sesión"**
2. El sistema generará un **Informe de Evaluación Cognitiva (IEC)**:
   - **Competencia general**: INICIAL, INTERMEDIO, AVANZADO
   - **Score**: 0-100
   - **Dimensiones evaluadas**:
     - Descomposición de problemas
     - Razonamiento algorítmico
     - Comprensión de estructuras de datos
     - Capacidad de debugging
     - Autorregulación

3. **Lee el informe completo**: Incluye fortalezas y áreas de mejora

---

## 🎭 Paso 4: Simuladores Profesionales (60 minutos)

### 4.1 Product Owner (PO-IA)

1. Crea una nueva sesión con **Modo: PO**
2. El PO te presentará un requerimiento:
   ```
   "Necesitamos un sistema de gestión de colas de atención para un hospital"
   ```
3. Haz preguntas de clarificación:
   ```
   ¿Qué tipos de prioridades debe manejar?
   ¿Cuál es el volumen esperado de pacientes por hora?
   ```

### 4.2 Scrum Master (SM-IA)

1. Crea una nueva sesión con **Modo: SM**
2. Completa un Daily Standup:
   - **¿Qué hiciste ayer?**: "Completé la clase ColaCircular"
   - **¿Qué harás hoy?**: "Implementaré los tests unitarios"
   - **¿Impedimentos?**: "Ninguno" o describe un bloqueo real

3. El SM te dará feedback sobre:
   - Claridad de tu reporte
   - Detección de impedimentos ocultos
   - Sugerencias de proceso ágil

### 4.3 Technical Interviewer (IT-IA)

1. Crea una nueva sesión con **Modo: INTERVIEW**
2. Selecciona tipo: **CONCEPTUAL** o **ALGORITHMIC**
3. Responde las preguntas del entrevistador:
   ```
   IT-IA: "Explícame la diferencia entre una cola y una pila"
   ```
4. Al final, recibirás una evaluación con score y breakdown

### 4.4 Incident Responder (IR-IA)

1. Crea una nueva sesión con **Modo: INCIDENT**
2. El sistema simulará un incidente DevOps:
   ```
   "Producción caída - Error 500 en API de pagos - 5 min downtime"
   ```
3. Diagnostica y propón resolución:
   ```
   1. Revisar logs de la API
   2. Verificar conectividad a base de datos
   3. Rollback a versión anterior si es necesario
   ```

### 4.5 Client Experience (CX-IA)

1. Crea una nueva sesión con **Modo: CLIENT**
2. El cliente te dará requerimientos vagos:
   ```
   "Quiero una app que sea fácil de usar y rápida"
   ```
3. Practica soft skills:
   - Empatía: "Entiendo que la usabilidad es clave para usted"
   - Clarificación: "¿Podría describirme un flujo típico de uso?"
   - Profesionalismo: Evita jerga técnica excesiva

4. Recibirás evaluación de soft skills: empatía, claridad, profesionalismo

### 4.6 DevSecOps (DSO-IA)

1. Crea una nueva sesión con **Modo: SECURITY**
2. Comparte un snippet de código:
   ```python
   password = input("Ingrese contraseña: ")
   query = f"SELECT * FROM users WHERE password = '{password}'"
   ```
3. El DSO auditará según OWASP Top 10:
   - 🔴 **A03:2021 - Injection**: SQL Injection detectada
   - Recomendación: Usar prepared statements

---

## 📊 Paso 5: Reportar Bugs y Dar Feedback (Durante toda la UAT)

### 5.1 Reportar un Bug

Si encuentras un problema:

1. Haz clic en **"Reportar Bug"** (ícono de bicho en la esquina)
2. Completa el formulario:
   - **Título**: "Error al enviar prompt largo"
   - **Descripción**: "Cuando envío un prompt de >500 palabras, la respuesta se corta"
   - **Pasos para reproducir**:
     1. Crear sesión con T-IA-Cog
     2. Enviar prompt de 600 palabras
     3. Observar respuesta truncada
   - **Severidad**: CRITICAL, HIGH, MEDIUM, LOW
   - **Captura de pantalla** (si aplica): Adjuntar

3. El bug será visible en el dashboard del instructor

### 5.2 Completar Encuestas

Durante la UAT, se te pedirá completar:

**Encuesta SUS (System Usability Scale)** - 10 preguntas:
- "Creo que me gustaría usar este sistema frecuentemente"
- "Encontré el sistema innecesariamente complejo"
- Escala 1-5 (Totalmente en desacuerdo → Totalmente de acuerdo)

**Encuesta de Satisfacción** - 8 preguntas:
- Facilidad de uso, utilidad pedagógica, etc.
- Escala 1-5 (Muy insatisfecho → Muy satisfecho)

**Encuesta de Calidad Pedagógica** - 7 preguntas:
- "El tutor promueve razonamiento crítico"
- "Las evaluaciones reflejan mi proceso de aprendizaje"

**Feedback Abierto**:
- "¿Qué es lo que más te gustó?"
- "¿Qué mejorarías?"
- "¿Recomendarías este sistema?"

---

## ⚠️ Problemas Comunes y Soluciones

### "No puedo iniciar sesión"
- ✅ Verifica que estés usando el email correcto
- ✅ Cambia contraseña temporal en primer acceso
- ✅ Limpia caché del navegador (Ctrl+Shift+Del)
- ✅ Contacta al instructor si persiste

### "El tutor no responde / tarda mucho"
- ✅ Espera hasta 15 segundos (LLM requiere procesamiento)
- ✅ Si tarda >30s, refresca la página
- ✅ Reporta como bug si es recurrente

### "No veo mis trazas / riesgos"
- ✅ Asegúrate de haber finalizado la sesión
- ✅ Las trazas se generan durante la interacción (no al final)
- ✅ Refresca la página del panel de trazabilidad

### "El sistema me bloqueó sin razón"
- ✅ Revisa si tu prompt incluye solicitudes de código completo
- ✅ Esto es intencional (GOV-IA protege contra delegación total)
- ✅ Reformula tu pregunta con más especificidad

### "Encontré un bug pero no sé qué severidad poner"
**Guía**:
- **CRITICAL**: Sistema inutilizable, pérdida de datos
- **HIGH**: Funcionalidad principal no funciona
- **MEDIUM**: Funcionalidad secundaria afectada
- **LOW**: Problema cosmético, no afecta uso

---

## 📞 Contacto y Soporte

**Durante la UAT** (Horario: Lunes a Viernes, 9:00-18:00):
- **Email**: [email del instructor]
- **Slack**: Canal #uat-ai-native (respuesta <2h)
- **Videollamada urgente**: [link a Google Meet/Zoom]

**Fuera de horario**:
- Reporta bugs mediante el formulario (serán revisados al día siguiente)
- Consulta la documentación completa: `UAT_PLAN.md`

---

## 🎯 Recordatorios Importantes

1. **Sé honesto**: Reporta TODO lo que encuentres, bueno y malo
2. **Experimenta**: Prueba casos extremos, prompts raros, etc.
3. **No tengas miedo de romper cosas**: Estás en staging, no en producción
4. **Feedback cualitativo es valioso**: "Esto me confundió" es útil aunque no sea un bug
5. **Compara con herramientas reales**: ¿Usarías esto vs ChatGPT/Copilot? ¿Por qué?

---

## 📅 Cronograma de 2 Semanas

**Semana 1** (Días 1-5):
- Día 1-2: Escenarios 1-3 (Onboarding, T-IA-Cog, Uso intensivo)
- Día 3-4: Escenario 4 (Simuladores profesionales)
- Día 5: Completar encuestas SUS y satisfacción

**Semana 2** (Días 6-10):
- Día 6-7: Escenarios 5-6 (E-IA-Proc, AR-IA)
- Día 8-9: Escenario 7 (Accesibilidad/Usabilidad) + Uso libre
- Día 10: Feedback final y cierre

**Tiempo estimado diario**: 45-60 minutos

---

## 🏆 Al Finalizar la UAT

Recibirás:
- ✅ Certificado de participación en UAT
- ✅ Reporte personalizado de tu proceso cognitivo (datos anonimizados)
- ✅ Acceso anticipado a la plataforma en producción (si aprueba Go/No-Go)

**¡Gracias por tu participación!** 🚀

Tu feedback es fundamental para hacer de esta plataforma una herramienta útil para futuros estudiantes de programación.

---

**Versión**: 1.0
**Última actualización**: 2025-11-24
**Contacto**: Mag. Alberto Cortez - [email]