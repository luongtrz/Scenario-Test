# 🛒 PrestaShop E2E Test Suite

> **Dual-Framework Testing:** Cùng một test case được implement bằng cả **Selenium (Python)** và **Playwright (TypeScript)** để demo cross-framework testing patterns.

[![Selenium](https://img.shields.io/badge/Selenium-4.15.2-43B02A?logo=selenium)](https://selenium.dev)
[![Playwright](https://img.shields.io/badge/Playwright-1.40.0-2EAD33?logo=playwright)](https://playwright.dev)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?logo=typescript&logoColor=white)](https://typescriptlang.org)

---

## 🚀 Quick Start

```bash
# Chạy tất cả tests (tự động cài dependencies)
./run-tests.sh

# Hoặc chạy riêng từng framework
./run-tests.sh selenium    # Python + Selenium
./run-tests.sh playwright  # TypeScript + Playwright
```

**Lần đầu chạy?** → Đọc [GETTING_STARTED.md](GETTING_STARTED.md) để setup environment.

---

## 📚 Documentation

Không biết đọc file nào? → Xem [DOCS_GUIDE.md](DOCS_GUIDE.md)

| File | Mô Tả | Audience |
|------|-------|----------|
| [GETTING_STARTED.md](GETTING_STARTED.md) | 🎯 Quick start, cài đặt, troubleshooting | Beginners |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 🏗️ Design patterns, technical decisions | Developers |
| [TEST_CASE_DOCUMENTATION.md](TEST_CASE_DOCUMENTATION.md) | 📝 Test design chi tiết (IEEE 29119) | QA Engineers |
| [.github/copilot-instructions.md](.github/copilot-instructions.md) | 🤖 AI coding agent guidelines | AI Assistants |

---

## 📋 Test Case TC-E2E-001: Guest Checkout

**Mục tiêu:** Verify khách vãng lai có thể hoàn tất quy trình mua hàng từ đầu đến cuối.

**Test Flow (16 bước):**

1. Navigate → PrestaShop demo
2. Switch → Iframe context (`#framelive`) ⚠️ **Critical!**
3. Locate → Sản phẩm đầu tiên
4. Click → Xem chi tiết
5. Add to Cart → Thêm vào giỏ
6. Proceed to Checkout → Từ modal
7. Proceed to Checkout → Từ cart page
8-9. Fill Form → Thông tin cá nhân & địa chỉ
10. Continue → Shipping method
11. Confirm → Phương thức vận chuyển
12. Continue → Payment method
13. Select → "Pay by Check"
14. Accept → Terms and Conditions
15. Place Order → Submit
16. Verify → Order confirmation

**Current Status:** ⚠️ Pass 5/16 steps (failing at step 6 - checkout modal selector issue)

---

## ⚠️ Kiến Trúc Quan Trọng

PrestaShop demo chạy storefront bên trong **iframe `#framelive`**. Đây là điểm khác biệt quan trọng nhất!

### Selenium - Explicit Context Switch
```python
iframe = driver.find_element(By.ID, "framelive")
driver.switch_to.frame(iframe)
# Bây giờ mới interact được với storefront
```

### Playwright - frameLocator API
```typescript
const frameLocator = page.frameLocator('#framelive');
// Tất cả interactions dùng frameLocator
```

→ Chi tiết: [ARCHITECTURE.md](ARCHITECTURE.md#iframe-handling-patterns)

---

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
