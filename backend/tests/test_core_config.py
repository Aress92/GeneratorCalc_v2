"""
Tests for core configuration functionality.

Testy dla funkcjonalności konfiguracji.
"""

import pytest
import os
from unittest.mock import patch

from app.core.config import Settings


class TestSettings:
    """Test application settings."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        # Test default values
        assert settings.API_V1_STR == "/api/v1"
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == "INFO"

    def test_database_url_validation(self):
        """Test database URL validation."""
        # Test with valid MySQL URL
        with patch.dict(os.environ, {"DATABASE_URL": "mysql+aiomysql://user:pass@localhost/db"}):
            settings = Settings()
            assert "mysql" in settings.DATABASE_URL

        # Test with SQLite URL
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///./test.db"}):
            settings = Settings()
            assert "sqlite" in settings.DATABASE_URL

    def test_cors_origins_parsing(self):
        """Test CORS origins parsing."""
        # Test single origin
        with patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": "http://localhost:3000"}):
            settings = Settings()
            assert len(settings.BACKEND_CORS_ORIGINS) == 1
            assert str(settings.BACKEND_CORS_ORIGINS[0]) == "http://localhost:3000"

        # Test multiple origins
        origins = "http://localhost:3000,http://127.0.0.1:3000,https://example.com"
        with patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": origins}):
            settings = Settings()
            assert len(settings.BACKEND_CORS_ORIGINS) == 3

    def test_allowed_hosts_parsing(self):
        """Test allowed hosts parsing."""
        # Test single host
        with patch.dict(os.environ, {"ALLOWED_HOSTS": "localhost"}):
            settings = Settings()
            assert "localhost" in settings.ALLOWED_HOSTS

        # Test multiple hosts
        hosts = "localhost,127.0.0.1,example.com"
        with patch.dict(os.environ, {"ALLOWED_HOSTS": hosts}):
            settings = Settings()
            assert len(settings.ALLOWED_HOSTS) == 3
            assert "localhost" in settings.ALLOWED_HOSTS
            assert "127.0.0.1" in settings.ALLOWED_HOSTS
            assert "example.com" in settings.ALLOWED_HOSTS

    def test_debug_mode(self):
        """Test debug mode settings."""
        # Test debug enabled
        with patch.dict(os.environ, {"DEBUG": "true"}):
            settings = Settings()
            assert settings.DEBUG is True

        # Test debug disabled
        with patch.dict(os.environ, {"DEBUG": "false"}):
            settings = Settings()
            assert settings.DEBUG is False

    def test_log_level_validation(self):
        """Test log level validation."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in valid_levels:
            with patch.dict(os.environ, {"LOG_LEVEL": level}):
                settings = Settings()
                assert settings.LOG_LEVEL == level

    def test_secret_key_requirement(self):
        """Test secret key validation."""
        # Test with custom secret key
        with patch.dict(os.environ, {"SECRET_KEY": "custom-secret-key-123"}):
            settings = Settings()
            assert settings.SECRET_KEY == "custom-secret-key-123"

        # Test default secret key
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            assert len(settings.SECRET_KEY) > 0

    def test_redis_url_configuration(self):
        """Test Redis URL configuration."""
        # Test custom Redis URL
        redis_url = "redis://localhost:6379/0"
        with patch.dict(os.environ, {"REDIS_URL": redis_url}):
            settings = Settings()
            assert settings.REDIS_URL == redis_url

        # Test Celery broker URL
        broker_url = "redis://localhost:6379/1"
        with patch.dict(os.environ, {"CELERY_BROKER_URL": broker_url}):
            settings = Settings()
            assert settings.CELERY_BROKER_URL == broker_url

    def test_email_configuration(self):
        """Test email configuration settings."""
        email_config = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_USER": "test@example.com",
            "SMTP_PASSWORD": "password123",
            "SMTP_TLS": "true"
        }

        with patch.dict(os.environ, email_config):
            settings = Settings()
            assert settings.SMTP_HOST == "smtp.example.com"
            assert settings.SMTP_PORT == 587
            assert settings.SMTP_USER == "test@example.com"
            assert settings.SMTP_TLS is True

    def test_file_upload_settings(self):
        """Test file upload configuration."""
        upload_config = {
            "MAX_UPLOAD_SIZE": "10485760",  # 10MB
            "ALLOWED_EXTENSIONS": "xlsx,csv,json"
        }

        with patch.dict(os.environ, upload_config):
            settings = Settings()
            assert settings.MAX_UPLOAD_SIZE == 10485760
            assert "xlsx" in settings.ALLOWED_EXTENSIONS
            assert "csv" in settings.ALLOWED_EXTENSIONS

    def test_optimization_settings(self):
        """Test optimization algorithm settings."""
        opt_config = {
            "MAX_OPTIMIZATION_TIME": "300",  # 5 minutes
            "DEFAULT_ALGORITHM": "SLSQP",
            "MAX_ITERATIONS": "1000"
        }

        with patch.dict(os.environ, opt_config):
            settings = Settings()
            assert settings.MAX_OPTIMIZATION_TIME == 300
            assert settings.DEFAULT_ALGORITHM == "SLSQP"
            assert settings.MAX_ITERATIONS == 1000

    def test_security_settings(self):
        """Test security-related settings."""
        security_config = {
            "ACCESS_TOKEN_EXPIRE_MINUTES": "120",
            "REFRESH_TOKEN_EXPIRE_DAYS": "7",
            "PASSWORD_MIN_LENGTH": "8",
            "REQUIRE_EMAIL_VERIFICATION": "true"
        }

        with patch.dict(os.environ, security_config):
            settings = Settings()
            assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 120
            assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
            assert settings.PASSWORD_MIN_LENGTH == 8
            assert settings.REQUIRE_EMAIL_VERIFICATION is True

    def test_monitoring_settings(self):
        """Test monitoring and metrics settings."""
        monitoring_config = {
            "ENABLE_METRICS": "true",
            "METRICS_PORT": "9090",
            "ENABLE_TRACING": "false"
        }

        with patch.dict(os.environ, monitoring_config):
            settings = Settings()
            assert settings.ENABLE_METRICS is True
            assert settings.METRICS_PORT == 9090
            assert settings.ENABLE_TRACING is False

    def test_api_rate_limiting(self):
        """Test API rate limiting settings."""
        rate_limit_config = {
            "RATE_LIMIT_ENABLED": "true",
            "RATE_LIMIT_REQUESTS_PER_MINUTE": "60",
            "RATE_LIMIT_BURST": "10"
        }

        with patch.dict(os.environ, rate_limit_config):
            settings = Settings()
            assert settings.RATE_LIMIT_ENABLED is True
            assert settings.RATE_LIMIT_REQUESTS_PER_MINUTE == 60
            assert settings.RATE_LIMIT_BURST == 10

    def test_environment_specific_settings(self):
        """Test environment-specific configurations."""
        # Production environment
        prod_config = {
            "ENVIRONMENT": "production",
            "DEBUG": "false",
            "LOG_LEVEL": "WARNING"
        }

        with patch.dict(os.environ, prod_config):
            settings = Settings()
            assert settings.ENVIRONMENT == "production"
            assert settings.DEBUG is False
            assert settings.LOG_LEVEL == "WARNING"

        # Development environment
        dev_config = {
            "ENVIRONMENT": "development",
            "DEBUG": "true",
            "LOG_LEVEL": "DEBUG"
        }

        with patch.dict(os.environ, dev_config):
            settings = Settings()
            assert settings.ENVIRONMENT == "development"
            assert settings.DEBUG is True
            assert settings.LOG_LEVEL == "DEBUG"

    def test_database_pool_settings(self):
        """Test database connection pool settings."""
        pool_config = {
            "DB_POOL_SIZE": "20",
            "DB_MAX_OVERFLOW": "30",
            "DB_POOL_TIMEOUT": "60",
            "DB_POOL_RECYCLE": "3600"
        }

        with patch.dict(os.environ, pool_config):
            settings = Settings()
            assert settings.DB_POOL_SIZE == 20
            assert settings.DB_MAX_OVERFLOW == 30
            assert settings.DB_POOL_TIMEOUT == 60
            assert settings.DB_POOL_RECYCLE == 3600

    def test_celery_configuration(self):
        """Test Celery task queue configuration."""
        celery_config = {
            "CELERY_BROKER_URL": "redis://localhost:6379/1",
            "CELERY_RESULT_BACKEND": "redis://localhost:6379/2",
            "CELERY_TIMEZONE": "UTC",
            "CELERY_TASK_SERIALIZER": "json"
        }

        with patch.dict(os.environ, celery_config):
            settings = Settings()
            assert settings.CELERY_BROKER_URL == "redis://localhost:6379/1"
            assert settings.CELERY_RESULT_BACKEND == "redis://localhost:6379/2"
            assert settings.CELERY_TIMEZONE == "UTC"

    def test_settings_validation_errors(self):
        """Test settings validation with invalid values."""
        # Test invalid log level
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}):
            with pytest.raises(ValueError):
                Settings()

        # Test invalid port number
        with patch.dict(os.environ, {"SMTP_PORT": "invalid_port"}):
            with pytest.raises(ValueError):
                Settings()

    def test_settings_immutability(self):
        """Test that settings are immutable after creation."""
        settings = Settings()

        # Settings should be frozen/immutable
        with pytest.raises(AttributeError):
            settings.DEBUG = True

        with pytest.raises(AttributeError):
            settings.new_attribute = "value"