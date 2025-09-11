"""Legacy test file - functionality moved to tests/core/test_scanner.py."""

# This file is kept for backward compatibility
# All scanner tests have been moved to tests/core/test_scanner.py
# to match the source code structure

import unittest


class TestLegacyScanner(unittest.TestCase):
    """Legacy test class - see tests/core/test_scanner.py for actual tests."""
    
    def test_legacy_notice(self):
        """Test to indicate tests have been moved."""
        self.assertTrue(True, "Scanner tests moved to tests/core/test_scanner.py")


if __name__ == "__main__":
    unittest.main()