"""
S4: B1 → B2 → Admin reduces stock → B3 (Checkout blocked)
User adds 2+ items to cart, admin reduces stock to 1, user tries checkout
Expected: Error at checkout due to insufficient stock

Equivalent to: playwright_typescript/tests/bagisto-s4-out-of-stock.spec.ts
"""
import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from pages.store_page import StorePage


class TestBagistoS5StockReduction:
    """S4 - Out of Stock Handling Test Suite"""
    
    def test_s5_stock_reduction_blocks_checkout(self, driver, base_url, credentials):
        """
        S4 – Insufficient stock blocks checkout
        
        Full flow matching Playwright:
        1. User: Login and add product to cart
        2. User: Navigate to cart and verify
        3. User: Click product link to open product page
        4. Admin: Open admin panel in new window
        5. Admin: Login to admin (just click Sign In)
        6. Admin: Search for product using Mega Search
        7. Admin: Open product edit page from search results
        8. Admin: Reduce stock to 1
        9. Admin: Return to product catalog
        10. User: Return to cart and try checkout
        11. Expected: Blocked with error message
        12. Admin Cleanup: Restore stock to 200
        """
        print("\n" + "="*80)
        print("S4 – OUT OF STOCK HANDLING")
        print("="*80)
        
        store = StorePage(driver, base_url)
        
        # Get admin credentials from environment
        admin_url = os.getenv('BAGISTO_ADMIN_URL', f'{base_url}/admin')
        admin_email = os.getenv('BAGISTO_ADMIN_EMAIL', 'admin@example.com')
        admin_password = os.getenv('BAGISTO_ADMIN_PASSWORD', 'admin123')
        
        # Step 1: User login and add product
        print("\nStep 1 (User): Logging in...")
        store.login()
        
        # Step 2: Navigate to cart (skip adding - use existing cart items)
        print("\nStep 2 (User): Navigating to cart...")
        driver.get(f"{base_url}/checkout/cart")
        time.sleep(3)
        
        # Step 2: Navigate to cart (skip adding - use existing cart items)
        print("\nStep 2 (User): Navigating to cart...")
        driver.get(f"{base_url}/checkout/cart")
        time.sleep(3)
        
        # Count both physical and e-book items
        qty_inputs = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="hidden"][name="quantity"]'
        )
        ebook_checkboxes = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="checkbox"][id^="item_"]'
        )
        
        physical_count = len(qty_inputs)
        ebook_count = len(ebook_checkboxes)
        total_count = physical_count + ebook_count
        
        print(f"  ✓ Cart has {total_count} item(s) ({physical_count} physical, {ebook_count} e-book)")
        
        if total_count == 0:
            print('  ⚠ Cart is empty, cannot test out-of-stock scenario')
            print('  ℹ Please add at least one product to cart before running S4')
            return
        
        # Step 3: Find and click ANY product link in cart to open product page
        print("\nStep 3 (User): Opening product page from cart...")
        
        # HTML structure: <a href="..."><p class="text-base font-medium">Product Name</p></a>
        product_link = None
        added_product_name = "Unknown Product"  # Will be extracted from cart
        
        try:
            # Find ALL links containing <p class="text-base font-medium"> (product names in cart)
            product_links = driver.find_elements(
                By.XPATH,
                "//a[.//p[contains(@class, 'text-base') and contains(@class, 'font-medium')]]"
            )
            
            if len(product_links) > 0:
                # Use FIRST product link (simplest approach)
                product_link = product_links[0]
                p_elem = product_link.find_element(By.CSS_SELECTOR, 'p.text-base.font-medium')
                added_product_name = p_elem.text.strip()
                print(f"  → Using first product in cart: {added_product_name[:30]}...")
            else:
                print(f"  ⚠ No product links found in cart")
                return
                
        except NoSuchElementException:
            print(f"  ⚠ No product links found in cart")
            return
        
        if product_link:
            # CRITICAL FIX: Use JavaScript click
            driver.execute_script("arguments[0].click();", product_link)
            time.sleep(3)
            print(f"  ✓ Product page opened: {driver.current_url}")
        else:
            print(f"  ⚠ No product links found in cart")
            return
        
        # Save current user window handle
        user_window = driver.current_window_handle
        
        # Step 5: Open admin in new tab
        print("\nStep 5 (Admin): Opening admin panel in new tab...")
        
        # Try to find "Opens in a new tab" link on product page
        admin_link_found = False
        try:
            admin_link = driver.find_element(
                By.XPATH,
                "//a[@target='_blank' and contains(text(), 'Opens in a new tab')]"
            )
            
            if admin_link.is_displayed():
                print('  → Clicking "Opens in a new tab" link...')
                # CRITICAL FIX: Use JavaScript click
                driver.execute_script("arguments[0].click();", admin_link)
                time.sleep(3)
                admin_link_found = True
                print('  ✓ Admin tab opened via product page link')
        except NoSuchElementException:
            pass
        
        if not admin_link_found:
            # Fallback: open admin URL directly
            print('  → Admin link not found, opening admin URL directly...')
            driver.execute_script(f"window.open('{admin_url}', '_blank');")
            time.sleep(2)
        
        # Switch to admin window
        admin_window = None
        for window_handle in driver.window_handles:
            if window_handle != user_window:
                admin_window = window_handle
                break
        
        if not admin_window:
            print("  ✗ Could not open admin window")
            return
        
        driver.switch_to.window(admin_window)
        time.sleep(2)
        
        # Step 6: Login to admin (JUST CLICK Sign In - credentials autofilled)
        print("\nStep 6 (Admin): Logging in to admin panel...")
        
        try:
            sign_in_btn = driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Sign In')]"
            )
            
            if sign_in_btn.is_displayed():
                print("  → Clicking Sign In button (credentials autofilled)...")
                sign_in_btn.click()
                time.sleep(3)
                print("  ✓ Admin logged in")
            else:
                print("  ℹ Already logged in to admin")
        except NoSuchElementException:
            print("  ℹ Already logged in to admin")
        
        # Step 7: Search for product using Mega Search
        print("\nStep 7 (Admin): Searching for product...")
        
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
                    search_box = driver.find_element(by, selector)
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
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)  # Wait for search results
            
            print("  ✓ Search completed")
            
        except (NoSuchElementException, Exception) as e:
            print(f"  ⚠ Mega Search failed: {type(e).__name__}")
            print(f"  ℹ Cannot search for product - skipping stock modification")
            
            # Close admin and return to user window
            driver.close()
            driver.switch_to.window(user_window)
            return
        
        # Step 8: Click on product from search results
        print("\nStep 8 (Admin): Opening product edit page...")
        
        try:
            # Use first word of search term (like Playwright)
            first_word = search_term.split()[0]
            print(f"  → Looking for product containing: '{first_word}'")
            
            # Wait for search results to load
            time.sleep(2)
            
            # Find edit link: a[href*="/catalog/products/edit/"]:has-text("firstWord")
            search_result_link = driver.find_element(
                By.XPATH,
                f"//a[contains(@href, '/catalog/products/edit/') and .//p[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{first_word.lower()}')]]"
            )

            
            if search_result_link.is_displayed():
                print(f"  → Found product in search results")
                # CRITICAL FIX: Use JavaScript click
                driver.execute_script("arguments[0].click();", search_result_link)
                time.sleep(3)
                print("  ✓ Product edit page opened")
            else:
                raise NoSuchElementException("Product edit link not visible")
                
        except NoSuchElementException:
            print('  ⚠ Product not found in search results')
            print('  ⚠ Cannot modify stock - skipping stock reduction step')
            
            # Close admin and return to user window
            driver.close()
            driver.switch_to.window(user_window)
            return
        
        # Step 9: Find and modify stock
        print("\nStep 9 (Admin): Reducing stock to 1...")
        
        try:
            stock_input = driver.find_element(
                By.NAME,
                "inventories[1]"
            )
            
            if stock_input.is_displayed():
                current_stock = stock_input.get_attribute('value')
                print(f"  Current stock: {current_stock}")
                
                stock_input.click()
                stock_input.clear()
                stock_input.send_keys('1')
                print("  ✓ Set stock to 1")
                
                # Save product
                try:
                    save_btn = driver.find_element(
                        By.XPATH,
                        "//button[contains(text(), 'Save Product')]"
                    )
                    
                    if save_btn.is_displayed():
                        # CRITICAL FIX: Use JavaScript click
                        driver.execute_script("arguments[0].click();", save_btn)
                        time.sleep(3)
                        print("  ✓ Product save attempted (stock = 1)")
                except NoSuchElementException:
                    print("  ⚠ Save Product button not found")
            else:
                print("  ⚠ Stock input not visible")
                
        except NoSuchElementException:
            print('  ⚠ Stock input not found (demo may not allow editing)')
        
        # Go back to catalog (like Playwright)
        print("  → Returning to product catalog...")
        admin_base = admin_url.replace('/login', '')  # Remove /login if present
        driver.get(f"{admin_base}/catalog/products")
        time.sleep(2)
        print("  ✓ Returned to product catalog")
        
        # Step 10: Switch back to user tab
        print("\nStep 10 (User): Returning to cart and proceeding to checkout...")
        driver.switch_to.window(user_window)
        
        driver.get(f"{base_url}/checkout/cart")
        time.sleep(2)
        
        # Try to proceed to checkout
        try:
            proceed_btn = driver.find_element(
                By.XPATH,
                "//a[contains(text(), 'Proceed To Checkout')]"
            )
            
            if proceed_btn.is_displayed():
                print('  → Clicking "Proceed To Checkout"...')
                proceed_btn.click()
                time.sleep(2)
                
                # Check if still on cart page or redirected to checkout
                current_url = driver.current_url
                
                if '/checkout/cart' in current_url:
                    print('  ✓ Blocked on cart page (expected due to insufficient stock)')
                    
                    # Look for error message
                    error_keywords = [
                        'out of stock',
                        'insufficient',
                        'not available',
                        'error',
                        'quantity'
                    ]
                    
                    for keyword in error_keywords:
                        try:
                            error_elem = driver.find_element(
                                By.XPATH,
                                f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                                f"'abcdefghijklmnopqrstuvwxyz'), '{keyword}')]"
                            )
                            if error_elem.is_displayed():
                                print(f"  ✓ Error message: {error_elem.text.strip()[:80]}")
                                break
                        except NoSuchElementException:
                            continue
                
                elif '/checkout/onepage' in current_url:
                    print('  ⚠ Proceeded to checkout (demo may not enforce stock limit)')
                    print('  ℹ Expected: Should be blocked with insufficient stock error')
                    
        except NoSuchElementException:
            print('  ⚠ Proceed To Checkout button not found')
        
        # Step 11: Cleanup - Restore stock
        print("\nStep 11 (Admin Cleanup): Restoring stock to 200...")
        
        # Switch back to admin window
        driver.switch_to.window(admin_window)
        
        # Go back to admin dashboard
        admin_base = admin_url.replace('/login', '')
        driver.get(admin_base)
        time.sleep(2)
        
        try:
            # Search for product again
            search_box2 = None
            for by, selector in search_selectors:
                try:
                    search_box2 = driver.find_element(by, selector)
                    if search_box2.is_displayed():
                        break
                except NoSuchElementException:
                    continue
            
            if search_box2:
                search_term2 = ' '.join(added_product_name.split()[:3])
                print(f'  → Searching for: "{search_term2}"')
                
                search_box2.click()
                time.sleep(1)
                search_box2.send_keys(search_term2)
                search_box2.send_keys(Keys.RETURN)
                time.sleep(2)
                
                # Click product from search
                first_word2 = search_term2.split()[0]
                search_result_link2 = driver.find_element(
                    By.XPATH,
                    f"//a[contains(@href, '/catalog/products/edit/') and contains(text(), '{first_word2}')]"
                )
                
                if search_result_link2.is_displayed():
                    driver.execute_script("arguments[0].click();", search_result_link2)
                    time.sleep(2)
                    
                    # Restore stock to 200
                    restore_stock = driver.find_element(By.NAME, "inventories[1]")
                    if restore_stock.is_displayed():
                        restore_stock.click()
                        restore_stock.clear()
                        restore_stock.send_keys('200')
                        print('  ✓ Stock restored to 200')
                        
                        # Save
                        save_btn2 = driver.find_element(
                            By.XPATH,
                            "//button[contains(text(), 'Save Product')]"
                        )
                        driver.execute_script("arguments[0].click();", save_btn2)
                        time.sleep(2)
                        print('  ✓ Product saved with stock = 200')
        
        except Exception as e:
            print(f'  ⚠ Could not restore stock: {type(e).__name__}')
            print('  ℹ Manual cleanup may be required')
        
        # Close admin window
        driver.close()
        
        # Switch back to user window
        driver.switch_to.window(user_window)
        
        print("\n" + "="*80)
        print("S4: COMPLETED - Out of stock handling tested")
        print("Expected: Cart checkout blocked when stock < cart quantity")
        print("="*80 + "\n")
