# Bagisto Commerce E2E Test Suite - AI Coding Agent Instructions

## Project Overview

Dual-framework E2E test automation suite targeting Bagisto Commerce storefront. Implements **shopping cart state machine test cases** in both Selenium Python and Playwright TypeScript to demonstrate comprehensive cart lifecycle testing.

**Target System:** https://commerce.bagisto.com/ (Laravel-based e-commerce platform)  
**Key Focus:** Cart state transitions from empty → add → modify → checkout → completion

## Critical Test Architecture

### Bagisto Commerce - Direct DOM Interaction

**NO IFRAME HANDLING REQUIRED** - Unlike PrestaShop, Bagisto renders storefront directly.

```python
# Selenium - Direct element access
driver.get("https://commerce.bagisto.com/")
product = driver.find_element(By.CSS_SELECTOR, ".product-card")
product.click()
```

```typescript
// Playwright - Direct locator
await page.goto('https://commerce.bagisto.com/');
const product = page.locator('.product-card').first();
await product.click();
```

**Key Difference from PrestaShop:**
- ❌ No `driver.switch_to.frame()` needed
- ❌ No `page.frameLocator()` needed
- ✅ Standard DOM selectors work immediately

## Critical Developer Workflows

### Selenium Python (`selenium_python/`)

```bash
cd selenium_python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run Bagisto tests (shopping cart state machine)
python test_bagisto_cart.py

# Run PrestaShop tests (legacy - preserved for reference)
python test_e2e_purchase.py
```

**Important:** On Ubuntu 24.04+, Python packages must be installed in a virtual environment (PEP 668). Chrome/Chromium must be installed system-wide.

**Key Pattern - Bagisto:** Direct element interaction
```python
# Add to cart
add_button = driver.find_element(By.CSS_SELECTOR, ".add-to-cart, button[aria-label*='Add to cart']")
add_button.click()

# Verify cart count
cart_counter = driver.find_element(By.CSS_SELECTOR, ".cart-count, [data-cart-count]")
count = cart_counter.text
```

### Playwright TypeScript (`playwright_typescript/`)

```bash
cd playwright_typescript
npm install
npx playwright install chromium
sudo npx playwright install-deps chromium  # Install system dependencies
npm test                         # Run all tests (headless)
npm run test:headed              # Visible browser
npm run test:debug               # Inspector mode
```

**Important:** `playwright.config.ts` must include `ignoreHTTPSErrors: true` for demo sites.

**Key Pattern - Bagisto:** Auto-wait with multiple selector fallbacks
```typescript
// Try multiple selectors for robustness
const addToCartSelectors = [
  'button[aria-label*="Add to cart" i]',
  '.add-to-cart',
  'button.btn-add-to-cart'
];

for (const selector of addToCartSelectors) {
  const button = page.locator(selector).first();
  if (await button.isVisible({ timeout: 2000 })) {
    await button.click();
    break;
  }
}
```

## Project-Specific Conventions

### 1. Selector Strategy for Bagisto (Vue.js Application)

**Priority Order:**
1. **`data-*` attributes** - Most stable (if available)
   ```html
   <button data-action="add-to-cart"> → [data-action="add-to-cart"]
   ```

2. **`aria-label` attributes** - Accessibility-first
   ```html
   <button aria-label="Add to cart"> → button[aria-label*="Add to cart" i]
   ```

3. **Stable CSS classes** - Avoid dynamic Vue classes
   ```html
   <div class="cart-count"> → .cart-count  (good)
   <div class="v-1a2b3c"> → avoid (Vue dynamic)
   ```

4. **Text content** - Last resort, case-insensitive
   ```typescript
   page.locator('button:has-text("Add to Cart")')
   ```

**Why Multiple Selectors?**
Bagisto uses Vue.js components with dynamic class names. Always provide fallback selectors:

```python
# Selenium - Try multiple selectors
selectors = [
    ".add-to-cart",
    "button[aria-label*='Add to cart']",
    "[data-action='add-to-cart']"
]
for selector in selectors:
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        if element.is_displayed():
            element.click()
            break
    except:
        continue
```

### 2. Robust Element Interaction Pattern

**Problem:** Vue.js components may have animations or conditional rendering

**Solution - Wait + Fallback:**

**Selenium:**
```python
# JavaScript click for stubborn elements
try:
    element.click()
except:
    driver.execute_script("arguments[0].click();", element)
```

**Playwright:**
```typescript
// Try with and without force
try {
  await element.click({ timeout: 5000 });
} catch {
  await element.click({ force: true });
}
```

### 3. Wait Strategy Differences

**Bagisto Specifics:**
- Page transitions: Wait for `networkidle` (AJAX-heavy)
- Cart updates: Wait 2-3 seconds after actions
- Form validation: Wait for error/success messages

**Selenium:**
```python
wait = WebDriverWait(driver, 20)
element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
time.sleep(2)  # AJAX cart update
```

**Playwright:**
```typescript
await page.goto('https://commerce.bagisto.com/', { waitUntil: 'networkidle' });
await addButton.click();
await page.waitForTimeout(3000);  // Cart count update
```

### 4. Test Case Structure - Shopping Cart State Machine

**Current Approach:** 7 core test cases + 5 extended scenarios

**Core Tests (Always Run):**
1. TC-CART-001: Empty cart verification
2. TC-CART-002: Add product to cart
3. TC-CART-003: Modify quantity
4. TC-CART-004: Remove product
5. TC-CART-005: Cart persistence (navigation)
6. TC-CHECKOUT-001: Complete guest checkout
7. TC-CHECKOUT-002: Cart reset after order

**Extended Tests (Conditional/Manual):**
8. TC-SESSION-001: Browser restart persistence
9. TC-SESSION-002: Abandoned checkout preservation
10. TC-WISHLIST-001: Save for later
11. TC-INVENTORY-001: Out-of-stock handling
12. TC-PRICE-001: Price change notification

**State Machine Flow:**
```
EMPTY → ADD → ACTIVE → MODIFY → CHECKOUT → COMPLETE → EMPTY
         ↓      ↓         ↓
         └ BROWSE┘        └ REMOVE → EMPTY
                ↓
         SAVE_FOR_LATER
         OUT_OF_STOCK
         PRICE_CHANGE
```

### 5. Console Logging Pattern

**Format - Simple and Professional:**
```
Step 1: Navigating to Bagisto Commerce...
Step 2: Locating product...
  Found product using: .product-card
Step 3: Adding to cart...
  Cart count: 1
TC-CART-002: PASSED
```

**Avoid:**
- ❌ Emojis (📍, ✓, ❌)
- ❌ ASCII art (====)
- ❌ Excessive decoration
- ✅ Keep clean, scannable logs

### 6. Test Data Standards

```python
# Selenium
EMAIL = "john.doe.bagisto@test.com"
FIRST_NAME = "John"
LAST_NAME = "Doe"
ADDRESS = "123 Test Street"
CITY = "New York"
POSTCODE = "10001"
PHONE = "5551234567"
```

```typescript
// Playwright - identical values
const testData = {
  email: 'john.doe.bagisto@test.com',
  firstName: 'John',
  lastName: 'Doe',
  address: '123 Test Street',
  city: 'New York',
  postcode: '10001',
  phone: '5551234567'
};
```

## Error Handling Requirements

### Selenium
- Always capture screenshot on failure: `driver.save_screenshot("selenium_failure.png")`
- Implement `try/except/finally` with `driver.quit()` in finally block

### Playwright
- Configure in `playwright.config.ts`:
  ```typescript
  screenshot: 'only-on-failure',
  video: 'retain-on-failure',
  trace: 'on-first-retry',
  ```
- Built-in HTML report: `npx playwright show-report`

## Adding New Test Cases

1. **Document in `TEST_CASE_DOCUMENTATION.md`** following IEEE 29119 structure (see TC-E2E-001 template)
2. **Implement in both frameworks** to maintain parity
3. **Use identical test data** and step numbers
4. **Follow the 16-step structure** already established (browse → select → cart → checkout → confirm)

## Known Quirks & Workarounds

### PrestaShop Demo Instability
- Demo site resets periodically - tests may fail randomly
- **Mitigation:** CI/CD should retry 2x (Playwright: `retries: 2` in config)
- **Timeout Settings:**
  - Selenium: 20s element wait
  - Playwright: 15s action, 30s navigation

### Flaky Elements (wrap in try-catch)
- Privacy checkbox (`psgdpr`) - may not be present
- Social title radio (`id_gender`) - sometimes optional  
- Password field (`password`) - varies between guest/account mode

### Payment & Terms Checkboxes
Use JavaScript click in Selenium, standard `.check()` in Playwright:
```python
# Selenium - checkboxes often fail with regular click()
driver.execute_script("arguments[0].click();", terms_checkbox)
```

```typescript
// Playwright - built-in .check() handles visibility/interactability
await termsCheckbox.check();
```

## Cross-Framework Test Parity

When modifying tests, **maintain identical behavior** across both implementations:
- Same test steps and numbering
- Same console output format
- Same test data values
- Same error handling patterns
- Update both `test_e2e_purchase.py` and `test-e2e-purchase.spec.ts`

## CI/CD Integration

See `README.md` GitHub Actions example for:
- Parallel matrix execution (Selenium + Playwright)
- Browser installation (`playwright install --with-deps chromium`)
- Python/Node version pinning
- Sequential execution (demo may throttle parallel requests)

---

**Primary Files:**
- Test implementations: `selenium_python/test_e2e_purchase.py`, `playwright_typescript/test-e2e-purchase.spec.ts`
- Test case design: `TEST_CASE_DOCUMENTATION.md`
- QA notes & issues: `README.md` (sections: QA Notes, Known Issues)
