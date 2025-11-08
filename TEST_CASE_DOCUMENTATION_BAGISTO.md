# Test Case Documentation - Bagisto Commerce (IEEE 29119)

## System Under Test

**Platform:** Bagisto Commerce Demo  
**URL:** https://commerce.bagisto.com/  
**Technology:** Laravel-based E-commerce  
**Test Scope:** Shopping Cart State Machine & Checkout Flow

---

## Test Suite Overview

This test suite validates shopping cart behavior through various state transitions:

```
EMPTY → ADD_ITEM → CART_ACTIVE → MODIFY → CHECKOUT → ORDER_PLACED → EMPTY
         ↓           ↓            ↓
         └─ BROWSE ─┘            └─ REMOVE_ALL → EMPTY
```

### Test Cases

1. **TC-CART-001:** Empty Cart Verification
2. **TC-CART-002:** Add Single Product to Cart
3. **TC-CART-003:** Modify Cart Quantity
4. **TC-CART-004:** Remove Product from Cart
5. **TC-CART-005:** Cart Persistence After Navigation
6. **TC-CHECKOUT-001:** Guest Checkout Complete Flow
7. **TC-CHECKOUT-002:** Cart State After Order Completion

---

## TC-CART-001: Empty Cart Verification

**Test ID:** TC-CART-001  
**Priority:** High  
**Type:** Functional - State Verification  
**Automation:** Selenium + Playwright

### Objective

Verify that a new user session begins with an empty shopping cart.

### Preconditions

- Clean browser session (no cookies)
- Access to https://commerce.bagisto.com/

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Navigate to Bagisto Commerce | Homepage loads successfully |
| 2 | Locate cart icon/counter | Cart counter shows 0 or empty |
| 3 | Click on cart icon | Empty cart message displayed |

### Expected Results

- Cart count = 0
- Message: "Your cart is empty" or similar
- No products listed in cart

### Test Data

N/A (Empty state verification)

---

## TC-CART-002: Add Single Product to Cart

**Test ID:** TC-CART-002  
**Priority:** Critical  
**Type:** Functional - Cart Update  
**Automation:** Selenium + Playwright

### Objective

Verify that adding a product updates cart count and reflects in cart view.

### Preconditions

- Cart is empty (TC-CART-001 passed)
- Products available on homepage/catalog

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Navigate to homepage | Products displayed |
| 2 | Locate first available product | Product card visible |
| 3 | Click "Add to Cart" button | Cart counter updates to 1 |
| 4 | Open cart view | Product appears in cart |
| 5 | Verify product details | Name, price, quantity=1 shown |

### Expected Results

- Cart count increments from 0 to 1
- Product appears in mini-cart dropdown
- Product details match selected item
- Subtotal = product price × 1

### Test Data

| Field | Value |
|-------|-------|
| Product | First available product on homepage |
| Quantity | 1 (default) |

---

## TC-CART-003: Modify Cart Quantity

**Test ID:** TC-CART-003  
**Priority:** High  
**Type:** Functional - Quantity Update  
**Automation:** Selenium + Playwright

### Objective

Verify that cart subtotal updates correctly when quantity is modified.

### Preconditions

- One product already in cart (TC-CART-002 passed)
- Cart view accessible

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Open cart page | Cart with 1 item displayed |
| 2 | Locate quantity input field | Input shows current qty (1) |
| 3 | Change quantity to 3 | Input updates to 3 |
| 4 | Click update/apply button | Cart recalculates |
| 5 | Verify subtotal | Subtotal = price × 3 |
| 6 | Verify cart counter | Counter shows 3 items |

### Expected Results

- Quantity field accepts numeric input
- Subtotal updates: `new_subtotal = unit_price × 3`
- Cart counter updates to 3
- No errors displayed

### Test Data

| Field | Before | After |
|-------|--------|-------|
| Quantity | 1 | 3 |

---

## TC-CART-004: Remove Product from Cart

**Test ID:** TC-CART-004  
**Priority:** High  
**Type:** Functional - Cart Reset  
**Automation:** Selenium + Playwright

### Objective

Verify that removing all items returns cart to empty state.

### Preconditions

- Product(s) in cart (TC-CART-002 or TC-CART-003)

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Open cart page | Cart with items displayed |
| 2 | Click remove/delete icon | Confirmation prompt (may appear) |
| 3 | Confirm removal | Product removed from cart |
| 4 | Verify cart state | Empty cart message shown |
| 5 | Check cart counter | Counter shows 0 |

### Expected Results

- Product removed successfully
- Cart returns to empty state
- Message: "Your cart is empty"
- Cart counter = 0
- Subtotal = 0 or hidden

---

## TC-CART-005: Cart Persistence After Navigation

**Test ID:** TC-CART-005  
**Priority:** Medium  
**Type:** Functional - Session Persistence  
**Automation:** Selenium + Playwright

### Objective

Verify cart contents persist when navigating between pages.

### Preconditions

- Product added to cart (TC-CART-002)

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Add product to cart | Cart count = 1 |
| 2 | Navigate to "About" or category page | Navigation successful |
| 3 | Check cart counter | Counter still shows 1 |
| 4 | Return to homepage | Homepage loads |
| 5 | Open cart view | Product still in cart |

### Expected Results

- Cart data persists across page navigation
- Cart count unchanged
- Product details intact
- Session cookie maintains cart state

---

## TC-CHECKOUT-001: Guest Checkout Complete Flow

**Test ID:** TC-CHECKOUT-001  
**Priority:** Critical  
**Type:** End-to-End - Checkout Process  
**Automation:** Selenium + Playwright

### Objective

Verify guest user can complete checkout from cart to order confirmation.

### Preconditions

- Product(s) in cart
- Guest checkout enabled

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Open cart page | Cart with items shown |
| 2 | Click "Proceed to Checkout" | Checkout page loads |
| 3 | Fill billing address | Form accepts input |
| 4 | Enter email | Valid email accepted |
| 5 | Enter first name | "John" |
| 6 | Enter last name | "Doe" |
| 7 | Enter address | "123 Test Street" |
| 8 | Enter city | "New York" |
| 9 | Enter postal code | "10001" |
| 10 | Select country | "United States" |
| 11 | Enter phone | "5551234567" |
| 12 | Select shipping method | Method selected |
| 13 | Select payment method | "Cash on Delivery" or available |
| 14 | Click "Place Order" | Order submitted |
| 15 | Verify confirmation page | Order number displayed |

### Expected Results

- All form fields accept valid input
- Shipping method selectable
- Payment method selectable
- Order confirmation page displays:
  - Order number
  - Order summary
  - Success message
  - Order total matches cart

### Test Data

| Field | Value |
|-------|-------|
| Email | john.doe.bagisto@test.com |
| First Name | John |
| Last Name | Doe |
| Address | 123 Test Street |
| City | New York |
| Postal Code | 10001 |
| Country | United States |
| Phone | 5551234567 |

---

## TC-CHECKOUT-002: Cart State After Order Completion

**Test ID:** TC-CHECKOUT-002  
**Priority:** High  
**Type:** Functional - Post-Checkout State  
**Automation:** Selenium + Playwright

### Objective

Verify cart resets to empty state after successful order placement.

### Preconditions

- Order completed successfully (TC-CHECKOUT-001)

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | After order confirmation | Confirmation page displayed |
| 2 | Check cart counter | Counter shows 0 |
| 3 | Navigate to cart page | Empty cart message shown |
| 4 | Verify order in history (if logged in) | Order appears in account |

### Expected Results

- Cart counter = 0
- Cart is empty
- Previous order not in cart
- New shopping session can begin

---

## Known Limitations & Test Environment Notes

### Bagisto Commerce Specifics

1. **No Iframe:** Unlike PrestaShop, Bagisto renders directly (no iframe switching needed)
2. **Guest Checkout:** May require account creation depending on configuration
3. **Dynamic Selectors:** Uses Vue.js components, selectors may change
4. **Payment Methods:** Demo may have limited payment options
5. **Stock Management:** Products may go out of stock in demo

### Selector Strategy

**Priority:**
1. `data-*` attributes (if available)
2. `id` attributes
3. Stable CSS classes (avoid dynamic Vue classes)
4. ARIA labels
5. Text content (last resort)

### Test Data Constraints

- Email must be unique per test run
- Phone format varies by country
- Postal code validation by country
- Real payment gateway not tested (demo limitation)

---

## Test Execution Notes

### Selenium Python

```python
# Expected patterns
driver.get("https://commerce.bagisto.com/")
cart_icon = driver.find_element(By.CSS_SELECTOR, ".cart-icon")
add_to_cart = driver.find_element(By.CSS_SELECTOR, "[aria-label='Add to cart']")
```

### Playwright TypeScript

```typescript
// Expected patterns
await page.goto('https://commerce.bagisto.com/');
const cartIcon = page.locator('.cart-icon');
const addToCart = page.locator('[aria-label="Add to cart"]');
```

### Wait Strategies

- **Page Load:** Wait for network idle
- **AJAX:** Wait for cart counter update
- **Checkout:** Wait for form validation messages
- **Confirmation:** Wait for order number element

---

## Success Criteria

**All test cases pass when:**

1. Cart state transitions correctly through all phases
2. Cart count updates accurately
3. Cart persists across navigation
4. Checkout flow completes without errors
5. Order confirmation displays
6. Cart resets after order placement

**Test Coverage:**

- Empty state ✓
- Add product ✓
- Modify quantity ✓
- Remove product ✓
- Persistence ✓
- Checkout ✓
- Post-order reset ✓

---

**Last Updated:** 2025-11-08  
**Test Design:** IEEE 29119 Compliant  
**Automation Framework:** Selenium 4.15+ / Playwright 1.40+
