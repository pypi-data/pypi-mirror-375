"""
Constants for ALT-file-utils package.
"""

# Package metadata
PACKAGE_NAME = "alt_file_utils"
PACKAGE_VERSION = "0.1.0"

# Retry configuration
DEFAULT_RETRY_MAX_ATTEMPTS = 3
DEFAULT_RETRY_DELAY = 0.5  # seconds

# File operation limits
MAX_FILE_SIZE_MB = 100  # Maximum file size for safe operations
TEMP_FILE_PREFIX = ".tmp_"
TEMP_FILE_SUFFIX = ".tmp"

# JSON formatting
JSON_INDENT_SPACES = 2

# Encoding
DEFAULT_ENCODING = "utf-8"
FILE_ENCODING = "utf-8"
