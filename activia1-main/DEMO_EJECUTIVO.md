# 🎯 DEMO EJECUTIVO - SISTEMA ACTIVIA

## Sistema de Entrenamiento con Inteligencia Artificial

### 📋 Resumen Ejecutivo

**ACTIVIA** es una plataforma completa de entrenamiento en programación que combina múltiples agentes de IA especializados para ofrecer una experiencia de aprendizaje personalizada y adaptativa.

### 🚀 Características Principales

#### 1. **Tutor Socrático (T-IA-Cog)** 🎓
- Metodología socrática con Mistral AI
- Respuestas personalizadas basadas en el nivel del estudiante
- Guía paso a paso sin dar soluciones directas
- Fomenta el pensamiento crítico

#### 2. **Simuladores de Entrevista (S-IA-X)** 💼
Múltiples perfiles de entrevistadores:
- **S-IA-Tec**: Entrevistador técnico senior
- **S-IA-RRHH**: Reclutador de recursos humanos
- **S-IA-CTO**: Líder técnico / CTO
- Feedback realista y constructivo

#### 3. **Entrenador Digital** 💻
Sistema de ejercicios prácticos multi-lenguaje:
- **Python**: Fundamentos y avanzado (5 unidades)
- **Java**: POO y fundamentos (1 unidad)
- **Spring Boot**: Framework empresarial (1 unidad)

**Características del Entrenador:**
- ✅ Evaluación automática con IA (Mistral)
- ✅ Feedback personalizado en tiempo real
- ✅ Filtrado avanzado (lenguaje, framework, dificultad)
- ✅ Sistema de gamificación (XP, logros, niveles)
- ✅ Tests ocultos para validación rigurosa

#### 4. **Análisis de Riesgos 5D** 🔍
Evaluación personalizada de la interacción del estudiante:
- **Cognitivo**: Comprensión y razonamiento
- **Ético**: Uso responsable de la IA
- **Epistémico**: Validación de conocimiento
- **Técnico**: Implementación correcta
- **Gobernanza**: Seguimiento de mejores prácticas

Puntuación: 0-50 por dimensión (0=sin riesgo, 50=riesgo máximo)

---

## 🏃‍♂️ Inicio Rápido del Demo

### Prerequisitos
- Docker y Docker Compose instalados
- Python 3.11+
- Node.js 18+ (para frontend)

### 1. Iniciar el Sistema

```powershell
# Opción A: Con Docker (Recomendado)
docker-compose up -d

# Opción B: Desarrollo local
# Backend
cd backend
python -m backend

# Frontend (en otra terminal)
cd frontEnd
npm install
npm run dev
```

### 2. Verificar que el Sistema Está Listo

```powershell
python check_sistema_demo.py
```

Deberías ver:
```
✅ Backend respondiendo en /health
✅ Sistema listo para el demo!
```

### 3. Ejecutar el Demo Completo

```powershell
python test_sistema_completo_demo.py
```

Este script ejecuta automáticamente:
1. ✅ Tests del Tutor Socrático (4 casos)
2. ✅ Tests de Simuladores (3 perfiles)
3. ✅ Tests del Entrenador Digital (estadísticas, filtros, evaluaciones)
4. ✅ Test de Análisis de Riesgos 5D
5. 📊 Genera reporte JSON completo

---

## 📊 Interpretación de Resultados

### Salida del Demo

El script genera una salida colorizada en consola mostrando:

#### ✅ Tests Exitosos (Verde)
```
✅ Pregunta Conceptual - POO
   • Longitud respuesta: 450 caracteres
   • Es Socrática: Sí
```

#### ⚠️ Advertencias (Amarillo)
```
⚠️ Test con resultado parcial
   • Score: 65/100
```

#### ❌ Errores (Rojo)
```
❌ Test fallido
   • Error: Connection timeout
```

### Reporte JSON

Se genera automáticamente `demo_report_TIMESTAMP.json`:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "session_id": "demo_session_1705320600",
  "tests": [
    {
      "section": "Tutor Socrático",
      "total": 4,
      "passed": 4,
      "details": [...]
    },
    ...
  ]
}
```

---

## 🎯 Casos de Uso Demostrados

### 1. Estudiante Aprendiendo Python
```
Usuario: "¿Cómo funciona una lista de comprensión?"
Tutor: "Excelente pregunta. Antes de explicarte, 
        ¿puedes decirme cómo crearías una lista 
        de números del 1 al 10 con un bucle for?"
```

### 2. Practicando Java en el Entrenador
```
Ejercicio: U6-JAVA-02 - Sistema de Descuentos
Dificultad: Medium
Lenguaje: Java

El estudiante escribe código → IA evalúa → Feedback instantáneo
Score: 85/100
XP Ganado: 25
Feedback: "Excelente implementación de condicionales..."
```

### 3. Simulación de Entrevista Técnica
```
Candidato: "¿Qué es un closure en JavaScript?"
Entrevistador (S-IA-Tec): "Interesante que menciones closures. 
                           ¿Podrías explicarme un caso real 
                           donde los hayas utilizado?"
```

### 4. Análisis de Riesgos Post-Sesión
```
Dimensión Cognitiva: 15/50 (BAJO) ✅
- El estudiante demuestra razonamiento sólido
- Hace preguntas relevantes y profundas

Dimensión Ética: 5/50 (BAJO) ✅
- Uso responsable de la IA como herramienta de apoyo
- No busca soluciones directas
```

---

## 🔧 Configuración del Sistema

### Variables de Entorno Importantes

```bash
# Mistral AI
MISTRAL_API_KEY=tu_api_key_aqui

# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/activia

# Redis (cache y sessions)
REDIS_URL=redis://localhost:6379
```

### Endpoints Principales

#### Backend (http://localhost:8000)
- `/docs` - Documentación interactiva de API
- `/tutor/ask` - Tutor Socrático
- `/simulator/interact` - Simuladores
- `/exercises/json/list` - Lista de ejercicios
- `/exercises/json/evaluate` - Evaluar código
- `/risk-analysis/analyze` - Análisis 5D

#### Frontend (http://localhost:3000)
- `/dashboard` - Panel principal
- `/tutor` - Interfaz del tutor
- `/simulators` - Simuladores de entrevista
- `/exercises` - **Entrenador Digital** ⭐
- `/risk-analysis` - Análisis de riesgos

---

## 📈 Métricas del Sistema

### Ejercicios Disponibles
- **Python**: 4-5 unidades (variables, funciones, OOP, async, etc.)
- **Java**: 1 unidad (fundamentos, POO)
- **Spring Boot**: 1 unidad (REST, JPA, Services)

**Total**: 12+ ejercicios con evaluación automática

### Filtros Disponibles
- **Por Lenguaje**: Python, Java
- **Por Framework**: Spring Boot
- **Por Dificultad**: Easy, Medium, Hard
- **Por Tags**: variables, loops, oop, rest-api, jpa, etc.
- **Por Unidad**: 1-7

### Sistema de Gamificación
- **XP por ejercicio**: 10-50 puntos
- **Niveles**: Novato → Intermedio → Avanzado → Experto
- **Logros**: Primer ejercicio, Racha de 7 días, etc.

---

## 🎓 Arquitectura Técnica

```
┌─────────────────────────────────────────────┐
│           Frontend (React + TS)             │
│    Dashboard | Tutor | Simuladores |        │
│           Entrenador Digital                │
└─────────────────┬───────────────────────────┘
                  │ REST API
┌─────────────────▼───────────────────────────┐
│         Backend (FastAPI + Python)          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Tutor   │  │Simulator │  │Entrenador│  │
│  │  Agent   │  │  Agents  │  │ Digital  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │              │        │
│  ┌────▼─────────────▼──────────────▼─────┐  │
│  │      Mistral AI Integration           │  │
│  │   (mistral-small, mistral-large)      │  │
│  └───────────────────────────────────────┘  │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│     PostgreSQL + Redis + Docker             │
└─────────────────────────────────────────────┘
```

---

## 🏆 Ventajas Competitivas

### 1. **Multi-Agente Especializado**
No es un chatbot genérico, sino agentes especializados:
- Tutor pedagógico (metodología socrática)
- Entrevistadores con diferentes perfiles
- Evaluador automático de código

### 2. **Multi-Lenguaje**
Soporte real para Python, Java y Spring Boot
- No solo teoría, ejercicios prácticos ejecutables
- Evaluación automática con tests ocultos

### 3. **IA de Última Generación**
- Mistral AI (modelos europeos, GDPR-compliant)
- Prompts especializados por contexto
- Temperatura ajustada según tipo de tarea

### 4. **Análisis Profundo**
- Análisis de Riesgos 5D personalizado
- No es genérico, analiza conversaciones reales
- Recomendaciones accionables

### 5. **Gamificación Completa**
- Sistema de XP y niveles
- Logros y recompensas
- Seguimiento de progreso

---

## 📞 Soporte y Siguiente Pasos

### Para Ejecutivos

**Pregunta**: ¿El sistema está listo para producción?
**Respuesta**: 
- ✅ Core funcional al 100%
- ✅ Integración con Mistral AI estable
- ⚠️ Pendiente: Escalabilidad (Kubernetes)
- ⚠️ Pendiente: Monitoreo avanzado (Grafana/Prometheus)

**Pregunta**: ¿Cuánto cuesta operar?
**Respuesta**:
- Mistral AI: ~$0.002 por 1K tokens (muy económico)
- Infra: ~$50-100/mes (AWS/DigitalOcean básico)
- **Proyección**: $200-300/mes para 100 usuarios activos

**Pregunta**: ¿Cómo se diferencia de ChatGPT?
**Respuesta**:
- ✅ Especializado en educación (no genérico)
- ✅ Metodología pedagógica integrada
- ✅ Evaluación automática de código
- ✅ Análisis de riesgos personalizado
- ✅ Gamificación y seguimiento de progreso

### Roadmap Q1 2024

1. **Enero**: 
   - ✅ Migración a Mistral AI (COMPLETADO)
   - ✅ Entrenador Digital multi-lenguaje (COMPLETADO)

2. **Febrero**:
   - 🔄 Dashboard analytics avanzado
   - 🔄 Más ejercicios (JavaScript, TypeScript)

3. **Marzo**:
   - 📅 Integración con LMS (Moodle, Canvas)
   - 📅 API pública para instituciones

---

## 🎬 Demo en Vivo

### Guión Recomendado (10 minutos)

**Minuto 1-2**: Introducción
- Mostrar dashboard
- Explicar 4 módulos principales

**Minuto 3-4**: Tutor Socrático
- Hacer pregunta sobre POO
- Mostrar cómo guía sin dar respuesta directa

**Minuto 5-6**: Entrenador Digital ⭐
- Mostrar catálogo de ejercicios
- Filtrar por Java / Spring Boot
- Resolver ejercicio simple
- Mostrar evaluación IA en tiempo real

**Minuto 7-8**: Simulador de Entrevista
- Iniciar entrevista con S-IA-Tec
- Responder pregunta técnica
- Mostrar feedback realista

**Minuto 9-10**: Análisis de Riesgos
- Ejecutar análisis 5D
- Explicar dimensiones
- Mostrar recomendaciones personalizadas

**Cierre**: Ejecutar `test_sistema_completo_demo.py` y mostrar reporte

---

## 📝 Notas Técnicas

### Performance
- Tutor: ~2-4s de respuesta
- Evaluación ejercicio: ~5-8s
- Análisis de Riesgos: ~10-15s

### Escalabilidad
- Backend: Stateless, fácil de escalar horizontalmente
- Redis: Cache de sesiones y resultados
- PostgreSQL: Almacenamiento persistente

### Seguridad
- Ejecución de código en sandbox aislado
- Rate limiting en endpoints
- Validación de inputs
- Logs de auditoría completos

---

## ✅ Checklist Pre-Demo

```
□ Backend corriendo (python -m backend o docker-compose up)
□ Frontend corriendo (npm run dev)
□ Mistral API key configurada
□ Base de datos inicializada
□ Redis funcionando
□ Ejecutar check_sistema_demo.py (debe pasar ✅)
□ Test rápido manual de cada módulo
□ Preparar ejercicio demo en Entrenador Digital
```

---

**🎯 ¡Sistema listo para demostración ejecutiva!**

Para cualquier duda técnica, consultar:
- Documentación API: http://localhost:8000/docs
- Logs del sistema: `docker-compose logs -f backend`
- Test de salud: `python check_sistema_demo.py`
