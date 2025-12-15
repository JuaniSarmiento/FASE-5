"""
Sistema de Gobernanza y Procesamiento del Tutor Socrático

Implementa la lógica de "semáforos" y procesamiento inteligente:
1. IPC (Ingesta y Comprensión de Prompt)
2. GSR (Gobernanza y Gestión de Riesgo)
3. Selección de Estrategia de Andamiaje
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from .tutor_rules import (
    TutorRulesEngine,
    CognitiveScaffoldingLevel,
    InterventionType
)


class SemaforoState(str, Enum):
    """Estado del semáforo de riesgo"""
    VERDE = "verde"  # Bajo riesgo, permitir interacción normal
    AMARILLO = "amarillo"  # Riesgo medio, monitorear
    ROJO = "rojo"  # Riesgo alto, intervención restrictiva


class PromptIntent(str, Enum):
    """Intención detectada en el prompt del estudiante"""
    EXPLORACION = "exploracion"  # Está explorando el problema
    DEPURACION = "depuracion"  # Está debugueando código
    DELEGACION = "delegacion"  # Quiere que la IA resuelva todo
    CLARIFICACION = "clarificacion"  # Necesita entender conceptos
    VALIDACION = "validacion"  # Quiere validar su enfoque


class StudentContextAnalysis:
    """Análisis del contexto del estudiante"""
    
    def __init__(
        self,
        intent: PromptIntent,
        cognitive_state: str,
        autonomy_level: float,  # 0-1 (0=dependiente, 1=autónomo)
        risk_level: SemaforoState,
        student_level: CognitiveScaffoldingLevel
    ):
        self.intent = intent
        self.cognitive_state = cognitive_state
        self.autonomy_level = autonomy_level
        self.risk_level = risk_level
        self.student_level = student_level


class TutorGovernanceEngine:
    """
    Motor de Gobernanza del Tutor (Semáforos y Decisiones)
    
    Implementa 3 fases de procesamiento:
    1. Ingesta y Diagnóstico (IPC)
    2. Chequeo de Semáforo (GSR)
    3. Selección de Estrategia de Andamiaje
    """
    
    def __init__(self, rules_engine: TutorRulesEngine):
        self.rules_engine = rules_engine
        
        # Umbrales de riesgo
        self.risk_thresholds = {
            "high_ai_dependency": 0.7,  # Si AI involvement > 0.7 -> ROJO
            "plagiarism_keywords": [
                "generame", "escribí todo", "hace el proyecto",
                "dame la solución completa", "resolvelo vos"
            ],
            "max_consecutive_requests": 5  # Máx solicitudes sin autonomía
        }
    
    def process_student_request(
        self,
        student_prompt: str,
        student_profile: Dict[str, Any],
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Procesa request del estudiante siguiendo las 3 fases:
        
        1. IPC: Ingesta y Comprensión de Prompt
        2. GSR: Gobernanza y Semáforo de Riesgo
        3. Selección de Estrategia
        
        Returns:
            Dict con:
            - analysis: StudentContextAnalysis
            - semaforo: SemaforoState
            - strategy: Dict con estrategia de andamiaje
            - intervention: Dict con tipo de intervención recomendada
        """
        # FASE 1: IPC - Ingesta y Comprensión de Prompt
        ipc_analysis = self._ipc_ingesta_comprension(
            student_prompt,
            conversation_history
        )
        
        # FASE 2: GSR - Gobernanza y Semáforo de Riesgo
        gsr_result = self._gsr_gobernanza_semaforo(
            student_prompt,
            student_profile,
            conversation_history,
            ipc_analysis
        )
        
        # FASE 3: Selección de Estrategia de Andamiaje
        strategy = self._select_scaffolding_strategy(
            ipc_analysis,
            gsr_result,
            student_profile
        )
        
        return {
            "analysis": ipc_analysis,
            "semaforo": gsr_result["semaforo"],
            "risk_details": gsr_result,
            "strategy": strategy,
            "metadata": {
                "processing_pipeline": ["IPC", "GSR", "ANDAMIAJE"],
                "timestamp": self._get_timestamp()
            }
        }
    
    def _ipc_ingesta_comprension(
        self,
        student_prompt: str,
        conversation_history: List[Dict[str, Any]]
    ) -> StudentContextAnalysis:
        """
        FASE 1: IPC (Ingesta y Comprensión de Prompt)
        
        Analiza el prompt para detectar:
        - Intención (exploración, depuración, delegación, etc.)
        - Estado cognitivo
        - Nivel de autonomía demostrado
        
        Returns:
            StudentContextAnalysis con diagnóstico completo
        """
        # Detectar intención del prompt
        intent = self._detect_prompt_intent(student_prompt)
        
        # Detectar estado cognitivo
        cognitive_state = self._detect_cognitive_state(
            student_prompt,
            conversation_history
        )
        
        # Estimar nivel de autonomía
        autonomy_level = self._estimate_autonomy_level(
            student_prompt,
            conversation_history
        )
        
        # Nivel de andamiaje (provisional, se ajusta con GSR)
        student_level = self._estimate_student_level(
            autonomy_level,
            conversation_history
        )
        
        return StudentContextAnalysis(
            intent=intent,
            cognitive_state=cognitive_state,
            autonomy_level=autonomy_level,
            risk_level=SemaforoState.VERDE,  # Se determina en GSR
            student_level=student_level
        )
    
    def _gsr_gobernanza_semaforo(
        self,
        student_prompt: str,
        student_profile: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        ipc_analysis: StudentContextAnalysis
    ) -> Dict[str, Any]:
        """
        FASE 2: GSR (Gobernanza y Semáforo de Riesgo)
        
        Evalúa riesgos éticos y pedagógicos:
        - Riesgo de plagio (delegación total)
        - Riesgo de dependencia excesiva
        - Riesgo de bypassing del aprendizaje
        
        Returns:
            Dict con:
            - semaforo: SemaforoState (VERDE, AMARILLO, ROJO)
            - risk_type: str (tipo de riesgo detectado)
            - restrictions: List[str] (restricciones a aplicar)
        """
        semaforo = SemaforoState.VERDE
        risk_type = None
        restrictions = []
        
        # RIESGO 1: Solicitud de código completo (plagio potencial)
        if ipc_analysis.intent == PromptIntent.DELEGACION:
            semaforo = SemaforoState.ROJO
            risk_type = "delegacion_total"
            restrictions.append("block_code_generation")
            restrictions.append("require_justification")
        
        # RIESGO 2: Alta dependencia de IA (AI involvement alto)
        avg_ai_involvement = student_profile.get("avg_ai_involvement", 0.0)
        if avg_ai_involvement > self.risk_thresholds["high_ai_dependency"]:
            if semaforo == SemaforoState.VERDE:
                semaforo = SemaforoState.AMARILLO
            risk_type = "alta_dependencia_ia"
            restrictions.append("reduce_help_level")
            restrictions.append("increase_question_ratio")
        
        # RIESGO 3: Patrones de plagio en keywords
        plagiarism_detected = any(
            keyword in student_prompt.lower()
            for keyword in self.risk_thresholds["plagiarism_keywords"]
        )
        if plagiarism_detected:
            semaforo = SemaforoState.ROJO
            risk_type = "patron_plagio_detectado"
            restrictions.append("block_code_generation")
            restrictions.append("educative_warning")
        
        # RIESGO 4: Solicitudes consecutivas sin mostrar trabajo propio
        consecutive_requests = self._count_consecutive_requests_without_work(
            conversation_history
        )
        if consecutive_requests >= self.risk_thresholds["max_consecutive_requests"]:
            if semaforo != SemaforoState.ROJO:
                semaforo = SemaforoState.AMARILLO
            risk_type = "solicitudes_sin_trabajo_propio"
            restrictions.append("require_work_shown")
        
        return {
            "semaforo": semaforo,
            "risk_type": risk_type,
            "restrictions": restrictions,
            "should_warn": semaforo == SemaforoState.ROJO,
            "warning_message": self._generate_warning_message(semaforo, risk_type)
        }
    
    def _select_scaffolding_strategy(
        self,
        ipc_analysis: StudentContextAnalysis,
        gsr_result: Dict[str, Any],
        student_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        FASE 3: Selección de Estrategia de Andamiaje
        
        Basándose en IPC y GSR, decide:
        - Tipo de respuesta (socrática, explicativa, pistas)
        - Nivel de ayuda (mínimo, bajo, medio, alto)
        - Restricciones a aplicar
        
        Returns:
            Dict con estrategia de andamiaje completa
        """
        semaforo = gsr_result["semaforo"]
        restrictions = gsr_result["restrictions"]
        
        # Si semáforo ROJO, aplicar estrategia restrictiva
        if semaforo == SemaforoState.ROJO:
            return {
                "response_type": "socratic_questioning",
                "help_level": "minimo",
                "intervention_type": InterventionType.PREGUNTA_SOCRATICA,
                "allow_code": False,
                "allow_pseudocode": False,
                "require_student_work": True,
                "tone": "restrictive_educative",
                "restrictions": restrictions,
                "priority": "enforce_rules"
            }
        
        # Si semáforo AMARILLO, reducir ayuda
        if semaforo == SemaforoState.AMARILLO:
            return {
                "response_type": "guided_hints",
                "help_level": "bajo",
                "intervention_type": InterventionType.PISTA_GRADUADA,
                "allow_code": False,
                "allow_pseudocode": True,
                "require_justification": True,
                "tone": "supportive_but_firm",
                "restrictions": restrictions,
                "priority": "promote_autonomy"
            }
        
        # Semáforo VERDE - Estrategia según intención y nivel
        strategy_map = {
            PromptIntent.EXPLORACION: {
                "response_type": "socratic_questioning",
                "help_level": self._get_help_level_by_student_level(ipc_analysis.student_level),
                "intervention_type": InterventionType.PREGUNTA_SOCRATICA,
                "allow_pseudocode": True,
            },
            PromptIntent.DEPURACION: {
                "response_type": "guided_hints",
                "help_level": "medio",
                "intervention_type": InterventionType.PISTA_GRADUADA,
                "allow_pseudocode": True,
            },
            PromptIntent.CLARIFICACION: {
                "response_type": "conceptual_explanation",
                "help_level": "medio",
                "intervention_type": InterventionType.CORRECCION_CONCEPTUAL,
                "allow_pseudocode": True,
            },
            PromptIntent.VALIDACION: {
                "response_type": "socratic_questioning",
                "help_level": "bajo",
                "intervention_type": InterventionType.PREGUNTA_SOCRATICA,
                "allow_pseudocode": False,
            }
        }
        
        base_strategy = strategy_map.get(ipc_analysis.intent, {
            "response_type": "socratic_questioning",
            "help_level": "medio",
            "intervention_type": InterventionType.PREGUNTA_SOCRATICA,
        })
        
        # Añadir configuraciones generales
        base_strategy.update({
            "allow_code": False,  # NUNCA permitir código completo
            "require_justification": True,
            "tone": "supportive",
            "restrictions": restrictions,
            "priority": "learning_over_solving"
        })
        
        return base_strategy
    
    # === Métodos de Detección ===
    
    def _detect_prompt_intent(self, student_prompt: str) -> PromptIntent:
        """Detecta la intención del prompt del estudiante"""
        prompt_lower = student_prompt.lower()
        
        # Patrones de delegación
        delegation_patterns = [
            "haceme", "resolvé", "dame el código", "escribí el código",
            "solucioná", "implementá esto", "generá el código"
        ]
        if any(pattern in prompt_lower for pattern in delegation_patterns):
            return PromptIntent.DELEGACION
        
        # Patrones de depuración
        debug_patterns = [
            "no funciona", "error", "falla", "bug", "debuguear",
            "qué está mal", "por qué no", "no anda"
        ]
        if any(pattern in prompt_lower for pattern in debug_patterns):
            return PromptIntent.DEPURACION
        
        # Patrones de clarificación
        clarification_patterns = [
            "qué es", "cómo funciona", "explica", "no entiendo",
            "qué significa", "para qué sirve"
        ]
        if any(pattern in prompt_lower for pattern in clarification_patterns):
            return PromptIntent.CLARIFICACION
        
        # Patrones de validación
        validation_patterns = [
            "está bien", "es correcto", "funciona esto", "revisá",
            "qué te parece", "está ok"
        ]
        if any(pattern in prompt_lower for pattern in validation_patterns):
            return PromptIntent.VALIDACION
        
        # Default: exploración
        return PromptIntent.EXPLORACION
    
    def _detect_cognitive_state(
        self,
        student_prompt: str,
        conversation_history: List[Dict[str, Any]]
    ) -> str:
        """Detecta el estado cognitivo del estudiante"""
        # Simplificado: usar intención como proxy
        intent = self._detect_prompt_intent(student_prompt)
        
        state_map = {
            PromptIntent.EXPLORACION: "exploracion",
            PromptIntent.DEPURACION: "depuracion",
            PromptIntent.DELEGACION: "delegacion_critica",
            PromptIntent.CLARIFICACION: "confusion",
            PromptIntent.VALIDACION: "validacion_autonoma"
        }
        
        return state_map.get(intent, "exploracion")
    
    def _estimate_autonomy_level(
        self,
        student_prompt: str,
        conversation_history: List[Dict[str, Any]]
    ) -> float:
        """
        Estima nivel de autonomía del estudiante (0-1)
        
        Factores:
        - ¿Muestra trabajo propio?
        - ¿Explica su razonamiento?
        - ¿Hace preguntas específicas vs genéricas?
        """
        autonomy_score = 0.5  # Base
        
        # +0.2 si muestra código o pseudocódigo propio
        if "```" in student_prompt or "mi código" in student_prompt.lower():
            autonomy_score += 0.2
        
        # +0.2 si explica su razonamiento
        if any(word in student_prompt.lower() for word in ["porque", "pensé", "intenté"]):
            autonomy_score += 0.2
        
        # -0.3 si es una solicitud de delegación total
        if self._detect_prompt_intent(student_prompt) == PromptIntent.DELEGACION:
            autonomy_score -= 0.3
        
        # -0.2 si es muy corto (< 20 caracteres)
        if len(student_prompt.strip()) < 20:
            autonomy_score -= 0.2
        
        return max(0.0, min(1.0, autonomy_score))
    
    def _estimate_student_level(
        self,
        autonomy_level: float,
        conversation_history: List[Dict[str, Any]]
    ) -> CognitiveScaffoldingLevel:
        """Estima nivel de andamiaje basado en autonomía"""
        if autonomy_level < 0.3:
            return CognitiveScaffoldingLevel.NOVATO
        elif autonomy_level > 0.7:
            return CognitiveScaffoldingLevel.AVANZADO
        else:
            return CognitiveScaffoldingLevel.INTERMEDIO
    
    def _count_consecutive_requests_without_work(
        self,
        conversation_history: List[Dict[str, Any]]
    ) -> int:
        """Cuenta solicitudes consecutivas sin mostrar trabajo propio"""
        count = 0
        for msg in reversed(conversation_history[-10:]):  # Últimas 10 interacciones
            if msg.get("role") == "student":
                # Si no muestra código/pseudocódigo, cuenta como "sin trabajo"
                if "```" not in msg.get("content", ""):
                    count += 1
                else:
                    break  # Si mostró trabajo, resetear contador
        return count
    
    def _get_help_level_by_student_level(
        self,
        student_level: CognitiveScaffoldingLevel
    ) -> str:
        """Mapea nivel del estudiante a nivel de ayuda"""
        level_map = {
            CognitiveScaffoldingLevel.NOVATO: "medio",
            CognitiveScaffoldingLevel.INTERMEDIO: "bajo",
            CognitiveScaffoldingLevel.AVANZADO: "minimo"
        }
        return level_map[student_level]
    
    def _generate_warning_message(
        self,
        semaforo: SemaforoState,
        risk_type: Optional[str]
    ) -> Optional[str]:
        """Genera mensaje de advertencia según riesgo detectado"""
        if semaforo != SemaforoState.ROJO:
            return None
        
        warnings = {
            "delegacion_total": """
⚠️ **Advertencia Pedagógica**

Detecté que estás pidiendo que resuelva el problema completo por vos.

**Esto NO es ayuda, es sabotaje a tu aprendizaje.**

Como tutor IA, mi responsabilidad es guiar tu razonamiento, no sustituirlo.
Si te doy la solución directa, no vas a desarrollar las habilidades que necesitás.

Por favor, reformulá tu consulta explicando:
1. Qué intentaste hasta ahora
2. Dónde específicamente te trabaste
3. Qué pensás que podría funcionar
""",
            "patron_plagio_detectado": """
🚨 **Alerta Ética: Patrón de Plagio Detectado**

Tu solicitud viola las políticas académicas de integridad.

**No voy a generar código completo para proyectos o tareas.**

Si necesitás ayuda legítima:
- Mostrá tu trabajo actual
- Explicá tu razonamiento
- Hacé preguntas específicas sobre conceptos

El plagio académico tiene consecuencias serias.
""",
            "alta_dependencia_ia": """
⚠️ **Advertencia: Alta Dependencia de IA**

Tus métricas muestran dependencia excesiva de la IA para resolver problemas.

**Esto impacta negativamente tu aprendizaje.**

Por un tiempo, voy a reducir el nivel de ayuda directa para fomentar
tu autonomía. Vas a recibir más preguntas y menos respuestas.

**Objetivo**: Que desarrolles capacidad de resolver problemas por vos mismo.
"""
        }
        
        return warnings.get(risk_type, "⚠️ Advertencia: Riesgo pedagógico detectado")
    
    def _get_timestamp(self) -> str:
        """Retorna timestamp actual"""
        from datetime import datetime
        return datetime.now().isoformat()
