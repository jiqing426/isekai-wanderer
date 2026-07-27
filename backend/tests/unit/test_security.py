"""Security module tests - JWT and password hashing."""

import pytest
from datetime import timedelta
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "secure_password_123"
    hashed = get_password_hash(password)
    
    # Hash should be different from plain password
    assert hashed != password
    
    # Verification should work
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_access_token_creation():
    """Test JWT access token creation."""
    data = {"sub": "user-123"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_access_token_decode():
    """Test JWT access token decoding."""
    data = {"sub": "user-123"}
    token = create_access_token(data)
    decoded = decode_token(token)
    
    assert decoded is not None
    assert decoded["sub"] == "user-123"
    assert decoded["type"] == "access"


def test_refresh_token_creation():
    """Test JWT refresh token creation."""
    data = {"sub": "user-123"}
    token = create_refresh_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0


def test_refresh_token_decode():
    """Test JWT refresh token decoding."""
    data = {"sub": "user-123"}
    token = create_refresh_token(data)
    decoded = decode_token(token)
    
    assert decoded is not None
    assert decoded["sub"] == "user-123"
    assert decoded["type"] == "refresh"


def test_token_expiration():
    """Test token with custom expiration."""
    data = {"sub": "user-123"}
    expires = timedelta(minutes=5)
    token = create_access_token(data, expires_delta=expires)
    decoded = decode_token(token)
    
    assert decoded is not None
    assert "exp" in decoded


def test_invalid_token():
    """Test decoding invalid token."""
    decoded = decode_token("invalid.token.here")
    assert decoded is None


def test_token_with_extra_data():
    """Test token with additional claims."""
    data = {"sub": "user-123", "role": "admin", "email": "test@example.com"}
    token = create_access_token(data)
    decoded = decode_token(token)
    
    assert decoded is not None
    assert decoded["sub"] == "user-123"
    assert decoded["role"] == "admin"
    assert decoded["email"] == "test@example.com"
