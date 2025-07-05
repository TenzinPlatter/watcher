# Best Practices Guide

Collection of recommended practices for using watcher effectively and safely.

## Configuration Best Practices

### 1. Use Descriptive Configuration Names

**Good naming patterns:**
```bash
# Purpose-based names
watcher init dotfiles
watcher init work-api-server
watcher init personal-blog
watcher init home-automation

# Project-based names
watcher init mycompany-frontend
watcher init mycompany-backend
watcher init side-project-app
```

**Avoid generic names:**
```bash
# These names are not descriptive
watcher init config      # Too generic
watcher init project1    # Not descriptive
watcher init test        # Unclear purpose
watcher init temp        # Sounds temporary
```

### 2. Set Appropriate Commit Delays

Choose commit delays based on your workflow:

```yaml
# Active development - quick feedback
commit_delay: 30         # 30 seconds

# Configuration files - allow multiple edits
commit_delay: 300        # 5 minutes

# Documentation - moderate delay
commit_delay: 120        # 2 minutes

# Large projects - prevent too many commits
commit_delay: 180        # 3 minutes
```

### 3. Configure Auto-Push Strategically

```yaml
# Personal projects - auto-push for backup
auto_push: true

# Work projects - manual push for review
auto_push: false

# Shared repositories - consider team workflow
auto_push: false         # Usually better to push manually

# Dotfiles - auto-push for synchronization
auto_push: true
```

### 4. Use Hierarchical Ignore Patterns

Organize ignore patterns by scope:

```yaml
# Global ignore (~/.config/watcher/ignore)
# - OS files (.DS_Store, Thumbs.db)
# - Editor files (.vscode/, *.swp)
# - Git internals (.git/)
# - Common temporary files

# Language-specific ignore files
# - ~/.config/watcher/nodejs-ignore
# - ~/.config/watcher/python-ignore
# - ~/.config/watcher/go-ignore

# Project-specific ignore (in config file)
ignore_patterns:
  - "logs/"              # Project uses logs directory
  - "*.secret"           # Project-specific secret files
  - "build-output/"      # Project-specific build directory
```

## Security Best Practices

### 1. Protect Sensitive Information

#### Never commit sensitive data:
```yaml
# Add to ignore patterns
ignore_patterns:
  - "*.key"
  - "*.pem"
  - "*.p12"
  - ".env"
  - ".env.*"
  - "secrets/"
  - "private/"
  - "credentials.*"
  - "*.secret"
  - "api-keys.*"
  - "passwords.*"
```

#### Review commits before auto-push:
```yaml
# For repositories with sensitive data
auto_push: false         # Manual review before push
```

#### Use project-specific ignore files:
```yaml
# Reference project-local ignore for sensitive patterns
ignore_files:
  - ".watcher-ignore"    # Project team manages this file
```

### 2. Repository Access Control

#### Use appropriate git remotes:
```bash
# For private repositories, ensure proper authentication
git remote -v

# Use SSH keys for better security
git remote set-url origin git@github.com:user/private-repo.git
```

#### Set up proper git configuration:
```bash
# Use work email for work repositories
cd ~/work/project
git config user.email "work@company.com"

# Use personal email for personal projects
cd ~/personal/project
git config user.email "personal@email.com"
```

### 3. File Permissions

#### Protect configuration files:
```bash
# Ensure config directory has proper permissions
chmod 700 ~/.config/watcher

# Protect individual config files
chmod 600 ~/.config/watcher/*.yaml
```

#### Monitor file permissions in watched directories:
```bash
# Check for accidentally committed sensitive files
find ~/projects -name "*.key" -o -name "*.secret" -o -name ".env"
```

## Performance Best Practices

### 1. Optimize Ignore Patterns

#### Exclude large directories early:
```yaml
# Put large, obvious excludes first
ignore_patterns:
  - "node_modules/"      # Often the largest directory
  - ".git/"              # Large and changing frequently
  - "build/"             # Build artifacts
  - "dist/"              # Distribution files
  - "__pycache__/"       # Python cache
  - ".cache/"            # General cache
```

#### Use specific patterns:
```yaml
# Good - specific patterns
ignore_patterns:
  - "*.log"              # Specific file type
  - "build/"             # Specific directory
  - "tmp/"               # Specific temporary directory

# Avoid - overly broad patterns
ignore_patterns:
  - "*/"                 # Too broad
  - "temp*"              # Could match important files
```

### 2. Manage Resource Usage

#### Monitor system resources:
```bash
# Check watcher process resource usage
ps aux | grep watcher
top -p $(pgrep -f "watcher run")

# Check file descriptor usage
lsof -p $(pgrep -f "watcher run") | wc -l
```

#### Limit concurrent watchers:
```bash
# Don't run too many watchers simultaneously
# Start only what you actively need
watcher ls                    # Check current watchers
watcher down inactive-project # Stop unused watchers
```

#### Split large projects:
```yaml
# Instead of watching entire monorepo
watch_directory: "~/monorepo"

# Split into components
# Frontend watcher
name: "monorepo-frontend"
watch_directory: "~/monorepo/frontend"

# Backend watcher  
name: "monorepo-backend"
watch_directory: "~/monorepo/backend"
```

### 3. Optimize Git Operations

#### Keep repositories clean:
```bash
# Regular cleanup
cd ~/project
git gc --prune=now         # Garbage collect
git remote prune origin    # Clean remote branches

# Check repository size
du -sh .git/
```

#### Use shallow clones for large repositories:
```bash
# For very large repositories
git clone --depth 1 <url>
```

## Workflow Best Practices

### 1. Daily Workflow

#### Morning startup routine:
```bash
# Start essential watchers
watcher up dotfiles
watcher up current-project

# Check status
watcher ls

# Review any issues
journalctl --user -u 'watcher@*.service' -p err --since "24 hours ago"
```

#### Evening shutdown routine:
```bash
# Check for uncommitted changes
watcher ls

# Stop work-related watchers
watcher down work-project

# Keep personal watchers running
# (dotfiles, personal projects)
```

### 2. Project Lifecycle Management

#### Starting a new project:
```bash
# Initialize git repository first
cd ~/projects/new-project
git init
git remote add origin <url>

# Create watcher configuration
watcher init new-project --watch-dir ~/projects/new-project

# Customize configuration
watcher edit-config new-project

# Start watching
watcher up new-project
```

#### Finishing a project:
```bash
# Ensure all changes are committed
watcher logs project-name | grep commit

# Final manual push if needed
cd ~/projects/project
git push

# Stop and remove watcher
watcher down project-name
watcher remove project-name --force
```

### 3. Team Collaboration

#### Working with shared repositories:
```yaml
# Use shorter commit delays for active collaboration
commit_delay: 30

# Fetch frequently to stay updated
fetch_interval: 300

# Enable remote change notifications
notify_on_remote_changes: true

# Manual push for review workflow
auto_push: false
```

#### Handling merge conflicts:
```bash
# When watcher detects conflicts
cd ~/project
git status

# Resolve conflicts manually
git add .
git commit -m "Resolve merge conflicts"

# Restart watcher if needed
watcher down project-name
watcher up project-name
```

## Maintenance Best Practices

### 1. Regular Maintenance Tasks

#### Weekly tasks:
```bash
# Check service health
watcher ls

# Review error logs
journalctl --user -u 'watcher@*.service' -p err --since "7 days ago"

# Clean up old logs
journalctl --user --vacuum-time=30d

# Update ignore patterns if needed
watcher edit-ignore
```

#### Monthly tasks:
```bash
# Review and optimize configurations
for config in $(watcher ls --quiet); do
    watcher status $config
done

# Check disk space usage
df -h
du -sh ~/.config/watcher

# Update watcher if needed
pip install --upgrade -e .
```

### 2. Backup and Recovery

#### Backup configurations:
```bash
# Create backup script
#!/bin/bash
BACKUP_DIR="$HOME/.local/backup/watcher"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/watcher-config-$DATE.tar.gz" \
    -C "$HOME/.config" watcher/

echo "Backup created: $BACKUP_DIR/watcher-config-$DATE.tar.gz"
```

#### Recovery procedures:
```bash
# Restore from backup
cd ~/.config
tar -xzf ~/.local/backup/watcher/watcher-config-20231201_120000.tar.gz

# Restart services
systemctl --user daemon-reload
watcher up config-name
```

### 3. Monitoring and Alerting

#### Health monitoring script:
```bash
#!/bin/bash
# ~/.local/bin/watcher-health-check

FAILED_SERVICES=()

for config in $(watcher ls --quiet 2>/dev/null); do
    if ! systemctl --user is-active watcher@$config.service >/dev/null 2>&1; then
        FAILED_SERVICES+=("$config")
    fi
done

if [ ${#FAILED_SERVICES[@]} -gt 0 ]; then
    echo "⚠️ Failed watcher services: ${FAILED_SERVICES[*]}"
    # Send notification or email
    notify-send "Watcher Alert" "Services failed: ${FAILED_SERVICES[*]}"
fi
```

#### Automated health checks:
```bash
# Add to crontab for regular monitoring
crontab -e

# Check every 30 minutes
*/30 * * * * ~/.local/bin/watcher-health-check
```

## Troubleshooting Best Practices

### 1. Systematic Debugging

#### Debug workflow:
```bash
# 1. Check service status
watcher status problematic-config

# 2. Check recent logs
watcher logs problematic-config -n 50

# 3. Test configuration
watcher test-ignore suspicious-file.txt problematic-config

# 4. Run manually for detailed output
watcher run problematic-config
```

#### Log analysis:
```bash
# Find specific issues
journalctl --user -u watcher@config.service | grep -i error
journalctl --user -u watcher@config.service | grep -i "push.*fail"
journalctl --user -u watcher@config.service | grep -i "commit.*fail"
```

### 2. Prevention Strategies

#### Validate configurations before deployment:
```bash
# Test configuration before starting service
watcher status new-config

# Verify ignore patterns
watcher test-ignore important-file.txt new-config

# Check git repository state
cd ~/project
git status
git remote -v
```

#### Monitor resource usage:
```bash
# Set up resource monitoring
echo "Checking watcher resource usage..."
ps -o pid,vsz,rss,comm -p $(pgrep -f "watcher run")

# Alert if memory usage is too high
MEMORY_LIMIT=100000  # 100MB in KB
for pid in $(pgrep -f "watcher run"); do
    memory=$(ps -o rss= -p $pid)
    if [ "$memory" -gt "$MEMORY_LIMIT" ]; then
        echo "⚠️ High memory usage for PID $pid: ${memory}KB"
    fi
done
```

## Documentation Best Practices

### 1. Document Your Setup

#### Create project documentation:
```markdown
# Project Watcher Setup

## Configuration
- Config name: `my-project`
- Watch directory: `~/projects/my-project`
- Commit delay: 60 seconds
- Auto-push: Disabled (manual review required)

## Special Ignore Patterns
- `*.secret` - Project secret files
- `build-cache/` - Custom build cache directory
- `local-config/` - Local development configurations

## Team Notes
- Manual push required for code review
- Notify team before major ignore pattern changes
- Use `git pull --rebase` to avoid merge commits
```

#### Document custom workflows:
```bash
# Create workflow documentation
cat > ~/projects/my-project/.watcher-workflow.md << 'EOF'
# Watcher Workflow for This Project

## Starting Development
1. `watcher up my-project`
2. `watcher logs my-project -f` (in separate terminal)

## Before Pushing
1. Review recent commits: `git log --oneline -5`
2. Manual push: `git push`

## Troubleshooting
- Check ignore patterns: `watcher test-ignore path/to/file my-project`
- View service status: `watcher status my-project`
EOF
```

### 2. Share Knowledge

#### Team documentation:
```markdown
# Team Watcher Guidelines

## Naming Conventions
- Use project name as config name
- Format: `team-project-component`
- Examples: `api-server`, `frontend-app`, `shared-utils`

## Ignore Patterns
- Follow team ignore file: `.team-watcher-ignore`
- Don't modify global patterns without team discussion
- Document project-specific patterns

## Commit Messages
- Auto-commits use format: "Auto-commit: {action} {count} files"
- Manual commits should be descriptive
- Squash auto-commits before major releases
```

## Advanced Best Practices

### 1. Custom Ignore Patterns

#### Language-specific patterns:
```bash
# Create comprehensive language ignores
cat > ~/.config/watcher/web-ignore << 'EOF'
# Web development ignore patterns
node_modules/
bower_components/
npm-debug.log*
yarn-debug.log*
.env.local
.env.development.local
.env.test.local
.env.production.local
dist/
build/
coverage/
.cache/
.parcel-cache/
.next/
.nuxt/
.vuepress/dist/
EOF
```

#### Framework-specific patterns:
```bash
# Framework-specific ignores
cat > ~/.config/watcher/react-ignore << 'EOF'
# React specific
build/
.env.local
.env.development.local
.env.test.local
.env.production.local
npm-debug.log*
yarn-debug.log*
yarn-error.log*
EOF
```

### 2. Multi-Environment Setup

#### Development vs Production:
```yaml
# Development configuration
name: "myapp-dev"
watch_directory: "~/dev/myapp"
commit_delay: 30        # Fast feedback
auto_push: false        # Review before push

# Staging configuration  
name: "myapp-staging"
watch_directory: "~/staging/myapp"
commit_delay: 120       # Longer delay
auto_push: true         # Auto-deploy to staging
```

### 3. Integration with Other Tools

#### CI/CD Integration:
```yaml
# Configure for CI/CD workflow
auto_push: true         # Push triggers CI
commit_delay: 180       # Allow batching before CI

# Ignore CI artifacts
ignore_patterns:
  - ".ci/"
  - "ci-output/"
  - "*.ci.log"
```

#### Editor Integration:
```yaml
# Work well with editors
ignore_patterns:
  - "*.swp"             # Vim
  - "*.swo"             # Vim
  - ".vscode/"          # VS Code
  - ".idea/"            # IntelliJ
  - "*.sublime-*"       # Sublime Text
```

By following these best practices, you'll have a more reliable, secure, and efficient watcher setup that scales with your development workflow.