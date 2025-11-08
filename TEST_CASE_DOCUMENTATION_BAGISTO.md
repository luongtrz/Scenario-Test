# Test Case Documentation - Bagisto Commerce (IEEE 29119)

## System Under Test

**Platform:** Bagisto Commerce Demo  
**URL:** https://commerce.bagisto.com/  
**Technology:** Laravel-based E-commerce  
**Test Scope:** Shopping Cart State Machine & Checkout Flow

---

## Test Suite Overview

This test suite validates shopping cart behavior through various state transitions and edge cases:

```
EMPTY → ADD_ITEM → CART_ACTIVE → MODIFY → CHECKOUT → ORDER_PLACED → EMPTY
         ↓           ↓            ↓            ↓
         └─ BROWSE ─┘            └─ REMOVE ─┘  └─ ABANDONED (preserved)
                                 ↓
                          SAVE_FOR_LATER
                          OUT_OF_STOCK
                          PRICE_CHANGE
```

### Core Test Cases

1. **TC-CART-001:** Empty Cart Verification
2. **TC-CART-002:** Add Single Product to Cart
3. **TC-CART-003:** Modify Cart Quantity
4. **TC-CART-004:** Remove Product from Cart
5. **TC-CART-005:** Cart Persistence After Navigation
6. **TC-CHECKOUT-001:** Guest Checkout Complete Flow
7. **TC-CHECKOUT-002:** Cart State After Order Completion

### Extended Test Cases (Session & Edge Cases)

8. **TC-SESSION-001:** Cart Persistence After Browser Restart
9. **TC-SESSION-002:** Abandoned Checkout Cart Preservation
10. **TC-WISHLIST-001:** Save Item for Later
11. **TC-INVENTORY-001:** Out of Stock Product Handling
12. **TC-PRICE-001:** Price Change Notification

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

## TC-SESSION-001: Cart Persistence After Browser Restart

**Test ID:** TC-SESSION-001  
**Priority:** High  
**Type:** Functional - Session Management  
**Automation:** Manual + Selenium (with cookie storage)

### Objective

Verify that cart contents persist after browser is closed and reopened (simulating session preservation).

### Preconditions

- Product added to cart
- Browser supports cookies/localStorage

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Add product to cart | Cart count = 1 |
| 2 | Note session cookie/localStorage | Cart data stored |
| 3 | Close browser completely | Browser closed |
| 4 | Wait 1 minute | Simulate brief inactivity |
| 5 | Reopen browser | Browser starts fresh |
| 6 | Navigate to Bagisto | Homepage loads |
| 7 | Check cart counter | Cart still shows 1 item |
| 8 | Open cart view | Product still present |

### Expected Results

- Cart data persists via cookies/localStorage
- Session ID maintained or cart restored
- Product details unchanged
- User can continue shopping without re-adding items

### Test Data

N/A (Uses existing cart data)

### Notes

**Implementation:**
- Selenium: Save/restore cookies between sessions
- Playwright: context.storageState() for session persistence
- Verify localStorage keys: `bagisto_cart`, `session_id`, etc.

---

## TC-SESSION-002: Abandoned Checkout Cart Preservation

**Test ID:** TC-SESSION-002  
**Priority:** Medium  
**Type:** Functional - Abandoned Cart  
**Automation:** Selenium + Playwright

### Objective

Verify that cart remains incomplete (preserved) when user abandons checkout process.

### Preconditions

- Product in cart
- User at checkout page

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Add product to cart | Cart count = 1 |
| 2 | Proceed to checkout | Checkout page loads |
| 3 | Fill partial information (email only) | Email entered |
| 4 | Navigate away (homepage) | User leaves checkout |
| 5 | Wait 30 seconds | Simulate brief abandonment |
| 6 | Check cart counter | Cart still shows 1 item |
| 7 | Return to checkout | Checkout page reloads |
| 8 | Verify form state | Email may be pre-filled (depends on system) |

### Expected Results

- Cart NOT cleared when abandoning checkout
- Cart data preserved for continued shopping
- Incomplete order NOT created in system
- User can resume checkout later

### Test Data

| Field | Value |
|-------|-------|
| Email | abandoned.user@test.com |

### Notes

- Typical e-commerce platforms preserve cart for 24-72 hours
- Some systems send abandoned cart emails
- Demo environment may have shorter preservation time

---

## TC-WISHLIST-001: Save Item for Later

**Test ID:** TC-WISHLIST-001  
**Priority:** Low  
**Type:** Functional - Wishlist/Save for Later  
**Automation:** Selenium + Playwright (if feature exists)

### Objective

Verify user can move items from cart to "Save for Later" or wishlist.

### Preconditions

- Product in cart
- "Save for Later" feature available

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Add product to cart | Cart count = 1 |
| 2 | Open cart page | Cart displays product |
| 3 | Click "Save for Later" button | Button clickable |
| 4 | Verify cart updated | Cart count = 0 |
| 5 | Verify saved items section | Product appears in "Saved" list |
| 6 | Click "Move to Cart" | Product returns to cart |
| 7 | Verify cart restored | Cart count = 1 |

### Expected Results

- Product removed from active cart
- Product appears in saved/wishlist section
- User can restore item to cart later
- Cart subtotal excludes saved items

### Test Data

N/A

### Notes

**Feature Availability:**
- Bagisto may call this "Wishlist" instead of "Save for Later"
- Some platforms require login for this feature
- Guest users may have limited save functionality

**Automation Strategy:**
- Check if feature exists on site first
- If not present, mark test as SKIPPED
- Log feature availability for documentation

---

## TC-INVENTORY-001: Out of Stock Product Handling

**Test ID:** TC-INVENTORY-001  
**Priority:** High  
**Type:** Functional - Inventory Management  
**Automation:** Manual (requires stock manipulation) / API-assisted

### Objective

Verify system prevents checkout when product becomes out of stock after being added to cart.

### Preconditions

- Ability to change product stock (admin access or API)
- Product with low stock

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Identify product with stock = 2 | Product available |
| 2 | Add product to cart (qty=1) | Cart updated successfully |
| 3 | Simulate stock change to 0 (admin/API) | Product now out of stock |
| 4 | Return to cart page | Cart displays product |
| 5 | Attempt to proceed to checkout | System blocks checkout |
| 6 | Verify error message | "Product out of stock" shown |
| 7 | Verify product status in cart | Marked as unavailable |

### Expected Results

- System detects stock change
- Checkout button disabled or shows error
- Clear error message displayed
- User prompted to remove item or check alternatives
- Cart cannot be finalized with out-of-stock items

### Test Data

| Field | Value |
|-------|-------|
| Product | Test product with controllable stock |
| Initial Stock | 2 |
| Changed Stock | 0 |

### Notes

**Manual Steps Required:**
1. Access Bagisto admin: `https://commerce.bagisto.com/admin`
2. Navigate to product inventory
3. Update stock quantity
4. Or use API endpoint: `PUT /api/products/{id}/inventory`

**Automation Approach:**
- Use Bagisto Admin API for stock manipulation
- Requires admin credentials (not available in public demo)
- Alternative: Mock scenario in documentation only

---

## TC-PRICE-001: Price Change Notification

**Test ID:** TC-PRICE-001  
**Priority:** Medium  
**Type:** Functional - Price Management  
**Automation:** Manual (requires price manipulation) / API-assisted

### Objective

Verify system notifies user when product price changes after being added to cart.

### Preconditions

- Ability to change product price (admin access)
- Product in cart

### Test Steps

| Step | Action | Expected Result |
|------|--------|----------------|
| 1 | Add product to cart (price=$100) | Cart shows subtotal=$100 |
| 2 | Simulate price change to $120 (admin/API) | Price updated in catalog |
| 3 | Return to cart page | Cart refreshes |
| 4 | Verify cart subtotal | May show old price ($100) or new ($120) |
| 5 | Proceed to checkout | System validates prices |
| 6 | Check for price difference notification | "Price changed" message (if implemented) |
| 7 | Verify final order total | Uses current price ($120) |

### Expected Results

**Scenario A (Price Updated):**
- Cart automatically updates to new price
- Notification: "Product price has changed"
- User can review and confirm

**Scenario B (Price Locked):**
- Cart maintains original price temporarily
- Price synced at checkout validation
- Clear disclosure of price change

### Test Data

| Field | Initial | Changed |
|-------|---------|---------|
| Product Price | $100.00 | $120.00 |

### Notes

**Implementation Varies:**
- Some platforms lock price when added to cart
- Others update in real-time
- Best practice: Notify user before final payment

**Automation Limitations:**
- Requires admin access to demo (usually restricted)
- Alternative: Document expected behavior
- Future: Mock API responses for testing

---

## Test Execution Priority

### Critical Path (Run Always)

1. TC-CART-001 (Empty cart)
2. TC-CART-002 (Add product)
3. TC-CHECKOUT-001 (Complete checkout)
4. TC-CHECKOUT-002 (Cart reset)

### Standard Path (Regular CI/CD)

5. TC-CART-003 (Modify quantity)
6. TC-CART-004 (Remove product)
7. TC-CART-005 (Navigation persistence)
8. TC-SESSION-002 (Abandoned cart)

### Extended Path (Weekly/Release)

9. TC-SESSION-001 (Browser restart - requires cookie handling)
10. TC-WISHLIST-001 (Save for later - if feature exists)
11. TC-INVENTORY-001 (Out of stock - requires admin access)
12. TC-PRICE-001 (Price change - requires admin access)

---

## Success Criteria

**All test cases pass when:**

- Empty state ✓
- Add product ✓
- Modify quantity ✓
- Remove product ✓
- Persistence ✓
- Checkout ✓
- Post-order reset ✓
- Session preservation ✓
- Abandoned cart handling ✓
- Wishlist functionality ✓ (if available)
- Inventory validation ✓ (manual/API)
- Price change handling ✓ (manual/API)

**Test Coverage:**

- Core cart operations: 100%
- Session management: 100%
- Edge cases: 80% (limited by demo constraints)
- Admin-required tests: Documentation only

---

**Last Updated:** 2025-11-08  
**Test Design:** IEEE 29119 Compliant  
**Automation Framework:** Selenium 4.15+ / Playwright 1.40+
