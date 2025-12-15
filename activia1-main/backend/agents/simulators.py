"""
Submodelo 3: Simuladores Profesionales IA (S-IA-X)

Agentes que recrean roles profesionales auténticos de la industria del software.

SPRINT 4: Integración completa con LLM real (Gemini/OpenAI) para respuestas dinámicas
"""
from typing import Optional, Dict, Any, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SimuladorType(str, Enum):
    """Tipos de simuladores profesionales

    V1 (Original - 6 tipos):
    - PRODUCT_OWNER, SCRUM_MASTER, TECH_INTERVIEWER, INCIDENT_RESPONDER, CLIENT, DEVSECOPS

    V2 (Enhanced - Sprint 6 - 8 tipos adicionales):
    - SENIOR_DEV, QA_ENGINEER, SECURITY_AUDITOR, TECH_LEAD, DEMANDING_CLIENT
    """
    # V1 - Original simulators
    PRODUCT_OWNER = "product_owner"  # PO-IA
    SCRUM_MASTER = "scrum_master"  # SM-IA
    TECH_INTERVIEWER = "tech_interviewer"  # IT-IA
    INCIDENT_RESPONDER = "incident_responder"  # IR-IA
    CLIENT = "client"  # CX-IA
    DEVSECOPS = "devsecops"  # DSO-IA

    # V2 - Enhanced simulators (Sprint 6)
    SENIOR_DEV = "senior_dev"  # SD-IA - Senior Developer
    QA_ENGINEER = "qa_engineer"  # QA-IA - QA Engineer
    SECURITY_AUDITOR = "security_auditor"  # SA-IA - Security Auditor
    TECH_LEAD = "tech_lead"  # TL-IA - Tech Lead
    DEMANDING_CLIENT = "demanding_client"  # DC-IA - Demanding Client (harder version)


class SimuladorProfesionalAgent:
    """
    S-IA-X: Simuladores Profesionales

    Funciones:
    1. Crear condiciones situadas de práctica profesional
    2. Desarrollar competencias transversales
    3. Entrenar interacción humano-IA contextualizada
    4. Modelar decisiones profesionales con trazabilidad
    5. Generar evidencia para evaluación formativa
    """

    def __init__(
        self, 
        simulator_type: SimuladorType, 
        llm_provider=None, 
        trace_repo=None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.simulator_type = simulator_type
        self.llm_provider = llm_provider
        self.trace_repo = trace_repo
        self.config = config or {}
        self.context = {}

    async def interact(
        self, 
        student_input: str, 
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Interactúa según el rol del simulador.

        SPRINT 4: Si llm_provider está disponible, usa respuestas dinámicas.
        Si no, usa respuestas predefinidas (fallback para testing).
        
        Args:
            student_input: Prompt del estudiante
            context: Contexto adicional de la conversación
            session_id: ID de sesión para recuperar historial de conversación
        """
        if self.simulator_type == SimuladorType.PRODUCT_OWNER:
            return await self._interact_as_product_owner(student_input, context, session_id)
        elif self.simulator_type == SimuladorType.SCRUM_MASTER:
            return await self._interact_as_scrum_master(student_input, context, session_id)
        elif self.simulator_type == SimuladorType.TECH_INTERVIEWER:
            return await self._interact_as_interviewer(student_input, context, session_id)
        elif self.simulator_type == SimuladorType.INCIDENT_RESPONDER:
            return await self._interact_as_incident_responder(student_input, context, session_id)
        elif self.simulator_type == SimuladorType.DEVSECOPS:
            return await self._interact_as_devsecops(student_input, context, session_id)
        elif self.simulator_type == SimuladorType.CLIENT:
            return await self._interact_as_client(student_input, context, session_id)
        else:
            return {"message": "Simulador en desarrollo", "metadata": {}}

    async def _interact_as_product_owner(
        self,
        student_input: str,
        context: Optional[Dict[str, Any]],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Simula Product Owner"""
        # Si hay LLM provider disponible, usar respuesta dinámica
        if self.llm_provider:
            return await self._generate_llm_response(
                role="Product Owner",
                system_prompt="""Eres un Product Owner experimentado de una empresa de software.
Tu rol es cuestionar propuestas técnicas, pedir criterios de aceptación claros,
evaluar el valor para el usuario final, y priorizar el backlog por ROI.
Debes ser exigente pero constructivo. Pide justificaciones técnicas sólidas.
Evalúas: comunicación técnica, análisis de requisitos, priorización, justificación de decisiones.""",
                student_input=student_input,
                context=context,
                competencies=["comunicacion_tecnica", "analisis_requisitos", "priorizacion", "justificacion_decisiones"],
                expects=["criterios_aceptacion", "justificacion_tecnica", "analisis_alternativas"],
                session_id=session_id
            )

        # Fallback: respuesta predefinida
        return {
            "message": """
Como Product Owner, necesito que me aclares algunos puntos:

1. ¿Cuáles son los criterios de aceptación específicos para esta funcionalidad?
2. ¿Cómo pensás que esto agrega valor al usuario final?
3. ¿Qué alternativas consideraste y por qué elegiste este enfoque?
4. ¿Cuál es el impacto si postergamos esta funcionalidad un sprint?

Necesito justificaciones técnicas sólidas para priorizar esto en el backlog.
            """.strip(),
            "role": "product_owner",
            "expects": ["criterios_aceptacion", "justificacion_tecnica", "analisis_alternativas"],
            "metadata": {
                "competencies_evaluated": [
                    "comunicacion_tecnica",
                    "analisis_requisitos",
                    "priorizacion"
                ]
            }
        }

    async def _interact_as_scrum_master(
        self,
        student_input: str,
        context: Optional[Dict[str, Any]],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Simula Scrum Master"""
        # Si hay LLM provider disponible, usar respuesta dinámica
        if self.llm_provider:
            return await self._generate_llm_response(
                role="Scrum Master",
                system_prompt="""Eres un Scrum Master certificado facilitando ceremonias ágiles.
Tu rol es hacer daily standups, identificar impedimentos, ayudar al equipo a auto-organizarse,
y mejorar procesos. Debes ser empático pero directo cuando hay problemas de estimación o bloqueos.
Evalúas: gestión de tiempo, comunicación, identificación de impedimentos, auto-organización.""",
                student_input=student_input,
                context=context,
                competencies=["gestion_tiempo", "comunicacion", "identificacion_impedimentos", "auto_organizacion"],
                expects=["status_update", "impediments", "plan"],
                session_id=session_id
            )

        # Fallback: respuesta predefinida
        return {
            "message": """
En nuestro daily:

1. ¿Qué lograste ayer?
2. ¿Qué vas a hacer hoy?
3. ¿Hay algún impedimento que te esté bloqueando?

Noto que tu estimación original era de 3 puntos y llevás 5 días. ¿Qué está
pasando? ¿Necesitamos re-estimar o hay deuda técnica no considerada?
            """.strip(),
            "role": "scrum_master",
            "expects": ["status_update", "impediments", "plan"],
            "metadata": {
                "competencies_evaluated": [
                    "gestion_tiempo",
                    "comunicacion",
                    "identificacion_impedimentos"
                ]
            }
        }

    async def _interact_as_interviewer(
        self,
        student_input: str,
        context: Optional[Dict[str, Any]],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Simula entrevista técnica"""
        # Si hay LLM provider disponible, usar respuesta dinámica
        if self.llm_provider:
            return await self._generate_llm_response(
                role="Senior Technical Interviewer",
                system_prompt="""Eres un entrevistador técnico senior evaluando candidatos.
Tu rol es hacer preguntas conceptuales sobre algoritmos y estructuras de datos,
pedir análisis de complejidad, y evaluar razonamiento en voz alta.
Debes hacer follow-up questions para profundizar, y valorar claridad en las explicaciones.
Evalúas: dominio conceptual, análisis algorítmico, comunicación técnica, razonamiento estructurado.""",
                student_input=student_input,
                context=context,
                competencies=["dominio_conceptual", "analisis_algoritmico", "comunicacion_tecnica", "razonamiento_en_voz_alta"],
                expects=["explicacion_conceptual", "ejemplos", "analisis_complejidad"],
                session_id=session_id
            )

        # Fallback: respuesta predefinida
        return {
            "message": """
Pregunta técnica:

Explicame la diferencia entre complejidad temporal O(n) y O(log n).
Dame un ejemplo concreto de cada caso.

Luego: ¿cómo optimizarías una búsqueda lineal en una lista ordenada?
Justificá tu respuesta con análisis de complejidad.
            """.strip(),
            "role": "tech_interviewer",
            "expects": ["explicacion_conceptual", "ejemplos", "analisis_complejidad"],
            "metadata": {
                "competencies_evaluated": [
                    "dominio_conceptual",
                    "analisis_algoritmico",
                    "comunicacion_tecnica"
                ]
            }
        }

    async def _interact_as_devsecops(
        self,
        student_input: str,
        context: Optional[Dict[str, Any]],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Simula analista DevSecOps"""
        # Si hay LLM provider disponible, usar respuesta dinámica
        if self.llm_provider:
            return await self._generate_llm_response(
                role="DevSecOps Security Analyst",
                system_prompt="""Eres un analista de seguridad DevSecOps experimentado.
Tu rol es auditar código, detectar vulnerabilidades (SQL injection, XSS, CSRF, etc.),
analizar dependencias obsoletas, y exigir planes de remediación con timeline.
Debes ser directo, enfocarte en riesgos críticos, y pedir evidencia de mitigación.
Evalúas: seguridad, análisis de vulnerabilidades, gestión de riesgo, cumplimiento normativo.""",
                student_input=student_input,
                context=context,
                competencies=["seguridad", "analisis_vulnerabilidades", "gestion_riesgo", "cumplimiento"],
                expects=["plan_remediacion", "analisis_riesgo", "estrategia_testing"],
                session_id=session_id
            )

        # Fallback: respuesta predefinida
        return {
            "message": """
He detectado varias vulnerabilidades en tu código:

1. **SQL Injection** en línea 45: query string no parametrizada
2. **XSS** en línea 78: input de usuario sin sanitizar
3. **Dependencia vulnerable**: lodash 4.17.15 (CVE-2020-8203)

¿Cómo pensás remediar estos issues? Necesito:
- Plan de mitigación
- Timeline
- Tests que validen el fix
            """.strip(),
            "role": "devsecops",
            "expects": ["plan_remediacion", "analisis_riesgo", "estrategia_testing"],
            "metadata": {
                "competencies_evaluated": [
                    "seguridad",
                    "analisis_vulnerabilidades",
                    "gestion_riesgo"
                ]
            }
        }

    async def _interact_as_incident_responder(
        self,
        student_input: str,
        context: Optional[Dict[str, Any]],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        SPRINT 4: Simula un Incident Responder (IR-IA)

        Gestiona incidentes de producción bajo presión.
        """
        # Si hay LLM provider disponible, usar respuesta dinámica
        if self.llm_provider:
            return await self._generate_llm_response(
                role="Senior DevOps Incident Responder",
                system_prompt="""Eres un ingeniero DevOps senior gestionando un incidente en producción.
Tu rol es hacer triage, diagnosticar el problema, priorizar acciones bajo presión,
coordinar hotfixes, y documentar post-mortem.
Debes ser sistemático, priorizar por impacto, y requerir evidencia (logs, métricas).
Evalúas: diagnóstico sistemático, priorización bajo presión, documentación, manejo de crisis.""",
                student_input=student_input,
                context=context,
                competencies=["diagnostico_sistematico", "priorizacion", "documentacion", "manejo_presion"],
                expects=["diagnostico", "plan_accion", "hotfix_propuesto", "post_mortem"],
                session_id=session_id
            )

        # Fallback: respuesta predefinida
        return {
            "message": """
🚨 INCIDENTE CRÍTICO EN PRODUCCIÓN 🚨

**Severidad**: P1 (crítico)
**Impacto**: El servidor de API está caído. 5000 usuarios afectados.
**Tiempo de inactividad**: 12 minutos

**Síntomas**:
- HTTP 503 Service Unavailable
- Logs muestran: "OutOfMemoryError: Java heap space"
- CPU al 100% en todos los nodos
- Base de datos respondiendo normalmente

**Tu turno**:
1. ¿Cuál es tu hipótesis inicial?
2. ¿Qué comandos ejecutarías para diagnosticar?
3. ¿Cuál es tu plan de acción inmediato?
4. ¿Cómo prevenimos que vuelva a ocurrir?

Necesito respuestas en <5 minutos. El CEO está preguntando cuándo volvemos online.
            """.strip(),
            "role": "incident_responder",
            "expects": ["diagnostico", "plan_accion", "hotfix_propuesto", "post_mortem"],
            "metadata": {
                "competencies_evaluated": [
                    "diagnostico_sistematico",
                    "priorizacion",
                    "documentacion",
                    "manejo_presion"
                ],
                "incident_severity": "P1",
                "time_pressure": "high"
            }
        }

    async def _interact_as_client(
        self,
        student_input: str,
        context: Optional[Dict[str, Any]],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        SPRINT 4: Simula un Cliente (CX-IA)

        Cliente con requisitos ambiguos que requiere elicitación y negociación.
        """
        # Si hay LLM provider disponible, usar respuesta dinámica
        if self.llm_provider:
            return await self._generate_llm_response(
                role="Non-technical Client",
                system_prompt="""Eres un cliente no técnico con una idea de negocio.
Tus requisitos son ambiguos, a veces contradictorios, y cambias de opinión.
El estudiante debe hacer elicitación efectiva, negociar prioridades, y gestionar expectativas.
No entiendes jerga técnica. Valoras explicaciones simples y justificaciones de negocio.
Evalúas: elicitación de requisitos, negociación, empatía, gestión de expectativas.""",
                student_input=student_input,
                context=context,
                competencies=["elicitacion_requisitos", "negociacion", "empatia", "gestion_expectativas"],
                expects=["clarificacion_requisitos", "propuesta_alternativas", "justificacion_negocio"],
                session_id=session_id
            )

        # Fallback: respuesta predefinida
        return {
            "message": """
Hola, necesito una app "como Uber pero para delivery de comida".

Quiero que:
- Los usuarios puedan pedir comida
- Los restaurantes reciban los pedidos
- Los repartidores... no sé, algo con GPS
- Pagos con tarjeta, pero también efectivo
- Notificaciones cuando llegue el pedido

Ah, y tiene que estar lista en 2 semanas porque mi cuñado dijo que puede conseguir inversores.

¿Cuánto sale? ¿Podés empezar ya?
            """.strip(),
            "role": "client",
            "expects": ["clarificacion_requisitos", "propuesta_alternativas", "justificacion_negocio"],
            "metadata": {
                "competencies_evaluated": [
                    "elicitacion_requisitos",
                    "negociacion",
                    "empatia",
                    "gestion_expectativas"
                ],
                "requirements_clarity": "low",
                "technical_knowledge": "none"
            }
        }

    async def _generate_llm_response(
        self,
        role: str,
        system_prompt: str,
        student_input: str,
        context: Optional[Dict[str, Any]],
        competencies: List[str],
        expects: List[str],
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        SPRINT 4: Genera respuesta dinámica usando LLM provider (Gemini/OpenAI).
        
        ✅ NUEVO: Ahora soporta memoria de conversación mediante session_id.

        Args:
            role: Rol del simulador (e.g., "Scrum Master", "Product Owner")
            system_prompt: Instrucciones del sistema para el LLM
            student_input: Entrada del estudiante
            context: Contexto adicional de la conversación
            competencies: Competencias a evaluar
            expects: Qué se espera en la respuesta del estudiante
            session_id: ID de sesión para cargar historial de conversación

        Returns:
            Dict con mensaje, role, expects, metadata (competencias + análisis)
        """
        try:
            from ..llm.base import LLMMessage, LLMRole
            from ..models.cognitive_trace import InteractionType

            # Construir contexto completo
            context_str = ""
            if context:
                context_str = f"\n\nContexto adicional:\n{context}"

            # Construir mensajes: empezar con system prompt
            messages = [
                LLMMessage(
                    role=LLMRole.SYSTEM,
                    content=f"{system_prompt}{context_str}"
                )
            ]
            
            # ✅ NUEVO: Cargar historial de conversación si hay session_id
            if session_id and self.trace_repo:
                conversation_history = self._load_conversation_history(session_id)
                messages.extend(conversation_history)
                logger.info(
                    f"Loaded {len(conversation_history)} messages from conversation history",
                    extra={"session_id": session_id, "role": role}
                )
            
            # Agregar el prompt actual del estudiante
            messages.append(
                LLMMessage(
                    role=LLMRole.USER,
                    content=student_input
                )
            )

            # Generar respuesta
            logger.info(f"Generando respuesta con LLM para rol: {role}")
            response = await self.llm_provider.generate(
                messages=messages,
                temperature=0.7,  # Creatividad moderada para simuladores
                max_tokens=500  # Respuestas concisas
            )

            # Analizar competencias en la respuesta del estudiante
            competency_scores = self._analyze_competencies(student_input, response.content, competencies)

            return {
                "message": response.content,
                "role": role.lower().replace(" ", "_"),
                "expects": expects,
                "metadata": {
                    "competencies_evaluated": competencies,
                    "competency_scores": competency_scores,
                    "llm_model": response.model,
                    "tokens_used": response.usage.get("total_tokens", 0)
                }
            }

        except Exception as e:
            logger.error(f"Error generando respuesta con LLM: {e}", exc_info=True)
            # Fallback: respuesta genérica
            return {
                "message": f"[{role}] Ha ocurrido un error. Por favor, reformula tu consulta.",
                "role": role.lower().replace(" ", "_"),
                "expects": expects,
                "metadata": {
                    "competencies_evaluated": competencies,
                    "error": str(e)
                }
            }

    def _analyze_competencies(
        self,
        student_input: str,
        simulator_response: str,
        competencies: List[str]
    ) -> Dict[str, float]:
        """
        SPRINT 4: Analiza competencias transversales en la interacción.

        Evalúa cuantitativamente cada competencia en escala 0.0-1.0 basado en:
        - Claridad de comunicación
        - Profundidad técnica
        - Estructura del razonamiento
        - Justificación de decisiones

        Returns:
            Dict con scores 0.0-1.0 para cada competencia
        """
        scores = {}

        # Heurísticas simples (en producción, usar LLM para análisis más sofisticado)
        input_length = len(student_input.split())
        has_technical_terms = any(term in student_input.lower() for term in [
            "complejidad", "algoritmo", "estructura", "patrón", "arquitectura",
            "performance", "escalabilidad", "mantenibilidad", "testing", "refactor"
        ])
        has_questions = "?" in student_input
        has_structure = any(marker in student_input for marker in ["1.", "2.", "-", "•"])

        for competency in competencies:
            score = 0.5  # Base score

            # Ajustes por competencia
            if competency in ["comunicacion_tecnica", "comunicacion"]:
                if input_length > 30:
                    score += 0.2
                if has_technical_terms:
                    score += 0.2
                if has_structure:
                    score += 0.1

            elif competency in ["analisis_algoritmico", "dominio_conceptual"]:
                if has_technical_terms:
                    score += 0.3
                if input_length > 50:
                    score += 0.2

            elif competency in ["elicitacion_requisitos"]:
                if has_questions:
                    score += 0.3
                if input_length > 20:
                    score += 0.2

            elif competency in ["gestion_tiempo", "priorizacion"]:
                priority_terms = ["urgente", "critico", "primero", "luego", "después"]
                if any(term in student_input.lower() for term in priority_terms):
                    score += 0.3

            # Cap score at 1.0
            scores[competency] = min(score, 1.0)

        return scores

    def _load_conversation_history(
        self,
        session_id: str
    ) -> List:
        """
        ✅ NUEVO: Carga el historial de conversación de esta sesión como mensajes LLM.
        
        Recupera todas las trazas de la sesión y las convierte al formato de mensajes
        que espera el LLM provider, manteniendo el contexto completo de la conversación.
        
        Args:
            session_id: ID de la sesión actual
        
        Returns:
            Lista de LLMMessage con el historial formateado
        """
        if self.trace_repo is None:
            logger.warning("No trace repository available for conversation history")
            return []
        
        try:
            from ..llm.base import LLMMessage, LLMRole
            from ..models.cognitive_trace import InteractionType
            
            # Recuperar todas las trazas de esta sesión
            db_traces = self.trace_repo.get_by_session(session_id)
            
            messages = []
            for trace in db_traces:
                # Agregar mensaje del usuario (STUDENT_PROMPT)
                if trace.interaction_type == InteractionType.STUDENT_PROMPT.value and trace.content:
                    messages.append(
                        LLMMessage(
                            role=LLMRole.USER,
                            content=trace.content
                        )
                    )
                
                # Agregar respuesta del asistente (AI_RESPONSE o TUTOR_INTERVENTION)
                elif trace.interaction_type in [
                    InteractionType.AI_RESPONSE.value,
                    InteractionType.TUTOR_INTERVENTION.value
                ] and trace.content:
                    messages.append(
                        LLMMessage(
                            role=LLMRole.ASSISTANT,
                            content=trace.content
                        )
                    )
            
            logger.info(
                f"Loaded conversation history: {len(messages)} messages",
                extra={"session_id": session_id}
            )
            return messages
            
        except Exception as e:
            logger.error(
                f"Error loading conversation history: {e}",
                exc_info=True,
                extra={"session_id": session_id}
            )
            return []

    # ========================================================================
    # SPRINT 6: Métodos especializados para IT-IA (Technical Interviewer)
    # ========================================================================

    async def generar_pregunta_entrevista(
        self,
        tipo_entrevista: str,
        dificultad: str = "MEDIUM",
        contexto: str = ""
    ) -> str:
        """
        Genera una pregunta de entrevista técnica personalizada.

        Args:
            tipo_entrevista: CONCEPTUAL, ALGORITHMIC, DESIGN, BEHAVIORAL
            dificultad: EASY, MEDIUM, HARD
            contexto: Contexto adicional (actividad, preguntas previas, etc.)

        Returns:
            str: Pregunta formulada por el entrevistador
        """
        if not self.llm_provider:
            # Fallback: preguntas predefinidas
            return self._get_fallback_question(tipo_entrevista, dificultad)

        try:
            from ..llm.base import LLMMessage, LLMRole

            system_prompt = f"""Eres un entrevistador técnico senior evaluando candidatos para una posición de desarrollador.

Tipo de entrevista: {tipo_entrevista}
Nivel de dificultad: {dificultad}

INSTRUCCIONES:
- Genera UNA pregunta específica y desafiante apropiada para el tipo y dificultad
- Para CONCEPTUAL: pregunta sobre fundamentos, paradigmas, patrones de diseño
- Para ALGORITHMIC: pregunta sobre complejidad, estructuras de datos, algoritmos
- Para DESIGN: pregunta sobre diseño de sistemas, escalabilidad, arquitectura
- Para BEHAVIORAL: pregunta sobre experiencia, decisiones técnicas pasadas

La pregunta debe ser:
- Clara y específica
- Apropiada para el nivel ({dificultad})
- Que requiera razonamiento en voz alta
- Que permita evaluar profundidad técnica

{contexto}

Responde SOLO con la pregunta, sin preambles ni explicaciones."""

            messages = [
                LLMMessage(role=LLMRole.SYSTEM, content=system_prompt),
                LLMMessage(role=LLMRole.USER, content=f"Genera una pregunta {tipo_entrevista} de nivel {dificultad}")
            ]

            response = await self.llm_provider.generate(
                messages=messages,
                temperature=0.8,  # Alta creatividad para preguntas variadas
                max_tokens=300
            )

            logger.info(
                f"Pregunta de entrevista generada",
                extra={"tipo": tipo_entrevista, "dificultad": dificultad}
            )

            return response.content.strip()

        except Exception as e:
            logger.error(f"Error generando pregunta de entrevista: {e}", exc_info=True)
            return self._get_fallback_question(tipo_entrevista, dificultad)

    def _get_fallback_question(self, tipo_entrevista: str, dificultad: str) -> str:
        """Preguntas predefinidas como fallback"""
        preguntas = {
            "CONCEPTUAL": {
                "EASY": "¿Qué es un algoritmo? ¿Cuál es la diferencia entre un array y una lista enlazada?",
                "MEDIUM": "Explicá la diferencia entre herencia y composición. ¿Cuándo usarías cada una?",
                "HARD": "¿Cómo implementarías un sistema de cache distribuido? ¿Qué estrategias de invalidación considerarías?"
            },
            "ALGORITHMIC": {
                "EASY": "Escribí una función que determine si un número es primo. ¿Cuál es su complejidad temporal?",
                "MEDIUM": "¿Cómo invertirías una lista enlazada? Describí el proceso paso a paso y analizá la complejidad.",
                "HARD": "Dado un array de enteros, encuentra el subarreglo con la suma máxima (problema de Kadane). Optimizá la solución."
            },
            "DESIGN": {
                "EASY": "Diseñá una clase para representar un stack. ¿Qué métodos incluirías?",
                "MEDIUM": "¿Cómo diseñarías un sistema de URL shortener (como bit.ly)? Considerá escalabilidad.",
                "HARD": "Diseñá un sistema de recomendaciones para un ecommerce con millones de usuarios. ¿Qué componentes incluirías?"
            },
            "BEHAVIORAL": {
                "EASY": "Contame sobre un proyecto técnico del que estés orgulloso. ¿Qué desafíos enfrentaste?",
                "MEDIUM": "Describí una situación donde tuviste que debuggear un problema complejo. ¿Cómo lo resolviste?",
                "HARD": "Hablame de una decisión técnica difícil que tomaste. ¿Qué alternativas consideraste y por qué elegiste esa solución?"
            }
        }

        return preguntas.get(tipo_entrevista, {}).get(dificultad, "Explicá tu enfoque para resolver problemas técnicos complejos.")

    async def evaluar_respuesta_entrevista(
        self,
        pregunta: str,
        respuesta: str,
        tipo_entrevista: str
    ) -> Dict[str, Any]:
        """
        Evalúa la respuesta del estudiante a una pregunta de entrevista.

        Args:
            pregunta: La pregunta formulada
            respuesta: La respuesta del estudiante
            tipo_entrevista: Tipo de entrevista

        Returns:
            Dict con evaluación detallada:
            - clarity_score: 0.0-1.0
            - technical_accuracy: 0.0-1.0
            - thinking_aloud: bool
            - key_points_covered: List[str]
            - feedback: str
        """
        if not self.llm_provider:
            # Fallback: evaluación heurística simple
            return self._evaluate_response_heuristic(respuesta)

        try:
            from ..llm.base import LLMMessage, LLMRole

            system_prompt = f"""Eres un entrevistador técnico senior evaluando una respuesta.

Pregunta formulada: {pregunta}
Tipo de entrevista: {tipo_entrevista}

EVALÚA la respuesta del candidato en estas dimensiones:

1. **Claridad** (0.0-1.0): ¿Se explica de forma clara y estructurada?
2. **Precisión técnica** (0.0-1.0): ¿Es técnicamente correcta?
3. **Razonamiento en voz alta** (true/false): ¿Explica su proceso de pensamiento?
4. **Puntos clave cubiertos**: Lista de conceptos importantes mencionados

Responde SOLO en formato JSON:
{{
  "clarity_score": 0.0-1.0,
  "technical_accuracy": 0.0-1.0,
  "thinking_aloud": true/false,
  "key_points_covered": ["punto1", "punto2", ...],
  "feedback": "Feedback breve y constructivo (2-3 oraciones)"
}}"""

            messages = [
                LLMMessage(role=LLMRole.SYSTEM, content=system_prompt),
                LLMMessage(role=LLMRole.USER, content=f"Respuesta del candidato:\n{respuesta}")
            ]

            response = await self.llm_provider.generate(
                messages=messages,
                temperature=0.3,  # Baja temperatura para evaluación consistente
                max_tokens=400
            )

            # Parse JSON response with explicit error handling
            import json
            try:
                evaluation = json.loads(response.content)
            except json.JSONDecodeError as json_err:
                logger.warning(
                    f"Failed to parse LLM response as JSON: {json_err}",
                    extra={"raw_response": response.content[:200]}
                )
                return self._evaluate_response_heuristic(respuesta)

            logger.info(
                "Respuesta de entrevista evaluada",
                extra={
                    "clarity": evaluation.get("clarity_score"),
                    "accuracy": evaluation.get("technical_accuracy")
                }
            )

            return evaluation

        except Exception as e:
            logger.error(f"Error evaluando respuesta de entrevista: {e}", exc_info=True)
            return self._evaluate_response_heuristic(respuesta)

    def _evaluate_response_heuristic(self, respuesta: str) -> Dict[str, Any]:
        """Evaluación heurística simple como fallback"""
        words = respuesta.split()
        length = len(words)

        # Heurísticas básicas
        clarity = min(length / 50.0, 1.0) if length > 10 else 0.3
        has_technical = any(term in respuesta.lower() for term in [
            "complejidad", "algoritmo", "estructura", "patrón", "o(n)", "o(log n)"
        ])
        technical_accuracy = 0.7 if has_technical else 0.4
        thinking_aloud = any(word in respuesta.lower() for word in ["primero", "luego", "entonces", "porque"])

        return {
            "clarity_score": clarity,
            "technical_accuracy": technical_accuracy,
            "thinking_aloud": thinking_aloud,
            "key_points_covered": ["respuesta proporcionada"],
            "feedback": "Evaluación básica. Para evaluación completa, configure un LLM provider."
        }

    async def generar_evaluacion_entrevista(
        self,
        preguntas: List[Dict[str, Any]],
        respuestas: List[Dict[str, Any]],
        tipo_entrevista: str
    ) -> Dict[str, Any]:
        """
        Genera evaluación final de la entrevista completa.

        Args:
            preguntas: Lista de preguntas realizadas con metadata
            respuestas: Lista de respuestas con evaluaciones parciales
            tipo_entrevista: Tipo de entrevista

        Returns:
            Dict con:
            - overall_score: 0.0-1.0 (promedio ponderado)
            - breakdown: Dict con scores por dimensión
            - feedback: Feedback narrativo final
        """
        if not respuestas:
            return {
                "overall_score": 0.0,
                "breakdown": {},
                "feedback": "No se registraron respuestas en la entrevista."
            }

        # Calcular scores promedio
        clarity_scores = [r.get("evaluation", {}).get("clarity_score", 0.5) for r in respuestas]
        accuracy_scores = [r.get("evaluation", {}).get("technical_accuracy", 0.5) for r in respuestas]
        thinking_aloud_count = sum(1 for r in respuestas if r.get("evaluation", {}).get("thinking_aloud", False))

        avg_clarity = sum(clarity_scores) / len(clarity_scores)
        avg_accuracy = sum(accuracy_scores) / len(accuracy_scores)
        communication_score = min((thinking_aloud_count / len(respuestas)) * 1.2, 1.0)

        # Score global (ponderado)
        overall_score = (avg_clarity * 0.3 + avg_accuracy * 0.5 + communication_score * 0.2)

        breakdown = {
            "clarity": round(avg_clarity, 2),
            "technical_accuracy": round(avg_accuracy, 2),
            "communication": round(communication_score, 2),
            "thinking_aloud_percentage": round((thinking_aloud_count / len(respuestas)) * 100, 1)
        }

        # Generar feedback narrativo
        if self.llm_provider:
            try:
                from ..llm.base import LLMMessage, LLMRole

                system_prompt = f"""Eres un entrevistador técnico senior proporcionando feedback final.

Tipo de entrevista: {tipo_entrevista}
Número de preguntas: {len(preguntas)}
Score global: {overall_score:.2f} / 1.0

Scores por dimensión:
- Claridad: {avg_clarity:.2f}
- Precisión técnica: {avg_accuracy:.2f}
- Comunicación: {communication_score:.2f}

Genera un feedback narrativo (4-5 oraciones) que:
1. Resuma el desempeño general
2. Destaque fortalezas específicas
3. Identifique áreas de mejora
4. Sea constructivo y motivador

Responde SOLO con el feedback, sin formato JSON."""

                messages = [
                    LLMMessage(role=LLMRole.SYSTEM, content=system_prompt),
                    LLMMessage(role=LLMRole.USER, content="Genera el feedback final de la entrevista")
                ]

                response = await self.llm_provider.generate(
                    messages=messages,
                    temperature=0.6,
                    max_tokens=300
                )

                feedback = response.content.strip()

            except Exception as e:
                logger.error(f"Error generando feedback final: {e}")
                feedback = self._generate_fallback_feedback(overall_score, breakdown)
        else:
            feedback = self._generate_fallback_feedback(overall_score, breakdown)

        logger.info(
            "Evaluación final de entrevista generada",
            extra={"overall_score": overall_score, "num_questions": len(preguntas)}
        )

        return {
            "overall_score": round(overall_score, 2),
            "breakdown": breakdown,
            "feedback": feedback
        }

    def _generate_fallback_feedback(self, overall_score: float, breakdown: Dict[str, float]) -> str:
        """Genera feedback básico sin LLM"""
        if overall_score >= 0.8:
            level = "Excelente desempeño"
        elif overall_score >= 0.6:
            level = "Buen desempeño"
        elif overall_score >= 0.4:
            level = "Desempeño aceptable"
        else:
            level = "Necesita mejorar"

        return f"""{level} en la entrevista técnica.
Claridad de comunicación: {breakdown.get('clarity', 0):.2f}/1.0.
Precisión técnica: {breakdown.get('technical_accuracy', 0):.2f}/1.0.
Se recomienda practicar razonamiento en voz alta y profundizar conceptos técnicos."""

    # ========================================================================
    # SPRINT 6: Métodos especializados para IR-IA (Incident Responder)
    # ========================================================================

    async def generar_incidente(
        self,
        tipo_incidente: str,
        severidad: str = "HIGH"
    ) -> Dict[str, Any]:
        """
        Genera un escenario realista de incidente en producción.

        Args:
            tipo_incidente: API_ERROR, PERFORMANCE, SECURITY, DATABASE, DEPLOYMENT
            severidad: LOW, MEDIUM, HIGH, CRITICAL

        Returns:
            Dict con:
            - description: Descripción del incidente
            - logs: Logs simulados del sistema
            - metrics: Métricas simuladas (CPU, memory, etc.)
        """
        if not self.llm_provider:
            return self._get_fallback_incident(tipo_incidente, severidad)

        try:
            from ..llm.base import LLMMessage, LLMRole

            system_prompt = f"""Eres un sistema de monitoreo generando un reporte de incidente en producción.

Tipo de incidente: {tipo_incidente}
Severidad: {severidad}

Genera un escenario REALISTA de incidente que incluya:

1. **Descripción del incidente** (2-3 líneas):
   - Qué está fallando
   - Impacto en usuarios/negocio
   - Tiempo de inactividad aproximado

2. **Logs simulados** (5-8 líneas de logs realistas):
   - Timestamps
   - Niveles de log (ERROR, WARN, INFO)
   - Stack traces si aplica
   - Mensajes de error específicos

3. **Métricas simuladas** (JSON):
   - cpu_usage_percent (0-100)
   - memory_usage_percent (0-100)
   - requests_per_second (número)
   - error_rate_percent (0-100)
   - response_time_ms (número)

Responde SOLO en formato JSON:
{{
  "description": "descripción del incidente",
  "logs": "logs simulados del sistema\\n...",
  "metrics": {{
    "cpu_usage_percent": 0-100,
    "memory_usage_percent": 0-100,
    "requests_per_second": número,
    "error_rate_percent": 0-100,
    "response_time_ms": número
  }}
}}"""

            messages = [
                LLMMessage(role=LLMRole.SYSTEM, content=system_prompt),
                LLMMessage(role=LLMRole.USER, content=f"Genera incidente {tipo_incidente} de severidad {severidad}")
            ]

            response = await self.llm_provider.generate(
                messages=messages,
                temperature=0.7,
                max_tokens=600
            )

            import json
            try:
                incident_data = json.loads(response.content)
            except json.JSONDecodeError as json_err:
                logger.warning(
                    f"Failed to parse incident JSON from LLM: {json_err}",
                    extra={"raw_response": response.content[:200]}
                )
                return self._get_fallback_incident(tipo_incidente, severidad)

            logger.info(
                "Incidente generado",
                extra={"tipo": tipo_incidente, "severidad": severidad}
            )

            return incident_data

        except Exception as e:
            logger.error(f"Error generando incidente: {e}", exc_info=True)
            return self._get_fallback_incident(tipo_incidente, severidad)

    def _get_fallback_incident(self, tipo_incidente: str, severidad: str) -> Dict[str, Any]:
        """Incidentes predefinidos como fallback"""
        incidents = {
            "API_ERROR": {
                "description": "🚨 API endpoint /users devuelve HTTP 500. 3,500 usuarios afectados. Tiempo de inactividad: 8 minutos.",
                "logs": """[2025-11-21 14:32:15] ERROR - NullPointerException at UserController.getUser()
[2025-11-21 14:32:16] ERROR - Failed to retrieve user from database
[2025-11-21 14:32:17] WARN  - Connection pool exhausted, waiting for available connection
[2025-11-21 14:32:18] ERROR - Timeout waiting for database connection after 5000ms
[2025-11-21 14:32:19] ERROR - Circuit breaker OPEN for database connection pool""",
                "metrics": {
                    "cpu_usage_percent": 45,
                    "memory_usage_percent": 78,
                    "requests_per_second": 1200,
                    "error_rate_percent": 85,
                    "response_time_ms": 8500
                }
            },
            "PERFORMANCE": {
                "description": "🚨 Degradación severa de performance. Tiempos de respuesta >10s. 8,000 usuarios afectados.",
                "logs": """[2025-11-21 14:45:22] WARN  - Slow query detected: SELECT * FROM orders WHERE... (12,345ms)
[2025-11-21 14:45:23] ERROR - Request timeout after 10000ms
[2025-11-21 14:45:24] WARN  - Database connection pool at 95% capacity
[2025-11-21 14:45:25] ERROR - OutOfMemoryError: Java heap space
[2025-11-21 14:45:26] WARN  - GC overhead limit exceeded""",
                "metrics": {
                    "cpu_usage_percent": 98,
                    "memory_usage_percent": 95,
                    "requests_per_second": 450,
                    "error_rate_percent": 12,
                    "response_time_ms": 15000
                }
            },
            "SECURITY": {
                "description": "🚨 CRÍTICO: Posible ataque de SQL injection detectado. Firewall bloqueó 15,000 requests maliciosos en 5 minutos.",
                "logs": """[2025-11-21 15:10:01] CRITICAL - SQL injection attempt detected from IP 45.123.67.89
[2025-11-21 15:10:02] WARN  - Malicious payload: ' OR '1'='1' --
[2025-11-21 15:10:03] ERROR - Authentication bypass attempt blocked
[2025-11-21 15:10:04] CRITICAL - Rate limit exceeded: 5000 requests/minute from same IP
[2025-11-21 15:10:05] INFO  - Firewall rule activated, IP 45.123.67.89 blocked""",
                "metrics": {
                    "cpu_usage_percent": 67,
                    "memory_usage_percent": 55,
                    "requests_per_second": 8500,
                    "error_rate_percent": 3,
                    "response_time_ms": 450
                }
            },
            "DATABASE": {
                "description": "🚨 Base de datos principal no responde. Conexiones timeout. Toda la aplicación afectada.",
                "logs": """[2025-11-21 16:20:10] CRITICAL - Database connection failed: Connection timed out
[2025-11-21 16:20:11] ERROR - Unable to acquire JDBC Connection
[2025-11-21 16:20:12] WARN  - Replica lag: 45 seconds behind master
[2025-11-21 16:20:13] ERROR - Too many connections (max_connections = 500)
[2025-11-21 16:20:14] CRITICAL - Master database unreachable, attempting failover to replica""",
                "metrics": {
                    "cpu_usage_percent": 15,
                    "memory_usage_percent": 45,
                    "requests_per_second": 50,
                    "error_rate_percent": 100,
                    "response_time_ms": 30000
                }
            },
            "DEPLOYMENT": {
                "description": "🚨 Deployment falló. Rollback necesario. Nuevo release tiene breaking changes no detectados.",
                "logs": """[2025-11-21 17:05:30] ERROR - Deployment v2.5.0 failed health check
[2025-11-21 17:05:31] CRITICAL - NoSuchMethodError: UserService.authenticate(String, String)
[2025-11-21 17:05:32] ERROR - Incompatible API version detected
[2025-11-21 17:05:33] WARN  - Rolling back to previous version v2.4.9
[2025-11-21 17:05:34] INFO  - Rollback initiated, ETA 3 minutes""",
                "metrics": {
                    "cpu_usage_percent": 32,
                    "memory_usage_percent": 60,
                    "requests_per_second": 200,
                    "error_rate_percent": 78,
                    "response_time_ms": 6500
                }
            }
        }

        incident = incidents.get(tipo_incidente, incidents["API_ERROR"])
        return incident

    async def evaluar_resolucion_incidente(
        self,
        proceso_diagnostico: List[Dict[str, Any]],
        solucion: str,
        causa_raiz: str,
        post_mortem: str
    ) -> Dict[str, Any]:
        """
        Evalúa la resolución del incidente por parte del estudiante.

        Args:
            proceso_diagnostico: Lista de pasos de diagnóstico realizados
            solucion: Solución propuesta
            causa_raiz: Causa raíz identificada
            post_mortem: Documentación post-mortem

        Returns:
            Dict con:
            - overall_score: 0.0-1.0
            - diagnosis_systematic: 0.0-1.0
            - prioritization: 0.0-1.0
            - documentation_quality: 0.0-1.0
            - communication_clarity: 0.0-1.0
            - feedback: str
        """
        if not self.llm_provider:
            return self._evaluate_incident_heuristic(
                proceso_diagnostico, solucion, causa_raiz, post_mortem
            )

        try:
            from ..llm.base import LLMMessage, LLMRole

            system_prompt = f"""Eres un ingeniero DevOps senior evaluando la resolución de un incidente.

PROCESO DE DIAGNÓSTICO ({len(proceso_diagnostico)} pasos):
{self._format_diagnosis_process(proceso_diagnostico)}

SOLUCIÓN PROPUESTA:
{solucion}

CAUSA RAÍZ IDENTIFICADA:
{causa_raiz}

POST-MORTEM:
{post_mortem}

EVALÚA en estas dimensiones (0.0-1.0):

1. **Diagnóstico sistemático**: ¿Siguió un proceso lógico de triage y diagnóstico?
2. **Priorización**: ¿Priorizó correctamente las acciones por impacto?
3. **Calidad de documentación**: ¿El post-mortem es completo y útil?
4. **Claridad de comunicación**: ¿Se expresó de forma clara y profesional?

Responde SOLO en formato JSON:
{{
  "diagnosis_systematic": 0.0-1.0,
  "prioritization": 0.0-1.0,
  "documentation_quality": 0.0-1.0,
  "communication_clarity": 0.0-1.0,
  "feedback": "Feedback constructivo (3-4 oraciones)"
}}"""

            messages = [
                LLMMessage(role=LLMRole.SYSTEM, content=system_prompt),
                LLMMessage(role=LLMRole.USER, content="Evalúa la resolución del incidente")
            ]

            response = await self.llm_provider.generate(
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )

            import json
            try:
                evaluation = json.loads(response.content)
            except json.JSONDecodeError as json_err:
                logger.warning(
                    f"Failed to parse incident evaluation JSON from LLM: {json_err}",
                    extra={"raw_response": response.content[:200]}
                )
                return self._evaluate_incident_heuristic(
                    proceso_diagnostico, solucion, causa_raiz, post_mortem
                )

            # Calcular overall score
            overall_score = sum([
                evaluation.get("diagnosis_systematic", 0.5) * 0.3,
                evaluation.get("prioritization", 0.5) * 0.2,
                evaluation.get("documentation_quality", 0.5) * 0.25,
                evaluation.get("communication_clarity", 0.5) * 0.25
            ])

            evaluation["overall_score"] = round(overall_score, 2)

            logger.info(
                "Resolución de incidente evaluada",
                extra={"overall_score": overall_score, "num_steps": len(proceso_diagnostico)}
            )

            return evaluation

        except Exception as e:
            logger.error(f"Error evaluando resolución de incidente: {e}", exc_info=True)
            return self._evaluate_incident_heuristic(
                proceso_diagnostico, solucion, causa_raiz, post_mortem
            )

    def _format_diagnosis_process(self, proceso: List[Dict[str, Any]]) -> str:
        """Formatea el proceso de diagnóstico para el LLM"""
        formatted = []
        for i, step in enumerate(proceso, 1):
            action = step.get("action", "")
            finding = step.get("finding", "N/A")
            formatted.append(f"{i}. {action}\n   Hallazgo: {finding}")
        return "\n".join(formatted)

    def _evaluate_incident_heuristic(
        self,
        proceso_diagnostico: List[Dict[str, Any]],
        solucion: str,
        causa_raiz: str,
        post_mortem: str
    ) -> Dict[str, Any]:
        """Evaluación heurística simple como fallback"""
        num_steps = len(proceso_diagnostico)
        solution_length = len(solucion.split())
        postmortem_length = len(post_mortem.split())

        # Heurísticas básicas
        diagnosis_systematic = min(num_steps / 5.0, 1.0) if num_steps > 0 else 0.2
        prioritization = 0.7 if num_steps >= 3 else 0.4
        documentation_quality = min(postmortem_length / 100.0, 1.0) if postmortem_length > 50 else 0.3
        communication_clarity = min(solution_length / 50.0, 1.0) if solution_length > 20 else 0.4

        overall_score = (
            diagnosis_systematic * 0.3 +
            prioritization * 0.2 +
            documentation_quality * 0.25 +
            communication_clarity * 0.25
        )

        return {
            "overall_score": round(overall_score, 2),
            "diagnosis_systematic": round(diagnosis_systematic, 2),
            "prioritization": round(prioritization, 2),
            "documentation_quality": round(documentation_quality, 2),
            "communication_clarity": round(communication_clarity, 2),
            "feedback": f"Incidente resuelto con {num_steps} pasos de diagnóstico. Para evaluación completa, configure un LLM provider."
        }

    # ========================================================================
    # SPRINT 6: Métodos adicionales para otros simuladores
    # ========================================================================

    def procesar_daily_standup(
        self,
        que_hizo_ayer: str,
        que_hara_hoy: str,
        impedimentos: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesa participación en Daily Standup (SM-IA).

        Returns:
            Dict con feedback, questions, detected_issues, suggestions
        """
        # Implementación básica - puede mejorarse con LLM
        response = {
            "feedback": "Gracias por tu actualización. Veo progreso en tus tareas.",
            "questions": [],
            "detected_issues": [],
            "suggestions": []
        }

        if impedimentos:
            response["questions"].append("¿Qué apoyo necesitás para remover ese impedimento?")
            response["detected_issues"].append("Impedimento reportado")

        if len(que_hizo_ayer.split()) < 10:
            response["suggestions"].append("Sé más específico en tu reporte de tareas completadas")

        return response

    def generar_requerimientos_cliente(self, tipo_proyecto: str) -> Dict[str, Any]:
        """
        Genera requerimientos ambiguos de cliente (CX-IA).

        Returns:
            Dict con requirements, additional (lista)
        """
        return {
            "requirements": f"Necesito una app de {tipo_proyecto} que sea fácil de usar y rápida. Quiero que los usuarios puedan hacer... bueno, las cosas típicas de este tipo de apps. ¿Cuánto sale?",
            "additional": [
                "También querría notificaciones push",
                "Y que funcione offline",
                "Ah, y tiene que ser en español e inglés"
            ]
        }

    def responder_clarificacion(self, pregunta: str) -> Dict[str, Any]:
        """
        Responde pregunta de clarificación del estudiante (CX-IA).

        Returns:
            Dict con answer, new_requirements (lista), soft_skills_evaluation
        """
        return {
            "answer": "Buena pregunta. No había pensado en eso. Sí, definitivamente necesitamos esa funcionalidad.",
            "new_requirements": ["Requisito adicional descubierto"],
            "soft_skills_evaluation": {
                "empathy": 0.8,
                "clarity": 0.75,
                "professionalism": 0.85
            }
        }

    def auditar_seguridad(self, codigo: str, lenguaje: str) -> Dict[str, Any]:
        """
        Audita código en busca de vulnerabilidades (DSO-IA).

        Returns:
            Dict con audit_id, vulnerabilities, security_score, etc.
        """
        # Implementación básica - en producción usar análisis estático real
        import uuid

        vulnerabilities_found = []

        # Detección simple de patrones inseguros
        if "eval(" in codigo or "exec(" in codigo:
            vulnerabilities_found.append({
                "severity": "CRITICAL",
                "vulnerability_type": "CODE_INJECTION",
                "description": "Uso de eval/exec permite ejecución de código arbitrario",
                "recommendation": "Nunca uses eval/exec con input de usuario"
            })

        if "SELECT * FROM" in codigo and "%" in codigo:
            vulnerabilities_found.append({
                "severity": "HIGH",
                "vulnerability_type": "SQL_INJECTION",
                "description": "Posible SQL injection por concatenación de strings",
                "recommendation": "Usa queries parametrizadas"
            })

        if "password" in codigo.lower() and ("=" in codigo or ":" in codigo):
            vulnerabilities_found.append({
                "severity": "CRITICAL",
                "vulnerability_type": "HARDCODED_CREDENTIALS",
                "description": "Credenciales hardcodeadas en el código",
                "recommendation": "Usa variables de entorno o secret management"
            })

        total = len(vulnerabilities_found)
        critical = sum(1 for v in vulnerabilities_found if v.get("severity") == "CRITICAL")
        high = sum(1 for v in vulnerabilities_found if v.get("severity") == "HIGH")

        security_score = max(10.0 - (critical * 3 + high * 2), 0.0)

        return {
            "audit_id": str(uuid.uuid4()),
            "total_vulnerabilities": total,
            "critical_count": critical,
            "high_count": high,
            "medium_count": 0,
            "low_count": 0,
            "vulnerabilities": vulnerabilities_found,
            "security_score": security_score,
            "recommendations": ["Revisar todos los critical y high priority issues"],
            "owasp_compliant": critical == 0 and high == 0
        }