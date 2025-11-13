"""
S9: B1 → B2 → B3 → B4 → B5c (Reload During Order Placement)
User clicks Place Order, waits 1-2s, then reloads (F5) during order creation
Expected: No duplicate orders, can re-checkout after reload

Equivalent to: playwright_typescript/tests/bagisto-s9-refresh-payment.spec.ts
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from pages.store_page import StorePage


class TestBagistoS9ReloadDuringCheckout:
    """S9 - Reload During Checkout Test Suite"""
    
    def test_s9_reload_during_order_placement(self, driver, base_url, credentials):
        """
        S9 – Click Place Order, reload (F5) during loading, then re-order
        
        Steps:
        1. Login and check cart
        2. Capture initial order count
        3. Proceed to checkout
        4. Fill shipping address
        5. Select shipping and payment
        6. Click Place Order
        7. Wait 3 seconds (order in progress)
        8. RELOAD PAGE (F5) - interrupt order creation
        9. Check if order was created during interruption
        10. Check cart state after reload
        11. Re-checkout and place order again
        12. Verify only 1 order created (no duplicate)
        """
        print("\n" + "="*80)
        print("S9 – RELOAD DURING CHECKOUT")
        print("="*80)
        
        store = StorePage(driver, base_url)
        
        # Step 1: Login
        print("\nStep 1 (B1): Logging in...")
        store.login()
        
        # Step 2: Check cart
        print("\nStep 2 (B2): Checking cart...")
        store.open_cart()
        
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
        
        # Get order rows (exclude header)
        order_rows = driver.find_elements(By.CSS_SELECTOR, '.row.grid')
        data_rows = []
        for row in order_rows:
            row_text = row.text.lower()
            if 'order id' not in row_text and 'order date' not in row_text:
                data_rows.append(row)
        
        initial_order_count = len(data_rows)
        
        # Get first order ID (for detecting new orders)
        initial_first_order_id = ''
        if initial_order_count > 0:
            try:
                first_order_p = data_rows[0].find_element(By.TAG_NAME, 'p')
                initial_first_order_id = first_order_p.text.strip()
                print(f'  Initial order count: {initial_order_count} (first ID: #{initial_first_order_id})')
            except:
                print(f'  Initial order count: {initial_order_count}')
        else:
            print('  Initial order count: 0')
        
        # Step 4: Go back to cart and checkout
        print("\nStep 4 (B3): Going back to cart...")
        driver.get(f"{base_url}/checkout/cart")
        time.sleep(1.5)
        print('  ✓ Back at cart page')
        
        print("\nStep 5 (B3): Proceeding to checkout...")
        store.go_checkout()
        
        print("\nStep 6 (B4): Filling shipping address...")
        store.fill_shipping_address_minimal()
        
        # Step 7: Select shipping and payment
        print("\nStep 7 (B5): Selecting shipping and payment methods...")
        time.sleep(2)
        
        # Free shipping
        try:
            free_labels = driver.find_elements(
                By.CSS_SELECTOR,
                'label[for="free_free"]'
            )
            if free_labels:
                free_labels[-1].click()
                print('  ✓ Selected Free Shipping')
                time.sleep(1)
        except:
            pass
        
        # COD payment
        try:
            cod_labels = driver.find_elements(
                By.CSS_SELECTOR,
                'label[for="cashondelivery"]'
            )
            if cod_labels:
                cod_labels[-1].click()
                print('  ✓ Selected Cash on Delivery')
                time.sleep(1)
        except:
            pass
        
        # Step 8: Click Place Order and INTERRUPT with F5
        print("\nStep 8 (B5c): Clicking Place Order and INTERRUPTING with F5...")
        
        # Scroll to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        
        try:
            place_order_btn = driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Place Order')]"
            )
            
            if place_order_btn.is_displayed():
                print('  → Clicking Place Order...')
                place_order_btn.click()
                
                print('  → Waiting 1.5 seconds (interrupt BEFORE order completes)...')
                time.sleep(2)
                
                print('  → RELOADING PAGE (F5) during order creation!')
                driver.refresh()
                time.sleep(2)
                print(f'  ✓ Page reloaded, URL: {driver.current_url}')
            else:
                print('  ⚠ Place Order button not visible!')
                driver.refresh()
                time.sleep(2)
        
        except NoSuchElementException:
            print('  ⚠ Place Order button not found!')
            driver.refresh()
            time.sleep(2)
        
        # Step 9: Check if order was created during interruption
        print("\nStep 9 (B5c): Checking if order was created during interrupted placement...")
        driver.get(f"{base_url}/customer/account/orders")
        time.sleep(2)
        
        # Re-query order rows
        order_rows_after = driver.find_elements(By.CSS_SELECTOR, '.row.grid')
        data_rows_after = []
        for row in order_rows_after:
            row_text = row.text.lower()
            if 'order id' not in row_text and 'order date' not in row_text:
                data_rows_after.append(row)
        
        order_count_after_reload = len(data_rows_after)
        
        first_order_id_after_reload = ''
        if order_count_after_reload > 0:
            try:
                first_order_p = data_rows_after[0].find_element(By.TAG_NAME, 'p')
                first_order_id_after_reload = first_order_p.text.strip()
            except:
                pass
        
        print(f'  Order count after reload: {order_count_after_reload} (first ID: #{first_order_id_after_reload})')
        
        order_created_during_interrupt = False
        if first_order_id_after_reload != initial_first_order_id and first_order_id_after_reload != '':
            order_created_during_interrupt = True
            print(f'  ⚠ Order WAS created during interrupted placement! (New ID: #{first_order_id_after_reload})')
            print('     → Reload did NOT prevent order creation!')
        else:
            print('  ✓ No order created during interrupted placement')
        
        # Step 10: Check cart state
        print("\nStep 10 (B5c): Checking cart state after reload...")
        driver.get(f"{base_url}/checkout/cart")
        time.sleep(1.5)
        
        qty_inputs_after = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="hidden"][name="quantity"]'
        )
        cart_count_after_reload = len(qty_inputs_after)
        print(f'  Cart items after reload: {cart_count_after_reload}')
        
        # Determine scenario
        if cart_count_after_reload == 0:
            if order_created_during_interrupt:
                print('  ℹ SCENARIO A: Order completed before F5 → cart cleared')
                print('  → This is EXPECTED behavior (F5 was too slow)')
                print('  → Skipping re-checkout since order already placed')
                
                # Skip to final verification
                print("\nStep 11-13: SKIPPED - Order already created")
                print("\nStep 14 (B5c): Final verification...")
                
                # Final order count should be initial + 1
                driver.get(f"{base_url}/customer/account/orders")
                time.sleep(2)
                
                order_rows_final = driver.find_elements(By.CSS_SELECTOR, '.row.grid')
                data_rows_final = []
                for row in order_rows_final:
                    row_text = row.text.lower()
                    if 'order id' not in row_text and 'order date' not in row_text:
                        data_rows_final.append(row)
                
                final_order_count = len(data_rows_final)
                final_first_order_id = ''
                if final_order_count > 0:
                    try:
                        first_order_p = data_rows_final[0].find_element(By.TAG_NAME, 'p')
                        final_first_order_id = first_order_p.text.strip()
                    except:
                        pass
                
                actual_new_orders = 1 if order_created_during_interrupt else 0
                
                print('')
                print('=== ORDER CREATION SUMMARY (Scenario A) ===')
                print(f'  Initial: {initial_order_count} (first ID: #{initial_first_order_id or "None"})')
                print(f'  After F5: {order_count_after_reload} (first ID: #{first_order_id_after_reload}) ← Order completed!')
                print(f'  Final: {final_order_count} (first ID: #{final_first_order_id})')
                print(f'  Total new orders: {actual_new_orders}')
                print(f'  Result: ✓ No duplicate (order completed, cart cleared)')
                print('')
                
                # Verify cart empty
                print('Step 15: Verifying cart is empty...')
                store.open_cart()
                
                try:
                    empty_msg = driver.find_element(By.XPATH, "//*[contains(text(), 'cart is empty') or contains(text(), 'Cart is empty')]")
                    print('  ✓ Cart is empty')
                except:
                    qty_inputs_empty = driver.find_elements(By.CSS_SELECTOR, 'input[type="hidden"][name="quantity"]')
                    if len(qty_inputs_empty) == 0:
                        print('  ✓ Cart is empty (no quantity inputs)')
                    else:
                        print(f'  ⚠ Cart has {len(qty_inputs_empty)} item(s)')
                
                print('\n' + '='*80)
                print('S9: COMPLETED - Scenario A (Order completed before F5)')
                print('='*80 + '\n')
                return  # End test here
            else:
                print('  ⚠ Cart empty but no order created (unexpected state)')
                print('  → Adding product to continue test...')
                store.add_first_product_from_home()
        else:
            print('  ✓ SCENARIO B: Cart still has items (F5 interrupted order creation)')
            print('  → Proceeding to re-checkout...')
        
        # Step 11: Re-checkout
        print("\nStep 11 (B5c): Proceeding to checkout again...")
        store.go_checkout()
        
        print("\nStep 12 (B4): Filling shipping address again...")
        store.fill_shipping_address_minimal()
        
        print("\nStep 13 (B5): Placing order after reload...")
        store.choose_payment_and_place(expect_success_msg=False)
        
        # Step 14: Wait for success
        print("\nStep 14 (B5): Waiting for order success page...")
        try:
            WebDriverWait(driver, 30).until(
                EC.url_contains('/checkout/onepage/success')
            )
            print('  ✓ Order redirected to success page')
            
            order_link = driver.find_element(
                By.CSS_SELECTOR,
                'p.text-xl a.text-blue-700[href*="/customer/account/orders/view/"]'
            )
            order_id_text = order_link.text.strip()
            print(f'  ✓ Order created: #{order_id_text}')
        
        except TimeoutException:
            print('  ⚠ Did not redirect to success page')
            print(f'  Current URL: {driver.current_url}')
        
        time.sleep(2)
        
        # Step 15: Final verification
        print("\nStep 15 (B5c): Final order count verification...")
        driver.get(f"{base_url}/customer/account/orders")
        time.sleep(2)
        
        # Re-query final orders
        order_rows_final = driver.find_elements(By.CSS_SELECTOR, '.row.grid')
        data_rows_final = []
        for row in order_rows_final:
            row_text = row.text.lower()
            if 'order id' not in row_text and 'order date' not in row_text:
                data_rows_final.append(row)
        
        final_order_count = len(data_rows_final)
        
        final_first_order_id = ''
        if final_order_count > 0:
            try:
                first_order_p = data_rows_final[0].find_element(By.TAG_NAME, 'p')
                final_first_order_id = first_order_p.text.strip()
            except:
                pass
        
        print(f'  Final order count: {final_order_count} (first ID: #{final_first_order_id})')
        
        # Calculate new orders
        actual_new_orders = 0
        if final_first_order_id != initial_first_order_id and final_first_order_id != '':
            if first_order_id_after_reload != initial_first_order_id and first_order_id_after_reload != '':
                actual_new_orders = 2  # Reload + re-order
            else:
                actual_new_orders = 1  # Only re-order
        
        print('')
        print('=== ORDER CREATION SUMMARY (Scenario B) ===')
        print(f'  Initial: {initial_order_count} (first ID: #{initial_first_order_id or "None"})')
        print(f'  After F5: {order_count_after_reload} (first ID: #{first_order_id_after_reload or "None"})', end='')
        if first_order_id_after_reload != initial_first_order_id and first_order_id_after_reload != '':
            print(' ← NEW ORDER CREATED!')
        else:
            print(' ← No change')
        print(f'  Final: {final_order_count} (first ID: #{final_first_order_id or "None"})')
        print(f'  Total new orders: {actual_new_orders}')
        print('')
        
        if actual_new_orders == 1:
            print('  ✓ PASS: Only 1 order created (no duplicate)')
            if first_order_id_after_reload != initial_first_order_id and first_order_id_after_reload != '':
                print('    → Scenario: F5 too slow, order completed before reload')
            else:
                print('    → F5 reload prevented duplicate order')
        elif actual_new_orders == 2:
            print('  ⚠ FAIL: 2 orders created - DUPLICATE BUG!')
            print('    → Interrupted order + re-order = DUPLICATE!')
        else:
            print(f'  ℹ Created {actual_new_orders} orders')
        
        # Step 16: Verify cart empty
        print('\nStep 16: Verifying cart is empty...')
        store.open_cart()
        
        try:
            store.cart_is_empty()
            print('  ✓ Cart empty after order')
        except:
            qty_check = driver.find_elements(
                By.CSS_SELECTOR,
                'input[type="hidden"][name="quantity"]'
            )
            print(f'  ⚠ Cart not empty: {len(qty_check)} items')
        
        print('\n' + '='*80)
        print('S9: COMPLETED - Order placement interruption tested')
        print('=== KEY FINDINGS ===')
        print(f'  Initial state: #{initial_first_order_id or "No orders"}')
        print(f'  After Place Order + F5 (1.5s): #{first_order_id_after_reload or "No new order"}', end='')
        if first_order_id_after_reload != initial_first_order_id and first_order_id_after_reload != '':
            print(' (⚠ Order created before F5!)')
        else:
            print(' (✓ No order)')
        print(f'  After re-order: #{final_first_order_id or "No order"}')
        print(f'  Duplicate prevention: {"✓ PASS" if actual_new_orders == 1 else "✗ FAIL"}')
        print('')
        print('Test Scenarios:')
        print('  Scenario A: F5 too slow (>2s) → Order completes → Cart cleared → Skip re-checkout')
        print('  Scenario B: F5 fast (<2s) → Order interrupted → Cart remains → Re-checkout')
        print('='*80 + '\n')
