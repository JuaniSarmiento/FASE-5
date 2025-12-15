# ============================================================================
# AI-Native MVP - Production Dockerfile
# ============================================================================
# Multi-stage build para optimizar tamaño de imagen y seguridad
#
# Características:
# - Build stage: Compila dependencias
# - Runtime stage: Solo archivos necesarios para ejecución
# - Non-root user para seguridad
# - Health check incluido
#
# Build:
#   docker build -t ai-native-mvp:latest .
#
# Run:
#   docker run -p 8000:8000 --env-file .env ai-native-mvp:latest
# ============================================================================

# ============================================================================
# STAGE 1: Builder - Instalar dependencias
# ============================================================================
FROM python:3.11.9-slim as builder

# Metadata
LABEL maintainer="Alberto Cortez <alberto.cortez@example.com>"
LABEL description="AI-Native MVP - Sistema de Enseñanza-Aprendizaje con IA Generativa"
LABEL version="0.1.0"

# Variables de build
ARG DEBIAN_FRONTEND=noninteractive

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar solo requirements.txt primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python en user directory
# --user instala en ~/.local (sin necesidad de root)
# --no-cache-dir reduce tamaño de imagen
RUN pip install --user --no-cache-dir -r requirements.txt

# ============================================================================
# STAGE 2: Runtime - Imagen final ligera
# ============================================================================
FROM python:3.11.9-slim

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/home/appuser/.local/bin:$PATH

# Instalar dependencias runtime (solo librerías, no compiladores)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear usuario no-root para seguridad
# UID 1000 es estándar para primer usuario en la mayoría de sistemas
RUN useradd -m -u 1000 -s /bin/bash appuser

# Crear directorio de aplicación
WORKDIR /app

# Copiar dependencias instaladas desde builder al home del appuser
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copiar código fuente (NO copiar .env - debe proporcionarse via --env-file o docker-compose)
COPY --chown=appuser:appuser backend/ backend/
# SECURITY: Do NOT copy .env.example into the image - environment variables must be
# provided at runtime via --env-file or docker-compose environment section

# Crear directorio para base de datos SQLite (si se usa)
RUN mkdir -p /app/data && chown appuser:appuser /app/data

# Cambiar a usuario no-root
USER appuser

# Exponer puerto 8000
EXPOSE 8000

# Health check (verifica que el servidor responde)
# Docker marca container como unhealthy si falla 3 veces consecutivas
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando de inicio
# --host 0.0.0.0: Escuchar en todas las interfaces (necesario para Docker)
# --port 8000: Puerto de la aplicación
# --workers 4: Número de workers (ajustar según CPU cores disponibles)
# --log-level info: Nivel de logging
CMD ["uvicorn", "backend.api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "info"]

# ============================================================================
# Notas de Uso
# ============================================================================
#
# Build:
#   docker build -t ai-native-mvp:latest .
#
# Run (standalone):
#   docker run -d \
#     --name ai-native-api \
#     -p 8000:8000 \
#     --env-file .env \
#     ai-native-mvp:latest
#
# Run (con docker-compose):
#   docker-compose up -d
#
# Logs:
#   docker logs -f ai-native-api
#
# Shell interactivo:
#   docker exec -it ai-native-api /bin/bash
#
# Stop:
#   docker stop ai-native-api
#
# ============================================================================