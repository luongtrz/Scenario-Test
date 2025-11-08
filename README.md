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
         ↓              ↓           ↓
    WISHLIST      NAVIGATION   REMOVE → EMPTY
```

| Test ID | Description | Selenium | Playwright |
|---------|-------------|----------|------------|
| TC-CART-001 | Empty Cart Verification | ✅ | ✅ |
| TC-CART-002 | Add Single Product to Cart | ✅ | ✅ |
| TC-CART-003 | Modify Cart Quantity | ✅ | ✅ |
| TC-CART-004 | Remove Product from Cart | ✅ | ✅ |
| TC-CART-005 | Cart Persistence After Navigation | ✅ | ✅ |
| TC-CHECKOUT-001 | Guest Checkout Complete Flow | ✅ | ✅ |
| TC-CHECKOUT-002 | Cart State After Order Completion | ✅ | ✅ |
| TC-SESSION-001 | Cart Persistence After Browser Restart | ✅ | ✅ |
| TC-SESSION-002 | Abandoned Checkout Cart Preservation | ✅ | ✅ |
| TC-WISHLIST-001 | Save Item for Later (Wishlist) | ✅ | ✅ |
| TC-INVENTORY-001 | Out-of-Stock Handling | 📝 | 📝 |
| TC-PRICE-001 | Price Change Notification | 📝 | 📝 |

**Legend:**
- ✅ Fully Automated
- 📝 Documented Only (Requires Admin API)

**Automation Coverage:** 10/12 test cases (83%)

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

============================================================
TEST EXECUTION SUMMARY
============================================================
TC-CART-001: PASS
TC-CART-002: PASS
TC-CART-003: PASS
TC-CART-004: PASS
TC-CART-005: PASS
TC-CHECKOUT-001: PASS
TC-CHECKOUT-002: PASS
TC-SESSION-001: PASS
TC-SESSION-002: PASS
TC-WISHLIST-001: PASS (or SKIPPED)

Total: 10/10 passed
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
| **Test Cases** | 1 E2E test (16 steps) | 10 automated + 2 documented |
| **Complexity** | Single checkout flow | Complete cart lifecycle |
| **Selectors** | `name`, `id` attributes | `data-*`, `aria-label`, CSS |
| **Frameworks** | Selenium + Playwright | Selenium + Playwright (full parity) |

---

**Last Updated:** 2025-11-08  
**Test Framework Versions:** Selenium 4.15.2, Playwright 1.40+
