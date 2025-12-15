"""
Logging estructurado con formato JSON y contexto
"""
import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
import traceback
from contextvars import ContextVar

from backend.core.constants import utc_now

# Context variables para request tracing
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')

class StructuredLogger(logging.Logger):
    """Logger personalizado con soporte para logs estructurados"""
    
    def _log_structured(
        self,
        level: int,
        msg: str,
        extra: Dict[str, Any] = None,
        exc_info=None
    ):
        """Log con formato estructurado JSON"""
        record = {
            "timestamp": utc_now().isoformat(),
            "level": logging.getLevelName(level),
            "message": msg,
            "logger": self.name,
        }
        
        # Agregar contexto de request
        request_id = request_id_var.get()
        if request_id:
            record["request_id"] = request_id
        
        correlation_id = correlation_id_var.get()
        if correlation_id:
            record["correlation_id"] = correlation_id
        
        user_id = user_id_var.get()
        if user_id:
            record["user_id"] = user_id
        
        # Agregar extra fields
        if extra:
            record.update(extra)
        
        # Agregar exception info si existe
        if exc_info:
            if isinstance(exc_info, Exception):
                record["exception"] = {
                    "type": type(exc_info).__name__,
                    "message": str(exc_info),
                    "traceback": traceback.format_exc()
                }
            elif exc_info is True:
                record["exception"] = {
                    "traceback": traceback.format_exc()
                }
        
        super()._log(level, json.dumps(record), ())
    
    def info_structured(self, msg: str, **kwargs):
        """Log INFO estructurado"""
        self._log_structured(logging.INFO, msg, kwargs)
    
    def error_structured(self, msg: str, exc_info=None, **kwargs):
        """Log ERROR estructurado"""
        self._log_structured(logging.ERROR, msg, kwargs, exc_info)
    
    def warning_structured(self, msg: str, **kwargs):
        """Log WARNING estructurado"""
        self._log_structured(logging.WARNING, msg, kwargs)
    
    def debug_structured(self, msg: str, **kwargs):
        """Log DEBUG estructurado"""
        self._log_structured(logging.DEBUG, msg, kwargs)

class JSONFormatter(logging.Formatter):
    """Formateador JSON para logs"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Agregar contexto si existe
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
        
        correlation_id = correlation_id_var.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id
        
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id
        
        # Agregar extra fields
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        # Agregar exception info
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None
            }
        
        return json.dumps(log_data, default=str)

def setup_logging(level: str = "INFO", json_format: bool = True):
    """
    Configura logging para toda la aplicación.
    
    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        json_format: Si True, usa formato JSON; si False, formato legible
    """
    logging.setLoggerClass(StructuredLogger)
    
    handler = logging.StreamHandler(sys.stdout)
    
    if json_format:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(handler)
    
    # Reducir verbosidad de librerías externas
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    return root_logger

def get_logger(name: str) -> StructuredLogger:
    """Obtiene logger estructurado"""
    return logging.getLogger(name)

# Context managers para request tracing
def set_request_context(request_id: str, correlation_id: str = None, user_id: str = None):
    """Establece contexto de request para logging"""
    request_id_var.set(request_id)
    if correlation_id:
        correlation_id_var.set(correlation_id)
    if user_id:
        user_id_var.set(user_id)

def clear_request_context():
    """Limpia contexto de request"""
    request_id_var.set('')
    correlation_id_var.set('')
    user_id_var.set('')
