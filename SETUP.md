# Bagisto E2E Test Suite - Setup Guide

Complete E2E test automation for Bagisto Commerce (https://commerce.bagisto.com) covering 16 checkout scenarios using both Playwright TypeScript and Selenium Python.

## Test Coverage

**16 Scenarios (S1-S16):**
- **S1**: Empty Cart Checkout
- **S2**: Remove All Products
- **S3**: Move to Wishlist
- **S4**: Zero Stock Handling
- **S5**: Stock Reduction During Checkout
- **S6**: Price Change During Checkout
- **S7**: Change Shipping Method
- **S8**: Apply Coupon Code
- **S9**: Change Payment Method
- **S10**: Digital Goods (E-Books)
- **S11**: Happy Path Single Product
- **S12**: Reload During Order Creation
- **S13**: Immediate F5 After Place Order
- **S14**: Cancel Order & Reorder
- **S15**: Concurrent Cart Editing
- **S16**: Concurrent Place Order Race

## Quick Start

### Prerequisites

**For Playwright (TypeScript):**
- Node.js 18+ and npm
- Chromium browser (auto-installed by Playwright)

**For Selenium (Python):**
- Python 3.10+
- Chrome/Chromium browser
- ChromeDriver (auto-managed by webdriver-manager)

### 1. Playwright TypeScript Setup

```bash
cd playwright_typescript

# Install dependencies
npm install

# Install Playwright browsers
npx playwright install chromium

# Install system dependencies (Ubuntu/Debian)
sudo npx playwright install-deps chromium

# Create .env file (copy from template)
cp .env.example .env
# Edit .env with your credentials

# Run single test (headed mode - browser visible)
npm run test:bagisto:s1:headed

# Run all tests
npm run test:bagisto:all:headed

# View test report
npx playwright show-report
```

**Available Scripts:**
```bash
npm run test:bagisto:s1:headed   # S1 - Empty Cart
npm run test:bagisto:s11:headed  # S11 - Happy Path
npm run test:bagisto:all         # All tests (headless)
npm run test:bagisto:all:headed  # All tests (browser visible)
```

### 2. Selenium Python Setup

```bash
cd selenium_python

# Create virtual environment (REQUIRED on Ubuntu 24.04+)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run single test (headed mode)
./run-tests.sh s1 headed

# Run in headless mode
./run-tests.sh s1 headless

# Run all tests
./run-tests.sh all headed
```

**Available Test Commands:**
```bash
./run-tests.sh s1 headed    # S1 - Empty Cart (browser visible)
./run-tests.sh s11 headed   # S11 - Happy Path
./run-tests.sh s6 headless  # S6 - Price Change (background)
./run-tests.sh all headed   # All tests (browser visible)
```

## Project Structure

```
.
├── playwright_typescript/          # Playwright TypeScript tests
│   ├── pages/
│   │   ├── AdminPage.ts           # Admin panel interactions
│   │   └── StorePage.ts           # Storefront page object
│   ├── tests/
│   │   ├── bagisto-s1.spec.ts     # S1 - Empty Cart
│   │   ├── bagisto-s11.spec.ts    # S11 - Happy Path
│   │   └── ...                    # 15 test files (S1-S15)
│   ├── playwright.config.ts       # Playwright configuration
│   ├── package.json               # NPM dependencies & scripts
│   └── run-tests.sh               # Test runner script
│
├── selenium_python/               # Selenium Python tests
│   ├── pages/
│   │   ├── admin_page.py          # Admin panel interactions
│   │   └── store_page.py          # Storefront page object
│   ├── tests/
│   │   ├── test_bagisto_s1.py     # S1 - Empty Cart
│   │   ├── test_bagisto_s11.py    # S11 - Happy Path
│   │   └── ...                    # 16 test files (S1-S17, no S13)
│   ├── conftest.py                # Pytest fixtures
│   ├── requirements.txt           # Python dependencies
│   └── run-tests.sh               # Test runner script
│
└── SETUP.md                       # This file
```

## Environment Configuration

Create `.env` file in both `playwright_typescript/` and `selenium_python/`:

```bash
# Bagisto Store URLs
BAGISTO_BASE_URL=https://commerce.bagisto.com
BAGISTO_ADMIN_URL=https://commerce.bagisto.com/admin

# Admin Credentials (Bagisto Demo)
BAGISTO_ADMIN_EMAIL=admin@example.com
BAGISTO_ADMIN_PASSWORD=admin123

# User Credentials (Auto-login for demo)
BAGISTO_USER_EMAIL=john@example.com
BAGISTO_USER_PASSWORD=password123

# Test Configuration
HEADLESS=false  # Set to 'true' for headless mode
```

## Running Tests

### Playwright TypeScript

**Individual Tests:**
```bash
cd playwright_typescript
npm run test:bagisto:s1:headed   # S1 - Empty Cart
npm run test:bagisto:s11:headed  # S11 - Happy Path
npm run test:bagisto:s15:headed  # S15 - Cancel & Reorder
```

**All Tests:**
```bash
npm run test:bagisto:all:headed  # All 15 tests (browser visible)
npm run test:bagisto:all         # Headless mode
```

**Debug Mode:**
```bash
npx playwright test tests/bagisto-s1.spec.ts --debug
```

### Selenium Python

**Always activate virtual environment first:**
```bash
cd selenium_python
source venv/bin/activate  # REQUIRED!
```

**Individual Tests:**
```bash
./run-tests.sh s1 headed    # S1 - Empty Cart (browser visible)
./run-tests.sh s11 headed   # S11 - Happy Path
./run-tests.sh s4 headed    # S4 - Zero Stock (admin dual browser)
```

**All Tests:**
```bash
./run-tests.sh all headed   # All 16 tests (browser visible)
```

**Direct pytest:**
```bash
HEADLESS=false pytest tests/test_bagisto_s1.py -v -s
```

## Troubleshooting

### Playwright Issues

**1. Browser not installed:**
```bash
npx playwright install chromium
sudo npx playwright install-deps chromium
```

**2. CSS not loading (WSL/Ubuntu):**
- Add to `playwright.config.ts`:
```typescript
launchOptions: {
  args: ['--disable-web-security']
}
```

**3. Timeout errors:**
- Increase timeout in `playwright.config.ts`:
```typescript
timeout: 150000,  // 2.5 minutes
```

### Selenium Issues

**1. ChromeDriver version mismatch:**
```bash
pip install --upgrade selenium webdriver-manager
```

**2. Running as root user:**
- Selenium tests auto-add `--no-sandbox` flag when root detected

**3. Virtual environment errors (Ubuntu 24.04+):**
```bash
# Always create and activate venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Element click crashes (ProtocolError):**
- Tests use JavaScript click workaround:
```python
driver.execute_script("arguments[0].click();", element)
```

**Last Updated:** 2025-11-13  
**Test Count:** 15 Playwright + 16 Selenium = 31 total test files  
**Coverage:** 16 unique scenarios (S1-S17 except S13)
