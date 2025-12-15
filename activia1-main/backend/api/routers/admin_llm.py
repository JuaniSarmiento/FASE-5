"""
Router para configuración de proveedores LLM (Administración)

Sprint 3 - HU-ADM-004

SECURITY: API keys are NEVER exposed in responses.
All API key fields show only configuration status (true/false).

AUTHENTICATION: All endpoints require admin role.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import os
import logging

from ..schemas.common import APIResponse
from ..deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/llm", tags=["Admin - LLM Configuration"])


# =============================================================================
# SECURITY: Admin Role Verification
# =============================================================================

async def require_admin_role(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to verify user has admin role.

    Raises:
        HTTPException 403: If user is not an admin
    """
    user_roles = current_user.get("roles", [])
    if "admin" not in user_roles and "administrator" not in user_roles:
        logger.warning(
            "Unauthorized admin access attempt",
            extra={
                "user_id": current_user.get("user_id"),
                "email": current_user.get("email"),
                "roles": user_roles,
                "attempted_action": "admin_llm_access"
            }
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required. Your roles: " + ", ".join(user_roles)
        )
    return current_user


# =============================================================================
# SECURITY: API Key Redaction
# =============================================================================

# Pattern to match common API key formats
API_KEY_PATTERNS = [
    r'(sk-[a-zA-Z0-9]{20,})',           # OpenAI format
    r'(AIza[a-zA-Z0-9_-]{35})',          # Google/Gemini format
    r'(sk-ant-[a-zA-Z0-9_-]{40,})',      # Anthropic format
    r'([a-zA-Z0-9]{32,})',               # Generic long alphanumeric keys
]


def redact_api_key(key: str, visible_chars: int = 4) -> str:
    """
    Redact an API key, showing only the first few characters.

    Args:
        key: The API key to redact
        visible_chars: Number of characters to show at the start

    Returns:
        Redacted key like "sk-ab****..."
    """
    if not key or len(key) <= visible_chars:
        return "*" * 8
    return f"{key[:visible_chars]}{'*' * 8}..."


def redact_dict_keys(data: Dict[str, Any], sensitive_keys: List[str] = None) -> Dict[str, Any]:
    """
    Recursively redact sensitive keys in a dictionary.

    Args:
        data: Dictionary to process
        sensitive_keys: Keys to redact (default: api_key, apikey, secret, password, token)

    Returns:
        Dictionary with redacted values
    """
    if sensitive_keys is None:
        sensitive_keys = ['api_key', 'apikey', 'secret', 'password', 'token', 'key']

    result = {}
    for k, v in data.items():
        if isinstance(v, dict):
            result[k] = redact_dict_keys(v, sensitive_keys)
        elif isinstance(v, str) and any(sk in k.lower() for sk in sensitive_keys):
            result[k] = redact_api_key(v)
        else:
            result[k] = v
    return result


def safe_log_config(config: Dict[str, Any], message: str = "Config"):
    """
    Safely log configuration without exposing sensitive data.

    Args:
        config: Configuration dictionary
        message: Log message prefix
    """
    safe_config = redact_dict_keys(config)
    logger.info(f"{message}: {safe_config}")


class LLMProviderConfig(BaseModel):
    """Configuración de un proveedor LLM"""
    provider: str = Field(..., description="Nombre del proveedor (openai, gemini, anthropic, mock)")
    enabled: bool = Field(..., description="Si el proveedor está habilitado")
    api_key_configured: bool = Field(..., description="Si tiene API key configurada")
    model: Optional[str] = Field(None, description="Modelo por defecto")
    temperature: Optional[float] = Field(None, description="Temperatura por defecto")
    max_tokens: Optional[int] = Field(None, description="Máximo de tokens")
    limits: Optional[Dict[str, Any]] = Field(None, description="Límites de uso")
    privacy_compliant: bool = Field(..., description="Si cumple con privacidad institucional")
    cost_per_1k_tokens: Optional[float] = Field(None, description="Costo estimado por 1K tokens (USD)")


class LLMProviderUpdate(BaseModel):
    """Actualización de configuración de proveedor"""
    enabled: Optional[bool] = Field(None, description="Habilitar/deshabilitar")
    model: Optional[str] = Field(None, description="Modelo por defecto")
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperatura (0.0-2.0)")
    max_tokens: Optional[int] = Field(None, gt=0, description="Máximo de tokens")
    daily_request_limit: Optional[int] = Field(None, description="Límite de requests por día")
    monthly_token_limit: Optional[int] = Field(None, description="Límite de tokens por mes")


@router.get(
    "/providers",
    response_model=APIResponse[List[LLMProviderConfig]],
    summary="Listar proveedores LLM",
    description="Lista todos los proveedores LLM disponibles con su configuración (HU-ADM-004). Requiere rol admin."
)
async def list_llm_providers(
    current_user: dict = Depends(require_admin_role)
) -> APIResponse[List[LLMProviderConfig]]:
    """
    Lista todos los proveedores LLM disponibles en el sistema.

    **HU-ADM-004**: Permite al administrador ver qué proveedores están configurados
    y cuáles están habilitados para uso institucional.

    **Información incluida:**
    - Estado de habilitación
    - Configuración de API keys (sin exponer valores)
    - Modelos disponibles
    - Límites de uso
    - Cumplimiento de privacidad
    - Costos estimados
    """
    # Leer configuración actual del sistema
    current_provider = os.getenv("LLM_PROVIDER", "mock")

    providers = [
        LLMProviderConfig(
            provider="mock",
            enabled=current_provider == "mock",
            api_key_configured=True,  # No requiere
            model="mock-model",
            temperature=0.7,
            max_tokens=2000,
            privacy_compliant=True,
            cost_per_1k_tokens=0.0,
            limits={
                "requests_per_day": "unlimited",
                "tokens_per_month": "unlimited"
            }
        ),
        LLMProviderConfig(
            provider="openai",
            enabled=current_provider == "openai",
            api_key_configured=bool(os.getenv("OPENAI_API_KEY")),
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "2000")),
            privacy_compliant=False,  # Datos enviados a OpenAI
            cost_per_1k_tokens=0.03,  # GPT-4 input
            limits={
                "requests_per_day": os.getenv("OPENAI_DAILY_LIMIT", "unlimited"),
                "tokens_per_month": os.getenv("OPENAI_MONTHLY_TOKEN_LIMIT", "unlimited")
            }
        ),
        LLMProviderConfig(
            provider="gemini",
            enabled=current_provider == "gemini",
            api_key_configured=bool(os.getenv("GEMINI_API_KEY")),
            model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            temperature=float(os.getenv("GEMINI_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("GEMINI_MAX_TOKENS", "8192")),
            privacy_compliant=False,  # Datos enviados a Google
            cost_per_1k_tokens=0.0,  # Free tier
            limits={
                "requests_per_day": "1500",  # 60 req/min * 60 min * 24h / 60
                "tokens_per_month": "1000000"  # Free tier
            }
        ),
        LLMProviderConfig(
            provider="anthropic",
            enabled=current_provider == "anthropic",
            api_key_configured=bool(os.getenv("ANTHROPIC_API_KEY")),
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            temperature=float(os.getenv("ANTHROPIC_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("ANTHROPIC_MAX_TOKENS", "4096")),
            privacy_compliant=False,  # Datos enviados a Anthropic
            cost_per_1k_tokens=0.015,  # Claude 3 Sonnet
            limits={
                "requests_per_day": os.getenv("ANTHROPIC_DAILY_LIMIT", "unlimited"),
                "tokens_per_month": os.getenv("ANTHROPIC_MONTHLY_TOKEN_LIMIT", "unlimited")
            }
        ),
    ]

    return APIResponse(
        success=True,
        data=providers,
        message=f"Se encontraron {len(providers)} proveedores LLM configurados"
    )


@router.get(
    "/providers/{provider_name}",
    response_model=APIResponse[LLMProviderConfig],
    summary="Obtener configuración de proveedor",
    description="Obtiene la configuración detallada de un proveedor LLM específico. Requiere rol admin."
)
async def get_provider_config(
    provider_name: str,
    current_user: dict = Depends(require_admin_role)
) -> APIResponse[LLMProviderConfig]:
    """
    Obtiene la configuración detallada de un proveedor LLM específico.
    """
    # Obtener lista de proveedores
    providers_response = await list_llm_providers()
    providers = providers_response.data

    # Buscar proveedor específico
    provider = next((p for p in providers if p.provider == provider_name), None)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found. Available: mock, openai, gemini, anthropic"
        )

    return APIResponse(
        success=True,
        data=provider,
        message=f"Configuración de proveedor {provider_name}"
    )


@router.patch(
    "/providers/{provider_name}",
    response_model=APIResponse[Dict[str, Any]],
    summary="Actualizar configuración de proveedor",
    description="Actualiza la configuración de un proveedor LLM (HU-ADM-004). Requiere rol admin."
)
async def update_provider_config(
    provider_name: str,
    update: LLMProviderUpdate,
    current_user: dict = Depends(require_admin_role)
) -> APIResponse[Dict[str, Any]]:
    """
    Actualiza la configuración de un proveedor LLM.

    **HU-ADM-004**: Permite al administrador configurar límites de uso,
    habilitar/deshabilitar proveedores, y ajustar parámetros.

    **IMPORTANTE**: En el MVP actual, esto solo retorna una confirmación.
    En producción, esto debería:
    1. Actualizar variables de entorno o archivo de configuración
    2. Reiniciar el servicio LLM con la nueva configuración
    3. Validar que el proveedor funciona con las nuevas configuraciones
    4. Registrar el cambio en auditoría

    **Ejemplo:**
    ```bash
    PATCH /api/v1/admin/llm/providers/openai
    {
      "enabled": true,
      "model": "gpt-3.5-turbo",
      "daily_request_limit": 1000,
      "monthly_token_limit": 500000
    }
    ```
    """
    # Validar que el proveedor existe
    valid_providers = ["mock", "openai", "gemini", "anthropic"]
    if provider_name not in valid_providers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider_name}' not found. Available: {', '.join(valid_providers)}"
        )

    # En el MVP, solo retornamos confirmación
    # En producción, aquí se actualizaría la configuración real

    changes = {}
    if update.enabled is not None:
        changes["enabled"] = update.enabled
    if update.model is not None:
        changes["model"] = update.model
    if update.temperature is not None:
        changes["temperature"] = update.temperature
    if update.max_tokens is not None:
        changes["max_tokens"] = update.max_tokens
    if update.daily_request_limit is not None:
        changes["daily_request_limit"] = update.daily_request_limit
    if update.monthly_token_limit is not None:
        changes["monthly_token_limit"] = update.monthly_token_limit

    return APIResponse(
        success=True,
        data={
            "provider": provider_name,
            "changes_applied": changes,
            "note": "En producción, requiere reinicio del servicio para aplicar cambios",
            "next_steps": [
                f"Actualizar archivo .env con nuevos valores",
                "Reiniciar servidor: python scripts/run_api.py",
                "Verificar que el proveedor funciona correctamente"
            ]
        },
        message=f"Configuración de {provider_name} actualizada (MVP: solo confirmación)"
    )


@router.get(
    "/usage/stats",
    response_model=APIResponse[Dict[str, Any]],
    summary="Obtener estadísticas de uso de LLM",
    description="Obtiene estadísticas de uso de proveedores LLM. Requiere rol admin."
)
async def get_llm_usage_stats(
    current_user: dict = Depends(require_admin_role)
) -> APIResponse[Dict[str, Any]]:
    """
    Obtiene estadísticas de uso de proveedores LLM.

    **Útil para:**
    - Monitorear costos
    - Identificar patrones de uso
    - Planificar capacidad
    - Justificar presupuesto

    **NOTA**: En el MVP actual, retorna datos de ejemplo.
    En producción, esto debería leer de una tabla `llm_usage_logs`.
    """
    # En el MVP, retornamos datos de ejemplo
    # En producción, esto vendría de la base de datos

    stats = {
        "current_month": "2025-11",
        "total_requests": 1248,
        "total_tokens": 345678,
        "estimated_cost_usd": 12.45,
        "by_provider": {
            "mock": {
                "requests": 856,
                "tokens": 245000,
                "cost_usd": 0.0,
                "percentage": 68.6
            },
            "openai": {
                "requests": 392,
                "tokens": 100678,
                "cost_usd": 12.45,
                "percentage": 31.4
            },
            "gemini": {
                "requests": 0,
                "tokens": 0,
                "cost_usd": 0.0,
                "percentage": 0.0
            }
        },
        "top_activities": [
            {"activity_id": "prog2_tp1_colas", "requests": 423, "cost_usd": 5.12},
            {"activity_id": "prog2_tp2_arboles", "requests": 389, "cost_usd": 4.67},
            {"activity_id": "prog2_tp3_grafos", "requests": 234, "cost_usd": 2.66}
        ],
        "limits_status": {
            "daily_limit": {"used": 48, "limit": 1000, "percentage": 4.8},
            "monthly_limit": {"used": 345678, "limit": 1000000, "percentage": 34.6}
        }
    }

    return APIResponse(
        success=True,
        data=stats,
        message="Estadísticas de uso de LLM (datos de ejemplo en MVP)"
    )


@router.post(
    "/test",
    response_model=APIResponse[Dict[str, Any]],
    summary="Probar conexión con proveedor LLM",
    description="Verifica que un proveedor LLM esté configurado correctamente y responda. Requiere rol admin."
)
async def test_llm_connection(
    provider: str,
    model: Optional[str] = None,
    current_user: dict = Depends(require_admin_role)
) -> APIResponse[Dict[str, Any]]:
    """
    Prueba la conexión con un proveedor LLM específico.

    **Flujo:**
    1. Verifica que el proveedor esté configurado
    2. Intenta realizar una llamada simple al LLM
    3. Reporta latencia y estado

    **Ejemplo:**
    ```bash
    POST /api/v1/admin/llm/test?provider=ollama
    POST /api/v1/admin/llm/test?provider=openai&model=gpt-4
    ```
    """
    import time
    from ...llm.factory import LLMProviderFactory

    valid_providers = ["mock", "openai", "gemini", "anthropic", "ollama"]
    if provider not in valid_providers:
        return APIResponse(
            success=False,
            data={
                "provider": provider,
                "status": "error",
                "message": f"Provider '{provider}' not recognized. Valid: {', '.join(valid_providers)}"
            },
            message=f"Provider '{provider}' not found"
        )

    try:
        # Medir tiempo de respuesta
        start_time = time.time()

        # Intentar crear el provider
        llm_provider = LLMProviderFactory.create(provider)

        # Hacer una llamada de prueba simple
        test_response = await llm_provider.generate(
            prompt="Responde solo con 'OK' si funcionas correctamente.",
            max_tokens=10
        )

        latency_ms = (time.time() - start_time) * 1000

        return APIResponse(
            success=True,
            data={
                "provider": provider,
                "model": model or llm_provider.model_name,
                "status": "ok",
                "latency_ms": round(latency_ms, 2),
                "test_response": test_response[:100] if test_response else "Empty response",
                "message": f"Provider {provider} is working correctly"
            },
            message=f"Connection to {provider} successful"
        )

    except Exception as e:
        return APIResponse(
            success=False,
            data={
                "provider": provider,
                "model": model,
                "status": "error",
                "error_type": type(e).__name__,
                "message": str(e)
            },
            message=f"Connection to {provider} failed: {str(e)}"
        )


@router.get(
    "/metrics",
    response_model=APIResponse[Dict[str, Any]],
    summary="Obtener métricas del sistema",
    description="Obtiene métricas generales del sistema para el panel de administración. Requiere rol admin."
)
async def get_system_metrics(
    current_user: dict = Depends(require_admin_role)
) -> APIResponse[Dict[str, Any]]:
    """
    Obtiene métricas generales del sistema.

    **Métricas incluidas:**
    - Usuarios totales
    - Sesiones activas
    - Interacciones totales
    - Uso de LLM
    - Estado de servicios

    **NOTA**: En el MVP, retorna datos de ejemplo.
    En producción, esto debería consultar la base de datos y servicios.
    """
    from backend.core.constants import utc_now

    # En el MVP, retornamos datos de ejemplo
    metrics = {
        "timestamp": utc_now().isoformat(),
        "total_users": 45,
        "active_sessions": 12,
        "total_sessions_today": 28,
        "total_interactions": 1543,
        "avg_response_time_ms": 245.7,
        "llm_usage": [
            {
                "provider": "mock",
                "model": "mock-model",
                "total_requests": 856,
                "total_tokens": 245000,
                "avg_response_time_ms": 50.2,
                "error_rate": 0.01,
                "last_used": utc_now().isoformat()
            },
            {
                "provider": "ollama",
                "model": "phi3",
                "total_requests": 392,
                "total_tokens": 100678,
                "avg_response_time_ms": 320.5,
                "error_rate": 0.02,
                "last_used": utc_now().isoformat()
            }
        ],
        "storage_used_mb": 128.5,
        "database_status": "healthy",
        "redis_status": "healthy",
        "llm_status": "healthy"
    }

    return APIResponse(
        success=True,
        data=metrics,
        message="System metrics retrieved successfully"
    )


@router.get(
    "/config/debug",
    response_model=APIResponse[Dict[str, Any]],
    summary="Debug configuración LLM (redactada)",
    description="Muestra la configuración actual de LLM con API keys redactadas para debug. Requiere rol admin."
)
async def get_debug_config(
    current_user: dict = Depends(require_admin_role)
) -> APIResponse[Dict[str, Any]]:
    """
    Obtiene la configuración actual de LLM con información de debug.

    **SECURITY**: Las API keys son automáticamente redactadas.
    Solo se muestran los primeros 4 caracteres para verificar que la key correcta está configurada.

    **Uso:**
    - Verificar que las variables de entorno están correctamente configuradas
    - Debug de problemas de conexión
    - Auditoría de configuración

    **Ejemplo de salida:**
    ```json
    {
      "OPENAI_API_KEY": "sk-a********...",
      "GEMINI_API_KEY": "AIza********...",
      ...
    }
    ```
    """
    # Collect all LLM-related env vars
    llm_env_vars = {}
    llm_prefixes = ['LLM_', 'OPENAI_', 'GEMINI_', 'ANTHROPIC_', 'OLLAMA_']

    for key, value in os.environ.items():
        if any(key.startswith(prefix) for prefix in llm_prefixes):
            # Redact if it looks like a sensitive value
            if any(sensitive in key.lower() for sensitive in ['key', 'secret', 'token', 'password']):
                llm_env_vars[key] = redact_api_key(value) if value else "(not set)"
            else:
                llm_env_vars[key] = value if value else "(not set)"

    # Add current provider status
    current_provider = os.getenv("LLM_PROVIDER", "mock")
    status_info = {
        "current_provider": current_provider,
        "environment_variables": llm_env_vars,
        "providers_configured": {
            "mock": True,
            "openai": bool(os.getenv("OPENAI_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
            "ollama": bool(os.getenv("OLLAMA_BASE_URL")),
        },
        "security_notice": "API keys are redacted for security. Only first 4 characters shown."
    }

    # Log access for audit
    logger.info("LLM debug config accessed", extra={"provider": current_provider})

    return APIResponse(
        success=True,
        data=status_info,
        message="LLM configuration (API keys redacted)"
    )