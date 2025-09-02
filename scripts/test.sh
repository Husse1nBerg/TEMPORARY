#!/bin/bash
# Test script for CROPS Price Tracker
# Path: scripts/test.sh

set -e

echo "🧪 Running CROPS Price Tracker Tests..."

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Track test results
TESTS_PASSED=0
TESTS_FAILED=0

# Backend Tests
echo -e "${BLUE}Running backend tests...${NC}"
cd backend

# Unit tests
echo "  Running unit tests..."
python -m pytest tests/unit -v
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✅ Unit tests passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}  ❌ Unit tests failed${NC}"
    ((TESTS_FAILED++))
fi

# Integration tests
echo "  Running integration tests..."
python -m pytest tests/integration -v
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✅ Integration tests passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}  ❌ Integration tests failed${NC}"
    ((TESTS_FAILED++))
fi

# Test scrapers
echo "  Testing scrapers..."
python -m pytest tests/test_scrapers.py -v
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✅ Scraper tests passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}  ⚠️  Scraper tests failed (may be due to website changes)${NC}"
fi

cd ..

# Frontend Tests
echo -e "${BLUE}Running frontend tests...${NC}"
cd frontend

# Unit tests
echo "  Running unit tests..."
npm run test:ci
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✅ Frontend unit tests passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}  ❌ Frontend unit tests failed${NC}"
    ((TESTS_FAILED++))
fi

# Type checking
echo "  Running type check..."
npm run type-check
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✅ Type check passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}  ❌ Type check failed${NC}"
    ((TESTS_FAILED++))
fi

# Linting
echo "  Running linter..."
npm run lint
if [ $? -eq 0 ]; then
    echo -e "${GREEN}  ✅ Linting passed${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}  ⚠️  Linting warnings${NC}"
fi

cd ..

# E2E Tests (if services are running)
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${BLUE}Running E2E tests...${NC}"
    cd frontend
    npm run test:e2e
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}  ✅ E2E tests passed${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}  ❌ E2E tests failed${NC}"
        ((TESTS_FAILED++))
    fi
    cd ..
else
    echo -e "${YELLOW}Skipping E2E tests (services not running)${NC}"
fi

# Test Summary
echo ""
echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}         TEST SUMMARY              ${NC}"
echo -e "${BLUE}===================================${NC}"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi