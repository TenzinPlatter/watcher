# Configuration Reference

Complete reference for watcher configuration files.

## Configuration File Location

Configuration files are stored in `~/.config/watcher/` and use YAML format:
```
~/.config/watcher/
├── config.yaml          # Default configuration
├── myproject.yaml       # Project-specific configuration
├── work-api.yaml        # Another project configuration
└── ignore               # Global ignore file
```

## Configuration Structure

### Basic Configuration

```yaml
# Basic required settings
name: "myproject"
watch_directory: "~/projects/myapp"
repo_directory: "~/projects/myapp"
```

### Complete Configuration Example

```yaml
# ~/.config/watcher/myproject.yaml

# Basic Settings
name: "myproject"                    # Configuration name
watch_directory: "~/projects/myapp"  # Directory to monitor
repo_directory: "~/projects/myapp"   # Git repository directory

# Timing Settings (in seconds)
commit_delay: 60                     # Wait time before committing
fetch_interval: 600                  # Interval between remote fetches

# Notification Settings
enable_notifications: true           # Enable desktop notifications
notify_on_commit: true              # Notify when commits are made
notify_on_remote_changes: true      # Notify when remote changes detected

# Git Settings
auto_push: true                     # Automatically push commits
respect_gitignore: true             # Follow .gitignore patterns

# Ignore Patterns
ignore_patterns:                    # Project-specific ignore patterns
  - "*.log"
  - "build/"
  - "dist/"
  - ".env.local"

ignore_files:                       # Additional ignore files to read
  - "~/.config/watcher/nodejs-ignore"
  - ".watcher-ignore"
```

## Configuration Options

### Required Settings

#### `name`
- **Type**: String
- **Description**: Name of the configuration
- **Example**: `"myproject"`
- **Notes**: Used for systemd service name and identification

#### `watch_directory`
- **Type**: String (path)
- **Description**: Directory to monitor for changes
- **Example**: `"~/projects/myapp"`
- **Notes**: Supports `~` expansion, must exist

#### `repo_directory`
- **Type**: String (path)
- **Description**: Git repository directory for commits
- **Example**: `"~/projects/myapp"`
- **Notes**: Must be a valid git repository, supports `~` expansion

### Timing Settings

#### `commit_delay`
- **Type**: Integer
- **Default**: `60`
- **Description**: Seconds to wait after last change before committing
- **Range**: `0` to `3600` (1 hour)
- **Examples**:
  - `30` - Quick commits for active development
  - `300` - 5 minutes for less frequent commits
  - `1800` - 30 minutes for large projects

#### `fetch_interval`
- **Type**: Integer
- **Default**: `600`
- **Description**: Seconds between remote repository fetches
- **Range**: `60` to `86400` (24 hours)
- **Examples**:
  - `300` - 5 minutes for active collaboration
  - `1800` - 30 minutes for normal projects
  - `7200` - 2 hours for personal projects

### Notification Settings

#### `enable_notifications`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Master switch for all notifications
- **Examples**:
  - `true` - Enable all notifications
  - `false` - Disable all notifications

#### `notify_on_commit`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Send notification when commits are made
- **Notes**: Requires `enable_notifications: true`

#### `notify_on_remote_changes`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Send notification when remote changes are detected
- **Notes**: Requires `enable_notifications: true`

### Git Settings

#### `auto_push`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Automatically push commits to remote repository
- **Examples**:
  - `true` - Push immediately after commit
  - `false` - Manual push required

#### `respect_gitignore`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Follow .gitignore patterns in addition to watcher ignore patterns
- **Examples**:
  - `true` - Honor .gitignore files
  - `false` - Only use watcher ignore patterns

### Ignore Settings

#### `ignore_patterns`
- **Type**: Array of strings
- **Default**: `[]`
- **Description**: Project-specific ignore patterns using gitignore syntax
- **Examples**:
  ```yaml
  ignore_patterns:
    - "*.log"           # Ignore all log files
    - "build/"          # Ignore build directory
    - "dist/"           # Ignore dist directory
    - ".env.local"      # Ignore local environment file
    - "temp_*"          # Ignore files starting with temp_
  ```

#### `ignore_files`
- **Type**: Array of strings (paths)
- **Default**: `[]`
- **Description**: Additional ignore files to read and apply
- **Examples**:
  ```yaml
  ignore_files:
    - "~/.config/watcher/nodejs-ignore"     # Language-specific ignore
    - ".watcher-ignore"                     # Project-local ignore
    - "~/shared/common-ignore"              # Shared ignore file
  ```

## Configuration Templates

### Dotfiles Configuration

```yaml
name: "dotfiles"
watch_directory: "~/.dotfiles"
repo_directory: "~/.dotfiles"
commit_delay: 300          # 5 minutes - less frequent
fetch_interval: 1800       # 30 minutes
enable_notifications: true
notify_on_commit: true
auto_push: true

ignore_patterns:
  - ".DS_Store"
  - "*.swp"
  - ".vscode/"
  - "*.tmp"
```

### Node.js Project Configuration

```yaml
name: "nodejs-app"
watch_directory: "~/projects/my-node-app"
repo_directory: "~/projects/my-node-app"
commit_delay: 60           # 1 minute
fetch_interval: 300        # 5 minutes
enable_notifications: true
notify_on_commit: true
auto_push: false           # Manual push for review

ignore_patterns:
  - "dist/"
  - "build/"
  - "coverage/"
  - "*.log"
  - ".env.local"

ignore_files:
  - "~/.config/watcher/nodejs-ignore"
```

### Python Project Configuration

```yaml
name: "python-project"
watch_directory: "~/projects/my-python-app"
repo_directory: "~/projects/my-python-app"
commit_delay: 90           # 1.5 minutes
fetch_interval: 600        # 10 minutes
enable_notifications: true
notify_on_commit: true
auto_push: true

ignore_patterns:
  - "*.pyc"
  - "__pycache__/"
  - "build/"
  - "dist/"
  - "*.egg-info/"
  - ".pytest_cache/"
  - ".coverage"
  - "htmlcov/"

ignore_files:
  - "~/.config/watcher/python-ignore"
```

### Work Project Configuration

```yaml
name: "work-api"
watch_directory: "~/work/api-server"
repo_directory: "~/work/api-server"
commit_delay: 30           # Quick commits
fetch_interval: 300        # Frequent fetches
enable_notifications: true
notify_on_commit: true
notify_on_remote_changes: true
auto_push: false           # Manual push for work

ignore_patterns:
  - "logs/"
  - "*.log"
  - "tmp/"
  - ".env.local"
  - "coverage/"
  - "dist/"
  - "build/"
```

### Personal Project Configuration

```yaml
name: "personal-blog"
watch_directory: "~/projects/blog"
repo_directory: "~/projects/blog"
commit_delay: 120          # 2 minutes
fetch_interval: 600        # 10 minutes
enable_notifications: false # Quiet
notify_on_commit: false
notify_on_remote_changes: false
auto_push: true

ignore_patterns:
  - "_site/"
  - ".jekyll-cache/"
  - "*.draft"
  - ".sass-cache/"
```

## Configuration Validation

### Automatic Validation

Watcher automatically validates configurations when:
- Starting a service (`watcher up`)
- Checking status (`watcher status`)
- Running directly (`watcher run`)

### Manual Validation

```bash
# Check configuration validity
watcher status myproject

# Test ignore patterns
watcher test-ignore path/to/file.txt myproject
```

### Common Validation Errors

1. **Directory doesn't exist**:
   ```
   ❌ Watch directory does not exist: /path/to/directory
   ```

2. **Not a git repository**:
   ```
   ❌ Repository directory is not a git repository: /path/to/repo
   ```

3. **Invalid timing values**:
   ```
   ❌ commit_delay must be non-negative
   ```

4. **Missing ignore files**:
   ```
   ⚠️ Ignore file does not exist: /path/to/ignore-file
   ```

## Configuration Management

### Creating Configurations

```bash
# Create with defaults
watcher init myproject

# Create with custom settings
watcher init myproject --watch-dir ~/projects/app --commit-delay 30
```

### Editing Configurations

```bash
# Edit specific configuration
watcher edit-config myproject

# Edit global ignore file
watcher edit-ignore
```

### Removing Configurations

```bash
# Remove configuration (with confirmation)
watcher remove myproject

# Remove without confirmation
watcher remove myproject --force
```

### Copying Configurations

```bash
# Copy existing configuration
cp ~/.config/watcher/myproject.yaml ~/.config/watcher/newproject.yaml

# Edit the copy
watcher edit-config newproject
```

## Environment Variables

Configuration files support environment variable expansion:

```yaml
# Use environment variables
watch_directory: "${HOME}/projects/myapp"
repo_directory: "${PROJECT_ROOT}/repo"

# With defaults
watch_directory: "${PROJECTS_DIR:-~/projects}/myapp"
```

## Advanced Configuration

### Submodule Support

Watcher automatically detects and handles git submodules:

```yaml
# No special configuration needed
name: "main-with-submodules"
watch_directory: "~/projects/main-repo"
repo_directory: "~/projects/main-repo"
# Submodules will be handled automatically
```

### Multiple Watch Directories

To watch multiple directories, create separate configurations:

```yaml
# Config 1: Frontend
name: "frontend"
watch_directory: "~/projects/myapp/frontend"
repo_directory: "~/projects/myapp"

# Config 2: Backend  
name: "backend"
watch_directory: "~/projects/myapp/backend"
repo_directory: "~/projects/myapp"
```

### Symbolic Links

Watcher follows symbolic links by default:

```yaml
# Watching symlinked directory
watch_directory: "~/current-project"  # Symlink to actual project
repo_directory: "~/current-project"
```

## Best Practices

### 1. Use Descriptive Names
```yaml
# Good
name: "work-api-server"
name: "personal-blog"
name: "dotfiles"

# Avoid
name: "config"
name: "project1"
name: "temp"
```

### 2. Set Appropriate Timing
```yaml
# Active development
commit_delay: 30

# Configuration files
commit_delay: 300

# Large projects
commit_delay: 120
```

### 3. Configure Notifications Thoughtfully
```yaml
# Important projects
enable_notifications: true
notify_on_commit: true
notify_on_remote_changes: true

# Background projects
enable_notifications: false
```

### 4. Use Language-Specific Ignore Files
```yaml
# Node.js projects
ignore_files:
  - "~/.config/watcher/nodejs-ignore"

# Python projects
ignore_files:
  - "~/.config/watcher/python-ignore"
```

### 5. Document Your Configurations
```yaml
# Add comments to explain project-specific settings
name: "work-api"
# Fast commits for active development
commit_delay: 30
# No auto-push for work projects requiring review
auto_push: false
```