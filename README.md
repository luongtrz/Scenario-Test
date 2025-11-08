# PrestaShop E2E Test Suite

Dual-framework E2E test automation for PrestaShop demo storefront using Selenium (Python) and Playwright (TypeScript).

## Quick Start

```bash
# Run all tests (auto-installs dependencies)
./run-tests.sh

# Run specific framework
./run-tests.sh selenium
./run-tests.sh playwright
```

## Manual Setup

### Selenium Python

```bash
cd selenium_python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test_e2e_purchase.py
```

### Playwright TypeScript

```bash
cd playwright_typescript
npm install
npx playwright install chromium
sudo npx playwright install-deps chromium  # Ubuntu/Debian
npm test                    # headless
npm run test:headed         # visible browser
npm run test:debug          # debug mode
```

## Test Case: TC-E2E-001 Guest Checkout

16-step end-to-end purchase flow testing guest user checkout on PrestaShop demo.

**Status:** Pass 5/16 steps (failing at checkout modal selector - step 6)

## Critical Architecture Note

PrestaShop demo runs storefront inside iframe `#framelive` - all tests must handle this:

```python
# Selenium - explicit context switch
iframe = driver.find_element(By.ID, "framelive")
driver.switch_to.frame(iframe)
```

```typescript
// Playwright - frameLocator API
const frameLocator = page.frameLocator('#framelive');
```

## Documentation

- **ARCHITECTURE.md** - Technical details, design patterns, framework comparisons
- **TEST_CASE_DOCUMENTATION.md** - IEEE 29119 test case design
- **.github/copilot-instructions.md** - AI coding agent guidelines

## Requirements

- Python 3.8+ (with venv on Ubuntu 24.04+)
- Node.js 18+
- Chrome/Chromium browser

## CI/CD Example

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        framework: [selenium, playwright]
    steps:
      - uses: actions/checkout@v3
      - run: ./run-tests.sh ${{ matrix.framework }}
```
