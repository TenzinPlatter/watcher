"""
Ignore pattern management for watcher
Handles hierarchical ignore patterns from multiple sources
"""

import os
import fnmatch
from pathlib import Path
from typing import List, Set, Optional, Dict, Any


class IgnoreManager:
    """Manages ignore patterns from multiple sources with hierarchical precedence"""
    
    def __init__(self, config_name: str, config_data: Dict[str, Any]) -> None:
        self.config_name: str = config_name
        self.config_data: Dict[str, Any] = config_data
        self.watch_dir: Path = Path(config_data['watch_directory']).expanduser().resolve()
        
        # Load ignore patterns from different sources
        self.global_patterns: List[str] = self._load_global_ignore()
        self.config_patterns: List[str] = self._load_config_ignore()
        self.additional_patterns: List[str] = self._load_additional_ignore_files()
        self.gitignore_patterns: Dict[str, List[str]] = {}  # Will be loaded per directory
        
        # Combine all patterns for efficient matching
        self.all_patterns: List[str] = self.global_patterns + self.config_patterns + self.additional_patterns
        
    def should_ignore(self, file_path: str) -> bool:
        """
        Check if a file should be ignored based on all ignore sources
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            True if the file should be ignored, False otherwise
        """
        file_path = Path(file_path).resolve()
        
        # Convert to relative path from watch directory for pattern matching
        try:
            rel_path = file_path.relative_to(self.watch_dir)
        except ValueError:
            # File is outside watch directory
            return True
            
        rel_path_str = str(rel_path)
        
        # Check against all combined patterns
        for pattern in self.all_patterns:
            if self._matches_pattern(rel_path_str, pattern):
                return True
                
        # Check gitignore patterns if enabled
        if self.config_data.get('respect_gitignore', True):
            if self._matches_gitignore(file_path):
                return True
                
        return False
        
    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if a file path matches a single ignore pattern"""
        # Remove leading/trailing whitespace
        pattern = pattern.strip()
        
        # Skip empty lines and comments
        if not pattern or pattern.startswith('#'):
            return False
            
        # Handle negation patterns (patterns starting with !)
        if pattern.startswith('!'):
            # TODO: Implement negation patterns if needed
            return False
            
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            # Check if any parent directory matches
            path_parts = file_path.split('/')
            for i in range(len(path_parts)):
                parent_path = '/'.join(path_parts[:i+1])
                if fnmatch.fnmatch(parent_path, pattern):
                    return True
        else:
            # Check against full path and just filename
            if fnmatch.fnmatch(file_path, pattern):
                return True
            if fnmatch.fnmatch(Path(file_path).name, pattern):
                return True
                
        return False
        
    def _load_global_ignore(self) -> List[str]:
        """Load patterns from global ignore file"""
        global_ignore_path = Path.home() / '.config' / 'watcher' / 'ignore'
        return self._load_ignore_file(global_ignore_path)
        
    def _load_config_ignore(self) -> List[str]:
        """Load patterns from config's ignore_patterns"""
        return self.config_data.get('ignore_patterns', [])
        
    def _load_additional_ignore_files(self) -> List[str]:
        """Load patterns from config's ignore_files"""
        patterns = []
        ignore_files = self.config_data.get('ignore_files', [])
        
        for ignore_file in ignore_files:
            ignore_path = Path(ignore_file).expanduser().resolve()
            patterns.extend(self._load_ignore_file(ignore_path))
            
        return patterns
        
    def _load_ignore_file(self, ignore_path: Path) -> List[str]:
        """Load patterns from a single ignore file"""
        if not ignore_path.exists():
            return []
            
        try:
            with open(ignore_path, 'r') as f:
                patterns = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
                return patterns
        except (IOError, OSError) as e:
            print(f"⚠️  Warning: Could not read ignore file {ignore_path}: {e}")
            return []
            
    def _matches_gitignore(self, file_path: Path) -> bool:
        """Check if file matches any gitignore patterns"""
        # Start from the file's directory and walk up to the watch directory
        current_dir = file_path.parent
        
        while current_dir >= self.watch_dir:
            gitignore_path = current_dir / '.gitignore'
            
            if gitignore_path.exists():
                # Load gitignore patterns for this directory if not already loaded
                if str(current_dir) not in self.gitignore_patterns:
                    self.gitignore_patterns[str(current_dir)] = self._load_ignore_file(gitignore_path)
                
                # Check file against this directory's gitignore patterns
                try:
                    rel_path = file_path.relative_to(current_dir)
                    rel_path_str = str(rel_path)
                    
                    for pattern in self.gitignore_patterns[str(current_dir)]:
                        if self._matches_pattern(rel_path_str, pattern):
                            return True
                except ValueError:
                    # File is not under this directory
                    pass
                    
            # Move up one directory
            if current_dir == self.watch_dir:
                break
            current_dir = current_dir.parent
            
        return False
        
    def get_all_patterns(self) -> Dict[str, Any]:
        """Get all loaded patterns for debugging"""
        return {
            'global': self.global_patterns,
            'config': self.config_patterns,
            'additional': self.additional_patterns,
            'gitignore': self.gitignore_patterns
        }
        
    def test_pattern(self, file_path: str) -> Dict[str, Any]:
        """Test which ignore sources would match a file (for debugging)"""
        result = {
            'ignored': False,
            'matched_by': []
        }
        
        if self.should_ignore(file_path):
            result['ignored'] = True
            
            # Test each source individually
            file_path_obj = Path(file_path).resolve()
            try:
                rel_path = file_path_obj.relative_to(self.watch_dir)
                rel_path_str = str(rel_path)
                
                # Test global patterns
                for pattern in self.global_patterns:
                    if self._matches_pattern(rel_path_str, pattern):
                        result['matched_by'].append(f"global: {pattern}")
                        
                # Test config patterns
                for pattern in self.config_patterns:
                    if self._matches_pattern(rel_path_str, pattern):
                        result['matched_by'].append(f"config: {pattern}")
                        
                # Test additional patterns
                for pattern in self.additional_patterns:
                    if self._matches_pattern(rel_path_str, pattern):
                        result['matched_by'].append(f"additional: {pattern}")
                        
                # Test gitignore patterns
                if self.config_data.get('respect_gitignore', True):
                    if self._matches_gitignore(file_path_obj):
                        result['matched_by'].append("gitignore")
                        
            except ValueError:
                result['matched_by'].append("outside watch directory")
                
        return result