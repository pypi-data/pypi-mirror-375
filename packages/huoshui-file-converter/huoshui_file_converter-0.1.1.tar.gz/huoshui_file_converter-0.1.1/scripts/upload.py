#!/usr/bin/env python3
"""
Automated upload script for huoshui-file-converter PyPI package

This script provides comprehensive publishing automation including:
- TestPyPI and production PyPI upload
- Pre-upload validation
- Interactive confirmation for production
- Post-upload verification
- Installation testing from repositories
"""

import os
import sys
import subprocess
import json
import time
import requests
import getpass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import tempfile


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
    cmd: List[str],
    cwd: Optional[Path] = None,
    capture_output: bool = True,
    input_text: str = None,
) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            input=input_text,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


class PackageUploader:
    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.dist_dir = project_root / "dist"
        self.pyproject_path = project_root / "pyproject.toml"

        # Repository configurations
        self.repositories = {
            "testpypi": {
                "name": "TestPyPI",
                "url": "https://test.pypi.org/simple/",
                "upload_url": "https://test.pypi.org/legacy/",
                "web_url": "https://test.pypi.org/project/",
                "repository_flag": "--repository-url https://test.pypi.org/legacy/",
            },
            "pypi": {
                "name": "PyPI",
                "url": "https://pypi.org/simple/",
                "upload_url": "https://upload.pypi.org/legacy/",
                "web_url": "https://pypi.org/project/",
                "repository_flag": "",
            },
        }

    def get_package_info(self) -> Dict:
        """Extract package information from pyproject.toml"""
        import toml

        with open(self.pyproject_path, "r") as f:
            config = toml.load(f)

        project = config.get("project", {})
        return {
            "name": project.get("name", "unknown"),
            "version": project.get("version", "0.0.0"),
            "description": project.get("description", ""),
            "authors": project.get("authors", []),
        }

    def validate_build_artifacts(self) -> bool:
        """Validate that build artifacts exist and are complete"""
        print_header("Pre-Upload Validation")

        print_step("Checking build artifacts...")

        if not self.dist_dir.exists():
            print_error(
                "dist/ directory not found. Run 'python scripts/build.py' first."
            )
            return False

        wheel_files = list(self.dist_dir.glob("*.whl"))
        source_files = list(self.dist_dir.glob("*.tar.gz"))

        if not wheel_files:
            print_error("No wheel (.whl) files found in dist/")
            return False

        if not source_files:
            print_error("No source distribution (.tar.gz) files found in dist/")
            return False

        print_success(f"Found {len(wheel_files)} wheel file(s)")
        print_success(f"Found {len(source_files)} source distribution(s)")

        # Show artifacts
        print_step("Build artifacts to upload:")
        total_size = 0
        for file in sorted(self.dist_dir.glob("*")):
            size = file.stat().st_size
            total_size += size
            size_mb = size / (1024 * 1024)
            print(f"  - {file.name}: {size_mb:.2f} MB")

        print_success(f"Total upload size: {total_size / (1024 * 1024):.2f} MB")
        return True

    def run_twine_check(self) -> bool:
        """Run twine check on all distributions"""
        print_step("Running twine check for metadata validation...")

        code, stdout, stderr = run_command(
            ["uv", "run", "twine", "check", "dist/*"], cwd=self.project_root
        )

        if code != 0:
            print_error(f"Twine check failed: {stderr}")
            return False

        print_success("Twine check passed - all distributions are valid")
        if self.verbose:
            print(f"Output: {stdout}")

        return True

    def check_credentials(self, repository: str) -> bool:
        """Check if credentials are available for the repository"""
        print_step(f"Checking {self.repositories[repository]['name']} credentials...")

        # Check for environment variables
        if repository == "testpypi":
            token_var = "TESTPYPI_TOKEN"
            username_var = "TESTPYPI_USERNAME"
            password_var = "TESTPYPI_PASSWORD"
        else:
            token_var = "PYPI_TOKEN"
            username_var = "PYPI_USERNAME"
            password_var = "PYPI_PASSWORD"

        has_token = bool(os.environ.get(token_var))
        has_user_pass = bool(
            os.environ.get(username_var) and os.environ.get(password_var)
        )

        if has_token:
            print_success(f"API token found in environment variable {token_var}")
            return True
        elif has_user_pass:
            print_success(f"Username/password found in environment variables")
            return True
        else:
            print_warning(f"No credentials found in environment variables")
            print(f"Set {token_var} or {username_var}/{password_var}")
            print("You'll be prompted for credentials during upload")
            return True  # We'll let twine handle the prompting

    def check_package_exists(
        self, repository: str, package_name: str, version: str
    ) -> bool:
        """Check if package version already exists on repository"""
        print_step(
            f"Checking if {package_name} v{version} exists on {self.repositories[repository]['name']}..."
        )

        try:
            if repository == "testpypi":
                url = f"https://test.pypi.org/pypi/{package_name}/{version}/json"
            else:
                url = f"https://pypi.org/pypi/{package_name}/{version}/json"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                print_warning(
                    f"Version {version} already exists on {self.repositories[repository]['name']}"
                )
                return True
            elif response.status_code == 404:
                print_success(f"Version {version} is available for upload")
                return False
            else:
                print_warning(
                    f"Could not verify package existence (HTTP {response.status_code})"
                )
                return False

        except requests.RequestException as e:
            print_warning(f"Could not check package existence: {e}")
            return False

    def upload_to_repository(self, repository: str, dry_run: bool = False) -> bool:
        """Upload package to specified repository"""
        repo_info = self.repositories[repository]
        package_info = self.get_package_info()

        print_header(f"Phase 4: Upload to {repo_info['name']}")

        if dry_run:
            print_step("DRY RUN MODE - No actual upload will occur")

        # Pre-upload checks
        print_step("Running pre-upload checks...")

        # Check if version already exists
        exists = self.check_package_exists(
            repository, package_info["name"], package_info["version"]
        )
        if exists:
            if not dry_run:
                confirm = input(
                    f"Version {package_info['version']} already exists. Continue? (y/N): "
                )
                if confirm.lower() != "y":
                    print("Upload cancelled by user")
                    return False

        # Build twine command
        cmd = ["uv", "run", "twine", "upload"]

        if dry_run:
            print_success("Dry run completed - command would be:")
            print(f"  {' '.join(cmd)} {repo_info['repository_flag']} dist/*")
            return True

        if repository == "testpypi":
            cmd.extend(["--repository-url", "https://test.pypi.org/legacy/"])

        cmd.append("dist/*")

        print_step(f"Uploading to {repo_info['name']}...")
        if self.verbose:
            print(f"Command: {' '.join(cmd)}")

        # Run upload
        code, stdout, stderr = run_command(
            cmd, cwd=self.project_root, capture_output=False
        )

        if code != 0:
            print_error(f"Upload to {repo_info['name']} failed")
            if stderr:
                print(f"Error: {stderr}")
            return False

        print_success(f"Upload to {repo_info['name']} completed successfully!")

        # Show package URL
        package_url = f"{repo_info['web_url']}{package_info['name']}/"
        print(f"\n{Colors.BOLD}📦 Package URL:{Colors.RESET}")
        print(f"   {package_url}")

        return True

    def test_installation_from_repository(
        self, repository: str, package_name: str, timeout: int = 300
    ) -> bool:
        """Test package installation from repository"""
        repo_info = self.repositories[repository]

        print_header(f"Installation Test from {repo_info['name']}")

        print_step("Creating test environment...")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            venv_path = temp_path / "test_env"

            # Create virtual environment
            code, stdout, stderr = run_command(["python", "-m", "venv", str(venv_path)])
            if code != 0:
                print_error(f"Failed to create test environment: {stderr}")
                return False

            # Setup pip and python paths
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

            # Wait for package to be available
            print_step(
                f"Waiting for package to become available on {repo_info['name']}..."
            )

            max_attempts = timeout // 10
            for attempt in range(max_attempts):
                time.sleep(10)

                # Try to install
                install_cmd = [
                    pip_cmd,
                    "install",
                    "--index-url",
                    repo_info["url"],
                    package_name,
                ]

                code, stdout, stderr = run_command(install_cmd, capture_output=True)

                if code == 0:
                    print_success(
                        f"Package installed successfully (attempt {attempt + 1})"
                    )
                    break
                else:
                    if attempt < max_attempts - 1:
                        print_step(f"Attempt {attempt + 1} failed, retrying in 10s...")
                    else:
                        print_error(
                            f"Installation failed after {max_attempts} attempts"
                        )
                        if stderr:
                            print(f"Last error: {stderr}")
                        return False

            # Test import
            print_step("Testing package import...")
            code, stdout, stderr = run_command(
                [python_cmd, "-c", 'import server; print("✅ Import successful")']
            )

            if code != 0:
                print_error(f"Import test failed: {stderr}")
                return False

            print_success("Package import test passed")

            # Test console script
            package_info = self.get_package_info()
            import toml

            with open(self.pyproject_path, "r") as f:
                config = toml.load(f)

            scripts = config.get("project", {}).get("scripts", {})
            if scripts:
                script_name = list(scripts.keys())[0]
                script_cmd = (
                    str(venv_path / "bin" / script_name)
                    if os.name != "nt"
                    else str(venv_path / "Scripts" / script_name + ".exe")
                )

                print_step(f"Testing console script: {script_name}")

                if Path(script_cmd).exists():
                    code, stdout, stderr = run_command([script_cmd, "--version"])

                    if code == 0:
                        print_success("Console script test passed")
                    else:
                        print_warning(
                            f"Console script test failed (may be expected): {stderr}"
                        )
                else:
                    print_warning("Console script not found in test environment")

        return True

    def generate_upload_report(self, repository: str, success: bool) -> Dict:
        """Generate upload report"""
        package_info = self.get_package_info()
        repo_info = self.repositories[repository]

        report = {
            "package_name": package_info["name"],
            "version": package_info["version"],
            "repository": repo_info["name"],
            "upload_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "upload_success": success,
            "package_url": f"{repo_info['web_url']}{package_info['name']}/"
            if success
            else None,
            "artifacts_uploaded": [],
        }

        if self.dist_dir.exists():
            for file in self.dist_dir.glob("*"):
                report["artifacts_uploaded"].append(
                    {"filename": file.name, "size_bytes": file.stat().st_size}
                )

        # Save report
        report_filename = f"upload_report_{repository}_{int(time.time())}.json"
        report_path = self.project_root / report_filename

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)

        print_success(f"Upload report saved to: {report_filename}")
        return report

    def interactive_production_upload(self) -> bool:
        """Interactive production upload with confirmations"""
        package_info = self.get_package_info()

        print_header("🚨 PRODUCTION PyPI UPLOAD", Colors.RED)
        print(
            f"{Colors.YELLOW}⚠️  You are about to upload to PRODUCTION PyPI!{Colors.RESET}"
        )
        print()
        print(f"Package: {Colors.BOLD}{package_info['name']}{Colors.RESET}")
        print(f"Version: {Colors.BOLD}{package_info['version']}{Colors.RESET}")
        print()
        print("This action cannot be undone. Once uploaded, you cannot:")
        print("- Delete the package")
        print("- Re-upload the same version")
        print("- Modify the uploaded files")
        print()

        # First confirmation
        confirm1 = input(
            f"{Colors.BOLD}Type the package name to continue: {Colors.RESET}"
        )
        if confirm1 != package_info["name"]:
            print_error("Package name mismatch. Upload cancelled.")
            return False

        # Second confirmation
        confirm2 = input(
            f"{Colors.BOLD}Type 'UPLOAD' to confirm production upload: {Colors.RESET}"
        )
        if confirm2 != "UPLOAD":
            print_error("Confirmation failed. Upload cancelled.")
            return False

        print_success("Confirmations received. Proceeding with production upload...")
        return True

    def run_upload_workflow(
        self, target: str, test_install: bool = True, dry_run: bool = False
    ) -> bool:
        """Run the complete upload workflow"""
        start_time = time.time()

        if target == "prod":
            target = "pypi"
        elif target == "test":
            target = "testpypi"

        if target not in self.repositories:
            print_error(f"Unknown repository: {target}")
            return False

        repo_info = self.repositories[target]
        package_info = self.get_package_info()

        print_header(f"🚀 Upload Workflow - {repo_info['name']}")

        # Pre-upload validation
        if not self.validate_build_artifacts():
            return False

        if not self.run_twine_check():
            return False

        self.check_credentials(target)

        # Production upload requires interactive confirmation
        if target == "pypi" and not dry_run:
            if not self.interactive_production_upload():
                return False

        # Upload
        success = self.upload_to_repository(target, dry_run=dry_run)

        if not success:
            return False

        # Generate report
        self.generate_upload_report(target, success)

        # Test installation
        if test_install and not dry_run:
            print_step("Waiting 30 seconds before installation test...")
            time.sleep(30)

            install_success = self.test_installation_from_repository(
                target, package_info["name"]
            )
            if not install_success:
                print_warning("Installation test failed, but upload was successful")

        upload_time = time.time() - start_time
        print_header(f"🎉 UPLOAD COMPLETED - {upload_time:.1f}s", Colors.GREEN)

        if target == "testpypi":
            print(f"\n{Colors.BOLD}Next steps:{Colors.RESET}")
            print("1. Test the installation manually:")
            print(
                f"   pip install --index-url https://test.pypi.org/simple/ {package_info['name']}"
            )
            print("2. If everything works, upload to production:")
            print("   python scripts/upload.py --prod")
        else:
            print(f"\n{Colors.BOLD}🎊 Package is now live on PyPI!{Colors.RESET}")
            print(f"Install with: pip install {package_info['name']}")
            print(f"Package URL: {repo_info['web_url']}{package_info['name']}/")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Upload huoshui-file-converter to PyPI repositories"
    )
    parser.add_argument("--test", action="store_true", help="Upload to TestPyPI")
    parser.add_argument("--prod", action="store_true", help="Upload to production PyPI")
    parser.add_argument(
        "--no-test-install", action="store_true", help="Skip installation testing"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be uploaded without actually uploading",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    if not args.test and not args.prod:
        print_error("Specify --test for TestPyPI or --prod for production PyPI")
        parser.print_help()
        sys.exit(1)

    if args.test and args.prod:
        print_error("Cannot specify both --test and --prod")
        sys.exit(1)

    project_root = Path(__file__).parent.parent
    uploader = PackageUploader(project_root, verbose=args.verbose)

    target = "test" if args.test else "prod"
    test_install = not args.no_test_install

    success = uploader.run_upload_workflow(
        target, test_install=test_install, dry_run=args.dry_run
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
