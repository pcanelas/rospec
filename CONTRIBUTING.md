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

### Branch Naming

Use descriptive branch names:
- `feature/add-new-parser` for new features
- `fix/parameter-validation` for bug fixes
- `docs/update-readme` for documentation changes

## License

By contributing to rospec, you agree that your contributions will be licensed under the Apache License 2.0.
