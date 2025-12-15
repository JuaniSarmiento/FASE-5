"""
Sistema de Metadata y Trazabilidad para Tutor Socrático

Registra todas las intervenciones del tutor para análisis N4:
- Tipo de intervención
- Estado cognitivo detectado
- Nivel de ayuda otorgado
- Efectividad de la intervención
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from .tutor_rules import InterventionType, CognitiveScaffoldingLevel
from .tutor_governance import SemaforoState

logger = logging.getLogger(__name__)


class InterventionEffectiveness(str, Enum):
    """Efectividad de la intervención pedagógica"""
    MUY_EFECTIVA = "muy_efectiva"  # Estudiante mostró gran progreso
    EFECTIVA = "efectiva"  # Estudiante mostró progreso moderado
    NEUTRA = "neutra"  # Sin cambio observable
    INEFECTIVA = "inefectiva"  # No ayudó al estudiante
    CONTRAPRODUCENTE = "contraproducente"  # Empeoró la situación


class StudentCognitiveEvent(str, Enum):
    """Eventos cognitivos detectados en el estudiante"""
    FORMULACION_HIPOTESIS = "formulacion_hipotesis"
    CAMBIO_ESTRATEGIA = "cambio_estrategia"
    AUTOCORRECCION = "autocorreccion"
    DESCOMPOSICION_PROBLEMA = "descomposicion_problema"
    JUSTIFICACION_DECISION = "justificacion_decision"
    REFLEXION_METACOGNITIVA = "reflexion_metacognitiva"
    PLANIFICACION = "planificacion"
    ABANDONO_DELEGACION = "abandono_delegacion"  # Dejó de pedir código directo


class TutorInterventionMetadata:
    """
    Metadata completa de una intervención del tutor
    
    Esta información se registra en N4 para análisis posterior:
    - Efectividad de estrategias pedagógicas
    - Patrones de aprendizaje del estudiante
    - Ajuste fino de parámetros del tutor
    """
    
    def __init__(
        self,
        session_id: str,
        interaction_id: str,
        timestamp: str,
        intervention_type: InterventionType,
        student_level: CognitiveScaffoldingLevel,
        help_level: str,
        semaforo_state: SemaforoState,
        cognitive_state_detected: str,
        student_intent: str,
        student_autonomy_level: float,
        rules_applied: List[str],
        restrictions_applied: List[str],
        student_cognitive_events: Optional[List[StudentCognitiveEvent]] = None,
        effectiveness: Optional[InterventionEffectiveness] = None,
        additional_metadata: Optional[Dict[str, Any]] = None
    ):
        self.session_id = session_id
        self.interaction_id = interaction_id
        self.timestamp = timestamp
        self.intervention_type = intervention_type
        self.student_level = student_level
        self.help_level = help_level
        self.semaforo_state = semaforo_state
        self.cognitive_state_detected = cognitive_state_detected
        self.student_intent = student_intent
        self.student_autonomy_level = student_autonomy_level
        self.rules_applied = rules_applied or []
        self.restrictions_applied = restrictions_applied or []
        self.student_cognitive_events = student_cognitive_events or []
        self.effectiveness = effectiveness
        self.additional_metadata = additional_metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte metadata a diccionario para persistencia"""
        return {
            "session_id": self.session_id,
            "interaction_id": self.interaction_id,
            "timestamp": self.timestamp,
            "intervention_type": self.intervention_type.value if isinstance(self.intervention_type, Enum) else self.intervention_type,
            "student_level": self.student_level.value if isinstance(self.student_level, Enum) else self.student_level,
            "help_level": self.help_level,
            "semaforo_state": self.semaforo_state.value if isinstance(self.semaforo_state, Enum) else self.semaforo_state,
            "cognitive_state_detected": self.cognitive_state_detected,
            "student_intent": self.student_intent,
            "student_autonomy_level": self.student_autonomy_level,
            "rules_applied": self.rules_applied,
            "restrictions_applied": self.restrictions_applied,
            "student_cognitive_events": [
                event.value if isinstance(event, Enum) else event 
                for event in self.student_cognitive_events
            ],
            "effectiveness": self.effectiveness.value if self.effectiveness else None,
            "additional_metadata": self.additional_metadata
        }


class TutorMetadataTracker:
    """
    Sistema de registro y análisis de metadata del tutor
    
    Funciones:
    1. Registrar cada intervención con metadata completa
    2. Detectar eventos cognitivos del estudiante
    3. Evaluar efectividad de intervenciones
    4. Generar métricas para análisis N4
    """
    
    def __init__(self):
        self.intervention_history: List[TutorInterventionMetadata] = []
    
    def record_intervention(
        self,
        session_id: str,
        interaction_id: str,
        intervention_type: InterventionType,
        student_level: CognitiveScaffoldingLevel,
        help_level: str,
        semaforo_state: SemaforoState,
        cognitive_state: str,
        student_intent: str,
        autonomy_level: float,
        rules_applied: List[str],
        restrictions_applied: List[str],
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> TutorInterventionMetadata:
        """
        Registra una intervención del tutor
        
        Args:
            session_id: ID de la sesión
            interaction_id: ID único de esta interacción
            intervention_type: Tipo de intervención pedagógica
            student_level: Nivel de andamiaje del estudiante
            help_level: Nivel de ayuda otorgado
            semaforo_state: Estado del semáforo de riesgo
            cognitive_state: Estado cognitivo detectado
            student_intent: Intención del estudiante
            autonomy_level: Nivel de autonomía (0-1)
            rules_applied: Reglas pedagógicas aplicadas
            restrictions_applied: Restricciones aplicadas
            additional_metadata: Metadata adicional
        
        Returns:
            TutorInterventionMetadata creado
        """
        metadata = TutorInterventionMetadata(
            session_id=session_id,
            interaction_id=interaction_id,
            timestamp=datetime.now().isoformat(),
            intervention_type=intervention_type,
            student_level=student_level,
            help_level=help_level,
            semaforo_state=semaforo_state,
            cognitive_state_detected=cognitive_state,
            student_intent=student_intent,
            student_autonomy_level=autonomy_level,
            rules_applied=rules_applied,
            restrictions_applied=restrictions_applied,
            additional_metadata=additional_metadata
        )
        
        self.intervention_history.append(metadata)
        return metadata
    
    def detect_cognitive_events(
        self,
        student_response: str,
        previous_intervention: TutorInterventionMetadata
    ) -> List[StudentCognitiveEvent]:
        """
        Detecta eventos cognitivos en la respuesta del estudiante
        
        Args:
            student_response: Respuesta del estudiante
            previous_intervention: Intervención previa del tutor
        
        Returns:
            Lista de eventos cognitivos detectados
        """
        events = []
        response_lower = student_response.lower()
        
        # Detectar formulación de hipótesis
        hypothesis_signals = [
            "creo que", "supongo que", "mi hipótesis",
            "podría ser que", "tal vez", "quizás"
        ]
        if any(signal in response_lower for signal in hypothesis_signals):
            events.append(StudentCognitiveEvent.FORMULACION_HIPOTESIS)
        
        # Detectar cambio de estrategia
        strategy_change_signals = [
            "voy a intentar", "mejor pruebo", "cambio de enfoque",
            "en vez de", "otra forma", "distinto approach"
        ]
        if any(signal in response_lower for signal in strategy_change_signals):
            events.append(StudentCognitiveEvent.CAMBIO_ESTRATEGIA)
        
        # Detectar autocorrección
        correction_signals = [
            "me equivoqué", "ahora veo el error", "corregí",
            "me di cuenta", "estaba mal", "el problema era"
        ]
        if any(signal in response_lower for signal in correction_signals):
            events.append(StudentCognitiveEvent.AUTOCORRECCION)
        
        # Detectar descomposición del problema
        decomposition_signals = [
            "primero", "después", "luego", "paso 1", "paso 2",
            "divido en", "partes", "subproblema"
        ]
        if any(signal in response_lower for signal in decomposition_signals):
            events.append(StudentCognitiveEvent.DESCOMPOSICION_PROBLEMA)
        
        # Detectar justificación
        justification_signals = [
            "porque", "ya que", "debido a", "mi razón",
            "lo elegí porque", "considerando que"
        ]
        if any(signal in response_lower for signal in justification_signals):
            events.append(StudentCognitiveEvent.JUSTIFICACION_DECISION)
        
        # Detectar reflexión metacognitiva
        reflection_signals = [
            "entiendo que", "ahora comprendo", "me doy cuenta",
            "aprendí que", "mi error fue", "debería"
        ]
        if any(signal in response_lower for signal in reflection_signals):
            events.append(StudentCognitiveEvent.REFLEXION_METACOGNITIVA)
        
        # Detectar planificación
        planning_signals = [
            "voy a", "mi plan", "planeo", "estrategia",
            "mi enfoque", "haré esto", "primero voy a"
        ]
        if any(signal in response_lower for signal in planning_signals):
            events.append(StudentCognitiveEvent.PLANIFICACION)
        
        # Detectar abandono de delegación
        # Si la intervención anterior fue un rechazo y ahora muestra trabajo propio
        if (previous_intervention.intervention_type == InterventionType.RECHAZO_PEDAGOGICO and
            ("```" in student_response or len(student_response) > 100)):
            events.append(StudentCognitiveEvent.ABANDONO_DELEGACION)
        
        return events
    
    def evaluate_intervention_effectiveness(
        self,
        intervention: TutorInterventionMetadata,
        student_response: str,
        cognitive_events: List[StudentCognitiveEvent],
        time_to_response_minutes: float
    ) -> InterventionEffectiveness:
        """
        Evalúa la efectividad de una intervención
        
        Criterios:
        - Eventos cognitivos detectados
        - Tiempo de respuesta
        - Calidad de la respuesta
        - Cambio en nivel de autonomía
        
        Args:
            intervention: Intervención a evaluar
            student_response: Respuesta del estudiante
            cognitive_events: Eventos cognitivos detectados
            time_to_response_minutes: Tiempo en minutos hasta la respuesta
        
        Returns:
            InterventionEffectiveness
        """
        effectiveness_score = 0.0
        
        # Factor 1: Eventos cognitivos positivos (+0.3 cada uno, máx 1.0)
        positive_events = [
            StudentCognitiveEvent.AUTOCORRECCION,
            StudentCognitiveEvent.DESCOMPOSICION_PROBLEMA,
            StudentCognitiveEvent.JUSTIFICACION_DECISION,
            StudentCognitiveEvent.REFLEXION_METACOGNITIVA,
            StudentCognitiveEvent.ABANDONO_DELEGACION
        ]
        
        events_score = sum(0.3 for event in cognitive_events if event in positive_events)
        effectiveness_score += min(1.0, events_score)
        
        # Factor 2: Longitud de respuesta (mín 50 chars para ser significativa)
        if len(student_response) > 50:
            effectiveness_score += 0.3
        if len(student_response) > 150:
            effectiveness_score += 0.2
        
        # Factor 3: Tiempo de respuesta razonable (2-30 min es óptimo)
        if 2 <= time_to_response_minutes <= 30:
            effectiveness_score += 0.2
        elif time_to_response_minutes < 2:
            # Respuesta muy rápida podría ser superficial
            effectiveness_score -= 0.1
        elif time_to_response_minutes > 60:
            # Mucho tiempo podría indicar frustración
            effectiveness_score -= 0.2
        
        # Factor 4: Si muestra código propio (buen signo)
        if "```" in student_response:
            effectiveness_score += 0.3
        
        # Normalizar y clasificar
        effectiveness_score = max(0.0, min(2.0, effectiveness_score))
        
        if effectiveness_score >= 1.5:
            return InterventionEffectiveness.MUY_EFECTIVA
        elif effectiveness_score >= 1.0:
            return InterventionEffectiveness.EFECTIVA
        elif effectiveness_score >= 0.5:
            return InterventionEffectiveness.NEUTRA
        elif effectiveness_score >= 0.2:
            return InterventionEffectiveness.INEFECTIVA
        else:
            return InterventionEffectiveness.CONTRAPRODUCENTE
    
    def update_intervention_effectiveness(
        self,
        interaction_id: str,
        effectiveness: InterventionEffectiveness,
        cognitive_events: List[StudentCognitiveEvent]
    ) -> bool:
        """
        Actualiza la efectividad de una intervención registrada
        
        Args:
            interaction_id: ID de la interacción
            effectiveness: Efectividad evaluada
            cognitive_events: Eventos cognitivos detectados
        
        Returns:
            True si se actualizó, False si no se encontró
        """
        for intervention in self.intervention_history:
            if intervention.interaction_id == interaction_id:
                intervention.effectiveness = effectiveness
                intervention.student_cognitive_events = cognitive_events
                return True
        return False
    
    def generate_n4_analytics(
        self,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Genera métricas de análisis N4 para una sesión
        
        Args:
            session_id: ID de la sesión a analizar
        
        Returns:
            Dict con métricas agregadas
        """
        session_interventions = [
            i for i in self.intervention_history
            if i.session_id == session_id
        ]
        
        if not session_interventions:
            return {"error": "No interventions found for session"}
        
        # Métricas de intervenciones
        intervention_types_count = {}
        for intervention in session_interventions:
            itype = intervention.intervention_type.value if isinstance(intervention.intervention_type, Enum) else intervention.intervention_type
            intervention_types_count[itype] = intervention_types_count.get(itype, 0) + 1
        
        # Métricas de efectividad
        effectiveness_counts = {}
        for intervention in session_interventions:
            if intervention.effectiveness:
                eff = intervention.effectiveness.value if isinstance(intervention.effectiveness, Enum) else intervention.effectiveness
                effectiveness_counts[eff] = effectiveness_counts.get(eff, 0) + 1
        
        # Métricas de eventos cognitivos
        cognitive_events_count = {}
        for intervention in session_interventions:
            for event in intervention.student_cognitive_events:
                event_name = event.value if isinstance(event, Enum) else event
                cognitive_events_count[event_name] = cognitive_events_count.get(event_name, 0) + 1
        
        # Métricas de semáforo
        semaforo_states_count = {}
        for intervention in session_interventions:
            state = intervention.semaforo_state.value if isinstance(intervention.semaforo_state, Enum) else intervention.semaforo_state
            semaforo_states_count[state] = semaforo_states_count.get(state, 0) + 1
        
        # Progresión de autonomía
        autonomy_progression = [
            i.student_autonomy_level for i in session_interventions
        ]
        
        # Nivel de ayuda promedio
        help_levels = [i.help_level for i in session_interventions]
        
        return {
            "session_id": session_id,
            "total_interventions": len(session_interventions),
            "intervention_types_distribution": intervention_types_count,
            "effectiveness_distribution": effectiveness_counts,
            "cognitive_events_detected": cognitive_events_count,
            "semaforo_states_distribution": semaforo_states_count,
            "autonomy_progression": autonomy_progression,
            "initial_autonomy": autonomy_progression[0] if autonomy_progression else None,
            "final_autonomy": autonomy_progression[-1] if autonomy_progression else None,
            "autonomy_improvement": (
                autonomy_progression[-1] - autonomy_progression[0]
                if autonomy_progression else 0.0
            ),
            "help_levels_used": help_levels,
            "avg_help_level": self._calculate_avg_help_level(help_levels),
            "rules_applied_frequency": self._count_rules_applied(session_interventions),
            "restrictions_applied_frequency": self._count_restrictions_applied(session_interventions)
        }
    
    def _calculate_avg_help_level(self, help_levels: List[str]) -> float:
        """Calcula nivel de ayuda promedio (0-1)"""
        level_values = {
            "minimo": 0.25,
            "bajo": 0.5,
            "medio": 0.75,
            "alto": 1.0
        }
        
        if not help_levels:
            return 0.0
        
        total = sum(level_values.get(level, 0.5) for level in help_levels)
        return total / len(help_levels)
    
    def _count_rules_applied(
        self,
        interventions: List[TutorInterventionMetadata]
    ) -> Dict[str, int]:
        """Cuenta frecuencia de reglas aplicadas"""
        counts = {}
        for intervention in interventions:
            for rule in intervention.rules_applied:
                counts[rule] = counts.get(rule, 0) + 1
        return counts
    
    def _count_restrictions_applied(
        self,
        interventions: List[TutorInterventionMetadata]
    ) -> Dict[str, int]:
        """Cuenta frecuencia de restricciones aplicadas"""
        counts = {}
        for intervention in interventions:
            for restriction in intervention.restrictions_applied:
                counts[restriction] = counts.get(restriction, 0) + 1
        return counts
    
    def export_to_n4_database(
        self,
        session_id: str,
        db_connection: Any
    ) -> bool:
        """
        Exporta metadata de intervenciones a base de datos N4
        
        Args:
            session_id: ID de la sesión
            db_connection: Conexión a la base de datos N4
        
        Returns:
            True si se exportó exitosamente
        """
        # TODO: Implementar integración con N4 database
        # Por ahora, retornar los datos como dict para logging
        analytics = self.generate_n4_analytics(session_id)

        logger.info(
            f"N4 Export - Analytics for session {session_id}",
            extra={"session_id": session_id, "analytics": analytics}
        )

        return True
