# Plantilla de Reporte de Bugs - UAT AI-Native MVP

Use esta plantilla para reportar cualquier problema, error o comportamiento inesperado durante las pruebas de aceptación de usuarios.

---

## 📝 Información del Bug

### Bug ID
**Generado automáticamente por el sistema**: BUG-XXX

### Título del Bug
**Descripción concisa en una línea** (ej: "Error 504 al enviar prompt largo")

```
_________________________________________________________________
```

### Reportado por
- **Estudiante**: [E01/E02/E03/E04/E05]
- **Fecha y hora**: [Automático - 2025-11-24 10:30:00]
- **Sesión ID**: [Automático si aplica]

---

## 🎯 Severidad y Prioridad

### Severidad
Selecciona UNA opción:

- [ ] **CRITICAL** (P0) - Sistema inutilizable, pérdida de datos, vulnerabilidad de seguridad
  - Ejemplos: No puedo iniciar sesión, sesión se pierde al recargar, datos desaparecen

- [ ] **HIGH** (P1) - Funcionalidad principal no funciona, afecta mayoría de usuarios
  - Ejemplos: Tutor no responde, evaluación no se genera, trazas no se guardan

- [ ] **MEDIUM** (P2) - Funcionalidad secundaria afectada, workaround disponible
  - Ejemplos: Gráfico de trazabilidad no se actualiza, filtro no funciona correctamente

- [ ] **LOW** (P3) - Problema cosmético, no afecta funcionalidad
  - Ejemplos: Texto desalineado, color incorrecto, botón demasiado grande

### Frecuencia
¿Con qué frecuencia ocurre este bug?

- [ ] **Siempre** (100% reproducible)
- [ ] **Frecuente** (50-99% del tiempo)
- [ ] **Ocasional** (10-49% del tiempo)
- [ ] **Raro** (< 10% del tiempo)
- [ ] **Una sola vez** (no pude reproducir)

---

## 📋 Descripción del Bug

### ¿Qué pasó?
Describe el problema con el mayor detalle posible.

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

### ¿Qué esperabas que pasara?
Describe el comportamiento esperado/correcto.

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

### ¿Qué pasó en realidad?
Describe el comportamiento incorrecto observado.

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

## 🔄 Pasos para Reproducir

**IMPORTANTE**: Proporciona pasos detallados para que el equipo técnico pueda reproducir el bug.

**Paso 1**:
```
_________________________________________________________________
```

**Paso 2**:
```
_________________________________________________________________
```

**Paso 3**:
```
_________________________________________________________________
```

**Paso 4** (si aplica):
```
_________________________________________________________________
```

**Paso 5** (si aplica):
```
_________________________________________________________________
```

### Resultado Esperado
```
_________________________________________________________________
```

### Resultado Actual
```
_________________________________________________________________
```

---

## 🖼️ Evidencia

### Capturas de Pantalla
**Adjunta capturas** (recomendado - arrastra archivos aquí o pega URLs):

- Screenshot 1: _____________________________________________________
- Screenshot 2: _____________________________________________________
- Screenshot 3: _____________________________________________________

**Tip**: Usa Snipping Tool (Windows) o Cmd+Shift+4 (Mac) para capturar pantalla.

### Video
**Si el bug es difícil de capturar** en una imagen, graba un video corto (10-30 segundos):

- Video URL (Loom, Drive, YouTube): _____________________________________

### Logs / Mensajes de Error
**Si ves algún mensaje de error**, cópialo textualmente aquí:

```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

### Datos de Prueba
**Si el bug involucra datos específicos**, proporciónalos:

**Prompt usado**:
```
_________________________________________________________________
```

**Actividad**: [ej: TP1 - Colas Circulares]

**Modo**: [TUTOR / PO / SM / IT / IR / CX / DSO / EVAL]

**Session ID**: [Si aplica - visible en panel de trazabilidad]

---

## 💻 Información del Entorno

### Navegador
- [ ] Chrome (versión: _______)
- [ ] Firefox (versión: _______)
- [ ] Edge (versión: _______)
- [ ] Safari (versión: _______)
- [ ] Otro: _______________

### Sistema Operativo
- [ ] Windows 10
- [ ] Windows 11
- [ ] macOS (versión: _______)
- [ ] Linux (distribución: _______)
- [ ] Otro: _______________

### Resolución de Pantalla
- [ ] 1920x1080 (Full HD)
- [ ] 1366x768
- [ ] 1280x720 (HD)
- [ ] Otra: _______________

### Conexión a Internet
- [ ] Wifi (velocidad aprox: ______ Mbps)
- [ ] Ethernet (cableada)
- [ ] Móvil (4G/5G)

**¿La conexión era estable cuando ocurrió el bug?**
- [ ] Sí
- [ ] No (hubo cortes o lentitud)

---

## 🔍 Contexto Adicional

### ¿Estabas haciendo algo inusual antes del bug?
```
_________________________________________________________________

_________________________________________________________________
```

### ¿Usaste algún atajo de teclado o acción especial?
```
_________________________________________________________________
```

### ¿Copiaste/pegaste texto de otra fuente?
- [ ] Sí, desde: ___________________
- [ ] No

### ¿Abriste DevTools (F12) o Console?
- [ ] Sí → ¿Viste errores en la consola?
  ```
  _________________________________________________________________
  ```
- [ ] No

---

## 🛠️ Workaround (Solución Temporal)

### ¿Encontraste alguna forma de evitar el problema?
```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

**Ejemplos**:
- Recargar la página funcionó
- Cambiar de navegador resolvió el problema
- Usar un prompt más corto evitó el error

---

## 📌 Información Adicional

### ¿Este bug bloquea tu progreso en la UAT?
- [ ] Sí, no puedo continuar con las pruebas
- [ ] No, puedo seguir con otras actividades
- [ ] Parcialmente (puedo hacer algunas cosas)

### ¿Es similar a otro bug que ya reportaste?
- [ ] Sí, relacionado con: BUG-____
- [ ] No, es un problema nuevo

### Comentarios Adicionales
```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

## ✅ Checklist de Envío

Antes de enviar, verifica:

- [ ] Título es descriptivo (no solo "Error" o "No funciona")
- [ ] Severidad está seleccionada
- [ ] Pasos para reproducir están completos
- [ ] Adjunté captura de pantalla o video
- [ ] Copié mensaje de error completo (si aplica)
- [ ] Especifiqué navegador y sistema operativo
- [ ] Describí qué esperaba vs qué pasó realmente

---

## 📬 Envío del Reporte

**Método 1** - Formulario Web (Recomendado):
1. Ve a: `https://staging.ai-native.example.com/report-bug`
2. Copia y pega la información de esta plantilla
3. Haz click en "Enviar Reporte"

**Método 2** - Email (Alternativo):
- Envía a: [email instructor]
- Asunto: `[UAT BUG] [SEVERITY] Título del bug`
- Adjunta capturas de pantalla

**Método 3** - Slack (Urgente):
- Canal: #uat-bugs
- Menciona: @instructor
- Solo para bugs CRITICAL que bloquean tu progreso

---

## 🔄 Seguimiento

### Confirmación de Recepción
Recibirás un email automático con:
- Bug ID asignado (ej: BUG-015)
- Link para seguimiento en tiempo real
- Tiempo estimado de respuesta

### Actualizaciones
Serás notificado cuando:
- El bug sea **triaged** (priorizado)
- Se **asigne** a un desarrollador
- Se **resuelva** (fix disponible en staging)
- Se **cierre** (verificado y funcional)

### Tu Feedback
Si el fix resuelve el problema, por favor:
1. Verifica el fix en staging
2. Responde al email de cierre con: "Verificado ✓"
3. Si persiste, responde: "NO resuelto" + descripción

---

## 📊 Ejemplos de Buenos Reportes

### Ejemplo 1: Bug CRITICAL

```markdown
**Título**: "Error 500 al finalizar sesión - Datos de evaluación se pierden"

**Severidad**: CRITICAL
**Frecuencia**: Siempre (100%)

**Descripción**:
Cuando intento finalizar una sesión de trabajo (después de 30-45 minutos),
el sistema muestra "Error 500 Internal Server Error" y la evaluación de
proceso (E-IA-Proc) no se genera. Al volver a iniciar sesión, la sesión
aparece como "activa" pero no puedo acceder a ella ni finalizarla.

**Pasos para Reproducir**:
1. Crear sesión con TUTOR mode
2. Interactuar durante ~40 minutos (7-8 prompts)
3. Click en botón "Finalizar Sesión"
4. Ver error 500 en pantalla roja
5. Recargar página
6. Ver sesión aún en estado "activa" pero inaccesible

**Resultado Esperado**: Sesión finaliza correctamente, se genera reporte de evaluación

**Resultado Actual**: Error 500, sesión queda colgada

**Screenshot**: [adjunto: error-500-finalize.png]

**Logs**:
```
POST /api/v1/sessions/session_abc123/end
Status: 500 Internal Server Error
Body: {"error": "Database connection timeout"}
```

**Entorno**: Chrome 120.0, Windows 11, 1920x1080, Wifi 50 Mbps

**Workaround**: Ninguno - no puedo finalizar la sesión

**Bloquea progreso**: SÍ - no puedo completar escenario 2 de UAT
```

### Ejemplo 2: Bug HIGH

```markdown
**Título**: "Gráfico de trazabilidad no se actualiza en tiempo real"

**Severidad**: HIGH
**Frecuencia**: Frecuente (80%)

**Descripción**:
El gráfico de "Evolución de AI Dependency" en el panel de trazabilidad
muestra datos desactualizados. Solo se actualiza al recargar la página
manualmente (F5).

**Pasos para Reproducir**:
1. Abrir panel de trazabilidad en pestaña separada
2. Hacer 3 interacciones en pestaña de chat
3. Volver a pestaña de trazabilidad
4. El gráfico muestra los mismos datos de hace 10 minutos

**Resultado Esperado**: Gráfico se actualiza automáticamente cada 30-60 segundos

**Resultado Actual**: Requiere recarga manual (F5)

**Screenshot**: [adjunto: grafico-desactualizado.png]

**Entorno**: Firefox 118.0, macOS Ventura, 1440x900

**Workaround**: Recargar página cada vez que quiero ver datos actualizados

**Bloquea progreso**: NO - puedo continuar, pero es tedioso
```

### Ejemplo 3: Bug MEDIUM

```markdown
**Título**: "Tooltip de estado cognitivo desaparece muy rápido"

**Severidad**: MEDIUM
**Frecuencia**: Siempre (100%)

**Descripción**:
Cuando paso el mouse sobre el badge de "Estado Cognitivo: PLANIFICACION",
el tooltip con explicación aparece pero desaparece después de 1 segundo.
No hay tiempo suficiente para leerlo.

**Pasos para Reproducir**:
1. Ir a cualquier sesión activa
2. Pasar mouse sobre badge "PLANIFICACION"
3. Intentar leer tooltip completo
4. Tooltip desaparece antes de terminar de leer

**Resultado Esperado**: Tooltip permanece visible mientras mouse esté encima

**Resultado Actual**: Tooltip desaparece después de ~1 segundo

**Video**: [loom.com/share/abc123xyz]

**Entorno**: Chrome 120.0, Windows 11

**Workaround**: Pasar mouse varias veces para leer de a poco

**Bloquea progreso**: NO
```

---

**¡Gracias por reportar bugs!** 🐛

Tu ayuda es invaluable para hacer de AI-Native MVP un sistema robusto y confiable.

---

**Versión**: 1.0
**Última actualización**: 2025-11-24
**Contacto**: [email instructor] | Slack: #uat-bugs