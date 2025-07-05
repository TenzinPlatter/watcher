# API Reference

Internal API documentation for developers working on the watcher codebase.

## Module Overview

### Core Modules

- `watcher.cli` - Command line interface
- `watcher.core` - Main file watching and git operations
- `watcher.config` - Configuration management
- `watcher.ignore` - Ignore pattern handling

## CLI Module (`watcher.cli`)

### Main Functions

#### `main()`
Entry point for the CLI application.

```python
@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Watcher - Multi-directory file watcher with automated git commits"""
```

#### `init(config_name, watch_dir, repo_dir, commit_delay)`
Initialize a new watcher configuration.

```python
@main.command()
@click.argument('config_name', default='config')
@click.option('--watch-dir', '-w', help='Directory to watch')
@click.option('--repo-dir', '-r', help='Git repository directory')
@click.option('--commit-delay', '-d', type=int, help='Commit delay in seconds')
def init(config_name: str, watch_dir: Optional[str], repo_dir: Optional[str], commit_delay: Optional[int]) -> None
```

**Parameters:**
- `config_name` - Name of the configuration
- `watch_dir` - Directory to watch for changes
- `repo_dir` - Git repository directory
- `commit_delay` - Delay in seconds before committing

**Returns:** None

**Side Effects:**
- Creates configuration file
- Installs systemd service template
- Creates global ignore file if needed

#### `up(config_name)`
Start watcher service for a configuration.

```python
@main.command()
@click.argument('config_name', default='config')
def up(config_name: str) -> None
```

#### `down(config_name)`
Stop watcher service for a configuration.

```python
@main.command()
@click.argument('config_name', default='config')
def down(config_name: str) -> None
```

#### `run(config_name)`
Run watcher directly (used by systemd service).

```python
@main.command()
@click.argument('config_name')
def run(config_name: str) -> None
```

### Utility Functions

#### `_install_systemd_service()`
Install systemd service template.

```python
def _install_systemd_service() -> None
```

#### `_get_editor()`
Get the preferred editor for editing configuration files.

```python
def _get_editor() -> str
```

**Returns:** Path to editor executable

## Core Module (`watcher.core`)

### Main Classes

#### `GitCommitHandler`
Main event handler for file system events and git operations.

```python
class GitCommitHandler(FileSystemEventHandler):
    def __init__(self, config_name: str) -> None:
        self.config_name: str = config_name
        self.config_manager: ConfigManager = ConfigManager()
        self.config: Dict[str, Any] = self.config_manager.load_config(config_name)
        self.watch_dir: Path = Path(self.config['watch_directory']).expanduser().resolve()
        self.repo_dir: Path = Path(self.config['repo_directory']).expanduser().resolve()
        self.ignore_manager: IgnoreManager = IgnoreManager(config_name, self.config)
        self.submodules: List[Path] = self._get_submodules()
        self.pending_commits: Dict[str, Set[str]] = {}
        self.commit_timers: Dict[str, threading.Timer] = {}
        self.timer_lock: threading.Lock = threading.Lock()
        self.fetch_timer: Optional[threading.Timer] = None
```

**Attributes:**
- `config_name` - Name of the configuration
- `config_manager` - Configuration manager instance
- `config` - Loaded configuration data
- `watch_dir` - Directory being watched
- `repo_dir` - Git repository directory
- `ignore_manager` - Ignore pattern manager
- `submodules` - List of git submodules
- `pending_commits` - Files pending commit per directory
- `commit_timers` - Active commit timers per directory
- `timer_lock` - Thread lock for timer operations
- `fetch_timer` - Timer for periodic fetching

### Key Methods

#### File System Event Handlers

```python
def on_modified(self, event: FileSystemEvent) -> None:
    """Handle file modification events"""

def on_created(self, event: FileSystemEvent) -> None:
    """Handle file creation events"""

def on_deleted(self, event: FileSystemEvent) -> None:
    """Handle file deletion events"""

def on_moved(self, event: FileSystemEvent) -> None:
    """Handle file move events"""
```

#### Git Operations

```python
def _run_git_command(self, cmd: List[str], cwd: Union[str, Path], description: str = "Git command") -> subprocess.CompletedProcess[str]:
    """Run a git command with proper error logging"""

def _commit_squashed_main_repo(self, repo_dir: Path, changed_files: Set[str]) -> None:
    """Create a squashed commit for main repository changes"""

def _commit_squashed_submodule(self, submodule_dir: Path, changed_files: Set[str]) -> None:
    """Create a squashed commit for submodule changes"""

def _push_changes(self, repo_dir: Path, repo_name: str) -> None:
    """Push changes to remote repository"""
```

#### Timer Management

```python
def _handle_file_change(self, file_path: str, change_type: str) -> None:
    """Handle a file change event"""

def _execute_delayed_commit(self, dir_key: str) -> None:
    """Execute a delayed commit for a directory"""

def start_fetch_timer(self) -> None:
    """Start the periodic fetch timer"""
```

#### Utility Methods

```python
def _get_submodules(self) -> List[Path]:
    """Get list of submodule paths"""

def _should_exclude_file(self, file_path: str) -> bool:
    """Check if file should be excluded from monitoring"""

def _create_squashed_commit_message(self, repo_dir: Path, changed_files: Set[str]) -> str:
    """Create a commit message based on actual git status"""
```

### Main Function

#### `run_watcher(config_name)`
Main function to run the file watcher.

```python
def run_watcher(config_name: str) -> None:
    """
    Run the file watcher for a specific configuration
    
    Args:
        config_name: Name of the configuration to use
    """
```

## Configuration Module (`watcher.config`)

### Main Class

#### `ConfigManager`
Manages watcher configurations.

```python
class ConfigManager:
    def __init__(self) -> None:
        self.config_dir: Path = Path.home() / '.config' / 'watcher'
        self.templates_dir: Path = Path(__file__).parent.parent / 'templates'
```

**Attributes:**
- `config_dir` - Configuration directory path
- `templates_dir` - Templates directory path

### Configuration Methods

```python
def load_config(self, config_name: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file with fallback to defaults
    
    Args:
        config_name: Name of the config file (without .yaml extension)
        
    Returns:
        Dictionary containing configuration data
    """

def create_config(self, config_name: str, template_data: Optional[Dict[str, Any]] = None) -> Path:
    """
    Create a new config file from template
    
    Args:
        config_name: Name of the config file to create
        template_data: Optional template data to customize the config
        
    Returns:
        Path to the created config file
    """

def validate_config(self, config_name: str) -> Dict[str, Any]:
    """
    Validate a configuration and return validation results
    
    Args:
        config_name: Name of the config to validate
        
    Returns:
        Dictionary with validation results
    """
```

### Utility Methods

```python
def ensure_config_dir(self) -> None:
    """Ensure the config directory exists"""

def get_config_path(self, config_name: str) -> Path:
    """Get the path to a specific config file"""

def get_global_ignore_path(self) -> Path:
    """Get the path to the global ignore file"""

def list_configs(self) -> List[str]:
    """List all available config files"""

def config_exists(self, config_name: str) -> bool:
    """Check if a config file exists"""

def ensure_global_ignore(self) -> Path:
    """Ensure the global ignore file exists"""

def get_config_status(self, config_name: str) -> Dict[str, Any]:
    """Get status information for a config"""
```

## Ignore Module (`watcher.ignore`)

### Main Class

#### `IgnoreManager`
Manages hierarchical ignore patterns.

```python
class IgnoreManager:
    def __init__(self, config_name: str, config_data: Dict[str, Any]) -> None:
        self.config_name: str = config_name
        self.config_data: Dict[str, Any] = config_data
        self.watch_dir: Path = Path(config_data['watch_directory']).expanduser().resolve()
        self.global_patterns: List[str] = self._load_global_ignore()
        self.config_patterns: List[str] = self._load_config_ignore()
        self.additional_patterns: List[str] = self._load_additional_ignore_files()
        self.gitignore_patterns: Dict[str, List[str]] = {}
        self.all_patterns: List[str] = self.global_patterns + self.config_patterns + self.additional_patterns
```

**Attributes:**
- `config_name` - Configuration name
- `config_data` - Configuration data
- `watch_dir` - Directory being watched
- `global_patterns` - Patterns from global ignore file
- `config_patterns` - Patterns from config file
- `additional_patterns` - Patterns from additional ignore files
- `gitignore_patterns` - Patterns from gitignore files
- `all_patterns` - Combined patterns for efficient matching

### Core Methods

```python
def should_ignore(self, file_path: str) -> bool:
    """
    Check if a file should be ignored based on all ignore sources
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file should be ignored, False otherwise
    """

def test_pattern(self, file_path: str) -> Dict[str, Any]:
    """Test which ignore sources would match a file (for debugging)"""

def get_all_patterns(self) -> Dict[str, Any]:
    """Get all loaded patterns for debugging"""
```

### Pattern Loading Methods

```python
def _load_global_ignore(self) -> List[str]:
    """Load patterns from global ignore file"""

def _load_config_ignore(self) -> List[str]:
    """Load patterns from config's ignore_patterns"""

def _load_additional_ignore_files(self) -> List[str]:
    """Load patterns from config's ignore_files"""

def _load_ignore_file(self, ignore_path: Path) -> List[str]:
    """Load patterns from a single ignore file"""
```

### Pattern Matching Methods

```python
def _matches_pattern(self, file_path: str, pattern: str) -> bool:
    """Check if a file path matches a single ignore pattern"""

def _matches_gitignore(self, file_path: Path) -> bool:
    """Check if file matches any gitignore patterns"""
```

## Data Structures

### Configuration Schema

```python
ConfigData = Dict[str, Any]  # Configuration dictionary

# Required fields:
{
    'name': str,                    # Configuration name
    'watch_directory': str,         # Directory to watch
    'repo_directory': str,          # Git repository directory
}

# Optional fields with defaults:
{
    'commit_delay': int,            # Default: 60
    'fetch_interval': int,          # Default: 600
    'enable_notifications': bool,   # Default: True
    'notify_on_commit': bool,       # Default: True
    'notify_on_remote_changes': bool, # Default: True
    'auto_push': bool,              # Default: True
    'respect_gitignore': bool,      # Default: True
    'ignore_patterns': List[str],   # Default: []
    'ignore_files': List[str],      # Default: []
}
```

### Validation Results

```python
ValidationResult = Dict[str, Any]
{
    'valid': bool,                  # Overall validity
    'errors': List[str],           # Error messages
    'warnings': List[str],         # Warning messages
}
```

### Status Information

```python
StatusInfo = Dict[str, Any]
{
    'name': str,                   # Configuration name
    'exists': bool,                # Configuration file exists
    'service_active': bool,        # Systemd service is active
    'service_enabled': bool,       # Systemd service is enabled
    'watch_directory': Optional[str], # Watch directory path
    'repo_directory': Optional[str],  # Repository directory path
}
```

## Error Handling

### Exception Types

The watcher uses standard Python exceptions:

- `FileNotFoundError` - Configuration or directory not found
- `subprocess.CalledProcessError` - Git command failures
- `yaml.YAMLError` - Configuration file parsing errors
- `KeyboardInterrupt` - User interruption

### Error Patterns

#### Configuration Errors
```python
# Configuration doesn't exist
if not config_manager.config_exists(config_name):
    click.echo(f"❌ Config '{config_name}' does not exist. Run 'watcher init {config_name}' first.")
    sys.exit(1)

# Configuration validation errors
validation = config_manager.validate_config(config_name)
if not validation['valid']:
    for error in validation['errors']:
        click.echo(f"❌ Config error: {error}")
    sys.exit(1)
```

#### Git Command Errors
```python
def _run_git_command(self, cmd: List[str], cwd: Union[str, Path], description: str = "Git command") -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            # Log detailed error information
            print(f"❌ {description} failed: {' '.join(cmd)}")
            print(f"   Return code: {result.returncode}")
            if result.stderr.strip():
                print(f"   STDERR: {result.stderr.strip()}")
        return result
    except Exception as e:
        print(f"❌ {description} unexpected error: {e}")
        raise
```

## Extension Points

### Adding New CLI Commands

1. Define command function with Click decorators:
```python
@main.command()
@click.argument('arg_name')
@click.option('--option-name', help='Description')
def new_command(arg_name: str, option_name: Optional[str]) -> None:
    """Command description"""
    # Implementation
```

2. Add command to documentation in `docs/cli/commands.md`

### Adding New Configuration Options

1. Add option to default configuration in `ConfigManager.load_config()`:
```python
default_config = {
    # ... existing options ...
    'new_option': default_value,
}
```

2. Add validation in `ConfigManager.validate_config()`:
```python
if config.get('new_option') < 0:
    results['errors'].append("new_option must be non-negative")
```

3. Use option in `GitCommitHandler`:
```python
def __init__(self, config_name: str) -> None:
    # ... existing initialization ...
    self.new_option = self.config['new_option']
```

### Adding New Ignore Pattern Sources

1. Add pattern loading method to `IgnoreManager`:
```python
def _load_new_source(self) -> List[str]:
    """Load patterns from new source"""
    # Implementation
    return patterns
```

2. Add patterns to combined list in `__init__()`:
```python
self.new_patterns: List[str] = self._load_new_source()
self.all_patterns: List[str] = (
    self.global_patterns + 
    self.config_patterns + 
    self.additional_patterns +
    self.new_patterns
)
```

3. Update `test_pattern()` to include new source in debug output

## Testing

### Unit Testing Structure

Tests should be organized by module:
```
tests/
├── test_cli.py          # CLI command tests
├── test_core.py         # Core functionality tests
├── test_config.py       # Configuration management tests
├── test_ignore.py       # Ignore pattern tests
└── fixtures/            # Test data and configurations
```

### Mock Patterns

#### Mocking Git Commands
```python
from unittest.mock import patch, MagicMock

@patch('watcher.core.subprocess.run')
def test_git_command(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="output", stderr="")
    # Test implementation
```

#### Mocking File System
```python
from unittest.mock import patch
from pathlib import Path

@patch('pathlib.Path.exists')
@patch('pathlib.Path.is_dir')
def test_directory_validation(mock_is_dir, mock_exists):
    mock_exists.return_value = True
    mock_is_dir.return_value = True
    # Test implementation
```

### Integration Testing

Integration tests should cover:
- Full watcher workflow with real git repositories
- Systemd service integration
- Configuration file operations
- Multi-project scenarios

## Performance Considerations

### File Watching Optimization

- Use efficient ignore patterns to reduce monitored files
- Implement proper cleanup of timers and resources
- Monitor memory usage with large file trees

### Git Operation Optimization

- Batch multiple file changes into single commits
- Use `--porcelain` flags for consistent git output
- Handle large repositories gracefully

### Threading Considerations

- Use locks for shared timer state
- Ensure proper cleanup on shutdown
- Handle threading exceptions gracefully