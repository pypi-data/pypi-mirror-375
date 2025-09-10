#!/usr/bin/env python3
"""Comprehensive testing script for huoshui-fetch package."""

import asyncio
import subprocess
import sys
from pathlib import Path

from build import PackageBuilder


class PackageTester:
    """Comprehensive testing for the huoshui-fetch package."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.builder = PackageBuilder(self.project_root)

    def run_unit_tests(self) -> bool:
        """Run pytest unit tests."""
        print("🧪 Running unit tests...")

        try:
            result = subprocess.run(
                ["uv", "run", "pytest", "-v", "--tb=short"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("  ✅ All unit tests passed")
                if result.stdout:
                    # Show test summary
                    lines = result.stdout.split("\n")
                    summary_lines = [
                        line for line in lines if "passed" in line and "::" not in line
                    ]
                    if summary_lines:
                        print(f"  📊 {summary_lines[-1]}")
                return True
            else:
                print("❌ Unit tests failed:")
                print(result.stdout)
                print(result.stderr)
                return False

        except FileNotFoundError:
            print("  ⚠️  pytest not available, skipping unit tests")
            return True

    def test_package_import(self) -> bool:
        """Test basic package import and version check."""
        print("📦 Testing package import...")

        try:
            result = subprocess.run(
                [
                    "uv",
                    "run",
                    "python",
                    "-c",
                    "import huoshui_fetch; print(f'Version: {huoshui_fetch.__version__}'); print('✅ Import successful')",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"  {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Import failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Import test error: {e}")
            return False

    def test_console_script(self) -> bool:
        """Test the console script execution."""
        print("🖥️  Testing console script...")

        try:
            # Test that the script can be invoked (it's an MCP server, so it will run continuously)
            # We'll test by checking if it starts without immediate error
            result = subprocess.run(
                ["timeout", "5", "uv", "run", "huoshui-fetch"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            # For MCP servers, timeout is expected
            if result.returncode == 124:  # timeout exit code
                print("  ✅ Console script starts correctly (MCP server)")
                return True
            elif result.returncode == 0:
                print("  ✅ Console script executed successfully")
                return True
            else:
                print(f"❌ Console script failed: {result.stderr}")
                return False

        except FileNotFoundError:
            print("  ⚠️  timeout command not available, trying alternative test")
            try:
                # Alternative test - check if the script imports correctly
                result = subprocess.run(
                    [
                        "uv",
                        "run",
                        "python",
                        "-c",
                        "from huoshui_fetch import main; print('✅ Console script import successful')",
                    ],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print(f"  {result.stdout.strip()}")
                    return True
                else:
                    print(f"❌ Console script import failed: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Console script test error: {e}")
                return False

    async def test_mcp_tools(self) -> bool:
        """Test MCP tools functionality."""
        print("🔧 Testing MCP tools...")

        try:
            # Import and test some basic tools
            test_code = """
import asyncio
from huoshui_fetch.__main__ import (
    fetch_url, html_to_markdown_tool, extract_metadata_tool
)

async def test_tools():
    # Test HTML to Markdown conversion
    html = '<h1>Test</h1><p>Hello world!</p>'
    result = html_to_markdown_tool(html)
    assert result['success'] == True
    assert '# Test' in result['data']['markdown']
    print('✅ html_to_markdown_tool works')

    # Test metadata extraction
    html_with_meta = '''
    <html><head>
        <title>Test Page</title>
        <meta name="description" content="A test page">
    </head><body><h1>Content</h1></body></html>
    '''
    result = extract_metadata_tool(html_with_meta)
    assert result['success'] == True
    assert result['data']['title'] == 'Test Page'
    print('✅ extract_metadata_tool works')

    print('✅ All MCP tools tested successfully')

asyncio.run(test_tools())
"""

            result = subprocess.run(
                ["uv", "run", "python", "-c", test_code],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print(f"  {result.stdout.strip()}")
                return True
            else:
                print(f"❌ MCP tools test failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ MCP tools test error: {e}")
            return False

    def test_build_artifacts(self) -> bool:
        """Test that build artifacts are valid."""
        print("📦 Testing build artifacts...")

        dist_dir = self.project_root / "dist"

        if not dist_dir.exists():
            print("❌ No dist directory found")
            return False

        wheel_files = list(dist_dir.glob("*.whl"))
        sdist_files = list(dist_dir.glob("*.tar.gz"))

        if not wheel_files:
            print("❌ No wheel files found")
            return False

        if not sdist_files:
            print("❌ No source distribution files found")
            return False

        print(f"  ✅ Found {len(wheel_files)} wheel file(s)")
        print(f"  ✅ Found {len(sdist_files)} sdist file(s)")

        # Test wheel integrity
        try:
            result = subprocess.run(
                ["python", "-m", "zipfile", "-l", str(wheel_files[0])],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                print("  ✅ Wheel file integrity check passed")
                return True
            else:
                print(f"❌ Wheel integrity check failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Wheel test error: {e}")
            return False

    def test_dependencies(self) -> bool:
        """Test that all required dependencies are available."""
        print("📚 Testing dependencies...")

        required_deps = [
            "fastmcp",
            "httpx",
            "bs4",
            "markdownify",
            "readability",
            "pydantic",
            "lxml",
        ]

        failed_imports = []

        for dep in required_deps:
            try:
                result = subprocess.run(
                    ["uv", "run", "python", "-c", f"import {dep}; print(f'{dep}: OK')"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )

                if result.returncode == 0:
                    print(f"  ✅ {dep}")
                else:
                    failed_imports.append(dep)
                    print(f"  ❌ {dep}: {result.stderr.strip()}")

            except Exception as e:
                failed_imports.append(dep)
                print(f"  ❌ {dep}: {e}")

        if failed_imports:
            print(f"❌ Failed to import: {', '.join(failed_imports)}")
            return False

        print("  ✅ All dependencies are available")
        return True

    def run_comprehensive_tests(self, include_build: bool = False) -> bool:
        """Run all tests in sequence."""
        print("🚀 Running comprehensive test suite...\n")

        test_results = {}

        # If requested, build the package first
        if include_build:
            print("=" * 50)
            print("BUILD PHASE")
            print("=" * 50)
            test_results["build"] = self.builder.build_full(skip_quality_checks=False)
            print()

        print("=" * 50)
        print("TESTING PHASE")
        print("=" * 50)

        # Run all tests
        test_functions = [
            ("dependencies", self.test_dependencies),
            ("import", self.test_package_import),
            ("console_script", self.test_console_script),
            ("unit_tests", self.run_unit_tests),
            (
                "mcp_tools",
                asyncio.run(self.test_mcp_tools()).__class__(
                    lambda: asyncio.run(self.test_mcp_tools())
                ),
            ),
        ]

        # Add build artifact tests if dist exists
        if (self.project_root / "dist").exists():
            test_functions.append(("build_artifacts", self.test_build_artifacts))

        for test_name, test_func in test_functions:
            print(f"\n--- {test_name.upper()} ---")
            if test_name == "mcp_tools":
                # Special handling for async test
                try:
                    result = asyncio.run(self.test_mcp_tools())
                    test_results[test_name] = result
                except Exception as e:
                    print(f"❌ MCP tools test error: {e}")
                    test_results[test_name] = False
            else:
                test_results[test_name] = test_func()

        # Summary
        print("\n" + "=" * 50)
        print("TEST SUMMARY")
        print("=" * 50)

        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)

        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:20} {status}")

        print(f"\nTotal: {passed}/{total} tests passed")

        success = all(test_results.values())
        if success:
            print("\n🎉 All tests passed! Package is ready for publishing.")
        else:
            print("\n⚠️  Some tests failed. Please review and fix before publishing.")

        return success


def main():
    """CLI interface for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Test huoshui-fetch package")
    parser.add_argument("--with-build", action="store_true", help="Build package before testing")
    parser.add_argument(
        "--test",
        choices=["dependencies", "import", "console", "unit", "mcp", "build"],
        help="Run specific test only",
    )

    args = parser.parse_args()

    tester = PackageTester()

    if args.test:
        # Run specific test
        test_map = {
            "dependencies": tester.test_dependencies,
            "import": tester.test_package_import,
            "console": tester.test_console_script,
            "unit": tester.run_unit_tests,
            "mcp": lambda: asyncio.run(tester.test_mcp_tools()),
            "build": tester.test_build_artifacts,
        }

        if args.test in test_map:
            success = test_map[args.test]()
            return 0 if success else 1
        else:
            print(f"Unknown test: {args.test}")
            return 1

    # Run comprehensive tests
    success = tester.run_comprehensive_tests(include_build=args.with_build)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
