"""
ALT-file-utils: Robust file I/O utilities for Python.

This package provides utilities for safe file operations including atomic writes,
retry mechanisms, and comprehensive error handling.
"""

from alt_file_utils.constants import PACKAGE_NAME, PACKAGE_VERSION
from alt_file_utils.core import (
    atomic_write,
    ensure_directory,
    get_file_size,
    is_file_locked,
    retry_on_failure,
    safe_copy,
    safe_delete,
    safe_file_read,
    safe_file_write,
    safe_json_dump,
    safe_json_load,
    safe_toml_load,
    safe_yaml_dump,
    safe_yaml_load,
    temporary_directory,
)
from alt_file_utils.exceptions import (
    FileLockError,
    FileOperationError,
    FileParseError,
    FileReadError,
    FileUtilsError,
    FileWriteError,
)

__version__ = PACKAGE_VERSION
__author__ = "Avi Layani"
__email__ = "alayani@redhat.com"

__all__ = [
    # Core utilities
    "atomic_write",
    "retry_on_failure",
    "temporary_directory",
    # File operations
    "safe_file_read",
    "safe_file_write",
    "safe_copy",
    "safe_delete",
    "ensure_directory",
    "get_file_size",
    "is_file_locked",
    # Format-specific operations
    "safe_json_dump",
    "safe_json_load",
    "safe_yaml_dump",
    "safe_yaml_load",
    "safe_toml_load",
    # Exception classes
    "FileUtilsError",
    "FileOperationError",
    "FileReadError",
    "FileWriteError",
    "FileParseError",
    "FileLockError",
    # Constants
    "PACKAGE_NAME",
    "PACKAGE_VERSION",
]
