# Testing GitHub Actions Workflows Locally

This guide explains how to test the `.github/workflows/deploy.yml` workflow file locally before pushing to GitHub.

## Prerequisites

1. **Docker** - Required for `act` to run GitHub Actions locally
   - Install: https://www.docker.com/get-started
   - Make sure Docker is running

2. **act** - Local GitHub Actions runner
   ```bash
   # macOS
   brew install act
   
   # Linux
   curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
   
   # Windows (use WSL)
   # Or download from: https://github.com/nektos/act/releases
   ```

## Quick Start

Use the provided test script:

```bash
chmod +x .github/act-test.sh
./github/act-test.sh
```

## Manual Testing Methods

### 1. Test Frontend Build Steps Only (Safest)

This tests the Node.js setup and frontend build without attempting deployment:

```bash
act push -b staging \
  --job deploy-staging \
  --dryrun \
  --workflows .github/workflows/deploy.yml \
  --step "Setup Node.js" \
  --step "Install frontend dependencies" \
  --step "Build frontend"
```

### 2. Validate YAML Syntax

Check if the workflow file has syntax errors:

```bash
# Using act
act push -b staging --dryrun --workflows .github/workflows/deploy.yml

# Using yamllint (if installed)
yamllint .github/workflows/deploy.yml

# Using GitHub CLI (if installed)
gh workflow view deploy.yml
```

### 3. Test with Secrets (Dry Run)

Create a `.secrets` file in the project root:

```bash
# .secrets file (already in .gitignore)
SSH_PRIVATE_KEY=test-key-here
SSH_USER=test-user
SSH_HOST=login.toolforge.org
TARGET_DIR=www/python/src/
GITHUB_REPO=https://github.com/indictechcom/wikicontest.git
```

Then test:

```bash
# Test staging workflow
act push -b staging \
  --job deploy-staging \
  --dryrun \
  --workflows .github/workflows/deploy.yml \
  --secret-file .secrets

# Test production workflow
act push -b main \
  --job deploy-production \
  --dryrun \
  --workflows .github/workflows/deploy.yml \
  --secret-file .secrets
```

### 4. Test Specific Steps

Test individual steps to debug issues:

```bash
# List all steps
act push -b staging --list

# Run specific steps only
act push -b staging \
  --job deploy-staging \
  --workflows .github/workflows/deploy.yml \
  --step "Setup Node.js" \
  --step "Install frontend dependencies" \
  --step "Build frontend"
```

## Limitations

⚠️ **Important Notes:**

1. **SSH Deployment Steps**: The SSH deployment steps will **NOT** actually connect to Toolforge when testing locally. They will fail or be skipped. This is expected.

2. **Secrets**: Use test/dummy values in `.secrets` file. Never commit real secrets.

3. **Environment Differences**: Local testing may behave slightly differently than GitHub Actions:
   - Different container images
   - Different environment variables
   - Network access limitations

4. **Dry Run Mode**: Always use `--dryrun` first to see what would happen without actually executing.

## Testing Checklist

Before pushing to GitHub:

- [ ] YAML syntax is valid
- [ ] Frontend build steps work locally
- [ ] Node.js setup completes successfully
- [ ] npm install runs without errors
- [ ] npm run build creates `frontend/dist/` directory
- [ ] Workflow triggers match expected branches (main/staging)
- [ ] Secrets are properly referenced (use dummy values for testing)

## Troubleshooting

### act Not Found

```bash
# Check if act is installed
which act

# Install if missing (macOS)
brew install act

# Install if missing (Linux)
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

### Docker Not Running

```bash
# Check Docker status
docker ps

# Start Docker Desktop (macOS/Windows)
# Or start Docker service (Linux)
sudo systemctl start docker
```

### Permission Denied

```bash
# Make script executable
chmod +x .github/act-test.sh
```

### Frontend Build Fails

Check:
- Node.js version matches (v20)
- `package-lock.json` exists
- Dependencies are installable
- Build script works manually: `cd frontend && npm run build`

## Alternative: Manual Step Testing

You can also test individual steps manually:

```bash
# Test frontend build manually
cd frontend
npm ci
npm run build

# Verify dist/ was created
ls -la dist/
```

## Resources

- [act GitHub Repository](https://github.com/nektos/act)
- [act Documentation](https://github.com/nektos/act#example-commands)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)

