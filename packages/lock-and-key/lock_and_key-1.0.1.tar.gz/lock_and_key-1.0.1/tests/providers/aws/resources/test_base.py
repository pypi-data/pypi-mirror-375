"""Unit tests for AWS base service."""

import unittest
from unittest.mock import Mock, patch
import boto3

from lock_and_key.types import AWSCreds
from lock_and_key.providers.aws.resources.base import AWSServiceBase


class TestAWSServiceBase(unittest.TestCase):
    """Test cases for AWSServiceBase class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = Mock(spec=boto3.Session)
        self.service = AWSServiceBase(self.mock_session)

    def test_init(self):
        """Test service initialization."""
        self.assertEqual(self.service.session, self.mock_session)

    @patch('boto3.Session')
    def test_from_creds_with_profile(self, mock_session):
        """Test creating service from profile credentials."""
        creds = AWSCreds(profile="test-profile")
        
        service = AWSServiceBase.from_creds(creds)
        
        mock_session.assert_called_once_with(profile_name="test-profile")
        self.assertIsInstance(service, AWSServiceBase)

    @patch('boto3.Session')
    def test_from_creds_with_keys(self, mock_session):
        """Test creating service from access key credentials."""
        creds = AWSCreds(access_key="AKIA123", secret_key="secret", region="us-west-2")
        
        service = AWSServiceBase.from_creds(creds)
        
        mock_session.assert_called_once_with(
            aws_access_key_id="AKIA123",
            aws_secret_access_key="secret",
            region_name="us-west-2"
        )

    @patch('boto3.Session')
    def test_from_creds_default_region(self, mock_session):
        """Test default region is used when none provided."""
        creds = AWSCreds(access_key="AKIA123", secret_key="secret")
        
        AWSServiceBase.from_creds(creds)
        
        mock_session.assert_called_once_with(
            aws_access_key_id="AKIA123",
            aws_secret_access_key="secret",
            region_name="us-east-1"
        )

    def test_get_account_id(self):
        """Test getting AWS account ID."""
        mock_sts = Mock()
        mock_sts.get_caller_identity.return_value = {"Account": "123456789012"}
        self.mock_session.client.return_value = mock_sts
        
        account_id = self.service.get_account_id()
        
        self.assertEqual(account_id, "123456789012")
        self.mock_session.client.assert_called_once_with("sts")


if __name__ == '__main__':
    unittest.main()