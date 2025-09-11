# CI/CD Integration Guide

This document provides comprehensive guidance for integrating the Scientific Calculator MCP Server v2.0.0 into CI/CD pipelines, including security scanning, testing, and deployment automation.

## Related Documentation

- **[Security Guide](security.md)** - Security features and troubleshooting
- **[Developer Guide](DEVELOPER_GUIDE.md)** - Development setup and contribution
- **[Scripts and Tools](SCRIPTS_AND_TOOLS.md)** - Available development scripts
- **[Release Guide](RELEASE.md)** - Release process and deployment
- **[Deployment Guide](deployment.md)** - Production deployment options

## Overview

Security scanning is automatically integrated into the development workflow and should be included in all CI/CD pipelines to ensure code security before deployment.

## GitHub Actions Integration

### Basic Security Workflow

Create `.github/workflows/security.yml`:

```yaml
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  security:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install bandit>=1.7.0
        
    - name: Run security scan
      run: |
        chmod +x scripts/ci/security-scan.sh
        ./scripts/ci/security-scan.sh
        
    - name: Upload security report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: security-report
        path: reports/security-report.json
        retention-days: 30
```

### Complete CI/CD Pipeline with Security

Create `.github/workflows/ci.yml`:

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  release:
    types: [ published ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']
        
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
        
    - name: Run comprehensive tests (includes security scan)
      run: |
        chmod +x scripts/dev/run-tests.sh
        ./scripts/dev/run-tests.sh
        
    - name: Upload test coverage
      uses: codecov/codecov-action@v3
      if: matrix.python-version == '3.11'
      
    - name: Upload security report
      uses: actions/upload-artifact@v3
      if: always() && matrix.python-version == '3.11'
      with:
        name: security-report-${{ github.sha }}
        path: reports/security-report.json

  security-only:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install bandit
      run: pip install bandit>=1.7.0
        
    - name: Run security scan only
      run: |
        chmod +x scripts/ci/security-scan.sh
        ./scripts/ci/security-scan.sh
        
    - name: Comment PR with security results
      uses: actions/github-script@v6
      if: always()
      with:
        script: |
          const fs = require('fs');
          try {
            const report = JSON.parse(fs.readFileSync('reports/security-report.json', 'utf8'));
            const metrics = report.metrics._totals;
            
            const comment = `## 🔒 Security Scan Results
            
            - **High Severity**: ${metrics['SEVERITY.HIGH'] || 0} issues
            - **Medium Severity**: ${metrics['SEVERITY.MEDIUM'] || 0} issues  
            - **Low Severity**: ${metrics['SEVERITY.LOW'] || 0} issues
            
            ${metrics['SEVERITY.HIGH'] > 0 ? '❌ **Deployment blocked due to High severity issues**' : 
              metrics['SEVERITY.MEDIUM'] > 0 ? '⚠️ **Fix Medium severity issues before release**' : 
              '✅ **No High or Medium severity security issues found**'}
            
            <details>
            <summary>View detailed report</summary>
            
            \`\`\`json
            ${JSON.stringify(report.results, null, 2)}
            \`\`\`
            </details>`;
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
          } catch (error) {
            console.log('Could not read security report:', error);
          }

  build:
    needs: [test, security-only]
    runs-on: ubuntu-latest
    if: github.event_name == 'push' || github.event_name == 'release'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
        
    - name: Build package (includes security scan)
      run: |
        chmod +x scripts/deployment/build-package.sh
        ./scripts/deployment/build-package.sh
        
    - name: Upload build artifacts
      uses: actions/upload-artifact@v3
      with:
        name: dist-${{ github.sha }}
        path: dist/

  deploy-test-pypi:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment: test-pypi
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Download build artifacts
      uses: actions/download-artifact@v3
      with:
        name: dist-${{ github.sha }}
        path: dist/
        
    - name: Publish to Test PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.TEST_PYPI_API_TOKEN }}
      run: |
        pip install twine
        twine upload --repository testpypi dist/*

  deploy-pypi:
    needs: build
    runs-on: ubuntu-latest
    if: github.event_name == 'release'
    environment: pypi
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Download build artifacts
      uses: actions/download-artifact@v3
      with:
        name: dist-${{ github.sha }}
        path: dist/
        
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: |
        pip install twine
        twine upload dist/*
```

## GitLab CI Integration

Create `.gitlab-ci.yml`:

```yaml
stages:
  - security
  - test
  - build
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/
    - venv/

security-scan:
  stage: security
  image: python:3.11
  before_script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install bandit>=1.7.0
  script:
    - chmod +x scripts/ci/security-scan.sh
    - ./scripts/ci/security-scan.sh
  artifacts:
    reports:
      junit: reports/security-report.json
    paths:
      - reports/
    expire_in: 30 days
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_COMMIT_BRANCH == "develop"

test:
  stage: test
  image: python:3.11
  needs: ["security-scan"]
  before_script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install -e ".[dev]"
  script:
    - chmod +x scripts/dev/run-tests.sh
    - ./scripts/dev/run-tests.sh
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/
    expire_in: 30 days

build:
  stage: build
  image: python:3.11
  needs: ["test"]
  before_script:
    - python -m venv venv
    - source venv/bin/activate
    - pip install -e ".[dev]"
  script:
    - chmod +x scripts/deployment/build-package.sh
    - ./scripts/deployment/build-package.sh
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_COMMIT_BRANCH == "develop"
    - if: $CI_COMMIT_TAG

deploy-test-pypi:
  stage: deploy
  image: python:3.11
  needs: ["build"]
  before_script:
    - pip install twine
  script:
    - twine upload --repository testpypi dist/*
  environment:
    name: test-pypi
    url: https://test.pypi.org/project/p6plab-mcp-calculator/
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"

deploy-pypi:
  stage: deploy
  image: python:3.11
  needs: ["build"]
  before_script:
    - pip install twine
  script:
    - twine upload dist/*
  environment:
    name: pypi
    url: https://pypi.org/project/p6plab-mcp-calculator/
  rules:
    - if: $CI_COMMIT_TAG
  when: manual
```

## Jenkins Pipeline Integration

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    environment {
        PYTHON_VERSION = '3.11'
    }
    
    stages {
        stage('Setup') {
            steps {
                sh '''
                    python${PYTHON_VERSION} -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -e ".[dev]"
                '''
            }
        }
        
        stage('Security Scan') {
            steps {
                sh '''
                    . venv/bin/activate
                    chmod +x scripts/ci/security-scan.sh
                    ./scripts/ci/security-scan.sh
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'reports/security-report.json', fingerprint: true
                    publishHTML([
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'reports',
                        reportFiles: 'security-report.json',
                        reportName: 'Security Report'
                    ])
                }
                failure {
                    emailext (
                        subject: "Security Scan Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                        body: "Security scan failed. Check the build logs for details.",
                        to: "${env.CHANGE_AUTHOR_EMAIL}"
                    )
                }
            }
        }
        
        stage('Test') {
            steps {
                sh '''
                    . venv/bin/activate
                    chmod +x scripts/dev/run-tests.sh
                    ./scripts/dev/run-tests.sh
                '''
            }
            post {
                always {
                    publishTestResults testResultsPattern: 'test-results.xml'
                    publishCoverage adapters: [
                        coberturaAdapter('coverage.xml')
                    ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                }
            }
        }
        
        stage('Build') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    tag pattern: 'v\\d+\\.\\d+\\.\\d+', comparator: 'REGEXP'
                }
            }
            steps {
                sh '''
                    . venv/bin/activate
                    chmod +x scripts/deployment/build-package.sh
                    ./scripts/deployment/build-package.sh
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'dist/*', fingerprint: true
                }
            }
        }
        
        stage('Deploy to Test PyPI') {
            when { branch 'develop' }
            steps {
                withCredentials([string(credentialsId: 'test-pypi-token', variable: 'TWINE_PASSWORD')]) {
                    sh '''
                        . venv/bin/activate
                        pip install twine
                        TWINE_USERNAME=__token__ twine upload --repository testpypi dist/*
                    '''
                }
            }
        }
        
        stage('Deploy to PyPI') {
            when { tag pattern: 'v\\d+\\.\\d+\\.\\d+', comparator: 'REGEXP' }
            steps {
                input message: 'Deploy to production PyPI?', ok: 'Deploy'
                withCredentials([string(credentialsId: 'pypi-token', variable: 'TWINE_PASSWORD')]) {
                    sh '''
                        . venv/bin/activate
                        pip install twine
                        TWINE_USERNAME=__token__ twine upload dist/*
                    '''
                }
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        failure {
            emailext (
                subject: "Build Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Build failed. Check the build logs for details.",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

## Azure DevOps Integration

Create `azure-pipelines.yml`:

```yaml
trigger:
  branches:
    include:
    - main
    - develop
  tags:
    include:
    - v*

pr:
  branches:
    include:
    - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'

stages:
- stage: Security
  displayName: 'Security Scan'
  jobs:
  - job: SecurityScan
    displayName: 'Run Security Scan'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
      displayName: 'Use Python $(pythonVersion)'
      
    - script: |
        python -m pip install --upgrade pip
        pip install bandit>=1.7.0
      displayName: 'Install bandit'
      
    - script: |
        chmod +x scripts/ci/security-scan.sh
        ./scripts/ci/security-scan.sh
      displayName: 'Run security scan'
      
    - task: PublishTestResults@2
      condition: always()
      inputs:
        testResultsFiles: 'reports/security-report.json'
        testRunTitle: 'Security Scan Results'
      displayName: 'Publish security results'

- stage: Test
  displayName: 'Test'
  dependsOn: Security
  jobs:
  - job: Test
    displayName: 'Run Tests'
    strategy:
      matrix:
        Python38:
          pythonVersion: '3.8'
        Python39:
          pythonVersion: '3.9'
        Python310:
          pythonVersion: '3.10'
        Python311:
          pythonVersion: '3.11'
        Python312:
          pythonVersion: '3.12'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
      displayName: 'Use Python $(pythonVersion)'
      
    - script: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
      displayName: 'Install dependencies'
      
    - script: |
        chmod +x scripts/dev/run-tests.sh
        ./scripts/dev/run-tests.sh
      displayName: 'Run comprehensive tests'
      
    - task: PublishTestResults@2
      condition: always()
      inputs:
        testResultsFiles: '**/test-*.xml'
        testRunTitle: 'Python $(pythonVersion)'
      displayName: 'Publish test results'
      
    - task: PublishCodeCoverageResults@1
      inputs:
        codeCoverageTool: Cobertura
        summaryFileLocation: '$(System.DefaultWorkingDirectory)/**/coverage.xml'

- stage: Build
  displayName: 'Build'
  dependsOn: Test
  condition: and(succeeded(), or(eq(variables['Build.SourceBranch'], 'refs/heads/main'), eq(variables['Build.SourceBranch'], 'refs/heads/develop'), startsWith(variables['Build.SourceBranch'], 'refs/tags/v')))
  jobs:
  - job: Build
    displayName: 'Build Package'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
      displayName: 'Use Python $(pythonVersion)'
      
    - script: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"
      displayName: 'Install dependencies'
      
    - script: |
        chmod +x scripts/deployment/build-package.sh
        ./scripts/deployment/build-package.sh
      displayName: 'Build package'
      
    - task: PublishBuildArtifacts@1
      inputs:
        pathToPublish: 'dist'
        artifactName: 'dist'
      displayName: 'Publish build artifacts'

- stage: Deploy
  displayName: 'Deploy'
  dependsOn: Build
  condition: and(succeeded(), or(eq(variables['Build.SourceBranch'], 'refs/heads/develop'), startsWith(variables['Build.SourceBranch'], 'refs/tags/v')))
  jobs:
  - deployment: DeployTestPyPI
    condition: eq(variables['Build.SourceBranch'], 'refs/heads/develop')
    displayName: 'Deploy to Test PyPI'
    environment: 'test-pypi'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'
            displayName: 'Use Python $(pythonVersion)'
            
          - script: |
              pip install twine
              TWINE_USERNAME=__token__ TWINE_PASSWORD=$(TEST_PYPI_TOKEN) twine upload --repository testpypi $(Pipeline.Workspace)/dist/*
            displayName: 'Upload to Test PyPI'
            
  - deployment: DeployPyPI
    condition: startsWith(variables['Build.SourceBranch'], 'refs/tags/v')
    displayName: 'Deploy to PyPI'
    environment: 'pypi'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '$(pythonVersion)'
            displayName: 'Use Python $(pythonVersion)'
            
          - script: |
              pip install twine
              TWINE_USERNAME=__token__ TWINE_PASSWORD=$(PYPI_TOKEN) twine upload $(Pipeline.Workspace)/dist/*
            displayName: 'Upload to PyPI'
```

## Security Configuration Best Practices

### Environment Variables

Set these environment variables in your CI/CD system:

```bash
# PyPI deployment tokens
PYPI_API_TOKEN=pypi-...
TEST_PYPI_API_TOKEN=pypi-...

# Security scanning configuration
BANDIT_CONFIG_FILE=.bandit
SECURITY_SCAN_FAIL_ON_HIGH=true
SECURITY_SCAN_FAIL_ON_MEDIUM=true
```

### Secret Management

1. **Never commit secrets to version control**
2. **Use CI/CD secret management systems**
3. **Rotate tokens regularly**
4. **Use least-privilege access tokens**

### Notification Configuration

Configure notifications for security scan failures:

```yaml
# GitHub Actions notification
- name: Notify on security failure
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    text: 'Security scan failed in ${{ github.repository }}'
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

## Monitoring and Alerting

### Security Metrics to Track

1. **Security scan pass/fail rates**
2. **Time to fix security issues**
3. **Number of security issues by severity**
4. **Security scan execution time**

### Dashboard Integration

Integrate security metrics into your monitoring dashboards:

- **Grafana**: Create security scan dashboards
- **DataDog**: Track security metrics
- **New Relic**: Monitor security scan performance

## Troubleshooting CI/CD Security Integration

### Common Issues

1. **Permission denied on scripts**: Ensure `chmod +x` is run
2. **Bandit not found**: Install bandit in CI environment
3. **Report parsing failures**: Check JSON report format
4. **False positive handling**: Update `.bandit` configuration

### Debug Commands

```bash
# Test security scan locally
./scripts/ci/security-scan.sh

# Check bandit configuration
bandit --help

# Validate JSON report
python -c "import json; print(json.load(open('reports/security-report.json')))"
```

This comprehensive CI/CD integration ensures security scanning is properly integrated into your development workflow across multiple platforms.