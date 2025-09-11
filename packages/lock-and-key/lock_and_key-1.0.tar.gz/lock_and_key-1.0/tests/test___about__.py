"""Unit tests for lock_and_key.__about__ module."""

import unittest

from lock_and_key import __about__


class TestAbout(unittest.TestCase):
    """Test cases for version information."""

    def test_version_exists(self):
        """Test that __version__ attribute exists."""
        self.assertTrue(hasattr(__about__, '__version__'))

    def test_version_format(self):
        """Test that version follows semantic versioning format."""
        version = __about__.__version__
        self.assertIsInstance(version, str)
        # Basic semantic version check (x.y.z)
        parts = version.split('.')
        self.assertEqual(len(parts), 3)
        for part in parts:
            self.assertTrue(part.isdigit())


if __name__ == '__main__':
    unittest.main()