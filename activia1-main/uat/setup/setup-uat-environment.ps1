# ============================================================================
# Setup UAT Environment - AI-Native MVP (PowerShell Version)
# ============================================================================
#
# This script prepares the complete UAT environment on Windows:
# 1. Create test users (5 students + 1 instructor)
# 2. Create test activity (TP1 - Colas Circulares)
# 3. Configure bug reporting system
# 4. Setup monitoring and logging
# 5. Generate credentials file
#
# Usage:
#   .\setup-uat-environment.ps1 [-Environment staging|local]
#
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("staging", "local")]
    [string]$Environment = "local"
)

# Error handling
$ErrorActionPreference = "Stop"

# Colors
function Write-Success { param($Message) Write-Host "✓ $Message" -ForegroundColor Green }
function Write-Info { param($Message) Write-Host "ℹ $Message" -ForegroundColor Blue }
function Write-Warning { param($Message) Write-Host "⚠ $Message" -ForegroundColor Yellow }
function Write-Error { param($Message) Write-Host "✗ $Message" -ForegroundColor Red }

Write-Info "============================================================================"
Write-Info "UAT ENVIRONMENT SETUP - AI-Native MVP"
Write-Info "============================================================================"

Write-Warning "`nEnvironment: $Environment`n"

# ============================================================================
# 1. Verify Prerequisites
# ============================================================================

Write-Info "[1/6] Verifying prerequisites..."

# Check Python
try {
    $pythonVersion = & python --version 2>&1
    Write-Success "Python found: $pythonVersion"
} catch {
    Write-Error "Python 3 is not installed or not in PATH"
    exit 1
}

# Check virtual environment
if (-Not (Test-Path ".venv")) {
    Write-Warning "Virtual environment not found - creating..."
    & python -m venv .venv
}
Write-Success "Virtual environment ready"

# Activate virtual environment
& .venv\Scripts\Activate.ps1
Write-Success "Virtual environment activated"

# Check database configuration
if ($Environment -eq "staging") {
    if (-Not $env:DATABASE_URL) {
        Write-Warning "DATABASE_URL not set - using default staging DB"
        $env:DATABASE_URL = "postgresql://ai_native:password@localhost:5432/ai_native_staging"
    }
    Write-Success "Using PostgreSQL: $env:DATABASE_URL"
} else {
    Write-Success "Using SQLite: ai_native.db"
}

# ============================================================================
# 2. Initialize Database
# ============================================================================

Write-Info "`n[2/6] Initializing database..."

if ($Environment -eq "staging") {
    & python scripts/init_database.py --database-url $env:DATABASE_URL
} else {
    & python scripts/init_database.py
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Database initialization failed"
    exit 1
}

Write-Success "Database initialized"

# ============================================================================
# 3. Create Test Users
# ============================================================================

Write-Info "`n[3/6] Creating test users..."

$credentialsPath = "user-acceptance-testing\setup\credentials\uat-credentials.md"

if ($Environment -eq "staging") {
    & python user-acceptance-testing\setup\create-test-users.py `
        --database-url $env:DATABASE_URL `
        --output $credentialsPath
} else {
    & python user-acceptance-testing\setup\create-test-users.py `
        --output $credentialsPath
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "User creation failed"
    exit 1
}

Write-Success "Test users created (5 students + 1 instructor)"

# ============================================================================
# 4. Create Test Activity
# ============================================================================

Write-Info "`n[4/6] Creating test activity..."

if ($Environment -eq "staging") {
    & python user-acceptance-testing\setup\create-test-activity.py `
        --database-url $env:DATABASE_URL
} else {
    & python user-acceptance-testing\setup\create-test-activity.py
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Activity creation failed"
    exit 1
}

Write-Success "Test activity created (TP1 - Colas Circulares)"

# ============================================================================
# 5. Configure Bug Reporting System
# ============================================================================

Write-Info "`n[5/6] Configuring bug reporting system..."

# Create bugs directory
New-Item -ItemType Directory -Force -Path "user-acceptance-testing\bugs" | Out-Null

# Create bug tracking file
$bugTracker = @{
    bugs = @()
    metadata = @{
        created_at = (Get-Date -Format o)
        total_bugs = 0
        critical = 0
        high = 0
        medium = 0
        low = 0
    }
} | ConvertTo-Json -Depth 10

$bugTracker | Out-File -FilePath "user-acceptance-testing\bugs\bug-tracker.json" -Encoding utf8

Write-Success "Bug tracking system configured"

# ============================================================================
# 6. Setup Monitoring and Logging
# ============================================================================

Write-Info "`n[6/6] Setting up monitoring and logging..."

# Create logs directory
New-Item -ItemType Directory -Force -Path "logs\uat" | Out-Null

# Create monitoring configuration
$monitoringConfig = @{
    log_level = "INFO"
    log_to_file = $true
    log_file = "logs/uat/uat-session.log"
    metrics = @{
        track_response_time = $true
        track_errors = $true
        track_user_actions = $true
    }
    alerts = @{
        critical_bugs = @{
            enabled = $true
            email = "instructor@uat.ai-native.edu"
        }
        high_errors = @{
            enabled = $true
            threshold = 10
            window_minutes = 5
        }
    }
} | ConvertTo-Json -Depth 10

$monitoringConfig | Out-File -FilePath "logs\uat\monitoring-config.json" -Encoding utf8

Write-Success "Monitoring and logging configured"

# ============================================================================
# Final Summary
# ============================================================================

Write-Info "`n============================================================================"
Write-Success "UAT ENVIRONMENT SETUP COMPLETE"
Write-Info "============================================================================"

Write-Warning "`n📊 Summary:"
Write-Host "   Environment: $Environment"
Write-Host "   Database: $(if ($Environment -eq 'staging') { 'PostgreSQL' } else { 'SQLite' })"
Write-Host "   Users created: 6 (5 students + 1 instructor)"
Write-Host "   Activities created: 1 (TP1 - Colas Circulares)"
Write-Host "   Bug tracking: Enabled"
Write-Host "   Monitoring: Enabled"

Write-Warning "`n📁 Generated Files:"
Write-Host "   Credentials: $credentialsPath"
Write-Host "   Bug tracker: user-acceptance-testing\bugs\bug-tracker.json"
Write-Host "   Monitoring config: logs\uat\monitoring-config.json"

Write-Warning "`n🚀 Next Steps:"
Write-Host "   1. Review credentials file (CONFIDENTIAL)"
Write-Host "   2. Send credentials to participants via SECURE channel"
Write-Host "   3. Start API server:"
if ($Environment -eq "staging") {
    Write-Info "      python scripts\run_api.py --production"
} else {
    Write-Info "      python scripts\run_api.py"
}
Write-Host "   4. Test login with one student account"
Write-Host "   5. Begin UAT execution (2 weeks)"

Write-Warning "`n📞 Support:"
Write-Host "   Email: instructor@uat.ai-native.edu"
Write-Host "   Slack: #uat-ai-native"
Write-Host "   Phone: [Contact number]"

Write-Info "`n============================================================================"

# Deactivate virtual environment
deactivate

exit 0