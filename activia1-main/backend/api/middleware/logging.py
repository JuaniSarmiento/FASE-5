"""
Middleware para logging de requests y responses
"""
import time
import logging
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

# Prometheus metrics instrumentation (HIGH-01)
try:
    from ..monitoring.metrics import (
        record_http_request,
        record_http_request_start,
        record_http_request_end,
    )
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra información de cada request/response.

    Captura:
    - Método HTTP
    - Path
    - Query parameters
    - Status code de respuesta
    - Tiempo de procesamiento
    - IP del cliente
    """

    async def dispatch(self, request: Request, call_next):
        """
        Procesa el request y captura métricas.

        Args:
            request: Request de FastAPI
            call_next: Siguiente middleware en la cadena

        Returns:
            Response del siguiente middleware
        """
        # Timestamp de inicio
        start_time = time.time()

        # Capturar información del request
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path
        query = str(request.url.query) if request.url.query else None

        # ✅ HIGH-01: Record request start for in_progress metric
        if METRICS_AVAILABLE:
            record_http_request_start(method, path)

        try:
            # Procesar request
            response = await call_next(request)

            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time

            # Log de la request
            log_message = (
                f"{method} {path} - "
                f"Status: {response.status_code} - "
                f"Duration: {process_time:.3f}s - "
                f"Client: {client_ip}"
            )

            if query:
                log_message += f" - Query: {query}"

            # Nivel de log según status code
            if response.status_code >= 500:
                logger.error(log_message)
            elif response.status_code >= 400:
                logger.warning(log_message)
            else:
                logger.info(log_message)

            # Agregar header con tiempo de procesamiento
            response.headers["X-Process-Time"] = f"{process_time:.3f}s"

            # ✅ HIGH-01: Record complete HTTP request metrics
            if METRICS_AVAILABLE:
                record_http_request(method, path, response.status_code, process_time)

            return response

        finally:
            # ✅ HIGH-01: Record request end for in_progress metric
            if METRICS_AVAILABLE:
                record_http_request_end(method, path)


def setup_logging_middleware(app: FastAPI):
    """
    Configura el middleware de logging para la aplicación.

    Args:
        app: Instancia de FastAPI
    """
    app.add_middleware(RequestLoggingMiddleware)
    logger.info("Request logging middleware configured")