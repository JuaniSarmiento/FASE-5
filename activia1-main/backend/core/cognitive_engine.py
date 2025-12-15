"""
Motor de Razonamiento Cognitivo-Pedagógico (CRPE)
Componente central del ai-gateway que coordina todos los submodelos
"""
from typing import Optional, Dict, Any, List, Tuple
from enum import Enum

from ..models.trace import CognitiveTrace, InteractionType, CognitiveState


class AgentMode(str, Enum):
    """
    Modos operativos del motor cognitivo.

    IMPORTANTE: Valores en MAYÚSCULAS para consistencia con API y database.
    Se unificó con SessionMode (que fue deprecado) para evitar duplicación.
    """
    TUTOR = "TUTOR"  # T-IA-Cog
    EVALUATOR = "EVALUATOR"  # E-IA-Proc
    SIMULATOR = "SIMULATOR"  # S-IA-X
    RISK_ANALYST = "RISK_ANALYST"  # AR-IA
    GOVERNANCE = "GOVERNANCE"  # GOV-IA
    PRACTICE = "PRACTICE"  # Modo práctica libre (sin asistencia activa)


# NOTE: CognitiveState moved to models.trace to avoid circular dependencies
# (repositories shouldn't import from core). Re-exported here for backward compatibility.
# New code should import directly from models.trace


class CognitiveReasoningEngine:
    """
    Motor de Razonamiento Cognitivo-Pedagógico (CRPE)

    Coordina la interacción entre todos los submodelos AI-Native y determina
    el comportamiento del sistema según el contexto pedagógico.
    """

    def __init__(self, llm_provider=None, config: Optional[Dict[str, Any]] = None):
        self.llm_provider = llm_provider
        self.config = config or {}
        self.current_mode: AgentMode = AgentMode.TUTOR
        self.current_state: Optional[CognitiveState] = None

        # Políticas pedagógicas configurables
        self.pedagogical_policies = {
            "max_help_level": self.config.get("max_help_level", 0.7),  # 0-1
            "require_justification": self.config.get("require_justification", True),
            "block_total_delegation": self.config.get("block_total_delegation", True),
            "adaptive_difficulty": self.config.get("adaptive_difficulty", True),
        }

    def classify_prompt(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clasifica el prompt del estudiante y determina el estado cognitivo

        Args:
            prompt: El prompt enviado por el estudiante
            context: Contexto de la actividad

        Returns:
            Diccionario con clasificación y metadata
        """
        prompt_lower = prompt.lower()

        # Detectar delegación total
        delegation_signals = [
            "dame el código completo",
            "hacé todo",
            "resolvelo por mí",
            "código entero",
            "implementa todo"
        ]
        is_total_delegation = any(signal in prompt_lower for signal in delegation_signals)

        # Detectar tipo de solicitud
        question_signals = ["cómo", "por qué", "qué", "cuál", "explica", "ayuda"]
        is_question = any(signal in prompt_lower for signal in question_signals)

        # Detectar solicitud de explicación (incluye preguntas "qué es")
        explanation_signals = ["explica", "no entiendo", "ayuda a entender", "por qué", "qué es", "qué son"]
        requests_explanation = any(signal in prompt_lower for signal in explanation_signals)

        # Determinar estado cognitivo
        if "no entiendo" in prompt_lower or "no sé" in prompt_lower:
            cognitive_state = CognitiveState.EXPLORACION
        elif "cómo implemento" in prompt_lower or "cómo hago" in prompt_lower:
            cognitive_state = CognitiveState.PLANIFICACION
        elif "error" in prompt_lower or "bug" in prompt_lower or "falla" in prompt_lower:
            cognitive_state = CognitiveState.DEPURACION
        elif "funciona" in prompt_lower or "correcto" in prompt_lower:
            cognitive_state = CognitiveState.VALIDACION
        else:
            cognitive_state = CognitiveState.IMPLEMENTACION

        return {
            "is_total_delegation": is_total_delegation,
            "is_question": is_question,
            "requests_explanation": requests_explanation,
            "cognitive_state": cognitive_state,
            "requires_intervention": is_total_delegation and self.pedagogical_policies["block_total_delegation"],
            "suggested_response_type": self._determine_response_type(
                is_total_delegation, is_question, requests_explanation
            )
        }

    def _determine_response_type(
        self,
        is_delegation: bool,
        is_question: bool,
        requests_explanation: bool
    ) -> str:
        """Determina el tipo de respuesta apropiada"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Determining response type: delegation={is_delegation}, question={is_question}, explanation={requests_explanation}")
        
        if is_delegation:
            return "socratic_questioning"  # Preguntas socráticas
        elif requests_explanation:
            return "conceptual_explanation"  # Explicación conceptual
        elif is_question:
            return "guided_hints"  # Pistas guiadas
        else:
            return "clarification_request"  # Solicitar clarificación

    def should_block_response(self, classification: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Determina si debe bloquearse la respuesta según políticas de gobernanza

        Returns:
            (should_block, reason)
        """
        if classification["is_total_delegation"] and self.pedagogical_policies["block_total_delegation"]:
            return True, "Delegación total detectada. Se requiere descomposición del problema."

        return False, None

    def generate_pedagogical_response_strategy(
        self,
        prompt: str,
        classification: Dict[str, Any],
        student_history: Optional[List[CognitiveTrace]] = None
    ) -> Dict[str, Any]:
        """
        Genera la estrategia de respuesta pedagógica

        Args:
            prompt: Prompt del estudiante
            classification: Clasificación del prompt
            student_history: Historial de trazas del estudiante

        Returns:
            Estrategia de respuesta con instrucciones para el LLM
        """
        response_type = classification["suggested_response_type"]
        cognitive_state = classification["cognitive_state"]

        # Construir estrategia base
        strategy = {
            "response_type": response_type,
            "cognitive_state": cognitive_state,
            "max_help_level": self.pedagogical_policies["max_help_level"],
            "instructions": [],
            "constraints": [],
            "expected_elements": []
        }

        # Instrucciones según tipo de respuesta
        if response_type == "socratic_questioning":
            strategy["instructions"] = [
                "No proporcionar código completo",
                "Hacer preguntas que guíen el razonamiento",
                "Solicitar que el estudiante explique su comprensión del problema",
                "Pedir que descomponga el problema en pasos"
            ]
            strategy["expected_elements"] = [
                "preguntas_guia",
                "solicitud_explicacion",
                "descomposicion_problema"
            ]

        elif response_type == "conceptual_explanation":
            strategy["instructions"] = [
                "Explicar conceptos fundamentales relevantes",
                "Usar ejemplos simples y analogías",
                "Evitar dar la implementación específica",
                "Conectar con conocimientos previos"
            ]
            strategy["expected_elements"] = [
                "explicacion_conceptual",
                "ejemplos",
                "principios_fundamentales"
            ]

        elif response_type == "guided_hints":
            strategy["instructions"] = [
                "Proporcionar pistas graduadas",
                "Sugerir dirección sin revelar la solución",
                "Ofrecer pseudocódigo de alto nivel si es apropiado",
                "Pedir que el estudiante justifique sus próximos pasos"
            ]
            strategy["expected_elements"] = [
                "pistas_graduadas",
                "direccion_general",
                "solicitud_justificacion"
            ]

        # Restricciones comunes
        strategy["constraints"] = [
            "No generar código completo sin mediación",
            "Exigir justificación de decisiones",
            "Registrar todo en trazabilidad N4",
            "Promover la autorregulación"
        ]

        # Ajustar según historial del estudiante
        if student_history:
            strategy["student_context"] = self._analyze_student_history(student_history)

        return strategy

    def _analyze_student_history(self, history: List[CognitiveTrace]) -> Dict[str, Any]:
        """Analiza el historial del estudiante para personalizar la respuesta"""
        if not history:
            return {"level": "beginner", "patterns": []}

        # Contar patrones
        delegation_count = sum(
            1 for t in history
            if "delegación" in t.content.lower() or "código completo" in t.content.lower()
        )
        self_correction_count = sum(
            1 for t in history
            if t.interaction_type == InteractionType.SELF_CORRECTION
        )

        return {
            "total_interactions": len(history),
            "delegation_tendency": delegation_count / len(history) if history else 0,
            "self_correction_rate": self_correction_count / len(history) if history else 0,
            "suggested_difficulty_adjustment": "increase" if self_correction_count > 3 else "maintain"
        }

    def set_mode(self, mode: AgentMode) -> None:
        """Cambia el modo operativo del motor"""
        self.current_mode = mode

    def get_current_mode(self) -> AgentMode:
        """Retorna el modo operativo actual"""
        return self.current_mode