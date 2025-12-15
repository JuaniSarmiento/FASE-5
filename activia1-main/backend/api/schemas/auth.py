"""
Pydantic schemas for authentication endpoints

Provides:
- UserRegister: Schema for user registration
- UserLogin: Schema for user login
- TokenResponse: Schema for token pair response
- UserResponse: Schema for user data response
- ChangePasswordRequest: Schema for password change
"""
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator


# === Authentication Request Schemas ===

class UserRegister(BaseModel):
    """Schema for user registration"""

    email: EmailStr = Field(
        ...,
        description="User email address (unique)",
        examples=["student@example.com"]
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (unique, 3-50 characters)",
        examples=["john_doe"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)",
        examples=["SecurePassword123!"]
    )
    full_name: Optional[str] = Field(
        None,
        max_length=255,
        description="User's full name",
        examples=["John Doe"]
    )
    student_id: Optional[str] = Field(
        None,
        max_length=100,
        description="Student ID (for linking to StudentProfileDB)",
        examples=["student_001"]
    )

    @validator("username")
    def validate_username(cls, v):
        """Validate username format"""
        if not v.isalnum() and "_" not in v:
            raise ValueError("Username must contain only alphanumeric characters and underscores")
        return v

    @validator("password")
    def validate_password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for at least one uppercase, one lowercase, and one digit
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, and one digit")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "username": "john_doe",
                "password": "SecurePassword123!",
                "full_name": "John Doe",
                "student_id": "student_001"
            }
        }


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["student@example.com"]
    )
    password: str = Field(
        ...,
        description="User password",
        examples=["SecurePassword123!"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john.doe@example.com",
                "password": "SecurePassword123!"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing access token"""

    refresh_token: str = Field(
        ...,
        description="Valid refresh token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class ChangePasswordRequest(BaseModel):
    """Schema for changing user password"""

    current_password: str = Field(
        ...,
        description="Current password for verification",
        examples=["OldPassword123!"]
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password (minimum 8 characters)",
        examples=["NewSecurePassword456!"]
    )

    @validator("new_password")
    def validate_new_password_strength(cls, v):
        """Validate new password strength"""
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)

        if not (has_upper and has_lower and has_digit):
            raise ValueError("New password must contain at least one uppercase letter, one lowercase letter, and one digit")

        return v

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "OldPassword123!",
                "new_password": "NewSecurePassword456!"
            }
        }


# === Authentication Response Schemas ===

class TokenResponse(BaseModel):
    """Schema for token pair response"""

    access_token: str = Field(
        ...,
        description="JWT access token (short-lived)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    refresh_token: str = Field(
        ...,
        description="JWT refresh token (long-lived)",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
        examples=["bearer"]
    )
    expires_in: Optional[int] = Field(
        None,
        description="Access token expiration time in seconds",
        examples=[1800]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class UserResponse(BaseModel):
    """Schema for user data response"""

    id: str = Field(..., description="User ID", examples=["user_123"])
    email: str = Field(..., description="User email", examples=["john.doe@example.com"])
    username: str = Field(..., description="Username", examples=["john_doe"])
    full_name: Optional[str] = Field(None, description="Full name", examples=["John Doe"])
    student_id: Optional[str] = Field(None, description="Student ID", examples=["student_001"])
    roles: List[str] = Field(..., description="User roles", examples=[["student"]])
    is_active: bool = Field(..., description="Is user active", examples=[True])
    is_verified: bool = Field(..., description="Is email verified", examples=[False])
    created_at: str = Field(..., description="Account creation timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "email": "john.doe@example.com",
                "username": "john_doe",
                "full_name": "John Doe",
                "student_id": "student_001",
                "roles": ["student"],
                "is_active": True,
                "is_verified": False,
                "created_at": "2025-01-15T10:30:00Z"
            }
        }


class UserWithTokenResponse(BaseModel):
    """Schema for user registration/login response with token"""

    user: UserResponse = Field(..., description="User data")
    tokens: TokenResponse = Field(..., description="Authentication tokens")

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": "user_123",
                    "email": "john.doe@example.com",
                    "username": "john_doe",
                    "full_name": "John Doe",
                    "student_id": "student_001",
                    "roles": ["student"],
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2025-01-15T10:30:00Z"
                },
                "tokens": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 1800
                }
            }
        }


class MessageResponse(BaseModel):
    """Schema for simple message response"""

    message: str = Field(..., description="Response message", examples=["Password changed successfully"])

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Password changed successfully"
            }
        }
