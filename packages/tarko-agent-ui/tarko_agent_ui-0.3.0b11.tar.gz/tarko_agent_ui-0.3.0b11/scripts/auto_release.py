#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Automated release script for tarko-agent-ui package.

Checks for new @tarko/agent-ui-builder versions and automatically:
1. Downloads latest assets
2. Bumps package version
3. Builds and publishes to PyPI
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union

import requests


def get_npm_latest_version(package: str) -> Optional[str]:
    """Get latest version of npm package."""
    try:
        response = requests.get(f"https://registry.npmjs.org/{package}/latest")
        response.raise_for_status()
        data = response.json()
        return str(data["version"])
    except Exception as e:
        print(f"❌ Failed to get npm version: {e}")
        return None


def get_current_python_version() -> Optional[str]:
    """Get current Python package version from pyproject.toml."""
    try:
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text()
        match = re.search(r'version = "([^"]+)"', content)
        return match.group(1) if match else None
    except Exception as e:
        print(f"❌ Failed to get current version: {e}")
        return None


def normalize_npm_version_to_python(npm_version: str) -> str:
    """Convert npm version format to Python version format.

    Examples:
        0.3.0-beta.11 -> 0.3.0b11
        0.3.0-alpha.5 -> 0.3.0a5
        1.0.0 -> 1.0.0
    """
    # Handle beta versions: 0.3.0-beta.11 -> 0.3.0b11
    if "-beta." in npm_version:
        base, beta_num = npm_version.split("-beta.")
        return f"{base}b{beta_num}"

    # Handle alpha versions: 0.3.0-alpha.5 -> 0.3.0a5
    if "-alpha." in npm_version:
        base, alpha_num = npm_version.split("-alpha.")
        return f"{base}a{alpha_num}"

    # Handle rc versions: 0.3.0-rc.1 -> 0.3.0rc1
    if "-rc." in npm_version:
        base, rc_num = npm_version.split("-rc.")
        return f"{base}rc{rc_num}"

    # Regular version: 1.0.0 -> 1.0.0
    return npm_version


def should_update_version(current_python_version: str, npm_version: str) -> bool:
    """Check if Python package should be updated based on npm version."""
    target_python_version = normalize_npm_version_to_python(npm_version)
    return current_python_version != target_python_version


def update_version_in_pyproject(new_version: str) -> bool:
    """Update version in pyproject.toml."""
    try:
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text()

        # Replace version
        new_content = re.sub(
            r'version = "[^"]+"', f'version = "{new_version}"', content
        )

        pyproject_path.write_text(new_content)
        return True
    except Exception as e:
        print(f"❌ Failed to update version: {e}")
        return False


def run_command(cmd: str) -> bool:
    """Run shell command and return success status."""
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"   Error: {e.stderr}")
        return False


def verify_npm_version_exists(npm_version: str) -> bool:
    """Verify that the specified npm version exists."""
    try:
        response = requests.get(
            "https://registry.npmjs.org/%40tarko%2Fagent-ui-builder"
        )
        response.raise_for_status()
        package_info = response.json()
        return npm_version in package_info["versions"]
    except Exception as e:
        print(f"❌ Failed to verify npm version: {e}")
        return False


def update_all_version_files(new_version: str) -> bool:
    """Update version in all relevant files."""
    try:
        # Update pyproject.toml
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text()
        new_content = re.sub(
            r'version = "[^"]+"', f'version = "{new_version}"', content
        )
        pyproject_path.write_text(new_content)

        # Update __init__.py
        init_path = Path("tarko_agent_ui/__init__.py")
        content = init_path.read_text()
        new_content = re.sub(
            r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content
        )
        init_path.write_text(new_content)

        # Update test file
        test_path = Path("tests/test_core.py")
        if test_path.exists():
            content = test_path.read_text()
            new_content = re.sub(
                r'assert version_info\["sdk_version"\] == "[^"]+"',
                f'assert version_info["sdk_version"] == "{new_version}"',
                content,
            )
            test_path.write_text(new_content)

        return True
    except Exception as e:
        print(f"❌ Failed to update version files: {e}")
        return False


def main():
    """Main release automation workflow."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Automated release for tarko-agent-ui package"
    )
    parser.add_argument(
        "--version",
        type=str,
        help="Specific npm version to release (e.g., 0.3.0-beta.9). If not specified, uses latest.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it",
    )

    args = parser.parse_args()

    print("🚀 Starting automated release process...")

    # Get target npm version
    if args.version:
        npm_version = args.version
        print(f"📦 Using specified version: {npm_version}")

        # Verify specified version exists
        if not verify_npm_version_exists(npm_version):
            print(f"❌ Version {npm_version} does not exist on npm")
            sys.exit(1)
    else:
        npm_version = get_npm_latest_version("@tarko/agent-ui-builder")
        if not npm_version:
            sys.exit(1)
        print(f"📦 Using latest npm version: {npm_version}")

    current_version = get_current_python_version()
    if not current_version:
        sys.exit(1)

    print(f"🐍 Current Python version: {current_version}")

    # Generate target Python version
    target_python_version = normalize_npm_version_to_python(npm_version)
    print(f"🔄 Target Python version: {target_python_version}")

    # Check if update needed (skip for manual version)
    if not args.version and not should_update_version(current_version, npm_version):
        print("✅ Already up to date!")
        return

    if args.dry_run:
        print("\n🔍 DRY RUN - Commands that would be executed:")
        commands = [
            f"# Update version files to {target_python_version}",
            f"uv run python scripts/build_assets.py --version='{npm_version}'",
            "uv run pytest",
            "uv build",
            "uv publish",
            f"git add . && git commit -m 'feat: update to @tarko/agent-ui-builder@{npm_version}'",
            f"git tag v{target_python_version}",
            "git push origin main --tags",
        ]
        for cmd in commands:
            print(f"  {cmd}")
        return

    # Confirm release
    confirm = input(f"\nProceed with release {target_python_version}? [y/N]: ")
    if confirm.lower() != "y":
        print("❌ Release cancelled")
        return

    # Update version files
    if not update_all_version_files(target_python_version):
        sys.exit(1)
    print(f"📝 Updated version files to {target_python_version}")

    # Release workflow
    steps = [
        f"uv run python scripts/build_assets.py --version='{npm_version}'",  # Build assets with specific version
        "uv run pytest",  # Run tests
        "uv build",  # Build package
        "uv publish",  # Publish to PyPI
        f"git add . && git commit -m 'feat: update to @tarko/agent-ui-builder@{npm_version}'",
        f"git tag v{target_python_version}",  # Create git tag
        "git push origin main --tags",  # Push changes and tags
    ]

    # Execute release steps
    for step in steps:
        if not run_command(step):
            print(f"❌ Release failed at step: {step}")
            sys.exit(1)

    print(f"\n🎉 Successfully released {target_python_version}!")
    print(
        f"📦 Package: https://pypi.org/project/tarko-agent-ui/{target_python_version}/"
    )


if __name__ == "__main__":
    main()
