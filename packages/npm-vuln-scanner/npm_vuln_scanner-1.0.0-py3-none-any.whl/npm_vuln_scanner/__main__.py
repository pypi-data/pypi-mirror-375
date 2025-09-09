#!/usr/bin/env python3
"""
Main entry point for npm-vuln-scanner when run as a module.

This allows the package to be run with:
    python -m npm_vuln_scanner
    pipx run npm-vuln-scanner
    uvx npm-vuln-scanner
"""

import sys
from .cli import main

if __name__ == '__main__':
    sys.exit(main())