"""AWS IAM policy scanner."""

from typing import Any, Dict, List

from botocore.exceptions import ClientError
from mypy_boto3_iam import IAMClient
from mypy_boto3_iam.type_defs import PolicyTypeDef

from lock_and_key.providers.aws.resources.base import AWSServiceBase
from lock_and_key.providers.aws.resources.iam_policy_analyzer import IAMPolicyAnalyzer
from lock_and_key.types import Finding


class IAMService(AWSServiceBase):
    """AWS IAM service for policy analysis."""

    def scan_policies(self, account_id: str) -> List[str]:
        """Scan IAM policies for security issues."""
        issues: List[str] = []
        iam: "IAMClient" = self.session.client("iam")

        # Scan customer managed policies
        try:
            paginator = iam.get_paginator("list_policies")
            for page in paginator.paginate(Scope="Local"):
                for policy in page["Policies"]:
                    policy_issues = self._analyze_policy(iam, policy, account_id)
                    issues.extend(policy_issues)
        except ClientError:
            issues.append("Failed to list customer managed policies")

        return issues

    def scan_policies_detailed(self, account_id: str) -> List[Finding]:
        """Scan IAM policies and return detailed findings."""
        findings: List[Finding] = []
        iam: "IAMClient" = self.session.client("iam")
        analyzer = IAMPolicyAnalyzer(account_id)

        try:
            paginator = iam.get_paginator("list_policies")
            for page in paginator.paginate(Scope="Local"):
                for policy in page["Policies"]:
                    try:
                        policy_arn = policy.get("Arn")
                        version_id = policy.get("DefaultVersionId")
                        if not policy_arn or not version_id:
                            continue
                        response = iam.get_policy_version(PolicyArn=policy_arn, VersionId=version_id)
                        policy_doc = response["PolicyVersion"]["Document"]

                        from typing import cast

                        findings.extend(
                            analyzer.analyze_policy(
                                cast(str, policy_doc), policy.get("PolicyName", "MISSING"), policy.get("Arn", "MISSING")
                            )
                        )
                    except ClientError:
                        findings.append(
                            Finding(
                                resource_name=policy.get("PolicyName", "MISSING"),
                                resource_id=policy.get("Arn", "MISSING"),
                                issue_type="Access Error",
                                severity="Low",
                                description="Failed to retrieve policy document",
                                recommendation="Ensure IAM permissions allow policy document access",
                            )
                        )
        except ClientError:
            findings.append(
                Finding(
                    resource_name="IAM Policies",
                    resource_id="N/A",
                    issue_type="Access Error",
                    severity="Medium",
                    description="Failed to list customer managed policies",
                    recommendation="Ensure IAM permissions allow policy listing",
                )
            )

        return findings

    def _analyze_policy(self, iam: Any, policy: PolicyTypeDef, account_id: str) -> List[str]:
        """Analyze individual IAM policy."""
        issues: List[str] = []
        policy_name = policy.get("PolicyName")

        try:
            # Get policy document
            response = iam.get_policy_version(PolicyArn=policy.get("Arn"), VersionId=policy.get("DefaultVersionId"))

            policy_doc = response["PolicyVersion"]["Document"]

            for statement in policy_doc.get("Statement", []):
                # Check for overly permissive actions
                if self._has_admin_permissions(statement):
                    issues.append(f"Policy {policy_name}: Administrative permissions (*:*) detected")

                # Check for wildcard resources
                if self._has_wildcard_resources(statement):
                    issues.append(f"Policy {policy_name}: Wildcard resources (*) detected")

                # Check for privilege escalation risks
                if self._has_privilege_escalation_risk(statement):
                    issues.append(f"Policy {policy_name}: Privilege escalation risk detected")

        except ClientError:
            issues.append(f"Policy {policy_name}: Failed to retrieve policy document")

        return issues

    def _has_admin_permissions(self, statement: Dict[str, Any]) -> bool:
        """Check for administrative permissions."""
        actions = statement.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]

        return "*" in actions or any("*:*" in action for action in actions)

    def _has_wildcard_resources(self, statement: Dict[str, Any]) -> bool:
        """Check for wildcard resources."""
        resources = statement.get("Resource", [])
        if isinstance(resources, str):
            resources = [resources]

        return "*" in resources

    def _has_privilege_escalation_risk(self, statement: Dict[str, Any]) -> bool:
        """Check for privilege escalation risks."""
        actions = statement.get("Action", [])
        if isinstance(actions, str):
            actions = [actions]

        risky_actions = [
            "iam:CreateRole",
            "iam:AttachRolePolicy",
            "iam:PutRolePolicy",
            "iam:CreateUser",
            "iam:AttachUserPolicy",
            "iam:PutUserPolicy",
            "sts:AssumeRole",
        ]

        return any(action in risky_actions for action in actions)

    def _analyze_policy_detailed(self, iam: Any, policy: PolicyTypeDef, account_id: str) -> List[Finding]:
        """Analyze individual IAM policy and return detailed findings."""
        findings: List[Finding] = []
        policy_name = policy.get("PolicyName", "MISSING")

        try:
            response = iam.get_policy_version(PolicyArn=policy.get("Arn"), VersionId=policy.get("DefaultVersionId"))
            policy_doc = response["PolicyVersion"]["Document"]

            for statement in policy_doc.get("Statement", []):
                if self._has_admin_permissions(statement):
                    findings.append(
                        Finding(
                            resource_name=policy_name,
                            resource_id=policy.get("Arn", "MISSING"),
                            issue_type="Excessive Permissions",
                            severity="High",
                            description="Administrative permissions (*:*) detected",
                            recommendation="Replace wildcard permissions with specific actions",
                        )
                    )

                if self._has_wildcard_resources(statement):
                    findings.append(
                        Finding(
                            resource_name=policy_name,
                            resource_id=policy.get("Arn", "MISSING"),
                            issue_type="Overly Broad Access",
                            severity="Medium",
                            description="Wildcard resources (*) detected",
                            recommendation="Specify exact resource ARNs instead of wildcards",
                        )
                    )

                if self._has_privilege_escalation_risk(statement):
                    findings.append(
                        Finding(
                            resource_name=policy_name,
                            resource_id=policy.get("Arn", "MISSING"),
                            issue_type="Privilege Escalation",
                            severity="High",
                            description="Privilege escalation risk detected",
                            recommendation="Review and restrict IAM management permissions",
                        )
                    )

        except ClientError:
            findings.append(
                Finding(
                    resource_name=policy_name,
                    resource_id=policy.get("Arn", "MISSING"),
                    issue_type="Access Error",
                    severity="Low",
                    description="Failed to retrieve policy document",
                    recommendation="Ensure IAM permissions allow policy document access",
                )
            )

        return findings
