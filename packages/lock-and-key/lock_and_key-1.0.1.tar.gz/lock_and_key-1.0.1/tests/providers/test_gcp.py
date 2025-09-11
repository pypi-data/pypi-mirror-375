"""Unit tests for lock_and_key.providers.gcp module."""

import unittest
from unittest.mock import patch

from lock_and_key.types import GCPCreds, CloudProviderBase
from lock_and_key.providers.gcp import GCPProvider


class TestGCPProvider(unittest.TestCase):
    """Test cases for GCPProvider class."""

    def setUp(self):
        """Set up test fixtures."""
        self.provider = GCPProvider()

    def test_inheritance(self):
        """Test that GCPProvider inherits from CloudProviderBase."""
        self.assertIsInstance(self.provider, CloudProviderBase)

    def test_class_attributes(self):
        """Test GCPProvider class attributes."""
        self.assertEqual(self.provider.name, "GCP")
        self.assertEqual(self.provider.description, "Google Cloud Platform")

    @patch('click.prompt')
    def test_prompt_creds_with_file_path(self, mock_prompt):
        """Test prompting for credentials with file path."""
        mock_prompt.return_value = "/path/to/service-account.json"
        
        creds = self.provider.prompt_creds()
        
        self.assertIsInstance(creds, GCPCreds)
        self.assertEqual(creds.creds_path, "/path/to/service-account.json")
        self.assertIsNone(creds.creds_json)
        
        # Should only prompt once for file path
        self.assertEqual(mock_prompt.call_count, 1)

    @patch('click.prompt')
    def test_prompt_creds_with_json_content(self, mock_prompt):
        """Test prompting for credentials with JSON content."""
        json_content = '{"type": "service_account", "project_id": "test-project"}'
        # First prompt returns empty string (no file path)
        # Second prompt returns JSON content
        mock_prompt.side_effect = ["", json_content]
        
        creds = self.provider.prompt_creds()
        
        self.assertIsInstance(creds, GCPCreds)
        self.assertIsNone(creds.creds_path)
        self.assertEqual(creds.creds_json, json_content)
        
        # Should prompt twice: file path, then JSON content
        self.assertEqual(mock_prompt.call_count, 2)

    @patch('click.prompt')
    def test_prompt_creds_file_path_prompt_text(self, mock_prompt):
        """Test that file path prompt has correct text."""
        mock_prompt.return_value = "/test/path.json"
        
        self.provider.prompt_creds()
        
        # Check the prompt text for file path
        first_call = mock_prompt.call_args_list[0]
        prompt_text = first_call[0][0]
        self.assertIn("GCP service account JSON file", prompt_text)
        self.assertIn("leave blank to paste JSON", prompt_text)

    @patch('click.prompt')
    def test_prompt_creds_json_prompt_text(self, mock_prompt):
        """Test that JSON prompt has correct text."""
        mock_prompt.side_effect = ["", '{"test": "json"}']
        
        self.provider.prompt_creds()
        
        # Check the prompt text for JSON content
        second_call = mock_prompt.call_args_list[1]
        prompt_text = second_call[0][0]
        self.assertIn("GCP service account JSON", prompt_text)

    def test_run_analysis_inherited(self):
        """Test that run_analysis method is inherited from base class."""
        # This tests the inherited behavior
        creds = GCPCreds(creds_path="/test/path.json")
        result = self.provider.run_analysis(creds)
        
        self.assertEqual(result.provider, "GCP")
        self.assertIn("gcp", result.report_path.lower())


if __name__ == '__main__':
    unittest.main()