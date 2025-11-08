# 🛒 PrestaShop E2E Test Suite

> **Dual-Framework Testing**: Cùng một test case được implement bằng cả **Selenium (Python)** và **Playwright (TypeScript)** để demo cross-framework testing patterns.

## 📖 Tổng Quan

Project này là bộ test automation end-to-end cho PrestaShop demo storefront. Test case chính (TC-E2E-001) mô phỏng quy trình mua hàng hoàn chỉnh của khách vãng lai (guest checkout).

### ⚠️ Kiến Trúc Quan Trọng

PrestaShop demo chạy storefront bên trong một **iframe** (`#framelive`). Đây là điểm khác biệt quan trọng - tất cả các test đều phải xử lý iframe context này.

---

## 🚀 Quick Start

### Cách Đơn Giản Nhất - Chạy Tất Cả Tests

```bash
./run-tests.sh
```

### Chạy Từng Framework

```bash
# Chỉ chạy Selenium Python
./run-tests.sh selenium

# Chỉ chạy Playwright TypeScript  
./run-tests.sh playwright
```

---

## 📋 Test Case TC-E2E-001: Guest Checkout

**Mục tiêu:** Verify khách vãng lai có thể hoàn tất quy trình mua hàng từ đầu đến cuối.

**Test Flow (16 bước):**
1. ️Navigate → PrestaShop demo
2. ️Switch → Iframe context (`#framelive`)
3. ️Locate → Sản phẩm đầu tiên
4. ️Click → Xem chi tiết sản phẩm
5. ️Click → "Add to Cart"
6. ️Click → "Proceed to Checkout" (modal)
7. ️Click → "Proceed to Checkout" (cart page)
8-9. Fill → Thông tin cá nhân (tên, email, địa chỉ)
10. ️Continue → Shipping method
11. Confirm → Phương thức vận chuyển
12. ️Continue → Payment method
13. Select → "Pay by Check"
14. Check → Terms and Conditions
15. Click → "Place Order"
16. ️Verify → Order confirmation

**Status:** ⚠️ Hiện tại pass 5/16 bước (vấn đề với selector tại bước 6)

---

## 🔧 Setup Chi Tiết

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
