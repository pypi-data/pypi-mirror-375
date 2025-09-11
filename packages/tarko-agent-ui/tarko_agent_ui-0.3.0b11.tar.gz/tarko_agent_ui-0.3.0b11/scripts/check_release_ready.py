#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Release readiness checker for tarko-agent-ui package.

Verifies all requirements are met before PyPI publication:
- Package builds successfully
- All tests pass
- Code quality checks pass
- Static assets are present
- Version consistency
- Git repository is clean
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class ReleaseChecker:
    """Comprehensive release readiness checker."""

    def __init__(self):
        self.issues: List[str] = []
        self.warnings: List[str] = []

    def run_command(self, cmd: str, description: str) -> Tuple[bool, str]:
        """Run command and return success status with output."""
        try:
            result = subprocess.run(
                cmd, shell=True, check=True, capture_output=True, text=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr

    def check_git_status(self) -> bool:
        """Check if git repository is clean."""
        print("🔍 Checking git repository status...")

        # Check if we're in a git repo
        success, _ = self.run_command("git rev-parse --git-dir", "git repo check")
        if not success:
            self.issues.append("Not in a git repository")
            return False

        # Check for uncommitted changes
        success, output = self.run_command("git status --porcelain", "git status")
        if success and output.strip():
            self.issues.append(f"Uncommitted changes found:\n{output}")
            return False

        # Check if we're on main branch
        success, output = self.run_command(
            "git branch --show-current", "current branch"
        )
        if success and output.strip() != "main":
            self.warnings.append(f"Not on main branch (current: {output.strip()})")

        print("  ✅ Git repository is clean")
        return True

    def check_static_assets(self) -> bool:
        """Check if static assets are built and present."""
        print("🔍 Checking static assets...")

        static_dir = Path("tarko_agent_ui/static")
        if not static_dir.exists():
            self.issues.append(
                "Static assets directory not found. Run: python scripts/build_assets.py"
            )
            return False

        index_file = static_dir / "index.html"
        if not index_file.exists():
            self.issues.append("index.html not found in static assets")
            return False

        # Check version file
        version_file = Path("tarko_agent_ui/_static_version.py")
        if not version_file.exists():
            self.issues.append("Static version file not found")
            return False

        print("  ✅ Static assets are present")
        return True

    def check_tests(self) -> bool:
        """Run test suite and check results."""
        print("🔍 Running tests...")

        success, output = self.run_command("uv run pytest --tb=short", "test suite")
        if not success:
            self.issues.append(f"Tests failed:\n{output}")
            return False

        print("  ✅ All tests pass")
        return True

    def check_code_quality(self) -> bool:
        """Check code formatting and type checking."""
        print("🔍 Checking code quality...")

        # Check black formatting
        success, output = self.run_command("uv run black --check .", "black formatting")
        if not success:
            self.issues.append(f"Code formatting issues found. Run: uv run black .")
            return False

        # Check mypy type checking
        success, output = self.run_command("uv run mypy .", "mypy type checking")
        if not success:
            self.warnings.append(f"Type checking issues found:\n{output}")

        print("  ✅ Code quality checks pass")
        return True

    def check_package_build(self) -> bool:
        """Test package building."""
        print("🔍 Testing package build...")

        # Clean previous builds
        success, _ = self.run_command("rm -rf dist/", "clean dist")

        # Build package
        success, output = self.run_command("uv build", "package build")
        if not success:
            self.issues.append(f"Package build failed:\n{output}")
            return False

        # Check if files were created
        dist_dir = Path("dist")
        if not dist_dir.exists() or not list(dist_dir.glob("*.whl")):
            self.issues.append("No wheel file generated")
            return False

        print("  ✅ Package builds successfully")
        return True

    def check_version_consistency(self) -> bool:
        """Check version consistency across files."""
        print("🔍 Checking version consistency...")

        # Read version from pyproject.toml
        pyproject_path = Path("pyproject.toml")
        if not pyproject_path.exists():
            self.issues.append("pyproject.toml not found")
            return False

        import re

        content = pyproject_path.read_text()
        version_match = re.search(r'version = "([^"]+)"', content)
        if not version_match:
            self.issues.append("Version not found in pyproject.toml")
            return False

        pyproject_version = version_match.group(1)

        # Check __init__.py version
        init_path = Path("tarko_agent_ui/__init__.py")
        if init_path.exists():
            init_content = init_path.read_text()
            init_match = re.search(r'__version__ = "([^"]+)"', init_content)
            if init_match and init_match.group(1) != pyproject_version:
                self.issues.append(
                    f"Version mismatch: pyproject.toml={pyproject_version}, __init__.py={init_match.group(1)}"
                )
                return False

        print(f"  ✅ Version consistency checked: {pyproject_version}")
        return True

    def check_dependencies(self) -> bool:
        """Check if dependencies are properly configured."""
        print("🔍 Checking dependencies...")

        # Verify zero-dependency status
        pyproject_path = Path("pyproject.toml")
        content = pyproject_path.read_text()

        if "dependencies = []" not in content:
            self.warnings.append("Package should be zero-dependency")

        print("  ✅ Dependencies checked")
        return True

    def check_pypi_credentials(self) -> bool:
        """Check if PyPI credentials are configured."""
        print("🔍 Checking PyPI credentials...")

        # Check for uv publish configuration
        success, _ = self.run_command("uv --version", "uv availability")
        if not success:
            self.issues.append("uv not available for publishing")
            return False

        # Note: We can't easily check credentials without attempting to publish
        self.warnings.append("Ensure PyPI credentials are configured for 'uv publish'")

        print("  ⚠️  PyPI credentials check skipped (manual verification needed)")
        return True

    def run_all_checks(self) -> bool:
        """Run all release readiness checks."""
        print("🚀 Starting release readiness check...\n")

        checks = [
            self.check_git_status,
            self.check_static_assets,
            self.check_version_consistency,
            self.check_dependencies,
            self.check_code_quality,
            self.check_tests,
            self.check_package_build,
            self.check_pypi_credentials,
        ]

        all_passed = True
        for check in checks:
            if not check():
                all_passed = False
            print()  # Empty line for readability

        return all_passed

    def print_summary(self) -> None:
        """Print final summary of checks."""
        print("=" * 60)
        print("📋 RELEASE READINESS SUMMARY")
        print("=" * 60)

        if not self.issues and not self.warnings:
            print("🎉 ALL CHECKS PASSED! Ready for release.")
            print("\n📦 To publish:")
            print("   uv publish")
        else:
            if self.issues:
                print("❌ CRITICAL ISSUES (must fix before release):")
                for i, issue in enumerate(self.issues, 1):
                    print(f"   {i}. {issue}")
                print()

            if self.warnings:
                print("⚠️  WARNINGS (recommended to address):")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"   {i}. {warning}")
                print()

            if self.issues:
                print("🚫 NOT READY FOR RELEASE")
            else:
                print("⚠️  READY WITH WARNINGS")


def main() -> None:
    """Main entry point."""
    checker = ReleaseChecker()

    try:
        all_passed = checker.run_all_checks()
        checker.print_summary()

        # Exit with appropriate code
        sys.exit(0 if all_passed and not checker.issues else 1)

    except KeyboardInterrupt:
        print("\n❌ Check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
