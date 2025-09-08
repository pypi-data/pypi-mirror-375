"""File I/O utilities with comprehensive error handling.

This module provides robust file operations with error handling,
atomic writes, and proper cleanup.
"""

import contextlib
import json
import logging
import os
import shutil
import tempfile
import time
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import IO, Any, Callable, Dict, Generator, Optional, TypeVar, Union, cast

import yaml

# Optional TOML support
try:
    import tomllib  # type: ignore[import-not-found]
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[import-not-found]
    except ImportError:
        tomllib = None

from alt_file_utils.constants import (
    DEFAULT_ENCODING,
    DEFAULT_RETRY_DELAY,
    DEFAULT_RETRY_MAX_ATTEMPTS,
    JSON_INDENT_SPACES,
)
from alt_file_utils.exceptions import (
    FileOperationError,
    FileParseError,
    FileReadError,
    FileWriteError,
)

T = TypeVar("T")
logger = logging.getLogger(__name__)


def retry_on_failure(
    max_attempts: int = DEFAULT_RETRY_MAX_ATTEMPTS,
    delay: float = DEFAULT_RETRY_DELAY,
    exceptions: tuple = (OSError, IOError),
) -> Callable:
    """Decorator to retry file operations on transient failures.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between retries in seconds
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        logger.debug(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {e}")
            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Unexpected state in retry decorator")

        return wrapper

    return decorator


@contextmanager
def atomic_write(
    filepath: Union[str, Path], mode: str = "w", encoding: Optional[str] = DEFAULT_ENCODING
) -> Generator[IO[Any], None, None]:
    """Context manager for atomic file writes.

    Writes to a temporary file and atomically moves it to the target path
    only if the write succeeds. This prevents partial writes and corruption.

    Args:
        filepath: Target file path
        mode: File open mode (default: 'w')
        encoding: File encoding for text mode (default: utf-8)

    Yields:
        File handle for writing

    Raises:
        FileWriteError: If the write operation fails
    """
    filepath = Path(filepath)

    # Ensure parent directory exists
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise FileWriteError(f"Failed to create directory {filepath.parent}: {e}") from e

    # Create temporary file in the same directory (for atomic rename)
    temp_fd = None
    temp_path = None

    try:
        temp_fd, temp_path_str = tempfile.mkstemp(
            dir=filepath.parent, prefix=f".{filepath.name}.", suffix=".tmp"
        )
        temp_path = Path(temp_path_str)

        # Close the file descriptor and open with requested mode
        os.close(temp_fd)
        temp_fd = None

        if "b" in mode:
            with open(temp_path, mode) as f:
                yield f
        else:
            with open(temp_path, mode, encoding=encoding) as f:
                yield f

        # Atomic rename (on same filesystem)
        temp_path.replace(filepath)
        logger.debug(f"Successfully wrote {filepath}")

    except Exception as e:
        logger.error(f"Failed to write {filepath}: {e}")
        raise FileWriteError(f"Failed to write {filepath}: {e}") from e

    finally:
        # Clean up temp file if it still exists
        if temp_path and temp_path.exists():
            with contextlib.suppress(OSError):
                temp_path.unlink()


@retry_on_failure()
def safe_json_dump(
    data: Dict[str, Any],
    filepath: Union[str, Path],
    indent: int = JSON_INDENT_SPACES,
    **kwargs: Any,
) -> None:
    """Safely write JSON data to a file with error handling.

    Args:
        data: Data to serialize
        filepath: Target file path
        indent: JSON indentation level
        **kwargs: Additional arguments for json.dump

    Raises:
        FileWriteError: If the write fails
        FileParseError: If the data cannot be serialized
    """
    # Test serialization first to catch errors early
    try:
        json.dumps(data)
    except (TypeError, ValueError) as e:
        raise FileParseError(f"Failed to serialize data to JSON: {e}") from e

    # Now do the actual write
    try:
        with atomic_write(filepath, mode="w") as f:
            json.dump(data, f, indent=indent, **kwargs)
    except Exception as e:
        raise FileWriteError(f"Failed to write JSON to {filepath}: {e}") from e


@retry_on_failure()
def safe_json_load(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Safely load JSON data from a file with error handling.

    Args:
        filepath: Path to JSON file

    Returns:
        Parsed JSON data

    Raises:
        FileReadError: If the file cannot be read
        FileParseError: If the JSON is invalid
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileReadError(f"File not found: {filepath}")

    try:
        with open(filepath, encoding=DEFAULT_ENCODING) as f:
            result = json.load(f)
            return cast(Dict[str, Any], result)
    except json.JSONDecodeError as e:
        raise FileParseError(f"Invalid JSON in {filepath}: {e}") from e
    except Exception as e:
        raise FileReadError(f"Failed to read {filepath}: {e}") from e


@retry_on_failure()
def safe_yaml_dump(data: Dict[str, Any], filepath: Union[str, Path], **kwargs: Any) -> None:
    """Safely write YAML data to a file with error handling.

    Args:
        data: Data to serialize
        filepath: Target file path
        **kwargs: Additional arguments for yaml.dump

    Raises:
        FileWriteError: If the write fails
        FileParseError: If the data cannot be serialized
    """
    try:
        with atomic_write(filepath, mode="w") as f:
            yaml.dump(data, f, default_flow_style=False, **kwargs)
    except yaml.YAMLError as e:
        raise FileParseError(f"Failed to serialize data to YAML: {e}") from e
    except Exception as e:
        raise FileWriteError(f"Failed to write YAML to {filepath}: {e}") from e


@retry_on_failure()
def safe_yaml_load(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Safely load YAML data from a file with error handling.

    Args:
        filepath: Path to YAML file

    Returns:
        Parsed YAML data

    Raises:
        FileReadError: If the file cannot be read
        FileParseError: If the YAML is invalid
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileReadError(f"File not found: {filepath}")

    try:
        with open(filepath, encoding=DEFAULT_ENCODING) as f:
            result = yaml.safe_load(f)
            return cast(Dict[str, Any], result)
    except yaml.YAMLError as e:
        raise FileParseError(f"Invalid YAML in {filepath}: {e}") from e
    except Exception as e:
        raise FileReadError(f"Failed to read {filepath}: {e}") from e


@retry_on_failure()
def safe_toml_load(filepath: Union[str, Path]) -> Dict[str, Any]:
    """Safely load TOML data from a file with error handling.

    Args:
        filepath: Path to TOML file

    Returns:
        Parsed TOML data

    Raises:
        FileReadError: If the file cannot be read
        FileParseError: If the TOML is invalid
        RuntimeError: If TOML support is not available
    """
    if tomllib is None:
        raise RuntimeError("TOML support not available. Install 'tomli' package for Python < 3.11")

    filepath = Path(filepath)

    if not filepath.exists():
        raise FileReadError(f"File not found: {filepath}")

    try:
        with open(filepath, "rb") as f:
            result = tomllib.load(f)
            return cast(Dict[str, Any], result)
    except Exception as e:
        if "toml" in str(e).lower():
            raise FileParseError(f"Invalid TOML in {filepath}: {e}") from e
        else:
            raise FileReadError(f"Failed to read {filepath}: {e}") from e


def safe_file_read(
    filepath: Union[str, Path], mode: str = "r", encoding: str = DEFAULT_ENCODING
) -> str:
    """Safely read a file with error handling.

    Args:
        filepath: Path to file
        mode: Read mode
        encoding: File encoding (default: utf-8)

    Returns:
        File contents

    Raises:
        FileReadError: If the file cannot be read
    """
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileReadError(f"File not found: {filepath}")

    try:
        with open(filepath, mode, encoding=encoding if "b" not in mode else None) as f:
            content = f.read()
            return cast(str, content)
    except Exception as e:
        raise FileReadError(f"Failed to read {filepath}: {e}") from e


def safe_file_write(
    content: Union[str, bytes],
    filepath: Union[str, Path],
    mode: str = "w",
    encoding: str = DEFAULT_ENCODING,
) -> None:
    """Safely write content to a file with error handling.

    Args:
        content: Content to write
        filepath: Target file path
        mode: Write mode
        encoding: File encoding (default: utf-8)

    Raises:
        FileWriteError: If the write fails
    """
    try:
        with atomic_write(filepath, mode=mode, encoding=encoding) as f:
            if isinstance(content, str) and "b" not in mode:
                f.write(content)
            elif isinstance(content, bytes) and "b" in mode:
                f.write(content)  # type: ignore
            else:
                raise TypeError(f"Content type {type(content)} doesn't match mode {mode}")
    except Exception as e:
        raise FileWriteError(f"Failed to write to {filepath}: {e}") from e


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for the directory

    Raises:
        FileOperationError: If directory cannot be created
    """
    path = Path(path)

    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        raise FileOperationError(f"Failed to create directory {path}: {e}") from e


def safe_copy(
    source: Union[str, Path], destination: Union[str, Path], overwrite: bool = False
) -> None:
    """Safely copy a file with error handling.

    Args:
        source: Source file path
        destination: Destination file path
        overwrite: Whether to overwrite existing file

    Raises:
        FileReadError: If source cannot be read
        FileWriteError: If destination cannot be written
        FileOperationError: If file exists and overwrite is False
    """
    source = Path(source)
    destination = Path(destination)

    if not source.exists():
        raise FileReadError(f"Source file not found: {source}")

    if destination.exists() and not overwrite:
        raise FileOperationError(f"Destination already exists: {destination}")

    try:
        # Ensure destination directory exists
        ensure_directory(destination.parent)

        # Copy with atomic write
        with atomic_write(destination, mode="wb") as dst, open(source, "rb") as src:
            shutil.copyfileobj(src, dst)

    except Exception as e:
        raise FileWriteError(f"Failed to copy {source} to {destination}: {e}") from e


def safe_delete(filepath: Union[str, Path], missing_ok: bool = True) -> None:
    """Safely delete a file with error handling.

    Args:
        filepath: File to delete
        missing_ok: If True, don't raise error if file doesn't exist

    Raises:
        FileOperationError: If file cannot be deleted
    """
    filepath = Path(filepath)

    try:
        filepath.unlink(missing_ok=missing_ok)
        logger.debug(f"Deleted {filepath}")
    except Exception as e:
        raise FileOperationError(f"Failed to delete {filepath}: {e}") from e


@contextmanager
def temporary_directory(prefix: str = "tmp_") -> Generator[Path, None, None]:
    """Context manager for creating a temporary directory.

    Args:
        prefix: Prefix for the temporary directory name

    Yields:
        Path to temporary directory
    """
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        yield Path(temp_dir)
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to remove temporary directory {temp_dir}: {e}")


def get_file_size(filepath: Union[str, Path]) -> int:
    """Get file size with error handling.

    Args:
        filepath: Path to file

    Returns:
        File size in bytes

    Raises:
        FileReadError: If file cannot be accessed
    """
    filepath = Path(filepath)

    try:
        return filepath.stat().st_size
    except Exception as e:
        raise FileReadError(f"Cannot get size of {filepath}: {e}") from e


def is_file_locked(filepath: Union[str, Path]) -> bool:
    """Check if a file is locked (platform-agnostic).

    Args:
        filepath: Path to file

    Returns:
        True if file appears to be locked
    """
    filepath = Path(filepath)

    if not filepath.exists():
        return False

    try:
        # Try to open the file for exclusive write
        with open(filepath, "a"):
            return False
    except OSError:
        return True
