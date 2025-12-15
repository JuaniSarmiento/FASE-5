"""
Response Generator - Genera respuestas pedagógicas usando el agente apropiado

Extraído de AIGateway como parte de la refactorización God Class → componentes especializados.
"""
from typing import Dict, Any, Optional
import logging

from ..agents.tutor import TutorCognitivoAgent
from ..agents.evaluator import ProcessEvaluatorAgent
from ..agents.simulators import SimuladorProfesionalAgent, SimuladorType
from ..llm.base import LLMProvider

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Genera respuestas pedagógicas usando el agente apropiado.

    Responsabilidad: Routing de requests a agentes especializados y generación de respuestas.

    Extracted from: AIGateway (God Class refactoring)
    """

    def __init__(
        self,
        tutor: TutorCognitivoAgent,
        evaluator: ProcessEvaluatorAgent,
        llm_provider: LLMProvider,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa el generador de respuestas.

        Args:
            tutor: Agente tutor cognitivo
            evaluator: Agente evaluador de procesos
            llm_provider: Proveedor de LLM
            config: Configuración adicional
        """
        self.tutor = tutor
        self.evaluator = evaluator
        self.llm_provider = llm_provider
        self.config = config or {}

        # Simuladores (lazy loading)
        self._simulators = {}

        logger.info("ResponseGenerator initialized")

    def generate_response(
        self,
        classification: Dict[str, Any],
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Genera respuesta usando el agente apropiado según la clasificación.

        Args:
            classification: Resultado de clasificación de CRPE
            prompt: Prompt del estudiante
            context: Contexto adicional
            session_id: ID de la sesión

        Returns:
            Respuesta pedagógica generada

        Raises:
            ValueError: Si el tipo de request no es reconocido
        """
        request_type = classification.get("type")
        cognitive_state = classification.get("cognitive_state")

        logger.info(
            f"Generating response for request type: {request_type}",
            extra={
                "request_type": request_type,
                "cognitive_state": cognitive_state,
                "session_id": session_id
            }
        )

        # Route to appropriate agent
        if request_type == "help_request":
            return self._generate_tutor_response(
                prompt, context, cognitive_state
            )
        elif request_type == "evaluation_request":
            return self._generate_evaluation_response(
                session_id, context
            )
        elif request_type == "simulator_request":
            simulator_type = classification.get("simulator")
            return self._generate_simulator_response(
                simulator_type, prompt, context
            )
        else:
            return self._generate_default_response(prompt)

    def _generate_tutor_response(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]],
        cognitive_state: str
    ) -> str:
        """
        Genera respuesta usando T-IA-Cog (Tutor Cognitivo).

        Args:
            prompt: Pregunta del estudiante
            context: Contexto (código, traza, etc.)
            cognitive_state: Estado cognitivo detectado

        Returns:
            Respuesta pedagógica del tutor
        """
        logger.debug(
            f"Generating tutor response for cognitive state: {cognitive_state}"
        )

        # Preparar request para el tutor
        tutor_request = {
            "prompt": prompt,
            "cognitive_state": cognitive_state,
            "context": context or {}
        }

        # Generar respuesta usando el tutor
        response = self.tutor.process_request(tutor_request)

        return response

    def _generate_evaluation_response(
        self,
        session_id: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Genera respuesta de evaluación usando E-IA-Proc.

        Args:
            session_id: ID de la sesión a evaluar
            context: Contexto adicional

        Returns:
            Reporte de evaluación
        """
        logger.debug(f"Generating evaluation for session: {session_id}")

        # El evaluador necesita acceso a las trazas de la sesión
        # (esto se maneja en el AIGateway que pasa las trazas)
        evaluation = self.evaluator.evaluate_process(
            session_id=session_id,
            context=context or {}
        )

        return evaluation

    def _generate_simulator_response(
        self,
        simulator_type: str,
        prompt: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Genera respuesta usando S-IA-X (Simuladores Profesionales).

        Args:
            simulator_type: Tipo de simulador (PO, SM, IT, etc.)
            prompt: Interacción del estudiante
            context: Contexto de la simulación

        Returns:
            Respuesta del simulador
        """
        logger.debug(f"Generating simulator response: {simulator_type}")

        # Get or create simulator
        simulator = self._get_simulator(simulator_type)

        if not simulator:
            return f"Simulador '{simulator_type}' no disponible actualmente."

        # Generate response using the interact method
        result = simulator.interact(prompt, context or {})

        # Return the message from the result
        return result.get("message", str(result))

    def _get_simulator(self, simulator_type: str):
        """
        Obtiene o crea un simulador (lazy loading).

        Args:
            simulator_type: Tipo de simulador (PO, SM, IT, etc.)

        Returns:
            Instancia del simulador o None
        """
        # Mapping de códigos cortos a SimuladorType
        type_mapping = {
            "PO": SimuladorType.PRODUCT_OWNER,
            "SM": SimuladorType.SCRUM_MASTER,
            "IT": SimuladorType.TECH_INTERVIEWER,
            "IR": SimuladorType.INCIDENT_RESPONDER,
            "CX": SimuladorType.CLIENT,
            "DSO": SimuladorType.DEVSECOPS,
        }

        # Lazy loading de simuladores
        if simulator_type not in self._simulators:
            sim_type = type_mapping.get(simulator_type)
            if sim_type:
                self._simulators[simulator_type] = SimuladorProfesionalAgent(
                    simulator_type=sim_type,
                    llm_provider=self.llm_provider
                )
            else:
                logger.warning(f"Unknown simulator type: {simulator_type}")
                return None

        return self._simulators.get(simulator_type)

    def _generate_default_response(self, prompt: str) -> str:
        """
        Genera respuesta por defecto cuando el tipo no es reconocido.

        Args:
            prompt: Prompt original

        Returns:
            Respuesta genérica
        """
        logger.warning(f"Generating default response for unrecognized request")

        return (
            "No puedo procesar tu solicitud en este momento. "
            "¿Podrías reformular tu pregunta o ser más específico sobre lo que necesitas?"
        )
