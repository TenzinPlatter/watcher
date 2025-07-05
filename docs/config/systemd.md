# Systemd Integration Guide

Complete guide to watcher's systemd integration for service management.

## Overview

Watcher uses systemd user services to manage multiple watcher instances. Each configuration runs as a separate service, allowing independent control and monitoring.

## Service Architecture

### Service Template
Watcher installs a systemd service template at:
```
~/.config/systemd/user/watcher@.service
```

### Service Instances
Each configuration creates a service instance:
```
watcher@config.service      # Default configuration
watcher@myproject.service   # Custom configuration
watcher@dotfiles.service    # Dotfiles configuration
```

### Service Template Content
```ini
[Unit]
Description=Watcher for %i configuration
After=graphical-session.target

[Service]
Type=simple
ExecStart=watcher run %i
WorkingDirectory=%h
Restart=always
RestartSec=10

# Environment variables
Environment=HOME=%h
Environment=PATH=/usr/local/bin:/usr/bin:/bin:%h/.local/bin

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=watcher-%i

[Install]
WantedBy=default.target
```

## Service Management

### Using Watcher Commands

#### Start Service
```bash
# Start specific configuration
watcher up myproject

# Start default configuration
watcher up
```

#### Stop Service
```bash
# Stop specific configuration
watcher down myproject

# Stop default configuration
watcher down
```

#### Service Status
```bash
# Check watcher status
watcher status myproject

# List all configurations
watcher ls
```

#### View Logs
```bash
# Follow logs in real-time
watcher logs myproject -f

# Show last 50 lines
watcher logs myproject

# Show specific number of lines
watcher logs myproject -n 100
```

### Using Systemctl Directly

#### Service Control
```bash
# Start service
systemctl --user start watcher@myproject.service

# Stop service
systemctl --user stop watcher@myproject.service

# Restart service
systemctl --user restart watcher@myproject.service

# Enable service (start on login)
systemctl --user enable watcher@myproject.service

# Disable service
systemctl --user disable watcher@myproject.service
```

#### Service Status
```bash
# Check service status
systemctl --user status watcher@myproject.service

# Check if service is active
systemctl --user is-active watcher@myproject.service

# Check if service is enabled
systemctl --user is-enabled watcher@myproject.service

# List all watcher services
systemctl --user list-units 'watcher@*.service'
```

#### Logs
```bash
# View service logs
journalctl --user -u watcher@myproject.service

# Follow logs
journalctl --user -u watcher@myproject.service -f

# Show logs since boot
journalctl --user -u watcher@myproject.service -b

# Show logs for last hour
journalctl --user -u watcher@myproject.service --since "1 hour ago"

# Show logs with specific priority
journalctl --user -u watcher@myproject.service -p err
```

## Service Configuration

### Automatic Service Installation

When you run `watcher init`, it automatically:
1. Creates the service template if it doesn't exist
2. Reloads the systemd daemon
3. Makes the service available for your configuration

### Manual Service Installation

If you need to manually install the service template:

```bash
# Create service directory
mkdir -p ~/.config/systemd/user

# Create service template
cat > ~/.config/systemd/user/watcher@.service << 'EOF'
[Unit]
Description=Watcher for %i configuration
After=graphical-session.target

[Service]
Type=simple
ExecStart=watcher run %i
WorkingDirectory=%h
Restart=always
RestartSec=10
Environment=HOME=%h
Environment=PATH=/usr/local/bin:/usr/bin:/bin:%h/.local/bin
StandardOutput=journal
StandardError=journal
SyslogIdentifier=watcher-%i

[Install]
WantedBy=default.target
EOF

# Reload systemd daemon
systemctl --user daemon-reload
```

### Service Template Customization

You can customize the service template for your needs:

#### Custom Environment Variables
```ini
[Service]
# Add custom environment variables
Environment=HOME=%h
Environment=PATH=/usr/local/bin:/usr/bin:/bin:%h/.local/bin
Environment=WATCHER_LOG_LEVEL=DEBUG
Environment=PYTHON_PATH=/usr/local/lib/python3.9/site-packages
```

#### Different Restart Behavior
```ini
[Service]
# Restart only on failure
Restart=on-failure
RestartSec=30

# Don't restart automatically
Restart=no

# Restart always (default)
Restart=always
RestartSec=10
```

#### Resource Limits
```ini
[Service]
# Limit memory usage
MemoryMax=512M

# Limit CPU usage
CPUQuota=50%

# Set nice level
Nice=10
```

## Service Lifecycle

### Service States

#### Active States
- **active (running)**: Service is running normally
- **active (exiting)**: Service is stopping
- **active (dead)**: Service stopped normally

#### Inactive States
- **inactive (dead)**: Service is stopped
- **failed**: Service failed to start or crashed

#### Check Current State
```bash
# Get detailed status
systemctl --user status watcher@myproject.service

# Get just the active state
systemctl --user is-active watcher@myproject.service

# Get just the enabled state
systemctl --user is-enabled watcher@myproject.service
```

### Service Dependencies

#### Prerequisites
Services depend on:
- `graphical-session.target`: Ensures GUI session is available
- User session: Requires user to be logged in

#### Starting Order
```bash
# Services start after graphical session
After=graphical-session.target

# Services want to be part of default target
WantedBy=default.target
```

### Automatic Startup

#### Enable on Login
```bash
# Enable service to start when user logs in
systemctl --user enable watcher@myproject.service

# Enable multiple services
systemctl --user enable watcher@dotfiles.service
systemctl --user enable watcher@work-project.service
```

#### Disable Automatic Startup
```bash
# Disable automatic startup
systemctl --user disable watcher@myproject.service

# Service can still be started manually
systemctl --user start watcher@myproject.service
```

#### Check Enabled Services
```bash
# List enabled watcher services
systemctl --user list-unit-files 'watcher@*.service'

# Show only enabled services
systemctl --user list-unit-files 'watcher@*.service' | grep enabled
```

## Logging and Monitoring

### Log Locations

#### Systemd Journal
All service logs go to the systemd journal:
```bash
# View all logs for a service
journalctl --user -u watcher@myproject.service

# View logs from specific time
journalctl --user -u watcher@myproject.service --since "2023-12-01 10:00:00"

# View logs with specific priority
journalctl --user -u watcher@myproject.service -p info
```

#### Log Identifiers
Each service has a unique identifier:
- `watcher-config`: Default configuration
- `watcher-myproject`: Custom configuration
- `watcher-dotfiles`: Dotfiles configuration

#### Finding Logs
```bash
# Find logs by identifier
journalctl --user -t watcher-myproject

# Find all watcher logs
journalctl --user -t watcher-*

# Find logs across all services
journalctl --user -u 'watcher@*.service'
```

### Log Filtering

#### By Time
```bash
# Last hour
journalctl --user -u watcher@myproject.service --since "1 hour ago"

# Last day
journalctl --user -u watcher@myproject.service --since "1 day ago"

# Specific date range
journalctl --user -u watcher@myproject.service --since "2023-12-01" --until "2023-12-02"

# Since last boot
journalctl --user -u watcher@myproject.service -b
```

#### By Priority
```bash
# Errors only
journalctl --user -u watcher@myproject.service -p err

# Warnings and above
journalctl --user -u watcher@myproject.service -p warning

# Info and above
journalctl --user -u watcher@myproject.service -p info
```

#### By Keywords
```bash
# Filter for specific content
journalctl --user -u watcher@myproject.service | grep "commit"
journalctl --user -u watcher@myproject.service | grep "ERROR"
journalctl --user -u watcher@myproject.service | grep "push"
```

### Real-time Monitoring

#### Follow Logs
```bash
# Follow logs for specific service
journalctl --user -u watcher@myproject.service -f

# Follow logs for all watcher services
journalctl --user -u 'watcher@*.service' -f

# Follow with timestamps
journalctl --user -u watcher@myproject.service -f --show-cursor
```

#### Monitor Service Status
```bash
# Watch service status
watch systemctl --user status watcher@myproject.service

# Monitor all watcher services
watch 'systemctl --user list-units "watcher@*.service"'
```

## Troubleshooting

### Common Issues

#### Service Won't Start
1. **Check configuration validity**:
   ```bash
   watcher status myproject
   ```

2. **Check systemd status**:
   ```bash
   systemctl --user status watcher@myproject.service
   ```

3. **Check logs for errors**:
   ```bash
   journalctl --user -u watcher@myproject.service -p err
   ```

4. **Verify watcher command**:
   ```bash
   which watcher
   watcher --version
   ```

#### Service Crashes Repeatedly
1. **Check restart count**:
   ```bash
   systemctl --user status watcher@myproject.service
   ```

2. **View crash logs**:
   ```bash
   journalctl --user -u watcher@myproject.service --since "1 hour ago"
   ```

3. **Check configuration**:
   ```bash
   watcher test-ignore some-file.txt myproject
   ```

4. **Run manually for debugging**:
   ```bash
   watcher run myproject
   ```

#### Service Template Missing
1. **Reinstall service template**:
   ```bash
   watcher init myproject
   ```

2. **Check template exists**:
   ```bash
   ls -la ~/.config/systemd/user/watcher@.service
   ```

3. **Reload systemd daemon**:
   ```bash
   systemctl --user daemon-reload
   ```

### Debugging Steps

#### 1. Check Service Status
```bash
systemctl --user status watcher@myproject.service
```

#### 2. Check Configuration
```bash
watcher status myproject
```

#### 3. Check Logs
```bash
journalctl --user -u watcher@myproject.service -n 50
```

#### 4. Test Configuration
```bash
watcher run myproject
```

#### 5. Check Dependencies
```bash
# Check if user session is active
loginctl show-user $(whoami)

# Check if graphical session is available
systemctl --user status graphical-session.target
```

### Performance Monitoring

#### Resource Usage
```bash
# Check memory usage
systemctl --user show watcher@myproject.service --property=MemoryCurrent

# Check CPU usage
top -p $(systemctl --user show watcher@myproject.service --property=MainPID --value)
```

#### Service Statistics
```bash
# Show service statistics
systemctl --user show watcher@myproject.service

# Show specific properties
systemctl --user show watcher@myproject.service --property=ActiveState,SubState,MainPID
```

## Advanced Service Management

### Multiple Service Operations

#### Bulk Operations
```bash
# Start all watcher services
for service in $(systemctl --user list-unit-files 'watcher@*.service' --state=disabled --no-legend | cut -d' ' -f1); do
    systemctl --user start "$service"
done

# Stop all watcher services
systemctl --user stop 'watcher@*.service'

# Restart all watcher services
systemctl --user restart 'watcher@*.service'
```

#### Service Groups
Create systemd targets for grouped operations:

```ini
# ~/.config/systemd/user/watcher-work.target
[Unit]
Description=Work Watcher Services
Wants=watcher@work-api.service watcher@work-frontend.service
After=watcher@work-api.service watcher@work-frontend.service

[Install]
WantedBy=default.target
```

```bash
# Start all work services
systemctl --user start watcher-work.target

# Stop all work services  
systemctl --user stop watcher-work.target
```

### Service Health Monitoring

#### Health Checks
Create a monitoring script:

```bash
#!/bin/bash
# ~/.local/bin/watcher-health-check

for config in dotfiles work-api personal-blog; do
    if systemctl --user is-active watcher@$config.service >/dev/null; then
        echo "✅ $config is running"
    else
        echo "❌ $config is not running"
        systemctl --user start watcher@$config.service
    fi
done
```

#### Automatic Health Monitoring
Create a timer for regular health checks:

```ini
# ~/.config/systemd/user/watcher-health.service
[Unit]
Description=Watcher Health Check

[Service]
Type=oneshot
ExecStart=%h/.local/bin/watcher-health-check
```

```ini
# ~/.config/systemd/user/watcher-health.timer
[Unit]
Description=Run Watcher Health Check
Requires=watcher-health.service

[Timer]
OnCalendar=*:0/10
Persistent=true

[Install]
WantedBy=timers.target
```

```bash
# Enable health monitoring
systemctl --user enable watcher-health.timer
systemctl --user start watcher-health.timer
```

## Best Practices

### 1. Use Watcher Commands
Prefer `watcher up/down/status` over direct systemctl commands for better integration.

### 2. Enable Important Services
```bash
# Enable critical services to start on login
systemctl --user enable watcher@dotfiles.service
systemctl --user enable watcher@work-project.service
```

### 3. Monitor Service Health
```bash
# Check service status regularly
watcher ls

# Monitor logs for errors
journalctl --user -u 'watcher@*.service' -p err --since "1 day ago"
```

### 4. Use Descriptive Configuration Names
Service names will be `watcher@{config-name}.service`, so use clear names:
- `watcher@dotfiles.service`
- `watcher@work-api.service`
- `watcher@personal-blog.service`

### 5. Organize by Purpose
Group related services:
- Work services: `work-api`, `work-frontend`, `work-docs`
- Personal services: `dotfiles`, `personal-blog`, `home-automation`

### 6. Regular Maintenance
```bash
# Clean up old logs
journalctl --user --vacuum-time=30d

# Check for failed services
systemctl --user --failed

# Update service template when needed
watcher init --force
```