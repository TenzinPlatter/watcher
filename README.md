# Watcher

Multi-directory file watcher with automated git commits. Monitor multiple git repositories simultaneously and automatically commit and push changes with intelligent squashing and comprehensive ignore patterns.

## Features

- **Multi-directory support**: Watch multiple git repositories simultaneously
- **Intelligent commit squashing**: Combines multiple file changes into single commits
- **Hierarchical ignore patterns**: Global ignore file + project-specific patterns
- **Systemd integration**: Easy service management with systemctl
- **Desktop notifications**: Get notified of commits and remote changes
- **Submodule support**: Handles git submodules correctly
- **Configurable timing**: Customizable commit delays and fetch intervals
- **CLI management**: Simple commands for service control

## Quick Start

```bash
# Install in development mode
pip install -e .

# Initialize default configuration
watcher init

# Start watching your dotfiles
watcher up

# View logs
watcher logs

# Stop watching
watcher down
```

## Installation

### Development Installation

```bash
git clone <repo>
cd watcher
pip install -e .
```

### Dependencies

The package requires:
- Python 3.8+
- `watchdog` for file monitoring
- `PyYAML` for configuration
- `click` for CLI interface
- `systemd` for service management
- `git` for version control operations

## Configuration

### Directory Structure

```
~/.config/watcher/
├── ignore                 # Global ignore file
├── config.yaml           # Default configuration
├── project1.yaml         # Project-specific config
└── work.yaml             # Another project config
```

### Configuration Files

Each configuration file defines a separate watcher instance:

```yaml
# ~/.config/watcher/config.yaml
name: "dotfiles"
watch_directory: "~/.dotfiles"
repo_directory: "~/.dotfiles"
commit_delay: 60
fetch_interval: 600
enable_notifications: true
notify_on_commit: true
auto_push: true

# Project-specific ignore patterns (optional)
ignore_patterns:
  - "*.log"
  - "build/"

# Additional ignore files (optional)
ignore_files:
  - "~/.config/watcher/nodejs-ignore"
  - ".watcher-ignore"
```

### Global Ignore File

The global ignore file (`~/.config/watcher/ignore`) uses gitignore syntax and applies to all watcher instances:

```
# Git internals
.git/
*.swp
*.tmp
__pycache__/
node_modules/
```

## CLI Commands

### Basic Commands

```bash
# Initialize new configuration
watcher init [config_name]

# Start watcher service
watcher up [config_name]

# Stop watcher service  
watcher down [config_name]

# View logs (follow with -f)
watcher logs [config_name] [-f]

# Check service status
watcher status [config_name]

# List all configurations
watcher list
```

### Configuration Management

```bash
# Edit configuration file
watcher edit-config [config_name]

# Edit global ignore file
watcher edit-ignore

# Test ignore patterns
watcher test-ignore <file_path> [config_name]
```

### Advanced Usage

```bash
# Initialize with custom settings
watcher init myproject --watch-dir ~/projects/myapp --commit-delay 30

# View logs for last 100 lines
watcher logs myproject -n 100

# Follow logs in real-time
watcher logs myproject -f
```

## Multiple Project Setup

You can watch multiple directories simultaneously:

```bash
# Set up dotfiles watcher
watcher init dotfiles --watch-dir ~/.dotfiles

# Set up project watcher
watcher init myproject --watch-dir ~/projects/myapp

# Set up work watcher
watcher init work --watch-dir ~/work/repo

# Start all watchers
watcher up dotfiles
watcher up myproject  
watcher up work

# Check status of all
watcher list
```

## Ignore Patterns

### Hierarchy

1. **Global ignore** (`~/.config/watcher/ignore`) - applies to all watchers
2. **Config ignore patterns** - project-specific patterns in YAML config
3. **Additional ignore files** - referenced in config's `ignore_files`
4. **Gitignore files** - project's `.gitignore` files (if `respect_gitignore: true`)

### Example Setup

```yaml
# ~/.config/watcher/nodejs.yaml
name: "nodejs-app"
watch_directory: "~/projects/my-node-app"
ignore_patterns:
  - "dist/"
  - "*.log"
ignore_files:
  - "~/.config/watcher/nodejs-ignore"
```

```
# ~/.config/watcher/nodejs-ignore
node_modules/
npm-debug.log*
.npm
.eslintcache
```

## Systemd Integration

Each configuration runs as a separate systemd user service:

```bash
# Manual systemd operations
systemctl --user status watcher@config.service
systemctl --user enable watcher@myproject.service
systemctl --user restart watcher@work.service

# View logs directly
journalctl --user -u watcher@config.service -f
```

## Git Operations

### Commit Behavior

- **Delay**: Waits for configurable delay (default 60s) after last change
- **Squashing**: Combines multiple file changes into single commit
- **Messages**: Descriptive messages based on actual git status
- **Submodules**: Commits to submodule first, then updates reference in main repo
- **Auto-push**: Optionally pushes commits immediately (configurable)

### Fetch and Notifications

- **Periodic fetch**: Checks for remote changes every 10 minutes (configurable)
- **Notifications**: Desktop notifications for commits and remote changes
- **Branch tracking**: Works with current branch, doesn't change branches

## Configuration Options

### Timing Settings

```yaml
commit_delay: 60        # Seconds to wait before committing
fetch_interval: 600     # Seconds between remote fetches
```

### Notification Settings

```yaml
enable_notifications: true
notify_on_commit: true           # Notify on local commits
notify_on_remote_changes: true   # Notify on remote changes
```

### Git Settings

```yaml
auto_push: true         # Push commits automatically
respect_gitignore: true # Follow .gitignore files
```

## Troubleshooting

### Common Issues

**Service won't start:**
```bash
# Check configuration
watcher status config

# View detailed logs
watcher logs config

# Validate configuration
watcher test-ignore some/file.txt config
```

**Push fails:**
```bash
# Check git remote configuration
git remote -v

# Set up tracking branch
git push -u origin main
```

**Files not being ignored:**
```bash
# Test ignore patterns
watcher test-ignore path/to/file.txt config

# Edit ignore files
watcher edit-ignore
watcher edit-config config
```

### Debug Information

```bash
# Service status
systemctl --user status watcher@config.service

# System logs
journalctl --user -u watcher@config.service --since "1 hour ago"

# Configuration validation
watcher status config
```

## Development

### Running from Source

```bash
# Install in development mode
pip install -e .

# Run directly
python -m watcher.cli --help

# Run watcher directly
python -m watcher.core config
```

### Project Structure

```
watcher/
├── watcher/
│   ├── __init__.py
│   ├── cli.py          # Command line interface
│   ├── config.py       # Configuration management
│   ├── core.py         # File watcher logic
│   └── ignore.py       # Ignore pattern handling
├── templates/
│   ├── config.yaml     # Default config template
│   └── ignore          # Default ignore template
├── systemd/
│   └── watcher@.service # Systemd service template
├── setup.py
├── pyproject.toml
└── README.md
```

## License

MIT License - see LICENSE file for details.
