# Contributing to yfinance-mcp

Thank you for your interest in contributing to yfinance-mcp! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We welcome contributors of all experience levels.

## How to Contribute

### Reporting Issues

- Check existing issues before creating a new one
- Provide a clear description of the problem
- Include steps to reproduce the issue
- Specify your environment (OS, Python version, etc.)

### Submitting Changes

1. **Fork the repository** and create a new branch from `main`
2. **Make your changes** following the coding standards below
3. **Add or update tests** for your changes
4. **Run the test suite** to ensure all tests pass
5. **Submit a pull request** with a clear description of your changes

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/yfinance-mcp.git
cd yfinance-mcp

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions
- Keep functions focused and single-purpose
- Format code with `black` before committing

### Testing

- Write tests for new functionality
- Ensure existing tests pass
- Use pytest for testing
- Mock external API calls (yfinance) in tests

### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 72 characters
- Reference issues when applicable (e.g., "Fixes #123")

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure CI passes
4. Request review from maintainers
5. Address any feedback

## Questions?

If you have questions about contributing, please open an issue for discussion.

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.
