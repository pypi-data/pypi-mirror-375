#!/usr/bin/env python3
"""Master automation script for PyPI package build and publish workflow."""

import sys
from pathlib import Path
from typing import Optional

from build import PackageBuilder
from test import PackageTester
from upload import PyPIUploader
from version_manager import VersionManager


class PublishWorkflow:
    """Complete automation workflow for package publishing."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.version_manager = VersionManager(self.project_root)
        self.builder = PackageBuilder(self.project_root)
        self.tester = PackageTester(self.project_root)
        self.uploader = PyPIUploader(self.project_root)

    def run_pre_publishing_validation(self) -> bool:
        """Phase 1: Pre-Publishing Validation."""
        print("🔍 PHASE 1: PRE-PUBLISHING VALIDATION")
        print("=" * 60)

        # Version management
        print("\n1. Version Management")
        consistent, versions = self.version_manager.validate_version_consistency()
        if not consistent:
            print(f"❌ Version inconsistency: {versions}")
            return False
        print(f"✅ Version consistency: {list(versions.values())[0]}")

        # Project structure validation
        print("\n2. Project Structure")
        valid, errors = self.builder.validate_project_structure()
        if not valid:
            return False

        # Dependencies check
        print("\n3. Dependencies Check")
        if not self.tester.test_dependencies():
            return False

        return True

    def run_configuration_setup(self) -> bool:
        """Phase 2: Configuration & Setup."""
        print("\n🔧 PHASE 2: CONFIGURATION & SETUP")
        print("=" * 60)

        # Install build dependencies
        print("\n1. Installing Build Dependencies")
        if not self.builder.install_build_dependencies():
            return False

        # Quality checks
        print("\n2. Quality Checks")
        if not self.builder.run_quality_checks():
            print("⚠️  Quality checks failed, but continuing...")

        return True

    def run_build_automation(self) -> bool:
        """Phase 3: Build Automation."""
        print("\n🔨 PHASE 3: BUILD AUTOMATION")
        print("=" * 60)

        # Clean and build
        success, built_files = self.builder.build_package()
        if not success:
            return False

        # Local testing
        print("\n1. Local Testing")
        if not self.tester.test_package_import():
            print("⚠️  Package import test failed")

        if not self.tester.test_console_script():
            print("⚠️  Console script test failed")

        return True

    def run_publishing_validation(
        self, include_testpypi: bool = True, include_pypi: bool = False, test_install: bool = True
    ) -> bool:
        """Phase 4: Publishing & Validation."""
        print("\n📤 PHASE 4: PUBLISHING & VALIDATION")
        print("=" * 60)

        # Validate built packages
        valid, package_files = self.uploader.validate_built_packages()
        if not valid:
            return False

        # Interactive upload
        if include_testpypi or include_pypi:
            return self.uploader.interactive_upload(test_first=include_testpypi)

        print("✅ Package validation complete, ready for manual upload")
        return True

    def run_full_workflow(
        self,
        version_bump: Optional[str] = None,
        skip_quality_checks: bool = False,
        include_testpypi: bool = True,
        include_pypi: bool = False,
        test_install: bool = True,
    ) -> bool:
        """Run complete workflow."""
        print("🚀 HUOSHUI-FETCH PYPI PUBLISH WORKFLOW")
        print("=" * 70)

        try:
            # Version bump if requested
            if version_bump:
                print(f"\n📝 Bumping version ({version_bump})...")
                new_version = self.version_manager.bump_version(version_bump)
                print(f"✅ Version bumped to: {new_version}")

            # Phase 1: Pre-Publishing Validation
            if not self.run_pre_publishing_validation():
                print("❌ Pre-publishing validation failed")
                return False

            # Phase 2: Configuration & Setup
            if not self.run_configuration_setup():
                print("❌ Configuration & setup failed")
                return False

            # Phase 3: Build Automation
            if not self.run_build_automation():
                print("❌ Build automation failed")
                return False

            # Phase 4: Publishing & Validation
            if not self.run_publishing_validation(
                include_testpypi=include_testpypi,
                include_pypi=include_pypi,
                test_install=test_install,
            ):
                print("❌ Publishing & validation failed")
                return False

            print("\n" + "=" * 70)
            print("🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
            print("=" * 70)

            # Show final summary
            versions = self.version_manager.get_current_versions()
            current_version = list(versions.values())[0]
            print(f"📦 Package: huoshui-fetch")
            print(f"📋 Version: {current_version}")
            print(f"🔗 Ready for: {'TestPyPI & PyPI' if include_pypi else 'TestPyPI only'}")

            return True

        except KeyboardInterrupt:
            print("\n❌ Workflow cancelled by user")
            return False
        except Exception as e:
            print(f"\n❌ Workflow failed with error: {e}")
            return False


def main():
    """CLI interface for the publish workflow."""
    import argparse

    parser = argparse.ArgumentParser(description="Complete PyPI publish workflow")

    # Version management
    parser.add_argument(
        "--version-bump", choices=["major", "minor", "patch"], help="Bump version before publishing"
    )

    # Quality control
    parser.add_argument(
        "--skip-quality-checks", action="store_true", help="Skip linting and type checking"
    )

    # Publishing stages
    parser.add_argument("--skip-testpypi", action="store_true", help="Skip TestPyPI upload")
    parser.add_argument(
        "--include-pypi", action="store_true", help="Include PyPI upload (requires confirmation)"
    )
    parser.add_argument("--no-test-install", action="store_true", help="Skip installation testing")

    # Individual phases
    parser.add_argument(
        "--phase", choices=["validate", "setup", "build", "publish"], help="Run only specific phase"
    )

    # Testing
    parser.add_argument("--test-only", action="store_true", help="Run comprehensive tests only")

    args = parser.parse_args()

    workflow = PublishWorkflow()

    # Test only mode
    if args.test_only:
        success = workflow.tester.run_comprehensive_tests(include_build=True)
        return 0 if success else 1

    # Individual phase mode
    if args.phase:
        if args.phase == "validate":
            success = workflow.run_pre_publishing_validation()
        elif args.phase == "setup":
            success = workflow.run_configuration_setup()
        elif args.phase == "build":
            success = workflow.run_build_automation()
        elif args.phase == "publish":
            success = workflow.run_publishing_validation(
                include_testpypi=not args.skip_testpypi,
                include_pypi=args.include_pypi,
                test_install=not args.no_test_install,
            )
        return 0 if success else 1

    # Full workflow
    success = workflow.run_full_workflow(
        version_bump=args.version_bump,
        skip_quality_checks=args.skip_quality_checks,
        include_testpypi=not args.skip_testpypi,
        include_pypi=args.include_pypi,
        test_install=not args.no_test_install,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
