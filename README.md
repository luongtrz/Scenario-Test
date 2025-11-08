# Bagisto Commerce E2E Test Suite

Dual-framework E2E test automation for Bagisto Commerce demo storefront using Selenium (Python) and Playwright (TypeScript).

**Target System:** https://commerce.bagisto.com/  
**Test Focus:** Shopping cart state transitions and checkout workflows

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
python test_bagisto_cart.py
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

## Test Cases

### Shopping Cart State Machine

```
EMPTY → ADD_ITEM → CART_ACTIVE → MODIFY → CHECKOUT → ORDER → EMPTY
```

| Test ID | Description | Status |
|---------|-------------|--------|
| TC-CART-001 | Empty Cart Verification | Automated |
| TC-CART-002 | Add Single Product to Cart | Automated |
| TC-CART-003 | Modify Cart Quantity | Automated |
| TC-CART-004 | Remove Product from Cart | Automated |
| TC-CART-005 | Cart Persistence After Navigation | Automated |
| TC-CHECKOUT-001 | Guest Checkout Complete Flow | Automated |
| TC-CHECKOUT-002 | Cart State After Order Completion | Automated |

## Key Features Tested

**Cart Behavior:**
- Empty cart initial state
- Add product → cart count updates
- Quantity modifications → subtotal recalculation
- Remove items → return to empty state
- Cart persistence across page navigation

**Checkout Flow:**
- Guest user checkout (no registration)
- Billing address form completion
- Shipping method selection
- Payment method selection (Cash on Delivery)
- Order confirmation verification
- Post-checkout cart reset

## Architecture Note

Unlike PrestaShop (which uses iframe), Bagisto Commerce renders directly - no iframe handling required. Tests interact with standard DOM elements.

**Selector Strategy:**
- `data-*` attributes (preferred)
- `aria-label` attributes
- Stable CSS classes (avoid Vue dynamic classes)
- Text content (fallback)

## Documentation

- **TEST_CASE_DOCUMENTATION_BAGISTO.md** - Detailed test case specifications (IEEE 29119)
- **ARCHITECTURE.md** - Technical patterns and framework comparisons
- **.github/copilot-instructions.md** - AI agent guidelines (updated for Bagisto)

## Requirements

- Python 3.8+ (with venv on Ubuntu 24.04+)
- Node.js 18+
- Chrome/Chromium browser
- Internet connection (tests run against live demo)

## Test Execution Example

```bash
$ python selenium_python/test_bagisto_cart.py

============================================================
TC-CART-001: Empty Cart Verification
============================================================
Step 1: Navigate to Bagisto Commerce...
Step 2: Locate cart icon/counter...
  Cart counter: 0
  PASS: Cart is empty

TC-CART-001: PASSED

============================================================
TC-CART-002: Add Single Product to Cart
============================================================
...

TEST EXECUTION SUMMARY
============================================================
TC-CART-001: PASS
TC-CART-002: PASS
TC-CHECKOUT-001: PASS

Total: 3/3 passed
============================================================
```

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

## Project Comparison

| Aspect | Previous (PrestaShop) | Current (Bagisto) |
|--------|-----------------------|-------------------|
| **Target** | demo.prestashop.com | commerce.bagisto.com |
| **Architecture** | Iframe-based | Direct DOM |
| **Test Cases** | 1 E2E test (16 steps) | 7 test cases (state machine) |
| **Complexity** | Single checkout flow | Cart lifecycle + checkout |
| **Selectors** | `name`, `id` attributes | `data-*`, `aria-label` |

---

**Last Updated:** 2025-11-08  
**Test Framework Versions:** Selenium 4.15.2, Playwright 1.40+
