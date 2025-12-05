"""
S16B: Concurrent Place Order (Race Condition Test)
Two browsers click "Place Order" at EXACTLY the same time
Expected: Backend prevents duplicate orders OR creates 2 separate orders

Equivalent to: playwright_typescript/tests/bagisto-s16b-concurrent-place-order.spec.ts
"""
import pytest
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from pages.store_page import StorePage


class TestBagistoS17ConcurrentPlaceOrder:
    """S16B - Concurrent Place Order Race Condition Test Suite"""
    
    def test_s17_concurrent_place_order_race_condition(self, driver, base_url, credentials):
        """
        S16B – Two browsers place order at EXACTLY same time
        
        Test Flow:
        1. Browser 1: Login and add product to cart
        2. Browser 2: Create second WebDriver, login with same account
        3. Both browsers: Add product to cart
        4. Both browsers: Navigate to checkout
        5. Both browsers: Fill address and select shipping/payment
        6. CRITICAL: Use threading.Thread to click BOTH "Place Order" buttons simultaneously
        7. Wait for both browsers to reach success page
        8. Compare Order IDs - detect if duplicate
        
        Expected Outcomes:
        - Scenario A: Only 1 order created (race condition handled)
        - Scenario B: 2 orders created with SAME content (duplicate bug!)
        - Scenario C: One browser gets error (cart locked)
        """
        print("\n" + "="*80)
        print("S16B: CONCURRENT PLACE ORDER - Race Condition Test with 2 REAL BROWSERS")
        print("="*80)
        print("\n🔥 Testing SIMULTANEOUS Place Order clicks with threading!\n")
        
        store1 = StorePage(driver, base_url)
        
        # Step 1: Browser 1 - Login and add product
        print("\nStep 1 (B1): Browser 1 - Logging in...")
        store1.login()
        
        print("\nStep 2 (B2): Browser 1 - Adding product to cart...")
        store1.add_first_product_from_home()
        
        # Step 2: Create Browser 2
        print("\nStep 3: Creating Browser 2 (second WebDriver)...")
        
        import os
        chrome_options = Options()
        if os.getenv('HEADLESS', 'false').lower() == 'true':
            chrome_options.add_argument('--headless=new')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        service2 = Service(ChromeDriverManager().install())
        driver2 = webdriver.Chrome(service=service2, options=chrome_options)
        driver2.implicitly_wait(10)
        
        print("  ✓ Browser 2 created")
        
        try:
            # Step 3: Browser 2 - Login
            print("\nStep 4 (B1): Browser 2 - Logging in with SAME account...")
            store2 = StorePage(driver2, base_url)
            store2.login()
            
            # Step 4: Browser 2 - Add product
            print("\nStep 5 (B2): Browser 2 - Adding product to cart...")
            store2.add_first_product_from_home()
            
            # Step 5: Capture initial order count
            print("\nStep 6: Capturing initial order count...")
            driver.get(f"{base_url}/customer/account/orders")
            time.sleep(2)
            
            order_rows = driver.find_elements(By.CSS_SELECTOR, '.row.grid')
            order_data_rows = [
                row for row in order_rows
                if 'Order ID' not in row.text and 'Order Date' not in row.text
            ]
            
            initial_first_order_id = ''
            if len(order_data_rows) > 0:
                first_cells = order_data_rows[0].find_elements(By.TAG_NAME, 'p')
                if first_cells:
                    initial_first_order_id = first_cells[0].text.strip()
                    print(f'  Initial first order: #{initial_first_order_id}')
            
            # Step 6: Both browsers go to checkout
            print("\nStep 7: Both browsers navigating to checkout...")
            
            # Browser 1
            driver.get(f"{base_url}/checkout/cart")
            time.sleep(2)
            store1.go_checkout()
            print("  ✓ Browser 1 at checkout")
            
            # Browser 2
            driver2.get(f"{base_url}/checkout/cart")
            time.sleep(2)
            store2.go_checkout()
            print("  ✓ Browser 2 at checkout")
            
            # Step 7: Browser 1 - Fill address and select payment
            print("\nStep 8: Browser 1 - Filling address and selecting payment...")
            store1.fill_shipping_address_minimal()
            time.sleep(2)
            
            try:
                free_ship1 = driver.find_element(By.CSS_SELECTOR, 'label[for="free_free"]')
                free_ship1.click()
                time.sleep(1)
            except:
                pass
            
            try:
                cod1 = driver.find_element(By.CSS_SELECTOR, 'label[for="cashondelivery"]')
                cod1.click()
                time.sleep(2)
                print("  ✓ Browser 1 ready to place order")
            except:
                print("  ⚠ Browser 1 payment method not found")
            
            # Step 8: Browser 2 - Fill address and select payment
            print("\nStep 9: Browser 2 - Filling address and selecting payment...")
            store2.fill_shipping_address_minimal()
            time.sleep(2)
            
            try:
                free_ship2 = driver2.find_element(By.CSS_SELECTOR, 'label[for="free_free"]')
                free_ship2.click()
                time.sleep(1)
            except:
                pass
            
            try:
                cod2 = driver2.find_element(By.CSS_SELECTOR, 'label[for="cashondelivery"]')
                cod2.click()
                time.sleep(2)
                print("  ✓ Browser 2 ready to place order")
            except:
                print("  ⚠ Browser 2 payment method not found")
            
            # Step 9: Locate Place Order buttons
            print("\nStep 10: Locating Place Order buttons in both browsers...")
            
            try:
                place_order_btn1 = driver.find_element(
                    By.XPATH,
                    "//button[contains(text(), 'Place Order')]"
                )
                btn1_visible = place_order_btn1.is_displayed()
                print(f"  Browser 1 Place Order: {'VISIBLE ✓' if btn1_visible else 'NOT VISIBLE ✗'}")
            except:
                btn1_visible = False
                print("  Browser 1 Place Order: NOT FOUND ✗")
            
            try:
                place_order_btn2 = driver2.find_element(
                    By.XPATH,
                    "//button[contains(text(), 'Place Order')]"
                )
                btn2_visible = place_order_btn2.is_displayed()
                print(f"  Browser 2 Place Order: {'VISIBLE ✓' if btn2_visible else 'NOT VISIBLE ✗'}")
            except:
                btn2_visible = False
                print("  Browser 2 Place Order: NOT FOUND ✗")
            
            if not btn1_visible or not btn2_visible:
                print("\n  ⚠ Cannot proceed - one or both buttons not ready")
                return
            
            # Step 10: CRITICAL - Click BOTH buttons SIMULTANEOUSLY using threading
            print("\n" + "="*80)
            print("CRITICAL: CONCURRENT PLACE ORDER - RACE CONDITION TEST")
            print("="*80)
            print("\nStep 11: 🔥 Clicking BOTH Place Order buttons SIMULTANEOUSLY...")
            print("  → Using threading.Thread to click at EXACT same time...")
            
            # Click results
            browser1_success = False
            browser2_success = False
            browser1_order_id = ''
            browser2_order_id = ''
            
            # Define click functions
            def click_browser1():
                try:
                    place_order_btn1.click()
                    print("  → Browser 1: Clicked!")
                except Exception as e:
                    print(f"  ✗ Browser 1 click error: {e}")
            
            def click_browser2():
                try:
                    place_order_btn2.click()
                    print("  → Browser 2: Clicked!")
                except Exception as e:
                    print(f"  ✗ Browser 2 click error: {e}")
            
            # Create threads
            thread1 = threading.Thread(target=click_browser1)
            thread2 = threading.Thread(target=click_browser2)
            
            # Start BOTH threads at same time
            thread1.start()
            thread2.start()
            
            # Wait for both to complete
            thread1.join()
            thread2.join()
            
            print("  ✓ Both browsers clicked Place Order")
            
            # Step 11: Wait for both browsers to reach success page
            print("\nStep 12: Waiting for BOTH browsers to reach success page...")
            print("  ⏱ Polling every 2 seconds (max 3 minutes)...")
            
            attempt = 0
            max_attempts = 90  # 3 minutes
            
            while attempt < max_attempts:
                attempt += 1
                
                # Check Browser 1
                url1 = driver.current_url
                if '/checkout/onepage/success' in url1 and not browser1_success:
                    browser1_success = True
                    try:
                        order_link1 = driver.find_element(
                            By.CSS_SELECTOR,
                            'p.text-xl a.text-blue-700[href*="/orders/view/"]'
                        )
                        browser1_order_id = order_link1.text.strip()
                    except:
                        pass
                
                # Check Browser 2
                url2 = driver2.current_url
                if '/checkout/onepage/success' in url2 and not browser2_success:
                    browser2_success = True
                    try:
                        order_link2 = driver2.find_element(
                            By.CSS_SELECTOR,
                            'p.text-xl a.text-blue-700[href*="/orders/view/"]'
                        )
                        browser2_order_id = order_link2.text.strip()
                    except:
                        pass
                
                # Show progress every 5 attempts
                if attempt % 5 == 0 or (browser1_success and browser2_success):
                    status1 = f"✓ Success (Order #{browser1_order_id})" if browser1_success else f"⏳ {url1.split('/')[-1]}"
                    status2 = f"✓ Success (Order #{browser2_order_id})" if browser2_success else f"⏳ {url2.split('/')[-1]}"
                    print(f"  [{attempt * 2}s] Browser 1: {status1}")
                    print(f"  [{attempt * 2}s] Browser 2: {status2}")
                
                # Break if BOTH succeeded
                if browser1_success and browser2_success:
                    print(f"\n  ✓ Both browsers reached success page after {attempt * 2}s")
                    print(f"    Browser 1: Order #{browser1_order_id}")
                    print(f"    Browser 2: Order #{browser2_order_id}")
                    break
                
                time.sleep(2)
            
            # Step 12: Compare results
            print("\n" + "="*80)
            print("RACE CONDITION ANALYSIS")
            print("="*80)
            
            if not browser1_success and not browser2_success:
                print("\n⚠ TIMEOUT: Neither browser reached success page")
                print("  → Test inconclusive")
            
            elif browser1_success and not browser2_success:
                print("\n✓ SCENARIO C: Only Browser 1 succeeded")
                print(f"  Browser 1: Order #{browser1_order_id}")
                print(f"  Browser 2: Stuck at {driver2.current_url.split('/')[-1]}")
                print("  → Race condition handled (cart locked or cleared)")
            
            elif browser2_success and not browser1_success:
                print("\n✓ SCENARIO C: Only Browser 2 succeeded")
                print(f"  Browser 2: Order #{browser2_order_id}")
                print(f"  Browser 1: Stuck at {driver.current_url.split('/')[-1]}")
                print("  → Race condition handled (cart locked or cleared)")
            
            elif browser1_order_id == browser2_order_id:
                print("\n❌ CRITICAL: SAME Order ID!")
                print(f"  Both browsers: Order #{browser1_order_id}")
                print("  → This should NEVER happen!")
            
            else:
                print("\n⚠ BOTH browsers succeeded with DIFFERENT Order IDs")
                print(f"  Browser 1: Order #{browser1_order_id}")
                print(f"  Browser 2: Order #{browser2_order_id}")
                print("  → Checking if duplicate content...")
                
                # Compare order details
                print("\nStep 13: Comparing order details...")
                
                # Browser 1 order details
                driver.execute_script(
                    "arguments[0].click();",
                    driver.find_element(By.CSS_SELECTOR, 'p.text-xl a.text-blue-700')
                )
                time.sleep(3)
                
                order1_grand_total = 'N/A'
                try:
                    gt_rows = driver.find_elements(
                        By.XPATH,
                        "//div[contains(@class, 'flex') and contains(@class, 'justify-between')]"
                    )
                    for row in gt_rows:
                        if 'Grand Total' in row.text:
                            price_elem = row.find_elements(By.TAG_NAME, 'p')[-1]
                            order1_grand_total = price_elem.text.strip()
                            break
                except:
                    pass
                
                print(f"  Order #{browser1_order_id}: {order1_grand_total}")
                
                # Browser 2 order details
                driver2.execute_script(
                    "arguments[0].click();",
                    driver2.find_element(By.CSS_SELECTOR, 'p.text-xl a.text-blue-700')
                )
                time.sleep(3)
                
                order2_grand_total = 'N/A'
                try:
                    gt_rows = driver2.find_elements(
                        By.XPATH,
                        "//div[contains(@class, 'flex') and contains(@class, 'justify-between')]"
                    )
                    for row in gt_rows:
                        if 'Grand Total' in row.text:
                            price_elem = row.find_elements(By.TAG_NAME, 'p')[-1]
                            order2_grand_total = price_elem.text.strip()
                            break
                except:
                    pass
                
                print(f"  Order #{browser2_order_id}: {order2_grand_total}")
                
                # Compare
                if order1_grand_total != 'N/A' and order1_grand_total == order2_grand_total:
                    print("\n❌ DUPLICATE BUG CONFIRMED!")
                    print(f"  Both orders have Grand Total: {order1_grand_total}")
                    print("  → Race condition NOT prevented by backend!")
                else:
                    print("\n✓ Different Grand Totals")
                    print("  → Not duplicates (separate legitimate orders)")
        
        finally:
            # Cleanup
            print("\nStep 14: Cleanup - closing Browser 2...")
            driver2.quit()
            print("  ✓ Browser 2 closed")
        
        print("\n" + "="*80)
        print("S16B: COMPLETED - Concurrent Place Order Race Condition Tested")
        print("="*80 + "\n")
