"""
Submodelo 1: Tutor IA Disciplinar Cognitivo (T-IA-Cog)

Agente de andamiaje cognitivo y metacognitivo que amplifica capacidades
del estudiante sin sustituirlas, operando bajo reglas pedagógicas y éticas explícitas.

VERSIÓN 2.0 - TUTOR SOCRÁTICO PERSONALIZADO
Incorpora:
1. Reglas inquebrantables (Anti-Solución, Socrático, Explicitación, Refuerzo Conceptual)
2. Sistema de gobernanza con semáforos (Verde/Amarillo/Rojo)
3. Procesamiento IPC -> GSR -> Andamiaje
4. Metadata completa para análisis N4
"""
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)

from ..models.trace import CognitiveTrace, TraceLevel, InteractionType
from .tutor_rules import (
    TutorRulesEngine,
    TutorRule,
    InterventionType as TutorInterventionType,
    CognitiveScaffoldingLevel
)
from .tutor_governance import (
    TutorGovernanceEngine,
    SemaforoState,
    PromptIntent
)
from .tutor_metadata import (
    TutorMetadataTracker,
    TutorInterventionMetadata,
    StudentCognitiveEvent
)
from .tutor_prompts import TutorSystemPrompts


class TutorMode(str, Enum):
    """Modos de tutoría"""
    SOCRATICO = "socratico"  # Preguntas socráticas
    EXPLICATIVO = "explicativo"  # Explicaciones conceptuales
    GUIADO = "guiado"  # Pistas graduadas
    METACOGNITIVO = "metacognitivo"  # Reflexión sobre el proceso


class HelpLevel(str, Enum):
    """Niveles de ayuda"""
    MINIMO = "minimo"  # Solo preguntas orientadoras
    BAJO = "bajo"  # Pistas muy generales
    MEDIO = "medio"  # Pistas con algo de detalle
    ALTO = "alto"  # Explicaciones detalladas (sin código completo)


class TutorCognitivoAgent:
    """
    T-IA-Cog: Tutor IA Disciplinar Cognitivo (VERSIÓN 2.0 - Socrático)

    Funciones principales:
    1. Guiar el razonamiento (NO proveer soluciones - REGLA INQUEBRANTABLE)
    2. Promover la explicitación del pensamiento (forzar justificación)
    3. Prevenir delegación acrítica (sistema de semáforos)
    4. Reforzar fundamentos conceptuales (no parches sintácticos)
    5. Escalar dificultad cognitiva adaptativamente (por nivel)

    NUEVOS COMPONENTES V2.0:
    - TutorRulesEngine: Aplica las 4 reglas inquebrantables
    - TutorGovernanceEngine: Procesa IPC -> GSR -> Andamiaje
    - TutorMetadataTracker: Registra metadata para análisis N4
    - TutorSystemPrompts: System prompts personalizados por contexto

    Basado en:
    - Cognición distribuida (Hutchins, 1995)
    - Cognición extendida (Clark & Chalmers, 1998)
    - Teoría de carga cognitiva (Sweller, 1988)
    - Autorregulación (Zimmerman, 2002)
    """

    def __init__(self, llm_provider=None, config: Optional[Dict[str, Any]] = None):
        self.llm_provider = llm_provider
        self.config = config or {}
        
        # Log LLM provider status
        if llm_provider:
            logger.info(f"TutorCognitivoAgent initialized with LLM provider: {type(llm_provider).__name__}")
        else:
            logger.warning("TutorCognitivoAgent initialized WITHOUT LLM provider - will use templates")
        
        # Componentes V2.0
        self.rules_engine = TutorRulesEngine(config)
        self.governance_engine = TutorGovernanceEngine(self.rules_engine)
        self.metadata_tracker = TutorMetadataTracker()
        self.prompts = TutorSystemPrompts()
        
        # Políticas pedagógicas (legacy - mantenidas por compatibilidad)
        self.policies = {
            "prioritize_questions": True,
            "require_justification": True,
            "adaptive_difficulty": True,
            "max_help_level": HelpLevel.MEDIO,
            "block_complete_solutions": True,
        }

        # Actualizar con config
        if config:
            self.policies.update(config.get("policies", {}))
    
    async def process_student_request(
        self,
        session_id: str,
        student_prompt: str,
        student_profile: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        MÉTODO PRINCIPAL V2.0: Procesa request del estudiante con pipeline completo
        
        Pipeline:
        1. IPC (Ingesta y Comprensión de Prompt)
        2. GSR (Gobernanza y Semáforo de Riesgo)
        3. Selección de Estrategia de Andamiaje
        4. Chequeo de Reglas Pedagógicas
        5. Generación de Respuesta
        6. Registro de Metadata para N4
        
        Args:
            session_id: ID de la sesión
            student_prompt: Pregunta/solicitud del estudiante
            student_profile: Perfil del estudiante con métricas
            conversation_history: Historial de la conversación
        
        Returns:
            Dict con:
            - message: Respuesta del tutor
            - intervention_type: Tipo de intervención
            - metadata: Metadata completa para N4
            - semaforo: Estado del semáforo
        """
        conversation_history = conversation_history or []
        interaction_id = str(uuid.uuid4())
        
        # FASE 1-3: Procesamiento por Gobernanza (IPC -> GSR -> Andamiaje)
        governance_result = self.governance_engine.process_student_request(
            student_prompt=student_prompt,
            student_profile=student_profile,
            conversation_history=conversation_history
        )
        
        analysis = governance_result["analysis"]
        semaforo = governance_result["semaforo"]
        strategy = governance_result["strategy"]
        risk_details = governance_result["risk_details"]
        
        # FASE 4: Chequeo de Reglas Pedagógicas
        rules_violations = self._check_pedagogical_rules(
            student_prompt=student_prompt,
            student_level=analysis.student_level,
            conversation_history=conversation_history,
            strategy=strategy
        )
        
        # Si hay violaciones críticas (ej: solicitud de código), aplicar regla
        if rules_violations.get("critical_violation"):
            # Aplicar intervención de rechazo pedagógico
            intervention_type = TutorInterventionType.RECHAZO_PEDAGOGICO
            message = rules_violations.get("rejection_message")
            counter_question = rules_violations.get("counter_question")
            
            response = {
                "message": f"{message}\n\n{counter_question}",
                "intervention_type": intervention_type.value,
                "semaforo": semaforo.value,
                "requires_student_response": True,
                "metadata": self._build_metadata(
                    interaction_id,
                    session_id,
                    intervention_type,
                    analysis,
                    semaforo,
                    strategy,
                    rules_violations.get("rules_applied", [])
                )
            }
        else:
            # FASE 5: Generación de Respuesta Normal
            response = await self._generate_tutor_response(
                interaction_id=interaction_id,
                session_id=session_id,
                student_prompt=student_prompt,
                strategy=strategy,
                analysis=analysis,
                semaforo=semaforo,
                risk_details=risk_details
            )
        
        # FASE 6: Registrar Metadata para N4
        self.metadata_tracker.record_intervention(
            session_id=session_id,
            interaction_id=interaction_id,
            intervention_type=response.get("intervention_type"),
            student_level=analysis.student_level,
            help_level=strategy.get("help_level", "medio"),
            semaforo_state=semaforo,
            cognitive_state=analysis.cognitive_state,
            student_intent=analysis.intent.value,
            autonomy_level=analysis.autonomy_level,
            rules_applied=rules_violations.get("rules_applied", []),
            restrictions_applied=risk_details.get("restrictions", []),
            additional_metadata=response.get("metadata", {})
        )
        
        return response
    
    def _check_pedagogical_rules(
        self,
        student_prompt: str,
        student_level: CognitiveScaffoldingLevel,
        conversation_history: List[Dict[str, Any]],
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Chequea las reglas pedagógicas inquebrantables
        
        Returns:
            Dict con:
            - critical_violation: bool
            - rules_applied: List[str]
            - rejection_message: str (si aplica)
            - counter_question: str (si aplica)
        """
        violations = {
            "critical_violation": False,
            "rules_applied": [],
        }
        
        # Regla #1: Anti-Solución Directa
        anti_solution_result = self.rules_engine.check_anti_solution_rule(
            student_request=student_prompt,
            student_level=student_level
        )
        
        if anti_solution_result.get("violated"):
            violations["critical_violation"] = True
            violations["rules_applied"].append(TutorRule.ANTI_SOLUCION.value)
            violations["rejection_message"] = anti_solution_result.get("message")
            violations["counter_question"] = anti_solution_result.get("counter_question")
            return violations  # Retornar inmediatamente
        
        # Regla #2: Modo Socrático Prioritario
        socratic_result = self.rules_engine.check_socratic_priority_rule(
            conversation_context=conversation_history
        )
        
        if socratic_result.get("should_question_first"):
            violations["rules_applied"].append(TutorRule.MODO_SOCRATICO.value)
            strategy["force_socratic"] = True
        
        # Regla #3: Exigencia de Explicitación
        explicitacion_result = self.rules_engine.check_explicitacion_rule(
            student_message=student_prompt,
            conversation_context=conversation_history
        )
        
        if explicitacion_result.get("needs_explicitacion"):
            violations["rules_applied"].append(TutorRule.EXIGIR_EXPLICITACION.value)
            strategy["require_justification"] = True
            strategy["explicitacion_message"] = explicitacion_result.get("message")
        
        return violations
    
    async def _generate_tutor_response(
        self,
        interaction_id: str,
        session_id: str,
        student_prompt: str,
        strategy: Dict[str, Any],
        analysis: Any,  # StudentContextAnalysis
        semaforo: SemaforoState,
        risk_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera respuesta del tutor según estrategia y contexto
        
        Usa system prompts personalizados para garantizar cumplimiento de reglas.
        """
        intervention_type = strategy.get("intervention_type", TutorInterventionType.PREGUNTA_SOCRATICA)
        
        # Generar system prompt personalizado
        system_prompt = self.prompts.get_intervention_prompt(
            intervention_type=intervention_type,
            student_level=analysis.student_level,
            semaforo_state=semaforo,
            context={
                "risk_type": risk_details.get("risk_type"),
                "restrictions": risk_details.get("restrictions", []),
                "student_intent": analysis.intent.value,
                "cognitive_state": analysis.cognitive_state
            }
        )
        
        # Si hay mensaje de advertencia (semáforo rojo), incluirlo
        warning_message = risk_details.get("warning_message")
        
        # ✅ NUEVO: Si hay LLM provider, usar respuesta dinámica con memoria de conversación
        if self.llm_provider and hasattr(self.llm_provider, 'generate'):
            try:
                # Recuperar historial de conversación (ya cargado en guide())
                conversation_history = strategy.get("conversation_history", [])
                
                # Agregar el prompt actual al historial
                messages = conversation_history + [
                    {"role": "user", "content": student_prompt}
                ]
                
                # Generar respuesta con contexto completo
                llm_response = await self.llm_provider.generate(
                    messages=messages,
                    system_prompt=system_prompt,
                    temperature=0.7,
                    max_tokens=500
                )
                
                legacy_response = {
                    "message": llm_response,
                    "requires_student_response": True
                }
                
            except Exception as e:
                logger.warning(f"LLM generation failed, using fallback: {e}")
                # Fallback a método legacy
                response_type = strategy.get("response_type", "socratic_questioning")
                if response_type == "socratic_questioning":
                    legacy_response = await self._generate_socratic_response(
                        student_prompt, analysis.cognitive_state, strategy
                    )
                elif response_type == "conceptual_explanation":
                    legacy_response = await self._generate_conceptual_explanation(
                        student_prompt, analysis.cognitive_state, strategy
                    )
                elif response_type == "guided_hints":
                    legacy_response = await self._generate_guided_hints(
                        student_prompt, analysis.cognitive_state, strategy, None
                    )
                else:
                    legacy_response = self._generate_clarification_request(
                        student_prompt, analysis.cognitive_state
                    )
        else:
            # Sin LLM provider, usar método legacy
            response_type = strategy.get("response_type", "socratic_questioning")

            if response_type == "socratic_questioning":
                legacy_response = await self._generate_socratic_response(
                    student_prompt, analysis.cognitive_state, strategy
                )
            elif response_type == "conceptual_explanation":
                legacy_response = await self._generate_conceptual_explanation(
                    student_prompt, analysis.cognitive_state, strategy
                )
            elif response_type == "guided_hints":
                legacy_response = await self._generate_guided_hints(
                    student_prompt, analysis.cognitive_state, strategy, None
                )
            else:
                legacy_response = self._generate_clarification_request(
                    student_prompt, analysis.cognitive_state
                )
        
        # Combinar warning si existe
        final_message = legacy_response["message"]
        if warning_message:
            final_message = f"{warning_message}\n\n---\n\n{final_message}"
        
        response_dict = {
            "message": final_message,
            "intervention_type": intervention_type.value if hasattr(intervention_type, 'value') else intervention_type,
            "semaforo": semaforo.value,
            "help_level": strategy.get("help_level"),
            "requires_student_response": legacy_response.get("requires_student_response", True),
            "system_prompt_used": system_prompt,  # Para logging/debugging
            "metadata": self._build_metadata(
                interaction_id,
                session_id,
                intervention_type,
                analysis,
                semaforo,
                strategy,
                []
            )
        }
        
        # Guardar la respuesta del tutor en metadata para historial
        response_dict["metadata"]["tutor_response"] = final_message
        
        return response_dict
    
    def _build_metadata(
        self,
        interaction_id: str,
        session_id: str,
        intervention_type: Any,
        analysis: Any,
        semaforo: SemaforoState,
        strategy: Dict[str, Any],
        rules_applied: List[str]
    ) -> Dict[str, Any]:
        """Construye metadata completa para N4"""
        return {
            "interaction_id": interaction_id,
            "session_id": session_id,
            "intervention_type": intervention_type.value if hasattr(intervention_type, 'value') else intervention_type,
            "student_level": analysis.student_level.value if hasattr(analysis, 'student_level') else "intermedio",
            "student_intent": analysis.intent.value if hasattr(analysis, 'intent') else "exploracion",
            "cognitive_state": analysis.cognitive_state if hasattr(analysis, 'cognitive_state') else "exploracion",
            "autonomy_level": analysis.autonomy_level if hasattr(analysis, 'autonomy_level') else 0.5,
            "semaforo": semaforo.value,
            "help_level": strategy.get("help_level", "medio"),
            "rules_applied": rules_applied,
            "restrictions": strategy.get("restrictions", []),
            "allow_code": strategy.get("allow_code", False),
            "allow_pseudocode": strategy.get("allow_pseudocode", True),
            "require_justification": strategy.get("require_justification", True)
        }
    
    def evaluate_student_response_v2(
        self,
        session_id: str,
        interaction_id: str,
        student_response: str,
        time_to_response_minutes: float
    ) -> Dict[str, Any]:
        """
        NUEVO V2.0: Evalúa respuesta del estudiante y actualiza metadata
        
        Args:
            session_id: ID de la sesión
            interaction_id: ID de la intervención a evaluar
            student_response: Respuesta del estudiante
            time_to_response_minutes: Tiempo en minutos
        
        Returns:
            Dict con análisis de la respuesta
        """
        # Buscar la intervención en el historial
        intervention = None
        for i in self.metadata_tracker.intervention_history:
            if i.interaction_id == interaction_id:
                intervention = i
                break
        
        if not intervention:
            return {"error": "Intervention not found"}
        
        # Detectar eventos cognitivos
        cognitive_events = self.metadata_tracker.detect_cognitive_events(
            student_response=student_response,
            previous_intervention=intervention
        )
        
        # Evaluar efectividad
        effectiveness = self.metadata_tracker.evaluate_intervention_effectiveness(
            intervention=intervention,
            student_response=student_response,
            cognitive_events=cognitive_events,
            time_to_response_minutes=time_to_response_minutes
        )
        
        # Actualizar metadata
        self.metadata_tracker.update_intervention_effectiveness(
            interaction_id=interaction_id,
            effectiveness=effectiveness,
            cognitive_events=cognitive_events
        )
        
        return {
            "cognitive_events": [e.value for e in cognitive_events],
            "effectiveness": effectiveness.value,
            "analysis": self.evaluate_student_response(student_response, {}),  # Legacy
            "should_adjust_strategy": self._should_adjust_strategy(
                effectiveness, cognitive_events
            )
        }
    
    def _should_adjust_strategy(
        self,
        effectiveness: Any,
        cognitive_events: List[StudentCognitiveEvent]
    ) -> Dict[str, Any]:
        """Determina si se debe ajustar la estrategia pedagógica"""
        from .tutor_metadata import InterventionEffectiveness
        
        # Si la intervención fue muy efectiva, mantener nivel
        if effectiveness == InterventionEffectiveness.MUY_EFECTIVA:
            return {"adjust": False, "reason": "highly_effective"}
        
        # Si fue contraproducente, reducir complejidad
        if effectiveness == InterventionEffectiveness.CONTRAPRODUCENTE:
            return {
                "adjust": True,
                "direction": "simplify",
                "reason": "counterproductive_intervention"
            }
        
        # Si no hay eventos cognitivos positivos, incrementar guía
        positive_events = [
            StudentCognitiveEvent.AUTOCORRECCION,
            StudentCognitiveEvent.REFLEXION_METACOGNITIVA,
            StudentCognitiveEvent.JUSTIFICACION_DECISION
        ]
        
        if not any(event in cognitive_events for event in positive_events):
            return {
                "adjust": True,
                "direction": "increase_guidance",
                "reason": "lack_of_cognitive_events"
            }
        
        return {"adjust": False, "reason": "adequate_effectiveness"}
    
    def get_session_analytics_n4(self, session_id: str) -> Dict[str, Any]:
        """
        NUEVO V2.0: Obtiene analytics N4 de una sesión
        
        Args:
            session_id: ID de la sesión
        
        Returns:
            Métricas agregadas para análisis N4
        """
        return self.metadata_tracker.generate_n4_analytics(session_id)

        # Políticas pedagógicas
        self.policies = {
            "prioritize_questions": True,
            "require_justification": True,
            "adaptive_difficulty": True,
            "max_help_level": HelpLevel.MEDIO,
            "block_complete_solutions": True,
        }

        # Actualizar con config
        if config:
            self.policies.update(config.get("policies", {}))

    def generate_response(
        self,
        student_prompt: str,
        cognitive_state: str,
        strategy: Dict[str, Any],
        student_history: Optional[List[CognitiveTrace]] = None
    ) -> Dict[str, Any]:
        """
        Genera respuesta tutorial basada en principios pedagógicos

        Args:
            student_prompt: Pregunta/solicitud del estudiante
            cognitive_state: Estado cognitivo actual
            strategy: Estrategia pedagógica definida por CRPE
            student_history: Historial de interacciones

        Returns:
            Diccionario con respuesta y metadata pedagógica
        """
        response_type = strategy.get("response_type", "socratic_questioning")

        if response_type == "socratic_questioning":
            return self._generate_socratic_response(
                student_prompt, cognitive_state, strategy
            )
        elif response_type == "conceptual_explanation":
            return self._generate_conceptual_explanation(
                student_prompt, cognitive_state, strategy
            )
        elif response_type == "guided_hints":
            return self._generate_guided_hints(
                student_prompt, cognitive_state, strategy, student_history
            )
        else:
            return self._generate_clarification_request(
                student_prompt, cognitive_state
            )

    async def _generate_socratic_response(
        self,
        prompt: str,
        cognitive_state: str,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera respuesta socrática con preguntas que guían el razonamiento

        Usa LLM si está disponible, sino usa plantillas predefinidas.
        """
        # Si hay LLM provider, generar respuesta con IA
        if self.llm_provider:
            try:
                logger.info(f"Attempting to generate Socratic response with LLM for prompt: {prompt[:50]}...")
                return await self._generate_socratic_with_llm(prompt, cognitive_state, strategy)
            except Exception as e:
                # Fallback a plantillas si falla el LLM
                logger.error(f"LLM generation failed, falling back to template. Error: {type(e).__name__}: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                pass
        else:
            logger.warning("No LLM provider available, using template")
        
        # Fallback: Plantillas predefinidas
        questions = self._formulate_socratic_questions(prompt, cognitive_state)

        message = f"""
## Análisis del Problema

Para guiarte efectivamente, necesito comprender tu proceso de pensamiento.
Por favor, respondé las siguientes preguntas:

{self._format_questions(questions)}

📝 **Importante**: No estoy evitando ayudarte. Estas preguntas son fundamentales
para que desarrolles tu capacidad de descomposición y análisis de problemas,
que es más valiosa que cualquier solución específica.

Una vez que compartas tu razonamiento, podré orientarte de manera precisa.
"""

        return {
            "message": message.strip(),
            "mode": TutorMode.SOCRATICO,
            "pedagogical_intent": "promote_decomposition_and_planning",
            "questions": questions,
            "requires_student_response": True,
            "metadata": {
                "cognitive_state": cognitive_state,
                "help_level": HelpLevel.MINIMO,
            }
        }

    async def _generate_socratic_with_llm(
        self,
        prompt: str,
        cognitive_state: str,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera respuesta socrática usando LLM (async)"""
        from ..llm.base import LLMMessage, LLMRole

        # Preparar parámetros para el prompt
        student_level = strategy.get("student_level", CognitiveScaffoldingLevel.INTERMEDIO)
        semaforo_state_str = strategy.get("semaforo_state", "verde")

        # Convertir string de semaforo a enum si es necesario
        if isinstance(semaforo_state_str, str):
            semaforo_map = {"verde": SemaforoState.VERDE, "amarillo": SemaforoState.AMARILLO, "rojo": SemaforoState.ROJO}
            semaforo_state = semaforo_map.get(semaforo_state_str, SemaforoState.VERDE)
        else:
            semaforo_state = semaforo_state_str

        system_prompt = self.prompts.get_intervention_prompt(
            intervention_type=TutorInterventionType.PREGUNTA_SOCRATICA,
            student_level=student_level,
            semaforo_state=semaforo_state,
            context={
                "cognitive_state": cognitive_state,
                "help_level": strategy.get("help_level", "bajo"),
                "prompt": prompt
            }
        )

        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content=system_prompt),
            LLMMessage(role=LLMRole.USER, content=f"Estudiante pregunta: {prompt}")
        ]

        # Ejecutar generate de forma asíncrona
        llm_response = await self.llm_provider.generate(messages, temperature=0.7, max_tokens=500)

        # Extraer el texto de la respuesta
        response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)

        return {
            "message": response_text,
            "mode": TutorMode.SOCRATICO,
            "pedagogical_intent": "socratic_questioning",
            "requires_student_response": True,
            "metadata": {
                "cognitive_state": cognitive_state,
                "help_level": strategy.get("help_level", HelpLevel.BAJO),
                "generated_with_llm": True
            }
        }

    async def _generate_conceptual_with_llm(
        self,
        prompt: str,
        cognitive_state: str,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera corrección conceptual usando LLM (async)"""
        from ..llm.base import LLMMessage, LLMRole

        student_level = strategy.get("student_level", CognitiveScaffoldingLevel.INTERMEDIO)
        semaforo_state_str = strategy.get("semaforo_state", "verde")

        if isinstance(semaforo_state_str, str):
            semaforo_map = {"verde": SemaforoState.VERDE, "amarillo": SemaforoState.AMARILLO, "rojo": SemaforoState.ROJO}
            semaforo_state = semaforo_map.get(semaforo_state_str, SemaforoState.VERDE)
        else:
            semaforo_state = semaforo_state_str

        system_prompt = self.prompts.get_intervention_prompt(
            intervention_type=TutorInterventionType.CORRECCION_CONCEPTUAL,
            student_level=student_level,
            semaforo_state=semaforo_state,
            context={
                "cognitive_state": cognitive_state,
                "help_level": strategy.get("help_level", "medio"),
                "prompt": prompt
            }
        )

        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content=system_prompt),
            LLMMessage(role=LLMRole.USER, content=f"Pregunta del estudiante: {prompt}")
        ]

        # Ejecutar generate de forma asíncrona
        llm_response = await self.llm_provider.generate(messages, temperature=0.7, max_tokens=600)

        response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)

        return {
            "message": response_text,
            "mode": TutorMode.EXPLICATIVO,
            "pedagogical_intent": "conceptual_understanding",
            "help_level": HelpLevel.MEDIO,
            "metadata": {
                "cognitive_state": cognitive_state,
                "provides_code": False,
                "generated_with_llm": True
            }
        }

    async def _generate_hints_with_llm(
        self,
        prompt: str,
        cognitive_state: str,
        strategy: Dict[str, Any],
        student_history: Optional[List[CognitiveTrace]] = None
    ) -> Dict[str, Any]:
        """Genera pistas guiadas usando LLM (async)"""
        from ..llm.base import LLMMessage, LLMRole

        student_level = strategy.get("student_level", CognitiveScaffoldingLevel.INTERMEDIO)
        semaforo_state_str = strategy.get("semaforo_state", "verde")
        help_level = self._determine_adaptive_help_level(student_history, strategy)

        if isinstance(semaforo_state_str, str):
            semaforo_map = {"verde": SemaforoState.VERDE, "amarillo": SemaforoState.AMARILLO, "rojo": SemaforoState.ROJO}
            semaforo_state = semaforo_map.get(semaforo_state_str, SemaforoState.VERDE)
        else:
            semaforo_state = semaforo_state_str

        system_prompt = self.prompts.get_intervention_prompt(
            intervention_type=TutorInterventionType.PISTAS_GUIADAS,
            student_level=student_level,
            semaforo_state=semaforo_state,
            context={
                "cognitive_state": cognitive_state,
                "help_level": help_level.value if hasattr(help_level, 'value') else str(help_level),
                "prompt": prompt,
                "previous_hints": self._count_previous_hints(student_history) if student_history else 0
            }
        )

        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content=system_prompt),
            LLMMessage(role=LLMRole.USER, content=f"Estudiante pregunta: {prompt}")
        ]

        # Ejecutar generate de forma asíncrona
        llm_response = await self.llm_provider.generate(messages, temperature=0.7, max_tokens=700)

        response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)

        return {
            "message": response_text,
            "mode": TutorMode.GUIADO,
            "pedagogical_intent": "scaffolding",
            "help_level": help_level,
            "requires_justification": True,
            "metadata": {
                "cognitive_state": cognitive_state,
                "generated_with_llm": True
            }
        }

    def _formulate_socratic_questions(
        self,
        prompt: str,
        cognitive_state: str
    ) -> List[str]:
        """Formula preguntas socráticas adaptadas al contexto"""
        base_questions = [
            "¿Qué entendés que te están pidiendo resolver en este problema?",
            "¿Qué conceptos o estructuras de datos considerás relevantes?",
            "¿Podés describir con tus palabras cómo funcionaría una solución?",
            "¿Qué intentaste hasta ahora? ¿Qué resultado obtuviste?",
        ]

        # Adaptar según estado cognitivo
        if cognitive_state == "exploracion":
            base_questions.insert(
                1,
                "¿Qué partes del enunciado te resultan claras y cuáles confusas?"
            )
        elif cognitive_state == "depuracion":
            base_questions = [
                "¿Qué comportamiento esperabas y qué obtuviste?",
                "¿En qué punto específico falla tu código?",
                "¿Qué hipótesis tenés sobre la causa del error?",
                "¿Qué pruebas hiciste para verificar tu hipótesis?",
            ]

        return base_questions

    def _format_questions(self, questions: List[str]) -> str:
        """Formatea lista de preguntas"""
        return "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

    async def _generate_conceptual_explanation(
        self,
        prompt: str,
        cognitive_state: str,
        strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera explicación conceptual sin dar implementación específica

        Reduce carga extrínseca, favorece carga germinal (Sweller, 1988)
        """
        # Usar LLM si está disponible
        if self.llm_provider:
            try:
                logger.info(f"Generating conceptual explanation with LLM for: {prompt[:50]}...")
                return await self._generate_conceptual_with_llm(prompt, cognitive_state, strategy)
            except Exception as e:
                logger.error(f"LLM generation failed for conceptual explanation: {type(e).__name__}: {str(e)}")
                pass
        
        # Fallback: template genérico
        message = """
## Conceptos Fundamentales

Vamos a abordar esto desde los conceptos fundamentales, sin adelantarnos a la implementación.

### Concepto Clave

[El concepto principal que necesitás comprender para resolver este problema]

### Principios Importantes

1. **Principio 1**: [Explicación del principio]
2. **Principio 2**: [Explicación del principio]

### Ejemplo Simple

[Analogía o ejemplo simple que ilustra el concepto]

### Conexión con tu Problema

Para tu caso específico, estos conceptos significan que...

---

💡 **Próximo paso**: Ahora que tenés más claros estos conceptos, ¿cómo
pensás aplicarlos a tu problema? ¿Qué parte querés que profundice?
"""

        return {
            "message": message.strip(),
            "mode": TutorMode.EXPLICATIVO,
            "pedagogical_intent": "conceptual_understanding",
            "help_level": HelpLevel.MEDIO,
            "metadata": {
                "cognitive_state": cognitive_state,
                "provides_code": False,
            }
        }

    async def _generate_guided_hints(
        self,
        prompt: str,
        cognitive_state: str,
        strategy: Dict[str, Any],
        student_history: Optional[List[CognitiveTrace]] = None
    ) -> Dict[str, Any]:
        """
        Genera pistas graduadas sin revelar la solución completa

        Implementa andamiaje cognitivo (scaffolding) con niveles adaptativos
        según el historial del estudiante.

        Niveles de pistas:
        - Nivel 1 (MINIMO): Preguntas socráticas orientadoras
        - Nivel 2 (BAJO): Pistas conceptuales generales
        - Nivel 3 (MEDIO): Pistas con algo de detalle + pseudocódigo alto nivel
        - Nivel 4 (ALTO): Fragmentos conceptuales + estrategia detallada
        """
        # Usar LLM si está disponible
        if self.llm_provider:
            try:
                logger.info(f"Generating guided hints with LLM for: {prompt[:50]}...")
                return await self._generate_hints_with_llm(prompt, cognitive_state, strategy, student_history)
            except Exception as e:
                logger.error(f"LLM generation failed for hints: {type(e).__name__}: {str(e)}")
                pass
        
        # Fallback: lógica de templates
        # Determinar nivel de ayuda basado en historial
        help_level = self._determine_adaptive_help_level(student_history, strategy)

        # Analizar cuántas pistas ha recibido ya
        previous_hints_count = self._count_previous_hints(student_history) if student_history else 0

        # Generar pistas según nivel
        if help_level == HelpLevel.MINIMO:
            hints = self._generate_level1_hints(prompt, cognitive_state)
        elif help_level == HelpLevel.BAJO:
            hints = self._generate_level2_hints(prompt, cognitive_state)
        elif help_level == HelpLevel.MEDIO:
            hints = self._generate_level3_hints(prompt, cognitive_state)
        else:  # ALTO
            hints = self._generate_level4_hints(prompt, cognitive_state)

        # Construir mensaje
        message = f"""
## Pistas Graduadas - Nivel {help_level.value.upper()}

{self._format_hints_message(hints, help_level)}

---

{self._generate_followup_question(help_level, previous_hints_count)}
"""

        return {
            "message": message.strip(),
            "mode": TutorMode.GUIADO,
            "pedagogical_intent": "scaffolding",
            "help_level": help_level,
            "hints_provided": hints,
            "hints_count": len(hints),
            "previous_hints_count": previous_hints_count,
            "requires_justification": True,
            "metadata": {
                "cognitive_state": cognitive_state,
                "provides_code": False,
                "provides_pseudocode": help_level in [HelpLevel.MEDIO, HelpLevel.ALTO],
                "adaptive_level": help_level.value,
            }
        }

    def _determine_adaptive_help_level(
        self,
        student_history: Optional[List[CognitiveTrace]],
        strategy: Dict[str, Any]
    ) -> HelpLevel:
        """
        Determina el nivel de ayuda adaptativamente según:
        1. Estrategia sugerida por CRPE
        2. Historial de pistas recibidas (si recibió muchas, reducir detalle)
        3. Nivel de AI involvement acumulado
        """
        # Nivel base desde estrategia
        strategy_level = strategy.get("help_level", HelpLevel.MEDIO)

        if not student_history:
            return strategy_level

        # Contar pistas previas
        hints_received = self._count_previous_hints(student_history)

        # Si ya recibió muchas pistas (>5), reducir nivel para fomentar autonomía
        if hints_received > 5:
            if strategy_level == HelpLevel.ALTO:
                return HelpLevel.MEDIO
            elif strategy_level == HelpLevel.MEDIO:
                return HelpLevel.BAJO

        # Calcular AI involvement promedio
        avg_ai_involvement = sum(t.ai_involvement for t in student_history) / len(student_history)

        # Si dependency alta (>0.6), reducir nivel de ayuda
        if avg_ai_involvement > 0.6:
            if strategy_level == HelpLevel.ALTO:
                return HelpLevel.MEDIO
            elif strategy_level == HelpLevel.MEDIO:
                return HelpLevel.BAJO

        return strategy_level

    def _count_previous_hints(self, student_history: List[CognitiveTrace]) -> int:
        """Cuenta cuántas pistas ha recibido el estudiante"""
        return sum(
            1 for t in student_history
            if "hints_provided" in t.metadata.get("response_metadata", {})
        )

    def _generate_level1_hints(self, prompt: str, cognitive_state: str) -> List[Dict[str, str]]:
        """Nivel 1 - MINIMO: Solo preguntas socráticas orientadoras"""
        return [
            {
                "level": 1,
                "type": "question",
                "content": "¿Qué pasos creés que son necesarios para resolver este problema?"
            },
            {
                "level": 1,
                "type": "question",
                "content": "¿Qué conceptos o estructuras de datos podrían ser relevantes aquí?"
            },
            {
                "level": 1,
                "type": "question",
                "content": "¿Podés describir con tus palabras cómo funcionaría una solución ideal?"
            }
        ]

    def _generate_level2_hints(self, prompt: str, cognitive_state: str) -> List[Dict[str, str]]:
        """Nivel 2 - BAJO: Pistas conceptuales generales"""
        return [
            {
                "level": 2,
                "type": "conceptual",
                "content": "Pensá en descomponer el problema en partes más pequeñas. ¿Cuáles serían esas partes?"
            },
            {
                "level": 2,
                "type": "conceptual",
                "content": "Considerá qué estructura de datos se adapta mejor a las operaciones que necesitás realizar."
            },
            {
                "level": 2,
                "type": "reflection",
                "content": "¿Qué casos especiales o de borde deberías tener en cuenta?"
            }
        ]

    def _generate_level3_hints(self, prompt: str, cognitive_state: str) -> List[Dict[str, str]]:
        """Nivel 3 - MEDIO: Pistas con detalle + pseudocódigo alto nivel"""
        return [
            {
                "level": 3,
                "type": "decomposition",
                "content": "Dividí el problema en estas etapas: 1) Inicialización, 2) Operación principal, 3) Validación"
            },
            {
                "level": 3,
                "type": "strategy",
                "content": "Una estrategia común es usar [concepto general] para gestionar [aspecto del problema]"
            },
            {
                "level": 3,
                "type": "pseudocode",
                "content": """```
// Estructura general (alto nivel)
función resolver():
    // Paso 1: Preparar datos
    // Paso 2: Procesar elemento por elemento
    // Paso 3: Retornar resultado
```"""
            }
        ]

    def _generate_level4_hints(self, prompt: str, cognitive_state: str) -> List[Dict[str, str]]:
        """Nivel 4 - ALTO: Fragmentos conceptuales + estrategia detallada"""
        return [
            {
                "level": 4,
                "type": "detailed_strategy",
                "content": "Considerá este enfoque: [descripción detallada de estrategia sin código específico]"
            },
            {
                "level": 4,
                "type": "pattern",
                "content": "Un patrón útil aquí es [nombre del patrón], que consiste en [explicación conceptual]"
            },
            {
                "level": 4,
                "type": "conceptual_fragment",
                "content": """Para gestionar [aspecto específico]:
- Opción A: [ventajas y desventajas]
- Opción B: [ventajas y desventajas]
¿Cuál elegirías y por qué?"""
            }
        ]

    def _format_hints_message(self, hints: List[Dict[str, str]], level: HelpLevel) -> str:
        """Formatea las pistas para el mensaje"""
        icons = {
            "question": "❓",
            "conceptual": "💡",
            "reflection": "🤔",
            "decomposition": "🔍",
            "strategy": "🎯",
            "pseudocode": "📝",
            "detailed_strategy": "🗺️",
            "pattern": "🧩",
            "conceptual_fragment": "💭"
        }

        formatted = []
        for i, hint in enumerate(hints, 1):
            icon = icons.get(hint["type"], "•")
            hint_type = hint["type"].replace("_", " ").title()
            formatted.append(f"### {icon} Pista {i}: {hint_type}\n{hint['content']}")

        return "\n\n".join(formatted)

    def _generate_followup_question(self, level: HelpLevel, hints_count: int) -> str:
        """Genera pregunta de seguimiento según contexto"""
        if hints_count > 5:
            return """⚠️ **Nota**: Has recibido varias pistas ya. Es momento de que intentes
avanzar de forma más autónoma. ¿Qué vas a hacer con la información que tenés?"""
        elif level == HelpLevel.MINIMO:
            return """❓ **Pregunta para vos**: Respondé primero estas preguntas antes de
solicitar más ayuda. La clave está en tu razonamiento, no en la respuesta de la IA."""
        elif level in [HelpLevel.MEDIO, HelpLevel.ALTO]:
            return """❓ **Pregunta para vos**: Basándote en estas pistas, ¿cuál sería tu
próximo paso concreto? ¿Qué decisión de diseño tomarías y **por qué**?"""
        else:
            return """❓ **Próximo paso**: Intentá formular un plan basándote en estas pistas.
¿Qué harías primero?"""

    def _generate_clarification_request(
        self,
        prompt: str,
        cognitive_state: str
    ) -> Dict[str, Any]:
        """Solicita clarificación cuando el prompt es ambiguo"""
        message = """
## Necesito Más Información

Para poder ayudarte de manera efectiva, necesito que seas más específico:

### 📌 Contexto del Problema
- ¿Qué parte exacta te genera dificultad?
- ¿Qué entendés que tenés que lograr?

### 📌 Lo que Intentaste
- ¿Qué enfoque probaste?
- ¿Qué código escribiste hasta ahora?
- ¿Qué resultado obtuviste vs. qué esperabas?

### 📌 Tu Hipótesis
- ¿Qué creés que podría estar causando el problema?
- ¿Qué soluciones consideraste?

Por favor, reformulá tu consulta incluyendo esta información.
"""

        return {
            "message": message.strip(),
            "mode": TutorMode.SOCRATICO,
            "pedagogical_intent": "promote_specificity",
            "requires_student_response": True,
            "metadata": {
                "cognitive_state": cognitive_state,
            }
        }

    def evaluate_student_response(
        self,
        student_response: str,
        previous_interaction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evalúa la respuesta del estudiante a preguntas/pistas previas

        Detecta:
        - Nivel de elaboración
        - Explicitación del razonamiento
        - Justificación de decisiones
        - Autocorrección
        """
        analysis = {
            "has_justification": self._detect_justification(student_response),
            "shows_decomposition": self._detect_decomposition(student_response),
            "shows_planning": self._detect_planning(student_response),
            "shows_self_reflection": self._detect_self_reflection(student_response),
            "quality_score": 0.0,  # 0-1
        }

        # Calcular score de calidad
        score = 0.0
        if analysis["has_justification"]:
            score += 0.3
        if analysis["shows_decomposition"]:
            score += 0.3
        if analysis["shows_planning"]:
            score += 0.2
        if analysis["shows_self_reflection"]:
            score += 0.2

        analysis["quality_score"] = score

        return analysis

    def _detect_justification(self, text: str) -> bool:
        """Detecta si hay justificación en la respuesta"""
        justification_signals = [
            "porque", "ya que", "debido a", "considerando que",
            "mi razón es", "pensé que", "decidí", "elegí"
        ]
        return any(signal in text.lower() for signal in justification_signals)

    def _detect_decomposition(self, text: str) -> bool:
        """Detecta si hay descomposición del problema"""
        decomposition_signals = [
            "primero", "luego", "después", "paso", "parte",
            "dividir", "separar", "componente", "subproblema"
        ]
        return any(signal in text.lower() for signal in decomposition_signals)

    def _detect_planning(self, text: str) -> bool:
        """Detecta si hay evidencia de planificación"""
        planning_signals = [
            "voy a", "planeo", "mi estrategia", "mi plan",
            "primero haré", "mi enfoque", "mi idea es"
        ]
        return any(signal in text.lower() for signal in planning_signals)

    def _detect_self_reflection(self, text: str) -> bool:
        """Detecta si hay reflexión metacognitiva"""
        reflection_signals = [
            "me doy cuenta", "entiendo que", "ahora veo",
            "me confundí", "cometí el error", "debería"
        ]
        return any(signal in text.lower() for signal in reflection_signals)