# Contributing to fast-django

Thank you for your interest in contributing to fast-django! We welcome contributions from the community and appreciate your help in making this project better.

## 🎯 How to Contribute

There are many ways to contribute to fast-django:

- 🐛 **Bug Reports** - Report issues you encounter
- 💡 **Feature Requests** - Suggest new features or improvements
- 📝 **Documentation** - Improve or add documentation
- 🧪 **Testing** - Add tests or improve test coverage
- 🔧 **Code** - Fix bugs or implement new features
- 📚 **Examples** - Add example applications or tutorials

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- A GitHub account

### Development Setup

1. **Fork the repository**
   ```bash
   # Go to https://github.com/AakarSharma/fast-django and click "Fork"
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/fast-django.git
   cd fast-django
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/AakarSharma/fast-django.git
   ```

4. **Install development dependencies**
   ```bash
   # Install the package in development mode with all dependencies
   pip install -e ".[dev,test,docs]"

   # Install pre-commit hooks
   pre-commit install
   ```

5. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## 🧪 Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/fast_django --cov-report=html

# Run specific test file
pytest tests/test_specific.py

# Run tests with verbose output
pytest -v
```

### Code Quality Checks

```bash
# Run linting
ruff check .

# Auto-fix linting issues
ruff check . --fix

# Check code formatting
ruff format --check .

# Auto-format code
ruff format .

# Run type checking
mypy src

# Run all checks at once
ruff check . && ruff format --check . && mypy src && pytest
```

### Building Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build

# Check for broken links
mkdocs build --strict
```

## 📝 Code Style

We use several tools to maintain code quality:

- **Ruff** - Fast Python linter and formatter
- **MyPy** - Static type checking
- **Pre-commit** - Git hooks for code quality
- **Pytest** - Testing framework

### Code Style Guidelines

1. **Follow PEP 8** - Use ruff to automatically format code
2. **Type Hints** - Add type hints to all functions and methods
3. **Docstrings** - Use Google-style docstrings for public APIs
4. **Tests** - Write tests for new features and bug fixes
5. **Documentation** - Update documentation for user-facing changes

### Pre-commit Hooks

Pre-commit hooks automatically run checks before each commit:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files

# Skip hooks for a commit (not recommended)
git commit --no-verify -m "Your commit message"
```

## 🐛 Reporting Bugs

### Before Reporting

1. Check if the issue already exists in [GitHub Issues](https://github.com/AakarSharma/fast-django/issues)
2. Try the latest version of fast-django
3. Search the [documentation](https://aakarsharma.github.io/fast-django/) for solutions

### Bug Report Template

When creating a bug report, please include:

```markdown
**Bug Description**
A clear and concise description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Environment**
- OS: [e.g. macOS, Linux, Windows]
- Python version: [e.g. 3.11.0]
- fast-django version: [e.g. 0.1.0]
- Database: [e.g. SQLite, PostgreSQL, MySQL]

**Additional Context**
Add any other context about the problem here.
```

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Feature Description**
A clear and concise description of the feature you'd like to see.

**Use Case**
Describe the problem this feature would solve or the use case it would enable.

**Proposed Solution**
A clear description of what you want to happen.

**Alternatives**
Describe any alternative solutions or features you've considered.

**Additional Context**
Add any other context or screenshots about the feature request here.
```

## 🔧 Pull Request Process

### Before Submitting

1. **Update your branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks**
   ```bash
   ruff check . && ruff format --check . && mypy src && pytest
   ```

3. **Update documentation** if needed
4. **Add tests** for new features or bug fixes
5. **Update CHANGELOG.md** if applicable

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] All existing tests pass

## Checklist
- [ ] Code follows the project's style guidelines
- [ ] Self-review of code completed
- [ ] Code is properly commented
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Breaking changes documented
```

### Review Process

1. **Automated Checks** - CI/CD pipeline runs tests and linting
2. **Code Review** - Maintainers review the code
3. **Testing** - Changes are tested in different environments
4. **Approval** - At least one maintainer approval required
5. **Merge** - Changes are merged to main branch

## 📚 Documentation

### Types of Documentation

- **API Documentation** - Docstrings and type hints
- **User Documentation** - Guides and tutorials in `docs/`
- **Code Comments** - Inline comments for complex logic
- **README Updates** - Keep README.md current

### Documentation Guidelines

1. **Use clear, concise language**
2. **Include code examples**
3. **Keep documentation up-to-date with code changes**
4. **Use proper markdown formatting**
5. **Test all code examples**

## 🧪 Testing

### Test Types

- **Unit Tests** - Test individual functions and methods
- **Integration Tests** - Test component interactions
- **End-to-End Tests** - Test complete workflows
- **Performance Tests** - Test performance characteristics

### Writing Tests

```python
import pytest
from fast_django import create_app, Settings

def test_create_app():
    """Test that create_app returns a FastAPI instance."""
    app = create_app()
    assert app is not None
    assert hasattr(app, 'routes')

@pytest.mark.asyncio
async def test_database_operations():
    """Test database operations."""
    # Your test code here
    pass
```

### Test Coverage

We aim for high test coverage. Run coverage reports:

```bash
pytest --cov=src/fast_django --cov-report=html
open htmlcov/index.html  # View coverage report
```

## 🏷️ Release Process

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in `pyproject.toml`
- [ ] Release notes prepared
- [ ] Tag created

## 🤝 Community Guidelines

### Code of Conduct

We follow the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please:

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Communication

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and discussions
- **Pull Requests** - Code changes and reviews
- **Discord/Slack** - Real-time chat (if available)

## 🆘 Getting Help

If you need help:

1. **Check the documentation** - [https://aakarsharma.github.io/fast-django/](https://aakarsharma.github.io/fast-django/)
2. **Search existing issues** - [GitHub Issues](https://github.com/AakarSharma/fast-django/issues)
3. **Ask in discussions** - [GitHub Discussions](https://github.com/AakarSharma/fast-django/discussions)
4. **Create a new issue** - If you can't find an answer

## 🙏 Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md** - List of all contributors
- **Release notes** - Major contributors mentioned
- **GitHub contributors** - Automatic recognition on GitHub

## 📄 License

By contributing to fast-django, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to fast-django! 🎉
