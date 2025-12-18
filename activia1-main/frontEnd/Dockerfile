# ============================================================================
# AI-Native MVP - Frontend Dockerfile
# ============================================================================
# Build optimizado para React + Vite con TypeScript
# ============================================================================

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files primero para aprovechar cache de Docker
COPY package*.json ./

# Instalar dependencias (todas, incluyendo devDependencies para el build)
RUN npm ci

# Copiar el resto del código
COPY . .

# Build de producción
RUN npm run build

# Stage 2: Production
FROM nginx:1.25-alpine

# Copiar archivos compilados desde builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración de nginx personalizada
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://127.0.0.1/health || exit 1

# Nginx se ejecuta automáticamente como comando por defecto
CMD ["nginx", "-g", "daemon off;"]
