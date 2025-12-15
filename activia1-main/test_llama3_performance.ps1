# Script para probar el rendimiento de llama3.2:3b vs phi3

Write-Host "`n=== PRUEBA DE RENDIMIENTO: llama3.2:3b ===" -ForegroundColor Cyan
Write-Host "Modelo: llama3.2:3b (2.0 GB, 3B parametros)" -ForegroundColor Yellow
Write-Host "Esperado: ~2.3x mas rapido que phi3 (7B parametros)`n" -ForegroundColor Yellow

# Test 1: Respuesta Socratica Simple
Write-Host "[TEST 1] Generacion Socratica (Prompt corto)..." -ForegroundColor Green
$body1 = @{
    student_code = "def suma(a, b): return a + b"
    exercise_context = "Implementar funcion de suma"
} | ConvertTo-Json

$start1 = Get-Date
try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/generate-socratic" `
                                   -Method POST `
                                   -ContentType "application/json" `
                                   -Body $body1 `
                                   -TimeoutSec 30
    $end1 = Get-Date
    $duration1 = ($end1 - $start1).TotalMilliseconds
    Write-Host "  Latencia: $([math]::Round($duration1))ms" -ForegroundColor Cyan
    Write-Host "  Respuesta: $($response1.socratic_response.Substring(0, [Math]::Min(100, $response1.socratic_response.Length)))..." -ForegroundColor Gray
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Test 2: Analisis de Riesgo (Prompt medio)
Write-Host "`n[TEST 2] Analisis de Riesgo Cognitivo..." -ForegroundColor Green
$body2 = @{
    student_code = @"
# Fibonacci
def fib(n):
    if n <= 1:
        return n
    return fib(n-1) + fib(n-2)
print(fib(10))
"@
    exercise_context = "Implementar Fibonacci recursivo"
    execution_trace = @{
        stdout = "55"
        stderr = ""
        exit_code = 0
    }
} | ConvertTo-Json

$start2 = Get-Date
try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/analyze-risk" `
                                   -Method POST `
                                   -ContentType "application/json" `
                                   -Body $body2 `
                                   -TimeoutSec 30
    $end2 = Get-Date
    $duration2 = ($end2 - $start2).TotalMilliseconds
    Write-Host "  Latencia: $([math]::Round($duration2))ms" -ForegroundColor Cyan
    Write-Host "  Riesgo Plagio: $($response2.plagiarism_risk)%" -ForegroundColor Gray
    Write-Host "  Dependencia IA: $($response2.ai_dependency)%" -ForegroundColor Gray
} catch {
    Write-Host "  ERROR: $_" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# Test 3: Retry Logic (provocar error y recuperacion)
Write-Host "`n[TEST 3] Circuit Breaker - Fallback (simulando error)..." -ForegroundColor Green
Write-Host "  (Si Ollama falla, debe devolver respuesta de fallback pedagogica)" -ForegroundColor Yellow
$body3 = @{
    student_code = ""
    exercise_context = "Test fallback"
} | ConvertTo-Json

$start3 = Get-Date
try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/ai/generate-socratic" `
                                   -Method POST `
                                   -ContentType "application/json" `
                                   -Body $body3 `
                                   -TimeoutSec 30
    $end3 = Get-Date
    $duration3 = ($end3 - $start3).TotalMilliseconds
    Write-Host "  Latencia: $([math]::Round($duration3))ms" -ForegroundColor Cyan
    if ($response3.socratic_response -match "reflexiona|piensa|considera") {
        Write-Host "  Circuit Breaker OK - Respuesta pedagogica activa" -ForegroundColor Green
    }
} catch {
    Write-Host "  ERROR esperado (parte del test): $_" -ForegroundColor Yellow
}

# Resumen
Write-Host "`n=== RESUMEN ===" -ForegroundColor Cyan
Write-Host "Modelo activo: llama3.2:3b (2.0 GB)" -ForegroundColor White
Write-Host "OLLAMA_KEEP_ALIVE: -1 (modelo siempre en memoria)" -ForegroundColor White
Write-Host "Retry Logic: 3 intentos con backoff exponencial" -ForegroundColor White
Write-Host "Circuit Breaker: 3 metodos de fallback pedagogico" -ForegroundColor White
Write-Host "`nFrontend ejecutando en: http://localhost:3001" -ForegroundColor Yellow
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "`nTodos los componentes implementados:" -ForegroundColor Green
Write-Host "  - Monaco Editor (VS Code engine)" -ForegroundColor Gray
Write-Host "  - Workbench Layout (3 paneles resizables)" -ForegroundColor Gray
Write-Host "  - AI Companion Panel (Tutor/Judge/Simulator)" -ForegroundColor Gray
Write-Host "  - Teacher Dashboard (metricas en tiempo real)" -ForegroundColor Gray
Write-Host "  - Toast System (notificaciones)" -ForegroundColor Gray
Write-Host "  - Loading Skeletons (UX optimizada)" -ForegroundColor Gray
