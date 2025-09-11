"""
API client for HLA-Compass platform

This module provides the APIClient class that handles all communication
with the HLA-Compass REST API. It's used internally by the data access
classes (PeptideData, ProteinData, SampleData) to fetch scientific data.
"""

import requests
import logging
import time
import platform
import uuid
from typing import Dict, Any, List, Optional

from .auth import Auth
from .config import Config
from .utils import parse_api_error, RateLimiter


logger = logging.getLogger(__name__)


class APIError(Exception):
    """API request error"""

    def __init__(self, message: str, status_code: int = None, details: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}


class APIClient:
    """
    Client for interacting with HLA-Compass API

    This client handles:
    - Authentication using JWT tokens
    - Request formatting and response parsing
    - Error handling and retries
    - Pagination support
    """

    def __init__(self, provider: str = None, catalog: str = None):
        """Initialize API client with authentication and a persistent session
        
        Args:
            provider: Data provider name (default: from config or 'alithea-bio')
            catalog: Data catalog name (default: from config or 'immunopeptidomics')
        """
        self.auth = Auth()
        self.config = Config()
        self.base_url = self.config.get_api_endpoint()
        
        # Set provider and catalog from args, config, or defaults
        self.provider = provider or self.config.get("data_provider", "alithea-bio")
        self.catalog = catalog or self.config.get("data_catalog", "immunopeptidomics")
        
        self.rate_limiter = RateLimiter(
            max_requests=100,  # 100 requests per minute
            time_window=60,
        )

        # Create a persistent HTTP session for connection reuse and default headers
        self.session = requests.Session()

        # Build a descriptive User-Agent
        try:
            from . import __version__ as SDK_VERSION  # Avoid hard dependency if import path changes
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

        # Configure retries for idempotent requests (GET/HEAD/OPTIONS)
        try:  # Optional dependency present in requests.adapters
            from urllib3.util import Retry  # type: ignore
            from requests.adapters import HTTPAdapter  # type: ignore

            retry = Retry(
                total=3,
                connect=3,
                read=3,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods={"GET", "HEAD", "OPTIONS"},
                respect_retry_after_header=True,
            )
            adapter = HTTPAdapter(max_retries=retry)
            self.session.mount("https://", adapter)
            self.session.mount("http://", adapter)
        except Exception:
            # If retry configuration fails, continue without it
            pass

    def _headers(self) -> Dict[str, str]:
        """Compose request headers by combining session defaults with auth headers"""
        headers = dict(self.session.headers)
        headers.update(self.auth.get_headers())
        # Optional correlation id for cross-service tracing
        try:
            corr = self.config.get_correlation_id()
            if corr:
                headers["X-Correlation-Id"] = corr
        except Exception:
            pass
        return headers

    def _build_data_endpoint(self, entity: str, entity_id: str = None) -> str:
        """Build a data API endpoint path.
        
        Args:
            entity: Entity name (e.g., 'peptides', 'proteins')
            entity_id: Optional entity ID for specific resource
            
        Returns:
            Complete endpoint path
        """
        base = f"/v1/data/{self.provider}/{self.catalog}/{entity}"
        if entity_id:
            return f"{base}/{entity_id}"
        return base

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        json_data: Dict = None,
        max_retries: int = 3,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Make an authenticated API request with retries and timeouts

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., /v1/data/alithea-bio/immunopeptidomics/peptides)
            params: Query parameters
            json_data: JSON body data
            max_retries: Maximum number of retry attempts for transient errors

        Returns:
            Parsed JSON response

        Raises:
            APIError: If request fails
        """
        # Ensure we have authentication
        if not self.auth.is_authenticated():
            raise APIError(
                "Not authenticated. Please run 'hla-compass auth login' first"
            )

        # Build full URL
        url = f"{self.base_url}{endpoint}"

        # Apply rate limiting
        self.rate_limiter.acquire()

        # Get combined headers (session defaults + auth)
        headers = self._headers()

        # Retry logic for transient errors
        # For POST requests, only allow retry when an idempotency key is provided.
        # Generate a stable idempotency key per call if not provided so that
        # internal retries are safe and deduplicated server-side.
        method_upper = (method or "").upper()
        if method_upper == "POST" and not idempotency_key:
            idempotency_key = str(uuid.uuid4())
        can_retry_post = method_upper != "POST" or (idempotency_key is not None)

        for attempt in range(max_retries):
            try:
                # Create a fresh set of headers per attempt and add a unique request id
                attempt_headers = dict(headers)
                attempt_headers["X-Request-Id"] = str(uuid.uuid4())
                # Add idempotency key for POSTs to make retries safe
                if method_upper == "POST" and idempotency_key:
                    attempt_headers.setdefault("Idempotency-Key", idempotency_key)
                # Make request with timeout (5s connect, 30s read)
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=attempt_headers,
                    params=params,
                    json=json_data,
                    timeout=(5, 30),
                )

                # Handle 401 - try to refresh token once
                if response.status_code == 401 and attempt == 0:
                    logger.info("Token expired, attempting refresh")
                    new_token = self.auth.refresh_token()
                    if new_token:
                        # Rebuild base headers to include new Authorization and retry
                        headers = self._headers()
                        continue  # Retry with new token
                    else:
                        raise APIError(
                            "Authentication expired. Please run 'hla-compass auth login' again"
                        )

                # Handle rate limiting with exponential backoff
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        retry_after = int(
                            response.headers.get("Retry-After", 2**attempt)
                        )
                        logger.warning(
                            f"Rate limited, retrying after {retry_after} seconds"
                        )
                        time.sleep(retry_after)
                        continue
                    else:
                        raise APIError(
                            "Rate limit exceeded. Please try again later.", 429
                        )

                # Handle server errors with retry
                if response.status_code >= 500 and attempt < max_retries - 1:
                    # Only retry POSTs when idempotency is guaranteed
                    if method_upper == "POST" and not can_retry_post:
                        raise APIError(
                            f"Server error {response.status_code}", response.status_code
                        )
                    wait_time = 2**attempt  # Exponential backoff
                    logger.warning(
                        f"Server error {response.status_code}, retrying in {wait_time} seconds"
                    )
                    time.sleep(wait_time)
                    continue

                # Check for other errors
                if response.status_code >= 400:
                    # Sanitize error message to avoid info disclosure
                    error_msg = parse_api_error(response, "API request failed")
                    raise APIError(error_msg, response.status_code)

                # Parse successful response
                data = response.json()

                # Handle success wrapper format
                if isinstance(data, dict) and data.get("success"):
                    return data.get("data", data)

                return data

            except requests.Timeout:
                if attempt < max_retries - 1:
                    wait_time = 2**attempt
                    logger.warning(f"Request timeout, retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                else:
                    raise APIError(
                        "Request timed out. Please check your connection and try again."
                    )

            except requests.RequestException as e:
                if attempt < max_retries - 1 and "connection" in str(e).lower():
                    wait_time = 2**attempt
                    logger.warning(f"Connection error, retrying in {wait_time} seconds")
                    time.sleep(wait_time)
                    continue
                else:
                    raise APIError(f"Network error: {str(e)}")

    # Peptide endpoints

    def get_peptides(
        self, filters: Dict = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search peptides with filters

        Args:
            filters: Search filters (sequence, min_length, max_length, etc.)
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            List of peptide records
        """
        params = {"limit": limit, "offset": offset}

        # Add filters to params
        if filters:
            # Map internal filter names to API parameter names
            filter_mapping = {
                "sequence": "sequence",
                "min_length": "min_length",
                "max_length": "max_length",
                "mass": "mass",
                "mass_tolerance": "mass_tolerance",
                "modifications": "modifications",
                "hla_allele": "hla",
                "organ": "organ",
                "disease": "disease",
            }

            for key, value in filters.items():
                api_param = filter_mapping.get(key, key)
                if isinstance(value, list):
                    params[api_param] = ",".join(str(v) for v in value)
                else:
                    params[api_param] = value

        result = self._make_request("GET", self._build_data_endpoint("peptides"), params=params)

        # Extract peptides from response
        if isinstance(result, dict):
            return result.get("peptides", result.get("items", []))
        return result if isinstance(result, list) else []

    def get_peptide(self, peptide_id: str) -> Dict[str, Any]:
        """Get single peptide by ID"""
        result = self._make_request("GET", self._build_data_endpoint("peptides", peptide_id))
        return result.get("peptide", result)

    def get_peptide_samples(self, peptide_id: str) -> List[Dict[str, Any]]:
        """Get samples containing a peptide"""
        result = self._make_request(
            "GET", f"{self._build_data_endpoint('peptides', peptide_id)}/samples"
        )
        return result.get("samples", result.get("items", []))

    def get_peptide_proteins(self, peptide_id: str) -> List[Dict[str, Any]]:
        """Get proteins containing a peptide"""
        result = self._make_request(
            "GET", f"{self._build_data_endpoint('peptides', peptide_id)}/proteins"
        )
        return result.get("proteins", result.get("items", []))

    def search_peptides_by_mass(
        self, mass: float, tolerance: float = 0.01, unit: str = "Da"
    ) -> List[Dict[str, Any]]:
        """Search peptides by mass"""
        params = {"mass": mass, "tolerance": tolerance, "unit": unit}
        result = self._make_request(
            "GET", f"{self._build_data_endpoint('peptides')}/search/mass", params=params
        )
        return result.get("peptides", result.get("items", []))

    # Protein endpoints

    def get_proteins(
        self, filters: Dict = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search proteins with filters

        Args:
            filters: Search filters (accession, gene_name, organism, etc.)
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            List of protein records
        """
        params = {"limit": limit, "offset": offset}

        if filters:
            params.update(filters)

        result = self._make_request("GET", self._build_data_endpoint("proteins"), params=params)

        # Extract proteins from response
        if isinstance(result, dict):
            return result.get("proteins", result.get("items", []))
        return result if isinstance(result, list) else []

    def get_protein(self, protein_id: str) -> Dict[str, Any]:
        """Get single protein by ID"""
        result = self._make_request("GET", self._build_data_endpoint("proteins", protein_id))
        return result.get("protein", result)

    def get_protein_peptides(self, protein_id: str) -> List[Dict[str, Any]]:
        """Get peptides from a protein"""
        result = self._make_request(
            "GET", f"{self._build_data_endpoint('proteins', protein_id)}/peptides"
        )
        return result.get("peptides", result.get("items", []))

    def get_protein_coverage(self, protein_id: str) -> Dict[str, Any]:
        """Get protein coverage information"""
        result = self._make_request(
            "GET", f"{self._build_data_endpoint('proteins', protein_id)}/coverage"
        )
        return result

    # Sample endpoints

    def get_samples(
        self, filters: Dict = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Search samples with filters

        Args:
            filters: Search filters (tissue, disease, cell_line, etc.)
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            List of sample records
        """
        params = {"limit": limit, "offset": offset}

        if filters:
            params.update(filters)

        result = self._make_request("GET", self._build_data_endpoint("samples"), params=params)

        # Extract samples from response
        if isinstance(result, dict):
            return result.get("samples", result.get("items", []))
        return result if isinstance(result, list) else []

    def get_sample(self, sample_id: str) -> Dict[str, Any]:
        """Get single sample by ID"""
        result = self._make_request("GET", self._build_data_endpoint("samples", sample_id))
        return result.get("sample", result)

    def get_sample_peptides(self, sample_id: str) -> List[Dict[str, Any]]:
        """Get peptides from a sample"""
        result = self._make_request(
            "GET", f"{self._build_data_endpoint('samples', sample_id)}/peptides"
        )
        return result.get("peptides", result.get("items", []))

    def compare_samples(
        self, sample_ids: List[str], metric: str = "jaccard"
    ) -> Dict[str, Any]:
        """Compare multiple samples"""
        json_data = {"sample_ids": sample_ids, "metric": metric}
        return self._make_request(
            "POST", f"{self._build_data_endpoint('samples')}/compare", json_data=json_data
        )

    # HLA endpoints

    def get_hla_alleles(
        self, locus: str = None, resolution: str = "2-digit"
    ) -> List[str]:
        """Get list of HLA alleles"""
        params = {"resolution": resolution}
        if locus:
            params["locus"] = locus

        result = self._make_request("GET", f"{self._build_data_endpoint('hla')}/alleles", params=params)
        return result.get("alleles", result if isinstance(result, list) else [])

    def get_hla_frequencies(self, population: str = None) -> Dict[str, float]:
        """Get HLA allele frequencies"""
        params = {}
        if population:
            params["population"] = population

        result = self._make_request(
            "GET", f"{self._build_data_endpoint('hla')}/frequencies", params=params
        )
        return result.get("frequencies", result if isinstance(result, dict) else {})

    def predict_hla_binding(
        self, peptides: List[str], alleles: List[str], method: str = "netmhcpan"
    ) -> List[Dict[str, Any]]:
        """Predict HLA-peptide binding"""
        json_data = {"peptides": peptides, "alleles": alleles, "method": method}
        result = self._make_request(
            "POST", f"{self._build_data_endpoint('hla')}/predict", json_data=json_data
        )
        return result.get("predictions", result if isinstance(result, list) else [])

    # Module endpoints

    def execute_module(
        self, module_id: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a module with parameters

        Args:
            module_id: Module ID to execute
            parameters: Input parameters for the module

        Returns:
            Job information including job_id
        """
        json_data = {"parameters": parameters}
        return self._make_request(
            "POST", f"/v1/modules/{module_id}/execute", json_data=json_data
        )

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job execution status"""
        return self._make_request("GET", f"/v1/modules/jobs/{job_id}/status")

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        """Get job execution result"""
        return self._make_request("GET", f"/v1/modules/jobs/{job_id}/result")

    def list_modules(
        self, category: str = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List available modules"""
        params = {"limit": limit}
        if category:
            params["category"] = category

        result = self._make_request("GET", "/v1/modules", params=params)
        return result.get("modules", result.get("items", []))

    def upload_module(
        self, module_path: str, module_name: str, version: str
    ) -> Dict[str, Any]:
        """
        Upload module package to platform

        Args:
            module_path: Path to module zip file
            module_name: Name of the module
            version: Module version

        Returns:
            Upload response with module_id
        """
        import os

        # Check file exists
        if not os.path.exists(module_path):
            raise APIError(f"Module package not found: {module_path}")

        # Get file size
        file_size = os.path.getsize(module_path)
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            raise APIError(
                f"Module package too large: {file_size / 1024 / 1024:.1f}MB (max 50MB)"
            )

        # Prepare multipart upload
        with open(module_path, "rb") as f:
            files = {"module": (f"{module_name}-{version}.zip", f, "application/zip")}
            data = {"name": module_name, "version": version}

            # Make request with file upload
            base_headers = self._headers()
            # Remove Content-Type header to let requests set it for multipart
            base_headers.pop("Content-Type", None)
            # Idempotency ensures safe retries for POST upload
            idem_key = str(uuid.uuid4())
            base_headers.setdefault("Idempotency-Key", idem_key)
            url = f"{self.base_url}/v1/modules"

            # Attempt with basic backoff for 429/5xx
            # Track last error for raising after retries
            last_err = None  # type: ignore[assignment]
            for attempt in range(3):
                headers = dict(base_headers)
                headers["X-Request-Id"] = str(uuid.uuid4())
                response = self.session.post(
                    url=url,
                    headers=headers,
                    files=files,
                    data=data,
                    timeout=(10, 60),  # 10s connect, 60s read for upload
                )

                if response.status_code >= 400:
                    # Retry on 429/5xx only (safe with idempotency)
                    if response.status_code == 429 or response.status_code >= 500:
                        if attempt < 2:
                            retry_after = int(response.headers.get("Retry-After", 2**attempt))
                            time.sleep(retry_after)
                            continue
                    try:
                        error_data = response.json() if response.text else {}
                        error_msg = error_data.get("error", {}).get(
                            "message", f"Upload failed: {response.status_code}"
                        )
                    except Exception:
                        error_msg = f"Upload failed: {response.status_code}"
                    last_err = APIError(error_msg, response.status_code)
                    break

                result = response.json()
                if isinstance(result, dict) and result.get("success"):
                    return result.get("data", result)
                return result

            if last_err:
                raise last_err  # type: ignore[misc]
            # Should not reach here, but guard just in case
            raise APIError("Upload failed after retries")

    def register_module(
        self, module_id: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Register uploaded module in platform

        Args:
            module_id: Module ID from upload
            metadata: Module metadata (manifest info)

        Returns:
            Registration confirmation
        """
        json_data = {"module_id": module_id, "metadata": metadata}
        return self._make_request("POST", "/v1/modules/register", json_data=json_data)
