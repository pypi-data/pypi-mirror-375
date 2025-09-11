"""Unit tests for lock_and_key.__init__ module."""

import unittest

import lock_and_key
from lock_and_key import (
    LockAndKeyScanner,
    PROVIDER_CLASSES,
    ScanResult,
    ScanSummary,
    __version__,
)


class TestInit(unittest.TestCase):
    """Test cases for package initialization and exports."""

    def test_version_import(self):
        """Test that __version__ is properly imported."""
        self.assertTrue(hasattr(lock_and_key, '__version__'))
        self.assertIsInstance(__version__, str)

    def test_scanner_import(self):
        """Test that LockAndKeyScanner is properly imported."""
        self.assertTrue(hasattr(lock_and_key, 'LockAndKeyScanner'))
        # Test that it's the correct class
        from lock_and_key.core.scanner import LockAndKeyScanner as OriginalScanner
        self.assertIs(LockAndKeyScanner, OriginalScanner)

    def test_models_import(self):
        """Test that model classes are properly imported."""
        self.assertTrue(hasattr(lock_and_key, 'ScanResult'))
        self.assertTrue(hasattr(lock_and_key, 'ScanSummary'))
        
        # Test that they're the correct classes
        from lock_and_key.types import ScanResult as OriginalScanResult
        from lock_and_key.types import ScanSummary as OriginalScanSummary
        self.assertIs(ScanResult, OriginalScanResult)
        self.assertIs(ScanSummary, OriginalScanSummary)

    def test_providers_import(self):
        """Test that PROVIDER_CLASSES is properly imported."""
        self.assertTrue(hasattr(lock_and_key, 'PROVIDER_CLASSES'))
        self.assertIsInstance(PROVIDER_CLASSES, dict)
        
        # Test that it contains expected providers
        expected_providers = {"AWS", "GCP", "Azure"}
        self.assertEqual(set(PROVIDER_CLASSES.keys()), expected_providers)

    def test_all_exports(self):
        """Test that __all__ contains all expected exports."""
        expected_exports = {
            "LockAndKeyScanner",
            "ScanResult", 
            "ScanSummary",
            "PROVIDER_CLASSES",
            "__version__"
        }
        self.assertEqual(set(lock_and_key.__all__), expected_exports)

    def test_all_exports_accessible(self):
        """Test that all items in __all__ are accessible."""
        for item in lock_and_key.__all__:
            self.assertTrue(hasattr(lock_and_key, item))

    def test_package_docstring(self):
        """Test that package has a docstring."""
        self.assertIsNotNone(lock_and_key.__doc__)
        self.assertIn("Lock & Key", lock_and_key.__doc__)


if __name__ == '__main__':
    unittest.main()