# Script para reconstruir Docker con el nuevo Entrenador Digital

Write-Host "Reconstruyendo Docker - Entrenador Digital" -ForegroundColor Yellow

Write-Host "`nPaso 1: Detener contenedores..." -ForegroundColor Yellow
docker-compose down

Write-Host "`nPaso 2: Reconstruir backend..." -ForegroundColor Yellow
docker-compose build --no-cache api

Write-Host "`nPaso 3: Iniciar servicios..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "`nEsperando servicios..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "`nEstado:" -ForegroundColor Cyan
docker-compose ps

Write-Host "`nVerificando endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/training/materias" -Method Get -ErrorAction Stop
    Write-Host "Endpoint OK!" -ForegroundColor Green
    Write-Host "Materias: $($response.Count)" -ForegroundColor Green
}
catch {
    Write-Host "Error conectando" -ForegroundColor Red
    Write-Host "Ver logs: docker-compose logs -f api" -ForegroundColor Yellow
}

Write-Host "`nListo!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173/training" -ForegroundColor Cyan
