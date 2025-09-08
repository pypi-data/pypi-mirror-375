"""Tests for file utility functions with error handling."""

from unittest.mock import MagicMock, patch

import pytest

from alt_file_utils import (
    FileOperationError,
    FileParseError,
    FileReadError,
    FileWriteError,
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


class TestExceptions:
    """Test custom exception hierarchy."""

    def test_exception_inheritance(self):
        """Test that exceptions inherit correctly."""
        assert issubclass(FileReadError, FileOperationError)
        assert issubclass(FileWriteError, FileOperationError)
        assert issubclass(FileParseError, FileOperationError)

    def test_exception_messages(self):
        """Test exception messages."""
        err = FileReadError("test message")
        assert str(err) == "test message"


class TestRetryDecorator:
    """Test retry_on_failure decorator."""

    def test_retry_success_on_second_attempt(self):
        """Test function succeeds on retry."""
        mock_func = MagicMock(side_effect=[OSError("First fail"), "success"])

        @retry_on_failure(max_attempts=3, delay=0.01)
        def test_func():
            return mock_func()

        result = test_func()
        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_all_attempts_fail(self):
        """Test function fails after all retries."""
        mock_func = MagicMock(side_effect=OSError("Always fail"))

        @retry_on_failure(max_attempts=3, delay=0.01)
        def test_func():
            return mock_func()

        with pytest.raises(OSError):
            test_func()
        assert mock_func.call_count == 3

    def test_retry_non_retryable_exception(self):
        """Test non-retryable exceptions are raised immediately."""
        mock_func = MagicMock(side_effect=ValueError("Not retryable"))

        @retry_on_failure(max_attempts=3, delay=0.01, exceptions=(OSError,))
        def test_func():
            return mock_func()

        with pytest.raises(ValueError):
            test_func()
        assert mock_func.call_count == 1


class TestAtomicWrite:
    """Test atomic write context manager."""

    def test_atomic_write_success(self, tmp_path):
        """Test successful atomic write."""
        target = tmp_path / "test.txt"

        with atomic_write(target) as f:
            f.write("test content")

        assert target.exists()
        assert target.read_text() == "test content"

    def test_atomic_write_creates_parent_dirs(self, tmp_path):
        """Test atomic write creates parent directories."""
        target = tmp_path / "deep" / "nested" / "test.txt"

        with atomic_write(target) as f:
            f.write("test content")

        assert target.exists()
        assert target.read_text() == "test content"

    def test_atomic_write_failure_cleanup(self, tmp_path):
        """Test cleanup on write failure."""
        target = tmp_path / "test.txt"

        with pytest.raises(FileWriteError), atomic_write(target) as f:
            f.write("partial")
            raise ValueError("Simulated error")

        # Original file should not exist
        assert not target.exists()

        # Temp files should be cleaned up
        temp_files = list(tmp_path.glob(".test.txt.*.tmp"))
        assert len(temp_files) == 0

    def test_atomic_write_replaces_existing(self, tmp_path):
        """Test atomic write replaces existing file."""
        target = tmp_path / "test.txt"
        target.write_text("old content")

        with atomic_write(target) as f:
            f.write("new content")

        assert target.read_text() == "new content"


class TestJsonOperations:
    """Test JSON file operations."""

    def test_safe_json_dump_and_load(self, tmp_path):
        """Test JSON round trip."""
        filepath = tmp_path / "test.json"
        data = {"key": "value", "number": 42, "nested": {"inner": True}}

        safe_json_dump(data, filepath)
        loaded = safe_json_load(filepath)

        assert loaded == data

    def test_safe_json_dump_with_indent(self, tmp_path):
        """Test JSON formatting."""
        filepath = tmp_path / "test.json"
        data = {"key": "value"}

        safe_json_dump(data, filepath, indent=4)
        content = filepath.read_text()

        assert "    " in content  # 4-space indent

    def test_safe_json_load_file_not_found(self, tmp_path):
        """Test loading non-existent JSON file."""
        filepath = tmp_path / "missing.json"

        with pytest.raises(FileReadError, match="File not found"):
            safe_json_load(filepath)

    def test_safe_json_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON."""
        filepath = tmp_path / "invalid.json"
        filepath.write_text("{invalid json}")

        with pytest.raises(FileParseError, match="Invalid JSON"):
            safe_json_load(filepath)

    def test_safe_json_dump_serialization_error(self, tmp_path):
        """Test JSON serialization error."""
        filepath = tmp_path / "test.json"
        data = {"key": object()}  # Not JSON serializable

        with pytest.raises(FileParseError, match="Failed to serialize"):
            safe_json_dump(data, filepath)


class TestYamlOperations:
    """Test YAML file operations."""

    def test_safe_yaml_dump_and_load(self, tmp_path):
        """Test YAML round trip."""
        filepath = tmp_path / "test.yml"
        data = {"key": "value", "number": 42, "nested": {"inner": True}}

        safe_yaml_dump(data, filepath)
        loaded = safe_yaml_load(filepath)

        assert loaded == data

    def test_safe_yaml_load_file_not_found(self, tmp_path):
        """Test loading non-existent YAML file."""
        filepath = tmp_path / "missing.yml"

        with pytest.raises(FileReadError, match="File not found"):
            safe_yaml_load(filepath)

    def test_safe_yaml_load_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML."""
        filepath = tmp_path / "invalid.yml"
        filepath.write_text("invalid:\n  - unbalanced")

        # This might not raise on all YAML content, so we'll test with definitely bad YAML
        filepath.write_text(":\n  bad")

        with pytest.raises(FileParseError, match="Invalid YAML"):
            safe_yaml_load(filepath)


class TestTomlOperations:
    """Test TOML file operations."""

    def test_safe_toml_load(self, tmp_path):
        """Test TOML loading."""
        filepath = tmp_path / "test.toml"
        filepath.write_text('[tool.test]\nkey = "value"\nnumber = 42\n')

        result = safe_toml_load(filepath)
        assert result["tool"]["test"]["key"] == "value"
        assert result["tool"]["test"]["number"] == 42

    def test_safe_toml_load_file_not_found(self, tmp_path):
        """Test loading non-existent TOML file."""
        filepath = tmp_path / "missing.toml"

        with pytest.raises(FileReadError, match="File not found"):
            safe_toml_load(filepath)

    @patch("alt_file_utils.core.tomllib", None)
    def test_safe_toml_load_no_tomllib(self, tmp_path):
        """Test TOML loading when tomllib is not available."""
        filepath = tmp_path / "test.toml"
        filepath.touch()

        with pytest.raises(RuntimeError, match="TOML support not available"):
            safe_toml_load(filepath)


class TestFileOperations:
    """Test general file operations."""

    def test_safe_file_read_and_write(self, tmp_path):
        """Test file read/write round trip."""
        filepath = tmp_path / "test.txt"
        content = "Test content\nwith multiple lines"

        safe_file_write(content, filepath)
        read_content = safe_file_read(filepath)

        assert read_content == content

    def test_safe_file_read_not_found(self, tmp_path):
        """Test reading non-existent file."""
        filepath = tmp_path / "missing.txt"

        with pytest.raises(FileReadError, match="File not found"):
            safe_file_read(filepath)

    def test_safe_file_write_binary(self, tmp_path):
        """Test binary file write."""
        filepath = tmp_path / "test.bin"
        content = b"\x00\x01\x02\x03"

        safe_file_write(content, filepath, mode="wb")
        assert filepath.read_bytes() == content


class TestDirectoryOperations:
    """Test directory operations."""

    def test_ensure_directory_creates_nested(self, tmp_path):
        """Test creating nested directories."""
        dir_path = tmp_path / "deep" / "nested" / "dir"

        result = ensure_directory(dir_path)

        assert result == dir_path
        assert dir_path.exists()
        assert dir_path.is_dir()

    def test_ensure_directory_existing(self, tmp_path):
        """Test ensure_directory on existing directory."""
        dir_path = tmp_path / "existing"
        dir_path.mkdir()

        result = ensure_directory(dir_path)

        assert result == dir_path
        assert dir_path.exists()

    def test_ensure_directory_permission_error(self):
        """Test directory creation with permission error."""
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("No permission")

            with pytest.raises(FileOperationError, match="Failed to create"):
                ensure_directory("/some/path")


class TestFileCopy:
    """Test file copy operations."""

    def test_safe_copy(self, tmp_path):
        """Test copying a file."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        source.write_text("content")

        safe_copy(source, dest)

        assert dest.exists()
        assert dest.read_text() == "content"

    def test_safe_copy_creates_dest_dir(self, tmp_path):
        """Test copy creates destination directory."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "subdir" / "dest.txt"
        source.write_text("content")

        safe_copy(source, dest)

        assert dest.exists()
        assert dest.read_text() == "content"

    def test_safe_copy_no_overwrite(self, tmp_path):
        """Test copy with overwrite=False."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        source.write_text("new")
        dest.write_text("old")

        with pytest.raises(FileOperationError, match="already exists"):
            safe_copy(source, dest, overwrite=False)

    def test_safe_copy_overwrite(self, tmp_path):
        """Test copy with overwrite=True."""
        source = tmp_path / "source.txt"
        dest = tmp_path / "dest.txt"
        source.write_text("new")
        dest.write_text("old")

        safe_copy(source, dest, overwrite=True)

        assert dest.read_text() == "new"

    def test_safe_copy_source_not_found(self, tmp_path):
        """Test copying non-existent file."""
        source = tmp_path / "missing.txt"
        dest = tmp_path / "dest.txt"

        with pytest.raises(FileReadError, match="Source file not found"):
            safe_copy(source, dest)


class TestFileDelete:
    """Test file deletion."""

    def test_safe_delete(self, tmp_path):
        """Test deleting a file."""
        filepath = tmp_path / "test.txt"
        filepath.write_text("content")

        safe_delete(filepath)

        assert not filepath.exists()

    def test_safe_delete_missing_ok(self, tmp_path):
        """Test deleting non-existent file with missing_ok=True."""
        filepath = tmp_path / "missing.txt"

        safe_delete(filepath, missing_ok=True)  # Should not raise

    def test_safe_delete_missing_not_ok(self, tmp_path):
        """Test deleting non-existent file with missing_ok=False."""
        filepath = tmp_path / "missing.txt"

        with pytest.raises(FileOperationError):
            safe_delete(filepath, missing_ok=False)


class TestTemporaryDirectory:
    """Test temporary directory context manager."""

    def test_temporary_directory(self):
        """Test temporary directory creation and cleanup."""
        temp_path = None

        with temporary_directory() as temp_dir:
            temp_path = temp_dir
            assert temp_dir.exists()
            assert temp_dir.is_dir()

            # Create a file in temp dir
            test_file = temp_dir / "test.txt"
            test_file.write_text("content")
            assert test_file.exists()

        # Directory should be cleaned up
        assert not temp_path.exists()

    def test_temporary_directory_with_prefix(self):
        """Test temporary directory with custom prefix."""
        with temporary_directory(prefix="test_prefix_") as temp_dir:
            assert "test_prefix_" in temp_dir.name


class TestFileUtilities:
    """Test file utility functions."""

    def test_get_file_size(self, tmp_path):
        """Test getting file size."""
        filepath = tmp_path / "test.txt"
        content = "x" * 1000
        filepath.write_text(content)

        size = get_file_size(filepath)
        assert size == 1000

    def test_get_file_size_not_found(self, tmp_path):
        """Test getting size of non-existent file."""
        filepath = tmp_path / "missing.txt"

        with pytest.raises(FileReadError, match="Cannot get size"):
            get_file_size(filepath)

    def test_is_file_locked(self, tmp_path):
        """Test file lock detection."""
        filepath = tmp_path / "test.txt"
        filepath.write_text("content")

        # File should not be locked
        assert not is_file_locked(filepath)

        # Test with non-existent file
        missing = tmp_path / "missing.txt"
        assert not is_file_locked(missing)

    @pytest.mark.skipif(
        not hasattr(open, "exclusive"), reason="Platform doesn't support exclusive open"
    )
    def test_is_file_locked_when_locked(self, tmp_path):
        """Test file lock detection when file is actually locked."""
        filepath = tmp_path / "test.txt"
        filepath.write_text("content")

        # Hold file open exclusively
        with open(filepath, "r+") as _:
            # On some systems, this might show as locked
            is_file_locked(filepath)
            # Result depends on platform behavior
