"""
Script para ejecutar la API REST del MVP AI-Native

Este script inicia el servidor FastAPI con uvicorn.

Uso:
    python scripts/run_api.py              # Modo desarrollo
    python scripts/run_api.py --production # Modo producción
"""
import sys
import os
import argparse

# Agregar directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_dev_server():
    """Ejecuta servidor en modo desarrollo con auto-reload"""
    import uvicorn

    print("=" * 80)
    print("AI-Native MVP - Development Server")
    print("=" * 80)
    print("Starting FastAPI server in development mode...")
    print("Server: http://localhost:8000")
    print("Swagger UI: http://localhost:8000/docs")
    print("ReDoc: http://localhost:8000/redoc")
    print("=" * 80)

    uvicorn.run(
        "src.ai_native_mvp.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload en cambios
        log_level="info",
        access_log=True,
    )


def run_production_server():
    """Ejecuta servidor en modo producción"""
    import uvicorn

    print("=" * 80)
    print("AI-Native MVP - Production Server")
    print("=" * 80)
    print("Starting FastAPI server in production mode...")
    print("Server: http://localhost:8000")
    print("=" * 80)

    uvicorn.run(
        "src.ai_native_mvp.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Sin auto-reload
        workers=4,  # Múltiples workers para producción
        log_level="warning",
        access_log=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run AI-Native MVP API Server")
    parser.add_argument(
        "--production",
        action="store_true",
        help="Run in production mode (no auto-reload, multiple workers)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )

    args = parser.parse_args()

    if args.production:
        run_production_server()
    else:
        run_dev_server()
