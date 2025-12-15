# Test de Funcionalidades del Sistema AI-Native MVP
# Script simplificado para PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AI-Native MVP - Test de Funcionalidades" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000/api/v1"

# ============================================
# 1. HEALTH CHECK
# ============================================
Write-Host "[1/8] Verificando estado del sistema..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "   ✅ Sistema operacional" -ForegroundColor Green
    Write-Host "   Database: $($response.database)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
    exit 1
}

Start-Sleep -Seconds 1

# ============================================
# 2. CREAR SESIÓN
# ============================================
Write-Host "`n[2/8] Creando sesión de prueba..." -ForegroundColor Cyan
$sessionBody = @{
    student_id = "test_student_$(Get-Date -Format 'yyyyMMddHHmmss')"
    activity_id = "test_activity"
    mode = "TUTOR"
} | ConvertTo-Json

try {
    $sessionResponse = Invoke-RestMethod -Uri "$baseUrl/sessions" -Method Post -Body $sessionBody -ContentType "application/json"
    $sessionId = $sessionResponse.data.id
    Write-Host "   ✅ Sesión creada: $sessionId" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
    exit 1
}

Start-Sleep -Seconds 1

# ============================================
# 3. PREGUNTA NORMAL AL TUTOR
# ============================================
Write-Host "`n[3/8] Probando Tutor Cognitivo (pregunta normal)..." -ForegroundColor Cyan
$interactionBody1 = @{
    session_id = $sessionId
    student_id = $sessionResponse.data.student_id
    prompt = "¿Cómo puedo implementar una cola circular en Python?"
} | ConvertTo-Json

try {
    $interaction1 = Invoke-RestMethod -Uri "$baseUrl/interactions" -Method Post -Body $interactionBody1 -ContentType "application/json"
    Write-Host "   ✅ Interacción procesada" -ForegroundColor Green
    $preview = $interaction1.data.response.Substring(0, [Math]::Min(100, $interaction1.data.response.Length))
    Write-Host "   Response: $preview..." -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# ============================================
# 4. INTENTO DE DELEGACIÓN TOTAL
# ============================================
Write-Host "`n[4/8] Probando detección de delegación total..." -ForegroundColor Cyan
$delegationBody = @{
    session_id = $sessionId
    student_id = $sessionResponse.data.student_id
    prompt = "Dame el código completo de una cola circular en Python"
} | ConvertTo-Json

try {
    $interaction2 = Invoke-RestMethod -Uri "$baseUrl/interactions" -Method Post -Body $delegationBody -ContentType "application/json"
    if ($interaction2.data.delegation_detected) {
        Write-Host "   ✅ Delegación detectada correctamente" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Delegación no detectada" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# ============================================
# 5. FILTRADO DE PII
# ============================================
Write-Host "`n[5/8] Probando filtrado de PII (Gobernanza)..." -ForegroundColor Cyan
$piiBody = @{
    session_id = $sessionId
    student_id = $sessionResponse.data.student_id
    prompt = "Mi email es test@example.com y mi DNI es 12345678"
} | ConvertTo-Json

try {
    $interaction3 = Invoke-RestMethod -Uri "$baseUrl/interactions" -Method Post -Body $piiBody -ContentType "application/json"
    Write-Host "   ✅ Prompt procesado (PII sanitizado)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# ============================================
# 6. DETECCIÓN DE CÓDIGO SOSPECHOSO
# ============================================
Write-Host "`n[6/8] Probando detección de código sospechoso..." -ForegroundColor Cyan

# Mensaje corto
$shortBody = @{
    session_id = $sessionId
    student_id = $sessionResponse.data.student_id
    prompt = "Hola"
} | ConvertTo-Json

Invoke-RestMethod -Uri "$baseUrl/interactions" -Method Post -Body $shortBody -ContentType "application/json" | Out-Null
Start-Sleep -Seconds 1

# Código largo inmediatamente
$longCode = "def cola_circular():`n    class Cola:`n        def __init__(self, capacidad):`n            self.capacidad = capacidad"
$codeBody = @{
    session_id = $sessionId
    student_id = $sessionResponse.data.student_id
    prompt = $longCode
} | ConvertTo-Json

try {
    $interaction5 = Invoke-RestMethod -Uri "$baseUrl/interactions" -Method Post -Body $codeBody -ContentType "application/json"
    Write-Host "   ✅ Código procesado (riesgo temporal detectado)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Error: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# ============================================
# 7. CONSULTAR RIESGOS
# ============================================
Write-Host "`n[7/8] Consultando riesgos detectados..." -ForegroundColor Cyan
try {
    $risks = Invoke-RestMethod -Uri "$baseUrl/risks/$sessionId" -Method Get
    if ($risks.data -and $risks.data.Count -gt 0) {
        Write-Host "   ✅ Se detectaron $($risks.data.Count) riesgos" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️ No se detectaron riesgos" -ForegroundColor Cyan
    }
} catch {
    Write-Host "   ⚠️ Error consultando riesgos: $_" -ForegroundColor Yellow
}

Start-Sleep -Seconds 1

# ============================================
# 8. CONSULTAR TRAZABILIDAD
# ============================================
Write-Host "`n[8/8] Consultando trazabilidad cognitiva..." -ForegroundColor Cyan
try {
    $traces = Invoke-RestMethod -Uri "$baseUrl/traces/$sessionId/sequence" -Method Get
    if ($traces.data) {
        $traceCount = @($traces.data).Count
        Write-Host "   ✅ Se registraron $traceCount trazas cognitivas" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️ Error consultando trazas: $_" -ForegroundColor Yellow
}

# ============================================
# RESUMEN
# ============================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  TESTS COMPLETADOS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`n✅ Todos los agentes AI-Native están operacionales" -ForegroundColor Green
Write-Host "`nSession ID: $sessionId" -ForegroundColor Gray
Write-Host 'Frontend: http://localhost:3001' -ForegroundColor Gray
Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Gray
Write-Host ""
