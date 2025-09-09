# NPM Vulnerability Scanner

A Python-based tool to detect compromised npm packages from the September 8, 2025 supply chain attack. This scanner uses only Python standard library modules (no external dependencies required) and provides intelligent severity-based detection of compromised packages.

## Compromised Versions

The scanner detects specific versions of popular packages that were compromised on September 8, 2025:

| Package | Compromised Versions |
|---------|---------------------|
| **chalk** | 5.6.1, 5.6.2 |
| **debug** | 4.4.2 |
| **ansi-styles** | 6.2.2, 6.2.3 |
| **color-convert** | 3.1.1 |
| **strip-ansi** | 7.1.1, 7.1.2 |
| **ansi-regex** | 6.2.1, 6.2.2 |
| **wrap-ansi** | 9.0.1, 9.0.2 |
| **supports-color** | 10.2.1, 10.2.2 |
| **color-name** | 2.0.1 |
| **is-arrayish** | 0.3.3 |
| **slice-ansi** | 7.1.1, 7.1.2 |
| **error-ex** | 1.3.3 |
| **color-string** | 2.1.1 |
| **simple-swizzle** | 0.2.3 |
| **has-ansi** | 6.0.1, 6.0.2 |
| **supports-hyperlinks** | 4.1.1, 4.1.2 |
| **chalk-template** | 1.1.1, 1.1.2 |
| **backslash** | 0.2.1 |

## Severity Levels

The scanner uses intelligent detection with four severity levels:

### 🚨 **CRITICAL** 
- **What**: Confirmed compromised version is installed or specified
- **Example**: `"debug": "4.4.2"` or found in `node_modules/debug/`
- **Action**: Immediate removal or downgrade required

### ⚠️ **HIGH**
- **What**: Version specification could resolve to compromised version
- **Example**: `"chalk": "^5.6.0"` could install 5.6.1 or 5.6.2
- **Action**: Pin to safe version or verify actual installed version

### ℹ️ **MEDIUM**
- **What**: Package from compromised list but using safe version
- **Example**: `"ansi-styles": "6.2.1"` (safe, not 6.2.2 or 6.2.3)
- **Action**: Monitor for updates, consider alternatives

### ❓ **WARNING**
- **What**: Package found but version cannot be determined
- **Example**: Missing version in package.json
- **Action**: Investigate and specify exact version

## Features

- **Intelligent Severity Detection**: Four-level severity system based on actual risk
- **Semver Range Analysis**: Understands `^`, `~`, `>=` and other version specifiers
- **Actual Version Detection**: Checks `node_modules` folders for installed versions
- **Comprehensive Scanning**: 
  - Direct and dev dependencies in package.json
  - Actual installed versions in node_modules
  - Lock files (package-lock.json, yarn.lock)
  - Global, user, and project installations
- **Parallel Processing**: Uses multiprocessing for efficient scanning
- **Export Options**: Results can be exported to JSON or CSV formats
- **Color-coded Output**: Clear visual indicators for different severity levels
- **No External Dependencies**: Uses only Python standard library

## Installation

### Quick Install with pipx (Recommended)

```bash
# Install with pipx (isolated environment)
pipx install npm-vuln-scanner

# Or run directly without installing
pipx run npm-vuln-scanner scan
```

### Quick Run with uvx

```bash
# Run directly with uvx
uvx npm-vuln-scanner scan
```

### Install with pip

```bash
# Install globally
pip install npm-vuln-scanner

# Or install in virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install npm-vuln-scanner
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/mjbommar/npm-vuln-scanner.git
cd npm-vuln-scanner

# Install in development mode
pip install -e .
```

## Usage

### Basic Commands

After installation, use the `npm-vuln-scanner` command (or `nvs` for short):

```bash
# Scan current directory
npm-vuln-scanner scan
nvs scan  # Short alias

# Scan specific paths
npm-vuln-scanner scan /path/to/project1 /path/to/project2

# Scan with home directory and global npm packages
npm-vuln-scanner scan --include-home --include-global

# Check a specific package.json file
npm-vuln-scanner check package.json

# List all compromised packages being checked
npm-vuln-scanner list
```

### Export Results

```bash
# Export results to JSON
npm-vuln-scanner scan --export-json results.json

# Export results to CSV
npm-vuln-scanner scan --export-csv results.csv

# Export both formats
npm-vuln-scanner scan --export-json results.json --export-csv results.csv
```

### Advanced Options

```bash
# Enable verbose output
npm-vuln-scanner scan -v

# Disable colored output
npm-vuln-scanner scan --no-color

# Check package.json without scanning transitive dependencies
npm-vuln-scanner check package.json --no-transitive
```

### JSON Output (for Automation)

The scanner supports JSON output for integration with CI/CD pipelines and automation tools:

```bash
# Output scan results as JSON
npm-vuln-scanner --json scan

# Check specific package with JSON output
npm-vuln-scanner --json check package.json

# List compromised packages as JSON
npm-vuln-scanner --json list
```

#### Using with jq

```bash
# Get summary of findings
npm-vuln-scanner --json scan | jq '.summary'

# Get only critical findings
npm-vuln-scanner --json scan | jq '.findings.critical[]'

# Count high severity issues
npm-vuln-scanner --json scan | jq '.summary.by_severity.high'

# Get all findings for a specific package
npm-vuln-scanner --json scan | jq '.findings.critical[], .findings.high[] | select(.package_name == "chalk")'

# Format custom output
npm-vuln-scanner --json scan | jq -r '.findings.critical[] | "\(.package_name)@\(.version_spec): \(.message)"'

# Check exit code in JSON
npm-vuln-scanner --json scan | jq '.summary.exit_code'

# Get recommendations
npm-vuln-scanner --json scan | jq '.recommendations.immediate_actions[]' -r
```

### Run Without Installation

```bash
# Using pipx
pipx run npm-vuln-scanner scan

# Using uvx
uvx npm-vuln-scanner scan

# Using Python module directly
python -m npm_vuln_scanner scan
```

## Module Structure

```
npm_vuln_scanner/
├── __init__.py       # Package initialization
├── __main__.py       # Entry point for module execution
├── cli.py           # Command-line interface
├── scanner.py       # Node.js installation scanner
├── checker.py       # Vulnerability detection logic
└── utils.py         # Formatting and utilities
```

## Exit Codes

- `0`: No packages from the compromised list detected
- `1`: Any packages from the compromised list found (regardless of severity) or error occurred
- `130`: Scan interrupted by user (Ctrl+C)

## Performance

The scanner uses parallel processing to efficiently scan large codebases:
- Concurrent directory traversal
- Parallel package.json and node_modules checking
- Configurable worker threads for optimal performance

## Recommendations

When compromised packages are detected:

1. **Review each detection** and assess the risk to your project
2. **Check for security advisories** and available patches
3. **Update to patched versions** if available
4. **Consider alternative packages** if no patches exist
5. **Run npm audit** or yarn audit for additional security checks
6. **Monitor official security channels** for updates

## Example Output

```
================================================================================
                           NPM Vulnerability Scanner                            
================================================================================

Checking /home/user/project/package.json
🚨 CRITICAL: 2 confirmed compromised version(s) found!
⚠️  HIGH: 1 package(s) could install compromised versions
ℹ️  MEDIUM: 1 package(s) present but using safe versions

🚨 CRITICAL - Confirmed Compromised Versions
-------------------------------------------

  debug
    Specified in: /home/user/project/package.json
    Version spec: 4.4.2
    Type: direct
    Exact compromised version specified: 4.4.2

  wrap-ansi
    Installed in: /home/user/project/node_modules/wrap-ansi
    Installed version: 9.0.1
    Type: installed
    CONFIRMED: Compromised version 9.0.1 is installed

⚠️  HIGH - Could Install Compromised Versions
---------------------------------------------

  chalk
    Specified in: /home/user/project/package.json
    Version spec: ^5.6.0
    Type: direct
    Caret range ^5.6.0 can resolve to 5.6.1

ℹ️  MEDIUM - Safe Versions Specified
------------------------------------

  ansi-styles
    Specified in: /home/user/project/package.json
    Version spec: 6.2.1
    Type: dev
    Exact version 6.2.1 is safe

Scan Summary
------------
  Paths scanned: 1
  Total findings: 4
  By severity:
    • CRITICAL: 2
    • HIGH: 1
    • MEDIUM: 1
  Scan duration: 0.52 seconds

🚨 IMMEDIATE ACTION REQUIRED
---------------------------
  1. You have CONFIRMED compromised packages installed!
  2. These packages contain malicious code targeting crypto wallets
  3. Immediately downgrade or remove these packages
  4. Check for any suspicious transactions if your app handles crypto
  5. Rotate any exposed credentials or keys
```

## License

This tool is provided as-is for security scanning purposes.