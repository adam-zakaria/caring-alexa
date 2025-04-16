#!/bin/bash

echo "============ DEPLOYMENT DEBUG SCRIPT ============"

# Check AWS credentials
echo "Checking AWS credentials..."
if aws sts get-caller-identity &>/dev/null; then
    echo "✓ AWS credentials are working"
else
    echo "✗ AWS credentials issue - make sure your credentials are correctly configured"
    echo "  Run 'aws configure' to set up credentials"
    exit 1
fi

# Check if ask-cli is installed
echo "Checking ASK CLI installation..."
if command -v ask &>/dev/null; then
    ask_version=$(ask --version)
    echo "✓ ASK CLI is installed: $ask_version"
else
    echo "✗ ASK CLI is not installed"
    echo "  Install with: npm install -g ask-cli"
    exit 1
fi

# Check ASK profile
echo "Checking ASK CLI profile..."
if ask profile ls &>/dev/null; then
    echo "✓ ASK profile exists"
else
    echo "✗ ASK profile issue"
    echo "  Run 'ask configure' to set up profile"
    exit 1
fi

# Check network connectivity to AWS
echo "Checking network connectivity to AWS Lambda..."
if curl -s https://lambda.us-east-1.amazonaws.com &>/dev/null; then
    echo "✓ Network connectivity to AWS Lambda is working"
else
    echo "✗ Network connectivity issue to AWS Lambda"
    echo "  Check security groups and network configuration"
    exit 1
fi

# Check if the API endpoint is reachable
api_host=$(grep -oP 'apiHost = "\K[^"]+' config.py | head -1)
echo "Checking API host connectivity to $api_host..."
if curl -s --max-time 10 "$api_host/health" &>/dev/null; then
    echo "✓ API host is reachable"
else
    echo "⚠ API host might not be reachable"
    echo "  This could cause runtime issues but shouldn't affect deployment"
fi

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version)
echo "Using $python_version"

# Verify required packages
echo "Checking required Python packages..."
echo "Installing packages to temporary directory for verification..."
temp_dir=$(mktemp -d)
pip install -r requirements.txt -t "$temp_dir" > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ Python packages installation successful"
else
    echo "✗ Failed to install Python packages"
    echo "  Check requirements.txt and network connectivity"
    rm -rf "$temp_dir"
    exit 1
fi
rm -rf "$temp_dir"

echo ""
echo "All pre-deployment checks passed. Try deploying with:"
echo "cd .. && ask deploy"
echo "==============================================" 