#!/usr/bin/env python3
"""Test runner for Lock & Key unit tests."""

import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def discover_and_run_tests():
    """Discover and run all unit tests in the tests directory."""
    # Start discovery from the tests directory
    loader = unittest.TestLoader()
    start_dir = Path(__file__).parent
    
    # Discover all test files matching the pattern test_*.py
    suite = loader.discover(
        start_dir=str(start_dir),
        pattern='test_*.py',
        top_level_dir=str(project_root)
    )
    
    # Run the tests with verbose output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = discover_and_run_tests()
    sys.exit(exit_code)