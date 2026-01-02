#!/bin/bash
# Test Docker deployment locally for SovereignCore

set -e

echo "========================================"
echo "SovereignCore Docker Deployment Test"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose is installed${NC}"

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env file not found, creating from .env.example${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env file${NC}"
        echo -e "${YELLOW}⚠ Please update passwords in .env before production use!${NC}"
    else
        echo -e "${RED}✗ .env.example not found${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

echo ""
echo "Building Docker image..."
docker build -t sovereigncore:latest .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}✗ Docker image build failed${NC}"
    exit 1
fi

echo ""
echo "Starting services with Docker Compose..."
docker compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Services started${NC}"
else
    echo -e "${RED}✗ Failed to start services${NC}"
    exit 1
fi

echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check service health
echo ""
echo "Checking service health..."

# Check Redis
echo -n "Redis: "
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
fi

# Check API
echo -n "API: "
if curl -f http://localhost:8528/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${YELLOW}⚠ Not ready yet (may need more time)${NC}"
fi

# Check Prometheus
echo -n "Prometheus: "
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${YELLOW}⚠ Not ready yet${NC}"
fi

# Check Grafana
echo -n "Grafana: "
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${YELLOW}⚠ Not ready yet${NC}"
fi

echo ""
echo "========================================"
echo "Service URLs:"
echo "========================================"
echo "API:        http://localhost:8528"
echo "API Docs:   http://localhost:8528/api/docs"
echo "Health:     http://localhost:8528/health"
echo "Metrics:    http://localhost:8528/metrics"
echo "Prometheus: http://localhost:9090"
echo "Grafana:    http://localhost:3000 (admin/admin)"
echo ""
echo "========================================"
echo "Useful Commands:"
echo "========================================"
echo "View logs:        docker compose logs -f"
echo "View API logs:    docker compose logs -f api"
echo "Stop services:    docker compose down"
echo "Restart services: docker compose restart"
echo "Remove volumes:   docker compose down -v"
echo ""
echo -e "${GREEN}✓ Deployment test complete!${NC}"
