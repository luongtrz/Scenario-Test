#!/bin/bash

# PrestaShop E2E Test Runner
# Runs both Selenium (Python) and Playwright (TypeScript) tests

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   PrestaShop E2E Test Suite - Running All Tests   ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════╝${NC}"
echo ""

# Check for test selection argument
TEST_SUITE="${1:-all}"

# Function to run Selenium Python test
run_selenium() {
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}▶ Running Selenium Python Test...${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    cd selenium_python
    
    # Create venv if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate venv and install dependencies
    source venv/bin/activate
    pip install -q -r requirements.txt
    
    # Run test
    python test_e2e_purchase.py
    SELENIUM_EXIT=$?
    
    deactivate
    cd ..
    
    if [ $SELENIUM_EXIT -eq 0 ]; then
        echo -e "${GREEN}✓ Selenium test PASSED${NC}"
    else
        echo -e "${RED}✗ Selenium test FAILED${NC}"
    fi
    
    return $SELENIUM_EXIT
}

# Function to run Playwright TypeScript test
run_playwright() {
    echo ""
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}▶ Running Playwright TypeScript Test...${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    cd playwright_typescript
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "Installing Node.js dependencies..."
        npm install
        npx playwright install chromium
    fi
    
    # Run test
    npm test
    PLAYWRIGHT_EXIT=$?
    
    cd ..
    
    if [ $PLAYWRIGHT_EXIT -eq 0 ]; then
        echo -e "${GREEN}✓ Playwright test PASSED${NC}"
    else
        echo -e "${RED}✗ Playwright test FAILED${NC}"
    fi
    
    return $PLAYWRIGHT_EXIT
}

# Run tests based on argument
case $TEST_SUITE in
    selenium|python)
        run_selenium
        EXIT_CODE=$?
        ;;
    playwright|typescript|ts)
        run_playwright
        EXIT_CODE=$?
        ;;
    all|*)
        SELENIUM_PASSED=0
        PLAYWRIGHT_PASSED=0
        
        run_selenium || SELENIUM_PASSED=$?
        run_playwright || PLAYWRIGHT_PASSED=$?
        
        echo ""
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}   Test Summary${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        if [ $SELENIUM_PASSED -eq 0 ]; then
            echo -e "   Selenium:  ${GREEN}✓ PASSED${NC}"
        else
            echo -e "   Selenium:  ${RED}✗ FAILED${NC}"
        fi
        
        if [ $PLAYWRIGHT_PASSED -eq 0 ]; then
            echo -e "   Playwright: ${GREEN}✓ PASSED${NC}"
        else
            echo -e "   Playwright: ${RED}✗ FAILED${NC}"
        fi
        
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        # Exit with failure if any test failed
        if [ $SELENIUM_PASSED -ne 0 ] || [ $PLAYWRIGHT_PASSED -ne 0 ]; then
            EXIT_CODE=1
        else
            EXIT_CODE=0
        fi
        ;;
esac

exit $EXIT_CODE
