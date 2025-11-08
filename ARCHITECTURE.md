# Architecture & Design Patterns

## Project Overview

This E2E test suite demonstrates cross-framework testing by implementing identical test case (TC-E2E-001) in both Selenium Python and Playwright TypeScript.

**Target System:** PrestaShop demo storefront  
**Key Challenge:** All storefront elements exist inside iframe `#framelive`

```
PrestaShop Demo Site
└── Main Page (demo.prestashop.com)
    └── <iframe id="framelive">  ← STOREFRONT RUNS HERE
        ├── Product Listings
        ├── Product Details
        ├── Shopping Cart
        └── Checkout Flow
```

## Iframe Handling Patterns

### Selenium Python - Explicit Context Switch

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Must switch context before any storefront interaction
iframe = wait.until(EC.presence_of_element_located((By.ID, "framelive")))
driver.switch_to.frame(iframe)

# Now all interactions happen in iframe context
element = driver.find_element(By.CSS_SELECTOR, ".product")
element.click()

# Switch back to main page if needed
driver.switch_to.default_content()
```

**Pros:** Explicit control, works across all browsers  
**Cons:** Easy to forget switch, context management overhead

### Playwright TypeScript - frameLocator API

```typescript
// Create frame locator (no context switch needed)
const frameLocator = page.frameLocator('#framelive');

// All interactions use frameLocator prefix
const product = frameLocator.locator('.product');
await product.click();

// Main page context remains unchanged
```

**Pros:** Cleaner API, no context switching, less error-prone  
**Cons:** Playwright-specific, not available in Selenium

## Element Interaction Patterns

### 1. Robust Click Strategy

**Problem:** Standard `.click()` sometimes fails on checkboxes, radio buttons, or overlapped elements

**Selenium Solution:**
```python
try:
    element.click()
except:
    # Fallback: JavaScript executor bypasses visibility checks
    driver.execute_script("arguments[0].click();", element)
```

**Playwright Solution:**
```typescript
// Built-in retry and actionability checks
await element.click();

// Force click if element is covered
await element.click({ force: true });
```

### 2. Optional Elements Pattern

**Problem:** Privacy checkbox, social title radio, password field may not always be present

**Solution - Try-Catch Wrapper:**

```python
# Selenium
try:
    privacy_checkbox = driver.find_element(By.NAME, "psgdpr")
    if not privacy_checkbox.is_selected():
        driver.execute_script("arguments[0].click();", privacy_checkbox)
except:
    print("Privacy checkbox not found - continuing")
```

```typescript
// Playwright with timeout
try {
  const privacyCheckbox = frameLocator.locator('input[name="psgdpr"]');
  await privacyCheckbox.check({ timeout: 3000 });
} catch {
  console.log('Privacy checkbox not found - continuing');
}
```

### 3. Wait Strategy Comparison

| Aspect | Selenium | Playwright |
|--------|----------|------------|
| **Default Behavior** | Immediate fail if not found | Auto-wait up to 30s |
| **Explicit Waits** | WebDriverWait + EC required | `.waitFor()` available |
| **AJAX Transitions** | `time.sleep()` needed | Minimal `waitForTimeout()` |
| **Best Practice** | Always use explicit waits | Trust auto-wait, add waits for AJAX only |

**Selenium Example:**
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 20)
element = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary"))
)
time.sleep(2)  # Wait for AJAX animation
```

**Playwright Example:**
```typescript
// Auto-wait built-in - no explicit wait needed
const element = frameLocator.locator('.btn-primary');
await element.click();  // Waits for element to be clickable

// Only for AJAX transitions
await page.waitForTimeout(2000);
```

## Selector Strategy

**Priority (high to low):**

1. **`name` attribute** - Most stable for form fields
   ```html
   <input name="firstname"> → name="firstname"
   ```

2. **`id` attribute** - Unique identifiers
   ```html
   <div id="payment-option-1"> → #payment-option-1
   ```

3. **`data-*` attributes** - Semantic action indicators
   ```html
   <button data-button-action="add-to-cart"> → [data-button-action='add-to-cart']
   ```

4. **CSS classes** - Structural selectors
   ```html
   <article class="product"> → .product
   ```

**Avoid:**
- XPath (difficult to maintain, slower performance)
- Text-based selectors (internationalization issues)
- Deep nested selectors (brittle, breaks easily)

## Test Data Constants

```python
# Define at top of test file for easy maintenance
FIRST_NAME = "John"
LAST_NAME = "Doe"
EMAIL = "john.doe.{framework}@automation.com"  # Unique per framework
ADDRESS = "123 Test Street"
POSTCODE = "10001"
CITY = "New York"
```

**Why unique email per framework?**
- Prevents conflicts if running tests in parallel
- Easier debugging - know which test generated the data
- Avoids potential duplicate account issues on demo site

## Error Handling & Reporting

### Selenium - Screenshot + Cleanup Pattern

```python
try:
    test_guest_checkout_e2e()
except Exception as e:
    print(f"Test failed: {str(e)}")
    driver.save_screenshot("selenium_failure.png")
    raise
finally:
    driver.quit()  # Always cleanup resources
```

### Playwright - Built-in Reporter

```typescript
// playwright.config.ts
{
  screenshot: 'only-on-failure',
  video: 'retain-on-failure',
  trace: 'on-first-retry',
}

// Artifacts automatically captured on failure
// View with: npx playwright show-report
```

## Console Logging Pattern

**Standard format used in both frameworks:**

```
Step 1: Navigating to PrestaShop demo...
Step 2: Switching to storefront iframe...
  Switched to iframe successfully
Step 3: Locating product on homepage...
```

**Benefits:**
- Easy comparison between framework outputs
- Clear visual debugging
- Professional test reports
- No verbose emojis or decorations

## Cross-Framework Test Parity

**Rule:** When modifying one test, update both to maintain parity

| Aspect | Requirement |
|--------|-------------|
| Test steps | Same numbering (1-16) |
| Test data | Identical values |
| Console output | Consistent format |
| Error handling | Similar patterns |
| Assertions | Equivalent logic |

## Known Quirks & Workarounds

### 1. PrestaShop Demo Instability
- **Issue:** Demo site resets periodically, may be unavailable
- **Impact:** Random test failures unrelated to code
- **Mitigation:**
  - Selenium: 20s element timeout
  - Playwright: `retries: 2` in config
  - Screenshot capture on failure for debugging

### 2. Flaky Checkboxes
- **Issue:** Standard click() fails on privacy/terms checkboxes
- **Root Cause:** Custom checkbox styling with overlapping elements
- **Solution:** 
  - Selenium: JavaScript executor click
  - Playwright: Built-in `.check()` method handles this

```python
# Selenium - reliable checkbox interaction
driver.execute_script("arguments[0].click();", checkbox)
```

```typescript
// Playwright - handles overlay automatically
await checkbox.check();
```

### 3. AJAX Page Transitions
- **Issue:** PrestaShop uses AJAX without full page reloads
- **Impact:** Elements may not be immediately available
- **Solution:** Explicit waits after major navigation actions

```python
# After clicking "Add to Cart"
time.sleep(2)  # Wait for modal animation
```

```typescript
// After clicking "Add to Cart"
await page.waitForTimeout(2000);
```

## Framework Comparison

### When to Use Selenium

- Multi-language support needed (Java, C#, Ruby, Python, etc.)
- Large existing Selenium codebase
- Team already familiar with Selenium
- Cross-browser support with Selenium Grid
- Enterprise environments with strict tooling requirements

### When to Use Playwright

- Modern web apps (SPAs, PWAs)
- Starting new test automation project
- Need built-in auto-wait and retry mechanisms
- Want powerful debugging tools (trace viewer, inspector)
- TypeScript/JavaScript team
- Parallel execution and sharding built-in

## Design Decisions

### Why Not Page Object Model (POM)?

**Current Approach:** Direct interaction in test file

**Rationale:**
- Educational purpose - easier for learners to understand
- Single test case - abstraction overhead not justified yet
- Transparency - entire flow visible in one file

**Future:** If scaling to multiple test cases, refactor to POM:
```typescript
class CheckoutPage {
  constructor(private frame: FrameLocator) {}
  
  async fillCustomerDetails(data: CustomerData) {
    await this.frame.locator('input[name="firstname"]').fill(data.firstName);
    // ... other fields
  }
}
```

### Why 16 Steps?

- Covers complete end-to-end checkout flow
- Each step = one user action or verification
- Easy debugging - identify exact failure point
- Consistent with IEEE 29119 test case documentation
- Matches real user journey through the application

### Why CLI Script (run-tests.sh)?

**Benefits:**
- One-command setup and execution
- Auto-installs dependencies (venv, npm packages)
- Colored output for better readability
- Summary report comparing both frameworks
- CI/CD ready with exit codes

## Performance Considerations

- **Execution Mode:** Sequential (demo site may throttle parallel requests)
- **Average Duration:** 35-50 seconds per test
- **Primary Bottleneck:** Network latency to demo site
- **Timeout Settings:**
  - Selenium: 20s element wait
  - Playwright: 15s action timeout, 30s navigation
- **Optimization:** Current performance acceptable, avoid premature optimization

## Maintenance Guidelines

1. **Quarterly Review:** Verify selectors after PrestaShop updates
2. **Monitor Demo Site:** Track uptime and SSL certificate expiry
3. **Update Dependencies:** Keep Selenium and Playwright current
4. **Document New Issues:** Add to known issues section when discovered
5. **Maintain Parity:** Always update both test implementations together
6. **Selector Resilience:** Use semantic selectors over fragile ones
7. **CI/CD Integration:** Monitor test stability metrics

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        framework: [selenium, playwright]
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: ./run-tests.sh ${{ matrix.framework }}
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: test-failures-${{ matrix.framework }}
          path: |
            selenium_failure.png
            playwright-report/
```

### Parallel vs Sequential Execution

**Recommendation:** Sequential execution

**Reasoning:**
- Demo site may throttle concurrent requests
- Shared demo environment could cause race conditions
- Minimal time savings (2-3 minutes) vs. increased flakiness
- Easier to debug when tests run one at a time

## Test Case TC-E2E-001 Design

### Scope
Guest checkout flow from product browsing to order confirmation

### Preconditions
- PrestaShop demo site accessible
- No authentication required
- Test data constants defined

### Test Flow
1. Navigate to demo site
2. Switch to iframe context
3-5. Product selection and cart
6-7. Proceed to checkout
8-9. Fill customer information
10-12. Shipping method selection
13-14. Payment method and terms
15-16. Place order and verify confirmation

### Postconditions
- Order confirmation page displayed
- Order reference number generated
- Test artifacts captured (screenshots, videos, traces)

### Known Limitations
- Demo site resets periodically
- Mock payment only (Pay by Check)
- No real email verification
- Fails at step 6 due to modal selector change

## Key Takeaways

1. **Iframe handling is critical** - Most common failure point for new users
2. **Wait strategies differ significantly** - Playwright auto-wait vs Selenium explicit waits
3. **Optional elements need defensive coding** - Try-catch for resilience
4. **Consistent logging aids debugging** - Simple, clear format without excessive decoration
5. **Cross-framework parity requires discipline** - Update both tests together
6. **JavaScript executor is powerful fallback** - Selenium's ace card for tricky elements
7. **Modern doesn't mean better** - Choose framework based on team and context
