# Bagisto Commerce E2E Tests - Selenium Python

Selenium Python implementation of Bagisto Commerce test suite (equivalent to Playwright TypeScript version).

## Project Structure

```
selenium_python/
├── pages/
│   ├── __init__.py
│   └── store_page.py          # Page Object Model for storefront
├── tests/
│   ├── __init__.py
│   └── test_bagisto_s1_single_checkout.py  # S1 test case
├── conftest.py                 # Pytest fixtures and configuration
├── pytest.ini                  # Pytest settings
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (credentials)
└── README.md                   # This file
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Chrome or Firefox browser

## Installation

### 1. Create Virtual Environment (Ubuntu 24.04+ Required)

```bash
cd selenium_python
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `selenium` - WebDriver automation
- `webdriver-manager` - Auto-download browser drivers
- `pytest` - Test framework
- `python-dotenv` - Environment variable management
- `pytest-html` - HTML test reports

### 3. Configure Environment Variables

Edit `.env` file with your Bagisto credentials:

```bash
BAGISTO_BASE_URL=https://commerce.bagisto.com
BAGISTO_EMAIL=your-email@example.com
BAGISTO_PASSWORD=your-password

# Test Configuration
HEADLESS=false          # Set to 'true' for headless mode
BROWSER=chrome          # 'chrome' or 'firefox'
IMPLICIT_WAIT=10
PAGE_LOAD_TIMEOUT=30
```

**IMPORTANT:** Never commit `.env` to version control!

## Running Tests

### Run All Tests

```bash
# Headed mode (browser visible)
pytest tests/

# Headless mode
HEADLESS=true pytest tests/
```

### Run Specific Test

```bash
# Run S1 test only
pytest tests/test_bagisto_s1_single_checkout.py

# Run with verbose output
pytest tests/test_bagisto_s1_single_checkout.py -v

# Run with detailed output
pytest tests/test_bagisto_s1_single_checkout.py -vv -s
```

### Run with HTML Report

```bash
pytest tests/ --html=reports/report.html --self-contained-html
```

### Run with Different Browser

```bash
# Firefox
BROWSER=firefox pytest tests/

# Chrome (default)
BROWSER=chrome pytest tests/
```

## Test Case: S1 - Single Product Checkout

**File:** `tests/test_bagisto_s1_single_checkout.py`

**Scenario:** Complete checkout flow for single product

**Steps:**
1. Login to Bagisto Commerce
2. Add first simple product to cart
3. Verify cart has item
4. Proceed to checkout
5. Fill shipping address
6. Capture checkout prices (Subtotal, Delivery, Grand Total)
7. Select Free Shipping + Cash On Delivery
8. Place order
9. Verify order success page
10. Extract order ID and navigate to order details
11. Compare checkout prices vs order detail prices
12. Verify cart is empty after checkout
13. Verify order appears in order history

**Expected Results:**
- Order placed successfully
- Prices match between checkout and order detail
- Cart emptied after order
- Order visible in order history with valid status

## Key Implementation Details

### Page Object Model

`pages/store_page.py` implements reusable methods:
- `login()` - Login with auto cookie consent dismissal
- `add_first_product_from_home()` - Add product with 5s AJAX wait
- `fill_shipping_address_minimal()` - Fill address form
- `choose_payment_and_place()` - Select shipping/payment + place order
- `get_latest_order()` - Retrieve order from history

### Critical Patterns

#### 1. Add to Cart - AJAX Wait Pattern

```python
# Click Add To Cart
add_btn.click()

# CRITICAL: Wait 5 seconds for AJAX
time.sleep(5)

# Navigate to cart page to verify
driver.get(f"{base_url}/checkout/cart")

# Count items
qty_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="hidden"][name="quantity"]')
```

#### 2. Click Labels for Hidden Inputs

```python
# ❌ WRONG - Input is hidden
driver.find_element(By.ID, "free_free").click()

# ✅ CORRECT - Click the label
free_shipping_label = driver.find_element(By.CSS_SELECTOR, 'label[for="free_free"]')
free_shipping_label.click()
```

#### 3. Price Verification Pattern

```python
# Capture BEFORE placing order
checkout_grand_total = driver.find_element(...).text

# Place order and navigate to order details
# ...

# Wait 3s for order page to render (CRITICAL!)
time.sleep(3)

# Extract order price
order_grand_total = driver.find_element(...).text

# Compare
assert checkout_grand_total == order_grand_total
```

## Browser Drivers

`webdriver-manager` automatically downloads browser drivers:
- **ChromeDriver** for Chrome
- **GeckoDriver** for Firefox

No manual driver installation needed!

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'selenium'"

**Solution:** Activate virtual environment and install dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Cart not updating after Add To Cart

**Solution:** This is expected - test waits 5 seconds and verifies by navigating to cart page.

### Issue: Place Order button not clickable

**Solution:** Test scrolls to bottom and uses JavaScript click as fallback.

### Issue: Prices don't match

**Solution:** Ensure 3-second wait after navigating to order detail page.

## Comparison with Playwright TypeScript

| Feature | Playwright TypeScript | Selenium Python |
|---------|----------------------|-----------------|
| Framework | Playwright + TypeScript | Selenium + Python + Pytest |
| Page Objects | `pages/StorePage.ts` | `pages/store_page.py` |
| Config | `playwright.config.ts` | `conftest.py` + `pytest.ini` |
| Test Files | `tests/bagisto-s*.spec.ts` | `tests/test_bagisto_s*.py` |
| Run Tests | `npm test` | `pytest tests/` |
| Reports | Built-in HTML | `pytest-html` plugin |

**Both implementations:**
- Follow same 20-scenario structure (S1-S17 + edge cases)
- Use Page Object Model
- Handle Bagisto-specific quirks (AJAX cart, hidden inputs, etc.)
- Support headed/headless modes
- Generate detailed reports

## Next Steps

To implement remaining scenarios (S2-S17):

1. Create new test files: `test_bagisto_s2_*.py`, etc.
2. Reuse methods from `StorePage`
3. Follow same console logging pattern
4. Add scenario-specific logic (coupons, digital goods, etc.)

**Example:**
```python
# tests/test_bagisto_s2_multiple_coupon.py
def test_s2_checkout_with_coupon(driver, base_url, credentials):
    store = StorePage(driver, base_url)
    store.login()
    store.add_first_product_from_home()
    store.go_checkout()
    # Apply coupon logic here
    store.fill_shipping_address_minimal()
    store.choose_payment_and_place()
    # ...
```

## License

Test automation suite for educational purposes.

**Target System:** https://commerce.bagisto.com/ (demo site)
