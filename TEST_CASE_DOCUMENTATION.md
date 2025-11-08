# 📚 Test Case TC-E2E-001: Complete Documentation

## PHASE 1 — Test Design (Theory)

### Test Identification
- **ID:** TC-E2E-001
- **Name:** Guest Checkout - Happy Path (Single Product Purchase)
- **Type:** End-to-End Acceptance Test
- **Priority:** P1 (High)
- **IEEE/ISTQB Compliance:** ✅

---

### Test Basis
**Business Requirement:** Enable guest users to purchase products without account creation

**High-Level Flow:**
```
Browse → Select → Add to Cart → Checkout → Personal Info → 
Shipping → Payment → Confirm → Order Confirmation
```

**Preconditions:**
1. PrestaShop demo accessible at https://demo.prestashop.com/
2. Guest checkout enabled in system
3. Product inventory available
4. Browser: Chrome/Chromium latest
5. JavaScript enabled
6. Clean browser session (no cookies)

**Test Environment:**
- SUT: PrestaShop Demo (iframe-embedded storefront)
- URL: https://demo.prestashop.com/
- Architecture: Iframe (`#framelive`) contains storefront
- Payment: Mock payment methods (demo safe)

---

### Test Case Structure

#### Objective
Verify end-to-end guest checkout functionality from product selection through successful order placement and confirmation.

#### Test Data

| Field          | Value                          | Validation               |
|----------------|--------------------------------|--------------------------|
| First Name     | John                           | Alpha only, required     |
| Last Name      | Doe                            | Alpha only, required     |
| Email          | john.doe@testmail.com          | Valid email format       |
| Address        | 123 Test Street                | Required                 |
| Postal Code    | 10001                          | Numeric, valid ZIP       |
| City           | New York                       | Alpha, required          |
| Country        | United States                  | Default/selected         |
| Shipping       | (Auto-selected)                | Any available method     |
| Payment        | Pay by Check                   | Demo-safe method         |
| Terms Accepted | ✓                              | Required for submission  |

---

#### Test Steps (Detailed)

| # | Action | Expected Result | Pass Criteria |
|---|--------|-----------------|---------------|
| 1 | Navigate to https://demo.prestashop.com/ | Homepage loads; iframe visible | HTTP 200, iframe present |
| 2 | Switch to iframe `#framelive` | Context switched to storefront | Frame accessible |
| 3 | Locate first product on homepage | Product displayed with image, name, price | Element visible |
| 4 | Click product to view details | Product detail page loads | "Add to Cart" button visible |
| 5 | Click "Add to Cart" | Modal confirms product added | Success message/modal appears |
| 6 | Click "Proceed to Checkout" (modal) | Cart page displays | Product listed in cart |
| 7 | Click "Proceed to Checkout" (cart) | Checkout form loads | Personal info fields visible |
| 8 | Fill first name, last name, email | Fields accept input | No validation errors |
| 9 | Fill address, postal code, city, country | Fields accept input | Form validates successfully |
| 10 | Click "Continue" → Shipping | Shipping options page loads | Shipping methods visible |
| 11 | Confirm shipping method | Method selected | Price updates (if applicable) |
| 12 | Click "Continue" → Payment | Payment options page loads | Payment methods visible |
| 13 | Select "Pay by Check" | Payment method selected | Radio button checked |
| 14 | Check "Terms and Conditions" | Checkbox checked | "Place Order" enabled |
| 15 | Click "Place Order" | Order submitted | Confirmation page loads |
| 16 | Verify confirmation & order ref | Success message + order # displayed | Message contains "confirm"/"thank you" + unique order reference |

---

#### Postconditions
- Order created in system (order reference issued)
- Cart emptied
- Guest session can place another order
- Order confirmation page displayed

---

#### Acceptance Criteria

**✅ PASS if ALL met:**
1. No errors or exceptions during any step
2. Order confirmation page displays within 60 seconds
3. Confirmation message contains: "confirmed", "thank you", or "order reference"
4. Order reference number is visible and non-empty
5. All mandatory fields validated correctly

**❌ FAIL if ANY met:**
1. Any step produces error/exception
2. Timeout exceeds 60 seconds total
3. Order confirmation page doesn't load
4. No order reference displayed
5. User redirected to error/payment failure page

---

### Test Variants (Not Automated)

| ID | Scenario | Expected | Priority |
|----|----------|----------|----------|
| TC-E2E-002 | Invalid email (test@) | Validation error | P2 |
| TC-E2E-003 | Missing last name | Form blocked | P2 |
| TC-E2E-004 | Unchecked terms | Order button disabled | P2 |
| TC-E2E-005 | Empty cart checkout | Error or redirect | P3 |
| TC-E2E-006 | Out-of-stock product | Error message | P3 |
| TC-E2E-007 | Special chars in name | Accepted or rejected clearly | P3 |
| TC-E2E-008 | Invalid postal code | Validation error | P3 |

---

## PHASE 2 — Automation Implementation

### Script 1: Selenium (Python)

**File:** `selenium_python/test_e2e_purchase.py`

**Key Features:**
- WebDriver Manager for auto-driver setup
- Explicit waits (WebDriverWait + ExpectedConditions)
- Iframe switching with context management
- JavaScript executor for problematic clicks
- Screenshot on failure
- Step-by-step console logging

**Technology Stack:**
- selenium==4.15.2
- webdriver-manager==4.0.1
- Python 3.8+

**Run Command:**
```bash
cd selenium_python
pip install -r requirements.txt
python test_e2e_purchase.py
```

---

### Script 2: Playwright (TypeScript)

**File:** `playwright_typescript/test-e2e-purchase.spec.ts`

**Key Features:**
- frameLocator for iframe handling (no context switch)
- Auto-wait functionality (no explicit waits needed mostly)
- Regex-based assertions (language-independent)
- HTML report generation
- Video recording on failure
- Trace viewer support

**Technology Stack:**
- @playwright/test==1.40.0
- TypeScript
- Node.js 18+

**Run Command:**
```bash
cd playwright_typescript
npm install
npx playwright install chromium
npm test
```

---

## Test Execution Comparison

| Aspect | Selenium | Playwright |
|--------|----------|------------|
| Setup Complexity | Medium (pip install) | Medium (npm install) |
| Iframe Handling | Manual switch_to.frame() | frameLocator (cleaner) |
| Wait Strategy | Explicit WebDriverWait | Auto-wait built-in |
| Debugging | Screenshots only | Screenshots + Video + Trace |
| Speed | ~40-50 seconds | ~35-45 seconds |
| Report | Console output | HTML + console |
| CI/CD Ready | ✅ | ✅✅ (better) |
| Cross-browser | ✅ | ✅✅ |

---

## Quality Assurance Notes

### Covered Scenarios
✅ Product browsing and selection  
✅ Add to cart functionality  
✅ Guest checkout (no login)  
✅ Personal information validation  
✅ Address entry and validation  
✅ Shipping method selection  
✅ Payment method selection  
✅ Terms acceptance requirement  
✅ Order submission  
✅ Order confirmation verification  

### Not Covered (Out of Scope)
❌ Registered user checkout  
❌ Multiple products in cart  
❌ Coupon/discount codes  
❌ Real payment gateway integration  
❌ Email confirmation receipt  
❌ Stock validation  
❌ Internationalization (multiple languages)  
❌ Mobile responsive testing  

### Risk Assessment

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Demo site down | High | Medium | Retry logic, monitoring |
| Iframe not loading | High | Low | Explicit iframe wait |
| Selector changes | Medium | Low | Semantic selectors |
| Timeout issues | Medium | Medium | Generous timeouts (20-30s) |
| Localization changes | Low | Low | Regex patterns, avoid text |

---

## Maintenance Schedule

**Weekly:** Monitor test pass rate in CI/CD  
**Monthly:** Review and update selectors if needed  
**Quarterly:** Full regression with multiple products  
**Annually:** Update framework versions  

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-08 | QA Team | Initial test case design & automation |

---

**IEEE 29119 Compliance:** ✅  
**ISTQB Best Practices:** ✅  
**Code Review:** Pending  
**Approved By:** _[Pending]_  
**Status:** Ready for Execution
