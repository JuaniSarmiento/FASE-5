"""
Excepciones personalizadas para la API REST
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class AINativeAPIException(HTTPException):
    """Excepción base para la API AI-Native"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code
        self.extra = extra or {}


class SessionNotFoundError(AINativeAPIException):
    """Sesión no encontrada"""

    def __init__(self, session_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found",
            error_code="SESSION_NOT_FOUND",
            extra={"session_id": session_id}
        )


class StudentNotFoundError(AINativeAPIException):
    """Estudiante no encontrado"""

    def __init__(self, student_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student '{student_id}' not found",
            error_code="STUDENT_NOT_FOUND",
            extra={"student_id": student_id}
        )


class InvalidInteractionError(AINativeAPIException):
    """Interacción inválida"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
            error_code="INVALID_INTERACTION",
            extra=details or {}
        )


class GovernanceBlockedError(AINativeAPIException):
    """Interacción bloqueada por políticas de gobernanza"""

    def __init__(self, reason: str, policy: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Interaction blocked by governance: {reason}",
            error_code="GOVERNANCE_BLOCKED",
            extra={"reason": reason, "policy": policy}
        )


class RiskThresholdExceededError(AINativeAPIException):
    """Umbral de riesgo excedido"""

    def __init__(self, risk_type: str, risk_level: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Risk threshold exceeded: {risk_type} ({risk_level})",
            error_code="RISK_THRESHOLD_EXCEEDED",
            extra={"risk_type": risk_type, "risk_level": risk_level}
        )


class AgentNotAvailableError(AINativeAPIException):
    """Agente no disponible"""

    def __init__(self, agent_name: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Agent '{agent_name}' is not available",
            error_code="AGENT_NOT_AVAILABLE",
            extra={"agent_name": agent_name}
        )


class DatabaseOperationError(AINativeAPIException):
    """Error en operación de base de datos"""

    def __init__(self, operation: str, details: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database operation failed: {operation}",
            error_code="DATABASE_ERROR",
            extra={"operation": operation, "details": details}
        )


class AuthenticationError(AINativeAPIException):
    """Error de autenticación"""

    def __init__(self, detail: str = "Invalid authentication credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_FAILED",
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(AINativeAPIException):
    """Error de autorización"""

    def __init__(self, detail: str = "Not authorized to perform this action"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_FAILED"
        )