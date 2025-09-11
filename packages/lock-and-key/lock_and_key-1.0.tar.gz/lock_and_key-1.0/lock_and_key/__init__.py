# SPDX-FileCopyrightText: 2025-present WinterShadow <wolf@cyberwolf.dev>
#
# SPDX-License-Identifier: MIT
"""Lock & Key - Cloud Security Scanner."""

from lock_and_key.__about__ import __version__
from lock_and_key.core import LockAndKeyScanner
from lock_and_key.providers import PROVIDER_CLASSES
from lock_and_key.types import ScanResult, ScanSummary

__all__ = [
    "LockAndKeyScanner",
    "ScanResult",
    "ScanSummary",
    "PROVIDER_CLASSES",
    "__version__",
]
