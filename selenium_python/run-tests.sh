#!/bin/bash
# Run individual Bagisto Selenium Python test scenarios

set -e

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

echo "🧪 Bagisto Selenium Python - Test Runner"
echo "========================================="
echo ""

# Check for .env
if [ ! -f ".env" ]; then
    echo "⚠️  ERROR: .env file not found!"
    echo "   Please create .env with your credentials"
    exit 1
fi

# Parse command line arguments
SCENARIO=${1:-all}
MODE=${2:-headed}

# Set headless based on mode
if [ "$MODE" = "headless" ]; then
    export HEADLESS=true
else
    export HEADLESS=false
fi

echo "Test Mode: $MODE (HEADLESS=$HEADLESS)"
echo ""

# Run specific scenario or all
case $SCENARIO in
    s1|S1)
        echo "Running S1 - Single Product Checkout..."
        pytest tests/test_bagisto_s1_single_checkout.py -v -s
        ;;
    s2|S2)
        echo "Running S2 - Multiple Products + Coupon..."
        pytest tests/test_bagisto_s2_multiple_coupon.py -v -s
        ;;
    s3|S3)
        echo "Running S3 - Payment Methods..."
        pytest tests/test_bagisto_s3_payment_methods.py -v -s
        ;;
    s4|S4)
        echo "Running S4 - Out of Stock..."
        pytest tests/test_bagisto_s4_out_of_stock.py -v -s
        ;;
    s4b|S4B)
        echo "Running S4B - Zero Stock Product Handling..."
        pytest tests/test_bagisto_s4b_zero_stock.py -v -s
        ;;
    s5|S5)
        echo "Running S5 - Price Change Handling..."
        pytest tests/test_bagisto_s5_price_change_real.py -v -s
        ;;
    s6|S6)
        echo "Running S6 - Shipping Method Change..."
        pytest tests/test_bagisto_s6_shipping_method.py -v -s
        ;;
    s9|S9)
        echo "Running S9 - Refresh Payment..."
        pytest tests/test_bagisto_s9_refresh_payment.py -v -s
        ;;
    s9b|S9B)
        echo "Running S9B - Refresh Payment Immediate F5..."
        pytest tests/test_bagisto_s9b_immediate_f5.py -v -s
        ;;
    s14|S14)
        echo "Running S14 - Digital Goods..."
        pytest tests/test_bagisto_s14_digital_goods.py -v -s
        ;;
    s16|S16)
        echo "Running S16 - Guest Checkout..."
        pytest tests/test_bagisto_s16_concurrent_carts.py -v -s
        ;;
    s16b|S16B)
        echo "Running S16B - Concurrent Place Order Race Condition..."
        pytest tests/test_bagisto_s16b_concurrent_place_order.py -v -s
        ;;
    s17|S17)
        echo "Running S17 - Cancel Order & Reorder..."
        pytest tests/test_bagisto_s17_cancel_order.py -v -s
        ;;
    b1a|B1A)
        echo "Running B1A - Step B1a..."
        pytest tests/test_bagisto_step_b1a.py -v -s
        ;;
    b1b|B1B)
        echo "Running B1B - Step B1b..."
        pytest tests/test_bagisto_step_b1b.py -v -s
        ;;
    b1c|B1C)
        echo "Running B1C - Step B1c..."
        pytest tests/test_bagisto_step_b1c.py -v -s
        ;;
    
    all)
        echo "Running ALL test scenarios..."
        pytest tests/ -v -s
        ;;
    *)
        echo "Usage: $0 [scenario] [mode]"
        echo ""
        echo "Scenarios:"
        echo "  s1   - Single product checkout"
        echo "  s2   - Multiple products with coupon"
        echo "  s3   - Payment methods"
        echo "  s4   - Out of stock handling"
        echo "  s5   - Price change handling"
        echo "  s6   - Shipping method change"
        echo "  s9   - Refresh payment (dual scenario)"
        echo "  s9b  - Refresh payment (immediate F5)"
        echo "  s14  - Digital goods (e-books)"
        echo "  s16  - Concurrent carts"
        echo "  s16b - Concurrent Place Order race"
        echo "  s17  - Cancel order & reorder"
        echo "  all  - Run all scenarios (default)"
        echo ""
        echo "Mode:"
        echo "  headed   - Browser visible (default)"
        echo "  headless - Browser hidden"
        echo ""
        echo "Examples:"
        echo "  $0 s1          # Run S1 in headed mode"
        echo "  $0 s2 headless # Run S2 in headless mode"
        echo "  $0 all headed  # Run all tests with browser visible"
        exit 1
        ;;
esac

echo ""
echo "✅ Test execution completed!"
