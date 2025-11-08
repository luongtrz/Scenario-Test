# 🛒 PrestaShop E2E Purchase Test Suite

Complete test documentation and automation for PrestaShop demo storefront end-to-end purchase flow.

---

## 📋 Test Case Documentation

### TC-E2E-001: Guest Checkout - Happy Path

**Objective:** Verify that a guest user can successfully complete a purchase from product selection to order confirmation.

**Test Type:** End-to-End Acceptance Test  
**Priority:** High (P1)  
**Status:** ✅ Automated

**Coverage:**
- Product browsing and selection
- Add to cart functionality
- Guest checkout process
- Personal information validation
- Address entry
- Shipping method selection
- Payment method selection
- Terms acceptance
- Order placement
- Order confirmation verification

---

## 🚀 Run Instructions

### Option 1: Selenium (Python)

#### Prerequisites
- Python 3.8+
- pip package manager
- Chrome browser installed

#### Installation
```bash
cd selenium_python
pip install -r requirements.txt
```

#### Execution
```bash
# Run the test
python test_e2e_purchase.py
```

#### Expected Output
```
🚀 Starting Selenium WebDriver...
📍 Step 1: Navigating to PrestaShop demo...
📍 Step 2: Switching to storefront iframe...
   ✓ Switched to iframe successfully
...
============================================================
✅ Selenium: Order placed successfully!
============================================================
```

---

### Option 2: Playwright (TypeScript)

#### Prerequisites
- Node.js 18+
- npm package manager

#### Installation
```bash
cd playwright_typescript
npm install
npx playwright install chromium
```

#### Execution
```bash
# Run in headless mode
npm test

# Run with visible browser
npm run test:headed

# Run in debug mode with Playwright Inspector
npm run test:debug
```

#### Expected Output
```
Running 1 test using 1 worker
🚀 Starting Playwright test...
📍 Step 1: Navigating to PrestaShop demo...
📍 Step 2: Switching to storefront iframe...
...
============================================================
✅ Playwright: Order placed successfully!
============================================================

  1 passed (45.2s)
```

---

## 📊 Test Results & Reports

### Selenium
- **Screenshots:** Captured on failure → `selenium_failure.png`
- **Console Output:** Real-time step-by-step progress
- **Exit Code:** 0 = Pass, Non-zero = Fail

### Playwright
- **HTML Report:** Auto-generated at `playwright-report/index.html`
- **Screenshots:** Captured on failure in report
- **Trace Viewer:** Available for debugging failures
- **Video Recording:** Available for failed tests

To view Playwright report:
```bash
npx playwright show-report
```

---

## ⚠️ QA Notes & Known Issues

### 1. **Iframe Handling**
- **Issue:** The PrestaShop demo loads the storefront inside an iframe (`#framelive`)
- **Impact:** Direct selectors won't work without switching context
- **Solution:** 
  - Selenium: Use `driver.switch_to.frame()`
  - Playwright: Use `page.frameLocator('#framelive')`

### 2. **Dynamic Content Loading**
- **Issue:** AJAX-based page transitions without full reloads
- **Impact:** May cause timing issues if not properly awaited
- **Solution:** Use explicit waits (WebDriverWait / waitFor) with appropriate timeouts

### 3. **Selector Stability**
- **Issue:** Some elements use generated IDs or dynamic classes
- **Impact:** Tests may break if PrestaShop updates their theme
- **Solution:** 
  - Prefer semantic selectors (name, data attributes)
  - Use CSS selectors over XPath for better resilience
  - Implemented fallback strategies where possible

### 4. **Localization / Language Variations**
- **Issue:** Button text may vary based on demo language settings
- **Impact:** Text-based assertions could fail
- **Solution:** 
  - Use regex patterns for flexible matching
  - Rely on structural selectors (IDs, data attributes) over text
  - Case-insensitive matching for confirmation messages

### 5. **Demo Environment Limitations**
- **Issue:** PrestaShop demo resets periodically and may be unavailable
- **Impact:** Tests may fail due to infrastructure, not code
- **Mitigation:** 
  - Implemented 20-30 second timeouts
  - Retry logic recommended in CI/CD (2 retries configured for Playwright)
  - Screenshot capture on failure for debugging

### 6. **Payment Processing**
- **Issue:** Demo uses mock payment methods (Pay by Check)
- **Impact:** Real payment gateway flows are not tested
- **Note:** This is acceptable for demo environment testing

### 7. **Flaky Elements**
- **Privacy Checkbox (psgdpr):** May not always be present
- **Social Title Radio:** Sometimes optional
- **Password Field:** Inconsistent between true guest vs account creation
- **Solution:** All wrapped in try-catch blocks with informative warnings

### 8. **Performance Considerations**
- **Average Test Duration:** 35-50 seconds (network dependent)
- **Timeout Settings:** 
  - Selenium: 20 seconds per element wait
  - Playwright: 15 seconds action timeout, 30 seconds navigation
- **Recommendation:** Run tests sequentially, not in parallel (demo may throttle)

### 9. **Browser Compatibility**
- **Tested On:** Chrome/Chromium (latest)
- **Expected Support:** Firefox, Safari (with minor adjustments)
- **Not Tested:** Edge, mobile browsers

### 10. **Maintenance Recommendations**
- Review selectors quarterly or after PrestaShop updates
- Monitor demo site stability (uptime, SSL cert expiry)
- Keep Selenium WebDriver and Playwright updated
- Document any new failures in CI/CD pipeline

---

## 🔄 CI/CD Integration Suggestions

### GitHub Actions Example
```yaml
name: PrestaShop E2E Tests

on: [push, pull_request]

jobs:
  selenium-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          cd selenium_python
          pip install -r requirements.txt
          python test_e2e_purchase.py

  playwright-typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: |
          cd playwright_typescript
          npm install
          npx playwright install --with-deps chromium
          npm test
```

---

## 📞 Support & Contribution

**Test Documentation:** See inline comments in test files  
**Bug Reports:** Create issue with failure screenshot and logs  
**Improvements:** Follow IEEE 29119 test design principles

---

**Last Updated:** 2025-11-08  
**Maintained By:** QA Automation Team  
**Test Framework Versions:** Selenium 4.15.2, Playwright 1.40.0
