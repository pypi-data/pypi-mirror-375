#!/usr/bin/env python3
"""Format script that runs black and isort on all Python files."""

import subprocess
import sys
from pathlib import Path


def main():
    """Run black and isort formatters."""
    # Get the workspace root
    workspace_root = Path(__file__).parent.parent.parent

    # Find all Python files
    py_files = list(workspace_root.glob("lock_and_key/**/*.py"))

    if not py_files:
        print("No Python files found to format")
        return 0

    # Run black
    print("Running black...")
    black_cmd = [sys.executable, "-m", "black",
                 "--line-length", "120"] + [str(f) for f in py_files]
    result = subprocess.run(black_cmd, cwd=workspace_root)
    if result.returncode != 0:
        print("Black formatting failed")
        return result.returncode

    # Run isort
    print("Running isort...")
    isort_cmd = [sys.executable, "-m", "isort", "--profile",
                 "black", "--line-length", "120"] + [str(f) for f in py_files]
    result = subprocess.run(isort_cmd, cwd=workspace_root)
    if result.returncode != 0:
        print("Isort formatting failed")
        return result.returncode

    print("Formatting completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
