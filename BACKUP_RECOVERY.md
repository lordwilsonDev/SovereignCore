# Backup and Recovery Procedures

This document outlines the backup and recovery procedures for SovereignCore.

## Overview

SovereignCore includes automated backup scripts that protect:
- Redis data (RDB and AOF files)
- SQLite database (sovereign_rekor.db)
- Configuration files (.env, redis.conf, etc.)
- Data directories (data/, mcp_data/, memory/)

## Backup Strategy

### Automated Backups

**Daily Backups** (recommended)

Set up a cron job to run daily backups:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/sovereigncore/backup.sh >> /var/log/sovereigncore-backup.log 2>&1
```

**Hourly Backups** (for critical systems)

```bash
# Hourly backups
0 * * * * /opt/sovereigncore/backup.sh >> /var/log/sovereigncore-backup.log 2>&1
```

### Manual Backup

To create a manual backup:

```bash
cd /opt/sovereigncore
sudo ./backup.sh
```

### Backup Configuration

Environment variables for backup script:

```bash
# Backup directory (default: /var/backups/sovereigncore)
export BACKUP_DIR="/var/backups/sovereigncore"

# Retention period in days (default: 30)
export RETENTION_DAYS=30

# Remote backup location (optional)
export REMOTE_BACKUP_PATH="user@backup-server:/backups/sovereigncore"
```

## Backup Contents

Each backup includes:

1. **Redis Data**
   - dump.rdb (RDB snapshot)
   - appendonly.aof (AOF log)

2. **Database**
   - sovereign_rekor.db (SQLite database)

3. **Configuration Files**
   - .env (environment variables)
   - redis.conf (Redis configuration)
   - users.acl (Redis ACL)
   - prometheus.yml
   - alertmanager.yml
   - alerts.yml
   - docker-compose.yml
   - gunicorn.conf.py

4. **Data Directories**
   - data/
   - mcp_data/
   - memory/

5. **Metadata**
   - backup_info.txt (backup information)

## Recovery Procedures

### Full System Restore

1. **List available backups:**

```bash
ls -lh /var/backups/sovereigncore/
```

2. **Restore from backup:**

```bash
cd /opt/sovereigncore
sudo ./restore.sh sovereigncore_backup_20260102_140000
```

3. **Verify restoration:**

```bash
# Check service status
sudo systemctl status sovereigncore

# Check API health
curl http://localhost:8528/health

# Check logs
sudo journalctl -u sovereigncore -f
```

### Partial Recovery

#### Restore Redis Only

```bash
# Extract backup
tar -xzf /var/backups/sovereigncore/sovereigncore_backup_TIMESTAMP.tar.gz

# Stop Redis
sudo systemctl stop redis

# Restore RDB file
sudo cp sovereigncore_backup_TIMESTAMP/redis_dump.rdb /var/lib/redis/dump.rdb
sudo chown redis:redis /var/lib/redis/dump.rdb

# Start Redis
sudo systemctl start redis
```

#### Restore Database Only

```bash
# Extract backup
tar -xzf /var/backups/sovereigncore/sovereigncore_backup_TIMESTAMP.tar.gz

# Stop service
sudo systemctl stop sovereigncore

# Restore database
cp sovereigncore_backup_TIMESTAMP/sovereign_rekor.db /opt/sovereigncore/

# Start service
sudo systemctl start sovereigncore
```

#### Restore Configuration Only

```bash
# Extract backup
tar -xzf /var/backups/sovereigncore/sovereigncore_backup_TIMESTAMP.tar.gz

# Restore config files
cp sovereigncore_backup_TIMESTAMP/config/* /opt/sovereigncore/

# Restart services
sudo systemctl restart sovereigncore
```

## Remote Backup

### Using rsync

Add to backup.sh or run separately:

```bash
# Sync to remote server
rsync -avz --delete \
  /var/backups/sovereigncore/ \
  user@backup-server:/backups/sovereigncore/
```

### Using AWS S3

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure

# Upload backup
aws s3 cp /var/backups/sovereigncore/sovereigncore_backup_TIMESTAMP.tar.gz \
  s3://your-bucket/backups/sovereigncore/

# Sync entire backup directory
aws s3 sync /var/backups/sovereigncore/ \
  s3://your-bucket/backups/sovereigncore/
```

### Using Google Cloud Storage

```bash
# Install gsutil
pip install gsutil

# Authenticate
gcloud auth login

# Upload backup
gsutil cp /var/backups/sovereigncore/sovereigncore_backup_TIMESTAMP.tar.gz \
  gs://your-bucket/backups/sovereigncore/
```

## Disaster Recovery Plan

### Scenario 1: Data Corruption

1. Stop all services
2. Identify last known good backup
3. Run restore script
4. Verify data integrity
5. Restart services
6. Monitor for issues

### Scenario 2: Complete System Failure

1. Provision new server
2. Install dependencies
3. Clone repository
4. Download latest backup from remote storage
5. Run restore script
6. Update DNS/load balancer
7. Verify functionality

### Scenario 3: Accidental Deletion

1. Identify what was deleted
2. Find appropriate backup
3. Extract specific files/directories
4. Restore only affected components
5. Verify restoration

## Testing Backups

**Monthly Backup Test** (recommended)

1. Create test environment
2. Restore latest backup
3. Verify all services start
4. Run smoke tests
5. Document any issues

```bash
# Test restore script
./test_restore.sh
```

## Monitoring Backups

### Check Backup Status

```bash
# List recent backups
ls -lht /var/backups/sovereigncore/ | head -10

# Check backup log
tail -f /var/log/sovereigncore-backup.log

# Verify backup integrity
tar -tzf /var/backups/sovereigncore/sovereigncore_backup_TIMESTAMP.tar.gz
```

### Backup Alerts

Set up monitoring for:
- Backup failures
- Missing backups (no backup in 24 hours)
- Backup size anomalies
- Disk space for backups

## Retention Policy

**Recommended retention:**
- Daily backups: 30 days
- Weekly backups: 12 weeks
- Monthly backups: 12 months
- Yearly backups: 7 years (if required by compliance)

**Implementation:**

```bash
# Keep daily backups for 30 days
find /var/backups/sovereigncore -name "*daily*.tar.gz" -mtime +30 -delete

# Keep weekly backups for 84 days
find /var/backups/sovereigncore -name "*weekly*.tar.gz" -mtime +84 -delete

# Keep monthly backups for 365 days
find /var/backups/sovereigncore -name "*monthly*.tar.gz" -mtime +365 -delete
```

## Security Considerations

1. **Encrypt backups** before uploading to remote storage
2. **Restrict access** to backup files (chmod 600)
3. **Store credentials** securely (use secrets manager)
4. **Audit backup access** regularly
5. **Test restore procedures** regularly

### Encrypting Backups

```bash
# Encrypt backup with GPG
gpg --symmetric --cipher-algo AES256 \
  /var/backups/sovereigncore/sovereigncore_backup_TIMESTAMP.tar.gz

# Decrypt backup
gpg --decrypt \
  /var/backups/sovereigncore/sovereigncore_backup_TIMESTAMP.tar.gz.gpg \
  > sovereigncore_backup_TIMESTAMP.tar.gz
```

## Troubleshooting

### Backup Fails

1. Check disk space: `df -h`
2. Check permissions: `ls -la /var/backups/sovereigncore`
3. Check logs: `tail -f /var/log/sovereigncore-backup.log`
4. Verify Redis is running: `systemctl status redis`

### Restore Fails

1. Verify backup integrity: `tar -tzf backup.tar.gz`
2. Check available disk space
3. Ensure services are stopped
4. Check file permissions
5. Review restore logs

### Backup Too Large

1. Exclude unnecessary files in backup script
2. Compress more aggressively
3. Implement incremental backups
4. Clean old data before backup

## References

- [Redis Persistence](https://redis.io/topics/persistence)
- [SQLite Backup](https://www.sqlite.org/backup.html)
- [Linux Backup Best Practices](https://www.redhat.com/sysadmin/backup-best-practices)
