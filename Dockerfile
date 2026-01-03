# Simplified Dockerfile for SovereignCore
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production

# Create non-root user and set permissions
RUN useradd -m sovereign && chown -R sovereign:sovereign /app
USER sovereign

# Expose API port
EXPOSE 8528

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8528/health || exit 1

# Run the application with gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "api_server:app"]
