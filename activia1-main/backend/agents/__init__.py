"""
Agentes especializados del ecosistema AI-Native
"""
from .tutor import TutorCognitivoAgent
from .evaluator import EvaluadorProcesosAgent, ProcessEvaluatorAgent
from .simulators import SimuladorProfesionalAgent, SimuladorType
from .risk_analyst import AnalistaRiesgoAgent
from .governance import GobernanzaAgent
from .traceability import TrazabilidadN4Agent

# Nuevos módulos V2.0 del Tutor Socrático
from .tutor_rules import (
    TutorRulesEngine,
    TutorRule,
    InterventionType,
    CognitiveScaffoldingLevel
)
from .tutor_governance import (
    TutorGovernanceEngine,
    SemaforoState,
    PromptIntent,
    StudentContextAnalysis
)
from .tutor_metadata import (
    TutorMetadataTracker,
    TutorInterventionMetadata,
    StudentCognitiveEvent,
    InterventionEffectiveness
)
from .tutor_prompts import TutorSystemPrompts

__all__ = [
    # Agentes principales
    "TutorCognitivoAgent",
    "EvaluadorProcesosAgent",
    "ProcessEvaluatorAgent",  # Alias for backwards compatibility
    "SimuladorProfesionalAgent",
    "SimuladorType",
    "AnalistaRiesgoAgent",
    "GobernanzaAgent",
    "TrazabilidadN4Agent",
    
    # Tutor V2.0 - Sistema de Reglas
    "TutorRulesEngine",
    "TutorRule",
    "InterventionType",
    "CognitiveScaffoldingLevel",
    
    # Tutor V2.0 - Gobernanza
    "TutorGovernanceEngine",
    "SemaforoState",
    "PromptIntent",
    "StudentContextAnalysis",
    
    # Tutor V2.0 - Metadata y Trazabilidad
    "TutorMetadataTracker",
    "TutorInterventionMetadata",
    "StudentCognitiveEvent",
    "InterventionEffectiveness",
    
    # Tutor V2.0 - Prompts
    "TutorSystemPrompts",
]