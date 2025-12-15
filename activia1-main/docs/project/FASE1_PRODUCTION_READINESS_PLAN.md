# FASE 1: PRODUCTION READINESS - PLAN DE IMPLEMENTACIÓN

**Fecha inicio**: 2025-11-21
**Duración estimada**: 8-9 días (67 horas)
**Objetivo**: Sistema listo para despliegue en staging con seguridad, escalabilidad y observabilidad

---

## 📋 OVERVIEW

Esta fase implementa las **7 correcciones críticas** identificadas en el análisis arquitectónico:

| Task | Severidad | Esfuerzo | Status |
|------|-----------|----------|--------|
| P1.1: JWT Authentication | CRÍTICO | 16h | 🔴 TODO |
| P1.2: Redis Cache Migration | CRÍTICO | 8h | 🔴 TODO |
| P1.3: DB Connection Pooling | ALTO | 3h | 🔴 TODO |
| P1.4: Refactor AIGateway | ALTO | 8h | 🔴 TODO |
| P1.5: Docker Configuration | CRÍTICO | 8h | 🔴 TODO |
| P1.6: CI/CD Pipeline | CRÍTICO | 6h | 🔴 TODO |
| P1.7: Monitoring Stack | CRÍTICO | 18h | 🔴 TODO |
| **TOTAL** | | **67h** | |

---

## 🔐 P1.1: JWT AUTHENTICATION IMPLEMENTATION (16h)

### Objetivo
Reemplazar el stub de autenticación con implementación JWT real + RBAC

### Componentes a Crear

#### 1. User Model (2h)

**Archivo**: `src/ai_native_mvp/database/models.py`

```python
class UserDB(Base, BaseModel):
    """User model for authentication"""

    __tablename__ = "users"

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(255), nullable=True)
    student_id = Column(String(100), nullable=True, unique=True, index=True)

    # Authorization
    roles = Column(JSON, default=list, nullable=False)  # ["student", "instructor", "admin"]
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Metadata
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0)

    # Relationships
    sessions = relationship("SessionDB", back_populates="user", foreign_keys="SessionDB.user_id")

    __table_args__ = (
        Index('idx_email_active', 'email', 'is_active'),
        Index('idx_username_active', 'username', 'is_active'),
    )

# Add to SessionDB
class SessionDB(Base, BaseModel):
    # ... existing fields
    user_id = Column(String(100), ForeignKey('users.id'), nullable=True, index=True)  # NEW
    user = relationship("UserDB", back_populates="sessions")  # NEW
```

#### 2. User Repository (1h)

**Archivo**: `src/ai_native_mvp/database/repositories.py`

```python
class UserRepository:
    """Repository for user operations"""

    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, email: str, username: str, hashed_password: str,
               full_name: str, roles: List[str]) -> UserDB:
        """Create new user"""
        user = UserDB(
            id=str(uuid4()),
            email=email.lower(),
            username=username,
            hashed_password=hashed_password,
            full_name=full_name,
            roles=roles,
            is_active=True,
            is_verified=False
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> Optional[UserDB]:
        """Get user by email"""
        return self.db.query(UserDB)\
            .filter(UserDB.email == email.lower())\
            .filter(UserDB.is_active == True)\
            .first()

    def get_by_username(self, username: str) -> Optional[UserDB]:
        """Get user by username"""
        return self.db.query(UserDB)\
            .filter(UserDB.username == username)\
            .filter(UserDB.is_active == True)\
            .first()

    def get_by_id(self, user_id: str) -> Optional[UserDB]:
        """Get user by ID"""
        return self.db.query(UserDB)\
            .filter(UserDB.id == user_id)\
            .filter(UserDB.is_active == True)\
            .first()

    def update_last_login(self, user_id: str):
        """Update last login timestamp"""
        user = self.get_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            user.login_count += 1
            self.db.commit()

    def verify_user(self, user_id: str):
        """Mark user as verified"""
        user = self.get_by_id(user_id)
        if user:
            user.is_verified = True
            self.db.commit()
```

#### 3. Security Module (3h)

**Archivo**: `src/ai_native_mvp/api/security.py` (NUEVO)

```python
"""
Security utilities for JWT authentication and password hashing
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

# Configuration from environment
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))  # 30 min
REFRESH_TOKEN_EXPIRATION_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", "7"))  # 7 days

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash

    Args:
        plain_password: Plain text password from user
        hashed_password: Stored hashed password

    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token

    Args:
        data: Payload to encode (should include 'sub' for user ID)
        expires_delta: Custom expiration time

    Returns:
        str: Encoded JWT token

    Example:
        token = create_access_token(
            data={"sub": user.id, "roles": user.roles}
        )
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str) -> str:
    """
    Create JWT refresh token (longer expiration)

    Args:
        user_id: User identifier

    Returns:
        str: Encoded refresh token
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)

    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token

    Args:
        token: JWT token string

    Returns:
        dict: Decoded payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def validate_token_type(payload: Dict[str, Any], expected_type: str):
    """
    Validate token type (access vs refresh)

    Args:
        payload: Decoded JWT payload
        expected_type: Expected token type ("access" or "refresh")

    Raises:
        HTTPException: If token type doesn't match
    """
    token_type = payload.get("type")
    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected {expected_type}, got {token_type}",
        )
```

#### 4. Updated Authentication Dependencies (2h)

**Archivo**: `src/ai_native_mvp/api/deps.py` (MODIFICAR)

```python
from typing import Optional
import logging

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .security import decode_token, validate_token_type
from ..database.repositories import UserRepository

logger = logging.getLogger(__name__)


async def get_current_user(
    authorization: Optional[str] = Header(None, description="Bearer token")
) -> dict:
    """
    Dependency para obtener usuario autenticado desde JWT

    Production: Valida JWT y obtiene usuario desde base de datos
    Development: Modo permisivo (si ENVIRONMENT != production)

    Args:
        authorization: Header Authorization con Bearer token

    Returns:
        dict: Usuario autenticado con id, email, username, roles

    Raises:
        HTTPException: Si token inválido o usuario no existe
    """
    import os

    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    if ENVIRONMENT == "production":
        # ✅ PRODUCTION: JWT validation estricto
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Please provide a valid token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = authorization.replace("Bearer ", "")

        # Decode and validate JWT
        payload = decode_token(token)
        validate_token_type(payload, "access")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )

        # Verify user exists and is active
        from ..database import get_db_session
        with get_db_session() as db:
            user_repo = UserRepository(db)
            user = user_repo.get_by_id(user_id)

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )

            logger.info(
                "User authenticated successfully",
                extra={"user_id": user.id, "username": user.username}
            )

            return {
                "id": user.id,
                "user_id": user.id,  # Backward compatibility
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "roles": user.roles,
                "is_verified": user.is_verified
            }

    else:
        # ✅ DEVELOPMENT: Modo permisivo
        logger.debug("Development mode - permissive authentication")

        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")

            try:
                # Try to decode token if provided
                payload = decode_token(token)
                user_id = payload.get("sub", "dev_user")
                roles = payload.get("roles", ["student", "instructor"])
            except:
                # If token invalid, use dev defaults
                user_id = "dev_user"
                roles = ["student", "instructor"]

            return {
                "id": user_id,
                "user_id": user_id,
                "email": "dev@example.com",
                "username": "developer",
                "full_name": "Developer User",
                "roles": roles,
                "is_verified": True
            }

        # No token provided in development
        return {
            "id": "anonymous",
            "user_id": "anonymous",
            "email": "anonymous@example.com",
            "username": "anonymous",
            "full_name": "Anonymous User",
            "roles": ["student"],
            "is_verified": False
        }


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    Dependency para obtener usuario activo (verificado)

    Args:
        current_user: Usuario autenticado

    Returns:
        dict: Usuario activo

    Raises:
        HTTPException: Si usuario no está verificado (en producción)
    """
    import os

    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    if ENVIRONMENT == "production" and not current_user.get("is_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email before accessing this resource."
        )

    return current_user


def require_role(required_role: str):
    """
    Dependency factory para requerir un rol específico

    Args:
        required_role: Rol requerido (student, instructor, admin)

    Returns:
        Dependency function

    Example:
        require_instructor = Depends(require_role("instructor"))

        @app.post("/evaluations")
        async def create_evaluation(user: dict = require_instructor):
            # Only instructors can access
            ...
    """
    async def role_checker(current_user: dict = Depends(get_current_active_user)) -> dict:
        user_roles = current_user.get("roles", [])

        if required_role not in user_roles:
            logger.warning(
                f"Access denied - insufficient permissions",
                extra={
                    "user_id": current_user.get("id"),
                    "required_role": required_role,
                    "user_roles": user_roles
                }
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required role: {required_role}. Your roles: {', '.join(user_roles)}"
            )

        return current_user

    return role_checker


def require_any_role(*required_roles: str):
    """
    Dependency factory para requerir AL MENOS uno de los roles especificados

    Args:
        *required_roles: Roles requeridos (al menos uno debe coincidir)

    Returns:
        Dependency function

    Example:
        require_staff = Depends(require_any_role("instructor", "admin"))

        @app.post("/activities")
        async def create_activity(user: dict = require_staff):
            # Instructors OR admins can access
            ...
    """
    async def role_checker(current_user: dict = Depends(get_current_active_user)) -> dict:
        user_roles = current_user.get("roles", [])

        if not any(role in user_roles for role in required_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required one of: {', '.join(required_roles)}. Your roles: {', '.join(user_roles)}"
            )

        return current_user

    return role_checker
```

#### 5. Auth API Schemas (1h)

**Archivo**: `src/ai_native_mvp/api/schemas/auth.py` (NUEVO)

```python
"""
Pydantic schemas for authentication endpoints
"""
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=8, max_length=100, description="Password (min 8 characters)")
    full_name: str = Field(..., min_length=2, max_length=255, description="Full name")
    student_id: Optional[str] = Field(None, max_length=100, description="Student ID (optional)")

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

    @validator('username')
    def username_alphanumeric(cls, v):
        """Validate username format"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (underscores and hyphens allowed)')
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="JWT refresh token")


class UserResponse(BaseModel):
    """User information response"""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    student_id: Optional[str]
    roles: List[str]
    is_active: bool
    is_verified: bool
    created_at: str

    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Password change request"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")

    @validator('new_password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
```

#### 6. Auth Router (3h)

**Archivo**: `src/ai_native_mvp/api/routers/auth.py` (NUEVO)

```python
"""
Authentication endpoints: login, register, refresh token
"""
import logging
from datetime import timedelta
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..deps import get_db, get_current_user, get_current_active_user
from ..schemas.auth import (
    UserRegister, UserLogin, TokenResponse, RefreshTokenRequest,
    UserResponse, PasswordChange
)
from ..schemas.common import APIResponse
from ..security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token, validate_token_type,
    JWT_EXPIRATION_MINUTES
)
from ...database.repositories import UserRepository

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new user account with email and password"
)
async def register(
    data: UserRegister,
    db: Session = Depends(get_db)
) -> APIResponse[UserResponse]:
    """
    Register a new user

    - **email**: Valid email address (must be unique)
    - **username**: Alphanumeric username (must be unique)
    - **password**: Minimum 8 characters with uppercase, lowercase, and digit
    - **full_name**: User's full name
    - **student_id**: Optional student identifier

    Returns user information without password
    """
    user_repo = UserRepository(db)

    # Check if email already exists
    existing_user = user_repo.get_by_email(data.email)
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_user = user_repo.get_by_username(data.username)
    if existing_user:
        logger.warning(f"Registration attempt with existing username: {data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Hash password
    hashed_password = hash_password(data.password)

    # Create user with "student" role by default
    user = user_repo.create(
        email=data.email,
        username=data.username,
        hashed_password=hashed_password,
        full_name=data.full_name,
        roles=["student"]  # Default role
    )

    # TODO: Send email verification

    logger.info(
        "User registered successfully",
        extra={
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }
    )

    return APIResponse(
        success=True,
        data=UserResponse.model_validate(user),
        message=f"User {user.username} registered successfully. Please verify your email."
    )


@router.post(
    "/login",
    response_model=APIResponse[TokenResponse],
    summary="Login",
    description="Authenticate user and return JWT tokens"
)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
) -> APIResponse[TokenResponse]:
    """
    Authenticate user and return JWT access + refresh tokens

    - **email**: Registered email address
    - **password**: User password

    Returns JWT tokens for authenticated requests
    """
    user_repo = UserRepository(db)

    # Get user by email
    user = user_repo.get_by_email(credentials.email)
    if not user:
        logger.warning(f"Login attempt with non-existent email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, user.hashed_password):
        logger.warning(
            f"Failed login attempt for user {user.username}",
            extra={"user_id": user.id, "email": credentials.email}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create tokens
    access_token = create_access_token(
        data={"sub": user.id, "roles": user.roles}
    )
    refresh_token = create_refresh_token(user.id)

    # Update last login
    user_repo.update_last_login(user.id)

    logger.info(
        "User logged in successfully",
        extra={
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }
    )

    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=JWT_EXPIRATION_MINUTES * 60  # Convert to seconds
        ),
        message="Login successful"
    )


@router.post(
    "/refresh",
    response_model=APIResponse[TokenResponse],
    summary="Refresh Token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> APIResponse[TokenResponse]:
    """
    Refresh access token using refresh token

    - **refresh_token**: Valid JWT refresh token

    Returns new access token (refresh token remains the same)
    """
    # Decode and validate refresh token
    payload = decode_token(data.refresh_token)
    validate_token_type(payload, "refresh")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Verify user still exists and is active
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    # Create new access token
    access_token = create_access_token(
        data={"sub": user.id, "roles": user.roles}
    )

    logger.info(
        "Token refreshed successfully",
        extra={"user_id": user.id}
    )

    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=access_token,
            refresh_token=data.refresh_token,  # Same refresh token
            token_type="bearer",
            expires_in=JWT_EXPIRATION_MINUTES * 60
        ),
        message="Token refreshed successfully"
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponse],
    summary="Get Current User",
    description="Get authenticated user information"
)
async def get_me(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> APIResponse[UserResponse]:
    """
    Get current authenticated user information

    Requires valid JWT token in Authorization header
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return APIResponse(
        success=True,
        data=UserResponse.model_validate(user)
    )


@router.post(
    "/change-password",
    response_model=APIResponse[Dict],
    summary="Change Password",
    description="Change user password (requires authentication)"
)
async def change_password(
    data: PasswordChange,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> APIResponse[Dict]:
    """
    Change user password

    - **current_password**: Current password for verification
    - **new_password**: New password (min 8 chars with complexity requirements)

    Requires valid JWT token
    """
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(current_user["id"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify current password
    if not verify_password(data.current_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    # Hash and update new password
    user.hashed_password = hash_password(data.new_password)
    db.commit()

    logger.info(
        "Password changed successfully",
        extra={"user_id": user.id}
    )

    return APIResponse(
        success=True,
        data={"message": "Password changed successfully"},
        message="Password changed successfully. Please login with your new password."
    )


@router.post(
    "/logout",
    response_model=APIResponse[Dict],
    summary="Logout",
    description="Logout user (client should discard tokens)"
)
async def logout(
    current_user: dict = Depends(get_current_user)
) -> APIResponse[Dict]:
    """
    Logout user

    Note: JWTs are stateless, so we can't invalidate tokens server-side.
    Client should discard tokens after logout.

    For production: Implement token blacklist with Redis if needed.
    """
    logger.info(
        "User logged out",
        extra={"user_id": current_user["id"]}
    )

    return APIResponse(
        success=True,
        data={"message": "Logged out successfully"},
        message="Logged out successfully. Please discard your tokens."
    )
```

#### 7. Update requirements.txt (5 min)

```txt
# Add to requirements.txt:
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6  # For form data
```

#### 8. Update .env.example (5 min)

```bash
# Authentication (JWT)
JWT_SECRET=your-secret-key-change-in-production-use-openssl-rand-hex-32
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
REFRESH_TOKEN_EXPIRATION_DAYS=7

# Environment
ENVIRONMENT=development  # development, staging, production
```

#### 9. Database Migration Script (1h)

**Archivo**: `scripts/create_users_table.py` (NUEVO)

```python
"""
Create users table in existing database
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_native_mvp.database import init_database
from src.ai_native_mvp.database.models import UserDB
from src.ai_native_mvp.api.security import hash_password

def create_users_table():
    """Create users table and add admin user"""
    # Initialize database (creates all tables)
    db_config = init_database(create_tables=True)

    print("✅ Users table created successfully")

    # Create default admin user
    from src.ai_native_mvp.database import get_db_session
    from src.ai_native_mvp.database.repositories import UserRepository

    with get_db_session() as session:
        user_repo = UserRepository(session)

        # Check if admin exists
        admin = user_repo.get_by_email("admin@ai-native.com")

        if not admin:
            admin = user_repo.create(
                email="admin@ai-native.com",
                username="admin",
                hashed_password=hash_password("Admin123!"),
                full_name="System Administrator",
                roles=["admin", "instructor", "student"]
            )
            print(f"✅ Admin user created: {admin.email}")
            print(f"   Username: admin")
            print(f"   Password: Admin123!")
        else:
            print(f"ℹ️  Admin user already exists: {admin.email}")

if __name__ == "__main__":
    create_users_table()
```

#### 10. Testing Script (1h)

**Archivo**: `examples/test_auth_flow.py` (NUEVO)

```python
"""
Test authentication flow: register → login → access protected endpoint
"""
import requests
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

API_BASE = "http://localhost:8000/api/v1"

def test_auth_flow():
    """Test complete authentication flow"""
    print("🔐 Testing Authentication Flow\n")

    # 1. Register new user
    print("1. Registering new user...")
    register_response = requests.post(f"{API_BASE}/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123!",
        "full_name": "Test User",
        "student_id": "student_test_001"
    })

    if register_response.status_code == 201:
        print("   ✅ User registered successfully")
        user = register_response.json()["data"]
        print(f"   User ID: {user['id']}")
        print(f"   Username: {user['username']}")
    else:
        print(f"   ❌ Registration failed: {register_response.json()}")
        return

    # 2. Login
    print("\n2. Logging in...")
    login_response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "test@example.com",
        "password": "Test123!"
    })

    if login_response.status_code == 200:
        print("   ✅ Login successful")
        tokens = login_response.json()["data"]
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        print(f"   Access token (first 20 chars): {access_token[:20]}...")
        print(f"   Expires in: {tokens['expires_in']} seconds")
    else:
        print(f"   ❌ Login failed: {login_response.json()}")
        return

    # 3. Access protected endpoint (Get current user)
    print("\n3. Accessing protected endpoint /auth/me...")
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = requests.get(f"{API_BASE}/auth/me", headers=headers)

    if me_response.status_code == 200:
        print("   ✅ Protected endpoint accessed successfully")
        user = me_response.json()["data"]
        print(f"   Username: {user['username']}")
        print(f"   Email: {user['email']}")
        print(f"   Roles: {', '.join(user['roles'])}")
    else:
        print(f"   ❌ Access denied: {me_response.json()}")
        return

    # 4. Create session (protected endpoint)
    print("\n4. Creating session with authenticated user...")
    create_session_response = requests.post(
        f"{API_BASE}/sessions",
        headers=headers,
        json={
            "student_id": user["id"],
            "activity_id": "prog2_tp1",
            "mode": "TUTOR"
        }
    )

    if create_session_response.status_code == 200:
        print("   ✅ Session created successfully")
        session = create_session_response.json()["data"]
        print(f"   Session ID: {session['id']}")
    else:
        print(f"   ❌ Session creation failed: {create_session_response.json()}")

    # 5. Refresh token
    print("\n5. Refreshing access token...")
    refresh_response = requests.post(f"{API_BASE}/auth/refresh", json={
        "refresh_token": refresh_token
    })

    if refresh_response.status_code == 200:
        print("   ✅ Token refreshed successfully")
        new_tokens = refresh_response.json()["data"]
        new_access_token = new_tokens["access_token"]
        print(f"   New access token (first 20 chars): {new_access_token[:20]}...")
    else:
        print(f"   ❌ Token refresh failed: {refresh_response.json()}")

    # 6. Logout
    print("\n6. Logging out...")
    logout_response = requests.post(f"{API_BASE}/auth/logout", headers=headers)

    if logout_response.status_code == 200:
        print("   ✅ Logged out successfully")
    else:
        print(f"   ❌ Logout failed: {logout_response.json()}")

    print("\n✅ Authentication flow test completed!")

if __name__ == "__main__":
    print("Make sure API server is running: python scripts/run_api.py\n")
    input("Press Enter to start test...")
    test_auth_flow()
```

#### 11. Update main.py to include auth router (5 min)

**Archivo**: `src/ai_native_mvp/api/main.py` (MODIFICAR)

```python
# Add auth router
from .routers import health, sessions, interactions, traces, risks, auth  # NEW

# Include router
app.include_router(auth.router, prefix="/api/v1")  # NEW
```

### Implementation Checklist

- [ ] Step 1: Add User model to models.py (2h)
- [ ] Step 2: Add UserRepository to repositories.py (1h)
- [ ] Step 3: Create security.py module (3h)
- [ ] Step 4: Update deps.py with JWT auth (2h)
- [ ] Step 5: Create auth schemas (1h)
- [ ] Step 6: Create auth router (3h)
- [ ] Step 7: Update requirements.txt (5min)
- [ ] Step 8: Update .env.example (5min)
- [ ] Step 9: Create migration script (1h)
- [ ] Step 10: Create testing script (1h)
- [ ] Step 11: Update main.py (5min)
- [ ] Step 12: Run migration script
- [ ] Step 13: Run tests
- [ ] Step 14: Test with Postman/curl
- [ ] Step 15: Update documentation

### Testing Commands

```bash
# 1. Install dependencies
pip install python-jose[cryptography] passlib[bcrypt] python-multipart

# 2. Create users table and admin user
python scripts/create_users_table.py

# 3. Start API server
python scripts/run_api.py

# 4. Test auth flow
python examples/test_auth_flow.py

# 5. Manual test with curl
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test123!",
    "full_name": "Test User"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'

# Get current user (use token from login)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Success Criteria

✅ **P1.1 Complete** when:
1. User can register with email/password
2. User can login and receive JWT tokens
3. Protected endpoints validate JWT tokens
4. RBAC enforces role-based access (student, instructor, admin)
5. Password is hashed with bcrypt
6. Refresh token flow works
7. All tests pass
8. Documentation updated

---

## 🚀 Next Steps After P1.1

Once authentication is complete, proceed to:
- **P1.2**: Migrate cache to Redis (8h)
- **P1.3**: Configure DB connection pooling (3h)
- **P1.4**: Refactor AIGateway (8h)

---

**Estimated completion**: P1.1 can be completed in 2 working days (16 hours) by 1 developer.

¿Quieres que comience con la implementación paso a paso o prefieres revisar el plan completo primero?
