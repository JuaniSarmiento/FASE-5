"""
Test de memoria de conversación para tutor y simuladores

Verifica que:
1. El tutor AI carga historial de conversación de la sesión
2. Los simuladores profesionales cargan historial de conversación de la sesión
3. El historial se convierte correctamente a mensajes LLM
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import sys
from pathlib import Path

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.ai_gateway import AIGateway
from backend.agents.simulators import SimuladorProfesionalAgent, SimuladorType
from backend.models.trace import InteractionType, TraceLevel
from backend.llm.base import LLMMessage, LLMRole


@pytest.fixture
def mock_trace_repo():
    """Mock TraceRepository con historial de conversación"""
    repo = Mock()
    
    # Simular historial de 2 interacciones previas
    repo.get_by_session.return_value = [
        Mock(
            interaction_type=InteractionType.STUDENT_PROMPT.value,
            content="¿Qué es un algoritmo?"
        ),
        Mock(
            interaction_type=InteractionType.AI_RESPONSE.value,
            content="Un algoritmo es una secuencia finita de pasos bien definidos..."
        ),
        Mock(
            interaction_type=InteractionType.STUDENT_PROMPT.value,
            content="¿Y cuál es la diferencia con una heurística?"
        ),
        Mock(
            interaction_type=InteractionType.TUTOR_INTERVENTION.value,
            content="Excelente pregunta. Una heurística es un método práctico..."
        ),
    ]
    
    return repo


@pytest.fixture
def mock_llm_provider():
    """Mock LLMProvider"""
    provider = Mock()
    
    # Mock response
    response = Mock()
    response.content = "Esta es una respuesta con contexto de la conversación anterior."
    response.model = "phi3"
    response.usage = {"total_tokens": 150}
    
    provider.generate = Mock(return_value=response)
    
    return provider


class TestTutorConversationMemory:
    """Tests para memoria de conversación del tutor AI"""
    
    def test_load_conversation_history(self, mock_trace_repo):
        """Test: _load_conversation_history carga historial correctamente"""
        gateway = AIGateway(
            trace_repo=mock_trace_repo,
            llm_provider=None
        )
        
        session_id = "test_session_001"
        history = gateway._load_conversation_history(session_id)
        
        # Verificar que se llamó al repositorio
        mock_trace_repo.get_by_session.assert_called_once_with(session_id)
        
        # Verificar que se cargaron 4 mensajes (2 USER, 2 ASSISTANT)
        assert len(history) == 4
        
        # Verificar roles alternados
        assert history[0].role == LLMRole.USER
        assert history[1].role == LLMRole.ASSISTANT
        assert history[2].role == LLMRole.USER
        assert history[3].role == LLMRole.ASSISTANT
        
        # Verificar contenido
        assert "algoritmo" in history[0].content.lower()
        assert "heurística" in history[2].content.lower()
    
    def test_load_conversation_history_no_repo(self):
        """Test: _load_conversation_history sin repositorio devuelve lista vacía"""
        gateway = AIGateway(trace_repo=None, llm_provider=None)
        
        history = gateway._load_conversation_history("test_session")
        
        assert history == []


class TestSimulatorConversationMemory:
    """Tests para memoria de conversación de simuladores"""
    
    def test_simulator_load_conversation_history(self, mock_trace_repo):
        """Test: Simulador carga historial correctamente"""
        simulator = SimuladorProfesionalAgent(
            simulator_type=SimuladorType.PRODUCT_OWNER,
            llm_provider=None,
            trace_repo=mock_trace_repo
        )
        
        session_id = "test_session_002"
        history = simulator._load_conversation_history(session_id)
        
        # Verificar que se llamó al repositorio
        mock_trace_repo.get_by_session.assert_called_once_with(session_id)
        
        # Verificar que se cargaron 4 mensajes
        assert len(history) == 4
        
        # Verificar roles
        assert all(
            msg.role in [LLMRole.USER, LLMRole.ASSISTANT]
            for msg in history
        )
    
    @pytest.mark.asyncio
    async def test_simulator_uses_conversation_history(
        self, 
        mock_trace_repo,
        mock_llm_provider
    ):
        """Test: Simulador usa historial en _generate_llm_response"""
        simulator = SimuladorProfesionalAgent(
            simulator_type=SimuladorType.SCRUM_MASTER,
            llm_provider=mock_llm_provider,
            trace_repo=mock_trace_repo
        )
        
        session_id = "test_session_003"
        
        # Llamar a _generate_llm_response con session_id
        response = await simulator._generate_llm_response(
            role="Scrum Master",
            system_prompt="Eres un Scrum Master certificado.",
            student_input="¿Qué hago si hay un impedimento?",
            context=None,
            competencies=["gestion_tiempo"],
            expects=["plan_accion"],
            session_id=session_id
        )
        
        # Verificar que se cargó el historial
        mock_trace_repo.get_by_session.assert_called_once_with(session_id)
        
        # Verificar que se llamó al LLM provider
        mock_llm_provider.generate.assert_called_once()
        
        # Verificar que los mensajes incluyen el historial
        call_args = mock_llm_provider.generate.call_args
        messages = call_args.kwargs['messages']
        
        # Debe tener: 1 SYSTEM + 4 historial + 1 USER actual = 6 mensajes
        assert len(messages) >= 5  # Al menos system + historial + current
        
        # Verificar que la respuesta contiene el contenido esperado
        assert "contexto de la conversación anterior" in response["message"]
        assert response["role"] == "scrum_master"
    
    @pytest.mark.asyncio
    async def test_simulator_interact_passes_session_id(
        self,
        mock_trace_repo,
        mock_llm_provider
    ):
        """Test: interact() pasa session_id a _generate_llm_response"""
        simulator = SimuladorProfesionalAgent(
            simulator_type=SimuladorType.PRODUCT_OWNER,
            llm_provider=mock_llm_provider,
            trace_repo=mock_trace_repo
        )
        
        session_id = "test_session_004"
        
        # Llamar a interact con session_id
        response = await simulator.interact(
            student_input="¿Cuáles son los criterios de aceptación?",
            context={"sprint": 3},
            session_id=session_id
        )
        
        # Verificar que se cargó el historial (indirectamente)
        mock_trace_repo.get_by_session.assert_called_once_with(session_id)
        
        # Verificar que se generó respuesta
        assert response is not None
        assert "message" in response


class TestConversationMemoryIntegration:
    """Tests de integración para memoria de conversación"""
    
    def test_empty_session_no_history(self, mock_trace_repo):
        """Test: Sesión sin historial devuelve lista vacía"""
        mock_trace_repo.get_by_session.return_value = []
        
        gateway = AIGateway(
            trace_repo=mock_trace_repo,
            llm_provider=None
        )
        
        history = gateway._load_conversation_history("empty_session")
        
        assert history == []
        mock_trace_repo.get_by_session.assert_called_once()
    
    def test_filters_only_relevant_interaction_types(self):
        """Test: Solo se convierten STUDENT_PROMPT y AI_RESPONSE/TUTOR_INTERVENTION"""
        repo = Mock()
        repo.get_by_session.return_value = [
            Mock(
                interaction_type=InteractionType.STUDENT_PROMPT.value,
                content="Pregunta 1"
            ),
            Mock(
                interaction_type=InteractionType.AGENT_REASONING.value,  # No debe incluirse
                content="Razonamiento interno"
            ),
            Mock(
                interaction_type=InteractionType.AI_RESPONSE.value,
                content="Respuesta 1"
            ),
        ]
        
        gateway = AIGateway(trace_repo=repo, llm_provider=None)
        history = gateway._load_conversation_history("test_session")
        
        # Solo deben cargarse 2 mensajes (STUDENT_PROMPT y AI_RESPONSE)
        assert len(history) == 2
        assert history[0].content == "Pregunta 1"
        assert history[1].content == "Respuesta 1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
