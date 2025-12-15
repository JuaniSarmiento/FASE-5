# Guía de Ejecución de UAT - AI-Native MVP

**Fecha de creación**: 2025-11-24
**Estado**: Lista para ejecución
**Duración total**: 2 semanas (10 días hábiles)

---

## 📋 Tabla de Contenidos

1. [Pre-Ejecución: Preparación del Ambiente](#1-pre-ejecución-preparación-del-ambiente)
2. [Semana 1: Escenarios Fundamentales](#2-semana-1-escenarios-fundamentales)
3. [Semana 2: Escenarios Avanzados](#3-semana-2-escenarios-avanzados)
4. [Post-Ejecución: Análisis y Decisión](#4-post-ejecución-análisis-y-decisión)
5. [Troubleshooting y Soporte](#5-troubleshooting-y-soporte)

---

## 1. Pre-Ejecución: Preparación del Ambiente

### Día -3 a Día -1 (3 días antes de iniciar UAT)

#### 1.1 Configuración del Ambiente de Staging

**Ejecutar script de setup**:

**Windows**:
```powershell
cd C:\2025Desarrollo\ariel2\Tesis
.\user-acceptance-testing\setup\setup-uat-environment.ps1 -Environment staging
```

**Linux/macOS**:
```bash
cd /path/to/Tesis
chmod +x user-acceptance-testing/setup/setup-uat-environment.sh
./user-acceptance-testing/setup/setup-uat-environment.sh --staging
```

**Qué hace este script**:
- ✅ Verifica pre-requisitos (Python, venv, database)
- ✅ Inicializa base de datos PostgreSQL (staging)
- ✅ Crea 6 usuarios (E01-E05, INST01)
- ✅ Crea actividad "TP1 - Colas Circulares"
- ✅ Configura sistema de reporte de bugs
- ✅ Configura monitoreo y logging
- ✅ Genera archivo de credenciales (`uat-credentials.md`)

**Duración estimada**: 10-15 minutos

---

#### 1.2 Verificar Infraestructura Kubernetes

**Verificar que staging esté desplegado**:

```bash
# Verificar namespace
kubectl get namespaces | grep ai-native-staging

# Verificar pods
kubectl get pods -n ai-native-staging

# Expected output:
# ai-native-backend-xxx    1/1     Running
# ai-native-frontend-xxx   1/1     Running
# ai-native-postgresql-0   1/1     Running
# redis-xxx                1/1     Running

# Verificar servicios
kubectl get svc -n ai-native-staging

# Verificar ingress
kubectl get ingress -n ai-native-staging
```

**Si hay problemas**:
```bash
# Re-desplegar staging
cd kubernetes/staging
./deploy.sh

# Esperar a que todos los pods estén Ready
./verify.sh
```

**Duración estimada**: 5 minutos (si ya está desplegado), 20 minutos (si hay que re-desplegar)

---

#### 1.3 Validar Acceso a la Aplicación

**Probar acceso a URLs**:

1. **Backend API**: `https://staging.ai-native.example.com/api/v1/health`
   ```bash
   curl https://staging.ai-native.example.com/api/v1/health
   # Expected: {"status": "healthy", "agents": [...]}
   ```

2. **Frontend**: `https://staging.ai-native.example.com`
   - Abrir en navegador
   - Verificar que cargue la página de login

3. **Swagger UI**: `https://staging.ai-native.example.com/docs`
   - Verificar documentación de API

**Duración estimada**: 5 minutos

---

#### 1.4 Probar Login con Usuario de Prueba

**Probar con E01** (primer estudiante):

```bash
curl -X POST https://staging.ai-native.example.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "estudiante1@uat.ai-native.edu",
    "password": "UAT2025_E01!"
  }'

# Expected:
# {
#   "success": true,
#   "data": {
#     "access_token": "eyJ...",
#     "token_type": "bearer",
#     "user": {
#       "id": "E01",
#       "name": "Estudiante 1",
#       "email": "estudiante1@uat.ai-native.edu",
#       "role": "STUDENT"
#     }
#   }
# }
```

**Si falla**:
- Verificar que los usuarios fueron creados correctamente
- Revisar logs del backend: `kubectl logs -n ai-native-staging <backend-pod>`
- Re-ejecutar `create-test-users.py`

**Duración estimada**: 5 minutos

---

#### 1.5 Distribuir Credenciales a Participantes

**Archivo de credenciales**: `user-acceptance-testing/setup/credentials/uat-credentials.md`

**IMPORTANTE - Seguridad**:
- ❌ **NO** enviar credenciales por email sin cifrar
- ❌ **NO** compartir archivo en canales públicos (Slack, WhatsApp)
- ✅ **SÍ** usar email cifrado (PGP, ProtonMail) o servicio seguro (1Password, LastPass)
- ✅ **SÍ** enviar contraseñas separadas del email (por SMS o llamada)

**Plantilla de email**:

```
Asunto: [CONFIDENCIAL] Credenciales UAT - AI-Native MVP

Hola [Nombre del participante],

Gracias por participar en las pruebas de aceptación de usuarios (UAT) del
sistema AI-Native MVP.

CREDENCIALES:
- URL: https://staging.ai-native.example.com
- Email: [email del participante]
- Contraseña temporal: [VER MENSAJE SEPARADO]

IMPORTANTE:
1. Cambiarás tu contraseña en el primer login
2. Lee la Guía Rápida: [link a student-quick-start.md]
3. Firma el consentimiento informado: [link]
4. Horario de soporte: Lun-Vie 9:00-18:00

Cualquier duda, escríbeme.

Saludos,
Instructor UAT
```

**Enviar a**:
- 5 estudiantes (E01-E05)
- 1 instructor (INST01)

**Duración estimada**: 30 minutos (redactar y enviar 6 emails)

---

#### 1.6 Recolectar Consentimientos Informados

**Opciones**:

1. **Formulario digital** (recomendado):
   - Google Forms con pregunta obligatoria de aceptación
   - Incluir texto completo de `CONSENTIMIENTO_INFORMADO.md`
   - Validar identidad (email institucional)

2. **Firma digital**:
   - DocuSign, HelloSign, o similar
   - PDF del consentimiento informado

3. **Email de confirmación**:
   - Participante responde email con "Acepto participar en UAT"
   - Guardar evidencia de consentimiento

**Checklist de consentimientos**:
- [ ] E01 - Estudiante 1
- [ ] E02 - Estudiante 2
- [ ] E03 - Estudiante 3
- [ ] E04 - Estudiante 4
- [ ] E05 - Estudiante 5
- [ ] INST01 - Instructor

**CRÍTICO**: No iniciar UAT hasta tener TODOS los consentimientos firmados.

**Duración estimada**: 2-3 días (esperar respuestas)

---

#### 1.7 Configurar Canales de Comunicación

**Crear canales de Slack** (o alternativa):

1. **#uat-ai-native** (general)
   - Anuncios del instructor
   - Actualizaciones del sistema
   - Coordinación general

2. **#uat-bugs** (reportes de bugs)
   - Solo bugs (severidad CRITICAL/HIGH)
   - Template de bug report
   - Respuestas del equipo técnico

3. **#uat-soporte** (soporte técnico)
   - Dudas de uso del sistema
   - Problemas de acceso
   - Consultas generales

**Invitar a participantes**:
- Todos los estudiantes (E01-E05)
- Instructor (INST01)
- Equipo técnico de soporte

**Duración estimada**: 15 minutos

---

#### 1.8 Sesión de Onboarding (Opcional pero Recomendado)

**Videollamada grupal**: 30-45 minutos

**Agenda**:
1. **Bienvenida** (5 min)
   - Presentación del proyecto
   - Objetivos de la UAT
   - Importancia del feedback honesto

2. **Tour del sistema** (15 min)
   - Demostración de login
   - Creación de primera sesión
   - Interacción con T-IA-Cog
   - Panel de trazabilidad
   - Reportar un bug

3. **Expectativas y cronograma** (10 min)
   - Tiempo estimado diario (45-60 min)
   - Escenarios a completar
   - Fechas de encuestas
   - Soporte disponible

4. **Q&A** (10 min)
   - Responder dudas
   - Aclarar cualquier inquietud

**Grabar sesión** para referencia futura.

**Duración estimada**: 45 minutos + preparación (1 hora total)

---

### Checklist de Pre-Ejecución

Antes de iniciar Día 1, verificar:

- [ ] Ambiente de staging desplegado y funcional
- [ ] Usuarios creados (5 estudiantes + 1 instructor)
- [ ] Actividad "TP1 - Colas Circulares" disponible
- [ ] Credenciales distribuidas a todos los participantes
- [ ] Consentimientos informados firmados por todos (6/6)
- [ ] Canales de comunicación creados (Slack)
- [ ] Sistema de reporte de bugs configurado
- [ ] Monitoreo y logging habilitado
- [ ] Sesión de onboarding completada (opcional)
- [ ] Guías distribuidas (student-quick-start.md, instructor-guide.md)

**Si TODOS los items están marcados**: ✅ **Listo para iniciar Día 1**

---

## 2. Semana 1: Escenarios Fundamentales

### Día 1-2: Onboarding y Tutor Cognitivo

**Participantes**: Todos (E01-E05)
**Tiempo estimado**: 45-60 minutos por día

#### Día 1: Primera Interacción (Escenario 1)

**Objetivos**:
- Validar facilidad de acceso
- Verificar claridad de interfaz
- Probar creación de sesión

**Tareas para estudiantes**:
1. Login con credenciales
2. Cambiar contraseña temporal
3. Crear primera sesión (modo TUTOR)
4. Enviar 3 prompts de exploración conceptual:
   - "¿Qué es una cola circular?"
   - "¿Cuándo usar cola circular vs cola simple?"
   - "¿Cuáles son las operaciones básicas?"

**Criterios de éxito**:
- ✅ Login exitoso en < 30 segundos
- ✅ Creación de sesión sin errores
- ✅ Tutor responde en < 5 segundos
- ✅ Respuestas son pedagógicamente útiles

**Métricas a recolectar**:
- Tiempo desde login hasta primera interacción
- Número de intentos de login fallidos
- Tiempo de respuesta del tutor (p95)

#### Día 2: Sesión de Trabajo Típica (Escenario 2)

**Participantes**: E02, E03, E05 (3 estudiantes intermedios)
**Tiempo estimado**: 45 minutos

**Tareas**:
1. Crear sesión con actividad "TP1 - Colas Circulares"
2. Interactuar con T-IA-Cog durante 30-45 minutos
3. Preguntas sugeridas:
   - Planificación: "Voy a usar un arreglo de tamaño fijo, ¿es correcto?"
   - Implementación: "¿Cómo manejo el wrap-around de índices?"
   - Debugging: "Mi método enqueue() falla cuando la cola está llena"
4. Intentar solicitar código completo (provocar bloqueo de GOV-IA)
5. Finalizar sesión y revisar trazabilidad

**Criterios de éxito**:
- ✅ Tutor responde en modo socrático (no da código completo)
- ✅ Bloqueo de GOV-IA funciona correctamente
- ✅ Trazas N4 capturan intención cognitiva
- ✅ Panel de trazabilidad muestra camino cognitivo

**Acción del instructor**:
- Monitorear sesiones en tiempo real (Live View)
- Observar si GOV-IA bloquea correctamente
- Revisar trazabilidad al final del día

---

### Día 3-4: Simuladores Profesionales

**Participantes**: E02, E03, E05
**Tiempo estimado**: 90 minutos por día

#### Día 3: PO-IA y SM-IA

**Tarea 1: Product Owner (30 min)**
1. Crear sesión con modo PO
2. Recibir requerimiento del PO
3. Hacer preguntas de clarificación:
   - "¿Qué volumen de datos esperamos?"
   - "¿Hay requisitos de performance?"
   - "¿Prioridad de este feature?"

**Tarea 2: Scrum Master (15 min)**
1. Crear sesión con modo SM
2. Completar Daily Standup:
   - ¿Qué hiciste ayer?
   - ¿Qué harás hoy?
   - ¿Impedimentos?
3. Recibir feedback del SM

**Criterios de éxito**:
- ✅ PO da requerimientos realistas pero vagos (simula cliente real)
- ✅ SM detecta impedimentos ocultos
- ✅ Evaluaciones de soft skills son coherentes

#### Día 4: IT-IA, IR-IA, DSO-IA

**Tarea 1: Technical Interviewer (45 min)**
1. Crear sesión con modo INTERVIEW
2. Responder preguntas conceptuales y algorítmicas
3. Recibir evaluación con score y breakdown

**Tarea 2: Incident Responder (20 min)**
1. Crear sesión con modo INCIDENT
2. Diagnosticar incidente simulado
3. Proponer resolución paso a paso

**Tarea 3: DevSecOps (15 min)**
1. Crear sesión con modo SECURITY
2. Compartir código con vulnerabilidad intencional
3. Recibir auditoría OWASP Top 10

**Criterios de éxito**:
- ✅ IT-IA evalúa correctamente nivel técnico
- ✅ IR-IA simula presión de incidente real
- ✅ DSO-IA detecta vulnerabilidades conocidas (SQL injection, etc.)

---

### Día 5: Encuestas SUS y Satisfacción

**Participantes**: Todos (E01-E05)
**Tiempo estimado**: 15-20 minutos

**Tareas**:
1. Completar encuesta SUS (10 preguntas, 5 min)
2. Completar encuesta de satisfacción (8 dimensiones + abiertas, 10 min)
3. Reportar cualquier bug pendiente

**Instructor**:
- Compilar resultados de SUS (calcular score)
- Analizar feedback cualitativo
- Identificar bugs críticos para resolver en fin de semana

**Métricas clave esperadas**:
- SUS Score: ≥65 (aceptable en UAT)
- Satisfacción promedio: ≥3.8/5.0
- Bugs críticos: ≤3 (idealmente 0)

---

## 3. Semana 2: Escenarios Avanzados

### Día 6-7: Evaluación de Proceso y Riesgos

#### Día 6: Evaluador de Procesos (E-IA-Proc)

**Participantes**: Todos (E01-E05)
**Tiempo estimado**: 60 minutos

**Tareas**:
1. Crear sesión completa (30-45 min) con T-IA-Cog
2. Trabajar en implementación de ColaCircular
3. Finalizar sesión
4. Revisar Informe de Evaluación Cognitiva (IEC):
   - Competencia general (INICIAL/INTERMEDIO/AVANZADO)
   - Score (0-100)
   - Dimensiones evaluadas (5)
   - Fortalezas y áreas de mejora

**Criterios de éxito**:
- ✅ Reporte refleja proceso real del estudiante
- ✅ Score es coherente con nivel de competencia
- ✅ Feedback es accionable y útil
- ✅ Estudiantes prefieren esta evaluación vs exámenes tradicionales

#### Día 7: Detección de Riesgos (AR-IA)

**Participante principal**: E04 (estudiante con dificultades)
**Tiempo estimado**: 45 minutos

**Tareas**:
1. Provocar riesgos intencionalmente:
   - Delegación excesiva (solicitar código varias veces)
   - Razonamiento superficial (preguntas muy genéricas)
   - Aceptación acrítica (no cuestionar respuestas)
2. Observar alertas de AR-IA en tiempo real
3. Revisar panel de riesgos al final

**Criterios de éxito**:
- ✅ AR-IA detecta delegación cuando AI Dependency > 60%
- ✅ Alertas son útiles, no intrusivas
- ✅ Estudiante reflexiona sobre su uso de IA

---

### Día 8-9: Accesibilidad, Usabilidad y Uso Libre

#### Día 8: Accesibilidad y Usabilidad (Escenario 7)

**Participantes**: Todos (E01-E05)
**Tiempo estimado**: 30 minutos

**Tareas**:
1. Probar navegación con teclado (Tab, Enter, Esc)
2. Verificar contraste de colores (inspeccionar con DevTools)
3. Probar en diferentes resoluciones:
   - 1920x1080 (Full HD)
   - 1366x768 (laptop común)
   - Mobile (responsive)
4. Probar con diferentes navegadores:
   - Chrome
   - Firefox
   - Edge

**Criterios de éxito**:
- ✅ Navegación por teclado funcional
- ✅ Contraste cumple WCAG 2.1 AA (4.5:1 para texto normal)
- ✅ Responsive funciona en mobile
- ✅ Compatible con 3 navegadores principales

#### Día 9: Uso Libre

**Participantes**: Todos
**Tiempo estimado**: 60 minutos

**Tareas**:
- Usar el sistema libremente
- Probar funcionalidades favoritas
- Experimentar con casos extremos
- Reportar cualquier bug encontrado
- Explorar áreas no cubiertas en escenarios anteriores

**Objetivo**: Descubrir bugs o problemas no anticipados

---

### Día 10: Encuestas Finales y Cierre

**Participantes**: Todos (E01-E05, INST01)
**Tiempo estimado**: 30 minutos

**Tareas**:
1. Completar encuesta de calidad pedagógica (10 min)
2. Completar encuesta de feedback final (15 min)
3. Sesión de cierre grupal (opcional, 30 min):
   - Compartir experiencias
   - Feedback en vivo
   - Agradecimientos
   - Entrega de certificados

**Instructor**:
- Exportar todos los datos de UAT
- Compilar bugs reportados
- Calcular métricas finales
- Preparar para fase de análisis

---

## 4. Post-Ejecución: Análisis y Decisión

### Día 11-12: Compilación de Datos

**Responsable**: Instructor + Equipo técnico
**Duración**: 2 días

**Tareas**:

1. **Exportar datos de staging**:
   ```bash
   # Ejecutar desde frontend del instructor
   curl -X POST https://staging.ai-native.example.com/api/v1/export/research-data \
     -H "Authorization: Bearer $INSTRUCTOR_TOKEN" \
     -d '{
       "start_date": "2025-11-24T00:00:00Z",
       "end_date": "2025-12-08T23:59:59Z",
       "include_traces": true,
       "include_evaluations": true,
       "include_risks": true,
       "format": "json",
       "k_anonymity": 5
     }' > uat-export.json
   ```

2. **Calcular métricas cuantitativas**:
   - SUS Score promedio
   - Satisfacción promedio por dimensión
   - NPS (Net Promoter Score)
   - Bugs por severidad (CRITICAL, HIGH, MEDIUM, LOW)
   - Response time (p50, p95, p99)
   - Error rate (%)
   - Session completion rate (%)

3. **Consolidar feedback cualitativo**:
   - Categorizar comentarios (positivo, neutral, negativo)
   - Identificar temas recurrentes
   - Extraer citas representativas

4. **Analizar trazabilidad cognitiva**:
   - Patrones de uso de agentes (T-IA-Cog, S-IA-X, etc.)
   - Evolución de AI Dependency por estudiante
   - Caminos cognitivos típicos (EXPLOR → PLAN → IMPL → DEBUG)

5. **Compilar bugs**:
   - Listar todos los bugs reportados
   - Clasificar por severidad y frecuencia
   - Identificar bugs duplicados
   - Priorizar para remediación

**Entregable**: Dataset consolidado de UAT

---

### Día 13-14: Análisis Cualitativo

**Responsable**: Instructor + Investigador doctoral
**Duración**: 2 días

**Tareas**:

1. **Análisis de feedback abierto**:
   - Identificar patrones en respuestas abiertas
   - Codificar feedback con categorías (usabilidad, pedagogía, funcionalidad)
   - Extraer insights clave

2. **Correlación de datos**:
   - ¿Estudiantes con alta satisfacción tienen baja AI Dependency?
   - ¿Riesgos detectados correlacionan con frustración reportada?
   - ¿SUS Score correlaciona con tiempo de respuesta?

3. **Análisis pedagógico**:
   - ¿Tutor socrático fue efectivo?
   - ¿Evaluación de proceso fue percibida como justa?
   - ¿Simuladores profesionales añadieron valor?

**Entregable**: Informe de análisis cualitativo

---

### Día 15: Generación de Reportes

**Responsable**: Instructor
**Duración**: 1 día

**Reportes a generar**:

1. **Reporte Ejecutivo** (para stakeholders):
   - Resumen de 2 páginas
   - Métricas clave (SUS, satisfacción, bugs)
   - Decisión Go/No-Go preliminar
   - Recomendaciones de alto nivel

2. **Reporte Técnico** (para equipo de desarrollo):
   - Lista completa de bugs priorizados
   - Mejoras de usabilidad requeridas
   - Performance issues detectados
   - Plan de remediación

3. **Reporte Pedagógico** (para comité académico):
   - Efectividad del tutor socrático
   - Validez de evaluación de proceso
   - Análisis de trazabilidad N4
   - Contribución a objetivos de tesis

**Templates**: Ver sección "Anexos" al final de este documento

---

### Día 16-17: Decisión Go/No-Go

**Responsable**: Instructor + Stakeholders
**Duración**: 2 días

#### Día 16: Reunión de Revisión

**Participantes**:
- Instructor UAT
- Investigador doctoral (Alberto Cortez)
- Equipo técnico (backend, frontend)
- Comité académico (opcional)

**Agenda** (2 horas):
1. Presentación de resultados (30 min)
2. Revisión de métricas cuantitativas (20 min)
3. Discusión de feedback cualitativo (30 min)
4. Análisis de bugs críticos (20 min)
5. Recomendaciones (20 min)

#### Día 17: Decisión Final

**Evaluar criterios Go/No-Go**:

| Criterio | Target | Resultado UAT | Status |
|----------|--------|---------------|--------|
| SUS Score | ≥70 | [resultado] | [GO/NO-GO] |
| Satisfacción | ≥4.0 | [resultado] | [GO/NO-GO] |
| Bugs críticos | ≤5 | [resultado] | [GO/NO-GO] |
| Response time p95 | <3s | [resultado] | [GO/NO-GO] |
| Error rate | <5% | [resultado] | [GO/NO-GO] |

**Opciones de decisión**:

1. **GO (Lanzar a Producción)**:
   - Todos los criterios cuantitativos cumplidos
   - Feedback cualitativo mayormente positivo (≥70%)
   - Bugs críticos resueltos o con workaround
   - Instructor aprueba calidad pedagógica

2. **NO-GO (Postponer Lanzamiento)**:
   - SUS Score <60
   - Bugs críticos >10 sin resolver
   - Feedback cualitativo mayormente negativo
   - Problemas fundamentales de arquitectura

3. **CONDITIONAL GO (Lanzamiento con Reservas)**:
   - SUS Score 60-69 (aceptable pero mejorable)
   - Bugs high >15 pero no críticos
   - Feedback mixto (50/50)
   - **Requiere**: Plan de mejoras en Sprint Post-MVP

**Documentar decisión**:
- Acta de reunión
- Justificación detallada
- Plan de acción (si NO-GO o CONDITIONAL GO)
- Firmas de aprobación

---

### Fase de Remediación (si NO-GO o CONDITIONAL GO)

**Duración**: 2-3 semanas

**Sprint de Corrección**:

**Semana 1: Bugs Críticos**
- Resolver todos los bugs CRITICAL (P0)
- Resolver 80% de bugs HIGH (P1)
- Testing exhaustivo de fixes

**Semana 2: Mejoras de Usabilidad**
- Implementar mejoras identificadas en feedback
- Refinar respuestas de agentes (si aplica)
- Optimizar performance (si response time >3s)

**Semana 3: Validación**
- **Mini-UAT**: 3 días con 2 estudiantes
- Verificar que fixes funcionan
- Calcular nuevo SUS Score
- **Decisión Go/No-Go final**

---

## 5. Troubleshooting y Soporte

### Problemas Comunes Durante UAT

#### Problema 1: Usuario No Puede Iniciar Sesión

**Síntomas**:
- Error "Invalid credentials"
- Error 500 en login
- Página de login no carga

**Solución**:
1. Verificar credenciales (copiar/pegar desde archivo)
2. Verificar que usuario existe:
   ```bash
   kubectl exec -it -n ai-native-staging <backend-pod> -- \
     python -c "from src.ai_native_mvp.database import *; \
                with get_db_session() as s: \
                  print(s.execute(text('SELECT * FROM users WHERE email=:email'), \
                        {'email': 'estudiante1@uat.ai-native.edu'}).fetchone())"
   ```
3. Resetear contraseña si es necesario
4. Verificar logs del backend

#### Problema 2: Tutor No Responde o Tarda Mucho

**Síntomas**:
- Timeout después de 30 segundos
- Response time >10 segundos
- Error 504 Gateway Timeout

**Solución**:
1. Verificar LLM provider (OpenAI API status)
2. Revisar logs de backend (búsqueda de "LLM timeout")
3. Aumentar timeout temporalmente (no ideal para UAT)
4. Usar prompt más corto (workaround)
5. Reportar como bug HIGH

#### Problema 3: Trazas No Se Guardan

**Síntomas**:
- Panel de trazabilidad vacío
- Error al finalizar sesión
- Trazas no aparecen después de interacción

**Solución**:
1. Verificar estado de la base de datos:
   ```bash
   kubectl exec -it -n ai-native-staging postgresql-0 -- \
     psql -U ai_native -d ai_native_staging -c "SELECT COUNT(*) FROM cognitive_traces;"
   ```
2. Revisar logs de backend (errores de database)
3. Verificar transacciones (posible rollback)
4. Re-ejecutar interacción
5. Reportar como bug CRITICAL

#### Problema 4: Estudiante Reporta Bug Duplicado

**Síntomas**:
- Mismo bug reportado por 2+ estudiantes
- Bug ya está en tracker como TRIAGED

**Solución**:
1. Buscar bug en tracker (`bug-tracker.json`)
2. Si existe, responder:
   "Gracias por reportar. Este bug ya está registrado como BUG-XXX y está siendo trabajado."
3. Añadir estudiante como "reporter adicional" en bug
4. Notificar cuando se resuelva

### Escalación de Problemas

**Severidad CRITICAL (P0)** - Respuesta inmediata:
- Sistema inutilizable
- Pérdida de datos
- Vulnerabilidad de seguridad

**Acción**:
1. Notificar a instructor inmediatamente (Slack + email)
2. Equipo técnico investiga en <1 hora
3. Fix o workaround en <4 horas
4. Comunicar a todos los participantes

**Severidad HIGH (P1)** - Respuesta en 4 horas:
- Funcionalidad principal no funciona
- Afecta mayoría de usuarios

**Acción**:
1. Triaging en <4 horas
2. Fix en <2 días
3. Comunicar a usuarios afectados

**Severidad MEDIUM/LOW** - Respuesta en 1-2 días:
- Funcionalidad secundaria
- Problema cosmético

**Acción**:
1. Documentar en tracker
2. Priorizar para post-UAT
3. No bloquear progreso de UAT

---

## Anexos

### Anexo A: Template de Reporte Ejecutivo

```markdown
# UAT Results - Executive Summary

**Project**: AI-Native MVP
**Duration**: 2025-11-24 to 2025-12-08 (2 weeks)
**Participants**: 5 students + 1 instructor

## Key Metrics

| Metric | Target | Result | Status |
|--------|--------|--------|--------|
| SUS Score | ≥70 | [X] | [✅/❌] |
| Satisfaction | ≥4.0 | [X] | [✅/❌] |
| Critical Bugs | ≤5 | [X] | [✅/❌] |
| NPS | ≥50 | [X] | [✅/❌] |

## Highlights

**Strengths**:
- [Point 1]
- [Point 2]
- [Point 3]

**Areas for Improvement**:
- [Point 1]
- [Point 2]
- [Point 3]

## Recommendation

**Decision**: [GO / NO-GO / CONDITIONAL GO]

**Justification**: [2-3 sentences]

**Next Steps**: [If GO: production deployment plan] [If NO-GO: remediation plan]
```

### Anexo B: Template de Bug Report (para equipo técnico)

```markdown
# Bug Report Summary - UAT

**Total Bugs**: [X]
**Critical**: [X] | **High**: [X] | **Medium**: [X] | **Low**: [X]

## Critical Bugs (P0)

### BUG-001: [Título]
- **Severidad**: CRITICAL
- **Frecuencia**: [Siempre/Frecuente/Ocasional]
- **Reportado por**: E01, E03 (2 estudiantes)
- **Descripción**: [...]
- **Pasos para reproducir**: [...]
- **Fix propuesto**: [...]
- **ETA**: [Fecha]

[Repetir para cada bug crítico]

## High Bugs (P1)

[Similar format]

## Prioridades para Sprint de Corrección

1. [BUG-ID]: [Título] - Impacto: [Alto/Medio/Bajo]
2. [...]
```

### Anexo C: Template de Feedback Consolidado

```markdown
# UAT Feedback - Consolidated

## Quantitative Summary

**SUS Score**: [X] / 100
**Satisfaction**: [X] / 5.0
**NPS**: [X]

## Qualitative Themes

### Theme 1: Usability
- **Positive**: [Quote 1], [Quote 2]
- **Negative**: [Quote 1], [Quote 2]
- **Recommendation**: [...]

### Theme 2: Pedagogical Effectiveness
- **Positive**: [...]
- **Negative**: [...]
- **Recommendation**: [...]

[Repetir para cada tema]

## Student Quotes (Representative)

**Most Liked**:
> "[Quote from survey]" - E03

**Most Disliked**:
> "[Quote from survey]" - E04

**Feature Request**:
> "[Quote from survey]" - E01
```

---

## Resumen de Tiempos

| Fase | Duración | Esfuerzo (horas) |
|------|----------|------------------|
| **Pre-Ejecución** | 3-5 días | 8-10 horas (instructor) |
| **Semana 1** | 5 días | 25-30 horas (estudiantes), 10 horas (instructor) |
| **Semana 2** | 5 días | 20-25 horas (estudiantes), 8 horas (instructor) |
| **Post-Ejecución** | 7 días | 40-50 horas (instructor + equipo) |
| **Remediación** (si aplica) | 2-3 semanas | 80-120 horas (equipo técnico) |

**Total**: 3-5 semanas desde pre-ejecución hasta decisión final

---

**¡Éxito en la UAT!** 🚀

Si tienes dudas, consulta las guías completas o contacta al equipo de soporte.

---

**Versión**: 1.0
**Última actualización**: 2025-11-24
**Autor**: Mag. Alberto Cortez