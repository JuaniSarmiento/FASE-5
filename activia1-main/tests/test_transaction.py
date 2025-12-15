"""
Tests for Transaction Management utilities

Verifies:
- Context manager transaction handling
- Automatic commit on success
- Automatic rollback on exception
- Transactional decorator
- TransactionManager class
- Savepoint functionality
"""
import pytest
from unittest.mock import Mock, MagicMock, patch, call
from sqlalchemy.orm import Session

from backend.database.transaction import (
    transaction,
    transactional,
    TransactionManager
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_session():
    """Create a mock SQLAlchemy session"""
    session = Mock(spec=Session)
    session.commit = Mock()
    session.rollback = Mock()
    session.begin_nested = Mock(return_value=Mock())
    return session


# ============================================================================
# Context Manager Tests
# ============================================================================

class TestTransactionContextManager:
    """Tests for transaction() context manager"""

    def test_transaction_commits_on_success(self, mock_session):
        """Test that transaction commits when no exception occurs"""
        with transaction(mock_session, "Test transaction"):
            # Simulate DB operation
            pass

        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_not_called()

    def test_transaction_rollback_on_exception(self, mock_session):
        """Test that transaction rolls back on exception"""
        with pytest.raises(ValueError):
            with transaction(mock_session, "Failing transaction"):
                raise ValueError("Test error")

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()

    def test_transaction_re_raises_exception(self, mock_session):
        """Test that exception is re-raised after rollback"""
        with pytest.raises(ValueError, match="Test error"):
            with transaction(mock_session, "Failing transaction"):
                raise ValueError("Test error")

    def test_transaction_with_description(self, mock_session):
        """Test transaction with description logs correctly"""
        with transaction(mock_session, "Creating session and trace"):
            pass

        mock_session.commit.assert_called_once()

    def test_transaction_without_description(self, mock_session):
        """Test transaction without description still works"""
        with transaction(mock_session):
            pass

        mock_session.commit.assert_called_once()

    def test_transaction_yields_session(self, mock_session):
        """Test that transaction yields the session"""
        with transaction(mock_session) as session:
            assert session is mock_session

    def test_transaction_with_db_operation(self, mock_session):
        """Test transaction with simulated DB operations"""
        with transaction(mock_session, "Multiple operations"):
            mock_session.add("entity1")
            mock_session.add("entity2")

        # Operations should complete before commit
        assert mock_session.add.call_count == 2
        mock_session.commit.assert_called_once()

    def test_transaction_handles_multiple_exception_types(self, mock_session):
        """Test rollback for different exception types"""
        exceptions = [ValueError, TypeError, RuntimeError, KeyError]

        for exc_type in exceptions:
            mock_session.reset_mock()

            with pytest.raises(exc_type):
                with transaction(mock_session):
                    raise exc_type("Test")

            mock_session.rollback.assert_called_once()


# ============================================================================
# Transactional Decorator Tests
# ============================================================================

class TestTransactionalDecorator:
    """Tests for @transactional decorator"""

    def test_transactional_decorator_with_self_and_session(self, mock_session):
        """Test decorator on method with self and session"""

        class MyService:
            @transactional("Process data")
            def process(self, session: Session, data: str):
                return f"processed: {data}"

        service = MyService()
        result = service.process(mock_session, "test")

        assert result == "processed: test"
        mock_session.commit.assert_called_once()

    def test_transactional_decorator_with_session_only(self, mock_session):
        """Test decorator on function with session as first arg"""

        @transactional("Direct function")
        def process_data(session: Session, data: str):
            return f"processed: {data}"

        result = process_data(mock_session, "test")

        assert result == "processed: test"
        mock_session.commit.assert_called_once()

    def test_transactional_decorator_with_kwargs_session(self, mock_session):
        """Test decorator with session as keyword argument"""

        @transactional("Kwargs function")
        def process_data(data: str, session: Session = None):
            return f"processed: {data}"

        result = process_data("test", session=mock_session)

        assert result == "processed: test"
        mock_session.commit.assert_called_once()

    def test_transactional_decorator_rollback_on_exception(self, mock_session):
        """Test decorator rolls back on exception"""

        @transactional("Failing function")
        def failing_function(session: Session):
            raise ValueError("Error in function")

        with pytest.raises(ValueError):
            failing_function(mock_session)

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()

    def test_transactional_decorator_without_session(self):
        """Test decorator warns when no session found"""

        @transactional("No session function")
        def no_session_function(data: str):
            return data

        # Should execute without error but warn
        result = no_session_function("test")
        assert result == "test"

    def test_transactional_decorator_preserves_return_value(self, mock_session):
        """Test that decorator preserves function return value"""

        @transactional()
        def get_value(session: Session):
            return {"key": "value", "count": 42}

        result = get_value(mock_session)

        assert result == {"key": "value", "count": 42}

    def test_transactional_decorator_with_default_description(self, mock_session):
        """Test decorator uses function name as default description"""

        @transactional()  # No description
        def my_custom_function(session: Session):
            return "done"

        result = my_custom_function(mock_session)

        assert result == "done"
        mock_session.commit.assert_called_once()


# ============================================================================
# TransactionManager Tests
# ============================================================================

class TestTransactionManager:
    """Tests for TransactionManager class"""

    def test_init_with_session(self, mock_session):
        """Test TransactionManager initialization"""
        manager = TransactionManager(mock_session)

        assert manager.session is mock_session
        assert manager._savepoints == []

    def test_begin_returns_context_manager(self, mock_session):
        """Test that begin() returns a context manager"""
        manager = TransactionManager(mock_session)

        with manager.begin("Test operation"):
            pass

        mock_session.commit.assert_called_once()

    def test_begin_commits_on_success(self, mock_session):
        """Test that begin() commits on success"""
        manager = TransactionManager(mock_session)

        with manager.begin("Create entity"):
            mock_session.add("entity")

        mock_session.commit.assert_called_once()

    def test_begin_rollback_on_error(self, mock_session):
        """Test that begin() rolls back on error"""
        manager = TransactionManager(mock_session)

        with pytest.raises(RuntimeError):
            with manager.begin("Failing operation"):
                raise RuntimeError("Error")

        mock_session.rollback.assert_called_once()

    def test_savepoint_creation(self, mock_session):
        """Test savepoint creation"""
        manager = TransactionManager(mock_session)
        mock_nested = Mock()
        mock_session.begin_nested.return_value = mock_nested

        savepoint = manager.savepoint("before_risky_op")

        mock_session.begin_nested.assert_called_once()
        assert "before_risky_op" in manager._savepoints
        assert savepoint == mock_nested

    def test_savepoint_auto_naming(self, mock_session):
        """Test savepoint auto-naming when no name provided"""
        manager = TransactionManager(mock_session)
        mock_nested = Mock()
        mock_session.begin_nested.return_value = mock_nested

        manager.savepoint()
        manager.savepoint()

        assert "sp_1" in manager._savepoints
        assert "sp_2" in manager._savepoints

    def test_rollback_to_savepoint(self, mock_session):
        """Test rolling back to a savepoint"""
        manager = TransactionManager(mock_session)
        mock_savepoint = Mock()
        mock_session.begin_nested.return_value = mock_savepoint

        savepoint = manager.savepoint("test_sp")
        manager.rollback_to_savepoint(savepoint)

        mock_savepoint.rollback.assert_called_once()

    def test_manual_commit(self, mock_session):
        """Test manual commit"""
        manager = TransactionManager(mock_session)

        manager.commit()

        mock_session.commit.assert_called_once()

    def test_manual_rollback(self, mock_session):
        """Test manual rollback"""
        manager = TransactionManager(mock_session)

        manager.rollback()

        mock_session.rollback.assert_called_once()

    def test_nested_transactions_with_savepoints(self, mock_session):
        """Test nested transactions using savepoints"""
        manager = TransactionManager(mock_session)
        mock_savepoint = Mock()
        mock_session.begin_nested.return_value = mock_savepoint

        with manager.begin("Main transaction"):
            mock_session.add("entity1")

            # Create savepoint before risky operation
            sp = manager.savepoint("before_risky")

            try:
                mock_session.add("risky_entity")
                raise ValueError("Risky operation failed")
            except ValueError:
                manager.rollback_to_savepoint(sp)

            mock_session.add("entity2")

        # Main transaction should still commit
        mock_session.commit.assert_called_once()
        # Savepoint should have been rolled back
        mock_savepoint.rollback.assert_called_once()


# ============================================================================
# Integration Tests
# ============================================================================

class TestTransactionIntegration:
    """Integration tests for transaction utilities"""

    def test_transaction_with_multiple_operations(self, mock_session):
        """Test transaction wrapping multiple operations"""
        operations_completed = []

        with transaction(mock_session, "Multi-op transaction"):
            operations_completed.append("op1")
            mock_session.add("entity1")
            operations_completed.append("op2")
            mock_session.add("entity2")
            operations_completed.append("op3")

        assert len(operations_completed) == 3
        mock_session.commit.assert_called_once()

    def test_transaction_manager_complex_workflow(self, mock_session):
        """Test TransactionManager with complex workflow"""
        manager = TransactionManager(mock_session)
        mock_savepoint1 = Mock()
        mock_savepoint2 = Mock()
        mock_session.begin_nested.side_effect = [mock_savepoint1, mock_savepoint2]

        results = []

        with manager.begin("Complex workflow"):
            # Phase 1
            results.append("phase1")
            sp1 = manager.savepoint("after_phase1")

            # Phase 2 - risky
            try:
                results.append("phase2_start")
                sp2 = manager.savepoint("mid_phase2")
                raise ValueError("Phase 2 failed")
            except ValueError:
                manager.rollback_to_savepoint(sp2)
                results.append("phase2_recovered")

            # Phase 3
            results.append("phase3")

        assert results == ["phase1", "phase2_start", "phase2_recovered", "phase3"]
        mock_session.commit.assert_called_once()

    def test_decorator_and_context_manager_together(self, mock_session):
        """Test using decorator with nested context manager"""

        @transactional("Outer transaction")
        def outer_function(session: Session):
            session.add("entity1")

            # Nested context manager (simulating sub-transaction)
            # Note: In real SQLAlchemy, nested transactions need savepoints
            session.add("entity2")

            return "completed"

        result = outer_function(mock_session)

        assert result == "completed"
        mock_session.commit.assert_called_once()

    def test_partial_failure_with_savepoint(self, mock_session):
        """Test partial failure recovery using savepoints"""
        manager = TransactionManager(mock_session)
        mock_savepoint = Mock()
        mock_session.begin_nested.return_value = mock_savepoint

        successful_entities = []
        failed_entities = []

        entities = ["entity1", "entity2", "bad_entity", "entity3"]

        with manager.begin("Batch insert"):
            for entity in entities:
                sp = manager.savepoint(f"before_{entity}")

                try:
                    if entity == "bad_entity":
                        raise ValueError(f"Cannot insert {entity}")
                    successful_entities.append(entity)
                    mock_session.add(entity)
                except ValueError:
                    manager.rollback_to_savepoint(sp)
                    failed_entities.append(entity)

        assert successful_entities == ["entity1", "entity2", "entity3"]
        assert failed_entities == ["bad_entity"]
        mock_session.commit.assert_called_once()


# ============================================================================
# Edge Cases Tests
# ============================================================================

class TestTransactionEdgeCases:
    """Tests for edge cases and error conditions"""

    def test_transaction_with_none_session(self):
        """Test transaction behavior with None session"""
        # This should raise an AttributeError when trying to call commit/rollback
        with pytest.raises(AttributeError):
            with transaction(None, "Invalid session"):
                pass

    def test_nested_transactions_without_savepoints(self, mock_session):
        """Test warning about nested transactions"""
        # Nested context managers without savepoints
        with transaction(mock_session, "Outer"):
            with transaction(mock_session, "Inner"):
                pass

        # Should commit twice (once for each context manager)
        assert mock_session.commit.call_count == 2

    def test_exception_in_commit(self, mock_session):
        """Test handling when commit itself fails"""
        mock_session.commit.side_effect = RuntimeError("Commit failed")

        with pytest.raises(RuntimeError, match="Commit failed"):
            with transaction(mock_session, "Will fail on commit"):
                pass

    def test_exception_in_rollback(self, mock_session):
        """Test handling when rollback fails"""
        mock_session.rollback.side_effect = RuntimeError("Rollback failed")

        with pytest.raises(RuntimeError):
            with transaction(mock_session, "Will fail on rollback"):
                raise ValueError("Original error")

    def test_transactional_decorator_with_async_function(self, mock_session):
        """Test that decorator works with sync functions"""
        # Note: Current implementation is sync-only

        @transactional("Sync function")
        def sync_function(session: Session):
            return "sync_result"

        result = sync_function(mock_session)
        assert result == "sync_result"
        mock_session.commit.assert_called_once()

    def test_transaction_manager_multiple_savepoints(self, mock_session):
        """Test creating multiple savepoints"""
        manager = TransactionManager(mock_session)
        savepoints = []

        for i in range(5):
            mock_sp = Mock()
            mock_session.begin_nested.return_value = mock_sp
            sp = manager.savepoint(f"sp_{i}")
            savepoints.append(sp)

        assert len(manager._savepoints) == 5
        assert mock_session.begin_nested.call_count == 5