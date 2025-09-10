#!/usr/bin/env python3
"""
Scanner module for finding Node.js installations and package files.
"""

import json
import os
from pathlib import Path
from typing import List, Set, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess


class NodeScanner:
    """Scanner for Node.js installations and package files."""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.common_node_paths = [
            Path.home() / ".npm",
            Path.home() / ".nvm",
            Path.home() / "node_modules",
            Path("/usr/local/lib/node_modules"),
            Path("/usr/lib/node_modules"),
            Path("/opt/node_modules"),
        ]
    
    def find_package_json_files(self, start_path: Path, max_depth: int = 10) -> List[Path]:
        """
        Find all package.json files starting from a given path.
        
        Args:
            start_path: Directory to start searching from
            max_depth: Maximum directory depth to search
            
        Returns:
            List of paths to package.json files
        """
        package_files = []
        
        def _search_dir(path: Path, current_depth: int = 0):
            if current_depth > max_depth:
                return
            
            try:
                if not path.is_dir():
                    return
                
                # Check for package.json in current directory
                package_json = path / "package.json"
                if package_json.exists() and package_json.is_file():
                    package_files.append(package_json)
                
                # Skip certain directories to avoid infinite loops and improve performance
                skip_dirs = {'.git', '.svn', '.hg', '__pycache__', '.pytest_cache', 'venv', '.venv'}
                
                # Recursively search subdirectories
                for item in path.iterdir():
                    if item.is_dir() and item.name not in skip_dirs:
                        # Don't recurse into node_modules for finding package.json
                        if item.name != 'node_modules':
                            _search_dir(item, current_depth + 1)
            except (PermissionError, OSError):
                pass
        
        _search_dir(start_path)
        return package_files
    
    def find_node_modules_dirs(self, start_path: Path, max_depth: int = 10) -> List[Path]:
        """
        Find all node_modules directories starting from a given path.
        
        Args:
            start_path: Directory to start searching from
            max_depth: Maximum directory depth to search
            
        Returns:
            List of paths to node_modules directories
        """
        node_modules_dirs = []
        
        def _search_dir(path: Path, current_depth: int = 0):
            if current_depth > max_depth:
                return
            
            try:
                if not path.is_dir():
                    return
                
                # Check for node_modules in current directory
                node_modules = path / "node_modules"
                if node_modules.exists() and node_modules.is_dir():
                    node_modules_dirs.append(node_modules)
                
                # Skip certain directories
                skip_dirs = {'.git', '.svn', '.hg', '__pycache__', '.pytest_cache', 'venv', '.venv', 'node_modules'}
                
                # Recursively search subdirectories
                for item in path.iterdir():
                    if item.is_dir() and item.name not in skip_dirs:
                        _search_dir(item, current_depth + 1)
            except (PermissionError, OSError):
                pass
        
        _search_dir(start_path)
        return node_modules_dirs
    
    def find_global_npm_prefix(self) -> Path:
        """
        Find the global npm prefix directory.
        
        Returns:
            Path to global npm prefix or None if not found
        """
        try:
            result = subprocess.run(
                ['npm', 'config', 'get', 'prefix'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return Path(result.stdout.strip())
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        return None
    
    def find_all_node_installations(self, search_paths: List[Path] = None) -> Dict[str, List[Path]]:
        """
        Find all Node.js installations including global, user, and project-specific.
        
        Args:
            search_paths: List of paths to search (defaults to common locations)
            
        Returns:
            Dictionary with 'package_json' and 'node_modules' lists
        """
        if search_paths is None:
            search_paths = [Path.home(), Path.cwd()]
            
            # Add global npm prefix if found
            global_prefix = self.find_global_npm_prefix()
            if global_prefix:
                search_paths.append(global_prefix)
            
            # Add common node paths that exist
            for path in self.common_node_paths:
                if path.exists():
                    search_paths.append(path)
        
        all_package_files = set()
        all_node_modules = set()
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit package.json search tasks
            package_futures = {
                executor.submit(self.find_package_json_files, path): path 
                for path in search_paths
            }
            
            # Submit node_modules search tasks
            modules_futures = {
                executor.submit(self.find_node_modules_dirs, path): path 
                for path in search_paths
            }
            
            # Collect package.json results
            for future in as_completed(package_futures):
                try:
                    results = future.result(timeout=30)
                    all_package_files.update(results)
                except Exception:
                    pass
            
            # Collect node_modules results
            for future in as_completed(modules_futures):
                try:
                    results = future.result(timeout=30)
                    all_node_modules.update(results)
                except Exception:
                    pass
        
        return {
            'package_json': sorted(list(all_package_files)),
            'node_modules': sorted(list(all_node_modules))
        }
    
    def scan_path(self, path: Path) -> Dict[str, List[Path]]:
        """
        Scan a specific path for Node.js installations.
        
        Args:
            path: Path to scan
            
        Returns:
            Dictionary with 'package_json' and 'node_modules' lists
        """
        return self.find_all_node_installations([path])