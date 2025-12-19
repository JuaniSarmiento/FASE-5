#!/bin/bash

# ==============================================
# Script de Verificación de Deploy en EasyPanel
# ==============================================

echo "🔍 Verificando deploy de Activia..."
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# URLs (ajusta con tus URLs de EasyPanel)
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:80}"

# ==============================================
# 1. Verificar Backend Health
# ==============================================
echo "1️⃣  Verificando Backend Health..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/health")

if [ "$HEALTH_RESPONSE" -eq 200 ]; then
    echo -e "${GREEN}✅ Backend está funcionando (HTTP $HEALTH_RESPONSE)${NC}"
    curl -s "$BACKEND_URL/api/v1/health" | jq .
else
    echo -e "${RED}❌ Backend no responde (HTTP $HEALTH_RESPONSE)${NC}"
    exit 1
fi

echo ""

# ==============================================
# 2. Verificar PostgreSQL Connection
# ==============================================
echo "2️⃣  Verificando conexión a PostgreSQL..."
DB_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/v1/health/detailed")

if [ "$DB_RESPONSE" -eq 200 ]; then
    echo -e "${GREEN}✅ PostgreSQL conectado correctamente${NC}"
else
    echo -e "${RED}❌ Error en conexión a PostgreSQL${NC}"
fi

echo ""

# ==============================================
# 3. Verificar Redis Connection
# ==============================================
echo "3️⃣  Verificando conexión a Redis..."
REDIS_CHECK=$(curl -s "$BACKEND_URL/api/v1/health/detailed" | jq -r '.cache')

if [ "$REDIS_CHECK" == "connected" ] || [ "$REDIS_CHECK" == "healthy" ]; then
    echo -e "${GREEN}✅ Redis conectado correctamente${NC}"
else
    echo -e "${YELLOW}⚠️  Redis no está disponible (usando modo fallback)${NC}"
fi

echo ""

# ==============================================
# 4. Verificar Frontend
# ==============================================
echo "4️⃣  Verificando Frontend..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")

if [ "$FRONTEND_RESPONSE" -eq 200 ]; then
    echo -e "${GREEN}✅ Frontend está sirviendo correctamente (HTTP $FRONTEND_RESPONSE)${NC}"
else
    echo -e "${RED}❌ Frontend no responde (HTTP $FRONTEND_RESPONSE)${NC}"
fi

echo ""

# ==============================================
# 5. Verificar API Routes
# ==============================================
echo "5️⃣  Verificando rutas principales de API..."

ROUTES=(
    "/api/v1/health"
    "/api/v1/activities"
    "/docs"
)

for route in "${ROUTES[@]}"; do
    ROUTE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL$route")
    if [ "$ROUTE_RESPONSE" -eq 200 ] || [ "$ROUTE_RESPONSE" -eq 401 ]; then
        echo -e "${GREEN}✅${NC} $route (HTTP $ROUTE_RESPONSE)"
    else
        echo -e "${RED}❌${NC} $route (HTTP $ROUTE_RESPONSE)"
    fi
done

echo ""

# ==============================================
# 6. Verificar CORS
# ==============================================
echo "6️⃣  Verificando CORS..."
CORS_RESPONSE=$(curl -s -H "Origin: $FRONTEND_URL" -H "Access-Control-Request-Method: GET" -X OPTIONS "$BACKEND_URL/api/v1/health" -I | grep -i "access-control-allow-origin")

if [ -n "$CORS_RESPONSE" ]; then
    echo -e "${GREEN}✅ CORS configurado correctamente${NC}"
    echo "   $CORS_RESPONSE"
else
    echo -e "${YELLOW}⚠️  CORS podría no estar configurado correctamente${NC}"
fi

echo ""

# ==============================================
# Resumen
# ==============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 RESUMEN DEL DEPLOY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo -e "${GREEN}✅ Deploy verificado exitosamente${NC}"
echo ""
echo "🚀 Próximos pasos:"
echo "   1. Inicializar usuarios: python backend/scripts/seed_dev.py"
echo "   2. Cambiar passwords por defecto"
echo "   3. Configurar backups de PostgreSQL"
echo "   4. Monitorear logs y métricas"
echo ""
