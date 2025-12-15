# Test Rápido del Sistema AI-Native MVP
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI-Native MVP - Test Rápido" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000/api/v1"

# 1. Health Check
Write-Host "[1/5] Health Check..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "$baseUrl/health"
Write-Host "   Status: $($health.status)" -ForegroundColor Green
Write-Host ""

# 2. Crear Sesión
Write-Host "[2/5] Creando sesión..." -ForegroundColor Yellow
$sessionBody = @{
    student_id = "test_" + (Get-Date -Format "HHmmss")
    activity_id = "test_activity"
    mode = "TUTOR"
} | ConvertTo-Json

$session = Invoke-RestMethod -Uri "$baseUrl/sessions" -Method Post -Body $sessionBody -ContentType "application/json"
$sessionId = $session.data.id
Write-Host "   Session ID: $sessionId" -ForegroundColor Green
Write-Host ""

# 3. Interacción con Tutor
Write-Host "[3/5] Interacción con Tutor..." -ForegroundColor Yellow
$interactionBody = @{
    session_id = $sessionId
    student_id = $session.data.student_id
    prompt = "Como implementar una cola circular?"
} | ConvertTo-Json

$interaction = Invoke-RestMethod -Uri "$baseUrl/interactions" -Method Post -Body $interactionBody -ContentType "application/json"
$responsePreview = $interaction.data.response.Substring(0, [Math]::Min(80, $interaction.data.response.Length))
Write-Host "   Response: $responsePreview..." -ForegroundColor Green
Write-Host ""

# 4. Test Delegación
Write-Host "[4/5] Probando delegación total..." -ForegroundColor Yellow
$delegationBody = @{
    session_id = $sessionId
    student_id = $session.data.student_id
    prompt = "Dame todo el codigo completo"
} | ConvertTo-Json

$delegation = Invoke-RestMethod -Uri "$baseUrl/interactions" -Method Post -Body $delegationBody -ContentType "application/json"
Write-Host "   Delegacion detectada: $($delegation.data.delegation_detected)" -ForegroundColor Green
Write-Host ""

# 5. Consultar Trazas
Write-Host "[5/5] Consultando trazas..." -ForegroundColor Yellow
try {
    $traces = Invoke-RestMethod -Uri "$baseUrl/traces/$sessionId"
    $traceCount = @($traces.data).Count
    Write-Host "   Trazas registradas: $traceCount" -ForegroundColor Green
} catch {
    Write-Host "   No se pudieron consultar trazas (esperado en modo de prueba)" -ForegroundColor Yellow
}
Write-Host ""

# Resumen
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTS COMPLETADOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Session ID: $sessionId" -ForegroundColor Gray
Write-Host "Frontend: http://localhost:3001" -ForegroundColor Gray
Write-Host ""
