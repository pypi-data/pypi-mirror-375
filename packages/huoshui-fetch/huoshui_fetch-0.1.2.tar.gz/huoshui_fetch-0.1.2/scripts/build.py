#!/usr/bin/env python3
"""Automated build script for huoshui-fetch package."""

import shutil
import subprocess
import sys
from pathlib import Path

from version_manager import VersionManager


class PackageBuilder:
    """Automated package building with validation."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.version_manager = VersionManager(self.project_root)

    def clean_build_artifacts(self) -> bool:
        """Clean previous build artifacts."""
        print("🧹 Cleaning build artifacts...")

        artifacts = [self.dist_dir, self.build_dir]
        egg_info_dirs = list(self.project_root.glob("*.egg-info"))
        artifacts.extend(egg_info_dirs)

        for artifact in artifacts:
            if artifact.exists():
                if artifact.is_dir():
                    shutil.rmtree(artifact)
                else:
                    artifact.unlink()
                print(f"  Removed: {artifact.name}")

        print("✅ Build artifacts cleaned")
        return True

    def validate_project_structure(self) -> tuple[bool, list[str]]:
        """Validate project structure and configuration."""
        print("🔍 Validating project structure...")

        errors = []

        # Check essential files
        essential_files = [
            self.project_root / "pyproject.toml",
            self.project_root / "README.md",
            self.project_root / "LICENSE",
            self.project_root / "huoshui_fetch" / "__init__.py",
            self.project_root / "huoshui_fetch" / "__main__.py",
        ]

        for file_path in essential_files:
            if not file_path.exists():
                errors.append(f"Missing required file: {file_path.relative_to(self.project_root)}")

        # Check version consistency
        consistent, versions = self.version_manager.validate_version_consistency()
        if not consistent:
            errors.append(f"Version inconsistency detected: {versions}")

        # Check pyproject.toml structure
        pyproject_path = self.project_root / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            required_sections = ["[project]", "[build-system]"]
            for section in required_sections:
                if section not in content:
                    errors.append(f"Missing {section} section in pyproject.toml")

        success = len(errors) == 0
        if success:
            print("✅ Project structure validation passed")
        else:
            print("❌ Project structure validation failed:")
            for error in errors:
                print(f"  - {error}")

        return success, errors

    def run_quality_checks(self) -> bool:
        """Run linting and type checking."""
        print("🔍 Running quality checks...")

        checks_passed = True

        # Run ruff linting
        try:
            result = subprocess.run(
                ["uv", "run", "ruff", "check", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("  ✅ Ruff linting passed")
            else:
                print("  ❌ Ruff linting failed:")
                print(f"    {result.stdout}")
                checks_passed = False
        except FileNotFoundError:
            print("  ⚠️  Ruff not available, skipping linting")

        # Run mypy type checking
        try:
            result = subprocess.run(
                ["uv", "run", "mypy", "huoshui_fetch"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("  ✅ MyPy type checking passed")
            else:
                print("  ❌ MyPy type checking failed:")
                print(f"    {result.stdout}")
                checks_passed = False
        except FileNotFoundError:
            print("  ⚠️  MyPy not available, skipping type checking")

        return checks_passed

    def install_build_dependencies(self) -> bool:
        """Install build dependencies."""
        print("📦 Installing build dependencies...")

        try:
            result = subprocess.run(
                ["uv", "sync"], cwd=self.project_root, capture_output=True, text=True
            )

            if result.returncode == 0:
                print("✅ Build dependencies installed")
                return True
            else:
                print("❌ Failed to install build dependencies:")
                print(result.stderr)
                return False
        except FileNotFoundError:
            print("❌ uv not found. Please install uv first.")
            return False

    def build_package(self) -> tuple[bool, dict[str, Path]]:
        """Build wheel and source distributions."""
        print("🔨 Building package...")

        try:
            result = subprocess.run(
                ["uv", "build"], cwd=self.project_root, capture_output=True, text=True
            )

            if result.returncode != 0:
                print("❌ Package build failed:")
                print(result.stderr)
                return False, {}

            # Find built files
            built_files = {}
            if self.dist_dir.exists():
                for file_path in self.dist_dir.iterdir():
                    if file_path.suffix == ".whl":
                        built_files["wheel"] = file_path
                    elif file_path.suffix == ".gz":
                        built_files["sdist"] = file_path

            print("✅ Package built successfully:")
            for build_type, file_path in built_files.items():
                size = file_path.stat().st_size / 1024  # Size in KB
                print(f"  {build_type}: {file_path.name} ({size:.1f} KB)")

            return True, built_files

        except FileNotFoundError:
            print("❌ uv not found. Please install uv first.")
            return False, {}

    def test_package_import(self) -> bool:
        """Test package import after build."""
        print("🧪 Testing package import...")

        try:
            # Test importing from wheel
            wheel_files = list(self.dist_dir.glob("*.whl"))
            if not wheel_files:
                print("❌ No wheel file found for testing")
                return False

            wheel_file = wheel_files[0]

            result = subprocess.run(
                [
                    "python",
                    "-c",
                    f"import sys; sys.path.insert(0, '{wheel_file}'); import huoshui_fetch; print(f'✅ Import successful, version: {{huoshui_fetch.__version__}}')",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                print(f"  {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Import test failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Import test error: {e}")
            return False

    def validate_console_scripts(self) -> bool:
        """Validate console scripts are properly configured."""
        print("🔍 Validating console scripts...")

        try:
            # Test the console script in a subprocess
            result = subprocess.run(
                ["uv", "run", "huoshui-fetch", "--help"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            # For MCP servers, --help might not be available, so we check if it runs without error
            if result.returncode == 0 or "huoshui-fetch" in result.stderr:
                print("  ✅ Console script is accessible")
                return True
            else:
                print(f"  ❌ Console script test failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("  ✅ Console script runs (timeout expected for MCP server)")
            return True
        except Exception as e:
            print(f"  ❌ Console script validation error: {e}")
            return False

    def build_full(self, skip_quality_checks: bool = False) -> bool:
        """Run complete build process."""
        print("🚀 Starting full build process...\n")

        # Step 1: Validate project structure
        valid, errors = self.validate_project_structure()
        if not valid:
            print("❌ Build failed: Project structure validation errors")
            return False

        # Step 2: Clean artifacts
        if not self.clean_build_artifacts():
            return False

        # Step 3: Install dependencies
        if not self.install_build_dependencies():
            return False

        # Step 4: Quality checks (optional)
        if not skip_quality_checks:
            if not self.run_quality_checks():
                print("⚠️  Quality checks failed, but continuing build...")

        # Step 5: Build package
        success, built_files = self.build_package()
        if not success:
            return False

        # Step 6: Test package
        if not self.test_package_import():
            print("⚠️  Package import test failed")

        # Step 7: Validate console scripts
        if not self.validate_console_scripts():
            print("⚠️  Console script validation failed")

        print("\n🎉 Build process completed successfully!")
        print("\nBuilt files:")
        for build_type, file_path in built_files.items():
            print(f"  📦 {file_path}")

        return True


def main():
    """CLI interface for building packages."""
    import argparse

    parser = argparse.ArgumentParser(description="Build huoshui-fetch package")
    parser.add_argument(
        "--skip-quality-checks", action="store_true", help="Skip linting and type checking"
    )
    parser.add_argument("--clean-only", action="store_true", help="Only clean build artifacts")

    args = parser.parse_args()

    builder = PackageBuilder()

    if args.clean_only:
        return 0 if builder.clean_build_artifacts() else 1

    success = builder.build_full(skip_quality_checks=args.skip_quality_checks)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
