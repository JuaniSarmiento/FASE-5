# Tutor Socrático IA - Sistema de Reglas Pedagógicas V2.0

## 📚 Descripción General

El **Tutor Socrático V2.0** es una implementación completa de un agente pedagógico que opera bajo **reglas inquebrantables** diseñadas para maximizar el aprendizaje del estudiante y prevenir la dependencia excesiva de la IA.

### Principios Fundamentales

1. **"Ni a Palos"** - Anti-Solución Directa
2. **Modo Socrático Prioritario** - Preguntar antes que responder
3. **Exigencia de Explicitación** - Convertir pensamiento en palabras
4. **Refuerzo Conceptual** - Conceptos teóricos, no parches

---

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────────────────────────────────────────────┐
│                  TUTOR COGNITIVO V2.0                    │
└─────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
        ┌───────▼─────────┐    ┌───────▼─────────┐
        │ RULES ENGINE    │    │ GOVERNANCE      │
        │ (4 Reglas)      │    │ ENGINE          │
        └─────────────────┘    │ (IPC→GSR→AND)   │
                │              └─────────────────┘
                │                       │
        ┌───────▼─────────┐    ┌───────▼─────────┐
        │ METADATA        │    │ SYSTEM          │
        │ TRACKER (N4)    │    │ PROMPTS         │
        └─────────────────┘    └─────────────────┘
```

### 1. **TutorRulesEngine** - Motor de Reglas

Implementa las 4 reglas inquebrantables:

```python
from backend.agents import TutorRulesEngine, TutorRule

rules_engine = TutorRulesEngine()

# Regla 1: Anti-Solución Directa
result = rules_engine.check_anti_solution_rule(
    student_request="Haceme el código de una cola",
    student_level=CognitiveScaffoldingLevel.INTERMEDIO
)

if result["violated"]:
    print(result["rejection_message"])
    print(result["counter_question"])
```

### 2. **TutorGovernanceEngine** - Sistema de Semáforos

Procesa requests en 3 fases: **IPC → GSR → Andamiaje**

```python
from backend.agents import TutorGovernanceEngine

governance = TutorGovernanceEngine(rules_engine)

result = governance.process_student_request(
    student_prompt="No entiendo cómo funciona esto",
    student_profile={
        "avg_ai_involvement": 0.5,
        "successful_autonomous_solutions": 10
    },
    conversation_history=[]
)

# Resultado incluye:
# - analysis: StudentContextAnalysis (intención, estado cognitivo, autonomía)
# - semaforo: VERDE | AMARILLO | ROJO
# - strategy: Estrategia de andamiaje adaptativa
```

**Estados del Semáforo:**

| Semáforo | Condición | Acción |
|----------|-----------|--------|
| 🟢 VERDE | Bajo riesgo | Interacción normal |
| 🟡 AMARILLO | Riesgo medio (alta dependencia IA) | Reducir ayuda, más preguntas |
| 🔴 ROJO | Riesgo alto (delegación total, plagio) | Modo restrictivo, solo preguntas socráticas |

### 3. **TutorMetadataTracker** - Trazabilidad N4

Registra toda la metadata de intervenciones para análisis:

```python
from backend.agents import TutorMetadataTracker

tracker = TutorMetadataTracker()

# Registrar intervención
metadata = tracker.record_intervention(
    session_id="session_123",
    interaction_id="int_456",
    intervention_type=InterventionType.PREGUNTA_SOCRATICA,
    student_level=CognitiveScaffoldingLevel.INTERMEDIO,
    help_level="bajo",
    semaforo_state=SemaforoState.VERDE,
    cognitive_state="exploracion",
    student_intent="clarificacion",
    autonomy_level=0.6,
    rules_applied=["modo_socratico_prioritario"],
    restrictions_applied=[]
)

# Evaluar respuesta del estudiante
cognitive_events = tracker.detect_cognitive_events(
    student_response="Creo que debería usar un array porque...",
    previous_intervention=metadata
)

# Resultados N4
analytics = tracker.generate_n4_analytics("session_123")
```

**Eventos Cognitivos Detectados:**

- `FORMULACION_HIPOTESIS` - "Creo que...", "Supongo que..."
- `AUTOCORRECCION` - "Me equivoqué", "Ahora veo el error"
- `DESCOMPOSICION_PROBLEMA` - "Primero...", "Luego..."
- `JUSTIFICACION_DECISION` - "Porque...", "Elegí esto ya que..."
- `REFLEXION_METACOGNITIVA` - "Entiendo que...", "Me doy cuenta..."
- `PLANIFICACION` - "Voy a...", "Mi plan es..."
- `ABANDONO_DELEGACION` - Deja de pedir código directo

### 4. **TutorSystemPrompts** - Prompts Personalizados

Genera system prompts específicos por contexto:

```python
from backend.agents import TutorSystemPrompts

prompts = TutorSystemPrompts()

# Prompt base (reglas inquebrantables)
base_prompt = prompts.get_base_tutor_prompt()

# Prompt específico por intervención
intervention_prompt = prompts.get_intervention_prompt(
    intervention_type=InterventionType.RECHAZO_PEDAGOGICO,
    student_level=CognitiveScaffoldingLevel.NOVATO,
    semaforo_state=SemaforoState.ROJO,
    context={
        "risk_type": "delegacion_total",
        "restrictions": ["block_code_generation"]
    }
)
```

---

## 🚀 Uso del Sistema

### Ejemplo Completo

```python
from backend.agents import TutorCognitivoAgent

# Inicializar tutor
tutor = TutorCognitivoAgent(
    llm_provider=None,  # Opcional: integrar con LLM
    config={
        "policies": {
            "prioritize_questions": True,
            "require_justification": True
        }
    }
)

# Procesar request del estudiante
response = tutor.process_student_request(
    session_id="ses_123",
    student_prompt="Haceme el código de una cola con arreglos",
    student_profile={
        "avg_ai_involvement": 0.4,
        "successful_autonomous_solutions": 5,
        "error_self_correction_rate": 0.3
    },
    conversation_history=[]
)

print(response["message"])
print(f"Semáforo: {response['semaforo']}")
print(f"Tipo de intervención: {response['intervention_type']}")

# Evaluar respuesta posterior del estudiante
evaluation = tutor.evaluate_student_response_v2(
    session_id="ses_123",
    interaction_id=response["metadata"]["interaction_id"],
    student_response="Ok, entiendo. Mi idea es usar un array...",
    time_to_response_minutes=5.0
)

print(f"Eventos cognitivos: {evaluation['cognitive_events']}")
print(f"Efectividad: {evaluation['effectiveness']}")

# Obtener analytics N4
analytics = tutor.get_session_analytics_n4("ses_123")
print(f"Mejora en autonomía: {analytics['autonomy_improvement']}")
```

---

## 📊 Tipos de Intervención

### 1. Pregunta Socrática

**Cuándo:** Primera interacción, exploración, validación

**Ejemplo:**
```
❓ Para guiarte efectivamente, necesito comprender tu proceso de pensamiento.

1. ¿Qué entendés que tenés que resolver en este problema?
2. ¿Qué conceptos o estructuras de datos considerás relevantes?
3. ¿Podés describir con tus palabras cómo funcionaría una solución?
```

### 2. Rechazo Pedagógico

**Cuándo:** Solicitud de código directo

**Ejemplo:**
```
🚫 No puedo darte el código directamente

Mi función es guiar tu razonamiento, no sustituirlo.

💭 En vez de eso, respondeme:
1. ¿Qué entendés que tenés que resolver?
2. ¿Qué enfoque se te ocurre?
3. ¿Qué conceptos creés que son relevantes?
```

### 3. Pista Graduada

**Cuándo:** Estudiante genuinamente trabado, necesita orientación

**Niveles:**
- **Mínimo:** Solo preguntas orientadoras
- **Bajo:** Pistas conceptuales generales
- **Medio:** Pseudocódigo alto nivel
- **Alto:** Estrategia detallada (sin código)

### 4. Corrección Conceptual

**Cuándo:** Error conceptual detectado

**Ejemplo:**
```
📚 Concepto Teórico: Invariantes y Precondiciones

El error que estás enfrentando está relacionado con **invariantes**.

**Invariante**: Condición que siempre debe ser verdadera.

En tu caso:
- ¿Qué condición debe cumplirse antes de acceder a ese dato?
- ¿Cómo podrías garantizar esa condición?
```

### 5. Exigencia de Justificación

**Cuándo:** Respuesta sin razonamiento explicitado

**Ejemplo:**
```
💭 Necesito que Justifiques tu Decisión

No alcanza con mostrar código o decir "creo que es así".

Explicá:
- ¿Por qué elegiste este enfoque?
- ¿Qué alternativas consideraste?
- ¿Qué ventajas/desventajas ves?
```

---

## 🎯 Niveles de Andamiaje

### Novato 🌱

- **Características:** Poca experiencia, necesita más contexto
- **Adaptación:** Más explicativo, ejemplos simples
- **Balance:** 60% guía, 40% exigencia

### Intermedio 📚

- **Características:** Conocimientos básicos, puede resolver problemas simples
- **Adaptación:** Balance entre guía y autonomía
- **Balance:** 50% guía, 50% exigencia

### Avanzado 🚀

- **Características:** Experiencia significativa, necesita desafíos
- **Adaptación:** Rol de auditor crítico, mínima ayuda
- **Balance:** 30% guía, 70% exigencia

---

## 📈 Métricas N4 Generadas

El sistema registra automáticamente:

```python
{
    "session_id": "ses_123",
    "total_interventions": 8,
    "intervention_types_distribution": {
        "pregunta_socratica": 5,
        "pista_graduada": 2,
        "rechazo_pedagogico": 1
    },
    "effectiveness_distribution": {
        "muy_efectiva": 3,
        "efectiva": 4,
        "neutra": 1
    },
    "cognitive_events_detected": {
        "justificacion_decision": 6,
        "descomposicion_problema": 3,
        "autocorreccion": 2
    },
    "semaforo_states_distribution": {
        "verde": 6,
        "amarillo": 1,
        "rojo": 1
    },
    "autonomy_progression": [0.3, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85],
    "autonomy_improvement": 0.55,
    "avg_help_level": 0.6
}
```

---

## 🔧 Configuración Avanzada

### Ajustar Umbrales de Riesgo

```python
from backend.agents import TutorGovernanceEngine, TutorRulesEngine

rules = TutorRulesEngine()
governance = TutorGovernanceEngine(rules)

# Modificar umbrales
governance.risk_thresholds["high_ai_dependency"] = 0.8  # Más permisivo
governance.risk_thresholds["max_consecutive_requests"] = 3  # Más estricto
```

### Desactivar Reglas Específicas (NO RECOMENDADO)

```python
rules = TutorRulesEngine()

# Desactivar regla (solo para testing)
rules.active_rules[TutorRule.ANTI_SOLUCION] = False
```

---

## ✅ Buenas Prácticas

### ✅ DO

- Usar `process_student_request()` como punto de entrada principal
- Evaluar respuestas con `evaluate_student_response_v2()`
- Registrar todas las interacciones para análisis N4
- Mantener perfil del estudiante actualizado
- Respetar el semáforo (no bypasear restricciones)

### ❌ DON'T

- No desactivar reglas en producción
- No ignorar el semáforo rojo
- No dar código completo "comentado" (sigue violando la regla)
- No aceptar respuestas sin justificación
- No saltar directamente a pseudocódigo sin preguntas previas

---

## 🧪 Testing

### Ejemplo de Test

```python
def test_anti_solution_rule():
    tutor = TutorCognitivoAgent()
    
    response = tutor.process_student_request(
        session_id="test_ses",
        student_prompt="Haceme el código completo",
        student_profile={"avg_ai_involvement": 0.5},
        conversation_history=[]
    )
    
    # Debe rechazar
    assert response["semaforo"] == "rojo"
    assert "no puedo" in response["message"].lower()
    assert response["intervention_type"] == "rechazo_pedagogico"

def test_socratic_questioning():
    tutor = TutorCognitivoAgent()
    
    response = tutor.process_student_request(
        session_id="test_ses",
        student_prompt="No entiendo este problema",
        student_profile={"avg_ai_involvement": 0.3},
        conversation_history=[]
    )
    
    # Debe hacer preguntas
    assert "?" in response["message"]
    assert response["intervention_type"] == "pregunta_socratica"
```

---

## 📚 Referencias Teóricas

El sistema se basa en:

- **Hutchins (1995)** - Cognición Distribuida
- **Clark & Chalmers (1998)** - Cognición Extendida
- **Sweller (1988)** - Teoría de Carga Cognitiva
- **Zimmerman (2002)** - Autorregulación del Aprendizaje
- **Bloom (1984)** - Problema 2-Sigma (Tutoring 1-a-1)

---

## 🆘 Troubleshooting

### Problema: El tutor da demasiada ayuda

**Solución:** Revisar `student_profile.avg_ai_involvement` - si es alto, el semáforo debería activarse.

### Problema: Semáforo siempre en verde

**Solución:** Verificar que `student_profile` tenga datos actualizados de AI involvement.

### Problema: No detecta eventos cognitivos

**Solución:** Asegurar que las respuestas del estudiante tengan suficiente longitud (>50 chars) y palabras clave como "porque", "creo que", etc.

---

## 📝 Roadmap

### Futuras Mejoras

- [ ] Integración directa con LLM para generación dinámica
- [ ] Detección automática de patrones de plagio más sofisticada
- [ ] Dashboard visual de analytics N4
- [ ] Sistema de recomendaciones adaptativo basado en historial
- [ ] Multilenguaje (inglés, portugués)

---

**Versión:** 2.0  
**Última actualización:** Diciembre 2025  
**Autor:** Sistema AI-Native Educativo
