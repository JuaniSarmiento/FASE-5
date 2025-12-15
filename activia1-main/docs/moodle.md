# Guia de Integracion AI-Native MVP con Moodle via LTI 1.3

## Documentacion Tecnica Completa

**Version**: 1.0
**Fecha**: Diciembre 2025
**Proyecto**: AI-Native MVP - Tesis Doctoral
**Historia de Usuario**: HU-SYS-010 - Integracion LTI 1.3

---

## Tabla de Contenidos

1. [Introduccion a LTI 1.3](#1-introduccion-a-lti-13)
2. [Arquitectura de Integracion](#2-arquitectura-de-integracion)
3. [Infraestructura Existente en AI-Native](#3-infraestructura-existente-en-ai-native)
4. [Configuracion de Moodle](#4-configuracion-de-moodle)
5. [Configuracion de AI-Native](#5-configuracion-de-ai-native)
6. [Implementacion del Router LTI](#6-implementacion-del-router-lti)
7. [Flujo de Autenticacion Completo](#7-flujo-de-autenticacion-completo)
8. [Mapeo de Datos LTI a AI-Native](#8-mapeo-de-datos-lti-a-ai-native)
9. [Integracion con Agentes](#9-integracion-con-agentes)
10. [LTI Advantage Services](#10-lti-advantage-services)
11. [Seguridad y Gobernanza](#11-seguridad-y-gobernanza)
12. [Pruebas y Validacion](#12-pruebas-y-validacion)
13. [Troubleshooting](#13-troubleshooting)
14. [Referencias](#14-referencias)

---

## 1. Introduccion a LTI 1.3

### 1.1 Que es LTI?

**Learning Tools Interoperability (LTI)** es un estandar desarrollado por IMS Global que permite integrar herramientas de aprendizaje externas con plataformas LMS (Learning Management Systems) como Moodle, Canvas, Blackboard, etc.

**LTI 1.3** es la version mas reciente (2019) que incorpora:
- **OAuth 2.0** para autenticacion segura
- **OpenID Connect (OIDC)** para intercambio de identidad
- **JSON Web Tokens (JWT)** para mensajes firmados
- **LTI Advantage** para servicios adicionales

### 1.2 Beneficios de la Integracion

| Beneficio | Descripcion |
|-----------|-------------|
| **Single Sign-On (SSO)** | Estudiantes acceden desde Moodle sin login adicional |
| **Contexto Academico** | AI-Native recibe info del curso, actividad y estudiante |
| **Sincronizacion de Calificaciones** | Reportes de evaluacion pueden enviarse a Moodle |
| **Gestion Centralizada** | Docentes administran desde Moodle |
| **Trazabilidad Institucional** | GOV-IA puede vincular sesiones con cursos reales |

### 1.3 Componentes Clave de LTI 1.3

```
+==================+                    +==================+
|      MOODLE      |                    |    AI-NATIVE     |
|   (Platform)     |                    |     (Tool)       |
+==================+                    +==================+
|                  |                    |                  |
| - Issuer         |    OIDC Login      | - Client ID      |
| - JWKS URL       | -----------------> | - Deployment ID  |
| - Auth URL       |                    | - JWKS URL       |
| - Token URL      |    LTI Launch      | - Launch URL     |
|                  | -----------------> |                  |
|                  |    JWT Token       |                  |
|                  | =================> |                  |
|                  |                    |                  |
|                  |   Grade Passback   |                  |
|                  | <================= |                  |
|                  |    (LTI-AGS)       |                  |
+==================+                    +==================+
```

### 1.4 Terminologia

| Termino | Significado |
|---------|-------------|
| **Platform** | El LMS (Moodle) que inicia el launch |
| **Tool** | La aplicacion externa (AI-Native) |
| **Issuer** | URL unico que identifica a Moodle |
| **Client ID** | ID de la herramienta registrada en Moodle |
| **Deployment ID** | ID de un deployment especifico |
| **Resource Link** | Actividad especifica en Moodle |
| **JWKS** | JSON Web Key Set para validar tokens |

---

## 2. Arquitectura de Integracion

### 2.1 Diagrama de Arquitectura Completo

```
+============================================================================+
|                         ARQUITECTURA LTI 1.3                                |
|                    AI-Native MVP <-> Moodle                                 |
+============================================================================+

                            MOODLE LMS
                    +------------------------+
                    |                        |
                    |  +------------------+  |
                    |  |   Curso:         |  |
                    |  |   Programacion I |  |
                    |  +--------+---------+  |
                    |           |            |
                    |  +--------v---------+  |
                    |  | Actividad LTI:   |  |
                    |  | "Tutor IA"       |  |
                    |  +--------+---------+  |
                    |           |            |
                    +-----------|------------+
                                |
                    1. OIDC Login Request
                    (redirect con login_hint)
                                |
                                v
+============================================================================+
|                         AI-NATIVE MVP                                       |
+============================================================================+
|                                                                             |
|   +-----------------+     +------------------+     +------------------+     |
|   |  LTI Router     |---->|  LTI Service     |---->|   Repositories   |     |
|   |  /api/v1/lti/*  |     |                  |     |                  |     |
|   +-----------------+     +------------------+     +------------------+     |
|          |                       |                        |                 |
|          |                       |                        v                 |
|   2. Validate OIDC        3. Verify JWT          +------------------+      |
|      Parameters              Signature           |  PostgreSQL      |      |
|          |                       |               |  - lti_deployments|      |
|          v                       v               |  - lti_sessions   |      |
|   +-----------------+     +------------------+   |  - sessions       |      |
|   |  OIDC Handler   |     |   JWT Validator  |   +------------------+      |
|   |  (state, nonce) |     |   (JWKS fetch)   |                              |
|   +-----------------+     +------------------+                              |
|          |                       |                                          |
|          +----------+------------+                                          |
|                     |                                                       |
|                     v                                                       |
|          +------------------+                                               |
|          |  Session Creator |                                               |
|          |  - Map LTI user  |                                               |
|          |  - Create session|                                               |
|          +--------+---------+                                               |
|                   |                                                         |
|                   v                                                         |
|   +===============================================+                         |
|   |           AI GATEWAY (STATELESS)              |                         |
|   +===============================================+                         |
|   |                                               |                         |
|   |   +----------+  +----------+  +----------+   |                         |
|   |   | T-IA-Cog |  | E-IA-Proc|  | S-IA-X   |   |                         |
|   |   | (Tutor)  |  | (Eval)   |  | (Sim)    |   |                         |
|   |   +----------+  +----------+  +----------+   |                         |
|   |        |              |             |        |                         |
|   |        +------+-------+-------------+        |                         |
|   |               |                              |                         |
|   |   +----------v----------+                    |                         |
|   |   |      GOV-IA         |                    |                         |
|   |   | - LTI context aware |                    |                         |
|   |   | - Course policies   |                    |                         |
|   |   +---------------------+                    |                         |
|   +===============================================+                         |
|                                                                             |
+============================================================================+
```

### 2.2 Flujo de Launch LTI 1.3

```
Estudiante          Moodle              AI-Native           AI-Native
  (Browser)        (Platform)          (LTI Router)         (Gateway)
     |                 |                    |                    |
     | 1. Click        |                    |                    |
     |    actividad    |                    |                    |
     |---------------->|                    |                    |
     |                 |                    |                    |
     |    2. OIDC      |                    |                    |
     |    Login        |                    |                    |
     |<----------------|                    |                    |
     |    Request      |                    |                    |
     |                 |                    |                    |
     | 3. Redirect     |                    |                    |
     |-----------------|------------------>|                    |
     |                 |                    |                    |
     |                 |   4. Validate     |                    |
     |                 |      & store      |                    |
     |                 |      state/nonce  |                    |
     |                 |                    |                    |
     |    5. Auth      |                    |                    |
     |    Response     |                    |                    |
     |<----------------|<-------------------|                    |
     |    (form POST)  |                    |                    |
     |                 |                    |                    |
     | 6. POST         |                    |                    |
     |    id_token     |                    |                    |
     |-----------------|------------------>|                    |
     |                 |                    |                    |
     |                 |   7. Validate     |                    |
     |                 |      JWT          |                    |
     |                 |      (JWKS)       |                    |
     |                 |                    |                    |
     |                 |   8. Create       |                    |
     |                 |      LTI Session  |                    |
     |                 |                    |                    |
     |                 |   9. Create       |                    |
     |                 |      AI-Native    |                    |
     |                 |      Session      |                    |
     |                 |                    |------->           |
     |                 |                    |                    |
     |   10. Redirect  |                    |                    |
     |       to app    |                    |                    |
     |<----------------|<-------------------|                    |
     |                 |                    |                    |
```

---

## 3. Infraestructura Existente en AI-Native

### 3.1 Modelos de Base de Datos

El sistema AI-Native ya tiene preparada la infraestructura de base de datos para LTI:

#### 3.1.1 Tabla `lti_deployments`

**Ubicacion**: `backend/database/models.py` (linea 1272)

```python
class LTIDeploymentDB(Base, BaseModel):
    """
    LTI 1.3 platform deployments (Moodle, Canvas, etc.)
    Stores LTI configuration for external platforms for HU-SYS-010
    """

    __tablename__ = "lti_deployments"

    # Platform information
    platform_name = Column(String(100), nullable=False)  # "Moodle"
    issuer = Column(String(255), nullable=False)         # LTI issuer URL
    client_id = Column(String(255), nullable=False)      # OAuth2 client ID
    deployment_id = Column(String(255), nullable=False)  # LTI deployment ID

    # OIDC endpoints
    auth_login_url = Column(Text, nullable=False)        # OIDC auth login URL
    auth_token_url = Column(Text, nullable=False)        # OAuth2 token URL
    public_keyset_url = Column(Text, nullable=False)     # JWKS URL

    # Optional: Access token URL for LTI Advantage services
    access_token_url = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True, server_default='true')
```

#### 3.1.2 Tabla `lti_sessions`

**Ubicacion**: `backend/database/models.py` (linea 1364)

```python
class LTISessionDB(Base, BaseModel):
    """
    LTI launch sessions (student launches from Moodle)
    Maps LTI users to AI-Native sessions for HU-SYS-010
    """

    __tablename__ = "lti_sessions"

    # LTI deployment
    deployment_id = Column(String(36), ForeignKey("lti_deployments.id", ondelete="CASCADE"))

    # LTI user information
    lti_user_id = Column(String(255), nullable=False)    # User ID from Moodle
    lti_user_name = Column(String(255), nullable=True)
    lti_user_email = Column(String(255), nullable=True)

    # LTI context (course)
    lti_context_id = Column(String(255), nullable=True)  # Course ID from Moodle
    lti_context_label = Column(String(100), nullable=True)  # Course code
    lti_context_title = Column(String(255), nullable=True)  # Course name

    # LTI resource link (activity within course)
    resource_link_id = Column(String(255), nullable=False)

    # Mapped to AI-Native session
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)

    # Launch metadata
    launch_token = Column(Text, nullable=True)  # JWT token from LTI launch
    locale = Column(String(10), nullable=True)  # User's locale (e.g., "es_AR")
```

### 3.2 Schemas Pydantic

**Ubicacion**: `backend/api/schemas/sprint5_6.py` (linea 285)

```python
# LTI Deployment schemas
class LTIDeploymentCreate(BaseModel):
    platform_name: str
    issuer: str
    client_id: str
    deployment_id: str
    auth_login_url: str
    auth_token_url: str
    public_keyset_url: str
    access_token_url: Optional[str] = None

class LTIDeploymentResponse(BaseModel):
    id: str
    platform_name: str
    issuer: str
    client_id: str
    deployment_id: str
    # ... (ver archivo completo)

# LTI Session schemas
class LTISessionCreate(BaseModel):
    deployment_id: str
    lti_user_id: str
    lti_user_name: Optional[str] = None
    lti_user_email: Optional[str] = None
    lti_context_id: Optional[str] = None
    lti_context_label: Optional[str] = None
    lti_context_title: Optional[str] = None
    resource_link_id: str
    session_id: Optional[str] = None
    launch_token: Optional[str] = None
    locale: Optional[str] = None
```

### 3.3 Estado Actual de Implementacion

| Componente | Estado | Ubicacion |
|------------|--------|-----------|
| Modelos ORM | IMPLEMENTADO | `backend/database/models.py` |
| Schemas Pydantic | IMPLEMENTADO | `backend/api/schemas/sprint5_6.py` |
| Router LTI | PENDIENTE | Necesita crearse |
| Servicio LTI | PENDIENTE | Necesita crearse |
| JWKS Validation | PENDIENTE | Necesita crearse |
| OIDC Flow | PENDIENTE | Necesita crearse |

---

## 4. Configuracion de Moodle

### 4.1 Requisitos Previos

- Moodle 3.9+ (recomendado 4.x)
- Rol de administrador en Moodle
- AI-Native MVP desplegado y accesible via HTTPS
- Certificado SSL valido (requerido para LTI 1.3)

### 4.2 Paso 1: Habilitar LTI en Moodle

1. Acceder como **Administrador**
2. Ir a **Site administration > Plugins > Activity modules > External tool**
3. Verificar que "Manage tools" este habilitado

### 4.3 Paso 2: Registrar AI-Native como Tool

1. Ir a **Site administration > Plugins > Activity modules > External tool > Manage tools**
2. Click en **"configure a tool manually"**

#### 4.3.1 Configuracion Basica

| Campo | Valor |
|-------|-------|
| **Tool name** | AI-Native Tutor |
| **Tool URL** | `https://your-domain.com/api/v1/lti/launch` |
| **LTI version** | LTI 1.3 |
| **Public key type** | Keyset URL |
| **Public keyset** | `https://your-domain.com/api/v1/lti/jwks` |
| **Initiate login URL** | `https://your-domain.com/api/v1/lti/login` |
| **Redirection URI(s)** | `https://your-domain.com/api/v1/lti/launch` |

#### 4.3.2 Configuracion de Servicios

| Servicio | Configuracion |
|----------|---------------|
| **IMS LTI Assignment and Grade Services** | Use for grade sync and column management |
| **IMS LTI Names and Role Provisioning Services** | Use for retrieving members' info |
| **Tool Settings** | Use as instructed by tool |

#### 4.3.3 Configuracion de Privacidad

| Campo | Valor Recomendado |
|-------|-------------------|
| **Share launcher's name** | Always |
| **Share launcher's email** | Always |
| **Accept grades** | Always |

### 4.4 Paso 3: Obtener Credenciales de Moodle

Despues de guardar, Moodle generara:

```
Platform ID (Issuer):     https://your-moodle.edu
Client ID:                abc123xyz
Deployment ID:            1
Public keyset URL:        https://your-moodle.edu/mod/lti/certs.php
Access token URL:         https://your-moodle.edu/mod/lti/token.php
Authentication request URL: https://your-moodle.edu/mod/lti/auth.php
```

**IMPORTANTE**: Guardar estos valores para configurar AI-Native.

### 4.5 Paso 4: Agregar Actividad en un Curso

1. Ir al curso deseado
2. **Turn editing on**
3. **Add an activity or resource > External tool**
4. Seleccionar "AI-Native Tutor" de la lista preconfigured
5. Configurar nombre y descripcion
6. Guardar

---

## 5. Configuracion de AI-Native

### 5.1 Variables de Entorno

Agregar al archivo `.env`:

```bash
# =============================================================================
# LTI 1.3 Configuration
# =============================================================================

# AI-Native as LTI Tool
LTI_TOOL_CLIENT_ID=your-generated-client-id
LTI_TOOL_DEPLOYMENT_ID=1
LTI_TOOL_ISSUER=https://your-domain.com

# Key pair for JWT signing (generate with: openssl genrsa -out private.pem 2048)
LTI_PRIVATE_KEY_PATH=/app/keys/private.pem
LTI_PUBLIC_KEY_PATH=/app/keys/public.pem

# JWKS cache TTL (seconds)
LTI_JWKS_CACHE_TTL=3600

# State/Nonce expiration (seconds)
LTI_STATE_EXPIRATION=600

# Frontend redirect after successful launch
LTI_SUCCESS_REDIRECT=https://your-domain.com/app
```

### 5.2 Generar Par de Claves RSA

```bash
# Crear directorio para claves
mkdir -p keys

# Generar clave privada RSA 2048 bits
openssl genrsa -out keys/private.pem 2048

# Extraer clave publica
openssl rsa -in keys/private.pem -pubout -out keys/public.pem

# Verificar que se crearon correctamente
ls -la keys/
```

### 5.3 Registrar Deployment en Base de Datos

Ejecutar script SQL o usar el endpoint de admin (cuando se implemente):

```sql
INSERT INTO lti_deployments (
    id,
    platform_name,
    issuer,
    client_id,
    deployment_id,
    auth_login_url,
    auth_token_url,
    public_keyset_url,
    access_token_url,
    is_active,
    created_at,
    updated_at
) VALUES (
    'uuid-generado',
    'Moodle Universidad',
    'https://your-moodle.edu',
    'abc123xyz',
    '1',
    'https://your-moodle.edu/mod/lti/auth.php',
    'https://your-moodle.edu/mod/lti/token.php',
    'https://your-moodle.edu/mod/lti/certs.php',
    'https://your-moodle.edu/mod/lti/token.php',
    true,
    NOW(),
    NOW()
);
```

O usando Python:

```python
from backend.database.models import LTIDeploymentDB
from backend.database import get_db

db = next(get_db())

deployment = LTIDeploymentDB(
    platform_name="Moodle Universidad",
    issuer="https://your-moodle.edu",
    client_id="abc123xyz",
    deployment_id="1",
    auth_login_url="https://your-moodle.edu/mod/lti/auth.php",
    auth_token_url="https://your-moodle.edu/mod/lti/token.php",
    public_keyset_url="https://your-moodle.edu/mod/lti/certs.php",
    access_token_url="https://your-moodle.edu/mod/lti/token.php",
    is_active=True
)

db.add(deployment)
db.commit()
print(f"Deployment created with ID: {deployment.id}")
```

---

## 6. Implementacion del Router LTI

### 6.1 Archivo del Router

**Crear**: `backend/api/routers/lti.py`

```python
"""
LTI 1.3 Router - Endpoints para integracion con Moodle y otros LMS

Endpoints:
- GET  /lti/login      - OIDC Login Initiation
- POST /lti/launch     - LTI Launch (recibe JWT)
- GET  /lti/jwks       - Public Key Set (JWKS)
- POST /lti/deeplink   - Deep Linking (opcional)

HU-SYS-010: Integracion LTI 1.3
"""

import json
import uuid
import time
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from urllib.parse import urlencode

import httpx
import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from fastapi import APIRouter, Request, Response, HTTPException, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.database.models import LTIDeploymentDB, LTISessionDB, SessionDB
from backend.core.redis_cache import RedisCache
from backend.core.config import settings

router = APIRouter(prefix="/lti", tags=["LTI 1.3"])

# Cache para state/nonce (usar Redis en produccion)
_state_cache: Dict[str, Dict[str, Any]] = {}


def get_redis_cache():
    """Obtener instancia de cache Redis"""
    return RedisCache()


def load_private_key():
    """Cargar clave privada RSA para firmar tokens"""
    with open(settings.LTI_PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )


def load_public_key():
    """Cargar clave publica RSA"""
    with open(settings.LTI_PUBLIC_KEY_PATH, "rb") as f:
        return f.read()


async def fetch_platform_jwks(jwks_url: str) -> Dict[str, Any]:
    """
    Obtener JWKS de la plataforma (Moodle) para validar tokens.
    Implementa cache para evitar requests repetidos.
    """
    cache = get_redis_cache()
    cache_key = f"lti_jwks:{hashlib.md5(jwks_url.encode()).hexdigest()}"

    # Intentar obtener de cache
    cached = await cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Fetch desde la plataforma
    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url, timeout=10.0)
        response.raise_for_status()
        jwks = response.json()

    # Guardar en cache (1 hora)
    await cache.set(cache_key, json.dumps(jwks), ex=3600)

    return jwks


def validate_jwt_token(
    token: str,
    jwks: Dict[str, Any],
    expected_issuer: str,
    expected_client_id: str
) -> Dict[str, Any]:
    """
    Validar JWT token del launch LTI.

    Verificaciones:
    - Firma valida (usando JWKS de la plataforma)
    - Issuer correcto
    - Audience (client_id) correcto
    - Token no expirado
    - Nonce no reutilizado
    """
    # Obtener header sin verificar para extraer kid
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    # Buscar la clave correcta en JWKS
    public_key = None
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
            break

    if not public_key:
        raise HTTPException(status_code=401, detail="No matching key found in JWKS")

    try:
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=expected_client_id,
            issuer=expected_issuer,
            options={
                "verify_exp": True,
                "verify_iat": True,
                "require": ["exp", "iat", "iss", "aud", "sub", "nonce"]
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# =============================================================================
# ENDPOINT: OIDC Login Initiation
# =============================================================================

@router.get("/login")
async def lti_login(
    request: Request,
    iss: str,                          # Issuer (Moodle URL)
    login_hint: str,                   # User hint from Moodle
    target_link_uri: str,              # Where to redirect after auth
    lti_message_hint: Optional[str] = None,
    client_id: Optional[str] = None,
    lti_deployment_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    OIDC Login Initiation Endpoint.

    Moodle redirige aqui cuando un estudiante hace click en la actividad LTI.
    Este endpoint:
    1. Valida que el issuer este registrado
    2. Genera state y nonce
    3. Redirige al auth endpoint de Moodle
    """
    # Buscar deployment por issuer
    deployment = db.query(LTIDeploymentDB).filter(
        LTIDeploymentDB.issuer == iss,
        LTIDeploymentDB.is_active == True
    ).first()

    if not deployment:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown issuer: {iss}. Platform not registered."
        )

    # Si se proporciono client_id, verificar que coincida
    if client_id and client_id != deployment.client_id:
        raise HTTPException(
            status_code=400,
            detail="Client ID mismatch"
        )

    # Generar state y nonce unicos
    state = str(uuid.uuid4())
    nonce = str(uuid.uuid4())

    # Guardar en cache para validar luego (expira en 10 minutos)
    cache_data = {
        "deployment_id": deployment.id,
        "target_link_uri": target_link_uri,
        "nonce": nonce,
        "created_at": datetime.utcnow().isoformat()
    }

    # Usar Redis en produccion, dict en desarrollo
    cache = get_redis_cache()
    await cache.set(f"lti_state:{state}", json.dumps(cache_data), ex=600)

    # Construir URL de autorizacion
    auth_params = {
        "response_type": "id_token",
        "response_mode": "form_post",
        "scope": "openid",
        "client_id": deployment.client_id,
        "redirect_uri": str(request.url_for("lti_launch")),
        "login_hint": login_hint,
        "state": state,
        "nonce": nonce,
        "prompt": "none"  # No mostrar UI de login (ya autenticado en Moodle)
    }

    if lti_message_hint:
        auth_params["lti_message_hint"] = lti_message_hint

    auth_url = f"{deployment.auth_login_url}?{urlencode(auth_params)}"

    return RedirectResponse(url=auth_url, status_code=302)


# =============================================================================
# ENDPOINT: LTI Launch (recibe JWT)
# =============================================================================

@router.post("/launch")
async def lti_launch(
    request: Request,
    id_token: str = Form(...),
    state: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    LTI Launch Endpoint.

    Moodle envia aqui el id_token JWT despues de la autenticacion OIDC.
    Este endpoint:
    1. Valida el state
    2. Valida el JWT (firma, claims)
    3. Crea LTISession en BD
    4. Crea o recupera Session de AI-Native
    5. Redirige a la aplicacion frontend
    """
    cache = get_redis_cache()

    # 1. Validar state
    state_data_raw = await cache.get(f"lti_state:{state}")
    if not state_data_raw:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired state. Please try launching again."
        )

    state_data = json.loads(state_data_raw)

    # Eliminar state usado (one-time use)
    await cache.delete(f"lti_state:{state}")

    # 2. Obtener deployment
    deployment = db.query(LTIDeploymentDB).filter(
        LTIDeploymentDB.id == state_data["deployment_id"]
    ).first()

    if not deployment:
        raise HTTPException(status_code=400, detail="Deployment not found")

    # 3. Obtener JWKS de Moodle y validar token
    jwks = await fetch_platform_jwks(deployment.public_keyset_url)

    try:
        claims = validate_jwt_token(
            id_token,
            jwks,
            expected_issuer=deployment.issuer,
            expected_client_id=deployment.client_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")

    # 4. Validar nonce
    if claims.get("nonce") != state_data["nonce"]:
        raise HTTPException(status_code=401, detail="Nonce mismatch")

    # 5. Extraer claims LTI
    lti_user_id = claims.get("sub")
    lti_user_name = claims.get("name") or claims.get("given_name", "")
    lti_user_email = claims.get("email")

    # Context claim (curso)
    context = claims.get("https://purl.imsglobal.org/spec/lti/claim/context", {})
    lti_context_id = context.get("id")
    lti_context_label = context.get("label")
    lti_context_title = context.get("title")

    # Resource link claim (actividad)
    resource_link = claims.get("https://purl.imsglobal.org/spec/lti/claim/resource_link", {})
    resource_link_id = resource_link.get("id")

    if not resource_link_id:
        raise HTTPException(status_code=400, detail="Missing resource_link_id")

    # Roles del usuario
    roles = claims.get("https://purl.imsglobal.org/spec/lti/claim/roles", [])
    is_instructor = any("Instructor" in role for role in roles)

    # Locale
    locale = claims.get("locale", "es_AR")

    # 6. Buscar o crear LTI Session
    existing_lti_session = db.query(LTISessionDB).filter(
        LTISessionDB.deployment_id == deployment.id,
        LTISessionDB.lti_user_id == lti_user_id,
        LTISessionDB.resource_link_id == resource_link_id
    ).first()

    if existing_lti_session and existing_lti_session.session_id:
        # Ya existe sesion, recuperar
        ai_session = db.query(SessionDB).filter(
            SessionDB.id == existing_lti_session.session_id
        ).first()

        if ai_session and ai_session.status == "active":
            # Sesion activa existente, actualizar launch token
            existing_lti_session.launch_token = id_token
            existing_lti_session.updated_at = datetime.utcnow()
            db.commit()

            # Redirigir a frontend con sesion existente
            redirect_url = f"{settings.LTI_SUCCESS_REDIRECT}?session_id={ai_session.id}"
            return RedirectResponse(url=redirect_url, status_code=302)

    # 7. Crear nueva sesion AI-Native
    ai_session = SessionDB(
        student_id=f"lti:{lti_user_id}",  # Prefijo para identificar usuarios LTI
        activity_id=f"lti:{resource_link_id}",
        mode="tutor",  # Default mode
        status="active",
        context={
            "lti_launch": True,
            "lti_context_id": lti_context_id,
            "lti_context_title": lti_context_title,
            "is_instructor": is_instructor,
            "roles": roles
        }
    )
    db.add(ai_session)
    db.flush()  # Para obtener el ID

    # 8. Crear o actualizar LTI Session
    if existing_lti_session:
        existing_lti_session.session_id = ai_session.id
        existing_lti_session.launch_token = id_token
        existing_lti_session.lti_user_name = lti_user_name
        existing_lti_session.lti_user_email = lti_user_email
        existing_lti_session.lti_context_id = lti_context_id
        existing_lti_session.lti_context_label = lti_context_label
        existing_lti_session.lti_context_title = lti_context_title
        existing_lti_session.locale = locale
        existing_lti_session.updated_at = datetime.utcnow()
    else:
        lti_session = LTISessionDB(
            deployment_id=deployment.id,
            lti_user_id=lti_user_id,
            lti_user_name=lti_user_name,
            lti_user_email=lti_user_email,
            lti_context_id=lti_context_id,
            lti_context_label=lti_context_label,
            lti_context_title=lti_context_title,
            resource_link_id=resource_link_id,
            session_id=ai_session.id,
            launch_token=id_token,
            locale=locale
        )
        db.add(lti_session)

    db.commit()

    # 9. Redirigir a frontend
    redirect_url = f"{settings.LTI_SUCCESS_REDIRECT}?session_id={ai_session.id}&lti=1"

    # Si es instructor, agregar flag
    if is_instructor:
        redirect_url += "&instructor=1"

    return RedirectResponse(url=redirect_url, status_code=302)


# =============================================================================
# ENDPOINT: JWKS (Public Key Set)
# =============================================================================

@router.get("/jwks")
async def get_jwks():
    """
    JSON Web Key Set endpoint.

    Moodle usa este endpoint para obtener las claves publicas
    de AI-Native para verificar tokens firmados por nosotros
    (usado en LTI Advantage services como AGS).
    """
    public_key_pem = load_public_key()

    # Parsear la clave publica
    from cryptography.hazmat.primitives.serialization import load_pem_public_key
    public_key = load_pem_public_key(public_key_pem, backend=default_backend())

    # Obtener numeros de la clave RSA
    public_numbers = public_key.public_numbers()

    import base64

    def int_to_base64url(n: int) -> str:
        """Convertir entero a base64url"""
        byte_length = (n.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(
            n.to_bytes(byte_length, byteorder='big')
        ).decode('ascii').rstrip('=')

    jwk = {
        "kty": "RSA",
        "use": "sig",
        "alg": "RS256",
        "kid": "ai-native-key-1",
        "n": int_to_base64url(public_numbers.n),
        "e": int_to_base64url(public_numbers.e)
    }

    return {"keys": [jwk]}


# =============================================================================
# ENDPOINT: Health Check LTI
# =============================================================================

@router.get("/health")
async def lti_health(db: Session = Depends(get_db)):
    """
    Health check para el subsistema LTI.
    Verifica que hay deployments activos.
    """
    active_deployments = db.query(LTIDeploymentDB).filter(
        LTIDeploymentDB.is_active == True
    ).count()

    return {
        "status": "ok" if active_deployments > 0 else "warning",
        "active_deployments": active_deployments,
        "message": "LTI subsystem operational" if active_deployments > 0
                   else "No active LTI deployments configured"
    }
```

### 6.2 Registrar Router en la Aplicacion

**Editar**: `backend/api/main.py`

```python
# Agregar import
from backend.api.routers import lti

# Agregar router (despues de los otros routers)
app.include_router(lti.router, prefix="/api/v1")
```

### 6.3 Agregar Configuracion

**Editar**: `backend/core/config.py`

```python
class Settings(BaseSettings):
    # ... configuraciones existentes ...

    # LTI 1.3 Configuration
    LTI_PRIVATE_KEY_PATH: str = "keys/private.pem"
    LTI_PUBLIC_KEY_PATH: str = "keys/public.pem"
    LTI_SUCCESS_REDIRECT: str = "http://localhost:5173/app"
    LTI_STATE_EXPIRATION: int = 600  # 10 minutes
    LTI_JWKS_CACHE_TTL: int = 3600   # 1 hour
```

---

## 7. Flujo de Autenticacion Completo

### 7.1 Secuencia Detallada

```
1. ESTUDIANTE EN MOODLE
   |
   | Click en "Actividad: AI-Native Tutor"
   v

2. MOODLE GENERA OIDC REQUEST
   - login_hint: "user123"
   - target_link_uri: "https://ai-native/api/v1/lti/launch"
   - lti_message_hint: "resource789"
   |
   | HTTP 302 Redirect
   v

3. AI-NATIVE /lti/login
   - Valida issuer (debe estar registrado)
   - Genera state y nonce
   - Guarda en Redis: state -> {deployment_id, nonce, ...}
   |
   | HTTP 302 Redirect a Moodle auth
   v

4. MOODLE /mod/lti/auth.php
   - Valida que el usuario esta logueado
   - Genera id_token JWT con claims LTI
   - Firma con clave privada de Moodle
   |
   | HTTP 200 con form auto-submit
   v

5. BROWSER AUTO-SUBMIT FORM
   - POST a AI-Native con id_token y state
   |
   | HTTP POST
   v

6. AI-NATIVE /lti/launch
   - Valida state (busca en Redis)
   - Fetch JWKS de Moodle
   - Valida firma del JWT
   - Valida claims (iss, aud, exp, nonce)
   - Extrae informacion del usuario y curso
   - Crea/recupera LTISession
   - Crea/recupera Session AI-Native
   |
   | HTTP 302 Redirect
   v

7. FRONTEND AI-NATIVE
   - Recibe session_id en query params
   - Carga sesion y muestra interfaz
   - Usuario puede interactuar con agentes
```

### 7.2 Claims JWT Importantes

```json
{
  "iss": "https://moodle.universidad.edu",
  "aud": "abc123xyz",
  "sub": "user123",
  "exp": 1702500000,
  "iat": 1702496400,
  "nonce": "uuid-nonce",
  "name": "Juan Perez",
  "email": "juan.perez@universidad.edu",
  "locale": "es_AR",

  "https://purl.imsglobal.org/spec/lti/claim/message_type": "LtiResourceLinkRequest",
  "https://purl.imsglobal.org/spec/lti/claim/version": "1.3.0",
  "https://purl.imsglobal.org/spec/lti/claim/deployment_id": "1",

  "https://purl.imsglobal.org/spec/lti/claim/context": {
    "id": "course123",
    "label": "PROG1",
    "title": "Programacion I",
    "type": ["CourseSection"]
  },

  "https://purl.imsglobal.org/spec/lti/claim/resource_link": {
    "id": "resource789",
    "title": "Actividad Tutor IA"
  },

  "https://purl.imsglobal.org/spec/lti/claim/roles": [
    "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner",
    "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student"
  ],

  "https://purl.imsglobal.org/spec/lti-ags/claim/endpoint": {
    "scope": ["..."],
    "lineitems": "https://moodle.edu/mod/lti/services.php/.../lineitems",
    "lineitem": "https://moodle.edu/mod/lti/services.php/.../lineitem"
  }
}
```

---

## 8. Mapeo de Datos LTI a AI-Native

### 8.1 Mapeo de Usuario

| LTI Claim | AI-Native Field | Transformacion |
|-----------|-----------------|----------------|
| `sub` | `student_id` | Prefijo "lti:" |
| `name` | `LTISession.lti_user_name` | Directo |
| `email` | `LTISession.lti_user_email` | Directo |
| `locale` | `LTISession.locale` | Directo |

### 8.2 Mapeo de Contexto

| LTI Claim | AI-Native Field | Uso |
|-----------|-----------------|-----|
| `context.id` | `lti_context_id` | Identificar curso |
| `context.label` | `lti_context_label` | Codigo del curso |
| `context.title` | `lti_context_title` | Nombre del curso |
| `resource_link.id` | `activity_id` | Identificar actividad |

### 8.3 Mapeo de Roles

```python
def map_lti_role_to_ai_native(roles: List[str]) -> str:
    """Mapear roles LTI a roles AI-Native"""

    # Buscar rol de instructor
    instructor_patterns = [
        "Instructor",
        "ContentDeveloper",
        "Administrator",
        "TeachingAssistant"
    ]

    for role in roles:
        for pattern in instructor_patterns:
            if pattern in role:
                return "teacher"

    return "student"
```

---

## 9. Integracion con Agentes

### 9.1 Contexto LTI en Interacciones

Cuando una sesion proviene de LTI, los agentes reciben contexto adicional:

```python
# En AIGateway.process_interaction()
if session.context.get("lti_launch"):
    # Agregar contexto LTI para los agentes
    lti_context = {
        "course_id": session.context.get("lti_context_id"),
        "course_name": session.context.get("lti_context_title"),
        "is_instructor": session.context.get("is_instructor", False)
    }
    context["lti"] = lti_context
```

### 9.2 Politicas por Curso (GOV-IA)

El agente GOV-IA puede aplicar politicas especificas por curso:

```python
# En GobernanzaAgent.get_course_policies()
def get_course_policies(self, lti_context_id: str) -> Dict[str, Any]:
    """
    Obtener politicas especificas del curso desde configuracion
    o base de datos.
    """
    # Buscar configuracion del curso
    course_config = self.course_policies_repo.get(lti_context_id)

    if course_config:
        return {
            "max_ai_assistance_level": course_config.max_ai_level,
            "block_complete_solutions": course_config.block_solutions,
            "require_traceability": True,
            "custom_rules": course_config.custom_rules
        }

    # Usar defaults institucionales
    return self.default_policies
```

### 9.3 Reportes por Curso

Los reportes institucionales pueden agruparse por curso LTI:

```python
# En reports router
@router.get("/course/{lti_context_id}/report")
async def get_course_report(
    lti_context_id: str,
    db: Session = Depends(get_db)
):
    """Obtener reporte agregado del curso"""

    # Buscar todas las sesiones LTI del curso
    lti_sessions = db.query(LTISessionDB).filter(
        LTISessionDB.lti_context_id == lti_context_id
    ).all()

    session_ids = [s.session_id for s in lti_sessions if s.session_id]

    # Generar reporte agregado
    return course_report_service.generate(session_ids)
```

---

## 10. LTI Advantage Services

### 10.1 Assignment and Grade Services (AGS)

LTI-AGS permite enviar calificaciones de vuelta a Moodle.

```python
@router.post("/grades/{session_id}")
async def submit_grade(
    session_id: str,
    score: float,  # 0.0 - 1.0
    db: Session = Depends(get_db)
):
    """
    Enviar calificacion a Moodle via LTI-AGS.
    """
    # Obtener sesion LTI
    lti_session = db.query(LTISessionDB).filter(
        LTISessionDB.session_id == session_id
    ).first()

    if not lti_session or not lti_session.launch_token:
        raise HTTPException(status_code=404, detail="LTI session not found")

    # Decodificar launch token para obtener AGS endpoint
    claims = jwt.decode(
        lti_session.launch_token,
        options={"verify_signature": False}
    )

    ags_claim = claims.get("https://purl.imsglobal.org/spec/lti-ags/claim/endpoint")
    if not ags_claim:
        raise HTTPException(status_code=400, detail="AGS not supported")

    # Obtener access token
    deployment = lti_session.deployment
    access_token = await get_ags_access_token(deployment)

    # Enviar calificacion
    score_payload = {
        "userId": lti_session.lti_user_id,
        "scoreGiven": score * 100,  # Moodle espera 0-100
        "scoreMaximum": 100,
        "activityProgress": "Completed",
        "gradingProgress": "FullyGraded",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            ags_claim["lineitem"] + "/scores",
            json=score_payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/vnd.ims.lis.v1.score+json"
            }
        )
        response.raise_for_status()

    return {"status": "submitted", "score": score}
```

### 10.2 Names and Role Provisioning Services (NRPS)

Para obtener lista de estudiantes del curso:

```python
@router.get("/course/{lti_context_id}/members")
async def get_course_members(
    lti_context_id: str,
    db: Session = Depends(get_db)
):
    """
    Obtener miembros del curso via LTI-NRPS.
    """
    # Similar a AGS, usar el claim NRPS del launch token
    # para obtener la lista de miembros
    pass
```

---

## 11. Seguridad y Gobernanza

### 11.1 Consideraciones de Seguridad

| Aspecto | Medida |
|---------|--------|
| **Transporte** | Solo HTTPS |
| **State** | UUID aleatorio, expira en 10 min |
| **Nonce** | Uso unico, validado |
| **JWT** | Validacion completa de firma |
| **Claves** | RSA 2048+ bits |
| **Tokens** | Almacenados encriptados |

### 11.2 Validaciones de Gobernanza

GOV-IA aplica validaciones adicionales para sesiones LTI:

```python
class LTIGovernancePolicy:
    """
    Politicas especificas para sesiones LTI
    """

    def validate_launch(self, claims: Dict[str, Any]) -> ComplianceResult:
        """Validar launch antes de crear sesion"""

        # 1. Verificar que el deployment esta activo
        if not self.deployment_active(claims["deployment_id"]):
            return ComplianceResult(
                status=ComplianceStatus.VIOLATION,
                reason="Deployment inactivo o revocado"
            )

        # 2. Verificar roles permitidos
        roles = claims.get("roles", [])
        if not self.has_allowed_role(roles):
            return ComplianceResult(
                status=ComplianceStatus.VIOLATION,
                reason="Rol no autorizado para acceder"
            )

        # 3. Verificar limites de uso
        if self.exceeded_usage_limits(claims["sub"]):
            return ComplianceResult(
                status=ComplianceStatus.WARNING,
                reason="Limite de uso cercano"
            )

        return ComplianceResult(status=ComplianceStatus.COMPLIANT)
```

### 11.3 Auditoria de Launches LTI

```python
# En la tabla de auditoria
class LTIAuditLog(Base):
    """Registro de todos los launches LTI para auditoria"""

    __tablename__ = "lti_audit_log"

    id = Column(String(36), primary_key=True)
    deployment_id = Column(String(36), nullable=False)
    lti_user_id = Column(String(255), nullable=False)
    lti_context_id = Column(String(255), nullable=True)
    resource_link_id = Column(String(255), nullable=False)
    launch_type = Column(String(50), nullable=False)  # LtiResourceLinkRequest
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 12. Pruebas y Validacion

### 12.1 Herramientas de Prueba

| Herramienta | URL | Uso |
|-------------|-----|-----|
| **IMS LTI Reference Implementation** | https://lti-ri.imsglobal.org | Test completo LTI 1.3 |
| **Moodle Test Site** | https://sandbox.moodledemo.net | Moodle de prueba |
| **JWT.io** | https://jwt.io | Depurar tokens JWT |

### 12.2 Tests Unitarios

```python
# tests/test_lti.py

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.database.models import LTIDeploymentDB

client = TestClient(app)


@pytest.fixture
def mock_deployment(db_session):
    """Crear deployment de prueba"""
    deployment = LTIDeploymentDB(
        platform_name="Test Moodle",
        issuer="https://test-moodle.edu",
        client_id="test-client-123",
        deployment_id="1",
        auth_login_url="https://test-moodle.edu/mod/lti/auth.php",
        auth_token_url="https://test-moodle.edu/mod/lti/token.php",
        public_keyset_url="https://test-moodle.edu/mod/lti/certs.php",
        is_active=True
    )
    db_session.add(deployment)
    db_session.commit()
    return deployment


def test_lti_login_unknown_issuer():
    """Test login con issuer desconocido"""
    response = client.get(
        "/api/v1/lti/login",
        params={
            "iss": "https://unknown.edu",
            "login_hint": "user123",
            "target_link_uri": "https://ai-native.com/lti/launch"
        }
    )
    assert response.status_code == 400
    assert "Unknown issuer" in response.json()["detail"]


def test_lti_login_valid_issuer(mock_deployment):
    """Test login con issuer valido"""
    response = client.get(
        "/api/v1/lti/login",
        params={
            "iss": "https://test-moodle.edu",
            "login_hint": "user123",
            "target_link_uri": "https://ai-native.com/lti/launch"
        },
        allow_redirects=False
    )
    assert response.status_code == 302
    assert "auth.php" in response.headers["location"]


def test_lti_jwks():
    """Test JWKS endpoint"""
    response = client.get("/api/v1/lti/jwks")
    assert response.status_code == 200
    data = response.json()
    assert "keys" in data
    assert len(data["keys"]) > 0
    assert data["keys"][0]["kty"] == "RSA"


def test_lti_launch_invalid_state():
    """Test launch con state invalido"""
    response = client.post(
        "/api/v1/lti/launch",
        data={
            "id_token": "fake.jwt.token",
            "state": "invalid-state"
        }
    )
    assert response.status_code == 400
    assert "Invalid or expired state" in response.json()["detail"]
```

### 12.3 Test de Integracion Manual

1. **Configurar Moodle sandbox**
2. **Registrar AI-Native como tool**
3. **Crear actividad en un curso**
4. **Hacer click como estudiante**
5. **Verificar:**
   - Redireccion correcta a AI-Native
   - Sesion creada en BD
   - Usuario identificado correctamente
   - Curso/actividad mapeados

---

## 13. Troubleshooting

### 13.1 Errores Comunes

| Error | Causa | Solucion |
|-------|-------|----------|
| "Unknown issuer" | Issuer no registrado | Verificar URL exacta en lti_deployments |
| "Invalid state" | State expirado o Redis caido | Verificar Redis, aumentar TTL |
| "Token validation failed" | JWKS no accesible o expirado | Verificar URL JWKS, limpiar cache |
| "Nonce mismatch" | Replay attack o bug | Verificar que nonce se guarda/recupera correctamente |
| "Client ID mismatch" | Configuracion incorrecta | Verificar client_id en Moodle y BD |

### 13.2 Logs de Depuracion

```python
import logging

logger = logging.getLogger("lti")
logger.setLevel(logging.DEBUG)

# En lti_login
logger.debug(f"LTI Login: issuer={iss}, login_hint={login_hint}")
logger.debug(f"Found deployment: {deployment.id if deployment else 'None'}")

# En lti_launch
logger.debug(f"LTI Launch: state={state}")
logger.debug(f"JWT claims: {json.dumps(claims, indent=2)}")
```

### 13.3 Verificar Configuracion

```bash
# Verificar claves RSA
openssl rsa -in keys/private.pem -check
openssl rsa -pubin -in keys/public.pem -text

# Verificar conectividad con Moodle
curl -I https://your-moodle.edu/mod/lti/certs.php

# Verificar deployment en BD
psql -c "SELECT * FROM lti_deployments WHERE is_active = true;"

# Verificar Redis
redis-cli ping
redis-cli keys "lti_state:*"
```

---

## 14. Referencias

### 14.1 Especificaciones LTI

- [IMS LTI 1.3 Specification](https://www.imsglobal.org/spec/lti/v1p3/)
- [LTI Advantage](https://www.imsglobal.org/lti-advantage-overview)
- [LTI Security Framework](https://www.imsglobal.org/spec/security/v1p0/)

### 14.2 Documentacion Moodle

- [Moodle LTI Provider](https://docs.moodle.org/en/LTI_and_Moodle)
- [External Tool Settings](https://docs.moodle.org/en/External_tool_settings)

### 14.3 Librerias Recomendadas

| Libreria | Uso | URL |
|----------|-----|-----|
| **PyJWT** | Manejo de JWT | https://pyjwt.readthedocs.io |
| **python-jose** | Alternativa JWT con JWKS | https://python-jose.readthedocs.io |
| **pylti1.3** | Libreria LTI completa | https://github.com/dmitry-viskov/pylti1.3 |

---

## Apendice A: Checklist de Implementacion

- [ ] Generar par de claves RSA
- [ ] Configurar variables de entorno LTI
- [ ] Crear router `backend/api/routers/lti.py`
- [ ] Registrar router en `main.py`
- [ ] Configurar deployment en BD
- [ ] Configurar Moodle como platform
- [ ] Probar flujo OIDC completo
- [ ] Implementar AGS (opcional)
- [ ] Configurar auditoria LTI
- [ ] Tests de integracion

---

## Apendice B: Ejemplo de Configuracion Completa

### `.env` completo para LTI

```bash
# =============================================================================
# LTI 1.3 Configuration - AI-Native MVP
# =============================================================================

# Tool Identity
LTI_TOOL_ISSUER=https://ai-native.universidad.edu

# Keys (generate with: make generate-lti-keys)
LTI_PRIVATE_KEY_PATH=/app/keys/private.pem
LTI_PUBLIC_KEY_PATH=/app/keys/public.pem

# Frontend redirect
LTI_SUCCESS_REDIRECT=https://ai-native.universidad.edu/app

# Cache settings
LTI_STATE_EXPIRATION=600
LTI_JWKS_CACHE_TTL=3600

# Logging
LTI_DEBUG=true
```

---

**Documento creado**: Diciembre 2025
**Autor**: Claude Code (Analisis Tecnico)
**Proyecto**: AI-Native MVP - Tesis Doctoral
**Historia de Usuario**: HU-SYS-010