#!/usr/bin/env python3
"""
Script to upload the kft package to PyPI

Usage:
    python scripts/upload_to_pypi.py [--test]

Options:
    --test    Upload to TestPyPI instead of PyPI
    
Prerequisites:
    - Install twine: pip install twine
    - Configure PyPI credentials (API token recommended)
    - Build the package: uv build
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def main():
    # Check if we should use test PyPI
    use_test_pypi = "--test" in sys.argv
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("kFT Package Upload Script")
    print("=" * 40)
    
    # Check if dist directory exists
    if not Path("dist").exists():
        print("❌ dist/ directory not found. Please run 'uv build' first.")
        return 1
    
    # List files in dist directory
    dist_files = list(Path("dist").glob("kft-*"))
    if not dist_files:
        print("❌ No kft distribution files found in dist/")
        return 1
    
    print(f"Found distribution files:")
    for file in dist_files:
        print(f"  - {file}")
    
    # Upload to PyPI or TestPyPI
    if use_test_pypi:
        print("\n📦 Uploading to TestPyPI...")
        cmd = ["twine", "upload", "--repository", "testpypi", "dist/*"]
        repository = "TestPyPI"
    else:
        print("\n📦 Uploading to PyPI...")
        cmd = ["twine", "upload", "dist/*"]
        repository = "PyPI"
    
    success = run_command(cmd, f"Upload to {repository}")
    
    if success:
        print(f"\n🎉 Successfully uploaded kft package to {repository}!")
        if use_test_pypi:
            print("\nTo install from TestPyPI:")
            print("pip install --index-url https://test.pypi.org/simple/ kft")
        else:
            print("\nTo install from PyPI:")
            print("pip install kft")
    else:
        print(f"\n❌ Failed to upload to {repository}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())