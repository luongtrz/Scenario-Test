# 🏗️ Kiến Trúc Và Design Patterns

## Tổng Quan Kiến Trúc

```
PrestaShop Demo Site
└── Main Page (demo.prestashop.com)
    └── <iframe id="framelive">  ← STOREFRONT CHẠY ĐÂY!
        ├── Product Listings
        ├── Product Details
        ├── Shopping Cart
        └── Checkout Flow
```

**⚠️ KEY INSIGHT:** Toàn bộ storefront chạy trong iframe `#framelive`. Đây là điểm khác biệt quan trọng nhất!

## Iframe Handling Patterns

### Selenium Python - Explicit Context Switch

```python
# Phải switch context trước khi interact
iframe = wait.until(EC.presence_of_element_located((By.ID, "framelive")))
driver.switch_to.frame(iframe)

# Bây giờ tất cả interactions ở trong iframe
element = driver.find_element(By.CSS_SELECTOR, ".product")
element.click()

# Để quay lại main page:
driver.switch_to.default_content()
```

### Playwright TypeScript - frameLocator API

```typescript
// Tạo frame locator (không switch context)
const frameLocator = page.frameLocator('#framelive');

// Tất cả interactions sử dụng frameLocator
const product = frameLocator.locator('.product');
await product.click();

// Main page context vẫn giữ nguyên!
```

**So Sánh:**
- **Selenium:** Phải switch context → dễ quên → bugs
- **Playwright:** Frame locator → clean hơn → ít bugs

## Element Interaction Patterns

### 1. Robust Click Pattern

**Problem:** Một số elements không click được với `.click()` standard

**Solution - Selenium:**
```python
try:
    element.click()
except:
    # Fallback: JavaScript executor
    driver.execute_script("arguments[0].click();", element)
```

**Solution - Playwright:**
```typescript
// Auto-retry built-in, ít cần fallback hơn
await element.click();

// Nếu cần force:
await element.click({ force: true });
```

### 2. Optional Elements Pattern

**Problem:** Một số fields (privacy checkbox, social title) không phải lúc nào cũng có

**Solution - Try-Catch Pattern:**

```python
# Selenium
try:
    privacy_checkbox = driver.find_element(By.NAME, "psgdpr")
    if not privacy_checkbox.is_selected():
        driver.execute_script("arguments[0].click();", privacy_checkbox)
except:
    print("   ℹ Privacy checkbox not found")
```

```typescript
// Playwright
try {
  const privacyCheckbox = frameLocator.locator('input[name="psgdpr"]');
  await privacyCheckbox.check({ timeout: 3000 });
} catch {
  console.log('   ℹ Privacy checkbox not found');
}
```

### 3. Wait Strategy Differences

| Aspect | Selenium | Playwright |
|--------|----------|------------|
| **Default** | No wait (immediate fail) | Auto-wait (retry ~30s) |
| **Explicit Wait** | WebDriverWait + EC required | `.waitFor()` available |
| **AJAX Transitions** | `time.sleep()` needed | Minimal `waitForTimeout()` |
| **Recommendation** | Always use explicit waits | Trust auto-wait, add waits for AJAX only |

**Selenium Example:**
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 20)
element = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-primary"))
)
time.sleep(2)  # Wait for AJAX
```

**Playwright Example:**
```typescript
// Auto-wait built-in
const element = frameLocator.locator('.btn-primary');
await element.click();  // Automatically waits for clickable

// AJAX transitions
await page.waitForTimeout(2000);
```

## Selector Strategy

**Ưu tiên từ cao → thấp:**

1. **`name` attribute** (forms)
   ```html
   <input name="firstname"> → name="firstname"
   ```

2. **`id` attribute** (unique elements)
   ```html
   <div id="payment-option-1"> → #payment-option-1
   ```

3. **`data-*` attributes** (actions)
   ```html
   <button data-button-action="add-to-cart"> → [data-button-action='add-to-cart']
   ```

4. **CSS classes** (structural)
   ```html
   <article class="product"> → .product
   ```

**❌ TRÁNH:**
- XPath (khó maintain, slow)
- Text-based selectors (i18n issues)
- Deep nested selectors (brittle)

## Test Data Pattern

```python
# Constants ở đầu file
FIRST_NAME = "John"
LAST_NAME = "Doe"
EMAIL = "john.doe.{framework}@automation.com"  # Unique per framework
ADDRESS = "123 Test Street"
POSTCODE = "10001"
CITY = "New York"
```

**Tại sao unique email per framework?**
- Tránh conflicts nếu chạy parallel
- Dễ debug: biết test nào generate data

## Error Handling Pattern

### Selenium - Screenshot + Cleanup

```python
try:
    # Test logic
    test_guest_checkout_e2e()
except Exception as e:
    print(f"❌ Test failed: {str(e)}")
    driver.save_screenshot("selenium_failure.png")
    raise
finally:
    driver.quit()  # Always cleanup
```

### Playwright - Built-in Reporter

```typescript
// playwright.config.ts
{
  screenshot: 'only-on-failure',
  video: 'retain-on-failure',
  trace: 'on-first-retry',
}

// Test auto-captures artifacts on fail!
```

## Console Logging Pattern

**Format chuẩn (giống nhau cả 2 frameworks):**

```
📍 Step X: [Action description]...
   ✓ [Success message]
   ⚠ [Warning - optional element]
   ℹ [Info message]
```

**Why consistent?**
- Dễ đọc logs khi compare 2 frameworks
- Visual debugging nhanh hơn
- Professional output

## Cross-Framework Test Parity

**Rule:** Khi sửa 1 test, phải sửa cả 2!

| Aspect | Must Match |
|--------|------------|
| Test steps | ✅ Same numbering (1-16) |
| Test data | ✅ Same values |
| Console output | ✅ Same format |
| Error handling | ✅ Same patterns |
| Assertions | ✅ Same logic |

**Ví dụ:**
```python
# Selenium - Step 5
print("📍 Step 5: Adding product to cart...")
add_to_cart_btn.click()
print("   ✓ Product added to cart")
```

```typescript
// Playwright - Step 5
console.log('📍 Step 5: Adding product to cart...');
await addToCartBtn.click();
console.log('   ✓ Product added to cart');
```

## Known Quirks & Workarounds

### 1. PrestaShop Demo Instability
- **Issue:** Demo site reset periodically
- **Impact:** Random failures
- **Mitigation:**
  - Selenium: 20s timeout
  - Playwright: `retries: 2` in config
  - Screenshot on failure

### 2. Flaky Checkboxes
- **Issue:** Standard click() fails
- **Solution:** JavaScript executor (Selenium) hoặc `.check()` (Playwright)

```python
# Selenium - reliable checkbox click
driver.execute_script("arguments[0].click();", checkbox)
```

```typescript
// Playwright - built-in robust check
await checkbox.check();
```

### 3. AJAX Page Transitions
- **Issue:** No full page reload → timing issues
- **Solution:** Explicit sleeps sau major actions

```python
# After clicking "Add to Cart"
time.sleep(2)  # Wait for modal animation
```

## Testing Philosophy

### Why Dual-Framework?

1. **Educational:** Compare modern (Playwright) vs traditional (Selenium)
2. **Flexibility:** Teams có thể choose based on needs
3. **Validation:** Same test = same results (ideal)
4. **Learning:** Best practices từ cả 2 worlds

### When to Use Which?

**Selenium:**
- ✅ Multi-language support needed (Java, C#, Ruby, etc.)
- ✅ Large existing codebase
- ✅ Team đã familiar với Selenium
- ✅ Cross-browser support across multiple vendors

**Playwright:**
- ✅ Modern web apps (SPAs, PWAs)
- ✅ Starting new project
- ✅ Need auto-wait and retry
- ✅ Want built-in debugging tools (trace viewer, inspector)
- ✅ TypeScript/JavaScript team

## Design Decisions

### Why Not Page Object Model?

**Current:** Direct interaction trong test file

**Reason:**
- Demo purpose - dễ hiểu hơn cho learners
- Single test case - không cần abstraction yet
- Rõ ràng: thấy toàn bộ flow trong 1 file

**Future:** Nếu scale lên nhiều test cases → nên refactor sang POM

### Why 16 Steps?

**Lý do:**
- Cover toàn bộ checkout flow
- Mỗi step = 1 user action or verification
- Dễ debug: biết chính xác step nào fail
- Consistent với test case documentation (IEEE 29119)

### Why CLI Script?

**`run-tests.sh` benefits:**
- One-command setup và execution
- Auto-install dependencies
- Colored output cho UX tốt hơn
- Summary report comparison
- CI/CD ready

## Performance Considerations

- **Sequential vs Parallel:** Run sequential (demo throttles)
- **Average Duration:** 35-50 seconds per test
- **Bottleneck:** Network (demo site)
- **Optimization:** Không nên optimize premature - test đã fast enough

## Maintenance Guidelines

1. **Quarterly Review:** Check selectors sau PrestaShop updates
2. **Monitor Demo:** Track uptime và SSL cert expiry
3. **Update Dependencies:** Selenium, Playwright versions
4. **Document Failures:** Add to Known Issues section
5. **Cross-Framework Sync:** Luôn update cả 2 tests

---

**💡 Key Takeaway:** Kiến trúc đơn giản nhưng deliberate. Mỗi pattern được chọn vì lý do cụ thể, không phải "best practice" theoretical mà là practical solutions cho real problems.
