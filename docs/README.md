# Watcher Documentation

Welcome to the Watcher documentation! This directory contains comprehensive guides and references for using the Watcher package.

## Quick Navigation

### Getting Started
- [Installation & Quick Start](../README.md) - Main package README
- [Multi-Project Setup Guide](guides/multi-project-setup.md) - Setting up multiple watchers

### CLI Reference
- [CLI Commands](cli/commands.md) - Complete command reference
- [CLI Examples](cli/examples.md) - Practical usage examples and workflows

### Configuration
- [Configuration Guide](config/configuration.md) - Complete config file reference
- [Ignore Patterns](config/ignore-patterns.md) - Understanding ignore hierarchies
- [Service Management](config/systemd.md) - Systemd integration

### Guides
- [Multi-Project Workflows](guides/multi-project-setup.md) - Managing multiple repositories
- [Troubleshooting](guides/troubleshooting.md) - Common issues and solutions
- [Best Practices](guides/best-practices.md) - Recommended usage patterns

### Development
- [API Reference](development/api.md) - Internal API documentation
- [Contributing](development/contributing.md) - How to contribute to the project

## Documentation Structure

```
docs/
├── README.md                    # This file - documentation overview
├── cli/
│   ├── commands.md             # Complete CLI command reference
│   └── examples.md             # Practical CLI usage examples
├── config/
│   ├── configuration.md        # Complete configuration file reference
│   ├── ignore-patterns.md      # Hierarchical ignore patterns guide
│   └── systemd.md              # Systemd service integration guide
├── guides/
│   ├── multi-project-setup.md  # Setting up multiple watcher instances
│   ├── troubleshooting.md      # Comprehensive troubleshooting guide
│   └── best-practices.md       # Recommended practices and workflows
├── examples/
│   ├── dotfiles-config.yaml    # Example dotfiles configuration
│   ├── nodejs-config.yaml      # Example Node.js project configuration
│   └── python-config.yaml      # Example Python project configuration
└── development/
    ├── api.md                   # Internal API documentation
    └── contributing.md          # Development and contribution guide
```

## Quick Reference

### Essential Commands
```bash
# Initialize and start a watcher
watcher init myproject --watch-dir ~/projects/myapp
watcher up myproject

# Check status and logs
watcher status myproject
watcher logs myproject -f

# List all configurations
watcher ls

# Edit configuration
watcher edit-config myproject
watcher edit-ignore

# Remove configuration
watcher remove myproject
```

### Key Concepts

1. **Configurations**: Each project has its own YAML config file in `~/.config/watcher/`
2. **Services**: Each config runs as a separate systemd service (`watcher@config.service`)
3. **Ignore Hierarchy**: Global ignore → Config ignore → Additional files → Gitignore
4. **Multi-Project**: Run multiple watchers simultaneously for different repositories

## Getting Help

- Check the [Troubleshooting Guide](guides/troubleshooting.md) for common issues
- Use `watcher --help` or `watcher <command> --help` for CLI help
- View logs with `watcher logs <config> -f` for real-time debugging
- Test ignore patterns with `watcher test-ignore <file> <config>`

## Contributing to Documentation

Found an error or want to improve the docs? See the [Contributing Guide](development/contributing.md) for how to submit improvements.