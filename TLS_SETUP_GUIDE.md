# TLS/HTTPS Setup Guide for SovereignCore

## Overview

This guide covers enabling TLS/HTTPS for SovereignCore in both development and production environments.

## Quick Start (Development)

For local development with self-signed certificates:

```bash
# Generate self-signed certificates
chmod +x scripts/generate_certs.sh
./scripts/generate_certs.sh

# Update .env
TLS_ENABLED=true
TLS_CERT_PATH=./certs/cert.pem
TLS_KEY_PATH=./certs/key.pem

# Restart services
docker compose restart
```

## Production Setup

### Option 1: Let's Encrypt (Recommended)

Let's Encrypt provides free, automated SSL/TLS certificates.

#### Prerequisites

- Domain name pointing to your server
- Port 80 and 443 accessible
- Certbot installed

#### Installation

```bash
# Install Certbot (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Install Certbot (macOS)
brew install certbot

# Install Certbot (CentOS/RHEL)
sudo yum install certbot python3-certbot-nginx
```

#### Generate Certificates

```bash
# Standalone mode (if no web server running)
sudo certbot certonly --standalone -d api.yourdomain.com

# Nginx mode (if Nginx is running)
sudo certbot --nginx -d api.yourdomain.com

# Manual DNS challenge (for wildcard certs)
sudo certbot certonly --manual --preferred-challenges dns -d "*.yourdomain.com"
```

#### Configure SovereignCore

```bash
# Update .env
TLS_ENABLED=true
TLS_CERT_PATH=/etc/letsencrypt/live/api.yourdomain.com/fullchain.pem
TLS_KEY_PATH=/etc/letsencrypt/live/api.yourdomain.com/privkey.pem
```

#### Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Set up auto-renewal (cron)
sudo crontab -e

# Add this line (runs twice daily)
0 0,12 * * * certbot renew --quiet --post-hook "docker compose -f /path/to/sovereigncore/docker-compose.yml restart"
```

### Option 2: Commercial Certificate

If you have a commercial SSL certificate:

#### 1. Obtain Certificate Files

You should have:
- `certificate.crt` - Your SSL certificate
- `private.key` - Your private key
- `ca_bundle.crt` - Certificate Authority bundle (optional)

#### 2. Combine Certificate and CA Bundle

```bash
# Create fullchain certificate
cat certificate.crt ca_bundle.crt > fullchain.pem

# Copy private key
cp private.key privkey.pem
```

#### 3. Secure the Files

```bash
# Create certs directory
sudo mkdir -p /etc/ssl/sovereigncore

# Copy certificates
sudo cp fullchain.pem /etc/ssl/sovereigncore/
sudo cp privkey.pem /etc/ssl/sovereigncore/

# Set permissions
sudo chmod 644 /etc/ssl/sovereigncore/fullchain.pem
sudo chmod 600 /etc/ssl/sovereigncore/privkey.pem
sudo chown root:root /etc/ssl/sovereigncore/*
```

#### 4. Configure SovereignCore

```bash
# Update .env
TLS_ENABLED=true
TLS_CERT_PATH=/etc/ssl/sovereigncore/fullchain.pem
TLS_KEY_PATH=/etc/ssl/sovereigncore/privkey.pem
```

### Option 3: Self-Signed Certificate (Development Only)

**⚠️ WARNING: Self-signed certificates should NEVER be used in production!**

#### Using the Provided Script

```bash
./scripts/generate_certs.sh
```

This creates:
- `certs/cert.pem` - Self-signed certificate
- `certs/key.pem` - Private key
- Valid for 365 days

#### Manual Generation

```bash
# Create certs directory
mkdir -p certs

# Generate private key and certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Set permissions
chmod 644 certs/cert.pem
chmod 600 certs/key.pem
```

## Docker Configuration

### Update docker-compose.yml

Add volume mounts for certificates:

```yaml
services:
  api:
    volumes:
      - ./certs:/app/certs:ro
      # OR for Let's Encrypt
      - /etc/letsencrypt:/etc/letsencrypt:ro
    environment:
      - TLS_ENABLED=true
      - TLS_CERT_PATH=/app/certs/cert.pem
      - TLS_KEY_PATH=/app/certs/key.pem
    ports:
      - "443:8528"  # HTTPS
      - "80:8528"   # HTTP (optional, for redirect)
```

### Nginx Reverse Proxy (Recommended)

For production, use Nginx as a reverse proxy:

```nginx
# /etc/nginx/sites-available/sovereigncore

server {
    listen 80;
    server_name api.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Proxy to SovereignCore
    location / {
        proxy_pass http://localhost:8528;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/sovereigncore /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Redis TLS Configuration

To enable TLS for Redis connections:

### 1. Generate Redis Certificates

```bash
# Generate CA
openssl genrsa -out redis-ca-key.pem 4096
openssl req -x509 -new -nodes -key redis-ca-key.pem \
  -days 3650 -out redis-ca-cert.pem \
  -subj "/CN=Redis-CA"

# Generate Redis server certificate
openssl genrsa -out redis-server-key.pem 4096
openssl req -new -key redis-server-key.pem \
  -out redis-server.csr \
  -subj "/CN=redis-server"
openssl x509 -req -in redis-server.csr \
  -CA redis-ca-cert.pem -CAkey redis-ca-key.pem \
  -CAcreateserial -out redis-server-cert.pem -days 3650

# Generate client certificate
openssl genrsa -out redis-client-key.pem 4096
openssl req -new -key redis-client-key.pem \
  -out redis-client.csr \
  -subj "/CN=redis-client"
openssl x509 -req -in redis-client.csr \
  -CA redis-ca-cert.pem -CAkey redis-ca-key.pem \
  -CAcreateserial -out redis-client-cert.pem -days 3650
```

### 2. Update redis.conf

```conf
# Enable TLS
port 0
tls-port 6379

# Certificate paths
tls-cert-file /path/to/redis-server-cert.pem
tls-key-file /path/to/redis-server-key.pem
tls-ca-cert-file /path/to/redis-ca-cert.pem

# Client authentication
tls-auth-clients yes

# TLS protocols
tls-protocols "TLSv1.2 TLSv1.3"
```

### 3. Update .env

```bash
REDIS_URL=rediss://localhost:6379/0  # Note: rediss:// for TLS
REDIS_TLS_CERT=/path/to/redis-client-cert.pem
REDIS_TLS_KEY=/path/to/redis-client-key.pem
REDIS_TLS_CA=/path/to/redis-ca-cert.pem
```

## Verification

### Test HTTPS Connection

```bash
# Test with curl
curl -v https://localhost:8528/health

# Test with specific certificate (self-signed)
curl -v --cacert certs/cert.pem https://localhost:8528/health

# Test SSL/TLS configuration
openssl s_client -connect localhost:8528 -tls1_3
```

### Check Certificate Details

```bash
# View certificate information
openssl x509 -in certs/cert.pem -text -noout

# Check certificate expiration
openssl x509 -in certs/cert.pem -noout -dates

# Verify certificate chain
openssl verify -CAfile /etc/ssl/certs/ca-certificates.crt certs/cert.pem
```

### SSL Labs Test (Production)

For production deployments, test your SSL configuration:

```
https://www.ssllabs.com/ssltest/analyze.html?d=api.yourdomain.com
```

Aim for an **A+** rating.

## Security Best Practices

### 1. Use Strong Protocols

```bash
# Only allow TLS 1.2 and 1.3
ssl_protocols TLSv1.2 TLSv1.3;
```

### 2. Use Strong Ciphers

```bash
# Modern cipher suite
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
```

### 3. Enable HSTS

```bash
# Force HTTPS for 1 year
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

### 4. Disable SSL Compression

```bash
ssl_compression off;
```

### 5. Enable OCSP Stapling

```bash
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/api.yourdomain.com/chain.pem;
```

### 6. Secure Private Keys

```bash
# Restrict permissions
chmod 600 /path/to/privkey.pem
chown root:root /path/to/privkey.pem
```

### 7. Regular Certificate Rotation

```bash
# Set up monitoring for certificate expiration
# Renew certificates 30 days before expiration
```

## Troubleshooting

### Issue: "SSL certificate problem: self signed certificate"

**For Development:**
```bash
# Use -k flag to ignore certificate validation
curl -k https://localhost:8528/health

# Or add certificate to trusted store
sudo cp certs/cert.pem /usr/local/share/ca-certificates/sovereigncore.crt
sudo update-ca-certificates
```

### Issue: "Certificate has expired"

**Solution:** Renew the certificate

```bash
# Let's Encrypt
sudo certbot renew

# Self-signed (regenerate)
./scripts/generate_certs.sh
```

### Issue: "Wrong host name in certificate"

**Solution:** Ensure certificate CN matches your domain

```bash
# Check certificate CN
openssl x509 -in cert.pem -noout -subject

# Regenerate with correct CN
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem -out cert.pem -days 365 \
  -subj "/CN=api.yourdomain.com"
```

### Issue: "Permission denied" reading certificate

**Solution:** Fix file permissions

```bash
# Make certificate readable
chmod 644 cert.pem

# Make key readable only by owner
chmod 600 key.pem

# Ensure correct ownership
sudo chown $USER:$USER cert.pem key.pem
```

### Issue: Mixed content warnings

**Solution:** Ensure all resources use HTTPS

```bash
# Update CORS origins to use https://
CORS_ORIGINS=["https://app.yourdomain.com"]

# Update all API calls in frontend to use https://
```

## Certificate Monitoring

### Set Up Expiration Alerts

```bash
#!/bin/bash
# check_cert_expiry.sh

CERT_FILE="/etc/letsencrypt/live/api.yourdomain.com/cert.pem"
DAYS_WARNING=30

EXPIRY_DATE=$(openssl x509 -in "$CERT_FILE" -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
CURRENT_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt $DAYS_WARNING ]; then
    echo "WARNING: Certificate expires in $DAYS_LEFT days!"
    # Send alert (email, Slack, etc.)
fi
```

Add to cron:

```bash
# Run daily at 9 AM
0 9 * * * /path/to/check_cert_expiry.sh
```

## Additional Resources

- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Mozilla SSL Configuration Generator](https://ssl-config.mozilla.org/)
- [SSL Labs Best Practices](https://github.com/ssllabs/research/wiki/SSL-and-TLS-Deployment-Best-Practices)
- [OWASP TLS Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Protection_Cheat_Sheet.html)

## Next Steps

After enabling TLS:

1. **Update DNS:** Point your domain to the server
2. **Configure Firewall:** Open ports 80 and 443
3. **Test Thoroughly:** Verify all endpoints work over HTTPS
4. **Monitor Certificates:** Set up expiration alerts
5. **Update Documentation:** Document your TLS setup for your team
