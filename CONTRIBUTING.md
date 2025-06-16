# Contributing to alletaal-lint

Thanks for your interest in contributing! 

## Quick Start

1. **Fork and clone** the repository
2. **Set up your environment**:
   ```bash
   pip install -e ".[dev]"
   python -m spacy download nl_core_news_sm
   ```
3. **Make your changes**
4. **Run tests**: `make test`
5. **Submit a pull request**

## Reporting Issues

Found a bug or have a feature idea? [Create an issue](https://github.com/Amsterdam/alletaal-lint/issues/new/choose) using one of our templates.

## Development

### Code Style
We use standard Python tools:
- **Black** for formatting
- **flake8** for linting  
- **mypy** for type checking

Run `make format` and `make lint` before submitting.

### Testing
- Add tests for new features
- Run `make test` to check everything works
- Aim for good test coverage

### Pull Requests
- Keep changes focused
- Update docs if needed
- Make sure tests pass
- Use the PR template

## Need Help?

- Check the [README](README.md) and [METHODOLOGY](METHODOLOGY.md) 
- Look at existing [issues](https://github.com/Amsterdam/alletaal-lint/issues)
- Ask questions in a new issue

## Scientific Context

This project implements the LiNT methodology for Dutch text readability. When making changes that affect scoring:
- Preserve scientific validity
- Document methodology changes
- Consider compatibility with research use cases

## License

By contributing, you agree your contributions will be licensed under EUPL-1.2.