"""
HLA-Compass Python SDK

SDK for developing modules on the HLA-Compass platform.
"""

__version__ = "1.2.8"

# Allow CI/workflows to override version at runtime (does not affect setup.py parsing)
try:
    import os as _os
    _ver = _os.getenv("HLA_COMPASS_SDK_VERSION")
    if _ver:
        __version__ = _ver
except Exception:
    pass

# Core module base class
from .module import Module, ModuleError, ValidationError

# Data access classes
from .data import PeptideData, ProteinData, SampleData, HLAData, DataAccessError

# Authentication
from .auth import Auth, AuthError

# Storage utilities
from .storage import Storage, StorageError

# Testing utilities
from .testing import ModuleTester, MockContext, MockAPI

# CLI utilities
from .cli import main as cli_main

# Types
from .types import (
    ExecutionContext,
    ModuleInput,
    ModuleOutput,
    JobStatus,
    ComputeType,
    ModuleType,
)

# Constants
from .constants import (
    SUPPORTED_HLA_ALLELES,
    AMINO_ACIDS,
    MAX_PEPTIDE_LENGTH,
    MIN_PEPTIDE_LENGTH,
)

__all__ = [
    # Version
    "__version__",
    # Core classes
    "Module",
    "ModuleError",
    "ValidationError",
    # Data access
    "PeptideData",
    "ProteinData",
    "SampleData",
    "HLAData",
    "DataAccessError",
    # Auth
    "Auth",
    "AuthError",
    # Storage
    "Storage",
    "StorageError",
    # Testing
    "ModuleTester",
    "MockContext",
    "MockAPI",
    # CLI
    "cli_main",
    # Types
    "ExecutionContext",
    "ModuleInput",
    "ModuleOutput",
    "JobStatus",
    "ComputeType",
    "ModuleType",
    # Constants
    "SUPPORTED_HLA_ALLELES",
    "AMINO_ACIDS",
    "MAX_PEPTIDE_LENGTH",
    "MIN_PEPTIDE_LENGTH",
]
