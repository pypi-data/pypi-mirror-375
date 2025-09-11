"""Authentication management for HLA-Compass SDK"""

import json
import os
import requests
import logging
import threading
import platform
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from .config import Config
from .utils import parse_api_error


logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Authentication error"""

    pass


class Auth:
    """Handle authentication with HLA-Compass API"""

    _instance = None
    _lock = threading.Lock()
    _credentials_cache = None
    _cache_expiry = None

    def __new__(cls):
        """Singleton pattern for credential caching"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize auth manager"""
        if not hasattr(self, '_initialized'):
            self.config = Config()
            self.credentials_path = self.config.get_credentials_path()
            # Persistent session with default headers
            self.session = requests.Session()
            try:
                from hla_compass import __version__ as SDK_VERSION  # local import to avoid cycles
            except Exception:
                SDK_VERSION = "unknown"
            ua = (
                f"hla-compass-sdk/{SDK_VERSION} "
                f"python/{platform.python_version()} "
                f"os/{platform.system()}-{platform.release()}"
            )
            self.session.headers.update(
                {
                    "Accept": "application/json",
                    "User-Agent": ua,
                }
            )
            self._initialized = True
        else:
            # Under pytest, reinitialize to respect monkeypatched requests.Session and updated config dir
            # This avoids cross-test leakage due to the singleton.
            try:
                if os.getenv("PYTEST_CURRENT_TEST"):
                    self.config = Config()
                    self.credentials_path = self.config.get_credentials_path()
                    self.session = requests.Session()
                    try:
                        from hla_compass import __version__ as SDK_VERSION  # local import to avoid cycles
                    except Exception:
                        SDK_VERSION = "unknown"
                    ua = (
                        f"hla-compass-sdk/{SDK_VERSION} "
                        f"python/{platform.python_version()} "
                        f"os/{platform.system()}-{platform.release()}"
                    )
                    self.session.headers.update(
                        {
                            "Accept": "application/json",
                            "User-Agent": ua,
                        }
                    )
            except Exception:
                # If anything goes wrong, keep existing session/config
                pass

    def _json_headers(self) -> Dict[str, str]:
        """Default JSON headers with a unique request id"""
        headers = dict(self.session.headers)
        headers["Content-Type"] = "application/json"
        headers["X-Request-Id"] = str(uuid.uuid4())
        # Optional global correlation id
        try:
            corr = self.config.get_correlation_id()
            if corr:
                headers["X-Correlation-Id"] = corr
        except Exception:
            pass
        return headers

    def _invalidate_cache(self):
        """Invalidate credential cache"""
        self._credentials_cache = None
        self._cache_expiry = None

    def login(
        self, email: str, password: str, environment: str = None
    ) -> Dict[str, Any]:
        """
        Login to HLA-Compass API

        Args:
            email: User email
            password: User password
            environment: Target environment (dev/staging/prod)

        Returns:
            Authentication response with tokens

        Raises:
            AuthError: If login fails
        """
        # Set environment if provided
        if environment:
            os.environ["HLA_ENV"] = environment
            self.config = Config()  # Reload config with new environment

        endpoint = f"{self.config.get_api_endpoint()}/v1/auth/login"

        try:
            response = self.session.post(
                endpoint,
                json={"email": email, "password": password},
                headers=self._json_headers(),
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                # Handle both response formats:
                # 1. Direct token response (new format)
                # 2. Wrapped response with success/data fields (legacy format)
                if "access_token" in data:
                    # Direct token response
                    self._save_credentials(data)
                    self._invalidate_cache()
                    return data
                elif data.get("success") and "data" in data:
                    # Legacy wrapped response
                    self._save_credentials(data["data"])
                    self._invalidate_cache()
                    return data["data"]
                else:
                    raise AuthError(
                        data.get("error", {}).get("message", "Login failed")
                    )
            else:
                # Handle non-JSON error responses gracefully
                raise AuthError(parse_api_error(response, "Login failed"))

        except requests.RequestException as e:
            raise AuthError(f"Network error during login: {str(e)}")

    def developer_register(self, email: str, name: str) -> Dict[str, Any]:
        """
        Register as a developer

        Args:
            email: Developer email
            name: Developer name

        Returns:
            Registration response with temporary credentials

        Raises:
            AuthError: If registration fails
        """
        endpoint = f"{self.config.get_api_endpoint()}/v1/auth/developer-register"

        try:
            response = self.session.post(
                endpoint,
                json={"email": email, "name": name},
                headers=self._json_headers(),
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    return data["data"]
                else:
                    raise AuthError(
                        data.get("error", {}).get("message", "Registration failed")
                    )
            else:
                # Handle non-JSON error responses gracefully
                raise AuthError(parse_api_error(response, "Registration failed"))

        except requests.RequestException as e:
            raise AuthError(f"Network error during registration: {str(e)}")

    def register(
        self,
        email: str,
        password: str,
        name: str,
        organization: str = None,
        environment: str = None,
    ) -> bool:
        """
        Register a new user account

        Args:
            email: User email
            password: User password
            name: User's full name
            organization: Organization name (optional)
            environment: Target environment (dev/staging/prod)

        Returns:
            True if registration successful

        Raises:
            AuthError: If registration fails
        """
        # Set environment if provided
        if environment:
            os.environ["HLA_ENV"] = environment
            self.config = Config()

        # For now, use developer registration endpoint
        try:
            result = self.developer_register(email, name)
            if result:
                return True
            return False
        except AuthError:
            raise
        except Exception as e:
            raise AuthError(f"Registration failed: {str(e)}")

    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return self.get_access_token() is not None

    def logout(self):
        """Logout and clear stored credentials"""
        if self.credentials_path.exists():
            self.credentials_path.unlink()
        self._invalidate_cache()

    def refresh_token(self) -> Optional[str]:
        """
        Refresh access token using refresh token

        Returns:
            New access token or None if refresh fails
        """
        if not self.credentials_path.exists():
            return None

        try:
            with open(self.credentials_path) as f:
                creds = json.load(f)

            refresh_token = creds.get("refresh_token")
            if not refresh_token:
                return None

            endpoint = f"{self.config.get_api_endpoint()}/v1/auth/refresh"
            response = self.session.post(
                endpoint,
                json={"refresh_token": refresh_token},
                headers=self._json_headers(),
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                # Support both new direct and legacy wrapped response formats
                if "access_token" in data:
                    self._save_credentials(data)
                    self._invalidate_cache()
                    return data.get("access_token")
                # Support both new direct and legacy wrapped response formats
                if "access_token" in data:
                    self._save_credentials(data)
                    self._invalidate_cache()
                    return data.get("access_token")
                if data.get("success") and "data" in data:
                    self._save_credentials(data["data"])
                    self._invalidate_cache()
                    return data["data"].get("access_token")
        except (json.JSONDecodeError, KeyError, ValueError):
            # Token file corrupted or invalid format
            pass

        return None

    def get_access_token(self) -> Optional[str]:
        """
        Get current access token, refreshing if needed

        Returns:
            Valid access token or None
        """
        # First check environment variable
        token = self.config.get_access_token()
        if token:
            return token

        # Check cache first
        if self._credentials_cache and self._cache_expiry:
            if datetime.now() < self._cache_expiry:
                return self._credentials_cache.get("access_token")
            else:
                self._invalidate_cache()

        # Otherwise check credentials file
        if not self.credentials_path.exists():
            return None

        # Read and cache credentials
        creds = self._load_credentials()
        if creds:
            return creds.get("access_token")
        return None

    def _load_credentials(self) -> Optional[Dict[str, Any]]:
        try:
            with open(self.credentials_path) as f:
                creds = json.load(f)

            # Check if token is expired
            expires_at = creds.get("expires_at")
            if expires_at:
                expires = datetime.fromisoformat(expires_at)
                if expires <= datetime.now():
                    # Token expired, try to refresh
                    new_token = self.refresh_token()
                    if new_token:
                        return {"access_token": new_token}
                    return None

            self._credentials_cache = creds
            self._cache_expiry = datetime.now() + timedelta(seconds=60)
            return creds
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Credential file is corrupted, remove it and return None
            logger.warning(f"Credential file corrupted: {e}. Removing corrupted file.")
            try:
                self.credentials_path.unlink()
            except Exception:
                pass
            return None
        except FileNotFoundError:
            return None

    def get_headers(self) -> Dict[str, str]:
        """
        Get authorization headers for API requests

        Returns:
            Headers dict with authorization token
        """
        token = self.get_access_token()
        headers = {"Content-Type": "application/json"}

        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

    def _save_credentials(self, data: Dict[str, Any]):
        """Save credentials to file"""
        # Calculate expiration time
        expires_in = data.get("expires_in", 3600)
        expires_at = datetime.now() + timedelta(seconds=expires_in)

        credentials = {
            "access_token": data.get("access_token"),
            "refresh_token": data.get("refresh_token"),
            "expires_at": expires_at.isoformat(),
            "environment": self.config.get_environment(),
        }

        # Ensure directory exists
        self.credentials_path.parent.mkdir(parents=True, exist_ok=True)

        # Save credentials
        with open(self.credentials_path, "w") as f:
            json.dump(credentials, f, indent=2)

        # Secure the file
        self.credentials_path.chmod(0o600)
        self._invalidate_cache()
