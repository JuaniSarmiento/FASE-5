"""
Router para Git Analytics

FIX Cortez21 DEFECTO 2.1, 2.5: Added authentication and typed response_model
FIX Cortez22 DEFECTO 1.2: Added path validation to prevent command injection
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta
import subprocess
import os
import re
from pydantic import BaseModel

from ..schemas.common import APIResponse
from ..deps import get_current_user

router = APIRouter(prefix="/git-analytics", tags=["Git Analytics"])


# FIX Cortez22 DEFECTO 1.2: Path validation to prevent command injection
def is_safe_git_path(repo_path: str) -> bool:
    """
    Validates that the repository path is safe for git operations.
    Prevents command injection by ensuring the path:
    - Is an absolute path
    - Contains only allowed characters
    - Does not contain shell metacharacters
    - Actually exists and is a directory
    - Contains a .git directory (is a git repository)
    """
    # Check for null bytes (used in some injection attacks)
    if '\x00' in repo_path:
        return False

    # Check for shell metacharacters that could enable injection
    dangerous_chars = ['|', '&', ';', '$', '`', '(', ')', '{', '}', '[', ']', '<', '>', '!', '\n', '\r']
    if any(char in repo_path for char in dangerous_chars):
        return False

    # Check for path traversal attempts
    if '..' in repo_path:
        return False

    # Normalize the path and check it's absolute
    normalized_path = os.path.normpath(repo_path)
    if not os.path.isabs(normalized_path):
        return False

    # Check the path exists and is a directory
    if not os.path.isdir(normalized_path):
        return False

    # Check it's a git repository (has .git directory or is a bare repo)
    git_dir = os.path.join(normalized_path, '.git')
    if not (os.path.isdir(git_dir) or os.path.isfile(os.path.join(normalized_path, 'HEAD'))):
        return False

    return True


# FIX Cortez21 DEFECTO 2.5: Define typed response schema
class ContributorStats(BaseModel):
    name: str
    email: str
    commits: int
    insertions: int
    deletions: int
    percentage: float


class TrendData(BaseModel):
    date: str
    commits: int
    insertions: int
    deletions: int


class GitMetrics(BaseModel):
    total_commits: int
    avg_commits_per_day: float
    total_insertions: int
    total_deletions: int
    code_churn: int
    avg_commit_size: float
    refactoring_ratio: float


class QualityIndicators(BaseModel):
    message_quality_score: float
    avg_message_length: float
    conventional_commits_ratio: float


class GitAnalyticsResponse(BaseModel):
    repository: str
    branch: str
    period: dict
    metrics: GitMetrics
    contributors: List[ContributorStats]
    trends: List[TrendData]
    quality_indicators: QualityIndicators

    class Config:
        from_attributes = True


@router.get(
    "/analytics",
    response_model=APIResponse[GitAnalyticsResponse],  # FIX Cortez21: Typed response_model
    summary="Git Analytics Dashboard",
    description="Obtiene métricas de commits, colaboración y calidad de código del repositorio"
)
async def get_git_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    _current_user: dict = Depends(get_current_user),  # FIX Cortez21 DEFECTO 2.1: Require auth
):
    """
    Obtiene analytics del repositorio Git:
    - Métricas de commits (total, avg/día, churn)
    - Contribuidores con porcentajes
    - Indicadores de calidad (message quality, conventional commits, refactoring ratio)
    - Tendencias temporales
    
    Períodos soportados: 7d, 30d, 90d, 1y
    """
    
    # Determinar rango de fechas
    now = datetime.now()
    if period == "7d":
        days = 7
    elif period == "30d":
        days = 30
    elif period == "90d":
        days = 90
    else:  # 1y
        days = 365
    
    start_date = now - timedelta(days=days)
    
    try:
        # Obtener ruta del repositorio (asumimos que estamos en el repo)
        repo_path = os.getcwd()

        # FIX Cortez22 DEFECTO 1.2: Validate path before git operations
        if not is_safe_git_path(repo_path):
            raise HTTPException(
                status_code=400,
                detail="Invalid repository path: not a valid git repository"
            )

        # Obtener commits del período
        git_log_cmd = [
            "git", "log",
            f"--since={start_date.strftime('%Y-%m-%d')}",
            "--pretty=format:%H|%an|%ae|%s|%ad",
            "--date=iso",
            "--numstat"
        ]
        
        result = subprocess.run(
            git_log_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Git command failed: {result.stderr}")
        
        # Parse commits
        commits_data = []
        contributors = {}
        total_insertions = 0
        total_deletions = 0
        
        lines = result.stdout.split('\n')
        current_commit = None
        
        for line in lines:
            if '|' in line and not line.startswith('+') and not line.startswith('-'):
                parts = line.split('|')
                if len(parts) == 5:
                    commit_hash, author, email, message, date_str = parts
                    current_commit = {
                        "hash": commit_hash,
                        "author": author,
                        "email": email,
                        "message": message,
                        "date": date_str,
                        "insertions": 0,
                        "deletions": 0
                    }
                    commits_data.append(current_commit)
                    
                    if author not in contributors:
                        contributors[author] = {
                            "name": author,
                            "email": email,
                            "commits": 0,
                            "insertions": 0,
                            "deletions": 0
                        }
                    contributors[author]["commits"] += 1
            elif line.strip() and current_commit:
                parts = line.split('\t')
                if len(parts) == 3:
                    try:
                        insertions = int(parts[0]) if parts[0] != '-' else 0
                        deletions = int(parts[1]) if parts[1] != '-' else 0
                        current_commit["insertions"] += insertions
                        current_commit["deletions"] += deletions
                        contributors[current_commit["author"]]["insertions"] += insertions
                        contributors[current_commit["author"]]["deletions"] += deletions
                        total_insertions += insertions
                        total_deletions += deletions
                    except ValueError:
                        pass
        
        # Calcular métricas
        total_commits = len(commits_data)
        avg_commits_per_day = total_commits / days if days > 0 else 0
        code_churn = total_insertions + total_deletions
        avg_commit_size = code_churn / total_commits if total_commits > 0 else 0
        
        # Refactoring ratio (estimación: deletions/insertions ratio cerca de 1 indica refactoring)
        refactoring_ratio = min(total_deletions / total_insertions, 1.0) if total_insertions > 0 else 0
        
        # Calcular porcentajes de contribuidores
        total_contributor_commits = sum(c["commits"] for c in contributors.values())
        contributors_list = []
        for contrib in contributors.values():
            contributors_list.append({
                **contrib,
                "percentage": (contrib["commits"] / total_contributor_commits * 100) if total_contributor_commits > 0 else 0
            })
        
        # Ordenar por commits desc
        contributors_list.sort(key=lambda x: x["commits"], reverse=True)
        
        # Calcular tendencias (agrupadas por día)
        trends = {}
        for commit in commits_data:
            date_str = commit["date"][:10]  # YYYY-MM-DD
            if date_str not in trends:
                trends[date_str] = {
                    "date": date_str,
                    "commits": 0,
                    "insertions": 0,
                    "deletions": 0
                }
            trends[date_str]["commits"] += 1
            trends[date_str]["insertions"] += commit["insertions"]
            trends[date_str]["deletions"] += commit["deletions"]
        
        trends_list = sorted(trends.values(), key=lambda x: x["date"])
        
        # Quality indicators
        conventional_commits = sum(
            1 for c in commits_data
            if any(c["message"].startswith(prefix) for prefix in ["feat:", "fix:", "docs:", "style:", "refactor:", "test:", "chore:"])
        )
        conventional_commits_ratio = conventional_commits / total_commits if total_commits > 0 else 0
        
        avg_message_length = sum(len(c["message"]) for c in commits_data) / total_commits if total_commits > 0 else 0
        
        # Message quality score (0-100)
        message_quality_score = min(
            (conventional_commits_ratio * 50) +  # 50 points for conventional commits
            (min(avg_message_length / 50, 1.0) * 50),  # 50 points for descriptive messages
            100
        )
        
        # Get current branch
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "main"
        
        analytics = {
            "repository": os.path.basename(repo_path),
            "branch": current_branch,
            "period": {
                "start": start_date.isoformat(),
                "end": now.isoformat()
            },
            "metrics": {
                "total_commits": total_commits,
                "avg_commits_per_day": round(avg_commits_per_day, 2),
                "total_insertions": total_insertions,
                "total_deletions": total_deletions,
                "code_churn": code_churn,
                "avg_commit_size": round(avg_commit_size, 2),
                "refactoring_ratio": round(refactoring_ratio, 2)
            },
            "contributors": contributors_list[:10],  # Top 10
            "trends": trends_list[-30:],  # Last 30 days
            "quality_indicators": {
                "message_quality_score": round(message_quality_score, 2),
                "avg_message_length": round(avg_message_length, 2),
                "conventional_commits_ratio": round(conventional_commits_ratio, 2)
            }
        }
        
        return APIResponse(
            success=True,
            message="Git analytics retrieved successfully",
            data=analytics
        )
        
    except Exception as e:
        # Fallback: datos de demo
        analytics = {
            "repository": "FASE-3.1",
            "branch": "main",
            "period": {
                "start": start_date.isoformat(),
                "end": now.isoformat()
            },
            "metrics": {
                "total_commits": 127,
                "avg_commits_per_day": 4.2,
                "total_insertions": 15678,
                "total_deletions": 5432,
                "code_churn": 21110,
                "avg_commit_size": 166.2,
                "refactoring_ratio": 0.35
            },
            "contributors": [
                {
                    "name": "Developer 1",
                    "email": "dev1@example.com",
                    "commits": 87,
                    "insertions": 12340,
                    "deletions": 4100,
                    "percentage": 68.5
                },
                {
                    "name": "Developer 2",
                    "email": "dev2@example.com",
                    "commits": 40,
                    "insertions": 3338,
                    "deletions": 1332,
                    "percentage": 31.5
                }
            ],
            "trends": [
                {"date": (now - timedelta(days=i)).strftime("%Y-%m-%d"), "commits": 3 + (i % 5), "insertions": 450, "deletions": 180}
                for i in range(15, -1, -1)
            ],
            "quality_indicators": {
                "message_quality_score": 72.5,
                "avg_message_length": 48.3,
                "conventional_commits_ratio": 0.65
            }
        }
        
        return APIResponse(
            success=True,
            message=f"Git analytics retrieved (demo mode): {str(e)}",
            data=analytics
        )
