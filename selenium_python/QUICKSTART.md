# Bagisto Selenium Python - Quick Reference

## Test Scenarios Completed

| Test | Description | File |
|------|-------------|------|
| **S1** | Single Product Checkout | `test_bagisto_s1_single_checkout.py` |
| **S2** | Multiple Products + Coupon (HCMUS) | `test_bagisto_s2_multiple_coupon.py` |
| **S3** | Payment Methods Selection | `test_bagisto_s3_payment_methods.py` |
| **S4** | Out of Stock Handling | `test_bagisto_s4_out_of_stock.py` |

## Quick Start

```bash
# 1. Setup (first time only)
./setup.sh

# 2. Configure credentials
nano .env  # Add your Bagisto email/password

# 3. Run tests
./run-tests.sh s1          # Run S1 (headed mode)
./run-tests.sh s2 headless # Run S2 (headless)
./run-tests.sh all         # Run all tests
```

## Run Individual Tests

```bash
# Activate venv
source venv/bin/activate

# Run specific test with verbose output
pytest tests/test_bagisto_s1_single_checkout.py -v -s
pytest tests/test_bagisto_s2_multiple_coupon.py -v -s
pytest tests/test_bagisto_s3_payment_methods.py -v -s
pytest tests/test_bagisto_s4_out_of_stock.py -v -s

# Run all tests
pytest tests/ -v

# Run with HTML report
pytest tests/ --html=reports/report.html --self-contained-html
```

## Environment Variables (.env)

```bash
BAGISTO_BASE_URL=https://commerce.bagisto.com
BAGISTO_EMAIL=your-email@example.com      # ← UPDATE THIS
BAGISTO_PASSWORD=your-password            # ← UPDATE THIS

# Test Configuration
HEADLESS=false                            # true for headless
BROWSER=chrome                            # chrome or firefox
IMPLICIT_WAIT=10
PAGE_LOAD_TIMEOUT=30

# Admin (for S4 - Out of Stock test)
BAGISTO_ADMIN_URL=https://commerce.bagisto.com/admin
BAGISTO_ADMIN_EMAIL=admin@example.com
BAGISTO_ADMIN_PASSWORD=admin123
```

## Test Scenarios Details

### S1 - Single Product Checkout
- Login → Add product → Checkout → Verify order → Verify cart empty
- Captures prices before/after order
- Compares checkout vs order detail prices
- **Expected:** Order created, cart cleared, prices match

### S2 - Multiple Products + Coupon
- Login → Add product → Apply coupon "HCMUS" → Checkout → Verify discount
- Coupon applied at **cart page** (before checkout)
- Verifies discount appears in order detail
- **Expected:** 20% discount applied, order created

### S3 - Payment Methods
- Login → Add product → Test different payment methods → Checkout
- Detects available payment methods
- Tests switching between payment options
- Selects shipping method (Flat Rate with fee)
- **Expected:** Can select payment methods, order created

### S4 - Out of Stock
- User adds product → Admin reduces stock → User tries checkout
- **Expected:** Checkout blocked with error message
- **Note:** Full admin automation requires separate browser instance
- Current implementation demonstrates user flow and detection logic

## Key Implementation Patterns

### 1. Add to Cart - AJAX Wait
```python
add_btn.click()
time.sleep(5)  # CRITICAL: Wait for AJAX
driver.get(f"{base_url}/checkout/cart")  # Verify in cart page
```

### 2. Click Labels for Hidden Inputs
```python
# ✅ CORRECT - Click label
free_shipping_label = driver.find_element(
    By.CSS_SELECTOR, 'label[for="free_free"]'
)
free_shipping_label.click()
```

### 3. Price Verification
```python
# Capture BEFORE placing order
checkout_grand_total = driver.find_element(...).text

# Place order, navigate to order details
time.sleep(3)  # CRITICAL wait for page render

# Compare
order_grand_total = driver.find_element(...).text
assert checkout_grand_total == order_grand_total
```

## Comparison with Playwright TypeScript

| Aspect | Playwright TypeScript | Selenium Python |
|--------|----------------------|-----------------|
| **Run Tests** | `npm test` | `pytest tests/` |
| **Headed Mode** | `npm run test:bagisto:s1:headed` | `./run-tests.sh s1` |
| **Page Objects** | `pages/StorePage.ts` | `pages/store_page.py` |
| **Wait AJAX** | `await page.waitForTimeout(5000)` | `time.sleep(5)` |
| **Click Element** | `await element.click()` | `element.click()` |
| **Reports** | Built-in HTML | `pytest-html` |

Both implementations:
- ✅ Same Page Object Model structure
- ✅ Same test scenarios (S1-S4 completed)
- ✅ Handle Bagisto-specific quirks (AJAX, hidden inputs)
- ✅ Detailed console logging
- ✅ Price verification patterns

## Troubleshooting

### Import errors (pytest not found)
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Cart not updating
- Expected behavior - test waits 5s and verifies via cart page

### Place Order button not clickable
- Test scrolls to bottom and uses JS click as fallback

### Prices don't match
- Ensure 3-second wait after navigating to order detail page

## Next Steps

To implement remaining scenarios (S5-S17):
- S5: Price change detection
- S6: Shipping methods
- S9: Refresh during payment
- S14: Digital goods (e-books)
- S16: Concurrent carts
- S17: Cancel & reorder

**Template:**
```python
# tests/test_bagisto_s5_price_change.py
def test_s5_price_change_detection(driver, base_url, credentials):
    store = StorePage(driver, base_url)
    store.login()
    store.add_first_product_from_home()
    # Add scenario-specific logic here
    store.go_checkout()
    store.fill_shipping_address_minimal()
    store.choose_payment_and_place()
```

---

**Last Updated:** November 12, 2025  
**Status:** S1, S2, S3, S4 completed ✅  
**Total Scenarios:** 4/20 (20% complete)
