"""
Risk Analyzer - Analiza y gestiona riesgos cognitivos, éticos y técnicos

Extraído de AIGateway como parte de la refactorización God Class → componentes especializados.
"""
from typing import Dict, Any, Optional, List
import logging
import uuid

from ..models.trace import CognitiveTrace, TraceSequence
from ..models.risk import Risk, RiskType, RiskLevel, RiskDimension, RiskReport
from ..database.repositories import RiskRepository
from ..agents.risk_analyst import AnalistaRiesgoAgent

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """
    Analiza y gestiona detección de riesgos (AR-IA).

    Responsabilidad: Análisis de riesgos cognitivos, éticos, epistémicos, técnicos y de gobernanza.

    Extracted from: AIGateway (God Class refactoring)
    """

    def __init__(
        self,
        risk_repo: RiskRepository,
        risk_agent: AnalistaRiesgoAgent,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa el analizador de riesgos.

        Args:
            risk_repo: Repositorio de riesgos
            risk_agent: Agente AR-IA para análisis
            config: Configuración adicional
        """
        self.risk_repo = risk_repo
        self.risk_agent = risk_agent
        self.config = config or {}

        logger.info("RiskAnalyzer initialized")

    def analyze_interaction(
        self,
        session_id: str,
        input_trace: CognitiveTrace,
        response_trace: CognitiveTrace,
        classification: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Risk]:
        """
        Analiza una interacción individual para detectar riesgos.

        Args:
            session_id: ID de la sesión
            input_trace: Traza de entrada del estudiante
            response_trace: Traza de respuesta del agente
            classification: Clasificación CRPE
            context: Contexto adicional

        Returns:
            Lista de riesgos detectados
        """
        logger.debug(
            "Analyzing interaction for risks",
            extra={
                "session_id": session_id,
                "input_trace_id": input_trace.id,
                "response_trace_id": response_trace.id,
                "classification_type": classification.get("type", "unknown")
            }
        )

        detected_risks = []

        # Análisis rápido de delegación total
        delegation_risk = self._check_delegation_risk(
            session_id, input_trace, response_trace, classification
        )
        if delegation_risk:
            detected_risks.append(delegation_risk)
            self.risk_repo.create(delegation_risk)

        # Análisis de razonamiento superficial
        superficial_risk = self._check_superficial_reasoning(
            session_id, input_trace, classification
        )
        if superficial_risk:
            detected_risks.append(superficial_risk)
            self.risk_repo.create(superficial_risk)

        # Análisis de integridad académica
        integrity_risk = self._check_academic_integrity(
            session_id, input_trace, context or {}
        )
        if integrity_risk:
            detected_risks.append(integrity_risk)
            self.risk_repo.create(integrity_risk)

        if detected_risks:
            logger.warning(
                f"Detected {len(detected_risks)} risks in interaction",
                extra={
                    "session_id": session_id,
                    "risk_count": len(detected_risks),
                    "risk_types": [r.risk_type.value for r in detected_risks]
                }
            )
        else:
            logger.debug(
                "No risks detected in interaction",
                extra={"session_id": session_id}
            )

        return detected_risks

    def analyze_session(
        self,
        trace_sequence: TraceSequence,
        context: Optional[Dict[str, Any]] = None
    ) -> RiskReport:
        """
        Analiza una sesión completa y genera reporte de riesgos.

        Este método delega al agente AR-IA para análisis profundo de:
        - Riesgos cognitivos (RC)
        - Riesgos éticos (RE)
        - Riesgos epistémicos (REp)
        - Riesgos técnicos (RT)
        - Riesgos de gobernanza (RG)

        Args:
            trace_sequence: Secuencia completa de trazas
            context: Contexto adicional

        Returns:
            RiskReport completo
        """
        logger.info(
            "Analyzing complete session for risks",
            extra={
                "session_id": trace_sequence.session_id,
                "trace_count": len(trace_sequence.traces),
                "student_id": trace_sequence.student_id
            }
        )

        # Delegar análisis profundo al agente AR-IA
        report = self.risk_agent.analyze_session(
            trace_sequence=trace_sequence,
            context=context
        )

        # Persistir riesgos detectados
        for risk in report.risks:
            try:
                self.risk_repo.create(risk)
            except Exception as e:
                logger.error(
                    f"Failed to persist risk: {type(e).__name__}: {str(e)}",
                    exc_info=True,
                    extra={
                        "risk_id": risk.id,
                        "risk_type": risk.risk_type.value,
                        "session_id": trace_sequence.session_id
                    }
                )

        logger.info(
            "Session risk analysis completed",
            extra={
                "session_id": trace_sequence.session_id,
                "total_risks": len(report.risks),
                "critical_risks": len([r for r in report.risks if r.risk_level == RiskLevel.CRITICAL]),
                "high_risks": len([r for r in report.risks if r.risk_level == RiskLevel.HIGH])
            }
        )

        return report

    def get_risk_report(
        self,
        student_id: str,
        activity_id: str
    ) -> Optional[RiskReport]:
        """
        Obtiene el reporte de riesgos desde BD.

        Args:
            student_id: ID del estudiante
            activity_id: ID de la actividad

        Returns:
            RiskReport o None si no hay riesgos
        """
        risks = self.risk_repo.get_by_student(student_id)

        # Filtrar por activity_id
        risks = [r for r in risks if r.activity_id == activity_id]

        if not risks:
            return None

        # Construir RiskReport desde BD
        report = RiskReport(
            id=f"report_{student_id}_{activity_id}",
            student_id=student_id,
            activity_id=activity_id
        )

        for db_risk in risks:
            risk = Risk(
                id=db_risk.id,
                session_id=db_risk.session_id,
                student_id=db_risk.student_id,
                activity_id=db_risk.activity_id,
                risk_type=RiskType(db_risk.risk_type),
                risk_level=RiskLevel(db_risk.risk_level),
                dimension=RiskDimension(db_risk.dimension),
                description=db_risk.description or "",
                evidence=db_risk.evidence or [],
                trace_ids=db_risk.trace_ids or [],
                recommendations=db_risk.recommendations or [],
                resolved=db_risk.resolved,
                resolution_notes=db_risk.resolution_notes
            )
            report.add_risk(risk)

        logger.debug(
            f"Risk report retrieved for {student_id}/{activity_id}",
            extra={
                "student_id": student_id,
                "activity_id": activity_id,
                "risk_count": len(report.risks)
            }
        )

        return report

    def persist_risk(
        self,
        student_id: str,
        activity_id: str,
        risk_type: RiskType,
        risk_level: RiskLevel,
        dimension: RiskDimension,
        description: str,
        evidence: List[str],
        trace_ids: List[str],
        recommendations: Optional[List[str]] = None,
        **kwargs
    ) -> Optional[Risk]:
        """
        Registra un riesgo detectado en BD.

        Args:
            student_id: ID del estudiante
            activity_id: ID de la actividad
            risk_type: Tipo de riesgo
            risk_level: Nivel de severidad
            dimension: Dimensión de riesgo
            description: Descripción del riesgo
            evidence: Evidencia del riesgo
            trace_ids: IDs de trazas relacionadas
            recommendations: Recomendaciones para mitigar
            **kwargs: Campos adicionales

        Returns:
            Risk creado o None si falló
        """
        risk = Risk(
            id=str(uuid.uuid4()),
            student_id=student_id,
            activity_id=activity_id,
            risk_type=risk_type,
            risk_level=risk_level,
            dimension=dimension,
            description=description,
            evidence=evidence,
            trace_ids=trace_ids,
            recommendations=recommendations or [],
            **kwargs
        )

        try:
            self.risk_repo.create(risk)
            logger.info(
                f"Risk persisted: {risk.risk_type.value}",
                extra={
                    "risk_id": risk.id,
                    "student_id": student_id,
                    "risk_level": risk_level.value,
                    "dimension": dimension.value
                }
            )
            return risk
        except Exception as e:
            logger.error(
                f"Failed to persist risk: {type(e).__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "student_id": student_id,
                    "risk_type": risk_type.value
                }
            )
            return None

    # ========== Private Helper Methods ==========

    def _check_delegation_risk(
        self,
        session_id: str,
        input_trace: CognitiveTrace,
        response_trace: CognitiveTrace,
        classification: Dict[str, Any]
    ) -> Optional[Risk]:
        """Verifica riesgo de delegación total."""
        prompt = input_trace.content.lower()

        # Patrones de delegación total
        delegation_patterns = [
            "dame el código",
            "escribe el código",
            "resuelve esto",
            "hazlo por mi",
            "hacelo por mi",
            "genera el código completo",
            "completa el código"
        ]

        is_delegation = any(pattern in prompt for pattern in delegation_patterns)

        if is_delegation:
            return Risk(
                id=str(uuid.uuid4()),
                session_id=session_id,
                student_id=input_trace.student_id,
                activity_id=input_trace.activity_id,
                risk_type=RiskType.COGNITIVE_DELEGATION,
                risk_level=RiskLevel.HIGH,
                dimension=RiskDimension.COGNITIVE,
                description="Delegación total detectada - solicitud de código completo sin razonamiento propio",
                evidence=[prompt],
                trace_ids=[input_trace.id],
                recommendations=[
                    "Descomponer el problema en pasos más pequeños",
                    "Explicar el razonamiento antes de solicitar ayuda",
                    "Intentar resolver subproblemas de forma incremental"
                ]
            )

        return None

    def _check_superficial_reasoning(
        self,
        session_id: str,
        input_trace: CognitiveTrace,
        classification: Dict[str, Any]
    ) -> Optional[Risk]:
        """Verifica riesgo de razonamiento superficial."""
        prompt = input_trace.content

        # Prompts muy cortos sin contexto ni razonamiento
        if len(prompt) < 20:
            return Risk(
                id=str(uuid.uuid4()),
                session_id=session_id,
                student_id=input_trace.student_id,
                activity_id=input_trace.activity_id,
                risk_type=RiskType.LACK_JUSTIFICATION,
                risk_level=RiskLevel.MEDIUM,
                dimension=RiskDimension.COGNITIVE,
                description="Consulta muy breve sin contexto ni razonamiento previo",
                evidence=[prompt],
                trace_ids=[input_trace.id],
                recommendations=[
                    "Proporcionar contexto del problema",
                    "Explicar qué se intentó hasta ahora",
                    "Describir el razonamiento actual"
                ]
            )

        return None

    def _check_academic_integrity(
        self,
        session_id: str,
        input_trace: CognitiveTrace,
        context: Dict[str, Any]
    ) -> Optional[Risk]:
        """Verifica riesgo de integridad académica."""
        # Placeholder - en producción verificaría patrones de plagio,
        # uso no declarado de IA, etc.

        # Ejemplo: Si el código del contexto parece ser copiado sin modificación
        if context.get("code_snippet") and len(context.get("code_snippet", "")) > 500:
            # Verificación básica - en producción usaría análisis más sofisticado
            pass

        return None
