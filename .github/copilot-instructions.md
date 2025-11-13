# Bagisto Commerce E2E Test Suite - AI Coding Agent Instructions

## Project Overview

Dual-framework E2E test automation suite targeting Bagisto Commerce storefront. Implements **20 comprehensive checkout scenarios** in Playwright TypeScript covering complete e-commerce workflows from cart to payment completion.

**Target System:** https://commerce.bagisto.com/ (Laravel + Vue.js e-commerce platform)  
**Test Coverage:** 20 scenarios including happy paths, edge cases, digital goods (e-books), concurrent orders, cancel/reorder flows  
**Architecture:** Page Object Model with robust error handling and demo limitation awareness

**Test Files Structure:**
- `bagisto-s1-single-checkout.spec.ts` through `bagisto-s17-cancel-order.spec.ts` - Full scenario tests (S1-S17)
- `bagisto-step-b1a.spec.ts` through `bagisto-step-b1c.spec.ts` - Cart edge case tests (B1a-B1c)
- `pages/StorePage.ts` - Page Object with reusable methods (login, addFirstProductFromHome, goCheckout, etc.)
- `pages/AdminPage.ts` - Admin operations (not frequently used)

**NPM Scripts Available:**
```bash
npm run test:bagisto:s1:headed   # S1 - Single product checkout
npm run test:bagisto:s14:headed  # S14 - Digital goods (e-books)
npm run test:bagisto:s17:headed  # S17 - Cancel & reorder
# See package.json for all 20+ test scripts
```

## Critical Test Architecture

### Bagisto Commerce - Direct DOM Interaction

**NO IFRAME HANDLING REQUIRED** - Unlike PrestaShop, Bagisto renders storefront directly.

**Key Difference from PrestaShop:**
- No `driver.switch_to.frame()` needed
- No `page.frameLocator()` needed
- Standard DOM selectors work immediately

## Critical Developer Workflows

### Playwright TypeScript (`playwright_typescript/`)

```bash
cd playwright_typescript
npm install
npx playwright install chromium
sudo npx playwright install-deps chromium  # Install system dependencies

# Run tests using npm scripts (PREFERRED - full output)
npm run test:bagisto:s1:headed  # S1 - Single checkout
npm run test:bagisto:s2:headed  # S2 - Coupon checkout
npm run test:bagisto:s3:headed  # S3 - Payment methods

# Or run directly with Playwright CLI
npm test tests/bagisto-s1-single-checkout.spec.ts -- --headed

# Run all tests in headed mode
npm test -- --headed

# View last test report
npx playwright show-report
```

**Important:** 
- `playwright.config.ts` includes `ignoreHTTPSErrors: true` for demo sites
- Loads environment variables from `.env`
- **Browser state cleared between tests:** `storageState: undefined` ensures clean cookies/cache
- **Test timeout:** 120 seconds (2 minutes) for full checkout flow

### Selenium Python (`selenium_python/`)

```bash
cd selenium_python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests using test runner script (PREFERRED)
./run-tests.sh s1 headed      # S1 - Single checkout (browser visible)
./run-tests.sh s2 headless    # S2 - Coupon (background)

# Or run directly with pytest
pytest tests/test_bagisto_s1_single_checkout.py -v -s
HEADLESS=false pytest tests/ -v -s  # All tests headed mode
```

**Important:** 
- **ALWAYS activate venv** before running tests (Ubuntu 24.04+ PEP 668 requirement)
- **Selenium 4.38.0+** required (ChromeDriver version mismatch fix)
- Dependencies: `selenium==4.38.0`, `webdriver-manager==4.0.2`, `pytest==7.4.3`

## Project-Specific Conventions

### CRITICAL: Selenium Python - JavaScript Click Pattern (ChromeDriver Bug Workaround)

**Problem:** ChromeDriver 142.0.7444.162 + Chrome 142.0.7444.134 version mismatch causes `element.click()` to crash with `ProtocolError`.

**Solution - ALWAYS use JavaScript click for product links and critical buttons:**

```python
# ❌ WRONG - Causes ProtocolError/RemoteDisconnected
first_product.click()

# ✅ CORRECT - JavaScript click bypasses ChromeDriver bug
self.driver.execute_script("arguments[0].click();", first_product)
```

**Where to apply (Selenium Python only):**
- Product link clicks in `add_first_product_from_home()`
- Order detail link clicks in test files
- Any element click that causes connection crash

**Files affected:**
- `pages/store_page.py` (line ~131) - Product link click
- `tests/test_bagisto_s1_single_checkout.py` (line ~150) - Order link click
- Apply to S2-S17 tests as needed

**Root cause:** Patch version mismatch in Chrome/ChromeDriver (134 vs 162). Selenium 4.38.0 improves compatibility but JavaScript click is still required.

### CRITICAL: Selenium Python - Price Capture Pattern

**Problem:** XPath selectors with `[.//text()[contains(., 'Subtotal')]]` don't work due to whitespace in text nodes.

**Solution - Iterate through price rows and check text content:**

```python
# ✅ CORRECT - Find all flex rows, check text, get last <p>
price_rows = driver.find_elements(
    By.XPATH,
    "//div[contains(@class, 'flex') and contains(@class, 'justify-between')]"
)

for row in price_rows:
    row_text = row.text
    
    if 'Subtotal' in row_text:
        price_elem = row.find_elements(By.TAG_NAME, 'p')[-1]
        checkout_subtotal = price_elem.text.strip()
    
    elif 'Grand Total' in row_text:
        price_elem = row.find_elements(By.TAG_NAME, 'p')[-1]
        checkout_grand_total = price_elem.text.strip()
```

**Why:** Bagisto HTML has text nodes with leading/trailing spaces (` Subtotal `, ` Grand Total `). Python's `'Subtotal' in row_text` handles this better than XPath text predicates.

**File:** `tests/test_bagisto_s1_single_checkout.py` Step 6 (price capture before order placement)

### 1. CRITICAL: Bagisto Add-to-Cart Flow

**Problem:** Bagisto requires 5+ seconds for AJAX cart update after clicking "Add To Cart"

**Solution - Always wait and verify in cart page:**
```typescript
await addBtn.click();

// CRITICAL: Wait 5 seconds for AJAX to complete
await page.waitForTimeout(5000);

// Navigate to cart page to verify
await page.goto(baseUrl + '/checkout/cart', { 
    waitUntil: 'networkidle',  // Wait for all AJAX requests
    timeout: 20000 
});

// Count actual items by checking quantity inputs
const qtyInputs = page.locator('input[type="hidden"][name="quantity"]');
const itemCount = await qtyInputs.count();

if (itemCount > 0) {
    console.log(`  ✓ Cart has ${itemCount} item(s)`);
    return; // Success!
}
```

**DON'T rely on:**
- Cart badge counter (may not update)
- Success message toast (may disappear or not appear)
- Cart icon in header (unreliable)

**DO verify by:**
- Opening cart page and counting `input[type="hidden"][name="quantity"]` elements
- Each item has exactly ONE quantity input

### 2. Configurable Products - Must Skip or Select Options

**Problem:** Bundle/configurable products (e.g., "All-in-One Outfit Set") have options that MUST be selected before adding to cart.

**Solution - Skip products with options:**
```typescript
await product.click();
await page.waitForLoadState('networkidle');

// Check if product has configurable options
const hasOptions = await page.locator('text=/select.*:|choose.*:|pick.*/i')
    .first()
    .isVisible({ timeout: 2000 })
    .catch(() => false);

if (hasOptions) {
    console.log(`  ⚠ Product has configurable options, skipping...`);
    continue; // Try next category
}

// Safe to add simple products
await addBtn.click();
```

### 2.5. Digital Goods (E-Books) - Special Cart Handling

**Problem:** E-books use checkboxes instead of quantity inputs AND require download link selection before adding to cart.

**Cart Verification for E-books:**
```typescript
// Physical products: input[type="hidden"][name="quantity"]
// E-books: input[type="checkbox"][id^="item_"]
const physicalProductInputs = page.locator('input[type="hidden"][name="quantity"]');
const ebookCheckboxes = page.locator('input[type="checkbox"][id^="item_"]');

const physicalCount = await physicalProductInputs.count();
const ebookCount = await ebookCheckboxes.count();
const totalCount = physicalCount + ebookCount;

console.log(`Cart has ${totalCount} item(s) (${physicalCount} physical, ${ebookCount} e-book)`);
```

**E-book Download Link Selection (REQUIRED before Add To Cart):**
```typescript
// Must click download link checkbox - error "The Links field is required" if not selected
const downloadCheckboxLabel = page.locator('label[for]').filter({ hasText: /Champions Mindset.*\$/i }).first();

if (await downloadCheckboxLabel.isVisible({ timeout: 3000 })) {
  await downloadCheckboxLabel.click();
  console.log('✓ Download link checkbox selected');
} else {
  // Cannot proceed without checkbox
  return;
}
```

**E-book Checkout Flow (NO SHIPPING):**
```typescript
// Check if Proceed button exists (address form present)
const proceedBtn = page.getByRole('button', { name: 'Proceed' });
const hasProceedBtn = await proceedBtn.isVisible({ timeout: 3000 });

if (hasProceedBtn) {
  // Physical product - needs address + shipping
  await store.fillShippingAddressMinimal();
  await freeShippingLabel.click(); // Select shipping method
} else {
  // E-book - no shipping, go straight to payment
  console.log('No shipping needed for e-book');
}

// Select payment method (both product types)
await codLabel.click();
```

### 3. Bagisto Checkout Flow - Multi-Step with Hidden Inputs

**Flow:**
1. Fill address → Click "**Proceed**" button
2. **Wait 2 seconds** for shipping/payment options to load
3. **Click label** (not input) for shipping method - inputs are `class="peer hidden"`
4. **Click label** for payment method
5. Click "Place Order" button

**CRITICAL - Click Labels, Not Hidden Inputs:**
```typescript
// ❌ WRONG - Inputs are hidden
await page.locator('input[id="free_free"]').check();

// ✅ CORRECT - Click the visible label
const freeShippingLabel = page.locator('label[for="free_free"]').last();
await freeShippingLabel.click();

// Same for payment
const codLabel = page.locator('label[for="cashondelivery"]').last();
await codLabel.click();
```

**HTML Structure:**
```html
<!-- Input is hidden -->
<input type="radio" id="free_free" class="peer hidden" />

<!-- Must click THIS label -->
<label for="free_free" class="block cursor-pointer...">
    <p>$0.00</p>
    <p>Free Shipping</p>
</label>
```

### 4. Order Verification - Use Success Page URL and Order Link

**Problem:** After clicking "Place Order", we don't know if order was created successfully.

**Solution - Wait for success page and extract order ID:**
```typescript
// ❌ WRONG - Wait blindly for 3 seconds
await page.waitForTimeout(3000);

// ✅ CORRECT - Wait for redirect to success page
await page.waitForURL('**/checkout/onepage/success', { 
    timeout: 30000,
    waitUntil: 'networkidle' 
});

// Extract order ID from: <a class="text-blue-700" href=".../orders/view/67">67</a>
const orderLink = page.locator('p.text-xl a.text-blue-700[href*="/customer/account/orders/view/"]').first();

if (await orderLink.isVisible({ timeout: 5000 })) {
    const orderIdText = await orderLink.textContent(); // "67"
    const orderHref = await orderLink.getAttribute('href'); // ".../orders/view/67"
    
    // Click link to verify order details
    await orderLink.click();
    await page.waitForLoadState('networkidle');
}
```

**Success Page Structure:**
```html
<p class="text-xl max-md:text-sm">
    Your order id is #<a class="text-blue-700" 
                         href="https://commerce.bagisto.com/customer/account/orders/view/67">67</a>
</p>
```

### 4.5. Price Verification - Compare Checkout vs Order Detail

**Purpose:** Verify that prices displayed during checkout match the final order.

**Critical Pattern (proven in S1, S2, S3):**

```typescript
// STEP 1: Capture checkout summary BEFORE placing order
console.log('Capturing checkout summary before placing order...');
await page.waitForTimeout(2000); // Wait for totals to update

const checkoutSubtotal = await page
  .locator('div.flex.justify-between:has-text("Subtotal")')
  .locator('p').last()
  .textContent();

const checkoutDelivery = await page
  .locator('div.flex.justify-between:has-text("Delivery Charges")')
  .locator('p').last()
  .textContent();

const checkoutGrandTotal = await page
  .locator('div.flex.justify-between:has-text("Grand Total")')
  .locator('p').last()
  .textContent();

console.log(`Checkout Summary:`);
console.log(`  Subtotal: ${checkoutSubtotal?.trim()}`);
console.log(`  Delivery: ${checkoutDelivery?.trim()}`);
console.log(`  Grand Total: ${checkoutGrandTotal?.trim()}`);

// STEP 2: Place order and navigate to order detail page
await placeOrderBtn.click();
await page.waitForURL('**/checkout/onepage/success', { timeout: 30000 });

const orderLink = page.locator('p.text-xl a.text-blue-700[href*="/orders/view/"]').first();
await orderLink.click();
await page.waitForLoadState('networkidle');

// STEP 3: CRITICAL - Wait 3000ms for order detail page to fully render
await page.waitForTimeout(3000);

// STEP 4: Parse order detail summary
const gtRow = page.locator('div.flex.justify-between:has-text("Grand Total")').first();
const orderGrandTotal = await gtRow.locator('p').last().textContent();

const subtotalRow = page.locator('div.flex.justify-between:has-text("Subtotal")').first();
const orderSubtotal = await subtotalRow.locator('p').last().textContent();

console.log(`Order Detail Summary:`);
console.log(`  Subtotal: ${orderSubtotal?.trim()}`);
console.log(`  Grand Total: ${orderGrandTotal?.trim()}`);

// STEP 5: Compare
const checkoutGT = checkoutGrandTotal?.trim() || '';
const orderGT = orderGrandTotal?.trim() || '';

if (checkoutGT === orderGT) {
  console.log(`✓ Grand Total MATCHES: ${checkoutGT} = ${orderGT}`);
} else {
  console.log(`⚠ Grand Total MISMATCH: Checkout ${checkoutGT} ≠ Order ${orderGT}`);
}
```

**Key Points:**
- **Wait 3000ms** after navigating to order detail page (CRITICAL!)
- Use **specific row selectors**: `div.flex.justify-between:has-text("Grand Total")`
- Don't use "last price on page" - sidebar/related products interfere
- Capture checkout prices BEFORE placing order
- Always trim values before comparison

### 5. Cookie Consent Modal - Dismiss Early

**Problem:** Cookie consent modal can block clicks during checkout.

**Solution - Dismiss in login():**
```typescript
async login() {
    await page.goto(baseUrl + '/customer/login');
    
    // Dismiss cookie consent if present
    const acceptBtn = page.locator('button:has-text("Accept")').first();
    if (await acceptBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await acceptBtn.click();
        await page.waitForTimeout(500);
    }
    
    // Continue login...
}
```

### 5. Selector Strategy for Bagisto (Vue.js Application)

**Priority Order:**
1. **`data-*` attributes** - Most stable (if available)
2. **`aria-label` attributes** - Accessibility-first
3. **Stable CSS classes** - Avoid dynamic Vue classes like `.v-1a2b3c`
4. **Text content with `:has-text()`** - Last resort, case-insensitive

**Multiple Selector Fallbacks:**
```typescript
const cartCountSelectors = [
    '.cart-count',
    '[data-cart-count]',
    'button:has-text("Shopping Cart") + *'
];

for (const selector of cartCountSelectors) {
    const element = page.locator(selector).first();
    if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
        // Use this selector
        break;
    }
}
```

### 6. Order Verification in Order History

**Verify order after checkout:**
```typescript
await page.goto(baseUrl + '/customer/account/orders', { 
    waitUntil: 'networkidle' 
});

// Skip header row, get first data row
const orderRows = page.locator('.row.grid')
    .filter({ hasNot: page.locator('text=/Order ID|Order Date/i') });

const firstRow = orderRows.first();
const cellsText = await firstRow.locator('p').allTextContents();

// cellsText[0] = Order ID
// cellsText[1] = Date  
// cellsText[2] = Total ($150.00)
// cellsText[3] = Status (Completed, Pending, etc.)
```

### 7. Console Logging Pattern

**Format - Clear Step-by-Step:**
```
Step 1 (B1): Logging in to save order...
  ✓ Logged in successfully
Step 2 (B2): Adding single product to cart...
  → Waiting for cart to update...
  → Checking cart...
  → Found 4 items in cart
  ✓ Cart has 4 item(s)
Step 6 (B5): Choosing payment method and placing order...
  → Selecting shipping method...
    Clicking Free Shipping label...
  → Selecting payment method...
    Clicking Cash On Delivery label...
  → Clicking Place Order...
    Found button with selector: button:has-text("Place Order")
```

**Symbols:**
- `✓` - Success/confirmation
- `⚠` - Warning/limitation detected
- `→` - Action in progress
- `✗` - Failure/retry

### 8. Test Case Structure - 20 Comprehensive Scenarios

**File Naming Convention:**
- `bagisto-step-b1a.spec.ts` - Cart edge cases (empty cart, remove all, wishlist)
- `bagisto-s1-single-checkout.spec.ts` - Full scenario tests (S1-S17)
- Each file is self-contained with clear console logging

**Test Pattern:**
```typescript
test('S1 – Add product, checkout, verify order & empty cart', async ({ page }) => {
  console.log('Step 1 (B1): Logging in...');
  const store = new StorePage(page);
  await store.login();  // Auto-dismisses cookie consent
  
  console.log('Step 2 (B2): Adding product to cart...');
  await store.addFirstProductFromHome();  // Waits 5s, navigates to cart, verifies
  
  console.log('Step 3 (B3): Proceeding to checkout...');
  await store.goCheckout();
  
  console.log('Step 4 (B4): Filling shipping address...');
  await store.fillShippingAddressMinimal();  // Auto-clicks "Proceed"
  
  console.log('Step 5 (B5): Placing order...');
  await store.choosePaymentAndPlace(false);  // Clicks labels, not inputs
  
  // Verify order in history
  const order = await store.getLatestOrder();
  console.log(`  Order ID: ${order.orderId}, Total: ${order.total}`);
});
```

### 9. Cancel & Reorder Flow (S17) - CRITICAL Navigation Handling

**Problem:** Cancel order with "Agree" button triggers page reload/navigation that causes timeout.

**Solution - Use `noWaitAfter: true` option:**
```typescript
// Step 1: Click Cancel link
await page.getByRole('link', { name: 'Cancel' }).click();

// Step 2: Click Agree button WITHOUT waiting for navigation
const agreeBtn = page.getByRole('button', { name: 'Agree', exact: true });
await agreeBtn.click({ noWaitAfter: true }); // CRITICAL!
await page.waitForTimeout(3000);

// Step 3: Reorder link may need page refresh to appear
let reorderLink = page.getByRole('link', { name: 'Reorder' });
if (!await reorderLink.isVisible({ timeout: 3000 })) {
  await page.reload({ waitUntil: 'networkidle' });
  reorderLink = page.getByRole('link', { name: 'Reorder' });
}
await reorderLink.click();

// Step 4: Reorder checkout - must select BOTH shipping AND payment
await store.fillShippingAddressMinimal(); // Fills address + clicks Proceed
await page.waitForTimeout(2000);

// CRITICAL: Physical products need shipping method selection
const freeShippingLabel = page.locator('label[for="free_free"]').last();
if (await freeShippingLabel.isVisible({ timeout: 3000 })) {
  await freeShippingLabel.click();
  await page.waitForTimeout(1000);
}

// Then select payment
const codLabel = page.locator('label[for="cashondelivery"]').last();
await codLabel.click({ force: true });
await page.waitForTimeout(2000);

// Place Order button should now be visible
await page.keyboard.press('End'); // Scroll to bottom
const placeOrderBtn = page.getByRole('button', { name: 'Place Order' });
await placeOrderBtn.click();
```

**Key Points:**
- `noWaitAfter: true` prevents timeout on navigation actions
- Reorder link may need page refresh after cancellation
- Physical products require shipping method selection (Free Shipping) before payment
- E-books skip shipping, go straight to payment

## Error Handling Requirements

### Playwright
- Configure in `playwright.config.ts`:
  ```typescript
  screenshot: 'only-on-failure',
  video: 'retain-on-failure',
  trace: 'on-first-retry',
  ```
- Built-in HTML report: `npx playwright show-report`

## Known Quirks & Workarounds

### Bagisto Demo Limitations
- **Cart Session Issues:** Demo has cart persistence problems
- **Admin Access:** Stock/price editing may not persist
- **Rate Limiting:** Multiple rapid requests may be throttled

**Mitigation:**
```typescript
// Soft assertions for demo limitations
if (itemCount === 0) {
  console.log('  ⚠ Cart empty (known demo limitation)');
  console.log('  ℹ Documenting expected production behavior...');
  return; // Skip rest gracefully
}
```

### Order History Pagination - CRITICAL Detection Pattern

**Problem:** Order history has **pagination (10 orders per page)**, so `count()` is unreliable for detecting new orders.

**❌ WRONG - Count always returns 10 even with new orders:**
```typescript
const orderRows = page.locator('.row.grid')
  .filter({ hasNot: page.locator('text=/Order ID|Order Date/i') });

const orderCount = await orderRows.count(); // Always 10 due to pagination!
const newOrders = orderCount - initialCount; // Always 0! ❌
```

**✅ CORRECT - Compare first order ID to detect new orders:**
```typescript
// Step 1: Capture initial first order ID
const orderRows = page.locator('.row.grid')
  .filter({ hasNot: page.locator('text=/Order ID|Order Date/i') });

let initialFirstOrderId = '';
if (await orderRows.count() > 0) {
  const firstOrderIdText = await orderRows.first().locator('p').first().textContent();
  initialFirstOrderId = firstOrderIdText?.trim() || '';
  console.log(`Initial first order: #${initialFirstOrderId}`);
}

// Step 2: After action, check if first order ID changed
await page.goto(baseUrl + '/customer/account/orders', { waitUntil: 'networkidle' });
await page.waitForTimeout(2000);

// Re-query after navigation (stale elements!)
const newOrderRows = page.locator('.row.grid')
  .filter({ hasNot: page.locator('text=/Order ID|Order Date/i') });

let currentFirstOrderId = '';
if (await newOrderRows.count() > 0) {
  const firstOrderIdText = await newOrderRows.first().locator('p').first().textContent();
  currentFirstOrderId = firstOrderIdText?.trim() || '';
}

// Step 3: Detect new order by ID change
if (currentFirstOrderId !== initialFirstOrderId && currentFirstOrderId !== '') {
  console.log(`✓ New order detected: #${currentFirstOrderId} (was #${initialFirstOrderId})`);
} else {
  console.log('No new order created');
}
```

**Key Points:**
- **Never reuse selectors** after page navigation (stale elements!)
- **Always re-query** `orderRows` after `page.goto()`
- **Compare IDs, not counts** when pagination exists
- Orders sorted by newest first, so **first row = latest order**

### Timeout Settings
- **Test timeout:** 120 seconds (full login → checkout flow)
- **Action timeout:** 15 seconds (clicks, fills, etc.)
- **Navigation timeout:** 30 seconds (page loads)
- **Cart update:** 5 seconds minimum after "Add To Cart"
- **Shipping/payment load:** 2 seconds after "Proceed" button
- **Order success page:** 30 seconds max for redirect

## Adding New Test Cases

1. **Create new test file**: `bagisto-sXX-description.spec.ts`
2. **Use Page Object Model** - call methods from StorePage/AdminPage
3. **Follow B1→B5 notation** (Browse, Select, Validate, Checkout, Complete)
4. **Add clear console logging** with step labels and status symbols
5. **Always run tests in headed mode** during development: `npm test -- --headed`

---

## Quick Reference

**Most Common Issues & Solutions:**

| Issue | Solution | File Reference |
|-------|----------|----------------|
| Cart not updating after Add To Cart | Wait 5s + navigate to cart page | Convention #1 |
| Place Order button not visible | Click shipping label FIRST, then payment label | Convention #3 |
| Timeout on "Agree" button | Use `click({ noWaitAfter: true })` | Convention #9 |
| E-book cart shows 0 items | Use checkbox selector `input[type="checkbox"][id^="item_"]` | Convention #2.5 |
| Price mismatch between checkout/order | Wait 3000ms after order page loads | Convention #4.5 |
| Cannot detect new order | Compare first order ID, not count | Order History Pagination |

**Test Execution Commands:**
```bash
# Run single test (headed mode - recommended for debugging)
npm run test:bagisto:s1:headed

# Run all tests (headless)
npm test

# View latest report
npx playwright show-report

# Debug specific test
npx playwright test tests/bagisto-s14-digital-goods.spec.ts --debug
```

**Primary Files:**
- Page Objects: `playwright_typescript/pages/StorePage.ts`, `AdminPage.ts`
- Tests: `playwright_typescript/tests/bagisto-s*.spec.ts` (20 scenarios)
- Config: `playwright_typescript/playwright.config.ts`
- Environment: `playwright_typescript/.env`

**Last Updated:** 2025-11-12 (Added S17 Cancel/Reorder flow, E-book handling, navigation timeout fixes, Selenium Python JavaScript click workaround)

---

## Selenium Python-Specific Quick Reference

**Most Common Selenium Issues & Solutions:**

| Issue | Selenium Solution | File Reference |
|-------|----------|----------------|
| ProtocolError on element.click() | Use `driver.execute_script("arguments[0].click();", element)` | `store_page.py` line 131 |
| Price capture returns empty strings | Loop through rows, check text with `in`, get last `<p>` | `test_bagisto_s1_single_checkout.py` Step 6 |
| Configurable products block all adds | Disable check: `has_required_options = False` | `store_page.py` line 152 |
| Cart verification (physical + e-book) | Count `input[name="quantity"]` + `input[id^="item_"]` | `store_page.py` line 180 |

**Selenium Test Execution:**
```bash
# ALWAYS activate venv first
cd selenium_python && source venv/bin/activate

# Run single test (headed mode - browser visible)
./run-tests.sh s1 headed

# Run in headless mode
./run-tests.sh s1 headless

# Direct pytest (with environment variable)
HEADLESS=false pytest tests/test_bagisto_s1_single_checkout.py -v -s
```

**‼️ IMPORTANT - MANDATORY HEADED MODE VERIFICATION ‼️**

**After completing ANY test development or bug fixes, you MUST:**
1. Run the test in **HEADED mode** (browser visible) for user verification
2. Use command: `./run-tests.sh sX headed` or `HEADLESS=false pytest tests/test_bagisto_sX_*.py -v -s`
3. **DO NOT** consider the work complete until user confirms they can see the browser executing
4. User needs to visually verify the test flow and catch any issues automation might miss

**Why headed mode is mandatory:**
- User can observe actual browser behavior
- Visual confirmation of each test step
- Catches UI issues that pass in headless but fail visually
- Ensures test matches real user experience

**Example workflow:**
```bash
# After fixing S2 test, ALWAYS run:
cd selenium_python && source venv/bin/activate
./run-tests.sh s2 headed  # User MUST see browser!

# Or with direct pytest:
HEADLESS=false pytest tests/test_bagisto_s2_multiple_coupon.py -v -s
```

**Key Selenium Patterns:**

1. **JavaScript Click (ChromeDriver bug):**
   ```python
   self.driver.execute_script("arguments[0].click();", element)
   ```

2. **Wait for AJAX cart update:**
   ```python
   add_btn.click()
   time.sleep(5)  # CRITICAL - cart AJAX takes 5+ seconds
   driver.get(f"{base_url}/checkout/cart")  # Navigate to verify
   ```

3. **Click labels for hidden inputs:**
   ```python
   # Shipping method
   free_shipping = driver.find_element(By.CSS_SELECTOR, 'label[for="free_free"]')
   free_shipping.click()
   
   # Payment method
   cod_label = driver.find_element(By.CSS_SELECTOR, 'label[for="cashondelivery"]')
   cod_label.click()
   ```

4. **Price capture with text checking:**
   ```python
   price_rows = driver.find_elements(By.XPATH, "//div[@class='flex justify-between']")
   for row in price_rows:
       if 'Grand Total' in row.text:
           price = row.find_elements(By.TAG_NAME, 'p')[-1].text.strip()
   ```

**Primary Selenium Files:**
- Page Object: `selenium_python/pages/store_page.py`
- Tests: `selenium_python/tests/test_bagisto_s*.py` (15 test files)
- Config: `selenium_python/conftest.py` (pytest fixtures)
- Environment: `selenium_python/.env`
- Bug fix summary: `selenium_python/S1_BUG_FIX_SUMMARY.md`

**Last Updated:** 2025-11-12 (Added S17 Cancel/Reorder flow, E-book handling, navigation timeout fixes)
