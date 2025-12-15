"""
Transaction management utilities

Provides decorators and context managers for explicit transaction control,
ensuring atomicity and consistency across multiple repository operations.
"""
from functools import wraps
from typing import Callable, TypeVar, Any
from contextlib import contextmanager
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


@contextmanager
def transaction(session: Session, description: str = ""):
    """
    Context manager for explicit transaction control.

    Automatically handles commit on success, rollback on exception.
    Provides clear logging of transaction boundaries.

    Args:
        session: SQLAlchemy session
        description: Description of the transaction for logging

    Yields:
        Session: The same session, within a transaction

    Example:
        with transaction(session, "Create session and initial trace"):
            session_repo.create(...)
            trace_repo.create(...)
            # Auto-commit if no exception, rollback otherwise
    """
    tx_id = id(session)  # Unique identifier for logging

    try:
        if description:
            logger.debug(f"Transaction {tx_id} started: {description}")
        else:
            logger.debug(f"Transaction {tx_id} started")

        yield session

        session.commit()
        logger.debug(f"Transaction {tx_id} committed successfully")

    except Exception as e:
        session.rollback()
        logger.error(
            f"Transaction {tx_id} rolled back due to error",
            extra={
                "description": description,
                "error": str(e),
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        raise

    finally:
        logger.debug(f"Transaction {tx_id} completed")


def transactional(description: str = ""):
    """
    Decorator for methods that should run within a single transaction.

    Assumes the method's first argument after self is a SQLAlchemy session.
    Wraps the entire method execution in a transaction context.

    Args:
        description: Description of the transaction for logging

    Example:
        @transactional("Process student interaction")
        def process_interaction(self, session: Session, ...):
            # All DB operations here are atomic
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Extract session from arguments
            # Assumes: func(self, session, ...) or func(session, ...)
            session = None

            if len(args) >= 2 and isinstance(args[1], Session):
                session = args[1]
            elif len(args) >= 1 and isinstance(args[0], Session):
                session = args[0]
            elif 'session' in kwargs and isinstance(kwargs['session'], Session):
                session = kwargs['session']

            if session is None:
                # No session found, execute without transaction wrapper
                logger.warning(
                    f"@transactional decorator on {func.__name__} but no Session found in args"
                )
                return func(*args, **kwargs)

            # Execute within transaction
            with transaction(session, description or func.__name__):
                return func(*args, **kwargs)

        return wrapper
    return decorator


class TransactionManager:
    """
    Transaction manager for coordinating multiple repository operations.

    Provides a higher-level interface for complex transactions that
    involve multiple repositories.

    Example:
        tx_manager = TransactionManager(session)
        with tx_manager.begin("Create session with traces"):
            session_repo = SessionRepository(tx_manager.session)
            trace_repo = TraceRepository(tx_manager.session)

            session = session_repo.create(...)
            trace = trace_repo.create(...)

            # Auto-commit on success
    """

    def __init__(self, session: Session):
        """
        Initialize transaction manager.

        Args:
            session: SQLAlchemy session to manage
        """
        self.session = session
        self._savepoints: list[str] = []

    def begin(self, description: str = ""):
        """
        Begin a new transaction context.

        Args:
            description: Description for logging

        Returns:
            Context manager for the transaction
        """
        return transaction(self.session, description)

    def savepoint(self, name: str = ""):
        """
        Create a savepoint within the current transaction.

        Savepoints allow partial rollback to a specific point
        without rolling back the entire transaction.

        Args:
            name: Optional name for the savepoint

        Returns:
            Savepoint identifier

        Example:
            tx_manager = TransactionManager(session)
            with tx_manager.begin("Main transaction"):
                session_repo.create(...)

                sp = tx_manager.savepoint("before_risky_operation")
                try:
                    risky_operation()
                except Exception:
                    tx_manager.rollback_to_savepoint(sp)

                trace_repo.create(...)
        """
        if not name:
            name = f"sp_{len(self._savepoints) + 1}"

        savepoint = self.session.begin_nested()
        self._savepoints.append(name)

        logger.debug(f"Savepoint created: {name}")
        return savepoint

    def rollback_to_savepoint(self, savepoint):
        """
        Rollback to a specific savepoint.

        Args:
            savepoint: Savepoint identifier returned by savepoint()
        """
        savepoint.rollback()
        logger.debug(f"Rolled back to savepoint")

    def commit(self):
        """Commit the current transaction"""
        self.session.commit()
        logger.debug("Transaction committed manually")

    def rollback(self):
        """Rollback the current transaction"""
        self.session.rollback()
        logger.warning("Transaction rolled back manually")