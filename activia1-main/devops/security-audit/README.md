# Security Audit - AI-Native MVP

**Autor**: Mag. Alberto Cortez
**Fecha**: 2025-11-24
**Versión**: 1.0

Este directorio contiene la infraestructura completa para realizar auditoría de seguridad del ecosistema AI-Native MVP.

---

## 📁 Estructura de Archivos

```
security-audit/
├── zap-scan-config.yaml     # Configuración OWASP ZAP Automation Framework
├── run-security-scan.sh     # Script interactivo para ejecutar scans
├── analyze-security.py      # Analizador de resultados (Python)
├── reports/                 # Reportes generados (HTML + JSON)
└── README.md                # Este archivo
```

---

## 🎯 Objetivos del Security Audit

1. **OWASP Top 10 Compliance**:
   - A01: Broken Access Control
   - A02: Cryptographic Failures
   - A03: Injection (SQL, XSS, etc.)
   - A04: Insecure Design
   - A05: Security Misconfiguration
   - A06: Vulnerable and Outdated Components
   - A07: Identification and Authentication Failures
   - A08: Software and Data Integrity Failures
   - A09: Security Logging and Monitoring Failures
   - A10: Server-Side Request Forgery (SSRF)

2. **Container Security**:
   - Vulnerabilities en imágenes Docker
   - Base images actualizadas
   - Dependencias sin CVEs críticos

3. **Kubernetes Security**:
   - Pod Security Standards
   - Network Policies
   - RBAC configurado correctamente
   - Secrets management

4. **Secrets Detection**:
   - No credentials en Git history
   - No API keys hardcoded
   - Secrets rotados regularmente

5. **Dependency Scanning**:
   - Python packages sin vulnerabilidades conocidas
   - Npm packages actualizados (frontend)

---

## 🚀 Quick Start

### Prerrequisitos

```bash
# Docker (para OWASP ZAP)
docker --version  # 20.0+

# Trivy (container scanning)
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# TruffleHog (secrets detection)
# macOS
brew install trufflehog

# Linux
wget https://github.com/trufflesecurity/trufflehog/releases/download/v3.63.0/trufflehog_3.63.0_linux_amd64.tar.gz
tar -xzf trufflehog_3.63.0_linux_amd64.tar.gz
sudo mv trufflehog /usr/local/bin/

# Safety (Python dependency scanning)
pip install safety

# Python 3.8+ (para análisis)
python --version
```

### Ejecución Rápida

```bash
# 1. Navegar al directorio
cd security-audit

# 2. Dar permisos de ejecución
chmod +x run-security-scan.sh
chmod +x analyze-security.py

# 3. Ejecutar scan interactivo
./run-security-scan.sh

# Opciones disponibles:
# 1) Full scan (OWASP ZAP + Trivy + Kubesec) - 45 min
# 2) Quick scan (OWASP ZAP baseline) - 5 min
# 3) Container scan (Trivy only) - 2 min
# 4) Kubernetes manifest scan (Kubesec) - 1 min
# 5) Secrets scan (TruffleHog) - 3 min
# 6) Custom OWASP ZAP scan
```

---

## 🔍 Tipos de Scans

### 1. Full Scan (Comprehensive)

**Duración**: ~45 minutos
**Herramientas**: OWASP ZAP + Trivy + Kubesec + TruffleHog + Safety

```bash
./run-security-scan.sh
# Opción 1
```

**Qué incluye**:
1. OWASP ZAP full scan (OWASP Top 10)
2. Trivy container vulnerability scan
3. Kubesec Kubernetes manifest security
4. TruffleHog secrets detection
5. Safety Python dependency check

**Uso**: Pre-producción, auditorías completas

### 2. Quick Scan (Baseline)

**Duración**: ~5 minutos
**Herramienta**: OWASP ZAP baseline

```bash
./run-security-scan.sh
# Opción 2
```

**Qué hace**:
- Passive scan de endpoints
- Detecta issues comunes rápidamente
- No invasivo (no active scanning)

**Uso**: CI/CD pipeline, smoke tests de seguridad

### 3. Container Scan

**Duración**: ~2 minutos
**Herramienta**: Trivy

```bash
./run-security-scan.sh
# Opción 3
```

**Qué hace**:
- Escanea imagen Docker por vulnerabilidades
- Detecta CVEs en dependencias
- Compara con databases (NVD, etc.)

**Severidades**: CRITICAL, HIGH, MEDIUM, LOW, UNKNOWN

### 4. Kubernetes Manifest Scan

**Duración**: ~1 minuto
**Herramienta**: Kubesec

```bash
./run-security-scan.sh
# Opción 4
```

**Qué valida**:
- Security contexts
- Pod Security Standards
- Capabilities
- Network policies
- Resource limits

**Score**: 0-10 (higher is better)

### 5. Secrets Scan

**Duración**: ~3 minutos
**Herramienta**: TruffleHog

```bash
./run-security-scan.sh
# Opción 5
```

**Qué detecta**:
- API keys (AWS, Azure, Google, etc.)
- Database credentials
- Private keys (RSA, SSH)
- JWT tokens
- OAuth tokens
- Generic secrets (regex patterns)

**⚠️ CRITICAL**: Si encuentra secrets, exit code 1

### 6. Custom OWASP ZAP Scan

**Duración**: Variable (según config)
**Herramienta**: OWASP ZAP Automation Framework

```bash
./run-security-scan.sh
# Opción 6
```

**Usa**: `zap-scan-config.yaml` (personalizable)

**Fases**:
1. Spider (discovery)
2. OpenAPI import (si disponible)
3. Passive scan
4. Active scan
5. Ajax spider
6. Report generation

---

## 📊 OWASP ZAP Configuration

El archivo `zap-scan-config.yaml` define el scan completo:

### Contexts

```yaml
contexts:
  - name: "ai-native-staging"
    urls:
      - "http://localhost:8000"
    includePaths:
      - "http://localhost:8000/api/v1/.*"
    excludePaths:
      - "http://localhost:8000/api/v1/health/ping"  # Exclude health checks
```

### Active Scan Rules (OWASP Top 10)

| Rule ID | Vulnerability | Strength | Threshold |
|---------|---------------|----------|-----------|
| 40018 | SQL Injection | HIGH | LOW |
| 40012 | XSS (Reflected) | HIGH | LOW |
| 40014 | XSS (Persistent) | HIGH | LOW |
| 6 | Path Traversal | HIGH | MEDIUM |
| 90020 | Remote OS Command Injection | HIGH | LOW |
| 40046 | SSRF | MEDIUM | MEDIUM |

**Strength**: INSANE, HIGH, MEDIUM, LOW
**Threshold**: OFF, LOW, MEDIUM, HIGH (lower = more alerts)

### Scan Phases

1. **Spider** (5 min): Descubre endpoints
2. **Passive Scan** (10 min): Analiza tráfico pasivamente
3. **Active Scan** (30 min): Intenta explotar vulnerabilidades
4. **Ajax Spider** (3 min): JavaScript-heavy pages
5. **Report Generation**: HTML, JSON, XML

---

## 🔬 Análisis de Resultados

### Analizador Automático (Python)

```bash
python analyze-security.py ./reports
```

**Output**:
1. **Executive Summary**: Total findings por severidad y herramienta
2. **Critical & High Findings**: Detalle de issues más graves
3. **OWASP Top 10 Mapping**: Clasificación por categoría
4. **Recommendations**: Acciones priorizadas de remediación
5. **Compliance Report**: Score de cumplimiento

### Ejemplo de Output

```
==============================================================
SECURITY AUDIT SUMMARY
==============================================================

Total Findings: 47

🔴 CRITICAL: 2
🟠 HIGH: 8
🟡 MEDIUM: 25
🟢 LOW: 10
🔵 INFORMATIONAL: 2

Findings by Tool:
  • OWASP ZAP: 35
  • Trivy: 8
  • Kubesec: 4
  • TruffleHog: 0

==============================================================
CRITICAL & HIGH SEVERITY FINDINGS
==============================================================

🔴 Finding #1: SQL Injection
   Tool: OWASP ZAP
   Severity: CRITICAL
   Description: SQL injection vulnerability detected in /api/v1/sessions endpoint...
   Solution: Use parameterized queries or ORM with proper escaping...

🟠 Finding #2: Outdated Python Package
   Tool: Trivy
   Severity: HIGH
   Description: CVE-2024-1234 in requests==2.28.0
   Fixed in: 2.31.0

==============================================================
OWASP TOP 10 2021 MAPPING
==============================================================

✓ A01:2021 – Broken Access Control: No issues
✗ A02:2021 – Cryptographic Failures: 1 finding(s)
✗ A03:2021 – Injection: 3 finding(s)
✓ A04:2021 – Insecure Design: No issues
✗ A05:2021 – Security Misconfiguration: 4 finding(s)
✗ A06:2021 – Vulnerable and Outdated Components: 8 finding(s)
✓ A07:2021 – Identification and Authentication Failures: No issues
✓ A08:2021 – Software and Data Integrity Failures: No issues
✓ A09:2021 – Security Logging and Monitoring Failures: No issues
✓ A10:2021 – Server-Side Request Forgery (SSRF): No issues

==============================================================
REMEDIATION RECOMMENDATIONS
==============================================================

🟠 High Severity Vulnerabilities (8 finding(s))
   Priority: HIGH
   Actions:
      • Update vulnerable dependencies to patched versions
      • Implement input validation and sanitization
      • Review and fix security misconfigurations
      • Enable security headers (CSP, HSTS, X-Frame-Options)

🟡 Kubernetes Security (4 finding(s))
   Priority: MEDIUM
   Actions:
      • Add security contexts to all pods (runAsNonRoot: true)
      • Implement network policies for pod isolation
      • Enable Pod Security Standards (restricted)
      • Use read-only root filesystems where possible

==============================================================
COMPLIANCE STATUS
==============================================================

Compliance Score: 4/5 (80%)

✅ PASS No critical vulnerabilities
✅ PASS No high-severity vulnerabilities
✅ PASS No secrets in repository
❌ FAIL Kubernetes security best practices
✅ PASS No outdated dependencies

⚠️  Minor compliance issues found. Review recommendations.
```

---

## 🛡️ Herramientas de Seguridad

### 1. OWASP ZAP (Zed Attack Proxy)

**Propósito**: Web application security scanner

**Capacidades**:
- Active/Passive scanning
- Automated/Manual penetration testing
- OWASP Top 10 coverage
- API testing (REST, GraphQL)

**Instalación**:
```bash
# Docker (recomendado)
docker pull softwaresecurityproject/zap-stable

# O standalone
# Download from: https://www.zaproxy.org/download/
```

**Uso en CI/CD**:
```yaml
# GitHub Actions example
- name: OWASP ZAP Scan
  uses: zaproxy/action-full-scan@v0.7.0
  with:
    target: 'https://api-staging.example.com'
```

### 2. Trivy

**Propósito**: Container vulnerability scanner

**Capacidades**:
- OS packages (Alpine, RHEL, etc.)
- Application dependencies (Python, Node, Go, etc.)
- CVE database (NVD, Red Hat, etc.)
- SBOM (Software Bill of Materials)

**Instalación**:
```bash
# Linux
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# macOS
brew install trivy

# Windows
# Download from: https://github.com/aquasecurity/trivy/releases
```

**Uso**:
```bash
# Scan image
trivy image python:3.11-slim

# Scan with severity filter
trivy image --severity HIGH,CRITICAL ai-native-backend:latest

# Generate report
trivy image --format json --output trivy-report.json ai-native-backend:latest
```

### 3. Kubesec

**Propósito**: Kubernetes manifest security scanner

**Capacidades**:
- Security context validation
- Pod Security Standards
- Best practices scoring
- Critical issue detection

**Instalación**:
```bash
# Online API (no installation)
curl -sSX POST --data-binary @pod.yaml https://v2.kubesec.io/scan

# Standalone binary
wget https://github.com/controlplaneio/kubesec/releases/download/v2.13.0/kubesec_linux_amd64.tar.gz
tar -xzf kubesec_linux_amd64.tar.gz
sudo mv kubesec /usr/local/bin/
```

**Uso**:
```bash
# Scan manifest
kubesec scan pod.yaml

# Scan all manifests
kubesec scan *.yaml > kubesec-report.json
```

### 4. TruffleHog

**Propósito**: Secrets detection in Git history

**Capacidades**:
- 700+ secret patterns
- Git history scanning
- Entropy detection
- Custom regex patterns

**Instalación**:
```bash
# macOS
brew install trufflehog

# Linux
wget https://github.com/trufflesecurity/trufflehog/releases/download/v3.63.0/trufflehog_3.63.0_linux_amd64.tar.gz
tar -xzf trufflehog_3.63.0_linux_amd64.tar.gz
sudo mv trufflehog /usr/local/bin/

# Go
go install github.com/trufflesecurity/trufflehog/v3@latest
```

**Uso**:
```bash
# Scan Git repo
trufflehog git file:///path/to/repo

# Scan with JSON output
trufflehog git file:///path/to/repo --json > secrets.json

# Scan GitHub repo
trufflehog github --org=myorg --repo=myrepo
```

### 5. Safety

**Propósito**: Python dependency vulnerability scanner

**Instalación**:
```bash
pip install safety
```

**Uso**:
```bash
# Scan requirements.txt
safety check -r requirements.txt

# Scan with JSON output
safety check --json > safety-report.json

# Check specific packages
safety check --stdin < requirements.txt
```

---

## 🔧 Remediación de Vulnerabilidades

### SQL Injection

**Detección**: OWASP ZAP rule 40018

**Remediación**:
```python
# ❌ BAD: String concatenation
query = f"SELECT * FROM users WHERE username = '{username}'"

# ✅ GOOD: SQLAlchemy ORM
users = session.query(User).filter(User.username == username).all()

# ✅ GOOD: Parameterized query
query = text("SELECT * FROM users WHERE username = :username")
result = session.execute(query, {"username": username})
```

### XSS (Cross-Site Scripting)

**Detección**: OWASP ZAP rules 40012, 40014

**Remediación**:
```python
# Backend: Validate and sanitize
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    content: str

    @validator('content')
    def sanitize_content(cls, v):
        # Remove HTML tags
        return re.sub(r'<[^>]+>', '', v)

# Frontend: Use framework escaping (React auto-escapes)
<div>{userInput}</div>  {/* React escapes automatically */}
```

### Vulnerable Dependencies

**Detección**: Trivy CVE scan

**Remediación**:
```bash
# Update specific package
pip install --upgrade requests==2.31.0

# Update all packages
pip install --upgrade -r requirements.txt

# Use Dependabot (GitHub)
# Create .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Secrets in Git

**Detección**: TruffleHog

**Remediación**:
```bash
# 1. Remove from history (DANGER: rewrites history)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret/file" \
  --prune-empty --tag-name-filter cat -- --all

# 2. Rotate compromised credentials
# - Change passwords
# - Regenerate API keys
# - Revoke tokens

# 3. Use secrets management
# - HashiCorp Vault
# - AWS Secrets Manager
# - Kubernetes Secrets

# 4. Prevent future commits
# Install pre-commit hook
pip install pre-commit
pre-commit install
```

### Kubernetes Security

**Detección**: Kubesec score < 5

**Remediación**:
```yaml
# Add security context
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
  readOnlyRootFilesystem: true

# Add resource limits
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

---

## 🎯 Security Checklist

### Pre-Deployment

- [ ] No critical vulnerabilities in container images
- [ ] No secrets in Git history
- [ ] All dependencies up-to-date
- [ ] OWASP ZAP scan passed (no HIGH alerts)
- [ ] Kubernetes manifests scored > 5 (Kubesec)
- [ ] Security headers configured (CSP, HSTS, etc.)
- [ ] Rate limiting enabled
- [ ] Authentication implemented (JWT)
- [ ] Input validation on all endpoints
- [ ] Error messages don't leak sensitive info

### Post-Deployment

- [ ] Monitor security logs
- [ ] Regular vulnerability scans (weekly)
- [ ] Incident response plan documented
- [ ] Security patches applied within 7 days
- [ ] Penetration test conducted (annually)

---

## 📚 Referencias

- **OWASP Top 10 2021**: https://owasp.org/Top10/
- **OWASP ZAP**: https://www.zaproxy.org/
- **Trivy**: https://aquasecurity.github.io/trivy/
- **Kubesec**: https://kubesec.io/
- **TruffleHog**: https://github.com/trufflesecurity/trufflehog
- **CWE Top 25**: https://cwe.mitre.org/top25/
- **NIST Cybersecurity Framework**: https://www.nist.gov/cyberframework

---

## 🔄 Integración CI/CD

### GitHub Actions Example

```yaml
name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'ai-native-backend:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run OWASP ZAP Baseline
        uses: zaproxy/action-baseline@v0.7.0
        with:
          target: 'https://api-staging.example.com'
          fail_action: true

      - name: Run TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
```

---

**Próximo Paso**: Paso 4 - User Acceptance Testing

---

**Autor**: Mag. Alberto Cortez
**Fecha**: 2025-11-24
**Versión**: 1.0