# Security Guide v2.0.0

This document provides comprehensive security information for the Scientific Calculator MCP Server v2.0.0, including security scanning, best practices, production security features, and troubleshooting.

## Overview

The Scientific Calculator MCP Server v2.0.0 implements comprehensive security measures including automated security scanning, input validation, resource limits, and audit logging. The system has achieved **zero high/medium severity security issues** through rigorous security practices.

## Security Features

### 🛡️ **Production Security**
- **Zero High/Medium Security Issues** (Bandit validated)
- **No Code Injection** - SymPy for safe expression parsing
- **Input Validation** - Comprehensive Pydantic model validation
- **Resource Limits** - Configurable computation time (30s) and memory (512MB) limits
- **Audit Logging** - Complete operation tracking
- **Privacy Controls** - External APIs disabled by default

### 🔒 **Multi-Layer Security**
1. **Input Validation & Sanitization**
2. **Resource Protection & Limits**
3. **Security Monitoring & Auditing**
4. **Production Security Hardening**

## Security Scanning

The project uses [bandit](https://bandit.readthedocs.io/) for automated security scanning of Python code. Security scanning is integrated into the development workflow to identify and fix security vulnerabilities before deployment.

## Security Scanning Process

### Automated Integration

Security scanning is automatically integrated into:

1. **Development Testing**: `./scripts/dev/run-tests.sh` includes security scanning
2. **Package Building**: `./scripts/deployment/build-package.sh` runs security scan before building
3. **CI/CD Pipeline**: Security scanning blocks deployment if High/Medium severity issues are found

### Manual Security Scanning

To run security scanning manually:

```bash
# Run security scan
./scripts/ci/security-scan.sh

# Or run bandit directly
bandit -r calculator/ -ll  # Show only High and Medium severity
bandit -r calculator/ -f json -o reports/security-report.json  # Generate JSON report
```

## Severity Levels

### High Severity
- **Action Required**: Must be fixed before deployment
- **Build Impact**: Blocks deployment completely
- **Examples**: SQL injection, command injection, hardcoded passwords

### Medium Severity  
- **Action Required**: Must be fixed before release
- **Build Impact**: Blocks release but allows development builds
- **Examples**: Insecure random generators, weak cryptographic keys

### Low Severity
- **Action Required**: May be left unfixed with proper justification
- **Build Impact**: Does not block builds or deployment
- **Examples**: Use of assert statements, weak SSL/TLS protocols in test code

## Configuration

### Bandit Configuration (`.bandit`)

```ini
[bandit]
exclude_dirs = ["tests", "venv", "dist", "build", "__pycache__", ".git", ".kiro"]
skips = ["B101"]  # Skip assert_used test for test files
severity = ["high", "medium", "low"]

[bandit.blacklist]
# Mathematical operations may use eval-like functions safely
# B307: Use of possibly insecure function - consider using safer alternatives

[bandit.hardcoded_password_string]
# Exclude test files and configuration examples
word_list = ["tests/", "examples/", "docs/"]

[bandit.assert_used]
# Skip assert statements in test files
skips = ["*test*.py", "tests/*"]
```

### Excluded Directories

The following directories are excluded from security scanning:
- `tests/` - Test files may contain intentionally insecure code for testing
- `venv/` - Virtual environment dependencies
- `dist/` - Distribution packages
- `build/` - Build artifacts
- `__pycache__/` - Python cache files
- `.git/` - Git repository files
- `.kiro/` - Kiro IDE configuration

## Common Security Issues and Remediation

### B101: assert_used
**Issue**: Use of assert statement detected
**Remediation**: Replace assert statements with proper error handling in production code
**Example**:
```python
# Instead of:
assert x > 0, "x must be positive"

# Use:
if x <= 0:
    raise ValueError("x must be positive")
```

### B307: eval_used
**Issue**: Use of possibly insecure function
**Remediation**: Use safer alternatives like `ast.literal_eval()` or SymPy parsing
**Example**:
```python
# Instead of:
result = eval(expression)

# Use:
import sympy as sp
result = sp.sympify(expression).evalf()
```

### B108: hardcoded_tmp_directory
**Issue**: Hardcoded temporary file/directory
**Remediation**: Use `tempfile` module for secure temporary files
**Example**:
```python
# Instead of:
temp_file = "/tmp/myfile.txt"

# Use:
import tempfile
with tempfile.NamedTemporaryFile() as temp_file:
    # Use temp_file.name
```

## Security Scanning Reports

### Report Location
Security scan reports are generated in the `reports/` directory:
- `reports/security-report.json` - Detailed JSON report for CI/CD integration
- Console output provides immediate feedback during development

### Report Format
The JSON report contains:
```json
{
  "results": [
    {
      "code": "code snippet",
      "filename": "path/to/file.py",
      "issue_confidence": "HIGH|MEDIUM|LOW",
      "issue_severity": "HIGH|MEDIUM|LOW",
      "issue_text": "Description of the issue",
      "line_number": 42,
      "line_range": [40, 44],
      "test_id": "B101",
      "test_name": "assert_used"
    }
  ],
  "metrics": {
    "loc": 1234,
    "nosec": 0
  }
}
```

## Troubleshooting

### False Positives

If bandit reports false positives, you can:

1. **Update Configuration**: Add exclusions to `.bandit` file
2. **Use # nosec Comment**: Add `# nosec` to specific lines
3. **Skip Specific Tests**: Add test IDs to `skips` in configuration

Example:
```python
# This is safe in our mathematical context
result = eval(safe_expression)  # nosec B307
```

### Installation Issues

If bandit is not installed:
```bash
# Install bandit
pip install bandit>=1.7.0

# Or install all dev dependencies
pip install -e ".[dev]"
```

### Permission Issues

If the security scan script is not executable:
```bash
chmod +x scripts/ci/security-scan.sh
```

## Best Practices

### Development Workflow

1. **Run Security Scans Regularly**: Include security scanning in your regular development workflow
2. **Fix Issues Early**: Address security issues as soon as they're identified
3. **Review Low Severity Issues**: Even if allowed, review and document low severity issues
4. **Keep Dependencies Updated**: Regularly update security scanning tools

### Code Review

1. **Security-First Mindset**: Consider security implications during code review
2. **Validate External Inputs**: Always validate and sanitize external inputs
3. **Use Secure Libraries**: Prefer well-established, secure libraries
4. **Avoid Dangerous Functions**: Avoid `eval()`, `exec()`, and similar dangerous functions

### CI/CD Integration

1. **Fail Fast**: Configure CI/CD to fail immediately on High/Medium severity issues
2. **Generate Reports**: Always generate and archive security scan reports
3. **Monitor Trends**: Track security issues over time to identify patterns
4. **Automate Remediation**: Where possible, automate the fixing of common security issues

## Security Scanning in CI/CD

### GitHub Actions Example

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install bandit
      - name: Run security scan
        run: |
          ./scripts/ci/security-scan.sh
      - name: Upload security report
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: security-report
          path: reports/security-report.json
```

## Additional Resources

- [Bandit Documentation](https://bandit.readthedocs.io/)
- [OWASP Python Security](https://owasp.org/www-project-python-security/)
- [Python Security Best Practices](https://python.org/dev/security/)
- [Secure Coding Guidelines](https://wiki.sei.cmu.edu/confluence/display/python/SEI+CERT+Oracle+Coding+Standard+for+Java)

---

# Security Scanning Troubleshooting

This section helps resolve common issues with security scanning in the Scientific Calculator MCP Server.

## Common Issues and Solutions

### 1. Security Scan Script Not Executable

**Error:**
```bash
bash: ./scripts/ci/security-scan.sh: Permission denied
```

**Solution:**
```bash
chmod +x scripts/ci/security-scan.sh
```

### 2. Bandit Not Found

**Error:**
```bash
bandit: command not found
```

**Solutions:**
```bash
# Install bandit
pip install bandit>=1.7.0

# Or install all dev dependencies
pip install -e ".[dev]"

# Or use the script which auto-installs
./scripts/ci/security-scan.sh
```

### 3. Reports Directory Missing

**Error:**
```bash
FileNotFoundError: [Errno 2] No such file or directory: 'reports/security-report.json'
```

**Solution:**
```bash
mkdir -p reports
./scripts/ci/security-scan.sh
```

### 4. JSON Report Parsing Errors

**Error:**
```bash
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**Causes and Solutions:**
- **Empty report file**: Run bandit scan again
- **Corrupted JSON**: Delete and regenerate report
- **Permission issues**: Check file permissions

```bash
# Clean and regenerate
rm -f reports/security-report.json
./scripts/ci/security-scan.sh

# Check file contents
cat reports/security-report.json | head -10
```

### 5. False Positive Issues

**Issue:** Bandit reports security issues that are actually safe in context

**Solutions:**

#### Option 1: Update .bandit Configuration
```ini
# Add to .bandit file
[bandit.blacklist]
B307 = "Use of possibly insecure function - consider using safer alternatives"

[bandit.assert_used]
skips = ["*test*.py", "tests/*"]
```

#### Option 2: Use # nosec Comments
```python
# This is safe in our mathematical context
result = eval(safe_expression)  # nosec B307
```

#### Option 3: Skip Specific Tests
```ini
# In .bandit file
[bandit]
skips = ["B101", "B307"]
```

### 6. CI/CD Integration Issues

#### GitHub Actions Permission Errors
```yaml
# Add to workflow
- name: Make scripts executable
  run: chmod +x scripts/ci/security-scan.sh
```

#### GitLab CI Script Errors
```yaml
# In .gitlab-ci.yml
before_script:
  - chmod +x scripts/ci/security-scan.sh
```

#### Jenkins Pipeline Issues
```groovy
// In Jenkinsfile
sh 'chmod +x scripts/ci/security-scan.sh'
```

### 7. High/Medium Severity Issues Blocking Build

**Error:**
```bash
❌ 1 HIGH severity issues found - deployment blocked
```

**Resolution Process:**

1. **Identify the Issue:**
```bash
./scripts/ci/security-scan.sh
# Or check the detailed report
cat reports/security-report.json | jq '.results[]'
```

2. **Common High Severity Issues:**

#### B324: Use of weak MD5 hash
```python
# Instead of:
hashlib.md5(data.encode()).hexdigest()

# Use:
hashlib.sha256(data.encode()).hexdigest()
# Or if not for security:
hashlib.md5(data.encode(), usedforsecurity=False).hexdigest()  # Python 3.9+
```

#### B506: Test for use of yaml.load
```python
# Instead of:
yaml.load(data)

# Use:
yaml.safe_load(data)
```

#### B108: Hardcoded tmp directory
```python
# Instead of:
temp_file = "/tmp/myfile.txt"

# Use:
import tempfile
with tempfile.NamedTemporaryFile() as temp_file:
    # Use temp_file.name
```

3. **Verify Fix:**
```bash
./scripts/ci/security-scan.sh
```

### 8. Performance Issues with Large Codebases

**Issue:** Security scanning takes too long

**Solutions:**

1. **Exclude Unnecessary Directories:**
```ini
# In .bandit file
[bandit]
exclude_dirs = ["tests", "venv", "dist", "build", "__pycache__", ".git", "node_modules"]
```

2. **Parallel Scanning:**
```bash
# Use multiple processes
bandit -r calculator/ --processes 4
```

3. **Skip Low Severity:**
```bash
# Only scan for High/Medium
bandit -r calculator/ -ll
```

### 9. Configuration File Issues

#### Invalid .bandit Configuration
**Error:**
```bash
configparser.ParsingError: Source contains parsing errors
```

**Solution:**
```bash
# Validate configuration syntax
python -c "
import configparser
config = configparser.ConfigParser()
config.read('.bandit')
print('Configuration is valid')
"
```

#### Missing Configuration Sections
```ini
# Ensure proper section headers
[bandit]
exclude_dirs = ["tests"]

[bandit.blacklist]
# Comments here

[bandit.assert_used]
skips = ["*test*.py"]
```

### 10. Environment-Specific Issues

#### Python Version Compatibility
```bash
# Check Python version
python --version

# Bandit requires Python 3.6+
pip install bandit>=1.7.0
```

#### Virtual Environment Issues
```bash
# Ensure you're in the right environment
which python
which bandit

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

### 11. Security Report Integration Issues

#### Missing Security Metrics
```python
# Check if report has expected structure
import json
with open('reports/security-report.json') as f:
    report = json.load(f)
    print("Metrics:", report.get('metrics', {}))
    print("Results count:", len(report.get('results', [])))
```

#### CI/CD Report Upload Failures
```yaml
# Ensure reports directory exists
- name: Create reports directory
  run: mkdir -p reports

- name: Upload security report
  uses: actions/upload-artifact@v3
  if: always()  # Upload even if scan fails
  with:
    name: security-report
    path: reports/security-report.json
```

## Security Troubleshooting Best Practices

### 1. Enable Debug Mode
```bash
export CALCULATOR_DEBUG_MODE=true
export CALCULATOR_LOG_LEVEL=DEBUG
./scripts/ci/security-scan.sh
```

### 2. Check Dependencies
```bash
pip list | grep bandit
pip check
```

### 3. Validate Environment
```bash
# Check all required tools
which python
which bandit
which pip

# Check permissions
ls -la scripts/ci/security-scan.sh
```

### 4. Test Incrementally
```bash
# Test bandit directly
bandit --version
bandit -r calculator/ --dry-run

# Test script components
chmod +x scripts/ci/security-scan.sh
bash -x scripts/ci/security-scan.sh  # Debug mode
```

### 5. Clean Environment
```bash
# Clean and restart
rm -rf reports/
mkdir -p reports/
./scripts/clean.sh
./scripts/ci/security-scan.sh
```

## Emergency Procedures

### Bypass Security Scan (Development Only)
```bash
# ONLY for development/testing - NOT for production
export CALCULATOR_SKIP_SECURITY_SCAN=true
./scripts/build-uvx-package.sh
```

### Force Build Despite Security Issues
```bash
# Modify security-scan.sh temporarily
# Change exit codes from 1 to 0 for testing
# NEVER commit this change
```

### Rollback Security Configuration
```bash
# Restore default configuration
git checkout .bandit
./scripts/ci/security-scan.sh
```

**Remember**: Security scanning is a critical part of the development process. While these troubleshooting steps can help resolve issues, never permanently disable security scanning in production environments.
