# CLI Commands Reference

Complete reference for all Watcher CLI commands.

## Global Options

All commands support these global options:

```bash
watcher --version    # Show version and exit
watcher --help       # Show help and exit
```

## Commands Overview

| Command | Description | Config Required |
|---------|-------------|-----------------|
| `init` | Initialize new configuration | No |
| `up` | Start watcher service | Yes |
| `down` | Stop watcher service | Yes |
| `status` | Show service status | Yes |
| `logs` | Show service logs | Yes |
| `ls` | List all configurations | No |
| `remove` | Remove configuration and associated files | Yes |
| `edit-config` | Edit configuration file | Yes |
| `edit-ignore` | Edit global ignore file | No |
| `run` | Run watcher (used by systemd) | Yes |
| `test-ignore` | Test ignore patterns | Yes |

---

## `watcher init`

Initialize a new watcher configuration.

### Syntax
```bash
watcher init [CONFIG_NAME] [OPTIONS]
```

### Arguments
- `CONFIG_NAME` - Name of the configuration (default: `config`)

### Options
- `-w, --watch-dir TEXT` - Directory to watch
- `-r, --repo-dir TEXT` - Git repository directory  
- `-d, --commit-delay INTEGER` - Commit delay in seconds
- `--help` - Show help

### Examples
```bash
# Initialize default configuration
watcher init

# Initialize with custom name and settings
watcher init myproject --watch-dir ~/projects/myapp --commit-delay 30

# Initialize dotfiles watcher
watcher init dotfiles --watch-dir ~/.dotfiles --repo-dir ~/.dotfiles
```

### What it does
1. Creates `~/.config/watcher/` directory if it doesn't exist
2. Creates global ignore file at `~/.config/watcher/ignore`
3. Creates configuration file at `~/.config/watcher/{CONFIG_NAME}.yaml`
4. Installs systemd service template at `~/.config/systemd/user/watcher@.service`
5. Reloads systemd daemon

---

## `watcher up`

Enable and start the watcher service for a configuration.

### Syntax
```bash
watcher up [CONFIG_NAME]
```

### Arguments
- `CONFIG_NAME` - Name of the configuration (default: `config`)

### Examples
```bash
# Start default configuration
watcher up

# Start specific configuration
watcher up myproject
```

### What it does
1. Validates the configuration file exists and is valid
2. Enables the systemd service (`watcher@{CONFIG_NAME}.service`)
3. Starts the systemd service
4. Reloads systemd daemon

### Error Handling
- Exits with error if configuration doesn't exist
- Exits with error if configuration is invalid
- Shows validation warnings but continues if non-critical

---

## `watcher down`

Disable and stop the watcher service for a configuration.

### Syntax
```bash
watcher down [CONFIG_NAME]
```

### Arguments
- `CONFIG_NAME` - Name of the configuration (default: `config`)

### Examples
```bash
# Stop default configuration
watcher down

# Stop specific configuration
watcher down myproject
```

### What it does
1. Stops the systemd service (`watcher@{CONFIG_NAME}.service`)
2. Disables the systemd service

---

## `watcher status`

Show detailed status information for a configuration.

### Syntax
```bash
watcher status [CONFIG_NAME]
```

### Arguments
- `CONFIG_NAME` - Name of the configuration (default: `config`)

### Examples
```bash
# Show status of default configuration
watcher status

# Show status of specific configuration
watcher status myproject
```

### Output
Shows:
- Configuration name and file location
- Watch directory and repository directory
- Service status (ACTIVE/INACTIVE)
- Service enabled status (enabled/disabled)
- Detailed systemd status output
- Configuration validation results

---

## `watcher logs`

Show logs for a watcher service.

### Syntax
```bash
watcher logs [CONFIG_NAME] [OPTIONS]
```

### Arguments
- `CONFIG_NAME` - Name of the configuration (default: `config`)

### Options
- `-f, --follow` - Follow log output (like `tail -f`)
- `-n, --lines INTEGER` - Number of lines to show (default: 50)
- `--help` - Show help

### Examples
```bash
# Show last 50 lines of logs
watcher logs myproject

# Follow logs in real-time
watcher logs myproject -f

# Show last 100 lines
watcher logs myproject -n 100

# Follow logs for default config
watcher logs -f
```

### What it does
- Uses `journalctl --user -u watcher@{CONFIG_NAME}.service` to show logs
- Supports all journalctl features through the systemd integration

---

## `watcher ls`

List all available configurations and their status.

### Syntax
```bash
watcher ls
```

### Examples
```bash
watcher ls
```

### Output
Shows a table with:
- Configuration name
- Service status (✅ ACTIVE / ❌ INACTIVE)
- Enabled status (enabled/disabled)
- Watch directory path

Example output:
```
Available configurations:

  config          ✅ ACTIVE (enabled)
    Watch: /home/user/.dotfiles

  myproject       ❌ INACTIVE (disabled)
    Watch: /home/user/projects/myapp

  work-stuff      ✅ ACTIVE (enabled)
    Watch: /home/user/work/repo
```

---

## `watcher remove`

Remove a configuration and all associated files.

### Syntax
```bash
watcher remove CONFIG_NAME [OPTIONS]
```

### Arguments
- `CONFIG_NAME` - Name of the configuration to remove (required)

### Options
- `--force` - Skip confirmation prompt
- `--help` - Show help

### Examples
```bash
# Remove a configuration (with confirmation)
watcher remove myproject

# Remove without confirmation
watcher remove myproject --force

# Remove multiple configurations
watcher remove work-api --force
watcher remove personal-blog --force
```

### What it does
1. Stops the systemd service if running
2. Disables the systemd service
3. Removes the configuration file (`~/.config/watcher/{CONFIG_NAME}.yaml`)
4. Removes any project-specific ignore files referenced in the config
5. Shows confirmation before deletion (unless `--force` is used)

### Safety Features
- Prompts for confirmation before deletion
- Shows what will be removed before proceeding
- Stops and disables service before file removal
- Does NOT remove the global ignore file or systemd service template

### Error Handling
- Exits with error if configuration doesn't exist
- Continues if systemd operations fail (file removal still proceeds)
- Shows warnings for files that couldn't be removed

---

## `watcher edit-config`

Open a configuration file in your default editor.

### Syntax
```bash
watcher edit-config [CONFIG_NAME]
```

### Arguments
- `CONFIG_NAME` - Name of the configuration (default: `config`)

### Examples
```bash
# Edit default configuration
watcher edit-config

# Edit specific configuration
watcher edit-config myproject
```

### Editor Selection
Uses editors in this order of preference:
1. `$EDITOR` environment variable
2. `$VISUAL` environment variable  
3. First available: `nano`, `vim`, `vi`, `emacs`, `code`
4. Falls back to `nano`

### What it does
1. Checks if configuration exists
2. Opens the YAML file in your preferred editor
3. Shows file path if editor is not available

---

## `watcher edit-ignore`

Open the global ignore file in your default editor.

### Syntax
```bash
watcher edit-ignore
```

### Examples
```bash
watcher edit-ignore
```

### What it does
1. Ensures global ignore file exists at `~/.config/watcher/ignore`
2. Opens the file in your preferred editor
3. Creates basic ignore file if it doesn't exist

---

## `watcher run`

Run the watcher for a specific configuration. This command is used internally by the systemd service.

### Syntax
```bash
watcher run CONFIG_NAME
```

### Arguments
- `CONFIG_NAME` - Name of the configuration (required)

### Examples
```bash
# Run watcher for myproject (used by systemd)
watcher run myproject
```

### What it does
1. Loads the specified configuration
2. Validates directories and git repository
3. Starts the file monitoring loop
4. Runs until interrupted or error occurs

**Note**: This command is primarily used by systemd services. Use `watcher up/down` for manual service management.

---

## `watcher test-ignore`

Test whether a file would be ignored by the watcher.

### Syntax
```bash
watcher test-ignore FILE_PATH [CONFIG_NAME]
```

### Arguments
- `FILE_PATH` - Path to the file to test (required)
- `CONFIG_NAME` - Name of the configuration (default: `config`)

### Examples
```bash
# Test if a file would be ignored
watcher test-ignore ".git/index" myproject
watcher test-ignore "src/main.py" myproject
watcher test-ignore "node_modules/package/index.js"
```

### Output
Shows:
- File path being tested
- Configuration name
- Result: ✅ NOT IGNORED or ❌ IGNORED
- If ignored, shows which ignore source matched:
  - `global: .git/` (from global ignore file)
  - `config: *.log` (from config ignore_patterns)
  - `additional: node_modules/` (from additional ignore files)
  - `gitignore` (from .gitignore files)

Example output:
```bash
$ watcher test-ignore ".git/index" myproject
File: .git/index
Config: myproject
Result: ❌ IGNORED
Matched by:
  - global: .git/
```

---

## Exit Codes

All commands use standard exit codes:

- `0` - Success
- `1` - General error (invalid config, command failed, etc.)
- `2` - Invalid command line arguments

## Environment Variables

### Editor Selection
- `EDITOR` - Preferred editor for `edit-config` and `edit-ignore`
- `VISUAL` - Alternative editor preference

### Systemd Integration
The CLI automatically handles systemd user services and doesn't require additional environment configuration.

## Configuration File Location

All commands expect configuration files in:
```
~/.config/watcher/{CONFIG_NAME}.yaml
```

The global ignore file is located at:
```
~/.config/watcher/ignore
```

## Service Template Location

The systemd service template is installed at:
```
~/.config/systemd/user/watcher@.service
```