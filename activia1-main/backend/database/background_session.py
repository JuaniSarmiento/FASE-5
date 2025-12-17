"""
Background Task Database Session Management - Production Pattern

PROBLEMA RESUELTO: ResourceClosedError en BackgroundTasks de FastAPI

Este módulo implementa el patrón Factory para crear sesiones de base de datos
independientes y thread-safe para tareas en segundo plano.

CAUSAS DEL PROBLEMA:
1. FastAPI cierra la sesión del request cuando el response se envía al cliente
2. BackgroundTasks se ejecutan DESPUÉS del response (sesión ya cerrada)
3. Intentar usar la misión sesión causa ResourceClosedError

SOLUCIÓN IMPLEMENTADA:
- Factory Pattern: Crea sesiones frescas e independientes
- Context Manager: Gestión automática de lifecycle (commit/rollback/close)
- Thread-Safe: Cada tarea obtiene su propia sesión aislada
- Type-Safe: Protocols para type checking sin imports circulares

USAGE:

    # En endpoint FastAPI
    @app.post("/process")
    async def process_data(
        background_tasks: BackgroundTasks,
        data: DataModel
    ):
        # NO pasar db session del request a background task
        background_tasks.add_task(
            process_in_background,
            data_id=data.id,
            # NO pasar 'db' aquí
        )
        return {"status": "processing"}
    
    # En función de background task
    def process_in_background(data_id: str):
        # Crear sesión NUEVA y FRESCA
        with get_background_db_session() as db:
            data = db.query(DataModel).get(data_id)
            # ... procesamiento ...
            db.commit()  # Commit automático al salir del context manager

ARQUITECTURA:
- Usa el mismo engine/pool de conexiones que las requests normales
- No crea overhead adicional (reutiliza conexiones del pool)
- Compatible con PostgreSQL y SQLite
- Integración transparente con repositorios existentes
"""
from contextlib import contextmanager
from typing import Generator, Optional, Callable, Any
from functools import wraps
import logging

from sqlalchemy.orm import Session

from .config import get_db_config

logger = logging.getLogger(__name__)


@contextmanager
def get_background_db_session() -> Generator[Session, None, None]:
    """
    Context manager para sesiones de base de datos en BackgroundTasks.
    
    Crea una sesión NUEVA e INDEPENDIENTE que:
    - Es thread-safe (no comparte estado con otras sesiones)
    - Se auto-gestiona (commit/rollback/close automáticos)
    - Reutiliza el pool de conexiones existente (no overhead)
    
    Usage en BackgroundTask:
        with get_background_db_session() as db:
            trace = db.query(CognitiveTraceDB).filter_by(id=trace_id).first()
            trace.processed = True
            db.commit()  # Opcional: commit automático al salir
    
    Yields:
        Session: Nueva sesión SQLAlchemy lista para usar
        
    Raises:
        Exception: Cualquier error de BD (con rollback automático)
    
    Note:
        - El commit se hace automáticamente al salir del bloque 'with'
        - Si hay excepción, se hace rollback automático
        - La sesión se cierra siempre (finally block)
    """
    db_config = get_db_config()
    session_factory = db_config.get_session_factory()
    session = session_factory()
    
    logger.debug("Created new background DB session", extra={
        "session_id": id(session),
        "engine": str(db_config.get_engine().url)
    })
    
    try:
        yield session
        session.commit()
        logger.debug("Background DB session committed successfully", extra={
            "session_id": id(session)
        })
    except Exception as e:
        session.rollback()
        logger.error(
            "Background DB session rolled back due to error",
            extra={
                "session_id": id(session),
                "error": str(e),
                "error_type": type(e).__name__
            },
            exc_info=True
        )
        raise
    finally:
        session.close()
        logger.debug("Background DB session closed", extra={
            "session_id": id(session)
        })


def create_background_db_session() -> Session:
    """
    Factory function para crear sesiones de BD en background tasks.
    
    IMPORTANTE: El caller es responsable de cerrar la sesión manualmente.
    Preferir usar get_background_db_session() context manager cuando sea posible.
    
    Returns:
        Session: Nueva sesión SQLAlchemy
        
    Usage (NO recomendado - preferir context manager):
        db = create_background_db_session()
        try:
            # ... operaciones ...
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    """
    db_config = get_db_config()
    session_factory = db_config.get_session_factory()
    session = session_factory()
    
    logger.debug("Created background DB session (manual management)", extra={
        "session_id": id(session)
    })
    
    return session


def with_background_db_session(func: Callable) -> Callable:
    """
    Decorador para inyectar automáticamente una sesión DB en background tasks.
    
    El decorador:
    1. Crea una sesión NUEVA antes de ejecutar la función
    2. La inyecta como parámetro 'db'
    3. Hace commit automático si no hay errores
    4. Hace rollback automático si hay excepción
    5. Cierra la sesión siempre
    
    Usage:
        @with_background_db_session
        def process_trace(trace_id: str, db: Session):
            trace = db.query(CognitiveTraceDB).get(trace_id)
            trace.processed = True
            # Commit automático al terminar
        
        # Llamar sin pasar 'db' (se inyecta automáticamente)
        background_tasks.add_task(process_trace, trace_id="123")
    
    Args:
        func: Función que recibe un parámetro 'db: Session'
        
    Returns:
        Función decorada con gestión automática de sesión
        
    Note:
        - La función DEBE tener un parámetro 'db' en su firma
        - El decorador funciona con funciones síncronas y asíncronas
        - No usar si la función ya recibe una sesión de otra fuente
    """
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        with get_background_db_session() as db:
            # Inyectar sesión como kwarg 'db'
            return func(*args, db=db, **kwargs)
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        with get_background_db_session() as db:
            # Inyectar sesión como kwarg 'db'
            return await func(*args, db=db, **kwargs)
    
    # Retornar wrapper apropiado según si la función es async o no
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


# ============================================================================
# Unit of Work Pattern (Optional - Advanced)
# ============================================================================

class BackgroundUnitOfWork:
    """
    Unit of Work pattern para background tasks con múltiples repositorios.
    
    Útil cuando una background task necesita acceder a múltiples repositorios
    y se requiere transaccionalidad atómica.
    
    Usage:
        def process_complex_task(session_id: str):
            uow = BackgroundUnitOfWork()
            with uow:
                # Todos los repositorios comparten la misma sesión
                session = uow.sessions.get(session_id)
                traces = uow.traces.get_by_session(session_id)
                risks = uow.risks.get_by_session(session_id)
                
                # ... procesamiento ...
                
                # Commit atómico de todos los cambios
                uow.commit()
    """
    
    def __init__(self):
        self._session: Optional[Session] = None
        
    def __enter__(self):
        """Crear sesión al entrar al context manager"""
        db_config = get_db_config()
        session_factory = db_config.get_session_factory()
        self._session = session_factory()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit/rollback/close al salir"""
        if exc_type is not None:
            self._session.rollback()
        else:
            self._session.commit()
        
        self._session.close()
        self._session = None
    
    @property
    def session(self) -> Session:
        """Obtener la sesión activa"""
        if self._session is None:
            raise RuntimeError("UnitOfWork no inicializado - usar context manager")
        return self._session
    
    def commit(self):
        """Commit manual de cambios"""
        if self._session:
            self._session.commit()
    
    def rollback(self):
        """Rollback manual de cambios"""
        if self._session:
            self._session.rollback()
    
    # Lazy loading de repositorios (se crean solo si se usan)
    @property
    def sessions(self):
        """Repository de sesiones"""
        from .repositories import SessionRepository
        return SessionRepository(self.session)
    
    @property
    def traces(self):
        """Repository de trazas"""
        from .repositories import TraceRepository
        return TraceRepository(self.session)
    
    @property
    def risks(self):
        """Repository de riesgos"""
        from .repositories import RiskRepository
        return RiskRepository(self.session)
    
    @property
    def evaluations(self):
        """Repository de evaluaciones"""
        from .repositories import EvaluationRepository
        return EvaluationRepository(self.session)
    
    @property
    def sequences(self):
        """Repository de secuencias"""
        from .repositories import TraceSequenceRepository
        return TraceSequenceRepository(self.session)


# ============================================================================
# Ejemplo de uso completo
# ============================================================================

if __name__ == "__main__":
    """
    Ejemplos de uso de los diferentes patrones
    """
    
    # Ejemplo 1: Context Manager (RECOMENDADO)
    def example_background_task_context_manager(trace_id: str):
        with get_background_db_session() as db:
            from .models import CognitiveTraceDB
            trace = db.query(CognitiveTraceDB).filter_by(id=trace_id).first()
            if trace:
                trace.processed = True
                # Commit automático al salir del 'with'
    
    # Ejemplo 2: Decorador (MÁS LIMPIO)
    @with_background_db_session
    def example_background_task_decorator(trace_id: str, db: Session):
        from .models import CognitiveTraceDB
        trace = db.query(CognitiveTraceDB).filter_by(id=trace_id).first()
        if trace:
            trace.processed = True
            # Commit automático al terminar la función
    
    # Ejemplo 3: Unit of Work (COMPLEJO - múltiples repos)
    def example_background_task_uow(session_id: str):
        uow = BackgroundUnitOfWork()
        with uow:
            session = uow.sessions.get(session_id)
            traces = uow.traces.get_by_session(session_id)
            risks = uow.risks.get_by_session(session_id)
            
            # ... procesamiento complejo ...
            
            # Commit atómico de todos los cambios
            uow.commit()
    
    # Ejemplo 4: En FastAPI endpoint
    """
    from fastapi import BackgroundTasks
    
    @app.post("/analyze")
    async def analyze_session(
        session_id: str,
        background_tasks: BackgroundTasks
    ):
        # NO pasar la sesión DB del request
        background_tasks.add_task(
            analyze_session_background,
            session_id=session_id
        )
        return {"status": "processing"}
    
    @with_background_db_session
    def analyze_session_background(session_id: str, db: Session):
        # db se inyecta automáticamente
        traces = db.query(CognitiveTraceDB).filter_by(session_id=session_id).all()
        # ... análisis ...
    """
