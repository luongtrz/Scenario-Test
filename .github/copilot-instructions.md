# PrestaShop E2E Test Suite - AI Coding Agent Instructions

## Project Overview

Dual-framework E2E test automation suite targeting PrestaShop demo storefront. Implements **identical test case (TC-E2E-001)** in both Selenium Python and Playwright TypeScript to demonstrate cross-framework testing patterns.

**SUT Architecture:** PrestaShop demo runs storefront inside an **iframe** (`#framelive`) - all tests must handle this iframe context.

## Critical Developer Workflows

### Selenium Python (`selenium_python/`)
```bash
cd selenium_python
python3 -m venv venv              # Create virtual environment (Ubuntu/Debian required)
source venv/bin/activate          # Activate venv
pip install -r requirements.txt
python test_e2e_purchase.py
```

**Important:** On Ubuntu 24.04+, Python packages must be installed in a virtual environment (PEP 668). Chrome/Chromium must be installed system-wide.

**Key Pattern:** Explicit iframe switching required
```python
iframe = wait.until(EC.presence_of_element_located((By.ID, "framelive")))
driver.switch_to.frame(iframe)
# All subsequent interactions happen in iframe context
```

### Playwright TypeScript (`playwright_typescript/`)
```bash
cd playwright_typescript
npm install
npx playwright install chromium  # Required for first-time setup
sudo npx playwright install-deps chromium  # Install system dependencies
npm test                         # Headless
npm run test:headed              # Visible browser
npm run test:debug               # Inspector mode
```

**Important:** `playwright.config.ts` must include `ignoreHTTPSErrors: true` for the demo site.

**Key Pattern:** frameLocator (no context switch needed)
```typescript
const frameLocator = page.frameLocator('#framelive');
// All interactions use frameLocator.locator() - stays in main context
```

## Project-Specific Conventions

### 1. Iframe Handling is Non-Negotiable
- **Never** interact with storefront elements without iframe handling
- Selenium: Must `switch_to.frame()` before any storefront interaction
- Playwright: Must use `frameLocator('#framelive')` for all storefront selectors

### 2. Robust Element Interaction Pattern
Both frameworks use fallback strategies for flaky elements:

**Selenium:**
```python
# Use JavaScript executor for unreliable clicks
driver.execute_script("arguments[0].click();", element)

# Try-except blocks for optional elements (privacy checkbox, social title)
try:
    privacy_checkbox = driver.find_element(By.NAME, "psgdpr")
    if not privacy_checkbox.is_selected():
        driver.execute_script("arguments[0].click();", privacy_checkbox)
except:
    print("   ℹ Privacy checkbox not found")
```

**Playwright:**
```typescript
// Timeout-scoped interactions for optional fields
try {
  const privacyCheckbox = frameLocator.locator('input[name="psgdpr"]');
  await privacyCheckbox.check({ timeout: 3000 });
} catch {
  console.log('   ℹ Privacy checkbox not found');
}
```

### 3. Wait Strategy Differences

**Selenium:** Explicit waits required everywhere
- Use `WebDriverWait(driver, 20)` with `expected_conditions`
- Add `time.sleep()` for AJAX transitions (1-3 seconds)

**Playwright:** Auto-wait built-in
- Minimal `waitForTimeout()` needed (2-3 seconds for AJAX only)
- `waitFor({ state: 'visible' })` for critical elements

### 4. Step-by-Step Console Logging Pattern
Both tests implement identical logging format:
```
📍 Step X: [Action description]...
   ✓ [Success confirmation]
   ⚠ [Warning for optional elements]
   ℹ [Informational message]
```

Maintain this format when adding new test steps.

### 5. Selector Strategy
**Prefer this priority:**
1. `name` attribute (forms: `firstname`, `lastname`, `email`)
2. `id` attribute (payments: `#payment-option-1`)
3. `data-*` attributes (`data-button-action='add-to-cart'`)
4. CSS classes (`.product article .thumbnail`)

**Avoid:** XPath, text-based selectors (internationalization risk)

## Test Data Standards

```python
# Use consistent test data across both frameworks
FIRST_NAME = "John"
LAST_NAME = "Doe"
EMAIL = "john.doe.{framework}@automation.com"  # Unique per framework
ADDRESS = "123 Test Street"
POSTCODE = "10001"
CITY = "New York"
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
