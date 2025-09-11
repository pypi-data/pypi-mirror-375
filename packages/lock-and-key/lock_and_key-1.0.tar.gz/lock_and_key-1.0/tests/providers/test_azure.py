"""Unit tests for lock_and_key.providers.azure module."""

import unittest
from unittest.mock import patch

from lock_and_key.types import AzureCreds, CloudProviderBase
from lock_and_key.providers.azure import AzureProvider


class TestAzureProvider(unittest.TestCase):
    """Test cases for AzureProvider class."""

    def setUp(self):
        """Set up test fixtures."""
        self.provider = AzureProvider()

    def test_inheritance(self):
        """Test that AzureProvider inherits from CloudProviderBase."""
        self.assertIsInstance(self.provider, CloudProviderBase)

    def test_class_attributes(self):
        """Test AzureProvider class attributes."""
        self.assertEqual(self.provider.name, "Azure")
        self.assertEqual(self.provider.description, "Microsoft Azure")

    @patch('click.prompt')
    def test_prompt_creds_with_file_path(self, mock_prompt):
        """Test prompting for credentials with file path."""
        mock_prompt.return_value = "/path/to/azure-creds.json"
        
        creds = self.provider.prompt_creds()
        
        self.assertIsInstance(creds, AzureCreds)
        self.assertEqual(creds.creds_path, "/path/to/azure-creds.json")
        self.assertIsNone(creds.client_id)
        self.assertIsNone(creds.secret)
        self.assertIsNone(creds.tenant_id)
        self.assertIsNone(creds.subscription_id)
        
        # Should only prompt once for file path
        self.assertEqual(mock_prompt.call_count, 1)

    @patch('click.prompt')
    def test_prompt_creds_with_manual_values(self, mock_prompt):
        """Test prompting for credentials with manual input."""
        # First prompt returns empty string (no file path)
        # Then prompts for client_id, secret, tenant_id, subscription_id
        mock_prompt.side_effect = [
            "",  # No file path
            "test-client-id",
            "test-client-secret", 
            "test-tenant-id",
            "test-subscription-id"
        ]
        
        creds = self.provider.prompt_creds()
        
        self.assertIsInstance(creds, AzureCreds)
        self.assertIsNone(creds.creds_path)
        self.assertEqual(creds.client_id, "test-client-id")
        self.assertEqual(creds.secret, "test-client-secret")
        self.assertEqual(creds.tenant_id, "test-tenant-id")
        self.assertEqual(creds.subscription_id, "test-subscription-id")
        
        # Should prompt 5 times: file path + 4 manual fields
        self.assertEqual(mock_prompt.call_count, 5)

    @patch('click.prompt')
    def test_prompt_creds_file_path_prompt_text(self, mock_prompt):
        """Test that file path prompt has correct text."""
        mock_prompt.return_value = "/test/path.json"
        
        self.provider.prompt_creds()
        
        # Check the prompt text for file path
        first_call = mock_prompt.call_args_list[0]
        prompt_text = first_call[0][0]
        self.assertIn("Azure credentials file", prompt_text)
        self.assertIn("leave blank to enter manually", prompt_text)

    @patch('click.prompt')
    def test_prompt_creds_manual_prompts(self, mock_prompt):
        """Test manual credential prompts have correct text."""
        mock_prompt.side_effect = ["", "client", "secret", "tenant", "subscription"]
        
        self.provider.prompt_creds()
        
        # Check prompt texts for manual fields
        prompts = [call[0][0] for call in mock_prompt.call_args_list[1:]]
        
        self.assertIn("Azure Client ID", prompts[0])
        self.assertIn("Azure Client Secret", prompts[1])
        self.assertIn("Azure Tenant ID", prompts[2])
        self.assertIn("Azure Subscription ID", prompts[3])

    @patch('click.prompt')
    def test_prompt_creds_hide_secret_input(self, mock_prompt):
        """Test that client secret input is hidden."""
        mock_prompt.side_effect = ["", "client", "secret", "tenant", "subscription"]
        
        self.provider.prompt_creds()
        
        # Check that the client secret prompt has hide_input=True
        secret_call = mock_prompt.call_args_list[2]
        self.assertTrue(secret_call[1]['hide_input'])

    def test_run_analysis_inherited(self):
        """Test that run_analysis method is inherited from base class."""
        # This tests the inherited behavior
        creds = AzureCreds(client_id="test-client-id")
        result = self.provider.run_analysis(creds)
        
        self.assertEqual(result.provider, "Azure")
        self.assertIn("azure", result.report_path.lower())


if __name__ == '__main__':
    unittest.main()