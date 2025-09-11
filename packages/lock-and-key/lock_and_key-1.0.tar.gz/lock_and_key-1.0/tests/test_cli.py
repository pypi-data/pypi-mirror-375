"""Unit tests for lock_and_key.cli module."""

import unittest
from unittest.mock import Mock, patch

from click.testing import CliRunner

from lock_and_key.cli import cli, interactive, scan


class TestCLI(unittest.TestCase):
    """Test cases for CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_group_exists(self):
        """Test that CLI group is properly defined."""
        result = self.runner.invoke(cli, ['--help'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Lock & Key Cloud Scanner CLI', result.output)

    @patch('lock_and_key.cli.LockAndKeyScanner')
    def test_interactive_command(self, mock_scanner_class):
        """Test interactive command execution."""
        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner
        
        result = self.runner.invoke(interactive)
        
        self.assertEqual(result.exit_code, 0)
        mock_scanner_class.assert_called_once()
        mock_scanner.run_interactive.assert_called_once()

    @patch('lock_and_key.cli.LockAndKeyScanner')
    def test_scan_command_aws(self, mock_scanner_class):
        """Test scan command with AWS provider."""
        mock_scanner = Mock()
        mock_scanner_class.return_value = mock_scanner
        
        result = self.runner.invoke(scan, [
            '--provider', 'AWS',
            '--profile', 'test-profile'
        ])
        
        self.assertEqual(result.exit_code, 0)
        mock_scanner_class.assert_called_once()
        mock_scanner.run_single_provider.assert_called_once_with(
            'AWS', 
            profile='test-profile',
            access_key=None,
            secret_key=None,
            region=None,
            creds_path=None,
            creds_json=None,
            client_id=None,
            secret=None,
            tenant_id=None,
            subscription_id=None
        )

    def test_scan_command_missing_provider(self):
        """Test scan command fails without provider."""
        result = self.runner.invoke(scan)
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('Missing option', result.output)

    def test_scan_command_invalid_provider(self):
        """Test scan command with invalid provider choice."""
        result = self.runner.invoke(scan, ['--provider', 'INVALID'])
        self.assertNotEqual(result.exit_code, 0)


if __name__ == '__main__':
    unittest.main()