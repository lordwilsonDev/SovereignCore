# Environment Setup Guide

## Quick Start

The easiest way to set up your environment is to use the automated setup script:

```bash
chmod +x setup_env.sh
./setup_env.sh
```

This script will:
1. Create `.env` from `.env.example`
2. Generate secure random secrets for:
   - `SECRET_KEY` (API secret key)
   - `REDIS_PASSWORD` (Redis authentication)
   - `JWT_SECRET` (JWT token signing)
3. Update the `.env` file with these secrets

## Manual Setup

If you prefer to set up manually:

### 1. Copy the Example File

```bash
cp .env.example .env
```

### 2. Generate Secrets

Generate secure random secrets using OpenSSL:

```bash
# Generate SECRET_KEY (64 characters)
openssl rand -base64 48

# Generate REDIS_PASSWORD (32 characters)
openssl rand -base64 24

# Generate JWT_SECRET (64 characters)
openssl rand -base64 48
```

### 3. Update .env File

Edit `.env` and replace the placeholder values:

```bash
# Security - CHANGE THESE IN PRODUCTION!
SECRET_KEY=<your-generated-secret-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=<your-generated-redis-password>
```

## Environment Variables Reference

### API Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | Host to bind the API server |
| `API_PORT` | `8528` | Port for the API server |
| `API_WORKERS` | `4` | Number of Gunicorn workers |

### Security

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | **Yes** | Secret key for signing tokens (min 32 chars) |
| `ALGORITHM` | No | JWT algorithm (default: HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Access token lifetime (default: 30) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | Refresh token lifetime (default: 7) |

### CORS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ORIGINS` | `["http://localhost:3000","http://localhost:8528"]` | Allowed origins |
| `CORS_ALLOW_CREDENTIALS` | `true` | Allow credentials |
| `CORS_ALLOW_METHODS` | `["GET","POST","PUT","DELETE"]` | Allowed methods |
| `CORS_ALLOW_HEADERS` | `["*"]` | Allowed headers |

### Rate Limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `RATE_LIMIT_DEFAULT` | `100/minute` | Default rate limit |
| `RATE_LIMIT_AUTH` | `5/minute` | Auth endpoint rate limit |

### Redis

| Variable | Required | Description |
|----------|----------|-------------|
| `REDIS_URL` | No | Redis connection URL |
| `REDIS_PASSWORD` | **Yes** | Redis authentication password |

### TLS/HTTPS

| Variable | Default | Description |
|----------|---------|-------------|
| `TLS_ENABLED` | `false` | Enable TLS/HTTPS |
| `TLS_CERT_PATH` | - | Path to TLS certificate |
| `TLS_KEY_PATH` | - | Path to TLS private key |

### Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | Environment name (development/staging/production) |
| `DEBUG` | `true` | Enable debug mode |

## Production Configuration

For production deployments, ensure you:

### 1. Generate Strong Secrets

```bash
# Use at least 64 characters for SECRET_KEY
openssl rand -base64 64

# Use at least 32 characters for REDIS_PASSWORD
openssl rand -base64 32
```

### 2. Update Security Settings

```bash
ENVIRONMENT=production
DEBUG=false
TLS_ENABLED=true
TLS_CERT_PATH=/etc/ssl/certs/sovereigncore.crt
TLS_KEY_PATH=/etc/ssl/private/sovereigncore.key
```

### 3. Configure CORS Properly

```bash
# Replace with your actual frontend URLs
CORS_ORIGINS=["https://app.yourdomain.com","https://api.yourdomain.com"]
```

### 4. Adjust Rate Limits

```bash
# Stricter limits for production
RATE_LIMIT_DEFAULT=50/minute
RATE_LIMIT_AUTH=3/minute
```

### 5. Update Redis Configuration

After setting `REDIS_PASSWORD`, update Redis configuration:

```bash
# Update redis.conf
sed -i "s/requirepass .*/requirepass YOUR_REDIS_PASSWORD/" redis.conf

# Update users.acl
sed -i "s/>.*/>YOUR_REDIS_PASSWORD/" users.acl

# Restart Redis
./scripts/setup_redis.sh
```

## Security Best Practices

### 1. Never Commit .env to Version Control

The `.env` file is already in `.gitignore`, but double-check:

```bash
grep -q "^\.env$" .gitignore || echo ".env" >> .gitignore
```

### 2. Rotate Secrets Regularly

In production, rotate secrets every 90 days:

```bash
# Generate new secrets
./setup_env.sh

# Update Redis
./scripts/setup_redis.sh

# Restart services
docker compose restart
```

### 3. Use Environment-Specific Files

For multiple environments:

```bash
.env.development
.env.staging
.env.production
```

Load the appropriate file:

```bash
cp .env.production .env
```

### 4. Restrict File Permissions

```bash
chmod 600 .env
```

### 5. Use Secrets Management in Production

For production, consider using:
- **AWS Secrets Manager**
- **HashiCorp Vault**
- **Azure Key Vault**
- **Google Secret Manager**

## Verification

After setup, verify your configuration:

```bash
# Check .env exists and has correct permissions
ls -la .env

# Verify secrets are set (without revealing them)
grep -q "SECRET_KEY=your-secret-key" .env && echo "⚠️  SECRET_KEY not changed!" || echo "✓ SECRET_KEY set"
grep -q "REDIS_PASSWORD=your-redis-password" .env && echo "⚠️  REDIS_PASSWORD not changed!" || echo "✓ REDIS_PASSWORD set"

# Test Redis connection
redis-cli -a $(grep REDIS_PASSWORD .env | cut -d'=' -f2) ping
```

## Troubleshooting

### Issue: "SECRET_KEY not set" error

**Solution:** Ensure `.env` file exists and `SECRET_KEY` is set:

```bash
grep SECRET_KEY .env
```

### Issue: Redis authentication failed

**Solution:** Ensure Redis password matches in `.env` and `redis.conf`:

```bash
# Check .env
grep REDIS_PASSWORD .env

# Check redis.conf
grep requirepass redis.conf

# Update if needed
./scripts/setup_redis.sh
```

### Issue: CORS errors in browser

**Solution:** Update `CORS_ORIGINS` with your frontend URL:

```bash
CORS_ORIGINS=["https://your-frontend-url.com"]
```

## Next Steps

After setting up your environment:

1. **Initialize Database:**
   ```bash
   python init_db.py
   ```

2. **Generate TLS Certificates (if needed):**
   ```bash
   ./scripts/generate_certs.sh
   ```

3. **Start Services:**
   ```bash
   docker compose up -d
   ```

4. **Verify Deployment:**
   ```bash
   curl http://localhost:8528/health
   ```

## Additional Resources

- [Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Security Best Practices](PRODUCTION_READINESS_CHECKLIST.md)
- [Docker Setup](docker-compose.yml)
- [Testing Guide](TESTING_GUIDE.md)
