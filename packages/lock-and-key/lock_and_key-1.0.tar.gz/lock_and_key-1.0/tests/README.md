# Lock & Key Test Suite

This directory contains comprehensive unit tests for the Lock & Key cloud security scanner.

## Test Structure

The test directory mirrors the source code structure:

```
tests/
├── config/
│   ├── __init__.py
│   └── test_settings.py          # Tests for config.settings
├── core/
│   ├── __init__.py
│   ├── test_scanner.py           # Tests for core.scanner
│   └── test_ui.py                # Tests for core.ui
├── exceptions/
│   ├── __init__.py
│   └── test_base.py              # Tests for exceptions.base
├── models/
│   ├── __init__.py
│   ├── test_credentials.py       # Tests for models.credentials
│   └── test_scan_results.py      # Tests for models.scan_results
├── providers/
│   ├── __init__.py
│   ├── test_base.py              # Tests for providers.base
│   ├── test_aws.py               # Tests for providers.aws
│   ├── test_gcp.py               # Tests for providers.gcp
│   └── test_azure.py             # Tests for providers.azure
├── test___about__.py             # Tests for __about__.py
├── test___init__.py              # Tests for __init__.py
├── test_cli.py                   # Tests for cli.py
├── test_scanner.py               # Legacy test file (redirects)
├── run_tests.py                  # Test runner script
└── README.md                     # This file
```

## Running Tests

### Run All Tests
```bash
# From project root
python -m pytest tests/

# Or using the test runner
python tests/run_tests.py

# Or using unittest discovery
python -m unittest discover tests/
```

### Run Specific Test Files
```bash
# Test a specific module
python -m unittest tests.core.test_scanner

# Test a specific class
python -m unittest tests.core.test_scanner.TestLockAndKeyScanner

# Test a specific method
python -m unittest tests.core.test_scanner.TestLockAndKeyScanner.test_scanner_initialization
```

### Run Tests by Category
```bash
# Core functionality tests
python -m unittest discover tests/core/

# Provider tests
python -m unittest discover tests/providers/

# Model tests  
python -m unittest discover tests/models/
```

## Test Coverage

The test suite covers:

- **Core Scanner Logic**: Interactive workflows, credential building, provider selection
- **CLI Interface**: Command parsing, argument validation, error handling
- **Cloud Providers**: AWS, GCP, and Azure credential prompting and validation
- **Data Models**: Credential classes, scan results, summary generation
- **Configuration**: Settings validation and provider definitions
- **Exception Handling**: Custom exception classes and inheritance
- **UI Components**: Banner printing and console output

## Test Best Practices

### Test Structure
- Each test file mirrors its corresponding source file
- Test classes use descriptive names (e.g., `TestLockAndKeyScanner`)
- Test methods start with `test_` and describe what they test
- Setup and teardown methods are used for common fixtures

### Documentation
- All test files include module docstrings
- Test classes include class docstrings
- Individual test methods include docstrings explaining their purpose
- Comments explain complex test logic or mocking scenarios

### Mocking
- External dependencies are mocked using `unittest.mock`
- User input is mocked for CLI testing
- Console output is mocked for UI testing
- Provider implementations use base class testing patterns

### Assertions
- Tests use descriptive assertion methods
- Multiple related assertions are grouped logically
- Error conditions are tested with `assertRaises`
- Mock calls are verified with `assert_called_*` methods

## Adding New Tests

When adding new functionality:

1. Create corresponding test files in the same directory structure
2. Follow the naming convention: `test_<module_name>.py`
3. Include comprehensive docstrings
4. Test both success and failure cases
5. Mock external dependencies
6. Verify all public methods and edge cases

## Dependencies

Test dependencies are minimal and use standard library modules:
- `unittest` - Core testing framework
- `unittest.mock` - Mocking functionality
- `click.testing` - CLI testing utilities (for CLI tests)

No additional test dependencies are required beyond what's needed for the main application.