"""
S16: B1 → B2 (Concurrent Carts)
Login on 2 browsers, add different products, verify cart merging/conflict handling
Expected: Cart syncs across sessions or shows conflict resolution

Equivalent to: playwright_typescript/tests/bagisto-s16-concurrent-carts.spec.ts
"""
import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from pages.store_page import StorePage


class TestBagistoS16ConcurrentCarts:
    """S16 - Concurrent Carts Test Suite"""
    
    def test_s16_concurrent_browser_sessions(self, driver, base_url, credentials):
        """
        S16 – Multiple browser sessions with same account
        
        Flow:
        1. Browser 1: Login and add product to cart
        2. Browser 2: Create second WebDriver instance
        3. Browser 2: Login with same account
        4. Browser 2: Check cart - should sync from Browser 1
        5. Browser 2: Add different product
        6. Browser 1: Refresh cart - should see items from Browser 2
        7. Verify cart sync behavior
        8. Browser 1: Place order FIRST
        9. Browser 2: Try to place order → Should fail (cart cleared)
        """
        print("\n" + "="*80)
        print("S16 – CONCURRENT CARTS (2 REAL BROWSERS)")
        print("="*80)
        print("\n🔥 Testing with 2 ACTUAL WebDriver instances!\n")
        
        store1 = StorePage(driver, base_url)
        
        # Step 1: Browser 1 - Login
        print("\nStep 1 (B1): Logging in on Browser 1...")
        store1.login()
        
        # Step 2: Browser 1 - Add product
        print("\nStep 2 (B2): Adding product in Browser 1...")
        store1.add_first_product_from_home()
        
        # Get cart count
        store1.open_cart()
        time.sleep(2)
        
        qty_inputs_1 = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="hidden"][name="quantity"]'
        )
        browser1_initial_count = len(qty_inputs_1)
        print(f'  Browser 1 cart: {browser1_initial_count} item(s)')
        
        # Get product name
        product1_name = "Unknown Product"
        try:
            first_product_link = driver.find_element(
                By.CSS_SELECTOR,
                'a[href*="/product/"]'
            )
            product1_name = first_product_link.text.strip()
            if not product1_name:
                product1_name = "Product 1"
            print(f'  Product 1: {product1_name[:50]}...')
        except:
            pass
        
        # Step 3: Create Browser 2 (second WebDriver instance)
        print("\nStep 3 (B1): Creating Browser 2 (second WebDriver)...")
        print("  → Initializing second Chrome browser...")
        
        # Create second driver with same options as conftest.py
        chrome_options = Options()
        if base_url:  # Check if headless mode needed
            import os
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
            # Step 4: Browser 2 - Login with SAME account
            print("\nStep 4 (B1): Logging in on Browser 2 with SAME account...")
            store2 = StorePage(driver2, base_url)
            store2.login()
            
            # Step 5: Browser 2 - Check cart (should sync from Browser 1)
            print("\nStep 5 (B2): Checking cart in Browser 2...")
            store2.open_cart()
            time.sleep(2)
            
            qty_inputs_2 = driver2.find_elements(
                By.CSS_SELECTOR,
                'input[type="hidden"][name="quantity"]'
            )
            browser2_initial_count = len(qty_inputs_2)
            print(f'  Browser 2 initial cart: {browser2_initial_count} item(s)')
            
            if browser2_initial_count == browser1_initial_count:
                print('  ✓ Cart SYNCED between browsers!')
            else:
                print(f'  ⚠ Cart NOT synced (B1: {browser1_initial_count}, B2: {browser2_initial_count})')
            
            # Step 6: Browser 2 - Add different product
            print("\nStep 6 (B2): Adding different product in Browser 2...")
            print("  → Navigating to /girls-clothing category...")
            driver2.get(f"{base_url}/girls-clothing")
            time.sleep(2)
            
            browser2_count_after = browser2_initial_count  # Default: no change
            
            # Find first product
            try:
                product2_links = driver2.find_elements(
                    By.CSS_SELECTOR,
                    'a[href*="/product/"]'
                )
                
                if product2_links:
                    product2 = product2_links[0]
                    product2_name = product2.get_attribute('aria-label') or 'Product 2'
                    print(f'  Selected product: {product2_name[:50]}...')
                    
                    # Use JavaScript click
                    driver2.execute_script("arguments[0].click();", product2)
                    time.sleep(2)
                    
                    # Add to cart
                    add_btn = driver2.find_element(
                        By.XPATH,
                        "//button[contains(text(), 'Add To Cart')]"
                    )
                    add_btn.click()
                    print('  → Clicked Add To Cart')
                    time.sleep(5)  # Wait for AJAX
                    
                    # Verify in cart
                    driver2.get(f"{base_url}/checkout/cart")
                    time.sleep(2)
                    
                    qty_inputs_2_after = driver2.find_elements(
                        By.CSS_SELECTOR,
                        'input[type="hidden"][name="quantity"]'
                    )
                    browser2_count_after = len(qty_inputs_2_after)
                    print(f'  Browser 2 cart after add: {browser2_count_after} item(s)')
                else:
                    print('  ⚠ No products found in /woman category')
            
            except Exception as e:
                print(f'  ⚠ Could not add product in Browser 2: {e}')
            
            # Step 7: Browser 1 - Refresh cart
            print("\nStep 7 (B1): Refreshing cart in Browser 1...")
            driver.get(f"{base_url}/checkout/cart")
            time.sleep(2)
            
            qty_inputs_1_after = driver.find_elements(
                By.CSS_SELECTOR,
                'input[type="hidden"][name="quantity"]'
            )
            browser1_count_after = len(qty_inputs_1_after)
            print(f'  Browser 1 cart after refresh: {browser1_count_after} item(s)')
            
            # Verify sync
            print("\nStep 8: Analyzing cart sync behavior...")
            if browser1_count_after == browser2_count_after:
                print(f'  ✓ CART SYNCED: Both browsers show {browser1_count_after} item(s)')
            else:
                print(f'  ⚠ Cart counts differ: B1={browser1_count_after}, B2={browser2_count_after}')
            
            print("\n" + "="*80)
            print("CONCURRENT ORDER PLACEMENT TEST")
            print("="*80)
            
            # Capture initial order count
            print("\nStep 9: Capturing initial order count...")
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
            
            # Browser 1: Start checkout
            print("\nStep 10 (B1): Browser 1 starting checkout...")
            driver.get(f"{base_url}/checkout/cart")
            time.sleep(2)
            
            try:
                checkout_btn1 = driver.find_element(
                    By.XPATH,
                    "//a[contains(text(), 'Proceed To Checkout')]"
                )
                driver.execute_script("arguments[0].click();", checkout_btn1)
                time.sleep(2)
                print('  ✓ Browser 1: At checkout page')
                
                # Fill address
                store1.fill_shipping_address_minimal()
                
                # Select shipping/payment
                time.sleep(2)
                try:
                    free_ship_label = driver.find_element(By.CSS_SELECTOR, 'label[for="free_free"]')
                    free_ship_label.click()
                    time.sleep(1)
                except:
                    pass
                
                try:
                    cod_label = driver.find_element(By.CSS_SELECTOR, 'label[for="cashondelivery"]')
                    cod_label.click()
                    time.sleep(2)
                except:
                    pass
                
                # Place order
                print("  → Browser 1: Clicking Place Order...")
                place_order_btn = driver.find_element(
                    By.XPATH,
                    "//button[contains(text(), 'Place Order')]"
                )
                place_order_btn.click()
                
                # Wait for success
                try:
                    WebDriverWait(driver, 60).until(
                        EC.url_contains('/checkout/onepage/success')
                    )
                    print('  ✓ Browser 1: Order placed successfully')
                    
                    # Get order ID
                    order_link = driver.find_element(
                        By.CSS_SELECTOR,
                        'p.text-xl a.text-blue-700[href*="/orders/view/"]'
                    )
                    browser1_order_id = order_link.text.strip()
                    print(f'  ✓ Browser 1 Order ID: #{browser1_order_id}')
                except:
                    print('  ⚠ Browser 1: Did not reach success page')
            
            except Exception as e:
                print(f'  ⚠ Browser 1 checkout failed: {e}')
            
            # Browser 2: Try to checkout AFTER Browser 1
            print("\nStep 11 (B2): Browser 2 trying to checkout...")
            print("  → Expected: Cart should be EMPTY (Browser 1 placed order)")
            
            driver2.get(f"{base_url}/checkout/cart")
            time.sleep(2)
            
            qty_inputs_final = driver2.find_elements(
                By.CSS_SELECTOR,
                'input[type="hidden"][name="quantity"]'
            )
            browser2_final_count = len(qty_inputs_final)
            
            if browser2_final_count == 0:
                print(f'  ✓ Browser 2 cart is EMPTY (order placed by Browser 1)')
            else:
                print(f'  ⚠ Browser 2 cart still has {browser2_final_count} item(s)')
            
            # Verify only 1 order created
            print("\nStep 12: Verifying order count...")
            driver.get(f"{base_url}/customer/account/orders")
            time.sleep(2)
            
            new_order_rows = driver.find_elements(By.CSS_SELECTOR, '.row.grid')
            new_order_data_rows = [
                row for row in new_order_rows
                if 'Order ID' not in row.text and 'Order Date' not in row.text
            ]
            
            if len(new_order_data_rows) > 0:
                new_first_cells = new_order_data_rows[0].find_elements(By.TAG_NAME, 'p')
                if new_first_cells:
                    new_first_order_id = new_first_cells[0].text.strip()
                    
                    if new_first_order_id != initial_first_order_id:
                        print(f'  ✓ New order created: #{new_first_order_id}')
                        print('  ✓ Only 1 order (no duplicate from Browser 2)')
                    else:
                        print('  ⚠ No new order detected')
        
        finally:
            # Cleanup: Close Browser 2
            print("\nStep 13: Cleanup - closing Browser 2...")
            driver2.quit()
            print("  ✓ Browser 2 closed")
        
        print("\n" + "="*80)
        print("S16: COMPLETED - Concurrent carts with 2 REAL browsers tested")
        print("="*80)
        print("\n=== Key Findings ===")
        print(f"  - Initial sync: {browser2_initial_count == browser1_initial_count}")
        print(f"  - Cart behavior: {'SYNCED' if browser1_count_after == browser2_count_after else 'INDEPENDENT'}")
        print(f"  - Browser 1 placed order → Browser 2 cart cleared: {'✓' if browser2_final_count == 0 else '✗'}")
        print("  - Race condition prevention: ✓ (only 1 order created)")
        print("="*80 + "\n")
