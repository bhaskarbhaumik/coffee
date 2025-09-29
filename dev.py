#!/usr/bin/env python3
"""
Development script for Coffee Script project
Provides common development tasks and utilities
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str = "") -> bool:
    """Run a command and return success status."""
    if description:
        print(f"🔄 {description}...")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(e.stderr)
        return False


def install_dev_dependencies():
    """Install development dependencies."""
    return run_command(
        ["pip", "install", "-e", ".[dev]"], 
        "Installing development dependencies"
    )


def setup_pre_commit():
    """Set up pre-commit hooks."""
    commands = [
        (["pre-commit", "install"], "Installing pre-commit hooks"),
        (["pre-commit", "install", "--hook-type", "commit-msg"], "Installing commit message hooks"),
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    return True


def run_tests(coverage: bool = False, verbose: bool = False):
    """Run the test suite."""
    cmd = ["pytest"]
    
    if coverage:
        cmd.extend(["--cov=src/coffee", "--cov-report=html", "--cov-report=term"])
    
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    cmd.append("tests/")
    
    return run_command(cmd, "Running tests")


def run_linting():
    """Run linting tools."""
    commands = [
        (["black", "--check", "src/", "tests/"], "Checking code formatting with black"),
        (["ruff", "check", "src/", "tests/"], "Linting with ruff"),
        (["mypy", "src/coffee/"], "Type checking with mypy"),
    ]
    
    success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            success = False
    
    return success


def format_code():
    """Format code with black and ruff."""
    commands = [
        (["black", "src/", "tests/"], "Formatting code with black"),
        (["ruff", "--fix", "src/", "tests/"], "Auto-fixing issues with ruff"),
        (["isort", "src/", "tests/"], "Sorting imports with isort"),
    ]
    
    success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            success = False
    
    return success


def clean_project():
    """Clean build artifacts and cache files."""
    import shutil
    
    paths_to_clean = [
        "build/",
        "dist/",
        "*.egg-info/",
        "__pycache__/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".ruff_cache/",
        "htmlcov/",
        ".coverage",
    ]
    
    project_root = Path.cwd()
    cleaned = []
    
    for pattern in paths_to_clean:
        if pattern.endswith("/"):
            # Directory patterns
            for path in project_root.rglob(pattern.rstrip("/")):
                if path.is_dir():
                    shutil.rmtree(path)
                    cleaned.append(str(path))
        else:
            # File patterns
            for path in project_root.rglob(pattern):
                if path.is_file():
                    path.unlink()
                    cleaned.append(str(path))
    
    if cleaned:
        print(f"🧹 Cleaned {len(cleaned)} items:")
        for item in cleaned[:10]:  # Show first 10 items
            print(f"  - {item}")
        if len(cleaned) > 10:
            print(f"  ... and {len(cleaned) - 10} more")
    else:
        print("✨ Project already clean")
    
    return True


def build_package():
    """Build the package."""
    return run_command(
        ["python", "-m", "build"], 
        "Building package"
    )


def run_security_check():
    """Run security checks."""
    commands = [
        (["bandit", "-r", "src/"], "Running security checks with bandit"),
        (["pip-audit"], "Checking for known vulnerabilities in dependencies"),
    ]
    
    success = True
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            success = False
    
    return success


def main():
    """Main development script entry point."""
    parser = argparse.ArgumentParser(description="Coffee Script Development Tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up development environment")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--coverage", "-c", action="store_true", help="Run with coverage")
    test_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Lint command
    lint_parser = subparsers.add_parser("lint", help="Run linting tools")
    
    # Format command
    format_parser = subparsers.add_parser("format", help="Format code")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean build artifacts")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build package")
    
    # Security command
    security_parser = subparsers.add_parser("security", help="Run security checks")
    
    # All command
    all_parser = subparsers.add_parser("all", help="Run complete development workflow")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    success = True
    
    if args.command == "setup":
        success &= install_dev_dependencies()
        success &= setup_pre_commit()
    
    elif args.command == "test":
        success &= run_tests(coverage=args.coverage, verbose=args.verbose)
    
    elif args.command == "lint":
        success &= run_linting()
    
    elif args.command == "format":
        success &= format_code()
    
    elif args.command == "clean":
        success &= clean_project()
    
    elif args.command == "build":
        success &= clean_project()
        success &= build_package()
    
    elif args.command == "security":
        success &= run_security_check()
    
    elif args.command == "all":
        print("🚀 Running complete development workflow...")
        success &= format_code()
        success &= run_linting()
        success &= run_tests(coverage=True)
        success &= run_security_check()
        success &= build_package()
    
    if success:
        print("✅ All tasks completed successfully!")
        return 0
    else:
        print("❌ Some tasks failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())