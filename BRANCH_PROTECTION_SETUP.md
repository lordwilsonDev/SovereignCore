# Branch Protection Rules Setup Guide

This document provides instructions for setting up branch protection rules for the SovereignCore repository.

## Why Branch Protection?

Branch protection rules ensure:
- Code quality through required reviews
- Automated testing before merging
- Prevention of accidental force pushes
- Consistent deployment process

## Recommended Branch Protection Rules

### For `main` branch (Production)

1. **Navigate to Repository Settings**
   - Go to your GitHub repository
   - Click on "Settings" → "Branches"
   - Click "Add branch protection rule"

2. **Branch name pattern**: `main`

3. **Enable the following rules**:

   ✅ **Require a pull request before merging**
   - Require approvals: 1 (or 2 for critical projects)
   - Dismiss stale pull request approvals when new commits are pushed
   - Require review from Code Owners (if CODEOWNERS file exists)

   ✅ **Require status checks to pass before merging**
   - Require branches to be up to date before merging
   - Status checks that are required:
     - `Code Quality`
     - `Tests (3.11)` (or all Python versions)
     - `CodeQL Security Analysis`
     - `Docker Build & Scan`

   ✅ **Require conversation resolution before merging**
   - All review comments must be resolved

   ✅ **Require signed commits**
   - Ensures commit authenticity

   ✅ **Require linear history**
   - Prevents merge commits, enforces rebase or squash

   ✅ **Do not allow bypassing the above settings**
   - Applies to administrators too

   ✅ **Restrict who can push to matching branches**
   - Only allow specific users/teams (optional)

   ✅ **Allow force pushes**: ❌ Disabled
   
   ✅ **Allow deletions**: ❌ Disabled

### For `develop` branch (Staging)

1. **Branch name pattern**: `develop`

2. **Enable the following rules**:

   ✅ **Require a pull request before merging**
   - Require approvals: 1

   ✅ **Require status checks to pass before merging**
   - Status checks that are required:
     - `Code Quality`
     - `Tests (3.11)`
     - `Docker Build & Scan`

   ✅ **Require conversation resolution before merging**

   ✅ **Allow force pushes**: ❌ Disabled
   
   ✅ **Allow deletions**: ❌ Disabled

### For `feature/*` branches

1. **Branch name pattern**: `feature/*`

2. **Enable the following rules**:

   ✅ **Require status checks to pass before merging**
   - Status checks that are required:
     - `Code Quality`
     - `Tests (3.11)`

## GitHub CLI Setup (Alternative)

You can also set up branch protection using GitHub CLI:

```bash
# Install GitHub CLI if not already installed
brew install gh

# Authenticate
gh auth login

# Enable branch protection for main
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]=Code Quality \
  --field required_status_checks[contexts][]=Tests \
  --field required_pull_request_reviews[required_approving_review_count]=1 \
  --field required_pull_request_reviews[dismiss_stale_reviews]=true \
  --field enforce_admins=true \
  --field required_linear_history=true \
  --field allow_force_pushes=false \
  --field allow_deletions=false
```

## CODEOWNERS File

Create a `.github/CODEOWNERS` file to automatically request reviews from specific people:

```
# Default owners for everything in the repo
*       @your-username

# API and security-critical files
/api_server.py              @your-username @security-team
/requirements.txt           @your-username
/.github/workflows/         @your-username @devops-team

# Docker and deployment
/Dockerfile                 @your-username @devops-team
/docker-compose.yml         @your-username @devops-team

# Security configurations
/redis.conf                 @your-username @security-team
/users.acl                  @your-username @security-team
```

## Deployment Protection Rules

### For Production Environment

1. **Navigate to Repository Settings**
   - Go to "Settings" → "Environments" → "production"

2. **Enable the following**:

   ✅ **Required reviewers**
   - Add specific users who must approve production deployments
   - Minimum: 1-2 reviewers

   ✅ **Wait timer**
   - Optional: Add a wait time (e.g., 5 minutes) before deployment

   ✅ **Deployment branches**
   - Only allow deployments from `main` branch

   ✅ **Environment secrets**
   - Add production-specific secrets:
     - `SECRET_KEY`
     - `REDIS_PASSWORD`
     - `GRAFANA_PASSWORD`
     - etc.

### For Staging Environment

1. **Navigate to Repository Settings**
   - Go to "Settings" → "Environments" → "staging"

2. **Enable the following**:

   ✅ **Deployment branches**
   - Allow deployments from `main` and `develop` branches

   ✅ **Environment secrets**
   - Add staging-specific secrets

## Verification

After setting up branch protection:

1. Try to push directly to `main` - should be blocked
2. Create a PR without passing tests - should not be mergeable
3. Create a PR with passing tests - should be mergeable after approval
4. Try to force push - should be blocked

## Additional Security Measures

### Enable Dependabot

1. Go to "Settings" → "Security & analysis"
2. Enable:
   - Dependency graph
   - Dependabot alerts
   - Dependabot security updates

### Enable Secret Scanning

1. Go to "Settings" → "Security & analysis"
2. Enable:
   - Secret scanning
   - Push protection (prevents committing secrets)

### Enable Code Scanning

1. Go to "Security" → "Code scanning"
2. Set up CodeQL analysis (already configured in CI/CD)

## References

- [GitHub Branch Protection Documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [GitHub Environments Documentation](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [CODEOWNERS Documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
