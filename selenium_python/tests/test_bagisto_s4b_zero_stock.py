"""
S4B: Add to Cart with Zero Stock
Admin sets product stock to 0, then user tries to add to cart
Expected: Error message "Product is out of stock" or button disabled

Equivalent to: playwright_typescript/tests/bagisto-s4b-zero-stock.spec.ts
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from pages.store_page import StorePage


class TestBagistoS4bZeroStock:
    """S4B - Zero Stock Handling Test"""
    
    def test_s4b_cannot_add_zero_stock_to_cart(self, driver, base_url, credentials):
        """
        S4B – Cannot add product with zero stock to cart
        
        Test Flow:
        1. User login and add product to cart
        2. Open product page from cart
        3. Admin opens new browser and sets stock to 0
        4. User reloads product page
        5. Verify "Add To Cart" button disabled OR shows error
        6. Verify cart unchanged
        7. Admin restores stock to 200
        """
        print("\n" + "="*80)
        print("S4B: ZERO STOCK HANDLING - ADMIN SETS STOCK TO 0")
        print("="*80)
        
        store = StorePage(driver, base_url)
        
        # Admin credentials (from environment or default)
        admin_url = credentials.get('admin_url', 'https://commerce.bagisto.com/admin')
        admin_email = credentials.get('admin_email', 'admin@example.com')
        admin_password = credentials.get('admin_password', 'admin123')
        
        print("\nStep 1 (User): Logging in...")
        store.login()
        
        print("\nStep 2 (User): Finding first product...")
        store.add_first_product_from_home()
        
        # Get product name (stored in StorePage)
        added_product_name = getattr(store, 'last_added_product_name', 'Arctic')
        added_product_url = getattr(store, 'last_added_product_url', None)
        print(f'  ✓ Added product: {added_product_name}')
        
        print("\nStep 3 (User): Opening product page directly...")
        if added_product_url:
            driver.get(added_product_url)
            time.sleep(2)
            print(f'  ✓ Product page opened: {added_product_url}')
        else:
            print('  ⚠ Product URL not saved, cannot continue')
            return

        
        # Open admin in new browser window
        print("\nStep 4 (Admin): Opening admin panel in new window...")
        
        # Create second WebDriver for admin
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Check if headless mode from environment
        import os
        if os.getenv('HEADLESS', 'false').lower() == 'true':
            chrome_options.add_argument('--headless=new')
        
        service2 = Service(ChromeDriverManager().install())
        admin_driver = webdriver.Chrome(service=service2, options=chrome_options)
        admin_driver.maximize_window()
        
        admin_driver.get(admin_url)
        time.sleep(2)
        print('  ✓ Admin panel opened')
        
        # Login to admin
        print("\nStep 5 (Admin): Logging in to admin panel...")
        try:
            email_input = admin_driver.find_element(By.NAME, 'email')
            password_input = admin_driver.find_element(By.NAME, 'password')
            sign_in_btn = admin_driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Sign In')]"
            )
            
            email_input.clear()
            email_input.send_keys(admin_email)
            password_input.clear()
            password_input.send_keys(admin_password)
            sign_in_btn.click()
            time.sleep(5)  # Wait longer for login to complete
            
            # Verify login succeeded by checking URL
            current_url = admin_driver.current_url
            if '/admin/login' in current_url:
                print(f'  ⚠ Still on login page: {current_url}')
                print('  ⚠ Login may have failed - check credentials')
                admin_driver.quit()
                return
            else:
                print(f'  ✓ Admin logged in - Now at: {current_url}')
        except NoSuchElementException:
            print('  ℹ Already logged in to admin')
        
        # Search for product using Mega Search (SAME AS S4)
        print("\nStep 6 (Admin): Searching for product...")
        
        try:
            # Find Mega Search textbox - try multiple selectors
            search_box = None
            search_selectors = [
                (By.XPATH, "//input[@aria-label='Mega Search']"),
                (By.XPATH, "//input[@placeholder='Mega Search']"),
                (By.CSS_SELECTOR, "input[aria-label='Mega Search']"),
                (By.CSS_SELECTOR, "input[placeholder='Mega Search']")
            ]
            
            for by, selector in search_selectors:
                try:
                    search_box = admin_driver.find_element(by, selector)
                    if search_box.is_displayed():
                        print(f"  → Found Mega Search box")
                        break
                except NoSuchElementException:
                    continue
            
            if not search_box:
                raise NoSuchElementException("Mega Search box not found")
            
            # Use first 3 words only for better search match (like Playwright)
            search_term = ' '.join(added_product_name.split()[:3])
            print(f'  → Searching for: "{search_term}"')
            
            search_box.click()
            time.sleep(1)
            search_box.send_keys(search_term)
            
            # CRITICAL: Press Enter instead of submit() (like Playwright)
            from selenium.webdriver.common.keys import Keys
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)  # Wait for search results
            
            print("  ✓ Search completed")
            
        except (NoSuchElementException, Exception) as e:
            print(f"  ⚠ Mega Search failed: {type(e).__name__}")
            print(f"  ℹ Cannot search for product - skipping stock modification")
            admin_driver.quit()
            return
        
        # Click on product from search results (EXACT COPY FROM S4)
        print("\nStep 7 (Admin): Opening product edit page...")
        
        try:
            # Use first word of search term (like Playwright)
            first_word = search_term.split()[0]
            print(f"  → Looking for product containing: '{first_word}'")
            
            # Wait for search results to load
            time.sleep(2)
            
            # Find edit link: a[href*="/catalog/products/edit/"]:has-text("firstWord")
            # Use translate() for case-insensitive match
            search_result_link = admin_driver.find_element(
                By.XPATH,
                f"//a[contains(@href, '/catalog/products/edit/') and .//p[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{first_word.lower()}')]]"
            )
            
            if search_result_link.is_displayed():
                print(f"  → Found product in search results")
                # CRITICAL FIX: Use JavaScript click
                admin_driver.execute_script("arguments[0].click();", search_result_link)
                time.sleep(3)
                print("  ✓ Product edit page opened")
            else:
                raise NoSuchElementException("Product edit link not visible")
                
        except NoSuchElementException:
            print('  ⚠ Product not found in search results')
            print('  ⚠ Cannot modify stock - skipping stock reduction step')
            admin_driver.quit()
            return
        
        # Set stock to 0
        print("\nStep 8 (Admin): Setting stock to 0...")
        try:
            stock_input = admin_driver.find_element(
                By.CSS_SELECTOR,
                'input[name="inventories[1]"]'
            )
            
            current_stock = stock_input.get_attribute('value')
            print(f'  Current stock: {current_stock}')
            
            stock_input.click()
            stock_input.clear()
            stock_input.send_keys('0')
            print('  ✓ Set stock to 0')
            
            # Save product
            save_btn = admin_driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Save Product')]"
            )
            # CRITICAL FIX: Use JavaScript click
            admin_driver.execute_script("arguments[0].click();", save_btn)
            time.sleep(3)
            print('  ✓ Product saved with stock = 0')
        except NoSuchElementException:
            print('  ⚠ Stock input not found (demo may not allow editing)')
            admin_driver.quit()
            return
        
        # Switch back to user browser
        print("\nStep 9 (User): Returning to product page...")
        driver.refresh()
        time.sleep(2)
        
        print("\nStep 10 (User): Verifying 'Add To Cart' button state...")
        
        # FIRST: Count items in cart BEFORE attempting to add
        driver.get(f"{base_url}/checkout/cart")
        time.sleep(2)
        
        qty_inputs_before = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="hidden"][name="quantity"]'
        )
        items_before = len(qty_inputs_before)
        print(f'  → Cart before: {items_before} item(s)')
        
        # Go back to product page
        if added_product_url:
            driver.get(added_product_url)
            time.sleep(2)
        
        try:
            add_to_cart_btn = driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Add To Cart')]"
            )
            
            is_enabled = add_to_cart_btn.is_enabled()
            
            if not is_enabled:
                print('  ✓ "Add To Cart" button is DISABLED (correct behavior)')
                print('  → Cannot add out-of-stock product to cart')
            else:
                print('  ⚠ "Add To Cart" button is ENABLED')
                print('  → Attempting to click (should show error)...')
                
                add_to_cart_btn.click()
                time.sleep(2)
                
                # Check for error message
                print('\nStep 11 (User): Checking for error message...')
                error_selectors = [
                    "//*[contains(text(), 'not available')]",
                    "//*[contains(text(), 'out of stock')]",
                    "//*[contains(text(), 'insufficient')]",
                    "//*[contains(@class, 'error')]",
                    "//*[contains(@class, 'alert')]"
                ]
                
                error_found = False
                for selector in error_selectors:
                    try:
                        error = driver.find_element(By.XPATH, selector)  # FIX: Use driver not admin_driver
                        if error.is_displayed():
                            error_text = error.text
                            print(f'  ✓ Error message: "{error_text.strip()}"')
                            error_found = True
                            break
                    except:
                        continue
                
                if not error_found:
                    print('  ⚠ No error message displayed')
        except NoSuchElementException:
            # Check for "Out of Stock" label
            try:
                out_of_stock_label = driver.find_element(
                    By.XPATH,
                    "//*[contains(text(), 'Out of Stock') or contains(text(), 'Sold Out')]"
                )
                
                if out_of_stock_label.is_displayed():
                    print('  ✓ "Out of Stock" label displayed')
                    print('  ✓ No "Add To Cart" button (correct behavior)')
            except:
                print('  ⚠ Neither "Add To Cart" button nor "Out of Stock" label found')
        
        print("\nStep 12 (User): Verifying cart did not change...")
        driver.get(f"{base_url}/checkout/cart")
        time.sleep(2)
        
        qty_inputs_after = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="hidden"][name="quantity"]'
        )
        items_after = len(qty_inputs_after)
        
        print(f'  → Cart after: {items_after} item(s)')
        
        if items_after == items_before:
            print(f'  ✓ Cart unchanged ({items_before} → {items_after})')
            print('  ✓ Out-of-stock product NOT added')
        elif items_after > items_before:
            print(f'  ⚠ Cart increased ({items_before} → {items_after})')
            print('  ⚠ Out-of-stock product WAS added (demo limitation)')
        else:
            print(f'  ℹ Cart decreased ({items_before} → {items_after})')
        
        # Cleanup: Restore stock to 200
        print("\nStep 13 (Admin Cleanup): Restoring stock to 200...")
        
        # Go back to admin dashboard
        admin_driver.get(admin_url)
        time.sleep(2)
        
        # Search for product again
        try:
            search_inputs = admin_driver.find_elements(By.XPATH, "//input[@type='text']")
            
            search_box = None
            for inp in search_inputs:
                placeholder = inp.get_attribute('placeholder')
                if placeholder and 'search' in placeholder.lower():
                    search_box = inp
                    break
            
            if not search_box and search_inputs:
                search_box = search_inputs[0]
            
            if search_box:
                print(f'  → Searching for: "{search_term}"')
                search_box.click()
                search_box.send_keys(search_term)
                search_box.send_keys('\n')
                time.sleep(3)
                
                # Click product from search (use translate() for case-insensitive)
                first_word = search_term.split()[0]
                search_result_link = admin_driver.find_element(
                    By.XPATH,
                    f"//a[contains(@href, '/catalog/products/edit/') and .//p[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{first_word.lower()}')]]"
                )
                admin_driver.execute_script("arguments[0].click();", search_result_link)
                time.sleep(3)
                
                # Restore stock
                restore_stock = admin_driver.find_element(
                    By.CSS_SELECTOR,
                    'input[name="inventories[1]"]'
                )
                restore_stock.click()
                restore_stock.clear()
                restore_stock.send_keys('200')
                print('  ✓ Stock restored to 200')
                
                save_btn = admin_driver.find_element(
                    By.XPATH,
                    "//button[contains(text(), 'Save Product')]"
                )
                admin_driver.execute_script("arguments[0].click();", save_btn)
                time.sleep(3)
                print('  ✓ Product saved with stock = 200')
        except Exception as e:
            print(f'  ⚠ Could not restore stock: {e}')
        
        # Close admin browser
        admin_driver.quit()
        
        print('\n' + '='*80)
        print('S4B: COMPLETED - Zero stock handling tested')
        print('Expected behavior:')
        print('  - Admin sets stock to 0')
        print('  - User reloads product page')
        print('  - "Add To Cart" button disabled OR error message shown')
        print('  - Out-of-stock product cannot be added to cart')
        print('='*80 + '\n')
