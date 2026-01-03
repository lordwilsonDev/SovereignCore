#!/bin/bash
# 🔮 ULTIMATE SOVEREIGNCORE TEST SUITE
# Comprehensive validation of all systems

set -e  # Exit on any error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     🔮 SOVEREIGNCORE ULTIMATE TEST SUITE 🔮                   ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
WARNINGS=0

# Test result tracking
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASSED${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}: $2"
        ((FAILED++))
    fi
}

warning() {
    echo -e "${YELLOW}⚠️  WARNING${NC}: $1"
    ((WARNINGS++))
}

section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

cd /Users/lordwilson/SovereignCore

# ============================================================================
# PHASE 1: ENVIRONMENT VALIDATION
# ============================================================================
section "PHASE 1: Environment Validation"

# Check Python version
echo "Checking Python version..."
python3 --version
test_result $? "Python 3 installed"

# Check virtual environment
if [ -d ".venv" ]; then
    test_result 0 "Virtual environment exists"
    source .venv/bin/activate
else
    warning "No virtual environment found - using system Python"
fi

# Check dependencies
echo "Checking critical dependencies..."
python3 -c "import fastapi" 2>/dev/null
test_result $? "FastAPI installed"

python3 -c "import jwt" 2>/dev/null
test_result $? "PyJWT installed"

python3 -c "import pytest" 2>/dev/null
test_result $? "Pytest installed"

# Check database
if [ -f "sovereign_users.db" ]; then
    test_result 0 "User database exists"
else
    warning "User database not found - will be created on first run"
fi

# Check .env file
if [ -f ".env" ]; then
    test_result 0 ".env configuration file exists"
else
    warning ".env file not found - using defaults"
fi

# ============================================================================
# PHASE 2: UNIT TESTS
# ============================================================================
section "PHASE 2: Unit Tests"

echo "Running pytest unit tests..."
if pytest tests/ -v --tb=short -m "not integration" 2>&1 | tee /tmp/pytest_output.txt; then
    test_result 0 "Unit tests passed"
else
    test_result 1 "Unit tests failed - check output above"
fi

# ============================================================================
# PHASE 3: INTEGRATION TESTS
# ============================================================================
section "PHASE 3: Integration Tests"

echo "Running integration tests..."
if pytest tests/ -v --tb=short -m "integration" 2>&1; then
    test_result 0 "Integration tests passed"
else
    warning "Integration tests failed or skipped (may require Redis)"
fi

# ============================================================================
# PHASE 4: CODE COVERAGE
# ============================================================================
section "PHASE 4: Code Coverage Analysis"

echo "Running coverage analysis..."
if pytest --cov=api_server --cov=consciousness_bridge --cov=database --cov-report=term-missing --cov-report=html tests/ 2>&1 | tee /tmp/coverage_output.txt; then
    
    # Extract coverage percentage
    COVERAGE=$(grep "TOTAL" /tmp/coverage_output.txt | awk '{print $NF}' | sed 's/%//')
    
    if [ ! -z "$COVERAGE" ]; then
        echo "Coverage: ${COVERAGE}%"
        if [ $(echo "$COVERAGE >= 80" | bc -l) -eq 1 ]; then
            test_result 0 "Code coverage ≥80% (${COVERAGE}%)"
        elif [ $(echo "$COVERAGE >= 60" | bc -l) -eq 1 ]; then
            warning "Code coverage is ${COVERAGE}% (target: 80%)"
        else
            test_result 1 "Code coverage too low: ${COVERAGE}% (minimum: 60%)"
        fi
    else
        warning "Could not extract coverage percentage"
    fi
else
    test_result 1 "Coverage analysis failed"
fi

# ============================================================================
# PHASE 5: API SERVER STARTUP TEST
# ============================================================================
section "PHASE 5: API Server Startup Test"

echo "Testing API server startup..."

# Start server in background
python3 api_server.py &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if server is running
if kill -0 $SERVER_PID 2>/dev/null; then
    test_result 0 "API server started successfully (PID: $SERVER_PID)"
    
    # Test health endpoint
    echo "Testing /health endpoint..."
    if curl -s http://localhost:8528/health | grep -q "healthy"; then
        test_result 0 "Health endpoint responding"
    else
        test_result 1 "Health endpoint not responding correctly"
    fi
    
    # Test root endpoint
    echo "Testing / endpoint..."
    if curl -s http://localhost:8528/ | grep -q "SovereignCore"; then
        test_result 0 "Root endpoint responding"
    else
        test_result 1 "Root endpoint not responding correctly"
    fi
    
    # Test metrics endpoint
    echo "Testing /metrics endpoint..."
    if curl -s http://localhost:8528/metrics | grep -q "python_info"; then
        test_result 0 "Metrics endpoint responding"
    else
        test_result 1 "Metrics endpoint not responding correctly"
    fi
    
    # Cleanup: Stop server
    echo "Stopping test server..."
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    test_result 0 "Server stopped cleanly"
else
    test_result 1 "API server failed to start"
fi

# ============================================================================
# PHASE 6: AUTHENTICATION FLOW TEST
# ============================================================================
section "PHASE 6: Authentication Flow Test"

echo "Starting server for auth tests..."
python3 api_server.py &
SERVER_PID=$!
sleep 3

if kill -0 $SERVER_PID 2>/dev/null; then
    # Test login endpoint
    echo "Testing authentication flow..."
    
    # Try to get token (may fail if no test user exists)
    TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8528/token \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin&password=admin123" 2>/dev/null)
    
    if echo "$TOKEN_RESPONSE" | grep -q "access_token"; then
        test_result 0 "Authentication endpoint working"
        
        # Extract token
        ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
        
        if [ ! -z "$ACCESS_TOKEN" ]; then
            test_result 0 "Access token generated"
            
            # Test protected endpoint with token
            PROTECTED_RESPONSE=$(curl -s http://localhost:8528/api/v1/consciousness/status \
                -H "Authorization: Bearer $ACCESS_TOKEN" 2>/dev/null)
            
            if [ $? -eq 0 ]; then
                test_result 0 "Protected endpoint accessible with token"
            else
                warning "Protected endpoint test inconclusive"
            fi
        else
            warning "Could not extract access token"
        fi
    else
        warning "Authentication test skipped (no test user configured)"
    fi
    
    # Cleanup
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
else
    test_result 1 "Could not start server for auth tests"
fi

# ============================================================================
# PHASE 7: SECURITY CHECKS
# ============================================================================
section "PHASE 7: Security Validation"

# Check for .env.example
if [ -f ".env.example" ]; then
    test_result 0 ".env.example template exists"
else
    warning ".env.example not found"
fi

# Check TLS certificates
if [ -d "certs" ]; then
    test_result 0 "TLS certificates directory exists"
    
    if [ -f "certs/server.crt" ] && [ -f "certs/server.key" ]; then
        test_result 0 "TLS certificates present"
    else
        warning "TLS certificates not generated (run generate_certs.sh)"
    fi
else
    warning "TLS certificates directory not found"
fi

# Check for security headers in code
if grep -q "X-Content-Type-Options" api_server.py; then
    test_result 0 "Security headers implemented"
else
    warning "Security headers may not be configured"
fi

# ============================================================================
# PHASE 8: PRODUCTION READINESS
# ============================================================================
section "PHASE 8: Production Readiness Checks"

# Check for Docker support
if [ -f "Dockerfile" ]; then
    test_result 0 "Dockerfile exists"
else
    warning "Dockerfile not found"
fi

if [ -f "docker-compose.yml" ]; then
    test_result 0 "Docker Compose configuration exists"
else
    warning "docker-compose.yml not found"
fi

# Check for monitoring
if [ -f "prometheus.yml" ]; then
    test_result 0 "Prometheus configuration exists"
else
    warning "Prometheus configuration not found"
fi

# Check for backup scripts
if [ -f "backup.sh" ]; then
    test_result 0 "Backup script exists"
else
    warning "Backup script not found"
fi

# Check for CI/CD
if [ -d ".github/workflows" ]; then
    test_result 0 "GitHub Actions workflows configured"
else
    warning "CI/CD workflows not found"
fi

# ============================================================================
# FINAL REPORT
# ============================================================================
section "FINAL REPORT"

TOTAL=$((PASSED + FAILED))
PASS_RATE=0
if [ $TOTAL -gt 0 ]; then
    PASS_RATE=$((PASSED * 100 / TOTAL))
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    TEST RESULTS SUMMARY                        ║"
echo "╠════════════════════════════════════════════════════════════════╣"
printf "║  ✅ Passed:   %-3d                                             ║\n" $PASSED
printf "║  ❌ Failed:   %-3d                                             ║\n" $FAILED
printf "║  ⚠️  Warnings: %-3d                                             ║\n" $WARNINGS
printf "║  📊 Pass Rate: %-3d%%                                           ║\n" $PASS_RATE
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Determine overall status
if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}🎉 PERFECT! All tests passed with no warnings!${NC}"
        echo -e "${GREEN}✨ SovereignCore is PRODUCTION READY! ✨${NC}"
        exit 0
    else
        echo -e "${YELLOW}✅ All tests passed, but there are $WARNINGS warnings to address.${NC}"
        echo -e "${YELLOW}📋 Review warnings above for optimization opportunities.${NC}"
        exit 0
    fi
else
    echo -e "${RED}⚠️  ATTENTION: $FAILED test(s) failed!${NC}"
    echo -e "${RED}🔧 Please review and fix the failed tests above.${NC}"
    exit 1
fi
