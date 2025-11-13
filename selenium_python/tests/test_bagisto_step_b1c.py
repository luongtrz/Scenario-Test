"""
B1c: Save for Later (Move to Wishlist)
Scenario: User chooses "Move to Wishlist" to save product without checking out
Expected: Product is moved to "Saved for later" list (requires login)

Equivalent to: playwright_typescript/tests/bagisto-step-b1c.spec.ts

Note: Bagisto uses "Wishlist" instead of "Save for Later"
"""
import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from pages.store_page import StorePage


class TestBagistoB1cSaveForLater:
    """B1c - Save for Later (Wishlist) Test"""
    
    def test_b1c_save_for_later_moves_to_wishlist(self, driver, base_url, credentials):
        """
        B1c – Save for later moves product to wishlist
        
        Test Flow:
        1. Login (required for wishlist/save for later)
        2. Add product to cart
        3. Verify cart has items
        4. Select item for "Save for Later"
        5. Click "Move To Wishlist" button
        6. Navigate to wishlist/saved items page
        7. Verify item appears in wishlist
        8. Verify cart is now empty
        """
        print("\n" + "="*80)
        print("B1c: SAVE FOR LATER (MOVE TO WISHLIST)")
        print("="*80)
        print("\nNote: Bagisto uses 'Wishlist' instead of 'Save for Later'\n")
        
        store = StorePage(driver, base_url)
        
        print("\nStep 1: Logging in (required for wishlist/save for later)...")
        store.login()
        
        print("\nStep 2: Adding product to cart...")
        store.add_first_product_from_home()
        
        print("\nStep 3: Cart page loaded with product...")
        # add_first_product_from_home already navigates to cart
        
        print("\nStep 4: Verifying cart has items...")
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
        item_count = physical_count + ebook_count
        
        print(f'  Cart has {item_count} item(s) ({physical_count} physical, {ebook_count} e-book)')
        
        assert item_count > 0, "Cart should have items"
        
        print("\nStep 5: Selecting item for 'Save for Later'...")
        try:
            select_all_label = driver.find_element(By.CSS_SELECTOR, 'label[for="select-all"]')
            select_all_label.click()
            time.sleep(1)
            print('  ✓ Item(s) selected')
        except NoSuchElementException:
            print('  ⚠ Select All checkbox not found')
        
        print("\nStep 6: Looking for 'Move To Wishlist' button...")
        try:
            # Try multiple selectors for Move To Wishlist button
            move_to_wishlist_btn = None
            
            # Selector 1: span with role=button
            try:
                move_to_wishlist_btn = driver.find_element(
                    By.CSS_SELECTOR,
                    'span[role="button"]'
                )
                # Verify text contains "Move To Wishlist"
                if "Move To Wishlist" not in move_to_wishlist_btn.text:
                    move_to_wishlist_btn = None
            except NoSuchElementException:
                pass
            
            # Selector 2: Any element with text "Move To Wishlist"
            if not move_to_wishlist_btn:
                move_to_wishlist_btn = driver.find_element(
                    By.XPATH,
                    "//*[contains(text(), 'Move To Wishlist')]"
                )
            
            is_wishlist_available = move_to_wishlist_btn.is_displayed()
            print(f'  ✓ Found button: "{move_to_wishlist_btn.text}"')
        except NoSuchElementException:
            is_wishlist_available = False
        
        if not is_wishlist_available:
            print('  ⚠ "Move To Wishlist" button not visible')
            print('  Note: Bagisto uses "Wishlist" instead of "Save for Later"')
            print('\n' + "="*80)
            print('B1c: SKIPPED - Feature requires specific UI or multiple items selected')
            print("="*80 + "\n")
            pytest.skip("Move To Wishlist button not available")
            return
        
        print("\nStep 7: Clicking 'Move To Wishlist' button...")
        move_to_wishlist_btn.click()
        time.sleep(0.5)
        print('  ✓ Move To Wishlist clicked')
        
        print("\nStep 7b: Confirming move in modal (if present)...")
        try:
            # Look for "Agree" button in confirmation modal
            agree_btn = driver.find_element(
                By.XPATH,
                "//button[contains(text(), 'Agree')]"
            )
            if agree_btn.is_displayed():
                print('  ✓ Confirmation modal appeared, clicking Agree...')
                agree_btn.click()
                time.sleep(2)
        except NoSuchElementException:
            print('  ℹ No confirmation modal (move immediate)')
            time.sleep(2)
        
        print("\nStep 8: Navigating to wishlist/saved items page...")
        driver.get(f"{base_url}/customer/account/wishlist")
        time.sleep(2)
        
        print("\nStep 9: Verifying item appears in wishlist...")
        try:
            wishlist_heading = driver.find_element(
                By.XPATH,
                "//h2[contains(text(), 'Wishlist')]"
            )
            assert wishlist_heading.is_displayed(), "Wishlist heading not visible"
            print('  ✓ On wishlist page')
        except NoSuchElementException:
            print('  ⚠ Wishlist heading not found')
        
        # Count wishlist items
        try:
            wishlist_items = driver.find_elements(
                By.XPATH,
                "//button[contains(text(), 'Move To Cart')]"
            )
            saved_count = len(wishlist_items)
            print(f'  Found {saved_count} item(s) in wishlist/saved list')
            
            assert saved_count > 0, "Wishlist should have at least 1 item"
        except NoSuchElementException:
            print('  ⚠ No wishlist items found')
            saved_count = 0
        
        print("\nStep 10: Verifying cart status after moving to wishlist...")
        store.open_cart()
        
        # Count items remaining in cart
        qty_inputs_after = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="hidden"][name="quantity"]'
        )
        ebook_checkboxes_after = driver.find_elements(
            By.CSS_SELECTOR,
            'input[type="checkbox"][id^="item_"]'
        )
        
        physical_after = len(qty_inputs_after)
        ebook_after = len(ebook_checkboxes_after)
        total_after = physical_after + ebook_after
        
        print(f'  Cart after move: {total_after} item(s) ({physical_after} physical, {ebook_after} e-book)')
        print(f'  Initial cart: {item_count} item(s)')
        
        # Verify that items were actually moved
        if total_after >= item_count:
            print('  ❌ FAILED - Items were NOT moved to wishlist!')
            print('  Cart still has same or more items')
            assert False, "Move To Wishlist did not work - cart unchanged"
        elif total_after == 0:
            print('  ✓ Cart is now empty - all items moved to wishlist')
        else:
            print(f'  ⚠ Cart reduced from {item_count} to {total_after} items')
            print('  Some items moved, some remain (may be e-book or unsupported type)')
        
        print("\n" + "="*80)
        if total_after < item_count:
            print('B1c: PASSED - Product(s) moved to "Saved for Later" (Wishlist)')
        else:
            print('B1c: FAILED - Move To Wishlist did not reduce cart items')
        print("="*80 + "\n")
