"""
MVP del Ecosistema AI-Native
Sistema de enseñanza-aprendizaje de programación con IA generativa
"""

__version__ = "0.1.0"
__author__ = "Mag. en Ing. de Software Alberto Cortez"

from .core import AIGateway, CognitiveReasoningEngine
from .agents import (
    TutorCognitivoAgent,
    EvaluadorProcesosAgent,
    SimuladorProfesionalAgent,
    AnalistaRiesgoAgent,
    GobernanzaAgent,
    TrazabilidadN4Agent,
)

__all__ = [
    "AIGateway",
    "CognitiveReasoningEngine",
    "TutorCognitivoAgent",
    "EvaluadorProcesosAgent",
    "SimuladorProfesionalAgent",
    "AnalistaRiesgoAgent",
    "GobernanzaAgent",
    "TrazabilidadN4Agent",
]