# 🔧 Guía del Administrador - Ecosistema AI-Native

## Manual de Instalación, Configuración y Mantenimiento Institucional

Esta guía te ayudará a instalar, configurar, desplegar y mantener el **Ecosistema AI-Native** en tu institución educativa, garantizando su correcto funcionamiento, seguridad, escalabilidad y cumplimiento de políticas institucionales.

---

## 📚 Índice

1. [Introducción para Administradores](#introducción-para-administradores)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación Paso a Paso](#instalación-paso-a-paso)
4. [Configuración Inicial](#configuración-inicial)
5. [Integración con LMS (Moodle)](#integración-con-lms-moodle)
6. [Gestión de Usuarios y Roles](#gestión-de-usuarios-y-roles)
7. [Configuración de LLM Providers](#configuración-de-llm-providers)
8. [Base de Datos y Respaldos](#base-de-datos-y-respaldos)
9. [Monitoreo y Observabilidad](#monitoreo-y-observabilidad)
10. [Seguridad y Privacidad](#seguridad-y-privacidad)
11. [Escalamiento y Performance](#escalamiento-y-performance)
12. [Deployment en Producción](#deployment-en-producción)
13. [Mantenimiento y Actualizaciones](#mantenimiento-y-actualizaciones)
14. [Troubleshooting](#troubleshooting)
15. [Cumplimiento y Gobernanza](#cumplimiento-y-gobernanza)
16. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Introducción para Administradores

### ¿Qué es el Ecosistema AI-Native?

El **Ecosistema AI-Native** es una plataforma educativa institucional que permite la enseñanza de programación en la era de la IA generativa, garantizando:

- ✅ **Trazabilidad N4**: Captura completa del proceso cognitivo del estudiante
- ✅ **Gobernanza institucional**: Cumplimiento de políticas académicas automatizado
- ✅ **Evaluación de procesos**: No solo productos, sino razonamiento y autonomía
- ✅ **Gestión de riesgos**: Detección automática de delegación excesiva, plagio, vulnerabilidades

### Tu Rol como Administrador

Como administrador institucional, sos responsable de:

1. **Instalación y configuración** del sistema
2. **Integración** con sistemas institucionales (Moodle, AD, Git)
3. **Gestión de usuarios** (docentes, estudiantes, permisos)
4. **Configuración de LLM providers** (OpenAI, Gemini, Claude)
5. **Monitoreo y observabilidad** (logs, métricas, alertas)
6. **Seguridad y privacidad** (datos sensibles, GDPR, auditorías)
7. **Escalamiento** (performance, alta disponibilidad)
8. **Cumplimiento normativo** (CONEAU, ISO/IEC 42001, políticas institucionales)

---

## Requisitos del Sistema

### Desarrollo (MVP - Hasta 50 estudiantes)

#### Servidor

- **CPU**: 2 cores (4 recomendado)
- **RAM**: 4 GB (8 GB recomendado)
- **Disco**: 20 GB SSD
- **OS**: Linux (Ubuntu 22.04 LTS recomendado), Windows 10/11, macOS

#### Software

- **Python**: 3.11+ (3.12 recomendado)
- **Node.js**: 18+ (para frontend)
- **Base de datos**: SQLite (incluida)
- **Git**: 2.40+

### Producción (50-500 estudiantes)

#### Servidor Backend

- **CPU**: 4 cores (8 recomendado)
- **RAM**: 16 GB (32 GB recomendado)
- **Disco**: 100 GB SSD
- **OS**: Linux Ubuntu 22.04 LTS (recomendado)

#### Base de Datos

- **PostgreSQL**: 15+ (separado del backend)
- **CPU**: 2 cores
- **RAM**: 8 GB
- **Disco**: 200 GB SSD (con crecimiento para trazas N4)

#### Frontend

- **Servidor web**: Nginx 1.24+
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disco**: 10 GB

#### Load Balancer (opcional, >200 estudiantes)

- **HAProxy** o **Nginx**
- **CPU**: 2 cores
- **RAM**: 4 GB

### Producción (500+ estudiantes - Enterprise)

#### Arquitectura de Microservicios

```
┌─────────────────────────────────────────┐
│        Load Balancer (HAProxy)          │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┴──────────┐
    ▼                     ▼
┌─────────┐         ┌─────────┐
│ Backend │         │ Backend │  (N instancias)
│ Server 1│         │ Server 2│
└────┬────┘         └────┬────┘
     │                   │
     └─────────┬─────────┘
               ▼
      ┌────────────────┐
      │   PostgreSQL   │  (Primary-Replica)
      │    Cluster     │
      └────────────────┘
               │
      ┌────────┴────────┐
      ▼                 ▼
  ┌──────┐        ┌──────┐
  │ Redis│        │ RabbitMQ│  (Cache & Queues)
  └──────┘        └──────┘
```

**Requerimientos**:
- **Backend**: 3+ instancias (8 cores, 32 GB RAM cada una)
- **PostgreSQL**: Primary + 2 replicas (8 cores, 64 GB RAM)
- **Redis**: 2 instancias (4 cores, 16 GB RAM)
- **RabbitMQ**: 3 nodos cluster (4 cores, 8 GB RAM)
- **Almacenamiento**: 1 TB SSD inicial

### Red y Conectividad

- **Ancho de banda**: 100 Mbps (1 Gbps para >500 estudiantes)
- **Latencia**: <50ms a LLM providers (OpenAI, Gemini)
- **Firewall**: Configurado (ver sección Seguridad)

### Software Adicional

- **Docker**: 24+ (para deployment con contenedores)
- **Kubernetes**: 1.28+ (para enterprise)
- **Nginx**: 1.24+ (proxy reverso)
- **Certbot**: Para SSL/TLS (Let's Encrypt)

---

## Instalación Paso a Paso

### Opción 1: Instalación Manual (Desarrollo)

#### 1. Clonar Repositorio

```bash
# Crear directorio de instalación
sudo mkdir -p /opt/ai-native-mvp
cd /opt/ai-native-mvp

# Clonar repositorio (reemplazar con tu repo)
git clone https://github.com/tu-institucion/ai-native-mvp.git .

# Verificar archivos
ls -la
# Deberías ver: src/, frontEnd/, scripts/, requirements.txt, README_MVP.md, etc.
```

#### 2. Crear Entorno Virtual Python

```bash
# Instalar virtualenv si no lo tenés
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip

# Crear venv
python3.12 -m venv .venv

# Activar
source .venv/bin/activate

# Verificar versión
python --version  # Debe ser Python 3.12.x
```

#### 3. Instalar Dependencias Backend

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar requirements
pip install -r requirements.txt

# Verificar instalación
pip list | grep -E "(fastapi|sqlalchemy|pydantic|openai)"
```

#### 4. Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar con tu editor favorito
nano .env
```

**Configuración mínima para desarrollo:**

```bash
# === DATABASE ===
DATABASE_URL=sqlite:///ai_native.db

# === LLM PROVIDER ===
LLM_PROVIDER=mock  # Sin costo para testing

# === API ===
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development

# === CORS ===
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# === LOGGING ===
LOG_LEVEL=INFO

# === SECURITY ===
SECRET_KEY=your-secret-key-here-change-in-production
```

**Generar SECRET_KEY seguro:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
# Copiar el resultado a SECRET_KEY en .env
```

#### 5. Inicializar Base de Datos

```bash
# Ejecutar script de inicialización
python scripts/init_database.py

# Deberías ver:
# ✓ Base de datos creada: ai_native.db
# ✓ Tablas creadas: 7
# ✓ Índices creados: 16
```

**Verificar base de datos:**

```bash
# Instalar sqlite3 si no lo tenés
sudo apt install sqlite3

# Abrir DB
sqlite3 ai_native.db

# Ver tablas
.tables
# Deberías ver: sessions, cognitive_traces, risks, evaluations, etc.

# Salir
.quit
```

#### 6. Verificar Backend

```bash
# Ejecutar ejemplo completo
python examples/ejemplo_basico.py

# Deberías ver:
# ========================================
# EJEMPLO COMPLETO - ECOSISTEMA AI-NATIVE
# ========================================
# [...]
# ✅ Example completed successfully
```

#### 7. Instalar Frontend (Opcional para desarrollo)

```bash
# Navegar a frontend
cd frontEnd

# Instalar Node.js 18+ si no lo tenés
# Ubuntu/Debian:
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar versión
node --version  # Debe ser v18.x o superior
npm --version

# Instalar dependencias
npm install

# Verificar instalación
ls node_modules/  # Debería tener muchos paquetes
```

#### 8. Iniciar Backend y Frontend

**Terminal 1 - Backend:**

```bash
cd /opt/ai-native-mvp
source .venv/bin/activate
python scripts/run_api.py

# Deberías ver:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
```

**Terminal 2 - Frontend:**

```bash
cd /opt/ai-native-mvp/frontEnd
npm run dev

# Deberías ver:
#   VITE v5.0.0  ready in 500 ms
#   ➜  Local:   http://localhost:3000/
#   ➜  Network: use --host to expose
```

#### 9. Verificar Instalación

**Abrir navegador:**

1. Backend API: http://localhost:8000/docs (Swagger UI)
2. Frontend: http://localhost:3000

**Health check:**

```bash
curl http://localhost:8000/api/v1/health | jq

# Respuesta esperada:
# {
#   "success": true,
#   "data": {
#     "status": "healthy",
#     "version": "0.1.0",
#     "database": "connected",
#     "agents_available": 6
#   }
# }
```

### Opción 2: Instalación con Docker (Recomendado para Producción)

#### 1. Instalar Docker y Docker Compose

```bash
# Ubuntu 22.04
sudo apt update
sudo apt install -y docker.io docker-compose

# Verificar instalación
docker --version
docker-compose --version

# Agregar tu usuario al grupo docker
sudo usermod -aG docker $USER

# Recargar grupos (o cerrar sesión y volver)
newgrp docker
```

#### 2. Crear Archivo docker-compose.yml

```yaml
version: '3.8'

services:
  # Backend API
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ai-native-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://ai_native:password@db:5432/ai_native
      - LLM_PROVIDER=openai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=production
      - SECRET_KEY=${SECRET_KEY}
    volumes:
      - ./logs:/app/logs
    depends_on:
      - db
      - redis
    networks:
      - ai-native-network

  # PostgreSQL Database
  db:
    image: postgres:15
    container_name: ai-native-db
    restart: unless-stopped
    environment:
      - POSTGRES_USER=ai_native
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=ai_native
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - ai-native-network

  # Redis (Cache)
  redis:
    image: redis:7-alpine
    container_name: ai-native-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - ai-native-network

  # Frontend (Nginx serving React build)
  frontend:
    build:
      context: ./frontEnd
      dockerfile: Dockerfile
    container_name: ai-native-frontend
    restart: unless-stopped
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - ai-native-network

volumes:
  postgres-data:
  redis-data:

networks:
  ai-native-network:
    driver: bridge
```

#### 3. Crear Dockerfile para Backend

```dockerfile
# Dockerfile (en la raíz del proyecto)
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY pytest.ini .
COPY .env.example .env

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando de inicio
CMD ["python", "scripts/run_api.py", "--host", "0.0.0.0", "--port", "8000"]
```

#### 4. Crear Dockerfile para Frontend

```dockerfile
# frontEnd/Dockerfile
FROM node:18-alpine AS build

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código
COPY . .

# Build para producción
RUN npm run build

# Stage 2: Nginx
FROM nginx:1.24-alpine

# Copiar build
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### 5. Configurar Nginx para Frontend

```nginx
# frontEnd/nginx.conf
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # React Router - todas las rutas van a index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 6. Iniciar con Docker Compose

```bash
# En la raíz del proyecto

# Build images
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Verificar estado
docker-compose ps

# Deberías ver:
# ai-native-backend    running   0.0.0.0:8000->8000/tcp
# ai-native-db         running   0.0.0.0:5432->5432/tcp
# ai-native-redis      running   0.0.0.0:6379->6379/tcp
# ai-native-frontend   running   0.0.0.0:3000->80/tcp
```

#### 7. Inicializar Base de Datos en Docker

```bash
# Ejecutar init_database dentro del contenedor
docker exec -it ai-native-backend python scripts/init_database.py

# O ejecutar manualmente SQL
docker exec -it ai-native-db psql -U ai_native -d ai_native -f /docker-entrypoint-initdb.d/init.sql
```

#### 8. Verificar Instalación Docker

```bash
# Health check backend
curl http://localhost:8000/api/v1/health | jq

# Abrir frontend
xdg-open http://localhost:3000  # Linux
# o visitar manualmente en navegador
```

---

## Configuración Inicial

### 1. Crear Usuario Administrador

```bash
# Método 1: Script interactivo
python scripts/create_admin_user.py

# Ingresa:
# Email: admin@tu-institucion.edu.ar
# Nombre: Administrador Sistema
# Contraseña: [tu contraseña segura]

# Método 2: SQL directo
sqlite3 ai_native.db <<EOF
INSERT INTO users (id, email, name, role, hashed_password, created_at)
VALUES (
    'admin_001',
    'admin@tu-institucion.edu.ar',
    'Administrador Sistema',
    'ADMIN',
    '\$2b\$12\$...', -- Hash de la contraseña (generar con bcrypt)
    datetime('now')
);
EOF
```

**Generar hash de contraseña:**

```python
# En Python interactivo
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("tu_contraseña_segura")
print(hashed)
```

### 2. Configurar Políticas Institucionales

Editar `src/ai_native_mvp/config/institutional_policies.json`:

```json
{
  "institution": {
    "name": "Universidad Tecnológica Nacional - FRM",
    "code": "UTN-FRM",
    "timezone": "America/Argentina/Buenos_Aires"
  },

  "ai_governance": {
    "default_max_help_level": "MEDIO",
    "block_complete_solutions": true,
    "require_justification": true,
    "allow_code_snippets": false,
    "min_traceability_level": "N4",

    "risk_thresholds": {
      "ai_dependency_warning": 0.6,
      "ai_dependency_critical": 0.8,
      "lack_justification_warning": 0.3,
      "lack_justification_critical": 0.5
    }
  },

  "academic_integrity": {
    "require_ai_disclosure": true,
    "allow_external_ai_tools": true,
    "require_external_ai_documentation": true,
    "plagiarism_detection_enabled": true
  },

  "data_retention": {
    "traces_retention_days": 730,
    "sessions_retention_days": 1095,
    "logs_retention_days": 90
  },

  "privacy": {
    "anonymize_exports": true,
    "allow_student_data_access": true,
    "gdpr_compliant": true
  }
}
```

### 3. Configurar Notificaciones

Editar `.env`:

```bash
# === EMAIL (para alertas a docentes) ===
SMTP_HOST=smtp.tu-institucion.edu.ar
SMTP_PORT=587
SMTP_USER=ai-native@tu-institucion.edu.ar
SMTP_PASSWORD=tu_password_smtp
SMTP_FROM=ai-native@tu-institucion.edu.ar
SMTP_TLS=true

# === SLACK (opcional - para alertas críticas) ===
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
SLACK_CHANNEL=#ai-native-alertas
```

### 4. Configurar Rate Limiting

```bash
# .env
RATE_LIMIT_PER_MINUTE=60      # Requests por minuto por IP
RATE_LIMIT_PER_HOUR=1000      # Requests por hora por IP
RATE_LIMIT_PER_DAY=10000      # Requests por día por IP
```

### 5. Configurar Cache LLM

```bash
# .env
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL=3600            # 1 hora
LLM_CACHE_MAX_ENTRIES=1000
LLM_CACHE_BACKEND=redis       # o 'memory' para desarrollo
REDIS_URL=redis://localhost:6379/0
```

---

## Integración con LMS (Moodle)

### Integración vía LTI 1.3 (Learning Tools Interoperability)

#### 1. Instalar Plugin LTI en el Backend

```bash
pip install lti
```

#### 2. Configurar LTI Provider en el Backend

Crear `src/ai_native_mvp/api/routers/lti.py`:

```python
from fastapi import APIRouter, Request, HTTPException
from pylti1p3.contrib.fastapi import FastAPILTI
from pylti1p3.tool_config import ToolConfJsonFile

router = APIRouter(prefix="/lti", tags=["LTI"])

# Configuración LTI
lti_config = ToolConfJsonFile('lti_config.json')
lti = FastAPILTI(lti_config)

@router.post("/login")
async def lti_login(request: Request):
    """LTI login initiation"""
    return lti.oidc_login(request)

@router.post("/launch")
async def lti_launch(request: Request):
    """LTI launch (after login)"""
    message = lti.launch(request)

    # Extraer datos del estudiante
    user_id = message.get_user_id()
    user_name = message.get_user_name()
    user_email = message.get_user_email()
    course_id = message.get_course_id()

    # Crear sesión en AI-Native
    # ... (lógica de creación de sesión)

    return {"message": "Launch successful", "user": user_name}

@router.get("/jwks")
async def lti_jwks():
    """Public keyset for LTI"""
    return lti.get_jwks()
```

#### 3. Configurar Moodle

**En Moodle como Administrador:**

1. **Administración del sitio** → **Extensiones** → **Actividad módulos** → **External tool** → **Manage tools**

2. **Configure a tool manually**:
   - Tool name: `AI-Native Ecosystem`
   - Tool URL: `https://tu-dominio.edu.ar/api/v1/lti/launch`
   - LTI version: `LTI 1.3`
   - Public key type: `Keyset URL`
   - Public keyset: `https://tu-dominio.edu.ar/api/v1/lti/jwks`
   - Initiate login URL: `https://tu-dominio.edu.ar/api/v1/lti/login`
   - Redirection URI: `https://tu-dominio.edu.ar/api/v1/lti/launch`

3. **Privacy settings**:
   - Share launcher's name: ✓
   - Share launcher's email: ✓
   - Accept grades from the tool: ✓

4. **Copiar credenciales**:
   - Client ID: `xxxxxxx`
   - Deployment ID: `xxxxxxx`

#### 4. Configurar lti_config.json en Backend

```json
{
  "https://moodle.tu-institucion.edu.ar": [{
    "client_id": "xxxxxxx",
    "auth_login_url": "https://moodle.tu-institucion.edu.ar/mod/lti/auth.php",
    "auth_token_url": "https://moodle.tu-institucion.edu.ar/mod/lti/token.php",
    "key_set_url": "https://moodle.tu-institucion.edu.ar/mod/lti/certs.php",
    "deployment_ids": ["xxxxxxx"],
    "private_key_file": "private.key",
    "public_key_file": "public.key"
  }]
}
```

#### 5. Generar Claves RSA

```bash
# Generar clave privada
openssl genrsa -out private.key 2048

# Generar clave pública
openssl rsa -in private.key -pubout -out public.key

# Mover a ubicación segura
sudo mkdir -p /etc/ai-native/keys
sudo mv private.key public.key /etc/ai-native/keys/
sudo chmod 600 /etc/ai-native/keys/private.key
```

#### 6. Agregar Actividad en Moodle

**En tu curso Moodle:**

1. Activar edición
2. Agregar actividad → **External tool**
3. Título: `Tutor Cognitivo AI-Native`
4. Preconfigured tool: `AI-Native Ecosystem`
5. Guardar y mostrar

**Resultado**: Al hacer clic, los estudiantes son redirigidos al sistema AI-Native con SSO automático.

### Integración vía API REST (Alternativa)

Si no usás LTI, podés integrar vía API:

**En Moodle (PHP):**

```php
<?php
// moodle/local/ainative/create_session.php

// Obtener usuario actual
$user = $USER;

// Llamar a API de AI-Native
$api_url = 'https://tu-dominio.edu.ar/api/v1/sessions';
$data = [
    'student_id' => $user->id,
    'student_email' => $user->email,
    'activity_id' => 'prog2_tp1_colas',
    'mode' => 'TUTOR'
];

$options = [
    'http' => [
        'header'  => "Content-Type: application/json\r\n" .
                     "Authorization: Bearer YOUR_API_KEY\r\n",
        'method'  => 'POST',
        'content' => json_encode($data)
    ]
];

$context  = stream_context_create($options);
$result = file_get_contents($api_url, false, $context);
$session = json_decode($result, true);

// Redirigir a frontend de AI-Native
$redirect_url = "https://tu-dominio.edu.ar/?session_id=" . $session['data']['id'];
redirect($redirect_url);
?>
```

---

## Gestión de Usuarios y Roles

### Modelo de Roles

El sistema tiene **4 roles**:

1. **STUDENT**: Estudiantes (interactúan con tutores)
2. **TEACHER**: Docentes (diseñan actividades, monitorean)
3. **ADMIN**: Administradores (configuración, usuarios, sistema)
4. **AUDITOR**: Auditores (solo lectura, para auditorías institucionales)

### Crear Usuarios Manualmente

```python
# scripts/create_users.py
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import UserRepository
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

with get_db_session() as db:
    user_repo = UserRepository(db)

    # Crear docente
    teacher = user_repo.create(
        email="profesor@tu-institucion.edu.ar",
        name="Juan Pérez",
        role="TEACHER",
        hashed_password=pwd_context.hash("password123"),
        department="Sistemas"
    )

    # Crear estudiante
    student = user_repo.create(
        email="estudiante@tu-institucion.edu.ar",
        name="María García",
        role="STUDENT",
        hashed_password=pwd_context.hash("password123"),
        student_id="12345"
    )
```

### Importar Usuarios desde CSV

```bash
# Preparar CSV (users.csv)
# email,name,role,student_id,department
# est001@inst.edu.ar,Juan Pérez,STUDENT,12345,
# est002@inst.edu.ar,María García,STUDENT,12346,
# prof001@inst.edu.ar,Carlos López,TEACHER,,Sistemas

# Ejecutar script de importación
python scripts/import_users.py users.csv
```

Script `scripts/import_users.py`:

```python
import csv
import sys
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import UserRepository
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def import_users(csv_path):
    with get_db_session() as db:
        user_repo = UserRepository(db)

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Generar contraseña temporal
                temp_password = secrets.token_urlsafe(12)

                user = user_repo.create(
                    email=row['email'],
                    name=row['name'],
                    role=row['role'],
                    hashed_password=pwd_context.hash(temp_password),
                    student_id=row.get('student_id') or None,
                    department=row.get('department') or None
                )

                print(f"✓ Usuario creado: {row['email']} (contraseña: {temp_password})")

                # TODO: Enviar email con contraseña temporal

if __name__ == "__main__":
    import_users(sys.argv[1])
```

### Sincronización con Active Directory (LDAP)

Para instituciones con AD/LDAP:

```bash
# Instalar dependencias
pip install python-ldap
```

Configurar `.env`:

```bash
LDAP_ENABLED=true
LDAP_SERVER=ldap://ad.tu-institucion.edu.ar
LDAP_BIND_DN=CN=ServiceAccount,OU=Services,DC=tu-institucion,DC=edu,DC=ar
LDAP_BIND_PASSWORD=password
LDAP_SEARCH_BASE=OU=Users,DC=tu-institucion,DC=edu,DC=ar
```

Script `scripts/sync_ldap.py`:

```python
import ldap
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.repositories import UserRepository

def sync_ldap():
    # Conectar a LDAP
    conn = ldap.initialize(os.getenv('LDAP_SERVER'))
    conn.simple_bind_s(os.getenv('LDAP_BIND_DN'), os.getenv('LDAP_BIND_PASSWORD'))

    # Buscar usuarios
    results = conn.search_s(
        os.getenv('LDAP_SEARCH_BASE'),
        ldap.SCOPE_SUBTREE,
        '(objectClass=person)'
    )

    with get_db_session() as db:
        user_repo = UserRepository(db)

        for dn, attrs in results:
            email = attrs.get('mail', [b''])[0].decode()
            name = attrs.get('displayName', [b''])[0].decode()

            # Verificar si ya existe
            existing = user_repo.get_by_email(email)
            if existing:
                continue

            # Crear usuario
            user_repo.create(
                email=email,
                name=name,
                role='STUDENT',  # Por defecto
                auth_method='LDAP'
            )

            print(f"✓ Sincronizado: {email}")

if __name__ == "__main__":
    sync_ldap()
```

Ejecutar sincronización:

```bash
# Manual
python scripts/sync_ldap.py

# Automática (cron - cada día a las 3am)
sudo crontab -e
# Agregar:
# 0 3 * * * /opt/ai-native-mvp/.venv/bin/python /opt/ai-native-mvp/scripts/sync_ldap.py >> /var/log/ai-native/ldap_sync.log 2>&1
```

---

## Configuración de LLM Providers

### Provider: Mock (Desarrollo - Gratis)

Configuración en `.env`:

```bash
LLM_PROVIDER=mock
```

**Características**:
- ✅ Sin costo
- ✅ Respuestas instantáneas
- ❌ No son respuestas reales de IA

**Uso**: Solo para desarrollo y testing.

### Provider: OpenAI (GPT-4, GPT-3.5)

#### 1. Obtener API Key

1. Ir a https://platform.openai.com/api-keys
2. Crear nueva clave API
3. Copiar clave (comienza con `sk-proj-...`)

#### 2. Configurar en .env

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4                # o gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=2000
OPENAI_ORGANIZATION=org-xxxxxx    # Opcional
```

#### 3. Configurar Límites de Uso

Para evitar gastos excesivos:

```bash
OPENAI_MAX_REQUESTS_PER_MINUTE=100
OPENAI_MAX_TOKENS_PER_DAY=1000000
```

#### 4. Monitorear Costos

```python
# scripts/monitor_openai_costs.py
import openai
from datetime import datetime, timedelta

openai.api_key = os.getenv('OPENAI_API_KEY')

# Obtener uso del último mes
usage = openai.Usage.retrieve(
    start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
    end_date=datetime.now().strftime('%Y-%m-%d')
)

print(f"Tokens usados: {usage['total_tokens']:,}")
print(f"Costo estimado: ${usage['total_tokens'] * 0.00003:.2f}")
```

**Cron job para alertas:**

```bash
# Cada día a las 9am
0 9 * * * /opt/ai-native-mvp/.venv/bin/python /opt/ai-native-mvp/scripts/monitor_openai_costs.py | mail -s "OpenAI Usage Report" admin@tu-institucion.edu.ar
```

### Provider: Google Gemini (GRATIS - 60 req/min)

#### 1. Obtener API Key

1. Ir a https://ai.google.dev/
2. Get API Key
3. Copiar clave

#### 2. Configurar en .env

```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
GEMINI_MODEL=gemini-1.5-flash     # Rápido y gratis
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=8192
```

**Modelos disponibles**:
- `gemini-1.5-flash`: Rápido, gratis (60 req/min)
- `gemini-1.5-pro`: Más capaz, gratis (2 req/min)

#### 3. Instalar Dependencias

```bash
pip install google-generativeai
```

**Características Gemini**:
- ✅ **GRATIS** (con límites generosos)
- ✅ 60 requests/min (Flash)
- ✅ Buen rendimiento
- ✅ Multimodal (texto + imágenes)

**Recomendado para**: Instituciones con presupuesto limitado.

### Provider: Anthropic Claude (Alternativa a OpenAI)

#### 1. Obtener API Key

1. Ir a https://console.anthropic.com/
2. Crear API key

#### 2. Configurar en .env

```bash
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-3-sonnet-20240229
ANTHROPIC_TEMPERATURE=0.7
ANTHROPIC_MAX_TOKENS=4096
```

**Modelos disponibles**:
- `claude-3-opus`: Más capaz (caro)
- `claude-3-sonnet`: Equilibrado (recomendado)
- `claude-3-haiku`: Rápido y económico

### Configuración Multi-Provider (Fallback)

Para alta disponibilidad, configurá múltiples providers:

```bash
# .env
LLM_PROVIDER=openai
LLM_FALLBACK_PROVIDERS=gemini,anthropic

OPENAI_API_KEY=sk-proj-xxx
GEMINI_API_KEY=AIzaSyxxx
ANTHROPIC_API_KEY=sk-ant-xxx
```

**Comportamiento**:
1. Intenta con OpenAI
2. Si falla (rate limit, error), intenta con Gemini
3. Si falla, intenta con Anthropic
4. Si todos fallan, devuelve error al usuario

---

## Base de Datos y Respaldos

### Migración de SQLite a PostgreSQL (Producción)

#### 1. Instalar PostgreSQL

```bash
# Ubuntu 22.04
sudo apt update
sudo apt install -y postgresql postgresql-contrib

# Verificar instalación
sudo systemctl status postgresql

# Conectar como usuario postgres
sudo -u postgres psql
```

#### 2. Crear Base de Datos y Usuario

```sql
-- En psql
CREATE USER ai_native WITH PASSWORD 'tu_password_seguro';
CREATE DATABASE ai_native OWNER ai_native;
GRANT ALL PRIVILEGES ON DATABASE ai_native TO ai_native;

-- Salir
\q
```

#### 3. Actualizar .env

```bash
# Cambiar de SQLite a PostgreSQL
DATABASE_URL=postgresql://ai_native:tu_password_seguro@localhost:5432/ai_native
```

#### 4. Migrar Datos de SQLite a PostgreSQL

```bash
# Instalar herramienta de migración
pip install pgloader

# Ejecutar migración
pgloader sqlite://ai_native.db postgresql://ai_native:tu_password_seguro@localhost:5432/ai_native

# Verificar tablas
psql -U ai_native -d ai_native -c "\dt"
```

#### 5. Recrear Índices (Importante para Performance)

```bash
python create_db_indexes.py
```

### Respaldos Automáticos (PostgreSQL)

#### Script de Backup

```bash
# /opt/ai-native-mvp/scripts/backup_database.sh

#!/bin/bash
set -e

BACKUP_DIR="/var/backups/ai-native"
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/ai_native_$DATE.sql.gz"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup con pg_dump (comprimido)
PGPASSWORD="tu_password_seguro" pg_dump -U ai_native -h localhost ai_native | gzip > $BACKUP_FILE

# Verificar tamaño
SIZE=$(du -h $BACKUP_FILE | cut -f1)
echo "✓ Backup creado: $BACKUP_FILE ($SIZE)"

# Eliminar backups mayores a 30 días
find $BACKUP_DIR -name "ai_native_*.sql.gz" -mtime +30 -delete

# Notificar
echo "Backup completado: $DATE" | mail -s "AI-Native DB Backup OK" admin@tu-institucion.edu.ar
```

Hacer ejecutable:

```bash
chmod +x /opt/ai-native-mvp/scripts/backup_database.sh
```

#### Automatizar con Cron

```bash
sudo crontab -e

# Backup cada día a las 2am
0 2 * * * /opt/ai-native-mvp/scripts/backup_database.sh >> /var/log/ai-native/backup.log 2>&1

# Backup cada hora (para alta frecuencia)
0 * * * * /opt/ai-native-mvp/scripts/backup_database.sh >> /var/log/ai-native/backup.log 2>&1
```

### Restaurar desde Backup

```bash
# Listar backups disponibles
ls -lh /var/backups/ai-native/

# Restaurar backup específico
gunzip < /var/backups/ai-native/ai_native_2025-11-19_02-00-00.sql.gz | psql -U ai_native -d ai_native
```

### Replicación Primary-Replica (Alta Disponibilidad)

Para >500 estudiantes, configurar replicación:

**Primary (escritura)**: `db-primary.tu-institucion.edu.ar`
**Replicas (lectura)**: `db-replica-1.tu-institucion.edu.ar`, `db-replica-2.tu-institucion.edu.ar`

Ver: https://www.postgresql.org/docs/15/high-availability.html

---

## Monitoreo y Observabilidad

### Logs Estructurados

El sistema genera logs en formato JSON estructurado:

```json
{
  "timestamp": "2025-11-19T10:30:45.123Z",
  "level": "INFO",
  "logger": "ai_native_mvp.api.routers.interactions",
  "message": "Processing interaction",
  "extra": {
    "session_id": "session_abc123",
    "student_id": "student_001",
    "activity_id": "prog2_tp1_colas",
    "request_id": "req_xyz789"
  }
}
```

**Ubicación de logs**:
- Desarrollo: `logs/ai-native-dev.log`
- Producción: `/var/log/ai-native/ai-native-prod.log`

### Configurar Log Rotation

```bash
# /etc/logrotate.d/ai-native

/var/log/ai-native/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 ai-native ai-native
    sharedscripts
    postrotate
        systemctl reload ai-native.service > /dev/null 2>&1 || true
    endscript
}
```

### Integración con ELK Stack (Elasticsearch, Logstash, Kibana)

#### 1. Instalar Filebeat

```bash
# Ubuntu 22.04
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
sudo apt-get install apt-transport-https
echo "deb https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee -a /etc/apt/sources.list.d/elastic-8.x.list
sudo apt-get update && sudo apt-get install filebeat
```

#### 2. Configurar Filebeat

```yaml
# /etc/filebeat/filebeat.yml

filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/ai-native/*.log
  json.keys_under_root: true
  json.add_error_key: true
  fields:
    service: ai-native-mvp
    environment: production

output.elasticsearch:
  hosts: ["elasticsearch.tu-institucion.edu.ar:9200"]
  username: "filebeat_user"
  password: "password"
  index: "ai-native-%{+yyyy.MM.dd}"

setup.kibana:
  host: "kibana.tu-institucion.edu.ar:5601"
```

#### 3. Iniciar Filebeat

```bash
sudo systemctl enable filebeat
sudo systemctl start filebeat
sudo systemctl status filebeat
```

#### 4. Crear Dashboards en Kibana

**Acceder a Kibana**: `http://kibana.tu-institucion.edu.ar:5601`

**Métricas clave a visualizar**:
- Requests por minuto
- Latencia promedio (p50, p95, p99)
- Errores (4xx, 5xx)
- Dependencia IA promedio por estudiante
- Riesgos detectados por tipo
- Tasa de bloqueos por delegación

### Métricas con Prometheus + Grafana

#### 1. Instrumentar Backend con Prometheus

```bash
pip install prometheus-fastapi-instrumentator
```

```python
# src/ai_native_mvp/api/main.py

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Instrumentar
Instrumentator().instrument(app).expose(app)
```

**Métricas expuestas en**: `http://localhost:8000/metrics`

#### 2. Configurar Prometheus

```yaml
# /etc/prometheus/prometheus.yml

global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-native-backend'
    static_configs:
      - targets: ['localhost:8000']
```

#### 3. Visualizar en Grafana

**Importar dashboard pre-configurado**: ID 14282 (FastAPI Dashboard)

**Métricas custom a agregar**:
- `ai_native_sessions_total`: Total de sesiones creadas
- `ai_native_interactions_total`: Total de interacciones procesadas
- `ai_native_risks_detected_total`: Total de riesgos detectados
- `ai_native_llm_requests_total`: Requests a LLM providers
- `ai_native_llm_cost_usd`: Costo estimado en USD

### Alertas (Slack, Email)

Configurar alertas para eventos críticos:

**Prometheus AlertManager**:

```yaml
# /etc/prometheus/alertmanager.yml

route:
  receiver: 'slack-notifications'

receivers:
  - name: 'slack-notifications'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#ai-native-alertas'
        title: 'AI-Native Alert'
        text: '{{ .CommonAnnotations.summary }}'
```

**Reglas de alerta**:

```yaml
# /etc/prometheus/rules/ai-native.yml

groups:
  - name: ai-native
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "Alta tasa de errores 5xx"
          description: "{{ $value }} errors/s en los últimos 5 minutos"

      - alert: DatabaseDown
        expr: up{job="ai-native-backend"} == 0
        for: 1m
        annotations:
          summary: "Base de datos caída"

      - alert: HighLLMCost
        expr: ai_native_llm_cost_usd > 100
        for: 1h
        annotations:
          summary: "Costo LLM excesivo: ${{ $value }}"
```

---

## Seguridad y Privacidad

### HTTPS/SSL con Let's Encrypt

#### 1. Instalar Certbot

```bash
sudo apt install certbot python3-certbot-nginx
```

#### 2. Obtener Certificado

```bash
sudo certbot --nginx -d tu-dominio.edu.ar -d www.tu-dominio.edu.ar
```

#### 3. Renovación Automática

```bash
# Test de renovación
sudo certbot renew --dry-run

# Cron job (cada día a las 3am)
0 3 * * * certbot renew --quiet
```

### Configurar Nginx como Reverse Proxy

```nginx
# /etc/nginx/sites-available/ai-native

server {
    listen 80;
    server_name tu-dominio.edu.ar;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name tu-dominio.edu.ar;

    ssl_certificate /etc/letsencrypt/live/tu-dominio.edu.ar/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.edu.ar/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
    }

    # Frontend
    location / {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

Activar configuración:

```bash
sudo ln -s /etc/nginx/sites-available/ai-native /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Firewall (UFW)

```bash
# Permitir solo puertos necesarios
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP (redirect a HTTPS)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 8000/tcp   # Backend (solo interno)
sudo ufw deny 5432/tcp   # PostgreSQL (solo interno)

# Activar
sudo ufw enable
sudo ufw status
```

### Anonimización de Datos (GDPR)

Configurar en `.env`:

```bash
ANONYMIZE_EXPORTS=true
ANONYMIZE_AFTER_DAYS=730  # 2 años
```

Script de anonimización:

```python
# scripts/anonymize_old_data.py

from datetime import datetime, timedelta
from src.ai_native_mvp.database import get_db_session
from src.ai_native_mvp.database.models import SessionDB, CognitiveTraceDB

def anonymize_old_data():
    cutoff_date = datetime.now() - timedelta(days=730)

    with get_db_session() as db:
        # Anonimizar sesiones antiguas
        old_sessions = db.query(SessionDB).filter(
            SessionDB.created_at < cutoff_date
        ).all()

        for session in old_sessions:
            session.student_id = f"ANON_{session.id[:8]}"
            # Mantener trazas para investigación, pero sin identificadores

        db.commit()
        print(f"✓ {len(old_sessions)} sesiones anonimizadas")

if __name__ == "__main__":
    anonymize_old_data()
```

Automatizar:

```bash
# Cron: Primer día de cada mes
0 0 1 * * /opt/ai-native-mvp/.venv/bin/python /opt/ai-native-mvp/scripts/anonymize_old_data.py
```

### Auditoría de Seguridad

```bash
# Escaneo de vulnerabilidades con Safety
pip install safety
safety check

# Escaneo de dependencias desactualizadas
pip list --outdated

# Análisis de código con Bandit
pip install bandit
bandit -r src/

# Logs de acceso sospechosos
grep "401\|403\|404" /var/log/ai-native/access.log | tail -100
```

---

## Escalamiento y Performance

### Optimización de Consultas

#### 1. Verificar Índices

```bash
python verify_indexes.py

# Deberías ver:
# ✓ 16/16 índices creados correctamente
```

#### 2. Analizar Queries Lentas (PostgreSQL)

```sql
-- Habilitar log de queries lentas
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1 segundo

-- Ver queries lentas
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Caché con Redis

#### 1. Instalar Redis

```bash
sudo apt install redis-server
sudo systemctl enable redis
sudo systemctl start redis
```

#### 2. Configurar Backend para usar Redis

```bash
# .env
LLM_CACHE_BACKEND=redis
REDIS_URL=redis://localhost:6379/0
```

### Escalamiento Horizontal (Load Balancing)

Para >200 estudiantes concurrentes:

#### 1. Múltiples Instancias Backend

```bash
# Server 1
python scripts/run_api.py --port 8001

# Server 2
python scripts/run_api.py --port 8002

# Server 3
python scripts/run_api.py --port 8003
```

#### 2. Configurar HAProxy

```bash
# /etc/haproxy/haproxy.cfg

frontend http_front
    bind *:80
    default_backend http_back

backend http_back
    balance roundrobin
    option httpchk GET /api/v1/health
    server backend1 127.0.0.1:8001 check
    server backend2 127.0.0.1:8002 check
    server backend3 127.0.0.1:8003 check
```

### Escalamiento con Kubernetes (Enterprise)

Ver documentación completa en: `docs/kubernetes_deployment.md`

---

## Deployment en Producción

### Servicio Systemd (Ubuntu)

#### 1. Crear archivo de servicio

```ini
# /etc/systemd/system/ai-native.service

[Unit]
Description=AI-Native MVP Backend
After=network.target postgresql.service

[Service]
Type=simple
User=ai-native
Group=ai-native
WorkingDirectory=/opt/ai-native-mvp
Environment="PATH=/opt/ai-native-mvp/.venv/bin"
ExecStart=/opt/ai-native-mvp/.venv/bin/python scripts/run_api.py --production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 2. Activar servicio

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-native.service
sudo systemctl start ai-native.service
sudo systemctl status ai-native.service
```

#### 3. Ver logs

```bash
sudo journalctl -u ai-native.service -f
```

### Deploy con Docker Compose (Producción)

Ver sección "Instalación con Docker" más arriba.

---

## Mantenimiento y Actualizaciones

### Actualizar Sistema

```bash
cd /opt/ai-native-mvp

# Backup antes de actualizar
./scripts/backup_database.sh

# Pull cambios
git pull origin main

# Actualizar dependencias
source .venv/bin/activate
pip install --upgrade -r requirements.txt

# Ejecutar migraciones (si hay)
# python scripts/run_migrations.py

# Reiniciar servicio
sudo systemctl restart ai-native.service

# Verificar
curl http://localhost:8000/api/v1/health | jq
```

### Limpieza de Datos Antiguos

```bash
# Eliminar sesiones finalizadas hace >3 años
python scripts/cleanup_old_sessions.py --days 1095

# Limpiar cache LLM antiguo
python scripts/cleanup_llm_cache.py --days 30

# Limpiar logs antiguos
find /var/log/ai-native -name "*.log" -mtime +90 -delete
```

---

## Troubleshooting

### Problema: Backend no inicia

**Síntoma**: `uvicorn` falla al iniciar.

**Soluciones**:

1. Verificar puerto no esté en uso:
```bash
lsof -i:8000
# Si está ocupado, matar proceso o cambiar puerto
```

2. Verificar logs:
```bash
sudo journalctl -u ai-native.service -n 50
```

3. Verificar dependencias:
```bash
source .venv/bin/activate
pip list | grep -E "(fastapi|uvicorn|sqlalchemy)"
```

### Problema: Base de datos bloqueada (SQLite)

**Síntoma**: `OperationalError: database is locked`

**Soluciones**:

1. SQLite no soporta múltiples escritores concurrentes.
2. **Migrar a PostgreSQL** (ver sección correspondiente).

### Problema: Alta latencia en requests

**Síntoma**: Respuestas lentas (>2 segundos).

**Soluciones**:

1. Verificar queries lentas:
```sql
SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 5;
```

2. Verificar caché LLM activo:
```bash
grep "LLM_CACHE_ENABLED" .env
# Debe ser: LLM_CACHE_ENABLED=true
```

3. Verificar latencia a LLM provider:
```bash
curl -w "Time: %{time_total}s\n" -o /dev/null -s https://api.openai.com/v1/models
```

### Problema: Frontend no carga

**Síntoma**: Página en blanco o error 404.

**Soluciones**:

1. Verificar servidor frontend:
```bash
curl http://localhost:3000
```

2. Verificar build:
```bash
cd frontEnd
npm run build
ls dist/  # Debe tener archivos HTML, JS, CSS
```

3. Verificar proxy en Nginx:
```bash
sudo nginx -t
sudo journalctl -u nginx -n 50
```

---

## Cumplimiento y Gobernanza

### Acreditación CONEAU (Argentina)

Para acreditación de carreras por CONEAU, documentar:

1. **Trazabilidad N4** → Evidencia de procesos de aprendizaje
2. **Evaluación formativa** → No solo sumativa
3. **Transparencia algorítmica** → Políticas de IA documentadas
4. **Integridad académica** → Detección de plagio y delegación

**Generar reporte para CONEAU**:

```bash
python scripts/generate_coneau_report.py --year 2025 --output coneau_report_2025.pdf
```

### ISO/IEC 42001:2023 (AI Management System)

Para cumplimiento ISO/IEC 42001:

1. **Documentar políticas de IA**: Ver `institutional_policies.json`
2. **Gestión de riesgos**: Sistema AR-IA automatiza esto
3. **Trazabilidad**: N4 proporciona auditoría completa
4. **Gobernanza**: GOV-IA operacionaliza políticas

### GDPR (Europa) / Ley 25.326 (Argentina)

**Principios implementados**:

- ✅ **Minimización de datos**: Solo capturar lo necesario
- ✅ **Derecho al olvido**: Anonimización automática después de 2 años
- ✅ **Transparencia**: Estudiantes pueden acceder a sus trazas
- ✅ **Portabilidad**: Exportar datos en JSON/CSV

**Script para solicitud de datos (GDPR Article 15)**:

```bash
python scripts/export_user_data.py --student_id student_001 --output student_001_data.zip
```

---

## Preguntas Frecuentes

### ¿Cuánto cuesta operar el sistema?

**Costos principales**:

- **LLM Provider** (variable):
  - Mock: $0/mes (desarrollo)
  - Gemini: $0/mes (60 req/min gratis)
  - OpenAI GPT-3.5: ~$50-200/mes (50-200 estudiantes)
  - OpenAI GPT-4: ~$200-800/mes (50-200 estudiantes)

- **Servidor**:
  - VPS 8GB RAM: ~$40/mes
  - Dedicado 32GB RAM: ~$200/mes

- **Backup/Storage**: ~$10/mes

**Total estimado (50-200 estudiantes)**: $100-400/mes

### ¿Cuánto tiempo toma la instalación?

- **Desarrollo (manual)**: 1-2 horas
- **Producción (Docker)**: 2-4 horas
- **Enterprise (Kubernetes)**: 1-2 días

### ¿Soporta múltiples idiomas?

Actualmente en **español**. Para agregar inglés u otros idiomas:

1. Traducir prompts de agentes (`agents/*.py`)
2. Actualizar frontend (`frontEnd/src/locales/`)
3. Configurar `LANGUAGE=en` en `.env`

### ¿Funciona sin conexión a Internet?

**Parcialmente**:
- ✅ Con `LLM_PROVIDER=mock`: Sí (respuestas simuladas)
- ❌ Con OpenAI/Gemini/Claude: No (requiere conexión)

**Solución offline**: Deployar LLM local (LLaMA, Mistral) con Ollama.

---

## 📞 Soporte Técnico

### Contacto

- **Email**: admin@tu-institucion.edu.ar
- **Documentación**: `/opt/ai-native-mvp/README_MVP.md`
- **Issues**: GitHub (si aplicable)

### Recursos Adicionales

- **Manual Docente**: `GUIA_DOCENTE.md`
- **Manual Estudiante**: `GUIA_ESTUDIANTE.md`
- **API Docs**: `README_API.md`
- **Tesis Completa**: `tesis.txt`

---

**¡Éxito con el deployment! 🚀**

**Mag. en Ing. de Software Alberto Cortez**
Universidad Tecnológica Nacional