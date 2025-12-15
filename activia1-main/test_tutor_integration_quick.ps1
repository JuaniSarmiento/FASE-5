# Test rápido de integración Frontend-Backend Tutor V2.0
# Ejecutar: .\test_tutor_integration_quick.ps1

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "🧪 TEST RAPIDO TUTOR SOCRATICO V2.0" -ForegroundColor Cyan
Write-Host "============================================`n" -ForegroundColor Cyan

$BASE_URL = "http://localhost:8000"

# Test 1: Health check
Write-Host "📡 Test 1: Verificando backend..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get -ErrorAction Stop
    Write-Host "✅ Backend activo" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend no disponible en $BASE_URL" -ForegroundColor Red
    Write-Host "   Ejecuta: cd backend; python -m uvicorn api.main:app --reload" -ForegroundColor Yellow
    exit 1
}

# Test 2: Crear sesión de tutor
Write-Host "`n📝 Test 2: Creando sesión de tutor..." -ForegroundColor Yellow
try {
    $session = Invoke-RestMethod -Uri "$BASE_URL/sessions/create-tutor" -Method Post -ErrorAction Stop
    $sessionId = $session.session_id
    Write-Host "✅ Sesión creada: $sessionId" -ForegroundColor Green
    Write-Host "   Mensaje de bienvenida recibido (${($session.welcome_message.Length)} chars)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error creando sesión: $_" -ForegroundColor Red
    exit 1
}

# Test 3: Enviar mensaje (solicitar código - debe rechazar)
Write-Host "`n💬 Test 3: Enviando mensaje (solicitar código)..." -ForegroundColor Yellow
$requestBody = @{
    message = "Dame el código para ordenar un array en Python"
    student_profile = @{
        avg_ai_involvement = 0.5
        successful_autonomous_solutions = 2
        error_self_correction_rate = 0.3
    }
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/sessions/$sessionId/interact" `
        -Method Post `
        -Body $requestBody `
        -ContentType "application/json" `
        -ErrorAction Stop
    
    Write-Host "✅ Respuesta recibida" -ForegroundColor Green
    Write-Host "   Tipo de intervención: $($response.metadata.intervention_type)" -ForegroundColor Gray
    Write-Host "   Semáforo: $($response.metadata.semaforo)" -ForegroundColor Gray
    Write-Host "   Nivel de ayuda: $($response.metadata.help_level)" -ForegroundColor Gray
    
    # Validar que rechazó código
    if ($response.metadata.intervention_type -in @("rechazo_pedagogico", "pregunta_socratica")) {
        Write-Host "   ✅ Rechazó código correctamente" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Se esperaba rechazo pedagógico" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Error en interacción: $_" -ForegroundColor Red
    exit 1
}

# Test 4: Obtener analytics
Write-Host "`n📊 Test 4: Obteniendo analytics..." -ForegroundColor Yellow
try {
    $analytics = Invoke-RestMethod -Uri "$BASE_URL/sessions/$sessionId/analytics-n4" `
        -Method Get `
        -ErrorAction Stop
    
    Write-Host "✅ Analytics obtenidos" -ForegroundColor Green
    Write-Host "   Total mensajes: $($analytics.total_messages)" -ForegroundColor Gray
    Write-Host "   Semáforos - Verde: $($analytics.semaforo_distribution.verde), Amarillo: $($analytics.semaforo_distribution.amarillo), Rojo: $($analytics.semaforo_distribution.rojo)" -ForegroundColor Gray
    
} catch {
    Write-Host "❌ Error obteniendo analytics: $_" -ForegroundColor Red
    Write-Host "   (Esto es normal si el tutor aún no implementa get_session_analytics_n4)" -ForegroundColor Yellow
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "✅ TESTS COMPLETADOS" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan

Write-Host "`n💡 Próximo paso:" -ForegroundColor Yellow
Write-Host "   1. Abrir frontend: cd frontEnd; npm run dev" -ForegroundColor White
Write-Host "   2. Navegar a: http://localhost:5173/tutor" -ForegroundColor White
Write-Host "   3. Probar interacción completa con UI`n" -ForegroundColor White
