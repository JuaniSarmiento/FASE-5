"""
AI-Native MVP - FastAPI REST API

Aplicación principal FastAPI para el sistema de enseñanza-aprendizaje
de programación con IA generativa.

Arquitectura C4 Extendida + Clean Architecture + Repository Pattern

Autores: AI-Native Research Team
Versión: 0.1.0
"""
import logging
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .. import __version__, __author__
from ..database import init_database
from .routers import (
    health_router,
    sessions_router,
    interactions_router,
    traces_router,
    risks_router,
    activities_router,
)
# Sprint 3 - Nuevos routers
from .routers.simulators import router as simulators_router
from .routers.cognitive_path import router as cognitive_path_router
from .routers.teacher_tools import router as teacher_tools_router
from .routers.admin_llm import router as admin_llm_router
# Sprint 5 - Git N2 + Analytics + Risk Management
from .routers.git_traces import router as git_traces_router
from .routers.reports import router as reports_router
from .routers.institutional_risks import router as institutional_risks_router
# Sprint 6 - Data Export for Research
from .routers.export import router as export_router
# HIGH-01 - Prometheus Metrics
from .routers.metrics import router as metrics_router
# FASE 3.1 - Nuevos endpoints integrados
from .routers.risk_analysis import router as risk_analysis_router
from .routers.traceability import router as traceability_router
from .routers.git_analytics import router as git_analytics_router
from .routers.evaluations import router as evaluations_router
from .routers.events import router as events_router
from .routers.exercises import router as exercises_router
from .routers.auth_new import router as auth_new_router
from .routers.training import router as training_router
from .middleware import setup_exception_handlers, setup_logging_middleware
from .middleware.rate_limiter import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager para inicialización y limpieza.

    Ejecuta código al inicio y al cierre de la aplicación.

    Args:
        app: Instancia de FastAPI
    """
    # Startup
    logger.info("=" * 80)
    logger.info("AI-Native MVP - Starting up")
    logger.info(f"Version: {__version__}")
    logger.info(f"Authors: {__author__}")
    logger.info("=" * 80)

    # ✅ NUEVO: Validar configuración de entorno
    try:
        logger.info("Validating environment configuration...")
        from .startup_validation import validate_startup_config
        validate_startup_config()
        logger.info("[OK] Configuration validation PASSED")
    except Exception as e:
        logger.error(f"[FAILED] Configuration validation FAILED: {e}")
        logger.error("Server will NOT start with invalid configuration")
        raise

    # Inicializar base de datos
    try:
        logger.info("Initializing database...")
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Inicializar Prometheus metrics
    try:
        logger.info("Initializing Prometheus metrics...")
        from .monitoring.metrics import get_metrics_registry
        get_metrics_registry()
        logger.info("Prometheus metrics initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize Prometheus metrics (non-critical): {e}")

    yield  # Aplicación en ejecución

    # Shutdown
    logger.info("AI-Native MVP - Shutting down")


# =============================================================================
# Crear aplicación FastAPI
# =============================================================================

app = FastAPI(
    title="AI-Native MVP API",
    description="""
    **API REST para el sistema AI-Native de enseñanza-aprendizaje de programación**

    Este sistema implementa un ecosistema completo con 6 agentes de IA que permiten:

    - **Tutorización cognitiva** sin sustituir agencia del estudiante (T-IA-Cog)
    - **Evaluación basada en procesos** (no productos) (E-IA-Proc)
    - **Simulación de roles profesionales** (S-IA-X)
    - **Análisis de riesgos** cognitivos, éticos y técnicos (AR-IA)
    - **Gobernanza institucional** automatizada (GOV-IA)
    - **Trazabilidad cognitiva N4** completa (TC-N4)

    ## Arquitectura

    - **C4 Extended Model**: 6 componentes integrados (C1-C6)
    - **Clean Architecture**: Separación de capas (API, Core, Database)
    - **Repository Pattern**: Abstracción de persistencia
    - **Dependency Injection**: Desacoplamiento de componentes

    ## Características principales

    - ✅ Trazabilidad cognitiva N4 (captura razonamiento completo)
    - ✅ Evaluación de procesos (no solo productos)
    - ✅ Detección de riesgos en 5 dimensiones
    - ✅ Gobernanza institucional verificable
    - ✅ Simuladores profesionales (PO, SM, IT, IR, CX, DSO)

    ## Autores

    Mag. en Ing. de Software Alberto Cortez - Proyecto de investigación doctoral

    ## Documentación

    - 📖 [Guía de uso](../README_MVP.md)
    - 🏗️ [Arquitectura](../IMPLEMENTACIONES_ARQUITECTURALES.md)
    - 🧪 [Testing](../pytest.ini)
    """,
    version=__version__,
    contact={
        "name": __author__,
        "email": "alberto.cortez@example.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "Health",
            "description": "Endpoints de health check y status del servicio",
        },
        {
            "name": "Sessions",
            "description": "Gestión de sesiones de aprendizaje (CRUD)",
        },
        {
            "name": "Interactions",
            "description": "Procesamiento de interacciones estudiante-IA (endpoint principal)",
        },
        {
            "name": "Traceability",
            "description": "Consultas de trazabilidad N4 y reconstrucción de caminos cognitivos",
        },
        {
            "name": "Risks & Evaluation",
            "description": "Análisis de riesgos y reportes de evaluación de procesos",
        },
        {
            "name": "Activities",
            "description": "Gestión de actividades creadas por docentes con políticas pedagógicas configurables",
        },
        {
            "name": "Authentication",
            "description": "JWT Authentication: register, login, token refresh, user management",
        },
        # Sprint 3 - Nuevos tags
        {
            "name": "Simulators",
            "description": "Simuladores profesionales (S-IA-X): PO-IA, SM-IA, IT-IA, IR-IA, CX-IA, DSO-IA",
        },
        {
            "name": "Cognitive Path",
            "description": "Camino cognitivo reconstructivo con visualización de fases y transiciones (HU-EST-006)",
        },
        {
            "name": "Teacher Tools",
            "description": "Herramientas para docentes: comparación de estudiantes, alertas en tiempo real (HU-DOC-003, HU-DOC-004)",
        },
        {
            "name": "Admin - LLM Configuration",
            "description": "Configuración de proveedores LLM y estadísticas de uso (HU-ADM-004)",
        },
        {
            "name": "Data Export",
            "description": "Exportación de datos anonimizados para investigación institucional con garantías de privacidad (HU-ADM-005)",
        },
        {
            "name": "Monitoring",
            "description": "Prometheus metrics endpoint for observability and monitoring (HIGH-01)",
        },
    ],
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# =============================================================================
# Configurar middleware
# =============================================================================

# CORS - Permitir acceso desde frontends (configurado desde variables de entorno)
from .config import CORS_ALLOWED_ORIGINS

# FIX 1.4 Cortez3: Restrict CORS methods and headers (security hardening)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,  # Parametrizado desde .env (ALLOWED_ORIGINS)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],  # FIX 1.4: Explicit methods
    allow_headers=["Content-Type", "Authorization", "X-Request-ID", "Accept", "Accept-Language"],  # FIX 1.4: Explicit headers
    expose_headers=["X-Process-Time", "X-Request-ID", "X-Total-Count"],  # Headers exposed to client
    max_age=3600,  # FIX 1.4: Cache preflight for 1 hour
)

logger.info(f"CORS middleware configured with {len(CORS_ALLOWED_ORIGINS)} allowed origins")

# Compresión GZip para respuestas grandes
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Trusted Host - Prevención de Host Header attacks (opcional)
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["localhost", "127.0.0.1", "your-domain.com"]
# )

# Middleware personalizado
setup_logging_middleware(app)
setup_exception_handlers(app)

# =============================================================================
# Configurar Rate Limiting
# =============================================================================

# Agregar limiter al estado de la app
app.state.limiter = limiter

# Registrar exception handler para rate limit exceeded
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

logger.info("Rate limiting configured: 100 requests/hour default, 10 interactions/minute")


# =============================================================================
# Registrar routers
# =============================================================================

# Prefijo global de API versioning
API_V1_PREFIX = "/api/v1"

app.include_router(health_router, prefix=API_V1_PREFIX)
app.include_router(sessions_router, prefix=API_V1_PREFIX)
app.include_router(interactions_router, prefix=API_V1_PREFIX)
app.include_router(traces_router, prefix=API_V1_PREFIX)
app.include_router(risks_router, prefix=API_V1_PREFIX)
app.include_router(activities_router, prefix=API_V1_PREFIX)

# Sprint 3 - Nuevos routers
app.include_router(simulators_router, prefix=API_V1_PREFIX)
app.include_router(cognitive_path_router, prefix=API_V1_PREFIX)
app.include_router(teacher_tools_router, prefix=API_V1_PREFIX)
app.include_router(admin_llm_router, prefix=API_V1_PREFIX)

# Sprint 5 - Git N2 + Analytics + Risk Management
app.include_router(git_traces_router, prefix=API_V1_PREFIX)
app.include_router(reports_router, prefix=API_V1_PREFIX)
app.include_router(institutional_risks_router, prefix=API_V1_PREFIX)

# Sprint 6 - Data Export for Research
app.include_router(export_router, prefix=API_V1_PREFIX)

# HIGH-01 - Prometheus Metrics (NO prefix, expone en /metrics directamente)
app.include_router(metrics_router)

# FASE 3.1 - Nuevos endpoints integrados con Ollama
app.include_router(risk_analysis_router, prefix=API_V1_PREFIX)
app.include_router(traceability_router, prefix=API_V1_PREFIX)
app.include_router(git_analytics_router, prefix=API_V1_PREFIX)
app.include_router(evaluations_router, prefix=API_V1_PREFIX)
app.include_router(events_router, prefix=API_V1_PREFIX)
app.include_router(exercises_router, prefix=API_V1_PREFIX)
app.include_router(auth_new_router, prefix=API_V1_PREFIX)
app.include_router(training_router, prefix=API_V1_PREFIX)

# FASE 3.2 - Nuevos componentes de UI y Trazabilidad N4 Completa
from .routers.cognitive_status import router as cognitive_status_router
from .routers.simulators_enhanced import router as simulators_enhanced_router

app.include_router(cognitive_status_router, prefix=API_V1_PREFIX)
app.include_router(simulators_enhanced_router, prefix=API_V1_PREFIX)

logger.info(f"Routers registered with prefix: {API_V1_PREFIX} (23 routers total, including FASE 3.2)")
logger.info("Prometheus metrics endpoint: /metrics")


# =============================================================================
# Root endpoint
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz con información general de la API.

    Returns:
        dict: Información del servicio
    """
    return {
        "name": "AI-Native MVP API",
        "version": __version__,
        "description": "API REST para enseñanza-aprendizaje de programación con IA generativa",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_json": "/openapi.json",
        },
        "endpoints": {
            "health": f"{API_V1_PREFIX}/health",
            "sessions": f"{API_V1_PREFIX}/sessions",
            "interactions": f"{API_V1_PREFIX}/interactions",
            "traces": f"{API_V1_PREFIX}/traces",
            "risks": f"{API_V1_PREFIX}/risks",
            "activities": f"{API_V1_PREFIX}/activities",
        },
        "features": [
            "N4 Cognitive Traceability",
            "Process-based Evaluation",
            "Multi-dimensional Risk Analysis",
            "Automated Governance",
            "Professional Simulators",
        ],
        "authors": __author__,
    }


# =============================================================================
# Ejecutar aplicación (para desarrollo)
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    # Configuración para desarrollo
    uvicorn.run(
        "src.ai_native_mvp.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en cambios de código
        log_level="info",
        access_log=True,
    )