"""Base cloud provider interface."""

from abc import ABC, abstractmethod
from typing import Any

from .scan_results import ScanResult


class CloudProviderBase(ABC):
    """Base class for cloud provider implementations."""

    name: str
    description: str

    @abstractmethod
    def prompt_creds(self) -> Any:
        """Prompt user for credentials."""
        pass

    def run_analysis(self, creds: Any, output_dir: str = "./reports") -> ScanResult:
        """Run security analysis for the provider."""
        # Placeholder implementation
        return ScanResult(
            provider=self.name,
            account_id="123456789012",
            issues_found=3,
            least_privilege_violations=2,
            high_risk_permissions=1,
            summary=f"Sample summary for {self.name}",
            report_path=f"{output_dir}/{self.name.lower()}_report.json",
        )
