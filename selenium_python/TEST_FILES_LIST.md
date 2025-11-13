# Test Files List - Selenium Python

## 📂 All Converted Test Files

### Main Scenario Tests (15 files total)

```
selenium_python/tests/
├── test_bagisto_s1_single_checkout.py          ✅ (Pre-existing)
├── test_bagisto_s2_multiple_coupon.py          ✅ Converted
├── test_bagisto_s3_payment_methods.py          ✅ Converted
├── test_bagisto_s4_out_of_stock.py             ✅ Converted
├── test_bagisto_s5_price_change.py             ✅ Converted
├── test_bagisto_s6_shipping_method.py          ✅ Converted
├── test_bagisto_s9_refresh_payment.py          ✅ Converted
├── test_bagisto_s9b_immediate_f5.py            ✅ Converted (NEW)
├── test_bagisto_s14_digital_goods.py           ✅ Converted
├── test_bagisto_s16_concurrent_carts.py        ✅ Converted (NEW)
├── test_bagisto_s16b_concurrent_place_order.py ✅ Converted (NEW)
├── test_bagisto_s17_cancel_order.py            ✅ Converted
├── test_bagisto_step_b1a.py                    ✅ Converted (Edge case)
├── test_bagisto_step_b1b.py                    ✅ Converted (Edge case)
└── test_bagisto_step_b1c.py                    ✅ Converted (Edge case)
```

### Quick Run Commands

```bash
# S1 - Single product checkout
pytest tests/test_bagisto_s1_single_checkout.py -v -s

# S2 - Coupon code checkout
pytest tests/test_bagisto_s2_multiple_coupon.py -v -s

# S3 - Payment methods switching
pytest tests/test_bagisto_s3_payment_methods.py -v -s

# S4 - Out of stock handling
pytest tests/test_bagisto_s4_out_of_stock.py -v -s

# S5 - Price change during checkout
pytest tests/test_bagisto_s5_price_change.py -v -s

# S6 - Shipping method switching
pytest tests/test_bagisto_s6_shipping_method.py -v -s

# S9 - F5 reload (3 second delay)
pytest tests/test_bagisto_s9_refresh_payment.py -v -s

# S9b - F5 reload IMMEDIATE (< 100ms)
pytest tests/test_bagisto_s9b_immediate_f5.py -v -s

# S14 - Digital goods (e-books)
pytest tests/test_bagisto_s14_digital_goods.py -v -s

# S16 - Concurrent browser carts
pytest tests/test_bagisto_s16_concurrent_carts.py -v -s

# S16b - Concurrent Place Order race condition
pytest tests/test_bagisto_s16b_concurrent_place_order.py -v -s

# S17 - Cancel and reorder
pytest tests/test_bagisto_s17_cancel_order.py -v -s

# B1a - Empty cart checkout validation
pytest tests/test_bagisto_step_b1a.py -v -s

# B1b - Remove all products
pytest tests/test_bagisto_step_b1b.py -v -s

# B1c - Save for later (Wishlist)
pytest tests/test_bagisto_step_b1c.py -v -s

# Run all tests
pytest tests/ -v -s
```

### Test Categories

#### Happy Path (6 tests)
- S1: Single checkout
- S2: Coupon checkout
- S3: Payment methods
- S6: Shipping methods
- S14: Digital goods
- S17: Cancel & reorder

#### Edge Cases (3 tests)
- B1a: Empty cart checkout
- B1b: Remove all products
- B1c: Save for later

#### Error Handling (2 tests)
- S4: Out of stock
- S5: Price change

#### Race Conditions (4 tests)
- S9: F5 reload (3s)
- S9b: F5 immediate (< 100ms)
- S16: Concurrent carts
- S16b: Concurrent Place Order

---

**Total:** 15 test files, 20+ scenarios
