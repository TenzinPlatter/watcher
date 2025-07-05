# Multi-Project Setup Guide

This guide shows how to set up and manage multiple watcher instances for different projects simultaneously.

## Overview

Watcher supports running multiple instances simultaneously, each monitoring different directories with their own configurations. This is perfect for:

- Managing multiple git repositories
- Separating work and personal projects
- Different commit timing requirements
- Project-specific ignore patterns

## Basic Multi-Project Setup

### Step 1: Initialize Multiple Configurations

```bash
# Set up dotfiles watcher
watcher init dotfiles --watch-dir ~/.dotfiles --repo-dir ~/.dotfiles

# Set up work project watcher
watcher init work-api --watch-dir ~/work/api-server --commit-delay 30

# Set up personal project watcher
watcher init personal-blog --watch-dir ~/projects/blog --commit-delay 120
```

### Step 2: Customize Each Configuration

Edit each configuration to match your needs:

```bash
# Edit dotfiles config
watcher edit-config dotfiles

# Edit work project config
watcher edit-config work-api

# Edit personal project config
watcher edit-config personal-blog
```

### Step 3: Start All Watchers

```bash
watcher up dotfiles
watcher up work-api
watcher up personal-blog
```

### Step 4: Monitor All Projects

```bash
# Check status of all projects
watcher ls

# View logs for specific project
watcher logs work-api -f
```

## Example Configurations

### Dotfiles Configuration

```yaml
# ~/.config/watcher/dotfiles.yaml
name: "dotfiles"
watch_directory: "~/.dotfiles"
repo_directory: "~/.dotfiles"
commit_delay: 300  # 5 minutes - less frequent commits
fetch_interval: 1800  # 30 minutes
enable_notifications: true
notify_on_commit: true
auto_push: true

ignore_patterns:
  - ".DS_Store"
  - "*.swp"
  - ".vscode/"
```

### Work Project Configuration

```yaml
# ~/.config/watcher/work-api.yaml
name: "work-api"
watch_directory: "~/work/api-server"
repo_directory: "~/work/api-server"
commit_delay: 30  # Quick commits for active development
fetch_interval: 300  # 5 minutes
enable_notifications: true
notify_on_commit: true
auto_push: false  # Manual push for work projects

ignore_patterns:
  - "*.log"
  - "logs/"
  - "build/"
  - "dist/"
  - "coverage/"
  - ".env.local"

ignore_files:
  - "~/.config/watcher/nodejs-ignore"
```

### Personal Project Configuration

```yaml
# ~/.config/watcher/personal-blog.yaml
name: "personal-blog"
watch_directory: "~/projects/blog"
repo_directory: "~/projects/blog"
commit_delay: 120  # 2 minutes
fetch_interval: 600  # 10 minutes
enable_notifications: false  # Quiet for personal projects
notify_on_commit: false
auto_push: true

ignore_patterns:
  - "_site/"
  - ".jekyll-cache/"
  - "node_modules/"
  - "*.draft"
```

## Advanced Multi-Project Workflows

### Language-Specific Ignore Files

Create shared ignore files for different languages:

```bash
# Create Node.js ignore file
cat > ~/.config/watcher/nodejs-ignore << 'EOF'
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.yarn-integrity
.env.local
.env.development.local
.env.test.local
.env.production.local
dist/
build/
coverage/
.nyc_output/
.cache/
EOF

# Create Python ignore file
cat > ~/.config/watcher/python-ignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/
.coverage
htmlcov/
.tox/
.env
.venv
ENV/
env/
venv/
EOF
```

Then reference these in your project configs:

```yaml
# In your Python project config
ignore_files:
  - "~/.config/watcher/python-ignore"

# In your Node.js project config
ignore_files:
  - "~/.config/watcher/nodejs-ignore"
```

### Conditional Auto-Push

Set up different push behaviors for different project types:

```yaml
# Work projects - manual push for review
auto_push: false

# Personal projects - auto push
auto_push: true

# Dotfiles - auto push with longer delay
auto_push: true
commit_delay: 300
```

### Notification Strategies

Configure notifications based on project importance:

```yaml
# Critical work projects - full notifications
enable_notifications: true
notify_on_commit: true
notify_on_remote_changes: true

# Personal projects - minimal notifications
enable_notifications: true
notify_on_commit: false
notify_on_remote_changes: true

# Dotfiles - commit notifications only
enable_notifications: true
notify_on_commit: true
notify_on_remote_changes: false
```

## Managing Multiple Projects

### Daily Workflow Commands

```bash
# Start all watchers for the day
watcher up dotfiles
watcher up work-api
watcher up personal-blog

# Check status throughout the day
watcher ls

# View logs when needed
watcher logs work-api -f

# Stop all watchers at end of day
watcher down dotfiles
watcher down work-api
watcher down personal-blog
```

### Bulk Operations

Create shell functions for bulk operations:

```bash
# Add to ~/.bashrc or ~/.zshrc
watcher-start-all() {
    for config in dotfiles work-api personal-blog; do
        echo "Starting $config..."
        watcher up $config
    done
}

watcher-stop-all() {
    for config in dotfiles work-api personal-blog; do
        echo "Stopping $config..."
        watcher down $config
    done
}

watcher-remove-all() {
    for config in dotfiles work-api personal-blog; do
        echo "Removing $config..."
        watcher remove $config --force
    done
}

watcher-status-all() {
    watcher ls
}
```

### Systemd Service Management

You can also manage services directly with systemd:

```bash
# Enable all services to start on boot
systemctl --user enable watcher@dotfiles.service
systemctl --user enable watcher@work-api.service
systemctl --user enable watcher@personal-blog.service

# Start all services
systemctl --user start watcher@dotfiles.service
systemctl --user start watcher@work-api.service
systemctl --user start watcher@personal-blog.service

# Check status of all services
systemctl --user status 'watcher@*.service'
```

## Best Practices

### 1. Organize Configurations by Purpose

- **dotfiles**: Personal environment configurations
- **work-{project}**: Work-related projects
- **personal-{project}**: Personal projects
- **{lang}-{project}**: Language-specific projects

### 2. Use Appropriate Commit Delays

- **Active development**: 30-60 seconds
- **Configuration files**: 5-10 minutes
- **Documentation**: 2-5 minutes
- **Large projects**: 60-120 seconds

### 3. Configure Notifications Wisely

- Enable for important/work projects
- Disable for background/personal projects
- Use remote change notifications for shared repositories

### 4. Set Up Language-Specific Ignore Files

Create shared ignore files for:
- Node.js projects
- Python projects
- Go projects
- Rust projects
- Web projects (HTML/CSS/JS)

### 5. Use Descriptive Configuration Names

Good names:
- `dotfiles`
- `work-api-server`
- `personal-blog`
- `python-ml-project`

Avoid:
- `config`
- `project1`
- `test`
- `temp`

## Troubleshooting Multi-Project Setup

### Common Issues

1. **Services not starting**: Check configuration validity
   ```bash
   watcher status project-name
   ```

2. **Conflicting ignore patterns**: Test specific files
   ```bash
   watcher test-ignore path/to/file.txt project-name
   ```

3. **Performance issues**: Monitor system resources
   ```bash
   systemctl --user status 'watcher@*.service'
   ```

### Resource Management

With multiple watchers running:
- Monitor CPU usage (`top` or `htop`)
- Check memory usage
- Limit number of concurrent watchers if needed
- Use longer commit delays for less active projects

### Debugging Multiple Services

```bash
# View logs for all services
journalctl --user -u 'watcher@*.service' -f

# View logs for specific service
journalctl --user -u watcher@work-api.service -f

# Check service status
systemctl --user list-units 'watcher@*.service'
```

## Migration from Single to Multi-Project

If you're currently using a single watcher configuration:

1. **Backup existing configuration**:
   ```bash
   cp ~/.config/watcher/config.yaml ~/.config/watcher/config.yaml.backup
   ```

2. **Create new named configuration**:
   ```bash
   watcher init main-project --watch-dir ~/projects/main
   ```

3. **Copy settings from old config**:
   ```bash
   watcher edit-config main-project
   # Copy relevant settings from config.yaml.backup
   ```

4. **Test new configuration**:
   ```bash
   watcher up main-project
   watcher logs main-project -f
   ```

5. **Stop old service and start new**:
   ```bash
   watcher down config
   watcher up main-project
   ```

This approach ensures a smooth transition while maintaining your existing setup.