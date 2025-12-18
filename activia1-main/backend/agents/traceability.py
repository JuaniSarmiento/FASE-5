"""
Submodelo 6: Sistema N4 de Trazabilidad Cognitiva Institucional (TC-N4)

Captura y reconstruye el proceso completo de razonamiento híbrido humano-IA
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import re

from ..models.trace import CognitiveTrace, TraceLevel, TraceSequence, InteractionType
from ..llm.base import LLMMessage, LLMRole


class TrazabilidadN4Agent:
    """
    TC-N4: Sistema de Trazabilidad Cognitiva (4 niveles)

    Niveles:
    - N1: Superficial (archivos, entregas)
    - N2: Técnico (commits, tests)
    - N3: Interaccional (prompts, respuestas)
    - N4: Cognitivo completo (razonamiento, decisiones, justificaciones)

    Este sistema es la columna vertebral del ecosistema AI-Native
    """

    def __init__(
        self,
        llm_provider=None,
        config: Optional[Dict[str, Any]] = None,
        trace_repository=None,
        sequence_repository=None
    ):
        self.llm_provider = llm_provider
        self.config = config or {}
        self.trace_repository = trace_repository
        self.sequence_repository = sequence_repository

    def capture_interaction(
        self,
        student_id: str,
        activity_id: str,
        interaction_type: InteractionType,
        content: str,
        level: TraceLevel = TraceLevel.N4_COGNITIVO,
        **metadata
    ) -> CognitiveTrace:
        """
        Captura una interacción en el sistema de trazabilidad

        Args:
            student_id: ID del estudiante
            activity_id: ID de la actividad
            interaction_type: Tipo de interacción
            content: Contenido de la interacción
            level: Nivel de trazabilidad
            **metadata: Metadata adicional (cognitive_intent, etc.)

        Returns:
            CognitiveTrace creada
        """
        trace = CognitiveTrace(
            id=f"trace_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            student_id=student_id,
            activity_id=activity_id,
            trace_level=level,
            interaction_type=interaction_type,
            content=content,
            **metadata
        )

        # Persistir usando repositorio si está disponible
        if self.trace_repository:
            self.trace_repository.create(trace)

        return trace

    def create_sequence(
        self,
        student_id: str,
        activity_id: str,
        sequence_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> TraceSequence:
        """Crea una nueva secuencia de trazas"""
        if not sequence_id:
            sequence_id = f"seq_{student_id}_{activity_id}_{datetime.now().timestamp()}"

        sequence = TraceSequence(
            id=sequence_id,
            student_id=student_id,
            activity_id=activity_id,
            session_id=session_id
        )

        # Persistir usando repositorio si está disponible
        if self.sequence_repository:
            self.sequence_repository.create(sequence)

        return sequence

    def get_sequence(self, sequence_id: str) -> Optional[TraceSequence]:
        """Obtiene una secuencia por ID"""
        if self.sequence_repository:
            db_sequence = self.sequence_repository.get_by_id(sequence_id)
            if db_sequence:
                # Convertir de ORM a Pydantic
                return TraceSequence(
                    id=db_sequence.id,
                    session_id=db_sequence.session_id,
                    student_id=db_sequence.student_id,
                    activity_id=db_sequence.activity_id,
                    start_time=db_sequence.start_time,
                    end_time=db_sequence.end_time,
                    reasoning_path=db_sequence.reasoning_path or [],
                    strategy_changes=db_sequence.strategy_changes or [],
                    ai_dependency_score=db_sequence.ai_dependency_score or 0.0,
                    traces=[]  # Las trazas se cargan por demanda
                )
        return None

    def get_student_traces(
        self,
        student_id: str,
        activity_id: Optional[str] = None,
        level: Optional[TraceLevel] = None
    ) -> List[CognitiveTrace]:
        """Obtiene todas las trazas de un estudiante"""
        if self.trace_repository:
            # Usar repositorio para obtener trazas
            db_traces = self.trace_repository.get_by_student(student_id, limit=1000)

            # Convertir de ORM a Pydantic y filtrar
            traces = []
            for db_trace in db_traces:
                # Aplicar filtros
                if activity_id and db_trace.activity_id != activity_id:
                    continue
                if level and db_trace.trace_level != level.value:
                    continue

                # Convertir a CognitiveTrace
                trace = CognitiveTrace(
                    id=db_trace.id,
                    session_id=db_trace.session_id,
                    timestamp=db_trace.created_at,
                    student_id=db_trace.student_id,
                    activity_id=db_trace.activity_id,
                    trace_level=TraceLevel(db_trace.trace_level),
                    interaction_type=InteractionType(db_trace.interaction_type),
                    content=db_trace.content,
                    context=db_trace.context,
                    # NOTE: ORM uses trace_metadata, domain model uses metadata
                    metadata=db_trace.trace_metadata,
                    cognitive_intent=db_trace.cognitive_intent,
                    decision_justification=db_trace.decision_justification,
                    alternatives_considered=db_trace.alternatives_considered
                )
                traces.append(trace)

            return traces

        return []

    def reconstruct_cognitive_path(
        self,
        sequence_id: str
    ) -> Dict[str, Any]:
        """
        Reconstruye el camino cognitivo completo de una secuencia

        Returns:
            Mapa del proceso de razonamiento con:
            - Fases cognitivas
            - Decisiones clave
            - Cambios de estrategia
            - Intervenciones
        """
        sequence = self.get_sequence(sequence_id)
        if not sequence:
            return {"error": "Sequence not found"}

        return {
            "sequence_id": sequence_id,
            "student_id": sequence.student_id,
            "activity_id": sequence.activity_id,
            "duration": (sequence.end_time - sequence.start_time).total_seconds() if sequence.end_time else None,
            "total_interactions": len(sequence.traces),
            "cognitive_path": sequence.get_cognitive_path(),
            "phases": self._identify_cognitive_phases(sequence),
            "key_decisions": self._extract_key_decisions(sequence),
            "strategy_changes": sequence.strategy_changes,
            "ai_dependency_score": sequence.ai_dependency_score,
            "timeline": self._build_timeline(sequence)
        }

    def _identify_cognitive_phases(self, sequence: TraceSequence) -> List[Dict[str, Any]]:
        """Identifica las fases cognitivas en la secuencia"""
        phases = []
        current_phase = None

        for trace in sequence.traces:
            # Detectar fase basándose en contenido y tipo
            detected_phase = self._detect_phase(trace)

            if detected_phase != current_phase:
                phases.append({
                    "phase": detected_phase,
                    "start_time": trace.timestamp,
                    "trace_id": trace.id
                })
                current_phase = detected_phase

        return phases

    def _detect_phase(self, trace: CognitiveTrace) -> str:
        """Detecta la fase cognitiva de una traza"""
        content_lower = trace.content.lower()

        if any(kw in content_lower for kw in ["plan", "voy a", "estrategia"]):
            return "planificacion"
        elif any(kw in content_lower for kw in ["entiendo", "qué es", "explica"]):
            return "exploracion"
        elif any(kw in content_lower for kw in ["implemento", "código", "función"]):
            return "implementacion"
        elif any(kw in content_lower for kw in ["error", "bug", "falla"]):
            return "depuracion"
        elif any(kw in content_lower for kw in ["prueba", "test", "funciona"]):
            return "validacion"
        else:
            return "indefinido"

    def _extract_key_decisions(self, sequence: TraceSequence) -> List[Dict[str, Any]]:
        """Extrae decisiones clave con justificaciones"""
        decisions = []

        for trace in sequence.traces:
            if trace.decision_justification:
                decisions.append({
                    "trace_id": trace.id,
                    "timestamp": trace.timestamp,
                    "decision": trace.content[:100],
                    "justification": trace.decision_justification,
                    "alternatives_considered": trace.alternatives_considered
                })

        return decisions

    def _build_timeline(self, sequence: TraceSequence) -> List[Dict[str, Any]]:
        """Construye timeline visual de la secuencia"""
        return [
            {
                "timestamp": trace.timestamp.isoformat(),
                "type": trace.interaction_type.value,
                "level": trace.trace_level.value,
                "content_preview": trace.content[:50] + "..." if len(trace.content) > 50 else trace.content
            }
            for trace in sequence.traces
        ]

    def capture_design_decision(
        self,
        student_id: str,
        activity_id: str,
        session_id: str,
        decision: str,
        justification: str,
        alternatives_considered: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> CognitiveTrace:
        """
        Captura una decisión de diseño con su justificación (HU-EST-005)

        Args:
            student_id: ID del estudiante
            activity_id: ID de la actividad
            session_id: ID de la sesión
            decision: La decisión tomada
            justification: Por qué se tomó esa decisión
            alternatives_considered: Alternativas que el estudiante consideró
            context: Contexto adicional

        Returns:
            CognitiveTrace con la decisión registrada
        """
        trace = CognitiveTrace(
            id=f"decision_{datetime.now().timestamp()}",
            session_id=session_id,
            timestamp=datetime.now(),
            student_id=student_id,
            activity_id=activity_id,
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            content=decision,
            cognitive_intent="JUSTIFICATION",  # Marcador específico para decisiones
            decision_justification=justification,
            alternatives_considered=alternatives_considered or [],
            context=context or {},
            metadata={
                "is_design_decision": True,
                "has_justification": bool(justification),
                "alternatives_count": len(alternatives_considered or [])
            }
        )

        # Persistir
        if self.trace_repository:
            self.trace_repository.create(trace)

        return trace

    def detect_unjustified_decisions(
        self,
        session_id: str,
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Detecta decisiones sin justificación o con justificación débil (HU-EST-005)

        Args:
            session_id: ID de la sesión a analizar
            threshold: Ratio mínimo de decisiones justificadas esperado (0.7 = 70%)

        Returns:
            Análisis de justificaciones con alertas si aplica
        """
        if not self.trace_repository:
            return {"error": "Repository not available"}

        # Obtener todas las trazas de la sesión
        traces = self.trace_repository.get_by_session(session_id)

        # Identificar decisiones (trazas donde se toman decisiones de diseño)
        decision_keywords = [
            "elegí", "decidí", "voy a usar", "implemento con",
            "opto por", "selecciono", "usaré", "aplico"
        ]

        decisions = []
        unjustified = []

        for trace in traces:
            content_lower = trace.content.lower()

            # Detectar si es una decisión
            is_decision = any(kw in content_lower for kw in decision_keywords)

            if is_decision:
                has_justification = bool(trace.decision_justification and len(trace.decision_justification) > 10)

                decisions.append({
                    "trace_id": trace.id,
                    "decision": trace.content[:100],
                    "has_justification": has_justification,
                    "justification": trace.decision_justification
                })

                if not has_justification:
                    unjustified.append({
                        "trace_id": trace.id,
                        "decision": trace.content[:100],
                        "timestamp": trace.created_at.isoformat()
                    })

        # Calcular ratios
        total_decisions = len(decisions)
        justified_count = sum(1 for d in decisions if d["has_justification"])
        justification_ratio = justified_count / total_decisions if total_decisions > 0 else 1.0

        # Determinar si hay alerta
        alert_level = None
        if justification_ratio < threshold:
            if justification_ratio < 0.3:
                alert_level = "HIGH"
            elif justification_ratio < 0.5:
                alert_level = "MEDIUM"
            else:
                alert_level = "LOW"

        return {
            "session_id": session_id,
            "total_decisions": total_decisions,
            "justified_decisions": justified_count,
            "unjustified_decisions": len(unjustified),
            "justification_ratio": justification_ratio,
            "threshold": threshold,
            "alert": alert_level is not None,
            "alert_level": alert_level,
            "unjustified_list": unjustified,
            "recommendation": self._generate_justification_recommendation(justification_ratio) if alert_level else None
        }

    async def _analyze_cognitive_path_with_llm(self, sequence: TraceSequence) -> Optional[Dict[str, Any]]:
        """Usa LLM para análisis profundo del camino cognitivo"""
        if not self.llm_provider:
            return None

        # Construir resumen de trazas
        traces_summary = self._build_traces_summary_for_llm(sequence.traces[:20])

        system_prompt = """Eres un experto en análisis cognitivo de procesos de aprendizaje.
        
Analiza el proceso de razonamiento del estudiante e identifica:
        1. Fases cognitivas (exploración, planificación, implementación, validación)
        2. Estrategias de resolución utilizadas
        3. Momentos de cambio de estrategia y por qué
        4. Calidad del razonamiento (superficial vs profundo)
        
        Responde SOLO con JSON en este formato:
        {
            "phases": [{"phase": "exploración|planificación|implementación|validación", "description": "..."}],
            "strategies": ["estrategia1", "estrategia2"],
            "strategy_changes": [{"from": "...", "to": "...", "reason": "..."}],
            "reasoning_quality": "superficial|moderado|profundo",
            "insights": ["insight1", "insight2"]
        }"""

        user_prompt = f"""Analiza el proceso cognitivo del estudiante:

Estudiante: {sequence.student_id}
Actividad: {sequence.activity_id}
Duración: {(sequence.end_time - sequence.start_time).total_seconds() if sequence.end_time else 'en curso'} segundos

Trazas del proceso:
{traces_summary}

Identifica patrones cognitivos, estrategias y calidad del razonamiento."""

        messages = [
            LLMMessage(role=LLMRole.SYSTEM, content=system_prompt),
            LLMMessage(role=LLMRole.USER, content=user_prompt)
        ]

        try:
            response = await self.llm_provider.generate(
                messages=messages,
                temperature=0.4,
                max_tokens=700,
                is_code_analysis=False  # Usar Flash para análisis de trazabilidad
            )

            # Extraer JSON
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None

        except Exception as e:
            print(f"Error en análisis LLM cognitivo: {e}")
            return None

    def _build_traces_summary_for_llm(self, traces: List[CognitiveTrace]) -> str:
        """Construye resumen de trazas para análisis LLM"""
        summary_lines = []
        for i, trace in enumerate(traces, 1):
            summary_lines.append(
                f"{i}. [{trace.interaction_type.value}] {trace.content[:120]}..."
                + (f" | Justificación: {trace.decision_justification[:50]}..." if trace.decision_justification else "")
            )
        return "\n".join(summary_lines)

    def _generate_justification_recommendation(self, ratio: float) -> str:
        """Genera recomendación según el ratio de justificación"""
        if ratio < 0.3:
            return (
                "CRÍTICO: Muy pocas decisiones están justificadas (<30%). "
                "El docente debe exigir explícitamente que el estudiante documente "
                "POR QUÉ toma cada decisión de diseño."
            )
        elif ratio < 0.5:
            return (
                "MODERADO: Menos de la mitad de las decisiones están justificadas. "
                "Se recomienda solicitar al estudiante que justifique sus elecciones "
                "y considere alternativas."
            )
        else:
            return (
                "LEVE: Hay decisiones sin justificar, pero la mayoría están documentadas. "
                "Reforzar la importancia de justificar todas las decisiones clave."
            )

    async def reconstruct_cognitive_path_async(
        self,
        sequence_id: str
    ) -> Dict[str, Any]:
        """Versión async que usa LLM para análisis cognitivo profundo"""
        # Reconstrucción base
        base_reconstruction = self.reconstruct_cognitive_path(sequence_id)
        
        if "error" in base_reconstruction:
            return base_reconstruction

        sequence = self.get_sequence(sequence_id)
        if not sequence:
            return {"error": "Sequence not found"}

        # Análisis LLM (opcional)
        llm_analysis = None
        if self.llm_provider:
            llm_analysis = await self._analyze_cognitive_path_with_llm(sequence)

        # Combinar análisis base + LLM
        result = base_reconstruction.copy()
        if llm_analysis:
            result["llm_cognitive_analysis"] = llm_analysis
            result["enhanced_phases"] = llm_analysis.get("phases", [])
            result["identified_strategies"] = llm_analysis.get("strategies", [])
            result["reasoning_quality"] = llm_analysis.get("reasoning_quality")
            result["cognitive_insights"] = llm_analysis.get("insights", [])

        return result

    def export_for_evaluation(
        self,
        sequence_id: str,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Exporta trazas para evaluación docente

        Args:
            sequence_id: ID de la secuencia
            format: Formato de exportación

        Returns:
            Datos estructurados para evaluación
        """
        cognitive_path = self.reconstruct_cognitive_path(sequence_id)
        sequence = self.get_sequence(sequence_id)

        if not sequence:
            return {"error": "Sequence not found"}

        return {
            "export_metadata": {
                "sequence_id": sequence_id,
                "export_date": datetime.now().isoformat(),
                "format": format
            },
            "student_info": {
                "student_id": sequence.student_id,
                "activity_id": sequence.activity_id
            },
            "cognitive_reconstruction": cognitive_path,
            "full_traces": [
                {
                    "id": t.id,
                    "timestamp": t.timestamp.isoformat(),
                    "type": t.interaction_type.value,
                    "content": t.content,
                    "cognitive_intent": t.cognitive_intent,
                    "decision_justification": t.decision_justification
                }
                for t in sequence.traces
            ]
        }