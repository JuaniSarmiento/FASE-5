"""
Submodelo 4: Analista de Riesgo Cognitivo y Ético (AR-IA)

Supervisa, detecta y clasifica riesgos cognitivos, éticos y epistémicos
"""
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..models.trace import CognitiveTrace, TraceSequence, InteractionType
from ..models.risk import Risk, RiskType, RiskLevel, RiskDimension, RiskReport


class AnalistaRiesgoAgent:
    """
    AR-IA: Analista de Riesgo Cognitivo y Ético

    Monitorea 5 dimensiones de riesgo:
    1. Riesgos Cognitivos (RC): delegación, razonamiento superficial
    2. Riesgos Éticos (RE): integridad académica
    3. Riesgos Epistémicos (REp): errores conceptuales, aceptación acrítica
    4. Riesgos Técnicos (RT): vulnerabilidades, mala calidad
    5. Riesgos de Gobernanza (RG): violación de políticas

    Basado en:
    - UNESCO (2021), OECD (2019), IEEE (2019)
    - ISO/IEC 23894:2023 (Risk Management in AI)
    - ISO/IEC 42001:2023 (AI Management System)
    """

    def __init__(self, llm_provider=None, config: Optional[Dict[str, Any]] = None):
        self.llm_provider = llm_provider
        self.config = config or {}

        # Umbrales de riesgo configurables
        self.thresholds = {
            "ai_dependency": self.config.get("ai_dependency_threshold", 0.7),
            "delegation_consecutive": self.config.get("delegation_threshold", 3),
            "no_justification_ratio": self.config.get("no_justification_threshold", 0.6),
        }

    def analyze_session(
        self,
        trace_sequence: TraceSequence,
        context: Optional[Dict[str, Any]] = None
    ) -> RiskReport:
        """
        Analiza una sesión completa y genera reporte de riesgos

        Args:
            trace_sequence: Secuencia de trazas a analizar
            context: Contexto adicional

        Returns:
            RiskReport con todos los riesgos detectados
        """
        report = RiskReport(
            id=f"risk_report_{trace_sequence.id}",
            student_id=trace_sequence.student_id,
            activity_id=trace_sequence.activity_id
        )

        # Analizar cada dimensión de riesgo
        self._analyze_cognitive_risks(trace_sequence, report)
        self._analyze_ethical_risks(trace_sequence, report)
        self._analyze_epistemic_risks(trace_sequence, report)
        self._analyze_technical_risks(trace_sequence, report)
        self._analyze_governance_risks(trace_sequence, report)

        # Generar evaluación general
        report.overall_assessment = self._generate_overall_assessment(report)
        report.priority_interventions = self._generate_priority_interventions(report)
        report.trends = self._analyze_trends(trace_sequence)

        return report

    def _analyze_cognitive_risks(
        self,
        trace_sequence: TraceSequence,
        report: RiskReport
    ) -> None:
        """Analiza riesgos cognitivos (RC)"""
        traces = trace_sequence.traces

        # RC1: Delegación total
        delegation_count = self._count_delegation_attempts(traces)
        if delegation_count >= self.thresholds["delegation_consecutive"]:
            risk = Risk(
                id=f"risk_cog_delegation_{trace_sequence.id}",
                session_id=trace_sequence.session_id,
                student_id=trace_sequence.student_id,
                activity_id=trace_sequence.activity_id,
                risk_type=RiskType.COGNITIVE_DELEGATION,
                risk_level=RiskLevel.HIGH,
                dimension=RiskDimension.COGNITIVE,
                description=(
                    f"Se detectaron {delegation_count} intentos de delegación total "
                    "sin descomposición del problema"
                ),
                evidence=[
                    t.content for t in traces
                    if self._is_delegation(t.content)
                ][:3],
                trace_ids=[t.id for t in traces if self._is_delegation(t.content)],
                root_cause="Tendencia a delegar la resolución completa a la IA",
                recommendations=[
                    "Solicitar descomposición explícita del problema",
                    "Exigir justificación de cada paso",
                    "Reducir nivel de ayuda del tutor temporalmente"
                ],
                pedagogical_intervention=(
                    "Modo socrático estricto: solo preguntas, sin pistas directas"
                )
            )
            report.add_risk(risk)

        # RC2: Dependencia excesiva de IA
        if trace_sequence.ai_dependency_score > self.thresholds["ai_dependency"]:
            risk = Risk(
                id=f"risk_cog_dependency_{trace_sequence.id}",
                session_id=trace_sequence.session_id,
                student_id=trace_sequence.student_id,
                activity_id=trace_sequence.activity_id,
                risk_type=RiskType.AI_DEPENDENCY,
                risk_level=RiskLevel.MEDIUM,
                dimension=RiskDimension.COGNITIVE,
                description=(
                    f"Nivel de dependencia de IA alto: "
                    f"{trace_sequence.ai_dependency_score:.2%}"
                ),
                evidence=[],
                trace_ids=[],
                recommendations=[
                    "Fomentar resolución autónoma con menos asistencia de IA",
                    "Asignar ejercicios sin acceso a IA para desarrollar autonomía"
                ]
            )
            report.add_risk(risk)

        # RC3: Falta de justificación
        justification_ratio = self._calculate_justification_ratio(traces)
        if justification_ratio < (1 - self.thresholds["no_justification_ratio"]):
            risk = Risk(
                id=f"risk_cog_justification_{trace_sequence.id}",
                session_id=trace_sequence.session_id,
                student_id=trace_sequence.student_id,
                activity_id=trace_sequence.activity_id,
                risk_type=RiskType.LACK_JUSTIFICATION,
                risk_level=RiskLevel.MEDIUM,
                dimension=RiskDimension.COGNITIVE,
                description=(
                    f"Baja tasa de justificación de decisiones: "
                    f"{justification_ratio:.2%}"
                ),
                evidence=[],
                trace_ids=[],
                recommendations=[
                    "Exigir explícitamente justificaciones",
                    "Usar rúbricas que valoren el razonamiento sobre el código"
                ]
            )
            report.add_risk(risk)

    def _analyze_ethical_risks(
        self,
        trace_sequence: TraceSequence,
        report: RiskReport
    ) -> None:
        """Analiza riesgos éticos (RE)"""
        traces = trace_sequence.traces
        
        # RE1: Código sospechoso (tiempo < 5s y longitud > 100 chars)
        # Buscar pares de prompts y respuestas rápidas con código largo
        for i, trace in enumerate(traces):
            if trace.interaction_type == InteractionType.STUDENT_PROMPT and i + 1 < len(traces):
                next_trace = traces[i + 1]
                
                # Si la siguiente traza es una respuesta/código del estudiante
                if next_trace.student_id == trace.student_id and \
                   next_trace.interaction_type in [InteractionType.STUDENT_CODE_SUBMISSION, InteractionType.STUDENT_PROMPT]:
                    
                    # Calcular tiempo entre trazas
                    time_diff = (next_trace.timestamp - trace.timestamp).total_seconds()
                    
                    # Verificar si es código (contiene palabras clave de programación)
                    is_code = self._looks_like_code(next_trace.content)
                    code_length = len(next_trace.content)
                    
                    # Detectar código sospechoso: tiempo < 5s y longitud > 100 chars
                    if time_diff < 5 and code_length > 100 and is_code:
                        risk = Risk(
                            id=f"risk_eth_suspicious_code_{trace_sequence.id}_{i}",
                            session_id=trace_sequence.session_id,
                            student_id=trace_sequence.student_id,
                            activity_id=trace_sequence.activity_id,
                            risk_type=RiskType.ACADEMIC_INTEGRITY,
                            risk_level=RiskLevel.HIGH,
                            dimension=RiskDimension.ETHICAL,
                            description=(
                                f"Código sospechoso detectado: {code_length} caracteres "
                                f"enviados en {time_diff:.1f} segundos (< 5s). "
                                "Posible copia de fuente externa."
                            ),
                            evidence=[
                                f"Prompt: {trace.content[:100]}...",
                                f"Código: {next_trace.content[:100]}..."
                            ],
                            trace_ids=[trace.id, next_trace.id],
                            root_cause="Tiempo de respuesta incompatible con escritura humana de código",
                            recommendations=[
                                "Revisar fuente del código enviado",
                                "Solicitar explicación detallada del código",
                                "Considerar entrevista presencial para verificar comprensión"
                            ],
                            pedagogical_intervention=(
                                "Solicitar que explique línea por línea el código enviado"
                            )
                        )
                        report.add_risk(risk)

    def _analyze_epistemic_risks(
        self,
        trace_sequence: TraceSequence,
        report: RiskReport
    ) -> None:
        """Analiza riesgos epistémicos (REp)"""
        traces = trace_sequence.traces

        # REp1: Aceptación acrítica de salidas de IA
        uncritical_acceptance_count = sum(
            1 for t in traces
            if t.interaction_type == InteractionType.AI_RESPONSE
            and not any(
                followup.interaction_type == InteractionType.AI_CRITIQUE
                for followup in traces
                if followup.timestamp > t.timestamp
            )
        )

        if uncritical_acceptance_count > 3:
            risk = Risk(
                id=f"risk_epis_uncritical_{trace_sequence.id}",
                session_id=trace_sequence.session_id,
                student_id=trace_sequence.student_id,
                activity_id=trace_sequence.activity_id,
                risk_type=RiskType.UNCRITICAL_ACCEPTANCE,
                risk_level=RiskLevel.MEDIUM,
                dimension=RiskDimension.EPISTEMIC,
                description=(
                    f"Aceptación acrítica de {uncritical_acceptance_count} "
                    "respuestas de IA sin cuestionamiento"
                ),
                evidence=[],
                trace_ids=[],
                recommendations=[
                    "Promover revisión crítica de salidas de IA",
                    "Solicitar que identifique posibles errores en respuestas de IA"
                ]
            )
            report.add_risk(risk)

    def _analyze_technical_risks(
        self,
        trace_sequence: TraceSequence,
        report: RiskReport
    ) -> None:
        """
        Analiza riesgos técnicos (RT)

        Detecta:
        - RT1: Código con patrones de vulnerabilidad
        - RT2: Mala calidad de código (repetición excesiva)
        - RT3: Falta de manejo de errores
        """
        traces = trace_sequence.traces

        # RT1: Detectar patrones de código potencialmente inseguros
        security_patterns = [
            ("sql injection", ["execute(", "cursor.execute", "SELECT * FROM", "' OR '", "\" OR \""]),
            ("hardcoded secrets", ["password=", "api_key=", "secret=", "token="]),
            ("eval/exec", ["eval(", "exec(", "compile("]),
        ]

        for trace in traces:
            if trace.interaction_type == InteractionType.STUDENT_CODE_SUBMISSION:
                content_lower = trace.content.lower()

                for vuln_name, patterns in security_patterns:
                    if any(p.lower() in content_lower for p in patterns):
                        risk = Risk(
                            id=f"risk_tech_{vuln_name.replace(' ', '_')}_{trace.id}",
                            session_id=trace_sequence.session_id,
                            student_id=trace_sequence.student_id,
                            activity_id=trace_sequence.activity_id,
                            risk_type=RiskType.SECURITY_VULNERABILITY,
                            risk_level=RiskLevel.MEDIUM,
                            dimension=RiskDimension.TECHNICAL,
                            description=(
                                f"Posible vulnerabilidad detectada: {vuln_name}. "
                                "El código contiene patrones que podrían indicar problemas de seguridad."
                            ),
                            evidence=[trace.content[:200] + "..."] if len(trace.content) > 200 else [trace.content],
                            trace_ids=[trace.id],
                            recommendations=[
                                f"Revisar el código para posibles problemas de {vuln_name}",
                                "Consultar OWASP Top 10 para mejores prácticas",
                                "Usar parametrized queries en lugar de string concatenation"
                            ]
                        )
                        report.add_risk(risk)
                        break  # Solo reportar una vulnerabilidad por traza

        # RT2: Detectar código repetitivo (DRY violation)
        code_submissions = [
            t for t in traces
            if t.interaction_type == InteractionType.STUDENT_CODE_SUBMISSION
        ]

        if len(code_submissions) >= 3:
            # Buscar bloques de código duplicados
            duplicate_count = 0
            for i, submission in enumerate(code_submissions[:-1]):
                for later_submission in code_submissions[i+1:]:
                    # Si más del 70% del código es igual
                    if self._calculate_similarity(submission.content, later_submission.content) > 0.7:
                        duplicate_count += 1

            if duplicate_count > 2:
                risk = Risk(
                    id=f"risk_tech_dry_{trace_sequence.id}",
                    session_id=trace_sequence.session_id,
                    student_id=trace_sequence.student_id,
                    activity_id=trace_sequence.activity_id,
                    risk_type=RiskType.POOR_CODE_QUALITY,
                    risk_level=RiskLevel.LOW,
                    dimension=RiskDimension.TECHNICAL,
                    description=(
                        f"Se detectaron {duplicate_count} bloques de código muy similares. "
                        "Posible violación del principio DRY (Don't Repeat Yourself)."
                    ),
                    evidence=[],
                    trace_ids=[t.id for t in code_submissions],
                    recommendations=[
                        "Refactorizar código duplicado en funciones reutilizables",
                        "Revisar principios de clean code",
                        "Identificar patrones comunes para abstraer"
                    ]
                )
                report.add_risk(risk)

    def _analyze_governance_risks(
        self,
        trace_sequence: TraceSequence,
        report: RiskReport
    ) -> None:
        """
        Analiza riesgos de gobernanza (RG)

        Detecta:
        - RG1: Uso excesivo de IA fuera de horarios permitidos
        - RG2: Sesiones demasiado largas (posible uso no supervisado)
        - RG3: Patrones de uso que violan políticas institucionales
        """
        traces = trace_sequence.traces

        if not traces:
            return

        # RG1: Verificar duración de sesión
        session_start = traces[0].timestamp
        session_end = traces[-1].timestamp
        session_duration_hours = (session_end - session_start).total_seconds() / 3600

        max_session_hours = self.config.get("max_session_hours", 4)
        if session_duration_hours > max_session_hours:
            risk = Risk(
                id=f"risk_gov_duration_{trace_sequence.id}",
                session_id=trace_sequence.session_id,
                student_id=trace_sequence.student_id,
                activity_id=trace_sequence.activity_id,
                risk_type=RiskType.POLICY_VIOLATION,
                risk_level=RiskLevel.LOW,
                dimension=RiskDimension.GOVERNANCE,
                description=(
                    f"Sesión excesivamente larga: {session_duration_hours:.1f} horas. "
                    f"El límite recomendado es {max_session_hours} horas."
                ),
                evidence=[
                    f"Inicio: {session_start.isoformat()}",
                    f"Fin: {session_end.isoformat()}"
                ],
                trace_ids=[traces[0].id, traces[-1].id],
                recommendations=[
                    "Tomar descansos regulares durante sesiones largas",
                    "Dividir el trabajo en sesiones más cortas",
                    "Revisar políticas de uso del sistema"
                ]
            )
            report.add_risk(risk)

        # RG2: Verificar frecuencia de interacciones (posible uso automatizado)
        if len(traces) > 10:
            time_gaps = []
            for i in range(1, len(traces)):
                gap = (traces[i].timestamp - traces[i-1].timestamp).total_seconds()
                time_gaps.append(gap)

            # Si muchas interacciones tienen gaps muy regulares (< 2s variación)
            if time_gaps:
                avg_gap = sum(time_gaps) / len(time_gaps)
                variance = sum((g - avg_gap) ** 2 for g in time_gaps) / len(time_gaps)

                # Varianza muy baja indica posible automatización
                if variance < 1 and avg_gap < 5:
                    risk = Risk(
                        id=f"risk_gov_automation_{trace_sequence.id}",
                        session_id=trace_sequence.session_id,
                        student_id=trace_sequence.student_id,
                        activity_id=trace_sequence.activity_id,
                        risk_type=RiskType.AUTOMATION_SUSPECTED,
                        risk_level=RiskLevel.MEDIUM,
                        dimension=RiskDimension.GOVERNANCE,
                        description=(
                            "Patrón de interacción sospechoso detectado. "
                            f"Promedio entre mensajes: {avg_gap:.1f}s con varianza muy baja ({variance:.2f}). "
                            "Posible uso de herramientas automatizadas."
                        ),
                        evidence=[
                            f"Promedio entre mensajes: {avg_gap:.1f}s",
                            f"Varianza: {variance:.2f}",
                            f"Total interacciones: {len(traces)}"
                        ],
                        trace_ids=[t.id for t in traces[:5]],  # Solo primeras 5 como evidencia
                        recommendations=[
                            "Verificar que las interacciones son genuinas",
                            "Revisar logs de actividad del usuario",
                            "Considerar implementar CAPTCHA si persiste"
                        ]
                    )
                    report.add_risk(risk)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calcula similitud simple entre dos textos.
        Retorna valor entre 0 y 1.
        """
        if not text1 or not text2:
            return 0.0

        # Tokenizar por palabras
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _is_delegation(self, content: str) -> bool:
        """Detecta si un prompt es delegación total"""
        delegation_signals = [
            "dame el código completo",
            "hacé todo",
            "resolvelo por mí",
            "código entero",
            "implementa todo",
            "haceme"
        ]
        return any(signal in content.lower() for signal in delegation_signals)

    def _looks_like_code(self, content: str) -> bool:
        """Detecta si el contenido parece ser código de programación"""
        code_indicators = [
            "def ", "class ", "function ", "return ", "import ",
            "if ", "else:", "for ", "while ", "{", "}", 
            "var ", "const ", "let ", "=>", "public ", "private ",
            "#include", "void ", "int ", "string "
        ]
        content_lower = content.lower()
        # Considerar código si tiene al menos 2 indicadores
        matches = sum(1 for indicator in code_indicators if indicator.lower() in content_lower)
        return matches >= 2

    def _count_delegation_attempts(self, traces: List[CognitiveTrace]) -> int:
        """Cuenta intentos de delegación"""
        return sum(1 for t in traces if self._is_delegation(t.content))

    def _calculate_justification_ratio(self, traces: List[CognitiveTrace]) -> float:
        """Calcula ratio de decisiones con justificación"""
        if not traces:
            return 0.0

        with_justification = sum(
            1 for t in traces
            if t.decision_justification is not None and t.decision_justification != ""
        )

        return with_justification / len(traces)

    def _generate_overall_assessment(self, report: RiskReport) -> str:
        """Genera evaluación general del perfil de riesgo"""
        if report.critical_risks > 0:
            return "CRÍTICO: Requiere intervención docente inmediata"
        elif report.high_risks > 2:
            return "ALTO: Requiere atención prioritaria y ajuste de estrategia pedagógica"
        elif report.high_risks > 0 or report.medium_risks > 3:
            return "MODERADO: Monitorear evolución y aplicar intervenciones preventivas"
        else:
            return "BAJO: Proceso dentro de parámetros esperados"

    def _generate_priority_interventions(self, report: RiskReport) -> List[str]:
        """Genera intervenciones prioritarias"""
        interventions = []

        # Priorizar por nivel
        critical_risks = [r for r in report.risks if r.risk_level == RiskLevel.CRITICAL]
        high_risks = [r for r in report.risks if r.risk_level == RiskLevel.HIGH]

        for risk in critical_risks + high_risks[:3]:  # Top 3 high risks
            if risk.pedagogical_intervention:
                interventions.append(risk.pedagogical_intervention)
            else:
                interventions.extend(risk.recommendations[:1])

        return interventions

    def _analyze_trends(self, trace_sequence: TraceSequence) -> Dict[str, Any]:
        """Analiza tendencias en el comportamiento del estudiante"""
        traces = trace_sequence.traces

        if len(traces) < 10:
            return {"insufficient_data": True}

        # Dividir en mitades para detectar mejora/empeoramiento
        mid = len(traces) // 2
        first_half = traces[:mid]
        second_half = traces[mid:]

        delegation_first = sum(1 for t in first_half if self._is_delegation(t.content))
        delegation_second = sum(1 for t in second_half if self._is_delegation(t.content))

        return {
            "delegation_trend": (
                "mejorando" if delegation_second < delegation_first
                else "empeorando" if delegation_second > delegation_first
                else "estable"
            ),
            "delegation_first_half": delegation_first,
            "delegation_second_half": delegation_second,
        }