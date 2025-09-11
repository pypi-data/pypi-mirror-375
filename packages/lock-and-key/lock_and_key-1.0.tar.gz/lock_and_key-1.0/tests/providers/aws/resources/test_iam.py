"""Unit tests for AWS IAM service."""

import unittest
from unittest.mock import Mock, patch
from botocore.exceptions import ClientError

from lock_and_key.providers.aws.resources.iam import IAMService


class TestIAMService(unittest.TestCase):
    """Test cases for IAMService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.service = IAMService(self.mock_session)

    def test_scan_policies_success(self):
        """Test successful policy scanning."""
        mock_iam = Mock()
        mock_paginator = Mock()
        mock_iam.get_paginator.return_value = mock_paginator
        mock_paginator.paginate.return_value = [
            {"Policies": [{"PolicyName": "TestPolicy", "Arn": "arn:aws:iam::123:policy/TestPolicy", "DefaultVersionId": "v1"}]}
        ]
        mock_iam.get_policy_version.return_value = {
            "PolicyVersion": {"Document": {"Statement": [{"Action": "*", "Resource": "*"}]}}
        }
        self.mock_session.client.return_value = mock_iam
        
        issues = self.service.scan_policies("123456789012")
        
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("Administrative permissions" in issue for issue in issues))

    def test_scan_policies_client_error(self):
        """Test policy scanning with client error."""
        mock_iam = Mock()
        mock_iam.get_paginator.side_effect = ClientError({"Error": {"Code": "AccessDenied"}}, "ListPolicies")
        self.mock_session.client.return_value = mock_iam
        
        issues = self.service.scan_policies("123456789012")
        
        self.assertEqual(len(issues), 1)
        self.assertIn("Failed to list customer managed policies", issues[0])

    def test_has_admin_permissions(self):
        """Test detection of administrative permissions."""
        # Test wildcard action
        statement = {"Action": "*"}
        self.assertTrue(self.service._has_admin_permissions(statement))
        
        # Test admin action in list
        statement = {"Action": ["s3:GetObject", "*:*"]}
        self.assertTrue(self.service._has_admin_permissions(statement))
        
        # Test normal action
        statement = {"Action": "s3:GetObject"}
        self.assertFalse(self.service._has_admin_permissions(statement))

    def test_has_wildcard_resources(self):
        """Test detection of wildcard resources."""
        # Test wildcard resource
        statement = {"Resource": "*"}
        self.assertTrue(self.service._has_wildcard_resources(statement))
        
        # Test wildcard in list
        statement = {"Resource": ["arn:aws:s3:::bucket/*", "*"]}
        self.assertTrue(self.service._has_wildcard_resources(statement))
        
        # Test specific resource
        statement = {"Resource": "arn:aws:s3:::bucket/key"}
        self.assertFalse(self.service._has_wildcard_resources(statement))

    def test_has_privilege_escalation_risk(self):
        """Test detection of privilege escalation risks."""
        # Test risky action
        statement = {"Action": "iam:CreateRole"}
        self.assertTrue(self.service._has_privilege_escalation_risk(statement))
        
        # Test risky action in list
        statement = {"Action": ["s3:GetObject", "iam:AttachRolePolicy"]}
        self.assertTrue(self.service._has_privilege_escalation_risk(statement))
        
        # Test safe action
        statement = {"Action": "s3:GetObject"}
        self.assertFalse(self.service._has_privilege_escalation_risk(statement))


if __name__ == '__main__':
    unittest.main()