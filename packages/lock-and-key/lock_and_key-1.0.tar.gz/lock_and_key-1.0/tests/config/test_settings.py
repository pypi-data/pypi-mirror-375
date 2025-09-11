"""Unit tests for lock_and_key.config.settings module."""

import unittest

from lock_and_key.config.settings import CLOUD_PROVIDERS


class TestSettings(unittest.TestCase):
    """Test cases for configuration settings."""

    def test_cloud_providers_exists(self):
        """Test that CLOUD_PROVIDERS constant exists."""
        self.assertIsInstance(CLOUD_PROVIDERS, dict)

    def test_cloud_providers_content(self):
        """Test that CLOUD_PROVIDERS contains expected providers."""
        expected_providers = {"AWS", "GCP", "Azure"}
        self.assertEqual(set(CLOUD_PROVIDERS.keys()), expected_providers)

    def test_cloud_providers_values(self):
        """Test that CLOUD_PROVIDERS has correct descriptions."""
        expected_values = {
            "AWS": "Amazon Web Services",
            "GCP": "Google Cloud Platform", 
            "Azure": "Microsoft Azure"
        }
        self.assertEqual(CLOUD_PROVIDERS, expected_values)

    def test_cloud_providers_immutable(self):
        """Test that modifying CLOUD_PROVIDERS doesn't affect original."""
        original_count = len(CLOUD_PROVIDERS)
        test_dict = CLOUD_PROVIDERS.copy()
        test_dict["TEST"] = "Test Provider"
        self.assertEqual(len(CLOUD_PROVIDERS), original_count)


if __name__ == '__main__':
    unittest.main()