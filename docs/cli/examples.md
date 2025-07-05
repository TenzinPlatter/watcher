# CLI Examples

Practical examples of using watcher CLI commands in real-world scenarios.

## Getting Started Examples

### Basic Setup

#### Initialize Your First Watcher
```bash
# Initialize with defaults
watcher init

# This creates:
# - ~/.config/watcher/config.yaml
# - ~/.config/watcher/ignore (global ignore file)
# - ~/.config/systemd/user/watcher@.service (systemd template)
```

#### Start Watching
```bash
# Start the default configuration
watcher up

# Check that it's running
watcher status

# View real-time logs
watcher logs -f
```

#### Make a Test Change
```bash
# In another terminal, make a change to your files
echo "# Test change" >> ~/README.md

# Watch the logs for commit activity
# You should see something like:
# ⏰ Scheduled commit for repo in 60 seconds (1 changes)
# ✓ Committed: Auto-commit: modified 1 file
```

## Multi-Project Setup Examples

### Setting Up Multiple Projects

#### Dotfiles Watcher
```bash
# Initialize dotfiles configuration
watcher init dotfiles --watch-dir ~/.dotfiles --repo-dir ~/.dotfiles

# Customize for dotfiles
watcher edit-config dotfiles
# Set commit_delay: 300 (5 minutes for config files)
# Set auto_push: true (backup dotfiles automatically)

# Start dotfiles watcher
watcher up dotfiles
```

#### Work Project Watcher
```bash
# Initialize work project
watcher init work-api --watch-dir ~/work/api-server --commit-delay 30

# Customize for work environment
watcher edit-config work-api
# Set auto_push: false (manual push for code review)
# Add work-specific ignore patterns

# Start work watcher
watcher up work-api
```

#### Personal Project Watcher
```bash
# Initialize personal project
watcher init personal-blog --watch-dir ~/projects/blog

# Start personal project
watcher up personal-blog

# Check all running watchers
watcher ls
# Output:
#   dotfiles        ✅ ACTIVE (enabled)
#     Watch: /home/user/.dotfiles
#   
#   work-api        ✅ ACTIVE (enabled)
#     Watch: /home/user/work/api-server
#   
#   personal-blog   ✅ ACTIVE (enabled)
#     Watch: /home/user/projects/blog
```

## Configuration Examples

### Customizing Configurations

#### Edit Configuration File
```bash
# Open configuration in your editor
watcher edit-config work-api

# Example customizations:
# commit_delay: 30          # Quick commits for active development
# fetch_interval: 300       # Check for remote changes every 5 minutes
# auto_push: false          # Manual push for code review
# ignore_patterns:
#   - "*.log"
#   - "build/"
#   - "dist/"
#   - ".env.local"
```

#### Edit Global Ignore File
```bash
# Edit global ignore patterns
watcher edit-ignore

# Add patterns that apply to all projects:
# .DS_Store
# *.swp
# __pycache__/
# node_modules/
# .git/
```

### Testing Ignore Patterns

#### Test Specific Files
```bash
# Test if a file would be ignored
watcher test-ignore "build/output.js" work-api
# Output:
# File: build/output.js
# Config: work-api
# Result: ❌ IGNORED
# Matched by:
#   - config: build/

# Test a source file
watcher test-ignore "src/main.py" work-api
# Output:
# File: src/main.py
# Config: work-api
# Result: ✅ NOT IGNORED
```

#### Test Different File Types
```bash
# Test various file types
watcher test-ignore ".git/index" work-api          # Should be ignored
watcher test-ignore "node_modules/package.json" work-api  # Should be ignored
watcher test-ignore "src/components/App.js" work-api      # Should NOT be ignored
watcher test-ignore "README.md" work-api                  # Should NOT be ignored
```

## Service Management Examples

### Starting and Stopping Services

#### Individual Service Control
```bash
# Start specific service
watcher up dotfiles
watcher up work-api

# Stop specific service
watcher down work-api

# Check specific service status
watcher status dotfiles
```

#### Bulk Service Operations
```bash
# Start multiple services
for config in dotfiles work-api personal-blog; do
    echo "Starting $config..."
    watcher up $config
done

# Stop all watcher services
for config in $(watcher ls --quiet); do
    echo "Stopping $config..."
    watcher down $config
done
```

### Service Status and Monitoring

#### Check Service Status
```bash
# List all configurations and their status
watcher ls

# Detailed status for specific service
watcher status work-api
# Output:
# Config: work-api
#   Watch directory: /home/user/work/api-server
#   Repo directory: /home/user/work/api-server
#   Service: ✅ ACTIVE
#   Enabled: ✅ YES
# 
# Systemd status:
# ● watcher@work-api.service - Watcher for work-api configuration
#    Active: active (running) since Mon 2023-12-04 09:00:00 EST; 2h 15min ago
#    ...
```

#### Monitor Service Logs
```bash
# Follow logs in real-time
watcher logs work-api -f

# Show last 100 log lines
watcher logs work-api -n 100

# Show logs for all services
for config in $(watcher ls --quiet); do
    echo "=== Logs for $config ==="
    watcher logs $config -n 20
done
```

## Troubleshooting Examples

### Common Issues and Solutions

#### Service Won't Start
```bash
# Check configuration validity
watcher status problematic-config

# Example output showing issues:
# ❌ Config 'problematic-config' is invalid:
#    Watch directory does not exist: /nonexistent/path
#    Repository directory is not a git repository: /path/to/non-git

# Fix the issues
mkdir -p /correct/path
cd /correct/path
git init

# Edit configuration to fix paths
watcher edit-config problematic-config

# Try starting again
watcher up problematic-config
```

#### Files Not Being Committed
```bash
# Check if files are being ignored
watcher test-ignore "my-file.txt" my-config

# Check watcher activity
watcher logs my-config -f
# Make a test change and watch for activity

# Check git repository state
cd ~/project
git status

# Check commit delay (files might be pending)
watcher status my-config
# Look for commit_delay setting
```

#### Push Failures
```bash
# Check logs for push errors
watcher logs my-config | grep -i push

# Check git remote configuration
cd ~/project
git remote -v
git push  # Test manual push

# Common fix: set up remote tracking
git push -u origin main
```

## Advanced Usage Examples

### Working with Submodules

#### Project with Submodules
```bash
# Initialize project with submodules
cd ~/project/main-repo
git submodule add https://github.com/user/library.git lib/library

# Set up watcher (automatically detects submodules)
watcher init main-repo --watch-dir ~/project/main-repo

# Start watching
watcher up main-repo

# Make changes in submodule
echo "// Update" >> lib/library/src/main.c

# Watch logs - watcher will:
# 1. Commit changes in submodule
# 2. Update submodule reference in main repo
# 3. Commit the reference update
```

### Language-Specific Setups

#### Node.js Project
```bash
# Create Node.js specific ignore file
cat > ~/.config/watcher/nodejs-ignore << 'EOF'
node_modules/
npm-debug.log*
yarn-debug.log*
.env.local
dist/
build/
coverage/
.cache/
EOF

# Initialize Node.js project watcher
watcher init my-node-app --watch-dir ~/projects/my-node-app

# Edit config to use Node.js ignore file
watcher edit-config my-node-app
# Add to config:
# ignore_files:
#   - "~/.config/watcher/nodejs-ignore"

# Start watching
watcher up my-node-app
```

#### Python Project
```bash
# Create Python specific ignore file
cat > ~/.config/watcher/python-ignore << 'EOF'
__pycache__/
*.pyc
*.pyo
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
.venv/
venv/
EOF

# Initialize Python project
watcher init python-ml --watch-dir ~/projects/ml-project

# Configure for Python
watcher edit-config python-ml
# Add:
# ignore_files:
#   - "~/.config/watcher/python-ignore"
# commit_delay: 90  # Slightly longer for testing

# Start watching
watcher up python-ml
```

### Custom Workflows

#### Development Workflow
```bash
# Morning routine - start development watchers
echo "Starting development environment..."
watcher up dotfiles
watcher up current-project
watcher up documentation

# Check everything is running
watcher ls

# Open logs in separate terminals
gnome-terminal -- watcher logs current-project -f
gnome-terminal -- watcher logs documentation -f
```

#### Work Environment Setup
```bash
# Work day startup script
#!/bin/bash
echo "🚀 Starting work environment..."

# Start work-related watchers
for project in work-frontend work-backend work-docs; do
    if watcher status $project >/dev/null 2>&1; then
        echo "Starting $project..."
        watcher up $project
    else
        echo "⚠️ Configuration $project not found"
    fi
done

# Show status
echo ""
echo "Work watchers status:"
watcher ls | grep work-

# Show any recent errors
echo ""
echo "Recent errors:"
journalctl --user -u 'watcher@work-*.service' -p err --since "1 hour ago" --no-pager
```

#### Project Cleanup
```bash
# End of project - cleanup script
#!/bin/bash
PROJECT_NAME="$1"

if [ -z "$PROJECT_NAME" ]; then
    echo "Usage: $0 <project-name>"
    exit 1
fi

echo "🧹 Cleaning up project: $PROJECT_NAME"

# Stop watcher
echo "Stopping watcher..."
watcher down $PROJECT_NAME

# Check for uncommitted changes
echo "Checking for uncommitted changes..."
if watcher logs $PROJECT_NAME | grep -q "pending"; then
    echo "⚠️ There may be pending changes. Check manually."
fi

# Final push if auto-push is disabled
echo "Performing final push..."
cd ~/projects/$PROJECT_NAME
git push

# Remove watcher configuration
echo "Removing watcher configuration..."
watcher remove $PROJECT_NAME --force

echo "✅ Project cleanup complete"
```

## Integration Examples

### Editor Integration

#### VS Code Integration
```bash
# Create VS Code task for watcher management
mkdir -p .vscode
cat > .vscode/tasks.json << 'EOF'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Watcher",
            "type": "shell",
            "command": "watcher",
            "args": ["up", "my-project"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "panel": "new"
            }
        },
        {
            "label": "Stop Watcher",
            "type": "shell", 
            "command": "watcher",
            "args": ["down", "my-project"],
            "group": "build"
        },
        {
            "label": "Show Watcher Logs",
            "type": "shell",
            "command": "watcher", 
            "args": ["logs", "my-project", "-f"],
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "new"
            }
        }
    ]
}
EOF
```

#### Shell Aliases
```bash
# Add to ~/.bashrc or ~/.zshrc
alias ws='watcher status'
alias wl='watcher ls'
alias wup='watcher up'
alias wdown='watcher down'
alias wlogs='watcher logs'

# Project-specific aliases
alias start-work='watcher up work-frontend && watcher up work-backend'
alias stop-work='watcher down work-frontend && watcher down work-backend'
alias work-status='watcher ls | grep work-'

# Development aliases
alias dev-start='watcher up current-project && watcher logs current-project -f'
alias dev-stop='watcher down current-project'
```

### CI/CD Integration

#### Pre-commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
# Ensure watcher has committed all changes before manual commit

CONFIG_NAME="my-project"

# Check if watcher is running
if ! systemctl --user is-active watcher@$CONFIG_NAME.service >/dev/null; then
    echo "⚠️ Watcher is not running for $CONFIG_NAME"
    echo "Starting watcher to catch any pending changes..."
    watcher up $CONFIG_NAME
    sleep 5  # Give watcher time to process any pending changes
fi

# Check for any recent watcher activity
RECENT_ACTIVITY=$(watcher logs $CONFIG_NAME --since "5 minutes ago" | grep -c "commit")
if [ "$RECENT_ACTIVITY" -gt 0 ]; then
    echo "⚠️ Recent watcher activity detected. Waiting for stability..."
    sleep 10
fi

echo "✅ Pre-commit check passed"
```

### Backup Integration

#### Automated Backup
```bash
# Daily backup script
#!/bin/bash
# ~/.local/bin/daily-watcher-backup

BACKUP_DIR="$HOME/.local/backup/watcher"
DATE=$(date +%Y%m%d)

mkdir -p "$BACKUP_DIR"

# Backup configurations
tar -czf "$BACKUP_DIR/watcher-configs-$DATE.tar.gz" \
    -C "$HOME/.config" watcher/

# Backup recent logs
journalctl --user -u 'watcher@*.service' --since "24 hours ago" \
    > "$BACKUP_DIR/watcher-logs-$DATE.txt"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "watcher-*" -mtime +7 -delete

echo "✅ Watcher backup completed: $BACKUP_DIR/watcher-configs-$DATE.tar.gz"
```

These examples demonstrate practical usage patterns that you can adapt to your specific workflow and requirements.