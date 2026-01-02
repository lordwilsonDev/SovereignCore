#!/bin/bash
# Run tests with coverage reporting for SovereignCore

set -e

echo "========================================"
echo "SovereignCore Test Suite with Coverage"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Warning: No virtual environment detected${NC}"
    echo "Attempting to activate .venv..."
    if [ -d ".venv" ]; then
        source .venv/bin/activate
        echo -e "${GREEN}Virtual environment activated${NC}"
    else
        echo -e "${RED}Error: .venv not found. Please create a virtual environment first.${NC}"
        exit 1
    fi
fi

# Install test dependencies if needed
echo "Checking test dependencies..."
pip install -q pytest pytest-cov pytest-asyncio pytest-httpx 2>/dev/null || true

echo ""
echo "Running tests with coverage..."
echo ""

# Run pytest with coverage
pytest \
    --cov=api_server \
    --cov=consciousness_bridge \
    --cov=mcp_bridge \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=json \
    --cov-fail-under=80 \
    -v \
    tests/

COVERAGE_EXIT_CODE=$?

echo ""
echo "========================================"

if [ $COVERAGE_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Tests passed with >80% coverage!${NC}"
    echo ""
    echo "Coverage reports generated:"
    echo "  - Terminal: See above"
    echo "  - HTML: htmlcov/index.html"
    echo "  - JSON: coverage.json"
else
    echo -e "${RED}✗ Tests failed or coverage below 80%${NC}"
    echo ""
    echo "To view detailed HTML coverage report:"
    echo "  open htmlcov/index.html"
fi

echo "========================================"

exit $COVERAGE_EXIT_CODE
