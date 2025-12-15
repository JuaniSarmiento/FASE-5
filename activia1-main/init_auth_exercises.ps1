# Script para inicializar el sistema completo de autenticación y ejercicios
# Ejecuta: .\init_auth_exercises.ps1

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Inicializando Sistema de Auth + Ejercicios" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que backend está en funcionamiento
Write-Host "[1/4] Verificando dependencias..." -ForegroundColor Yellow
try {
    python -c "import sqlalchemy; import fastapi; import passlib; import jwt; print('✓ Dependencias OK')"
} catch {
    Write-Host "❌ Error: Faltan dependencias. Instalando..." -ForegroundColor Red
    pip install -r requirements.txt
}

# 2. Crear tablas de base de datos
Write-Host ""
Write-Host "[2/4] Creando tablas en la base de datos..." -ForegroundColor Yellow
python -m backend.scripts.init_db

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error creando tablas" -ForegroundColor Red
    exit 1
}

# 3. Poblar ejercicios
Write-Host ""
Write-Host "[3/4] Poblando ejercicios de Python..." -ForegroundColor Yellow
python -m backend.scripts.init_exercises

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error poblando ejercicios" -ForegroundColor Red
    exit 1
}

# 4. Verificar frontend
Write-Host ""
Write-Host "[4/4] Verificando frontend..." -ForegroundColor Yellow
Set-Location frontEnd
if (!(Test-Path "node_modules")) {
    Write-Host "Instalando dependencias de Node..." -ForegroundColor Yellow
    npm install
}
Set-Location ..

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "✓ Inicialización Completa" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Siguiente paso: Ejecuta los servidores" -ForegroundColor Cyan
Write-Host ""
Write-Host "Terminal 1 - Backend:" -ForegroundColor Yellow
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  python -m uvicorn api.main:app --reload" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 - Frontend:" -ForegroundColor Yellow
Write-Host "  cd frontEnd" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "Luego abre http://localhost:5173 y:" -ForegroundColor Cyan
Write-Host "  1. Regístrate con email/password" -ForegroundColor White
Write-Host "  2. Ve a 'Ejercicios de Código'" -ForegroundColor White
Write-Host "  3. Selecciona un ejercicio" -ForegroundColor White
Write-Host "  4. Escribe código Python" -ForegroundColor White
Write-Host "  5. Presiona 'Ejecutar y Evaluar'" -ForegroundColor White
Write-Host "  6. Ve resultados y evaluación de Ollama IA" -ForegroundColor White
Write-Host ""
