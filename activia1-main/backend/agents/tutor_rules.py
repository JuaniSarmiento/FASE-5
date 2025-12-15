"""
Sistema de Reglas Pedagógicas del Tutor Socrático

Define las reglas inquebrantables que gobiernan el comportamiento del tutor IA.
Basado en principios de andamiaje cognitivo y pedagogía socrática.
"""
from typing import Dict, Any, List, Optional
from enum import Enum


class TutorRule(str, Enum):
    """Reglas pedagógicas inquebrantables del tutor"""
    ANTI_SOLUCION = "anti_solucion_directa"  # Prohibido dar código completo
    MODO_SOCRATICO = "modo_socratico_prioritario"  # Default: preguntar, no responder
    EXIGIR_EXPLICITACION = "exigir_explicitacion"  # Forzar conversión pensamiento->palabras
    REFUERZO_CONCEPTUAL = "refuerzo_conceptual"  # Ir a conceptos teóricos, no parches


class InterventionType(str, Enum):
    """Tipos de intervención pedagógica del tutor"""
    PREGUNTA_SOCRATICA = "pregunta_socratica"  # Pregunta orientadora
    RECHAZO_PEDAGOGICO = "rechazo_pedagogico"  # Rechazo de solicitud de código directo
    PISTA_GRADUADA = "pista_graduada"  # Pista conceptual sin solución
    CORRECCION_CONCEPTUAL = "correccion_conceptual"  # Explicación de concepto violado
    EXIGENCIA_JUSTIFICACION = "exigencia_justificacion"  # Pedir justificación
    EXIGENCIA_PSEUDOCODIGO = "exigencia_pseudocodigo"  # Pedir pseudocódigo/plan
    REMISION_TEORIA = "remision_teoria"  # Redirigir a concepto teórico


class CognitiveScaffoldingLevel(str, Enum):
    """Niveles de andamiaje cognitivo adaptativo"""
    NOVATO = "novato"  # Más explicaciones, ejemplos parciales
    INTERMEDIO = "intermedio"  # Balance entre guía y autonomía
    AVANZADO = "avanzado"  # Mínima ayuda, máxima exigencia crítica


class TutorRulesEngine:
    """
    Motor de reglas pedagógicas del tutor socrático
    
    Implementa las 4 reglas fundamentales:
    1. Regla del "Ni a Palos" (Anti-Solución Directa)
    2. Modo Socrático Prioritario
    3. Exigencia de Explicitación
    4. Refuerzo Conceptual
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Reglas activas (todas por default)
        self.active_rules = {
            TutorRule.ANTI_SOLUCION: True,
            TutorRule.MODO_SOCRATICO: True,
            TutorRule.EXIGIR_EXPLICITACION: True,
            TutorRule.REFUERZO_CONCEPTUAL: True,
        }
        
        # Umbrales de activación
        self.thresholds = {
            "min_student_level_for_code_hints": CognitiveScaffoldingLevel.AVANZADO,
            "max_consecutive_hints": 3,  # Máximo de pistas consecutivas sin justificación
            "min_explanation_length": 50,  # Mínimo de caracteres para justificación
        }
    
    def check_anti_solution_rule(
        self,
        student_request: str,
        student_level: CognitiveScaffoldingLevel
    ) -> Dict[str, Any]:
        """
        Regla #1: Anti-Solución Directa
        
        Bloquea solicitudes de código completo o soluciones finales.
        Solo permite en fases muy iniciales de diagnóstico.
        
        Returns:
            Dict con:
            - violated: bool (si se violó la regla)
            - action: str (acción a tomar)
            - message: str (mensaje para el estudiante)
        """
        if not self.active_rules[TutorRule.ANTI_SOLUCION]:
            return {"violated": False, "action": "allow"}
        
        # Detectar solicitudes de código directo
        code_request_patterns = [
            "haceme", "dame el código", "muéstrame el código",
            "escribe el código", "cual es el código",
            "resuelve esto", "solucioná", "hacé el ejercicio",
            "implementá", "codificá", "programá esto"
        ]
        
        request_lower = student_request.lower()
        is_code_request = any(pattern in request_lower for pattern in code_request_patterns)
        
        if is_code_request:
            return {
                "violated": True,
                "action": "reject_and_counter",
                "intervention_type": InterventionType.RECHAZO_PEDAGOGICO,
                "message": self._generate_rejection_message(student_level),
                "counter_question": self._generate_counter_question(student_request)
            }
        
        return {"violated": False, "action": "allow"}
    
    def check_socratic_priority_rule(
        self,
        conversation_context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Regla #2: Modo Socrático Prioritario
        
        El default es preguntar, no responder.
        Antes de dar cualquier explicación, debe hacer preguntas.
        
        Returns:
            Dict con recomendación de modo de respuesta
        """
        if not self.active_rules[TutorRule.MODO_SOCRATICO]:
            return {"should_question_first": False}
        
        # Analizar últimas interacciones
        recent_tutor_messages = [
            msg for msg in conversation_context[-5:]
            if msg.get("role") == "tutor"
        ]
        
        # Contar cuántas fueron preguntas vs explicaciones
        questions_count = sum(
            1 for msg in recent_tutor_messages
            if msg.get("type") == InterventionType.PREGUNTA_SOCRATICA
        )
        
        explanations_count = len(recent_tutor_messages) - questions_count
        
        # Si dio muchas explicaciones sin preguntar, forzar pregunta
        if explanations_count > 2 and questions_count == 0:
            return {
                "should_question_first": True,
                "reason": "too_many_explanations_without_questioning",
                "intervention_type": InterventionType.PREGUNTA_SOCRATICA
            }
        
        # Default: siempre priorizar preguntas en primera interacción
        if not recent_tutor_messages:
            return {
                "should_question_first": True,
                "reason": "first_interaction",
                "intervention_type": InterventionType.PREGUNTA_SOCRATICA
            }
        
        return {"should_question_first": False}
    
    def check_explicitacion_rule(
        self,
        student_message: str,
        conversation_context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Regla #3: Exigencia de Explicitación
        
        Fuerza al alumno a convertir su pensamiento en palabras.
        Debe pedir:
        - Plan antes de codear
        - Pseudocódigo
        - Justificación de decisiones
        
        Returns:
            Dict con:
            - needs_explicitacion: bool
            - type: str (plan, pseudocode, justification)
            - message: str
        """
        if not self.active_rules[TutorRule.EXIGIR_EXPLICITACION]:
            return {"needs_explicitacion": False}
        
        # Detectar si el estudiante dio una respuesta sin justificación
        has_justification = self._detect_justification(student_message)
        has_plan = self._detect_planning(student_message)
        
        # Verificar longitud de la explicación
        is_too_short = len(student_message.strip()) < self.thresholds["min_explanation_length"]
        
        # Verificar si ya se pidió explicitación antes
        last_tutor_msg = next(
            (msg for msg in reversed(conversation_context) if msg.get("role") == "tutor"),
            None
        )
        
        already_asked_explicitacion = (
            last_tutor_msg and
            last_tutor_msg.get("type") in [
                InterventionType.EXIGENCIA_JUSTIFICACION,
                InterventionType.EXIGENCIA_PSEUDOCODIGO
            ]
        )
        
        # Si ya pidió y sigue sin explicar, ser más enfático
        if already_asked_explicitacion and (not has_justification or is_too_short):
            return {
                "needs_explicitacion": True,
                "type": "justification_emphatic",
                "intervention_type": InterventionType.EXIGENCIA_JUSTIFICACION,
                "message": self._generate_emphatic_explicitacion_request(),
                "severity": "high"
            }
        
        # Primera solicitud de explicitación
        if not has_plan and not has_justification:
            return {
                "needs_explicitacion": True,
                "type": "plan_and_justification",
                "intervention_type": InterventionType.EXIGENCIA_PSEUDOCODIGO,
                "message": self._generate_explicitacion_request("plan"),
                "severity": "medium"
            }
        
        return {"needs_explicitacion": False}
    
    def check_conceptual_reinforcement_rule(
        self,
        error_detected: Optional[str],
        student_level: CognitiveScaffoldingLevel
    ) -> Dict[str, Any]:
        """
        Regla #4: Refuerzo Conceptual
        
        Cuando el alumno se equivoca, no dar el fix sintáctico,
        sino remitir al concepto teórico violado.
        
        Args:
            error_detected: Tipo de error detectado
            student_level: Nivel del estudiante
        
        Returns:
            Dict con concepto teórico a reforzar
        """
        if not self.active_rules[TutorRule.REFUERZO_CONCEPTUAL]:
            return {"needs_conceptual_reinforcement": False}
        
        if not error_detected:
            return {"needs_conceptual_reinforcement": False}
        
        # Mapeo de errores a conceptos teóricos
        error_to_concept = {
            "null_pointer": "invariantes_y_precondiciones",
            "array_bounds": "invariantes_de_estructura_de_datos",
            "tight_coupling": "acoplamiento_y_cohesion",
            "complexity_high": "complejidad_algoritmica",
            "memory_leak": "gestion_de_recursos",
            "race_condition": "concurrencia_y_sincronizacion",
            "duplicated_code": "principio_dry",
            "god_class": "single_responsibility_principle",
        }
        
        concept = error_to_concept.get(error_detected, "fundamentos_de_programacion")
        
        return {
            "needs_conceptual_reinforcement": True,
            "concept": concept,
            "intervention_type": InterventionType.REMISION_TEORIA,
            "message": self._generate_conceptual_reinforcement_message(concept),
            "explanation_level": self._get_explanation_depth(student_level)
        }
    
    def get_scaffolding_level(
        self,
        student_profile: Dict[str, Any]
    ) -> CognitiveScaffoldingLevel:
        """
        Determina el nivel de andamiaje cognitivo según perfil del estudiante
        
        Args:
            student_profile: Perfil con métricas del estudiante
        
        Returns:
            Nivel de andamiaje (novato, intermedio, avanzado)
        """
        # Métricas de autonomía
        avg_ai_involvement = student_profile.get("avg_ai_involvement", 0.5)
        successful_autonomous_solutions = student_profile.get("successful_autonomous_solutions", 0)
        error_self_correction_rate = student_profile.get("error_self_correction_rate", 0.0)
        
        # Clasificación por nivel
        if avg_ai_involvement > 0.7 or successful_autonomous_solutions < 3:
            return CognitiveScaffoldingLevel.NOVATO
        elif error_self_correction_rate > 0.6 and avg_ai_involvement < 0.4:
            return CognitiveScaffoldingLevel.AVANZADO
        else:
            return CognitiveScaffoldingLevel.INTERMEDIO
    
    # === Métodos auxiliares de detección ===
    
    def _detect_justification(self, text: str) -> bool:
        """Detecta si hay justificación en el texto"""
        justification_signals = [
            "porque", "ya que", "debido a", "considerando que",
            "mi razón es", "pensé que", "decidí", "elegí",
            "esto se debe", "la razón es"
        ]
        return any(signal in text.lower() for signal in justification_signals)
    
    def _detect_planning(self, text: str) -> bool:
        """Detecta si hay evidencia de planificación"""
        planning_signals = [
            "voy a", "planeo", "mi estrategia", "mi plan",
            "primero", "luego", "después", "paso",
            "mi enfoque", "mi idea es"
        ]
        return any(signal in text.lower() for signal in planning_signals)
    
    # === Generadores de mensajes ===
    
    def _generate_rejection_message(self, student_level: CognitiveScaffoldingLevel) -> str:
        """Genera mensaje de rechazo pedagógico"""
        if student_level == CognitiveScaffoldingLevel.NOVATO:
            return """
## 🚫 No puedo darte el código directamente

Entiendo que querés la solución rápida, pero **mi trabajo es ayudarte a aprender**, 
no a resolver el problema por vos.

Si te doy el código, no vas a desarrollar las habilidades que necesitás. 
En cambio, trabajemos juntos para que **vos llegues a la solución**.
"""
        else:
            return """
## 🚫 Solicitud Rechazada

Como tutor socrático, **no entrego código completo**. Mi función es guiar tu 
razonamiento, no sustituirlo.

Si necesitás ayuda, reformulá tu consulta explicando:
- ¿Qué intentaste?
- ¿Qué razonamiento seguiste?
- ¿Dónde te trabaste exactamente?
"""
    
    def _generate_counter_question(self, student_request: str) -> str:
        """Genera contra-pregunta después de un rechazo"""
        return """
## 💭 En vez de eso, respondeme:

1. **¿Qué entendés que tenés que resolver?** (Explicalo con tus palabras)
2. **¿Qué enfoque se te ocurre?** (No importa si no estás seguro)
3. **¿Qué conceptos o herramientas creés que son relevantes?**

Una vez que compartas tu razonamiento, puedo guiarte efectivamente.
"""
    
    def _generate_explicitacion_request(self, request_type: str) -> str:
        """Genera solicitud de explicitación"""
        if request_type == "plan":
            return """
## 📝 Antes de continuar: Explicá tu Plan

Para ayudarte efectivamente, necesito que **conviertas tu pensamiento en palabras**.

Por favor, escribí (en texto, no en código):
1. **Tu plan general**: ¿Qué pasos vas a seguir?
2. **Pseudocódigo de alto nivel**: Estructura básica de tu solución
3. **Justificación**: ¿Por qué elegiste este enfoque?

Esto no es burocracia: es una habilidad fundamental de programación.
"""
        else:
            return """
## 💭 Necesito que Justifiques tu Decisión

No alcanza con mostrar código o decir "creo que es así".

Explicá:
- ¿Por qué elegiste este enfoque?
- ¿Qué alternativas consideraste?
- ¿Qué ventajas/desventajas ves?

**La justificación es tan importante como la solución misma.**
"""
    
    def _generate_emphatic_explicitacion_request(self) -> str:
        """Genera solicitud enfática de explicitación (segunda vez)"""
        return """
## ⚠️ Explicitación Requerida

Ya te pedí que justifiques tu razonamiento, pero todavía no lo hiciste.

**No voy a poder ayudarte hasta que expliques tu pensamiento.** 

Esto no es capricho: estoy entrenado para fomentar tu autonomía cognitiva.
Si te doy pistas sin que vos razonés primero, estoy saboteando tu aprendizaje.

Por favor, tomá unos minutos y escribí:
1. Tu análisis del problema
2. Tu plan de acción
3. Por qué pensás que ese plan podría funcionar
"""
    
    def _generate_conceptual_reinforcement_message(self, concept: str) -> str:
        """Genera mensaje de refuerzo conceptual"""
        concept_explanations = {
            "invariantes_y_precondiciones": """
## 📚 Concepto Teórico: Invariantes y Precondiciones

El error que estás enfrentando está relacionado con **invariantes**.

**Invariante**: Una condición que siempre debe ser verdadera en cierto punto del programa.

**Precondición**: Lo que debe ser verdad ANTES de ejecutar una operación.

En tu caso:
- ¿Qué condición debe cumplirse antes de acceder a ese dato?
- ¿Cómo podrías garantizar esa condición?

📖 Leé sobre: "Design by Contract" y "Defensive Programming"
""",
            "acoplamiento_y_cohesion": """
## 📚 Concepto Teórico: Acoplamiento y Cohesión

Tu diseño tiene problemas de **acoplamiento**.

**Acoplamiento**: Grado de interdependencia entre módulos.
- **Alto** (malo): Cambiar un módulo rompe otros
- **Bajo** (bueno): Módulos independientes

**Cohesión**: Grado de relación entre elementos de un módulo.
- **Alta** (bueno): Todo en el módulo tiene un propósito común
- **Baja** (malo): Módulo hace cosas no relacionadas

¿Cómo afecta esto tu problema?

📖 Leé sobre: "Separation of Concerns" y "Single Responsibility Principle"
""",
            "complejidad_algoritmica": """
## 📚 Concepto Teórico: Complejidad Algorítmica

Tu solución tiene un problema de **complejidad**.

**Complejidad Temporal**: ¿Cuántas operaciones hace tu algoritmo?
- O(1): Constante
- O(n): Lineal
- O(n²): Cuadrática (problemática para n grande)

**Pregunta clave**: Si tus datos crecen 10x, ¿tu tiempo crece 10x o 100x?

En tu caso:
- ¿Cuántas veces estás iterando sobre los datos?
- ¿Hay operaciones repetidas que podrías evitar?

📖 Leé sobre: "Big O Notation" y "Algorithm Analysis"
"""
        }
        
        return concept_explanations.get(
            concept,
            f"## 📚 Concepto Teórico: {concept.replace('_', ' ').title()}\n\n"
            "Este error está relacionado con un concepto fundamental que necesitás revisar."
        )
    
    def _get_explanation_depth(self, student_level: CognitiveScaffoldingLevel) -> str:
        """Determina profundidad de explicación según nivel"""
        depth_map = {
            CognitiveScaffoldingLevel.NOVATO: "detailed_with_examples",
            CognitiveScaffoldingLevel.INTERMEDIO: "conceptual_with_hints",
            CognitiveScaffoldingLevel.AVANZADO: "minimal_conceptual_only"
        }
        return depth_map[student_level]
