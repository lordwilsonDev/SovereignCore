# Gunicorn Configuration for SovereignCore
# Production-ready WSGI server configuration

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('API_PORT', '8528')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('API_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'uvicorn.workers.UvicornWorker'
worker_connections = 1000
max_requests = 10000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 1000  # Add randomness to prevent all workers restarting at once
timeout = 120  # Worker timeout in seconds
graceful_timeout = 30  # Graceful shutdown timeout
keepalive = 5  # Keep-alive connections

# Server mechanics
daemon = False
pidfile = '/tmp/sovereigncore.pid'
user = None  # Run as current user (set to 'sovereign' in Docker)
group = None
tmp_upload_dir = None

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'  # Log to stderr
loglevel = os.getenv('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'sovereigncore'

# Server hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting SovereignCore API Server")

def on_reload(server):
    """Called to recycle workers during a reload."""
    server.log.info("Reloading SovereignCore workers")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"SovereignCore API ready on {bind}")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def pre_exec(server):
    """Called just before a new master process is forked."""
    server.log.info("Forked child, re-executing.")

def worker_int(worker):
    """Called when a worker receives the SIGINT or SIGQUIT signal."""
    worker.log.info(f"Worker received INT or QUIT signal (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info(f"Worker received SIGABRT signal (pid: {worker.pid})")

def on_exit(server):
    """Called just before exiting Gunicorn."""
    server.log.info("Shutting down SovereignCore API Server")

# SSL/TLS Configuration (if enabled)
if os.getenv('TLS_ENABLED', 'false').lower() == 'true':
    certfile = os.getenv('TLS_CERT_PATH')
    keyfile = os.getenv('TLS_KEY_PATH')
    if certfile and keyfile:
        # SSL version and ciphers
        ssl_version = 5  # TLS 1.2+
        ciphers = 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256'
