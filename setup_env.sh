#!/bin/bash
# Setup environment file for SovereignCore
# This script creates a .env file from .env.example with generated secrets

set -e

echo "========================================"
echo "SovereignCore Environment Setup"
echo "========================================"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Existing .env file preserved."
        exit 0
    fi
    echo ""
fi

# Check if .env.example exists
if [ ! -f ".env.example" ]; then
    echo "❌ Error: .env.example not found!"
    exit 1
fi

echo "Creating .env file from .env.example..."
cp .env.example .env

# Generate random secrets
echo "Generating secure secrets..."

# Generate SECRET_KEY (64 character random string)
SECRET_KEY=$(openssl rand -base64 48 | tr -d "\n")

# Generate REDIS_PASSWORD (32 character random string)
REDIS_PASSWORD=$(openssl rand -base64 24 | tr -d "\n")

# Generate JWT secret (64 character random string)
JWT_SECRET=$(openssl rand -base64 48 | tr -d "\n")

# Update .env file with generated secrets
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" .env
    sed -i '' "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=${REDIS_PASSWORD}|" .env
    sed -i '' "s|JWT_SECRET=.*|JWT_SECRET=${JWT_SECRET}|" .env
else
    # Linux
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=${SECRET_KEY}|" .env
    sed -i "s|REDIS_PASSWORD=.*|REDIS_PASSWORD=${REDIS_PASSWORD}|" .env
    sed -i "s|JWT_SECRET=.*|JWT_SECRET=${JWT_SECRET}|" .env
fi

echo ""
echo "✅ .env file created successfully!"
echo ""
echo "Generated secrets:"
echo "  - SECRET_KEY: ${SECRET_KEY:0:20}..."
echo "  - REDIS_PASSWORD: ${REDIS_PASSWORD:0:20}..."
echo "  - JWT_SECRET: ${JWT_SECRET:0:20}..."
echo ""
echo "⚠️  IMPORTANT:"
echo "  1. Review .env file and update any additional settings"
echo "  2. Never commit .env to version control"
echo "  3. Keep these secrets secure"
echo "  4. Update Redis configuration with the new password"
echo ""
echo "Next steps:"
echo "  1. Update redis.conf with REDIS_PASSWORD"
echo "  2. Update users.acl with REDIS_PASSWORD"
echo "  3. Run: ./scripts/setup_redis.sh"
echo ""
echo "========================================"
