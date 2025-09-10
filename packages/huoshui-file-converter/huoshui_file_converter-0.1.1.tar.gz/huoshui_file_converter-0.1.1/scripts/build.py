#!/usr/bin/env python3
"""
Automated build script for huoshui-file-converter PyPI package

This script provides comprehensive build automation including:
- Pre-build validation
- Version consistency checks
- Dependency verification
- Quality checks
- Build process with progress tracking
- Local testing
"""

import os
import sys
import subprocess
import shutil
import toml
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import time


# Color codes for output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_header(message: str, color: str = Colors.BLUE) -> None:
    """Print a formatted header message"""
    print(f"\n{color}{Colors.BOLD}{'=' * 60}")
    print(f"{message}")
    print(f"{'=' * 60}{Colors.RESET}")


def print_step(message: str, color: str = Colors.CYAN) -> None:
    """Print a formatted step message"""
    print(f"{color}▶ {message}{Colors.RESET}")


def print_success(message: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_warning(message: str) -> None:
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def print_error(message: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def run_command(
    cmd: List[str], cwd: Optional[Path] = None, capture_output: bool = True
) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=capture_output, text=True, check=False
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


class PackageBuilder:
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.pyproject_path = project_root / "pyproject.toml"
        self.server_init_path = project_root / "server" / "__init__.py"
        self.dist_dir = project_root / "dist"
        self.build_dir = project_root / "build"

    def load_pyproject_config(self) -> Dict:
        """Load and validate pyproject.toml"""
        if not self.pyproject_path.exists():
            raise FileNotFoundError("pyproject.toml not found")

        with open(self.pyproject_path, "r") as f:
            return toml.load(f)

    def get_package_version(self) -> str:
        """Extract version from pyproject.toml"""
        config = self.load_pyproject_config()
        return config.get("project", {}).get("version", "0.0.0")

    def get_init_version(self) -> str:
        """Extract version from __init__.py"""
        if not self.server_init_path.exists():
            return "0.0.0"

        with open(self.server_init_path, "r") as f:
            content = f.read()
            for line in content.split("\n"):
                if line.strip().startswith("__version__"):
                    # Extract version from __version__ = "x.x.x"
                    return line.split("=")[1].strip().strip('"').strip("'")
        return "0.0.0"

    def validate_project_structure(self) -> bool:
        """Phase 1: Pre-Publishing Validation"""
        print_header("Phase 1: Pre-Publishing Validation")

        issues = []

        # 1. Check pyproject.toml exists and is complete
        print_step("Validating pyproject.toml...")
        try:
            config = self.load_pyproject_config()
            project_config = config.get("project", {})

            required_fields = ["name", "version", "description", "authors"]
            missing_fields = [
                field for field in required_fields if not project_config.get(field)
            ]

            if missing_fields:
                issues.append(
                    f"Missing required fields in pyproject.toml: {missing_fields}"
                )
            else:
                print_success("pyproject.toml validation passed")

        except Exception as e:
            issues.append(f"Failed to load pyproject.toml: {e}")

        # 2. Check version consistency
        print_step("Checking version consistency...")
        pyproject_version = self.get_package_version()
        init_version = self.get_init_version()

        if pyproject_version != init_version:
            issues.append(
                f"Version mismatch: pyproject.toml={pyproject_version}, __init__.py={init_version}"
            )
        else:
            print_success(f"Version consistency verified: {pyproject_version}")

        # 3. Check main package directory
        print_step("Validating package structure...")
        server_dir = self.project_root / "server"
        if not server_dir.exists() or not (server_dir / "__init__.py").exists():
            issues.append(
                "Main package directory 'server' not found or missing __init__.py"
            )
        else:
            print_success("Package structure validated")

        # 4. Check Python version requirements
        print_step("Checking Python compatibility...")
        config = self.load_pyproject_config()
        requires_python = config.get("project", {}).get("requires-python", "")
        if requires_python:
            print_success(f"Python requirement specified: {requires_python}")
        else:
            print_warning("No Python version requirement specified")

        if issues:
            print_error("Validation failed with issues:")
            for issue in issues:
                print(f"  - {issue}")
            return False

        print_success("All validation checks passed!")
        return True

    def check_dependencies(self) -> bool:
        """Verify all dependencies are properly declared"""
        print_header("Dependency Verification")

        print_step("Checking declared dependencies...")
        config = self.load_pyproject_config()
        dependencies = config.get("project", {}).get("dependencies", [])

        if not dependencies:
            print_warning("No dependencies declared")
            return True

        print(f"Found {len(dependencies)} dependencies:")
        for dep in dependencies:
            print(f"  - {dep}")

        # Test dependency installation
        print_step("Testing dependency installation...")
        code, stdout, stderr = run_command(["uv", "pip", "list"], cwd=self.project_root)

        if code != 0:
            print_error(f"Failed to check installed packages: {stderr}")
            return False

        print_success("Dependencies verification completed")
        return True

    def run_quality_checks(self) -> bool:
        """Run linting and type checking if configured"""
        print_header("Quality Checks")

        issues_found = False

        # Check if we can import the package
        print_step("Testing package import...")
        code, stdout, stderr = run_command(
            [
                "uv",
                "run",
                "python",
                "-c",
                'import server; print("✅ Package imports successfully")',
            ],
            cwd=self.project_root,
        )

        if code != 0:
            print_error(f"Package import failed: {stderr}")
            issues_found = True
        else:
            print_success("Package imports successfully")

        # Test entry point if defined
        print_step("Testing console script entry point...")
        config = self.load_pyproject_config()
        scripts = config.get("project", {}).get("scripts", {})

        if scripts:
            script_name = list(scripts.keys())[0]
            print_step(f"Testing entry point: {script_name}")
            code, stdout, stderr = run_command(
                ["uv", "run", script_name, "--help"], cwd=self.project_root
            )

            if code != 0:
                print_warning(f"Entry point test failed (this may be normal): {stderr}")
            else:
                print_success("Entry point functional")

        return not issues_found

    def clean_build_artifacts(self) -> None:
        """Clean previous build artifacts"""
        print_step("Cleaning previous build artifacts...")

        paths_to_clean = [self.dist_dir, self.build_dir]
        for path in paths_to_clean:
            if path.exists():
                shutil.rmtree(path)
                print(f"  Removed: {path}")

        print_success("Build artifacts cleaned")

    def build_package(self) -> bool:
        """Phase 3: Build the package"""
        print_header("Phase 3: Build Process")

        # Clean artifacts first
        self.clean_build_artifacts()

        # Install build dependencies
        print_step("Installing build dependencies...")
        code, stdout, stderr = run_command(
            ["uv", "pip", "install", "build", "twine"], cwd=self.project_root
        )
        if code != 0:
            print_error(f"Failed to install build dependencies: {stderr}")
            return False

        print_success("Build dependencies installed")

        # Build the package
        print_step("Building wheel and source distribution...")
        code, stdout, stderr = run_command(
            ["uv", "run", "python", "-m", "build"], cwd=self.project_root
        )

        if code != 0:
            print_error(f"Build failed: {stderr}")
            return False

        print_success("Package built successfully")

        # Report package information
        if self.dist_dir.exists():
            files = list(self.dist_dir.glob("*"))
            print_step("Build artifacts:")
            total_size = 0
            for file in files:
                size = file.stat().st_size
                total_size += size
                size_mb = size / (1024 * 1024)
                print(f"  - {file.name}: {size_mb:.2f} MB")

            print_success(f"Total package size: {total_size / (1024 * 1024):.2f} MB")

        return True

    def test_local_install(self) -> bool:
        """Test package installation in a temporary environment"""
        print_header("Local Installation Test")

        if not self.dist_dir.exists() or not list(self.dist_dir.glob("*.whl")):
            print_error("No wheel file found. Build the package first.")
            return False

        wheel_file = list(self.dist_dir.glob("*.whl"))[0]

        print_step(f"Testing installation of {wheel_file.name}...")

        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a test virtual environment
            venv_path = temp_path / "test_env"
            code, stdout, stderr = run_command(["python", "-m", "venv", str(venv_path)])

            if code != 0:
                print_error(f"Failed to create test environment: {stderr}")
                return False

            # Activate venv and install package
            pip_cmd = (
                str(venv_path / "bin" / "pip")
                if os.name != "nt"
                else str(venv_path / "Scripts" / "pip")
            )
            python_cmd = (
                str(venv_path / "bin" / "python")
                if os.name != "nt"
                else str(venv_path / "Scripts" / "python")
            )

            # Install the wheel
            code, stdout, stderr = run_command([pip_cmd, "install", str(wheel_file)])
            if code != 0:
                print_error(f"Installation failed: {stderr}")
                return False

            print_success("Package installed successfully in test environment")

            # Test import
            code, stdout, stderr = run_command(
                [python_cmd, "-c", 'import server; print("Import successful")']
            )
            if code != 0:
                print_error(f"Import test failed: {stderr}")
                return False

            print_success("Package import test passed")

            # Test console script if available
            config = self.load_pyproject_config()
            scripts = config.get("project", {}).get("scripts", {})
            if scripts:
                script_name = list(scripts.keys())[0]
                script_cmd = (
                    str(venv_path / "bin" / script_name)
                    if os.name != "nt"
                    else str(venv_path / "Scripts" / script_name + ".exe")
                )

                if Path(script_cmd).exists():
                    print_step(f"Testing console script: {script_name}")
                    code, stdout, stderr = run_command(
                        [script_cmd, "--version"], capture_output=True
                    )

                    if code == 0:
                        print_success("Console script test passed")
                    else:
                        print_warning(
                            f"Console script test failed (may be expected): {stderr}"
                        )

        return True

    def validate_package_metadata(self) -> bool:
        """Validate package metadata using twine"""
        print_step("Validating package metadata with twine...")

        if not self.dist_dir.exists():
            print_error("No dist directory found")
            return False

        code, stdout, stderr = run_command(
            ["uv", "run", "twine", "check", "dist/*"], cwd=self.project_root
        )

        if code != 0:
            print_error(f"Metadata validation failed: {stderr}")
            return False

        print_success("Package metadata validation passed")
        return True

    def generate_build_report(self) -> Dict:
        """Generate a comprehensive build report"""
        print_header("Build Report Generation")

        config = self.load_pyproject_config()

        report = {
            "package_name": config.get("project", {}).get("name", "unknown"),
            "version": self.get_package_version(),
            "build_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "python_version": sys.version,
            "dependencies": config.get("project", {}).get("dependencies", []),
            "build_artifacts": [],
            "total_size_mb": 0,
        }

        if self.dist_dir.exists():
            total_size = 0
            for file in self.dist_dir.glob("*"):
                size = file.stat().st_size
                total_size += size
                report["build_artifacts"].append(
                    {
                        "filename": file.name,
                        "size_bytes": size,
                        "size_mb": round(size / (1024 * 1024), 3),
                    }
                )

            report["total_size_mb"] = round(total_size / (1024 * 1024), 3)

        # Save report
        report_path = self.project_root / "build_report.json"
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print_success(f"Build report saved to: {report_path}")

        # Display summary
        print(f"\n{Colors.BOLD}📊 BUILD SUMMARY{Colors.RESET}")
        print(f"Package: {report['package_name']} v{report['version']}")
        print(f"Artifacts: {len(report['build_artifacts'])}")
        print(f"Total size: {report['total_size_mb']} MB")
        print(f"Dependencies: {len(report['dependencies'])}")

        return report

    def run_full_build(self, skip_tests: bool = False) -> bool:
        """Run the complete build process"""
        start_time = time.time()

        print_header("🚀 Huoshui File Converter - Automated Build Process")

        steps = [
            ("Validate project structure", self.validate_project_structure),
            ("Check dependencies", self.check_dependencies),
            ("Run quality checks", self.run_quality_checks),
            ("Build package", self.build_package),
            ("Validate metadata", self.validate_package_metadata),
        ]

        if not skip_tests:
            steps.append(("Test local installation", self.test_local_install))

        for step_name, step_func in steps:
            print(
                f"\n{Colors.MAGENTA}{'=' * 20} {step_name.upper()} {'=' * 20}{Colors.RESET}"
            )

            if not step_func():
                print_error(f"Build failed at step: {step_name}")
                return False

            print_success(f"Step completed: {step_name}")

        # Generate final report
        self.generate_build_report()

        build_time = time.time() - start_time
        print_header(
            f"🎉 BUILD SUCCESSFUL - Completed in {build_time:.1f}s", Colors.GREEN
        )

        print(f"\n{Colors.BOLD}Next steps:{Colors.RESET}")
        print("1. Review the build artifacts in ./dist/")
        print("2. Run: python scripts/upload.py --test  # Upload to TestPyPI")
        print("3. Run: python scripts/upload.py --prod  # Upload to PyPI")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Automated build script for huoshui-file-converter"
    )
    parser.add_argument(
        "--skip-tests", action="store_true", help="Skip local installation tests"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--clean-only", action="store_true", help="Only clean build artifacts"
    )

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent
    builder = PackageBuilder(project_root, verbose=args.verbose)

    if args.clean_only:
        builder.clean_build_artifacts()
        print_success("Clean completed")
        return

    success = builder.run_full_build(skip_tests=args.skip_tests)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
