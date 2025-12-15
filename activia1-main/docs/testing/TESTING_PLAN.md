# 🧪 Plan de Testing - Mejoras AI-Native

## Objetivo
Validar que las optimizaciones de rendimiento, resiliencia y UX funcionan correctamente antes de producción.

---

## 📋 Pre-requisitos

- [x] Docker Desktop instalado y corriendo
- [x] Node.js 18+ instalado
- [x] PowerShell 5.1+ (Windows)
- [x] 8GB RAM disponible (4GB para Ollama + 4GB para sistema)
- [x] 10GB espacio en disco (para modelo llama3.2:3b)

---

## 🎯 Tests de Backend

### Test 1: Verificar Modelo Llama3.2:3b

**Objetivo**: Confirmar que el modelo nuevo está instalado y es más rápido

```powershell
# Verificar modelo instalado
docker exec ai-native-ollama ollama list

# Debe mostrar:
# llama3.2:3b    abc123    2.0 GB    ...
```

**Criterio de éxito**: ✅ Modelo aparece en la lista

---

### Test 2: Keep-Alive Permanente

**Objetivo**: Validar que no hay latencia en la primera consulta

```powershell
# Primera consulta (debe ser <2s, no 10s como antes)
Measure-Command {
  curl -X POST http://localhost:8000/api/v1/tutor/ask `
    -H "Content-Type: application/json" `
    -d '{"session_id":"test","prompt":"Hola"}'
}

# Segunda consulta (debe ser <1s)
Measure-Command {
  curl -X POST http://localhost:8000/api/v1/tutor/ask `
    -H "Content-Type: application/json" `
    -d '{"session_id":"test","prompt":"¿Cómo estás?"}'
}
```

**Criterio de éxito**: 
- ✅ Primera consulta: <3s
- ✅ Segunda consulta: <1s
- ❌ ANTES: Primera consulta ~8-10s

---

### Test 3: Reintentos Inteligentes

**Objetivo**: Confirmar que el sistema se recupera automáticamente de fallos temporales

```powershell
# Paso 1: Detener Ollama
docker-compose stop ollama

# Paso 2: Intentar consulta (debe fallar pero reintentando)
curl -X POST http://localhost:8000/api/v1/tutor/ask `
  -H "Content-Type: application/json" `
  -d '{"session_id":"test","prompt":"Test"}' `
  -v

# Paso 3: Ver logs (debe mostrar reintentos)
docker-compose logs api | Select-String "attempt"

# Paso 4: Reiniciar Ollama rápido
docker-compose start ollama

# Paso 5: Intentar de nuevo (debe recuperarse en 2-4s)
curl -X POST http://localhost:8000/api/v1/tutor/ask `
  -H "Content-Type: application/json" `
  -d '{"session_id":"test","prompt":"Test recuperación"}'
```

**Criterio de éxito**:
- ✅ Logs muestran "attempt 1/3", "attempt 2/3", etc.
- ✅ Si Ollama se recupera durante reintentos, la request tiene éxito
- ✅ Si no se recupera, falla después de 3 intentos (no infinito)

---

### Test 4: Circuit Breaker (Fallback)

**Objetivo**: Validar respuestas de fallback cuando Ollama está muerto

```powershell
# Detener Ollama completamente
docker-compose stop ollama

# Consulta al tutor (debe retornar fallback, no error 500)
curl -X POST http://localhost:8000/api/v1/tutor/ask `
  -H "Content-Type: application/json" `
  -d '{"session_id":"test","prompt":"¿Cómo hago un bucle?"}'
```

**Criterio de éxito**:
- ✅ HTTP 200 (no 500)
- ✅ Respuesta contiene "⚠️ El sistema de IA está experimentando dificultades"
- ✅ Respuesta tiene pistas genéricas pero útiles (preguntas socráticas)

---

### Test 5: Comparación de Performance

**Objetivo**: Medir mejora cuantificable vs. phi3

| Métrica | phi3 (ANTES) | llama3.2:3b (AHORA) | Mejora |
|---------|--------------|---------------------|--------|
| Latencia primera consulta | 8-10s | <3s | **70% menos** |
| Latencia consultas siguientes | 1-2s | <1s | **50% menos** |
| RAM consumida (Ollama) | ~7GB | ~3GB | **57% menos** |
| Tamaño del modelo | 4.7GB | 2.0GB | **57% menos** |

**Cómo medir**:
```powershell
# Reiniciar Ollama para limpiar memoria
docker-compose restart ollama
Start-Sleep -Seconds 15

# Medir primera consulta
Measure-Command { 
  curl -s http://localhost:8000/api/v1/tutor/ask -X POST -H "Content-Type: application/json" -d '{"session_id":"perf","prompt":"Hola"}' | Out-Null 
}

# Medir RAM de Ollama
docker stats ai-native-ollama --no-stream
```

---

## 🎨 Tests de Frontend

### Test 6: Skeleton Loading

**Objetivo**: Validar que no se ve pantalla blanca durante carga

```powershell
# Iniciar frontend
cd frontEnd
npm run dev
```

**Pasos manuales**:
1. Abrir http://localhost:5173/exercises/1 con DevTools (Network tab)
2. Throttle: "Slow 3G"
3. Recargar página (Ctrl+Shift+R)

**Criterio de éxito**:
- ✅ Aparecen skeletons grises animados inmediatamente
- ✅ NO se ve pantalla blanca vacía
- ✅ Skeletons se reemplazan por contenido real cuando carga

---

### Test 7: Monaco Editor

**Objetivo**: Validar editor profesional con syntax highlighting

**Pasos manuales**:
1. Ir a /exercises/1
2. Escribir código Python en el editor
3. Verificar:
   - ✅ Syntax highlighting (keywords en rosa, strings en amarillo)
   - ✅ Autocomplete funciona (Ctrl+Space)
   - ✅ Números de línea visibles
   - ✅ Tema oscuro aplicado

---

### Test 8: Panel Resizable

**Objetivo**: Validar layout de 3 columnas ajustables

**Pasos manuales**:
1. Ir a /exercises/1
2. Arrastrar divisores verticales (entre paneles)
3. Verificar:
   - ✅ Paneles se redimensionan suavemente
   - ✅ Divisor cambia de color al hover
   - ✅ Tamaños se respetan (min/max)

---

### Test 9: AI Companion Modes

**Objetivo**: Validar cambio entre modos (Tutor/Juez/Simulador)

**Pasos manuales**:
1. Ir a /exercises/1
2. Click en tabs del panel derecho
3. Verificar:
   - ✅ Tab "Tutor" muestra chat
   - ✅ Tab "Juez" muestra interfaz de evaluación
   - ✅ Tab "Simulador" muestra interfaz de roleplay
   - ✅ Cambio de tab es instantáneo

---

### Test 10: Toast Notifications

**Objetivo**: Validar sistema de notificaciones no-intrusivo

**Pasos manuales**:
1. Ir a /exercises/1
2. Pegar código largo (>100 caracteres) en el editor
3. Verificar:
   - ✅ Toast amarillo aparece arriba-derecha
   - ✅ Mensaje: "⚠️ Inserción masiva detectada"
   - ✅ NO bloquea el código (puede seguir escribiendo)
   - ✅ Desaparece solo después de 7s

---

### Test 11: Teacher Dashboard

**Objetivo**: Validar dashboard del docente

**Pasos manuales**:
1. Ir a /teacher/dashboard
2. Verificar:
   - ✅ Gráfico de barras de actividad se renderiza
   - ✅ Tabla de riesgo muestra estudiantes
   - ✅ Badges de riesgo tienen colores (verde/amarillo/rojo)
   - ✅ Live Feed muestra eventos recientes

---

## 🔥 Test de Estrés

### Test 12: Reintentos Bajo Carga

**Objetivo**: Validar que reintentos no causan colapso con múltiples usuarios

```powershell
# Simular 10 usuarios concurrentes (requiere Apache Bench o similar)
# Si no tienes ab, instala: choco install apache-httpd

ab -n 100 -c 10 -p request.json -T "application/json" http://localhost:8000/api/v1/tutor/ask
```

Contenido de `request.json`:
```json
{"session_id":"stress","prompt":"Test"}
```

**Criterio de éxito**:
- ✅ Todas las requests completan (no timeouts)
- ✅ Tasa de éxito >95%
- ✅ p95 latencia <5s

---

## 📊 Checklist de Validación Final

### Backend
- [ ] Modelo llama3.2:3b instalado
- [ ] Keep-Alive funciona (primera consulta rápida)
- [ ] Reintentos funcionan (logs muestran attempts)
- [ ] Fallback funciona (respuesta pedagógica cuando Ollama muerto)
- [ ] Performance mejorada vs. phi3

### Frontend
- [ ] Skeleton loading visible durante carga
- [ ] Monaco Editor con syntax highlighting
- [ ] Paneles resizables funcionan
- [ ] AI Companion con 3 modos
- [ ] Toast notifications aparecen correctamente
- [ ] Teacher Dashboard renderiza gráficos
- [ ] No errores de TypeScript en consola

### Integración
- [ ] Frontend conecta con backend (API calls funcionan)
- [ ] Chat del Tutor recibe respuestas de Ollama
- [ ] Ejecución de código muestra output en terminal
- [ ] Detección de paste masivo dispara toast

---

## 🐛 Registro de Bugs (Template)

Si encontrás bugs durante testing:

```markdown
### Bug #X: [Título descriptivo]

**Componente**: Backend / Frontend / Integración
**Severidad**: 🔴 Crítico / 🟡 Medio / 🟢 Bajo
**Pasos para reproducir**:
1. ...
2. ...

**Resultado esperado**: ...
**Resultado actual**: ...
**Logs/Screenshots**: ...
```

---

## 📈 Métricas a Reportar en Tesis

| Métrica | Cómo medirla | Valor objetivo |
|---------|--------------|----------------|
| Latencia p50 primera consulta | Measure-Command (PowerShell) | <3s |
| Latencia p95 consultas siguientes | Measure-Command | <1.5s |
| Tasa de recuperación de fallos | Logs de reintentos | >80% |
| RAM consumida por Ollama | docker stats | <4GB |
| Time to Interactive (TTI) frontend | Lighthouse (DevTools) | <3s |
| Errores de consola (frontend) | DevTools Console | 0 |

---

**Última actualización**: Diciembre 2025
