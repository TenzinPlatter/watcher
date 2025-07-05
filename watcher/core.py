"""
Core file watcher functionality
Handles git operations and file monitoring for a single configuration
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .config import ConfigManager
from .ignore import IgnoreManager


class GitCommitHandler(FileSystemEventHandler):
    """Handles file system events and manages git commits with intelligent squashing"""
    
    def __init__(self, config_name: str) -> None:
        self.config_name: str = config_name
        self.config_manager: ConfigManager = ConfigManager()
        self.config: Dict[str, Any] = self.config_manager.load_config(config_name)
        
        # Initialize paths
        self.watch_dir: Path = Path(self.config['watch_directory']).expanduser().resolve()
        self.repo_dir: Path = Path(self.config['repo_directory']).expanduser().resolve()
        
        # Initialize ignore manager
        self.ignore_manager: IgnoreManager = IgnoreManager(config_name, self.config)
        
        # Get submodules
        self.submodules: List[Path] = self._get_submodules()
        
        # Threading and timing
        self.pending_commits: Dict[str, Set[str]] = {}  # Track pending commits per directory
        self.commit_timers: Dict[str, threading.Timer] = {}  # Track active timers per directory
        self.timer_lock: threading.Lock = threading.Lock()  # Thread safety for timer operations
        self.fetch_timer: Optional[threading.Timer] = None  # Timer for periodic fetching
        
        # Initialize
        self._commit_existing_changes()
        self.start_fetch_timer()
        
    def _run_git_command(self, cmd: List[str], cwd: Union[str, Path], description: str = "Git command") -> subprocess.CompletedProcess[str]:
        """Run a git command with proper error logging"""
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True
            )
            
            # Log command details if it fails
            if result.returncode != 0:
                cmd_str = ' '.join(cmd)
                print(f"❌ {description} failed: {cmd_str}")
                print(f"   Working directory: {cwd}")
                print(f"   Return code: {result.returncode}")
                if result.stdout.strip():
                    print(f"   STDOUT: {result.stdout.strip()}")
                if result.stderr.strip():
                    print(f"   STDERR: {result.stderr.strip()}")
            
            return result
            
        except subprocess.CalledProcessError as e:
            cmd_str = ' '.join(cmd)
            print(f"❌ {description} subprocess error: {cmd_str}")
            print(f"   Working directory: {cwd}")
            print(f"   Exception: {e}")
            raise
        except Exception as e:
            cmd_str = ' '.join(cmd)
            print(f"❌ {description} unexpected error: {cmd_str}")
            print(f"   Working directory: {cwd}")
            print(f"   Exception: {e}")
            raise
        
    def _get_submodules(self) -> List[Path]:
        """Get list of submodule paths"""
        try:
            result = self._run_git_command(
                ['git', 'submodule', 'foreach', '--quiet', 'echo $sm_path'],
                self.repo_dir,
                "Get submodules"
            )
            if result.returncode == 0:
                return [Path(self.repo_dir / line.strip()) for line in result.stdout.strip().split('\n') if line.strip()]
            else:
                return []
        except Exception:
            return []
    
    def _is_in_submodule(self, file_path: Union[str, Path]) -> bool:
        """Check if file is in a submodule"""
        file_path = Path(file_path).resolve()
        return any(file_path.is_relative_to(submodule) for submodule in self.submodules)
    
    def _get_submodule_for_file(self, file_path: Union[str, Path]) -> Optional[Path]:
        """Get the submodule directory for a file"""
        file_path = Path(file_path).resolve()
        for submodule in self.submodules:
            if file_path.is_relative_to(submodule):
                return submodule
        return None
    
    def _should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded from monitoring"""
        return self.ignore_manager.should_ignore(file_path)
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events"""
        if event.is_directory:
            return
        self._handle_file_change(event.src_path, "modified")
        
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events"""
        if event.is_directory:
            return
        self._handle_file_change(event.src_path, "created")
        
    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events"""
        if event.is_directory:
            return
        self._handle_file_change(event.src_path, "deleted")
        
    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file move events"""
        if event.is_directory:
            return
        if hasattr(event, 'dest_path'):
            self._handle_file_change(event.dest_path, "moved")
    
    def _handle_file_change(self, file_path: str, change_type: str) -> None:
        """Handle a file change event"""
        # Check if file should be excluded
        if self._should_exclude_file(file_path):
            return
            
        file_path = Path(file_path).resolve()
        
        # Determine which repository this change belongs to
        if self._is_in_submodule(file_path):
            submodule_dir = self._get_submodule_for_file(file_path)
            if submodule_dir:
                target_dir = submodule_dir
        else:
            target_dir = self.repo_dir
            
        dir_key = str(target_dir)
        
        # Add to pending commits
        with self.timer_lock:
            if dir_key not in self.pending_commits:
                self.pending_commits[dir_key] = set()
            self.pending_commits[dir_key].add(str(file_path))
            
            # Cancel existing timer for this directory
            if dir_key in self.commit_timers:
                self.commit_timers[dir_key].cancel()
                
            # Start new timer
            timer = threading.Timer(self.config['commit_delay'], self._execute_delayed_commit, [dir_key])
            self.commit_timers[dir_key] = timer
            timer.start()
            
            change_count = len(self.pending_commits[dir_key])
            print(f"⏰ Scheduled commit for {target_dir.name} in {self.config['commit_delay']} seconds ({change_count} changes)")
    
    def _execute_delayed_commit(self, dir_key: str) -> None:
        """Execute a delayed commit for a directory"""
        with self.timer_lock:
            if dir_key not in self.pending_commits:
                return
                
            changed_files = self.pending_commits[dir_key].copy()
            del self.pending_commits[dir_key]
            
            if dir_key in self.commit_timers:
                del self.commit_timers[dir_key]
                
        target_dir = Path(dir_key)
        
        # Determine if this is a submodule or main repo
        if target_dir in self.submodules:
            self._commit_squashed_submodule(target_dir, changed_files)
        else:
            self._commit_squashed_main_repo(target_dir, changed_files)
    
    def _commit_squashed_submodule(self, submodule_dir: Path, changed_files: Set[str]) -> None:
        """Create a squashed commit for submodule changes"""
        print(f"🔨 Creating submodule commit in {submodule_dir.name}")
        
        # Stage all changes in submodule
        stage_result = self._run_git_command(['git', 'add', '.'], submodule_dir, "Stage submodule changes")
        if stage_result.returncode != 0:
            print(f"❌ Failed to stage changes in submodule {submodule_dir}")
            return
            
        # Create commit message
        commit_message = self._create_squashed_commit_message(submodule_dir, changed_files)
        
        # Commit changes
        commit_result = self._run_git_command(
            ['git', 'commit', '-m', commit_message], 
            submodule_dir, 
            "Commit submodule changes"
        )
        
        if commit_result.returncode == 0:
            print(f"✓ Submodule commit: {commit_message}")
            # Push the submodule changes
            if self.config['auto_push']:
                self._push_changes(submodule_dir, f"submodule {submodule_dir.name}")
        else:
            print(f"❌ Failed to commit changes in submodule {submodule_dir}")
            return
            
        # Update submodule reference in main repo
        self._commit_submodule_update(submodule_dir)
    
    def _commit_squashed_main_repo(self, repo_dir: Path, changed_files: Set[str]) -> None:
        """Create a squashed commit for main repository changes"""
        print(f"🔨 Creating main repo commit")
        
        # Stage all changes
        stage_result = self._run_git_command(['git', 'add', '.'], repo_dir, "Stage main repo changes")
        if stage_result.returncode != 0:
            print(f"❌ Failed to stage changes in main repo")
            return
            
        # Create commit message
        commit_message = self._create_squashed_commit_message(repo_dir, changed_files)
        
        # Commit changes
        commit_result = self._run_git_command(
            ['git', 'commit', '-m', commit_message], 
            repo_dir, 
            "Commit main repo changes"
        )
        
        if commit_result.returncode == 0:
            print(f"✓ Committed: {commit_message}")
            # Send notification for main repo commit
            if self.config['enable_notifications'] and self.config['notify_on_commit']:
                self._send_commit_notification(commit_message)
            # Push the main repo changes
            if self.config['auto_push']:
                self._push_changes(self.repo_dir, "main repo")
        else:
            print(f"❌ Failed to commit changes in main repo")
    
    def _commit_submodule_update(self, submodule_dir: Path) -> None:
        """Commit submodule reference update in main repo"""
        rel_path = submodule_dir.relative_to(self.repo_dir)
        
        # Stage the submodule update
        stage_result = self._run_git_command(['git', 'add', str(rel_path)], self.repo_dir, "Stage submodule update")
        if stage_result.returncode != 0:
            return
            
        # Check if there are changes to commit
        status_result = self._run_git_command(['git', 'diff', '--cached', '--quiet'], self.repo_dir, "Check staged changes")
        if status_result.returncode == 0:
            # No changes to commit
            return
            
        commit_message = f"Update {submodule_dir.name} submodule"
        
        # Commit the submodule update
        commit_result = self._run_git_command(
            ['git', 'commit', '-m', commit_message], 
            self.repo_dir, 
            "Commit submodule update"
        )
        
        if commit_result.returncode == 0:
            print(f"✓ Main repo commit: {commit_message}")
            # Send notification for main repo commit
            if self.config['enable_notifications'] and self.config['notify_on_commit']:
                self._send_commit_notification(commit_message)
            # Push the main repo changes
            if self.config['auto_push']:
                self._push_changes(self.repo_dir, "main repo")
    
    def _create_squashed_commit_message(self, repo_dir: Path, changed_files: Set[str]) -> str:
        """Create a commit message based on actual git status"""
        try:
            # Get git status to see what actually changed
            status_result = self._run_git_command(['git', 'status', '--porcelain'], repo_dir, "Get git status")
            if status_result.returncode != 0:
                return "Update files"
                
            status_lines = [line.strip() for line in status_result.stdout.strip().split('\n') if line.strip()]
            
            if not status_lines:
                return "Update files"
                
            # Count different types of changes
            created = sum(1 for line in status_lines if line.startswith('A '))
            modified = sum(1 for line in status_lines if line.startswith('M ') or line.startswith(' M'))
            deleted = sum(1 for line in status_lines if line.startswith('D '))
            renamed = sum(1 for line in status_lines if line.startswith('R '))
            
            # Build commit message
            parts = []
            if created > 0:
                parts.append(f"created {created} file{'s' if created != 1 else ''}")
            if modified > 0:
                parts.append(f"modified {modified} file{'s' if modified != 1 else ''}")
            if deleted > 0:
                parts.append(f"deleted {deleted} file{'s' if deleted != 1 else ''}")
            if renamed > 0:
                parts.append(f"renamed {renamed} file{'s' if renamed != 1 else ''}")
                
            if parts:
                message = "Auto-commit: " + ", ".join(parts)
            else:
                message = "Auto-commit: updated files"
                
            return message
            
        except Exception:
            return "Auto-commit: updated files"
    
    def _push_changes(self, repo_dir: Path, repo_name: str) -> None:
        """Push changes to remote repository"""
        push_result = self._run_git_command(['git', 'push'], repo_dir, f"Push {repo_name}")
        if push_result.returncode == 0:
            print(f"🚀 Pushed {repo_name} changes")
        else:
            print(f"❌ Failed to push {repo_name} changes")
    
    def _send_commit_notification(self, commit_message: str) -> None:
        """Send desktop notification for commit"""
        try:
            subprocess.run([
                'notify-send',
                f'📦 {self.config["name"]} Commit',
                commit_message,
                '-t', '5000',  # 5 second timeout
                '-a', 'Watcher'
            ], check=False)
        except Exception as e:
            print(f"⚠️  Failed to send notification: {e}")
    
    def start_fetch_timer(self) -> None:
        """Start the periodic fetch timer"""
        if self.fetch_timer:
            self.fetch_timer.cancel()
            
        self.fetch_timer = threading.Timer(self.config['fetch_interval'], self._periodic_fetch)
        self.fetch_timer.start()
        print(f"🔄 Started periodic fetch timer (every {self.config['fetch_interval']//60} minutes)")
    
    def _periodic_fetch(self) -> None:
        """Perform periodic fetch and notify of remote changes"""
        print("🔄 Performing periodic fetch...")
        
        # Fetch main repo
        main_changes = self._fetch_and_check_changes(self.repo_dir, "main repo")
        
        # Fetch submodules
        submodule_changes = {}
        for submodule in self.submodules:
            changes = self._fetch_and_check_changes(submodule, f"submodule {submodule.name}")
            if changes:
                submodule_changes[submodule.name] = changes
        
        # Send notification if there were remote changes
        if main_changes or submodule_changes:
            if self.config['enable_notifications'] and self.config['notify_on_remote_changes']:
                self._send_change_notification(main_changes, submodule_changes)
        
        # Restart the timer
        self.start_fetch_timer()
    
    def _fetch_and_check_changes(self, repo_dir: Path, repo_name: str) -> Optional[str]:
        """Fetch and check for remote changes"""
        # Get current HEAD
        head_result = self._run_git_command(['git', 'rev-parse', 'HEAD'], repo_dir, f"Get {repo_name} HEAD")
        if head_result.returncode != 0:
            return None
        old_head = head_result.stdout.strip()
        
        # Fetch
        fetch_result = self._run_git_command(['git', 'fetch'], repo_dir, f"Fetch {repo_name}")
        if fetch_result.returncode != 0:
            return None
            
        # Check if remote has new commits
        branch_result = self._run_git_command(['git', 'branch', '--show-current'], repo_dir, f"Get {repo_name} branch")
        if branch_result.returncode != 0:
            return None
        current_branch = branch_result.stdout.strip()
        
        if not current_branch:
            return None
            
        remote_head_result = self._run_git_command(
            ['git', 'rev-parse', f'origin/{current_branch}'], 
            repo_dir, 
            f"Get {repo_name} remote HEAD"
        )
        if remote_head_result.returncode != 0:
            return None
        remote_head = remote_head_result.stdout.strip()
        
        if old_head != remote_head:
            # Get commit count
            count_result = self._run_git_command(
                ['git', 'rev-list', '--count', f'{old_head}..{remote_head}'], 
                repo_dir, 
                f"Count {repo_name} commits"
            )
            if count_result.returncode == 0:
                commit_count = count_result.stdout.strip()
                return f"{commit_count} new commit{'s' if commit_count != '1' else ''}"
        
        return None
    
    def _send_change_notification(self, main_changes: Optional[str], submodule_changes: Dict[str, str]) -> None:
        """Send notification about remote changes"""
        try:
            if main_changes:
                subprocess.run([
                    'notify-send',
                    f'🔄 {self.config["name"]} Remote Changes',
                    f'Main repo: {main_changes}',
                    '-t', '10000',  # 10 second timeout
                    '-a', 'Watcher'
                ], check=False)
            
            for submodule, changes in submodule_changes.items():
                subprocess.run([
                    'notify-send',
                    f'🔄 {self.config["name"]} Remote Changes',
                    f'{submodule}: {changes}',
                    '-t', '10000',  # 10 second timeout
                    '-a', 'Watcher'
                ], check=False)
        except Exception as e:
            print(f"⚠️  Failed to send change notification: {e}")
    
    def _commit_existing_changes(self) -> None:
        """Check for and commit any existing uncommitted changes on startup"""
        print("🔍 Checking for existing uncommitted changes...")
        
        # Check main repo
        self._commit_existing_in_repo(self.repo_dir, "main repo")
        
        # Check submodules
        for submodule in self.submodules:
            self._commit_existing_in_repo(submodule, f"submodule {submodule.name}")
    
    def _commit_existing_in_repo(self, repo_dir: Path, repo_name: str) -> None:
        """Check for and commit existing changes in a specific repository"""
        # Check if there are any changes (staged or unstaged)
        status_result = self._run_git_command(['git', 'status', '--porcelain'], repo_dir, f"Check {repo_name} status")
        
        if status_result.returncode == 0 and status_result.stdout.strip():
            print(f"📝 Found existing changes in {repo_name}, committing...")
            
            # Stage all changes
            add_result = self._run_git_command(['git', 'add', '.'], repo_dir, f"Stage {repo_name} changes")
            if add_result.returncode == 0:
                # Create commit message
                commit_message = f"Auto-commit existing changes in {repo_name}"
                
                # Commit the changes
                commit_result = self._run_git_command(
                    ['git', 'commit', '-m', commit_message], 
                    repo_dir, 
                    f"Commit existing {repo_name} changes"
                )
                
                if commit_result.returncode == 0:
                    print(f"✅ Committed existing changes in {repo_name}")
                    if self.config['enable_notifications'] and self.config['notify_on_commit']:
                        self._send_commit_notification(commit_message)
                    
                    # Push the changes
                    if self.config['auto_push']:
                        if repo_dir == self.repo_dir:
                            self._push_changes(repo_dir, "main repo")
                        else:
                            self._push_changes(repo_dir, f"submodule {repo_dir.name}")
                            # Also update the submodule reference in main repo
                            self._commit_submodule_update(repo_dir)
    
    def stop(self) -> None:
        """Stop the watcher and clean up resources"""
        print("🛑 Stopping watcher...")
        
        # Cancel all timers
        with self.timer_lock:
            for timer in self.commit_timers.values():
                timer.cancel()
            self.commit_timers.clear()
            
        if self.fetch_timer:
            self.fetch_timer.cancel()


def run_watcher(config_name: str) -> None:
    """
    Run the file watcher for a specific configuration
    
    Args:
        config_name: Name of the configuration to use
    """
    # Ensure stdout/stderr are unbuffered for journalctl
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 1)
    
    print(f"🚀 Starting watcher for config: {config_name}")
    print(f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load_config(config_name)
    
    # Validate configuration
    validation = config_manager.validate_config(config_name)
    if not validation['valid']:
        for error in validation['errors']:
            print(f"❌ Config error: {error}")
        return
        
    for warning in validation['warnings']:
        print(f"⚠️  Config warning: {warning}")
    
    # Expand the watch directory path
    watch_dir = Path(config['watch_directory']).expanduser().resolve()
    
    # Validate directory exists
    if not watch_dir.exists():
        print(f"❌ Error: Directory {watch_dir} does not exist")
        return
    
    # Check if it's a git repository
    if not (Path(config['repo_directory']) / '.git').exists():
        print(f"❌ Error: {config['repo_directory']} is not a git repository")
        return
    
    print(f"📁 Watching directory: {watch_dir}")
    print(f"📦 Git repository: {config['repo_directory']}")
    print("⏰ Starting file monitoring...")
    
    # Set up file watcher
    event_handler = GitCommitHandler(config_name)
    observer = Observer()
    observer.schedule(event_handler, str(watch_dir), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping file watcher...")
        event_handler.stop()
        observer.stop()
        observer.join()
        print("✅ File watcher stopped successfully")


if __name__ == "__main__":
    # Default to 'config' if no argument provided
    config_name = sys.argv[1] if len(sys.argv) > 1 else 'config'
    run_watcher(config_name)