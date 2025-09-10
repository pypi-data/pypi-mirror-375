#!/usr/bin/env python3
"""Version management utility for huoshui-fetch package."""

import json
import re
from pathlib import Path


class VersionManager:
    """Manages version synchronization across project files."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.pyproject_path = self.project_root / "pyproject.toml"
        self.init_path = self.project_root / "huoshui_fetch" / "__init__.py"
        self.manifest_path = self.project_root / "manifest.json"

    def get_current_versions(self) -> dict[str, str]:
        """Get current versions from all relevant files."""
        versions = {}

        # Get version from pyproject.toml
        if self.pyproject_path.exists():
            content = self.pyproject_path.read_text()
            match = re.search(r'version = "([^"]+)"', content)
            if match:
                versions["pyproject.toml"] = match.group(1)

        # Get version from __init__.py
        if self.init_path.exists():
            content = self.init_path.read_text()
            match = re.search(r'__version__ = "([^"]+)"', content)
            if match:
                versions["__init__.py"] = match.group(1)

        # Get version from manifest.json
        if self.manifest_path.exists():
            try:
                manifest = json.loads(self.manifest_path.read_text())
                if "version" in manifest:
                    versions["manifest.json"] = manifest["version"]
            except json.JSONDecodeError:
                pass

        return versions

    def validate_version_consistency(self) -> tuple[bool, dict[str, str]]:
        """Check if all versions are consistent."""
        versions = self.get_current_versions()
        if not versions:
            return False, {}

        reference_version = list(versions.values())[0]
        consistent = all(v == reference_version for v in versions.values())
        return consistent, versions

    def update_version(self, new_version: str) -> bool:
        """Update version in all relevant files."""
        success = True

        # Update pyproject.toml
        if self.pyproject_path.exists():
            content = self.pyproject_path.read_text()
            updated_content = re.sub(r'version = "[^"]+"', f'version = "{new_version}"', content)
            self.pyproject_path.write_text(updated_content)

        # Update __init__.py
        if self.init_path.exists():
            content = self.init_path.read_text()
            if "__version__" in content:
                updated_content = re.sub(
                    r'__version__ = "[^"]+"', f'__version__ = "{new_version}"', content
                )
            else:
                # Add version if not present
                lines = content.split("\n")
                insert_idx = 1 if lines[0].startswith('"""') else 0
                for i, line in enumerate(lines[insert_idx:], insert_idx):
                    if (
                        line.strip()
                        and not line.startswith('"""')
                        and not line.startswith("from")
                        and not line.startswith("import")
                    ):
                        break
                lines.insert(i, f'__version__ = "{new_version}"')
                updated_content = "\n".join(lines)
            self.init_path.write_text(updated_content)

        # Update manifest.json
        if self.manifest_path.exists():
            try:
                manifest = json.loads(self.manifest_path.read_text())
                manifest["version"] = new_version
                self.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
            except json.JSONDecodeError:
                success = False

        return success

    def bump_version(self, bump_type: str = "patch") -> str:
        """Bump version and return new version string."""
        versions = self.get_current_versions()
        if not versions:
            return "0.1.0"

        current = list(versions.values())[0]
        parts = current.split(".")

        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {current}")

        major, minor, patch = map(int, parts)

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        new_version = f"{major}.{minor}.{patch}"
        self.update_version(new_version)
        return new_version


def main():
    """CLI interface for version management."""
    import argparse

    parser = argparse.ArgumentParser(description="Manage package version")
    parser.add_argument("--check", action="store_true", help="Check version consistency")
    parser.add_argument("--bump", choices=["major", "minor", "patch"], help="Bump version")
    parser.add_argument("--set", help="Set specific version")

    args = parser.parse_args()

    vm = VersionManager()

    if args.check:
        consistent, versions = vm.validate_version_consistency()
        print("Current versions:")
        for file, version in versions.items():
            print(f"  {file}: {version}")
        print(f"Consistent: {'✅' if consistent else '❌'}")
        return 0 if consistent else 1

    if args.bump:
        try:
            new_version = vm.bump_version(args.bump)
            print(f"Version bumped to: {new_version}")
            return 0
        except Exception as e:
            print(f"Error bumping version: {e}")
            return 1

    if args.set:
        try:
            vm.update_version(args.set)
            print(f"Version set to: {args.set}")
            return 0
        except Exception as e:
            print(f"Error setting version: {e}")
            return 1

    # Default: show current versions
    consistent, versions = vm.validate_version_consistency()
    for file, version in versions.items():
        print(f"{file}: {version}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
