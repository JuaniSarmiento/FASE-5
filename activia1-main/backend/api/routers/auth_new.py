"""
New Authentication endpoints using User model with roles

Endpoints:
- POST /auth/login: JSON login (frontend compatible)
- POST /auth/token: OAuth2 FormData login (Swagger compatible)
- POST /auth/register: Register new user
- POST /auth/refresh: Refresh access token
- GET /auth/me: Get current user info
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import timedelta

from backend.database.config import get_db
# FIX Cortez25: Use UserDB from database.models to avoid duplicate table definition
from backend.database.models import UserDB as User
from backend.models.user import UserRole
from backend.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from ..schemas.common import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# Refresh token expiration (longer than access token)
REFRESH_TOKEN_EXPIRE_DAYS = 30


# =============================================================================
# SCHEMAS
# =============================================================================

class UserRegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "student"


class UserResponseSchema(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    roles: List[str]
    is_active: bool
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokensSchema(BaseModel):
    """Token pair for access and refresh"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class UserWithTokensResponse(BaseModel):
    """Combined user and tokens response - matches frontend expectation"""
    user: UserResponseSchema
    tokens: TokensSchema


class LoginRequest(BaseModel):
    """JSON login request - matches frontend auth.service.ts"""
    email: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

# Dependency to get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _create_token_pair(user_id: str) -> TokensSchema:
    """Create access and refresh token pair"""
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_access_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return TokensSchema(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


def _user_to_response(user: User) -> UserResponseSchema:
    """Convert User ORM model to response schema"""
    return UserResponseSchema(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        roles=user.roles or [],
        is_active=user.is_active,
        created_at=user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None
    )


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post(
    "/register",
    response_model=APIResponse[UserWithTokensResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user and return user info with tokens"
)
async def register(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    """
    Register a new user.

    Returns APIResponse with { user, tokens } structure matching frontend expectation.
    """
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        roles=[user_data.role] if user_data.role in [r.value for r in UserRole] else ["student"],
        is_active=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Create token pair
    tokens = _create_token_pair(user.id)

    return APIResponse(
        success=True,
        data=UserWithTokensResponse(
            user=_user_to_response(user),
            tokens=tokens
        ),
        message="User registered successfully"
    )


@router.post(
    "/login",
    response_model=APIResponse[UserWithTokensResponse],
    summary="Login with JSON (frontend compatible)",
    description="Login with email and password in JSON body. Returns user info with tokens."
)
async def login_json(
    credentials: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login with JSON body - matches frontend auth.service.ts expectation.

    Request body: { email: string, password: string }
    Response: APIResponse[{ user: User, tokens: { access_token, refresh_token, token_type } }]
    """
    import logging
    logger = logging.getLogger(__name__)

    # Try to find user by email or username
    user = db.query(User).filter(
        (User.email == credentials.email) | (User.username == credentials.email)
    ).first()

    logger.info(f"Login attempt: email={credentials.email}, user_found={user is not None}")

    if not user:
        logger.warning(f"User not found: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f"User found: {user.email}, checking password...")
    password_valid = verify_password(credentials.password, user.hashed_password)
    logger.info(f"Password verification result: {password_valid}")

    if not password_valid:
        logger.warning(f"Invalid password for user: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create token pair
    tokens = _create_token_pair(user.id)

    return APIResponse(
        success=True,
        data=UserWithTokensResponse(
            user=_user_to_response(user),
            tokens=tokens
        ),
        message="Login successful"
    )


@router.post(
    "/token",
    response_model=TokenSchema,
    summary="Login with OAuth2 FormData (Swagger compatible)",
    description="OAuth2 compatible login endpoint for Swagger UI testing"
)
async def login_oauth2(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible login with FormData.

    This endpoint is maintained for Swagger UI compatibility.
    For frontend, use POST /auth/login with JSON body.
    """
    # Try to find user by email or username
    user = db.query(User).filter(
        (User.email == form_data.username) | (User.username == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create access token only (OAuth2 standard)
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post(
    "/refresh",
    response_model=APIResponse[TokensSchema],
    summary="Refresh access token",
    description="Use refresh token to get a new access token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.

    Request body: { refresh_token: string }
    Response: APIResponse[{ access_token, refresh_token, token_type }]
    """
    # Decode refresh token
    payload = decode_access_token(request.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type - not a refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token - no user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists and is active
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create new token pair
    tokens = _create_token_pair(user.id)

    return APIResponse(
        success=True,
        data=tokens,
        message="Token refreshed successfully"
    )


@router.get(
    "/me",
    response_model=APIResponse[UserResponseSchema],
    summary="Get current user",
    description="Get current authenticated user information"
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return APIResponse(
        success=True,
        data=_user_to_response(current_user),
        message="User retrieved successfully"
    )
