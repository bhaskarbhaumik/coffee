# Contributing to Coffee Script

Thank you for your interest in contributing to Coffee Script! This document provides guidelines and information for contributors.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct (see CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- Python 3.13 or higher
- uv package manager (recommended) or pip
- Git

### Setting up the Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/bhaskarbhaumik/coffee.git
   cd coffee
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Verify the setup**:
   ```bash
   python -m pytest
   python dev.py lint
   ```

## Development Workflow

### Project Structure

```
coffee/
├── src/coffee/           # Main package source code
│   ├── __init__.py      # Package initialization
│   ├── main.py          # CLI application entry point
│   ├── power.py         # Power management functionality
│   └── network.py       # Network monitoring functionality
├── tests/               # Test suite
│   ├── conftest.py      # Test configuration and fixtures
│   ├── test_main.py     # Main module tests
│   ├── test_power.py    # Power module tests
│   ├── test_network.py  # Network module tests
│   └── test_integration.py # Integration tests
├── docs/                # Documentation
├── .github/             # GitHub workflows and templates
└── pyproject.toml       # Project configuration
```

### Development Commands

We provide several convenience commands via the `dev.py` script:

```bash
# Run tests
python dev.py test

# Run tests with coverage
python dev.py test --coverage

# Run linting
python dev.py lint

# Format code
python dev.py format

# Type checking
python dev.py type-check

# Run all quality checks
python dev.py check

# Build package
python dev.py build

# Clean build artifacts
python dev.py clean
```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write clean, well-documented code
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**:
   ```bash
   python dev.py check
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Standards

### Code Style

- **Formatting**: We use `black` for code formatting
- **Import Sorting**: We use `isort` for import organization
- **Linting**: We use `ruff` for comprehensive linting
- **Type Checking**: We use `mypy` for static type analysis

### Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

### Code Quality

- **Type Hints**: All functions and methods must have type annotations
- **Documentation**: Public functions and classes must have docstrings
- **Testing**: New features must include appropriate tests
- **Coverage**: Maintain test coverage above 90%

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src/coffee --cov-report=html

# Run specific test file
python -m pytest tests/test_power.py

# Run specific test
python -m pytest tests/test_power.py::test_battery_info
```

### Writing Tests

- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common test data
- Mock external dependencies
- Test both success and error cases

### Test Structure

```python
def test_function_name():
    # Arrange
    input_data = "test data"
    expected_result = "expected output"
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_result
```

## Documentation

### Code Documentation

- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Type Hints**: Comprehensive type annotations for all function parameters and return values
- **Comments**: Explain complex logic and business rules

### Example Docstring

```python
def calculate_battery_percentage(current: int, maximum: int) -> float:
    """Calculate battery percentage from current and maximum values.
    
    Args:
        current: Current battery level in mAh
        maximum: Maximum battery capacity in mAh
        
    Returns:
        Battery percentage as a float between 0.0 and 100.0
        
    Raises:
        ValueError: If maximum is zero or negative
        
    Example:
        >>> calculate_battery_percentage(2500, 5000)
        50.0
    """
```

## Pull Request Process

1. **Before Submitting**:
   - Ensure all tests pass
   - Verify code quality checks pass
   - Update documentation if needed
   - Add changelog entry if applicable

2. **Pull Request Description**:
   - Clearly describe the changes made
   - Reference any related issues
   - Include screenshots for UI changes
   - List any breaking changes

3. **Review Process**:
   - At least one maintainer review required
   - All CI checks must pass
   - Address any feedback promptly

## Release Process

Releases are handled by maintainers:

1. Version is bumped in `pyproject.toml`
2. Changelog is updated
3. Tag is created following semantic versioning
4. GitHub Actions automatically builds and publishes to PyPI

## Getting Help

- **Issues**: Create a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check the README and docs/ directory
- **Code Examples**: Look at the test suite for usage examples

## Recognition

Contributors are recognized in:
- CHANGELOG.md for their contributions
- GitHub contributors list
- Release notes for significant contributions

Thank you for contributing to Coffee Script!