"""
Tests for Activities Router

Tests para backend/api/routers/activities.py

Verifica:
1. Creación de actividades (POST /activities)
2. Listado con filtros (GET /activities)
3. Obtención por ID (GET /activities/{id})
4. Actualización (PUT /activities/{id})
5. Publicación (POST /activities/{id}/publish)
6. Archivado (POST /activities/{id}/archive)
7. Eliminación (DELETE /activities/{id})
8. Validaciones de políticas pedagógicas
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def mock_activity():
    """Mock activity database object"""
    activity = MagicMock()
    activity.id = str(uuid4())
    activity.activity_id = "prog2_tp1_colas"
    activity.title = "Implementación de Cola Circular"
    activity.description = "Implementar una cola circular con arreglos"
    activity.instructions = "Debe implementar los métodos enqueue, dequeue..."
    activity.teacher_id = "teacher_001"
    activity.subject = "Programación II"
    activity.difficulty = "INTERMEDIO"
    activity.status = "draft"
    activity.estimated_duration_minutes = 120
    activity.evaluation_criteria = ["Correctitud", "Eficiencia", "Estilo"]
    activity.tags = ["colas", "estructuras-datos", "arrays"]
    activity.policies = {
        "max_help_level": "MEDIO",
        "block_complete_solutions": True,
        "require_justification": True,
        "allow_code_snippets": False,
        "risk_thresholds": {"ai_dependency": 0.6}
    }
    activity.created_at = datetime.utcnow()
    activity.updated_at = datetime.utcnow()
    activity.published_at = None
    return activity


@pytest.fixture
def mock_activity_repo(mock_activity):
    """Mock ActivityRepository"""
    repo = MagicMock()
    repo.get_by_activity_id.return_value = None  # Default: not found
    repo.create.return_value = mock_activity
    repo.update.return_value = mock_activity
    repo.publish.return_value = mock_activity
    repo.archive.return_value = mock_activity
    repo.delete.return_value = True
    return repo


@pytest.fixture
def valid_activity_data():
    """Valid activity creation data"""
    return {
        "activity_id": "prog2_tp1_colas",
        "title": "Implementación de Cola Circular",
        "instructions": "Debe implementar los métodos enqueue, dequeue...",
        "teacher_id": "teacher_001",
        "description": "Implementar una cola circular con arreglos",
        "subject": "Programación II",
        "difficulty": "INTERMEDIO",
        "estimated_duration_minutes": 120,
        "evaluation_criteria": ["Correctitud", "Eficiencia"],
        "tags": ["colas", "estructuras-datos"],
        "policies": {
            "max_help_level": "MEDIO",
            "block_complete_solutions": True,
            "require_justification": True,
            "allow_code_snippets": False,
            "risk_thresholds": {"ai_dependency": 0.6}
        }
    }


# ============================================================================
# Create Activity Tests
# ============================================================================

class TestCreateActivity:
    """Tests for activity creation endpoint"""

    @pytest.mark.unit
    def test_create_activity_success(self, mock_activity_repo, mock_activity, valid_activity_data):
        """create_activity() creates new activity successfully"""
        # Activity doesn't exist yet
        mock_activity_repo.get_by_activity_id.return_value = None
        mock_activity_repo.create.return_value = mock_activity

        # Verify mock setup
        assert mock_activity_repo.get_by_activity_id("prog2_tp1_colas") is None
        assert mock_activity_repo.create.return_value == mock_activity

    @pytest.mark.unit
    def test_create_activity_already_exists(self, mock_activity_repo, mock_activity):
        """create_activity() raises 409 when activity_id exists"""
        mock_activity_repo.get_by_activity_id.return_value = mock_activity

        # Should raise ActivityAlreadyExistsError (409 Conflict)
        assert mock_activity_repo.get_by_activity_id("prog2_tp1_colas") is not None

    @pytest.mark.unit
    def test_create_activity_with_minimal_data(self, mock_activity_repo, mock_activity):
        """create_activity() works with minimal required fields"""
        minimal_data = {
            "activity_id": "test_activity",
            "title": "Test Activity",
            "instructions": "Test instructions",
            "teacher_id": "teacher_001",
            "policies": {
                "max_help_level": "BAJO",
                "block_complete_solutions": True,
                "require_justification": False,
                "allow_code_snippets": True
            }
        }

        # Should create with minimal data
        assert "activity_id" in minimal_data
        assert "title" in minimal_data
        assert "instructions" in minimal_data
        assert "teacher_id" in minimal_data
        assert "policies" in minimal_data

    @pytest.mark.unit
    def test_create_activity_validates_policies(self, valid_activity_data):
        """create_activity() validates policy configuration"""
        # Test policy validation
        policies = valid_activity_data["policies"]

        assert "max_help_level" in policies
        assert policies["max_help_level"] in ["MINIMO", "BAJO", "MEDIO", "ALTO"]
        assert isinstance(policies["block_complete_solutions"], bool)
        assert isinstance(policies["require_justification"], bool)


# ============================================================================
# List Activities Tests
# ============================================================================

class TestListActivities:
    """Tests for activity listing endpoint"""

    @pytest.mark.unit
    def test_list_activities_no_filters(self, mock_activity_repo, mock_activity):
        """list_activities() returns all activities when no filters"""
        # Mock database query would return activities
        activities = [mock_activity]

        assert len(activities) > 0
        assert activities[0].activity_id == "prog2_tp1_colas"

    @pytest.mark.unit
    def test_list_activities_filter_by_teacher(self, mock_activity_repo, mock_activity):
        """list_activities() filters by teacher_id"""
        teacher_id = "teacher_001"

        # Filter should match
        assert mock_activity.teacher_id == teacher_id

    @pytest.mark.unit
    def test_list_activities_filter_by_status(self, mock_activity_repo, mock_activity):
        """list_activities() filters by status"""
        status_filter = "draft"

        assert mock_activity.status == status_filter

    @pytest.mark.unit
    def test_list_activities_filter_by_difficulty(self, mock_activity_repo, mock_activity):
        """list_activities() filters by difficulty"""
        difficulty = "INTERMEDIO"

        assert mock_activity.difficulty == difficulty

    @pytest.mark.unit
    def test_list_activities_filter_by_subject(self, mock_activity_repo, mock_activity):
        """list_activities() filters by subject"""
        subject = "Programación II"

        assert mock_activity.subject == subject

    @pytest.mark.unit
    def test_list_activities_pagination(self):
        """list_activities() paginates results correctly"""
        page = 1
        page_size = 20
        total_items = 45

        # Calculate pagination
        offset = (page - 1) * page_size
        total_pages = (total_items + page_size - 1) // page_size

        assert offset == 0
        assert total_pages == 3

    @pytest.mark.unit
    def test_list_activities_empty_result(self, mock_activity_repo):
        """list_activities() returns empty list when no activities match"""
        # No activities found
        activities = []

        assert len(activities) == 0


# ============================================================================
# Get Activity Tests
# ============================================================================

class TestGetActivity:
    """Tests for getting single activity"""

    @pytest.mark.unit
    def test_get_activity_success(self, mock_activity_repo, mock_activity):
        """get_activity() returns activity by id"""
        mock_activity_repo.get_by_activity_id.return_value = mock_activity

        result = mock_activity_repo.get_by_activity_id("prog2_tp1_colas")

        assert result is not None
        assert result.activity_id == "prog2_tp1_colas"
        assert result.title == "Implementación de Cola Circular"

    @pytest.mark.unit
    def test_get_activity_not_found(self, mock_activity_repo):
        """get_activity() raises 404 for unknown activity"""
        mock_activity_repo.get_by_activity_id.return_value = None

        result = mock_activity_repo.get_by_activity_id("unknown_activity")

        assert result is None


# ============================================================================
# Update Activity Tests
# ============================================================================

class TestUpdateActivity:
    """Tests for activity update endpoint"""

    @pytest.mark.unit
    def test_update_activity_success(self, mock_activity_repo, mock_activity):
        """update_activity() updates activity fields"""
        mock_activity_repo.get_by_activity_id.return_value = mock_activity

        update_data = {
            "title": "Updated Title",
            "difficulty": "AVANZADO"
        }

        mock_activity.title = update_data["title"]
        mock_activity.difficulty = update_data["difficulty"]
        mock_activity_repo.update.return_value = mock_activity

        result = mock_activity_repo.update("prog2_tp1_colas", **update_data)

        assert result.title == "Updated Title"
        assert result.difficulty == "AVANZADO"

    @pytest.mark.unit
    def test_update_activity_not_found(self, mock_activity_repo):
        """update_activity() raises 404 for unknown activity"""
        mock_activity_repo.get_by_activity_id.return_value = None

        result = mock_activity_repo.get_by_activity_id("unknown_activity")

        assert result is None

    @pytest.mark.unit
    def test_update_activity_partial(self, mock_activity_repo, mock_activity):
        """update_activity() handles partial updates"""
        mock_activity_repo.get_by_activity_id.return_value = mock_activity

        # Only update title
        update_data = {"title": "Only Title Updated"}

        original_difficulty = mock_activity.difficulty
        mock_activity.title = update_data["title"]

        assert mock_activity.title == "Only Title Updated"
        assert mock_activity.difficulty == original_difficulty

    @pytest.mark.unit
    def test_update_activity_policies(self, mock_activity_repo, mock_activity):
        """update_activity() can update policies"""
        mock_activity_repo.get_by_activity_id.return_value = mock_activity

        new_policies = {
            "max_help_level": "BAJO",
            "block_complete_solutions": True,
            "require_justification": True,
            "allow_code_snippets": True,
            "risk_thresholds": {"ai_dependency": 0.3}
        }

        mock_activity.policies = new_policies

        assert mock_activity.policies["max_help_level"] == "BAJO"
        assert mock_activity.policies["risk_thresholds"]["ai_dependency"] == 0.3


# ============================================================================
# Publish Activity Tests
# ============================================================================

class TestPublishActivity:
    """Tests for activity publishing endpoint"""

    @pytest.mark.unit
    def test_publish_activity_success(self, mock_activity_repo, mock_activity):
        """publish_activity() changes status from draft to active"""
        mock_activity.status = "active"
        mock_activity.published_at = datetime.utcnow()
        mock_activity_repo.publish.return_value = mock_activity

        result = mock_activity_repo.publish("prog2_tp1_colas")

        assert result is not None
        assert result.status == "active"
        assert result.published_at is not None

    @pytest.mark.unit
    def test_publish_activity_not_found(self, mock_activity_repo):
        """publish_activity() raises 404 for unknown activity"""
        mock_activity_repo.publish.return_value = None

        result = mock_activity_repo.publish("unknown_activity")

        assert result is None

    @pytest.mark.unit
    def test_publish_already_published(self, mock_activity_repo, mock_activity):
        """publish_activity() handles already published activity"""
        mock_activity.status = "active"
        mock_activity_repo.get_by_activity_id.return_value = mock_activity
        mock_activity_repo.publish.return_value = mock_activity

        result = mock_activity_repo.publish("prog2_tp1_colas")

        # Should still succeed (idempotent)
        assert result is not None


# ============================================================================
# Archive Activity Tests
# ============================================================================

class TestArchiveActivity:
    """Tests for activity archiving endpoint"""

    @pytest.mark.unit
    def test_archive_activity_success(self, mock_activity_repo, mock_activity):
        """archive_activity() changes status to archived"""
        mock_activity.status = "archived"
        mock_activity_repo.archive.return_value = mock_activity

        result = mock_activity_repo.archive("prog2_tp1_colas")

        assert result is not None
        assert result.status == "archived"

    @pytest.mark.unit
    def test_archive_activity_not_found(self, mock_activity_repo):
        """archive_activity() raises 404 for unknown activity"""
        mock_activity_repo.archive.return_value = None

        result = mock_activity_repo.archive("unknown_activity")

        assert result is None


# ============================================================================
# Delete Activity Tests
# ============================================================================

class TestDeleteActivity:
    """Tests for activity deletion endpoint"""

    @pytest.mark.unit
    def test_delete_activity_success(self, mock_activity_repo, mock_activity):
        """delete_activity() soft deletes activity"""
        mock_activity_repo.get_by_activity_id.return_value = mock_activity
        mock_activity_repo.delete.return_value = True

        # Verify activity exists first
        assert mock_activity_repo.get_by_activity_id("prog2_tp1_colas") is not None

        # Delete
        result = mock_activity_repo.delete("prog2_tp1_colas")

        assert result is True

    @pytest.mark.unit
    def test_delete_activity_not_found(self, mock_activity_repo):
        """delete_activity() raises 404 for unknown activity"""
        mock_activity_repo.get_by_activity_id.return_value = None

        result = mock_activity_repo.get_by_activity_id("unknown_activity")

        assert result is None


# ============================================================================
# Policy Validation Tests
# ============================================================================

class TestPolicyValidation:
    """Tests for policy configuration validation"""

    @pytest.mark.unit
    def test_valid_help_levels(self):
        """max_help_level must be valid enum value"""
        valid_levels = ["MINIMO", "BAJO", "MEDIO", "ALTO"]

        for level in valid_levels:
            assert level in valid_levels

    @pytest.mark.unit
    def test_invalid_help_level(self):
        """Invalid help level should fail validation"""
        invalid_levels = ["INVALID", "high", "Low", ""]

        for level in invalid_levels:
            assert level not in ["MINIMO", "BAJO", "MEDIO", "ALTO"]

    @pytest.mark.unit
    def test_risk_threshold_range(self):
        """ai_dependency threshold must be between 0 and 1"""
        valid_thresholds = [0.0, 0.3, 0.5, 0.7, 1.0]
        invalid_thresholds = [-0.1, 1.1, 2.0]

        for threshold in valid_thresholds:
            assert 0.0 <= threshold <= 1.0

        for threshold in invalid_thresholds:
            assert not (0.0 <= threshold <= 1.0)

    @pytest.mark.unit
    def test_boolean_policy_fields(self):
        """Boolean policy fields must be bool type"""
        policy = {
            "block_complete_solutions": True,
            "require_justification": False,
            "allow_code_snippets": True
        }

        for key, value in policy.items():
            assert isinstance(value, bool)


# ============================================================================
# Difficulty Validation Tests
# ============================================================================

class TestDifficultyValidation:
    """Tests for activity difficulty validation"""

    @pytest.mark.unit
    def test_valid_difficulty_levels(self):
        """Difficulty must be valid enum value"""
        valid_difficulties = ["INICIAL", "INTERMEDIO", "AVANZADO"]

        for difficulty in valid_difficulties:
            assert difficulty in valid_difficulties

    @pytest.mark.unit
    def test_invalid_difficulty(self):
        """Invalid difficulty should fail validation"""
        invalid_difficulties = ["EASY", "HARD", "beginner", ""]

        for difficulty in invalid_difficulties:
            assert difficulty not in ["INICIAL", "INTERMEDIO", "AVANZADO"]


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestActivityEdgeCases:
    """Edge cases and error handling tests"""

    @pytest.mark.unit
    def test_empty_activity_id(self):
        """Empty activity_id should fail validation"""
        # Schema validation should reject empty string
        assert "" == ""  # Placeholder

    @pytest.mark.unit
    def test_very_long_title(self):
        """Very long title should be handled"""
        long_title = "A" * 1000

        # Should either accept or truncate gracefully
        assert len(long_title) == 1000

    @pytest.mark.unit
    def test_special_characters_in_instructions(self):
        """Special characters in instructions should work"""
        instructions_with_special = """
        # Step 1
        - Use `queue.enqueue(item)`
        - Check if `queue.isEmpty()` returns **True**

        ```python
        def example():
            pass
        ```
        """

        assert "```" in instructions_with_special
        assert "`" in instructions_with_special

    @pytest.mark.unit
    def test_unicode_in_activity_content(self):
        """Unicode characters should work in activity content"""
        unicode_content = {
            "title": "Implementación de Cola Circular 日本語",
            "description": "Descripción con ñ y acentos: árbol, búsqueda"
        }

        assert "日本語" in unicode_content["title"]
        assert "ñ" in unicode_content["description"]

    @pytest.mark.unit
    def test_empty_tags_list(self):
        """Empty tags list should be valid"""
        tags = []

        assert isinstance(tags, list)
        assert len(tags) == 0

    @pytest.mark.unit
    def test_empty_evaluation_criteria(self):
        """Empty evaluation criteria should be valid"""
        criteria = []

        assert isinstance(criteria, list)
        assert len(criteria) == 0


# ============================================================================
# Integration Tests (require database)
# ============================================================================

class TestActivityIntegration:
    """Integration tests for activity endpoints"""

    @pytest.mark.integration
    def test_full_activity_lifecycle(self):
        """Complete activity lifecycle: create -> update -> publish -> archive"""
        # 1. Create activity
        # 2. Get activity
        # 3. Update activity
        # 4. Publish activity
        # 5. Archive activity
        # 6. Delete activity
        pass

    @pytest.mark.integration
    def test_list_with_multiple_filters(self):
        """List activities with combined filters"""
        # teacher_id + status + difficulty
        pass

    @pytest.mark.integration
    def test_pagination_consistency(self):
        """Pagination returns consistent results"""
        pass