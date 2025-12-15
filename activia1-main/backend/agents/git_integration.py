"""
GitIntegrationAgent - SPRINT 5 HU-SYS-008

Agente responsable de integración con Git para trazabilidad N2 (nivel técnico).

Funcionalidades:
- Capturar eventos Git (commits, branches, merges)
- Analizar cambios en código (diffs, archivos modificados, métricas)
- Detectar patrones (copy-paste, código generado por IA, debugging)
- Correlacionar eventos Git con trazas N3/N4 (cognitivas)

IMPORTANTE: Este agente NO modifica el repositorio Git del estudiante,
solo CAPTURA y ANALIZA eventos para trazabilidad.
"""

import logging
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
from uuid import uuid4

try:
    from git import Repo, Commit, GitCommandError
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    # Mock types when GitPython is not available
    Commit = Any
    Repo = Any
    GitCommandError = Exception
    logging.warning(
        "GitPython not installed. Git integration disabled. "
        "Install with: pip install GitPython"
    )

from ..models.git_trace import (
    GitTrace,
    GitEventType,
    GitFileChange,
    CodePattern,
    CodeEvolution,
    GitN2CorrelationResult,
)
from ..database.repositories import GitTraceRepository
from ..models.trace import CognitiveTrace

logger = logging.getLogger(__name__)


class GitIntegrationAgent:
    """
    Agente de integración Git para trazabilidad N2

    Captura eventos Git y los correlaciona con trazas cognitivas (N4)
    para reconstruir el proceso completo de desarrollo.
    """

    def __init__(self, git_trace_repo: Optional[GitTraceRepository] = None):
        """
        Initialize GitIntegrationAgent

        Args:
            git_trace_repo: Repository for persisting Git traces (optional)
        """
        if not GIT_AVAILABLE:
            raise RuntimeError(
                "GitPython is required for GitIntegrationAgent. "
                "Install with: pip install GitPython"
            )

        self.git_trace_repo = git_trace_repo

    def capture_commit(
        self,
        repo_path: str,
        commit_hash: str,
        session_id: str,
        student_id: str,
        activity_id: str,
        cognitive_traces: Optional[List[CognitiveTrace]] = None,
    ) -> GitTrace:
        """
        Capture a Git commit as a N2-level trace

        Args:
            repo_path: Path to Git repository
            commit_hash: SHA-1 hash of the commit
            session_id: Associated learning session ID
            student_id: Student ID
            activity_id: Activity ID
            cognitive_traces: Related N4 cognitive traces for correlation

        Returns:
            GitTrace instance

        Raises:
            GitCommandError: If repository or commit not found
        """
        repo = Repo(repo_path)
        commit = repo.commit(commit_hash)

        # Extract Git metadata
        event_type = self._detect_event_type(commit)
        files_changed = self._extract_file_changes(commit)
        total_lines_added = sum(f.lines_added for f in files_changed)
        total_lines_deleted = sum(f.lines_deleted for f in files_changed)
        diff = self._get_commit_diff(commit)

        # Analyze patterns
        detected_patterns = self._detect_code_patterns(commit, diff)

        # Correlate with cognitive traces (N3/N4)
        correlation = self._correlate_with_cognitive_traces(
            commit, cognitive_traces or []
        )

        # Create GitTrace
        git_trace = GitTrace(
            id=str(uuid4()),
            session_id=session_id,
            student_id=student_id,
            activity_id=activity_id,
            event_type=event_type,
            commit_hash=commit_hash,
            commit_message=commit.message.strip(),
            author_name=commit.author.name,
            author_email=commit.author.email,
            timestamp=datetime.fromtimestamp(commit.committed_date, tz=timezone.utc),
            branch_name=self._get_branch_name(repo, commit),
            parent_commits=[p.hexsha for p in commit.parents],
            files_changed=files_changed,
            total_lines_added=total_lines_added,
            total_lines_deleted=total_lines_deleted,
            diff=diff,
            is_merge=len(commit.parents) > 1,
            is_revert="revert" in commit.message.lower(),
            detected_patterns=detected_patterns,
            # TODO(TECH-DEBT): Implement cyclomatic complexity analysis
            # Requires: radon library (pip install radon)
            # Use: radon.complexity.cc_visit() on Python files
            # Calculate delta between parent commit and current
            complexity_delta=None,
            related_cognitive_traces=correlation["related_trace_ids"],
            cognitive_state_during_commit=correlation.get("cognitive_state"),
            time_since_last_interaction_minutes=correlation.get(
                "time_since_last_interaction_minutes"
            ),
            repo_path=repo_path,
            remote_url=self._get_remote_url(repo),
        )

        # Persist to database if repository is available
        if self.git_trace_repo:
            self.git_trace_repo.create(
                session_id=git_trace.session_id,
                student_id=git_trace.student_id,
                activity_id=git_trace.activity_id,
                event_type=git_trace.event_type.value,
                commit_hash=git_trace.commit_hash,
                commit_message=git_trace.commit_message,
                author_name=git_trace.author_name,
                author_email=git_trace.author_email,
                timestamp=git_trace.timestamp,
                branch_name=git_trace.branch_name,
                parent_commits=git_trace.parent_commits,
                files_changed=[f.model_dump() for f in git_trace.files_changed],
                total_lines_added=git_trace.total_lines_added,
                total_lines_deleted=git_trace.total_lines_deleted,
                diff=git_trace.diff,
                is_merge=git_trace.is_merge,
                is_revert=git_trace.is_revert,
                detected_patterns=[p.value for p in git_trace.detected_patterns],
                complexity_delta=git_trace.complexity_delta,
                related_cognitive_traces=git_trace.related_cognitive_traces,
                cognitive_state_during_commit=git_trace.cognitive_state_during_commit,
                time_since_last_interaction_minutes=git_trace.time_since_last_interaction_minutes,
                repo_path=git_trace.repo_path,
                remote_url=git_trace.remote_url,
            )

        logger.info(
            "Git commit captured",
            extra={
                "commit_hash": commit_hash,
                "session_id": session_id,
                "patterns": [p.value for p in detected_patterns],
            },
        )
        return git_trace

    def capture_session_commits(
        self,
        repo_path: str,
        session_id: str,
        student_id: str,
        activity_id: str,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        cognitive_traces: Optional[List[CognitiveTrace]] = None,
    ) -> List[GitTrace]:
        """
        Capture all commits in a time window (typically a learning session)

        Args:
            repo_path: Path to Git repository
            session_id: Session ID
            student_id: Student ID
            activity_id: Activity ID
            since: Start datetime (optional)
            until: End datetime (optional)
            cognitive_traces: N4 traces for correlation

        Returns:
            List of GitTrace instances
        """
        repo = Repo(repo_path)
        commits = list(repo.iter_commits(since=since, until=until))

        git_traces = []
        for commit in commits:
            try:
                git_trace = self.capture_commit(
                    repo_path=repo_path,
                    commit_hash=commit.hexsha,
                    session_id=session_id,
                    student_id=student_id,
                    activity_id=activity_id,
                    cognitive_traces=cognitive_traces,
                )
                git_traces.append(git_trace)
            except Exception as e:
                logger.error(
                    f"Error capturing commit {commit.hexsha}: {e}",
                    exc_info=True,
                    extra={"commit_hash": commit.hexsha, "session_id": session_id},
                )

        logger.info(
            f"Captured {len(git_traces)} commits for session",
            extra={"session_id": session_id, "total_commits": len(git_traces)},
        )
        return git_traces

    def analyze_code_evolution(
        self, session_id: str, git_traces: List[GitTrace]
    ) -> CodeEvolution:
        """
        Analyze code evolution during a session

        Args:
            session_id: Session ID
            git_traces: List of GitTrace instances

        Returns:
            CodeEvolution analysis
        """
        if not git_traces:
            raise ValueError("No Git traces provided for analysis")

        # Extract student_id and activity_id from first trace
        first_trace = git_traces[0]

        # Aggregate metrics
        total_commits = len(git_traces)
        total_lines_added = sum(t.total_lines_added for t in git_traces)
        total_lines_deleted = sum(t.total_lines_deleted for t in git_traces)
        net_lines_change = total_lines_added - total_lines_deleted

        # Files
        all_files = set()
        for trace in git_traces:
            for file_change in trace.files_changed:
                all_files.add(file_change.file_path)
        files_modified = list(all_files)
        unique_files_count = len(all_files)

        # Pattern distribution
        pattern_distribution: Dict[str, int] = {}
        for trace in git_traces:
            for pattern in trace.detected_patterns:
                pattern_key = pattern.value
                pattern_distribution[pattern_key] = (
                    pattern_distribution.get(pattern_key, 0) + 1
                )

        # Commit timeline
        commit_timeline = [
            {
                "commit_hash": t.commit_hash,
                "timestamp": t.timestamp.isoformat(),
                "message": t.commit_message,
                "lines_added": t.total_lines_added,
                "lines_deleted": t.total_lines_deleted,
            }
            for t in git_traces
        ]

        # Commits by cognitive state
        commits_by_cognitive_state: Dict[str, int] = {}
        for trace in git_traces:
            if trace.cognitive_state_during_commit:
                state = trace.cognitive_state_during_commit
                commits_by_cognitive_state[state] = (
                    commits_by_cognitive_state.get(state, 0) + 1
                )

        # Commit frequency by hour
        commit_frequency: Dict[str, int] = {}
        for trace in git_traces:
            hour_key = trace.timestamp.strftime("%Y-%m-%d %H:00")
            commit_frequency[hour_key] = commit_frequency.get(hour_key, 0) + 1

        evolution = CodeEvolution(
            session_id=session_id,
            student_id=first_trace.student_id,
            activity_id=first_trace.activity_id,
            total_commits=total_commits,
            total_lines_added=total_lines_added,
            total_lines_deleted=total_lines_deleted,
            net_lines_change=net_lines_change,
            files_modified=files_modified,
            unique_files_count=unique_files_count,
            pattern_distribution=pattern_distribution,
            commit_timeline=commit_timeline,
            commit_frequency=commit_frequency,
            commits_by_cognitive_state=commits_by_cognitive_state,
        )

        logger.info(
            "Code evolution analysis completed",
            extra={
                "session_id": session_id,
                "total_commits": total_commits,
                "unique_files": unique_files_count,
            },
        )
        return evolution

    def correlate_git_with_cognitive_traces(
        self, git_traces: List[GitTrace], cognitive_traces: List[CognitiveTrace]
    ) -> GitN2CorrelationResult:
        """
        Correlate Git events (N2) with cognitive traces (N3/N4)

        Finds temporal relationships between commits and AI interactions
        to identify patterns like:
        - Commits immediately after AI assistance
        - Commits without nearby interactions (possible external AI use)
        - Cognitive state during commits

        Args:
            git_traces: List of Git N2 traces
            cognitive_traces: List of cognitive N4 traces

        Returns:
            GitN2CorrelationResult with correlations
        """
        if not git_traces:
            raise ValueError("No Git traces provided")

        session_id = git_traces[0].session_id

        correlations = []
        time_diffs = []
        commits_without_nearby_interactions = 0
        interaction_count = len(cognitive_traces)

        for git_trace in git_traces:
            # Find nearest cognitive traces within ±30 min window
            nearby_traces = self._find_nearby_traces(
                git_trace.timestamp, cognitive_traces, window_minutes=30
            )

            if not nearby_traces:
                commits_without_nearby_interactions += 1

            correlations.append(
                {
                    "commit_hash": git_trace.commit_hash,
                    "commit_timestamp": git_trace.timestamp.isoformat(),
                    "commit_message": git_trace.commit_message,
                    "cognitive_traces_nearby": [
                        {
                            "trace_id": t.id,
                            "cognitive_state": (
                                t.cognitive_state.value
                                if hasattr(t.cognitive_state, 'value')
                                else t.cognitive_state
                            )
                            if t.cognitive_state
                            else None,
                            "timestamp": t.timestamp.isoformat(),
                            "time_diff_minutes": int(
                                abs(
                                    (git_trace.timestamp - t.timestamp).total_seconds()
                                    / 60
                                )
                            ),
                            "interaction_type": t.interaction_type.value,
                            "content_preview": t.content[:100] + "..."
                            if len(t.content) > 100
                            else t.content,
                        }
                        for t in nearby_traces
                    ],
                }
            )

            # Track time differences for average calculation
            if nearby_traces:
                nearest_trace = min(
                    nearby_traces,
                    key=lambda t: abs((git_trace.timestamp - t.timestamp).total_seconds()),
                )
                time_diff_minutes = abs(
                    (git_trace.timestamp - nearest_trace.timestamp).total_seconds() / 60
                )
                time_diffs.append(time_diff_minutes)

        avg_time_between = sum(time_diffs) / len(time_diffs) if time_diffs else None
        ratio = (
            interaction_count / len(git_traces) if len(git_traces) > 0 else None
        )

        result = GitN2CorrelationResult(
            session_id=session_id,
            correlations=correlations,
            avg_time_between_commit_and_interaction=avg_time_between,
            commits_without_nearby_interactions=commits_without_nearby_interactions,
            interaction_to_commit_ratio=ratio,
        )

        logger.info(
            "Git-Cognitive correlation completed",
            extra={
                "session_id": session_id,
                "correlations": len(correlations),
                "commits_without_interactions": commits_without_nearby_interactions,
            },
        )
        return result

    # ==========================================================================
    # PRIVATE METHODS
    # ==========================================================================

    def _detect_event_type(self, commit: Commit) -> GitEventType:
        """Detect the type of Git event"""
        if len(commit.parents) > 1:
            return GitEventType.MERGE
        if "revert" in commit.message.lower():
            return GitEventType.REVERT
        return GitEventType.COMMIT

    def _extract_file_changes(self, commit: Commit) -> List[GitFileChange]:
        """Extract file changes from a commit"""
        changes = []

        # Get parent commit for diff
        if commit.parents:
            parent = commit.parents[0]
            diffs = parent.diff(commit, create_patch=True)
        else:
            # First commit: compare to null tree
            diffs = commit.diff(None, create_patch=True)

        for diff in diffs:
            # Determine change type
            if diff.new_file:
                change_type = "added"
            elif diff.deleted_file:
                change_type = "deleted"
            elif diff.renamed_file:
                change_type = "renamed"
            else:
                change_type = "modified"

            # Extract line counts from diff stats
            lines_added = 0
            lines_deleted = 0
            if hasattr(diff, 'diff') and diff.diff:
                diff_text = diff.diff.decode('utf-8', errors='ignore')
                lines_added = diff_text.count('\n+') - diff_text.count('\n+++')
                lines_deleted = diff_text.count('\n-') - diff_text.count('\n---')

            # Determine if binary
            is_binary = diff.b_blob and diff.b_blob.data_stream.read(8192).find(b'\x00') != -1 if diff.b_blob else False

            changes.append(
                GitFileChange(
                    file_path=diff.b_path or diff.a_path,
                    change_type=change_type,
                    lines_added=max(0, lines_added),
                    lines_deleted=max(0, lines_deleted),
                    is_binary=is_binary,
                )
            )

        return changes

    def _get_commit_diff(self, commit: Commit) -> str:
        """Get full diff text for a commit"""
        try:
            if commit.parents:
                parent = commit.parents[0]
                diffs = parent.diff(commit, create_patch=True)
            else:
                diffs = commit.diff(None, create_patch=True)

            diff_text = ""
            for diff in diffs:
                if hasattr(diff, 'diff') and diff.diff:
                    diff_text += diff.diff.decode('utf-8', errors='ignore') + "\n"
            return diff_text[:10000]  # Limit to 10KB
        except Exception as e:
            logger.warning(f"Error extracting diff: {e}")
            return ""

    def _detect_code_patterns(
        self, commit: Commit, diff: str
    ) -> List[CodePattern]:
        """
        Detect patterns in code changes

        Patterns:
        - COPY_PASTE: Large blocks of similar code added
        - AI_GENERATED: Very large additions in single commit
        - DEBUGGING: Print statements, console.log, etc.
        - COMMENTED_CODE: Large blocks of commented code
        """
        patterns = []

        # Large additions (> 200 lines) might indicate AI generation
        total_additions = diff.count('\n+')
        if total_additions > 200:
            patterns.append(CodePattern.AI_GENERATED)

        # Detect debugging code
        debug_patterns = [
            r'print\s*\(',
            r'console\.log\s*\(',
            r'System\.out\.println\s*\(',
            r'fmt\.Println\s*\(',
            r'echo\s+',
            r'var_dump\s*\(',
        ]
        if any(re.search(pattern, diff, re.IGNORECASE) for pattern in debug_patterns):
            patterns.append(CodePattern.DEBUGGING)

        # Detect commented code
        comment_lines = len(re.findall(r'^\+\s*(#|//|/\*)', diff, re.MULTILINE))
        if comment_lines > 20:
            patterns.append(CodePattern.COMMENTED_CODE)

        # Detect refactoring (high deletion/addition ratio with similar names)
        deletions = diff.count('\n-')
        additions = diff.count('\n+')
        if deletions > 50 and additions > 50 and abs(deletions - additions) < 20:
            patterns.append(CodePattern.REFACTORING)

        # Default: normal commit
        if not patterns:
            patterns.append(CodePattern.NORMAL)

        return patterns

    def _correlate_with_cognitive_traces(
        self, commit: Commit, cognitive_traces: List[CognitiveTrace]
    ) -> Dict[str, Any]:
        """
        Find nearest cognitive traces to a commit

        Returns:
            Dict with:
            - related_trace_ids: List of trace IDs
            - cognitive_state: State from nearest trace
            - time_since_last_interaction_minutes: Minutes since last trace
        """
        commit_time = datetime.fromtimestamp(commit.committed_date, tz=timezone.utc)
        nearby_traces = self._find_nearby_traces(
            commit_time, cognitive_traces, window_minutes=30
        )

        if not nearby_traces:
            return {"related_trace_ids": []}

        # Find nearest trace
        nearest = min(
            nearby_traces,
            key=lambda t: abs((commit_time - t.timestamp).total_seconds()),
        )

        time_diff = int(
            abs((commit_time - nearest.timestamp).total_seconds() / 60)
        )

        return {
            "related_trace_ids": [t.id for t in nearby_traces],
            "cognitive_state": (
                nearest.cognitive_state.value
                if hasattr(nearest.cognitive_state, 'value')
                else nearest.cognitive_state
            )
            if nearest.cognitive_state
            else None,
            "time_since_last_interaction_minutes": time_diff,
        }

    def _find_nearby_traces(
        self,
        timestamp: datetime,
        traces: List[CognitiveTrace],
        window_minutes: int = 30,
    ) -> List[CognitiveTrace]:
        """Find traces within a time window"""
        window = timedelta(minutes=window_minutes)
        nearby = []
        for trace in traces:
            time_diff = abs((timestamp - trace.timestamp).total_seconds())
            if time_diff <= window.total_seconds():
                nearby.append(trace)
        return nearby

    def _get_branch_name(self, repo: Repo, commit: Commit) -> str:
        """Get branch name for a commit"""
        try:
            branches = repo.git.branch("--contains", commit.hexsha)
            if branches:
                # Extract first branch name
                return branches.split('\n')[0].strip().lstrip('* ')
            return "unknown"
        except (GitCommandError, AttributeError, IndexError) as e:
            logger.debug(f"Failed to get current branch: {e}")
            return "unknown"

    def _get_remote_url(self, repo: Repo) -> Optional[str]:
        """Get remote URL for repository"""
        try:
            if repo.remotes:
                return repo.remotes.origin.url
            return None
        except (GitCommandError, AttributeError) as e:
            logger.debug(f"Failed to get remote URL: {e}")
            return None
