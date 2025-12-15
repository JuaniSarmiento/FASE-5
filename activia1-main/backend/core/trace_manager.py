"""
Trace Manager - Gestiona captura y persistencia de trazas N4

Extraído de AIGateway como parte de la refactorización God Class → componentes especializados.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from ..models.trace import CognitiveTrace, TraceLevel, InteractionType, TraceSequence, CognitiveState
from ..database.repositories import TraceRepository, TraceSequenceRepository
from ..agents.traceability import TrazabilidadN4Agent
from ..core.constants import utc_now

logger = logging.getLogger(__name__)


class TraceManager:
    """
    Gestiona captura y persistencia de trazas N4.

    Responsabilidad: Captura de trazas de entrada/salida, secuencias y persistencia.

    Extracted from: AIGateway (God Class refactoring)
    """

    def __init__(
        self,
        trace_repo: TraceRepository,
        sequence_repo: TraceSequenceRepository,
        traceability_agent: TrazabilidadN4Agent
    ):
        """
        Inicializa el gestor de trazas.

        Args:
            trace_repo: Repositorio de trazas
            sequence_repo: Repositorio de secuencias
            traceability_agent: Agente TC-N4
        """
        self.trace_repo = trace_repo
        self.sequence_repo = sequence_repo
        self.traceability_agent = traceability_agent

        logger.info("TraceManager initialized")

    def capture_input_trace(
        self,
        session_id: str,
        student_id: str,
        activity_id: str,
        prompt: str,
        cognitive_state: CognitiveState,
        context: Optional[Dict[str, Any]] = None
    ) -> CognitiveTrace:
        """
        Captura traza de entrada del estudiante (N4).

        Args:
            session_id: ID de la sesión
            student_id: ID del estudiante
            activity_id: ID de la actividad
            prompt: Prompt del estudiante
            cognitive_state: Estado cognitivo detectado
            context: Contexto adicional (código, archivos, etc.)

        Returns:
            Traza capturada

        Raises:
            ValueError: Si faltan campos requeridos
        """
        logger.debug(
            "Capturing input trace",
            extra={
                "session_id": session_id,
                "student_id": student_id,
                "cognitive_state": cognitive_state
            }
        )

        # Crear traza usando TC-N4
        trace = self.traceability_agent.capture_trace(
            session_id=session_id,
            student_id=student_id,
            activity_id=activity_id,
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            content=prompt,
            context=context or {},
            cognitive_state=cognitive_state,
            metadata={
                "timestamp": utc_now().isoformat(),
                "trace_type": "input"
            }
        )

        # Persistir
        self.trace_repo.create(trace)

        logger.info(
            f"Input trace captured: {trace.id}",
            extra={"trace_id": trace.id, "session_id": session_id}
        )

        return trace

    def capture_output_trace(
        self,
        session_id: str,
        student_id: str,
        activity_id: str,
        response: str,
        agent_used: str,
        cognitive_state: CognitiveState,
        ai_involvement: float,
        decision_justification: Optional[str] = None,
        alternatives_considered: Optional[List[str]] = None,
        parent_trace_id: Optional[str] = None
    ) -> CognitiveTrace:
        """
        Captura traza de salida del agente (N4).

        Args:
            session_id: ID de la sesión
            student_id: ID del estudiante
            activity_id: ID de la actividad
            response: Respuesta generada
            agent_used: Agente que generó la respuesta
            cognitive_state: Estado cognitivo
            ai_involvement: Nivel de involucramiento de IA (0.0-1.0)
            decision_justification: Justificación de la decisión pedagógica
            alternatives_considered: Alternativas consideradas
            parent_trace_id: ID de la traza de entrada relacionada

        Returns:
            Traza capturada
        """
        logger.debug(
            "Capturing output trace",
            extra={
                "session_id": session_id,
                "agent_used": agent_used,
                "ai_involvement": ai_involvement
            }
        )

        # Crear traza usando TC-N4
        trace = self.traceability_agent.capture_trace(
            session_id=session_id,
            student_id=student_id,
            activity_id=activity_id,
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.AI_RESPONSE,
            content=response,
            context={"agent_used": agent_used},
            cognitive_state=cognitive_state,
            ai_involvement=ai_involvement,
            decision_justification=decision_justification,
            alternatives_considered=alternatives_considered or [],
            agent_id=agent_used,
            parent_trace_id=parent_trace_id,
            metadata={
                "timestamp": utc_now().isoformat(),
                "trace_type": "output"
            }
        )

        # Persistir
        self.trace_repo.create(trace)

        logger.info(
            f"Output trace captured: {trace.id}",
            extra={
                "trace_id": trace.id,
                "session_id": session_id,
                "ai_involvement": ai_involvement
            }
        )

        return trace

    def create_trace_sequence(
        self,
        session_id: str,
        student_id: str,
        activity_id: str,
        trace_ids: List[str],
        reasoning_path: Optional[List[str]] = None,
        strategy_changes: int = 0,
        ai_dependency_score: float = 0.0
    ) -> TraceSequence:
        """
        Crea una secuencia de trazas para análisis de proceso.

        Args:
            session_id: ID de la sesión
            student_id: ID del estudiante
            activity_id: ID de la actividad
            trace_ids: IDs de las trazas en la secuencia
            reasoning_path: Camino de razonamiento reconstruido
            strategy_changes: Número de cambios de estrategia
            ai_dependency_score: Score de dependencia de IA

        Returns:
            Secuencia creada
        """
        logger.debug(
            "Creating trace sequence",
            extra={
                "session_id": session_id,
                "trace_count": len(trace_ids)
            }
        )

        # Crear secuencia
        sequence = TraceSequence(
            session_id=session_id,
            student_id=student_id,
            activity_id=activity_id,
            trace_ids=trace_ids,
            reasoning_path=reasoning_path or [],
            strategy_changes=strategy_changes,
            ai_dependency_score=ai_dependency_score,
            start_time=utc_now(),
            end_time=utc_now()
        )

        # Persistir
        self.sequence_repo.create(sequence)

        logger.info(
            f"Trace sequence created: {sequence.id}",
            extra={
                "sequence_id": sequence.id,
                "session_id": session_id,
                "trace_count": len(trace_ids)
            }
        )

        return sequence

    def get_session_traces(
        self,
        session_id: str,
        interaction_type: Optional[InteractionType] = None
    ) -> List[CognitiveTrace]:
        """
        Obtiene todas las trazas de una sesión.

        Args:
            session_id: ID de la sesión
            interaction_type: Filtrar por tipo de interacción (opcional)

        Returns:
            Lista de trazas
        """
        traces = self.trace_repo.get_by_session(session_id)

        if interaction_type:
            traces = [t for t in traces if t.interaction_type == interaction_type]

        logger.debug(
            f"Retrieved {len(traces)} traces for session {session_id}",
            extra={"session_id": session_id, "trace_count": len(traces)}
        )

        return traces

    def get_trace_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        Calcula estadísticas de las trazas de una sesión.

        Args:
            session_id: ID de la sesión

        Returns:
            Diccionario con estadísticas
        """
        traces = self.get_session_traces(session_id)

        if not traces:
            return {
                "total_traces": 0,
                "input_traces": 0,
                "output_traces": 0,
                "avg_ai_involvement": 0.0,
                "cognitive_states": []
            }

        input_traces = [t for t in traces if t.interaction_type == InteractionType.STUDENT_PROMPT]
        output_traces = [t for t in traces if t.interaction_type == InteractionType.AI_RESPONSE]

        # Calcular promedio de AI involvement
        ai_involvements = [t.ai_involvement for t in traces if t.ai_involvement is not None]
        avg_ai_involvement = sum(ai_involvements) / len(ai_involvements) if ai_involvements else 0.0

        # Estados cognitivos únicos
        cognitive_states = list(set([t.cognitive_state for t in traces if t.cognitive_state]))

        stats = {
            "total_traces": len(traces),
            "input_traces": len(input_traces),
            "output_traces": len(output_traces),
            "avg_ai_involvement": round(avg_ai_involvement, 2),
            "cognitive_states": cognitive_states
        }

        logger.debug(
            "Trace statistics calculated",
            extra={"session_id": session_id, **stats}
        )

        return stats
