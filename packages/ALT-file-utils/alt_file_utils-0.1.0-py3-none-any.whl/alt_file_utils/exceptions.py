"""
Exception classes for ALT-file-utils package.
"""

from typing import Any, Dict, Optional


class FileUtilsError(Exception):
    """Base exception for all file utilities errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize exception with message and optional context.

        Args:
            message: Error message
            context: Optional context information for debugging
        """
        super().__init__(message)
        self.context = context or {}


class FileOperationError(FileUtilsError):
    """Base exception for file operation errors."""

    pass


class FileReadError(FileOperationError):
    """Raised when a file cannot be read."""

    pass


class FileWriteError(FileOperationError):
    """Raised when a file cannot be written."""

    pass


class FileParseError(FileOperationError):
    """Raised when a file cannot be parsed."""

    pass


class FileLockError(FileOperationError):
    """Raised when a file lock cannot be acquired."""

    pass
