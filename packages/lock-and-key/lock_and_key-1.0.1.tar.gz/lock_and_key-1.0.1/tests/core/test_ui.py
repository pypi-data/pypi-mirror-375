"""Unit tests for lock_and_key.core.ui module."""

import unittest
from unittest.mock import patch

from lock_and_key.core.ui import print_banner


class TestUI(unittest.TestCase):
    """Test cases for UI utilities."""

    @patch('lock_and_key.core.ui.Console')
    def test_print_banner(self, mock_console_class):
        """Test that print_banner creates console and prints panel."""
        mock_console = mock_console_class.return_value
        
        print_banner()
        
        mock_console_class.assert_called_once()
        mock_console.print.assert_called_once()
        
        # Verify the panel was created with correct content
        call_args = mock_console.print.call_args[0][0]
        self.assertEqual(call_args.title, 'Lock & Key Cloud Scanner')

    @patch('rich.console.Console.print')
    def test_print_banner_content(self, mock_print):
        """Test that banner contains expected content."""
        print_banner()
        
        mock_print.assert_called_once()
        # Check that the panel contains the ASCII art and title
        panel_arg = mock_print.call_args[0][0]
        self.assertIn('Lock & Key Cloud Scanner', panel_arg.title)


if __name__ == '__main__':
    unittest.main()