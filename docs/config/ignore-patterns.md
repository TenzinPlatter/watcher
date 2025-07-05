# Ignore Patterns Guide

Complete guide to understanding and using watcher's hierarchical ignore pattern system.

## Overview

Watcher uses a hierarchical ignore system that combines patterns from multiple sources to determine which files to ignore. This provides flexibility while maintaining consistency across projects.

## Ignore Hierarchy

Ignore patterns are applied in this order (higher priority overrides lower):

1. **Global Ignore File** (`~/.config/watcher/ignore`)
2. **Config Ignore Patterns** (in YAML config file)
3. **Additional Ignore Files** (referenced in config)
4. **Gitignore Files** (`.gitignore` files in the repository)

## Global Ignore File

### Location
```
~/.config/watcher/ignore
```

### Purpose
Contains patterns that should be ignored by ALL watcher instances across all projects.

### Example Global Ignore File
```gitignore
# Global ignore file for watcher
# This file contains patterns that should be ignored by all watcher instances

# Git internal files
.git/
.git\
/.git/
\.git\
index.lock
COMMIT_EDITMSG
HEAD.lock
refs/heads/
refs/remotes/
logs/HEAD
logs/refs/
objects/
hooks/
info/
packed-refs
config.lock
shallow.lock
modules/
ORIG_HEAD
FETCH_HEAD
MERGE_HEAD
CHERRY_PICK_HEAD

# Temporary files
.tmp_
__pycache__/
*.pyc
*.pyo
*.swp
*.swo
*.tmp
*~
*.bak

# Editor files
.vscode/
.idea/
*.sublime-*

# OS files
.DS_Store
Thumbs.db
desktop.ini

# Common build artifacts
build/
dist/
*.egg-info/
node_modules/
.cache/
.pytest_cache/
```

### Editing Global Ignore
```bash
# Edit global ignore file
watcher edit-ignore

# Or edit directly
nano ~/.config/watcher/ignore
```

## Config Ignore Patterns

### Location
In your project's YAML configuration file under `ignore_patterns`.

### Purpose
Project-specific ignore patterns that apply only to that watcher instance.

### Example Configuration
```yaml
# ~/.config/watcher/myproject.yaml
name: "myproject"
watch_directory: "~/projects/myapp"
repo_directory: "~/projects/myapp"

ignore_patterns:
  - "*.log"           # All log files
  - "logs/"           # Logs directory
  - "build/"          # Build directory
  - "dist/"           # Distribution directory
  - ".env.local"      # Local environment file
  - "coverage/"       # Test coverage directory
  - "*.draft"         # Draft files
  - "temp_*"          # Temporary files with prefix
```

### Pattern Types

#### File Extensions
```yaml
ignore_patterns:
  - "*.log"          # All .log files
  - "*.tmp"          # All .tmp files
  - "*.swp"          # Vim swap files
  - "*.bak"          # Backup files
```

#### Directories
```yaml
ignore_patterns:
  - "build/"         # build directory
  - "dist/"          # dist directory
  - "logs/"          # logs directory
  - ".cache/"        # cache directory
```

#### Specific Files
```yaml
ignore_patterns:
  - ".env.local"     # Specific file
  - "config.json"    # Another specific file
  - "debug.txt"      # Debug file
```

#### Wildcard Patterns
```yaml
ignore_patterns:
  - "temp_*"         # Files starting with temp_
  - "*_backup"       # Files ending with _backup
  - "test_*.py"      # Python test files
```

## Additional Ignore Files

### Purpose
Reference external ignore files that contain patterns for specific languages, frameworks, or shared across projects.

### Configuration
```yaml
# In your config YAML file
ignore_files:
  - "~/.config/watcher/nodejs-ignore"
  - "~/.config/watcher/python-ignore"
  - ".watcher-ignore"
  - "~/shared/common-ignore"
```

### Example Language-Specific Ignore Files

#### Node.js Ignore File
```bash
# ~/.config/watcher/nodejs-ignore
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
.parcel-cache/
.next/
.nuxt/
.vuepress/dist/
.serverless/
.fusebox/
.dynamodb/
.tern-port
```

#### Python Ignore File
```bash
# ~/.config/watcher/python-ignore
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
.mypy_cache/
.dmypy.json
dmypy.json
```

#### Go Ignore File
```bash
# ~/.config/watcher/go-ignore
# Binaries for programs and plugins
*.exe
*.exe~
*.dll
*.so
*.dylib

# Test binary, built with `go test -c`
*.test

# Output of the go coverage tool
*.out

# Dependency directories
vendor/

# Go workspace file
go.work
```

### Creating Language-Specific Ignore Files

```bash
# Create Node.js ignore file
cat > ~/.config/watcher/nodejs-ignore << 'EOF'
node_modules/
npm-debug.log*
dist/
build/
coverage/
.env.local
EOF

# Create Python ignore file
cat > ~/.config/watcher/python-ignore << 'EOF'
__pycache__/
*.pyc
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
EOF

# Reference them in your configs
echo "ignore_files:" >> ~/.config/watcher/myproject.yaml
echo "  - \"~/.config/watcher/nodejs-ignore\"" >> ~/.config/watcher/myproject.yaml
```

## Gitignore Integration

### Purpose
Respect existing `.gitignore` files in your repository to maintain consistency with git's ignore behavior.

### Configuration
```yaml
# Enable gitignore respect (default: true)
respect_gitignore: true

# Disable gitignore respect
respect_gitignore: false
```

### How It Works
When `respect_gitignore: true`:
1. Watcher walks up from each file to the repository root
2. Checks for `.gitignore` files in each directory
3. Applies patterns from found `.gitignore` files
4. Combines with watcher's own ignore patterns

### Example Project Structure
```
~/projects/myapp/
├── .gitignore                 # Root gitignore
├── src/
│   ├── components/
│   │   └── .gitignore        # Component-specific gitignore
│   └── utils/
├── tests/
│   └── .gitignore            # Test-specific gitignore
└── docs/
```

Each `.gitignore` file applies to files in its directory and subdirectories.

## Pattern Syntax

Watcher uses gitignore-style pattern syntax:

### Basic Patterns
```gitignore
# Comments start with #
# Blank lines are ignored

# Ignore specific file
filename.txt

# Ignore all files with extension
*.log

# Ignore directory
dirname/

# Ignore files starting with prefix
temp_*

# Ignore files ending with suffix
*_backup
```

### Advanced Patterns
```gitignore
# Ignore files in any subdirectory
**/logs/

# Ignore files only in root
/config.json

# Character ranges
[Dd]ebug.txt

# Question mark wildcard
test?.py

# Negation (currently not fully supported)
!important.log
```

### Directory vs File Patterns
```gitignore
# Directory (trailing slash)
build/          # Ignores build directory and all contents

# File or directory (no trailing slash)  
build           # Ignores build file OR directory
```

## Testing Ignore Patterns

### Command Line Testing
```bash
# Test if a file would be ignored
watcher test-ignore path/to/file.txt myproject

# Test multiple files
watcher test-ignore .git/index myproject
watcher test-ignore src/main.py myproject
watcher test-ignore node_modules/package/index.js myproject
```

### Example Test Output
```bash
$ watcher test-ignore ".git/index" myproject
File: .git/index
Config: myproject
Result: ❌ IGNORED
Matched by:
  - global: .git/

$ watcher test-ignore "src/main.py" myproject
File: src/main.py
Config: myproject
Result: ✅ NOT IGNORED
```

### Testing Different Sources
```bash
# Test against different ignore sources
watcher test-ignore "build/output.js" myproject
# Might show:
# Matched by:
#   - config: build/
#   - gitignore

watcher test-ignore "*.log" myproject
# Might show:
# Matched by:
#   - global: *.log
#   - additional: *.log
```

## Common Ignore Patterns

### Development Files
```gitignore
# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids/
*.pid
*.seed
*.pid.lock

# Coverage directory used by tools like istanbul
coverage/
.nyc_output/

# Dependency directories
node_modules/
vendor/

# Build outputs
build/
dist/
out/
.next/
.nuxt/
```

### Language-Specific

#### JavaScript/Node.js
```gitignore
node_modules/
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
```

#### Python
```gitignore
__pycache__/
*.py[cod]
*$py.class
build/
dist/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
.tox/
.env
.venv
venv/
```

#### Go
```gitignore
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
vendor/
go.work
```

#### Rust
```gitignore
target/
Cargo.lock
*.pdb
```

### Editor and IDE Files
```gitignore
# VSCode
.vscode/
*.code-workspace

# IntelliJ
.idea/
*.iml
*.iws
*.ipr

# Vim
*.swp
*.swo
*~

# Emacs
*~
\#*\#
/.emacs.desktop
/.emacs.desktop.lock
*.elc
auto-save-list
tramp
.\#*

# Sublime Text
*.sublime-project
*.sublime-workspace
```

### OS Files
```gitignore
# macOS
.DS_Store
.AppleDouble
.LSOverride
._*

# Windows
Thumbs.db
Thumbs.db:encryptable
ehthumbs.db
ehthumbs_vista.db
Desktop.ini
$RECYCLE.BIN/

# Linux
*~
.fuse_hidden*
.directory
.Trash-*
.nfs*
```

## Best Practices

### 1. Use Global Ignore for Universal Patterns
Put patterns that apply to ALL projects in the global ignore file:
```gitignore
# In ~/.config/watcher/ignore
.git/
.DS_Store
*.swp
__pycache__/
node_modules/
```

### 2. Use Config Patterns for Project-Specific Needs
```yaml
# In project config
ignore_patterns:
  - "logs/"          # Project uses logs/ directory
  - "*.secret"       # Project has .secret files
  - "temp_data/"     # Project-specific temp directory
```

### 3. Create Language-Specific Ignore Files
```bash
# Create once, use many times
~/.config/watcher/nodejs-ignore
~/.config/watcher/python-ignore
~/.config/watcher/go-ignore
```

### 4. Use Project-Local Ignore Files
```yaml
# Reference project-local ignore
ignore_files:
  - ".watcher-ignore"    # In project root
```

### 5. Test Your Patterns
```bash
# Always test important files
watcher test-ignore "important-file.txt" myproject
watcher test-ignore "build/output.js" myproject
```

### 6. Document Complex Patterns
```yaml
ignore_patterns:
  # Ignore all build artifacts
  - "build/"
  - "dist/"
  # Ignore temporary files from our custom build system
  - "temp_build_*"
  # Ignore local development environment files
  - ".env.local"
```

### 7. Keep Patterns Minimal
- Don't duplicate patterns between global and project config
- Use the most specific location for each pattern
- Avoid overly broad patterns that might catch important files

## Troubleshooting Ignore Patterns

### File Still Being Watched
1. **Test the pattern**:
   ```bash
   watcher test-ignore "path/to/file" myproject
   ```

2. **Check pattern syntax**:
   - Ensure directory patterns end with `/`
   - Check for typos in patterns
   - Verify file paths are relative to watch directory

3. **Check ignore hierarchy**:
   - Global ignore file
   - Config ignore patterns
   - Additional ignore files
   - Gitignore files

### Pattern Not Working
1. **Verify pattern location**:
   - Is it in the right ignore file?
   - Is the ignore file referenced in config?

2. **Check pattern syntax**:
   ```gitignore
   # Correct
   build/          # Directory
   *.log           # File extension
   temp_*          # Prefix pattern
   
   # Incorrect
   build           # Ambiguous
   .log            # Missing wildcard
   temp*           # Missing underscore
   ```

3. **Test incrementally**:
   ```bash
   # Test specific pattern
   echo "test.log" | grep -E "*.log"
   
   # Test in watcher
   watcher test-ignore "test.log" myproject
   ```

### Performance Issues
1. **Avoid overly complex patterns**:
   ```gitignore
   # Good
   build/
   *.log
   
   # Potentially slow
   **/**/temp/**/*
   ```

2. **Use specific patterns**:
   ```gitignore
   # Good
   node_modules/
   
   # Too broad
   */
   ```

3. **Monitor ignored file count**:
   - Check watcher logs for excessive ignore pattern matching
   - Consider splitting large projects into multiple watchers