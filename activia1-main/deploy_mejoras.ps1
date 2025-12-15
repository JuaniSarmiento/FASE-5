# ========================================================================
# Script de Instalación y Despliegue - Mejoras AI-Native
# ========================================================================
# 
# Despliega las optimizaciones de Ollama y el frontend modernizado
#
# Uso:
#   .\deploy_mejoras.ps1
# ========================================================================

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "  AI-Native - Deploy de Mejoras  " -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Verificar que Docker está corriendo
Write-Host "[1/6] Verificando Docker..." -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host "✓ Docker está corriendo" -ForegroundColor Green
} catch {
    Write-Host "✗ ERROR: Docker no está corriendo" -ForegroundColor Red
    Write-Host "  Por favor inicia Docker Desktop y vuelve a ejecutar este script" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Paso 2: Detener contenedores actuales
Write-Host "[2/6] Deteniendo contenedores actuales..." -ForegroundColor Yellow
docker-compose down
Write-Host "✓ Contenedores detenidos" -ForegroundColor Green
Write-Host ""

# Paso 3: Rebuild con nueva configuración
Write-Host "[3/6] Rebuilding stack con nuevas configuraciones..." -ForegroundColor Yellow
docker-compose up -d --build
Write-Host "✓ Stack levantado" -ForegroundColor Green
Write-Host ""

# Paso 4: Esperar que Ollama esté listo
Write-Host "[4/6] Esperando que Ollama esté listo..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$ready = $false

while (-not $ready -and $attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    try {
        docker exec ai-native-ollama ollama list 2>$null | Out-Null
        $ready = $true
    } catch {
        $attempt++
        Write-Host "  Intento $attempt/$maxAttempts..." -ForegroundColor Gray
    }
}

if ($ready) {
    Write-Host "✓ Ollama está listo" -ForegroundColor Green
} else {
    Write-Host "✗ ERROR: Ollama no respondió después de 60s" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Paso 5: Pull del nuevo modelo llama3.2:3b
Write-Host "[5/6] Descargando modelo llama3.2:3b..." -ForegroundColor Yellow
Write-Host "  (Esto puede tardar 1-2 minutos la primera vez)" -ForegroundColor Gray
docker exec ai-native-ollama ollama pull llama3.2:3b

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Modelo llama3.2:3b descargado" -ForegroundColor Green
} else {
    Write-Host "✗ ERROR: Fallo al descargar modelo" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Paso 6: Instalar dependencias del frontend
Write-Host "[6/6] Instalando dependencias del frontend..." -ForegroundColor Yellow
Push-Location frontEnd
try {
    npm install
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencias instaladas" -ForegroundColor Green
    } else {
        Write-Host "✗ ERROR: Fallo npm install" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} finally {
    Pop-Location
}
Write-Host ""

# Resumen
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "  ✓ Deploy Completado" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend (API):" -ForegroundColor Yellow
Write-Host "  → http://localhost:8000" -ForegroundColor White
Write-Host "  → Modelo: llama3.2:3b (ultra-rápido)" -ForegroundColor White
Write-Host "  → Keep-Alive: Permanente (sin latencia inicial)" -ForegroundColor White
Write-Host ""
Write-Host "Frontend:" -ForegroundColor Yellow
Write-Host "  → Ejecuta: cd frontEnd; npm run dev" -ForegroundColor White
Write-Host "  → URL: http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "Verificar modelo:" -ForegroundColor Yellow
Write-Host "  docker exec ai-native-ollama ollama list" -ForegroundColor White
Write-Host ""
Write-Host "Ver logs:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f api" -ForegroundColor White
Write-Host "  docker-compose logs -f ollama" -ForegroundColor White
Write-Host ""
