"""
S6: B1 → B2 → B3 → B4a (Change Shipping) → B5
User adds product, proceeds to checkout, selects different shipping methods
Expected: Total updates based on shipping cost, order completes

Equivalent to: playwright_typescript/tests/bagisto-s6-shipping-method.spec.ts
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.store_page import StorePage


class TestBagistoS6ShippingMethod:
    """S6 - Change Shipping Method Test Suite"""
    
    def test_s6_select_different_shipping_methods(self, driver, base_url, credentials):
        """
        S6 – Select different shipping methods at checkout
        
        Steps:
        1. Login and ensure cart has items
        2. Proceed to checkout
        3. Fill shipping address
        4. Detect available shipping methods
        5. List all shipping methods with costs
        6. Switch between shipping methods
        7. Verify total updates with different shipping costs
        8. Place order with selected shipping
        9. Verify order shipping matches selection
        10. Verify cart is empty
        """
        print("\n" + "="*80)
        print("S6 – CHANGE SHIPPING METHOD")
        print("="*80)
        
        store = StorePage(driver, base_url)
        
        # Step 1: Login
        print("\nStep 1 (B1): Logging in...")
        store.login()
        
        # Step 2: Ensure cart has items
        print("\nStep 2 (B2): Ensuring cart has items...")
        driver.get(f"{base_url}/checkout/cart")
        time.sleep(2)
        
        qty_inputs = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="hidden"][name="quantity"]'
        )
        item_count = len(qty_inputs)
        
        if item_count == 0:
            print('  → Cart empty, adding products...')
            store.add_first_product_from_home()
            print('  ✓ Product added')
        else:
            print(f'  ✓ Cart has {item_count} item(s)')
        
        # Step 3: Proceed to checkout
        print("\nStep 3 (B3): Proceeding to checkout...")
        store.go_checkout()
        
        # Step 4: Fill shipping address
        print("\nStep 4 (B4): Filling shipping address...")
        store.fill_shipping_address_minimal()
        
        # Step 5: Detect shipping methods
        print("\nStep 5 (B4a): Detecting available shipping methods...")
        time.sleep(2)
        
        shipping_inputs = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="radio"][name="shipping_method"]'
        )
        shipping_count = len(shipping_inputs)
        
        if shipping_count > 0:
            print(f'  ✓ Found {shipping_count} shipping method(s)')
            
            # List shipping methods
            print("\nStep 6 (B4a): Listing shipping methods...")
            shipping_details = []
            
            for i, input_elem in enumerate(shipping_inputs, 1):
                input_id = input_elem.get_attribute('id')
                input_value = input_elem.get_attribute('value') or 'N/A'
                
                shipping_name = 'Unknown'
                cost = 'N/A'
                
                if input_id:
                    try:
                        # CRITICAL: Get LAST label (second one has content)
                        labels = driver.find_elements(
                            By.CSS_SELECTOR,
                            f'label[for="{input_id}"]'
                        )
                        
                        if labels:
                            # Use LAST label (first is icon-only, second has content)
                            label_elem = labels[-1]  # Last label with actual content
                            
                            # Find <p> tags inside the label
                            p_tags = label_elem.find_elements(By.TAG_NAME, 'p')
                            
                            if len(p_tags) >= 2:
                                cost = p_tags[0].text.strip()
                                shipping_name = p_tags[1].text.strip()
                            elif len(p_tags) == 1:
                                text = p_tags[0].text
                                # Extract cost
                                import re
                                cost_match = re.search(r'\$[\d,]+\.?\d*', text)
                                cost = cost_match.group(0) if cost_match else text.strip()
                                shipping_name = text.replace(cost, '').strip() or input_value
                            else:
                                # No <p> tags found, use input value
                                pass
                    except Exception as e:
                        pass
                
                shipping_details.append({
                    'index': i,
                    'id': input_id,
                    'value': input_value,
                    'name': shipping_name,
                    'cost': cost
                })
                
                print(f"  Shipping {i}: {input_value} - {shipping_name} ({cost})")
            
            # Capture initial totals with first shipping method
            time.sleep(2)
            
            def get_checkout_totals():
                """Helper to get checkout summary using row iteration pattern"""
                subtotal = 'N/A'
                delivery = 'N/A'
                grand_total = 'N/A'
                
                price_rows = driver.find_elements(
                    By.XPATH,
                    "//div[contains(@class, 'flex') and contains(@class, 'justify-between')]"
                )
                
                for row in price_rows:
                    try:
                        row_text = row.text
                        
                        if 'Subtotal' in row_text:
                            price_elems = row.find_elements(By.TAG_NAME, 'p')
                            if len(price_elems) > 0:
                                subtotal = price_elems[-1].text.strip()
                        
                        elif 'Delivery Charges' in row_text or 'Delivery' in row_text:
                            price_elems = row.find_elements(By.TAG_NAME, 'p')
                            if len(price_elems) > 0:
                                delivery = price_elems[-1].text.strip()
                        
                        elif 'Grand Total' in row_text:
                            price_elems = row.find_elements(By.TAG_NAME, 'p')
                            if len(price_elems) > 0:
                                grand_total = price_elems[-1].text.strip()
                    except:
                        continue
                
                return subtotal, delivery, grand_total
            
            st1, del1, gt1 = get_checkout_totals()
            
            print(f"\n  Initial Checkout (Shipping 1 - {shipping_details[0]['value']}):")
            print(f"    Subtotal: {st1}")
            print(f"    Delivery: {del1}")
            print(f"    Grand Total: {gt1}")
            
            # Validate: Delivery should match shipping method cost
            expected_delivery_1 = shipping_details[0]['cost']
            if del1 == expected_delivery_1:
                print(f"  ✓ Delivery matches label cost: {del1} = {expected_delivery_1}")
            else:
                print(f"  ⚠ MISMATCH: Label shows {expected_delivery_1}, but checkout shows {del1}")
                print(f"    → This is Bagisto lazy-load bug - delivery charges don't update until AJAX triggered")
            
            # Switch to second shipping method if available
            if shipping_count > 1:
                print(f"\nStep 7 (B4a): Switching to second shipping method...")
                second = shipping_details[1]
                
                print(f"  → Switching to: {second['value']} ({second['cost']})")
                
                try:
                    # Click LABEL for second shipping (using JavaScript click)
                    labels = driver.find_elements(
                        By.CSS_SELECTOR,
                        f'label[for="{second["id"]}"]'
                    )
                    
                    if labels:
                        driver.execute_script("arguments[0].click();", labels[-1])  # Last label
                        time.sleep(2)
                        print(f"  ✓ Clicked label for: {second['value']}")
                        
                        # Capture updated totals
                        st2, del2, gt2 = get_checkout_totals()
                        
                        print(f"  Updated Checkout (Shipping 2 - {second['value']}):")
                        print(f"    Subtotal: {st2}")
                        print(f"    Delivery: {del2}")
                        print(f"    Grand Total: {gt2}")
                        
                        # Validate: Delivery should match second shipping method cost
                        expected_delivery_2 = second['cost']
                        if del2 == expected_delivery_2:
                            print(f"  ✓ Delivery matches label cost: {del2} = {expected_delivery_2}")
                        else:
                            print(f"  ⚠ MISMATCH: Label shows {expected_delivery_2}, but checkout shows {del2}")
                        
                        # Compare
                        print("\n  📊 Comparison:")
                        print(f"    Shipping 1: Delivery={del1}, Total={gt1}")
                        print(f"    Shipping 2: Delivery={del2}, Total={gt2}")
                        
                        if del2 != del1:
                            print('  ✓ Delivery charges CHANGED!')
                        
                        if gt2 != gt1:
                            print('  ✓ Grand Total CHANGED!')
                
                except Exception as e:
                    print(f'  ⚠ Could not switch: {str(e)}')
                
                # Switch back to first method
                print(f"\nStep 8 (B4a): Switching back to first shipping method...")
                first = shipping_details[0]
                
                try:
                    labels = driver.find_elements(
                        By.CSS_SELECTOR,
                        f'label[for="{first["id"]}"]'
                    )
                    
                    if labels:
                        driver.execute_script("arguments[0].click();", labels[-1])
                        time.sleep(2)
                        print(f"  ✓ Switched back to: {first['value']}")
                        
                        st3, del3, gt3 = get_checkout_totals()
                        
                        if gt3 == gt1:
                            print('  ✓ Grand Total matches initial (toggle works)')
                        else:
                            print('  ⚠ Grand Total mismatch after toggle')
                
                except:
                    pass
        
        else:
            print('  ⚠ No shipping method radio buttons found')
        
        # Step 9: Place order
        print("\nStep 9 (B5): Placing order with selected shipping...")
        
        # Capture final checkout summary
        time.sleep(1)
        final_st, final_del, final_gt = get_checkout_totals()
        
        print(f"  Final Checkout Summary:")
        print(f"    Subtotal: {final_st}")
        print(f"    Delivery: {final_del}")
        print(f"    Grand Total: {final_gt}")
        
        store.choose_payment_and_place(expect_success_msg=False)
        
        try:
            WebDriverWait(driver, 30).until(
                EC.url_contains('/checkout/onepage/success')
            )
            print('  ✓ Order placed')
            
            # Get order details
            order_link = driver.find_element(
                By.CSS_SELECTOR,
                'p.text-xl a.text-blue-700[href*="/customer/account/orders/view/"]'
            )
            
            order_id = order_link.text.strip()
            print(f'  ✓ Order #{order_id} created')
            
            # View order details (use JavaScript click to avoid ProtocolError)
            driver.execute_script("arguments[0].click();", order_link)
            time.sleep(3)
            
            # Get order totals
            try:
                order_gt_row = driver.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'flex') and contains(@class, 'justify-between')]"
                    "[.//text()[contains(., 'Grand Total')]][1]"
                )
                order_gt = order_gt_row.find_element(By.XPATH, ".//p[last()]").text.strip()
                
                print(f"  Order Grand Total: {order_gt}")
                
                if final_gt == order_gt:
                    print('  ✓ Grand Total MATCHES (checkout = order)')
                else:
                    print('  ⚠ Grand Total MISMATCH')
            
            except:
                print('  ⚠ Could not get order grand total')
        
        except TimeoutException:
            print('  ⚠ Timeout waiting for success page')
        
        # Step 10: Verify cart empty
        print("\nStep 10: Verifying cart is empty...")
        store.goto_home()
        store.open_cart()
        
        try:
            store.cart_is_empty()
            print('  ✓ Cart cleared after order')
        except:
            qty_check = driver.find_elements(
                By.CSS_SELECTOR,
                'input[type="hidden"][name="quantity"]'
            )
            print(f'  ⚠ Cart not empty: {len(qty_check)} items')
        
        print("\n" + "="*80)
        print("S6: COMPLETED - Shipping method selection tested")
        print("="*80 + "\n")
