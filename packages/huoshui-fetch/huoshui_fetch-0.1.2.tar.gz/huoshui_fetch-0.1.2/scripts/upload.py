#!/usr/bin/env python3
"""Interactive PyPI publishing script for huoshui-fetch package."""

import subprocess
import sys
from pathlib import Path

from build import PackageBuilder
from version_manager import VersionManager


class PyPIUploader:
    """Handles PyPI package upload with validation."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.dist_dir = self.project_root / "dist"
        self.builder = PackageBuilder(self.project_root)
        self.version_manager = VersionManager(self.project_root)

    def check_pypi_credentials(self, repository: str = "pypi") -> bool:
        """Check if PyPI credentials are available."""
        print(f"🔐 Checking {repository} credentials...")

        try:
            subprocess.run(
                ["twine", "check", "--repository", repository, "--help"],
                capture_output=True,
                text=True,
            )
            print(f"  ✅ Twine is available for {repository}")
            return True
        except FileNotFoundError:
            print("❌ Twine not found. Please install: pip install twine")
            return False

    def validate_built_packages(self) -> tuple[bool, list[Path]]:
        """Validate built packages exist and are valid."""
        print("📦 Validating built packages...")

        if not self.dist_dir.exists():
            print("❌ No dist directory found. Run build first.")
            return False, []

        package_files = list(self.dist_dir.glob("*.whl")) + list(self.dist_dir.glob("*.tar.gz"))

        if not package_files:
            print("❌ No package files found in dist/. Run build first.")
            return False, []

        print(f"  Found {len(package_files)} package file(s):")
        for package_file in package_files:
            size = package_file.stat().st_size / 1024
            print(f"    📦 {package_file.name} ({size:.1f} KB)")

        # Use twine to check packages
        try:
            result = subprocess.run(
                ["twine", "check"] + [str(f) for f in package_files],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                print("  ✅ All packages passed validation")
                return True, package_files
            else:
                print("❌ Package validation failed:")
                print(f"    {result.stdout}")
                print(f"    {result.stderr}")
                return False, package_files

        except FileNotFoundError:
            print("⚠️  Twine not available, skipping package validation")
            return True, package_files

    def check_package_exists(
        self, package_name: str, version: str, repository: str = "pypi"
    ) -> bool:
        """Check if package version already exists on PyPI."""
        print(f"🔍 Checking if {package_name} {version} exists on {repository}...")

        try:
            if repository == "testpypi":
                index_url = "https://test.pypi.org/simple/"
            else:
                index_url = "https://pypi.org/simple/"

            result = subprocess.run(
                ["pip", "index", "versions", package_name, "--index-url", index_url],
                capture_output=True,
                text=True,
            )

            if version in result.stdout:
                print(f"  ⚠️  Version {version} already exists on {repository}")
                return True
            else:
                print(f"  ✅ Version {version} is available on {repository}")
                return False

        except Exception as e:
            print(f"  ⚠️  Could not check version existence: {e}")
            return False

    def upload_to_repository(self, package_files: list[Path], repository: str = "testpypi") -> bool:
        """Upload packages to specified repository."""
        print(f"🚀 Uploading to {repository}...")

        repository_url = {
            "testpypi": "https://test.pypi.org/legacy/",
            "pypi": "https://upload.pypi.org/legacy/",
        }

        try:
            cmd = [
                "twine",
                "upload",
                "--repository-url",
                repository_url[repository],
            ] + [str(f) for f in package_files]

            result = subprocess.run(cmd, cwd=self.project_root)

            if result.returncode == 0:
                print(f"✅ Successfully uploaded to {repository}")
                return True
            else:
                print(f"❌ Upload to {repository} failed")
                return False

        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False

    def test_installation(
        self, package_name: str, version: str, repository: str = "testpypi"
    ) -> bool:
        """Test installing the package from the repository."""
        print(f"🧪 Testing installation from {repository}...")

        if repository == "testpypi":
            index_url = "https://test.pypi.org/simple/"
            extra_index = "--extra-index-url https://pypi.org/simple/"
        else:
            index_url = "https://pypi.org/simple/"
            extra_index = ""

        # Create a temporary virtual environment for testing
        test_env = self.project_root / ".test-env"

        try:
            # Create test environment
            subprocess.run(["python", "-m", "venv", str(test_env)], check=True)

            # Install package
            pip_cmd = [str(test_env / "bin" / "pip"), "install"]
            if extra_index:
                pip_cmd.extend(extra_index.split())
            pip_cmd.extend(["--index-url", index_url, f"{package_name}=={version}"])

            result = subprocess.run(pip_cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"❌ Installation failed: {result.stderr}")
                return False

            # Test import
            python_cmd = [
                str(test_env / "bin" / "python"),
                "-c",
                f"import {package_name.replace('-', '_')}; print(f'✅ Successfully imported {package_name}')",
            ]

            result = subprocess.run(python_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"  {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Import test failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Installation test error: {e}")
            return False
        finally:
            # Cleanup test environment
            import shutil

            if test_env.exists():
                shutil.rmtree(test_env)

    def interactive_upload(self, test_first: bool = True) -> bool:
        """Interactive upload process with user confirmations."""
        print("🎯 Starting interactive PyPI upload process...\n")

        # Get current version
        versions = self.version_manager.get_current_versions()
        if not versions:
            print("❌ No version information found")
            return False

        current_version = list(versions.values())[0]
        package_name = "huoshui-fetch"

        print(f"📋 Package: {package_name}")
        print(f"📋 Version: {current_version}")

        # Validate packages
        valid, package_files = self.validate_built_packages()
        if not valid:
            rebuild = input("\n🔄 Rebuild packages? [y/N]: ").lower().startswith("y")
            if rebuild:
                if not self.builder.build_full():
                    return False
                valid, package_files = self.validate_built_packages()
                if not valid:
                    return False
            else:
                return False

        # Check if version already exists
        if test_first:
            exists_on_testpypi = self.check_package_exists(
                package_name, current_version, "testpypi"
            )
            if exists_on_testpypi:
                print("⚠️  Version already exists on TestPyPI")
                continue_anyway = input("Continue anyway? [y/N]: ").lower().startswith("y")
                if not continue_anyway:
                    return False

        exists_on_pypi = self.check_package_exists(package_name, current_version, "pypi")
        if exists_on_pypi:
            print("❌ Version already exists on PyPI!")
            bump_version = input("Bump version and retry? [y/N]: ").lower().startswith("y")
            if bump_version:
                new_version = self.version_manager.bump_version("patch")
                print(f"🔄 Version bumped to: {new_version}")
                # Rebuild with new version
                if not self.builder.build_full():
                    return False
                valid, package_files = self.validate_built_packages()
                if not valid:
                    return False
            else:
                return False

        # TestPyPI upload
        if test_first:
            print("\n" + "=" * 50)
            print("📤 STAGE 1: TestPyPI Upload")
            print("=" * 50)

            upload_to_testpypi = input(
                f"\n🚀 Upload {package_name} {current_version} to TestPyPI? [Y/n]: "
            )
            if not upload_to_testpypi.lower().startswith("n"):
                if not self.upload_to_repository(package_files, "testpypi"):
                    return False

                # Test installation from TestPyPI
                test_install = input("\n🧪 Test installation from TestPyPI? [Y/n]: ")
                if not test_install.lower().startswith("n"):
                    if not self.test_installation(package_name, current_version, "testpypi"):
                        print("⚠️  TestPyPI installation test failed")
                        continue_to_pypi = input("Continue to PyPI anyway? [y/N]: ")
                        if not continue_to_pypi.lower().startswith("y"):
                            return False

        # PyPI upload
        print("\n" + "=" * 50)
        print("📤 STAGE 2: PyPI Upload")
        print("=" * 50)

        upload_to_pypi = input(f"\n🎯 Upload {package_name} {current_version} to PyPI? [y/N]: ")
        if not upload_to_pypi.lower().startswith("y"):
            print("📤 Upload to PyPI cancelled by user")
            return True  # TestPyPI upload was successful

        if not self.upload_to_repository(package_files, "pypi"):
            return False

        # Final validation
        print("\n" + "=" * 50)
        print("🎉 UPLOAD COMPLETE!")
        print("=" * 50)

        final_test = input("\n🧪 Test installation from PyPI? [Y/n]: ")
        if not final_test.lower().startswith("n"):
            if self.test_installation(package_name, current_version, "pypi"):
                print(f"\n🎊 SUCCESS: {package_name} {current_version} is now live on PyPI!")
                print(f"📦 Install with: pip install {package_name}")
                print(f"🔗 View at: https://pypi.org/project/{package_name}/")
            else:
                print("⚠️  PyPI installation test failed, but package was uploaded")

        return True


def main():
    """CLI interface for uploading packages."""
    import argparse

    parser = argparse.ArgumentParser(description="Upload huoshui-fetch to PyPI")
    parser.add_argument("--no-test", action="store_true", help="Skip TestPyPI upload")
    parser.add_argument("--testpypi-only", action="store_true", help="Only upload to TestPyPI")

    args = parser.parse_args()

    uploader = PyPIUploader()

    # Check prerequisites
    if not uploader.check_pypi_credentials():
        return 1

    success = uploader.interactive_upload(test_first=not args.no_test)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
