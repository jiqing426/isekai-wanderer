"""Configuration tests."""

import pytest
from app.core.config import settings


def test_settings_load():
    """Test that settings load successfully."""
    assert settings.app_name is not None
    assert settings.app_version is not None
    assert settings.backend_port == 8000


def test_cors_origins():
    """Test CORS origins parsing."""
    origins = settings.cors_origins_list
    assert isinstance(origins, list)
    assert len(origins) > 0


def test_database_url():
    """Test database URL is set."""
    assert settings.database_url is not None
    assert "postgresql" in settings.database_url or "sqlite" in settings.database_url


def test_jwt_settings():
    """Test JWT configuration."""
    assert settings.jwt_secret is not None
    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_access_token_expire_minutes == 15
    assert settings.jwt_refresh_token_expire_days == 7


def test_rate_limit_settings():
    """Test rate limiting configuration."""
    assert settings.api_rate_limit == 60
    assert settings.llm_rate_limit == 10
