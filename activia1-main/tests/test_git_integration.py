"""
Tests for Git Integration Agent (N2 Traceability)

Tests para src/ai_native_mvp/agents/git_integration.py

Verifica captura de commits, análisis de patrones, correlación con trazas N4.
"""

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from uuid import uuid4

# Solo importar si GitPython está disponible
try:
    from git import Repo, Commit
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="GitPython not installed")

from backend.agents.git_integration import GitIntegrationAgent
from backend.models.git_trace import (
    GitTrace,
    GitEventType,
    GitFileChange,
    CodePattern,
    CodeEvolution,
)
from backend.models.trace import CognitiveTrace, InteractionType, TraceLevel
from backend.core.cognitive_engine import CognitiveState


@pytest.fixture
def mock_git_trace_repo():
    """Mock repository para Git traces"""
    repo = Mock()
    repo.create = Mock(return_value=None)
    repo.get_by_session = Mock(return_value=[])
    return repo


@pytest.fixture
def git_agent(mock_git_trace_repo):
    """Git integration agent con repositorio mock"""
    if not GIT_AVAILABLE:
        pytest.skip("GitPython not available")
    return GitIntegrationAgent(git_trace_repo=mock_git_trace_repo)


@pytest.fixture
def sample_cognitive_traces():
    """Trazas cognitivas de ejemplo para correlación"""
    base_time = datetime.now(tz=timezone.utc)

    traces = [
        CognitiveTrace(
            id=str(uuid4()),
            session_id="session_123",
            student_id="student_001",
            activity_id="prog2_tp1",
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            content="¿Cómo implemento una cola circular?",
            cognitive_state=CognitiveState.EXPLORACION,
            ai_involvement=0.3,
            timestamp=base_time - timedelta(minutes=10),
        ),
        CognitiveTrace(
            id=str(uuid4()),
            session_id="session_123",
            student_id="student_001",
            activity_id="prog2_tp1",
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.AI_RESPONSE,
            content="Para implementar una cola circular...",
            cognitive_state=CognitiveState.EXPLORACION,
            ai_involvement=0.6,
            timestamp=base_time - timedelta(minutes=9),
        ),
        CognitiveTrace(
            id=str(uuid4()),
            session_id="session_123",
            student_id="student_001",
            activity_id="prog2_tp1",
            trace_level=TraceLevel.N4_COGNITIVO,
            interaction_type=InteractionType.STUDENT_PROMPT,
            content="Estoy implementando el enqueue",
            cognitive_state=CognitiveState.IMPLEMENTACION,
            ai_involvement=0.2,
            timestamp=base_time - timedelta(minutes=2),
        ),
    ]
    return traces


class TestGitIntegrationAgent:
    """Tests para GitIntegrationAgent"""

    def test_agent_initialization_without_repo(self):
        """Agent puede inicializarse sin repositorio"""
        if not GIT_AVAILABLE:
            pytest.skip("GitPython not available")

        agent = GitIntegrationAgent(git_trace_repo=None)
        assert agent.git_trace_repo is None

    def test_agent_initialization_with_repo(self, mock_git_trace_repo):
        """Agent puede inicializarse con repositorio"""
        if not GIT_AVAILABLE:
            pytest.skip("GitPython not available")

        agent = GitIntegrationAgent(git_trace_repo=mock_git_trace_repo)
        assert agent.git_trace_repo is mock_git_trace_repo

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_detect_event_type_normal_commit(self, git_agent):
        """Detectar tipo de evento: commit normal"""
        mock_commit = Mock(spec=Commit)
        mock_commit.parents = [Mock()]  # 1 padre = commit normal
        mock_commit.message = "Add feature X"

        event_type = git_agent._detect_event_type(mock_commit)
        assert event_type == GitEventType.COMMIT

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_detect_event_type_merge(self, git_agent):
        """Detectar tipo de evento: merge commit"""
        mock_commit = Mock(spec=Commit)
        mock_commit.parents = [Mock(), Mock()]  # 2+ padres = merge
        mock_commit.message = "Merge branch 'feature'"

        event_type = git_agent._detect_event_type(mock_commit)
        assert event_type == GitEventType.MERGE

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_detect_event_type_revert(self, git_agent):
        """Detectar tipo de evento: revert commit"""
        mock_commit = Mock(spec=Commit)
        mock_commit.parents = [Mock()]
        mock_commit.message = "Revert previous changes"

        event_type = git_agent._detect_event_type(mock_commit)
        assert event_type == GitEventType.REVERT

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_detect_code_patterns_normal(self, git_agent):
        """Detectar patrones: commit normal"""
        mock_commit = Mock(spec=Commit)
        diff = """
+   def enqueue(self, item):
+       self.items.append(item)
-   # TODO: implement
        """

        patterns = git_agent._detect_code_patterns(mock_commit, diff)

        assert CodePattern.NORMAL in patterns
        assert CodePattern.AI_GENERATED not in patterns

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_detect_code_patterns_ai_generated(self, git_agent):
        """Detectar patrones: código generado por IA (>200 líneas)"""
        mock_commit = Mock(spec=Commit)
        # Simular diff con 250 líneas agregadas
        diff = "\n".join(["+   line " + str(i) for i in range(250)])

        patterns = git_agent._detect_code_patterns(mock_commit, diff)

        assert CodePattern.AI_GENERATED in patterns

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_detect_code_patterns_debugging(self, git_agent):
        """Detectar patrones: código de debugging"""
        mock_commit = Mock(spec=Commit)
        diff = """
+   print("Debug: value =", value)
+   console.log("Testing...")
+   import pdb; pdb.set_trace()
        """

        patterns = git_agent._detect_code_patterns(mock_commit, diff)

        assert CodePattern.DEBUGGING in patterns

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_detect_code_patterns_commented_code(self, git_agent):
        """Detectar patrones: código comentado masivo"""
        mock_commit = Mock(spec=Commit)
        # Simular 25 líneas comentadas
        diff = "\n".join(["+   # commented line " + str(i) for i in range(25)])

        patterns = git_agent._detect_code_patterns(mock_commit, diff)

        assert CodePattern.COMMENTED_CODE in patterns

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_detect_code_patterns_refactoring(self, git_agent):
        """Detectar patrones: refactoring (alto ratio deletion/addition)"""
        mock_commit = Mock(spec=Commit)
        # Simular refactoring: 60 deletions, 65 additions
        diff = "\n".join(["-   old line " + str(i) for i in range(60)])
        diff += "\n" + "\n".join(["+   new line " + str(i) for i in range(65)])

        patterns = git_agent._detect_code_patterns(mock_commit, diff)

        assert CodePattern.REFACTORING in patterns

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_find_nearby_traces_within_window(self, git_agent, sample_cognitive_traces):
        """Encontrar trazas cercanas dentro de ventana temporal"""
        commit_time = datetime.now(tz=timezone.utc)

        # Trace a 2 minutos antes (dentro de ventana de 5 min)
        nearby = git_agent._find_nearby_traces(
            commit_time,
            sample_cognitive_traces,
            window_minutes=5  # Changed from 30 to 5 to match test expectation
        )

        assert len(nearby) == 1  # Solo el trace más reciente (2 min antes)
        assert nearby[0].cognitive_state == CognitiveState.IMPLEMENTACION

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_find_nearby_traces_outside_window(self, git_agent, sample_cognitive_traces):
        """No encontrar trazas fuera de ventana temporal"""
        # Commit 2 horas después
        commit_time = datetime.now(tz=timezone.utc) + timedelta(hours=2)

        nearby = git_agent._find_nearby_traces(
            commit_time,
            sample_cognitive_traces,
            window_minutes=30
        )

        assert len(nearby) == 0

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_correlate_with_cognitive_traces_found(self, git_agent, sample_cognitive_traces):
        """Correlación exitosa con trazas cognitivas"""
        mock_commit = Mock(spec=Commit)
        mock_commit.committed_date = datetime.now(tz=timezone.utc).timestamp()

        correlation = git_agent._correlate_with_cognitive_traces(
            mock_commit,
            sample_cognitive_traces
        )

        assert "related_trace_ids" in correlation
        assert len(correlation["related_trace_ids"]) > 0
        assert "cognitive_state" in correlation
        assert correlation["cognitive_state"] == CognitiveState.IMPLEMENTACION.value

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_correlate_with_cognitive_traces_not_found(self, git_agent):
        """Correlación sin trazas cercanas"""
        mock_commit = Mock(spec=Commit)
        # Commit muy antiguo (hace 1 día)
        mock_commit.committed_date = (datetime.now(tz=timezone.utc) - timedelta(days=1)).timestamp()

        correlation = git_agent._correlate_with_cognitive_traces(
            mock_commit,
            []  # Sin trazas
        )

        assert correlation["related_trace_ids"] == []
        assert "cognitive_state" not in correlation


class TestCodeEvolutionAnalysis:
    """Tests para análisis de evolución de código"""

    @pytest.fixture
    def sample_git_traces(self):
        """Git traces de ejemplo para análisis"""
        session_id = "session_123"
        student_id = "student_001"
        activity_id = "prog2_tp1"

        traces = [
            GitTrace(
                id=str(uuid4()),
                session_id=session_id,
                student_id=student_id,
                activity_id=activity_id,
                event_type=GitEventType.COMMIT,
                commit_hash="abc123",
                commit_message="Initial implementation",
                author_name="Student",
                author_email="student@example.com",
                timestamp=datetime.now(tz=timezone.utc) - timedelta(hours=2),
                branch_name="main",
                parent_commits=["parent1"],
                files_changed=[
                    GitFileChange(file_path="queue.py", change_type="added", lines_added=45, lines_deleted=0)
                ],
                total_lines_added=45,
                total_lines_deleted=0,
                diff="+ implementation",
                is_merge=False,
                is_revert=False,
                detected_patterns=[CodePattern.NORMAL],
                related_cognitive_traces=["trace1"],
                cognitive_state_during_commit="IMPLEMENTACION",
            ),
            GitTrace(
                id=str(uuid4()),
                session_id=session_id,
                student_id=student_id,
                activity_id=activity_id,
                event_type=GitEventType.COMMIT,
                commit_hash="def456",
                commit_message="Fix bug in dequeue",
                author_name="Student",
                author_email="student@example.com",
                timestamp=datetime.now(tz=timezone.utc) - timedelta(hours=1),
                branch_name="main",
                parent_commits=["abc123"],
                files_changed=[
                    GitFileChange(file_path="queue.py", change_type="modified", lines_added=5, lines_deleted=3)
                ],
                total_lines_added=5,
                total_lines_deleted=3,
                diff="- old\n+ new",
                is_merge=False,
                is_revert=False,
                detected_patterns=[CodePattern.DEBUGGING],
                related_cognitive_traces=["trace2"],
                cognitive_state_during_commit="DEPURACION",
            ),
        ]
        return traces

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_analyze_code_evolution_basic_metrics(self, git_agent, sample_git_traces):
        """Análisis de evolución: métricas básicas"""
        evolution = git_agent.analyze_code_evolution("session_123", sample_git_traces)

        assert evolution.session_id == "session_123"
        assert evolution.student_id == "student_001"
        assert evolution.activity_id == "prog2_tp1"
        assert evolution.total_commits == 2
        assert evolution.total_lines_added == 50  # 45 + 5
        assert evolution.total_lines_deleted == 3
        assert evolution.net_lines_change == 47  # 50 - 3

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_analyze_code_evolution_files_modified(self, git_agent, sample_git_traces):
        """Análisis de evolución: archivos modificados"""
        evolution = git_agent.analyze_code_evolution("session_123", sample_git_traces)

        assert "queue.py" in evolution.files_modified
        assert evolution.unique_files_count == 1

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_analyze_code_evolution_pattern_distribution(self, git_agent, sample_git_traces):
        """Análisis de evolución: distribución de patrones"""
        evolution = git_agent.analyze_code_evolution("session_123", sample_git_traces)

        assert "normal" in evolution.pattern_distribution
        assert "debugging" in evolution.pattern_distribution
        assert evolution.pattern_distribution["normal"] == 1
        assert evolution.pattern_distribution["debugging"] == 1

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_analyze_code_evolution_cognitive_states(self, git_agent, sample_git_traces):
        """Análisis de evolución: commits por estado cognitivo"""
        evolution = git_agent.analyze_code_evolution("session_123", sample_git_traces)

        assert "IMPLEMENTACION" in evolution.commits_by_cognitive_state
        assert "DEPURACION" in evolution.commits_by_cognitive_state
        assert evolution.commits_by_cognitive_state["IMPLEMENTACION"] == 1
        assert evolution.commits_by_cognitive_state["DEPURACION"] == 1

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_analyze_code_evolution_timeline(self, git_agent, sample_git_traces):
        """Análisis de evolución: timeline de commits"""
        evolution = git_agent.analyze_code_evolution("session_123", sample_git_traces)

        assert len(evolution.commit_timeline) == 2
        assert evolution.commit_timeline[0]["commit_hash"] == "abc123"
        assert evolution.commit_timeline[1]["commit_hash"] == "def456"

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_analyze_code_evolution_empty_raises_error(self, git_agent):
        """Análisis de evolución sin traces debe generar error"""
        with pytest.raises(ValueError, match="No Git traces provided"):
            git_agent.analyze_code_evolution("session_123", [])


class TestGitCognitiveCorrelation:
    """Tests para correlación Git-Cognitive"""

    @pytest.fixture
    def sample_git_traces_for_correlation(self):
        """Git traces para correlación"""
        base_time = datetime.now(tz=timezone.utc)
        return [
            GitTrace(
                id=str(uuid4()),
                session_id="session_123",
                student_id="student_001",
                activity_id="prog2_tp1",
                event_type=GitEventType.COMMIT,
                commit_hash="commit1",
                commit_message="Implement enqueue",
                author_name="Student",
                author_email="student@example.com",
                timestamp=base_time - timedelta(minutes=5),
                branch_name="main",
                parent_commits=[],
                files_changed=[],
                total_lines_added=20,
                total_lines_deleted=0,
                diff="",
                is_merge=False,
                is_revert=False,
                detected_patterns=[CodePattern.NORMAL],
                related_cognitive_traces=["trace1"],
            ),
            GitTrace(
                id=str(uuid4()),
                session_id="session_123",
                student_id="student_001",
                activity_id="prog2_tp1",
                event_type=GitEventType.COMMIT,
                commit_hash="commit2",
                commit_message="Add large feature",
                author_name="Student",
                author_email="student@example.com",
                timestamp=base_time + timedelta(hours=2),  # Muy adelante, sin interacciones cercanas
                branch_name="main",
                parent_commits=[],
                files_changed=[],
                total_lines_added=250,
                total_lines_deleted=0,
                diff="",
                is_merge=False,
                is_revert=False,
                detected_patterns=[CodePattern.AI_GENERATED],
                related_cognitive_traces=[],  # Sin trazas relacionadas
            ),
        ]

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_correlate_git_with_cognitive_basic(
        self, git_agent, sample_git_traces_for_correlation, sample_cognitive_traces
    ):
        """Correlación básica Git-Cognitive"""
        result = git_agent.correlate_git_with_cognitive_traces(
            sample_git_traces_for_correlation,
            sample_cognitive_traces
        )

        assert result.session_id == "session_123"
        assert len(result.correlations) == 2  # 2 commits

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_correlate_detects_commits_without_interactions(
        self, git_agent, sample_git_traces_for_correlation, sample_cognitive_traces
    ):
        """Correlación detecta commits sin interacciones cercanas"""
        result = git_agent.correlate_git_with_cognitive_traces(
            sample_git_traces_for_correlation,
            sample_cognitive_traces
        )

        # El segundo commit (2 horas después) no tiene interacciones cercanas
        assert result.commits_without_nearby_interactions >= 1

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_correlate_calculates_interaction_ratio(
        self, git_agent, sample_git_traces_for_correlation, sample_cognitive_traces
    ):
        """Correlación calcula ratio de interacciones por commit"""
        result = git_agent.correlate_git_with_cognitive_traces(
            sample_git_traces_for_correlation,
            sample_cognitive_traces
        )

        assert result.interaction_to_commit_ratio is not None
        # 3 interacciones / 2 commits = 1.5
        assert result.interaction_to_commit_ratio == 1.5

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_correlate_empty_git_traces_raises_error(self, git_agent, sample_cognitive_traces):
        """Correlación sin git traces debe generar error"""
        with pytest.raises(ValueError, match="No Git traces provided"):
            git_agent.correlate_git_with_cognitive_traces([], sample_cognitive_traces)


@pytest.mark.integration
class TestGitIntegrationPersistence:
    """Tests de integración con persistencia"""

    @pytest.mark.skipif(not GIT_AVAILABLE, reason="GitPython not available")
    def test_agent_persists_trace_when_repo_provided(self, mock_git_trace_repo):
        """Agent persiste trace cuando se provee repositorio"""
        agent = GitIntegrationAgent(git_trace_repo=mock_git_trace_repo)

        # Este test solo verifica que el agente tiene el repo
        # Los tests reales de persistencia requieren un repo Git real
        assert agent.git_trace_repo is not None
        assert agent.git_trace_repo == mock_git_trace_repo
