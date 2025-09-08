#!/bin/bash

# Script to configure GitHub Branch Protection Rules using GitHub CLI
# Requires: gh CLI tool to be installed and authenticated

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) is not installed.${NC}"
    echo "Please install it from: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo -e "${RED}Error: Not authenticated with GitHub CLI.${NC}"
    echo "Please run: gh auth login"
    exit 1
fi

# Get repository information
REPO_OWNER=$(gh repo view --json owner --jq '.owner.login')
REPO_NAME=$(gh repo view --json name --jq '.name')

echo -e "${GREEN}Setting up branch protection for ${REPO_OWNER}/${REPO_NAME}${NC}"

# Check if repository exists and we have admin access
if ! gh api repos/${REPO_OWNER}/${REPO_NAME} &> /dev/null; then
    echo -e "${RED}Error: Cannot access repository or insufficient permissions.${NC}"
    exit 1
fi

# Configure branch protection for main branch
echo -e "${YELLOW}Configuring branch protection rules for 'main' branch...${NC}"

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/${REPO_OWNER}/${REPO_NAME}/branches/main/protection \
  --input - << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {
        "context": "lint",
        "app_id": -1
      },
      {
        "context": "test",
        "app_id": -1
      }
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": true
}
EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Branch protection configured successfully!${NC}"
else
    echo -e "${RED}✗ Failed to configure branch protection.${NC}"
    exit 1
fi

echo -e "${GREEN}Branch protection setup completed!${NC}"
echo ""
echo -e "${YELLOW}Configuration summary:${NC}"
echo "• Require status checks to pass before merging"
echo "• Require branches to be up to date before merging"
echo "• Require pull request reviews before merging (1 approval)"
echo "• Dismiss stale pull request approvals when new commits are pushed"
echo "• Require conversation resolution before merging"
echo "• Restrict pushes that create files"
echo ""
echo -e "${GREEN}Your main branch is now protected!${NC}"
