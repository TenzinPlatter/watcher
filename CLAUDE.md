# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Python file watcher application that monitors git repositories for changes and automatically commits them. The application uses systemd services to manage multiple watcher instances, each with their own configuration.

## Development Commands

### Installation
```bash
# Install in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

### Testing/Running
```bash
# Run watcher directly for testing
python -m watcher.core config_name

# Run CLI interface
python -m watcher.cli --help

# Test specific watcher instance
watcher run config_name
```

### Common Operations
```bash
# Initialize and start a watcher
watcher init myproject --watch-dir ~/projects/myapp
watcher up myproject

# View logs
watcher logs myproject -f

# Stop watcher
watcher down myproject

# Test ignore patterns
watcher test-ignore path/to/file.txt myproject
```

## Architecture

### Core Components

1. **CLI Interface** (`watcher/cli.py`): Click-based command line interface that manages systemd services and configurations
2. **Core Watcher** (`watcher/core.py`): Main file monitoring logic using watchdog library with intelligent git commit handling
3. **Configuration Management** (`watcher/config.py`): Handles multiple YAML configuration files with validation
4. **Ignore Pattern Management** (`watcher/ignore.py`): Hierarchical ignore pattern system supporting global, config-specific, and gitignore patterns

### Key Architecture Patterns

- **Multi-instance Design**: Each configuration creates a separate systemd service (watcher@{config_name}.service)
- **Hierarchical Ignore System**: Global ignore → config patterns → additional files → gitignore files
- **Intelligent Commit Squashing**: Uses timers to batch file changes into single commits with descriptive messages
- **Submodule Support**: Handles git submodules by committing to submodule first, then updating reference in main repo

### File Structure
```
watcher/
├── watcher/
│   ├── cli.py          # Command line interface
│   ├── core.py         # File watcher and git operations
│   ├── config.py       # Configuration management
│   └── ignore.py       # Ignore pattern handling
├── templates/
│   ├── config.yaml     # Default configuration template
│   └── ignore          # Global ignore patterns
├── systemd/
│   └── watcher@.service # Systemd service template
└── setup.py/pyproject.toml # Package configuration
```

### Configuration System

- **Config Directory**: `~/.config/watcher/`
- **Global Ignore**: `~/.config/watcher/ignore`
- **Per-project Configs**: `~/.config/watcher/{name}.yaml`
- **Systemd Services**: `~/.config/systemd/user/watcher@{name}.service`

### Git Operations

The watcher implements sophisticated git handling:
- **Commit Delays**: Waits for configurable delay after last change to batch modifications
- **Squashed Commits**: Combines multiple file changes into single commit with descriptive message
- **Submodule Handling**: Commits to submodule first, then updates reference in main repo
- **Auto-push**: Optionally pushes commits immediately after creation
- **Periodic Fetch**: Checks for remote changes and sends notifications

### Threading Model

- **Main Thread**: Runs watchdog file observer
- **Timer Threads**: Handle delayed commits per repository
- **Fetch Timer**: Periodic remote checking
- **Thread Safety**: Uses locks for timer management

## Important Implementation Details

- Uses `watchdog` library for cross-platform file monitoring
- Systemd user services for process management (Linux-specific)
- Desktop notifications via `notify-send` command
- YAML configuration with validation
- Git operations via subprocess calls with proper error handling
- Comprehensive logging to systemd journal