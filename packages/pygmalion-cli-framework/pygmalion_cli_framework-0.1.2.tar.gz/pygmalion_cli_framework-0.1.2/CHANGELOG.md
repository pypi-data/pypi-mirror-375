# Changelog

All notable changes to Pygmalion will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of Pygmalion adaptive CLI framework
- Core command tracking and analytics
- Intelligent alias suggestion system
- Multi-command workflow builder
- Adaptive help system with personalized recommendations
- JSON and SQLite storage backends
- Rich CLI demo application
- Comprehensive test suite

### Features
- **Command Tracking**: Automatic logging of command usage with timestamps and arguments
- **Smart Suggestions**: AI-driven recommendations for aliases and workflows based on usage patterns
- **Adaptive Help**: Personalized help messages showing most-used commands first
- **Alias Management**: Create and manage command shortcuts with automatic name suggestions
- **Workflow Builder**: Chain commands together into reusable workflows
- **Analytics Dashboard**: Usage statistics, patterns, and optimization recommendations
- **Data Export**: Export usage data to JSON or CSV formats
- **Click Integration**: Drop-in decorators for existing Click applications
- **Storage Options**: Flexible storage with JSON (default) or SQLite backends

## [0.1.0] - 2025-01-09

### Added
- Initial project structure and core architecture
- `PygmalionApp` main application class
- `CommandTracker` for usage analytics
- `AliasManager` for shortcuts and workflows
- `AdaptiveHelp` for intelligent help generation
- `StorageBackend` abstraction with JSON and SQLite implementations
- Click integration decorators (`@pygmalion.command`, `@pygmalion.group`)
- Demo CLI application showcasing all features
- Comprehensive test suite with >90% coverage
- Documentation and contribution guidelines

### Technical Details
- Python 3.9+ support
- Click framework integration
- Rich terminal output
- Atomic file operations for data safety
- Type hints throughout codebase
- Pytest-based testing
- Black code formatting
- Flake8 linting
- MyPy type checking

### Documentation
- Comprehensive README with examples
- API documentation with docstrings
- Contributing guidelines
- MIT license

---

## Release Notes Template

### [Version] - YYYY-MM-DD

#### Added
- New features and capabilities

#### Changed
- Changes to existing functionality

#### Deprecated
- Features that will be removed in future versions

#### Removed
- Features removed in this version

#### Fixed
- Bug fixes and corrections

#### Security
- Security-related improvements
