# Contributing Guide

Thank you for your interest in contributing to Watcher! This guide will help you get started with development and contributing.

## Getting Started

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd watcher
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .
   pip install -r requirements.txt
   ```

4. **Verify installation**:
   ```bash
   watcher --version
   watcher --help
   ```

### Development Environment

#### Required Tools
- Python 3.8 or higher
- Git
- systemd (for Linux integration)
- Text editor or IDE

#### Recommended Tools
- `pytest` for testing
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

#### Install Development Dependencies
```bash
pip install pytest black flake8 mypy
```

## Project Structure

```
watcher/
├── watcher/                 # Main package
│   ├── __init__.py
│   ├── cli.py              # Command line interface
│   ├── core.py             # Core file watching logic
│   ├── config.py           # Configuration management
│   └── ignore.py           # Ignore pattern handling
├── templates/              # Configuration templates
│   ├── config.yaml         # Default config template
│   └── ignore              # Default ignore patterns
├── systemd/                # Systemd service template
│   └── watcher@.service
├── docs/                   # Documentation
├── tests/                  # Test suite
├── setup.py               # Package setup
├── pyproject.toml         # Project configuration
├── requirements.txt       # Dependencies
└── README.md              # Main documentation
```

## Development Workflow

### 1. Making Changes

#### Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

#### Make Your Changes
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed
- Test your changes thoroughly

### 2. Code Style

#### Python Code Style
We follow PEP 8 with some modifications:

- Line length: 120 characters
- Use type hints for function signatures
- Use descriptive variable names
- Add docstrings for classes and functions

#### Example Code Style
```python
def create_config(self, config_name: str, template_data: Optional[Dict[str, Any]] = None) -> Path:
    """
    Create a new config file from template
    
    Args:
        config_name: Name of the config file to create
        template_data: Optional template data to customize the config
        
    Returns:
        Path to the created config file
        
    Raises:
        FileExistsError: If config file already exists
        PermissionError: If unable to write config file
    """
    self.ensure_config_dir()
    config_path = self.get_config_path(config_name)
    
    if config_path.exists():
        raise FileExistsError(f"Config file already exists: {config_path}")
    
    # Implementation continues...
```

#### Formatting
```bash
# Format code with black
black watcher/

# Check style with flake8
flake8 watcher/

# Type checking with mypy
mypy watcher/
```

### 3. Testing

#### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_config.py

# Run with coverage
pytest --cov=watcher
```

#### Writing Tests
- Add tests for new functionality
- Test both success and error cases
- Use descriptive test names
- Mock external dependencies (git, filesystem, systemd)

#### Example Test
```python
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from watcher.config import ConfigManager

def test_create_config_success():
    """Test successful configuration creation"""
    with patch('pathlib.Path.exists') as mock_exists, \
         patch('builtins.open', create=True) as mock_open:
        
        mock_exists.return_value = False
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        config_manager = ConfigManager()
        result = config_manager.create_config("test", {"watch_directory": "/test"})
        
        assert result == config_manager.get_config_path("test")
        mock_open.assert_called_once()

def test_create_config_file_exists():
    """Test configuration creation when file already exists"""
    with patch('pathlib.Path.exists') as mock_exists:
        mock_exists.return_value = True
        
        config_manager = ConfigManager()
        
        with pytest.raises(FileExistsError):
            config_manager.create_config("test")
```

### 4. Documentation

#### Updating Documentation
- Update docstrings for modified functions
- Add new CLI commands to `docs/cli/commands.md`
- Update configuration options in `docs/config/configuration.md`
- Add examples for new features

#### Documentation Style
- Use clear, concise language
- Include code examples
- Provide both basic and advanced usage
- Keep examples up to date

### 5. Committing Changes

#### Commit Message Format
```
type(scope): brief description

Detailed description of the changes made.

- List specific changes
- Reference issue numbers if applicable
- Explain why the change was made

Closes #123
```

#### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### Example Commit Messages
```
feat(cli): add remove command to delete configurations

Add new `watcher remove` command that allows users to delete
configurations and associated files safely.

- Add remove command with --force option
- Implement confirmation prompts for safety
- Clean up systemd services when removing configs
- Update documentation and examples

Closes #45

fix(core): handle git push failures gracefully

Previously, git push failures would crash the watcher service.
Now we log the error and continue monitoring.

- Catch subprocess.CalledProcessError in _push_changes
- Log detailed error information
- Continue operation even if push fails
- Add tests for push failure scenarios

Fixes #67
```

## Types of Contributions

### 1. Bug Fixes

#### Reporting Bugs
Before fixing a bug, check if it's already reported in the issue tracker.

When reporting bugs, include:
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, etc.)
- Relevant logs or error messages
- Configuration files (sanitized)

#### Fixing Bugs
1. Create a test that reproduces the bug
2. Fix the bug
3. Ensure the test passes
4. Update documentation if needed

### 2. New Features

#### Proposing Features
1. Check existing issues and discussions
2. Create an issue describing the feature
3. Discuss the approach with maintainers
4. Implement the feature
5. Add tests and documentation

#### Feature Guidelines
- Features should be generally useful
- Maintain backward compatibility
- Follow existing patterns and conventions
- Include comprehensive tests
- Update documentation

### 3. Documentation

#### Areas for Documentation Contribution
- User guides and tutorials
- API documentation
- Configuration examples
- Troubleshooting guides
- Installation instructions

#### Documentation Standards
- Clear, concise writing
- Up-to-date examples
- Proper formatting and structure
- Cross-platform considerations

### 4. Performance Improvements

#### Performance Guidelines
- Profile before optimizing
- Measure performance impact
- Consider memory usage
- Test with realistic data sizes
- Document performance characteristics

## Specific Areas for Contribution

### 1. CLI Improvements

#### Potential Enhancements
- Better error messages
- Progress indicators for long operations
- Shell completion support
- Color output options
- Interactive configuration setup

### 2. Core Functionality

#### Areas for Enhancement
- Better git conflict handling
- Support for more VCS systems
- Improved ignore pattern performance
- Better handling of large repositories
- Enhanced notification systems

### 3. Configuration Management

#### Improvement Areas
- Configuration validation
- Migration tools for config format changes
- Configuration templates for different project types
- Better error reporting

### 4. Platform Support

#### Platform-Specific Work
- Windows systemd alternative
- macOS launchd integration
- Cross-platform notification support
- Path handling improvements

## Testing Guidelines

### Test Categories

#### Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Test edge cases and error conditions
- Fast execution

#### Integration Tests
- Test component interactions
- Use real git repositories
- Test systemd integration
- Test file system operations

#### End-to-End Tests
- Test complete workflows
- Use real configurations
- Test CLI commands
- Validate actual file watching

### Test Structure

```python
# tests/test_module.py
import pytest
from unittest.mock import patch, MagicMock
from watcher.module import ClassName

class TestClassName:
    """Test suite for ClassName"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.instance = ClassName()
    
    def test_method_success(self):
        """Test successful method execution"""
        # Test implementation
        
    def test_method_error(self):
        """Test method error handling"""
        # Test implementation
        
    @patch('watcher.module.external_dependency')
    def test_method_with_mock(self, mock_dependency):
        """Test method with mocked dependency"""
        # Test implementation
```

### Test Data

#### Configuration Fixtures
```python
# tests/fixtures/configs.py
VALID_CONFIG = {
    'name': 'test',
    'watch_directory': '/tmp/test',
    'repo_directory': '/tmp/test',
    'commit_delay': 60,
    'auto_push': True,
}

INVALID_CONFIG = {
    'name': 'test',
    # Missing required fields
}
```

## Release Process

### Version Management

#### Semantic Versioning
We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Incompatible API changes
- MINOR: New functionality (backward compatible)
- PATCH: Bug fixes (backward compatible)

#### Version Updates
Update version numbers in:
- `setup.py`
- `pyproject.toml`
- `watcher/__init__.py`
- `watcher/cli.py` (version option)

### Release Checklist

1. **Update Version Numbers**
2. **Update CHANGELOG.md**
3. **Run Full Test Suite**
4. **Update Documentation**
5. **Create Release Tag**
6. **Publish Release**

## Getting Help

### Communication Channels
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: General questions and ideas
- Code Review: Pull request discussions

### Code Review Process

#### Submitting Pull Requests
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit pull request with clear description

#### Pull Request Template
```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Criteria

#### Code Quality
- Follows project conventions
- Includes appropriate tests
- Handles errors gracefully
- Performs well

#### Documentation
- Functions have docstrings
- Complex logic is commented
- User-facing changes documented
- Examples are accurate

## Security Considerations

### Security Guidelines
- Never commit secrets or credentials
- Validate all user inputs
- Use secure defaults
- Follow security best practices
- Report security issues privately

### Sensitive Information
- Configuration files may contain sensitive paths
- Log output should not expose secrets
- Git repositories may contain sensitive data
- File permissions should be appropriate

## License

By contributing to Watcher, you agree that your contributions will be licensed under the same license as the project (MIT License).

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Watcher!