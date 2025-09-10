# Contributing to Pygmalion

Thank you for your interest in contributing to Pygmalion! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Okymi-X/pygmalion.git
   cd pygmalion
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests to ensure everything works**
   ```bash
   pytest
   ```

## 🛠️ Development Workflow

### Code Style

We use several tools to maintain code quality:

- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

Run these before submitting:

```bash
black pygmalion tests
flake8 pygmalion tests
mypy pygmalion
```

### Testing

We use pytest for testing. Please ensure:

- All new features have tests
- Tests pass locally before submitting
- Aim for good test coverage

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pygmalion

# Run specific test file
pytest tests/test_tracker.py
```

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add workflow execution functionality
fix: resolve storage race condition in JSONStorage
docs: update README with installation instructions
test: add integration tests for alias system
```

## 🎯 What to Contribute

### High Priority

- **Documentation improvements** - Better examples, API docs
- **Performance optimizations** - Faster command tracking, storage efficiency
- **Storage backends** - Redis, PostgreSQL, MongoDB support
- **CLI integrations** - Better Click/Typer integration, tab completion
- **Analytics features** - More sophisticated usage analysis

### Ideas Welcome

- **Machine learning** - Better pattern recognition, predictive suggestions
- **Export formats** - CSV, Excel, custom format support
- **Visualization** - Command usage graphs, timeline views
- **Plugin system** - Extensible architecture for custom behaviors
- **Multi-user support** - Team analytics, shared aliases

## 📝 Pull Request Process

1. **Fork the repository** and create a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes** following the code style guidelines

3. **Add or update tests** for your changes

4. **Update documentation** if needed

5. **Run the full test suite**
   ```bash
   pytest --cov=pygmalion
   black pygmalion tests
   flake8 pygmalion tests
   mypy pygmalion
   ```

6. **Submit a pull request** with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots/examples if applicable

## 🐛 Reporting Issues

When reporting issues, please include:

- **Python version** and operating system
- **Pygmalion version**
- **Complete error message** and stack trace
- **Minimal example** to reproduce the issue
- **Expected vs actual behavior**

## 💡 Suggesting Features

For feature requests:

- **Search existing issues** to avoid duplicates
- **Describe the problem** you're trying to solve
- **Explain your proposed solution**
- **Consider alternatives** you've thought about
- **Provide use cases** and examples

## 🏗️ Architecture Guidelines

### Core Principles

1. **Modularity** - Keep components loosely coupled
2. **Extensibility** - Design for easy extension and customization
3. **Performance** - Minimize overhead on CLI applications
4. **Privacy** - Never track sensitive data without explicit consent
5. **Reliability** - Graceful degradation when storage fails

### Code Organization

```
pygmalion/
├── core.py          # Main PygmalionApp class
├── tracker.py       # Command tracking and analytics
├── alias.py         # Alias and workflow management
├── help.py          # Adaptive help system
├── storage.py       # Storage backends
├── decorators.py    # Click integration decorators
└── cli.py           # Demo CLI application
```

### Adding New Storage Backends

To add a new storage backend:

1. **Inherit from `StorageBackend`**
2. **Implement all abstract methods**
3. **Add comprehensive tests**
4. **Update documentation**
5. **Consider performance implications**

### Adding New Suggestion Types

To add new suggestion types:

1. **Extend `CommandTracker.suggest_optimizations()`**
2. **Add suggestion handling in `AdaptiveHelp`**
3. **Update help templates**
4. **Add tests for new suggestions**

## 📚 Documentation

### API Documentation

- Use Google-style docstrings
- Include parameter types and descriptions
- Provide usage examples
- Document exceptions that may be raised

### README Updates

- Keep examples current and working
- Update feature lists for new capabilities
- Maintain installation instructions
- Include performance considerations

## 🧪 Testing Guidelines

### Test Structure

- **Unit tests** for individual components
- **Integration tests** for component interactions
- **End-to-end tests** for complete workflows
- **Performance tests** for critical paths

### Test Coverage

Aim for high test coverage, especially for:

- Core functionality (tracking, storage, suggestions)
- Error handling paths
- Edge cases and boundary conditions
- Platform-specific behavior

### Mock Usage

- Mock external dependencies (file system, databases)
- Use real implementations for integration tests
- Avoid over-mocking - test real interactions when possible

## 🚀 Release Process

### Version Numbers

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** - Breaking API changes
- **MINOR** - New features, backwards compatible
- **PATCH** - Bug fixes, backwards compatible

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version bumped
- [ ] GitHub release created
- [ ] PyPI package published

## 🤝 Community

### Communication

- **GitHub Issues** - Bug reports, feature requests
- **GitHub Discussions** - General questions, ideas
- **Pull Requests** - Code contributions, documentation

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- Be respectful and constructive
- Help others learn and grow
- Focus on the code and ideas, not the person
- Acknowledge different perspectives and experiences

## 🎉 Recognition

Contributors are recognized in:

- **README.md** - Major contributors section
- **CHANGELOG.md** - Release notes
- **GitHub releases** - Thank you notes

Thank you for contributing to Pygmalion! 🎭✨
