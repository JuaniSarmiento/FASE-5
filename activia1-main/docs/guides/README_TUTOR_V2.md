# 🎓 Tutor Socrático IA - V2.0

## 🚀 Quick Start

### Instalación
```python
from backend.agents import TutorCognitivoAgent

# Inicializar el tutor
tutor = TutorCognitivoAgent()
```

### Uso Básico
```python
# Procesar una solicitud del estudiante
response = tutor.process_student_request(
    session_id="session_123",
    student_prompt="Haceme el código de una cola",
    student_profile={
        "avg_ai_involvement": 0.5,
        "successful_autonomous_solutions": 5,
        "error_self_correction_rate": 0.3
    },
    conversation_history=[]
)

print(response["message"])
# Output: "🚫 No puedo darte el código directamente..."
```

---

## 📋 Características Principales

### ✅ 4 Reglas Inquebrantables

1. **🚫 "Ni a Palos" (Anti-Solución Directa)**
   - Prohibido entregar código completo
   - Rechaza solicitudes de tipo "haceme el código"
   - Contraataca con preguntas

2. **❓ Modo Socrático Prioritario**
   - Default: preguntar, NO responder
   - Usa preguntas orientadoras
   - Guía sin revelar la solución

3. **💭 Exigencia de Explicitación**
   - Fuerza a convertir pensamiento en palabras
   - Requiere plan ANTES de codear
   - Exige justificación de decisiones

4. **📚 Refuerzo Conceptual**
   - No da fixes sintácticos
   - Remite a conceptos teóricos
   - Enseña fundamentos, no parches

### 🚦 Sistema de Semáforos

| Estado | Condición | Acción |
|--------|-----------|--------|
| 🟢 VERDE | Bajo riesgo | Interacción normal |
| 🟡 AMARILLO | Alta dependencia IA (>0.7) | Reducir ayuda |
| 🔴 ROJO | Delegación total/Plagio | Solo preguntas |

### 📊 Trazabilidad N4

Registra automáticamente:
- Tipo de intervención
- Estado cognitivo
- Nivel de ayuda
- Eventos cognitivos detectados
- Efectividad de la intervención
- Progresión de autonomía

---

## 🎯 Ejemplos de Uso

### Ejemplo 1: Rechazo de Código Directo

```python
response = tutor.process_student_request(
    session_id="ses_1",
    student_prompt="Haceme el código de una pila",
    student_profile={"avg_ai_involvement": 0.5},
    conversation_history=[]
)

# Resultado:
# Semáforo: 🔴 ROJO
# Intervención: rechazo_pedagogico
# Mensaje: "No puedo darte el código directamente..."
```

### Ejemplo 2: Pregunta Socrática

```python
response = tutor.process_student_request(
    session_id="ses_2",
    student_prompt="¿Cómo funciona una cola?",
    student_profile={"avg_ai_involvement": 0.3},
    conversation_history=[]
)

# Resultado:
# Semáforo: 🟢 VERDE
# Intervención: pregunta_socratica
# Mensaje: "¿Qué entendés por cola? ¿Qué operaciones..."
```

### Ejemplo 3: Evaluación de Respuesta

```python
# Evaluar respuesta del estudiante
evaluation = tutor.evaluate_student_response_v2(
    session_id="ses_2",
    interaction_id=response["metadata"]["interaction_id"],
    student_response="Creo que es FIFO porque...",
    time_to_response_minutes=3.0
)

# Resultado:
# cognitive_events: ["formulacion_hipotesis", "justificacion_decision"]
# effectiveness: "efectiva"
```

### Ejemplo 4: Analytics N4

```python
# Obtener analytics de sesión
analytics = tutor.get_session_analytics_n4("ses_2")

print(f"Mejora en autonomía: {analytics['autonomy_improvement']}")
print(f"Eventos cognitivos: {analytics['cognitive_events_detected']}")
```

---

## 🧪 Testing

### Ejecutar Test Rápido
```bash
python test_tutor_socratico.py
```

### Ejecutar Ejemplos Completos
```bash
python examples/ejemplo_tutor_socratico_v2.py
```

---

## 📚 Documentación

### Documentación Completa
- [TUTOR_SOCRATICO_V2.md](docs/TUTOR_SOCRATICO_V2.md) - Guía detallada

### Resumen Ejecutivo
- [TUTOR_SOCRATICO_RESUMEN.md](TUTOR_SOCRATICO_RESUMEN.md) - Resumen de implementación

---

## 🏗️ Arquitectura

```
TutorCognitivoAgent
├── TutorRulesEngine          # 4 reglas inquebrantables
├── TutorGovernanceEngine      # IPC → GSR → Andamiaje
├── TutorMetadataTracker       # Trazabilidad N4
└── TutorSystemPrompts         # Prompts personalizados
```

### Componentes

- **tutor_rules.py** - Sistema de reglas pedagógicas
- **tutor_governance.py** - Gobernanza y semáforos
- **tutor_metadata.py** - Metadata y analytics N4
- **tutor_prompts.py** - System prompts
- **tutor.py** - Integración completa

---

## 🔧 Configuración Avanzada

### Ajustar Umbrales de Riesgo

```python
from backend.agents import TutorGovernanceEngine, TutorRulesEngine

rules = TutorRulesEngine()
governance = TutorGovernanceEngine(rules)

# Modificar umbrales
governance.risk_thresholds["high_ai_dependency"] = 0.8
governance.risk_thresholds["max_consecutive_requests"] = 3
```

### Personalizar Niveles de Ayuda

```python
from backend.agents import TutorCognitivoAgent

tutor = TutorCognitivoAgent(
    config={
        "policies": {
            "prioritize_questions": True,
            "require_justification": True,
            "adaptive_difficulty": True
        }
    }
)
```

---

## 📊 Tipos de Intervención

| Tipo | Cuándo | Ejemplo |
|------|--------|---------|
| Pregunta Socrática | Primera interacción | "¿Qué entendés por...?" |
| Rechazo Pedagógico | Solicitud de código | "No puedo darte..." |
| Pista Graduada | Estudiante trabado | Niveles 1-4 de ayuda |
| Corrección Conceptual | Error conceptual | "Este concepto establece..." |
| Exigencia Justificación | Sin razonamiento | "Explicá por qué..." |
| Remisión Teoría | Necesita fundamentos | "Revisá estos conceptos..." |

---

## 🎯 Niveles de Estudiante

### 🌱 Novato
- Balance: 60% guía, 40% exigencia
- Más explicaciones y ejemplos
- Tono paciente y educativo

### 📚 Intermedio
- Balance: 50% guía, 50% exigencia
- Preguntas más técnicas
- Asume conocimientos básicos

### 🚀 Avanzado
- Balance: 30% guía, 70% exigencia
- Rol de auditor crítico
- Cuestiona decisiones de diseño

---

## 🧠 Eventos Cognitivos Detectados

- `FORMULACION_HIPOTESIS` - "Creo que...", "Supongo..."
- `AUTOCORRECCION` - "Me equivoqué", "Ahora veo..."
- `DESCOMPOSICION_PROBLEMA` - "Primero...", "Luego..."
- `JUSTIFICACION_DECISION` - "Porque...", "Elegí esto..."
- `REFLEXION_METACOGNITIVA` - "Entiendo que...", "Me doy cuenta..."
- `PLANIFICACION` - "Voy a...", "Mi plan es..."
- `ABANDONO_DELEGACION` - Deja de pedir código directo

---

## ✅ Buenas Prácticas

### ✅ DO
- Usar `process_student_request()` como entrada principal
- Evaluar respuestas con `evaluate_student_response_v2()`
- Mantener perfil del estudiante actualizado
- Respetar el semáforo (no bypassear)

### ❌ DON'T
- No desactivar reglas en producción
- No ignorar semáforo rojo
- No dar código "comentado" (sigue violando regla)
- No aceptar respuestas sin justificación

---

## 🆘 Troubleshooting

### Problema: Tutor da demasiada ayuda
**Solución:** Verificar `student_profile.avg_ai_involvement`

### Problema: Semáforo siempre verde
**Solución:** Actualizar datos del perfil del estudiante

### Problema: No detecta eventos cognitivos
**Solución:** Respuestas deben tener >50 chars y palabras clave

---

## 📈 Métricas N4

```python
{
    "total_interventions": 8,
    "autonomy_improvement": 0.55,
    "cognitive_events_detected": {
        "justificacion_decision": 6,
        "autocorreccion": 2
    },
    "semaforo_states_distribution": {
        "verde": 6, "amarillo": 1, "rojo": 1
    }
}
```

---

## 🔗 Referencias

- Hutchins (1995) - Cognición Distribuida
- Clark & Chalmers (1998) - Cognición Extendida
- Sweller (1988) - Teoría de Carga Cognitiva
- Zimmerman (2002) - Autorregulación

---

**Versión:** 2.0  
**Estado:** ✅ Producción  
**Licencia:** Educativo
