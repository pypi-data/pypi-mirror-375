"""
NPM Vulnerability Scanner

A Python tool to detect compromised npm packages from the September 2025 supply chain attack.
"""

__version__ = "1.1.0"
__author__ = "Michael Bommarito"

from .scanner import NodeScanner
from .checker import DependencyChecker, Severity, DetectionResult
from .cli import NPMVulnerabilityScanner

__all__ = [
    "NodeScanner",
    "DependencyChecker", 
    "Severity",
    "DetectionResult",
    "NPMVulnerabilityScanner",
    "__version__"
]