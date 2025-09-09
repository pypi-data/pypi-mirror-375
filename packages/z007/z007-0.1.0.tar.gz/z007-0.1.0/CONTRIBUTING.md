# Contributing to z007

Thank you for your interest in contributing to z007! This document provides guidelines and instructions for contributors.

## Development Setup

### Prerequisites
- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager

### Setup
```bash
# Clone the repository
git clone https://github.com/okigan/z007.git
cd z007

# Install dependencies
uv sync

# Install in development mode
uv pip install -e .
```

## Development Workflow

### Running the Application
```bash
# Run the CLI
uv run z007

# Run with specific options
uv run z007 --model-id "anthropic.claude-3-sonnet-20240229-v1:0"
```

### Testing
```bash
# Run tests
uv run python test.py

# Run examples
uv run python examples.py
```

### Code Quality
```bash
# Format code
uv run ruff format z007/

# Check linting
uv run ruff check z007/

# Type checking
uv run mypy z007/
```

### Building
```bash
# Build the package
uv build

# Test installation
uv pip install dist/z007-*.whl
```

## Making Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests and linting: `make ci` or `just ci`
5. Commit your changes: `git commit -am "Add feature"`
6. Push to your fork: `git push origin feature-name`
7. Create a Pull Request

## Code Style

- Use [Ruff](https://github.com/astral-sh/ruff) for formatting and linting
- Follow [PEP 8](https://pep8.org/) style guidelines
- Add type hints where possible
- Write docstrings for public functions

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` (if you have one)
3. Build: `uv build`
4. Test publish: `uv publish --repository testpypi`
5. Publish: `uv publish`

## Questions?

Feel free to open an issue if you have questions about contributing!
