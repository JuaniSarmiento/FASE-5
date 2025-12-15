"""
Middleware para manejo centralizado de errores
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import traceback
import logging

from backend.core.constants import utc_now

from ..exceptions import AINativeAPIException
from ..schemas.common import ErrorResponse, ErrorDetail

logger = logging.getLogger(__name__)


def setup_exception_handlers(app: FastAPI):
    """
    Configura los manejadores de excepciones para la aplicación FastAPI.

    Args:
        app: Instancia de FastAPI
    """

    @app.exception_handler(AINativeAPIException)
    async def ainative_exception_handler(request: Request, exc: AINativeAPIException):
        """
        Maneja excepciones personalizadas de AI-Native.

        Args:
            request: Request de FastAPI
            exc: Excepción de AI-Native

        Returns:
            JSONResponse con error estructurado
        """
        logger.warning(
            f"AINative exception: {exc.error_code} - {exc.detail}",
            extra={"extra": exc.extra, "path": request.url.path}
        )

        error_response = ErrorResponse(
            success=False,
            error=ErrorDetail(
                error_code=exc.error_code or "UNKNOWN_ERROR",
                message=exc.detail,
                extra=exc.extra,
            ),
            timestamp=utc_now(),
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(mode="json"),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Maneja errores de validación de Pydantic.

        Args:
            request: Request de FastAPI
            exc: Error de validación

        Returns:
            JSONResponse con detalles de validación
        """
        logger.warning(
            f"Validation error on {request.url.path}: {exc.errors()}",
        )

        # Extraer primer error para el mensaje principal
        first_error = exc.errors()[0] if exc.errors() else {}
        field = ".".join(str(loc) for loc in first_error.get("loc", []))
        message = first_error.get("msg", "Validation error")

        # Clean errors: convert ValueError objects to strings for serialization
        cleaned_errors = []
        for error in exc.errors():
            cleaned_error = {
                "type": error.get("type"),
                "loc": error.get("loc"),
                "msg": error.get("msg"),
                "input": str(error.get("input", ""))[:100],  # Truncate long inputs
            }
            # Extract error message from ctx if present (for value_error types)
            if "ctx" in error and "error" in error["ctx"]:
                error_obj = error["ctx"]["error"]
                cleaned_error["detail"] = str(error_obj)
            cleaned_errors.append(cleaned_error)

        error_response = ErrorResponse(
            success=False,
            error=ErrorDetail(
                error_code="VALIDATION_ERROR",
                message=f"Validation error in field '{field}': {message}",
                field=field,
                extra={"errors": cleaned_errors},
            ),
            timestamp=utc_now(),
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(mode="json"),
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_exception_handler(request: Request, exc: SQLAlchemyError):
        """
        Maneja errores de base de datos.

        Args:
            request: Request de FastAPI
            exc: Error de SQLAlchemy

        Returns:
            JSONResponse con error de base de datos
        """
        logger.error(
            f"Database error on {request.url.path}: {str(exc)}",
            exc_info=True,
        )

        error_response = ErrorResponse(
            success=False,
            error=ErrorDetail(
                error_code="DATABASE_ERROR",
                message="A database error occurred",
                extra={"details": str(exc) if app.debug else "Contact support"},
            ),
            timestamp=utc_now(),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        """
        Maneja excepciones no capturadas.

        Args:
            request: Request de FastAPI
            exc: Excepción genérica

        Returns:
            JSONResponse con error interno
        """
        logger.error(
            f"Unhandled exception on {request.url.path}: {str(exc)}",
            exc_info=True,
        )

        # En desarrollo, incluir traceback
        extra_info = {}
        if app.debug:
            extra_info["traceback"] = traceback.format_exc()
            extra_info["exception_type"] = type(exc).__name__

        error_response = ErrorResponse(
            success=False,
            error=ErrorDetail(
                error_code="INTERNAL_ERROR",
                message="An internal server error occurred",
                extra=extra_info if app.debug else {"details": "Contact support"},
            ),
            timestamp=utc_now(),
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(mode="json"),
        )

    logger.info("Exception handlers configured")