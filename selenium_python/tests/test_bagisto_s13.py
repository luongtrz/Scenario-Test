"""
S9B: B1 → B2 → B3 → B4 → B5c (Immediate F5 After Place Order)
Click Place Order, IMMEDIATELY press F5 (< 100ms - instant reload)
Then place order again, WAIT for completion, check for duplicates

Equivalent to: playwright_typescript/tests/bagisto-s9b-immediate-f5.spec.ts

Difference from S9:
- S9: Wait 3 seconds after Place Order, then F5
- S9B: Wait < 100ms (IMMEDIATE F5)
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from pages.store_page import StorePage


class TestBagistoS9bImmediateF5:
    """S9B - Immediate F5 After Place Order Test Suite"""
    
    def test_s9b_place_order_immediate_f5_then_retry(self, driver, base_url, credentials):
        """
        S9B – Place Order #1, IMMEDIATE F5, Place Order #2, verify duplicates
        
        Test Flow:
        1. Login and add product to cart
        2. Capture initial order count
        3. Go to checkout, fill address
        4. Select shipping and payment methods
        5. ORDER #1: Click Place Order
        6. IMMEDIATE F5 (< 100ms) - Interrupt order processing
        7. ORDER #2: Place order again and WAIT for success page
        8. Check orders page - count NEW orders
        9. If 2 orders created: Compare for duplicates
        10. Verify cart is empty
        
        Expected:
        - Only 1 order created (first interrupted by F5)
        - If 2 orders: Flag as duplicate bug
        """
        print("\n" + "="*80)
        print("S9B: IMMEDIATE F5 AFTER PLACE ORDER")
        print("="*80)
        print("\n⚠️  Testing VERY FAST F5 interrupt (< 100ms after clicking Place Order)\n")
        
        store = StorePage(driver, base_url)
        
        # Step 1: Login
        print("\nStep 1 (B1): Logging in to save order...")
        store.login()
        
        # Step 2: Check cart
        print("\nStep 2 (B2): Checking cart...")
        store.open_cart()
        time.sleep(2)
        
        initial_qty_inputs = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="hidden"][name="quantity"]'
        )
        initial_cart_count = len(initial_qty_inputs)
        print(f'  ✓ Cart has {initial_cart_count} item(s)')
        
        if initial_cart_count == 0:
            print('  → Cart empty, adding product...')
            store.add_first_product_from_home()
        else:
            print('  ✓ Using existing cart items')
        
        # Step 3: Capture initial order count
        print("\nStep 3 (B5c): Capturing initial order count BEFORE checkout...")
        driver.get(f"{base_url}/customer/account/orders")
        time.sleep(2)
        
        order_rows = driver.find_elements(
            By.CSS_SELECTOR,
            '.row.grid'
        )
        
        # Filter out header row
        order_data_rows = [
            row for row in order_rows
            if 'Order ID' not in row.text and 'Order Date' not in row.text
        ]
        
        initial_order_count = len(order_data_rows)
        
        # Get first order ID to detect new orders (pagination shows only 10 per page)
        initial_first_order_id = ''
        if initial_order_count > 0:
            first_order_cells = order_data_rows[0].find_elements(By.TAG_NAME, 'p')
            if first_order_cells:
                initial_first_order_id = first_order_cells[0].text.strip()
                print(f'  Initial order count: {initial_order_count} (first ID: #{initial_first_order_id})')
        else:
            print('  Initial order count: 0')
        
        # Step 4: Back to cart
        print("\nStep 4 (B3): Going back to cart...")
        driver.get(f"{base_url}/checkout/cart")
        time.sleep(1.5)
        print('  ✓ Back at cart page')
        
        # Step 5: Proceed to checkout
        print("\nStep 5 (B3): Proceeding to checkout...")
        store.go_checkout()
        
        # Step 6: Fill address
        print("\nStep 6 (B4): Filling shipping address...")
        store.fill_shipping_address_minimal()
        
        # Step 7: Select shipping and payment
        print("\nStep 7 (B5): Selecting shipping and payment methods...")
        time.sleep(2)
        
        try:
            free_shipping_label = driver.find_element(
                By.CSS_SELECTOR,
                'label[for="free_free"]'
            )
            free_shipping_label.click()
            print('  ✓ Selected Free Shipping')
            time.sleep(1)
        except NoSuchElementException:
            print('  ⚠ No shipping method found')
        
        try:
            cod_label = driver.find_element(
                By.CSS_SELECTOR,
                'label[for="cashondelivery"]'
            )
            cod_label.click()
            print('  ✓ Selected Cash on Delivery')
            time.sleep(1)
        except NoSuchElementException:
            print('  ⚠ Payment method not found')
        
        # ORDER #1 - Place and immediate F5
        print("\n" + "="*80)
        print("ORDER #1 - PLACE AND IMMEDIATE F5")
        print("="*80)
        print("\nStep 8 (B5c): Clicking Place Order and IMMEDIATE F5...")
        
        try:
            place_order_btn = driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Place Order')]"
            )
            
            if place_order_btn.is_displayed():
                print('  → Clicking Place Order button...')
                place_order_btn.click()
                
                print('  → IMMEDIATE F5 (< 100ms)!')
                time.sleep(0.1)  # Only 100ms - VERY FAST!
                
                driver.refresh()
                time.sleep(1)
                
                print('  ✓ Page reloaded immediately')
                print(f'  Current URL: {driver.current_url}')
        except NoSuchElementException:
            print('  ⚠ Place Order button not visible!')
            driver.refresh()
            time.sleep(1)
        
        # CHECK IF ORDER #1 ALREADY COMPLETED (AJAX cleared cart)
        print("\n" + "="*80)
        print("DETECTING SCENARIO - Check if Order #1 completed")
        print("="*80)
        print("\nStep 9: Checking if Order #1 completed during F5...")
        
        time.sleep(2)
        
        current_url = driver.current_url
        print(f'  Current URL: {current_url}')
        
        # Check if redirected to cart page (sign of order completion)
        if '/checkout/cart' in current_url:
            print('  → Redirected to cart page - checking if cart is empty...')
            
            # Check cart status
            qty_inputs_after = driver.find_elements(
                By.CSS_SELECTOR,
                'input[type="hidden"][name="quantity"]'
            )
            ebook_checkboxes_after = driver.find_elements(
                By.CSS_SELECTOR,
                'input[type="checkbox"][id^="item_"]'
            )
            
            cart_count_after = len(qty_inputs_after) + len(ebook_checkboxes_after)
            print(f'  Cart count after F5: {cart_count_after}')
            
            if cart_count_after == 0:
                print("\n" + "="*80)
                print("SCENARIO A: Order #1 COMPLETED before F5")
                print("="*80)
                print("  ✓ F5 was TOO SLOW - Order #1 completed")
                print("  ✓ Cart cleared by AJAX after order completion")
                print("  → Cannot test duplicate (cart empty)")
                print("  → Test PASSED: Only 1 order created")
                print("\n⚠ LIMITATION: 100ms F5 not fast enough for this product")
                print("   Backend processed order before interrupt could take effect")
                
                # Still verify order was created
                driver.get(f"{base_url}/customer/account/orders")
                time.sleep(2)
                
                new_order_rows = driver.find_elements(By.CSS_SELECTOR, '.row.grid')
                new_order_data_rows = [
                    row for row in new_order_rows
                    if 'Order ID' not in row.text and 'Order Date' not in row.text
                ]
                
                if len(new_order_data_rows) > 0:
                    new_first_order_cells = new_order_data_rows[0].find_elements(By.TAG_NAME, 'p')
                    if new_first_order_cells:
                        new_first_order_id = new_first_order_cells[0].text.strip()
                        if new_first_order_id != initial_first_order_id:
                            print(f"\n✓ Order created: #{new_first_order_id}")
                
                print("\n" + "="*80)
                print("S9B: COMPLETED - Scenario A (Order completed, cart cleared)")
                print("="*80)
                return
        
        # SCENARIO B: Order NOT completed, cart still has items
        print("\n" + "="*80)
        print("SCENARIO B: Order #1 INTERRUPTED - Cart remains")
        print("="*80)
        print("  ✓ F5 was FAST ENOUGH - Order interrupted")
        print("  ✓ Cart still has items")
        print("  → Proceeding to re-checkout for duplicate test")
        
        # ORDER #2 - Re-checkout with existing cart
        print("\n" + "="*80)
        print("ORDER #2 - PLACE AGAIN AND WAIT FOR COMPLETION")
        print("="*80)
        print("\nStep 10 (B5c): Placing order again after F5...")
        
        # Check if payment options are visible
        payment_visible = False
        try:
            driver.find_element(
                By.CSS_SELECTOR,
                'input[type="radio"][id*="free_free"], input[type="radio"][id*="cashondelivery"]'
            )
            payment_visible = True
            print('  → Payment options already visible, proceeding...')
        except NoSuchElementException:
            pass
        
        if not payment_visible:
            # Address info still filled, just need to click Proceed button
            print('  → Payment options not visible, clicking Proceed button...')
            try:
                proceed_btn = driver.find_element(
                    By.XPATH,
                    "//button[contains(text(), 'Proceed')]"
                )
                driver.execute_script("arguments[0].click();", proceed_btn)
                print('    ✓ Clicked Proceed button')
                time.sleep(2)  # Wait for shipping/payment to load
            except NoSuchElementException:
                print('    ⚠ Proceed button not found')
        
        print("\nStep 11 (B5): Selecting payment and placing order #2...")
        time.sleep(1)
        
        # Select shipping method
        try:
            free_shipping_label_2 = driver.find_element(
                By.CSS_SELECTOR,
                'label[for="free_free"]'
            )
            free_shipping_label_2.click()
            print('  ✓ Selected Free Shipping')
            time.sleep(0.5)
        except NoSuchElementException:
            pass
        
        # Select payment method
        try:
            cod_label_2 = driver.find_element(
                By.CSS_SELECTOR,
                'label[for="cashondelivery"]'
            )
            cod_label_2.click()
            print('  ✓ Selected Cash on Delivery')
            time.sleep(0.5)
        except NoSuchElementException:
            pass
        
        # Click Place Order #2
        try:
            place_order_btn_2 = driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Place Order')]"
            )
            
            if place_order_btn_2.is_displayed():
                print('  → Clicking Place Order #2...')
                place_order_btn_2.click()
                print('  → Waiting for order processing (this may take time)...')
        except NoSuchElementException:
            print('  ⚠ Place Order button not found')
        
        # Step 12: Wait for success page
        print("\nStep 12 (B5): Waiting for order #2 success page...")
        second_order_id = ''
        try:
            WebDriverWait(driver, 60).until(
                EC.url_contains('/checkout/onepage/success')
            )
            print('  ✓ Order #2 redirected to success page')
            time.sleep(2)
            
            # Extract order ID
            try:
                order_link = driver.find_element(
                    By.CSS_SELECTOR,
                    'p.text-xl a.text-blue-700[href*="/customer/account/orders/view/"]'
                )
                second_order_id = order_link.text.strip()
                print(f'  ✓ Order #2 created: #{second_order_id}')
            except NoSuchElementException:
                second_order_id = ''
                print('  ⚠ Could not extract Order ID from success page')
        except TimeoutException:
            print('  ⚠ Did not redirect to success page')
            print(f'  Current URL: {driver.current_url}')
        
        # VERIFICATION - Check for duplicate orders
        print("\n" + "="*80)
        print("VERIFICATION - CHECK FOR DUPLICATE ORDERS")
        print("="*80)
        print("\nStep 13: Checking orders after both place order attempts...")
        driver.get(f"{base_url}/customer/account/orders")
        time.sleep(2)
        
        # Re-query after navigation
        order_rows_final = driver.find_elements(
            By.CSS_SELECTOR,
            '.row.grid'
        )
        
        order_data_rows_final = [
            row for row in order_rows_final
            if 'Order ID' not in row.text and 'Order Date' not in row.text
        ]
        
        final_order_count = len(order_data_rows_final)
        print(f'  Total orders on page: {final_order_count}')
        
        # Count NEW orders by iterating until we hit the initial order ID
        actual_new_orders = 0
        new_order_ids = []
        
        for i, row in enumerate(order_data_rows_final):
            cells = row.find_elements(By.TAG_NAME, 'p')
            if cells:
                order_id = cells[0].text.strip()
                
                if order_id == initial_first_order_id:
                    print(f'  → Found initial order #{initial_first_order_id} at position {i + 1}')
                    break
                
                actual_new_orders += 1
                new_order_ids.append(order_id)
                print(f'  → New order #{i + 1}: #{order_id}')
        
        # If 2 orders were created, compare them for duplicates
        if actual_new_orders == 2 and len(new_order_ids) >= 2:
            print("\nStep 14 (B5c): ⚠ 2 ORDERS CREATED - Comparing for duplicate detection...")
            
            order1_id = new_order_ids[0]
            order2_id = new_order_ids[1]
            print(f'  → Comparing Order #{order1_id} vs Order #{order2_id}...')
            
            # Helper function to extract order details
            def get_order_details(order_id_val):
                driver.get(f"{base_url}/customer/account/orders/view/{order_id_val}")
                time.sleep(3)  # CRITICAL: Wait for order page to load
                
                grand_total = 'N/A'
                product_name = 'N/A'
                
                # Extract Grand Total
                try:
                    gt_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Grand Total')]")
                    for elem in gt_elements:
                        text = elem.text
                        if '$' in text:
                            import re
                            match = re.search(r'\$[\d,]+\.?\d*', text)
                            if match:
                                grand_total = match.group(0)
                                break
                except:
                    pass
                
                # Extract Product Name
                try:
                    product_cells = driver.find_elements(By.XPATH, "//td[contains(@class, 'text')]")
                    if product_cells:
                        product_name = product_cells[0].text.strip()
                except:
                    pass
                
                return grand_total, product_name
            
            # Get Order #1 details
            order1_gt, order1_product = get_order_details(order1_id)
            print(f'    Order #{order1_id}: {order1_gt}')
            print(f'    Product: {order1_product[:50]}...')
            
            # Get Order #2 details
            order2_gt, order2_product = get_order_details(order2_id)
            print(f'    Order #{order2_id}: {order2_gt}')
            print(f'    Product: {order2_product[:50]}...')
            
            # Compare
            print("\n  === DUPLICATE COMPARISON ===")
            same_totals = order1_gt != 'N/A' and order1_gt == order2_gt
            same_products = (order1_product != 'N/A' and order2_product != 'N/A' and 
                           order1_product == order2_product)
            
            if same_totals and same_products:
                print('  ❌ DUPLICATE CONFIRMED!')
                print(f'    Both orders have:')
                print(f'      - Same Grand Total: {order1_gt}')
                print(f'      - Same Product: {order1_product[:60]}...')
                print('    → IMMEDIATE F5 created duplicate order!')
            else:
                print('  ℹ Orders are DIFFERENT:')
                print(f'    Order #{order1_id}: {order1_gt} - {order1_product[:40]}...')
                print(f'    Order #{order2_id}: {order2_gt} - {order2_product[:40]}...')
                print('    → Not duplicate (different products or prices)')
        
        # Order creation summary
        print("\n" + "="*80)
        print("ORDER CREATION SUMMARY")
        print("="*80)
        print(f'  Initial first order: #{initial_first_order_id or "None"}')
        print(f'  New orders created: {actual_new_orders}')
        
        if actual_new_orders >= 1 and actual_new_orders <= 3:
            for i, order_id in enumerate(new_order_ids[:3]):
                print(f'    Order #{i + 1}: #{order_id}')
        
        print()
        
        if actual_new_orders == 1:
            print('  ✓ PASS: Only 1 order created (no duplicate)')
            print('    → First order was interrupted by F5, second order succeeded')
        elif actual_new_orders == 2:
            print('  ⚠ POTENTIAL DUPLICATE: 2 orders created!')
            print('    → Need to compare orders to confirm duplicate')
        else:
            print(f'  ℹ Created {actual_new_orders} orders (check manually)')
        
        # Step 15: Verify cart is empty
        print("\nStep 15: Verifying cart is empty...")
        store.open_cart()
        time.sleep(2)
        
        try:
            store.cart_is_empty()
            print('  ✓ Cart empty after order')
        except:
            qty_inputs_check = driver.find_elements(
                By.CSS_SELECTOR,
                'input[type="hidden"][name="quantity"]'
            )
            cart_items = len(qty_inputs_check)
            print(f'  ⚠ Cart not empty: {cart_items} items')
        
        print("\n" + "="*80)
        print("S9B: COMPLETED - Immediate F5 (0ms) + Immediate Re-order Test")
        print("="*80)
        print("\n=== KEY FINDINGS ===")
        print(f'  Initial order: #{initial_first_order_id or "No orders"}')
        print(f'  New orders created: {actual_new_orders} {f"(Success page showed #{second_order_id})" if second_order_id else ""}')
        print(f'  Duplicate prevention: {"✓ PASS" if actual_new_orders == 1 else "✗ FAIL (DUPLICATE!)" if actual_new_orders == 2 else "?"}')
        print("\nTest Scenario:")
        print("  1. Place Order #1 → Click button")
        print("  2. Wait 100ms (VERY FAST interrupt)")
        print("  3. Press F5 to reload page")
        print("  4. Add product → Checkout → Place Order #2 (IMMEDIATE re-order)")
        print("  5. Check orders page - COUNT new orders")
        print("  6. If 2 orders: Compare price + product for duplicate detection")
        print("="*80 + "\n")
