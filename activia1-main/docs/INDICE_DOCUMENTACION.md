# 📚 Índice de Documentación - AI-Native Platform v2.0

## 🎯 Por Rol/Objetivo

### 👨‍💻 Quiero INSTALAR el sistema
→ **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** (5 min lectura)
- Instrucciones paso a paso
- Troubleshooting común
- Verificación de instalación

**Quick Start**:
```powershell
.\deploy_mejoras.ps1
```

---

### 🧪 Quiero VALIDAR que funciona
→ **[TESTING_PLAN.md](TESTING_PLAN.md)** (15 min lectura + 30 min ejecución)
- 12 tests de Backend
- 6 tests de Frontend
- 4 tests de Integración
- Métricas a medir

**Quick Check**:
```powershell
# Backend
curl http://localhost:8000/api/v1/health

# Modelo
docker exec ai-native-ollama ollama list
```

---

### 📊 Quiero entender QUÉ CAMBIÓ
→ **[RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)** (10 min lectura)
- Overview de 11 mejoras
- Métricas Before/After
- Impacto esperado

**TL;DR**: 2.3x más rápido + resiliencia automática + UX moderna

---

### 🔧 Quiero saber DETALLES TÉCNICOS
→ **[MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md)** (30 min lectura)
- Explicación profunda de cada optimización
- Código modificado (diffs)
- Justificación de decisiones técnicas

**Highlights**:
- Retry Pattern con Exponential Backoff
- Circuit Breaker con fallbacks pedagógicos
- Workbench Layout tipo VS Code

---

### ✅ Quiero hacer TRACKING de progreso
→ **[CHECKLIST.md](CHECKLIST.md)** (5 min lectura, uso continuo)
- Checklist de implementación (✅ completo)
- Checklist de deploy (🟡 pendiente)
- Checklist de testing (🟡 pendiente)
- Tracking de bugs

**Uso**: Marcar checkboxes a medida que avanzas

---

### 🎓 Escribo mi TESIS
→ **Todas las anteriores** + estos archivos adicionales:

1. **[RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)** → Abstract y Resultados
2. **[MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md)** → Metodología
3. **[TESTING_PLAN.md](TESTING_PLAN.md)** → Experimentación
4. **[CHECKLIST.md](CHECKLIST.md)** → Cronograma

**Papers a citar**:
- Perceived Performance (Nielsen)
- Cognitive Load Theory (Sweller)
- Exponential Backoff (Google SRE Book)
- Circuit Breaker (Martin Fowler)

---

### 🧑‍🏫 Soy DOCENTE (demo/evaluación)
→ **[README_SPRINT_FINAL.md](README_SPRINT_FINAL.md)** (5 min lectura)
- Overview general del sistema
- Quick Start
- Arquitectura simplificada
- Highlights de mejoras

**Demo Script**:
1. Mostrar Workbench (3 paneles)
2. Ejecutar código en Monaco Editor
3. Interactuar con AI Companion (Tutor)
4. Mostrar Teacher Dashboard

---

## 📂 Por Archivo

### 🚀 Documentos Principales (Empezar aquí)

| Archivo | Propósito | Audiencia | Tiempo |
|---------|-----------|-----------|--------|
| **[README_SPRINT_FINAL.md](README_SPRINT_FINAL.md)** | Overview general | Todos | 5 min |
| **[DEPLOY_GUIDE.md](DEPLOY_GUIDE.md)** | Instalación | Developers | 5 min |
| **[RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md)** | Highlights | Stakeholders | 10 min |

### 📖 Documentos Técnicos

| Archivo | Propósito | Audiencia | Tiempo |
|---------|-----------|-----------|--------|
| **[MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md)** | Detalles técnicos | Developers | 30 min |
| **[TESTING_PLAN.md](TESTING_PLAN.md)** | Plan de validación | QA/Testers | 15 min |
| **[CHECKLIST.md](CHECKLIST.md)** | Tracking de progreso | Project Manager | 5 min |

### 🏛️ Documentos Legacy (Referencia)

| Archivo | Propósito | Estado |
|---------|-----------|--------|
| **[FRONTEND_COMPLETO.md](FRONTEND_COMPLETO.md)** | Frontend v1.0 | Obsoleto (v2.0 disponible) |
| **[SISTEMA_OPERACIONAL.md](SISTEMA_OPERACIONAL.md)** | Backend architecture | Vigente |
| **[INSTALL.md](INSTALL.md)** | Instalación básica | Obsoleto (usar DEPLOY_GUIDE.md) |

### 🛠️ Scripts

| Archivo | Propósito | Comando |
|---------|-----------|---------|
| **[deploy_mejoras.ps1](deploy_mejoras.ps1)** | Deploy automático | `.\deploy_mejoras.ps1` |

---

## 🗺️ Flujo de Lectura Recomendado

### Para Implementadores (Developers)

```
1. README_SPRINT_FINAL.md (5 min)
   ↓
2. DEPLOY_GUIDE.md (5 min)
   ↓
3. Ejecutar: .\deploy_mejoras.ps1 (3-5 min)
   ↓
4. TESTING_PLAN.md (15 min lectura)
   ↓
5. Ejecutar tests (30 min)
   ↓
6. CHECKLIST.md (marcar completados)
   ↓
7. MEJORAS_IMPLEMENTADAS.md (profundizar si es necesario)
```

**Total**: ~1-2 horas de setup completo

---

### Para Evaluadores (Tesis/Defensas)

```
1. RESUMEN_EJECUTIVO.md (10 min)
   ↓
2. README_SPRINT_FINAL.md (5 min)
   ↓
3. MEJORAS_IMPLEMENTADAS.md (secciones relevantes)
   ↓
4. Ver demo en vivo o video
```

**Total**: ~30 min de lectura + demo

---

### Para Usuarios Finales (Alumnos/Docentes)

```
1. README_SPRINT_FINAL.md → Sección "Quick Start"
   ↓
2. Abrir: http://localhost:5173
   ↓
3. Tutorial in-app (si aplica)
```

**Total**: <5 min para empezar a usar

---

## 🎯 Matriz de Decisión

**¿Qué documento leer según tu pregunta?**

| Pregunta | Documento |
|----------|-----------|
| ¿Cómo instalo el sistema? | [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) |
| ¿Qué mejoró en esta versión? | [RESUMEN_EJECUTIVO.md](RESUMEN_EJECUTIVO.md) |
| ¿Cómo funciona técnicamente X? | [MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md) |
| ¿Cómo valido que funcione? | [TESTING_PLAN.md](TESTING_PLAN.md) |
| ¿En qué estado está el proyecto? | [CHECKLIST.md](CHECKLIST.md) |
| ¿Qué es el sistema en general? | [README_SPRINT_FINAL.md](README_SPRINT_FINAL.md) |
| ¿Qué archivos modifiqué? | [CHECKLIST.md](CHECKLIST.md) → Fase 1 |
| ¿Cómo reporto un bug? | [CHECKLIST.md](CHECKLIST.md) → Fase 5 |
| ¿Qué métricas medir para tesis? | [TESTING_PLAN.md](TESTING_PLAN.md) → Sección Métricas |

---

## 📦 Archivos NO Documentados (Pero Importantes)

### Código Fuente Modificado

| Archivo | Cambio Principal |
|---------|------------------|
| `docker-compose.yml` | Modelo llama3.2:3b + Keep-Alive |
| `backend/llm/ollama_provider.py` | Retry logic |
| `backend/core/ai_gateway.py` | Circuit Breaker |
| `frontEnd/package.json` | Nuevas dependencias |
| `frontEnd/tsconfig.json` | Path aliases |

Ver **[CHECKLIST.md](CHECKLIST.md)** → Fase 1 para lista completa.

### Componentes Nuevos (Frontend)

Ver estructura en:
- `frontEnd/src/components/ui/` (Skeleton, Toast)
- `frontEnd/src/components/layout/` (WorkbenchLayout)
- `frontEnd/src/components/editor/` (MonacoEditor)
- `frontEnd/src/components/ai/` (AICompanionPanel)
- `frontEnd/src/components/teacher/` (TeacherDashboard)
- `frontEnd/src/pages/` (ExercisePage)

Documentados en: **[MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md)**

---

## 🔍 Búsqueda Rápida

### Temas Clave

- **Retry Logic** → [MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md) #3
- **Circuit Breaker** → [MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md) #4
- **llama3.2:3b** → [MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md) #1
- **Keep-Alive** → [MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md) #2
- **Monaco Editor** → [MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md) #7
- **Workbench Layout** → [MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md) #6
- **Teacher Dashboard** → [MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md) #9
- **Skeleton Loading** → [MEJORAS_IMPLEMENTADAS.md](MEJORAS_IMPLEMENTADAS.md) #10

### Comandos Útiles

```powershell
# Deploy completo
.\deploy_mejoras.ps1

# Verificar backend
curl http://localhost:8000/api/v1/health

# Verificar modelo
docker exec ai-native-ollama ollama list

# Verificar logs
docker-compose logs -f api
docker-compose logs -f ollama

# Iniciar frontend
cd frontEnd; npm run dev
```

---

## 📞 ¿Aún perdido?

**Empezá aquí**: [README_SPRINT_FINAL.md](README_SPRINT_FINAL.md)

**Si algo no funciona**: [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) → Troubleshooting

**Si querés entender todo**: Leé los 5 documentos en orden:
1. README_SPRINT_FINAL.md
2. DEPLOY_GUIDE.md
3. RESUMEN_EJECUTIVO.md
4. MEJORAS_IMPLEMENTADAS.md
5. TESTING_PLAN.md

**Total**: ~1 hora de lectura completa

---

**Creado**: Diciembre 2025  
**Versión**: 2.0  
**Mantenedor**: GitHub Copilot (Claude Sonnet 4.5)
