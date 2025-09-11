"""Unified IAM policy analyzer for AWS resource and identity policies."""

import json
from typing import Any, Dict, List, Union

from lock_and_key.types import Finding


class IAMPolicyAnalyzer:
    """Unified analyzer for IAM policy structures (resource and identity policies)."""

    def __init__(self, account_id: str):
        """Initialize analyzer with account ID for external access detection."""
        self.account_id = account_id

    def analyze_policy(self, policy_data: Union[str, dict], resource_name: str, resource_id: str) -> List[Finding]:
        """Analyze a single policy and return findings."""
        findings = []

        try:
            if isinstance(policy_data, str):
                policy = json.loads(policy_data)
            else:
                policy = policy_data

            statements = policy.get("Statement", [])
            if not isinstance(statements, list):
                statements = [statements]

            for statement in statements:
                findings.extend(self._analyze_statement(statement, resource_name, resource_id))

        except (json.JSONDecodeError, TypeError):
            findings.append(
                Finding(
                    resource_name=resource_name,
                    resource_id=resource_id,
                    issue_type="Policy Parse Error",
                    severity="High",
                    description="Failed to parse policy JSON",
                    recommendation="Verify policy syntax and structure",
                )
            )

        return findings

    def _analyze_statement(self, statement: Dict[str, Any], resource_name: str, resource_id: str) -> List[Finding]:
        """Analyze individual policy statement."""
        findings = []

        # Check for external access
        if self._has_external_access(statement):
            findings.append(
                Finding(
                    resource_name=resource_name,
                    resource_id=resource_id,
                    issue_type="External Access",
                    severity="High",
                    description="Policy allows access from external accounts",
                    recommendation="Restrict access to trusted accounts only",
                )
            )

        # Check for public access
        if self._has_public_access(statement):
            findings.append(
                Finding(
                    resource_name=resource_name,
                    resource_id=resource_id,
                    issue_type="Public Access",
                    severity="Critical",
                    description="Policy allows public access (*)",
                    recommendation="Remove public access or add strict conditions",
                )
            )

        # Check for overly broad permissions
        if self._has_overly_broad_permissions(statement):
            findings.append(
                Finding(
                    resource_name=resource_name,
                    resource_id=resource_id,
                    issue_type="Overly Broad Access",
                    severity="Medium",
                    description="Policy uses wildcard actions or resources without conditions",
                    recommendation="Use specific actions and resources with appropriate conditions",
                )
            )

        # Check for privilege escalation risks
        if self._has_privilege_escalation_risk(statement):
            findings.append(
                Finding(
                    resource_name=resource_name,
                    resource_id=resource_id,
                    issue_type="Privilege Escalation Risk",
                    severity="High",
                    description="Policy allows dangerous administrative actions",
                    recommendation="Restrict administrative permissions to specific use cases",
                )
            )

        return findings

    def _has_external_access(self, statement: Dict[str, Any]) -> bool:
        """Check if statement allows external account access."""
        principals = statement.get("Principal", {})

        if isinstance(principals, dict):
            aws_principals = principals.get("AWS", [])
            if isinstance(aws_principals, str):
                aws_principals = [aws_principals]

            for principal in aws_principals:
                if isinstance(principal, str) and self.account_id not in principal and principal != "*":
                    return True

        return False

    def _has_public_access(self, statement: Dict[str, Any]) -> bool:
        """Check if statement allows public access."""
        principals = statement.get("Principal", {})

        if principals == "*":
            return True

        if isinstance(principals, dict):
            aws_principals = principals.get("AWS", [])
            if aws_principals == "*" or (isinstance(aws_principals, list) and "*" in aws_principals):
                return True

        return False

    def _has_overly_broad_permissions(self, statement: Dict[str, Any]) -> bool:
        """Check if statement has overly broad permissions."""
        actions = statement.get("Action", [])
        resources = statement.get("Resource", [])
        conditions = statement.get("Condition", {})

        if isinstance(actions, str):
            actions = [actions]
        if isinstance(resources, str):
            resources = [resources]

        # Check for wildcard actions without conditions
        has_wildcard_action = any("*" in action for action in actions)
        has_wildcard_resource = any("*" in resource for resource in resources)

        return (has_wildcard_action or has_wildcard_resource) and not conditions

    def _has_privilege_escalation_risk(self, statement: Dict[str, Any]) -> bool:
        """Check if statement has privilege escalation risks."""
        actions = statement.get("Action", [])

        if isinstance(actions, str):
            actions = [actions]

        dangerous_actions = [
            "iam:*",
            "iam:CreateRole",
            "iam:AttachRolePolicy",
            "iam:PutRolePolicy",
            "iam:CreateUser",
            "iam:AttachUserPolicy",
            "iam:PutUserPolicy",
            "sts:AssumeRole",
            "*",
        ]

        return any(action in dangerous_actions for action in actions)
