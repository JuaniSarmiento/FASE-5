# ========================================================================
# Test Rápido de Mejoras Backend
# ========================================================================
# 
# Valida que los cambios implementados funcionen correctamente
#
# Uso:
#   .\test_backend_mejoras.ps1
# ========================================================================

Write-Host "=================================" -ForegroundColor Cyan
Write-Host "  Test de Mejoras Backend  " -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: API Health
Write-Host "[1/4] Verificando API Health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method Get
    if ($response.status -eq "healthy") {
        Write-Host "✓ API está healthy" -ForegroundColor Green
    } else {
        Write-Host "✗ API no está healthy: $($response.status)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ ERROR: No se puede conectar a la API" -ForegroundColor Red
    Write-Host "  Detalles: $_" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Test 2: Verificar modelo
Write-Host "[2/4] Verificando modelo Ollama..." -ForegroundColor Yellow
$models = docker exec ai-native-ollama ollama list
if ($models -match "llama3.2:3b") {
    Write-Host "✓ Modelo llama3.2:3b instalado" -ForegroundColor Green
} else {
    Write-Host "⚠ Modelo llama3.2:3b NO encontrado" -ForegroundColor Yellow
    Write-Host "  Ejecuta: docker exec ai-native-ollama ollama pull llama3.2:3b" -ForegroundColor Yellow
}
Write-Host ""

# Test 3: Verificar Keep-Alive
Write-Host "[3/4] Verificando Keep-Alive..." -ForegroundColor Yellow
$env = docker exec ai-native-ollama env | Select-String "OLLAMA_KEEP_ALIVE"
if ($env -match "OLLAMA_KEEP_ALIVE=-1") {
    Write-Host "✓ Keep-Alive configurado correctamente (-1)" -ForegroundColor Green
} else {
    Write-Host "⚠ Keep-Alive NO configurado" -ForegroundColor Yellow
    Write-Host "  Valor actual: $env" -ForegroundColor Gray
}
Write-Host ""

# Test 4: Test de latencia (si llama3.2:3b está disponible)
Write-Host "[4/4] Test de latencia..." -ForegroundColor Yellow
if ($models -match "llama3.2:3b") {
    Write-Host "  Haciendo consulta de prueba..." -ForegroundColor Gray
    
    $body = @{
        session_id = "test-mejoras"
        prompt = "Hola"
    } | ConvertTo-Json
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        $response = Invoke-RestMethod `
            -Uri "http://localhost:8000/api/v1/tutor/ask" `
            -Method Post `
            -ContentType "application/json" `
            -Body $body `
            -TimeoutSec 30
        
        $stopwatch.Stop()
        $latency = $stopwatch.Elapsed.TotalSeconds
        
        Write-Host "  ✓ Consulta exitosa" -ForegroundColor Green
        Write-Host "  Latencia: $([math]::Round($latency, 2))s" -ForegroundColor Cyan
        
        if ($latency -lt 3) {
            Write-Host "  🎉 EXCELENTE: menor a 3s (objetivo cumplido)" -ForegroundColor Green
        } elseif ($latency -lt 5) {
            Write-Host "  ✓ BUENO: menor a 5s" -ForegroundColor Green
        } else {
            Write-Host "  ⚠ LENTO: mayor a 5s (esperado: menor a 3s)" -ForegroundColor Yellow
        }
        
        # Verificar si usó reintentos (buscar en metadata)
        if ($response.metadata -and $response.metadata.attempts) {
            Write-Host "  Reintentos: $($response.metadata.attempts)" -ForegroundColor Gray
        }
        
    } catch {
        $stopwatch.Stop()
        Write-Host "  ✗ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "  ⏭ Omitido (llama3.2:3b no disponible)" -ForegroundColor Gray
}
Write-Host ""

# Resumen
Write-Host "=================================" -ForegroundColor Cyan
Write-Host "  Resumen" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Mejoras implementadas:" -ForegroundColor Yellow
Write-Host "  ✓ Reintentos inteligentes (3 intentos con backoff)" -ForegroundColor White
Write-Host "  ✓ Circuit Breaker (fallbacks pedagógicos)" -ForegroundColor White
Write-Host "  Modelo llama3.2:3b configurado (si descargado)" -ForegroundColor White
Write-Host "  Keep-Alive permanente (sin latencia inicial)" -ForegroundColor White
Write-Host ""
Write-Host "Para verificar logs completos:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f api" -ForegroundColor White
Write-Host ""
Write-Host "Para descargar modelo (si falta):" -ForegroundColor Yellow
Write-Host '  docker exec ai-native-ollama ollama pull llama3.2:3b' -ForegroundColor White
Write-Host ""
