#!/usr/bin/env python3
"""
Command-line interface for npm vulnerability scanner.
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional

from .scanner import NodeScanner
from .checker import DependencyChecker
from .utils import OutputFormatter, ProgressReporter, validate_path, get_project_root


class NPMVulnerabilityScanner:
    """Main CLI application for scanning npm vulnerabilities."""
    
    def __init__(self):
        self.scanner = NodeScanner()
        self.checker = DependencyChecker()
        self.formatter = OutputFormatter()
        self.progress = ProgressReporter()
    
    def scan_paths(self, paths: List[Path], verbose: bool = False) -> dict:
        """
        Scan multiple paths for Node.js installations and vulnerabilities.
        
        Args:
            paths: List of paths to scan
            verbose: Enable verbose output
            
        Returns:
            Detection results
        """
        self.progress.verbose = verbose
        
        # Find all Node.js installations
        if verbose:
            print("Discovering Node.js installations...")
        
        installations = self.scanner.find_all_node_installations(paths)
        
        package_files = installations['package_json']
        node_modules = installations['node_modules']
        
        if verbose:
            print(f"Found {len(package_files)} package.json file(s)")
            print(f"Found {len(node_modules)} node_modules directory(ies)")
        
        # Check for vulnerabilities
        if verbose:
            print("\nChecking for compromised packages...")
        
        results = self.checker.check_all(package_files, node_modules)
        
        return results
    
    def scan_package_json(self, package_json_path: Path, check_transitive: bool = True, verbose: bool = False) -> dict:
        """
        Scan a specific package.json file.
        
        Args:
            package_json_path: Path to package.json
            check_transitive: Also check transitive dependencies
            verbose: Enable verbose output
            
        Returns:
            Detection results organized by severity
        """
        self.progress.verbose = verbose
        
        results = {
            'critical': [],
            'high': [],
            'medium': [],
            'warning': []
        }
        
        # Check the package.json file
        if verbose:
            print(f"Checking {package_json_path}...")
        
        package_results = self.checker.check_package_json(package_json_path)
        for result in package_results:
            results[result.severity.value].append(result)
        
        if check_transitive:
            parent_dir = package_json_path.parent
            
            # Check node_modules
            node_modules = parent_dir / 'node_modules'
            if node_modules.exists():
                if verbose:
                    print(f"Checking node_modules in {parent_dir}...")
                
                module_results = self.checker.check_node_modules(node_modules)
                for result in module_results:
                    results[result.severity.value].append(result)
            
            # Check lock files
            lock_files = [
                parent_dir / 'package-lock.json',
                parent_dir / 'yarn.lock'
            ]
            
            for lock_file in lock_files:
                if lock_file.exists():
                    if verbose:
                        print(f"Checking {lock_file.name}...")
                    
                    lock_results = self.checker.check_lock_file(lock_file)
                    for result in lock_results:
                        results[result.severity.value].append(result)
        
        return results
    
    def run_scan_command(self, args):
        """Handle the 'scan' command."""
        paths = []
        
        if args.paths:
            for path_str in args.paths:
                try:
                    path = validate_path(path_str)
                    paths.append(path)
                except ValueError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(1)
        else:
            # Default to current directory
            paths = [Path.cwd()]
        
        # Add home directory if requested
        if args.include_home:
            paths.append(Path.home())
        
        # Add global npm if requested
        if args.include_global:
            global_prefix = self.scanner.find_global_npm_prefix()
            if global_prefix:
                paths.append(global_prefix)
            else:
                print("Warning: Could not find global npm prefix", file=sys.stderr)
        
        self.formatter.print_header("NPM Vulnerability Scanner")
        self.formatter.print_compromised_packages(self.checker.compromised_versions)
        
        print(f"\nScanning {len(paths)} path(s)...")
        for path in paths:
            print(f"  • {path}")
        
        start_time = time.time()
        results = self.scan_paths(paths, verbose=args.verbose)
        duration = time.time() - start_time
        
        self.formatter.print_detection_results(results)
        self.formatter.print_summary(results, paths, duration)
        
        # Export results if requested
        if args.export_json:
            self.formatter.export_json(results, Path(args.export_json))
        
        if args.export_csv:
            self.formatter.export_csv(results, Path(args.export_csv))
        
        # Return exit code 1 for any findings
        total_findings = sum(len(r) for r in results.values())
        return 1 if total_findings > 0 else 0
    
    def run_check_command(self, args):
        """Handle the 'check' command."""
        try:
            # First check if it's a path string
            package_path = Path(args.package_json).resolve()
            
            # If it's a directory, look for package.json inside
            if package_path.is_dir():
                package_path = package_path / 'package.json'
            
            # Check if the file exists and has the right name
            if not package_path.exists():
                print(f"Error: {package_path} does not exist", file=sys.stderr)
                sys.exit(1)
            
            if not package_path.name.endswith('package.json'):
                print(f"Error: {package_path} is not a package.json file", file=sys.stderr)
                sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        
        self.formatter.print_header("NPM Vulnerability Scanner")
        self.formatter.print_compromised_packages(self.checker.compromised_versions)
        
        print(f"\nChecking {package_path}")
        
        start_time = time.time()
        results = self.scan_package_json(
            package_path, 
            check_transitive=not args.no_transitive,
            verbose=args.verbose
        )
        duration = time.time() - start_time
        
        self.formatter.print_detection_results(results)
        self.formatter.print_summary(results, [package_path], duration)
        
        # Export results if requested
        if args.export_json:
            self.formatter.export_json(results, Path(args.export_json))
        
        if args.export_csv:
            self.formatter.export_csv(results, Path(args.export_csv))
        
        # Return exit code 1 for any findings
        total_findings = sum(len(r) for r in results.values())
        return 1 if total_findings > 0 else 0
    
    def run_list_command(self, args):
        """Handle the 'list' command."""
        self.formatter.print_header("Compromised NPM Packages")
        
        print("The following packages and versions have been identified as compromised:")
        print("Published after September 8, 2025 13:00 UTC\n")
        
        total_versions = 0
        for i, (pkg_name, versions) in enumerate(sorted(self.checker.compromised_versions.items()), 1):
            name = self.formatter._color(pkg_name, self.formatter.RED)
            version_list = ", ".join(versions)
            print(f"{i:2}. {name}: {version_list}")
            total_versions += len(versions)
        
        print(f"\nTotal: {len(self.checker.compromised_versions)} packages, {total_versions} versions")
        return 0


def create_parser():
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        description='Scan for compromised npm packages in Node.js projects',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan current directory
  %(prog)s scan
  
  # Scan specific paths
  %(prog)s scan /path/to/project1 /path/to/project2
  
  # Scan with home directory and global npm
  %(prog)s scan --include-home --include-global
  
  # Check specific package.json
  %(prog)s check package.json
  
  # Export results
  %(prog)s scan --export-json results.json --export-csv results.csv
  
  # List compromised packages
  %(prog)s list
        """
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser(
        'scan',
        help='Scan paths for Node.js installations and vulnerabilities'
    )
    scan_parser.add_argument(
        'paths',
        nargs='*',
        help='Paths to scan (defaults to current directory)'
    )
    scan_parser.add_argument(
        '--include-home',
        action='store_true',
        help='Include home directory in scan'
    )
    scan_parser.add_argument(
        '--include-global',
        action='store_true',
        help='Include global npm packages in scan'
    )
    scan_parser.add_argument(
        '--export-json',
        metavar='FILE',
        help='Export results to JSON file'
    )
    scan_parser.add_argument(
        '--export-csv',
        metavar='FILE',
        help='Export results to CSV file'
    )
    
    # Check command
    check_parser = subparsers.add_parser(
        'check',
        help='Check a specific package.json file'
    )
    check_parser.add_argument(
        'package_json',
        help='Path to package.json file or directory containing it'
    )
    check_parser.add_argument(
        '--no-transitive',
        action='store_true',
        help='Skip checking transitive dependencies'
    )
    check_parser.add_argument(
        '--export-json',
        metavar='FILE',
        help='Export results to JSON file'
    )
    check_parser.add_argument(
        '--export-csv',
        metavar='FILE',
        help='Export results to CSV file'
    )
    
    # List command
    list_parser = subparsers.add_parser(
        'list',
        help='List all compromised packages being checked'
    )
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Create scanner instance
    scanner = NPMVulnerabilityScanner()
    
    # Disable colors if requested
    if hasattr(args, 'no_color') and args.no_color:
        scanner.formatter.use_color = False
    
    # Set verbose mode
    if hasattr(args, 'verbose'):
        scanner.progress.verbose = args.verbose
    
    # Execute command
    exit_code = 0
    
    try:
        if args.command == 'scan':
            exit_code = scanner.run_scan_command(args)
        elif args.command == 'check':
            exit_code = scanner.run_check_command(args)
        elif args.command == 'list':
            exit_code = scanner.run_list_command(args)
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user", file=sys.stderr)
        exit_code = 130
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()