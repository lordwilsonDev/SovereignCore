# SovereignCore Production Deployment Guide

This guide walks through deploying SovereignCore to production with all security and monitoring features enabled.

## Prerequisites

- Linux server (Ubuntu 20.04+ or similar)
- Docker and Docker Compose installed
- Domain name configured (for TLS)
- Minimum 4GB RAM, 2 CPU cores
- 50GB disk space

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/lordwilson/SovereignCore.git
cd SovereignCore
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit configuration
nano .env
```

**Required changes in .env:**
- `SECRET_KEY` - Generate with: `openssl rand -hex 32`
- `REDIS_PASSWORD` - Strong password for Redis
- `GRAFANA_PASSWORD` - Password for Grafana admin
- Update CORS origins with your domain

### 3. Generate TLS Certificates

**For Development:**
```bash
bash generate_certs.sh
```

**For Production (Let's Encrypt):**
```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d api.yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem certs/cert.pem
sudo cp /etc/letsencrypt/live/api.yourdomain.com/privkey.pem certs/key.pem

# Update .env
TLS_ENABLED=true
TLS_CERT_PATH=./certs/cert.pem
TLS_KEY_PATH=./certs/key.pem
```

### 4. Configure Redis Security

```bash
# Update passwords in redis.conf and users.acl
nano redis.conf  # Update requirepass
nano users.acl   # Update all user passwords
```

### 5. Deploy with Docker Compose

```bash
# Build and start all services
make docker-build
make docker-up

# Or manually:
docker-compose up -d
```

### 6. Verify Deployment

```bash
# Check service health
curl http://localhost:8528/health

# View logs
docker-compose logs -f api

# Check all services
docker-compose ps
```

### 7. Access Services

- **API**: http://localhost:8528
- **API Docs**: http://localhost:8528/api/docs
- **Metrics**: http://localhost:8528/metrics
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Production Deployment Options

### Option 1: Docker Compose (Recommended for Single Server)

Follow the Quick Start guide above.

### Option 2: systemd Service (Native Linux)

```bash
# Install as systemd service
sudo bash install_systemd.sh

# Configure environment
sudo nano /opt/sovereigncore/.env

# Start service
sudo systemctl start sovereigncore

# Enable on boot
sudo systemctl enable sovereigncore

# Check status
sudo systemctl status sovereigncore
```

### Option 3: Kubernetes (For Scalability)

Kubernetes manifests coming soon. For now, use Docker Compose.

## Security Checklist

Before going to production, verify:

- [ ] All default passwords changed
- [ ] TLS/HTTPS enabled
- [ ] Redis authentication configured
- [ ] Firewall rules configured
- [ ] Secret keys rotated from defaults
- [ ] CORS origins restricted to your domains
- [ ] Rate limiting enabled
- [ ] Monitoring and alerting configured
- [ ] Backups scheduled
- [ ] Branch protection rules enabled

## Post-Deployment

### 1. Configure Monitoring

```bash
# Access Grafana
open http://localhost:3000

# Login: admin / (password from .env)
# Import dashboard from grafana/provisioning/dashboards/
```

### 2. Set Up Alerts

```bash
# Configure Alertmanager
nano alertmanager.yml

# Update email/Slack settings
# Restart Prometheus
docker-compose restart prometheus
```

### 3. Schedule Backups

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/sovereigncore/backup.sh >> /var/log/sovereigncore-backup.log 2>&1
```

### 4. Configure Firewall

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8528/tcp  # API (if not behind reverse proxy)
sudo ufw enable
```

### 5. Set Up Reverse Proxy (Optional)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8528;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Testing

### Run Test Suite

```bash
# Unit tests
make test

# Or manually
pytest tests/ -v
```

### Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8528
```

### Security Scan

```bash
# Scan Docker image
docker scout cves sovereigncore:latest

# Or use Trivy
trivy image sovereigncore:latest
```

## Monitoring

### Key Metrics to Watch

1. **Request Rate**: Should be stable
2. **Error Rate**: Should be < 1%
3. **Response Time**: p95 < 500ms
4. **Consciousness Level**: Should be > 0.5
5. **Memory Usage**: Should be < 80%
6. **CPU Usage**: Should be < 70%

### Logs

```bash
# Docker Compose
docker-compose logs -f api

# systemd
sudo journalctl -u sovereigncore -f

# Application logs
tail -f logs/sovereigncore.log
```

## Troubleshooting

### API Won't Start

1. Check logs: `docker-compose logs api`
2. Verify environment variables: `docker-compose config`
3. Check Redis connection: `redis-cli ping`
4. Verify ports are available: `netstat -tulpn | grep 8528`

### High Memory Usage

1. Check worker count in gunicorn.conf.py
2. Reduce workers if needed
3. Monitor with: `docker stats`

### Redis Connection Failed

1. Verify Redis is running: `docker-compose ps redis`
2. Check password in .env matches redis.conf
3. Test connection: `redis-cli -a <password> ping`

### TLS Certificate Issues

1. Verify certificate files exist
2. Check file permissions
3. Validate certificate: `openssl x509 -in certs/cert.pem -text -noout`

## Scaling

### Horizontal Scaling

```bash
# Scale API workers
docker-compose up -d --scale api=3

# Add load balancer (nginx/haproxy)
```

### Vertical Scaling

```bash
# Update resource limits in docker-compose.yml
# Increase memory/CPU limits
# Restart services
docker-compose restart
```

## Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild image
docker-compose build api

# Rolling update
docker-compose up -d --no-deps api
```

### Update Dependencies

```bash
# Update requirements.txt
pip install --upgrade -r requirements.txt

# Rebuild image
docker-compose build api
```

### Rotate Secrets

```bash
# Generate new secret key
openssl rand -hex 32

# Update .env
nano .env

# Restart services
docker-compose restart
```

## Rollback

### Docker Compose

```bash
# Stop current version
docker-compose down

# Checkout previous version
git checkout <previous-commit>

# Rebuild and start
docker-compose up -d --build
```

### systemd

```bash
# Restore from backup
sudo ./restore.sh sovereigncore_backup_TIMESTAMP

# Restart service
sudo systemctl restart sovereigncore
```

## Support

- Documentation: See README.md and other .md files
- Issues: GitHub Issues
- Logs: Check application and system logs

## Next Steps

1. Set up CI/CD pipeline (see .github/workflows/)
2. Configure branch protection rules
3. Set up monitoring alerts
4. Schedule regular backups
5. Plan disaster recovery procedures
6. Document runbooks for common issues
