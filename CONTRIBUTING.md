# Contributing to rospec

We welcome contributions to rospec! This document provides guidelines for contributing to the project.

## Development Setup

### Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)
- [uv (>=0.7.6)](https://docs.astral.sh/uv/getting-started/installation/)

### Setting up your development environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pcanelas/rospec.git
   cd rospec
   ```

2. **Create a virtual environment and install dependencies:**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync --dev
   ```

3. **Install pre-commit hooks:**
   ```bash
   uv run pre-commit install
   ```

## Development Workflow

### Code Style and Quality

We use several tools to maintain code quality:

- **Ruff**: For linting and code formatting
- **mypy**: For type checking
- **pytest**: For testing

### Running Tests

Run the test suite:
```bash
uv run pytest
```

Run tests with coverage:
```bash
uv run pytest
```

### Code Formatting and Linting

Format code and check for issues:
```bash
# Format code
uv run ruff format

# Check for linting issues
uv run ruff check

# Auto-fix linting issues where possible
uv run ruff check --fix
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-parser` for new features
- `fix/parameter-validation` for bug fixes
- `docs/update-readme` for documentation changes

### Commit Messages

Write clear, descriptive commit messages:
- Use the imperative mood ("Add feature" not "Added feature")
- Keep the first line under 50 characters
- Provide more detail in the body if necessary

Example:
```
Add support for service specifications

- Implement service type parsing
- Add validation for service connections
- Update grammar to include service definitions
```

### Pull Requests

1. **Create a new branch** from `main`
2. **Make your changes** following the coding standards
3. **Add tests** for new functionality
4. **Update documentation** if necessary
5. **Ensure all tests pass** and pre-commit hooks succeed
6. **Submit a pull request** with a clear description of your changes

## Code of Conduct

Please be respectful and professional in all interactions. We aim to create an inclusive and welcoming environment for all contributors.

## License

By contributing to rospec, you agree that your contributions will be licensed under the Apache License 2.0.
