# Lock-And-Key

[![PyPI - Version](https://img.shields.io/pypi/v/lock-and-key.svg)](https://pypi.org/project/lock-and-key)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/lock-and-key.svg)](https://pypi.org/project/lock-and-key)

**Lock & Key** is a comprehensive cloud security scanner that analyzes IAM policies and resource-based policies across multiple cloud providers to identify security vulnerabilities, excessive permissions, and compliance issues.

## Features

- **Multi-Cloud Support**: AWS (fully implemented), Azure (in progress), GCP (in progress)
- **Comprehensive Policy Analysis**: Scans IAM policies and resource-based policies across all supported services
- **Security Vulnerability Detection**: Identifies privilege escalation risks, wildcard permissions, and administrative access
- **Interactive CLI**: User-friendly command-line interface with rich formatting and progress indicators
- **Detailed Reporting**: Generates JSON reports with actionable findings and recommendations
- **Least Privilege Analysis**: Highlights violations of the principle of least privilege

## Supported AWS Services

- **IAM**: Customer managed policies, roles, users
- **S3**: Bucket policies
- **DynamoDB**: Table resource policies
- **Lambda**: Function resource policies
- **SNS**: Topic policies
- **SQS**: Queue policies
- **Glue**: Data catalog and database policies

## Installation

```console
pip install lock-and-key
```

## Usage

### Interactive Mode

Run the interactive scanner to select providers and enter credentials:

```console
lock-and-key interactive
```

### Direct Scan Mode

Scan a specific provider with credentials:

```console
# AWS with profile
lock-and-key scan --provider AWS --profile my-profile

# AWS with access keys
lock-and-key scan --provider AWS --access-key YOUR_KEY --secret-key YOUR_SECRET --region us-east-1

# Azure (in progress)
lock-and-key scan --provider Azure --client-id YOUR_ID --secret YOUR_SECRET --tenant-id YOUR_TENANT

# GCP (in progress)
lock-and-key scan --provider GCP --creds-path /path/to/service-account.json
```

### Options

- `--output-dir`: Specify output directory for reports (default: `./reports`)
- `--provider`: Choose cloud provider (AWS, Azure, GCP)
- Various credential options for each provider

## Security Checks

Lock & Key identifies the following security issues:

- **Administrative Permissions**: Policies with `*:*` actions
- **Wildcard Resources**: Policies allowing access to all resources (`*`)
- **Privilege Escalation**: IAM permissions that could lead to privilege escalation
- **Overly Broad Access**: Resource policies with excessive permissions
- **Cross-Account Access**: Policies allowing external account access

## Report Format

Reports are generated in JSON format with the following structure:

```json
{
  "provider": "AWS",
  "account_id": "123456789012",
  "issues_found": 15,
  "least_privilege_violations": 8,
  "high_risk_permissions": 3,
  "summary": "Scanned IAM and all resource policies. Found 15 security issues.",
  "findings": [
    {
      "resource_name": "MyPolicy",
      "resource_id": "arn:aws:iam::123456789012:policy/MyPolicy",
      "issue_type": "Excessive Permissions",
      "severity": "High",
      "description": "Administrative permissions (*:*) detected",
      "recommendation": "Replace wildcard permissions with specific actions"
    }
  ]
}
```

## Development

### Requirements

- Python 3.8+
- boto3 (for AWS)
- click (CLI framework)
- rich (terminal formatting)
- pydantic (data validation)

### Project Structure

```
lock_and_key/
├── cli.py              # Command-line interface
├── core/
│   ├── scanner.py      # Main scanner logic
│   └── ui.py          # User interface utilities
├── providers/
│   ├── aws/           # AWS implementation
│   ├── azure.py       # Azure (in progress)
│   └── gcp.py         # GCP (in progress)
└── types/             # Data models and types
```

## Cloud Provider Status

- ✅ **AWS**: Fully implemented with comprehensive policy analysis
- 🚧 **Azure**: In progress
- 🚧 **GCP**: In progress

## License

`lock-and-key` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.

