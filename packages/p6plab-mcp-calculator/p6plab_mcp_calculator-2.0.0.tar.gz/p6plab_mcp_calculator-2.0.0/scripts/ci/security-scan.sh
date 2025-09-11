#!/bin/bash
# Comprehensive security scanning with bandit
set -e

echo "🔒 Running security scan with bandit..."

# Create reports directory if it doesn't exist
mkdir -p reports

# Check if bandit is installed
if ! command -v bandit &> /dev/null; then
    echo "❌ bandit is not installed. Installing..."
    pip install bandit>=1.7.0
fi

# Run bandit with JSON output for CI/CD integration
echo "📊 Generating detailed security report..."
bandit -r calculator/ -f json -o reports/security-report.json || true

# Run bandit with console output for developer feedback
echo "🔍 Scanning for High and Medium severity issues..."
bandit -r calculator/ -ll || true

# Check for High/Medium severity issues
echo "✅ Security scan completed - check reports/security-report.json for details"

# Parse JSON report to check severity levels
python3 -c "
import json
import sys
import os

if not os.path.exists('reports/security-report.json'):
    print('❌ Security report not found')
    sys.exit(1)

try:
    with open('reports/security-report.json', 'r') as f:
        report = json.load(f)
    
    results = report.get('results', [])
    high_issues = [issue for issue in results if issue.get('issue_severity') == 'HIGH']
    medium_issues = [issue for issue in results if issue.get('issue_severity') == 'MEDIUM']
    low_issues = [issue for issue in results if issue.get('issue_severity') == 'LOW']
    
    print(f'📈 Security scan summary:')
    print(f'   High severity: {len(high_issues)} issues')
    print(f'   Medium severity: {len(medium_issues)} issues')
    print(f'   Low severity: {len(low_issues)} issues')
    
    if high_issues:
        print(f'❌ {len(high_issues)} HIGH severity issues found - deployment blocked')
        for issue in high_issues:
            print(f'   - {issue.get(\"test_name\", \"Unknown\")}: {issue.get(\"issue_text\", \"No description\")}')
        sys.exit(1)
    elif medium_issues:
        print(f'⚠️  {len(medium_issues)} MEDIUM severity issues found - fix before release')
        for issue in medium_issues:
            print(f'   - {issue.get(\"test_name\", \"Unknown\")}: {issue.get(\"issue_text\", \"No description\")}')
        sys.exit(1)
    else:
        print('✅ No High or Medium severity security issues found')
        if low_issues:
            print(f'ℹ️  {len(low_issues)} Low severity issues found (acceptable)')
        sys.exit(0)
        
except Exception as e:
    print(f'❌ Error parsing security report: {e}')
    sys.exit(1)
"

echo "🎉 Security scanning completed successfully"