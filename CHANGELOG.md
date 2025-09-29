# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete project modernization with Python 3.13+ support
- Modern src/coffee/ package structure following PEP standards
- Comprehensive type annotations throughout codebase
- Rich library integration for beautiful terminal UI
- PowerManager class for macOS power management and battery monitoring
- NetworkManager class for network interface monitoring
- ASCII art time display with animated updates
- Unit test suite with pytest framework (90%+ coverage)
- Development tooling with black, ruff, mypy, and isort
- Pre-commit hooks for automated code quality checks
- GitHub Actions CI/CD pipeline with comprehensive testing
- Security scanning with bandit and pip-audit
- Automated release workflow with changelog generation
- Comprehensive documentation (README, CONTRIBUTING, SECURITY)
- Development convenience scripts and Makefile
- Professional project structure with proper packaging

### Changed
- Migrated from legacy main.py structure to modern package layout
- Refactored all code to use classes and modern Python patterns
- Updated all dependencies to latest versions
- Improved error handling and signal management
- Enhanced system monitoring with structured data classes
- Modernized CLI interface with better user experience

### Fixed
- Code compliance with latest Python and PEP standards
- Proper package initialization and imports
- Type safety issues throughout codebase
- Code formatting and linting issues
- Security vulnerabilities in dependencies

### Technical Details
- Python 3.13+ with modern typing and dataclasses
- Hatchling build system with proper wheel generation
- pytest testing framework with fixtures and mocks
- Rich library for terminal UI components
- macOS system integration via system_profiler and pmset
- Comprehensive error handling and logging
- Signal-safe shutdown handling
- Thread-safe operations for system monitoring

## [0.1.0] - Initial Release

### Added
- Basic coffee script functionality
- Power monitoring capabilities
- Network interface monitoring
- Terminal-based display