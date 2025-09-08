# ALT-file-utils

[![PyPI version](https://badge.fury.io/py/ALT-file-utils.svg)](https://badge.fury.io/py/ALT-file-utils)
[![Python Support](https://img.shields.io/pypi/pyversions/ALT-file-utils.svg)](https://pypi.org/project/ALT-file-utils/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Robust file I/O utilities for Python with atomic writes, retries, and comprehensive error handling.

## Features

- 🔒 **Atomic file writes** - Prevents corruption by writing to temp files and atomically replacing
- 🔄 **Automatic retries** - Configurable retry logic for transient failures
- 🛡️ **Comprehensive error handling** - Detailed exceptions for different failure modes
- 📁 **Safe file operations** - Read, write, copy, delete with proper error handling
- 🔧 **Multiple format support** - JSON, YAML, TOML with safe loading/dumping
- 🌐 **Cross-platform** - Works on Windows, macOS, and Linux
- 🐍 **Type hints** - Full typing support for better IDE integration

## Installation

```bash
pip install ALT-file-utils
```

For TOML support on Python < 3.11:
```bash
pip install "ALT-file-utils[toml]"
```

## Quick Start

### Atomic File Writing

```python
from alt_file_utils import atomic_write

# Write text file atomically
with atomic_write('output.txt') as f:
    f.write('Hello, World!')
    # File is written to a temporary location
# On successful completion, file is atomically moved to 'output.txt'
# On exception, temporary file is cleaned up automatically
```

### Safe JSON Operations

```python
from alt_file_utils import safe_json_dump, safe_json_load

# Write JSON safely with atomic write
data = {'name': 'example', 'value': 42}
safe_json_dump(data, 'data.json', indent=2)

# Read JSON with error handling
loaded_data = safe_json_load('data.json')
```

### Retry Mechanism

```python
from alt_file_utils import retry_on_failure
import time

@retry_on_failure(max_attempts=3, delay=1.0)
def flaky_file_operation():
    # This will retry up to 3 times with 1 second delay
    with open('important.txt', 'r') as f:
        return f.read()
```

### Safe File Operations

```python
from alt_file_utils import (
    safe_file_read, 
    safe_file_write,
    safe_copy,
    safe_delete,
    ensure_directory
)

# Read file safely
content = safe_file_read('input.txt')

# Write file safely with atomic operation
safe_file_write('Hello!', 'output.txt')

# Copy file safely
safe_copy('source.txt', 'destination.txt', overwrite=True)

# Delete file safely (missing_ok=True by default)
safe_delete('temp.txt')

# Ensure directory exists
ensure_directory('path/to/directory')
```

### Temporary Directory

```python
from alt_file_utils import temporary_directory

# Create and clean up temporary directory
with temporary_directory(prefix='myapp_') as temp_dir:
    temp_file = temp_dir / 'temp.txt'
    temp_file.write_text('Temporary data')
    # Do work with temporary files
# Directory and all contents are automatically cleaned up
```

### File Information

```python
from alt_file_utils import get_file_size, is_file_locked

# Get file size
size = get_file_size('large_file.bin')
print(f"File size: {size} bytes")

# Check if file is locked (platform-agnostic)
if is_file_locked('database.db'):
    print("File is currently locked")
```

## Error Handling

The library provides specific exceptions for different error cases:

```python
from alt_file_utils import (
    FileReadError,
    FileWriteError,
    FileParseError,
    FileOperationError
)

try:
    data = safe_json_load('config.json')
except FileReadError:
    # File doesn't exist or can't be read
    pass
except FileParseError:
    # File exists but JSON is invalid
    pass
```

## Advanced Usage

### Custom Retry Logic

```python
from alt_file_utils import retry_on_failure

# Customize retry behavior
@retry_on_failure(
    max_attempts=5,
    delay=0.5,
    exceptions=(IOError, OSError, TimeoutError)
)
def custom_operation():
    # Your code here
    pass
```

### YAML Support

```python
from alt_file_utils import safe_yaml_dump, safe_yaml_load

# Write YAML safely
config = {
    'database': {
        'host': 'localhost',
        'port': 5432
    }
}
safe_yaml_dump(config, 'config.yaml')

# Read YAML safely
loaded_config = safe_yaml_load('config.yaml')
```

### TOML Support

```python
from alt_file_utils import safe_toml_load

# Read TOML safely (write not supported by tomli)
settings = safe_toml_load('pyproject.toml')
```

## Development

```bash
# Clone the repository
git clone https://github.com/Avilir/ALT-file-utils.git
cd ALT-file-utils

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run type checks
mypy src

# Run linting
ruff check src tests

# Format code
black src tests
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

- **Avi Layani** - [GitHub](https://github.com/Avilir)

## See Also

- [ALT-time-utils](https://pypi.org/project/ALT-time-utils/) - Time utilities
- [ALT-error-handling](https://pypi.org/project/ALT-error-handling/) - Error handling utilities
