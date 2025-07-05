# Troubleshooting Guide

Complete guide to diagnosing and solving common watcher issues.

## Quick Diagnosis

### 1. Check Service Status
```bash
# Check if service is running
watcher status myproject

# List all configurations
watcher ls

# Check systemd service directly
systemctl --user status watcher@myproject.service
```

### 2. View Recent Logs
```bash
# Show recent logs
watcher logs myproject -n 50

# Follow logs in real-time
watcher logs myproject -f

# Show error logs only
journalctl --user -u watcher@myproject.service -p err
```

### 3. Test Configuration
```bash
# Validate configuration
watcher status myproject

# Test ignore patterns
watcher test-ignore path/to/file.txt myproject

# Run watcher manually
watcher run myproject
```

## Common Issues

### Service Won't Start

#### Symptoms
- `watcher up myproject` fails
- Service shows as "failed" or "inactive"
- Error messages when starting

#### Diagnosis Steps

1. **Check configuration exists**:
   ```bash
   watcher status myproject
   ```

2. **Check configuration validity**:
   ```bash
   # Look for validation errors
   watcher up myproject
   ```

3. **Check directory permissions**:
   ```bash
   # Verify watch directory exists and is accessible
   ls -la ~/projects/myapp
   
   # Check if it's a git repository
   ls -la ~/projects/myapp/.git
   ```

4. **Check systemd service**:
   ```bash
   systemctl --user status watcher@myproject.service
   ```

#### Common Causes and Solutions

**Configuration file doesn't exist**:
```bash
❌ Config 'myproject' does not exist. Run 'watcher init myproject' first.

# Solution:
watcher init myproject
```

**Watch directory doesn't exist**:
```bash
❌ Config error: Watch directory does not exist: /path/to/directory

# Solution:
mkdir -p /path/to/directory
# Or edit config to point to correct directory
watcher edit-config myproject
```

**Not a git repository**:
```bash
❌ Config error: Repository directory is not a git repository: /path/to/repo

# Solution:
cd /path/to/repo
git init
# Or edit config to point to correct git repository
watcher edit-config myproject
```

**Systemd service template missing**:
```bash
# Solution:
watcher init myproject  # Reinstalls service template
systemctl --user daemon-reload
```

### Service Keeps Crashing

#### Symptoms
- Service starts but immediately stops
- High restart count in systemd status
- Repeated error messages in logs

#### Diagnosis Steps

1. **Check restart count**:
   ```bash
   systemctl --user status watcher@myproject.service
   # Look for "Restarts: X"
   ```

2. **View crash logs**:
   ```bash
   journalctl --user -u watcher@myproject.service --since "1 hour ago"
   ```

3. **Run manually to see errors**:
   ```bash
   watcher run myproject
   ```

#### Common Causes and Solutions

**Permission denied on directories**:
```bash
❌ Error: Permission denied: '/path/to/directory'

# Solution:
chmod 755 /path/to/directory
# Or change ownership
sudo chown -R $USER:$USER /path/to/directory
```

**Git command failures**:
```bash
❌ Git command failed: git status

# Check git configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Check repository state
cd /path/to/repo
git status
```

**Python/dependency issues**:
```bash
❌ ModuleNotFoundError: No module named 'watchdog'

# Solution:
pip install -r requirements.txt
# Or reinstall watcher
pip install -e .
```

### Files Not Being Committed

#### Symptoms
- Watcher is running but files aren't being committed
- No error messages in logs
- File changes are detected but no commits happen

#### Diagnosis Steps

1. **Check if files are being ignored**:
   ```bash
   watcher test-ignore path/to/changed/file.txt myproject
   ```

2. **Check git status manually**:
   ```bash
   cd /path/to/repo
   git status
   ```

3. **Look for watcher activity in logs**:
   ```bash
   watcher logs myproject -f
   # Make a test change and watch for activity
   ```

#### Common Causes and Solutions

**Files are being ignored**:
```bash
$ watcher test-ignore "temp.log" myproject
Result: ❌ IGNORED
Matched by:
  - global: *.log

# Solution: Remove from ignore patterns or use different filename
watcher edit-ignore
watcher edit-config myproject
```

**Git repository has issues**:
```bash
# Check for git errors
cd /path/to/repo
git status

# Common issues:
# - Merge conflicts
# - Detached HEAD
# - Corrupted repository

# Solutions:
git merge --abort  # If in merge
git checkout main  # If detached
git fsck          # Check repository integrity
```

**Commit delay too long**:
```bash
# Check commit delay setting
watcher status myproject

# Files might be pending commit
# Wait for commit_delay seconds or edit config
watcher edit-config myproject
# Set commit_delay: 30  # 30 seconds instead of default 60
```

### Push Failures

#### Symptoms
- Commits are created but not pushed
- Push error messages in logs
- Auto-push is enabled but doesn't work

#### Diagnosis Steps

1. **Check auto-push setting**:
   ```bash
   watcher status myproject
   # Look for auto_push setting
   ```

2. **Check git remote configuration**:
   ```bash
   cd /path/to/repo
   git remote -v
   git push  # Test manual push
   ```

3. **Check push errors in logs**:
   ```bash
   watcher logs myproject | grep -i push
   ```

#### Common Causes and Solutions

**No remote configured**:
```bash
❌ Failed to push: no remote repository

# Solution:
cd /path/to/repo
git remote add origin https://github.com/user/repo.git
git push -u origin main
```

**Authentication issues**:
```bash
❌ Failed to push: authentication failed

# Solutions:
# For HTTPS:
git config credential.helper store
git push  # Enter credentials

# For SSH:
ssh-keygen -t ed25519 -C "your.email@example.com"
# Add key to GitHub/GitLab/etc.
```

**Diverged branches**:
```bash
❌ Failed to push: rejected (non-fast-forward)

# Solution:
cd /path/to/repo
git pull --rebase
# Or configure in watcher to handle automatically
```

### High Resource Usage

#### Symptoms
- High CPU usage
- High memory usage
- System feels slow when watcher is running

#### Diagnosis Steps

1. **Check watcher processes**:
   ```bash
   ps aux | grep watcher
   top -p $(pgrep -f "watcher run")
   ```

2. **Check number of files being watched**:
   ```bash
   find /path/to/watch/directory -type f | wc -l
   ```

3. **Check ignore patterns effectiveness**:
   ```bash
   watcher test-ignore large-directory/ myproject
   ```

#### Common Causes and Solutions

**Watching too many files**:
```bash
# Large directories like node_modules/ not ignored
# Solution: Add to ignore patterns
watcher edit-config myproject
ignore_patterns:
  - "node_modules/"
  - "build/"
  - "dist/"
```

**Inefficient ignore patterns**:
```bash
# Avoid overly complex patterns
# Bad:
ignore_patterns:
  - "**/**/temp/**/*"

# Good:
ignore_patterns:
  - "temp/"
  - "*/temp/"
```

**Multiple watchers on same directory**:
```bash
# Check for conflicting watchers
watcher ls

# Solution: Remove duplicate watchers
watcher remove duplicate-config --force
```

### Desktop Notifications Not Working

#### Symptoms
- Watcher is working but no notifications appear
- Notification settings are enabled

#### Diagnosis Steps

1. **Check notification settings**:
   ```bash
   watcher status myproject
   # Look for enable_notifications, notify_on_commit, etc.
   ```

2. **Test notifications manually**:
   ```bash
   notify-send "Test" "This is a test notification"
   ```

3. **Check notification daemon**:
   ```bash
   ps aux | grep notification
   systemctl --user status notification-daemon
   ```

#### Common Causes and Solutions

**Notification daemon not running**:
```bash
# For GNOME:
systemctl --user start gnome-session-manager

# For KDE:
systemctl --user start knotification

# For others, install notification daemon:
sudo apt install dunst  # Debian/Ubuntu
sudo pacman -S dunst    # Arch
```

**Notifications disabled in config**:
```bash
# Edit configuration
watcher edit-config myproject

# Enable notifications:
enable_notifications: true
notify_on_commit: true
notify_on_remote_changes: true
```

**notify-send not available**:
```bash
# Install libnotify:
sudo apt install libnotify-bin  # Debian/Ubuntu
sudo pacman -S libnotify        # Arch
sudo dnf install libnotify      # Fedora
```

## Performance Issues

### Slow File Detection

#### Symptoms
- Long delay between file change and commit
- Watcher seems unresponsive

#### Solutions

1. **Reduce commit delay**:
   ```bash
   watcher edit-config myproject
   # Set commit_delay: 30  # Reduce from default 60
   ```

2. **Check file system**:
   ```bash
   # Ensure file system supports inotify
   cat /proc/sys/fs/inotify/max_user_watches
   
   # Increase if needed:
   echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   ```

3. **Optimize ignore patterns**:
   ```bash
   # Add common large directories to ignore
   watcher edit-config myproject
   ignore_patterns:
     - "node_modules/"
     - ".git/"
     - "build/"
     - "dist/"
     - "__pycache__/"
   ```

### Memory Usage Issues

#### High Memory Usage

1. **Check process memory**:
   ```bash
   ps -o pid,vsz,rss,comm -p $(pgrep -f "watcher run")
   ```

2. **Reduce watched files**:
   ```bash
   # Add more ignore patterns
   watcher edit-config myproject
   ```

3. **Split large projects**:
   ```bash
   # Instead of watching entire project
   watcher init frontend --watch-dir ~/project/frontend
   watcher init backend --watch-dir ~/project/backend
   ```

## Log Analysis

### Understanding Log Messages

#### Normal Operation
```
🚀 Starting watcher for config: myproject
📁 Watching directory: /home/user/projects/myapp
⏰ Scheduled commit for myapp in 60 seconds (3 changes)
✓ Committed: Auto-commit: modified 3 files
🚀 Pushed main repo changes
```

#### Warning Messages
```
⚠️ Warning: Could not read ignore file /path/to/ignore: No such file
⚠️ Config warning: Ignore file does not exist: /path/to/ignore
⚠️ Failed to send notification: Command 'notify-send' not found
```

#### Error Messages
```
❌ Error: Directory /path/to/directory does not exist
❌ Config error: Repository directory is not a git repository
❌ Git command failed: git push
❌ Failed to stage changes in main repo
```

### Log Filtering

#### Find Specific Issues
```bash
# Find all errors
journalctl --user -u watcher@myproject.service -p err

# Find git-related issues
watcher logs myproject | grep -i git

# Find push failures
watcher logs myproject | grep -i "push.*failed"

# Find commit activity
watcher logs myproject | grep -i commit
```

#### Time-based Analysis
```bash
# Issues in last hour
journalctl --user -u watcher@myproject.service --since "1 hour ago"

# Issues today
journalctl --user -u watcher@myproject.service --since "today"

# Issues during specific period
journalctl --user -u watcher@myproject.service --since "2023-12-01 09:00" --until "2023-12-01 17:00"
```

## Recovery Procedures

### Service Recovery

#### Restart Failed Service
```bash
# Stop and start service
watcher down myproject
watcher up myproject

# Or restart directly
systemctl --user restart watcher@myproject.service
```

#### Reset Service Template
```bash
# Reinstall service template
rm ~/.config/systemd/user/watcher@.service
watcher init myproject
```

### Configuration Recovery

#### Backup and Restore
```bash
# Backup configurations
cp -r ~/.config/watcher ~/.config/watcher.backup

# Restore from backup
cp -r ~/.config/watcher.backup ~/.config/watcher
```

#### Reset to Defaults
```bash
# Remove configuration
watcher remove myproject --force

# Recreate with defaults
watcher init myproject
```

### Repository Recovery

#### Uncommitted Changes
```bash
cd /path/to/repo

# Stash uncommitted changes
git stash

# Or commit manually
git add .
git commit -m "Manual commit before watcher restart"
```

#### Corrupted Repository
```bash
cd /path/to/repo

# Check repository integrity
git fsck

# Reset to known good state
git reset --hard HEAD~1

# Or clone fresh copy
cd ..
git clone <repository-url> repo-fresh
cp -r repo/.git repo-fresh/
```

## Prevention Strategies

### Regular Maintenance

#### Weekly Checks
```bash
# Check all service status
watcher ls

# Check for errors in logs
journalctl --user -u 'watcher@*.service' -p err --since "1 week ago"

# Clean old logs
journalctl --user --vacuum-time=30d
```

#### Monthly Tasks
```bash
# Update watcher if needed
pip install --upgrade -e .

# Review and optimize ignore patterns
watcher edit-ignore

# Check disk space usage
df -h
```

### Monitoring Setup

#### Health Check Script
```bash
#!/bin/bash
# ~/.local/bin/watcher-health-check

echo "Watcher Health Check - $(date)"
echo "================================"

for config in $(watcher ls --quiet); do
    if systemctl --user is-active watcher@$config.service >/dev/null; then
        echo "✅ $config: Running"
    else
        echo "❌ $config: Not running"
        watcher up $config
    fi
done

# Check for errors in last 24 hours
echo ""
echo "Recent errors:"
journalctl --user -u 'watcher@*.service' -p err --since "24 hours ago" --no-pager | tail -10
```

#### Automated Monitoring
```bash
# Add to crontab
crontab -e

# Run health check every hour
0 * * * * ~/.local/bin/watcher-health-check >> ~/.local/log/watcher-health.log
```

### Backup Strategy

#### Configuration Backup
```bash
#!/bin/bash
# ~/.local/bin/backup-watcher-config

BACKUP_DIR="$HOME/.local/backup/watcher"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/watcher-config-$DATE.tar.gz" -C "$HOME/.config" watcher/

# Keep only last 10 backups
ls -t "$BACKUP_DIR"/watcher-config-*.tar.gz | tail -n +11 | xargs rm -f

echo "Watcher configuration backed up to $BACKUP_DIR/watcher-config-$DATE.tar.gz"
```

#### Automated Backup
```bash
# Add to crontab for daily backup
crontab -e

# Backup configurations daily at 2 AM
0 2 * * * ~/.local/bin/backup-watcher-config
```

## Getting Help

### Collect Diagnostic Information

When reporting issues, collect this information:

```bash
# System information
uname -a
python3 --version
pip show watcher

# Watcher status
watcher ls
watcher status problematic-config

# Service status
systemctl --user status watcher@problematic-config.service

# Recent logs
journalctl --user -u watcher@problematic-config.service -n 100

# Configuration
cat ~/.config/watcher/problematic-config.yaml

# Test ignore patterns
watcher test-ignore problematic-file.txt problematic-config
```

### Common Support Questions

**Q: How do I increase the file watch limit?**
```bash
# Check current limit
cat /proc/sys/fs/inotify/max_user_watches

# Increase limit temporarily
sudo sysctl fs.inotify.max_user_watches=524288

# Make permanent
echo 'fs.inotify.max_user_watches=524288' | sudo tee -a /etc/sysctl.conf
```

**Q: How do I exclude large directories?**
```bash
watcher edit-config myproject
# Add to ignore_patterns:
ignore_patterns:
  - "node_modules/"
  - "build/"
  - "dist/"
  - ".git/"
```

**Q: How do I handle merge conflicts?**
```bash
cd /path/to/repo
git status
# Resolve conflicts manually
git add .
git commit -m "Resolve merge conflicts"
```

**Q: How do I change the commit message format?**
Currently, commit messages are automatically generated based on git status. This feature may be configurable in future versions.