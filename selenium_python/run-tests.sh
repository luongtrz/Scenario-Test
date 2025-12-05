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
        echo "Running S1 - Empty Cart Checkout..."
        pytest tests/test_bagisto_s1.py -v -s
        ;;
    s2|S2)
        echo "Running S2 - Remove All Products..."
        pytest tests/test_bagisto_s2.py -v -s
        ;;
    s3|S3)
        echo "Running S3 - Move to Wishlist..."
        pytest tests/test_bagisto_s3.py -v -s
        ;;
    s4|S4)
        echo "Running S4 - Zero Stock Handling..."
        pytest tests/test_bagisto_s4.py -v -s
        ;;
    s5|S5)
        echo "Running S5 - Stock Reduction During Checkout..."
        pytest tests/test_bagisto_s5.py -v -s
        ;;
    s6|S6)
        echo "Running S6 - Price Change During Checkout..."
        pytest tests/test_bagisto_s6.py -v -s
        ;;
    s7|S7)
        echo "Running S7 - Change Shipping Method..."
        pytest tests/test_bagisto_s7.py -v -s
        ;;
    s8|S8)
        echo "Running S8 - Apply Coupon Code..."
        pytest tests/test_bagisto_s8.py -v -s
        ;;
    s9|S9)
        echo "Running S9 - Change Payment Method..."
        pytest tests/test_bagisto_s9.py -v -s
        ;;
    s10|S10)
        echo "Running S10 - Digital Goods (E-Books)..."
        pytest tests/test_bagisto_s10.py -v -s
        ;;
    s11|S11)
        echo "Running S11 - Happy Path Single Product..."
        pytest tests/test_bagisto_s11.py -v -s
        ;;
    s12|S12)
        echo "Running S12 - Reload During Order Creation..."
        pytest tests/test_bagisto_s12.py -v -s
        ;;
    s14|S14)
        echo "Running S14 - Immediate F5 After Place Order..."
        pytest tests/test_bagisto_s14.py -v -s
        ;;
    s15|S15)
        echo "Running S15 - Cancel Order & Reorder..."
        pytest tests/test_bagisto_s15.py -v -s
        ;;
    s16|S16)
        echo "Running S16 - Concurrent Cart Editing..."
        pytest tests/test_bagisto_s16.py -v -s
        ;;
    s13|S13)
        echo "Running S13 - Concurrent Place Order Race..."
        pytest tests/test_bagisto_s13.py -v -s
        ;;
    
    all)
        echo "Running ALL test scenarios..."
        pytest tests/ -v -s
        ;;
    *)
        echo "Usage: $0 [scenario] [mode]"
        echo ""
        echo "Scenarios:"
        echo "  s1   - Empty cart checkout"
        echo "  s2   - Remove all products"
        echo "  s3   - Move to wishlist"
        echo "  s4   - Zero stock handling"
        echo "  s5   - Stock reduction during checkout"
        echo "  s6   - Price change during checkout"
        echo "  s7   - Change shipping method"
        echo "  s8   - Apply coupon code"
        echo "  s9   - Change payment method"
        echo "  s10  - Digital goods (e-books)"
        echo "  s11  - Happy path single product"
        echo "  s12  - Reload during order creation"
        echo "  s14  - Immediate F5 after place order"
        echo "  s15  - Cancel order & reorder"
        echo "  s16  - Concurrent cart editing"
        echo "  s17  - Concurrent place order race"
        echo "  all  - Run all scenarios (default)"
        echo ""
        echo "Mode:"
        echo "  headed   - Browser visible (default)"
        echo "  headless - Browser hidden"
        echo ""
        echo "Examples:"
        echo "  $0 s1          # Run S1 in headed mode"
        echo "  $0 s11 headless # Run S11 in headless mode"
        echo "  $0 all headed  # Run all tests with browser visible"
        exit 1
        ;;
esac

echo ""
echo "✅ Test execution completed!"
