#!/bin/bash
# Script to test GitHub Actions workflow locally using act
# Install act first: https://github.com/nektos/act

set -e

echo "🧪 Testing GitHub Actions Workflow Locally"
echo "==========================================="
echo ""

# Check if act is installed
if ! command -v act &> /dev/null; then
    echo "❌ 'act' is not installed."
    echo ""
    echo "Install it using one of these methods:"
    echo "  macOS:   brew install act"
    echo "  Linux:   curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash"
    echo "  Windows: Use WSL or Docker Desktop"
    echo ""
    echo "More info: https://github.com/nektos/act"
    exit 1
fi

echo "✅ act is installed"
echo ""

# Create a .secrets file for testing (if it doesn't exist)
if [ ! -f .secrets ]; then
    echo "📝 Creating .secrets file template..."
    cat > .secrets << EOF
# GitHub Actions Secrets for Local Testing
# These are used by 'act' to simulate GitHub Secrets
# DO NOT commit this file with real secrets!

SSH_PRIVATE_KEY=your-ssh-private-key-here
SSH_USER=your-ssh-username
SSH_HOST=login.toolforge.org
TARGET_DIR=www/python/src/
GITHUB_REPO=https://github.com/indictechcom/wikicontest.git
EOF
    echo "⚠️  Created .secrets file. Please fill in your test values."
    echo "⚠️  Note: .secrets is in .gitignore and won't be committed."
    echo ""
fi

# Test options
echo "Select test option:"
echo "1) Test frontend build steps only (safe, no deployment)"
echo "2) Test staging workflow (requires secrets)"
echo "3) Test production workflow (requires secrets)"
echo "4) Validate YAML syntax only"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo ""
        echo "🧪 Testing frontend build steps..."
        act push -b staging \
            --job deploy-staging \
            --dryrun \
            --workflows .github/workflows/deploy.yml \
            --container-architecture linux/amd64 \
            -s SSH_PRIVATE_KEY="test-key" \
            -s SSH_USER="test-user" \
            -s SSH_HOST="test-host" \
            -s TARGET_DIR="test-dir" \
            -s GITHUB_REPO="test-repo" \
            --env BRANCH_NAME=staging \
            --step "Setup Node.js" \
            --step "Install frontend dependencies" \
            --step "Build frontend"
        ;;
    2)
        echo ""
        echo "🧪 Testing staging workflow..."
        if [ ! -f .secrets ]; then
            echo "❌ .secrets file not found. Please create it first."
            exit 1
        fi
        act push -b staging \
            --job deploy-staging \
            --workflows .github/workflows/deploy.yml \
            --container-architecture linux/amd64 \
            --secret-file .secrets \
            --env BRANCH_NAME=staging \
            --dryrun
        ;;
    3)
        echo ""
        echo "🧪 Testing production workflow..."
        if [ ! -f .secrets ]; then
            echo "❌ .secrets file not found. Please create it first."
            exit 1
        fi
        act push -b main \
            --job deploy-production \
            --workflows .github/workflows/deploy.yml \
            --container-architecture linux/amd64 \
            --secret-file .secrets \
            --dryrun
        ;;
    4)
        echo ""
        echo "🧪 Validating YAML syntax..."
        if command -v yamllint &> /dev/null; then
            yamllint .github/workflows/deploy.yml
        else
            echo "⚠️  yamllint not installed. Using act --dryrun for validation..."
            act push -b staging --dryrun --workflows .github/workflows/deploy.yml
        fi
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Test completed!"

