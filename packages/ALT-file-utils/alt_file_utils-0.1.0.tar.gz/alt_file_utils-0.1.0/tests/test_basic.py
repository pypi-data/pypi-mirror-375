"""Basic tests to verify package structure and imports."""


def test_package_imports():
    """Test that all main components can be imported."""
    # Core functions

    # Exceptions

    # Constants
    from alt_file_utils import PACKAGE_NAME, PACKAGE_VERSION

    assert PACKAGE_NAME == "alt_file_utils"
    assert PACKAGE_VERSION == "0.1.0"


def test_version():
    """Test that version is accessible."""
    import alt_file_utils

    assert hasattr(alt_file_utils, "__version__")
    assert alt_file_utils.__version__ == "0.1.0"
