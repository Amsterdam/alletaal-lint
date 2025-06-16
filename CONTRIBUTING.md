# Contributing to alletaal-lint

Thank you for your interest in contributing to alletaal-lint! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Issues

Before creating a new issue, please:

1. Search existing issues to avoid duplicates
2. Use the appropriate issue template
3. Provide as much relevant information as possible

#### Bug Reports

Include:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or logs
- Sample text that causes the issue (if applicable)

#### Feature Requests

Include:
- Clear description of the proposed feature
- Use case or problem it solves
- Possible implementation approach
- Any relevant research or references

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/alletaal-lint.git
   cd alletaal-lint
   ```

2. **Set up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Install Dutch spaCy Model**
   ```bash
   python -m spacy download nl_core_news_sm
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

### Making Changes

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make Your Changes**
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed
   - Keep commits focused and atomic

3. **Run Tests**
   ```bash
   pytest
   pytest --cov=alletaal_lint  # With coverage
   ```

4. **Run Linting and Formatting**
   ```bash
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

### Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking

Configuration is provided in `pyproject.toml`.

#### Style Guidelines

- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Follow PEP 8 naming conventions
- Keep line length to 88 characters (Black default)
- Use meaningful variable and function names

### Testing

- Write tests for all new functionality
- Maintain or improve test coverage
- Use descriptive test names
- Test edge cases and error conditions

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=alletaal_lint --cov-report=html

# Run specific test file
pytest tests/test_core.py

# Run tests matching pattern
pytest -k "test_lint_score"
```

### Documentation

- Update docstrings for any changed functions
- Update README.md if adding new features
- Add examples for new functionality
- Update API documentation if needed

### Commit Messages

Use clear, descriptive commit messages:

```
type(scope): brief description

Longer description if needed, explaining what and why.

Closes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build process or auxiliary tool changes

### Pull Requests

1. **Before Submitting**
   - Ensure all tests pass
   - Run linting and formatting tools
   - Update documentation
   - Rebase your branch on the latest main

2. **PR Description**
   - Clearly describe the changes
   - Reference related issues
   - Include testing information
   - Add screenshots for UI changes

3. **Review Process**
   - Address feedback promptly
   - Keep the PR updated with main
   - Be open to suggestions and changes

## Development Guidelines

### Architecture

- Keep core logic in `src/alletaal_lint/core.py`
- API endpoints in `src/alletaal_lint/api.py`
- CLI commands in `src/alletaal_lint/cli.py`
- Maintain separation of concerns

### Performance

- Consider performance impact of changes
- Profile code for performance-critical sections
- Use appropriate data structures and algorithms
- Cache expensive operations where appropriate

### Dependencies

- Minimize new dependencies
- Ensure compatibility with supported Python versions
- Update requirements files when adding dependencies
- Consider security implications of new dependencies

### Internationalization

- Keep user-facing text in English
- Use appropriate Dutch examples in documentation
- Consider localization for future CLI messages

## Research and Academic Context

This project is based on academic research. When contributing:

- Respect the scientific methodology
- Cite relevant research when proposing changes
- Consider backward compatibility with existing research
- Document algorithmic changes thoroughly

### Key References

- [LiNT methodology](https://www.gebruikercentraal.nl/hulpmiddelen/lint-leesbaarheidsinstrument-voor-nederlandse-teksten/)
- [T-Scan project](https://github.com/CentreForDigitalHumanities/tscan)
- Related academic papers on Dutch text readability

## License

By contributing to alletaal-lint, you agree that your contributions will be licensed under the EUPL-1.2 license.

## Questions?

If you have questions about contributing, please:

1. Check existing documentation
2. Search closed issues
3. Create a discussion or issue
4. Contact the maintainers at innovatie@amsterdam.nl

Thank you for contributing to making Dutch text more accessible!