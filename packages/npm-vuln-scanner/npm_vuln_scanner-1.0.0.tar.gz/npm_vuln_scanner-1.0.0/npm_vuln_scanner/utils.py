#!/usr/bin/env python3
"""
Utility functions for npm package vulnerability detection.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from .checker import DetectionResult, Severity


class OutputFormatter:
    """Format and display detection results."""
    
    # ANSI color codes
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    def __init__(self, use_color: bool = True):
        self.use_color = use_color and sys.stdout.isatty()
    
    def _color(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if self.use_color:
            return f"{color}{text}{self.RESET}"
        return text
    
    def print_header(self, text: str):
        """Print a formatted header."""
        print(f"\n{self._color('=' * 80, self.CYAN)}")
        print(self._color(text.center(80), self.BOLD + self.CYAN))
        print(f"{self._color('=' * 80, self.CYAN)}\n")
    
    def print_section(self, text: str):
        """Print a section header."""
        print(f"\n{self._color(text, self.BOLD + self.YELLOW)}")
        print(self._color('-' * len(text), self.YELLOW))
    
    def print_compromised_packages(self, compromised_versions: dict):
        """Print list of compromised packages and versions being checked."""
        self.print_section("Compromised Packages and Versions")
        print("These specific versions were published after September 8, 2025 13:00 UTC:")
        print()
        
        # Sort packages by name
        for pkg_name in sorted(compromised_versions.keys()):
            versions = compromised_versions[pkg_name]
            name = self._color(pkg_name, self.RED)
            version_list = ", ".join(versions)
            print(f"  • {name}: {version_list}")
    
    def print_detection_results(self, results: Dict[str, List[DetectionResult]]):
        """Print formatted detection results by severity."""
        total_critical = len(results.get('critical', []))
        total_high = len(results.get('high', []))
        total_medium = len(results.get('medium', []))
        total_warning = len(results.get('warning', []))
        total_all = total_critical + total_high + total_medium + total_warning
        
        if total_all == 0:
            print(self._color("✓ No packages from the compromised list detected!", self.GREEN + self.BOLD))
            return
        
        # Print summary
        if total_critical > 0:
            print(self._color(f"🚨 CRITICAL: {total_critical} confirmed compromised version(s) found!", self.RED + self.BOLD))
        if total_high > 0:
            print(self._color(f"⚠️  HIGH: {total_high} package(s) could install compromised versions", self.YELLOW + self.BOLD))
        if total_medium > 0:
            print(self._color(f"ℹ️  MEDIUM: {total_medium} package(s) present but using safe versions", self.BLUE))
        if total_warning > 0:
            print(self._color(f"❓ WARNING: {total_warning} package(s) present but version unknown", self.MAGENTA))
        
        # Print in order from least to most severe (so most severe is at the bottom, easier to see)
        
        # Print warnings first
        if total_warning > 0:
            self.print_section("❓ WARNING - Version Unknown")
            for detection in results['warning']:
                self._print_detection(detection, self.MAGENTA)
        
        # Print medium severity
        if total_medium > 0:
            self.print_section("ℹ️  MEDIUM - Safe Versions Specified")
            for detection in results['medium']:
                self._print_detection(detection, self.BLUE)
        
        # Print high severity
        if total_high > 0:
            self.print_section("⚠️  HIGH - Could Install Compromised Versions")
            for detection in results['high']:
                self._print_detection(detection, self.YELLOW + self.BOLD)
        
        # Print critical findings last (most visible at the bottom)
        if total_critical > 0:
            self.print_section("🚨 CRITICAL - Confirmed Compromised Versions")
            for detection in results['critical']:
                self._print_detection(detection, self.RED + self.BOLD)
    
    def _print_detection(self, detection: DetectionResult, color: str):
        """Print a single detection result."""
        location_type = "Installed in" if detection.detection_type == 'installed' else "Specified in"
        print(f"\n  {self._color(detection.package_name, color)}")
        print(f"    {location_type}: {detection.file_path}")
        
        if detection.actual_version:
            print(f"    Installed version: {detection.actual_version}")
        elif detection.package_version:
            print(f"    Version spec: {detection.package_version}")
        
        print(f"    Type: {detection.detection_type}")
        print(f"    {detection.message}")
        
        if detection.parent_package:
            print(f"    Parent: {detection.parent_package}")
    
    def _get_type_label(self, detection_type: str) -> str:
        """Get formatted label for detection type."""
        labels = {
            'direct': self._color('[Direct Dependencies]', self.RED + self.BOLD),
            'dev': self._color('[Dev Dependencies]', self.YELLOW + self.BOLD),
            'optional': self._color('[Optional Dependencies]', self.YELLOW),
            'transitive': self._color('[Transitive Dependencies]', self.MAGENTA),
            'installed': self._color('[Installed in node_modules]', self.CYAN + self.BOLD)
        }
        return labels.get(detection_type, f'[{detection_type}]')
    
    def print_summary(self, results: Dict[str, List[DetectionResult]], scan_paths: List[Path], duration: float):
        """Print scan summary."""
        self.print_section("Scan Summary")
        
        total_detections = sum(len(r) for r in results.values())
        critical_count = len(results.get('critical', []))
        high_count = len(results.get('high', []))
        
        print(f"  Paths scanned: {len(scan_paths)}")
        print(f"  Total findings: {total_detections}")
        
        if total_detections > 0:
            print(f"  By severity:")
            for severity in ['critical', 'high', 'medium', 'warning']:
                if severity in results and results[severity]:
                    severity_color = {
                        'critical': self.RED + self.BOLD,
                        'high': self.YELLOW + self.BOLD,
                        'medium': self.BLUE,
                        'warning': self.MAGENTA
                    }[severity]
                    print(f"    • {self._color(severity.upper(), severity_color)}: {len(results[severity])}")
        
        print(f"  Scan duration: {duration:.2f} seconds")
        
        # Recommendations based on severity
        if critical_count > 0:
            self.print_section("🚨 IMMEDIATE ACTION REQUIRED")
            print("  1. You have CONFIRMED compromised packages installed!")
            print("  2. These packages contain malicious code targeting crypto wallets")
            print("  3. Immediately downgrade or remove these packages")
            print("  4. Check for any suspicious transactions if your app handles crypto")
            print("  5. Rotate any exposed credentials or keys")
        elif high_count > 0:
            self.print_section("⚠️  ACTION RECOMMENDED")
            print("  1. Your version specifications could install compromised versions")
            print("  2. Run 'npm install' or 'yarn install' to check actual versions")
            print("  3. Pin versions to safe releases (before Sept 8, 2025)")
            print("  4. Consider using lock files to ensure consistent installs")
        elif total_detections > 0:
            self.print_section("ℹ️  Monitoring Recommended")
            print("  1. You have packages from the compromised list")
            print("  2. Currently using safe versions")
            print("  3. Monitor for updates and security advisories")
            print("  4. Consider alternative packages if available")
    
    def export_json(self, results: Dict[str, List[DetectionResult]], output_file: Path):
        """Export results to JSON file."""
        export_data = {
            'scan_timestamp': datetime.now().isoformat(),
            'total_findings': sum(len(r) for r in results.values()),
            'summary': {
                'critical': len(results.get('critical', [])),
                'high': len(results.get('high', [])),
                'medium': len(results.get('medium', [])),
                'warning': len(results.get('warning', []))
            },
            'findings': {}
        }
        
        for severity, detections in results.items():
            export_data['findings'][severity] = [
                {
                    'file_path': str(d.file_path),
                    'package_name': d.package_name,
                    'package_version': d.package_version,
                    'actual_version': d.actual_version,
                    'detection_type': d.detection_type,
                    'severity': d.severity.value,
                    'message': d.message,
                    'parent_package': d.parent_package
                }
                for d in detections
            ]
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n{self._color('Results exported to:', self.GREEN)} {output_file}")
    
    def export_csv(self, results: Dict[str, List[DetectionResult]], output_file: Path):
        """Export results to CSV file."""
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Severity', 'Package Name', 'Version Spec', 'Actual Version', 'File Path', 'Detection Type', 'Message', 'Parent Package'])
            
            for severity_level in ['critical', 'high', 'medium', 'warning']:
                if severity_level in results:
                    for d in results[severity_level]:
                        writer.writerow([
                            d.severity.value.upper(),
                            d.package_name,
                            d.package_version or '',
                            d.actual_version or '',
                            str(d.file_path),
                            d.detection_type,
                            d.message,
                            d.parent_package or ''
                        ])
        
        print(f"\n{self._color('Results exported to:', self.GREEN)} {output_file}")


class ProgressReporter:
    """Report progress during scanning operations."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.current_task = None
        self.completed_tasks = 0
        self.total_tasks = 0
    
    def start_scan(self, total_tasks: int):
        """Start a new scan operation."""
        self.total_tasks = total_tasks
        self.completed_tasks = 0
        if self.verbose:
            print(f"Starting scan of {total_tasks} location(s)...")
    
    def update(self, task_name: str):
        """Update current task."""
        self.current_task = task_name
        if self.verbose:
            print(f"  Scanning: {task_name}")
    
    def complete_task(self):
        """Mark current task as complete."""
        self.completed_tasks += 1
        if self.verbose and self.total_tasks > 0:
            progress = (self.completed_tasks / self.total_tasks) * 100
            print(f"  Progress: {progress:.1f}% ({self.completed_tasks}/{self.total_tasks})")
    
    def finish(self):
        """Finish the scan operation."""
        if self.verbose:
            print("Scan complete!")


def validate_path(path_str: str) -> Path:
    """
    Validate and convert a path string to Path object.
    
    Args:
        path_str: String path to validate
        
    Returns:
        Path object
        
    Raises:
        ValueError: If path doesn't exist or isn't accessible
    """
    path = Path(path_str).resolve()
    
    if not path.exists():
        raise ValueError(f"Path does not exist: {path}")
    
    if not path.is_dir() and not path.is_file():
        raise ValueError(f"Path is neither a file nor directory: {path}")
    
    return path


def get_project_root(start_path: Path) -> Optional[Path]:
    """
    Find the project root by looking for package.json.
    
    Args:
        start_path: Path to start searching from
        
    Returns:
        Path to project root or None if not found
    """
    current = start_path
    
    if current.is_file():
        current = current.parent
    
    while current != current.parent:
        if (current / 'package.json').exists():
            return current
        current = current.parent
    
    return None