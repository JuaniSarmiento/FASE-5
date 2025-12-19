"""
Minimal ExerciseLoader implementation for EasyPanel deployment.
Returns empty/mock data to prevent import errors.
"""
from typing import List, Dict, Any, Optional


class ExerciseLoader:
    """Minimal loader that returns empty data to prevent crashes."""

    def __init__(self):
        """Initialize with empty exercises."""
        self.exercises = []

    def search(
        self,
        difficulty: Optional[str] = None,
        topic: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """Return empty list of exercises."""
        return []

    def get_stats(self) -> Dict[str, Any]:
        """Return empty stats."""
        return {
            "total": 0,
            "by_difficulty": {},
            "by_topic": {},
            "by_language": {}
        }

    def get_available_filters(self) -> Dict[str, List[str]]:
        """Return empty filters."""
        return {
            "difficulties": [],
            "topics": [],
            "languages": []
        }

    def get_by_id(self, exercise_id: str) -> Optional[Dict[str, Any]]:
        """Return None (exercise not found)."""
        return None
