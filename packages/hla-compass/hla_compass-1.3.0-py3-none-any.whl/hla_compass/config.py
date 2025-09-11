"""Configuration management for HLA-Compass SDK"""

import os
from pathlib import Path
from typing import Optional


class Config:
    """SDK configuration management"""

    # API endpoints by environment (base URLs without version prefix)
    API_ENDPOINTS = {
        "dev": "https://api-dev.alithea.bio",
        "staging": "https://api-staging.alithea.bio",
        "prod": "https://api.alithea.bio",
    }

    @classmethod
    def get_environment(cls) -> str:
        """Get current environment (dev/staging/prod)

        Precedence: HLA_COMPASS_ENV > HLA_ENV > 'dev'
        """
        return os.getenv("HLA_COMPASS_ENV") or os.getenv("HLA_ENV", "dev")

    @classmethod
    def get_api_endpoint(cls) -> str:
        """Get API endpoint for current environment"""
        env = cls.get_environment()
        return cls.API_ENDPOINTS.get(env, cls.API_ENDPOINTS["dev"])

    @classmethod
    def get_config_dir(cls) -> Path:
        """Get configuration directory path"""
        # Honor HLA_COMPASS_CONFIG_DIR environment variable
        config_dir_str = os.getenv("HLA_COMPASS_CONFIG_DIR")
        if config_dir_str:
            # Validate and sanitize path to prevent traversal
            config_path = Path(config_dir_str).resolve()
            home_path = Path.home().resolve()
            cwd_path = Path.cwd().resolve()
            # Ensure config_dir is within user's home, current directory, or temp directories
            try:
                # Check if path is relative to home
                config_path.relative_to(home_path)
                config_dir = config_path
            except ValueError:
                try:
                    # Check if path is relative to cwd
                    config_path.relative_to(cwd_path)
                    config_dir = config_path
                except ValueError:
                    # Also allow temp directories for testing
                    import tempfile
                    temp_path = Path(tempfile.gettempdir()).resolve()
                    try:
                        config_path.relative_to(temp_path)
                        config_dir = config_path
                    except ValueError:
                        # Path is outside allowed directories
                        raise ValueError(
                            "Invalid config directory: must be within home, current, or temp directory"
                        )
        else:
            config_dir = Path.home() / ".hla-compass"

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    @classmethod
    def get_credentials_path(cls) -> Path:
        """Get path to credentials file"""
        return cls.get_config_dir() / "credentials.json"

    @classmethod
    def get_config_path(cls) -> Path:
        """Get path to config file"""
        return cls.get_config_dir() / "config.json"

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Get API key from environment"""
        return os.getenv("HLA_API_KEY")

    @classmethod
    def get_access_token(cls) -> Optional[str]:
        """Get access token from credentials file or environment"""
        # First check environment
        token = os.getenv("HLA_ACCESS_TOKEN")
        if token:
            return token

        # Then check credentials file
        creds_path = cls.get_credentials_path()
        if creds_path.exists():
            import json

            try:
                with open(creds_path) as f:
                    creds = json.load(f)
                    return creds.get("access_token")
            except Exception:
                pass

        return None

    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if user is authenticated"""
        return cls.get_access_token() is not None

    @classmethod
    def get_correlation_id(cls) -> Optional[str]:
        """Get global correlation id for tracing (optional).

        Set via environment variable `HLA_CORRELATION_ID` to propagate a
        cross-service correlation identifier in the `X-Correlation-Id` header.
        """
        return os.getenv("HLA_CORRELATION_ID")

    def get(self, key: str, default=None):
        """
        Provide dict-like access for tests/utilities that call config.get(...).

        Supported keys:
          - 'environment'
          - 'api_endpoint'
          - 'config_dir'
          - 'credentials_path'
          - 'config_path'
          - 'api_key'
          - 'access_token'
          - 'is_authenticated'
          - 'correlation_id'
        """
        mapping = {
            "environment": self.get_environment(),
            "api_endpoint": self.get_api_endpoint(),
            "config_dir": str(self.get_config_dir()),
            "credentials_path": str(self.get_credentials_path()),
            "config_path": str(self.get_config_path()),
            "api_key": self.get_api_key(),
            "access_token": self.get_access_token(),
            "is_authenticated": self.is_authenticated(),
            "correlation_id": self.get_correlation_id(),
        }
        return mapping.get(key, default)

    def get(self, key: str, default=None):
        """
        Provide dict-like access for tests/utilities that call config.get(...).

        Supported keys:
          - 'environment'
          - 'api_endpoint'
          - 'config_dir'
          - 'credentials_path'
          - 'config_path'
          - 'api_key'
          - 'access_token'
          - 'is_authenticated'
          - 'correlation_id'
        """
        mapping = {
            "environment": self.get_environment(),
            "api_endpoint": self.get_api_endpoint(),
            "config_dir": str(self.get_config_dir()),
            "credentials_path": str(self.get_credentials_path()),
            "config_path": str(self.get_config_path()),
            "api_key": self.get_api_key(),
            "access_token": self.get_access_token(),
            "is_authenticated": self.is_authenticated(),
            "correlation_id": self.get_correlation_id(),
        }
        return mapping.get(key, default)
