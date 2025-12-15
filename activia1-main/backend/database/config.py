"""
Database configuration and session management

Supports:
- SQLite (development/testing)
- PostgreSQL (production)
- Session management with context managers
- Connection pooling
"""
import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine, event, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from .base import Base

# IMPORTANT: Import all models before calling create_all_tables()
# This ensures SQLAlchemy's metadata is aware of all table definitions
def _import_all_models():
    """Import all ORM models to register them with SQLAlchemy metadata"""
    from . import models  # noqa: F401
    # This import registers all model classes with Base.metadata

_import_all_models()


class DatabaseConfig:
    """
    Database configuration manager with production-ready connection pooling.

    Features:
    - Configurable pool size and overflow from environment variables
    - Pool timeout and connection recycling
    - Health checks (pre-ping)
    - Automatic connection retry
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
        echo: bool = False,
        pool_size: Optional[int] = None,
        max_overflow: Optional[int] = None,
        pool_timeout: Optional[int] = None,
        pool_recycle: Optional[int] = None,
        pool_pre_ping: bool = True,
    ):
        """
        Initialize database configuration

        Args:
            database_url: SQLAlchemy database URL. If None, uses from env or SQLite default
            echo: Whether to log SQL statements (default: False)
            pool_size: Connection pool size (default: from env or 20)
            max_overflow: Maximum overflow connections (default: from env or 40)
            pool_timeout: Seconds to wait before giving up on getting a connection (default: 30)
            pool_recycle: Seconds before recycling connections (default: 3600)
            pool_pre_ping: Test connections before using them (default: True)
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", "sqlite:///ai_native_mvp.db"
        )
        self.echo = echo

        # Read pool configuration from environment variables (P1.3 - Production Readiness)
        self.pool_size = pool_size or int(os.getenv("DB_POOL_SIZE", "20"))
        self.max_overflow = max_overflow or int(os.getenv("DB_MAX_OVERFLOW", "40"))
        self.pool_timeout = pool_timeout or int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = pool_recycle or int(os.getenv("DB_POOL_RECYCLE", "3600"))
        self.pool_pre_ping = pool_pre_ping

        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None

    def get_engine(self) -> Engine:
        """Get or create SQLAlchemy engine"""
        if self._engine is None:
            # SQLite specific configuration
            if self.database_url.startswith("sqlite"):
                self._engine = create_engine(
                    self.database_url,
                    echo=self.echo,
                    connect_args={"check_same_thread": False},
                    poolclass=StaticPool if ":memory:" in self.database_url else None,
                )

                # Enable foreign keys for SQLite
                @event.listens_for(self._engine, "connect")
                def set_sqlite_pragma(dbapi_conn, connection_record):
                    cursor = dbapi_conn.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()

            # PostgreSQL configuration (P1.3 - Production-ready pooling)
            else:
                self._engine = create_engine(
                    self.database_url,
                    echo=self.echo,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    pool_timeout=self.pool_timeout,
                    pool_recycle=self.pool_recycle,
                    pool_pre_ping=self.pool_pre_ping,  # Verify connections before using
                    # Additional production settings
                    pool_use_lifo=True,  # Last In First Out for better cache locality
                    connect_args={
                        "connect_timeout": 10,  # Connection timeout in seconds
                        "options": "-c statement_timeout=30000"  # Query timeout: 30s
                    }
                )

        return self._engine

    def get_session_factory(self) -> sessionmaker:
        """Get or create session factory"""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                bind=self.get_engine(),
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
        return self._session_factory

    def create_all_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.get_engine())

    def drop_all_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.get_engine())

    def close(self):
        """Close database connections"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


# Global database configuration instance
_db_config: Optional[DatabaseConfig] = None


def init_database(
    database_url: Optional[str] = None,
    echo: bool = False,
    create_tables: bool = True,
) -> DatabaseConfig:
    """
    Initialize the database

    Args:
        database_url: Database URL (default: SQLite)
        echo: Whether to echo SQL
        create_tables: Whether to create tables on init

    Returns:
        DatabaseConfig instance
    """
    global _db_config
    _db_config = DatabaseConfig(database_url=database_url, echo=echo)

    if create_tables:
        _db_config.create_all_tables()

    return _db_config


def get_db_config() -> DatabaseConfig:
    """Get the global database configuration"""
    global _db_config
    if _db_config is None:
        _db_config = init_database()
    return _db_config


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions

    Usage:
        with get_db_session() as session:
            session.add(obj)
            session.commit()
    """
    db_config = get_db_config()
    session_factory = db_config.get_session_factory()
    session = session_factory()

    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Session:
    """
    Get a new database session (manual management)

    Note: Caller is responsible for closing the session

    Returns:
        SQLAlchemy Session
    """
    db_config = get_db_config()
    session_factory = db_config.get_session_factory()
    return session_factory()


def get_db():
    """
    Dependency for FastAPI to get database session
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = get_session()
    try:
        yield db
    finally:
        db.close()


# Aliases for compatibility
SessionLocal = get_db_config().get_session_factory()
engine = get_db_config().get_engine()