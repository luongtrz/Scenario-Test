#!/bin/bash

echo "==================================="
echo "Running All Bagisto Test Scenarios"
echo "==================================="
echo ""

TESTS=(
    "bagisto-s1-single-checkout.spec.ts"
    # "bagisto-s2-multiple-coupon.spec.ts"
    # "bagisto-s3-payment-methods.spec.ts"
    # "bagisto-s4-out-of-stock.spec.ts"
    # "bagisto-s5-price-change.spec.ts"
    # "bagisto-s6-shipping-method.spec.ts"
    # "bagisto-s7-3ds-otp.spec.ts"
    # "bagisto-s8-gateway-timeout.spec.ts"
    # "bagisto-s9-refresh-payment.spec.ts"
    # "bagisto-s10-split-tender.spec.ts"
    # "bagisto-s11-guest-checkout.spec.ts"
    # "bagisto-s12-pickup.spec.ts"
    # "bagisto-s13-preorder.spec.ts"
    # "bagisto-s14-digital-goods.spec.ts"
    # "bagisto-s15-subscription.spec.ts"
    # "bagisto-s16-concurrent-carts.spec.ts"
    # "bagisto-s17-cancel-order.spec.ts"
    # "bagisto-step-b1a.spec.ts"
    # "bagisto-step-b1b.spec.ts"
    # "bagisto-step-b1c.spec.ts"
)

PASSED=0
FAILED=0
FAILED_TESTS=()

for test in "${TESTS[@]}"; do
    echo ">>> Running: $test"
    if npm test tests/$test > /dev/null 2>&1; then
        echo "    ✅ PASSED"
        ((PASSED++))
    else
        echo "    ❌ FAILED"
        ((FAILED++))
        FAILED_TESTS+=("$test")
    fi
    echo ""
done

echo "==================================="
echo "Test Summary"
echo "==================================="
echo "Total: $((PASSED + FAILED)) tests"
echo "✅ Passed: $PASSED"
echo "❌ Failed: $FAILED"
echo ""

if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
    echo "Failed tests:"
    for test in "${FAILED_TESTS[@]}"; do
        echo "  - $test"
    done
fi
