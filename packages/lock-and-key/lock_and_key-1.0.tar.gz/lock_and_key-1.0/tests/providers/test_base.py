"""Unit tests for lock_and_key.providers.base module."""

import unittest
from abc import ABC

from lock_and_key.types import ScanResult, CloudProviderBase


class TestCloudProviderBase(unittest.TestCase):
    """Test cases for CloudProviderBase abstract class."""

    def test_is_abstract_class(self):
        """Test that CloudProviderBase is an abstract class."""
        self.assertTrue(issubclass(CloudProviderBase, ABC))

    def test_cannot_instantiate_directly(self):
        """Test that CloudProviderBase cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            CloudProviderBase()

    def test_run_analysis_default_implementation(self):
        """Test the default run_analysis implementation."""
        # Create a concrete implementation for testing
        class TestProvider(CloudProviderBase):
            name = "TestProvider"
            description = "Test Provider Description"
            
            def prompt_creds(self):
                return {"test": "credentials"}
        
        provider = TestProvider()
        result = provider.run_analysis({"test": "creds"})
        
        self.assertIsInstance(result, ScanResult)
        self.assertEqual(result.provider, "TestProvider")
        self.assertEqual(result.account_id, "123456789012")
        self.assertEqual(result.issues_found, 3)
        self.assertEqual(result.least_privilege_violations, 2)
        self.assertEqual(result.high_risk_permissions, 1)
        self.assertIn("TestProvider", result.summary)
        self.assertIn("testprovider", result.report_path.lower())

    def test_abstract_methods_required(self):
        """Test that abstract methods must be implemented."""
        # Missing prompt_creds implementation
        class IncompleteProvider(CloudProviderBase):
            name = "Incomplete"
            description = "Incomplete Provider"
        
        with self.assertRaises(TypeError):
            IncompleteProvider()

    def test_concrete_implementation_works(self):
        """Test that a complete concrete implementation works."""
        class CompleteProvider(CloudProviderBase):
            name = "Complete"
            description = "Complete Provider"
            
            def prompt_creds(self):
                return {"complete": "credentials"}
        
        # Should not raise an exception
        provider = CompleteProvider()
        self.assertEqual(provider.name, "Complete")
        self.assertEqual(provider.description, "Complete Provider")
        
        # Test that prompt_creds works
        creds = provider.prompt_creds()
        self.assertEqual(creds, {"complete": "credentials"})


if __name__ == '__main__':
    unittest.main()