# Lock & Key Architecture

## Project Structure

```
lock_and_key/
├── __init__.py              # Main package exports
├── __about__.py             # Version information
├── cli.py                   # Command-line interface
├── core/                    # Core functionality
│   ├── __init__.py
│   ├── scanner.py           # Main scanner class
│   └── ui.py               # UI utilities
├── models/                  # Data models
│   ├── __init__.py
│   ├── credentials.py       # Credential models
│   └── scan_results.py     # Scan result models
├── providers/              # Cloud provider implementations
│   ├── __init__.py
│   ├── base.py             # Base provider interface
│   ├── aws.py              # AWS provider
│   ├── gcp.py              # GCP provider
│   └── azure.py            # Azure provider
├── config/                 # Configuration management
│   ├── __init__.py
│   └── settings.py         # Application settings
├── exceptions/             # Custom exceptions
│   ├── __init__.py
│   └── base.py             # Base exception classes
└── modules/                # Legacy analysis modules (to be refactored)
    └── aws/
        ├── clients/
        └── object_classes/
```

## Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Providers are pluggable and testable
3. **Type Safety**: Full type hints throughout the codebase
4. **Error Handling**: Custom exceptions for different error types
5. **Extensibility**: Easy to add new cloud providers

## Key Components

### Core Scanner (`core/scanner.py`)
- Main orchestration logic
- Handles interactive and programmatic workflows
- Manages provider selection and credential building

### Providers (`providers/`)
- Pluggable cloud provider implementations
- Each provider implements the same interface
- Easy to add new providers

### Models (`models/`)
- Pydantic models for data validation
- Separate credential and result models
- Type-safe data structures

### CLI (`cli.py`)
- Clean Click-based command interface
- Interactive and non-interactive modes
- Proper argument validation

## Usage

### Interactive Mode
```bash
lock-and-key interactive
```

### Direct Scan
```bash
lock-and-key scan --provider AWS --profile my-profile
```

### Programmatic Usage
```python
from lock_and_key import LockAndKeyScanner

scanner = LockAndKeyScanner()
scanner.run_interactive()
```