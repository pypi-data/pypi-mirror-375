#!/usr/bin/env python3
"""
Dependency checker module for detecting compromised npm packages.
"""

import json
import re
from pathlib import Path
from typing import List, Set, Dict, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Severity levels for detections."""
    CRITICAL = "critical"  # Confirmed compromised version installed
    HIGH = "high"          # Version spec could resolve to compromised version
    MEDIUM = "medium"      # Package present but safe version specified
    WARNING = "warning"    # Package present but can't determine version


@dataclass
class DetectionResult:
    """Result of package detection."""
    file_path: Path
    package_name: str
    package_version: Optional[str]
    detection_type: str  # 'direct', 'dev', 'transitive', 'installed'
    severity: Severity
    message: str
    actual_version: Optional[str] = None  # For node_modules detections
    parent_package: Optional[str] = None


class SemverChecker:
    """Check if semver ranges could resolve to specific versions."""
    
    @staticmethod
    def parse_version(version_str: str) -> Tuple[int, int, int]:
        """Parse a version string into major, minor, patch tuple."""
        match = re.match(r'(\d+)\.(\d+)\.(\d+)', version_str)
        if match:
            return tuple(map(int, match.groups()))
        return (0, 0, 0)
    
    @staticmethod
    def could_resolve_to(spec: str, target_versions: List[str]) -> Tuple[bool, str]:
        """
        Check if a version spec could resolve to any of the target versions.
        Returns (could_resolve, reason)
        """
        if not spec:
            return True, "No version specified"
        
        spec = spec.strip()
        
        # Exact version
        if re.match(r'^\d+\.\d+\.\d+$', spec):
            if spec in target_versions:
                return True, f"Exact match for compromised version {spec}"
            return False, f"Exact version {spec} is safe"
        
        # Latest or * 
        if spec in ['latest', '*', '']:
            return True, "Could install latest compromised version"
        
        # Caret range (^x.y.z)
        if spec.startswith('^'):
            base_version = spec[1:].strip()
            base_parsed = SemverChecker.parse_version(base_version)
            
            for target in target_versions:
                target_parsed = SemverChecker.parse_version(target)
                # Caret allows changes that do not modify left-most non-zero digit
                if base_parsed[0] == 0:
                    # 0.x.y - can update patch only
                    if target_parsed[0] == 0 and target_parsed[1] == base_parsed[1] and target_parsed[2] >= base_parsed[2]:
                        return True, f"Caret range {spec} can resolve to {target}"
                else:
                    # x.y.z where x>0 - can update minor and patch
                    if target_parsed[0] == base_parsed[0] and (
                        target_parsed[1] > base_parsed[1] or 
                        (target_parsed[1] == base_parsed[1] and target_parsed[2] >= base_parsed[2])
                    ):
                        return True, f"Caret range {spec} can resolve to {target}"
        
        # Tilde range (~x.y.z)
        if spec.startswith('~'):
            base_version = spec[1:].strip()
            base_parsed = SemverChecker.parse_version(base_version)
            
            for target in target_versions:
                target_parsed = SemverChecker.parse_version(target)
                # Tilde allows patch-level changes
                if (target_parsed[0] == base_parsed[0] and 
                    target_parsed[1] == base_parsed[1] and 
                    target_parsed[2] >= base_parsed[2]):
                    return True, f"Tilde range {spec} can resolve to {target}"
        
        # Greater than or equal (>=x.y.z)
        if spec.startswith('>='):
            base_version = spec[2:].strip()
            base_parsed = SemverChecker.parse_version(base_version)
            
            for target in target_versions:
                target_parsed = SemverChecker.parse_version(target)
                if target_parsed >= base_parsed:
                    return True, f"Range {spec} can resolve to {target}"
        
        # Range (x.y.z - a.b.c)
        if ' - ' in spec:
            parts = spec.split(' - ')
            if len(parts) == 2:
                min_parsed = SemverChecker.parse_version(parts[0])
                max_parsed = SemverChecker.parse_version(parts[1])
                
                for target in target_versions:
                    target_parsed = SemverChecker.parse_version(target)
                    if min_parsed <= target_parsed <= max_parsed:
                        return True, f"Range {spec} can resolve to {target}"
        
        # Complex ranges with spaces
        if ' ' in spec:
            # For complex ranges, be conservative
            return True, f"Complex range {spec} might resolve to compromised version"
        
        return False, f"Version spec {spec} appears safe"


class DependencyChecker:
    """Check for compromised dependencies in Node.js projects."""
    
    def __init__(self):
        # Map of package names to compromised versions
        # These versions were published on or after Sept 8, 2025 13:00 UTC
        self.compromised_versions = {
            "chalk": ["5.6.1", "5.6.2"],
            "debug": ["4.4.2"],
            "ansi-styles": ["6.2.2", "6.2.3"],
            "color-convert": ["3.1.1"],
            "strip-ansi": ["7.1.1", "7.1.2"],
            "ansi-regex": ["6.2.1", "6.2.2"],
            "wrap-ansi": ["9.0.1", "9.0.2"],
            "supports-color": ["10.2.1", "10.2.2"],
            "color-name": ["2.0.1"],
            "is-arrayish": ["0.3.3"],
            "slice-ansi": ["7.1.1", "7.1.2"],
            "error-ex": ["1.3.3"],
            "color-string": ["2.1.1"],
            "simple-swizzle": ["0.2.3"],
            "has-ansi": ["6.0.1", "6.0.2"],
            "supports-hyperlinks": ["4.1.1", "4.1.2"],
            "chalk-template": ["1.1.1", "1.1.2"],
            "backslash": ["0.2.1"],
        }
        self.compromised_names = set(self.compromised_versions.keys())
        self.semver_checker = SemverChecker()
    
    def check_version_spec(self, package_name: str, version_spec: Optional[str]) -> Tuple[Severity, str]:
        """
        Analyze a version spec to determine severity.
        Returns (severity, message)
        """
        if package_name not in self.compromised_versions:
            return Severity.MEDIUM, "Package not in compromised list"
        
        compromised = self.compromised_versions[package_name]
        
        if not version_spec:
            return Severity.WARNING, f"Package found but no version specified - could be using {', '.join(compromised)}"
        
        # Check if exact version is compromised
        clean_version = re.match(r'^[~^>=<]*\s*(\d+\.\d+\.\d+)', version_spec)
        if clean_version and clean_version.group(1) in compromised:
            return Severity.CRITICAL, f"Exact compromised version specified: {clean_version.group(1)}"
        
        # Check if range could resolve to compromised version
        could_resolve, reason = self.semver_checker.could_resolve_to(version_spec, compromised)
        
        if could_resolve:
            return Severity.HIGH, reason
        else:
            return Severity.MEDIUM, reason
    
    def check_package_json(self, package_json_path: Path) -> List[DetectionResult]:
        """
        Check a package.json file for compromised dependencies.
        """
        results = []
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check direct dependencies
            if 'dependencies' in data:
                for pkg_name, version in data['dependencies'].items():
                    if pkg_name in self.compromised_names:
                        severity, message = self.check_version_spec(pkg_name, version)
                        results.append(DetectionResult(
                            file_path=package_json_path,
                            package_name=pkg_name,
                            package_version=version,
                            detection_type='direct',
                            severity=severity,
                            message=message
                        ))
            
            # Check dev dependencies
            if 'devDependencies' in data:
                for pkg_name, version in data['devDependencies'].items():
                    if pkg_name in self.compromised_names:
                        severity, message = self.check_version_spec(pkg_name, version)
                        results.append(DetectionResult(
                            file_path=package_json_path,
                            package_name=pkg_name,
                            package_version=version,
                            detection_type='dev',
                            severity=severity,
                            message=message
                        ))
            
            # Check optional dependencies
            if 'optionalDependencies' in data:
                for pkg_name, version in data['optionalDependencies'].items():
                    if pkg_name in self.compromised_names:
                        severity, message = self.check_version_spec(pkg_name, version)
                        results.append(DetectionResult(
                            file_path=package_json_path,
                            package_name=pkg_name,
                            package_version=version,
                            detection_type='optional',
                            severity=severity,
                            message=message
                        ))
        
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            pass
        
        return results
    
    def check_node_modules(self, node_modules_path: Path, max_workers: int = 10) -> List[DetectionResult]:
        """
        Check a node_modules directory for actual installed versions.
        """
        results = []
        
        if not node_modules_path.exists() or not node_modules_path.is_dir():
            return results
        
        def check_module_dir(module_path: Path) -> Optional[DetectionResult]:
            """Check a single module directory for actual installed version."""
            if not module_path.is_dir():
                return None
            
            module_name = module_path.name
            
            # Check if this is a potentially compromised package
            if module_name in self.compromised_names:
                # Get the actual installed version from package.json
                actual_version = None
                package_json = module_path / "package.json"
                if package_json.exists():
                    try:
                        with open(package_json, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            actual_version = data.get('version')
                    except:
                        pass
                
                if actual_version:
                    # Check if this actual version is compromised
                    if actual_version in self.compromised_versions[module_name]:
                        return DetectionResult(
                            file_path=module_path,
                            package_name=module_name,
                            package_version=actual_version,
                            actual_version=actual_version,
                            detection_type='installed',
                            severity=Severity.CRITICAL,
                            message=f"CONFIRMED: Compromised version {actual_version} is installed"
                        )
                    else:
                        return DetectionResult(
                            file_path=module_path,
                            package_name=module_name,
                            package_version=actual_version,
                            actual_version=actual_version,
                            detection_type='installed',
                            severity=Severity.MEDIUM,
                            message=f"Safe version {actual_version} is installed"
                        )
                else:
                    # Can't determine version
                    return DetectionResult(
                        file_path=module_path,
                        package_name=module_name,
                        package_version=None,
                        detection_type='installed',
                        severity=Severity.WARNING,
                        message=f"Package found but version cannot be determined"
                    )
            
            return None
        
        # Check immediate subdirectories
        try:
            module_dirs = []
            
            # Direct packages
            for item in node_modules_path.iterdir():
                if item.is_dir():
                    if item.name.startswith('@'):
                        # Scoped packages
                        try:
                            for scoped_item in item.iterdir():
                                if scoped_item.is_dir():
                                    module_dirs.append(scoped_item)
                        except (PermissionError, OSError):
                            pass
                    else:
                        module_dirs.append(item)
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(check_module_dir, d): d for d in module_dirs}
                
                for future in as_completed(futures):
                    try:
                        result = future.result(timeout=5)
                        if result:
                            results.append(result)
                    except Exception:
                        pass
        
        except (PermissionError, OSError):
            pass
        
        return results
    
    def check_lock_file(self, lock_file_path: Path) -> List[DetectionResult]:
        """
        Check a package-lock.json or yarn.lock file for compromised packages.
        """
        results = []
        
        if lock_file_path.name == 'package-lock.json':
            results = self._check_package_lock(lock_file_path)
        elif lock_file_path.name == 'yarn.lock':
            results = self._check_yarn_lock(lock_file_path)
        
        return results
    
    def _check_package_lock(self, lock_file_path: Path) -> List[DetectionResult]:
        """Check package-lock.json for compromised packages."""
        results = []
        
        try:
            with open(lock_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check dependencies in lockfile v1 format
            if 'dependencies' in data:
                self._check_lock_v1_deps(data['dependencies'], lock_file_path, results)
            
            # Check packages in lockfile v2/v3 format
            if 'packages' in data:
                for pkg_path, pkg_info in data['packages'].items():
                    # Extract package name from path
                    if pkg_path and pkg_path != '':
                        pkg_name = pkg_path.split('node_modules/')[-1]
                        version = pkg_info.get('version')
                        
                        if pkg_name in self.compromised_names and version:
                            if version in self.compromised_versions[pkg_name]:
                                results.append(DetectionResult(
                                    file_path=lock_file_path,
                                    package_name=pkg_name,
                                    package_version=version,
                                    detection_type='transitive',
                                    severity=Severity.CRITICAL,
                                    message=f"Lock file specifies compromised version {version}"
                                ))
                            else:
                                results.append(DetectionResult(
                                    file_path=lock_file_path,
                                    package_name=pkg_name,
                                    package_version=version,
                                    detection_type='transitive',
                                    severity=Severity.MEDIUM,
                                    message=f"Lock file specifies safe version {version}"
                                ))
        
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            pass
        
        return results
    
    def _check_lock_v1_deps(self, deps: Dict, lock_file_path: Path, results: List[DetectionResult], parent: str = None):
        """Recursively check v1 lockfile dependencies."""
        for pkg_name, pkg_info in deps.items():
            version = pkg_info.get('version')
            
            if pkg_name in self.compromised_names and version:
                if version in self.compromised_versions[pkg_name]:
                    results.append(DetectionResult(
                        file_path=lock_file_path,
                        package_name=pkg_name,
                        package_version=version,
                        detection_type='transitive',
                        severity=Severity.CRITICAL,
                        message=f"Lock file specifies compromised version {version}",
                        parent_package=parent
                    ))
                else:
                    results.append(DetectionResult(
                        file_path=lock_file_path,
                        package_name=pkg_name,
                        package_version=version,
                        detection_type='transitive',
                        severity=Severity.MEDIUM,
                        message=f"Lock file specifies safe version {version}",
                        parent_package=parent
                    ))
            
            # Check nested dependencies
            if 'dependencies' in pkg_info:
                self._check_lock_v1_deps(pkg_info['dependencies'], lock_file_path, results, pkg_name)
    
    def _check_yarn_lock(self, lock_file_path: Path) -> List[DetectionResult]:
        """Check yarn.lock for compromised packages."""
        results = []
        
        try:
            with open(lock_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse yarn.lock format
            current_package = None
            current_version = None
            
            for line in content.split('\n'):
                line = line.strip()
                
                # Package declaration line
                if line and not line.startswith(' ') and '@' in line:
                    # Extract package name
                    for pkg_name in self.compromised_names:
                        if pkg_name in line:
                            current_package = pkg_name
                            break
                
                # Version line
                if current_package and line.startswith('version'):
                    match = re.search(r'version\s+"([^"]+)"', line)
                    if match:
                        version = match.group(1)
                        
                        if version in self.compromised_versions[current_package]:
                            results.append(DetectionResult(
                                file_path=lock_file_path,
                                package_name=current_package,
                                package_version=version,
                                detection_type='transitive',
                                severity=Severity.CRITICAL,
                                message=f"Yarn lock specifies compromised version {version}"
                            ))
                        else:
                            results.append(DetectionResult(
                                file_path=lock_file_path,
                                package_name=current_package,
                                package_version=version,
                                detection_type='transitive',
                                severity=Severity.MEDIUM,
                                message=f"Yarn lock specifies safe version {version}"
                            ))
                        
                        current_package = None
        
        except (FileNotFoundError, PermissionError):
            pass
        
        return results
    
    def check_all(self, package_files: List[Path], node_modules_dirs: List[Path], max_workers: int = 10) -> Dict[str, List[DetectionResult]]:
        """
        Check all provided package files and node_modules directories.
        """
        all_results = {
            'critical': [],
            'high': [],
            'medium': [],
            'warning': []
        }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit package.json checks
            package_futures = {
                executor.submit(self.check_package_json, path): path 
                for path in package_files
            }
            
            # Submit node_modules checks
            modules_futures = {
                executor.submit(self.check_node_modules, path): path 
                for path in node_modules_dirs
            }
            
            # Check for lock files alongside package.json files
            lock_futures = {}
            for package_file in package_files:
                parent_dir = package_file.parent
                
                # Check for package-lock.json
                package_lock = parent_dir / 'package-lock.json'
                if package_lock.exists():
                    lock_futures[executor.submit(self.check_lock_file, package_lock)] = package_lock
                
                # Check for yarn.lock
                yarn_lock = parent_dir / 'yarn.lock'
                if yarn_lock.exists():
                    lock_futures[executor.submit(self.check_lock_file, yarn_lock)] = yarn_lock
            
            # Collect all results
            all_futures = list(package_futures.keys()) + list(modules_futures.keys()) + list(lock_futures.keys())
            
            for future in as_completed(all_futures):
                try:
                    results = future.result(timeout=30)
                    for result in results:
                        if result.severity == Severity.CRITICAL:
                            all_results['critical'].append(result)
                        elif result.severity == Severity.HIGH:
                            all_results['high'].append(result)
                        elif result.severity == Severity.MEDIUM:
                            all_results['medium'].append(result)
                        elif result.severity == Severity.WARNING:
                            all_results['warning'].append(result)
                except Exception:
                    pass
        
        return all_results