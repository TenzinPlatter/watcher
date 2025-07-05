"""
Configuration management for watcher
Handles loading and managing multiple configuration files
"""

import os
import yaml
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any


class ConfigManager:
    """Manages multiple watcher configurations"""
    
    def __init__(self) -> None:
        self.config_dir: Path = Path.home() / '.config' / 'watcher'
        self.templates_dir: Path = Path(__file__).parent.parent / 'templates'
        
    def ensure_config_dir(self) -> None:
        """Ensure the config directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    def get_config_path(self, config_name: str) -> Path:
        """Get the path to a specific config file"""
        if not config_name.endswith('.yaml'):
            config_name += '.yaml'
        return self.config_dir / config_name
        
    def get_global_ignore_path(self) -> Path:
        """Get the path to the global ignore file"""
        return self.config_dir / 'ignore'
        
    def list_configs(self) -> List[str]:
        """List all available config files"""
        if not self.config_dir.exists():
            return []
            
        configs = []
        for config_file in self.config_dir.glob('*.yaml'):
            configs.append(config_file.stem)
        return sorted(configs)
        
    def config_exists(self, config_name: str) -> bool:
        """Check if a config file exists"""
        return self.get_config_path(config_name).exists()
        
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file with fallback to defaults
        
        Args:
            config_name: Name of the config file (without .yaml extension)
            
        Returns:
            Dictionary containing configuration data
        """
        config_path = self.get_config_path(config_name)
        
        # Default configuration
        default_config = {
            'name': config_name,
            'watch_directory': '~/.dotfiles',
            'repo_directory': '~/.dotfiles',
            'commit_delay': 60,
            'fetch_interval': 600,
            'enable_notifications': True,
            'notify_on_commit': True,
            'notify_on_remote_changes': True,
            'auto_push': True,
            'respect_gitignore': True,
            'ignore_patterns': [],
            'ignore_files': []
        }
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
                # Merge user config with defaults
                config = {**default_config, **user_config}
                print(f"📄 Loaded configuration from {config_path}")
            else:
                config = default_config
                print(f"⚠️  Config file not found at {config_path}, using defaults")
        except Exception as e:
            print(f"❌ Error loading config file: {e}")
            print("   Using default configuration")
            config = default_config
        
        # Expand user paths
        config['watch_directory'] = os.path.expanduser(config['watch_directory'])
        config['repo_directory'] = os.path.expanduser(config['repo_directory'])
        
        # Expand paths in ignore_files
        expanded_ignore_files = []
        for ignore_file in config.get('ignore_files', []):
            expanded_ignore_files.append(os.path.expanduser(ignore_file))
        config['ignore_files'] = expanded_ignore_files
        
        return config
        
    def create_config(self, config_name: str, template_data: Optional[Dict[str, Any]] = None) -> Path:
        """
        Create a new config file from template
        
        Args:
            config_name: Name of the config file to create
            template_data: Optional template data to customize the config
            
        Returns:
            Path to the created config file
        """
        self.ensure_config_dir()
        config_path = self.get_config_path(config_name)
        
        if config_path.exists():
            print(f"⚠️  Config file already exists: {config_path}")
            return config_path
            
        # Load template
        template_path = self.templates_dir / 'config.yaml'
        if template_path.exists():
            with open(template_path, 'r') as f:
                config_data = yaml.safe_load(f)
        else:
            # Fallback to default config
            config_data = {
                'name': config_name,
                'watch_directory': '~/.dotfiles',
                'repo_directory': '~/.dotfiles',
                'commit_delay': 60,
                'fetch_interval': 600,
                'enable_notifications': True,
                'notify_on_commit': True,
                'notify_on_remote_changes': True,
                'auto_push': True,
                'respect_gitignore': True,
                'ignore_patterns': [],
                'ignore_files': []
            }
            
        # Apply template customizations
        if template_data:
            config_data.update(template_data)
            
        # Set the config name
        config_data['name'] = config_name
        
        # Write config file
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
            
        print(f"✅ Created config file: {config_path}")
        return config_path
        
    def ensure_global_ignore(self) -> Path:
        """Ensure the global ignore file exists"""
        self.ensure_config_dir()
        ignore_path = self.get_global_ignore_path()
        
        if ignore_path.exists():
            return ignore_path
            
        # Copy template ignore file
        template_ignore = self.templates_dir / 'ignore'
        if template_ignore.exists():
            shutil.copy2(template_ignore, ignore_path)
            print(f"✅ Created global ignore file: {ignore_path}")
        else:
            # Create basic ignore file
            with open(ignore_path, 'w') as f:
                f.write("# Global ignore patterns for watcher\n")
                f.write("# Add patterns here that should be ignored by all watchers\n\n")
                f.write(".git/\n")
                f.write("*.pyc\n")
                f.write("__pycache__/\n")
            print(f"✅ Created basic global ignore file: {ignore_path}")
            
        return ignore_path
        
    def validate_config(self, config_name: str) -> Dict[str, Any]:
        """
        Validate a configuration and return validation results
        
        Args:
            config_name: Name of the config to validate
            
        Returns:
            Dictionary with validation results
        """
        config = self.load_config(config_name)
        results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Check if watch directory exists
        watch_dir = Path(config['watch_directory'])
        if not watch_dir.exists():
            results['errors'].append(f"Watch directory does not exist: {watch_dir}")
            results['valid'] = False
            
        # Check if repo directory exists and is a git repository
        repo_dir = Path(config['repo_directory'])
        if not repo_dir.exists():
            results['errors'].append(f"Repository directory does not exist: {repo_dir}")
            results['valid'] = False
        elif not (repo_dir / '.git').exists():
            results['errors'].append(f"Repository directory is not a git repository: {repo_dir}")
            results['valid'] = False
            
        # Check ignore files
        for ignore_file in config.get('ignore_files', []):
            ignore_path = Path(ignore_file)
            if not ignore_path.exists():
                results['warnings'].append(f"Ignore file does not exist: {ignore_file}")
                
        # Check timing values
        if config.get('commit_delay', 0) < 0:
            results['errors'].append("commit_delay must be non-negative")
            results['valid'] = False
            
        if config.get('fetch_interval', 0) < 0:
            results['errors'].append("fetch_interval must be non-negative")
            results['valid'] = False
            
        return results
        
    def get_config_status(self, config_name: str) -> Dict[str, Any]:
        """Get status information for a config"""
        import subprocess
        
        status = {
            'name': config_name,
            'exists': self.config_exists(config_name),
            'service_active': False,
            'service_enabled': False,
            'watch_directory': None,
            'repo_directory': None
        }
        
        if status['exists']:
            config = self.load_config(config_name)
            status['watch_directory'] = config['watch_directory']
            status['repo_directory'] = config['repo_directory']
            
            # Check systemd service status
            service_name = f"watcher@{config_name}.service"
            try:
                # Check if service is active
                result = subprocess.run(
                    ['systemctl', '--user', 'is-active', service_name],
                    capture_output=True, text=True
                )
                status['service_active'] = result.returncode == 0
                
                # Check if service is enabled
                result = subprocess.run(
                    ['systemctl', '--user', 'is-enabled', service_name],
                    capture_output=True, text=True
                )
                status['service_enabled'] = result.returncode == 0
                
            except Exception:
                # If systemctl commands fail, assume service is not available
                pass
                
        return status