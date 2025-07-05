"""
Command line interface for watcher
Provides commands for managing multiple watcher instances
"""

import sys
import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

import click

from .config import ConfigManager
from .core import run_watcher


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Watcher - Multi-directory file watcher with automated git commits"""
    pass


@main.command()
@click.argument('config_name', default='config')
@click.option('--watch-dir', '-w', help='Directory to watch')
@click.option('--repo-dir', '-r', help='Git repository directory')
@click.option('--commit-delay', '-d', type=int, help='Commit delay in seconds')
def init(config_name: str, watch_dir: Optional[str], repo_dir: Optional[str], commit_delay: Optional[int]) -> None:
    """Initialize watcher configuration and systemd service"""
    config_manager = ConfigManager()
    
    # Ensure global ignore file exists
    config_manager.ensure_global_ignore()
    
    # Prepare template data
    template_data: Dict[str, Any] = {}
    if watch_dir:
        template_data['watch_directory'] = watch_dir
    if repo_dir:
        template_data['repo_directory'] = repo_dir
    if commit_delay:
        template_data['commit_delay'] = commit_delay
    
    # Create config file
    config_path = config_manager.create_config(config_name, template_data)
    
    # Install systemd service template
    _install_systemd_service()
    
    click.echo(f"✅ Initialized watcher configuration: {config_name}")
    click.echo(f"   Config file: {config_path}")
    click.echo(f"   Global ignore: {config_manager.get_global_ignore_path()}")
    click.echo("")
    click.echo("Next steps:")
    click.echo(f"  1. Edit config: watcher edit-config {config_name}")
    click.echo(f"  2. Start watcher: watcher up {config_name}")


@main.command()
@click.argument('config_name', default='config')
def up(config_name: str) -> None:
    """Enable and start watcher service for specified config"""
    config_manager = ConfigManager()
    
    # Check if config exists
    if not config_manager.config_exists(config_name):
        click.echo(f"❌ Config '{config_name}' does not exist. Run 'watcher init {config_name}' first.")
        sys.exit(1)
    
    # Validate config
    validation = config_manager.validate_config(config_name)
    if not validation['valid']:
        click.echo(f"❌ Config '{config_name}' is invalid:")
        for error in validation['errors']:
            click.echo(f"   {error}")
        sys.exit(1)
    
    # Show warnings
    for warning in validation['warnings']:
        click.echo(f"⚠️  {warning}")
    
    service_name = f"watcher@{config_name}.service"
    
    try:
        # Enable and start the service
        subprocess.run(['systemctl', '--user', 'enable', service_name], check=True, capture_output=True)
        subprocess.run(['systemctl', '--user', 'start', service_name], check=True, capture_output=True)
        
        # Reload daemon to ensure changes are picked up
        subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True, capture_output=True)
        
        click.echo(f"✅ Started watcher service: {service_name}")
        click.echo(f"   View logs: watcher logs {config_name}")
        click.echo(f"   Check status: watcher status {config_name}")
        
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Failed to start service: {e}")
        sys.exit(1)
    except FileNotFoundError:
        click.echo("❌ systemctl not found. Make sure systemd is installed.")
        sys.exit(1)


@main.command()
@click.argument('config_name', default='config')
def down(config_name: str) -> None:
    """Disable and stop watcher service for specified config"""
    service_name = f"watcher@{config_name}.service"
    
    try:
        # Stop and disable the service
        subprocess.run(['systemctl', '--user', 'stop', service_name], check=True, capture_output=True)
        subprocess.run(['systemctl', '--user', 'disable', service_name], check=True, capture_output=True)
        
        click.echo(f"✅ Stopped watcher service: {service_name}")
        
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Failed to stop service: {e}")
        sys.exit(1)
    except FileNotFoundError:
        click.echo("❌ systemctl not found. Make sure systemd is installed.")
        sys.exit(1)


@main.command()
@click.argument('config_name', default='config')
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--lines', '-n', type=int, default=50, help='Number of lines to show')
def logs(config_name: str, follow: bool, lines: int) -> None:
    """Show logs for watcher service"""
    service_name = f"watcher@{config_name}.service"
    
    cmd = ['journalctl', '--user', '-u', service_name, '-n', str(lines)]
    if follow:
        cmd.append('-f')
    
    try:
        subprocess.run(cmd)
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Failed to show logs: {e}")
        sys.exit(1)
    except FileNotFoundError:
        click.echo("❌ journalctl not found. Make sure systemd is installed.")
        sys.exit(1)
    except KeyboardInterrupt:
        # Normal exit when following logs
        pass


@main.command()
@click.argument('config_name', default='config')
def status(config_name: str) -> None:
    """Show status of watcher service"""
    config_manager = ConfigManager()
    status_info = config_manager.get_config_status(config_name)
    
    if not status_info['exists']:
        click.echo(f"❌ Config '{config_name}' does not exist")
        return
    
    click.echo(f"Config: {config_name}")
    click.echo(f"  Watch directory: {status_info['watch_directory']}")
    click.echo(f"  Repo directory: {status_info['repo_directory']}")
    
    # Show service status
    service_name = f"watcher@{config_name}.service"
    
    if status_info['service_active']:
        click.echo(f"  Service: ✅ ACTIVE")
    else:
        click.echo(f"  Service: ❌ INACTIVE")
    
    if status_info['service_enabled']:
        click.echo(f"  Enabled: ✅ YES")
    else:
        click.echo(f"  Enabled: ❌ NO")
    
    # Show detailed systemd status
    try:
        result = subprocess.run(
            ['systemctl', '--user', 'status', service_name, '--no-pager', '-l'],
            capture_output=True, text=True
        )
        click.echo(f"\nSystemd status:")
        click.echo(result.stdout)
    except subprocess.CalledProcessError:
        pass
    except FileNotFoundError:
        click.echo("❌ systemctl not found. Make sure systemd is installed.")


@main.command()
def ls() -> None:
    """List all available configs and their status"""
    config_manager = ConfigManager()
    configs = config_manager.list_configs()
    
    if not configs:
        click.echo("No configurations found.")
        click.echo("Run 'watcher init' to create your first configuration.")
        return
    
    click.echo("Available configurations:")
    click.echo("")
    
    for config_name in configs:
        status_info = config_manager.get_config_status(config_name)
        
        # Status indicators
        service_status = "✅ ACTIVE" if status_info['service_active'] else "❌ INACTIVE"
        enabled_status = "enabled" if status_info['service_enabled'] else "disabled"
        
        click.echo(f"  {config_name:<15} {service_status} ({enabled_status})")
        click.echo(f"    Watch: {status_info['watch_directory']}")
        click.echo("")


@main.command()
@click.argument('config_name', default='config')
def edit_config(config_name: str) -> None:
    """Edit configuration file"""
    config_manager = ConfigManager()
    
    if not config_manager.config_exists(config_name):
        click.echo(f"❌ Config '{config_name}' does not exist. Run 'watcher init {config_name}' first.")
        sys.exit(1)
    
    config_path = config_manager.get_config_path(config_name)
    editor = _get_editor()
    
    try:
        subprocess.run([editor, str(config_path)], check=True)
    except subprocess.CalledProcessError:
        click.echo(f"❌ Failed to open editor: {editor}")
        sys.exit(1)
    except FileNotFoundError:
        click.echo(f"❌ Editor not found: {editor}")
        click.echo(f"   Config file location: {config_path}")
        sys.exit(1)


@main.command()
def edit_ignore() -> None:
    """Edit global ignore file"""
    config_manager = ConfigManager()
    ignore_path = config_manager.ensure_global_ignore()
    editor = _get_editor()
    
    try:
        subprocess.run([editor, str(ignore_path)], check=True)
    except subprocess.CalledProcessError:
        click.echo(f"❌ Failed to open editor: {editor}")
        sys.exit(1)
    except FileNotFoundError:
        click.echo(f"❌ Editor not found: {editor}")
        click.echo(f"   Ignore file location: {ignore_path}")
        sys.exit(1)


@main.command()
@click.argument('config_name')
def run(config_name: str) -> None:
    """Run watcher for specified config (used by systemd service)"""
    try:
        run_watcher(config_name)
    except KeyboardInterrupt:
        click.echo("\n🛑 Watcher stopped by user")
    except Exception as e:
        click.echo(f"❌ Watcher error: {e}")
        sys.exit(1)


@main.command()
@click.argument('file_path')
@click.argument('config_name', default='config')
def test_ignore(file_path: str, config_name: str) -> None:
    """Test if a file would be ignored by the specified config"""
    config_manager = ConfigManager()
    
    if not config_manager.config_exists(config_name):
        click.echo(f"❌ Config '{config_name}' does not exist")
        sys.exit(1)
    
    config = config_manager.load_config(config_name)
    
    from .ignore import IgnoreManager
    ignore_manager = IgnoreManager(config_name, config)
    
    result = ignore_manager.test_pattern(file_path)
    
    click.echo(f"File: {file_path}")
    click.echo(f"Config: {config_name}")
    
    if result['ignored']:
        click.echo("Result: ❌ IGNORED")
        click.echo("Matched by:")
        for match in result['matched_by']:
            click.echo(f"  - {match}")
    else:
        click.echo("Result: ✅ NOT IGNORED")


def _install_systemd_service() -> None:
    """Install systemd service template"""
    service_dir = Path.home() / '.config' / 'systemd' / 'user'
    service_dir.mkdir(parents=True, exist_ok=True)
    
    service_file = service_dir / 'watcher@.service'
    
    # Check if service file already exists
    if service_file.exists():
        return
    
    # Create service file content
    service_content = f"""[Unit]
Description=Watcher for %i configuration
After=graphical-session.target

[Service]
Type=simple
ExecStart=watcher run %i
WorkingDirectory=%h
Restart=always
RestartSec=10
Environment=HOME=%h
Environment=PATH=/usr/local/bin:/usr/bin:/bin:{Path.home() / '.local' / 'bin'}

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=watcher-%i

[Install]
WantedBy=default.target
"""
    
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    # Reload systemd daemon
    try:
        subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True, capture_output=True)
        click.echo(f"✅ Installed systemd service template: {service_file}")
    except subprocess.CalledProcessError as e:
        click.echo(f"⚠️  Service file created but failed to reload daemon: {e}")
    except FileNotFoundError:
        click.echo(f"⚠️  Service file created but systemctl not found: {service_file}")


def _get_editor() -> str:
    """Get the preferred editor"""
    import os
    
    # Try environment variables
    for var in ['EDITOR', 'VISUAL']:
        editor = os.environ.get(var)
        if editor and shutil.which(editor):
            return editor
    
    # Try common editors
    for editor in ['nano', 'vim', 'vi', 'emacs', 'code']:
        if shutil.which(editor):
            return editor
    
    # Fallback
    return 'nano'


if __name__ == '__main__':
    main()